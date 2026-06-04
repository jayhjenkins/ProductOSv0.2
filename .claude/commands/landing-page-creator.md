# /landing-page-creator

## MANDATORY: Use the workflow-landing-page-creator Skill

**You MUST use the `workflow-landing-page-creator` skill located at `.claude/skills/workflow-landing-page-creator/SKILL.md`**

## Before Starting

1. **Announce**: "I'm using workflow-landing-page-creator to generate an on-brand Unlayer landing-page JSON"
2. **Read the skill**: Load `.claude/skills/workflow-landing-page-creator/SKILL.md`
3. **Read the references**: The skill points at `unlayer-schema.md` and `block-snippets.md` in the templates folder — read both before generating JSON
4. **Follow exactly**: Execute the skill as written, all seven phases in order

## Purpose

Generate a paste-ready Unlayer landing-page JSON for a management-company / association pair. The skill researches the prospect's public website, distills a brand system (palette, voice, persona), selects one of the six layout archetypes, and produces:

- `landing-page.json` — the design ready for `unlayer.loadDesign(designObj)`
- `brand-brief.md` — extracted palette, voice, persona, image inventory
- `source-research.md` — raw WebFetch findings for traceability

## Guiding Principles

Encoded in detail inside the skill. Highlights:

- **Background-image overlay hack** — `fullWidth: false` on the row's `backgroundImage` so the image and overlay share the same box. Don't skip this — it's the most common visual bug.
- **Seven-tag merge contract** — only `community_name`, `management_company_name`, `manager_phone`, `manager_email`, `portal_login_url`, `pay_now_url`, `calendar_url`. Anything else is a static URL or static text.
- **External top bar** — never include hamburger, centered logo, or login button in the JSON. The portal shell renders those above the canvas.
- **Static evergreen pages only** — no "Latest News," no `[ DATE ]` placeholders. Static copy + manager-editable bracketed instructions.
- **Persona-aware** — the Sunset Simple pattern exists because residents (including 85-year-old grandmothers) don't want to click a menu to find documents. Match the layout to the audience.

## Inputs

The skill will ask via `AskUserQuestion` if you don't supply them inline:
- Management company name
- Association / community name
- Brand reference website URL (the prospect's public site)

## Output Location

```
datasets/product/landing-pages/{management-company-slug}/{association-slug}_{YYYY-MM-DD}/
```

## Validation

The skill runs three mechanical checks before handing off:
1. Strict JSON parse via `python3 -m json.tool`
2. Schema sanity (`schemaVersion: 12`, every row's `cells` sums to 12, `cells` length matches `columns` length)
3. Tag audit (zero instances of the four disallowed merge tags)

If any fail, fix and re-run before completing.
