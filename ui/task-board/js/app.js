// ─── Tab Navigation ─────────────────────────────────────────────────

function switchTab(tabName) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.topbar-tab').forEach(el => el.classList.remove('active'));
  document.getElementById(`tab-${tabName}`).classList.add('active');
  document.querySelector(`.topbar-tab[data-tab="${tabName}"]`).classList.add('active');
  if (tabName === 'prompts') fetchPrompts();
  if (tabName === 'cron') fetchCronJobs();
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
