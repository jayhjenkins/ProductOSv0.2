# /project:press-release

## MANDATORY: Use the vision-clarifier Skill

**You MUST use the `vision-clarifier` skill located at `.claude/skills/workflow-vision-clarifier/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using vision-clarifier to produce press releases and one-pager"
2. **Read the skill**: Load `.claude/skills/workflow-vision-clarifier/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Articulate the product vision through dual press releases (external customer-facing, internal team-facing with persona sections) and a condensed one-pager.

## Prerequisites

- A Context Brief should exist (from `/discover` or manual input)
- The PM must have a rough vision, problem statement, or feature idea

## Arguments

- `--external` — Generate external press release only
- `--internal` — Generate internal press release only
- `--both` — Generate both press releases and the one-pager (default)
- `--refine` — Iterate on existing drafts with new input

## Output

All artifacts are written to the initiative's package folder: `datasets/product/packages/{YYYY}/{slug}/`

- `{package}/press-release-external.md` — Customer-facing press release
- `{package}/press-release-internal.md` — Team-facing press release with Sales, PMM, PS, CSM sections
- `{package}/one-pager.md` — 10-minute pitch summary

If the package folder doesn't exist yet, create it (derive slug from the product/feature name).

## Gate

Both press releases must exist and be reviewed by the PM. The one-pager must be producible from the press release content — if it can't be condensed into a 10-minute pitch, the vision isn't clear enough.
