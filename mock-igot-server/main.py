from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Mock iGOT Karmayogi API", description="Standalone mock server for SIH MoSPI Prototype")

# Enable CORS for cross-origin requests from our main LMS and Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-Memory Dummy Data ---
# Courses (CBPs) mapped to FRAC competencies
MOCK_CATALOG = [
    {
        "igot_course_id": "CRS-IGOT-5521",
        "course_title": "National Accounts Statistics: SNA 2008 & GDP Estimation Methods",
        "provider_name": "iGOT Karmayogi",
        "duration_minutes": 2400,
        "skills_covered": [
            {
                "external_skill_id": "C-001",
                "skill_name": "National Accounts Framework (SNA 2008)",
                "proficiency_taught": 4
            }
        ]
    },
    {
        "igot_course_id": "CRS-IGOT-7734",
        "course_title": "Applied Machine Learning for Official Statistics",
        "provider_name": "iGOT Karmayogi",
        "duration_minutes": 2700,
        "skills_covered": [
            {
                "external_skill_id": "C-005",
                "skill_name": "Machine Learning for Statistics",
                "proficiency_taught": 3
            }
        ]
    },
    {
        "igot_course_id": "CRS-IGOT-8812",
        "course_title": "Survey Design and Sampling Methodologies",
        "provider_name": "iGOT Karmayogi",
        "duration_minutes": 1800,
        "skills_covered": [
            {
                "external_skill_id": "C-002",
                "skill_name": "Survey Methodology",
                "proficiency_taught": 4
            }
        ]
    },
    {
        "igot_course_id": "CRS-IGOT-9999",
        "course_title": "Data Privacy in Government",
        "provider_name": "iGOT Karmayogi",
        "duration_minutes": 900,
        "skills_covered": [
            {
                "external_skill_id": "C-003",
                "skill_name": "Data Privacy & Security",
                "proficiency_taught": 2
            }
        ]
    },
    {
        "igot_course_id": "CRS-IGOT-4422",
        "course_title": "Advanced Data Visualization with Python",
        "provider_name": "iGOT Karmayogi",
        "duration_minutes": 1200,
        "skills_covered": [
            {
                "external_skill_id": "C-004",
                "skill_name": "Data Visualization",
                "proficiency_taught": 3
            }
        ]
    }
]

# User Histories
MOCK_USER_HISTORY = {
    "user123": [
        {
            "igot_course_id": "CRS-IGOT-5521",
            "course_title": "National Accounts Statistics: SNA 2008 & GDP Estimation Methods",
            "status": "IN_PROGRESS",
            "progress_percentage": 65,
            "remaining_minutes": 840,
            "last_accessed_at": "2026-08-20T10:00:00Z"
        },
        {
            "igot_course_id": "CRS-IGOT-9999",
            "course_title": "Data Privacy in Government",
            "status": "COMPLETED",
            "progress_percentage": 100,
            "remaining_minutes": 0,
            "last_accessed_at": "2026-07-25T14:00:00Z"
        }
    ],
    "EMP-8472": [
        {
            "igot_course_id": "CRS-IGOT-5521",
            "course_title": "National Accounts Statistics: SNA 2008 & GDP Estimation Methods",
            "status": "COMPLETED",
            "progress_percentage": 100,
            "remaining_minutes": 0,
            "last_accessed_at": "2025-10-12T09:00:00Z"
        },
        {
            "igot_course_id": "CRS-IGOT-8812",
            "course_title": "Survey Design and Sampling Methodologies",
            "status": "IN_PROGRESS",
            "progress_percentage": 45,
            "remaining_minutes": 990,
            "last_accessed_at": "2026-08-15T11:30:00Z"
        }
    ]
}

# In-memory storage for incoming scores and enrollments to simulate saving state
MOCK_SCORES_DB = []
MOCK_ENROLLMENTS_DB = []

# --- Pydantic Models for Requests ---
class ScoreRequest(BaseModel):
    competency_id: str
    new_level: int
    score_percentage: float
    passed: bool
    evaluated_at: str
    source: str

class EnrollRequest(BaseModel):
    igot_course_id: str
    enrolled_at: str

# --- Endpoints ---

@app.get("/api/external/igot/catalog")
def get_catalog():
    """
    Catalog Sync (Read All Courses)
    """
    return {
        "status": "success",
        "data": MOCK_CATALOG
    }

@app.get("/api/external/igot/users/{userId}/history")
def get_user_history(userId: str):
    """
    Fetch User History (Read Enrollments)
    """
    # Return user history or empty list if user not found, 
    # to mimic reality where a new user has no history.
    history = MOCK_USER_HISTORY.get(userId, [])
    return {
        "status": "success",
        "data": history
    }

@app.post("/api/external/igot/users/{userId}/score", status_code=201)
def push_score(userId: str, payload: ScoreRequest):
    """
    Push Score (Write / Event Sink)
    """
    # Simulate saving the synced score to the government database
    MOCK_SCORES_DB.append({
        "userId": userId,
        "score_data": payload.model_dump()
    })
    return {"status": "success", "message": "Score synced successfully to iGOT"}

@app.post("/api/external/igot/users/{userId}/enroll", status_code=201)
def enroll_user(userId: str, payload: EnrollRequest):
    """
    Enroll User (Write)
    """
    MOCK_ENROLLMENTS_DB.append({
        "userId": userId,
        "enrollment_data": payload.model_dump()
    })
    
    if userId not in MOCK_USER_HISTORY:
        MOCK_USER_HISTORY[userId] = []
        
    course_info = next((c for c in MOCK_CATALOG if c["igot_course_id"] == payload.igot_course_id), None)
    if course_info:
        # Mocking an enrollment by pushing NOT_STARTED status into user's history
        MOCK_USER_HISTORY[userId].append({
            "igot_course_id": course_info["igot_course_id"],
            "course_title": course_info["course_title"],
            "status": "NOT_STARTED",
            "progress_percentage": 0,
            "remaining_minutes": course_info["duration_minutes"],
            "last_accessed_at": payload.enrolled_at
        })

    return {"status": "success", "message": "User enrolled successfully on iGOT"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
