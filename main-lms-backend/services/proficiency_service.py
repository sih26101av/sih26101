"""
services/proficiency_service.py — probabilistic proficiency state (SCIL v6 §2)

The displayed FRAC level stays the monotone, evidence-floor level from
baseline_assembler.resolve_level. On top of it this module keeps a
Gaussian belief θ ~ N(μ, σ²) per competency on the same 0–5 level scale:

* μ = the fused K/A/U/S score; σ from the confidence tier.
* Dated two-class decay: the belief relaxes toward the POPULATION prior as
  the newest evidence ages — it never snaps to zero.
      λ = 0.5^(age / half-life)
      μ_t = μ_pop + λ·(μ − μ_pop)
      σ_t² = λ²·σ² + (1 − λ²)·σ_pop²
  Half-life by the competency's decayClass (FRAC data): accuracy 6.5 months,
  procedural 12 months.
* Expected-shortfall gap  G = (T − μ)·Φ(z) + σ·φ(z),  z = (T − μ)/σ — the
  expected number of levels still missing given the uncertainty.
* Cold start: an UNASSESSED competency gets a COHORT prior from officials in
  the same posting cluster (office's dominant GSBPM phase × tenure band) with
  assessed evidence, widened, shown as "inferred from role — unassessed". A
  divergence check drops the pooling for an official whose assessed
  competencies sit far from their cohort.

All numbers come from this code; the inputs are synthetic.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from statistics import mean, pstdev
from typing import Any, Dict, List, Optional, Tuple

HALF_LIFE_MONTHS = {"accuracy": 6.5, "procedural": 12.0}   # SCIL v6 §2 two-class decay
SIGMA_BY_CONFIDENCE = {"HIGH": 0.45, "MEDIUM": 0.7, "LOW": 0.95}   # belief width by evidence tier (levels)
POP_MU_DEFAULT, POP_SIGMA_DEFAULT = 2.0, 1.1   # used until the workforce snapshot exists
POP_SIGMA_FLOOR = 0.6          # a population prior is never narrower than this
REFRESH_MARGIN = 1.0           # decayed μ a full level below the displayed level → refresher suggested
COHORT_MIN_N = 5               # officials needed in a cluster before its prior is used
COHORT_BAND_INFLATION = 1.5    # widen the cohort spread: "inferred from role" is weak evidence
DIVERGENCE_Z = 2.0             # mean |z| of an official's assessed μ vs cohort above this → don't pool
TENURE_BANDS = ((0, 5, "0–5 y"), (6, 15, "6–15 y"), (16, 99, "16+ y"))
BAND_Z = 1.2816                # 80% central band


def _phi(z: float) -> float:
    return math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)


def _Phi(z: float) -> float:
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def expected_shortfall(target: float, mu: float, sigma: float) -> float:
    """E[max(0, T − θ)] for θ ~ N(μ, σ²)."""
    if sigma <= 0:
        return max(0.0, target - mu)
    z = (target - mu) / sigma
    return (target - mu) * _Phi(z) + sigma * _phi(z)


def decay(mu: float, sigma: float, age_months: float, decay_class: str,
          pop_mu: float, pop_sigma: float) -> Tuple[float, float, float]:
    """(μ_t, σ_t, λ) — relax the belief toward the population prior as evidence ages."""
    h = HALF_LIFE_MONTHS.get(decay_class, HALF_LIFE_MONTHS["procedural"])
    lam = 0.5 ** (max(0.0, age_months) / h)
    mu_t = pop_mu + lam * (mu - pop_mu)
    var_t = lam * lam * sigma * sigma + (1 - lam * lam) * pop_sigma * pop_sigma
    return mu_t, math.sqrt(var_t), lam


def months_between(earlier: str, now: datetime) -> Optional[float]:
    try:
        d = datetime.fromisoformat(earlier.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return max(0.0, (now - d).days / 30.4375)


def tenure_band(years: int) -> str:
    return next(label for lo, hi, label in TENURE_BANDS if lo <= int(years or 0) <= hi)


def office_phase(office: Optional[Dict[str, Any]]) -> str:
    """The GSBPM phase the office spends most officer-hours in ('4' Collect, 'OA' overarching …)."""
    if not office:
        return "?"
    hours: Dict[str, int] = {}
    for sp in office.get("subprocesses", []):
        ph = sp["id"].split(".")[0]
        hours[ph] = hours.get(ph, 0) + int(sp.get("officerHours") or 0)
    return max(sorted(hours), key=lambda p: hours[p]) if hours else "?"


# ── Population + cohort statistics from the workforce snapshot ────────────────

def population_stats(snapshot: Dict[str, Dict[str, Any]]) -> Dict[str, Tuple[float, float, int]]:
    """comp → (μ_pop, σ_pop, n) over officials with assessed evidence on it."""
    vals: Dict[str, List[float]] = {}
    for off in snapshot.values():
        for c in off["competencies"]:
            if c["confidence"] != "UNASSESSED":
                vals.setdefault(c["catalogueId"], []).append(c["mu"])
    return {k: (mean(v), max(POP_SIGMA_FLOOR, pstdev(v) if len(v) > 1 else POP_SIGMA_DEFAULT), len(v))
            for k, v in vals.items()}


def cluster_of(off: Dict[str, Any]) -> str:
    return f"GSBPM phase {off['phase']} × {tenure_band(off['experienceYears'])}"


def cohort_prior(
    user_id: str, comp: str, snapshot: Dict[str, Dict[str, Any]],
    population: Dict[str, Tuple[float, float, int]],
) -> Optional[Dict[str, Any]]:
    """Cohort prior for an UNASSESSED competency, with the divergence check."""
    me = snapshot.get(user_id)
    if not me:
        return None
    cluster = cluster_of(me)
    peers = [o for uid, o in snapshot.items() if uid != user_id and cluster_of(o) == cluster]

    def assessed(off, cid):
        return next((c["mu"] for c in off["competencies"]
                     if c["catalogueId"] == cid and c["confidence"] != "UNASSESSED"), None)

    cohort_vals = [v for v in (assessed(o, comp) for o in peers) if v is not None]
    pop = population.get(comp, (POP_MU_DEFAULT, POP_SIGMA_DEFAULT, 0))

    # Divergence check: is this official typical of the cohort on what IS assessed?
    zs = []
    for c in me["competencies"]:
        if c["confidence"] == "UNASSESSED":
            continue
        others = [v for v in (assessed(o, c["catalogueId"]) for o in peers) if v is not None]
        if len(others) >= COHORT_MIN_N:
            sd = max(POP_SIGMA_FLOOR, pstdev(others))
            zs.append(abs(c["mu"] - mean(others)) / sd)
    divergence = mean(zs) if zs else None

    if len(cohort_vals) >= COHORT_MIN_N and (divergence is None or divergence <= DIVERGENCE_Z):
        mu = mean(cohort_vals)
        sigma = max(POP_SIGMA_FLOOR, pstdev(cohort_vals)) * COHORT_BAND_INFLATION
        pooled, source = True, "cohort"
        reason = f"Inferred from role — {len(cohort_vals)} officials in {cluster} with assessed evidence."
    else:
        mu, sigma = pop[0], pop[1] * COHORT_BAND_INFLATION
        pooled, source = False, "population"
        reason = (f"Profile diverges from its cohort (mean |z| = {divergence:.1f} > {DIVERGENCE_Z}); "
                  f"population prior used instead." if divergence is not None and divergence > DIVERGENCE_Z
                  else f"Fewer than {COHORT_MIN_N} assessed officials in {cluster}; population prior used.")
    return {
        "label": "inferred from role — unassessed",
        "mu": round(mu, 2), "sigma": round(sigma, 2),
        "band80": [round(max(0.0, mu - BAND_Z * sigma), 1), round(min(5.0, mu + BAND_Z * sigma), 1)],
        "cluster": cluster, "source": source, "pooled": pooled,
        "cohortN": len(cohort_vals) if len(cohort_vals) >= COHORT_MIN_N else None,   # n < 5 suppressed
        "divergence": round(divergence, 2) if divergence is not None else None,
        "reason": reason,
    }


def proficiency_state(
    row: Dict[str, Any], decay_class: str, population: Dict[str, Tuple[float, float, int]],
    now: Optional[datetime] = None,
) -> Optional[Dict[str, Any]]:
    """Belief for an assessed competency, decayed by the age of its newest dated evidence."""
    conf = row.get("confidence")
    if conf == "UNASSESSED" or conf not in SIGMA_BY_CONFIDENCE:
        return None
    now = now or datetime.now(timezone.utc)
    mu, sigma = float(row.get("rawScore") or 0.0), SIGMA_BY_CONFIDENCE[conf]
    pop_mu, pop_sigma, _n = population.get(row.get("catalogueId") or row["competencyId"],
                                           (POP_MU_DEFAULT, POP_SIGMA_DEFAULT, 0))
    age = months_between(row["lastEvidenceDate"], now) if row.get("lastEvidenceDate") else None
    if age is None:
        mu_t, sigma_t, lam = mu, sigma, 1.0            # priors only: nothing dated to decay
    else:
        mu_t, sigma_t, lam = decay(mu, sigma, age, decay_class, pop_mu, pop_sigma)
    target, level = float(row["targetLevel"]), row.get("currentLevel")
    return {
        "mu": round(mu, 2), "sigma": round(sigma, 2),
        "decayedMu": round(mu_t, 2), "decayedSigma": round(sigma_t, 2),
        "band80": [round(max(0.0, mu_t - BAND_Z * sigma_t), 1), round(min(5.0, mu_t + BAND_Z * sigma_t), 1)],
        "evidenceAgeMonths": round(age, 1) if age is not None else None,
        "decayClass": decay_class, "halfLifeMonths": HALF_LIFE_MONTHS.get(decay_class),
        "retention": round(lam, 3),
        "populationMu": round(pop_mu, 2),
        "expectedShortfall": round(expected_shortfall(target, mu_t, sigma_t), 2),
        "refresherRecommended": bool(level is not None and mu_t < level - REFRESH_MARGIN),
    }
