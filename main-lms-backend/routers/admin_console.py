"""
routers/admin_console.py — admin console: server-side KPIs, trends, actions

All admin endpoints are `require_role("admin")`, under /api/v1/admin/console.
Every view takes the same filters: ?department=&grade=&office= (officeId).

  GET  /filters                 filter options with headcounts
  GET  /overview                KPIs, status counts, shortage heatmap, departmental compliance
  GET  /roster                  paginated, searchable roster (?page=&pageSize=&search=&status=)
  GET  /trends                  daily trend points (?days=): stored snapshots + reconstructed history
  POST /trends/snapshot         record today's snapshot now (upsert)
  GET  /courses                 catalogue search for the assign form (?q=)
  GET  /assignments             training plans assigned by admins, with completion progress
  POST /assignments             assign courses to a department (optionally narrowed) or officials
  GET  /mandatory-behind        officials with pending ACBP mandatory courses (paginated)
  GET  /nudges                  recent nudges
  POST /nudges                  nudge officials behind on mandatory training
  GET  /emerging-skills         required vs supply vs 36-month forecast — "what should NSSTA train next"
  GET  /system-health           /health + live probes (iGOT, DB, embedders, Gemini with ?probeGemini=true)
  GET  /export/{kind}.csv       roster | mandatory-behind | emerging-skills | trends | departments | shortages

Learner side (own data only, admins may read anyone's):
  GET  /api/v1/learner/{user_id}/training-actions   assignments + nudges addressed to the learner
  POST /api/v1/learner/{user_id}/nudges/{nudge_id}/read

The daily snapshot is recorded by daily_snapshot_loop (started in main._startup):
an upsert of today's row every SNAPSHOT_INTERVAL_S, so each day keeps its last
reading. Days before the first snapshot are reconstructed on read from dated
iGOT course completions (training rates only — competency levels need snapshots).
"""
from __future__ import annotations

import asyncio
import csv
import io
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response
from pydantic import BaseModel, Field

from adapters.igot_adapter import MockIgotAdapter
from auth.database import SessionLocal
from auth.dependencies import get_current_user, require_role
from auth.models import UserAuth
from models.models import AdminDailySnapshot, TrainingAssignment, TrainingNudge
from services import admin_analytics as aa
from services import app_state, gsbpm_service, system_health

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin/console", tags=["admin-console"])
learner_router = APIRouter(prefix="/api/v1/learner", tags=["admin-console"])

_adapter = MockIgotAdapter()
_ROSTER_TTL_S = 60.0
_roster_cache: Dict[str, Any] = {"expires": 0.0, "rows": None}
SNAPSHOT_INTERVAL_S = 3600
NUDGE_COOLDOWN_H = 24
DEFAULT_NUDGE = ("Reminder: you have mandatory ACBP courses pending for this cycle. "
                 "Please complete them on iGOT Karmayogi.")


# ── Shared helpers ─────────────────────────────────────────────────────────────

async def _roster(force: bool = False) -> List[Dict[str, Any]]:
    """Normalised roster rows, cached for _ROSTER_TTL_S (the mock returns every official)."""
    if not force and _roster_cache["rows"] is not None and time.monotonic() < _roster_cache["expires"]:
        return _roster_cache["rows"]
    try:
        raw = await _adapter.fetch_user_roster()
    except Exception as exc:
        if _roster_cache["rows"] is not None:          # serve stale rather than fail the dashboard
            log.warning("[admin-console] roster refresh failed, serving cached: %s", exc)
            return _roster_cache["rows"]
        raise HTTPException(status_code=502, detail=f"iGOT roster unavailable: {exc.__class__.__name__}")
    rows = [aa.normalise(u) for u in raw]
    _roster_cache.update(rows=rows, expires=time.monotonic() + _ROSTER_TTL_S)
    return rows


def _filters(
    department: Optional[str] = Query(None),
    grade: Optional[str] = Query(None),
    office: Optional[str] = Query(None, description="officeId"),
) -> aa.Filters:
    return aa.Filters(department or None, grade or None, office or None)


def _status_filter(rows: List[Dict[str, Any]], status: Optional[int]) -> List[Dict[str, Any]]:
    return rows if status is None else [r for r in rows if r["enrollmentStatus"] == status]


def _name(r: Dict[str, Any]) -> str:
    return f"{r['firstName']} {r['lastName']}".strip() or r["govId"]


def _db(fn):
    """Run fn(session) in the threadpool with a committed-or-rolled-back session."""
    def work():
        db = SessionLocal()
        try:
            out = fn(db)
            db.commit()
            return out
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    return run_in_threadpool(work)


def _csv(filename: str, header: List[str], rows: List[List[Any]]) -> Response:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(header)
    w.writerows(["" if v is None else v for v in r] for r in rows)
    return Response(content="﻿" + buf.getvalue(), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


# ── Filters, overview, roster ──────────────────────────────────────────────────

@router.get("/filters")
async def filter_options(_admin: UserAuth = Depends(require_role("admin"))):
    return aa.facets(await _roster())


@router.get("/overview")
async def overview(f: aa.Filters = Depends(_filters), _admin: UserAuth = Depends(require_role("admin"))):
    rows = aa.apply_filters(await _roster(), f)
    needs = [aa.public_row(r) for r in rows if r["enrollmentStatus"] == 0][:5]
    return {
        "filters": f.active(),
        "kpis": aa.kpis(rows),
        "statusCounts": aa.status_counts(rows),
        "heatmap": aa.heatmap(rows),
        "deptCompliance": aa.dept_compliance(rows),
        "needsTraining": needs,
        "asOf": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


@router.get("/roster")
async def roster_page(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=200),
    search: str = "",
    status: Optional[int] = Query(None, ge=0, le=2),
    f: aa.Filters = Depends(_filters),
    _admin: UserAuth = Depends(require_role("admin")),
):
    base = aa.search(aa.apply_filters(await _roster(), f), search)
    counts = aa.status_counts(base)
    result = aa.paginate(_status_filter(base, status), page, pageSize)
    result["items"] = [aa.public_row(r) for r in result["items"]]
    return {**result, "statusCounts": counts, "filters": f.active()}


# ── Trends (daily snapshots) ───────────────────────────────────────────────────

async def record_daily_snapshot() -> Dict[str, Any]:
    """Upsert today's AdminDailySnapshot from the live roster + workforce snapshot."""
    rows = await _roster(force=True)
    stored = aa.daily_metrics(rows, app_state.snapshot)
    day = _today()

    def upsert(db):
        row = db.get(AdminDailySnapshot, day)
        if row is None:
            db.add(AdminDailySnapshot(snapshotDate=day, metrics=stored))
        else:
            row.metrics = stored
            row.createdAt = datetime.utcnow()
        return {"date": day, "overall": stored["overall"], "workforceSnapshot": stored["workforceSnapshot"]}
    return await _db(upsert)


async def daily_snapshot_loop() -> None:
    """Started once from main._startup. Waits for the DB, gives the workforce snapshot
    a few minutes so the first row carries competency levels, then upserts hourly."""
    await app_state.db_ready.wait()
    for _ in range(40):                                   # ≤ 10 min for the workforce snapshot
        if app_state.snapshot_status not in ("not built", "building"):
            break
        await asyncio.sleep(15)
    while True:
        try:
            out = await record_daily_snapshot()
            log.info("[admin-console] daily snapshot %s recorded.", out["date"])
        except Exception as exc:
            log.warning("[admin-console] daily snapshot failed: %s", exc)
        await asyncio.sleep(SNAPSHOT_INTERVAL_S)


def _trend_loader(days: int):
    since = (datetime.now(timezone.utc).date() - timedelta(days=days)).isoformat()

    def load(db):
        return [(r.snapshotDate, r.metrics) for r in
                db.query(AdminDailySnapshot).filter(AdminDailySnapshot.snapshotDate >= since)
                .order_by(AdminDailySnapshot.snapshotDate).all()]
    return load


async def _trend_series(days: int, f: aa.Filters) -> Dict[str, Any]:
    """
    Stored daily snapshots where they exist (live readings, incl. competency
    levels); every other day in range is reconstructed from dated iGOT course
    completions for the exact filter (training rates only).
    """
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)
    rows = aa.apply_filters(await _roster(), f)
    rebuilt = aa.reconstruct_history(rows, start, end)
    stored = {d: p for d, m in await _db(_trend_loader(days)) if (p := aa.trend_point(d, m, f))}
    points = [stored.get(p["date"], p) for p in rebuilt["points"]]
    live = sorted(stored)
    return {"points": points, "weeklyCompletions": rebuilt["weeklyCompletions"],
            "liveSnapshots": len(live), "firstLiveSnapshot": live[0] if live else None}


@router.get("/trends")
async def trends(
    days: int = Query(90, ge=1, le=730),
    f: aa.Filters = Depends(_filters),
    _admin: UserAuth = Depends(require_role("admin")),
):
    series = await _trend_series(days, f)
    note = ("Training rates before the first daily snapshot are reconstructed from dated iGOT course "
            "completions (today's roster, current ACBP plan). Competency levels come only from daily "
            "snapshots, recorded since the feature was deployed.")
    if len(f.active()) > 1:
        note += " On snapshot days with several filters, the most specific stored breakdown is used."
    return {"days": days, "filters": f.active(), "scope": aa.trend_dimension(f), **series, "note": note}


@router.post("/trends/snapshot")
async def trends_snapshot_now(_admin: UserAuth = Depends(require_role("admin"))):
    return await record_daily_snapshot()


# ── Actions: assign courses / training plans ───────────────────────────────────

def _catalogue() -> Dict[str, Dict[str, Any]]:
    engine = app_state.engine
    if engine is None:
        raise HTTPException(status_code=503, detail="Course catalogue not loaded yet.")
    names = {cid: m.get("name", cid) for cid, m in engine._frac_map.items()}
    return {d.identifier: {"courseId": d.identifier, "title": d.name, "hours": d.duration_hrs,
                           "competencies": [names.get(c, c) for c in d.comp_ids]}
            for d in engine._catalog}


@router.get("/courses")
async def course_search(q: str = "", limit: int = Query(20, ge=1, le=50),
                        _admin: UserAuth = Depends(require_role("admin"))):
    ql = q.strip().lower()
    hits = [c for c in _catalogue().values()
            if not ql or ql in c["title"].lower() or ql in c["courseId"].lower()
            or any(ql in n.lower() for n in c["competencies"])]
    return {"courses": sorted(hits, key=lambda c: c["title"])[:limit], "total": len(hits)}


class AssignmentIn(BaseModel):
    title: str = Field(..., min_length=3, max_length=160)
    scope: Literal["department", "officials"]
    department: Optional[str] = None
    grade: Optional[str] = None         # narrows a department assignment
    office: Optional[str] = None
    userIds: List[str] = Field(default_factory=list)
    courseIds: List[str] = Field(..., min_length=1, max_length=25)
    dueDate: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    note: Optional[str] = Field(None, max_length=500)


def _assignment_out(a: TrainingAssignment, by_id: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    course_ids = {c["courseId"] for c in a.courses}
    assignees = [by_id[u] for u in a.assigneeIds if u in by_id]
    done = sum(course_ids <= set(r["completedCourseIds"]) for r in assignees)
    started = sum(bool(course_ids & set(r["completedCourseIds"])) for r in assignees)
    n = len(a.assigneeIds)
    return {
        "assignmentId": a.assignmentId, "title": a.title, "scope": a.scope, "department": a.department,
        "courses": a.courses, "assignees": n, "dueDate": a.dueDate, "note": a.note,
        "createdBy": a.createdBy, "createdAt": a.createdAt.isoformat() if a.createdAt else None,
        "progress": {"completedAll": done, "completedSome": started,
                     "completionPct": round(100 * done / n) if n else 0},
        "overdue": bool(a.dueDate and a.dueDate < _today() and done < n),
    }


@router.get("/assignments")
async def list_assignments(limit: int = Query(50, ge=1, le=200),
                           _admin: UserAuth = Depends(require_role("admin"))):
    by_id = {r["userId"]: r for r in await _roster()}
    # Serialise inside the session — rows are expired (unloadable) once it commits and closes.
    return {"assignments": await _db(lambda db: [
        _assignment_out(a, by_id) for a in
        db.query(TrainingAssignment).order_by(TrainingAssignment.createdAt.desc()).limit(limit).all()])}


@router.post("/assignments", status_code=201)
async def create_assignment(body: AssignmentIn, admin: UserAuth = Depends(require_role("admin"))):
    rows = await _roster()
    by_id = {r["userId"]: r for r in rows}
    if body.scope == "department":
        if not body.department:
            raise HTTPException(status_code=422, detail="department is required for a department assignment.")
        assignees = aa.apply_filters(rows, aa.Filters(body.department, body.grade, body.office))
    else:
        unknown = [u for u in body.userIds if u not in by_id]
        if not body.userIds or unknown:
            raise HTTPException(status_code=422, detail=f"Unknown or missing userIds: {unknown[:5]}")
        assignees = [by_id[u] for u in dict.fromkeys(body.userIds)]
    if not assignees:
        raise HTTPException(status_code=422, detail="No officials match this assignment.")
    catalogue = _catalogue()
    missing = [c for c in body.courseIds if c not in catalogue]
    if missing:
        raise HTTPException(status_code=422, detail=f"Courses not in the catalogue: {missing[:5]}")
    courses = [{k: catalogue[c][k] for k in ("courseId", "title", "hours")} for c in dict.fromkeys(body.courseIds)]

    def create(db):
        a = TrainingAssignment(title=body.title.strip(), scope=body.scope, department=body.department,
                               courses=courses, assigneeIds=[r["userId"] for r in assignees],
                               dueDate=body.dueDate, note=body.note, createdBy=admin.username)
        db.add(a)
        db.flush()
        db.refresh(a)
        return _assignment_out(a, by_id)
    out = await _db(create)
    log.info("[admin-console] %s assigned %d course(s) to %d official(s).",
             admin.username, len(courses), len(assignees))
    return out


# ── Actions: nudge officials behind on mandatory training ──────────────────────

def _last_nudges(user_ids: List[str]):
    def load(db):
        out: Dict[str, datetime] = {}
        q = db.query(TrainingNudge.userId, TrainingNudge.createdAt)
        if user_ids:
            q = q.filter(TrainingNudge.userId.in_(user_ids))
        for uid, at in q.all():
            if uid not in out or at > out[uid]:
                out[uid] = at
        return out
    return load


def _behind_row(r: Dict[str, Any], last: Optional[datetime]) -> Dict[str, Any]:
    m = r["mandatory"]
    return {"userId": r["userId"], "govId": r["govId"], "name": _name(r), "designation": r["designation"],
            "department": r["department"], "grade": r["grade"], "gradeLabel": r["gradeLabel"],
            "officeName": r["officeName"], "completed": m["completed"], "total": m["total"],
            "pending": m["pending"], "lastNudgedAt": last.isoformat() if last else None}


async def _behind(f: aa.Filters, search: str = "") -> List[Dict[str, Any]]:
    rows = [r for r in aa.search(aa.apply_filters(await _roster(), f), search) if aa.is_behind_mandatory(r)]
    last = await _db(_last_nudges([r["userId"] for r in rows]))
    out = [_behind_row(r, last.get(r["userId"])) for r in rows]
    out.sort(key=lambda x: (-(x["total"] - x["completed"]), x["name"]))
    return out


@router.get("/mandatory-behind")
async def mandatory_behind(
    page: int = Query(1, ge=1), pageSize: int = Query(10, ge=1, le=200), search: str = "",
    f: aa.Filters = Depends(_filters), _admin: UserAuth = Depends(require_role("admin")),
):
    rows = await _behind(f, search)
    return {**aa.paginate(rows, page, pageSize),
            "summary": aa.mandatory_summary(aa.apply_filters(await _roster(), f)), "filters": f.active()}


class NudgeIn(BaseModel):
    userIds: List[str] = Field(default_factory=list)   # empty → everyone behind within the filters
    department: Optional[str] = None
    grade: Optional[str] = None
    office: Optional[str] = None
    message: Optional[str] = Field(None, max_length=500)
    force: bool = False                                 # ignore the NUDGE_COOLDOWN_H cooldown


@router.post("/nudges", status_code=201)
async def send_nudges(body: NudgeIn, admin: UserAuth = Depends(require_role("admin"))):
    behind = {r["userId"]: r for r in await _behind(aa.Filters(body.department, body.grade, body.office))}
    targets = body.userIds or list(behind)
    skipped = [{"userId": u, "reason": "not behind on mandatory training"} for u in targets if u not in behind]
    cutoff = datetime.utcnow() - timedelta(hours=NUDGE_COOLDOWN_H)
    to_send = []
    for u in targets:
        if u not in behind:
            continue
        last = behind[u]["lastNudgedAt"]
        if not body.force and last and datetime.fromisoformat(last) > cutoff:
            skipped.append({"userId": u, "reason": f"already nudged in the last {NUDGE_COOLDOWN_H} h"})
        else:
            to_send.append(behind[u])
    message = (body.message or "").strip() or DEFAULT_NUDGE

    def create(db):
        for r in to_send:
            db.add(TrainingNudge(userId=r["userId"], message=message, createdBy=admin.username,
                                 pendingCourses=[{"courseId": c["courseId"], "title": c["title"]}
                                                 for c in r["pending"]]))
    await _db(create)
    log.info("[admin-console] %s nudged %d official(s).", admin.username, len(to_send))
    return {"sent": len(to_send), "skipped": skipped, "message": message}


@router.get("/nudges")
async def recent_nudges(limit: int = Query(50, ge=1, le=500), _admin: UserAuth = Depends(require_role("admin"))):
    by_id = {r["userId"]: r for r in await _roster()}

    def load(db):
        return [{"nudgeId": n.nudgeId, "userId": n.userId,
                 "name": _name(by_id[n.userId]) if n.userId in by_id else n.userId,
                 "department": by_id.get(n.userId, {}).get("department"),
                 "message": n.message, "pendingCourses": n.pendingCourses or [],
                 "createdBy": n.createdBy, "createdAt": n.createdAt.isoformat(),
                 "readAt": n.readAt.isoformat() if n.readAt else None}
                for n in db.query(TrainingNudge).order_by(TrainingNudge.createdAt.desc()).limit(limit).all()]
    return {"nudges": await _db(load)}


# ── Emerging skills ────────────────────────────────────────────────────────────

def _emerging(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    from services import proficiency_service
    if not app_state.snapshot:
        raise HTTPException(status_code=503,
                            detail=f"Workforce snapshot not ready ({app_state.snapshot_status}). Try again shortly.")
    engine, ref = app_state.engine, app_state.ref
    names = {cid: m.get("name", cid) for cid, m in (engine._frac_map.items() if engine else [])}
    in_scope = set()
    if ref.gsbpm and ref.offices:
        if "gsbpm_in_scope" not in ref.cache:
            scope = gsbpm_service.scope_report(ref.gsbpm, ref.offices, names=names)
            ref.cache["gsbpm_in_scope"] = {c["competencyId"] for c in scope["competencies"] if c["inScope"]}
        in_scope = ref.cache["gsbpm_in_scope"]
    critical = {c for comps in (ref.hrms or {}).get("productCriticalCompetencies", {}).values() for c in comps}
    flagged: Dict[str, int] = {}
    for c in (ref.cache.get("uplift") or {}).get("courses", []):
        if c.get("misTagFlag"):
            flagged[c["competencyId"]] = flagged.get(c["competencyId"], 0) + 1
    return aa.emerging_skills(
        rows, app_state.snapshot, ref.hrms, names, proficiency_service.population_stats(app_state.snapshot),
        in_scope, critical, (engine.levels_available if engine else (lambda _c: set())), flagged)


@router.get("/emerging-skills")
async def emerging_skills(f: aa.Filters = Depends(_filters), _admin: UserAuth = Depends(require_role("admin"))):
    rows = aa.apply_filters(await _roster(), f)
    return {**_emerging(rows), "filters": f.active(),
            "dataNote": "Computed on synthetic mock data — demo only."}


# ── System health ──────────────────────────────────────────────────────────────

@router.get("/system-health")
async def system_health_panel(probeGemini: bool = False, _admin: UserAuth = Depends(require_role("admin"))):
    out = await system_health.detailed(probe_gemini=probeGemini)
    last = await _db(lambda db: db.query(AdminDailySnapshot.snapshotDate)
                     .order_by(AdminDailySnapshot.snapshotDate.desc()).limit(1).scalar())
    out["lastDailySnapshot"] = last
    return out


# ── CSV exports (respect the same filters as the views) ────────────────────────

@router.get("/export/{kind}.csv")
async def export_csv(
    kind: Literal["roster", "mandatory-behind", "emerging-skills", "trends", "departments", "shortages"],
    search: str = "", status: Optional[int] = Query(None, ge=0, le=2), days: int = Query(90, ge=1, le=730),
    f: aa.Filters = Depends(_filters), _admin: UserAuth = Depends(require_role("admin")),
):
    stamp = _today()
    tag = "-".join(f.active().values()).replace(" ", "_") or "all"
    rows = aa.apply_filters(await _roster(), f)
    if kind == "roster":
        rs = _status_filter(aa.search(rows, search), status)
        return _csv(f"nso-roster-{tag}-{stamp}.csv",
                    ["Gov ID", "User ID", "First name", "Last name", "Email", "Designation", "Department",
                     "Grade", "Office", "Top missing skill", "Status", "Mandatory completed", "Mandatory total"],
                    [[r["govId"], r["userId"], r["firstName"], r["lastName"], r["email"], r["designation"],
                      r["department"], r["gradeLabel"], r["officeName"], r["missingSkill"],
                      aa.STATUS_LABELS[r["enrollmentStatus"]],
                      (r["mandatory"] or {}).get("completed"), (r["mandatory"] or {}).get("total")] for r in rs])
    if kind == "mandatory-behind":
        rs = await _behind(f, search)
        return _csv(f"mandatory-behind-{tag}-{stamp}.csv",
                    ["Gov ID", "Name", "Department", "Grade", "Office", "Completed", "Total", "Pending courses",
                     "Last nudged"],
                    [[r["govId"], r["name"], r["department"], r["gradeLabel"], r["officeName"], r["completed"],
                      r["total"], "; ".join(c["title"] for c in r["pending"]), r["lastNudgedAt"]] for r in rs])
    if kind == "emerging-skills":
        e = _emerging(rows)
        return _csv(f"emerging-skills-{tag}-{stamp}.csv",
                    ["Rank", "Competency", "Required", "Supply now", "Expected supply 36m", "Shortfall now",
                     "Shortfall 36m", "Rising", "GSBPM scope", "Product critical", "Missing catalogue levels",
                     "Priority", "Train next year", "Recommended action"],
                    [[i["rank"], i["competencyName"], i["required"]["display"], i["supplyNow"]["display"],
                      i["expectedSupply36"]["display"], i["shortfallNow"]["display"], i["shortfall36"]["display"],
                      i["rising"], i["inScope"], i["critical"],
                      " ".join(map(str, i["missingCatalogueLevels"])), i["priorityScore"], i["trainNextYear"],
                      i["recommendedAction"]] for i in e["items"]])
    if kind == "trends":
        pts = (await _trend_series(days, f))["points"]
        cols = ["reconstructed", "officials", "compliancePct", "mandatoryCompletionPct", "behindMandatory", "avgMissingSkills",
                "avgLevel", "atTargetPct", "assessedPct"]
        return _csv(f"workforce-trends-{tag}-{stamp}.csv", ["date", *cols],
                    [[p["date"], *[p.get(c) for c in cols]] for p in pts])
    if kind == "departments":
        return _csv(f"department-compliance-{tag}-{stamp}.csv",
                    ["Department", "Headcount", "Compliance %", "Mandatory completion %", "Behind mandatory"],
                    [[d["dept"], d["headcount"], d["pct"], d["mandatoryPct"], d["behindMandatory"]["display"]]
                     for d in aa.dept_compliance(rows)])
    return _csv(f"competency-shortage-index-{tag}-{stamp}.csv", ["Competency", "Shortage index", "Officials"],
                [[h["competency"], h["gap"], h["officials"]["display"]] for h in aa.heatmap(rows, top=100)])


# ── Learner side: what admins sent me ──────────────────────────────────────────

def _ensure_self_or_admin(user_id: str, user: UserAuth) -> None:
    if user.username != user_id and user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only view your own training actions.")


@learner_router.get("/{user_id}/training-actions")
async def my_training_actions(user_id: str, current_user: UserAuth = Depends(get_current_user)):
    _ensure_self_or_admin(user_id, current_user)

    def load(db):
        nudges = (db.query(TrainingNudge).filter(TrainingNudge.userId == user_id)
                  .order_by(TrainingNudge.createdAt.desc()).limit(20).all())
        # JSON-array membership isn't portable across SQLite/Postgres; the table is small.
        assigns = [a for a in db.query(TrainingAssignment).order_by(TrainingAssignment.createdAt.desc()).all()
                   if user_id in (a.assigneeIds or [])]
        return (
            [{"nudgeId": n.nudgeId, "message": n.message, "pendingCourses": n.pendingCourses or [],
              "createdAt": n.createdAt.isoformat(), "readAt": n.readAt.isoformat() if n.readAt else None}
             for n in nudges],
            [{"assignmentId": a.assignmentId, "title": a.title, "courses": a.courses, "dueDate": a.dueDate,
              "note": a.note, "createdAt": a.createdAt.isoformat()} for a in assigns],
        )
    nudges, assignments = await _db(load)
    return {"userId": user_id, "nudges": nudges, "assignments": assignments,
            "unread": sum(n["readAt"] is None for n in nudges)}


@learner_router.post("/{user_id}/nudges/{nudge_id}/read")
async def mark_nudge_read(user_id: str, nudge_id: str, current_user: UserAuth = Depends(get_current_user)):
    if current_user.username != user_id:
        raise HTTPException(status_code=403, detail="Only the recipient can mark a nudge read.")

    def mark(db):
        n = db.get(TrainingNudge, nudge_id)
        if n is None or n.userId != user_id:
            raise HTTPException(status_code=404, detail="Nudge not found.")
        n.readAt = n.readAt or datetime.utcnow()
        return {"nudgeId": n.nudgeId, "readAt": n.readAt.isoformat()}
    return await _db(mark)
