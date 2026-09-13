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
from services.recommendation_service import HybridRecommendationEngine
from fastapi import Depends, FastAPI
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



@app.on_event("startup")
async def _startup():
    """Create users_auth table and karma tables if they don't exist yet."""
    global _rec_engine, _assembler
    AuthBase.metadata.create_all(bind=engine)
    # Create karma tables (KarmaEvent, KarmaMonthlyUsage) in the same auth.db
    from models.models import Base as DomainBase
    DomainBase.metadata.create_all(bind=engine)

    try:
        _rec_engine = HybridRecommendationEngine()
        import logging
        logging.getLogger(__name__).info("[startup] HybridRecommendationEngine ready.")

        # Build course → [comp_id, ...] map by inverting the rec engine's comp_index
        # _comp_index: {comp_id → [catalog_idx, ...]}
        # We need:      {course_id → [comp_id, ...]}
        course_comp_map: dict[str, list[str]] = {}
        for comp_id, cat_indices in _rec_engine._comp_index.items():
            for idx in cat_indices:
                course_id = _rec_engine._catalog[idx].identifier
                course_comp_map.setdefault(course_id, []).append(comp_id)

        _assembler = BaselineAssembler(course_comp_map)
        logging.getLogger(__name__).info(
            "[startup] BaselineAssembler ready. Mapped %d courses.", len(course_comp_map)
        )

    except Exception as exc:
        import logging
        logging.getLogger(__name__).error(
            "[startup] Engine/Assembler failed to initialise: %s", exc
        )
        _rec_engine = None
        _assembler  = None





# ── Register routers ───────────────────────────────────────────────────────────
app.include_router(auth_router,    prefix="/auth",       tags=["auth"])
app.include_router(chatbot_router, prefix="/api/v1",     tags=["chatbot"])
app.include_router(rag_router,     prefix="/api/v1/rag", tags=["rag"])
app.include_router(ai_tools_router,prefix="/api/v1/ai",  tags=["ai-tools"])
app.include_router(karma_router,   prefix="/api/v1",     tags=["karma"])
app.include_router(competency.router)
    
    



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
    _current_user: UserAuth = Depends(get_current_user),
):
    """
    Skill-gap analysis using the locked 6-term baseline formula:

      core_k = 0.45·Verified + 0.15·Documented + 0.20·Tenure
             + 0.10·SelfReport + 0.05·Education + 0.05·Seniority

      b_k = clamp(core_k + synergy_k, 0, InferredCeiling_k)

    Evidence sources:
      Verified    — iGOT/NSSTA enrollment completions (via adapter)
      Documented  — uploaded certificate rows (EvidenceLog DB)
      Tenure      — career history from user profile (role-relevant, decayed)
      SelfReport  — EvidenceLog SELF_REPORT rows (0 if not provided)
      Education   — degree relevance to competency type
      Seniority   — designation tier (only for Generic/Behavioural; 0 for Domain/Technical)

    Confidence tags (HIGH/MEDIUM/LOW) determine how fast scores can move
    on new evidence and whether a diagnostic quiz is offered.
    """
    from fastapi import HTTPException

    # ── FRAC type → frontend CompetencyDomain ─────────────────────────────
    _DOMAIN_MAP: dict[str, str] = {
        "Domain":      "Statistical",
        "Functional":  "Governance",
        "Behavioural": "Leadership",
        "Technical":   "Technical",
        "COMPETENCY":  "Statistical",
    }

    # 1. Fetch user profile
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

    prof_list = (user.get("profileDetails") or {}).get("professionalDetails") or [{}]
    prof      = prof_list[0] if prof_list else {}

    # 2. Fetch enrollments (needed for Verified term + exclusion filter in recs)
    try:
        enrollments = await adapter.fetch_user_enrollments(user_id)
    except Exception:
        enrollments = []

    # 3. Fetch DB EvidenceLog rows for this user (Documented / SelfReport rows)
    from auth.database import get_db
    from models.models import EvidenceLog
    db_session = next(get_db())
    try:
        db_rows = db_session.query(EvidenceLog).filter(
            EvidenceLog.userId == user_id
        ).all()
        db_evidence = [
            {
                "comp_id":       row.compId,
                "evidence_type": row.evidenceType,
                "granted_value": row.grantedValue,
                "issue_date":    row.issueDate,
            }
            for row in db_rows
        ]
    except Exception:
        db_evidence = []
    finally:
        db_session.close()

    # 4. Run the 6-term baseline formula via BaselineAssembler
    #    Falls back to simple heuristic if assembler not ready (startup failed)
    _DOMAIN_MAP_FRAC = _DOMAIN_MAP   # alias for closure below

    if _assembler is not None:
        baseline_results = _assembler.compute_for_user(
            user=user,
            enrollments=enrollments,
            db_evidence=db_evidence,
        )
    else:
        # Fallback heuristic (should never happen in normal operation)
        baseline_results = {}

    # 5. Build skill gap list from role competencies + computed baselines
    raw_comps = user.get("competencies") or \
                (user.get("profileDetails") or {}).get("competencies") or []
    seen_ids: set = set()
    unique_comps = []
    for c in raw_comps:
        cid = c.get("id", "")
        if cid and cid not in seen_ids:
            seen_ids.add(cid)
            unique_comps.append(c)

    # Track names already added — if two comps share the same name but different IDs
    # (mock data artifact), suffix the ID so the UI shows them as distinct
    name_counts: dict[str, int] = {}
    for comp in unique_comps:
        n = comp.get("name", "").strip()
        name_counts[n] = name_counts.get(n, 0) + 1

    skill_gaps = []
    for comp in unique_comps:
        cid          = comp.get("id", "")
        frac_type    = comp.get("type", "Functional")
        domain       = _DOMAIN_MAP_FRAC.get(frac_type, "Governance")
        target_level = int(comp.get("requiredLevel") or 3)
        base_name    = comp.get("name", "").strip()

        # Disambiguate duplicate display names by appending the comp ID
        skill_name = base_name if name_counts.get(base_name, 1) == 1 \
                     else f"{base_name} ({cid})"

        # Get baseline result from assembler (or fallback to 0)
        bline         = baseline_results.get(cid, {})
        current_level = int(bline.get("currentLevel", 0))
        confidence    = bline.get("confidence", "LOW")
        raw_score     = float(bline.get("score", 0.0))
        evidence      = bline.get("_evidence", {})

        gap = max(0, target_level - current_level)

        skill_gaps.append({
            "competencyId": cid,
            "skillName":    skill_name,
            "domain":       domain,
            "currentLevel": current_level,
            "targetLevel":  target_level,
            "gapScore":     gap,
            "confidence":   confidence,       # HIGH | MEDIUM | LOW
            "rawScore":     round(raw_score, 3),  # b_k ∈ [0, 5]
            "evidence":     evidence,              # per-term breakdown
        })



    # Sort by gap desc, then by rawScore asc (biggest gaps with lowest scores first)
    skill_gaps.sort(key=lambda g: (-g["gapScore"], g["rawScore"]))

    total_courses     = len(enrollments)
    completed_courses = sum(1 for e in enrollments if (e.get("completionPercentage") or 0) >= 100)

    return {
        "userId":           user_id,
        "govId":            user.get("govId", user_id),
        "jobRole":          prof.get("designation", "Official"),
        "department":       prof.get("department", "MoSPI"),
        "totalCourses":     total_courses,
        "completedCourses": completed_courses,
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
        done_nodes   = int(leaf * progress_pct / 100) if progress_pct else e.get("progress", 0)
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
    _current_user: UserAuth = Depends(get_current_user),
):
    """
    3-Stage Hybrid Recommendation Engine:
      Stage 0 — Cross-gap prioritization (priority_k = gap_k * target_k/5)
      Stage 1 — Mandatory FRAC-tag filtering (no untagged courses)
      Stage 2 — Dense FAISS + Sparse BM25 + RRF fusion + NSSTA 1.25× boost
      Stage 3 — final = 0.6*relevance + 0.4*quality (Wilson rating, log-pop)
    """
    from fastapi import HTTPException

    if _rec_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Recommendation engine is not available. Check startup logs.",
        )

    # 1. Fetch user profile to derive competency baselines
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

    # 2. Get enrollments (needed for Verified term + enrolled_ids exclusion filter)
    try:
        enrolled_raw = await adapter.fetch_user_enrollments(user_id)
    except Exception:
        enrolled_raw = []

    enrolled_ids = {e.get("courseId", "") for e in enrolled_raw}

    # 3. Fetch DB EvidenceLog rows (same as skill-gaps endpoint)
    from auth.database import get_db
    from models.models import EvidenceLog
    db_session = next(get_db())
    try:
        db_rows = db_session.query(EvidenceLog).filter(
            EvidenceLog.userId == user_id
        ).all()
        db_evidence = [
            {
                "comp_id":       row.compId,
                "evidence_type": row.evidenceType,
                "granted_value": row.grantedValue,
                "issue_date":    row.issueDate,
            }
            for row in db_rows
        ]
    except Exception:
        db_evidence = []
    finally:
        db_session.close()

    # 4. Run 6-term assembler to get b_k for every competency (same formula as skill-gaps)
    if _assembler is not None:
        baseline_results = _assembler.compute_for_user(
            user=user, enrollments=enrolled_raw, db_evidence=db_evidence
        )
    else:
        baseline_results = {}

    # Build baselines + targets for the rec engine (uses b_k from assembler)
    raw_comps = user.get("competencies") or \
                (user.get("profileDetails") or {}).get("competencies") or []
    seen_ids: set = set()
    unique_comps = []
    for c in raw_comps:
        cid = c.get("id", "")
        if cid and cid not in seen_ids:
            seen_ids.add(cid); unique_comps.append(c)

    baselines: dict[str, float] = {}
    targets:   dict[str, float] = {}
    for comp in unique_comps:
        cid = comp.get("id", "")
        if cid:
            bline = baseline_results.get(cid, {})
            baselines[cid] = float(bline.get("score", 0.0))   # raw b_k score [0,5]
            targets[cid]   = float(int(comp.get("requiredLevel") or 3))

    # 5. Inject comp names into rec engine's frac_map so GapEntry.competencyName is readable
    for comp in unique_comps:
        cid  = comp.get("id", "")
        name = comp.get("name", "").strip()
        if cid and name and cid not in _rec_engine._frac_map:
            _rec_engine._frac_map[cid] = {
                "name":        name,
                "description": name,
                "type":        comp.get("type", "Functional"),
            }

    # 6. Compute prioritised gaps (Stage 0)
    gaps = _rec_engine.calculate_gaps(baselines, targets)

    if not gaps:
        return {
            "status": "success",
            "officialId": user_id,
            "message": "No skill gaps detected. Keep learning!",
            "skillGaps": [],
            "recommendations": [],
            }


    # 4. Run hybrid search + scoring (Stages 1-3)
    recs = _rec_engine.get_recommendations(
        gaps=gaps,
        limit_per_gap=3,
        enrolled_ids=enrolled_ids,
    )

    # 5. Shape response — map to what api.ts fetchRecommendations expects
    skill_gaps_payload = [
        {
            "competencyId":   g.competencyId,
            "competencyName": g.competencyName,
            "currentLevel":   g.currentLevel,
            "targetLevel":    g.targetLevel,
            "gapScore":       g.gapScore,
            "priorityScore":  g.priorityScore,
        }
        for g in gaps
    ]

    recommendations_payload = [
        {
            "courseId":       r.courseId,
            "title":          r.title,
            "provider":       r.provider,
            "durationHours":  r.durationHours,
            "finalScore":     r.finalScore,
            "relevanceScore": r.relevanceScore,
            "qualityScore":   r.qualityScore,
            "isTpac":         r.isTpac,
            "competencyId":   r.competencyId,
            "competencyName": r.competencyName,
            "priorityRank":   r.priorityRank,
            "matchReasons":   r.matchReasons,
            # Legacy alias consumed by older api.ts mapper
            "matchReason":    r.matchReasons[0] if r.matchReasons else "",
            "tags":           [r.competencyName],
        }
        for r in recs
    ]

    return {
        "status":          "success",
        "officialId":      user_id,
        "skillGaps":       skill_gaps_payload,
        "recommendations": recommendations_payload,
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