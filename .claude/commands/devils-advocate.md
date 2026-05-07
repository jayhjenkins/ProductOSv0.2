# /project:devils-advocate

## MANDATORY: Use the devils-advocate Skill

**You MUST use the `devils-advocate` skill located at `.claude/skills/workflow-devils-advocate/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using devils-advocate to stress-test the product vision from business-user and customer perspectives"
2. **Read the skill**: Load `.claude/skills/workflow-devils-advocate/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Adopt business-user and customer perspectives (CSM, Professional Services, Support, new customer, existing customer) to surface the questions those audiences will actually ask about this feature. Produce a short, audience-focused Living FAQ.

This skill does NOT produce engineering, architecture, security-implementation, or compliance-implementation questions. Engineers surface their own questions downstream during tech spec. Abuse/misuse and harm scenarios go in the red team report.

## Prerequisites

- Context Brief must exist
- Press Releases (external + internal) should exist
- One-Pager should exist

## Hard Caps

- ≤ 20 questions total
- ≤ 50 words per answer
- ≤ 2,000 words total
- Zero engineering/architecture/security-implementation questions
- Zero abuse/misuse scenarios (route to red-team-report)

## Arguments

- `--full` — Run all audience perspectives (default)
- `--audience "name"` — Run a single audience (e.g., "csm", "ps", "support", "new-customer", "existing-customer")
- `--update` — Re-run against updated upstream artifacts
- `--unanswered` — Surface the "Open Questions for PM" section only

## Output

Written to the initiative's package folder: `datasets/product/packages/{YYYY}/{slug}/`

- `{package}/living-faq.md` — audience-first FAQ: Internal Teams (CSM / PS / Support) + Customers (New / Existing) + Open Questions for PM
