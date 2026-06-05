// ═══════════════════════════════════════════════════════════════════════
//  MOODS · swappable themes
// ───────────────────────────────────────────────────────────────────────
//  A "mood" is a complete palette living in themes/<id>.css under the
//  selector [data-theme="<id>"]. Switching a mood ONLY swaps design tokens —
//  every interaction (proximity warmth, modals, routing, auto-refresh) is
//  left completely untouched. The look changes; the UX doesn't.
//
//  ┌─ TO ADD A MOOD ───────────────────────────────────────────────────┐
//  │ 1. cp themes/_TEMPLATE.css themes/<id>.css  and fill in every token │
//  │ 2. add  <link rel="stylesheet" href="themes/<id>.css">  to          │
//  │    index.html <head> (next to the other theme links)                │
//  │ 3. add an entry to the MOODS array below                            │
//  └────────────────────────────────────────────────────────────────────┘
//  That's the whole job. See themes/README.md for the long version.
//
//  Mood entry shape:
//    {
//      id:     'organic',          // must match themes/<id>.css selector
//      label:  'Organic',          // shown in the menu + as the active name
//      blurb:  'Forest & wood…',   // one-line description under the name
//      fontHref: 'https://…'       // OPTIONAL Google-Fonts URL, lazy-loaded
//    }
// ═══════════════════════════════════════════════════════════════════════

const MOODS = [
  {
    id: 'organic',
    label: 'Organic',
    blurb: 'Forest & wood · restful dusk',
    // Spectral + Mulish are already linked in index.html <head> — no fontHref needed.
  },
  {
    id: 'modafinil',
    label: 'Modafinil',
    blurb: 'Vaporwave · digital sunset',
    fontHref: 'https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;500;600;700;800&display=swap',
  },
  {
    id: 'breathe',
    label: 'Breathe',
    blurb: 'Soft aurora · drifting pastels',
    fontHref: 'https://fonts.googleapis.com/css2?family=Nunito:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap',
  },
  {
    id: 'karesansui',
    label: 'Zen Garden',
    blurb: 'Karesansui · empty stillness',
    fontHref: 'https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@300;400;500;700&family=Zen+Old+Mincho:wght@400;500;600&display=swap',
  },
  {
    id: 'vantaca',
    label: 'Vantacan',
    blurb: 'Powered by HOAi',
    fontHref: 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap',
    favicon: '/assets/vantaca-v.png',   // swaps the browser-tab icon to the Vantaca "V"
  },
  // ── add more moods here ──
];

const MOOD_KEY = 'pmos-mood';
const DEFAULT_MOOD = 'organic';
// Fallback favicon for moods that don't declare one (the default PM-OS leaf mark).
const DEFAULT_FAVICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32'%3E%3Crect x='6' y='6' width='20' height='20' rx='3' ry='12' transform='rotate(-12 16 16)' fill='%237a9e6d'/%3E%3C/svg%3E";

function moodById(id) {
  return MOODS.find(m => m.id === id) || null;
}

function currentMood() {
  const id = localStorage.getItem(MOOD_KEY) || DEFAULT_MOOD;
  return moodById(id) ? id : DEFAULT_MOOD;
}

// Apply a mood: flip the [data-theme] attribute, persist it, lazy-load its
// webfont if it declares one, and sync the control's UI. This is the single
// entry point — call applyMood(id) from anywhere.
//
// Switching MELDS one palette into the next: the look-swap is wrapped in a
// View Transition, so the browser cross-fades a snapshot of the old palette
// into the new one — colours, gradients, type, the logo and shadows all
// dissolve together, uniformly, in one gentle ~0.42s pass (tuned in
// index.html's ::view-transition-* rules). It's only a cross-fade — nothing
// moves, so it stays calm and never feels busy. Browsers without the API, and
// anyone who prefers reduced motion, get the instant swap. Nothing else about
// the swap changes.
function applyMood(id, { persist = true } = {}) {
  const mood = moodById(id) || MOODS[0];

  // Lazy-load the mood's webfont up front so it's ready as the new look melds in.
  if (mood.fontHref && !document.getElementById(`mood-font-${mood.id}`)) {
    const link = document.createElement('link');
    link.id = `mood-font-${mood.id}`;
    link.rel = 'stylesheet';
    link.href = mood.fontHref;
    document.head.appendChild(link);
  }

  // The actual look-swap: flip [data-theme] + the browser-tab favicon.
  const swap = () => {
    document.documentElement.dataset.theme = mood.id;
    const fav = document.getElementById('app-favicon');
    if (fav) fav.href = mood.favicon || DEFAULT_FAVICON;
  };

  const changing = document.documentElement.dataset.theme !== mood.id;
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (changing && !reduce && document.startViewTransition) {
    const vt = document.startViewTransition(swap);   // gentle full-page cross-fade
    // If the user switches again mid-fade the transition is skipped — that's
    // fine and expected; swallow the resulting rejection so it stays silent.
    if (vt && vt.ready && vt.ready.catch) vt.ready.catch(() => {});
  } else {
    swap();                               // instant (initial load / no support / reduced-motion)
  }

  if (persist) {
    try { localStorage.setItem(MOOD_KEY, mood.id); } catch (e) { /* private mode */ }
  }
  syncMoodUI(mood.id);
}

function syncMoodUI(activeId) {
  document.querySelectorAll('.mood-option').forEach(o => {
    o.setAttribute('aria-checked', String(o.dataset.mood === activeId));
  });
}

const MOOD_CHEV = `<svg class="mood-chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>`;
const MOOD_CHECK = `<svg class="mood-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;

function buildMoodControl() {
  const root = document.getElementById('mood-control');
  if (!root) return;
  const active = currentMood();

  const options = MOODS.map(m => `
    <button class="mood-option" data-mood="${m.id}" role="menuitemradio" aria-checked="${m.id === active}">
      <span class="mood-option-text">
        <span class="mood-option-name">${m.label}</span>
        <span class="mood-option-blurb">${m.blurb || ''}</span>
      </span>
      ${MOOD_CHECK}
    </button>`).join('');

  root.innerHTML = `
    <button class="mood-btn" id="mood-btn" aria-haspopup="true" aria-expanded="false" title="Switch mood">
      <span class="mood-label">Mood</span>
      ${MOOD_CHEV}
    </button>
    <div class="mood-menu" id="mood-menu" role="menu" aria-label="Mood">
      <div class="mood-menu-head">Mood</div>
      ${options}
    </div>`;

  const btn = root.querySelector('#mood-btn');
  const menu = root.querySelector('#mood-menu');
  const close = () => { menu.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); };
  const open  = () => { menu.classList.add('open');    btn.setAttribute('aria-expanded', 'true');  };

  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    menu.classList.contains('open') ? close() : open();
  });
  root.querySelectorAll('.mood-option').forEach(o => {
    o.addEventListener('click', () => { applyMood(o.dataset.mood); close(); });
  });
  document.addEventListener('click', (e) => { if (!root.contains(e.target)) close(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });

  syncMoodUI(active);
}

// The <head> pre-paint script already set [data-theme]; this keeps font + UI
// state in sync (without re-persisting), then builds the control. The script
// tag sits after the static #mood-control markup, so the element exists.
applyMood(currentMood(), { persist: false });
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', buildMoodControl);
} else {
  buildMoodControl();
}
