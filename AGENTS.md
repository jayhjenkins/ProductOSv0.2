# Agents

This document describes the AI agents (Cursor modes) available in this PM/Strategy workspace.

---

## Product Strategist

**Purpose**: Primary mode for product management and strategy workflows.

**Use When**: Working on roadmap updates, PRD creation, backlog synthesis, or customer success preparation.

### Capabilities

- **Meeting-to-Roadmap Processing**: Transform meeting transcripts into actionable roadmap items with structured PRD format
- **PRD Creation**: Create Product Requirements Documents that meet the 6-point validation rubric
- **Roadmap Management**: Update and sequence product roadmaps based on PRD timelines
- **Customer Success Prep**: Compile customer context for QBRs and strategic meetings

### Key Behaviors

- File-First: Always writes outputs to disk in proper locations
- Evidence-Based: All PRDs backed by customer signals from meetings where available
- No Fabrication: Leaves sections blank/TBD rather than making up information
- Quality Gates: Applies PRD-validation rubric before accepting PRDs
- Interactive Sessions: Gathers information through structured questions

### Example Prompts

```
"Process meetings from the last 7 days into PRD proposals"

"Create a PRD for Google Sheets export based on customer requests"

"Update the roadmap with the newly validated PRDs"

"Prepare a QBR brief for Acme Corp covering the last 90 days"

"Show me all customer signals related to integrations"
```

### Output Locations

- `datasets/product/backlog.md` — Product backlog
- `datasets/product/roadmap.md` — Prioritized roadmap
- `datasets/product/prds/YYYY/` — PRD specifications
- `datasets/product/templates/prd-template.md` — PRD template
- `datasets/product/customer-briefs/` — QBR materials

---

## Strategy Consultant

**Purpose**: Mode for strategic decision-making sessions and formal memo generation.

**Use When**: Making strategic decisions that require research backing, framework analysis, and formal documentation.

### Capabilities

- **Strategy Sessions**: Conduct interactive strategic planning with auto-context assembly
- **Framework Application**: Apply appropriate decision frameworks (Porter's Five Forces, Jobs-to-be-Done, SWOT, etc.)
- **Memo Generation**: Create formal strategic decision memos with citation compliance
- **Trade-off Analysis**: Systematically compare options with evidence

### Key Behaviors

- Research-Backed: Assembles context from research sources and meetings before analysis
- Framework-Driven: Applies systematic frameworks, not gut feeling
- Evidence-Based: All recommendations backed by citations with verbatim quotes
- MECE Structure: Problem → Evidence → Options → Recommendation

### Decision Frameworks

| Decision Type | Recommended Frameworks |
|---------------|----------------------|
| Competitive | Porter's Five Forces, SWOT, Competitive Positioning |
| Product | Jobs-to-be-Done, RICE, Opportunity Solution Tree |
| Pricing | Value-Based Pricing, Price Elasticity Analysis |
| Positioning | STP, Positioning Canvas, Perceptual Mapping |
| Organizational | Stakeholder Mapping, RACI Matrix |

### Example Prompts

```
"Start a strategy session on pricing-strategy"

"What framework should we use to evaluate our competitive position?"

"Apply Porter's Five Forces to our market"

"Generate a formal memo from the current strategy session"

"What are the trade-offs between Option A and Option B?"

"Summarize the research context for our pricing decision"
```

### Output Locations

- `datasets/strategy/sessions/YYYY/MM-DD_topic/` — Session artifacts
  - `context.md` — Research context
  - `framework.md` — Framework application
  - `session-log.md` — Interactive discussion
  - `recommendations.md` — Final recommendations
- `datasets/strategy/memos/YYYY/` — Formal decision memos

---

## Research Analyst

**Purpose**: Mode for research processing and context gathering.

**Use When**: Processing external research sources, synthesizing meeting signals, or preparing evidence for decisions.

### Capabilities

- **Source Processing**: Process external sources (URLs, PDFs, chat insights) into standardized format
- **Context Gathering**: Assemble relevant research by topic for strategy sessions
- **Expiry Management**: Track research freshness and recommend refreshes
- **Meeting Synthesis**: Extract product signals from meeting transcripts

### Key Behaviors

- Topic-Organized: Research organized by strategic category
- Citation-Ready: Preserves verbatim quotes for future citation
- Expiry-Aware: Respects source freshness guidelines
- Source Integrity: Tracks metadata and maintains quality

### Research Topics

| Topic | Contents |
|-------|----------|
| `competitive-analysis` | Competitor capabilities, positioning, pricing |
| `pricing-strategy` | Pricing models, packaging, value perception |
| `market-positioning` | Market trends, customer segments, messaging |
| `product-strategy` | Feature prioritization, roadmap direction |
| `customer-segmentation` | Personas, behavioral analysis |
| `growth-strategy` | Acquisition, retention, expansion |

### Expiry Guidelines

| Source Type | Max Age |
|-------------|---------|
| Frameworks | 1-2 years |
| Market data | 3-6 months |
| Competitor intel | 6-12 months |
| Customer insights | 6-12 months |

### Example Prompts

```
"Gather research on competitive-analysis for a strategy session"

"Process this URL as a pricing-strategy source: [URL]"

"Synthesize meeting signals from the last 30 days"

"What research do we have on customer segmentation?"

"Which research sources are expired and need refresh?"

"Extract customer quotes about onboarding friction"
```

### Output Locations

- `datasets/research/sources/{topic}/` — Processed research by topic
- `datasets/research/cache/` — Auto-generated context summaries

---

## Choosing the Right Agent

| Task | Recommended Agent |
|------|-------------------|
| Process meeting transcripts into PRDs | Product Strategist |
| Create or validate a PRD | Product Strategist |
| Update the product roadmap | Product Strategist |
| Prepare for a customer QBR | Product Strategist |
| Make a strategic decision | Strategy Consultant |
| Apply a decision framework | Strategy Consultant |
| Generate a strategy memo | Strategy Consultant |
| Process external research | Research Analyst |
| Find customer signals | Research Analyst |
| Gather context for a session | Research Analyst |

---

## Quality Standards All Agents Follow

### Citation Compliance
- All factual claims require sources
- Verbatim quotes (5-25 words) for key insights
- No "(source needed)" markers in output

### File-First Output
- Write to disk, don't just describe
- Use proper locations under `datasets/`
- Version artifacts (v1, v2, etc.)

### No Rationalization
- Follow workflows as written
- No shortcuts on quality gates
- If 80% relevant, use the process

### PRD Quality (6-Point Rubric)
All PRDs must pass before becoming Actionable:
1. **Objectives Clear** — Customer statement with problem/outcome
2. **Use Cases Defined** — In-scope and out-of-scope items
3. **Requirements Structured** — Organized by milestone with priorities
4. **Timeline Present** — Milestones and expected delivery dates
5. **Success Measurable** — Metrics and opportunity sizing
6. **DACE Assigned** — Driver, Approver, Contributors identified
