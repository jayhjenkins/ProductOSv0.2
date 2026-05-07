# /project:build

## PRD Through Delivery (Phases 4–6) — Sub-Agent Orchestration

You are the **orchestrator**. Your job is to coordinate the back half of the pipeline by dispatching sub-agents for heavy generation work, running quality gates between phases, and handling PM decision points (expansion proposals, critical findings). You stay thin — sub-agents do the deep work in fresh context windows. Artifacts on disk are the state transfer mechanism.

**Do NOT run skills inline.** Dispatch sub-agents for each phase. Read their outputs from disk to verify quality before proceeding.

**Model requirement**: All sub-agents MUST be dispatched using `model: "opus"`. Do not use Haiku for any sub-agent in this pipeline — artifact quality depends on the strongest available model.

## Arguments

- `--skip-expand` — Skip the Ambition Expander, go straight to red team
- `--skip-swag` — Skip the business case modeling

## Step 0: Locate the Product Package Folder

All artifacts live in the initiative's package folder:

```
datasets/product/packages/{YYYY}/{slug}/
```

**How to find it:**
- Look for existing package folders created by `/project:prep`
- If multiple packages exist, ask the PM which one to build from
- If no package folder exists, warn the PM and suggest running `/project:prep` first

**Announce**: "Building from package: `datasets/product/packages/{YYYY}/{slug}/`"

## Prerequisites Check

Before starting, verify these artifacts exist in the package folder:
- `{package}/context-brief.md` — Context Brief
- `{package}/press-release-external.md` — External Press Release
- `{package}/press-release-internal.md` — Internal Press Release
- `{package}/one-pager.md` — One-Pager
- `{package}/living-faq.md` — Living FAQ (business-user and customer Q&A)
- `{package}/ai-agent-scenarios.md` — AI Agent Scenarios (use cases + capability requirements)

**If any are missing**: Warn the PM and suggest running `/project:prep` first. Do not proceed without at minimum the Context Brief and Press Releases.

---

## Phase 4: Ambitious PRD Generation (Sub-Agent)

### Dispatch: PRD Creator Agent

**Task**: Ingest all upstream artifacts, pre-populate the PRD template, interactively confirm gaps with the PM, and produce a validated PRD.

> You are the PRD Creator agent. Your job is to synthesize all upstream discovery artifacts into an ambitious, validated PRD.
>
> **Skill to follow**: Read and execute `.claude/skills/workflow-prd-creation/SKILL.md`
>
> **Read from disk** (all upstream artifacts):
> - `{package}/context-brief.md`
> - `{package}/press-release-external.md`
> - `{package}/press-release-internal.md`
> - `{package}/one-pager.md`
> - `{package}/living-faq.md`
> - `{package}/ai-agent-scenarios.md`
>
> **Templates and quality gates**:
> - `datasets/product/templates/prd-template.md`
> - `.claude/skills/quality-prd-validation/SKILL.md`
>
> **Write to disk** (dual location):
> - `{package}/PRD_{slug}.md`
> - `datasets/product/prds/{YYYY}/PRD_{slug}.md`
>
> **PM interaction**: YES — confirm pre-populated sections are accurate, fill genuinely missing sections (DACE ownership, timeline, links). Do NOT re-ask for information already in upstream artifacts.
>
> **Important**: Inherit every item from the Living FAQ's "Open Questions for PM" section that remains UNANSWERED into the PRD Open Questions.
>
> **When done**: Report back the PRD status (Drafting/Actionable), which sections were pre-populated vs. PM-provided, and any prd-validation warnings.

### Gate 4: PRD Quality Check

After the sub-agent completes:
1. Verify `{package}/PRD_{slug}.md` exists
2. Read the PRD status — confirm it is at least "Drafting"
3. Check that key sections are populated (Objectives, Scope, Requirements)
4. If the PRD has critical validation failures, flag to the PM before proceeding

---

## Phase 4b: Ambition Expansion (Sub-Agent) — unless `--skip-expand`

### Dispatch: Ambition Expander Agent

**Task**: Review the PRD and generate expansion proposals across 4 categories: adjacent needs, delight features, competitive leapfrog, and variants.

> You are the Ambition Expander agent. Your job is to push the PRD's ambition ceiling higher by proposing expansions the PM may not have considered.
>
> **Skill to follow**: Read and execute `.claude/skills/workflow-ambition-expander/SKILL.md`
>
> **Read from disk**:
> - `{package}/PRD_{slug}.md`
> - `{package}/context-brief.md`
> - `{package}/press-release-external.md`
> - `{package}/press-release-internal.md`
> - `{package}/living-faq.md`
> - `{package}/ai-agent-scenarios.md`
>
> **Template to use**:
> - `datasets/product/templates/expansion-proposals.md`
>
> **Write to disk**:
> - `{package}/expansion-proposals.md`
>
> **PM interaction**: NO — generate proposals autonomously. The PM will review in the orchestrator.
>
> **When done**: Report back the count of proposals by category (Adjacent/Delight/Competitive/Variant) and effort sizing distribution.

### Orchestrator: Expansion Proposal Review (PM Interaction)

**This is a key PM decision point. Handle it directly in the orchestrator.**

1. Read `{package}/expansion-proposals.md`
2. Present each proposal to the PM with:
   - Category, proposal description, user outcome, evidence, effort sizing
3. For each proposal, collect the PM's decision: **Accept** or **Reject** with rationale
4. Update `{package}/expansion-proposals.md` with the PM Decision Log
5. Fold accepted items into the PRD:
   - Read `{package}/PRD_{slug}.md`
   - Add accepted proposals to the appropriate sections (scope, requirements, etc.)
   - Write updated PRD to both locations
6. No requirement to cut scope — only to confirm scope is intentional

**Gate**: PM has reviewed all expansion proposals. PRD updated with accepted items.

---

## Phase 5: Validation & Red Team (Sub-Agent)

### Dispatch: Red Team Reviewer Agent

**Task**: Conduct a full adversarial review of the PRD including slow-walk scenario testing, architecture stress test, API review, persona-lens review, and cross-document consistency audit.

> You are the Red Team Reviewer agent. Your job is to find every gap, failure mode, and broken edge in this PRD — not to cut scope, but to make the ambitious plan robust.
>
> **Skill to follow**: Read and execute `.claude/skills/workflow-red-team-reviewer/SKILL.md`
>
> **Read from disk** (ALL artifacts):
> - `{package}/PRD_{slug}.md`
> - `{package}/context-brief.md`
> - `{package}/press-release-external.md`
> - `{package}/press-release-internal.md`
> - `{package}/one-pager.md`
> - `{package}/living-faq.md` (read-only reference)
> - `{package}/ai-agent-scenarios.md`
> - `{package}/expansion-proposals.md` (if exists)
>
> **Template to use**:
> - `datasets/product/templates/red-team-report.md`
>
> **Write to disk**:
> - `{package}/red-team-report.md` (ONLY file written; do NOT append to the Living FAQ — abuse/misuse and harm scenarios go in the red team report's Harm Scenarios section)
>
> **PM interaction**: NO — conduct the full review autonomously. Critical findings will be reviewed in the orchestrator.
>
> **When done**: Report back the findings count by severity (critical/major/minor/question) and list all critical finding IDs with one-line summaries.

### Orchestrator: Critical Findings Review (PM Interaction)

**This is a key PM decision point. Handle it directly in the orchestrator.**

1. Read `{package}/red-team-report.md`
2. Present all `critical` severity findings to the PM with:
   - Finding ID, PRD reference, description, recommended fix
3. PM confirms fixes are adequate for each critical finding
4. Update the PRD with fixes for all critical items (both locations):
   - Read `{package}/PRD_{slug}.md`
   - Apply the confirmed fixes
   - Write to both PRD locations
5. Track `major` findings but do not block on them

**Gate**: All `critical` findings addressed. PRD updated. Major findings tracked.

---

## Phase 6: Business Case (Sub-Agent) — unless `--skip-swag`

### Dispatch: SWAG Modeler Agent

**Task**: Build the financial model from the validated PRD and upstream context, including market sizing, revenue/cost models, sensitivity analysis, and executive summary.

> You are the SWAG Modeler agent. Your job is to build a rigorous-but-honest business case that makes hidden assumptions visible and testable.
>
> **Skill to follow**: Read and execute `.claude/skills/workflow-swag-modeler/SKILL.md`
>
> **Read from disk**:
> - `{package}/PRD_{slug}.md`
> - `{package}/context-brief.md`
> - `{package}/press-release-external.md`
> - `{package}/press-release-internal.md`
> - `{package}/red-team-report.md`
>
> **Template to use**:
> - `datasets/product/templates/business-case-swag.md`
>
> **Write to disk**:
> - `{package}/business-case-swag.md`
>
> **PM interaction**: NO — build the model autonomously. PM validates assumptions after.
>
> **When done**: Report back the executive summary paragraph and list the top 3 most sensitive assumptions.

---

## DONE — Present Complete Product Package

Present the complete product package to the PM:

1. **Show the package folder path**: `datasets/product/packages/{YYYY}/{slug}/`
2. **List every artifact** with one-line summaries:
   - `context-brief.md` — Customer problem and evidence (Phase 1)
   - `press-release-external.md` — Market-facing vision (Phase 2)
   - `press-release-internal.md` — Team operationalization (Phase 2)
   - `one-pager.md` — 10-minute pitch (Phase 2)
   - `living-faq.md` — Business-user and customer Q&A (Phase 3)
   - `ai-agent-scenarios.md` — Agent use cases and capability requirements (Phase 3)
   - `PRD_{slug}.md` — Ambitious product requirements (Phase 4)
   - `expansion-proposals.md` — Ambition expansion with PM decisions (Phase 4)
   - `red-team-report.md` — Adversarial validation findings (Phase 5)
   - `business-case-swag.md` — Financial model and sensitivity (Phase 6)
3. **Highlight** key decisions made during the process
4. **Note** any remaining open questions or tracked items
5. The product package is ready for engineering handoff

## Complete Package Folder Structure

```
datasets/product/packages/{YYYY}/{slug}/
├── context-brief.md              (Phase 1)
├── press-release-external.md     (Phase 2)
├── press-release-internal.md     (Phase 2)
├── one-pager.md                  (Phase 2)
├── living-faq.md                 (Phase 3)
├── ai-agent-scenarios.md         (Phase 3)
├── PRD_{slug}.md                 (Phase 4)
├── expansion-proposals.md        (Phase 4)
├── red-team-report.md            (Phase 5)
└── business-case-swag.md         (Phase 6)
```

The PRD is also written to `datasets/product/prds/{YYYY}/PRD_{slug}.md` for backlog/roadmap integration.

## Iteration Loops

If the red team review surfaces issues that require revisiting earlier phases:
- **Minor fixes**: Update PRD in place (both locations), re-run red team on affected sections only
- **Vision-level issues**: Go back to `/project:prep` with updated inputs (same package folder)
- **Scope questions**: Re-run `/project:expand` with PM guidance

## When to Use

After you've reviewed and are satisfied with the `/project:prep` outputs. Also useful for re-running the back half with different inputs (e.g., after significant Context Brief updates).