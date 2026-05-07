# /project:prep

## Discovery Through Context (Phases 1–3) — Sub-Agent Orchestration

You are the **orchestrator**. Your job is to coordinate the discovery pipeline by dispatching sub-agents for heavy generation work, running quality gates between phases, and handling PM interactions for key decisions. You stay thin — sub-agents do the deep work in fresh context windows. Artifacts on disk are the state transfer mechanism.

**Do NOT run skills inline.** Dispatch sub-agents for each phase. Read their outputs from disk to verify quality before proceeding.

**Model requirement**: All sub-agents MUST be dispatched using `model: "opus"`. Do not use Haiku for any sub-agent in this pipeline — artifact quality depends on the strongest available model.

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
3. Use the skills as appropriate in the /skills/context-assembly repo (typically, you'll start with the research-gathering.md skill and expand as needed from there) to produce the Context Brief through interactive conversation with the PM or autonomously with your context aggregation and MCP tools.

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

**Task**: Stress-test the product vision from business-user and customer perspectives and produce a short, audience-focused Living FAQ.

> You are the Devils Advocate agent. Your job is to stress-test this product vision from business-user and customer perspectives (CSM, PS, Support, new customer, existing customer) and produce a short, audience-focused Living FAQ.
>
> **Skill to follow**: Read and execute `.claude/skills/workflow-devils-advocate/SKILL.md`
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
> **PM interaction**: NO — generate autonomously. Items requiring PM input belong in the "Open Questions for PM" section.
>
> **Hard caps**: ≤20 questions total, ≤50 words per answer, ≤2,000 words total. No engineering/architecture/security-implementation questions.
>
> **When done**: Report back the question count by audience (CSM, PS, Support, New Customer, Existing Customer) and the number of items in "Open Questions for PM".

### Dispatch: AI Agent Scenarios Designer Agent (Phase 3b)

**Task**: Define agent use cases, jobs-to-be-done scenarios, and capability requirements for engineering — NOT to prescribe API shape.

> You are the AI Agent Scenarios Designer agent. Your job is to define the jobs an AI agent must accomplish with this feature and the capability requirements for engineering. You do NOT design the API shape.
>
> **Skill to follow**: Read and execute `.claude/skills/workflow-agentic-api-designer/SKILL.md`
>
> **Read from disk**:
> - `{package}/context-brief.md`
> - `{package}/press-release-external.md`
> - `{package}/press-release-internal.md`
> - `{package}/one-pager.md`
>
> **Template to use**:
> - `datasets/product/templates/ai-agent-scenarios.md`
>
> **Write to disk**:
> - `{package}/ai-agent-scenarios.md`
>
> **PM interaction**: NO — generate autonomously.
>
> **Hard rule**: No HTTP methods/paths, no JSON schemas, no resource-model tables, no state machines. Scenarios in prose. Capability requirements as bullets.
>
> **When done**: Report back confirmation that the artifact was created and list the top use cases from the Use Case Inventory.

### Gate 3: Knowledge Base Quality Check

After BOTH sub-agents complete:

1. **Living FAQ check**: Read `{package}/living-faq.md`
   - Verify it stays under the hard caps (≤20 questions, ≤50 words per answer, ≤2,000 total words)
   - If the "Open Questions for PM" section has items, present them to the PM and collect answers
   - Update the FAQ with the PM's answers

2. **AI Agent Scenarios check**: Read `{package}/ai-agent-scenarios.md`
   - Verify it has a Use Case Inventory section
   - Verify it has at least 3 scenarios in prose (no HTTP verbs, no JSON blocks, no schemas)
   - Verify it has an API Requirements bullet list
   - If any of the above is missing or the doc strayed into API prescription, flag to the PM

3. **Cross-reference**: Do any open FAQ items directly challenge the scenarios or capability requirements? If so, flag for PM review.

---

## STOP — Present Results to PM

Present all artifacts to the PM for review:

1. **List all generated artifacts** with full paths:
   - `{package}/context-brief.md`
   - `{package}/press-release-external.md`
   - `{package}/press-release-internal.md`
   - `{package}/one-pager.md`
   - `{package}/living-faq.md`
   - `{package}/ai-agent-scenarios.md`

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
└── ai-agent-scenarios.md
```

## When to Use

When you have raw inputs (a problem statement, transcripts, a rough idea) and want to rapidly build out all context artifacts. Run this first, review outputs, then run `/project:build` to continue.

## This Command is Cheap to Run

Feed it different input context, run it multiple times, compare outputs, iterate. The system is designed to be re-run, not to be precious about a single pass.