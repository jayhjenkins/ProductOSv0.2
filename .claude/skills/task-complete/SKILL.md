---
name: task-complete
description: Use when finishing tasks and recording completion with output artifacts
---

# Task Complete

## Purpose

Properly close out tasks in the PM-OS system by marking them done, linking output artifacts, and archiving to the monthly archive. Ensures no completed work is lost and all outputs are traceable.

## When to Use

Activate when:
- Human finishes a task and wants to mark it done
- Agent has completed assigned work and produced output
- A task is no longer needed and should be cancelled
- Reviewing agent-completed tasks from the inbox

Do NOT use when:
- Task is still in progress (use `task-update` to add progress notes)
- Task is blocked and needs help (use `task-update` to set `blocked`)
- Creating new tasks (use `task-create`)

## Workflow Steps

### 1. Human Completion Flow

```bash
# Mark done and archive
./scripts/task.sh done TASK-0042

# Mark done with output artifact
./scripts/task.sh done TASK-0042 --output "datasets/product/prds/2026/PRD_feature-x.md"
```

This does three things:
1. Sets status to `done`
2. Records the output artifact path (if provided)
3. Moves the task file to `_archive/YYYY-MM/`

### 2. Agent Completion Flow

Agents use the dedicated alias which also records agent-specific metadata:

```bash
# Agent marks work complete
./scripts/task.sh agent:complete TASK-0042 --output "datasets/product/reports/analysis.md"
```

This does:
1. Sets `agent_status: complete` with timestamp
2. Records `agent_output` path
3. Sets status to `done`
4. Archives the task file

### 3. Cancellation

For tasks that are no longer relevant:

```bash
./scripts/task.sh update TASK-0042 --status cancelled --comment "Superseded by TASK-0055"
```

Cancelled tasks remain in their queue directory (not archived). Always add a comment explaining why.

### 4. Archive Structure

Completed tasks are moved to:
```
datasets/tasks/_archive/YYYY-MM/TASK-NNNN.md
```

The archive is organized by completion month. This keeps active queue directories clean while preserving full history.

### 5. Reviewing Agent Completions

When `inbox` shows agent-completed tasks:

1. Run `./scripts/task.sh show TASK-NNNN` to see what the agent produced
2. Check the `agent_output` field for the artifact path
3. Review the artifact
4. If acceptable, the task is already archived -- no further action needed
5. If revisions needed, create a new follow-up task with `task-create`

### 6. Output Artifacts

Always link meaningful outputs when completing tasks:
- PRDs, reports, memos, strategies
- Data files, processed datasets
- Any file generated as a result of the task

The `--output` flag records the path in the task frontmatter for traceability.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Completing without linking output | If the task produced a file, always use `--output` |
| Agent using `done` instead of `agent:complete` | Agents must use `agent:complete` for proper metadata |
| Not reviewing agent completions | Check `inbox` regularly; agent work needs human verification |
| Deleting cancelled tasks | Use `--status cancelled` with a comment; never delete task files |
| Completing a blocked task | Resolve the blocker first, then complete |

## Success Criteria

- Task status set to `done` (or `cancelled` with explanation)
- Output artifact path recorded when applicable
- Task file archived to `_archive/YYYY-MM/` directory
- Agent completions include `agent_status: complete` and timestamp
- Activity log documents the completion with actor attribution
- Human has reviewed agent-completed work before considering it final
