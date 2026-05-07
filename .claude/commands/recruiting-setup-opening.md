# /recruiting:setup-opening

## MANDATORY: Use the setup-new-opening Skill

**You MUST use the `setup-new-opening` skill located at `.claude/skills/recruiting-setup-new-opening/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using setup-new-opening to scaffold a new PM job opening"
2. **Read the skill**: Load `.claude/skills/recruiting-setup-new-opening/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Create the folder structure, blank job description, and seeded stackrank for a new PM hiring opening.

## Execution

The skill orchestrates:
1. Ask for job title
2. Generate slug and dated folder name
3. Create opening folder and candidates/ subfolder
4. Create blank job-description.md with frontmatter stub
5. Seed stackrank.md from template
6. Report paths and instruct user to paste JD
