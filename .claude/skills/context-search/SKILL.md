---
name: context-search
description: Unified semantic + keyword search across all PM-OS datasets (meetings, research, product artifacts, tasks). Use when you need to find relevant context across collections without knowing which dataset contains it.
allowed-tools: Bash, Read, mcp__qmd__query, mcp__qmd__get, mcp__qmd__multi_get
---

# Context Search

## Purpose

Cross-dataset search using qmd hybrid search. Finds semantically relevant content across:
- Meeting transcripts (product, leadership, general, strategy, recruiting)
- Research library
- Product artifacts (PRDs, epics, backlog, roadmaps)
- Active tasks

## When to Use (and Why This Over Grep)

- User asks "what do we know about X"
- User runs `/search <query>`
- Any workflow needs cross-dataset context before knowing which dataset is relevant
- You want to surface related signals from multiple datasets in one pass

### Why semantic search, not grep

**Use qmd (this skill) when:**
- Searching meeting transcripts — people say "it's really slow" not "performance degradation." Semantic search catches conceptual matches that grep misses entirely.
- Exploring a topic you don't know the exact vocabulary for — qmd understands meaning, not just character patterns.
- Searching across multiple datasets at once — one query spans meetings, research, product artifacts, and tasks.
- Looking for themes or patterns — "customer frustration with setup" will find onboarding complaints phrased dozens of different ways.

**Use grep/Glob when:**
- You need an exact string (a customer name, a specific error message, a task ID).
- You need structural matches (YAML frontmatter fields, specific markdown headings).
- qmd is unavailable (binary not found or index not built).

**Rule of thumb:** If the query is a concept or question, use qmd. If the query is a literal string, use grep.

## Inputs

- `query` (required): The search query in natural language
- `--collection <name>` (optional): Restrict to one collection
- `--mode semantic|keyword|hybrid` (optional, default: hybrid)
- `--research` (optional flag): Research mode — auto-reads top results and returns extracted content ready for synthesis. Designed for agent-to-agent use where the caller needs content, not file pointers.
- `--top N` (optional, default: 5): Number of top results to auto-read in research mode.

## Execution

### Search Mode Selection

| Situation | Command | Why |
|-----------|---------|-----|
| Default — any topic/concept search | `qmd query` | Hybrid (BM25 + vector + reranking). Best quality. Handles both exact terms and semantic meaning. |
| Quick lookup — you know the exact terms | `qmd search` | BM25 keyword only. Fastest. No model overhead. Good when you already know what words appear in the document (e.g. "QCC q2", a customer name). |
| Conceptual/fuzzy — no exact terms known | `qmd vsearch` | Pure vector semantic search. Best when the query is a concept and you don't know how it's worded in the source (e.g. "feedback about career growth"). |

**Default to `qmd query`** (hybrid) unless you have a reason to use a faster/narrower mode. The MCP `query` tool always uses hybrid mode.

### Step 1: Run the Search

**Prefer MCP tools when available, Bash as fallback.**

**MCP (preferred):**
Use `mcp__qmd__query` tool with appropriate search configuration. Pass the query and optional collection/limit parameters.

**Bash fallback — default hybrid search across all collections:**

```bash
qmd query "<query>" --json -n 10
```

**Collection-scoped:**
```bash
qmd query "<query>" -c <collection_name> --json -n 10
```

**Keyword-only (fast, exact terms):**
```bash
qmd search "<query>" --json -n 10
```

**Semantic-only (meaning, not terms):**
```bash
qmd vsearch "<query>" --json -n 10
```

> **Fallback:** If qmd exits non-zero or binary not found, log "qmd unavailable" and respond that search requires qmd to be installed. Run `which qmd` to confirm availability.

### Step 2: Parse and Label Results

For each hit in the JSON response:
- Extract: `file`, `score`, `snippet`, `title`
- Map `file` path prefix to dataset label:

| Path prefix | Label |
|-------------|-------|
| `qmd://meetings_product/` | Product Meetings |
| `qmd://meetings_leadership/` | Leadership Meetings |
| `qmd://meetings_general/` | General Meetings |
| `qmd://meetings_strategy/` | Strategy Meetings |
| `qmd://meetings_recruiting/` | Recruiting Meetings |
| `qmd://research/` | Research Library |
| `qmd://product_artifacts/` | Product Artifacts |
| `qmd://tasks/` | Tasks |

**If `--research` flag is set, skip Steps 3-4 and go to Research Mode below.**

### Step 3: Format Output (Display Mode)

Present results as:

```
## Search: "<query>"

### [RANK]. [Dataset Label] — [Title]
Score: [score] | File: [file]
> [snippet]

---
```

Group by dataset label if 3+ results from same collection. Show top 10 results total.

### Step 4: Offer Follow-Up Actions (Display Mode)

After results, offer:
- "Read full document: `qmd get <file>`"
- "Synthesize signals across results"
- "Search within a specific collection: `qmd query '<query>' -c <name>`"
- "Run with embeddings for semantic search: `qmd vsearch '<query>'`"

---

## Example: qmd Query JSON Response

When you run `qmd query "onboarding friction" --json -n 3`, the response looks like:

```json
{
  "hits": [
    {
      "file": "qmd://meetings_product/home/2026/2026-03-12_product_home-squad-standup.txt",
      "score": 0.847,
      "title": "Home Squad Standup - Onboarding Discussion",
      "snippet": "...the onboarding flow is causing a lot of drop-off. Three customers this week mentioned they couldn't figure out how to connect their first data source..."
    },
    {
      "file": "qmd://product_artifacts/epics/2025/onboarding-revamp-v2.md",
      "score": 0.723,
      "title": "Epic: Revamp Onboarding to Reduce TTFV",
      "snippet": "...Problem: Time-to-first-value exceeds 14 days for 60% of new accounts. Users abandon setup at the data connection step..."
    },
    {
      "file": "qmd://meetings_general/2026/2026-02-28_general_cs-sync.txt",
      "score": 0.691,
      "title": "CS Sync - Customer Feedback Roundup",
      "snippet": "...CompoundStudio said onboarding took them three weeks, which is way too long. They almost churned before getting value..."
    }
  ],
  "query": "onboarding friction",
  "total": 3,
  "collections": ["meetings_product", "product_artifacts", "meetings_general"]
}
```

---

## Research Mode (`--research` flag)

When `--research` is passed, skip Steps 3-4 (display formatting) and execute this extended pipeline. Research mode is designed for agent-to-agent use: the calling workflow gets pre-read content in one pass with no follow-up reads needed.

### Research Step 1: Search (same as Step 1)

Run the search as normal. Prefer MCP tools if available:

**MCP (preferred):**
Use `mcp__qmd__query` with the query. For broad topic research, use natural language. For specific terms plus concepts, combine approaches.

**Bash fallback:**
```bash
qmd query "<query>" --json -n 10
```

### Research Step 2: Auto-Read Top N Results

For the top N results (default 5, configurable via `--top`):

**MCP (preferred):**
Use `mcp__qmd__get` for each result file path. For efficiency when results span few collections, use `mcp__qmd__multi_get` with comma-separated paths.

**Bash fallback:**
```bash
qmd get <file_path>
```

For each document, extract:
- **Title** (from frontmatter or first heading)
- **Date** (from frontmatter `date:` field or filename)
- **Relevance score** (from search results)
- **Key content**: AI Summary section if present (preferred for transcripts), otherwise Key Insights section (for research), otherwise first 200 lines
- **Verbatim quotes** relevant to the search query
- **Source path**: Full `qmd://` path for citation

### Research Step 3: Return Structured Bundle

```markdown
## Research Results: "<query>"
**Results found**: N | **Documents read**: M | **Collections**: [list]

---

### 1. [Title] ([Date])
**Source**: `qmd://collection/path/to/file`
**Relevance**: [score]

**Content:**
[Extracted summary or key content from the document — 100-300 words]

**Key quotes:**
> "[Verbatim quote relevant to the query]"

---

### 2. [Title] ([Date])
[... same structure ...]

---

## Cross-Document Patterns
[2-3 bullet points identifying themes, contradictions, or gaps across results]
```

### Research Mode Notes
- The caller does NOT need to do follow-up `qmd get` or `Read` calls — content comes back in one pass
- If fewer than N results are returned by search, read all of them
- For meeting transcripts: prioritize the `## AI Summary` section over `## Full Transcript`
- For research sources: prioritize `Key Insights` and `Strategic Applications` sections
- For product artifacts: include the full document if short, or the problem statement + key decisions if long

### Example: Research Mode Output

```markdown
## Research Results: "auth strategy for API platform"
**Results found**: 8 | **Documents read**: 5 | **Collections**: meetings_leadership, meetings_product, product_artifacts

---

### 1. Leadership Sync (2026-03-23)
**Source**: `qmd://meetings_leadership/2026/2026-03-23_leadership-sync.txt`
**Relevance**: 0.88

**Content:**
Trisha identified API permissions framework as the top priority for the new platform PM hire.
Concern: sophisticated customers requesting full API access to build their own agents, bypassing
the product. Stan AI already building on Vantaca APIs. Direction: be "very opinionated" about
which APIs are externally usable vs. internal-only as the system becomes headless.

**Key quotes:**
> "That is like the one of the first things I would go tell Zach he needs to go figure out before we do anything else."

---

### 2. CMP API Improvements — Prioritization (2026-03-09)
**Source**: `qmd://meetings_product/platform/2026/2026-03-09_cmp-api-improvements.txt`
**Relevance**: 0.79

**Content:**
Discussion of authentication model for search index API. Currently using system user accounts
that bypass permission checks. Team debated whether to enforce granular permissions or maintain
system-level access for backend operations. No resolution — flagged for platform PM to own.

**Key quotes:**
> "The permission check validates system user access but can be bypassed when using the system user account for backend operations."

---

## Cross-Document Patterns
- Auth/permissions consistently identified as top priority by leadership, but no design exists yet
- Current system uses god-mode system accounts — recognized as a risk but no one owns the fix
- External API exposure is both a competitive threat and a customer demand
```

---

## Notes

- `qmd query` is hybrid (BM25 + reranking) but requires LLM models (downloaded on first use).
- `qmd search` is pure BM25 — always available, no model download needed.
- `qmd vsearch` requires vector embeddings to be built (`qmd embed`).
- Collection names: `meetings_product`, `meetings_leadership`, `meetings_general`, `meetings_strategy`, `meetings_recruiting`, `research`, `product_artifacts`, `tasks`

---

## Complementary MCP Data Sources

qmd searches local PM-OS datasets (meetings, research, product artifacts, tasks). For live external data not indexed locally, complement with MCP sources:

| Need | MCP Tool | Example |
|------|----------|---------|
| Product entity search | `mcp__claude_ai_Pendo__searchEntities` (subId: `4818486697721856`) | Find pages, features, guides by name/concept |
| Customer feedback search | `mcp__claude_ai_Pendo__get_feedback_items` with `similaritySearchTerms` | Semantic search across Pendo Listen feedback |
| Gong transcript search | Databricks: `SELECT sentence FROM is_prod.gongio.transcript WHERE sentence LIKE '%{terms}%'` | Keyword search in sales call transcripts |
| Zendesk ticket search | Databricks: `SELECT subject, description FROM is_prod.zendesk.ticket WHERE subject LIKE '%{terms}%' OR custom_intent LIKE '%{terms}%'` | Search support ticket subjects and intents |
| Engineering work items | Databricks: `SELECT title, state FROM is_prod.azure_devops.work_item WHERE title LIKE '%{terms}%'` | Find related ADO work items |

**When to supplement**: If qmd results are sparse or the query involves sales/support/product analytics data that wouldn't be in local meeting files or research docs, try the MCP sources above.
