---
name: context-pendo-analytics
description: Use when pulling Pendo product analytics data for prioritization, decision-making, or feature analysis - connects to Pendo MCP server to query page/feature usage, visitor behavior, segment data, customer feedback (Listen), session replays, and AI agent analytics for Vantaca products
allowed-tools: Read, Grep, Glob, Bash
---

# Pendo Analytics

## Purpose

Pull Pendo product analytics data into PM workflows:
- Query feature and page usage for prioritization decisions
- Analyze visitor/account behavior patterns
- Retrieve segment definitions and membership data
- Surface customer feedback and AI-extracted insights via Pendo Listen
- Investigate UX issues through session replays with frustration filtering
- Monitor AI agent performance (HOAi, Vantaca IQ)
- Support data-driven product decisions with real usage evidence
- Provide analytics context for strategy sessions, PRDs, and roadmap reviews

## When to Use This Skill

Activate automatically when:
- Prioritizing features and need usage data to support decisions
- Writing PRDs that require current adoption/engagement metrics
- Preparing for strategy sessions that need product usage evidence
- Investigating feature performance or adoption trends
- Building business cases with quantitative product data
- Comparing feature usage across segments or accounts
- Gathering customer feedback or sentiment for a product area
- Investigating UX friction through session replay frustration signals
- Monitoring HOAi or Vantaca IQ agent performance and conversation patterns

## Prerequisites

### Vantaca Pendo Connection

MCP is already configured. Authentication is handled via OAuth through Pendo login.

**Subscription**: Vantaca
**subId** (required on every MCP call): `4818486697721856`

**Applications:**

| App | appId | Notes |
|-----|-------|-------|
| Vantaca IQ | `-323232` |  |
| Vantaca Manage | `5412977898749952` | |
| Vantaca Home | `5961191088521216` | Default app; use when no specific app is specified |
| HOAi | `6037667364143104` | AI agent app |
| Vantaca Core | `6243085483048960` | |

**Critical**: All `mcp__claude_ai_Pendo__*` tool calls require `subId: "4818486697721856"` as a parameter. Most also require `appId` -- default to `-323232` (Vantaca IQ) unless the query targets a specific app.

### Admin Requirements
- A Pendo subscription admin must enable the MCP server in Pendo settings
- You need a Pendo account with appropriate data access permissions

## Available MCP Tools

All tools are prefixed with `mcp__claude_ai_Pendo__`. Every call must include `subId: "4818486697721856"`.

### Usage Analytics

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `activityQuery` | Page/feature/visitor/account usage data | `appId`, date range, grouping, sorting, segment filtering |
| `productEngagementScore` | PES score (adoption + stickiness + growth) | `appId` |
| `searchEntities` | Semantic search for pages, features, guides, accounts | `appId`, search query |

### Account & Visitor Data

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `accountQuery` | Query account-level data and metadata | `appId`, filters |
| `visitorQuery` | Query visitor-level data and metadata | `appId`, filters |
| `accountMetadataSchema` | Get account metadata field definitions | `appId` |
| `visitorMetadataSchema` | Get visitor metadata field definitions | `appId` |

### Segments

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `segmentList` | List available segments and definitions | `appId` |

### Guides

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `guideMetrics` | Guide reach, engagement, completion rates | `appId` |

### Session Replays

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sessionReplayList` | Browse session recordings with frustration filtering | `appId`, duration, activity filters, frustration types |

**Frustration types**: `rageClick`, `errorClick`, `deadClick`, `uTurn`, `overGuidance`, `detractorNps`

### Pendo Listen (Customer Feedback)

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `get_feedback_items` | Raw customer feedback entries (max 30 per call) | Filters below |
| `get_feedback_insights` | AI-extracted actionable insights with supporting quotes | Filters below |
| `generate_feedback_topics` | AI-clustered topic themes with counts | Filters below |
| `get_ideas` | Internal product ideas | Filters below |

**Listen filter options:**
- `accountTypes`: Customer, Prospect, Churned
- `feedbackTypes`: Product Enhancement Request, Product Issues, Pain Point, Positive Product Feedback, Competitor Weakness, Competitor Strength
- `alerts`: Churn Risk, High Frustration, Blocker to Sale
- `exactMatchSearchTerms`: exact string matching
- `similaritySearchTerms`: semantic/fuzzy matching
- `productAreaIds`: filter by product area
- `segmentId`: filter by Pendo segment
- Date range filters

### AI Agent Analytics

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `list_ai_agents` | List agents (get IDs and names) | `subId` |
| `agent_analytics_key_metrics` | Conversations, visitors, accounts, rage prompts, retention | Agent ID, period comparison (max 90 days) |
| `list_use_cases` | Conversation clustering analysis (topics, metrics per cluster) | Agent ID |
| `list_ai_agent_issues` | Detected issues with instance/conversation counts | Agent ID |

Useful for monitoring HOAi and Vantaca IQ agent performance, identifying common user intents, and surfacing agent issues.

## Querying Patterns

### Pattern 1: Feature Adoption Check

**Use case:** "How many users are using Feature X?"

**Query approach:**
1. Use `searchEntities` to find the feature by name (pass `subId`, `appId`)
2. Use `activityQuery` with the feature ID and date range to get usage counts
3. Calculate adoption rate (unique users / total active users)

**Output format:**
```markdown
## Feature Usage: {Feature Name}
- **Period**: {start_date} to {end_date}
- **Unique visitors**: {count}
- **Total clicks**: {count}
- **Adoption rate**: {percentage} of active visitors
- **Trend**: {increasing/decreasing/stable} vs prior period
```

### Pattern 2: Page Engagement Analysis

**Use case:** "Which pages get the most/least traffic?"

**Query approach:**
1. Use `activityQuery` with page-level grouping across all pages (pass `subId`, `appId`)
2. Sort by visitor count or view count
3. Identify top and bottom performers

**Output format:**
```markdown
## Page Engagement Summary
| Page | Unique Visitors | Views | Avg Views/Visitor |
|------|----------------|-------|-------------------|
| {name} | {count} | {count} | {ratio} |
```

### Pattern 3: Segment Comparison

**Use case:** "How does usage differ between Enterprise and SMB accounts?"

**Query approach:**
1. Use `segmentList` to retrieve segment definitions (pass `subId`, `appId`)
2. Use `activityQuery` with segment filtering for each segment
3. Compare metrics across segments

**Output format:**
```markdown
## Segment Comparison: {Feature/Page}
| Metric | {Segment A} | {Segment B} | Delta |
|--------|-------------|-------------|-------|
| Active users | {count} | {count} | {diff} |
| Usage frequency | {rate} | {rate} | {diff} |
```

### Pattern 4: Prioritization Data Pull

**Use case:** "I need usage data to prioritize these 5 features"

**Query approach:**
1. For each feature/area, use `activityQuery` to get page and feature usage (pass `subId`, `appId`)
2. Use `productEngagementScore` for overall engagement context
3. Cross-reference with `segmentList` data if available
4. Format for prioritization framework input

**Output format:**
```markdown
## Prioritization Data
| Feature Area | Monthly Active Users | Adoption % | Trend (30d) | Top Segment |
|-------------|---------------------|------------|-------------|-------------|
| {name} | {count} | {pct} | {direction} | {segment} |
```

### Pattern 5: Pendo Listen Feedback Query

**Use case:** "What are customers saying about invoicing?" or "What feedback themes are emerging?"

**Query approach:**
1. Start with `get_feedback_insights` for a quick AI-summarized overview (pass `subId` and relevant filters)
2. Use `generate_feedback_topics` to see thematic clustering with counts
3. Drill into `get_feedback_items` for raw feedback with specific filters

**Example with filters:**
```
get_feedback_insights:
  subId: "4818486697721856"
  similaritySearchTerms: "invoicing payments billing"
  accountTypes: ["Customer"]
  feedbackTypes: ["Product Enhancement Request", "Pain Point"]
  alerts: ["High Frustration"]
```

**Output format:**
```markdown
## Feedback Summary: {Topic}
- **Insights**: {count} actionable insights extracted
- **Top themes**: {theme 1} ({count}), {theme 2} ({count}), ...
- **Key quotes**: "{verbatim quote}" -- {account name}
- **Alerts**: {Churn Risk: N, High Frustration: N, Blocker to Sale: N}
```

### Pattern 6: Native Mobile App Usage (Vantaca Home)

**Use case:** "How many users are on the native Android/iOS app?" or "What's our mobile app adoption?"

**Background:** Vantaca Home (`5961191088521216`) serves both web and native mobile app traffic under a single Pendo app ID. There are no separate app IDs for iOS/Android. Native app users are identified by mobile-specific visitor metadata fields set by the native SDK at login.

**Key metadata fields (all in `metadata.agent.*`):**

| Field | Type | Purpose |
|-------|------|---------|
| `mobilewhitelabelid` | string | White-label brand (e.g., `vantaca-home`, `cma-home`, `alliant-association-management`, `cadden-connect`, `ips-portal`) |
| `mobileplatformos` | string | **Lowercase** values: `"android"`, `"ios"` |
| `mobiledevicetype` | string | Device type |
| `mobileappversion` | string | App version |
| `mobilebuildnumber` | integer | Build number (numeric — critical for activity query filtering) |
| `mobileplatformversion` | string | OS version |

These same fields also exist under `metadata.custom.*` as mirrors.

**Critical gotchas:**

| Gotcha | Details |
|--------|---------|
| Values are **lowercase** | `mobileplatformos` is `"android"` / `"ios"`, NOT `"Android"` / `"iOS"`. The auto-detected `lastoperatingsystem` uses title case, but the native SDK fields use lowercase. |
| `!= ""` matches nulls | `null != ""` evaluates true in Pendo. Use `> ""` to find "field is populated and non-empty". |
| `activityQuery` only supports numeric metadata filters | `visitorMetadataFilter` in `activityQuery` cannot filter on strings. Use `metadata.agent.mobilebuildnumber > 0` as a numeric proxy — it is always set alongside the string fields for native sessions. |
| `visitorQuery` supports string metadata filters | `metadataFilter` in `visitorQuery` handles string comparisons fine (e.g., `metadata.agent.mobileplatformos == "android"`). |
| `lastoperatingsystem` ≠ native app | `metadata.auto.lastoperatingsystem == "Android"` catches native AND mobile web users. It also reflects the visitor's most recent OS, not necessarily the OS used during the queried period. |

**Query approach — Visitor counts (all-time or with metadata filters):**
```
visitorQuery:
  subId: "4818486697721856"
  appId: "5961191088521216"
  count: true
  metadataFilter: 'metadata.agent.mobileplatformos == "android"'
```

**Query approach — Active visitors in a date range (use numeric proxy):**
```
activityQuery:
  entityType: visitor
  subId: "4818486697721856"
  appId: "5961191088521216"
  dateRange: { range: relative, lastNDays: 7 }
  group: [visitorId]
  count: true
  visitorMetadataFilter: 'metadata.agent.mobilebuildnumber > 0'
```

To split by platform in activity queries, combine the numeric proxy with `lastoperatingsystem` (imperfect but closest available):
```
visitorMetadataFilter: 'metadata.agent.mobilebuildnumber > 0 && metadata.auto.lastoperatingsystem == "Android"'
```

Note: this undercounts because visitors who also used web will show their last OS, not their mobile OS.

**Query approach — Sample visitors with metadata details:**
```
visitorQuery:
  subId: "4818486697721856"
  appId: "5961191088521216"
  count: false
  limit: 50
  select: [metadata.agent.mobileplatformos, metadata.agent.mobilewhitelabelid, metadata.agent.mobileappversion]
  metadataFilter: 'metadata.agent.mobilewhitelabelid > "" && metadata.agent.mobileplatformos > ""'
```

**Output format:**
```markdown
## Native Mobile App Usage: Vantaca Home
- **Period**: {start_date} to {end_date}
- **Total native app visitors**: {count} (mobilebuildnumber > 0)
- **Android**: {count}
- **iOS**: {count}
- **White-label breakdown**: vantaca-home ({n}), cma-home ({n}), ...
- **Note**: All native mobile traffic routes through the Vantaca Home app ID; no other Pendo apps capture mobile metadata.
```

### Pattern 7: Session Replay Investigation

**Use case:** "Users are struggling with the new workflow -- show me what's happening"

**Query approach:**
1. Use `sessionReplayList` with frustration type filtering (pass `subId`, `appId`)
2. Filter by relevant frustration signals: `rageClick`, `deadClick`, `uTurn`, `errorClick`
3. Review session metadata for patterns (duration, pages visited, frustration density)

**Output format:**
```markdown
## Session Replay Analysis: {Area}
- **Sessions reviewed**: {count}
- **Common frustration signals**: {type 1} ({count}), {type 2} ({count})
- **Pages with highest friction**: {page 1}, {page 2}
- **Pattern**: {description of observed UX issue}
```

## Integration with PM Workflows

### With PRD Creation (`prd-creation` skill)
- Pull current usage data for the problem area via `activityQuery`
- Quantify the opportunity with visitor/account counts
- Identify which segments are most affected via segment-filtered queries

### With Product Strategy (`product-strategy-creation` skill)
- Provide quantitative evidence for investment area selection
- Support market context with adoption and engagement data
- Ground roadmap decisions in actual usage patterns

### With Priority Scoring (`priority-scoring` skill)
- Feed adoption rates into impact scoring
- Use segment data for reach estimation
- Provide trend data for urgency assessment

### With Metrics Definition (`metrics-definition` workflow)
- Identify baseline metrics from current usage via `activityQuery`
- Map existing Pendo events to proposed success metrics via `searchEntities`
- Validate that proposed metrics are actually measurable in Pendo

### With Strategy Sessions (`strategy-session` skill)
- Provide quantitative context for strategic decisions
- Compare feature performance across customer segments
- Support competitive analysis with product usage evidence

### With CS Prep (`cs-prep` skill)
- Pull account-level usage via `accountQuery` for QBR briefs
- Surface account-specific feedback from Pendo Listen via `get_feedback_items`
- Check `productEngagementScore` for the account's app engagement

### With Metric Diagnosis (`metric-diagnosis` workflow)
- Segment-level usage data via `activityQuery` for root cause investigation
- Session replays via `sessionReplayList` with frustration filtering for UX causes
- Pendo Listen feedback to correlate qualitative signals with metric movements

### With Root Cause Diagnosis (`root-cause-diagnosis` skill)
- Frustration signals from `sessionReplayList` (rage clicks, dead clicks, u-turns)
- Segment comparisons via `activityQuery` to isolate affected cohorts
- AI agent issue detection via `list_ai_agent_issues` for HOAi/IQ-related metric changes

## REST API Fallback

If MCP is unavailable, the Pendo REST API is accessible at `https://app.pendo.io/api/v1/` with an integration key passed as `x-pendo-integration-key` header. Key endpoints: `/aggregation`, `/feature`, `/page`, `/guide`, `/segment`.

## Output Guidelines

When presenting Pendo data in PM workflows:

1. **Always state the time period** -- "In the last 30 days" not just raw numbers
2. **Include trends** -- Compare to prior period when possible
3. **Segment when relevant** -- Break down by customer segment if it matters for the decision
4. **Cite the source** -- "Per Pendo analytics, {date range}" for auditability
5. **Contextualize** -- Raw numbers without context are not useful; calculate rates, percentages, and comparisons
6. **Flag data gaps** -- If a feature is not instrumented in Pendo, say so explicitly
7. **Specify the app** -- When reporting cross-app data, always note which Vantaca app the data comes from

## Error Handling

| Scenario | Action |
|----------|--------|
| MCP not configured | Inform user, offer REST API fallback |
| Authentication failed | Guide user to re-authenticate via `/mcp` |
| Feature/page not found | Use `searchEntities` to list available features/pages |
| No data for time period | Expand time range or note that the feature may not be instrumented |
| Rate limiting | Wait and retry; inform user if persistent |
| Wrong appId | List available apps (see table above) and confirm with user |

## Success Criteria

Pendo analytics query complete when:
- Requested data retrieved and formatted
- Time period clearly stated
- App identified (Vantaca IQ, Manage, Home, HOAi, or Core)
- Trends calculated where applicable
- Data contextualized for the PM decision at hand
- Sources cited for audit trail
- Data gaps or limitations flagged

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Presenting raw counts without context | Calculate rates, percentages, and comparisons |
| Missing time period | Always state the date range |
| Ignoring segments | Break down by relevant segments when available |
| Treating absence of data as zero usage | Feature may not be instrumented -- flag this |
| Not connecting data to the decision | Frame analytics in terms of the PM question being answered |
| Omitting subId from MCP calls | Every call requires `subId: "4818486697721856"` |
| Using wrong appId | Default to `-323232` (Vantaca IQ); confirm app if query targets Manage, Home, HOAi, or Core |
| Mixing app data without labeling | Always note which app the data comes from |
| Using `"Android"` / `"iOS"` for native SDK fields | Native SDK fields (`mobileplatformos`) use lowercase: `"android"`, `"ios"`. Only `auto.lastoperatingsystem` uses title case. |
| Using `!= ""` to find populated fields | `null != ""` is true in Pendo. Use `> ""` instead. |
| Using string filters in `activityQuery.visitorMetadataFilter` | Only numeric comparisons work. Use `mobilebuildnumber > 0` as a proxy for native app users. |
| Confusing `lastoperatingsystem` with native app usage | `lastoperatingsystem == "Android"` includes mobile web browsers, not just native app users. Use `mobilebuildnumber > 0` for true native app filtering. |

## Related Skills

- **priority-scoring**: Consumes Pendo data for impact/reach scoring
- **research-gathering**: Pendo data can supplement research context
- **product-strategy-creation**: Uses Pendo data for evidence-based strategy
- **metrics-definition**: Maps Pendo events to success metrics
- **north-star-alignment**: Connects Pendo metrics to company mission
- **databricks-analytics**: Complements Pendo with Gong, Zendesk, and Azure DevOps data from the warehouse
