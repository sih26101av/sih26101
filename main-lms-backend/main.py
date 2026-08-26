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
import httpx
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
@app.on_event("startup")
async def _startup():
    """Create users_auth table if it doesn't exist yet."""
    AuthBase.metadata.create_all(bind=engine)


# ── Register routers ───────────────────────────────────────────────────────────
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(chatbot_router, prefix="/api/v1", tags=["chatbot"])


# ── iGOT Adapter singleton ─────────────────────────────────────────────────────
adapter = MockIgotAdapter()

# ── iGOT mock server config (for admin proxy) ──────────────────────────────────
_IGOT_BASE = os.getenv("IGOT_MOCK_BASE_URL", "http://localhost:8001")
_IGOT_TOKEN = os.getenv("IGOT_MOCK_TOKEN", "mock-api-key-2026")

# ── Role-level requirements for Deputy Director, National Accounts Division ────
ROLE_REQUIREMENTS = {
    "C-001": {"skillName": "National Accounts Framework (SNA 2008)", "domain": "Statistical", "targetLevel": 4},
    "C-002": {"skillName": "Survey Methodology",                      "domain": "Statistical", "targetLevel": 4},
    "C-003": {"skillName": "Data Privacy & Security",                  "domain": "Governance",  "targetLevel": 3},
    "C-004": {"skillName": "Data Visualization",                       "domain": "Technical",   "targetLevel": 3},
    "C-005": {"skillName": "Machine Learning for Statistics",          "domain": "Technical",   "targetLevel": 3},
}

# ── Static achievement log ─────────────────────────────────────────────────────
ACHIEVEMENTS_BY_USER = {
    "EMP-8472": [
        {"id": "ACH-001", "title": "National Accounts Framework (SNA 2008)", "score": 88, "date": "2025-10-13T10:00:00Z", "category": "External Certification"},
        {"id": "ACH-002", "title": "Sampling Methods in Surveys",             "score": 81, "date": "2026-08-16T14:00:00Z", "category": "RAG Quiz"},
    ]
}


# ─────────────────────────────────────────────────────────────────────────────
# LEARNER ENDPOINTS (protected — requires any authenticated user)
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/v1/users/{gov_id}/skill-gaps", response_model=SkillGapResponse)
async def get_skill_gaps(
    gov_id: str,
    _current_user: UserAuth = Depends(get_current_user),
):
    """
    Skill Gap Engine: dynamically computes competency gaps from iGOT history.
    Protected — requires a valid JWT access token.
    """
    history = await adapter.fetch_user_history(gov_id)
    catalog = await adapter.fetch_catalog()

    current_levels = {
        "C-001": 1,
        "C-002": 3,
        "C-003": 2,
        "C-004": 2,
        "C-005": 1,
    }

    for enrollment in history:
        if enrollment.get("status") == "COMPLETED":
            course = next((c for c in catalog if c["igot_course_id"] == enrollment["igot_course_id"]), None)
            if course:
                for skill in course.get("skills_covered", []):
                    sid = skill["external_skill_id"]
                    if sid in current_levels:
                        current_levels[sid] = max(current_levels[sid], skill["proficiency_taught"])

    skill_gaps = [
        {
            "competencyId": cid,
            "skillName": req["skillName"],
            "domain": req["domain"],
            "currentLevel": current_levels[cid],
            "targetLevel": req["targetLevel"],
            "gapScore": max(0, req["targetLevel"] - current_levels[cid]),
        }
        for cid, req in ROLE_REQUIREMENTS.items()
    ]

    return {
        "officialId": gov_id,
        "jobRole": "Deputy Director",
        "department": "National Accounts Division",
        "skillGaps": skill_gaps,
    }


@app.get("/api/v1/recommendations/{gov_id}", response_model=RecommendationResponse)
async def get_recommendations(
    gov_id: str,
    _current_user: UserAuth = Depends(get_current_user),
):
    """
    Recommendation Engine: returns courses from iGOT catalog bridging the user's active gaps.
    Protected — requires a valid JWT access token.
    """
    catalog = await adapter.fetch_catalog()
    gaps_data = await get_skill_gaps(gov_id, _current_user)
    gaps = gaps_data["skillGaps"]

    recommendations = []
    for course in catalog:
        for skill in course.get("skills_covered", []):
            gap_info = next(
                (g for g in gaps if g["competencyId"] == skill["external_skill_id"] and g["gapScore"] > 0),
                None,
            )
            if gap_info and skill["proficiency_taught"] > gap_info["currentLevel"]:
                recommendations.append({
                    "courseId": course["igot_course_id"],
                    "title": course["course_title"],
                    "provider": course["provider_name"],
                    "durationHours": round(course["duration_minutes"] / 60.0, 1),
                    "matchReason": f"Directly addresses your {gap_info['gapScore']}-level gap in {gap_info['skillName']}.",
                    "tags": [gap_info["domain"], gap_info["skillName"]],
                })
                break

    return {"status": "success", "recommendations": recommendations}


@app.get("/api/v1/users/{gov_id}/enrollments", response_model=EnrollmentsResponse)
async def get_enrollments(
    gov_id: str,
    _current_user: UserAuth = Depends(get_current_user),
):
    """
    Active Enrollments: returns IN_PROGRESS courses from iGOT history.
    Protected — requires a valid JWT access token.
    """
    history = await adapter.fetch_user_history(gov_id)
    catalog = await adapter.fetch_catalog()

    enrollments = []
    for i, enrollment in enumerate(history):
        if enrollment.get("status") == "IN_PROGRESS":
            course = next((c for c in catalog if c["igot_course_id"] == enrollment["igot_course_id"]), None)
            total_hours = (course["duration_minutes"] / 60.0) if course else 0
            remaining_hours = round(enrollment.get("remaining_minutes", 0) / 60.0, 1)
            enrollments.append({
                "enrollmentId": f"ENR-{gov_id}-{i:03d}",
                "courseId": enrollment["igot_course_id"],
                "courseTitle": enrollment["course_title"],
                "provider": course["provider_name"] if course else "iGOT Karmayogi",
                "durationHours": round(total_hours, 1),
                "progressPercentage": enrollment.get("progress_percentage", 0),
                "remainingHours": remaining_hours,
                "lastAccessed": enrollment.get("last_accessed_at", ""),
                "status": enrollment.get("status", "IN_PROGRESS"),
            })

    return {"status": "success", "enrollments": enrollments}


@app.get("/api/v1/users/{gov_id}/achievements", response_model=AchievementsResponse)
async def get_achievements(
    gov_id: str,
    _current_user: UserAuth = Depends(get_current_user),
):
    """
    Achievements: returns completed assessments and certifications.
    Protected — requires a valid JWT access token.
    """
    achievements = ACHIEVEMENTS_BY_USER.get(gov_id, [])
    return {"status": "success", "achievements": achievements}


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN ENDPOINTS (protected — requires role=admin)
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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)