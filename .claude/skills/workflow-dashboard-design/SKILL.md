---
name: workflow-dashboard-design
description: Use when creating recurring product health dashboards - structures metrics by lifecycle stages, ensures North Star anchoring, includes counter-metrics, and establishes review cadence
---

# Dashboard Design Workflow

## Purpose

Design a structured set of metrics across the user lifecycle that gives a complete picture of product health, not just a single North Star. Creates recurring dashboards for team reviews, early problem detection, and strategic decision-making.

## When to Use This Workflow

Use this workflow when:
- Standing up a new product team and need recurring dashboard
- Existing dashboard feels incomplete or unfocused
- Preparing for quarterly business reviews
- Onboarding to a product and want to understand what "healthy" looks like
- Establishing metrics for ongoing product monitoring
- Need to rally team around clear success indicators

## Skills Sequence

This workflow orchestrates 4 core skills:

```
1. North Star Alignment
   ↓ (Anchor dashboard to company mission and business model)
2. Funnel-Based Metric Mapping
   ↓ (Ensure coverage across all lifecycle stages)
3. Proxy Metric Selection
   ↓ (Pick measurable indicators for each stage)
4. Trade-off Evaluation
   ↓ (Include counter-metrics to catch unintended effects)
   
OUTPUT: Dashboard structure by funnel, 5-10 metrics with definitions,
        counter-metrics, review cadence, alert thresholds
```

## Required Inputs

Gather this information before starting:

### Product Context
- **Company/product mission statement**
  - What's the overarching goal?
- **Business model type**
  - One of 5 categories (ads, freemium, SaaS, marketplace, e-commerce)
- **Strategic priorities**
  - Growth, retention, monetization, quality?

### Product Lifecycle
- **User lifecycle stages for this product**
  - How do users progress through your product?
  - What's the journey from awareness to retained power user?

### Current State
- **Existing metrics (if any)**
  - What are you currently tracking?
  - What gaps exist?
- **Key stakeholder questions**
  - What questions should dashboard answer?
  - What decisions does it inform?

### Operational Constraints
- **Review cadence desired**
  - Daily, weekly, monthly?
  - Different cadences for different audiences?
- **Alert capability**
  - Can you set automated alerts?
  - What thresholds trigger escalation?

## Workflow Steps

### Step 1: North Star Anchoring (15 minutes)

**Use the `north-star-alignment` skill**

Ground the dashboard in company-level goals:

**Activities:**
1. Identify business model and corresponding North Star metrics
2. Articulate how this product serves company mission
3. Define "healthy" for this product relative to North Star

**Questions to answer:**
- What company-level metrics does this product impact?
- How does product health translate to company health?
- What would "great" look like for this product?
- What's the connection between product and company success?

**Output:**

```markdown
## North Star Anchoring

**Business Model:** [Type]

**Company North Star Metrics:**
- [Metric 1]: [Definition]
- [Metric 2]: [Definition]

**Product's North Star Connection:**
- This product contributes to [Company North Star] by [mechanism]
- "Healthy" product = [Description tied to North Star]

**Mission Alignment:**
- Product serves mission: [How]
- Strategic priority: [Growth/Retention/Monetization/Quality]
```

### Step 2: Funnel Structure Mapping (20 minutes)

**Use the `funnel-metric-mapping` skill**

Decompose user journey into stages and identify metrics per stage:

**Activities:**
1. Define lifecycle stages (typically 4-5 stages)
2. List 1-3 key metrics per stage
3. Identify transition conversion rates
4. Map any flywheel dynamics

**Funnel template:**

```
Reach → Activation → Engagement (Breadth) → Engagement (Depth) → Retention
```

**For each stage, ask:**
- What defines success at this stage?
- What volume metric matters?
- What quality metric matters?
- What's the conversion rate to next stage?

**Output:**

```markdown
## Funnel Structure

**Stage 1: Reach**
- Definition: [When users become aware/access product]
- Key Metrics:
  1. [Metric]: [Definition + why it matters]
  2. [Metric]: [Definition + why it matters]
- Conversion to Activation: [%]

**Stage 2: Activation**
- Definition: [When users complete setup and reach first value]
- Key Metrics:
  1. [Metric]: [Definition + why it matters]
  2. [Metric]: [Definition + why it matters]
- Conversion to Engagement: [%]

**Stage 3: Engagement (Breadth)**
- Definition: [Regular product usage]
- Key Metrics:
  1. [Metric]: [Definition + why it matters]
  2. [Metric]: [Definition + why it matters]

**Stage 4: Engagement (Depth)**
- Definition: [Value-creating actions]
- Key Metrics:
  1. [Metric]: [Definition + why it matters]
  2. [Metric]: [Definition + why it matters]

**Stage 5: Retention**
- Definition: [Long-term repeat usage]
- Key Metrics:
  1. [Metric]: [Definition + why it matters]
  2. [Metric]: [Definition + why it matters]

**Flywheel Dynamics:**
- [If applicable, describe virtuous cycles]
```

### Step 3: Proxy Metric Selection (20 minutes)

**Use the `proxy-metric-selection` skill**

For each funnel stage, define precise measurable indicators:

**Activities:**
1. For each metric, define mathematical formula (numerator/denominator)
2. Create simplified alternatives where needed
3. Validate each metric is actionable by the team
4. Ensure leading indicators (not just lagging)

**Criteria for dashboard metrics:**
- **Actionable:** Team can directly influence
- **Understandable:** Explainable in one sentence
- **Measurable:** Clear data source
- **Leading:** Provides early signal, not just hindsight

**Output:**

```markdown
## Metric Definitions

**Reach Metrics:**

**1. [Metric Name]**
- Formula: [Numerator] / [Denominator]
- Data Source: [Where to measure]
- Actionability: [How team influences]
- Why it matters: [Connection to funnel stage goal]

**2. [Metric Name]**
[Same structure]

**Activation Metrics:**
[1-2 metrics with same detail]

**Engagement (Breadth) Metrics:**
[1-2 metrics with same detail]

**Engagement (Depth) Metrics:**
[1-2 metrics with same detail]

**Retention Metrics:**
[1-2 metrics with same detail]
```

### Step 4: Counter-Metric Identification (15 minutes)

**Use the `tradeoff-evaluation` skill**

Identify metrics that could indicate unintended consequences:

**Activities:**
1. For each primary metric, ask "what could go wrong?"
2. Identify cannibalization risks
3. Define acceptable ranges
4. Plan monitoring approach

**Counter-metric categories:**

1. **Cannibalization Metrics**
   - What other products/features might suffer?
   - Example: New feature adoption hurting core feature usage

2. **Quality Degradation Metrics**
   - What quality indicators could decline?
   - Example: Growth at expense of user satisfaction

3. **Sustainability Metrics**
   - What could indicate unsustainable growth?
   - Example: High churn masked by high acquisition

4. **Balance Metrics (for marketplaces)**
   - Supply vs. demand balance
   - Example: Too many drivers, not enough riders

**Output:**

```markdown
## Counter-Metrics

**For Primary Metric: [Name]**
- Counter-metric 1: [Name]
  - What it catches: [Unintended effect]
  - Acceptable range: [Threshold]
  - Alert if: [Condition]

**For Primary Metric: [Name]**
- Counter-metric 2: [Name]
  - What it catches: [Unintended effect]
  - Acceptable range: [Threshold]
  - Alert if: [Condition]

[2-3 counter-metrics total]

**Cannibalization Watch:**
- [Product/feature to monitor for impact]

**Quality Indicators:**
- [Metric to ensure quality maintained]
```

### Step 5: Dashboard Assembly and Review Cadence (15 minutes)

**Activities:**
1. Prioritize metrics (not all are equal)
2. Organize into dashboard sections
3. Define review cadence
4. Set alert thresholds
5. Assign ownership

**Dashboard structure:**

```markdown
# [Product Name] Health Dashboard

## 🎯 North Star (Company-Level)
[1-2 company metrics this product impacts]

## 📊 Product North Star
[1-2 top-line product metrics]

## 🔄 Funnel Health

### Reach
- [Metric 1]: [Current value] [Trend ↑↓→]
- [Metric 2]: [Current value] [Trend ↑↓→]

### Activation
- [Metric 1]: [Current value] [Trend ↑↓→]
- Reach → Activation: [Conversion %]

### Engagement (Breadth)
- [Metric 1]: [Current value] [Trend ↑↓→]
- Activation → Engagement: [Conversion %]

### Engagement (Depth)
- [Metric 1]: [Current value] [Trend ↑↓→]

### Retention
- [Metric 1]: [Current value] [Trend ↑↓→]
- [Metric 2]: [Current value] [Trend ↑↓→]

## ⚠️ Counter-Metrics & Health Checks
- [Counter-metric 1]: [Current value] [Status: ✓ Healthy / ⚠️ Warning / 🚨 Alert]
- [Counter-metric 2]: [Current value] [Status: ✓ Healthy / ⚠️ Warning / 🚨 Alert]

## 📈 Key Insights (Updated Weekly)
- [Insight 1]
- [Insight 2]
- [Action items]
```

**Review cadence definition:**

```markdown
## Dashboard Review Cadence

**Daily Review (5 minutes):**
- Audience: Product team
- Metrics: [2-3 most critical metrics]
- Purpose: Early problem detection
- Action threshold: [What triggers immediate investigation]

**Weekly Review (30 minutes):**
- Audience: Product team + stakeholders
- Metrics: Full dashboard
- Purpose: Trend analysis, prioritization
- Format: [Standup / Presentation / Async doc]

**Monthly Deep-Dive (60 minutes):**
- Audience: Product team + leadership
- Metrics: Full dashboard + segmentation analysis
- Purpose: Strategic review, goal setting
- Format: [Meeting / Written review]

**Quarterly Business Review:**
- Audience: Executives
- Metrics: North Star + key highlights
- Purpose: Alignment on strategy and resources
```

**Alert thresholds:**

```markdown
## Alert Configuration

**Critical Alerts (Immediate attention):**
- [Metric] drops below [threshold]: [Who to notify]
- [Counter-metric] exceeds [threshold]: [Who to notify]

**Warning Alerts (Next-day review):**
- [Metric] trends down for [X days]: [Who to notify]

**Monitoring (Weekly review):**
- [Metric ranges to track]
```

**Ownership:**

```markdown
## Metric Ownership

| Metric | Owner | Data Source | Update Frequency |
|--------|-------|-------------|------------------|
| [Metric 1] | [Name/Team] | [Tool/Table] | Real-time |
| [Metric 2] | [Name/Team] | [Tool/Table] | Daily |
| [Metric 3] | [Name/Team] | [Tool/Table] | Weekly |
```


## MCP Data Enrichment (Optional)

When MCP data sources are connected, map dashboard metrics to actual data sources and validate measurability. Skip if tools are unavailable.

### Map Metrics to Pendo Entities

For each proposed dashboard metric, use `mcp__claude_ai_Pendo__searchEntities` (subId: `4818486697721856`, appId for relevant app, itemType: ["Feature", "Page", "Guide"], search: "{metric_behavior}", search_fallback: ["{metric_keyword}"]) to:
- Find the Pendo entity that corresponds to each metric
- Record the entity ID for dashboard implementation
- Flag metrics that have no Pendo instrumentation as requiring setup

### Zendesk Health Metrics

Suggest including support-derived metrics in the dashboard:
- **Ticket volume trend**: From `is_prod.zendesk_zendesk.zendesk__ticket_summary` or daily aggregation of `is_prod.zendesk.ticket`
- **CSAT score trend**: From `is_prod.zendesk.satisfaction_rating` with monthly aggregation
- **Resolution time**: From `is_prod.zendesk_zendesk.zendesk__ticket_metrics` (first reply time, resolution time)
- **Open ticket backlog**: From `is_prod.zendesk_zendesk.zendesk__ticket_backlog`
- **Escalation rate**: From `is_prod.zendesk.ticket` WHERE `custom_escalated_client = true`

### Data Source Mapping Table

Add a "Data Source" column to the Metric Ownership table:

| Metric | Owner | Data Source | Entity ID / Query |
|--------|-------|-------------|-------------------|
| {metric_name} | {team} | Pendo | {pendo_entity_id} |
| {metric_name} | {team} | Zendesk | {sql_query_pattern} |
| {metric_name} | {team} | Gong | {tracker_name} |
| {metric_name} | {team} | Manual | {collection_method} |

This mapping ensures every dashboard metric has a concrete, queryable data source.

## Dashboard Design Principles

### Principle 1: Comprehensive but Focused

**Balance:**
- Cover all lifecycle stages (comprehensive)
- Limit to 5-10 metrics total (focused)
- Prioritize metrics by impact and actionability

**Avoid:**
- Single-metric dashboards (miss problems elsewhere)
- 20+ metric dashboards (overwhelming, unfocused)

### Principle 2: Leading + Lagging Indicators

**Leading indicators (early signals):**
- Activation rate (predicts retention)
- Engagement frequency (predicts habit formation)
- NPS/satisfaction (predicts churn)

**Lagging indicators (confirm outcomes):**
- Retention rate (confirms product-market fit)
- Revenue (confirms monetization)
- Lifetime value (confirms unit economics)

**Balance:** Include both for complete picture

### Principle 3: Volume + Quality

**Volume metrics (quantity):**
- Total users
- Total transactions
- Total content created

**Quality metrics (value):**
- User satisfaction scores
- Transaction value
- Content engagement rate

**Balance:** Prevent optimizing for wrong thing

### Principle 4: Segment Where It Matters

**Standard view:**
- Aggregate metrics for whole product

**Segmented views:**
- By user type (power users, new users, paying users)
- By geography (if relevant)
- By cohort (when they joined)

**When to segment:**
- Behavior varies significantly by segment
- Different strategies for different segments
- Need to track specific initiatives

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Only measuring retention | Cover full funnel (reach through retention) |
| Vanity metrics without action | Ensure each metric is actionable by team |
| No counter-metrics | Add 2-3 to catch unintended effects |
| Too many metrics (20+) | Prioritize to 5-10 most important |
| No review cadence defined | Set daily/weekly/monthly schedule |
| Metrics without owners | Assign ownership for each |
| No alert thresholds | Define when to escalate |

## Success Criteria

Dashboard design succeeds when:
- Anchored to company North Star explicitly
- Covers all major lifecycle stages (4-5 stages)
- 5-10 primary metrics with precise definitions
- 2-3 counter-metrics included
- Review cadence established (daily, weekly, monthly)
- Alert thresholds defined
- Ownership assigned for each metric
- Stakeholders understand and accept dashboard
- Dashboard answers key product questions
- Team can explain why each metric matters

## Real-World Example: Uber Driver Quality Dashboard

### Step 1: North Star Anchoring (15 min)

```
Business Model: Two-sided marketplace
Company North Star: Monthly Active Drivers + Monthly Active Riders
Product (Driver Quality): Contributes to driver retention and rider satisfaction
"Healthy" = High-quality drivers staying active long-term
Strategic Priority: Quality + Retention (sustainable supply)
```

### Step 2: Funnel Structure (20 min)

```
Reach: All active drivers (baseline)
  - Total active drivers (monthly)
  
Activation: Drivers engage with quality program
  - % viewing quality dashboard (target: 80%)
  - % reading quality tips (target: 50%)

Engagement (Breadth): Drivers aware of ratings
  - % checking ratings weekly (target: 60%)
  
Engagement (Depth): Drivers improve quality
  - Tips received per active driver
  - Rating improvement trend

Retention: Drivers maintain high quality
  - % drivers in 4.8+ bucket month-over-month
  - Hours driven by quality tier
```

### Step 3: Proxy Metrics (20 min)

```
PRIMARY METRICS:

1. Driver Quality Distribution
   - Formula: Hours driven by rating bucket / Total hours
   - X-axis: 4.5-4.74, 4.75-5.0, 5.0+ with tips
   - Y-axis: Hours driven
   - Goal: Maximize hours in 5.0+ bucket

2. Quality Program Engagement
   - Formula: Drivers viewing dashboard weekly / Total active drivers
   - Target: 80%
   - Leading indicator of quality awareness

3. Tip Rate
   - Formula: Drivers receiving ≥1 tip per week / Total active drivers
   - Target: 40%
   - Quality indicator beyond ratings

4. Rating Stability
   - Formula: Drivers maintaining/improving rating MoM / Total
   - Target: 85%
   - Retention proxy
```

### Step 4: Counter-Metrics (15 min)

```
COUNTER-METRICS:

1. Driver Churn Rate
   - What it catches: Quality standards too strict
   - Current: 8%/month
   - Acceptable: <10%
   - Alert if: >12%

2. Ride Acceptance Rate
   - What it catches: Drivers becoming too picky
   - Current: 92%
   - Acceptable: >85%
   - Alert if: <85%

3. Surge Pricing Frequency
   - What it catches: Insufficient supply
   - Current: 15% of rides
   - Acceptable: <20%
   - Alert if: >25%
```

### Step 5: Dashboard Assembly (15 min)

```
# Uber Driver Quality Dashboard

## 🎯 Company North Star
- Monthly Active Drivers: 500K (↑ 2%)
- Hours Driven (Total): 8M (↑ 3%)

## 📊 Product North Star
- Hours Driven in 4.8+ Bucket: 4.8M / 60% of total (↑ 5%) [GOAL: 65%]
- Quality Program Engagement: 78% (↑ 3%)

## 🔄 Funnel Health

### Activation (Quality Program)
- Dashboard Views: 78% of drivers (target: 80%)
- Tips Read: 52% of drivers (target: 50%) ✓

### Engagement (Quality Awareness)
- Check Ratings Weekly: 58% (target: 60%)
- Tips Received: 38% of drivers (target: 40%)

### Retention (Quality Maintenance)
- Rating Stability MoM: 84% (target: 85%)
- Hours by Quality Tier:
  - 4.5-4.74: 1.5M / 19% (↓ 2%) [Good]
  - 4.75-5.0: 1.7M / 21% (→)
  - 5.0+ tips: 4.8M / 60% (↑ 5%) [Great]

## ⚠️ Counter-Metrics
- Driver Churn: 9.2%/month ✓ (threshold: <10%)
- Acceptance Rate: 90% ✓ (threshold: >85%)
- Surge Frequency: 17% ✓ (threshold: <20%)

## 📈 Key Insights (Week of Dec 1)
- Strong progress toward 65% quality goal (on track for Q1)
- Tip rate slightly below target; testing new prompts
- Churn elevated but within acceptable range
- Action: Launch tip prompt experiment next week

---

## Review Cadence

**Daily (5 min):** Churn rate, acceptance rate (critical alerts)
**Weekly (30 min):** Full dashboard, trend review
**Monthly (60 min):** Deep-dive, segmentation analysis
**Quarterly:** Strategic review with leadership

## Alert Configuration

**Critical:**
- Churn >12%: Alert product lead + ops
- Acceptance <85%: Alert product lead + ops

**Warning:**
- Quality goal progress <2%/month: Weekly review
- Counter-metric approaching threshold: Flag in review
```

**Time to complete: 90 minutes**

## Related Skills

This workflow orchestrates these skills:
- **north-star-alignment** (Step 1)
- **funnel-metric-mapping** (Step 2)
- **proxy-metric-selection** (Step 3)
- **tradeoff-evaluation** (Step 4)

## Related Workflows

- **metrics-definition**: Similar process but for one-time metric selection
- **goal-setting**: Uses dashboard metrics to set OKR targets
- **tradeoff-decision**: Uses dashboard to monitor trade-offs

## Time Estimate

**Total: 85-100 minutes**
- Step 1 (North Star): 15 min
- Step 2 (Funnel): 20 min
- Step 3 (Proxy): 20 min
- Step 4 (Counter-metrics): 15 min
- Step 5 (Assembly): 15 min
- Buffer: 10 min

