"""
Skill-gap levels + level-aware recommendations + learning pathways.

Runs on a tiny synthetic catalogue with a deterministic bag-of-words stub
embedder, so no model download is needed:  pytest tests/test_pathway.py
"""
import hashlib
import json

import numpy as np
import pytest

import services.recommendation_service as rs
from services.baseline_assembler import BaselineAssembler, resolve_level
from services.competency_service import CompetencyCalculator

_DIM = 256


class _StubEmbedder:
    """Hashed bag-of-words → L2-normalised vector. Shared words ⇒ positive cosine."""

    def encode(self, texts, kind=None, batch_size=None, normalize_embeddings=True,
               show_progress_bar=False):
        out = np.zeros((len(texts), _DIM), dtype="float32")
        for row, text in enumerate(texts):
            for word in text.lower().replace(".", " ").split():
                out[row, int(hashlib.md5(word.encode()).hexdigest(), 16) % _DIM] += 1.0
            norm = np.linalg.norm(out[row])
            if norm:
                out[row] /= norm
        return out


def _frac(cid, name, desc):
    return {
        "id": cid, "name": name, "description": desc, "competencyType": "Domain",
        "children": [{"level": n, "description": f"{name} level {n} descriptor"} for n in range(1, 6)],
    }


def _course(cid, name, tags, hours=1.0, **quality):
    return {
        "identifier": cid, "name": name, "description": name,
        "duration": str(int(hours * 3600)),
        "competencies_v3": json.dumps([
            {"id": comp, "name": comp, "competencyType": "Domain", "competencyLevel": f"Level {lvl}"}
            for comp, lvl in tags
        ]),
        **quality,
    }


CATALOG = [
    _course("a1", "survey sampling basics", [("comp_a", 1)]),
    _course("a2", "survey sampling design", [("comp_a", 2)], hours=2.0),
    # mis-tagged: great quality numbers, content unrelated to comp_a
    _course("a2x", "cooking recipes weekend", [("comp_a", 2)],
            rating=5.0, rating_count=500, enrollment_count=9000, completion_rate=0.95),
    # no Level-3 course for comp_a — a catalogue hole
    _course("a4", "survey sampling estimation advanced", [("comp_a", 4)], hours=3.0),
    _course("a5", "survey sampling estimation expert", [("comp_a", 5)], hours=4.0),
    _course("b1", "price index numbers", [("comp_b", 1)]),
    # the only Level-2 comp_b course also teaches comp_a at Level 1
    _course("shared", "survey sampling for price index inflation", [("comp_a", 1), ("comp_b", 2)]),
    _course("f1", "leadership skills workshop", []),
    _course("f2", "office file management", []),
    _course("f3", "email etiquette", []),
    _course("f4", "public speaking", []),
]


@pytest.fixture
def engine(tmp_path, monkeypatch):
    monkeypatch.setattr(rs, "get_embedder", lambda role=None: _StubEmbedder())
    cat, frac = tmp_path / "catalog.json", tmp_path / "frac.json"
    cat.write_text(json.dumps(CATALOG), encoding="utf-8")
    frac.write_text(json.dumps([
        _frac("comp_a", "Survey Sampling", "survey sampling design estimation"),
        _frac("comp_b", "Price Index", "price index numbers inflation"),
    ]), encoding="utf-8")
    return rs.HybridRecommendationEngine(str(cat), str(frac))


def _gap(engine, comp, current, target):
    return engine.calculate_gaps({comp: current}, {comp: target})[0]


def _kinds_levels(pathway):
    return [(s["kind"], s["toLevel"]) for s in pathway["steps"]]


# ── Catalogue parsing ─────────────────────────────────────────────────────────

def test_course_levels_are_kept(engine):
    assert engine.course_comp_levels()["a2"] == {"comp_a": 2}
    assert engine.course_comp_levels()["shared"] == {"comp_a": 1, "comp_b": 2}
    assert engine.levels_available("comp_a") == {1, 2, 4, 5}


# ── Level-gated flat recommendations ──────────────────────────────────────────

def test_beginner_gets_next_levels_in_order_never_advanced_or_basic(engine):
    recs = engine.get_recommendations([_gap(engine, "comp_a", 1, 4)], limit_per_gap=3)
    levels = [r.courseLevel for r in recs]
    assert levels and all(1 < lvl <= 4 for lvl in levels)       # no L1 refresher, no L5
    assert levels[:2] == [2, 4]                                   # best of each level, lowest first


def test_expert_only_sees_courses_above_their_level(engine):
    recs = engine.get_recommendations([_gap(engine, "comp_a", 4, 5)], limit_per_gap=3)
    assert [r.courseId for r in recs] == ["a5"]


def test_hole_band_falls_back_to_nearest_level_above_target(engine):
    recs = engine.get_recommendations([_gap(engine, "comp_a", 2, 3)], limit_per_gap=3)
    assert [r.courseLevel for r in recs] == [4]
    assert any("stretch" in reason for reason in recs[0].matchReasons)


def test_unassessed_is_not_ranked_as_a_gap(engine):
    gaps = engine.calculate_gaps({"comp_a": 2.0}, {"comp_a": 4.0, "comp_b": 3.0})
    assert [g.competencyId for g in gaps] == ["comp_a"]


# ── Pathways ──────────────────────────────────────────────────────────────────

def test_pathway_climbs_one_level_at_a_time_and_bridges_holes(engine):
    p = engine.build_pathway("comp_a", "", 1, 4, confidence="HIGH")
    assert _kinds_levels(p) == [("course", 2), ("stretch", 4)]
    stretch = p["steps"][1]
    assert stretch["covers"] == [3, 4] and stretch["course"]["courseId"] == "a4"
    assert p["coverageGaps"] == [3] and p["status"] == "ready"
    assert p["totalHours"] == 5.0                                  # a2 2h + a4 3h
    assert p["steps"][0]["levelDescriptor"] == "Survey Sampling level 2 descriptor"


def test_content_supported_course_beats_better_rated_mistagged_one(engine):
    p = engine.build_pathway("comp_a", "", 1, 2, confidence="HIGH")
    step = p["steps"][0]
    assert step["course"]["courseId"] == "a2"
    assert [a["courseId"] for a in step["alternatives"]] == ["a2x"]
    assert step["alternatives"][0]["tagSupported"] is False
    assert p["tagReviewFlags"] == []


def test_mistagged_course_is_used_only_as_last_resort_and_flagged(engine):
    p = engine.build_pathway("comp_a", "", 1, 2, confidence="HIGH", completed_ids={"a2"})
    step = p["steps"][0]
    assert step["course"]["courseId"] == "a2x"
    assert "flagged for review" in step["reason"]
    assert p["tagReviewFlags"] == ["a2x"]


def test_top_of_ladder_hole_uses_closest_course_above_target(engine):
    p = engine.build_pathway("comp_a", "", 2, 3, confidence="HIGH")
    (step,) = p["steps"]
    assert step["kind"] == "stretch" and step["toLevel"] == 3
    assert step["course"]["courseLevel"] == 4 and p["status"] == "ready"


def test_unassessed_starts_with_diagnostic_then_from_level_zero(engine):
    p = engine.build_pathway("comp_a", "", None, 2, confidence="UNASSESSED", basis="none")
    assert p["needsDiagnostic"] and p["steps"][0]["kind"] == "diagnostic"
    assert [lvl for kind, lvl in _kinds_levels(p) if kind != "diagnostic"] == [1, 2]


def test_self_reported_level_gets_diagnostic_and_optional_bridge_rungs(engine):
    p = engine.build_pathway("comp_a", "", 3, 5, confidence="LOW",
                             basis="self_report", evidence_level=1)
    assert _kinds_levels(p) == [("diagnostic", 3), ("bridge", 2), ("course", 4), ("course", 5)]
    assert p["bridgeHours"] == 2.0 and p["totalHours"] == 7.0      # bridge not in total


def test_completed_never_suggested_and_in_progress_is_continued(engine):
    p = engine.build_pathway("comp_a", "", 3, 5, confidence="HIGH",
                             completed_ids={"a5"}, in_progress={"a4": 50.0})
    kinds = _kinds_levels(p)
    assert kinds[0] == ("continue", 4)
    assert p["steps"][0]["hours"] == 1.5                           # half of 3h left
    assert all(s["course"]["courseId"] != "a5" for s in p["steps"] if s["course"])
    assert p["status"] == "partial" and p["unreachableLevels"] == [5]


def test_met_target_offers_one_optional_next_level(engine):
    p = engine.build_pathway("comp_a", "", 4, 4, confidence="HIGH")
    assert p["status"] == "met" and _kinds_levels(p) == [("optional", 5)]
    assert p["totalHours"] == 0


# ── Study plan ────────────────────────────────────────────────────────────────

def test_study_plan_keeps_ladder_order_and_shares_courses(engine):
    pa = engine.build_pathway("comp_a", "", 0, 2, confidence="HIGH")
    pb = engine.build_pathway("comp_b", "", 1, 2, confidence="HIGH")
    plan = engine.build_study_plan([pa, pb])
    ids = [s["courseId"] for s in plan["steps"]]
    assert ids == ["shared", "a2"]                  # one course closes two rungs; a1 never needed
    assert {a["competencyId"] for a in plan["steps"][0]["advances"]} == {"comp_a", "comp_b"}
    assert pa["steps"][0]["course"]["courseId"] == "shared"         # pathway updated to match
    assert plan["deferred"] == []


def test_study_plan_budget_defers_ladders_that_do_not_fit(engine):
    pa = engine.build_pathway("comp_a", "", 3, 5, confidence="HIGH")   # a4 3h → a5 4h
    plan = engine.build_study_plan([pa], budget_hours=5)
    assert [s["courseId"] for s in plan["steps"]] == ["a4"]
    assert plan["totalHours"] <= 5
    assert plan["deferred"][0]["remainingSteps"] == 1


def test_study_plan_lists_diagnostics_and_skips_unassessed_ladders(engine):
    pu = engine.build_pathway("comp_b", "", None, 2, confidence="UNASSESSED", basis="none")
    plan = engine.build_study_plan([pu])
    assert plan["steps"] == [] and plan["diagnostics"][0]["competencyId"] == "comp_b"


# ── Opportunity to practise: ordinal tie-breaker only (SCIL v6 §4) ────────────

def _two_level1_ladders(engine, opp_a=None, opp_b=None, hours_b=None):
    pa = engine.build_pathway("comp_a", "Survey Sampling", 0, 1, confidence="HIGH",
                              completed_ids={"shared"})
    pb = engine.build_pathway("comp_b", "Price Index", 0, 1, confidence="HIGH")
    pa["opportunity"] = {"level": opp_a} if opp_a else None
    pb["opportunity"] = {"level": opp_b} if opp_b else None
    if hours_b is not None:
        pb["steps"][0]["hours"] = hours_b
    return [pa, pb]


def test_opportunity_breaks_near_ties_towards_the_practisable_gap(engine):
    plain = engine.build_study_plan(_two_level1_ladders(engine))
    first = plain["steps"][0]["advances"][0]["competencyId"]
    other = "comp_b" if first == "comp_a" else "comp_a"
    opp = {first: "Low", other: "High"}
    plan = engine.build_study_plan(_two_level1_ladders(engine, opp["comp_a"], opp["comp_b"]))
    assert plan["steps"][0]["advances"][0]["competencyId"] == other
    assert plan["steps"][0]["selectedBy"] == "opportunity_tie_break"
    assert plan["steps"][0]["opportunity"] == "High"
    # never hides a gap: the low-opportunity ladder is still scheduled
    assert {s["advances"][0]["competencyId"] for s in plan["steps"]} == {"comp_a", "comp_b"}


def test_opportunity_never_overrides_a_clear_gain_per_hour_winner(engine):
    # comp_b's course is 5× longer → far outside the tie band; High opportunity can't pull it forward
    plan = engine.build_study_plan(_two_level1_ladders(engine, "Low", "High", hours_b=5.0))
    assert plan["steps"][0]["advances"][0]["competencyId"] == "comp_a"
    assert plan["steps"][0]["selectedBy"] == "gain_per_hour"
    assert rs.OPPORTUNITY_TIE_BAND == 0.10


# ── ACBP mandatory courses, budget, modality mix (SCIL v6 §5) ─────────────────

_MANDATORY_A1 = {"courseId": "a1", "title": "survey sampling basics", "competencyId": "comp_a",
                 "hours": 1.0, "aparLinked": True, "reason": "Mandatory (ACBP)"}


def test_mandatory_course_goes_first_even_over_budget(engine):
    pb = engine.build_pathway("comp_b", "Price Index", 0, 1, confidence="HIGH")
    plan = engine.build_study_plan([pb], budget_hours=0.5, mandatory=[_MANDATORY_A1])
    assert plan["steps"][0]["courseId"] == "a1" and plan["steps"][0]["mandatory"]
    assert plan["steps"][0]["kind"] == "mandatory" and plan["steps"][0]["selectedBy"] == "mandatory_acbp"
    assert plan["overBudget"] is True and plan["mandatory"][0]["status"] == "scheduled"
    assert plan["deferred"][0]["competencyId"] == "comp_b" and plan["deferred"][0]["reason"] == "over budget"


def test_completed_mandatory_course_is_listed_not_rescheduled(engine):
    pb = engine.build_pathway("comp_b", "Price Index", 0, 1, confidence="HIGH")
    plan = engine.build_study_plan([pb], mandatory=[_MANDATORY_A1], completed_ids={"a1"})
    assert plan["mandatory"][0]["status"] == "completed"
    assert "a1" not in [s["courseId"] for s in plan["steps"]]


def test_mandatory_course_advances_its_ladder_and_is_never_taken_twice(engine):
    pa = engine.build_pathway("comp_a", "Survey Sampling", 0, 2, confidence="HIGH",
                              completed_ids={"shared"})
    mandatory_a2 = {**_MANDATORY_A1, "courseId": "a2", "hours": 2.0}   # the L2 rung, forced first
    plan = engine.build_study_plan([pa], mandatory=[mandatory_a2])
    ids = [s["courseId"] for s in plan["steps"]]
    assert ids[0] == "a2" and ids.count("a2") == 1
    assert ids == ["a2", "a1"]
    # the L2 rung was absorbed by the already-planned mandatory course
    assert [a["toLevel"] for a in plan["steps"][0]["advances"]] == [2]
    assert plan["deferred"] == []


def test_classroom_cap_defers_the_ladder(tmp_path, monkeypatch):
    monkeypatch.setattr(rs, "get_embedder", lambda role=None: _StubEmbedder())
    cat = [_course("c1", "survey sampling programme", [("comp_a", 1)], hours=3.0, modality="classroom"),
           _course("p1", "price index numbers", [("comp_b", 1)], hours=1.0, modality="self_paced")]
    eng = rs.HybridRecommendationEngine(
        catalog=cat, frac=[_frac("comp_a", "Survey Sampling", "survey sampling"),
                           _frac("comp_b", "Price Index", "price index numbers")])
    paths = [eng.build_pathway("comp_a", "Survey Sampling", 0, 1, confidence="HIGH"),
             eng.build_pathway("comp_b", "Price Index", 0, 1, confidence="HIGH")]
    plan = eng.build_study_plan(paths, budget_hours=10, classroom_cap_hours=2.0)
    assert [s["courseId"] for s in plan["steps"]] == ["p1"]
    assert plan["deferred"] == [{"competencyId": "comp_a", "competencyName": "Survey Sampling",
                                 "remainingSteps": 1, "remainingHours": 3.0, "reason": "classroom cap"}]
    assert plan["classroomHours"] == 0.0 and plan["classroomCapHours"] == 2.0


# ── Cross-competency prerequisite DAG (SCIL v6 §5, B4) ────────────────────────

def _edge(a, la, b, lb):
    return {"id": f"{a}>{b}", "from": {"competencyId": a, "level": la},
            "to": {"competencyId": b, "level": lb}, "source": "expert"}


def test_prerequisite_edge_orders_the_dependent_ladder_after_its_prerequisite(engine):
    first = engine.build_study_plan(_two_level1_ladders(engine))["steps"][0]["advances"][0]["competencyId"]
    other = "comp_b" if first == "comp_a" else "comp_a"
    # make the normally-first ladder depend on the other one
    plan = engine.build_study_plan(_two_level1_ladders(engine), prerequisites=[_edge(other, 1, first, 1)],
                                   current_levels={"comp_a": 0, "comp_b": 0})
    order = [s["advances"][0]["competencyId"] for s in plan["steps"]]
    assert order == [other, first]
    assert [a["status"] for a in plan["prerequisitesApplied"]] == ["ordered"]


def test_unmet_prerequisite_defers_the_ladder_with_its_reason(engine):
    # comp_a L1 needs comp_b L1, but comp_b's course doesn't fit the budget
    plan = engine.build_study_plan(_two_level1_ladders(engine, hours_b=5.0), budget_hours=2.0,
                                   prerequisites=[_edge("comp_b", 1, "comp_a", 1)],
                                   current_levels={"comp_a": 0, "comp_b": 0})
    assert plan["steps"] == []
    reasons = {d["competencyId"]: d["reason"] for d in plan["deferred"]}
    assert reasons["comp_b"] == "over budget"
    assert reasons["comp_a"] == "prerequisite: Price Index Level 1 first"
    assert plan["prerequisitesApplied"][0]["status"] == "blocked"


def test_unknown_prerequisite_level_is_advisory_only(engine):
    plan = engine.build_study_plan(_two_level1_ladders(engine),
                                   prerequisites=[_edge("comp_zzz", 3, "comp_a", 1)],
                                   current_levels={"comp_a": 0, "comp_b": 0})
    assert {s["advances"][0]["competencyId"] for s in plan["steps"]} == {"comp_a", "comp_b"}
    assert plan["prerequisitesApplied"][0]["status"] == "advisory"


def test_already_met_prerequisite_changes_nothing(engine):
    base = engine.build_study_plan(_two_level1_ladders(engine))
    plan = engine.build_study_plan(_two_level1_ladders(engine), prerequisites=[_edge("comp_zzz", 2, "comp_a", 1)],
                                   current_levels={"comp_a": 0, "comp_b": 0, "comp_zzz": 3})
    assert [s["courseId"] for s in plan["steps"]] == [s["courseId"] for s in base["steps"]]
    assert plan["prerequisitesApplied"] == []


# ── Crosswalk: role competency ids outside the catalogue's FRAC set ───────────

def test_crosswalk_exact_semantic_and_rejected(engine):
    assert engine.crosswalk("comp_a", "anything")["method"] == "exact"
    xw = engine.crosswalk("CID0001", "Survey Sampling Design")
    assert xw["catalogueId"] == "comp_a" and xw["method"] == "semantic_crosswalk"
    assert engine.crosswalk("CID0002", "Gardening Club") is None


def test_crosswalked_competency_gets_a_ladder_under_its_own_id(engine):
    p = engine.build_pathway("comp_a", "Survey Sampling Design", 1, 2, confidence="HIGH",
                             role_comp_id="CID0001")
    assert p["competencyId"] == "CID0001" and p["catalogueCompetencyId"] == "comp_a"
    assert _kinds_levels(p) == [("course", 2)]
    gaps = engine.calculate_gaps({"CID0001": 1.0}, {"CID0001": 2.0},
                                 catalogue_ids={"CID0001": "comp_a"})
    recs = engine.get_recommendations(gaps, limit_per_gap=1)
    assert recs[0].competencyId == "CID0001" and recs[0].courseLevel == 2


def test_curated_crosswalk_is_used_before_embeddings(tmp_path, monkeypatch):
    monkeypatch.setattr(rs, "get_embedder", lambda role=None: _StubEmbedder())
    eng = rs.HybridRecommendationEngine(
        catalog=CATALOG,
        frac=[_frac("comp_a", "Survey Sampling", "survey sampling design estimation"),
              _frac("comp_b", "Price Index", "price index numbers inflation")],
        crosswalk=[{"cidId": "CID0100", "fracId": "comp_b", "confirmed": False},
                   {"cidId": "CID0101", "fracId": None, "confirmed": False}],
    )
    xw = eng.crosswalk("CID0100", "Survey Sampling Design")   # the name alone would say comp_a
    assert xw["catalogueId"] == "comp_b" and xw["method"] == "curated_crosswalk"
    assert xw["confirmed"] is False
    assert eng.crosswalk("CID0101", "Survey Sampling Design")["method"] == "semantic_crosswalk"
    assert eng.catalog_source == "adapter"


def test_explicit_non_tpac_flag_is_not_overridden_by_creator_name(tmp_path, monkeypatch):
    monkeypatch.setattr(rs, "get_embedder", lambda role=None: _StubEmbedder())
    nssta = "National Statistical Systems Training Academy (NSSTA)"
    cat = [
        {**_course("t1", "survey sampling programme", [("comp_a", 3)]), "creator": nssta, "is_tpac": True},
        {**_course("t2", "survey sampling workshop", [("comp_a", 3)]), "creator": nssta, "is_tpac": False},
        {**_course("t3", "survey sampling legacy", [("comp_a", 3)]), "creator": nssta},
    ]
    eng = rs.HybridRecommendationEngine(catalog=cat, frac=[_frac("comp_a", "Survey Sampling", "survey")])
    src = {d.identifier: d.tpac_source for d in eng._catalog}
    assert src == {"t1": "verified", "t2": "none", "t3": "inferred"}


def test_uncatalogued_competency_reports_no_content(engine):
    p = engine.build_pathway("CID0002", "Gardening Club", 1, 3, confidence="HIGH")
    assert p["status"] == "no_content" and p["message"]


def test_completion_evidence_follows_the_crosswalk():
    user = {**_USER, "competencies": [{"id": "CID0009", "name": "Survey Design", "type": "Domain",
                                       "requiredLevel": 4, "competencyLevel": ""}]}
    asm = BaselineAssembler({"course_A": {"comp_x": 3}})
    bline = asm.compute_for_user(user, [{"courseId": "course_A", "status": 2}], [],
                                 comp_aliases={"CID0009": "comp_x"})["CID0009"]
    assert bline["completedLevel"] == 3 and resolve_level(bline, 0)["level"] == 3


# ── Baseline formula + level resolution (bugs found in review) ────────────────

_USER = {
    "experienceYears": 8, "jobProfile": {"tier": "TIER3_MID"},
    "education": [{"degree": "MSc Statistics"}],
    "careerHistory": [{"title": "Survey Officer", "duration_years": 6}],
    "competencies": [{"id": "comp_x", "name": "Survey Design", "type": "Domain",
                      "requiredLevel": 4, "competencyLevel": "Level 4"}],
}


def _resolved(enrollments):
    asm = BaselineAssembler({"course_A": {"comp_x": 3}})
    bline = asm.compute_for_user(_USER, enrollments, [])["comp_x"]
    return bline, resolve_level(bline, 4)


def test_finishing_a_course_never_lowers_the_level():
    before  = _resolved([])[1]
    partial = _resolved([{"courseId": "course_A", "completionPercentage": 10}])[1]
    done    = _resolved([{"courseId": "course_A", "completionPercentage": 100}])[1]
    assert before["level"] == partial["level"] == done["level"] == 4
    assert done["evidenceLevel"] == 3                 # completed Level-3 course is evidence


def test_partial_progress_is_not_verified_evidence():
    bline, _ = _resolved([{"courseId": "course_A", "completionPercentage": 10}])
    assert bline["_evidence"]["verified"] == 0 and bline["confidence"] == "LOW"


def test_missing_channels_do_not_drag_the_score_to_zero():
    score, conf = CompetencyCalculator().calculate_baseline(
        "Domain", {"verified": 4.0}, 0, verified_scores_by_comp={}, comp_id="comp_x",
    )
    assert (score, conf) == (4.0, "HIGH")


def test_evidence_can_close_a_gap():
    """The old `requiredLevel - 1` cap made every evidence-backed gap permanent."""
    asm = BaselineAssembler({"course_A": {"comp_x": 5}})
    user = {**_USER, "competencies": [{**_USER["competencies"][0], "competencyLevel": ""}]}
    bline = asm.compute_for_user(user, [{"courseId": "course_A", "status": 2}], [])["comp_x"]
    assert resolve_level(bline, 0)["level"] >= 4


def test_no_evidence_and_no_claim_is_unassessed():
    res = resolve_level({"confidence": "UNASSESSED", "currentLevel": None}, 0)
    assert res == {"level": None, "confidence": "UNASSESSED", "basis": "none", "evidenceLevel": None}


def test_self_report_above_evidence_is_flagged_low():
    res = resolve_level({"confidence": "HIGH", "currentLevel": 2, "completedLevel": 2}, 4)
    assert res == {"level": 4, "confidence": "LOW", "basis": "self_report", "evidenceLevel": 2}
