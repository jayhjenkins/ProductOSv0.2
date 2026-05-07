#!/usr/bin/env python3
"""
eval_meeting_classifier.py — LangFuse dataset & eval pipeline for meeting domain classification.

Subcommands:
    create-dataset     Build LangFuse dataset from human annotations
    register-prompt    Register the classifier system prompt in LangFuse
    run                Run an eval experiment (LLM or keyword baseline)

Usage:
    # After annotating meetings via annotate_meetings.py:
    python3 scripts/eval_meeting_classifier.py create-dataset
    python3 scripts/eval_meeting_classifier.py register-prompt
    python3 scripts/eval_meeting_classifier.py run --run-name "llm-v1-nemotron"
    python3 scripts/eval_meeting_classifier.py run --mode keyword --run-name "keyword-baseline"
    python3 scripts/eval_meeting_classifier.py run --prompt-label staging --run-name "v2-experiment"
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
MEETINGS_DIR = PROJECT_DIR / "datasets" / "meetings"
ANNOTATIONS_PATH = PROJECT_DIR / "datasets" / "evals" / "meeting-classifier" / "annotations.json"
ENV_FILE = PROJECT_DIR / ".env.langfuse"

# Add otter scripts to path for importing classifier logic
OTTER_DIR = Path.home() / "scripts" / "otter"
if OTTER_DIR.exists():
    sys.path.insert(0, str(OTTER_DIR))

OLLAMA_BASE = "http://localhost:11434/v1"
DEFAULT_MODEL = "nemotron-3-nano:30b"
FALLBACK_MODEL = "qwen3:4b"

VALID_DOMAINS = {
    "recruiting", "product/payments", "product/home", "product/platform",
    "leadership", "strategy", "customer", "general",
}

DATASET_NAME = "meeting-classifier"
PROMPT_NAME = "meeting-classifier"


# ── Helpers ─────────────────────────────────────────────────────────────────────

def load_env():
    """Load .env.langfuse into os.environ."""
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            # Handle export KEY=VALUE and KEY=VALUE
            line = line.removeprefix("export ")
            key, _, val = line.partition("=")
            val = val.strip().strip('"').strip("'")
            os.environ.setdefault(key.strip(), val)


def get_langfuse():
    """Import and return the LangFuse client."""
    load_env()
    try:
        from langfuse import Langfuse
        return Langfuse(
            public_key=os.environ.get("LANGFUSE_PUBLIC_KEY", ""),
            secret_key=os.environ.get("LANGFUSE_SECRET_KEY", ""),
            host=os.environ.get("LANGFUSE_HOST", "http://localhost:3000"),
        )
    except ImportError:
        print("Error: langfuse package not installed. Run: pip install langfuse")
        sys.exit(1)


def load_annotations():
    """Load the annotations JSON."""
    if not ANNOTATIONS_PATH.exists():
        print(f"Error: No annotations found at {ANNOTATIONS_PATH}")
        print("Run annotate_meetings.py first to create annotations.")
        sys.exit(1)
    return json.loads(ANNOTATIONS_PATH.read_text())


def parse_frontmatter(text):
    """Extract YAML frontmatter dict."""
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        kv = re.match(r'^(\w[\w_]*)\s*:\s*"?(.+?)"?\s*$', line)
        if kv:
            fm[kv.group(1)] = kv.group(2)
    return fm


def transcript_body(text, max_chars=600):
    """Extract transcript body after frontmatter (matching classifier input)."""
    m = re.match(r"^---\n.*?\n---\n?", text, re.DOTALL)
    body = text[m.end():] if m else text
    return body.strip()[:max_chars]


def domain_from_path(rel_path):
    """Extract domain from relative path."""
    parts = Path(rel_path).parts
    if len(parts) >= 2 and parts[0] == "product":
        return f"product/{parts[1]}"
    if len(parts) >= 1 and parts[0] in VALID_DOMAINS:
        return parts[0]
    return "unknown"


def item_id(rel_path):
    """Deterministic ID for a dataset item (for idempotent upserts)."""
    return hashlib.sha256(rel_path.encode()).hexdigest()[:16]


def get_classify_system():
    """Get the classifier system prompt — try importing from otter_classify.py, fallback to hardcoded."""
    try:
        from otter_classify import CLASSIFY_SYSTEM
        return CLASSIFY_SYSTEM
    except ImportError:
        return (
            "You are classifying meeting transcripts for a Director of Product at a B2B SaaS company "
            "(Vantaca — property management software). Respond with ONLY the domain path, nothing else.\n\n"
            "Domains:\n"
            "- recruiting           (PM candidate interviews, hiring discussions)\n"
            "- product/payments     (payments product meetings, Pay Standup, Payments L10)\n"
            "- product/home         (home product feature work, home team meetings)\n"
            "- product/platform     (platform, API, AI, technical infrastructure)\n"
            "- leadership           (1:1s with anyone, exec intros, cross-functional syncs, team standups)\n"
            "- strategy             (roadmap, quarterly planning, vendor strategy, partner intros)\n"
            "- customer             (customer calls, demos, prospect calls, CS reviews)\n"
            "- general              (anything else)"
        )


def keyword_classify(title, filename_hint=""):
    """Keyword-based fallback classifier (mirrors otter_classify._keyword_classify)."""
    t = (title + " " + filename_hint).lower()
    if any(w in t for w in ("interview", "hiring", "candidate")):
        return "recruiting"
    if any(w in t for w in ("l10", "standup", "stand-up")):
        if any(w in t for w in ("pay", "payment", "payments")):
            return "product/payments"
        return "leadership"
    if "1:1" in t or "1-1" in t or "one on one" in t:
        return "leadership"
    if any(w in t for w in ("payments", "payment", "pay standup", "pay release")):
        return "product/payments"
    if "home" in t and "product" not in t:
        return "product/home"
    if any(w in t for w in ("platform", "apollo", "api", "infrastructure")):
        return "product/platform"
    if any(w in t for w in ("customer", "demo", "prospect", "cs review")):
        return "customer"
    if any(w in t for w in ("roadmap", "strategy", "quarterly", "vendor", "partner", "intro to")):
        return "strategy"
    return "general"


# ── Subcommand: create-dataset ──────────────────────────────────────────────────

def cmd_create_dataset(args):
    """Create or update LangFuse dataset from annotations."""
    data = load_annotations()
    annotations = data.get("annotations", {})
    if not annotations:
        print("No annotations found. Run annotate_meetings.py first.")
        sys.exit(1)

    lf = get_langfuse()

    # Create dataset (idempotent)
    print(f"Creating dataset '{DATASET_NAME}'...")
    lf.create_dataset(
        name=DATASET_NAME,
        description=f"Meeting domain classification ground truth ({len(annotations)} items)",
    )

    created = 0
    skipped = 0
    for rel_path, ann in annotations.items():
        # Read the actual meeting file for classifier input
        meeting_path = MEETINGS_DIR / rel_path
        if not meeting_path.exists():
            print(f"  Warning: {rel_path} not found, skipping")
            skipped += 1
            continue

        text = meeting_path.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)
        title = fm.get("title", meeting_path.stem)
        preview = transcript_body(text, max_chars=600)

        lf.create_dataset_item(
            dataset_name=DATASET_NAME,
            id=item_id(rel_path),
            input={"title": title, "transcript_preview": preview},
            expected_output=ann["correct_domain"],
            metadata={
                "original_domain": ann.get("original_domain", ""),
                "frontmatter_domain": fm.get("domain", ""),
                "date": ann.get("date", ""),
                "rel_path": rel_path,
            },
        )
        created += 1

    lf.flush()
    print(f"Done. {created} items created/updated, {skipped} skipped.")
    print(f"View in LangFuse: http://localhost:3000 -> Datasets -> {DATASET_NAME}")


# ── Subcommand: register-prompt ─────────────────────────────────────────────────

def cmd_register_prompt(args):
    """Register the classifier system prompt in LangFuse."""
    lf = get_langfuse()
    system_prompt = get_classify_system()

    print(f"Registering prompt '{PROMPT_NAME}'...")
    try:
        lf.create_prompt(
            name=PROMPT_NAME,
            prompt=system_prompt,
            config={
                "model": DEFAULT_MODEL,
                "fallback_model": FALLBACK_MODEL,
                "temperature": 0,
                "valid_domains": sorted(VALID_DOMAINS),
            },
            labels=["production"],
            type="text",
        )
        print("Prompt registered with label 'production'.")
    except Exception as e:
        if "already exists" in str(e).lower() or "409" in str(e):
            print("Prompt already exists. Edit it in the LangFuse UI to create new versions.")
        else:
            raise

    lf.flush()
    print(f"View in LangFuse: http://localhost:3000 -> Prompts -> {PROMPT_NAME}")


# ── Subcommand: run ─────────────────────────────────────────────────────────────

def cmd_run(args):
    """Run an eval experiment against the dataset."""
    lf = get_langfuse()
    mode = args.mode
    model = args.model
    prompt_label = args.prompt_label
    run_name = args.run_name

    # Fetch dataset
    print(f"Fetching dataset '{DATASET_NAME}'...")
    dataset = lf.get_dataset(DATASET_NAME)
    items = dataset.items
    print(f"Dataset has {len(items)} items.")

    if not items:
        print("No items in dataset. Run create-dataset first.")
        sys.exit(1)

    # Get system prompt
    system_prompt = None
    if mode == "llm":
        # Try LangFuse prompt first
        try:
            lf_prompt = lf.get_prompt(PROMPT_NAME, label=prompt_label, cache_ttl_seconds=0)
            system_prompt = lf_prompt.prompt
            print(f"Using LangFuse prompt '{PROMPT_NAME}' (label={prompt_label})")
        except Exception:
            system_prompt = get_classify_system()
            print(f"LangFuse prompt not found, using hardcoded prompt")

        # Check Ollama is available
        try:
            import urllib.request
            urllib.request.urlopen(f"{OLLAMA_BASE.replace('/v1', '')}/api/tags", timeout=5)
            print(f"Ollama is running. Model: {model}")
        except Exception:
            print("Error: Ollama is not running. Start it or use --mode keyword")
            sys.exit(1)

    # Single shared client (avoids leaking connections to Ollama)
    from openai import OpenAI
    _ollama_client = OpenAI(base_url=OLLAMA_BASE, api_key="ollama") if mode == "llm" else None

    # Define task function
    def classify_task(*, item, **kwargs):
        input_data = item.input if hasattr(item, "input") else item["input"]
        title = input_data["title"]
        preview = input_data["transcript_preview"]

        if mode == "keyword":
            return keyword_classify(title)

        # LLM classification
        user_msg = f"Title: {title}\nContent preview: {preview[:600]}"
        models = [model, FALLBACK_MODEL] if model != FALLBACK_MODEL else [model]

        for m in models:
            try:
                resp = _ollama_client.chat.completions.create(
                    model=m,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_msg},
                    ],
                    temperature=0,
                    max_tokens=1024,
                )
                raw = resp.choices[0].message.content or ""
                raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
                raw = raw.strip().lower()
                raw = re.sub(r'["\'\n]', "", raw).strip().rstrip(".")
                if raw in VALID_DOMAINS:
                    return raw
            except Exception as exc:
                print(f"  Warning: Ollama error ({m}): {exc}")

        # Keyword fallback
        return keyword_classify(title)

    # Define evaluators (must return Evaluation objects, not dicts)
    from langfuse import Evaluation

    def exact_match(*, output, expected_output, **kwargs):
        match = output == expected_output
        return Evaluation(
            name="exact_match",
            value=1.0 if match else 0.0,
            comment=f"predicted={output}, expected={expected_output}",
        )

    def category_match(*, output, expected_output, **kwargs):
        out_cat = (output or "").split("/")[0]
        exp_cat = (expected_output or "").split("/")[0]
        match = out_cat == exp_cat
        return Evaluation(
            name="category_match",
            value=1.0 if match else 0.0,
            comment=f"predicted_cat={out_cat}, expected_cat={exp_cat}",
        )

    def frontmatter_consistent(*, input, metadata, **kwargs):
        if not metadata:
            return Evaluation(name="frontmatter_consistent", value=1.0, comment="no metadata")
        fm_domain = metadata.get("frontmatter_domain", "")
        orig_domain = metadata.get("original_domain", "")
        match = fm_domain == orig_domain or fm_domain == ""
        return Evaluation(
            name="frontmatter_consistent",
            value=1.0 if match else 0.0,
            comment=f"frontmatter={fm_domain}, path={orig_domain}",
        )

    # Run-level evaluators
    def overall_accuracy(*, item_results, **kwargs):
        scores = []
        for r in item_results:
            for ev in (r.evaluations or []):
                if ev.name == "exact_match":
                    scores.append(ev.value)
        avg = sum(scores) / len(scores) if scores else 0
        return Evaluation(
            name="overall_accuracy",
            value=round(avg, 4),
            comment=f"{sum(1 for s in scores if s == 1.0)}/{len(scores)} correct",
        )

    def confusion_summary(*, item_results, **kwargs):
        matrix = defaultdict(lambda: defaultdict(int))
        for r in item_results:
            expected = r.item.expected_output if hasattr(r.item, "expected_output") else r.item.get("expected_output")
            predicted = r.output
            if expected and predicted:
                matrix[expected][predicted] += 1

        # Find top confused pairs
        confused = []
        for exp, preds in matrix.items():
            for pred, count in preds.items():
                if exp != pred:
                    confused.append((exp, pred, count))
        confused.sort(key=lambda x: -x[2])
        top5 = confused[:5]
        comment = "; ".join(f"{e}->{p}: {c}" for e, p, c in top5) if top5 else "no confusion"
        return Evaluation(
            name="confusion_pairs",
            value=len(confused),
            comment=comment,
        )

    # Run experiment
    print(f"\nRunning experiment: {run_name} (mode={mode})...")
    if mode == "llm":
        print(f"This will make {len(items)} Ollama calls. Estimated time: ~{len(items) * 3}s\n")

    result = lf.run_experiment(
        name=DATASET_NAME,
        run_name=run_name,
        description=f"Meeting classifier eval: mode={mode}, model={model}, prompt_label={prompt_label}",
        data=items,
        task=classify_task,
        evaluators=[exact_match, category_match, frontmatter_consistent],
        run_evaluators=[overall_accuracy, confusion_summary],
        max_concurrency=1,
        metadata={"mode": mode, "model": model, "prompt_label": prompt_label},
    )

    # Print results
    print("\n" + "=" * 60)
    print(f"EXPERIMENT RESULTS: {run_name}")
    print("=" * 60)

    # Run-level evaluations
    if result.run_evaluations:
        for ev in result.run_evaluations:
            print(f"\n  {ev.name}: {ev.value}")
            if ev.comment:
                print(f"    {ev.comment}")

    # Per-domain accuracy
    domain_stats = defaultdict(lambda: {"correct": 0, "total": 0})
    confusion = defaultdict(lambda: defaultdict(int))

    for r in result.item_results:
        expected = r.item.expected_output if hasattr(r.item, "expected_output") else r.item.get("expected_output")
        predicted = r.output
        if expected:
            domain_stats[expected]["total"] += 1
            if predicted == expected:
                domain_stats[expected]["correct"] += 1
            confusion[expected][predicted] += 1

    print("\n  Per-Domain Accuracy:")
    print(f"  {'Domain':<20} {'Correct':>8} {'Total':>8} {'Accuracy':>10}")
    print(f"  {'-'*48}")
    for domain in sorted(VALID_DOMAINS):
        s = domain_stats[domain]
        acc = s["correct"] / s["total"] if s["total"] > 0 else 0
        print(f"  {domain:<20} {s['correct']:>8} {s['total']:>8} {acc:>9.1%}")

    # Confusion matrix
    print("\n  Confusion Matrix (rows=expected, cols=predicted):")
    domains_sorted = sorted(VALID_DOMAINS)
    # Short labels for display
    short = {d: d.split("/")[-1][:6] for d in domains_sorted}
    header = "  " + f"{'':>12}" + "".join(f"{short[d]:>8}" for d in domains_sorted)
    print(header)
    for exp in domains_sorted:
        row = f"  {short[exp]:>12}"
        for pred in domains_sorted:
            count = confusion[exp][pred]
            cell = str(count) if count > 0 else "."
            row += f"{cell:>8}"
        print(row)

    print(f"\n  View detailed results: http://localhost:3000 -> Datasets -> {DATASET_NAME}")

    if hasattr(result, "dataset_run_url") and result.dataset_run_url:
        print(f"  Direct link: {result.dataset_run_url}")

    lf.flush()


# ── CLI ─────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Meeting classifier LangFuse eval pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("create-dataset", help="Create LangFuse dataset from annotations")
    sub.add_parser("register-prompt", help="Register classifier prompt in LangFuse")

    run_parser = sub.add_parser("run", help="Run eval experiment")
    run_parser.add_argument("--run-name", default=None, help="Name for this experiment run")
    run_parser.add_argument("--mode", choices=["llm", "keyword"], default="llm", help="Classification mode")
    run_parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model (default: {DEFAULT_MODEL})")
    run_parser.add_argument("--prompt-label", default="production", help="LangFuse prompt label to use")

    args = parser.parse_args()

    if args.command == "create-dataset":
        cmd_create_dataset(args)
    elif args.command == "register-prompt":
        cmd_register_prompt(args)
    elif args.command == "run":
        if args.run_name is None:
            from datetime import datetime
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            args.run_name = f"{args.mode}-{args.model.split(':')[0]}-{ts}"
        cmd_run(args)


if __name__ == "__main__":
    main()
