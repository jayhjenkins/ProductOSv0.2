# /task:add

## MANDATORY: Use the task-create Skill

**You MUST use the `task-create` skill located at `.claude/skills/task-create/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using task-create to interactively create a new task"
2. **Read the skill**: Load `.claude/skills/task-create/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Interactive task creation. Prompts for title, queue, priority, and domain. Creates the task file via `./scripts/task.sh add`.

## Arguments

None. The skill will interactively prompt for all required fields:
- Title
- Queue (e.g., human, agent)
- Priority (e.g., P0, P1, P2, P3)
- Domain (e.g., engineering, product, design, marketing)

## No Rationalization

You MUST follow the referenced skill exactly. No shortcuts.
