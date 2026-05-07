# /recruiting:prep-interview

## MANDATORY: Use the prep-interview Skill

**You MUST use the `prep-interview` skill located at `.claude/skills/recruiting-prep-interview/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using prep-interview to set up a candidate folder for an upcoming interview"
2. **Read the skill**: Load `.claude/skills/recruiting-prep-interview/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Create the candidate folder, blank resume, and blank interview transcript for a new candidate inside an existing job opening.

## Execution

The skill orchestrates:
1. List existing job openings and ask user to select
2. Ask for candidate's full name
3. Generate candidate slug
4. Create candidates/{slug}/ folder
5. Create blank resume.md and interview-transcript.md with frontmatter stubs
6. Report paths and instruct user to paste resume and transcript
