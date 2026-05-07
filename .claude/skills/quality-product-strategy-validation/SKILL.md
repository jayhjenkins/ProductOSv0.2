---
name: quality-product-strategy-validation
description: Use when creating or reviewing product strategies - enforces 8-point rubric ensuring strategies have evidenced problems, market context, competitive synthesis, decisive strategy, clear vision, defined investment areas, value-creating metrics, and actionable roadmap
---

# Product Strategy Validation

## The Iron Law

**NO PRODUCT STRATEGY BECOMES FINAL WITHOUT PASSING ALL 8 RUBRIC CHECKS**

If a strategy fails any rubric criterion, it must be:
1. Refined until it passes, OR
2. Kept in Draft status (if information is pending), OR
3. Scoped down (if too broad for one strategy document)

No "good enough" strategies. No "we'll fill it in later" for Final status. Pass or fail.

## Purpose

Ensure all product strategies maintain consistent quality standards:
- Problem is evidenced and material (not assumed)
- Market context includes timing rationale
- Competitive assessment drives synthesis (not just comparison)
- Strategic implications are decisive (not descriptive)
- Vision enables team decisions and tradeoffs
- Investment areas are clear bets with scope
- Metrics reflect value creation with hierarchy
- Roadmap and asks drive action (not just inform)

## When to Use This Skill

Activate automatically when:
- Creating new product strategies via `product-strategy-creation` workflow
- Reviewing strategy documents before transitioning to Final
- User requests strategy validation
- Strategy is being presented to stakeholders

## Validation by Strategy Status

| Status | Validation Requirement |
|--------|----------------------|
| Draft | Warnings allowed, no blockers. Must have: product name, problem statement, at least 1 investment area |
| Final | **ALL 8 criteria must pass**. No TBD in critical sections |

## The 8-Point Product Strategy Rubric

All strategies must pass **all eight criteria** to become Final:

### 1. Problem Evidenced & Material
**Requirement**: Problem is specific, evidenced from customer perspective, and material to the business

**Pass**:
```
Primary User (C1): Marketing managers at mid-market e-commerce companies
- Unmet jobs: Cannot correlate campaign spend to revenue attribution across channels
- Key friction: Manual data stitching across 3+ tools, 4hrs/week per manager
- Workarounds: Custom spreadsheets with stale data, leading to misallocation

Secondary User (C2): CFOs reviewing marketing ROI
- Impact: Cannot trust marketing budget requests due to attribution gaps

Evidence:
- Qualitative: 12 customer interviews, 3 CS escalations in Q4
- Quantitative: 40% of churned accounts cited "reporting gaps" in exit survey
- Severity: High frequency (daily), High impact ($50K+ misallocation/quarter), High strategic importance (core value prop)
```

**Fail**:
- Solution-shaped problem ("Users need a dashboard")
- Only anecdotal evidence ("A few customers mentioned...")
- No C1/C2 user framing
- Missing business impact or severity assessment
- Generic problem without specifics

### 2. Market Context with "Why Now"
**Requirement**: Trends tied to product implications with clear timing rationale

**Pass**:
```
| Trend | Category | Product Implication |
|-------|----------|-------------------|
| Privacy regulation (GDPR/CCPA expansion) | Regulatory | First-party data strategy required; cookie-based attribution dying |
| AI-driven attribution models | Technology | Opportunity to leapfrog rule-based competitors |
| Marketing budget scrutiny post-2024 | Customer Behavior | Higher willingness to pay for provable ROI |

Why Now: Privacy regulation eliminates legacy attribution methods within 18 months.
Competitors are 6-12 months behind on first-party data infrastructure.
Customer urgency is at peak (3x inbound requests for attribution features in Q4 vs Q3).
```

**Fail**:
- Market research dump without implications
- Long lists of trends with no product connection
- Missing "Why Now" entirely
- Generic industry overview

### 3. Competitive Assessment with Synthesis
**Requirement**: Competitors identified with insight into intent and strategy, not just features

**Pass**:
```
| Competitor | Type | Positioning | Key Strength | Key Weakness |
|-----------|------|-------------|-------------|-------------|
| CompetitorA | Direct | Enterprise-first | Deep integrations | Slow to ship, expensive |
| CompetitorB | Direct | SMB self-serve | Easy onboarding | No cross-channel attribution |
| Spreadsheets | Alternative | Free/flexible | No vendor lock-in | Manual, error-prone, stale |

Investment signals: CompetitorA hiring 20+ ML engineers (likely building AI attribution).
CompetitorB raised Series C, expanding upmarket.

User sentiment: CompetitorA users frustrated by 6-month implementation cycles.
Our NPS 15 points higher than CompetitorB on "time to value."
```

**Fail**:
- Feature-by-feature comparison table only
- No insight into competitor strategy or investment
- Missing indirect competitors or alternatives
- No user sentiment data

### 4. Strategic Synthesis is Decisive
**Requirement**: 5-7 distinct insights that drive choices, with SWOT informing strategy (not just listing)

**Pass**:
```
Key Insights:
1. Attribution accuracy is now a retention driver, not just a nice-to-have (3 churned accounts cited it)
2. Privacy regulation creates a 12-18 month window where first-party data infrastructure is a moat
3. Mid-market is underserved: too complex for SMB tools, can't afford enterprise implementations
4. AI attribution is table stakes within 24 months; early movers capture trust and training data
5. Cross-channel is the wedge: no competitor does it well for mid-market

Strategic Posture:
| Area | Posture | Rationale |
| Cross-channel attribution | Lead | Core differentiator, competitor gap |
| Enterprise features | Match | Needed for upmarket expansion, not a bet |
| SMB self-serve | Avoid | CompetitorB owns this; dilutes focus |
```

**Fail**:
- Repetition of earlier assessment sections
- Generic SWOT lists without decision implications
- No clear opportunity framing
- Missing strategic posture (lead/match/avoid)

### 5. Vision Enables Decisions
**Requirement**: Vision and mission help teams say no; non-goals and tradeoffs are explicit

**Pass**:
```
Vision: Every marketing dollar is accountable, in real time, across every channel.

Mission: Build the fastest path from campaign spend to provable revenue impact
for mid-market e-commerce teams.

Non-Goals:
- We will NOT build a campaign execution tool (we integrate, not replace)
- We will NOT pursue SMB self-serve (focus on mid-market with guided onboarding)
- We will NOT build custom BI (we feed data to existing BI tools)

Key Tradeoffs:
| Tradeoff | Choice | Rationale |
| Breadth vs. depth | Depth in e-commerce | Vertical expertise > horizontal coverage |
| Speed vs. accuracy | Accuracy first | Trust is our moat; fast-but-wrong kills credibility |
```

**Fail**:
- Buzzword vision ("Be the best platform for modern marketers")
- No non-goals listed
- No tradeoffs acknowledged
- Vision that can't help a team decide what NOT to build

### 6. Investment Areas are Clear Bets
**Requirement**: 3-5 investment areas with scope, rationale, positioning, and success measurement

**Pass**:
```
Investment Area 1: First-Party Attribution Engine
- Problem: Cookie deprecation breaks 60% of current attribution methods
- Why it matters: Core value prop depends on accurate attribution
- Why we're positioned: Existing data pipeline handles 500M events/day; competitors would need 12+ months to build
- In Scope: Server-side tracking, first-party cookie framework, ML attribution models
- Out of Scope: Third-party cookie alternatives, ad serving
- Success Metric: Attribution accuracy within 5% of source-of-truth (A/B test validated)
```

**Fail**:
- More than 5 investment areas (lack of focus)
- Vague areas without scope boundaries
- No rationale for why positioned to win
- Missing success measurement
- Overlapping or redundant themes

### 7. Metrics Reflect Value Creation
**Requirement**: North star with formula, leading indicators, business outcomes, guardrails in clear hierarchy

**Pass**:
```
North Star: Attributed Revenue Accuracy Rate
- Formula: (Revenue correctly attributed / Total revenue) * 100
- Why: Directly measures the value customers pay for

Leading Indicators:
| Indicator | Definition | Target |
| Attribution coverage | % of revenue touchpoints tracked | >90% |
| Time to first attribution | Hours from campaign launch to first attribution report | <4 hours |

Business Outcomes:
| Outcome | Metric | Target | Timeline |
| Retention | Net revenue retention | >110% | 12 months |
| Expansion | Avg channels per account | 3.5 → 5.0 | 18 months |

Guardrails:
| Guardrail | Threshold | Action if Breached |
| Data processing latency | <15 min p95 | Pause new feature work, fix pipeline |
| False attribution rate | <2% | Rollback model, investigate |
```

**Fail**:
- Output metrics only ("ship 5 features")
- Too many unprioritized metrics
- No north star or unclear formula
- Missing guardrails
- No hierarchy (leading vs. lagging unclear)

### 8. Roadmap & Asks Drive Action
**Requirement**: Themes (not feature lists), risks with mitigation, 30/60/90 plan, explicit asks with owners

**Pass**:
```
Roadmap organized by Theme 1: First-Party Attribution:
| Q1 | Server-side tracking MVP | Attribution coverage >50% | Validate data accuracy |
| Q2 | ML attribution models | Accuracy within 10% | A/B test vs. rule-based |

Risks:
| Risk | Likelihood | Impact | Mitigation | Owner |
| ML model accuracy insufficient | Medium | High | Fallback to rule-based hybrid | ML Lead |
| Partner API deprecation | Low | High | Build abstraction layer | Platform Lead |

30/60/90:
- 30 days: Finalize investment area scoping, begin server-side tracking design
- 60 days: Ship tracking MVP to 5 beta accounts, validate data pipeline
- 90 days: First ML model in staging, present accuracy benchmarks to leadership

Asks:
| Ask | From | Urgency | Context |
| 2 additional ML engineers | Engineering VP | Q1 hire | Critical for attribution model timeline |
| Partner API access agreement | BD | 30 days | Blocking server-side tracking |
```

**Fail**:
- Feature lists with dates (no strategic themes)
- Risks minimized or buried
- No 30/60/90 plan
- Ends with "discussion" instead of explicit asks
- Missing owners on asks

## Validation Process

### 1. Load Strategy

Read strategy from:
- `datasets/product/strategies/{YYYY}/strategy_{slug}/strategy_{slug}.md`, OR
- In-memory strategy draft

### 2. Apply Rubric

Check each criterion sequentially:

```
1. Problem Evidenced & Material? [Yes/No] → [Has C1/C2 users, qual+quant evidence, severity]
2. Market Context with "Why Now"? [Yes/No] → [Trends tied to implications, timing rationale]
3. Competitive Assessment with Synthesis? [Yes/No] → [Competitors with intent, not just features]
4. Strategic Synthesis is Decisive? [Yes/No] → [5-7 insights, SWOT drives choices, posture defined]
5. Vision Enables Decisions? [Yes/No] → [Vision+mission help say no, non-goals, tradeoffs]
6. Investment Areas are Clear Bets? [Yes/No] → [3-5 areas with scope, rationale, metrics]
7. Metrics Reflect Value Creation? [Yes/No] → [North star formula, hierarchy, guardrails]
8. Roadmap & Asks Drive Action? [Yes/No] → [Themes, risks+mitigation, 30/60/90, asks]
```

### 3. Generate Report

**If all pass:**
```markdown
# Product Strategy Validation Report: PASS

**Strategy**: [Title]
**Current Status**: [Status]
**Target Status**: Final

1. Problem Evidenced & Material: C1/C2 defined, qual+quant evidence, severity assessed
2. Market Context with "Why Now": N trends with implications, timing rationale clear
3. Competitive Assessment with Synthesis: N competitors analyzed, investment signals, user sentiment
4. Strategic Synthesis is Decisive: N insights, SWOT-driven, posture defined (N lead, N match, N avoid)
5. Vision Enables Decisions: Non-goals explicit, N tradeoffs acknowledged
6. Investment Areas are Clear Bets: N areas with scope, rationale, and metrics
7. Metrics Reflect Value Creation: North star with formula, N leading indicators, N guardrails
8. Roadmap & Asks Drive Action: Themed roadmap, N risks with mitigation, 30/60/90 plan, N asks

**Recommendation**: Approve for Final status
```

**If any fail:**
```markdown
# Product Strategy Validation Report: FAIL

**Strategy**: [Title]
**Current Status**: [Status]
**Target Status**: Final

Failed criteria:
X [Criterion name]: [Specific failure reason]

**Required fixes**:
1. [Specific action to address failure]
2. [Specific action to address failure]

**Recommendation**: Keep as Draft / Needs Revision
```

### 4. Block or Approve

**If PASS:**
- Strategy can transition to Final
- Strategy ready for stakeholder presentation
- Implementation planning can begin

**If FAIL:**
- Strategy stays in Draft status
- Must address failures before re-validation
- User notified of required additions

## Integration with Workflows

### Product Strategy Creation Integration

**Invoked by:**
- `product-strategy-creation` workflow (Phase 10, before output)

**Blocking behavior:**
- Failed strategies remain in Draft status
- Failed strategies flagged in validation report
- User notified of required additions

### Manual Validation

**Direct usage:**
User can invoke validation on existing strategies:
```
"Validate the strategy at datasets/product/strategies/2026/strategy_attribution-engine/strategy_attribution-engine.md"
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Solution-shaped problems ("need a dashboard") | Frame from C1/C2 perspective with evidence |
| Market research dump without "Why Now" | Tie each trend to a product implication |
| Feature comparison tables | Synthesize competitor intent and strategy |
| Generic SWOT lists | Make every SWOT item drive a strategic choice |
| Buzzword vision | Test: can a team use this to say "no"? |
| Too many investment areas (>5) | Consolidate or sequence; focus is a strategy |
| Output metrics only | Define north star with formula, add guardrails |
| Feature roadmap with dates | Organize by strategic themes, leave room for learning |

## Anti-Rationalization Blocks

Common excuses that are **explicitly rejected**:

| Rationalization | Reality |
|-----------------|---------|
| "We can fill in evidence later" | No evidence = no validated problem = no strategy |
| "The market context is obvious" | Obvious to you is not obvious to stakeholders; document it |
| "Everyone knows the competition" | Synthesis and intent matter more than awareness |
| "The vision is aspirational by nature" | Aspirational AND actionable; it must help teams decide |
| "We'll narrow investment areas later" | Strategy IS choosing; more than 5 areas means no strategy |
| "Metrics will come from eng" | PM owns the metric framework; eng owns implementation |
| "The roadmap is flexible" | Flexible AND themed; not an excuse for missing structure |
| "Close enough to pass" | All 8 criteria or remain in Draft |

## Related Skills

- **product-strategy-creation**: Invokes this quality gate before output
- **meeting-synthesis**: Gathers customer evidence for problem validation
- **research-gathering**: Provides market and competitive context
- **north-star-alignment**: Helps define metrics framework
