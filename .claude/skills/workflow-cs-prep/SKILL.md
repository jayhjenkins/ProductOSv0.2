---
name: workflow-cs-prep
description: Use when preparing customer success materials (QBR briefs) - synthesizes customer-specific meeting history, extracts signals, quotes, and pain points for strategic discussions
---

# CS Prep

## Purpose

Compile customer context for QBR or strategic CS meetings:
- Customer-specific meeting history
- Signal synthesis (asks, problems, wins)
- Key quotes and testimonials
- Pain points and friction areas
- Feature request timeline

## When to Use

Activate when:
- User invokes `/project:cs-prep`
- Preparing for QBR
- Customer check-in planning

## Workflow

### 1. Determine Customer and Time Window

**Inputs:**
- `customer`: Customer name (required)
- `days`: Lookback window (default: 90 for QBRs)

### 2. Synthesize Customer Meetings

**Invoke:** `meeting-synthesis` skill

**Inputs:**
- include_customers: {specified customer only}
- Time window: {days}
- No thresholds (include all signals for this customer)

**Outputs:**
- All signals from this customer
- Chronological meeting list
- Verbatim quotes

### 2b. MCP Data Enrichment (Optional)

After synthesizing customer meetings, optionally enrich with live external data for a comprehensive QBR brief. Skip if MCP tools are unavailable.

#### Pendo Account Usage

Pull product usage data for the specific customer account:

1. **Account identification**: Use `mcp__claude_ai_Pendo__searchEntities` (subId: `4818486697721856`, appId: `-323232`, itemType: ["Account"], search: "{customer_name}", search_fallback: ["{customer_name}"]) to find the account and get its ID.

2. **Account metadata**: Use `mcp__claude_ai_Pendo__accountQuery` (subId: `4818486697721856`, accountId: "{account_id}", select: [relevant metadata fields from `accountMetadataSchema`]) to pull account-level properties like ARR, plan tier, etc.

3. **Account activity**: Use `mcp__claude_ai_Pendo__activityQuery` (subId: `4818486697721856`, appId: "-323232", entityType: "account", accountId: "{account_id}", dateRange: {range: "relative", lastNDays: 90}) for usage metrics (events, minutes, unique visitors).

4. **Feature adoption**: Use `mcp__claude_ai_Pendo__activityQuery` with entityType: "feature", accountId: "{account_id}", group: ["featureId"], sort: ["-numEvents"] to see which features the customer uses most/least.

#### Pendo Account Feedback

Use `mcp__claude_ai_Pendo__get_feedback_items` (subId: `4818486697721856`, filters: {accountIds: ["{account_id}"]}) to surface feedback the customer has submitted through Pendo Listen. Also check `mcp__claude_ai_Pendo__get_feedback_insights` with the same filter for AI-extracted insights.

#### Zendesk Ticket History (via Databricks)

```sql
SELECT t.id, t.subject, t.status, t.priority, t.custom_product_field,
       t.custom_intent, t.custom_sentiment, t.created_at, t.updated_at
FROM is_prod.zendesk.ticket t
JOIN is_prod.zendesk.organization o ON t.organization_id = o.id
WHERE LOWER(o.name) LIKE LOWER('%{customer_name}%')
  AND t.created_at >= DATE_SUB(CURRENT_DATE(), {days})
ORDER BY t.created_at DESC
LIMIT 50
```

Also pull CSAT for the customer:
```sql
SELECT sr.score, sr.created_at, t.subject
FROM is_prod.zendesk.satisfaction_rating sr
JOIN is_prod.zendesk.ticket t ON sr.ticket_id = t.id
JOIN is_prod.zendesk.organization o ON t.organization_id = o.id
WHERE LOWER(o.name) LIKE LOWER('%{customer_name}%')
  AND sr.created_at >= DATE_SUB(CURRENT_DATE(), {days})
ORDER BY sr.created_at DESC
```

#### Gong Call Summaries (via Databricks)

```sql
SELECT c.id, c.title, c.started, c.brief, c.duration,
       c.call_outcome_category, c.call_outcome_name
FROM is_prod.gongio.call c
WHERE LOWER(c.title) LIKE LOWER('%{customer_name}%')
  AND c.started >= DATE_SUB(CURRENT_DATE(), {days})
  AND c._fivetran_deleted = false
ORDER BY c.started DESC
```

For key points from those calls:
```sql
SELECT c.title, c.started, ckp.text as key_point
FROM is_prod.gongio.call c
JOIN is_prod.gongio.call_key_point ckp ON c.id = ckp.call_id
WHERE LOWER(c.title) LIKE LOWER('%{customer_name}%')
  AND c.started >= DATE_SUB(CURRENT_DATE(), {days})
  AND c._fivetran_deleted = false
ORDER BY c.started DESC
```

#### QBR Brief Template Additions

When MCP data is available, add these sections to the QBR brief output:

```markdown
## Product Usage (Pendo)
- **Active users (90d)**: {unique_visitors} across {apps_used} apps
- **Top features**: {top_3_features_by_usage}
- **Engagement trend**: {increasing/decreasing/stable} vs prior period
- **PES score**: {score} (Adoption: {a}, Stickiness: {s}, Growth: {g})

## Customer Feedback (Pendo Listen)
- **Feedback submitted**: {count} items in the last {days} days
- **Key themes**: {top_feedback_topics}
- **Alerts**: {churn_risk/high_frustration flags if any}

## Support History (Zendesk)
- **Tickets (90d)**: {total_count} ({open_count} open, {high_priority_count} high/urgent)
- **Top issues**: {top_3_product_fields_by_volume}
- **CSAT**: {avg_score} ({trend} vs prior period)
- **Escalations**: {escalated_count}

## Sales Call Insights (Gong)
- **Recent calls**: {call_count} in the last {days} days
- **Key themes**: {top_key_points_summarized}
- **Outcome trends**: {outcome_categories}
```

### 3. Organize by Category

**Group signals:**
- **Wins**: Positive feedback, success stories
- **Pain Points**: Friction, challenges, blockers
- **Feature Requests**: Asks for new capabilities
- **Onboarding/Setup**: Implementation challenges
- **Performance/Scale**: Technical concerns

### 4. Extract Key Quotes

**For each category:**
- Select 2-3 most impactful quotes
- Include speaker, date, context

### 5. Build Timeline

**Feature request timeline:**
```
2025-08-15: Requested Google Sheets export
2025-09-02: Asked about real-time sync
2025-10-10: Followed up on export feature
```

### 6. Generate CS Brief

**Output:** `datasets/product/customer-briefs/{Customer}_{YYYYMMDD}_qbr.md`

**Format:**
```markdown
# QBR Brief: {Customer}

**Date**: {YYYY-MM-DD}
**Time Window**: Last {N} days
**Meetings Reviewed**: {N}

## Wins
- {Quote/signal 1}
- {Quote/signal 2}

## Pain Points
- {Quote/signal 1}
- {Quote/signal 2}

## Feature Requests
- {Request 1} (mentioned {N} times)
- {Request 2} (mentioned {N} times)

## Timeline of Key Events
- {Date}: {Event}
- {Date}: {Event}

## Recommended Discussion Topics
1. {Topic 1}
2. {Topic 2}
```

## Success Criteria

- Customer-specific signals synthesized
- Quotes extracted and categorized
- Timeline of requests built
- CS brief written to customer-briefs/

## Related Skills

- `meeting-synthesis`: Extracts customer signals
- `product-planning`: Uses similar synthesis logic
