#!/usr/bin/env bash
# run_task_server.sh — launchd entrypoint for the PM-OS task board + cron scheduler.
#
# Wraps `python3 scripts/task_server.py` so it runs with:
#   - the repo as working directory
#   - LangFuse env vars sourced from .env.langfuse (for prompt tracing)
#   - the `claude` CLI on PATH (the Haiku task/cron parser shells out to it;
#     launchd hands processes a minimal PATH that omits ~/.local/bin)
#
# Loaded by ~/Library/LaunchAgents/com.jayjenkins.task-server.plist (KeepAlive).
set -euo pipefail

REPO="/Users/jayjenkins/pm-os"
cd "$REPO"

# Ensure the claude binary and homebrew python are reachable under launchd.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# Source LangFuse keys if present (server degrades gracefully without them).
if [ -f "$REPO/.env.langfuse" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$REPO/.env.langfuse"
  set +a
fi

exec /opt/homebrew/bin/python3 "$REPO/scripts/task_server.py"
