# /project:ship-it

## End-to-End Product Package (Phases 1–6)

This is the "do all this and make sure it's amazing" command. Runs the entire pipeline from raw inputs to complete product package.

## Arguments

- `--topic "feature X"` — Start from a topic or problem statement
- `--from-transcript ./path/to/transcript.md` — Start from a meeting transcript

## Step 0: Establish the Product Package Folder

Create the package folder where ALL artifacts will live:

```
datasets/product/packages/{YYYY}/{slug}/
```

Derive the slug from `--topic` if provided, or ask the PM for the initiative name. Announce the folder path before starting.

## Sequence

This command runs `/project:prep` then `/project:build` in sequence, with minimal pauses. The PM can review at the end rather than at intermediate checkpoints.

### Phase 1–3: Discovery Through Context

1. **Execute the full `/project:prep` sequence** (using the established package folder):
   - Phase 1: Discovery & Context Intake → `{package}/context-brief.md`
   - Phase 2: Vision Articulation → `{package}/press-release-external.md`, `{package}/press-release-internal.md`, `{package}/one-pager.md`
   - Phase 3: Knowledge Base & Edge Cases → `{package}/living-faq.md`, `{package}/agentic-api-design.md`, `{package}/api-agent-scenarios.md`

2. **Brief status checkpoint** — Summarize what was produced. Do NOT stop for a full review — continue to Phase 4.

### Phase 4–6: PRD Through Delivery

3. **Execute the full `/project:build` sequence** (using the same package folder):
   - Phase 4: PRD Generation + Ambition Expansion → `{package}/PRD_{slug}.md` + `{package}/expansion-proposals.md`
   - Phase 5: Red Team Review → `{package}/red-team-report.md` → Fix critical findings
   - Phase 6: Business Case → `{package}/business-case-swag.md`

### Complete Package Delivery

4. **Present the complete product package:**
   - Show the package folder path: `datasets/product/packages/{YYYY}/{slug}/`
   - List every artifact produced with one-line summaries
   - Highlight the 3 most important decisions/findings
   - Call out any remaining UNANSWERED questions in the Living FAQ
   - Note critical findings that were addressed and how
   - Summarize the business case executive summary

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
- Generating multiple complete packages from different starting points for comparison
- When you've been through the process once and trust the intermediate outputs

## Philosophy

This pipeline is cheap to run. Feed it different input context, run it multiple times, compare outputs, iterate. Don't be precious about a single pass.

## PM Review Points

While `/ship-it` minimizes pauses, the PM MUST still make judgment calls at:
- **Expansion proposals**: Accept or reject each one (auto-pauses here)
- **Critical red team findings**: Confirm fixes are adequate

These pauses are non-negotiable even in end-to-end mode. The PM decides, agents propose.
