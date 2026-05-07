#!/usr/bin/env python3
"""
doc_sync.py — Bidirectional Markdown <-> Word document sync engine.

Converts local markdown files to .docx (via pandoc) for SharePoint/OneDrive
collaboration, and syncs Word edits back to local markdown.

Usage:
  python3 scripts/doc_sync.py sync-one <md_path>      # Convert one md -> docx
  python3 scripts/doc_sync.py sync-back <docx_path>    # Convert one docx -> md
  python3 scripts/doc_sync.py sync-folder <dir> [--json] # Convert all md in dir -> docx
  python3 scripts/doc_sync.py sync-all                 # Sync all tracked files
  python3 scripts/doc_sync.py status                   # Show sync state
  python3 scripts/doc_sync.py resolve <md_path>        # Clear conflict state
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from fnmatch import fnmatch
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
PM_OS_DIR = SCRIPT_DIR.parent
CONFIG_PATH = SCRIPT_DIR / "sync_config.yaml"
MANIFEST_PATH = SCRIPT_DIR / "_sync_manifest.json"
REFERENCE_DOCX = SCRIPT_DIR / "pandoc_reference.docx"

# ─── Config Loading ───────────────────────────────────────────────────────────

def load_config():
    """Load sync configuration from sync_config.yaml."""
    if not CONFIG_PATH.exists():
        print(f"Error: Config not found at {CONFIG_PATH}")
        print("Run scripts/setup_doc_sync.sh to initialize.")
        sys.exit(1)

    # Simple YAML parsing for our flat config (avoids ruamel dependency)
    config = {
        "onedrive_root": "",
        "sharepoint_site": "PM-OS",
        "sharepoint_tenant_url": "",
        "sharepoint_doc_root": "",
        "sync_enabled": True,
        "sync_paths": [],
        "sync_exclude": [],
    }
    current_list = None
    with open(CONFIG_PATH) as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("onedrive_root:"):
                val = line.split(":", 1)[1].strip().strip('"').strip("'")
                config["onedrive_root"] = os.path.expanduser(val)
            elif line.startswith("sharepoint_site:"):
                val = line.split(":", 1)[1].strip().strip('"').strip("'")
                config["sharepoint_site"] = val
            elif line.startswith("sharepoint_tenant_url:"):
                val = line.split(":", 1)[1].strip().strip('"').strip("'")
                config["sharepoint_tenant_url"] = val
            elif line.startswith("sharepoint_doc_root:"):
                val = line.split(":", 1)[1].strip().strip('"').strip("'")
                config["sharepoint_doc_root"] = val
            elif line.startswith("sync_enabled:"):
                val = line.split(":", 1)[1].strip()
                config["sync_enabled"] = val.lower() == "true"
            elif line.startswith("sync_paths:"):
                current_list = "sync_paths"
            elif line.startswith("sync_exclude:"):
                current_list = "sync_exclude"
            elif current_list and line.strip().startswith("- "):
                config[current_list].append(line.strip()[2:].strip())
            elif not line.strip().startswith("#") and ":" in line and not line.startswith(" "):
                current_list = None

    return config


def onedrive_dir(config):
    """Return the PM-OS subfolder inside OneDrive."""
    return Path(config["onedrive_root"]) / config["sharepoint_site"]


# ─── Manifest ─────────────────────────────────────────────────────────────────

def load_manifest():
    """Load the sync manifest (tracked file pairs with hashes)."""
    if not MANIFEST_PATH.exists():
        return {}
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def save_manifest(manifest):
    """Save the sync manifest atomically."""
    tmp = MANIFEST_PATH.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(manifest, f, indent=2)
    tmp.rename(MANIFEST_PATH)


def file_hash(filepath):
    """Compute SHA-256 of a file. Returns None if file doesn't exist."""
    p = Path(filepath)
    if not p.exists():
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ─── Path Mapping ─────────────────────────────────────────────────────────────

def md_to_docx_path(md_path, config):
    """Map a local markdown path to its OneDrive docx path.

    Rule: strip 'datasets/' prefix, mirror directory structure, change .md -> .docx.
    Example: datasets/product/prds/2026/X.md -> {onedrive}/PM-OS/product/prds/2026/X.docx
    """
    rel = Path(md_path).relative_to(PM_OS_DIR)
    # Strip 'datasets/' prefix
    parts = rel.parts
    if parts[0] == "datasets":
        parts = parts[1:]
    rel_no_datasets = Path(*parts)
    docx_name = rel_no_datasets.with_suffix(".docx")
    return onedrive_dir(config) / docx_name


def docx_to_md_path(docx_path, config):
    """Map a OneDrive docx path back to local markdown path.

    Reverse of md_to_docx_path: add 'datasets/' prefix, change .docx -> .md.
    """
    rel = Path(docx_path).relative_to(onedrive_dir(config))
    md_name = rel.with_suffix(".md")
    return PM_OS_DIR / "datasets" / md_name


def matches_sync_paths(md_path, config):
    """Check if a markdown file matches any sync_paths patterns and not excluded."""
    rel = str(Path(md_path).relative_to(PM_OS_DIR))
    for pattern in config.get("sync_exclude", []):
        if fnmatch(rel, pattern):
            return False
    for pattern in config.get("sync_paths", []):
        if fnmatch(rel, pattern):
            return True
        # fnmatch **/ doesn't match zero directories; also try with **/ stripped
        # so datasets/product/file.md matches datasets/product/**/*.md
        if "**/" in pattern:
            flat = pattern.replace("**/", "", 1)
            if fnmatch(rel, flat):
                return True
    return False


# ─── YAML Frontmatter Handling ────────────────────────────────────────────────

def strip_frontmatter(md_text):
    """Strip YAML frontmatter from markdown. Returns (frontmatter_str, body).

    frontmatter_str includes the --- delimiters. body is everything after
    the closing --- (including any leading newline).
    """
    if not md_text.startswith("---"):
        return "", md_text
    parts = md_text.split("---", 2)
    if len(parts) < 3:
        return "", md_text
    frontmatter = f"---{parts[1]}---"
    body = parts[2]
    return frontmatter, body


def reattach_frontmatter(frontmatter_str, body):
    """Re-attach YAML frontmatter to a markdown body."""
    if not frontmatter_str:
        return body
    return frontmatter_str + body



# ─── Conversion ───────────────────────────────────────────────────────────────

def md_to_docx(md_path, docx_path):
    """Convert a markdown file to docx via pandoc.

    Strips YAML frontmatter before conversion (pandoc doesn't need it).
    Uses reference template for styling if available.
    """
    md_path = Path(md_path)
    docx_path = Path(docx_path)

    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    # Read and strip frontmatter
    md_text = md_path.read_text(encoding="utf-8")
    _, body = strip_frontmatter(md_text)

    # Write temp file without frontmatter
    tmp_md = md_path.with_suffix(".tmp.md")
    try:
        tmp_md.write_text(body, encoding="utf-8")

        # Ensure output directory exists
        docx_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = ["pandoc", str(tmp_md), "-o", str(docx_path), "--from=markdown", "--to=docx"]
        if REFERENCE_DOCX.exists():
            cmd.extend(["--reference-doc", str(REFERENCE_DOCX)])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            raise RuntimeError(f"pandoc failed: {result.stderr}")
    finally:
        tmp_md.unlink(missing_ok=True)

    return docx_path


def docx_to_md(docx_path, md_path):
    """Convert a docx file back to markdown via pandoc.

    Re-attaches the YAML frontmatter from the existing local markdown file.
    """
    docx_path = Path(docx_path)
    md_path = Path(md_path)

    if not docx_path.exists():
        raise FileNotFoundError(f"Word file not found: {docx_path}")

    # Preserve existing frontmatter
    frontmatter_str = ""
    if md_path.exists():
        existing = md_path.read_text(encoding="utf-8")
        frontmatter_str, _ = strip_frontmatter(existing)

    # Convert docx to markdown
    tmp_md = md_path.with_suffix(".pandoc-tmp.md")
    try:
        cmd = [
            "pandoc", str(docx_path), "-o", str(tmp_md),
            "--from=docx", "--to=markdown",
            "--wrap=none",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            raise RuntimeError(f"pandoc failed: {result.stderr}")

        new_body = tmp_md.read_text(encoding="utf-8")
    finally:
        tmp_md.unlink(missing_ok=True)

    # Re-attach frontmatter and write
    final = reattach_frontmatter(frontmatter_str, new_body)
    md_path.write_text(final, encoding="utf-8")

    return md_path


# ─── Sync Operations ─────────────────────────────────────────────────────────

def sync_one(local_path):
    """Convert a single markdown file to docx and update manifest."""
    config = load_config()
    local_path = Path(local_path).resolve()

    if not local_path.exists():
        print(f"Error: File not found: {local_path}")
        return False

    if not matches_sync_paths(local_path, config):
        print(f"Warning: {local_path} doesn't match any sync_paths patterns. Syncing anyway.")

    docx_path = md_to_docx_path(local_path, config)
    print(f"Converting: {local_path.relative_to(PM_OS_DIR)}")
    print(f"       -> {docx_path}")

    md_to_docx(local_path, docx_path)

    # Update manifest
    manifest = load_manifest()
    key = str(local_path.relative_to(PM_OS_DIR))
    manifest[key] = {
        "local_path": str(local_path),
        "remote_path": str(docx_path),
        "local_hash": file_hash(local_path),
        "remote_hash": file_hash(docx_path),
        "last_sync": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "direction": "local->remote",
        "status": "synced",
    }
    save_manifest(manifest)
    print("Synced.")
    return True


def sync_back(remote_path):
    """Convert a docx change back to markdown and update manifest."""
    config = load_config()
    remote_path = Path(remote_path).resolve()

    if not remote_path.exists():
        print(f"Error: File not found: {remote_path}")
        return False

    local_path = docx_to_md_path(remote_path, config)
    manifest = load_manifest()
    key = str(local_path.relative_to(PM_OS_DIR))

    # Check for conflict: both sides changed since last sync
    entry = manifest.get(key, {})
    if entry:
        old_local_hash = entry.get("local_hash")
        old_remote_hash = entry.get("remote_hash")
        cur_local_hash = file_hash(local_path)
        cur_remote_hash = file_hash(remote_path)

        local_changed = old_local_hash and cur_local_hash and cur_local_hash != old_local_hash
        remote_changed = old_remote_hash and cur_remote_hash and cur_remote_hash != old_remote_hash

        if local_changed and remote_changed:
            # CONFLICT: both sides edited
            ts = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
            conflict_md = local_path.with_stem(f"{local_path.stem}_CONFLICT_{ts}")
            conflict_docx = remote_path.with_stem(f"{remote_path.stem}_CONFLICT_{ts}")

            import shutil
            shutil.copy2(local_path, conflict_md)
            shutil.copy2(remote_path, conflict_docx)

            entry["status"] = "conflict"
            entry["conflict_time"] = ts
            manifest[key] = entry
            save_manifest(manifest)

            # Log conflict
            log_dir = PM_OS_DIR / "logs"
            log_dir.mkdir(exist_ok=True)
            with open(log_dir / "doc_sync_conflicts.log", "a") as f:
                f.write(f"{ts} CONFLICT: {key}\n")
                f.write(f"  Local backup:  {conflict_md}\n")
                f.write(f"  Remote backup: {conflict_docx}\n\n")

            print(f"CONFLICT detected for {key}")
            print(f"  Both local and remote changed since last sync.")
            print(f"  Backup copies created. Run 'resolve' after manual merge.")
            return False

    print(f"Syncing back: {remote_path}")
    print(f"         -> {local_path}")

    docx_to_md(remote_path, local_path)

    # Update manifest
    manifest[key] = {
        "local_path": str(local_path),
        "remote_path": str(remote_path),
        "local_hash": file_hash(local_path),
        "remote_hash": file_hash(remote_path),
        "last_sync": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "direction": "remote->local",
        "status": "synced",
    }
    save_manifest(manifest)
    print("Synced.")
    return True


def sync_all():
    """Sync all files matching sync_paths patterns."""
    config = load_config()
    if not config["sync_enabled"]:
        print("Sync is disabled in config.")
        return

    manifest = load_manifest()
    synced = 0
    errors = 0

    for pattern in config.get("sync_paths", []):
        # Glob for matching files
        base = PM_OS_DIR
        for md_file in base.glob(pattern):
            if not md_file.is_file() or md_file.suffix != ".md":
                continue
            if not matches_sync_paths(md_file, config):
                continue
            try:
                sync_one(str(md_file))
                synced += 1
            except Exception as e:
                print(f"Error syncing {md_file}: {e}")
                errors += 1

    print(f"\nSync complete: {synced} files synced, {errors} errors.")


def sync_folder(dir_path, json_output=False):
    """Sync all .md files in a directory (non-recursive) to OneDrive.

    Converts each markdown file to docx via sync_one(), then prints a summary
    table with Word Online URLs, or structured JSON when json_output=True.
    """
    config = load_config()
    dir_path = Path(dir_path).resolve()

    if not dir_path.is_dir():
        print(f"Error: Not a directory: {dir_path}")
        return False

    md_files = sorted(dir_path.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {dir_path}")
        return False

    results = []
    errors = 0

    for md_file in md_files:
        try:
            if json_output:
                # Suppress sync_one's stdout when producing JSON
                _real_stdout = sys.stdout
                sys.stdout = open(os.devnull, "w")
                try:
                    sync_one(str(md_file))
                finally:
                    sys.stdout.close()
                    sys.stdout = _real_stdout
            else:
                sync_one(str(md_file))
            docx_path = md_to_docx_path(md_file, config)
            url = sharepoint_url_for(str(md_file))
            results.append({
                "file": md_file.name,
                "docx_path": str(docx_path),
                "url": url or "(URL not configured)",
                "status": "synced",
            })
        except Exception as e:
            results.append({
                "file": md_file.name,
                "docx_path": "",
                "url": "",
                "status": f"error: {e}",
            })
            errors += 1

    if json_output:
        import json as json_mod
        print(json_mod.dumps({"folder": str(dir_path), "files": results}, indent=2))
    else:
        print(f"\n{'File':<45} {'Status':<10} {'Word Online URL'}")
        print("-" * 120)
        for r in results:
            print(f"{r['file']:<45} {r['status']:<10} {r['url']}")
        print(f"\n{len(results) - errors}/{len(results)} files synced successfully.")

    return errors == 0


def status():
    """Show all tracked file pairs and their sync state."""
    manifest = load_manifest()

    if not manifest:
        print("No files tracked. Use 'sync-one <path>' to start syncing.")
        return

    print(f"{'Status':<10} {'Direction':<15} {'Last Sync':<22} {'File'}")
    print("-" * 90)

    for key, entry in sorted(manifest.items()):
        st = entry.get("status", "unknown")
        direction = entry.get("direction", "?")
        last_sync = entry.get("last_sync", "never")
        print(f"{st:<10} {direction:<15} {last_sync:<22} {key}")

        # Check for drift
        cur_local = file_hash(entry.get("local_path", ""))
        cur_remote = file_hash(entry.get("remote_path", ""))
        if cur_local != entry.get("local_hash"):
            print(f"  {'^ local changed since last sync':>50}")
        if cur_remote != entry.get("remote_hash"):
            print(f"  {'^ remote changed since last sync':>50}")


def resolve(local_path):
    """Clear conflict state for a file after manual resolution."""
    local_path = Path(local_path).resolve()
    manifest = load_manifest()
    key = str(local_path.relative_to(PM_OS_DIR))

    if key not in manifest:
        print(f"File not tracked: {key}")
        return False

    entry = manifest[key]
    if entry.get("status") != "conflict":
        print(f"File is not in conflict state (current: {entry.get('status')})")
        return False

    # Re-sync local -> remote
    config = load_config()
    docx_path = md_to_docx_path(local_path, config)
    md_to_docx(local_path, docx_path)

    entry["local_hash"] = file_hash(local_path)
    entry["remote_hash"] = file_hash(docx_path)
    entry["last_sync"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    entry["direction"] = "local->remote (resolved)"
    entry["status"] = "synced"
    del entry["conflict_time"]

    manifest[key] = entry
    save_manifest(manifest)
    print(f"Conflict resolved for {key}. Local version pushed to remote.")
    return True


def sharepoint_path_for(local_path):
    """Return the OneDrive/SharePoint path for a local markdown file, or None."""
    try:
        config = load_config()
    except SystemExit:
        return None
    local_path = Path(local_path).resolve()
    if not matches_sync_paths(local_path, config):
        return None
    return str(md_to_docx_path(local_path, config))


def _build_sharepoint_url(config, onedrive_rel_path):
    """Build a Word Online URL from a path relative to the OneDrive root.

    Uses the :w:/r/ URL pattern which opens .docx files in Word Online.
    Example: PM-OS/product/file.docx ->
      https://vantaca-my.sharepoint.com/:w:/r/personal/.../Documents/PM-OS/product/file.docx
    """
    tenant_url = config.get("sharepoint_tenant_url")
    doc_root = config.get("sharepoint_doc_root")
    if not tenant_url or not doc_root:
        return None
    from urllib.parse import quote
    server_path = f"{doc_root}/{onedrive_rel_path}"
    encoded_path = quote(server_path, safe="/")
    return f"{tenant_url}/:w:/r{encoded_path}?web=1"


def sharepoint_url_for(local_path):
    """Return a browser-openable SharePoint/OneDrive URL for a local markdown file, or None.

    Uses the :w:/r/ URL pattern which opens Word Online in the browser.
    Requires sharepoint_tenant_url and sharepoint_doc_root in sync_config.yaml.
    """
    try:
        config = load_config()
    except SystemExit:
        return None

    local_path = Path(local_path).resolve()
    if not matches_sync_paths(local_path, config):
        return None

    docx_path = md_to_docx_path(local_path, config)
    rel = docx_path.relative_to(Path(config["onedrive_root"]).expanduser())
    return _build_sharepoint_url(config, rel)


def sharepoint_url_from_docx_path(docx_path):
    """Convert a local OneDrive docx path to a browser-openable SharePoint URL, or None.

    Use this for tasks that already have sharepoint_path but not sharepoint_url.
    """
    try:
        config = load_config()
    except SystemExit:
        return None

    try:
        rel = Path(docx_path).relative_to(Path(config["onedrive_root"]).expanduser())
    except ValueError:
        return None

    return _build_sharepoint_url(config, rel)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "sync-one":
        if len(sys.argv) < 3:
            print("Usage: doc_sync.py sync-one <md_path>")
            sys.exit(1)
        path = Path(sys.argv[2])
        if not path.is_absolute():
            path = PM_OS_DIR / path
        success = sync_one(str(path))
        sys.exit(0 if success else 1)

    elif cmd == "sync-back":
        if len(sys.argv) < 3:
            print("Usage: doc_sync.py sync-back <docx_path>")
            sys.exit(1)
        success = sync_back(sys.argv[2])
        sys.exit(0 if success else 1)

    elif cmd == "sync-folder":
        if len(sys.argv) < 3:
            print("Usage: doc_sync.py sync-folder <directory> [--json]")
            sys.exit(1)
        path = Path(sys.argv[2])
        if not path.is_absolute():
            path = PM_OS_DIR / path
        json_flag = "--json" in sys.argv[3:]
        success = sync_folder(str(path), json_output=json_flag)
        sys.exit(0 if success else 1)

    elif cmd == "sync-all":
        sync_all()

    elif cmd == "status":
        status()

    elif cmd == "resolve":
        if len(sys.argv) < 3:
            print("Usage: doc_sync.py resolve <md_path>")
            sys.exit(1)
        path = Path(sys.argv[2])
        if not path.is_absolute():
            path = PM_OS_DIR / path
        success = resolve(str(path))
        sys.exit(0 if success else 1)

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
