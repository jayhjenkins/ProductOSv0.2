# /project:ship-it

## End-to-End Product Package (Phases 1–7) — Sub-Agent Orchestration

This is the "do all this and make sure it's amazing" command. You are the **orchestrator** — a thin coordination layer that dispatches 7 sub-agents across Phases 1–6, runs quality gates between each, handles PM decision points, and (in Phase 7) drives a short interactive Jira Feature handoff directly. You do NOT run skills inline for Phases 1–6. Sub-agents do the deep work in fresh context windows. Artifacts on disk are the state transfer mechanism.

**Your job**: Manage the sequence, verify quality at each gate, handle PM interactions for key decisions, and keep the overall process on track. Stay lean — don't accumulate artifact content in your context when you can read summaries from disk.

**Model requirement**: All sub-agents MUST be dispatched using `model: "opus"`. Do not use Haiku for any sub-agent in this pipeline — artifact quality depends on the strongest available model.

## Arguments

- `--topic "feature X"` — Start from a topic or problem statement
- `--from-transcript ./path/to/transcript.md` — Start from a meeting transcript
- `--skip-expand` — Skip the Ambition Expander
- `--skip-swag` — Skip the business case modeling
- `--skip-jira` — Skip the Phase 7 Jira Feature handoff (no draft task created)
- `--jira-only --package <path>` — Run only Phase 7 against an existing package folder (skips Phases 1–6). Useful when a package already exists and you just need the Jira Feature draft.

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
> **Skill to follow**: Read and execute `.claude/skills/workflow-vision-clarifier/SKILL.md`
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

> You are the Devils Advocate agent. Your job is to stress-test this product vision from business-user and customer perspectives and produce a short, audience-focused Living FAQ.
>
> **Skill to follow**: Read and execute `.claude/skills/workflow-devils-advocate/SKILL.md`
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
> **PM interaction**: NO — generate autonomously. Mark any draft answers clearly; pure-PM-input items belong in the "Open Questions for PM" section.
>
> **Hard caps**: ≤20 questions total, ≤50 words per answer, ≤2,000 words total. No engineering/architecture/security-implementation questions.
>
> **When done**: Report question counts by audience (CSM, PS, Support, New Customer, Existing Customer) and the number of items in "Open Questions for PM".

#### Dispatch: AI Agent Scenarios Designer Agent (3b)

> You are the AI Agent Scenarios Designer agent. Your job is to define the jobs an AI agent must accomplish with this feature and the capability requirements for engineering — NOT to design the API shape.
>
> **Skill to follow**: Read and execute `.claude/skills/workflow-agentic-api-designer/SKILL.md`
>
> **Read from disk**:
> - `{package}/context-brief.md`
> - `{package}/press-release-external.md`
> - `{package}/press-release-internal.md`
> - `{package}/one-pager.md`
>
> **Template**: `datasets/product/templates/ai-agent-scenarios.md`
>
> **Write to disk**: `{package}/ai-agent-scenarios.md`
>
> **PM interaction**: NO — generate autonomously.
>
> **Hard rule**: No HTTP methods/paths, no JSON schemas, no resource-model tables, no state machines. Scenarios in prose. Capability requirements as bullets.
>
> **When done**: Report confirmation and list the top use cases in the Use Case Inventory.

**Gate 3**:
1. Read `living-faq.md` — if the "Open Questions for PM" section has any items, present them to the PM and collect answers. Update the FAQ with the PM's answers.
2. Read `ai-agent-scenarios.md` — verify the Use Case Inventory and at least 3 scenarios exist in prose form (no HTTP/JSON).
3. Cross-reference: do any open FAQ items challenge the scenarios? Flag if so.

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
> **PM interaction**: YES — confirm pre-populated sections, fill genuinely missing sections. Do NOT re-ask for info already in upstream artifacts.
>
> **Important**: Inherit every item from the Living FAQ's "Open Questions for PM" section that remains UNANSWERED into the PRD Open Questions.
>
> **When done**: Report PRD status, which sections were pre-populated vs. PM-provided, and any validation warnings.

**Gate 4**: Verify PRD exists with at least "Drafting" status. Check key sections are populated.

---

### Phase 4b: Ambition Expansion (Sub-Agent 5) — unless `--skip-expand`

#### Dispatch: Ambition Expander Agent

> You are the Ambition Expander agent. Your job is to push the PRD's ambition ceiling higher.
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
> **Template**: `datasets/product/templates/red-team-report.md`
>
> **Write to disk**:
> - `{package}/red-team-report.md` (ONLY file written; do NOT append to the Living FAQ — abuse/misuse and harm scenarios go in the red team report's Harm Scenarios section)
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

---

### Phase 6: Business Case (Sub-Agent 7) — unless `--skip-swag`

#### Dispatch: SWAG Modeler Agent

> You are the SWAG Modeler agent. Your job is to build a rigorous-but-honest business case.
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
> **Template**: `datasets/product/templates/business-case-swag.md`
>
> **Write to disk**: `{package}/business-case-swag.md`
>
> **PM interaction**: NO — build autonomously.
>
> **When done**: Report the executive summary paragraph and top 3 most sensitive assumptions.

---

### Phase 7: Jira Feature Handoff (Orchestrator — Direct) — unless `--skip-jira`

Sam's 2026-05-22 process refresh made the Jira **Feature** the source of truth for downstream comms. Three fields drive that workflow: **Spec Reference** (URL of the spec/PRD), **GTM Date**, and **EA Date**. Phase 7 turns this package into a published-ready Jira Feature draft.

**Handle this directly in the orchestrator — no sub-agent.** It is interactive and short.

#### Step 7.1: Confirm intent

Ask the PM:
> "All artifacts are in `{package}`. Want to draft the Jira Feature now so engineering can pick it up? (Y/N)"

- If `--skip-jira` or the PM declines: end Phase 7 with the reminder "Run `/jira:create --feature` later, or re-run with `--jira-only --package {package}`."
- If yes: continue.

#### Step 7.2: Get the Spec Reference URL (manual publish gate)

The PRD's Word/SharePoint URL becomes both the Jira **Spec Reference** field value and the in-body link. We also need the internal press release URL for the description body.

Ask:
> "To populate Spec Reference, the PRD needs a Word URL. Pick one:
> (a) Publish the package to SharePoint now (manual confirmation — same rule as always).
> (b) Paste a URL I already have.
> (c) Skip — draft with Spec Reference blank, fill in later."

- **(a)**: Run `python3 scripts/doc_sync.py sync-folder {package} --json`. Parse the JSON output (shape: `{"folder": "...", "files": [{"file": "...", "url": "...", ...}]}`). Capture two URLs:
  - The `url` from the entry whose `file` matches `PRD_{slug}.md` → **Spec Reference** field + "Full PRD" line in the description.
  - The `url` from the entry whose `file` matches `press-release-internal.md` → "Internal Press Release" line in the description.
  Skip a URL silently if its entry has `status: "error: ..."` or `url` is empty.
- **(b)**: Prompt twice — once for the PRD URL (Spec Reference) and once for the internal press release URL. Either can be skipped.
- **(c)**: Leave both empty.

#### Step 7.3: Gather Feature fields

Ask in order, accepting `TBD` or empty for each date field (these mean "leave the Jira field blank — Sam's process accepts filling them in later"):

1. **Feature Name** — default to `{slug}` title-cased; allow edit.
2. **GTM Date** — `YYYY-MM-DD`, or `TBD`/empty.
3. **EA Date** — `YYYY-MM-DD`, or `TBD`/empty. (Early-access date; typically before GTM.)
4. **Client Commitment** — `CAI` / `Vision` / none.

Do **not** ask about Release Notes, Priority, Components, or Regression Area — those are set in Jira when the issue transitions out of Refinement.

#### Step 7.4: Build the description body (lean)

The description has exactly, in this order:

1. **Outcome paragraph** — 1–3 sentences lifted from `one-pager.md` / `press-release-external.md` (the "why we're building this").
2. **Full PRD line** — `Full PRD: {PRD Word URL}`. Omit silently if no URL.
3. **Internal Press Release line** — `Internal Press Release: {press-release-internal Word URL}`. Omit silently if no URL.
4. **AC seed** — 3–5 bullets lifted from the PRD's Requirements section as placeholders for engineering to refine.

Explicitly **omit**: meeting framing, name-dropping, version narrative, TASK-NNNN IDs, local paths, transcript filenames.

#### Step 7.5: Save as a JIRA_DRAFT task

Create the task. Build the description argument as a single string containing the JIRA_DRAFT block plus the body sections — the existing `task.sh add` writes `--description` into the body, and `jira_publish.py` parses the `<!-- JIRA_DRAFT -->…<!-- /JIRA_DRAFT -->` block wherever it appears.

```
./scripts/task.sh add "Publish Jira Feature: {Feature Name}" \
  -q human -p medium -d product \
  --description "$(cat <<'EOF'
<!-- JIRA_DRAFT -->
<!-- JIRA_TYPE:Feature -->
<!-- JIRA_SUMMARY:{summary} -->
<!-- JIRA_LABELS:home_aidlc -->
<!-- JIRA_FEATURE_NAME:{feature name} -->
<!-- JIRA_GTM_DATE:{YYYY-MM-DD or empty} -->
<!-- JIRA_EA_DATE:{YYYY-MM-DD or empty} -->
<!-- JIRA_SPEC_REFERENCE:{PRD Word URL or empty} -->
<!-- JIRA_CLIENT_COMMITMENT:{CAI/Vision/empty} -->

### Summary
{summary}

### Description
{outcome paragraph}

Full PRD: {PRD Word URL}
Internal Press Release: {press-release-internal Word URL}

**Acceptance Criteria (seed)**
- {AC bullet 1}
- {AC bullet 2}
- {AC bullet 3}

### Fields
- Type: Feature
- Labels: home_aidlc (Features go to the AI DLC swim lane)
<!-- /JIRA_DRAFT -->
EOF
)"
```

Print the TASK ID and the task-board URL. End with:
> "Draft saved at TASK-NNNN. Open the task board, review the draft, click **Publish to Jira** when ready. Sam's process is satisfied as long as Spec Reference is set — GTM/EA dates can be filled in later in the Jira UI."

---

## COMPLETE PACKAGE DELIVERY

Present the complete product package:

1. **Package folder**: `datasets/product/packages/{YYYY}/{slug}/`
2. **List every artifact** with one-line summaries
3. **Highlight the 3 most important decisions/findings**
4. **Call out any remaining UNANSWERED items** in the Living FAQ's "Open Questions for PM" section
5. **Note critical findings** that were addressed and how
6. **Summarize the business case** executive summary

## Complete Package Folder Structure

```
datasets/product/packages/{YYYY}/{slug}/
├── context-brief.md              (Phase 1)
├── press-release-external.md     (Phase 2)
├── press-release-internal.md     (Phase 2)
├── one-pager.md                  (Phase 2)
├── living-faq.md                 (Phase 3, PM-edited after Phase 3)
├── ai-agent-scenarios.md         (Phase 3)
├── PRD_{slug}.md                 (Phase 4)
├── expansion-proposals.md        (Phase 4)
├── red-team-report.md            (Phase 5)
└── business-case-swag.md         (Phase 6)
```

The PRD is also written to `datasets/product/prds/{YYYY}/PRD_{slug}.md` for backlog/roadmap integration.

Phase 7 produces one side-effect outside the package folder: a `human`-queue task titled `Publish Jira Feature: {Feature Name}` containing a JIRA_DRAFT block. The PM publishes it from the task board.

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
- **Jira Feature handoff (Phase 7)**: Confirm intent, decide on manual publish vs. paste vs. skip for the Spec Reference URL, and provide GTM/EA dates (TBD allowed)

These pauses are non-negotiable even in end-to-end mode. The PM decides, agents propose.