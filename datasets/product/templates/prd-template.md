# {PROJECT_NAME}

**Product Requirements Document**

**STATUS:** 🚧 Drafting

> {One to three line description of the project or initiative for the reader's quick context.}

---

## Background

{Add context or additional details about why this project exists and what problem it solves.}

---

## DACE & Key Resources

### DACE

| Role | Person/Team |
|------|-------------|
| **Driver** | {Who is driving this initiative} |
| **Approver** | {Who has final approval authority} |
| **Contributors** | {Who is contributing to the work} |
| **Escalation Path** | {Where to escalate blockers or decisions} |

### Driving Teams

| Team | Product Mgt | PMO | Engineering | Design |
|------|-------------|-----|-------------|--------|
| {Team 1} | | | | |
| {Team 2} | | | | |

### Contributing Teams

| Team | Product Mgt | PMO | Engineering | Design |
|------|-------------|-----|-------------|--------|
| {Team 3} | | | | |
| {Team 4} | | | | |

### Other Stakeholders

| Function | Contact |
|----------|---------|
| Legal | |
| Security | |

### Key Resources & Links

| Resource | Link |
|----------|------|
| Slack Channels | |
| Experience Design & Content (Figma) | |
| Architecture & Technical Design Docs | |
| Project Plan / Tracking (JIRA) | |
| Additional Links | |

---

## Objectives / Goals

### For {Customer / Partner / Developer / etc.}

> {Summary objective / customer statement}

| Element | Description |
|---------|-------------|
| **I am** | {A narrow description of the customer (not you!) that highlights their motivations, attributes and/or characteristics} |
| **I'm trying to** | {Desired outcome} |
| **But** | {Problem/barrier} |
| **Because** | {Root cause} |
| **Which makes me feel** | {Emotion} |

### Success Measure & Opportunity Sizing

{A criteria or metric which will indicate whether the above objective/goal is successful. Can also include or be limited to an overall Acceptance criteria for the project or product. Includes a rough opportunity sizing which could link to a full analysis spreadsheet.}

| Dimension | Metric/Target |
|-----------|---------------|
| User Experience | |
| Technical Capabilities | |
| Opportunity Sizing | |

---

## Use Cases & Input Goals

### In Scope

{In scope use cases and input goals to be supported with a short description}

| Use Case ID | Description |
|-------------|-------------|
| UC-1 | |
| UC-2 | |
| UC-3 | |

### Agent / API Scenario Coverage

> Every capability described above should also be evaluated for agent and API consumers. For each use case, note whether full API coverage exists, and capture any agent-specific scenarios that differ from the human-user path.

| Use Case ID | Human Scenario | Agent / API Scenario | Full API Coverage? | Notes |
|-------------|----------------|----------------------|--------------------|-------|
| UC-1 | {Human user flow} | {Equivalent API / agent flow} | Yes / No / Partial | |
| UC-2 | | | | |
| UC-3 | | | | |

{Add any agent-only or API-only scenarios that do not have a direct human-user counterpart.}

| Agent / API Scenario ID | Description | API Coverage | Notes |
|-------------------------|-------------|--------------|-------|
| API-1 | | | |
| API-2 | | | |

### Out of Scope

{Items that are explicitly out of scope}

| Item | Reason |
|------|--------|
| | |

### Non-Goals

> Non-goals are distinct from out-of-scope items. Out-of-scope items are simply not part of this effort. Non-goals define what this product **explicitly does not aim to do**, even if someone might reasonably expect it to. Stating non-goals prevents misaligned expectations and scope drift.

| Non-Goal | Why It Is a Non-Goal |
|----------|----------------------|
| | |

---

## Requirements

> **Priority Key (Build Phase):**
> - **[P0] Foundation phase** — Core capabilities that everything else depends on. Ships first.
> - **[P1] Expansion phase** — Capabilities that broaden reach, cover more use cases, or add integrations. Ships second.
> - **[P2] Polish phase** — Refinements, optimizations, and delighters that round out the experience. Ships third.
>
> All three phases ship. Priority determines **sequence**, not whether something gets built.
>
> Note: Include concept mock-ups, designs, functional flow diagrams as helpful. Note external dependencies.

### Milestone 1: {Name/Summary}

| P | Dependent Teams | User Story / Requirement | Acceptance Criteria / Expected Behavior | Figma | JIRA |
|---|-----------------|--------------------------|----------------------------------------|-------|------|
| P0 | {Your Team}, {Another Team} | In order to accomplish X, we will build Y. | How we know the requirements are met. | | |
| P1 | | | | | |
| P2 | | | | | |

### Milestone 2: {Name/Summary}

| P | Dependent Teams | User Story / Requirement | Acceptance Criteria / Expected Behavior | Figma | JIRA |
|---|-----------------|--------------------------|----------------------------------------|-------|------|
| P0 | | | | | |
| P1 | | | | | |
| P2 | | | | | |

---

## Build Sequence

> Everything in this PRD ships. The build sequence determines the **order** in which capabilities are delivered, not whether they are delivered. Each phase builds on the previous one, and all phases are planned from the start.

### Foundation (P0)

> The structural core. These capabilities must land first because everything else depends on them. Focus: get the architecture right, deliver the primary user path end-to-end.

| Seq | Requirement / Capability | Depends On | Target Milestone | JIRA |
|-----|--------------------------|------------|------------------|------|
| F-1 | | — | | |
| F-2 | | F-1 | | |
| F-3 | | | | |

### Expansion (P1)

> Broaden the product surface. These capabilities extend the foundation to more use cases, user types, integrations, or platforms. They ship once the foundation is stable.

| Seq | Requirement / Capability | Depends On | Target Milestone | JIRA |
|-----|--------------------------|------------|------------------|------|
| E-1 | | F-{n} | | |
| E-2 | | | | |
| E-3 | | | | |

### Polish (P2)

> Refinement and delight. These capabilities improve performance, add convenience features, and smooth rough edges. They ship once expansion is in place.

| Seq | Requirement / Capability | Depends On | Target Milestone | JIRA |
|-----|--------------------------|------------|------------------|------|
| R-1 | | E-{n} | | |
| R-2 | | | | |
| R-3 | | | | |

---

## Milestones and Timeline

| Milestone / Phase | Team(s) Leading & Contributing | One liner for the milestone to be delivered | Expected Delivery Timeline |
|-------------------|--------------------------------|---------------------------------------------|---------------------------|
| {Architecture, Schemas, Planning} | | | |
| {Design} | | | |
| {Capability Enablement X in Platform Y} | | | |
| {Testing & QA} | | | |
| {Launch} | | | |

---

## Metrics and Learning Agenda

> This section is used to list all of the metrics that will be used to measure the success of the implementation. Ensure to provide guidance if these metrics exist or need to be built. Make sure to incorporate guardrail metrics as well.

| Goals and Hypotheses | Signals | Metrics |
|----------------------|---------|---------|
| {What do you want to happen?} | {What would indicate success or validation?} | {What to measure to see these signals?} |
| | | |

---

## Open Questions / Tracked Assumptions

> This section inherits unanswered `important` and `tracked` items from the Living FAQ. Review and update this section as the Living FAQ evolves. Items resolved in the Living FAQ should be moved to a "Resolved" sub-table or removed.

### Open Questions

| ID | Question | Source (Living FAQ ref) | Status | Owner | Target Resolution Date |
|----|----------|------------------------|--------|-------|------------------------|
| OQ-1 | | {living-faq#section} | Open | | |
| OQ-2 | | | Open | | |

### Tracked Assumptions

> These are assumptions the team is proceeding with that have not yet been validated. If an assumption proves false, the impacted requirements and build sequence should be revisited.

| ID | Assumption | Risk if Wrong | Validation Plan | Status |
|----|------------|---------------|-----------------|--------|
| TA-1 | | | | Unvalidated |
| TA-2 | | | | Unvalidated |

---

## Future Work and Follow-up

> This section captures items that extend beyond the current build sequence, or emerged during development and are better addressed in a subsequent effort.

| Description | Priority | Impact if NOT completed | Timeframe |
|-------------|----------|------------------------|-----------|
| | | | |

---

## Appendix / Upstream Artifact Links

> Links to all upstream artifacts that informed or feed into this PRD. Keep these current so readers can trace decisions back to their source.

| Artifact | Link | Description |
|----------|------|-------------|
| Context Brief | {link} | Background context and strategic framing |
| Press Release(s) | {link} | Working-backwards press release(s) |
| One-Pager | {link} | Executive summary / pitch document |
| Living FAQ | {link} | Running list of questions, answers, and tracked assumptions |
| API Design | {link} | API specifications and design documents |
| Agent Scenarios | {link} | Agent and programmatic use case definitions |
| Expansion Proposals | {link} | Proposals for future expansion beyond current scope |
| Red Team Report | {link} | Adversarial review findings and mitigations |
| Business Case / SWAG | {link} | Financial and opportunity sizing estimates |

---

## Changelog

> **Pro-Tip:** Once PRD is actionable, color changelog entries and corresponding edits in doc to match so changes stand out.

| Date | Changes | By |
|------|---------|-----|
| {YYYY-MM-DD} | Initial draft created | |

---

## PRD Status Reference

| Status | Meaning |
|--------|---------|
| 🚧 Drafting | Known to be incomplete as it starts to come together. Do not rely on content at this point. |
| 🏃 Actionable | While it will continue to evolve with discovery through the process, Eng partners have agreed that there is enough to get going. |
| 🔒 Closed | The PRD represents what was finally delivered. Comments have been closed with outcomes incorporated in the document. |
| ❗ Abandoned | It shouldn't happen often, but when it does, flag a PRD this way so others will know the content may not represent a current state. |
