"""
SCIL v6 §2 dated decay / expected-shortfall / cold start, and §11 workforce
foresight (capability risk, projection, TPAC agenda, n < 5 suppression).

    pytest tests/test_proficiency_foresight.py
"""
from datetime import date, datetime, timezone

import pytest

from services import proficiency_service as ps
from services import workforce_service as ws

NOW = datetime(2026, 9, 15, tzinfo=timezone.utc)


# ── Decay ─────────────────────────────────────────────────────────────────────

def test_decay_relaxes_toward_the_population_mean_not_zero():
    mu, sigma, lam = ps.decay(4.0, 0.4, ps.HALF_LIFE_MONTHS["accuracy"], "accuracy", pop_mu=2.0, pop_sigma=1.0)
    assert lam == pytest.approx(0.5)
    assert mu == pytest.approx(3.0)                          # halfway back to 2.0 after one half-life
    assert 0.4 < sigma < 1.0                                 # uncertainty grows toward the population's
    far_mu, far_sigma, _ = ps.decay(4.0, 0.4, 600, "accuracy", 2.0, 1.0)
    assert far_mu == pytest.approx(2.0, abs=1e-6) and far_sigma == pytest.approx(1.0, abs=1e-6)


def test_accuracy_skills_decay_faster_than_procedural():
    acc, _, _ = ps.decay(4.0, 0.4, 12, "accuracy", 2.0, 1.0)
    proc, _, _ = ps.decay(4.0, 0.4, 12, "procedural", 2.0, 1.0)
    assert acc < proc < 4.0
    assert ps.HALF_LIFE_MONTHS == {"accuracy": 6.5, "procedural": 12.0}


def test_expected_shortfall():
    assert ps.expected_shortfall(3, 1.0, 0.0) == 2.0
    assert ps.expected_shortfall(3, 4.0, 1e-9) == pytest.approx(0.0)
    g_close, g_far = ps.expected_shortfall(3, 2.5, 0.8), ps.expected_shortfall(3, 1.5, 0.8)
    assert 0.5 < g_close < g_far                             # uncertainty adds to the plain gap
    assert ps.expected_shortfall(3, 3.0, 0.8) == pytest.approx(0.8 * 0.3989, rel=1e-3)


def test_proficiency_state_flags_a_refresher_after_long_decay():
    row = {"competencyId": "c", "catalogueId": "c", "confidence": "HIGH", "rawScore": 4.2,
           "targetLevel": 4, "currentLevel": 4, "lastEvidenceDate": "2024-09-15"}
    fresh = ps.proficiency_state({**row, "lastEvidenceDate": "2026-09-01"}, "accuracy", {"c": (2.0, 1.0, 50)}, NOW)
    stale = ps.proficiency_state(row, "accuracy", {"c": (2.0, 1.0, 50)}, NOW)
    assert not fresh["refresherRecommended"] and stale["refresherRecommended"]
    assert stale["decayedMu"] < fresh["decayedMu"] and stale["expectedShortfall"] > fresh["expectedShortfall"]
    assert ps.proficiency_state({**row, "confidence": "UNASSESSED"}, "accuracy", {}, NOW) is None


# ── Cold start ────────────────────────────────────────────────────────────────

def _official(phase, years, comps):
    return {"phase": phase, "experienceYears": years,
            "competencies": [{"catalogueId": c, "confidence": "HIGH" if mu is not None else "UNASSESSED",
                              "mu": mu if mu is not None else 0.0} for c, mu in comps.items()]}


def _snapshot(me_other_mu=2.0):
    snap = {f"peer{i}": _official("4", 3, {"x": 2.0 + 0.1 * i, "y": 2.0}) for i in range(6)}
    snap["me"] = _official("4", 2, {"x": None, "y": me_other_mu})
    snap["far"] = _official("6", 20, {"x": 4.5, "y": 4.5})
    return snap


def test_unassessed_competency_gets_a_wide_cohort_prior():
    snap = _snapshot()
    prior = ps.cohort_prior("me", "x", snap, ps.population_stats(snap))
    assert prior["source"] == "cohort" and prior["pooled"] and prior["cohortN"] == 6
    assert prior["mu"] == pytest.approx(2.25, abs=0.01)
    assert prior["band80"][1] - prior["band80"][0] > 1.5    # "inferred from role" is weak evidence
    assert prior["label"] == "inferred from role — unassessed"


def test_divergent_official_is_not_pooled_with_the_cohort():
    snap = _snapshot(me_other_mu=4.9)                     # far above the cohort on what IS assessed
    prior = ps.cohort_prior("me", "x", snap, ps.population_stats(snap))
    assert prior["source"] == "population" and not prior["pooled"]
    assert prior["divergence"] > ps.DIVERGENCE_Z


def test_small_cohort_falls_back_to_the_population_and_hides_its_size():
    snap = {f"peer{i}": _official("4", 3, {"x": 2.0}) for i in range(3)}
    snap["me"] = _official("4", 2, {"x": None})
    prior = ps.cohort_prior("me", "x", snap, ps.population_stats(snap))
    assert prior["source"] == "population" and prior["cohortN"] is None


# ── Workforce foresight ──────────────────────────────────────────────────────

def test_counts_of_one_to_four_are_suppressed():
    assert ws.cell(0) == {"value": 0, "suppressed": False, "display": "0"}
    assert ws.cell(3)["suppressed"] and ws.cell(3)["value"] is None and ws.cell(3)["display"] == "<5"
    assert ws.cell(5)["value"] == 5 and not ws.cell(5)["suppressed"]


def _hrms(retire):
    return {"products": {"P": "Product P"}, "productCriticalCompetencies": {"P": ["x"]},
            "officials": {u: {"products": ["P"], "superannuationDate": d} for u, d in retire.items()}}


def _snap(levels):
    return {u: {"competencies": [{"catalogueId": "x", "level": lvl, "target": 4, "confidence": "HIGH",
                                  "mu": float(lvl) + 0.5, "lastEvidenceDate": "2026-08-01",
                                  "decayClass": "procedural"}]}
            for u, lvl in levels.items()}


def test_single_point_of_failure_and_retirement_risk():
    snap = _snap({"a": 4, "b": 1, "c": 2})
    risk = ws.capability_risk(snap, _hrms({"a": "2040-01-31", "b": "2040-01-31", "c": "2040-01-31"}),
                              {"x": "X"}, today=date(2026, 9, 15))
    row = risk["products"][0]["competencies"][0]
    assert row["singlePointOfFailure"] and row["risk"] == "critical"
    assert row["capable"]["display"] == "<5"                 # the count itself is still suppressed

    snap = _snap({f"u{i}": 4 for i in range(6)})
    retiring = {f"u{i}": "2027-01-31" for i in range(6)}
    row = ws.capability_risk(snap, _hrms(retiring), {"x": "X"}, today=date(2026, 9, 15))["products"][0]["competencies"][0]
    assert row["risk"] == "critical" and row["capable"]["value"] == 6
    assert row["retiringWithin36m"]["value"] == 6


def test_foresight_declines_with_retirements_and_attrition():
    snap = _snap({f"u{i}": 4 for i in range(8)})
    retire = {f"u{i}": ("2027-06-30" if i < 3 else "2045-01-31") for i in range(8)}
    fc = ws.foresight(snap, _hrms(retire), {"x": "X"}, {"x": (2.0, 1.0, 8)}, now=NOW)
    s = fc["series"][0]
    start, end = s["attritionOnly"][0]["expectedCapable"], s["attritionOnly"][-1]["expectedCapable"]
    assert start["value"] == 8 and end["value"] == 5           # 3 retire, the rest × 0.97^3
    decayed_end = s["withDecay"][-1]["expectedCapable"]
    assert decayed_end["suppressed"] or decayed_end["value"] <= end["value"]
    assert s["declining"]
