#!/usr/bin/env python3
"""Render the Resident Experience scorecard + Rocks as ONE self-contained HTML file.

Reads registry.json (display metadata) + values.json (append-only weekly time series).
Optionally records a week's fetched results (--record) or a manual value (--set-manual)
into values.json before rendering. No third-party dependencies.

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


def sparkline(series: list, w=120, h=28) -> str:
    pts = [v for _, v in series]
    if len(pts) < 2:
        return '<span class="spark-empty">—</span>'
    lo, hi = min(pts), max(pts)
    rng = (hi - lo) or 1
    n = len(pts)
    coords = []
    for i, v in enumerate(pts):
        x = i * (w / (n - 1))
        y = h - ((v - lo) / rng) * (h - 4) - 2
        coords.append(f"{x:.1f},{y:.1f}")
    return (f'<svg class="spark" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<polyline points="{" ".join(coords)}" fill="none" '
            f'stroke="currentColor" stroke-width="1.5"/></svg>')


def status_color(metric: dict, value) -> str:
    """Green/amber/red only for rock metrics with a target; else neutral."""
    target = metric.get("target")
    if target is None or value is None:
        return "neutral"
    higher = metric.get("higher_better", True)
    ratio = value / target if higher else target / max(value, 1e-9)
    if ratio >= 1.0:
        return "good"
    if ratio >= 0.9:
        return "warn"
    return "bad"


def render(registry: dict, values: dict, week: str) -> str:
    metrics = sorted(registry["metrics"], key=lambda m: m.get("order", 99))
    wkdata = values.get("weeks", {}).get(week, {})
    rows = []
    for m in metrics:
        slug = m["slug"]
        cell = wkdata.get(slug, {})
        value = cell.get("value")
        src = m.get("source", "auto")
        if src == "deferred":
            disp = '<span class="badge defer">deferred</span>'
            note = m.get("note", "")
        elif src == "manual" and value is None:
            disp = '<span class="badge manual">enter manually</span>'
            note = ""
        else:
            disp = html.escape(fmt(m["format"], value))
            note = ""
        pct_of = ""
        if m.get("show_pct_of") and isinstance(value, (int, float)):
            base = wkdata.get(m["show_pct_of"], {}).get("value")
            if isinstance(base, (int, float)) and base:
                pct_of = f'<span class="pctof">{value/base*100:.1f}% of web</span>'
        raw = ""
        if m.get("raw_label") and cell.get("raw") is not None:
            raw = f'<span class="raw">{m["raw_label"]}: {html.escape(str(cell["raw"]))}</span>'
        target = (f'<span class="target">target {html.escape(m["target_display"])}</span>'
                  if m.get("target_display") else "")
        color = status_color(m, value)
        spark = sparkline(series_for(values, slug))
        copy_val = html.escape(fmt(m["format"], value)) if value is not None else ""
        rock = '<span class="rockflag">★ Rock</span>' if m.get("rock") else ""
        note_html = f'<span class="note">{html.escape(note)}</span>' if note else ""
        rows.append(f"""
        <tr class="{color}">
          <td class="name">{html.escape(m['name'])} {rock}</td>
          <td class="val">{disp} {pct_of} {raw} {note_html}</td>
          <td class="tgt">{target}</td>
          <td class="trend">{spark}</td>
          <td class="copy"><button onclick="cp(this)" data-v="{copy_val}">⧉ {copy_val or '—'}</button></td>
        </tr>""")

    rock_rows = []
    for m in metrics:
        if not m.get("rock"):
            continue
        value = wkdata.get(m["slug"], {}).get("value")
        color = status_color(m, value)
        rock_rows.append(
            f'<div class="rock {color}"><div class="rname">{html.escape(m["name"])}</div>'
            f'<div class="rval">{html.escape(fmt(m["format"], value))}</div>'
            f'<div class="rtgt">target {html.escape(m.get("target_display",""))}</div></div>')

    gen = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    weeks_avail = ", ".join(sorted_weeks(values)) or "none"
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>{html.escape(registry['scorecard'])} Scorecard — week of {week}</title>
<style>
 body{{font:14px -apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#0f1419;color:#e6e9ef}}
 .wrap{{max-width:920px;margin:0 auto;padding:28px}}
 h1{{font-size:20px;margin:0 0 2px}} .sub{{color:#8b97a8;font-size:12px;margin-bottom:20px}}
 h2{{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:#8b97a8;margin:26px 0 10px}}
 table{{width:100%;border-collapse:collapse}}
 td{{padding:10px 8px;border-bottom:1px solid #1e2630;vertical-align:middle}}
 .name{{font-weight:600;width:34%}} .val{{font-size:16px}} .tgt{{color:#8b97a8;font-size:12px}}
 .rockflag{{color:#f5c451;font-size:11px;margin-left:6px}}
 .pctof,.raw,.note{{display:block;color:#8b97a8;font-size:11px;font-weight:400}}
 .target{{white-space:nowrap}}
 tr.good .val{{color:#5fd38a}} tr.warn .val{{color:#f5c451}} tr.bad .val{{color:#f08a8a}}
 .badge{{font-size:11px;padding:2px 7px;border-radius:10px}}
 .badge.defer{{background:#2a2f3a;color:#8b97a8}} .badge.manual{{background:#3a2f12;color:#f5c451}}
 .spark{{color:#5b8def}} .spark-empty{{color:#3a414c}}
 .copy button{{background:#1b2230;color:#aeb8c7;border:1px solid #2a3340;border-radius:6px;
   padding:5px 9px;cursor:pointer;font:12px monospace}} .copy button:hover{{background:#243047}}
 .rocks{{display:flex;gap:14px;flex-wrap:wrap}}
 .rock{{flex:1;min-width:200px;background:#161c25;border:1px solid #1e2630;border-radius:10px;padding:14px}}
 .rock.good{{border-color:#2f5e43}} .rock.warn{{border-color:#5e5026}} .rock.bad{{border-color:#5e2f2f}}
 .rname{{color:#8b97a8;font-size:12px}} .rval{{font-size:26px;font-weight:700;margin:4px 0}}
 .rtgt{{color:#8b97a8;font-size:12px}}
</style></head><body><div class="wrap">
 <h1>{html.escape(registry['scorecard'])} Scorecard</h1>
 <div class="sub">Week ending (as_of) <b>{week}</b> · generated {gen} · weeks on file: {weeks_avail}</div>
 <h2>Rocks</h2><div class="rocks">{''.join(rock_rows)}</div>
 <h2>Scorecard</h2>
 <table><thead><tr><td class="name">Metric</td><td>This week</td><td>Target</td><td>Trend</td><td>Copy</td></tr></thead>
 <tbody>{''.join(rows)}</tbody></table>
 <div class="sub" style="margin-top:18px">Click a Copy cell to put the value on your clipboard, then paste into the SharePoint Scorecard tab.</div>
</div>
<script>
function cp(b){{navigator.clipboard.writeText(b.dataset.v);b.textContent='✓ copied';setTimeout(()=>b.textContent='⧉ '+(b.dataset.v||'—'),1200);}}
</script></body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    ap.add_argument("--values", type=Path, default=DEFAULT_VALUES)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--week", help="as_of Saturday YYYY-MM-DD; default = latest week on file")
    ap.add_argument("--record", type=Path, help="JSON file of {slug:{value,raw,status,source}} to merge into the week")
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

    week = args.week or (sorted_weeks(values)[-1] if sorted_weeks(values) else
                         dt.date.today().isoformat())
    out_html = render(registry, values, week)
    write_atomic(args.out, out_html)
    print(f"Wrote {args.out} (week {week}, {len(sorted_weeks(values))} weeks on file)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
