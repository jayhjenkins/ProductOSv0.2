---
description: Fetch this week's Resident Experience scorecard metrics and rebuild the HTML dashboard
---
MANDATORY: Use the `metric-scorecard-fetch` skill at
`.claude/skills/metric-scorecard-fetch/SKILL.md`.

Resolve the last completed Saturday, fetch all auto metrics via per-metric subagents, record to
`datasets/scorecard/values.json`, render `datasets/scorecard/dashboard.html`, and report the path
plus a per-metric summary. Do NOT write to SharePoint — the human copies values from the HTML.
$ARGUMENTS
