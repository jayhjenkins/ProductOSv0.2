#!/usr/bin/env python3
"""
doc_sync_watcher.py — Bidirectional file watcher for MD <-> DOCX sync.

Watches local datasets/ for .md changes and OneDrive PM-OS/ for .docx changes.
Uses fswatch for file system events with debouncing to prevent loops.

Runs as a launchd daemon: ~/Library/LaunchAgents/com.pm-os.doc-sync.plist
"""

import os
import subprocess
import sys
import threading
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PM_OS_DIR = SCRIPT_DIR.parent

# Add script dir to path
sys.path.insert(0, str(SCRIPT_DIR))
import doc_sync

# Debounce tracking: path -> last_event_time
_local_pending = {}
_remote_pending = {}
_lock = threading.Lock()

LOCAL_DEBOUNCE_SEC = 3
REMOTE_DEBOUNCE_SEC = 5

# Temp file patterns to ignore
IGNORE_PATTERNS = {"~$", ".tmp", ".~lock", ".DS_Store"}


def should_ignore(path):
    """Check if a file path is a temp/lock file that should be ignored."""
    name = os.path.basename(path)
    return any(name.startswith(p) or name.endswith(p) for p in IGNORE_PATTERNS)


def process_local_events():
    """Process debounced local .md file changes."""
    while True:
        time.sleep(1)
        now = time.time()
        to_process = []
        with _lock:
            for path, event_time in list(_local_pending.items()):
                if now - event_time >= LOCAL_DEBOUNCE_SEC:
                    to_process.append(path)
                    del _local_pending[path]

        for path in to_process:
            try:
                config = doc_sync.load_config()
                p = Path(path)
                if not p.exists() or not p.suffix == ".md":
                    continue
                if not doc_sync.matches_sync_paths(p, config):
                    continue

                # Check manifest - skip if this is our own change
                manifest = doc_sync.load_manifest()
                key = str(p.relative_to(PM_OS_DIR))
                entry = manifest.get(key, {})
                cur_hash = doc_sync.file_hash(path)
                if cur_hash == entry.get("local_hash"):
                    continue  # Our own write, skip

                log(f"Local change detected: {key}")
                doc_sync.sync_one(path)
            except Exception as e:
                log(f"Error syncing local {path}: {e}")


def process_remote_events():
    """Process debounced remote .docx file changes."""
    while True:
        time.sleep(1)
        now = time.time()
        to_process = []
        with _lock:
            for path, event_time in list(_remote_pending.items()):
                if now - event_time >= REMOTE_DEBOUNCE_SEC:
                    to_process.append(path)
                    del _remote_pending[path]

        for path in to_process:
            try:
                p = Path(path)
                if not p.exists() or not p.suffix == ".docx":
                    continue

                # Check manifest - skip if this is our own change
                config = doc_sync.load_config()
                local_path = doc_sync.docx_to_md_path(p, config)
                manifest = doc_sync.load_manifest()
                key = str(local_path.relative_to(PM_OS_DIR))
                entry = manifest.get(key, {})
                cur_hash = doc_sync.file_hash(path)
                if cur_hash == entry.get("remote_hash"):
                    continue  # Our own write, skip

                log(f"Remote change detected: {p.name}")
                doc_sync.sync_back(path)
            except Exception as e:
                log(f"Error syncing remote {path}: {e}")


def watch_local(datasets_dir):
    """Watch local datasets/ directory for .md changes using fswatch."""
    cmd = [
        "fswatch", "-r", "--event", "Updated", "--event", "Created",
        "-e", r".*\.tmp.*", "-e", r".*~\$.*",
        "-i", r".*\.md$",
        str(datasets_dir),
    ]
    log(f"Watching local: {datasets_dir}")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)

    for line in iter(proc.stdout.readline, ""):
        path = line.strip()
        if not path or should_ignore(path):
            continue
        with _lock:
            _local_pending[path] = time.time()


def watch_remote(remote_dir):
    """Watch OneDrive PM-OS/ directory for .docx changes using fswatch."""
    cmd = [
        "fswatch", "-r", "--event", "Updated", "--event", "Created",
        "-e", r".*~\$.*", "-e", r".*\.tmp$",
        "-i", r".*\.docx$",
        str(remote_dir),
    ]
    log(f"Watching remote: {remote_dir}")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)

    for line in iter(proc.stdout.readline, ""):
        path = line.strip()
        if not path or should_ignore(path):
            continue
        with _lock:
            _remote_pending[path] = time.time()


def log(msg):
    """Print timestamped log message."""
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def main():
    config = doc_sync.load_config()

    if not config["sync_enabled"]:
        log("Sync disabled in config. Exiting.")
        sys.exit(0)

    datasets_dir = PM_OS_DIR / "datasets"
    remote_dir = doc_sync.onedrive_dir(config)

    if not datasets_dir.exists():
        log(f"Error: datasets directory not found: {datasets_dir}")
        sys.exit(1)

    if not remote_dir.exists():
        log(f"Warning: OneDrive directory not found: {remote_dir}")
        log("Creating it...")
        remote_dir.mkdir(parents=True, exist_ok=True)

    log("PM-OS Doc Sync Watcher starting")
    log(f"  Local:  {datasets_dir}")
    log(f"  Remote: {remote_dir}")

    # Start debounce processors
    threading.Thread(target=process_local_events, daemon=True).start()
    threading.Thread(target=process_remote_events, daemon=True).start()

    # Start watchers in threads
    local_thread = threading.Thread(target=watch_local, args=(datasets_dir,), daemon=True)
    remote_thread = threading.Thread(target=watch_remote, args=(remote_dir,), daemon=True)
    local_thread.start()
    remote_thread.start()

    log("Watcher running. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        log("Shutting down.")


if __name__ == "__main__":
    main()
