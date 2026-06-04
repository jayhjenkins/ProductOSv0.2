#!/usr/bin/env python3
"""
task_cli.py — CLI core for PM-OS task management.

Called by task.sh wrapper. Provides five core commands (add, list, show,
update, done) and agent convenience aliases (agent:start, agent:complete,
agent:fail, agent:ask).
"""

import argparse
import json
import os
import subprocess
import sys

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import task_lib


# ─── Output Formatting ──────────────────────────────────────────────────────

def _is_tty():
    return sys.stdout.isatty()


def _format_table(tasks):
    """Format tasks as a human-readable table."""
    if not tasks:
        print("No tasks found.")
        return

    # Header
    header = f"{'ID':<12} {'Queue':<9} {'Pri':<9} {'Status':<14} {'Domain':<11} Title"
    sep = "─" * 80
    print(header)
    print(sep)

    for t in tasks:
        domain = t.get("domain") or ""
        title = t.get("title", "")[:50]

        # Add waiting info for waiting queue
        if t.get("queue") == "waiting" and t.get("waiting_on"):
            waiting_info = f" (from: {t['waiting_on']}"
            if t.get("waiting_expected"):
                exp = str(t["waiting_expected"])
                waiting_info += f", exp: {exp}"
            if t.get("overdue"):
                waiting_info += " OVERDUE"
            waiting_info += ")"
            title = title[:35] + waiting_info

        print(f"{t['id']:<12} {t['queue']:<9} {t['priority']:<9} {t['status']:<14} {domain:<11} {title}")

    print(f"\n{len(tasks)} task(s)")


def _format_json(tasks):
    """Format tasks as JSON."""
    print(json.dumps(tasks, indent=2, default=str))


# ─── Command: add ────────────────────────────────────────────────────────────

def cmd_add(args):
    """Create a new task."""
    attendees = None
    if args.meeting_attendees:
        attendees = [a.strip() for a in args.meeting_attendees.split(",") if a.strip()]

    task_id, filepath = task_lib.create_task(
        title=args.title,
        queue=args.queue,
        priority=args.priority,
        domain=args.domain,
        due=args.due,
        tags=args.tags.split(",") if args.tags else None,
        creator=args.creator,
        description=args.description or "",
        source_meeting=args.source_meeting,
        project=args.project,
        waiting_on=args.waiting_on,
        waiting_expected=args.waiting_expected,
        task_type=args.task_type,
        meeting_attendees=attendees,
        meeting_duration=args.meeting_duration,
        meeting_title=args.meeting_title,
        meeting_description=args.meeting_description,
        message_channel=args.message_channel,
        message_to=args.message_to,
        message_subject=args.message_subject,
        message_body=args.message_body,
    )
    print(f"Created {task_id} in {args.queue} queue")
    print(f"  File: {os.path.relpath(filepath, os.path.dirname(task_lib.TASKS_DIR))}")

    # Event-driven dispatch: if task is in agent queue and auto-dispatch is on
    if args.queue == "agent" and os.environ.get("TASK_AUTO_DISPATCH") == "1":
        pm_os_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dispatch_script = os.path.join(pm_os_dir, "scripts", "task_dispatch.py")
        if os.path.exists(dispatch_script):
            subprocess.Popen(
                [sys.executable, dispatch_script, "--task", task_id],
                cwd=pm_os_dir,
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"  Auto-dispatching {task_id} to agent...")

    return task_id


# ─── Command: list ───────────────────────────────────────────────────────────

def cmd_list(args):
    """List tasks with optional filters."""
    tasks = task_lib.list_tasks(
        queue=args.queue,
        status=args.status,
        domain=args.domain,
        priority=args.priority,
    )

    if args.json or not _is_tty():
        _format_json(tasks)
    else:
        _format_table(tasks)


# ─── Command: show ───────────────────────────────────────────────────────────

def cmd_show(args):
    """Show full task detail."""
    content = task_lib.get_task_full(args.task_id)
    print(content)


# ─── Command: update ─────────────────────────────────────────────────────────

def cmd_update(args):
    """Update task fields and/or append a comment."""
    changes = {}
    if args.status:
        changes["status"] = args.status
    if args.priority:
        changes["priority"] = args.priority
    if args.due:
        changes["due"] = args.due
    if args.domain:
        changes["domain"] = args.domain
    if args.queue:
        changes["queue"] = args.queue
    if args.project:
        changes["project"] = args.project
    if args.agent_status:
        changes["agent_status"] = args.agent_status
    if args.agent_output:
        changes["agent_output"] = args.agent_output
    if args.agent_error:
        changes["agent_error"] = args.agent_error
    if args.waiting_on:
        changes["waiting_on"] = args.waiting_on
    if args.waiting_expected:
        changes["waiting_expected"] = args.waiting_expected
    if getattr(args, "message_channel", None):
        changes["message_channel"] = args.message_channel
    if getattr(args, "message_to", None):
        changes["message_to"] = args.message_to
    if getattr(args, "message_subject", None):
        changes["message_subject"] = args.message_subject
    if getattr(args, "message_body", None):
        changes["message_body"] = args.message_body

    comment = args.comment
    actor = args.actor or "human"

    if not changes and not comment:
        print("No changes specified. Use --status, --priority, --queue, --comment, etc.")
        sys.exit(1)

    filepath = task_lib.update_task(args.task_id, changes=changes, comment=comment, actor=actor)
    print(f"Updated {args.task_id}")
    if args.queue:
        print(f"  Moved to {args.queue} queue")


# ─── Command: done ───────────────────────────────────────────────────────────

def cmd_done(args):
    """Mark task complete and archive."""
    archive_path = task_lib.complete_task(
        args.task_id,
        output_path=args.output,
        actor="human",
    )
    print(f"Completed {args.task_id}")
    print(f"  Archived to: {os.path.relpath(archive_path, os.path.dirname(task_lib.TASKS_DIR))}")


# ─── Agent Convenience Aliases ───────────────────────────────────────────────

def cmd_agent_start(args):
    """Mark task as in-progress by agent."""
    now = task_lib._now_iso()
    changes = {
        "status": "in-progress",
        "agent_status": "running",
        "agent_started": now,
    }
    task_lib.update_task(args.task_id, changes=changes,
                         comment="Agent starting work on this task.",
                         actor="agent")
    print(f"Agent started {args.task_id}")


def cmd_agent_complete(args):
    """Agent finished its work. Status stays open until the human approves via
    task.sh done or the UI; this only flips agent_status so the task surfaces
    in the inbox's agent_completed review bucket."""
    now = task_lib._now_iso()
    changes = {
        "agent_status": "complete",
        "agent_completed": now,
    }
    if args.output:
        changes["agent_output"] = args.output
        # Compute SharePoint path and URL so Word link appears on task card
        sp = task_lib._sharepoint_path(args.output)
        if sp:
            changes["sharepoint_path"] = sp
        sp_url = task_lib._sharepoint_url(args.output)
        if sp_url:
            changes["sharepoint_url"] = sp_url

    comment = "Agent work complete."
    if args.output:
        comment += f" Output: {args.output}"
    comment += " Awaiting human review."

    task_lib.update_task(args.task_id, changes=changes,
                         comment=comment, actor="agent")
    # Trigger doc sync for the output file
    if args.output and changes.get("sharepoint_path"):
        task_lib._trigger_doc_sync(args.output)
    print(f"Agent completed {args.task_id} — awaiting human review")
    if args.output:
        print(f"  Output: {args.output}")
        _spawn_judge(args.task_id)


def _spawn_judge(task_id):
    """Fire the shadow judge detached so it scores the artifact without blocking
    or affecting completion. Strictly additive — any failure here is swallowed."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        pm_os_dir = os.path.dirname(script_dir)
        log_dir = os.path.join(pm_os_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, f"judge-{task_id}.log")
        logf = open(log_path, "a")
        subprocess.Popen(
            [sys.executable, os.path.join(script_dir, "judge.py"), "--task", task_id],
            cwd=pm_os_dir,
            stdout=logf,
            stderr=logf,
            start_new_session=True,
        )
        print(f"  Judge dispatched (log: logs/judge-{task_id}.log)")
    except Exception as e:
        print(f"  (judge not dispatched: {e})")


def cmd_agent_fail(args):
    """Mark task as failed by agent."""
    changes = {
        "agent_status": "failed",
        "agent_error": args.error,
        "_comment_type": "error",
    }
    task_lib.update_task(args.task_id, changes=changes,
                         comment=f"Agent failed: {args.error}",
                         actor="agent")
    print(f"Agent failed {args.task_id}: {args.error}")


def cmd_agent_ask(args):
    """Agent asks a question, blocks task, moves to collab (except cron-sourced)."""
    # Read current task to check queue and creator
    task_data = task_lib.read_task(args.task_id)
    current_queue = task_data["queue"]
    creator = task_data.get("creator")

    changes = {
        "status": "blocked",
        "agent_status": "needs-human",
        "_comment_type": "question",
    }
    # Cron-sourced tasks stay in the agent column so recurring work
    # remains grouped with the agent queue even when blocked.
    if current_queue == "agent" and creator != "cron":
        changes["queue"] = "collab"

    task_lib.update_task(args.task_id, changes=changes,
                         comment=f"[question] {args.question}",
                         actor="agent")
    print(f"Agent question on {args.task_id}: {args.question}")
    if changes.get("queue") == "collab":
        print(f"  Moved to collab queue for human response")
    elif creator == "cron":
        print(f"  Kept in agent queue (cron-sourced task)")


# ─── Command: inbox ──────────────────────────────────────────────────────────

def cmd_inbox(args):
    """Show human inbox digest."""
    inbox = task_lib.get_inbox()
    today = task_lib.datetime.now(task_lib.timezone.utc).strftime("%Y-%m-%d")

    needs_attention = len(inbox["agent_questions"]) + len(inbox["agent_completed"])

    print("=" * 72)
    print(f"  PM-OS INBOX — {today}                    {needs_attention} need attention")
    print("=" * 72)
    print()

    # Agent questions
    if inbox["agent_questions"]:
        print("AGENT QUESTIONS (need your answer):")
        for t in inbox["agent_questions"]:
            domain = f"[{t.get('domain', '?')}]" if t.get("domain") else ""
            print(f"  {t['id']}  {domain:<12}  {t['title'][:50]}")
        print()

    # Agent completed
    if inbox["agent_completed"]:
        print("COMPLETED BY AGENT (need your review):")
        for t in inbox["agent_completed"]:
            domain = f"[{t.get('domain', '?')}]" if t.get("domain") else ""
            print(f"  {t['id']}  {domain:<12}  {t['title'][:50]}")
        print()

    # Human open tasks
    if inbox["human_open"]:
        print("YOUR OPEN TASKS:")
        for t in inbox["human_open"]:
            domain = f"[{t.get('domain', '?')}]" if t.get("domain") else ""
            due = f"due:{t['due']}" if t.get("due") else ""
            print(f"  {t['id']}  {domain:<12}  {t['priority']:<9}  {due:<14}  {t['title'][:40]}")
        print()

    # Waiting
    if inbox["waiting"]:
        print("WAITING ON OTHERS:")
        for t in inbox["waiting"]:
            overdue_flag = "  OVERDUE" if t.get("overdue") else ""
            waiting_on = t.get("waiting_on") or "unknown"
            exp = f"expected:{t['waiting_expected']}" if t.get("waiting_expected") else ""
            print(f"  {t['id']}  {waiting_on:<20}  {exp:<20}  {t['title'][:30]}{overdue_flag}")
        print()

    # Summary
    summary = inbox["summary"]
    parts = [f"{v} {k}" for k, v in summary.items()]
    print(f"SUMMARY: {' | '.join(parts)} | {inbox['total']} total")
    print("=" * 72)


# ─── Argument Parsing ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="task",
        description="PM-OS Task Management CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # ─── add ─────────────────────────────────────────────────────────────
    p_add = subparsers.add_parser("add", help="Create a new task")
    p_add.add_argument("title", help="Task title")
    p_add.add_argument("-q", "--queue", default="human", choices=task_lib.QUEUES)
    p_add.add_argument("-p", "--priority", default="medium", choices=task_lib.PRIORITIES)
    p_add.add_argument("-d", "--domain", default=None, choices=task_lib.DOMAINS)
    p_add.add_argument("--due", default=None, help="Due date (ISO format)")
    p_add.add_argument("--tags", default=None, help="Comma-separated tags")
    p_add.add_argument("--creator", default="human", choices=["human", "agent"])
    p_add.add_argument("--description", default="", help="Task description")
    p_add.add_argument("--source-meeting", default=None, help="Source meeting filename")
    p_add.add_argument("--project", default=None, help="Project grouping")
    p_add.add_argument("--waiting-on", default=None, help="Who you're waiting on (waiting queue)")
    p_add.add_argument("--waiting-expected", default=None, help="Expected date (waiting queue)")
    p_add.add_argument("--task-type", default=None, help="Task type (e.g., schedule-meeting)")
    p_add.add_argument("--meeting-attendees", default=None, help="Comma-separated attendee emails")
    p_add.add_argument("--meeting-duration", type=int, default=None, help="Meeting duration in minutes (default 30)")
    p_add.add_argument("--meeting-title", default=None, help="Calendar event title")
    p_add.add_argument("--meeting-description", default=None, help="Calendar event description")
    p_add.add_argument("--message-channel", default=None, help="Message channel (send-message): Teams, Email, Slack")
    p_add.add_argument("--message-to", default=None, help="Message recipient (send-message)")
    p_add.add_argument("--message-subject", default=None, help="Message subject (send-message, email)")
    p_add.add_argument("--message-body", default=None, help="Message body draft (send-message)")
    p_add.set_defaults(func=cmd_add)

    # ─── list ────────────────────────────────────────────────────────────
    p_list = subparsers.add_parser("list", help="List tasks")
    p_list.add_argument("--queue", default=None, choices=task_lib.QUEUES)
    p_list.add_argument("--status", default=None, choices=task_lib.STATUSES)
    p_list.add_argument("--domain", default=None, choices=task_lib.DOMAINS)
    p_list.add_argument("--priority", default=None, choices=task_lib.PRIORITIES)
    p_list.add_argument("--json", action="store_true", help="JSON output")
    p_list.set_defaults(func=cmd_list)

    # ─── show ────────────────────────────────────────────────────────────
    p_show = subparsers.add_parser("show", help="Show full task detail")
    p_show.add_argument("task_id", help="Task ID (e.g., TASK-0001)")
    p_show.set_defaults(func=cmd_show)

    # ─── update ──────────────────────────────────────────────────────────
    p_update = subparsers.add_parser("update", help="Update task fields")
    p_update.add_argument("task_id", help="Task ID")
    p_update.add_argument("--status", choices=task_lib.STATUSES)
    p_update.add_argument("--priority", choices=task_lib.PRIORITIES)
    p_update.add_argument("--queue", choices=task_lib.QUEUES)
    p_update.add_argument("--domain", choices=task_lib.DOMAINS)
    p_update.add_argument("--due", default=None)
    p_update.add_argument("--project", default=None)
    p_update.add_argument("--comment", default=None, help="Activity log comment")
    p_update.add_argument("--actor", default="human", choices=["human", "agent"])
    p_update.add_argument("--agent-status", default=None, choices=task_lib.AGENT_STATUSES)
    p_update.add_argument("--agent-output", default=None)
    p_update.add_argument("--agent-error", default=None)
    p_update.add_argument("--waiting-on", default=None)
    p_update.add_argument("--waiting-expected", default=None)
    p_update.add_argument("--message-channel", default=None, help="Message channel (send-message)")
    p_update.add_argument("--message-to", default=None, help="Message recipient (send-message)")
    p_update.add_argument("--message-subject", default=None, help="Message subject (send-message)")
    p_update.add_argument("--message-body", default=None, help="Message body draft (send-message)")
    p_update.set_defaults(func=cmd_update)

    # ─── done ────────────────────────────────────────────────────────────
    p_done = subparsers.add_parser("done", help="Mark task complete and archive")
    p_done.add_argument("task_id", help="Task ID")
    p_done.add_argument("--output", default=None, help="Path to output artifact")
    p_done.set_defaults(func=cmd_done)

    # ─── agent:start ─────────────────────────────────────────────────────
    p_astart = subparsers.add_parser("agent:start", help="Agent marks task in-progress")
    p_astart.add_argument("task_id", help="Task ID")
    p_astart.set_defaults(func=cmd_agent_start)

    # ─── agent:complete ──────────────────────────────────────────────────
    p_acomplete = subparsers.add_parser("agent:complete", help="Agent marks task done")
    p_acomplete.add_argument("task_id", help="Task ID")
    p_acomplete.add_argument("--output", default=None, help="Path to output artifact")
    p_acomplete.set_defaults(func=cmd_agent_complete)

    # ─── agent:fail ──────────────────────────────────────────────────────
    p_afail = subparsers.add_parser("agent:fail", help="Agent reports failure")
    p_afail.add_argument("task_id", help="Task ID")
    p_afail.add_argument("--error", required=True, help="Error message")
    p_afail.set_defaults(func=cmd_agent_fail)

    # ─── agent:ask ───────────────────────────────────────────────────────
    p_aask = subparsers.add_parser("agent:ask", help="Agent asks question")
    p_aask.add_argument("task_id", help="Task ID")
    p_aask.add_argument("question", help="Question for the human")
    p_aask.set_defaults(func=cmd_agent_ask)

    # ─── inbox ───────────────────────────────────────────────────────────
    p_inbox = subparsers.add_parser("inbox", help="Show human inbox digest")
    p_inbox.set_defaults(func=cmd_inbox)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
