# /project:api-design

## MANDATORY: Use the agentic-api-designer Skill

**You MUST use the `agentic-api-designer` skill located at `.claude/skills/workflow-agentic-api-designer/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using agentic-api-designer to define agent use cases and capability requirements — not to design the API shape"
2. **Read the skill**: Load `.claude/skills/workflow-agentic-api-designer/SKILL.md`
3. **Follow exactly**: Execute the skill as written

## Purpose

Define the jobs an AI agent must be able to accomplish with this feature, as jobs-to-be-done scenarios, plus a capability list engineering uses to design the actual API. This command does NOT produce an API specification — engineering owns endpoint naming, HTTP shape, payload schemas, and resource models.

## What You Produce

A single artifact: `{package}/ai-agent-scenarios.md` containing:
- TL;DR
- Agent Use Case Inventory (what jobs the agent can do)
- 3–5 scenarios written in prose (no HTTP, no JSON, no code)
- API Requirements for Engineering (bullet list of capabilities, not endpoints)
- Discoverability Principles (high-level)

## What You Do NOT Produce

- HTTP methods, paths, or endpoint specifications
- JSON request/response schemas
- Resource models with attribute types or state machines
- OpenAPI specs
- Pagination, filter, idempotency implementation details

If the output contains any of the above, you've gone too far. Rewrite as plain-language use cases or capability requirements.

## Prerequisites

- Context Brief must exist
- Press Releases should exist
- Living FAQ should exist (from `/project:devils-advocate`) — optional, provides audience context

## Arguments

- `--generate` — Full scenarios artifact from current upstream artifacts (default)
- `--scenarios` — Regenerate just the scenarios section against updated upstream artifacts
- `--review` — Critique an existing scenarios doc for use-case coverage and prose discipline (flag any HTTP/JSON/schema creep)

## Output

Written to the initiative's package folder: `datasets/product/packages/{YYYY}/{slug}/`

- `{package}/ai-agent-scenarios.md` — single artifact

## Guiding Principle

The PM defines what agents must be able to do. Engineering decides how. Every capability a human can do in the UI should also be possible for an agent — stated in use cases, not endpoint specs.
