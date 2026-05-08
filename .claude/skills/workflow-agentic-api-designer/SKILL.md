---
name: workflow-agentic-api-designer
description: Use when defining what AI agents must be able to do with a feature - produces a single ai-agent-scenarios.md artifact with use cases, jobs-to-be-done, and capability requirements for engineering. Does NOT prescribe API shape, HTTP verbs, endpoints, or schemas - engineering owns those.
---

# AI Agent Scenarios Designer

## Purpose

Define the jobs an AI agent must be able to accomplish with this feature, and the capabilities the API must expose to make those jobs possible. Stop short of prescribing the API itself.

- Capture agent use cases as jobs-to-be-done
- Write 3–5 end-to-end scenarios in prose — no HTTP, no JSON
- Enumerate the capabilities engineering must expose, without telling engineering how
- Surface discoverability and error-handling principles at a high level

## Governing Principle

> The PM defines what agents must be able to do. Engineering decides how. This doc is about use cases and capabilities — not endpoints, payloads, or resource models.

## Non-Goals

This skill does NOT produce:
- HTTP method and path specifications
- JSON request/response schemas
- Resource model tables with attribute types and constraints
- State machines or state-transition tables
- OpenAPI or JSON Schema specs
- Pagination, filtering, idempotency, or rate-limiting specs
- Anti-patterns lists targeting engineering choices

If you catch yourself writing `POST /api/v1/...`, a JSON block, or a schema table — stop. Rewrite as a capability requirement in plain language.

## When to Use

Activate when:
- User invokes `/project:api-design`
- Phase 3 of `/project:prep` or `/project:ship-it`
- Defining what an agent needs from any new feature
- Reviewing an existing feature's agent coverage

## Product Package Folder

All artifacts are read from and written to the initiative's package folder:

```
datasets/product/packages/{YYYY}/{slug}/
```

## Inputs Required

- **Context Brief** (`{package}/context-brief.md`) — customer problems and use cases
- **External Press Release** (`{package}/press-release-external.md`) — product capabilities and outcomes
- **Internal Press Release** (`{package}/press-release-internal.md`) — operational requirements
- **One-Pager** (`{package}/one-pager.md`) — scope and differentiators
- **Living FAQ** (`{package}/living-faq.md`) — if available, for audience context (use cases may reference CSM/PS/customer needs)
- Minimum: Context Brief and at least one press release

## Outputs Produced

- `{package}/ai-agent-scenarios.md` — single artifact covering use cases, scenarios, capability requirements, and discoverability principles

## Workflow

### Task 1: Use Case Inventory

Enumerate every job an agent should be able to accomplish with this feature. Write each as a plain-language sentence:

> Agent can **{verb}** **{object}** to **{outcome}**.

Example: "Agent can apply a form template to an association to onboard a new customer in one step."

Group by purpose (configuration, execution, reporting, admin) if it helps readability, but do NOT group by HTTP verb.

### Task 2: Agent Scenarios (Jobs-to-be-Done)

Write 3–5 end-to-end scenarios. Each in prose. No HTTP. No JSON.

For each scenario:

- **Job to be done:** the outcome in one sentence
- **Trigger:** what causes the agent to initiate this (user request, scheduled event, system trigger, etc.)
- **Inputs needed:** what the agent must know or have — in plain language (e.g., "the association ID, the current action type, and the customer's preferred language"). Do NOT use JSON or schema notation.
- **Acting on behalf of:** the person whose authority the agent is using — customer, user, homeowner, or *none* if the agent is acting for itself (internal automation, scheduled job). Agent's actions and the audit trail attach to this party. If a scenario can fire on behalf of more than one party (e.g., a CAM acting for a homeowner), name both and state which is the principal.
- **Latency expectation:** *realtime* (sub-second; conversational flow), *interactive* (a few seconds; user is waiting), or *background* (minutes-to-hours; user is not waiting). This shapes which capabilities can compose into one scenario — a realtime flow can't chain ten capability calls.
- **Consumer scope:** *internal agents only* (HOAi voice, internal automation), *external partners too*, or *both*. This shapes which tier the underlying capabilities sit in and what guardrails engineering will apply.
- **Steps:** 3–7 numbered prose steps describing what the agent does. Example: "retrieves the association's current form configuration", "confirms the template is compatible with the association's action types", "applies the template and reports the result back to the user". Do NOT write HTTP calls or code.
- **Success criteria:** what state exists when done
- **Failure modes:** 2–4 things that can go wrong, each with how the agent should respond (retry, fall back, escalate, abort)

### Task 3: API Requirements for Engineering

Bullet list of what the API MUST be able to do to support the scenarios above. Capabilities only. No verbs, paths, payloads, or schemas.

Example entries:
- "list all associations accessible to the authenticated agent, with filters for status and management company"
- "retrieve the full current configuration of a single association"
- "apply a form template to an association in a single operation that either fully succeeds or fully rolls back"
- "enumerate the actions available for an association given its current state"
- "subscribe to events when an association's configuration changes"

Engineering uses this list to design the actual endpoints. The PM is not prescribing the shape.

### Task 4: Discoverability Principles

High-level requirements for how agents discover and navigate the API. Plain language. No endpoint specs.

Standard set (adapt to this feature):
- Agents must be able to enumerate the actions available on any resource from the resource itself — no out-of-band documentation required.
- Errors must include a remediation hint that tells the agent what to do next (retry, call another capability, or escalate to a human).
- Responses must be predictable — the same request returns the same shape regardless of which agent or which user is calling, and regardless of upstream context the caller can't see.
- Every write operation must be safely retryable.
- Every capability exposed to humans in the UI must also be available to agents.
- Every action taken by an agent must be retrievable on request — by user, customer, conversation, or call. The audit trail is part of the contract, not an afterthought. If a customer asks "what did your AI do for me on Tuesday?", the answer must exist.
- When the agent is acting on behalf of someone (per the scenario's *Acting on behalf of* field), the API must carry that identity end-to-end and never silently substitute it with a system identity mid-request.

## Arguments

- `--generate` — Full scenarios artifact from current upstream artifacts (default)
- `--scenarios` — Regenerate just the scenarios section against updated upstream artifacts
- `--review` — Critique an existing scenarios doc for use-case coverage and prose discipline (flag any HTTP/JSON/schema creep)

## Quality Criteria

- [ ] 3–5 scenarios written in prose — no HTTP, no JSON, no code blocks
- [ ] Use Case Inventory covers every capability implied by the press releases
- [ ] API Requirements section is bullet-list capabilities only — no verbs, paths, or schemas
- [ ] Each scenario has: job, trigger, inputs, acting-on-behalf-of, latency expectation, consumer scope, steps, success criteria, failure modes
- [ ] Failure modes include the agent's intended response for each
- [ ] Discoverability Principles present, including auditability/retrievability and on-behalf-of identity persistence
- [ ] No resource model, state machine, or endpoint specification anywhere in the doc

## Failure Modes

| Failure | Detection | Fix |
|---------|-----------|-----|
| API prescription creep | Any `GET/POST/PUT/DELETE`, `/api/...`, or JSON block | Delete the offending section; rewrite as prose capability |
| Resource-model thinking | Attribute tables with types and constraints | Delete; scope is use cases, not data modeling |
| State-machine creep | State transition tables with triggers | Delete; describe state changes in prose within scenarios |
| Call-sequence docs | Scenarios written as numbered API calls | Rewrite as plain-language "agent does X, then Y" |
| Incomplete failure modes | Scenarios that only describe the happy path | Add 2–4 failure modes per scenario with agent response |
| Vague capabilities | "Agent needs the right data" | Rewrite specifically: "list active associations for the authenticated agent" |
| Missing on-behalf-of | Scenario doesn't say whose authority the agent is using | Add the *Acting on behalf of* line — even if the answer is *none*, name it explicitly |
| No latency framing | Scenario silent on how fast the user expects the response | Add the *Latency expectation* line — realtime / interactive / background |
| Audit gap | Discoverability section silent on whether actions are retrievable later | Add the auditability principle — agent actions must be retrievable by user, customer, conversation, or call |

## Interaction Model

- **Agent generates the scenarios doc autonomously** from upstream artifacts
- **PM reviews for business logic accuracy** — are the use cases right? Are the scenarios realistic?
- **PM decides**: which use cases are required vs. aspirational, what business rules apply, which failure modes matter
- **Engineering owns**: endpoint shape, HTTP verbs, payload schemas, authentication/authorization mechanics, pagination, idempotency implementation

## Related Skills

- `vision-clarifier`: Produces press releases that define capabilities
- `devils-advocate`: Runs in parallel — produces audience-focused FAQ (separate concern)
- `prd-creation`: Inherits scenarios into the PRD's Agent/API Scenarios section
- `red-team-reviewer`: Reviews scenarios for completeness and validates that all press release capabilities map to at least one scenario
