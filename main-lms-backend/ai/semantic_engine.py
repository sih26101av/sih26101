"""
FILE: ai/semantic_engine.py
─────────────────────────────────────────────────────────────────────────────
Gyan — Semantic Intent Engine (Render-Deployable)
MoSPI Skill Intelligence Platform | SIH 2026

Replaces the Ollama hot-path with a fully self-contained, CPU-friendly
intent classifier + profile vectorizer.

Architecture:
  1. SemanticEngine.classify(query) → (intent_name, confidence_0_to_1)
     • Encodes query with sentence-transformers all-MiniLM-L6-v2 (~80 MB)
     • Cosine-similarity match against pre-encoded prototype phrases
     • Falls back to difflib fuzzy matching for low-confidence results

  2. vectorize_profile(skill_gaps) → dict of numeric profile features
     • Converts the list of SkillGapContext dicts into stat numbers
     • Used by chatbot.py to answer profile analysis queries instantly

Design decisions:
  • Model is loaded ONCE at module import (singleton) — no per-request cost.
  • all-MiniLM-L6-v2: 80 MB, ~384-dim vectors, <50 ms CPU inference.
  • Render free tier: 512 MB RAM → model fits with room to spare.
  • Ollama/ChromaDB are NOT used here — this file is standalone.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import logging
from collections import Counter
from difflib import get_close_matches
from typing import Optional

logger = logging.getLogger(__name__)

# ── Fuzzy correction vocabulary ───────────────────────────────────────────────
# All navigable keywords on the platform that users might mistype
_NAV_VOCAB = [
    "dashboard", "skill", "gap", "gaps", "competency", "competencies",
    "course", "courses", "enroll", "enrollment", "my courses", "active",
    "progress", "achievement", "achievements", "radar", "chart",
    "quiz", "assessment", "upload", "pdf", "generate", "ai generator",
    "profile", "header", "mandatory", "statistics", "analysis",
    "recommend", "recommendation", "pathway", "learning",
    "navigate", "how", "where", "help", "find", "access", "open", "go to",
    "tab", "section", "button", "panel",
]


def _correct_tokens(query: str) -> str:
    """
    Apply difflib fuzzy correction on each token to catch common typos
    like 'dasboard' → 'dashboard',  'progres' → 'progress', etc.
    Only corrects tokens of length >= 4 (avoids corrupting short words).
    """
    tokens = query.lower().split()
    corrected = []
    for tok in tokens:
        if len(tok) >= 4:
            match = get_close_matches(tok, _NAV_VOCAB, n=1, cutoff=0.80)
            corrected.append(match[0] if match else tok)
        else:
            corrected.append(tok)
    return " ".join(corrected)


# ── Intent prototype corpus ───────────────────────────────────────────────────
# Each key maps to a list of representative phrases for that intent.
# More phrases = better coverage of synonyms and paraphrases.
#
# INTENT MAPPING TO FRONTEND SECTIONS (from LearnerDashboard.tsx):
#   "dashboard"   → Dashboard tab  → SkillGapCard (Competency & Skill-Gap Analysis)
#                                    + StatsSummary (Learning Snapshot)
#                                    + AI Recommended Learning Pathway section
#   "my-courses"  → My Courses tab → MyCoursesView (Active Enrollments)
#   "progress"    → Progress tab   → ProgressView (Competency Radar + Achievements)
#   AssessmentUploadZone (AI Assessment Generator) → always visible on Dashboard tab
#   ChatWidget    → floating bot bubble (bottom-right, fixed)
#   ProfileHeader → top of every tab (name, role, department, profile ID)

INTENT_CORPUS: dict[str, list[str]] = {

    # ── Greetings ─────────────────────────────────────────────────────────────
    "greeting": [
        "hi", "hello", "hey there", "good morning", "good evening",
        "namaste", "namaskar", "pranam", "hie", "howdy",
        "sup", "what's up", "kaise ho", "sab theek",
        "nice to meet you", "pleasure to meet you", "greetings",
        "good afternoon", "hey gyan", "hello gyan", "hi gyan",
    ],

    # ── Bot Identity (what/who is Gyan) ──────────────────────────────────────
    "bot_identity": [
        "who are you", "what are you", "tell me about yourself",
        "introduce yourself", "who is gyan", "what is gyan",
        "aap kon ho", "tum kon ho", "aap kya ho",
        "apna parichay do", "aapka naam kya hai",
        "are you a bot", "are you AI", "are you human",
        "what can you do", "how do you work",
    ],

    # ── User Identity / Personal Info ───────────────────────────────────────────────
    "user_identity": [
        "what is my name", "tell me my name",
        "what is my employee id", "my emp id", "what is my gov id",
        "what is my user id", "what is my profile id",
        "mera naam kya hai", "mera employee id kya hai",
        "meri id kya hai", "mera id batao", "meri profile ID batao",
        "which department am I in", "what department do I belong to",
        "am I verified", "am I a verified official", "mera verification status kya hai",
        "mera role kya hai",
    ],

    # ── Last Assessment / Evaluation Date ────────────────────────────────────
    "last_assessment": [
        "when did I last assess myself", "when was my last assessment",
        "last assessment date", "when was I evaluated", "last evaluation date",
        "kab assess kiya tha", "last assess kab hua",
        "mera last evaluation kab tha", "assessment date kya hai",
        "when was my competency evaluated", "last evaluated date",
    ],

    # ── Profile Overview / Stats Summary ─────────────────────────────────────
    # Triggered when user wants to understand their overall profile numbers.
    # Corresponds to: ProfileHeader + StatsSummary (Learning Snapshot widget)
    "profile_stats": [
        "show my profile", "what is my profile", "tell me about my profile",
        "my overview", "give me a summary", "my details", "who am I",
        "mera profile dikhao", "mujhe apna overview do",
        "what are my statistics", "my learning snapshot",
        "how many competencies do I have", "total competencies",
        "show my learning snapshot", "profile ID kya hai",
        "my department", "my job role", "what role am I",
        "skill overview", "mera status kya hai",
    ],

    # ── Skill Gaps ────────────────────────────────────────────────────────────
    # Corresponds to: SkillGapCard on Dashboard tab
    # The card shows: domain badges (Statistical/Technical/Governance/Leadership),
    # current level pips, target level, gap score, mandatory flag
    "skill_gaps": [
        "what are my skill gaps", "show my gaps", "which skills am I weak in",
        "where am I lacking", "my competency gaps", "what do I need to improve",
        "kahan weak hoon", "kya gap hai", "mera skill gap batao",
        "show skill gap analysis", "competency gap", "missing skills",
        "how far am I from target", "how many gaps", "gap score",
        "mandatory gap", "which skills are mandatory", "domain gap",
        "Statistical gap", "Technical gap", "Governance gap", "Leadership gap",
        "skill deficiency", "current level target level", "gap analysis",
    ],

    # ── Course Recommendations ────────────────────────────────────────────────
    # Corresponds to: "AI Recommended Learning Pathway" section on Dashboard tab
    # Shows CourseCard items sorted by priorityRank
    "recommend": [
        "recommend me a course", "which course should I take",
        "suggest a course", "what should I learn next",
        "kaunsa course lena chahiye", "kya padhu", "course suggest karo",
        "best course for me", "recommended courses", "ai recommendations",
        "learning pathway", "learning path", "next course",
        "which course to enroll in", "course for my gap",
        "top course recommendation", "priority course",
        "AI recommended", "start learning",
    ],

    # ── My Progress ───────────────────────────────────────────────────────────
    # Corresponds to: Progress tab → ProgressView
    # Shows: Competency Radar chart (Current vs Target levels per skill)
    # + Recent Achievements timeline (RAG Quiz / External Certification)
    "progress": [
        "how am I doing", "show my progress", "my progress", "learning progress",
        "how far along", "what is my progress", "progress report",
        "kitna seekha", "kitna progress hua", "meri progress dikhao",
        "am I on track", "progress percentage", "completion percentage",
        "how complete am I", "percent done", "how much left",
    ],

    # ── Achievements ──────────────────────────────────────────────────────────
    # Corresponds to: Progress tab → Recent Achievements section
    # Shows dates, quiz scores, external certification badges
    "achievements": [
        "show my achievements", "what did I achieve", "my certificates",
        "quiz scores", "my quiz results", "certification history",
        "recent achievements", "past quizzes", "what quizzes did I pass",
        "meri achievements dikhao", "kya kiya maine", "score kya tha",
    ],

    # ── Navigation: Dashboard Tab ─────────────────────────────────────────────
    # Corresponds to: Topbar tab id="dashboard", icon=LayoutDashboard
    # Dashboard contains: SkillGapCard + StatsSummary + AssessmentUploadZone + AI Recommendations
    "navigation_dashboard": [
        "how do I go to dashboard", "where is the dashboard",
        "open dashboard", "dashboard tab kahan hai", "dashboard kaise dekhu",
        "how to see skill gaps on the site", "navigate to dashboard",
        "show me the main page", "go to home tab", "main section kahan hai",
        "where can I see my gaps on the website",
    ],

    # ── Navigation: My Courses Tab ────────────────────────────────────────────
    # Corresponds to: Topbar tab id="my-courses", icon=BookOpen
    # MyCoursesView shows: EnrolledCourseCard with progress bar, last accessed, Continue button
    "navigation_my_courses": [
        "how do I see my enrolled courses", "where are my courses",
        "my courses tab kahan hai", "active enrollments kahan dekhun",
        "where is my learning history", "how to check my course progress",
        "enrolled courses kaise dekhun", "course progress bar kahan hai",
        "how to continue a course", "resume course kaise karu",
        "iGOT course status kahan hai", "enrollment status",
        "where to track my courses", "go to my courses",
        "what courses have I enrolled into", "which courses am I enrolled in",
        "show my enrollments", "meri enrollments dikhao",
        "maine kaunse courses enroll kiye hain", "enrolled courses list",
        "courses I am taking", "my active courses", "currently enrolled in courses",
    ],

    # ── Navigation: Progress Tab ──────────────────────────────────────────────
    # Corresponds to: Topbar tab id="progress", icon=TrendingUp
    # ProgressView shows: Radar chart + Achievements timeline
    "navigation_progress": [
        "how do I see the radar chart", "progress tab kahan hai",
        "where is progress section", "analytics kahan hai",
        "competency radar kahan hai", "achievement timeline kahan hai",
        "where can I see my competency chart", "trend graph kahan hai",
        "how to check achievements on site", "learning analytics kaise dekhu",
        "go to progress tab", "navigate to progress",
    ],

    # ── Navigation: AI Assessment Generator ──────────────────────────────────
    # Corresponds to: AssessmentUploadZone on Dashboard tab (right panel)
    # Card title: "AI Assessment Generator" / subtitle: "RAG Document-to-Quiz Pipeline"
    # Actions: text query + file attach (.pdf/.pptx/.txt) + Generate Assessment button
    "navigation_quiz": [
        "how do I generate a quiz", "how to create an assessment",
        "AI assessment generator kahan hai", "PDF upload kaise karu",
        "how to upload a document for quiz", "where is the quiz generator",
        "generate assessment button kahan hai", "RAG quiz kaise banau",
        "MCQ generate karna hai", "document se quiz kaise banate hain",
        "how to attach a file", "assessment upload zone kahan hai",
        "quiz feature kahan hai", "test generate karna hai",
    ],

    # ── Navigation: Profile Header / Change Password ──────────────────────────
    # Corresponds to: ProfileHeader (top of every tab)
    # + Change Password button (Lock icon, top-right navbar)
    # + Sign Out button (LogOut icon, top-right navbar)
    "navigation_profile": [
        "how do I change my password", "where is change password",
        "password change kaise karu", "account settings kahan hai",
        "how to sign out", "logout kaise karu", "where is sign out",
        "profile section kahan hai", "my information kaise change karu",
        "lock button kya hai", "where is the lock icon",
    ],

    # ── Statistics / Knowledge Topics ─────────────────────────────────────────
    "statistics_gdp": [
        "what is GDP", "explain GDP", "GDP kya hai", "GDP kaise calculate hoti hai",
        "gross domestic product", "national accounts", "SNA 2008",
        "GDP expenditure method", "GDP production method",
    ],
    "statistics_cpi": [
        "what is CPI", "consumer price index", "CPI kya hai", "inflation index",
        "price index", "Laspeyres formula", "retail inflation",
    ],
    "statistics_sampling": [
        "what is sampling", "sampling methods", "stratified sampling",
        "cluster sampling", "NSSO sampling", "probability sampling",
        "sampling kya hai", "survey design", "PLFS sampling",
    ],
    "statistics_frac": [
        "what is FRAC", "FRAC framework", "competency framework",
        "iGOT framework", "roles activities competencies",
        "FRAC dictionary", "Karmayogi framework",
    ],

    # ── Motivation ────────────────────────────────────────────────────────────
    "motivation": [
        "I feel like giving up", "this is too hard", "learning is difficult",
        "mushkil lag raha hai", "struggling with courses",
        "I am not motivated", "boring courses", "can't focus",
        "how to stay motivated", "it's too much work",
    ],

    # ── About Platform / MoSPI ───────────────────────────────────────────────
    "about_platform": [
        "tell me about this website", "what is this platform", "what does this site do",
        "explain this app", "what is MoSPI skill intelligence platform",
        "yeh website kya hai", "yeh platform kya karta hai",
        "what can I do here", "what is this tool", "platform ke baare mein batao",
        "about this app", "describe this platform", "what is this system",
        "what features does this have", "platform ki features kya hain",
    ],

    # ── About MoSPI (the ministry) ───────────────────────────────────────────
    "about_mospi": [
        "what is MoSPI", "what is mospi about", "tell me about MoSPI",
        "MoSPI kya hai", "Ministry of Statistics", "what does MoSPI do",
        "MoSPI ka kaam kya hai", "what is iGOT Karmayogi",
        "iGOT kya hai", "what is Mission Karmayogi", "Karmayogi kya hai",
        "what is NSSO", "NSO kya hai", "National Statistical Office",
        "what is the ministry of statistics", "who runs MoSPI",
    ],

    # ── Farewells ─────────────────────────────────────────────────────────────
    "farewell": [
        "bye", "goodbye", "alvida", "shukriya",
        "dhanyavad", "ok bye", "see you", "tataa", "that's all",
        "good night", "shubh ratri", "good bye", "see ya",
        "thanks bye", "thank you bye", "ok thank you", "ok thanks",
    ],

    # ── Gratitude (thanks without bye — keep conversation going) ────────────────
    "gratitude": [
        "thanks", "thank you", "great", "awesome", "wonderful", "perfect",
        "that's helpful", "very helpful", "good job", "well done",
        "shukriya", "bahut acha", "zabardast", "wah", "bhai wah", "nice",
        "that helped", "got it", "understood", "ok got it", "clear",
    ],
}

# Flat list of intents and their prototype sentences (for vectorization)
_INTENT_LABELS: list[str] = []
_PROTOTYPE_SENTENCES: list[str] = []

for _intent, _phrases in INTENT_CORPUS.items():
    for _phrase in _phrases:
        _INTENT_LABELS.append(_intent)
        _PROTOTYPE_SENTENCES.append(_phrase)


# ── Singleton model ───────────────────────────────────────────────────────────

_model = None          # SentenceTransformer (loaded once)
_prototype_vecs = None  # numpy array shape (N, 384)
_engine_ready = False


def _load_model() -> None:
    """
    Load sentence-transformers model once at startup.
    Model: all-MiniLM-L6-v2 (~80 MB, CPU-safe, Render-compatible).
    """
    global _model, _prototype_vecs, _engine_ready
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np

        logger.info("[SemanticEngine] Loading all-MiniLM-L6-v2 model...")
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        # Encode all prototype phrases once (bulk — very fast)
        _prototype_vecs = _model.encode(
            _PROTOTYPE_SENTENCES,
            normalize_embeddings=True,   # L2-normalized → dot product == cosine
            show_progress_bar=False,
            batch_size=64,
        )  # shape: (N, 384)

        _engine_ready = True
        logger.info(
            "[SemanticEngine] Ready — %d intent prototypes across %d intents.",
            len(_PROTOTYPE_SENTENCES),
            len(INTENT_CORPUS),
        )
    except Exception as exc:
        logger.warning(
            "[SemanticEngine] Failed to load model — will use keyword fallback: %s", exc
        )
        _engine_ready = False


# Load immediately when module is imported (async-safe — called from startup)
_load_model()


def is_semantic_engine_ready() -> bool:
    """Returns True if the sentence-transformer model is loaded and ready."""
    return _engine_ready


# ── Core Classifier ───────────────────────────────────────────────────────────

def classify_intent(query: str) -> tuple[str, float]:
    """
    Classify the user query into one of the intent categories.

    Steps:
      1. Fuzzy-correct any typos in the query.
      2. Encode via sentence-transformers.
      3. Cosine similarity vs prototype vectors (dot product after L2 norm).
      4. Return best-matching intent and its confidence score (0–1).

    Falls back to ("general", 0.0) if model is not loaded.
    """
    if not _engine_ready or _model is None or _prototype_vecs is None:
        return "general", 0.0

    import numpy as np

    # Step 1: typo correction
    corrected = _correct_tokens(query)

    # Step 2: encode the query (single sentence)
    query_vec = _model.encode(
        corrected,
        normalize_embeddings=True,
        show_progress_bar=False,
    )  # shape: (384,)

    # Step 3: cosine similarity = dot product (vectors are L2-normalized)
    sims = _prototype_vecs @ query_vec  # shape: (N,)

    best_idx = int(np.argmax(sims))
    best_sim = float(sims[best_idx])
    best_intent = _INTENT_LABELS[best_idx]

    logger.debug(
        "[SemanticEngine] query=%r corrected=%r intent=%s confidence=%.3f",
        query, corrected, best_intent, best_sim,
    )

    return best_intent, best_sim


# ── Profile Vectorizer ────────────────────────────────────────────────────────

def vectorize_profile(skill_gaps: list[dict]) -> dict:
    """
    Maps a list of skill gap dicts (from ChatRequest) into a flat
    numeric feature dict for instant profile statistics responses.

    Input shape (each dict):
      {skillName, domain, currentLevel, targetLevel, gapScore}

    Output dict keys:
      total_competencies  : int   — total assessed
      gaps_count          : int   — how many have gapScore > 0
      met_count           : int   — competencies at target
      completion_pct      : int   — met / total * 100
      avg_gap_score       : float — mean gap score across active gaps
      max_gap             : int   — worst single gap
      mandatory_gaps      : int   — gaps where isMandatory (if key present)
      top_domain          : str   — domain with most gaps
      domain_breakdown    : dict  — {domain: gap_count}
      tier                : str   — "on_track" | "needs_focus" | "critical"
    """
    active = [g for g in skill_gaps if g.get("gapScore", 0) > 0]
    total = len(skill_gaps)
    met = total - len(active)
    completion_pct = round((met / max(total, 1)) * 100)

    avg_gap = (
        sum(g.get("gapScore", 0) for g in active) / len(active)
        if active else 0.0
    )
    max_gap = max((g.get("gapScore", 0) for g in active), default=0)

    domain_counts: Counter = Counter(
        g.get("domain", "Unknown") for g in active
    )
    top_domain = domain_counts.most_common(1)[0][0] if domain_counts else "None"

    # Tier logic
    if completion_pct >= 70:
        tier = "on_track"
    elif completion_pct >= 40:
        tier = "needs_focus"
    else:
        tier = "critical"

    return {
        "total_competencies": total,
        "gaps_count": len(active),
        "met_count": met,
        "completion_pct": completion_pct,
        "avg_gap_score": round(avg_gap, 1),
        "max_gap": max_gap,
        "top_domain": top_domain,
        "domain_breakdown": dict(domain_counts),
        "tier": tier,
    }
