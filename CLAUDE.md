# CLAUDE.md

Guidance for Claude Code working in this PM-OS repository.

This is an AI-driven automation workspace for product management: meeting-driven roadmap updates, marketing content, strategic decisions, learning, and task orchestration. Workflows are decomposed into auto-discovered skills under `.claude/skills/` (flat layout — see `.claude/CLAUDE.md` for conventions).

## Workspace Layout

- `datasets/product/` — Roadmaps, backlog, PRDs, epics, customer briefs, agent-output
- `datasets/marketing/` — Content pipeline (briefs, outlines, drafts, verify, snippets)
- `datasets/research/` — External sources organized by strategic topic
- `datasets/strategy/` — Strategy sessions and formal memos
- `datasets/learning/` — Notes, flashcards, decks
- `datasets/meetings/` — Meeting transcripts (Customers/, Internal/) with YAML frontmatter
- `datasets/recruiting/` — PM hiring openings, candidate folders, assessments
- `datasets/tasks/` — Unified task queues (human, agent, collab, waiting)
- `datasets/cron/` — Recurring job definitions
- `langfuse/` — Local LangFuse Docker stack
- `scripts/workers/` — Worker definitions for agent task dispatch
- `logs/` — Automation execution logs

## Search Tool Selection

| Need | Tool | Why |
|---|---|---|
| Conceptual/topic search | `context-search` skill (qmd) | Semantic search; transcripts use conversational language that doesn't match grep |
| Exact string lookup | Grep | Customer names, task IDs, error messages |
| File structure | Glob | Find files by path pattern |
| YAML frontmatter | Grep | Structured field matching |

**Default for transcript research: qmd first.** People say "it's really slow" not "performance issue."

## MCP Data Sources

Two MCP servers supplement local datasets. Steps that use them are optional and degrade gracefully when unavailable.

- **Pendo** (`mcp__claude_ai_Pendo__*`) — product analytics, feature usage, segments, Pendo Listen feedback, session replays, AI agent analytics. Vantaca subId: `4818486697721856`. App IDs and tool reference live in the `context-pendo-analytics` skill.
- **VantacaDatabricks** (`mcp__claude_ai_VantacaDatabricks__execute_sql_read_only`) — Gong sales calls, Zendesk tickets, Azure DevOps work items. Catalog `is_prod`. SQL templates and schema reference live in the `context-databricks-analytics` skill.

## Meeting File Schema

Every meeting markdown begins with:

```yaml
---
date: "YYYY-MM-DD"
type: "sales | product | customersuccess | onboarding | strategy | ops | marketing | general"
customer: "Company Name"
companies: ["Company A","Company B"]
participants: ["Person Name"]
granola_folder: "Sales"
granola_url: "https://…"
meeting_note_id: "uuid"
tags: ["2026Q2","keyword"]
---
```

**Naming**: `YYYY-MM-DD_{type}_{titleSlug}_{companyOrFunctionSlug}_{participantsSlug}.md`

**Sections**: `## ⬇️ AI Summary` · `## ⬇️ Action Items` · `## ⬇️ Full Transcript` · `## ⬇️ Links`

## Headless Automation

Run meeting-to-backlog automation directly:

```bash
./run-meetings-to-backlog.sh
```

Headless env vars: `CLAUDE_CODE_AUTO_APPROVE_FILE_READS=true`, `CLAUDE_CODE_AUTO_APPROVE_FILE_WRITES=true`, `CLAUDE_CODE_HEADLESS=true`. Logs land in `logs/meetings-to-backlog-YYYYMMDD_HHMMSS.log`.

## Task Management

A unified task system at `datasets/tasks/` with four queues: human, agent, collab (supervised agent actions requiring human approval), waiting.

```bash
./scripts/task.sh add "Title" -q queue -p priority -d domain
./scripts/task.sh list [--queue Q] [--status S] [--json]
./scripts/task.sh show TASK-NNNN
./scripts/task.sh update TASK-NNNN --status/--priority/--queue/--comment
./scripts/task.sh done TASK-NNNN [--output path]
./scripts/task.sh inbox
```

**Awareness in interactive sessions**: The task system exists, but do NOT auto-pick tasks. The human is here to do something specific. Reference and update tasks during work if relevant.

### Agent queue execution (headless only)

Agent tasks are dispatched by `scripts/task_dispatch.py`. Each task is matched to a worker (`scripts/workers/*.md`) that defines prompt, tools, skills, and timeout. Workers scope; skills instruct.

| Worker | Matches | Tools |
|---|---|---|
| `_default.md` | Catch-all | All tools |
| `researcher.md` | "research", "analyze"; product/strategy/metrics domain | Pendo, Databricks, WebSearch, qmd |
| `product-analyst.md` | "draft", "PRD", "ship-it", "strategy", "metrics" | Pendo, Databricks, WebSearch, qmd, full ship-it pipeline skills |
| `scheduler.md` | task_type: schedule-meeting | M365 |
| `ticket-creator.md` | "jira", "ticket", "bug" | qmd (drafts only — no Jira MCP; human publishes via UI) |

When you receive a headless task assignment:
- `./scripts/task.sh show TASK-NNNN` → read the full task
- `./scripts/task.sh agent:start TASK-NNNN` → mark in-progress
- Do the work using existing skills
- Need a human decision: `./scripts/task.sh agent:ask TASK-NNNN "question"` and STOP
- Done: `./scripts/task.sh agent:complete TASK-NNNN --output "datasets/product/agent-output/your-output.md"`
- Failed: `./scripts/task.sh agent:fail TASK-NNNN --error "what happened"`

Default output location: `datasets/product/agent-output/` (auto-synced to Word/SharePoint).

### Task creation

When work needs doing during any workflow, create a task with the right queue:
- Human decisions, meetings, approvals → `human`
- Autonomous research, drafting, analysis → `agent`
- Agent acts on external systems but needs approval → `collab`
- Owed by another person/team → `waiting`

### Web UI

```bash
cd ~/pm-os && python3 scripts/task_server.py   # http://localhost:8742
```

## LangFuse (Prompt Management & Observability)

Local Docker stack for prompt versioning and tracing. All LLM calls in the task system are instrumented.

```bash
cd langfuse && ./start.sh                  # http://localhost:3000
source ~/pm-os/.env.langfuse               # repo root, NOT langfuse/ — exports LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST
```

Login: `jay@pm-os.local` / `changeme123`.

**Traced**: `parse_task_input.py` (auto via langfuse.openai wrapper, trace name `task-parser`). `task_dispatch.py` (`worker-match` and `worker-execution` per dispatch). All use `session_id=task_id`.

**Prompts in LangFuse**: `task-parser`, `worker-*` (one per worker), `cron-parser`, `cron-execution`. Skills are read from disk at runtime, not fetched from LangFuse.

```bash
python3 scripts/langfuse_setup.py            # register/update all prompts
python3 scripts/langfuse_setup.py --dry-run
```

**Scoring**: Task board Agents tab → open completed task → Pipeline section → thumbs up/down per step lands on the LangFuse trace.

**Graceful degradation**: If LangFuse is not running or `LANGFUSE_SECRET_KEY` is unset, everything falls back to inline prompts and untraced execution.

## Cron System (Recurring Agent Tasks)

Cron jobs auto-create tasks on a schedule that flow through the existing dispatch pipeline.

- UI: Cron tab on the task board (paste text → Claude Haiku parses → review → save)
- Storage: `datasets/cron/jobs.json`, atomic counter at `datasets/cron/_counter`
- Scheduler: daemon thread in `task_server.py`, 30s tick
- Template vars in titles/descriptions: `{date}`, `{week}`, `{month}`, `{year}` resolved at execution

Key files: `scripts/cron_lib.py`, `scripts/cron_scheduler.py`, `scripts/parse_cron_input.py`.

## Output Conventions

- Never delete generated artifacts — append version suffixes (`v1`, `v2`)
- Maintain `status.json` for processing state, `progress.md` for human notes
- Historical snapshots for roadmaps and decisions
- Default to markdown with clear headings; `*-draft.md` if unsure

## Tools & Permissions

- Allowed: file read/write, dir listing, diffs, local shell ops in safe paths
- Ask first: MCP tools that modify external systems (Asana, HubSpot, Jira publish), file deletion
- Prefer create/append over overwrite

## Safety Rails

- Operate within `~/pm-os/` unless explicitly instructed otherwise
- Never overwrite large files without confirmation
- When unsure of a path, list directories first
- For batch operations, show a plan and await approval
