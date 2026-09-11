---
name: workflow-product-strategy-creation
description: Use when creating comprehensive product strategy documents - gathers assessment and strategy through 10-phase interactive session with optional context assembly from meetings and research, validates with product-strategy-validation, and writes strategy file using fillable template
---

# Product Strategy Creation

## Purpose

Create comprehensive product strategy documents through interactive session:
- 10-phase structured requirements gathering (Assessment + Strategy)
- Optional context-assisted mode with auto-assembly from meetings and research
- Apply 8-point product strategy validation rubric
- Generate strategy file from fillable template
- No fabrication - leave unknown sections as TBD

## When to Use

Activate when:
- User invokes `/project:create-product-strategy`
- Manual product strategy creation needed
- Capturing strategic direction from conversation or accumulated research

## Guiding Principles

1. **Strategy is about choices** - A strategy that tries to do everything is not a strategy
2. **Evidence before opinions** - Every claim should trace to customer data, market research, or quantitative evidence
3. **No fabrication** - Leave sections blank/TBD rather than making up information
4. **Synthesis over summary** - Turn data into insight and insight into choices
5. **Actionable output** - Strategy must end with decisions, asks, and a 30/60/90 plan

## Workflow

### Phase 0: Setup & Context Mode

**Ask user:**
- **Product/Area Name**: What product or area is this strategy for?
- **Time Horizon**: How far out does this strategy look? (e.g., 12 months, 18 months, 2 years)
- **Audience**: Who will review this? (e.g., Leadership, Cross-functional team, Board)
- **Context Mode**: Choose one:
  - **Fully Interactive** - All sections gathered through conversation
  - **Context-Assisted** - Auto-assemble from meetings + research, fill gaps interactively

**Create output folder:**
`datasets/product/strategies/{YYYY}/strategy_{slug}/`

**Initialize tracking files:**
- `status.json` with `{ "current_phase": 0, "mode": "[interactive|context-assisted]", "started": "YYYY-MM-DD", "status": "in_progress" }`
- `progress.md` with session metadata

**If Context-Assisted mode:**
1. **Invoke:** `meeting-synthesis` skill
   - Time window: 90 days
   - Keywords from product/area name
2. **Invoke:** `research-gathering` skill
   - Topics: competitive-analysis, product-strategy, market-positioning
3. Write assembled context to `{output-folder}/context.md`
4. Present context summary to user for confirmation before proceeding

## MCP Data Enrichment (Optional)

When MCP data sources are connected, enrich specific strategy phases with live external data. Skip if tools are unavailable.

### Phase 2 Enhancement: The Problem (Evidence Strengthening)

Supplement meeting-derived problem evidence with quantitative data:

**Pendo Listen pain points**: Use `mcp__claude_ai_Pendo__get_feedback_items` (subId: from profile (`profile_lib.py --pendo-subid`), filters: {feedbackTypes: ["Pain Point", "Product Issues"]}) to surface customer-reported problems. Use `mcp__claude_ai_Pendo__get_feedback_insights` with the same filters for AI-extracted insights with supporting quotes.

**Zendesk ticket volume by product area**:
```sql
SELECT custom_product_field, COUNT(*) as ticket_count,
       SUM(CASE WHEN priority IN ('urgent', 'high') THEN 1 ELSE 0 END) as high_priority,
       SUM(CASE WHEN custom_confirmed_bug = true THEN 1 ELSE 0 END) as confirmed_bugs
FROM {catalog}.zendesk.ticket
WHERE created_at >= DATE_SUB(CURRENT_DATE(), 90)
  AND custom_product_field IS NOT NULL
GROUP BY custom_product_field
ORDER BY ticket_count DESC
```

Use ticket patterns to quantify problem severity and identify which product areas carry the highest support burden.

### Phase 4 Enhancement: Competitive Assessment

**Pendo Listen competitive intelligence**: Use `mcp__claude_ai_Pendo__get_feedback_items` (subId: from profile (`profile_lib.py --pendo-subid`), filters: {feedbackTypes: ["Competitor Weakness", "Competitor Strength"]}) to surface customer feedback about competitors. This provides direct customer voice on competitive positioning.

**Gong competitive tracker data**:
```sql
SELECT ct.name as tracker_name, ct.phrase, SUM(ct.count) as total_mentions,
       COUNT(DISTINCT ct.call_id) as calls_mentioned
FROM {catalog}.gongio.call_tracker ct
JOIN {catalog}.gongio.call c ON CAST(ct.call_id AS STRING) = c.id
WHERE c.started >= DATE_SUB(CURRENT_DATE(), 90)
  AND ct._fivetran_deleted = false
GROUP BY ct.name, ct.phrase
ORDER BY total_mentions DESC
LIMIT 30
```

Filter for competitor-related trackers to see which competitors come up most in sales conversations and what phrases are associated.

### Phase 6 Enhancement: Current User Experience

**Pendo session replays**: Use `mcp__claude_ai_Pendo__sessionReplayList` (subId: from profile (`profile_lib.py --pendo-subid`)) with frustration filtering to find replays of critical flow friction:
- `frustrationTypes`: [{"frustrationType": "rageClick", "fact": "occurred"}, {"frustrationType": "deadClick", "fact": "occurred"}]

**Pendo feature adoption**: Use `mcp__claude_ai_Pendo__activityQuery` (subId: from profile (`profile_lib.py --pendo-subid`), appId for relevant app, entityType: "feature", group: ["featureId"], sort: ["-uniqueVisitorCount"], dateRange: {range: "relative", lastNDays: 30}) to identify most/least used features as evidence for UX assessment.

### Phase 9 Enhancement: Differentiation, Goals & Metrics

**Current baselines**: Use `mcp__claude_ai_Pendo__productEngagementScore` (subId: from profile (`profile_lib.py --pendo-subid`), appId for relevant app) to establish current PES as baseline for goal-setting within the strategy.

**Existing instrumentation check**: Use `mcp__claude_ai_Pendo__searchEntities` to verify proposed metrics can be measured with existing Pendo instrumentation.

### Phase 1: The Problem (Template 1.1)

**Gather from user:**
- **C1 (Primary User)**: Who are they? Unmet jobs, friction, failure modes, workarounds
- **C2 (Secondary User)**: Who are they? Downstream experience and trust impact
- **Company Framing**: Why this matters (growth, retention, brand, platform leverage)
- **Evidence**: Qualitative (interviews, usability, CS/sales) and Quantitative (funnel metrics, adoption, retention, NPS)
- **Severity**: Frequency x Impact x Strategic Importance

**In Context-Assisted mode:**
- Present customer quotes from meeting-synthesis for confirmation
- Surface relevant research findings as starting points
- Ask user to confirm, refine, or override assembled evidence

*If user doesn't have evidence, leave as TBD with note that validation will flag it.*

### Phase 2: Market & Industry Landscape (Template 1.2)

**Gather from user:**
- **Industry/category trends** with product implications
- **Customer behavior shifts** with product implications
- **Technology shifts** with product implications
- **Macro/regulatory forces** with product implications
- **Why Now**: Synthesized timing rationale

**In Context-Assisted mode:**
- Invoke `research-gathering` with topic `market-positioning` if not already run
- Present research findings as candidate trends
- Ask user to confirm relevance and add implications

### Phase 3: Competitive Assessment (Template 1.3)

**Gather from user:**
- **Competitive set**: Direct, indirect, and alternative competitors
- **Positioning and GTM models** for each
- **Investment signals**: What competitors are building/hiring for
- **User sentiment**: Where competitors win/lose from user perspective

**In Context-Assisted mode:**
- Invoke `research-gathering` with topic `competitive-analysis` if not already run
- Present competitive intel from research for confirmation
- Ask user to add investment signals and sentiment data

### Phase 4: Synthesis & Strategic Implications (Template 1.4)

**Semi-automated phase:**
1. Draft initial synthesis from Phases 1-3 content
2. Present 5-7 candidate insights to user for review
3. **Gather from user:**
   - Confirmation/refinement of insights
   - SWOT matrix inputs (strengths, weaknesses, opportunities, threats)
   - Strategic posture: Where to lead, match, avoid (with rationale)

*This phase synthesizes - it should NOT repeat earlier sections.*

### Phase 5: Current User Experience (Template 1.5)

**Gather from user:**
- **Critical flows**: 1-2 user flows tied to key outcomes
- **Friction points**: Where value leaks (time, trust, accuracy, confidence)
- **Workarounds**: What users do today to get around limitations

*If user has screenshots, journey maps, or Figma links, note paths but don't fabricate flow details.*

### Phase 6: Vision, Mission & Future Experience (Template 2.1 + 2.2)

**Gather from user:**
- **Vision**: Future state you're working toward
- **Mission**: How the product will get there
- **Non-goals**: What this strategy explicitly does NOT pursue
- **Key tradeoffs**: Choices made and rationale
- **Future-state user story**: Narrative walkthrough of C1/C2 experience
- **Moments of value**: Where disproportionate value is created

*Test vision quality: Can a team use this to say "no" to a feature request?*

### Phase 7: Themed User Stories & Investment Areas (Template 2.3 + 2.4)

**Gather from user:**

**Themed User Stories (3-5 themes):**
For each theme:
- Today: current pain and behavior
- Tomorrow: desired outcome
- Investment needed (product, platform, data, GTM)
- Cost level and dependencies
- Value unlocked (customer + business metrics)

**Strategic Investment Areas (3-5):**
For each area:
- What problem it addresses and for whom
- Why it matters strategically
- Why you're positioned to win
- In scope / Out of scope
- How success is measured

*Themes and investment areas should align. Flag misalignment to user.*

### Phase 8: Differentiation, Goals & Metrics (Template 2.5 + 2.6)

**Gather from user:**
- **Differentiators**: What matters to users, sources of advantage, how advantage compounds
- **Intentional tradeoffs**: What you choose NOT to compete on

**Invoke:** `north-star-alignment` skill for metrics framework

**Then gather/confirm:**
- **North star metric** with formula and rationale
- **Leading indicators** with definitions and targets
- **Business outcomes** with metrics and timelines
- **Guardrails** with thresholds and breach actions

*User confirms or refines metrics output from north-star-alignment.*

### Phase 9: Roadmap, Risks & Next Steps (Template 2.7 + 2.8 + 2.9)

**Gather from user:**

**Roadmap:**
- Initiatives organized by strategic theme (NOT feature lists)
- Quarterly or half-year milestones
- Expected metric impact per initiative
- Discovery points (where to pause and learn)

**Risks:**
- Key risks (technical, data, GTM, adoption, legal)
- Likelihood and impact ratings
- Mitigation plans with owners

**Dependencies:**
- Internal dependencies (teams, platforms)
- External dependencies (partners, APIs)

**Decisions & Asks:**
- Decisions needed from leadership (with options and recommendation)
- 30/60/90 day plan
- Explicit asks (resources, alignment, approvals) with owners and urgency

### Phase 10: Executive Summary, Validation & Output (Automated)

**Step 1: Auto-draft Executive Summary**
- Synthesize from all phases into template Section 0
- Include: Why we're here, core problem, opportunity, investment areas, asks, success metrics

**Step 2: Validate**
**Invoke:** `product-strategy-validation` skill
- Apply 8-point rubric
- Draft strategies may have warnings but not blockers
- Final strategies must pass all criteria

**Step 3: Write Strategy File**

**Use template:** `datasets/product/templates/product-strategy-fillable.md`

**Output:** `datasets/product/strategies/{YYYY}/strategy_{slug}/strategy_{slug}.md`

**Set initial status:** Draft

**Add changelog entry:**
```markdown
| {YYYY-MM-DD} | Initial draft created | {user} |
```

**Step 4: Update status.json**
```json
{
  "current_phase": 10,
  "mode": "[interactive|context-assisted]",
  "started": "YYYY-MM-DD",
  "completed": "YYYY-MM-DD",
  "status": "complete",
  "validation": "[PASS|FAIL]",
  "strategy_status": "[Draft|Final]"
}
```

**Step 5: Offer Next Steps**
"Generate strategy memo for stakeholder distribution?"
- If yes: Invoke `strategy-memo` skill with strategy folder path
- If no: Confirm artifacts saved, note memo can be generated later

## Fact-Checking Requirements

**CRITICAL**: Do not fabricate information. For any section where information is not provided:
- Leave the section blank or marked "TBD"
- Note in progress.md that section needs input
- Prompt user: "Do you have this information available?"
- Validation will flag missing critical sections appropriately

## Resumability

Strategy creation may span multiple sessions. The workflow supports resumption:
- `status.json` tracks `current_phase`
- On resume, read status.json and pick up from last completed phase
- Context from earlier phases preserved in progress.md

## Strategy Statuses

| Status | When to Use |
|--------|-------------|
| Draft | Initial creation, known to be incomplete |
| Final | All 8 validation criteria pass, ready for stakeholders |

## Success Criteria

- Strategy created with all provided information
- Unknown sections marked as TBD (not fabricated)
- Strategy file written to correct location using fillable template
- Changelog entry added
- Validation rubric applied
- status.json and progress.md maintained
- Context assembled (if context-assisted mode)

## Related Skills

- `product-strategy-validation`: Validates strategy quality (8-point rubric)
- `meeting-synthesis`: Gathers customer evidence from transcripts
- `research-gathering`: Assembles market and competitive context
- `north-star-alignment`: Defines metrics framework
- `strategy-session`: For one-off strategic decisions (different from comprehensive strategy)
- `strategy-memo`: Generates stakeholder-ready memo from strategy
