# PM/Strategy LLM Workspace

A Cursor-based AI assistant system for product management and strategic decision-making. This workspace automates roadmap planning, PRD creation, strategic research synthesis, and formal decision documentation.

## What This System Does

This workspace provides three specialized AI agents (Cursor modes) for:

- **Product Planning** — Transform meeting transcripts into validated, prioritized PRDs
- **Strategic Decision-Making** — Conduct research-backed strategy sessions with framework analysis
- **Research Synthesis** — Process external sources and extract customer signals from meetings

## Agents (Cursor Modes)

### Product Strategist
Primary mode for product management workflows:
- Meeting-to-roadmap processing
- PRD creation with 6-point validation and interactive sessions
- Roadmap sequencing based on PRD timelines
- Customer success QBR preparation

### Strategy Consultant
Mode for strategic decision-making:
- Interactive strategy sessions with auto-context assembly
- Framework application (Porter's Five Forces, SWOT, Jobs-to-be-Done, etc.)
- Formal memo generation with citation compliance
- Evidence-based recommendations

### Research Analyst
Mode for research and context gathering:
- External source processing (URLs, PDFs, notes)
- Research library management by strategic topic
- Meeting signal extraction and synthesis
- Source freshness and expiry management

## Directory Structure

```
datasets/
├── meetings/           # Meeting transcripts (Customers/ and Internal/)
├── product/            # PRDs, backlog, roadmap, customer briefs, templates
│   ├── prds/           # PRD specifications by year
│   └── templates/      # PRD template
├── research/           # Strategic research by topic
└── strategy/           # Sessions, memos, and archives

.cursor/
├── modes.json          # Agent definitions
└── rules/              # Workflow and quality rules
```

## Key Workflows

### Product Planning
```
Meeting Transcripts → Signal Extraction → Theme Clustering → 
PRD Drafting → 6-Point Validation → Roadmap Update
```

### PRD Creation (Interactive)
```
Core Identity → Ownership (DACE) → Objectives → Scope → 
Requirements → Timeline → Links/Resources → Metrics → Validation
```

### Strategy Sessions
```
Decision Question → Research Gathering → Meeting Synthesis →
Framework Application → Option Analysis → Trade-offs → Recommendation → Memo
```

### Research Processing
```
External Source → Structured Format → Key Insights → 
Citation-Ready Quotes → Topic-Organized Storage
```

## Quality Standards

### PRD Validation (6-Point Rubric)
All PRDs must pass before becoming Actionable:
1. **Objectives Clear** — Customer statement (I am / I'm trying to / But / Because / Which makes me feel)
2. **Use Cases Defined** — In-scope and out-of-scope items documented
3. **Requirements Structured** — Organized by milestone with P0/P1/P2 priorities
4. **Timeline Present** — Milestones and expected delivery dates
5. **Success Measurable** — Metrics and opportunity sizing defined
6. **DACE Assigned** — Driver, Approver, Contributors, Escalation Path

### PRD Statuses
| Status | Meaning |
|--------|---------|
| 🚧 Drafting | Incomplete, do not rely on content |
| 🏃 Actionable | Eng has agreed there's enough to start |
| 🔒 Closed | Represents what was finally delivered |
| ❗ Abandoned | Project cancelled or superseded |

### Citation Compliance
- All factual claims require sources
- Verbatim quotes (5-25 words) for key insights
- No "(source needed)" markers in final output

### No Fabrication Policy
- Leave sections blank/TBD rather than making up information
- PRDs are living documents that evolve with discovery
- Only include information that has been provided or sourced

## Research Topics

| Topic | Contents |
|-------|----------|
| `competitive-analysis` | Competitor intelligence, market positioning |
| `pricing-strategy` | Pricing models, value-based pricing |
| `market-positioning` | Brand positioning, customer segments |
| `product-strategy` | Feature prioritization, roadmap direction |
| `customer-segmentation` | Personas, behavioral analysis |
| `growth-strategy` | Acquisition, retention, expansion |

## Getting Started

### 1. Select a Mode
Choose the appropriate Cursor mode for your task:
- **Product Strategist** for roadmap and PRD work
- **Strategy Consultant** for strategic decisions
- **Research Analyst** for research and synthesis

### 2. Example Prompts

**Product Work:**
- "Process meetings from the last 7 days into PRD proposals"
- "Create a PRD for [feature] based on customer signals"
- "Prepare a QBR brief for [Customer]"

**Strategy Work:**
- "Start a strategy session on pricing-strategy"
- "Generate a memo from the current session"
- "Apply Jobs-to-be-Done to our product roadmap"

**Research Work:**
- "Gather research on competitive-analysis"
- "Process [URL] as a pricing-strategy source"
- "Synthesize meeting signals from last 30 days"

## Documentation

- **[AGENTS.md](./AGENTS.md)** — Agent descriptions and example prompts
- **[.cursor/rules/](/.cursor/rules/)** — Workflow and quality rule definitions
- **[datasets/product/templates/prd-template.md](./datasets/product/templates/prd-template.md)** — PRD template

## Configuration

This system uses Cursor's native configuration:

- **`.cursor/modes.json`** — Agent/mode definitions
- **`.cursor/rules/*.mdc`** — Workflow rules and quality gates

## Scope

This system focuses on:
- ✅ Product strategy and management
- ✅ PRD/spec creation with interactive sessions
- ✅ Backlog and roadmap management
- ✅ Meeting and research synthesis
- ✅ Strategic decision documentation

Intentionally excluded:
- ❌ Marketing/content creation workflows
- ❌ Learning/flashcard management
- ❌ SEO and content optimization

## Origin

This system was translated from an original Claude/Superpowers LLM framework to use Cursor's native configuration format. The workflows, quality standards, and agent behaviors were preserved during the translation.
