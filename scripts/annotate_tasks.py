#!/usr/bin/env python3
"""
annotate_tasks.py — Lightweight annotation server for task queue/worker classification.

Two-phase annotation: queue assignment (1-4), then worker assignment (Q/W/E/R/T)
for agent/collab tasks. Serves on port 8751.

Usage:
    python3 scripts/annotate_tasks.py
    # Then open http://localhost:8751
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

PORT = 8751
TASKS_DIR = Path(__file__).resolve().parent.parent / "datasets" / "tasks"
ARCHIVE_DIR = TASKS_DIR / "_archive"
ANNOTATIONS_PATH = (
    Path(__file__).resolve().parent.parent
    / "datasets"
    / "evals"
    / "task-classifier"
    / "annotations.json"
)

VALID_QUEUES = ["human", "agent", "collab", "waiting"]
VALID_WORKERS = ["default", "product-analyst", "researcher", "scheduler", "ticket-creator"]


def _parse_frontmatter(text):
    """Extract YAML frontmatter as a dict."""
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^(\w[\w_]*)\s*:\s*'?\"?(.+?)'?\"?\s*$", line)
        if kv:
            key, val = kv.group(1), kv.group(2)
            if val in ("null", "~", ""):
                fm[key] = None
            elif val.startswith("["):
                try:
                    fm[key] = json.loads(val.replace("'", '"'))
                except json.JSONDecodeError:
                    fm[key] = val
            else:
                fm[key] = val
    return fm


def _extract_description(text, max_chars=400):
    """Extract the Description section content."""
    m = re.search(r"## Description\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not m:
        # Fall back to body after frontmatter
        fm_end = re.match(r"^---\n.*?\n---\n?", text, re.DOTALL)
        body = text[fm_end.end():] if fm_end else text
        return body.strip()[:max_chars]
    desc = m.group(1).strip()
    if len(desc) > max_chars:
        desc = desc[:max_chars].rsplit(" ", 1)[0] + "..."
    return desc


def scan_tasks():
    """Scan all task files (active + archive) and return metadata list."""
    tasks = []
    # Active queue directories
    for queue_dir in VALID_QUEUES:
        queue_path = TASKS_DIR / queue_dir
        if queue_path.is_dir():
            for f in queue_path.glob("TASK-*.md"):
                tasks.append((_read_task(f), f"active/{queue_dir}"))
    # Archive
    if ARCHIVE_DIR.is_dir():
        for f in sorted(ARCHIVE_DIR.rglob("TASK-*.md")):
            rel = f.relative_to(ARCHIVE_DIR)
            tasks.append((_read_task(f), f"archive/{rel.parent}"))

    # Filter out None (failed reads) and sort by task ID numerically
    tasks = [(t, src) for t, src in tasks if t is not None]
    tasks.sort(key=lambda x: int(re.search(r"(\d+)", x[0].get("task_id", "0")).group(1)))

    return [dict(**t, source=src) for t, src in tasks]


def _read_task(path):
    """Read a single task file and return metadata dict."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    fm = _parse_frontmatter(text)
    task_id = fm.get("id", path.stem)
    return {
        "task_id": task_id,
        "title": fm.get("title", ""),
        "current_queue": fm.get("queue", ""),
        "priority": fm.get("priority", ""),
        "domain": fm.get("domain") or "",
        "creator": fm.get("creator", ""),
        "task_type": fm.get("task_type") or "",
        "status": fm.get("status", ""),
        "description": _extract_description(text),
    }


def load_annotations():
    """Load existing annotations from disk."""
    if ANNOTATIONS_PATH.exists():
        return json.loads(ANNOTATIONS_PATH.read_text())
    return {
        "created": datetime.now(timezone.utc).isoformat(),
        "updated": datetime.now(timezone.utc).isoformat(),
        "stats": {"total": 0, "annotated": 0, "queue_changed": 0, "worker_assigned": 0},
        "annotations": {},
    }


def save_annotations(data):
    """Save annotations to disk."""
    ANNOTATIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["updated"] = datetime.now(timezone.utc).isoformat()
    annotations = data.get("annotations", {})
    data["stats"]["annotated"] = len(annotations)
    data["stats"]["queue_changed"] = sum(
        1 for a in annotations.values() if a.get("original_queue") != a.get("correct_queue")
    )
    data["stats"]["worker_assigned"] = sum(
        1 for a in annotations.values() if a.get("correct_worker")
    )
    ANNOTATIONS_PATH.write_text(json.dumps(data, indent=2))


# Pre-scan at startup
print(f"Scanning tasks in {TASKS_DIR}...")
ALL_TASKS = scan_tasks()
print(f"Found {len(ALL_TASKS)} tasks.")


HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Task Routing Annotation</title>
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
    --purple: #9b59b6;
    --orange: #e67e22;
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
  .progress-bar { width: 200px; height: 6px; background: #333; border-radius: 3px; overflow: hidden; }
  .progress-fill { height: 100%; background: var(--green); transition: width 0.3s; }
  .filter-controls { display: flex; gap: 8px; align-items: center; }
  .filter-controls button {
    padding: 4px 12px; border-radius: 4px; border: 1px solid #555;
    background: transparent; color: var(--text); cursor: pointer; font-size: 12px;
  }
  .filter-controls button.active { background: var(--blue); border-color: var(--blue); }

  .main { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 24px; }
  .card {
    background: var(--card-bg); border-radius: 8px; padding: 24px;
    max-width: 800px; width: 100%; border: 1px solid #333;
  }
  .card-title { font-size: 18px; font-weight: 600; margin-bottom: 8px; }
  .card-id { font-size: 13px; color: var(--text-dim); margin-bottom: 12px; }
  .card-meta { font-size: 13px; color: var(--text-dim); margin-bottom: 12px; display: flex; gap: 16px; flex-wrap: wrap; }
  .badge {
    display: inline-block; padding: 3px 8px; border-radius: 4px;
    font-size: 12px; font-weight: 600;
  }
  .badge-queue { background: var(--accent); border: 1px solid var(--blue); }
  .badge-priority-critical { background: rgba(231,76,60,0.2); color: var(--red); }
  .badge-priority-high { background: rgba(230,126,34,0.2); color: var(--orange); }
  .badge-priority-medium { background: rgba(52,152,219,0.2); color: var(--blue); }
  .badge-priority-low { background: rgba(136,136,170,0.2); color: var(--text-dim); }
  .badge-domain { background: rgba(155,89,182,0.2); color: var(--purple); }
  .badge-status { background: rgba(46,204,113,0.15); color: var(--green); }

  .description {
    background: #0d1117; border-radius: 4px; padding: 16px;
    font-size: 13px; line-height: 1.6; max-height: 200px;
    overflow-y: auto; white-space: pre-wrap; color: #ccc; margin-top: 12px;
  }
  .annotation-status {
    margin-top: 12px; padding: 8px 12px; border-radius: 4px;
    font-size: 13px; font-weight: 600;
  }
  .annotation-correct { background: rgba(46,204,113,0.15); color: var(--green); }
  .annotation-changed { background: rgba(241,196,15,0.15); color: var(--yellow); }

  .action-bar { max-width: 800px; width: 100%; margin-top: 16px; }
  .action-row { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-bottom: 8px; }
  .section-label { font-size: 12px; color: var(--text-dim); text-align: center; margin-bottom: 6px; margin-top: 8px; }
  .action-btn {
    padding: 8px 16px; border-radius: 6px; border: 1px solid #555;
    background: var(--card-bg); color: var(--text); cursor: pointer;
    font-size: 13px; transition: all 0.15s; min-width: 120px; text-align: left;
  }
  .action-btn:hover { border-color: var(--blue); background: var(--accent); }
  .action-btn .key {
    display: inline-block; width: 20px; height: 20px; line-height: 20px;
    text-align: center; background: #555; border-radius: 3px;
    font-size: 11px; margin-right: 6px; font-weight: 700;
  }
  .confirm-btn {
    padding: 10px 32px; border-radius: 6px; border: 2px solid var(--green);
    background: rgba(46,204,113,0.15); color: var(--green);
    cursor: pointer; font-size: 14px; font-weight: 600;
  }
  .confirm-btn:hover { background: rgba(46,204,113,0.3); }
  .hidden { display: none !important; }

  .nav-row {
    display: flex; justify-content: space-between; align-items: center;
    margin-top: 12px; max-width: 800px; width: 100%;
  }
  .nav-btn {
    padding: 6px 16px; border-radius: 4px; border: 1px solid #555;
    background: transparent; color: var(--text); cursor: pointer; font-size: 13px;
  }
  .nav-btn:hover { border-color: var(--blue); }
  .nav-btn:disabled { opacity: 0.3; cursor: default; }
  .legend {
    max-width: 800px; width: 100%; margin-top: 16px;
    font-size: 12px; color: var(--text-dim); text-align: center; line-height: 1.8;
  }
  .stats-bar {
    max-width: 800px; width: 100%; margin-top: 16px;
    display: flex; gap: 12px; justify-content: center; flex-wrap: wrap;
    font-size: 12px; color: var(--text-dim);
  }
  .stat { padding: 4px 8px; background: var(--card-bg); border-radius: 4px; }
  .stat-changed { color: var(--yellow); }
  .empty-state { text-align: center; padding: 48px; color: var(--text-dim); font-size: 16px; }
</style>
</head>
<body>

<div class="topbar">
  <h1>Task Routing Annotation</h1>
  <div style="display:flex; gap:16px; align-items:center;">
    <div class="filter-controls">
      <button id="filterAll" class="active" onclick="setFilter('all')">All</button>
      <button id="filterUnannotated" onclick="setFilter('unannotated')">Unannotated (F)</button>
      <button id="filterChanged" onclick="setFilter('changed')">Changed (G)</button>
    </div>
    <div>
      <span class="progress-info" id="progressText">0 / 0</span>
      <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
    </div>
  </div>
</div>

<div class="main">
  <div class="card" id="taskCard"><div id="cardContent"></div></div>

  <div class="action-bar" id="actionBar">
    <div class="section-label" id="queueLabel">Queue Assignment</div>
    <div class="action-row" id="queueButtons"></div>
    <div class="action-row"><button class="confirm-btn" onclick="confirmQueue()">Correct (Enter/Space)</button></div>

    <div id="workerSection" class="hidden">
      <div class="section-label">Worker Assignment (for agent/collab)</div>
      <div class="action-row" id="workerButtons"></div>
    </div>
  </div>

  <div class="nav-row">
    <button class="nav-btn" id="prevBtn" onclick="navigate(-1)">&larr; Back</button>
    <span id="positionText" style="font-size:13px; color:var(--text-dim);"></span>
    <button class="nav-btn" id="nextBtn" onclick="navigate(1)">Skip &rarr;</button>
  </div>

  <div class="legend">
    <b>Queue:</b> <b>1</b>=human <b>2</b>=agent <b>3</b>=collab <b>4</b>=waiting <b>Enter/Space</b>=Correct<br>
    <b>Worker:</b> <b>Q</b>=default <b>W</b>=product-analyst <b>E</b>=researcher <b>R</b>=scheduler <b>T</b>=ticket-creator<br>
    <b>Nav:</b> <b>&larr;/&rarr;</b>=Navigate <b>F</b>=Unannotated <b>G</b>=Changed
  </div>

  <div class="stats-bar" id="statsBar"></div>
</div>

<script>
const QUEUES = ["human", "agent", "collab", "waiting"];
const WORKERS = ["default", "product-analyst", "researcher", "scheduler", "ticket-creator"];
const WORKER_KEYS = ["Q", "W", "E", "R", "T"];

let tasks = [];
let annotations = {};
let currentIndex = 0;
let filterMode = "all";
let phase = "queue"; // "queue" or "worker"
let pendingQueue = null;

async function init() {
  const resp = await fetch("/api/tasks");
  const data = await resp.json();
  tasks = data.tasks;
  annotations = data.annotations || {};
  renderQueueButtons();
  renderWorkerButtons();
  renderTask();
}

function getFilteredIndices() {
  const indices = [];
  for (let i = 0; i < tasks.length; i++) {
    const t = tasks[i];
    const ann = annotations[t.task_id];
    if (filterMode === "unannotated" && ann) continue;
    if (filterMode === "changed" && (!ann || ann.original_queue === ann.correct_queue)) continue;
    indices.push(i);
  }
  return indices;
}

function renderQueueButtons() {
  document.getElementById("queueButtons").innerHTML = QUEUES.map((q, i) =>
    `<button class="action-btn" onclick="setQueue('${q}')"><span class="key">${i+1}</span>${q}</button>`
  ).join("");
}

function renderWorkerButtons() {
  document.getElementById("workerButtons").innerHTML = WORKERS.map((w, i) =>
    `<button class="action-btn" onclick="setWorker('${w}')"><span class="key">${WORKER_KEYS[i]}</span>${w}</button>`
  ).join("");
}

function renderTask() {
  const filtered = getFilteredIndices();
  const content = document.getElementById("cardContent");

  if (filtered.length === 0) {
    content.innerHTML = '<div class="empty-state">No tasks match the current filter.</div>';
    document.getElementById("actionBar").style.display = "none";
    updateProgress();
    return;
  }
  document.getElementById("actionBar").style.display = "";

  if (currentIndex < 0) currentIndex = 0;
  if (currentIndex >= filtered.length) currentIndex = filtered.length - 1;

  const realIdx = filtered[currentIndex];
  const t = tasks[realIdx];
  const ann = annotations[t.task_id];

  // Reset to queue phase
  phase = "queue";
  pendingQueue = null;
  document.getElementById("workerSection").classList.add("hidden");
  document.getElementById("queueLabel").textContent = "Queue Assignment";

  let annotationHtml = "";
  if (ann) {
    if (ann.original_queue === ann.correct_queue) {
      let workerNote = ann.correct_worker ? ` | worker: ${ann.correct_worker}` : "";
      annotationHtml = `<div class="annotation-status annotation-correct">&#10003; Queue confirmed: ${ann.correct_queue}${workerNote}</div>`;
    } else {
      let workerNote = ann.correct_worker ? ` | worker: ${ann.correct_worker}` : "";
      annotationHtml = `<div class="annotation-status annotation-changed">&#8594; Queue: ${ann.original_queue} &rarr; ${ann.correct_queue}${workerNote}</div>`;
    }
  }

  const priorityClass = t.priority ? `badge-priority-${t.priority}` : "";

  content.innerHTML = `
    <div class="card-id">${t.task_id} &nbsp;|&nbsp; ${t.source} &nbsp;|&nbsp; ${t.status}</div>
    <div class="card-title">${escHtml(t.title)}</div>
    <div class="card-meta">
      <span class="badge badge-queue">${t.current_queue}</span>
      ${t.priority ? `<span class="badge ${priorityClass}">${t.priority}</span>` : ""}
      ${t.domain ? `<span class="badge badge-domain">${t.domain}</span>` : ""}
      ${t.creator ? `<span>creator: ${t.creator}</span>` : ""}
      ${t.task_type ? `<span>type: ${t.task_type}</span>` : ""}
    </div>
    ${annotationHtml}
    ${t.description ? `<div class="description">${escHtml(t.description)}</div>` : ""}
  `;

  document.getElementById("positionText").textContent =
    `${currentIndex + 1} of ${filtered.length}` + (filterMode !== "all" ? ` (${filterMode})` : "");
  document.getElementById("prevBtn").disabled = currentIndex <= 0;
  document.getElementById("nextBtn").disabled = currentIndex >= filtered.length - 1;

  updateProgress();
  updateStats();
}

function updateProgress() {
  const total = tasks.length;
  const annotated = Object.keys(annotations).length;
  document.getElementById("progressText").textContent = `${annotated} / ${total} annotated`;
  document.getElementById("progressFill").style.width = total > 0 ? `${(annotated / total) * 100}%` : "0%";
}

function updateStats() {
  const counts = {};
  QUEUES.forEach(q => counts[q] = { total: 0, annotated: 0, changed: 0 });
  tasks.forEach(t => {
    if (counts[t.current_queue]) counts[t.current_queue].total++;
    const ann = annotations[t.task_id];
    if (ann) {
      if (counts[t.current_queue]) counts[t.current_queue].annotated++;
      if (ann.original_queue !== ann.correct_queue) {
        if (counts[t.current_queue]) counts[t.current_queue].changed++;
      }
    }
  });
  document.getElementById("statsBar").innerHTML = QUEUES.map(q => {
    const c = counts[q];
    const ch = c.changed > 0 ? ` <span class="stat-changed">(${c.changed} changed)</span>` : "";
    return `<span class="stat">${q}: ${c.annotated}/${c.total}${ch}</span>`;
  }).join("");
}

function confirmQueue() {
  const filtered = getFilteredIndices();
  if (filtered.length === 0) return;
  const t = tasks[filtered[currentIndex]];
  setQueue(t.current_queue);
}

function setQueue(queue) {
  const filtered = getFilteredIndices();
  if (filtered.length === 0) return;
  const t = tasks[filtered[currentIndex]];
  pendingQueue = queue;

  if (queue === "agent" || queue === "collab") {
    // Show worker phase
    phase = "worker";
    document.getElementById("workerSection").classList.remove("hidden");
    document.getElementById("queueLabel").textContent = `Queue: ${queue} — now pick worker:`;
  } else {
    // Save immediately for human/waiting (no worker needed)
    saveAnnotation(t.task_id, queue, null);
  }
}

function setWorker(worker) {
  const filtered = getFilteredIndices();
  if (filtered.length === 0 || !pendingQueue) return;
  const t = tasks[filtered[currentIndex]];
  saveAnnotation(t.task_id, pendingQueue, worker);
}

async function saveAnnotation(taskId, queue, worker) {
  const filtered = getFilteredIndices();
  const t = tasks[filtered[currentIndex]];

  const annotation = {
    original_queue: t.current_queue,
    correct_queue: queue,
    correct_worker: worker,
    title: t.title,
    domain: t.domain,
    task_type: t.task_type || null,
    annotated_at: new Date().toISOString(),
  };

  annotations[taskId] = annotation;

  await fetch("/api/annotate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task_id: taskId, annotation }),
  });

  // Auto-advance
  if (filterMode === "unannotated") {
    renderTask();
  } else {
    if (currentIndex < filtered.length - 1) currentIndex++;
    renderTask();
  }
}

function navigate(delta) {
  const filtered = getFilteredIndices();
  const newIdx = currentIndex + delta;
  if (newIdx >= 0 && newIdx < filtered.length) {
    currentIndex = newIdx;
    renderTask();
  }
}

function setFilter(mode) {
  filterMode = mode;
  currentIndex = 0;
  document.getElementById("filterAll").classList.toggle("active", mode === "all");
  document.getElementById("filterUnannotated").classList.toggle("active", mode === "unannotated");
  document.getElementById("filterChanged").classList.toggle("active", mode === "changed");
  renderTask();
}

function escHtml(s) {
  const div = document.createElement("div");
  div.textContent = s || "";
  return div.innerHTML;
}

document.addEventListener("keydown", (e) => {
  if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;

  if (phase === "queue") {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); confirmQueue(); }
    else if (e.key === "1") { e.preventDefault(); setQueue("human"); }
    else if (e.key === "2") { e.preventDefault(); setQueue("agent"); }
    else if (e.key === "3") { e.preventDefault(); setQueue("collab"); }
    else if (e.key === "4") { e.preventDefault(); setQueue("waiting"); }
    else if (e.key === "ArrowLeft") { e.preventDefault(); navigate(-1); }
    else if (e.key === "ArrowRight") { e.preventDefault(); navigate(1); }
    else if (e.key === "f" || e.key === "F") { e.preventDefault(); setFilter(filterMode === "unannotated" ? "all" : "unannotated"); }
    else if (e.key === "g" || e.key === "G") { e.preventDefault(); setFilter(filterMode === "changed" ? "all" : "changed"); }
  } else if (phase === "worker") {
    if (e.key === "q" || e.key === "Q") { e.preventDefault(); setWorker("default"); }
    else if (e.key === "w" || e.key === "W") { e.preventDefault(); setWorker("product-analyst"); }
    else if (e.key === "e" || e.key === "E") { e.preventDefault(); setWorker("researcher"); }
    else if (e.key === "r" || e.key === "R") { e.preventDefault(); setWorker("scheduler"); }
    else if (e.key === "t" || e.key === "T") { e.preventDefault(); setWorker("ticket-creator"); }
    else if (e.key === "Escape") { e.preventDefault(); phase = "queue"; pendingQueue = null; document.getElementById("workerSection").classList.add("hidden"); document.getElementById("queueLabel").textContent = "Queue Assignment"; }
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
        elif self.path == "/api/tasks":
            self._serve_tasks()
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

    def _serve_tasks(self):
        data = load_annotations()
        payload = {"tasks": ALL_TASKS, "annotations": data.get("annotations", {})}
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def _handle_annotate(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        task_id = body["task_id"]
        annotation = body["annotation"]

        data = load_annotations()
        data["annotations"][task_id] = annotation
        data["stats"]["total"] = len(ALL_TASKS)
        save_annotations(data)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))

    def log_message(self, format, *args):
        if "POST" in str(args):
            super().log_message(format, *args)


if __name__ == "__main__":
    server = HTTPServer(("", PORT), AnnotationHandler)
    print(f"\nTask annotation tool running at http://localhost:{PORT}")
    print(f"Annotations saved to {ANNOTATIONS_PATH}")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()
