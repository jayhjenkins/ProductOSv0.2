---
name: workflow-vision-clarifier
description: Use when articulating product vision - produces dual press releases (external customer-facing, internal team-facing with persona sections) and a one-pager through structured PM interrogation
---

# Vision Clarifier

## Purpose

Articulate the product vision through structured interrogation and dual press releases:
- External press release for customers, press, and market
- Internal press release for team personas who need to operationalize
- One-pager summary for 10-minute pitch
- Force clarity before any code is written

## Governing Principle

> Start with the customer and work outward. Write the press release before writing any code. If you cannot articulate the product's value in simple, jargon-free language, the idea is not clear enough to build.

## When to Use

Activate when:
- User invokes `/project:press-release`
- Phase 2 of `/project:prep` or `/project:ship-it`
- PM needs to crystallize product vision before PRD

## Product Package Folder

All Shipping Greatness artifacts for a given initiative live in a single package folder:

```
datasets/product/packages/{YYYY}/{slug}/
```

The slug is derived from the product/feature name (lowercase, hyphens, no special chars). If the package folder doesn't exist yet, **create it** when producing the first artifact. All subsequent skills read from and write to this same folder.

## Inputs Required

- **Context Brief** (`{package}/context-brief.md`) — from Phase 1 discovery
- **PM's rough vision** — problem statement, feature idea, or outcome description
- Minimum: A clearly stated customer problem. If the Context Brief doesn't have one, loop back.

## Outputs Produced

- `{package}/press-release-external.md` — Customer-facing press release
- `{package}/press-release-internal.md` — Team-facing press release with persona sections
- `{package}/one-pager.md` — Condensed 10-minute pitch summary

## Workflow

### Task 1: Interrogation Loop

Ask the PM a structured sequence of questions. **Do not proceed until answers are sufficient.** If answers are vague, loop back with specific follow-ups.

1. **Who is the specific target customer?** Not "everyone." A named segment with characteristics.
2. **What is the exact problem they face today?** Specific, concrete, observable.
3. **How do they solve it now, and why does that suck?** Current workaround and its pain.
4. **What is the proposed solution, described as a USER OUTCOME?** Not a feature list — what does the user experience after this exists?
5. **What is the durable differentiation?** Why will this be better than alternatives long-term, not just at launch?
6. **What is the emotional hook?** Why would a customer CARE? What's the gut reaction?
7. **What is the explicit value to the management company (our buyer)?** What do they gain — operational efficiency, staff time saved, retention/expansion, the client/board/homeowner satisfaction they are accountable for, or a competitive edge? If the primary user is a resident or board member, push for the management-company benefit explicitly — don't let it stay implied.

**Cross-reference with Context Brief**: If the Context Brief has customer evidence, use it to pre-populate or challenge answers. Don't re-ask questions already answered upstream.

### Task 2: Draft External Press Release

Write a market-facing press release using template `datasets/product/templates/press-release-external.md`:

- **Headline**: Captures the outcome, not the feature
- **Subheadline**: One sentence expanding on the headline
- **Problem paragraph**: The customer's pain, in THEIR language (not engineering jargon)
- **Solution paragraph**: The product described as an experience
- **Value to the Management Company**: An explicit statement of what the management company (our buyer) gains. Make it explicit even when the primary user is a resident or board member.
- **Key benefits**: 3–4 outcome-oriented benefits
- **Simulated customer quote**: From a target persona (clearly labeled as simulated)
- **Call to action**

**Language requirement**: A customer with zero product knowledge must understand this. No jargon.

### Task 3: Draft Internal Press Release

Write a team-facing press release using template `datasets/product/templates/press-release-internal.md`:

**Shared Context (top of document):**
- Feature name and one-line description
- Strategic rationale (why now, why this)
- Durable differentiation statement
- Success criteria (how we'll know this worked)
- Timeline and key milestones
- Simulated executive sponsor quote

**Value to the Management Company Section (top of document, after Shared Context):**
- Explicit statement of what the management company (our buyer) gains — the value every internal team below must be able to articulate.
- Cover the business outcomes they care about: operational efficiency, staff time saved, retention/expansion, client/board/homeowner satisfaction they are accountable for, competitive edge when winning new associations.
- If the primary user is a resident or board member, make the management-company benefit explicit, not implied.

**Sales & Sales Demos Section:**
- What is the new capability and how does it change the demo flow?
- What new pain points can sales now address?
- Key talking points and objection handlers
- New competitive differentiators to highlight in deals

**Product Marketing Section:**
- Positioning and messaging framework for this feature
- How does this fit into the existing product narrative?
- Collateral needs (website, datasheets, case studies)
- Launch tier and go-to-market motion

**Professional Services & Implementation Section:**
- How does this affect implementation workflows?
- New configuration options, setup steps, or migration paths
- Guide/runbook/training material updates needed
- Onboarding experience for new customers who get this from day one

**Existing Customer Base (CSM/Support) Section:**
- How does this affect current customer experience?
- Migration path or additive?
- What do CSMs need to proactively communicate?
- Expected new support tickets and handling approach
- Help doc / KB / training material updates needed

### Task 4: Generate One-Pager

Produce a single-page summary using template `datasets/product/templates/one-pager.md`:

- Product name and tagline
- Target audience
- Problem statement (2 sentences max)
- Solution statement (2 sentences max)
- Value to the management company (1-2 sentences, explicit — our buyer's gain)
- Key differentiators (3 bullets max)
- Success metrics (2–3 measurable outcomes)
- Timeline and key milestones

**Test**: If the one-pager can't be condensed from the press release content, the vision isn't clear enough. Loop back to the interrogation.

## Arguments

- `--external` — Generate external press release only
- `--internal` — Generate internal press release only
- `--both` — Generate both press releases and one-pager (default)
- `--refine` — Iterate on existing drafts with new PM input

## Quality Criteria

- [ ] External PR readable by a customer with zero product knowledge
- [ ] Internal PR has actionable content for EACH persona section (Sales, PMM, PS, CSM)
- [ ] Value to the Management Company is explicitly stated in all three artifacts (external PR, internal PR, one-pager) — not implied
- [ ] One-pager could support a 10-minute pitch
- [ ] No engineering jargon in either press release
- [ ] Durable differentiation is clearly stated and defensible
- [ ] All content traceable to Context Brief evidence or PM input
- [ ] Simulated quotes clearly labeled as simulated

## Failure Modes

| Failure | Detection | Fix |
|---------|-----------|-----|
| Vague customer ("everyone", "users") | No named segment with characteristics | Loop interrogation Q1 |
| Feature-list solution | Solution describes what's built, not what user experiences | Rewrite as user outcome |
| Internal PR reads like release notes | No actionable guidance per persona | Rewrite each section with "what do you DO with this info" |
| Missing persona sections | Any of Sales/PMM/PS/CSM sections empty | Fill or mark TBD with rationale |
| One-pager too long | More than one printable page | Condense — if you can't, vision isn't clear |

## Interaction Model

- **Interrogation loop**: Agent asks, PM answers. Agent pushes back on vague answers.
- **Draft review**: Agent produces drafts, PM reviews. Agent incorporates feedback.
- **Judgment calls deferred to PM**: Product positioning, competitive framing, timeline
- **Agent decides**: Document structure, language quality, section completeness

## Related Skills

- `meeting-synthesis`: May provide input context
- `research-gathering`: May provide competitive/market context
- `devils-advocate`: Next phase — uses press releases as input
- `prd-creation`: Later phase — uses vision artifacts as input
