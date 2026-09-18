"""
FILE: routers/chatbot.py

Multilingual AI Learning Assistant — Gyan (ज्ञान)
MoSPI Skill Intelligence Platform | SIH 2026

Request flow
─────────────────────────────────────────────────────────────────────────────
  1. Language variant  services/language_service.resolve_chat_variant
                       (message signal first, then the widget's preferred_language)
                       en | hi (Devanagari) | hi_latn (Hinglish) | mr | bn | gu | or | ta | te
  2. English command intercepts (regex): theme / language switches, section
     scrolling, login, celebrity questions. These execute UI actions directly.
  3. Semantic intent   ai/semantic_engine.classify_intent (engine "semantic")
     Low confidence or unavailable model → keyword intents for Latin text,
     otherwise the localized fallback reply (engine "template").
  4. Reply text        services/chat_messages.render — every intent in every
     variant; this module contains no reply strings.

Ollama RAG (ai/rag_engine.py) is not in the request path.
"""

import logging
import re
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from services.chat_actions import detect_ui_actions
from services.chat_messages import (
    render,
    render_language_action,
    render_login_credentials,
    render_theme_action,
    render_theme_language_action,
)
from services.chat_messages.context import ReplyContext
from services.language_service import resolve_chat_variant, to_iso

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# REQUEST / RESPONSE MODELS
# =============================================================================

class SkillGapContext(BaseModel):
    skillName: str
    domain: str
    currentLevel: int
    targetLevel: int
    gapScore: int

class RecommendationContext(BaseModel):
    title: str
    provider: str
    durationHours: float
    matchReason: str

class ChatHistoryItem(BaseModel):
    role: str   # "user" | "model"
    content: str

class ChatRequest(BaseModel):
    user_id: str
    message: str
    history: List[ChatHistoryItem] = []
    job_role: Optional[str] = "Statistical Official"
    department: Optional[str] = "MoSPI"
    full_name: Optional[str] = None
    gov_id: Optional[str] = None
    context: Optional[str] = "dashboard"   # "dashboard" | "home"
    # Language picked in the chat widget. Used only when the message itself
    # carries no language signal — Devanagari input still gets Devanagari back.
    preferred_language: Optional[str] = None
    skill_gaps: List[SkillGapContext] = []
    recommendations: List[RecommendationContext] = []

class ChatResponse(BaseModel):
    reply: str
    detected_language: str  # ISO 639-1: en, hi, bn, mr, gu, or, ta, te
    engine: str = "template"  # "semantic" | "template"
    navigate_action: Optional[dict] = None   # single action {type, target, label}
    navigate_actions: List[dict] = []        # compound: multiple simultaneous actions


# =============================================================================
# KEYWORD FALLBACK — Latin-script intents when the semantic engine can't decide
# =============================================================================

_INTENTS = {
    "greeting":            r'\b(hi|hello|hey|namaste|namaskar|hie|good\s*(morning|evening|afternoon)|sup)\b',
    "skill_gaps":          r'\b(gap|gaps|skill\s*gap|missing|weak|improve|kya\s*gap|kitna\s*gap|deficiency|lacking|kahan\s*weak)\b',
    "recommend":           r'\b(recommend|suggest|course|courses|kya\s*padhu|kya\s*lu|kya\s*seekhu|pathway|next|start|begin|enroll|kaunsa)\b',
    "progress":            r'\b(progress|how\s*am\s*i|doing|achievement|score|result|kitna\s*seekha|kahan\s*tak)\b',
    "statistics":          r'\b(gdp|cpi|wpi|sampling|national\s*accounts|sna|frac|nsso|plfs|census|econometrics|regression|time\s*series|price\s*index)\b',
    "navigation_login":    r'\b(login|log\s*in|sign\s*in|signin|admin\s*portal|admin\s*login|kaise\s*login|login\s*karna)\b',
    "navigation_features": r'\b(feature|features|capabilities|feature\s*section|show\s*feature|scroll\s*to\s*feature)\b',
    "navigation_about":    r'\b(about\s*section|about\s*us|about\s*page|about\s*mospi|about\s*platform|scroll\s*to\s*about|take.*about)\b',
    "navigation_contact":  r'\b(contact|contact\s*section|reach\s*out|contact\s*us|contact\s*tab)\b',
    "navigation_home":     r'\b(home\s*page|landing\s*page|go\s*(to\s*)?home|take.*home|back\s*(to\s*)?home|homepage|scroll\s*to\s*top|back\s*to\s*top|top\s*of\s*page|ghar\s*jao)\b',
    "navigation_my_courses": r'\b(my\s*courses|enrolled\s*courses|course\s*list|course\s*tab)\b',
    "navigation_progress": r'\b(progress\s*tab|show.*progress|radar\s*chart|achievement\s*history)\b',
    "navigation_dashboard": r'\b(dashboard\s*tab|go\s*to\s*dashboard|open\s*dashboard)\b',
    "ui_action_request":   r'\b(dark\s*mode|light\s*mode|theme|toggle\s*theme|change.*language|switch.*language|language.*hindi|hindi.*language|language.*english|font\s*size|accessibility)\b',
    "about_platform":      r'\b(how\s*to|kaise\s*karu|navigate|use|igot|platform|karmayogi|where\s*can\s*i|help|assist|what\s*can)\b',
    "farewell":            r'\b(bye|goodbye|alvida|shukriya|thanks|thank\s*you|dhanyavad|dhanyabad|ok\s*bye|acha\s*bye)\b',
    "motivation":          r'\b(motivat|difficult|hard|tough|mushkil|give\s*up|hopeless|boring|struggle)\b',
}

_STATISTICS_TOPICS = (
    ("statistics_gdp", r'\b(gdp|national\s*accounts|sna)\b'),
    ("statistics_cpi", r'\b(cpi|wpi|price\s*index)\b'),
    ("statistics_sampling", r'\b(sampling|nsso|plfs|census)\b'),
    ("statistics_frac", r'\bfrac\b'),
)


def detect_intent_keyword(text: str) -> str:
    lower = text.lower()
    for intent, pattern in _INTENTS.items():
        if re.search(pattern, lower):
            if intent == "statistics":
                return next((topic for topic, rx in _STATISTICS_TOPICS if re.search(rx, lower)), "about_mospi")
            return intent
    return "fallback"


# =============================================================================
# NAVIGATION / UI ACTIONS
# =============================================================================

_HOME_NAV = {
    "navigation_features": {"type": "scroll", "target": "#features", "label": "Features section"},
    "navigation_about":    {"type": "scroll", "target": "#about",    "label": "About section"},
    "navigation_contact":  {"type": "scroll", "target": "#contact",  "label": "Contact section"},
    "navigation_login":    {"type": "modal",  "target": "login",     "label": "Login"},
    "navigation_home":     {"type": "scroll", "target": "#home",     "label": "Home (top)"},
}

_DASHBOARD_NAV = {
    "navigation_my_courses": {"type": "tab",      "target": "my-courses", "label": "My Courses tab"},
    "navigation_progress":   {"type": "tab",      "target": "progress",   "label": "Progress tab"},
    "navigation_dashboard":  {"type": "tab",      "target": "dashboard",  "label": "Dashboard tab"},
    "navigation_ai_quiz":    {"type": "tab",      "target": "dashboard",  "label": "AI Quiz Generator (Dashboard)"},
    "navigation_home":       {"type": "redirect", "target": "/",          "label": "Landing Page"},
}

# Intercept scroll keyword -> (intent whose reply describes it, #anchor)
_SCROLL_SECTIONS = {
    "contact": ("navigation_contact", "contact"),
    "feature": ("navigation_features", "features"),
    "about":   ("navigation_about", "about"),
    "home":    ("navigation_home", "home"),
    "top":     ("navigation_home", "home"),
}
_SCROLL_LABELS = {"contact": "Contact section", "features": "Features section", "about": "About section", "home": "Top of page"}

_LANGUAGE_NAMES = {"hi": "Hindi", "en": "English"}


def _theme_action(theme: str) -> dict:
    return {"type": "theme", "target": theme, "label": f"{theme.capitalize()} Mode"}


def _response(reply: str, variant: str, engine: str = "template", **actions) -> ChatResponse:
    return ChatResponse(reply=reply, detected_language=to_iso(variant), engine=engine, **actions)


def _ui_action_response(req: ChatRequest, variant: str, ctx: ReplyContext, engine: str) -> ChatResponse:
    theme, language = detect_ui_actions(req.message)
    if theme and language:
        if theme == "toggle":
            reply = f"{render_theme_action(variant, theme)}\n\n{render_language_action(variant, language)}"
        else:
            reply = render_theme_language_action(variant, theme, language)
        return _response(reply, variant, engine, navigate_actions=[
            _theme_action(theme),
            {"type": "language", "target": language, "label": _LANGUAGE_NAMES[language]},
        ])
    if theme:
        return _response(render_theme_action(variant, theme), variant, engine, navigate_action=_theme_action(theme))
    if language:
        return _response(
            render_language_action(variant, language), variant, engine,
            navigate_action={"type": "language", "target": language, "label": f"{_LANGUAGE_NAMES[language]} Language"},
        )
    return _response(render("ui_action_request", variant, ctx), variant, engine)


def _intent_response(intent: str, req: ChatRequest, variant: str, ctx: ReplyContext, engine: str) -> ChatResponse:
    if intent == "ui_action_request":
        return _ui_action_response(req, variant, ctx, engine)
    nav_map = _HOME_NAV if ctx.page == "home" else _DASHBOARD_NAV
    return _response(render(intent, variant, ctx), variant, engine, navigate_action=nav_map.get(intent))


# =============================================================================
# ENGLISH COMMAND INTERCEPTS
# =============================================================================

_SCROLL_RE = re.compile(
    r'\b(scroll|take\s+me|go|jump|show|navigate|open)\b.{0,25}\b(contact|features?|about|home|top)\b'
    r'|\b(contact|features?|about)\b.{0,15}\b(section|page|area)\b',
    re.IGNORECASE,
)
_LANGUAGE_CHANGE_RE = re.compile(
    r'\b(change|switch|set|turn|make).{0,20}\b(language|lang|website|site|ui|interface).{0,15}\b(hindi|english|en|hi)\b'
    r'|\b(switch|change)\s+(to\s+)?(hindi|english|en|hi)\b'
    r'|\b(website|site|ui)\s+(language|lang)\s+(to\s+)?(hindi|english)\b',
    re.IGNORECASE,
)
_THEME_WORD_RE = re.compile(
    r'\b(dark\s*mode|light\s*mode|turn\s*(on|off)\s*(dark|light)|'
    r'switch\s*(to\s*)?(dark|light)|enable\s*(dark|light)|toggle.*?(dark|light)|light|dark)\b',
    re.IGNORECASE,
)
_LANGUAGE_WORD_RE = re.compile(r'\b(hindi|english|change.*lang|switch.*lang|lang.*hindi|website.*hindi)\b', re.IGNORECASE)
_THEME_COMMAND_RE = re.compile(
    r'\b(dark\s*mode|light\s*mode|turn\s*(on|off)\s*(dark|light)|'
    r'switch\s*(to\s*)?(dark|light)|enable\s*(dark|light))\b',
    re.IGNORECASE,
)
_LOGIN_RE = re.compile(r'\b(login|log\s*in|sign\s*in|signin)\b', re.IGNORECASE)
_CREDENTIALS_RE = re.compile(r'\b(username|password|credentials|details|user\s*id|pass|userid)\b', re.IGNORECASE)
_OUT_OF_SCOPE_RE = re.compile(
    r'\b(when\s+was|when\s+is|who\s+is|who\s+was|tell\s+me\s+about|'
    r'what\s+is\s+photosynthesis|circular\s+convolution|'
    r'released|born|died|movie|film|actor|actress|singer|'
    r'cricketer|footballer|celebrity)\b',
    re.IGNORECASE,
)
_MOSPI_RE = re.compile(
    r'\b(mospi|igot|karmayogi|frac|gdp|cpi|census|plfs|nso|sna|'
    r'skill|course|dashboard|competency|training|platform)\b',
    re.IGNORECASE,
)


def _intercept(req: ChatRequest, variant: str, ctx: ReplyContext) -> Optional[ChatResponse]:
    """Deterministic handling of English commands the classifier has historically confused."""
    message = req.message

    if re.search(r'\bwho\s+am\s+i\b', message, re.IGNORECASE):
        return _response(render("user_identity", variant, ctx), variant)

    if ctx.page == "home" and _SCROLL_RE.search(message):
        lowered = message.lower()
        for keyword, (intent, anchor) in _SCROLL_SECTIONS.items():
            if keyword in lowered:
                return _response(
                    render(intent, variant, ctx), variant,
                    navigate_action={"type": "scroll", "target": f"#{anchor}", "label": _SCROLL_LABELS[anchor]},
                )

    # Compound theme + language must be checked before either single command.
    if _THEME_WORD_RE.search(message) and _LANGUAGE_WORD_RE.search(message):
        theme = "light" if re.search(r'\blight\b', message, re.IGNORECASE) else "dark"
        language = "hi" if re.search(r'\bhindi\b', message, re.IGNORECASE) else "en"
        return _response(
            render_theme_language_action(variant, theme, language), variant,
            navigate_actions=[_theme_action(theme), {"type": "language", "target": language, "label": _LANGUAGE_NAMES[language]}],
        )

    if _LANGUAGE_CHANGE_RE.search(message):
        language = "hi" if re.search(r'\b(hindi|hi)\b', message, re.IGNORECASE) else "en"
        return _response(
            render_language_action(variant, language), variant,
            navigate_action={"type": "language", "target": language, "label": f"{_LANGUAGE_NAMES[language]} Language"},
        )

    if _THEME_COMMAND_RE.search(message):
        theme = "light" if re.search(r'\blight\b', message, re.IGNORECASE) else "dark"
        return _response(render_theme_action(variant, theme), variant, navigate_action=_theme_action(theme))

    if _LOGIN_RE.search(message):
        if ctx.page != "home":
            return _response(render("navigation_login", variant, ctx), variant)
        reply = render_login_credentials(variant) if _CREDENTIALS_RE.search(message) else render("navigation_login", variant, ctx)
        return _response(reply, variant, navigate_action=_HOME_NAV["navigation_login"])

    if _OUT_OF_SCOPE_RE.search(message) and not _MOSPI_RE.search(message):
        return _response(render("out_of_scope", variant, ctx), variant)

    return None


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Multilingual AI Learning Assistant — Gyan (ज्ञान)."""
    variant = resolve_chat_variant(req.message, req.preferred_language)
    ctx = ReplyContext.from_request(req)

    intercepted = _intercept(req, variant, ctx)
    if intercepted is not None:
        return intercepted

    from ai.semantic_engine import LATIN_LANGUAGES, classify_intent

    intent, confidence = classify_intent(req.message, variant)
    logger.info("[Gyan/semantic] lang=%s intent=%s confidence=%.3f query=%r", variant, intent, confidence, req.message)

    # classify_intent already downgrades weak matches to out_of_scope, so its answer
    # is final. The keyword tier below only covers the embedder being unavailable —
    # it must not second-guess a working model, or nonsense containing domain words
    # ("course gap dashboard banana") gets answered with real recommendations.
    if intent != "general":
        return _intent_response(intent, req, variant, ctx, engine="semantic")

    logger.info("[Gyan] Semantic engine unavailable — keyword fallback.")
    fallback_intent = detect_intent_keyword(req.message) if variant in LATIN_LANGUAGES else "fallback"
    return _intent_response(fallback_intent, req, variant, ctx, engine="template")


@router.get("/chat/mode")
async def chat_mode():
    """Which response engine is active; the frontend shows it as a badge."""
    from ai.embedder import model_name
    from ai.semantic_engine import is_semantic_engine_ready

    semantic_ok = is_semantic_engine_ready()
    return {
        "engine":          "semantic" if semantic_ok else "template",
        "semantic_status": "ready" if semantic_ok else "not_loaded",
        "model":           model_name("chat"),
        "languages":       ["en", "hi", "mr", "bn", "gu", "or", "ta", "te"],
        "ollama_status":   "disconnected (not in request path)",
        "description": (
            "Gyan is running in Semantic AI mode (multilingual intent classifier)"
            if semantic_ok else
            "Gyan is running in Standard mode (keyword template engine)"
        ),
    }
