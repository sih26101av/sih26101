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

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

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
    ref = app_state.ref
    if app_state.competency_state is None:
        raise HTTPException(status_code=503, detail="Backend not ready.")
    state = await app_state.competency_state(current_user.username)
    row = next((r for r in state["competencies"]
                if body.competencyId in (r["competencyId"], r.get("catalogueId"))), None)
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
    return SESSIONS.start(current_user.username, comp, items, prior)


def _session(session_id: str, user: UserAuth):
    s = SESSIONS.get(session_id, user.username)
    if s is None:
        raise HTTPException(status_code=404, detail="Diagnostic session not found or expired.")
    return s


@router.post("/{session_id}/answer")
async def answer(session_id: str, body: AnswerBody, current_user: UserAuth = Depends(get_current_user)):
    _session(session_id, current_user)
    try:
        view = SESSIONS.answer(session_id, body.itemId, body.optionIndex)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    if view["done"]:
        _write_evidence(session_id)
    return view


@router.get("/{session_id}/result")
async def result(session_id: str, current_user: UserAuth = Depends(get_current_user)):
    s = _session(session_id, current_user)
    if not s["done"]:
        raise HTTPException(status_code=409, detail="The diagnostic is not finished yet.")
    return SESSIONS.result(session_id)


def _write_evidence(session_id: str) -> None:
    """Posterior mean → one PRACTICE_ASSESSMENT EvidenceLog row (the existing evidence path)."""
    from auth.database import get_db
    from models.models import Competency, EvidenceLog

    s = SESSIONS._s[session_id]
    if s["evidenceWritten"]:
        return
    comp = s["competency"]
    db = next(get_db())
    try:
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
    finally:
        db.close()
