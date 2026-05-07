#!/usr/bin/env python3
"""
annotate_meetings.py — Lightweight annotation server for meeting domain classification.

Serves a keyboard-driven web UI on port 8750 for reviewing/correcting the domain
classification of meeting transcripts. Annotations are saved to disk immediately
and the tool is resume-safe.

Usage:
    python3 scripts/annotate_meetings.py
    # Then open http://localhost:8750
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs

PORT = 8750
MEETINGS_DIR = Path(__file__).resolve().parent.parent / "datasets" / "meetings"
ANNOTATIONS_PATH = (
    Path(__file__).resolve().parent.parent
    / "datasets"
    / "evals"
    / "meeting-classifier"
    / "annotations.json"
)

VALID_DOMAINS = [
    "recruiting",
    "product/payments",
    "product/home",
    "product/platform",
    "leadership",
    "strategy",
    "customer",
    "general",
]


def _parse_frontmatter(text):
    """Extract YAML frontmatter as a dict from text between --- markers."""
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        # Simple key: "value" or key: value parser (no nested YAML needed)
        kv = re.match(r'^(\w[\w_]*)\s*:\s*"?(.+?)"?\s*$', line)
        if kv:
            key, val = kv.group(1), kv.group(2)
            if val.startswith("["):
                # Parse simple YAML arrays like ["a", "b"]
                try:
                    fm[key] = json.loads(val.replace("'", '"'))
                except json.JSONDecodeError:
                    fm[key] = val
            else:
                fm[key] = val
    return fm


def _domain_from_path(rel_path):
    """Extract domain from the relative file path (e.g., product/home/2026-03/file.txt -> product/home)."""
    parts = Path(rel_path).parts
    if len(parts) >= 2 and parts[0] == "product":
        return f"product/{parts[1]}"
    if len(parts) >= 1 and parts[0] in ("recruiting", "leadership", "strategy", "customer", "general"):
        return parts[0]
    return "unknown"


def _transcript_preview(text, max_chars=500):
    """Extract first max_chars of transcript body (after frontmatter and heading)."""
    # Strip frontmatter
    m = re.match(r"^---\n.*?\n---\n?", text, re.DOTALL)
    body = text[m.end():] if m else text
    # Strip the title heading and date line
    body = re.sub(r"^#[^\n]*\n", "", body)
    body = re.sub(r"^Date:[^\n]*\n", "", body)
    body = body.strip()
    if len(body) > max_chars:
        # Cut at last space before limit
        body = body[:max_chars].rsplit(" ", 1)[0] + "..."
    return body


def scan_meetings():
    """Scan all meeting .txt files and return metadata list."""
    meetings = []
    for txt_path in sorted(MEETINGS_DIR.rglob("*.txt")):
        rel = txt_path.relative_to(MEETINGS_DIR)
        rel_str = str(rel)
        try:
            text = txt_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        fm = _parse_frontmatter(text)
        path_domain = _domain_from_path(rel_str)
        fm_domain = fm.get("domain", "")
        preview = _transcript_preview(text)

        participants = fm.get("participants", "")
        if isinstance(participants, str) and participants.startswith("["):
            try:
                participants = json.loads(participants.replace("'", '"'))
            except json.JSONDecodeError:
                pass

        meetings.append({
            "rel_path": rel_str,
            "title": fm.get("title", txt_path.stem),
            "date": fm.get("date", ""),
            "duration_minutes": fm.get("duration_minutes", ""),
            "participants": participants if isinstance(participants, list) else [],
            "path_domain": path_domain,
            "frontmatter_domain": fm_domain,
            "domain_mismatch": path_domain != fm_domain and fm_domain != "",
            "preview": preview,
        })

    # Sort by date descending (newest first for faster annotation of recent meetings)
    meetings.sort(key=lambda m: m.get("date", ""), reverse=True)
    return meetings


def load_annotations():
    """Load existing annotations from disk."""
    if ANNOTATIONS_PATH.exists():
        return json.loads(ANNOTATIONS_PATH.read_text())
    return {
        "created": datetime.now(timezone.utc).isoformat(),
        "updated": datetime.now(timezone.utc).isoformat(),
        "stats": {"total": 0, "annotated": 0, "changed": 0},
        "annotations": {},
    }


def save_annotations(data):
    """Save annotations to disk."""
    ANNOTATIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["updated"] = datetime.now(timezone.utc).isoformat()
    # Recompute stats
    annotations = data.get("annotations", {})
    data["stats"]["annotated"] = len(annotations)
    data["stats"]["changed"] = sum(
        1 for a in annotations.values() if a.get("original_domain") != a.get("correct_domain")
    )
    ANNOTATIONS_PATH.write_text(json.dumps(data, indent=2))


# Pre-scan meetings at startup
print(f"Scanning meetings in {MEETINGS_DIR}...")
ALL_MEETINGS = scan_meetings()
print(f"Found {len(ALL_MEETINGS)} meetings.")


HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Meeting Classifier Annotation</title>
<style>
  :root {
    --bg: #1a1a2e;
    --card-bg: #16213e;
    --text: #e0e0e0;
    --text-dim: #8888aa;
    --accent: #0f3460;
    --green: #2ecc71;
    --yellow: #f1c40f;
    --red: #e74c3c;
    --blue: #3498db;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'SF Mono', 'Fira Code', monospace;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  /* Top bar */
  .topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 24px;
    background: var(--accent);
    border-bottom: 1px solid #333;
  }
  .topbar h1 { font-size: 16px; font-weight: 600; }
  .progress-info { font-size: 14px; color: var(--text-dim); }
  .progress-bar {
    width: 200px;
    height: 6px;
    background: #333;
    border-radius: 3px;
    overflow: hidden;
  }
  .progress-fill {
    height: 100%;
    background: var(--green);
    transition: width 0.3s;
  }
  .filter-controls { display: flex; gap: 8px; align-items: center; }
  .filter-controls button {
    padding: 4px 12px;
    border-radius: 4px;
    border: 1px solid #555;
    background: transparent;
    color: var(--text);
    cursor: pointer;
    font-size: 12px;
  }
  .filter-controls button.active { background: var(--blue); border-color: var(--blue); }

  /* Main content */
  .main { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 24px; }

  .card {
    background: var(--card-bg);
    border-radius: 8px;
    padding: 24px;
    max-width: 800px;
    width: 100%;
    border: 1px solid #333;
  }
  .card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
  .card-title { font-size: 20px; font-weight: 600; flex: 1; }
  .card-meta { font-size: 13px; color: var(--text-dim); margin-bottom: 12px; }
  .card-meta span { margin-right: 16px; }

  .domain-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 13px;
    font-weight: 600;
  }
  .domain-current { background: var(--accent); border: 1px solid var(--blue); }
  .domain-fm { background: #333; border: 1px solid var(--yellow); }
  .domain-mismatch-warning {
    color: var(--yellow);
    font-size: 12px;
    margin-left: 8px;
  }

  .preview {
    background: #0d1117;
    border-radius: 4px;
    padding: 16px;
    font-size: 13px;
    line-height: 1.6;
    max-height: 250px;
    overflow-y: auto;
    white-space: pre-wrap;
    color: #ccc;
    margin-top: 12px;
  }

  .annotation-status {
    margin-top: 12px;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 13px;
    font-weight: 600;
  }
  .annotation-correct { background: rgba(46, 204, 113, 0.15); color: var(--green); }
  .annotation-changed { background: rgba(241, 196, 15, 0.15); color: var(--yellow); }

  /* Action bar */
  .action-bar {
    max-width: 800px;
    width: 100%;
    margin-top: 16px;
  }
  .action-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    justify-content: center;
    margin-bottom: 8px;
  }
  .domain-btn {
    padding: 8px 16px;
    border-radius: 6px;
    border: 1px solid #555;
    background: var(--card-bg);
    color: var(--text);
    cursor: pointer;
    font-size: 13px;
    transition: all 0.15s;
    min-width: 140px;
    text-align: left;
  }
  .domain-btn:hover { border-color: var(--blue); background: var(--accent); }
  .domain-btn .key {
    display: inline-block;
    width: 20px;
    height: 20px;
    line-height: 20px;
    text-align: center;
    background: #555;
    border-radius: 3px;
    font-size: 11px;
    margin-right: 6px;
    font-weight: 700;
  }
  .confirm-btn {
    padding: 10px 32px;
    border-radius: 6px;
    border: 2px solid var(--green);
    background: rgba(46, 204, 113, 0.15);
    color: var(--green);
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: all 0.15s;
  }
  .confirm-btn:hover { background: rgba(46, 204, 113, 0.3); }

  /* Navigation */
  .nav-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 12px;
    max-width: 800px;
    width: 100%;
  }
  .nav-btn {
    padding: 6px 16px;
    border-radius: 4px;
    border: 1px solid #555;
    background: transparent;
    color: var(--text);
    cursor: pointer;
    font-size: 13px;
  }
  .nav-btn:hover { border-color: var(--blue); }
  .nav-btn:disabled { opacity: 0.3; cursor: default; }

  /* Legend */
  .legend {
    max-width: 800px;
    width: 100%;
    margin-top: 16px;
    font-size: 12px;
    color: var(--text-dim);
    text-align: center;
  }

  /* Stats bar */
  .stats-bar {
    max-width: 800px;
    width: 100%;
    margin-top: 16px;
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
    font-size: 12px;
    color: var(--text-dim);
  }
  .stat { padding: 4px 8px; background: var(--card-bg); border-radius: 4px; }
  .stat-changed { color: var(--yellow); }

  .empty-state {
    text-align: center;
    padding: 48px;
    color: var(--text-dim);
    font-size: 16px;
  }
</style>
</head>
<body>

<div class="topbar">
  <h1>Meeting Classifier Annotation</h1>
  <div style="display:flex; gap:16px; align-items:center;">
    <div class="filter-controls">
      <button id="filterAll" class="active" onclick="setFilter('all')">All</button>
      <button id="filterUnannotated" onclick="setFilter('unannotated')">Unannotated (F)</button>
      <button id="filterChanged" onclick="setFilter('changed')">Changed</button>
    </div>
    <div>
      <span class="progress-info" id="progressText">0 / 0</span>
      <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
    </div>
  </div>
</div>

<div class="main">
  <div class="card" id="meetingCard">
    <div id="cardContent"></div>
  </div>

  <div class="action-bar" id="actionBar">
    <div class="action-row" id="domainButtons"></div>
    <div class="action-row">
      <button class="confirm-btn" onclick="annotate(null)">Correct (Enter/Space)</button>
    </div>
  </div>

  <div class="nav-row">
    <button class="nav-btn" id="prevBtn" onclick="navigate(-1)">&larr; Back</button>
    <span id="positionText" style="font-size:13px; color:var(--text-dim);"></span>
    <button class="nav-btn" id="nextBtn" onclick="navigate(1)">Skip &rarr;</button>
  </div>

  <div class="legend">
    Keys: <b>Enter/Space</b> = Correct &nbsp; <b>1-8</b> = Reassign domain &nbsp;
    <b>&larr;/&rarr;</b> = Navigate &nbsp; <b>F</b> = Toggle unannotated filter
  </div>

  <div class="stats-bar" id="statsBar"></div>
</div>

<script>
const DOMAINS = [
  "recruiting", "product/payments", "product/home", "product/platform",
  "leadership", "strategy", "customer", "general"
];

let meetings = [];
let annotations = {};
let currentIndex = 0;
let filterMode = "all";  // "all", "unannotated", "changed"

async function init() {
  const resp = await fetch("/api/meetings");
  const data = await resp.json();
  meetings = data.meetings;
  annotations = data.annotations || {};
  renderDomainButtons();
  renderMeeting();
}

function getFilteredIndices() {
  const indices = [];
  for (let i = 0; i < meetings.length; i++) {
    const m = meetings[i];
    const ann = annotations[m.rel_path];
    if (filterMode === "unannotated" && ann) continue;
    if (filterMode === "changed" && (!ann || ann.original_domain === ann.correct_domain)) continue;
    indices.push(i);
  }
  return indices;
}

function renderDomainButtons() {
  const container = document.getElementById("domainButtons");
  container.innerHTML = DOMAINS.map((d, i) =>
    `<button class="domain-btn" onclick="annotate('${d}')">` +
    `<span class="key">${i + 1}</span>${d}</button>`
  ).join("");
}

function renderMeeting() {
  const filtered = getFilteredIndices();
  const content = document.getElementById("cardContent");

  if (filtered.length === 0) {
    content.innerHTML = '<div class="empty-state">No meetings match the current filter.</div>';
    document.getElementById("actionBar").style.display = "none";
    updateProgress();
    return;
  }
  document.getElementById("actionBar").style.display = "";

  // Clamp currentIndex to filtered range
  if (currentIndex < 0) currentIndex = 0;
  if (currentIndex >= filtered.length) currentIndex = filtered.length - 1;

  const realIdx = filtered[currentIndex];
  const m = meetings[realIdx];
  const ann = annotations[m.rel_path];

  let mismatchHtml = "";
  if (m.domain_mismatch) {
    mismatchHtml = `<span class="domain-mismatch-warning">&#9888; Frontmatter says: <span class="domain-badge domain-fm">${m.frontmatter_domain}</span></span>`;
  }

  let annotationHtml = "";
  if (ann) {
    if (ann.original_domain === ann.correct_domain) {
      annotationHtml = `<div class="annotation-status annotation-correct">&#10003; Confirmed correct</div>`;
    } else {
      annotationHtml = `<div class="annotation-status annotation-changed">&#8594; Reclassified to: ${ann.correct_domain}</div>`;
    }
  }

  const participants = Array.isArray(m.participants) ? m.participants.join(", ") : "";

  content.innerHTML = `
    <div class="card-header">
      <div class="card-title">${escHtml(m.title)}</div>
    </div>
    <div class="card-meta">
      <span>${m.date}</span>
      ${m.duration_minutes ? `<span>${m.duration_minutes} min</span>` : ""}
      ${participants ? `<span>${escHtml(participants)}</span>` : ""}
    </div>
    <div style="margin-bottom:12px;">
      <span class="domain-badge domain-current">${m.path_domain}</span>
      ${mismatchHtml}
    </div>
    ${annotationHtml}
    <div class="preview">${escHtml(m.preview)}</div>
  `;

  document.getElementById("positionText").textContent =
    `${currentIndex + 1} of ${filtered.length}` + (filterMode !== "all" ? ` (${filterMode})` : "");
  document.getElementById("prevBtn").disabled = currentIndex <= 0;
  document.getElementById("nextBtn").disabled = currentIndex >= filtered.length - 1;

  updateProgress();
  updateStats();
}

function updateProgress() {
  const total = meetings.length;
  const annotated = Object.keys(annotations).length;
  document.getElementById("progressText").textContent = `${annotated} / ${total} annotated`;
  document.getElementById("progressFill").style.width = total > 0 ? `${(annotated / total) * 100}%` : "0%";
}

function updateStats() {
  const counts = {};
  DOMAINS.forEach(d => counts[d] = { total: 0, annotated: 0, changed: 0 });
  meetings.forEach(m => {
    if (counts[m.path_domain]) counts[m.path_domain].total++;
    const ann = annotations[m.rel_path];
    if (ann) {
      if (counts[m.path_domain]) counts[m.path_domain].annotated++;
      if (ann.original_domain !== ann.correct_domain) {
        if (counts[m.path_domain]) counts[m.path_domain].changed++;
      }
    }
  });
  const bar = document.getElementById("statsBar");
  bar.innerHTML = DOMAINS.map(d => {
    const c = counts[d];
    const changedStr = c.changed > 0 ? ` <span class="stat-changed">(${c.changed} changed)</span>` : "";
    return `<span class="stat">${d}: ${c.annotated}/${c.total}${changedStr}</span>`;
  }).join("");
}

async function annotate(domain) {
  const filtered = getFilteredIndices();
  if (filtered.length === 0) return;
  const realIdx = filtered[currentIndex];
  const m = meetings[realIdx];

  const correctDomain = domain || m.path_domain;

  const annotation = {
    original_domain: m.path_domain,
    correct_domain: correctDomain,
    title: m.title,
    date: m.date,
    annotated_at: new Date().toISOString(),
  };

  // Save locally
  annotations[m.rel_path] = annotation;

  // Persist to server
  await fetch("/api/annotate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rel_path: m.rel_path, annotation }),
  });

  // Auto-advance
  if (filterMode === "unannotated") {
    // Stay at same index (next unannotated slides in)
    renderMeeting();
  } else {
    if (currentIndex < filtered.length - 1) currentIndex++;
    renderMeeting();
  }
}

function navigate(delta) {
  const filtered = getFilteredIndices();
  const newIdx = currentIndex + delta;
  if (newIdx >= 0 && newIdx < filtered.length) {
    currentIndex = newIdx;
    renderMeeting();
  }
}

function setFilter(mode) {
  filterMode = mode;
  currentIndex = 0;
  document.getElementById("filterAll").classList.toggle("active", mode === "all");
  document.getElementById("filterUnannotated").classList.toggle("active", mode === "unannotated");
  document.getElementById("filterChanged").classList.toggle("active", mode === "changed");
  renderMeeting();
}

function escHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}

// Keyboard shortcuts
document.addEventListener("keydown", (e) => {
  // Don't capture if user is in an input/textarea
  if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;

  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    annotate(null);
  } else if (e.key === "ArrowLeft") {
    e.preventDefault();
    navigate(-1);
  } else if (e.key === "ArrowRight") {
    e.preventDefault();
    navigate(1);
  } else if (e.key === "f" || e.key === "F") {
    e.preventDefault();
    const newMode = filterMode === "unannotated" ? "all" : "unannotated";
    setFilter(newMode);
  } else if (e.key >= "1" && e.key <= "8") {
    e.preventDefault();
    const idx = parseInt(e.key) - 1;
    if (idx < DOMAINS.length) annotate(DOMAINS[idx]);
  }
});

init();
</script>
</body>
</html>"""


class AnnotationHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self._serve_html()
        elif self.path == "/api/meetings":
            self._serve_meetings()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/annotate":
            self._handle_annotate()
        else:
            self.send_error(404)

    def _serve_html(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode("utf-8"))

    def _serve_meetings(self):
        data = load_annotations()
        payload = {
            "meetings": ALL_MEETINGS,
            "annotations": data.get("annotations", {}),
        }
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def _handle_annotate(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        rel_path = body["rel_path"]
        annotation = body["annotation"]

        data = load_annotations()
        data["annotations"][rel_path] = annotation
        data["stats"]["total"] = len(ALL_MEETINGS)
        save_annotations(data)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))

    def log_message(self, format, *args):
        # Quieter logs — only show POST requests
        if "POST" in str(args):
            super().log_message(format, *args)


if __name__ == "__main__":
    server = HTTPServer(("", PORT), AnnotationHandler)
    print(f"\nAnnotation tool running at http://localhost:{PORT}")
    print(f"Annotations will be saved to {ANNOTATIONS_PATH}")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()
