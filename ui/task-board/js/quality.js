// ─── Quality Surface (read-only) — calm worker-trust view ────────────
// A gentle, low-density read on how each agent/worker is doing, per a
// "shadow judge" that quietly scores completed artifacts. Observe-only:
// nothing here changes your tasks.
//
// Per worker: the loud overall score, a sparkline that SHOWS the trend
// (no words), and one compact dimension chart instead of four bleeding
// bars. No pills, no status labels. Below: a "Worth a second look" list
// of judge↔you divergences that link back to the originating card.

const Q_ICON = {
  keep: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 8.2 7 10.6l4.5-5"/></svg>',
  flag: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4.6 2.6v10.8"/><path d="M4.6 3.2h6.2l-1.3 2.2 1.3 2.2H4.6"/></svg>',
};

function _qTone(s) {
  if (s == null) return 'tone-mid';
  if (s >= 8) return 'tone-high';
  if (s >= 5.5) return 'tone-mid';
  return 'tone-low';
}

// Sparkline that shows the trend visually. Uses real history when present,
// otherwise draws a simple two-point slope from (score − trend) → score.
function _qSpark(g) {
  let pts = Array.isArray(g.history) && g.history.length >= 2
    ? g.history.slice(-8)
    : [Number(((g.avg_score ?? 0) - (g.trend || 0)).toFixed(1)), (g.avg_score ?? 0)];
  if (pts.length < 2) return '';

  const w = 72, h = 26, pad = 4;
  const min = Math.min(...pts), max = Math.max(...pts);
  const range = Math.max(0.6, max - min); // floor keeps a flat line gently centered
  const n = pts.length;
  const X = i => pad + i * (w - 2 * pad) / (n - 1);
  const Y = v => h - pad - ((v - min) / range) * (h - 2 * pad);
  const d = pts.map((v, i) => (i ? 'L' : 'M') + X(i).toFixed(1) + ' ' + Y(v).toFixed(1)).join(' ');
  const area = `M${X(0).toFixed(1)} ${(h - pad).toFixed(1)} ` +
    pts.map((v, i) => 'L' + X(i).toFixed(1) + ' ' + Y(v).toFixed(1)).join(' ') +
    ` L${X(n - 1).toFixed(1)} ${(h - pad).toFixed(1)} Z`;
  const lx = X(n - 1).toFixed(1), ly = Y(pts[n - 1]).toFixed(1);

  return `<svg class="q-spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" aria-hidden="true">
    <path class="q-spark-area" d="${area}"/>
    <path class="q-spark-line" d="${d}"/>
    <circle class="q-spark-dot" cx="${lx}" cy="${ly}" r="2.1"/>
  </svg>`;
}

// One compact dimension chart: short vertical bars sharing a baseline, so
// differences read at a glance. Dimension keys are kind-specific (documents use
// context/reasoning/evidence/format; messages use voice/format/fulfils_ask/
// clarity), so render whatever keys the group carries, in a sensible order.
const _Q_DIM_LABELS = {
  context: 'Context', reasoning: 'Reasoning', evidence: 'Evidence', format: 'Format',
  voice: 'Voice', fulfils_ask: 'Fulfils ask', clarity: 'Clarity',
};
const _Q_DIM_ORDER = ['context', 'reasoning', 'evidence', 'format', 'voice', 'fulfils_ask', 'clarity'];
function _qLabel(k) {
  return _Q_DIM_LABELS[k] || k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}
function _qDims(dims) {
  if (!dims) return '';
  const keys = Object.keys(dims).filter(k => dims[k] != null);
  if (!keys.length) return '';
  keys.sort((a, b) => {
    const ia = _Q_DIM_ORDER.indexOf(a), ib = _Q_DIM_ORDER.indexOf(b);
    return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
  });
  const cols = keys.map(k => {
    const label = _qLabel(k);
    const pct = Math.max(8, Math.min(100, dims[k] * 10));
    return `<div class="q-dcol" title="${label}: ${dims[k]}/10">
      <span class="q-dval">${dims[k]}</span>
      <span class="q-dtrack"><span class="q-dbar" style="height:${pct}%"></span></span>
      <span class="q-dlabel">${label}</span>
    </div>`;
  }).join('');
  return `<div class="q-dims">${cols}</div>`;
}

function _qAgreement(g, langfuse) {
  if (!langfuse) return 'agreement paused — LangFuse offline';
  if (g.agreement_pct == null || !g.reacted) return 'no ratings from you yet';
  return `you agree ${g.agreement_pct}%`;
}

async function renderQuality() {
  const view = document.getElementById('quality-view');
  if (!view) return;
  view.innerHTML = `<div class="loading">Loading quality…</div>`;

  let data;
  try {
    const res = await fetch(`${API}/quality`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    data = await res.json();
  } catch (err) {
    view.innerHTML = `<div class="loading">Error loading quality: ${escapeHtml(err.message)}</div>`;
    toast(`Quality failed to load: ${err.message}`);
    return;
  }

  const intro = `A quiet second opinion on agent work — observe-only, so nothing here touches your tasks.`;

  if (!data.total_judged) {
    view.innerHTML = `
      <div class="quality-head">
        <h3>Quality</h3>
        <p class="quality-sub">${intro}</p>
      </div>
      <div class="quality-empty">Nothing judged yet — the judge quietly scores agent artifacts as they complete.</div>`;
    return;
  }

  let html = `
    <div class="quality-head">
      <h3>Quality</h3>
      <p class="quality-sub">${intro} <span class="quality-sub-dim">${data.total_judged} reviewed so far.</span></p>
    </div>
    <div class="quality-grid">`;

  data.groups.forEach(g => {
    const tone = _qTone(g.avg_score);
    const phase = (g.phase || '').toLowerCase() === 'trusted' ? 'trusted' : 'observe-only';
    html += `
      <div class="card q-card ${tone}">
        <div class="q-card-head">
          <span class="q-name">${escapeHtml(g.task_type)}</span>
          <span class="q-phase-txt">${phase}</span>
        </div>
        <div class="q-headline">
          <span class="q-score-num">${g.avg_score ?? '—'}<span class="q-score-of">/10</span></span>
          ${_qSpark(g)}
        </div>
        ${_qDims(g.dimensions)}
        <div class="q-foot"><span>${g.count} reviewed</span><span class="q-foot-sep">·</span><span>${_qAgreement(g, data.langfuse)}</span></div>
      </div>`;
  });
  html += `</div>`;

  if (data.disagreements && data.disagreements.length) {
    html += `<div class="quality-section-title">Worth a second look <span class="quality-section-sub">where you and the judge saw it differently</span></div>`;
    html += `<div class="q-dis-list">`;
    data.disagreements.forEach(d => {
      const youMark = d.human_value === 1
        ? `<span class="q-you q-you-keep">${Q_ICON.keep}you kept it</span>`
        : `<span class="q-you q-you-flag">${Q_ICON.flag}you flagged it</span>`;
      html += `
        <div class="card q-disagreement" onclick="openTask('${d.task_id}')">
          <div class="q-dis-head">
            <span class="q-dis-id">${escapeHtml(d.task_id)}</span>
            <span class="q-dis-type">${escapeHtml(d.task_type)}</span>
          </div>
          <div class="q-dis-verdicts">
            <span class="q-judge ${_qTone(d.judge_score)}">Judge saw ${d.judge_score}/10</span>
            ${youMark}
          </div>
          <div class="q-dis-why">${escapeHtml(d.judge_why || '')}</div>
          ${d.human_comment ? `<div class="q-dis-note">Your note · ${escapeHtml(d.human_comment)}</div>` : ''}
        </div>`;
    });
    html += `</div>`;
  }

  view.innerHTML = html;
}
