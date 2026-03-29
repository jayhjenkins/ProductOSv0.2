# Agent Workflow Scenarios: {FEATURE_NAME}

**Date:** {YYYY-MM-DD}
**API Design Reference:** `agentic-api-design.md`

> These scenarios demonstrate how an AI agent would use the API to accomplish common tasks end-to-end, including decision points and error handling.

---

## Scenario 1: {Scenario Title}

**Goal:** {What the agent is trying to accomplish}

**Preconditions:**
- {What state must exist before starting}
- {Authentication/authorization requirements}

### Steps

**Step 1: {Action description}**
```http
{METHOD} /api/v1/{path}
Content-Type: application/json

{
  "{field}": "{value}"
}
```

**Response (200):**
```json
{
  "{field}": "{value}",
  "{field}": "{value}"
}
```

**Step 2: {Action description}**

> **Decision Point:** If `response.{field}` equals `{value_A}`, proceed to Step 3. If `{value_B}`, skip to Step 4.

```http
{METHOD} /api/v1/{path}
```

**Response (200):**
```json
{
  "{field}": "{value}"
}
```

**Step 3: {Action description}**

> **Error Handling:** If this call fails with `{ERROR_CODE}`, retry up to 3 times with exponential backoff. If `{OTHER_ERROR_CODE}`, escalate to human with the error message.

```http
{METHOD} /api/v1/{path}
```

**Expected Outcome:** {What state exists when this scenario completes successfully}

---

## Scenario 2: {Scenario Title}

{Same structure as Scenario 1}

---

## Scenario 3: {Scenario Title}

{Same structure as Scenario 1}

---

## Scenario Summary

| # | Scenario | Steps | Decision Points | Error Handlers | Complexity |
|---|----------|-------|-----------------|----------------|------------|
| 1 | {Title} | {N} | {N} | {N} | {Simple/Moderate/Complex} |
| 2 | {Title} | | | | |
| 3 | {Title} | | | | |

---

## Common Error Handling Patterns

| Error Code | Meaning | Agent Action |
|------------|---------|-------------|
| `{CODE}` | {Description} | {What agent should do} |
| `RATE_LIMITED` | Too many requests | Backoff and retry after `Retry-After` header value |
| `INVALID_STATE` | Resource not in correct state for this action | Call state inspection endpoint, re-evaluate |
| `NOT_FOUND` | Resource doesn't exist | Verify resource ID, check if deleted |

---

## Changelog

| Date | Changes | By |
|------|---------|-----|
| {YYYY-MM-DD} | Initial scenarios | |
