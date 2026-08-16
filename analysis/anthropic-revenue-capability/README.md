# Anthropic revenue vs. capability (ECI / METR)

**Question.** If Anthropic's revenue has tracked frontier-model capability so far,
what does the trend imply for annualized revenue when the [Epoch Capabilities
Index](https://epoch.ai/eci) reaches the 170s, 180s, 190s — assuming no compute
bottlenecks?

**Answer, in one table** (annualized run-rate revenue, central estimates; fitted
on data through 2026-08-16):

| ECI | central (ECI model) | 80% PI | plausible range across specs | ~when, current trends |
|---|---|---|---|---|
| **170** | **$217B** | $96B–$488B | $190B–$460B | Jan–Mar 2027 |
| 175 | $453B | $189B–$1.1T | $0.4T–$0.9T | Apr–Jul 2027 |
| **180** | **$948B** | $366B–$2.5T | $0.8T–$2.1T | Aug–Nov 2027 |
| 185 | $2.0T | $707B–$5.6T | $1.7T–$5.1T | Dec 2027–Apr 2028 |
| **190** | **$4.1T** | $1.4T–$12.6T | $3.4T–$12.9T | Apr–Aug 2028 |
| 195 | $8.7T | $2.6T–$28.8T | $7T–$33T | Aug–Dec 2028 |

"Plausible range across specs" spans the central estimates of the alternative
specifications in [Sensitivity](#sensitivity--cross-checks) (no-tracker, 90-day
lag, METR model, time-trend cross-check) — a better honesty band than any single
model's prediction interval. **Treat everything past ~$1T as trend arithmetic,
not a forecast** — see [Caveats](#caveats), especially demand saturation.

Everything here regenerates from two files: `data.json` (every observation, with
sources) and `fit.py` (stdlib-only OLS). Run `python3 fit.py`.

## Data

Three series, assembled 2026-08-16, every point sourced in `data.json`:

1. **Revenue** — 14 dated annualized run-rate observations, 2023-09 → 2026-08.
   The backbone is company-confirmed: $1B (end-2024), $5B (Aug 2025), $9B
   (end-2025), $14B (Feb 2026, Series G), $30B (Apr 2026), $47B (mid-May 2026,
   Series H). The most recent point (~$70B, Aug 2026) is tracker-sourced, not
   company-confirmed, and is tested in sensitivity. Excluded (with reasons, in
   the data file): a duplicate restatement, one noisier tracker point, and
   pre-2026 projections that actuals passed in Q1 2026.
2. **ECI** — Epoch's public-scale Capabilities Index (anchors: Claude 3.5
   Sonnet = 130, GPT-5 = 150) for Anthropic's successive frontier models:
   Claude 3 Opus 128 → 3.5 Sonnet 130 → 3.7 Sonnet 141.5 → Opus 4.1 144 →
   Opus 4.5 149.5 → Opus 4.6 155 → Fable 5 161 (June 2026, current all-time
   high; Opus 5 sits at 159). Anthropic's internal "AECI" fork (Mythos figures
   174/181) is a different scale and excluded.
3. **METR 50% time horizons** — Time Horizon 1.1 where available: Claude 3 Opus
   7 min → 3.5 Sonnet 11 min → 3.7 Sonnet 60 min → Opus 4 100 min → Opus 4.5
   293 min → Opus 4.6 719 min. The public Claude 5 family had no METR
   measurement as of 2026-08-16, so METR pairing tops out at Opus 4.6.

Each revenue observation is paired with the best value among Anthropic models
**publicly released by that date** (restricted-access models excluded). The
2023 revenue point predates both indices and drops out, leaving **n = 13**.

## Models

Revenue is exponential-ish in time; ECI is ~linear in time; METR horizon is
~exponential in time. So the natural single-variable specifications are:

| model | fit | R² | reading |
|---|---|---|---|
| ln ARR = a + b·ECI | b = 0.1475 ± 0.0155 | 0.892 | **×4.4 per +10 ECI** (95% CI ×3.1–×6.1) |
| ln ARR = a + b·log2(METR h) | b = 0.713 ± 0.077 | 0.887 | ×2.04 per horizon doubling |
| ln ARR = a + b·t | — | 0.983 | ARR doubles every 3.1 months |
| Anthropic frontier ECI vs t | +14.3 pts/yr | 0.978 | ETA driver |
| Cross-lab frontier ECI vs t (post-2024) | +15.5 pts/yr | 0.987 | matches Epoch's own 15.5 |
| log2(METR h) = a + b·ECI | b = 0.243 | 0.997 | horizon doubles per 4.1 ECI pts |

ECI and log2(horizon) are 0.97-correlated in this sample — they are close to the
same variable measured twice, so a joint two-regressor fit is not identifiable
at n = 13 and is deliberately not reported. The two single-variable models plus
their geometric-mean ensemble are the honest version.

**External validation.** Three fitted quantities land on independently published
values: the cross-lab frontier slope (15.5 pts/yr vs Epoch's published ~15.5),
the ECI-per-horizon-doubling link (4.1 pts vs Epoch's stated ~5), and the
implied METR doubling time (3.5 months vs METR's published post-2024 estimate of
~89–105 days). The moving parts of this analysis agree with the primary sources'
own trend fits.

## Projections

From the ECI model, with the METR model evaluated at each target's
horizon-equivalent (via the link fit), and the time-trend model evaluated at the
date the Anthropic ECI trend reaches the target:

| ECI | METR-equiv horizon | ECI model | METR model | ensemble | time-trend at ETA | ETA (Anthropic / frontier trend) |
|---|---|---|---|---|---|---|
| 170 | ~140 h (~3½ wk) | $217B | $376B | $285B | $319B | 2027-03 / 2027-01 |
| 175 | ~330 h (~8 wk) | $453B | $893B | $636B | $808B | 2027-07 / 2027-04 |
| 180 | ~770 h (~19 wk) | $948B | $2.1T | $1.4T | $2.0T | 2027-11 / 2027-08 |
| 185 | ~1,800 h (~44 wk) | $2.0T | $5.0T | $3.2T | $5.1T | 2028-04 / 2027-12 |
| 190 | ~25 work-months | $4.1T | $12.0T | $7.0T | $12.9T | 2028-08 / 2028-04 |
| 195 | ~57 work-months | $8.7T | $28.5T | $15.7T | $32.6T | 2028-12 / 2028-08 |

The ECI model is the most conservative of the four because revenue kept
compounding *within* each capability plateau (ECI 155 alone spans $14B → $47B,
Feb–May 2026), and the ECI regression averages over that diffusion; the pure
time trend inherits all of it. Reading: **ECI ~170 lands around $200–450B; the
180s around $1–2T; the 190s around $4–13T** — with the caveats below doing real
work by the 180s.

## Sensitivity — cross-checks

- **Drop the tracker point** (the only non-company/major-press observation,
  ~$70B Aug 2026): slope 0.1432 vs 0.1475; ECI 170 → $193B, 180 → $806B,
  190 → $3.4T. Direction: modestly lower.
- **Lag capability 90 days** (revenue responds to releases with delay): slope
  0.1498, but predictions roughly double (170 → $464B, 190 → $9.3T), because
  the same revenue attaches to lower contemporaneous ECI. Specification choice
  moves central estimates ~2×; the prediction intervals already dwarf this.
- **METR model vs ECI model**: METR-side estimates run ~2–3× higher, partly
  because Claude 5-family models are unmeasured and the METR series tops out at
  Opus 4.6 — the METR slope absorbs mid-2026 revenue growth against a stale
  capability value.

## Caveats

1. **Correlation, not causation.** Revenue, ECI, and METR horizons all grew
   monotonically 2024–2026. n = 13 dated observations of one company cannot
   separate "capability causes revenue" from "both ride time." The time-only
   model fits *better* (R² 0.983) than either capability model — consistent
   with revenue being adoption/diffusion-driven on top of capability. The
   capability regressions are best read as: *if* the historical
   revenue-per-capability elasticity persists, then ECI X ↦ revenue Y.
2. **Demand-side saturation is assumed away.** $4T ARR (ECI 190, central)
   is roughly triple the entire current global enterprise-software market and a
   few percent of world GDP. Extrapolations past ~$1T implicitly assume AI
   revenue stops being a software line item and starts substituting for a
   meaningful share of the global wage bill — possibly what a 25-work-month
   METR horizon means, but that is a macroeconomic regime change, not a
   regression's domain of validity. The intervals reported are sampling
   uncertainty only; regime risk is not in them.
3. **Compute is assumed unconstrained — as posed.** The question says "assuming
   no compute bottlenecks." Note the sign of the bias this buys: Anthropic's
   2026 growth was repeatedly described (by the company and its coverage) as
   compute-gated, so the fitted slope is, if anything, a supply-constrained
   *understatement* of the unconstrained capability→revenue relationship.
4. **Run-rate ≠ GAAP revenue.** Milestones are annualized month-run-rates,
   the metric Anthropic itself publicizes. One reported challenge (an OpenAI
   executive memo, Apr 2026) claimed ~$8B of overstatement; The Information's
   independent late-May estimate (~$45B vs the company's $47B) roughly
   corroborated the company figure. Competitive-dynamics risk (pricing, share)
   is likewise outside the model.
5. **Extrapolation reach.** Observed ECI range is 130–161; ECI 190 is ~2×
   further from the sample mean than the widest observed deviation. Prediction
   intervals widen accordingly, and they are honest about *statistical*
   uncertainty only (see 1–2 for the rest). METR horizons past ~16 h are
   already at the edge of what METR says it can measure; the horizon
   equivalents quoted for ECI ≥ 180 are pure link-model extrapolation.
6. **Measurement error in the regressors.** Epoch's 90% CIs are ±2–3 ECI
   points per model; METR's CIs at the top end span ~2× either way. Neither is
   propagated (errors-in-variables would flatten the slope slightly — another
   reason these are lower bounds on steepness).
7. **ETA uncertainty.** Dates assume the linear 14.3–15.5 pts/yr ECI trend
   holds. A third-party analysis of the (restricted) Mythos Preview argues for
   a post-Opus-4.6 breakpoint at ~67 pts/yr; if anything like that holds for
   *public* releases, the ETAs above are 2–4× too far out. Not modeled;
   recorded in `data.json` as a scenario.

## Files

- `data.json` — every observation with source, URL, and exclusions (with reasons)
- `fit.py` — the fits, prediction intervals, projections (`python3 fit.py`)
- `results.json` — generated output
- `index.html` — self-contained chart page
