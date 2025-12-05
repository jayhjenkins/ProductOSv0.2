# Cursor PM/Strategy System

This document describes the PM/Strategy LLM system as implemented in Cursor. This system was translated from the original Claude/Superpowers framework to use Cursor's native configuration (modes and rules).

## System Overview

This workspace provides AI-driven automation for:
- **Product development** — roadmap updates, epic creation, backlog synthesis
- **Metrics analysis** — define metrics, diagnose changes, evaluate trade-offs, design dashboards, set goals
- **Strategic decision-making** — research-backed sessions, formal memos
- **Meeting synthesis** — signal extraction, customer evidence gathering
- **Research management** — strategic context assembly, source processing

## Architecture

### Modes (Cursor Agents)

The system defines three specialized modes in `.cursor/modes.json`:

| Mode | Purpose |
|------|---------|
| **Product Strategist** | Primary mode for product management and strategy workflows |
| **Strategy Consultant** | Strategic decision-making sessions and formal memo generation |
| **Research Analyst** | Research processing and context gathering |

### Rules (Cursor Rules)

Rules in `.cursor/rules/` define workflows and behaviors:

| Rule File | Purpose |
|-----------|---------|
| `core-system.mdc` | Global behavior, file structure, safety rails |
| `product-workflows.mdc` | Epic creation, roadmap updates, product planning, CS prep |
| `metrics-workflows.mdc` | Metrics definition, diagnosis, trade-offs, dashboards, goal setting |
| `strategy-workflows.mdc` | Strategy sessions and formal memo generation |
| `research-workflows.mdc` | Research processing and context gathering |
| `quality-gates.mdc` | Epic validation, citation compliance, source integrity, documentation sync |
| `context-assembly.mdc` | Meeting synthesis, priority scoring, source normalization |

## Key Workflows

### Product Planning (meetings-to-backlog)

Transform meeting transcripts into actionable roadmap items:

1. **Meeting Synthesis** — Extract signals from transcripts
2. **Signal Clustering** — Group by theme
3. **Epic Drafting** — Structure into epic format
4. **Epic Validation** — Apply 6-point rubric
5. **Priority Scoring** — Rank with standardized formula
6. **Backlog Update** — Write to `datasets/product/backlog.md`

### Metrics Analysis

**Metrics Definition** (`/metrics:definition`):
1. **North Star Alignment** — Map to company mission and business model
2. **Funnel Mapping** — Decompose user journey into stages
3. **Proxy Selection** — Create measurable indicators
4. **Counter-Metrics** — Identify unintended effects

**Metric Diagnosis** (`/metrics:diagnosis`):
1. **4D Segmentation** — Narrow scope across People, Geography, Technology, Time
2. **Intrinsic vs Extrinsic** — Distinguish internal vs external factors
3. **Hypothesis Testing** — Build table and test against data
4. **Impact Assessment** — Evaluate North Star impact

**Trade-off Decision** (`/metrics:tradeoff`):
1. **Strategic Alignment** — Which metric matters more?
2. **Temporal Analysis** — Short-term vs long-term impact
3. **Mitigation Exploration** — Find "best of both worlds"
4. **Funnel Analysis** — Identify where problem occurs

**Dashboard Design** (`/metrics:dashboard`):
1. **North Star Anchoring** — Ground in company goals
2. **Funnel Coverage** — Ensure all stages monitored
3. **Proxy Metrics** — Define measurable indicators
4. **Review Cadence** — Set monitoring schedule

**Goal Setting** (`/metrics:goals`):
1. **Company Impact** — Assess movement needed
2. **Movability Validation** — Confirm team can influence
3. **Trade-off Evaluation** — Aggressive vs conservative targets
4. **Final Goal** — Set specific target with milestones

### Strategy Session

Conduct systematic strategic decision-making:

1. **Context Assembly** — Gather research and meeting signals
2. **Framework Selection** — Choose appropriate decision framework
3. **Framework Application** — Analyze with specific findings
4. **Option Development** — Develop concrete scenarios
5. **Trade-off Analysis** — Compare options systematically
6. **Recommendation** — Clear decision with rationale

### Strategy Memo

Generate formal strategic documentation:

1. **Content Extraction** — From session artifacts
2. **MECE Structure** — Problem → Evidence → Options → Recommendation
3. **Citation Compliance** — Validate all sources
4. **Quality Gates** — Pass all validation checks
5. **File Output** — Write to `datasets/strategy/memos/`

### CS Prep

Compile customer context for QBRs:

1. **Customer Meeting Synthesis** — Filter to specific customer
2. **Signal Organization** — Categorize wins, pain points, requests
3. **Quote Extraction** — Select impactful quotes
4. **Brief Generation** — Write to `datasets/product/customer-briefs/`

## Quality Gates

### Epic Validation (6-Point Rubric)

All epics must pass:

1. **Outcome-Oriented** — Changes user capability or business behavior
2. **Timeboxed** — Deliverable in 1-4 weeks
3. **Bounded** — Explicit in-scope and out-of-scope
4. **Actionable** — 3-6 testable acceptance criteria
5. **Non-Trivial** — Larger than ticket, smaller than initiative
6. **Evidence-Backed** — Supported by customer signals

### Citation Compliance

- All factual claims require sources
- Verbatim quotes (5-25 words) required
- Format: `[^N]: path/to/source: "Quote"`
- No "(source needed)" markers allowed

### Priority Scoring Formula

```
Score = (0.2 × SignalStrength) + (0.4 × StrategicFit) + (0.3 × Impact) - (0.1 × Complexity)
```

## Directory Structure

```
datasets/
├── meetings/           # Meeting transcripts
│   ├── Customers/      # Customer meetings by account
│   └── Internal/       # Internal meetings by function
├── product/            # Product artifacts
│   ├── backlog.md      # Product backlog
│   ├── roadmap.md      # Prioritized roadmap
│   ├── epics/          # Epic specifications by year
│   ├── customer-briefs/# QBR materials
│   └── snapshots/      # Historical roadmap versions
├── research/           # Strategic research
│   ├── sources/        # By topic (competitive, pricing, etc.)
│   ├── cache/          # Context summaries
│   └── templates/      # Source templates
└── strategy/           # Strategic decision-making
    ├── sessions/       # Strategy session artifacts
    ├── memos/          # Formal decision memos
    ├── templates/      # Memo/session templates
    └── archive/        # Completed sessions

.cursor/
├── modes.json          # Cursor mode definitions
└── rules/              # Cursor rules (.mdc files)
```

## Decision Frameworks

The system supports these frameworks for strategy sessions:

| Decision Type | Frameworks |
|---------------|------------|
| Competitive | Porter's Five Forces, SWOT, Competitive Positioning Matrix |
| Product | Jobs-to-be-Done, Opportunity Solution Tree, RICE |
| Pricing | Value-Based Pricing, Price Elasticity, Competitive Pricing |
| Market Positioning | STP, Positioning Canvas, Perceptual Mapping |
| Organizational | Stakeholder Mapping, RACI, Change Impact Analysis |

## Research Topics

Research is organized by strategic category:

| Topic | Contents |
|-------|----------|
| `competitive-analysis` | Competitor capabilities, positioning, pricing |
| `pricing-strategy` | Pricing models, packaging, value perception |
| `market-positioning` | Market trends, customer segments, messaging |
| `product-strategy` | Feature prioritization, roadmap direction |
| `customer-segmentation` | Audience targeting, personas |
| `growth-strategy` | Acquisition, retention, expansion |

## Source Expiry Guidelines

| Source Type | Max Age |
|-------------|---------|
| Frameworks | 1-2 years |
| Market data | 3-6 months |
| Competitor intel | 6-12 months |
| Customer insights | 6-12 months |

## Meeting File Schema

Meeting files use YAML frontmatter:

```yaml
---
date: "YYYY-MM-DD"
type: "sales|product|customersuccess|strategy|ops"
customer: "Company Name"
participants: ["Person Name"]
tags: ["2025Q3", "keyword"]
---
```

Standard sections:
- `## ⬇️ AI Summary` — Executive summary
- `## ⬇️ Action Items` — Bullets or checkboxes
- `## ⬇️ Full Transcript` — Raw text

## Usage

### Using Modes

Select a mode in Cursor to activate its specialized behavior:

- **Product Strategist**: For epic creation, roadmap updates, backlog work
- **Strategy Consultant**: For strategy sessions and memos
- **Research Analyst**: For research processing and context gathering

### Example Prompts

**Product Strategist:**
- "Process meetings from the last 7 days into epic proposals"
- "Create an epic for the Google Sheets export feature"
- "Prepare a QBR brief for Acme Corp"
- "Define success metrics for our new onboarding flow"
- "Investigate why weekly active users dropped 10%"
- "Should we ship this redesign with mixed A/B results?"
- "Design a product health dashboard for our driver team"
- "Set Q1 2025 goals for our engagement metrics"

**Strategy Consultant:**
- "Start a strategy session on pricing-strategy"
- "Generate a memo from the pricing session"
- "Apply Porter's Five Forces to our competitive position"

**Research Analyst:**
- "Gather research on competitive-analysis"
- "Process this URL as a pricing-strategy source"
- "Synthesize meeting signals from last 30 days"

## What's Not Included

The following workflows from the original Claude system were intentionally removed:

- **Marketing/Content workflows** — content pipeline, briefs, outlines, drafts, snippets
- **Learning/Flashcard workflows** — notes creation, cards creation, Mochi sync
- **SEO workflows** — keyword research, content optimization

The current scope is focused on:
- Product strategy and management
- Epic/PRD/spec creation
- Metrics analysis and goal setting
- Backlog and roadmap management
- Meeting and research synthesis
- Strategic decision documentation

