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
from services import app_state, gsbpm_service

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
