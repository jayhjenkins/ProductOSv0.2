# PM-OS Roadmap

> Living document. Anchored to what's actually on disk (skills, the task/cron/dispatch engine, LangFuse wiring, MCP connectors). This describes where the **system** goes — not the product data, which is gitignored.

**Last updated:** 2026-06-02

---

## Thesis

PM-OS already *runs* the work (dispatch → workers → skills) and *captures* feedback (LangFuse scoring + annotations). The part not yet nailed is the **loop closing**: captured feedback doesn't yet make the next run better, and the boundary between what an agent may finish autonomously vs. what needs a human is convention, not enforcement.

The spine that ties this together is a **shadow judge** that grows into a **quality manager**: it scores every card, gets calibrated against human feedback, and eventually gates output and earns task-types the right to run autonomously.

The arc: **report → scored report → autonomous action → product-area squad**, one task-type at a time, always reversible.

---

## 1. Self-improvement loop

Today: thumbs up/down and comments land on the LangFuse trace, but skills are read from disk and never change. **Capture ≠ learning.**

**What it looks like:** a weekly cron pass reads low-scored traces (judge *or* human) plus your free-text annotations. An improvement agent (a meta worker) clusters failures **by step** — worker-match? a specific skill? the voice? the output shape? — and proposes a concrete change as a `collab` card with a diff attached. You accept or reject. **Nothing auto-applies.**

**Fixes are not restricted to prompts.** The improvement agent picks the *altitude* of the fix:
- a skill edit (`.claude/skills/<name>/SKILL.md`)
- a new shared `voice.md` / `house-style.md` appended to relevant workers
- a worker scoping change (`scripts/workers/*.md`)
- a new quality-gate skill
- a golden example added to the eval set
- a rubric change to the judge itself

A recurring tone complaint becomes one `voice.md`, not six scattered skill edits. This is `meta-refine-workflow` pointed inward.

**Golden dataset:** the accumulated human-annotated traces. Seed pattern already exists in `eval_meeting_classifier.py` / `eval_task_classifier.py`; extend it to output-quality evals. The judge *proposes* candidates (high-score, high-agreement outputs); **you confirm inclusion.** The judge never adds to its own ground truth.

**Done when:** a down-vote reliably produces a proposed change (at the right altitude) that you can accept as a diff.

---

## 2. Shadow judge → quality manager

An LLM-as-judge, versioned in LangFuse like every other prompt. It has two roles and graduates from one to the other **per task-type**.

### Scoring is real-time; calibration is batch
- **Scoring:** event-driven. A task completes → judge scores it → score + per-dimension breakdown + a one-line "why" land on the card and the LangFuse trace **immediately**. You see it right away.
- **Calibration:** a weekly cron compares judge score vs. your annotations on the same cards → agreement %. Divergence is the signal: either the rubric is wrong (edit the judge prompt) or output genuinely varies. You review and accept the change. The judge improves through the loop, not through training.

### Phase A — Shadow (advisory)
Judge scores every output and writes score + notes to the card/trace. **Takes no action.** The read-only manager looking over the shoulder. You read the scores; calibration accrues.

### Phase B — Manager (gating)
Once agreement on a task-type crosses threshold, the judge graduates **for that type**: if score < threshold, it bounces the output back for revision **before it lands**.

**How revision works (this is the key mechanic):**
- The revision is **inline, inside the same task execution**: `generate → critique → revise`, bounded to 1–2 passes.
- The worker keeps full context naturally — the critic is a **sub-step of the run**, not a separate later agent. No cross-invocation memory problem.
- The trace records draft-v1, the critique, draft-v2.

The judge does **not** silently fix-and-merge (destroys the signal) and does **not** annotate-and-walk-away once it's a manager. The portfolio judge (scoring landed cards for calibration + the self-improvement loop) is the stateless, after-the-fact measurement layer using the same rubric.

**Done when:** every card carries a quality score on completion, and at least one task-type has graduated to inline gating with measured human agreement.

---

## 3. Capability tiers + autonomy promotion

Today nothing in the system *stops* an agent task from taking a real-world action without approval — it's safe only because agent tasks currently just write reports. As task-types promote to autonomous and start *doing* things, we need an enforced guardrail.

### Blast-radius tiers (declared per worker, checked — not convention)
- **Tier 0 — read-only:** research, Pendo / Databricks queries
- **Tier 1 — writes local:** reports, drafts, files in the repo
- **Tier 2 — writes external:** Jira publish, send doc, calendar, email

**Rule:** Tier 2 **always** routes through `collab` for approval, regardless of how autonomous the task-type is, until that specific action is explicitly graduated. A worker literally cannot publish to Jira without landing in collab unless graduated.

### Promotion ladder
**report → scored report → autonomous action**, one task-type at a time:
1. Reports prove the worker (safe — a report can't break anything).
2. The judge proves the quality.
3. Calibration proves the judge (high judge-vs-human agreement on that type).
4. *Then* the action graduates.

**Promote** a task-type when, over a rolling window (~last 10 runs): your approval rate of its collab proposals is high (>~90% accepted unmodified) **and** judge-vs-human agreement is high.

**Reversible:** the judge keeps scoring autonomous output. If scores drop, or a spot-check disagrees with the judge → **automatic demote** back to collab. A trust budget per task-type: up with agreement, down with surprises.

**Done when:** Tier 2 actions are blocked from autonomous execution by the system (not by habit), and at least one task-type has graduated through the full ladder.

---

## 4. Rocks as the reference workflow

`metric-quarterly-rocks` + `update_rocks_xlsx.py` is the most concrete recurring agent job (Q2 2026: Home WAU and Board Member Weekly Login Rate). Harden it as the canonical pattern: byte-reproducible, scored by the judge, cron-driven, exception-review only.

**Done when:** the weekly Rocks run requires zero manual touch and you review only the delta.

---

## 5. Consolidate, don't expand

~60 skills is past the point where coverage is the problem — overlap and drift are. `meta-refine-workflow` + `quality-documentation-sync` exist for exactly this.

**Rule:** prune / merge before adding. Every skill earns its slot.

**Done when:** the 6-file documentation-sync gate passes clean and no two skills cover the same trigger.

---

## 6. Product-area squads

Once 1–3 hold, organize workers into **mini squads by product area** (e.g., Home, Board Member portal). Not a scrum team — a small cross-functional crew whose job is **monitoring and addressing the customer / user experience** for its area.

**Squad roles (agents):**
- **Product** — watches the area's UX signals, triages, frames problems, drafts PRDs/proposals
- **Support** — surfaces and synthesizes customer pain (Zendesk, Gong, Pendo Listen)
- **QA** — validates behavior, catches regressions, checks against definition-of-done
- **Dev (optional)** — squashes bugs / drafts fixes for the small stuff

**Mostly it's about watching the experience:** Pendo usage + session replays, support tickets, sales-call signal — the squad triages what's degrading for users in its area, drafts the response (ticket, fix, PRD update), and escalates to you what needs a decision.

**Shared squad context:** its own backlog slice, `voice.md`, roadmap context, and definition-of-done. A pod-lead orchestrator routes work across the squad. The self-improvement loop (#1) runs scoped to the squad as its "retro."

**Done when:** one product area runs as a squad that detects a real UX issue, drafts the response, and escalates the decision — end to end.

---

## First 10 crons

The load-bearing recurring jobs (grows to ~20 over time):

1. **Rocks metrics refresh** — weekly; Home WAU + Board Member login rate (reference workflow)
2. **Human-queue audit** — weekly; finds human tasks an agent could own, messages an agent could draft, and stale tasks to kill → proposes each as a one-tap recommendation. The self-improvement loop pointed at task *routing*; keeps the human pile from forming. See `UX_VISION.md`. **Highest QoL priority.**
3. **Meetings-to-backlog** — nightly; new transcripts → signals / PRD proposals
4. **Shadow judge pass** — scores cards completed since last run *(note: per-card scoring is event-driven; this is the backfill/sweep)*
5. **Feedback-loop improvement pass** — weekly; low scores → collab proposals
6. **Judge calibration** — weekly; judge-vs-human agreement report, flags drift
7. **qmd index refresh** — nightly (`qmd-nightly-update.sh`)
8. **Task hygiene sweep** — stale `waiting` / `in-progress` → inbox
9. **Customer signal digest** — weekly synthesis by customer, QBR-ready
10. **Support / sales signal digest** — weekly; Zendesk + Gong via Databricks
11. **Doc-sync reconciliation** — agent-output → Word / SharePoint, detect drift

*Later (12–20): research expiry sweep, recruiting pipeline status, north-star weekly, cron self-audit, Jira draft reconciliation, competitive watch.*

---

## Open questions

- **Gating threshold** — one global bar, or per-tier? Leaning per-tier, with Tier 2 stricter than Tier 1.
- **Promotion event** — auto or human sign-off? Leaning: criteria can be met automatically, but the *flip to autonomous* is always one `collab` card you approve.
- **Judge rubric** — one shared rubric, or per-task-type? Leaning shared base + per-type overlay.

---

## Explicitly out of scope

- **Dispatch outside headless / cmux bridge** — different use cases, different feedback loops. cmux is active work; pm-os is automation. They stay separate.
