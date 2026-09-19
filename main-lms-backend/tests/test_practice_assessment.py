"""Quiz → skill-gap bridge: difficulty-aware ability update, weighted score, latest-practice read path."""
from datetime import datetime, timedelta

from services import practice_assessment as pa
from services.baseline_assembler import BaselineAssembler


def _one(theta, difficulty, correct):
    after, _ = pa.update_ability(theta, [{"difficulty": difficulty, "correct": correct}])
    return round(after - theta, 4)


def test_missing_easy_costs_more_than_missing_hard():
    assert _one(2.0, "Easy", False) < _one(2.0, "Hard", False) < 0


def test_solving_hard_gains_more_than_solving_easy():
    assert _one(2.0, "Hard", True) > _one(2.0, "Easy", True) > 0


def test_quiz_move_is_bounded():
    all_right = [{"difficulty": "Hard", "correct": True}] * 20
    after, trace = pa.update_ability(1.0, all_right)
    assert after - 1.0 <= pa.MAX_QUIZ_MOVE + 1e-9 and len(trace) == 20
    all_wrong = [{"difficulty": "Easy", "correct": False}] * 20
    after, _ = pa.update_ability(4.0, all_wrong)
    assert 4.0 - after <= pa.MAX_QUIZ_MOVE + 1e-9


def test_weighted_score_rewards_hard_questions():
    hard_right = [{"difficulty": "Hard", "correct": True}, {"difficulty": "Easy", "correct": False}]
    easy_right = [{"difficulty": "Hard", "correct": False}, {"difficulty": "Easy", "correct": True}]
    assert pa.weighted_score(hard_right) > 50 > pa.weighted_score(easy_right)


def test_normalise_difficulty():
    assert pa.normalise_difficulty("hard") == "Hard"
    assert pa.normalise_difficulty("Advanced") == "Hard"
    assert pa.normalise_difficulty(None) == "Medium"
    assert pa.media_question_difficulty("Hard", "synthesis") == "Hard"
    assert pa.media_question_difficulty("Easy", "synthesis") == "Medium"


def test_latest_practice_row_wins_not_max():
    now = datetime.utcnow()
    rows = [
        {"evidence_type": "PRACTICE_ASSESSMENT", "granted_value": 3.4, "issue_date": now - timedelta(days=2)},
        {"evidence_type": "PRACTICE_ASSESSMENT", "granted_value": 2.9, "issue_date": now},
    ]
    assert pa.latest_practice_value(rows)[0] == 2.9


def test_link_by_frac_tag():
    rows = [{"competencyId": "R1", "catalogueId": "FRAC-A", "name": "Sampling"},
            {"competencyId": "R2", "catalogueId": None, "name": "Leadership"}]
    row, method, _ = pa.link_competency(rows, {"competency_id": "FRAC-A"})
    assert row["competencyId"] == "R1" and method == "frac_tag"


def _profile():
    return {"experienceYears": 0, "competencies": [{"id": "C1", "name": "Sample Surveys", "type": "Domain",
                                                     "requiredLevel": 4}]}


def test_failed_quiz_lowers_skill_score_and_passed_quiz_raises_it():
    asm = BaselineAssembler({})
    now = datetime.utcnow()
    base = asm.compute_for_user(_profile(), [], [
        {"comp_id": "C1", "evidence_type": "PRACTICE_ASSESSMENT", "granted_value": 2.5, "issue_date": now - timedelta(days=1)},
    ], now=now)["C1"]["score"]
    worse = asm.compute_for_user(_profile(), [], [
        {"comp_id": "C1", "evidence_type": "PRACTICE_ASSESSMENT", "granted_value": 2.5, "issue_date": now - timedelta(days=1)},
        {"comp_id": "C1", "evidence_type": "PRACTICE_ASSESSMENT", "granted_value": 2.2, "issue_date": now},
    ], now=now)["C1"]["score"]
    better = asm.compute_for_user(_profile(), [], [
        {"comp_id": "C1", "evidence_type": "PRACTICE_ASSESSMENT", "granted_value": 2.5, "issue_date": now - timedelta(days=1)},
        {"comp_id": "C1", "evidence_type": "PRACTICE_ASSESSMENT", "granted_value": 2.9, "issue_date": now},
    ], now=now)["C1"]["score"]
    assert worse < base < better
