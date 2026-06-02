---
name: task-human-queue-audit
description: Use when reviewing the human/waiting task pile (weekly cron or on demand) — finds tasks an agent could own, messages an agent could draft, and stale tasks to kill, and proposes each as a one-tap recommendation. The chief-of-staff pass that keeps the human pile from forming.
allowed-tools: Read, Grep, Glob, Bash
---

# Human-Queue Audit

## Purpose

The human and waiting queues pile up because most tasks land there **by habit, not necessity**. This skill is the chief-of-staff weekly pass over that pile: it reads every open human/waiting task and proposes, for each, the cheapest honest disposition — **convert to an agent task**, **let an agent draft the message** so the human action collapses to *send*, **schedule a meeting**, or **kill/snooze** what has gone stale. Nothing auto-applies; the output is a digest of one-tap recommendations you accept or reject.

This is the self-improvement loop (`ROADMAP.md` #1) pointed at task *routing* instead of skills, and the engine behind the **People** lane in `UX_VISION.md`. It is **cron #11**.

## When to Use

Activate when:
- The weekly human-queue audit cron fires (`creator: cron`, tagged `human-audit`)
- Jay asks "why are my human tasks piling up?" / "what can be automated off my plate?" / "clean up my human queue"
- Reviewing the human/waiting queues during planning

Do NOT use when:
- Creating a single task (`task-create`) or completing one (`task-complete`)
- Auditing agent-output quality — that is the judge's job, not this skill

## Core Principle

**Human by habit ≠ human by necessity.** A task only truly belongs to a human when it needs Jay's body, voice, judgment, relationships, or credentials. Everything else is delegable — either fully (→ agent) or down to a single approval (→ agent drafts, Jay sends). Be aggressive about proposing delegation; Jay rejects what he disagrees with. A pass that proposes nothing has failed.

## Workflow Steps

### 1. Pull the pile

```bash
./scripts/task.sh list --queue human --status open --json
./scripts/task.sh list --queue waiting --json
```

For any task whose intent is ambiguous, read it fully:

```bash
./scripts/task.sh show TASK-NNNN
```

### 2. Classify each task

Assign exactly one disposition per task:

| Disposition | Signal | Recommended move |
|---|---|---|
| **Convert → agent** | Produces an artifact or information: *draft, write, research, summarize, analyze, compare, outline, prepare, review-and-note* | Re-queue as `agent` (or `collab` if it touches an external system) |
| **Draft the message** | A communication: *send, email, message, follow up with, ask, reach out, ping, request from, reply to* | Agent drafts the Teams/email via M365; re-queue as `collab` so Jay reviews + sends. Sending is Tier-2 external → approval required |
| **Schedule it** | "Talk to / connect with / sync with someone" | `collab` + `--task-type schedule-meeting` (per `task-create`) |
| **Kill / snooze** | Stale: open > 7 days, no activity, no near-term due date; or overtaken by events | Propose cancel, or snooze with a concrete revisit date |
| **Keep (truly human)** | Needs Jay's physical presence, voice, credentials, signature, a relationship-sensitive touch, or a decision only he can make | Leave in `human`; note *why* it's irreducible |

Staleness check: compare `created` / `updated` against today (`2026-06-02` at write time; use the real current date at run time). Flag waiting tasks past `waiting_expected` as **nudge candidates** — propose an agent-drafted follow-up to the person owed.

### 3. Be honest about "Keep"

Resist over-converting. These stay human:
- Synchronous / relationship-sensitive conversations (a hard 1:1, a delicate customer call)
- Decisions only Jay owns (budget approval, hiring call, strategy pick, anything he signs)
- Actions requiring his credentials or physical presence

For each Keep, state the one reason it's irreducible. If you can't name one, it's not a Keep.

### 4. Emit the digest

Write a single markdown digest to `datasets/product/agent-output/human-queue-audit-{date}.md`:

- **Headline:** counts by disposition (e.g., "12 human tasks: 4 convert, 3 draft, 2 schedule, 2 kill, 1 keep")
- **A table:** TASK-ID · title · age · disposition · one-line rationale · the exact `task.sh` command to enact it
- **Pile trend:** size of the human/waiting pile vs. the previous audit if a prior digest exists (Glob `human-queue-audit-*.md`)

Default to **one rollup digest**, not N cards — avoid recommendation spam. Only spawn an individual `collab` card (via `task-create`) for a **high-confidence, unambiguous conversion** where the one-tap action is obvious. Never enact a conversion, kill, or send directly — this skill **proposes**; Jay disposes.

### 5. Close out (headless)

When run as a cron-dispatched agent task:

```bash
./scripts/task.sh agent:complete TASK-NNNN --output "datasets/product/agent-output/human-queue-audit-{date}.md"
```

## Scheduling (cron #11)

Paste-ready text for the Cron tab (Haiku parses it into a job):

> Every Monday at 7:47 AM, audit my human and waiting task queues. Find tasks an agent could take over, messages an agent could draft so I just send, meetings I should schedule, and stale tasks to kill. Write a digest of recommendations to agent-output. Don't change anything — just propose. Tag it human-audit.

Off-hour minute offset (`:47`) follows the cron-parser convention. Weekly cadence keeps the pile from compounding without nagging.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Proposing nothing ("looks fine") | A piling-up queue always has delegation opportunities — find them |
| Over-converting irreducibly-human tasks | Name the one reason each Keep is irreducible; if you can't, convert it |
| Spawning a card per recommendation | Default to one rollup digest; individual cards only for high-confidence conversions |
| Enacting changes directly | This skill **proposes**; Jay accepts via the digest |
| Forgetting the draft for communication tasks | "Draft the message" means the agent *writes* it, not just flags it for Jay |
| Treating waiting tasks as untouchable | Past `waiting_expected` → propose an agent-drafted nudge |

## Success Criteria

- Every open human + waiting task gets exactly one disposition with a one-line rationale
- Convertible and communication tasks are surfaced aggressively; each Keep names why it's irreducible
- Output is a single skimmable digest with a ready-to-run command per recommendation
- Nothing is enacted automatically — Jay accepts or rejects each proposal
- A week's pile reliably yields a "here's what I'd convert / draft / schedule / kill" pass Jay can clear in one sitting
