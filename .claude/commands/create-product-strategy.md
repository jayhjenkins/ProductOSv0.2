# /project:create-product-strategy

## MANDATORY: Use the product-strategy-creation Skill

**You MUST use the `product-strategy-creation` skill located at `.claude/skills/workflow-product-strategy-creation/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using product-strategy-creation to create a comprehensive Product Strategy"
2. **Read the skill**: Load `.claude/skills/workflow-product-strategy-creation/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Create comprehensive product strategy through interactive session with structured information gathering across Assessment (problem, market, competition, synthesis, UX) and Strategy (vision, themes, investments, metrics, roadmap).

## Key Behaviors

- **Two modes**: Fully Interactive or Context-Assisted (auto-assembles from meetings + research)
- **10 phases**: Setup, Problem, Market, Competition, Synthesis, UX, Vision, Themes/Investments, Metrics, Roadmap/Asks
- **No fabrication**: Leave sections blank/TBD rather than making up information
- **Evidence-backed**: Every claim should trace to customer data, market research, or quantitative evidence

## Output Location

`datasets/product/strategies/{YYYY}/strategy_{slug}/strategy_{slug}.md`

## Validation

Strategy must pass 8-point validation before becoming Final:
1. Problem Evidenced & Material
2. Market Context with "Why Now"
3. Competitive Assessment with Synthesis
4. Strategic Synthesis is Decisive
5. Vision Enables Decisions
6. Investment Areas are Clear Bets
7. Metrics Reflect Value Creation
8. Roadmap & Asks Drive Action

## Critical Rules

- Strategy is about choices - doing everything is not a strategy
- 3-5 investment areas maximum (more = lack of focus)
- Roadmap organized by themes, not feature lists
- Must end with explicit asks, owners, and 30/60/90 plan
