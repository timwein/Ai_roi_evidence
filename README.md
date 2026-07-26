# AI ROI Evidence — Non-Tech Corporates

A running log of verified evidence that **non-software** corporations are getting
**top-line revenue** impact from AI spend, sorted into three shapes. Updated
daily at 07:00 PT by a scheduled agent run.

Live site: `https://<user>.github.io/ai_roi_evidence/`

See **[METHOD.md](METHOD.md)** for scope, the three shapes, the inclusion bar,
source tiers, and the standing skepticism rules. That file is authoritative.

## How it works

```
data/log.json   ← single source of truth. Append here, never hand-edit HTML.
build.py        ← regenerates the whole site from log.json
index.html      ← running page: stat tiles, shape filters, newest-first
days/*.html     ← one permalink per logged day
```

The daily run: reads `METHOD.md` → reads `data/log.json` to dedupe → searches →
appends new entries → runs `python3 build.py` → commits → pushes. GitHub Pages
serves the result. Git history doubles as an audit trail: if an entry is ever
revised, the diff shows it.

Rebuild locally:

```bash
python3 build.py
```

No dependencies beyond the Python standard library.

## Entry schema

```json
{
  "date": "2026-07-27",
  "company": "Acme Industrial",
  "sector": "Industrials",
  "country": "US",
  "shape": "S3",
  "scope": "main",
  "claim": "One sentence, with the number.",
  "status": "DISCLOSED",
  "source_tier": "A",
  "source_name": "Q2 2026 earnings call",
  "source_date": "2026-07-24",
  "source_url": "https://...",
  "mechanism": "How the AI actually produces the revenue. Be concrete.",
  "shape_justification": "For S3, answer tests (a)-(d). For S2, name who lost the sale. For S1, state whether revenue conversion was also disclosed or conspicuously absent.",
  "falsifier": "The specific thing that, if absent from a later quarter, means this was narrative rather than result.",
  "confidence": "medium",
  "confidence_why": "One line.",
  "counter_evidence": false
}
```

| Field | Values |
|---|---|
| `shape` | `S3` · `S3-CANDIDATE` · `S2` · `S1` |
| `scope` | `main` · `appendix` (out-of-scope S3 subject; never counted in totals) |
| `status` | `DISCLOSED` · `ESTIMATED` · `PROJECTED` |
| `source_tier` | `A` · `B` · `C` · `D` |
| `confidence` | `high` · `medium` · `low` · `speculative` |

Days with no qualifying findings still get a record:

```json
{ "date": "2026-07-28", "searched": ["angle", "angle"], "assessment": "Why nothing cleared the bar." }
```

## Design notes

Shape colors are the first three slots of a categorical palette validated for
colorblind separation on all pairs in both light and dark mode (worst CVD ΔE 9.2
light / 9.4 dark). `S3-CANDIDATE` is deliberately **not** a fourth hue — it is
S3's hue with a dashed outline, so an unproven claim can never be mistaken for a
confirmed one by color alone. Every shape marker carries a visible text label;
color never carries meaning unaided.
