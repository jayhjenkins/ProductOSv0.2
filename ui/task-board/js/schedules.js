// ─── Cron Tab ──────────────────────────────────────────────────────

const CRON_EXAMPLES = [
  "Every Monday morning, pull Pendo usage metrics and update the metrics spreadsheet",
  "Every Friday at 4pm, summarize this week's Jira tickets and standup notes into a velocity brief",
  "Daily at 8am for 2 weeks, check early adopter program metrics from Pendo and write a progress report",
  "Every Wednesday, go through Zendesk tickets from the past 7 days and give me a product feedback summary",
];

async function fetchCronJobs() {
  const view = document.getElementById('cron-view');
  try {
    const res = await fetch(`${API}/cron`);
    const data = await res.json();
    cronJobs = data.jobs || [];
    renderCronList();
  } catch (err) {
    view.innerHTML = `<div class="cron-empty" style="color:var(--danger)">Failed to load cron jobs: ${err.message}</div>`;
  }
}

function renderCronList() {
  const view = document.getElementById('cron-view');
  let html = `<div class="cron-head">
    <div>
      <h3>Recurring Jobs</h3>
      <p class="cron-head-sub">Standing jobs that quietly create tasks on a schedule.</p>
    </div>
    <button class="cron-btn" onclick="showCronCreate()">New job</button>
  </div>`;

  if (cronJobs.length === 0) {
    html += `<div class="cron-empty">
      <div style="font-size:20px;margin-bottom:6px;color:var(--text)">Nothing scheduled yet</div>
      <div>Create a job to have an agent do recurring work for you.</div>
    </div>`;
    view.innerHTML = html;
    return;
  }

  // Quiet relative date, e.g. "Mon, Jun 8" — the time already lives in the plain-English line
  const fmt = ts => ts ? new Date(ts).toLocaleString('en-US', {weekday:'short',month:'short',day:'numeric'}) : null;

  html += '<div class="cron-cards">';
  for (const job of cronJobs) {
    const isOff = !job.enabled;
    const schedule = esc(job.cron_human || job.cron_expr);
    const nextRun = fmt(job.next_run);
    const lastRun = fmt(job.last_run);
    const latestTask = job.task_history?.length ? job.task_history[job.task_history.length - 1] : null;

    // Foot — quiet, only what helps: when it next runs (or paused) and when it last ran
    const foot = [];
    foot.push(isOff ? `<span>Paused</span>` : (nextRun ? `<span>Next ${nextRun}</span>` : `<span>Schedule set</span>`));
    foot.push(`<span>${lastRun ? `Last ran ${lastRun}` : `Hasn’t run yet`}</span>`);
    if (job.expires) {
      const days = (new Date(job.expires) - new Date()) / 86400000;
      const ends = new Date(job.expires).toLocaleDateString('en-US', {month:'short',day:'numeric'});
      foot.push(`<span class="${days < 7 ? 'cron-card-expires' : ''}">Ends ${ends}</span>`);
    }

    html += `<div class="cron-card card ${isOff ? 'is-off' : ''}">
      <div class="cron-card-top">
        <span class="cron-card-name">${esc(job.name)}</span>
        <label class="cron-toggle" title="${job.enabled ? 'Turn off' : 'Turn on'}">
          <input type="checkbox" ${job.enabled ? 'checked' : ''} onchange="toggleCronJob('${job.id}')">
          <span class="cron-toggle-slider"></span>
        </label>
      </div>
      <div class="cron-card-when">${svgIcon('cron')}<span>${schedule}</span></div>
      <div class="cron-card-foot">${foot.join('<span class="sep">·</span>')}</div>
      <div class="cron-card-actions">
        <button class="card-action primary" id="cron-run-${job.id}" onclick="runCronJob('${job.id}')">Run now</button>
        <button class="card-action" onclick="editCronJob('${job.id}')">Edit</button>
        <button class="card-action danger" id="cron-del-${job.id}" onclick="deleteCronJob('${job.id}')">Delete</button>
        ${latestTask ? `<a class="card-action cron-latest" href="#" onclick="switchTab('now');setTimeout(()=>openTask('${latestTask}'),300);return false">${svgIcon('output')}Latest run</a>` : ''}
      </div>
    </div>`;
  }
  html += '</div>';
  view.innerHTML = html;
}

function esc(s) { if (!s) return ''; const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

function showCronCreate() {
  const view = document.getElementById('cron-view');
  cronRawInput = '';

  view.innerHTML = `<div class="cron-create">
    <h3>New job <button class="cron-btn small secondary" onclick="fetchCronJobs()">Cancel</button></h3>
    <textarea class="cron-textarea" id="cron-input" placeholder="Describe what you want to happen and when, in plain English.&#10;&#10;e.g. Every Monday morning, go through Zendesk tickets from the past 7 days and give me a report on product feedback themes."></textarea>
    <div class="cron-parse-actions">
      <button class="cron-btn" id="cron-parse-btn" onclick="parseCronInput()">Parse &rarr;</button>
      <span id="cron-parse-status"></span>
    </div>
  </div>`;

  document.getElementById('cron-input').addEventListener('keydown', e => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') parseCronInput();
  });
  document.getElementById('cron-input').focus();
}

async function parseCronInput() {
  const text = document.getElementById('cron-input').value.trim();
  if (!text) return;
  cronRawInput = text;

  const btn = document.getElementById('cron-parse-btn');
  const status = document.getElementById('cron-parse-status');
  btn.disabled = true;
  btn.textContent = 'Parsing...';
  status.innerHTML = '<span class="cron-spinner"></span> Asking Ollama to parse your request...';

  try {
    const res = await fetch(`${API}/cron/parse`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text}),
    });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    renderCronReview(data.parsed);
  } catch (err) {
    status.innerHTML = `<span style="color:var(--danger)">Parse failed: ${esc(err.message)}</span>`;
    btn.disabled = false;
    btn.textContent = 'Parse →';
  }
}

function renderCronReview(parsed, editJobId = null) {
  const view = document.getElementById('cron-view');
  const tpl = parsed.task_template || {};
  const isEdit = !!editJobId;

  view.innerHTML = `<div class="cron-create cron-review">
    <h3>${isEdit ? 'Edit' : 'Review'} Cron Job
      <button class="cron-btn small secondary" onclick="${isEdit ? 'fetchCronJobs()' : 'showCronCreate()'}">
        ${isEdit ? 'Cancel' : '&larr; Back'}
      </button>
    </h3>

    <div class="cron-field">
      <label>Name</label>
      <input type="text" id="cr-name" value="${esc(parsed.name || '')}">
    </div>

    <div class="cron-field-row">
      <div class="cron-field" style="flex:1">
        <label>Schedule (cron expression)</label>
        <input type="text" id="cr-cron-expr" value="${esc(parsed.cron_expr || '')}" oninput="previewCronExpr()">
        <div class="cron-preview-runs" id="cr-preview">Loading preview...</div>
      </div>
      <div class="cron-field" style="flex:1">
        <label>Human-readable</label>
        <input type="text" id="cr-cron-human" value="${esc(parsed.cron_human || '')}">
      </div>
    </div>

    <div class="cron-field">
      <label>Task Title (created each run — use {date}, {week}, {month})</label>
      <input type="text" id="cr-title" value="${esc(tpl.title || parsed.name || '')}">
    </div>

    <div class="cron-field-row">
      <div class="cron-field">
        <label>Queue</label>
        <select id="cr-queue">
          ${['agent','collab','human','waiting'].map(q => `<option value="${q}" ${tpl.queue===q?'selected':''}>${q}</option>`).join('')}
        </select>
      </div>
      <div class="cron-field">
        <label>Priority</label>
        <select id="cr-priority">
          ${['low','medium','high','critical'].map(p => `<option value="${p}" ${tpl.priority===p?'selected':''}>${p}</option>`).join('')}
        </select>
      </div>
      <div class="cron-field">
        <label>Domain</label>
        <select id="cr-domain">
          <option value="">(none)</option>
          ${['product','strategy','marketing','recruiting','metrics','learning','ops'].map(d => `<option value="${d}" ${tpl.domain===d?'selected':''}>${d}</option>`).join('')}
        </select>
      </div>
    </div>

    <div class="cron-field">
      <label>Task Instructions</label>
      <textarea class="cron-textarea" id="cr-description" style="min-height:120px">${esc(tpl.description || '')}</textarea>
    </div>

    <div class="cron-field-row">
      <div class="cron-field">
        <label>Expires</label>
        <input type="date" id="cr-expires" value="${parsed.expires ? parsed.expires.split('T')[0] : ''}">
      </div>
      <div class="cron-field" style="display:flex;align-items:flex-end;gap:8px;padding-bottom:2px">
        <label style="margin-bottom:0">
          <input type="checkbox" id="cr-auto-dispatch" ${parsed.auto_dispatch !== false ? 'checked' : ''}>
          Auto-dispatch when task is created
        </label>
      </div>
    </div>

    <div class="cron-review-actions">
      <button class="cron-btn" onclick="${isEdit ? `saveEditedCronJob('${editJobId}')` : 'confirmCronJob()'}">
        ${isEdit ? 'Save Changes' : 'Save Job'}
      </button>
      <button class="cron-btn secondary" onclick="${isEdit ? 'fetchCronJobs()' : 'showCronCreate()'}">Cancel</button>
    </div>
  </div>`;

  previewCronExpr();
}

async function previewCronExpr() {
  const expr = document.getElementById('cr-cron-expr').value.trim();
  const preview = document.getElementById('cr-preview');
  if (!expr) { preview.textContent = ''; return; }

  try {
    const res = await fetch(`${API}/cron/preview`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({cron_expr: expr, count: 5}),
    });
    const data = await res.json();
    if (data.error) {
      preview.className = 'cron-preview-runs error';
      preview.textContent = data.error;
      return;
    }
    const dates = data.runs.map(r => new Date(r).toLocaleString('en-US', {weekday:'short',month:'short',day:'numeric',hour:'numeric',minute:'2-digit'}));
    preview.className = 'cron-preview-runs';
    preview.textContent = 'Next 5: ' + dates.join('  ·  ');
  } catch {
    preview.className = 'cron-preview-runs error';
    preview.textContent = 'Could not preview';
  }
}

function _gatherCronForm() {
  return {
    name: document.getElementById('cr-name').value.trim(),
    cron_expr: document.getElementById('cr-cron-expr').value.trim(),
    cron_human: document.getElementById('cr-cron-human').value.trim(),
    task_template: {
      title: document.getElementById('cr-title').value.trim(),
      queue: document.getElementById('cr-queue').value,
      priority: document.getElementById('cr-priority').value,
      domain: document.getElementById('cr-domain').value || null,
      description: document.getElementById('cr-description').value.trim(),
      tags: ['cron'],
    },
    expires: document.getElementById('cr-expires').value || null,
    auto_dispatch: document.getElementById('cr-auto-dispatch').checked,
    raw_input: cronRawInput,
  };
}

async function confirmCronJob() {
  const job = _gatherCronForm();
  if (!job.name) return toast('Name is required', 'warn');
  if (!job.cron_expr) return toast('Cron expression is required', 'warn');

  try {
    const res = await fetch(`${API}/cron/confirm`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({job}),
    });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    fetchCronJobs();
  } catch (err) {
    toast('Failed to save: ' + err.message);
  }
}

function editCronJob(jobId) {
  const job = cronJobs.find(j => j.id === jobId);
  if (!job) return;
  cronRawInput = job.raw_input || '';
  renderCronReview({
    name: job.name,
    cron_expr: job.cron_expr,
    cron_human: job.cron_human,
    task_template: job.task_template,
    expires: job.expires,
    auto_dispatch: job.auto_dispatch,
  }, jobId);
}

async function saveEditedCronJob(jobId) {
  const form = _gatherCronForm();
  if (!form.name) return toast('Name is required', 'warn');
  if (!form.cron_expr) return toast('Cron expression is required', 'warn');

  try {
    const res = await fetch(`${API}/cron/${jobId}`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        name: form.name,
        cron_expr: form.cron_expr,
        cron_human: form.cron_human,
        task_template: form.task_template,
        expires: form.expires,
        auto_dispatch: form.auto_dispatch,
        raw_input: form.raw_input,
      }),
    });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    fetchCronJobs();
  } catch (err) {
    toast('Failed to save: ' + err.message);
  }
}

async function toggleCronJob(jobId) {
  try {
    await fetch(`${API}/cron/${jobId}/toggle`, {method: 'POST'});
    fetchCronJobs();
  } catch (err) {
    toast('Toggle failed: ' + err.message);
  }
}

async function runCronJob(jobId) {
  const job = cronJobs.find(j => j.id === jobId);
  const ok = await confirmAction({
    title: 'Run this job now?',
    message: job && job.name ? `“${job.name}” will run immediately and create a task.` : 'This job will run immediately and create a task.',
    confirmLabel: 'Run now',
  });
  if (!ok) return;
  const btn = document.getElementById(`cron-run-${jobId}`);
  if (btn) { btn.textContent = 'Running…'; btn.disabled = true; }
  try {
    const res = await fetch(`${API}/cron/${jobId}/run`, {method: 'POST'});
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    fetchCronJobs();
  } catch (err) {
    toast('Run failed: ' + err.message);
  }
}

async function deleteCronJob(jobId) {
  const job = cronJobs.find(j => j.id === jobId);
  const ok = await confirmAction({
    title: 'Delete this job?',
    message: job && job.name ? `“${job.name}” will stop running and be removed. This can’t be undone.` : 'This recurring job will stop running and be removed. This can’t be undone.',
    confirmLabel: 'Delete',
    danger: true,
  });
  if (!ok) return;
  try {
    await fetch(`${API}/cron/${jobId}/delete`, {method: 'POST'});
    fetchCronJobs();
  } catch (err) {
    toast('Delete failed: ' + err.message);
  }
}

function toggleCronHistory(jobId) {
  const el = document.getElementById(`history-${jobId}`);
  const job = cronJobs.find(j => j.id === jobId);
  if (!job || !el) return;
  const history = job.task_history || [];
  if (el.dataset.expanded === 'true') {
    el.innerHTML = `<a href="#" onclick="toggleCronHistory('${jobId}');return false">Show ${history.length} task history</a>`;
    el.dataset.expanded = 'false';
  } else {
    const links = history.slice().reverse().map(tid =>
      `<a href="#" onclick="switchTab('now');setTimeout(()=>openTask('${tid}'),300);return false">${tid}</a>`
    ).join(', ');
    el.innerHTML = `<a href="#" onclick="toggleCronHistory('${jobId}');return false">Hide history</a><br>${links}`;
    el.dataset.expanded = 'true';
  }
}
