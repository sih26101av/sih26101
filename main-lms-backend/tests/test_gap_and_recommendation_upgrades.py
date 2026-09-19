"""
Skill-gap + recommendation upgrades: rater leniency, "why this level", the
/baseline assembler path, career readiness, TPAC provenance boost, format
spread, opportunity tie-break, mandatory ACBP courses, stored embeddings,
feedback votes and level-dispute resolution.

No model download and no shared database: the engine uses the stub embedder
from test_pathway, and DB tests run on an in-memory SQLite session.
"""
import asyncio

import numpy as np
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import services.recommendation_service as rs
from services.baseline_assembler import _workplace_channels, assess_competency, explain_level, resolve_level
from services.competency_service import correct_supervisor_rating, rater_leniency_offsets
from test_pathway import CATALOG, _StubEmbedder, _frac, _gap, engine  # noqa: F401  (fixture)


# ── Rater leniency ────────────────────────────────────────────────────────────

def test_lenient_rater_is_corrected_down_and_shrunk():
    ratings = ([{"raterId": "lenient", "grantedValue": 5}] * 10
               + [{"raterId": "strict", "grantedValue": 2}] * 10)
    off = rater_leniency_offsets(ratings)
    assert off["lenient"]["offset"] > 0 > off["strict"]["offset"]
    # shrinkage: n/(n+k) = 10/15 of the raw 1.5 mean offset
    assert off["lenient"]["offset"] == pytest.approx(1.5 * 10 / 15, abs=1e-3)
    assert correct_supervisor_rating(5, "lenient", off)[0] == pytest.approx(5 - 1.0, abs=1e-3)
    assert correct_supervisor_rating(4, "unknown", off) == (4.0, 0.0)


def test_rater_with_too_few_ratings_is_not_corrected():
    off = rater_leniency_offsets([{"raterId": "a", "grantedValue": 5}] * 2
                                 + [{"raterId": "b", "grantedValue": 1}] * 10)
    assert off["a"]["offset"] == 0.0


def test_supervisor_channel_uses_corrected_rating():
    rows = [{"evidence_type": "SUPERVISOR_RATING", "granted_value": 5, "issue_date": "2026-01-01",
             "meta": {"raterId": "r1"}}]
    work = _workplace_channels(rows, {"r1": {"offset": 0.8}})
    assert work["S_raw"] == 5 and work["S"] == pytest.approx(4.2) and work["raterOffset"] == 0.8


# ── Why this level ────────────────────────────────────────────────────────────

def test_explanation_names_the_completed_course_that_sets_the_level():
    a = assess_competency("Domain", "comp_a", {"verified": 3.0, "tenure": 1.0}, work={}, completed_level=3)
    res = resolve_level(a, 0)
    why = explain_level(a, res, 0, [{"courseId": "c1", "title": "Sampling L3", "level": 3}])
    assert why["factors"][0]["key"] == "verified" and "Sampling L3" in why["factors"][0]["detail"]
    assert why["summary"].startswith(f"Level {res['level']}")


def test_explanation_flags_self_report_and_the_documented_cap():
    a = assess_competency("Domain", "comp_a", {"documented": 3.0}, work={})
    res = resolve_level(a, 4)
    why = explain_level(a, res, 4)
    assert why["basis"] == "self_report"
    assert any(f["key"] == "selfReport" and f["role"] == "sets_level" for f in why["factors"])
    assert any("capped at 3.5" in c for c in why["caps"])
    assert any("level check" in c for c in why["caps"])


def test_unassessed_explanation():
    a = assess_competency("Domain", "comp_a", {}, work={})
    why = explain_level(a, resolve_level(a, 0), 0)
    assert why["summary"].startswith("Not assessed")


# ── /baseline on the assembler path ───────────────────────────────────────────

def test_baseline_endpoint_uses_assembler_and_floors():
    from routers.competency import EvidencePayload, calculate_baseline
    out = asyncio.run(calculate_baseline(EvidencePayload(
        frac_type="Domain", comp_id="comp_x", documented=2.0, work_sample_level=4, work_sample_passed=True)))
    assert out["level"] == 4 and out["basis"] == "work_sample" and out["confidence"] == "HIGH"
    assert out["channels"]["A"] == 4.0 and "whyThisLevel" in out


# ── Career readiness ─────────────────────────────────────────────────────────

def test_office_ladder_and_readiness():
    from routers.career import office_ladder, readiness_for
    roles = {
        "jr": {"roleId": "jr", "officeId": "o", "tier": "TIER4_JUNIOR", "designation": "JSO"},
        "mid": {"roleId": "mid", "officeId": "o", "tier": "TIER3_MID", "designation": "AD"},
        "top": {"roleId": "top", "officeId": "o", "tier": "TIER1_APEX", "designation": "ADG"},
        "other": {"roleId": "other", "officeId": "x", "tier": "TIER3_MID", "designation": "AD"},
    }
    assert [t[0]["roleId"] for t in office_ladder(roles, "o")] == ["jr", "mid", "top"]
    rd = readiness_for([{"id": "a", "requiredLevel": 4}, {"id": "b", "requiredLevel": 2},
                        {"id": "c", "requiredLevel": 3}],
                       {"a": {"level": 2}, "b": {"level": 3}}, {})
    # (2/4 + 1 + 0) / 3 = 50%; c has no evidence → unassessed, not level 0 met
    assert rd["readinessPct"] == 50 and rd["metCount"] == 1 and rd["unassessedCount"] == 1
    assert rd["competencies"][0]["competencyId"] == "a"         # largest gap first


# ── Recommendation engine ────────────────────────────────────────────────────

def test_tpac_boost_depends_on_provenance(tmp_path, monkeypatch):
    import json
    monkeypatch.setattr(rs, "get_embedder", lambda role=None: _StubEmbedder())
    same = "survey sampling design"
    cat = [
        {"identifier": "v", "name": same, "description": same, "duration": "3600", "is_tpac": True,
         "competencies_v3": json.dumps([{"id": "comp_a", "competencyLevel": "Level 2"}])},
        {"identifier": "i", "name": same, "description": same, "duration": "3600", "creator": "NSSTA",
         "competencies_v3": json.dumps([{"id": "comp_a", "competencyLevel": "Level 2"}])},
        {"identifier": "n", "name": same, "description": same, "duration": "3600", "is_tpac": False,
         "competencies_v3": json.dumps([{"id": "comp_a", "competencyLevel": "Level 2"}])},
    ]
    (tmp_path / "c.json").write_text(json.dumps(cat), encoding="utf-8")
    (tmp_path / "f.json").write_text(json.dumps([_frac("comp_a", "Survey Sampling", same)]), encoding="utf-8")
    eng = rs.HybridRecommendationEngine(str(tmp_path / "c.json"), str(tmp_path / "f.json"))
    scores = dict((eng._catalog[i].identifier, s) for i, s in eng._retrieve_for_gap(_gap(eng, "comp_a", 1, 3)))
    assert scores["v"] > scores["i"] > scores["n"]


def _rec(cid, level, modality, score):
    return rs.RecommendationResult(courseId=cid, title=cid, provider="p", durationHours=1, finalScore=score,
                                   relevanceScore=score, qualityScore=0, isTpac=False, competencyId="c",
                                   competencyName="c", priorityRank=0, matchReasons=[], courseLevel=level,
                                   modality=modality)


def test_formats_are_spread_among_near_equal_courses_only():
    ordered = [_rec("a", 2, "self_paced", 0.9), _rec("b", 2, "self_paced", 0.85),
               _rec("c", 2, "classroom", 0.8), _rec("d", 2, "virtual_lab", 0.3)]
    # 2 slots: the near-equal classroom course replaces the second self-paced one
    assert [r.courseId for r in rs._spread_modalities(ordered, 2)] == ["a", "c"]
    # the weak lab course is never promoted; picks keep their original order
    assert [r.courseId for r in rs._spread_modalities(ordered, 3)] == ["a", "b", "c"]
    assert [r.courseId for r in rs._spread_modalities(ordered, 1)] == ["a"]


def test_opportunity_breaks_priority_ties_only(engine):
    g1 = engine.calculate_gaps({"comp_a": 1}, {"comp_a": 3})[0]
    g2 = engine.calculate_gaps({"comp_b": 1}, {"comp_b": 3})[0]
    g3 = engine.calculate_gaps({"comp_c": 1}, {"comp_c": 5})[0]      # clearly bigger gap
    out = engine.order_gaps_by_opportunity([g3, g1, g2], {"comp_a": "Low", "comp_b": "High", "comp_c": "Low"})
    assert [g.competencyId for g in out] == ["comp_c", "comp_b", "comp_a"]


def test_mandatory_courses_always_included_with_badge(engine):
    gap = _gap(engine, "comp_a", 1, 4)
    mand = [{"courseId": "a4", "competencyId": "comp_a", "level": 4, "aparLinked": True, "reason": "ACBP"},
            {"courseId": "gone", "competencyId": "comp_z", "title": "Not in catalogue", "hours": 2}]
    recs = engine.mandatory_recommendations(mand, exclude_ids=set(), gaps={"comp_a": gap})
    assert [r.courseId for r in recs] == ["a4", "gone"] and all(r.mandatory for r in recs)
    assert recs[0].why["badges"][0]["key"] == "mandatory" and recs[0].why["gap"]["competencyId"] == "comp_a"
    assert engine.mandatory_recommendations(mand, exclude_ids={"a4"}, gaps={})[0].courseId == "gone"


def test_why_recommended_describes_the_level_step(engine):
    recs = engine.get_recommendations([_gap(engine, "comp_a", 1, 4)], limit_per_gap=3)
    first = recs[0]
    assert first.why["gap"]["competencyId"] == "comp_a"
    assert first.why["levelStep"] == {"from": 1, "to": first.courseLevel, "kind": "next_step"}


def test_stored_embeddings_are_reused_only_when_text_matches(tmp_path, monkeypatch):
    import json
    monkeypatch.setattr(rs, "get_embedder", lambda role=None: _StubEmbedder())
    (tmp_path / "c.json").write_text(json.dumps(CATALOG), encoding="utf-8")
    (tmp_path / "f.json").write_text(json.dumps([_frac("comp_a", "Survey", "survey")]), encoding="utf-8")
    first = rs.HybridRecommendationEngine(str(tmp_path / "c.json"), str(tmp_path / "f.json"))
    stored = {cid: (h, v) for cid, h, v in first.course_embeddings()}
    stored["a1"] = ("stale-hash", np.zeros_like(stored["a1"][1]))
    again = rs.HybridRecommendationEngine(str(tmp_path / "c.json"), str(tmp_path / "f.json"),
                                          precomputed_embeddings=stored)
    assert again.embedding_stats == {"fromStore": len(CATALOG) - 1, "encoded": 1}
    assert np.allclose(again._embeddings, first._embeddings)


# ── Feedback + disputes (in-memory SQLite) ───────────────────────────────────

@pytest.fixture
def db():
    from models.models import Base
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(eng)
    session = sessionmaker(bind=eng)()
    yield session
    session.close()


def test_latest_vote_wins_and_clear_removes_it(db):
    from services import feedback_service as fs
    fs.record(db, "u", "c1", "thumbs_up")
    fs.record(db, "u", "c1", "thumbs_down")
    fs.record(db, "u", "c2", "thumbs_down")
    fs.record(db, "u", "c2", "clear_vote")
    fs.record(db, "u", "c3", "click", rank=1)
    assert fs.user_votes(db, "u") == {"c1": "down"}
    summary = fs.summary(db)
    assert {c["courseId"] for c in summary["courses"]} == {"c1", "c2", "c3"}
    assert summary["byRank"] == [{"rank": 1, "click": 1}]


@pytest.mark.parametrize("mu, shown, status", [(4.3, 3, "RAISED"), (3.1, 3, "CONFIRMED"),
                                               (1.8, 3, "LOWER_THAN_SHOWN")])
def test_dispute_is_resolved_from_the_tested_level(db, mu, shown, status):
    from models.models import LevelDispute
    from routers import diagnostic
    from services.irt_service import SESSIONS
    SESSIONS._s["sid-test"] = {"mu": mu}
    db.add(LevelDispute(userId="u", competencyId="c", shownLevel=shown, claimedLevel=4, sessionId="sid-test"))
    db.commit()
    try:
        out = diagnostic._resolve_dispute("sid-test", db)
    finally:
        SESSIONS._s.pop("sid-test", None)
    assert out["status"] == status and out["testedLevel"] == int(mu)
    assert diagnostic._resolve_dispute("sid-test-none", db) is None
