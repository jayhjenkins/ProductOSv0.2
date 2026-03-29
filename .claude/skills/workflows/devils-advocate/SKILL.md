---
name: devils-advocate
description: Use when stress-testing product vision - adopts adversarial perspectives (skeptical engineer, confused user, compliance officer, competitor analyst, support rep, executive) to generate Living FAQ with prioritized objections and edge cases
---

# Devil's Advocate

## Purpose

Stress-test the product vision through adversarial interrogation:
- Adopt multiple distinct critical perspectives
- Surface questions the PM hasn't thought of
- Generate the Living FAQ — a continuously updating document
- Identify abuse/misuse scenarios
- Classify questions by urgency and blocking status

## Governing Principle

> As product ideas become specific, unaddressed questions and assumptions emerge. You must expose edge cases, capture objections, and surface hard questions — all before engineering begins.

## When to Use

Activate when:
- User invokes `/project:devils-advocate`
- Phase 3 of `/project:prep` or `/project:ship-it`
- PM wants to stress-test a product concept
- Before writing a PRD to surface gaps

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

- `{package}/living-faq.md` — Prioritized FAQ organized by topic with perspective tags

## Workflow

### Task 1: Perspective-Based Interrogation

For each persona, generate 5–10 pointed, specific questions. These must be SPECIFIC to this product — not generic questions that apply to anything.

**Skeptical Engineer:**
- How does this scale? What happens at 10x, 100x current load?
- What happens when [specific component] fails? What's the blast radius?
- What are the performance implications of [specific design choice]?
- What's the data model? Where are the consistency risks?
- What third-party dependencies are we taking on and what's the fallback?

**Confused First-Time User:**
- What happens if I don't understand [specific concept]? Where do I go for help?
- What if I want to undo [specific action]? Is it reversible?
- What's the minimum I need to know to get value from this?
- How do I know if it's working correctly vs. silently failing?
- What happens if I make a mistake during [specific workflow]?

**Compliance Officer:**
- What data are we collecting? Where is it stored? Who has access?
- What regulations apply (GDPR, SOC2, HIPAA, etc.)?
- What happens to user data if they churn?
- Are there data residency requirements?
- What audit trail exists for [specific actions]?

**Competitor Analyst:**
- [Specific competitor] already does this. Why is our approach better?
- What stops them from copying this in 6 months?
- Where is our approach weaker than existing solutions?
- What would a customer switching FROM [competitor] expect that we don't have?

**Support Representative:**
- What are the top 5 things users will complain about?
- What's the most common failure mode and how do we diagnose it?
- What's the escalation path when [specific thing] breaks?
- What self-service resources do users need?
- What's the expected support ticket volume increase?

**Executive Sponsor:**
- What's the ROI? How does this align with company strategy?
- What's the opportunity cost of doing this instead of [alternative]?
- What's the worst case scenario if this fails?
- How do we know when to kill this if it's not working?
- What does success look like at 30, 60, 90 days?

### Task 2: Classify & Prioritize Questions

Tag each question with a priority:

| Tag | Meaning | Action |
|-----|---------|--------|
| `blocking` | Must be answered before PRD can be written | PM must answer now |
| `important` | Should be answered before engineering begins | Carried into PRD Open Questions |
| `tracked` | Good question, can be answered during development | Carried into PRD Open Questions |
| `deferred` | Relevant for v2 or future iterations | Logged for future reference |

### Task 3: Draft Living FAQ

Structure the FAQ using template `datasets/product/templates/living-faq.md`:

- Organize by **topic area** (not by persona)
- Each entry contains:
  - The question
  - The source perspective (which persona raised it)
  - The priority tag
  - The current best answer (or **"UNANSWERED"** if PM hasn't addressed it)
- Include status counts in the header

### Task 4: Abuse & Misuse Scenario Generation

Specifically brainstorm how the product could be:
- **Misused**: Used in ways that harm the user's own interests
- **Abused**: Used to harm others
- **Unintended consequences**: Produces negative outcomes nobody planned for

This is distinct from feature edge cases. It's about real-world harm scenarios.

For each scenario:
- Describe the scenario
- Rate severity (critical / major / minor)
- Propose mitigation

## Arguments

- `--full` — Run all perspectives (default)
- `--persona "name"` — Run a single perspective (e.g., "skeptical engineer")
- `--update` — Re-run against updated artifacts (incremental)
- `--unanswered` — Surface all questions still marked UNANSWERED

## Quality Criteria

- [ ] At least 5 questions per persona perspective
- [ ] All `blocking` questions clearly identified
- [ ] FAQ organized by topic, not by persona
- [ ] Abuse/misuse section present with at least 3 scenarios
- [ ] No softball questions — every question challenges assumptions
- [ ] Questions are specific to THIS product, not generic
- [ ] Priority distribution is realistic (not everything is `blocking`)

## Failure Modes

| Failure | Detection | Fix |
|---------|-----------|-----|
| Generic questions | Could apply to any product | Rewrite with specific references to this product's design |
| All same priority | No differentiation between blocking and tracked | Re-evaluate: what truly blocks PRD writing? |
| Missing perspectives | Fewer than 6 personas represented | Add missing perspective sections |
| FAQ restates Context Brief | Questions have obvious answers from existing docs | Push deeper — ask what the docs DON'T cover |
| No abuse/misuse section | Section missing or trivial | Dedicated brainstorm on harm scenarios |

## Interaction Model

- **Agent generates questions autonomously** — does not ask PM for permission to be critical
- **PM answers questions** — agent presents questions, PM provides answers or marks as "will answer later"
- **Blocking questions require answers** — agent should push the PM to answer these before proceeding
- **Agent never marks its own answers as final** — only PM can finalize answers
- **Living FAQ is updated by multiple agents** — later phases may add questions

## Living Document Rules

The FAQ is not frozen after this phase:
- Any agent in later phases can ADD questions
- Only the PM can mark answers as FINAL
- Answers added by agents are marked "DRAFT — PM review needed"
- The FAQ gets updated in Phase 4 (PRD), Phase 5 (Red Team), and beyond

## Related Skills

- `vision-clarifier`: Produces the press releases this skill interrogates
- `agentic-api-designer`: Runs in parallel during Phase 3
- `prd-creation`: Inherits unanswered items into Open Questions
- `red-team-reviewer`: May add questions during Phase 5
