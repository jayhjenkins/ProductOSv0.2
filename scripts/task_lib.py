#!/usr/bin/env python3
"""
task_lib.py — Shared library for PM-OS task management.

All file operations (read, write, parse, walk, validate, move, archive)
live here. Both task_cli.py and task_server.py import this library.
One implementation, zero duplication, zero drift.
"""

import os
import sys
import fcntl
import shutil
import re
from datetime import datetime, timezone
from pathlib import Path
from io import StringIO

from ruamel.yaml import YAML

# ─── Load LangFuse env vars if not already set ───────────────────────────────
_PM_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env_langfuse = os.path.join(_PM_OS_DIR, ".env.langfuse")
if not os.environ.get("LANGFUSE_SECRET_KEY") and os.path.isfile(_env_langfuse):
    with open(_env_langfuse) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _line = _line.removeprefix("export ")
                _key, _, _val = _line.partition("=")
                os.environ[_key.strip()] = _val.strip()

# ─── Constants ───────────────────────────────────────────────────────────────

TASKS_DIR = os.path.join(_PM_OS_DIR, "datasets", "tasks")
COUNTER_FILE = os.path.join(TASKS_DIR, "_counter")
PROCESSED_MEETINGS_FILE = os.path.join(TASKS_DIR, "_processed-meetings.txt")
ARCHIVE_DIR = os.path.join(TASKS_DIR, "_archive")

QUEUES = ["human", "agent", "collab", "waiting"]
STATUSES = ["open", "in-progress", "blocked", "done", "cancelled"]
PRIORITIES = ["critical", "high", "medium", "low"]
DOMAINS = ["product", "strategy", "marketing", "recruiting", "metrics", "learning", "ops"]
AGENT_STATUSES = ["queued", "running", "blocked", "needs-human", "complete", "failed"]

PRIORITY_ORDER = {p: i for i, p in enumerate(PRIORITIES)}

yaml = YAML()
yaml.preserve_quotes = True
yaml.width = 4096  # prevent line wrapping


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _now_iso():
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _queue_dir(queue):
    """Return absolute path to a queue directory."""
    return os.path.join(TASKS_DIR, queue)


def _find_task_file(task_id):
    """Find a task file across all queues. Returns (path, queue) or (None, None)."""
    for q in QUEUES:
        path = os.path.join(_queue_dir(q), f"{task_id}.md")
        if os.path.exists(path):
            return path, q
    return None, None


def _parse_task_file(filepath):
    """Parse a task file into (frontmatter_dict, body_string).

    Returns (dict, str) where dict is the YAML frontmatter and str is the
    markdown body after the closing ---.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        raise ValueError(f"Task file missing YAML frontmatter: {filepath}")

    # Split on the second ---
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Task file has malformed frontmatter: {filepath}")

    fm_str = parts[1]
    body = parts[2]

    fm = yaml.load(fm_str)
    if fm is None:
        fm = {}

    return fm, body


def _write_task_file(filepath, frontmatter, body):
    """Write a task file with YAML frontmatter + markdown body.

    Includes YAML validation gate: after writing, parses back to verify.
    On failure, reverts and raises.
    """
    # Backup existing content for revert
    backup = None
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            backup = f.read()

    # Serialize frontmatter
    stream = StringIO()
    yaml.dump(frontmatter, stream)
    fm_str = stream.getvalue()

    content = f"---\n{fm_str}---\n{body}"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    # YAML validation gate: parse back to verify
    try:
        _parse_task_file(filepath)
    except Exception as e:
        # Revert on failure
        if backup is not None:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(backup)
        else:
            os.remove(filepath)
        raise ValueError(f"YAML validation failed after write: {e}")


def _sharepoint_path(local_path):
    """Return the SharePoint/OneDrive docx path for a local file, or None.

    Non-critical: returns None silently if doc_sync is not configured.
    """
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "doc_sync", os.path.join(os.path.dirname(__file__), "doc_sync.py"))
        doc_sync = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(doc_sync)
        return doc_sync.sharepoint_path_for(local_path)
    except Exception:
        return None


def _sharepoint_url(local_path):
    """Return a browser-openable SharePoint/OneDrive URL for a local file, or None.

    Non-critical: returns None silently if doc_sync is not configured or URL config is missing.
    """
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "doc_sync", os.path.join(os.path.dirname(__file__), "doc_sync.py"))
        doc_sync = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(doc_sync)
        return doc_sync.sharepoint_url_for(local_path)
    except Exception:
        return None


def _sharepoint_url_from_docx(docx_path):
    """Convert a local OneDrive docx path to a browser-openable SharePoint URL, or None."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "doc_sync", os.path.join(os.path.dirname(__file__), "doc_sync.py"))
        doc_sync = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(doc_sync)
        return doc_sync.sharepoint_url_from_docx_path(docx_path)
    except Exception:
        return None


def _trigger_doc_sync(local_path):
    """Trigger async doc sync for an output artifact. Fire-and-forget."""
    try:
        import subprocess
        sync_script = os.path.join(os.path.dirname(__file__), "doc_sync.py")
        subprocess.Popen(
            ["python3", sync_script, "sync-one", str(local_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass  # Non-critical, don't break task completion


def _next_id():
    """Atomically read, increment, and return next task ID.

    Uses fcntl.flock on _counter for concurrency safety.
    Returns string like 'TASK-0042'.
    """
    fd = open(COUNTER_FILE, "r+")
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        current = int(fd.read().strip())
        task_id = f"TASK-{current:04d}"
        fd.seek(0)
        fd.write(str(current + 1))
        fd.truncate()
        return task_id
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        fd.close()


# ─── Core Operations ─────────────────────────────────────────────────────────

def create_task(title, queue="human", priority="medium", domain=None,
                due=None, tags=None, creator="human", description="",
                acceptance_criteria="", source_meeting=None, project=None,
                waiting_on=None, waiting_expected=None,
                task_type=None, meeting_attendees=None,
                meeting_duration=None, meeting_title=None,
                meeting_description=None, message_channel=None,
                message_to=None, message_subject=None, message_body=None):
    """Create a new task file in the appropriate queue directory.

    Returns (task_id, filepath).
    """
    # Validate inputs
    if not title or len(title) > 200:
        raise ValueError("Title must be non-empty and max 200 characters")
    if queue not in QUEUES:
        raise ValueError(f"Queue must be one of: {QUEUES}")
    if priority not in PRIORITIES:
        raise ValueError(f"Priority must be one of: {PRIORITIES}")
    if domain and domain not in DOMAINS:
        raise ValueError(f"Domain must be one of: {DOMAINS}")

    task_id = _next_id()
    now = _now_iso()

    # Determine assignee from queue
    assignee_map = {"human": "human", "agent": "agent", "collab": "both", "waiting": "human"}
    assignee = assignee_map[queue]

    frontmatter = {
        "id": task_id,
        "title": title,
        "status": "open",
        "queue": queue,
        "priority": priority,
        "created": now,
        "updated": now,
        "due": due,
        "creator": creator,
        "assignee": assignee,
        "domain": domain,
        "source_meeting": source_meeting,
        "source_epic": None,
        "project": project,
        "tags": tags or [],
        "agent_status": None,
        "agent_output": None,
        "agent_error": None,
        "agent_started": None,
        "agent_completed": None,
        "blocked_by": [],
        "blocks": [],
    }

    # Add waiting metadata if applicable
    if queue == "waiting":
        frontmatter["waiting_on"] = waiting_on
        frontmatter["waiting_since"] = now[:10]  # just the date
        frontmatter["waiting_expected"] = waiting_expected
    else:
        frontmatter["waiting_on"] = None
        frontmatter["waiting_since"] = None
        frontmatter["waiting_expected"] = None

    # Add scheduling metadata if applicable
    if task_type:
        frontmatter["task_type"] = task_type
    if task_type == "schedule-meeting":
        frontmatter["meeting_attendees"] = meeting_attendees or []
        frontmatter["meeting_duration"] = meeting_duration or 30
        frontmatter["meeting_title"] = meeting_title or title
        frontmatter["meeting_description"] = meeting_description or ""
        frontmatter["meeting_recurring"] = False
        frontmatter["meeting_recurrence_pattern"] = None
        frontmatter["meeting_selected_slot"] = None
        frontmatter["meeting_event_id"] = None
    if task_type == "send-message":
        frontmatter["message_channel"] = message_channel
        frontmatter["message_to"] = message_to
        frontmatter["message_subject"] = message_subject
        frontmatter["message_body"] = message_body

    # Build body
    body_parts = ["\n## Description\n"]
    if description:
        body_parts.append(f"\n{description}\n")
    else:
        body_parts.append("\n(No description provided)\n")

    if acceptance_criteria:
        body_parts.append(f"\n## Acceptance Criteria\n\n{acceptance_criteria}\n")

    body_parts.append(f"\n## Activity Log\n")
    body_parts.append(f"\n### {now} — {creator}\nCreated task.\n")

    body = "\n".join(body_parts)

    filepath = os.path.join(_queue_dir(queue), f"{task_id}.md")
    _write_task_file(filepath, frontmatter, body)

    # ─── LangFuse trace: task-creation ────────────────────────────────
    # Creates a trace linked to the task ID so users can evaluate the
    # extraction/classification decision (right queue? right priority?)
    # For meeting-extracted tasks, also creates a trace linked to the
    # source meeting so all extractions from one transcript are grouped.
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from langfuse_client import create_trace

        trace_tags = [f"queue:{queue}", f"priority:{priority}", f"creator:{creator}"]
        if source_meeting:
            trace_tags.append("meeting-extraction")

        # Trace linked to the task (shows in task's pipeline view)
        create_trace(
            name="task-creation",
            session_id=task_id,
            metadata={
                "queue": queue,
                "priority": priority,
                "domain": domain,
                "creator": creator,
                "task_type": task_type,
                "source_meeting": source_meeting,
            },
            tags=trace_tags,
            input_data={"title": title, "description": description[:500] if description else None,
                        "source_meeting": source_meeting},
            output_data={"task_id": task_id, "queue": queue, "priority": priority, "domain": domain},
        )

        # If extracted from a meeting, also create a trace linked to the
        # source meeting so all extractions are grouped together
        if source_meeting:
            meeting_name = os.path.basename(source_meeting) if source_meeting else None
            create_trace(
                name="meeting-task-extraction",
                session_id=f"meeting:{meeting_name}",
                metadata={
                    "source_meeting": source_meeting,
                    "task_id": task_id,
                    "queue": queue,
                    "priority": priority,
                    "domain": domain,
                    "task_type": task_type,
                },
                tags=["meeting-extraction", f"queue:{queue}"],
                input_data={"source_meeting": source_meeting,
                            "title": title,
                            "description": description[:500] if description else None},
                output_data={"task_id": task_id, "queue": queue, "priority": priority, "domain": domain},
            )
    except Exception:
        pass

    return task_id, filepath


def read_task(task_id):
    """Read and parse a task file. Returns dict with frontmatter + body."""
    filepath, queue = _find_task_file(task_id)
    if filepath is None:
        # Also check archive
        for root, dirs, files in os.walk(ARCHIVE_DIR):
            for f in files:
                if f == f"{task_id}.md":
                    filepath = os.path.join(root, f)
                    queue = "_archive"
                    break
            if filepath:
                break
    if filepath is None:
        raise FileNotFoundError(f"Task {task_id} not found")

    fm, body = _parse_task_file(filepath)
    return {
        "frontmatter": fm,
        "body": body,
        "filepath": filepath,
        "queue": queue,
    }


def list_tasks(queue=None, status=None, domain=None, priority=None,
               include_archive=False):
    """Walk queue directories, parse frontmatter, return filtered list.

    Returns list of dicts with key frontmatter fields + file path.
    """
    results = []
    queues_to_scan = [queue] if queue else QUEUES

    for q in queues_to_scan:
        qdir = _queue_dir(q)
        if not os.path.isdir(qdir):
            continue
        for fname in os.listdir(qdir):
            if not fname.startswith("TASK-") or not fname.endswith(".md"):
                continue
            filepath = os.path.join(qdir, fname)
            try:
                fm, _ = _parse_task_file(filepath)
            except Exception:
                continue  # skip malformed files

            # Apply filters
            if status and fm.get("status") != status:
                continue
            if domain and fm.get("domain") != domain:
                continue
            if priority and fm.get("priority") != priority:
                continue

            results.append({
                "id": fm.get("id", fname.replace(".md", "")),
                "title": fm.get("title", ""),
                "queue": fm.get("queue", q),
                "priority": fm.get("priority", "medium"),
                "status": fm.get("status", "open"),
                "domain": fm.get("domain"),
                "due": fm.get("due"),
                "created": fm.get("created"),
                "updated": fm.get("updated"),
                "agent_status": fm.get("agent_status"),
                "agent_output": fm.get("agent_output"),
                "sharepoint_path": fm.get("sharepoint_path"),
                "waiting_on": fm.get("waiting_on"),
                "waiting_expected": fm.get("waiting_expected"),
                "source_meeting": fm.get("source_meeting"),
                "task_type": fm.get("task_type"),
                "judge_score": fm.get("judge_score"),
                "judge_why": fm.get("judge_why"),
                "judge_dimensions": fm.get("judge_dimensions"),
                "judge_rubric_version": fm.get("judge_rubric_version"),
                "judge_scored_at": fm.get("judge_scored_at"),
                "file": os.path.relpath(filepath, TASKS_DIR),
            })

    # Sort by priority (critical first), then by created (oldest first)
    results.sort(key=lambda t: (
        PRIORITY_ORDER.get(t["priority"], 99),
        t["created"] or "",
    ))

    return results


def list_archived(limit=200):
    """Walk the archive directory, parse frontmatter, return light task dicts.

    Returns a list of dicts (no markdown bodies) for completed/cancelled tasks
    that have been moved to _archive/YYYY-MM/. Sorted by 'updated' descending
    (newest first) and capped to `limit` items.
    """
    results = []

    if not os.path.isdir(ARCHIVE_DIR):
        return results

    for root, dirs, files in os.walk(ARCHIVE_DIR):
        for fname in files:
            if not fname.startswith("TASK-") or not fname.endswith(".md"):
                continue
            filepath = os.path.join(root, fname)
            try:
                fm, _ = _parse_task_file(filepath)
            except Exception:
                continue  # skip malformed files

            results.append({
                "id": fm.get("id", fname.replace(".md", "")),
                "title": fm.get("title", ""),
                "queue": fm.get("queue"),
                "status": fm.get("status"),
                "domain": fm.get("domain"),
                "updated": fm.get("updated"),
                "agent_output": fm.get("agent_output"),
                "sharepoint_path": fm.get("sharepoint_path"),
                "sharepoint_url": fm.get("sharepoint_url"),
                "source_meeting": fm.get("source_meeting"),
                "task_type": fm.get("task_type"),
                "judge_score": fm.get("judge_score"),
                "judge_why": fm.get("judge_why"),
                "judge_dimensions": fm.get("judge_dimensions"),
                "judge_rubric_version": fm.get("judge_rubric_version"),
                "judge_scored_at": fm.get("judge_scored_at"),
            })

    # Sort by updated descending (newest first); missing/None values sort last
    results.sort(key=lambda t: t["updated"] or "", reverse=True)

    return results[:limit]


def update_task(task_id, changes=None, comment=None, actor="human"):
    """Update a task's frontmatter fields and/or append an activity log entry.

    changes: dict of frontmatter fields to update
    comment: string to append as activity log entry
    actor: 'human' or 'agent'

    If 'queue' is in changes, the file is moved to the new queue directory.
    """
    filepath, current_queue = _find_task_file(task_id)
    if filepath is None:
        raise FileNotFoundError(f"Task {task_id} not found")

    fm, body = _parse_task_file(filepath)
    changes = changes or {}
    now = _now_iso()

    new_queue = changes.pop("queue", None)
    comment_type = changes.pop("_comment_type", "comment")

    # Apply frontmatter changes
    for key, value in changes.items():
        fm[key] = value
    fm["updated"] = now

    # Append activity log entry if comment provided
    if comment:
        body = body.rstrip("\n") + f"\n\n### {now} — {actor} [{comment_type}]\n{comment}\n"

    # Handle queue movement
    if new_queue and new_queue != current_queue:
        fm["queue"] = new_queue
        # Update assignee
        assignee_map = {"human": "human", "agent": "agent", "collab": "both", "waiting": "human"}
        fm["assignee"] = assignee_map.get(new_queue, fm.get("assignee"))

        # Add waiting metadata if moving to waiting
        if new_queue == "waiting" and not fm.get("waiting_since"):
            fm["waiting_since"] = now[:10]

        new_path = os.path.join(_queue_dir(new_queue), f"{task_id}.md")
        _write_task_file(new_path, fm, body)
        os.remove(filepath)
        return new_path
    else:
        _write_task_file(filepath, fm, body)
        return filepath


def complete_task(task_id, output_path=None, actor="human"):
    """Mark a task as done and move to _archive/YYYY-MM/."""
    filepath, queue = _find_task_file(task_id)
    if filepath is None:
        raise FileNotFoundError(f"Task {task_id} not found")

    fm, body = _parse_task_file(filepath)
    now = _now_iso()

    fm["status"] = "done"
    fm["updated"] = now
    if output_path:
        fm["agent_output"] = output_path
        # Compute SharePoint path and URL if doc sync is configured
        sp = _sharepoint_path(output_path)
        if sp:
            fm["sharepoint_path"] = sp
        sp_url = _sharepoint_url(output_path)
        if sp_url:
            fm["sharepoint_url"] = sp_url

    # Append completion log entry
    log_msg = "Task completed."
    if output_path:
        log_msg += f" Output: {output_path}"
    body = body.rstrip("\n") + f"\n\n### {now} — {actor} [status-change]\n{log_msg}\n"

    # Move to archive under YYYY-MM
    month_dir = os.path.join(ARCHIVE_DIR, now[:7])  # YYYY-MM
    os.makedirs(month_dir, exist_ok=True)
    archive_path = os.path.join(month_dir, f"{task_id}.md")

    _write_task_file(archive_path, fm, body)
    os.remove(filepath)

    # Trigger async doc sync if output has a SharePoint path
    if output_path and fm.get("sharepoint_path"):
        _trigger_doc_sync(output_path)

    return archive_path


def complete_and_delete_task(task_id, actor="human"):
    """Mark task done, archive it, and delete its output artifacts."""
    filepath, queue = _find_task_file(task_id)
    if filepath is None:
        raise FileNotFoundError(f"Task {task_id} not found")

    fm, body = _parse_task_file(filepath)
    now = _now_iso()

    # Collect paths to delete BEFORE modifying frontmatter
    files_deleted = []
    agent_output = fm.get("agent_output")
    sharepoint_path = fm.get("sharepoint_path")

    # Delete local markdown output
    if agent_output:
        pm_os_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        abs_output = os.path.join(pm_os_root, agent_output) if not os.path.isabs(agent_output) else agent_output
        abs_output = os.path.normpath(abs_output)
        if os.path.isfile(abs_output):
            os.remove(abs_output)
            files_deleted.append(agent_output)

    # Delete OneDrive docx
    if sharepoint_path and os.path.isfile(str(sharepoint_path)):
        os.remove(str(sharepoint_path))
        files_deleted.append(str(sharepoint_path))

    # Update frontmatter
    fm["status"] = "done"
    fm["updated"] = now

    # Append log entry
    deleted_str = ", ".join(files_deleted) if files_deleted else "no files found"
    log_msg = f"Task approved and output deleted. Removed: {deleted_str}"
    body = body.rstrip("\n") + f"\n\n### {now} — {actor} [status-change]\n{log_msg}\n"

    # Archive
    month_dir = os.path.join(ARCHIVE_DIR, now[:7])
    os.makedirs(month_dir, exist_ok=True)
    archive_path = os.path.join(month_dir, f"{task_id}.md")
    _write_task_file(archive_path, fm, body)
    os.remove(filepath)

    return archive_path, files_deleted


def cancel_task(task_id, reason="", actor="human"):
    """Mark a task as cancelled and move to _archive/YYYY-MM/."""
    filepath, queue = _find_task_file(task_id)
    if filepath is None:
        raise FileNotFoundError(f"Task {task_id} not found")

    fm, body = _parse_task_file(filepath)
    now = _now_iso()

    fm["status"] = "cancelled"
    fm["updated"] = now

    log_msg = "Task cancelled."
    if reason:
        log_msg += f" Reason: {reason}"
    body = body.rstrip("\n") + f"\n\n### {now} — {actor} [status-change]\n{log_msg}\n"

    month_dir = os.path.join(ARCHIVE_DIR, now[:7])
    os.makedirs(month_dir, exist_ok=True)
    archive_path = os.path.join(month_dir, f"{task_id}.md")

    _write_task_file(archive_path, fm, body)
    os.remove(filepath)

    return archive_path


def update_task_description(task_id, new_description, actor="human"):
    """Replace the ## Description section content in a task's body.

    Finds the text between '## Description' and the next '##' heading,
    replaces it with new_description, and appends an activity log entry.
    """
    filepath, queue = _find_task_file(task_id)
    if filepath is None:
        raise FileNotFoundError(f"Task {task_id} not found")

    fm, body = _parse_task_file(filepath)
    now = _now_iso()

    # Replace description section content
    pattern = r"(## Description\s*\n)(.*?)((?=\n## )|$)"
    replacement = rf"\g<1>\n{new_description}\n\n"
    new_body = re.sub(pattern, replacement, body, count=1, flags=re.DOTALL)

    # Append activity log
    new_body = new_body.rstrip("\n") + f"\n\n### {now} — {actor} [edit]\nUpdated description.\n"

    fm["updated"] = now
    _write_task_file(filepath, fm, new_body)
    return filepath


def get_task_full(task_id):
    """Return full task content as a formatted string (for 'show' command)."""
    filepath, queue = _find_task_file(task_id)
    if filepath is None:
        raise FileNotFoundError(f"Task {task_id} not found")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def get_inbox():
    """Generate an inbox digest showing what needs human attention.

    Returns a dict with:
    - agent_questions: tasks where agent needs human answer
    - agent_completed: tasks recently completed by agent
    - human_open: open tasks in human/collab queues
    - waiting: waiting queue with overdue flags
    - summary: count summary
    """
    all_tasks = list_tasks()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    agent_questions = [t for t in all_tasks
                       if t.get("agent_status") == "needs-human"]
    agent_completed = [t for t in all_tasks
                       if t.get("agent_status") == "complete" and t["status"] != "done"]
    human_open = [t for t in all_tasks
                  if t["queue"] in ("human", "collab") and t["status"] in ("open", "in-progress", "blocked")]
    waiting = [t for t in all_tasks if t["queue"] == "waiting"]

    # Flag overdue waiting items
    for t in waiting:
        exp = t.get("waiting_expected")
        if exp and str(exp) < today:
            t["overdue"] = True
        else:
            t["overdue"] = False

    # Summary counts
    status_counts = {}
    for t in all_tasks:
        s = t["status"]
        status_counts[s] = status_counts.get(s, 0) + 1

    return {
        "agent_questions": agent_questions,
        "agent_completed": agent_completed,
        "human_open": human_open,
        "waiting": waiting,
        "summary": status_counts,
        "total": len(all_tasks),
    }
