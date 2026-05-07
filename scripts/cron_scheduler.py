#!/usr/bin/env python3
"""
cron_scheduler.py — Background scheduler for PM-OS cron jobs.

Runs as a daemon thread inside task_server.py. Checks every 30 seconds
which jobs are due, creates tasks via cron_lib.execute_job(), and
optionally auto-dispatches them.
"""

import sys
import os
import threading
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cron_lib

# ─── Logging ─────────────────────────────────────────────────────────────────

def _log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sys.stderr.write(f"[{ts}] [cron-scheduler] {msg}\n")
    sys.stderr.flush()


# ─── LangFuse tracing (optional) ────────────────────────────────────────────

def _trace_execution(job, task_id, success, error=None):
    """Create a LangFuse trace for a cron job execution."""
    try:
        from langfuse_client import create_trace
        create_trace(
            name="cron-execution",
            session_id=task_id,
            metadata={
                "cron_id": job["id"],
                "cron_name": job["name"],
                "cron_expr": job["cron_expr"],
                "auto_dispatch": job.get("auto_dispatch", True),
            },
            tags=[f"cron:{job['id']}", "cron"],
            input_data={"job_id": job["id"], "job_name": job["name"]},
            output_data={
                "task_id": task_id,
                "success": success,
                "error": error,
            },
        )
    except Exception:
        pass


# ─── Scheduler ───────────────────────────────────────────────────────────────

class CronScheduler:
    """Background cron scheduler that checks jobs every 30 seconds."""

    def __init__(self, tick_interval=30):
        self.tick_interval = tick_interval
        self._thread = None
        self._running = False

    def start(self):
        """Start the scheduler as a daemon thread."""
        if self._thread and self._thread.is_alive():
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="cron-scheduler")
        self._thread.start()
        _log(f"Started (tick every {self.tick_interval}s)")

    def stop(self):
        """Stop the scheduler."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        _log("Stopped")

    def _loop(self):
        """Main loop: tick, sleep, repeat."""
        # On startup, do an initial tick to catch any missed jobs
        self.tick(startup=True)
        while self._running:
            time.sleep(self.tick_interval)
            if self._running:
                self.tick()

    def tick(self, startup=False):
        """Check all jobs, execute any that are due."""
        try:
            jobs = cron_lib.list_jobs()
        except Exception as e:
            _log(f"Error loading jobs: {e}")
            return

        now = datetime.now(timezone.utc)
        executed = 0

        for job in jobs:
            if not job.get("enabled", False):
                continue

            # Check expiry
            if job.get("expires"):
                try:
                    exp = datetime.fromisoformat(job["expires"].replace("Z", "+00:00"))
                    if now > exp:
                        _log(f"Job {job['id']} expired, disabling")
                        cron_lib.update_job(job["id"], {"enabled": False, "next_run": None})
                        continue
                except (ValueError, TypeError):
                    pass

            # Check if due
            next_run = job.get("next_run")
            if not next_run:
                continue

            try:
                next_dt = datetime.fromisoformat(next_run.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                continue

            if next_dt > now:
                continue

            # On startup, skip jobs that are more than 1 hour overdue
            # (they missed their window; just advance to next run)
            if startup:
                hours_overdue = (now - next_dt).total_seconds() / 3600
                if hours_overdue > 1:
                    _log(f"Job {job['id']} is {hours_overdue:.1f}h overdue, skipping to next run")
                    new_next = cron_lib.compute_next_run(job["cron_expr"])
                    cron_lib.update_job(job["id"], {"next_run": new_next})
                    continue

            # Execute
            try:
                _log(f"Executing {job['id']} ({job['name']})")
                task_id, _ = cron_lib.execute_job(job)
                _log(f"Created {task_id} from {job['id']}")
                _trace_execution(job, task_id, success=True)
                executed += 1
            except Exception as e:
                _log(f"Error executing {job['id']}: {e}")
                _trace_execution(job, job["id"], success=False, error=str(e))
                # Advance next_run so we don't retry every tick
                try:
                    new_next = cron_lib.compute_next_run(job["cron_expr"])
                    cron_lib.update_job(job["id"], {"next_run": new_next})
                except Exception:
                    pass

        if executed > 0:
            _log(f"Tick complete: {executed} job(s) executed")


# ─── Standalone testing ──────────────────────────────────────────────────────

if __name__ == "__main__":
    _log("Running standalone — press Ctrl+C to stop")
    scheduler = CronScheduler(tick_interval=10)
    scheduler.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
