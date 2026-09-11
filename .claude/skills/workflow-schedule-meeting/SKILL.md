---
name: workflow-schedule-meeting
description: Find available meeting times via Microsoft 365 MCP and write structured time slot options into a collab task for human selection
---

# Schedule Meeting Workflow

## Purpose

Automate the scheduling legwork: find mutually available times for meeting attendees using the Microsoft 365 MCP, format them as selectable options in the task, and let the operator pick one in the web UI.

## When to Use

- Task has `task_type: schedule-meeting` in its frontmatter
- Task is in the `collab` queue with status `open`

## Core Rule (MANDATORY)

You ALWAYS deliver 3–4 selectable slots and end with `agent:complete`. The web UI renders a slot picker — the operator's interaction is clicking, not answering questions.

Never use `agent:ask` to:
- Ask which slot is best
- Ask permission to widen the search
- Ask whether to propose imperfect options (soft calendar conflicts are fine — note them inline)
- Ask whether to propose despite missing attendee availability (use the the operator-only fallback in Step 4)

`agent:ask` is reserved for hard blockers only: unresolvable attendee email, mgc auth failure, or genuinely zero the operator availability across 10 business days.

## Workflow

### 1. Read the Task

```bash
./scripts/task.sh show {TASK_ID}
```

Extract from frontmatter:
- `meeting_attendees` — list of email addresses
- `meeting_duration` — minutes (default 30)
- `meeting_title` — calendar event title
- `meeting_description` — event body text
- `source_meeting` — transcript that spawned this task (if any)

**Validate `meeting_description` for calendar appropriateness.** The `meeting_description` field becomes the calendar invite body that all attendees see. If it is empty, reads like internal task notes (e.g., "the operator mentioned wanting to..." or "At end of catch-up, someone suggested..."), or describes how the task was created rather than what the meeting is *for*, rewrite it:

1. Derive the meeting's purpose from the task title, task description, and source meeting transcript (if available)
2. Write 1-2 concise sentences describing what the meeting is about from the attendees' perspective
3. Update the `meeting_description` frontmatter field with the rewritten version before proceeding

Examples of rewrites:
| Original | Rewritten |
|---|---|
| *(empty)* | "Biweekly sync to review product roadmap progress and discuss blockers" |
| "During standup the operator said they'd set up time to align on the mobile rollout" | "Align on mobile rollout plan, timeline, and next steps" |
| "A teammate suggested standardizing a recurring touch base to stay aligned on billing" | "Recurring sync to stay aligned on billing priorities and surface blockers early" |

### 2. Gather Time Preferences (Optional)

If `source_meeting` exists, read the transcript and look for scheduling hints:
- "next week", "this Thursday", "before Friday"
- "30 minutes", "an hour"
- "morning", "afternoon"

Use these to narrow the search window. If no hints, default to **next 5 business days**.

### 3. Resolve Attendee Emails

If any attendee entry looks like a name (no `@`), attempt to resolve it in this order:

1. **Check the source transcript** — if `source_meeting` exists, read it and look for the `participant_emails:` frontmatter field. This maps participant names to corporate emails (resolved at ingest via Microsoft Graph). Match attendee names against this mapping.
2. **Check the email cache** — read `datasets/people/email_cache.json` which accumulates all resolved name→email mappings across transcripts.
3. **Search Outlook** — use MCP tool `outlook_email_search` to search your mailbox for messages from/to that person's name and extract their email from the results.
4. **If all fail** — use `agent:ask` to request the email from the operator:
   ```bash
   ./scripts/task.sh agent:ask {TASK_ID} "I need the email address for {name}. Who should I invite?"
   ```
   Then STOP. Do not continue.

### 4. Find Available Times

Run the `find_meeting_times.py` script (uses `mgc` CLI to call Microsoft Graph findMeetingTimes):

```bash
python3 ./scripts/find_meeting_times.py \
  --attendees "email1@co.com,email2@co.com" \
  --duration 30 \
  --max-slots 4
```

The script defaults to the next 5 business days. To narrow by transcript hints:
```bash
python3 ./scripts/find_meeting_times.py \
  --attendees "email@co.com" \
  --duration 30 \
  --start "2026-03-25" \
  --end "2026-03-28" \
  --max-slots 4
```

If the result has zero slots (`"slots": []`) OR `empty_reason` indicates `AttendeesUnavailableOrUnknown` (Graph can't see an attendee's calendar — permissions, free/busy not shared, etc.):

1. **Expand once.** Add 5 more business days via `--start`/`--end` and retry. If that returns slots, use them.

2. **the operator-only fallback.** If still zero/unknown, propose 4 slots from the operator's preferred ad hoc windows (Tue/Thu afternoons, Mon 2:00–4:00 PM ET) that do not conflict with the operator's calendar. Run `find_meeting_times.py` with `--attendees "<jay's email only>"` to confirm the operator is free, then format those as the suggested times. In the display line for each slot, append `(attendee calendar not visible — they'll RSVP)` instead of the normal `(all attendees free)` parenthetical.

3. **Hard block only.** Only call `agent:ask` if the operator himself has zero availability across the next 10 business days — that is a real scheduling failure. Do NOT ask whether to widen, whether to propose anyway, or which option is best.

**Do NOT use MCP tools for availability lookup** — the headless dispatch environment does not have MCP access. Always use the `find_meeting_times.py` script.

### 5. Format Suggested Times

Write a `## Suggested Times` section into the task description. Each slot MUST include an HTML comment with machine-parseable data followed by a human-readable line.

**For each slot, cross-reference the ET time against the operator's Calendar Structure Reference (below) and append a short contextual note** after the availability info. The note should help the operator evaluate soft tradeoffs at a glance. Keep each note to 1 short sentence max.

Context notes should cover whichever of these is most relevant to that slot:
- Whether it falls in a designated block (1:1 block, focus time, etc.)
- Back-to-back risk with adjacent meetings ("follows your Pay L10 — tight transition")
- Day character ("Tuesday is already your heaviest day")
- Policy fit for recurring meetings ("inside your Thursday 1:1 block" or "outside 1:1 block — fine for ad hoc")
- Clean openings ("open slot, no adjacency issues")

```markdown
## Suggested Times

<!-- SLOT:1|2026-03-25T14:00:00Z|2026-03-25T14:30:00Z -->
**Option 1:** Tuesday, March 25 at 10:00 AM - 10:30 AM ET _(all attendees free)_ — overlaps Home Standup window

<!-- SLOT:2|2026-03-26T18:00:00Z|2026-03-26T18:30:00Z -->
**Option 2:** Wednesday, March 26 at 2:00 PM - 2:30 PM ET _(all attendees free)_ — right before Home L10 at 2:30

<!-- SLOT:3|2026-03-27T15:00:00Z|2026-03-27T15:30:00Z -->
**Option 3:** Thursday, March 27 at 11:00 AM - 11:30 AM ET _(all attendees free)_ — open slot, no adjacency issues

<!-- SLOT:4|2026-03-27T18:00:00Z|2026-03-27T18:30:00Z -->
**Option 4:** Thursday, March 27 at 2:00 PM - 2:30 PM ET _(all attendees free)_ — inside your 1:1 block (good for recurring 1:1s)
```

**Critical format requirements:**
- `<!-- SLOT:N|startISO|endISO -->` — the web UI JavaScript parses these HTML comments to render the time picker. They must be on their own line, exactly this format.
- Start/end times in the comments are UTC (ISO 8601 with Z suffix)
- Display times are converted to ET (America/New_York) for readability
- Include day of week + date + time range in the display text
- Context note goes after the availability parenthetical, separated by " — " (em dash is OK here in UI display text, not in prose content)

### 6. Update the Task

Append the suggested times to the task description:

```bash
./scripts/task.sh update {TASK_ID} \
  --comment "Found {N} available time slots for: {attendee list}. Select a slot in the task board UI to create the calendar event."
```

Also update the description body to include the `## Suggested Times` section. Use `task_lib.update_task_description()` or write the updated body directly.

### 7. Complete Agent Work

```bash
./scripts/task.sh agent:complete {TASK_ID}
```

The task stays in the `collab` queue with `agent_status: complete` for the operator to review and select a time slot in the web UI.

## The Operator's Calendar Structure Reference

Use this reference when annotating suggested time slots in Step 5. **This section is a
placeholder template** — it's personal scheduling nuance, so per this system's own convention
(never bake person-specific nuance into a shared skill), replace it with your own real patterns
before relying on it. The shape below shows what's worth capturing; the specifics are illustrative
only.

### Work Hours & Hard Constraints
- **Work hours:** e.g. 9:00 AM - 5:00 PM ET, Monday-Friday
- **Hard start / end:** any buffer before/after standard hours you protect
- **Lunch hold:** e.g. Noon-1:00 PM daily
- **Other recurring personal constraints:** any other daily windows that are consistently unavailable

### Daily Anchors (Every Day)
- List any daily recurring standups/syncs that should never be double-booked, with their time and whether they're tentative or hard.

### Focus Time Blocks (Hard-Protected)
- List the blocks you protect for deep work, by day and time, noting which are most protected.

### Day Characters
- For each weekday, a one-line summary of that day's typical rhythm and its key recurring meetings — useful context for the model when suggesting or avoiding times.

### 1:1 Scheduling Policy
- Where recurring 1:1s live by default, and any established exceptions.
- Guidance for ad hoc/one-off 1:1s: which days/times you generally prefer, and which to avoid.

### Preferred Scheduling Slots (for ad hoc meetings)
- **Best:** the day/time windows you'd default to when proposing ad hoc meeting slots
- **Avoid:** the day/time windows to steer away from (focus blocks, low-energy periods, etc.)

## Error Handling

| Error | Action |
|-------|--------|
| `mgc` not found | `agent:fail` with install instructions |
| mgc auth expired | `agent:fail` — "Run `mgc login --scopes 'Calendars.ReadWrite User.Read.All'`" |
| No attendee emails resolvable | `agent:ask` the operator for email addresses |
| Zero availability found | Expand range once, then fall through to the operator-only fallback (Step 4). Do not ask. |
| `AttendeesUnavailableOrUnknown` | Same — propose against the operator's calendar, tag each slot "(attendee calendar not visible — they'll RSVP)". |
| All slots have soft conflicts | Propose them anyway with conflict notes inline. Do not ask "want to widen?". |

## Success Criteria

- Task updated with 2-4 selectable time slots
- HTML comments in exact `<!-- SLOT:N|start|end -->` format
- Display times in ET with day-of-week
- Agent status set to `complete`
- Task remains in collab queue for human selection
