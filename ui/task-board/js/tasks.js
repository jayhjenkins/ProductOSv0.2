// tasks.js — Task-detail modal + all task action verbs
// Extracted from index.html inline script (Task 0.2). Depends on globals from core.js
// (API, LANGFUSE_HOST, allTasks, currentTaskId, emailCache, escapeHtml, formatDate,
// toast, meetingName, obsidianUri, renderAgentOutput) and on board/cron functions
// (fetchTasks, etc.) that remain in the inline script — all resolved as globals at call time.

// ─── Modal ──────────────────────────────────────────────────────────

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

    modalTitle.textContent = `${task.id} — ${escapeHtml(task.title)}`;

    // Fields grid
    let html = '<div class="field-grid">';
    const fields = [
      ['Status', task.status],
      ['Queue', task.queue],
      ['Priority', task.priority],
      ['Domain', task.domain || '—'],
      ['Creator', task.creator],
      ['Assignee', task.assignee || '—'],
      ['Due', task.due || '—'],
      ['Project', task.project || '—'],
      ['Created', formatDate(task.created)],
      ['Updated', formatDate(task.updated)],
    ];
    if (task.source_meeting) {
      fields.push(['Source Meeting', meetingName(task.source_meeting)]);
    }
    if (task.agent_status) {
      fields.push(['Agent Status', task.agent_status]);
    }
    if (task.agent_output) {
      fields.push(['Agent Output', renderAgentOutput(task.agent_output), true]);
    }
    if (task.sharepoint_url) {
      const docName = task.sharepoint_path ? task.sharepoint_path.split('/').pop() : 'Open in Word Online';
      fields.push(['Word Doc', `<a href="${escapeHtml(task.sharepoint_url)}" target="_blank" rel="noopener" style="color:var(--accent);text-decoration:none;" title="Open in Word Online">${escapeHtml(docName)}</a>`, true]);
    } else if (task.sharepoint_path) {
      fields.push(['Word Doc', `<a href="/open?file=${encodeURIComponent(task.sharepoint_path)}" style="color:var(--accent);text-decoration:none;" title="Open in Word">${escapeHtml(task.sharepoint_path.split('/').pop())}</a>`, true]);
    }
    if (task.waiting_on) {
      fields.push(['Waiting On', task.waiting_on]);
      fields.push(['Expected', task.waiting_expected || '—']);
    }
    if (task.tags && task.tags.length > 0) {
      fields.push(['Tags', task.tags.join(', ')]);
    }

    fields.forEach(([label, value, raw]) => {
      const rendered = raw ? value : escapeHtml(String(value));
      html += `<div class="field-item"><span class="field-label">${label}</span><span class="field-value">${rendered}</span></div>`;
    });
    html += '</div>';

    // Determine task type flags early so all sections can use them
    const isScheduleMeeting = task.task_type === 'schedule-meeting';
    const isAgentComplete = task.agent_status === 'complete' && task.status === 'done';

    // Schedule-meeting info panel (above description and activity log)
    if (isScheduleMeeting) {
      // Pre-load email cache so we can resolve names → emails for chips
      await loadEmailCache();

      html += '<div class="section-title" style="display:flex;align-items:center;justify-content:space-between;">Meeting Details<button class="btn-edit-meeting" id="btn-edit-meeting" onclick="editMeetingDetails()">Edit</button></div>';
      html += '<div class="field-grid" style="margin-bottom:12px;">';
      if (task.meeting_title) {
        html += `<div class="field-item"><span class="field-label">Event Title</span><span class="field-value" id="meeting-title-display">${escapeHtml(task.meeting_title)}</span></div>`;
      }
      if (task.meeting_duration) {
        html += `<div class="field-item"><span class="field-label">Duration</span><span class="field-value">${task.meeting_duration} min</span></div>`;
      }
      // Editable attendees as chips — resolve names to emails via cache
      const attendees = task.meeting_attendees || [];
      html += `<div class="field-item" style="grid-column:1/-1;">`;
      html += `<span class="field-label">Attendees</span>`;
      html += `<div class="attendee-chips" id="attendee-chips">`;
      attendees.forEach(a => {
        const name = String(a);
        const email = (emailCache && emailCache[name]) || name;
        html += `<span class="attendee-chip" data-email="${escapeHtml(email)}">${escapeHtml(name)}<span class="chip-remove" onclick="removeAttendee(this)">&times;</span></span>`;
      });
      html += `</div>`;
      html += `<div class="attendee-add-wrap">`;
      html += `<input type="text" class="attendee-add-input" id="attendee-input" placeholder="Add attendee (name or email)..." autocomplete="off">`;
      html += `<div class="attendee-dropdown" id="attendee-dropdown"></div>`;
      html += `</div>`;
      html += `</div>`;
      if (task.meeting_description) {
        html += `<div class="field-item" style="grid-column:1/-1;"><span class="field-label">Description</span><span class="field-value" id="meeting-desc-display" style="white-space:pre-wrap;">${escapeHtml(task.meeting_description)}</span></div>`;
      }
      // Recurring meeting toggle
      const isRecurring = task.meeting_recurring || false;
      const recurrencePattern = task.meeting_recurrence_pattern || 'weekly';
      html += `<div class="field-item" style="grid-column:1/-1;">`;
      html += `<div class="recurring-toggle">`;
      html += `<label><input type="checkbox" id="recurring-check" ${isRecurring ? 'checked' : ''} onchange="toggleRecurring()"> Recurring meeting</label>`;
      html += `<select class="recurring-select" id="recurring-pattern" ${isRecurring ? '' : 'style="display:none;"'} onchange="updateRecurrencePattern()">`;
      html += `<option value="weekly" ${recurrencePattern === 'weekly' ? 'selected' : ''}>Weekly</option>`;
      html += `<option value="biweekly" ${recurrencePattern === 'biweekly' ? 'selected' : ''}>Biweekly</option>`;
      html += `<option value="monthly" ${recurrencePattern === 'monthly' ? 'selected' : ''}>Monthly</option>`;
      html += `</select>`;
      html += `</div>`;
      html += `</div>`;
      html += '</div>';
    }

    // Schedule-meeting slot picker (render whenever SLOT markers exist —
    // independent of agent_status so the picker shows even if the agent
    // ended in needs-human / open / blocked).
    if (isScheduleMeeting && task.body) {
      const slots = parseSlots(task.body);
      if (slots.length > 0) {
        html += '<div class="slot-picker">';
        html += '<div class="slot-picker-title">Select a Time Slot</div>';
        slots.forEach((slot, i) => {
          html += `<div class="slot-option" onclick="selectSlot(this, ${i})">`;
          html += `<input type="radio" name="slot" id="slot-${i}" value="${i}" data-start="${escapeHtml(slot.start)}" data-end="${escapeHtml(slot.end)}">`;
          html += `<label for="slot-${i}">${escapeHtml(slot.display)}</label>`;
          html += `</div>`;
        });
        html += '</div>';
      }
    }

    // Jira draft panel (when agent has drafted a ticket)
    const hasJiraDraft = task.body && task.body.includes('<!-- JIRA_DRAFT -->');
    if (hasJiraDraft) {
      const jiraDraft = parseJiraDraft(task.body);
      if (jiraDraft) {
        const typeBadgeColor = {
          'Feature': '#9f8fef',
          'Epic': '#9f8fef',
          'Unit': '#14b8a6',
          'Story': 'var(--success)',
          'Bug': 'var(--danger)',
          'Regression Defect': '#f59e0b',
          'Spike': 'var(--text-muted)',
          'Hotfix': '#dc2626',
          'Work Item Defect': '#f59e0b',
          'Performance Defect': '#f59e0b',
          'Security Defect': '#dc2626'
        }[jiraDraft.type] || 'var(--text-muted)';
        const featureFieldLabel = jiraDraft.type === 'Feature' ? 'Feature' : 'Epic';
        html += '<div style="background:var(--surface);border:1px solid var(--border);border-left:3px solid ' + typeBadgeColor + ';border-radius:8px;padding:14px;margin:12px 0;">';
        html += '<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">';
        html += `<span style="background:${typeBadgeColor};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;">${escapeHtml(jiraDraft.type)}</span>`;
        html += `<span style="font-weight:600;font-size:14px;">${escapeHtml(jiraDraft.summary)}</span>`;
        html += '</div>';
        if (jiraDraft.description) {
          html += `<div style="font-size:13px;color:var(--text-muted);white-space:pre-wrap;margin-bottom:10px;max-height:200px;overflow-y:auto;">${escapeHtml(jiraDraft.description)}</div>`;
        }
        html += '<div style="display:flex;gap:8px;flex-wrap:wrap;font-size:11px;">';
        if (jiraDraft.parent) html += `<span style="background:var(--surface-hover);padding:2px 6px;border-radius:3px;">Parent: ${escapeHtml(jiraDraft.parent)}</span>`;
        if (jiraDraft.priority) html += `<span style="background:var(--surface-hover);padding:2px 6px;border-radius:3px;">Priority: ${escapeHtml(jiraDraft.priority)}</span>`;
        if (jiraDraft.labels.length) html += `<span style="background:var(--surface-hover);padding:2px 6px;border-radius:3px;">Labels: ${escapeHtml(jiraDraft.labels.join(', '))}</span>`;
        if (jiraDraft.release_notes) html += `<span style="background:var(--surface-hover);padding:2px 6px;border-radius:3px;">Release: ${escapeHtml(jiraDraft.release_notes)}</span>`;
        if (jiraDraft.feature_name) html += `<span style="background:var(--surface-hover);padding:2px 6px;border-radius:3px;">${featureFieldLabel}: ${escapeHtml(jiraDraft.feature_name)}</span>`;
        if (jiraDraft.gtm_date) html += `<span style="background:var(--surface-hover);padding:2px 6px;border-radius:3px;">GTM: ${escapeHtml(jiraDraft.gtm_date)}</span>`;
        if (jiraDraft.client_commitment) html += `<span style="background:var(--surface-hover);padding:2px 6px;border-radius:3px;">Commit: ${escapeHtml(jiraDraft.client_commitment)}</span>`;
        html += '</div>';
        html += '<div style="margin-top:6px;font-size:11px;color:var(--text-dim);">Project: VNT &middot; Component: Vantaca HXP &middot; Board: AI DLC (1096) &middot; Status: Refinement</div>';
        html += '</div>';
      }
    }

    // Body sections (description, acceptance criteria)
    if (task.body) {
      const bodyText = task.body.trim();
      const sections = bodyText.split(/^## /m).filter(s => s.trim());
      sections.forEach(section => {
        const lines = section.split('\n');
        const title = lines[0].trim();
        const content = lines.slice(1).join('\n').trim();
        if (title.toLowerCase() === 'activity log') return;
        if (title.toLowerCase() === 'suggested times') return;
        if (title.toLowerCase() === 'jira draft') return;
        if (title.toLowerCase() === 'description') {
          html += `<div class="section-header"><span class="section-title" style="border:none;margin:0;padding-top:12px;">Description</span><button class="btn-edit" onclick="toggleDescEdit()" id="desc-edit-btn">Edit</button></div>`;
          html += `<div id="desc-display" class="section-content">${escapeHtml(content)}</div>`;
          html += `<div id="desc-editor" style="display:none;margin-top:8px;">`;
          html += `<textarea class="desc-textarea" id="desc-input">${escapeHtml(content)}</textarea>`;
          html += `<div class="desc-actions"><button class="btn btn-primary" onclick="saveDescription()">Save</button><button class="btn" onclick="toggleDescEdit()">Cancel</button></div>`;
          html += `</div>`;
        } else if (content) {
          html += `<div class="section-title">${escapeHtml(title)}</div>`;
          html += `<div class="section-content">${escapeHtml(content)}</div>`;
        }
      });
    }

    // Activity log
    if (task.activity_log && task.activity_log.length > 0) {
      html += '<div class="section-title">Activity Log</div>';
      html += '<div class="activity-log">';
      task.activity_log.forEach(entry => {
        const typeClass = entry.type || '';
        html += `<div class="log-entry ${typeClass}">`;
        html += `<div class="log-meta">${formatDate(entry.timestamp)} — ${entry.actor}${entry.type ? ` [${entry.type}]` : ''}</div>`;
        html += `<div class="log-content">${escapeHtml(entry.content)}</div>`;
        html += `</div>`;
      });
      html += '</div>';
    }

    // Comment box
    html += `
      <div class="comment-box">
        <textarea class="comment-input" id="comment-input" placeholder="Add a comment..."></textarea>
      </div>
    `;

    modalBody.innerHTML = html;

    // Load pipeline traces (async, appends to modal)
    // Show for all tasks — task-creation traces exist for every task,
    // not just agent-dispatched ones
    loadPipelineTraces(task.id).then(traces => {
      if (traces.length > 0) {
        const pipelineHtml = renderPipeline(traces, task.id);
        const pipelineDiv = document.createElement('div');
        pipelineDiv.innerHTML = pipelineHtml;
        modalBody.appendChild(pipelineDiv);
      }
    });

    // Set up attendee typeahead if this is a schedule-meeting task
    // (emailCache already loaded above during chip rendering)
    if (isScheduleMeeting) {
      setupAttendeeTypeahead();
    }

    // Actions — context-sensitive buttons
    const doneLabel = isAgentComplete ? 'Approve & Archive' : 'Mark Done';
    const canDispatch = (task.status === 'open' || (task.status === 'blocked' && task.agent_status === 'failed'))
                        && (task.queue === 'collab' || task.queue === 'agent');
    const canRerun = (task.queue === 'agent' || task.queue === 'collab')
                     && (task.agent_status === 'failed' || task.agent_status === 'complete' || task.status === 'blocked');
    let actionsHtml = '';
    if (canDispatch) {
      actionsHtml += `<button class="btn btn-schedule" id="btn-start-agent" onclick="startAgent('${task.id}')">Start Agent</button>`;
    }
    if (canRerun) {
      actionsHtml += `<button class="btn btn-warning" id="btn-rerun-agent" onclick="rerunAgent('${task.id}')">Rerun Agent</button>`;
    }
    actionsHtml += `<button class="btn btn-primary" onclick="addComment()">Add Comment</button>`;
    // Show "Create Meeting" whenever the picker is shown (i.e., SLOT markers exist).
    // Picker visibility is gated only on parsed slot count, not agent_status.
    const hasSlots = isScheduleMeeting && task.body && parseSlots(task.body).length > 0;
    if (hasSlots) {
      actionsHtml += `<button class="btn btn-schedule" id="btn-create-meeting" onclick="scheduleMeeting('${task.id}')" disabled>Create Meeting</button>`;
    }
    if (hasJiraDraft && (task.agent_status === 'complete' || task.agent_status === 'needs-human')) {
      actionsHtml += `<button class="btn btn-schedule" id="btn-publish-jira" onclick="publishToJira('${task.id}')">Publish to Jira</button>`;
    }
    if (isAgentComplete && task.agent_output) {
      const out = task.agent_output.trim();
      if (out.endsWith('.md')) {
        actionsHtml += `<a href="${obsidianUri(out)}" class="btn" title="Open in Obsidian">Open Output</a>`;
      } else {
        const urlMatch = out.match(/https?:\/\/[^\s)]+/);
        if (urlMatch) {
          actionsHtml += `<a href="${escapeHtml(urlMatch[0])}" target="_blank" rel="noopener" class="btn">Open Link</a>`;
        }
      }
    }
    if (task.sharepoint_url) {
      actionsHtml += `<a href="${escapeHtml(task.sharepoint_url)}" target="_blank" rel="noopener" class="btn" title="Open in Word Online">Open in Word</a>`;
    } else if (task.sharepoint_path) {
      actionsHtml += `<a href="/open?file=${encodeURIComponent(task.sharepoint_path)}" class="btn" title="Open in Microsoft Word">Open in Word</a>`;
    }
    actionsHtml += `<button class="btn btn-success" onclick="markDone()">${doneLabel}</button>`;
    if (isAgentComplete && task.agent_output) {
      actionsHtml += `<button class="btn btn-danger" id="btn-done-delete" onclick="markDoneAndDelete()">Approve & Delete</button>`;
    }
    actionsHtml += `<button class="btn" onclick="closeModal()">Close</button>`;
    modalActions.innerHTML = actionsHtml;
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
  const btn = document.getElementById('btn-done-delete');
  if (btn && !btn.dataset.armed) {
    btn.dataset.armed = 'true';
    btn.textContent = 'Click again to confirm delete';
    btn.classList.add('btn-danger');
    setTimeout(() => { if (btn && btn.dataset.armed) { delete btn.dataset.armed; btn.textContent = 'Done & Delete'; btn.classList.remove('btn-danger'); } }, 3000);
    return;
  }
  if (btn) delete btn.dataset.armed;
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
    btn.textContent = 'Dispatching...';
  }

  try {
    const res = await fetch(`${API}/tasks/${taskId}/dispatch`, { method: 'POST' });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || `HTTP ${res.status}`);
    }
    // Refresh modal to show in-progress state
    if (btn) btn.textContent = 'Agent Started';
    setTimeout(() => { if (currentTaskId === taskId) openTask(taskId); fetchTasks(); }, 2000);
  } catch (err) {
    toast(`Error dispatching agent: ${err.message}`);
    if (btn) {
      btn.disabled = false;
      btn.textContent = 'Start Agent';
    }
  }
}

// ─── Rerun Agent ─────────────────────────────────────────────────────

async function rerunAgent(taskId) {
  const btn = document.getElementById('btn-rerun-agent');
  // Two-click confirm: first click arms, second click fires
  if (btn && !btn.dataset.armed) {
    btn.dataset.armed = 'true';
    btn.textContent = 'Click again to confirm';
    btn.classList.add('btn-danger');
    setTimeout(() => { if (btn.dataset.armed) { delete btn.dataset.armed; btn.textContent = 'Rerun Agent'; btn.classList.remove('btn-danger'); } }, 3000);
    return;
  }
  if (btn) {
    delete btn.dataset.armed;
    btn.disabled = true;
    btn.textContent = 'Rerunning...';
  }

  try {
    const res = await fetch(`${API}/tasks/${taskId}/rerun`, { method: 'POST' });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || `HTTP ${res.status}`);
    }
    if (btn) btn.textContent = 'Agent Restarted';
    setTimeout(() => { if (currentTaskId === taskId) openTask(taskId); fetchTasks(); }, 2000);
  } catch (err) {
    toast(`Error rerunning agent: ${err.message}`);
    if (btn) {
      btn.disabled = false;
      btn.textContent = 'Rerun Agent';
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
  document.querySelectorAll('.slot-option').forEach(s => s.classList.remove('selected'));
  // Select this one
  el.classList.add('selected');
  el.querySelector('input[type="radio"]').checked = true;
  // Enable the create meeting button
  const btn = document.getElementById('btn-create-meeting');
  if (btn) btn.disabled = false;
}

async function scheduleMeeting(taskId) {
  const selected = document.querySelector('.slot-option.selected input[type="radio"]');
  if (!selected) {
    toast('Please select a time slot first.', 'warn');
    return;
  }

  const slotStart = selected.dataset.start;
  const slotEnd = selected.dataset.end;

  const btn = document.getElementById('btn-create-meeting');
  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Creating...';
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
      btn.textContent = 'Create Meeting';
    }
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
  const chips = document.querySelectorAll('#attendee-chips .attendee-chip');
  return Array.from(chips).map(c => c.dataset.email).filter(Boolean);
}

function removeAttendee(el) {
  el.closest('.attendee-chip').remove();
}

function addAttendeeChip(email) {
  if (!email) return;
  // Prevent duplicates
  const existing = getCurrentAttendees();
  if (existing.includes(email)) return;
  const container = document.getElementById('attendee-chips');
  const chip = document.createElement('span');
  chip.className = 'attendee-chip';
  chip.dataset.email = email;
  chip.innerHTML = `${escapeHtml(email)}<span class="chip-remove" onclick="removeAttendee(this)">&times;</span>`;
  container.appendChild(chip);
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

  let html = '<div class="pipeline-section">';
  html += '<div class="pipeline-title">Pipeline</div>';

  traces.forEach((t, i) => {
    // Determine icon from trace name
    const name = t.name || '';
    let icon = '⚙️';
    if (name.includes('task-parser')) icon = '📝';
    else if (name.includes('worker-match')) icon = '🔀';
    else if (name.includes('worker-execution')) icon = '🤖';

    const hasScores = t.scores && t.scores.length > 0;
    const thumbUp = t.scores?.find(s => s.name === 'human-feedback' && s.value === 1);
    const thumbDown = t.scores?.find(s => s.name === 'human-feedback' && s.value === 0);

    // Format timestamp
    const ts = t.timestamp ? new Date(t.timestamp).toLocaleTimeString() : '';

    html += `<div class="pipeline-step">
      <div class="pipeline-step-header">
        <span class="pipeline-step-name">${icon} ${t.name} <span style="color:var(--text-dim);font-weight:normal;font-size:11px;">${ts}</span></span>
        <div class="pipeline-step-actions">
          <button class="btn-score ${thumbUp ? 'scored-up' : ''}" onclick="scoreStep('${taskId}','${t.trace_id}',1,this)" title="Good">👍</button>
          <button class="btn-score ${thumbDown ? 'scored-down' : ''}" onclick="scoreStep('${taskId}','${t.trace_id}',0,this)" title="Bad">👎</button>
          <button class="btn-annotate" onclick="toggleAnnotation('annot-${i}')" title="Add note">💬</button>
        </div>
      </div>`;

    // Show output first (the result) — this is the most useful info
    if (t.output_summary && t.output_summary !== 'null') {
      html += `<div class="pipeline-step-detail" style="color:var(--text);">→ ${t.output_summary}</div>`;
    }
    // Show input as secondary context
    if (t.input_summary && t.input_summary !== 'null') {
      html += `<div class="pipeline-step-detail">In: ${t.input_summary}</div>`;
    }

    // Show existing scores
    if (hasScores) {
      html += '<div class="pipeline-scores">';
      for (const s of t.scores) {
        const cls = s.value === 1 || s.value === 'good' ? 'good' : 'bad';
        const label = s.comment || (s.value === 1 ? '👍' : s.value === 0 ? '👎' : s.value);
        html += `<span class="pipeline-score-badge ${cls}">${label}</span>`;
      }
      html += '</div>';
    }

    // Annotation box
    html += `<div class="annotation-box" id="annot-${i}">
      <textarea class="annotation-input" id="annot-input-${i}" placeholder="What went wrong or right?"></textarea>
      <button class="annotation-submit" onclick="submitAnnotation('${taskId}','${t.trace_id}','annot-input-${i}')">Submit</button>
    </div>`;

    html += '</div>';
  });

  html += `<a class="pipeline-link" href="${LANGFUSE_HOST}/project/pm-os/sessions/${taskId}" target="_blank">View full traces in LangFuse ↗</a>`;
  html += '</div>';
  return html;
}

async function scoreStep(taskId, traceId, score, btn) {
  try {
    await fetch(`${API}/tasks/${taskId}/traces/${traceId}/score`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ score }),
    });
    // Visual feedback
    const parent = btn.parentElement;
    parent.querySelectorAll('.btn-score').forEach(b => b.classList.remove('scored-up', 'scored-down'));
    btn.classList.add(score === 1 ? 'scored-up' : 'scored-down');
  } catch (err) {
    console.error('Score failed:', err);
  }
}

function toggleAnnotation(id) {
  const box = document.getElementById(id);
  box.classList.toggle('visible');
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
    input.value = '';
    input.parentElement.classList.remove('visible');
    // Refresh pipeline to show new annotation
    if (currentTaskId) openTask(currentTaskId);
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
  if (!confirm('Publish this draft to Jira?')) return;
  const btn = document.getElementById('btn-publish-jira');
  if (btn) { btn.disabled = true; btn.textContent = 'Publishing...'; }
  try {
    const res = await fetch(`${API}/tasks/${taskId}/publish-jira`, { method: 'POST' });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    alert(`Published! ${data.issue_key}: ${data.issue_url}`);
    fetchTasks();
    closeModal();
  } catch (err) {
    alert('Publish failed: ' + err.message);
    if (btn) { btn.disabled = false; btn.textContent = 'Publish to Jira'; }
  }
}
