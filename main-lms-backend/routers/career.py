"""
routers/career.py — career readiness + "I disagree with this level"

    GET  /api/v1/learner/{user_id}/career-readiness[?targetRoleId=]
        Gaps against the NEXT role's FRAC requirements (roles.json via the adapter):
        the next role is a role in the same office one tier up (TIER4 → TIER3 → …).
        Levels come from the same resolver as /skill-gaps; competencies the
        official's current profile does not carry are scored on the same
        evidence through the assembler (no self-report → often UNASSESSED).

    POST /api/v1/level-disputes          {competencyId, claimedLevel?, reason?}
        Records the disagreement and starts the adaptive level test
        (routers/diagnostic.py). When the test finishes, the dispute is closed
        as CONFIRMED / RAISED / LOWER_THAN_SHOWN (diagnostic._resolve_dispute).
    GET  /api/v1/level-disputes          → the learner's disputes, newest first
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth.database import get_db
from auth.dependencies import get_current_user
from auth.models import UserAuth
from services import app_state

router = APIRouter(tags=["career"])

# Lower number = more senior. Both naming schemes seen in the data are mapped.
TIER_RANK = {"TIER1_APEX": 1, "TIER1_SENIOR": 1, "TIER2_SENIOR": 2, "TIER2_UPPER": 2,
             "TIER3_MID": 3, "TIER4_JUNIOR": 4, "TIER5_ENTRY": 5}


def _ensure_can_view(user_id: str, current_user: UserAuth) -> None:
    if current_user.username != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only view your own learning data.")


def _tier(role: Dict[str, Any]) -> int:
    return TIER_RANK.get((role.get("tier") or "").upper(), 99)


def office_ladder(roles: Dict[str, Dict[str, Any]], office_id: str) -> List[List[Dict[str, Any]]]:
    """Roles of one office grouped by tier, most junior tier first."""
    by_tier: Dict[int, List[Dict[str, Any]]] = {}
    for r in roles.values():
        if r.get("officeId") == office_id:
            by_tier.setdefault(_tier(r), []).append(r)
    return [sorted(by_tier[t], key=lambda r: r.get("designation", "")) for t in sorted(by_tier, reverse=True)]


def readiness_for(requirements: List[Dict[str, Any]], levels: Dict[str, Dict[str, Any]],
                  names: Dict[str, str]) -> Dict[str, Any]:
    """
    readiness = mean over required competencies of min(level, required) / required.
    UNASSESSED counts as 0 there (no evidence is not readiness) and is listed so
    the learner can take the level check instead of a course.
    """
    rows, total = [], 0.0
    for req in requirements:
        cid, need = req["id"], int(req.get("requiredLevel") or 3)
        lv = levels.get(cid) or {}
        cur = lv.get("level")
        total += min(cur or 0, need) / need if need else 1.0
        rows.append({
            "competencyId": cid, "competencyName": names.get(cid, cid),
            "requiredLevel": need, "currentLevel": cur,
            "gap": (max(0, need - cur) if cur is not None else None),
            "confidence": lv.get("confidence", "UNASSESSED"), "basis": lv.get("basis", "none"),
            "inCurrentRole": lv.get("inCurrentRole", False),
        })
    rows.sort(key=lambda r: (r["gap"] is None, -(r["gap"] or 0), r["competencyName"]))
    n = len(requirements) or 1
    return {
        "readinessPct": round(100.0 * total / n),
        "metCount": sum(1 for r in rows if r["gap"] == 0),
        "gapCount": sum(1 for r in rows if (r["gap"] or 0) > 0),
        "unassessedCount": sum(1 for r in rows if r["gap"] is None),
        "competencies": rows,
    }


@router.get("/api/v1/learner/{user_id}/career-readiness")
async def career_readiness(user_id: str, targetRoleId: Optional[str] = None,
                           current_user: UserAuth = Depends(get_current_user)):
    from services.baseline_assembler import resolve_level

    _ensure_can_view(user_id, current_user)
    if app_state.competency_state is None:
        raise HTTPException(status_code=503, detail="Backend not ready.")
    roles = app_state.ref.roles
    if not roles:
        raise HTTPException(status_code=503, detail="Role profiles (roles.json) are not loaded.")

    state = await app_state.competency_state(user_id)
    user = state["user"]
    jp = user.get("jobProfile") or {}
    current_role = roles.get(jp.get("roleId") or "") or {
        "roleId": jp.get("roleId"), "officeId": jp.get("officeId"),
        "designation": jp.get("title") or "Current role", "tier": jp.get("tier"), "competencies": [],
    }
    ladder = office_ladder(roles, current_role.get("officeId") or "")
    cur_rank = _tier(current_role)
    higher = [tier for tier in ladder if _tier(tier[0]) < cur_rank]      # ascending seniority
    candidates = higher[0] if higher else []
    if targetRoleId:
        if targetRoleId not in roles:
            raise HTTPException(status_code=404, detail=f"Role '{targetRoleId}' not found.")
        candidates = [roles[targetRoleId]]

    # Levels the official already has resolved (role competencies, both id spaces).
    levels: Dict[str, Dict[str, Any]] = {}
    for r in state["competencies"]:
        entry = {"level": r["currentLevel"], "confidence": r["confidence"], "basis": r["basis"],
                 "inCurrentRole": True}
        levels[r["competencyId"]] = entry
        if r.get("catalogueId"):
            levels.setdefault(r["catalogueId"], entry)

    engine = app_state.engine
    frac = engine._frac_map if engine is not None else {}
    names = {cid: m.get("name", cid) for cid, m in frac.items()}
    names.update({r["competencyId"]: r["name"] for r in state["competencies"]})

    # Competencies the next role(s) need that are not in the current profile:
    # score them on the same evidence (enrollments + evidence rows), no self-report.
    needed = {c["id"] for role in candidates for c in role.get("competencies", [])} - set(levels)
    if needed and app_state.assembler is not None:
        extra = [{"id": cid, "name": names.get(cid, cid), "type": frac.get(cid, {}).get("type", "Domain"),
                  "requiredLevel": 3} for cid in sorted(needed)]
        scored = app_state.assembler.compute_for_user(
            user={**user, "competencies": extra, "profileDetails": {}},
            enrollments=state["enrollments"], db_evidence=state.get("evidenceRows") or [])
        for cid in needed:
            res = resolve_level(scored.get(cid, {}), 0)
            levels[cid] = {"level": res["level"], "confidence": res["confidence"], "basis": res["basis"],
                           "inCurrentRole": False}

    options = []
    for role in candidates:
        rd = readiness_for(role.get("competencies", []), levels, names)
        options.append({"roleId": role["roleId"], "designation": role.get("designation"),
                        "tier": role.get("tier"), **rd})
    options.sort(key=lambda o: -o["readinessPct"])
    current_rd = readiness_for(current_role.get("competencies", []), levels, names)

    milestones = [{"roleId": current_role.get("roleId"), "designation": current_role.get("designation"),
                   "tier": current_role.get("tier"), "status": "current"}]
    if options:
        milestones.append({"roleId": options[0]["roleId"], "designation": options[0]["designation"],
                           "tier": options[0]["tier"], "status": "next"})
    if len(higher) > 1 and not targetRoleId:
        after = higher[1][0]
        milestones.append({"roleId": after["roleId"], "designation": after.get("designation"),
                           "tier": after.get("tier"), "status": "future"})

    return {
        "status": "success",
        "officialId": user_id,
        "currentRole": {"roleId": current_role.get("roleId"), "designation": current_role.get("designation"),
                        "tier": current_role.get("tier"), "officeId": current_role.get("officeId"),
                        "readinessPct": current_rd["readinessPct"]},
        "nextRole": options[0] if options else None,
        "alternatives": options[1:],
        "atTopOfLadder": not options,
        "milestones": milestones,
        "method": ("readiness = mean over the next role's FRAC competencies of min(current level, required) "
                   "/ required; unassessed competencies count as 0. Next role = same office, one tier up."),
    }


# ── Level disputes ───────────────────────────────────────────────────────────

class DisputeBody(BaseModel):
    competencyId: str
    claimedLevel: Optional[int] = Field(default=None, ge=0, le=5)
    reason: Optional[str] = Field(default=None, max_length=500)


def _dispute_view(d) -> Dict[str, Any]:
    return {"disputeId": d.id, "competencyId": d.competencyId, "shownLevel": d.shownLevel,
            "claimedLevel": d.claimedLevel, "reason": d.reason, "status": d.status,
            "testedLevel": d.testedLevel, "sessionId": d.sessionId,
            "createdAt": d.createdAt.isoformat() if d.createdAt else None,
            "resolvedAt": d.resolvedAt.isoformat() if d.resolvedAt else None}


@router.post("/api/v1/level-disputes", status_code=201)
async def open_dispute(body: DisputeBody, current_user: UserAuth = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    from models.models import LevelDispute
    from routers.diagnostic import start_session

    if app_state.competency_state is None:
        raise HTTPException(status_code=503, detail="Backend not ready.")
    user_id = current_user.username
    state = await app_state.competency_state(user_id)
    row = next((r for r in state["competencies"]
                if body.competencyId in (r["competencyId"], r.get("catalogueId"))), None)
    if row is None:
        raise HTTPException(status_code=404, detail="Competency is not part of your role profile.")

    dispute = LevelDispute(userId=user_id, competencyId=row["competencyId"], shownLevel=row["currentLevel"],
                           claimedLevel=body.claimedLevel, reason=body.reason, status="OPEN")
    session = None
    try:
        session = await start_session(user_id, row["competencyId"])
        dispute.sessionId = session["sessionId"]
    except HTTPException as exc:
        if exc.status_code != 404:
            raise
        dispute.status = "NEEDS_REVIEW"          # no item bank for this competency → human review
    db.add(dispute)
    db.commit()
    return {"status": "success", "dispute": _dispute_view(dispute), "session": session}


@router.get("/api/v1/level-disputes")
async def my_disputes(current_user: UserAuth = Depends(get_current_user), db: Session = Depends(get_db)):
    from models.models import LevelDispute
    rows = (db.query(LevelDispute).filter(LevelDispute.userId == current_user.username)
            .order_by(LevelDispute.createdAt.desc()).limit(50).all())
    return {"status": "success", "disputes": [_dispute_view(d) for d in rows]}
