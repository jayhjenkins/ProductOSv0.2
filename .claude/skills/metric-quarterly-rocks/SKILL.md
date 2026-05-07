---
name: metric-quarterly-rocks
description: Use when computing or validating Jay's Q2 2026 Rocks metrics (Home WAU and Board Member Weekly Login Rate) - defines exact, reproducible Pendo query specifications and aggregation rules so weekly runs are byte-for-byte comparable across time
allowed-tools: Read, Bash
---

# Quarterly Rocks — Metric Definitions

## Purpose

Lock the calculation methodology for Jay's two Q2 2026 EOS Rocks so weekly reporting is reproducible and trend lines remain comparable across time. This skill is the single source of truth for **how** these metrics are computed; it does not handle persistence or reporting (the `/update-rocks` command does that).

## When to Use This Skill

Activate automatically when:
- Computing Home WAU or Board Member Weekly Login Rate for any reporting period
- Validating numbers in the L10 Rocks tab against fresh Pendo data
- Backfilling a missed week
- Spot-checking historical values during methodology audits
- Called by the `/update-rocks` command

**When NOT to use:**
- Defining metrics for a *new* feature or product (use `metrics-definition` workflow instead)
- Generating a metric *target* — targets are set out-of-band; this skill only computes current values
- Pulling Pendo data for non-Rocks analysis (use `pendo-analytics` directly)

## Conventions (Locked)

These conventions are non-negotiable. Changing any of them invalidates trend comparisons and must be a deliberate methodology decision documented in this file.

| Convention | Value | Rationale |
|---|---|---|
| **Metric `as_of_date`** | Last completed Saturday (most recent Saturday on or before "today") | Ends a complete Sun-Sat week; matches the historical reporting standard |
| **Reporting `report_date`** | The L10 meeting day (typically Thursday) when the metric is read out | This is the **column header** in the L10 Rocks tab; is *later* than `as_of_date` |
| **Mapping** | `as_of_date` = the Saturday immediately preceding `report_date` | If `report_date` is itself a Saturday, `as_of_date` = same day |
| **Week boundary** | Sunday 00:00 → Saturday 23:59 (Pendo's native weekly bucket alignment) | Pendo's `period: "weekly"` aggregation already aligns Sun-Sat |
| **Window inclusivity** | All trailing windows are **inclusive** of `as_of_date` | Validated against historical references to within 0.04–0.5pp |
| **Pendo subId** | `4818486697721856` (Vantaca subscription) | Required on every MCP call |
| **Pendo appId** | `5961191088521216` (Vantaca Home) | Both metrics scope to Home only |

## Metric 1 — Home WAU (4-week rolling average)

### Definition

Mean unique identified visitors per Sun-Sat week, averaged across the **4 most recent complete weeks** where the week's Saturday end-date is on or before `as_of_date`. No segment filter — counts all identified visitors in Home (board members and non-board users alike).

### Formula

```
WAU = mean(week_uniques[w-3], week_uniques[w-2], week_uniques[w-1], week_uniques[w])
```

where `w` is the Sun-Sat week ending on `as_of_date`, and each `week_uniques` is unique visitor count for that bucket.

### Pendo query (literal call)

Single query with weekly bucketing:

```
mcp__claude_ai_Pendo__activityQuery(
  subId="4818486697721856",
  appId="5961191088521216",
  entityType="visitor",
  dateRange={
    range: "custom",
    startDate: <as_of_date - 27 days>,   # Sunday 4 weeks before
    endDate:   <as_of_date>              # Saturday
  },
  period="weekly",
  group=["visitorId"],
  count=true
)
```

The response returns 4 weekly buckets in `results[].rows[].count`. Sum all 4 counts and divide by 4. Round to nearest integer.

### Spreadsheet output format

Text string in the WAU row cell. Format: `"{wau/1000:.1f}k"` with a trailing `.0` stripped:
- 504,000 → `"504k"`
- 504,600 → `"504.6k"`
- 502,000 → `"502k"`

Lowercase `k`, no commas. Existing data in the workbook has minor case inconsistency (`"505K"` in col H) — going forward we standardize on lowercase `k`.

### Q2 target

**540k** (+13% vs March 2026 baseline of 478k).

## Metric 2 — Board Member Weekly Login Rate

### Definition

Unique board members active in trailing 7 days inclusive of `as_of_date`, divided by unique board members active in trailing 90 days inclusive of `as_of_date`. A measure of stickiness within the board-member population.

### Formula

```
rate = unique_board_members_7d / unique_board_members_90d
```

### Filter

Pendo segment **`Home | Board Members`** (segmentId `ruTWzJHTx86HCgbOfdAP80T85UQ`). Functionally equivalent to `metadata.agent.isboardmember == true` but always use the segment id — the segment is the canonical definition managed in Pendo and may evolve.

### Pendo queries (two calls)

```
# Numerator — 7-day window
mcp__claude_ai_Pendo__activityQuery(
  subId="4818486697721856",
  appId="5961191088521216",
  entityType="visitor",
  segmentId="ruTWzJHTx86HCgbOfdAP80T85UQ",
  dateRange={ range:"custom", startDate:<as_of_date - 6 days>, endDate:<as_of_date> },
  group=["visitorId"],
  count=true
)

# Denominator — 90-day window
mcp__claude_ai_Pendo__activityQuery(
  subId="4818486697721856",
  appId="5961191088521216",
  entityType="visitor",
  segmentId="ruTWzJHTx86HCgbOfdAP80T85UQ",
  dateRange={ range:"custom", startDate:<as_of_date - 89 days>, endDate:<as_of_date> },
  group=["visitorId"],
  count=true
)
```

### Computation

`rate = numerator_count / denominator_count`. Keep 4 decimal places of precision (e.g., `0.3201`).

### Spreadsheet output format

Float decimal in the Stickiness row cell. Existing cell style applies a percent format, so `0.3201` renders as `32.01%`. Do **not** multiply by 100; do **not** write a string with `%`. Always write the raw decimal.

### Q2 target

**40%** (i.e., `0.40`).

## Validation Reference Points

These points were validated this session against existing L10 column data. Future runs should sanity-check against these for methodology integrity. Differences of >1pp indicate the calculation drifted.

| `as_of` Saturday | Equivalent column (Thu report_date) | WAU | Stickiness | Notes |
|---|---|---|---:|---|
| 2026-04-04 | 2026-04-09 (col F) | ~493k | ~32.08% | Reference cell shows 493k / 32.30%; matched within 0.22pp |
| 2026-04-11 | 2026-04-16 (col G) | ~503k | ~32.46% | Reference cell shows 504k / 32.42%; matched within 0.04pp |
| 2026-04-18 | 2026-04-23 (col H) | ~506k | ~31.48% | Reference cell shows 505K / 32.01%; matched within 0.53pp |
| 2026-04-25 | 2026-04-30 (col I) | ~502k | ~31.0% | First as-of-Saturday-anchored point; not yet reported |

Variations of 0.04–0.5pp across these checkpoints are expected — caused by Pendo's late-arriving identified-visitor backfill, not methodology drift.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Computing WAU over a 12-week / 90-day window | WAU is **4-week trailing**, not 90-day. Use exactly 4 weekly buckets. |
| Including the partial Sun-Sat week containing `as_of_date` if it isn't fully complete | Only count weeks whose Saturday end-date is **on or before** `as_of_date`. If `as_of_date` is itself a Saturday, that week is included; otherwise the most recent week ends on the prior Saturday. |
| Using exclusive `lastNDays` semantics | Windows are **inclusive** of `as_of_date`. 7d window = `as_of_date - 6` to `as_of_date`. 90d window = `as_of_date - 89` to `as_of_date`. |
| Writing the stickiness as a string `"32.01%"` | Write the raw decimal (`0.3201`); the cell's number format renders the % sign. |
| Reporting `as_of_date` as the column header | The column header is `report_date` (typically Thursday); `as_of_date` is the prior Saturday. They are different. |
| Filtering by `metadata.agent.isboardmember == true` instead of the segment | Use `segmentId="ruTWzJHTx86HCgbOfdAP80T85UQ"` — the segment is the canonical definition. |
| Querying without `subId` | Every Pendo MCP call requires `subId="4818486697721856"`. |
| Picking a different appId | Both metrics are Home-only. `appId="5961191088521216"`. Do not mix in IQ, Manage, HOAi, or Core data. |

## Anti-Rationalization

| Thought | Reality |
|---|---|
| "Going to a 12-week WAU smooths noise better" | The historical baseline and trend line are 4-week. Changing the window invalidates trend comparison and requires explicit baseline reset. |
| "I'll just use Pendo's `lastNDays: 7` for convenience" | Pendo's `lastNDays` excludes today, breaking inclusivity. Use explicit `custom` dateRange. |
| "Today's Tuesday — I'll anchor to today" | No. Always anchor to the last completed Saturday. Mid-week as-of dates produce incomplete trailing weeks and break WAU. |
| "I'll multiply stickiness by 100 to make the spreadsheet show a real %" | The cell already has a % format applied. Multiplying double-renders. Always write raw decimal. |

## Success Criteria

A run of either metric is correct when:
- `as_of_date` resolves to a Saturday on or before today
- WAU query returns exactly 4 weekly buckets (not 3, not 5)
- Stickiness numerator and denominator both come from `segmentId="ruTWzJHTx86HCgbOfdAP80T85UQ"`
- All windows are inclusive of `as_of_date`
- All outputs reference the validation table above and are within reasonable distance (no order-of-magnitude jumps without explanation)
- Output formats match the spreadsheet conventions (text `"504k"` for WAU, decimal `0.3201` for stickiness)

## Related Skills

- **pendo-analytics** (context-assembly) — Defines MCP connection, available tools, and query patterns. This skill specializes those patterns for the two Rocks metrics.
- **metrics-definition** (workflow) — Used when defining *new* metrics; not used for the established Rocks metrics.

## Integration Points

**Called by:**
- `/update-rocks` command — runs both metrics for the active reporting week and writes results to the L10 Rocks tab.

**Calls these skills:**
- `pendo-analytics` for MCP connection conventions (subId, appId references).
