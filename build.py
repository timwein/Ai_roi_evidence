#!/usr/bin/env python3
"""
Regenerate the AI ROI Evidence site from data/log.json.

Usage:  python3 build.py

Reads   data/log.json   (the single source of truth — append to this, never
                         hand-edit the HTML)
Writes  index.html      (running page, newest first, filterable)
        days/YYYY-MM-DD.html  (one permalink per logged day)

The daily agent run should: append to data/log.json, run this script, commit.
"""

import json
import html
import os
import re
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", "log.json")
DAYS_DIR = os.path.join(ROOT, "days")

# ---------------------------------------------------------------------------
# Shape metadata. Color follows the entity, never its rank, and the slot order
# is fixed. Slots 1-3 of the reference categorical palette validate all-pairs
# in both light and dark (worst CVD dE 9.2 light / 9.4 dark, normal-vision
# 24.0 / 20.9). Do not add a 4th hue: S3-CANDIDATE is S3's hue plus a dashed
# outline (composite encoding), not a new series color.
# Aqua sits below 3:1 on the light surface, so every shape marker ships a
# visible text label — the relief rule. Never let color carry meaning alone.
# ---------------------------------------------------------------------------
SHAPES = {
    "S3": {
        "label": "S3 — New TAM",
        "short": "S3",
        "light": "#2a78d6",
        "dark": "#3987e5",
        "blurb": "Demand that did not previously exist. GDP-additive, not share-shifting.",
    },
    "S3-CANDIDATE": {
        "label": "S3 candidate (unproven)",
        "short": "S3?",
        "light": "#2a78d6",
        "dark": "#3987e5",
        "blurb": "Looks like new TAM, but the counterfactual is not established by the source.",
    },
    "S2": {
        "label": "S2 — Share",
        "short": "S2",
        "light": "#eb6834",
        "dark": "#d95926",
        "blurb": "Revenue on existing products in existing segments. Zero-sum at industry level.",
    },
    "S1": {
        "label": "S1 — Velocity",
        "short": "S1",
        "light": "#1baf7a",
        "dark": "#199e70",
        "blurb": "Faster or higher-capacity inputs to revenue. A leading indicator, not realized ROI.",
    },
}

# ---------------------------------------------------------------------------
# Cost ledger. Added 2026-07-30. The revenue question (S1-S3) is the thesis;
# cost evidence is abundant, lower quality, and would drown it if pooled. So
# cost lives in a SEPARATE ledger with its own counts and its own section, and
# never enters the S1/S2/S3 totals.
#
# The four buckets are a 2x2 - sector (tech / non-tech) x function (software
# engineering / everything else) - not four unrelated categories. The whole
# point is the cell comparison: engineering-inside-tech is the easy, well
# documented cell, and non-engineering-outside-tech is where the bulk of the
# economy's labour cost actually sits.
#
# Deliberately ONE hue for all four, not four new series colors: the validated
# categorical palette carries three hues and adding four more would break the
# all-pairs CVD guarantee. The 2x2 cell is carried by TEXT (label + the cell
# line on every card), never by color. Cost uses a desaturated slate that reads
# as secondary against the three revenue hues - which is also the correct
# visual hierarchy, since this ledger is the supporting evidence, not the point.
# ---------------------------------------------------------------------------
COST_HUE = {"light": "#5c6672", "dark": "#8b95a3"}
COST_SHAPES = {
    "C1": ("Tech · engineering", "Cost saving inside a technology company, software engineering function."),
    "C2": ("Tech · non-engineering", "Cost saving inside a technology company, outside engineering - support, sales, marketing, G&A."),
    "C3": ("Non-tech · engineering", "Cost saving at a non-technology company, in its own software engineering function."),
    "C4": ("Non-tech · non-engineering", "Cost saving at a non-technology company, outside engineering. The cell that matters most and is hardest to evidence."),
}
for _k, (_cell, _blurb) in COST_SHAPES.items():
    SHAPES[_k] = {
        "label": f"{_k} — {_cell}",
        "short": _k,
        "cell": _cell,
        "light": COST_HUE["light"],
        "dark": COST_HUE["dark"],
        "blurb": _blurb,
    }

SHAPE_ORDER = ["S3", "S3-CANDIDATE", "S2", "S1"]
COST_ORDER = ["C1", "C2", "C3", "C4"]
ALL_ORDER = SHAPE_ORDER + COST_ORDER


def is_cost(shape):
    return shape in COST_SHAPES

STATUS_NOTE = {
    "DISCLOSED": "realized and reported",
    "ESTIMATED": "company's own internal attribution",
    "PROJECTED": "forward target, not a result",
}

TIER_NOTE = {
    "A": "Primary and accountable — filing, transcript, formal guidance",
    "B": "Company-issued, unaudited — press release, exec interview",
    "C": "Third-party reporting — journalism, trade press, sell-side",
    "D": "Vendor case study or consultant survey — lowest tier",
}


def esc(s):
    return html.escape(str(s if s is not None else ""))


def load():
    if not os.path.exists(DATA):
        return {"entries": [], "days": []}
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def norm_shape(s):
    s = (s or "").upper().strip()
    if s.startswith("S3-CAND") or s in ("S3 CANDIDATE", "S3?"):
        return "S3-CANDIDATE"
    return s if s in SHAPES else "S1"


def sort_key(e):
    return (e.get("date", ""), ALL_ORDER.index(norm_shape(e.get("shape"))))


def ledger_of(e):
    """revenue | appendix | cost. Cost is its own ledger regardless of scope."""
    if is_cost(norm_shape(e.get("shape"))):
        return "cost"
    return "appendix" if e.get("scope", "main") == "appendix" else "revenue"


# ---------------------------------------------------------------------------
# CSS. Roles as custom properties so light/dark swap in one place. Dark mode is
# selected from the dark steps of the same ramps, not an automatic flip, and is
# declared under both the media query and the data-theme scope so an explicit
# toggle wins either way.
# ---------------------------------------------------------------------------
def css():
    light_vars = "\n".join(
        f"  --shape-{k.lower()}: {v['light']};" for k, v in SHAPES.items()
    )
    dark_vars = "\n".join(
        f"    --shape-{k.lower()}: {v['dark']};" for k, v in SHAPES.items()
    )
    return f"""
:root {{
  color-scheme: light;
  --surface-1: #fcfcfb;
  --surface-2: #f4f3f0;
  --border: #dedcd6;
  --border-strong: #c3c1b9;
  --text-primary: #0b0b0b;
  --text-secondary: #52514e;
  --text-muted: #78766f;
  --good: #0ca30c;
  --critical: #d03b3b;
{light_vars}
}}
@media (prefers-color-scheme: dark) {{
  :root:where(:not([data-theme="light"])) {{
    color-scheme: dark;
    --surface-1: #1a1a19;
    --surface-2: #232322;
    --border: #383835;
    --border-strong: #4d4c48;
    --text-primary: #ffffff;
    --text-secondary: #c3c2b7;
    --text-muted: #99978d;
{dark_vars}
  }}
}}
:root[data-theme="dark"] {{
  color-scheme: dark;
  --surface-1: #1a1a19;
  --surface-2: #232322;
  --border: #383835;
  --border-strong: #4d4c48;
  --text-primary: #ffffff;
  --text-secondary: #c3c2b7;
  --text-muted: #99978d;
{dark_vars}
}}

* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--surface-1);
  color: var(--text-primary);
  font: 16px/1.6 ui-sans-serif, -apple-system, "Segoe UI", Inter, system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}}
.wrap {{ max-width: 1080px; margin: 0 auto; padding: 40px 24px 96px; }}
a {{ color: inherit; }}

header.masthead {{ border-bottom: 1px solid var(--border); padding-bottom: 28px; margin-bottom: 32px; }}
.eyebrow {{ font-size: 12px; letter-spacing: .09em; text-transform: uppercase; color: var(--text-muted); font-weight: 600; }}
h1 {{ font-size: clamp(26px, 4vw, 38px); line-height: 1.15; margin: 10px 0 12px; letter-spacing: -.02em; }}
.standfirst {{ color: var(--text-secondary); max-width: 68ch; margin: 0 0 18px; }}
.meta-row {{ display: flex; flex-wrap: wrap; gap: 8px 18px; font-size: 13px; color: var(--text-muted); align-items: center; }}
.btn {{
  font: inherit; font-size: 13px; padding: 5px 12px; border-radius: 999px;
  border: 1px solid var(--border-strong); background: var(--surface-1);
  color: var(--text-secondary); cursor: pointer;
}}
.btn:hover {{ border-color: var(--text-muted); color: var(--text-primary); }}

/* ---- stat tiles: a hero number needs no plot, so no hover layer here ---- */
.tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin: 0 0 14px; }}
.tile {{ background: var(--surface-2); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; }}
.tile .k {{ font-size: 11px; letter-spacing: .07em; text-transform: uppercase; color: var(--text-muted); font-weight: 600; display: flex; align-items: center; gap: 7px; }}
.tile .v {{ font-size: 30px; font-weight: 650; letter-spacing: -.02em; margin-top: 6px; font-variant-numeric: tabular-nums; }}
.tile .s {{ font-size: 12px; color: var(--text-muted); margin-top: 2px; }}
.swatch {{ width: 9px; height: 9px; border-radius: 2px; flex: none; }}
.swatch.hollow {{ background: transparent !important; border: 2px dashed currentColor; width: 10px; height: 10px; }}

.filters {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 24px 0 8px; align-items: center; }}
.filters .lab {{ font-size: 12px; text-transform: uppercase; letter-spacing: .07em; color: var(--text-muted); font-weight: 600; margin-right: 4px; }}
.chip {{
  font: inherit; font-size: 13px; padding: 5px 13px; border-radius: 999px; cursor: pointer;
  border: 1px solid var(--border-strong); background: var(--surface-1); color: var(--text-secondary);
  display: inline-flex; align-items: center; gap: 7px;
}}
.chip[aria-pressed="true"] {{ background: var(--text-primary); color: var(--surface-1); border-color: var(--text-primary); }}
.chip[aria-pressed="true"] .swatch.hollow {{ border-color: var(--surface-1); }}

.daygroup {{ margin-top: 34px; }}
.dayhead {{ display: flex; align-items: baseline; justify-content: space-between; gap: 12px; border-bottom: 1px solid var(--border); padding-bottom: 7px; margin-bottom: 16px; }}
.dayhead h2 {{ font-size: 15px; margin: 0; letter-spacing: .02em; font-variant-numeric: tabular-nums; }}
.dayhead .perma {{ font-size: 12px; color: var(--text-muted); text-decoration: none; }}
.dayhead .perma:hover {{ color: var(--text-primary); text-decoration: underline; }}

.card {{
  background: var(--surface-2); border: 1px solid var(--border);
  border-left: 3px solid var(--accent); border-radius: 10px;
  padding: 16px 18px; margin-bottom: 12px;
}}
.card.candidate {{ border-left-style: dashed; }}
.card.counter {{ border-left-color: var(--critical); }}
.card-top {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 8px; }}
.company {{ font-weight: 650; font-size: 17px; letter-spacing: -.01em; }}
.sector {{ font-size: 13px; color: var(--text-muted); }}
.tag {{
  font-size: 11px; font-weight: 650; letter-spacing: .05em; text-transform: uppercase;
  padding: 3px 8px; border-radius: 5px; border: 1px solid var(--border-strong);
  color: var(--text-secondary); background: var(--surface-1); display: inline-flex; align-items: center; gap: 6px;
}}
.tag.shape {{ border-color: var(--accent); }}
.tag.counter {{ border-color: var(--critical); color: var(--critical); }}
.claim {{ font-size: 16px; margin: 0 0 12px; }}
dl.fields {{ display: grid; grid-template-columns: 132px 1fr; gap: 5px 16px; margin: 0; font-size: 14px; }}
dl.fields dt {{ color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: .05em; font-weight: 600; padding-top: 3px; }}
dl.fields dd {{ margin: 0; color: var(--text-secondary); }}
dl.fields dd strong {{ color: var(--text-primary); font-weight: 600; }}
@media (max-width: 620px) {{ dl.fields {{ grid-template-columns: 1fr; gap: 1px 0; }} dl.fields dt {{ padding-top: 9px; }} }}

.assessment {{ background: var(--surface-2); border: 1px solid var(--border); border-radius: 10px; padding: 16px 20px 18px; margin-bottom: 12px; }}
.assessment h3 {{ font-size: 11px; text-transform: uppercase; letter-spacing: .08em; color: var(--text-muted); margin: 0 0 10px; }}
.assessment p {{ margin: 0 0 11px; color: var(--text-secondary); font-size: 15px; line-height: 1.62; }}
.assessment > *:last-child {{ margin-bottom: 0; }}
.assessment h4 {{
  font-size: 11.5px; text-transform: uppercase; letter-spacing: .07em; font-weight: 700;
  color: var(--text-muted); margin: 20px 0 8px; padding-top: 13px;
  border-top: 1px solid var(--border);
}}
.assessment h4:first-of-type {{ margin-top: 14px; }}
.assessment ul {{ margin: 0 0 11px; padding-left: 0; list-style: none; }}
.assessment li {{
  position: relative; margin: 0 0 8px; padding-left: 17px;
  color: var(--text-secondary); font-size: 15px; line-height: 1.58;
}}
.assessment li:last-child {{ margin-bottom: 0; }}
.assessment li::before {{
  content: ""; position: absolute; left: 3px; top: .62em;
  width: 5px; height: 5px; border-radius: 50%; background: var(--text-muted); opacity: .55;
}}
.assessment strong {{ color: var(--text-primary); font-weight: 650; }}
.assessment code {{
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .89em;
  background: var(--surface-1); border: 1px solid var(--border);
  border-radius: 4px; padding: 1px 5px; color: var(--text-primary);
  font-variant-numeric: tabular-nums; white-space: nowrap;
}}
.assessment .callout {{
  border-left: 3px solid var(--text-muted);
  background: var(--surface-1); border-radius: 0 7px 7px 0;
  padding: 11px 15px; margin: 0 0 13px;
  color: var(--text-primary); font-size: 15.5px; line-height: 1.55;
}}
.empty-note {{ color: var(--text-muted); font-style: italic; font-size: 15px; }}
.appendix-rule {{ margin: 26px 0 14px; padding: 9px 14px; border: 1px dashed var(--border-strong); border-radius: 8px; font-size: 13px; color: var(--text-muted); }}
.appendix-rule[data-ledger="cost"] {{ border-color: var(--shape-c4); border-left-width: 3px; border-left-style: solid; }}
.costmatrix {{ margin: 0 0 16px; }}
.costmatrix table {{ border-collapse: collapse; font-size: 13px; }}
.costmatrix caption {{ caption-side: top; text-align: left; color: var(--text-muted); font-size: 12px; padding-bottom: 7px; }}
.costmatrix th, .costmatrix td {{ border: 1px solid var(--border); padding: 8px 14px; text-align: left; }}
.costmatrix thead th {{ font-size: 11px; letter-spacing: .07em; text-transform: uppercase; color: var(--text-muted); }}
.costmatrix tbody th {{ font-weight: 550; color: var(--text-secondary); background: var(--surface-2); }}
.costmatrix .mv {{ font-size: 20px; font-weight: 650; font-variant-numeric: tabular-nums; }}
.costmatrix .mk {{ font-size: 11px; color: var(--shape-c4); font-weight: 650; letter-spacing: .04em; }}

table.tv {{ border-collapse: collapse; width: 100%; font-size: 13.5px; margin-top: 10px; }}
table.tv th, table.tv td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--border); vertical-align: top; }}
table.tv th {{ color: var(--text-muted); font-size: 11px; text-transform: uppercase; letter-spacing: .06em; }}
#tableview[hidden] {{ display: none; }}

footer {{ margin-top: 56px; padding-top: 20px; border-top: 1px solid var(--border); font-size: 13px; color: var(--text-muted); }}
footer a {{ color: var(--text-secondary); }}
.dayindex {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }}
.dayindex a {{ font-size: 12px; font-variant-numeric: tabular-nums; padding: 3px 9px; border: 1px solid var(--border); border-radius: 6px; text-decoration: none; color: var(--text-secondary); }}
.dayindex a:hover {{ border-color: var(--text-muted); color: var(--text-primary); }}
"""


def _inline(t):
    """Escape, then apply a tiny inline subset: **bold**, *italic*, `code`."""
    t = esc(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+?)`", r"<code>\1</code>", t)
    return t


def richtext(md):
    """Render the small markdown subset used by day assessments.

    Blocks are separated by blank lines:
      '## Heading'      -> section sub-heading
      '- item'          -> bullet list (continuation lines indent under the item)
      '> text'          -> callout box, for the one line that matters most
      anything else     -> paragraph
    Everything is escaped before any markup is introduced, so the JSON stays
    plain text and cannot inject HTML.
    """
    out = []
    for block in re.split(r"\n\s*\n", (md or "").strip()):
        lines = [l for l in block.strip().split("\n") if l.strip()]
        if not lines:
            continue
        if lines[0].lstrip().startswith("## "):
            out.append(f"<h4>{_inline(lines[0].lstrip()[3:].strip())}</h4>")
            rest = "\n".join(lines[1:]).strip()
            if rest:
                out.append(richtext(rest))
            continue
        if all(l.lstrip().startswith("> ") for l in lines):
            body = " ".join(l.lstrip()[2:].strip() for l in lines)
            out.append(f'<div class="callout">{_inline(body)}</div>')
            continue
        if lines[0].lstrip().startswith("- "):
            items = []
            for l in lines:
                s = l.strip()
                if s.startswith("- "):
                    items.append(s[2:].strip())
                elif items:
                    items[-1] += " " + s
            out.append(
                "<ul>" + "".join(f"<li>{_inline(i)}</li>" for i in items) + "</ul>"
            )
            continue
        out.append(f"<p>{_inline(' '.join(l.strip() for l in lines))}</p>")
    return "\n".join(out)


def shape_tag(shape):
    m = SHAPES[shape]
    hollow = " hollow" if shape == "S3-CANDIDATE" else ""
    return (
        f'<span class="tag shape"><span class="swatch{hollow}" '
        f'style="background:var(--shape-{shape.lower()});color:var(--shape-{shape.lower()})"></span>'
        f"{esc(m['label'])}</span>"
    )


def render_entry(e):
    shape = norm_shape(e.get("shape"))
    m = SHAPES[shape]
    classes = ["card"]
    if shape == "S3-CANDIDATE":
        classes.append("candidate")
    if e.get("counter_evidence"):
        classes.append("counter")

    src_bits = [b for b in [e.get("source_name"), e.get("source_date")] if b]
    src = esc(", ".join(src_bits)) or "source"
    if e.get("source_url"):
        src = f'<a href="{esc(e["source_url"])}" rel="noopener">{src}</a>'
    tier = (e.get("source_tier") or "").upper()

    status = (e.get("status") or "").upper()
    status_html = f"<strong>{esc(status)}</strong>"
    if status in STATUS_NOTE:
        status_html += f" — {STATUS_NOTE[status]}"

    rows = [
        ("Mechanism", esc(e.get("mechanism"))),
        ("Why this shape", esc(e.get("shape_justification"))),
        ("Status", status_html),
        (
            "Source",
            f"<strong>Tier {esc(tier)}</strong> — {TIER_NOTE.get(tier, '')}<br>{src}",
        ),
        ("Falsifier", esc(e.get("falsifier"))),
        (
            "Confidence",
            f"<strong>{esc((e.get('confidence') or '').lower())}</strong>"
            + (f" — {esc(e.get('confidence_why'))}" if e.get("confidence_why") else ""),
        ),
    ]
    fields = "".join(
        f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows if v and v.strip(" —")
    )

    counter = (
        '<span class="tag counter">⚠ Counter-evidence</span>'
        if e.get("counter_evidence")
        else ""
    )
    where = " · ".join(
        esc(x) for x in [e.get("sector"), e.get("country")] if x
    )

    return f"""<article class="{' '.join(classes)}" data-shape="{shape}"
  data-counter="{'1' if e.get('counter_evidence') else '0'}"
  data-scope="{esc(e.get('scope', 'main'))}"
  data-ledger="{ledger_of(e)}"
  style="--accent: var(--shape-{shape.lower()})">
  <div class="card-top">
    <span class="company">{esc(e.get('company'))}</span>
    <span class="sector">{where}</span>
    {shape_tag(shape)}{counter}
  </div>
  <p class="claim">{esc(e.get('claim'))}</p>
  <dl class="fields">{fields}</dl>
</article>"""


def render_day(day, entries):
    date = day.get("date")
    main = [e for e in entries if ledger_of(e) == "revenue"]
    appx = [e for e in entries if ledger_of(e) == "appendix"]
    cost = [e for e in entries if ledger_of(e) == "cost"]
    out = []
    if day.get("assessment"):
        out.append(
            f'<div class="assessment"><h3>Assessment</h3>'
            f'{richtext(day["assessment"])}</div>'
        )
    if not main:
        searched = day.get("searched") or []
        note = "No findings cleared the bar for the main revenue log."
        extra = []
        if appx:
            extra.append(
                f"{len(appx)} out-of-scope finding{'' if len(appx) == 1 else 's'} in the appendix"
            )
        if cost:
            extra.append(
                f"{len(cost)} in the cost ledger"
            )
        if extra:
            note += " " + " and ".join(extra) + " below."
        if searched:
            note += " Angles run: " + ", ".join(searched) + "."
        out.append(f'<p class="empty-note">{esc(note)}</p>')
    out += [render_entry(e) for e in main]
    if appx:
        out.append(
            '<div class="appendix-rule" data-ledger="appendix">Appendix — revenue findings of '
            "<em>any</em> shape whose subject is out of scope (software / AI-native). Kept visible "
            "so the S3 picture is not artificially empty and the incumbent-vs-entrant split stays "
            "measurable. <strong>Not counted in the revenue totals above.</strong></div>"
        )
        out += [render_entry(e) for e in appx]
    if cost:
        out.append(
            '<div class="appendix-rule" data-ledger="cost">Cost ledger — AI-attributed <em>cost</em> '
            "savings and productivity gains, on a 2×2 of sector (tech / non-tech) × function "
            "(software engineering / everything else). Tech subjects are in scope here, unlike the "
            "revenue log. <strong>A separate ledger: never counted in the S1–S3 revenue totals</strong>, "
            "because cost evidence is far more abundant than revenue evidence and pooling the two "
            "would bury the question this log exists to answer.</div>"
        )
        out += [render_entry(e) for e in cost]
    return "\n".join(out)


def counts(entries):
    """Revenue ledger only. Cost never enters these numbers."""
    rev = [e for e in entries if ledger_of(e) == "revenue"]
    c = Counter(norm_shape(e.get("shape")) for e in rev)
    appx = len([e for e in entries if ledger_of(e) == "appendix"])
    return c, len(rev), appx


def cost_counts(entries):
    cost = [e for e in entries if ledger_of(e) == "cost"]
    return Counter(norm_shape(e.get("shape")) for e in cost), len(cost)


def _tile(k, v, s, shape=None, hollow=False):
    sw = ""
    if shape:
        cls = "swatch hollow" if hollow else "swatch"
        sw = (
            f'<span class="{cls}" style="background:var(--shape-{shape.lower()});'
            f'color:var(--shape-{shape.lower()})"></span>'
        )
    return (
        f'<div class="tile"><div class="k">{sw}{esc(k)}</div>'
        f'<div class="v">{v}</div><div class="s">{esc(s)}</div></div>'
    )


def tiles_html(entries, days):
    c, total, appx = counts(entries)
    _, cost_total = cost_counts(entries)
    tiles = [
        _tile("Revenue findings", total, f"{appx} in appendix" if appx else "main log"),
        _tile("S3 — New TAM", c.get("S3", 0), "GDP-additive", "S3"),
        _tile("S3 candidates", c.get("S3-CANDIDATE", 0), "counterfactual unproven", "S3-CANDIDATE", True),
        _tile("S2 — Share", c.get("S2", 0), "zero-sum at industry level", "S2"),
        _tile("S1 — Velocity", c.get("S1", 0), "leading indicator", "S1"),
        _tile("Cost ledger", cost_total, "separate — not in revenue totals", "C4"),
        _tile("Days logged", len(days), f"{sum(1 for d in days if not d.get('entry_count'))} empty"),
    ]
    return '<div class="tiles">' + "".join(tiles) + "</div>"


def cost_matrix_html(entries):
    """The 2x2, rendered as a 2x2. Text carries the cell, never color alone."""
    cc, total = cost_counts(entries)
    if not total:
        return ""
    cells = [
        ("Software engineering", "C3", "C1"),
        ("Everything else", "C4", "C2"),
    ]
    rows = "".join(
        f"<tr><th scope=\"row\">{esc(fn)}</th>"
        f'<td><span class="mv">{cc.get(nontech, 0)}</span> <span class="mk">{nontech}</span></td>'
        f'<td><span class="mv">{cc.get(tech, 0)}</span> <span class="mk">{tech}</span></td></tr>'
        for fn, nontech, tech in cells
    )
    return (
        '<div class="costmatrix"><table><caption>Cost ledger — '
        f"{total} entr{'y' if total == 1 else 'ies'}, sector × function. "
        "Counted separately from the revenue log.</caption>"
        '<thead><tr><td></td><th scope="col">Non-tech</th><th scope="col">Tech</th></tr></thead>'
        f"<tbody>{rows}</tbody></table></div>"
    )


def table_view(entries):
    rows = []
    for e in sorted(entries, key=sort_key, reverse=True):
        sh = norm_shape(e.get("shape"))
        rows.append(
            "<tr>"
            f"<td>{esc(e.get('date'))}</td>"
            f"<td>{SHAPES[sh]['short']}</td>"
            f"<td>{esc(e.get('company'))}</td>"
            f"<td>{esc(e.get('sector'))}</td>"
            f"<td>{esc(e.get('claim'))}</td>"
            f"<td>{esc((e.get('status') or '').upper())}</td>"
            f"<td>{esc((e.get('source_tier') or '').upper())}</td>"
            f"<td>{esc((e.get('confidence') or '').lower())}</td>"
            "</tr>"
        )
    return (
        '<table class="tv"><thead><tr><th>Date</th><th>Shape</th><th>Company</th>'
        "<th>Sector</th><th>Claim</th><th>Status</th><th>Tier</th><th>Conf.</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
    )


SCRIPT = """
(function () {
  var root = document.documentElement;
  var tbtn = document.getElementById('themebtn');
  if (tbtn) tbtn.addEventListener('click', function () {
    var dark = getComputedStyle(root).getPropertyValue('color-scheme').trim() === 'dark';
    root.setAttribute('data-theme', dark ? 'light' : 'dark');
  });

  var vbtn = document.getElementById('viewbtn');
  var tv = document.getElementById('tableview');
  var cardsWrap = document.getElementById('cards');
  if (vbtn && tv && cardsWrap) vbtn.addEventListener('click', function () {
    var showTable = tv.hasAttribute('hidden');
    if (showTable) { tv.removeAttribute('hidden'); cardsWrap.setAttribute('hidden', ''); vbtn.textContent = 'Card view'; }
    else { tv.setAttribute('hidden', ''); cardsWrap.removeAttribute('hidden'); vbtn.textContent = 'Table view'; }
  });

  var chips = Array.prototype.slice.call(document.querySelectorAll('.chip[data-filter]'));
  function apply(f) {
    chips.forEach(function (c) { c.setAttribute('aria-pressed', String(c.dataset.filter === f)); });
    document.querySelectorAll('article.card').forEach(function (el) {
      var ok = f === 'all'
        || (f === 'counter' && el.dataset.counter === '1')
        || el.dataset.shape === f;
      el.style.display = ok ? '' : 'none';
    });
    document.querySelectorAll('.appendix-rule').forEach(function (r) {
      var sel = 'article.card[data-ledger="' + r.dataset.ledger + '"]';
      var any = false;
      var n = r.nextElementSibling;
      while (n && n.matches(sel)) {
        if (n.style.display !== 'none') { any = true; break; }
        n = n.nextElementSibling;
      }
      r.style.display = any ? '' : 'none';
    });
    document.querySelectorAll('.daygroup').forEach(function (g) {
      var any = Array.prototype.slice.call(g.querySelectorAll('article.card'))
        .some(function (el) { return el.style.display !== 'none'; });
      g.style.display = (f === 'all' || any) ? '' : 'none';
    });
  }
  chips.forEach(function (c) { c.addEventListener('click', function () { apply(c.dataset.filter); }); });
})();
"""


def page(title, body, depth=0):
    up = "../" * depth
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="A running log of verified evidence that non-software corporations are getting top-line revenue impact from AI.">
<style>{css()}</style>
</head>
<body>
<div class="wrap">
{body}
<footer>
  <p>Built from <code>data/log.json</code> by <code>build.py</code>. Method and inclusion bar:
  <a href="{up}METHOD.md">METHOD.md</a>. Every figure traces to a dated source; nothing is
  reconstructed from memory.</p>
</footer>
</div>
<script>{SCRIPT}</script>
</body>
</html>
"""


def build():
    log = load()
    entries = log.get("entries", [])
    days = log.get("days", [])

    by_date = {}
    for e in entries:
        by_date.setdefault(e.get("date"), []).append(e)

    known = {d.get("date") for d in days}
    for d in by_date:
        if d not in known:
            days.append({"date": d})
    for d in days:
        d["entry_count"] = len(
            [
                e
                for e in by_date.get(d.get("date"), [])
                if ledger_of(e) == "revenue"
            ]
        )
    days = sorted(days, key=lambda d: d.get("date", ""), reverse=True)

    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # ---- filter chips -----------------------------------------------------
    chips = ['<span class="lab">Filter</span>',
             '<button class="chip" data-filter="all" aria-pressed="true">All</button>']
    for s in SHAPE_ORDER:
        hollow = " hollow" if s == "S3-CANDIDATE" else ""
        chips.append(
            f'<button class="chip" data-filter="{s}" aria-pressed="false">'
            f'<span class="swatch{hollow}" style="background:var(--shape-{s.lower()});'
            f'color:var(--shape-{s.lower()})"></span>{esc(SHAPES[s]["label"])}</button>'
        )
    for s in COST_ORDER:
        chips.append(
            f'<button class="chip" data-filter="{s}" aria-pressed="false">'
            f'<span class="swatch" style="background:var(--shape-{s.lower()});'
            f'color:var(--shape-{s.lower()})"></span>{esc(SHAPES[s]["label"])}</button>'
        )
    chips.append(
        '<button class="chip" data-filter="counter" aria-pressed="false">⚠ Counter-evidence</button>'
    )

    groups = []
    for d in days:
        date = d.get("date")
        ents = sorted(by_date.get(date, []), key=sort_key)
        groups.append(
            f'<section class="daygroup" id="d{esc(date)}">'
            f'<div class="dayhead"><h2>{esc(date)}</h2>'
            f'<a class="perma" href="days/{esc(date)}.html">permalink →</a></div>'
            f"{render_day(d, ents)}</section>"
        )

    dayindex = "".join(
        f'<a href="days/{esc(d["date"])}.html">{esc(d["date"])}'
        + (f' · {d["entry_count"]}' if d.get("entry_count") else "")
        + "</a>"
        for d in days
    )

    legend = " ".join(
        f'{SHAPES[s]["short"]} = {esc(SHAPES[s]["blurb"])}'
        for s in ["S3", "S2", "S1"]
    )
    cost_legend = " · ".join(
        f'{s} = {esc(SHAPES[s]["cell"])}' for s in COST_ORDER
    )

    body = f"""
<header class="masthead">
  <div class="eyebrow">Running evidence log</div>
  <h1>Is AI creating new demand, or just moving revenue around?</h1>
  <p class="standfirst">Verified evidence that <strong>non-software</strong> corporations are getting
  <strong>top-line revenue</strong> impact from AI spend — sorted into three shapes. A second,
  separately counted <strong>cost ledger</strong> tracks AI-attributed cost savings on a 2×2 of
  sector × function, because that evidence arrives far more regularly and must not be allowed to
  stand in for the revenue question. Updated daily at 07:00 PT.</p>
  <div class="meta-row">
    <span>Last built {esc(updated)}</span>
    <button class="btn" id="themebtn" type="button">Toggle theme</button>
    <button class="btn" id="viewbtn" type="button">Table view</button>
  </div>
</header>

{tiles_html(entries, days)}
<p class="empty-note" style="font-size:13px">{legend}</p>
{cost_matrix_html(entries)}
<p class="empty-note" style="font-size:13px">{cost_legend}</p>

<div class="filters">{''.join(chips)}</div>

<div id="tableview" hidden>{table_view(entries)}</div>
<div id="cards">{''.join(groups)}</div>

<footer>
  <strong style="color:var(--text-secondary)">Every day logged</strong>
  <div class="dayindex">{dayindex}</div>
</footer>
"""
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page("AI ROI Evidence — Non-Tech Corporates", body))

    os.makedirs(DAYS_DIR, exist_ok=True)
    # Prune day pages whose date is no longer in the log, so the rendered site
    # can never assert a day the data does not contain.
    keep = {f"{d.get('date')}.html" for d in days}
    for stale in os.listdir(DAYS_DIR):
        if stale.endswith(".html") and stale not in keep:
            os.remove(os.path.join(DAYS_DIR, stale))
    for d in days:
        date = d.get("date")
        if not date or not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            continue
        ents = sorted(by_date.get(date, []), key=sort_key)
        dbody = f"""
<header class="masthead">
  <div class="eyebrow"><a href="../index.html">← All days</a></div>
  <h1>{esc(date)}</h1>
  <p class="standfirst">{len([e for e in ents if ledger_of(e)=='revenue'])}
  revenue finding(s) in the main log{
    ", " + str(len([e for e in ents if ledger_of(e)=='appendix'])) + " in the appendix"
    if any(ledger_of(e)=='appendix' for e in ents) else ""
  }{
    ", " + str(len([e for e in ents if ledger_of(e)=='cost'])) + " in the cost ledger"
    if any(ledger_of(e)=='cost' for e in ents) else ""
  }.</p>
</header>
{render_day(d, ents)}
"""
        with open(os.path.join(DAYS_DIR, f"{date}.html"), "w", encoding="utf-8") as f:
            f.write(page(f"{date} — AI ROI Evidence", dbody, depth=1))

    log["days"] = days
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

    c, total, appx = counts(entries)
    cc, cost_total = cost_counts(entries)
    print(
        f"built · {total} revenue findings ({appx} appendix) · {len(days)} days · "
        f"S3={c.get('S3',0)} S3?={c.get('S3-CANDIDATE',0)} S2={c.get('S2',0)} S1={c.get('S1',0)}"
        f" · cost ledger {cost_total} · "
        + " ".join(f"{k}={cc.get(k,0)}" for k in COST_ORDER)
    )


if __name__ == "__main__":
    build()
