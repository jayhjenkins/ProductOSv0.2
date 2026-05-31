---
name: quality-neutral-reporting
description: Use when investigating, diagnosing, researching, or synthesizing — enforces neutral framing so the agent reports what the evidence actually shows instead of confirming a presupposed outcome, and makes "no issue found" a valid, complete result
allowed-tools: Read, Grep, Glob
---

# Neutral Reporting

## The Iron Law

**REPORT WHAT YOU OBSERVE — DON'T MANUFACTURE A FINDING TO SATISFY THE REQUEST.**

Truth-seeking work (diagnosis, research, synthesis) is sycophancy-prone: asked to
"find the problem," an agent will invent one rather than return empty-handed. A
fabricated root cause or a manufactured insight is worse than no finding — it flows
straight into a decision. This gate exists to keep investigation honest.

This is the opposite stance from *adversarial* skills (`workflow-red-team-reviewer`,
`workflow-devils-advocate`, `workflow-ambition-expander`, the `ship-it`/`build`
"find every gap" prompts). Those are biased by design — their job is to hunt. Do NOT
apply this gate to them. Apply it to skills whose job is to report reality accurately.

## When to Use This Skill

Activate automatically when:
- Diagnosing a metric change (`metric-root-cause-diagnosis`, `workflow-metric-diagnosis`)
- Researching, investigating, analyzing, or auditing (researcher / analyst work)
- Synthesizing signals from meetings, tickets, or calls
- Any time the prompt presupposes an outcome ("why did X get worse", "find the bug")

## The Three Rules

### 1. Neutral framing

Investigate "what changed and why," not "why it got worse." Ask "what does the
evidence show here," not "what's wrong here." Strip the presupposed conclusion out of
your own framing before you start. A leading question manufactures a leading answer.

| Leading (avoid) | Neutral (use) |
|---|---|
| "Why did the metric drop?" | "What changed, and what most likely explains it?" |
| "Find the root cause." | "Identify the most likely cause(s) — including that the change was expected or benign." |
| "Confirm the bug." | "Determine whether a defect exists, and if so where." |
| "What's wrong with this?" | "What does this do, and where (if anywhere) does it fall short?" |

### 2. A clean result is a valid result

These are **complete, acceptable answers** — never pad them into a false finding:
- "No issue found."
- "The change is within expected variation / seasonal / a known release effect."
- "The logic is sound; no defect identified."
- "The data does not support a conclusion. Here is what would be needed to reach one."

An empty or null result delivered honestly is a success, not a failure to be hidden.

### 3. Report, then judge

State observations before conclusions. Express conclusions with calibrated confidence
("the evidence points to X, though Y is unverified"), not manufactured certainty. If
two explanations fit the data equally, say so and name the data that would separate them.

## Anti-Rationalization Blocks

| Rationalization | Reality |
|---|---|
| "They asked me to find a problem, so there must be one." | They asked you to *look*. "Nothing found" answers the request. |
| "An empty report looks like I didn't do the work." | The investigation IS the work. Show the method, then the null result. |
| "I'll pick the most plausible cause to be helpful." | Plausible ≠ supported. Unsupported guesses presented as findings mislead decisions. |
| "The deliverable has a 'root cause' field, so I must fill it." | Write "none identified — expected variation" in the field. |

## Success Criteria

Neutral reporting is satisfied when:
- The framing of the investigation does not presuppose its conclusion.
- Every conclusion is traceable to a specific observation, with confidence qualified.
- "No issue / expected variation" was available as an outcome and used if it fit.
- No finding was invented to fill a template or satisfy the phrasing of the request.

## Related Skills

- **metric-root-cause-diagnosis** / **workflow-metric-diagnosis** — apply this gate before diagnosing.
- **quality-citation-compliance** — pairs with this: neutral framing + sourced claims.
- **workflow-red-team-reviewer**, **workflow-devils-advocate**, **workflow-ambition-expander** — intentionally biased; this gate does NOT apply to them.
