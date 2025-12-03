#!/usr/bin/env bash
set -euo pipefail

SKILL_ROOT="/Users/jay/superpowers-llm/.claude/skills"
using_skills_content=$(cat "${SKILL_ROOT}/meta/using-skills/SKILL.md" 2>&1 || echo "Error: using-skills skill not found. Skills system may not be fully initialized.")

# Escape for JSON
using_skills_escaped=$(echo "$using_skills_content" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | awk '{printf "%s\\n", $0}')

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<EXTREMELY_IMPORTANT>\nYou have a sophisticated skills-based system.\n\n**The content below is from skills/meta/using-skills/SKILL.md - your introduction to using skills:**\n\n${using_skills_escaped}\n\n**Remember**: If a relevant skill exists for your task, YOU MUST use it. Finding a relevant skill = mandatory usage, not optional.\n</EXTREMELY_IMPORTANT>"
  }
}
EOF

exit 0
