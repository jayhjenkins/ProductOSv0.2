---
name: workflow-velocity-estimate
description: Use when estimating how long a feature/body of work will take to build — ingests a PRD + inception transcript (+ spec if it exists), breaks the work into units, estimates each unit's active execution time against observed Q2 benchmarks, and sums to a feature estimate. Anchors to unit throughput, not story points or team size.
allowed-tools: Read, Grep, Glob, Bash, Skill
---

# Velocity Estimate

## Purpose

Produce a bottom-up, **unit-level** time estimate for a feature, benchmarked to the Home team's observed Q2 2026 throughput. Give it a PRD + an inception transcript (and a spec if one exists); it returns each unit's active-execution estimate, sums them to a feature estimate, forecasts mini-inception rework, and reports controllable latency separately. Every number is traceable to `datasets/velocity/calibration.yaml`.

## When to Use

- User invokes `/estimate-velocity`
- Quarterly planning or two-quarter aspirational goal-setting
- Right after an inception, to size a body of work before committing
- Re-estimating after a calibration tune

## Guiding Principles

1. **Anchor to active execution per unit** (In Development → shippable). This is the clean, repeatable signal.
2. **Feature = SUM of units.** No team/captain/parallelism/critical-path modeling — team shape is upstream and changes constantly. The summed estimate vs. actual elapsed will later reveal the parallelism factor empirically.
3. **Latency is reported separately.** Pre-dev and integration/release latency are controllable overheads — show them, never fold them into the headline.
4. **Legible, not black-box.** Pull every number from `calibration.yaml`; cite the driver for each unit. If you'd have to invent a number, say so and flag low confidence instead.
5. **No fabrication.** Unknown unit list, unknown systems, non-inspectable repos → say so and lower confidence. The estimate is a prediction to be scored later, not a promise.

## Required reading at start

Load these every run (they are the model):
- `datasets/velocity/calibration.yaml` — all parameters. Note the `version`.
- `datasets/velocity/benchmarks.md` — observed anchors + evidence (for explaining drivers).
- `datasets/velocity/templates/velocity-estimate-template.md` — output shape.

## Inputs & two modes

Resolve inputs from the user's args (a feature slug, a package path, and/or explicit file paths):
- **PRD:** `datasets/product/packages/2026/<feature>/PRD_*.md`
- **Inception transcript:** `datasets/meetings/product/home/YYYY-MM/*Inception*.txt` (use `context-search`/qmd to locate — people say "inception" conversationally; also check for mini-inceptions via grep `"mini inception"`).
- **Spec / unit list (optional):** `~/dev/Vantaca/VantacaConnect/apps/home/doc/specs/NNN-*.md`, `~/dev/Vantaca/VantacaNextGeneration/Documentation/Inception/home/<feature>/`, or the Jira Feature's child-unit "Affected Areas" tables (pull via Jira MCP if available).

**Mode A — units given:** a spec or Jira already enumerates units → estimate each directly. Higher confidence.
**Mode B — units inferred:** only PRD + inception exist → first propose a probable unit list (decompose by surface/system/workstream the way real specs do), then estimate. Lower confidence — label it and list the inferred units as a prediction.

Announce which mode you're in and which inputs you found.

## Workflow

### Phase 1 — Assemble inputs
Locate and read PRD + inception (+ spec). State Mode A or B. If Mode B, derive a probable unit list now and show it for the user to eyeball before estimating.

### Phase 2 — Per-unit signal extraction (the rubric)
For each unit, determine:
1. **Systems touched** + count — from spec "Affected Areas"/"Target Repo(s)"/"File Locations", Jira components/labels, or (Mode B) inference. Map repos→systems using `system_weights`. `Vantaca HXP` is a team tag — ignore.
2. **Regime** — if any touched system is `Mobile`, it's `human_native` (out-of-model): flag, use `regimes.human_native.base_days`, set confidence low, do not pretend precision. Otherwise `ai_leveraged`.
3. **Foundation vs increment** — does an analogous Service/Contract/component/page already exist? **Inspect locally for NextGen** (`~/dev/Vantaca/VantacaNextGeneration/{Services,Contracts}/`) **and Connect** (`~/dev/Vantaca/VantacaConnect/apps/home/src/{components,pages,lib,stores}/`) with Glob/Grep. If the pattern exists → increment; if net-new → foundation. For systems in `non_local_default` scope (CMP/Core/Mobile/Migrations — not cloned), default to `foundation` and note it.
4. **Cross-repo** — ≥2 repos, especially CMP+Core both present → cross-repo.
5. **Scope size** — count affected files/areas in the spec → small/medium/large per `modifiers.scope_size`. In Mode B, estimate the count from the PRD scope and flag it.

### Phase 3 — Per-unit estimate
1. Pick archetype: `{increment|foundation}_{single_system|multi/cross_repo}` (use `foundation_cross_repo` when foundation + cross-repo; `increment_multi_system` when increment + ≥2 systems).
2. Look up `base_days` (p50/p75).
3. Apply modifiers (≤2): `cross_repo_handshake` multiplier (increments touching CMP+Core only), then `scope_size` factor.
4. If `foundation_tax.apply` is true in calibration AND this unit meets the triggers, apply that multiplier (default off — only for genuinely greenfield, unresolved-ownership work).
5. Round to 0.5 days. Assign confidence per `confidence` rules. Record the **drivers** (one phrase) for the unit row.

### Phase 4 — Feature roll-up (additive)
1. **Headline = Σ unit p50 … Σ unit p75** active days; also show ÷ `working_days_per_week` as weeks, explicitly labeled "effort-sum, not parallelism-adjusted wall-clock."
2. **Mini-inception forecast:** score `mini_inception.signals` from the inception/PRD (open-question count, unresolved cross-team CMP ownership, public/security surface, new external dependency) → risk low/medium/high → `expected_count` → add (`added_increment_units` × increment_single p50) + `respec_latency_days`. Report as a separate line.
3. **Latency (separate):** report `overheads.pre_dev_latency_days` + `overheads.integration_release_latency_days` as the controllable wall-clock overhead — not in the headline.
4. **Overall confidence** = lowest-common across units + mode + inspectability.

### Phase 5 — Write artifacts
Fill `velocity-estimate-template.md` →
- `datasets/velocity/estimates/{YYYY-MM-DD}_{feature-slug}_estimate.md`
- `datasets/velocity/estimates/{YYYY-MM-DD}_{feature-slug}_estimate.json` (machine record — schema below)

Then summarize to the user: headline range, the 2–3 units driving it, mini-inception risk, and the biggest uncertainty.

## Machine record (.json) — for future eval

```json
{
  "feature": "community-feed",
  "date": "2026-06-02",
  "mode": "A",
  "calibration_version": "2026-06-02.v1",
  "overall_confidence": "medium",
  "inputs": { "prd": "...", "inception": "...", "spec": "...", "repos_inspected": ["NextGen","Connect"] },
  "units": [
    { "id": "U1", "name": "Resident feed surface", "systems": ["Connect"],
      "regime": "ai_leveraged", "archetype": "foundation_single_system",
      "foundation_or_increment": "foundation", "scope_size": "medium",
      "modifiers_applied": [], "est_days_p50": 7, "est_days_p75": 9,
      "confidence": "high", "drivers": "net-new feed page, single repo" }
  ],
  "feature_sum_days": { "p50": 0, "p75": 0 },
  "mini_inception": { "risk": "low", "expected_count": 0, "added_days": 0 },
  "latency_overhead_days": { "pre_dev": {"p50":2,"p75":7}, "integration": {"p50":2,"p75":5} },
  "actuals": null
}
```

Leave `"actuals": null` — the future eval loop fills it by re-pulling Jira changelogs (as in the Step-1 analysis) and scores predicted vs. actual.

## Success Criteria

- Mode declared; inputs located and cited.
- Every unit has a systems list, archetype, foundation/increment call, scope, p50–p75, confidence, and a driver phrase — all traceable to `calibration.yaml`.
- Feature headline is the SUM of units, shown in days and weeks, labeled as effort-sum.
- Mini-inception forecast and latency overhead reported **separately** from the headline.
- Mobile/human-native units flagged out-of-model, never silently precise.
- Both `.md` and `.json` written with date-first names; `.json` carries the calibration version.

## Related Skills

- `context-search`: locate inception transcripts and specs semantically.
- `workflow-jira-home`: Jira field/workflow reference (units = "Unit" issue type; "Affected Areas" tables are the richest unit-scope source).
- `workflow-prd-creation`: produces the PRD this consumes.
- (future) `quality-velocity-estimation` / eval loop: scores estimates against actuals and proposes `calibration.yaml` edits. Not built yet.

## Out of scope (do not do here)

- Team capacity / captain / parallelism / critical-path scheduling.
- Estimate-vs-actual reconciliation, calibration auto-tuning, cron, Jira auto-pull (a later step — the `.json` exists to enable it).
