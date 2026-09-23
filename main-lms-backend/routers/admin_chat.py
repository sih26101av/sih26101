"""
routers/admin_chat.py — Gyan on the admin console

  POST /api/v1/admin/console/chat        admin-only; answers from live console data
  GET  /api/v1/admin/console/chat/mode   which tier is live (frontend badge)

This is the same assistant as `routers/chatbot.py`, given a second tier that can
read the admin console. The order of a request:

  1. Language variant          services.language_service.resolve_chat_variant
  2. Shared intercepts         chatbot._intercept — theme, language, "who am I",
                               login, out-of-scope. Identical behaviour to the
                               learner widget, so theme/language commands work here.
  3. Identity lookup           a usr_…, EMP-… or an email in the message resolves
                               straight to that official's brief, whatever the
                               classifier thinks.
  4. Admin intent              ai.semantic_engine.ADMIN_INDEX (its own corpus,
                               ai/intent_corpus_admin/) — KPIs, compliance, ACBP,
                               departments, shortages, emerging skills, trends,
                               health, nudges, plans, one official, navigation.
  5. Everything else           falls through to the learner pipeline
                               (classify_intent + chat_messages.render), so MoSPI,
                               FRAC, GDP/CPI, greetings and farewells still answer.

Whichever of the two classifiers scores higher wins; both run on the same
embedder and the same cosine scale, so the scores are comparable.

Data comes from routers/admin_console.py's cached roster and the same pure
aggregates the dashboard panels use — a chat answer and the panel beside it can
never disagree. Scope: a department / office / service tier named in the message
wins over the filter bar the admin has set; otherwise the request's `filters`
apply (services/admin_chat_data.resolve_scope).
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from auth.dependencies import require_role
from auth.models import UserAuth
from services import admin_analytics as aa
from services import admin_chat_data as facts
from services.chat_messages import admin as admin_msg
from services.chat_messages import render
from services.chat_messages.context import ReplyContext
from services.language_service import resolve_chat_variant, to_iso

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/admin/console", tags=["admin-console"])

TREND_DAYS = 90
TOP_ROWS = 5
# On this console an admin reading of a near-tie is the better bet: "take me to
# the learner dashboard" scores 0.945 admin against 0.948 for the learner
# corpus's own `navigation_dashboard`, and the admin answer is the right one.
# Kept small — "hello" and "what is GDP" lose by far more than this.
ADMIN_MARGIN = 0.02


# ── Request / response ────────────────────────────────────────────────────────

class ChatHistoryItem(BaseModel):
    role: str            # "user" | "model"
    content: str


class AdminChatFilters(BaseModel):
    department: Optional[str] = None
    grade: Optional[str] = None
    office: Optional[str] = None


class AdminChatRequest(BaseModel):
    message: str
    history: List[ChatHistoryItem] = []
    preferred_language: Optional[str] = None
    # The dashboard's filter bar, so "what is the compliance" answers about
    # whatever the admin is currently looking at.
    filters: Optional[AdminChatFilters] = None
    full_name: Optional[str] = None
    job_role: Optional[str] = "System Administrator"
    department: Optional[str] = "MoSPI"


class AdminChatResponse(BaseModel):
    reply: str
    detected_language: str
    engine: str = "template"                  # "semantic-admin" | "semantic" | "template"
    intent: Optional[str] = None
    navigate_action: Optional[dict] = None
    navigate_actions: List[dict] = []


# ── Navigation targets ────────────────────────────────────────────────────────

# `target` is an AdminTab id in frontend/src/pages/AdminDashboard.tsx.
_ADMIN_TABS = {
    "navigation_admin_dashboard":    ("dashboard",    "Admin Dashboard"),
    "navigation_admin_officials":    ("officials",    "Officials"),
    "navigation_admin_competencies": ("competencies", "FRAC Competencies"),
    "navigation_admin_analytics":    ("analytics",    "Analytics"),
    "navigation_admin_emerging":     ("emerging",     "Emerging Skills"),
    "navigation_admin_actions":      ("actions",      "Actions"),
    "navigation_admin_insights":     ("insights",     "Workforce Insights"),
    "navigation_admin_reports":      ("reports",      "Reports"),
}

_ADMIN_REDIRECTS = {
    "navigation_learner_dashboard": ("/dashboard", "Learner Dashboard"),
    "navigation_home":              ("/",          "Landing Page"),
}

# Learner-side intents asked from the admin console: send them to the admin
# view that holds the same thing, or across to the learner app.
_LEARNER_INTENT_NAV = {
    "navigation_dashboard":       {"type": "tab",      "target": "dashboard",  "label": "Admin Dashboard"},
    "navigation_progress":        {"type": "tab",      "target": "analytics",  "label": "Analytics"},
    "navigation_certificates":    {"type": "tab",      "target": "actions",    "label": "Certificate Review"},
    "navigation_skill_gap":       {"type": "tab",      "target": "analytics",  "label": "Analytics"},
    "navigation_my_courses":      {"type": "redirect", "target": "/dashboard", "label": "Learner Dashboard"},
    "navigation_recommendations": {"type": "redirect", "target": "/dashboard", "label": "Learner Dashboard"},
    "navigation_karma":           {"type": "redirect", "target": "/dashboard", "label": "Learner Dashboard"},
    "navigation_ai_quiz":         {"type": "redirect", "target": "/assessment", "label": "Assessment Studio"},
    "navigation_home":            {"type": "redirect", "target": "/",          "label": "Landing Page"},
    "navigation_features":        {"type": "redirect", "target": "/",          "label": "Landing Page"},
    "navigation_about":           {"type": "redirect", "target": "/",          "label": "Landing Page"},
    "navigation_contact":         {"type": "redirect", "target": "/",          "label": "Landing Page"},
}


# Learner intents whose reply is meaningless on this console: an admin's own
# `skill_gaps` are empty, and "how am I doing" is a question about the workforce
# here. Answer the console equivalent instead of a personalised reply full of
# zeroes. Everything else (MoSPI, FRAC, GDP/CPI, farewell, …) falls through
# unchanged, because those answers are the same for anyone.
_LEARNER_TO_ADMIN = {
    "greeting":      "admin_capabilities",
    "profile_stats": "admin_overview",
    "skill_gaps":    "admin_shortages",
    "recommend":     "admin_emerging",
    "progress":      "admin_trends",
    "about_platform": "admin_capabilities",
}


def _nav_action(intent: str) -> Optional[dict]:
    if intent in _ADMIN_TABS:
        target, label = _ADMIN_TABS[intent]
        return {"type": "tab", "target": target, "label": label}
    if intent in _ADMIN_REDIRECTS:
        target, label = _ADMIN_REDIRECTS[intent]
        return {"type": "redirect", "target": target, "label": label}
    return None


# ── Answer builders ───────────────────────────────────────────────────────────

async def _roster() -> List[Dict[str, Any]]:
    from routers.admin_console import _roster as load
    return await load()


async def _answer_admin(intent: str, message: str, req: AdminChatRequest,
                        variant: str) -> tuple[str, Optional[dict]]:
    """(reply, navigate_action) for an admin-tier intent."""
    nav = _nav_action(intent)
    if nav:
        return admin_msg.navigation(nav["label"], variant), nav

    if intent == "admin_capabilities":
        return admin_msg.lead("capabilities", variant), None

    rows_all = await _roster()
    scope_filter, scope = facts.resolve_scope(message, (req.filters.model_dump() if req.filters else {}), rows_all)
    rows = aa.apply_filters(rows_all, scope_filter)

    if intent == "admin_overview":
        return admin_msg.overview(facts.overview_facts(rows), scope, variant), None
    if intent == "admin_officials":
        return admin_msg.officials(facts.overview_facts(rows), scope, variant), None
    if intent == "admin_compliance":
        return admin_msg.compliance(facts.overview_facts(rows), scope, variant), None
    if intent == "admin_mandatory":
        return admin_msg.mandatory(facts.overview_facts(rows), facts.behind_facts(rows, TOP_ROWS),
                                   scope, variant), None
    if intent == "admin_departments":
        return admin_msg.departments(facts.department_facts(rows, TOP_ROWS), scope, variant), None
    if intent == "admin_shortages":
        return admin_msg.shortages(facts.shortage_facts(rows, TOP_ROWS), scope, variant), None
    if intent == "admin_needs_training":
        needs = facts.needs_training_facts(rows, TOP_ROWS)
        total = sum(1 for r in rows if r["enrollmentStatus"] == 0)
        return admin_msg.needs_training(total, needs, scope, variant), None

    if intent == "admin_emerging":
        from services import app_state
        if not app_state.snapshot:
            return admin_msg.lead("snapshotPending", variant, status=app_state.snapshot_status), None
        from routers.admin_console import _emerging
        report = _emerging(rows)
        return admin_msg.emerging(report["items"][:TOP_ROWS], report["horizonMonths"], scope, variant), None

    if intent == "admin_trends":
        from routers.admin_console import _trend_series
        series = await _trend_series(TREND_DAYS, scope_filter)
        trend = facts.trend_facts(series)
        if not trend["available"]:
            return admin_msg.error("no trend points yet", variant), None
        return admin_msg.trends(trend, scope, variant), None

    if intent == "admin_health":
        from services import system_health
        return admin_msg.health(await system_health.detailed(probe_gemini=False), variant), None

    if intent == "admin_nudges":
        entries = await _recent_nudges(TOP_ROWS)
        return admin_msg.nudges(len(entries), entries[:TOP_ROWS], variant), None

    if intent == "admin_assignments":
        entries = await _recent_assignments(TOP_ROWS)
        return admin_msg.assignments(len(entries), entries[:TOP_ROWS], variant), None

    if intent == "admin_user_lookup":
        return await _official_reply(message, rows_all, variant, require_hint=False), None

    return admin_msg.lead("capabilities", variant), None


async def _recent_nudges(limit: int) -> List[Dict[str, Any]]:
    from models.models import TrainingNudge
    from routers.admin_console import _db, _name, _roster as load

    by_id = {r["userId"]: r for r in await load()}

    def query(db):
        return db.query(TrainingNudge).order_by(TrainingNudge.createdAt.desc()).limit(limit).all()

    return [{"name": _name(by_id[n.userId]) if n.userId in by_id else n.userId,
             "createdAt": n.createdAt.isoformat() if n.createdAt else None,
             "readAt": n.readAt.isoformat() if n.readAt else None}
            for n in await _db(query)]


async def _recent_assignments(limit: int) -> List[Dict[str, Any]]:
    from routers.admin_console import _assignment_out, _db, _roster as load
    from models.models import TrainingAssignment

    by_id = {r["userId"]: r for r in await load()}

    def query(db):
        return db.query(TrainingAssignment).order_by(TrainingAssignment.createdAt.desc()).limit(limit).all()

    return [_assignment_out(a, by_id) for a in await _db(query)]


async def _official_reply(message: str, rows: List[Dict[str, Any]], variant: str,
                          require_hint: bool) -> str:
    matches, term = facts.find_officials(message, rows, require_hint=require_hint)
    if not matches:
        return admin_msg.not_found(term, variant) if term else admin_msg.lead("userPrompt", variant)
    if len(matches) > 1:
        return admin_msg.ambiguous(term, matches, variant)

    row = matches[0]
    db_facts: Dict[str, Any] = {}
    try:
        from routers.admin_console import _db
        db_facts = await _db(lambda db: facts.learner_db_facts(db, row["userId"]))
    except Exception as exc:                      # karma/nudges are extra, not the answer
        log.warning("[admin-chat] DB facts for %s failed: %s", row["userId"], exc)
    return admin_msg.official(facts.official_facts(row, db_facts), variant)


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.post("/chat", response_model=AdminChatResponse)
async def admin_chat(req: AdminChatRequest, admin: UserAuth = Depends(require_role("admin"))):
    from ai.semantic_engine import ADMIN_INDEX, classify_intent, low_confidence_threshold
    from routers import chatbot

    variant = resolve_chat_variant(req.message, req.preferred_language)
    ctx = ReplyContext(page="dashboard", role=req.job_role or "System Administrator",
                       dept=req.department or "MoSPI", message=req.message,
                       full_name=req.full_name or admin.username, gov_id=admin.username)

    # A message that names one official — by usr_…/EMP-…/email, or after a
    # lead-in like "tell me about …" — is answered before anything else. It has
    # to run ahead of the shared intercepts: "tell me about Ramesh Sharma" is
    # exactly the shape `chatbot._OUT_OF_SCOPE_RE` was written to refuse.
    lookup_term = ""
    try:
        rows = await _roster()
        matches, lookup_term = facts.find_officials(req.message, rows, require_hint=True)
        if matches:
            return AdminChatResponse(reply=await _official_reply(req.message, rows, variant, require_hint=True),
                                     detected_language=to_iso(variant), engine="semantic-admin",
                                     intent="admin_user_lookup")
    except Exception as exc:
        log.warning("[admin-chat] roster unavailable for identity lookup: %s", exc)

    threshold = low_confidence_threshold()
    admin_intent, admin_conf = ADMIN_INDEX.classify(req.message, variant)
    gen_intent, gen_conf = classify_intent(req.message, variant)
    admin_wins = (admin_intent != "general" and admin_conf >= threshold
                  and admin_conf + ADMIN_MARGIN >= gen_conf)
    log.info("[Gyan/admin] lang=%s admin=%s(%.3f) general=%s(%.3f) query=%r",
             variant, admin_intent, admin_conf, gen_intent, gen_conf, req.message)

    # A lookup-shaped message that matched nobody is a *failed lookup*, not an
    # out-of-scope question — say so before the shared intercept refuses it.
    # Two words, so "tell me about Nobody Atall" gets "not on the roster" while
    # "tell me about photosynthesis" keeps the out-of-scope refusal.
    looks_like_a_name = len(lookup_term.split()) >= 2
    if looks_like_a_name and (admin_intent == "admin_user_lookup" or admin_conf < threshold):
        return AdminChatResponse(reply=admin_msg.not_found(lookup_term, variant),
                                 detected_language=to_iso(variant), engine="semantic-admin",
                                 intent="admin_user_lookup")

    intercepted = chatbot._intercept(req, variant, ctx)
    if intercepted is not None:
        return AdminChatResponse(reply=intercepted.reply, detected_language=intercepted.detected_language,
                                 engine=intercepted.engine, navigate_action=intercepted.navigate_action,
                                 navigate_actions=intercepted.navigate_actions)

    # "how am I doing", "what are my skill gaps", "hello" — answered about the
    # workforce here, not about the admin's own (empty) learner profile.
    if not admin_wins and gen_conf >= threshold and gen_intent in _LEARNER_TO_ADMIN:
        admin_intent, admin_wins = _LEARNER_TO_ADMIN[gen_intent], True

    if admin_wins:
        try:
            reply, nav = await _answer_admin(admin_intent, req.message, req, variant)
        except Exception as exc:
            log.error("[admin-chat] %s failed: %s", admin_intent, exc)
            reply, nav = admin_msg.error(exc.__class__.__name__, variant), None
        return AdminChatResponse(reply=reply, detected_language=to_iso(variant), engine="semantic-admin",
                                 intent=admin_intent, navigate_action=nav)

    # ── Everything Gyan already knew ─────────────────────────────────────────
    if gen_intent != "general" and gen_conf >= threshold:
        if gen_intent == "ui_action_request":
            out = chatbot._ui_action_response(req, variant, ctx, "semantic")
            return AdminChatResponse(reply=out.reply, detected_language=out.detected_language,
                                     engine=out.engine, intent=gen_intent,
                                     navigate_action=out.navigate_action,
                                     navigate_actions=out.navigate_actions)
        return AdminChatResponse(reply=render(gen_intent, variant, ctx), detected_language=to_iso(variant),
                                 engine="semantic", intent=gen_intent,
                                 navigate_action=_LEARNER_INTENT_NAV.get(gen_intent))

    from ai.semantic_engine import LATIN_LANGUAGES
    fallback = chatbot.detect_intent_keyword(req.message) if variant in LATIN_LANGUAGES else "fallback"
    if fallback == "fallback":
        # An unrecognised question on the admin console is far more likely to be
        # about the console than about the asker's own training.
        return AdminChatResponse(reply=admin_msg.lead("capabilities", variant),
                                 detected_language=to_iso(variant), engine="template",
                                 intent="admin_capabilities")
    if fallback == "ui_action_request":
        out = chatbot._ui_action_response(req, variant, ctx, "template")
        return AdminChatResponse(reply=out.reply, detected_language=out.detected_language,
                                 engine=out.engine, intent=fallback,
                                 navigate_action=out.navigate_action,
                                 navigate_actions=out.navigate_actions)
    return AdminChatResponse(reply=render(fallback, variant, ctx), detected_language=to_iso(variant),
                             engine="template", intent=fallback,
                             navigate_action=_LEARNER_INTENT_NAV.get(fallback))


@router.get("/chat/mode")
async def admin_chat_mode(_admin: UserAuth = Depends(require_role("admin"))):
    from ai.embedder import model_name
    from ai.semantic_engine import ADMIN_INDEX, is_semantic_engine_ready

    return {
        "engine": "semantic-admin" if ADMIN_INDEX.is_ready() else
                  "semantic" if is_semantic_engine_ready() else "template",
        "adminCorpus": {"intents": len(ADMIN_INDEX.intents), "ready": ADMIN_INDEX.is_ready()},
        "learnerTier": "ready" if is_semantic_engine_ready() else "not_loaded",
        "model": model_name("chat"),
        "checkedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "description": ("Gyan is answering from the live admin console."
                        if ADMIN_INDEX.is_ready() else
                        "Gyan is in template mode — the intent model has not finished loading."),
    }
