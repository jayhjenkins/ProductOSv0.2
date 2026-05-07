---
name: hiring-assess-pm-practicum
description: Use when evaluating a PM candidate's live product practicum — assesses product craft across five dimensions (Problem Framing & User Insight, Strategic Thinking & Vision, Prioritization & Tradeoffs, AI-First Product Thinking, Metrics & Outcomes) using a demanding craft matrix that anchors each score to concrete behavioral descriptions calibrated to PM career ladders
---

# Assess PM Practicum

## Purpose

Evaluate a candidate's product craft from a live practicum. Score each craft dimension on a 1–5 scale anchored to concrete behavioral descriptions, synthesize an overall craft-level read, and produce a hire recommendation based on the gap between demonstrated craft and the role level.

This is the reference framework invoked by the `process-practicum` workflow. It is designed to be general — it does not encode the specifics of any single role, scenario prompt, or company. The practicum prompt provides scenario context; the role level and job description provide the target; this framework provides the craft calibration.

## When to Use

Activate when:
- `process-practicum` workflow reaches the analysis step
- Ad-hoc practicum evaluation is needed outside the full workflow

## What the Practicum Tests

The practicum is a short, live product exercise. Candidates are given a scenario, a short prep window with AI tools encouraged, a presentation window, and a Q&A window.

**Signal this surfaces that the interview does not:**
- How they frame ambiguous problems under time pressure
- Whether they have a thesis or improvise one under prompting
- How specific they get when forced to commit
- Whether they have a prioritization framework or wave their hands
- How their instincts survive contact with pushback and new facts
- Whether AI is genuinely part of how they think, or a buzzword

**Signal this does NOT surface:**
- Long-arc delivery record (interview covers that)
- Team Fit and culture (interview covers that)
- Values alignment (interview covers that)
- Stakeholder management, managing up, or team leadership (too contextual for a 60-minute exercise)

Keep practicum evaluation focused on what it actually tests: **product craft.**

---

## Framework Foundations

Adapted from widely-used PM career frameworks:

- **Ravi Mehta's Product Competency Toolkit** — 12 competencies across four areas, mapped across PM levels from APM to VP. The practicum surfaces only a subset; this framework selects and adapts those legitimately evaluable in a 60-minute live exercise.
- **Shreyas Doshi's Good PM / Great PM** — the behavioral tells that distinguish craft levels (metrics-informed vs metrics-driven, problem-preventing vs problem-solving, strategy validation before execution, intellectual flexibility).
- **Sachin Rekhi's cross-company PM ladder synthesis** — the three recurring advancement dimensions (independence, product scope, leadership).

This is a **craft matrix**, not a seniority gate. It describes what product craft looks like at each level. The score reflects what the candidate demonstrated. The hire recommendation compares demonstrated level to role level.

---

## Calibration Principles (read before scoring)

These principles prevent score inflation. They are the single most important part of the rubric. If the assessor does not internalize them, the matrix will drift generous.

### 1. Table stakes are not signal

The craft bar evolves with the industry. A signal of craft five years ago can be table stakes today. Right now, these are table stakes — they do not earn points, and their absence is a serious gap, not a neutral observation:

- Using AI tools during prep
- Building a working prototype or artifact in the prep window
- Naming users and jobs-to-be-done
- Using vocabulary like North Star, JTBD, leading vs lagging, RICE, impact/effort
- Distinguishing users from a vague "customer"
- Having a slide, doc, or sketch to present from
- Acknowledging that metrics matter

A candidate who does these things has cleared the entry threshold. They have not demonstrated craft. Score accordingly: table-stakes execution lands at Level 2 on the relevant dimension, not Level 3 or 4.

### 2. Naming ≠ applying

Saying "RICE" does not demonstrate prioritization. Using RICE to produce a ranked, defended tradeoff does. Saying "North Star" does not demonstrate metrics maturity. Defining one that survives hostile probing does. The matrix is calibrated to **applied** craft. Score the application, not the vocabulary.

### 3. Recovery is not craft

If a candidate's strong answer only appears after the interviewer walks them to it — through a prompt, a reframing question, or a new fact — credit the recovery but do not let it raise the score past where the candidate started. The craft signal is what they produced unassisted. Session Dynamics qualifies every dimension score: if the turning points came from the interviewer, the demonstrated level is what was demonstrated without assistance.

### 4. Specificity beats breadth

One deeply worked-through example beats five shallowly-named ones. A candidate who names seven metrics and defines none is weaker than one who names one and defines it precisely. When scoring, weight depth of application over surface area of concepts.

### 5. The scenario is bait

Practicum scenarios usually contain deliberate red herrings — a named competitor, a specific feature, a scoped mandate. A proficient PM pressure-tests the scenario framing. A strong PM reframes it when reframing is warranted. A weaker PM accepts the frame and optimizes within it. Accepting the frame at face value is not neutral — it is a craft gap.

### 6. Level 3 means "I'd ship this from them"

Anchor the matrix around this test:
- **Level 3 (Proficient)** — If I saw this quality of thinking from a PM on my team, I would be satisfied. I could hand them a problem and expect a usable answer.
- **Level 4 (Strong)** — I learned something from this candidate. They reframed, sequenced, or specified in a way I hadn't.
- **Level 5 (Exceptional)** — They changed how I think about the problem. Their framing will stick with me.

If the candidate's output would NOT satisfy you on a real team, it is not a 3.

---

## The Five Dimensions

1. **Problem Framing & User Insight** — Who is this for, what job are they doing, who pays, where does revenue come from?
2. **Strategic Thinking & Vision** — Thesis, differentiation, competitive positioning, point of view on the future.
3. **Prioritization & Tradeoffs** — What's in, what's out, what it costs, and why — with a visible framework.
4. **AI-First Product Thinking** — How AI reshapes the product as an architectural primitive, not a bolt-on layer.
5. **Metrics & Outcomes** — North Star, leading vs lagging, guardrails, counter-metrics, business alignment.

Not scored (observational only):
- **Session Dynamics** — Who drove turning points, how the candidate held up under pushback, specificity trajectory under probing. This qualifies the score reads; it does not produce an independent score.

---

## Craft Level Matrix

Each dimension is scored 1–5. The matrix is demanding by design — see Calibration Principles above.

**Level anchors (apply to all dimensions):**

| Score | Level Anchor | Test |
|-------|--------------|------|
| 1 | Foundational gaps | Missing the basics; cannot do this job |
| 2 | Developing | Names the concepts, applies them superficially; table-stakes execution |
| 3 | Proficient | Applied craft; I'd ship this work from them |
| 4 | Strong | I learned something; they reframed or sequenced beyond expectation |
| 5 | Exceptional | Changed how I think about the problem |

**Matrix — what each dimension looks like at each level:**

| Dimension | 1 — Foundational gaps | 2 — Developing | 3 — Proficient | 4 — Strong | 5 — Exceptional |
|-----------|----------------------|----------------|-----------------|------------|-----------------|
| **Problem Framing & User Insight** | No clear user; jumps to solutions; pain is buzzwords disconnected from business | Users and JTBD named; pain described in general terms; scenario framing accepted at face value; no buyer-vs-user separation; no sizing | Distinct personas with differentiated JTBD; pain tied to a specific business consequence; begins buyer/user separation and mentions segmentation; probes the scenario modestly | Buyer / user / payer / beneficiary mapped with economic clarity; segments sized even if back-of-envelope; revenue motion traced (new logo vs expansion vs upsell); non-obvious pain surfaced; pressure-tests the scenario framing | Reframes what the job actually is; identifies pains the user cannot articulate; maps the ecosystem with precision; produces insight that reshapes how I see the problem |
| **Strategic Thinking & Vision** | No thesis; reactive to scenario; vision is feature additions to current product | Thesis stated but thin ("add AI," "close the gap"); single hypothesis about the market; validation vague or absent; thesis collapses under basic probing | Thesis with rationale that survives first-round pushback; plural competitive hypotheses with specific validation tactics and timelines; explicit stance on match / differentiate / leapfrog; future state articulated in user terms | Thesis has teeth and the candidate will defend it; positions against an ecosystem, not one competitor; updates view gracefully on new facts without collapsing; reframes "catch up" into "open a new gap" | Reframes the category; thesis is non-obvious, survives inversion and hostile questioning; identifies second-order effects most PMs miss; the position is defensible even when stress-tested from opposite premises |
| **Prioritization & Tradeoffs** | Everything is "also"; no framework; no descoping; no costs acknowledged | Informal ranking by energy; tradeoffs implied but not named; may make one choice but without a visible framework; what's out is vague or missing; pivots expand scope without descoping | Visible prioritization framework (RICE-like, impact/effort, or a clearly reasoned qualitative lens); explicit in/out list stated or written; costs named; defends the tradeoff under basic pushback | Sequences choices for value capture and risk management; weighs reversibility and blast radius; pivots name what gets dropped; cuts are deliberate and defended with rationale that holds under pressure | Makes the strategic cuts most PMs avoid; treats "what we won't do" as a first-class product decision; articulates opportunity cost in both user and business terms; the prioritization itself is the insight |
| **AI-First Product Thinking** | AI as pure buzzword or single chatbot bolt-on; no architecture; no prep-window AI leverage | Prototype built (table stakes in 2026); AI named as a layer or feature; some mechanics described; no architectural primitives; agents not a persona; no evals or safety thinking | Prototype plus tiered AI response model (assistive / workflow / autonomous); confidence and human-in-the-loop concepts named and applied; some agent-as-persona thinking; prep artifacts show meaningful AI leverage beyond "I made a demo" | Product structurally re-conceived around what AI enables; agents-as-persona as a first-class design target with their own workflows; evals, guardrails, failure modes, and AI economics (cost / latency / quality) considered; data-flywheel logic present; thinks in AI primitives (orchestration, structured output, retrieval, memory) | AI changes what the product category IS; reshapes the job itself rather than accelerating the existing job; produces non-obvious AI-primitive insight that will stick with me; designs for human-AI collaboration as a first principle, not an afterthought |
| **Metrics & Outcomes** | Activity metrics (logins, MAU); no business tie; no distinction between leading and lagging | North Star named but ties weakly to user or business outcome; leading indicators are vanity signals (logins, time in app); guardrails not mentioned; metrics framing does not update when the strategy pivots | North Star tied cleanly to user outcome and business outcome; leading and lagging distinguished with real indicators (not vanity); early awareness of measurement traps; some guardrail thinking | Counter-metrics explicit; recognizes gaming and vanity risks; metrics tie to retention, expansion, or win rate; measurement shapes what ships and what gets rolled back; metrics update when strategy pivots | Metrics reshape organizational behavior; defines what would falsify the strategy; instruments for learning, not reporting; connects measurement to the product's data flywheel or AI evaluation layer |

---

## Per-Dimension Evaluation Guidance

Use this guidance to ground score narratives. The matrix is the rubric; the guidance below is how to interpret what you're seeing.

### Dimension 1: Problem Framing & User Insight

**What to look for:**
- Distinct users with differentiated JTBD
- Pain specificity — concrete and tied to business consequence
- Buyer vs user distinction — who pays, what's the revenue motion
- Market/segment sizing, even back-of-envelope
- Pressure-testing the scenario framing
- Evidence the candidate grounds claims in customer reality, not abstraction

**Common failure modes:**
- Personas functionally identical
- Generic pains ("better dashboards") with no business tie
- Treating the scenario prompt as the customer truth
- Ignoring the buyer — designing for users who don't control the budget
- Naming JTBD as vocabulary without specificity

### Dimension 2: Strategic Thinking & Vision

**What to look for:**
- A thesis the candidate will defend about where the product should go and why
- Plural competitive hypotheses, each falsifiable, each with a validation tactic
- Specific validation timelines (win/loss interviews, demo teardowns, job postings)
- Explicit stance on match vs differentiate vs leapfrog with rationale
- Future state described in user terms, not feature terms
- Whether they stay anchored to users and business outcomes or go reactive
- Survival of the thesis when new facts land

**Common failure modes:**
- Single guess about competitor presented as fact
- Strategy = "build what they build" or "add AI to current product"
- Vision is a feature list dressed as strategy
- Letting competitor framing drive the whole plan
- Thesis collapses on first probe; the candidate rebuilds it live rather than defending it

### Dimension 3: Prioritization & Tradeoffs

**What to look for:**
- A visible prioritization framework — quantitative (RICE, ICE), impact/effort, or clearly reasoned qualitative
- Explicit in-scope / out-of-scope list
- Named costs and tradeoffs — what each choice forecloses
- Reversibility and risk considerations
- Sequencing logic tied to value capture or risk reduction
- Pivots that name what gets dropped

**Common failure modes:**
- Everything is a priority; no framework visible
- Descoping is vague or missing
- Picks are assertions, not reasoned choices
- Pivots mid-session expand scope without naming descopes
- Framework named but never applied to the actual roadmap

### Dimension 4: AI-First Product Thinking

**What to look for:**
- AI as architecture, not feature — does it reshape what the product does or sit on top?
- Agent-as-persona thinking — are agents a first-class user type the product designs for?
- Human-in-the-loop design with confidence tiers, trust boundaries, and escalation paths
- Specificity: inputs, signals, model action, checkpoint, outcome
- Evidence of meaningful AI leverage in prep — frameworks or prototypes that could not have been produced without AI
- AI primitives in the vocabulary: evals, orchestration, retrieval, structured output, data flywheel, memory
- AI economics considered: cost, latency, quality tradeoffs

**Common failure modes:**
- Prototype exists but is just a UI with no architecture behind it
- "AI will do X" without mechanics
- No concept of confidence, autonomy levels, or human checkpoints
- Prep artifacts show AI was used for drawing, not thinking
- Buzzword usage without capability specificity
- Treating AI as a feature layer bolted onto existing workflows

**Important (2026 baseline):** AI-assisted prep and Claude-built prototypes are table stakes. Their presence does not raise the score. Their absence is a significant gap. Score the architecture and reasoning, not the demo polish.

### Dimension 5: Metrics & Outcomes

**What to look for:**
- North Star that connects user outcome to business outcome
- Leading indicators that move in days/weeks — not vanity signals like logins
- Business-tied lagging metrics (retention, expansion, win rate, revenue)
- Guardrails and counter-metrics — what would tell them they've broken something
- Awareness of measurement traps: vanity metrics, activity vs outcome, gameable signals
- Metrics framing that updates when the strategy pivots

**Common failure modes:**
- Metrics list = logins, MAU, engagement
- No connection to business outcome
- No counter-metrics, no guardrails
- Metrics framed as reporting artifacts, not decision inputs
- Leading indicators named but the "indicators" are vanity (logins, session length)
- Metrics don't update when the strategy pivots

---

## Session Dynamics (Observational — Qualifies Every Score)

Note these in the assessment. They do not produce a score; they qualify every score.

- **Who drove turning points** — candidate or interviewer? If the candidate only reached a strong conclusion after being walked there, credit the recovery but score at the level demonstrated without assistance.
- **Behavior under pushback** — hold position, update gracefully, collapse, or rigidify?
- **Specificity trajectory** — when probed, do they get more concrete or more abstract?
- **AI tool usage in the session itself** — did they reach for AI tools during Q&A to recover from gaps, or rely only on prepped artifacts?

**How Session Dynamics qualifies scores:** If most turning points came from the interviewer, the demonstrated craft level is a ceiling. Do not score a candidate at 3 on a dimension where they only reached 3 because you walked them there — score them at the level they started, and note the assist in the Session Dynamics section and in the dimension narrative.

---

## Craft Level Read

After scoring all five dimensions, synthesize a single-sentence **Craft Level Read**: what PM career level does this practicum most resemble, calibrated against the role level the candidate is interviewing for?

Use the average score as a starting point, then apply judgment:
- **Average ≥ 4.0** → Strong craft demonstrated (Level 4 overall)
- **Average 3.0–3.9** → Proficient craft (Level 3 overall)
- **Average 2.0–2.9** → Developing craft (Level 2 overall)
- **Average < 2.0** → Foundational gaps (Level 1 overall)
- **Any dimension at 5** with supporting scores → note the standout on that dimension
- **Any dimension at 1** on a load-bearing axis for the role → note the blocker regardless of average

If Session Dynamics materially changes the read (e.g., turning points came from the interviewer despite nominal scores), state that explicitly in the Craft Level Read. The written level should reflect demonstrated craft without assistance.

---

## Recommendation Guidance

The recommendation is the gap between demonstrated craft level and role level. Be precise about what the role level actually requires — use the job description and role title to calibrate.

**Typical role-level targets:**
- PM / Associate PM → Level 3 (Proficient)
- Senior PM → Level 4 (Strong)
- Staff PM / Principal PM → Level 5 (Exceptional) or high Level 4

**Recommendation mapping (gap between demonstrated and target):**

| Recommendation | When to Apply |
|----------------|---------------|
| **Strong Yes** | Demonstrated craft meets or exceeds role level; two or more dimensions above target; no material concerns from Session Dynamics |
| **Weak Yes** | Demonstrated craft is at the role level overall; one or two dimensions below target but addressable; Session Dynamics acceptable |
| **Weak No** | Demonstrated craft is one full level below role target; OR at target with meaningful gaps on load-bearing dimensions; OR at target but Session Dynamics shows passive pattern throughout |
| **Strong No** | Demonstrated craft is two or more levels below role target; OR foundational gaps (Level 1) on load-bearing dimensions; OR any average below 2.5 |

**Load-bearing dimensions shift by role.** For an AI-native product role, AI-First Product Thinking is load-bearing. For a platform role, Prioritization & Tradeoffs is load-bearing. For a new-category role, Strategic Thinking & Vision is load-bearing. Use the JD to identify which one or two dimensions are load-bearing for this specific role, and weight the recommendation accordingly.

**Do not inflate.** The most common scoring error is averaging your way past a weak dimension on a load-bearing axis. If the role requires strong strategic thinking and the candidate scored 2 there, a strong AI score does not rescue the recommendation.

---

## Green Flag Signals

- Pressure-tests the scenario framing rather than accepting it
- Distinguishes buyer from user; traces where revenue comes from
- Generates plural competitive hypotheses, each with a validation tactic and timeline
- Has a thesis on entry with teeth, not one assembled under prompting
- Visible prioritization framework applied to actual roadmap bets
- Treats agents as a first-class user persona, not just a feature
- Features described as end-to-end workflows with trigger, action, checkpoint, outcome
- North Star connects user outcome to business outcome
- Leading indicators that move in days, not vanity signals
- Prep artifacts show AI was used to think, not just to draw
- Updates position gracefully under Q&A pressure without collapsing
- Says "I don't know, but here's how I'd find out"
- Names tradeoffs explicitly — scope, time, risk, opportunity cost
- Reframes the scenario when reframing is warranted
- Gets more specific when probed, not more abstract

## Red Flag Signals

- Jumps to features before defining users or problem
- Generic personas and JTBD with no differentiation
- Single competitive hypothesis presented as fact
- Strategy = "build what they build" or "add AI to current product"
- Prototype exists but architecture behind it is thin
- AI as a chatbot bolt-on with no primitives
- Vision = parity feature list
- Metrics = usage counts with no business tie
- Leading indicators are vanity (logins, MAU, session length)
- No visible tradeoffs, no descoping, everything is "also"
- Framework named but never applied
- Collapses or rigidifies under Q&A pressure
- Cannot articulate what success looks like in user terms
- Strategy pivots without naming what gets dropped
- Every turning point comes from the interviewer
- Gets more abstract when probed, not more concrete

---

## Output

Produce a complete assessment using the `pm-practicum-assessment-template.md` format:
- All five dimensions rated 1–5 with level anchor noted and evidence-backed narrative
- Each dimension narrative references the matrix level explicitly ("This is a 2 because…")
- Craft Level Read sentence
- Standout Moments (3 bullets) and Concerns
- Session Dynamics observational note
- Overall recommendation (Strong Yes / Weak Yes / Weak No / Strong No)
- Summary (2-3 sentences) and Final Recommendation (1-2 sentences)

**Writing norms — follow exactly:**
- **Voice:** Write in first person as Jay. Use "I", "my", "me" throughout — never refer to Jay by name or write in third person.
- **Narrative length:** 2-4 sentences per dimension. State the key evidence, give the score rationale, move on. Do not pad.
- **Quotes:** Avoid direct quotes. If a specific phrase is worth noting, use 2-4 words in quotes at most. Maximum 1-2 such micro-quotes across the entire document.
- **Evidence style:** Paraphrase and synthesize — describe what the candidate demonstrated, not their exact words.
- **Take a stand:** Every narrative opens with an actual assessment — a view, a judgment, a read. Never open with "limited evidence" or "hard to assess". If confidence is lower, express it as a qualified opinion ("this felt thin to me because…") not as a refusal to assess.
- **Em dashes:** Use sparingly. No more than 1-2 em dashes in the entire document. Use a period or comma instead.
- **Level anchoring:** Reference the matrix explicitly. The score must be defensible against the rubric language.
- **Calibration discipline:** Apply the six Calibration Principles. Do not credit table stakes. Do not credit naming without applying. Do not let recovery raise the score past where the candidate started.
- **No fabrication:** Ground every claim in the practicum transcript and prompt. When evidence is thin for a dimension, reflect that in a lower score and note the gap.

## Related Skills

**Invoked by:**
- `process-practicum` workflow

**Related:**
- `pm-practicum-assessment-template.md` in `datasets/recruiting/templates/`
- `assess-pm-candidate` — the interview evaluation framework; these are complementary, not overlapping. The interview covers team fit, values, AI fluency in the abstract, and long-arc delivery record. The practicum covers live product craft. Run both, save both.
