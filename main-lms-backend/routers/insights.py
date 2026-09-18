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


@router.get("/training-effectiveness")
async def training_effectiveness(
    competencyId: Optional[str] = None,
    flaggedOnly: bool = False,
    minLearners: int = 0,
    _admin: UserAuth = Depends(require_role("admin")),
):
    """
    SCIL v6 §6 — courses by measured uplift (propensity-weighted, shrunk, 95%
    bootstrap CI) with the mis-tag flag (declared relevance high, uplift ≈ 0).
    Computed once at startup by services/uplift_service.py on synthetic data.
    """
    ref = app_state.ref
    est = ref.cache.get("uplift")
    if not est:
        raise HTTPException(status_code=503, detail="Course outcome data not loaded — no uplift estimates.")
    courses = [c for c in est["courses"]
               if (not competencyId or c["competencyId"] == competencyId)
               and (not flaggedOnly or c["misTagFlag"]) and c["n"] >= minLearners]
    all_courses = est["courses"]
    return {
        "summary": {
            "courses": len(all_courses),
            "learnerRecords": len(ref.outcomes),
            "comparisonEpisodes": len(ref.comparisons),
            "flagged": sum(c["misTagFlag"] for c in all_courses),
            "medianMeasuredUplift": sorted(c["measuredUplift"] for c in all_courses)[len(all_courses) // 2],
            "priorsByLevel": est["priors"],
        },
        "courses": courses,
        "constants": est["constants"],
        "method": est["method"],
        "dataNote": SYNTHETIC_NOTE + " Effects in this data are planted by the generator; recovering them "
                                     "shows the method works, it is not a validation.",
    }


# ── Workforce foresight (SCIL v6 §11) ─────────────────────────────────────────

def _snapshot_or_503():
    if not app_state.snapshot:
        raise HTTPException(status_code=503,
                            detail=f"Workforce snapshot not ready ({app_state.snapshot_status}). Try again shortly.")
    return app_state.snapshot


def _workforce() -> dict:
    """capability risk + foresight computed once per snapshot."""
    from services import proficiency_service, workforce_service
    ref = app_state.ref
    if "workforce" not in ref.cache:
        snap = _snapshot_or_503()
        if not ref.hrms:
            raise HTTPException(status_code=503, detail="HRMS data not loaded.")
        names = _frac_names()
        population = proficiency_service.population_stats(snap)
        ref.cache["workforce"] = {
            "risk": workforce_service.capability_risk(snap, ref.hrms, names),
            "foresight": workforce_service.foresight(snap, ref.hrms, names, population),
        }
    return ref.cache["workforce"]


@router.get("/workforce/status")
async def workforce_status(_admin: UserAuth = Depends(require_role("admin"))):
    snap = app_state.snapshot or {}
    return {"status": app_state.snapshot_status, "officials": len(snap), "dataNote": SYNTHETIC_NOTE}


@router.post("/workforce/refresh")
async def workforce_refresh(_admin: UserAuth = Depends(require_role("admin"))):
    """Rebuild the workforce snapshot now (≈ a few seconds)."""
    if app_state.snapshot_builder is None:
        raise HTTPException(status_code=503, detail="Snapshot builder not available.")
    await app_state.snapshot_builder()
    return await workforce_status(_admin)


@router.get("/workforce/capability-risk")
async def capability_risk(_admin: UserAuth = Depends(require_role("admin"))):
    """Per statistical product: capable officials per critical competency, retirements within
    36 months, single-point-of-failure flags. Counts of 1–4 are suppressed."""
    return {**_workforce()["risk"], "dataNote": SYNTHETIC_NOTE}


@router.get("/workforce/foresight")
async def workforce_foresight(_admin: UserAuth = Depends(require_role("admin"))):
    """36-month projection of expected capable officials: attrition × dated skill decay."""
    return {**_workforce()["foresight"], "dataNote": SYNTHETIC_NOTE}


@router.get("/workforce/tpac-agenda")
async def tpac_agenda(_admin: UserAuth = Depends(require_role("admin"))):
    """Draft TPAC agenda items from coverage gaps, capability risk, near-zero-uplift courses
    and proposed prerequisites — drafts for the committee, nothing is decided."""
    from services import workforce_service
    ref = app_state.ref
    wf = _workforce()
    names = _frac_names()
    if ref.outcomes and "prereq_suggestions" not in ref.cache:
        ref.cache["prereq_suggestions"] = prerequisite_service.infer_edges(ref.outcomes, ref.prerequisites, names)
    in_scope = set()
    if ref.gsbpm and ref.offices:
        scope = gsbpm_service.scope_report(ref.gsbpm, ref.offices, names=names)
        in_scope = {c["competencyId"] for c in scope["competencies"] if c["inScope"]}
    agenda = workforce_service.tpac_agenda(app_state.snapshot, app_state.engine, names, wf["risk"],
                                           wf["foresight"], ref.cache.get("uplift"),
                                           ref.cache.get("prereq_suggestions"), in_scope)
    return {**agenda, "dataNote": SYNTHETIC_NOTE}


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
