## MANDATORY: Use the jira-home Skill

Before doing anything else:
1. Announce: "Using the **Jira Home** skill to create a ticket/epic on the Vantaca HXP board."
2. Read and follow `.claude/skills/workflow-jira-home/SKILL.md` exactly.

## Purpose

Create Jira tickets (bugs, feature requests) and epics on the Vantaca Home (HXP) board using the Jira MCP integration.

## Arguments

- `/jira:create` — Interactive mode. Asks what type of issue to create.
- `/jira:create --bug "summary"` — Quick bug creation with the given summary.
- `/jira:create --story "summary"` — Quick story/feature request creation.
- `/jira:create --epic "epic name"` — Epic creation flow (will ask for additional details).

## What This Creates

**Tickets (Bug/Story):**
- Automatically sets component to `Vantaca HXP` so it appears on the HXP board
- Defaults to Refinement status
- Optionally sets priority, release notes, labels

**Epics:**
- Sets component to `Vantaca HXP`
- Prompts for GTM Date and Client Commitment flag (CAI/Vision) per team process
- Supports linking PRD packages in the description
- Defaults to Refinement status

## Examples

```
/jira:create
/jira:create --bug "Landing page WYSIWYG editor crashes on save"
/jira:create --story "Add push notification opt-in for residents"
/jira:create --epic "Mobile Push Notifications"
```
