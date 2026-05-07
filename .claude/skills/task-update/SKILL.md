---
name: task-update
description: Use when modifying existing task state, status, priority, queue, or adding comments to activity log
---

# Task Update

## Purpose

Modify existing tasks in the PM-OS system: change status, move between queues, adjust priority, and append activity log comments. All changes are tracked in the task's activity log for auditability.

## When to Use

Activate when:
- Changing task status (open, in-progress, blocked, etc.)
- Moving a task to a different queue
- Adjusting priority based on new information
- Adding a comment or progress note
- Agent needs to communicate status back to human

Do NOT use when:
- Creating a new task (use `task-create`)
- Marking a task fully complete with archival (use `task-complete`)
- Querying task state without changes (use `task-query`)

## Workflow Steps

### 1. Identify the Task

Use the task ID (e.g., `TASK-0042`). If unsure, query first:
```bash
./scripts/task.sh list --queue human --status open
```

### 2. Apply Changes via CLI

```bash
./scripts/task.sh update TASK-NNNN \
  --status in-progress \
  --priority high \
  --queue collab \
  --comment "Starting work, need human input on scope" \
  --actor human
```

### 3. Status Transitions

Valid status values: `open`, `in-progress`, `blocked`, `done`, `cancelled`

| From | Allowed To | Notes |
|------|-----------|-------|
| `open` | `in-progress`, `cancelled` | Normal start or cancellation |
| `in-progress` | `blocked`, `done`, `cancelled` | Work proceeds or hits a wall |
| `blocked` | `in-progress`, `cancelled` | Blocker resolved or task abandoned |
| `done` | (terminal) | Use `task-complete` for archival |
| `cancelled` | (terminal) | Cancelled tasks stay cancelled |

### 4. Queue Movement Rules

| From | To | When |
|------|-----|------|
| `human` | `agent` | Human decides agent can handle it autonomously |
| `human` | `collab` | Human wants to work on it together with agent |
| `human` | `waiting` | Human delegates externally |
| `agent` | `collab` | Agent needs human input (use `agent:ask`) |
| `agent` | `human` | Agent cannot proceed, needs human takeover |
| `collab` | `agent` | Human answers question, agent resumes |
| `collab` | `human` | Needs full human ownership |
| `waiting` | `human` | External deliverable received, human acts next |
| `waiting` | `agent` | External deliverable received, agent processes it |

### 5. Adding Comments

Comments append to the activity log with timestamp and actor:
```bash
./scripts/task.sh update TASK-0042 --comment "Completed first draft, waiting on review" --actor human
```

Agent comments use `--actor agent`. Always include meaningful context, not just "updated".

### 6. Agent-Specific Fields

When updating agent-managed tasks, you can also set:
- `--agent-status`: one of `queued`, `running`, `blocked`, `needs-human`, `complete`, `failed`
- `--agent-output`: path to output artifact
- `--agent-error`: error message on failure

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Changing status without a comment | Always explain why the status changed |
| Skipping `blocked` and going straight to `cancelled` | Mark blocked first; cancellation is permanent |
| Moving to `waiting` without setting `--waiting-on` | Always specify who you are waiting on |
| Empty comments like "updated" | Be specific: what changed and why |
| Agent updating without `--actor agent` | Always set actor correctly for audit trail |

## Success Criteria

- Task fields updated and confirmed by CLI output
- Activity log contains timestamped comment explaining the change
- Queue movement follows allowed transition rules
- Status transition is valid (no skipping terminal states)
- Actor correctly attributed (human or agent)
