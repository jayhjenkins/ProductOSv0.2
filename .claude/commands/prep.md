# /project:prep

## Discovery Through Context (Phases 1–3) — Sub-Agent Orchestration

You are the **orchestrator**. Your job is to coordinate the discovery pipeline by dispatching sub-agents for heavy generation work, running quality gates between phases, and handling PM interactions for key decisions. You stay thin — sub-agents do the deep work in fresh context windows. Artifacts on disk are the state transfer mechanism.

**Do NOT run skills inline.** Dispatch sub-agents for each phase. Read their outputs from disk to verify quality before proceeding.

**Model requirement**: All sub-agents MUST be dispatched using `model: "opus"`. Do not use Sonnet or Haiku for any sub-agent in this pipeline — artifact quality depends on the strongest available model.

## Arguments

- `--skip-discover` — Skip Phase 1 discovery, use existing Context Brief
- `--topic "feature X"` — Pass in the starting topic or problem statement

## Step 0: Establish the Product Package Folder

Create the package folder where ALL artifacts will live:

```
datasets/product/packages/{YYYY}/{slug}/
```

**How to determine the slug:**
- If `--topic` is provided, derive the slug from it (lowercase, hyphens, no special chars)
- If resuming an existing package, use the existing folder
- If neither, ask the PM for the initiative name

**Create the folder** if it doesn't exist. All subsequent sub-agents read from and write to this folder.

**Announce**: "Product package folder: `datasets/product/packages/{YYYY}/{slug}/`"

---

## Phase 1: Discovery & Context Intake (Orchestrator — Direct)

**This phase runs directly in the orchestrator, NOT as a sub-agent.** This is the PM's foundational conversation that seeds everything else.

1. If `--skip-discover` was provided, verify an existing Context Brief exists in the package folder and skip to Phase 2
2. If `--topic` was provided, use it as the starting problem statement
3. Run `/project:create-notes` or use Context Gathering skills to produce the Context Brief through interactive conversation with the PM

**Output**: `{package}/context-brief.md`

### Gate 1: Context Brief Quality Check

Before proceeding, verify:
- `{package}/context-brief.md` exists
- It contains at least one clearly stated customer problem backed by data
- If not, STOP and ask the PM for more input

---

## Phase 2: Vision Articulation (Sub-Agent)

### Dispatch: Vision Clarifier Agent

**Task**: Run the structured interrogation loop with the PM, then generate both press releases and the one-pager from the Context Brief.

**How to dispatch**: Launch a sub-agent with the following instructions:

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
> **PM interaction**: YES — walk the PM through the interrogation loop as described in the skill. Do not skip questions.
>
> **When done**: Report back which artifacts were created and any concerns about vision clarity.

### Gate 2: Vision Artifacts Quality Check

After the sub-agent completes:
1. Verify all 3 files exist: `press-release-external.md`, `press-release-internal.md`, `one-pager.md`
2. Read the one-pager — confirm it could support a 10-minute pitch (coherent problem/solution/differentiators)
3. If any artifact is missing or the one-pager is incoherent, flag to the PM before proceeding

---

## Phase 3: Knowledge Base & Edge Case Mapping (Parallel Sub-Agents)

**Dispatch BOTH sub-agents simultaneously.** These run in parallel — use parallel agent dispatch.

### Dispatch: Devils Advocate Agent (Phase 3a)

**Task**: Stress-test the product vision from 6 adversarial perspectives and produce the Living FAQ.

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
> **Template to use**:
> - `datasets/product/templates/living-faq.md`
>
> **Write to disk**:
> - `{package}/living-faq.md`
>
> **PM interaction**: NO — generate autonomously. Mark any answers as "DRAFT — PM review needed".
>
> **When done**: Report back the count of questions by priority tag (blocking/important/tracked/deferred) and how many blocking items remain UNANSWERED.

### Dispatch: Agentic API Designer Agent (Phase 3b)

**Task**: Design the agent-first API surface and workflow scenarios from upstream artifacts.

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
> **Templates to use**:
> - `datasets/product/templates/agentic-api-design.md`
> - `datasets/product/templates/api-agent-scenarios.md`
>
> **Write to disk**:
> - `{package}/agentic-api-design.md`
> - `{package}/api-agent-scenarios.md`
>
> **PM interaction**: NO — generate autonomously.
>
> **When done**: Report back confirmation that both artifacts were created, and list the core resources identified in the resource model.

### Gate 3: Knowledge Base Quality Check

After BOTH sub-agents complete:

1. **Living FAQ check**: Read `{package}/living-faq.md`
   - Count `blocking` questions that are `UNANSWERED`
   - If any blocking questions remain unanswered, present them to the PM and wait for answers
   - Update the FAQ with PM's answers (mark as FINAL, not DRAFT)
   - Update the status counts in the FAQ header

2. **API Design check**: Read `{package}/agentic-api-design.md`
   - Verify it has a Resource Model section with at least one resource defined
   - Verify it has a Capability Inventory section
   - If either is missing, flag to the PM

3. **Cross-reference**: Do any blocking FAQ questions directly challenge assumptions in the API design? If so, flag for PM review.

---

## STOP — Present Results to PM

Present all artifacts to the PM for review:

1. **List all generated artifacts** with full paths:
   - `{package}/context-brief.md`
   - `{package}/press-release-external.md`
   - `{package}/press-release-internal.md`
   - `{package}/one-pager.md`
   - `{package}/living-faq.md`
   - `{package}/agentic-api-design.md`
   - `{package}/api-agent-scenarios.md`

2. **Highlight** any open questions or incomplete sections
3. **Remind PM** of the package folder location
4. **Suggest** running `/project:build` when the PM is satisfied with upstream artifacts

## Package Folder Structure After `/prep`

```
datasets/product/packages/{YYYY}/{slug}/
├── context-brief.md
├── press-release-external.md
├── press-release-internal.md
├── one-pager.md
├── living-faq.md
├── agentic-api-design.md
└── api-agent-scenarios.md
```

## When to Use

When you have raw inputs (a problem statement, transcripts, a rough idea) and want to rapidly build out all context artifacts. Run this first, review outputs, then run `/project:build` to continue.

## This Command is Cheap to Run

Feed it different input context, run it multiple times, compare outputs, iterate. The system is designed to be re-run, not to be precious about a single pass.
