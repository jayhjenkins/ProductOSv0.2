# /recruiting:process-interview

## MANDATORY: Use the recruiting-process-interview Skill

**You MUST use the `recruiting-process-interview` skill located at `.claude/skills/recruiting-process-interview/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using recruiting-process-interview to process this PM interview"
2. **Read the skill**: Load `.claude/skills/recruiting-process-interview/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Transform a completed PM interview into a structured, scored assessment and update the candidate stack rank.

## What the Skill Does

- Self-scaffolds `datasets/recruiting/` structure if needed
- Prompts for opening and candidate selection
- Reads job description, resume, and interview transcript
- Applies the `hiring-assess-pm-candidate` framework (4 dimensions, scored 1-5)
- Generates and saves an assessment file
- Updates `stackrank.md` with the candidate's scores and rank position

## No Rationalization

Follow the skill exactly.
