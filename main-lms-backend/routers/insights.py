"""
routers/insights.py — admin-only SCIL v6 workforce insights

Every number here is computed by auditable code over SYNTHETIC mock data
(mock-igot-server/generate_mock_data.py). Responses say so in `dataNote`.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from auth.dependencies import require_role
from auth.models import UserAuth
from services import app_state, gsbpm_service, prerequisite_service

router = APIRouter(prefix="/api/v1/admin", tags=["admin-insights"])

SYNTHETIC_NOTE = "Computed on synthetic mock data — demo only."


@router.get("/gsbpm/scope")
async def gsbpm_scope(
    officeId: Optional[str] = None,
    _admin: UserAuth = Depends(require_role("admin")),
):
    """SCIL v6 §1 — the 80% officer-hours scoping report (whole NSO, or one office)."""
    ref = app_state.ref
    if not ref.gsbpm or not ref.offices:
        raise HTTPException(status_code=503, detail="GSBPM map / office workload not loaded.")
    if officeId and officeId not in ref.offices:
        raise HTTPException(status_code=404, detail=f"Office '{officeId}' not found.")
    engine = app_state.engine
    names = {cid: meta.get("name", cid) for cid, meta in (engine._frac_map.items() if engine else [])}
    report = gsbpm_service.scope_report(ref.gsbpm, ref.offices, names=names,
                                        office_id=officeId, cycle=ref.cycle)
    report["offices"] = [{"officeId": o["officeId"], "name": o["name"],
                          "totalOfficerHours": o["totalOfficerHours"]} for o in ref.offices.values()]
    report["dataNote"] = SYNTHETIC_NOTE
    return report


def _frac_names() -> dict:
    engine = app_state.engine
    return {cid: meta.get("name", cid) for cid, meta in (engine._frac_map.items() if engine else [])}


@router.get("/prerequisites")
async def prerequisite_dag(_admin: UserAuth = Depends(require_role("admin"))):
    """
    SCIL v6 §5 — the expert-seeded prerequisite DAG that build_study_plan
    enforces (after cycle validation), plus data-driven edge SUGGESTIONS from
    course outcome assessments. Suggestions are for human review and are never
    applied to any plan.
    """
    ref = app_state.ref
    names = _frac_names()
    if ref.outcomes and "prereq_suggestions" not in ref.cache:
        ref.cache["prereq_suggestions"] = prerequisite_service.infer_edges(
            ref.outcomes, ref.prerequisites, names)
    edges = [{**e, "fromName": names.get(e["from"]["competencyId"], e["from"]["competencyId"]),
              "toName": names.get(e["to"]["competencyId"], e["to"]["competencyId"])}
             for e in ref.prerequisites]
    return {
        "edges": edges,
        "validation": ref.prerequisite_check,
        "enforced": bool(ref.prerequisites),
        "inference": ref.cache.get("prereq_suggestions"),
        "dataNote": SYNTHETIC_NOTE,
    }
