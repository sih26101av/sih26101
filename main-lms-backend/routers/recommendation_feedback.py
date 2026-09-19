"""
routers/recommendation_feedback.py — log clicks, enrolments and thumbs on recommendations

    POST /api/v1/recommendations/feedback          {courseId, event, competencyId?, rank?, finalScore?, context?}
    GET  /api/v1/recommendations/feedback/mine     → {votes: {courseId: "up" | "down"}}
    GET  /api/v1/admin/recommendations/feedback    → per-course counts + click-through by rank (admin)

The learner is always the JWT subject (current_user.username), never a body field.
A thumbs-down removes the course from that learner's /recommendations (except
mandatory ACBP courses); a later thumbs-up or clear_vote brings it back.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth.database import get_db
from auth.dependencies import get_current_user, require_role
from auth.models import UserAuth
from services import feedback_service

router = APIRouter(tags=["recommendation-feedback"])


class FeedbackBody(BaseModel):
    courseId: str = Field(min_length=1, max_length=128)
    event: str
    competencyId: Optional[str] = None
    rank: Optional[int] = None
    finalScore: Optional[float] = None
    context: Optional[Dict[str, Any]] = None


@router.post("/api/v1/recommendations/feedback", status_code=201)
async def post_feedback(body: FeedbackBody, current_user: UserAuth = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    if body.event not in feedback_service.EVENTS:
        raise HTTPException(status_code=422, detail=f"event must be one of {sorted(feedback_service.EVENTS)}")
    row = feedback_service.record(db, current_user.username, body.courseId, body.event, body.competencyId,
                                  body.rank, body.finalScore, body.context)
    return {"status": "success", "id": row.id,
            "votes": feedback_service.user_votes(db, current_user.username)}


@router.get("/api/v1/recommendations/feedback/mine")
async def my_feedback(current_user: UserAuth = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"status": "success", "votes": feedback_service.user_votes(db, current_user.username)}


@router.get("/api/v1/admin/recommendations/feedback")
async def feedback_summary(_admin: UserAuth = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return {"status": "success", **feedback_service.summary(db)}
