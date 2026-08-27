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
from routers.rag import router as rag_router
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
@app.on_event("startup")
async def _startup():
    """Create users_auth table if it doesn't exist yet."""
    AuthBase.metadata.create_all(bind=engine)


# ── Register routers ───────────────────────────────────────────────────────────
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(chatbot_router, prefix="/api/v1", tags=["chatbot"])
app.include_router(rag_router, prefix="/api/v1/rag", tags=["rag"])


# ── iGOT Adapter singleton (HTTP → mock_igot_server.py on port 8001) ────────────
# Data only flows when the Sunbird-compliant mock server is running.
# Run: cd mock-igot-server && uvicorn mock_igot_server:app --reload --port 8001
adapter = MockIgotAdapter()

# ── iGOT mock server config (kept for admin proxy endpoint) ────────────────────
_IGOT_BASE = os.getenv("IGOT_MOCK_BASE_URL", "http://localhost:8001")
_IGOT_TOKEN = os.getenv("IGOT_MOCK_TOKEN", "mock-api-key-2026")

# ── Role-level requirements for Deputy Director, National Accounts Division ────
ROLE_REQUIREMENTS = {
    "C-001": {"skillName": "National Accounts Framework (SNA 2008)", "domain": "Statistical", "targetLevel": 4},
    "C-002": {"skillName": "Survey Methodology",                      "domain": "Statistical", "targetLevel": 4},
    "C-003": {"skillName": "Price Statistics & CPI Construction",     "domain": "Statistical", "targetLevel": 3},
    "C-004": {"skillName": "Data Analysis with Python & R",           "domain": "Technical",   "targetLevel": 4},
    "C-005": {"skillName": "Machine Learning for Statistics",          "domain": "Technical",   "targetLevel": 3},
}

# ── Static achievement log (keyed by govId) ────────────────────────────────────
ACHIEVEMENTS_BY_USER: dict[str, list] = {
    "EMP-8472": [
        {"id": "ACH-001", "title": "National Accounts Framework (SNA 2008)", "score": 88, "date": "2025-10-13T10:00:00Z", "category": "External Certification"},
        {"id": "ACH-002", "title": "Survey Methodology & Sampling Techniques", "score": 94, "date": "2025-11-20T14:30:00Z", "category": "RAG Quiz"},
    ]
}


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
        current_level = _level_to_int(comp.get("competencyLevel", "Level 2"))
        target_level  = 4
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
    """AI-ranked course recommendations personalised by skill gap."""
    user    = await adapter.fetch_user_by_id(user_id)
    catalog = await adapter.fetch_catalog()

    # Build gap map from profile competencies
    competencies = (user.get("profileDetails") or {}).get("competencies") or [] if user else []
    enrolled_ids = {e.get("courseId") for e in await adapter.fetch_user_enrollments(user_id)}

    gaps: dict[str, dict] = {}
    for comp in competencies:
        current = _level_to_int(comp.get("competencyLevel", "Level 2"))
        gaps[comp.get("name", "")] = {"current": current, "gap": max(0, 4 - current)}

    recommendations = []
    for course in catalog:
        if course.get("identifier") in enrolled_ids:
            continue  # skip already enrolled courses
        for skill in (course.get("competencies_v3") and [] or []):  # safe fallback
            pass
        # Match against user gap map via course name / description keywords
        # Primary: use course competency tag fields if available
        comp_tags = []
        raw_v3 = course.get("competencies_v3", "")
        if raw_v3:
            try:
                comp_tags = json.loads(raw_v3) if isinstance(raw_v3, str) else raw_v3
            except Exception:
                pass

        best_gap = 0
        match_skill = ""
        match_reason = ""
        for tag in comp_tags:
            name = tag.get("name", "") if isinstance(tag, dict) else ""
            gap_info = gaps.get(name)
            if gap_info and gap_info["gap"] > best_gap:
                best_gap = gap_info["gap"]
                match_skill = name
                match_reason = f"Bridges your gap in {name}."

        if not match_skill:
            # Fallback: recommend courses whose primaryCategory matches any gap skill
            cat = course.get("primaryCategory", "")
            for skill_name, gap_info in gaps.items():
                if gap_info["gap"] > 0 and (skill_name.lower() in cat.lower() or cat.lower() in skill_name.lower()):
                    match_skill = skill_name
                    match_reason = f"Recommended for your role."
                    best_gap = gap_info["gap"]
                    break

        if not match_skill and gaps:
            # Last resort: include top courses anyway with a generic reason
            match_reason = "Recommended for MoSPI officials."

        duration_sec = course.get("duration", "0")
        try:
            duration_hrs = round(int(duration_sec) / 3600, 1) if duration_sec else 0
        except (ValueError, TypeError):
            duration_hrs = round((course.get("leafNodesCount") or 10) * 0.5, 1)

        recommendations.append({
            "courseId":     course.get("identifier", ""),
            "title":        course.get("name", ""),
            "provider":     course.get("source", course.get("channel", "iGOT Karmayogi")),
            "durationHours": duration_hrs,
            "matchReason":  match_reason,
            "tags":         [match_skill] if match_skill else [],
            "gapScore":     best_gap,
        })

    # Sort by gap score descending, limit to top 8
    recommendations.sort(key=lambda r: r["gapScore"], reverse=True)
    return {"status": "success", "recommendations": recommendations[:8]}


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