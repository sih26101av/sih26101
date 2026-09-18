"""
services/irt_service.py — Tier-1 Bayesian 2PL posterior + adaptive diagnostic (SCIL v6 §2)

    P(correct | θ) = 1 / (1 + exp(−a(θ − b)))      θ, b on the FRAC level scale (0–5)

* Prior θ ~ N(μ₀, σ₀²): the official's decayed belief (proficiency_service), else
  the cold-start cohort prior, else the population default.
* Posterior by Laplace approximation: the mode of the log-posterior by Newton's
  method, σ² = −1 / (second derivative at the mode).
* Next item: the unused item with maximum Fisher information a²·P·(1−P) at the
  current posterior mode.
* Stop when σ < TAU (after MIN_ITEMS) or after MAX_ITEMS.
* Expected-shortfall gap G = (T − μ)Φ(z) + σφ(z).

CALIBRATED ON SYNTHETIC DATA — DEMO ONLY. The item parameters were simulated,
not estimated from real respondents. No accuracy/validation figure is computed
anywhere from responses generated with these same parameters (that would be
circular). Tier-2 attribute mastery (DINA) is NOT built: it needs 30–50 real
respondents per attribute set.
"""
from __future__ import annotations

import math
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from services.proficiency_service import expected_shortfall

TAU = 0.35               # stop once the posterior SD is below ~⅓ of a FRAC level …
MIN_ITEMS = 5            # … but never before 5 answers (a lucky streak isn't a measurement)
MAX_ITEMS = 15           # hard cap (SCIL v6: 12–15 items)
THETA_BOUNDS = (-1.0, 6.0)   # keep the Newton mode on a sane range around the 0–5 scale
SESSION_TTL_SECONDS = 2 * 3600
CALIBRATION_LABEL = "calibrated on synthetic data — demo only"


def p_correct(theta: float, a: float, b: float) -> float:
    return 1.0 / (1.0 + math.exp(-a * (theta - b)))


def fisher_information(theta: float, a: float, b: float) -> float:
    p = p_correct(theta, a, b)
    return a * a * p * (1.0 - p)


def laplace_posterior(prior_mu: float, prior_sigma: float,
                      responses: List[Tuple[float, float, int]]) -> Tuple[float, float]:
    """(mode, sd) of N(prior) × Π 2PL likelihoods, Laplace approximation. responses = [(a, b, y)]."""
    theta = prior_mu
    prec0 = 1.0 / (prior_sigma * prior_sigma)
    for _ in range(50):
        grad = -(theta - prior_mu) * prec0
        hess = -prec0
        for a, b, y in responses:
            p = p_correct(theta, a, b)
            grad += a * (y - p)
            hess -= a * a * p * (1 - p)
        step = grad / hess
        theta = min(THETA_BOUNDS[1], max(THETA_BOUNDS[0], theta - step))
        if abs(step) < 1e-7:
            break
    info = prec0 + sum(a * a * p_correct(theta, a, b) * (1 - p_correct(theta, a, b)) for a, b, _ in responses)
    return theta, 1.0 / math.sqrt(info)


def next_item(items: List[Dict[str, Any]], used: set, theta: float) -> Optional[Dict[str, Any]]:
    pool = [i for i in items if i["itemId"] not in used]
    if not pool:
        return None
    return max(pool, key=lambda i: (fisher_information(theta, i["a"], i["b"]), i["itemId"]))


def public_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """What the learner sees: no answer key, no parameters."""
    return {"itemId": item["itemId"], "stem": item["stem"], "options": item["options"],
            "bloom": item["bloom"], "level": item["level"]}


class DiagnosticSessions:
    """In-memory adaptive sessions (per process). Lost on restart — a session is minutes long."""

    def __init__(self) -> None:
        self._s: Dict[str, Dict[str, Any]] = {}

    def _gc(self) -> None:
        now = time.time()
        for sid in [k for k, v in self._s.items() if now - v["created"] > SESSION_TTL_SECONDS]:
            del self._s[sid]

    def start(self, user_id: str, comp: Dict[str, Any], items: List[Dict[str, Any]],
              prior: Dict[str, Any]) -> Dict[str, Any]:
        self._gc()
        sid = uuid.uuid4().hex
        first = next_item(items, set(), prior["mu"])
        self._s[sid] = {
            "sessionId": sid, "userId": user_id, "created": time.time(), "competency": comp,
            "items": items, "prior": prior, "responses": [], "used": set(),
            "mu": prior["mu"], "sigma": prior["sigma"], "current": first, "done": False,
            "stopReason": None, "evidenceWritten": False,
        }
        return self.view(sid)

    def get(self, sid: str, user_id: str) -> Optional[Dict[str, Any]]:
        s = self._s.get(sid)
        return s if s and s["userId"] == user_id else None

    def answer(self, sid: str, item_id: str, option_index: int) -> Dict[str, Any]:
        s = self._s[sid]
        if s["done"]:
            raise ValueError("This diagnostic is already finished.")
        item = s["current"]
        if item is None or item["itemId"] != item_id:
            raise ValueError("That is not the current item.")
        correct = int(option_index == item["answerIndex"])
        s["responses"].append({"itemId": item_id, "a": item["a"], "b": item["b"], "correct": correct,
                               "level": item["level"]})
        s["used"].add(item_id)
        s["mu"], s["sigma"] = laplace_posterior(
            s["prior"]["mu"], s["prior"]["sigma"], [(r["a"], r["b"], r["correct"]) for r in s["responses"]])
        n = len(s["responses"])
        if n >= MIN_ITEMS and s["sigma"] < TAU:
            s["done"], s["stopReason"] = True, f"posterior SD {s['sigma']:.2f} < τ = {TAU}"
        elif n >= MAX_ITEMS:
            s["done"], s["stopReason"] = True, f"reached the maximum of {MAX_ITEMS} items"
        else:
            s["current"] = next_item(s["items"], s["used"], s["mu"])
            if s["current"] is None:
                s["done"], s["stopReason"] = True, "item bank exhausted for this competency"
        return self.view(sid)

    def view(self, sid: str) -> Dict[str, Any]:
        s = self._s[sid]
        out = {
            "sessionId": sid,
            "competencyId": s["competency"]["competencyId"],
            "competencyName": s["competency"]["competencyName"],
            "answered": len(s["responses"]),
            "maxItems": MAX_ITEMS,
            "tau": TAU,
            "posterior": {"mu": round(s["mu"], 3), "sigma": round(s["sigma"], 3)},
            "done": s["done"],
            "calibration": CALIBRATION_LABEL,
        }
        if not s["done"] and s["current"] is not None:
            out["item"] = public_item(s["current"])
        return out

    def result(self, sid: str) -> Dict[str, Any]:
        s = self._s[sid]
        target = float(s["competency"]["targetLevel"])
        mu, sigma = s["mu"], s["sigma"]
        z = (target - mu) / sigma if sigma > 0 else 0.0
        p_at_target = 1.0 - 0.5 * (1 + math.erf(z / math.sqrt(2)))
        return {
            **self.view(sid),
            "prior": s["prior"],
            "stopReason": s["stopReason"],
            "estimatedLevel": max(0, min(5, int(math.floor(mu)))),
            "band80": [round(max(0.0, mu - 1.2816 * sigma), 2), round(min(5.0, mu + 1.2816 * sigma), 2)],
            "targetLevel": int(target),
            "probabilityAtOrAboveTarget": round(p_at_target, 3),
            "expectedShortfall": round(expected_shortfall(target, mu, sigma), 3),
            "responses": [{"itemId": r["itemId"], "level": r["level"], "correct": bool(r["correct"])}
                          for r in s["responses"]],
            "method": ("2PL IRT; prior = decayed belief / cohort prior; Laplace-approximated posterior; "
                       f"items chosen by maximum Fisher information; stop at σ < {TAU} (≥ {MIN_ITEMS} items) "
                       f"or {MAX_ITEMS} items."),
            "evidenceWritten": s["evidenceWritten"],
        }


SESSIONS = DiagnosticSessions()
