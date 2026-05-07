---
name: context-databricks-analytics
description: Query Gong sales calls, Zendesk support tickets, and Azure DevOps work items via Databricks SQL — use when gathering support/sales/engineering data for PM workflows
allowed-tools: mcp__claude_ai_VantacaDatabricks__execute_sql_read_only, mcp__claude_ai_VantacaDatabricks__execute_sql, mcp__claude_ai_VantacaDatabricks__poll_sql_result
---

## Purpose

Query the Vantaca data warehouse for support tickets, sales call analysis, and engineering data to enrich PM workflows with live external data.

## When to Use This Skill

- Investigating support ticket patterns for a customer or product area
- Analyzing sales call themes, trackers, or competitive mentions from Gong
- Checking recent engineering releases/deploys from Azure DevOps
- Enriching CS prep, strategy sessions, metric diagnosis, or PRDs with quantitative evidence
- Validating meeting signals against support/sales data

## Connection Details

- **MCP Tool**: `mcp__claude_ai_VantacaDatabricks__execute_sql_read_only` (prefer for all reads)
- **Catalog**: `is_prod`
- **Syntax**: Databricks SQL (DBSQL). Always use fully qualified names: `is_prod.schema.table`
- For long-running queries, tool returns a `statement_id` — poll with `mcp__claude_ai_VantacaDatabricks__poll_sql_result`

## Available Schemas

### Gong (`is_prod.gongio`)

Sales/CS call recordings, transcripts, and analytics.

| Table | Key Columns | Use For |
|-------|-------------|---------|
| `call` | id, title, started, duration, purpose, brief, direction, call_outcome_category, call_outcome_name, company_question_count, non_company_question_count | Call metadata, summaries, outcomes |
| `transcript` | call_id, speaker_id, topic, sentence | Full call transcripts by speaker |
| `call_key_point` | call_id, text | AI-extracted key points |
| `call_tracker` | call_id, phrase, name, count, type, speaker_id | Tracked keyword/phrase mentions |
| `call_topic` | call_id (+ topic fields) | Topics discussed |
| `call_highlight` / `call_highlight_item` | call_id | Notable moments |
| `call_interaction` | call_id | Interaction patterns |
| `call_participant` | call_id, name fields | Who was on the call |
| `call_speaker` | call_id | Speaker identification |
| `call_outline` / `call_outline_item` | call_id | Call structure/agenda |
| `scorecard` / `scorecard_question` / `answered_scorecard` / `answered_scorecard_answer` | Scorecard evaluation data |
| `users` | Gong user info |
| `tracker` / `tracker_language` / `language_keywords` | Tracker definitions |

### Zendesk (`is_prod.zendesk`)

Support tickets, CSAT, organizations.

| Table | Key Columns | Use For |
|-------|-------------|---------|
| `ticket` | id, subject, description, status, priority, type, created_at, updated_at, custom_product_field, custom_intent, custom_sentiment, custom_hoai_root_cause, custom_confirmed_bug, custom_escalated_client, custom_management_company_id, custom_sme_team, custom_platform, organization_id, requester_id, assignee_id, group_id | Core ticket data with rich custom fields |
| `ticket_comment` | ticket_id, body | Ticket conversation threads |
| `ticket_tag` | ticket_id, tag | Ticket categorization |
| `satisfaction_rating` | ticket_id, score, created_at | CSAT survey responses |
| `organization` | id, name | Customer/organization mapping |
| `ticket_custom_field` | ticket_id, field values | Additional custom fields |
| `csat_survey_answer` / `csat_survey_question` | CSAT survey details |

### Zendesk Modeled (`is_prod.zendesk_zendesk`)

Pre-built analytics models from Fivetran.

| Table | Use For |
|-------|---------|
| `zendesk__ticket_enriched` | Enriched ticket data with joins pre-computed |
| `zendesk__ticket_metrics` | Resolution times, reply times, reopen counts |
| `zendesk__ticket_summary` | Aggregated ticket statistics |
| `zendesk__ticket_backlog` | Current open ticket backlog |

### Azure DevOps (`is_prod.azure_devops`)

Engineering work items, PRs, commits.

| Table | Key Columns | Use For |
|-------|-------------|---------|
| `work_item` | id, title, state, changed_date, type | Stories, bugs, tasks, epics |
| `work_item_revision` | work_item_id, revision history | State change tracking |
| `pull_request` | id, title, status, created_date | PR activity |
| `backlog` / `backlog_work_item` | Backlog structure |
| `commit` | id, message, author, date | Code commits |
| `board` / `board_column` | Board structure |

## SQL Query Templates

### Pattern 1: Support Ticket Analysis by Product Area

```sql
SELECT
  custom_product_field,
  COUNT(*) as ticket_count,
  SUM(CASE WHEN priority = 'urgent' OR priority = 'high' THEN 1 ELSE 0 END) as high_priority,
  SUM(CASE WHEN custom_confirmed_bug = true THEN 1 ELSE 0 END) as confirmed_bugs,
  SUM(CASE WHEN custom_escalated_client = true THEN 1 ELSE 0 END) as escalated
FROM is_prod.zendesk.ticket
WHERE created_at >= DATE_SUB(CURRENT_DATE(), {days})
  AND custom_product_field IS NOT NULL
GROUP BY custom_product_field
ORDER BY ticket_count DESC
```

### Pattern 2: Customer-Specific Ticket History

```sql
SELECT t.id, t.subject, t.status, t.priority, t.custom_product_field,
       t.custom_intent, t.custom_sentiment, t.created_at
FROM is_prod.zendesk.ticket t
JOIN is_prod.zendesk.organization o ON t.organization_id = o.id
WHERE LOWER(o.name) LIKE LOWER('%{customer_name}%')
  AND t.created_at >= DATE_SUB(CURRENT_DATE(), {days})
ORDER BY t.created_at DESC
LIMIT 50
```

### Pattern 3: Zendesk Ticket Volume Trends (Daily)

```sql
SELECT DATE(created_at) as day, COUNT(*) as tickets,
       SUM(CASE WHEN custom_sentiment = 'negative' THEN 1 ELSE 0 END) as negative
FROM is_prod.zendesk.ticket
WHERE created_at >= DATE_SUB(CURRENT_DATE(), {days})
GROUP BY DATE(created_at)
ORDER BY day
```

### Pattern 4: CSAT Score Trends

```sql
SELECT DATE_TRUNC('month', sr.created_at) as month,
       COUNT(*) as responses,
       AVG(CAST(sr.score AS DOUBLE)) as avg_score
FROM is_prod.zendesk.satisfaction_rating sr
WHERE sr.created_at >= DATE_SUB(CURRENT_DATE(), 365)
GROUP BY DATE_TRUNC('month', sr.created_at)
ORDER BY month
```

### Pattern 5: Gong Call Key Points (Recent)

```sql
SELECT c.id, c.title, c.started, c.brief, c.purpose,
       c.call_outcome_category, ckp.text as key_point
FROM is_prod.gongio.call c
JOIN is_prod.gongio.call_key_point ckp ON c.id = ckp.call_id
WHERE c.started >= DATE_SUB(CURRENT_DATE(), {days})
  AND c._fivetran_deleted = false
ORDER BY c.started DESC
LIMIT 100
```

### Pattern 6: Gong Tracker Mentions (Competitive/Topic Analysis)

```sql
SELECT ct.name as tracker_name, ct.phrase,
       SUM(ct.count) as total_mentions,
       COUNT(DISTINCT ct.call_id) as calls_mentioned
FROM is_prod.gongio.call_tracker ct
JOIN is_prod.gongio.call c ON CAST(ct.call_id AS STRING) = c.id
WHERE c.started >= DATE_SUB(CURRENT_DATE(), {days})
  AND ct._fivetran_deleted = false
GROUP BY ct.name, ct.phrase
ORDER BY total_mentions DESC
LIMIT 30
```

### Pattern 7: Gong Calls for a Customer

```sql
SELECT c.id, c.title, c.started, c.brief, c.duration,
       c.call_outcome_category, c.call_outcome_name
FROM is_prod.gongio.call c
JOIN is_prod.gongio.call_participant cp ON c.id = cp.call_id
WHERE LOWER(cp.name) LIKE LOWER('%{customer_name}%')
  AND c.started >= DATE_SUB(CURRENT_DATE(), {days})
  AND c._fivetran_deleted = false
ORDER BY c.started DESC
```

### Pattern 8: Recent Azure DevOps Releases

```sql
SELECT title, state, changed_date
FROM is_prod.azure_devops.work_item
WHERE changed_date >= DATE_SUB(CURRENT_DATE(), {days})
  AND state IN ('Closed', 'Resolved', 'Done')
ORDER BY changed_date DESC
LIMIT 50
```

### Pattern 9: Zendesk Intent/Sentiment Distribution

```sql
SELECT custom_intent, custom_sentiment, COUNT(*) as count
FROM is_prod.zendesk.ticket
WHERE created_at >= DATE_SUB(CURRENT_DATE(), {days})
  AND custom_intent IS NOT NULL
GROUP BY custom_intent, custom_sentiment
ORDER BY count DESC
LIMIT 30
```

## Integration with PM Workflows

### With CS Prep (`cs-prep` skill)

- Pull customer-specific ticket history (Pattern 2) and Gong calls (Pattern 7)
- Include ticket volume, top issues, and CSAT in QBR briefs

### With Meeting Synthesis (`meeting-synthesis` skill)

- Cross-reference meeting signals with Zendesk ticket patterns (Pattern 1)
- Supplement signal frequency with Gong tracker mentions (Pattern 6)

### With Metric Diagnosis (`metric-diagnosis` workflow)

- Check Zendesk ticket volume trends for spikes (Pattern 3) correlating with metric changes
- Query Azure DevOps for recent releases (Pattern 8) as potential causes
- Check Gong trackers for competitive mentions (Pattern 6)

### With Strategy Sessions (`strategy-session` skill)

- Zendesk intent/sentiment distribution (Pattern 9) for market context
- Gong tracker analysis (Pattern 6) for competitive intelligence

### With Product Strategy (`product-strategy-creation` skill)

- Ticket volume by product area (Pattern 1) for problem evidence
- CSAT trends (Pattern 4) for customer satisfaction context

### With Priority Scoring (`priority-scoring` skill)

- Ticket volume by product area supplements SignalStrength scoring
- Gong mention frequency validates feature demand

### With Dashboard Design (`dashboard-design` workflow)

- Zendesk metrics (CSAT, ticket volume, resolution time) as health dashboard inputs
- Ticket backlog from `zendesk__ticket_backlog` for operational health

## Output Guidelines

1. **Always state the time window** — "Last 30 days" not just raw numbers
2. **Include row counts** — "Found 47 tickets matching..." for context
3. **Cite the source** — "Per Zendesk data (is_prod.zendesk.ticket)" for auditability
4. **Flag data quality** — Note if NULL counts are high or if results seem incomplete
5. **Contextualize** — Calculate rates, percentages, and period-over-period comparisons
6. **Use the modeled layer when possible** — `zendesk_zendesk` tables have pre-computed metrics

## Error Handling

| Scenario | Action |
|----------|--------|
| MCP not connected | Inform user; run `/mcp` to reconnect VantacaDatabricks |
| Permission denied on schema | Note which schema is inaccessible (e.g., `strata` requires elevated permissions) |
| Long-running query | Tool returns statement_id; use `poll_sql_result` to check status |
| No results | Widen date range or check filter spelling; note if data may not be populated |
| Column not found | Use `DESCRIBE TABLE is_prod.{schema}.{table}` to verify column names |

## Related Skills

- **pendo-analytics** — Product usage analytics and customer feedback via Pendo MCP
- **meeting-synthesis** — Enriched with Gong/Zendesk data from this skill
- **research-gathering** — Supplemented with live support/sales data
- **priority-scoring** — Uses ticket volume and call mentions for scoring
- **context-search** — Complements local qmd search with external data sources
