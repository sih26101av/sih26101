"""
FILE: routers/chatbot.py

Multilingual AI Learning Assistant — Gyan (ज्ञान)
Archit Shukla | MoSPI Skill Intelligence Platform | SIH 2026

Smart context-aware chatbot. Reads the user's live skill gap & recommendation
data and generates intelligent, personalized responses via keyword-intent
matching + MoSPI-grounded response templates.

Architecture is LLM-ready: swap _generate_response() with a Gemini/OpenAI
call and nothing else needs to change.
"""

import re
import random
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

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
    # Context injected from frontend (already fetched, no extra API call needed)
    job_role: Optional[str] = "Statistical Official"
    department: Optional[str] = "MoSPI"
    skill_gaps: List[SkillGapContext] = []
    recommendations: List[RecommendationContext] = []

class ChatResponse(BaseModel):
    reply: str
    detected_language: str  # "hi" | "en"


# =============================================================================
# LANGUAGE DETECTION
# =============================================================================

# Hindi-indicator patterns (Devanagari, common Hinglish keywords)
_HINDI_DEVANAGARI = re.compile(r'[\u0900-\u097F]')
_HINGLISH_WORDS = {
    'kya', 'kaun', 'kaise', 'mujhe', 'mera', 'meri', 'mein', 'hai', 'hain',
    'nahi', 'batao', 'bolo', 'karo', 'lena', 'chahiye', 'course', 'acha',
    'theek', 'samjhao', 'kab', 'kyun', 'kitna', 'kitne', 'sikho', 'padhna',
    'seekhna', 'lagta', 'zyada', 'thoda', 'bahut', 'sir', 'madam', 'help',
    'kuch', 'sab', 'jo', 'woh', 'abhi', 'aaj', 'kal'
}

def detect_language(text: str) -> str:
    if _HINDI_DEVANAGARI.search(text):
        return "hi"
    words = set(text.lower().split())
    if len(words & _HINGLISH_WORDS) >= 1:
        return "hi"
    return "en"


# =============================================================================
# INTENT DETECTION
# =============================================================================

_INTENTS = {
    "greeting":       r'\b(hi|hello|hey|namaste|namaskar|hie|good\s*(morning|evening|afternoon)|sup)\b',
    "skill_gaps":     r'\b(gap|gaps|skill\s*gap|missing|weak|improve|kya\s*gap|kitna\s*gap|deficiency|lacking|kahan\s*weak)\b',
    "recommend":      r'\b(recommend|suggest|course|courses|kya\s*padhu|kya\s*lu|kya\s*seekhu|path|pathway|next|start|begin|enroll|kaunsa|which)\b',
    "progress":       r'\b(progress|how\s*am\s*i|doing|status|achievement|score|result|kitna\s*seekha|kahan\s*tak)\b',
    "statistics":     r'\b(gdp|cpi|wpi|sampling|survey|national\s*accounts|sna|frac|nsso|plfs|census|econometrics|regression|time\s*series|price\s*index|imf|sdmx)\b',
    "platform_help":  r'\b(how\s*to|kaise\s*karu|navigate|use|igot|platform|login|enroll|karmayogi|where\s*can\s*i|help|assist)\b',
    "hindi_greeting": r'\b(namaste|namaskar|pranam|kaise\s*(ho|hain)|sab\s*(theek|thik))\b',
    "farewell":       r'\b(bye|goodbye|alvida|shukriya|thanks|thank\s*you|dhanyavad|dhanyabad|ok\s*bye|acha\s*bye)\b',
    "motivation":     r'\b(motivat|difficult|hard|tough|mushkil|give\s*up|hopeless|boring|struggle)\b',
}

def detect_intent(text: str) -> str:
    lower = text.lower()
    for intent, pattern in _INTENTS.items():
        if re.search(pattern, lower):
            return intent
    return "general"


# =============================================================================
# RESPONSE GENERATOR (Context-Aware Templates)
# =============================================================================

def _fmt_gaps(gaps: List[SkillGapContext], lang: str) -> str:
    active = [g for g in gaps if g.gapScore > 0]
    if not active:
        if lang == "hi":
            return "Aapke sabhi competencies target level par hain! Badhai ho! 🎉"
        return "All your competencies are at target level! 🎉"
    lines = []
    for g in sorted(active, key=lambda x: -x.gapScore)[:4]:
        if lang == "hi":
            lines.append(f"• **{g.skillName}**: Level {g.currentLevel} → {g.targetLevel} chahiye (Gap: {g.gapScore})")
        else:
            lines.append(f"• **{g.skillName}**: Level {g.currentLevel} → {g.targetLevel} needed (Gap: {g.gapScore})")
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

def _generate_response(req: ChatRequest, lang: str, intent: str) -> str:
    uid       = req.user_id
    role      = req.job_role or "Statistical Official"
    dept      = req.department or "MoSPI"
    gaps      = req.skill_gaps
    recs      = req.recommendations
    top_gap   = _top_gap(gaps)
    active_gaps = [g for g in gaps if g.gapScore > 0]
    msg_lower = req.message.lower()

    # ── GREETING ──────────────────────────────────────────────────────────────
    if intent in ("greeting", "hindi_greeting"):
        if lang == "hi":
            greetings = [
                f"Namaste! 🙏 Main Gyan hoon — aapka MoSPI AI Training Assistant.\n\nMain aapki training journey mein madad ke liye yahan hoon, **{uid}**. Aap {role} hain {dept} mein.\n\nAap mujhse pooch sakte hain:\n• Apne skill gaps ke baare mein\n• Recommended courses ke baare mein\n• Statistics topics samjhane ke liye\n\nAaj main aapki kya madad kar sakta hoon?",
                f"Namaskar! 🙏 Aapka swagat hai MoSPI Skill Intelligence Platform par.\n\nMujhe pta hai aap {role} hain. Kya aap apni learning journey shuru karna chahte hain? Main recommend kar sakta hoon kahan se start karein!",
            ]
        else:
            greetings = [
                f"Hello! 👋 I'm **Gyan**, your MoSPI AI Training Assistant.\n\nI can see you're a **{role}** in {dept}. I'm here to guide your personalized learning journey.\n\nAsk me about:\n• Your skill gaps and how to close them\n• Which courses to take next\n• Statistical concepts and MoSPI topics\n\nHow can I help you today?",
                f"Hi there! I'm Gyan, your AI learning companion on the MoSPI platform. 🎓\n\nYou have **{len(active_gaps)} active skill gap(s)** I can help you work through. What would you like to explore?",
            ]
        return random.choice(greetings)

    # ── FAREWELL ──────────────────────────────────────────────────────────────
    if intent == "farewell":
        if lang == "hi":
            return f"Alvida! 🙏 Aapki learning mein safalta ki shubhkamanayein.\n\nYaad rakhein — jab bhi koi sawaal ho, main yahan hoon. **Jai Hind!** 🇮🇳"
        return f"Goodbye! 👋 Best of luck with your learning journey.\n\nRemember, I'm always here when you need guidance. **Jai Hind!** 🇮🇳"

    # ── SKILL GAPS ────────────────────────────────────────────────────────────
    if intent == "skill_gaps":
        gap_text = _fmt_gaps(gaps, lang)
        if lang == "hi":
            if not active_gaps:
                return f"Mashallah! 🎉 Aapke **{len(gaps)} competencies** sab target level par hain.\n\nAap bahut accha kar rahe hain apni role mein '{role}'!"
            return (
                f"Aapke current skill gaps yeh hain ({role} ke liye):\n\n"
                f"{gap_text}\n\n"
                f"Sabse bada gap **{top_gap.skillName}** mein hai — {top_gap.gapScore} level ka farq hai. "
                f"Kya main is gap ko close karne ke liye courses suggest karun?"
            )
        else:
            if not active_gaps:
                return f"Excellent! 🎉 All **{len(gaps)} competencies** are at or above target level for your role as {role}. Keep it up!"
            return (
                f"Here are your active skill gaps for the **{role}** role:\n\n"
                f"{gap_text}\n\n"
                f"Your biggest priority is **{top_gap.skillName}** with a gap of {top_gap.gapScore} level(s). "
                f"Want me to recommend the best courses to close this gap?"
            )

    # ── RECOMMENDATIONS ───────────────────────────────────────────────────────
    if intent == "recommend":
        rec_text = _fmt_recs(recs, lang)
        if lang == "hi":
            if not recs:
                return "Abhi aapke liye recommendations generate nahi hui hain. Apna dashboard refresh karke dekhein."
            priority_reason = f"**{top_gap.skillName}** mein {top_gap.gapScore}-level gap" if top_gap else "aapke role requirements"
            return (
                f"Aapke liye personalized learning pathway, {priority_reason} ke basis par:\n\n"
                f"{rec_text}\n\n"
                f"**{recs[0].title}** se shuru karna best rahega — kyunki {recs[0].matchReason.lower()}"
            )
        else:
            if not recs:
                return "No recommendations found yet. Try refreshing your dashboard."
            priority_reason = f"your {top_gap.gapScore}-level gap in **{top_gap.skillName}**" if top_gap else "your role requirements"
            return (
                f"Based on {priority_reason}, here's your personalized learning pathway:\n\n"
                f"{rec_text}\n\n"
                f"I recommend starting with **{recs[0].title}** because {recs[0].matchReason.lower()}"
            )

    # ── PROGRESS ──────────────────────────────────────────────────────────────
    if intent == "progress":
        met = len(gaps) - len(active_gaps)
        total = len(gaps)
        pct = round((met / total * 100) if total else 0)
        if lang == "hi":
            return (
                f"Aapki progress summary ({role}):\n\n"
                f"✅ **{met}/{total}** competencies target level par hain ({pct}%)\n"
                f"⚠️ **{len(active_gaps)}** gaps abhi bhi close karne hain\n\n"
                f"{'Bahut badhiya! Aap sahi raaste par hain. 👏' if pct >= 60 else 'Abhi shuru karte hain — recommended courses follow karein aur gaps band karte jayein!'}"
            )
        else:
            return (
                f"Your learning progress as **{role}**:\n\n"
                f"✅ **{met}/{total}** competencies at target level ({pct}% complete)\n"
                f"⚠️ **{len(active_gaps)}** gap(s) still to close\n\n"
                f"{'Great progress! You\'re well on track. 👏' if pct >= 60 else 'Keep going — follow your recommended courses to close the remaining gaps!'}"
            )

    # ── STATISTICS TOPICS ─────────────────────────────────────────────────────
    stat_answers = {
        "gdp": {
            "en": "**GDP (Gross Domestic Product)** in India is compiled by the National Statistical Office (NSO) following the **System of National Accounts 2008 (SNA 2008)**.\n\nKey approaches:\n• **Expenditure method**: C + I + G + (X−M)\n• **Production method**: Sum of GVA across industries + taxes − subsidies\n• **Income method**: Compensation of employees + gross operating surplus\n\nIndia releases GDP estimates quarterly with two advance estimates. The base year is currently 2011-12.",
            "hi": "**GDP (सकल घरेलू उत्पाद)** — Bharat mein NSO dwara SNA 2008 ke anusar compute ki jati hai.\n\nTeen methods:\n• **Vyay Vidhi** (Expenditure): C + I + G + (X−M)\n• **Utpadan Vidhi** (Production): Sabhi industries ka GVA + taxes − subsidies\n• **Aay Vidhi** (Income): Shramik parishram + operating surplus\n\nAnglish mein GDP ki quarterly estimates aati hain. Base year 2011-12 hai."
        },
        "sampling": {
            "en": "**Sampling in official statistics** involves selecting a subset of a population to estimate parameters for the whole.\n\nKey types used in NSSO surveys:\n• **Stratified Sampling**: Population divided into strata (urban/rural, states)\n• **Cluster Sampling**: Groups (villages/blocks) selected first\n• **Multi-stage Sampling**: Used in PLFS, HCES — districts → blocks → households\n\nThe **NSSO** uses a rotating panel design for many surveys to track changes over time.",
            "hi": "**Sampling (प्रतिदर्श)** — Puri jansankhya ka ek chota hissa chunke puri population ka anuman lagana.\n\nNSSO mein upyog hone wale types:\n• **Stratified**: Urban/rural, state ke hisab se strata\n• **Cluster**: Pehle groups (gaon/blocks) chunte hain\n• **Multi-stage**: PLFS, HCES mein — district → block → ghar\n\nNSSO rotating panel design use karta hai time-series tracking ke liye."
        },
        "cpi": {
            "en": "**CPI (Consumer Price Index)** measures average price changes for a basket of goods and services bought by households.\n\nIn India:\n• **CPI-Combined**: Released monthly by MoSPI/NSO (base year 2012)\n• **CPI-Rural / CPI-Urban**: Separate series\n• Uses **Laspeyres formula** (fixed base-period weights)\n• Covers 299 items across 6 groups: Food, Fuel, Housing, Clothing, Miscellaneous\n\nCPI is used by RBI as the **inflation targeting benchmark** (target: 4% ± 2%).",
            "hi": "**CPI (उपभोक्ता मूल्य सूचकांक)** — Households dwara kharide jaane wale goods aur services ki average price change measure karta hai.\n\nBharat mein:\n• **CPI-Combined**: Monthly NSO release karta hai (base year 2012)\n• **Laspeyres formula** use hoti hai\n• 299 items, 6 groups: Food, Fuel, Housing, etc.\n\nRBI CPI ko inflation targeting benchmark maan ta hai — 4% ± 2%."
        },
        "frac": {
            "en": "**FRAC (Framework for Roles, Activities and Competencies)** is the Government of India's competency architecture for civil servants on iGOT Karmayogi.\n\nFRAC defines:\n• **Roles**: Job positions (Deputy Director, Field Investigator, etc.)\n• **Activities**: Key functions performed in a role\n• **Competencies**: Skills needed — grouped as Behavioural (B), Domain (D), Functional (F)\n\nYour skill gap assessment in this platform is fully aligned with the FRAC dictionary.",
            "hi": "**FRAC (Framework for Roles, Activities and Competencies)** — GoI ka civil servants ke liye competency framework hai, iGOT Karmayogi par based.\n\nFRAC mein teen cheezein hain:\n• **Roles**: Job positions (Deputy Director, Field Investigator, etc.)\n• **Activities**: Role mein ki jaane wali key functions\n• **Competencies**: Zaruri skills — Behavioural (B), Domain (D), Functional (F)\n\nIs platform par aapka skill gap assessment FRAC dictionary se bilkul aligned hai."
        },
    }
    for keyword, answers in stat_answers.items():
        if keyword in msg_lower:
            return answers[lang]

    # ── PLATFORM HELP ─────────────────────────────────────────────────────────
    if intent == "platform_help":
        if lang == "hi":
            return (
                "**MoSPI Skill Intelligence Platform** ka use kaise karein:\n\n"
                "📊 **Dashboard Tab** → Apne skill gaps aur recommended courses dekhein\n"
                "📚 **My Courses Tab** → Active enrollments aur progress track karein\n"
                "📈 **Progress Tab** → Achievements aur competency growth dekhein\n"
                "🤖 **AI Generator** (right panel) → PDF upload karke MCQs generate karein\n\n"
                "iGOT Karmayogi par enroll karne ke liye apne recommended courses mein se kisi bhi course ka naam copy karein aur iGOT portal par search karein."
            )
        else:
            return (
                "**How to navigate the MoSPI Skill Intelligence Platform:**\n\n"
                "📊 **Dashboard Tab** → View your skill gaps and AI-recommended courses\n"
                "📚 **My Courses Tab** → Track active enrollments and progress\n"
                "📈 **Progress Tab** → See achievements and competency growth\n"
                "🤖 **AI Generator** (right panel) → Upload a PDF to generate MCQ quizzes\n\n"
                "To enroll in a course on iGOT Karmayogi, copy the course title from your recommendations and search it on the iGOT portal."
            )

    # ── MOTIVATION ────────────────────────────────────────────────────────────
    if intent == "motivation":
        if lang == "hi":
            return (
                "Main samajhta hoon — upskilling aur kaam saath mein karna mushkil lagta hai. 💪\n\n"
                "Lekin yaad rakhein: **India ke statistical system ko aap jaise dedicated officials ki zarurat hai.** "
                "Aapka kaam GDP estimates se lekar poverty measurement tak — lakho logon ki lives affect karta hai.\n\n"
                "Ek step ek time: **sirf 30 minutes roz** ek course par — kuch hafte mein hi results dikhne lagte hain. "
                f"Abhi start karein **{recs[0].title if recs else 'aapka pehla recommended course'}** se! 🚀"
            )
        else:
            return (
                "I understand — balancing work and upskilling is genuinely challenging. 💪\n\n"
                "But remember: **India's statistical system depends on dedicated officials like you.** "
                "The data you produce — from GDP estimates to poverty measurement — impacts millions of lives.\n\n"
                "One step at a time: just **30 minutes a day** on a course will show results within weeks. "
                f"Start now with **{recs[0].title if recs else 'your first recommended course'}**! 🚀"
            )

    # ── GENERAL FALLBACK ──────────────────────────────────────────────────────
    fallbacks_en = [
        f"That's a great question! As a **{role}** in {dept}, your learning focus should align with MoSPI's capacity building goals.\n\nCould you rephrase your question or ask me about:\n• Your specific skill gaps\n• Course recommendations\n• Statistical concepts (GDP, CPI, Sampling, FRAC)\n• How to use this platform",
        f"I'm Gyan, your MoSPI AI assistant — I'm best at helping with training, skill gaps, and statistics topics. 🎓\n\nTry asking: *\"What courses should I take?\"* or *\"Explain GDP calculation\"*",
    ]
    fallbacks_hi = [
        f"Yeh ek achha sawaal hai! Main aapki madad kar sakta hoon:\n• Aapke skill gaps ke baare mein\n• Kaunsa course lena chahiye\n• Statistical topics (GDP, CPI, Sampling, FRAC)\n• Platform use kaise karein\n\nKya aap apna sawaal aur clearly pooch sakte hain?",
        f"Main Gyan hoon — aapka MoSPI AI assistant. Training aur statistics ke topics par main best hoon! 🎓\n\nPoochiye: *\"Mujhe kaunsa course lena chahiye?\"* ya *\"GDP kaise calculate hoti hai?\"*",
    ]
    return random.choice(fallbacks_hi if lang == "hi" else fallbacks_en)


# =============================================================================
# ENDPOINT
# =============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Multilingual AI Learning Assistant endpoint.
    Detects language, infers intent, and returns a context-aware response
    grounded in the user's live skill gap and recommendation data.
    """
    lang   = detect_language(req.message)
    intent = detect_intent(req.message)
    reply  = _generate_response(req, lang, intent)

    return ChatResponse(reply=reply, detected_language=lang)
