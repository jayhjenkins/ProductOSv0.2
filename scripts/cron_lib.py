#!/usr/bin/env python3
"""
cron_lib.py — Core library for PM-OS cron job management.

Handles CRUD for recurring jobs stored in datasets/cron/jobs.json.
When a job fires, it creates a task via task_lib.create_task() and
optionally auto-dispatches it.
"""

import fcntl
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta

from croniter import croniter

# ─── Constants ───────────────────────────────────────────────────────────────

PM_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRON_DIR = os.path.join(PM_OS_DIR, "datasets", "cron")
JOBS_FILE = os.path.join(CRON_DIR, "jobs.json")
COUNTER_FILE = os.path.join(CRON_DIR, "_counter")
MAX_HISTORY = 50

VALID_QUEUES = ["human", "agent", "collab", "waiting"]
VALID_PRIORITIES = ["critical", "high", "medium", "low"]
VALID_DOMAINS = ["product", "strategy", "marketing", "recruiting", "metrics", "learning", "ops"]


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _now_utc():
    return datetime.now(timezone.utc)


def _next_cron_id():
    """Atomically read, increment, and return next cron job ID."""
    fd = open(COUNTER_FILE, "r+")
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        current = int(fd.read().strip())
        cron_id = f"CRON-{current:04d}"
        fd.seek(0)
        fd.write(str(current + 1))
        fd.truncate()
        return cron_id
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        fd.close()


# ─── File I/O ────────────────────────────────────────────────────────────────

def _load_jobs():
    """Read all jobs from JSON file. Returns list of dicts."""
    if not os.path.exists(JOBS_FILE):
        return []
    fd = open(JOBS_FILE, "r")
    try:
        fcntl.flock(fd, fcntl.LOCK_SH)
        data = json.load(fd)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, ValueError):
        return []
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        fd.close()


def _save_jobs(jobs):
    """Atomically write all jobs to JSON file."""
    os.makedirs(CRON_DIR, exist_ok=True)
    fd = open(JOBS_FILE, "w")
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        json.dump(jobs, fd, indent=2, default=str)
        fd.write("\n")
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        fd.close()


# ─── Template Variables ──────────────────────────────────────────────────────

def resolve_template_vars(text, now=None):
    """Replace {date}, {week}, {month}, {year} with current values."""
    if not text:
        return text
    if now is None:
        now = _now_utc()

    date_str = now.strftime("%Y-%m-%d")
    year_str = now.strftime("%Y")
    month_str = now.strftime("%B %Y")

    # Week range: Monday–Sunday containing `now`
    monday = now - timedelta(days=now.weekday())
    sunday = monday + timedelta(days=6)
    week_str = f"{monday.strftime('%b %d')} – {sunday.strftime('%b %d')}"

    return (text
            .replace("{date}", date_str)
            .replace("{week}", week_str)
            .replace("{month}", month_str)
            .replace("{year}", year_str))


# ─── Cron Expression Helpers ────────────────────────────────────────────────

def compute_next_run(cron_expr, after=None):
    """Compute the next run time for a cron expression. Returns ISO string."""
    if after is None:
        after = _now_utc()
    elif isinstance(after, str):
        after = datetime.fromisoformat(after.replace("Z", "+00:00"))
    cron = croniter(cron_expr, after)
    next_dt = cron.get_next(datetime)
    if next_dt.tzinfo is None:
        next_dt = next_dt.replace(tzinfo=timezone.utc)
    return next_dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def compute_next_runs(cron_expr, count=5, after=None):
    """Compute the next N run times. Returns list of ISO strings."""
    if after is None:
        after = _now_utc()
    elif isinstance(after, str):
        after = datetime.fromisoformat(after.replace("Z", "+00:00"))
    cron = croniter(cron_expr, after)
    runs = []
    for _ in range(count):
        next_dt = cron.get_next(datetime)
        if next_dt.tzinfo is None:
            next_dt = next_dt.replace(tzinfo=timezone.utc)
        runs.append(next_dt.strftime("%Y-%m-%dT%H:%M:%SZ"))
    return runs


def validate_cron_expr(cron_expr):
    """Validate a cron expression. Returns (is_valid, error_message)."""
    try:
        croniter(cron_expr)
        return True, None
    except (ValueError, KeyError) as e:
        return False, str(e)


# ─── CRUD Operations ────────────────────────────────────────────────────────

def list_jobs():
    """Return all cron jobs."""
    return _load_jobs()


def get_job(job_id):
    """Return a single job by ID, or None."""
    for job in _load_jobs():
        if job["id"] == job_id:
            return job
    return None


def create_job(name, cron_expr, cron_human, task_template,
               expires=None, auto_dispatch=True, raw_input=""):
    """Create a new cron job. Returns the created job dict."""
    valid, err = validate_cron_expr(cron_expr)
    if not valid:
        raise ValueError(f"Invalid cron expression: {err}")

    # Validate task_template fields
    tpl = task_template or {}
    if tpl.get("queue") and tpl["queue"] not in VALID_QUEUES:
        raise ValueError(f"Invalid queue: {tpl['queue']}")
    if tpl.get("priority") and tpl["priority"] not in VALID_PRIORITIES:
        raise ValueError(f"Invalid priority: {tpl['priority']}")
    if tpl.get("domain") and tpl["domain"] not in VALID_DOMAINS:
        raise ValueError(f"Invalid domain: {tpl['domain']}")

    job_id = _next_cron_id()
    now = _now_iso()

    # Ensure the cron tag is in the template tags
    tags = tpl.get("tags", [])
    if "cron" not in tags:
        tags = ["cron"] + tags
    if job_id not in tags:
        tags.append(job_id)

    job = {
        "id": job_id,
        "name": name,
        "cron_expr": cron_expr,
        "cron_human": cron_human,
        "enabled": True,
        "created": now,
        "updated": now,
        "expires": expires,
        "last_run": None,
        "next_run": compute_next_run(cron_expr),
        "run_count": 0,
        "auto_dispatch": auto_dispatch,
        "task_template": {
            "title": tpl.get("title", name),
            "queue": tpl.get("queue", "agent"),
            "priority": tpl.get("priority", "medium"),
            "domain": tpl.get("domain"),
            "description": tpl.get("description", ""),
            "tags": tags,
        },
        "raw_input": raw_input,
        "task_history": [],
    }

    jobs = _load_jobs()
    jobs.append(job)
    _save_jobs(jobs)
    return job


def update_job(job_id, changes):
    """Update a job's fields. Returns updated job or None if not found."""
    jobs = _load_jobs()
    for i, job in enumerate(jobs):
        if job["id"] == job_id:
            for key, val in changes.items():
                if key == "task_template" and isinstance(val, dict):
                    job.setdefault("task_template", {}).update(val)
                else:
                    job[key] = val
            job["updated"] = _now_iso()
            # Recompute next_run if cron_expr changed
            if "cron_expr" in changes and job.get("enabled"):
                job["next_run"] = compute_next_run(job["cron_expr"])
            jobs[i] = job
            _save_jobs(jobs)
            return job
    return None


def delete_job(job_id):
    """Delete a job. Returns True if found and deleted."""
    jobs = _load_jobs()
    original_len = len(jobs)
    jobs = [j for j in jobs if j["id"] != job_id]
    if len(jobs) < original_len:
        _save_jobs(jobs)
        return True
    return False


def toggle_job(job_id):
    """Toggle a job's enabled state. Returns updated job or None."""
    jobs = _load_jobs()
    for i, job in enumerate(jobs):
        if job["id"] == job_id:
            job["enabled"] = not job["enabled"]
            job["updated"] = _now_iso()
            if job["enabled"]:
                job["next_run"] = compute_next_run(job["cron_expr"])
            else:
                job["next_run"] = None
            jobs[i] = job
            _save_jobs(jobs)
            return job
    return None


# ─── Job Execution ──────────────────────────────────────────────────────────

def execute_job(job):
    """Execute a cron job: create a task from the template, optionally dispatch.

    Returns (task_id, task_path) or raises on failure.
    """
    # Import task_lib here to avoid circular imports at module load
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import task_lib

    tpl = job.get("task_template", {})
    now = _now_utc()

    # Resolve template variables in title and description
    title = resolve_template_vars(tpl.get("title", job["name"]), now)
    description = resolve_template_vars(tpl.get("description", ""), now)

    # Add source line to description
    source_line = f"\n\nSource: {job['id']} ({job['name']})"
    if source_line not in description:
        description += source_line

    task_id, task_path = task_lib.create_task(
        title=title,
        queue=tpl.get("queue", "agent"),
        priority=tpl.get("priority", "medium"),
        domain=tpl.get("domain"),
        tags=tpl.get("tags", ["cron"]),
        creator="cron",
        description=description,
    )

    # Update job state
    jobs = _load_jobs()
    for i, j in enumerate(jobs):
        if j["id"] == job["id"]:
            j["last_run"] = _now_iso()
            j["next_run"] = compute_next_run(j["cron_expr"])
            j["run_count"] = j.get("run_count", 0) + 1
            history = j.get("task_history", [])
            history.append(task_id)
            if len(history) > MAX_HISTORY:
                history = history[-MAX_HISTORY:]
            j["task_history"] = history
            j["updated"] = _now_iso()
            jobs[i] = j
            break
    _save_jobs(jobs)

    # Auto-dispatch if enabled
    if job.get("auto_dispatch", True):
        _auto_dispatch(task_id)

    return task_id, task_path


def _auto_dispatch(task_id):
    """Fire task_dispatch.py --task {task_id} in background."""
    dispatch_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "task_dispatch.py")

    # Strip Claude env vars to prevent nested-session detection
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
        sys.stderr.write(f"[cron] Failed to auto-dispatch {task_id}: {e}\n")
