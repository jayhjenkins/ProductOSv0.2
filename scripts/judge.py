#!/usr/bin/env python3
"""
judge.py — PM-OS shadow judge v1 (observe-only).

Scores a completed agent task's output artifact and writes the verdict back to
the task plus a LangFuse score on the task's worker-execution trace. This is the
"shadow" phase from UX_VISION.md: the judge observes and records, it does NOT yet
route attention, reorder Review, or gate anything. It exists to build the
judge↔human agreement dataset before the system trusts it to triage.

The verdict is (score, per-dimension breakdown, rationale) with dimensions that
mirror the pipeline stages — context / reasoning / evidence / format — so a low
score localizes which stage failed (the GEPA credit-assignment note in the
vision). The rationale is a single substantive paragraph: it helps human↔judge
alignment now and is the textual feedback string a future optimizer consumes.

Model: Claude headless (Opus), like the rest of the dispatch system. No MCP — the
judge reads the task + artifact locally and emits structured JSON.

Usage:
    python3 scripts/judge.py --task TASK-NNNN

Spawned detached by task_cli.cmd_agent_complete after an agent reports done with
an --output artifact. Designed to be strictly additive: every failure path logs
and exits 0, never raising into the caller and never blocking completion.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PM_OS_DIR = os.path.dirname(SCRIPT_DIR)
LOG_DIR = os.path.join(PM_OS_DIR, "logs")
ENV_FILE = os.path.join(PM_OS_DIR, ".env.langfuse")
VOICE_FILE = os.path.join(PM_OS_DIR, "datasets", "reference", "jay-voice.md")

sys.path.insert(0, SCRIPT_DIR)
import task_lib  # noqa: E402

JUDGE_MODEL = "claude-opus-4-8"
ARTIFACT_CHAR_LIMIT = 16000
LOG_TAIL_CHAR_LIMIT = 3000
CLAUDE_TIMEOUT = 240  # seconds

# ── Rubrics ─────────────────────────────────────────────────────────────────
# One rubric per deliverable FORM, so the judge grades the meat of the ask by the
# standard that fits it: a document by document standards, a message by message
# standards, a meeting by meeting standards. Each is the inline fallback for a
# LangFuse prompt of the matching name (registered in scripts/langfuse_setup.py);
# judge.py prefers the LangFuse version and falls back to these when it's down.
#
# Only the document rubric asks for the four pipeline dimensions; message and
# meeting return score + why (the fitted paragraph carries the reasoning).

DEFAULT_RUBRIC_DOCUMENT = """You are the PM-OS shadow judge. You score the OUTPUT DOCUMENT a worker agent \
produced for a product-management task, judging how well it answers the task it was given.

Score on a 1-10 integer scale across four dimensions that mirror the work's pipeline stages, \
so a weak score points at the stage that failed:
- context   — did it gather and use the right inputs (the task ask, source material, prior decisions)?
- reasoning — is the thinking sound, decisive, and free of hand-waving or contradiction?
- evidence  — are claims grounded in specifics (quotes, data, citations) rather than assertion?
- format    — is it structured, scannable, and fit for its artifact type (PRD, research, memo, etc.)?

Then give an overall score (1-10) reflecting whether you, as a demanding PM lead, would let this \
document move forward as-is.

Calibration anchors: 9-10 = ship-ready, would forward untouched. 7-8 = solid, minor edits. \
5-6 = usable draft with real gaps. 3-4 = significant rework needed. 1-2 = off-target or empty.

Write the rationale as ONE substantive paragraph (3-5 sentences): name the weakest and strongest \
dimension, point to a concrete spot in the document, and say what would raise the score. Be specific \
and measured — no superlatives, no filler.

Return ONLY a single JSON object, no prose around it, no markdown fences:
{"score": <1-10 int>, "dimensions": {"context": <1-10>, "reasoning": <1-10>, "evidence": <1-10>, \
"format": <1-10>}, "why": "<one paragraph>"}"""


DEFAULT_RUBRIC_MESSAGE = """You are the PM-OS shadow judge. You score a DRAFTED MESSAGE a worker agent \
prepared for Jay to send, judging whether Jay could send it as-is. A draft usually contains BOTH a \
Teams / short version AND an email version — judge both.

A JAY'S VOICE GUIDE is provided below the task. Use it as the standard for the `voice` and `format` \
dimensions — the message should sound like Jay and follow his channel conventions, not generic "good writing".

Score on a 1-10 integer scale across four dimensions:
- voice       — does it sound like Jay per the voice guide (direct, plain, warm-but-efficient, no em dashes, \
his asks and rhythm)? Both the Teams and email versions.
- format      — channel-fit per the guide: the Teams version tight, low-caps, minimal greeting/sign-off; the \
email version subject + greeting + close, 1-3 sentence paragraphs, skimmable. Name the weaker channel.
- fulfils_ask — does it make the actual request the task asked, to the right recipient, framed for them?
- clarity     — clear, self-contained, sendable; no placeholders, loose ends, or buried ask.

Do NOT penalize a message for lacking citations, footnotes, or verbatim source quotes — it is a message, \
not a document. Judge it as something Jay will actually send.

Then give an overall score (1-10) for whether Jay could send it with at most a quick glance. \
Calibration: 9-10 = send as-is. 7-8 = send after a small tweak. 5-6 = usable but needs real edits. \
3-4 = significant rework. 1-2 = off-target.

Write the rationale as ONE substantive paragraph (3-5 sentences): name the weakest and strongest \
dimension, call out which channel version is weaker if they differ, and say what would make it sendable. \
Specific and measured — no superlatives, no filler.

Return ONLY a single JSON object, no prose around it, no markdown fences:
{"score": <1-10 int>, "dimensions": {"voice": <1-10>, "format": <1-10>, "fulfils_ask": <1-10>, \
"clarity": <1-10>}, "why": "<one paragraph>"}"""


DEFAULT_RUBRIC_MEETING = """You are the PM-OS shadow judge. You score a SCHEDULED MEETING a worker agent \
booked, judging whether it matches what the task asked.

You are given the meeting's recorded details (attendees, title, description, chosen time slot, duration, \
recurrence) and the original ask. Judge the booked meeting against the ask. Score 1-10 as a demanding \
chief of staff. Weigh:
- right invitees — do the attendees match who the ask names or clearly implies (no one wrongly added or omitted)?
- correct details — do the title and description/agenda reflect the purpose of the ask?
- sane timing — are the chosen time and duration reasonable for this kind of meeting?
- matches the ask — recurrence and any specifics line up with what was requested.

Calibration: 9-10 = exactly right. 7-8 = right, minor nit. 5-6 = roughly right with a real gap (wrong \
duration, thin agenda). 3-4 = wrong people or wrong purpose. 1-2 = off-target or not actually scheduled.

Write the rationale as ONE substantive paragraph (3-5 sentences): whether the right people, time, and \
purpose were captured, the weakest point, and what would make it right. Specific and measured.

Return ONLY a single JSON object, no prose around it, no markdown fences:
{"score": <1-10 int>, "why": "<one paragraph>"}"""


# deliverable kind → (LangFuse prompt name, inline fallback)
RUBRICS = {
    "document": ("judge-rubric-document", DEFAULT_RUBRIC_DOCUMENT),
    "message": ("judge-rubric-message", DEFAULT_RUBRIC_MESSAGE),
    "meeting": ("judge-rubric-meeting", DEFAULT_RUBRIC_MEETING),
}

# Per-kind dimension keys the verdict carries (meeting = none; paragraph only).
DIMENSIONS_BY_KIND = {
    "document": ["context", "reasoning", "evidence", "format"],
    "message": ["voice", "format", "fulfils_ask", "clarity"],
    "meeting": [],
}

# Back-compat alias (langfuse_setup imported DEFAULT_RUBRIC for the v1 prompt).
DEFAULT_RUBRIC = DEFAULT_RUBRIC_DOCUMENT

# Minimal inline fallback if the voice file and LangFuse are both unavailable.
DEFAULT_VOICE = (
    "Jay's voice: direct, plain, warm but efficient. No em dashes. Lead with the ask. "
    "Teams = tight, low caps, minimal greeting/sign-off. Email = subject + greeting + close, "
    "1-3 sentence paragraphs, ask up front."
)


# ── Helpers ─────────────────────────────────────────────────────────────────

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[judge {ts}] {msg}", file=sys.stderr, flush=True)


def load_env():
    """Load .env.langfuse into os.environ (export KEY=VALUE or KEY=VALUE)."""
    if not os.path.exists(ENV_FILE):
        return
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            line = line[len("export "):] if line.startswith("export ") else line
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def read_artifact(output_path):
    """Read the output artifact relative to PM_OS_DIR. Returns (text, abspath)."""
    if not output_path:
        return None, None
    candidate = output_path if os.path.isabs(output_path) else os.path.join(PM_OS_DIR, output_path)
    if not os.path.isfile(candidate):
        return None, candidate
    try:
        with open(candidate, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return None, candidate
    if len(text) > ARTIFACT_CHAR_LIMIT:
        text = text[:ARTIFACT_CHAR_LIMIT] + "\n…[truncated]"
    return text, candidate


def read_log_tail(task_id):
    """Read the tail of the dispatch log as the available execution 'trace'."""
    path = os.path.join(LOG_DIR, f"dispatch-{task_id}.log")
    if not os.path.isfile(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()[-LOG_TAIL_CHAR_LIMIT:]
    except OSError:
        return ""


def fetch_rubric(kind):
    """Return (rubric_text, version_label) for a deliverable kind.

    Prefer the LangFuse prompt for that kind; for documents also try the legacy
    `judge-rubric` name; fall back to the inline default.
    """
    name, default = RUBRICS[kind]
    candidates = [name] + (["judge-rubric"] if kind == "document" else [])
    try:
        from langfuse_client import fetch_prompt
        for nm in candidates:
            p = fetch_prompt(nm)
            if p is not None:
                text = p.prompt if hasattr(p, "prompt") else None
                version = getattr(p, "version", None)
                if text:
                    return text, f"langfuse:{nm}:v{version}" if version else f"langfuse:{nm}"
    except Exception as e:
        log(f"rubric fetch from LangFuse failed ({e}); using inline default")
    return default, f"inline:{kind}"


def fetch_voice():
    """Return (voice_text, source_label) for Jay's voice guide.

    Prefer the LangFuse prompt (`judge-voice-jay`); fall back to reading the
    on-disk source of truth; final fallback is a minimal inline default.
    """
    try:
        from langfuse_client import fetch_prompt
        p = fetch_prompt("judge-voice-jay")
        if p is not None:
            text = p.prompt if hasattr(p, "prompt") else None
            version = getattr(p, "version", None)
            if text:
                return text, f"langfuse:judge-voice-jay:v{version}" if version else "langfuse:judge-voice-jay"
    except Exception as e:
        log(f"voice fetch from LangFuse failed ({e}); falling back to file")
    try:
        if os.path.isfile(VOICE_FILE):
            with open(VOICE_FILE, "r", encoding="utf-8", errors="replace") as f:
                return f.read(), "file:jay-voice.md"
    except OSError:
        pass
    return DEFAULT_VOICE, "inline"


def detect_kind(fm):
    """Classify the deliverable form. Returns 'meeting' | 'message' | 'document' | None.

    None means there is no single deliverable to grade (skip) — e.g. a meeting
    task that hasn't been scheduled yet, or an action that left only a prose note.
    """
    task_type = fm.get("task_type")
    if task_type == "schedule-meeting":
        if fm.get("meeting_selected_slot") or fm.get("meeting_event_id"):
            return "meeting"
        return None  # nothing scheduled yet → nothing done to judge
    if task_type == "send-message":
        return "message"
    # Default: a document deliverable iff agent_output points to a readable file.
    artifact, _ = read_artifact(fm.get("agent_output"))
    if artifact is not None:
        return "document"
    return None


def _meeting_activity_line(body):
    """Pull the 'Calendar event created…' line from the activity log, if present."""
    for line in body.splitlines():
        if "calendar event created" in line.lower():
            return line.strip()
    return ""


def gather_evidence(kind, fm, body, task_id):
    """Return (evidence_text, log_note) for the deliverable, or (None, reason) to skip."""
    if kind == "document":
        artifact, abspath = read_artifact(fm.get("agent_output"))
        if artifact is None:
            return None, f"document not readable at {abspath}"
        return artifact, f"document {len(artifact)} chars"

    if kind == "message":
        # The drafted message is usually a file at agent_output; else fall back
        # to the task body (rare).
        artifact, _ = read_artifact(fm.get("agent_output"))
        if artifact:
            return artifact, f"message {len(artifact)} chars"
        if body.strip():
            return body.strip(), "message from task body"
        return None, "no message text found"

    if kind == "meeting":
        fields = [
            ("Title", fm.get("meeting_title") or fm.get("title")),
            ("Attendees", ", ".join(fm.get("meeting_attendees") or []) or "(none recorded)"),
            ("Chosen slot", fm.get("meeting_selected_slot") or "(none)"),
            ("Duration (min)", fm.get("meeting_duration")),
            ("Recurrence", fm.get("meeting_recurrence_pattern") or ("recurring" if fm.get("meeting_recurring") else "one-time")),
            ("Description / agenda", (fm.get("meeting_description") or "").strip() or "(none)"),
        ]
        block = "\n".join(f"- {k}: {v}" for k, v in fields)
        act = _meeting_activity_line(body)
        if act:
            block += f"\n- Activity log: {act}"
        return block, "meeting fields"

    return None, "unknown kind"


KIND_EVIDENCE_LABEL = {
    "document": "OUTPUT DOCUMENT (score this)",
    "message": "DRAFTED MESSAGE (score this)",
    "meeting": "SCHEDULED MEETING (score this)",
}


def build_prompt(kind, rubric, task_fm, body, evidence, log_tail, voice=None):
    title = task_fm.get("title", "")
    domain = task_fm.get("domain", "—")
    task_type = task_fm.get("task_type") or "—"
    parts = [
        rubric,
        "\n\n=== TASK (what the worker was asked to do) ===",
        f"Title: {title}\nDomain: {domain}\nType: {task_type}",
        "\nTask description:\n" + (body.strip() or "(none)"),
    ]
    # The voice guide is the standard for the message rubric's voice/format dims.
    if kind == "message" and voice:
        parts.append("\n=== JAY'S VOICE GUIDE (the standard for voice & format) ===\n" + voice)
    # The execution-trace tail helps for documents; meetings/messages are judged
    # on the deliverable itself, so skip the noise there.
    if log_tail and kind == "document":
        parts.append("\n=== EXECUTION TRACE (dispatch log tail — context only) ===\n" + log_tail)
    label = KIND_EVIDENCE_LABEL.get(kind, "DELIVERABLE (score this)")
    parts.append(f"\n=== {label} ===\n" + (evidence or "(missing or empty)"))
    parts.append("\n\nReturn only the JSON verdict object now.")
    return "\n".join(parts)


def run_claude(prompt):
    """Call Claude headless (Opus). Returns assistant text or None."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "CMUX_CLAUDE"))}
    env["PATH"] = (
        os.path.join(os.path.expanduser("~"), ".local", "bin")
        + ":/opt/homebrew/bin:" + env.get("PATH", "/usr/bin:/bin")
    )
    cmd = ["claude", "-p", prompt, "--model", JUDGE_MODEL, "--output-format", "json"]
    try:
        proc = subprocess.run(
            cmd, cwd=PM_OS_DIR, env=env, capture_output=True, text=True, timeout=CLAUDE_TIMEOUT
        )
    except FileNotFoundError:
        log("'claude' not found on PATH — skipping (completion is unaffected)")
        return None
    except subprocess.TimeoutExpired:
        log(f"claude timed out after {CLAUDE_TIMEOUT}s")
        return None
    if proc.returncode != 0:
        log(f"claude exited {proc.returncode}: {proc.stderr.strip()[:300]}")
        return None
    out = proc.stdout.strip()
    # --output-format json wraps the result in an envelope: {"result": "...", ...}
    try:
        env_obj = json.loads(out)
        if isinstance(env_obj, dict) and "result" in env_obj:
            return env_obj["result"]
    except (json.JSONDecodeError, ValueError):
        pass
    return out


def parse_verdict(text, kind):
    """Extract and validate the verdict JSON from the model's text.

    Dimension keys are kind-specific (DIMENSIONS_BY_KIND); meeting verdicts carry none.
    """
    if not text:
        return None
    obj = None
    # Strip markdown fences if present, then try direct then greedy-brace parse.
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    for candidate in (cleaned, text):
        try:
            obj = json.loads(candidate)
            break
        except (json.JSONDecodeError, ValueError):
            m = re.search(r"\{.*\}", candidate, re.DOTALL)
            if m:
                try:
                    obj = json.loads(m.group(0))
                    break
                except (json.JSONDecodeError, ValueError):
                    continue
    if not isinstance(obj, dict):
        return None

    def clamp(v):
        try:
            return max(1, min(10, int(round(float(v)))))
        except (TypeError, ValueError):
            return None

    score = clamp(obj.get("score"))
    if score is None:
        return None
    dims_in = obj.get("dimensions") or {}
    dimensions = {}
    for k in DIMENSIONS_BY_KIND.get(kind, []):
        cv = clamp(dims_in.get(k)) if isinstance(dims_in, dict) else None
        if cv is not None:
            dimensions[k] = cv
    why = str(obj.get("why") or "").strip()
    return {"score": score, "dimensions": dimensions, "why": why}


def write_back(task_id, verdict, rubric_version, kind):
    """Write judge_* fields onto the task (archive-aware) + activity comment."""
    changes = {
        "judge_score": verdict["score"],
        "judge_why": verdict["why"],
        "judge_dimensions": verdict["dimensions"],
        "judge_kind": kind,
        "judge_rubric_version": rubric_version,
        "judge_scored_at": task_lib._now_iso(),
    }
    comment = f"Judge scored: {verdict['score']}/10 — {verdict['why']}"
    try:
        task_lib.update_task(task_id, changes=changes, comment=comment, actor="judge")
        return True
    except FileNotFoundError:
        pass  # task already archived — update_task can't locate it; write in place
    # Archive-aware fallback using task_lib primitives.
    filepath = None
    for root, _dirs, files in os.walk(task_lib.ARCHIVE_DIR):
        if f"{task_id}.md" in files:
            filepath = os.path.join(root, f"{task_id}.md")
            break
    if not filepath:
        log(f"could not locate task file for {task_id} to write verdict")
        return False
    try:
        fm, body = task_lib._parse_task_file(filepath)
        fm.update(changes)
        fm["updated"] = task_lib._now_iso()
        body = body.rstrip("\n") + f"\n\n### {fm['updated']} — judge [comment]\n{comment}\n"
        task_lib._write_task_file(filepath, fm, body)
        return True
    except Exception as e:
        log(f"archive write-back failed: {e}")
        return False


def score_langfuse_trace(task_id, verdict, kind):
    """Write a judge-score onto the task's worker-execution trace + a judge trace."""
    try:
        from langfuse_client import get_langfuse, create_trace, score_trace, flush
    except Exception:
        return
    lf = get_langfuse()
    if lf is None:
        return
    # Visibility trace for the judge run itself.
    try:
        create_trace(
            name="judge",
            session_id=task_id,
            metadata={"model": JUDGE_MODEL, "kind": kind, "dimensions": verdict["dimensions"]},
            tags=["judge", "shadow", f"kind:{kind}"],
            input_data={"task_id": task_id, "kind": kind},
            output_data={"score": verdict["score"], "why": verdict["why"]},
        )
    except Exception:
        pass
    # Score the worker-execution trace so it sits alongside human-feedback.
    try:
        result = lf.api.trace.list(session_id=task_id, order_by="timestamp.asc")
        traces = result.data if hasattr(result, "data") else []
        target = None
        for t in traces:
            if str(getattr(t, "name", "")).startswith("worker-execution"):
                target = getattr(t, "id", None)  # last match wins (most recent rerun)
        if target:
            score_trace(target, "judge-score", float(verdict["score"]),
                        comment=verdict["why"], data_type="NUMERIC")
        else:
            log("no worker-execution trace found to score")
    except Exception as e:
        log(f"trace scoring failed: {e}")
    try:
        flush()
    except Exception:
        pass


# ── Main ────────────────────────────────────────────────────────────────────

def judge_task(task_id):
    load_env()
    try:
        task = task_lib.read_task(task_id)  # archive-aware read
    except Exception as e:
        log(f"cannot read {task_id}: {e}")
        return 0
    fm = task["frontmatter"]
    body = task.get("body", "")

    kind = detect_kind(fm)
    if kind is None:
        log(f"{task_id} has no gradeable deliverable (document/message/meeting); skipping")
        return 0

    evidence, note = gather_evidence(kind, fm, body, task_id)
    if evidence is None:
        log(f"{task_id} [{kind}]: {note}; skipping")
        return 0

    rubric, rubric_version = fetch_rubric(kind)
    voice = voice_version = None
    if kind == "message":
        voice, voice_version = fetch_voice()
    prompt = build_prompt(kind, rubric, fm, body, evidence, read_log_tail(task_id), voice=voice)

    vlabel = f", voice {voice_version}" if voice_version else ""
    log(f"scoring {task_id} [{kind}] ({note}, rubric {rubric_version}{vlabel})")
    text = run_claude(prompt)
    verdict = parse_verdict(text, kind)
    if verdict is None:
        log(f"could not parse a verdict for {task_id}; leaving unscored")
        return 0

    wrote = write_back(task_id, verdict, rubric_version, kind)
    score_langfuse_trace(task_id, verdict, kind)
    log(f"done: {task_id} [{kind}] → {verdict['score']}/10 {verdict['dimensions']} (written={wrote})")
    return 0


def main():
    ap = argparse.ArgumentParser(description="PM-OS shadow judge — score a completed agent artifact")
    ap.add_argument("--task", required=True, metavar="TASK-NNNN", help="task to judge")
    args = ap.parse_args()
    try:
        return judge_task(args.task)
    except Exception as e:  # never raise into the caller / spawner
        log(f"unexpected error: {e}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
