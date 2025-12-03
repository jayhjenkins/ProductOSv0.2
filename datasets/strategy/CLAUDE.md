# Strategy CLAUDE.md (Strategy Mode Defaults)
This subtree provides **interactive strategic decision-making** with research-backed analysis and formal memo documentation. All strategy work follows systematic decision frameworks.

## Directory Structure
Outputs live under:
`datasets/strategy/sessions/{YYYY}/{mm-dd}_{topic}/`
- context.md                     # Auto-assembled research context
- framework.md                   # Decision framework applied
- session-log.md                 # Interactive planning dialogue
- recommendations.md             # Emerging decisions and options

Final outputs:
`datasets/strategy/memos/{YYYY}/{mm-dd}_{title}.md`

## Commands (strategy expectations)
- `/strategy:session --topic="X"` - Start interactive strategic planning session
- `/strategy:memo` - Generate formal memo from current session

## Session Workflow
### Auto-Context Assembly
**Standard Context for All Sessions:**
- Relevant research from `/datasets/research/sources/{topic}/`
- Related internal meetings from `/datasets/meetings/Internal/Strategy/`
- Product roadmap context from `/datasets/product/`
- Marketing competitive intel from `/datasets/marketing/`

**Topic-Specific Context Enhancement:**
- **Pricing Decisions**: Include cost structure data, customer willingness-to-pay research, competitive pricing benchmarks
- **Product Decisions**: Include technical constraints, user research, feature usage data
- **Competitive Decisions**: Include competitor analysis, market position data, competitive response history
- **Market Positioning**: Include customer segmentation research, brand perception studies, messaging effectiveness data

### Framework Selection
Recommend appropriate decision framework based on topic:
- **Competitive decisions**: Porter's Five Forces, SWOT Analysis
- **Product decisions**: Jobs-to-be-Done, Product-Market Fit Canvas
- **Pricing decisions**: Value-Based Pricing, Competitive Analysis
- **Growth decisions**: Ansoff Matrix, Unit Economics Analysis

### Interactive Planning
- Present research context and framework
- Guide systematic decision-making process
- Capture options, trade-offs, and rationale
- Document assumptions and success metrics
- Build toward clear recommendation

## Session Quality Standards
- **Clear Problem Statement**: What exactly are we deciding?
- **Comprehensive Context**: All relevant research assembled (including topic-specific data)
- **Framework Application**: Systematic analysis approach appropriate to decision type
- **Multiple Options**: Consider alternatives and trade-offs with evidence
- **Clear Rationale**: Document decision reasoning based on assembled evidence
- **Data-Driven Analysis**: All claims supported by research sources
- **Focused Scope**: Strategic decision-making only, not implementation planning

## Quality Warning Flags
Sessions requiring additional work before memo generation:
- **Unsupported projections or speculation**: Claims without evidence basis
- **Missing critical context**: Economic data absent from pricing decisions, customer data absent from positioning decisions
- **Vague recommendations**: Unclear what specific action to take
- **Implementation details**: Project planning mixed with strategic decision-making
- **Excessive background**: Too much context relative to decision content

## Memo Generation Rules

### Core Required Sections (Always Include):
- **Problem Statement**: Clear, concise statement of decision requirement (1-2 sentences)
- **Key Evidence & Analysis**: Decision-relevant insights from research context
- **Recommendation**: Clear, actionable decision with rationale
- **Risk Management**: Key risks and mitigation strategies
- **Sources & Citations**: References to research sources and internal context

### Topic-Specific Optional Sections (Include When Relevant):
- **Economic Impact Analysis**: For pricing, investment, cost optimization decisions
- **Customer/Market Scenarios**: For user-facing decisions, market positioning, product strategy
- **Competitive Implications**: For positioning, competitive response, strategic differentiation
- **Technical Requirements**: For product, platform, integration decisions

### Memo Quality Guidelines:
- **Conciseness over verbosity**: Every section should be essential to the decision
- **Data-driven claims**: Assertions should link back to processed research sources
- **Clear recommendations**: What specifically are we deciding to do?
- **No implementation planning**: Strategy decisions, not project management
- **Eliminate speculation**: No unsupported projections or success metrics without data basis

## Integration with Research System
- Sessions automatically pull relevant research by topic
- New insights from sessions can be processed as research sources
- Research gaps identified during sessions trigger follow-up research
- Session outcomes inform future research priorities

## Integration with Existing Systems
- **Product Roadmap**: Align strategic decisions with product planning
- **Marketing**: Leverage competitive research and positioning work
- **Meetings**: Reference strategy meeting transcripts for context
- **Historical Reference**: Build on previous strategic decisions

## Documentation Standards
- Follow citation compliance from marketing system
- Version session artifacts (don't overwrite)
- Maintain audit trail of decision evolution
- Archive completed sessions for future reference
- Update memos if decisions change

## Session Management
- One active session at a time per topic
- Sessions can be paused and resumed
- Multiple stakeholders can contribute to sessions
- Sessions expire after 30 days if not converted to memo
- Completed sessions archived automatically