# /task:list

## MANDATORY: Use the task-query Skill

**You MUST use the `task-query` skill located at `.claude/skills/task-query/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using task-query to show current tasks"
2. **Read the skill**: Load `.claude/skills/task-query/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Show current tasks. Calls `./scripts/task.sh list` with smart defaults (active tasks, sorted by priority).

## Arguments

None. Uses smart defaults to display the current task list.

## No Rationalization

You MUST follow the referenced skill exactly. No shortcuts.
