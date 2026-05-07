---
name: workflow-swag-modeler
description: Use when building business case models - creates transparent financial models with labeled assumptions, TAM/SAM/SOM market sizing, revenue/cost models, sensitivity analysis showing assumption impact, and executive summary narrative
---

# SWAG Modeler

## Purpose

Build a simple, transparent financial model for the product:
- Expose assumptions, not produce precise forecasts
- TAM/SAM/SOM market sizing with sources
- Revenue and cost models with labeled variables
- Sensitivity analysis showing which assumptions matter most
- Executive summary readable in 5 minutes

## Governing Principle

> You don't need a 300-page economic analysis. You need a simple model that exposes your assumptions and shows whether the math works. The SWAG's value is not precision — it's making hidden assumptions visible and testable.

## When to Use

Activate when:
- User invokes `/project:swag`
- Phase 6 of `/project:build` or `/project:ship-it`
- PM needs to justify a product investment to leadership
- Evaluating whether a product opportunity is worth pursuing

## Product Package Folder

All artifacts are read from and written to the initiative's package folder:

```
datasets/product/packages/{YYYY}/{slug}/
```

## Inputs Required

- **Complete PRD** — in `{package}/` and `datasets/product/prds/{YYYY}/`
- **Context Brief** (`{package}/context-brief.md`) — customer evidence, market context
- **Press Releases** (`{package}/press-release-*.md`) — value proposition and target market
- **Red Team Report** (`{package}/red-team-report.md`) — risk factors (optional but recommended)
- Minimum: Complete PRD and Context Brief

## Outputs Produced

- `{package}/business-case-swag.md` — Financial model with assumptions, sizing, models, sensitivity, and executive summary

## Workflow

### Task 1: Market Sizing

Estimate the addressable market with clearly labeled sources:

| Level | Question | Requirement |
|-------|----------|-------------|
| **TAM** | Everyone who could theoretically use this | Estimate with source |
| **SAM** | The segment you can realistically reach | Estimate with source |
| **SOM** | The segment you'll capture in year 1 | Estimate with source and rationale |

Every estimate must be labeled with:
- **Source**: Where did this number come from?
- **Confidence**: High / Medium / Low
- **Methodology**: Top-down, bottom-up, or analogous

### Task 2: Revenue Model Construction

Build the revenue calculation with each variable as an explicit, labeled assumption:

**Pricing model**: Per user, per transaction, subscription, freemium conversion, usage-based, etc.

**Conversion funnel**:
```
Awareness → Trial/Signup → Activation → Retention → Revenue
   ↓            ↓              ↓            ↓          ↓
 [rate]       [rate]         [rate]       [rate]    [ARPU]
```
Each conversion rate is a labeled assumption with source.

**Growth model**:
- Paid acquisition (CAC by channel, expected volume)
- Organic (SEO, word of mouth, content)
- Viral/referral (k-factor if applicable)
- Channel partnerships

### Task 3: Cost Model Construction

Build the cost calculation:

**Infrastructure costs**:
- Compute (per-user or per-transaction cost)
- Storage (data growth rate)
- Third-party APIs (per-call costs, volume estimates)

**Support costs**:
- Cost per support ticket
- Expected ticket volume (per 100 users)
- Staffing implications

**Operational costs**:
- Monitoring and maintenance
- Content moderation (if applicable)
- Compliance and audit

**Customer acquisition cost (CAC)** by channel:
- Paid channels (cost per lead, conversion to customer)
- Sales-assisted (rep time per deal)
- Self-serve (infrastructure cost per signup)

### Task 4: Sensitivity Analysis

For each key assumption:

| Assumption | Baseline | -25% | +25% | Break-Even | Sensitivity |
|------------|----------|------|------|------------|-------------|
| {name} | {value} | {impact} | {impact} | {value where unprofitable} | High/Med/Low |

**Identify the 2–3 assumptions the model is most sensitive to.** These are the assumptions that deserve the most validation effort.

**Scenario comparison**:

| Metric | Pessimistic | Baseline | Optimistic |
|--------|-------------|----------|------------|
| Year 1 Revenue | | | |
| Year 1 Costs | | | |
| Break-even Timeline | | | |
| Users at Year 1 | | | |

### Task 5: Executive Summary

Produce a one-paragraph narrative:

> "This product targets [X] users in the [segment] market, priced at [Y] per [unit]. With [Z]% conversion from trial to paid, we estimate [revenue] in year 1 revenue against [costs] in costs. The model is most sensitive to [assumption A] and [assumption B]. If those assumptions hold, the product reaches profitability by [timeline]. The primary risk is [risk]; the primary upside is [upside]."

This paragraph must be understandable by a non-financial PM in under 60 seconds.

## Arguments

- `--generate` — Build full model from PRD and context (default)
- `--sensitivity` — Run sensitivity analysis on existing model
- `--scenario "pessimistic"` — Generate a specific scenario
- `--adjust "assumption=value"` — Modify a specific assumption and re-run

## Quality Criteria

- [ ] All assumptions explicitly labeled with source and confidence level
- [ ] Sensitivity analysis for every key assumption (at least 5)
- [ ] Both optimistic and pessimistic scenarios present
- [ ] Cost model includes support AND operational costs, not just infrastructure
- [ ] Executive summary is one readable paragraph
- [ ] Market sizing has TAM/SAM/SOM with distinct sources
- [ ] Revenue model shows complete funnel with conversion rates
- [ ] Break-even value identified for most sensitive assumptions
- [ ] No false precision — estimates rounded appropriately with confidence levels

## Failure Modes

| Failure | Detection | Fix |
|---------|-----------|-----|
| Hidden assumptions | Numbers appear without source or rationale | Label every assumption with source |
| Revenue-only model | No cost analysis | Add full cost model |
| No sensitivity | Single-point estimates without range | Add ±25% analysis for every assumption |
| False precision | "$1,234,567 in revenue" | Round appropriately, add confidence level |
| Missing cost-to-serve | Infrastructure only, no support/ops | Add support costs, operational costs, CAC |
| Optimism bias | Only best-case shown | Add pessimistic scenario and break-even analysis |

## Interaction Model

- **Agent builds the model autonomously** from PRD and upstream artifacts
- **PM validates assumptions** — are the numbers in the right ballpark?
- **Agent highlights most sensitive assumptions** — PM decides how much validation they need
- **PM decides**: Whether the business case is strong enough to proceed
- **Agent does NOT make go/no-go recommendations** — just exposes the math

## Related Skills

- `prd-creation`: Provides scope and target audience for sizing
- `red-team-reviewer`: Risk factors inform pessimistic scenarios
- `vision-clarifier`: Market positioning informs pricing model
- `research-gathering`: May have market data for sizing inputs
