#!/usr/bin/env python3
"""
parse_cron_input.py — Parse free-form text into structured cron job fields
using Claude Haiku.

Input: raw text describing a recurring task (via stdin, --text, or parse_cron())
Output: JSON with cron job fields ready for cron_lib.create_job()

Uses the same headless `claude` CLI calling pattern as parse_task_input.py.
LangFuse integration: degrades gracefully when LANGFUSE_SECRET_KEY is unset.
"""

import argparse
import json
import sys
import os
from datetime import date

# Reuse the Claude calling infrastructure from parse_task_input.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_task_input import call_claude, extract_json, PARSER_MODEL

# ─── Constants ───────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a cron job parser for a Product Manager's task automation system. You receive free-form text describing a recurring task and extract structured cron job fields.

Return ONLY valid JSON with these fields:

{
  "name": "Short descriptive name for this recurring job (max 60 chars)",
  "cron_expr": "Standard 5-field cron expression: minute hour day-of-month month day-of-week",
  "cron_human": "Human-readable schedule description",
  "task_template": {
    "title": "Imperative task title. May include template vars: {date}, {week}, {month}, {year}",
    "queue": "One of: human, agent, collab, waiting",
    "priority": "One of: critical, high, medium, low",
    "domain": "One of: product, strategy, marketing, recruiting, metrics, learning, ops",
    "description": "Full task instructions for the agent. Include ALL context, data sources, output paths, metric definitions, etc. from the user's input. This is the complete prompt the agent receives.",
    "tags": ["cron", "other-relevant-tags"]
  },
  "expires": null,
  "auto_dispatch": true
}

Cron expression reference (5 fields, space-separated):
  minute (0-59)  hour (0-23)  day-of-month (1-31)  month (1-12)  day-of-week (0-6, 0=Sunday)

  Special characters: * (any), */N (every N), N-M (range), N,M (list)

  Examples:
  - "Every Monday at 9am" → "0 9 * * 1"
  - "Every weekday at 8:30am" → "30 8 * * 1-5"
  - "Every Friday at 4pm" → "0 16 * * 5"
  - "Daily at 8am" → "0 8 * * *"
  - "Every 2 hours on weekdays" → "0 */2 * * 1-5"
  - "First Monday of each month at 10am" → "0 10 1-7 * 1"

IMPORTANT: Avoid scheduling on exact :00 and :30 minutes when the user's request is approximate.
Pick a minute offset like :03, :07, :47, :57 instead. Only use :00/:30 if the user explicitly says "at 9:00 sharp" or "on the half hour".

Queue rules:
- "agent": Work that produces a written artifact or analysis. Most recurring tasks are agent tasks.
- "collab": Agent prep + human decision needed.
- "human": Only human can do it.
- "waiting": Waiting on someone else.

Priority rules (for the recurring task instances):
- "high": Important recurring work
- "medium": Standard recurring work (most common)
- "low": Nice-to-have recurring monitoring

For the task_template.description: Include EVERYTHING the user mentioned — data sources (Pendo, Zendesk, Jira, spreadsheets), specific queries, metric definitions, output file paths, formatting requirements. The agent needs complete instructions each time the job runs.

Template variables for title: {date} = current date (YYYY-MM-DD), {week} = week range (e.g. "Mar 31 – Apr 06"), {month} = month name + year, {year} = year.

If the user mentions "for 2 weeks" or "until May", set expires to an ISO date string (YYYY-MM-DD). Otherwise null.

Today is {today}.

Return ONLY the JSON object. No markdown, no code fences, no explanation, no thinking."""


# ─── Prompt Management ───────────────────────────────────────────────────────

def _get_system_prompt():
    """Fetch system prompt from LangFuse if available, otherwise use hardcoded."""
    today = date.today().isoformat()
    try:
        from langfuse_client import fetch_prompt
        lf_prompt = fetch_prompt("cron-parser", label="production")
        if lf_prompt is not None:
            return lf_prompt.compile(today=today)
    except Exception:
        pass
    return SYSTEM_PROMPT.replace("{today}", today)


# ─── Parsing ─────────────────────────────────────────────────────────────────

def parse_cron(text):
    """Parse free-form text into structured cron job fields.

    Returns dict with: name, cron_expr, cron_human, task_template, expires, auto_dispatch.
    Raises on failure.
    """
    system = _get_system_prompt()

    raw = call_claude(system, text, model=PARSER_MODEL)
    parsed = extract_json(raw)

    # Validate cron expression
    from croniter import croniter
    if not croniter.is_valid(parsed.get("cron_expr", "")):
        raise ValueError(f"Invalid cron expression: {parsed.get('cron_expr')}")

    # Ensure required fields
    if not parsed.get("name"):
        raise ValueError("Missing job name")
    if not parsed.get("task_template", {}).get("description"):
        raise ValueError("Missing task description")

    # Defaults
    parsed.setdefault("auto_dispatch", True)
    parsed.setdefault("expires", None)
    tpl = parsed.setdefault("task_template", {})
    tpl.setdefault("queue", "agent")
    tpl.setdefault("priority", "medium")
    tags = tpl.get("tags", [])
    if "cron" not in tags:
        tags = ["cron"] + tags
    tpl["tags"] = tags

    return parsed


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Parse free-form text into a PM-OS cron job")
    parser.add_argument("--text", help="Raw text to parse (otherwise reads stdin)")
    parser.add_argument("--json", action="store_true", help="Output raw parsed JSON")
    args = parser.parse_args()

    text = args.text if args.text else sys.stdin.read()
    text = text.strip()

    if not text:
        print("Error: no input text provided", file=sys.stderr)
        sys.exit(1)

    try:
        parsed = parse_cron(text)
    except json.JSONDecodeError as e:
        print(f"Error: LLM returned invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(parsed, indent=2))


if __name__ == "__main__":
    main()
