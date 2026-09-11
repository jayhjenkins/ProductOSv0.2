## MANDATORY: Use the workflow-jira-home Skill

Before doing anything else:
1. Announce: "Using the **workflow-jira-home** skill to create a Jira issue." (If this is the first run and Jira isn't configured yet, announce that First-Run Setup will run first.)
2. Read and follow `.claude/skills/workflow-jira-home/SKILL.md` exactly — including its First-Run Setup section if `profile/integrations.yaml` has no Jira config yet.

## Purpose

Create Jira issues via the Jira MCP, scoped to whichever project/board your profile is configured for (see First-Run Setup in the skill). Most issues (Bugs, work items, Regression Defects) land on the team's board backlog and kanban. Top-level issues (Features/Epics) typically live on roadmap boards and carry the profile's configured swim-lane label as an initiative tag, if one is set. Labels follow the Swim Lane Rule defined in `workflow-jira-home/SKILL.md` — the command does not invent topical labels.

## Arguments

Primary (new hierarchy):
- `/jira:create` — Interactive mode. Asks what kind of issue to create.
- `/jira:create --feature "name"` — Top-level issue (PRD-linked product capability).
- `/jira:create --unit "summary"` — Work item (small enhancement, improvement, or single engineering change — the default for most engineering work). Will prompt for an optional parent key.
- `/jira:create --bug "summary"` — Bug (client-reported defect).
- `/jira:create --regression "summary"` — Regression Defect (internally-found regression, if configured).

Other:
- `/jira:create --spike "summary"` — Time-boxed investigation (if configured).
- `/jira:create --hotfix "summary"` — Emergency fix (if configured).
- `/jira:create --epic "name"` — Legacy Epic flow (retained for special cases).
- `/jira:create --story "summary"` — Legacy Story flow (retained for special cases).

## What This Creates

**All issues:**
- Component set per profile (`component_id`), if configured
- Labels follow the Swim Lane Rule: top-level issues get the profile's `auto_label` (if configured); Bugs, work items, and other one-offs get no labels
- Defaults to the standard new-issue status for the type
- Optionally sets priority and release notes. Additional labels are only added when the user explicitly names one in their prompt — the command never invents topical tags.

**Work items (and legacy Stories):**
- Optional parent issue key (top-level type or Epic). If left blank, it's created unparented and the user can wire it in Jira.

**Top-level issues (and legacy Epics):**
- Sets the top-level name custom field, if configured
- Prompts for **Spec Reference** (a shareable PRD/spec URL), if configured
- Prompts for **Target Date** and **Early Access Date** — either can be left blank or `TBD` to fill in later in the Jira UI, if those fields are configured
- Prompts for a Commitment flag, if configured
- **Assignee defaults to the profile's `default_assignee`** unless a different person is specified

## Examples

```
/jira:create
/jira:create --feature "Mobile Push Notifications"
/jira:create --unit "Wire dashboard to new index"
/jira:create --bug "Landing page editor crashes on save"
/jira:create --regression "Amenity image not displaying"
/jira:create --spike "Investigate slow page load"
/jira:create --hotfix "Login loop on iOS 18.4"
```

Result URLs follow the pattern `https://{cloud_id}/browse/{project_key}-XXXXX`, where `{cloud_id}` and `{project_key}` come from your profile config.
