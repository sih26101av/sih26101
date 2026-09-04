/**
 * FILE: src/services/chatApi.ts
 *
 * Chatbot API service for Gyan — MoSPI AI Learning Assistant.
 * Archit Shukla | SIH 2026
 *
 * Architecture:
 *  1. Tries POST /api/v1/chat (backend)
 *  2. On ANY failure → falls back to client-side response engine
 *     (so the chatbot ALWAYS works, even without the backend running)
 */

import type { SkillGapEntry, CourseRecommendation } from '../types/domain';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface ChatMessage {
  id: string;
  role: 'user' | 'model';
  content: string;
  timestamp: Date;
  detectedLanguage?: 'en' | 'hi';
}

export interface NavigateAction {
  type: 'scroll' | 'tab' | 'modal';
  target: string;          // e.g. '#features', 'my-courses', 'login'
  label: string;           // human-readable, e.g. 'Features section'
}

interface ChatApiPayload {
  user_id: string;
  message: string;
  history: { role: string; content: string }[];
  job_role: string;
  department: string;
  full_name?: string;
  gov_id?: string;
  context?: string;
  skill_gaps: {
    skillName: string;
    domain: string;
    currentLevel: number;
    targetLevel: number;
    gapScore: number;
  }[];
  recommendations: {
    title: string;
    provider: string;
    durationHours: number;
    matchReason: string;
  }[];
}

// ─── Language Detection ───────────────────────────────────────────────────────

const HINGLISH_WORDS = new Set([
  'kya', 'kaun', 'kaise', 'mujhe', 'mera', 'meri', 'mein', 'hai', 'hain',
  'nahi', 'batao', 'bolo', 'karo', 'lena', 'chahiye', 'acha', 'theek',
  'samjhao', 'kab', 'kyun', 'kitna', 'kitne', 'sikho', 'padhna', 'seekhna',
  'lagta', 'zyada', 'thoda', 'bahut', 'kuch', 'sab', 'jo', 'woh', 'abhi',
  'aaj', 'kal', 'namaste', 'namaskar',
]);

function detectLanguage(text: string): 'en' | 'hi' {
  if (/[\u0900-\u097F]/.test(text)) return 'hi';
  const words = new Set(text.toLowerCase().split(/\s+/));
  if ([...words].some(w => HINGLISH_WORDS.has(w))) return 'hi';
  return 'en';
}

// ─── Intent Detection ─────────────────────────────────────────────────────────

const INTENT_PATTERNS: Record<string, RegExp> = {
  greeting:      /\b(hi|hello|hey|namaste|namaskar|hie|good\s*(morning|evening|afternoon)|sup)\b/i,
  skill_gaps:    /\b(gap|gaps|skill\s*gap|missing|weak|improve|deficiency|lacking)\b/i,
  recommend:     /\b(recommend|suggest|course|courses|path|pathway|next|start|begin|enroll|which|kaunsa|padhu|seekhu|lu)\b/i,
  progress:      /\b(progress|how\s*am\s*i|doing|status|achievement|score|result)\b/i,
  statistics:    /\b(gdp|cpi|wpi|sampling|survey|national\s*accounts|sna|frac|nsso|plfs|census|regression|time\s*series|imf)\b/i,
  platform_help: /\b(how\s*to|navigate|use|igot|platform|login|karmayogi|where\s*can\s*i|help|assist)\b/i,
  farewell:      /\b(bye|goodbye|alvida|shukriya|thanks|thank\s*you|dhanyavad|ok\s*bye)\b/i,
  motivation:    /\b(motivat|difficult|hard|tough|mushkil|give\s*up|hopeless|boring|struggle)\b/i,
};

function detectIntent(text: string): string {
  const lower = text.toLowerCase();
  for (const [intent, pattern] of Object.entries(INTENT_PATTERNS)) {
    if (pattern.test(lower)) return intent;
  }
  return 'general';
}

// ─── Client-Side Response Engine (Devanagari Hindi + English) ────────────────

function pick<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

function fmtGaps(gaps: SkillGapEntry[], lang: 'en' | 'hi'): string {
  const active = gaps.filter(g => g.gap > 0).sort((a, b) => b.gap - a.gap).slice(0, 4);
  if (!active.length) {
    return lang === 'hi'
      ? 'आपकी सभी competencies target level पर हैं! 🎉'
      : 'All competencies are at target level! 🎉';
  }
  return active.map(g =>
    lang === 'hi'
      ? `• **${g.competency.skillName}**: Level ${g.currentLevel} → ${g.requiredLevel} चाहिए (Gap: ${g.gap})`
      : `• **${g.competency.skillName}**: Level ${g.currentLevel} → ${g.requiredLevel} needed (Gap: ${g.gap})`
  ).join('\n');
}

function fmtRecs(recs: CourseRecommendation[], lang: 'en' | 'hi', n = 3): string {
  if (!recs.length) {
    return lang === 'hi' ? 'अभी कोई recommendations उपलब्ध नहीं हैं।' : 'No recommendations available right now.';
  }
  return recs.slice(0, n).map((r, i) =>
    lang === 'hi'
      ? `${i + 1}. **${r.course.title}** (${r.course.source}, ${Math.round(r.course.durationHours)}h)`
      : `${i + 1}. **${r.course.title}** — ${r.course.source} | ${Math.round(r.course.durationHours)}h`
  ).join('\n');
}

function buildLocalReply(
  intent: string,
  lang: 'en' | 'hi',
  officialId: string,
  jobRole: string,
  department: string,
  skillGaps: SkillGapEntry[],
  recommendations: CourseRecommendation[],
  messageText: string
): string {
  const activeGaps = skillGaps.filter(g => g.gap > 0);
  const topGap = [...activeGaps].sort((a, b) => b.gap - a.gap)[0];
  const met = skillGaps.length - activeGaps.length;
  const pct = skillGaps.length ? Math.round((met / skillGaps.length) * 100) : 0;
  const msgLow = messageText.toLowerCase();

  // ── GREETING ────────────────────────────────────────────────────────────────
  if (intent === 'greeting') {
    return lang === 'hi'
      ? pick([
          `नमस्ते! 🙏 मैं **ज्ञान** हूँ — आपका MoSPI AI प्रशिक्षण सहायक।\n\n**${officialId}** जी, आप **${jobRole}** के पद पर **${department}** में कार्यरत हैं।\n\nआप मुझसे पूछ सकते हैं:\n• अपने skill gaps के बारे में\n• अनुशंसित courses के बारे में\n• GDP, CPI, FRAC जैसे सांख्यिकी विषयों के बारे में\n\nआज मैं आपकी क्या सहायता कर सकता हूँ?`,
          `नमस्कार! 🙏 MoSPI Skill Intelligence Platform पर आपका स्वागत है।\n\nमैं देख सकता हूँ कि आपके पास **${activeGaps.length} active skill gap${activeGaps.length !== 1 ? 's' : ''}** हैं। आइए मिलकर इन्हें दूर करें!`,
        ])
      : pick([
          `Hello! 👋 I'm **Gyan**, your MoSPI AI Training Assistant.\n\nI can see you're a **${jobRole}** in ${department}. I'm here to guide your personalized learning journey.\n\nAsk me about:\n• Your skill gaps and how to close them\n• Which courses to take next\n• Statistical concepts (GDP, CPI, FRAC, Sampling)\n\nHow can I help you today?`,
          `Hi there! I'm Gyan 🎓 — your AI learning companion on the MoSPI platform.\n\nYou have **${activeGaps.length} active skill gap(s)** I can help you work through. What would you like to explore?`,
        ]);
  }

  // ── FAREWELL ─────────────────────────────────────────────────────────────────
  if (intent === 'farewell') {
    return lang === 'hi'
      ? `अलविदा! 🙏 आपकी learning में सफलता की शुभकामनाएँ।\n\nयाद रखें — जब भी कोई प्रश्न हो, मैं यहाँ हूँ। **जय हिन्द!** 🇮🇳`
      : `Goodbye! 👋 Best of luck with your learning journey.\n\nI'm always here when you need guidance. **Jai Hind!** 🇮🇳`;
  }

  // ── SKILL GAPS ───────────────────────────────────────────────────────────────
  if (intent === 'skill_gaps') {
    const gapText = fmtGaps(skillGaps, lang);
    return lang === 'hi'
      ? activeGaps.length === 0
        ? `शाबाश! 🎉 आपकी सभी **${skillGaps.length} competencies** target level पर हैं।\n\nआप अपनी role '**${jobRole}**' में बहुत अच्छा काम कर रहे हैं!`
        : `**${jobRole}** की role के लिए आपके वर्तमान skill gaps:\n\n${gapText}\n\nसबसे बड़ी कमी **${topGap.competency.skillName}** में है — ${topGap.gap} level का अंतर है।\nक्या मैं इस gap को दूर करने के लिए courses suggest करूँ?`
      : activeGaps.length === 0
        ? `Excellent! 🎉 All **${skillGaps.length} competencies** are at or above target level for **${jobRole}**. Keep it up!`
        : `Here are your active skill gaps for the **${jobRole}** role:\n\n${gapText}\n\nYour biggest priority is **${topGap.competency.skillName}** with a gap of ${topGap.gap} level(s).\nWant me to recommend courses to close this gap?`;
  }

  // ── RECOMMENDATIONS ──────────────────────────────────────────────────────────
  if (intent === 'recommend') {
    const recText = fmtRecs(recommendations, lang);
    return lang === 'hi'
      ? recommendations.length === 0
        ? 'अभी आपके लिए recommendations generate नहीं हुई हैं। अपना dashboard refresh करके देखें।'
        : `${topGap ? `**${topGap.competency.skillName}** में ${topGap.gap}-level gap` : 'आपकी role requirements'} के आधार पर आपका personalized learning pathway:\n\n${recText}\n\n**${recommendations[0].course.title}** से शुरू करना सबसे उचित रहेगा।`
      : recommendations.length === 0
        ? 'No recommendations found yet. Try refreshing your dashboard.'
        : `Based on ${topGap ? `your ${topGap.gap}-level gap in **${topGap.competency.skillName}**` : 'your role requirements'}, here's your personalized learning pathway:\n\n${recText}\n\nI recommend starting with **${recommendations[0].course.title}** — it directly addresses your highest priority gap.`;
  }

  // ── PROGRESS ─────────────────────────────────────────────────────────────────
  if (intent === 'progress') {
    return lang === 'hi'
      ? `**${jobRole}** की role में आपकी progress:\n\n✅ **${met}/${skillGaps.length}** competencies target level पर हैं (${pct}%)\n⚠️ **${activeGaps.length}** gap${activeGaps.length !== 1 ? 's' : ''} अभी भी बंद करने हैं\n\n${pct >= 60 ? 'बहुत बढ़िया! आप सही रास्ते पर हैं। 👏' : 'अभी शुरू करें — recommended courses follow करें और gaps बंद करते जाएँ!'}`
      : `Your learning progress as **${jobRole}**:\n\n✅ **${met}/${skillGaps.length}** competencies at target level (${pct}% complete)\n⚠️ **${activeGaps.length}** gap(s) still to close\n\n${pct >= 60 ? "Great progress! You're well on track. 👏" : 'Keep going — follow your recommended courses to close the remaining gaps!'}`;
  }

  // ── STATISTICS TOPICS ────────────────────────────────────────────────────────
  const statDb: Record<string, Record<'en' | 'hi', string>> = {
    gdp: {
      en: '**GDP (Gross Domestic Product)** in India is compiled by the National Statistical Office (NSO) following **SNA 2008**.\n\nKey approaches:\n• **Expenditure**: C + I + G + (X−M)\n• **Production**: Sum of GVA + taxes − subsidies\n• **Income**: Compensation of employees + operating surplus\n\nIndia releases GDP estimates quarterly. Current base year: **2011-12**.',
      hi: '**GDP (सकल घरेलू उत्पाद)** — भारत में NSO द्वारा SNA 2008 के अनुसार संकलित की जाती है।\n\nतीन प्रमुख विधियाँ:\n• **व्यय विधि**: C + I + G + (X−M)\n• **उत्पादन विधि**: सभी क्षेत्रों का GVA + कर − सब्सिडी\n• **आय विधि**: श्रमिक परिश्रम + परिचालन अधिशेष\n\nGDP अनुमान तिमाही आधार पर जारी होते हैं। वर्तमान आधार वर्ष: **2011-12**।',
    },
    cpi: {
      en: '**CPI (Consumer Price Index)** measures average price changes for a basket of goods & services.\n\nIn India:\n• Released monthly by MoSPI/NSO (base year 2012)\n• Uses **Laspeyres formula** (fixed base-period weights)\n• Covers 299 items across 6 groups\n\nRBI uses CPI as the **inflation targeting benchmark** (target: 4% ± 2%).',
      hi: '**CPI (उपभोक्ता मूल्य सूचकांक)** — घरेलू उपभोग की वस्तुओं और सेवाओं की औसत कीमत में बदलाव मापता है।\n\nभारत में:\n• MoSPI/NSO द्वारा मासिक जारी (आधार वर्ष 2012)\n• **Laspeyres सूत्र** का उपयोग\n• 299 वस्तुएँ, 6 समूह\n\nRBI, CPI को **मुद्रास्फीति लक्ष्यीकरण** के मानदंड के रूप में प्रयोग करता है (लक्ष्य: 4% ± 2%)।',
    },
    sampling: {
      en: '**Sampling in official statistics** involves selecting a subset of a population to estimate parameters.\n\nKey types used in NSSO surveys:\n• **Stratified Sampling**: Population divided by strata (urban/rural, states)\n• **Cluster Sampling**: Groups (villages/blocks) selected first\n• **Multi-stage Sampling**: Used in PLFS, HCES — districts → blocks → households',
      hi: '**Sampling (प्रतिदर्श)** — पूरी जनसंख्या का अनुमान लगाने के लिए उसका एक प्रतिनिधि हिस्सा चुनना।\n\nNSSO सर्वेक्षणों में उपयोग:\n• **स्तरीकृत Sampling**: Urban/rural, राज्य के अनुसार strata\n• **Cluster Sampling**: पहले समूह (गाँव/blocks) चुने जाते हैं\n• **बहु-स्तरीय Sampling**: PLFS, HCES में — जिला → block → घर',
    },
    frac: {
      en: '**FRAC (Framework for Roles, Activities and Competencies)** is GoI\'s competency architecture for civil servants on iGOT Karmayogi.\n\nFRAC defines:\n• **Roles**: Job positions (Deputy Director, Field Investigator, etc.)\n• **Activities**: Key functions in a role\n• **Competencies**: Skills — Behavioural (B), Domain (D), Functional (F)\n\nYour skill gap assessment here is fully aligned with the FRAC dictionary.',
      hi: '**FRAC (Framework for Roles, Activities and Competencies)** — iGOT Karmayogi पर सरकारी कर्मचारियों के लिए भारत सरकार का competency framework।\n\nFRAC में तीन घटक:\n• **Roles**: पदनाम (Deputy Director, Field Investigator आदि)\n• **Activities**: पद में किए जाने वाले प्रमुख कार्य\n• **Competencies**: आवश्यक कौशल — व्यावहारिक (B), क्षेत्र (D), कार्यात्मक (F)\n\nइस platform पर आपका skill gap assessment, FRAC dictionary से पूरी तरह संरेखित है।',
    },
    plfs: {
      en: '**PLFS (Periodic Labour Force Survey)** is conducted by NSSO/MoSPI to measure employment and unemployment.\n\nKey features:\n• Annual survey with quarterly urban estimates\n• Covers Usual Status, Current Weekly Status, Current Daily Status\n• Sample: ~1 lakh households\n\nPLFS replaces the old Employment-Unemployment Survey (EUS).',
      hi: '**PLFS (आवधिक श्रम बल सर्वेक्षण)** — NSSO/MoSPI द्वारा रोजगार और बेरोजगारी मापने के लिए आयोजित।\n\nमुख्य विशेषताएँ:\n• वार्षिक सर्वेक्षण + तिमाही शहरी अनुमान\n• सामान्य स्थिति, वर्तमान साप्ताहिक स्थिति, वर्तमान दैनिक स्थिति\n• नमूना: ~1 लाख घर\n\nPLFS ने पुराने Employment-Unemployment Survey (EUS) की जगह ली।',
    },
  };

  for (const [keyword, answers] of Object.entries(statDb)) {
    if (msgLow.includes(keyword)) return answers[lang];
  }

  // ── PLATFORM HELP ────────────────────────────────────────────────────────────
  if (intent === 'platform_help') {
    return lang === 'hi'
      ? '**MoSPI Skill Intelligence Platform** का उपयोग कैसे करें:\n\n📊 **Dashboard Tab** → अपने skill gaps और recommended courses देखें\n📚 **My Courses Tab** → active enrollments और progress track करें\n📈 **Progress Tab** → achievements और competency growth देखें\n🤖 **AI Generator** (right panel) → PDF upload करके MCQs generate करें\n\niGOT Karmayogi पर enroll करने के लिए, अपनी recommendations में से किसी course का नाम copy करें और iGOT portal पर search करें।'
      : '**How to navigate the MoSPI Skill Intelligence Platform:**\n\n📊 **Dashboard Tab** → View skill gaps and AI-recommended courses\n📚 **My Courses Tab** → Track active enrollments and progress\n📈 **Progress Tab** → See achievements and competency growth\n🤖 **AI Generator** (right panel) → Upload a PDF to generate MCQ quizzes\n\nTo enroll on iGOT Karmayogi, copy the course title from your recommendations and search it on the iGOT portal.';
  }

  // ── MOTIVATION ───────────────────────────────────────────────────────────────
  if (intent === 'motivation') {
    const firstRec = recommendations[0]?.course.title;
    return lang === 'hi'
      ? `मैं समझता हूँ — काम के साथ upskilling करना कठिन लगता है। 💪\n\nलेकिन याद रखें: **India के statistical system को आप जैसे समर्पित अधिकारियों की आवश्यकता है।** GDP अनुमान से लेकर गरीबी मापन तक — आपका कार्य लाखों लोगों की जिंदगी पर असर डालता है।\n\nएक कदम एक समय: **केवल 30 मिनट रोज** एक course पर — कुछ हफ्तों में ही परिणाम दिखने लगते हैं।\n\n${firstRec ? `अभी **${firstRec}** से शुरू करें!` : 'अपना पहला recommended course शुरू करें!'} 🚀`
      : `I understand — balancing daily work and upskilling is genuinely challenging. 💪\n\nBut remember: **India's statistical system depends on dedicated officials like you.** From GDP estimation to poverty measurement — your work impacts millions of lives.\n\nOne step at a time: just **30 minutes a day** on a course will show results within weeks.\n\n${firstRec ? `Start now with **${firstRec}**!` : 'Start with your first recommended course!'} 🚀`;
  }

  // ── GENERAL FALLBACK ─────────────────────────────────────────────────────────
  return lang === 'hi'
    ? pick([
        `यह एक अच्छा प्रश्न है! मैं आपकी सहायता कर सकता हूँ:\n• आपके skill gaps के बारे में\n• कौन सा course लेना चाहिए\n• सांख्यिकी विषय (GDP, CPI, Sampling, FRAC)\n• Platform उपयोग कैसे करें\n\nक्या आप अपना प्रश्न और स्पष्ट रूप से पूछ सकते हैं?`,
        `मैं ज्ञान हूँ — आपका MoSPI AI सहायक। प्रशिक्षण और सांख्यिकी के विषयों पर मैं सबसे अच्छी सहायता कर सकता हूँ! 🎓\n\nपूछें: *"मुझे कौन सा course लेना चाहिए?"* या *"GDP कैसे calculate होती है?"*`,
      ])
    : pick([
        `Great question! As a **${jobRole}** in ${department}, I can help with:\n• Your specific skill gaps\n• Course recommendations\n• Statistical concepts (GDP, CPI, Sampling, FRAC, PLFS)\n• How to use this platform\n\nCould you rephrase your question so I can give you a more specific answer?`,
        `I'm Gyan, your MoSPI AI assistant — best at training, skill gaps, and statistics topics! 🎓\n\nTry: *"What courses should I take?"* or *"Explain GDP calculation"*`,
      ]);
}

// ─── Main Exported Function ───────────────────────────────────────────────────

export async function sendChatMessage(
  officialId: string,
  message: string,
  history: ChatMessage[],
  jobRole: string,
  department: string,
  skillGaps: SkillGapEntry[],
  recommendations: CourseRecommendation[],
  fullName?: string,
  govId?: string,
  context?: string,
): Promise<{ reply: string; detectedLanguage: 'en' | 'hi'; navigateAction?: NavigateAction }> {

  const payload: ChatApiPayload = {
    user_id: officialId,
    message,
    history: history.map(m => ({ role: m.role, content: m.content })),
    job_role: jobRole,
    department,
    full_name: fullName,
    gov_id: govId,
    context,
    skill_gaps: skillGaps.map(g => ({
      skillName: g.competency.skillName,
      domain: g.competency.domain,
      currentLevel: g.currentLevel,
      targetLevel: g.requiredLevel,
      gapScore: g.gap,
    })),
    recommendations: recommendations.map(r => ({
      title: r.course.title,
      provider: r.course.source,
      durationHours: r.course.durationHours,
      matchReason: r.aiMatchTag,
    })),
  };

  try {
    const res = await fetch('/api/v1/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    return {
      reply: data.reply,
      detectedLanguage: (data.detected_language as 'en' | 'hi') ?? 'en',
      navigateAction: data.navigate_action ?? undefined,
    };
  } catch {
    // ── Backend unavailable → use client-side engine ──────────────────────────
    const lang = detectLanguage(message);
    const intent = detectIntent(message);
    const reply = buildLocalReply(
      intent, lang, officialId, jobRole, department, skillGaps, recommendations, message
    );
    return { reply, detectedLanguage: lang, navigateAction: undefined };
  }
}
