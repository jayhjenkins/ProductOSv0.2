# /project:update-faq

## Add or Update an Entry in the Living FAQ

Add a new question, answer, or edit in the Living FAQ document. The Living FAQ is audience-first (internal business users + customers). It is NOT the place for engineering, architecture, or security-implementation questions.

## What to Do

1. **Locate the Living FAQ** in the initiative's package folder at `datasets/product/packages/{YYYY}/{slug}/living-faq.md`
   - List available package folders if the initiative is ambiguous
   - If no package folder or FAQ exists, inform the user and suggest running `/project:prep` first
2. **Ask the user** what they want to add or update:
   - New question? → Ask for: question text, audience tag, draft answer (≤50 words)
   - Answer to an existing question? → Ask which question ID, then the answer
   - Update existing entry? → Ask which entry and what to change
   - New PM-only open item? → Add to the "Open Questions for PM" section
3. **Respect the hard caps** — ≤20 total questions, ≤50 words per answer, ≤2,000 words total. If adding the new question would exceed a cap, ask the user which existing question to retire.
4. **Write the update** to the Living FAQ in the correct audience section
5. **Add a changelog entry** with the date and change description

## Audience Tags

Every question in the main FAQ sections is tagged with its audience:

| Tag | Audience | Section |
|-----|----------|---------|
| `internal-csm` | CSM / Account Management | For Internal Teams |
| `internal-ps` | Professional Services / Implementation | For Internal Teams |
| `internal-support` | Support | For Internal Teams |
| `customer-new` | End Customer — New User | For Customers |
| `customer-existing` | End Customer — Existing User | For Customers |

The "Open Questions for PM" section holds items the PM still needs to answer before the PRD can be finalized or engineering can start. Items here do not need an audience tag.

## Scope Rules

**Do NOT add to the Living FAQ:**
- Engineering implementation questions (architecture, scaling, data model, tech stack choice)
- Security-implementation questions (XSS, CSRF, tenant isolation, auth mechanics)
- Compliance-implementation questions (GDPR/SOC2/HIPAA technical controls)
- Performance or capacity-planning questions
- Abuse/misuse scenarios (those go in `red-team-report.md` under Harm Scenarios)

If you catch one of these, redirect it to the appropriate artifact or drop it. The FAQ is for non-engineers.

## Rules

- The PM owns the Living FAQ after its initial generation — other agents do not write to it
- The `red-team-reviewer` skill does NOT append to this file
- Keep each answer ≤50 words — if you need more, the question is probably too broad
