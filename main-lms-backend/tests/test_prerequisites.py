"""
Cross-competency prerequisite DAG (SCIL v6 §5): cycle rejection and
data-driven edge suggestions.

    pytest tests/test_prerequisites.py
"""
import json
import os
import random

from services import prerequisite_service as ps


def _edge(a, la, b, lb):
    return {"id": f"{a}>{b}", "from": {"competencyId": a, "level": la},
            "to": {"competencyId": b, "level": lb}, "source": "expert"}


def test_acyclic_expert_edges_are_accepted():
    res = ps.validate_edges([_edge("A", 2, "B", 3), _edge("B", 3, "C", 2)])
    assert res["cycle"] is None and len(res["edges"]) == 2 and not res["rejected"]


def test_cycle_through_the_level_ladders_is_rejected():
    # B@2 needs A@3 and A@2 needs B@3: with the ladders A@2→A@3 and B@2→B@3 that is
    # A@2 → A@3 → B@2 → B@3 → A@2 — neither can ever start.
    res = ps.validate_edges([_edge("A", 3, "B", 2), _edge("B", 3, "A", 2)])
    assert res["rejected"] and res["edges"] == []
    assert res["cycle"][0] == res["cycle"][-1]


def test_direct_cycle_is_rejected_and_self_edges_dropped():
    assert ps.find_cycle([_edge("A", 1, "B", 1), _edge("B", 1, "A", 1)])
    res = ps.validate_edges([_edge("A", 1, "A", 3)])
    assert res["edges"] == [] and res["invalid"] == 1


def test_generated_expert_edges_are_acyclic():
    path = os.path.join(os.path.dirname(__file__), "..", "..", "mock-igot-server", "data", "prerequisites.json")
    with open(path, encoding="utf-8") as fh:
        edges = json.load(fh)["edges"]
    assert ps.validate_edges(edges)["cycle"] is None
    assert all(e["source"] == "expert" for e in edges)


def _outcomes(bonus: float, n: int = 60, seed: int = 7):
    rng = random.Random(seed)
    rows = []
    for i in range(n):
        had = i % 2 == 0
        pre = rng.uniform(1.2, 1.9)
        gain = 0.5 + (bonus if had else 0.0) + rng.gauss(0, 0.15)
        rows.append({"learnerId": f"l{i}", "courseId": "c", "competencyId": "B", "courseLevel": 2,
                     "preTheta": pre, "postTheta": pre + gain,
                     "priorCompleted": [{"competencyId": "A", "level": 2}] if had else []})
    return rows


def test_planted_precedence_is_suggested_for_review_not_applied():
    res = ps.infer_edges(_outcomes(bonus=0.4), expert_edges=[])
    assert res["testedPairs"] == 1
    (s,) = res["suggestions"]
    assert s["from"]["competencyId"] == "A" and s["to"] == {"competencyId": "B", "competencyName": "B", "level": 2}
    assert s["status"] == "new_suggestion" and s["applied"] is False
    assert s["ci95"][0] > 0 and abs(s["effect"] - 0.4) < 0.15


def test_no_effect_gives_no_suggestion_and_expert_edges_are_recognised():
    assert ps.infer_edges(_outcomes(bonus=0.0), expert_edges=[])["suggestions"] == []
    res = ps.infer_edges(_outcomes(bonus=0.4), expert_edges=[_edge("A", 2, "B", 2)])
    assert res["suggestions"][0]["status"] == "supports_expert_edge"
