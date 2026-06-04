#!/usr/bin/env python3
"""
task_server.py — Local HTTP server for PM-OS task management.

Serves the task board web UI and exposes a JSON API backed by task_lib.py.
Runs on port 8742 using only Python stdlib.

API endpoints:
  GET  /api/tasks            — List non-archived tasks (filterable)
  GET  /api/tasks/{id}       — Full task detail with parsed activity log
  POST /api/tasks/{id}/done  — Mark task complete, move to archive
  POST /api/tasks/{id}/comment — Append activity log entry
"""

import json
import os
import re
import socket
import shlex
import subprocess
import sys
import traceback
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class ReusableHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True
    request_queue_size = 100

# Add script directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import task_lib
import cron_lib
import jira_publish
from cron_scheduler import CronScheduler

# ─── Load LangFuse env vars if not already set ───────────────────────────────
_PM_OS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env_langfuse = os.path.join(_PM_OS, ".env.langfuse")
if not os.environ.get("LANGFUSE_SECRET_KEY") and os.path.isfile(_env_langfuse):
    with open(_env_langfuse) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _line = _line.removeprefix("export ")
                _key, _, _val = _line.partition("=")
                os.environ[_key.strip()] = _val.strip()

# ─── Constants ────────────────────────────────────────────────────────────────

PORT = 8742
PM_OS_DIR = _PM_OS
UI_DIR = os.path.join(PM_OS_DIR, "ui", "task-board")

# Regex for parsing activity log entries:
#   ### 2026-02-26T12:00:00Z — human [comment]
#   The comment text here.
ACTIVITY_LOG_RE = re.compile(
    r"^###\s+(?P<timestamp>\S+)\s+[—-]+\s+(?P<actor>\S+)(?:\s+\[(?P<type>[^\]]+)\])?\s*\n(?P<content>(?:(?!^###\s).*\n?)*)",
    re.MULTILINE,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _json_response(handler, data, status=200):
    """Write a JSON HTTP response with CORS headers."""
    body = json.dumps(data, indent=2, default=str).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(body)


def _error_response(handler, message, status=400):
    """Write a JSON error response."""
    _json_response(handler, {"error": message}, status=status)


def _read_request_body(handler):
    """Read and parse JSON request body."""
    length = int(handler.headers.get("Content-Length", 0))
    if length == 0:
        return {}
    raw = handler.rfile.read(length)
    return json.loads(raw.decode("utf-8"))


def _parse_activity_log(body):
    """Parse the activity log section from a task's markdown body.

    Each entry follows:
        ### {ISO-timestamp} — {actor} [{type}]
        {content}

    Returns a list of dicts with keys: timestamp, actor, type, content.
    """
    entries = []
    for match in ACTIVITY_LOG_RE.finditer(body):
        entries.append({
            "timestamp": match.group("timestamp"),
            "actor": match.group("actor"),
            "type": match.group("type"),
            "content": match.group("content").strip(),
        })
    return entries


def _parse_task_id(path_segment):
    """Validate and normalize a task ID from a URL path segment.

    Accepts 'TASK-0001' format. Returns the ID string or None if invalid.
    """
    segment = path_segment.strip("/")
    if re.match(r"^TASK-\d{4,}$", segment):
        return segment
    return None


# ─── API Route Handlers ──────────────────────────────────────────────────────

def _enrich_sharepoint_url(task_dict):
    """Add sharepoint_url to a task dict if missing. Tries sharepoint_path first, then agent_output."""
    if task_dict.get("sharepoint_url"):
        return task_dict
    # Try from existing sharepoint_path (local docx path)
    if task_dict.get("sharepoint_path"):
        url = task_lib._sharepoint_url_from_docx(str(task_dict["sharepoint_path"]))
        if url:
            task_dict["sharepoint_url"] = url
            return task_dict
    # Fall back to computing from agent_output (markdown path)
    if task_dict.get("agent_output"):
        url = task_lib._sharepoint_url(str(task_dict["agent_output"]))
        if url:
            task_dict["sharepoint_url"] = url
    return task_dict


def handle_list_tasks(handler, query_params):
    """GET /api/tasks — Return all non-archived tasks as JSON."""
    queue = query_params.get("queue", [None])[0]
    status = query_params.get("status", [None])[0]
    domain = query_params.get("domain", [None])[0]
    priority = query_params.get("priority", [None])[0]

    try:
        tasks = task_lib.list_tasks(
            queue=queue,
            status=status,
            domain=domain,
            priority=priority,
            include_archive=False,
        )
        for t in tasks:
            _enrich_sharepoint_url(t)
        _json_response(handler, tasks)
    except Exception as e:
        _error_response(handler, f"Failed to list tasks: {e}", status=500)


def handle_list_activity(handler, query_params):
    """GET /api/activity — Return archived (completed/cancelled) tasks as JSON."""
    raw_limit = query_params.get("limit", ["200"])[0]
    try:
        limit = int(raw_limit)
    except (TypeError, ValueError):
        limit = 200

    try:
        tasks = task_lib.list_archived(limit=limit)
        for t in tasks:
            _enrich_sharepoint_url(t)
        _json_response(handler, tasks)
    except Exception as e:
        _error_response(handler, f"Failed to list activity: {e}", status=500)


# ─── Quality (shadow judge) ───────────────────────────────────────────────────

JUDGE_GOOD_THRESHOLD = 7  # judge_score >= this is "positive"; mirrors human 👍


def _task_type_of(task):
    """The scoreboard's grouping unit: explicit task_type, else domain."""
    return task.get("task_type") or task.get("domain") or "uncategorized"


def _human_feedback_for_task(lf, task_id, hf_by_trace):
    """Return human-feedback scores (👍/👎) across a task's traces, newest first.

    `hf_by_trace` is a prebuilt {traceId: [{value, comment}]} map (one global
    score pull, not one per task). Returns [] when none / LangFuse unavailable.
    """
    out = []
    try:
        result = lf.api.trace.list(session_id=task_id, order_by="timestamp.desc")
        traces = result.data if hasattr(result, "data") else []
        for t in traces:
            tid = getattr(t, "id", None)
            if tid in hf_by_trace:
                out.extend(hf_by_trace[tid])
    except Exception:
        pass
    return out


def handle_quality(handler):
    """GET /api/quality — Read-only shadow-judge scoreboard by task-type.

    Aggregates judged tasks (those with judge_score) into a row per task-type:
    count, average score, trend, per-dimension averages, and — where a human has
    thumbed the task's trace — judge↔you agreement %. Also returns the
    disagreement list (judge vs. you divergences) as evidence behind agreement.
    Agreement degrades gracefully to null when LangFuse is unavailable.
    """
    try:
        active = task_lib.list_tasks()
        archived = task_lib.list_archived(limit=1000)
    except Exception as e:
        _error_response(handler, f"Failed to gather tasks: {e}", status=500)
        return

    judged = [t for t in (active + archived) if t.get("judge_score") is not None]

    lf = _get_langfuse()

    # One global score pull → {traceId: [human-feedback]}, reused for every task.
    hf_by_trace = {}
    if lf is not None:
        try:
            from langfuse_client import list_scores
            for s in list_scores():
                if s.get("name") == "human-feedback":
                    try:
                        hf_by_trace.setdefault(s.get("traceId"), []).append(
                            {"value": float(s.get("value")), "comment": s.get("comment") or ""})
                    except (TypeError, ValueError):
                        pass
        except Exception:
            pass

    groups = {}
    disagreements = []

    for t in judged:
        gkey = _task_type_of(t)
        g = groups.setdefault(gkey, {
            "task_type": gkey, "count": 0, "scores": [], "scored_at": [],
            # Dimension keys are kind-specific (document vs message); collect
            # whatever keys appear so the scoreboard isn't locked to one set.
            "dimensions": {},
            "phase": "Shadow", "agree": 0, "disagree": 0,
        })
        try:
            score = float(t["judge_score"])
        except (TypeError, ValueError):
            continue
        g["count"] += 1
        g["scores"].append(score)
        g["scored_at"].append(t.get("judge_scored_at") or "")
        dims = t.get("judge_dimensions") or {}
        if isinstance(dims, dict):
            for k, v in dims.items():
                if v is not None:
                    try:
                        g["dimensions"].setdefault(k, []).append(float(v))
                    except (TypeError, ValueError):
                        pass

        # Agreement: compare the human 👍/👎 (if any) to the judge's verdict.
        if lf is not None and hf_by_trace:
            fb = _human_feedback_for_task(lf, t["id"], hf_by_trace)
            if fb:
                human_positive = fb[0]["value"] == 1.0
                judge_positive = score >= JUDGE_GOOD_THRESHOLD
                if human_positive == judge_positive:
                    g["agree"] += 1
                else:
                    g["disagree"] += 1
                    disagreements.append({
                        "task_id": t["id"], "title": t.get("title", ""),
                        "task_type": gkey, "judge_score": score,
                        "judge_why": t.get("judge_why", ""),
                        "human_value": fb[0]["value"], "human_comment": fb[0]["comment"],
                    })

    def avg(xs):
        return round(sum(xs) / len(xs), 1) if xs else None

    rows = []
    for g in groups.values():
        scores = g["scores"]
        # Trend: mean of the newer half minus the older half (by scored_at).
        order = sorted(range(len(scores)), key=lambda i: g["scored_at"][i])
        ordered = [scores[i] for i in order]
        trend = None
        if len(ordered) >= 2:
            mid = len(ordered) // 2
            older, newer = ordered[:mid], ordered[mid:]
            if older and newer:
                trend = round((sum(newer) / len(newer)) - (sum(older) / len(older)), 1)
        reacted = g["agree"] + g["disagree"]
        rows.append({
            "task_type": g["task_type"],
            "count": g["count"],
            "avg_score": avg(scores),
            "trend": trend,
            # Chronological score history (oldest→newest) so the sparkline can
            # SHOW the trend. Capped to the last 8 points; the UI slices too.
            "history": [round(v, 1) for v in ordered[-8:]],
            "phase": g["phase"],
            "dimensions": {k: avg(v) for k, v in g["dimensions"].items()},
            "agreement_pct": round(100 * g["agree"] / reacted) if reacted else None,
            "reacted": reacted,
        })

    rows.sort(key=lambda r: r["count"], reverse=True)
    disagreements.sort(key=lambda d: d["judge_score"])
    _json_response(handler, {
        "groups": rows,
        "disagreements": disagreements,
        "total_judged": len(judged),
        "langfuse": lf is not None,
    })


def handle_get_task(handler, task_id):
    """GET /api/tasks/{id} — Return full task detail with parsed activity log."""
    try:
        task_data = task_lib.read_task(task_id)
    except FileNotFoundError:
        _error_response(handler, f"Task {task_id} not found", status=404)
        return
    except Exception as e:
        _error_response(handler, f"Failed to read task: {e}", status=500)
        return

    fm = task_data["frontmatter"]
    body = task_data["body"]

    # Build response: all frontmatter fields + body + parsed activity log
    result = {}
    for key, value in fm.items():
        result[key] = value
    result["body"] = body.strip()
    result["activity_log"] = _parse_activity_log(body)

    _enrich_sharepoint_url(result)
    _json_response(handler, result)


def handle_complete_task(handler, task_id):
    """POST /api/tasks/{id}/done — Mark task complete and archive."""
    try:
        archive_path = task_lib.complete_task(task_id, actor="human")
        _json_response(handler, {
            "status": "ok",
            "message": f"Task {task_id} completed and archived",
            "archive_path": archive_path,
        })
    except FileNotFoundError:
        _error_response(handler, f"Task {task_id} not found", status=404)
    except Exception as e:
        _error_response(handler, f"Failed to complete task: {e}", status=500)


def handle_complete_and_delete_task(handler, task_id):
    """POST /api/tasks/{id}/done-and-delete — Complete task and delete output files."""
    try:
        archive_path, deleted = task_lib.complete_and_delete_task(task_id, actor="human")
        _json_response(handler, {
            "status": "ok",
            "message": f"Task {task_id} completed; output files deleted",
            "archive_path": archive_path,
            "files_deleted": deleted,
        })
    except FileNotFoundError:
        _error_response(handler, f"Task {task_id} not found", status=404)
    except Exception as e:
        _error_response(handler, f"Failed to complete task: {e}", status=500)


def handle_update_description(handler, task_id):
    """POST /api/tasks/{id}/description — Update the description section."""
    try:
        body = _read_request_body(handler)
    except (json.JSONDecodeError, ValueError) as e:
        _error_response(handler, f"Invalid JSON body: {e}", status=400)
        return

    description = body.get("description", "").strip()
    if not description:
        _error_response(handler, "Missing or empty 'description' field", status=400)
        return

    try:
        filepath = task_lib.update_task_description(task_id, description, actor="human")
        _json_response(handler, {
            "status": "ok",
            "message": f"Description updated for {task_id}",
        })
    except FileNotFoundError:
        _error_response(handler, f"Task {task_id} not found", status=404)
    except Exception as e:
        _error_response(handler, f"Failed to update description: {e}", status=500)


def handle_update_message(handler, task_id):
    """POST /api/tasks/{id}/message — Save edits to a send-message draft.

    Body: {message_body, message_subject?}. Persists to frontmatter so the
    Message preview reflects the human's edits before sending.
    """
    try:
        body = _read_request_body(handler)
    except (json.JSONDecodeError, ValueError) as e:
        _error_response(handler, f"Invalid JSON body: {e}", status=400)
        return

    message_body = (body.get("message_body") or "").strip()
    if not message_body:
        _error_response(handler, "Missing or empty 'message_body' field", status=400)
        return

    changes = {"message_body": message_body}
    if body.get("message_subject") is not None:
        changes["message_subject"] = str(body.get("message_subject")).strip()

    try:
        task_lib.update_task(
            task_id,
            changes=changes,
            comment="Message draft edited.",
            actor="human",
        )
        _json_response(handler, {
            "status": "ok",
            "message": f"Message draft updated for {task_id}",
        })
    except FileNotFoundError:
        _error_response(handler, f"Task {task_id} not found", status=404)
    except Exception as e:
        _error_response(handler, f"Failed to update message: {e}", status=500)


def handle_send_message(handler, task_id):
    """POST /api/tasks/{id}/send-message — Mark a send-message task as sent.

    Records the send and archives the task. PM-OS has no Slack/Teams/Email
    transmission channel — this is the approve-and-send step of the collab
    pattern: the human sends from the drafted doc, then confirms here. It does
    NOT transmit anything externally.
    """
    try:
        task_lib.update_task(
            task_id,
            changes={"message_sent_at": task_lib._now_iso()},
            comment="Message marked as sent (recorded; PM-OS does not transmit — sent manually from the draft).",
            actor="human",
        )
        archive_path = task_lib.complete_task(task_id, actor="human")
        _json_response(handler, {
            "status": "ok",
            "message": f"Message recorded as sent; {task_id} archived",
            "archive_path": archive_path,
        })
    except FileNotFoundError:
        _error_response(handler, f"Task {task_id} not found", status=404)
    except Exception as e:
        _error_response(handler, f"Failed to send message: {e}", status=500)


def handle_add_comment(handler, task_id):
    """POST /api/tasks/{id}/comment — Append activity log entry."""
    try:
        body = _read_request_body(handler)
    except (json.JSONDecodeError, ValueError) as e:
        _error_response(handler, f"Invalid JSON body: {e}", status=400)
        return

    content = body.get("content", "").strip()
    if not content:
        _error_response(handler, "Missing or empty 'content' field", status=400)
        return

    try:
        filepath = task_lib.update_task(
            task_id,
            comment=content,
            actor="human",
        )
        _json_response(handler, {
            "status": "ok",
            "message": f"Comment added to {task_id}",
        })
    except FileNotFoundError:
        _error_response(handler, f"Task {task_id} not found", status=404)
    except Exception as e:
        _error_response(handler, f"Failed to add comment: {e}", status=500)


def handle_dispatch_task(handler, task_id):
    """POST /api/tasks/{id}/dispatch — Dispatch agent for a single task in background."""
    dispatch_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "task_dispatch.py")

    # Fire and forget — dispatch runs in background
    # Strip ALL Claude-related env vars to prevent nested-session detection
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("CLAUDE", "CMUX_CLAUDE"))}
    env["PATH"] = (
        os.path.join(os.path.expanduser("~"), ".local", "bin")
        + ":/opt/homebrew/bin"
        + ":" + env.get("PATH", "/usr/bin:/bin")
    )

    try:
        subprocess.Popen(
            [sys.executable, dispatch_script, "--task", task_id],
            cwd=PM_OS_DIR,
            env=env,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        _error_response(handler, f"Failed to start dispatcher: {e}", status=500)
        return

    _json_response(handler, {
        "status": "ok",
        "message": f"Agent dispatched for {task_id}",
    })


def handle_rerun_task(handler, task_id):
    """POST /api/tasks/{id}/rerun — Reset agent state and re-dispatch the task."""
    try:
        # Reset agent fields and status to open
        task_lib.update_task(task_id, changes={
            "status": "open",
            "agent_status": "",
            "agent_error": "",
            "agent_output": "",
            "agent_started": "",
            "agent_completed": "",
        }, comment="Task reset for agent rerun.", actor="human", )
    except FileNotFoundError:
        _error_response(handler, f"Task {task_id} not found", status=404)
        return
    except Exception as e:
        _error_response(handler, f"Failed to reset task: {e}", status=500)
        return

    # Dispatch the agent (same logic as handle_dispatch_task)
    dispatch_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "task_dispatch.py")
    # Strip ALL Claude-related env vars to prevent nested-session detection
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("CLAUDE", "CMUX_CLAUDE"))}
    env["PATH"] = (
        os.path.join(os.path.expanduser("~"), ".local", "bin")
        + ":/opt/homebrew/bin"
        + ":" + env.get("PATH", "/usr/bin:/bin")
    )

    try:
        subprocess.Popen(
            [sys.executable, dispatch_script, "--task", task_id, "--rerun"],
            cwd=PM_OS_DIR,
            env=env,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        _error_response(handler, f"Reset succeeded but dispatch failed: {e}", status=500)
        return

    _json_response(handler, {
        "status": "ok",
        "message": f"Task {task_id} reset and agent re-dispatched",
    })


def handle_schedule_meeting(handler, task_id):
    """POST /api/tasks/{id}/schedule-meeting — Create calendar event and complete task."""
    try:
        body = _read_request_body(handler)
    except (json.JSONDecodeError, ValueError) as e:
        _error_response(handler, f"Invalid JSON body: {e}", status=400)
        return

    slot_start = body.get("slot_start", "").strip()
    slot_end = body.get("slot_end", "").strip()
    if not slot_start or not slot_end:
        _error_response(handler, "Missing slot_start or slot_end", status=400)
        return

    # Load the task and validate it's a schedule-meeting task
    try:
        task_data = task_lib.read_task(task_id)
    except FileNotFoundError:
        _error_response(handler, f"Task {task_id} not found", status=404)
        return

    fm = task_data["frontmatter"]
    if fm.get("task_type") != "schedule-meeting":
        _error_response(handler, f"Task {task_id} is not a schedule-meeting task", status=400)
        return

    # Use values from POST body if provided (user may have edited in UI), else fall back to task frontmatter
    meeting_title = body.get("meeting_title") or fm.get("meeting_title") or fm.get("title", "Meeting")
    meeting_attendees_raw = body.get("attendees") or fm.get("meeting_attendees") or []
    meeting_description = body.get("meeting_description") or fm.get("meeting_description") or ""
    timezone = "America/New_York"

    # Resolve name-based attendees to email addresses
    email_cache = _load_email_cache()
    meeting_attendees = []
    for a in meeting_attendees_raw:
        resolved = email_cache.get(str(a), str(a))
        if resolved:  # skip None entries from cache
            meeting_attendees.append(resolved)

    # Recurrence: from POST body or task frontmatter
    recurring = body.get("recurring") or None
    if not recurring and fm.get("meeting_recurring"):
        recurring = fm.get("meeting_recurrence_pattern") or "weekly"

    # Build args for create_calendar_event.py
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "create_calendar_event.py")
    cmd = [
        sys.executable, script_path,
        "--subject", meeting_title,
        "--start", slot_start,
        "--end", slot_end,
        "--timezone", timezone,
    ]
    if meeting_attendees:
        cmd.extend(["--attendees", ",".join(str(a) for a in meeting_attendees)])
    if meeting_description:
        cmd.extend(["--body", meeting_description])
    if recurring:
        cmd.extend(["--recurring", recurring])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        _error_response(handler, "Calendar event creation timed out", status=500)
        return
    except Exception as e:
        _error_response(handler, f"Failed to run calendar script: {e}", status=500)
        return

    if result.returncode != 0:
        error_msg = result.stderr.strip() or f"Exit code {result.returncode}"
        _error_response(handler, f"Calendar event creation failed: {error_msg}", status=500)
        return

    # Parse response for event ID
    event_id = None
    try:
        event_data = json.loads(result.stdout)
        event_id = event_data.get("id")
    except (json.JSONDecodeError, AttributeError):
        pass

    # Update task with selected slot and event ID, then complete+archive
    now = task_lib._now_iso()
    changes = {
        "meeting_selected_slot": slot_start,
    }
    if event_id:
        changes["meeting_event_id"] = event_id

    task_lib.update_task(
        task_id,
        changes=changes,
        comment=f"Calendar event created for {slot_start}. Attendees: {', '.join(str(a) for a in meeting_attendees)}",
        actor="human",
    )

    # Complete and archive
    archive_path = task_lib.complete_task(task_id, actor="human")

    _json_response(handler, {
        "status": "ok",
        "message": f"Calendar event created and task {task_id} archived",
        "event_id": event_id,
        "archive_path": archive_path,
    })


def handle_publish_jira(handler, task_id):
    """POST /api/tasks/{id}/publish-jira — Publish a Jira draft via mini Claude session."""
    try:
        task_data = task_lib.read_task(task_id)
    except FileNotFoundError:
        _error_response(handler, f"Task {task_id} not found", status=404)
        return

    body = task_data.get("body", "")
    draft = jira_publish.parse_jira_draft(body)
    if draft is None:
        _error_response(handler, "No JIRA_DRAFT block found in task body", status=400)
        return

    try:
        issue_key, issue_url = jira_publish.publish_to_jira(draft)
    except RuntimeError as e:
        # Log the error to the task activity log
        try:
            task_lib.update_task(task_id, changes={}, comment=f"Jira publish failed: {e}", actor="system")
        except Exception:
            pass
        jira_publish._trace_publish(task_id, draft, error=str(e))
        _error_response(handler, f"Jira publish failed: {e}", status=500)
        return

    # Success — update task with Jira link and complete it
    output_str = f"Created {issue_key}: {issue_url}"
    try:
        task_lib.update_task(task_id, changes={
            "agent_output": output_str,
        }, comment=f"Published to Jira: {output_str}", actor="system")
        archive_path, _ = task_lib.complete_task(task_id, actor="system")
    except Exception as e:
        # Ticket was created but archiving failed — still return success
        pass

    jira_publish._trace_publish(task_id, draft, issue_key=issue_key, issue_url=issue_url)

    _json_response(handler, {
        "status": "ok",
        "message": f"Published to Jira: {issue_key}",
        "issue_key": issue_key,
        "issue_url": issue_url,
    })


def _load_email_cache():
    """Load the people email cache (name → email mapping)."""
    email_cache_path = os.path.join(PM_OS_DIR, "datasets", "people", "email_cache.json")
    try:
        with open(email_cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def handle_update_meeting_details(handler, task_id):
    """POST /api/tasks/{id}/meeting-details — Update meeting title and description."""
    try:
        body = _read_request_body(handler)
    except (json.JSONDecodeError, ValueError) as e:
        _error_response(handler, f"Invalid JSON body: {e}", status=400)
        return

    changes = {}
    if "meeting_title" in body:
        changes["meeting_title"] = body["meeting_title"].strip()
    if "meeting_description" in body:
        changes["meeting_description"] = body["meeting_description"].strip()

    if not changes:
        _error_response(handler, "No meeting fields to update", status=400)
        return

    try:
        task_lib.update_task(
            task_id,
            changes=changes,
            comment=f"Meeting details updated: {', '.join(changes.keys())}",
            actor="human",
        )
        _json_response(handler, {
            "status": "ok",
            "message": f"Meeting details updated for {task_id}",
        })
    except FileNotFoundError:
        _error_response(handler, f"Task {task_id} not found", status=404)
    except Exception as e:
        _error_response(handler, f"Failed to update meeting details: {e}", status=500)


def handle_open_file(handler, query_params):
    """GET /open — Open a file in Ghostty + NeoVim."""
    file_param = query_params.get("file", [None])[0]
    if not file_param:
        _error_response(handler, "Missing 'file' query parameter", status=400)
        return

    # Resolve relative paths against PM_OS_DIR (agent_output paths are relative)
    if os.path.isabs(file_param):
        filepath = file_param
    else:
        filepath = os.path.join(PM_OS_DIR, file_param)

    filepath = os.path.normpath(filepath)

    if not os.path.isfile(filepath):
        _error_response(handler, f"File not found: {file_param}", status=404)
        return

    # Open .docx files in the default app (Word) instead of NeoVim
    if filepath.endswith(".docx"):
        cmd = ["open", filepath] if sys.platform == "darwin" else ["xdg-open", filepath]
    elif sys.platform == "darwin":
        cmd = [
            "open", "-na", "Ghostty.app", "--args",
            f"--command=nvim {shlex.quote(filepath)}",
        ]
    else:
        cmd = [
            "ghostty",
            f"--command=nvim {shlex.quote(filepath)}",
        ]

    subprocess.Popen(cmd, start_new_session=True)

    handler.send_response(204)
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()


def handle_people_emails(handler):
    """GET /api/people/emails — Return the email cache for attendee typeahead."""
    email_cache_path = os.path.join(PM_OS_DIR, "datasets", "people", "email_cache.json")
    try:
        with open(email_cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        _json_response(handler, data)
    except FileNotFoundError:
        _json_response(handler, {})
    except Exception as e:
        _error_response(handler, f"Failed to load email cache: {e}", status=500)


# ─── LangFuse API Handlers ───────────────────────────────────────────────────

def _get_langfuse():
    """Get LangFuse client, returning None if unavailable."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from langfuse_client import get_langfuse
        return get_langfuse()
    except Exception:
        return None


def handle_langfuse_health(handler):
    """GET /api/langfuse/health — Check LangFuse connectivity."""
    lf = _get_langfuse()
    if lf is None:
        _json_response(handler, {
            "status": "unavailable",
            "message": "LangFuse not configured (LANGFUSE_SECRET_KEY not set or package not installed)",
            "host": os.environ.get("LANGFUSE_HOST", "http://localhost:3000"),
        })
        return
    try:
        # Quick health check — try to fetch prompts list
        lf.api.prompts.list()
        _json_response(handler, {
            "status": "ok",
            "host": os.environ.get("LANGFUSE_HOST", "http://localhost:3000"),
        })
    except Exception as e:
        _json_response(handler, {
            "status": "error",
            "message": str(e),
            "host": os.environ.get("LANGFUSE_HOST", "http://localhost:3000"),
        }, status=503)


def handle_langfuse_prompts(handler):
    """GET /api/langfuse/prompts — List all prompts with version info (paginated fetch)."""
    lf = _get_langfuse()
    if lf is None:
        _json_response(handler, {"prompts": [], "error": "LangFuse not available"})
        return
    try:
        all_data = []
        page = 1
        while True:
            result = lf.api.prompts.list(page=page, limit=100)
            data = result.data if hasattr(result, 'data') else []
            all_data.extend(data)
            if len(data) < 100:
                break
            page += 1

        prompts = []
        for p in all_data:
            prompts.append({
                "name": p.name if hasattr(p, 'name') else str(p),
                "version": getattr(p, 'version', None) or getattr(p, 'last_version', None) or 1,
                "labels": getattr(p, 'labels', []),
                "type": getattr(p, 'type', 'text'),
                "updated_at": str(getattr(p, 'updated_at', '')),
                "tags": getattr(p, 'tags', []),
            })
        _json_response(handler, {"prompts": prompts})
    except Exception as e:
        _json_response(handler, {"prompts": [], "error": str(e)}, status=500)


def handle_langfuse_trace_stats(handler):
    """GET /api/langfuse/traces/stats — Aggregate trace statistics."""
    lf = _get_langfuse()
    if lf is None:
        _json_response(handler, {"stats": {}, "error": "LangFuse not available"})
        return
    try:
        # Fetch recent traces
        result = lf.api.trace.list(limit=100, order_by="timestamp.desc")
        traces = result.data if hasattr(result, 'data') else []

        # Aggregate by trace name
        stats = {}
        for t in traces:
            name = getattr(t, 'name', 'unknown')
            if name not in stats:
                stats[name] = {"count": 0, "success": 0, "errors": 0}
            stats[name]["count"] += 1
            level = getattr(t, 'level', 'DEFAULT')
            if level == "ERROR":
                stats[name]["errors"] += 1
            else:
                stats[name]["success"] += 1

        # Add success rates
        for name, s in stats.items():
            s["success_rate"] = round(s["success"] / s["count"] * 100, 1) if s["count"] > 0 else 0

        _json_response(handler, {"stats": stats, "total_traces": len(traces)})
    except Exception as e:
        _json_response(handler, {"stats": {}, "error": str(e)}, status=500)


def handle_task_traces(handler, task_id):
    """GET /api/tasks/{id}/traces — List all pipeline traces for a task."""
    lf = _get_langfuse()
    if lf is None:
        _json_response(handler, {"traces": [], "error": "LangFuse not available"})
        return
    try:
        # Query traces by session_id (which we set to task_id)
        result = lf.api.trace.list(session_id=task_id, order_by="timestamp.asc")
        traces = []
        for t in (result.data if hasattr(result, 'data') else []):
            # Summarize input/output for display
            input_data = getattr(t, 'input', None)
            output_data = getattr(t, 'output', None)
            input_summary = ""
            output_summary = ""
            if isinstance(input_data, dict):
                input_summary = json.dumps(input_data, default=str)[:200]
            elif isinstance(input_data, str):
                input_summary = input_data[:200]
            if isinstance(output_data, dict):
                output_summary = json.dumps(output_data, default=str)[:200]
            elif isinstance(output_data, str):
                output_summary = output_data[:200]

            traces.append({
                "trace_id": getattr(t, 'id', ''),
                "name": getattr(t, 'name', 'unknown'),
                "timestamp": str(getattr(t, 'timestamp', '')),
                "input_summary": input_summary,
                "output_summary": output_summary,
                "level": getattr(t, 'level', 'DEFAULT'),
                "metadata": getattr(t, 'metadata', {}),
                "scores": [],  # populated below
            })

        # Fetch scores via REST (the SDK score read path is broken on this
        # LangFuse version — see langfuse_client.list_scores). One pull,
        # filtered to this task's traces, then mapped back per trace.
        try:
            from langfuse_client import list_scores
            trace_ids = [t["trace_id"] for t in traces if t["trace_id"]]
            score_map = {}
            for s in list_scores(trace_ids=trace_ids):
                score_map.setdefault(s.get("traceId"), []).append({
                    "name": s.get("name", ""),
                    "value": s.get("value"),
                    "comment": s.get("comment", "") or "",
                    "data_type": s.get("dataType", "NUMERIC"),
                })
            for trace in traces:
                trace["scores"] = score_map.get(trace["trace_id"], [])
        except Exception:
            pass

        _json_response(handler, {"traces": traces, "task_id": task_id})
    except Exception as e:
        _json_response(handler, {"traces": [], "error": str(e)}, status=500)


def handle_score_trace(handler, task_id, trace_id):
    """POST /api/tasks/{id}/traces/{trace_id}/score — Score a pipeline step."""
    try:
        from langfuse_client import score_trace, _is_enabled
        if not _is_enabled():
            _error_response(handler, "LangFuse not available", status=503)
            return

        body = _read_request_body(handler)
        score_value = body.get("score")
        comment = body.get("comment", "")

        if score_value is None:
            _error_response(handler, "Missing 'score' field (0 or 1)")
            return

        result = score_trace(trace_id, "human-feedback", float(score_value), comment=comment, data_type="NUMERIC")
        _json_response(handler, {"ok": result is not None, "trace_id": trace_id, "score": score_value})
    except Exception as e:
        _error_response(handler, f"Scoring failed: {e}", status=500)


def handle_annotate_trace(handler, task_id, trace_id):
    """POST /api/tasks/{id}/traces/{trace_id}/annotation — Annotate a pipeline step."""
    try:
        from langfuse_client import score_trace, _is_enabled
        if not _is_enabled():
            _error_response(handler, "LangFuse not available", status=503)
            return

        body = _read_request_body(handler)
        comment = body.get("comment", "")
        category = body.get("category", "feedback")

        if not comment:
            _error_response(handler, "Missing 'comment' field")
            return

        result = score_trace(trace_id, "human-annotation", category, comment=comment, data_type="CATEGORICAL")
        _json_response(handler, {"ok": result is not None, "trace_id": trace_id})
    except Exception as e:
        _error_response(handler, f"Annotation failed: {e}", status=500)


# ─── Cron Job API Handlers ───────────────────────────────────────────────────

def handle_list_cron_jobs(handler):
    """GET /api/cron — List all cron jobs."""
    jobs = cron_lib.list_jobs()
    _json_response(handler, {"jobs": jobs})


def handle_get_cron_job(handler, job_id):
    """GET /api/cron/{id} — Get a single cron job."""
    job = cron_lib.get_job(job_id)
    if job is None:
        _error_response(handler, f"Cron job not found: {job_id}", status=404)
        return
    _json_response(handler, job)


def handle_parse_cron(handler):
    """POST /api/cron/parse — NLP parse free text into structured cron job fields."""
    body = _read_request_body(handler)
    text = body.get("text", "").strip()
    if not text:
        _error_response(handler, "Missing 'text' field", status=400)
        return
    try:
        from parse_cron_input import parse_cron
        parsed = parse_cron(text)
        _json_response(handler, {"status": "ok", "parsed": parsed})
    except Exception as e:
        _error_response(handler, f"Parse failed: {e}", status=500)


def handle_confirm_cron_job(handler):
    """POST /api/cron/confirm — Save a reviewed/edited cron job."""
    body = _read_request_body(handler)
    job_data = body.get("job", body)

    name = job_data.get("name")
    cron_expr = job_data.get("cron_expr")
    cron_human = job_data.get("cron_human", "")
    task_template = job_data.get("task_template", {})
    expires = job_data.get("expires")
    auto_dispatch = job_data.get("auto_dispatch", True)
    raw_input = job_data.get("raw_input", "")

    if not name:
        _error_response(handler, "Missing job name", status=400)
        return
    if not cron_expr:
        _error_response(handler, "Missing cron expression", status=400)
        return

    try:
        job = cron_lib.create_job(
            name=name,
            cron_expr=cron_expr,
            cron_human=cron_human,
            task_template=task_template,
            expires=expires,
            auto_dispatch=auto_dispatch,
            raw_input=raw_input,
        )
        _json_response(handler, {"status": "ok", "job": job})
    except ValueError as e:
        _error_response(handler, str(e), status=400)
    except Exception as e:
        _error_response(handler, f"Failed to create job: {e}", status=500)


def handle_cron_preview(handler):
    """POST /api/cron/preview — Return next N run times for a cron expression."""
    body = _read_request_body(handler)
    cron_expr = body.get("cron_expr", "").strip()
    count = body.get("count", 5)
    if not cron_expr:
        _error_response(handler, "Missing 'cron_expr' field", status=400)
        return
    valid, err = cron_lib.validate_cron_expr(cron_expr)
    if not valid:
        _error_response(handler, f"Invalid cron expression: {err}", status=400)
        return
    runs = cron_lib.compute_next_runs(cron_expr, count=count)
    _json_response(handler, {"runs": runs, "cron_expr": cron_expr})


def handle_update_cron_job(handler, job_id):
    """POST /api/cron/{id} — Update cron job fields."""
    body = _read_request_body(handler)
    changes = body.get("changes", body)
    # Don't allow changing the ID
    changes.pop("id", None)

    job = cron_lib.update_job(job_id, changes)
    if job is None:
        _error_response(handler, f"Cron job not found: {job_id}", status=404)
        return
    _json_response(handler, {"status": "ok", "job": job})


def handle_toggle_cron_job(handler, job_id):
    """POST /api/cron/{id}/toggle — Enable/disable a cron job."""
    job = cron_lib.toggle_job(job_id)
    if job is None:
        _error_response(handler, f"Cron job not found: {job_id}", status=404)
        return
    _json_response(handler, {"status": "ok", "job": job})


def handle_run_cron_job(handler, job_id):
    """POST /api/cron/{id}/run — Execute a cron job immediately."""
    job = cron_lib.get_job(job_id)
    if job is None:
        _error_response(handler, f"Cron job not found: {job_id}", status=404)
        return
    try:
        task_id, _ = cron_lib.execute_job(job)
        _json_response(handler, {"status": "ok", "task_id": task_id, "job_id": job_id})
    except Exception as e:
        _error_response(handler, f"Execution failed: {e}", status=500)


def handle_delete_cron_job(handler, job_id):
    """POST /api/cron/{id}/delete — Delete a cron job."""
    if cron_lib.delete_job(job_id):
        _json_response(handler, {"status": "ok", "message": f"Deleted {job_id}"})
    else:
        _error_response(handler, f"Cron job not found: {job_id}", status=404)


# ─── Worker API Handlers ─────────────────────────────────────────────────────

def handle_list_workers(handler):
    """GET /api/workers — List all worker definitions with tools, skills, and prompt body."""
    try:
        from task_dispatch import load_workers
        workers = load_workers()
        # Return all fields except internal matching state
        result = []
        for w in workers:
            result.append({
                "name": w.get("name", ""),
                "description": w.get("description", ""),
                "priority": w.get("priority", 0),
                "match": w.get("match", {}),
                "allowed_tools": w.get("allowed_tools", []),
                "skills": w.get("skills", []),
                "langfuse_prompt": w.get("langfuse_prompt", ""),
                "timeout": w.get("timeout", 600),
                "max_turns": w.get("max_turns", 30),
                "prompt_body": w.get("prompt_body", ""),
            })
        _json_response(handler, {"workers": result})
    except Exception as e:
        _error_response(handler, f"Failed to load workers: {e}", status=500)


# ─── Request Handler ──────────────────────────────────────────────────────────

class TaskServerHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    """HTTP request handler for the task server.

    Routes:
      /              → ui/task-board/index.html
      /api/...       → API handlers
      everything else → static files from ui/task-board/
    """

    def __init__(self, *args, **kwargs):
        # Set the static file serving directory
        super().__init__(*args, directory=UI_DIR, **kwargs)

    # Suppress default access logging to keep output clean
    def log_message(self, format, *args):
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), format % args))

    def _route_request(self, method):
        """Central router for all requests."""
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query_params = parse_qs(parsed.query)

        # ─── LangFuse API routes ────────────────────────────────────────
        if path == "/api/langfuse/health" and method == "GET":
            handle_langfuse_health(self)
            return True

        if path == "/api/langfuse/prompts" and method == "GET":
            handle_langfuse_prompts(self)
            return True

        if path == "/api/langfuse/traces/stats" and method == "GET":
            handle_langfuse_trace_stats(self)
            return True

        # ─── Cron API routes ───────────────────────────────────────────

        # Specific cron action routes (must come before generic /api/cron/{id})
        match = re.match(r"^/api/cron/([^/]+)/toggle$", path)
        if match and method == "POST":
            handle_toggle_cron_job(self, match.group(1))
            return True

        match = re.match(r"^/api/cron/([^/]+)/run$", path)
        if match and method == "POST":
            handle_run_cron_job(self, match.group(1))
            return True

        match = re.match(r"^/api/cron/([^/]+)/delete$", path)
        if match and method == "POST":
            handle_delete_cron_job(self, match.group(1))
            return True

        if path == "/api/cron/parse" and method == "POST":
            handle_parse_cron(self)
            return True

        if path == "/api/cron/confirm" and method == "POST":
            handle_confirm_cron_job(self)
            return True

        if path == "/api/cron/preview" and method == "POST":
            handle_cron_preview(self)
            return True

        # Generic cron routes
        match = re.match(r"^/api/cron/([^/]+)$", path)
        if match:
            job_id = match.group(1)
            if method == "GET":
                handle_get_cron_job(self, job_id)
                return True
            elif method == "POST":
                handle_update_cron_job(self, job_id)
                return True

        if path == "/api/cron" and method == "GET":
            handle_list_cron_jobs(self)
            return True

        # ─── Worker API routes ─────────────────────────────────────────

        if path == "/api/workers" and method == "GET":
            handle_list_workers(self)
            return True

        # ─── Task trace routes ─────────────────────────────────────────

        # Match /api/tasks/{id}/traces/{trace_id}/score
        match = re.match(r"^/api/tasks/([^/]+)/traces/([^/]+)/score$", path)
        if match and method == "POST":
            task_id = _parse_task_id(match.group(1))
            trace_id = match.group(2)
            if task_id is None:
                _error_response(self, "Invalid task ID format", status=400)
            else:
                handle_score_trace(self, task_id, trace_id)
            return True

        # Match /api/tasks/{id}/traces/{trace_id}/annotation
        match = re.match(r"^/api/tasks/([^/]+)/traces/([^/]+)/annotation$", path)
        if match and method == "POST":
            task_id = _parse_task_id(match.group(1))
            trace_id = match.group(2)
            if task_id is None:
                _error_response(self, "Invalid task ID format", status=400)
            else:
                handle_annotate_trace(self, task_id, trace_id)
            return True

        # Match /api/tasks/{id}/traces
        match = re.match(r"^/api/tasks/([^/]+)/traces$", path)
        if match and method == "GET":
            task_id = _parse_task_id(match.group(1))
            if task_id is None:
                _error_response(self, "Invalid task ID format", status=400)
            else:
                handle_task_traces(self, task_id)
            return True

        # ─── Task API routes ───────────────────────────────────────────
        if path == "/api/tasks" and method == "GET":
            handle_list_tasks(self, query_params)
            return True

        # Archived/completed tasks (Activity surface)
        if path == "/api/activity" and method == "GET":
            handle_list_activity(self, query_params)
            return True

        # Shadow-judge scoreboard (Quality surface)
        if path == "/api/quality" and method == "GET":
            handle_quality(self)
            return True

        # Match /api/tasks/{id}/dispatch
        match = re.match(r"^/api/tasks/([^/]+)/dispatch$", path)
        if match and method == "POST":
            task_id = _parse_task_id(match.group(1))
            if task_id is None:
                _error_response(self, "Invalid task ID format", status=400)
            else:
                handle_dispatch_task(self, task_id)
            return True

        # Match /api/tasks/{id}/rerun
        match = re.match(r"^/api/tasks/([^/]+)/rerun$", path)
        if match and method == "POST":
            task_id = _parse_task_id(match.group(1))
            if task_id is None:
                _error_response(self, "Invalid task ID format", status=400)
            else:
                handle_rerun_task(self, task_id)
            return True

        # Match /api/tasks/{id}/schedule-meeting
        match = re.match(r"^/api/tasks/([^/]+)/schedule-meeting$", path)
        if match and method == "POST":
            task_id = _parse_task_id(match.group(1))
            if task_id is None:
                _error_response(self, "Invalid task ID format", status=400)
            else:
                handle_schedule_meeting(self, task_id)
            return True

        # Match /api/tasks/{id}/publish-jira
        match = re.match(r"^/api/tasks/([^/]+)/publish-jira$", path)
        if match and method == "POST":
            task_id = _parse_task_id(match.group(1))
            if task_id is None:
                _error_response(self, "Invalid task ID format", status=400)
            else:
                handle_publish_jira(self, task_id)
            return True

        # Match /api/tasks/{id}/meeting-details
        match = re.match(r"^/api/tasks/([^/]+)/meeting-details$", path)
        if match and method == "POST":
            task_id = _parse_task_id(match.group(1))
            if task_id is None:
                _error_response(self, "Invalid task ID format", status=400)
            else:
                handle_update_meeting_details(self, task_id)
            return True

        # Match /api/tasks/{id}/done-and-delete
        match = re.match(r"^/api/tasks/([^/]+)/done-and-delete$", path)
        if match and method == "POST":
            task_id = _parse_task_id(match.group(1))
            if task_id is None:
                _error_response(self, "Invalid task ID format", status=400)
            else:
                handle_complete_and_delete_task(self, task_id)
            return True

        # Match /api/tasks/{id}/done
        match = re.match(r"^/api/tasks/([^/]+)/done$", path)
        if match and method == "POST":
            task_id = _parse_task_id(match.group(1))
            if task_id is None:
                _error_response(self, "Invalid task ID format", status=400)
            else:
                handle_complete_task(self, task_id)
            return True

        # Match /api/tasks/{id}/description
        match = re.match(r"^/api/tasks/([^/]+)/description$", path)
        if match and method == "POST":
            task_id = _parse_task_id(match.group(1))
            if task_id is None:
                _error_response(self, "Invalid task ID format", status=400)
            else:
                handle_update_description(self, task_id)
            return True

        # Match /api/tasks/{id}/send-message  (must precede /message)
        match = re.match(r"^/api/tasks/([^/]+)/send-message$", path)
        if match and method == "POST":
            task_id = _parse_task_id(match.group(1))
            if task_id is None:
                _error_response(self, "Invalid task ID format", status=400)
            else:
                handle_send_message(self, task_id)
            return True

        # Match /api/tasks/{id}/message
        match = re.match(r"^/api/tasks/([^/]+)/message$", path)
        if match and method == "POST":
            task_id = _parse_task_id(match.group(1))
            if task_id is None:
                _error_response(self, "Invalid task ID format", status=400)
            else:
                handle_update_message(self, task_id)
            return True

        # Match /api/tasks/{id}/comment
        match = re.match(r"^/api/tasks/([^/]+)/comment$", path)
        if match and method == "POST":
            task_id = _parse_task_id(match.group(1))
            if task_id is None:
                _error_response(self, "Invalid task ID format", status=400)
            else:
                handle_add_comment(self, task_id)
            return True

        # Match /api/tasks/{id}
        match = re.match(r"^/api/tasks/([^/]+)$", path)
        if match and method == "GET":
            task_id = _parse_task_id(match.group(1))
            if task_id is None:
                _error_response(self, "Invalid task ID format", status=400)
            else:
                handle_get_task(self, task_id)
            return True

        # People email cache
        if path == "/api/people/emails" and method == "GET":
            handle_people_emails(self)
            return True

        # Open file in Ghostty + NeoVim
        if path == "/open" and method == "GET":
            handle_open_file(self, query_params)
            return True

        # Catch-all for unrecognized /api/ routes
        if path.startswith("/api/"):
            _error_response(self, f"Unknown API endpoint: {method} {path}", status=404)
            return True

        return False  # Not an API route

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """Handle GET requests: API routes first, then static files."""
        if self._route_request("GET"):
            return

        # Static file serving: route / to index.html
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.path = "/index.html"

        # Add CORS header to static file responses
        super().do_GET()

    def do_POST(self):
        """Handle POST requests (API only)."""
        if self._route_request("POST"):
            return
        _error_response(self, "POST not allowed for this path", status=405)

    def end_headers(self):
        """Inject CORS header into all responses (including static files)."""
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()


# ─── Server Startup ───────────────────────────────────────────────────────────

def main():
    # Ensure the UI directory exists (server still works for API-only use)
    if not os.path.isdir(UI_DIR):
        print(f"Warning: UI directory not found at {UI_DIR}")
        print("  API endpoints will work, but static file serving will fail.")
        print(f"  Create {UI_DIR}/index.html to serve the task board UI.")
        print()

    # Start cron scheduler background thread
    scheduler = CronScheduler()
    scheduler.start()

    server = ReusableHTTPServer(("127.0.0.1", PORT), TaskServerHandler)
    print(f"PM-OS Task Server running at http://127.0.0.1:{PORT}")
    print(f"  API:    http://127.0.0.1:{PORT}/api/tasks")
    print(f"  Cron:   http://127.0.0.1:{PORT}/api/cron")
    print(f"  UI dir: {UI_DIR}")
    print("  Press Ctrl+C to stop.")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        scheduler.stop()
        server.server_close()


if __name__ == "__main__":
    main()
