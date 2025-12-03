# Research CLAUDE.md (Research Mode Defaults)
This subtree provides **research processing and context gathering** for strategic decision-making. Research sources are organized by strategic topic for efficient context assembly.

## Directory Structure
Outputs live under:
`datasets/research/sources/{topic}/`
- sources/competitive-analysis/    # Sources organized by strategic topic
- sources/pricing-strategy/
- sources/market-positioning/
- sources/product-strategy/
- sources/customer-segmentation/
- sources/growth-strategy/
- templates/                      # Source templates and formats
- cache/                         # Auto-generated context summaries

## Commands (research expectations)
- `/research:process-source` - Process external sources (URL, file, or chat session)
- `/research:refresh --topic="X"` - Update expired research in topic area

## Source Processing Rules
### URL Processing (`--url="..."`)
- Fetch web content via WebFetch tool
- Convert to standardized markdown format
- Extract key insights and frameworks
- Add citation-ready quotes following marketing standards
- Store in appropriate topic folder

### File Processing (`--file="..."`) 
- Process PDFs, docs, images, reports
- Extract text and key concepts
- Create structured source document with metadata
- Handle various file formats appropriately

### Chat Session Processing (`--from-chat`)
- Capture current conversation insights
- Extract strategic decisions and frameworks discussed
- Create reusable research artifact
- Link to related internal context

## Source Format (standardized)
Every processed source must include:
- **Frontmatter**: title, source_type, date_added, date_expires, topic, tags
- **Key Insights**: Strategic takeaways and frameworks
- **Strategic Applications**: How this applies to decision-making
- **Citations**: Verbatim quotes for citation compliance
- **Internal Links**: Connections to meetings, roadmap, other sources

## Topic Organization
Sources organized by strategic topic (not source type):
- **competitive-analysis**: Competitor research, market positioning
- **pricing-strategy**: Pricing models, competitor pricing, willingness to pay
- **market-positioning**: Brand positioning, customer segments, messaging
- **product-strategy**: Product roadmap, feature prioritization, user research
- **customer-segmentation**: Customer research, personas, behavioral data
- **growth-strategy**: Acquisition channels, retention, expansion

## Expiry Management
- **Frameworks**: Expire slowly (1-2 years) - Porter's 5 Forces, SWOT, etc.
- **Market Data**: Expire quickly (3-6 months) - pricing, trends, metrics
- **Competitor Intel**: Expire moderately (6-12 months) - company strategies
- **Customer Research**: Expire moderately (6-12 months) - unless major product changes

## Integration Points
- **Strategy Sessions**: Auto-reference relevant sources during `/strategy:session`
- **Internal Meetings**: Cross-reference `/datasets/meetings/Internal/Strategy/`
- **Product Context**: Link to `/datasets/product/` roadmap and epics
- **Marketing Research**: Reference `/datasets/marketing/` competitive content

## Quality Standards
- All sources must follow citation compliance standards from marketing system
- Include verbatim quotes for strategic claims
- Tag sources appropriately for context assembly
- Link to internal context where relevant
- Maintain source integrity and update tracking