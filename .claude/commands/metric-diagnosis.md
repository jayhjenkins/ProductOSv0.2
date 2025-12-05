# /metrics:diagnosis

## MANDATORY: Use the metric-diagnosis Skill

**You MUST use the `metric-diagnosis` skill located at `.claude/skills/workflows/metric-diagnosis/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using metric-diagnosis to investigate this metric change"
2. **Read the skill**: Load `.claude/skills/workflows/metric-diagnosis/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Systematically investigate unexpected metric changes to identify root cause through data segmentation, hypothesis testing, and impact assessment.

## Required Inputs

- Metric that changed (name and definition)
- Magnitude of change (absolute and %)
- Timeframe (when noticed, over what period)
- Access to segmented data
- Recent activity log (releases, experiments, campaigns)

## Workflow Sequence

0. Data Quality Verification → Confirm data is valid
1. Root Cause Diagnosis (Phase 1) → Narrow scope via 4D segmentation
2. Root Cause Diagnosis (Phase 2) → Brainstorm intrinsic vs extrinsic factors
3. Root Cause Diagnosis (Phase 3) → Test hypotheses with table method
4. North Star Alignment → Assess strategic impact
5. Recommend Actions → Fix/Mitigate/Monitor/No Action

## Output

- Narrowed problem scope
- Tested hypotheses with evidence
- Identified root cause (or top candidates)
- North Star impact assessment
- Recommended actions with owners and timelines
- Full diagnosis report

## Time Estimate

60-90 minutes total

## No Rationalization

Complete all phases systematically. No jumping to conclusions.

