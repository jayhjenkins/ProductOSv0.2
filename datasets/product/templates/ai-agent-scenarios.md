# AI Agent Scenarios: {FEATURE_NAME}

**Date:** {YYYY-MM-DD}
**Framing:** Agent jobs-to-be-done — what use cases the agent must support and what capabilities the API must expose. This is NOT an API design document. Engineering owns the HTTP shape, payload schemas, and endpoint naming.

<!--
Do NOT include:
  - HTTP methods, paths, or endpoint names
  - JSON request/response bodies or schemas
  - State machines or transition tables
  - Resource models with attribute types
  - OpenAPI references
  - Idempotency, pagination, or filtering specs

DO include:
  - Use cases in plain language
  - Scenarios written as prose steps the agent performs
  - A bullet list of capabilities the API must expose (no verbs or paths)
  - High-level discoverability principles
-->

---

## TL;DR

- **What agents can do with this feature:** {1–2 sentences covering the primary jobs}
- **Who the agents serve:** {HOAi, third-party agents, internal automation, etc.}

---

## Agent Use Case Inventory

One-line inventory of every job an agent should be able to accomplish. Write as "Agent can **{verb}** **{object}** to **{outcome}**."

- Agent can {verb} {object} to {outcome}
- Agent can {verb} {object} to {outcome}
- Agent can {verb} {object} to {outcome}
- ...

---

## Agent Scenarios

*3–5 end-to-end jobs. Each written in prose. No HTTP. No JSON. No code.*

### Scenario 1: {Scenario Title}

- **Job to be done:** {What the agent is trying to accomplish, stated as a user-facing outcome}
- **Trigger:** {When or why the agent initiates this — user request, event, schedule, etc.}
- **Inputs needed:** {What the agent must know or have on hand, in plain language — e.g., "the association ID, the current action type, and the customer's preferred language"}
- **Steps:**
  1. {What the agent does first, in plain language — e.g., "retrieves the association's current form configuration"}
  2. {Next step — e.g., "confirms the template is compatible with the association's action types"}
  3. {Next step — e.g., "applies the template and reports the result back to the user"}
- **Success criteria:** {What state exists when the job completes successfully}
- **Failure modes:**
  - **{What can go wrong, plain language}** → {how the agent should respond}
  - **{Another failure mode}** → {response}

### Scenario 2: {Scenario Title}

{Same structure as above}

### Scenario 3: {Scenario Title}

{Same structure as above}

---

## API Requirements for Engineering

*What the API MUST be able to do. Capabilities only — no shapes, no verbs, no paths. Engineering designs the actual endpoints.*

- {Capability, e.g., "list all associations accessible to the authenticated agent, with filters for status and management company"}
- {Capability, e.g., "retrieve the full current configuration of a single association"}
- {Capability, e.g., "apply a form template to an association in a single operation that either fully succeeds or fully rolls back"}
- {Capability, e.g., "enumerate the actions available for an association given its current state"}
- {Capability, e.g., "subscribe to events when an association's configuration changes"}

---

## Discoverability Principles

*High-level requirements for how agents discover and navigate the API. Not endpoint specs.*

- Agents must be able to enumerate the actions available on any resource from the resource itself — no out-of-band documentation required.
- Errors must include a remediation hint that tells the agent what to do next (retry, call another capability, or escalate to a human).
- Responses must be predictable — the same request returns the same shape regardless of context.
- Every write operation must be safely retryable.
- Every capability exposed to humans in the UI must also be available to agents.

---

## Changelog

| Date | Changes | By |
|------|---------|-----|
| {YYYY-MM-DD} | Initial scenarios | |
