"""
routers/diagnostic.py — adaptive "check your level" diagnostic (SCIL v6 §2, Tier 1)

    POST /api/v1/diagnostic/start              {competencyId}
    POST /api/v1/diagnostic/{sessionId}/answer {itemId, optionIndex}
    GET  /api/v1/diagnostic/{sessionId}/result

The official is always the logged-in user (JWT subject) — never a body field.
On completion the posterior mean is written ONCE as an EvidenceLog
PRACTICE_ASSESSMENT row (the same evidence path the RAG quiz uses), so it flows
into the documented channel of the baseline. Every response is labelled
"calibrated on synthetic data — demo only".
"""
from __future__ import annotations

from datetime import datetime, timezone

import math

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.database import get_db

from auth.dependencies import get_current_user
from auth.models import UserAuth
from services import app_state
from services.irt_service import CALIBRATION_LABEL, SESSIONS
from services.proficiency_service import POP_MU_DEFAULT, POP_SIGMA_DEFAULT

router = APIRouter(prefix="/api/v1/diagnostic", tags=["diagnostic"])


class StartBody(BaseModel):
    competencyId: str


class AnswerBody(BaseModel):
    itemId: str
    optionIndex: int


@router.post("/start")
async def start(body: StartBody, current_user: UserAuth = Depends(get_current_user)):
    return await start_session(current_user.username, body.competencyId)


async def start_session(user_id: str, competency_id: str) -> dict:
    """Start an adaptive session for one role competency (also used by level disputes)."""
    ref = app_state.ref
    if app_state.competency_state is None:
        raise HTTPException(status_code=503, detail="Backend not ready.")
    state = await app_state.competency_state(user_id)
    row = next((r for r in state["competencies"]
                if competency_id in (r["competencyId"], r.get("catalogueId"))), None)
    if row is None:
        raise HTTPException(status_code=404, detail="Competency is not part of your role profile.")
    comp_id = row.get("catalogueId") or row["competencyId"]
    items = ref.item_bank.get(comp_id)
    if not items:
        raise HTTPException(status_code=404, detail="No diagnostic items for this competency.")

    prof, cold = row.get("proficiency"), row.get("coldStartPrior")
    if prof:
        prior = {"mu": prof["decayedMu"], "sigma": max(prof["decayedSigma"], 0.6),
                 "source": "your evidence (decayed)"}
    elif cold:
        prior = {"mu": cold["mu"], "sigma": cold["sigma"], "source": cold["label"]}
    else:
        prior = {"mu": POP_MU_DEFAULT, "sigma": POP_SIGMA_DEFAULT, "source": "population default"}
    comp = {"competencyId": row["competencyId"], "catalogueId": comp_id,
            "competencyName": row["name"], "targetLevel": row["targetLevel"]}
    return SESSIONS.start(user_id, comp, items, prior)


def _session(session_id: str, user: UserAuth):
    s = SESSIONS.get(session_id, user.username)
    if s is None:
        raise HTTPException(status_code=404, detail="Diagnostic session not found or expired.")
    return s


@router.post("/{session_id}/answer")
async def answer(session_id: str, body: AnswerBody, current_user: UserAuth = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    _session(session_id, current_user)
    try:
        view = SESSIONS.answer(session_id, body.itemId, body.optionIndex)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    if view["done"]:
        _write_evidence(session_id, db)
        dispute = _resolve_dispute(session_id, db)
        if dispute:
            view["dispute"] = dispute
    return view


@router.get("/{session_id}/result")
async def result(session_id: str, current_user: UserAuth = Depends(get_current_user)):
    s = _session(session_id, current_user)
    if not s["done"]:
        raise HTTPException(status_code=409, detail="The diagnostic is not finished yet.")
    return SESSIONS.result(session_id)


def _write_evidence(session_id: str, db: Session) -> None:
    """Posterior mean → one PRACTICE_ASSESSMENT EvidenceLog row (the existing evidence path)."""
    from models.models import Competency, EvidenceLog

    s = SESSIONS._s[session_id]
    if s["evidenceWritten"]:
        return
    comp = s["competency"]
    # `db` is the request's session (Depends(get_db)); FastAPI closes it.
    if not db.query(Competency).filter(Competency.compId == comp["catalogueId"]).first():
        db.add(Competency(compId=comp["catalogueId"], domain="Statistical", skillName=comp["competencyName"]))
        db.flush()
    db.add(EvidenceLog(
        userId=s["userId"], compId=comp["catalogueId"], evidenceType="PRACTICE_ASSESSMENT",
        grantedValue=round(min(5.0, max(0.0, s["mu"])), 2), issueDate=datetime.now(timezone.utc),
        metadata_payload={"source": "adaptive_diagnostic_2pl", "sigma": round(s["sigma"], 3),
                          "items": len(s["responses"]), "calibration": CALIBRATION_LABEL},
    ))
    db.commit()
    s["evidenceWritten"] = True
    app_state.invalidate_user(s["userId"])      # dashboard shows the new level at once
    from models.models import KarmaEventType
    from services.karma_engine import karma_engine
    karma_engine.award_safe(s["userId"], KarmaEventType.DIAGNOSTIC_COMPLETED, {
        "referenceId": session_id, "note": comp["competencyName"],
    })


def _resolve_dispute(session_id: str, db: Session) -> dict | None:
    """
    Close the level dispute that started this session (if any): the tested level
    is floor(posterior mean). It is compared with the level shown when the
    learner disagreed. The PRACTICE_ASSESSMENT row written above is what moves
    the level; evidence floors (completed courses, work samples) still hold, so
    a lower tested level is recorded but cannot push the level below them.
    """
    from models.models import LevelDispute

    dispute = db.query(LevelDispute).filter(LevelDispute.sessionId == session_id,
                                            LevelDispute.status == "OPEN").first()
    if dispute is None:
        return None
    s = SESSIONS._s[session_id]
    tested = max(0, min(5, int(math.floor(s["mu"]))))
    shown = dispute.shownLevel
    if shown is None or tested > shown:
        dispute.status = "RAISED"
    elif tested == shown:
        dispute.status = "CONFIRMED"
    else:
        dispute.status = "LOWER_THAN_SHOWN"
    dispute.testedLevel = tested
    dispute.resolvedAt = datetime.now(timezone.utc)
    db.commit()
    app_state.invalidate_user(dispute.userId)
    return {"disputeId": dispute.id, "status": dispute.status, "shownLevel": shown,
            "claimedLevel": dispute.claimedLevel, "testedLevel": tested}
