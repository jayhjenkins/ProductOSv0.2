# /strategy:memo

## MANDATORY: Use the strategy-memo Skill

**You MUST use the `strategy-memo` skill located at `.claude/skills/workflows/strategy-memo/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using strategy-memo to generate formal strategic decision documentation"
2. **Read the skill**: Load `.claude/skills/workflows/strategy-memo/SKILL.md`
3. **Follow exactly**: Execute the skill's systematic process

## Purpose

Generate formal strategic decision memo with:
- **Systematic extraction** from session artifacts (not narrative construction)
- **MECE structure** (Problem→Evidence→Framework→Options→Recommendation)
- **Framework-driven analysis** with specific findings
- **Quantitative grounding** where appropriate
- **Concrete scenarios** and examples
- **Evidence-based recommendations** with citations
- **Quality gates** before completion

## Key Differences from Narrative Approach

This is NOT a narrative writing exercise. It is a systematic extraction process:
- Extract content from session artifacts, don't construct stories
- Preserve quantitative data and concrete examples
- Apply frameworks rigorously with specific findings
- Validate citations with verbatim quotes
- Check quality gates before writing file

## Accepted Invocation Styles

**A) Auto-detect latest session (recommended)**
```
/strategy:memo
```
Finds most recent completed strategy session and generates memo.

**B) Specify session path**
```
/strategy:memo --session="/datasets/strategy/sessions/2025/08-11_pricing-strategy/"
/strategy:memo --session-date="2025-08-11" --topic="pricing-strategy"
```

**C) Standalone memo (no prior session)**
```
/strategy:memo --standalone --topic="competitive-analysis"
```
Will gather context, apply framework, and build memo interactively.

**D) Custom memo parameters**
```
/strategy:memo --title="Q4 Pricing Strategy" --stakeholders="Jay,Nathan"
```

**E) YAML ARGS block**
```
/strategy:memo
ARGS:
  session_path: "/datasets/strategy/sessions/2025/08-11_pricing-strategy/"
  title: "Agency Pricing Model Launch Decision"
  decision_type: "strategic"
  stakeholders: ["Jay Jenkins", "Nathan Snell"]
```

## What Makes a Good Memo

Based on strategic decision-making best practices:

**Structure & Organization (MECE)**:
- Clear problem statement (1-2 sentences)
- Evidence section with research and framework findings
- Options with systematic pros/cons/impact analysis
- Clear recommendation with multi-point rationale
- Risk management with likelihood/impact

**Analytical Rigor**:
- Framework application with specific findings (e.g., "Porter's Five Forces: Buyer Power HIGH due to...")
- Quantitative data preserved (percentages, targets, metrics)
- Concrete scenarios and examples (not abstractions)
- Trade-off analysis comparing options
- Measurable success criteria

**Evidence & Citations**:
- All claims backed by research sources or customer signals
- Verbatim quotes (5-25 words) for key insights
- Accessible citation paths
- No "(source needed)" markers

**Strategic Focus**:
- Strategic decisions, not implementation project plans
- High-level timeline only (strategic phases)
- Appropriate detail for decision type
- Clear stakeholder considerations

## Quality Gates

The skill enforces these gates before writing:

**Structure validation** - All required sections present
**Content validation** - Quantitative data preserved, concrete examples included
**Citation validation** - All sources verified with verbatim quotes
**Completeness check** - Framework integrated, metrics measurable, risks assessed

## Common Issues to Avoid

**From evaluation of past outputs:**

❌ Narrative-focused without systematic framework application
❌ High-level concepts without concrete scenarios
❌ Vague abstractions instead of specific numbers
❌ Options without trade-off analysis
❌ Missing stakeholder mapping for relevant decisions
❌ Risks without likelihood/impact ratings
❌ Success criteria that aren't measurable
❌ Implementation details mixed with strategy

✅ Framework-driven with specific findings
✅ Concrete examples (e.g., "Agency with 15 clients, $50k MRR")
✅ Quantitative where appropriate (30% churn, 12-month timeline)
✅ Systematic options comparison with evidence
✅ Stakeholder analysis when decision impacts multiple groups
✅ Risk assessment with likelihood/impact and mitigations
✅ Specific, measurable metrics with timelines
✅ Strategic guidance only (not project plans)

## No Rationalization

- Citation compliance is mandatory
- Quality gates must pass before file write
- If session artifacts incomplete, stop and request completion
- If citations can't be verified, flag for user to provide sources

## Output Location

Memos written to: `datasets/strategy/memos/{YYYY}/{MM-DD}_{decision-slug}.md`

Session archived to: `datasets/strategy/archive/{YYYY}/{MM-DD}_{topic}/` (if from session)

---

**Remember**: The skill contains detailed templates, validation steps, and quality checklists. Follow the skill exactly for best results.
