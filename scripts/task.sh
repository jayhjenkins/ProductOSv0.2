#!/usr/bin/env bash
# task.sh — PM-OS Task Management CLI wrapper
# Thin bash wrapper that calls python3 scripts/task_cli.py
#
# Usage:
#   ./scripts/task.sh add "Title" --queue human --priority high
#   ./scripts/task.sh list --queue agent --json
#   ./scripts/task.sh show TASK-0001
#   ./scripts/task.sh update TASK-0001 --status in-progress
#   ./scripts/task.sh done TASK-0001
#   ./scripts/task.sh agent:start TASK-0001
#   ./scripts/task.sh agent:complete TASK-0001 --output "path/to/artifact"
#   ./scripts/task.sh agent:fail TASK-0001 --error "reason"
#   ./scripts/task.sh agent:ask TASK-0001 "question"
#   ./scripts/task.sh inbox

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PM_OS_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PM_OS_DIR"
exec /opt/homebrew/bin/python3 "$SCRIPT_DIR/task_cli.py" "$@"
