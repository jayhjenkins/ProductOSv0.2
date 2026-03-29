# /project:build

## PRD Through Delivery (Phases 4–6)

This is an orchestration command that takes existing upstream artifacts and runs the back half of the pipeline: PRD generation, red team validation, and business case modeling.

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
- `{package}/living-faq.md` — Living FAQ
- `{package}/agentic-api-design.md` — Agentic API Design
- `{package}/api-agent-scenarios.md` — Agent Workflow Scenarios

**If any are missing**: Warn the PM and suggest running `/project:prep` first. Do not proceed without at minimum the Context Brief and Press Releases.

## Sequence

### Phase 4: Ambitious PRD Generation

1. **Run the prd-creation skill** (equivalent to `/project:create-prd`)
   - Feed ALL upstream artifacts from the package folder as input context
   - Cross-reference Context Brief, Press Releases, Living FAQ, and API Design
   - Populate the PRD using the updated template with all new sections
   - Inherit unanswered `important` and `tracked` items from Living FAQ into the Open Questions section
   - Set status to 🚧 Drafting

**Output (dual location)**:
- `{package}/PRD_{slug}.md` — in the package folder
- `datasets/product/prds/{YYYY}/PRD_{slug}.md` — canonical PRD location

2. **Run the ambition-expander skill** (equivalent to `/project:expand --review`) — unless `--skip-expand` was provided
   - Review the PRD and generate expansion proposals
   - Produce adjacent needs, delight features, competitive leapfrog, and variant proposals

**Output**: `{package}/expansion-proposals.md`

3. **PAUSE for PM review.**
   - Present expansion proposals to the PM
   - PM accepts or rejects each proposal with rationale
   - Accepted items get folded into the PRD (update both locations)
   - Update the PM Decision Log in expansion-proposals.md
   - No requirement to cut scope — only to confirm scope is intentional

**Gate**: PM has reviewed all expansion proposals. PRD updated with accepted items.

### Phase 5: Validation & Red Team

4. **Run the red-team-reviewer skill** (equivalent to `/project:red-team --full`)
   - Full adversarial review including persona-lens
   - Walk through every scenario step by step
   - Architecture stress test, API review, consistency audit

**Output**: `{package}/red-team-report.md`

5. **Address critical findings.**
   - Present critical findings to the PM
   - Update the PRD with fixes for all critical items (both locations)
   - Track major items but do not block on them
   - Update `{package}/living-faq.md` with any new questions surfaced

**Gate**: All `critical` findings addressed. PRD updated. Major findings tracked.

### Phase 6: Business Case

6. **Run the swag-modeler skill** (equivalent to `/project:swag --generate`) — unless `--skip-swag` was provided
   - Build the financial model from PRD and context
   - Include sensitivity analysis and scenarios

**Output**: `{package}/business-case-swag.md`

### DONE

7. **Present the complete product package.**
   - Show the package folder path and list all artifacts with summaries
   - Highlight key decisions made during the process
   - Note any remaining open questions or tracked items
   - The product package is ready for engineering handoff

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

## Iteration Loops

If the red team review surfaces issues that require revisiting earlier phases:
- **Minor fixes**: Update PRD in place (both locations), re-run red team on affected sections only
- **Vision-level issues**: Go back to `/project:prep` with updated inputs (same package folder)
- **Scope questions**: Re-run `/project:expand` with PM guidance

## When to Use

After you've reviewed and are satisfied with the `/project:prep` outputs. Also useful for re-running the back half with different inputs (e.g., after significant Context Brief updates).
