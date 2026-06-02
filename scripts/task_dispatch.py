#!/usr/bin/env python3
"""
task_dispatch.py — Headless dispatcher for PM-OS task management.

Reads the agent queue, finds actionable tasks, and invokes Claude Code
in headless mode (`claude -p`) for each one.

Usage:
    python3 scripts/task_dispatch.py                  # process all actionable tasks
    python3 scripts/task_dispatch.py --task TASK-0001  # process a single task
    python3 scripts/task_dispatch.py --dry-run         # show what would be dispatched
"""

import json
import re
import signal
import subprocess
import os
import sys
import fcntl
import argparse
import time
import glob as globmod
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import task_lib

# ─── Constants ────────────────────────────────────────────────────────────────

PM_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ─── Load LangFuse env vars if not already set ───────────────────────────────
# .env.langfuse lives at the repo root and exports LANGFUSE_PUBLIC_KEY,
# LANGFUSE_SECRET_KEY, and LANGFUSE_HOST.  When dispatch is invoked from cron
# or a subprocess that didn't source the file, traces silently fail.
_env_langfuse = os.path.join(PM_OS_DIR, ".env.langfuse")
if not os.environ.get("LANGFUSE_SECRET_KEY") and os.path.isfile(_env_langfuse):
    with open(_env_langfuse) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _line = _line.removeprefix("export ")
                _key, _, _val = _line.partition("=")
                os.environ[_key.strip()] = _val.strip()
TASK_SH = os.path.join(PM_OS_DIR, "scripts", "task.sh")
LOCK_FILE = os.path.join(PM_OS_DIR, "datasets", "tasks", "_dispatch.lock")
LOG_DIR = os.path.join(PM_OS_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "dispatch.log")

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


# ─── Logging ──────────────────────────────────────────────────────────────────

def _ensure_log_dir():
    """Create log directory if it does not exist."""
    os.makedirs(LOG_DIR, exist_ok=True)


def log(message, task_id=None):
    """Append a timestamped log entry to dispatch.log and print to stderr."""
    _ensure_log_dir()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    prefix = f"[{ts}]"
    if task_id:
        prefix += f" [{task_id}]"
    line = f"{prefix} {message}"
    print(line, file=sys.stderr)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError as e:
        print(f"[{ts}] WARNING: Could not write to log file: {e}", file=sys.stderr)


# ─── Lockfile ─────────────────────────────────────────────────────────────────

def acquire_lock():
    """Acquire an exclusive lock on the dispatch lockfile.

    Returns the open file descriptor on success, or None if another
    dispatcher is already running.
    """
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    try:
        fd = open(LOCK_FILE, "w")
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fd.write(str(os.getpid()))
        fd.flush()
        return fd
    except (OSError, IOError):
        return None


def release_lock(fd):
    """Release the dispatch lock."""
    if fd:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
            fd.close()
        except (OSError, IOError):
            pass


# ─── Queue Reading ────────────────────────────────────────────────────────────

def get_actionable_tasks():
    """Fetch the agent queue and return tasks that are ready to dispatch.

    Actionable tasks are:
    - status: "open" (new, unstarted tasks)
    - status: "blocked" AND agent_status: "queued" (human answered, agent resumes)

    Returns a list of task dicts sorted by priority descending (critical first),
    then by created ascending (oldest first).
    """
    tasks = []
    for queue in ("agent", "collab"):
        try:
            result = subprocess.run(
                [TASK_SH, "list", "--queue", queue, "--json"],
                capture_output=True,
                text=True,
                cwd=PM_OS_DIR,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            log(f"ERROR: task.sh list --queue {queue} timed out")
            continue
        except FileNotFoundError:
            log(f"ERROR: task.sh not found at {TASK_SH}")
            return []

        if result.returncode != 0:
            log(f"ERROR: task.sh list --queue {queue} failed (rc={result.returncode}): {result.stderr.strip()}")
            continue

        try:
            queue_tasks = json.loads(result.stdout)
            tasks.extend(queue_tasks)
        except json.JSONDecodeError as e:
            log(f"ERROR: Failed to parse {queue} queue JSON: {e}")
            continue

    # Filter to actionable tasks
    actionable = []
    for t in tasks:
        status = t.get("status", "")
        agent_status = t.get("agent_status")

        if status == "open":
            actionable.append(t)
        elif status == "blocked" and agent_status == "queued":
            actionable.append(t)

    # Sort: priority descending (critical=0 first), then created ascending (oldest first)
    actionable.sort(key=lambda t: (
        PRIORITY_ORDER.get(t.get("priority", "medium"), 99),
        t.get("created", ""),
    ))

    return actionable


# ─── Skills Catalog ───────────────────────────────────────────────────────────

def parse_skill_frontmatter(path):
    """Read YAML frontmatter from a SKILL.md and extract name + description."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read(2000)  # frontmatter is near the top
    except OSError:
        return None, None

    # Match YAML frontmatter between --- delimiters
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None, None

    frontmatter = match.group(1)
    name = None
    desc = None
    for line in frontmatter.splitlines():
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            desc = line.split(":", 1)[1].strip().strip('"').strip("'")
    return name, desc


def build_skills_catalog():
    """Walk .claude/skills/ and return a concise catalog of available skills."""
    catalog_lines = []
    skills_dir = os.path.join(PM_OS_DIR, ".claude", "skills")
    if not os.path.isdir(skills_dir):
        return "(no skills directory found)"
    for root, dirs, files in os.walk(skills_dir):
        if "SKILL.md" in files:
            skill_path = os.path.join(root, "SKILL.md")
            name, desc = parse_skill_frontmatter(skill_path)
            if name and desc:
                catalog_lines.append(f"- **{name}**: {desc}")
    return "\n".join(catalog_lines) if catalog_lines else "(no skills found)"


# ─── Worker System ───────────────────────────────────────────────────────────

WORKERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workers")

# Synthetic default worker used when no worker files exist
_FALLBACK_DEFAULT_WORKER = {
    "name": "default",
    "description": "Fallback default worker",
    "priority": 0,
    "match": {"task_type": [], "domains": [], "title_patterns": [], "description_patterns": []},
    "allowed_tools": ["Bash(*)", "Read(*)", "Write(*)", "Edit(*)", "WebFetch(*)", "WebSearch(*)", "Agent(*)", "mcp__*"],
    "skills": [],
    "langfuse_prompt": "worker-default",
    "timeout": 600,
    "max_turns": 30,
    "prompt_body": None,  # signals: use legacy build_prompt()
}


def _parse_worker_frontmatter(path):
    """Parse YAML frontmatter from a worker .md file. Returns (frontmatter_dict, body_str)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return None, None

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)", content, re.DOTALL)
    if not match:
        return None, None

    fm_text = match.group(1)
    body = match.group(2).strip()

    # Parse YAML frontmatter using ruamel.yaml (already a project dependency)
    from ruamel.yaml import YAML
    from io import StringIO
    yaml = YAML()
    yaml.preserve_quotes = True
    try:
        fm = yaml.load(StringIO(fm_text))
        if not isinstance(fm, dict):
            return None, None
        # Convert ruamel types to plain Python types
        fm = json.loads(json.dumps(fm, default=str))
    except Exception:
        return None, None

    # Coerce types
    try:
        fm["priority"] = int(fm.get("priority", 0))
    except (ValueError, TypeError):
        fm["priority"] = 0
    try:
        fm["timeout"] = int(fm.get("timeout", 600))
    except (ValueError, TypeError):
        fm["timeout"] = 600
    try:
        fm["max_turns"] = int(fm.get("max_turns", 30))
    except (ValueError, TypeError):
        fm["max_turns"] = 30

    # Ensure match is a dict with expected keys
    if not isinstance(fm.get("match"), dict):
        fm["match"] = {"task_type": [], "domains": [], "title_patterns": [], "description_patterns": []}
    for k in ("task_type", "domains", "title_patterns", "description_patterns"):
        if k not in fm["match"]:
            fm["match"][k] = []
        if not isinstance(fm["match"][k], list):
            fm["match"][k] = []

    # Ensure skills and allowed_tools are lists
    for k in ("skills", "allowed_tools"):
        if not isinstance(fm.get(k), list):
            fm[k] = []

    fm["prompt_body"] = body
    return fm, body


def load_workers():
    """Load all worker definitions from scripts/workers/. Returns list sorted by priority desc."""
    workers = []
    if not os.path.isdir(WORKERS_DIR):
        log("WARNING: Workers directory not found, using fallback default worker")
        return [_FALLBACK_DEFAULT_WORKER]

    for path in sorted(globmod.glob(os.path.join(WORKERS_DIR, "*.md"))):
        fm, body = _parse_worker_frontmatter(path)
        if fm and fm.get("name"):
            workers.append(fm)
        else:
            log(f"WARNING: Could not parse worker file: {os.path.basename(path)}")

    if not workers:
        log("WARNING: No valid worker files found, using fallback default worker")
        return [_FALLBACK_DEFAULT_WORKER]

    # Sort by priority descending (higher priority checked first)
    workers.sort(key=lambda w: w.get("priority", 0), reverse=True)
    return workers


_WORKER_MATCH_PROMPT = """You are a task router for a PM automation system. Given a task and a list of available workers, select the single best worker to handle it.

## Available Workers

{worker_list}

## Task to Route

Title: {title}
Queue: {queue}
Domain: {domain}
Task Type: {task_type}
Description: {description}

## Instructions

Pick the ONE worker best suited for this task based on its description, domain, and intent.
Consider what tools and skills the worker needs — e.g., meeting scheduling needs M365,
data analysis needs Pendo/Databricks, document creation needs writing workflows.

Routing rules:
- "Talk to [person]", "chat with", "meet with", "sync with", "connect with", "catch up with" → ALWAYS route to scheduler. These mean "schedule a meeting."
- Tasks in the collab queue that involve a person by name are almost always meetings → scheduler.
- Software bugs, defects, feature requests, QA items → ALWAYS route to ticket-creator. The ticket-creator drafts a Jira ticket.
- "verify [something] bug", "fix [something]", "file ticket", "[something] display bug", "[something] retention policy" → ticket-creator, NOT researcher.
- If the title contains "bug", "defect", "error", "broken", "fix", or describes a software problem → ticket-creator.

Return ONLY valid JSON with these fields:
{{
  "worker": "worker-name",
  "reason": "One sentence explaining why this worker is the best match"
}}

No markdown, no code fences, no explanation outside the JSON."""


def _match_worker_llm(task, workers):
    """Use Claude Haiku to match a task to the best worker. Returns (worker, reason) or (None, None)."""
    try:
        from parse_task_input import call_claude, extract_json, PARSER_MODEL
    except ImportError:
        return None, None

    # Build worker list for the prompt
    worker_descs = []
    for w in workers:
        name = w.get("name", "unknown")
        desc = w.get("description", "")
        domains = ", ".join(w.get("match", {}).get("domains", []))
        task_types = ", ".join(w.get("match", {}).get("task_type", []))
        tools_summary = ", ".join(w.get("allowed_tools", []))
        worker_descs.append(
            f"- **{name}**: {desc}"
            + (f" | Domains: {domains}" if domains else "")
            + (f" | Task types: {task_types}" if task_types else "")
        )
    worker_list = "\n".join(worker_descs)

    # Get task description if available
    description = ""
    task_id = task.get("id", "")
    if task_id:
        try:
            task_data = task_lib.read_task(task_id)
            description = (task_data.get("body", "") or "")[:500]  # cap to avoid huge prompts
        except Exception:
            pass

    # Try LangFuse prompt first, fall back to hardcoded
    prompt_template = _WORKER_MATCH_PROMPT
    try:
        from langfuse_client import fetch_prompt
        lf_prompt = fetch_prompt("worker-router", label="production")
        if lf_prompt is not None:
            prompt_template = lf_prompt.prompt
    except Exception:
        pass

    prompt = prompt_template.format(
        worker_list=worker_list,
        title=task.get("title", ""),
        queue=task.get("queue", ""),
        domain=task.get("domain", ""),
        task_type=task.get("task_type", ""),
        description=description or "(no description)",
    )

    try:
        raw = call_claude(prompt, "Route this task to the best worker.", model=PARSER_MODEL)
        result = extract_json(raw)
        worker_name = result.get("worker", "")
        reason = result.get("reason", "")
        return worker_name, reason
    except Exception as e:
        log(f"LLM worker match failed: {e}")
        return None, None


def match_worker(task, workers):
    """Match a task to the best worker using LLM, with regex fallback."""
    title = task.get("title", "")
    task_type = task.get("task_type") or ""
    domain = task.get("domain") or ""

    # Try LLM-based matching first
    llm_name, llm_reason = _match_worker_llm(task, workers)
    if llm_name:
        for w in workers:
            if w.get("name") == llm_name:
                log(f"LLM matched worker: {llm_name} — {llm_reason}")
                return w, 100, [f"llm: {llm_reason}"]
        log(f"LLM returned unknown worker '{llm_name}', falling back to regex")

    # Regex fallback (claude CLI unavailable, unknown worker name, etc.)
    log("Using regex fallback for worker matching")
    best_worker = None
    best_score = -999
    match_reasons = []

    for worker in workers:
        score = 0
        reasons = []
        m = worker.get("match", {})

        # 1. Exact task_type match (+100)
        type_list = m.get("task_type", [])
        if type_list and task_type in type_list:
            score += 100
            reasons.append(f"task_type={task_type} +100")

        # 2. Domain match (+20 or -50)
        domain_list = m.get("domains", [])
        if domain_list:
            if domain in domain_list:
                score += 20
                reasons.append(f"domain={domain} +20")
            elif domain:
                score -= 50
                reasons.append(f"domain={domain} not in {domain_list} -50")

        # 3. Title pattern match (+30 per hit, max 60)
        title_hits = 0
        for pattern in m.get("title_patterns", []):
            try:
                if re.search(pattern, title):
                    title_hits += 1
                    reasons.append(f"title~/{pattern}/ +30")
                    if title_hits >= 2:
                        break
            except re.error:
                pass
        score += title_hits * 30

        if score > best_score:
            best_score = score
            best_worker = worker
            match_reasons = reasons

    # Fall back to default if nothing scored positively
    if best_score <= 0 or best_worker is None:
        for w in workers:
            if w.get("name") == "default":
                return w, 0, ["fallback to default"]
        return _FALLBACK_DEFAULT_WORKER, 0, ["no workers matched, using fallback"]

    return best_worker, best_score, match_reasons


def build_skills_catalog_filtered(skill_paths):
    """Build skills catalog containing only the specified skill paths."""
    if not skill_paths:
        return build_skills_catalog()  # empty filter = full catalog

    catalog_lines = []
    skills_dir = os.path.join(PM_OS_DIR, ".claude", "skills")
    if not os.path.isdir(skills_dir):
        return "(no skills directory found)"

    for rel_path in skill_paths:
        # Try both SKILL.md and skill.md
        for filename in ("SKILL.md", "skill.md"):
            full_path = os.path.join(skills_dir, rel_path, filename)
            if os.path.isfile(full_path):
                name, desc = parse_skill_frontmatter(full_path)
                if name and desc:
                    catalog_lines.append(f"- **{name}**: {desc}")
                break

    return "\n".join(catalog_lines) if catalog_lines else build_skills_catalog()


def build_prompt_for_worker(task_id, worker, rerun=False):
    """Build the dispatch prompt using a worker definition.

    Tries LangFuse prompt first, falls back to worker's inline markdown body.
    """
    # Build filtered skills catalog
    skill_paths = worker.get("skills", [])
    skills_catalog = build_skills_catalog_filtered(skill_paths)

    # Build rerun block
    rerun_block = """
9. RERUN CONTEXT (this task has been run before):
   This is a RERUN — you are retrying a task that previously completed or failed
   but the output was not satisfactory. When you read the task with `task.sh show`,
   pay special attention to the Activity Log section at the bottom:
   - Look for entries by "human" — especially [comment] entries. These contain
     corrections and clarifications about what went wrong in the previous attempt.
   - The most recent human comment before the "Task reset for agent rerun." entry
     is the PRIMARY guidance for what to do differently this time.
   - Treat human comments as HIGHER PRIORITY than the original description when
     they conflict — the human is telling you what to fix.
   - Read any previous agent output file if referenced — understand what was
     produced before so you can improve on it rather than starting blind.
   - Do NOT repeat the same approach that failed. Address the feedback explicitly.

""" if rerun else ""

    # Try LangFuse prompt management (get latest version text)
    prompt_text = None
    try:
        from langfuse_client import fetch_prompt
        lf_prompt = fetch_prompt(worker.get("langfuse_prompt", ""), label="production")
        if lf_prompt is not None:
            prompt_text = lf_prompt.prompt
            if not isinstance(prompt_text, str):
                prompt_text = str(prompt_text) if prompt_text else None
    except Exception:
        pass

    # Use LangFuse text if available, otherwise worker's inline body
    if prompt_text is None:
        prompt_text = worker.get("prompt_body") or ""

    # Final fallback: legacy build_prompt()
    if not prompt_text:
        return build_prompt(task_id, rerun=rerun)

    # Substitute template variables
    prompt_body = prompt_text.replace("{task_id}", task_id) \
                             .replace("{skills_catalog}", skills_catalog) \
                             .replace("{rerun_block}", rerun_block)

    return prompt_body


# ─── Task Dispatch ────────────────────────────────────────────────────────────

def _kill_process_group(proc):
    """Send SIGTERM to the process group, escalate to SIGKILL if needed."""
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except OSError:
        pass
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except OSError:
            pass
        proc.wait()


def build_prompt(task_id, rerun=False):
    """Build the prompt string sent to `claude -p` for a given task."""
    skills_catalog = build_skills_catalog()

    rerun_block = """
9. RERUN CONTEXT (this task has been run before):
   This is a RERUN — you are retrying a task that previously completed or failed
   but the output was not satisfactory. When you read the task with `task.sh show`,
   pay special attention to the Activity Log section at the bottom:
   - Look for entries by "human" — especially [comment] entries. These contain
     corrections and clarifications about what went wrong in the previous attempt.
   - The most recent human comment before the "Task reset for agent rerun." entry
     is the PRIMARY guidance for what to do differently this time.
   - Treat human comments as HIGHER PRIORITY than the original description when
     they conflict — the human is telling you what to fix.
   - Read any previous agent output file if referenced — understand what was
     produced before so you can improve on it rather than starting blind.
   - Do NOT repeat the same approach that failed. Address the feedback explicitly.

""" if rerun else ""

    return f"""You are the PM-OS agent working in ~/pm-os/. Read and follow CLAUDE.md.

## Available Skills

The following skills are available at .claude/skills/. Before starting work,
identify the most relevant skill, read its SKILL.md, and follow it exactly.

{skills_catalog}

Your assignment is task {task_id}. Follow these steps:

0. Read CLAUDE.md in the project root to understand the system.

1. Read the full task:
   Run: ./scripts/task.sh show {task_id}
   This gives you the title, description, acceptance criteria, and activity log.
   Pay close attention to:
   - The `source_meeting` field — if present, READ THAT TRANSCRIPT. It contains
     the context behind this task. Find it under datasets/meetings/.
   - The description — it may reference a specific PM-OS skill or workflow to use
     (e.g., "Use strategy-session skill", "Use research-gathering skill").
   - Any referenced files or datasets paths — read them for context.

2. Identify and load the relevant skill:
   Based on the task's domain and description, find the best-matching skill
   from the catalog above. Read its full SKILL.md at
   .claude/skills/<category>/<skill-name>/SKILL.md and follow its workflow.
   You MUST scan .claude/skills/ for a relevant skill before starting work.

3. Mark it started:
   Run: ./scripts/task.sh agent:start {task_id}

4. Gather context:
   - If there is a source_meeting, read the transcript file to understand the
     full context of what was discussed and what Jay needs.
   - If the description references other files, read those too.
   - Follow the skill's workflow for context gathering if it defines one.

5. Do the work:
   - Produce the requested output as a file on disk.
   - Follow the loaded skill's workflow exactly.
   - Write output artifacts to the appropriate datasets/ directory.

6. If you get stuck or need human input:
   Run: ./scripts/task.sh agent:ask {task_id} "your specific question"
   Then STOP immediately. Do not continue working on the task.

7. When the work is complete:
   Run: ./scripts/task.sh agent:complete {task_id} --output "path/to/output"
   where the output path points to the primary artifact you created.

8. If you encounter an unrecoverable error:
   Run: ./scripts/task.sh agent:fail {task_id} --error "description of what went wrong"

{rerun_block}Important rules:
- Always start by reading CLAUDE.md, then the task, then the source meeting transcript if one exists.
- Identify and follow the relevant skill before doing any work.
- Write outputs to disk in the appropriate datasets/ directory — do not just print them.
- Be thorough but concise. Prefer completing the task over asking questions.
- If you ask a question, STOP immediately after. Do not guess the answer."""


def dispatch_task(task, dry_run=False, rerun=False, workers=None):
    """Invoke claude in interactive mode for a single task.

    Uses interactive mode (not -p) to get full cloud MCP access (Pendo, Jira,
    Microsoft 365, etc.). Wraps in `script` to provide a pseudo-TTY since
    interactive mode requires a terminal.

    Returns a dict with keys: task_id, success, output, error.
    """
    task_id = task.get("id", "UNKNOWN")
    title = task.get("title", "(no title)")
    priority = task.get("priority", "medium")

    # ─── Worker matching ─────────────────────────────────────────────
    worker = None
    if workers:
        worker, score, reasons = match_worker(task, workers)
        log(f"Matched worker: {worker['name']} (score={score}, reasons={reasons})", task_id=task_id)

    if dry_run:
        worker_name = worker["name"] if worker else "default"
        log(f"DRY-RUN: Would dispatch {task_id} [{priority}] — {title} [worker={worker_name}]", task_id=task_id)
        return {"task_id": task_id, "success": True, "output": "(dry run)", "error": None}

    log(f"Dispatching{' (rerun)' if rerun else ''}: {task_id} [{priority}] — {title}", task_id=task_id)

    # ─── LangFuse tracing: worker-match ──────────────────────────────
    match_trace = None
    exec_trace = None
    rerun_label = " (rerun)" if rerun else ""
    try:
        from langfuse_client import create_trace, end_trace, flush as lf_flush
        if worker:
            match_trace = create_trace(
                name=f"worker-match{rerun_label}",
                session_id=task_id,
                metadata={
                    "task_title": title,
                    "task_domain": task.get("domain"),
                    "task_type": task.get("task_type"),
                    "allowed_tools": worker.get("allowed_tools", []),
                },
                tags=[f"worker:{worker['name']}", f"domain:{task.get('domain', 'none')}"],
                input_data={"title": title, "domain": task.get("domain"), "task_type": task.get("task_type")},
                output_data={"worker": worker["name"], "score": score, "reasons": reasons},
            )
    except Exception:
        pass

    # ─── Build prompt and tool list from worker ──────────────────────
    if worker and worker.get("prompt_body"):
        prompt = build_prompt_for_worker(task_id, worker, rerun=rerun)
        tools_str = ",".join(worker.get("allowed_tools", []))
        max_turns = str(worker.get("max_turns", 30))
    else:
        prompt = build_prompt(task_id, rerun=rerun)
        tools_str = "Bash(*),Read(*),Write(*),Edit(*),WebFetch(*),WebSearch(*),Agent(*),mcp__*"
        max_turns = "30"

    output_file = os.path.join(LOG_DIR, f"dispatch-{task_id}.log")

    # ─── LangFuse tracing: worker-execution (start) ─────────────────
    try:
        from langfuse_client import create_trace
        worker_name = worker["name"] if worker else "default"
        exec_trace = create_trace(
            name=f"worker-execution ({worker_name}){rerun_label}",
            session_id=task_id,
            metadata={"worker": worker_name, "rerun": rerun, "priority": priority},
            tags=[f"worker:{worker_name}", f"priority:{priority}"],
            input_data={"worker": worker_name, "tools": tools_str, "max_turns": max_turns, "prompt_length": len(prompt)},
        )
    except Exception:
        pass

    # Interactive mode (no -p) gets cloud MCPs (Pendo, Jira, M365, etc.)
    # Use `script` to provide a pseudo-TTY for the interactive TUI
    claude_cmd = [
        "claude",
        prompt,
        "--allowedTools", tools_str,
        "--max-turns", max_turns,
        "--permission-mode", "bypassPermissions",
    ]

    # Wrap in `script -q` to provide pseudo-TTY
    cmd = [
        "script", "-q", output_file,
    ] + claude_cmd

    # Strip ALL Claude-related env vars to prevent nested-session detection,
    # and ensure ~/.local/bin (claude) and /opt/homebrew/bin are in PATH for cron
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("CLAUDE", "CMUX_CLAUDE"))}
    env["PATH"] = (
        os.path.join(os.path.expanduser("~"), ".local", "bin")
        + ":/opt/homebrew/bin"
        + ":" + env.get("PATH", "/usr/bin:/bin")
    )

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=PM_OS_DIR,
            env=env,
            start_new_session=True,  # own process group for clean kill
        )
    except FileNotFoundError:
        log("ERROR: 'claude' or 'script' command not found in PATH", task_id=task_id)
        return {"task_id": task_id, "success": False, "output": None, "error": "claude not found"}

    # Poll: wait for process exit OR agent to report completion via task file.
    # The claude interactive process often hangs after the agent finishes, so we
    # detect completion by reading the task's agent_status and kill the process.
    TIMEOUT = worker.get("timeout", 600) if worker else 600
    POLL_INTERVAL = 5    # check task file every 5s
    POLL_DELAY = 30      # give agent time to start before polling
    TERMINAL_STATUSES = ("complete", "failed", "needs-human")

    start = time.monotonic()
    agent_done = False
    retcode = None

    while True:
        retcode = proc.poll()
        if retcode is not None:
            break  # process exited naturally

        elapsed = time.monotonic() - start

        # Hard timeout
        if elapsed >= TIMEOUT:
            log("TIMEOUT: Task exceeded 10 minute limit", task_id=task_id)
            _kill_process_group(proc)
            break

        # Poll task file after initial delay
        if elapsed >= POLL_DELAY:
            try:
                task_data = task_lib.read_task(task_id)
                agent_status = task_data["frontmatter"].get("agent_status")
                if agent_status in TERMINAL_STATUSES:
                    log(f"Agent reported '{agent_status}' — terminating process",
                        task_id=task_id)
                    agent_done = True
                    _kill_process_group(proc)
                    break
            except Exception:
                pass

        time.sleep(POLL_INTERVAL)

    # Read output from the script log file
    task_output = None
    try:
        with open(output_file, "r", encoding="utf-8", errors="replace") as f:
            task_output = f.read()[-2000:]
    except OSError:
        pass

    elapsed = time.monotonic() - start

    # Helper: end the execution trace with result
    def _finish_exec_trace(success, error=None):
        if exec_trace is None:
            return
        try:
            from langfuse_client import end_trace, flush as lf_flush
            end_trace(exec_trace,
                output={"success": success, "error": error, "duration_seconds": round(elapsed, 1)},
                level="ERROR" if not success else "DEFAULT",
            )
            lf_flush()
        except Exception:
            pass

    # Determine result
    if agent_done:
        log("Completed (agent self-reported)", task_id=task_id)
        _finish_exec_trace(True)
        return {"task_id": task_id, "success": True, "output": task_output, "error": None}

    if retcode is not None and retcode == 0:
        log("Completed successfully", task_id=task_id)
        _finish_exec_trace(True)
        return {"task_id": task_id, "success": True, "output": task_output, "error": None}

    # Timeout or non-zero exit — check if agent already completed before marking failed
    try:
        task_data = task_lib.read_task(task_id)
        current_status = task_data["frontmatter"].get("agent_status")
        if current_status in ("complete", "needs-human"):
            log(f"Agent already '{current_status}' — not marking failed", task_id=task_id)
            _finish_exec_trace(True)
            return {"task_id": task_id, "success": True, "output": task_output, "error": None}
    except Exception:
        pass

    # Genuinely failed or timed-out
    error_msg = (
        "Dispatch timeout: exceeded 10 minute limit"
        if retcode is None
        else f"exit code {retcode}"
    )
    try:
        subprocess.run(
            [TASK_SH, "agent:fail", task_id, "--error", error_msg],
            cwd=PM_OS_DIR,
            timeout=10,
        )
    except Exception:
        pass
    log(f"Failed: {error_msg}", task_id=task_id)
    _finish_exec_trace(False, error=error_msg)
    return {"task_id": task_id, "success": False, "output": task_output, "error": error_msg}


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="task_dispatch",
        description="PM-OS headless task dispatcher — invokes Claude Code for agent queue tasks.",
    )
    parser.add_argument(
        "--task",
        metavar="TASK-NNNN",
        default=None,
        help="Process only this specific task (skip queue scan)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be dispatched without invoking Claude Code",
    )
    parser.add_argument(
        "--rerun",
        action="store_true",
        help="Indicate this is a rerun — agent will prioritize activity log feedback",
    )
    args = parser.parse_args()

    # Acquire lock
    lock_fd = acquire_lock()
    if lock_fd is None:
        log("Another dispatcher is already running. Exiting.")
        sys.exit(0)

    try:
        log("Dispatcher started" + (" (dry-run)" if args.dry_run else ""))

        # Load worker definitions
        workers = load_workers()
        log(f"Loaded {len(workers)} worker(s): {', '.join(w['name'] for w in workers)}")

        # Determine which tasks to process
        if args.task:
            # Single-task mode: build a minimal task dict and dispatch directly
            task_id = args.task.upper()
            log(f"Single-task mode: {task_id}", task_id=task_id)
            # Try to read full task metadata for better worker matching
            try:
                task_data = task_lib.read_task(task_id)
                fm = task_data.get("frontmatter", {})
                task = {
                    "id": task_id,
                    "title": fm.get("title", "(single dispatch)"),
                    "priority": fm.get("priority", "medium"),
                    "domain": fm.get("domain"),
                    "task_type": fm.get("task_type"),
                }
            except Exception:
                task = {"id": task_id, "title": "(single dispatch)", "priority": "medium"}
            results = [dispatch_task(task, dry_run=args.dry_run, rerun=args.rerun, workers=workers)]
        else:
            # Normal mode: scan the agent queue for actionable tasks
            tasks = get_actionable_tasks()
            if not tasks:
                log("No actionable tasks found in agent queue.")
                return

            log(f"Found {len(tasks)} actionable task(s)")

            # Process sequentially, highest priority first (already sorted)
            results = []
            for task in tasks:
                result = dispatch_task(task, dry_run=args.dry_run, workers=workers)
                results.append(result)

        # Summary
        succeeded = sum(1 for r in results if r["success"])
        failed = sum(1 for r in results if not r["success"])
        log(f"Dispatcher finished: {succeeded} succeeded, {failed} failed, {len(results)} total")

    finally:
        release_lock(lock_fd)


if __name__ == "__main__":
    main()
