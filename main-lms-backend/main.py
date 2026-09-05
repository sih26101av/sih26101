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
from main import _rec_engine
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
_rec_engine: HybridRecommendationEngine | None = None


@app.on_event("startup")
async def _startup():
    """Create users_auth table and karma tables if they don't exist yet."""
    global _rec_engine
    AuthBase.metadata.create_all(bind=engine)
    # Create karma tables (KarmaEvent, KarmaMonthlyUsage) in the same auth.db
    from models.models import Base as DomainBase
    DomainBase.metadata.create_all(bind=engine)

    try:
        _rec_engine = HybridRecommendationEngine()
        import logging
        logging.getLogger(__name__).info("[startup] HybridRecommendationEngine ready.")

    except Exception as exc:
        import logging
        logging.getLogger(__name__).error(
            "[startup] RecommendationEngine failed to initialise: %s", exc
        )
        _rec_engine = None



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
    """Skill-gap analysis for a learner by their iGOT userId."""
    from fastapi import HTTPException
    user = await adapter.fetch_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")

    prof = (user.get("profileDetails") or {}).get("professionalDetails") or [{}]
    prof = prof[0] if prof else {}
    competencies = (user.get("profileDetails") or {}).get("competencies") or []

    skill_gaps = []
    for comp in competencies:
        current_level = _level_to_int(comp.get("competencyLevel", "Level 0"))  # Algo will calculate this later
        target_level  = comp.get("requiredLevel", 3)
        gap = max(0, target_level - current_level)
        skill_gaps.append({
            "competencyId": comp.get("id", ""),
            "skillName":    comp.get("name", ""),
            "domain":       comp.get("type", "Domain"),
            "currentLevel": current_level,
            "targetLevel":  target_level,
            "gapScore":     gap,
        })

    return {
        "userId":     user_id,
        "govId":      user.get("govId", user_id),
        "jobRole":    prof.get("designation", "Official"),
        "department": prof.get("department", "MoSPI"),
        "skillGaps":  skill_gaps,
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
    user = await adapter.fetch_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")

    competencies = (user.get("profileDetails") or {}).get("competencies") or []

    # Build baselines map: comp_id → current_level (float)
    baselines: dict[str, float] = {}
    for comp in competencies:
        cid = comp.get("id", "")
        if cid:
            baselines[cid] = float(_level_to_int(comp.get("competencyLevel", "Level 2")))

    # Build targets map: comp_id → target_level (from ROLE_REQUIREMENTS or default 4.0)
    # For each competency in the user's profile, set target to 4 unless overridden
    targets: dict[str, float] = {
        cid: 4.0 for cid in baselines
    }

    # 2. Get set of already-enrolled course IDs to exclude
    enrolled_raw  = await adapter.fetch_user_enrollments(user_id)
    enrolled_ids  = {e.get("courseId", "") for e in enrolled_raw}

    # 3. Compute prioritised gaps (Stage 0)
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