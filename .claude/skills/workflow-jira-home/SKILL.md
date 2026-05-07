---
name: workflow-jira-home
description: Create Jira tickets (bugs, stories) and epics on the Vantaca Home (HXP) board via the Jira MCP. Use when the user wants to log a bug, file a feature request, or create a PRD-linked epic for the Home product area.
triggers:
  - jira
  - create ticket
  - log bug
  - file bug
  - create epic
  - feature request
  - HXP board
  - Vantaca Home board
---

# Jira Home Ticket & Epic Creation

Create tickets and epics on the Vantaca Home (HXP) board using the Jira MCP.

## When to Use

- User wants to log a bug for Vantaca Home
- User wants to create a feature request (Story) for Home
- User wants to create an epic (often linked to a PRD or PRD package)
- User says "create a Jira ticket", "log this bug", "file a feature request", "create an epic"

## Draft Mode (Headless/Agent Context)

When invoked by the **ticket-creator worker** (headless agent dispatch), you operate in **draft mode**:
- You do NOT have access to Jira MCP tools
- You draft the ticket content in the task body using the `<!-- JIRA_DRAFT -->` format
- The human reviews the draft on the task board and clicks "Publish to Jira"
- Use this skill as a REFERENCE for field names, issue types, and configuration — not for direct publishing

When invoked **interactively** via `/jira:create` (human is in the CLI session), use the normal flow and call Jira MCP directly — the human is already in the loop.

### JIRA_DRAFT Format

```markdown
<!-- JIRA_DRAFT -->
<!-- JIRA_TYPE:Bug -->
<!-- JIRA_SUMMARY:Short summary here -->
<!-- JIRA_PRIORITY:High -->
<!-- JIRA_LABELS:hxp,regression -->
<!-- JIRA_RELEASE_NOTES:Internal Only -->
<!-- JIRA_EPIC_NAME: -->
<!-- JIRA_GTM_DATE: -->
<!-- JIRA_CLIENT_COMMITMENT: -->

### Summary
Short summary here

### Description
Full description with context...

### Fields
- **Type:** Bug
- **Priority:** High
- **Labels:** hxp, regression
- **Release Notes:** Internal Only
<!-- /JIRA_DRAFT -->
```

**Field rules:**
- `JIRA_TYPE`: Bug, Story, or Epic
- `JIRA_PRIORITY`: Highest, High, Medium, Low, Lowest (or empty for default)
- `JIRA_LABELS`: comma-separated (or empty)
- `JIRA_RELEASE_NOTES`: None, Internal Only, or External (or empty)
- Epic fields (`JIRA_EPIC_NAME`, `JIRA_GTM_DATE`, `JIRA_CLIENT_COMMITMENT`): only for Epics

## Jira Configuration

All values below are hardcoded from the Vantaca Jira instance.

| Setting | Value |
|---------|-------|
| Cloud ID | `vantaca.atlassian.net` |
| Project Key | `VNT` |
| Project ID | `10032` |
| Component | `Vantaca HXP` (id `10011`) |

### Issue Types

| Type | ID | Use Case |
|------|-----|----------|
| Bug | `10033` | Client-reported problems or errors |
| Story | `10009` | Feature requests, enhancements |
| Epic | `10000` | PRD-linked epics, roadmap items |

### Custom Field Reference

| Field | fieldId | Type | Notes |
|-------|---------|------|-------|
| Epic Name | `customfield_10011` | string | Short label (Epic only) |
| GTM Date | `customfield_10300` | date | `YYYY-MM-DD` (Epic only) |
| Client Commitment | `customfield_10298` | labels array | `CAI`, `Vision`, or custom (Epic only) |
| Release Notes | `customfield_10499` | select | `None` / `Internal Only` / `External` |
| Regression Area | `customfield_10293` | multiselect | 260+ product area options |
| Priority | `priority` | priority | Standard Jira priorities |
| Labels | `labels` | array of string | Free-form |

### Workflow Notes

- New tickets default to **Refinement** status (there is no Backlog status)
- To transition to "To Do", these fields must be filled: Release Notes, Regression Area, Components
- The `Vantaca HXP` component makes the ticket appear on the HXP board

---

## Phase 1: Determine What to Create

### If arguments are provided:
- `--bug "summary"` -> Skip to Phase 2 with type=Bug
- `--story "summary"` -> Skip to Phase 2 with type=Story
- `--epic "name"` -> Skip to Phase 3

### If no arguments (interactive):
Ask the user:
> What would you like to create?
> 1. **Bug** - Report a client-reported problem or error
> 2. **Story** - Feature request or enhancement
> 3. **Epic** - PRD-linked epic or roadmap item

---

## Phase 2: Create a Ticket (Bug or Story)

### Step 2.1: Gather Required Info

Ask for (skip any already provided via arguments):

1. **Summary** (required): One-line title for the ticket
2. **Description** (recommended): What's the issue or request? Provide context, steps to reproduce (for bugs), or expected behavior (for stories).

### Step 2.2: Gather Optional Info

Ask if the user wants to set any of these now (they can always be added later in Jira):

- **Priority**: Highest / High / Medium / Low / Lowest
- **Release Notes**: None / Internal Only / External
- **Labels**: Any tags to add

Do NOT ask about Regression Area — it has 260+ options and is better set in the Jira UI.

### Step 2.3: Create the Ticket

Build the `additional_fields` object and call:

```
mcp__claude_ai_Jira__createJiraIssue(
  cloudId: "vantaca.atlassian.net",
  projectKey: "VNT",
  issueTypeName: "Bug" or "Story",
  summary: "<user's summary>",
  description: "<user's description>",
  contentFormat: "markdown",
  additional_fields: {
    "components": [{"id": "10011"}],
    // Include only if user provided values:
    "priority": {"name": "<priority>"},
    "customfield_10499": {"value": "<release notes choice>"},
    "labels": ["<label1>", "<label2>"]
  }
)
```

### Step 2.4: Report Result

Display:
- Issue key (e.g., `VNT-1234`)
- Direct link: `https://vantaca.atlassian.net/browse/VNT-1234`
- Status: Refinement (default)
- Reminder: "To move to To Do, you'll need to set Release Notes, Regression Area, and Components in Jira (component is already set)."

---

## Phase 3: Create an Epic

### Step 3.1: Gather Required Info

Ask for (skip any already provided):

1. **Epic Name** (required): Short label for the epic (e.g., "Mobile Push Notifications")
2. **Summary** (required): One-line summary (can match epic name or be more descriptive)
3. **Description / Outcome Detail** (required): What is this epic about and why are we building it? This is the outcome detail that Alyssa requires before inception.

If the user provides a PRD package URL or path, incorporate it into the description:
- Add a "PRD Package" section with the link
- If it's a SharePoint/Word Online URL, include it directly
- If it's a local path, note it in the description for reference

### Step 3.2: Gather Epic-Specific Fields

Ask:

1. **GTM Date** (recommended): When do you expect this to ship? Format: `YYYY-MM-DD`. Even a rough quarter-end date is useful.
2. **Client Commitment** (recommended): Is this committed for a specific event?
   - `CAI` — committed for CAI conference
   - `Vision` — committed for Vision conference
   - None — not event-committed (skip field)

### Step 3.3: Create the Epic

```
mcp__claude_ai_Jira__createJiraIssue(
  cloudId: "vantaca.atlassian.net",
  projectKey: "VNT",
  issueTypeName: "Epic",
  summary: "<user's summary>",
  description: "<user's description with outcome detail>",
  contentFormat: "markdown",
  additional_fields: {
    "components": [{"id": "10011"}],
    "customfield_10011": "<epic name>",
    // Include only if user provided values:
    "customfield_10300": "<YYYY-MM-DD gtm date>",
    "customfield_10298": ["<commitment flag>"],
    "labels": ["<label1>"]
  }
)
```

### Step 3.4: Report Result

Display:
- Epic key (e.g., `VNT-5678`)
- Direct link: `https://vantaca.atlassian.net/browse/VNT-5678`
- Epic Name: displayed
- GTM Date: displayed (if set)
- Client Commitment: displayed (if set)
- Status: Refinement (default)

---

## Error Handling

- **MCP unavailable**: "The Jira MCP is not connected. Make sure you're running inside ~/pm-os/ with MCP integrations enabled."
- **Permission denied**: "You don't have permission to create issues in VNT. Check your Jira access."
- **Field validation error**: Display the error from Jira and suggest corrections.
- **Component not found**: Fall back to using the component name instead of ID: `[{"name": "Vantaca HXP"}]`

## Related Skills

- `prd-creation` — Create PRDs that can be linked to epics
- `publish-package` — Sync PRD packages to SharePoint (generates shareable URLs for epic descriptions)
- `product-planning` — Meetings-to-backlog pipeline that may generate tickets
