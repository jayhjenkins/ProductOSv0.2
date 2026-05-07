#!/usr/bin/env python3
"""
eval_task_classifier.py — LangFuse dataset & eval pipeline for task queue/worker classification.

Subcommands:
    create-dataset     Build LangFuse dataset from human annotations
    register-prompt    Register task-parser and worker-router prompts in LangFuse
    run                Run an eval experiment (queue classification, worker routing, or both)

Usage:
    python3 scripts/eval_task_classifier.py create-dataset
    python3 scripts/eval_task_classifier.py register-prompt
    python3 scripts/eval_task_classifier.py run --eval-type queue --run-name "queue-v1"
    python3 scripts/eval_task_classifier.py run --eval-type queue --mode keyword --run-name "queue-keyword"
    python3 scripts/eval_task_classifier.py run --eval-type worker --run-name "worker-v1"
"""

import argparse
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# ── Paths ───────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
TASKS_DIR = PROJECT_DIR / "datasets" / "tasks"
ANNOTATIONS_PATH = PROJECT_DIR / "datasets" / "evals" / "task-classifier" / "annotations.json"
ENV_FILE = PROJECT_DIR / ".env.langfuse"
WORKERS_DIR = SCRIPT_DIR / "workers"

OLLAMA_BASE = "http://localhost:11434/v1"
QUEUE_MODEL = "nemotron-3-nano:30b"
QUEUE_FALLBACK = "qwen3:30b-a3b"
WORKER_MODEL = "qwen3:4b"

VALID_QUEUES = {"human", "agent", "collab", "waiting"}
VALID_WORKERS = {"default", "product-analyst", "researcher", "scheduler", "ticket-creator"}

QUEUE_DATASET = "task-classifier"
QUEUE_PROMPT = "task-parser"
WORKER_PROMPT = "worker-router"


# ── Helpers ─────────────────────────────────────────────────────────────────────

def load_env():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip().removeprefix("export ")
            if line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def get_langfuse():
    load_env()
    try:
        from langfuse import Langfuse
        return Langfuse(
            public_key=os.environ.get("LANGFUSE_PUBLIC_KEY", ""),
            secret_key=os.environ.get("LANGFUSE_SECRET_KEY", ""),
            host=os.environ.get("LANGFUSE_HOST", "http://localhost:3000"),
        )
    except ImportError:
        print("Error: langfuse package not installed.")
        sys.exit(1)


def load_annotations():
    if not ANNOTATIONS_PATH.exists():
        print(f"Error: No annotations at {ANNOTATIONS_PATH}")
        print("Run annotate_tasks.py first.")
        sys.exit(1)
    return json.loads(ANNOTATIONS_PATH.read_text())


def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^(\w[\w_]*)\s*:\s*'?\"?(.+?)'?\"?\s*$", line)
        if kv:
            val = kv.group(2)
            fm[kv.group(1)] = None if val in ("null", "~", "") else val
    return fm


def extract_description(text):
    m = re.search(r"## Description\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    fm_end = re.match(r"^---\n.*?\n---\n?", text, re.DOTALL)
    return (text[fm_end.end():] if fm_end else text).strip()


def find_task_file(task_id):
    """Find a task file by ID across active queues and archive."""
    for queue in ("human", "agent", "collab", "waiting"):
        p = TASKS_DIR / queue / f"{task_id}.md"
        if p.exists():
            return p
    for p in (TASKS_DIR / "_archive").rglob(f"{task_id}.md"):
        return p
    return None


def item_id(task_id):
    return hashlib.sha256(task_id.encode()).hexdigest()[:16]


def get_task_parser_prompt():
    """Get the task-parser system prompt."""
    sys.path.insert(0, str(SCRIPT_DIR))
    try:
        from parse_task_input import SYSTEM_PROMPT
        return SYSTEM_PROMPT
    except ImportError:
        return None


def get_worker_router_prompt():
    """Get the worker-router prompt."""
    sys.path.insert(0, str(SCRIPT_DIR))
    try:
        from task_dispatch import _WORKER_MATCH_PROMPT
        return _WORKER_MATCH_PROMPT
    except ImportError:
        return None


def load_worker_descriptions():
    """Load worker name/description from worker definition files."""
    workers = []
    for f in sorted(WORKERS_DIR.glob("*.md")):
        text = f.read_text()
        fm = parse_frontmatter(text)
        name = fm.get("name", f.stem)
        desc = fm.get("description", "")
        workers.append({"name": name, "description": desc})
    return workers


def keyword_classify_queue(title, description=""):
    """Simple keyword baseline for queue classification."""
    t = (title + " " + (description or "")).lower()
    if any(w in t for w in ("waiting on", "receive from", "get back from", "waiting for")):
        return "waiting"
    if any(w in t for w in ("schedule meeting", "schedule a meeting", "talk to", "chat with",
                             "meet with", "sync with", "connect with", "catch up with",
                             "set up a meeting", "book a meeting")):
        return "collab"
    if any(w in t for w in ("send message", "send email", "have a conversation", "make a call",
                             "get access", "make a phone call", "message ", "ask ")):
        return "human"
    return "agent"


# ── Subcommand: create-dataset ──────────────────────────────────────────────────

def cmd_create_dataset(args):
    data = load_annotations()
    annotations = data.get("annotations", {})
    if not annotations:
        print("No annotations found.")
        sys.exit(1)

    lf = get_langfuse()
    print(f"Creating dataset '{QUEUE_DATASET}'...")
    lf.create_dataset(
        name=QUEUE_DATASET,
        description=f"Task queue/worker classification ground truth ({len(annotations)} items)",
    )

    created = 0
    skipped = 0
    for task_id, ann in annotations.items():
        task_path = find_task_file(task_id)
        if not task_path:
            print(f"  Warning: {task_id} not found, skipping")
            skipped += 1
            continue

        text = task_path.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)
        desc = extract_description(text)

        lf.create_dataset_item(
            dataset_name=QUEUE_DATASET,
            id=item_id(task_id),
            input={
                "title": fm.get("title", ""),
                "description": desc[:800],
                "domain": fm.get("domain") or "",
                "priority": fm.get("priority", ""),
                "task_type": fm.get("task_type") or "",
                "creator": fm.get("creator", ""),
            },
            expected_output={
                "queue": ann["correct_queue"],
                "worker": ann.get("correct_worker"),
            },
            metadata={
                "original_queue": ann.get("original_queue", ""),
                "task_id": task_id,
                "status": fm.get("status", ""),
            },
        )
        created += 1

    lf.flush()
    print(f"Done. {created} items created/updated, {skipped} skipped.")
    print(f"View: http://localhost:3000 -> Datasets -> {QUEUE_DATASET}")


# ── Subcommand: register-prompt ─────────────────────────────────────────────────

def cmd_register_prompt(args):
    lf = get_langfuse()

    # Task-parser prompt
    tp = get_task_parser_prompt()
    if tp:
        print(f"Registering '{QUEUE_PROMPT}'...")
        try:
            lf.create_prompt(
                name=QUEUE_PROMPT, prompt=tp,
                config={"model": QUEUE_MODEL, "temperature": 0},
                labels=["production"], type="text",
            )
            print(f"  Registered '{QUEUE_PROMPT}' with label 'production'.")
        except Exception as e:
            if "already exists" in str(e).lower() or "409" in str(e):
                print(f"  '{QUEUE_PROMPT}' already exists.")
            else:
                raise

    # Worker-router prompt
    wr = get_worker_router_prompt()
    if wr:
        print(f"Registering '{WORKER_PROMPT}'...")
        try:
            lf.create_prompt(
                name=WORKER_PROMPT, prompt=wr,
                config={"model": WORKER_MODEL, "temperature": 0},
                labels=["production"], type="text",
            )
            print(f"  Registered '{WORKER_PROMPT}' with label 'production'.")
        except Exception as e:
            if "already exists" in str(e).lower() or "409" in str(e):
                print(f"  '{WORKER_PROMPT}' already exists.")
            else:
                raise

    lf.flush()


# ── Subcommand: run ─────────────────────────────────────────────────────────────

def cmd_run(args):
    lf = get_langfuse()
    eval_type = args.eval_type
    mode = args.mode
    model = args.model or (WORKER_MODEL if eval_type == "worker" else QUEUE_MODEL)
    prompt_label = args.prompt_label
    run_name = args.run_name

    print(f"Fetching dataset '{QUEUE_DATASET}'...")
    dataset = lf.get_dataset(QUEUE_DATASET)
    items = dataset.items
    print(f"Dataset has {len(items)} items.")

    if not items:
        print("No items. Run create-dataset first.")
        sys.exit(1)

    # Filter to agent/collab items for worker eval
    if eval_type == "worker":
        items = [i for i in items if (i.expected_output or {}).get("worker")]
        print(f"Filtered to {len(items)} agent/collab items for worker eval.")
        if not items:
            print("No agent/collab items with worker annotations.")
            sys.exit(1)

    # Get prompts
    system_prompt = None
    if mode == "llm":
        prompt_name = WORKER_PROMPT if eval_type == "worker" else QUEUE_PROMPT
        try:
            lf_prompt = lf.get_prompt(prompt_name, label=prompt_label, cache_ttl_seconds=0)
            system_prompt = lf_prompt.prompt
            print(f"Using LangFuse prompt '{prompt_name}' (label={prompt_label})")
        except Exception:
            if eval_type == "worker":
                system_prompt = get_worker_router_prompt()
            else:
                system_prompt = get_task_parser_prompt()
            print(f"Using hardcoded prompt for '{prompt_name}'")

        # Check Ollama
        try:
            import urllib.request
            urllib.request.urlopen(f"{OLLAMA_BASE.replace('/v1', '')}/api/tags", timeout=5)
        except Exception:
            print("Error: Ollama not running.")
            sys.exit(1)

    # Shared Ollama client
    from openai import OpenAI
    _client = OpenAI(base_url=OLLAMA_BASE, api_key="ollama") if mode == "llm" else None

    # Worker descriptions for worker eval
    worker_descs = None
    if eval_type == "worker":
        workers = load_worker_descriptions()
        worker_descs = "\n".join(f"- **{w['name']}**: {w['description']}" for w in workers)

    # ── Task functions ──

    def queue_task(*, item, **kwargs):
        inp = item.input if hasattr(item, "input") else item["input"]
        title = inp.get("title", "")
        desc = inp.get("description", "")

        if mode == "keyword":
            return {"queue": keyword_classify_queue(title, desc)}

        # Build user message as title + description (approximating raw input)
        user_msg = f"{title}\n\n{desc}" if desc else title

        for m in [model, QUEUE_FALLBACK] if model != QUEUE_FALLBACK else [model]:
            try:
                resp = _client.chat.completions.create(
                    model=m,
                    messages=[
                        {"role": "system", "content": system_prompt.replace("{today}", "2026-04-13")},
                        {"role": "user", "content": user_msg},
                    ],
                    temperature=0, max_tokens=2048,
                )
                raw = resp.choices[0].message.content or ""
                raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
                # Extract JSON
                jm = re.search(r"\{.*\}", raw, re.DOTALL)
                if jm:
                    parsed = json.loads(jm.group())
                    q = parsed.get("queue", "").lower().strip()
                    if q in VALID_QUEUES:
                        return {"queue": q}
            except Exception as exc:
                print(f"  Warning: Ollama error ({m}): {exc}")

        return {"queue": keyword_classify_queue(title, desc)}

    def worker_task(*, item, **kwargs):
        inp = item.input if hasattr(item, "input") else item["input"]
        expected = item.expected_output if hasattr(item, "expected_output") else item["expected_output"]
        title = inp.get("title", "")
        desc = inp.get("description", "")
        domain = inp.get("domain", "")
        task_type = inp.get("task_type", "")
        queue = expected.get("queue", "agent")

        prompt = system_prompt.format(
            worker_list=worker_descs,
            title=title, queue=queue, domain=domain,
            task_type=task_type or "null", description=desc[:400],
        )

        try:
            resp = _client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0, max_tokens=512,
            )
            raw = resp.choices[0].message.content or ""
            raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
            jm = re.search(r"\{.*\}", raw, re.DOTALL)
            if jm:
                parsed = json.loads(jm.group())
                w = parsed.get("worker", "").lower().strip()
                if w in VALID_WORKERS:
                    return {"worker": w}
        except Exception as exc:
            print(f"  Warning: Worker routing error: {exc}")

        return {"worker": "default"}

    # ── Evaluators ──

    from langfuse import Evaluation

    if eval_type in ("queue", "both"):
        def queue_exact_match(*, output, expected_output, **kwargs):
            pred = (output or {}).get("queue", "")
            exp = (expected_output or {}).get("queue", "")
            return Evaluation(
                name="queue_exact_match", value=1.0 if pred == exp else 0.0,
                comment=f"predicted={pred}, expected={exp}",
            )

        def queue_actionable_match(*, output, expected_output, **kwargs):
            pred = (output or {}).get("queue", "")
            exp = (expected_output or {}).get("queue", "")
            pred_bucket = "actionable" if pred in ("agent", "collab") else "deferred"
            exp_bucket = "actionable" if exp in ("agent", "collab") else "deferred"
            return Evaluation(
                name="queue_actionable_match", value=1.0 if pred_bucket == exp_bucket else 0.0,
                comment=f"pred_bucket={pred_bucket}, exp_bucket={exp_bucket}",
            )

    if eval_type in ("worker", "both"):
        def worker_exact_match(*, output, expected_output, **kwargs):
            pred = (output or {}).get("worker", "")
            exp = (expected_output or {}).get("worker", "")
            if not exp:
                return Evaluation(name="worker_exact_match", value=1.0, comment="no worker expected")
            return Evaluation(
                name="worker_exact_match", value=1.0 if pred == exp else 0.0,
                comment=f"predicted={pred}, expected={exp}",
            )

    # Run-level evaluators
    def accuracy_summary(*, item_results, **kwargs):
        scores = [ev.value for r in item_results for ev in (r.evaluations or [])
                  if ev.name.endswith("_exact_match")]
        avg = sum(scores) / len(scores) if scores else 0
        correct = sum(1 for s in scores if s == 1.0)
        return Evaluation(
            name="overall_accuracy", value=round(avg, 4),
            comment=f"{correct}/{len(scores)} correct",
        )

    def confusion_summary(*, item_results, **kwargs):
        matrix = defaultdict(lambda: defaultdict(int))
        field = "worker" if eval_type == "worker" else "queue"
        for r in item_results:
            exp_out = r.item.expected_output if hasattr(r.item, "expected_output") else r.item.get("expected_output")
            expected = (exp_out or {}).get(field, "")
            predicted = (r.output or {}).get(field, "")
            if expected and predicted:
                matrix[expected][predicted] += 1
        confused = [(e, p, c) for e, preds in matrix.items() for p, c in preds.items() if e != p]
        confused.sort(key=lambda x: -x[2])
        comment = "; ".join(f"{e}->{p}: {c}" for e, p, c in confused[:5]) if confused else "none"
        return Evaluation(name="confusion_pairs", value=len(confused), comment=comment)

    # Build evaluator lists
    evaluators = []
    if eval_type in ("queue", "both"):
        evaluators += [queue_exact_match, queue_actionable_match]
    if eval_type in ("worker", "both"):
        evaluators.append(worker_exact_match)

    task_fn = worker_task if eval_type == "worker" else queue_task

    print(f"\nRunning experiment: {run_name} (eval_type={eval_type}, mode={mode})...")
    if mode == "llm":
        print(f"Estimated time: ~{len(items) * 3}s\n")

    result = lf.run_experiment(
        name=QUEUE_DATASET,
        run_name=run_name,
        description=f"Task routing eval: type={eval_type}, mode={mode}, model={model}",
        data=items,
        task=task_fn,
        evaluators=evaluators,
        run_evaluators=[accuracy_summary, confusion_summary],
        max_concurrency=1,
        metadata={"eval_type": eval_type, "mode": mode, "model": model, "prompt_label": prompt_label},
    )

    # Print results
    field = "worker" if eval_type == "worker" else "queue"
    valid_values = sorted(VALID_WORKERS if eval_type == "worker" else VALID_QUEUES)

    print("\n" + "=" * 60)
    print(f"EXPERIMENT RESULTS: {run_name}")
    print("=" * 60)

    if result.run_evaluations:
        for ev in result.run_evaluations:
            print(f"\n  {ev.name}: {ev.value}")
            if ev.comment:
                print(f"    {ev.comment}")

    # Per-value accuracy
    stats = defaultdict(lambda: {"correct": 0, "total": 0})
    confusion = defaultdict(lambda: defaultdict(int))
    for r in result.item_results:
        exp_out = r.item.expected_output if hasattr(r.item, "expected_output") else r.item.get("expected_output")
        expected = (exp_out or {}).get(field, "")
        predicted = (r.output or {}).get(field, "")
        if expected:
            stats[expected]["total"] += 1
            if predicted == expected:
                stats[expected]["correct"] += 1
            confusion[expected][predicted] += 1

    print(f"\n  Per-{field.title()} Accuracy:")
    print(f"  {field.title():<20} {'Correct':>8} {'Total':>8} {'Accuracy':>10}")
    print(f"  {'-'*48}")
    for val in valid_values:
        s = stats[val]
        acc = s["correct"] / s["total"] if s["total"] > 0 else 0
        print(f"  {val:<20} {s['correct']:>8} {s['total']:>8} {acc:>9.1%}")

    # Confusion matrix
    print(f"\n  Confusion Matrix (rows=expected, cols=predicted):")
    short = {v: v[:8] for v in valid_values}
    header = "  " + f"{'':>14}" + "".join(f"{short[v]:>10}" for v in valid_values)
    print(header)
    for exp in valid_values:
        row = f"  {short[exp]:>14}"
        for pred in valid_values:
            count = confusion[exp][pred]
            row += f"{str(count) if count > 0 else '.':>10}"
        print(row)

    print(f"\n  View: http://localhost:3000 -> Datasets -> {QUEUE_DATASET}")
    if hasattr(result, "dataset_run_url") and result.dataset_run_url:
        print(f"  Direct link: {result.dataset_run_url}")

    lf.flush()


# ── CLI ─────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Task routing LangFuse eval pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("create-dataset", help="Create LangFuse dataset from annotations")
    sub.add_parser("register-prompt", help="Register task-parser and worker-router prompts")

    rp = sub.add_parser("run", help="Run eval experiment")
    rp.add_argument("--run-name", default=None)
    rp.add_argument("--eval-type", choices=["queue", "worker", "both"], default="queue")
    rp.add_argument("--mode", choices=["llm", "keyword"], default="llm")
    rp.add_argument("--model", default=None)
    rp.add_argument("--prompt-label", default="production")

    args = parser.parse_args()

    if args.command == "create-dataset":
        cmd_create_dataset(args)
    elif args.command == "register-prompt":
        cmd_register_prompt(args)
    elif args.command == "run":
        if args.run_name is None:
            from datetime import datetime
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            args.run_name = f"{args.eval_type}-{args.mode}-{ts}"
        cmd_run(args)


if __name__ == "__main__":
    main()
