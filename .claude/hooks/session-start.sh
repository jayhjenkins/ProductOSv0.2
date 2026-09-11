#!/usr/bin/env bash
set -euo pipefail

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HOOK_DIR/../.." && pwd)"
SKILL_ROOT="$REPO_ROOT/.claude/skills"
using_skills_content=$(cat "${SKILL_ROOT}/meta-using-skills/SKILL.md" 2>&1 || echo "Error: using-skills skill not found. Skills system may not be fully initialized.")

# Escape for JSON
using_skills_escaped=$(echo "$using_skills_content" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | awk '{printf "%s\\n", $0}')

# Resolve the operator's display name from the active profile (robust relative path)
OPERATOR=$(python3 "$REPO_ROOT/scripts/profile_lib.py" --display-name 2>/dev/null || echo "the operator")

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<EXTREMELY_IMPORTANT>\nYou are the chief of staff for ${OPERATOR}. Where skills refer to \"the operator\", that means ${OPERATOR}.\n\nYou have a sophisticated skills-based system.\n\n**The content below is from skills/meta-using-skills/SKILL.md - your introduction to using skills:**\n\n${using_skills_escaped}\n\n**Remember**: If a relevant skill exists for your task, YOU MUST use it. Finding a relevant skill = mandatory usage, not optional.\n</EXTREMELY_IMPORTANT>"
  }
}
EOF

exit 0
