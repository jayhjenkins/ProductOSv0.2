#!/usr/bin/env python3
"""
find_meeting_times.py — Find available meeting slots via mgc CLI (Microsoft Graph).

Usage:
    python3 scripts/find_meeting_times.py \
      --attendees "alice@co.com,bob@co.com" \
      --duration 30 \
      --start "2026-03-23" \
      --end "2026-03-28" \
      [--max-slots 4] \
      [--timezone "America/New_York"]

Output: JSON array of slot suggestions with start/end times (UTC) and availability info.
"""

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta


def find_meeting_times(attendees, duration_minutes, start_date, end_date,
                       timezone="America/New_York", max_slots=4):
    """Call Microsoft Graph findMeetingTimes via mgc CLI.

    Returns list of dicts: [{start, end, confidence, attendee_availability}, ...]
    """
    if not shutil.which("mgc"):
        raise RuntimeError(
            "mgc (Microsoft Graph CLI) not found.\n"
            "Install from: https://github.com/microsoftgraph/msgraph-cli/releases\n"
            "Auth: mgc login --scopes \"Calendars.ReadWrite User.Read.All\""
        )

    # Build the request payload
    payload = {
        "attendees": [
            {
                "emailAddress": {"address": email.strip()},
                "type": "required",
            }
            for email in attendees
            if email.strip()
        ],
        "timeConstraint": {
            "timeslots": [
                {
                    "start": {
                        "dateTime": f"{start_date}T09:00:00",
                        "timeZone": timezone,
                    },
                    "end": {
                        "dateTime": f"{end_date}T17:00:00",
                        "timeZone": timezone,
                    },
                }
            ]
        },
        "meetingDuration": f"PT{duration_minutes}M",
        "maxCandidates": max_slots,
    }

    body_json = json.dumps(payload)

    try:
        result = subprocess.run(
            ["mgc", "me", "find-meeting-times", "post", "--body", body_json],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("mgc findMeetingTimes timed out after 30 seconds")

    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "token" in stderr.lower() or "login" in stderr.lower():
            raise RuntimeError(
                f"Authentication error. Run: mgc login --scopes \"Calendars.ReadWrite\"\n"
                f"Details: {stderr}"
            )
        raise RuntimeError(f"mgc failed (exit {result.returncode}): {stderr}")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"Failed to parse mgc response: {result.stdout[:500]}")

    suggestions = data.get("meetingTimeSuggestions", [])

    # Parse into simpler format
    slots = []
    for s in suggestions:
        slot = s.get("meetingTimeSlot", {})
        start = slot.get("start", {})
        end = slot.get("end", {})

        attendee_avail = []
        for aa in s.get("attendeeAvailability", []):
            attendee_avail.append({
                "email": aa.get("attendee", {}).get("emailAddress", {}).get("address", ""),
                "availability": aa.get("availability", "unknown"),
            })

        slots.append({
            "start": start.get("dateTime", ""),
            "end": end.get("dateTime", ""),
            "timezone": start.get("timeZone", "UTC"),
            "confidence": s.get("confidence", 0),
            "organizer_availability": s.get("organizerAvailability", "unknown"),
            "attendee_availability": attendee_avail,
        })

    return {
        "slots": slots,
        "empty_reason": data.get("emptySuggestionsReason", ""),
    }


def _business_date_range(days_out=5):
    """Return start and end date strings for the next N business days."""
    today = datetime.now()
    # Start from tomorrow
    start = today + timedelta(days=1)
    # Skip to Monday if weekend
    if start.weekday() >= 5:
        start += timedelta(days=(7 - start.weekday()))

    end = start
    biz_days = 0
    while biz_days < days_out:
        end += timedelta(days=1)
        if end.weekday() < 5:
            biz_days += 1

    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def main():
    parser = argparse.ArgumentParser(
        description="Find available meeting times via Microsoft Graph"
    )
    parser.add_argument("--attendees", required=True, help="Comma-separated attendee emails")
    parser.add_argument("--duration", type=int, default=30, help="Meeting duration in minutes")
    parser.add_argument("--start", default=None, help="Start date (YYYY-MM-DD, default: next business day)")
    parser.add_argument("--end", default=None, help="End date (YYYY-MM-DD, default: 5 business days out)")
    parser.add_argument("--max-slots", type=int, default=4, help="Max number of suggestions")
    parser.add_argument("--timezone", default="America/New_York", help="IANA timezone")
    args = parser.parse_args()

    attendees = [a.strip() for a in args.attendees.split(",") if a.strip()]
    if not attendees:
        print("Error: no attendees provided", file=sys.stderr)
        sys.exit(1)

    start_date = args.start
    end_date = args.end
    if not start_date or not end_date:
        default_start, default_end = _business_date_range(5)
        start_date = start_date or default_start
        end_date = end_date or default_end

    try:
        result = find_meeting_times(
            attendees=attendees,
            duration_minutes=args.duration,
            start_date=start_date,
            end_date=end_date,
            timezone=args.timezone,
            max_slots=args.max_slots,
        )
        print(json.dumps(result, indent=2))
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
