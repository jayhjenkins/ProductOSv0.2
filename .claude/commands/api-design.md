# /project:api-design

## MANDATORY: Use the agentic-api-designer Skill

**You MUST use the `agentic-api-designer` skill located at `.claude/skills/workflows/agentic-api-designer/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using agentic-api-designer to design agent-first API interfaces"
2. **Read the skill**: Load `.claude/skills/workflows/agentic-api-designer/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Design API interfaces with agents as the primary consumer. Stripe-level quality, optimized for machine callers — AI agents that need to discover, understand, and execute every capability without touching a UI.

## Prerequisites

- Context Brief must exist
- Press Releases should exist
- Living FAQ should exist (from `/devils-advocate`)

## Arguments

- `--generate` — Full API design from current artifacts (default)
- `--resources` — Generate just the resource model
- `--scenarios` — Generate agent workflow scenarios only
- `--review` — Critique existing API design for agent-friendliness

## Output

Written to the initiative's package folder: `datasets/product/packages/{YYYY}/{slug}/`

- `{package}/agentic-api-design.md` — Full API design document
- `{package}/api-agent-scenarios.md` — End-to-end agent workflow examples

## Design Principle

If a human can do it in the UI, an agent must be able to do it via API. No UI-only capabilities.
