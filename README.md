# AI ROI Evidence — Non-Tech Corporates

A running log of verified evidence that **non-software** corporations are getting
**top-line revenue** impact from AI spend, sorted into three shapes. Updated
daily at 07:00 PT by a scheduled agent run.

Live site: `https://timwein.github.io/Ai_roi_evidence/`

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
| `shape` | **Revenue:** `S3` · `S3-CANDIDATE` · `S2` · `S1` — **Cost:** `C1` · `C2` · `C3` · `C4` |
| `scope` | `main` · `appendix` (out-of-scope subject — software / AI-native — at **any** revenue shape; never counted in totals). Cost entries are always `main`; the cost ledger is separated by shape, not by scope. |
| `status` | `DISCLOSED` · `ESTIMATED` · `PROJECTED` |
| `source_tier` | `A` · `B` · `C` · `D` |
| `confidence` | `high` · `medium` · `low` · `speculative` |

### The two ledgers

`S1`–`S3` answer the question the site asks: is AI producing **top-line
revenue** at non-tech incumbents. `C1`–`C4` are a **separate ledger** of
AI-attributed **cost** savings, on a 2×2 of sector × function:

| | Non-tech | Tech |
|---|---|---|
| **Software engineering** | `C3` | `C1` |
| **Everything else** | `C4` | `C2` |

Cost entries are **never counted in the revenue totals** and are rendered in
their own section under a marked rule. Technology companies are in scope for the
cost ledger and out of scope for the revenue log. A single disclosure is logged
in exactly one ledger — see METHOD.md for why, and for the standing traps
(adoption-dressed-as-saving, composite "value" metrics, headcount with many
parents, the run-cost offset).

Days with no qualifying findings still get a record:

```json
{ "date": "2026-07-28", "searched": ["angle", "angle"], "assessment": "Why nothing cleared the bar." }
```

## Assessment formatting

`assessment` is the one long field on the page, so it is rendered through a
small markdown subset instead of as a single paragraph. **Write it structured —
a wall of text is not acceptable output.** Blocks are separated by blank lines:

| Markup | Renders as |
|---|---|
| `## Heading` | Section sub-heading with a rule above it |
| `- item` | Bullet list (wrapped continuation lines indent under the item) |
| `> text` | Callout box — use for the single line that matters most |
| plain text | Paragraph |
| `**bold**` · `*italic*` · `` `code` `` | Inline emphasis; `code` for figures (`$419m`, `19.5%`) |

Everything is HTML-escaped before markup is applied, so the JSON stays plain
text and cannot inject markup. Shape of a good assessment:

1. A `>` callout stating the day's verdict in one sentence — including whether
   any S3 appeared.
2. `## Sources read` — one bullet per company, **name bolded**, the number in
   backticks, and what was or was not attributed.
3. A `>` callout naming the pattern, if one is visible across runs.
4. `## Near-misses deliberately not logged` — one bullet each with the reason
   it failed a specific test. This is where the method does its visible work.
5. `## Nearest dated catalysts` — bullets, so the next run knows what to check.

## Design notes

Shape colors are the first three slots of a categorical palette validated for
colorblind separation on all pairs in both light and dark mode (worst CVD ΔE 9.2
light / 9.4 dark). `S3-CANDIDATE` is deliberately **not** a fourth hue — it is
S3's hue with a dashed outline, so an unproven claim can never be mistaken for a
confirmed one by color alone. Every shape marker carries a visible text label;
color never carries meaning unaided.
