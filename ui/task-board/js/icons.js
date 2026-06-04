// icons.js — calm monochrome line-marks that replace the bright emoji.
// All use currentColor and inherit size from the parent (width/height set in CSS).

const ICON = {
  // queue / type marks
  agent: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8 13.5c0-4 1.6-6.8 5-8.2C12.4 9 10.4 11.6 8 13.5Z"/><path d="M8 13.5c0-3-1.2-5.2-3.6-6.4"/><path d="M8 13.5V8.2"/></svg>`,
  collab: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6.2" r="2.4"/><circle cx="10.4" cy="7" r="2"/><path d="M2.8 12.8c.5-1.8 1.9-2.8 3.4-2.8s2.9 1 3.4 2.8"/></svg>`,
  human: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="5.4" r="2.6"/><path d="M3.4 13c.6-2.4 2.4-3.7 4.6-3.7s4 1.3 4.6 3.7"/></svg>`,
  waiting: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="5.2"/><path d="M8 5.2V8l1.9 1.4"/></svg>`,

  // source / context
  meeting: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3.4" width="10" height="9.2" rx="1.6"/><path d="M3 6.2h10"/><path d="M6 2.4v2M10 2.4v2"/></svg>`,

  // status marks
  complete: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="6" stroke-opacity="0.4"/><path d="M5.3 8.2l1.9 1.9 3.5-4"/></svg>`,
  needsHuman: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="6" stroke-opacity="0.4"/><path d="M6.4 6.3a1.7 1.7 0 0 1 3.1.9c0 1.1-1.5 1.3-1.5 2.4"/><circle cx="8" cy="11.4" r="0.55" fill="currentColor" stroke="none"/></svg>`,
  failed: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="6" stroke-opacity="0.4"/><path d="M6 6l4 4M10 6l-4 4"/></svg>`,

  // signals
  cron: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12.6 6.4A5 5 0 0 0 4 5.2L3 6.2"/><path d="M3.4 9.6A5 5 0 0 0 12 10.8l1-1"/><path d="M3 3.6v2.6h2.6M13 12.4V9.8h-2.6"/></svg>`,
  due: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="5.4"/><path d="M8 5.2V8l1.9 1.2"/></svg>`,
  overdue: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2.6 14 13H2L8 2.6Z"/><path d="M8 6.6v3"/><circle cx="8" cy="11.4" r="0.5" fill="currentColor" stroke="none"/></svg>`,
  hourglass: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3h6M5 13h6"/><path d="M5 3c0 2.4 3 3.2 3 5s-3 2.6-3 5M11 3c0 2.4-3 3.2-3 5s3 2.6 3 5"/></svg>`,

  // actions
  done: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 8.4l3 3 6-6.4"/></svg>`,
  output: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3h4v4"/><path d="M13 3l-5.4 5.4"/><path d="M11 9.5V12a1.5 1.5 0 0 1-1.5 1.5h-6A1.5 1.5 0 0 1 2 12V6a1.5 1.5 0 0 1 1.5-1.5H6"/></svg>`,
  doc: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 2.6h5l3 3v8H4Z"/><path d="M9 2.6v3h3"/><path d="M6 8.4h4M6 10.6h4"/></svg>`,
  jira: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M2.6 7.2 7.2 2.6a1 1 0 0 1 1.4 0l3.8 3.8a1 1 0 0 1 0 1.4L7.8 12.4a1 1 0 0 1-1.4 0L2.6 8.6a1 1 0 0 1 0-1.4Z"/></svg>`,
  mail: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><rect x="2.4" y="3.6" width="11.2" height="8.8" rx="1.6"/><path d="M2.8 4.4 8 8.4l5.2-4"/></svg>`,
  chat: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M2.8 4.2h10.4v6H7.4l-2.8 2.4V10.2H2.8z"/></svg>`,
  send: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M13.4 2.6 7 9"/><path d="M13.4 2.6 9.4 13.2l-2.4-4.2-4.2-2.4Z"/></svg>`,
  obsidian: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9.2 1.8 13.4 7l-3.1 7.2-5.3-1.4-2.4-4.5 3.3-6.5Z"/><path d="M9.2 1.8 7.2 6l2.4 3-1.5 5.2"/></svg>`,
};

function svgIcon(name) { return ICON[name] || ''; }
