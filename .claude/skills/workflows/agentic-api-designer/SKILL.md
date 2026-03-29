---
name: agentic-api-designer
description: Use when designing API interfaces for a feature - creates agent-first API design with Stripe-level quality optimized for machine callers, including resource models, endpoint specs, discoverability layers, and agent workflow scenarios
---

# Agentic API Designer

## Purpose

Design API interfaces where agents are the primary consumer:
- Stripe-level quality, optimized for machine callers
- Self-describing schemas that agents can read and understand
- Composable operations for agent chaining
- 100% feature coverage — no UI-only capabilities
- Actionable error responses for agent self-correction

## Governing Principle

> Agents are the primary consumer, not human developers. Every design decision should ask: "Can an agent figure this out and use it without human intervention?"

## When to Use

Activate when:
- User invokes `/project:api-design`
- Phase 3 of `/project:prep` or `/project:ship-it`
- Designing API surface for any new feature
- Reviewing existing API for agent-friendliness

## Product Package Folder

All artifacts are read from and written to the initiative's package folder:

```
datasets/product/packages/{YYYY}/{slug}/
```

## Inputs Required

- **Context Brief** (`{package}/context-brief.md`) — customer problems and use cases
- **External Press Release** (`{package}/press-release-external.md`) — product capabilities and outcomes
- **Internal Press Release** (`{package}/press-release-internal.md`) — operational requirements
- **Living FAQ** (`{package}/living-faq.md`) — edge cases and concerns (if available)
- **One-Pager** (`{package}/one-pager.md`) — scope and differentiators
- Minimum: Context Brief and at least one press release

## Outputs Produced

- `{package}/agentic-api-design.md` — Full API design document
- `{package}/api-agent-scenarios.md` — End-to-end agent workflow examples

## Workflow

### Task 1: Capability Inventory

From the press releases, FAQ, and Context Brief, enumerate **every discrete action** a user can take with this feature. This becomes the exhaustive list of things the API must support.

Group by domain:
- **Configuration**: Setup, settings, preferences
- **Execution**: Core operations, transactions, workflows
- **Reporting**: Queries, analytics, exports
- **Admin**: User management, permissions, audit

Output: Table of capabilities with domain grouping.

### Task 2: Resource Model Design

Define the core resources (nouns) the API exposes:

For each resource:
- **Name and description**
- **Attributes** (fields with types, descriptions, constraints)
- **Relationships** to other resources
- **Lifecycle**: Created → Active → [domain-specific states] → Archived/Deleted
- **State transitions**: What triggers each transition? Who/what can trigger it?

Produce a clear entity-relationship summary.

### Task 3: Endpoint Specification

For each capability from the inventory, define:

- **HTTP method and path** (RESTful, predictable, consistent naming)
- **Request payload schema** with field-level descriptions, types, constraints, and examples
- **Response payload schema** with field-level descriptions
- **Error response schemas** with:
  - Machine-readable error code (e.g., `INVALID_STATE_TRANSITION`)
  - Human-readable message
  - Remediation instruction (what the agent should do to fix it)
  - Related documentation link
- **Idempotency behavior**: Which operations are safe to retry? How? (idempotency keys?)
- **Pagination strategy** for list endpoints (cursor-based preferred)
- **Filtering and sorting** capabilities

### Task 4: Agent Discoverability Layer

Design the meta-API that helps agents understand what's available:

- **OpenAPI/JSON Schema spec**: Complete and accurate — agents will read this to plan calls
- **Capability discovery**: Endpoint that answers "what can I do with this feature?"
- **State inspection**: Endpoints that answer "what is the current state of X and what actions are available from here?"
- **Webhook/event contracts**: What events does this feature emit? What do payloads look like? How to subscribe/unsubscribe?

### Task 5: Agent Workflow Scenarios

Write 3–5 end-to-end scenarios using template `datasets/product/templates/api-agent-scenarios.md`:

Each scenario includes:
- **Goal**: What the agent is trying to accomplish
- **Preconditions**: What state must exist before starting
- **Step-by-step API call sequence** with request/response examples
- **Decision points**: "If the response contains X, call Y; otherwise call Z"
- **Error handling**: "If this call fails with error code A, retry; if error code B, escalate to human"
- **Expected outcome**: What state exists when done

### Task 6: Anti-Patterns Document

Explicitly list what the API must NOT do:

- No endpoints that require multi-step UI-style wizards
- No "confirm" steps that assume a human is watching (use idempotency keys instead)
- No ambiguous enums or magic strings — every value is documented
- No endpoints that return different shapes based on context (predictable contracts always)
- No undocumented side effects
- No endpoints that require knowledge not in the schema to use correctly

## Arguments

- `--generate` — Full API design from current artifacts (default)
- `--resources` — Generate just the resource model
- `--scenarios` — Generate agent workflow scenarios only
- `--review` — Critique existing API design for agent-friendliness

## Quality Criteria

- [ ] Every capability from press releases has API coverage
- [ ] All endpoints have complete request/response schemas with field descriptions
- [ ] Error responses include machine-readable codes AND remediation instructions
- [ ] At least 3 end-to-end agent scenarios with decision points
- [ ] Anti-patterns document present
- [ ] Resource model has clear lifecycle definitions for every entity
- [ ] Pagination, filtering, and sorting defined for all list endpoints
- [ ] Idempotency behavior documented for every write operation
- [ ] No UI-only capabilities — 100% API coverage

## Failure Modes

| Failure | Detection | Fix |
|---------|-----------|-----|
| UI-first thinking | Endpoints that assume human interaction flow | Redesign for agent callers |
| Generic error responses | "400 Bad Request" without details | Add structured error objects with remediation |
| Incomplete coverage | Capabilities in press release without API endpoints | Add missing endpoints |
| Simple scenarios | Agent scenarios without decision points or error handling | Add branching and error cases |
| Missing lifecycle | Resources without state transitions | Define full lifecycle |
| Ambiguous contracts | Response shape varies by context | Standardize to predictable contracts |

## Interaction Model

- **Agent generates the API design autonomously** from upstream artifacts
- **PM reviews for business logic accuracy** — are the capabilities right?
- **Agent decides**: Endpoint structure, naming conventions, error codes, pagination strategy
- **PM decides**: Business rules, state transition permissions, which capabilities are required vs. optional

## Design Principles (Non-Negotiable)

1. **Self-describing**: An agent reading the schema understands everything
2. **Composable**: Each endpoint does one thing cleanly, returns everything needed for next call
3. **Idempotent**: Safe to retry any operation
4. **100% coverage**: If a human can do it in the UI, an agent can do it via API
5. **Actionable errors**: Every error tells the agent how to fix it
6. **Predictable**: Same input always produces same response shape

## Related Skills

- `vision-clarifier`: Produces press releases that define capabilities
- `devils-advocate`: Runs in parallel, surfaces edge cases that inform error handling
- `prd-creation`: API design feeds into Agent/API Scenarios section of PRD
- `red-team-reviewer`: Reviews API design for completeness in Phase 5
