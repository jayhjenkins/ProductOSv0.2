---
name: workflow-red-team-reviewer
description: Use when validating PRDs through adversarial review - performs slow-walk scenario testing, architecture stress tests, agentic API review, persona-lens reviews, and cross-document consistency audits with severity-classified findings
---

# Red Team Reviewer

## Purpose

Conduct granular, adversarial review of the complete PRD:
- Walk through every scenario step by step
- Find broken edges, missing error states, scaling bottlenecks
- Validate API design for agent completeness
- Pressure-test from multiple user persona perspectives
- Audit cross-document consistency
- Make the ambitious plan ROBUST, not smaller

## Governing Principle

> Before building, the product must survive a searing critique. Not to cut scope — but to find the gaps, the failure modes, and the places where the user experience breaks down. The goal is to make the ambitious plan *robust*, not to make it *smaller*.

## When to Use

Activate when:
- User invokes `/project:red-team`
- Phase 5 of `/project:build` or `/project:ship-it`
- PRD is complete and needs validation before engineering handoff
- After expansion proposals have been accepted and folded into PRD

## Product Package Folder

All artifacts are read from and written to the initiative's package folder:

```
datasets/product/packages/{YYYY}/{slug}/
```

## Inputs Required

- **Complete PRD** — in `{package}/` and `datasets/product/prds/{YYYY}/`
- **Context Brief** (`{package}/context-brief.md`)
- **Press Releases** (`{package}/press-release-external.md`, `{package}/press-release-internal.md`)
- **Living FAQ** (`{package}/living-faq.md`) — for reference only; this skill does NOT write back to it
- **AI Agent Scenarios** (`{package}/ai-agent-scenarios.md`)
- **Expansion Proposals** (`{package}/expansion-proposals.md`) — if accepted items were folded in
- Minimum: Complete PRD and AI Agent Scenarios must exist

## Outputs Produced

- `{package}/red-team-report.md` — Severity-classified findings with recommended fixes. This is the ONLY file this skill writes to. It does NOT update the Living FAQ — any abuse/misuse, security, or harm-scenario concerns go in the red team report's Harm Scenarios section.

## Workflow

### Task 1: Slow Walk Execution

For **each user scenario** in the PRD:
1. Walk through every step sequentially
2. At each step, ask: **"What can go wrong here?"**
3. Identify:
   - Missing error states (what if this fails?)
   - Unclear feedback (how does the user know what happened?)
   - Ambiguous language (could this be interpreted differently?)
   - Broken transitions (does step N connect cleanly to step N+1?)
   - Performance bottlenecks (what if this takes 30 seconds?)
   - Accessibility issues (can all users complete this step?)
4. Document each finding with specific PRD section reference

### Task 2: Architecture Stress Test

Review the technical architecture for:
- **Single points of failure**: What breaks everything if it goes down?
- **Scaling bottlenecks**: What breaks at 10x? 100x? 1000x?
- **Data consistency risks**: Where can data get out of sync?
- **Security vulnerabilities**: At system boundaries, at data handoff points
- **Third-party dependency risks**: What if [vendor] has an outage or changes their API?

### Task 3: AI Agent Scenarios Review

Review `ai-agent-scenarios.md` for coverage and realism:
- Does every user scenario in the PRD have a corresponding agent scenario or use case?
- Are the scenarios realistic — does the prose describe something an agent could actually do?
- Are failure modes described for each scenario with the agent's intended response?
- Do the API Requirements cover every capability implied by the PRD and press releases?
- Are there UI-only capabilities in the PRD that lack an agent use case?

Do NOT review HTTP shape, endpoint naming, payload schemas, or state machines — those are engineering's responsibility, not this doc's scope.

### Task 4: Persona-Lens Review (when `--personas` flag used)

Adopt 3–5 distinct user profiles drawn from the Context Brief:

For each persona:
- Read the user scenarios as that specific person
- Assess: Does the described flow make sense for someone with their technical literacy, goals, and patience level?
- Flag places where the PRD describes an experience that would confuse, frustrate, or lose this persona
- Flag places where optimizing for one persona degrades another's experience

**Important**: This is a DOCUMENT REVIEW, not a software test. Output is "the PRD describes X, but persona Y would struggle because Z" — not "I clicked the button and nothing happened."

### Task 5: Consistency Audit

Check for contradictions across the full artifact set:
- Do user scenarios match capability specifications?
- Do success metrics align with stated goals?
- Do non-goals conflict with any proposed features?
- Do the AI Agent Scenarios cover ALL described user flows?
- Do the press releases promise anything the PRD doesn't deliver?
- Does the Living FAQ contain answered questions that contradict the PRD?

### Task 6: Findings Report

Produce structured report using template `datasets/product/templates/red-team-report.md`:

**Severity Classification:**

| Severity | Meaning | Action Required |
|----------|---------|-----------------|
| `critical` | Product breaks, data loss, security vulnerability | **Must fix before proceeding** |
| `major` | User experience degrades significantly | Track, fix before launch |
| `minor` | Polish issue, not user-facing | Fix if time permits |
| `question` | Needs clarification, not clearly a bug | PM must clarify |

**Each finding includes:**
- Unique ID for tracking
- PRD section reference
- Description of the issue
- Severity classification
- Recommended fix (NOT "cut this feature" — "fix it" or "improve it")

**Summary statistics**: Count by severity

## Arguments

- `--full` — Complete review, all tasks (default)
- `--scenario "name"` — Review a specific user scenario
- `--architecture` — Focus on architecture stress test
- `--agent-scenarios` — Focus on AI Agent Scenarios coverage review
- `--personas` — Run persona-lens review
- `--consistency` — Focus on cross-document consistency

## The Iron Rule

**Must NOT recommend cutting features. Must recommend FIXING or IMPROVING them.**

The goal is to make the ambitious plan robust. If something is broken, fix it. If something is unclear, clarify it. If something is missing, add it. Never shrink the scope.

## Quality Criteria

- [ ] Every user scenario walked step by step with findings documented
- [ ] Findings classified by severity with accurate counts
- [ ] Each finding has specific PRD section reference and recommended fix
- [ ] Architecture stress test covers 10x/100x/1000x dimensions
- [ ] AI Agent Scenarios review confirms every user scenario has agent coverage
- [ ] No finding recommends cutting a feature — all recommend fixes
- [ ] Consistency audit covers all artifact cross-references
- [ ] Summary statistics present

## Failure Modes

| Failure | Detection | Fix |
|---------|-----------|-----|
| Surface-level review | Findings summarize PRD instead of challenging it | Deeper analysis at each step |
| Scope-cutting recommendations | "Remove this feature" in findings | Rewrite as "fix this aspect of the feature" |
| Missing failure modes | No consideration of network, API, data failures | Add failure mode analysis per scenario |
| Generic findings | Could apply to any product | Make findings specific to this product's design |
| No actionable recommendations | "This is a problem" without "do this to fix it" | Add specific fix for every finding |

## Interaction Model

- **Agent conducts review autonomously** — does not ask PM for permission to be critical
- **PM reviews findings** — confirms severity, approves recommended fixes
- **Critical findings block progression** — PM must address before Phase 6
- **Major findings are tracked** — do not block, but are recorded
- **Agent does NOT write to the Living FAQ** — all red team concerns (including abuse/misuse and harm scenarios) go into `red-team-report.md` only. The Living FAQ stays focused on business-user and customer questions.

## Gate

All `critical` findings must be addressed (fixes incorporated into PRD). `Major` findings tracked but don't block. PRD updated with revisions before proceeding to Phase 6.

## Related Skills

- `prd-creation`: Produces the PRD being reviewed
- `ambition-expander`: Proposals that were accepted are now in the PRD
- `agentic-api-designer`: Produces the AI Agent Scenarios reviewed for coverage
- `devils-advocate`: Produces the Living FAQ (read-only for this skill)
- `swag-modeler`: Next phase — business case built from validated PRD
