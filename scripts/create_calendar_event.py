#!/usr/bin/env python3
"""
create_calendar_event.py — Create an Outlook calendar event via mgc CLI.

Usage:
    python3 scripts/create_calendar_event.py \
      --subject "Meeting Title" \
      --start "2026-03-25T14:00:00" \
      --end "2026-03-25T14:30:00" \
      --timezone "America/New_York" \
      --attendees "alice@co.com,bob@co.com" \
      --body "Meeting description" \
      [--dry-run]
"""

import argparse
import json
import shutil
import subprocess
import sys


def build_event_payload(subject, start, end, timezone, attendees=None, body=None,
                        recurring=None):
    """Build a Microsoft Graph API calendar event JSON payload."""
    event = {
        "subject": subject,
        "start": {
            "dateTime": start,
            "timeZone": timezone,
        },
        "end": {
            "dateTime": end,
            "timeZone": timezone,
        },
        "isOnlineMeeting": True,
        "onlineMeetingProvider": "teamsForBusiness",
    }

    if body:
        event["body"] = {
            "contentType": "text",
            "content": body,
        }

    if attendees:
        event["attendees"] = [
            {
                "emailAddress": {
                    "address": email.strip(),
                    "name": email.strip().split("@")[0],
                },
                "type": "required",
            }
            for email in attendees
            if email.strip()
        ]

    if recurring:
        # Determine recurrence pattern from the start datetime
        from datetime import datetime as _dt
        start_dt = _dt.fromisoformat(start)
        day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        day_of_week = day_names[start_dt.weekday()]
        start_date = start_dt.strftime("%Y-%m-%d")

        if recurring == "monthly":
            event["recurrence"] = {
                "pattern": {
                    "type": "absoluteMonthly",
                    "interval": 1,
                    "dayOfMonth": start_dt.day,
                },
                "range": {
                    "type": "noEnd",
                    "startDate": start_date,
                },
            }
        else:
            interval = 2 if recurring == "biweekly" else 1
            event["recurrence"] = {
                "pattern": {
                    "type": "weekly",
                    "interval": interval,
                    "daysOfWeek": [day_of_week],
                },
                "range": {
                    "type": "noEnd",
                    "startDate": start_date,
                },
            }

    return event


def create_event(payload, dry_run=False):
    """Create a calendar event using mgc CLI.

    Returns the parsed JSON response from Graph API on success.
    Raises RuntimeError on failure.
    """
    if dry_run:
        print(json.dumps(payload, indent=2))
        return {"dry_run": True, "payload": payload}

    # Check mgc is available
    if not shutil.which("mgc"):
        raise RuntimeError(
            "mgc (Microsoft Graph CLI) not found.\n"
            "Install: brew install microsoft/microsoft-graph-cli/mgc\n"
            "Auth:    mgc login --scopes \"Calendars.ReadWrite\""
        )

    try:
        result = subprocess.run(
            ["mgc", "me", "events", "create", "--body", json.dumps(payload)],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("mgc command timed out after 30 seconds")
    except FileNotFoundError:
        raise RuntimeError("mgc command not found in PATH")

    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "auth" in stderr.lower() or "token" in stderr.lower() or "login" in stderr.lower():
            raise RuntimeError(
                f"Authentication error. Run: mgc login --scopes \"Calendars.ReadWrite\"\n"
                f"Details: {stderr}"
            )
        raise RuntimeError(f"mgc failed (exit {result.returncode}): {stderr}")

    # Parse response
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError:
        # mgc may output non-JSON on success; return stdout as-is
        response = {"raw_output": result.stdout.strip()}

    return response


def main():
    parser = argparse.ArgumentParser(
        description="Create an Outlook calendar event via mgc CLI"
    )
    parser.add_argument("--subject", required=True, help="Event subject/title")
    parser.add_argument("--start", required=True, help="Start datetime (ISO 8601, no timezone)")
    parser.add_argument("--end", required=True, help="End datetime (ISO 8601, no timezone)")
    parser.add_argument("--timezone", default="America/New_York", help="IANA timezone (default: America/New_York)")
    parser.add_argument("--attendees", default=None, help="Comma-separated attendee emails")
    parser.add_argument("--body", default=None, help="Event body/description text")
    parser.add_argument("--recurring", default=None, choices=["weekly", "biweekly", "monthly"],
                        help="Make this a recurring event (weekly, biweekly, or monthly)")
    parser.add_argument("--dry-run", action="store_true", help="Print payload without creating event")
    args = parser.parse_args()

    attendees = None
    if args.attendees:
        attendees = [a.strip() for a in args.attendees.split(",") if a.strip()]

    payload = build_event_payload(
        subject=args.subject,
        start=args.start,
        end=args.end,
        timezone=args.timezone,
        attendees=attendees,
        body=args.body,
        recurring=args.recurring,
    )

    try:
        result = create_event(payload, dry_run=args.dry_run)
        print(json.dumps(result, indent=2))
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
