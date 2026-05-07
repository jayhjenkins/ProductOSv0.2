# /project:publish-package

## MANDATORY: Use the publish-package Skill

**You MUST use the `publish-package` skill located at `.claude/skills/workflow-publish-package/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using publish-package to sync a product package to SharePoint/OneDrive"
2. **Read the skill**: Load `.claude/skills/workflow-publish-package/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Convert all markdown files in a product package folder to Word documents and sync them to OneDrive/SharePoint. Returns Word Online URLs for sharing with stakeholders.

## Arguments

- `$ARGUMENTS` — Package folder path or slug (e.g., `dynamic-forms` or `datasets/product/packages/2026/dynamic-forms/`)
