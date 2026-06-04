// ─── LangFuse Health ────────────────────────────────────────────────

async function checkLangfuseHealth() {
  const dot = document.getElementById('lf-status-dot');
  if (!dot) return;
  try {
    const res = await fetch(`${API}/langfuse/health`);
    const data = await res.json();
    dot.className = 'lf-status ' + (data.status === 'ok' ? 'ok' : 'error');
    dot.title = data.status === 'ok' ? 'LangFuse connected' : `LangFuse: ${data.message || data.status}`;
  } catch {
    dot.className = 'lf-status error';
    dot.title = 'LangFuse unreachable';
  }
}

// ─── Prompts View ───────────────────────────────────────────────────

async function fetchPrompts() {
  const view = document.getElementById('prompts-view');
  try {
    const [promptsRes, statsRes] = await Promise.all([
      fetch(`${API}/langfuse/prompts`),
      fetch(`${API}/langfuse/traces/stats`),
    ]);
    const promptsData = await promptsRes.json();
    const statsData = await statsRes.json();
    renderPrompts(promptsData.prompts || [], statsData.stats || {});
  } catch (err) {
    view.innerHTML = `<div class="loading" style="color:var(--danger)">LangFuse unavailable: ${err.message}</div>`;
  }
}

function renderPrompts(prompts, stats) {
  const view = document.getElementById('prompts-view');
  const workers = prompts.filter(p => p.name.startsWith('worker-') && p.name !== 'worker-router');
  const workerRouter = prompts.find(p => p.name === 'worker-router');
  const taskParser = prompts.filter(p => p.name === 'task-parser');
  const cronParser = prompts.find(p => p.name === 'cron-parser');
  const skills = prompts.filter(p => p.name.startsWith('skill-'));
  const STEP_ICONS = {'task-parser': '📝', 'worker-match': '🔀', 'worker-execution': '🤖'};

  let html = '';

  // Workers section
  html += '<div class="prompts-section-title">Workers</div>';
  html += '<div class="prompt-cards">';
  if (workers.length === 0) {
    html += '<div style="color:var(--text-muted);font-size:13px;">No worker prompts registered. Run: python3 scripts/langfuse_setup.py</div>';
  }
  for (const p of workers) {
    const s = stats[`worker-execution`] || {};
    const workerName = p.name.replace('worker-', '');
    html += `<div class="prompt-card" onclick="openWorkerDetail('${workerName}')" style="cursor:pointer">
      <div class="prompt-card-header">
        <span class="prompt-card-name">${workerName}</span>
        <span class="prompt-card-version">v${p.version || '?'}</span>
      </div>
      <div class="prompt-card-desc">${(p.labels || []).join(', ') || 'no labels'}</div>
      <div class="prompt-card-stats">
        <span>Traces: ${s.count || 0}</span>
        <span class="${(s.success_rate||0) >= 80 ? 'stat-good' : 'stat-bad'}">Success: ${s.success_rate || 0}%</span>
      </div>
      <div style="font-size:11px;color:var(--text-dim);margin-top:6px;">Click for details</div>
    </div>`;
  }
  html += '</div>';

  // Infrastructure Prompts section
  html += '<div class="prompts-section-title">Infrastructure Prompts</div>';
  html += '<div class="prompt-cards">';

  // Task Parser
  for (const p of taskParser) {
    const s = stats['task-parser'] || {};
    html += `<div class="prompt-card">
      <div class="prompt-card-header">
        <span class="prompt-card-name">task-parser</span>
        <span class="prompt-card-version">v${p.version || '?'}</span>
      </div>
      <div class="prompt-card-desc">Classifies voice/text input into structured task fields (Ollama)</div>
      <div class="prompt-card-stats">
        <span>Traces: ${s.count || 0}</span>
        <span class="${(s.success_rate||0) >= 80 ? 'stat-good' : 'stat-bad'}">Success: ${s.success_rate || 0}%</span>
      </div>
      <a class="prompt-card-link" href="${LANGFUSE_HOST}/project/pm-os/prompts/${p.name}" target="_blank">View in LangFuse ↗</a>
    </div>`;
  }

  // Worker Router
  if (workerRouter) {
    const s = stats['worker-match'] || {};
    html += `<div class="prompt-card">
      <div class="prompt-card-header">
        <span class="prompt-card-name">worker-router</span>
        <span class="prompt-card-version">v${workerRouter.version || '?'}</span>
      </div>
      <div class="prompt-card-desc">Routes tasks to the best worker using LLM matching (Ollama)</div>
      <div class="prompt-card-stats">
        <span>Traces: ${s.count || 0}</span>
        <span class="${(s.success_rate||0) >= 80 ? 'stat-good' : 'stat-bad'}">Success: ${s.success_rate || 0}%</span>
      </div>
      <a class="prompt-card-link" href="${LANGFUSE_HOST}/project/pm-os/prompts/${workerRouter.name}" target="_blank">View in LangFuse ↗</a>
    </div>`;
  }

  // Cron Parser
  if (cronParser) {
    html += `<div class="prompt-card">
      <div class="prompt-card-header">
        <span class="prompt-card-name">cron-parser</span>
        <span class="prompt-card-version">v${cronParser.version || '?'}</span>
      </div>
      <div class="prompt-card-desc">Parses free-form text into structured cron job definitions (Ollama)</div>
      <a class="prompt-card-link" href="${LANGFUSE_HOST}/project/pm-os/prompts/${cronParser.name}" target="_blank">View in LangFuse ↗</a>
    </div>`;
  }

  if (taskParser.length === 0 && !workerRouter && !cronParser) {
    html += '<div style="color:var(--text-muted);font-size:13px;">Not registered yet. Run: python3 scripts/langfuse_setup.py</div>';
  }
  html += '</div>';

  // Skills section (collapsible)
  const skillsCollapsedDefault = skills.length > 12;
  html += `<div class="prompts-section-title" style="cursor:pointer;" onclick="toggleSkillsList()">
    Skills (${skills.length} registered) <span id="skills-toggle-icon">${skillsCollapsedDefault ? '▸' : '▾'}</span>
  </div>`;
  html += `<div class="prompt-cards" id="skills-grid" style="${skillsCollapsedDefault ? 'display:none;' : ''}">`;
  for (const p of skills) {
    html += `<a class="prompt-card" style="padding:10px;text-decoration:none;cursor:pointer;" href="${LANGFUSE_HOST}/project/pm-os/prompts/${p.name}" target="_blank">
      <div class="prompt-card-header">
        <span class="prompt-card-name" style="font-size:12px;">${p.name.replace('skill-', '')}</span>
        <span class="prompt-card-version">v${p.version || '?'}</span>
      </div>
    </a>`;
  }
  html += '</div>';

  // Link to full LangFuse UI
  html += `<div style="text-align:center;margin-top:20px;">
    <a href="${LANGFUSE_HOST}/project/pm-os" target="_blank" style="color:var(--accent);font-size:13px;text-decoration:none;">Open LangFuse Dashboard ↗</a>
  </div>`;

  view.innerHTML = html;
}

function toggleSkillsList() {
  const grid = document.getElementById('skills-grid');
  const icon = document.getElementById('skills-toggle-icon');
  if (grid.style.display === 'none') {
    grid.style.display = '';
    icon.textContent = '▾';
  } else {
    grid.style.display = 'none';
    icon.textContent = '▸';
  }
}

// ─── Worker Detail Modal ───────────────────────────────────────────

async function fetchWorkerDetails() {
  if (_workerCache) return _workerCache;
  try {
    const res = await fetch(`${API}/workers`);
    const data = await res.json();
    _workerCache = data.workers || [];
    return _workerCache;
  } catch { return []; }
}

async function openWorkerDetail(workerName) {
  const overlay = document.getElementById('modal-overlay');
  const modalBody = document.getElementById('modal-body');
  const modalTitle = document.getElementById('modal-title');
  const modalActions = document.getElementById('modal-actions');

  overlay.classList.add('active');
  modalBody.innerHTML = '<div class="loading">Loading worker details...</div>';
  modalTitle.textContent = workerName;
  modalActions.innerHTML = '';

  const workers = await fetchWorkerDetails();
  const w = workers.find(w => w.name === workerName);
  if (!w) {
    modalBody.innerHTML = '<div class="loading">Worker not found</div>';
    modalActions.innerHTML = '<button class="btn" onclick="closeModal()">Close</button>';
    return;
  }

  let html = '';

  // Description + meta
  html += `<div style="color:var(--text-muted);font-size:13px;margin-bottom:14px;">${escapeHtml(w.description || '')}</div>`;
  html += `<div style="display:flex;gap:12px;font-size:11px;color:var(--text-dim);margin-bottom:16px;">`;
  html += `<span>Priority: ${w.priority}</span>`;
  html += `<span>Timeout: ${w.timeout}s</span>`;
  html += `<span>Max turns: ${w.max_turns}</span>`;
  html += `</div>`;

  // Tools
  html += '<div class="worker-detail-section">';
  html += '<div class="worker-detail-section-title">Allowed Tools</div>';
  html += '<div class="worker-tool-badges">';
  for (const tool of (w.allowed_tools || [])) {
    const isMcp = tool.startsWith('mcp__');
    const displayName = isMcp ? tool.replace('mcp__claude_ai_', '').replace('__*', '') : tool.replace('(*)', '');
    html += `<span class="worker-tool-badge ${isMcp ? 'mcp' : ''}" title="${escapeHtml(tool)}">${escapeHtml(displayName)}</span>`;
  }
  html += '</div></div>';

  // Skills
  html += '<div class="worker-detail-section">';
  html += '<div class="worker-detail-section-title">Skills</div>';
  html += '<div class="worker-skill-chips">';
  for (const skill of (w.skills || [])) {
    const shortName = skill.split('/').pop();
    html += `<span class="worker-skill-chip" title="${escapeHtml(skill)}">${escapeHtml(shortName)}</span>`;
  }
  if (!w.skills?.length) html += '<span style="color:var(--text-dim);font-size:12px;">(full catalog)</span>';
  html += '</div></div>';

  // Matching rules
  html += '<div class="worker-detail-section">';
  html += '<div class="worker-detail-section-title">Matching Rules</div>';
  html += '<div class="worker-match-rules">';
  const m = w.match || {};
  if (m.task_type?.length) html += `<div>Task type: ${m.task_type.map(t => `<code>${escapeHtml(t)}</code>`).join(', ')}</div>`;
  if (m.domains?.length) html += `<div>Domains: ${m.domains.map(d => `<code>${escapeHtml(d)}</code>`).join(', ')}</div>`;
  if (m.title_patterns?.length) {
    html += '<div style="margin-top:4px;">Title patterns:</div>';
    for (const p of m.title_patterns) html += `<div style="margin-left:12px;"><code>${escapeHtml(p)}</code></div>`;
  }
  if (m.description_patterns?.length) {
    html += '<div style="margin-top:4px;">Description patterns:</div>';
    for (const p of m.description_patterns) html += `<div style="margin-left:12px;"><code>${escapeHtml(p)}</code></div>`;
  }
  if (!m.task_type?.length && !m.domains?.length && !m.title_patterns?.length) {
    html += '<div style="color:var(--text-dim);">Catch-all (matches everything)</div>';
  }
  html += '</div></div>';

  // Prompt body
  html += '<div class="worker-detail-section">';
  html += '<div class="worker-detail-section-title">Prompt (read-only)</div>';
  html += `<div class="worker-prompt-view">${escapeHtml(w.prompt_body || '(no prompt body)')}</div>`;
  html += '</div>';

  modalBody.innerHTML = html;

  // Actions
  const lfPrompt = w.langfuse_prompt || `worker-${w.name}`;
  modalActions.innerHTML = `
    <a href="${LANGFUSE_HOST}/project/pm-os/prompts/${lfPrompt}" target="_blank" class="btn btn-primary">Edit Prompt in LangFuse</a>
    <button class="btn" onclick="closeModal()">Close</button>
  `;
}
