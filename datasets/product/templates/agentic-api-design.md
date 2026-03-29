# Agentic API Design: {FEATURE_NAME}

**Date:** {YYYY-MM-DD}
**Design Philosophy:** Agent-first. Every design decision asks: "Can an agent figure this out and use it without human intervention?"
**Primary Consumer:** AI Agents

---

## Design Principles

1. **Self-describing** — An agent reading the schema understands everything
2. **Composable** — Each endpoint does one thing cleanly, returns everything needed for next call
3. **Idempotent** — Safe to retry any operation
4. **100% coverage** — If a human can do it in the UI, an agent can do it via API
5. **Actionable errors** — Every error tells the agent how to fix it
6. **Predictable** — Same input always produces same response shape

---

## Capability Inventory

| Domain | Capability | HTTP Method | Endpoint | Description |
|--------|-----------|-------------|----------|-------------|
| Configuration | {Capability 1} | {GET/POST/PUT/DELETE} | {/api/v1/...} | {What it does} |
| Configuration | {Capability 2} | | | |
| Execution | {Capability 3} | | | |
| Execution | {Capability 4} | | | |
| Reporting | {Capability 5} | | | |
| Admin | {Capability 6} | | | |

---

## Resource Model

### {Resource 1}

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `id` | string (UUID) | Unique identifier | Read-only, auto-generated |
| {attribute} | {type} | {description} | {constraints} |

**Lifecycle:**
```
Created → Active → {domain-specific states} → Archived
```

**State Transitions:**

| From | To | Trigger | Who Can Trigger |
|------|----|---------|-----------------|
| Created | Active | {action} | {role/system} |
| Active | {state} | {action} | |

**Relationships:**
- Has many: {related resource}
- Belongs to: {parent resource}

### {Resource 2}

{Same structure as above}

---

## Endpoint Specifications

### {Endpoint Name}

**`{METHOD} {/api/v1/path}`**

{One-sentence description of what this endpoint does.}

**Request:**
```json
{
  "{field}": "{type} — {description}",
  "{field}": "{type} — {description}"
}
```

**Response (200):**
```json
{
  "{field}": "{type} — {description}",
  "{field}": "{type} — {description}"
}
```

**Error Responses:**

| Status | Error Code | Message | Remediation |
|--------|-----------|---------|-------------|
| 400 | `{MACHINE_CODE}` | {Human message} | {What the agent should do} |
| 404 | `{MACHINE_CODE}` | | |
| 409 | `{MACHINE_CODE}` | | |

**Idempotency:** {Safe to retry? Idempotency key required? How?}

**Pagination:** {If list endpoint: cursor-based, page params, max per page}

**Filtering & Sorting:** {Available filter params, sort options}

---

## Agent Discoverability

### OpenAPI Spec
{Reference to the OpenAPI/JSON Schema specification file}

### Capability Discovery
**`GET /api/v1/capabilities`**
Returns the full list of available actions, their required inputs, and current state context.

### State Inspection
**`GET /api/v1/{resource}/{id}/available-actions`**
Returns what actions are available from the current state of the resource.

### Webhooks & Events

| Event | Trigger | Payload Description |
|-------|---------|---------------------|
| `{resource}.{action}` | {When this fires} | {What the payload contains} |
| | | |

---

## Anti-Patterns (What This API Must NOT Do)

1. **No multi-step wizards** — Every operation completes in a single call
2. **No "confirm" steps** — Use idempotency keys, not human confirmation
3. **No ambiguous enums** — Every value is documented with clear meaning
4. **No context-dependent response shapes** — Same endpoint always returns same structure
5. **No undocumented side effects** — Every side effect is in the schema
6. **No UI-only capabilities** — 100% of functionality available via API

---

## Changelog

| Date | Changes | By |
|------|---------|-----|
| {YYYY-MM-DD} | Initial API design | |
