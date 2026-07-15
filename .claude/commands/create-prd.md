# /project:create-prd

## MANDATORY: Use the prd-creation Skill

**You MUST use the `prd-creation` skill located at `.claude/skills/workflow-prd-creation/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using prd-creation to create a Product Requirements Document"
2. **Read the skill**: Load `.claude/skills/workflow-prd-creation/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Create individual PRD through interactive session with structured information gathering. When upstream Shipping Greatness artifacts exist (context brief, press releases, living FAQ, API design), the skill automatically ingests them to pre-populate sections.

## Guiding Principles

- PRD is a living document - will evolve through collaboration and discovery
- Ambitious by default - set the ceiling high, build the fully-featured version
- Sequence, don't cut - P0/P1/P2 = Foundation/Expansion/Polish phases, all ship
- No fabrication - leave sections blank/TBD rather than making up information
- Share and link - PRDs should be accessible with links to relevant resources

## Interactive Session

The skill guides through 9 phases:
1. Core Identity (name, description, background)
2. Objectives (customer statement, success metrics)
3. Scope & Non-Goals (use cases in/out, agent/API scenarios, non-goals)
4. Requirements (by milestone with priorities as build sequence)
4b. Build Sequence (Foundation → Expansion → Polish)
5. Timeline (milestones and delivery dates)
6. Links and Resources
7. Metrics and Learning Agenda
8. Open Questions / Tracked Assumptions (from Living FAQ)
9. Appendix / Upstream Artifact Links

## Upstream Artifact Ingestion

When invoked as part of `/project:build` or `/project:ship-it`, the skill automatically checks for and imports:
- Context Brief → Background, Objectives
- Press Releases → Vision, customer outcome, stakeholder impact
- One-Pager → Differentiators, success metrics, timeline
- Living FAQ → Open Questions (imports unanswered important/tracked items)
- API Design → Agent/API Scenarios section
- Agent Scenarios → Agent/API Scenarios section

## No Fabrication

If information is not provided, leave it blank or marked "TBD". PRDs are living documents - incomplete sections can be filled in later.

## Validation

PRD must pass 5-point validation before becoming Actionable:
1. Objectives Clear
2. Use Cases Defined
3. Requirements Structured
4. Timeline Present
5. Success Measurable

## Arguments

- `--generate` — Full PRD generation from all artifacts
- `--section "name"` — Regenerate a specific section
- `--update` — Re-run synthesis with updated inputs
- `--export` — Produce final formatted version
