# /project:ship-it

## End-to-End Product Package (Phases 1–6) — Sub-Agent Orchestration

This is the "do all this and make sure it's amazing" command. You are the **orchestrator** — a thin coordination layer that dispatches 7 sub-agents across 6 phases, runs quality gates between each, and handles PM decision points. You do NOT run skills inline. Sub-agents do the deep work in fresh context windows. Artifacts on disk are the state transfer mechanism.

**Your job**: Manage the sequence, verify quality at each gate, handle PM interactions for key decisions, and keep the overall process on track. Stay lean — don't accumulate artifact content in your context when you can read summaries from disk.

**Model requirement**: All sub-agents MUST be dispatched using `model: "opus"`. Do not use Haiku for any sub-agent in this pipeline — artifact quality depends on the strongest available model.

## Arguments

- `--topic "feature X"` — Start from a topic or problem statement
- `--from-transcript ./path/to/transcript.md` — Start from a meeting transcript
- `--skip-expand` — Skip the Ambition Expander
- `--skip-swag` — Skip the business case modeling

## Step 0: Establish the Product Package Folder

Create the package folder where ALL artifacts will live:

```
datasets/product/packages/{YYYY}/{slug}/
```

Derive the slug from `--topic` if provided, or ask the PM for the initiative name. **Announce the folder path before starting.**

---

## PHASES 1–3: DISCOVERY THROUGH CONTEXT

### Phase 1: Discovery & Context Intake (Orchestrator — Direct)

**Run this directly in the orchestrator.** This is the PM's foundational conversation.

1. If `--topic` was provided, use it as the starting problem statement
2. If `--from-transcript` was provided, process the transcript for context
3. Run `/project:create-notes` or use Context Gathering skills to produce the Context Brief through interactive conversation with the PM

**Output**: `{package}/context-brief.md`

**Gate 1**: Verify context-brief.md contains at least one clearly stated customer problem backed by data. If not, ask the PM for more input before proceeding.

---

### Phase 2: Vision Articulation (Sub-Agent 1)

#### Dispatch: Vision Clarifier Agent

> You are the Vision Clarifier agent. Your job is to articulate the product vision through structured PM interrogation and document generation.
>
> **Skill to follow**: Read and execute `.claude/skills/workflows/vision-clarifier/SKILL.md`
>
> **Read from disk**:
> - `{package}/context-brief.md`
>
> **Templates to use**:
> - `datasets/product/templates/press-release-external.md`
> - `datasets/product/templates/press-release-internal.md`
> - `datasets/product/templates/one-pager.md`
>
> **Write to disk**:
> - `{package}/press-release-external.md`
> - `{package}/press-release-internal.md`
> - `{package}/one-pager.md`
>
> **PM interaction**: YES — walk the PM through the interrogation loop. Do not skip questions.
>
> **When done**: Report which artifacts were created and any concerns about vision clarity.

**Gate 2**: Verify all 3 files exist. Read the one-pager to confirm it supports a 10-minute pitch. Flag issues to PM if needed.

---

### Phase 3: Knowledge Base & Edge Cases (Sub-Agents 2 + 3, Parallel)

**Dispatch BOTH agents simultaneously using parallel agent dispatch.**

#### Dispatch: Devils Advocate Agent (3a)

> You are the Devils Advocate agent. Your job is to interrogate this product vision from every skeptical angle and produce a comprehensive Living FAQ.
>
> **Skill to follow**: Read and execute `.claude/skills/workflows/devils-advocate/SKILL.md`
>
> **Read from disk**:
> - `{package}/context-brief.md`
> - `{package}/press-release-external.md`
> - `{package}/press-release-internal.md`
> - `{package}/one-pager.md`
>
> **Template**: `datasets/product/templates/living-faq.md`
>
> **Write to disk**: `{package}/living-faq.md`
>
> **PM interaction**: NO — generate autonomously. Mark answers as "DRAFT — PM review needed".
>
> **When done**: Report question counts by priority and count of blocking/unanswered items.

#### Dispatch: Agentic API Designer Agent (3b)

> You are the Agentic API Designer agent. Your job is to design a complete agent-consumable API from the product vision artifacts.
>
> **Skill to follow**: Read and execute `.claude/skills/workflows/agentic-api-designer/SKILL.md`
>
> **Read from disk**:
> - `{package}/context-brief.md`
> - `{package}/press-release-external.md`
> - `{package}/press-release-internal.md`
> - `{package}/one-pager.md`
>
> **Templates**: `datasets/product/templates/agentic-api-design.md`, `datasets/product/templates/api-agent-scenarios.md`
>
> **Write to disk**: `{package}/agentic-api-design.md`, `{package}/api-agent-scenarios.md`
>
> **PM interaction**: NO — generate autonomously.
>
> **When done**: Report confirmation and list core resources in the resource model.

**Gate 3**:
1. Read `living-faq.md` — if any `blocking` questions are `UNANSWERED`, present them to the PM and collect answers. Update FAQ with PM answers marked FINAL. Update status counts.
2. Read `agentic-api-design.md` — verify Resource Model and Capability Inventory sections exist.
3. Cross-reference: do blocking FAQ items challenge API design assumptions? Flag if so.

---

### Status Checkpoint (Phases 1–3 Complete)

Briefly summarize what was produced in Phases 1–3:
- List the 7 artifacts created
- Note any open issues or PM decisions made
- **Do NOT stop for a full review** — continue to Phase 4

---

## PHASES 4–6: PRD THROUGH DELIVERY

### Phase 4: Ambitious PRD Generation (Sub-Agent 4)

#### Dispatch: PRD Creator Agent

> You are the PRD Creator agent. Your job is to synthesize all upstream discovery artifacts into an ambitious, validated PRD.
>
> **Skill to follow**: Read and execute `.claude/skills/workflows/prd-creation/SKILL.md`
>
> **Read from disk** (all upstream artifacts):
> - `{package}/context-brief.md`
> - `{package}/press-release-external.md`
> - `{package}/press-release-internal.md`
> - `{package}/one-pager.md`
> - `{package}/living-faq.md`
> - `{package}/agentic-api-design.md`
> - `{package}/api-agent-scenarios.md`
>
> **Templates and quality gates**:
> - `datasets/product/templates/prd-template.md`
> - `.claude/skills/quality-gates/prd-validation/SKILL.md`
>
> **Write to disk** (dual location):
> - `{package}/PRD_{slug}.md`
> - `datasets/product/prds/{YYYY}/PRD_{slug}.md`
>
> **PM interaction**: YES — confirm pre-populated sections, fill genuinely missing sections. Do NOT re-ask for info already in upstream artifacts.
>
> **Important**: Inherit all `important` and `tracked` UNANSWERED items from Living FAQ into Open Questions.
>
> **When done**: Report PRD status, which sections were pre-populated vs. PM-provided, and any validation warnings.

**Gate 4**: Verify PRD exists with at least "Drafting" status. Check key sections are populated.

---

### Phase 4b: Ambition Expansion (Sub-Agent 5) — unless `--skip-expand`

#### Dispatch: Ambition Expander Agent

> You are the Ambition Expander agent. Your job is to push the PRD's ambition ceiling higher.
>
> **Skill to follow**: Read and execute `.claude/skills/workflows/ambition-expander/SKILL.md`
>
> **Read from disk**:
> - `{package}/PRD_{slug}.md`
> - `{package}/context-brief.md`
> - `{package}/press-release-external.md`
> - `{package}/press-release-internal.md`
> - `{package}/living-faq.md`
> - `{package}/agentic-api-design.md`
>
> **Template**: `datasets/product/templates/expansion-proposals.md`
>
> **Write to disk**: `{package}/expansion-proposals.md`
>
> **PM interaction**: NO — generate proposals autonomously.
>
> **When done**: Report proposal counts by category and effort distribution.

#### Orchestrator: Expansion Proposal Review (PM Decision Point)

**Handle directly in the orchestrator. This pause is non-negotiable.**

1. Read `{package}/expansion-proposals.md`
2. Present each proposal to the PM (category, description, outcome, evidence, effort)
3. Collect Accept/Reject + rationale for each
4. Update `expansion-proposals.md` with PM Decision Log
5. Fold accepted items into PRD (update both locations)

---

### Phase 5: Validation & Red Team (Sub-Agent 6)

#### Dispatch: Red Team Reviewer Agent

> You are the Red Team Reviewer agent. Your job is to find every gap and failure mode — not to cut scope, but to make the ambitious plan robust.
>
> **Skill to follow**: Read and execute `.claude/skills/workflows/red-team-reviewer/SKILL.md`
>
> **Read from disk** (ALL artifacts):
> - `{package}/PRD_{slug}.md`
> - `{package}/context-brief.md`
> - `{package}/press-release-external.md`
> - `{package}/press-release-internal.md`
> - `{package}/one-pager.md`
> - `{package}/living-faq.md`
> - `{package}/agentic-api-design.md`
> - `{package}/api-agent-scenarios.md`
> - `{package}/expansion-proposals.md` (if exists)
>
> **Template**: `datasets/product/templates/red-team-report.md`
>
> **Write to disk**:
> - `{package}/red-team-report.md`
> - `{package}/living-faq.md` (append new questions, marked "DRAFT — PM review needed")
>
> **PM interaction**: NO — conduct full review autonomously.
>
> **When done**: Report findings count by severity and list all critical finding IDs with summaries.

#### Orchestrator: Critical Findings Review (PM Decision Point)

**Handle directly in the orchestrator. This pause is non-negotiable.**

1. Read `{package}/red-team-report.md`
2. Present all `critical` findings to PM (ID, PRD reference, description, recommended fix)
3. PM confirms fixes are adequate
4. Update PRD with critical fixes (both locations)
5. Track major findings (don't block)
6. Check updated `living-faq.md` for new blocking questions

---

### Phase 6: Business Case (Sub-Agent 7) — unless `--skip-swag`

#### Dispatch: SWAG Modeler Agent

> You are the SWAG Modeler agent. Your job is to build a rigorous-but-honest business case.
>
> **Skill to follow**: Read and execute `.claude/skills/workflows/swag-modeler/SKILL.md`
>
> **Read from disk**:
> - `{package}/PRD_{slug}.md`
> - `{package}/context-brief.md`
> - `{package}/press-release-external.md`
> - `{package}/press-release-internal.md`
> - `{package}/red-team-report.md`
>
> **Template**: `datasets/product/templates/business-case-swag.md`
>
> **Write to disk**: `{package}/business-case-swag.md`
>
> **PM interaction**: NO — build autonomously.
>
> **When done**: Report the executive summary paragraph and top 3 most sensitive assumptions.

---

## COMPLETE PACKAGE DELIVERY

Present the complete product package:

1. **Package folder**: `datasets/product/packages/{YYYY}/{slug}/`
2. **List every artifact** with one-line summaries
3. **Highlight the 3 most important decisions/findings**
4. **Call out any remaining UNANSWERED questions** in the Living FAQ
5. **Note critical findings** that were addressed and how
6. **Summarize the business case** executive summary

## Complete Package Folder Structure

```
datasets/product/packages/{YYYY}/{slug}/
├── context-brief.md              (Phase 1)
├── press-release-external.md     (Phase 2)
├── press-release-internal.md     (Phase 2)
├── one-pager.md                  (Phase 2)
├── living-faq.md                 (Phase 3, updated throughout)
├── agentic-api-design.md         (Phase 3)
├── api-agent-scenarios.md        (Phase 3)
├── PRD_{slug}.md                 (Phase 4)
├── expansion-proposals.md        (Phase 4)
├── red-team-report.md            (Phase 5)
└── business-case-swag.md         (Phase 6)
```

The PRD is also written to `datasets/product/prds/{YYYY}/PRD_{slug}.md` for backlog/roadmap integration.

## When to Use

- When you have sufficient context and want to let the system rip
- Re-running the entire pipeline with new or updated input context
- Generating multiple complete packages for comparison
- When you've been through the process once and trust the intermediate outputs

## Philosophy

This pipeline is cheap to run. Feed it different input context, run it multiple times, compare outputs, iterate. Don't be precious about a single pass.

## PM Review Points

While `/ship-it` minimizes pauses, the PM MUST still make judgment calls at:
- **Expansion proposals**: Accept or reject each one (auto-pauses here)
- **Critical red team findings**: Confirm fixes are adequate

These pauses are non-negotiable even in end-to-end mode. The PM decides, agents propose.
