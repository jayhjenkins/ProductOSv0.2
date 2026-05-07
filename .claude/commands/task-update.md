# /task:update

## MANDATORY: Use the task-update Skill

**You MUST use the `task-update` skill located at `.claude/skills/task-update/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using task-update to interactively update a task"
2. **Read the skill**: Load `.claude/skills/task-update/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Interactive task update. Shows the current state of the specified task, then prompts for changes (status, priority, queue, domain, notes, etc.).

## Arguments

- `$ARGUMENTS` -- task ID (e.g., TASK-0001)

If no task ID is provided, prompt the user for one.

## No Rationalization

You MUST follow the referenced skill exactly. No shortcuts.
