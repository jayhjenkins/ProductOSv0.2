# /project:devils-advocate

## MANDATORY: Use the devils-advocate Skill

**You MUST use the `devils-advocate` skill located at `.claude/skills/workflows/devils-advocate/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using devils-advocate to stress-test the product vision"
2. **Read the skill**: Load `.claude/skills/workflows/devils-advocate/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Adopt adversarial perspectives to interrogate the product vision. Generate the Living FAQ — a continuously updating document capturing objections, edge cases, and hard questions.

## Prerequisites

- Context Brief must exist
- Press Releases (external + internal) should exist
- One-Pager should exist

## Arguments

- `--full` — Run all perspectives (default)
- `--persona "name"` — Run a single perspective (e.g., "skeptical engineer", "compliance officer")
- `--update` — Re-run against updated artifacts
- `--unanswered` — Surface all questions still marked UNANSWERED

## Output

Written to the initiative's package folder: `datasets/product/packages/{YYYY}/{slug}/`

- `{package}/living-faq.md` — Prioritized FAQ organized by topic with perspective tags

## Living Document

The FAQ is updated throughout the workflow, not just in this phase. Any agent can add questions. Only the PM can mark answers as final.
