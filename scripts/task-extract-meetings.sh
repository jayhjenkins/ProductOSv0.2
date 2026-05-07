#!/usr/bin/env bash
set -euo pipefail

PM_OS_DIR="$(cd "$(dirname "$0")/.." && pwd)"

MEETINGS_DIR="$PM_OS_DIR/datasets/meetings"
PROCESSED_FILE="$PM_OS_DIR/datasets/tasks/_processed-meetings.txt"

# Ensure the processed-meetings tracker exists
if [[ ! -f "$PROCESSED_FILE" ]]; then
  touch "$PROCESSED_FILE"
fi

###############################################################################
# Usage
###############################################################################
usage() {
  cat <<EOF
Usage:
  $(basename "$0") <transcript-path>    Process a single meeting transcript
  $(basename "$0") --all-unprocessed    Process all unprocessed transcripts

Examples:
  ./scripts/task-extract-meetings.sh datasets/meetings/2026-02-25_product-sync.md
  ./scripts/task-extract-meetings.sh --all-unprocessed
EOF
  exit 1
}

###############################################################################
# Helpers
###############################################################################
is_processed() {
  local file="$1"
  # Strip the datasets/meetings/ prefix if present, then check if either form exists.
  # This handles both "datasets/meetings/foo/bar.txt" and "foo/bar.txt" formats.
  local normalized="${file#datasets/meetings/}"
  grep -qF "$normalized" "$PROCESSED_FILE" 2>/dev/null
}

mark_processed() {
  local file="$1"
  # Always write the full datasets/meetings/ path for consistency going forward
  if ! is_processed "$file"; then
    echo "$file" >> "$PROCESSED_FILE"
  fi
}

process_transcript() {
  local filepath="$1"

  # Resolve to absolute path if relative
  if [[ "$filepath" != /* ]]; then
    filepath="$PM_OS_DIR/$filepath"
  fi

  if [[ ! -f "$filepath" ]]; then
    echo "[ERROR] File not found: $filepath"
    return 1
  fi

  # Use the relative path (from PM_OS_DIR) as the key in the processed list
  local relative_path="${filepath#"$PM_OS_DIR"/}"

  if is_processed "$relative_path"; then
    echo "[SKIP] Already processed: $relative_path"
    return 0
  fi

  echo "[PROCESSING] $relative_path"

  # Capture stderr to detect nested-session errors (claude exits 0 even on those)
  local tmpstderr
  tmpstderr="$(mktemp)"

  if claude -p "Read the meeting transcript at $filepath.

BEFORE extracting tasks, run: ./scripts/task.sh list --json
This gives you all existing open tasks. For EACH potential new task, check if a semantically similar task already exists (same underlying work, even if worded differently). If a duplicate exists:
- Do NOT create a new task
- Instead, run: ./scripts/task.sh update TASK-NNNN --comment \"Additional context from $filepath: <new details>\"
- Append-only: add new context, never remove existing context
- If priority should escalate, update that too

Only create a new task if no existing task covers the same work.

Use the task-extract-from-meeting skill at .claude/skills/task-management/task-extract-from-meeting/SKILL.md to identify action items and create tasks. For each action item, use ./scripts/task.sh add with appropriate --queue, --priority, --domain, --source-meeting flags. Apply the auto-queue rules: human decisions -> human queue, autonomous work -> agent queue, joint work -> collab queue, delegated to others -> waiting queue." \
    --allowedTools "Bash(*),Read(*),Write(*)" \
    --max-turns 20 2>"$tmpstderr"; then
    # claude exited 0, but check stderr for nested-session false positive
    if grep -q "cannot be launched inside another Claude Code session" "$tmpstderr" 2>/dev/null; then
      echo "[ERROR] Nested Claude session detected for: $relative_path (not marking as processed)"
      cat "$tmpstderr" >&2
    else
      mark_processed "$relative_path"
      echo "[DONE] $relative_path"
    fi
  else
    echo "[ERROR] claude exited non-zero for: $relative_path (not marking as processed)"
    cat "$tmpstderr" >&2
  fi
  rm -f "$tmpstderr"
}

###############################################################################
# Main
###############################################################################
if [[ $# -eq 0 ]]; then
  usage
fi

if [[ "$1" == "--all-unprocessed" ]]; then
  echo "=== Processing all unprocessed transcripts ==="
  echo "Meetings dir: $MEETINGS_DIR"
  echo ""

  found=0
  while IFS= read -r -d '' file; do
    found=1
    process_transcript "$file"
  done < <(find "$MEETINGS_DIR" -type f \( -name '*.md' -o -name '*.txt' \) -print0 | sort -z)

  if [[ "$found" -eq 0 ]]; then
    echo "[INFO] No .md or .txt files found under $MEETINGS_DIR"
  fi

  echo ""
  echo "=== All unprocessed transcripts handled ==="
else
  process_transcript "$1"
fi
