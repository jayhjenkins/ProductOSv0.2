# /task:done

## MANDATORY: Use the task-complete Skill

**You MUST use the `task-complete` skill located at `.claude/skills/task-complete/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using task-complete to mark a task as done"
2. **Read the skill**: Load `.claude/skills/task-complete/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Mark a task as complete. Takes a task ID argument and calls `./scripts/task.sh done` to update the task status.

## Arguments

- `$ARGUMENTS` -- task ID (e.g., TASK-0001)

If no task ID is provided, prompt the user for one.

## No Rationalization

You MUST follow the referenced skill exactly. No shortcuts.
