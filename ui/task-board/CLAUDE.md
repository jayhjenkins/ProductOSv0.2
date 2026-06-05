# PM-OS Task Board UI — notes

This directory IS the task board front end: `index.html` + `js/*.js`. It's a
vanilla HTML/CSS/JS board served by `scripts/task_server.py` (route `/` →
`ui/task-board/index.html`, static `/js/*` and `/themes/*`) against the real
backend API at `/api/*`. Default dev URL: http://localhost:8742.

> Note: a standalone build of this UI ships with a `js/mock-api.js` that
> intercepts `fetch()` for `/api*` and `/open*` with seed data so the redesign
> runs without the server. That file is intentionally **not** part of this live
> UI — here the real `task_server.py` backend serves the data. Don't add it.

## Moods (swappable themes)

The board supports swappable color/type/shape themes called **Moods**, surfaced
via a "Mood" dropdown in the top bar (right of the date). The default and first
mood is **Organic** (the original forest/wood dusk palette).

When asked to add or edit themes, follow `themes/README.md`. In short: a mood is
a token-only stylesheet `themes/<id>.css` (scoped to `[data-theme="<id>"]`),
linked in `index.html`'s `<head>`, and registered in `js/themes.js`'s `MOODS`
array. Switching moods only swaps CSS tokens — never change interactions/UX when
adding a mood. Copy `themes/_TEMPLATE.css` to start.

- Primitives (surfaces, text, accents, q-/prio- hues, radii, ease, app-bg,
  paper) live in each `themes/<id>.css`.
- Derived tokens (`*-soft` tints, legacy `*-bg` aliases) are computed once in
  `index.html`'s `:root` from those primitives — a mood file never repeats them.
- Use absolute paths (`/themes/...`, `/js/...`) in `index.html` to match how the
  server serves static files.
