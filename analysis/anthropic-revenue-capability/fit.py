#!/usr/bin/env python3
"""Fit Anthropic revenue run-rate against capability indices (Epoch ECI, METR
50% time horizon) and extrapolate to ECI 170/180/190.

Stdlib only, like the rest of this repo. Reads data.json, writes results.json,
prints a markdown summary.

Model choices, stated up front:
- Revenue is exponential-ish in time; ECI is ~linear in time; METR horizon is
  ~exponential in time (so log2(horizon) is ~linear in time). Therefore the
  natural specifications are  ln(ARR) = a + b*ECI  and  ln(ARR) = a + b*log2(h).
- Each revenue observation is paired with the best (max) capability value among
  Anthropic models released on or before that date ("best-to-date" step
  function), optionally lagged.
- ECI and log2(horizon) are near-collinear (both ~linear in time), so a joint
  two-regressor fit is not identifiable with this sample size. We fit the two
  single-variable models and also report a simple ensemble (geometric mean of
  the two central predictions), rather than pretending to separate them.
"""

import json
import math
import datetime as dt
from pathlib import Path

HERE = Path(__file__).parent
EPOCH0 = dt.date(2024, 1, 1)  # time origin for the time-trend fits


def d(s):
    return dt.date.fromisoformat(s)


def years_since(date, origin=EPOCH0):
    return (date - origin).days / 365.25


# ---------------------------------------------------------------- OLS helpers

# Two-sided Student-t critical values by dof (columns: 95% CI -> q=0.975,
# 80% CI -> q=0.90). Linear interpolation between tabulated dofs.
T_TABLE = {
    0.975: {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447,
            7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 12: 2.179, 14: 2.145,
            16: 2.120, 20: 2.086, 25: 2.060, 30: 2.042, 60: 2.000, 1000: 1.962},
    0.90:  {1: 3.078, 2: 1.886, 3: 1.638, 4: 1.533, 5: 1.476, 6: 1.440,
            7: 1.415, 8: 1.397, 9: 1.383, 10: 1.372, 12: 1.356, 14: 1.345,
            16: 1.337, 20: 1.325, 25: 1.316, 30: 1.310, 60: 1.296, 1000: 1.282},
}


def t_crit(dof, q):
    tab = T_TABLE[q]
    keys = sorted(tab)
    if dof <= keys[0]:
        return tab[keys[0]]
    if dof >= keys[-1]:
        return tab[keys[-1]]
    for lo, hi in zip(keys, keys[1:]):
        if lo <= dof <= hi:
            w = (dof - lo) / (hi - lo)
            return tab[lo] * (1 - w) + tab[hi] * w


class OLS:
    """Simple-regression y = a + b*x with prediction intervals."""

    def __init__(self, x, y):
        assert len(x) == len(y) >= 3, "need at least 3 points"
        self.n = n = len(x)
        self.x, self.y = list(x), list(y)
        xbar = sum(x) / n
        ybar = sum(y) / n
        sxx = sum((xi - xbar) ** 2 for xi in x)
        sxy = sum((xi - xbar) * (yi - ybar) for xi, yi in zip(x, y))
        self.b = sxy / sxx
        self.a = ybar - self.b * xbar
        self.xbar, self.sxx = xbar, sxx
        resid = [yi - (self.a + self.b * xi) for xi, yi in zip(x, y)]
        sse = sum(r * r for r in resid)
        sst = sum((yi - ybar) ** 2 for yi in y)
        self.r2 = 1 - sse / sst if sst > 0 else float("nan")
        self.dof = n - 2
        self.s = math.sqrt(sse / self.dof) if self.dof > 0 else float("nan")
        self.se_b = self.s / math.sqrt(sxx)

    def predict(self, x0):
        return self.a + self.b * x0

    def pi(self, x0, q):
        """(lo, hi) prediction interval for a new observation at x0."""
        se = self.s * math.sqrt(1 + 1 / self.n + (x0 - self.xbar) ** 2 / self.sxx)
        t = t_crit(self.dof, q)
        m = self.predict(x0)
        return m - t * se, m + t * se

    def solve_x(self, y0):
        return (y0 - self.a) / self.b

    def summary(self):
        return {"a": self.a, "b": self.b, "se_b": self.se_b, "r2": self.r2,
                "n": self.n, "resid_std": self.s}


def corr(x, y):
    n = len(x)
    xb, yb = sum(x) / n, sum(y) / n
    num = sum((a - xb) * (b - yb) for a, b in zip(x, y))
    den = math.sqrt(sum((a - xb) ** 2 for a in x) * sum((b - yb) ** 2 for b in y))
    return num / den


# ---------------------------------------------------------------- data prep

def best_to_date(models, key, date, lag_days=0):
    """Max capability value among models released <= date - lag."""
    cutoff = date - dt.timedelta(days=lag_days)
    vals = [m[key] for m in models
            if m.get(key) is not None and d(m["release_date"]) <= cutoff]
    return max(vals) if vals else None


def build_pairs(data, lag_days=0):
    models = data["anthropic_capability"]
    rows = []
    for p in data["revenue_points"]:
        if p["kind"] == "projection":
            continue
        date = d(p["date"])
        eci = best_to_date(models, "eci", date, lag_days)
        h = best_to_date(models, "metr_p50_minutes", date, lag_days)
        rows.append({"date": p["date"], "arr": p["arr_usd_b"], "eci": eci,
                     "metr_min": h, "t": years_since(date)})
    return rows


def fmt_b(x):
    if x >= 1000:
        return f"${x/1000:,.1f}T"
    if x >= 100:
        return f"${x:,.0f}B"
    return f"${x:,.1f}B"


def fmt_h(minutes):
    if minutes < 60:
        return f"{minutes:.0f} min"
    hours = minutes / 60
    if hours < 200:
        return f"{hours:,.0f} h"
    return f"{hours/167:,.0f} work-months" if hours >= 2000 else f"{hours:,.0f} h ({hours/40:,.0f} wk)"


# ---------------------------------------------------------------- main

def main():
    data = json.loads((HERE / "data.json").read_text())
    targets = data["targets_eci"]

    rows = build_pairs(data)
    used = [r for r in rows if r["eci"] is not None and r["metr_min"] is not None]
    dropped = [r for r in rows if r not in used]

    ln_arr = [math.log(r["arr"]) for r in used]
    eci = [r["eci"] for r in used]
    l2h = [math.log2(r["metr_min"]) for r in used]
    tt = [r["t"] for r in used]

    m_eci = OLS(eci, ln_arr)
    m_metr = OLS(l2h, ln_arr)
    m_time = OLS(tt, ln_arr)

    # Capability-vs-time trends (Anthropic best-to-date at each revenue date is
    # a step function; fit on the underlying model series instead).
    cap = [m for m in data["anthropic_capability"] if m.get("eci") is not None]
    cap_t = [years_since(d(m["release_date"])) for m in cap]
    m_eci_time = OLS(cap_t, [m["eci"] for m in cap])

    fr = data.get("frontier_eci", [])
    m_frontier_time = None
    if len(fr) >= 3:
        m_frontier_time = OLS([years_since(d(m["release_date"])) for m in fr],
                              [m["eci"] for m in fr])

    # ECI <-> log2(horizon) link, on Anthropic models with both measurements.
    both = [m for m in data["anthropic_capability"]
            if m.get("eci") is not None and m.get("metr_p50_minutes") is not None]
    link = OLS([m["eci"] for m in both],
               [math.log2(m["metr_p50_minutes"]) for m in both])

    # Sensitivity: pair revenue with capability lagged 90 days.
    rows_lag = [r for r in build_pairs(data, lag_days=90)
                if r["eci"] is not None and r["metr_min"] is not None]
    m_eci_lag = OLS([r["eci"] for r in rows_lag],
                    [math.log(r["arr"]) for r in rows_lag])

    # ------------------------------------------------------------ projections
    proj = []
    for T in targets:
        e_c = math.exp(m_eci.predict(T))
        e_lo95, e_hi95 = (math.exp(v) for v in m_eci.pi(T, 0.975))
        e_lo80, e_hi80 = (math.exp(v) for v in m_eci.pi(T, 0.90))
        h_eq = 2 ** link.predict(T)                    # horizon equivalent
        mtr_c = math.exp(m_metr.predict(math.log2(h_eq)))
        mtr_lo95, mtr_hi95 = (math.exp(v) for v in m_metr.pi(math.log2(h_eq), 0.975))
        ens = math.sqrt(e_c * mtr_c)                   # geometric mean
        when = EPOCH0 + dt.timedelta(days=365.25 * m_eci_time.solve_x(T))
        when_fr = None
        if m_frontier_time:
            when_fr = EPOCH0 + dt.timedelta(days=365.25 * m_frontier_time.solve_x(T))
        arr_at_when = math.exp(m_time.predict(years_since(when)))
        proj.append({
            "eci": T,
            "arr_central_b": e_c,
            "arr_pi80_b": [e_lo80, e_hi80],
            "arr_pi95_b": [e_lo95, e_hi95],
            "metr_equiv_p50_minutes": h_eq,
            "arr_via_metr_b": mtr_c,
            "arr_via_metr_pi95_b": [mtr_lo95, mtr_hi95],
            "arr_ensemble_b": ens,
            "eta_anthropic_trend": when.isoformat(),
            "eta_frontier_trend": when_fr.isoformat() if when_fr else None,
            "arr_time_trend_at_eta_b": arr_at_when,
        })

    results = {
        "generated": data.get("as_of"),
        "n_obs": len(used),
        "obs": used,
        "dropped_obs": dropped,
        "models": {
            "ln_arr_vs_eci": m_eci.summary(),
            "ln_arr_vs_log2_metr": m_metr.summary(),
            "ln_arr_vs_time": m_time.summary(),
            "eci_vs_time_anthropic": m_eci_time.summary(),
            "eci_vs_time_frontier": m_frontier_time.summary() if m_frontier_time else None,
            "log2_metr_vs_eci_link": link.summary(),
            "ln_arr_vs_eci_lag90d": m_eci_lag.summary(),
        },
        "collinearity_corr_eci_log2metr": corr(eci, l2h),
        "derived": {
            "arr_multiplier_per_10_eci": math.exp(10 * m_eci.b),
            "arr_multiplier_per_10_eci_pi95": [
                math.exp(10 * (m_eci.b - t_crit(m_eci.dof, 0.975) * m_eci.se_b)),
                math.exp(10 * (m_eci.b + t_crit(m_eci.dof, 0.975) * m_eci.se_b))],
            "arr_multiplier_per_horizon_doubling": math.exp(m_metr.b),
            "arr_doubling_time_months": 12 * math.log(2) / m_time.b,
            "eci_points_per_year_anthropic": m_eci_time.b,
            "eci_points_per_year_frontier": m_frontier_time.b if m_frontier_time else None,
            "metr_doubling_months_implied": 12 / (m_eci_time.b * link.b),
        },
        "projections": proj,
    }
    (HERE / "results.json").write_text(json.dumps(results, indent=2) + "\n")

    # ------------------------------------------------------------ report
    p = print
    p(f"n = {len(used)} revenue observations "
      f"({used[0]['date']} … {used[-1]['date']}), "
      f"{len(dropped)} dropped (no capability value yet at that date)\n")
    p("| model | slope | R² | reading |")
    p("|---|---|---|---|")
    p(f"| ln ARR ~ ECI | {m_eci.b:.4f} ± {m_eci.se_b:.4f} | {m_eci.r2:.3f} | "
      f"×{math.exp(10*m_eci.b):.1f} per +10 ECI |")
    p(f"| ln ARR ~ log2(METR h) | {m_metr.b:.3f} ± {m_metr.se_b:.3f} | {m_metr.r2:.3f} | "
      f"×{math.exp(m_metr.b):.2f} per horizon doubling |")
    p(f"| ln ARR ~ time | {m_time.b:.3f} | {m_time.r2:.3f} | "
      f"ARR doubles every {12*math.log(2)/m_time.b:.1f} mo |")
    p(f"| ECI ~ time (Anthropic) | {m_eci_time.b:.1f}/yr | {m_eci_time.r2:.3f} | — |")
    if m_frontier_time:
        p(f"| ECI ~ time (frontier) | {m_frontier_time.b:.1f}/yr | {m_frontier_time.r2:.3f} | — |")
    p(f"| log2(h) ~ ECI link | {link.b:.4f} | {link.r2:.3f} | "
      f"horizon doubles per {1/link.b:.1f} ECI pts |")
    p(f"\ncorr(ECI, log2 h) = {corr(eci, l2h):.3f}  → joint 2-var fit not identifiable")
    p(f"lag-90d sensitivity: ECI slope {m_eci_lag.b:.4f} (vs {m_eci.b:.4f})\n")
    p("| ECI | ARR (ECI model) | 80% PI | 95% PI | ARR (METR model) | ensemble | ~when (Anthropic / frontier trend) |")
    p("|---|---|---|---|---|---|---|")
    for pr in proj:
        w = pr["eta_anthropic_trend"][:7]
        wf = (pr["eta_frontier_trend"] or "")[:7]
        p(f"| {pr['eci']} | {fmt_b(pr['arr_central_b'])} "
          f"| {fmt_b(pr['arr_pi80_b'][0])}–{fmt_b(pr['arr_pi80_b'][1])} "
          f"| {fmt_b(pr['arr_pi95_b'][0])}–{fmt_b(pr['arr_pi95_b'][1])} "
          f"| {fmt_b(pr['arr_via_metr_b'])} | {fmt_b(pr['arr_ensemble_b'])} | {w} / {wf} |")
    p(f"\nMETR-equivalent horizons at targets: " + ", ".join(
        f"ECI {pr['eci']} ≈ {fmt_h(pr['metr_equiv_p50_minutes'])}" for pr in proj))


if __name__ == "__main__":
    main()
