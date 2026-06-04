// ─── Activity Surface (read-only) ──────────────────────────────────────
// Reverse-chron list of archived (done/cancelled) tasks from /api/activity.
// READ-ONLY: rows never call openTask or any write verb. Each row links to
// its output when available (agent_output → Obsidian, else sharepoint_url →
// Word Online). Client-side substring filter over id+title+domain+queue;
// the fetched data is cached so filtering never refetches.

let _activityData = [];

async function renderActivity() {
  const view = document.getElementById('activity-view');
  if (!view) return;

  view.innerHTML = `<div class="loading">Loading activity…</div>`;

  try {
    const res = await fetch(`${API}/activity?limit=1000`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    _activityData = await res.json();
  } catch (err) {
    view.innerHTML = `<div class="loading">Error loading activity: ${escapeHtml(err.message)}</div>`;
    toast(`Activity failed to load: ${err.message}`);
    return;
  }

  view.innerHTML = `
    <div class="activity-filter-bar">
      <input type="text" id="activity-filter" class="activity-filter-input"
             placeholder="Filter by id, title, domain, queue…"
             oninput="_renderActivityRows(this.value)">
    </div>
    <div class="activity-table">
      <div class="activity-head">
        <span>Date</span>
        <span>ID</span>
        <span>Title</span>
        <span>Type</span>
        <span>Domain</span>
        <span>Output</span>
      </div>
      <div class="activity-rows" id="activity-rows"></div>
    </div>
  `;

  _renderActivityRows('');
}

function _renderActivityRows(filterStr) {
  const rowsEl = document.getElementById('activity-rows');
  if (!rowsEl) return;

  const needle = (filterStr || '').trim().toLowerCase();
  const rows = needle
    ? _activityData.filter(t => {
        const hay = `${t.id || ''} ${t.title || ''} ${t.domain || ''} ${t.queue || ''}`.toLowerCase();
        return hay.includes(needle);
      })
    : _activityData;

  if (rows.length === 0) {
    rowsEl.innerHTML = `<div class="now-empty">No activity matches that filter.</div>`;
    return;
  }

  rowsEl.innerHTML = rows.map(_renderActivityRow).join('');
}

function _renderActivityRow(t) {
  const queue = t.queue || '';
  const typeClass = ['human', 'agent', 'collab', 'waiting'].includes(queue) ? `atype-${queue}` : '';
  const typeCell = queue
    ? `<span class="activity-type ${typeClass}">${escapeHtml(queue)}</span>`
    : `<span class="activity-type activity-empty-cell">—</span>`;
  const domainCell = t.domain
    ? `<span class="activity-domain">${escapeHtml(t.domain)}</span>`
    : `<span class="activity-domain activity-empty-cell">—</span>`;

  let link;
  if (t.agent_output) {
    link = `<a class="activity-link" href="${obsidianUri(t.agent_output)}" title="Open in Obsidian">Open output</a>`;
  } else if (t.sharepoint_url) {
    link = `<a class="activity-link" href="${escapeHtml(t.sharepoint_url)}" target="_blank" rel="noopener" title="Open in Word Online">Open output</a>`;
  } else {
    link = `<span class="activity-link activity-empty-cell">—</span>`;
  }

  return `
    <div class="activity-row card">
      <span class="activity-date">${escapeHtml(formatDate(t.updated))}</span>
      <span class="activity-id">${escapeHtml(t.id || '')}</span>
      <span class="activity-title">${escapeHtml(t.title || '')}</span>
      ${typeCell}
      ${domainCell}
      ${link}
    </div>
  `;
}
