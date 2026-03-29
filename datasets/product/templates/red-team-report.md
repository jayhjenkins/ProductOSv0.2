# Red Team Report: {PRODUCT_NAME}

**PRD Reference:** `{path to PRD}`
**Review Date:** {YYYY-MM-DD}
**Reviewer:** Red Team Reviewer Agent

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| Critical | {N} |
| Major | {N} |
| Minor | {N} |
| Questions | {N} |
| **Total** | **{N}** |

## Executive Summary

{One paragraph summarizing the overall health of the PRD, key risk areas, and the most important findings. This should give the PM a 30-second read on whether there are show-stoppers.}

---

## Critical Findings

*Product breaks, data loss, or security vulnerabilities. Must be fixed before proceeding.*

| ID | PRD Section | Finding | Recommended Fix | Status |
|----|-------------|---------|-----------------|--------|
| C-1 | {Section ref} | {What's wrong} | {How to fix — NOT "cut this feature"} | Open |
| C-2 | | | | Open |

---

## Major Findings

*User experience degrades significantly. Track and fix before launch.*

| ID | PRD Section | Finding | Recommended Fix | Status |
|----|-------------|---------|-----------------|--------|
| M-1 | {Section ref} | {What's wrong} | {How to fix} | Open |
| M-2 | | | | Open |

---

## Minor Findings

*Polish issues, not directly user-facing.*

| ID | PRD Section | Finding | Recommended Fix | Status |
|----|-------------|---------|-----------------|--------|
| m-1 | {Section ref} | {What's wrong} | {How to fix} | Open |
| m-2 | | | | Open |

---

## Questions / Clarifications

*Needs PM clarification — not clearly a bug.*

| ID | PRD Section | Question | Context |
|----|-------------|----------|---------|
| Q-1 | {Section ref} | {What needs clarification} | {Why this matters} |
| Q-2 | | | |

---

## Slow Walk Results

### Scenario: {Scenario Name}

| Step | What Can Go Wrong | Finding | Severity |
|------|-------------------|---------|----------|
| {Step 1} | {Failure mode} | {Finding ID or "OK"} | {C/M/m/Q} |
| {Step 2} | | | |

### Scenario: {Scenario Name}

{Same structure}

---

## Architecture Stress Test

| Dimension | Current Design | At 10x | At 100x | At 1000x | Finding |
|-----------|---------------|--------|---------|----------|---------|
| {Throughput} | {Current approach} | {Impact} | {Impact} | {Impact} | {Finding ID or "OK"} |
| {Storage} | | | | | |
| {Dependencies} | | | | | |

---

## Agentic API Review

| Check | Result | Finding |
|-------|--------|---------|
| Agent can complete all scenarios via API? | {Yes/No} | {Finding ID or "OK"} |
| Error responses actionable for agents? | {Yes/No} | |
| UI-only capabilities exist? | {Yes/No — list any} | |
| Agent scenarios realistic and complete? | {Yes/No} | |
| Endpoints match PRD capabilities? | {Yes/No} | |

---

## Persona-Lens Results

*Included when `--personas` flag is used.*

### Persona: {Name — e.g., "First-time admin with limited technical background"}

| PRD Section | Experience Assessment | Friction Points |
|-------------|---------------------|-----------------|
| {Section} | {How this persona experiences this part} | {Where they'd struggle and why} |

### Persona: {Name}

{Same structure}

### Cross-Persona Conflicts

| Scenario | Persona A Needs | Persona B Needs | Conflict | Finding |
|----------|----------------|-----------------|----------|---------|
| {Scenario} | {What A needs} | {What B needs} | {How they conflict} | {Finding ID} |

---

## Consistency Audit

| Check | Result | Finding |
|-------|--------|---------|
| User scenarios match capability specs? | {Yes/No} | {Finding ID or "OK"} |
| Success metrics align with stated goals? | {Yes/No} | |
| Non-goals conflict with proposed features? | {Yes/No} | |
| API design supports all user flows? | {Yes/No} | |
| Press releases match PRD commitments? | {Yes/No} | |
| Living FAQ answers consistent with PRD? | {Yes/No} | |

---

## Resolution Tracker

| Finding ID | Resolution | Date | By |
|------------|-----------|------|----|
| {ID} | {What was done to fix it} | {YYYY-MM-DD} | |

---

## Changelog

| Date | Changes | By |
|------|---------|-----|
| {YYYY-MM-DD} | Initial red team review | |
