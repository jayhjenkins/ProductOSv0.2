# /project:meetings-to-backlog

## MANDATORY: Use the product-planning Skill

**You MUST use the `product-planning` skill located at `.claude/skills/workflows/product-planning/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using product-planning to transform meeting signals into PRD proposals"
2. **Read the skill**: Load `.claude/skills/workflows/product-planning/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Synthesize meeting signals into validated PRD proposals.

## Arguments

- `days`: Lookback window (default: from last_run or 3 days)
- `include_customers`: Filter to specific customers
- `include_internal_functions`: Filter to specific functions
- `min_mentions`, `min_sources`: Signal thresholds
- `max_prds`: Cap on proposals
- `exclude_types`: Skip signal types (default: "bugs,housekeeping")
- `dry_run`: Preview without writing files

## Execution

The skill orchestrates:
1. Invoke `meeting-synthesis` to extract signals
2. Cluster signals into PRD themes
3. Draft PRDs using template
4. Invoke `prd-validation` for each proposal
5. Write to backlog.md and individual PRD files
6. Update state tracking

## No Fabrication

PRDs are created from meeting evidence only. Unknown sections are marked TBD - never fabricated.

## PRD Statuses

- 🚧 Drafting: Initial proposals (may be incomplete)
- 🏃 Actionable: Ready for engineering work
- 🔒 Closed: Reflects what was delivered
- ❗ Abandoned: Project cancelled
