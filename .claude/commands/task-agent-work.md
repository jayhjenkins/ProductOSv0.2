# /task:agent-work

## MANDATORY: Use the task-communicate Skill

**You MUST use the `task-communicate` skill located at `.claude/skills/task-communicate/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using task-communicate to pick up and begin work on the next queued task"
2. **Read the skill**: Load `.claude/skills/task-communicate/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Agent picks up the next task from its queue and begins work. For interactive sessions where the agent needs to select and execute a queued task. The agent will claim the highest-priority available task, transition it to in-progress, and begin execution.

## Arguments

None. The agent automatically selects the next available task from its queue.

## No Rationalization

You MUST follow the referenced skill exactly. No shortcuts.
