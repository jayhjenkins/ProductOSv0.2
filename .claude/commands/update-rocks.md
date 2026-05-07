# /update-rocks

## MANDATORY: Use the quarterly-rocks and pendo-analytics Skills

**You MUST read both skills before computing anything:**
- `quarterly-rocks` — locked metric definitions (formulas, queries, formats). Located at `.claude/skills/metric-quarterly-rocks/SKILL.md`.
- `pendo-analytics` — Pendo MCP connection conventions and tool reference. Located at `.claude/skills/context-pendo-analytics/SKILL.md`.

## Before Starting

1. **Announce both skills**:
   - "I'm using **quarterly-rocks** for the locked metric definitions."
   - "I'm using **pendo-analytics** for Pendo MCP access."
2. **Read both skill files** in parallel.
3. **Follow the metric definitions in `quarterly-rocks` exactly.** No methodology drift.

## Purpose

Pull this week's values for Jay's two Q2 Rocks (Home WAU and Board Member Weekly Login Rate) from Pendo and write them into the L10 Rocks tab in `~/Library/CloudStorage/OneDrive-Vantaca,LLC/EOS/L10-Resident Experience.xlsx`.

## Inputs (all optional)

| Flag | Default | Meaning |
|---|---|---|
| `--report-date YYYY-MM-DD` | Resolved from workbook (see below) | The L10 column-header date (typically a Thursday). |
| `--as-of YYYY-MM-DD` | Saturday immediately preceding `--report-date` | The metric calculation as-of date. Must be a Saturday per quarterly-rocks convention. |
| `--overwrite` | off | Replace existing values in the target column instead of refusing. |
| `--dry-run` | off | Compute and print the values; do not write to the workbook. |

## Resolution Rule (when `--report-date` is not supplied)

1. Open the workbook and read row 1 of the Rocks tab.
2. Build the list of dated columns (use cached formula values — many headers are formulas like `=H1+7`).
3. Walk the dated columns left-to-right. The **target** column = the leftmost column whose header date ≤ today AND whose Home WAU and Board Member Weekly Login Rate cells are both empty.
4. If every dated column ≤ today is already filled → append a new column at the rightmost position with header = (last existing header + 7 days), keeping the Thursday cadence.
5. Set `report_date` = target column's header date.
6. Set `as_of_date` = the Saturday immediately preceding `report_date` (or `report_date` itself if it is a Saturday).

## Workflow

### Step 1 — Resolve dates and target column

Use the helper script in dry-run mode (or read the workbook directly) to identify the target column. Print:

```
Target column: <letter> (<date>)
Report date  : YYYY-MM-DD (<weekday>)
As of date   : YYYY-MM-DD (<weekday>) — must be Saturday
```

If the user-supplied `--as-of` is not a Saturday, halt and ask the user to confirm — quarterly-rocks convention requires Saturday-anchored as-of dates.

### Step 2 — Confirm before mutating shared state

Print the resolved dates and ask Jay: **"Computing as of Saturday {as_of_date}, writing to column {report_date} in L10-Resident Experience.xlsx (Rocks tab). Proceed?"**

This matches Jay's standing preference for confirmation before mutating shared/published artifacts.

### Step 3 — Run Pendo queries per quarterly-rocks

Three MCP calls total. Use the literal call signatures specified in `quarterly-rocks` (do not improvise):

**WAU (1 call, 4-week bucketed):**
```
mcp__claude_ai_Pendo__activityQuery(
  subId="4818486697721856",
  appId="5961191088521216",
  entityType="visitor",
  dateRange={ range:"custom", startDate:<as_of - 27 days>, endDate:<as_of> },
  period="weekly",
  group=["visitorId"],
  count=true
)
```
The response should contain exactly 4 weekly buckets. If you get 3 or 5, halt — date arithmetic is wrong.

**Stickiness numerator (7d):**
```
mcp__claude_ai_Pendo__activityQuery(
  subId="4818486697721856",
  appId="5961191088521216",
  entityType="visitor",
  segmentId="ruTWzJHTx86HCgbOfdAP80T85UQ",
  dateRange={ range:"custom", startDate:<as_of - 6 days>, endDate:<as_of> },
  group=["visitorId"],
  count=true
)
```

**Stickiness denominator (90d):** same as above with `startDate:<as_of - 89 days>`.

### Step 4 — Compute

- WAU = mean of the 4 weekly counts, rounded to nearest integer.
- Stickiness = numerator_count / denominator_count, kept to 4 decimal places.

### Step 5 — Sanity check vs prior week

Read the prior dated column's values from the workbook. Print a side-by-side comparison:

```
Metric                              Prior ({prev_date})    This week ({report_date})    Δ
Home WAU (4-wk avg)                 504k                   {wau_str}                    {Δ}
Board Member Weekly Login Rate      32.42%                 {stickiness_pct}             {Δpp}
```

If a metric moved by >10% week-over-week, flag it explicitly so Jay can decide whether to investigate before publishing.

### Step 6 — Write to workbook

Run the helper script (it lives at `scripts/update_rocks_xlsx.py`):

```bash
python3 scripts/update_rocks_xlsx.py \
  --workbook "$HOME/Library/CloudStorage/OneDrive-Vantaca,LLC/EOS/L10-Resident Experience.xlsx" \
  --report-date <YYYY-MM-DD> \
  --as-of-date <YYYY-MM-DD> \
  --wau <int> \
  --stickiness <decimal> \
  [--insert-if-missing if step 1 determined a new column is needed] \
  [--overwrite if user explicitly said yes to overwriting] \
  [--dry-run if user invoked /update-rocks --dry-run]
```

The script handles cell location by label, formula-driven future columns, and column insertion. If it fails:
- `permission denied` → workbook is open in Excel; ask Jay to close it.
- `openpyxl is not installed` → run `pip3 install --break-system-packages -r requirements-rocks.txt` then retry.
- `already has values` → ask Jay whether to overwrite, then re-run with `--overwrite`.

### Step 7 — Final summary

Print:
```
Updated  : Rocks!{col_letter}{row} (Home WAU)              <prev> -> <new>
Updated  : Rocks!{col_letter}{row} (Board Member Login Rate) <prev> -> <new>
File     : <full path>
Sync     : OneDrive will push to SharePoint within ~30 sec.
```

## Bootstrap (first run only)

If `python3 -c "import openpyxl"` fails, run:
```bash
pip3 install --break-system-packages -r /Users/jayjenkins/pm-os/requirements-rocks.txt
```

## Error Handling

| Symptom | Cause | Fix |
|---|---|---|
| Pendo MCP calls return error | MCP not authenticated or disconnected | Tell Jay to re-auth via `/mcp`. Do NOT attempt to compute from estimates. |
| WAU query returns 3 or 5 buckets | Date arithmetic for the 4-week window is off | Halt; recompute startDate as `as_of - 27 days`. |
| `as_of_date` is not a Saturday | User passed `--as-of` for a non-Saturday | Halt; ask user to confirm or correct. |
| Workbook locked | File open in Excel | Ask Jay to close it. |
| No empty target column found and `--insert-if-missing` not yet used | Resolution rule needs to append | Re-invoke helper with `--insert-if-missing`. |
| Stickiness > 1.0 | Wrote percent (e.g. 32.0) instead of decimal (0.320) | Always pass the raw decimal; the cell formats as %. |

## Time Estimate

5–8 minutes (dominated by Pendo query latency and the user confirmation step).

## No Rationalization

Use the locked formulas, queries, segment id, and output formats from the `quarterly-rocks` skill exactly. Do not switch to a different WAU window, do not use Pendo's `lastNDays` shortcuts, do not compute stickiness from a metadata filter when the segment id exists. The whole point of this command is methodological consistency week over week.
