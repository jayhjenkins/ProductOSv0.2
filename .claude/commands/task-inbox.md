# /task:inbox

## MANDATORY: Use the task-query Skill

**You MUST use the `task-query` skill located at `.claude/skills/task-query/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using task-query to show the human inbox digest"
2. **Read the skill**: Load `.claude/skills/task-query/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Show human inbox digest. Calls `./scripts/task.sh inbox` to display tasks requiring human attention, organized by priority and domain.

## Arguments

None. Filters to the human inbox automatically.

## No Rationalization

You MUST follow the referenced skill exactly. No shortcuts.
