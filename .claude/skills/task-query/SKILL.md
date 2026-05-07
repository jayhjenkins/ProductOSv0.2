---
name: task-query
description: Use when searching, filtering, or reviewing task state across queues for planning or status reporting
---

# Task Query

## Purpose

Search, filter, and review tasks across the PM-OS task system. Supports human planning sessions, agent pre-work checks, status reporting, and inbox triage.

## When to Use

Activate when:
- User asks "What's on my plate?" or "Show me my tasks"
- Agent needs to check existing tasks before creating duplicates
- Planning session requires current state of all queues
- Status report or standup preparation
- Checking what is blocked or overdue

Do NOT use when:
- Creating or modifying tasks (use `task-create` or `task-update`)
- Completing tasks (use `task-complete`)

## Workflow Steps

### 1. Choose the Right Command

| Goal | Command |
|------|---------|
| See all tasks | `./scripts/task.sh list` |
| Filter by queue | `./scripts/task.sh list --queue agent` |
| Filter by status | `./scripts/task.sh list --status blocked` |
| Filter by domain | `./scripts/task.sh list --domain product` |
| Filter by priority | `./scripts/task.sh list --priority critical` |
| Combine filters | `./scripts/task.sh list --queue human --status open --priority high` |
| Full detail on one task | `./scripts/task.sh show TASK-0042` |
| Human inbox digest | `./scripts/task.sh inbox` |
| JSON output for scripts | `./scripts/task.sh list --json` |

### 2. Inbox for Human Triage

The `inbox` command provides a structured digest grouped by urgency:

```bash
./scripts/task.sh inbox
```

Sections displayed:
1. **Agent questions** -- tasks where the agent is blocked and needs a human answer
2. **Completed by agent** -- agent finished work, needs human review
3. **Your open tasks** -- human-queue tasks sorted by priority
4. **Waiting on others** -- external dependencies with overdue flags
5. **Summary** -- counts by queue

Start every planning session with `inbox`.

### 3. Full Task Detail

```bash
./scripts/task.sh show TASK-0042
```

Returns YAML frontmatter (all fields) plus the full markdown body including description and activity log.

### 4. JSON Output for Programmatic Use

```bash
./scripts/task.sh list --queue agent --status open --json
```

Returns a JSON array of task objects. Useful for:
- Feeding into other scripts or workflows
- Building reports or dashboards
- Agent pre-checks before creating tasks

### 5. Common Query Patterns

| Scenario | Command |
|----------|---------|
| Morning triage | `./scripts/task.sh inbox` |
| What can the agent work on? | `./scripts/task.sh list --queue agent --status open` |
| What is blocked? | `./scripts/task.sh list --status blocked` |
| All critical tasks | `./scripts/task.sh list --priority critical` |
| Product domain tasks | `./scripts/task.sh list --domain product` |
| Overdue waiting tasks | `./scripts/task.sh inbox` (shows OVERDUE flags) |
| Check before creating | `./scripts/task.sh list --json` and search for similar titles |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Creating a task without checking for duplicates | Always `list --json` and search first |
| Ignoring the inbox command | `inbox` is the best single command for human triage |
| Using `list` when you need full detail | Use `show TASK-NNNN` for activity log and description |
| Forgetting `--json` for scripted use | Table output is for humans; always use `--json` in automations |
| Filtering only one dimension | Combine filters: `--queue human --status open --priority high` |

## Success Criteria

- Query returns relevant tasks matching the filter criteria
- No duplicate tasks created due to skipped pre-check
- Human triage starts with `inbox` command
- JSON output used for any programmatic or agent-driven queries
- Full task detail retrieved before making update decisions
