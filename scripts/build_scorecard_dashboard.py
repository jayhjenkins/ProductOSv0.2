#!/usr/bin/env python3
"""Render the Resident Experience scorecard as ONE self-contained, dependency-free HTML file.

Trend-matrix view: metrics down the side, one dated column per week (newest on the right, a new
column appended each run). A North Star block on top shows the current Home WAU + Board rate and a
WAU line chart. HOAi is an editable, browser-persisted (localStorage) input. Each week column has a
"copy down" button that copies that week's values vertically for pasting into the SharePoint sheet.
Metric definitions are collapsible (click a metric name).

Reads registry.json (display metadata + definitions) + values.json (append-only weekly series).
Optionally records a week's fetched results (--record) or a manual value (--set-manual).

Companion to the metric-scorecard-fetch skill / /scorecard-update command.
"""
from __future__ import annotations
import argparse, json, html, os, tempfile, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = ROOT / "datasets/scorecard/registry.json"
DEFAULT_VALUES = ROOT / "datasets/scorecard/values.json"
DEFAULT_OUT = ROOT / "datasets/scorecard/dashboard.html"


def load_json(p: Path):
    with open(p) as fh:
        return json.load(fh)


def save_json_atomic(p: Path, data) -> None:
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), suffix=".tmp")
    with os.fdopen(fd, "w") as fh:
        json.dump(data, fh, indent=2)
    os.replace(tmp, p)


def write_atomic(p: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), suffix=".tmp")
    with os.fdopen(fd, "w") as fh:
        fh.write(text)
    os.replace(tmp, p)


def fmt(fmt_name: str, v) -> str:
    if v is None:
        return "—"
    if fmt_name in ("k", "pct", "ratio1", "ratio2", "int") and not isinstance(v, (int, float)):
        return str(v)  # a metric carrying a non-numeric value should never crash the render
    if fmt_name == "k":
        s = f"{v/1000:.1f}"
        if s.endswith(".0"):
            s = s[:-2]
        return f"{s}k"
    if fmt_name == "pct":
        return f"{v*100:.1f}%"
    if fmt_name == "ratio1":
        return f"{v:.1f}"
    if fmt_name == "ratio2":
        return f"{v:.2f}"
    if fmt_name == "int":
        return f"{int(v):,}"
    return str(v)


def sorted_weeks(values: dict) -> list:
    return sorted(values.get("weeks", {}).keys())


def series_for(values: dict, slug: str) -> list:
    out = []
    for wk in sorted_weeks(values):
        cell = values["weeks"][wk].get(slug)
        if cell and isinstance(cell.get("value"), (int, float)):
            out.append((wk, cell["value"]))
    return out


def status_color(metric: dict, value) -> str:
    """Green/amber/red only for metrics with a target; else neutral."""
    target = metric.get("target")
    if target is None or not isinstance(value, (int, float)):
        return "neutral"
    higher = metric.get("higher_better", True)
    ratio = value / target if higher else target / max(value, 1e-9)
    if ratio >= 1.0:
        return "good"
    if ratio >= 0.9:
        return "warn"
    return "bad"


def line_chart(series: list, target=None, w=680, h=170) -> str:
    pts = [v for _, v in series]
    if len(pts) < 2:
        return '<div class="chart-empty">Not enough weeks for a trend yet.</div>'
    vals = pts + ([target] if target else [])
    lo, hi = min(vals), max(vals)
    pad = (hi - lo) * 0.12 or 1
    lo -= pad; hi += pad
    rng = hi - lo or 1
    n = len(pts)
    padL, padR, padT, padB = 46, 14, 14, 24
    cw, ch = w - padL - padR, h - padT - padB
    X = lambda i: padL + i * (cw / (n - 1))
    Y = lambda v: padT + ch - ((v - lo) / rng) * ch
    poly = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(pts))
    dots = "".join(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="2.6"/>' for i, v in enumerate(pts))
    tline = ""
    if target:
        ty = Y(target)
        tline = (f'<line x1="{padL}" y1="{ty:.1f}" x2="{w-padR}" y2="{ty:.1f}" class="tline"/>'
                 f'<text x="{w-padR}" y="{ty-5:.1f}" class="tlab" text-anchor="end">target {fmt("k",target)}</text>')
    lx, ly = X(n - 1), Y(pts[-1])
    latest = f'<text x="{lx:.1f}" y="{ly-8:.1f}" class="clatest" text-anchor="end">{fmt("k",pts[-1])}</text>'
    xlabs = (f'<text x="{padL}" y="{h-7}" class="xlab">{series[0][0][5:]}</text>'
             f'<text x="{w-padR}" y="{h-7}" class="xlab" text-anchor="end">{series[-1][0][5:]}</text>')
    ylabs = (f'<text x="{padL-6}" y="{Y(hi-pad)+4:.1f}" class="ylab" text-anchor="end">{fmt("k",hi-pad)}</text>'
             f'<text x="{padL-6}" y="{Y(lo+pad)+4:.1f}" class="ylab" text-anchor="end">{fmt("k",lo+pad)}</text>')
    return (f'<svg class="chart" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{tline}<polyline points="{poly}" class="cline" fill="none"/>{dots}{latest}{xlabs}{ylabs}</svg>')


def render(registry: dict, values: dict, current_week: str) -> str:
    metrics = sorted(registry["metrics"], key=lambda m: m.get("order", 99))
    all_weeks = sorted_weeks(values)
    weeks = all_weeks[-8:]  # table shows the most recent 8 weeks; the WAU chart uses full history

    # North Star block (current values + WAU chart)
    ns_cards, chart = "", ""
    for m in (x for x in metrics if x.get("section") == "northstar"):
        cur = values.get("weeks", {}).get(current_week, {}).get(m["slug"], {}).get("value")
        color = status_color(m, cur)
        ns_cards += (f'<div class="ns {color}"><div class="ns-name">{html.escape(m["name"])}</div>'
                     f'<div class="ns-val">{html.escape(fmt(m["format"], cur))}</div>'
                     f'<div class="ns-tgt">target {html.escape(m.get("target_display",""))}</div></div>')
        if m["slug"] == "home-wau":
            chart = line_chart(series_for(values, "home-wau"), target=m.get("target"))

    # Header row: Metric | (toggle) | one column per week
    head = '<th class="mh">Metric</th>'
    for wk in weeks:
        cls = "wk latest" if wk == current_week else "wk"
        head += (f'<th class="{cls}">{wk[5:]}<span class="yr">{wk[:4]}</span>'
                 f'<button class="colcopy" onclick="copyCol(\'{wk}\',this)" '
                 f'title="Copy this week down (vertical paste)">copy &#8595;</button></th>')

    ncol = len(weeks) + 1
    rows = ""
    for m in metrics:
        slug, src = m["slug"], m.get("source", "auto")
        cells = ""
        for wk in weeks:
            cell = values.get("weeks", {}).get(wk, {}).get(slug, {})
            v = cell.get("value")
            if slug == "hoai-weekly-interactions":
                val = "" if v is None else fmt(m["format"], v)
                cells += (f'<td class="cell" data-week="{wk}">'
                          f'<input class="hoai" data-week="{wk}" value="{html.escape(val)}" '
                          f'placeholder="enter" oninput="saveHoai(this)"></td>')
                continue
            if src == "deferred":
                disp, copy = '<span class="defer">·</span>', ""
            elif v is None:
                disp, copy = "—", ""
            else:
                disp = html.escape(fmt(m["format"], v))
                copy = disp
            extra = ""
            if m.get("show_pct_of") and isinstance(v, (int, float)):
                base = values.get("weeks", {}).get(wk, {}).get(m["show_pct_of"], {}).get("value")
                if isinstance(base, (int, float)) and base:
                    extra = f'<span class="pof">{v/base*100:.1f}%</span>'
            seed = ' title="seeded from Rocks tab"' if str(cell.get("source","")).startswith("seed") else ""
            cells += f'<td class="cell" data-week="{wk}" data-copy="{html.escape(copy)}"{seed}>{disp}{extra}</td>'
        rows += (f'<tr class="mrow">'
                 f'<td class="mname" onclick="toggleDef(\'{slug}\')">'
                 f'<span class="tw">&#9656;</span>{html.escape(m["name"])}'
                 f'<span class="src {src}">{src}</span></td>{cells}</tr>')
        rows += (f'<tr class="defrow" id="def-{slug}"><td colspan="{ncol}">'
                 f'<b>How it&rsquo;s calculated:</b> {html.escape(m.get("definition",""))}</td></tr>')

    gen = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>{html.escape(registry['scorecard'])} Scorecard — trend</title>
<style>
 body{{font:14px -apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#0f1419;color:#e6e9ef}}
 .wrap{{max-width:1180px;margin:0 auto;padding:26px}}
 h1{{font-size:20px;margin:0 0 2px}} .sub{{color:#8b97a8;font-size:12px;margin-bottom:18px}}
 h2{{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:#8b97a8;margin:22px 0 10px}}
 .nsbar{{display:flex;gap:18px;align-items:center;flex-wrap:wrap;background:#161c25;border:1px solid #1e2630;border-radius:12px;padding:16px}}
 .ns{{min-width:150px}} .ns-name{{color:#8b97a8;font-size:12px}}
 .ns-val{{font-size:30px;font-weight:700;margin:2px 0}} .ns-tgt{{color:#8b97a8;font-size:12px}}
 .ns.good .ns-val{{color:#5fd38a}} .ns.warn .ns-val{{color:#f5c451}} .ns.bad .ns-val{{color:#f08a8a}}
 .chart{{flex:1;min-width:360px}} .chart-empty{{color:#8b97a8;font-size:12px}}
 .cline{{stroke:#5b8def;stroke-width:2}} circle{{fill:#5b8def}}
 .tline{{stroke:#5fd38a;stroke-dasharray:4 3;stroke-width:1}} .tlab{{fill:#5fd38a;font-size:10px}}
 .clatest{{fill:#e6e9ef;font-size:12px;font-weight:700}} .xlab,.ylab{{fill:#8b97a8;font-size:10px}}
 .tblwrap{{overflow-x:auto;border:1px solid #1e2630;border-radius:10px}}
 table{{border-collapse:collapse;width:100%;font-size:13px}}
 th,td{{padding:8px 10px;border-bottom:1px solid #1e2630;text-align:right;white-space:nowrap}}
 th.mh,td.mname{{text-align:left;position:sticky;left:0;z-index:2;background:#12171e;border-right:1px solid #2a3340}}
 thead th{{position:sticky;top:0;background:#11161d;color:#8b97a8;font-weight:600;font-size:11px}}
 thead th.mh{{z-index:3;background:#11161d}}
 .tw{{color:#5a6675;margin-right:6px;font-size:10px}}
 th.wk{{text-align:right}} th.wk .yr{{display:block;color:#5a6675;font-weight:400}}
 th.wk.latest{{color:#e6e9ef;background:#16202c}}
 .colcopy{{display:block;margin-top:4px;background:#1b2230;color:#aeb8c7;border:1px solid #2a3340;
   border-radius:5px;padding:2px 6px;cursor:pointer;font:10px monospace}}
 .colcopy:hover{{background:#243047}}
 td.mname{{font-weight:600}} .src{{display:inline-block;margin-left:7px;font-size:9px;font-weight:400;
   padding:1px 5px;border-radius:8px;color:#8b97a8;background:#1b222c;text-transform:uppercase}}
 .src.manual{{color:#f5c451;background:#332a12}} .src.deferred{{color:#7e8794;background:#23262c}}
 .dtoggle{{cursor:pointer;color:#5a6675}} .defer{{color:#5a6675}}
 .pof{{display:block;color:#8b97a8;font-size:10px}}
 td.cell.latest{{background:#141c26}}
 input.hoai{{width:64px;background:#11161d;color:#f5c451;border:1px solid #3a3320;border-radius:5px;
   padding:4px 6px;text-align:right;font:13px inherit}}
 tr.defrow{{display:none}} tr.defrow.show{{display:table-row}}
 tr.defrow td{{text-align:left;color:#aeb8c7;font-size:12px;background:#11161d;white-space:normal}}
 .hint{{color:#8b97a8;font-size:12px;margin-top:14px}}
</style></head><body><div class="wrap">
 <h1>{html.escape(registry['scorecard'])} Scorecard</h1>
 <div class="sub">Trend view · current week <b>{current_week}</b> · generated {gen} · showing last {len(weeks)} of {len(all_weeks)} weeks</div>
 <h2>North Star</h2>
 <div class="nsbar">{ns_cards}{chart}</div>
 <h2>Scorecard — weekly trend</h2>
 <div class="tblwrap"><table>
  <thead><tr>{head}</tr></thead>
  <tbody>{rows}</tbody>
 </table></div>
 <div class="hint">Click a metric name to see how it&rsquo;s calculated. Click <b>copy &#8595;</b> in any week
 header to copy that week&rsquo;s full column, then paste straight down a dated column in your L10 sheets.
 The HOAi cell is editable &mdash; type the number; it&rsquo;s saved in this browser.</div>
</div>
<script>
function toggleDef(s){{var r=document.getElementById('def-'+s);if(r)r.classList.toggle('show');}}
function saveHoai(i){{try{{localStorage.setItem('hoai_'+i.dataset.week,i.value);}}catch(e){{}}}}
function restore(){{document.querySelectorAll('input.hoai').forEach(function(i){{
  try{{var v=localStorage.getItem('hoai_'+i.dataset.week);if(v!==null&&v!=='')i.value=v;}}catch(e){{}}}});}}
function copyCol(wk,btn){{
  var cells=document.querySelectorAll('td.cell[data-week="'+wk+'"]');
  var out=[];cells.forEach(function(c){{var inp=c.querySelector('input');
    out.push(inp?inp.value:(c.dataset.copy||''));}});
  navigator.clipboard.writeText(out.join('\\n'));
  var t=btn.innerHTML;btn.innerHTML='&#10003; copied';setTimeout(function(){{btn.innerHTML=t;}},1100);
}}
window.addEventListener('load',restore);
</script></body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    ap.add_argument("--values", type=Path, default=DEFAULT_VALUES)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--week", help="current as_of Saturday YYYY-MM-DD; default = latest week on file")
    ap.add_argument("--record", type=Path, help="JSON {slug:{value,raw,status,source}} to merge into the week")
    ap.add_argument("--set-manual", help="slug:value to set a manual metric for the week")
    args = ap.parse_args()

    registry = load_json(args.registry)
    values = load_json(args.values)
    values.setdefault("weeks", {})

    if (args.record or args.set_manual) and not args.week:
        raise SystemExit("ERROR: --record/--set-manual require --week")

    if args.record:
        results = load_json(args.record)
        wk = values["weeks"].setdefault(args.week, {})
        stamp = dt.datetime.now().isoformat(timespec="seconds")
        for slug, cell in results.items():
            if not isinstance(cell, dict):  # a flaky subagent must not block the other metrics
                cell = {"value": None, "status": "error", "notes": f"malformed cell: {cell!r}"}
            cell.setdefault("computed_at", stamp)
            wk[slug] = cell
        save_json_atomic(args.values, values)

    if args.set_manual:
        slug, _, raw = args.set_manual.partition(":")
        wk = values["weeks"].setdefault(args.week, {})
        wk[slug] = {"value": float(raw), "status": "ok", "source": "manual",
                    "computed_at": dt.datetime.now().isoformat(timespec="seconds")}
        save_json_atomic(args.values, values)

    week = args.week or (sorted_weeks(values)[-1] if sorted_weeks(values) else dt.date.today().isoformat())
    write_atomic(args.out, render(registry, values, week))
    print(f"Wrote {args.out} (current week {week}, {len(sorted_weeks(values))} weeks on file)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
