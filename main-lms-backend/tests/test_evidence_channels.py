"""
SCIL v6 §3 evidence channels K/A/U/S (knowledge, application, utility,
supervisor) with equal PLACEHOLDER weights; peer ratings never scored.

    pytest tests/test_evidence_channels.py
"""
import pytest

from services.baseline_assembler import BaselineAssembler, resolve_level
from services.competency_service import CHANNEL_WEIGHTS, fuse_channels

USER = {
    "experienceYears": 8, "jobProfile": {"tier": "TIER3_MID"},
    "education": [{"degree": "MSc Statistics"}],
    "careerHistory": [{"title": "Survey Officer", "duration_years": 6}],
    "competencies": [{"id": "comp_x", "name": "Survey Design", "type": "Domain", "requiredLevel": 4}],
}
BARE = {**USER, "experienceYears": 0, "education": [], "careerHistory": []}
DONE_L2 = [{"courseId": "c2", "status": 2, "completionPercentage": 100}]
ASM = BaselineAssembler({"c2": {"comp_x": 2}, "c4": {"comp_x": 4}})


def _row(etype, value, meta=None, date="2026-05-10T09:00:00.000Z"):
    return {"comp_id": "comp_x", "evidence_type": etype, "granted_value": value,
            "issue_date": date, "meta": meta or {}}


def _assess(user=USER, enrollments=(), rows=()):
    return ASM.compute_for_user(user, list(enrollments), list(rows))["comp_x"]


def test_weights_are_an_equal_placeholder_and_absent_channels_renormalise():
    assert CHANNEL_WEIGHTS == {"K": 0.25, "A": 0.25, "U": 0.25, "S": 0.25}
    assert fuse_channels({"K": 2.0, "A": None, "U": None, "S": 4.0}) == pytest.approx(3.0)
    assert fuse_channels({"K": 1.0, "A": 3.0, "U": 2.0, "S": 2.0}) == pytest.approx(2.0)
    assert fuse_channels({"K": None, "A": None, "U": None, "S": None}) is None


def test_knowledge_only_score_is_unchanged():
    a = _assess(enrollments=DONE_L2)
    assert a["score"] == a["knowledgeScore"]
    assert a["completeness"]["present"] == ["K"] and a["completeness"]["missing"] == ["A", "U", "S"]


def test_lenient_supervisor_alone_cannot_lift_the_level_past_the_low_ceiling():
    a = _assess(user=BARE, rows=[_row("SUPERVISOR_RATING", 5)])
    assert a["confidence"] == "LOW" and a["score"] <= 2.5 and a["currentLevel"] == 2
    resolved = resolve_level(a, 0)
    assert resolved["basis"] == "evidence" and resolved["level"] == 2


def test_passed_work_sample_is_a_high_confidence_floor():
    a = _assess(rows=[_row("WORK_SAMPLE", 3, {"level": 3, "score": 82, "passed": True})])
    assert a["workSampleLevel"] == 3 and a["confidence"] == "HIGH"
    r = resolve_level(a, 0)
    assert r["level"] >= 3 and r["confidence"] == "HIGH"


def test_failed_work_sample_is_evidence_but_not_a_floor():
    a = _assess(rows=[_row("WORK_SAMPLE", 4, {"level": 4, "score": 40, "passed": False})])
    assert a["channels"]["A"] == 3.5 and a["workSampleLevel"] == 0


def test_confirmed_use_is_a_floor_unconfirmed_is_not():
    confirmed = _assess(user=BARE, rows=[_row("UTILITY", 3, {"confirmed": True, "willUse": True})])
    assert confirmed["appliedLevel"] == 3 and confirmed["confidence"] == "MEDIUM"
    r = resolve_level(confirmed, 0)
    assert (r["level"], r["confidence"]) == (3, "MEDIUM")
    pending = _assess(user=BARE, rows=[_row("UTILITY", 0, {"confirmed": None, "willUse": True})])
    assert pending["channels"]["U"] is None and pending["confidence"] == "UNASSESSED"


def test_peer_ratings_are_never_scored():
    base = _assess(enrollments=DONE_L2)
    with_peer = _assess(enrollments=DONE_L2, rows=[_row("PEER_RATING", 5), _row("PEER_RATING", 1)])
    assert with_peer["score"] == base["score"] and with_peer["peerFeedback"] == 2
    assert with_peer["channels"] == base["channels"]


def test_latest_supervisor_rating_counts():
    a = _assess(rows=[_row("SUPERVISOR_RATING", 2, date="2025-05-01T09:00:00.000Z"),
                      _row("SUPERVISOR_RATING", 4, date="2026-05-01T09:00:00.000Z")])
    assert a["channels"]["S"] == 4.0


def test_resolved_level_stays_monotone_when_more_learning_is_added():
    rows = [_row("SUPERVISOR_RATING", 1)]                      # a harsh rating stays on record
    before = resolve_level(_assess(enrollments=DONE_L2, rows=rows), 0)["level"]
    more = DONE_L2 + [{"courseId": "c4", "status": 2, "completionPercentage": 100}]
    after = resolve_level(_assess(enrollments=more, rows=rows), 0)["level"]
    assert after >= before and after >= 4
