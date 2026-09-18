"""
Measured course uplift (SCIL v6 §6): propensity weighting, shrinkage, mis-tag flag.

    pytest tests/test_uplift.py

The last test checks RECOVERY OF PLANTED SYNTHETIC EFFECTS on the generated
mock data (the ground truth the generator wrote to data/_truth/). It shows the
estimator works as designed; it validates nothing about real courses.
"""
import json
import os
import random

import numpy as np

from services import uplift_service as us

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "mock-igot-server", "data")


def _world(uplifts: dict, n_takers=40, n_controls=400, slope=0.15, seed=3):
    """Takers of a Level-4 course are strong; everyone grows by 0.02 + slope·pre anyway."""
    rng = random.Random(seed)
    outcomes, comparisons = [], []
    for course, uplift in uplifts.items():
        for i in range(n_takers):
            pre = 3 + rng.uniform(0.1, 0.9)
            post = pre + 0.02 + slope * pre + uplift + rng.gauss(0, 0.1)
            outcomes.append({"courseId": course, "competencyId": "X", "courseLevel": 4,
                             "preTheta": pre, "postTheta": post,
                             "covariates": {"tenureYears": 20, "education": "other"}})
    for i in range(n_controls):
        pre = rng.uniform(0.1, 4.9)
        comparisons.append({"competencyId": "X", "preTheta": pre,
                            "postTheta": pre + 0.02 + slope * pre + rng.gauss(0, 0.1),
                            "covariates": {"tenureYears": 20, "education": "other"}})
    return outcomes, comparisons


def test_propensity_weighting_removes_confounding_that_the_naive_estimate_keeps():
    outcomes, comparisons = _world({"good": 0.5})
    est = us.estimate_uplift(outcomes, comparisons)["courses"][0]
    # strong takers grow faster anyway: naive over-states by ≈ slope × (3.5 − 2.5)
    assert est["naiveUplift"] - 0.5 > 0.1
    assert abs(est["ipwUplift"] - 0.5) < 0.06


def test_shrinkage_formula_and_prior():
    outcomes, comparisons = _world({"a": 0.6, "b": 0.2})
    res = us.estimate_uplift(outcomes, comparisons)
    prior = res["priors"]["4"]
    for c in res["courses"]:
        n = c["n"]
        expected = (n * c["ipwUplift"] + us.KAPPA * prior) / (n + us.KAPPA)
        assert abs(c["measuredUplift"] - expected) < 0.002          # q̂ = (n·Δ + κ·q_prior)/(n+κ)
        assert c["ci95"][0] <= c["measuredUplift"] <= c["ci95"][1]


def test_near_zero_uplift_is_flagged_only_with_enough_learners():
    outcomes, comparisons = _world({"useful": 0.5, "dud": 0.0})
    by_id = {c["courseId"]: c for c in us.estimate_uplift(outcomes, comparisons)["courses"]}
    assert by_id["dud"]["misTagFlag"] and not by_id["useful"]["misTagFlag"]
    few, comp = _world({"dud": 0.0}, n_takers=us.MIN_TAKERS_FOR_FLAG - 1)
    assert not us.estimate_uplift(few, comp)["courses"][0]["misTagFlag"]


def test_estimates_are_deterministic():
    outcomes, comparisons = _world({"a": 0.4})
    assert us.estimate_uplift(outcomes, comparisons) == us.estimate_uplift(outcomes, comparisons)


def test_recovers_the_planted_zero_uplift_courses_in_the_mock_data():
    with open(os.path.join(DATA, "course_outcomes.json"), encoding="utf-8") as fh:
        doc = json.load(fh)
    with open(os.path.join(DATA, "_truth", "planted_effects.json"), encoding="utf-8") as fh:
        truth = json.load(fh)
    courses = us.estimate_uplift(doc["outcomes"], doc["comparisons"])["courses"]
    flagged = {c["courseId"] for c in courses if c["misTagFlag"]}
    assert flagged == set(truth["zeroUpliftCourses"])
    well_measured = [c for c in courses if c["n"] >= 15]
    r = np.corrcoef([truth["trueUplift"][c["courseId"]] for c in well_measured],
                    [c["measuredUplift"] for c in well_measured])[0, 1]
    assert r > 0.8
