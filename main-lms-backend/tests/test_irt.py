"""
Tier-1 2PL posterior + adaptive diagnostic (SCIL v6 §2).

    pytest tests/test_irt.py

These tests check the MATHS (Laplace vs a numerical grid posterior, Fisher
information, stopping rules, what the learner is shown). Deliberately there is
no "accuracy" test that simulates responses from the item parameters and
scores the estimator against them: with synthetic parameters that would be
circular and prove nothing about real officials.
"""
import math

import numpy as np
import pytest

from services import irt_service as irt


def _grid_posterior(mu0, s0, responses):
    th = np.linspace(-3, 8, 20001)
    logp = -0.5 * ((th - mu0) / s0) ** 2
    for a, b, y in responses:
        p = 1 / (1 + np.exp(-a * (th - b)))
        logp += y * np.log(p) + (1 - y) * np.log(1 - p)
    w = np.exp(logp - logp.max())
    w /= w.sum()
    mean = float((th * w).sum())
    return th[np.argmax(w)], mean, float(np.sqrt(((th - mean) ** 2 * w).sum()))


def test_laplace_posterior_matches_the_grid_posterior():
    responses = [(1.5, 2.0, 1), (1.2, 3.0, 1), (1.8, 3.5, 0), (1.0, 2.5, 1), (1.6, 4.0, 0)]
    mode, sd = irt.laplace_posterior(2.0, 1.0, responses)
    g_mode, g_mean, g_sd = _grid_posterior(2.0, 1.0, responses)
    assert mode == pytest.approx(g_mode, abs=0.01)
    assert sd == pytest.approx(g_sd, rel=0.1)


def test_no_responses_returns_the_prior_and_evidence_narrows_it():
    assert irt.laplace_posterior(2.3, 0.9, []) == pytest.approx((2.3, 0.9))
    _, sd = irt.laplace_posterior(2.3, 0.9, [(1.5, 2.3, 1), (1.5, 2.3, 0)])
    assert sd < 0.9


def test_correct_answers_move_the_estimate_up_wrong_ones_down():
    up, _ = irt.laplace_posterior(2.0, 1.0, [(1.5, 2.0, 1)] * 3)
    down, _ = irt.laplace_posterior(2.0, 1.0, [(1.5, 2.0, 0)] * 3)
    assert down < 2.0 < up


def test_next_item_maximises_fisher_information():
    items = [{"itemId": f"i{b}", "a": 1.5, "b": b} for b in (0.5, 1.5, 2.5, 3.5, 4.5)]
    assert irt.next_item(items, set(), 2.4)["itemId"] == "i2.5"
    assert irt.next_item(items, {"i2.5"}, 2.4)["itemId"] in ("i1.5", "i3.5")
    assert irt.fisher_information(2.5, 1.5, 2.5) == pytest.approx(1.5 ** 2 * 0.25)


def _bank(n_per_level=3):
    return [{"itemId": f"L{lvl}_{k}", "competencyId": "c", "level": lvl, "bloom": "Apply",
             "stem": "?", "options": ["a", "b", "c", "d"], "answerIndex": 0,
             "a": 1.4 + 0.1 * k, "b": lvl - 0.5 + 0.1 * k}
            for lvl in range(1, 6) for k in range(n_per_level)]


def _run(answer_fn, prior=(2.0, 1.0)):
    sessions = irt.DiagnosticSessions()
    comp = {"competencyId": "c", "competencyName": "C", "targetLevel": 3}
    view = sessions.start("usr_1", comp, _bank(), {"mu": prior[0], "sigma": prior[1], "source": "test"})
    while not view["done"]:
        item = next(i for i in _bank() if i["itemId"] == view["item"]["itemId"])
        view = sessions.answer(view["sessionId"], item["itemId"], 0 if answer_fn(item) else 1)
    return sessions, view


def test_session_stops_by_tau_or_max_items_and_hides_keys():
    sessions = irt.DiagnosticSessions()
    comp = {"competencyId": "c", "competencyName": "C", "targetLevel": 3}
    view = sessions.start("usr_1", comp, _bank(), {"mu": 2.0, "sigma": 1.0, "source": "test"})
    assert "answerIndex" not in view["item"] and "a" not in view["item"] and "b" not in view["item"]
    assert view["calibration"] == "calibrated on synthetic data — demo only"

    _, done = _run(lambda item: item["b"] < 2.6)          # a consistent pattern
    assert done["done"] and irt.MIN_ITEMS <= done["answered"] <= irt.MAX_ITEMS
    assert done["posterior"]["sigma"] < irt.TAU or done["answered"] == irt.MAX_ITEMS


def test_result_reports_level_band_and_expected_shortfall():
    sessions, done = _run(lambda item: item["b"] < 2.6)
    res = sessions.result(done["sessionId"])
    mu, sigma = res["posterior"]["mu"], res["posterior"]["sigma"]
    assert res["estimatedLevel"] == math.floor(mu)
    assert res["band80"][0] < mu < res["band80"][1]
    assert res["expectedShortfall"] == pytest.approx(irt.expected_shortfall(3, mu, sigma), abs=1e-3)
    assert 0 <= res["probabilityAtOrAboveTarget"] <= 1
    assert res["calibration"] == irt.CALIBRATION_LABEL


def test_answering_the_wrong_item_or_after_the_end_is_rejected():
    sessions, done = _run(lambda item: True)
    with pytest.raises(ValueError):
        sessions.answer(done["sessionId"], "L1_0", 0)
    other = irt.DiagnosticSessions()
    view = other.start("usr_1", {"competencyId": "c", "competencyName": "C", "targetLevel": 3}, _bank(),
                       {"mu": 2.0, "sigma": 1.0, "source": "t"})
    with pytest.raises(ValueError):
        other.answer(view["sessionId"], "not-the-current-item", 0)
    assert other.get(view["sessionId"], "usr_someone_else") is None
