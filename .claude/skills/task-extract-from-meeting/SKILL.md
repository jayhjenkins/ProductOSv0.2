---
name: task-extract-from-meeting
description: Use when processing meeting transcripts to identify tasks that Jay personally owns or needs to follow up on
---

# Task Extract from Meeting

## Purpose

Extract tasks from meeting transcripts that are **specifically relevant to Jay**. This is Jay's personal task system — not a project management tool for everyone in the meeting. The core question for every potential task is: **"Is this something Jay needs to do, or something Jay needs to make sure doesn't fall through the cracks?"**

## The Filter (apply to EVERY potential task)

Before creating any task, it must pass this test — **is Jay the owner or the tracker?**

1. **Did Jay commit to doing this?** → route via Queue Logic below
2. **Did Jay ask someone to do something, and he needs the result?** → `waiting` queue
3. **Did someone promise to send Jay (or Jay's group) a specific deliverable?** → `waiting` queue

If the answer to ALL three is no → **skip it. Do not create a task.**

### What to SKIP

- Someone else's action item that doesn't involve Jay ("Mason will fix the bug")
- Team standup updates where people report their own blockers
- General team commitments Jay isn't responsible for tracking
- Background discussion, context-setting, or knowledge transfer
- Someone else's deliverable to someone else
- Standard process steps ("recruiting will send next steps to the candidate")

### The Standup Problem

In standups and team meetings, people report what they're working on and what's blocking them. **Almost none of this is Jay's task.** Only extract from standups when:
- Jay explicitly says "I'll look into that" or "Let me follow up on that" or similar
- Someone asks Jay directly to do something
- Jay asks someone to send him something specific

## Queue Logic: Agent-First Routing

**The whole point of PM-OS is to take work off Jay's plate.** When Jay commits to something in a meeting, the first question is: **can the agent do most of this work?**

### Route to `agent` when the work produces:

- **A written artifact** — memo, PRD, strategy doc, experiment design, tradeoff analysis, competitive research, summary, brief, any document
- **Research or context gathering** — "we need to understand X", "look into Y", "figure out the competitive landscape", "what are our options for Z"
- **Data analysis or synthesis** — pulling together information from multiple sources, analyzing trends, summarizing findings
- **First drafts** that Jay will review — the agent writes, Jay approves/edits

These map to existing PM-OS workflows. When creating agent tasks, note the relevant skill in the description so the dispatcher knows which workflow to invoke:

| Work type | PM-OS skill/workflow |
|-----------|---------------------|
| Product strategy, vision docs | `product-strategy-creation` |
| PRDs, requirements, user stories | `prd-creation` |
| Strategic analysis, decision frameworks | `strategy-session`, `strategy-memo` |
| Competitive/market research | `research-gathering` (context assembly) |
| Metric analysis, experiment design | `metrics-definition`, `metric-diagnosis`, `tradeoff-decision` |
| Meeting synthesis, context summaries | `meeting-synthesis` (context assembly) |
| Priority scoring, roadmap sequencing | `priority-scoring` (context assembly) |

### Route to `collab` when:

- **A decision needs to be made** — the agent gathers context, writes the decision document, and Jay decides. The agent does the legwork; Jay provides judgment.
- **The work requires Jay's input partway through** — e.g., "pick the top 3, then I'll draft from there"
- **The agent itself must act on an external system** — post to Slack, publish to Jira, book a meeting, send a Teams message, update SharePoint. The external action is the agent's step, not Jay's.

**Important:** End-of-task human review does NOT make something `collab`. Every agent task ends with Jay reviewing the output before it's used — that's the baseline, not a queue distinction. If the agent's work is self-contained (produce a draft, do research, write a doc) and Jay is the one who sends/shares/acts on it afterward, it's `agent`, not `collab`. "Draft X and send to Y" = agent drafts → Jay reviews → Jay sends. The "send to Y" is Jay's step, so the task is `agent`.

### Route to `collab` with `--task-type send-message` when:

- **The task is to communicate with a person** — "talk to Will about X", "share this with Brandon", "forward the issue to the responsible PM", "loop in / reach out to / ping someone". The primary action is conveying something to a person, not producing an artifact and not a full meeting.
- This is the **lighter, communicative** case. "Talk to [person]" is a message, **not** a meeting — reserve `schedule-meeting` for the heavier, explicitly-framed engagements below.
- Capture the **recipient(s)** and **what to convey** in `--description`. (No `meeting_*` fields.)
- Distinct from "draft X and send to Y" (see the Important note above): that's an `agent` task where Jay sends the artifact afterward. A `send-message` task *is* the communication itself.

### Route to `collab` with `--task-type schedule-meeting` when:

- **Jay needs to schedule a meeting** — the heavier, explicitly-framed case: "I'll set up a sync with Brandon", "let's find a time to meet", "schedule a call with the team", "working session", "demo this for the team". A lighter "talk to / share with / forward to [person]" is a **send-message**, not a meeting.
- Extract: attendee names (agent resolves emails via MCP/calendar search), time preferences ("next week", "Thursday afternoon"), meeting purpose, suggested title
- Use `--meeting-attendees` (comma-separated emails or names as placeholder), `--meeting-duration` (minutes), `--meeting-title`, `--meeting-description`
- **Check the transcript's `participant_emails` frontmatter field first** — it maps participant names to corporate emails (resolved at ingest via Microsoft Graph). Use the email from there when available.
- If the attendee isn't in `participant_emails` (external contact, or mgc wasn't available at ingest), use the person's name as placeholder; the scheduling agent will attempt to resolve or flag for human input

**`--description` vs `--meeting-description` — these are different fields:**

- `--description` is the **task description** (background context for Jay — why this task exists, what was discussed, the origin story). This is internal to PM-OS.
- `--meeting-description` is the **calendar invite body** (what the meeting is *for*, from the attendees' perspective). This text appears in the calendar event that goes to all attendees.

Write `--meeting-description` as a concise, calendar-appropriate sentence describing the meeting's purpose — not how the task was created.

| Bad (task context as invite body) | Good (calendar-appropriate) |
|---|---|
| "At end of catch-up, Zach suggested standardizing a recurring touch base to stay aligned on Pay priorities" | "Recurring sync between Jay and Zach to stay aligned on Pay priorities and surface blockers early" |
| "Jay mentioned wanting to check in with Autumn about CS escalation trends" | "Review CS escalation patterns and discuss product backlog priorities" |
| "" *(empty)* | "Biweekly 1:1 to discuss Home product roadmap and team updates" |

Example:
```bash
./scripts/task.sh add "Schedule recurring Pay sync with Zach" \
  -q collab -p medium -d product \
  --task-type schedule-meeting \
  --meeting-attendees "zach.lastname@vantaca.com" \
  --meeting-duration 30 \
  --meeting-title "Jay x Zach - Pay Sync" \
  --meeting-description "Recurring sync to stay aligned on Pay priorities and surface blockers early" \
  --description "During catch-up on 3/18, Zach suggested standardizing a recurring touch base. Both agreed biweekly 30min would be right cadence." \
  --source-meeting "datasets/meetings/internal/2026-03/..."
```

### Route to `human` ONLY when:

- **Only Jay can physically do it** — have a conversation, send a message to a specific person, show up somewhere, make a phone call
- **Access/permissions requests** — "get access to X system" (Jay has to submit the request himself)
- **Relationship actions** — "connect with person X", "set up 1:1 with Y"

**If you're about to put something in `human` and the output is a document or research, stop — it's `agent` or `collab`.**
**If you're about to put "schedule a meeting" in `human`, stop — it's `collab` with `--task-type schedule-meeting`.**

## When to Use

- Processing new meeting transcripts from `datasets/meetings/`
- User asks to extract action items from a meeting

Do NOT use when:
- Meeting has already been processed (check `_processed-meetings.txt`)
- Creating tasks from non-meeting sources (use `task-create` directly)

## Workflow Steps

### 1. Check Processing History

```bash
grep "filename" datasets/tasks/_processed-meetings.txt
```

If already listed, skip unless explicitly asked to reprocess.

### 2. Load Existing Tasks (Duplicate Detection)

Before extracting any tasks, get the current task list:

```bash
./scripts/task.sh list --json
```

Keep this list in context. For EVERY potential task you identify in steps 3-4, check against this list for semantic duplicates.

**Duplicate = same underlying work**, even if:
- Different wording ("Draft product strategy" vs "Write strategy POV document")
- Different meetings as source
- Different level of detail

**When you find a duplicate:**
- Do NOT create a new task
- Instead, append the new context to the existing task:

```bash
./scripts/task.sh update TASK-NNNN --comment "Additional context from [meeting]: <new details from this meeting>"
```

- **Append-only**: add new information, never remove existing context
- If priority should escalate (e.g., task was medium but meeting revealed urgency), update that too:

```bash
./scripts/task.sh update TASK-NNNN --priority high --comment "Priority escalated: [reason from meeting]"
```

**When it's NOT a duplicate:**
- Different deliverable (strategy doc vs roadmap vs PRD = separate tasks)
- Same topic but genuinely different action (research competitors vs write strategy = separate)
- One is done/archived and new work is needed

### 3. Identify Jay in the Transcript

Jay may appear as "Jay", "Jay Jenkins", or as the meeting organizer. Identify which speaker is Jay so you can distinguish his commitments from others'.

### 4. Scan for Jay-Relevant Action Items Only

For each item that passes the filter, apply the queue logic:

| Situation | Queue | Example |
|-----------|-------|---------|
| Jay needs research, analysis, or a document produced | `agent` | "We need to understand competitor pricing" → agent researches + writes memo |
| Jay needs a decision made, with supporting analysis | `collab` | "We need to decide on API versioning" → agent writes tradeoff doc, Jay decides |
| Jay needs to schedule a meeting | `collab` + `--task-type schedule-meeting` | "I'll set up a sync with Brandon" → agent finds availability, Jay picks a slot |
| Jay must physically do it (message, access, show up) | `human` | "I'll send a Slack message to the team" |
| Jay asked someone for something, or was promised something | `waiting` | "Alyssa will send the VPN setup article" |

### 5. Create Tasks via CLI

```bash
# Agent produces research artifact (note the relevant PM-OS skill)
./scripts/task.sh add "Research Avid vendor payment solution and write competitive analysis" \
  -q agent -p medium -d strategy \
  --description "Discussed in vendor strategy meeting. Need to understand Avid's offering, pricing, and weaknesses. Use research-gathering skill. Output to datasets/research/sources/competitive-analysis/" \
  --source-meeting "2026-02-18_Discuss-Vantaca-Vendor.txt"

# Decision that needs agent prep + Jay's judgment
./scripts/task.sh add "Decide on email authoring tool (Unlayer vs GrapeJS)" \
  -q collab -p high -d product \
  --description "Agent: gather cost data, feature comparison, and write tradeoff analysis using tradeoff-decision workflow. Jay: make final call." \
  --source-meeting "2026-02-25_Email-Authoring-Review.txt"

# Only Jay can do this (physical/relationship action)
./scripts/task.sh add "Schedule recurring sync with Brandon Walker" \
  -q human -p medium -d product \
  --source-meeting "2026-02-26_Jay-x-Brandon-HOAi-Sync.txt"

# Jay is waiting on a deliverable from someone
./scripts/task.sh add "Receive VPN setup article and SUP credentials from Alyssa" \
  -q waiting -p high -d ops \
  --waiting-on "Alyssa Caskey" \
  --source-meeting "2026-02-25_HOAi-Vantaca-Product-Outcomes.txt"
```

**Title format:** Imperative verb + specific object. For agent tasks, include what the output should be.

**Priority:** Based on urgency signals:
- Explicit deadline within 2 days → `critical`
- Explicit deadline this week → `high`
- General follow-up, no urgency → `medium`
- "When you get a chance" → `low`

**Due date:** Only set when explicitly stated in the transcript. Do not fabricate.

### 6. Record Processing

```bash
# Path MUST start with "datasets/meetings/" for dedup to work correctly
echo "datasets/meetings/<domain>/<YYYY-MM>/<filename>" >> datasets/tasks/_processed-meetings.txt
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Extracting everyone's action items | Only extract what Jay owns or is tracking |
| Creating tasks from standup blockers | Skip unless Jay explicitly committed to help |
| Putting research/analysis in `human` queue | If the output is a document or data, it's `agent` |
| Putting decisions in `human` without agent prep | Decisions are `collab` — agent preps, Jay decides |
| Putting "schedule a meeting" in `human` queue | Use `collab` + `--task-type schedule-meeting` — agent finds availability |
| Routing "draft X and send to Y" to `collab` because Jay will review first | End-review is the baseline for every agent task, not a collab signal. Agent drafts, Jay sends. Use `agent`. Only use `collab` when the agent itself must act externally (e.g., post to Jira, book calendar). |
| "Mason will investigate the bug" → task | Not Jay's task. Skip it. |
| Too many waiting tasks for routine team work | Only `waiting` for deliverables Jay specifically needs |
| Agent task without noting relevant PM-OS skill | Include which workflow/skill the agent should use |
| Fabricating due dates not stated in transcript | Leave due blank unless a date was spoken |
| Creating a new task for work that already has an open task | Run `task.sh list --json` first; update existing task with new context instead |
| Losing context by not updating existing task | Always append meeting context to duplicate task via `--comment` |

## Success Criteria

- Every created task passes the filter: Jay owns it or Jay is tracking it
- Zero tasks for other people's work that doesn't involve Jay
- Agent tasks outnumber human tasks for any meeting with substantive discussion
- Agent task descriptions reference the PM-OS skill/workflow to use
- `human` queue contains ONLY things requiring Jay's physical presence or personal action
- `collab` queue used for decisions (agent preps, Jay decides)
- Waiting-queue tasks represent things Jay specifically asked for or was promised
- Source meeting linked on every task
- Meeting recorded in `_processed-meetings.txt`
- Zero duplicate tasks created for work that already has an open task
- Existing tasks enriched with new meeting context when the same topic resurfaces
- It's OK to extract zero tasks from a meeting — many meetings have nothing for Jay
