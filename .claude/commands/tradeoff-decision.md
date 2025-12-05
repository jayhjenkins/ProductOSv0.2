# /metrics:tradeoff

## MANDATORY: Use the tradeoff-decision Skill

**You MUST use the `tradeoff-decision` skill located at `.claude/skills/workflows/tradeoff-decision/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using tradeoff-decision to evaluate these mixed results"
2. **Read the skill**: Load `.claude/skills/workflows/tradeoff-decision/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Make informed ship/no-ship/iterate decisions when A/B test results are mixed or features show conflicting metric performance.

## Required Inputs

- Metrics that increased (with magnitude)
- Metrics that decreased (with magnitude)
- Change description (what was tested/launched)
- Company strategic priorities
- User journey context
- Rollback feasibility
- Iteration options

## Workflow Sequence

1. North Star Alignment → Which metric matters more strategically?
2. Trade-off Evaluation (Temporal) → Short vs. long-term impact
3. Trade-off Evaluation (Mitigation) → Explore "best of both worlds"
4. Funnel-Based Metric Mapping → Where in journey does trade-off occur?
5. Make Recommendation → Ship/Rollback/Iterate

## Decision Options

- Ship Fully (net positive, strategic alignment)
- Ship to Segments (positive for some users)
- Iterate First (needs modification)
- Gradual Rollout (monitor for delayed effects)
- Rollback (net negative, no mitigation)

## Output

- Strategic assessment
- Temporal analysis (short vs. long-term)
- Mitigation strategies evaluated
- Clear recommendation with rationale
- Implementation plan
- Risks and monitoring plan

## Time Estimate

70-90 minutes total

## No Rationalization

Explore mitigation strategies before binary rollback decisions. No shortcuts.

