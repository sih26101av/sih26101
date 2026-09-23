"""
Gyan on the admin console: routers/admin_chat.py end to end, with the roster,
the DB and both intent classifiers stubbed.

    pytest tests/test_admin_chat.py
"""
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ai import semantic_engine
from auth.dependencies import get_current_user
from auth.models import UserAuth
from models.models import Base
from routers import admin_chat, admin_console
from services import admin_analytics as aa
from services import app_state


def _u(i, dept, first, last, done=0, status=2):
    return aa.normalise({
        "userId": f"usr_{i}", "govId": f"EMP-{i}", "firstName": first, "lastName": last,
        "email": f"{first}.{last}@mospi.gov.in".lower(), "department": dept, "designation": "Deputy Director",
        "grade": "TIER3_MID", "officeId": "off_x", "officeName": "CSO Delhi", "enrollmentStatus": status,
        "competencies": [], "completedCourseIds": ["do_a"] if done else [],
        "mandatory": {"cycle": "FY2026-27", "total": 2, "completed": done,
                      "pending": [] if done else [{"courseId": "do_m", "title": "Price Statistics"}]},
    })


ROSTER = [
    _u(1, "National Accounts", "Shikha", "Thakur", done=2),
    _u(2, "National Accounts", "Ramesh", "Sharma", status=0),
    _u(3, "Price Statistics", "Pooja", "Sharma", status=0),
]


@pytest.fixture()
def client(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    monkeypatch.setattr(admin_console, "SessionLocal", sessionmaker(bind=engine))

    async def roster(force=False):
        return ROSTER
    monkeypatch.setattr(admin_console, "_roster", roster)
    monkeypatch.setattr(app_state, "engine", SimpleNamespace(_frac_map={}))
    monkeypatch.setattr(app_state, "snapshot", {})

    app = FastAPI()
    app.include_router(admin_chat.router)
    app.dependency_overrides[get_current_user] = lambda: UserAuth(username="admin", role="admin")
    return TestClient(app)


def stub_intents(monkeypatch, admin=("general", 0.0), general=("general", 0.0)):
    """Both classifiers answer fixed (intent, confidence) pairs — no embedder."""
    monkeypatch.setattr(semantic_engine.ADMIN_INDEX, "classify", lambda q, lang: admin)
    monkeypatch.setattr(semantic_engine, "classify_intent", lambda q, lang=None: general)
    monkeypatch.setattr(semantic_engine, "low_confidence_threshold", lambda: 0.5)


def ask(client, message, **body):
    r = client.post("/api/v1/admin/console/chat", json={"message": message, **body})
    assert r.status_code == 200, r.text
    return r.json()


# ── Identity lookup runs before everything else ───────────────────────────────

def test_user_id_in_the_message_answers_with_that_officials_brief(client, monkeypatch):
    stub_intents(monkeypatch)
    out = ask(client, "usr_1")
    assert out["intent"] == "admin_user_lookup"
    assert "Shikha Thakur" in out["reply"] and "EMP-1" in out["reply"]
    assert "National Accounts" in out["reply"]


def test_named_official_beats_the_out_of_scope_intercept(monkeypatch, client):
    # "tell me about <person>" is the exact shape chatbot._OUT_OF_SCOPE_RE refuses.
    stub_intents(monkeypatch)
    out = ask(client, "tell me about Ramesh Sharma")
    assert out["intent"] == "admin_user_lookup"
    assert "Ramesh Sharma" in out["reply"]


def test_a_shared_surname_asks_which_official(client, monkeypatch):
    stub_intents(monkeypatch)
    out = ask(client, "details of Sharma")
    assert "Ramesh Sharma" in out["reply"] and "Pooja Sharma" in out["reply"]


def test_unknown_name_is_reported_as_not_found(client, monkeypatch):
    stub_intents(monkeypatch, admin=("admin_user_lookup", 0.9))
    out = ask(client, "tell me about Nobody Here")
    assert "nobody here" in out["reply"].lower()


# ── Admin tier ────────────────────────────────────────────────────────────────

def test_overview_reports_the_console_numbers(client, monkeypatch):
    stub_intents(monkeypatch, admin=("admin_overview", 0.95))
    out = ask(client, "give me an overview")
    assert out["engine"] == "semantic-admin"
    assert "3" in out["reply"]                       # three officials on the stub roster


def test_a_department_named_in_the_message_scopes_the_answer(client, monkeypatch):
    stub_intents(monkeypatch, admin=("admin_officials", 0.95))
    out = ask(client, "how many officials in National Accounts")
    assert "National Accounts" in out["reply"]
    assert "**Officials:** 2" in out["reply"]


def test_the_filter_bar_scopes_the_answer_when_the_message_does_not(client, monkeypatch):
    stub_intents(monkeypatch, admin=("admin_officials", 0.95))
    out = ask(client, "how many officials", filters={"department": "Price Statistics"})
    assert "**Officials:** 1" in out["reply"]


def test_needs_training_lists_officials_with_no_completed_course(client, monkeypatch):
    stub_intents(monkeypatch, admin=("admin_needs_training", 0.95))
    out = ask(client, "who needs training")
    assert "Ramesh Sharma" in out["reply"] and "Pooja Sharma" in out["reply"]


def test_navigation_returns_an_admin_tab_action(client, monkeypatch):
    stub_intents(monkeypatch, admin=("navigation_admin_emerging", 0.95))
    out = ask(client, "open emerging skills")
    assert out["navigate_action"] == {"type": "tab", "target": "emerging", "label": "Emerging Skills"}


def test_learner_dashboard_navigation_redirects_out_of_the_console(client, monkeypatch):
    stub_intents(monkeypatch, admin=("navigation_learner_dashboard", 0.95))
    out = ask(client, "open the learner dashboard")
    assert out["navigate_action"]["type"] == "redirect"
    assert out["navigate_action"]["target"] == "/dashboard"


# ── Everything Gyan already knew still works ──────────────────────────────────

def test_general_intents_fall_through_to_the_learner_catalogue(client, monkeypatch):
    stub_intents(monkeypatch, admin=("admin_overview", 0.55), general=("statistics_gdp", 0.95))
    out = ask(client, "explain GDP calculation")
    assert out["engine"] == "semantic" and out["intent"] == "statistics_gdp"
    assert "GDP" in out["reply"]


def test_theme_commands_are_intercepted_exactly_as_on_the_learner_widget(client, monkeypatch):
    stub_intents(monkeypatch)
    out = ask(client, "switch to dark mode")
    assert out["navigate_action"] == {"type": "theme", "target": "dark", "label": "Dark Mode"}


def test_the_language_picker_reaches_the_reply(client, monkeypatch):
    stub_intents(monkeypatch, admin=("admin_overview", 0.95))
    out = ask(client, "overview", preferred_language="hi")
    assert out["detected_language"] == "hi"
    assert "अधिकारी" in out["reply"]


def test_an_unrecognised_question_offers_the_admin_capabilities(client, monkeypatch):
    stub_intents(monkeypatch)
    out = ask(client, "zzzz qqqq")
    assert out["intent"] == "admin_capabilities"


def test_non_admins_are_refused(client, monkeypatch):
    stub_intents(monkeypatch)
    client.app.dependency_overrides[get_current_user] = lambda: UserAuth(username="u", role="official")
    assert client.post("/api/v1/admin/console/chat", json={"message": "overview"}).status_code == 403


def test_learner_intents_that_mean_nothing_for_an_admin_are_remapped(client, monkeypatch):
    # An admin has no skill gaps of their own; the console answer is the
    # workforce's shortages.
    stub_intents(monkeypatch, general=("skill_gaps", 0.95))
    assert ask(client, "what are my skill gaps")["intent"] == "admin_shortages"
    stub_intents(monkeypatch, general=("greeting", 0.99))
    assert ask(client, "hello")["intent"] == "admin_capabilities"


def test_suppressed_counts_print_their_display_string_not_the_cell():
    from services.chat_messages import admin as admin_msg

    rows = [{"competency": "Survey Design", "gap": 62.0,
             "officials": {"value": None, "suppressed": True, "display": "<5"}}]
    reply = admin_msg.shortages(rows, {}, "en")
    assert "<5 officials" in reply and "suppressed" not in reply
