---
name: workflow-jira-home
description: Create Jira issues (Features, Units, Bugs, Regression Defects, etc.) on the Vantaca Home AI DLC board (VNT, board 1096) via the Jira MCP. Use when the user wants to log a bug, file a feature request, draft a unit, or create a PRD-linked Feature for the Home product area.
triggers:
  - jira
  - create ticket
  - log bug
  - file bug
  - create feature
  - create unit
  - feature request
  - Vantaca Home AI DLC
  - VNT board
  - board 1096
  - HXP
---

# Jira Home Issue Creation

Create issues on the Vantaca Home AI DLC board (project `VNT`, board `1096`) using the Jira MCP.

## When to Use

- User wants to log a bug for Vantaca Home (client-reported or internal regression)
- User wants to draft a Unit (small enhancement, improvement, or single engineering change) for Home work
- User wants to create a Feature (PRD-linked product capability)
- User wants to file a Spike, Hotfix, or other defect type
- User says "create a Jira ticket", "log this bug", "file a feature request", "draft a unit", "create a feature"
- User wants a legacy Epic or Story (still supported, not default)

## Draft Mode (Headless/Agent Context)

When invoked by the **ticket-creator worker** (headless agent dispatch), you operate in **draft mode**:
- You do NOT have access to Jira MCP tools
- You draft the issue content in the task body using the `<!-- JIRA_DRAFT -->` format
- The human reviews the draft on the task board and clicks "Publish to Jira"
- Use this skill as a REFERENCE for field names, issue types, and configuration — not for direct publishing

When invoked **interactively** via `/jira:create` (human is in the CLI session), use the normal flow and call Jira MCP directly — the human is already in the loop.

### JIRA_DRAFT Format

```markdown
<!-- JIRA_DRAFT -->
<!-- JIRA_TYPE:Unit -->
<!-- JIRA_SUMMARY:Short summary here -->
<!-- JIRA_PRIORITY:High -->
<!-- JIRA_LABELS: -->
<!-- JIRA_RELEASE_NOTES:Internal Only -->
<!-- JIRA_PARENT:VNT-12345 -->
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
- **Labels:** (none — Units land in "everything else" by default; set to `home_aidlc` only for Features/Epics or Units that mirror an AI DLC parent)
- **Release Notes:** Internal Only
- **Parent:** VNT-12345
<!-- /JIRA_DRAFT -->
```

**Field rules:**
- `JIRA_TYPE`: `Bug`, `Regression Defect`, `Story`, `Unit`, `Epic`, `Feature`, `Spike`, or `Hotfix`
- `JIRA_PRIORITY`: `Highest`, `High`, `Medium`, `Low`, `Lowest` (or empty for default)
- `JIRA_LABELS`: usually empty. The only label PM-OS applies is `home_aidlc`, and only on Features/Epics (see Swim Lane Rule below). For Bugs, Units, Regression Defects, Spikes, Hotfixes — leave this empty. Never invent topical labels (`calendar`, `compliance`, `resident-portal`, etc.) from the ticket subject — those create permanent noise in a taxonomy you don't own. Add a non-default label only when the user explicitly types it in their prompt.
- `JIRA_RELEASE_NOTES`: `None`, `Internal Only`, or `External` (or empty)
- `JIRA_PARENT`: parent issue key (e.g., `VNT-12345`) — typically for `Unit` linking to a `Feature` or `Epic`. Optional; leave empty to create unparented.
- `JIRA_FEATURE_NAME`: short label for the Feature (Feature only — also accepted as the legacy `JIRA_EPIC_NAME` for compatibility)
- `JIRA_GTM_DATE`: `YYYY-MM-DD`, or empty / `TBD` to leave blank (Feature / Epic only)
- `JIRA_EA_DATE`: `YYYY-MM-DD`, or empty / `TBD` to leave blank (Feature / Epic only). Early-access date — typically before GTM. Sam's process accepts incomplete dates so long as the field can be filled in later in the Jira UI.
- `JIRA_SPEC_REFERENCE`: absolute URL to the spec/PRD (Feature / Epic only). For PM-OS-driven Features this is the Word/SharePoint URL of `PRD_{slug}.md`. The URL goes in the Jira field, not in the description body — keep the description lean.
- `JIRA_CLIENT_COMMITMENT`: `CAI`, `Vision`, or empty (Feature / Epic only)
- `JIRA_ASSIGNEE`: Jira account ID string (e.g., `712020:aeec48b7-3829-433b-9125-c8c2a4c84e6f`). **For Features, defaults to Jay Jenkins (`712020:aeec48b7-3829-433b-9125-c8c2a4c84e6f`) unless the user specifies someone else.** Leave empty for non-Feature types unless the user explicitly sets it.

**Description hygiene (applies to both draft mode and direct-publish mode):**

The `### Description` body (or `description:` arg in direct MCP calls) becomes the Jira issue body — visible to engineering, QA, and stakeholders. Never include PM-OS-internal references:

- No PM-OS task IDs (`TASK-NNNN`) or phrases like "sibling task", "prior PM-OS task", "spun out of TASK-…"
- No local paths (`datasets/`, `scripts/`, `.claude/`, etc.)
- Reference meetings by **date + participants + customer**, not by local transcript filename

Cross-link via Jira-native references instead (`VNT-NNNNN` keys, Confluence URLs, customer names, dates, verbatim quotes).

## Jira Configuration

All values below are hardcoded from the Vantaca Jira instance. The migration to board 1096 over the weekend of 2026-05-10 did not change project-level identifiers; only the issue type hierarchy and the board filter changed.

| Setting | Value |
|---------|-------|
| Cloud ID | `vantaca.atlassian.net` |
| Project Key | `VNT` |
| Project ID | `10032` |
| Default Board | `1096` (Vantaca Home AI DLC) |
| Default Component | `Vantaca HXP` (id `10011`) |
| Default Label | **None.** `home_aidlc` is a *swim lane assignment* — apply it only to Features and Epics (which flow through the AI DLC automated lane). Bugs, Units, and other one-off types get no labels and land in the "everything else" column on board 1096. See the Swim Lane Rule below. |

### Issue Types

| Type | ID | Hierarchy | Use Case | Where it appears |
|------|-----|-----------|----------|------------------|
| Feature | `10446` | 1 | **Larger net-new product capability (PRD-scale).** Product-owned, contains Units as children. Replaces Epic. | Roadmap boards only — does **not** appear on the Home AI DLC kanban. |
| Unit | `10314` | 0 | **Small enhancement, improvement, or single engineering change.** Independently buildable, testable, deployable. Default for most engineering work. Replaces Story. | Home AI DLC board (1096) — backlog + kanban. |
| Bug | `10033` | 0 | **Client-reported problem or error.** Default for `--bug`. | Home AI DLC board (1096) — backlog + kanban. |
| Regression Defect | `10165` | 0 | **Internally-found regression** (QA, internal testing). Use when bug source is internal, not customer. | Home AI DLC board (1096) — backlog + kanban. |
| Spike | `10281` | 0 | Time-boxed investigation. | Home AI DLC board (1096). |
| Hotfix | `10076` | 0 | Emergency fix. | Home AI DLC board (1096). |
| Work Item Defect | `10164` | 0 | Internally-reported problem blocking a work item. | Home AI DLC board (1096). |
| Performance Defect | `10213` | 0 | Performance-class defect. | Home AI DLC board (1096). |
| Security Defect | `10214` | 0 | Security-class defect. | Home AI DLC board (1096). |
| Epic | `10000` | 1 | Legacy / cross-team grouping. Use Feature instead for new work. | Roadmap boards (mirrors Feature). |
| Story | `10009` | 0 | Legacy / non-Home flows. Use Unit instead for Home engineering work. | Home AI DLC board (1096). |

### Custom Field Reference

| Field | fieldId | Type | Notes |
|-------|---------|------|-------|
| Feature/Epic Name | `customfield_10011` | string | Short label (Feature or Epic only). Populated from `JIRA_FEATURE_NAME` or legacy `JIRA_EPIC_NAME`. |
| GTM Date | `customfield_10300` | date | `YYYY-MM-DD` (Feature / Epic only) |
| EA Date | `customfield_10683` | date | `YYYY-MM-DD` (Feature / Epic only). Early-access date introduced in Sam's 2026-05-22 process refresh. |
| Spec Reference | `customfield_10783` | URL string | Canonical home for the PRD's Word/SharePoint URL (Feature / Epic only). Sam's process refresh: downstream Teams comms and other automation read this field, so populate it whenever a published PRD URL exists. |
| Client Commitment | `customfield_10298` | labels array | `CAI`, `Vision`, or custom (Feature / Epic only) |
| Release Notes | `customfield_10499` | select | `None` / `Internal Only` / `External` |
| Regression Area | `customfield_10293` | multiselect | 260+ product area options — set in Jira UI, not in PM-OS drafts |
| Priority | `priority` | priority | Standard Jira priorities |
| Labels | `labels` | array of string | Swim lane assignment. `home_aidlc` → AI DLC automated lane (Features/Epics only). Empty → "everything else" column (bugs, ad-hoc work). No auto-prepend; the draft's labels are submitted as-is. |
| Parent | `parent` | issue link | Top-level field on Unit/Sub-task — value is `{"key": "VNT-XXXXX"}` |
| Assignee | `assignee` | account object | `{"accountId": "..."}`. **Features default to Jay Jenkins (`712020:aeec48b7-3829-433b-9125-c8c2a4c84e6f`) unless overridden.** Other types: leave unset unless user specifies. |

### Swim Lane Rule

The `home_aidlc` label plays two different roles depending on the issue type:

**For Features and Epics** — it's an *initiative tag*. Features and Epics live on roadmap boards (not on board 1096's kanban), but the label identifies them as part of the AI DLC initiative. PM-OS defaults Features and Epics to `["home_aidlc"]` for this reason.

**For Units, Bugs, and other backlog-tier types** — it's a *swim lane assignment* on the Home AI DLC board (1096):

- **With `home_aidlc`** → AI DLC swim lane (agent-driven, automated work the team consumes through pipelines).
- **Without any labels** → "everything else" column (manual kanban for ad-hoc Bugs, Regression Defects, Units, Spikes, Hotfixes, and other one-off work).

PM-OS defaults these types to `[]`. A Unit that's a child of an AI DLC Feature should mirror the parent's `home_aidlc` label so the Unit lands in the swim lane.

**Default by issue type:**

| Type | Default labels |
|---|---|
| Feature, Epic | `["home_aidlc"]` |
| Bug, Regression Defect, Hotfix, Work Item Defect, Performance Defect, Security Defect, Spike | `[]` (empty) |
| Unit, Story | `[]` by default. If the Unit is parented to a Feature/Epic that has `home_aidlc`, mirror the parent. |

**No-Invent Rule.** Do not synthesize labels from the ticket's topic, product area, customer name, or bug class. The Labels field is routing metadata controlled by the engineering team, not a tagging surface for AI-generated context — context belongs in the description. Only add a non-default label when the user explicitly dictates it in their prompt (e.g., "tag this `mobile-only`"). When in doubt, omit. The user can always add labels in the Jira UI after the fact; AI-generated labels are hard to remove once they spread.

**Publish behavior.** `jira_publish.py` submits the draft's labels as-is. No auto-prepend. If the draft has no `JIRA_LABELS`, the issue is created with no labels.

### Workflow Notes

- New issues default to **Refinement** status (some types — Unit, Feature — may default to Backlog; let Jira pick the initial transition)
- To transition out of Refinement to "To Do", these fields must be filled in Jira: Release Notes, Regression Area, Components
- The `Vantaca HXP` component makes the issue eligible for Home team boards
- The `home_aidlc` label has dual roles — initiative tag for Features/Epics (they live on roadmap boards), or swim lane assignment for Units/Bugs/etc. on board 1096. Defaults to applied for Features/Epics, omitted for everything else. See the Swim Lane Rule above.
- A `Unit` should be parented to a `Feature` (preferred) or `Epic` (legacy). Jira may reject Unit parents of other types — surface the error and let the user pick a valid parent.

---

## Phase 1: Determine What to Create

### If arguments are provided:
- `--feature "name"` → Phase 3 (Feature)
- `--unit "summary"` → Phase 4 (Unit)
- `--bug "summary"` → Phase 2 (Bug), default type=`Bug`
- `--regression "summary"` → Phase 2 (Bug flow), type=`Regression Defect`
- `--epic "name"` → Phase 5 (Legacy Epic)
- `--story "summary"` → Phase 5 (Legacy Story)

### If no arguments (interactive):
Ask the user:

> **Which type fits?**
>
> - **Is something broken or wrong?** → **Bug** (client-reported) or **Regression Defect** (caught internally by QA).
> - **Adding or changing something small** — a tweak, an improvement, a single capability change? → **Unit**. This is the default for most engineering work and is what you usually want.
> - **Net-new product capability** driven by a PRD or larger scope? → **Feature**. Only use this when the work is roadmap-tier; Features don't appear on the AI DLC kanban.
> - **Need to investigate before scoping?** → **Spike** (time-boxed investigation).
> - **Emergency fix?** → **Hotfix**.
> - Legacy hierarchy needed (Epic / Story)? → mention it explicitly.
>
> What would you like to create?

---

## Phase 2: Create a Bug or Regression Defect

### Step 2.1: Gather Required Info

Ask for (skip any already provided via arguments):

1. **Summary** (required): One-line title
2. **Description** (recommended): What's the issue? Provide context, steps to reproduce, expected vs actual behavior.
3. **Source** (only if type unknown): Was this reported by a client (→ `Bug`) or found internally by QA / product team (→ `Regression Defect`)?

### Step 2.2: Gather Optional Info

Ask if the user wants to set any of these now (they can always be added later in Jira):

- **Priority**: Highest / High / Medium / Low / Lowest
- **Release Notes**: None / Internal Only / External
- **Labels**: usually skip. Bugs default to no labels — they land in the "everything else" column on board 1096. Only ask if the user has already mentioned a specific label in their prompt. Do NOT volunteer topical tags. See the Swim Lane Rule above.

Do NOT ask about Regression Area — it has 260+ options and is better set in the Jira UI.

### Step 2.3: Create the Issue

```
mcp__claude_ai_Jira__createJiraIssue(
  cloudId: "vantaca.atlassian.net",
  projectKey: "VNT",
  issueTypeName: "Bug" | "Regression Defect",
  summary: "<user's summary>",
  description: "<user's description>",
  contentFormat: "markdown",
  additional_fields: {
    "components": [{"id": "10011"}],
    "labels": [],  // bugs default to no labels — "everything else" lane. Only populate if user explicitly named a label.
    // Include only if user provided values:
    "priority": {"name": "<priority>"},
    "customfield_10499": {"value": "<release notes choice>"}
  }
)
```

### Step 2.4: Report Result

Display:
- Issue key (e.g., `VNT-1234`)
- Direct link: `https://vantaca.atlassian.net/browse/VNT-1234`
- Type: `Bug` or `Regression Defect`
- Status: Refinement (default)
- Reminder: "To move to To Do, you'll need to set Release Notes, Regression Area, and Components in Jira (component is already set)."

---

## Phase 3: Create a Feature

Use this for larger net-new product capability work — PRD-scale, product-owned, contains Units as children. Replaces Epic for new work.

**Heads-up:** Features live on roadmap boards, not on the Home AI DLC kanban. If the work is a small enhancement or single change, use a Unit instead — that's where most engineering work belongs.

### Step 3.1: Gather Required Info

Ask for (skip any already provided):

1. **Feature Name** (required): Short label (e.g., "Mobile Push Notifications")
2. **Summary** (required): One-line summary (can match Feature Name or be more descriptive)
3. **Description / Outcome Detail** (required): What is this Feature about and why are we building it? This is the outcome detail required before inception. Keep the body lean per the Description hygiene rules — no meeting framing, no version narrative.

### Step 3.2: Gather Feature-Specific Fields

Ask each in turn (skip any already provided via arguments). For dates, accept `TBD` or empty as "leave the Jira field blank — Sam's process is fine with filling it in later."

1. **Spec Reference URL** (recommended): The Word/SharePoint URL of the PRD or spec document. This populates the dedicated **Spec Reference** field (`customfield_10783`) — downstream Teams comms key off it, per Sam's 2026-05-22 process refresh. Paste the URL, or skip to leave blank.
2. **GTM Date** (optional): `YYYY-MM-DD`, or `TBD` / empty.
3. **EA Date** (optional): `YYYY-MM-DD`, or `TBD` / empty. Early-access date — typically before GTM. New field in Sam's process refresh.
4. **Client Commitment** (optional): Is this committed for a specific event?
   - `CAI` — committed for CAI conference
   - `Vision` — committed for Vision conference
   - None — not event-committed (skip field)
5. **Assignee** (optional): Defaults to **Jay Jenkins** (`712020:aeec48b7-3829-433b-9125-c8c2a4c84e6f`) unless the user specifies someone else. Only ask if the user has already named a different person.

### Step 3.3: Create the Feature

```
mcp__claude_ai_Jira__createJiraIssue(
  cloudId: "vantaca.atlassian.net",
  projectKey: "VNT",
  issueTypeName: "Feature",
  summary: "<user's summary>",
  description: "<user's description with outcome detail>",
  contentFormat: "markdown",
  additional_fields: {
    "components": [{"id": "10011"}],
    "labels": ["home_aidlc"],  // Features go to the AI DLC swim lane
    "customfield_10011": "<feature name>",
    // Include only if user provided values:
    "customfield_10300": "<YYYY-MM-DD gtm date>",
    "customfield_10683": "<YYYY-MM-DD ea date>",
    "customfield_10783": "<absolute spec reference url>",
    "customfield_10298": ["<commitment flag>"],
    // Assignee: defaults to Jay Jenkins; override only if user specified someone else
    "assignee": {"accountId": "<accountId — default: 712020:aeec48b7-3829-433b-9125-c8c2a4c84e6f>"}
  }
)
```

### Step 3.4: Report Result

Display:
- Feature key (e.g., `VNT-5678`)
- Direct link: `https://vantaca.atlassian.net/browse/VNT-5678`
- Feature Name: displayed
- Spec Reference: displayed (if set) — confirm it renders as a clickable URL in Jira
- GTM Date: displayed (if set)
- EA Date: displayed (if set)
- Client Commitment: displayed (if set)
- Status: Refinement (default)

---

## Phase 4: Create a Unit

Use this for engineering work that is **a small enhancement, improvement, or single deployable change** — the default type for most Home engineering work. Replaces Story. Lands on the Home AI DLC board's backlog and kanban.

### Step 4.1: Gather Required Info

Ask for (skip any already provided):

1. **Summary** (required): One-line title
2. **Description** (required): What is this Unit doing? Include acceptance criteria when known.
3. **Parent issue key** (optional, recommended): The Feature or Epic this Unit belongs under (e.g., `VNT-42920`). Leave blank if not yet known — the Unit will be created unparented and you can wire it in Jira.

### Step 4.2: Gather Optional Info

Ask:

- **Priority**: Highest / High / Medium / Low / Lowest
- **Release Notes**: None / Internal Only / External
- **Labels**: usually skip. Units default to no labels — they land in the "everything else" column. If this Unit is a child of a Feature/Epic that lives in the AI DLC swim lane (`home_aidlc`), mirror the parent's label. Otherwise leave empty. Do NOT volunteer topical tags. See the Swim Lane Rule above.

### Step 4.3: Create the Unit

```
mcp__claude_ai_Jira__createJiraIssue(
  cloudId: "vantaca.atlassian.net",
  projectKey: "VNT",
  issueTypeName: "Unit",
  summary: "<user's summary>",
  description: "<user's description>",
  contentFormat: "markdown",
  additional_fields: {
    "components": [{"id": "10011"}],
    "labels": [],  // Units default to "everything else" — set to ["home_aidlc"] only if parented to a home_aidlc Feature
    // Include only if parent provided:
    "parent": {"key": "<VNT-XXXXX>"},
    // Include only if user provided values:
    "priority": {"name": "<priority>"},
    "customfield_10499": {"value": "<release notes choice>"}
  }
)
```

### Step 4.4: Report Result

Display:
- Unit key + URL
- Parent (if set) — confirm it linked correctly
- If unparented: "Heads-up — this Unit has no parent Feature/Epic yet. Wire it up in Jira when you know where it belongs."

---

## Phase 5: Legacy Epic / Story

Retained for cases where the user explicitly asks for Epic or Story, or for non-Home work routed through this skill. New Home work should prefer Feature / Unit (Phases 3 / 4).

The flow is identical to Phase 3 (Epic mirrors Feature) and Phase 4 (Story mirrors Unit). Substitute `issueTypeName: "Epic"` or `"Story"` accordingly. The legacy `JIRA_EPIC_NAME` field name is still accepted for Epic creation.

**Label defaults follow the Swim Lane Rule:** Epic defaults to `["home_aidlc"]` (mirrors Feature — AI DLC swim lane). Story defaults to `[]` (mirrors Unit — "everything else" column).

---

## Error Handling

- **MCP unavailable**: "The Jira MCP is not connected. Make sure you're running inside ~/pm-os/ with MCP integrations enabled."
- **Permission denied**: "You don't have permission to create issues in VNT. Check your Jira access."
- **Field validation error**: Display the error from Jira and suggest corrections.
- **Component not found**: Fall back to using the component name instead of ID: `[{"name": "Vantaca HXP"}]`
- **Parent issue invalid or wrong type**: Jira rejects Units parented to anything other than a Feature/Epic. Show the error, suggest a valid parent (Feature preferred), and offer to retry without the parent.
- **Unknown issue type**: Normalize common variants (`unit` → `Unit`, `regression defect` → `Regression Defect`, `feature` → `Feature`) before failing. If still unrecognized, list the valid types from the table above.

## Related Skills

- `prd-creation` — Create PRDs that can be linked to Features
- `publish-package` — Sync PRD packages to SharePoint (generates shareable URLs for Feature descriptions)
- `product-planning` — Meetings-to-backlog pipeline that may generate Unit / Bug drafts
