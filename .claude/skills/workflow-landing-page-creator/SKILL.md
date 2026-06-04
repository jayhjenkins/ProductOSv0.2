---
name: workflow-landing-page-creator
description: Use when generating an on-brand Unlayer landing-page JSON for a management-company and association pair — researches the prospect's public website, distills a brand system, decides which (if any) audience-fit structural shifts the page needs, and produces a paste-ready Unlayer JSON plus a brief notes file.
---

# Workflow: Landing Page Creator

## Purpose

- **Input:** management company name, association/community name, brand reference website URL.
- **Output:** a paste-ready Unlayer JSON (`unlayer.loadDesign(designObj)`-compatible) plus a short `notes.md` audit.
- **Method:** one focused WebFetch of the prospect's public site, distill brand presentation, gate audience-fit decisions behind explicit triggers, compose the page from `block-snippets.md` anchored on template 06's row inventory, validate in one shot, hand off.
- **Anchor:** every page exists to do two jobs for residents — **(1) log in to the portal** and **(2) find what they need quickly** (Pay / Documents / Calendar / Contact). Every other decision serves those two.

## When to Use

- The user invokes `/landing-page-creator`.
- The user wants a portal landing page for a specific prospect and gives you a public website URL.
- Sales / demo prep where Vantaca needs a branded landing-page preview.

Do **not** use this skill for:
- Generic gallery templates — those are hand-curated under `datasets/product/packages/2026/landing-page-wysiwyg/templates/01-05`.
- Anything requiring a CMS or dynamic content. These pages are static.
- Email design — use the email-template workflow.

## How decisions are organized — three layers

Three clearly separated layers. Read these before the workflow phases — they are the conceptual spine and they are unchanged from the previous overhaul.

### Layer 1 — Resident-jobs invariants (always true)

Non-negotiables for every generated page, regardless of brand or audience. Mechanical validation enforces most of these.

- **Login surface is unmistakable above the fold.** The first viewport contains: the community name, a primary CTA pointing at `{{portal_login_url}}`, and the visual cue (color, contrast, size) that makes the CTA the obvious next action. **No competing CTAs in the hero** — one button, one job.
- **The four "find what I need" destinations are reachable in one click from the page.** Pay (`{{pay_now_url}}`), Documents (`/documents`), Calendar (`{{calendar_url}}`), Contact (`mailto:{{manager_email}}`). They appear in a scannable group somewhere on the page. If a community legitimately doesn't offer one — most often Pay — the count can drop to three via Shift 3 (see Layer 3).
- **A contact moment is present.** Phone, email, or both.
- **Static evergreen content only.** No "Latest News" / "Upcoming Events" / "Recent Announcements" / `[ DATE ]` placeholders. Manager-editable bracketed instructions like `[ Replace with a friendly paragraph about your community... ]` are fine — they're setup notes, not dynamic content.
- **Seven allowed merge tags. Four banned ones.**
  - **Allowed:** `{{community_name}}`, `{{management_company_name}}`, `{{manager_phone}}`, `{{manager_email}}`, `{{portal_login_url}}`, `{{pay_now_url}}`, `{{calendar_url}}`
  - **Banned (zero instances ever):** `{{manager_name}}` → say "your management team"; `{{documents_url}}` → static `/documents`; `{{submit_request_url}}` → static `mailto:{{manager_email}}`; `{{current_year}}` → static year string
- **No external top bar elements in the JSON.** The portal shell renders hamburger / centered logo / login button above the canvas. The Unlayer canvas starts flush at the hero.
- **Schema discipline.** `schemaVersion: 12`. Every `counters.u_*` set to `99`. Every row's `cells` sums to `12` and `len(cells) == len(columns)`. `body.values.contentWidth: 1200` default (`1280` only when matching the Estate-Premium-style canvas, template 06).
- **Background-image overlay hack** when a photographic hero is chosen. `backgroundImage.fullWidth: false` so image and overlay occupy the same box. Row `backgroundColor` matches the overlay's dark base (`#0E1620`-ish) so the viewport-edge bleed reads continuous. Column `backgroundColor: rgba(R, G, B, 0.4–0.55)`. Add `text-shadow: 0 1px 4px rgba(0,0,0,0.5)` to hero eyebrow / H1 / subhead as a fallback. **If `fullWidth: true` is left in place, the image bleeds edge-to-edge but the column overlay only covers the center content box, leaving bright unshaded strips on the sides.** Most common visual mistake.

### Layer 2 — Brand presentation (the primary customization engine)

This is where most customer-to-customer differentiation lives. Two pages with the same row inventory but different palette, voice, and photography do not read as carbon copies — residents see *their* brand.

Distilled from the single Phase 1 WebFetch into the short `notes.md`:

- **Palette** — primary/accent, `<#PAGE_BG>` (white or tinted), `<#SURFACE>` (alternating section background), `<#HEADING>`, `<#BODY>`, `<#ACCENT_DARK>` (~15–20% darker than accent), `<#DARK_FALLBACK>` (if image hero).
- **Voice** — 2–4 verbatim phrases lifted from the brand's site. Used in hero subhead, promise paragraph, contact subheads.
- **Photography** — hero image and any supporting imagery. Squarespace: `images.squarespace-cdn.com/content/v1/{site-id}/{file-id}/{filename}` with `?format=2500w` (hero), `?format=1500w` (mid), `?format=500w` (icons). Wix: `static.wixstatic.com/media/...` as returned. WordPress / generic: as-is.
- **Typography family** — sans (Inter) by default. **Only** switch to serif headlines if the brand's own site uses one.
- **Brand facts the page reflects faithfully** — community name, management company name, location, business category, hours. These are inputs, not levers.

### Layer 3 — Audience-fit structural shifts (gated by triggers)

Five sanctioned shifts. They are **not evaluated on every run.** Default behavior is baseline 06's row inventory. Walk the shift table below only when an explicit trigger fires.

**Triggers (any one → evaluate the relevant shifts):**
- WebFetch surfaces explicit accessibility / senior signals — "55+", "retirement community", "active adult", "assisted living", "independent living", or similar → evaluate Shifts 1, 2, and 5.
- User flags at intake — "no online dues payment", "this is a senior community", "no hero photography available" → evaluate the relevant shift.
- WebFetch returns zero usable hero imagery → evaluate Shift 1.
- Brand has no quote-worthy positioning line in WebFetch → evaluate Shift 4.

If no triggers fire, `notes.md` records `Audience-fit: all defaults (no triggers)` and Phase 3 proceeds with the baseline 06 row inventory.

| # | Shift | Default (baseline 06) | Apply when |
|---|---|---|---|
| 1 | **Hero treatment** | Photo-backdrop hero with overlay (block-snippets §1) | Brand has no hero-quality photo, OR audience is accessibility-first, OR brand's own hero is photo-free — switch to solid-color hero (block-snippets §9). |
| 2 | **Action zone shape (4→stacked)** | 4-card grid (§8) | Audience is accessibility-first (senior community, screen-reader target) — switch to stacked full-width tall buttons (§10). |
| 3 | **Action zone shape (4→3)** | 4-card grid (§8) | Community doesn't offer one of the four jobs — most commonly no online payment — switch to 3-card grid (§11). |
| 4 | **About / promise block** | Half-image 6/6 promise band (`row-promise` in `06_estate-premium.json`) | Brand has no quote-worthy positioning, OR no second hero-quality image — switch to centered single-column about (§12). |
| 5 | **Contact section** | Two-column phone+email (`row-contact`) | Audience is accessibility-first — switch to single-column contact with 48px phone (§13). Phone becomes the dominant find-info pathway. |

**Coherence note:** if the trigger is accessibility-first, it typically fires Shifts 1, 2, and 5 together — they're driven by the same signal. That's expected, not over-shifting.

## Workflow

Four phases.

### Phase 1 — Inputs + research

1. Collect inputs via `AskUserQuestion` if any are missing: management company name, association/community name, brand reference website URL. If the user gave them inline, repeat back in one line and proceed.

2. **One WebFetch** against the homepage with this composed prompt structure (one request, one return):

   > Extract from this site: (a) brand name, tagline, location, business type; (b) full color palette with hex codes where visible — primary, accent, surface, heading, body; (c) typography — serif vs sans, weight pattern, any uppercase/letter-spacing treatment; (d) 3–5 verbatim copy phrases capturing tone; (e) **at least 5 image URLs** if the site has them — `<img>` src + srcset, OG meta image, background-image CSS, lazy-loaded data attributes. Label each as logo / icon / amenity / lifestyle / architectural / person / hero. **Specifically call out the 1–2 you'd nominate as hero candidates** and which are non-hero supporting visuals; (f) every nav link.

   **Images are what make these pages pop.** A page that ships with zero real images reads sparse. The skill should fight to find imagery before settling for placeholders. If the homepage genuinely has none, fire the fallback fetch in step 3.

3. **Conditional fallback fetch — image hunt only** (max one). Trigger when step 2 returned fewer than 2 usable image URLs AND neither Shift 1 nor Shift 4 will eliminate the need for imagery. Try `/about`, `/amenities`, `/gallery`, `/services` in that order with an image-only WebFetch prompt — no need to re-extract palette or voice; just enumerate every image URL with the same labels. Hard cap stays at two WebFetch calls total.

### Phase 2 — Decisions and notes

1. **Walk the audience-fit trigger gate.** Re-read the Layer 3 triggers. If any fire, evaluate the relevant shifts and commit. If none fire, record `all defaults`.

2. **Write `notes.md`** in the output folder. Tight, scannable, ~25 lines max. Shape:

   ```
   # Notes — {community_name} × {management_company_name}

   Generated: YYYY-MM-DD

   ## Palette
   - PAGE_BG  #XXXXXX
   - SURFACE  #XXXXXX
   - HEADING  #XXXXXX
   - BODY     #XXXXXX
   - ACCENT   #XXXXXX   (sourced from <brand site element>)
   - ACCENT_DARK #XXXXXX  (~18% darker for hover)
   - DARK_FALLBACK #XXXXXX  (only if image hero)

   ## Voice (verbatim from brand site)
   - "phrase 1"
   - "phrase 2"
   - "phrase 3"

   ## Image plan
   - Hero:        <use brand image | base64 placeholder | Shift 1 fires, no hero>
   - Promise:     <use brand image | base64 placeholder | Shift 4 fires, no promise>
   - Pillars:     <4 brand images | omit pillar row | 4 base64 placeholders>

   ## Image Sources
   | Slot | URL | Source page | Reason |
   |------|-----|-------------|--------|
   | Hero | https://… | homepage | Lifted directly from prospect homepage header |
   | Promise | https://… | /about | Closest "lifestyle" match on brand site |
   | Pillar 1 | (placeholder) | — | No suitable amenity image on brand site; needs AI-generated |

   ## Audience-fit
   - All defaults (no triggers)
       — OR —
   - Shift 1 (solid-color hero) — trigger: <reason>
   - Shift 5 (48px phone)       — trigger: <reason>
   ```

   This file is the audit trail. Nothing else. No verbose tables, no extended commentary.

   **Rule on `## Image Sources`:** every image URL that ends up in the JSON gets a row in this table, and every placeholder gets a row too (URL column reads `(placeholder)`, with the reason). Any URL pulled from a page **other than the supplied brand reference URL** is the audit signal — the user reads this table to validate that off-source images are appropriate before sending to a prospect.

### Phase 3 — Compose JSON

Same compose-from-blocks workflow as today, anchored on template 06's row inventory. Read `block-snippets.md` and assemble the page.

**Default row inventory** (baseline 06, when no triggers fired):

1. **Hero** — `block-snippets.md` §1 (image-with-overlay) — apply the overlay-hack rules from Layer 1
2. **Standard band** — thin centered brand-statement strip (template 06 `row-standard-band` shape — optional; drop if brand has no quote-worthy positioning)
3. **Actions intro** — eyebrow + heading + optional subhead
4. **Actions** — `block-snippets.md` §8 (4-card grid: Pay / Documents / Calendar / Contact)
5. **Promise band** — half-image 6/6 panel (see `row-promise` in `06_estate-premium.json` for the canonical shape)
6. **Pillars title + grid** — optional; include only when brand has 3–4 service or amenity icons worth showcasing
7. **Contact** — two-column phone + email (see `row-contact` in `06_estate-premium.json`)
8. **Footer** — community name + managed-by line + copyright

**Shift-alternative row swaps** (when a trigger fired in Phase 2):

| Triggered shift | Replace row | With block-snippets section |
|---|---|---|
| Shift 1 (solid-color hero) | Row 1 (hero) | §9 |
| Shift 2 (stacked actions) | Row 4 (4-card actions) | §10 × 4 rows (one Pay filled + three outlined) |
| Shift 3 (3-card actions)  | Row 4 (4-card actions) | §11 with three cards selected |
| Shift 4 (centered about)  | Row 5 (promise band) | §12 |
| Shift 5 (48px phone contact) | Row 7 (contact) | §13 |

Substitute color tokens (`<#PAGE_BG>`, `<#ACCENT>`, etc.) per `notes.md` palette, brand voice phrases where natural, and the chosen image URLs at the right CDN size. Use only the seven allowed merge tags; no top-bar elements; no dynamic-content language. Every `cells` array sums to 12 and matches its column count. `schemaVersion: 12`, all `counters.u_*` at 99.

Write the assembled JSON to `landing-page.json` in the output folder.

### Phase 4 — Validate and hand off

**Validate** — one combined Python invocation. All assertions in one script. Exit code 0 means everything passed.

```bash
python3 - <<'PY'
import json, sys
path = 'landing-page.json'
ok = True
try:
    d = json.load(open(path))
except Exception as e:
    print(f'FAIL: JSON parse: {e}'); sys.exit(1)
if d.get('schemaVersion') != 12:
    print(f'FAIL: schemaVersion is {d.get("schemaVersion")}, expected 12'); ok = False
if 'counters' not in d:
    print('FAIL: missing counters'); ok = False
for i, row in enumerate(d['body']['rows']):
    if sum(row['cells']) != 12:
        print(f'FAIL: row {i} cells dont sum to 12: {row["cells"]}'); ok = False
    if len(row['cells']) != len(row['columns']):
        print(f'FAIL: row {i} cells/columns mismatch'); ok = False
src = open(path).read()
for tag in ('manager_name','documents_url','submit_request_url','current_year'):
    n = src.count('{{' + tag + '}}')
    if n:
        print(f'FAIL: banned tag {{{{{tag}}}}} appears {n} time(s)'); ok = False
if ok:
    print(f'OK: schemaVersion=12, rows={len(d["body"]["rows"])}, all cells sum to 12, no banned tags')
    sys.exit(0)
sys.exit(1)
PY
```

If it exits non-zero, fix the JSON and re-run.

**Yellow-flag check — image coverage.** Count `"type": "image"` content blocks whose `src.url` is non-empty AND does **not** start with `data:image/svg+xml;base64,` (i.e., real imagery, not a SWAP-ME placeholder). If that count is zero AND `notes.md` does **not** record Shift 1 firing or an accessibility-first audience, prepend this warning to the top of `notes.md` and surface it in the hand-off summary:

> **Warning — zero real images shipped.** The page has no image content blocks pointing at real imagery. Acceptable for accessibility-first audiences or when no usable imagery exists on the prospect site, but on a typical demo it reads sparse. Either (a) re-run with a different brand reference URL that has imagery, (b) accept the placeholders and instruct the demo presenter to swap them in before showing, or (c) explicitly record the reason under `## Image plan` in `notes.md`.

Warning only — validation still exits 0 and the workflow proceeds.

**Resident-jobs sanity check** — final read before hand-off:
- The hero's first viewport (top ~700px) makes the login CTA unmistakable. One primary button, pointing at `{{portal_login_url}}`. No competing CTAs.
- Pay / Documents / Calendar / Contact are all reachable in one click — unless a shift legitimately dropped one with a recorded trigger.

**Hand off** — print to the user:

1. Output folder path: `datasets/product/landing-pages/{management-company-slug}/{association-slug}_{YYYY-MM-DD}/`
2. One-paragraph summary: 3–4 key palette hex codes, image count, row count, one-line list of audience-fit shifts applied (or "all defaults")
3. Paste-into-Unlayer instructions: open editor (`unlayer.init({ displayMode: 'web' })`), use `unlayer.loadDesign(designObj)` or the Import JSON dialog, paste the contents of `landing-page.json`
4. "Before you demo" checklist:
   - Each external image URL still loads
   - Hero text reads cleanly over the image (if photo hero)
   - No bright unshaded strips on hero sides (`fullWidth: false` worked)
   - No top-bar elements snuck in
   - Login CTA is the dominant first-viewport element
   - All four (or three) action destinations are scannable
   - If demo will live more than a few weeks, plan to re-host CDN images locally

## Reference files

**Required pre-reads:**
- `datasets/product/packages/2026/landing-page-wysiwyg/templates/unlayer-schema.md` — schema cheat sheet + Unlayer-specific hacks (overlay-with-fullWidth-false, rgba columns, text-shadow fallback). Non-negotiable.
- `datasets/product/packages/2026/landing-page-wysiwyg/templates/block-snippets.md` — composition raw material. §0 scaffold; §1–§8 baseline blocks; §9–§13 shift-alternative snippets; §14 color tokens; §15 when-in-doubt.

**Optional / on-demand:**
- `datasets/product/packages/2026/landing-page-wysiwyg/templates/06_estate-premium.json` — the canonical row-inventory anchor. Read when you need to see how the standard rows fit together end-to-end.
- `datasets/product/packages/2026/landing-page-wysiwyg/templates/README.md` — gallery summary (templates 01–06 are sales-gallery exemplars, not workflow inputs).
- `datasets/product/packages/2026/landing-page-wysiwyg/templates/01–05_*.json` — gallery-only. Read only if a specific reference is needed.
- `datasets/product/packages/2026/landing-page-wysiwyg/templates/image-prompts.md` — AI image generation prompts (slots 1A–6F) for filling placeholder image blocks before demo.
- `datasets/product/packages/2026/landing-page-wysiwyg/PRD_landing-page-wysiwyg.md` — source of truth for the merge tag list.

## Success criteria

1. Output folder exists with **two** files: `landing-page.json` and `notes.md`.
2. The combined Python validation script (Phase 4) exits 0.
3. `notes.md` is ≤30 lines and follows the shape in Phase 2: palette, voice, images, audience-fit decision (with triggers or "all defaults").
4. The JSON imports into Unlayer without errors and renders on-brand.
5. The Phase 4 resident-jobs check passes — login CTA dominates the first viewport; all relevant find-info destinations are scannable.
6. The hero (if image-backed) shows no bright unshaded strips on the sides.
7. Zero instances of the four banned merge tags.
8. `notes.md` includes an `## Image Sources` table with one row per image URL in the JSON, and one row per placeholder (marked `(placeholder)` with the reason).

## Related skills

- **Downstream:** `quality-link-verification` — once published to a real portal, verify every external URL still loads and every `mailto:` resolves.
- **Adjacent:** `workflow-launch-announcement` — when a real customer adopts a generated page, draft the internal announcement.

## Failure modes to watch for

- **Auth-walled site.** WebFetch fails on sites requiring login. Ask the user to paste the homepage HTML or describe the brand in their own words.
- **Image-free site.** Triggers Shift 1 (solid-color hero, §9). No second fetch needed.
- **Brand has no clear color palette.** Default to: `<#PAGE_BG>` white, `<#ACCENT>` navy `#1E3A5F`, `<#HEADING>` `#2C3E50`, `<#BODY>` `#5A6878`. Note explicitly in `notes.md` that the palette is a placeholder.
- **Audience-fit signals contradict each other** (e.g. accessibility-first audience but the brand site is editorial/magazine). Resolve in favor of accessibility — residents are the user, brand is the wrapper.
- **rgba overlay flattens to opaque** on an older Unlayer renderer. The text-shadow fallback covers this. If reported, swap the column `backgroundColor` from `rgba(...)` to a solid dark hex.
- **Tempted to add a sixth shift.** Don't. Five is the licensed surface.
- **Prospect site has imagery but WebFetch didn't extract URLs cleanly.** Symptom: the homepage clearly has photos in the browser, but step 2 returned zero URLs. Cause: lazy-loading, JS-rendered hero carousels, or background-image inline styles the fetch summarizer missed. Action: fire the fallback fetch (step 3) with the image-only prompt and try `/about`, `/amenities`, `/gallery`. If both fetches come back empty, ask the user for one direct image URL inline before falling back to placeholders.
