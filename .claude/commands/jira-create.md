## MANDATORY: Use the workflow-jira-home Skill

Before doing anything else:
1. Announce: "Using the **workflow-jira-home** skill to create an issue on the Vantaca Home AI DLC board (VNT, board 1096)."
2. Read and follow `.claude/skills/workflow-jira-home/SKILL.md` exactly.

## Purpose

Create Jira issues for Vantaca Home (project `VNT`) via the Jira MCP. Most issues (Bugs, Units, Regression Defects) land on the Home AI DLC board's backlog and kanban (board `1096`). Features and Epics live on the roadmap boards (not on the AI DLC kanban) and carry `home_aidlc` as an initiative tag. Labels follow the Swim Lane Rule defined in `workflow-jira-home/SKILL.md` — the command does not invent topical labels.

## Arguments

Primary (new hierarchy):
- `/jira:create` — Interactive mode. Asks what kind of issue to create.
- `/jira:create --feature "name"` — Feature (PRD-linked product capability). Replaces Epic for new work.
- `/jira:create --unit "summary"` — Unit (small enhancement, improvement, or single engineering change — the default for most engineering work). Replaces Story. Will prompt for an optional parent Feature/Epic key.
- `/jira:create --bug "summary"` — Bug (client-reported defect).
- `/jira:create --regression "summary"` — Regression Defect (internally-found regression).

Other:
- `/jira:create --spike "summary"` — Time-boxed investigation.
- `/jira:create --hotfix "summary"` — Emergency fix.
- `/jira:create --epic "name"` — Legacy Epic flow (retained for special cases).
- `/jira:create --story "summary"` — Legacy Story flow (retained for special cases).

## What This Creates

**All issues:**
- Component set to `Vantaca HXP` (id `10011`)
- Labels follow the Swim Lane Rule: Features/Epics get `home_aidlc` (AI DLC automated lane); Bugs, Units, and other one-offs get no labels (lands in "everything else" column on board 1096)
- Defaults to the standard new-issue status for the type (typically Refinement or Backlog)
- Optionally sets priority and release notes. Additional labels are only added when the user explicitly names one in their prompt — the command never invents topical tags.

**Units (and legacy Stories):**
- Optional parent issue key (Feature or Epic). If left blank, the Unit is created unparented and the user can wire it in Jira.

**Features (and legacy Epics):**
- Sets the Feature/Epic Name custom field
- Prompts for **Spec Reference** (the PRD/spec Word URL — Sam's 2026-05-22 process refresh; downstream Teams comms read this field)
- Prompts for **GTM Date** and **EA Date** — either can be left blank or `TBD` to fill in later in the Jira UI
- Prompts for Client Commitment flag (CAI / Vision)
- **Assignee defaults to Jay Jenkins** (`712020:aeec48b7-3829-433b-9125-c8c2a4c84e6f`) unless a different person is specified

## Examples

```
/jira:create
/jira:create --feature "Mobile Push Notifications"
/jira:create --unit "Wire Home dashboard to new homeowner index"
/jira:create --bug "Landing page WYSIWYG editor crashes on save"
/jira:create --regression "Home_V3 amenity image not displaying"
/jira:create --spike "Investigate slow My Requests page load"
/jira:create --hotfix "Login loop on iOS 18.4"
```

Result URLs follow the pattern `https://vantaca.atlassian.net/browse/VNT-XXXXX`.
