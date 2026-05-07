#!/bin/bash
set -euo pipefail
LOG="/Users/jayjenkins/pm-os/logs/qmd-update.log"
echo "=== qmd nightly update: $(date) ===" >> "$LOG"
/opt/homebrew/bin/qmd update >> "$LOG" 2>&1
/opt/homebrew/bin/qmd embed >> "$LOG" 2>&1
echo "=== done: $(date) ===" >> "$LOG"
