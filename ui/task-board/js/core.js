const API = '/api';
const LANGFUSE_HOST = 'http://localhost:3000';
let allTasks = [];
let currentTaskId = null;

// ─── Toast Notifications ─────────────────────────────────────────────
function toast(msg, type = 'error', duration = 4000) {
  // No confirmation banners — a click is its own confirmation. Only surface
  // real problems (errors), and even those stay quiet and dismissible.
  if (type !== 'error') return;
  const container = document.getElementById('toast-container');
  if (!container) return;
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.setAttribute('role', 'alert');
  el.textContent = msg;
  el.onclick = () => dismiss(el);
  container.appendChild(el);
  function dismiss(t) { t.classList.add('toast-out'); setTimeout(() => t.remove(), 200); }
  setTimeout(() => { if (el.parentNode) dismiss(el); }, duration);
}

// ─── Confirm dialog ──────────────────────────────────────────────────
// One styled, accessible confirmation for the whole app. Returns a Promise
// that resolves true (confirmed) / false (cancelled). Enter confirms, Esc or
// a backdrop click cancels, and focus is trapped between the two buttons and
// restored to the trigger on close.
function confirmAction({ title = 'Are you sure?', message = '', confirmLabel = 'Confirm', cancelLabel = 'Cancel', danger = false } = {}) {
  return new Promise(resolve => {
    const overlay = document.getElementById('confirm-overlay');
    if (!overlay) { resolve(window.confirm(message || title)); return; }
    const titleEl = document.getElementById('confirm-title');
    const msgEl = document.getElementById('confirm-msg');
    const okBtn = document.getElementById('confirm-ok');
    const cancelBtn = document.getElementById('confirm-cancel');

    titleEl.textContent = title;
    msgEl.textContent = message;
    msgEl.style.display = message ? '' : 'none';
    okBtn.textContent = confirmLabel;
    cancelBtn.textContent = cancelLabel;
    okBtn.className = 'btn ' + (danger ? 'btn-danger' : 'btn-primary');

    const prevFocus = document.activeElement;
    overlay.classList.add('active');
    okBtn.focus();

    function cleanup(result) {
      overlay.classList.remove('active');
      okBtn.removeEventListener('click', onOk);
      cancelBtn.removeEventListener('click', onCancel);
      overlay.removeEventListener('mousedown', onBackdrop);
      document.removeEventListener('keydown', onKey, true);
      if (prevFocus && prevFocus.focus) prevFocus.focus();
      resolve(result);
    }
    function onOk() { cleanup(true); }
    function onCancel() { cleanup(false); }
    function onBackdrop(e) { if (e.target === overlay) cleanup(false); }
    function onKey(e) {
      if (e.key === 'Enter') { e.preventDefault(); e.stopPropagation(); cleanup(true); }
      else if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); cleanup(false); }
      else if (e.key === 'Tab') {
        e.preventDefault();
        const order = [cancelBtn, okBtn];
        const i = order.indexOf(document.activeElement);
        order[(i + (e.shiftKey ? -1 : 1) + order.length) % order.length].focus();
      }
    }
    okBtn.addEventListener('click', onOk);
    cancelBtn.addEventListener('click', onCancel);
    overlay.addEventListener('mousedown', onBackdrop);
    document.addEventListener('keydown', onKey, true);
  });
}

let emailCache = null; // { "Name": "email@co.com", ... }

// ─── Helpers ────────────────────────────────────────────────────────

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function obsidianUri(filePath) {
  // Convert to vault-relative path (strip absolute prefix if present)
  let rel = filePath.startsWith('/') ? filePath.replace(/^\/Users\/jayjenkins\/pm-os\//, '') : filePath;
  // Strip .md extension (Obsidian doesn't need it)
  rel = rel.replace(/\.md$/, '');
  return `obsidian://open?vault=pm-os&file=${encodeURIComponent(rel)}`;
}

function renderAgentOutput(value) {
  if (!value) return '';
  const v = value.trim();
  // Local markdown file → Obsidian link
  if (v.endsWith('.md')) {
    return `<a href="${obsidianUri(v)}" style="color:var(--accent);text-decoration:none;" title="Open in Obsidian">${escapeHtml(value)}</a>`;
  }
  // Contains URL(s) → linkify them inline, keep surrounding text
  if (/https?:\/\//.test(v)) {
    return escapeHtml(value).replace(/https?:\/\/[^\s)&lt;]+/g, url => {
      const href = url.replace(/&amp;/g, '&');
      return `<a href="${href}" target="_blank" rel="noopener" style="color:var(--accent);text-decoration:none;">${url}</a>`;
    });
  }
  // Plain text fallback
  return escapeHtml(value);
}

function meetingName(sourcePath) {
  if (!sourcePath) return null;
  // Extract filename, strip date prefix and extension
  const fname = sourcePath.split('/').pop().replace(/\.[^.]+$/, '');
  // Remove leading date/time pattern like "2026-02-25_15-30_"
  return fname.replace(/^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}_/, '');
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    return d.toLocaleString('en-US', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  } catch {
    return dateStr;
  }
}

let _workerCache = null;

let cronJobs = [];
let cronRawInput = ''; // preserve between steps
