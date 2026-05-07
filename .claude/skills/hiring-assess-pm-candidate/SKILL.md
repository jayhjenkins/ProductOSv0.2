---
name: hiring-assess-pm-candidate
description: Use when evaluating a PM candidate — applies a four-dimension framework (Technical Experience, Team Fit, AI Fluency, Core Value Alignment) to produce a structured, evidence-backed assessment
---

# Assess PM Candidate

## Purpose

Apply a rigorous, evidence-backed evaluation framework to produce a structured PM candidate assessment. This is a reference skill invoked by the `process-interview` workflow.

## When to Use

Activate when:
- `process-interview` workflow reaches the analysis step
- Ad-hoc candidate evaluation is needed outside the full workflow

---

## Evaluation Framework

Analyze the candidate across four rated dimensions. Each dimension is scored 1–5. Base all evidence on the job description, resume, and interview transcript provided.

---

### Dimension 1: Technical Experience Alignment

**What to assess:**
- Domain relevance: Does their background map to B2B SaaS and/or property management / HOA / community management software (Vantaca's market)?
- Delivery record: Can they point to shipped products or features they owned end-to-end?
- Metrics fluency: Do they speak in outcomes and numbers, not just activity?
- Technical literacy: Sufficient depth to collaborate with engineers on a SaaS platform (APIs, integrations, data models)

**Strong evidence looks like:**
- Named products they shipped with measurable impact (e.g., "reduced churn by 12%", "increased NPS from 32 to 51")
- Familiarity with HOA, property management, or adjacent vertical a plus
- Comfortable discussing technical trade-offs without needing to be an engineer

**Weak evidence looks like:**
- Vague ownership ("I was part of the team that…")
- No metrics or outcomes cited
- No demonstrated SaaS delivery experience

---

### Dimension 2: Team Fit

**What to assess (interview signals only — not inferrable from resume):**
- Collaboration style: How do they describe working across functions (eng, design, CS, sales)?
- Communication clarity: Is their thinking structured and articulate in the interview itself?
- Conflict resolution signals: How do they describe navigating disagreement or misalignment?
- Energy and attitude: Genuine curiosity, openness, optimism — or evasiveness and blame-shifting?

**Strong evidence looks like:**
- Describes cross-functional work in terms of shared goals, not credit
- Provides specific examples of resolving disagreement constructively
- Communicates with clarity and structure in the interview itself

**Weak evidence looks like:**
- Shifts blame to past managers, teams, or org conditions
- Vague or evasive answers when asked about challenges
- Defensive or dismissive posture in response to follow-up questions

---

### Dimension 3: AI Fluency

**What to assess:**

This dimension has the highest weight for signal quality. Assess depth, not surface-level awareness.

- **Daily tool usage**: Which AI tools are they using? (Claude, ChatGPT, Cursor, Copilot, Perplexity, etc.) With what depth and regularity?
- **Workflow transformation**: Has AI fundamentally changed how they work — or is it a light accessory?
- **Operational AI maturity**: Can they prompt effectively? Do they use agents, automations, or scripts? Have they built any themselves?
- **AI product thinking**: Can they spec AI features? Do they think about agents as a user persona they design for?
- **Velocity signal**: Is the gain 10–20% (weak) or 10–20x (strong)?

**Strong signal (target profile):**
- Uses cutting-edge tools (Claude, Cursor, Perplexity, v0, etc.) daily with specificity — not just "ChatGPT sometimes"
- Has written scripts, built automations, or built an agent themselves
- Thinks about agents as a user persona when designing features
- Can articulate who they built things for with depth
- Reports AI has fundamentally restructured their research, spec-writing, user interview synthesis, or decision-making
- 20x velocity framing: "AI has changed what I'm capable of" not "it saves me an hour a week"

**Weak signal:**
- Mentions AI only as a buzzword ("I use AI tools")
- No specific tools, no depth, no workflow integration
- "Saves me an hour a week" framing — marginal productivity improvement rather than capability transformation
- No product thinking about AI features or AI-enabled user personas

---

### Dimension 4: Core Value Alignment (Vantaca)

**What to assess:**

Map evidence from both the resume and interview to Vantaca's five core values. Look for specificity — anyone can claim the values; strong candidates demonstrate them with examples.

**Vantaca's Five Core Values:**

1. **Win as a Team** — Evidence of collaboration, shared credit, collective success over individual glory
2. **Accountability Starts With Me** — Ownership under pressure, no blame-shifting, honest self-assessment when things went wrong
3. **Unwavering Commitment to Customer Experience** — Customer obsession, advocacy mindset, bringing the customer voice into decisions
4. **Always Growing** — Continuous learning, seeks feedback, growth mindset, comfort with ambiguity
5. **Innovate Boldly** — Curiosity, experimentation, progress over perfection, bias toward action and learning

**For each value:** Note whether there is strong evidence, limited evidence, or no evidence. Aggregate into the dimension score.

---

## Rating Anchors

Apply these consistently across all four dimensions:

| Score | Anchor |
|-------|--------|
| 5 | Exceptional — specific, compelling evidence; this dimension is a clear strength |
| 4 | Strong — clearly demonstrated; meets and exceeds expectations |
| 3 | Adequate — meets expectations but nothing standout |
| 2 | Limited — meaningful gaps or concerns; evidence is thin |
| 1 | Insufficient — contradicting evidence or clear misalignment |

---

## Recommendation Guidance

After scoring all four dimensions, apply this guidance:

| Recommendation | Criteria |
|----------------|----------|
| **Strong Yes** | Average 4+ across dimensions; no significant red flags; clear high-conviction hire |
| **Weak Yes** | Most dimensions 3+; minor concerns that are addressable on the job |
| **Weak No** | Multiple dimensions at 2–3; meaningful concerns outweigh positives |
| **Strong No** | Multiple dimensions at 1–2; clear misalignment or disqualifying red flags |

---

## Green Flag Signals

- Specific impact cited with metrics, not just "I led X"
- Structured, user-first thinking before jumping to solutions
- Data-backed prioritization reasoning
- Genuine curiosity about the company and role — did they research Vantaca?
- AI woven naturally into daily work, not just mentioned as a buzzword
- Uses cutting-edge tools with depth and specificity
- Writes scripts, builds automations, or has built an agent themselves
- Thinks about agents as a user persona when designing features
- Reports 20x velocity gains — AI has fundamentally changed how they work
- Can articulate "who I built it for" with depth

## Red Flag Signals

- Cannot cite specific outcomes or metrics they influenced
- Jumps to solutions before defining the user or problem
- Blame-shifting toward past employers, managers, or teams
- AI not part of daily workflow at all
- Evasive answers, overconfidence, or dismissiveness
- Inconsistencies between resume claims and interview answers
- No preparation or knowledge about Vantaca

---

## Output

Produce a complete, filled-in assessment using the `pm-assessment-template.md` format:
- All four dimensions rated 1–5 with evidence-backed narratives
- Strengths (3 bullets) and Red Flags grouped under Overall Recommendation
- Overall recommendation (Strong Yes / Weak Yes / Weak No / Strong No)
- Summary (2-3 sentences) and Final Recommendation (1-2 sentences)

**Writing norms — follow exactly:**
- **Voice:** Write in first person as Jay. Use "I", "my", "me" throughout — never refer to Jay by name or write in third person.
- **Narrative length:** 2-4 sentences per dimension. State the key evidence, give the score rationale, move on. Do not pad.
- **Quotes:** Avoid direct quotes. If a specific phrase is worth noting, use 2-4 words in quotes at most. Maximum 1-2 such micro-quotes across the entire document.
- **Evidence style:** Paraphrase and synthesize — describe what the candidate said or did, not their exact words.
- **Take a stand:** Every narrative must open with an actual assessment — a view, a judgment, a read on the candidate. Never open with phrases like "limited interview evidence", "insufficient data", or "hard to assess from the interview". If confidence is lower on a dimension, express it as a qualified opinion ("I'm less convinced here because…", "This felt thin to me…") not as a refusal to assess. State what you observed and what you made of it.
- **Em dashes:** Use sparingly. No more than 1-2 em dashes in the entire document. Use a period or comma instead.

## Related Skills

**Invoked by:**
- `process-interview` workflow

**Related:**
- `pm-assessment-template.md` in `datasets/recruiting/templates/`
