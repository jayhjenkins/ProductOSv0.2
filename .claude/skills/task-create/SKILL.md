---
name: task-create
description: Use when creating new tasks from any context - guides correct queue assignment, priority, and field population via CLI
---

# Task Create

## Purpose

Create well-formed tasks in the PM-OS task system with correct queue placement, priority assignment, and complete field population. Every task must land in the right queue from the start to avoid unnecessary triage overhead.

## When to Use

Activate when:
- User asks to create a new task, action item, or to-do
- Extracting tasks from meetings (use with `task-extract-from-meeting`)
- Agent identifies follow-up work during any workflow
- User invokes `/task:add` or similar

Do NOT use when:
- Updating an existing task (use `task-update`)
- Querying or filtering tasks (use `task-query`)
- Completing a task (use `task-complete`)

## Workflow Steps

### 1. Determine Queue

Select exactly one queue based on who owns the next action:

| Queue | Use When | Examples |
|-------|----------|---------|
| `human` | Requires the operator's physical presence or personal action that cannot be delegated to an agent at all | Send a personal Slack message, attend an event, make a phone call, submit an access request |
| `agent` | Fully autonomous; agent can complete without asking | Summarize transcript, generate report, sync data |
| `collab` | Agent takes action on external systems, but human must approve before execution | Calendar management (scheduling meetings), sending emails/comms, updating Jira/HubSpot/other systems |
| `waiting` | Delegated to someone outside the system | Waiting on legal review, design mockups from another team |

**Rule of thumb:** If the agent could do it alone with no ambiguity, it is `agent`. If a human must decide or approve, it is `human`. If blocked on an external party, it is `waiting`. If the agent acts on an external system but needs human approval first, it is `collab`.

**"Talk to someone" ≠ `human`:** When the operator needs to connect with someone, the first step is almost always scheduling a meeting — and that's `collab` with `--task-type schedule-meeting`. The agent finds availability, drafts the invite, and the operator approves. Only use `human` when the action is truly unschedulable (e.g., an impromptu hallway conversation, a quick Slack DM).

Example: "Talk to Greg about voting requirements" → `collab` + `--task-type schedule-meeting` (agent schedules a meeting with Greg, the operator approves the invite).

> **Note:** The `collab` queue is currently dormant — no dispatcher support yet. Tasks should be queued here for future supervised-action capability.

### 2. Set Priority

| Priority | Criteria |
|----------|----------|
| `critical` | Blocking other work or has an imminent deadline (today/tomorrow) |
| `high` | Due this week or significant business impact |
| `medium` | Standard work, due within 1-2 weeks |
| `low` | Nice-to-have, no deadline pressure |

### 3. Populate Fields

**Required fields:** title, queue, priority

**Recommended fields:** domain, description

**Optional fields:** due, tags, creator, source-meeting, project, waiting-on, waiting-expected

### 4. Create via CLI

```bash
./scripts/task.sh add "Title here" \
  -q <queue> \
  -p <priority> \
  -d <domain> \
  --description "What needs to happen and why" \
  --due "YYYY-MM-DD" \
  --tags "tag1,tag2" \
  --project "project-name"
```

For waiting queue tasks, also include:
```bash
  --waiting-on "Design team" \
  --waiting-expected "2026-03-15"
```

### 5. Validate

- Title: max 200 characters, imperative verb form ("Review X", "Draft Y", "Ship Z")
- Queue: one of `human`, `agent`, `collab`, `waiting`
- Priority: one of `critical`, `high`, `medium`, `low`
- Domain: one of `product`, `strategy`, `marketing`, `recruiting`, `metrics`, `learning`, `ops`
- Status: automatically set to `open` on creation

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Putting agent-decidable work in `human` queue | If there is no ambiguity and no approval needed, use `agent` |
| Putting "talk to someone" or "connect with someone" in `human` queue | These require scheduling a meeting first — use `collab` + `--task-type schedule-meeting` |
| Missing description on complex tasks | Always add `--description` for non-obvious tasks |
| Vague titles like "Follow up" | Use imperative + specific object: "Follow up with Legal on DPA review" |
| Forgetting `--waiting-on` for waiting queue | Every `waiting` task must specify who you are waiting on |
| Setting everything to `critical` | Reserve critical for genuine blockers; most work is `medium` |

## Success Criteria

- Task created with valid ID (TASK-NNNN format)
- Correct queue selected based on ownership rules
- Priority reflects actual urgency and impact
- Title is clear, actionable, and under 200 characters
- Waiting queue tasks have `waiting-on` populated
- CLI confirms creation with task ID and file path
