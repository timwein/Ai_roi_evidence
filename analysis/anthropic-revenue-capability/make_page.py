#!/usr/bin/env python3
"""Generate index.html — self-contained chart page for the revenue-vs-capability
fit. Reads data.json + results.json, re-derives fit objects via fit.py (so the
page can never drift from the model), emits inline SVG. Stdlib only."""

import json
import math
import datetime as dt
from pathlib import Path

import fit as F

HERE = Path(__file__).parent
data = json.loads((HERE / "data.json").read_text())
res = json.loads((HERE / "results.json").read_text())

obs = res["n_obs"]
rows = res["obs"]
proj = res["projections"]

# Re-derive the fit objects exactly as fit.main() does.
ln_arr = [math.log(r["arr"]) for r in rows]
m_eci = F.OLS([r["eci"] for r in rows], ln_arr)
cap = F.frontier_records(data["anthropic_capability"], "eci")
m_eci_time = F.OLS([F.years_since(F.d(m["release_date"])) for m in cap],
                   [m["eci"] for m in cap])
start = F.d(data["frontier_fit_start"])
frn = [m for m in F.frontier_records(data["frontier_eci"], "eci")
       if F.d(m["release_date"]) >= start]
m_frontier_time = F.OLS([F.years_since(F.d(m["release_date"])) for m in frn],
                        [m["eci"] for m in frn])
both = [m for m in data["anthropic_capability"]
        if m.get("eci") is not None and m.get("metr_p50_minutes") is not None]
link = F.OLS([m["eci"] for m in both],
             [math.log2(m["metr_p50_minutes"]) for m in both])

C = res["derived"]


def money(x_b, digits=None):
    if x_b >= 1000:
        v = x_b / 1000
        return f"${v:,.0f}T" if (digits == 0 or v >= 10) else f"${v:,.1f}T"
    if x_b >= 100:
        return f"${x_b:,.0f}B"
    if x_b >= 10:
        return f"${x_b:,.0f}B"
    return f"${x_b:,.1f}B" if x_b >= 1 else f"${x_b*1000:,.0f}M"


def horizon(minutes):
    if minutes < 90:
        return f"{minutes:.0f} min"
    h = minutes / 60
    if h < 48:
        return f"{h:,.0f} h"
    if h < 2000:
        return f"{h:,.0f} h (~{h/40:,.0f} wk)"
    return f"~{h/167:,.0f} work-months"


def fdate(iso):
    return dt.date.fromisoformat(iso).strftime("%b %Y")


# ---------------------------------------------------------------- chart A
# ARR (log y) vs ECI, with fit line, 80/95% PI bands, projections.

AW, AH = 920, 470
AP = {"l": 74, "r": 30, "t": 18, "b": 44}
X0, X1 = 126, 197
YMIN, YMAX = 0.6, 40000.0  # $B, log scale


def ax(v):  # ECI -> px
    return AP["l"] + (v - X0) / (X1 - X0) * (AW - AP["l"] - AP["r"])


def ay(v):  # $B -> px (log)
    ln0, ln1 = math.log10(YMIN), math.log10(YMAX)
    return AP["t"] + (ln1 - math.log10(v)) / (ln1 - ln0) * (AH - AP["t"] - AP["b"])


def path(pts):
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


xs = [X0 + 1 + i * (X1 - 1 - X0) / 120 for i in range(121)]
band95 = [(ax(x), ay(math.exp(m_eci.pi(x, 0.975)[1]))) for x in xs] + \
         [(ax(x), ay(math.exp(m_eci.pi(x, 0.975)[0]))) for x in reversed(xs)]
band80 = [(ax(x), ay(math.exp(m_eci.pi(x, 0.90)[1]))) for x in xs] + \
         [(ax(x), ay(math.exp(m_eci.pi(x, 0.90)[0]))) for x in reversed(xs)]
xmax_obs = max(r["eci"] for r in rows)
fit_in = [(ax(x), ay(math.exp(m_eci.predict(x)))) for x in xs if x <= xmax_obs]
fit_out = [(ax(x), ay(math.exp(m_eci.predict(x)))) for x in xs if x >= xmax_obs]

ygrid = [1, 3, 10, 30, 100, 300, 1000, 3000, 10000, 30000]
ylab = {1: "$1B", 3: "$3B", 10: "$10B", 30: "$30B", 100: "$100B", 300: "$300B",
        1000: "$1T", 3000: "$3T", 10000: "$10T", 30000: "$30T"}

gA = []
for v in ygrid:
    y = ay(v)
    gA.append(f'<line class="grid" x1="{AP["l"]}" y1="{y:.1f}" x2="{AW-AP["r"]}" y2="{y:.1f}"/>'
              f'<text class="tick" x="{AP["l"]-8}" y="{y+4:.1f}" text-anchor="end">{ylab[v]}</text>')
for v in range(130, 200, 10):
    x = ax(v)
    gA.append(f'<line class="grid" x1="{x:.1f}" y1="{AP["t"]}" x2="{x:.1f}" y2="{AH-AP["b"]}"/>'
              f'<text class="tick" x="{x:.1f}" y="{AH-AP["b"]+18}" text-anchor="middle">{v}</text>')
gA.append(f'<text class="axlab" x="{(AP["l"]+AW-AP["r"])/2:.0f}" y="{AH-6}" text-anchor="middle">Epoch Capabilities Index (best public Anthropic model)</text>')

gA.append(f'<polygon class="b95" points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in band95)}"/>')
gA.append(f'<polygon class="b80" points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in band80)}"/>')
gA.append(f'<path class="fit" d="{path(fit_in)}"/>')
gA.append(f'<path class="fit dash" d="{path(fit_out)}"/>')

# projection diamonds + selective labels
for p in proj:
    x, y = ax(p["eci"]), ay(p["arr_central_b"])
    lo95, hi95 = p["arr_pi95_b"]
    lo80, hi80 = p["arr_pi80_b"]
    tip = (f"<b>ECI {p['eci']}</b> — central {money(p['arr_central_b'])}"
           f"<br>80% PI {money(lo80)}–{money(hi80)}"
           f"<br>95% PI {money(lo95)}–{money(hi95)}"
           f"<br>METR model: {money(p['arr_via_metr_b'])} · ensemble {money(p['arr_ensemble_b'])}"
           f"<br>≈ {fdate(p['eta_anthropic_trend'])} (Anthropic trend)")
    gA.append(f'<g class="pt" tabindex="0" data-tip="{tip.replace(chr(34), "&quot;")}">'
              f'<circle class="hit" cx="{x:.1f}" cy="{y:.1f}" r="14"/>'
              f'<path class="diam" d="M{x:.1f} {y-5.5:.1f}L{x+5.5:.1f} {y:.1f}L{x:.1f} {y+5.5:.1f}L{x-5.5:.1f} {y:.1f}Z"/></g>')
    if p["eci"] in (170, 180, 190):
        gA.append(f'<text class="dlab proj" x="{x:.1f}" y="{y-12:.1f}" text-anchor="middle">{money(p["arr_central_b"], 0)}</text>')

# observation dots + selective labels (first, last)
for i, r in enumerate(rows):
    x, y = ax(r["eci"]), ay(r["arr"])
    tip = (f"<b>{r['date']}</b> — ARR {money(r['arr'])}"
           f"<br>ECI {r['eci']} · METR 50% horizon {horizon(r['metr_min'])}")
    gA.append(f'<g class="pt" tabindex="0" data-tip="{tip}">'
              f'<circle class="hit" cx="{x:.1f}" cy="{y:.1f}" r="13"/>'
              f'<circle class="obs" cx="{x:.1f}" cy="{y:.1f}" r="4.5"/></g>')
    if i == 0:
        gA.append(f'<text class="dlab" x="{x+10:.1f}" y="{y+4:.1f}" text-anchor="start">$1B · Dec 2024</text>')
    if i == len(rows) - 1:
        gA.append(f'<text class="dlab" x="{x-10:.1f}" y="{y-10:.1f}" text-anchor="end">~$70B · Aug 2026</text>')

chartA = (f'<svg viewBox="0 0 {AW} {AH}" role="img" '
          f'aria-label="Scatter of Anthropic annualized revenue against ECI with fitted exponential and prediction intervals extrapolated to ECI 195">'
          + "".join(gA) + "</svg>")

# ---------------------------------------------------------------- chart B
# ECI vs time: Anthropic records (blue), frontier records (green), targets.

BW, BH = 452, 360
BP = {"l": 46, "r": 82, "t": 14, "b": 40}
T0, T1 = -1.0, 5.4  # years since 2024-01-01: 2023.0 .. mid-2029
E0, E1 = 122, 200


def bx(t):
    return BP["l"] + (t - T0) / (T1 - T0) * (BW - BP["l"] - BP["r"])


def by(e):
    return BP["t"] + (E1 - e) / (E1 - E0) * (BH - BP["t"] - BP["b"])


gB = []
for yr in range(2023, 2030):
    t = F.years_since(dt.date(yr, 1, 1))
    x = bx(t)
    gB.append(f'<line class="grid" x1="{x:.1f}" y1="{BP["t"]}" x2="{x:.1f}" y2="{BH-BP["b"]}"/>'
              f'<text class="tick" x="{x:.1f}" y="{BH-BP["b"]+16}" text-anchor="middle">{yr}</text>')
for e in range(130, 200, 10):
    y = by(e)
    gB.append(f'<line class="grid" x1="{BP["l"]}" y1="{y:.1f}" x2="{BW-BP["r"]}" y2="{y:.1f}"/>'
              f'<text class="tick" x="{BP["l"]-6}" y="{y+4:.1f}" text-anchor="end">{e}</text>')

# trend lines
t_a0, t_a1 = F.years_since(F.d(cap[0]["release_date"])), m_eci_time.solve_x(196)
gB.append(f'<path class="tr-anth" d="{path([(bx(t_a0), by(m_eci_time.predict(t_a0))), (bx(min(t_a1, T1-0.05)), by(min(196, m_eci_time.predict(T1-0.05))))])}"/>')
t_f0 = F.years_since(start)
t_f1 = m_frontier_time.solve_x(196)
gB.append(f'<path class="tr-front" d="{path([(bx(t_f0), by(m_frontier_time.predict(t_f0))), (bx(min(t_f1, T1-0.05)), by(min(196, m_frontier_time.predict(T1-0.05))))])}"/>')

# target lines + ETA labels
for T in (170, 180, 190):
    y = by(T)
    eta = next(p for p in proj if p["eci"] == T)
    short = dt.date.fromisoformat(eta["eta_anthropic_trend"]).strftime("%b ’%y")
    gB.append(f'<line class="target" x1="{BP["l"]}" y1="{y:.1f}" x2="{BW-BP["r"]}" y2="{y:.1f}"/>'
              f'<text class="dlab proj" x="{BW-BP["r"]+5}" y="{y+3.5:.1f}" text-anchor="start">{short}</text>')

for m in frn + [f for f in F.frontier_records(data["frontier_eci"], "eci") if F.d(f["release_date"]) < start]:
    x, y = bx(F.years_since(F.d(m["release_date"]))), by(m["eci"])
    tip = f"<b>{m['model']}</b> ({m['lab']}) — ECI {m['eci']}<br>{fdate(m['release_date'])} · cross-lab frontier record"
    gB.append(f'<g class="pt" tabindex="0" data-tip="{tip}">'
              f'<circle class="hit" cx="{x:.1f}" cy="{y:.1f}" r="12"/>'
              f'<circle class="front" cx="{x:.1f}" cy="{y:.1f}" r="4.5"/></g>')
for m in cap:
    x, y = bx(F.years_since(F.d(m["release_date"]))), by(m["eci"])
    tip = f"<b>{m['model']}</b> — ECI {m['eci']}<br>{fdate(m['release_date'])} · Anthropic frontier record"
    gB.append(f'<g class="pt" tabindex="0" data-tip="{tip}">'
              f'<circle class="hit" cx="{x:.1f}" cy="{y:.1f}" r="12"/>'
              f'<circle class="obs" cx="{x:.1f}" cy="{y:.1f}" r="3.6"/></g>')

chartB = (f'<svg viewBox="0 0 {BW} {BH}" role="img" '
          f'aria-label="ECI versus time for Anthropic and cross-lab frontier records, with trend lines reaching 170, 180 and 190">'
          + "".join(gB) + "</svg>")

# ---------------------------------------------------------------- chart C
# METR horizon (log2 y) vs ECI — the link fit.

CW, CH = 452, 360
CP = {"l": 56, "r": 18, "t": 14, "b": 40}
XC0, XC1 = 125, 160
H0, H1 = 4.0, 1600.0  # minutes


def cx(e):
    return CP["l"] + (e - XC0) / (XC1 - XC0) * (CW - CP["l"] - CP["r"])


def cy(h):
    l0, l1 = math.log2(H0), math.log2(H1)
    return CP["t"] + (l1 - math.log2(h)) / (l1 - l0) * (CH - CP["t"] - CP["b"])


gC = []
for h, lab in [(5, "5 min"), (15, "15 min"), (60, "1 h"), (240, "4 h"), (720, "12 h")]:
    y = cy(h)
    gC.append(f'<line class="grid" x1="{CP["l"]}" y1="{y:.1f}" x2="{CW-CP["r"]}" y2="{y:.1f}"/>'
              f'<text class="tick" x="{CP["l"]-6}" y="{y+4:.1f}" text-anchor="end">{lab}</text>')
for e in range(130, 165, 10):
    x = cx(e)
    gC.append(f'<line class="grid" x1="{x:.1f}" y1="{CP["t"]}" x2="{x:.1f}" y2="{CH-CP["b"]}"/>'
              f'<text class="tick" x="{x:.1f}" y="{CH-CP["b"]+16}" text-anchor="middle">{e}</text>')
gC.append(f'<path class="fit" d="{path([(cx(XC0+1), cy(2**link.predict(XC0+1))), (cx(XC1-1), cy(2**link.predict(XC1-1)))])}"/>')
for m in both:
    x, y = cx(m["eci"]), cy(m["metr_p50_minutes"])
    tip = f"<b>{m['model']}</b> — ECI {m['eci']}<br>METR 50% horizon {horizon(m['metr_p50_minutes'])} ({m['metr_suite']})"
    gC.append(f'<g class="pt" tabindex="0" data-tip="{tip}">'
              f'<circle class="hit" cx="{x:.1f}" cy="{y:.1f}" r="12"/>'
              f'<circle class="obs" cx="{x:.1f}" cy="{y:.1f}" r="4.5"/></g>')
gC.append(f'<text class="dlab" x="{cx(129)}" y="{cy(300):.1f}">R² = {link.r2:.3f}</text>'
          f'<text class="dlab" x="{cx(129)}" y="{cy(300)+15:.1f}">horizon ×2 per {1/link.b:.1f} ECI pts</text>')

chartC = (f'<svg viewBox="0 0 {CW} {CH}" role="img" '
          f'aria-label="METR 50 percent time horizon versus ECI for six Anthropic models with near-perfect log-linear link">'
          + "".join(gC) + "</svg>")

# ---------------------------------------------------------------- tables

proj_rows = "".join(
    f"<tr{' class=hl' if p['eci'] in (170, 180, 190) else ''}>"
    f"<td>{p['eci']}</td><td>{horizon(p['metr_equiv_p50_minutes'])}</td>"
    f"<td><b>{money(p['arr_central_b'])}</b></td>"
    f"<td>{money(p['arr_pi80_b'][0])} – {money(p['arr_pi80_b'][1])}</td>"
    f"<td>{money(p['arr_pi95_b'][0])} – {money(p['arr_pi95_b'][1])}</td>"
    f"<td>{money(p['arr_via_metr_b'])}</td><td>{money(p['arr_ensemble_b'])}</td>"
    f"<td>{fdate(p['eta_anthropic_trend'])} / {fdate(p['eta_frontier_trend'])}</td></tr>"
    for p in proj)

src_by_date = {p["date"]: p for p in data["revenue_points"]}
obs_rows = "".join(
    f"<tr><td>{r['date']}</td><td>{money(r['arr'])}</td><td>{r['eci']}</td>"
    f"<td>{horizon(r['metr_min'])}</td>"
    f"<td>{src_by_date[r['date']]['confirmed']}</td>"
    f"<td><a href=\"{src_by_date[r['date']]['url']}\" rel=\"noopener\">{src_by_date[r['date']]['source'].split(':')[0].split('(')[0].strip()}</a></td></tr>"
    for r in rows)

# ---------------------------------------------------------------- page

html = f"""<title>Revenue per ECI Point</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root {{
  --surface-1: #fcfcfb; --surface-2: #f4f3f0;
  --text-primary: #0b0b0b; --text-secondary: #52514e; --text-muted: #78766f;
  --border: #dedcd6; --border-strong: #c3c1b9;
  --c-obs: #2a78d6; --c-model: #d95926; --c-front: #199e70;
  --band80: rgba(217,89,38,.16); --band95: rgba(217,89,38,.08);
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --surface-1: #1a1a19; --surface-2: #232322;
    --text-primary: #ffffff; --text-secondary: #c3c2b7; --text-muted: #99978d;
    --border: #383835; --border-strong: #4d4c48;
    --c-obs: #3987e5; --c-model: #e8622e; --c-front: #1baf7a;
    --band80: rgba(232,98,46,.20); --band95: rgba(232,98,46,.10);
  }}
}}
:root[data-theme="dark"] {{
  --surface-1: #1a1a19; --surface-2: #232322;
  --text-primary: #ffffff; --text-secondary: #c3c2b7; --text-muted: #99978d;
  --border: #383835; --border-strong: #4d4c48;
  --c-obs: #3987e5; --c-model: #e8622e; --c-front: #1baf7a;
  --band80: rgba(232,98,46,.20); --band95: rgba(232,98,46,.10);
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; background: var(--surface-1); color: var(--text-primary);
  font: 16px/1.6 ui-sans-serif, -apple-system, "Segoe UI", Inter, system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}}
.wrap {{ max-width: 1080px; margin: 0 auto; padding: 40px 22px 60px; }}
header h1 {{ font-size: 27px; letter-spacing: -.02em; margin: 0 0 6px; text-wrap: balance; }}
header .sub {{ color: var(--text-secondary); max-width: 72ch; margin: 0; }}
.mut {{ color: var(--text-muted); }}
.mini {{ font-size: 12.5px; }}
a {{ color: inherit; }}
code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .89em; }}

.callout {{
  border-left: 3px solid var(--c-model); background: var(--surface-2);
  border-radius: 0 10px 10px 0; padding: 12px 16px; margin: 22px 0;
  color: var(--text-secondary); max-width: 86ch;
}}
.callout b {{ color: var(--text-primary); }}

.tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(215px, 1fr)); gap: 12px; margin: 26px 0; }}
.tile {{ background: var(--surface-2); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; }}
.tile .k {{ font-size: 11px; letter-spacing: .07em; text-transform: uppercase; color: var(--text-muted); font-weight: 600; }}
.tile .v {{ font-size: 29px; font-weight: 650; letter-spacing: -.02em; margin-top: 6px; }}
.tile .s {{ font-size: 12px; color: var(--text-muted); margin-top: 2px; }}

.card {{ background: var(--surface-2); border: 1px solid var(--border); border-radius: 10px; padding: 18px 18px 10px; margin: 18px 0; }}
.card h2 {{ font-size: 15px; margin: 0 0 2px; letter-spacing: -.01em; }}
.card .note {{ font-size: 12.5px; color: var(--text-muted); margin: 0 0 10px; }}
.duo {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
@media (max-width: 780px) {{ .duo {{ grid-template-columns: 1fr; }} }}
svg {{ display: block; width: 100%; height: auto; }}

.legend {{ display: flex; flex-wrap: wrap; gap: 14px; font-size: 12.5px; color: var(--text-secondary); margin: 4px 0 10px; }}
.legend span {{ display: inline-flex; align-items: center; gap: 6px; }}
.sw {{ width: 10px; height: 10px; border-radius: 2px; flex: none; }}
.sw.line {{ height: 3px; border-radius: 2px; width: 16px; }}
.sw.dash {{ height: 0; width: 16px; border-top: 3px dashed; border-radius: 0; background: none !important; }}
.sw.hollow {{ background: transparent !important; border: 2px solid; border-radius: 50%; }}

.grid {{ stroke: var(--border); stroke-width: 1; }}
.tick {{ font-size: 11.5px; fill: var(--text-muted); font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
.axlab {{ font-size: 12px; fill: var(--text-secondary); }}
.b95 {{ fill: var(--band95); }}
.b80 {{ fill: var(--band80); }}
.fit {{ stroke: var(--c-model); stroke-width: 2.5; fill: none; }}
.fit.dash {{ stroke-dasharray: 6 5; }}
.obs {{ fill: var(--c-obs); stroke: var(--surface-2); stroke-width: 2; }}
.front {{ fill: none; stroke: var(--c-front); stroke-width: 2.2; }}
.diam {{ fill: var(--c-model); stroke: var(--surface-2); stroke-width: 1.5; }}
.tr-anth {{ stroke: var(--c-obs); stroke-width: 2; fill: none; opacity: .85; }}
.tr-front {{ stroke: var(--c-front); stroke-width: 2; fill: none; opacity: .85; }}
.target {{ stroke: var(--c-model); stroke-width: 1.6; stroke-dasharray: 5 5; }}
.dlab {{ font-size: 12px; fill: var(--text-secondary); font-weight: 600; }}
.dlab.proj {{ fill: var(--c-model); }}
.hit {{ fill: transparent; }}
.pt {{ cursor: default; outline: none; }}
.pt:hover .obs, .pt:focus .obs {{ stroke-width: 3; r: 6; }}
.pt:hover .front, .pt:focus .front {{ stroke-width: 3.4; }}
.pt:focus-visible .hit {{ stroke: var(--c-obs); stroke-width: 1.5; stroke-dasharray: 3 3; }}

#tip {{
  position: fixed; z-index: 10; pointer-events: none; visibility: hidden;
  background: var(--surface-1); color: var(--text-primary);
  border: 1px solid var(--border-strong); border-radius: 8px;
  padding: 8px 11px; font-size: 12.5px; line-height: 1.45; max-width: 300px;
  box-shadow: 0 4px 18px rgba(0,0,0,.14);
}}
#tip b {{ font-weight: 650; }}

.tblwrap {{ overflow-x: auto; margin: 10px 0 4px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13.5px; }}
th {{ text-align: left; font-size: 11px; letter-spacing: .06em; text-transform: uppercase; color: var(--text-muted); font-weight: 600; padding: 6px 12px 6px 0; border-bottom: 1px solid var(--border-strong); white-space: nowrap; }}
td {{ padding: 7px 12px 7px 0; border-bottom: 1px solid var(--border); font-variant-numeric: tabular-nums; white-space: nowrap; }}
tr.hl td {{ background: var(--band95); }}
tr.hl td:first-child {{ font-weight: 650; }}
details {{ margin: 14px 0; }}
summary {{ cursor: pointer; color: var(--text-secondary); font-size: 14px; }}
.caveats {{ max-width: 86ch; }}
.caveats li {{ margin: 7px 0; color: var(--text-secondary); }}
.caveats b {{ color: var(--text-primary); }}
footer {{ margin-top: 34px; padding-top: 14px; border-top: 1px solid var(--border); font-size: 12.5px; color: var(--text-muted); }}
@media (prefers-reduced-motion: no-preference) {{
  #tip {{ transition: opacity .12s; }}
}}
</style>

<div class="wrap">
<header>
  <h1>Revenue per ECI Point</h1>
  <p class="sub">Anthropic's annualized run-rate revenue, fitted against the
  <a href="https://epoch.ai/eci" rel="noopener">Epoch Capabilities Index</a> and
  <a href="https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/" rel="noopener">METR 50% time horizons</a>
  of its frontier models — then extended to ECI 170–195, assuming no compute bottlenecks.
  Data through <b>2026-08-16</b>, n&nbsp;=&nbsp;{obs} dated observations.</p>
</header>

<div class="tiles">
  <div class="tile"><div class="k">Fitted elasticity</div><div class="v">×4.4</div><div class="s">ARR per +10 ECI (95% CI ×3.1–×6.1) · R² 0.89</div></div>
  <div class="tile"><div class="k">ECI 170 → ARR</div><div class="v">{money(proj[0]['arr_central_b'])}</div><div class="s">80% PI {money(proj[0]['arr_pi80_b'][0])}–{money(proj[0]['arr_pi80_b'][1])} · ~{fdate(proj[0]['eta_anthropic_trend'])}</div></div>
  <div class="tile"><div class="k">ECI 180 → ARR</div><div class="v">{money(proj[2]['arr_central_b'])}</div><div class="s">80% PI {money(proj[2]['arr_pi80_b'][0])}–{money(proj[2]['arr_pi80_b'][1])} · ~{fdate(proj[2]['eta_anthropic_trend'])}</div></div>
  <div class="tile"><div class="k">ECI 190 → ARR</div><div class="v">{money(proj[4]['arr_central_b'])}</div><div class="s">80% PI {money(proj[4]['arr_pi80_b'][0])}–{money(proj[4]['arr_pi80_b'][1])} · ~{fdate(proj[4]['eta_anthropic_trend'])}</div></div>
</div>

<div class="callout"><b>Read this as trend arithmetic, not a forecast.</b>
Revenue, ECI and METR horizons all rose together 2024–2026; n&nbsp;=&nbsp;{obs} observations of one
company cannot separate "capability causes revenue" from "both ride time." Past
~$1T the extrapolation also assumes demand keeps absorbing supply — a
macroeconomic regime change, not a regression's domain of validity.</div>

<div class="card">
  <h2>ARR vs ECI — fit and extrapolation</h2>
  <p class="note">ln ARR = a + 0.1475·ECI. Each revenue observation is paired with the best Epoch-scored public Anthropic model at that date. Dashed = beyond observed range.</p>
  <div class="legend">
    <span><span class="sw" style="background:var(--c-obs)"></span>observed ARR (dated)</span>
    <span><span class="sw line" style="background:var(--c-model)"></span>fit</span>
    <span><span class="sw dash" style="border-color:var(--c-model)"></span>extrapolation</span>
    <span><span class="sw" style="background:var(--band80)"></span>80% PI</span>
    <span><span class="sw" style="background:var(--band95)"></span>95% PI</span>
    <span><span class="sw" style="background:var(--c-model);transform:rotate(45deg)"></span>projection at target ECI</span>
  </div>
  {chartA}
</div>

<div class="duo">
  <div class="card">
    <h2>When does ECI get there?</h2>
    <p class="note">Successive record-setters. Anthropic trend +14.3 pts/yr; cross-lab frontier +15.5 pts/yr (matches Epoch's published estimate).</p>
    <div class="legend">
      <span><span class="sw" style="background:var(--c-obs)"></span>Anthropic record</span>
      <span><span class="sw hollow" style="border-color:var(--c-front)"></span>cross-lab record</span>
      <span><span class="sw dash" style="border-color:var(--c-model)"></span>targets + ETA</span>
    </div>
    {chartB}
  </div>
  <div class="card">
    <h2>ECI ↔ METR horizon link</h2>
    <p class="note">Six Anthropic models measured on both. Near-collinear (r&nbsp;=&nbsp;0.97 in the revenue sample) — the two indices are one signal, so they are fitted separately, never jointly.</p>
    <div class="legend">
      <span><span class="sw" style="background:var(--c-obs)"></span>Anthropic model</span>
      <span><span class="sw line" style="background:var(--c-model)"></span>link fit</span>
    </div>
    {chartC}
  </div>
</div>

<div class="card">
  <h2>Projections</h2>
  <p class="note">ECI model with prediction intervals; METR model evaluated at each target's horizon-equivalent; ensemble = geometric mean. ETA from Anthropic / frontier ECI trends.</p>
  <div class="tblwrap">
  <table>
    <thead><tr><th>ECI</th><th>≈ METR horizon</th><th>ECI model</th><th>80% PI</th><th>95% PI</th><th>METR model</th><th>Ensemble</th><th>~When</th></tr></thead>
    <tbody>{proj_rows}</tbody>
  </table>
  </div>
</div>

<details>
  <summary>Observation table — all {obs} points with sources</summary>
  <div class="tblwrap">
  <table>
    <thead><tr><th>Date</th><th>ARR</th><th>ECI</th><th>METR 50% h</th><th>Confirmation</th><th>Source</th></tr></thead>
    <tbody>{obs_rows}</tbody>
  </table>
  </div>
  <p class="mini mut">Company-confirmed backbone: $1B → $5B → $9B → $14B → $30B → $47B. The Aug 2026 ~$70B point is tracker-sourced
  (FutureSearch: trackers "historically run hot"); refitting without it moves ECI 190 from $4.1T to $3.4T.</p>
</details>

<h2 style="font-size:16px;margin:26px 0 4px">What would make this wrong</h2>
<ol class="caveats">
  <li><b>Identification.</b> The time-only trend fits better (R² 0.983; ARR doubling ≈ 3.1 mo) than either capability model — revenue is diffusion on top of capability. These fits answer "if the historical revenue-per-capability elasticity persists," nothing stronger.</li>
  <li><b>Demand saturation.</b> $4T ARR ≈ 3× today's entire enterprise-software market. The 190s assume AI revenue substitutes for a meaningful share of the global wage bill — maybe what a 25-work-month METR horizon means, but far outside these intervals, which carry sampling uncertainty only.</li>
  <li><b>Compute assumed away, as posed.</b> Anthropic's 2026 growth was repeatedly described as compute-gated, so the fitted slope likely <i>understates</i> the unconstrained relationship — the one bias with a known sign.</li>
  <li><b>Specification.</b> Lagging capability 90 days roughly doubles the central estimates; dropping the tracker point trims ~15–20%. Spec choice moves the answer ~2×; the PIs already dwarf that.</li>
  <li><b>Measurement.</b> Run-rate ≠ GAAP revenue (one reported rival-memo challenge of ~$8B; independent estimates roughly corroborate the company figures). Epoch CIs are ±2–3 pts; METR CIs at the top span ~2×; the public Claude 5 family has no METR value yet, so the METR series tops out at Opus 4.6.</li>
  <li><b>ETA risk.</b> Dates assume the linear 14–15.5 pts/yr regime holds. A third-party breakpoint analysis of the restricted Mythos Preview argues for ~67 pts/yr; if that reaches public releases, ETAs compress 2–4×.</li>
</ol>

<footer>
  Generated {data['as_of']} · <code>python3 fit.py &amp;&amp; python3 make_page.py</code> ·
  every number sourced in <a href="https://github.com/timwein/Ai_roi_evidence/tree/main/analysis/anthropic-revenue-capability" rel="noopener">data.json</a> ·
  ECI: Epoch AI (public scale; anchors Claude 3.5 Sonnet = 130, GPT-5 = 150) · METR: Time Horizon 1.1 where available ·
  revenue: Anthropic announcements, Reuters, Bloomberg, CNBC, The Information, FutureSearch.
</footer>
</div>

<div id="tip" role="status"></div>
<script>
(function () {{
  var tip = document.getElementById('tip');
  function show(g) {{
    tip.innerHTML = g.getAttribute('data-tip');
    tip.style.visibility = 'visible';
    var r = g.getBoundingClientRect();
    var tw = tip.offsetWidth, th = tip.offsetHeight;
    var x = r.left + r.width / 2 - tw / 2;
    x = Math.max(8, Math.min(x, window.innerWidth - tw - 8));
    var y = r.top - th - 10;
    if (y < 8) y = r.bottom + 10;
    tip.style.left = x + 'px';
    tip.style.top = y + 'px';
  }}
  function hide() {{ tip.style.visibility = 'hidden'; }}
  document.querySelectorAll('.pt').forEach(function (g) {{
    g.addEventListener('mouseenter', function () {{ show(g); }});
    g.addEventListener('mouseleave', hide);
    g.addEventListener('focus', function () {{ show(g); }});
    g.addEventListener('blur', hide);
  }});
  window.addEventListener('scroll', hide, {{ passive: true }});
}})();
</script>
"""

(HERE / "index.html").write_text(html)
print(f"wrote index.html ({len(html):,} bytes)")
