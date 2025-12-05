# /launch-announcement

## MANDATORY: Use the launch-announcement Skill

**You MUST use the `launch-announcement` skill located at `.claude/skills/workflows/launch-announcement/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using launch-announcement to create an internal product launch announcement"
2. **Read the skill**: Load `.claude/skills/workflows/launch-announcement/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Create customer-centric internal launch announcements for shipped features. Communicate feature releases to cross-functional internal teams (product, eng, design, data, sales, CS, marketing, leadership).

## Workflow Overview

The skill guides through 5 phases:
1. Research existing documentation (PRDs, roadmap, meetings)
2. Gather missing information from user
3. Structure announcement following 10-section template
4. Write announcement file to disk
5. Confirm accuracy with user

## Key Behaviors

- **Research-First**: Search PRDs and documentation before asking user
- **No Fabrication**: Never make up metrics, names, or success stories
- **Validation Required**: Always confirm shipped features match documentation
- **Customer-Centric**: Focus on customer pain and value, not just tech
- **File-First**: Write to `datasets/product/launch-announcements/{YYYY}/`

## Required Template Structure

1. Launch Title (with emojis)
2. Context & Overview
3. Customer Problem (persona statement)
4. What Was Launched?
5. From → To (value shift)
6. How Will We Define Success?
7. What's Next?
8. Early Success Story (optional)
9. Shout Outs & HUGE THANKS
10. Resources (optional)

## Critical Rules

- **Always confirm what actually shipped** - PRDs may not match reality
- **Never fabricate metrics** - Ask user for baseline/target values
- **Only include real links** - No placeholder URLs
- **Validate success stories** - Only include if user provides specific story

## Output Location

`datasets/product/launch-announcements/{YYYY}/launch-{feature-slug}.md`

