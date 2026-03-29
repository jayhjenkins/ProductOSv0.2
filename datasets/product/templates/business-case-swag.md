# Business Case (SWAG): {PRODUCT_NAME}

**Date:** {YYYY-MM-DD}
**PRD Reference:** `{path to PRD}`

> The SWAG's value is not precision — it's making hidden assumptions visible and testable.

---

## Executive Summary

{This product targets [X] users in the [segment] market, priced at [Y] per [unit]. With [Z]% conversion from trial to paid, we estimate [revenue] in year 1 revenue against [costs] in costs. The model is most sensitive to [assumption A] and [assumption B]. If those assumptions hold, the product reaches profitability by [timeline]. The primary risk is [risk]; the primary upside is [upside].}

---

## Assumptions Register

*Every number in this model traces back to an assumption listed here.*

| ID | Assumption | Value | Source | Confidence |
|----|-----------|-------|--------|------------|
| A-1 | {Assumption name} | {Value} | {Where this came from} | {High/Medium/Low} |
| A-2 | | | | |
| A-3 | | | | |
| A-4 | | | | |
| A-5 | | | | |

---

## Market Sizing

| Level | Estimate | Source | Confidence | Methodology |
|-------|----------|--------|------------|-------------|
| **TAM** (Total Addressable Market) | {$X or N users} | {Source} | {High/Med/Low} | {Top-down/Bottom-up/Analogous} |
| **SAM** (Serviceable Addressable Market) | {$X or N users} | {Source} | | |
| **SOM** (Serviceable Obtainable Market — Year 1) | {$X or N users} | {Source + rationale} | | |

---

## Revenue Model

### Pricing Model

{Description of pricing approach: per user, per transaction, subscription, freemium, usage-based, etc.}

### Conversion Funnel

| Stage | Metric | Value | Assumption ID |
|-------|--------|-------|---------------|
| Awareness → Trial | Conversion Rate | {X%} | {A-N} |
| Trial → Activation | Conversion Rate | {X%} | |
| Activation → Retention (Month 1) | Retention Rate | {X%} | |
| Retained → Paid | Conversion Rate | {X%} | |
| **ARPU** | Average Revenue Per User | {$X/mo} | |

### Growth Model

| Channel | Expected Volume (Year 1) | CAC | Assumption ID |
|---------|-------------------------|-----|---------------|
| Paid Acquisition | {N users} | {$X} | {A-N} |
| Organic | {N users} | {$X} | |
| Viral/Referral | {N users} | {$X} | |
| Channel Partnerships | {N users} | {$X} | |
| **Total** | **{N users}** | **{weighted avg}** | |

---

## Cost Model

### Infrastructure Costs

| Item | Unit Cost | Volume (Year 1) | Total | Assumption ID |
|------|----------|-----------------|-------|---------------|
| Compute | {$/user/mo or $/transaction} | {N} | {$X} | {A-N} |
| Storage | {$/GB/mo} | {N GB} | | |
| Third-Party APIs | {$/call} | {N calls} | | |
| **Subtotal** | | | **{$X}** | |

### Support Costs

| Item | Unit Cost | Volume (Year 1) | Total | Assumption ID |
|------|----------|-----------------|-------|---------------|
| Cost per Ticket | {$X} | {N tickets} | {$X} | {A-N} |
| Staffing | {$X/FTE} | {N FTEs} | | |
| **Subtotal** | | | **{$X}** | |

### Operational Costs

| Item | Cost (Year 1) | Assumption ID |
|------|--------------|---------------|
| Monitoring & Maintenance | {$X} | {A-N} |
| Compliance & Audit | {$X} | |
| Content Moderation | {$X} | |
| **Subtotal** | **{$X}** | |

### Customer Acquisition Cost by Channel

| Channel | Cost per Lead | Lead → Customer Rate | Effective CAC |
|---------|-------------- |---------------------|---------------|
| {Channel 1} | {$X} | {X%} | {$X} |
| {Channel 2} | | | |

---

## Sensitivity Analysis

*How does the outcome change when each assumption shifts?*

| Assumption | Baseline | -25% Impact | +25% Impact | Break-Even Value | Sensitivity |
|------------|----------|-------------|-------------|------------------|-------------|
| {Assumption 1} | {value} | {revenue/profit impact} | {revenue/profit impact} | {value where unprofitable} | **High** |
| {Assumption 2} | | | | | **High** |
| {Assumption 3} | | | | | Medium |
| {Assumption 4} | | | | | Medium |
| {Assumption 5} | | | | | Low |

**Most Sensitive Assumptions:**
1. **{Assumption name}** — {Why this matters and what we can do to validate it}
2. **{Assumption name}** — {Why this matters}

---

## Scenario Comparison

| Metric | Pessimistic | Baseline | Optimistic |
|--------|-------------|----------|------------|
| Year 1 Users | {N} | {N} | {N} |
| Year 1 Revenue | {$X} | {$X} | {$X} |
| Year 1 Total Costs | {$X} | {$X} | {$X} |
| Year 1 Profit/Loss | {$X} | {$X} | {$X} |
| Break-Even Timeline | {months} | {months} | {months} |
| LTV:CAC Ratio | {X:1} | {X:1} | {X:1} |

---

## Key Risks and Assumptions

| Risk | Impact if Wrong | Likelihood | Mitigation |
|------|----------------|------------|------------|
| {Risk 1} | {What happens} | {High/Med/Low} | {How to reduce risk} |
| {Risk 2} | | | |

---

## Changelog

| Date | Changes | By |
|------|---------|-----|
| {YYYY-MM-DD} | Initial SWAG model | |
