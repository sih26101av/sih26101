"""
FILE: services/doc_quiz/calibration.py
─────────────────────────────────────────────────────────────────────────────
Item difficulty from response data, not the LLM's tag.

For each item (keyed by content, items.item_key) quiz_item_stats counts first-
submission responses: n, correct, Σθ (respondents' practice ability BEFORE the
quiz). A raw p-value confounds difficulty with who answered — strong learners
pick Hard quizzes — so the estimate is the ability-adjusted 1-PL (Rasch) one
used by practice_assessment:

    p̂  = (correct + 0.5) / (n + 1)                       (never 0 or 1)
    b̂  = mean θ − logit(p̂) / A                           A = DISCRIMINATION_A
    b  = (n·b̂ + m·b₀) / (n + m)                           b₀ = b of the LLM tag, m = PRIOR_WEIGHT

b is mapped back to Easy / Medium / Hard at the midpoints between the item
difficulties (2.0 and 3.0). Until an item has MIN_RESPONSES responses the
LLM's tag stands; after that the calibrated class is used for grading (θ
update and weighted score) and shown on the question.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import logging
import math
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

from services import practice_assessment as pa

logger = logging.getLogger(__name__)

MIN_RESPONSES = 5
PRIOR_WEIGHT = 6.0


def difficulty_from_b(b: float) -> str:
    bs = pa.ITEM_DIFFICULTY_B
    if b < (bs["Easy"] + bs["Medium"]) / 2:
        return "Easy"
    if b < (bs["Medium"] + bs["Hard"]) / 2:
        return "Medium"
    return "Hard"


def calibrate(llm_difficulty: Any, responses: int = 0, correct: int = 0, theta_sum: float = 0.0) -> Dict[str, Any]:
    """Effective difficulty of one item. Pure — unit-tested."""
    tag = pa.normalise_difficulty(llm_difficulty)
    out: Dict[str, Any] = {"llmDifficulty": tag, "responses": int(responses or 0)}
    n = int(responses or 0)
    if n <= 0:
        out.update({"difficulty": tag, "source": "llm_tag"})
        return out
    p_raw = correct / n
    p = (correct + 0.5) / (n + 1)
    mean_theta = theta_sum / n if theta_sum else pa.DEFAULT_PRIOR
    b_hat = mean_theta - math.log(p / (1 - p)) / pa.DISCRIMINATION_A
    b0 = pa.ITEM_DIFFICULTY_B[tag]
    b = (n * b_hat + PRIOR_WEIGHT * b0) / (n + PRIOR_WEIGHT)
    calibrated = difficulty_from_b(b)
    use = n >= MIN_RESPONSES
    out.update({
        "difficulty": calibrated if use else tag,
        "source": "response_data" if use else "llm_tag",
        "pValue": round(p_raw, 3),
        "meanAbility": round(mean_theta, 3),
        "b": round(b, 3),
        "calibratedDifficulty": calibrated,
        "agreesWithLlm": calibrated == tag,
    })
    return out


# ── DB access (sync; call from a worker thread) ───────────────────────────────

def load_stats(keys: Iterable[str]) -> Dict[str, Dict[str, Any]]:
    keys = [k for k in dict.fromkeys(keys) if k]
    if not keys:
        return {}
    from auth.database import SessionLocal
    from models.models import QuizItemStat

    db = SessionLocal()
    try:
        rows = db.query(QuizItemStat).filter(QuizItemStat.itemKey.in_(keys)).all()
        return {r.itemKey: {"responses": r.responses or 0, "correct": r.correctCount or 0,
                            "theta_sum": r.thetaSum or 0.0} for r in rows}
    except Exception as exc:          # table missing on an old DB, DB down: fall back to the LLM tag
        logger.warning("[calibration] stats unavailable: %s", exc)
        return {}
    finally:
        db.close()


def calibrate_items(items: List[Tuple[str, Any]]) -> List[Dict[str, Any]]:
    """[(item_key, llm_difficulty)] → calibration dict per item, in order."""
    stats = load_stats(k for k, _ in items)
    return [calibrate(tag, stats.get(k, {}).get("responses", 0), stats.get(k, {}).get("correct", 0),
                      stats.get(k, {}).get("theta_sum", 0.0)) for k, tag in items]


def record_responses(responses: List[Dict[str, Any]], theta: float) -> int:
    """responses: [{key, correct, llm_difficulty, type, question}] from ONE first submission.
    theta = the learner's practice ability before the quiz. Returns rows written."""
    responses = [r for r in responses if r.get("key")]
    if not responses:
        return 0
    from sqlalchemy.exc import IntegrityError
    from auth.database import SessionLocal
    from models.models import QuizItemStat

    for attempt in range(2):          # a concurrent first insert of the same item → retry as update
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            existing = {r.itemKey: r for r in db.query(QuizItemStat).filter(
                QuizItemStat.itemKey.in_([x["key"] for x in responses])).all()}
            for x in responses:
                row = existing.get(x["key"])
                if row is None:
                    row = QuizItemStat(itemKey=x["key"], questionType=x.get("type"),
                                       llmDifficulty=pa.normalise_difficulty(x.get("llm_difficulty")),
                                       responses=0, correctCount=0, thetaSum=0.0,
                                       sampleQuestion=str(x.get("question") or "")[:500], firstSeen=now)
                    db.add(row)
                    existing[x["key"]] = row
                row.responses = (row.responses or 0) + 1
                row.correctCount = (row.correctCount or 0) + (1 if x.get("correct") else 0)
                row.thetaSum = (row.thetaSum or 0.0) + float(theta)
                row.lastSeen = now
            db.commit()
            return len(responses)
        except IntegrityError:
            db.rollback()
            if attempt:
                raise
        except Exception as exc:
            db.rollback()
            logger.warning("[calibration] could not record responses: %s", exc)
            return 0
        finally:
            db.close()
    return 0
