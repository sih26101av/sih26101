"""
main.py — MoSPI LMS Backend API (Main Orchestrator)
─────────────────────────────────────────────────────────────────────────────
Service #3: My App Backend (port 8000)

Responsibilities
────────────────
• Owns all application-level authentication & authorisation (JWT + RBAC).
• Calls the Mock iGOT Server (port 8001) as an internal data-fetch step
  AFTER a request has been authenticated/authorised here.
• Never stores auth data on the mock server; never proxies raw tokens.

On startup: creates users_auth table in auth.db (idempotent).
"""

from routers import competency
from services.recommendation_service import CLASSROOM_CAP_HOURS_PER_QUARTER, HybridRecommendationEngine
from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from adapters.igot_adapter import MockIgotAdapter
from auth.database import AuthBase, engine
from auth.dependencies import get_current_user, require_role
from auth.models import UserAuth
from auth.router import router as auth_router
from models.domain import (
    AchievementsResponse,
    EnrollmentsResponse,
    RecommendationResponse,
    SkillGapResponse,
)
from routers.chatbot import router as chatbot_router
from routers.rag import router as rag_router
from routers.ai_tools import router as ai_tools_router
from routers.karma import router as karma_router
import httpx
import json
import os
import uvicorn


# ── App bootstrap ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="MoSPI LMS Backend API",
    description="Main Orchestrator Server — owns auth, delegates data to iGOT adapter",
    version="2.0",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
# Tightened from allow_origins=["*"] to explicit frontend origin so that
# httpOnly cookies are accepted (credentials require a non-wildcard origin).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",   # Vite default dev server port
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,   # Required for cookies to be sent cross-origin
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup: create auth.db table ─────────────────────────────────────────────
# ── App-level recommendation engine singleton ─────────────────────────────────
# Built once at startup: loads catalog JSON, builds FAISS index + BM25 corpus.
# All recommendation requests share this singleton (thread-safe read-only).
from services.baseline_assembler import BaselineAssembler

# ── App-level recommendation engine singleton ─────────────────────────────────
# Built once at startup: loads catalog JSON, builds FAISS index + BM25 corpus.
# All recommendation requests share this singleton (thread-safe read-only).
_rec_engine: HybridRecommendationEngine | None = None

# ── App-level baseline assembler singleton ────────────────────────────────────
# Shares the course→comp index from _rec_engine so we don't duplicate it.
_assembler: BaselineAssembler | None = None

# ── SCIL v6 reference data (GSBPM map, office workload, …) ────────────────────
from services.reference_data import ReferenceData
from services import app_state, gsbpm_service, prerequisite_service
_ref: ReferenceData = ReferenceData()



@app.on_event("startup")
async def _startup():
    """Create users_auth table and karma tables if they don't exist yet."""
    global _rec_engine, _assembler
    AuthBase.metadata.create_all(bind=engine)
    # Create karma tables (KarmaEvent, KarmaMonthlyUsage) in the same auth.db
    from models.models import Base as DomainBase
    DomainBase.metadata.create_all(bind=engine)

    # Load the chat embedder and encode intent prototypes now; done lazily this
    # takes ~30s and the first chat request would outlast the frontend's patience.
    from ai.semantic_engine import _ensure_prototypes
    _ensure_prototypes()

    import logging
    log = logging.getLogger(__name__)

    # One catalogue: rank over exactly what the mock iGOT server serves. If it
    # is down, fall back to the same generated files on disk (and say so).
    catalog = frac = crosswalk = None
    try:
        catalog   = await adapter.fetch_catalog()
        frac      = await adapter.fetch_frac_competencies()
        crosswalk = await adapter.fetch_frac_crosswalk()
        log.info("[startup] Catalogue loaded from iGOT adapter: %d courses, %d FRAC competencies.",
                 len(catalog), len(frac))
    except Exception as exc:
        catalog = frac = crosswalk = None
        log.warning("[startup] iGOT mock server unreachable (%s) — loading the catalogue from "
                    "mock-igot-server/data/*.json on disk instead.", exc)

    try:
        _rec_engine = HybridRecommendationEngine(catalog=catalog, frac=frac, crosswalk=crosswalk)
        log.info("[startup] HybridRecommendationEngine ready (catalogue source: %s).",
                 _rec_engine.catalog_source)

        # {course_id → {comp_id → FRAC level}} from the same tags the engine filters
        # on, so the Verified channel credits a completed course at its tagged level.
        course_comp_map = _rec_engine.course_comp_levels()

        _assembler = BaselineAssembler(course_comp_map)
        log.info("[startup] BaselineAssembler ready. Mapped %d courses.", len(course_comp_map))

    except Exception as exc:
        log.error("[startup] Engine/Assembler failed to initialise: %s", exc)
        _rec_engine = None
        _assembler  = None

    # SCIL v6 reference data (GSBPM map, office workload, …) — adapter, disk fallback.
    global _ref
    _ref = await ReferenceData.load(adapter)
    app_state.engine, app_state.assembler, app_state.ref = _rec_engine, _assembler, _ref

    # SCIL v6 §6: measured course uplift from outcome assessments (~1 s), used to
    # flag near-zero-uplift courses in ranking and for the admin effectiveness view.
    if _ref.outcomes and _rec_engine is not None:
        from services.uplift_service import estimate_uplift
        try:
            _ref.cache["uplift"] = estimate_uplift(_ref.outcomes, _ref.comparisons, _rec_engine.course_meta())
            _rec_engine.set_measured_uplift(_ref.cache["uplift"]["courses"])
            log.info("[startup] Measured uplift for %d courses (%d flagged).",
                     len(_ref.cache["uplift"]["courses"]),
                     sum(c["misTagFlag"] for c in _ref.cache["uplift"]["courses"]))
        except Exception as exc:
            log.error("[startup] Uplift estimation failed: %s", exc)





# ── Register routers ───────────────────────────────────────────────────────────
app.include_router(auth_router,    prefix="/auth",       tags=["auth"])
app.include_router(chatbot_router, prefix="/api/v1",     tags=["chatbot"])
app.include_router(rag_router,     prefix="/api/v1/rag", tags=["rag"])
app.include_router(ai_tools_router,prefix="/api/v1/ai",  tags=["ai-tools"])
app.include_router(karma_router,   prefix="/api/v1",     tags=["karma"])
app.include_router(competency.router)
from routers.insights import router as insights_router
app.include_router(insights_router)
    
    



# ── iGOT Adapter singleton (HTTP → mock_igot_server.py on port 8001) ────────────
# Data only flows when the Sunbird-compliant mock server is running.
# Run: cd mock-igot-server && uvicorn mock_igot_server:app --reload --port 8001
adapter = MockIgotAdapter()

# ── iGOT mock server config (kept for admin proxy endpoint) ────────────────────
_IGOT_BASE = os.getenv("IGOT_MOCK_BASE_URL", "http://localhost:8001")
_IGOT_TOKEN = os.getenv("IGOT_MOCK_TOKEN", "mock-api-key-2026")




# ── Helper: parse competency level string → int ────────────────────────────────
def _level_to_int(level_str: str) -> int:
    """'Level 3' → 3, 'Level 2' → 2, fallback → 2"""
    digits = "".join(filter(str.isdigit, level_str or ""))
    return int(digits) if digits else 2


# ── Skill-gap / recommendation / pathway shared state ─────────────────────────

def _ensure_can_view(user_id: str, current_user: UserAuth) -> None:
    """A learner may only read their own competency data; admins may read anyone's."""
    from fastapi import HTTPException
    if current_user.username != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only view your own learning data.")


def _self_reported_level(comp: dict) -> int:
    """iGOT profile competencyLevel ('Level 3') → 3; missing → 0 (no claim)."""
    import re
    m = re.search(r"\d+", comp.get("competencyLevel") or "")
    return int(m.group()) if m else 0


async def _learner_competency_state(user_id: str) -> dict:
    """
    Profile + enrollments + EvidenceLog → one resolved row per role competency.

    This is the ONLY place a learner's level is decided (via
    baseline_assembler.resolve_level); skill-gaps, recommendations and pathway
    all read these rows, so the dashboard and the course suggestions can no
    longer disagree about the same gap.
    """
    from fastapi import HTTPException
    from auth.database import get_db
    from models.models import EvidenceLog
    from services.baseline_assembler import resolve_level

    try:
        user = await adapter.fetch_user_by_id(user_id)
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="iGOT mock server is unreachable. Start it with: "
                   "cd mock-igot-server && uvicorn mock_igot_server:app --port 8001",
        )
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")

    try:
        enrollments = await adapter.fetch_user_enrollments(user_id)
    except Exception:
        enrollments = []

    db_session = next(get_db())
    try:
        db_evidence = [
            {
                "comp_id":       row.compId,
                "evidence_type": row.evidenceType,
                "granted_value": row.grantedValue,
                "issue_date":    row.issueDate,
            }
            for row in db_session.query(EvidenceLog).filter(EvidenceLog.userId == user_id).all()
        ]
    except Exception:
        db_evidence = []
    finally:
        db_session.close()

    raw_comps = user.get("competencies") or \
                (user.get("profileDetails") or {}).get("competencies") or []
    seen_ids: set = set()
    comps = []
    for comp in raw_comps:
        cid = comp.get("id", "")
        if cid and cid not in seen_ids:
            seen_ids.add(cid)
            comps.append(comp)

    # Role profiles may use a wider FRAC dictionary than the catalogue is tagged
    # with; map each competency to the catalogue competency that serves it.
    crosswalks = {
        c["id"]: (_rec_engine.crosswalk(c["id"], c.get("name") or "") if _rec_engine else None)
        for c in comps
    }
    aliases = {cid: xw["catalogueId"] for cid, xw in crosswalks.items()
               if xw and xw["catalogueId"] != cid}

    baseline_results = (
        _assembler.compute_for_user(user=user, enrollments=enrollments,
                                    db_evidence=db_evidence, comp_aliases=aliases)
        if _assembler is not None else {}
    )

    office = _ref.offices.get((user.get("jobProfile") or {}).get("officeId") or "")
    gsbpm_subs = _ref.gsbpm.get("competencies", {})

    rows = []
    for comp in comps:
        cid = comp["id"]
        bline = baseline_results.get(cid, {})
        resolved = resolve_level(bline, _self_reported_level(comp))
        catalogue_id = (crosswalks[cid] or {}).get("catalogueId") or cid
        rows.append({
            "competencyId":  cid,
            "name":          (comp.get("name") or "").strip(),
            "type":          comp.get("type", "Functional"),
            "targetLevel":   int(comp.get("requiredLevel") or 3),
            "currentLevel":  resolved["level"],          # None when UNASSESSED
            "confidence":    resolved["confidence"],
            "basis":         resolved["basis"],          # evidence | course_completion | self_report | none
            "evidenceLevel": resolved["evidenceLevel"],
            "rawScore":      float(bline.get("score", 0.0)),
            "evidence":      bline.get("_evidence", {}),
            "catalogueId":   (crosswalks[cid] or {}).get("catalogueId"),
            "crosswalk":     crosswalks[cid],                # None → not in catalogue
            # SCIL v6 §4: how much the official's office works in this
            # competency's GSBPM sub-processes this cycle (badge + tie-break only)
            "opportunity":   gsbpm_service.opportunity(office, gsbpm_subs.get(catalogue_id, []),
                                                       _ref.gsbpm, _ref.cycle),
        })

    return {"user": user, "enrollments": enrollments, "competencies": rows}


# ─────────────────────────────────────────────────────────────────────────────
# LEARNER ENDPOINTS — by userId (usr_...)
# All data access goes through adapter methods (Adapter pattern / OCP).
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/v1/profile/{user_id}")
async def get_profile_by_user_id(
    user_id: str,
    _current_user: UserAuth = Depends(get_current_user),
):
    """
    Full user profile for the given iGOT userId (usr_...).
    Reads from profileDetails.professionalDetails and profileDetails.competencies.
    """
    from fastapi import HTTPException
    user = await adapter.fetch_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")

    prof = (user.get("profileDetails") or {}).get("professionalDetails") or [{}]
    prof = prof[0] if prof else {}
    competencies = (user.get("profileDetails") or {}).get("competencies") or []

    return {
        "userId":       user.get("userId"),
        "govId":        user.get("govId"),
        "firstName":    user.get("firstName"),
        "lastName":     user.get("lastName"),
        "email":        user.get("email"),
        "designation":  prof.get("designation", "Official"),
        "department":   prof.get("department", "MoSPI"),
        "experienceYears": user.get("experienceYears", 0),
        "competencies": competencies,
    }


@app.get("/api/v1/learner/{user_id}/skill-gaps")
async def get_skill_gaps_by_user_id(
    user_id: str,
    current_user: UserAuth = Depends(get_current_user),
):
    """
    Skill-gap analysis on the 6-term baseline formula — a weighted mean over
    the evidence channels that are actually present (see
    services/competency_service.py):

      b_k = clamp(mean_w(Verified, Documented, Tenure, SelfReport, Education,
                         Seniority) + synergy_k, 0, ConfidenceCeiling_k)

    Evidence sources:
      Verified    — completed iGOT/NSSTA courses, credited at their FRAC tag level
      Documented  — certificates + passed practice assessments (EvidenceLog DB)
      Tenure      — career history from user profile (role-relevant, decayed)
      SelfReport  — EvidenceLog SELF_REPORT rows (0 if not provided)
      Education   — degree relevance to competency type
      Seniority   — designation tier (only for Behavioural; 0 otherwise)

    The displayed level comes from baseline_assembler.resolve_level — the same
    value /recommendations and /pathway use. `basis` says what set it
    (evidence | course_completion | self_report | none); LOW / UNASSESSED
    levels get a diagnostic step first in the learning pathway.
    """
    _ensure_can_view(user_id, current_user)
    from services.baseline_assembler import is_completed

    # ── FRAC type → frontend CompetencyDomain ─────────────────────────────
    _DOMAIN_MAP: dict[str, str] = {
        "Domain":      "Statistical",
        "Functional":  "Governance",
        "Behavioural": "Leadership",
        "Technical":   "Technical",
        "COMPETENCY":  "Statistical",
    }

    state = await _learner_competency_state(user_id)
    user, enrollments, rows = state["user"], state["enrollments"], state["competencies"]

    prof_list = (user.get("profileDetails") or {}).get("professionalDetails") or [{}]
    prof      = prof_list[0] if prof_list else {}

    # Two comps sharing a name but not an id (mock data artifact) get the id
    # appended so the UI shows them as distinct.
    name_counts: dict[str, int] = {}
    for row in rows:
        name_counts[row["name"]] = name_counts.get(row["name"], 0) + 1

    skill_gaps = []
    for row in rows:
        current = row["currentLevel"]
        skill_gaps.append({
            "competencyId":  row["competencyId"],
            "skillName":     row["name"] if name_counts.get(row["name"], 1) == 1
                             else f"{row['name']} ({row['competencyId']})",
            "domain":        _DOMAIN_MAP.get(row["type"], "Governance"),
            "currentLevel":  current,                        # None when UNASSESSED
            "targetLevel":   row["targetLevel"],
            "gapScore":      max(0, row["targetLevel"] - current) if current is not None else None,
            "confidence":    row["confidence"],              # "UNASSESSED" | "LOW" | "MEDIUM" | "HIGH"
            "basis":         row["basis"],
            "evidenceLevel": row["evidenceLevel"],
            "rawScore":      round(row["rawScore"], 3),
            "evidence":      row["evidence"],                # per-channel breakdown dict
            "crosswalk":     row["crosswalk"],               # catalogue competency serving it
            "opportunity":   row["opportunity"],             # Low | Medium | High this cycle (or None)
        })

    # Sort: known gaps first (largest gap, lowest score), UNASSESSED last
    skill_gaps.sort(key=lambda g: (
        g["gapScore"] is None,           # False (0) sorts before True (1)
        -(g["gapScore"] or 0),           # larger gap first
        g["rawScore"],                   # lower raw score first within same gap
    ))

    return {
        "userId":           user_id,
        "govId":            user.get("govId", user_id),
        "jobRole":          prof.get("designation", "Official"),
        "department":       prof.get("department", "MoSPI"),
        "totalCourses":     len(enrollments),
        "completedCourses": sum(1 for e in enrollments if is_completed(e)),
        "skillGaps":        skill_gaps,
    }


@app.get("/api/v1/learner/{user_id}/enrollments")
async def get_enrollments_by_user_id(
    user_id: str,
    _current_user: UserAuth = Depends(get_current_user),
):
    """Active/in-progress enrollments for a learner by iGOT userId."""
    raw_enrollments = await adapter.fetch_user_enrollments(user_id)

    enrollments = []
    for i, e in enumerate(raw_enrollments):
        status_int = e.get("status", 0)
        # Show both IN_PROGRESS (1) and COMPLETED (2) courses
        status_label = "Completed" if status_int == 2 else "In Progress" if status_int == 1 else "Not Started"
        leaf = e.get("leafNodesCount", 0) or 1
        progress_pct = e.get("completionPercentage", 0)
        # Hours from the catalogue `duration` (seconds) when the course is known;
        # the old rule (0.5 h per leaf module) only as a fallback.
        catalogue_hrs = _rec_engine.course_hours(e.get("courseId", "")) if _rec_engine else None
        if catalogue_hrs:
            total_hrs     = round(catalogue_hrs, 1)
            remaining_hrs = round(catalogue_hrs * (1 - (progress_pct or 0) / 100.0), 1)
        else:
            done_nodes    = int(leaf * progress_pct / 100) if progress_pct else e.get("progress", 0)
            remaining_hrs = round(max(0, leaf - done_nodes) * 0.5, 1)
            total_hrs     = round(leaf * 0.5, 1)

        enrollments.append({
            "enrollmentId":       f"ENR-{user_id}-{i:03d}",
            "courseId":           e.get("courseId", ""),
            "courseTitle":        e.get("courseName", ""),
            "provider":           e.get("channel", "iGOT Karmayogi"),
            "durationHours":      total_hrs,
            "progressPercentage": progress_pct,
            "remainingHours":     remaining_hrs,
            "lastAccessed":       e.get("enrolledDate", ""),
            "status":             status_label,
        })

    return {"status": "success", "enrollments": enrollments}


@app.get("/api/v1/learner/{user_id}/recommendations")
async def get_recommendations_by_user_id(
    user_id: str,
    current_user: UserAuth = Depends(get_current_user),
):
    """
    Level-gated hybrid recommendations:
      Stage 0 — gap prioritisation (priority_k = gap_k * target_k/5) on the
                resolved levels shared with /skill-gaps
      Stage 1 — FRAC-tag + level filter (current < courseLevel <= target)
      Stage 2 — dense + BM25, RRF fusion, NSSTA 1.25× boost
      Stage 3 — final = 0.6*relevance + 0.4*quality (Bayesian-shrunk rating, log-pop)
    UNASSESSED competencies are not ranked as gaps ("no evidence" is not
    "level 0"); they are returned under `needsDiagnostic` instead.
    """
    from fastapi import HTTPException
    from services.baseline_assembler import enrollment_course_id

    _ensure_can_view(user_id, current_user)
    if _rec_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Recommendation engine is not available. Check startup logs.",
        )

    state = await _learner_competency_state(user_id)
    rows = state["competencies"]
    enrolled_ids = {enrollment_course_id(e) for e in state["enrollments"]} - {""}

    needs_diagnostic = [
        {"competencyId": r["competencyId"], "competencyName": r["name"]}
        for r in rows if r["currentLevel"] is None
    ]
    gaps = _rec_engine.calculate_gaps(
        baselines  = {r["competencyId"]: float(r["currentLevel"])
                      for r in rows if r["currentLevel"] is not None},
        targets    = {r["competencyId"]: float(r["targetLevel"]) for r in rows},
        names      = {r["competencyId"]: r["name"] for r in rows},
        confidence = {r["competencyId"]: r["confidence"] for r in rows},
        catalogue_ids = {r["competencyId"]: r["catalogueId"] for r in rows if r["catalogueId"]},
    )

    if not gaps:
        return {
            "status": "success",
            "officialId": user_id,
            "message": "No skill gaps detected. Keep learning!",
            "skillGaps": [],
            "recommendations": [],
            "needsDiagnostic": needs_diagnostic,
        }

    recs = _rec_engine.get_recommendations(
        gaps=gaps,
        limit_per_gap=3,
        enrolled_ids=enrolled_ids,
    )

    # Shape response — map to what api.ts fetchRecommendations expects
    skill_gaps_payload = [
        {
            "competencyId":   g.competencyId,
            "competencyName": g.competencyName,
            "currentLevel":   g.currentLevel,
            "targetLevel":    g.targetLevel,
            "gapScore":       g.gapScore,
            "priorityScore":  g.priorityScore,
            "confidence":     g.confidence,
        }
        for g in gaps
    ]

    recommendations_payload = [
        {
            "courseId":       r.courseId,
            "title":          r.title,
            "provider":       r.provider,
            "durationHours":  r.durationHours,
            "matchReason":    r.matchReasons[0] if r.matchReasons else "",
            "tags":           r.matchReasons,
            "finalScore":     r.finalScore,
            "relevanceScore": r.relevanceScore,
            "qualityScore":   r.qualityScore,
            "isTpac":         r.isTpac,
            "competencyId":   r.competencyId,
            "competencyName": r.competencyName,
            "priorityRank":   r.priorityRank,
            "matchReasons":   r.matchReasons,
            "matchType":      r.matchType,     # "frac_tag" | "semantic_fallback"
            "tpacSource":     r.tpacSource,    # "verified" | "inferred" | "none"
            "courseLevel":    r.courseLevel,   # FRAC level the course is tagged at
            "tagSupported":   r.tagSupported,  # False → tag flagged for review
        }
        for r in recs
    ]

    return {
        "status":          "success",
        "officialId":      user_id,
        "skillGaps":       skill_gaps_payload,
        "recommendations": recommendations_payload,
        "needsDiagnostic": needs_diagnostic,
    }


@app.get("/api/v1/learner/{user_id}/pathway")
async def get_learning_pathway(
    user_id: str,
    competencyId: str | None = None,
    budgetHours: float | None = Query(default=None, gt=0),
    unbudgeted: bool = False,
    current_user: UserAuth = Depends(get_current_user),
):
    """
    Step-by-step learning paths. For every role competency: one course per
    FRAC level from the official's current level up to the target, lowest
    level first ("first this course, then that one"), with a diagnostic step
    first when the level is unassessed, inferred or self-reported. Plus one
    study plan ordering the rungs of all paths by priority-weighted levels
    gained per hour, never breaking a ladder's level order.

    ?competencyId=… returns only that competency's path (and a plan for it).
    ?budgetHours=… caps the plan; ladders that don't fit are listed under
    studyPlan.deferred. Without it the plan is THIS QUARTER's plan: the budget
    is the official's ACBP learning hours per quarter and classroom hours are
    capped (CLASSROOM_CAP_HOURS_PER_QUARTER). ?unbudgeted=true plans everything.
    APAR-linked mandatory ACBP courses are always included first (SCIL v6 §5).
    """
    from fastapi import HTTPException
    from services.baseline_assembler import enrollment_course_id, is_completed

    _ensure_can_view(user_id, current_user)
    if _rec_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Recommendation engine is not available. Check startup logs.",
        )

    state = await _learner_competency_state(user_id)
    rows = state["competencies"]
    if competencyId:
        rows = [r for r in rows if r["competencyId"] == competencyId]
        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"Competency '{competencyId}' is not part of this official's role profile.",
            )

    enrollments   = state["enrollments"]
    completed_ids = {enrollment_course_id(e) for e in enrollments if is_completed(e)} - {""}
    in_progress   = {
        enrollment_course_id(e): float(e.get("completionPercentage") or 0)
        for e in enrollments
        if enrollment_course_id(e) and not is_completed(e)
    }

    pathways = [
        _rec_engine.build_pathway(
            comp_id        = r["catalogueId"] or r["competencyId"],
            role_comp_id   = r["competencyId"],
            crosswalk      = r["crosswalk"],
            comp_name      = r["name"],
            current_level  = r["currentLevel"],
            target_level   = r["targetLevel"],
            confidence     = r["confidence"],
            basis          = r["basis"],
            evidence_level = r["evidenceLevel"],
            completed_ids  = completed_ids,
            in_progress    = in_progress,
        )
        for r in rows
    ]
    for p, r in zip(pathways, rows):
        p["opportunity"] = r["opportunity"]

    # ACBP (SCIL v6 §5): mandatory courses + this official's learning hours per quarter.
    try:
        cbplan = await adapter.fetch_user_cbplan(user_id)
    except Exception:
        cbplan = None
    mandatory = (cbplan or {}).get("mandatoryCourses") or []
    quarter_hours = (cbplan or {}).get("learningHoursPerQuarter")
    if unbudgeted:
        budget, budget_source, classroom_cap = None, "none", None
    elif budgetHours is not None:
        budget, budget_source, classroom_cap = budgetHours, "query", None
    elif quarter_hours:
        budget, budget_source = float(quarter_hours), "quarterly_hours"
        classroom_cap = CLASSROOM_CAP_HOURS_PER_QUARTER
    else:
        budget, budget_source, classroom_cap = None, "none", None

    # Cross-competency prerequisites (SCIL v6 §5): the official's current level per
    # catalogue competency (None = UNASSESSED → advisory only) and, per step, the
    # expert edges it depends on so the UI can say "needs X Level N first".
    current_levels = {(r["catalogueId"] or r["competencyId"]): r["currentLevel"]
                      for r in state["competencies"]}
    frac_names = {c: m.get("name", c) for c, m in _rec_engine._frac_map.items()}

    mandatory_ids = {m["courseId"] for m in mandatory}
    for p in pathways:
        for s in p["steps"]:
            s["mandatory"] = bool(s.get("course") and s["course"]["courseId"] in mandatory_ids)
            if s["kind"] in ("course", "continue", "stretch", "bridge"):
                s["prerequisites"] = prerequisite_service.step_prerequisites(
                    _ref.prerequisites, p["catalogueCompetencyId"], s["covers"], current_levels, frac_names)

    study_plan = _rec_engine.build_study_plan(
        pathways, budget_hours=budget, mandatory=mandatory if not competencyId else [],
        completed_ids=completed_ids, in_progress=in_progress, classroom_cap_hours=classroom_cap,
        prerequisites=_ref.prerequisites, current_levels=current_levels,
    )
    study_plan["budgetSource"] = budget_source            # quarterly_hours | query | none
    study_plan["learningHoursPerQuarter"] = quarter_hours
    study_plan["acbpCycle"] = (cbplan or {}).get("cycle")
    pathways.sort(key=lambda p: (p["status"] == "met", -p["priorityScore"]))

    return {
        "status":     "success",
        "officialId": user_id,
        "pathways":   pathways,
        "studyPlan":  study_plan,
    }


@app.get("/api/v1/learner/{user_id}/achievements")
async def get_achievements_by_user_id(
    user_id: str,
    _current_user: UserAuth = Depends(get_current_user),
):
    """Completed courses (status=2) treated as achievements."""
    raw_enrollments = await adapter.fetch_user_enrollments(user_id)
    achievements = []
    for i, e in enumerate(raw_enrollments):
        if e.get("status") == 2:
            certs = e.get("issuedCertificates") or []
            achievements.append({
                "id":       certs[0].get("identifier", f"ACH-{i:03d}") if certs else f"ACH-{i:03d}",
                "title":    e.get("courseName", ""),
                "score":    int(e.get("completionPercentage", 100)),
                "date":     e.get("enrolledDate", ""),
                "category": "iGOT Course" if not certs else "Certificate",
            })
    return {"status": "success", "achievements": achievements}


# ─────────────────────────────────────────────────────────────────────────────
# LEARNER ENDPOINTS — legacy by govId (kept for backward compat)
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/v1/admin/users")
async def get_admin_roster(
    _current_user: UserAuth = Depends(require_role("admin")),
):
    """
    Admin Roster: proxies the mock iGOT server's /api/admin/v1/users endpoint.

    Enforces: authenticated + admin role.
    The frontend admin dashboard calls this endpoint (port 8000), NOT the mock
    server directly, keeping the backend as the single auth enforcement point.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{_IGOT_BASE}/api/admin/v1/users",
            headers={"x-authenticated-user-token": _IGOT_TOKEN},
            timeout=15.0,
        )
        resp.raise_for_status()

    # Unwrap the Sunbird envelope — return result.users directly
    data = resp.json()
    return data.get("result", {})


@app.get("/api/v1/admin/frac/competencies")
async def get_frac_competencies(
    _current_user: UserAuth = Depends(require_role("admin")),
):
    """
    FRAC Competency Dictionary: proxies the mock iGOT server's
    /api/frac/competencies endpoint.

    Enforces: authenticated + admin role.
    Returns the unwrapped list: { count, competencies }
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{_IGOT_BASE}/api/frac/competencies",
            headers={"x-authenticated-user-token": _IGOT_TOKEN},
            timeout=15.0,
        )
        resp.raise_for_status()

    data = resp.json()
    return data.get("result", {})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)