---
name: workflow-publish-package
description: Sync all markdown files in a product package folder to Word/OneDrive/SharePoint and return shareable Word Online URLs
triggers:
  - publish package
  - sync package to SharePoint
  - share package documents
  - Word Online links for package
  - convert package to Word
type: workflow
---

# Publish Package Skill

## Purpose

Convert all markdown files in a product package directory to Word documents via doc_sync, then present Word Online URLs for easy stakeholder sharing.

## When to Use

- User invokes `/project:publish-package`
- User asks to "publish" or "share" a product package
- User wants Word/SharePoint links for package documents
- After completing `/project:ship-it` or `/project:build` and ready to share

**When NOT to use:**
- Syncing individual files (use `doc-sync` skill directly)
- Syncing all tracked files (use `python3 scripts/doc_sync.py sync-all`)

## Workflow

### Step 1: Resolve Package Folder

**If a full path is provided** (e.g., `datasets/product/packages/2026/dynamic-forms/`):
- Verify the directory exists
- Verify it contains `.md` files

**If only a slug is provided** (e.g., `dynamic-forms`):
- Search `datasets/product/packages/*/` for a matching folder
- If multiple matches across years, ask user to disambiguate
- If no match, list available packages

**If no argument provided:**
- List available packages under `datasets/product/packages/`
- Ask user to select one

### Step 2: Preview Files

List all `.md` files that will be synced:
```
Found [count] files in datasets/product/packages/2026/dynamic-forms/:
  - PRD_dynamic-forms.md
  - context-brief.md
  - press-release-external.md
  ... etc
```

### Step 3: Run sync-folder

Execute:
```bash
python3 scripts/doc_sync.py sync-folder datasets/product/packages/{YYYY}/{slug}/ --json
```

Parse the JSON output to get file statuses and URLs.

### Step 4: Present Results

Display a formatted summary:

```
## Package Published: {slug}

| Document | Word Online |
|----------|-------------|
| context-brief.md | [Open in Word](url) |
| PRD_dynamic-forms.md | [Open in Word](url) |
| press-release-external.md | [Open in Word](url) |
... etc

**OneDrive folder**: PM-OS/product/packages/{YYYY}/{slug}/
{N} files synced successfully.
```

If any files failed, list them separately with error details.

## Error Handling

| Error | Action |
|-------|--------|
| Package folder not found | List available packages, ask user to pick |
| No .md files in folder | Warn user, suggest checking the path |
| pandoc not installed | Tell user to run `scripts/setup_doc_sync.sh` |
| Individual file conversion fails | Report which files failed, continue with rest |
| sync_config.yaml missing | Tell user to run `scripts/setup_doc_sync.sh` |

## Hand-off to Jira

After publish, two URLs from the result table feed the Jira Feature ticket:

- **`PRD_{slug}.md`** → the Jira Feature's **Spec Reference** field (`customfield_10783`). Sam's 2026-05-22 process refresh made this the load-bearing field for downstream Teams comms.
- **`press-release-internal.md`** → an "Internal Press Release" link in the Feature's description body, so reviewers can jump straight from the ticket to the announce-style narrative.

`/project:ship-it` Phase 7 pulls both automatically from `sync-folder --json`. For manual use: copy the URLs from the rendered table and paste into `/jira:create --feature`.

## Related Skills

- **doc-sync**: Lower-level document sync (single files, bidirectional)
- **prd-creation**: Creates PRDs that live in packages
- **ship-it / build**: Upstream workflows that create the package artifacts
- **workflow-jira-home**: Consumes the Spec Reference URL when drafting the Jira Feature
