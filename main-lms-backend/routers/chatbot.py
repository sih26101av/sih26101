"""
FILE: routers/chatbot.py

Multilingual AI Learning Assistant — Gyan (ज्ञान)
Archit Shukla | MoSPI Skill Intelligence Platform | SIH 2026

Three-tier response engine:
─────────────────────────────────────────────────────────────────────────────
  TIER 1 (PRIMARY — Render-deployable)
    → Semantic Intent Engine (sentence-transformers all-MiniLM-L6-v2)
      • Classifies query via cosine similarity on pre-encoded intent prototypes
      • Instant profile vectorization for profile stats queries
      • Fuzzy typo correction via difflib
      • Tab-specific navigation answers based on actual frontend structure
      • Engine label: "semantic"

  TIER 2 (FALLBACK — always works, no dependencies)
    → Keyword + regex template engine
      • Original intent-matching templates
      • Activates if semantic model is not loaded (cold start or import error)
      • Engine label: "template"

  TIER 3 (DISCONNECTED — available for local/dev use only)
    → Ollama RAG pipeline (llama3.2:3b + ChromaDB nomic-embed-text)
      • NOT called from this router in production
      • Code kept in ai/rag_engine.py + ai/vector_store.py for easy revert
      • To re-enable: swap TIER 1 priority order below (search REVERT_OLLAMA)
─────────────────────────────────────────────────────────────────────────────

Frontend structure (verified from LearnerDashboard.tsx):
  Tabs  (Topbar):
    • "dashboard"   → SkillGapCard + StatsSummary (Learning Snapshot)
                      + AssessmentUploadZone + AI Recommended Pathway
    • "my-courses"  → MyCoursesView (Active Enrollments, progress bars)
    • "progress"    → ProgressView (Competency Radar chart + Achievements)
  Persistent:
    • ProfileHeader → top of every tab (name, role, dept, profile ID)
    • ChatWidget    → floating bubble bottom-right (this chatbot)
  Navbar icons:
    • Home (→ landing), Moon/Sun (theme toggle),
      Lock (→ /change-password), LogOut (sign out)
"""

import logging
import re
import random
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

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
    skill_gaps: List[SkillGapContext] = []
    recommendations: List[RecommendationContext] = []

class ChatResponse(BaseModel):
    reply: str
    detected_language: str  # "hi" | "en"
    engine: str = "template"  # "semantic" | "template"


# =============================================================================
# LANGUAGE DETECTION
# =============================================================================

_HINDI_DEVANAGARI = re.compile(r'[\u0900-\u097F]')
_HINGLISH_WORDS = {
    'kya', 'kaun', 'kaise', 'mujhe', 'mera', 'meri', 'mein', 'hai', 'hain',
    'nahi', 'batao', 'bolo', 'karo', 'lena', 'chahiye', 'acha',
    'theek', 'samjhao', 'kab', 'kyun', 'kitna', 'kitne', 'sikho', 'padhna',
    'seekhna', 'lagta', 'zyada', 'thoda', 'bahut', 'sir', 'madam',
    'kuch', 'sab', 'jo', 'woh', 'abhi', 'aaj', 'kal', 'dikhao',
    # Extended Hinglish
    'aap', 'kon', 'hoon', 'naam', 'mere', 'apna', 'ho', 'hua', 'hui',
    'raha', 'rahi', 'tha', 'thi', 'accha', 'bilkul', 'zaruri', 'milta',
    'namaste', 'namaskar', 'pranam', 'alvida', 'shukriya', 'dhanyavad',
    'tum', 'wah', 'zabardast', 'bahut', 'bahut', 'parichay',
}


def detect_language(text: str) -> str:
    if _HINDI_DEVANAGARI.search(text):
        return "hi"
    words = set(text.lower().split())
    if len(words & _HINGLISH_WORDS) >= 1:
        return "hi"
    return "en"


# =============================================================================
# KEYWORD FALLBACK — intent detection (regex, used for Tier 2 template engine)
# =============================================================================

_INTENTS = {
    "greeting":       r'\b(hi|hello|hey|namaste|namaskar|hie|good\s*(morning|evening|afternoon)|sup)\b',
    "skill_gaps":     r'\b(gap|gaps|skill\s*gap|missing|weak|improve|kya\s*gap|kitna\s*gap|deficiency|lacking|kahan\s*weak)\b',
    "recommend":      r'\b(recommend|suggest|course|courses|kya\s*padhu|kya\s*lu|kya\s*seekhu|path|pathway|next|start|begin|enroll|kaunsa|which)\b',
    "progress":       r'\b(progress|how\s*am\s*i|doing|status|achievement|score|result|kitna\s*seekha|kahan\s*tak)\b',
    "statistics":     r'\b(gdp|cpi|wpi|sampling|national\s*accounts|sna|frac|nsso|plfs|census|econometrics|regression|time\s*series|price\s*index)\b',
    "platform_help":  r'\b(how\s*to|kaise\s*karu|navigate|use|igot|platform|login|enroll|karmayogi|where\s*can\s*i|help|assist)\b',
    "hindi_greeting": r'\b(namaste|namaskar|pranam|kaise\s*(ho|hain)|sab\s*(theek|thik))\b',
    "farewell":       r'\b(bye|goodbye|alvida|shukriya|thanks|thank\s*you|dhanyavad|dhanyabad|ok\s*bye|acha\s*bye)\b',
    "motivation":     r'\b(motivat|difficult|hard|tough|mushkil|give\s*up|hopeless|boring|struggle)\b',
}

def detect_intent_keyword(text: str) -> str:
    lower = text.lower()
    for intent, pattern in _INTENTS.items():
        if re.search(pattern, lower):
            return intent
    return "general"


# =============================================================================
# PROFILE HELPERS (shared by both Tier 1 and Tier 2)
# =============================================================================

def _fmt_gaps(gaps: List[SkillGapContext], lang: str) -> str:
    active = [g for g in gaps if g.gapScore > 0]
    if not active:
        if lang == "hi":
            return "Aapke sabhi competencies target level par hain! Badhai ho! 🎉"
        return "All your competencies are at target level! 🎉"
    lines = []
    for g in sorted(active, key=lambda x: -x.gapScore):  # show ALL gaps, sorted by severity
        if lang == "hi":
            lines.append(f"• **{g.skillName}** ({g.domain}): Level {g.currentLevel} → {g.targetLevel} chahiye (Gap: {g.gapScore})")
        else:
            lines.append(f"• **{g.skillName}** ({g.domain}): Level {g.currentLevel} → {g.targetLevel} needed (Gap: {g.gapScore})")
    return "\n".join(lines)

def _fmt_recs(recs: List[RecommendationContext], lang: str, n: int = 3) -> str:
    if not recs:
        if lang == "hi":
            return "Abhi koi recommendations available nahi hain."
        return "No recommendations available right now."
    lines = []
    for i, r in enumerate(recs[:n], 1):
        hrs = f"{r.durationHours:.0f}h"
        if lang == "hi":
            lines.append(f"{i}. **{r.title}** ({r.provider}, {hrs})")
        else:
            lines.append(f"{i}. **{r.title}** — {r.provider} | {hrs}")
    return "\n".join(lines)

def _top_gap(gaps: List[SkillGapContext]) -> Optional[SkillGapContext]:
    active = [g for g in gaps if g.gapScore > 0]
    return sorted(active, key=lambda x: -x.gapScore)[0] if active else None


# =============================================================================
# TIER 1 — SEMANTIC RESPONSE HANDLERS
# Keyed by intent name returned by semantic_engine.classify_intent()
# Uses actual frontend section names from LearnerDashboard.tsx
# =============================================================================

def _handle_semantic(
    intent: str,
    req: ChatRequest,
    lang: str,
) -> str:
    """
    Dispatch to the correct response handler based on semantic intent.
    Returns a formatted markdown string.
    """
    gaps = req.skill_gaps
    recs = req.recommendations
    role = req.job_role or "Statistical Official"
    dept = req.department or "MoSPI"
    top = _top_gap(gaps)
    active_gaps = [g for g in gaps if g.gapScore > 0]

    # ── Greeting ────────────────────────────────────────────────────────────
    if intent in ("greeting", "hindi_greeting"):
        if lang == "hi":
            return (
                f"Namaste! 🙏 Main **Gyan** hoon — aapka MoSPI AI Training Assistant.\n\n"
                f"Main dekh sakta hoon ki aap **{role}** hain **{dept}** mein.\n"
                f"Aapke paas **{len(active_gaps)} active skill gap(s)** hain.\n\n"
                f"Aap mujhse pooch sakte hain:\n"
                f"• Apne skill gaps ke baare mein\n"
                f"• Recommended courses ke baare mein\n"
                f"• Platform navigate karne mein madad\n"
                f"• Statistics topics (GDP, CPI, Sampling, FRAC)\n\n"
                f"Aaj main aapki kya madad kar sakta hoon? 🎓"
            )
        return (
            f"Hello! 👋 I'm **Gyan**, your MoSPI AI Training Assistant.\n\n"
            f"You're a **{role}** in {dept}. "
            f"You currently have **{len(active_gaps)} active skill gap(s)**.\n\n"
            f"Ask me about:\n"
            f"• Your skill gaps and priority areas\n"
            f"• Which courses to take next\n"
            f"• How to navigate different parts of this platform\n"
            f"• Statistical concepts (GDP, CPI, Sampling, FRAC)\n\n"
            f"How can I help you today? 🎓"
        )

    # ── Bot Identity (who is Gyan) ─────────────────────────────────────────────────
    if intent == "bot_identity":
        if lang == "hi":
            return (
                f"Main **Gyan (\u091c\u094d\u091e\u093e\u0928)** hoon \u2014 MoSPI ka AI-powered Learning Assistant. \U0001f916\n\n"
                f"Main ek **semantic AI chatbot** hoon jo sentence-transformers model use karta hai "
                f"aapke sawalon ko samajhne ke liye.\n\n"
                f"Main aapki madad kar sakta hoon:\n"
                f"\u2022 **Skill Gaps** \u2014 aapke current aur target levels\n"
                f"\u2022 **Course Recommendations** \u2014 personalized learning pathway\n"
                f"\u2022 **Platform Navigation** \u2014 Dashboard, My Courses, Progress tabs\n"
                f"\u2022 **Statistics** \u2014 GDP, CPI, Sampling, FRAC framework\n\n"
                f"Aap {role} hain {dept} mein. Aaj main aapki kya madad kar sakta hoon? \U0001f393"
            )
        return (
            f"I'm **Gyan (\u091c\u094d\u091e\u093e\u0928)** \u2014 the AI-powered Learning Assistant for MoSPI. \U0001f916\n\n"
            f"I'm a **semantic AI chatbot** powered by sentence-transformers, "
            f"built to understand natural language \u2014 in English, Hindi, and Hinglish.\n\n"
            f"I can help you with:\n"
            f"\u2022 **Skill Gaps** \u2014 your current vs target competency levels\n"
            f"\u2022 **Course Recommendations** \u2014 your personalized learning pathway\n"
            f"\u2022 **Platform Navigation** \u2014 how to use Dashboard, My Courses, Progress tabs\n"
            f"\u2022 **Statistics** \u2014 GDP, CPI, Sampling, FRAC framework\n\n"
            f"You're a **{role}** in {dept}. What can I help you with today? \U0001f393"
        )

    # ── Gratitude (thanks/great without goodbye) ───────────────────────────────
    if intent == "gratitude":
        if lang == "hi":
            return random.choice([
                f"Khushi hui madad karke! \U0001f604 Kya aur kuch poochna hai?",
                f"Bilkul! Agar aur koi sawaal ho toh zaroor poochein. \U0001f393",
                f"Main hamesha yahan hoon. Aur kuch chahiye? \U0001f916",
            ])
        return random.choice([
            f"Glad I could help! \U0001f604 Anything else you'd like to know?",
            f"You're welcome! Feel free to ask me anything else. \U0001f393",
            f"Happy to assist! Is there anything else I can help with? \U0001f916",
        ])

    # ── User Identity ─────────────────────────────────────────────────────────────
    if intent == "user_identity":
        if lang == "hi":
            return (
                f"Aapki personal details **Profile Header** mein hoti hain — "
                f"jo har tab ke **top** par dikhti hai.\n\n"
                f"Wahan aapko milega:\n"
                f"👤 **Full Name** aur 'Verified Official' badge\n"
                f"🪪 **Gov ID / Employee ID** (User icon ke paas)\n"
                f"🏢 **Department**: {dept}\n"
                f"💼 **Job Role**: {role}\n"
                f"📅 **Last Assessment Date** (Clock icon ke paas)\n\n"
                f"Right side par **Profile ID** aur **Competencies Assessed** count bhi dikhta hai."
            )
        return (
            f"Your personal details are in the **Profile Header** — "
            f"visible at the **top of every tab**.\n\n"
            f"It shows:\n"
            f"👤 **Full Name** with 'Verified Official' badge\n"
            f"🪪 **Gov ID / Employee ID** (next to the User icon)\n"
            f"🏢 **Department**: {dept}\n"
            f"💼 **Job Role**: {role}\n"
            f"📅 **Last Assessment Date** (next to the Clock icon)\n\n"
            f"On the right side you'll also see your **Profile ID** and **Competencies Assessed** count."
        )

    # ── Last Assessment Date ─────────────────────────────────────────────────
    if intent == "last_assessment":
        if lang == "hi":
            return (
                f"Aapki **last assessment date** Profile Header mein dikhti hai — "
                f"jo har tab ke top par hoti hai.\n\n"
                f"📅 **Clock icon** ke paas, 'Last assessed: DD Mon YYYY' format mein date dikhti hai.\n\n"
                f"Detailed assessment history aur quiz scores dekhne ke liye "
                f"**Progress tab** par jayein (top navbar mein TrendingUp icon). "
                f"Wahan aapki achievements timeline hoti hai jisme:\n"
                f"• RAG Quiz results (score % ke saath)\n"
                f"• External Certifications\n"
                f"• Date aur title har achievement ka"
            )
        return (
            f"Your **last assessment date** is shown in the **Profile Header** — "
            f"at the top of every tab.\n\n"
            f"📅 Look for the **Clock icon** — it shows 'Last assessed: DD Mon YYYY'.\n\n"
            f"For detailed assessment history and quiz scores, go to the "
            f"**Progress tab** (TrendingUp icon in the top navbar). There you'll find:\n"
            f"• RAG Quiz results with scores (%)\n"
            f"• External Certifications\n"
            f"• Date and title for each achievement"
        )

    # ── Profile Stats ────────────────────────────────────────────────────────
    # Uses vectorize_profile() to compute stats from live incoming data
    if intent == "profile_stats":
        from ai.semantic_engine import vectorize_profile
        gaps_dicts = [
            {"skillName": g.skillName, "domain": g.domain,
             "currentLevel": g.currentLevel, "targetLevel": g.targetLevel,
             "gapScore": g.gapScore}
            for g in gaps
        ]
        stats = vectorize_profile(gaps_dicts)
        tier_label = {
            "on_track":    ("On Track 🟢", "Aap sahi raaste par hain 🟢"),
            "needs_focus": ("Needs Focus 🟡", "Kuch aur mehnat zaruri hai 🟡"),
            "critical":    ("Critical — Act Now 🔴", "Turant dhyan dena zaruri hai 🔴"),
        }.get(stats["tier"], ("In Progress", "Jari hai"))

        domain_lines = "\n".join(
            f"  • {domain}: {count} gap(s)"
            for domain, count in stats["domain_breakdown"].items()
        ) or "  • No active gaps"

        if lang == "hi":
            return (
                f"**Aapka Profile Overview** ({role}, {dept}):\n\n"
                f"📊 **Learning Snapshot** (Dashboard → right panel mein dikhta hai)\n"
                f"• Total Competencies Assessed: **{stats['total_competencies']}**\n"
                f"• Competencies Met: **{stats['met_count']}**\n"
                f"• Active Gaps: **{stats['gaps_count']}**\n"
                f"• Completion: **{stats['completion_pct']}%** — {tier_label[1]}\n\n"
                f"🎯 **Gap Detail:**\n"
                f"• Sabse bada gap: **{top.skillName if top else 'None'} ({top.gapScore if top else 0} levels)**\n"
                f"• Average gap score: {stats['avg_gap_score']}\n"
                f"• Domain-wise gaps:\n{domain_lines}\n\n"
                f"Apne skill gaps detail mein dekhne ke liye **Dashboard tab** par jayein. "
                f"Progress chart ke liye **Progress tab** use karein. 📈"
            )
        return (
            f"**Your Profile Overview** ({role}, {dept}):\n\n"
            f"📊 **Learning Snapshot** (visible on Dashboard → right panel)\n"
            f"• Total Competencies Assessed: **{stats['total_competencies']}**\n"
            f"• Competencies Met: **{stats['met_count']}**\n"
            f"• Active Gaps: **{stats['gaps_count']}**\n"
            f"• Completion: **{stats['completion_pct']}%** — {tier_label[0]}\n\n"
            f"🎯 **Gap Summary:**\n"
            f"• Biggest gap: **{top.skillName if top else 'None'} ({top.gapScore if top else 0} level(s) behind)**\n"
            f"• Average gap score: {stats['avg_gap_score']}\n"
            f"• Gaps by domain:\n{domain_lines}\n\n"
            f"Go to the **Dashboard tab** for detailed skill gap cards. "
            f"Visit the **Progress tab** for your Competency Radar chart. 📈"
        )

    # ── Skill Gaps ───────────────────────────────────────────────────────────
    if intent == "skill_gaps":
        gap_text = _fmt_gaps(gaps, lang)
        if lang == "hi":
            if not active_gaps:
                return f"Mashallah! 🎉 Aapke **{len(gaps)} competencies** sab target level par hain.\n\nAap bahut accha kar rahe hain '{role}' role mein!"
            return (
                f"Aapke current skill gaps ({role} ke liye):\n\n"
                f"{gap_text}\n\n"
                f"Sabse bada gap **{top.skillName}** mein hai — {top.gapScore} level ka farq.\n\n"
                f"💡 *Yeh gaps Dashboard tab ke **Competency & Skill-Gap Analysis** card mein dikhte hain, "
                f"jahan har competency ki current level aur target level pip-strip ke saath show hoti hai.*\n\n"
                f"Kya main courses suggest karun is gap ko close karne ke liye?"
            )
        if not active_gaps:
            return f"Excellent! 🎉 All **{len(gaps)} competencies** are at or above target level for your role as {role}. Keep it up!"
        return (
            f"Here are your active skill gaps for **{role}**:\n\n"
            f"{gap_text}\n\n"
            f"Your biggest priority is **{top.skillName}** with a {top.gapScore}-level gap.\n\n"
            f"💡 *You can see these visually on the **Dashboard tab** → "
            f"'Competency & Skill-Gap Analysis' card (left panel). "
            f"Each skill shows current level pips vs target level.*\n\n"
            f"Want me to recommend courses to close this gap?"
        )

    # ── Recommendations ──────────────────────────────────────────────────────
    if intent == "recommend":
        rec_text = _fmt_recs(recs, lang)
        if lang == "hi":
            if not recs:
                return "Abhi aapke liye recommendations generate nahi hui hain. Dashboard refresh karke dekhein."
            priority_reason = f"**{top.skillName}** mein {top.gapScore}-level gap" if top else "aapke role requirements"
            return (
                f"Aapke liye personalized learning pathway, {priority_reason} ke basis par:\n\n"
                f"{rec_text}\n\n"
                f"**{recs[0].title}** se shuru karna best rahega — kyunki {recs[0].matchReason.lower()}\n\n"
                f"💡 *Yeh courses **Dashboard tab** ke sabse neeche '**AI Recommended Learning Pathway**' "
                f"section mein dikhte hain.*"
            )
        if not recs:
            return "No recommendations found yet. Try refreshing your dashboard."
        priority_reason = f"your {top.gapScore}-level gap in **{top.skillName}**" if top else "your role requirements"
        return (
            f"Based on {priority_reason}, here's your personalized learning pathway:\n\n"
            f"{rec_text}\n\n"
            f"Start with **{recs[0].title}** — {recs[0].matchReason.lower()}\n\n"
            f"💡 *Find all these courses at the bottom of the **Dashboard tab**, "
            f"in the '**AI Recommended Learning Pathway**' section.*"
        )

    # ── Progress ─────────────────────────────────────────────────────────────
    if intent == "progress":
        met = len(gaps) - len(active_gaps)
        total = len(gaps)
        pct = round((met / total * 100) if total else 0)
        if lang == "hi":
            return (
                f"Aapki progress summary ({role}):\n\n"
                f"✅ **{met}/{total}** competencies target level par hain ({pct}%)\n"
                f"⚠️ **{len(active_gaps)}** gaps abhi bhi close karne hain\n\n"
                f"{'Bahut badhiya! Aap sahi raaste par hain. 👏' if pct >= 60 else 'Abhi shuru karte hain — recommended courses follow karein!'}\n\n"
                f"💡 *Detailed progress radar chart dekhne ke liye **Progress tab** par click karein. "
                f"Wahan har skill ka Current vs Target level radar chart mein dikh ta hai, "
                f"saath mein aapki recent achievements bhi.*"
            )
        return (
            f"Your learning progress as **{role}**:\n\n"
            f"✅ **{met}/{total}** competencies at target level ({pct}% complete)\n"
            f"⚠️ **{len(active_gaps)}** gap(s) still to close\n\n"
            f"{'Great progress! You\'re well on track. 👏' if pct >= 60 else 'Keep going — follow your recommended courses to close the remaining gaps!'}\n\n"
            f"💡 *For a detailed radar chart of all your skills (Current vs Target), "
            f"switch to the **Progress tab** (TrendingUp icon in the top navbar). "
            f"You'll also see your quiz and certification achievements there.*"
        )

    # ── Achievements ─────────────────────────────────────────────────────────
    if intent == "achievements":
        if lang == "hi":
            return (
                f"Aapki achievements **Progress tab** par dekhne ko milti hain.\n\n"
                f"**Progress tab** kaise open karein:\n"
                f"1. Top navigation bar mein **TrendingUp icon** par click karein\n"
                f"2. 'Progress' button choose karein (teen tabs mein se)\n\n"
                f"Wahan aapko milega:\n"
                f"📊 **Competency Radar Chart** — sab skills ka Current vs Target level\n"
                f"🏆 **Recent Achievements** — RAG Quiz results aur External Certifications\n\n"
                f"Har achievement mein date, title aur score (%) show hota hai."
            )
        return (
            f"Your achievements are visible on the **Progress tab**.\n\n"
            f"**How to get there:**\n"
            f"1. Click the **TrendingUp icon** (📈) in the top navigation bar\n"
            f"2. Select the **'Progress'** tab\n\n"
            f"On the Progress tab you'll find:\n"
            f"📊 **Competency Radar Chart** — all your skills plotted Current vs Target level\n"
            f"🏆 **Recent Achievements** — RAG Quiz scores and External Certifications\n\n"
            f"Each achievement shows the date, title, and your score (%)."
        )

    # ── Navigation: Dashboard ────────────────────────────────────────────────
    if intent == "navigation_dashboard":
        if lang == "hi":
            return (
                f"**Dashboard tab** kaise access karein:\n\n"
                f"Top navigation bar mein **LayoutDashboard icon** ke saath **'Dashboard'** button par click karein.\n\n"
                f"Dashboard tab par yeh sections milte hain:\n\n"
                f"📋 **Competency & Skill-Gap Analysis** (main left panel)\n"
                f"   Aapke har skill ka current level (pip-strip) aur target level,\n"
                f"   domain badge (Statistical/Technical/Governance/Leadership),\n"
                f"   aur gap score dikhta hai.\n\n"
                f"📊 **Learning Snapshot** (right panel)\n"
                f"   4 quick stats: Total Competencies, Active Gaps, Mandatory Gaps, Recommendations.\n\n"
                f"🤖 **AI Assessment Generator** (right panel, neeche)\n"
                f"   PDF ya text upload karke quiz generate karein.\n\n"
                f"✨ **AI Recommended Learning Pathway** (sabse neeche)\n"
                f"   Aapke gaps ke basis par personalized course cards."
            )
        return (
            f"**How to access the Dashboard tab:**\n\n"
            f"Click the **'Dashboard'** button (LayoutDashboard icon) in the top navigation bar.\n\n"
            f"The Dashboard tab contains:\n\n"
            f"📋 **Competency & Skill-Gap Analysis** (main left panel)\n"
            f"   Every skill with current level pip-strip, target level, domain badge\n"
            f"   (Statistical / Technical / Governance / Leadership), and gap score.\n\n"
            f"📊 **Learning Snapshot** (right panel)\n"
            f"   4 quick stats: Total Competencies, Active Gaps, Mandatory Gaps, Recommendations.\n\n"
            f"🤖 **AI Assessment Generator** (right panel, bottom)\n"
            f"   Upload a PDF/PPTX/TXT and generate an MCQ quiz.\n\n"
            f"✨ **AI Recommended Learning Pathway** (bottom of page)\n"
            f"   Personalized course cards ranked by your skill gap priority."
        )

    # ── Navigation: My Courses ───────────────────────────────────────────────
    if intent == "navigation_my_courses":
        if lang == "hi":
            return (
                f"**My Courses tab** kahan hai aur kaise access karein:\n\n"
                f"Top navigation bar mein **BookOpen icon** ke saath **'My Courses'** button par click karein.\n\n"
                f"My Courses tab mein dikhta hai:\n\n"
                f"📚 **Active Enrollments** — aapke enrolled sabhi courses\n"
                f"   Har course card mein:\n"
                f"   • Course naam aur source (iGOT Karmayogi / Other)\n"
                f"   • **Course Progress bar** (% complete)\n"
                f"   • Remaining hours\n"
                f"   • Last accessed date\n"
                f"   • **'Continue'** button (course resume karne ke liye)\n\n"
                f"Agar koi enrolled course nahi hai, toh **Dashboard tab** par jayein\n"
                f"aur 'AI Recommended Learning Pathway' se course select karein."
            )
        return (
            f"**How to access the My Courses tab:**\n\n"
            f"Click the **'My Courses'** button (BookOpen icon) in the top navigation bar.\n\n"
            f"On this tab you'll see:\n\n"
            f"📚 **Active Enrollments** — all your currently enrolled courses\n"
            f"   Each course card shows:\n"
            f"   • Course title and source (iGOT Karmayogi / Other)\n"
            f"   • **Course Progress bar** (% complete)\n"
            f"   • Remaining hours\n"
            f"   • Last accessed date\n"
            f"   • **'Continue'** button to resume the course\n\n"
            f"If you have no active enrollments, go to the **Dashboard tab** "
            f"and pick a course from the 'AI Recommended Learning Pathway' section."
        )

    # ── Navigation: Progress ─────────────────────────────────────────────────
    if intent == "navigation_progress":
        if lang == "hi":
            return (
                f"**Progress tab** kahan hai aur kya dikhta hai:\n\n"
                f"Top navigation bar mein **TrendingUp icon** ke saath **'Progress'** button par click karein.\n\n"
                f"Progress tab mein do sections hain:\n\n"
                f"📊 **Competency Radar Chart** (left side)\n"
                f"   Aapke sabhi skills ka radar/spider chart — blue fill = Current level,\n"
                f"   dashed line = Target level. Kisi bhi skill par hover karein\n"
                f"   toh Current/Target values aur gap tooltip mein dikh ta hai.\n\n"
                f"🏆 **Recent Achievements** (right side)\n"
                f"   Timeline format mein — RAG Quiz results (score %) aur\n"
                f"   External Certifications, date ke saath."
            )
        return (
            f"**How to access the Progress tab:**\n\n"
            f"Click the **'Progress'** button (TrendingUp icon) in the top navigation bar.\n\n"
            f"The Progress tab has two sections:\n\n"
            f"📊 **Competency Radar Chart** (left panel)\n"
            f"   A spider chart of all your skills — blue fill = Current level, "
            f"   dashed = Target level. Hover over any skill to see Current/Target values and gap.\n\n"
            f"🏆 **Recent Achievements** (right panel)\n"
            f"   A timeline of your RAG Quiz results (with scores) and External Certifications."
        )

    # ── Navigation: AI Quiz Generator ───────────────────────────────────────
    if intent == "navigation_quiz":
        if lang == "hi":
            return (
                f"**AI Assessment Generator** kaise use karein:\n\n"
                f"Yeh feature **Dashboard tab** par right panel mein neeche dikhta hai.\n\n"
                f"Steps:\n"
                f"1. **Dashboard tab** par jayein (top navbar → Dashboard icon)\n"
                f"2. Right side pe **'AI Assessment Generator'** card dhundhein\n"
                f"   (Bot icon ke saath, subtitle: 'RAG Document-to-Quiz Pipeline')\n"
                f"3. Text box mein apna query/topic type karein\n"
                f"4. (Optional) **'Attach document'** par click karke\n"
                f"   .pdf / .pptx / .txt file attach karein\n"
                f"5. **'Generate Assessment'** button click karein\n\n"
                f"💡 File upload se zyada accurate MCQs milte hain kyunki\n"
                f"AI document ke content se questions banata hai."
            )
        return (
            f"**How to use the AI Assessment Generator:**\n\n"
            f"This feature is on the **Dashboard tab**, in the right panel (bottom card).\n\n"
            f"Steps:\n"
            f"1. Go to the **Dashboard tab** (click Dashboard icon in top navbar)\n"
            f"2. Find the **'AI Assessment Generator'** card on the right side\n"
            f"   (Bot icon, subtitle: 'RAG Document-to-Quiz Pipeline')\n"
            f"3. Type your topic or query in the text box\n"
            f"4. (Optional) Click **'Attach document'** to upload a .pdf / .pptx / .txt file\n"
            f"5. Click the **'Generate Assessment'** button\n\n"
            f"💡 Attaching a document produces more accurate MCQs as the AI "
            f"generates questions directly from your document's content."
        )

    # ── Navigation: Profile / Password / Logout ──────────────────────────────
    if intent == "navigation_profile":
        if lang == "hi":
            return (
                f"**Profile, Password aur Logout** kaise karein:\n\n"
                f"Top navigation bar mein **right side** par yeh options hain:\n\n"
                f"🔒 **Change Password** — Lock icon par click karein\n"
                f"   → '/change-password' page par le jaata hai\n\n"
                f"🚪 **Sign Out** — 'Sign Out' button par click karein\n"
                f"   → aap login page par wapas aa jayenge\n\n"
                f"🌙/☀️ **Dark/Light Mode** — Moon ya Sun icon par click karein\n\n"
                f"🏠 **Landing Page** — Home icon par click karein\n\n"
                f"📋 **Aapka Profile** (read-only) har tab ke top par dikhta hai:\n"
                f"   Name, role, department, Profile ID, aur last assessment date."
            )
        return (
            f"**Profile, Password & Navigation options:**\n\n"
            f"All these are in the **top-right of the navigation bar**:\n\n"
            f"🔒 **Change Password** — click the Lock icon\n"
            f"   → Takes you to the Change Password page\n\n"
            f"🚪 **Sign Out** — click the 'Sign Out' button\n"
            f"   → Logs you out and redirects to the login page\n\n"
            f"🌙/☀️ **Dark / Light Mode** — click the Moon or Sun icon to toggle theme\n\n"
            f"🏠 **Landing Page** — click the Home icon to go back to the landing page\n\n"
            f"📋 **Your Profile** (read-only) is always visible at the top of each tab:\n"
            f"   Shows your name, job role, department, Profile ID, and last assessment date."
        )

    # ── About the Platform ───────────────────────────────────────────────────
    if intent == "about_platform":
        if lang == "hi":
            return (
                f"**MoSPI Skill Intelligence Platform** — aapka AI-powered learning tool hai "
                f"MoSPI ke government officials ke liye.\n\n"
                f"🎯 **Yeh platform kya karta hai:**\n"
                f"• Aapki **skill gaps** identify karta hai — job role ke liye kaunsi competencies target se kam hain\n"
                f"• **Personalized courses** recommend karta hai jo aapke gaps close karein\n"
                f"• **AI Assessment Generator** — PDF/PPTX upload karein, automatic MCQ quiz banega\n"
                f"• **Gyan AI Chatbot** (main hoon!) — training, statistics, platform navigation ke sawal ka jawab\n\n"
                f"📌 **Tabs:**\n"
                f"• **Dashboard** — skill gaps + recommended courses + quiz generator\n"
                f"• **My Courses** — active enrollments aur course progress\n"
                f"• **Progress** — competency radar chart aur achievements\n\n"
                f"Yeh platform iGOT Karmayogi ke FRAC framework se aligned hai — Mission Karmayogi ka hissa. 🇮🇳"
            )
        return (
            f"**MoSPI Skill Intelligence Platform** is an AI-powered learning tool "
            f"for government statistical officials.\n\n"
            f"🎯 **What this platform does:**\n"
            f"• Identifies your **skill gaps** — which competencies are below target for your job role\n"
            f"• Recommends **personalized courses** from iGOT Karmayogi to close those gaps\n"
            f"• **AI Assessment Generator** — upload any PDF/PPTX and get instant MCQ quizzes\n"
            f"• **Gyan AI Chatbot** (that's me!) — answers questions about training, statistics, and navigation\n\n"
            f"📌 **Three tabs:**\n"
            f"• **Dashboard** — skill gaps + AI-recommended courses + quiz generator\n"
            f"• **My Courses** — active enrollments and progress tracking\n"
            f"• **Progress** — competency radar chart and achievement history\n\n"
            f"Built for **Mission Karmayogi**, aligned with the iGOT FRAC competency framework. 🇮🇳"
        )

    # ── About MoSPI ──────────────────────────────────────────────────────────
    if intent == "about_mospi":
        if lang == "hi":
            return (
                f"**MoSPI (Ministry of Statistics and Programme Implementation)** "
                f"— Bharat Sarkar ka apex statistical body hai.\n\n"
                f"📊 **MoSPI ke kaam:**\n"
                f"• **GDP, CPI, IIP, WPI** jaise national statistics compile karna\n"
                f"• **NSO** (National Statistical Office) ko supervise karna\n"
                f"• Large surveys: **PLFS** (Labour Force), **HCES** (Household Consumer Expenditure)\n"
                f"• **SDG India Index** — UN Sustainable Development Goals ka tracking\n\n"
                f"🎓 **iGOT Karmayogi** — Mission Karmayogi ke under training platform:\n"
                f"• Government officials ki capacity building\n"
                f"• **FRAC framework** (Roles, Activities, Competencies) par based\n"
                f"• Yeh platform us training journey ka AI-powered hissa hai 🇮🇳"
            )
        return (
            f"**MoSPI (Ministry of Statistics and Programme Implementation)** "
            f"is India's apex body for the national statistical system.\n\n"
            f"📊 **What MoSPI does:**\n"
            f"• Compiles national statistics: **GDP, CPI, IIP, WPI**\n"
            f"• Oversees the **NSO** (National Statistical Office)\n"
            f"• Conducts large-scale surveys: **PLFS** (Labour Force), **HCES** (Consumer Expenditure)\n"
            f"• Tracks India's progress on the **SDG India Index**\n\n"
            f"🎓 **iGOT Karmayogi** — the learning platform under **Mission Karmayogi**:\n"
            f"• National capacity building for civil servants\n"
            f"• Based on the **FRAC framework** (Roles, Activities, Competencies)\n"
            f"• This platform is an AI-powered extension of that journey 🇮🇳"
        )

    # ── Statistics ───────────────────────────────────────────────────────────
    if intent == "statistics_gdp":
        return (
            "**GDP (Gross Domestic Product)** in India is compiled by the National "
            "Statistical Office (NSO) following the **System of National Accounts 2008 (SNA 2008)**.\n\n"
            "Three approaches:\n"
            "• **Expenditure method**: C + I + G + (X−M)\n"
            "• **Production method**: Sum of GVA across industries + taxes − subsidies\n"
            "• **Income method**: Compensation of employees + gross operating surplus\n\n"
            "India releases GDP quarterly, with two advance estimates. Base year: **2011-12**.\n\n"
            "Key agency: NSO under MoSPI. 🇮🇳"
        ) if lang == "en" else (
            "**GDP (सकल घरेलू उत्पाद)** — NSO dwara SNA 2008 ke anusar compute ki jati hai.\n\n"
            "Teen methods:\n"
            "• **Vyay Vidhi**: C + I + G + (X−M)\n"
            "• **Utpadan Vidhi**: GVA across industries + taxes − subsidies\n"
            "• **Aay Vidhi**: Shramik parishram + operating surplus\n\n"
            "Base year: **2011-12**. Quarterly estimates aati hain. NSO MoSPI ke under hai. 🇮🇳"
        )

    if intent == "statistics_cpi":
        return (
            "**CPI (Consumer Price Index)** measures average price changes for a basket of "
            "goods and services bought by households.\n\n"
            "In India:\n"
            "• **CPI-Combined**: Released monthly by MoSPI/NSO (base year 2012)\n"
            "• **Laspeyres formula** (fixed base-period weights)\n"
            "• Covers **299 items** across 6 groups: Food, Fuel, Housing, Clothing, Miscellaneous\n"
            "• Used by RBI as the **inflation targeting benchmark** (target: 4% ± 2%)"
        ) if lang == "en" else (
            "**CPI (उपभोक्ता मूल्य सूचकांक)** — households dwara kharide goods/services ki average price change.\n\n"
            "• Monthly NSO release, base year 2012\n"
            "• **Laspeyres formula** use hoti hai\n"
            "• 299 items, 6 groups: Food, Fuel, Housing, etc.\n"
            "• RBI inflation target: **4% ± 2%**"
        )

    if intent == "statistics_sampling":
        return (
            "**Sampling in official statistics** — selecting a subset to estimate population parameters.\n\n"
            "Key types used in NSSO surveys:\n"
            "• **Stratified Sampling**: Population divided into strata (urban/rural, states)\n"
            "• **Cluster Sampling**: Groups (villages/blocks) selected first\n"
            "• **Multi-stage Sampling**: Used in PLFS, HCES — districts → blocks → households\n\n"
            "NSSO uses a **rotating panel design** for many surveys to track changes over time."
        ) if lang == "en" else (
            "**Sampling (प्रतिदर्श)** — puri population ka chota hissa chunke anuman lagana.\n\n"
            "NSSO mein upyog hone wale types:\n"
            "• **Stratified**: Urban/rural, state ke hisab se\n"
            "• **Cluster**: Pehle groups chunte hain (gaon/blocks)\n"
            "• **Multi-stage**: PLFS, HCES mein — district → block → ghar\n\n"
            "NSSO **rotating panel design** use karta hai time-series tracking ke liye."
        )

    if intent == "statistics_frac":
        return (
            "**FRAC (Framework for Roles, Activities and Competencies)** is the Government "
            "of India's competency architecture for civil servants on iGOT Karmayogi.\n\n"
            "FRAC defines:\n"
            "• **Roles**: Job positions (Deputy Director, Field Investigator, etc.)\n"
            "• **Activities**: Key functions performed in a role\n"
            "• **Competencies**: Skills grouped as Behavioural (B), Domain (D), Functional (F)\n\n"
            "Your skill gap assessment here is **fully aligned with the FRAC dictionary**. 📋"
        ) if lang == "en" else (
            "**FRAC** — GoI ka civil servants ke liye competency framework, iGOT Karmayogi par.\n\n"
            "• **Roles**: Job positions\n"
            "• **Activities**: Role mein key functions\n"
            "• **Competencies**: Behavioural (B), Domain (D), Functional (F)\n\n"
            "Is platform ka skill gap assessment FRAC dictionary se aligned hai. 📋"
        )

    # ── Motivation ───────────────────────────────────────────────────────────
    if intent == "motivation":
        first_rec = recs[0].title if recs else "your first recommended course"
        if lang == "hi":
            return (
                f"Main samajhta hoon — upskilling aur kaam saath mein karna mushkil lagta hai. 💪\n\n"
                f"Lekin yaad rakhein: **India ke statistical system ko aap jaise dedicated officials ki zarurat hai.** "
                f"Aapka kaam GDP estimates se lekar poverty measurement tak — lakho logon ki lives affect karta hai.\n\n"
                f"Ek step ek time: **sirf 30 minutes roz** — kuch hafte mein results aane lagte hain.\n"
                f"Abhi start karein **{first_rec}** se! 🚀\n\n"
                f"Course **Dashboard tab → AI Recommended Learning Pathway** mein milega."
            )
        return (
            f"I understand — balancing work and upskilling is genuinely challenging. 💪\n\n"
            f"Remember: **India's statistical system depends on dedicated officials like you.** "
            f"Your data — from GDP estimates to poverty measurement — impacts millions of lives.\n\n"
            f"Just **30 minutes a day** will show results within weeks. "
            f"Start with **{first_rec}**! 🚀\n\n"
            f"Find it on the **Dashboard tab → AI Recommended Learning Pathway** section."
        )

    # ── Farewell ─────────────────────────────────────────────────────────────
    if intent == "farewell":
        if lang == "hi":
            return "Alvida! 🙏 Aapki learning mein safalta ki shubhkamanayein. **Jai Hind!** 🇮🇳"
        return "Goodbye! 👋 Best of luck with your learning journey. **Jai Hind!** 🇮🇳"

    # ── General / Unknown ────────────────────────────────────────────────────
    if lang == "hi":
        return random.choice([
            f"Yeh ek interesting sawaal hai! Main aapki madad kar sakta hoon:\n"
            f"• **Skill Gaps** — 'mera gap dikhao'\n"
            f"• **Courses** — 'course suggest karo'\n"
            f"• **Progress** — 'meri progress dikhao'\n"
            f"• **Navigation** — 'dashboard kahan hai', 'quiz kaise generate karu'\n"
            f"• **Statistics** — 'GDP kya hai', 'CPI explain karo'\n\n"
            f"Kya aap apna sawaal aur clearly pooch sakte hain?",
        ])
    return random.choice([
        f"Great question! I can help with:\n"
        f"• **Skill Gaps** — 'show my gaps'\n"
        f"• **Courses** — 'recommend me a course'\n"
        f"• **Progress** — 'show my progress'\n"
        f"• **Navigation** — 'where is the dashboard', 'how to generate a quiz'\n"
        f"• **Statistics** — 'explain GDP', 'what is CPI'\n\n"
        f"Could you rephrase your question?",
    ])


# =============================================================================
# TIER 2 — KEYWORD TEMPLATE FALLBACK (no dependencies)
# =============================================================================

def _generate_template_response(req: ChatRequest, lang: str, intent: str) -> str:
    """Original keyword/template engine — used when semantic model not loaded."""
    uid       = req.user_id
    role      = req.job_role or "Statistical Official"
    dept      = req.department or "MoSPI"
    gaps      = req.skill_gaps
    recs      = req.recommendations
    top_gap   = _top_gap(gaps)
    active_gaps = [g for g in gaps if g.gapScore > 0]
    msg_lower = req.message.lower()

    if intent in ("greeting", "hindi_greeting"):
        if lang == "hi":
            return (
                f"Namaste! 🙏 Main Gyan hoon — aapka MoSPI AI Training Assistant.\n\n"
                f"Aap {role} hain {dept} mein. Aaj main aapki kya madad kar sakta hoon?"
            )
        return (
            f"Hello! 👋 I'm **Gyan**, your MoSPI AI Training Assistant.\n\n"
            f"You're a **{role}** in {dept}. How can I help you today?"
        )

    if intent == "farewell":
        if lang == "hi":
            return "Alvida! 🙏 **Jai Hind!** 🇮🇳"
        return "Goodbye! 👋 **Jai Hind!** 🇮🇳"

    if intent == "skill_gaps":
        gap_text = _fmt_gaps(gaps, lang)
        if lang == "hi":
            return (
                f"Aapke skill gaps:\n\n{gap_text}\n\n"
                + (f"Sabse bada gap: **{top_gap.skillName}**" if top_gap else "")
            )
        return (
            f"Your skill gaps:\n\n{gap_text}\n\n"
            + (f"Biggest gap: **{top_gap.skillName}**" if top_gap else "")
        )

    if intent == "recommend":
        rec_text = _fmt_recs(recs, lang)
        return (
            f"Recommended courses:\n\n{rec_text}"
            if lang == "en" else
            f"Recommended courses:\n\n{rec_text}"
        )

    if intent == "progress":
        met = len(gaps) - len(active_gaps)
        total = len(gaps)
        pct = round((met / total * 100) if total else 0)
        if lang == "hi":
            return f"Progress: ✅ {met}/{total} competencies target par ({pct}%)."
        return f"Progress: ✅ {met}/{total} competencies at target ({pct}%)."

    if intent == "platform_help":
        if lang == "hi":
            return (
                "**Platform tabs:**\n\n"
                "📊 **Dashboard** → Skill gaps + AI Recommendations + Quiz Generator\n"
                "📚 **My Courses** → Active enrollments\n"
                "📈 **Progress** → Radar chart + Achievements\n"
            )
        return (
            "**Platform tabs:**\n\n"
            "📊 **Dashboard** → Skill gaps + AI Recommendations + Quiz Generator\n"
            "📚 **My Courses** → Active enrollments\n"
            "📈 **Progress** → Radar chart + Achievements\n"
        )

    # Statistics quick-hit
    stat_kw = {"gdp": "GDP", "cpi": "CPI", "sampling": "Sampling", "frac": "FRAC"}
    for kw, label in stat_kw.items():
        if kw in msg_lower:
            return f"You asked about **{label}**. Please ask Gyan via the AI-powered tier for a detailed answer."

    fallback_en = (
        f"I'm Gyan — ask me about your skill gaps, courses, platform navigation, "
        f"or statistics topics (GDP, CPI, FRAC, Sampling). 🎓"
    )
    fallback_hi = (
        f"Main Gyan hoon — apne skill gaps, courses, ya platform navigation ke baare mein poochiye. 🎓"
    )
    return fallback_hi if lang == "hi" else fallback_en


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Multilingual AI Learning Assistant — Gyan (ज्ञान).

    Tier 1: Semantic engine (sentence-transformers — Render-deployable).
      - Classifies intent via cosine similarity
      - Answers profile stats, navigation, skill gaps, recommendations directly
      - Engine label: "semantic"

    Tier 2: Keyword template fallback (zero dependencies).
      - Activates if semantic model is not loaded
      - Engine label: "template"

    Tier 3 (DISCONNECTED): Ollama RAG — available in ai/rag_engine.py
      - NOT called from here in production
      - Search REVERT_OLLAMA to re-enable
    """
    lang   = detect_language(req.message)

    # ── TIER 1: Semantic Engine ───────────────────────────────────────────────
    try:
        from ai.semantic_engine import classify_intent, is_semantic_engine_ready

        if is_semantic_engine_ready():
            intent, confidence = classify_intent(req.message)
            logger.info(
                "[Gyan/semantic] intent=%s confidence=%.3f query=%r",
                intent, confidence, req.message
            )

            # Confidence threshold: use semantic handler if ≥ 0.40
            # If below, still try it but note low confidence
            reply = _handle_semantic(intent, req, lang)
            return ChatResponse(reply=reply, detected_language=lang, engine="semantic")
        else:
            logger.info("[Gyan] Semantic engine not ready → falling back to templates")

    except Exception as exc:
        logger.warning("[Gyan] Semantic engine error, using template fallback: %s", exc)

    # ── TIER 2: Keyword Template Fallback ────────────────────────────────────
    intent = detect_intent_keyword(req.message)
    reply  = _generate_template_response(req, lang, intent)
    return ChatResponse(reply=reply, detected_language=lang, engine="template")

    # ── TIER 3: Ollama RAG (DISCONNECTED — REVERT_OLLAMA) ───────────────────
    # To re-enable Ollama as Tier 1, uncomment the block below and comment out
    # the "TIER 1: Semantic Engine" block above.
    #
    # try:
    #     from ai.rag_engine import generate_chat_response, is_ollama_available
    #     if is_ollama_available():
    #         gaps_dicts = [{...} for g in req.skill_gaps]
    #         recs_dicts = [{...} for r in req.recommendations]
    #         history_dicts = [{"role": h.role, "content": h.content} for h in req.history]
    #         ai_reply = await generate_chat_response(
    #             query=req.message, history=history_dicts,
    #             job_role=req.job_role or "Statistical Official",
    #             department=req.department or "MoSPI",
    #             skill_gaps=gaps_dicts, recommendations=recs_dicts,
    #             language_hint=lang,
    #         )
    #         return ChatResponse(reply=ai_reply, detected_language=lang, engine="rag_ollama")
    # except Exception as exc:
    #     logger.warning("[Gyan] Ollama RAG error: %s", exc)


@router.get("/chat/mode")
async def chat_mode():
    """
    Returns which response engine is currently active.
    Frontend can use this to show 'AI Powered' / 'Standard Mode' badge.
    """
    try:
        from ai.semantic_engine import is_semantic_engine_ready
        semantic_ok = is_semantic_engine_ready()
        return {
            "engine":          "semantic" if semantic_ok else "template",
            "semantic_status": "ready" if semantic_ok else "not_loaded",
            "model":           "all-MiniLM-L6-v2",
            "ollama_status":   "disconnected (Tier 3 — not in hot path)",
            "description": (
                "Gyan is running in Semantic AI mode (sentence-transformers intent classifier)"
                if semantic_ok else
                "Gyan is running in Standard mode (keyword template engine)"
            ),
        }
    except Exception:
        return {"engine": "template", "semantic_status": "error"}
