from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from adapters.igot_adapter import MockIgotAdapter
from models.domain import (
    SkillGapResponse, RecommendationResponse,
    EnrollmentsResponse, AchievementsResponse
)
import uvicorn

app = FastAPI(title="MoSPI LMS Backend API", description="Main Orchestrator Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

adapter = MockIgotAdapter()

# Role-level requirements for Deputy Director, National Accounts Division
ROLE_REQUIREMENTS = {
    "C-001": {"skillName": "National Accounts Framework (SNA 2008)", "domain": "Statistical", "targetLevel": 4},
    "C-002": {"skillName": "Survey Methodology",                      "domain": "Statistical", "targetLevel": 4},
    "C-003": {"skillName": "Data Privacy & Security",                  "domain": "Governance",  "targetLevel": 3},
    "C-004": {"skillName": "Data Visualization",                       "domain": "Technical",   "targetLevel": 3},
    "C-005": {"skillName": "Machine Learning for Statistics",          "domain": "Technical",   "targetLevel": 3},
}

# Static achievement log (driven by completed courses + assessments)
ACHIEVEMENTS_BY_USER = {
    "EMP-8472": [
        {"id": "ACH-001", "title": "National Accounts Framework (SNA 2008)", "score": 88, "date": "2025-10-13T10:00:00Z", "category": "External Certification"},
        {"id": "ACH-002", "title": "Sampling Methods in Surveys",             "score": 81, "date": "2026-08-16T14:00:00Z", "category": "RAG Quiz"},
    ]
}


@app.get("/api/v1/users/{gov_id}/skill-gaps", response_model=SkillGapResponse)
async def get_skill_gaps(gov_id: str):
    """
    Skill Gap Engine: dynamically computes competency gaps from iGOT history.
    """
    history = await adapter.fetch_user_history(gov_id)
    catalog = await adapter.fetch_catalog()

    current_levels = {comp_id: 1 for comp_id in ROLE_REQUIREMENTS}

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

    return {"officialId": gov_id, "jobRole": "Deputy Director", "department": "National Accounts Division", "skillGaps": skill_gaps}


@app.get("/api/v1/recommendations/{gov_id}", response_model=RecommendationResponse)
async def get_recommendations(gov_id: str):
    """
    Recommendation Engine: returns courses from iGOT catalog that bridge the user's active gaps.
    """
    catalog = await adapter.fetch_catalog()
    gaps_data = await get_skill_gaps(gov_id)
    gaps = gaps_data["skillGaps"]

    recommendations = []
    for course in catalog:
        for skill in course.get("skills_covered", []):
            gap_info = next((g for g in gaps if g["competencyId"] == skill["external_skill_id"] and g["gapScore"] > 0), None)
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
async def get_enrollments(gov_id: str):
    """
    Active Enrollments: returns IN_PROGRESS courses from iGOT history for the My Courses tab.
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
async def get_achievements(gov_id: str):
    """
    Achievements: returns the user's completed assessments and certifications.
    """
    achievements = ACHIEVEMENTS_BY_USER.get(gov_id, [])
    return {"status": "success", "achievements": achievements}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)