---
name: workflow-doc-sync
description: Bidirectional Markdown to Word document sync for SharePoint/OneDrive collaboration
triggers:
  - sync document to SharePoint
  - convert markdown to Word
  - doc sync
  - Word document sync
  - SharePoint sync
type: workflow
---

# Document Sync Skill

Manages bidirectional sync between local markdown files and Word documents in OneDrive/SharePoint.

## Architecture

```
Local MD files <-> pandoc <-> .docx in OneDrive sync folder <-> SharePoint
```

## Commands

### Manual Sync (single file)
```bash
python3 scripts/doc_sync.py sync-one datasets/product/prds/2026/example.md
```

### Sync Back (Word -> Markdown)
```bash
python3 scripts/doc_sync.py sync-back /path/to/OneDrive/PM-OS/product/prds/2026/example.docx
```

### Sync Folder (all .md files in a directory)
```bash
python3 scripts/doc_sync.py sync-folder datasets/product/packages/2026/example/ [--json]
```

### Sync All Tracked Files
```bash
python3 scripts/doc_sync.py sync-all
```

### Check Status
```bash
python3 scripts/doc_sync.py status
```

### Resolve Conflicts
```bash
python3 scripts/doc_sync.py resolve datasets/product/prds/2026/example.md
```

## Path Mapping

| Local | OneDrive |
|-------|----------|
| `datasets/product/prds/2026/X.md` | `{onedrive}/PM-OS/product/prds/2026/X.docx` |
| `datasets/strategy/memos/X.md` | `{onedrive}/PM-OS/strategy/memos/X.docx` |

Rule: strip `datasets/` prefix, mirror path, change `.md` to `.docx`.

## Conflict Resolution

When both local and remote files change since last sync:
1. Neither file is overwritten
2. Backup copies are created with `_CONFLICT_{timestamp}` suffix
3. Conflict logged to `logs/doc_sync_conflicts.log`
4. Run `resolve <path>` after manual merge (pushes local version)

## Watcher Daemon

Runs as launchd: `~/Library/LaunchAgents/com.pm-os.doc-sync.plist`

```bash
# Stop watcher
launchctl unload ~/Library/LaunchAgents/com.pm-os.doc-sync.plist

# Start watcher
launchctl load ~/Library/LaunchAgents/com.pm-os.doc-sync.plist
```

## Configuration

Edit `scripts/sync_config.yaml` to change:
- `onedrive_root` - OneDrive sync folder path
- `sync_paths` - Which file patterns to sync
- `sync_exclude` - Which patterns to skip

## Setup

Run `scripts/setup_doc_sync.sh` for first-time setup (installs pandoc, fswatch, configures launchd).

## Integration with Task System

When a task is completed with `--output`, the output artifact is automatically synced to SharePoint if it matches sync_paths. The task board UI shows "Open in Word" links for synced documents.
