"""
routers/karma.py
─────────────────────────────────────────────────────────────────────────────
Three FastAPI endpoints for the Karma Points system:

  GET  /api/v1/learner/{user_id}/karma
       Full ledger: total, streak, monthly cap usage, breakdown, last 10 events

  POST /api/v1/learner/{user_id}/karma/event
       Award points for a user action (COURSE_COMPLETION, ASSESSMENT_PASSED, etc.)

  POST /api/v1/learner/{user_id}/karma/claim-cbp-bonus
       Retroactive CBP +10 claim for a course now mandated in the user CBP plan
─────────────────────────────────────────────────────────────────────────────
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from adapters.igot_adapter import MockIgotAdapter
from auth.database import get_db
from auth.dependencies import get_current_user
from auth.models import UserAuth
from models.models import KarmaEventType
from services.karma_engine import karma_engine

router = APIRouter(tags=["karma"])

# Stateless adapter instance — safe to re-use; it only holds config, no state
_adapter = MockIgotAdapter()


# --- Request / Response schemas -----------------------------------------------

class KarmaEventRequest(BaseModel):
    eventType: str
    courseId: Optional[str] = None
    isCbp: bool = False
    is_mdo_onboarded: bool = False   # for SELF_REGISTRATION only


class CbpClaimRequest(BaseModel):
    courseId: str


# --- Helpers ------------------------------------------------------------------

def _serialize_ledger(events) -> list:
    return [
        {
            "eventId":       e.eventId,
            "eventType":     e.eventType.value,
            "pointsAwarded": e.pointsAwarded,
            "courseId":      e.courseId,
            "isCbp":         e.isCbp,
            "createdAt":     e.createdAt.isoformat() if e.createdAt else None,
        }
        for e in events
    ]


# --- Routes -------------------------------------------------------------------

@router.get("/learner/{user_id}/karma")
async def get_karma_ledger(
    user_id: str,
    _current_user: UserAuth = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns the full Karma Points summary for a learner.
    On the very first call (empty ledger), automatically seeds karma events
    from the user's real iGOT enrollment history so the card is never blank.
    """
    # ── Auto-seed on first visit ───────────────────────────────────────────────
    existing = karma_engine.get_ledger(user_id, db, limit=1)
    if not existing:
        try:
            raw_enrollments = await _adapter.fetch_user_enrollments(user_id)
            karma_engine.seed_from_enrollments(user_id, raw_enrollments, db)
        except Exception as exc:
            # Mock server may be offline — log and continue; return empty ledger
            print(f"[karma] seed skipped for {user_id}: {exc}")

    # ── Build response ─────────────────────────────────────────────────────────
    balance   = karma_engine.get_balance(user_id, db)
    ledger    = karma_engine.get_ledger(user_id, db, limit=10)
    monthly   = karma_engine.get_monthly_usage(user_id, db)
    streak    = karma_engine.get_streak(user_id, db)
    breakdown = karma_engine.get_breakdown(user_id, db)

    return {
        "userId":       user_id,
        "totalPoints":  balance,
        "streak":       streak,
        "monthlyUsage": monthly.to_dict(),
        "breakdown":    breakdown,
        "ledger":       _serialize_ledger(ledger),
    }


@router.post("/learner/{user_id}/karma/event", status_code=status.HTTP_200_OK)
async def award_karma_event(
    user_id: str,
    body: KarmaEventRequest,
    _current_user: UserAuth = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Award Karma Points for a specific user action.
    The KarmaEngine Strategy dispatches to the right concrete strategy,
    enforces all iGOT rules (one-time guards, monthly cap, idempotency),
    and appends an immutable ledger entry.
    """
    try:
        event_type = KarmaEventType(body.eventType)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown eventType '{body.eventType}'. "
                   f"Valid values: {[e.value for e in KarmaEventType]}",
        )

    metadata = {
        "courseId":        body.courseId,
        "isCbp":           body.isCbp,
        "is_mdo_onboarded": body.is_mdo_onboarded,
    }
    result = karma_engine.award(user_id, event_type, metadata, db)

    return {
        "userId":        user_id,
        "pointsAwarded": result.points_awarded,
        "capReached":    result.cap_reached,
        "alreadyClaimed": result.already_claimed,
        "newBalance":    karma_engine.get_balance(user_id, db),
        "monthlyUsage":  karma_engine.get_monthly_usage(user_id, db).to_dict(),
    }


@router.post("/learner/{user_id}/karma/claim-cbp-bonus", status_code=status.HTTP_200_OK)
async def claim_cbp_bonus(
    user_id: str,
    body: CbpClaimRequest,
    _current_user: UserAuth = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retroactive CBP +10 claim.
    Idempotent: if the user already claimed the bonus for this courseId, returns
    alreadyClaimed=True and pointsAwarded=0 (no double-dipping).
    """
    result = karma_engine.award(
        user_id,
        KarmaEventType.CBP_BONUS,
        {"courseId": body.courseId, "isCbp": True},
        db,
    )

    return {
        "userId":        user_id,
        "courseId":      body.courseId,
        "pointsAwarded": result.points_awarded,
        "alreadyClaimed": result.already_claimed,
        "newBalance":    karma_engine.get_balance(user_id, db),
    }
