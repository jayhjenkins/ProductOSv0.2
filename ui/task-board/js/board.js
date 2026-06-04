// ─── Fetch & Render ─────────────────────────────────────────────────

async function fetchTasks() {
  try {
    const res = await fetch(`${API}/tasks`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    allTasks = await res.json();
    renderNow();
    renderStats();
  } catch (err) {
    document.getElementById('now-view').innerHTML =
      `<div class="loading">Error loading tasks: ${err.message}</div>`;
  }
}

function renderStats() {
  const stats = document.getElementById('stats');
  if (!stats) return;
  // Quiet, non-alarming header: just the day. No counts — counts breed avoidance.
  const today = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
  stats.innerHTML = `<span class="stat-quiet">${today}</span>`;
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

// ─── Card (calm, decluttered) ───────────────────────────────────────
// Keeps the two signals that matter — which queue/type the card is, and
// the source meeting it came from — and pulls the two most-common actions
// (Mark done · Open output) onto the card face. Priority is a quiet dot;
// domain is quiet text; cron-born tasks get a calm `cron` chip.

const QUEUE_META = {
  human:   { cls: 'q-human',   label: 'human',      icon: 'human' },
  collab:  { cls: 'q-collab',  label: 'supervised', icon: 'collab' },
  agent:   { cls: 'q-agent',   label: 'agent',      icon: 'agent' },
  waiting: { cls: 'q-waiting', label: 'waiting',    icon: 'waiting' },
};

// Judge score — a quiet, band-tinted rating that lives in the card head
// (next to the status mark) so it reads as part of the card's state without
// adding a whole signals row of its own.
function judgeBand(score) {
  return score >= 8 ? 'good' : (score >= 5 ? 'mid' : 'low');
}
function judgeScoreBadge(task) {
  if (task.judge_score == null) return '';
  const js = Number(task.judge_score);
  return `<span class="card-score ${judgeBand(js)}" title="Judge rated this ${js}/10${task.judge_why ? ' — ' + task.judge_why.replace(/"/g, '&quot;') : ''}">${js}<span class="card-score-of">/10</span></span>`;
}

function statusMark(task) {
  switch (task.agent_status) {
    case 'running':     return '<span class="status-mark" title="Agent working"><span class="mark-running"></span></span>';
    case 'needs-human': return `<span class="status-mark" style="color:var(--warning)" title="Needs your input">${svgIcon('needsHuman')}</span>`;
    case 'complete':    return `<span class="status-mark" style="color:var(--success)" title="Ready for review">${svgIcon('complete')}</span>`;
    case 'failed':      return `<span class="status-mark" style="color:var(--danger)" title="Agent stopped">${svgIcon('failed')}</span>`;
    default:            return '';
  }
}

function outputLink(task) {
  if (task.agent_output) {
    const v = String(task.agent_output).trim();
    if (v.endsWith('.md')) return { href: obsidianUri(v), label: 'Open output', external: false };
    const m = v.match(/https?:\/\/[^\s)]+/);
    if (m) return { href: m[0], label: 'Open output', external: true };
  }
  if (task.sharepoint_url) return { href: task.sharepoint_url, label: 'Open in Word', external: true };
  if (task.sharepoint_path) return { href: `/open?file=${encodeURIComponent(task.sharepoint_path)}`, label: 'Open in Word', external: false };
  return null;
}

function isCronTask(task) {
  return !!((task.tags && task.tags.includes('cron')) || (task.body && /<!--\s*CRON\b/.test(task.body)));
}

// Card-face quick action — marks done without opening the modal.
function quickDone(id, ev) {
  if (ev) ev.stopPropagation();
  fetch(`${API}/tasks/${id}/done`, { method: 'POST' })
    .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); toast('Marked done. Nicely cleared.', 'success'); fetchTasks(); })
    .catch(err => toast(`Could not mark done: ${err.message}`));
}

function renderCard(task, queueName) {
  const q = QUEUE_META[task.queue] || QUEUE_META[queueName] || QUEUE_META.human;
  const prioClass = `prio-${task.priority || 'low'}`;
  const today = new Date().toISOString().slice(0, 10);

  // Head — queue/type chip (the "what kind of card is this") + judge score + status mark + id
  let head = `<div class="card-head">`;
  head += `<span class="card-queue">${svgIcon(q.icon)}${q.label}</span>`;
  head += `<span class="card-head-right">${judgeScoreBadge(task)}${statusMark(task)}<span class="card-id">${task.id}</span></span>`;
  head += `</div>`;

  // Title — with a single quiet priority dot
  const title = `<div class="card-title"><span class="prio-dot ${prioClass}" title="${task.priority || 'low'} priority"></span><span>${escapeHtml(task.title)}</span></div>`;

  // Context — source meeting (elevated) + domain (quiet)
  const ctxParts = [];
  const mtg = meetingName(task.source_meeting);
  if (mtg) ctxParts.push(`<span class="card-from" title="From: ${escapeHtml(task.source_meeting)}">${svgIcon('meeting')}<span>${escapeHtml(mtg)}</span></span>`);
  if (task.domain) ctxParts.push(`<span class="card-domain">${escapeHtml(task.domain)}</span>`);
  const context = ctxParts.length ? `<div class="card-context">${ctxParts.join('<span class="sep">·</span>')}</div>` : '';

  // Signals — only what's present, calm
  const signals = [];
  if (task.queue === 'waiting') {
    if (task.waiting_on) signals.push(`<span class="chip chip-waiting">${svgIcon('hourglass')}${escapeHtml(task.waiting_on)}</span>`);
    if (task.waiting_expected) {
      const overdue = String(task.waiting_expected) < today;
      signals.push(overdue
        ? `<span class="chip chip-overdue">${svgIcon('overdue')}overdue · ${task.waiting_expected}</span>`
        : `<span class="chip chip-due">${svgIcon('due')}by ${task.waiting_expected}</span>`);
    }
  } else if (task.due) {
    const overdue = String(task.due) < today;
    signals.push(overdue
      ? `<span class="chip chip-overdue">${svgIcon('overdue')}overdue · ${task.due}</span>`
      : `<span class="chip chip-due">${svgIcon('due')}due ${task.due}</span>`);
  }
  if (task.task_type === 'schedule-meeting') signals.push(`<span class="chip chip-meeting">${svgIcon('meeting')}schedule</span>`);
  if (task.task_type === 'send-message') signals.push(`<span class="chip chip-meeting" style="color:var(--q-human);background:color-mix(in oklab, var(--q-human) 16%, transparent)">${svgIcon('chat')}message</span>`);
  if (task.body && task.body.includes('<!-- JIRA_DRAFT -->')) signals.push(`<span class="chip chip-cron" style="color:var(--accent);background:var(--accent-soft)">${svgIcon('jira')}jira draft</span>`);
  if (isCronTask(task)) signals.push(`<span class="chip chip-cron">${svgIcon('cron')}cron</span>`);
  const signalsHtml = signals.length ? `<div class="card-signals">${signals.join('')}</div>` : '';

  // Actions — pulled forward: Mark done + Open output
  const running = task.agent_status === 'running';
  const out = outputLink(task);
  const actions = [];
  if (!running) actions.push(`<button class="card-action primary" onclick="quickDone('${task.id}', event)">${svgIcon('done')}Mark done</button>`);
  if (out) {
    const ext = out.external ? ' target="_blank" rel="noopener"' : '';
    actions.push(`<a class="card-action" href="${escapeHtml(out.href)}"${ext} onclick="event.stopPropagation()">${svgIcon('output')}${out.label}</a>`);
  }
  const actionsHtml = actions.length ? `<div class="card-actions">${actions.join('')}</div>` : '';

  return `<div class="card ${q.cls}" onclick="openTask('${task.id}')">${head}${title}${context}${signalsHtml}${actionsHtml}</div>`;
}
