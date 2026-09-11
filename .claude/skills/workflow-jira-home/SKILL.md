---
name: workflow-jira-home
description: Create Jira issues (Features/Epics, Units/Stories, Bugs, Regression Defects, etc.) on your team's Jira board via the Jira MCP. Self-configures on first use — discovers your instance's project/board/field IDs and writes them to profile/integrations.yaml so you never re-enter them. Use when the user wants to log a bug, file a feature request, draft a small work item, or create a PRD-linked top-level issue.
triggers:
  - jira
  - create ticket
  - log bug
  - file bug
  - create feature
  - create unit
  - feature request
  - jira board
---

# Jira Issue Creation

Create issues on your team's Jira board using the Jira MCP. This skill is a template: the first
time it runs against a fresh profile, it discovers your Jira instance's real IDs (cloud ID,
project, board, issue types, custom fields) and writes them into `profile/integrations.yaml`.
Every run after that just reads the profile — no rediscovery, no re-asking.

## First-Run Setup (Auto-Discovery)

Before doing anything else, read `profile/integrations.yaml` → `project_management.jira` (via
`python3 scripts/profile_lib.py` or by reading the file directly). If `cloud_id` and
`project_key` are both already populated, **skip this whole section** and go straight to
[Phase 1](#phase-1-determine-what-to-create) — setup is already done.

If either is empty, this is a first run. Walk the user through setup, then persist the results:

1. **Resolve the Jira Cloud ID.** Call `getAccessibleAtlassianResources`. If there's one
   accessible site, confirm it with the user ("Found `{cloud_id}` — use this Jira site?"). If
   there are several, ask which one.
2. **Resolve the project.** Call `getVisibleJiraProjects`. Ask the user which project this skill
   should default to (most users have one obvious answer — their team's project). Record its key
   and numeric id.
3. **Resolve the board** (optional but recommended). If the user knows their team's board name/id,
   record it and a short `product_area` label (free text — whatever the team calls this
   product/board slice). If they don't use a dedicated board, leave `board_id` empty.
4. **Map issue-type roles.** Call `getJiraProjectIssueTypesMetadata` for the resolved project.
   Every Jira project has `Epic` and `Story` by default — map those first. Then ask: "Does your
   team use a larger PRD-scale issue type above Epic (a custom 'Feature' type), or is Epic your
   top-level type?" and "Is there a small-work-item type below Story (like a custom 'Unit' or
   'Task'), or is Story your default?" Map `top_level` and `work_item` to whatever the user
   confirms — these may just be Epic and Story themselves. Do the same, optionally, for
   `regression` / `spike` / `hotfix` if the user's project has custom types for those; otherwise
   leave them empty and this skill will just use `Bug` / skip that phase.
5. **Discover custom fields.** For the `top_level` (and `epic`, if different) issue type, call
   `getJiraIssueTypeMetaWithFields`. Look for fields that plausibly match: a short-name field
   (`top_level_name`), a target/release date (`target_date`), an early-access-style date
   (`early_access_date`), a URL field for a linked spec/PRD (`spec_reference`), a select field for
   event/commitment tagging (`commitment` — if it's a select/multiselect, also capture its
   `allowedValues` into `commitment_values`), and a release-notes select (`release_notes`). Not
   every instance has all of these — leave a field empty if there's no match rather than guessing.
6. **Resolve the default assignee** (optional). Ask if top-level issues (Features/Epics) should
   default to a specific assignee. If yes, use `lookupJiraAccountId` or `atlassianUserInfo` to get
   their accountId. If the user has no preference, leave it empty — nothing will default.
7. **Resolve the component** (optional). If the team uses a Jira Component to scope issues to
   their board, ask for its name and look up its id.
8. **Resolve a swim-lane label** (optional). Some boards use a label to route issues into an
   automated/agent-driven lane vs. a manual "everything else" lane (see the Swim Lane Rule below).
   Ask if this applies; if so, record the label text as `auto_label`.
9. **Confirm and write.** Show the user everything discovered as a summary table, let them correct
   anything, then write it into `profile/integrations.yaml` → `project_management.jira`
   (`provider: "jira"` plus the fields above), preserving the file's existing comments/siblings.
   From this point on, every invocation of this skill reads these values instead of asking again.

## When to Use

- User wants to log a bug (client-reported or internal regression)
- User wants to draft a small work item (enhancement, improvement, or single engineering change)
- User wants to create a top-level, PRD-linked capability (Feature/Epic-role issue)
- User wants to file a Spike, Hotfix, or other defect type (if configured)
- User says "create a Jira ticket", "log this bug", "file a feature request", "draft a unit",
  "create a feature"
- User wants a legacy Epic or Story explicitly

## Draft Mode (Headless/Agent Context)

When invoked by the **ticket-creator worker** (headless agent dispatch), you operate in **draft mode**:
- You do NOT have access to Jira MCP tools
- You draft the issue content in the task body using the `<!-- JIRA_DRAFT -->` format
- The human reviews the draft on the task board and clicks "Publish to Jira"
- Use this skill as a REFERENCE for field names, issue types, and configuration — not for direct publishing
- Draft mode assumes First-Run Setup has already completed interactively at least once (headless
  dispatch can't run the discovery calls itself); `jira_publish.py` will error clearly if the
  profile isn't configured yet.

When invoked **interactively** via `/jira:create` (human is in the CLI session), use the normal flow and call Jira MCP directly — the human is already in the loop, and this is also where First-Run Setup runs if needed.

### JIRA_DRAFT Format

```markdown
<!-- JIRA_DRAFT -->
<!-- JIRA_TYPE:Unit -->
<!-- JIRA_SUMMARY:Short summary here -->
<!-- JIRA_PRIORITY:High -->
<!-- JIRA_LABELS: -->
<!-- JIRA_RELEASE_NOTES:Internal Only -->
<!-- JIRA_PARENT:ABC-12345 -->
<!-- JIRA_FEATURE_NAME: -->
<!-- JIRA_GTM_DATE: -->
<!-- JIRA_EA_DATE: -->
<!-- JIRA_SPEC_REFERENCE: -->
<!-- JIRA_CLIENT_COMMITMENT: -->
<!-- JIRA_ASSIGNEE: -->

### Summary
Short summary here

### Description
Full description with context...

### Fields
- **Type:** Unit
- **Priority:** High
- **Labels:** (none by default — see the Swim Lane Rule for when to set the configured swim-lane label)
- **Release Notes:** Internal Only
- **Parent:** ABC-12345
<!-- /JIRA_DRAFT -->
```

**Field rules:**
- `JIRA_TYPE`: whatever your profile's `issue_types` roles resolve to (e.g. `Bug`, `Regression Defect`, `Story`, `Unit`, `Epic`, `Feature`, `Spike`, `Hotfix`) — normalize common shorthand/casing before use.
- `JIRA_PRIORITY`: `Highest`, `High`, `Medium`, `Low`, `Lowest` (or empty for default)
- `JIRA_LABELS`: usually empty. The only label this skill ever applies is the profile's configured `auto_label` (if any), and only per the Swim Lane Rule. Never invent topical labels (`calendar`, `compliance`, `resident-portal`, etc.) from the ticket subject — those create permanent noise in a taxonomy you don't own. Add a non-default label only when the user explicitly types it in their prompt.
- `JIRA_RELEASE_NOTES`: `None`, `Internal Only`, or `External` (or empty) — only if your profile has a `release_notes` custom field configured
- `JIRA_PARENT`: parent issue key (e.g., `ABC-12345`) — typically for a work-item type linking to a top-level type. Optional; leave empty to create unparented.
- `JIRA_FEATURE_NAME`: short label for the top-level issue (also accepted as legacy `JIRA_EPIC_NAME`) — only if your profile has a `top_level_name` custom field configured
- `JIRA_GTM_DATE`: `YYYY-MM-DD`, or empty / `TBD` to leave blank — only if `target_date` is configured
- `JIRA_EA_DATE`: `YYYY-MM-DD`, or empty / `TBD` to leave blank — only if `early_access_date` is configured
- `JIRA_SPEC_REFERENCE`: absolute URL to the spec/PRD — only if `spec_reference` is configured. The URL goes in the Jira field, not in the description body — keep the description lean.
- `JIRA_CLIENT_COMMITMENT`: one of the profile's `commitment_values` (or empty) — only if `commitment` is configured
- `JIRA_ASSIGNEE`: Jira account ID string. **For top-level types, defaults to the profile's `default_assignee` unless the user specifies someone else.** Leave empty for other types unless the user explicitly sets it.

**Description hygiene (applies to both draft mode and direct-publish mode):**

The `### Description` body (or `description:` arg in direct MCP calls) becomes the Jira issue body — visible to engineering, QA, and stakeholders. Never include PM-OS-internal references:

- No PM-OS task IDs (`TASK-NNNN`) or phrases like "sibling task", "prior PM-OS task", "spun out of TASK-…"
- No local paths (`datasets/`, `scripts/`, `.claude/`, etc.)
- Reference meetings by **date + participants + customer**, not by local transcript filename

Cross-link via Jira-native references instead (issue keys, Confluence URLs, customer names, dates, verbatim quotes).

## Jira Configuration

**Never hardcode instance IDs in this file.** Every value below is resolved from
`profile/integrations.yaml` → `project_management.jira` (populated by First-Run Setup above, or
filled in by hand). If a value is empty and required, stop and run First-Run Setup rather than
guessing.

| Setting | Profile key |
|---------|-------------|
| Cloud ID | `cloud_id` |
| Project Key | `project_key` |
| Project ID | `project_id` |
| Default Board | `board_id` (label: `product_area`) |
| Default Component | `component_id` / `component_name` |
| Swim-lane label | `auto_label` — optional; see Swim Lane Rule below |

### Issue Types

Roles map to your instance's real issue types via `project_management.jira.issue_types` (see
First-Run Setup). Not every role needs a value — leave a role's `id` empty if your instance has
no equivalent type, and skip the corresponding phase.

| Role | Typical use case | Notes |
|------|----------|------|
| `top_level` | **Larger net-new product capability (PRD-scale).** Product-owned, contains work items as children. | Often a custom type (e.g. "Feature"); falls back to `epic` role if unconfigured. |
| `work_item` | **Small enhancement, improvement, or single engineering change.** Independently buildable, testable, deployable. Default for most engineering work. | Often a custom type (e.g. "Unit"); falls back to `story` role if unconfigured. |
| `bug` | Client-reported problem or error. | Default for `--bug`. Falls back to Jira's standard `Bug` type. |
| `regression` | Internally-found regression (QA, internal testing). | Optional — use `bug` role if unconfigured. |
| `spike` | Time-boxed investigation. | Optional. |
| `hotfix` | Emergency fix. | Optional. |
| `epic` | Standard Jira Epic. | Almost always available; used as `top_level` fallback. |
| `story` | Standard Jira Story. | Almost always available; used as `work_item` fallback. |

### Custom Field Reference

Logical fields map to your instance's real fieldIds via `project_management.jira.custom_fields`
(see First-Run Setup). Leave a field empty if your instance has no equivalent — this skill will
simply skip populating it rather than guess a fieldId.

| Field | Custom-fields key | Type | Notes |
|-------|---------|------|-------|
| Top-level Name | `top_level_name` | string | Short label for `top_level`/`epic`-role issues. Populated from `JIRA_FEATURE_NAME` or legacy `JIRA_EPIC_NAME`. |
| Target Date | `target_date` | date | `YYYY-MM-DD` (top-level types only) |
| Early Access Date | `early_access_date` | date | `YYYY-MM-DD` (top-level types only, if your team tracks this) |
| Spec Reference | `spec_reference` | URL string | Canonical home for the PRD's shareable URL (top-level types only) |
| Commitment | `commitment` | labels array | Values from `commitment_values` (top-level types only, if configured) |
| Release Notes | `release_notes` | select | `None` / `Internal Only` / `External`, or whatever your instance's options are |
| Priority | (standard `priority` field) | priority | Standard Jira priorities |
| Labels | (standard `labels` field) | array of string | Swim-lane assignment — see Swim Lane Rule. No auto-prepend; the draft's labels are submitted as-is. |
| Parent | (standard `parent` field) | issue link | Top-level field on the work-item type — value is `{"key": "ABC-XXXXX"}` |
| Assignee | (standard `assignee` field) | account object | `{"accountId": "..."}`. **Top-level types default to the profile's `default_assignee` unless overridden.** Other types: leave unset unless user specifies. |

### Swim Lane Rule

If your board uses a label to route work into an automated/agent-driven lane vs. a manual
"everything else" column, that label lives in the profile as `auto_label`. If `auto_label` is
unconfigured, skip labeling entirely — never invent one.

When configured, the label typically plays two roles:

**For top-level types (Feature/Epic-role)** — it's an *initiative tag*, applied by default,
identifying issues that belong to whatever standing initiative this board serves.

**For work-item/bug-tier types** — it's a *swim-lane assignment*:
- **With the label** → the automated/agent-driven lane.
- **Without any labels** → the manual "everything else" column.

Default by role, when `auto_label` is configured:

| Role | Default labels |
|---|---|
| `top_level`, `epic` | `[auto_label]` |
| `bug`, `regression`, `hotfix`, `spike` | `[]` (empty) |
| `work_item`, `story` | `[]` by default. If parented to a top-level issue that carries `auto_label`, mirror the parent. |

**No-Invent Rule.** Do not synthesize labels from the ticket's topic, product area, customer name, or bug class. The Labels field is routing metadata controlled by the engineering team, not a tagging surface for AI-generated context — context belongs in the description. Only add a non-default label when the user explicitly dictates it in their prompt (e.g., "tag this `mobile-only`"). When in doubt, omit. The user can always add labels in the Jira UI after the fact; AI-generated labels are hard to remove once they spread.

**Publish behavior.** `jira_publish.py` submits the draft's labels as-is. No auto-prepend. If the draft has no `JIRA_LABELS`, the issue is created with no labels.

### Workflow Notes

- New issues default to whatever status your project's workflow assigns on creation — let Jira pick the initial transition.
- Ask the user (once, during First-Run Setup, or note it as a convention) which fields must be filled to leave the initial status — commonly Release Notes, a defect-area field, or Components.
- If a Component is configured, it makes the issue eligible for the team's board filters.
- A work-item type should be parented to a top-level type (preferred) or Epic (legacy). Jira may reject invalid parent/child type combinations — surface the error and let the user pick a valid parent.

---

## Phase 1: Determine What to Create

### If arguments are provided:
- `--feature "name"` → Phase 3 (top-level type)
- `--unit "summary"` → Phase 4 (work-item type)
- `--bug "summary"` → Phase 2 (Bug), default type=`Bug`
- `--regression "summary"` → Phase 2 (Bug flow), type=`Regression Defect` (if configured, else `Bug`)
- `--epic "name"` → Phase 5 (Legacy Epic)
- `--story "summary"` → Phase 5 (Legacy Story)

### If no arguments (interactive):
Ask the user:

> **Which type fits?**
>
> - **Is something broken or wrong?** → **Bug** (client-reported) or **Regression Defect** (caught internally by QA, if your instance has this type).
> - **Adding or changing something small** — a tweak, an improvement, a single capability change? → the work-item type. This is the default for most engineering work and is what you usually want.
> - **Net-new product capability** driven by a PRD or larger scope? → the top-level type. Only use this when the work is roadmap-tier.
> - **Need to investigate before scoping?** → Spike (if configured).
> - **Emergency fix?** → Hotfix (if configured).
> - Legacy hierarchy needed (Epic / Story)? → mention it explicitly.
>
> What would you like to create?

---

## Phase 2: Create a Bug or Regression Defect

### Step 2.1: Gather Required Info

Ask for (skip any already provided via arguments):

1. **Summary** (required): One-line title
2. **Description** (recommended): What's the issue? Provide context, steps to reproduce, expected vs actual behavior.
3. **Source** (only if type unknown): Was this reported by a client (→ `Bug`) or found internally by QA / product team (→ `Regression Defect`, if configured)?

### Step 2.2: Gather Optional Info

Ask if the user wants to set any of these now (they can always be added later in Jira):

- **Priority**: Highest / High / Medium / Low / Lowest
- **Release Notes**: None / Internal Only / External (only if `release_notes` is configured)
- **Labels**: usually skip. Bugs default to no labels. Only ask if the user has already mentioned a specific label in their prompt. Do NOT volunteer topical tags. See the Swim Lane Rule above.

Do NOT ask about any high-cardinality classification field (250+ options) — better set in the Jira UI.

### Step 2.3: Create the Issue

```
mcp__claude_ai_Jira__createJiraIssue(
  cloudId: "{cloud_id from profile}",
  projectKey: "{project_key from profile}",
  issueTypeName: "Bug" | "Regression Defect",
  summary: "<user's summary>",
  description: "<user's description>",
  contentFormat: "markdown",
  additional_fields: {
    "components": [{"id": "{component_id from profile, if configured}"}],
    "labels": [],  // bugs default to no labels. Only populate if user explicitly named a label.
    // Include only if user provided values:
    "priority": {"name": "<priority>"},
    "{release_notes fieldId from profile}": {"value": "<release notes choice>"}
  }
)
```

### Step 2.4: Report Result

Display:
- Issue key (e.g., `{project_key}-1234`)
- Direct link: `https://{cloud_id}/browse/{project_key}-1234`
- Type: `Bug` or `Regression Defect`
- Status: whatever the project assigned on creation
- Reminder of any fields the team needs to fill in before this leaves its initial status (component is already set, if configured)

---

## Phase 3: Create a Top-Level Issue (Feature/Epic-role)

Use this for larger net-new product capability work — PRD-scale, product-owned, contains work items as children.

**Heads-up:** if your instance distinguishes a "Feature" type from Epic and puts it on separate roadmap boards, this issue won't show up on the team's kanban. If the work is a small enhancement or single change, use a work item instead — that's where most engineering work belongs.

### Step 3.1: Gather Required Info

Ask for (skip any already provided):

1. **Name** (required, if `top_level_name` is configured): Short label (e.g., "Mobile Push Notifications")
2. **Summary** (required): One-line summary (can match the name or be more descriptive)
3. **Description / Outcome Detail** (required): What is this about and why are we building it? Keep the body lean per the Description hygiene rules — no meeting framing, no version narrative.

### Step 3.2: Gather Top-Level-Specific Fields

Ask each in turn (skip any already provided via arguments, and skip any whose custom field isn't configured in the profile). For dates, accept `TBD` or empty as "leave the Jira field blank."

1. **Spec Reference URL** (recommended, if `spec_reference` is configured): The shareable URL of the PRD or spec document. Paste the URL, or skip to leave blank.
2. **Target Date** (optional, if `target_date` is configured): `YYYY-MM-DD`, or `TBD` / empty.
3. **Early Access Date** (optional, if `early_access_date` is configured): `YYYY-MM-DD`, or `TBD` / empty.
4. **Commitment** (optional, if `commitment` is configured): one of the profile's `commitment_values`, or none — not committed (skip field).
5. **Assignee** (optional): Defaults to the profile's `default_assignee` unless the user specifies someone else. Only ask if the user has already named a different person.

### Step 3.3: Create the Issue

```
mcp__claude_ai_Jira__createJiraIssue(
  cloudId: "{cloud_id from profile}",
  projectKey: "{project_key from profile}",
  issueTypeName: "{issue_types.top_level.name from profile}",
  summary: "<user's summary>",
  description: "<user's description with outcome detail>",
  contentFormat: "markdown",
  additional_fields: {
    "components": [{"id": "{component_id from profile, if configured}"}],
    "labels": ["{auto_label from profile, if configured}"],  // top-level types go to the initiative-tag lane, if one is configured
    "{top_level_name fieldId}": "<name>",
    // Include only if user provided values AND the field is configured:
    "{target_date fieldId}": "<YYYY-MM-DD>",
    "{early_access_date fieldId}": "<YYYY-MM-DD>",
    "{spec_reference fieldId}": "<absolute spec reference url>",
    "{commitment fieldId}": ["<commitment value>"],
    // Assignee: defaults to profile default_assignee; override only if user specified someone else
    "assignee": {"accountId": "<accountId — default: {default_assignee from profile}>"}
  }
)
```

### Step 3.4: Report Result

Display:
- Issue key + direct link
- Name: displayed (if set)
- Spec Reference: displayed (if set) — confirm it renders as a clickable URL in Jira
- Target Date / Early Access Date: displayed (if set)
- Commitment: displayed (if set)
- Status: whatever the project assigned on creation

---

## Phase 4: Create a Work-Item Issue

Use this for engineering work that is **a small enhancement, improvement, or single deployable change** — the default type for most engineering work.

### Step 4.1: Gather Required Info

Ask for (skip any already provided):

1. **Summary** (required): One-line title
2. **Description** (required): What is this doing? Include acceptance criteria when known.
3. **Parent issue key** (optional, recommended): The top-level issue this belongs under (e.g., `{project_key}-42920`). Leave blank if not yet known.

### Step 4.2: Gather Optional Info

Ask:

- **Priority**: Highest / High / Medium / Low / Lowest
- **Release Notes**: None / Internal Only / External (only if configured)
- **Labels**: usually skip. Work items default to no labels. If this item is a child of a top-level issue that carries the configured `auto_label`, mirror the parent's label. Otherwise leave empty. Do NOT volunteer topical tags. See the Swim Lane Rule above.

### Step 4.3: Create the Issue

```
mcp__claude_ai_Jira__createJiraIssue(
  cloudId: "{cloud_id from profile}",
  projectKey: "{project_key from profile}",
  issueTypeName: "{issue_types.work_item.name from profile}",
  summary: "<user's summary>",
  description: "<user's description>",
  contentFormat: "markdown",
  additional_fields: {
    "components": [{"id": "{component_id from profile, if configured}"}],
    "labels": [],  // defaults to no label; mirror parent's auto_label only if parented to one
    // Include only if parent provided:
    "parent": {"key": "<{project_key}-XXXXX>"},
    // Include only if user provided values:
    "priority": {"name": "<priority>"},
    "{release_notes fieldId}": {"value": "<release notes choice>"}
  }
)
```

### Step 4.4: Report Result

Display:
- Issue key + URL
- Parent (if set) — confirm it linked correctly
- If unparented: "Heads-up — this has no parent top-level issue yet. Wire it up in Jira when you know where it belongs."

---

## Phase 5: Legacy Epic / Story

Retained for cases where the user explicitly asks for Epic or Story. If your top-level/work-item roles are already mapped to Epic/Story (the common case for teams with no custom types), this phase is identical to Phases 3/4 — just use `issueTypeName: "Epic"` or `"Story"` directly.

The flow is identical to Phase 3 (Epic mirrors the top-level flow) and Phase 4 (Story mirrors the work-item flow). The legacy `JIRA_EPIC_NAME` field name is still accepted for Epic creation.

**Label defaults follow the Swim Lane Rule:** Epic defaults to `[auto_label]` if configured (mirrors top-level). Story defaults to `[]` (mirrors work-item).

---

## Error Handling

- **MCP unavailable**: "The Jira MCP is not connected. Make sure MCP integrations are enabled for this project."
- **Not yet configured**: If `profile/integrations.yaml` has no `cloud_id`/`project_key`, run First-Run Setup above before doing anything else.
- **Permission denied**: "You don't have permission to create issues in this project. Check your Jira access."
- **Field validation error**: Display the error from Jira and suggest corrections.
- **Component not found**: Fall back to using the component name instead of ID: `[{"name": "{component_name from profile}"}]`
- **Parent issue invalid or wrong type**: Jira rejects work items parented to an incompatible type. Show the error, suggest a valid parent (top-level type preferred), and offer to retry without the parent.
- **Unknown issue type**: Normalize common variants against the profile's `issue_types` map before failing. If still unrecognized, list the valid types from the profile.

## Related Skills

- `prd-creation` — Create PRDs that can be linked to top-level issues
- `publish-package` — Sync PRD packages to SharePoint (generates shareable URLs for spec-reference fields)
- `product-planning` — Meetings-to-backlog pipeline that may generate work-item / Bug drafts
