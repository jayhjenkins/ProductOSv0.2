---
name: workflow-metric-diagnosis
description: Use when investigating unexpected metric changes - systematically narrows root cause through 4D segmentation, intrinsic vs extrinsic factor analysis, hypothesis testing, and North Star impact assessment
---

# Metric Diagnosis Workflow

## Purpose

Systematically investigate why a metric changed unexpectedly (dropped or spiked) by segmenting data, distinguishing internal vs. external factors, and testing hypotheses to identify root cause. Prevents rushing to wrong conclusions and ensures evidence-based responses.

## When to Use This Workflow

Use this workflow when:
- Key metrics drop or spike unexpectedly
- Leadership asks "what happened to [metric]?"
- Post-mortem analysis needed after incident
- A/B test shows unexpected patterns
- Need to validate suspected root cause
- User behavior changed suddenly without obvious reason

## Skills Sequence

This workflow applies the `root-cause-diagnosis` skill three times, then assesses North Star impact:

```
1. Root Cause Diagnosis (Phase 1)
   ↓ (Segment across 4 dimensions: People, Geography, Technology, Time)
2. Root Cause Diagnosis (Phase 2)
   ↓ (Distinguish intrinsic vs extrinsic factors)
3. Root Cause Diagnosis (Phase 3)
   ↓ (Build hypothesis table and test against data)
4. North Star Alignment
   ↓ (Assess impact on top-line metrics)
   
OUTPUT: Narrowed scope, tested hypotheses, identified root cause, recommended actions
```

## Required Inputs

Gather this information before starting:

### Metric Change Information
- **The metric that changed**
  - Name and definition
  - Example: "Weekly Active Users (WAU)"
- **Magnitude of change**
  - Absolute and percentage
  - Example: "10,000 → 9,000 (10% drop)"
- **Timeframe**
  - When was it noticed?
  - Over what period did change occur?
  - Example: "Noticed today, change happened over past week"

### Data Access
- **Segmented data availability**
  - Can you segment by user type, geography, platform?
  - Are raw logs accessible?
- **Comparison data**
  - Historical baselines
  - Year-over-year seasonality
  - Competitor benchmarks (if available)

### Recent Activity Log
- **Recent releases** (past 1-4 weeks)
  - Feature launches
  - Bug fixes
  - Infrastructure changes
- **Running experiments**
  - A/B tests active
  - Configuration changes
- **External context**
  - Marketing campaigns
  - News events
  - Competitor activity

## Workflow Steps

### Phase 0: Data Quality Verification (5 minutes)

**Before investigating, confirm the data is real:**

1. **Check reporting systems**
   - Is tracking still functional?
   - Any pipeline issues?
   - Data freshness correct?

2. **Cross-reference sources**
   - Do multiple data sources show same pattern?
   - Internal dashboards vs. external tools aligned?

3. **Validate sample sizes**
   - Sufficient data for statistical significance?
   - Time periods comparable?

**Red flags that indicate data quality issues:**
- Metric went to exactly zero
- Change happened at exact midnight
- Only visible in one data source
- Coincides with known tracking deployment

**If data quality issue found:** Fix tracking first, then re-investigate if problem persists.

**If data is valid:** Proceed to Phase 1.

### Phase 1: Narrow the Scope (15-20 minutes)

**Use the `root-cause-diagnosis` skill - 4 Dimension Segmentation**

Ask clarifying questions across all four dimensions:

#### Dimension 1: People (User Segments)

Questions to ask:
- Does it affect all users equally?
- Specific demographics (age, gender, location)?
- New vs. returning users?
- Free vs. paid users?
- Power users vs. casual users?
- Specific cohorts or user types?

Request data segmentation by user attributes.

#### Dimension 2: Geography

Questions to ask:
- Specific countries or regions affected?
- Certain cities?
- Urban vs. rural?
- Climate zones?
- Time zones?

Request data segmentation by location.

#### Dimension 3: Technology (Platform)

Questions to ask:
- iOS vs. Android?
- Web vs. mobile app?
- Desktop vs. mobile web?
- Specific browser or OS versions?
- Device types?
- Network types (WiFi vs. cellular)?

Request data segmentation by platform/device.

#### Dimension 4: Time

Questions to ask:
- When exactly did it start?
- Gradual decline or sudden drop?
- Day of week patterns?
- Time of day patterns?
- Recurring or one-time?
- Seasonal effects?

Request time-series data with granular breakdown.

**Output of Phase 1:**

Narrow problem statement from:
- ❌ "Usage is down"

To:
- ✓ "iOS usage among teens in US dropped 10% starting Sept 1st"

**Document:**
```markdown
## Narrowed Scope

**Original statement:** [Broad problem]
**Narrowed statement:** [Specific problem]

**Affected segments:**
- People: [Which user groups]
- Geography: [Which locations]
- Technology: [Which platforms]
- Time: [When and pattern]

**Unaffected segments:**
- [What stayed stable - equally important]
```

### Phase 2: Generate Hypotheses (15-20 minutes)

**Use the `root-cause-diagnosis` skill - Intrinsic vs. Extrinsic Factor Analysis**

Brainstorm potential causes in both categories:

#### Intrinsic Factors (Internal Changes)

**Engineering & Product:**
- Recent code releases (check deploy logs)
- Bug introductions
- Feature launches by any team
- A/B experiments started/stopped
- Algorithm or ranking changes
- Performance degradations

**Check with:**
- Engineering team (deploys, errors, performance)
- Other product teams (their launches)
- Data team (tracking changes)

**Operations & Business:**
- Pricing changes
- Policy updates
- Support process changes
- Marketing campaign changes

**Check with:**
- Operations team
- Marketing team
- Customer success team

#### Extrinsic Factors (External Events)

**Competition:**
- Competitor product launches
- Competitor pricing changes
- Competitor marketing campaigns

**Market:**
- Economic shifts
- Industry trends
- Regulatory changes
- Platform policy changes (iOS, Android, etc.)

**Calendar/Seasonal:**
- Holidays
- School schedules
- Weather patterns
- Cultural events

**News/PR:**
- News coverage (positive or negative)
- Social media trends
- External events affecting user behavior

**Check with:**
- Sales team (competitive intelligence)
- Customer success (user feedback)
- Marketing (market trends)
- Industry news sources

**Output of Phase 2:**

List of 4-6 hypotheses (mix of intrinsic and extrinsic):

```markdown
## Hypothesis List

**Intrinsic (Internal):**
1. [Hypothesis name]: [Description]
2. [Hypothesis name]: [Description]
3. [Hypothesis name]: [Description]

**Extrinsic (External):**
4. [Hypothesis name]: [Description]
5. [Hypothesis name]: [Description]
6. [Hypothesis name]: [Description]
```

### Phase 3: Test Hypotheses (20-30 minutes)

**Use the `root-cause-diagnosis` skill - Hypothesis Table Method**

#### Step 3.1: Create Hypothesis Table

**Columns:** Data points observed (from Phase 1)
**Rows:** Potential causes (from Phase 2)

**Fill each cell with predicted impact:**
- ↓ = Would decrease this segment
- ↑ = Would increase this segment
- → = No effect on this segment
- ? = Uncertain

#### Step 3.2: Match Patterns

For each hypothesis:
- Do predictions match observations?
- If ALL predictions match → Possible cause
- If ANY predictions contradict → Rule out

#### Step 3.3: Request Differentiating Data

If multiple hypotheses fit:
- Identify data points that would differ between them
- Request additional segmentation
- Narrow to single most likely cause

**Example Table:**

| Cause | iOS ↓ | Android → | Teens ↓ | Adults → | US ↓ | EU → |
|-------|-------|-----------|---------|----------|------|------|
| iOS bug in latest update | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| School started (US only) | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ |
| Competitor targeted teens | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ |

**Pattern match:** "School started (US)" fits all observations → Most likely cause

**Output of Phase 3:**

```markdown
## Hypothesis Testing Results

**Ruled out:**
- [Hypothesis]: [Why ruled out]
- [Hypothesis]: [Why ruled out]

**Possible causes (remaining):**
1. [Most likely hypothesis]
   - Evidence supporting: [List]
   - Evidence against: [List if any]
   - Confidence: [High/Medium/Low]

2. [Second most likely] (if applicable)
   - Evidence supporting: [List]
   - Confidence: [High/Medium/Low]

**Additional data needed to confirm:**
- [Data point that would differentiate remaining hypotheses]
```

### Phase 4: Assess North Star Impact (10 minutes)

**Use the `north-star-alignment` skill**

Evaluate whether identified root cause impacts company-level metrics:

**Questions:**
- Does this affect North Star metrics?
- Is impact temporary or permanent?
- Does it require immediate action?
- What's the business impact (revenue, growth, retention)?

**Severity classification:**

**Critical (Act immediately):**
- Impacts revenue directly
- Affects North Star metrics substantially
- Permanent degradation if not fixed
- Competitive disadvantage

**Important (Act soon):**
- Impacts user experience
- Affects intermediate metrics
- May worsen over time
- Needs monitoring

**Low Priority (Monitor):**
- Expected variation (seasonality)
- Affects non-critical segments
- Self-resolving
- No action needed

**Output of Phase 4:**

```markdown
## North Star Impact Assessment

**Affected North Star metrics:**
- [Metric]: [Impact description]
- [Metric]: [Impact description]

**Business impact:**
- Revenue: [Direct/Indirect/None]
- Growth: [Slowed/Accelerated/Neutral]
- Retention: [Harmed/Improved/Neutral]

**Severity:** [Critical/Important/Low Priority]

**Urgency:** [Immediate/This week/Monitor]
```

### Phase 5: Recommend Actions (10 minutes)

Based on root cause and severity, recommend next steps:

**Action categories:**

1. **Fix (for bugs/issues)**
   - What needs to be fixed?
   - Who owns the fix?
   - Timeline for fix?

2. **Mitigate (for external factors)**
   - What can reduce harm?
   - Counter-measures available?
   - Timeline for mitigation?

3. **Monitor (for expected variations)**
   - What tracking is needed?
   - Alert thresholds?
   - Review cadence?

4. **No Action (for acceptable changes)**
   - Why no action needed?
   - What validates this decision?

**Output document:**

```markdown
# Metric Diagnosis Report: [Metric Name]

## Executive Summary
[One paragraph: What happened, why, what to do]

## Problem Statement
- **Initial observation:** [Broad statement]
- **Narrowed scope:** [Specific statement with segments]
- **Magnitude:** [Absolute and % change]
- **Timeframe:** [When occurred]

## Root Cause Analysis

### Narrowed Scope (Phase 1)
- **Affected:** [User segments, geography, platforms, time pattern]
- **Unaffected:** [What stayed stable]

### Hypotheses Tested (Phase 2-3)
| Hypothesis | Category | Evidence | Conclusion |
|------------|----------|----------|------------|
| [Name] | Intrinsic/Extrinsic | [Supporting/Contradicting] | Ruled Out/Possible/Likely |

### Identified Root Cause
**Most likely cause:** [Hypothesis name]

**Evidence supporting:**
1. [Data point matching prediction]
2. [Data point matching prediction]
3. [Stakeholder confirmation]

**Confidence level:** [High/Medium/Low]

### North Star Impact (Phase 4)
- **Affected metrics:** [List with impact]
- **Severity:** [Critical/Important/Low]
- **Urgency:** [Immediate/Soon/Monitor]

## Recommended Actions

### Primary action:
**[Fix/Mitigate/Monitor/No Action]**
- What: [Specific action]
- Who: [Owner]
- When: [Timeline]
- Success criteria: [How to know it worked]

### Secondary actions:
- [Action 1]
- [Action 2]

### Monitoring plan:
- Metrics to track: [List]
- Review frequency: [Daily/Weekly]
- Alert thresholds: [When to escalate]

## Appendix
- Hypothesis table: [Detailed]
- Data sources: [Links]
- Stakeholders consulted: [Names/teams]
```

## Common Diagnostic Patterns

### Pattern 1: Seasonal Variation
- **Symptoms:** Recurring pattern (weekly, yearly)
- **Investigation:** Compare to historical same period
- **Action:** Usually monitor, adjust baselines
- **Example:** School year start, holiday season

### Pattern 2: Competitor Impact
- **Symptoms:** Sudden shift, specific demographic
- **Investigation:** Check competitor news, market research
- **Action:** Counter-strategy, feature parity
- **Example:** Competing app launch with targeted marketing

### Pattern 3: Internal Bug
- **Symptoms:** Sudden drop, platform-specific
- **Investigation:** Check recent releases, error logs
- **Action:** Hotfix, rollback if needed
- **Example:** iOS update broke key feature

### Pattern 4: Product Change Side Effect
- **Symptoms:** Gradual shift after release
- **Investigation:** Analyze feature adoption patterns
- **Action:** Iterate on feature, A/B test variations
- **Example:** Redesign changed user behavior

### Pattern 5: Tracking Issue (False Alarm)
- **Symptoms:** Exact numbers, midnight timing, single source
- **Investigation:** Verify data pipeline
- **Action:** Fix tracking, dismiss false alarm
- **Example:** Analytics tag removed in deploy

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Jumping to conclusions without segmentation | Complete Phase 1 (4D segmentation) first |
| Only considering one type of factor | Brainstorm both intrinsic AND extrinsic |
| Accepting first matching hypothesis | Test all hypotheses systematically |
| Skipping data quality check | Always verify data is valid first |
| Not consulting stakeholders | Talk to sales, CS, engineering teams |
| Immediate rollback without diagnosis | Understand cause before acting |

## Success Criteria

Metric diagnosis succeeds when:
- Data quality verified
- Problem narrowed to specific segments (4 dimensions)
- 4-6 hypotheses brainstormed (intrinsic + extrinsic)
- Hypotheses tested against data systematically
- Root cause identified (or top 2-3 candidates with confidence levels)
- North Star impact assessed
- Recommended actions clear with owners and timelines
- Diagnosis document created and shared
- Stakeholders aligned on next steps

## Real-World Example: Microsoft Teams Downloads Drop

### Initial Report
"New app downloads down 50% from last week"

### Phase 1: Narrow Scope (15 min)
**Questions asked:**
- Geography? → "Predominantly US and Europe"
- User type? → "Enterprise customers, not consumers"
- Platform? → "Web and desktop primarily, some mobile"
- Other metrics? → "Usage unchanged (existing users still active)"

**Narrowed statement:**
"Enterprise customer downloads via web/desktop down 50% in US/Europe, starting last week. Existing user engagement unchanged."

### Phase 2: Generate Hypotheses (15 min)

**Intrinsic:**
1. Bug in download flow
2. Recent release broke something
3. A/B test reducing visibility

**Extrinsic:**
4. Marketing promotion ended
5. Competitor launch
6. Economic downturn affecting enterprise spending

**Stakeholder consults:**
- Engineering: No recent releases, no bugs reported
- Marketing: "We were running 50% off for enterprises switching from Slack"
- Sales: No competitor news, pipeline healthy

### Phase 3: Test Hypotheses (20 min)

| Hypothesis | Enterprise | Consumer | US/EU | Usage Same | Downloads Only |
|------------|------------|----------|-------|------------|----------------|
| Bug in flow | ✗ Both | ✗ Both | ✗ All | ? | ✓ |
| Promo ended | ✓ | ✗ | ✓ | ✓ | ✓ |
| Competitor | ✗ Both | ✗ Both | ✗ All | ? | ✓ |

**Pattern match:** "Promotion ended" fits all observations

**Confirmation:** Marketing confirms promotion ended last weekend

### Phase 4: North Star Impact (5 min)
**Root cause:** End of promotional campaign
- Downloads during promo = artificially inflated baseline
- Current downloads = return to normal baseline

**North Star impact:**
- MAU: No impact (existing users unaffected)
- Revenue: No impact (existing customers retained)
- Severity: Low (false alarm, not actual problem)

### Phase 5: Recommended Actions (5 min)

**Primary action: No action needed**
- Not an actual decline, just return to baseline
- Adjust baselines for future comparisons

**Secondary actions:**
- Update dashboards to flag promotional periods
- Establish "normal" baseline for future monitoring
- Document for future reference (prevent false alarms)

**Time to diagnosis: 60 minutes**

## MCP Data Enrichment (Optional)

When MCP data sources are connected, auto-query external systems to supplement or replace manual stakeholder consultation. Skip if tools are unavailable.

### Phase 1 Enhancement: Narrow Scope with Pendo Segments

Instead of only asking stakeholders about which user groups are affected, programmatically compare:

1. **List segments**: `mcp__claude_ai_Pendo__segmentList` (subId: `4818486697721856`) to enumerate available user segments.
2. **Segment comparison**: For each relevant segment, run `mcp__claude_ai_Pendo__activityQuery` (subId: `4818486697721856`, appId for relevant app, entityType matching the metric, segmentId: "{segment_id}", dateRange covering the investigation window) and compare metrics across segments.
3. **People dimension**: Compare enterprise vs. SMB, new vs. existing, power users vs. casual via segment-filtered queries.
4. **Technology dimension**: If platform segments exist, compare web vs. mobile, browser-specific segments.

### Phase 2 Enhancement: Auto-Query Stakeholder Data Sources

Replace or supplement stakeholder interviews with direct data queries:

**Sales perspective (Gong via Databricks)**:
```sql
SELECT ct.name as tracker_name, ct.phrase, SUM(ct.count) as mentions,
       COUNT(DISTINCT ct.call_id) as calls
FROM is_prod.gongio.call_tracker ct
JOIN is_prod.gongio.call c ON CAST(ct.call_id AS STRING) = c.id
WHERE c.started >= DATE_SUB(CURRENT_DATE(), 30)
  AND ct._fivetran_deleted = false
GROUP BY ct.name, ct.phrase
ORDER BY mentions DESC
LIMIT 20
```

**Customer Success perspective (Zendesk via Databricks)**:
```sql
SELECT DATE(created_at) as day, COUNT(*) as tickets,
       SUM(CASE WHEN priority IN ('urgent', 'high') THEN 1 ELSE 0 END) as high_priority,
       SUM(CASE WHEN custom_sentiment = 'negative' THEN 1 ELSE 0 END) as negative_sentiment
FROM is_prod.zendesk.ticket
WHERE created_at >= DATE_SUB(CURRENT_DATE(), 30)
GROUP BY DATE(created_at)
ORDER BY day
```

Also check for Pendo Listen churn/frustration signals:
- `mcp__claude_ai_Pendo__get_feedback_items` with `alerts`: ["Churn Risk", "High Frustration"] for the investigation period.

**Engineering perspective (Azure DevOps via Databricks)**:
```sql
SELECT title, state, changed_date
FROM is_prod.azure_devops.work_item
WHERE changed_date >= DATE_SUB(CURRENT_DATE(), 14)
  AND state IN ('Closed', 'Resolved', 'Done')
ORDER BY changed_date DESC
LIMIT 30
```

**UX investigation (Pendo Session Replays)**:
Use `mcp__claude_ai_Pendo__sessionReplayList` (subId: `4818486697721856`, startDate/endDate covering the metric change period) with frustration type filtering to find sessions showing user struggle:
- `frustrationTypes`: [{"frustrationType": "rageClick", "fact": "occurred"}, {"frustrationType": "errorClick", "fact": "occurred"}]

### Mapping MCP Findings to Hypothesis Table

| MCP Source | Maps To | Hypothesis Type |
|------------|---------|-----------------|
| Pendo segment comparison | People/Technology narrowing | Scope refinement |
| Azure DevOps releases | Recent code changes | Internal (intrinsic) |
| Gong tracker mentions | Competitive shifts | External (extrinsic) |
| Zendesk ticket spikes | Customer-reported issues | Internal or external |
| Pendo session replays | UX degradation | Internal (intrinsic) |
| Pendo Listen alerts | Acute customer pain | Corroborating evidence |

## Related Skills

This workflow orchestrates these skills:
- **root-cause-diagnosis** (Phases 1-3) - Core investigation method
- **north-star-alignment** (Phase 4) - Assess strategic impact

## Related Workflows

- **tradeoff-decision**: May use diagnosis to understand why metrics changed before deciding
- **metrics-definition**: Uses similar systematic approach for defining vs. diagnosing

## Time Estimate

**Total: 60-90 minutes**
- Phase 0 (Data quality): 5 min
- Phase 1 (Narrow scope): 15-20 min
- Phase 2 (Hypotheses): 15-20 min
- Phase 3 (Test): 20-30 min
- Phase 4 (Impact): 10 min
- Phase 5 (Actions): 10 min

For complex issues, may require multiple iterations or longer investigation time.

