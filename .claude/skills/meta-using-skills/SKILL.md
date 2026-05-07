---
name: meta-using-skills
description: Use at session start and before every task - establishes mandatory skill discovery and usage protocols to ensure relevant expertise is always applied
---

# Using PM-OS Skills

**If a relevant PM-OS skill exists, you MUST invoke it via the Skill tool before responding.**

Skills are auto-discovered from `.claude/skills/<name>/SKILL.md` and appear in the available-skills system reminder. Match against the user's intent using each skill's `description` field. A 1% chance a skill applies is enough — invoke it and adapt if it turns out wrong.

## Decision Flow

```
User message received
  ↓
Might any PM-OS skill apply?  ──no──→  Respond directly
  ↓ yes (even 1%)
Invoke Skill tool with the matched skill
  ↓
Announce: "Using [skill-name] to [purpose]"
  ↓
Has a checklist?  ──yes──→  Create TodoWrite todo per item
  ↓ no                          ↓
Follow skill exactly  ←─────────┘
  ↓
Respond
```

## Red Flags (Stop and Invoke)

| Thought | Reality |
|---|---|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I remember this skill" | Skills evolve. Read the current version. |
| "The user gave specific instructions" | User specifies WHAT. Skills control HOW. |
| "I'll just check the file first" | Skills tell you HOW to investigate. Invoke first. |
| "This skill doesn't quite fit" | If 80% relevant, use it and adapt. |
| "I need more context first" | Skill check comes before clarifying questions. |

## Skill Priority

When multiple skills could apply:

1. **Process skills first** — `superpowers:brainstorming`, `superpowers:systematic-debugging`, `meta-*`. These determine HOW to approach the task.
2. **Workflow skills next** — `workflow-*`. End-to-end procedures.
3. **Quality gates and context skills** — `quality-*`, `context-*`. Often invoked from inside a workflow.

"Let's build X" → brainstorming first, then `workflow-prd-creation`. "Diagnose this metric drop" → `metric-root-cause-diagnosis`.

## Quality Gates Are Iron-Law

Skills like `quality-citation-compliance`, `quality-prd-validation`, `quality-content-style` enforce non-negotiable requirements. When a workflow invokes a quality gate, the gate must pass before proceeding. No "fix it later."

## TodoWrite Enforcement

If a skill contains a checklist ("validate these 5 conditions", "verify each step"), every item becomes a TodoWrite todo. Mental tracking = skipped steps every time.

Procedural numbered lists ("1. read file 2. parse 3. write") are instructions, not checklists — no TodoWrite needed.

## User Instructions vs. Process

User controls **WHAT** (goals, requirements, success criteria). Skills control **HOW** (methodology, process, quality standards). "Write a blog post about X" → user controls topic and audience; the content-pipeline skill controls citation compliance and verification.

## The Iron Law

When a relevant skill exists, you MUST load and execute it via the Skill tool. No exceptions, no shortcuts, no rationalizations. This is the foundation of the entire system.
