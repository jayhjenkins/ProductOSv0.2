# /task:process-meetings

## MANDATORY: Use the task-extract-from-meeting Skill

**You MUST use the `task-extract-from-meeting` skill located at `.claude/skills/task-extract-from-meeting/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using task-extract-from-meeting to extract tasks from unprocessed meeting transcripts"
2. **Read the skill**: Load `.claude/skills/task-extract-from-meeting/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Run meeting-to-task extraction on unprocessed transcripts. Calls `./scripts/task-extract-meetings.sh --all-unprocessed` to scan meeting files, extract action items, and create task entries automatically.

## Arguments

None. Processes all unprocessed transcripts by default.

## No Rationalization

You MUST follow the referenced skill exactly. No shortcuts.
