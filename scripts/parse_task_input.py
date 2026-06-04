#!/usr/bin/env python3
"""
parse_task_input.py — Parse unstructured text (voice dump, quick notes) into
structured task fields using Claude Haiku.

Input: raw text blob via stdin or --text argument
Output: JSON with task fields ready for task_cli.py

Runs the structured extraction through a one-shot headless `claude` CLI call
(`claude -p ... --model claude-haiku-4-5`), the same invocation pattern the rest
of PM-OS uses for Claude (see task_dispatch.py and jira_publish.py). Override
the model with PM_OS_PARSER_MODEL.

LangFuse integration: parse operations are traced via langfuse_client.create_trace
when LANGFUSE_SECRET_KEY is set; degrades gracefully when unavailable.
"""

import argparse
import json
import re
import subprocess
import sys
import os
import atexit
from datetime import date

# ─── LangFuse flush registration (graceful degradation) ─────────────────────

try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from langfuse_client import flush as lf_flush
    atexit.register(lf_flush)
except ImportError:
    pass

# ─── Constants ───────────────────────────────────────────────────────────────

# Lightweight parsing/routing runs on Claude Haiku via the headless `claude`
# CLI. Override with PM_OS_PARSER_MODEL.
PARSER_MODEL = os.environ.get("PM_OS_PARSER_MODEL", "claude-haiku-4-5")

SYSTEM_PROMPT = """You are a task parser for a Product Manager's task system. You receive raw, unstructured text (often from voice-to-text) and extract a single structured task.

Return ONLY valid JSON with these fields:

{
  "title": "Imperative verb + specific object, max 120 chars. e.g. 'Draft competitive analysis for vendor payments'",
  "queue": "One of: human, agent, collab, waiting",
  "priority": "One of: critical, high, medium, low",
  "domain": "One of: product, strategy, marketing, recruiting, metrics, learning, ops",
  "description": "2-3 sentence description with context from the input. Include why this matters if mentioned.",
  "due": null,
  "tags": [],
  "project": null,
  "waiting_on": null,
  "task_type": null,
  "meeting_attendees": null,
  "meeting_duration": null,
  "meeting_title": null,
  "meeting_description": null,
  "message_channel": null,
  "message_to": null,
  "message_subject": null
}

Queue rules:
- "agent": Work that produces a written artifact (memo, PRD, research, analysis, summary, draft). The AI agent can do this autonomously.
- "collab": Decisions needing agent prep + human judgment; scheduling a meeting; OR sending a message to a person. Communicative tasks — "talk to / speak with / share with / forward to / loop in / reach out to / ping [person]" — are MESSAGES: set task_type to "send-message" and capture the recipient(s) and the gist in the title/description. For an explicitly heavier engagement ("meeting", "sync", "working session", "demo", "call to walk through"), set task_type to "schedule-meeting" and fill meeting_* fields. When ambiguous between a message and a meeting, prefer the message (the lighter action).
- "human": Only when the human must physically do something only they can do (get access to something, make a phone call, an in-person action). Note: drafting/sending a message is a "collab" send-message task, not human.
- "waiting": When waiting on someone else to deliver something. Set waiting_on to the person/team name.

Priority rules:
- "critical": Blocking other work or deadline today/tomorrow
- "high": Due this week or significant impact
- "medium": Standard work, 1-2 weeks
- "low": Nice-to-have, no deadline

For scheduling meetings (the heavier, explicitly-framed case — "meeting", "sync", "working session", "demo", "call to walk through"; a lighter "talk to / share / forward" is a send-message, not a meeting):
- Set queue to "collab", task_type to "schedule-meeting"
- Extract attendee names into meeting_attendees (comma-separated)
- Set meeting_duration (minutes, default 30)
- Write a calendar-appropriate meeting_title and meeting_description

For sending a message (the lighter, communicative case — "talk to / share with / forward to / loop in / reach out to [person]"):
- Set queue to "collab", task_type to "send-message"
- Capture the recipient(s) and what to convey in the title/description (no meeting_* fields)
- Set message_to to the recipient (person name, or a channel like "#platform-eng")
- Set message_channel if the channel is stated ("Teams", "Email", "Slack"); leave null if not mentioned
- Set message_subject only for an email when a subject is clear; otherwise null
- Do NOT draft the message body — the agent writes that later (leave it out)

Only include fields that are clearly indicated. Use null for anything not mentioned.
Only set "due" if a specific date is mentioned. Today is {today}.

Return ONLY the JSON object. No markdown, no code fences, no explanation, no thinking."""


# ─── Prompt Management (LangFuse or hardcoded fallback) ─────────────────────

def _get_system_prompt():
    """Fetch system prompt from LangFuse if available, otherwise use hardcoded."""
    today = date.today().isoformat()
    try:
        from langfuse_client import fetch_prompt
        lf_prompt = fetch_prompt("task-parser", label="production")
        if lf_prompt is not None:
            return lf_prompt.compile(today=today)
    except Exception:
        pass
    return SYSTEM_PROMPT.replace("{today}", today)


# ─── LLM Calls ──────────────────────────────────────────────────────────────

def _claude_bin() -> str:
    """Resolve the claude CLI path (same lookup as jira_publish.py)."""
    cand = os.path.join(os.path.expanduser("~"), ".local", "bin", "claude")
    if os.path.exists(cand):
        return cand
    cand = "/opt/homebrew/bin/claude"
    if os.path.exists(cand):
        return cand
    return "claude"  # fall back to PATH lookup


def call_claude(system: str, user: str, model: str = PARSER_MODEL, timeout: int = 120) -> str:
    """Run a one-shot headless `claude -p` call and return the printed result.

    Mirrors the dispatch / jira_publish pattern: strip CLAUDE_* env vars to
    avoid nested-session detection and keep the claude binary on PATH. Used for
    the lightweight structured-output calls (task parse, cron parse, worker
    route), which run on Claude Haiku.

    The call is a clean text completion, not an agent loop:
    - `--system-prompt` replaces the default agentic system prompt with ours,
    - `--tools ""` disables every tool,
    - `--setting-sources ""` loads no settings, so no project/user hooks fire
      (e.g. the SessionStart skill-usage injection) — the call stays hermetic,
    - `--max-turns 2` (the CLI reports an error at 1 even for a single reply).
    """
    # Strip Claude env vars to prevent nested-session detection; ensure the
    # claude binary's dirs are on PATH (important under cron / task_server).
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("CLAUDE", "CMUX_CLAUDE"))}
    env["PATH"] = (
        os.path.join(os.path.expanduser("~"), ".local", "bin")
        + ":/opt/homebrew/bin"
        + ":" + env.get("PATH", "/usr/bin:/bin")
    )

    cmd = [
        _claude_bin(), "-p", user or system,
        "--model", model,
        "--max-turns", "2",
        "--tools", "",
        "--setting-sources", "",
    ]
    if user:
        cmd += ["--system-prompt", system]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"claude CLI failed (exit {result.returncode}): {result.stderr.strip()[:300]}"
        )
    return result.stdout.strip()


def extract_json(raw: str) -> dict:
    """Extract JSON from LLM response, handling markdown fences and think blocks."""
    # Strip <think> blocks defensively (some models wrap reasoning this way)
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

    # Strip markdown code fences
    if raw.startswith("```"):
        lines = raw.split("\n")
        # Remove first line (```json or ```) and last line (```)
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw = "\n".join(lines).strip()

    return json.loads(raw)


def parse_task(text: str, source_meeting: str = None) -> dict:
    """Send raw text to Claude Haiku and get structured task fields back.

    Args:
        text: Raw text to parse into task fields.
        source_meeting: Optional meeting file path (for LangFuse tracing).
    """
    system = _get_system_prompt()
    model = PARSER_MODEL

    try:
        raw = call_claude(system, text, model=model)
        result = extract_json(raw)
    except Exception as e:
        # Trace the failure before raising
        _trace_parse(text, source_meeting, None, model, str(e))
        raise

    # Trace the successful parse
    _trace_parse(text, source_meeting, result, model, None)
    return result


def _trace_parse(text, source_meeting, result, model, error):
    """Create a LangFuse trace for a task parse operation."""
    try:
        from langfuse_client import create_trace
        tags = ["task-parser"]
        if source_meeting:
            tags.append("meeting-extraction")

        # Truncate input for trace (keep it readable)
        input_summary = text[:300] + ("..." if len(text) > 300 else "")

        create_trace(
            name="task-parser",
            session_id=source_meeting or None,
            metadata={
                "model": model,
                "source_meeting": source_meeting,
                "input_length": len(text),
            },
            tags=tags,
            input_data={"text": input_summary},
            output_data={
                "parsed": result,
                "error": error,
            } if result or error else None,
        )
    except Exception:
        pass


def build_cli_args(parsed: dict) -> list[str]:
    """Convert parsed dict into task_cli.py add arguments."""
    args = [parsed["title"]]

    field_map = {
        "queue": "-q",
        "priority": "-p",
        "domain": "-d",
    }

    for field, flag in field_map.items():
        if parsed.get(field):
            args.extend([flag, parsed[field]])

    optional_str_fields = {
        "description": "--description",
        "due": "--due",
        "project": "--project",
        "waiting_on": "--waiting-on",
        "task_type": "--task-type",
        "meeting_attendees": "--meeting-attendees",
        "meeting_title": "--meeting-title",
        "meeting_description": "--meeting-description",
        "message_channel": "--message-channel",
        "message_to": "--message-to",
        "message_subject": "--message-subject",
    }

    for field, flag in optional_str_fields.items():
        val = parsed.get(field)
        if val:
            args.extend([flag, str(val)])

    if parsed.get("meeting_duration"):
        args.extend(["--meeting-duration", str(parsed["meeting_duration"])])

    if parsed.get("tags"):
        tags = parsed["tags"]
        if isinstance(tags, list):
            tags = ",".join(tags)
        if tags:
            args.extend(["--tags", tags])

    args.extend(["--creator", "human"])

    return args


def main():
    parser = argparse.ArgumentParser(description="Parse unstructured text into a PM-OS task")
    parser.add_argument("--text", help="Raw text to parse (otherwise reads stdin)")
    parser.add_argument("--source-meeting", help="Source meeting file path (for LangFuse tracing)")
    parser.add_argument("--dry-run", action="store_true", help="Print parsed fields without creating task")
    parser.add_argument("--json", action="store_true", help="Output raw parsed JSON")
    args = parser.parse_args()

    text = args.text if args.text else sys.stdin.read()
    text = text.strip()

    if not text:
        print("Error: no input text provided", file=sys.stderr)
        sys.exit(1)

    try:
        parsed = parse_task(text, source_meeting=args.source_meeting)
    except json.JSONDecodeError as e:
        print(f"Error: LLM returned invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(parsed, indent=2))
        return

    if args.dry_run:
        print(f"Title:       {parsed.get('title')}")
        print(f"Queue:       {parsed.get('queue')}")
        print(f"Priority:    {parsed.get('priority')}")
        print(f"Domain:      {parsed.get('domain')}")
        print(f"Description: {parsed.get('description')}")
        if parsed.get("due"):
            print(f"Due:         {parsed['due']}")
        if parsed.get("tags"):
            print(f"Tags:        {parsed['tags']}")
        if parsed.get("waiting_on"):
            print(f"Waiting on:  {parsed['waiting_on']}")
        if parsed.get("task_type"):
            print(f"Task type:   {parsed['task_type']}")
        return

    # Build and execute task_cli.py add
    cli_args = build_cli_args(parsed)

    pm_os_dir = os.path.dirname(os.path.abspath(__file__))
    pm_os_dir = os.path.dirname(pm_os_dir)  # scripts/ -> pm-os/

    result = subprocess.run(
        ["/opt/homebrew/bin/python3", os.path.join(pm_os_dir, "scripts", "task_cli.py"), "add"] + cli_args,
        capture_output=True,
        text=True,
        cwd=pm_os_dir,
    )

    if result.returncode == 0:
        print(result.stdout.strip())
    else:
        print(f"Error creating task: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
