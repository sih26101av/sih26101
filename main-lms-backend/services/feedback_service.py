"""
services/feedback_service.py — recommendation feedback (clicks, enrolments, thumbs)

Every interaction is one RecommendationFeedback row; nothing is updated in
place, so the log can later drive offline evaluation (click-through by rank)
or bandit-style learning. Two things read it back today:
  • user_votes    — the learner's current thumbs per course (latest vote wins,
                    `clear_vote` removes it) for the UI toggle state;
  • downvoted_ids — courses the learner thumbed down, which /recommendations
                    stops suggesting to them (mandatory ACBP courses still show).
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Set

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.models import RecommendationFeedback

EVENTS = {"impression", "click", "enrol", "thumbs_up", "thumbs_down", "clear_vote"}
_VOTES = {"thumbs_up": "up", "thumbs_down": "down", "clear_vote": None}


def record(db: Session, user_id: str, course_id: str, event: str, competency_id: Optional[str] = None,
           rank: Optional[int] = None, final_score: Optional[float] = None,
           context: Optional[Dict[str, Any]] = None) -> RecommendationFeedback:
    row = RecommendationFeedback(userId=user_id, courseId=course_id, competencyId=competency_id,
                                 event=event, rank=rank, finalScore=final_score, context=context or {})
    db.add(row)
    db.commit()
    return row


def user_votes(db: Session, user_id: str) -> Dict[str, str]:
    """{courseId: "up" | "down"} — the latest vote event per course."""
    votes: Dict[str, Optional[str]] = {}
    rows = (db.query(RecommendationFeedback)
            .filter(RecommendationFeedback.userId == user_id,
                    RecommendationFeedback.event.in_(list(_VOTES)))
            .order_by(RecommendationFeedback.createdAt.asc()).all())
    for r in rows:
        votes[r.courseId] = _VOTES[r.event]
    return {cid: v for cid, v in votes.items() if v}


def downvoted_ids(user_id: str) -> Set[str]:
    """Courses currently thumbed down by this learner (sync; own session). Empty on DB error."""
    from auth.database import session_scope
    try:
        with session_scope() as db:
            return {cid for cid, v in user_votes(db, user_id).items() if v == "down"}
    except Exception:
        return set()


def summary(db: Session) -> Dict[str, Any]:
    """Per-course counts of each event + click-through by rank (admin view)."""
    per_course: Dict[str, Dict[str, int]] = {}
    for course_id, event, n in (db.query(RecommendationFeedback.courseId, RecommendationFeedback.event,
                                         func.count()).group_by(RecommendationFeedback.courseId,
                                                                RecommendationFeedback.event).all()):
        per_course.setdefault(course_id, {})[event] = n
    by_rank: Dict[int, Dict[str, int]] = {}
    for rank, event, n in (db.query(RecommendationFeedback.rank, RecommendationFeedback.event, func.count())
                           .filter(RecommendationFeedback.rank.isnot(None))
                           .group_by(RecommendationFeedback.rank, RecommendationFeedback.event).all()):
        by_rank.setdefault(int(rank), {})[event] = n
    courses = sorted(
        ({"courseId": cid, **counts,
          "net": counts.get("thumbs_up", 0) - counts.get("thumbs_down", 0)} for cid, counts in per_course.items()),
        key=lambda c: (-(c.get("click", 0) + c.get("enrol", 0)), c["courseId"]))
    # Real click-through per rank: the UI logs an impression for every card it
    # actually put in front of a learner, so clicks finally have a denominator.
    # `ctr` is null for a rank with no impressions recorded yet (older rows).
    by_rank_rows = []
    for r, c in sorted(by_rank.items()):
        shown = c.get("impression", 0)
        by_rank_rows.append({"rank": r, **c,
                             "ctr": round(c.get("click", 0) / shown, 4) if shown else None})
    return {"courses": courses, "byRank": by_rank_rows, "events": sorted(EVENTS)}
