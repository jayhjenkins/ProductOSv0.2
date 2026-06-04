#!/usr/bin/env python3
"""
eval_digest.py — Deterministic LangFuse negative-signal pull for the weekly
feedback-loop improvement pass (ROADMAP §1 / cron #5).

Reads human annotations (thumbs-down + free-text) that have landed on LangFuse
traces, joins each to its originating PM-OS task, clusters by pipeline step and
by worker, and writes structured raw material for the eval-analyst worker to
turn into recommendations. No LLM here — this is the deterministic data layer.

Scores read (written by task_server.py):
    human-feedback   NUMERIC      1 = 👍, 0 = 👎
    human-annotation CATEGORICAL  category + free-text comment

Reads go through the LangFuse REST API directly. The Python SDK's read surface
changed across v3/v4 (attribute is `scores` vs `score`, etc.) and is unreliable;
the REST API is stable across versions — same approach langfuse_client.py takes
for writes. Driving off the /scores endpoint (which returns each score's
traceId) is also far cheaper than walking every trace.

Usage:
    python3 scripts/eval_digest.py                  # last 7 days
    python3 scripts/eval_digest.py --days 14
    python3 scripts/eval_digest.py --all            # full history (backfill)
    python3 scripts/eval_digest.py --out datasets/evals/feedback-loop/2026-06-05/

Outputs (to --out, default datasets/evals/feedback-loop/{date}[-backfill]/):
    digest.json   structured, for the agent
    digest.md     human-readable

Exit 0 even when LangFuse is unavailable (writes a stub report) — safe under
headless cron dispatch.
"""

import argparse
import base64
import json
import os
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
TASKS_DIR = PROJECT_DIR / "datasets" / "tasks"
FEEDBACK_DIR = PROJECT_DIR / "datasets" / "evals" / "feedback-loop"
ENV_FILE = PROJECT_DIR / ".env.langfuse"

PAGE_LIMIT = 100
MAX_PAGES = 200  # safety cap: PAGE_LIMIT * MAX_PAGES scores


# ── Env / REST ────────────────────────────────────────────────────────────────

def load_env():
    """Load .env.langfuse into os.environ (export KEY=VALUE or KEY=VALUE)."""
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        line = line.removeprefix("export ")
        key, _, val = line.partition("=")
        val = val.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), val)


def _auth_header():
    pk = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
    sk = os.environ.get("LANGFUSE_SECRET_KEY", "")
    if not sk:
        return None
    return "Basic " + base64.b64encode(f"{pk}:{sk}".encode()).decode()


def rest_get(path, params=None):
    """GET the LangFuse public REST API. Returns parsed JSON or None."""
    auth = _auth_header()
    if auth is None:
        return None
    host = os.environ.get("LANGFUSE_HOST", "http://localhost:3000")
    url = f"{host}/api/public{path}"
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    req = urllib.request.Request(url, headers={"Authorization": auth}, method="GET")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ── Fetch ─────────────────────────────────────────────────────────────────────

def fetch_scores(from_ts=None):
    """Page through /scores newest-first. Returns list of score dicts.

    Each: {name, value, comment, traceId, timestamp, dataType}.
    from_ts: ISO string to filter by score timestamp, or None for all history.
    """
    scores = []
    first = rest_get("/scores", {"limit": PAGE_LIMIT, "page": 1, "fromTimestamp": from_ts})
    if first is None:
        return None  # signals unavailable
    total_pages = first.get("meta", {}).get("totalPages", 1)
    scores.extend(first.get("data", []))
    for page in range(2, min(total_pages, MAX_PAGES) + 1):
        batch = rest_get("/scores", {"limit": PAGE_LIMIT, "page": page, "fromTimestamp": from_ts})
        if not batch:
            break
        scores.extend(batch.get("data", []))
    return scores


_TRACE_CACHE = {}


def fetch_trace(trace_id):
    """GET a single trace; cached. Returns dict or None."""
    if not trace_id:
        return None
    if trace_id in _TRACE_CACHE:
        return _TRACE_CACHE[trace_id]
    try:
        t = rest_get(f"/traces/{urllib.parse.quote(trace_id)}")
    except Exception:
        t = None
    _TRACE_CACHE[trace_id] = t
    return t


# ── Task join ─────────────────────────────────────────────────────────────────

_TASK_INDEX = None


def find_task(task_id):
    """Locate a task file by id under datasets/tasks/** and pull light metadata."""
    global _TASK_INDEX
    if not task_id:
        return None
    if _TASK_INDEX is None:
        _TASK_INDEX = {p.stem: p for p in TASKS_DIR.glob("**/*.md")}
    path = _TASK_INDEX.get(task_id)
    if not path:
        return None
    title = queue = domain = tags = ""
    try:
        text = path.read_text(errors="replace")
        if text.startswith("---"):
            fm = text.split("---", 2)[1]
            for line in fm.splitlines():
                k, _, v = line.partition(":")
                k = k.strip().lower()
                v = v.strip().strip('"').strip("'")
                if k == "title":
                    title = v
                elif k == "queue":
                    queue = v
                elif k == "domain":
                    domain = v
                elif k == "tags":
                    tags = v
    except Exception:
        pass
    return {"task_id": task_id, "title": title, "queue": queue,
            "domain": domain, "tags": tags,
            "path": str(path.relative_to(PROJECT_DIR))}


# ── Signal logic ──────────────────────────────────────────────────────────────

def is_negative(score):
    """thumbs-down, or any human-annotation (annotations are signal by definition)."""
    name = (score.get("name") or "").lower()
    val = score.get("value")
    if name == "human-feedback":
        try:
            return float(val) == 0.0
        except (TypeError, ValueError):
            return False
    if name == "human-annotation":
        return True
    return False


def summarize(data, limit=240):
    if data is None:
        return ""
    if isinstance(data, (dict, list)):
        return json.dumps(data, default=str)[:limit]
    return str(data)[:limit]


# ── Output ────────────────────────────────────────────────────────────────────

def write_stub(out_dir, reason, window_label):
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window": window_label,
        "status": "no-data",
        "reason": reason,
        "totals": {"negative_scores": 0, "flagged_traces": 0},
        "by_step": {}, "by_worker": {}, "flagged": [],
    }
    (out_dir / "digest.json").write_text(json.dumps(payload, indent=2))
    (out_dir / "digest.md").write_text(
        f"# Feedback-loop digest — {window_label}\n\n"
        f"**Status:** no data — {reason}\n\nGenerated {payload['generated']}.\n")
    print(f"[eval_digest] {reason} — wrote stub to {out_dir}")


def _write_markdown(path, payload):
    lines = [f"# Feedback-loop digest — {payload['window']}", ""]
    t = payload["totals"]
    lines.append(f"Generated {payload['generated']}. Status: **{payload['status']}**.")
    lines += ["",
              f"- Negative scores: **{t['negative_scores']}**",
              f"- Flagged traces: **{t['flagged_traces']}**", ""]
    if payload["status"] == "clean":
        lines.append("No negative signal in this window. Clean week.")
        path.write_text("\n".join(lines) + "\n")
        return

    lines += ["## By step", "", "| Step | Flagged | Sample comments |", "|---|---|---|"]
    for step, d in sorted(payload["by_step"].items(), key=lambda kv: -kv[1]["flagged"]):
        sample = "; ".join(c.replace("|", "/").replace("\n", " ") for c in d["comments"][:3])
        lines.append(f"| {step} | {d['flagged']} | {sample} |")
    lines.append("")

    if payload.get("by_worker"):
        lines += ["## By worker / task-type", "", "| Group | Flagged |", "|---|---|"]
        for g, d in sorted(payload["by_worker"].items(), key=lambda kv: -kv[1]["flagged"]):
            lines.append(f"| {g} | {d['flagged']} |")
        lines.append("")

    lines += ["## Flagged traces", ""]
    for r in payload["flagged"]:
        task = r.get("task") or {}
        title = task.get("title", "") if task else ""
        lines.append(f"### `{r['step']}` — {title or r.get('session_id') or r['trace_id']}")
        lines.append(f"- trace: `{r['trace_id']}` · task: `{r.get('session_id') or '—'}`"
                     f" · domain: {task.get('domain','—') if task else '—'} · {r['timestamp']}")
        for s in r["negative_scores"]:
            c = (s.get("comment") or "").strip()
            lines.append(f"- **{s['name']}** = {s['value']}" + (f" — \"{c}\"" if c else ""))
        if r.get("output_summary"):
            lines.append(f"- output: {r['output_summary']}")
        lines.append("")
    path.write_text("\n".join(lines) + "\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="LangFuse negative-signal digest")
    ap.add_argument("--days", type=int, default=7, help="lookback window in days (default 7)")
    ap.add_argument("--all", action="store_true", help="full history (ignore --days)")
    ap.add_argument("--out", default=None,
                    help="output dir (default datasets/evals/feedback-loop/{date}[-backfill])")
    args = ap.parse_args()

    load_env()
    now = datetime.now(timezone.utc)
    date_slug = now.strftime("%Y-%m-%d")

    if args.all:
        from_ts = None
        window_label = "all history"
        default_out = FEEDBACK_DIR / f"{date_slug}-backfill"
    else:
        cutoff = now - timedelta(days=args.days)
        from_ts = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
        window_label = f"last {args.days} days (since {cutoff.strftime('%Y-%m-%d')})"
        default_out = FEEDBACK_DIR / date_slug

    out_dir = Path(args.out) if args.out else default_out
    if not out_dir.is_absolute():
        out_dir = PROJECT_DIR / out_dir

    if _auth_header() is None:
        write_stub(out_dir, "LANGFUSE_SECRET_KEY not set", window_label)
        return 0

    try:
        scores = fetch_scores(from_ts)
    except Exception as e:
        write_stub(out_dir, f"LangFuse unreachable: {e}", window_label)
        return 0
    if scores is None:
        write_stub(out_dir, "LangFuse unreachable", window_label)
        return 0

    # Group negative scores by trace
    neg_by_trace = defaultdict(list)
    for s in scores:
        if is_negative(s):
            neg_by_trace[s.get("traceId")].append({
                "name": s.get("name"), "value": s.get("value"),
                "comment": s.get("comment") or "", "data_type": s.get("dataType"),
                "timestamp": s.get("timestamp"),
            })

    flagged = []
    negative_scores = 0
    by_step = defaultdict(lambda: {"flagged": 0, "comments": []})
    by_worker = defaultdict(lambda: {"flagged": 0})

    for trace_id, neg in neg_by_trace.items():
        if not trace_id:
            continue
        negative_scores += len(neg)
        t = fetch_trace(trace_id) or {}
        step = t.get("name") or "unknown"
        session_id = t.get("sessionId")
        task = find_task(session_id)
        metadata = t.get("metadata") or {}
        worker = ""
        if isinstance(metadata, dict):
            worker = metadata.get("worker") or metadata.get("worker_name") or ""

        flagged.append({
            "trace_id": trace_id,
            "step": step,
            "session_id": session_id,
            "task": task,
            "worker": worker,
            "timestamp": t.get("timestamp", ""),
            "level": t.get("level", "DEFAULT"),
            "input_summary": summarize(t.get("input")),
            "output_summary": summarize(t.get("output")),
            "negative_scores": neg,
        })
        by_step[step]["flagged"] += 1
        for s in neg:
            c = (s.get("comment") or "").strip()
            if c:
                by_step[step]["comments"].append(c)
        group = worker or (task["domain"] if task and task.get("domain") else "") or step
        by_worker[group]["flagged"] += 1

    flagged.sort(key=lambda r: r["timestamp"], reverse=True)

    payload = {
        "generated": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window": window_label,
        "status": "ok" if flagged else "clean",
        "totals": {"negative_scores": negative_scores, "flagged_traces": len(flagged)},
        "by_step": dict(by_step),
        "by_worker": dict(by_worker),
        "flagged": flagged,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "digest.json").write_text(json.dumps(payload, indent=2, default=str))
    _write_markdown(out_dir / "digest.md", payload)

    print(f"[eval_digest] window={window_label}")
    print(f"[eval_digest] scanned {len(scores)} scores, "
          f"flagged {len(flagged)} traces with {negative_scores} negative scores")
    if by_step:
        print("[eval_digest] by step:")
        for step, d in sorted(by_step.items(), key=lambda kv: -kv[1]["flagged"]):
            print(f"    {step}: {d['flagged']}")
    print(f"[eval_digest] wrote {out_dir}/digest.json + digest.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
