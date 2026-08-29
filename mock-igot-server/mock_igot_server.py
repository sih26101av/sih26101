"""
mock_igot_server.py — High-Fidelity iGOT Karmayogi / Sunbird Mock Server
=========================================================================
Loads authentic dataset files (courses.json, competencies.json,
jobprofiles.json) into memory once at startup and exposes
Sunbird-compliant REST endpoints on Port 8001.

Architecture:
  * Data is loaded into in-memory stores at startup (lifespan) — no
    file-system reads on hot paths.
  * Every response is wrapped in the standard Sunbird envelope.
  * x-authenticated-user-token header is enforced on all protected routes.
  * Telemetry endpoint validates v3.1 payloads and de-duplicates by mid.
  * Content-state endpoint merges live in-memory state with seed snapshots.
  * Legacy /api/external/igot/* endpoints maintained for MockIgotAdapter
    compatibility (ICatalogSync / IScorePublisher per ARCHITECTURE.md).

Data Sources (root-level JSON files — authentic datasets):
  * courses.json       — 8 848 real iGOT courses (identifier, name,
                         description, duration_seconds, ...)
  * competencies.json  — FRAC competency dictionary (competency_id, name,
                         category, description)
  * jobprofiles.json   — NCO job roles (position_id, nco_code, title,
                         is_public_sector_role)

Usage:
  pip install fastapi uvicorn
  python mock_igot_server.py
"""

from __future__ import annotations

import json
import os
import random
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Optional

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

# ─────────────────────────────────────────────────────────────
# App bootstrap
# ─────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────
# Path helpers
# ─────────────────────────────────────────────────────────────

ROOT_DIR = os.path.dirname(__file__)


def _load_json(filename: str) -> Any:
    """Load a JSON file from ROOT_DIR. Raises RuntimeError on missing file."""
    path = os.path.join(ROOT_DIR, filename)
    if not os.path.exists(path):
        raise RuntimeError(f"Required dataset file {filename!r} not found in {ROOT_DIR}.")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _load_json_from_dir(directory: str, filename: str) -> Any:
    path = os.path.join(directory, filename)
    if not os.path.exists(path):
        raise RuntimeError(f"{filename!r} not found in {directory}.")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ─────────────────────────────────────────────────────────────
# In-Memory stores — populated once at startup via lifespan
# ─────────────────────────────────────────────────────────────

# Primary authentic datasets (root-level JSON files)
DB_COURSES: list[dict] = []          # courses.json      — 8 848 courses
DB_COMPETENCIES: list[dict] = []     # competencies.json — FRAC dictionary
DB_JOB_PROFILES: list[dict] = []     # jobprofiles.json  — NCO job roles

# Legacy seed data for user / enrolment / content-state lookups
DB_USERS: list[dict] = []
DB_ENROLLMENTS: list[dict] = []
DB_CONTENT_STATES: dict[str, dict] = {}

# O(1) course lookup index: identifier → course dict (built at startup)
_COURSE_INDEX: dict[str, dict] = {}

# Runtime stores (grow during the server's lifetime)
TELEMETRY_STORE: list[dict] = []         # incoming telemetry events
SEEN_MIDS: set[str] = set()              # for deduplication
SCORE_PUSH_LOG: list[dict] = []          # synced scores from LMS
ENROLL_MUTATIONS: dict[str, list] = {}   # userId → newly enrolled records


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load all datasets into memory once at startup.
    courses.json is large (~27 MB / 8 848 records) — loading it here avoids
    repeated file-system I/O on every API request.
    """
    global DB_COURSES, DB_COMPETENCIES, DB_JOB_PROFILES
    global DB_USERS, DB_ENROLLMENTS, DB_CONTENT_STATES, _COURSE_INDEX

    # ── Authentic datasets (new primary sources) ────────────────────────────
    print("[STARTUP] Loading courses.json …", flush=True)
    raw_courses = _load_json("courses.json")
    
    # Filter to ensure we only load courses with English titles
    DB_COURSES = []
    for c in raw_courses:
        name = c.get("name") or ""
        ascii_cnt = sum(1 for ch in name if ord(ch) < 128)
        if (ascii_cnt / max(len(name), 1)) > 0.8:
            DB_COURSES.append(c)

    print("[STARTUP] Loading competencies.json …", flush=True)
    DB_COMPETENCIES = _load_json("competencies.json")

    print("[STARTUP] Loading jobprofiles.json …", flush=True)
    DB_JOB_PROFILES = _load_json("jobprofiles.json")

    # Build fast O(1) lookup index keyed by course identifier
    _COURSE_INDEX = {c["identifier"]: c for c in DB_COURSES if c.get("identifier")}

    # ── Legacy seed data (users / enrolments / content-states) ─────────────
    data_dir = os.path.join(ROOT_DIR, "data")
    try:
        DB_USERS = _load_json_from_dir(data_dir, "users.json")
        DB_ENROLLMENTS = _load_json_from_dir(data_dir, "enrollments.json")
        DB_CONTENT_STATES = _load_json_from_dir(data_dir, "content_states.json")
        print(
            f"[STARTUP] Loaded {len(DB_USERS)} users, "
            f"{len(DB_ENROLLMENTS)} enrolments, "
            f"{len(DB_CONTENT_STATES)} content-state snapshots.",
            flush=True,
        )
    except RuntimeError as exc:
        print(f"[WARN] Legacy seed data not found: {exc}", flush=True)

    print(
        f"[STARTUP] [OK] {len(DB_COURSES)} courses | "
        f"{len(DB_COMPETENCIES)} competencies | "
        f"{len(DB_JOB_PROFILES)} job profiles loaded into memory.",
        flush=True,
    )
    yield  # server is running
    print("[SHUTDOWN] Mock iGOT server shutting down.", flush=True)



# ─────────────────────────────────────────────────────────────
# App bootstrap (lifespan replaces deprecated @app.on_event)
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Mock iGOT Karmayogi API (Sunbird-Compliant)",
    description=(
        "High-fidelity standalone mock server for the MoSPI SIH Prototype. "
        "Serves authentic iGOT datasets from in-memory stores."
    ),
    version="4.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
# Sunbird Envelope factory
# ─────────────────────────────────────────────────────────────


def _ts_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S:%f")[:-3] + "+0000"

def sunbird_ok(api_id: str, ver: str, result: dict) -> dict:
    return {
        "id": api_id,
        "ver": ver,
        "ts": _ts_now(),
        "params": {
            "resmsgid": str(uuid.uuid4()),
            "msgid": str(uuid.uuid4()),
            "err": None,
            "status": "successful",
            "errmsg": None,
        },
        "responseCode": "OK",
        "result": result,
    }

def sunbird_err(api_id: str, ver: str, status_code: int, err_code: str, msg: str) -> JSONResponse:
    body = {
        "id": api_id,
        "ver": ver,
        "ts": _ts_now(),
        "params": {
            "resmsgid": str(uuid.uuid4()),
            "msgid": None,
            "err": err_code,
            "status": "failed",
            "errmsg": msg,
        },
        "responseCode": "BAD_REQUEST" if status_code == 400 else
                        "UNAUTHORIZED"        if status_code == 401 else
                        "RESOURCE_NOT_FOUND"  if status_code == 404 else
                        "INTERNAL_SERVER_ERROR",
        "result": {},
    }
    return JSONResponse(status_code=status_code, content=body)


# ─────────────────────────────────────────────────────────────
# Auth guard helper
# ─────────────────────────────────────────────────────────────

def _require_auth(token: str | None, api_id: str, ver: str) -> None:
    """Raises a JSONResponse (as HTTPException detail) when token is absent."""
    if not token:
        raise HTTPException(
            status_code=401,
            detail=sunbird_err(api_id, ver, 401, "ERR_UNAUTHORIZED",
                               "Mandatory header 'x-authenticated-user-token' is missing.").body.decode(),
        )


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _user_by_id(user_id: str) -> dict | None:
    return next((u for u in DB_USERS if u.get("userId") == user_id), None)

def _course_by_id(course_id: str) -> dict | None:
    """O(1) lookup via pre-built _COURSE_INDEX."""
    return _COURSE_INDEX.get(course_id)

def _user_enrolments(user_id: str) -> list[dict]:
    """Merge seed enrolments with any runtime mutations."""
    base = [e for e in DB_ENROLLMENTS if e.get("userId") == user_id]
    return base + ENROLL_MUTATIONS.get(user_id, [])


# ─────────────────────────────────────────────────────────────
# ① GET /api/content/read   — Course Catalog
# ─────────────────────────────────────────────────────────────

@app.get("/api/content/read")
async def get_course_catalog(
    request: Request,
    x_authenticated_user_token: str | None = Header(default=None),
):
    API_ID, VER = "api.content.read", "3.0"
    _require_auth(x_authenticated_user_token, API_ID, VER)

    # Honour optional ?identifier= query param to return a single course
    identifier = request.query_params.get("identifier")
    if identifier:
        course = _course_by_id(identifier)
        if not course:
            return sunbird_err(API_ID, VER, 404, "ERR_CONTENT_NOT_FOUND",
                               f"Content '{identifier}' not found.")
        return sunbird_ok(API_ID, VER, {"content": course})

    # Pagination — DB_COURSES is large (8 848 records); use ?limit= & ?offset=
    try:
        limit  = int(request.query_params.get("limit", 100))
        offset = int(request.query_params.get("offset", 0))
    except ValueError:
        limit, offset = 100, 0

    page = DB_COURSES[offset: offset + limit]
    return sunbird_ok(API_ID, VER, {
        "count": len(DB_COURSES),
        "content": page,
    })


# ─────────────────────────────────────────────────────────────
# ② GET /api/user/v2/read/{user_id}   — User Profile
# ─────────────────────────────────────────────────────────────

@app.get("/api/user/v2/read/{user_id}")
async def get_user_profile(
    user_id: str,
    x_authenticated_user_token: str | None = Header(default=None),
):
    API_ID, VER = "api.user.read", "v2"
    _require_auth(x_authenticated_user_token, API_ID, VER)

    user = _user_by_id(user_id)
    if not user:
        return sunbird_err(API_ID, VER, 404, "ERR_USER_NOT_FOUND",
                           f"User '{user_id}' does not exist.")

    return sunbird_ok(API_ID, VER, {"response": user})


# ─────────────────────────────────────────────────────────────
# ③ GET /api/course/v1/user/enrollment/list/{user_id}
# ─────────────────────────────────────────────────────────────

@app.get("/api/course/v1/user/enrollment/list/{user_id}")
async def get_user_enrolments(
    user_id: str,
    request: Request,
    x_authenticated_user_token: str | None = Header(default=None),
):
    API_ID, VER = "api.course.getuserenrolment", "v1"
    _require_auth(x_authenticated_user_token, API_ID, VER)

    user = _user_by_id(user_id)
    if not user:
        return sunbird_err(API_ID, VER, 404, "ERR_USER_NOT_FOUND",
                           f"User '{user_id}' does not exist.")

    enrolments = _user_enrolments(user_id)

    # Optional: enrich with course metadata if 'fields' param requested
    fields_param = request.query_params.get("fields", "")
    requested_fields = {f.strip() for f in fields_param.split(",") if f.strip()}

    enriched = []
    for enrol in enrolments:
        record = dict(enrol)
        if requested_fields:
            course = _course_by_id(enrol["courseId"])
            if course:
                for field in requested_fields:
                    if field in course:
                        record[field] = course[field]
        enriched.append(record)

    return sunbird_ok(API_ID, VER, {"courses": enriched})



# ─────────────────────────────────────────────────────────────
# Pydantic Models — updated to match authentic JSON schemas
# ─────────────────────────────────────────────────────────────

class CourseOut(BaseModel):
    """Mirrors the authentic courses.json schema."""
    identifier: str
    name: str
    description: Optional[str] = None
    duration_seconds: Optional[int] = None
    duration_formatted: Optional[str] = None
    organisation: Optional[str] = None
    source: Optional[str] = None
    primaryCategory: Optional[str] = None
    contentType: Optional[str] = None
    appIcon: Optional[str] = None
    posterImage: Optional[str] = None
    competencies_v3: Optional[list[dict]] = None
    model_config = {"populate_by_name": True}


class CompetencyOut(BaseModel):
    """Mirrors the authentic competencies.json schema."""
    competency_id: str
    name: str
    category: Optional[str] = None
    description: Optional[str] = None


class JobProfileOut(BaseModel):
    """Mirrors the authentic jobprofiles.json schema."""
    position_id: str
    nco_code: Optional[str] = None
    title: str
    description: Optional[str] = None
    is_public_sector_role: Optional[bool] = None


class ContentStateRequest(BaseModel):

    request: dict

    @field_validator("request")
    @classmethod
    def _check_required_keys(cls, v: dict) -> dict:
        for key in ("userId", "courseId", "batchId"):
            if key not in v:
                raise ValueError(f"Missing required field in request: '{key}'")
        return v


@app.post("/api/course/v1/content/state/read")
async def get_content_state(
    body: ContentStateRequest,
    x_authenticated_user_token: str | None = Header(default=None),
):
    API_ID, VER = "api.content.state.read", "v1"
    _require_auth(x_authenticated_user_token, API_ID, VER)

    req     = body.request
    user_id = req["userId"]
    cid     = req["courseId"]
    bid     = req["batchId"]
    key     = f"{user_id}|{cid}|{bid}"

    state = DB_CONTENT_STATES.get(key)
    if not state:
        # Return empty contentList rather than 404 — mirrors Sunbird behaviour
        return sunbird_ok(API_ID, VER, {
            "contentList": [],
            "lastReadContentId": None,
            "completionPercentage": 0,
            "courseId": cid,
            "batchId": bid,
        })

    return sunbird_ok(API_ID, VER, state)


# ─────────────────────────────────────────────────────────────
# ⑤ POST /v1/telemetry
#    Validates v3.0 / v3.1 event batches with mid deduplication
# ─────────────────────────────────────────────────────────────

VALID_EIDS = {
    "START", "END", "IMPRESSION", "INTERACT", "ASSESS",
    "RESPONSE", "INTERRUPT", "FEEDBACK", "INDEX", "ERROR",
    "HEARTBEAT", "LOG", "SEARCH", "METRICS", "SUMMARY",
    "EXDATA", "AUDIT",
}

VALID_TELEMETRY_VERSIONS = {"3.0", "3.1"}


class TelemetryBatch(BaseModel):
    id:     str
    ver:    str
    ts:     str
    events: list[dict]

    @field_validator("ver")
    @classmethod
    def _ver_check(cls, v: str) -> str:
        if v not in VALID_TELEMETRY_VERSIONS:
            raise ValueError(f"Unsupported telemetry version: '{v}'. Must be 3.0 or 3.1")
        return v

    @field_validator("events")
    @classmethod
    def _events_not_empty(cls, v: list) -> list:
        if not v:
            raise ValueError("'events' array must not be empty.")
        return v


def _validate_event(event: dict) -> list[str]:
    """Returns a list of validation errors for a single telemetry event."""
    errors: list[str] = []
    mid = event.get("mid")

    if not event.get("eid") or event["eid"] not in VALID_EIDS:
        errors.append(f"Invalid or missing 'eid'. Got: {event.get('eid')!r}")
    if not isinstance(event.get("ets"), (int, float)):
        errors.append("'ets' must be a numeric epoch timestamp in milliseconds.")
    if not event.get("ver") or event["ver"] not in VALID_TELEMETRY_VERSIONS:
        errors.append(f"Invalid 'ver': {event.get('ver')!r}. Must be '3.0' or '3.1'.")
    if not mid:
        errors.append("'mid' (message ID) is required.")

    actor = event.get("actor", {})
    if not actor.get("id"):
        errors.append("actor.id is required.")
    if not actor.get("type"):
        errors.append("actor.type is required.")

    context = event.get("context", {})
    if not context.get("channel"):
        errors.append("context.channel is required.")
    if not context.get("env"):
        errors.append("context.env is required.")

    obj = event.get("object", {})
    if not obj.get("id"):
        errors.append("object.id is required.")
    if not obj.get("type"):
        errors.append("object.type is required.")

    return errors


@app.post("/v1/telemetry", status_code=200)
async def ingest_telemetry(
    batch: TelemetryBatch,
    x_authenticated_user_token: str | None = Header(default=None),
):
    API_ID, VER = "api.telemetry", "3.1"
    _require_auth(x_authenticated_user_token, API_ID, VER)

    accepted  = 0
    skipped   = 0
    rejected  = 0
    errors_log: list[dict] = []

    for event in batch.events:
        mid = event.get("mid")

        # Deduplication
        if mid and mid in SEEN_MIDS:
            skipped += 1
            continue

        # Schema validation
        errs = _validate_event(event)
        if errs:
            rejected += 1
            errors_log.append({"mid": mid, "errors": errs})
            continue

        # Accept
        TELEMETRY_STORE.append(event)
        if mid:
            SEEN_MIDS.add(mid)
        accepted += 1

    return sunbird_ok(API_ID, VER, {
        "message": "Telemetry batch processed.",
        "accepted": accepted,
        "skipped_duplicates": skipped,
        "rejected_invalid": rejected,
        "total_in_store": len(TELEMETRY_STORE),
        "validation_errors": errors_log if errors_log else None,
    })


# ─────────────────────────────────────────────────────────────
# Legacy /api/external/igot/* endpoints
# Consumed by MockIgotPlatformAdapter (ICatalogSync / IScorePublisher)
# in main-lms-backend — must remain backward-compatible.
# ─────────────────────────────────────────────────────────────

class ScorePayload(BaseModel):
    competency_id: str
    new_level: int
    score_percentage: float
    passed: bool
    evaluated_at: str
    source: str


class EnrolPayload(BaseModel):
    igot_course_id: str
    enrolled_at: str


@app.get("/api/external/igot/catalog")
async def legacy_catalog():
    """
    ICatalogSync.fetchCourses() — returns the full course list.
    Now served from in-memory DB_COURSES (authentic courses.json data).
    """
    return {"status": "success", "count": len(DB_COURSES), "data": DB_COURSES}


@app.get("/api/external/igot/frac")
async def legacy_frac():
    """
    ICatalogSync — returns the FRAC competency dictionary.
    Served from in-memory DB_COMPETENCIES (authentic competencies.json).
    """
    return {"status": "success", "count": len(DB_COMPETENCIES), "data": DB_COMPETENCIES}


@app.get("/api/external/igot/job-profiles")
async def legacy_job_profiles():
    """NCO job profiles from authentic jobprofiles.json."""
    return {"status": "success", "count": len(DB_JOB_PROFILES), "data": DB_JOB_PROFILES}


@app.get("/api/external/igot/users/{user_id}/history")
async def legacy_user_history(user_id: str):
    """ICatalogSync.fetchUserHistory() — consumed by MockIgotPlatformAdapter."""
    simplified = []
    for e in _user_enrolments(user_id):
        status_str = (
            "COMPLETED"   if e.get("status") == 2 else
            "IN_PROGRESS" if e.get("status") == 1 else
            "NOT_STARTED"
        )
        simplified.append({
            "igot_course_id":      e.get("courseId", ""),
            "course_title":        e.get("courseName", ""),
            "status":              status_str,
            "progress_percentage": e.get("completionPercentage", 0),
            "remaining_minutes":   0,
            "last_accessed_at":    e.get("enrolledDate", ""),
        })
    return {"status": "success", "data": simplified}




@app.post("/api/external/igot/users/{user_id}/score", status_code=201)
async def legacy_push_score(user_id: str, payload: ScorePayload):
    SCORE_PUSH_LOG.append({"userId": user_id, **payload.model_dump()})
    return {"status": "success", "message": "Score synced to iGOT."}


@app.post("/competencies/update", status_code=200)
async def update_competency_from_rag(
    payload: dict,
    x_authenticated_user_token: str | None = Header(default=None),
):
    """Updates learner competency level after passing a RAG assessment quiz."""
    SCORE_PUSH_LOG.append(payload)
    return {
        "status": "success",
        "message": "Competency record successfully updated on iGOT Karmayogi.",
        "syncedData": payload,
    }


@app.post("/api/external/igot/users/{user_id}/enroll", status_code=201)
async def legacy_enroll_user(user_id: str, payload: EnrolPayload):
    course = _course_by_id(payload.igot_course_id)
    if not course:
        return JSONResponse(status_code=404, content={"status": "error", "message": "Course not found."})

    new_record = {
        "active": True,
        "courseId": course["identifier"],
        "courseName": course["name"],
        "contentId": course["identifier"],
        "batchId": "batch_" + course["identifier"][3:] + "_01",
        "userId": user_id,
        "enrolledDate": payload.enrolled_at,
        "status": 0,
        "completionPercentage": 0,
        "progress": 0,
        "leafNodesCount": course["leafNodesCount"],
        "lastReadContentId": "",
        "lastReadContentStatus": 0,
        "issuedCertificates": [],
        "channel": course.get("channel", "igot-mdo-mospi-01"),
    }
    ENROLL_MUTATIONS.setdefault(user_id, []).append(new_record)
    return {"status": "success", "message": "User enrolled on iGOT."}


# ─────────────────────────────────────────────────────────────
# Health / introspection endpoints
# ─────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────
# ⑥ GET /api/admin/v1/users   — Admin Roster (all users)
# ─────────────────────────────────────────────────────────────

@app.get("/api/admin/v1/users")
async def get_admin_roster(
    x_authenticated_user_token: str | None = Header(default=None),
):
    API_ID, VER = "api.admin.users.list", "v1"
    _require_auth(x_authenticated_user_token, API_ID, VER)

    enriched = []
    for user in DB_USERS:
        user_id = user["userId"]
        enrolments = _user_enrolments(user_id)

        # Derive enrollment status: 2=completed, 1=in-progress, 0=none
        if any(e["status"] == 2 for e in enrolments):
            enroll_status = 2
        elif any(e["status"] == 1 for e in enrolments):
            enroll_status = 1
        else:
            enroll_status = 0

        # Find the most recent PLANNED or IN_PROGRESS competency as the "missing skill"
        comps = user.get("profileDetails", {}).get("competencies", [])
        missing = next(
            (c["name"] for c in comps if c.get("status") in ("PLANNED", "IN_PROGRESS")),
            None,
        )

        prof = user.get("profileDetails", {}).get("professionalDetails", [{}])[0]
        enriched.append({
            "userId":           user_id,
            "govId":            user.get("govId", user_id),
            "firstName":        user.get("firstName", ""),
            "lastName":         user.get("lastName", ""),
            "email":            user.get("email", ""),
            "designation":      prof.get("designation", "Official"),
            "department":       prof.get("department", "MoSPI"),
            "enrollmentStatus": enroll_status,
            "missingSkill":     missing,
            "competencies":     comps,
        })

    return sunbird_ok(API_ID, VER, {
        "count": len(enriched),
        "users": enriched,
    })


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "server": "Mock iGOT Karmayogi (Sunbird-Compliant) v4.0",
        "port": 8001,
        "data_loaded": {
            "courses":                 len(DB_COURSES),
            "competencies":            len(DB_COMPETENCIES),
            "job_profiles":            len(DB_JOB_PROFILES),
            "users":                   len(DB_USERS),
            "enrollments":             len(DB_ENROLLMENTS),
            "content_state_snapshots": len(DB_CONTENT_STATES),
        },
        "runtime": {
            "telemetry_events_ingested":   len(TELEMETRY_STORE),
            "score_pushes_received":       len(SCORE_PUSH_LOG),
            "runtime_enrolment_mutations": sum(len(v) for v in ENROLL_MUTATIONS.values()),
        }
    }


@app.get("/api/frac/competencies")
async def get_competencies(
    x_authenticated_user_token: str | None = Header(default=None),
):
    API_ID, VER = "api.frac.competencies.read", "v1"
    _require_auth(x_authenticated_user_token, API_ID, VER)
    return sunbird_ok(API_ID, VER, {
        "count": len(DB_COMPETENCIES),
        "competencies": DB_COMPETENCIES,
    })


@app.get("/api/job-profiles")
async def get_job_profiles(
    request: Request,
    x_authenticated_user_token: str | None = Header(default=None),
):
    """
    GET /api/job-profiles — NCO Job Role Catalogue (Sunbird-compliant).
    Served from in-memory DB_JOB_PROFILES (authentic jobprofiles.json).
    Supports ?public_sector_only=true, ?limit=, ?offset=.
    """
    API_ID, VER = "api.job.profiles.read", "v1"
    _require_auth(x_authenticated_user_token, API_ID, VER)

    public_only = request.query_params.get("public_sector_only", "").lower() == "true"
    profiles = (
        [p for p in DB_JOB_PROFILES if p.get("is_public_sector_role") is True]
        if public_only else DB_JOB_PROFILES
    )
    try:
        limit  = int(request.query_params.get("limit", 100))
        offset = int(request.query_params.get("offset", 0))
    except ValueError:
        limit, offset = 100, 0

    return sunbird_ok(API_ID, VER, {
        "count": len(profiles),
        "job_profiles": profiles[offset: offset + limit],
    })




# ─────────────────────────────────────────────────────────────
# Exception handler — ensure 401s from _require_auth
# keep Sunbird envelope format
# ─────────────────────────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exc_handler(request: Request, exc: HTTPException):
    # If detail is already a JSON-encoded Sunbird envelope, return it raw
    if isinstance(exc.detail, str):
        try:
            body = json.loads(exc.detail)
            return JSONResponse(status_code=exc.status_code, content=body)
        except (json.JSONDecodeError, TypeError):
            pass
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "id": "api.error",
            "ver": "v1",
            "ts": _ts_now(),
            "params": {"err": str(exc.status_code), "status": "failed", "errmsg": str(exc.detail)},
            "responseCode": "INTERNAL_SERVER_ERROR",
            "result": {},
        }
    )


if __name__ == "__main__":
    uvicorn.run("mock_igot_server:app", host="0.0.0.0", port=8001, reload=True)
