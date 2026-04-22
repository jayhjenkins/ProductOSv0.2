# /project:status

## Product Workflow Status Check

Show the current state of the Shipping Greatness workflow for the active product initiative.

## Step 1: Locate the Package Folder

All Shipping Greatness artifacts live in package folders:

```
datasets/product/packages/{YYYY}/{slug}/
```

- List all existing package folders under `datasets/product/packages/`
- If multiple packages exist, show status for each (or ask PM which one)
- If no packages exist, report that no Shipping Greatness workflows have been started

## Step 2: Check for Artifacts

For each package folder, check for these files:

| Phase | Artifact | File |
|-------|----------|------|
| 1 | Context Brief | `{package}/context-brief.md` |
| 2 | External Press Release | `{package}/press-release-external.md` |
| 2 | Internal Press Release | `{package}/press-release-internal.md` |
| 2 | One-Pager | `{package}/one-pager.md` |
| 3 | Living FAQ | `{package}/living-faq.md` |
| 3 | AI Agent Scenarios | `{package}/ai-agent-scenarios.md` |
| 4 | PRD | `{package}/PRD_{slug}.md` |
| 4 | Expansion Proposals | `{package}/expansion-proposals.md` |
| 5 | Red Team Report | `{package}/red-team-report.md` |
| 6 | Business Case SWAG | `{package}/business-case-swag.md` |

## Step 3: Report Status

For each artifact:
- ✅ Exists and appears complete
- ⚠️ Exists but has gaps (TBD sections, UNANSWERED questions)
- ❌ Does not exist yet

## Step 4: Check Blockers

- **Living FAQ**: Count UNANSWERED items in the "Open Questions for PM" section
- **Red Team Report**: Count unresolved critical findings

## Step 5: Suggest Next Action

- If Phases 1-3 incomplete → "Run `/project:prep` to complete upstream artifacts"
- If Phases 1-3 complete, 4-6 incomplete → "Run `/project:build` to generate PRD and validate"
- If all phases complete → "Product package complete. Review and iterate as needed."
- If specific gaps exist → Suggest the specific command to fill them

## Output Format

```
## Workflow Status: {Product Name}

**Package folder**: `datasets/product/packages/{YYYY}/{slug}/`

### Phase Completion
- Phase 1 (Discovery): {✅/⚠️/❌}
- Phase 2 (Vision): {✅/⚠️/❌}
- Phase 3 (Knowledge Base): {✅/⚠️/❌}
- Phase 4 (PRD): {✅/⚠️/❌}
- Phase 5 (Red Team): {✅/⚠️/❌}
- Phase 6 (Business Case): {✅/⚠️/❌}

### Blockers
- {count} UNANSWERED items in Living FAQ "Open Questions for PM"
- {count} unresolved critical findings in Red Team Report

### Suggested Next Action
{recommendation}
```
