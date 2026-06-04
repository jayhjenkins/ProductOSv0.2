# /estimate-velocity

MANDATORY: Use the `workflow-velocity-estimate` skill (`.claude/skills/workflow-velocity-estimate/SKILL.md`).

Estimates how long a feature/body of work will take to build, bottom-up from units, benchmarked to the Home team's observed Q2 2026 throughput. Anchors to **unit active-execution time**, not story points or team size.

## Arguments
- `--feature <slug>` — package slug under `datasets/product/packages/2026/<slug>/` (finds the PRD; the skill locates the inception transcript)
- `--prd <path>` / `--inception <path>` / `--spec <path>` — point at inputs explicitly
- (no args) — the skill asks which feature, then resolves inputs

## What it does
Reads `datasets/velocity/calibration.yaml` (the levers) + `benchmarks.md`, breaks the work into units (Mode A if a spec enumerates them, Mode B if it must infer from PRD + inception), estimates each unit's p50–p75 active days, sums to a feature estimate, forecasts mini-inception rework, and reports pre-dev/integration latency separately. Writes `datasets/velocity/estimates/YYYY-MM-DD_<feature>_estimate.{md,json}`.

To tune the model, edit `datasets/velocity/calibration.yaml` and re-run — no skill edits needed.
