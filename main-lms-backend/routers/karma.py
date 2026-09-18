"""
routers/karma.py
─────────────────────────────────────────────────────────────────────────────
Karma Points endpoints (mounted at /api/v1):

  GET  /karma/rules
       Earning rules, daily cap, streak milestones and levels (drives the
       "How to earn" section — the UI never hardcodes point values).

  POST /learner/{user_id}/karma/check-in
       Called once per dashboard load: seeds / syncs from iGOT, awards the
       daily check-in and streak milestones, returns the full summary plus
       the awards just made. Idempotent within an IST day.

  GET  /learner/{user_id}/karma?limit=&offset=
       Full summary (balance, level, today vs daily cap, streaks, rank,
       monthly cap, breakdown, passbook page). Read-only apart from the
       first-visit seed.

  POST /learner/{user_id}/karma/event
       Learner-triggered events only (registration, first enrolment, course
       completion, course rating) — verified against iGOT. Quiz / diagnostic
       points are awarded server-side by the grading code, never by the client.

  POST /learner/{user_id}/karma/claim-cbp-bonus
       Retroactive CBP +10 for a course the learner has completed.

  POST /admin/karma/{user_id}/adjust
       Admin-only signed grant / deduction with a mandatory reason.
─────────────────────────────────────────────────────────────────────────────
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from adapters.igot_adapter import MockIgotAdapter
from auth.database import get_db
from auth.dependencies import get_current_user
from auth.models import UserAuth
from models.models import KarmaEvent, KarmaEventType
from services.karma_engine import RULES, AwardResult, karma_engine, rules_payload

log = logging.getLogger(__name__)
router = APIRouter(tags=["karma"])

# Stateless adapter instance — safe to re-use; it only holds config, no state
_adapter = MockIgotAdapter()

# Events that need proof from iGOT before a learner may self-report them
_VERIFIED_EVENTS = {
    KarmaEventType.FIRST_ENROLLMENT,
    KarmaEventType.COURSE_COMPLETION,
    KarmaEventType.COURSE_RATED,
}


# --- Request schemas ----------------------------------------------------------

class KarmaEventRequest(BaseModel):
    eventType: str
    courseId: Optional[str] = None
    isCbp: bool = False
    is_mdo_onboarded: bool = False   # for SELF_REGISTRATION only


class CbpClaimRequest(BaseModel):
    courseId: str


class AdminAdjustRequest(BaseModel):
    points: int = Field(..., ge=-1000, le=1000)
    reason: str = Field(..., min_length=3, max_length=200)


# --- Helpers ------------------------------------------------------------------

def _serialize_ledger(events: List[KarmaEvent]) -> list:
    return [
        {
            "eventId":       e.eventId,
            "eventType":     e.eventType.value,
            "pointsAwarded": e.pointsAwarded,
            "courseId":      e.courseId,
            "isCbp":         e.isCbp,
            "referenceId":   e.referenceId,
            "note":          e.note,
            "createdAt":     (e.createdAt.isoformat() + "Z") if e.createdAt else None,
        }
        for e in events
    ]


def _summary(user_id: str, db: Session, limit: int = 20, offset: int = 0,
             recent: Optional[List[AwardResult]] = None) -> dict:
    balance = karma_engine.get_balance(user_id, db)
    streak = karma_engine.get_streak_stats(user_id, db)
    return {
        "userId":        user_id,
        "totalPoints":   balance,
        "level":         karma_engine.get_level(balance),
        "today":         karma_engine.get_today(user_id, db),
        "streak":        streak["current"],
        "longestStreak": streak["longest"],
        "rank":          karma_engine.get_rank(user_id, db),
        "monthlyUsage":  karma_engine.get_monthly_usage(user_id, db).to_dict(),
        "breakdown":     karma_engine.get_breakdown(user_id, db),
        "totalEvents":   karma_engine.count_events(user_id, db),
        "ledger":        _serialize_ledger(karma_engine.get_ledger(user_id, db, limit, offset)),
        "recentAwards":  [a.to_dict() for a in (recent or [])],
    }


def _award_response(user_id: str, result: AwardResult, db: Session) -> dict:
    return {
        "userId":       user_id,
        **result.to_dict(),
        "newBalance":   karma_engine.get_balance(user_id, db),
        "monthlyUsage": karma_engine.get_monthly_usage(user_id, db).to_dict(),
        "today":        karma_engine.get_today(user_id, db),
    }


async def _enrollments_or_503(user_id: str) -> list:
    try:
        return await _adapter.fetch_user_enrollments(user_id) or []
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"iGOT is unreachable, cannot verify: {exc}")


# --- Identity guard -----------------------------------------------------------

def _assert_self_or_admin(user_id: str, current_user: UserAuth) -> None:
    """Learners can only read/write their own karma; admins can access anyone's."""
    if current_user.role != "admin" and current_user.username != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own karma data.",
        )


# --- Routes -------------------------------------------------------------------

@router.get("/karma/rules")
async def get_karma_rules(current_user: UserAuth = Depends(get_current_user)):
    return rules_payload()


@router.post("/learner/{user_id}/karma/check-in")
async def karma_check_in(
    user_id: str,
    limit: int = Query(20, ge=1, le=200),
    current_user: UserAuth = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _assert_self_or_admin(user_id, current_user)
    awards: List[AwardResult] = []
    try:
        raw_enrollments = await _adapter.fetch_user_enrollments(user_id) or []
        awards += await run_in_threadpool(karma_engine.sync_from_igot, user_id, raw_enrollments, db)
    except Exception as exc:
        db.rollback()
        log.warning("[karma] iGOT sync skipped for %s: %s", user_id, exc)
    # Only the learner's own visit counts as a check-in, not an admin viewing it
    if current_user.username == user_id:
        awards += await run_in_threadpool(karma_engine.check_in, user_id, db)
    # Sync DB work (Neon round-trips) stays off the event loop
    return await run_in_threadpool(_summary, user_id, db, limit, 0, awards)


@router.get("/learner/{user_id}/karma")
async def get_karma_ledger(
    user_id: str,
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: UserAuth = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _assert_self_or_admin(user_id, current_user)

    # Auto-seed on first visit so the card is never blank
    if not await run_in_threadpool(karma_engine.get_ledger, user_id, db, 1):
        try:
            raw_enrollments = await _adapter.fetch_user_enrollments(user_id) or []
            await run_in_threadpool(karma_engine.seed_from_enrollments, user_id, raw_enrollments, db)
        except Exception as exc:
            db.rollback()
            log.warning("[karma] seed skipped for %s: %s", user_id, exc)

    return await run_in_threadpool(_summary, user_id, db, limit, offset)


@router.post("/learner/{user_id}/karma/event", status_code=status.HTTP_200_OK)
async def award_karma_event(
    user_id: str,
    body: KarmaEventRequest,
    current_user: UserAuth = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _assert_self_or_admin(user_id, current_user)

    try:
        event_type = KarmaEventType(body.eventType)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown eventType '{body.eventType}'. "
                   f"Valid values: {[t.value for t, r in RULES.items() if r.client_awardable]}",
        )
    if not RULES[event_type].client_awardable:
        raise HTTPException(
            status_code=403,
            detail=f"{event_type.value} is awarded automatically by the platform and cannot be claimed.",
        )

    is_cbp = body.isCbp
    if event_type in _VERIFIED_EVENTS:
        enrollments = await _enrollments_or_503(user_id)
        if event_type == KarmaEventType.FIRST_ENROLLMENT:
            if not enrollments:
                raise HTTPException(status_code=409, detail="No iGOT enrolment found yet.")
        else:
            if not body.courseId:
                raise HTTPException(status_code=400, detail="courseId is required.")
            match = next((e for e in enrollments if e.get("courseId") == body.courseId), None)
            if match is None:
                raise HTTPException(status_code=409, detail="You are not enrolled in this course on iGOT.")
            if event_type == KarmaEventType.COURSE_COMPLETION and match.get("status") != 2:
                raise HTTPException(status_code=409, detail="iGOT does not show this course as completed yet.")
            is_cbp = bool(match.get("isCbp", body.isCbp))

    metadata = {
        "courseId":         body.courseId,
        "isCbp":            is_cbp,
        "is_mdo_onboarded": body.is_mdo_onboarded,
    }
    result = karma_engine.award(user_id, event_type, metadata, db)
    return _award_response(user_id, result, db)


@router.post("/learner/{user_id}/karma/claim-cbp-bonus", status_code=status.HTTP_200_OK)
async def claim_cbp_bonus(
    user_id: str,
    body: CbpClaimRequest,
    current_user: UserAuth = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retroactive CBP +10. Requires a recorded completion of the course; idempotent."""
    _assert_self_or_admin(user_id, current_user)

    completed = db.query(KarmaEvent.eventId).filter(
        KarmaEvent.userId == user_id,
        KarmaEvent.eventType == KarmaEventType.COURSE_COMPLETION,
        KarmaEvent.courseId == body.courseId,
    ).first()
    if not completed:
        raise HTTPException(status_code=409, detail="Complete this course before claiming its CBP bonus.")

    result = karma_engine.award(
        user_id, KarmaEventType.CBP_BONUS,
        {"courseId": body.courseId, "isCbp": True, "note": "CBP bonus claimed"}, db,
    )
    return {"courseId": body.courseId, **_award_response(user_id, result, db)}


@router.post("/admin/karma/{user_id}/adjust", status_code=status.HTTP_200_OK)
async def admin_adjust_karma(
    user_id: str,
    body: AdminAdjustRequest,
    current_user: UserAuth = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only.")
    if body.points == 0:
        raise HTTPException(status_code=400, detail="points must be non-zero.")
    result = karma_engine.award(
        user_id, KarmaEventType.ADMIN_ADJUSTMENT,
        {"points": body.points, "note": f"{body.reason} (by {current_user.username})"}, db,
    )
    return _award_response(user_id, result, db)
