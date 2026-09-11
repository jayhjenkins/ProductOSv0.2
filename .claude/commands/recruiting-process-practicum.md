# /recruiting:process-practicum

## MANDATORY: Use the recruiting-process-practicum Skill

**You MUST use the `recruiting-process-practicum` skill located at `.claude/skills/recruiting-process-practicum/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using recruiting-process-practicum to process this PM practicum"
2. **Read the skill**: Load `.claude/skills/recruiting-process-practicum/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Transform a completed PM product practicum into a scored craft assessment and update the candidate stack rank.

## What the Skill Does

- Self-scaffolds `datasets/recruiting/` structure if needed
- Prompts for opening and candidate selection
- Reads the practicum prompt and candidate's practicum transcript
- Applies the `hiring-assess-pm-practicum` framework (5 craft dimensions scored against a level matrix)
- Generates and saves a practicum assessment file
- Updates `stackrank.md` notes and rank position

## No Rationalization

Follow the skill exactly.
