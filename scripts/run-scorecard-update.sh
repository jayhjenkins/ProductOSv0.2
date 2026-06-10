#!/usr/bin/env bash
# Weekly headless run of the Resident Experience scorecard update.
# Invoked by the launchd job com.jayjenkins.scorecard-weekly (Mondays 9:03am),
# or run manually from a normal terminal (NOT inside a Claude Code session):
#     bash ~/pm-os/scripts/run-scorecard-update.sh
set -euo pipefail

PM_OS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PM_OS_DIR"

mkdir -p "$PM_OS_DIR/logs"
LOG="$PM_OS_DIR/logs/scorecard-$(date +%Y%m%d_%H%M%S).log"

# Resolve the claude binary (launchd has a minimal PATH).
CLAUDE_BIN="${CLAUDE_BIN:-$(command -v claude || true)}"
if [[ -z "$CLAUDE_BIN" ]]; then
  CLAUDE_BIN="/Applications/cmux.app/Contents/Resources/bin/claude"
fi

PROMPT="Use the metric-scorecard-fetch skill at .claude/skills/metric-scorecard-fetch/SKILL.md to update Jay's Resident Experience scorecard for the most recent completed Saturday. Fetch all auto metrics via the per-metric subagents, record results to datasets/scorecard/values.json, and render datasets/scorecard/dashboard.html. Do NOT write to SharePoint. Print a one-line per-metric summary at the end."

echo "[$(date)] starting scorecard update with $CLAUDE_BIN" | tee -a "$LOG"

# Unattended run: skip interactive permission prompts. Read-only data pulls + local file writes only.
if "$CLAUDE_BIN" -p "$PROMPT" --dangerously-skip-permissions >> "$LOG" 2>&1; then
  echo "[$(date)] OK -> $LOG" | tee -a "$PM_OS_DIR/logs/scorecard-cron.log"
else
  echo "[$(date)] FAILED (exit $?) -> $LOG" | tee -a "$PM_OS_DIR/logs/scorecard-cron.log"
  exit 1
fi
