"""
Admin console write actions end to end on an in-memory SQLite DB, with the
roster and catalogue stubbed: assign a training plan to a department, nudge
officials behind on mandatory training (with the 24 h cooldown), the learner's
view of both, and CSV export.

    pytest tests/test_admin_console_api.py
"""
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from auth.dependencies import get_current_user
from auth.models import UserAuth
from models.models import Base
from routers import admin_console
from services import admin_analytics as aa
from services import app_state


def _u(i, dept, done=0):
    return aa.normalise({
        "userId": f"usr_{i}", "govId": f"EMP-{i}", "firstName": f"F{i}", "lastName": "L", "department": dept,
        "grade": "TIER3_MID", "officeId": "off_x", "enrollmentStatus": 2, "competencies": [],
        "completedCourseIds": ["do_a"] if done else [],
        "mandatory": {"cycle": "FY", "total": 1, "completed": done,
                      "pending": [] if done else [{"courseId": "do_m", "title": "Mandatory"}]},
    })


@pytest.fixture()
def client(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    monkeypatch.setattr(admin_console, "SessionLocal", sessionmaker(bind=engine))
    rows = [_u(1, "NAD"), _u(2, "NAD", done=1), _u(3, "PSD")]

    async def roster(force=False):
        return rows
    monkeypatch.setattr(admin_console, "_roster", roster)
    doc = SimpleNamespace(identifier="do_a", name="Course A", duration_hrs=2.0, comp_ids=["comp_x"])
    monkeypatch.setattr(app_state, "engine", SimpleNamespace(_frac_map={"comp_x": {"name": "X"}}, _catalog=[doc]))

    app = FastAPI()
    app.include_router(admin_console.router)
    app.include_router(admin_console.learner_router)
    who = {"user": UserAuth(username="admin", role="admin")}
    app.dependency_overrides[get_current_user] = lambda: who["user"]
    c = TestClient(app)
    c.who = who
    return c


def test_assign_plan_to_department_tracks_progress(client):
    r = client.post("/api/v1/admin/console/assignments", json={
        "title": "NAD refresher", "scope": "department", "department": "NAD", "courseIds": ["do_a"],
        "dueDate": "2026-12-31"})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["assignees"] == 2 and body["progress"]["completedAll"] == 1 and body["progress"]["completionPct"] == 50
    assert client.get("/api/v1/admin/console/assignments").json()["assignments"][0]["title"] == "NAD refresher"
    bad = client.post("/api/v1/admin/console/assignments", json={
        "title": "x plan", "scope": "department", "department": "NAD", "courseIds": ["do_missing"]})
    assert bad.status_code == 422


def test_nudge_only_officials_behind_and_respect_cooldown(client):
    r = client.post("/api/v1/admin/console/nudges", json={"department": "NAD"})
    assert r.status_code == 201 and r.json()["sent"] == 1           # usr_2 has completed its mandatory course
    again = client.post("/api/v1/admin/console/nudges", json={"userIds": ["usr_1", "usr_2"]}).json()
    assert again["sent"] == 0
    reasons = {s["userId"]: s["reason"] for s in again["skipped"]}
    assert "already nudged" in reasons["usr_1"] and "not behind" in reasons["usr_2"]
    behind = client.get("/api/v1/admin/console/mandatory-behind?department=NAD").json()
    assert behind["total"] == 1 and behind["items"][0]["lastNudgedAt"]
    log = client.get("/api/v1/admin/console/nudges").json()["nudges"]
    assert [n["userId"] for n in log] == ["usr_1"] and log[0]["createdBy"] == "admin"

    client.who["user"] = UserAuth(username="usr_1", role="learner")
    mine = client.get("/api/v1/learner/usr_1/training-actions").json()
    assert mine["unread"] == 1 and mine["nudges"][0]["pendingCourses"][0]["courseId"] == "do_m"
    nid = mine["nudges"][0]["nudgeId"]
    assert client.post(f"/api/v1/learner/usr_1/nudges/{nid}/read").status_code == 200
    assert client.get("/api/v1/learner/usr_1/training-actions").json()["unread"] == 0
    assert client.get("/api/v1/learner/usr_3/training-actions").status_code == 403
    assert client.get("/api/v1/admin/console/overview").status_code == 403


def test_daily_snapshot_upserts_and_trends_filter(client):
    assert client.post("/api/v1/admin/console/trends/snapshot").status_code == 200
    assert client.post("/api/v1/admin/console/trends/snapshot").status_code == 200    # same day → upsert
    t = client.get("/api/v1/admin/console/trends").json()
    assert len(t["points"]) == 91 and t["liveSnapshots"] == 1         # 90 days back-filled + today
    today = t["points"][-1]
    assert today["reconstructed"] is False and today["officials"] == 3 and today["suppressed"]
    assert all(p["reconstructed"] for p in t["points"][:-1])
    csv = client.get("/api/v1/admin/console/export/roster.csv?department=NAD")
    assert csv.status_code == 200 and csv.headers["content-type"].startswith("text/csv")
    assert csv.text.count("\n") == 3                                  # header + 2 NAD officials
