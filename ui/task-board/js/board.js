// ─── Fetch & Render ─────────────────────────────────────────────────

async function fetchTasks() {
  try {
    const res = await fetch(`${API}/tasks`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    allTasks = await res.json();
    renderBoard();
    renderStats();
  } catch (err) {
    document.getElementById('board').innerHTML =
      `<div class="loading">Error loading tasks: ${err.message}</div>`;
  }
}

function renderStats() {
  const stats = document.getElementById('stats');
  const byQueue = {};
  let needsAttention = 0;

  allTasks.forEach(t => {
    byQueue[t.queue] = (byQueue[t.queue] || 0) + 1;
    if (t.agent_status === 'needs-human' || t.agent_status === 'complete') {
      needsAttention++;
    }
  });

  let html = '';
  const queueLabels = { human: 'human', collab: 'supervised', agent: 'agent', waiting: 'waiting' };
  for (const q of ['human', 'collab', 'agent', 'waiting']) {
    html += `<span class="stat-badge">${queueLabels[q]}: ${byQueue[q] || 0}</span>`;
  }
  if (needsAttention > 0) {
    html += `<span class="stat-badge attention">${needsAttention} need attention</span>`;
  }
  html += `<span class="stat-badge">total: ${allTasks.length}</span>`;
  stats.innerHTML = html;
}

function renderBoard() {
  const board = document.getElementById('board');
  const lanes = {
    human: { label: 'Human', icon: '', tasks: [] },
    collab: { label: 'Supervised', icon: '', tasks: [] },
    agent: { label: 'Agent', icon: '', tasks: [] },
    waiting: { label: 'Waiting', icon: '', tasks: [] },
  };

  allTasks.forEach(t => {
    if (lanes[t.queue]) lanes[t.queue].tasks.push(t);
  });

  let html = '';
  for (const [queueName, lane] of Object.entries(lanes)) {
    html += `<div class="lane">`;
    html += `<div class="lane-header">`;
    html += `<span>${lane.icon} ${lane.label}</span>`;
    html += `<span class="count">${lane.tasks.length}</span>`;
    html += `</div>`;
    html += `<div class="lane-body">`;

    if (lane.tasks.length === 0) {
      html += `<div class="empty-lane">No tasks</div>`;
    } else {
      // Group by status — include 'done' for agent and collab lanes (awaiting review/action)
      const statusOrder = (queueName === 'agent' || queueName === 'collab')
        ? ['done', 'in-progress', 'open', 'blocked']
        : ['open', 'in-progress', 'blocked'];
      const grouped = {};
      lane.tasks.forEach(t => {
        const s = t.status || 'open';
        if (!grouped[s]) grouped[s] = [];
        grouped[s].push(t);
      });

      for (const status of statusOrder) {
        if (!grouped[status] || grouped[status].length === 0) continue;
        html += `<div class="status-group">`;
        let label = status;
        if (status === 'done' && queueName === 'agent') label = 'Ready for Review';
        if (status === 'done' && queueName === 'collab') label = 'Needs Your Action';
        html += `<div class="status-label">${label}</div>`;
        grouped[status].forEach(t => {
          html += renderCard(t, queueName);
        });
        html += `</div>`;
      }
    }

    html += `</div></div>`;
  }
  board.innerHTML = html;
}

function renderCard(task, queueName) {
  const priClass = `badge-${task.priority}`;
  let icons = '';

  // Agent status icons
  if (task.agent_status === 'running') icons += '<span class="agent-icon" title="Agent running">&#129302;</span>';
  else if (task.agent_status === 'needs-human') icons += '<span class="agent-icon" title="Needs human input">&#10067;</span>';
  else if (task.agent_status === 'complete') icons += '<span class="agent-icon" title="Agent complete">&#9989;</span>';
  else if (task.agent_status === 'failed') icons += '<span class="agent-icon" title="Agent failed">&#10060;</span>';

  // Schedule-meeting indicator
  if (task.task_type === 'schedule-meeting') icons += '<span class="agent-icon" title="Schedule meeting" style="font-size:12px;">&#128197;</span>';
  // Jira draft indicator
  if (task.body && task.body.includes('<!-- JIRA_DRAFT -->')) icons += '<span class="agent-icon" title="Jira draft ready" style="font-size:12px;">&#127915;</span>';

  // Word doc sync indicator
  if (task.sharepoint_url || task.sharepoint_path) icons += '<span class="agent-icon" title="Synced to Word/SharePoint" style="font-size:11px;font-weight:700;color:var(--accent);">W</span>';

  let meta = `<span class="badge ${priClass}">${task.priority}</span>`;
  if (task.domain) meta += `<span class="badge badge-domain">${task.domain}</span>`;
  const mtg = meetingName(task.source_meeting);
  if (mtg) meta += `<span class="badge badge-meeting" title="${escapeHtml(task.source_meeting)}">${escapeHtml(mtg)}</span>`;

  if (queueName === 'waiting') {
    if (task.waiting_on) meta += `<span class="badge badge-waiting">${task.waiting_on}</span>`;
    if (task.waiting_expected) {
      const today = new Date().toISOString().slice(0, 10);
      const isOverdue = String(task.waiting_expected) < today;
      const cls = isOverdue ? 'badge-overdue' : 'badge-due';
      const label = isOverdue ? `OVERDUE (${task.waiting_expected})` : `exp: ${task.waiting_expected}`;
      meta += `<span class="badge ${cls}">${label}</span>`;
    }
  } else if (task.due) {
    const today = new Date().toISOString().slice(0, 10);
    const isOverdue = String(task.due) < today;
    const cls = isOverdue ? 'badge-overdue' : 'badge-due';
    const label = isOverdue ? `OVERDUE (${task.due})` : `due: ${task.due}`;
    meta += `<span class="badge ${cls}">${label}</span>`;
  }

  return `
    <div class="card" onclick="openTask('${task.id}')">
      <div class="card-top">
        <span class="card-id">${task.id}</span>
        <span class="card-icons">${icons}</span>
      </div>
      <div class="card-title">${escapeHtml(task.title)}</div>
      <div class="card-meta">${meta}</div>
    </div>
  `;
}
