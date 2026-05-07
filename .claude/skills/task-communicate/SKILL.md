---
name: task-communicate
description: Use when agents need to communicate status, questions, or results back through the task system
---

# Task Communicate

## Purpose

Define the protocol for agent-to-human communication through the task system. Agents must use structured communication patterns so that humans can efficiently triage, respond, and maintain flow without context-switching overhead.

## When to Use

Activate when:
- Agent needs to report progress on a task
- Agent encounters a blocker and needs human input
- Agent has completed work and is delivering output
- Agent hits an error and cannot proceed
- Agent needs to hand off a task to human ownership

Do NOT use when:
- Human is updating their own tasks (use `task-update`)
- Creating a new task from scratch (use `task-create`)
- No communication is needed (agent working silently is fine)

## Workflow Steps

### 1. Communication Types

| Type | When | CLI Command |
|------|------|-------------|
| **Start** | Agent begins work on a task | `./scripts/task.sh agent:start TASK-NNNN` |
| **Complete** | Agent finished, delivering output | `./scripts/task.sh agent:complete TASK-NNNN --output "path"` |
| **Fail** | Agent cannot complete, error occurred | `./scripts/task.sh agent:fail TASK-NNNN --error "reason"` |
| **Ask** | Agent needs human answer to proceed | `./scripts/task.sh agent:ask TASK-NNNN "question"` |
| **Status update** | Progress note, no state change | `./scripts/task.sh update TASK-NNNN --comment "note" --actor agent` |

### 2. Agent Start Protocol

When an agent picks up a task:
```bash
./scripts/task.sh agent:start TASK-0042
```

This sets:
- `status: in-progress`
- `agent_status: running`
- `agent_started: <timestamp>`
- Activity log entry: "Agent starting work on this task."

### 3. Agent Question Protocol (Critical Path)

When an agent is blocked and needs human input:

```bash
./scripts/task.sh agent:ask TASK-0042 "Should we include historical data before 2024 in the retention analysis?"
```

This triggers a specific sequence:
1. Appends `[question]` entry to the activity log
2. Sets `agent_status: needs-human`
3. Sets `status: blocked`
4. If task was in `agent` queue, moves it to `collab` (supervised) queue

The human sees this in their `inbox` under "AGENT QUESTIONS (need your answer)".

**After the human answers**, they should:
```bash
./scripts/task.sh update TASK-0042 --comment "Yes, include all data back to 2022" --queue agent --status in-progress --actor human
```

This moves the task back to `agent` queue for the agent to resume.

### 4. Agent Complete Protocol

When the agent finishes work:
```bash
./scripts/task.sh agent:complete TASK-0042 --output "datasets/product/agent-output/retention-analysis.md"
```

**Output location:** Save agent work products to `datasets/product/agent-output/` by default. This folder is synced to Word/SharePoint, so the "Open in Word" link will appear on the task card automatically. Use domain-specific folders (e.g., `datasets/recruiting/...`) only when the output clearly belongs there.

This sets:
- `agent_status: complete`
- `agent_completed: <timestamp>`
- `agent_output: <path>`
- `sharepoint_path: <computed Word/OneDrive path>` (if output is in a synced folder)
- Archives the task to `_archive/YYYY-MM/`

The human sees completed tasks in `inbox` under "COMPLETED BY AGENT (need your review)".

### 5. Agent Fail Protocol

When the agent encounters an unrecoverable error:
```bash
./scripts/task.sh agent:fail TASK-0042 --error "Meeting transcript file not found at expected path"
```

This sets:
- `agent_status: failed`
- `agent_error: <message>`
- Activity log entry with error detail

The task remains in its current queue for human triage.

### 6. Status Update (No State Change)

For progress notes that do not change task state:
```bash
./scripts/task.sh update TASK-0042 --comment "Processed 3 of 5 transcripts so far" --actor agent
```

Use sparingly. Only add status updates for long-running tasks where the human benefits from knowing progress.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Agent silently failing without reporting | Always use `agent:fail` with a clear error message |
| Asking vague questions | Be specific: include what you tried, what you need, and options if possible |
| Forgetting `--output` on completion | If work produced a file, always link it |
| Over-communicating status updates | Only add progress notes on long-running tasks; skip for fast tasks |
| Not moving task back after human answers | Human must `--queue agent --status in-progress` to resume agent work |
| Agent using `update` instead of `agent:ask` | Use `agent:ask` for questions; it handles queue movement automatically |

## Success Criteria

- Agent uses the correct CLI alias for each communication type
- Questions are specific and actionable (human can respond in one message)
- Completed tasks link their output artifact
- Failed tasks include a clear error message explaining what went wrong
- Task moves to `collab` (supervised) queue when agent asks a question
- Human inbox surfaces all items needing attention
- Communication overhead is minimal (no noise, only signal)
