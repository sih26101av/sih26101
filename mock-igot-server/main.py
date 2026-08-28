"""
main.py — Simplified MoSPI Mock iGOT Endpoint Set
==================================================
A lightweight companion to mock_igot_server.py that exposes the same
legacy /api/external/igot/* routes for teams that run this file directly.

Data is loaded from authentic JSON files at startup (lifespan):
  • courses.json       — 8 848 real iGOT courses
  • competencies.json  — FRAC competency dictionary
  • jobprofiles.json   — NCO job roles

Usage:
  python main.py        # starts on port 8001
"""

from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from typing import Any, Optional

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

ROOT_DIR = os.path.dirname(__file__)


def _load_json(filename: str) -> Any:
    path = os.path.join(ROOT_DIR, filename)
    if not os.path.exists(path):
        raise RuntimeError(f"Required dataset file {filename!r} not found in {ROOT_DIR}.")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# In-Memory stores — populated once at startup
# ---------------------------------------------------------------------------

DB_COURSES: list[dict] = []
DB_COMPETENCIES: list[dict] = []
DB_JOB_PROFILES: list[dict] = []
_COURSE_INDEX: dict[str, dict] = {}

# Runtime write stores
MOCK_SCORES_DB: list[dict] = []
MOCK_ENROLLMENTS_DB: list[dict] = []
MOCK_USER_HISTORY: dict[str, list] = {
    "EMP-8472": [
        {"igot_course_id": "do_placeholder_1", "course_title": "National Accounts Statistics", "status": "COMPLETED", "progress_percentage": 100, "remaining_minutes": 0, "last_accessed_at": "2025-10-12T09:00:00Z"},
    ],
    "user123": [
        {"igot_course_id": "do_placeholder_2", "course_title": "Fundamentals of GFR 2017", "status": "COMPLETED", "progress_percentage": 100, "remaining_minutes": 0, "last_accessed_at": "2026-08-05T09:00:00Z"},
    ],
}


# ---------------------------------------------------------------------------
# Lifespan — load all datasets into memory once at startup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    global DB_COURSES, DB_COMPETENCIES, DB_JOB_PROFILES, _COURSE_INDEX

    print("[STARTUP] main.py — Loading courses.json …", flush=True)
    raw_courses = _load_json("courses.json")
    
    # Filter to ensure we only load courses with English titles
    DB_COURSES = []
    for c in raw_courses:
        name = c.get("name") or ""
        ascii_cnt = sum(1 for ch in name if ord(ch) < 128)
        if (ascii_cnt / max(len(name), 1)) > 0.8:
            DB_COURSES.append(c)

    print("[STARTUP] main.py — Loading competencies.json …", flush=True)
    DB_COMPETENCIES = _load_json("competencies.json")

    print("[STARTUP] main.py — Loading jobprofiles.json …", flush=True)
    DB_JOB_PROFILES = _load_json("jobprofiles.json")

    _COURSE_INDEX = {c["identifier"]: c for c in DB_COURSES if c.get("identifier")}

    print(
        f"[STARTUP] ✓ {len(DB_COURSES)} courses | "
        f"{len(DB_COMPETENCIES)} competencies | "
        f"{len(DB_JOB_PROFILES)} job profiles loaded.",
        flush=True,
    )
    yield
    print("[SHUTDOWN] main.py server shutting down.", flush=True)


# ---------------------------------------------------------------------------
# App bootstrap
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Mock iGOT Karmayogi API",
    description="Standalone mock server for SIH MoSPI Prototype",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/external/igot/catalog")
def get_catalog():
    """Returns the full authentic course catalog from courses.json."""
    return {"status": "success", "count": len(DB_COURSES), "data": DB_COURSES}


@app.get("/api/external/igot/frac")
def get_frac_dictionary():
    """Returns the FRAC competency dictionary from competencies.json."""
    return {"status": "success", "count": len(DB_COMPETENCIES), "data": DB_COMPETENCIES}


@app.get("/api/external/igot/job-profiles")
def get_job_profiles():
    """Returns NCO job profiles from jobprofiles.json."""
    return {"status": "success", "count": len(DB_JOB_PROFILES), "data": DB_JOB_PROFILES}


@app.get("/api/external/igot/users/{userId}/history")
def get_user_history(userId: str):
    history = MOCK_USER_HISTORY.get(userId, [])
    return {"status": "success", "data": history}


@app.post("/api/external/igot/users/{userId}/score", status_code=201)
def push_score(userId: str, payload: ScoreRequest):
    MOCK_SCORES_DB.append({"userId": userId, "score_data": payload.model_dump()})
    return {"status": "success", "message": "Score synced successfully to iGOT"}


@app.post("/competencies/update", status_code=200)
def update_competency(payload: dict):
    MOCK_SCORES_DB.append(payload)
    return {
        "status": "success",
        "message": "Competency profile updated successfully on iGOT",
        "syncedData": payload,
    }


@app.post("/api/external/igot/users/{userId}/enroll", status_code=201)
def enroll_user(userId: str, payload: EnrollRequest):
    MOCK_ENROLLMENTS_DB.append({"userId": userId, "enrollment_data": payload.model_dump()})
    # O(1) lookup via pre-built index
    course_info = _COURSE_INDEX.get(payload.igot_course_id)
    if userId not in MOCK_USER_HISTORY:
        MOCK_USER_HISTORY[userId] = []
    if course_info:
        duration_mins = (course_info.get("duration_seconds") or 0) // 60
        MOCK_USER_HISTORY[userId].append({
            "igot_course_id":      course_info["identifier"],
            "course_title":        course_info.get("name", ""),
            "status":              "NOT_STARTED",
            "progress_percentage": 0,
            "remaining_minutes":   duration_mins,
            "last_accessed_at":    payload.enrolled_at,
        })
    return {"status": "success", "message": "User enrolled successfully on iGOT"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "server": "Mock iGOT Karmayogi API (main.py) v2.0",
        "port": 8001,
        "data_loaded": {
            "courses":      len(DB_COURSES),
            "competencies": len(DB_COMPETENCIES),
            "job_profiles": len(DB_JOB_PROFILES),
        },
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
