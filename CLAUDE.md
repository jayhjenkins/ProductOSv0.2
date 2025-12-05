# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Overview

This is a comprehensive AI-driven automation workspace for product development, marketing content creation, strategic decision-making, and knowledge management. The system uses a **skills-based architecture** where workflows are decomposed into reusable, composable skills with strict quality gate enforcement and mandatory execution protocols.

## Skills-Based Architecture

**NEW**: This system now uses a skills-based architecture inspired by the Superpowers framework.

### Skills System

**Location**: `.claude/skills/`

**Categories**:
1. **Meta Skills** - System improvement (using-skills, skill-discovery, create-skill, refine-workflow)
2. **Quality Gates** - Validation checks (citation-compliance, epic-validation, content-style, source-integrity, link-verification, meeting-schema-validation, documentation-sync)
3. **Context Assembly** - Reusable context patterns (meeting-synthesis, research-gathering, priority-scoring, source-normalization)
4. **Metrics Analysis** - Analytical thinking (north-star-alignment, proxy-metric-selection, funnel-metric-mapping, root-cause-diagnosis, tradeoff-evaluation)
5. **Workflows** - End-to-end processes (23+ workflow skills for all major operations)

### Mandatory Skill Usage

**CRITICAL**: When a relevant skill exists, YOU MUST use it. No exceptions.

- Bootstrap hook loads `using-skills` on session start
- Skills auto-discover based on task descriptions
- Slash commands are thin wrappers that invoke skills
- Quality gates are enforced within workflows
- Anti-rationalization blocks prevent shortcuts

### Slash Commands → Skills Mapping

All commands now delegate to skills:
- `/content:run` → `content-pipeline` skill
- `/project:meetings-to-backlog` → `product-planning` skill
- `/strategy:session` → `strategy-session` skill
- `/metrics:definition` → `metrics-definition` workflow
- `/metrics:diagnosis` → `metric-diagnosis` workflow
- `/metrics:tradeoff` → `tradeoff-decision` workflow
- `/metrics:dashboard` → `dashboard-design` workflow
- `/metrics:goals` → `goal-setting` workflow
- `/cards-to-mochi` → `mochi-sync` skill
- [etc for all 24+ commands]

## Core Commands

### Product Development Workflow
```bash
# Automated processing (primary method)
./run-meetings-to-backlog.sh

# Manual processing 
claude code "/project:meetings-to-backlog"
```

**Purpose**: Transform meeting transcripts into actionable roadmap items with priority scoring and structured epic format.

### Metrics Analysis Workflows
```bash
# Define success metrics for new features
claude code "/metrics:definition"

# Investigate metric changes
claude code "/metrics:diagnosis"

# Evaluate A/B test trade-offs
claude code "/metrics:tradeoff"

# Design product health dashboards
claude code "/metrics:dashboard"

# Set OKR targets
claude code "/metrics:goals"
```

**Purpose**: Apply analytical frameworks for metrics definition, root cause diagnosis, trade-off evaluation, dashboard design, and goal setting based on PM interview best practices.

### Marketing Content Pipeline
```bash
# Interactive content creation
claude code "/content:run"

# Modular approach
claude code "/content:new --type=blog"
claude code "/content:outline" 
claude code "/content:draft"
claude code "/content:verify"
claude code "/content:snippets"
```

**Content Types**: Blog posts (1000-1500 words), case studies (500-800 words), internal docs (600-1200 words).

### Research Processing
```bash
# Process external sources
claude code "/research:process-source --url='https://example.com/framework'"
claude code "/research:process-source --file='/path/to/report.pdf'" 
claude code "/research:process-source --from-chat"

# Refresh outdated research
claude code "/research:refresh --topic='pricing-strategy'"
```

**Topics**: competitive-analysis, pricing-strategy, market-positioning, product-strategy, customer-segmentation, growth-strategy.

### Strategic Decision-Making
```bash
# Start strategy session with auto-context gathering
claude code "/strategy:session --topic='competitive-analysis'"

# Generate formal memo from session
claude code "/strategy:memo"
```

**Process**: Research gathering → Framework application → Interactive planning → Memo documentation.

### Learning Card Management
```bash
# Sync flashcards to Mochi (all cards)
claude code "/cards-to-mochi"

# Sync specific topic only
MOCHI_API_KEY="your_key" python3 tools/mochi_sync.py --topic=derivatives

# Preview sync without changes (dry run)
MOCHI_API_KEY="your_key" python3 tools/mochi_sync.py --dry-run
```

**Purpose**: Upload flashcards from `datasets/learning/cards/` to Mochi spaced repetition system with sync tracking.

## System Architecture

### Directory Structure
- **`datasets/product/`**: Roadmaps, backlog, epics, snapshots
- **`datasets/marketing/`**: Content pipeline with presets, templates, multi-stage outputs  
- **`datasets/research/`**: External sources organized by strategic topic
- **`datasets/strategy/`**: Interactive sessions and formal memos
- **`datasets/learning/`**: Flashcards, notes, knowledge management
- **`datasets/meetings/`**: Meeting transcripts and processing inputs
- **`logs/`**: Automation execution logs with timestamps

### Key Configuration Files
- **`datasets/marketing/CLAUDE.md`**: Content creation rules, citation compliance
- **`datasets/marketing/presets.yaml`**: Style guides, word counts, structural requirements
- **`datasets/research/CLAUDE.md`**: Source processing and topic organization rules
- **`datasets/strategy/CLAUDE.md`**: Decision frameworks and session quality standards
- **`datasets/learning/decks/mochi.yaml`**: Mochi API configuration and deck mappings
- **`tools/mochi_sync.py`**: Flashcard synchronization script with API integration
- **`run-meetings-to-backlog.sh`**: Headless automation script with logging

### Workflow Patterns

**Marketing Content Pipeline**:
1. Intent (YAML requirements) → Brief (editorial requirements) → Outline (structure) → Draft with Verification (citation-compliant content) → Snippets (social media adaptations)
2. Output structure: `datasets/marketing/content/YYYY/mm-dd_type_slug/`
3. Citation compliance: Strategic quoting with inline links, "(source needed)" stops processing
4. Quality controls: Grade 8 readability, no em dashes, word count enforcement

**Product Epic Structure**:
1. Problem statement → Why now → User story → Appetite → In/out of scope → Acceptance criteria → Seed sub-stories  
2. Priority scoring system with automated roadmap updates
3. Structured templates with appetite (time allocation) and clear acceptance criteria

**Research Organization**:
1. Sources organized by strategic topic, not source type
2. Expiry management: frameworks (1-2 years), market data (3-6 months), competitor intel (6-12 months)
3. Standardized format: frontmatter, key insights, strategic applications, citations, internal links

**Strategy Session Process**:
1. Auto-context assembly from relevant research and internal meetings
2. Framework selection based on decision type (Porter's Five Forces, Jobs-to-be-Done, etc.)
3. Interactive planning with options analysis
4. Formal memo generation with implementation focus

**Learning Card Management**:
1. Flashcard creation: Source notes → Q&A/Cloze/Bidirectional cards → Topic tagging
2. Sync tracking: Content hashing for change detection and status management
3. Deck organization: Topic-based deck mapping with auto-creation
4. API integration: Mochi API sync with error handling and retry logic

## Headless Automation

### Environment Variables for Automation
```bash
export CLAUDE_CODE_AUTO_APPROVE_FILE_READS=true
export CLAUDE_CODE_AUTO_APPROVE_FILE_WRITES=true  
export CLAUDE_CODE_HEADLESS=true
```

### Automation Script Features
- Comprehensive logging to `logs/meetings-to-backlog-YYYYMMDD_HHMMSS.log`
- Error handling and exit code reporting
- PATH setup for Node.js and Claude Code binary
- Timestamped execution tracking

## Quality Standards

### Content Quality Controls
- **Citation Compliance**: All claims must have verifiable sources or "(source needed)" marker
- **Link Verification**: All URLs validated during draft creation
- **Style Enforcement**: Grade 8 readability, no em dashes, specific word count ranges
- **Brand Consistency**: Soft Raleon integration (≈1x per piece) with prescribed CTAs

### Product Planning Quality
- **Structured Format**: Problem/Why now/User story/Appetite/Scope/Acceptance criteria
- **Priority Scoring**: Standardized criteria with numerical rankings
- **Audit Trail**: Historical snapshots and changelog maintenance
- **Clear Scoping**: Explicit in-scope/out-of-scope boundaries

### Research Standards  
- **Source Integrity**: Checksums, metadata tracking, expiry dates
- **Topic Organization**: Strategic categorization for efficient context assembly
- **Citation Ready**: Verbatim quotes and source references prepared
- **Cross-referencing**: Links to internal meetings, roadmap, and related sources

### Strategy Documentation
- **Framework Application**: Systematic use of appropriate decision frameworks
- **Research-backed**: All recommendations supported by assembled context
- **Clear Recommendations**: Specific, actionable decisions with rationale
- **Implementation Focus**: Strategic decisions, not project planning details

### Learning Card Standards
- **Content Integrity**: SHA-256 hashing for change detection and sync status tracking
- **Format Consistency**: Q&A (question::answer), Cloze (==highlighted==), Bidirectional (term:::definition)
- **Topic Organization**: Hashtag-based topic extraction (#flashcards/derivatives) with deck mapping
- **Sync Reliability**: Frontmatter status tracking, error handling, and retry mechanisms

## Integration Points

The system maintains integration between all workflows:
- **Product roadmaps** inform **strategic decisions** and **marketing content**
- **Research sources** provide context for **strategy sessions** and **marketing pieces**
- **Meeting transcripts** feed **product planning** and **research processing**
- **Strategy memos** influence **product priorities** and **marketing positioning**
- **Learning cards** capture insights from **research sources**, **meetings**, and **strategy sessions**

## Common Patterns

### Output Versioning
- Never delete generated artifacts; append version suffixes (v1, v2, etc.)
- Maintain `status.json` for processing state and `progress.md` for human notes
- Historical snapshots for roadmaps and decision documentation

### Template-Driven Structure
- Standardized templates for briefs, outlines, epics, research sources, and strategy frameworks
- Handlebars-style templating with preset variable substitution
- Consistent metadata frontmatter across all document types

### Multi-Stage Processing
- Content creation: Intent → Brief → Outline → Draft → Verify → Snippets
- Product planning: Meeting transcripts → Epic extraction → Priority scoring → Roadmap update
- Research processing: Source intake → Topic categorization → Insight extraction → Context preparation
- Strategy sessions: Context assembly → Framework application → Interactive analysis → Memo generation
- Learning cards: Source material → Card extraction → Topic tagging → Mochi sync → Spaced repetition

This workspace enables sophisticated knowledge work automation while maintaining quality controls and comprehensive audit trails for all generated artifacts.