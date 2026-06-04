// ─── Tab Navigation ─────────────────────────────────────────────────

function switchTab(tabName) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.topbar-tab').forEach(el => el.classList.remove('active'));
  document.getElementById(`tab-${tabName}`).classList.add('active');
  document.querySelector(`.topbar-tab[data-tab="${tabName}"]`).classList.add('active');
  if (tabName === 'activity') renderActivity();
  if (tabName === 'quality') renderQuality();
  if (tabName === 'engine') fetchPrompts();
  if (tabName === 'schedules') fetchCronJobs();
}

// Close modal on overlay click
document.getElementById('modal-overlay').addEventListener('click', (e) => {
  if (e.target === e.currentTarget) closeModal();
});

// Close modal on Escape
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeModal();
});

// ─── Open file links (Word docs via /open endpoint) ─────────────────

document.addEventListener('click', (e) => {
  const link = e.target.closest('a[href^="/open"]');
  if (link) {
    e.preventDefault();
    fetch(link.href);
  }
});

// ─── Init ───────────────────────────────────────────────────────────

fetchTasks();
checkLangfuseHealth();
// Auto-refresh every 15 seconds
setInterval(fetchTasks, 15000);
// Check LangFuse health every 60 seconds
setInterval(checkLangfuseHealth, 60000);

// ─── Proximity highlight ─────────────────────────────────────────────
// Cards warm up based on how close the cursor is (smooth distance falloff),
// instead of a binary hover. Feels gentler and more organic.
(function () {
  const RADIUS = 90;           // px: tighter, so only the card under the cursor warms
  let mx = -99999, my = -99999, raf = null;

  function update() {
    raf = null;
    const cards = document.querySelectorAll('.card');
    for (const c of cards) {
      const r = c.getBoundingClientRect();
      if (r.bottom < -60 || r.top > window.innerHeight + 60) {
        if (c.style.getPropertyValue('--prox') !== '0') c.style.setProperty('--prox', '0');
        continue;
      }
      const dx = Math.max(r.left - mx, 0, mx - r.right);
      const dy = Math.max(r.top - my, 0, my - r.bottom);
      const d = Math.hypot(dx, dy);
      let t = 1 - d / RADIUS;
      if (t < 0) t = 0;
      const p = t * t * t; // cubic falloff — gentle, concentrated on the nearest card
      c.style.setProperty('--prox', p.toFixed(3));
    }
  }
  function schedule() { if (!raf) raf = requestAnimationFrame(update); }

  document.addEventListener('mousemove', (e) => { mx = e.clientX; my = e.clientY; schedule(); }, { passive: true });
  document.addEventListener('scroll', schedule, { capture: true, passive: true });
  window.addEventListener('resize', schedule);
  document.addEventListener('mouseleave', () => { mx = my = -99999; schedule(); });
})();
