---
name: workflow-devils-advocate
description: Use when stress-testing product vision from business-user and customer perspectives - adopts CSM, Professional Services, Support, and end-customer lenses to generate a short, audience-focused Living FAQ. Does NOT generate engineering, security, or architecture questions - engineers run their own tech-spec process.
---

# Devil's Advocate

## Purpose

Stress-test the product vision from the perspectives of the people who will have to sell it, implement it, support it, and use it:

- Adopt business-user and customer lenses (CSM, Professional Services, Support, New Customer, Existing Customer)
- Surface the questions those audiences will actually ask
- Generate a short, usable Living FAQ — not a comprehensive objection dump
- Flag unanswered items the PM must resolve before the PRD is finalized

## Governing Principle

> The Living FAQ is for non-engineers. Its job is to help internal business teams sell, implement, and support the feature, and to help customers understand what's changing. Engineering questions belong in tech spec, security review, and the red team report — not here.

## Non-Goals

This skill does NOT produce:
- Scaling, performance, or architecture questions
- Security or compliance implementation details (XSS, auth tenancy, CSRF, CDN caching, etc.)
- Technology selection debates (vendor comparisons, framework trade-offs)
- API design concerns
- Abuse and misuse scenarios (those live in the red-team-report under harm scenarios)

If a question can only be answered by an engineer looking at code or architecture, drop it. Engineers surface those questions themselves downstream.

## When to Use

Activate when:
- User invokes `/project:devils-advocate`
- Phase 3 of `/project:prep` or `/project:ship-it`
- PM wants to stress-test a product concept from business-user angles
- Before writing a PRD to surface audience-level gaps

## Product Package Folder

All artifacts are read from and written to the initiative's package folder:

```
datasets/product/packages/{YYYY}/{slug}/
```

## Inputs Required

- **Context Brief** (`{package}/context-brief.md`) — customer evidence and problem statement
- **External Press Release** (`{package}/press-release-external.md`) — product vision and value prop
- **Internal Press Release** (`{package}/press-release-internal.md`) — team impact and operationalization
- **One-Pager** (`{package}/one-pager.md`) — condensed vision summary
- Minimum: Context Brief and at least one press release must exist

## Outputs Produced

- `{package}/living-faq.md` — audience-first FAQ with ≤20 total questions, ≤50 words per answer, ≤2,000 words total

## Hard Caps (Non-Negotiable)

| Cap | Limit |
|-----|-------|
| Total questions | ≤ 20 |
| Words per answer | ≤ 50 |
| Total words in the FAQ | ≤ 2,000 |
| Engineering-only questions | 0 |
| Abuse/misuse scenarios in FAQ | 0 (route to red-team-report) |

If a section would exceed its share, cut the lowest-value questions. The FAQ is useful only if it's short.

## Workflow

### Task 1: Audience-Based Interrogation

For each audience below, generate 2–4 specific questions that audience will actually ask about THIS product. Skip any question an engineer would ask.

**CSM / Account Manager:**
- How do I position this to customers? What's the 30-second pitch?
- Which customers are best suited for this? Which aren't?
- What objections should I expect, and how do I answer them?
- What should I tell customers this does NOT do yet?
- When can I start mentioning it on calls?

**Professional Services / Implementation:**
- How does this change the implementation or setup process?
- What training or documentation will internal teams need?
- Are there rollout edge cases (multi-entity customers, legacy data, special configs)?
- How does this interact with existing customer workflows?
- Who handles configuration changes — us, the customer, or the agent?

**Support:**
- What will customers most commonly get stuck on?
- What self-service resources need to exist at launch?
- What's the escalation path for bugs or confusion?
- What known limitations should support expect to explain?
- How will customers discover this feature exists?

**End Customer — New User:**
- What can I actually do with this?
- How do I get started? What's the first step?
- Where do I go if I need help?
- How will I know it's working?

**End Customer — Existing User:**
- Does this replace anything I'm using today?
- What stays the same? What changes for me?
- Is there a price change or new requirement?
- What happens to my existing data or setup?

### Task 2: Tag Each Question by Audience

Tag every question with its audience:

| Tag | Audience |
|-----|----------|
| `internal-csm` | CSM / Account Management |
| `internal-ps` | Professional Services / Implementation |
| `internal-support` | Support |
| `customer-new` | End Customer — New User |
| `customer-existing` | End Customer — Existing User |

Do NOT use priority tags (blocking/important/tracked/deferred) — those are retired.

### Task 3: Draft the Living FAQ

Use template `datasets/product/templates/living-faq.md`. Structure:

1. **TL;DR** — 3 lines: what it is, who it's for, when it ships
2. **For Internal Teams** — CSM / PS / Support subsections
3. **For Customers** — New Users / Existing Users subsections
4. **Open Questions for PM** — items the PM must answer before the PRD can be finalized or engineering can start. This section replaces the old blocking/important/tracked/deferred lists. Each item has: question, why it matters (one sentence), status (UNANSWERED / ANSWERED).

Answer what you can from the upstream artifacts. Mark the rest UNANSWERED and move it to "Open Questions for PM."

Every answer must be ≤50 words. If an answer needs more, the question is probably too broad — split or drop it.

### Task 4: Self-Check Against Hard Caps

Before writing the file, verify:
- Total questions ≤ 20
- Every answer ≤ 50 words
- Total word count ≤ 2,000
- Zero engineering/architecture/security-implementation questions
- Zero abuse/misuse scenarios (route to red-team-report if applicable)
- Every question has a clear audience tag

If any cap is exceeded, cut the lowest-value items until compliant.

## Arguments

- `--full` — Run all audience perspectives (default)
- `--audience "name"` — Run a single audience (e.g., "csm", "support", "new-customer")
- `--update` — Re-run against updated upstream artifacts (incremental)
- `--unanswered` — Surface the "Open Questions for PM" section only

## Quality Criteria

- [ ] ≤ 20 total questions across all audiences
- [ ] Every answer ≤ 50 words
- [ ] Total FAQ ≤ 2,000 words
- [ ] All 5 audiences represented (CSM, PS, Support, New Customer, Existing Customer)
- [ ] No engineering-only questions (scaling, architecture, security implementation, tech selection)
- [ ] No abuse/misuse scenarios (routed to red-team-report instead)
- [ ] Open Questions for PM section populated with items the PM must answer
- [ ] Every question references THIS product, not generic product questions

## Failure Modes

| Failure | Detection | Fix |
|---------|-----------|-----|
| Engineering drift | Questions about scaling, XSS, auth, CDN, performance, etc. | Delete — not the FAQ's job |
| Over-granular questions | Answers longer than 50 words, too much assumed detail | Cut or split the question |
| Compliance/security creep | "How do we handle GDPR / SOC2 / HIPAA?" | Route to red-team-report; drop from FAQ |
| Persona restatement | Questions that mirror the press release | Push deeper — what does this audience actually worry about? |
| Generic questions | Could apply to any product | Rewrite with specifics from this product |
| Over-volume | More than 20 questions total | Cut lowest-value items until ≤ 20 |

## Interaction Model

- **Agent generates questions and draft answers autonomously** — no PM permission needed
- **PM answers the Open Questions for PM section** — these are the only items that block PRD progress
- **Agent never marks its own answers as FINAL** — only PM can
- **Living FAQ may be updated by the PM in later phases** — red-team-reviewer does NOT write to this file

## Living Document Rules

- Only the PM edits the FAQ after initial generation (to add answers, refine wording, or retire stale questions)
- The `red-team-reviewer` skill does NOT append to this file — its findings go in `red-team-report.md` only
- Abuse/misuse scenarios live in `red-team-report.md`, not here

## Related Skills

- `vision-clarifier`: Produces the press releases this skill interrogates
- `agentic-api-designer`: Runs in parallel during Phase 3 (separate concern — agent use cases)
- `prd-creation`: Inherits the "Open Questions for PM" section into PRD Open Questions
- `red-team-reviewer`: Produces the adversarial/engineering/abuse review (separate artifact, does not touch this FAQ)
