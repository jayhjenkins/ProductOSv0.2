#!/usr/bin/env python3
"""
langfuse_setup.py — Register PM-OS prompts in LangFuse for versioning and management.

Registers:
  1. task-parser — The system prompt from parse_task_input.py
  2. worker-* — One prompt per worker definition in scripts/workers/
  3. skill-* — All skill files (for version tracking, not runtime fetch)

Usage:
    python3 scripts/langfuse_setup.py              # register all prompts
    python3 scripts/langfuse_setup.py --dry-run     # show what would be registered
    python3 scripts/langfuse_setup.py --workers     # only register worker prompts
    python3 scripts/langfuse_setup.py --skills      # only register skill prompts

Requires: LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY env vars
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PM_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workers")
SKILLS_DIR = os.path.join(PM_OS_DIR, ".claude", "skills")


def _parse_frontmatter(path):
    """Parse YAML frontmatter from a markdown file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return None, None

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)", content, re.DOTALL)
    if not match:
        return None, content  # no frontmatter, entire content is body

    fm_text = match.group(1)
    body = match.group(2).strip()

    from ruamel.yaml import YAML
    from io import StringIO
    yaml = YAML()
    yaml.preserve_quotes = True
    try:
        fm = yaml.load(StringIO(fm_text))
        if not isinstance(fm, dict):
            return {}, body
        fm = json.loads(json.dumps(fm, default=str))
    except Exception:
        return {}, body

    return fm, body


def register_task_parser(langfuse, dry_run=False):
    """Register the task-parser system prompt."""
    from parse_task_input import SYSTEM_PROMPT

    name = "task-parser"
    print(f"  {'[DRY-RUN] ' if dry_run else ''}Registering: {name}")

    if dry_run:
        print(f"    Template vars: {{today}}")
        print(f"    Length: {len(SYSTEM_PROMPT)} chars")
        return

    try:
        langfuse.create_prompt(
            name=name,
            prompt=SYSTEM_PROMPT,
            config={"model": "claude-haiku-4-5", "temperature": 0.1},
            labels=["production"],
            type="text",
        )
        print(f"    OK — registered with 'production' label")
    except Exception as e:
        # Prompt may already exist — try to get it
        if "already exists" in str(e).lower() or "409" in str(e):
            print(f"    Already exists — skipping")
        else:
            print(f"    ERROR: {e}")


def register_workers(langfuse, dry_run=False):
    """Register all worker prompts."""
    if not os.path.isdir(WORKERS_DIR):
        print("  No workers directory found")
        return

    for filename in sorted(os.listdir(WORKERS_DIR)):
        if not filename.endswith(".md"):
            continue

        path = os.path.join(WORKERS_DIR, filename)
        fm, body = _parse_frontmatter(path)
        if fm is None:
            continue

        name = fm.get("langfuse_prompt") or f"worker-{fm.get('name', filename.replace('.md', ''))}"
        worker_name = fm.get("name", filename)
        model = "claude-code"

        print(f"  {'[DRY-RUN] ' if dry_run else ''}Registering: {name} ({worker_name})")

        if dry_run:
            print(f"    Template vars: {{task_id}}, {{skills_catalog}}, {{rerun_block}}")
            print(f"    Length: {len(body)} chars")
            tools = fm.get("allowed_tools", [])
            print(f"    Tools: {len(tools)} allowed")
            continue

        try:
            langfuse.create_prompt(
                name=name,
                prompt=body,
                config={
                    "model": model,
                    "worker": worker_name,
                    "allowed_tools": fm.get("allowed_tools", []),
                    "skills": fm.get("skills", []),
                    "timeout": fm.get("timeout", 600),
                    "max_turns": fm.get("max_turns", 30),
                },
                labels=["production"],
                type="text",
            )
            print(f"    OK — registered with 'production' label")
        except Exception as e:
            if "already exists" in str(e).lower() or "409" in str(e):
                print(f"    Already exists — skipping")
            else:
                print(f"    ERROR: {e}")


def register_skills(langfuse, dry_run=False):
    """Register all skill files for version tracking."""
    if not os.path.isdir(SKILLS_DIR):
        print("  No skills directory found")
        return

    count = 0
    for root, dirs, files in os.walk(SKILLS_DIR):
        for filename in files:
            if filename.lower() not in ("skill.md",):
                continue

            path = os.path.join(root, filename)
            fm, body = _parse_frontmatter(path)

            # Get relative path for naming
            rel = os.path.relpath(root, SKILLS_DIR)
            skill_name = fm.get("name", rel.replace("/", "-")) if fm else rel.replace("/", "-")
            prompt_name = f"skill-{skill_name}"

            if dry_run:
                print(f"  [DRY-RUN] Registering: {prompt_name}")
                count += 1
                continue

            try:
                langfuse.create_prompt(
                    name=prompt_name,
                    prompt=body or "(empty)",
                    config={
                        "skill_path": rel,
                        "description": fm.get("description", "") if fm else "",
                    },
                    labels=["production"],
                    tags=["skill"],
                    type="text",
                )
                count += 1
            except Exception as e:
                if "already exists" in str(e).lower() or "409" in str(e):
                    pass  # silently skip existing skills
                else:
                    print(f"  ERROR registering {prompt_name}: {e}")

    print(f"  {'[DRY-RUN] ' if dry_run else ''}Registered {count} skill prompts")


def register_cron_parser(langfuse, dry_run=False):
    """Register the cron-parser system prompt."""
    from parse_cron_input import SYSTEM_PROMPT

    name = "cron-parser"
    print(f"  {'[DRY-RUN] ' if dry_run else ''}Registering: {name}")

    if dry_run:
        print(f"    Template vars: {{today}}")
        print(f"    Length: {len(SYSTEM_PROMPT)} chars")
        return

    try:
        langfuse.create_prompt(
            name=name,
            prompt=SYSTEM_PROMPT,
            config={"model": "claude-haiku-4-5", "temperature": 0.1},
            labels=["production"],
            type="text",
        )
        print(f"    Registered (production)")
    except Exception as e:
        if "already exists" in str(e).lower() or "409" in str(e):
            print(f"    Already exists (skipped)")
        else:
            print(f"    Error: {e}")


def register_worker_router(langfuse, dry_run=False):
    """Register the worker-router prompt (LLM-based task→worker matching)."""
    from task_dispatch import _WORKER_MATCH_PROMPT

    name = "worker-router"
    print(f"  {'[DRY-RUN] ' if dry_run else ''}Registering: {name}")

    if dry_run:
        print(f"    Length: {len(_WORKER_MATCH_PROMPT)} chars")
        return

    try:
        langfuse.create_prompt(
            name=name,
            prompt=_WORKER_MATCH_PROMPT,
            config={"model": "claude-haiku-4-5", "temperature": 0.1},
            labels=["production"],
            type="text",
        )
        print(f"    Registered (production)")
    except Exception as e:
        if "already exists" in str(e).lower() or "409" in str(e):
            print(f"    Already exists (skipped)")
        else:
            print(f"    Error: {e}")


def register_judge_rubric(langfuse, dry_run=False):
    """Register the per-deliverable judge rubrics (document / message / meeting)."""
    from judge import RUBRICS

    for kind, (name, text) in RUBRICS.items():
        print(f"  {'[DRY-RUN] ' if dry_run else ''}Registering: {name} ({kind})")
        if dry_run:
            print(f"    Length: {len(text)} chars")
            continue
        try:
            langfuse.create_prompt(
                name=name,
                prompt=text,
                config={"model": "claude-opus-4-8", "temperature": 0.0, "kind": kind},
                labels=["production"],
                type="text",
            )
            print(f"    Registered (production)")
        except Exception as e:
            if "already exists" in str(e).lower() or "409" in str(e):
                print(f"    Already exists (skipped)")
            else:
                print(f"    Error: {e}")


def register_voice(langfuse, dry_run=False):
    """Register Jay's voice guide (judge-voice-jay) from datasets/reference/jay-voice.md.

    The on-disk file is the editable source of truth; this pushes its body to
    LangFuse so the judge can fetch a versioned copy (composed into the message rubric).
    """
    from judge import VOICE_FILE

    name = "judge-voice-jay"
    if not os.path.isfile(VOICE_FILE):
        print(f"  Skipping {name}: {VOICE_FILE} not found")
        return
    with open(VOICE_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    print(f"  {'[DRY-RUN] ' if dry_run else ''}Registering: {name}")
    if dry_run:
        print(f"    Length: {len(text)} chars")
        return
    try:
        langfuse.create_prompt(
            name=name,
            prompt=text,
            config={"source": "datasets/reference/jay-voice.md"},
            labels=["production"],
            type="text",
        )
        print(f"    Registered (production)")
    except Exception as e:
        if "already exists" in str(e).lower() or "409" in str(e):
            print(f"    Already exists (skipped)")
        else:
            print(f"    Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Register PM-OS prompts in LangFuse")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be registered")
    parser.add_argument("--workers", action="store_true", help="Only register worker prompts")
    parser.add_argument("--skills", action="store_true", help="Only register skill prompts")
    parser.add_argument("--parser", action="store_true", help="Only register task-parser prompt")
    parser.add_argument("--cron", action="store_true", help="Only register cron-parser prompt")
    parser.add_argument("--judge", action="store_true", help="Only register judge-rubric prompt")
    args = parser.parse_args()

    register_all = not (args.workers or args.skills or args.parser or args.cron or args.judge)

    if not args.dry_run:
        from langfuse_client import get_langfuse
        langfuse = get_langfuse()
        if langfuse is None:
            print("ERROR: LangFuse not configured. Set LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY.")
            sys.exit(1)
    else:
        langfuse = None

    print("PM-OS Prompt Registration")
    print("=" * 40)

    if register_all or args.parser:
        print("\n[Task Parser]")
        register_task_parser(langfuse, dry_run=args.dry_run)

    if register_all or args.workers:
        print("\n[Workers]")
        register_workers(langfuse, dry_run=args.dry_run)
        print("\n[Worker Router]")
        register_worker_router(langfuse, dry_run=args.dry_run)

    if register_all or args.skills:
        print("\n[Skills]")
        register_skills(langfuse, dry_run=args.dry_run)

    if register_all or args.cron:
        print("\n[Cron Parser]")
        register_cron_parser(langfuse, dry_run=args.dry_run)

    if register_all or args.judge:
        print("\n[Judge Rubric]")
        register_judge_rubric(langfuse, dry_run=args.dry_run)
        print("\n[Judge Voice]")
        register_voice(langfuse, dry_run=args.dry_run)

    if not args.dry_run and langfuse:
        from langfuse_client import flush
        flush()

    print("\nDone.")


if __name__ == "__main__":
    main()
