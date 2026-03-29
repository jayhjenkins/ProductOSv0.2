# /project:prep

## Discovery Through Context (Phases 1–3)

This is an orchestration command that runs the full upstream context-gathering pipeline and stops at the natural checkpoint before PRD generation.

## Arguments

- `--skip-discover` — Skip Phase 1 discovery, use existing Context Brief
- `--topic "feature X"` — Pass in the starting topic or problem statement

## Step 0: Establish the Product Package Folder

Before any phase runs, establish the package folder where ALL artifacts for this initiative will live:

```
datasets/product/packages/{YYYY}/{slug}/
```

**How to determine the slug:**
- If `--topic` is provided, derive the slug from it (lowercase, hyphens, no special chars)
- If resuming an existing package, use the existing folder
- If neither, ask the PM for the initiative name

**Create the folder** if it doesn't exist. All subsequent skills read from and write to this folder.

**Announce**: "Product package folder: `datasets/product/packages/{YYYY}/{slug}/`"

## Sequence

Execute these phases in order. At each gate, verify the artifact exists and meets quality criteria before proceeding.

### Phase 1: Discovery & Context Intake

1. **Run `/project:create-notes`** or use existing Context Gathering skills to produce the Context Brief
2. If `--topic` was provided, use it as the starting problem statement
3. If `--skip-discover` was provided, verify an existing Context Brief exists in the package folder and skip to Phase 2

**Gate**: Context Brief must contain at least one clearly stated customer problem backed by data. If not, STOP and ask the PM for more input.

**Output**: `{package}/context-brief.md`

### Phase 2: Vision Articulation

4. **Run the vision-clarifier skill** (equivalent to `/project:press-release --both`)
5. Use the Context Brief as primary input
6. Walk the PM through the interrogation loop — do not skip questions
7. Generate both press releases and the one-pager

**Gate**: Both press releases must exist. The one-pager must be producible from the PR content. If the vision can't be condensed to a 10-minute pitch, loop back with the PM for clarification.

**Output**: `{package}/press-release-external.md`, `{package}/press-release-internal.md`, `{package}/one-pager.md`

### Phase 3: Knowledge Base & Edge Case Mapping

These two agents can run in parallel:

8. **Run the devils-advocate skill** (equivalent to `/project:devils-advocate --full`)
   - Generate the Living FAQ from all perspectives
   - Classify all questions by priority

9. **Run the agentic-api-designer skill** (equivalent to `/project:api-design --generate`)
   - Produce the full API design and agent workflow scenarios

**Gate**: Living FAQ must exist with all `blocking` questions answered. API Design must have at least resource model and capability inventory complete. If blocking questions remain UNANSWERED, present them to the PM and wait for answers before completing.

**Output**: `{package}/living-faq.md`, `{package}/agentic-api-design.md`, `{package}/api-agent-scenarios.md`

### STOP

10. **Present all artifacts to the PM for review.**
    - List all generated artifacts with full paths
    - Highlight any open questions or incomplete sections
    - Remind PM of the package folder location
    - Suggest running `/project:build` when the PM is satisfied with upstream artifacts

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
