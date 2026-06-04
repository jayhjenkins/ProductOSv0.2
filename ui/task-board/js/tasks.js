// tasks.js — Task-detail modal + all task action verbs
// Extracted from index.html inline script (Task 0.2). Depends on globals from core.js
// (API, LANGFUSE_HOST, allTasks, currentTaskId, emailCache, escapeHtml, formatDate,
// toast, meetingName, obsidianUri, renderAgentOutput) and on board/cron functions
// (fetchTasks, etc.) that remain in the inline script — all resolved as globals at call time.

// Provenance for the Details row. "creator" recorded the mechanism (human ran
// the CLI / cron fired / an agent acted), so meeting-spawned tasks all read
// "human" — as if a person authored them. Prefer the originating meeting (with
// its date) when there is one; otherwise say plainly where the task came from.
function taskSource(task) {
  if (task.source_meeting) {
    const name = meetingName(task.source_meeting) || 'Meeting';
    const d = (task.source_meeting.split('/').pop().match(/^(\d{4}-\d{2}-\d{2})/) || [])[1];
    return d ? `${name} · ${d}` : name;
  }
  if (task.creator === 'cron') return 'Recurring job';
  if (task.creator === 'agent') return 'Agent';
  return 'Added manually';
}

// ─── Modal ──────────────────────────────────────────────────────────

// Shorten an artifact path to read relative to the PM-OS root. Output files
// always live under the PM-OS folder structure (locally as datasets/…, mirrored
// to OneDrive as …/PM-OS/…), so the long absolute prefix is just noise. Both
// the Obsidian (.md) and Word (.docx) tiles end up showing product/agent-output/…
function shortArtifactPath(p) {
  if (!p) return '';
  let s = String(p).replace(/\\/g, '/');
  const m = s.match(/\/(?:pm[-_ ]?os)\//i);   // OneDrive mirror or absolute repo path
  if (m) s = s.slice(m.index + m[0].length);
  s = s.replace(/^datasets\//i, '');          // drop the local datasets/ wrapper
  return s;
}

async function openTask(taskId) {
  currentTaskId = taskId;
  const overlay = document.getElementById('modal-overlay');
  const modalBody = document.getElementById('modal-body');
  const modalTitle = document.getElementById('modal-title');
  const modalActions = document.getElementById('modal-actions');

  overlay.classList.add('active');
  modalBody.innerHTML = '<div class="loading">Loading...</div>';
  modalTitle.textContent = taskId;
  modalActions.innerHTML = '';

  try {
    const res = await fetch(`${API}/tasks/${taskId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const task = await res.json();

    modalTitle.innerHTML = escapeHtml(task.title);

    let html = '';

    // ── Identity: the keepers — id · type · state · source · updated ──
    const QMETA = { agent: ['agent', 'agent'], collab: ['supervised', 'collab'], human: ['human', 'human'], waiting: ['waiting', 'waiting'] };
    const qm = QMETA[task.queue] || QMETA.human;
    let stCls = '', stLabel = (task.status || 'open').replace(/-/g, ' '), stIcon = '';
    if (task.agent_status === 'running')          { stCls = 'is-running';     stLabel = 'running';         stIcon = '<span class="mark-running"></span>'; }
    else if (task.agent_status === 'needs-human') { stCls = 'is-needs-human'; stLabel = 'needs you';       stIcon = svgIcon('needsHuman'); }
    else if (task.agent_status === 'complete')    { stCls = 'is-complete';    stLabel = 'ready to review'; stIcon = svgIcon('complete'); }
    else if (task.agent_status === 'failed')      { stCls = 'is-failed';      stLabel = 'stopped';         stIcon = svgIcon('failed'); }
    else if (task.queue === 'waiting')            { stLabel = 'waiting';      stIcon = svgIcon('hourglass'); }

    html += `<div class="dt-identity">`;
    html += `<span class="dt-type q-${task.queue}">${svgIcon(qm[1])}${qm[0]}</span>`;
    html += `<span class="dt-idsep">·</span><span class="dt-status ${stCls}">${stIcon}${stLabel}</span>`;
    if (task.source_meeting) {
      html += `<span class="dt-idsep">·</span><span class="dt-source" title="From ${escapeHtml(task.source_meeting)}">${svgIcon('meeting')}<span>${escapeHtml(meetingName(task.source_meeting))}</span></span>`;
    }
    html += `<span class="dt-idsep">·</span><span class="dt-when">updated ${formatDate(task.updated)}</span>`;
    html += `</div>`;

    // ── Output — prime real estate, same place on every card ──────────
    const isAgentish = task.queue === 'agent' || task.queue === 'collab';
    const artifacts = [];
    if (task.agent_output) {
      const v = String(task.agent_output).trim();
      if (v.endsWith('.md')) {
        artifacts.push({ icon: 'obsidian', cls: '', kind: 'Obsidian', name: v.split('/').pop(), path: shortArtifactPath(v), href: obsidianUri(v), label: 'Open in Obsidian', external: false });
      } else {
        const mu = v.match(/https?:\/\/[^\s)]+/);
        if (mu) artifacts.push({ icon: 'output', cls: '', kind: 'Link', name: 'Agent output', path: mu[0].replace(/^https?:\/\//, ''), href: mu[0], label: 'Open', external: true });
        else artifacts.push({ icon: 'output', cls: '', kind: 'Output', name: 'Agent output', path: v, href: null, label: '', external: false });
      }
    }
    if (task.sharepoint_url || task.sharepoint_path) {
      const p = task.sharepoint_path || '';
      artifacts.push({ icon: 'doc', cls: 'doc', kind: 'Word', name: p ? p.split('/').pop() : 'Word document', path: p ? shortArtifactPath(p) : 'Word Online', href: task.sharepoint_url || `/open?file=${encodeURIComponent(task.sharepoint_path)}`, label: 'Open in Word', external: !!task.sharepoint_url });
    }
    if (artifacts.length) {
      html += `<div class="dt-output-wrap"><div class="dt-art-grid">`;
      artifacts.forEach(a => {
        const ext = a.external ? ' target="_blank" rel="noopener"' : '';
        const href = a.href ? ` href="${escapeHtml(a.href)}"` : '';
        html += `<a class="dt-artifact ${a.cls}"${href}${ext} onclick="event.stopPropagation()">`;
        html += `<span class="dt-art-top"><span class="dt-art-icon">${svgIcon(a.icon)}</span><span class="dt-art-kind">${a.kind}</span></span>`;
        html += `<span class="dt-art-name">${escapeHtml(a.name)}</span>`;
        html += `<span class="dt-art-path">${escapeHtml(a.path)}</span>`;
        if (a.label) html += `<span class="dt-art-open">${a.label}${svgIcon('output')}</span>`;
        html += `</a>`;
      });
      html += `</div>`;
      const lastOut = (task.activity_log || []).filter(e => e.type === 'output').pop();
      if (lastOut) html += `<div class="dt-output-note">${escapeHtml(lastOut.content)}</div>`;
      html += `</div>`;
    } else if (isAgentish && task.task_type !== 'schedule-meeting' && task.task_type !== 'send-message' && !(task.body && task.body.includes('<!-- JIRA_DRAFT -->'))) {
      let msg = 'No output yet.', mIcon = svgIcon('waiting');
        if (task.agent_status === 'running') { msg = 'Agent is working — the output will land here when it’s done.'; mIcon = '<span class="mark-running"></span>'; }
        else if (task.agent_status === 'failed') { msg = 'Agent stopped before producing an output.'; mIcon = svgIcon('failed'); }
        else if (task.agent_status === 'needs-human') { msg = 'Paused — it needs your input before it can finish.'; mIcon = svgIcon('needsHuman'); }
        else if (task.status === 'open') { msg = 'Not started yet — dispatch the agent to produce an output.'; }
        html += `<div class="dt-output-wrap"><div class="dt-output-empty">${mIcon}<span>${msg}</span></div></div>`;
    }

    // ── The task — what was actually asked (the brief) ────────────────
    let descContent = null; const otherSecs = [];
    if (task.body) {
      task.body.trim().split(/^## /m).filter(s => s.trim()).forEach(section => {
        const lines = section.split('\n');
        const t = lines[0].trim(); const content = lines.slice(1).join('\n').trim();
        const tl = t.toLowerCase();
        if (tl === 'activity log' || tl === 'suggested times' || tl === 'jira draft') return;
        if (tl === 'description') descContent = content;
        else if (content) otherSecs.push([t, content]);
      });
    }
    html += `<div class="dt-section">`;
    html += `<div class="dt-sec-head"><span class="dt-sec-title">The task</span>`;
    if (descContent !== null) html += `<button class="dt-textbtn" id="desc-edit-btn" onclick="toggleDescEdit()">Edit</button>`;
    html += `</div>`;
    if (descContent !== null) {
      html += `<div id="desc-display" class="dt-prose">${escapeHtml(descContent)}</div>`;
      html += `<div id="desc-editor" style="display:none;margin-top:8px;"><textarea class="desc-textarea" id="desc-input">${escapeHtml(descContent)}</textarea><div class="desc-actions"><button class="btn btn-primary" onclick="saveDescription()">Save</button><button class="btn" onclick="toggleDescEdit()">Cancel</button></div></div>`;
    } else {
      html += `<div class="dt-prose dim">${escapeHtml(task.title)}</div>`;
    }
    otherSecs.forEach(([t, content]) => {
      html += `<div class="dt-subsec"><div class="dt-subsec-label">${escapeHtml(t)}</div><div class="dt-prose">${escapeHtml(content)}</div></div>`;
    });
    html += `</div>`;

    // Determine task type flags early so all sections can use them
    const isScheduleMeeting = task.task_type === 'schedule-meeting';
    const isAgentComplete = task.agent_status === 'complete' && task.status === 'done';

    // Schedule-meeting — two calm columns: the invite · pick a time
    if (isScheduleMeeting) {
      await loadEmailCache();
      const attendees = task.meeting_attendees || [];
      const slots = task.body ? parseSlots(task.body) : [];
      const isRecurring = task.meeting_recurring || false;
      const recurrencePattern = task.meeting_recurrence_pattern || 'weekly';
      const initials = (s) => String(s).trim().split(/\s+/).map(w => w[0] || '').slice(0, 2).join('').toUpperCase() || '?';

      html += `<div class="dt-section">`;
      html += `<div class="dt-sec-head"><span class="dt-sec-title">Meeting</span><button class="dt-textbtn" id="btn-edit-meeting" onclick="editMeetingDetails()">Edit</button></div>`;
      html += `<div class="dt-meeting">`;

      // Left — the invite
      html += `<div class="dt-mcol">`;
      html += `<div class="dt-mcol-label">The invite</div>`;
      if (task.meeting_title) html += `<div class="dt-mtitle" id="meeting-title-display">${escapeHtml(task.meeting_title)}</div>`;
      html += `<div class="dt-mline"><span class="dt-mline-icon">${svgIcon('due')}</span><span class="dt-mwhen">${task.meeting_duration ? task.meeting_duration + ' minutes' : 'Duration TBD'}</span></div>`;
      html += `<div class="dt-att-list" id="attendee-chips">`;
      attendees.forEach(a => {
        const name = String(a);
        const email = (emailCache && emailCache[name]) || name;
        const hasEmail = email && email !== name;
        html += `<div class="dt-att" data-email="${escapeHtml(email)}"><span class="dt-att-avatar">${escapeHtml(initials(name))}</span><span class="dt-att-main"><span class="dt-att-name">${escapeHtml(name)}</span>${hasEmail ? `<span class="dt-att-email">${escapeHtml(email)}</span>` : ''}</span><span class="dt-att-remove" onclick="removeAttendee(this)">&times;</span></div>`;
      });
      html += `</div>`;
      html += `<div class="attendee-add-wrap dt-att-add"><input type="text" class="attendee-add-input" id="attendee-input" placeholder="Add someone…" autocomplete="off"><div class="attendee-dropdown" id="attendee-dropdown"></div></div>`;
      html += `<div class="dt-recurring"><label><input type="checkbox" id="recurring-check" ${isRecurring ? 'checked' : ''} onchange="toggleRecurring()"> Recurring</label><select class="recurring-select" id="recurring-pattern" ${isRecurring ? '' : 'style="display:none;"'} onchange="updateRecurrencePattern()"><option value="weekly" ${recurrencePattern === 'weekly' ? 'selected' : ''}>Weekly</option><option value="biweekly" ${recurrencePattern === 'biweekly' ? 'selected' : ''}>Biweekly</option><option value="monthly" ${recurrencePattern === 'monthly' ? 'selected' : ''}>Monthly</option></select></div>`;
      html += `</div>`;

      // Right — pick a time
      html += `<div class="dt-mcol">`;
      html += `<div class="dt-mcol-label">Pick a time</div>`;
      if (slots.length) {
        html += `<div class="dt-slots">`;
        slots.forEach((slot, i) => {
          html += `<div class="dt-slot" onclick="selectSlot(this, ${i})"><span class="dt-slot-radio"></span><input type="radio" name="slot" id="slot-${i}" value="${i}" data-start="${escapeHtml(slot.start)}" data-end="${escapeHtml(slot.end)}" style="display:none"><span class="dt-slot-label">${escapeHtml(slot.display)}</span></div>`;
        });
        html += `</div>`;
      } else {
        html += `<div class="dt-prose dim" style="font-size:12.5px;">No proposed times yet.</div>`;
      }
      html += `</div>`;

      html += `</div>`; // dt-meeting

      if (task.meeting_description) html += `<div class="dt-subsec"><div class="dt-subsec-label">Notes for the invite</div><div class="dt-prose" id="meeting-desc-display">${escapeHtml(task.meeting_description)}</div></div>`;
      html += `</div>`;
    }

    // Send-message — a calm preview of what will be sent
    if (task.task_type === 'send-message') {
      const ch = task.message_channel || 'Message';
      const isEmail = /email/i.test(ch);
      const to = task.message_to || '';
      const toInit = String(to).replace(/^[#@]/, '').trim().split(/\s+/).map(w => w[0] || '').slice(0, 2).join('').toUpperCase() || '?';
      html += `<div class="dt-section">`;
      html += `<div class="dt-sec-head"><span class="dt-sec-title">Message</span><button class="dt-textbtn" id="btn-edit-message" onclick="editMessage()">Edit</button></div>`;
      html += `<div class="dt-msg-to">`;
      html += `<span class="dt-msg-chip"><span class="k">To</span><span class="dt-msg-avatar">${escapeHtml(toInit)}</span>${escapeHtml(to)}</span>`;
      html += `<span class="dt-msg-channel">${svgIcon(isEmail ? 'mail' : 'chat')}${escapeHtml(ch)}</span>`;
      html += `</div>`;
      html += `<div class="dt-msg-bubble ${isEmail ? 'email' : ''}" id="message-display">`;
      if (isEmail && task.message_subject) html += `<div class="dt-msg-subject">${escapeHtml(task.message_subject)}</div>`;
      html += `<div id="message-body-text">${escapeHtml(task.message_body || '')}</div>`;
      html += `</div>`;
      html += `<div class="dt-msg-edit" id="message-editor" style="display:none;"><textarea id="message-input">${escapeHtml(task.message_body || '')}</textarea><div class="dt-msg-edit-actions"><button class="btn btn-primary" onclick="saveMessage()">Save</button><button class="btn" onclick="editMessage()">Cancel</button></div></div>`;
      html += `</div>`;
    }

    // Jira draft panel (when agent has drafted a ticket)
    const hasJiraDraft = task.body && task.body.includes('<!-- JIRA_DRAFT -->');
    if (hasJiraDraft) {
      const jiraDraft = parseJiraDraft(task.body);
      if (jiraDraft) {
        const featureFieldLabel = jiraDraft.type === 'Feature' ? 'Feature' : 'Epic';
        html += `<div class="dt-section">`;
        html += `<div class="dt-sec-head"><div style="display:flex;align-items:baseline;gap:9px;flex-wrap:wrap;"><span class="dt-sec-title">Jira draft</span><span class="dt-sec-hint">${escapeHtml(jiraDraft.type)}</span></div></div>`;
        html += `<div class="dt-prose" style="font-weight:600;margin-bottom:8px;">${escapeHtml(jiraDraft.summary)}</div>`;
        if (jiraDraft.description) html += `<div class="dt-prose dim" style="margin-bottom:13px;">${escapeHtml(jiraDraft.description)}</div>`;
        const meta = [];
        if (jiraDraft.parent) meta.push(['Parent', jiraDraft.parent]);
        if (jiraDraft.priority) meta.push(['Priority', jiraDraft.priority]);
        if (jiraDraft.labels.length) meta.push(['Labels', jiraDraft.labels.join(', ')]);
        if (jiraDraft.release_notes) meta.push(['Release', jiraDraft.release_notes]);
        if (jiraDraft.feature_name) meta.push([featureFieldLabel, jiraDraft.feature_name]);
        if (jiraDraft.gtm_date) meta.push(['GTM', jiraDraft.gtm_date]);
        if (jiraDraft.client_commitment) meta.push(['Commit', jiraDraft.client_commitment]);
        if (meta.length) {
          html += `<div class="dt-summary">`;
          meta.forEach(([k, v]) => html += `<div class="dt-sum-item"><span class="dt-sum-k">${k}</span><span class="dt-sum-v">${escapeHtml(v)}</span></div>`);
          html += `</div>`;
        }
        html += `<div class="dt-sec-hint" style="margin-top:11px;">Project VNT · Vantaca HXP · Board AI DLC (1096) · Refinement</div>`;
        html += `</div>`;
      }
    }

    // ── Details — the demoted metadata, parked next to the pipeline ──
    html += `<div class="dt-section">`;
    html += `<div class="dt-sec-head"><span class="dt-sec-title">Details</span></div>`;
    html += `<div class="dt-summary">`;
    const sum = [
      ['Priority', task.priority || '—'],
      ['Domain', task.domain || '—'],
      ['Assignee', task.assignee || '—'],
      ['Source', taskSource(task)],
      ['Project', task.project || '—'],
    ];
    if (task.due) sum.push(['Due', task.due]);
    sum.push(['Created', formatDate(task.created)]);
    if (task.waiting_on) { sum.push(['Waiting on', task.waiting_on]); sum.push(['Expected', task.waiting_expected || '—']); }
    sum.forEach(([k, v]) => html += `<div class="dt-sum-item"><span class="dt-sum-k">${k}</span><span class="dt-sum-v">${escapeHtml(String(v))}</span></div>`);
    html += `</div></div>`;

    // ── Pipeline (evals) — filled async into this slot ─────────────────
    html += `<div class="dt-section" id="pipeline-slot"></div>`;

    // ── Activity + comments — one calm thread, no left bars ───────────
    html += `<div class="dt-section">`;
    html += `<div class="dt-sec-head"><span class="dt-sec-title">Activity</span></div>`;
    if (task.activity_log && task.activity_log.length > 0) {
      html += `<div class="dt-thread">`;
      task.activity_log.forEach(e => {
        const kind = e.type || 'comment';
        html += `<div class="dt-event ev-${kind}"><span class="dt-ev-dot"></span><div><div class="dt-ev-meta"><span class="dt-ev-actor">${escapeHtml(e.actor)}</span><span>${formatDate(e.timestamp)}</span>${e.type ? `<span class="dt-ev-kind">${e.type.replace(/-/g, ' ')}</span>` : ''}</div><div class="dt-ev-body">${escapeHtml(e.content)}</div></div></div>`;
      });
      html += `</div>`;
    } else {
      html += `<div class="dt-prose dim" style="font-size:12.5px;">Nothing logged yet.</div>`;
    }
    html += `<div class="dt-composer"><textarea class="comment-input" id="comment-input" placeholder="Leave a note for your agent — or yourself…"></textarea><div class="dt-composer-actions"><button class="btn btn-quiet" id="dt-comment-btn" onclick="addComment()">Add comment</button></div></div>`;
    html += `</div>`;

    modalBody.innerHTML = html;
    // Always open at the top — never inherit the last card's scroll position.
    modalBody.scrollTop = 0;
    overlay.scrollTop = 0;

    // Load pipeline traces (async, appends to modal)
    // Show for all tasks — task-creation traces exist for every task,
    // not just agent-dispatched ones
    loadPipelineTraces(task.id).then(traces => {
      const slot = document.getElementById('pipeline-slot');
      if (!slot) return;
      if (traces.length > 0) slot.innerHTML = renderPipeline(traces, task.id);
      else slot.remove();
    });

    // Set up attendee typeahead if this is a schedule-meeting task
    // (emailCache already loaded above during chip rendering)
    if (isScheduleMeeting) {
      setupAttendeeTypeahead();
    }

    // Actions — regrouped by job. The output opens from the panel up top,
    // so it's gone from here. Left = utilities (incl. rerun, moved aside);
    // right = the one act you came to do.
    const doneLabel = isAgentComplete ? 'Approve & archive' : 'Mark done';
    const canDispatch = (task.status === 'open' || (task.status === 'blocked' && task.agent_status === 'failed'))
                        && (task.queue === 'collab' || task.queue === 'agent');
    const canRerun = (task.queue === 'agent' || task.queue === 'collab')
                     && (task.agent_status === 'failed' || task.agent_status === 'complete' || task.status === 'blocked');
    const hasSlots = isScheduleMeeting && task.body && parseSlots(task.body).length > 0;
    const canSendMessage = task.task_type === 'send-message' && (task.agent_status === 'complete' || task.agent_status === 'needs-human');

    let leftHtml = `<button class="btn btn-quiet" onclick="closeModal()">Close</button>`;
    if (canRerun) leftHtml += `<button class="btn btn-quiet" id="btn-rerun-agent" onclick="rerunAgent('${task.id}')">Rerun agent</button>`;

    let rightHtml = '';
    if (canDispatch) rightHtml += `<button class="btn btn-schedule" id="btn-start-agent" onclick="startAgent('${task.id}')">Start agent</button>`;
    if (hasSlots) rightHtml += `<button class="btn btn-schedule" id="btn-create-meeting" onclick="scheduleMeeting('${task.id}')" disabled>Create meeting</button>`;
    if (hasJiraDraft && (task.agent_status === 'complete' || task.agent_status === 'needs-human')) rightHtml += `<button class="btn btn-schedule" id="btn-publish-jira" onclick="publishToJira('${task.id}')">Publish to Jira</button>`;
    if (canSendMessage) rightHtml += `<button class="btn btn-schedule" id="btn-send-message" onclick="sendMessage('${task.id}')">${svgIcon('send')}Send message</button>`;
    // Both approvals sit together on the right
    if (isAgentComplete && task.agent_output) rightHtml += `<button class="btn btn-danger" id="btn-done-delete" onclick="markDoneAndDelete()">Approve & delete</button>`;
    rightHtml += `<button class="btn btn-success" onclick="markDone()">${doneLabel}</button>`;

    modalActions.innerHTML = `<div class="dt-foot-left">${leftHtml}</div><div class="dt-foot-right">${rightHtml}</div>`;
  } catch (err) {
    modalBody.innerHTML = `<div class="loading">Error: ${err.message}</div>`;
  }
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('active');
  currentTaskId = null;
}

async function markDone() {
  if (!currentTaskId) return;

  try {
    const res = await fetch(`${API}/tasks/${currentTaskId}/done`, { method: 'POST' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    closeModal();
    fetchTasks();
  } catch (err) {
    toast(`Error: ${err.message}`);
  }
}

async function markDoneAndDelete() {
  if (!currentTaskId) return;
  const ok = await confirmAction({
    title: 'Approve & delete?',
    message: 'This approves the task and permanently removes it from the board. This can’t be undone.',
    confirmLabel: 'Approve & delete',
    danger: true,
  });
  if (!ok) return;
  try {
    const res = await fetch(`${API}/tasks/${currentTaskId}/done-and-delete`, { method: 'POST' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    closeModal();
    fetchTasks();
  } catch (err) {
    toast(`Error: ${err.message}`);
  }
}

async function addComment() {
  if (!currentTaskId) return;
  const input = document.getElementById('comment-input');
  const content = input.value.trim();
  if (!content) return;

  try {
    const res = await fetch(`${API}/tasks/${currentTaskId}/comment`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    openTask(currentTaskId); // refresh modal
  } catch (err) {
    toast(`Error: ${err.message}`);
  }
}

// ─── Start Agent ─────────────────────────────────────────────────────

async function startAgent(taskId) {
  const btn = document.getElementById('btn-start-agent');
  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Dispatching…';
  }

  try {
    const res = await fetch(`${API}/tasks/${taskId}/dispatch`, { method: 'POST' });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || `HTTP ${res.status}`);
    }
    // Refresh modal to show in-progress state
    if (btn) btn.textContent = 'Agent started';
    setTimeout(() => { if (currentTaskId === taskId) openTask(taskId); fetchTasks(); }, 2000);
  } catch (err) {
    toast(`Error dispatching agent: ${err.message}`);
    if (btn) {
      btn.disabled = false;
      btn.textContent = 'Start agent';
    }
  }
}

// ─── Rerun Agent ─────────────────────────────────────────────────────

async function rerunAgent(taskId) {
  const ok = await confirmAction({
    title: 'Rerun this agent?',
    message: 'The current output will be discarded and the agent will start over from the task brief.',
    confirmLabel: 'Rerun agent',
  });
  if (!ok) return;
  const btn = document.getElementById('btn-rerun-agent');
  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Rerunning…';
  }

  try {
    const res = await fetch(`${API}/tasks/${taskId}/rerun`, { method: 'POST' });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || `HTTP ${res.status}`);
    }
    if (btn) btn.textContent = 'Agent restarted';
    setTimeout(() => { if (currentTaskId === taskId) openTask(taskId); fetchTasks(); }, 2000);
  } catch (err) {
    toast(`Error rerunning agent: ${err.message}`);
    if (btn) {
      btn.disabled = false;
      btn.textContent = 'Rerun agent';
    }
  }
}

// ─── Schedule Meeting ────────────────────────────────────────────────

function parseSlots(body) {
  // Extract <!-- SLOT:N|startISO|endISO --> comments + the display line that follows
  const slotRegex = /<!--\s*SLOT:(\d+)\|([^|]+)\|([^>]+?)\s*-->\s*\n(.+)/g;
  const slots = [];
  let match;
  while ((match = slotRegex.exec(body)) !== null) {
    slots.push({
      num: parseInt(match[1]),
      start: match[2].trim(),
      end: match[3].trim(),
      display: match[4].replace(/\*\*/g, '').replace(/_/g, '').trim(),
    });
  }
  return slots;
}

function selectSlot(el, index) {
  // Deselect all
  document.querySelectorAll('.dt-slot').forEach(s => s.classList.remove('selected'));
  // Select this one
  el.classList.add('selected');
  el.querySelector('input[type="radio"]').checked = true;
  // Enable the create meeting button
  const btn = document.getElementById('btn-create-meeting');
  if (btn) btn.disabled = false;
}

async function scheduleMeeting(taskId) {
  const selected = document.querySelector('.dt-slot.selected input[type="radio"]');
  if (!selected) {
    toast('Please select a time slot first.', 'warn');
    return;
  }

  const slotStart = selected.dataset.start;
  const slotEnd = selected.dataset.end;

  const btn = document.getElementById('btn-create-meeting');
  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Creating…';
  }

  // Gather current attendees from chips
  const attendeeEmails = getCurrentAttendees();
  // Gather recurrence setting
  const recurringCheck = document.getElementById('recurring-check');
  const recurringPattern = document.getElementById('recurring-pattern');
  const postBody = { slot_start: slotStart, slot_end: slotEnd };
  if (attendeeEmails.length > 0) {
    postBody.attendees = attendeeEmails;
  }
  if (recurringCheck && recurringCheck.checked && recurringPattern) {
    postBody.recurring = recurringPattern.value;
  }
  // Include meeting title and description (from edit input if active, else display span)
  const titleInput = document.getElementById('meeting-title-input');
  const titleDisplay = document.getElementById('meeting-title-display');
  const titleVal = titleInput ? titleInput.value.trim() : (titleDisplay ? titleDisplay.textContent.trim() : '');
  if (titleVal) postBody.meeting_title = titleVal;

  const descInput = document.getElementById('meeting-desc-input');
  const descDisplay = document.getElementById('meeting-desc-display');
  const descVal = descInput ? descInput.value.trim() : (descDisplay ? descDisplay.textContent.trim() : '');
  if (descVal) postBody.meeting_description = descVal;

  try {
    const res = await fetch(`${API}/tasks/${taskId}/schedule-meeting`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(postBody),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || `HTTP ${res.status}`);
    }
    closeModal();
    fetchTasks();
  } catch (err) {
    toast(`Error creating meeting: ${err.message}`);
    if (btn) {
      btn.disabled = false;
      btn.textContent = 'Create meeting';
    }
  }
}

// ─── Send Message ────────────────────────────────────────────────────

function editMessage() {
  const display = document.getElementById('message-display');
  const editor = document.getElementById('message-editor');
  const btn = document.getElementById('btn-edit-message');
  if (!editor) return;
  const editing = editor.style.display !== 'none';
  editor.style.display = editing ? 'none' : 'block';
  if (display) display.style.display = editing ? '' : 'none';
  if (btn) btn.style.display = editing ? '' : 'none';
  if (!editing) { const ta = document.getElementById('message-input'); if (ta) ta.focus(); }
}

async function saveMessage() {
  if (!currentTaskId) return;
  const input = document.getElementById('message-input');
  const message_body = input.value.trim();
  try {
    const res = await fetch(`${API}/tasks/${currentTaskId}/message`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message_body }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const bodyEl = document.getElementById('message-body-text');
    if (bodyEl) bodyEl.textContent = message_body;
    editMessage();
    toast('Message updated.', 'success');
  } catch (err) {
    toast(`Could not save message: ${err.message}`);
  }
}

async function sendMessage(taskId) {
  const btn = document.getElementById('btn-send-message');
  if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
  try {
    const res = await fetch(`${API}/tasks/${taskId}/send-message`, { method: 'POST' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    toast('Message sent.', 'success');
    closeModal();
    fetchTasks();
  } catch (err) {
    toast(`Could not send: ${err.message}`);
    if (btn) { btn.disabled = false; btn.textContent = 'Send message'; }
  }
}

// ─── Meeting Details Edit/Save ───────────────────────────────────────

function editMeetingDetails() {
  const btn = document.getElementById('btn-edit-meeting');
  const titleEl = document.getElementById('meeting-title-display');
  const descEl = document.getElementById('meeting-desc-display');

  if (titleEl) {
    const val = titleEl.textContent;
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'field-input';
    input.id = 'meeting-title-input';
    input.value = val;
    titleEl.replaceWith(input);
  }
  if (descEl) {
    const val = descEl.textContent;
    const textarea = document.createElement('textarea');
    textarea.className = 'field-input';
    textarea.id = 'meeting-desc-input';
    textarea.rows = 3;
    textarea.value = val;
    descEl.replaceWith(textarea);
  }
  btn.textContent = 'Save';
  btn.onclick = () => saveMeetingDetails(currentTaskId);
}

async function saveMeetingDetails(taskId) {
  const btn = document.getElementById('btn-edit-meeting');
  const titleInput = document.getElementById('meeting-title-input');
  const descInput = document.getElementById('meeting-desc-input');

  const body = {};
  if (titleInput) body.meeting_title = titleInput.value.trim();
  if (descInput) body.meeting_description = descInput.value.trim();

  btn.textContent = 'Saving...';
  btn.disabled = true;

  try {
    const res = await fetch(`${API}/tasks/${taskId}/meeting-details`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || `HTTP ${res.status}`);
    }

    // Swap back to read-only spans
    if (titleInput) {
      const span = document.createElement('span');
      span.className = 'field-value';
      span.id = 'meeting-title-display';
      span.textContent = body.meeting_title;
      titleInput.replaceWith(span);
    }
    if (descInput) {
      const span = document.createElement('span');
      span.className = 'field-value';
      span.id = 'meeting-desc-display';
      span.style.whiteSpace = 'pre-wrap';
      span.textContent = body.meeting_description;
      descInput.replaceWith(span);
    }
    btn.textContent = 'Edit';
    btn.onclick = editMeetingDetails;
  } catch (err) {
    toast(`Failed to save: ${err.message}`);
    btn.textContent = 'Save';
  } finally {
    btn.disabled = false;
  }
}

// ─── Attendee Management ─────────────────────────────────────────────

async function loadEmailCache() {
  if (emailCache !== null) return;
  try {
    const res = await fetch(`${API}/people/emails`);
    if (res.ok) emailCache = await res.json();
    else emailCache = {};
  } catch { emailCache = {}; }
}

function getCurrentAttendees() {
  const chips = document.querySelectorAll('#attendee-chips .dt-att');
  return Array.from(chips).map(c => c.dataset.email).filter(Boolean);
}

function removeAttendee(el) {
  el.closest('.dt-att').remove();
}

function addAttendeeChip(email) {
  if (!email) return;
  // Prevent duplicates
  const existing = getCurrentAttendees();
  if (existing.includes(email)) return;
  const container = document.getElementById('attendee-chips');
  const row = document.createElement('div');
  row.className = 'dt-att';
  row.dataset.email = email;
  const initial = (email[0] || '?').toUpperCase();
  row.innerHTML = `<span class="dt-att-avatar">${initial}</span><span class="dt-att-main"><span class="dt-att-name">${escapeHtml(email)}</span></span><span class="dt-att-remove" onclick="removeAttendee(this)">&times;</span>`;
  container.appendChild(row);
}

function setupAttendeeTypeahead() {
  const input = document.getElementById('attendee-input');
  const dropdown = document.getElementById('attendee-dropdown');
  if (!input || !dropdown) return;

  input.addEventListener('input', () => {
    const query = input.value.trim().toLowerCase();
    if (query.length < 1 || !emailCache) {
      dropdown.classList.remove('visible');
      return;
    }
    const matches = Object.entries(emailCache)
      .filter(([name, email]) => email && (name.toLowerCase().includes(query) || email.toLowerCase().includes(query)))
      // Deduplicate by email
      .reduce((acc, [name, email]) => {
        if (!acc.some(m => m[1] === email)) acc.push([name, email]);
        return acc;
      }, [])
      .slice(0, 8);

    if (matches.length === 0) {
      dropdown.classList.remove('visible');
      return;
    }
    dropdown.innerHTML = matches.map(([name, email]) =>
      `<div class="attendee-dropdown-item" onclick="selectAttendee('${escapeHtml(email)}')">${escapeHtml(name)}<span class="email-hint">${escapeHtml(email)}</span></div>`
    ).join('');
    dropdown.classList.add('visible');
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const val = input.value.trim();
      if (val.includes('@')) {
        addAttendeeChip(val);
        input.value = '';
        dropdown.classList.remove('visible');
      } else if (emailCache && emailCache[val]) {
        addAttendeeChip(emailCache[val]);
        input.value = '';
        dropdown.classList.remove('visible');
      }
    }
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.attendee-add-wrap')) {
      dropdown.classList.remove('visible');
    }
  });
}

function selectAttendee(email) {
  addAttendeeChip(email);
  const input = document.getElementById('attendee-input');
  const dropdown = document.getElementById('attendee-dropdown');
  if (input) input.value = '';
  if (dropdown) dropdown.classList.remove('visible');
}

// ─── Recurring Toggle ────────────────────────────────────────────────

function toggleRecurring() {
  const check = document.getElementById('recurring-check');
  const select = document.getElementById('recurring-pattern');
  if (select) select.style.display = check.checked ? '' : 'none';
}

function updateRecurrencePattern() {
  // Value is read directly from the select when scheduling
}

// ─── Description Editing ─────────────────────────────────────────────

function toggleDescEdit() {
  const display = document.getElementById('desc-display');
  const editor = document.getElementById('desc-editor');
  const btn = document.getElementById('desc-edit-btn');
  if (editor.style.display === 'none') {
    editor.style.display = 'block';
    display.style.display = 'none';
    btn.style.display = 'none';
    document.getElementById('desc-input').focus();
  } else {
    editor.style.display = 'none';
    display.style.display = 'block';
    btn.style.display = '';
  }
}

async function saveDescription() {
  if (!currentTaskId) return;
  const input = document.getElementById('desc-input');
  const description = input.value.trim();
  if (!description) return;

  try {
    const res = await fetch(`${API}/tasks/${currentTaskId}/description`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    openTask(currentTaskId); // refresh modal
    fetchTasks(); // refresh board in background
  } catch (err) {
    toast(`Error saving description: ${err.message}`);
  }
}

// ─── Pipeline (Per-Step Scoring) ────────────────────────────────────

async function loadPipelineTraces(taskId) {
  try {
    const res = await fetch(`${API}/tasks/${taskId}/traces`);
    const data = await res.json();
    return data.traces || [];
  } catch {
    return [];
  }
}

function renderPipeline(traces, taskId) {
  if (!traces || traces.length === 0) return '';

  const FRIENDLY = {
    'task-parser':      'Task parser',
    'worker-match':     'Worker match',
    'worker-execution': 'Worker execution',
  };
  const upSvg = `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="7" width="2.6" height="6" rx="0.7"/><path d="M5.6 7.4 8 2.6c1 0 1.7.8 1.7 1.8V6h2.6c.7 0 1.2.64 1.04 1.3l-.92 3.9c-.12.5-.58.85-1.1.85H5.6z"/></svg>`;
  const downSvg = `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><rect x="10.4" y="3" width="2.6" height="6" rx="0.7"/><path d="M10.4 8.6 8 13.4c-1 0-1.7-.8-1.7-1.8V10H3.7c-.7 0-1.2-.64-1.04-1.3l.92-3.9c.12-.5.58-.85 1.1-.85H10.4z"/></svg>`;
  const noteSvg = `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M3 4.4h10v6H7.2L4.6 12.6V10.4H3z"/></svg>`;
  const judgeSvg = `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2.4v11.2M4.4 4h7.2M3.2 13.2h9.6"/><path d="M4.4 4 2.4 8.2a2 2 0 0 0 4 0L4.4 4ZM11.6 4 9.6 8.2a2 2 0 0 0 4 0L11.6 4Z"/></svg>`;

  let html = '<div class="dt-sec-head"><span class="dt-sec-title">How it ran</span></div>';
  html += '<div class="dt-pipe">';

  traces.forEach((t, i) => {
    const name = t.name || '';
    let key = 'worker-execution';
    if (name.includes('task-parser')) key = 'task-parser';
    else if (name.includes('worker-match')) key = 'worker-match';
    const label = FRIENDLY[key] || name;

    const thumbUp = t.scores && t.scores.find(s => s.name === 'human-feedback' && s.value === 1);
    const thumbDown = t.scores && t.scores.find(s => s.name === 'human-feedback' && s.value === 0);
    const isError = String(t.output_summary || '').toLowerCase().includes('error');
    let stClass = '';
    if (thumbUp) stClass = 'st-good';
    else if (thumbDown || isError) stClass = 'st-bad';

    html += `<div class="dt-step ${stClass}">`;
    html += `<div class="dt-step-head"><span class="dt-step-dot"></span><span class="dt-step-name">${label}</span>`;
    html += `<span class="dt-step-rate">`;
    html += `<button class="dt-rate-btn ${thumbUp ? 'on-up' : ''}" onclick="scoreStep('${taskId}','${t.trace_id}',1,this)" title="Looks right">${upSvg}</button>`;
    html += `<button class="dt-rate-btn ${thumbDown ? 'on-down' : ''}" onclick="scoreStep('${taskId}','${t.trace_id}',0,this)" title="Not right">${downSvg}</button>`;
    html += `<button class="dt-rate-btn dt-rate-note" onclick="toggleAnnotation('annot-${i}')" title="Add a note">${noteSvg}Note</button>`;
    html += `</span></div>`;

    if (t.output_summary && t.output_summary !== 'null') html += `<div class="dt-step-out">${escapeHtml(String(t.output_summary))}</div>`;

    // Saved notes — attribute by author. The LLM judge writes evaluation
    // scores with reasoning comments onto these traces; only genuine human
    // annotations are "your note". Everything else is the judge's rationale.
    (t.scores || []).filter(s => s.comment).forEach(s => {
      const src = String(s.source || '').toUpperCase();
      const isHuman = s.name === 'human-feedback' || s.name === 'human' || src === 'ANNOTATION';
      if (isHuman) {
        html += `<div class="dt-saved-note mine"><span class="who">Your note</span>${escapeHtml(s.comment)}</div>`;
      } else {
        const verdict = (s.value != null) ? ` · ${s.value}/10` : '';
        html += `<div class="dt-saved-note judge"><span class="who">${judgeSvg}Judge${verdict}</span>${escapeHtml(s.comment)}</div>`;
      }
    });

    html += `<div class="dt-anno" id="annot-${i}"><textarea id="annot-input-${i}" placeholder="What was off — or what to keep doing?"></textarea><div class="dt-anno-actions"><button class="btn btn-quiet" onclick="submitAnnotation('${taskId}','${t.trace_id}','annot-input-${i}')">Save note</button><button class="btn btn-quiet" onclick="toggleAnnotation('annot-${i}')">Cancel</button></div></div>`;

    html += `</div>`;
  });

  html += '</div>';
  html += `<a class="dt-pipe-link" href="${LANGFUSE_HOST}/project/pm-os/sessions/${taskId}" target="_blank">${svgIcon('output')}Full trace in LangFuse</a>`;
  return html;
}

async function scoreStep(taskId, traceId, score, btn) {
  try {
    await fetch(`${API}/tasks/${taskId}/traces/${traceId}/score`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ score }),
    });
    // Visual feedback — light up the chosen thumb, settle the step's dot
    const parent = btn.parentElement;
    parent.querySelectorAll('.dt-rate-btn').forEach(b => b.classList.remove('on-up', 'on-down'));
    btn.classList.add(score === 1 ? 'on-up' : 'on-down');
    const step = btn.closest('.dt-step');
    if (step) { step.classList.remove('st-good', 'st-bad'); step.classList.add(score === 1 ? 'st-good' : 'st-bad'); }
  } catch (err) {
    console.error('Score failed:', err);
  }
}

function toggleAnnotation(id) {
  const box = document.getElementById(id);
  if (!box) return;
  box.classList.toggle('open');
  const ta = box.querySelector('textarea');
  if (ta && box.classList.contains('open')) ta.focus();
}

async function submitAnnotation(taskId, traceId, inputId) {
  const input = document.getElementById(inputId);
  const comment = input.value.trim();
  if (!comment) return;
  try {
    await fetch(`${API}/tasks/${taskId}/traces/${traceId}/annotation`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ comment }),
    });
    // Show the saved note inline (feels real without a round-trip refresh)
    const box = input.closest('.dt-anno');
    const note = document.createElement('div');
    note.className = 'dt-saved-note mine';
    note.innerHTML = `<span class="who">Your note</span>${escapeHtml(comment)}`;
    box.parentNode.insertBefore(note, box);
    input.value = '';
    box.classList.remove('open');
    toast('Note saved.', 'success');
  } catch (err) {
    console.error('Annotation failed:', err);
  }
}

// ─── Jira Draft ────────────────────────────────────────────────────

function parseJiraDraft(body) {
  if (!body || !body.includes('<!-- JIRA_DRAFT -->')) return null;
  const block = body.match(/<!-- JIRA_DRAFT -->([\s\S]+?)<!-- \/JIRA_DRAFT -->/);
  if (!block) return null;
  const b = block[1];
  const field = (name) => { const m = b.match(new RegExp(`<!-- ${name}:(.+?) -->`)); return m ? m[1].trim() : ''; };
  const descMatch = b.match(/### Description\s*\n([\s\S]*?)(?=\n### |\n<!-- \/JIRA_DRAFT)/);
  const featureName = field('JIRA_FEATURE_NAME') || field('JIRA_EPIC_NAME') || '';
  return {
    type: field('JIRA_TYPE') || 'Bug',
    summary: field('JIRA_SUMMARY') || '',
    priority: field('JIRA_PRIORITY') || '',
    labels: field('JIRA_LABELS').split(',').map(s => s.trim()).filter(Boolean),
    release_notes: field('JIRA_RELEASE_NOTES') || '',
    feature_name: featureName,
    epic_name: featureName,
    gtm_date: field('JIRA_GTM_DATE') || '',
    client_commitment: field('JIRA_CLIENT_COMMITMENT') || '',
    parent: field('JIRA_PARENT') || '',
    description: descMatch ? descMatch[1].trim() : '',
  };
}

async function publishToJira(taskId) {
  const ok = await confirmAction({
    title: 'Publish to Jira?',
    message: 'This creates a Jira issue from the current draft.',
    confirmLabel: 'Publish',
  });
  if (!ok) return;
  const btn = document.getElementById('btn-publish-jira');
  if (btn) { btn.disabled = true; btn.textContent = 'Publishing…'; }
  try {
    const res = await fetch(`${API}/tasks/${taskId}/publish-jira`, { method: 'POST' });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    fetchTasks();
    closeModal();
  } catch (err) {
    toast(`Publish failed: ${err.message}`);
    if (btn) { btn.disabled = false; btn.textContent = 'Publish to Jira'; }
  }
}
