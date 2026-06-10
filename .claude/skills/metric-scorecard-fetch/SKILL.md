---
name: metric-scorecard-fetch
description: Use when updating Jay's Resident Experience EOS scorecard — fetches the auto-sourceable metrics from Pendo + Databricks via per-metric subagents, records them to the values store, and renders the HTML dashboard. Invoked by /scorecard-update.
allowed-tools: Read, Bash, Agent, Write
---

# Scorecard Fetch & Render (Dispatcher)

This skill is the long-lived scorecard orchestrator. It holds only metric slugs + results — never
all metric specs at once. Each metric's calculation lives in its own self-contained file under
`.claude/skills/metric-scorecard-fetch/metrics/<slug>.md`. These definitions are independent of the
temporal quarterly Rocks/OKR skill — do not couple them.

## Flow

1. **Resolve `as_of_date`** = last completed Saturday on/before today:
   `python3 -c "import datetime as d;t=d.date.today();print(t-d.timedelta(days=(t.weekday()-5)%7))"`

2. **Read** `datasets/scorecard/registry.json` to get the metric list.

3. **Fetch `home-wau` first** (the `/1k-WAU` metrics and stickiness need its value). Dispatch a
   subagent (general-purpose) handed ONLY the contents of `metrics/home-wau.md` + the `as_of_date`.

4. **Dispatch the remaining `auto` metrics in parallel** — one subagent each, in a single message
   with multiple Agent calls. Hand each subagent ONLY:
   - the contents of its own `metrics/<slug>.md`
   - the resolved `as_of_date`
   - if its file lists `depends_on: home-wau`, also the already-computed home-wau integer value
   Instruct each to execute its spec exactly and return ONLY its JSON contract line (nothing else).

5. **Handle non-auto metrics:**
   - `manual` (hoai-weekly-interactions): reuse the prior week's value from values.json if present
     (status `manual_carried`); else value null, status `manual`.
   - `deferred` (new-resident-activation-rate): value null, status `deferred`.

6. **Collect** all results into a dict keyed by slug, write it with the Write tool to
   `/tmp/scorecard_results_<as_of>.json`, then record + render:
   `python3 scripts/build_scorecard_dashboard.py --week <as_of> --record /tmp/scorecard_results_<as_of>.json`

7. **Report** the dashboard path and a one-line summary per metric (value + status). Flag any
   `error`/`stale` metric and any value outside its file's stated Sanity range.

## Conventions
- Pendo subId=4818486697721856. Databricks is_prod, READ-ONLY (never modify data).
- Saturday-anchored as_of; Sun–Sat weeks; windows inclusive of as_of.
- Never overwrite past weeks — the renderer appends to the time series.
- If a subagent errors, record status=error (carry last-known value if any) and continue; never
  let one metric block the others.
- Do NOT write to SharePoint — the human copies values from the rendered HTML.
