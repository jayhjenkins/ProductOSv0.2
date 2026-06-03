# PM-OS UX Vision

> Living document. The companion to `ROADMAP.md`: the roadmap says where the **system** goes, this says how the **experience** should feel as it gets there. Anchored to what's on disk today (the task board at `ui/task-board/index.html`, the task/cron engine, LangFuse wiring) and to where the roadmap is taking it (shadow judge, self-improvement loop, capability tiers).

**Last updated:** 2026-06-02

---

## Thesis: the system is a chief of staff

Everything below serves one relationship. PM-OS is not a task board you operate; it is a **chief of staff** that does the legwork, triages the inbox, drafts the messages, watches quality, and walks into your office with only two kinds of things:

- **"Here's what I need you to decide or own."**
- **"Here's what I already handled, FYI."**

A good chief of staff is measured by how little of your attention they waste and how much you trust what crosses your desk. That is the whole design goal. Today's board fails it in a specific way, and the fix is a single reframe.

---

## The core reframe: organize by demand on you, not by who executes

Today the board's primary axis is the **queue** — Human / Supervised / Agent / Waiting. That is a division-of-labor model: it answers *who does the work*. It was the right lens while **building** the system. It is the wrong lens for **living in** it.

When you sit down, you never think "let me check the agent queue." You think: *what needs me, what did the machine already handle, and can I trust it.* The pile-up is the symptom; the cause is that the board makes everything compete for your attention equally, whether or not it actually wants anything from you.

**The move:** make *"what does this want from me?"* the primary axis. The four queues stay exactly as they are in the **data** (they model who executes, which is real). They stop being how you **look** at the work.

---

## Two kinds of work

There are only two, and they are different animals:

1. **Machine work** — the agent already did it. By the time you look, it is past tense. Your relationship to it is *after the fact*.
2. **People work** (human + waiting) — depends on a person doing something in the real world, and that something is almost always **a message**: send a follow-up, ask for help, make a request, chase a reply. This is the work that actually *lives in time and piles up.*

There is no meaningful "in flight" lane. Agents run near-real-time; "running" is a transient micro-state on a card, not a place you visit. The only genuinely live, temporal work is People work.

---

## Inside machine work: accountability is the gate

Not all agent work is a receipt. It splits by **what you are on the hook for**:

- **Artifacts you are accountable for** — research, plans, PRDs, docs, memos, analysis. These are **Review, always.** Your name is on the PRD; it becomes real software downstream; you must read it before it counts. This is not an exception stream — it is the *core of your day* on the machine side.
- **Actions already taken** — published to Jira, sent a message, refreshed a metric, wrote a file. These are **Receipts.** Past tense, reversible, confirm-or-undo.

The dividing rule:

- **Accountability** decides whether something can *ever* be a receipt. Artifacts you sign → **permanent Review**. No quality score retires that read. **Trust can automate the *doing*; it cannot transfer the *accountability*.**
- **Blast radius + reversibility** decides receipt *eligibility* among actions.
- **The judge** routes *attention depth* (skim a 9, scrutinize a 5), never *whether* you look.

The Task → Receipt migration in the roadmap's promotion ladder applies **only to the action class**. A PRD-drafting task-type can become fully trusted to *produce well* and still land in Review forever, because you own the outcome. That is not a gap in automation — it is the line automation should not cross.

---

## Tasks vs. Receipts (the two card kinds)

A first-class distinction in the data, not just the display:

- **A Task** is *future tense*: "Do X." It demands you. It may legitimately pile up — each one wants something.
- **A Receipt** is *past tense*: "Did X. Here's what changed. Here's the score. Confirm / Undo." Its default state is *fine*. It wants a skim, then auto-archives after N days unless flagged.

A receipt carries exactly three things: **what it did** (the diff / what changed), **whether it's done well** (judge score + one-line why), and **one reversible affordance** (Undo / Flag). As a task-type graduates report → scored report → autonomous action, its card *changes tense* — from Review (artifact you bless) or Decide (action you pre-approve) to a Receipt you confirm after. **The promotion ladder is literally visible as where a card-kind lands on your screen.**

---

## The judge is the attention router

The roadmap's shadow judge is not only a quality gauge; it is what keeps the machine pile from forming. Because it scores *everything* — agent artifacts, message drafts, approval recommendations — it decides **how much of your attention each item deserves**:

- **Action, high score, low tier** → auto-Receipt. You never had to touch it.
- **Anything low-scored** → pulled into your lane with "judge flagged this." *This* wants your eyes.
- **Artifact you're accountable for** → Review regardless of score; the score sets *depth*, not *whether*.
- **Tier 2 external action** → always surfaces for approval; blast radius trumps confidence.

So Review stays the heavyweight daily lane (artifacts you must bless, depth-sorted by the judge), and Activity is the skim lane (actions that already happened). The eval work and the UX work are the same project: the judge is the thing that makes the board calm.

---

## People work is communication — so draft it or convert it

Human and Waiting are one category: *things involving other people that aren't done*, executed through Teams or email. This is the pile that actually hurts, and most of it is human **by habit, not necessity.** Two attacks:

1. **Convert.** Many "human" tasks — draft a follow-up, research X, summarize, write the request — were never human tasks. An agent owns them.
2. **Assist the ones that stay human.** If it's "send a message," the agent **drafts it** (Teams / email via the M365 MCP already used for scheduling), the judge scores the draft, and your action collapses to *review + send*. Sending is a Tier-2 external action, so it routes through approval per the roadmap.

A People-work card should rarely be a naked "Jay, go do this." It arrives with a draft attached and a one-tap send, or it has already been promoted to an agent task. The planned weekly **human-queue audit** (cron #2 in `ROADMAP.md`) is the engine that keeps this pile from forming.

---

## The briefing is a recommendation feed, not a readout

Counting what you can already see is noise. The top of the board is the chief-of-staff's morning standup: **a short stack of proposed actions, each one-tap.**

- *"TASK-0123 (human) has sat 7 days — kill it · convert to agent · snooze?"*
- *"3 human tasks look like message drafts — let agents draft them?"*
- *"Waiting on Priya, 5 days past expected — send a nudge? (draft ready)"*
- *"Judge scored TASK-0098's output 4/10 — review before it ships."*

Every recommendation has the same shape: it is a **proposal** — from hygiene, the judge, a conversion audit, calibration drift, or an improvement-loop diff. They all empty into one surface where **the system proposes and you dispose.** That is the chief of staff made literal.

---

## Information architecture

Sort surfaces by **what they want from you** and by **cadence** (daily / weekly / rare). Three tabs that each do several jobs become two daily surfaces, one weekly gauge, two quiet config rooms.

**Daily — where you live:**

1. **Now** (default)
   - **Recommendations** (top) — the action feed. Least time, most leverage.
   - **Review** — machine artifacts you're accountable for, plus judge-flagged exceptions. Verbs: review / approve / annotate / delete. Judge score + one-line why on each, depth-sorted.
   - **People** — human + waiting, unified and communication-centric. Most items carry an agent-drafted message + send, or a convert-to-agent option. Verbs: send / ask / follow up / chase.

2. **Activity** — the receipts stream. Auto-archived actions, completed sends, what cron did. Reverse-chron, filterable by area / customer / source. Skim, don't work. **This is where completed cron output lands** — not siloed in the Cron tab, not clogging a to-do lane.

**Weekly — the machine's report card:**

3. **Quality** (today's Eval tab, split out into its own tab) — a **read-only** trust dashboard organized by task-type. Calibration itself happens per-card on the board, not here; this is where you *understand* drift and watch types climb toward graduation. Full design below.

**Rarely — config rooms:**

4. **Engine** (today's Agents tab) — workers, prompts, skills. How it's wired.
5. **Schedules** (today's Cron tab) — recurring job *definitions only*. Their runs live in Activity.

No "In Flight" lane. No four-column scan. The whole thing reduces to a sentence: **the judge triages the machine pile down to what you're accountable for, a weekly audit plus message-drafting dissolves the people pile, and whatever's left the system proposes as one-tap actions at the top of your day.**

---

## The Quality tab

Its own tab, split from **Engine**: Engine is *how the machine is wired* (workers, prompts, skills), Quality is *how well it's doing and whether it's learning*. The organizing unit is the **task-type**.

**Calibration is a free byproduct of review, not a chore.** The judge scores everything; its verdict (score + per-dimension breakdown + one-line why) rides on the card. When you review an artifact you're accountable for, your normal reaction — good / needs-work, plus an optional note — *is* the calibration signal. Agreement is the delta between your read and the judge's. You never sit down to "calibrate"; it accrues from the review you already owe the artifact. This is why calibration is **per-card and real-time**, and why the Quality tab can stay read-only.

**Three surfaces, one job each — no competing action surfaces:**

| Surface | Role | What you do |
|---|---|---|
| **Card** (on the board) | calibration input, in context | react to the output (the free signal) |
| **Quality tab** | trust dashboard, read-only | understand where and why it's drifting |
| **Now / Recommendations** | control | accept / reject rubric and promotion changes |

**What the Quality tab shows** (all read-only):
- **Scoreboard / promotion board** — a row per task-type: score trend, judge↔you agreement %, phase (Shadow / Gated), and trajectory toward graduate-or-demote. Answers "can I trust it more or less than last week" at a glance.
- **Drill into a type** — its score distribution; the **disagreement list** (the biggest judge-vs-you divergences, each linking back to the card where it happened). This is the "queue" — kept as *evidence behind the agreement %*, not a place you work.
- **The judge itself** — current rubric version + history, the draft → critique → revise traces when inline gating fired, and any **pending rubric change** shown as status ("PRD-draft: v4→v5 proposed → act on Now").

**Governance is accept/reject only.** You never hand-edit the judge prompt. When divergences cluster, the improvement loop drafts a rubric change (or a promotion / demotion) and it lands as a Recommendation on **Now**, with the diff. The judge improves through your accept/reject plus your passive per-card reactions — never through manual tuning.

**Incremental path** (the tab need not wait for the judge):
1. **Now** — aggregate the per-card reactions you already collect into the scoreboard-by-task-type. Pure read, immediate value.
2. **+ judge lands** — add the judge score column → agreement % appears → the disagreement list lights up.
3. **+ loop lands** — clustered divergences start drafting rubric-change Recommendations on Now.

### Note to explore: GEPA as the optimizer behind the judge

The judge's `(score, feedback)` output is structurally a **GEPA metric** — GEPA (reflective prompt evolution) is the one optimizer whose loop *consumes a textual feedback string*, not just a scalar, which is exactly the asset the judge already produces. Worth exploring as the engine that *drafts* the rubric-change and prompt-improvement Recommendations (you still accept/reject; never hand-tune).

Sequence and gates if pursued:
- **Classifiers first** (task / worker / cron parsing) — verifiable labels, existing golden datasets, cheap rollouts, no judge needed. Low-risk proving ground.
- **The judge itself next** — optimize against human agreement (real ground truth, not a proxy). GEPA proposes the rubric diff; you accept/reject. Fits the governance decision exactly.
- **Workers last, and gated** — only after the judge is calibrated (else the optimizer **Goodharts** it — evolves prompts that win the judge, which is only as good as the judge). Calibration crossing threshold is a hard prerequisite.

**Credit assignment is the real challenge for end-to-end work.** A single score on "is the PRD good?" can't say *which stage* failed — context gathering, reasoning, or formatting. An optimizer mutates one specific prompt, so a blob score gives it nothing to aim at. Two ways to make it tractable: (a) design the **judge's dimensions to mirror the pipeline stages** (context / reasoning / evidence / format) so failure localizes, or (b) decompose the worker into separately-scored stages. Either way, score against **trace + output**, not output alone — the judge can't tell "never gathered the evidence" from "gathered and ignored it" without the trace. The stage-aware judge is the cheaper path and is the same judge work already planned.

*Optimization runs offline/batch (a training-style job, e.g. DSPy pointed at the Anthropic API) — separate from the headless-CLI runtime dispatch. Winning prompts land in LangFuse as new versions; accept/reject promotes them to `production`. Caveat: GEPA is recent; verify the current `dspy.GEPA` API before building.*

---

## How this maps to the roadmap

- **Shadow judge (#2)** → the attention router. Per-card score + why is the load-bearing UI element; the depth-sort of Review is the judge's first job.
- **Self-improvement loop (#1)** → its output is Recommendations cards (diffs you accept). The planned human-queue audit (cron #2) is the same loop pointed at task *routing* instead of skills.
- **Capability tiers (#3)** → tier is a badge on every card and the gate for receipt-eligibility; Tier 2 always surfaces in Review/Decide. Promotion and demotion are Recommendations.
- **Product-area squads (#6)** → the lens that makes "find things" work: slice Now / Activity / Quality by product area, customer, or source.

---

## What changes in the data (evolvable, not a rewrite)

Mostly a presentation-layer reframe over the existing model, plus a few fields:

- a card **`kind`**: `task` vs `receipt`
- a capability **`tier`**: 0 / 1 / 2 (read-only / writes-local / writes-external)
- a **`judge_score`** + one-line `judge_why` (and a `revised` marker when inline gating fired)

Queues, statuses (`open / in-progress / blocked / done / cancelled`), and `agent_status` survive untouched. The board becomes a *view* that derives attention-state from (queue + status + tier + score + kind), instead of a fixed four-column map of the queues.

---

## Surfaces not yet designed

The reframe and the Quality tab are designed; these surfaces still need a design pass.

- **The Recommendations feed** — the load-bearing chief-of-staff surface. Several roadmap pieces empty into it (hygiene, judge flags, rubric changes, promotions/demotions, the human-queue audit). Needs: the card shape for a proposal, how one-tap accept/reject flows, how proposals from different sources are ranked/grouped, and what an empty feed looks like.
- **The People lane** — the draft-the-message interaction (agent drafts via M365, you review + send), and how a human→agent conversion presents on the card. Ties to "Where People drafts route" below.
- **Tier / promotion visibility** — how blast-radius badges (Tier 0/1/2) render across cards, how the promotion ladder shows a task-type climbing or being auto-demoted, and where the "graduate this?" moment surfaces.

## Open questions

- **Recommendation density** — one rollup digest card per audit, or individual one-tap cards per item? Leaning: digest by default, spawn individual cards only for high-confidence conversions.
- **Receipt retention** — how long before an unflagged receipt auto-archives? Leaning 7 days.
- **Where People drafts route** — collab queue (stage for approval) vs. a new "draft attached" state on the human card. Leaning: reuse collab (it's already the "agent preps, human acts" pattern, currently dormant).

---

## Explicitly out of scope

- **Rebuilding the board as a SPA framework.** The reframe is information architecture, not a rewrite of `index.html`. Evolve the existing vanilla UI.
- **Mobile / push notifications.** The briefing is the notification surface for now.
