const API = '/api';
const LANGFUSE_HOST = 'http://localhost:3000';
let allTasks = [];
let currentTaskId = null;

// ─── Toast Notifications ─────────────────────────────────────────────
function toast(msg, type = 'error', duration = 4000) {
  const container = document.getElementById('toast-container');
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.textContent = msg;
  el.onclick = () => dismiss(el);
  container.appendChild(el);
  function dismiss(t) { t.classList.add('toast-out'); setTimeout(() => t.remove(), 200); }
  setTimeout(() => { if (el.parentNode) dismiss(el); }, duration);
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
