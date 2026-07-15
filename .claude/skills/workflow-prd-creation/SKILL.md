---
name: workflow-prd-creation
description: Use when creating standalone PRD from user input or upstream artifacts - gathers requirements through interactive session, ingests Shipping Greatness artifacts (context brief, press releases, FAQ, AI agent scenarios), validates with prd-validation, and writes PRD file using template
---

# PRD Creation

## Purpose

Create individual Product Requirements Document through interactive session:
- Ingest and cross-reference upstream Shipping Greatness artifacts when available
- Structured requirements gathering across 9 phases
- Apply PRD validation rubric
- Generate PRD file from template
- No fabrication - leave unknown sections as TBD

## When to Use

Activate when:
- User invokes `/project:create-prd`
- `/project:build` or `/project:ship-it` invokes this skill as part of the pipeline
- Manual PRD creation needed
- Capturing product requirements from conversation

## Guiding Principles

1. **PRD is a living document** — It will evolve through collaboration and discovery
2. **Ambitious by default** — Set the ceiling as high as possible. Build the fully-featured version. Code is cheap — ambiguity and timidity are expensive
3. **Ambitious scope, incremental delivery** — Ambition governs *what* we build; slicing governs *when* a customer gets value. Set the scope ceiling high, but deliver in vertical slices that put working software in a customer's hands early. Ship small, validate, iterate. Avoid big-bang/waterfall delivery.
4. **Sequence as shippable slices, don't cut** — Instead of asking "what's the minimum?" ask "what's the best possible version, and what's the thinnest end-to-end slice a real customer could use first?" Everything ships, sequenced so each slice delivers standalone customer value — not so a horizontal layer is completed before anyone can use anything.
5. **Value to the management company is explicit** — The management company is our buyer. Every PRD states what they gain, even when the primary user is a resident or board member.
6. **Share and link** — PRDs should be accessible with links to Slack channels
7. **No fabrication** — Leave sections blank/TBD rather than making up information
8. **Reflect what was delivered** — At close, PRD should document actual outcomes

## Product Package Folder

All Shipping Greatness artifacts for a given initiative live in a single package folder:

```
datasets/product/packages/{YYYY}/{slug}/
```

The slug is derived from the product/feature name (lowercase, hyphens, no special chars). If this skill is invoked as part of `/project:build` or `/project:ship-it`, the package folder already exists from earlier phases. If invoked standalone, create the folder if it doesn't exist.

### Preflight — check for an existing initiative (do this BEFORE creating anything)

Creating a duplicate package folder for an initiative that already exists is a known failure mode (it splits a PRD across two folders and the older one gets orphaned). Before creating a new folder or PRD:

1. **Glob existing packages**: list `datasets/product/packages/{YYYY}/*/` and read the slugs (also skim adjacent years if the work could be a continuation).
2. **Semantic match, not just slug match**: the same initiative is often named differently ("FTUE redesign" vs "new-resident onboarding"). If the slug isn't an obvious match, run `context-search` over `product_artifacts` for the topic to catch a differently-named existing package or PRD.
3. **If a plausible match exists, STOP and ask the PM**: *"This looks like it overlaps with `{existing-slug}` — update that package, or create a new one?"* **Default to updating the existing package.** If the PM wants it separate, cross-link the two PRDs and note the relationship in both.
4. Only scaffold a **new** package folder when the PM confirms it's genuinely new, or no match exists.

### Output location (single source of truth)

The PRD is written to **one** location — inside the package folder:

```
{package}/PRD_{slug}.md
```

This is the canonical PRD. Backlog/roadmap tooling discovers PRDs by globbing `datasets/product/packages/{YYYY}/*/PRD_*.md`. (Historically the PRD was also mirror-copied to `datasets/product/prds/{YYYY}/` — that flat mirror has been **retired** to avoid the dual-copy drift that let duplicates hide. Do not write to `prds/{YYYY}/`.)

## Upstream Artifact Ingestion

Before starting the interactive session, check the package folder for these artifacts and ingest them if they exist. Pre-populate PRD sections from them — don't re-ask the PM for information already captured upstream:

| Artifact | Path | What to Extract |
|----------|------|----------------|
| Context Brief | `{package}/context-brief.md` | Customer problems, evidence, behavioral baselines, open questions |
| External Press Release | `{package}/press-release-external.md` | Product vision, customer outcome, key benefits, emotional hook, **value to the management company** |
| Internal Press Release | `{package}/press-release-internal.md` | Stakeholder impact, implementation considerations, support implications, **value to the management company** |
| One-Pager | `{package}/one-pager.md` | Tagline, target audience, differentiators, success metrics, timeline, **value to the management company** |
| Living FAQ | `{package}/living-faq.md` | Import all items in the "Open Questions for PM" section that are still UNANSWERED into the PRD Open Questions. Use answered items to inform requirements and customer-facing positioning. |
| AI Agent Scenarios | `{package}/ai-agent-scenarios.md` | Use Case Inventory, scenarios, and API Requirements → populate Agent/API Scenarios section. Do NOT prescribe endpoint shape in the PRD — engineering owns that. |

If upstream artifacts exist, announce what was imported and which sections were pre-populated. Only ask the PM to confirm or refine pre-populated content, not re-enter it.

## Workflow

### Phase 1: Core Identity

**Ask user:**
- **Project Name**: What is this PRD called?
- **One-liner Description**: 1-3 sentence summary for quick context
- **Background**: Why does this project exist? What problem does it solve?

### Phase 2: Objectives

**Ask user:**
- **Target Customer/User**: Who is this for? (Customer/Partner/Developer/etc.)
- **Customer Statement**:
  - I am: (narrow description of customer with motivations/attributes)
  - I'm trying to: (desired outcome)
  - But: (problem/barrier)
  - Because: (root cause)
  - Which makes me feel: (emotion)
- **Value to the Management Company**: What does the management company (our buyer) gain? Operational efficiency, staff time saved, retention/expansion, the client/board/homeowner satisfaction they are accountable for, or a competitive edge. Make it explicit even when the primary user is a resident or board member. (Pre-populate from the press releases / one-pager if available.)
- **Success Metrics**: How will we measure success? (User Experience, Technical Capabilities)
- **Opportunity Sizing**: What's the potential impact?

*Source from meeting signals if available. Leave blank if not known.*

### Phase 3: Scope & Non-Goals

**Ask user:**
- **Use Cases In Scope**: What specific use cases will be supported? Include descriptions.
- **Agent/API Scenarios**: For each human use case, what is the equivalent agent scenario? Reference the use cases and scenarios in `ai-agent-scenarios.md`. (Pre-populate from `ai-agent-scenarios.md` if available. The PRD references the scenarios; it does NOT duplicate endpoint-level API design.)
- **Out of Scope**: What are we explicitly NOT doing? Include reasons.
- **Non-Goals**: What does this product explicitly NOT aim to do? (Distinct from out-of-scope — non-goals define philosophical boundaries, not just "not in this release.")

*Be specific. Think through edge cases.*

### Phase 4: Requirements

**For each milestone, ask:**
- **Milestone Name/Summary**: What does this milestone deliver?
- **Requirements** with:
  - Priority: P0 = Foundation phase (build first), P1 = Expansion phase (build second), P2 = Polish phase (build third). All phases ship — priority determines sequence, not whether something gets built.
  - Dependent Teams
  - User Story: "In order to accomplish X, we will build Y"
  - Acceptance Criteria: How we know requirements are met
  - Figma links (if available)
  - JIRA tickets (if available)

*Only include requirements that are known. Don't fabricate.*

### Phase 4b: Build Sequence

**First, define the Shipping Strategy (vertical slices) — this is the delivery lens:**
- **Identify the thinnest end-to-end slice** a real customer or early adopter could actually use and benefit from. It must cut through the whole stack (not be a horizontal layer) and deliver standalone customer value on its own.
- **Name the first-delivery audience for each slice** — who gets it and when: dogfood → design partner → early adopter → GA. (Framed by audience, not calendar dates — engineering owns the schedule.)
- **State what each slice validates before widening** — the learning that unlocks the next slice. Ship small, validate, iterate.
- Sequence slices so a customer gets value early and often, rather than waiting for a big-bang release.

**Then organize all requirements into build phases — this is the build-order lens:**
- **Foundation (P0)**: Core capabilities that everything else depends on
- **Expansion (P1)**: Features that extend and enrich the foundation
- **Polish (P2)**: Delight features, optimizations, and refinements

Each slice cuts across these phases. All phases ship — this is sequencing, not cutting. Include dependency tracking between phases, and map each slice's requirements back to the phases.

### Phase 5: Timeline

**Ask user:**
- **Milestones**: List of major milestones (e.g., Architecture, Design, Development, Testing, Launch)
- **Expected Delivery Timeline**: Target dates/quarters for each milestone
- **Teams Leading Each Phase**: Who owns each milestone?

*If timeline is not yet determined, leave as TBD.*

### Phase 6: Links and Resources

**Ask user:**
- **Slack Channels**: Related Slack channels for discussion
- **Figma/Design Links**: Experience design and content
- **Architecture/Technical Design Docs**: Lucidcharts, Miro, etc.
- **JIRA Project/Tracking Links**: Project plan / tracking
- **Any Other Relevant Links**

*Only include links that exist. Don't create placeholder URLs.*

### Phase 7: Metrics and Learning Agenda

**Ask user:**
- **Goals and Hypotheses**: What do you want to happen?
- **Signals**: What would indicate success or validation?
- **Metrics**: What to measure to see these signals?

### Phase 8: Open Questions / Tracked Assumptions

**Populate from Living FAQ:**
- Import every item from the "Open Questions for PM" section of `living-faq.md` that is still UNANSWERED
- Add any new questions surfaced during PRD creation
- Track assumptions the PRD is built on — what happens if they're wrong?

### Phase 9: Appendix / Upstream Artifact Links

**Link to all upstream artifacts** for traceability:
- Context Brief, Press Releases, One-Pager, Living FAQ, AI Agent Scenarios
- Any expansion proposals or red team reports (if they exist from a previous `/build` run)

*Only link artifacts that actually exist. Don't create placeholder links.*

### Fact-Checking Requirements

**CRITICAL**: Do not fabricate information. For any section where information is not provided:
- Leave the section blank or marked "TBD"
- Note in changelog that section needs input
- Prompt user: "Do you have this information available?"

### Validate PRD

**Invoke:** `prd-validation` skill

- Apply 5-point rubric
- Drafting PRDs may have warnings but not blockers
- Actionable PRDs must pass all criteria

### Write PRD File

**Use template:** `datasets/product/templates/prd-template.md`

**Output (single canonical location):**
- `datasets/product/packages/{YYYY}/{slug}/PRD_{slug}.md` — in the package folder with all other artifacts

This is the only copy. Do not also write to `prds/{YYYY}/` — that mirror is retired (see "Output location" above). Roadmap/backlog discovery globs `packages/{YYYY}/*/PRD_*.md`.

**Set initial status:** 🚧 Drafting

**Add changelog entry:**
```markdown
| {YYYY-MM-DD} | Initial draft created | {user} |
```

### Optionally Update Backlog

**Ask user:**
"Add to backlog.md? (yes/no)"

If yes: Prepend to `datasets/product/backlog.md`

## PRD Statuses

| Status | When to Use |
|--------|-------------|
| 🚧 Drafting | Initial creation, known to be incomplete |
| 🏃 Actionable | Eng has agreed there's enough to start work |
| 🔒 Closed | Represents what was finally delivered |
| ❗ Abandoned | Project cancelled or superseded |

## Success Criteria

- PRD created with all provided information
- Unknown sections marked as TBD (not fabricated)
- PRD file written to correct location
- Template structure followed
- Changelog entry added
- Optionally added to backlog

## Related Skills

- `prd-validation`: Validates PRD quality
- `product-planning`: Batch PRD creation from meetings
- `meeting-synthesis`: Gathers evidence from meeting transcripts
- `vision-clarifier`: Produces press releases and one-pager (upstream)
- `devils-advocate`: Produces Living FAQ (upstream)
- `agentic-api-designer`: Produces AI Agent Scenarios (upstream)
- `ambition-expander`: Reviews PRD and proposes scope expansion (downstream)
- `red-team-reviewer`: Adversarial PRD validation (downstream)




