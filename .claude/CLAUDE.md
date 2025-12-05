# ./CLAUDE.md  (TOP-LEVEL, REPLACEMENT)

# Project CLAUDE.md (Top-Level)
You are working inside a local LLM workspace that powers:
- Meeting-driven automations (roadmap updates, CS prep, case studies from transcripts)
- Study/flashcards
- Content creation (blogs, case studies, docs) with strict sourcing

Keep responses concise, reproducible, and **file-first** (write to disk). Default to **interactive prompts** when required inputs are missing.

---

## Modes & Routing
You operate in two main modes; choose based on the current working directory, invoked command, or explicit user request.

1) **Product Mode** (default outside `datasets/marketing/`)
   - Target outputs: backlog/roadmap updates, customer briefs, internal docs.
   - Preferred sources: `/datasets/meetings/**`, `/datasets/product/**`.
   - Commands: `/project:*`, `/content:*` (allowed but content rules may be relaxed unless inside marketing path).

2) **Content Mode** (inside `datasets/marketing/**` or when `/content:*` commands run)
   - Target outputs: briefs, outlines, drafts, verification reports, snippets.
   - **Non-negotiables:** Intent-first; zero-hallucination; footnote+quote per factual sentence; grade-8; no em dashes.
   - Preferred sources: `/datasets/marketing/content/**/inputs/**`, `/datasets/learning/**`, verified meeting files, and (if enabled) fetched URLs.

> If both could apply, prefer **Content Mode** when the user invokes `/content:*`.

---

## Context Map (read/write targets)
- `datasets/meetings/` — Canonical meeting notes & transcripts (markdown + YAML front-matter).
  - `Customers/{Account}/{YYYY}/...`
  - `Internal/{Function}/{YYYY}/...`
- `datasets/product/` — Product artifacts (`backlog.md`, `roadmap.md`, `customer-briefs/`, etc.).
- `datasets/marketing/` — Marketing content pipeline (briefs/outlines/drafts/verify/snippets) and templates/presets.
- `datasets/learning/` — Study notes and flashcards (`cards/`, `decks/`, `sources/`, `templates/`).
- `datasets/research/` — Competitive/market notes (freeform).
- `.claude/commands/` — Reusable commands exposed as slash-commands.

---

## Meeting File Schema (YAML front-matter)
Every meeting markdown begins with:
---
date: "YYYY-MM-DD"
type: "sales" | "product" | "customersuccess" | "onboarding" | "strategy" | "ops" | "marketing" | "general"
customer: "Company Name"
companies: ["Company A","Company B"]
participants: ["Person Name"]
granola_folder: "Sales"
granola_url: "https://…"
meeting_note_id: "uuid"
tags: ["2025Q3","keyword"]
---
**Naming:** `YYYY-MM-DD_{type}_{titleSlug}_{companyOrFunctionSlug}_{participantsSlug}.md`

**Sections**
- ## ⬇️ AI Summary — executive summary
- ## ⬇️ Action Items — bullets or checkboxes
- ## ⬇️ Full Transcript — raw text
- ## ⬇️ Links — source links

---

## Skills System (MANDATORY)

**You have a sophisticated skills-based system. Skills give you superpowers.**

### Core Mandate

**IF A RELEVANT SKILL EXISTS, YOU MUST USE IT.**

This is not optional. Finding a relevant skill = mandatory usage.

### Skill Categories

**`.claude/skills/` contains:**

**Meta Skills** (`meta/`):
- `using-skills` - Mandatory skill usage protocol (loaded at session start)
- `skill-discovery` - Find available skills
- `create-skill` - Generate new skills (test-driven)
- `refine-workflow` - Identify skill extraction opportunities

**Quality Gates** (`quality-gates/`):
- `citation-compliance` - Zero "(source needed)" tolerance
- `prd-validation` - 6-point PRD rubric enforcement
- `content-style` - Grade-8, no em dashes, word count bands
- `source-integrity` - Checksum validation, expiry management
- `link-verification` - URL accessibility, verbatim quote checking
- `meeting-schema-validation` - YAML frontmatter validation

**Context Assembly** (`context-assembly/`):
- `meeting-synthesis` - Extract signals from transcripts
- `research-gathering` - Topic-based research collection
- `priority-scoring` - Standardized ranking formula for roadmap sequencing
- `source-normalization` - Normalize files/URLs/text to citations

**Workflows** (`workflows/`):
- `content-pipeline` - Complete content creation (Intent → Snippets)
- `product-planning` - Meetings → validated PRDs
- `prd-creation` - Interactive PRD creation
- `launch-announcement` - Internal feature launch communications
- `strategy-session` - Research-backed decision framework
- `mochi-sync` - Flashcard synchronization
- [more workflow skills...]

### How Skills Work

**1. Bootstrap Hook**: On session start, `using-skills` is loaded automatically
**2. Discovery**: Skills auto-activate based on description matching task
**3. Announcement**: "I'm using [Skill Name] to [purpose]"
**4. Execution**: Follow skill exactly, no shortcuts
**5. Sub-Skills**: Workflows invoke quality gates and context assembly skills

### Slash Commands Are Thin Wrappers

**All `/content:*` and `/project:*` commands now invoke skills.**

Example: `/content:run` → Loads and executes `content-pipeline` skill

Commands tell you which skill to use. You MUST follow that instruction.

---

## Commands (Index & Expectations)
Keep commands idempotent and time-bounded by default (e.g., last 14 days) unless overridden.

**All commands now delegate to skills. See `.claude/commands/*.md` for skill references.**

**Project / Product**
- `/project:meetings-to-roadmap` → `product-planning` skill
- `/project:cs-prep` → `cs-prep` skill
- `/launch-announcement` → `launch-announcement` skill

**Content (Agentic pipeline; interactive by default)**
- `/content:run` → `content-pipeline` skill (full pipeline)
- Modular steps → Individual content skills (intent-gathering, brief-creation, outlining, drafting, verification, snippet-generation)

**Learning**
- `/project:create-notes` → `learning-notes-creation` skill
- `/project:notes-to-cards` → `learning-cards-creation` skill

---

## Content Mode — Global Guardrails (apply anywhere `/content:*` runs)
- **Intent-first:** If no `intent/intent.yaml` or inline `INTENT:` is provided, ask interactively and write it.
- **Citations:** Every **factual sentence** ends with a footnote `[^\s#]`. Each footnote must include a **5–25 word verbatim quote** in “Sources” and map to a concrete file or URL.
- **Verification:** `/content:verify` must open the referenced source and confirm the quoted fragment is present **verbatim**. Any missing/mismatched quote or `(source needed)` → **fail** the run and set `step="NEEDS_FIX"`.
- **Style:** Grade-8 readability; short sentences; skimmable sub-heads; **no em dashes**; single-line soft Raleon nudge; keep marketing claims measured.
- **Audit trail:** Every phase writes an artifact (`brief/*.md`, `outline/*.md`, `drafts/*.md`, `verify/*.md`, `snippets/*.md`) and maintains `status.json` + `progress.md`.

---

## Tools & Permissions
- Allowed by default: file read/write, directory listing, diffs, local shell ops (safe paths).
- Ask before: invoking MCP tools that modify external systems (Asana, HubSpot); deleting files.
- Prefer: create/append; keep diffs minimal and idempotent.

**MCP servers (expected)**
- Filesystem (read/write local workspace)
- Fetch (optional; only when `--web` or `web: true`)
- Time, Git (optional)

---

## Safety Rails
- Operate only within `~/Workspace/llm/`, unless explicitly instructed.
- Never overwrite large files without confirmation—prefer append or create `*-draft.md`.
- When unsure of a path, list directories first; do not guess.
- For batch operations, show a plan first and await approval.

---

## Style & Output
- Default to markdown files with clear headings.
- When summarizing, include skim-friendly bullets and dates.
- When generating artifacts, write to the path, then return a short confirmation with the file path.

---

## Command Index (Quick Links)
- Product: `/project:meetings-to-roadmap`, `/project:cs-prep`, `/launch-announcement`
- Content: `/content:run`, `/content:resume`, `/content:verify` (see `datasets/marketing/CLAUDE.md` for stricter local rules)
- Learning: `/project:create-notes`, `/project:notes-to-cards`