#!/usr/bin/env python3
"""
parse_task_input.py — Parse unstructured text (voice dump, quick notes) into
structured task fields using local Ollama LLM.

Input: raw text blob via stdin or --text argument
Output: JSON with task fields ready for task_cli.py

Uses nemotron-3-nano:30b for structured extraction.
Falls back to qwen3:30b-a3b if nemotron fails.

LangFuse integration: auto-traces all LLM calls when LANGFUSE_SECRET_KEY is set.
Falls back to stdlib urllib when langfuse/openai packages are not installed.
"""

import argparse
import json
import re
import subprocess
import sys
import os
import urllib.request
import atexit
from datetime import date

# ─── LangFuse / OpenAI client setup (graceful degradation) ──────────────────

_USE_OPENAI = False
_openai_client = None

try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from langfuse_client import get_openai_client, get_langfuse, flush as lf_flush
    _client = get_openai_client()
    if _client is not None:
        _openai_client = _client
        _USE_OPENAI = True
        atexit.register(lf_flush)
except ImportError:
    pass

if not _USE_OPENAI:
    try:
        from openai import OpenAI
        _openai_client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        _USE_OPENAI = True
    except ImportError:
        pass

# ─── Constants ───────────────────────────────────────────────────────────────

OLLAMA_URL = "http://localhost:11434/v1/chat/completions"
OLLAMA_NATIVE_URL = "http://localhost:11434/api/chat"

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
  "meeting_description": null
}

Queue rules:
- "agent": Work that produces a written artifact (memo, PRD, research, analysis, summary, draft). The AI agent can do this autonomously.
- "collab": Decisions needing agent prep + human judgment, OR scheduling meetings. For meetings, set task_type to "schedule-meeting" and fill meeting_* fields.
- "human": Only when the human must physically do it (send a message, have a conversation, get access to something, make a phone call).
- "waiting": When waiting on someone else to deliver something. Set waiting_on to the person/team name.

Priority rules:
- "critical": Blocking other work or deadline today/tomorrow
- "high": Due this week or significant impact
- "medium": Standard work, 1-2 weeks
- "low": Nice-to-have, no deadline

For scheduling meetings:
- Set queue to "collab", task_type to "schedule-meeting"
- Extract attendee names into meeting_attendees (comma-separated)
- Set meeting_duration (minutes, default 30)
- Write a calendar-appropriate meeting_title and meeting_description

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

def _call_ollama_openai(model: str, system: str, user: str) -> str:
    """Call Ollama via OpenAI SDK (with LangFuse auto-tracing if configured)."""
    response = _openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content.strip()


def _call_ollama_native(model: str, system: str, user: str, num_ctx: int) -> str:
    """Call Ollama native /api/chat endpoint (supports num_ctx, no LangFuse tracing)."""
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "options": {"num_ctx": num_ctx, "temperature": 0.1},
        "stream": False,
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_NATIVE_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    return data["message"]["content"].strip()


def _call_ollama_urllib(model: str, system: str, user: str) -> str:
    """Call Ollama chat completions endpoint using stdlib urllib (no tracing)."""
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.1,
        "stream": False,
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    return data["choices"][0]["message"]["content"].strip()


def call_ollama(model: str, system: str, user: str, num_ctx: int = None) -> str:
    """Call Ollama — uses OpenAI SDK with LangFuse tracing when available.

    Args:
        num_ctx: Override context window size via native API. The OpenAI-compat
                 endpoint (/v1/) ignores num_ctx, so we use /api/chat instead.
    """
    if num_ctx is not None:
        return _call_ollama_native(model, system, user, num_ctx)
    if _USE_OPENAI:
        return _call_ollama_openai(model, system, user)
    return _call_ollama_urllib(model, system, user)


def extract_json(raw: str) -> dict:
    """Extract JSON from LLM response, handling markdown fences and think blocks."""
    # Strip <think> blocks (qwen3 sometimes emits these)
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
    """Send raw text to Ollama and get structured task fields back.

    Args:
        text: Raw text to parse into task fields.
        source_meeting: Optional meeting file path (for LangFuse tracing).
    """
    system = _get_system_prompt()

    models = ["nemotron-3-nano:30b", "qwen3:30b-a3b"]
    result = None
    used_model = None
    error_msg = None

    for model in models:
        try:
            raw = call_ollama(model, system, text)
            result = extract_json(raw)
            used_model = model
            break
        except Exception as e:
            error_msg = str(e)
            if model == models[-1]:
                # Trace the failure before raising
                _trace_parse(text, source_meeting, None, model, str(e))
                raise
            continue

    # Trace the successful parse
    _trace_parse(text, source_meeting, result, used_model, None)
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
