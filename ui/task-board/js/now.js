// ─── Now Surface ───────────────────────────────────────────────────────
// Vertical priority STACK (not a 4-col grid). Buckets active tasks by
// demand-on-the-user via deriveAttentionState(task).lane:
//   Review · Decide · People · Agent queue (collapsed)
// Reuses renderCard(task, queue) from board.js so the modal verb matrix
// survives unchanged. fetchTasks() (board.js) calls this on every refresh.

const PRIORITY_RANK = { critical: 0, high: 1, medium: 2, low: 3 };

function sortByPriority(tasks) {
  return tasks.slice().sort((a, b) => {
    const ra = PRIORITY_RANK[a.priority] ?? 99;
    const rb = PRIORITY_RANK[b.priority] ?? 99;
    return ra - rb;
  });
}

function renderNowSection(title, tasks, emptyText) {
  let html = `<section class="now-section">`;
  html += `<div class="now-section-header"><span>${title}</span></div>`;
  html += `<div class="now-section-body">`;
  if (tasks.length === 0) {
    html += `<div class="now-empty">${emptyText}</div>`;
  } else {
    sortByPriority(tasks).forEach(t => { html += renderCard(t, t.queue); });
  }
  html += `</div></section>`;
  return html;
}

function renderNow() {
  const view = document.getElementById('now-view');
  if (!view) return;

  const lanes = { review: [], decide: [], people: [], 'agent-queue': [] };
  allTasks
    .filter(t => t.status !== 'cancelled')
    .forEach(t => {
      const { lane } = deriveAttentionState(t);
      if (lanes[lane]) lanes[lane].push(t);
    });

  let html = '';
  html += renderNowSection(
    `Decide`, lanes.decide,
    'Nothing waiting on your approval.');
  html += renderNowSection(
    `Review`, lanes.review,
    'Nothing to review.');
  html += renderNowSection(
    `People`, lanes.people,
    'Inbox zero.');

  // Agent queue — collapsed by default, running cards show their mark via renderCard
  const aq = lanes['agent-queue'];
  html += `<details class="now-section now-agent-queue">`;
  html += `<summary class="now-section-header"><span>Agent queue</span></summary>`;
  html += `<div class="now-section-body">`;
  if (aq.length === 0) {
    html += `<div class="now-empty">Agent queue is empty.</div>`;
  } else {
    sortByPriority(aq).forEach(t => { html += renderCard(t, t.queue); });
  }
  html += `</div></details>`;

  view.innerHTML = html;
}
