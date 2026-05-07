# /recruiting:process-interview

## MANDATORY: Use the process-interview Skill

**You MUST use the `process-interview` skill located at `.claude/skills/recruiting-process-interview/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using process-interview to generate a PM candidate assessment"
2. **Read the skill**: Load `.claude/skills/recruiting-process-interview/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Read job description, resume, and interview transcript; invoke the assess-pm-candidate framework; generate a complete scored assessment; save it to the candidate folder; and update the opening's stackrank.

## Execution

The skill orchestrates:
1. Ask user to select job opening
2. Ask user to select candidate
3. Read job-description.md, resume.md, and interview-transcript.md
4. Invoke assess-pm-candidate skill — apply full 4-dimension framework
5. Generate complete assessment draft using pm-assessment-template.md
6. Display to user, incorporate any adjustments
7. Save as {YYYY-MM-DD}-assessment.md in candidate folder
8. Display current stackrank and ask for candidate's rank
9. Update stackrank.md with new candidate row and last_updated date
