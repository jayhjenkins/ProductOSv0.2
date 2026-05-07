# /project:expand

## MANDATORY: Use the ambition-expander Skill

**You MUST use the `ambition-expander` skill located at `.claude/skills/workflow-ambition-expander/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using ambition-expander to push scope UP and identify opportunities"
2. **Read the skill**: Load `.claude/skills/workflow-ambition-expander/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Review the PRD and actively push scope UP. Identify features, capabilities, and experiences the PM hasn't thought of but that would make the product significantly better. This agent is the antidote to institutional conservatism.

## Prerequisites

- Complete PRD must exist (from `/project:create-prd`)
- Context Brief, Press Releases, Living FAQ, and API Design should exist

## Arguments

- `--review` — Review current PRD and propose additions (default)
- `--variants "topic"` — Generate alternative approaches for a specific capability
- `--competitive` — Focus on competitive leapfrog opportunities
- `--delight` — Focus on delight features

## Output

Written to the initiative's package folder: `datasets/product/packages/{YYYY}/{slug}/`

- `{package}/expansion-proposals.md` — Proposed additions with evidence, effort sizing, and PM decision log

## Philosophy

Don't cut scope. Expand ambition. Code is cheap — ambiguity and timidity are expensive. The PM decides what's in; the expander's job is to make sure nothing great was left on the table.
