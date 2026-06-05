# Moods — swappable themes

A **mood** is a complete color/type/shape palette for PM-OS. Switching moods
only swaps CSS design tokens — every interaction (the proximity-hover warmth,
modals, routing, auto-refresh) is untouched. The look changes; the UX doesn't.

The control lives in the top bar, to the right of the date, labeled **Mood**.
The choice is saved to `localStorage` (`pmos-mood`) and restored on load.
Default is **Organic**.

## How it fits together

| Piece | Role |
|---|---|
| `themes/<id>.css` | One file per mood. Defines tokens under `[data-theme="<id>"]`. |
| `index.html` `<head>` | A `<link>` per mood + a pre-paint script that sets `[data-theme]` from `localStorage` (avoids a flash). |
| `index.html` `:root` | Holds **derived** tokens only (the `*-soft` tints, legacy `*-bg` aliases). Computed from a mood's primitives so you never repeat them. |
| `js/themes.js` | The registry (`MOODS`), the Mood dropdown, persistence, and lazy webfont loading. |

Every component in the app reads tokens (`var(--accent)`, `var(--bg)`, …).
A mood file just redefines those tokens — nothing else needs to change.

## Add a new mood (3 steps)

1. **Create the palette.** Copy the template and fill in *every* token:
   ```
   cp themes/_TEMPLATE.css themes/calm.css
   ```
   Replace each `<id>` with your mood id (`calm`), set all values.

2. **Link it.** Add one line to `index.html` `<head>`, next to the other theme links:
   ```html
   <link rel="stylesheet" href="themes/calm.css">
   ```

3. **Register it.** Add an entry to the `MOODS` array in `js/themes.js`:
   ```js
   {
     id: 'calm',
     label: 'Calm',
     blurb: 'Cool greys · low light',
     // fontHref: 'https://fonts.googleapis.com/css2?family=…' // optional
   }
   ```

That's it. The mood appears in the dropdown immediately.

## Token contract

A mood **must** define all of these (see `_TEMPLATE.css` for the annotated list):

- **Type:** `--font-sans`, `--font-serif`
- **Surfaces:** `--bg`, `--bg-deep`, `--surface`, `--surface-hover`, `--card-bg`, `--border`, `--border-soft`
- **Text:** `--text`, `--text-muted`, `--text-dim`
- **Accents:** `--accent`, `--accent-ink`, `--success`, `--warning`, `--danger`
- **Queue hues:** `--q-agent`, `--q-collab`, `--q-human`, `--q-waiting`
- **Priority dots:** `--prio-critical`, `--prio-high`, `--prio-medium`, `--prio-low`
- **Shape & motion:** `--r-card`, `--r-lane`, `--r-badge`, `--r-btn`, `--ease`
- **Background:** `--app-bg`, `--paper`, `--paper-opacity`

You do **not** define `--accent-soft`, `--success-soft`, `--warning-soft`,
`--danger-soft`, `--critical-bg`, `--high-bg`, `--medium-bg`, `--low-bg` —
those derive automatically in `index.html`'s `:root`.

## Conventions / tips

- `--accent-ink` is the text/icon color that sits **on** an accent fill (e.g.
  button labels). Pick something readable against `--accent`.
- Going light? Just invert the surface/text tokens — nothing else cares.
- Going retro/sharp? Drop the `--r-*` radii toward `0`.
- Custom font? Add `fontHref` to the registry entry (lazy-loaded on first
  switch), then point `--font-sans`/`--font-serif` at it in the css file.
- Set `--paper: none; --paper-opacity: 0;` to remove the grain overlay.
- Use the same lightness/chroma across your accent hues for harmony; vary hue.
