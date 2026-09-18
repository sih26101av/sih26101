"""
services/prerequisite_service.py — cross-competency prerequisite DAG (SCIL v6 §5)

* validate_edges — expert-seeded edges (competency@level → competency@level)
  are checked for cycles TOGETHER with the implicit within-competency ladder
  (c@L-1 → c@L). A cyclic edge set is rejected as a whole: build_study_plan
  then runs without cross-competency prerequisites and the admin endpoint shows
  the cycle.
* step_prerequisites — which edges a pathway step depends on (for the UI).
* infer_edges — data-driven SUGGESTIONS ("taking A before B shows higher gain
  on B") from course outcome assessments, for human review only. They are
  never applied to any plan.

Enforcement itself lives in recommendation_service._PrerequisiteGate.
"""
from __future__ import annotations

import math
import zlib
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Data-driven suggestion rules (all on the FRAC level scale of θ):
SUGGEST_MIN_GROUP = 8        # learners needed both with and without A before B
SUGGEST_MIN_EFFECT = 0.20    # extra gain on B (levels) worth an expert's time
SUGGEST_FDR = 0.10           # Benjamini–Hochberg false-discovery rate across all tested pairs
BOOTSTRAP_ROUNDS = 400       # resamples for the reported confidence interval


def _node(end: Dict[str, Any]) -> Tuple[str, int]:
    return end["competencyId"], int(end["level"])


def find_cycle(edges: List[Dict[str, Any]]) -> Optional[List[str]]:
    """Cycle through expert edges + ladder edges c@L-1 → c@L, or None if acyclic."""
    graph: Dict[Tuple[str, int], set] = {}
    comps = set()
    for e in edges:
        a, b = _node(e["from"]), _node(e["to"])
        graph.setdefault(a, set()).add(b)
        comps |= {a[0], b[0]}
    for c in comps:
        for lvl in range(1, 5):
            graph.setdefault((c, lvl), set()).add((c, lvl + 1))
    colour: Dict[Tuple[str, int], int] = {}

    for start in sorted(graph):
        if start in colour:
            continue
        stack = [(start, iter(sorted(graph.get(start, ()))))]
        path = [start]
        colour[start] = 1
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                colour[node] = 2
                stack.pop()
                path.pop()
            elif colour.get(nxt) == 1:
                cyc = path[path.index(nxt):] + [nxt]
                return [f"{c}@L{l}" for c, l in cyc]
            elif nxt not in colour:
                colour[nxt] = 1
                path.append(nxt)
                stack.append((nxt, iter(sorted(graph.get(nxt, ())))))
    return None


def validate_edges(edges: List[Dict[str, Any]]) -> Dict[str, Any]:
    """{'edges': usable edges ([] if rejected), 'cycle': None | [...], 'rejected': bool}."""
    clean = [e for e in edges or []
             if e.get("from", {}).get("competencyId") and e.get("to", {}).get("competencyId")
             and 1 <= int(e["from"].get("level") or 0) <= 5 and 1 <= int(e["to"].get("level") or 0) <= 5
             and e["from"]["competencyId"] != e["to"]["competencyId"]]
    cycle = find_cycle(clean)
    return {"edges": [] if cycle else clean, "cycle": cycle, "rejected": bool(cycle),
            "invalid": len(edges or []) - len(clean)}


def step_prerequisites(edges: List[Dict[str, Any]], comp_id: str, covers: List[int],
                       levels: Dict[str, Optional[int]], names: Dict[str, str]) -> List[Dict[str, Any]]:
    """Edges into `comp_id` at a level this step closes, with whether the official already meets them."""
    out = []
    for e in edges:
        if e["to"]["competencyId"] != comp_id or int(e["to"]["level"]) not in covers:
            continue
        a, need = e["from"]["competencyId"], int(e["from"]["level"])
        have = levels.get(a)
        out.append({"competencyId": a, "competencyName": names.get(a, a), "level": need,
                    "currentLevel": have, "met": None if have is None else have >= need,
                    "rationale": e.get("rationale"), "source": e.get("source", "expert")})
    return out


# ── Data-driven edge inference (suggestions for human review) ─────────────────

def _ols(y: np.ndarray, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Coefficients and their standard errors for y ~ x (x already has the intercept column)."""
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    resid = y - x @ beta
    dof = max(1, len(y) - x.shape[1])
    sigma2 = float(resid @ resid) / dof
    cov = sigma2 * np.linalg.pinv(x.T @ x)
    return beta, np.sqrt(np.clip(np.diag(cov), 0, None))


def _norm_sf(z: float) -> float:
    return 0.5 * math.erfc(z / math.sqrt(2))


def infer_edges(
    outcomes: List[Dict[str, Any]],
    expert_edges: List[Dict[str, Any]],
    names: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    For every (course competency B, level L) and every competency A that some
    takers had completed BEFORE the course: regress the gain on B
    (postθ − preθ) on [1, preθ, hadA]. The hadA coefficient is the extra gain
    associated with doing A first, adjusted for starting ability. Pairs with
    at least SUGGEST_MIN_GROUP learners on each side are tested; suggestions
    are those that pass Benjamini–Hochberg at SUGGEST_FDR with an effect of at
    least SUGGEST_MIN_EFFECT. This is observational: an association for an
    expert to review, never a causal claim, and never auto-applied.
    """
    names = names or {}
    groups: Dict[Tuple[str, int], List[Dict[str, Any]]] = {}
    for o in outcomes:
        groups.setdefault((o["competencyId"], int(o["courseLevel"])), []).append(o)
    expert = {(e["from"]["competencyId"], e["to"]["competencyId"]): e for e in expert_edges}

    tests = []
    for (b, level), rows in sorted(groups.items()):
        candidates = sorted({p["competencyId"] for r in rows for p in r.get("priorCompleted", [])} - {b})
        pre = np.array([r["preTheta"] for r in rows], dtype=float)
        gain = np.array([r["postTheta"] - r["preTheta"] for r in rows], dtype=float)
        for a in candidates:
            had = np.array([any(p["competencyId"] == a for p in r.get("priorCompleted", [])) for r in rows])
            n_with, n_without = int(had.sum()), int((~had).sum())
            if n_with < SUGGEST_MIN_GROUP or n_without < SUGGEST_MIN_GROUP:
                continue
            x = np.column_stack([np.ones(len(rows)), pre, had.astype(float)])
            beta, se = _ols(gain, x)
            effect, s = float(beta[2]), float(se[2]) or 1e-9
            tests.append({"a": a, "b": b, "level": level, "effect": effect, "se": s,
                          "p": 2 * _norm_sf(abs(effect) / s), "nWith": n_with, "nWithout": n_without,
                          "rows": rows, "had": had,
                          "fromLevel": int(round(float(np.median(
                              [p["level"] for r, h in zip(rows, had) if h for p in r["priorCompleted"]
                               if p["competencyId"] == a]))))})

    # Benjamini–Hochberg across every tested pair
    m = len(tests)
    ranked = sorted(tests, key=lambda t: t["p"])
    cutoff = 0
    for i, t in enumerate(ranked, start=1):
        if t["p"] <= SUGGEST_FDR * i / m:
            cutoff = i
    passing = [t for t in ranked[:cutoff] if t["effect"] >= SUGGEST_MIN_EFFECT]

    suggestions = []
    for t in passing:
        rng = np.random.default_rng(zlib.crc32(f"{t['a']}|{t['b']}|{t['level']}".encode()))
        rows, had = t["rows"], t["had"]
        pre = np.array([r["preTheta"] for r in rows], dtype=float)
        gain = np.array([r["postTheta"] - r["preTheta"] for r in rows], dtype=float)
        boots = []
        for _ in range(BOOTSTRAP_ROUNDS):
            idx = rng.integers(0, len(rows), len(rows))
            if had[idx].all() or not had[idx].any():
                continue
            x = np.column_stack([np.ones(len(idx)), pre[idx], had[idx].astype(float)])
            boots.append(float(np.linalg.lstsq(x, gain[idx], rcond=None)[0][2]))
        lo, hi = (np.percentile(boots, [2.5, 97.5]) if boots else (float("nan"), float("nan")))
        ex = expert.get((t["a"], t["b"]))
        suggestions.append({
            "from": {"competencyId": t["a"], "competencyName": names.get(t["a"], t["a"]), "level": t["fromLevel"]},
            "to": {"competencyId": t["b"], "competencyName": names.get(t["b"], t["b"]), "level": t["level"]},
            "effect": round(t["effect"], 3), "ci95": [round(float(lo), 3), round(float(hi), 3)],
            "pValue": round(t["p"], 6), "nWith": t["nWith"], "nWithout": t["nWithout"],
            "status": "supports_expert_edge" if ex else "new_suggestion",
            "expertEdgeId": ex["id"] if ex else None,
            "applied": False,
        })
    suggestions.sort(key=lambda s: (s["status"] != "new_suggestion", -s["effect"]))
    return {
        "testedPairs": m,
        "fdr": SUGGEST_FDR,
        "minEffect": SUGGEST_MIN_EFFECT,
        "minGroup": SUGGEST_MIN_GROUP,
        "suggestions": suggestions,
        "method": ("gain on B (postθ − preθ) regressed on [1, preθ, completed A before B] per (B, level); "
                   f"pairs with ≥{SUGGEST_MIN_GROUP} learners each side; Benjamini–Hochberg FDR "
                   f"{SUGGEST_FDR:.0%}; effect ≥ {SUGGEST_MIN_EFFECT} levels; 95% bootstrap CI "
                   f"({BOOTSTRAP_ROUNDS} resamples). Observational association — for expert review, never "
                   "applied automatically."),
    }
