"""
services/uplift_service.py — measured course uplift (SCIL v6 §6 coverage learning)

For every course j (primary FRAC competency c, level L) from course outcome
assessments (pre/post θ on the FRAC level scale):

  1. Treated = learners who took j; controls = comparison episodes of
     learners who took no course on c in a similar interval.
  2. Propensity e(x) = P(took j | preθ, tenure, statistics degree) by ridge
     logistic regression over treated ∪ controls. Strong officers self-select
     into advanced courses AND grow faster anyway, so an unweighted
     comparison overstates uplift; ATT weights w = e/(1−e) on the controls
     rebalance them to look like the takers.
         uplift_ipw = mean_T(Δθ) − Σ_C w·Δθ / Σ_C w        (Δθ = postθ − preθ)
  3. Shrinkage toward a prior:  q̂_jc = (n·uplift_ipw + κ·q_prior) / (n + κ),
     q_prior = pooled mean IPW uplift of the courses at the same FRAC level.
  4. 95% CI by bootstrap (treated and controls resampled; the propensity
     model is held fixed, so the CI is conditional on it).
  5. Mis-tag flag: the course declares c as its primary FRAC tag (high declared
     relevance) but the upper bound of the data-only (unshrunk) IPW CI is below
     MIS_TAG_MAX_UPLIFT.

Everything is computed by this code over SYNTHETIC data with planted effects.
Recovering those effects demonstrates the method; it validates nothing.
"""
from __future__ import annotations

import zlib
from typing import Any, Dict, List, Optional

import numpy as np

KAPPA = 5.0                  # the prior counts as 5 learners: n=5 → half data, half prior
PROPENSITY_RIDGE = 0.1       # small L2 penalty: keeps the logistic fit finite when takers separate
PROPENSITY_CLIP = (0.02, 0.98)   # trims extreme weights (a control that "should" have taken j)
BOOTSTRAP_ROUNDS = 300       # resamples per course for the 95% CI
MIS_TAG_MAX_UPLIFT = 0.15    # CI upper bound below this (< 1/6 level) → near-zero uplift
MIN_TAKERS_FOR_FLAG = 10     # don't flag a course on fewer learners than this


def _features(rows: List[Dict[str, Any]], level: int) -> np.ndarray:
    """[1, z, z², tenure/10, statistics degree] with z = preθ − (level − 0.5): takers sit in a band
    just below the course level, which a linear term in preθ alone cannot represent."""
    z = np.array([r["preTheta"] for r in rows], dtype=float) - (level - 0.5)
    tenure = np.array([(r.get("covariates") or {}).get("tenureYears", 10) for r in rows], dtype=float)
    stats = np.array([1.0 if (r.get("covariates") or {}).get("education") in ("statistics", "mathematics")
                      else 0.0 for r in rows])
    return np.column_stack([np.ones(len(rows)), z, z * z, tenure / 10.0, stats])


def _ridge_logit(x: np.ndarray, t: np.ndarray, ridge: float = PROPENSITY_RIDGE, iters: int = 25) -> np.ndarray:
    """Newton–Raphson for an L2-penalised logistic regression (intercept unpenalised)."""
    beta = np.zeros(x.shape[1])
    pen = np.full(x.shape[1], ridge)
    pen[0] = 0.0
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-(x @ beta)))
        grad = x.T @ (t - p) - pen * beta
        hess = (x * (p * (1 - p))[:, None]).T @ x + np.diag(pen)
        step = np.linalg.solve(hess, grad)
        beta += step
        if np.max(np.abs(step)) < 1e-6:
            break
    return beta


def _ipw(delta_t: np.ndarray, delta_c: np.ndarray, w_c: np.ndarray) -> float:
    return float(delta_t.mean() - (w_c @ delta_c) / w_c.sum())


def estimate_uplift(
    outcomes: List[Dict[str, Any]],
    comparisons: List[Dict[str, Any]],
    catalog_meta: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """{courses: [...per-course estimates...], priors, method} — see module docstring."""
    catalog_meta = catalog_meta or {}
    by_course: Dict[str, List[Dict[str, Any]]] = {}
    for o in outcomes:
        by_course.setdefault(o["courseId"], []).append(o)
    controls_by_comp: Dict[str, List[Dict[str, Any]]] = {}
    for c in comparisons:
        controls_by_comp.setdefault(c["competencyId"], []).append(c)

    raw: Dict[str, Dict[str, Any]] = {}
    for cid, rows in sorted(by_course.items()):
        comp, level = rows[0]["competencyId"], int(rows[0]["courseLevel"])
        ctl = controls_by_comp.get(comp, [])
        if not ctl:
            continue
        x_t, x_c = _features(rows, level), _features(ctl, level)
        x = np.vstack([x_t, x_c])
        t = np.concatenate([np.ones(len(rows)), np.zeros(len(ctl))])
        beta = _ridge_logit(x, t)
        e = np.clip(1.0 / (1.0 + np.exp(-(x_c @ beta))), *PROPENSITY_CLIP)
        w = e / (1 - e)
        d_t = np.array([r["postTheta"] - r["preTheta"] for r in rows], dtype=float)
        d_c = np.array([r["postTheta"] - r["preTheta"] for r in ctl], dtype=float)
        raw[cid] = {"comp": comp, "level": level, "d_t": d_t, "d_c": d_c, "w": w,
                    "naive": float(d_t.mean() - d_c.mean()), "ipw": _ipw(d_t, d_c, w),
                    "ess": float(w.sum() ** 2 / (w @ w))}

    # q_prior: pooled IPW uplift per FRAC level (data-derived, not tuned)
    priors: Dict[int, float] = {}
    for level in range(1, 6):
        vals = [r["ipw"] for r in raw.values() if r["level"] == level]
        priors[level] = float(np.mean(vals)) if vals else float(np.mean([r["ipw"] for r in raw.values()]))

    courses = []
    for cid, r in raw.items():
        n, prior = len(r["d_t"]), priors[r["level"]]
        shrunk = (n * r["ipw"] + KAPPA * prior) / (n + KAPPA)
        rng = np.random.default_rng(zlib.crc32(cid.encode()))
        it = rng.integers(0, n, (BOOTSTRAP_ROUNDS, n))
        ic = rng.integers(0, len(r["d_c"]), (BOOTSTRAP_ROUNDS, len(r["d_c"])))
        w_b = r["w"][ic]
        ipw_b = r["d_t"][it].mean(axis=1) - (w_b * r["d_c"][ic]).sum(axis=1) / w_b.sum(axis=1)
        raw_lo, raw_hi = np.percentile(ipw_b, [2.5, 97.5])            # data only (for the flag)
        lo, hi = np.percentile((n * ipw_b + KAPPA * prior) / (n + KAPPA), [2.5, 97.5])   # shrunk q̂
        meta = catalog_meta.get(cid, {})
        # the flag asks the DATA whether uplift is near zero, so it uses the unshrunk IPW
        # interval — shrinking toward the (positive) prior would hide exactly these courses
        flag = bool(n >= MIN_TAKERS_FOR_FLAG and raw_hi < MIS_TAG_MAX_UPLIFT)
        courses.append({
            "courseId": cid,
            "title": meta.get("title", cid),
            "competencyId": r["comp"],
            "competencyName": meta.get("competencyName", r["comp"]),
            "courseLevel": r["level"],
            "format": meta.get("format"),
            "rating": meta.get("rating"),
            "enrollmentCount": meta.get("enrollmentCount"),
            "n": n,
            "controls": len(r["d_c"]),
            "controlsEffectiveN": round(r["ess"], 1),
            "naiveUplift": round(r["naive"], 3),
            "ipwUplift": round(r["ipw"], 3),
            "prior": round(prior, 3),
            "measuredUplift": round(float(shrunk), 3),
            "ci95": [round(float(lo), 3), round(float(hi), 3)],
            "ipwCi95": [round(float(raw_lo), 3), round(float(raw_hi), 3)],
            "misTagFlag": flag,
            "flagReason": ("Primary FRAC tag declares this competency, but measured uplift is near zero "
                           f"(IPW 95% CI upper bound {raw_hi:.2f} < {MIS_TAG_MAX_UPLIFT} levels on {n} learners)."
                           if flag else None),
        })
    courses.sort(key=lambda c: (-c["measuredUplift"], c["courseId"]))
    return {
        "courses": courses,
        "priors": {str(k): round(v, 3) for k, v in priors.items()},
        "constants": {"kappa": KAPPA, "propensityRidge": PROPENSITY_RIDGE, "propensityClip": list(PROPENSITY_CLIP),
                      "bootstrapRounds": BOOTSTRAP_ROUNDS, "misTagMaxUplift": MIS_TAG_MAX_UPLIFT,
                      "minTakersForFlag": MIN_TAKERS_FOR_FLAG},
        "method": ("ATT by inverse propensity weighting (ridge logistic on preθ, tenure, statistics degree; "
                   "controls = learners with no course on the competency), shrunk toward the pooled uplift at "
                   f"the course's FRAC level with κ = {KAPPA:g}; 95% bootstrap CI ({BOOTSTRAP_ROUNDS} resamples, "
                   "propensity model held fixed). Mis-tag flag: primary tag but unshrunk IPW CI upper bound < "
                   f"{MIS_TAG_MAX_UPLIFT} with ≥ {MIN_TAKERS_FOR_FLAG} learners."),
    }
