# /project:red-team

## MANDATORY: Use the red-team-reviewer Skill

**You MUST use the `red-team-reviewer` skill located at `.claude/skills/workflow-red-team-reviewer/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using red-team-reviewer for adversarial PRD review"
2. **Read the skill**: Load `.claude/skills/workflow-red-team-reviewer/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Conduct a granular, adversarial review of the complete PRD. Walk through every scenario step by step. Find broken edges, missing error states, scaling bottlenecks, and logical contradictions. Make the ambitious plan ROBUST, not smaller.

## Prerequisites

- Complete PRD must exist
- All upstream artifacts should exist (Context Brief, Press Releases, Living FAQ, API Design)
- Expansion Proposals (if any were accepted and folded into PRD)

## Arguments

- `--full` — Complete review of entire PRD, all tasks (default)
- `--scenario "name"` — Review a specific user scenario
- `--architecture` — Focus on technical architecture stress test
- `--api` — Focus on agentic API design review
- `--personas` — Run persona-lens review (adopts 3-5 user profiles)
- `--consistency` — Focus on cross-document consistency audit

## Output

Written to the initiative's package folder: `datasets/product/packages/{YYYY}/{slug}/`

- `{package}/red-team-report.md` — Severity-classified findings with recommended fixes

## Gate

All `critical` findings must be addressed (fixes incorporated into PRD). `Major` findings tracked but don't block. PRD updated with revisions before proceeding.

## The Rule

Must NOT recommend cutting features. Must recommend FIXING or IMPROVING them.
