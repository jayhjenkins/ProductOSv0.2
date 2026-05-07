# /project:swag

## MANDATORY: Use the swag-modeler Skill

**You MUST use the `swag-modeler` skill located at `.claude/skills/workflow-swag-modeler/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using swag-modeler to build the business case"
2. **Read the skill**: Load `.claude/skills/workflow-swag-modeler/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Build a simple, transparent financial model that validates the business opportunity. The model's primary purpose is to expose assumptions, not to produce precise forecasts.

## Prerequisites

- Complete PRD must exist
- Context Brief should exist
- Red Team Report should exist (optional but recommended)

## Arguments

- `--generate` — Build full model from PRD and context (default)
- `--sensitivity` — Run sensitivity analysis on existing model
- `--scenario "pessimistic"` — Generate a specific scenario
- `--adjust "assumption=value"` — Modify a specific assumption and re-run

## Output

Written to the initiative's package folder: `datasets/product/packages/{YYYY}/{slug}/`

- `{package}/business-case-swag.md` — Financial model with labeled assumptions, market sizing, revenue/cost models, sensitivity analysis, and executive summary

## Principle

Understandable by a non-financial PM in 5 minutes. Every assumption labeled. Sensitivity shown. The value is making hidden assumptions visible, not false precision.
