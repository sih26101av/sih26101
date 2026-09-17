/**
 * FILE: src/i18n/chatLanguages.ts
 *
 * The single source of truth for Gyan's language picker and its UI copy.
 * Both widgets (dashboard + landing page) read from here, so the two pickers
 * can never drift apart.
 *
 * The codes mirror the backend exactly — `SUPPORTED_CHAT_LANGUAGES` in
 * `services/language_service.py` plus `hi_latn` (romanized Hindi), and one
 * template module per code under `services/chat_messages/`. Adding a language
 * to this list without adding it there would show an option that silently
 * replies in English.
 *
 * Archit Shukla | SIH 2026
 */

import type { ChatLanguage } from '../services/chatApi';

// ─── The picker ──────────────────────────────────────────────────────────────

export interface ChatLanguageOption {
  code: ChatLanguage;
  /** Shown in the dropdown, in its own script. */
  native: string;
  /** Secondary line in the dropdown, so the list stays scannable in English. */
  english: string;
  /** Two/three-letter code on the header pill. */
  pill: string;
  /** BCP-47 tag for the Web Speech recogniser. */
  speech: string;
}

export const CHAT_LANGUAGES: readonly ChatLanguageOption[] = [
  { code: 'en',      native: 'English',  english: 'English',   pill: 'EN',  speech: 'en-IN' },
  { code: 'hi',      native: 'हिंदी',     english: 'Hindi',     pill: 'HI',  speech: 'hi-IN' },
  { code: 'hi_latn', native: 'Hinglish', english: 'Romanized', pill: 'HIN', speech: 'hi-IN' },
  { code: 'mr',      native: 'मराठी',     english: 'Marathi',   pill: 'MR',  speech: 'mr-IN' },
  { code: 'gu',      native: 'ગુજરાતી',    english: 'Gujarati',  pill: 'GU',  speech: 'gu-IN' },
  { code: 'te',      native: 'తెలుగు',    english: 'Telugu',    pill: 'TE',  speech: 'te-IN' },
  { code: 'ta',      native: 'தமிழ்',     english: 'Tamil',     pill: 'TA',  speech: 'ta-IN' },
  { code: 'or',      native: 'ଓଡ଼ିଆ',      english: 'Odia',      pill: 'OR',  speech: 'or-IN' },
  { code: 'bn',      native: 'বাংলা',     english: 'Bengali',   pill: 'BN',  speech: 'bn-IN' },
] as const;

export function languageOption(code: ChatLanguage): ChatLanguageOption {
  return CHAT_LANGUAGES.find(l => l.code === code) ?? CHAT_LANGUAGES[0];
}

/** The landing page itself is only translated into English and Hindi. */
export function isPageLanguage(code: ChatLanguage): code is 'en' | 'hi' {
  return code === 'en' || code === 'hi';
}

// ─── Widget copy ─────────────────────────────────────────────────────────────

/** Prompts that a capability card or a suggestion row actually sends. */
interface AskCopy {
  gaps: string;
  firstCourse: string;
  progress: string;
  assessment: string;
  platform: string;
  recommendations: string;
  gapAnalysis: string;
  mospi: string;
  gdp: string;
  usePlatform: string;
  features: string;
  login: string;
}

/** Capability-card captions. */
interface LabelCopy {
  gaps: string;
  courses: string;
  progress: string;
  assess: string;
  guidance: string;
  courseRecs: string;
  insights: string;
  quick: string;
}

export interface ChatCopy {
  tagline: string;
  greeting: string;
  homeSubtitle: string;
  dashSubtitle: (gapCount: number) => string;
  placeholderDash: string;
  placeholderHome: string;
  tryAsking: string;
  hintNewline: string;
  hintMic: string;
  navConfirmDash: (label: string) => string;
  navConfirmHome: (label: string) => string;
  yes: string;
  no: string;
  error: string;
  bubbleTitle: string;
  languageLabel: string;
  ask: AskCopy;
  label: LabelCopy;
}

const COPY: Record<ChatLanguage, ChatCopy> = {
  en: {
    tagline: 'Ask me anything',
    greeting: "Hello! I'm Gyan 👋",
    homeSubtitle: 'Your AI assistant for KarmaSkill',
    dashSubtitle: n => `You have ${n} active skill gap${n !== 1 ? 's' : ''}. Ask me anything!`,
    placeholderDash: 'Ask anything about your training…',
    placeholderHome: 'Ask about MoSPI, features, login…',
    tryAsking: 'Try asking',
    hintNewline: 'Shift + Enter for new line',
    hintMic: 'Click mic to speak',
    navConfirmDash: l => `Take you to the ${l}?`,
    navConfirmHome: l => `Scroll to the ${l}?`,
    yes: 'Yes, take me there ✈️',
    no: 'No',
    error: 'Sorry, I ran into a technical issue. Please try again in a moment. 🙏',
    bubbleTitle: 'Chat with Gyan AI',
    languageLabel: 'Language',
    ask: {
      gaps: 'What are my skill gaps?',
      firstCourse: 'Which course should I take first?',
      progress: 'Show me my progress',
      assessment: 'How do I take an assessment?',
      platform: 'What is this platform?',
      recommendations: 'How do course recommendations work?',
      gapAnalysis: 'How does skill gap analysis work?',
      mospi: 'Tell me about MoSPI',
      gdp: 'Explain GDP calculation',
      usePlatform: 'How do I use this platform?',
      features: 'Show me the Features section',
      login: 'How do I login?',
    },
    label: {
      gaps: 'Skill Gaps', courses: 'My Courses', progress: 'My Progress', assess: 'Assessments',
      guidance: 'Platform Guidance', courseRecs: 'Course Recommendations',
      insights: 'Competency Insights', quick: 'Quick Information',
    },
  },

  hi: {
    tagline: 'कुछ भी पूछें',
    greeting: 'नमस्ते! मैं ज्ञान हूँ 🙏',
    homeSubtitle: 'KarmaSkill के लिए आपका AI सहायक',
    dashSubtitle: n => `आपके पास ${n} सक्रिय skill gap ${n !== 1 ? 'हैं' : 'है'}।`,
    placeholderDash: 'अपने प्रशिक्षण के बारे में पूछें…',
    placeholderHome: 'MoSPI, features, login के बारे में पूछें…',
    tryAsking: 'यह पूछकर देखें',
    hintNewline: 'नई line के लिए Shift + Enter',
    hintMic: 'बोलने के लिए mic दबाएँ',
    navConfirmDash: l => `क्या मैं आपको "${l}" पर ले जाऊँ?`,
    navConfirmHome: l => `क्या मैं आपको "${l}" पर ले जाऊँ?`,
    yes: 'हाँ, ले चलो ✈️',
    no: 'नहीं',
    error: 'क्षमा करें, कुछ तकनीकी समस्या आ गई। थोड़ी देर बाद पुनः प्रयास करें। 🙏',
    bubbleTitle: 'Gyan AI से बात करें',
    languageLabel: 'भाषा',
    ask: {
      gaps: 'मेरे skill gaps क्या हैं?',
      firstCourse: 'मुझे पहले कौन सा course लेना चाहिए?',
      progress: 'मेरी progress दिखाओ',
      assessment: 'Assessment कैसे लूँ?',
      platform: 'यह platform क्या है?',
      recommendations: 'Course recommendations कैसे काम करती हैं?',
      gapAnalysis: 'Skill gap analysis कैसे होता है?',
      mospi: 'MoSPI के बारे में बताओ',
      gdp: 'GDP कैसे calculate होती है?',
      usePlatform: 'यह platform कैसे use करूँ?',
      features: 'Features section दिखाओ',
      login: 'Login कैसे करूँ?',
    },
    label: {
      gaps: 'कौशल अंतर', courses: 'मेरे पाठ्यक्रम', progress: 'मेरी प्रगति', assess: 'मूल्यांकन',
      guidance: 'प्लेटफ़ॉर्म मार्गदर्शन', courseRecs: 'पाठ्यक्रम अनुशंसाएँ',
      insights: 'दक्षता अंतर्दृष्टि', quick: 'त्वरित जानकारी',
    },
  },

  hi_latn: {
    tagline: 'Kuch bhi poochhein',
    greeting: 'Namaste! Main Gyan hoon 🙏',
    homeSubtitle: 'KarmaSkill ke liye aapka AI sahayak',
    dashSubtitle: n => `Aapke paas ${n} active skill gap ${n !== 1 ? 'hain' : 'hai'}.`,
    placeholderDash: 'Apni training ke baare mein poochhein…',
    placeholderHome: 'MoSPI, features, login ke baare mein poochhein…',
    tryAsking: 'Yeh poochh kar dekhein',
    hintNewline: 'Nayi line ke liye Shift + Enter',
    hintMic: 'Bolne ke liye mic dabayein',
    navConfirmDash: l => `Kya main aapko "${l}" par le jaun?`,
    navConfirmHome: l => `Kya main aapko "${l}" par le jaun?`,
    yes: 'Haan, le chalo ✈️',
    no: 'Nahi',
    error: 'Maafi chahta hoon, abhi kuch technical problem aa gayi. Thodi der baad try karein. 🙏',
    bubbleTitle: 'Gyan AI se baat karein',
    languageLabel: 'Bhasha',
    ask: {
      gaps: 'Mere skill gaps kya hain?',
      firstCourse: 'Mujhe pehle kaunsa course lena chahiye?',
      progress: 'Meri progress dikhao',
      assessment: 'Assessment kaise lun?',
      platform: 'Yeh platform kya hai?',
      recommendations: 'Course recommendations kaise kaam karti hain?',
      gapAnalysis: 'Skill gap analysis kaise hota hai?',
      mospi: 'MoSPI ke baare mein batao',
      gdp: 'GDP kaise calculate hoti hai?',
      usePlatform: 'Yeh platform kaise use karun?',
      features: 'Features section dikhao',
      login: 'Login kaise karun?',
    },
    label: {
      gaps: 'Skill Gaps', courses: 'Mere Courses', progress: 'Meri Progress', assess: 'Assessments',
      guidance: 'Platform Margdarshan', courseRecs: 'Course Recommendations',
      insights: 'Competency Insights', quick: 'Turant Jaankari',
    },
  },

  mr: {
    tagline: 'काहीही विचारा',
    greeting: 'नमस्कार! मी ज्ञान आहे 🙏',
    homeSubtitle: 'KarmaSkill साठी तुमचा AI सहाय्यक',
    dashSubtitle: n => `तुमच्याकडे ${n} सक्रिय skill gap आहेत.`,
    placeholderDash: 'तुमच्या प्रशिक्षणाबद्दल विचारा…',
    placeholderHome: 'MoSPI, features, login बद्दल विचारा…',
    tryAsking: 'हे विचारून पहा',
    hintNewline: 'नवीन ओळीसाठी Shift + Enter',
    hintMic: 'बोलण्यासाठी mic दाबा',
    navConfirmDash: l => `मी तुम्हाला "${l}" वर नेऊ का?`,
    navConfirmHome: l => `मी तुम्हाला "${l}" वर नेऊ का?`,
    yes: 'होय, चला ✈️',
    no: 'नाही',
    error: 'क्षमस्व, तांत्रिक अडचण आली. थोड्या वेळाने पुन्हा प्रयत्न करा. 🙏',
    bubbleTitle: 'Gyan AI शी बोला',
    languageLabel: 'भाषा',
    ask: {
      gaps: 'माझे skill gaps कोणते आहेत?',
      firstCourse: 'मी आधी कोणता course घ्यावा?',
      progress: 'माझी progress दाखवा',
      assessment: 'Assessment कसे द्यावे?',
      platform: 'हे platform काय आहे?',
      recommendations: 'Course recommendations कशा काम करतात?',
      gapAnalysis: 'Skill gap analysis कसे होते?',
      mospi: 'MoSPI बद्दल सांगा',
      gdp: 'GDP कशी calculate होते?',
      usePlatform: 'हे platform कसे वापरावे?',
      features: 'Features section दाखवा',
      login: 'Login कसे करावे?',
    },
    label: {
      gaps: 'कौशल्य अंतर', courses: 'माझे कोर्स', progress: 'माझी प्रगती', assess: 'मूल्यांकन',
      guidance: 'प्लॅटफॉर्म मार्गदर्शन', courseRecs: 'कोर्स शिफारसी',
      insights: 'क्षमता अंतर्दृष्टी', quick: 'त्वरित माहिती',
    },
  },

  gu: {
    tagline: 'કંઈ પણ પૂછો',
    greeting: 'નમસ્તે! હું જ્ઞાન છું 🙏',
    homeSubtitle: 'KarmaSkill માટે તમારો AI સહાયક',
    dashSubtitle: n => `તમારી પાસે ${n} સક્રિય skill gap છે.`,
    placeholderDash: 'તમારી તાલીમ વિશે પૂછો…',
    placeholderHome: 'MoSPI, features, login વિશે પૂછો…',
    tryAsking: 'આ પૂછી જુઓ',
    hintNewline: 'નવી લાઇન માટે Shift + Enter',
    hintMic: 'બોલવા માટે mic દબાવો',
    navConfirmDash: l => `શું હું તમને "${l}" પર લઈ જાઉં?`,
    navConfirmHome: l => `શું હું તમને "${l}" પર લઈ જાઉં?`,
    yes: 'હા, ચાલો ✈️',
    no: 'ના',
    error: 'માફ કરશો, થોડી ટેકનિકલ સમસ્યા આવી. થોડી વારે ફરી પ્રયાસ કરો. 🙏',
    bubbleTitle: 'Gyan AI સાથે વાત કરો',
    languageLabel: 'ભાષા',
    ask: {
      gaps: 'મારા skill gaps કયા છે?',
      firstCourse: 'મારે પહેલા કયો course લેવો જોઈએ?',
      progress: 'મારી progress બતાવો',
      assessment: 'Assessment કેવી રીતે આપું?',
      platform: 'આ platform શું છે?',
      recommendations: 'Course recommendations કેવી રીતે કામ કરે છે?',
      gapAnalysis: 'Skill gap analysis કેવી રીતે થાય છે?',
      mospi: 'MoSPI વિશે જણાવો',
      gdp: 'GDP કેવી રીતે calculate થાય છે?',
      usePlatform: 'આ platform કેવી રીતે વાપરું?',
      features: 'Features section બતાવો',
      login: 'Login કેવી રીતે કરું?',
    },
    label: {
      gaps: 'કૌશલ્ય અંતર', courses: 'મારા કોર્સ', progress: 'મારી પ્રગતિ', assess: 'મૂલ્યાંકન',
      guidance: 'પ્લેટફોર્મ માર્ગદર્શન', courseRecs: 'કોર્સ ભલામણો',
      insights: 'ક્ષમતા આંતરદૃષ્ટિ', quick: 'ઝડપી માહિતી',
    },
  },

  te: {
    tagline: 'ఏదైనా అడగండి',
    greeting: 'నమస్తే! నేను జ్ఞాన్ 🙏',
    homeSubtitle: 'KarmaSkill కోసం మీ AI సహాయకుడు',
    dashSubtitle: n => `మీకు ${n} క్రియాశీల skill gap ఉన్నాయి.`,
    placeholderDash: 'మీ శిక్షణ గురించి అడగండి…',
    placeholderHome: 'MoSPI, features, login గురించి అడగండి…',
    tryAsking: 'ఇలా అడిగి చూడండి',
    hintNewline: 'కొత్త లైన్ కోసం Shift + Enter',
    hintMic: 'మాట్లాడటానికి mic నొక్కండి',
    navConfirmDash: l => `నేను మిమ్మల్ని "${l}" కు తీసుకెళ్లనా?`,
    navConfirmHome: l => `నేను మిమ్మల్ని "${l}" కు తీసుకెళ్లనా?`,
    yes: 'అవును, వెళ్దాం ✈️',
    no: 'వద్దు',
    error: 'క్షమించండి, సాంకేతిక సమస్య వచ్చింది. కొద్దిసేపటి తర్వాత ప్రయత్నించండి. 🙏',
    bubbleTitle: 'Gyan AI తో మాట్లాడండి',
    languageLabel: 'భాష',
    ask: {
      gaps: 'నా skill gaps ఏమిటి?',
      firstCourse: 'నేను మొదట ఏ course తీసుకోవాలి?',
      progress: 'నా progress చూపించు',
      assessment: 'Assessment ఎలా తీసుకోవాలి?',
      platform: 'ఈ platform ఏమిటి?',
      recommendations: 'Course recommendations ఎలా పని చేస్తాయి?',
      gapAnalysis: 'Skill gap analysis ఎలా జరుగుతుంది?',
      mospi: 'MoSPI గురించి చెప్పండి',
      gdp: 'GDP ఎలా calculate అవుతుంది?',
      usePlatform: 'ఈ platform ఎలా ఉపయోగించాలి?',
      features: 'Features section చూపించు',
      login: 'Login ఎలా చేయాలి?',
    },
    label: {
      gaps: 'నైపుణ్య అంతరాలు', courses: 'నా కోర్సులు', progress: 'నా పురోగతి', assess: 'మూల్యాంకనాలు',
      guidance: 'ప్లాట్‌ఫారమ్ మార్గదర్శకం', courseRecs: 'కోర్సు సిఫార్సులు',
      insights: 'సామర్థ్య అంతర్దృష్టులు', quick: 'త్వరిత సమాచారం',
    },
  },

  ta: {
    tagline: 'எதையும் கேளுங்கள்',
    greeting: 'வணக்கம்! நான் ஞான் 🙏',
    homeSubtitle: 'KarmaSkill க்கான உங்கள் AI உதவியாளர்',
    dashSubtitle: n => `உங்களிடம் ${n} செயலில் உள்ள skill gap உள்ளது.`,
    placeholderDash: 'உங்கள் பயிற்சி பற்றி கேளுங்கள்…',
    placeholderHome: 'MoSPI, features, login பற்றி கேளுங்கள்…',
    tryAsking: 'இதைக் கேட்டுப் பாருங்கள்',
    hintNewline: 'புதிய வரிக்கு Shift + Enter',
    hintMic: 'பேச mic ஐ அழுத்தவும்',
    navConfirmDash: l => `உங்களை "${l}" க்கு அழைத்துச் செல்லவா?`,
    navConfirmHome: l => `உங்களை "${l}" க்கு அழைத்துச் செல்லவா?`,
    yes: 'ஆம், செல்வோம் ✈️',
    no: 'வேண்டாம்',
    error: 'மன்னிக்கவும், தொழில்நுட்பச் சிக்கல் ஏற்பட்டது. சிறிது நேரம் கழித்து முயற்சிக்கவும். 🙏',
    bubbleTitle: 'Gyan AI உடன் பேசுங்கள்',
    languageLabel: 'மொழி',
    ask: {
      gaps: 'என் skill gaps என்ன?',
      firstCourse: 'நான் முதலில் எந்த course எடுக்க வேண்டும்?',
      progress: 'என் progress காட்டு',
      assessment: 'Assessment எப்படி எடுப்பது?',
      platform: 'இந்த platform என்ன?',
      recommendations: 'Course recommendations எப்படி வேலை செய்கின்றன?',
      gapAnalysis: 'Skill gap analysis எப்படி நடக்கிறது?',
      mospi: 'MoSPI பற்றி சொல்லுங்கள்',
      gdp: 'GDP எப்படி calculate செய்யப்படுகிறது?',
      usePlatform: 'இந்த platform எப்படி பயன்படுத்துவது?',
      features: 'Features section காட்டு',
      login: 'Login எப்படி செய்வது?',
    },
    label: {
      gaps: 'திறன் இடைவெளிகள்', courses: 'என் படிப்புகள்', progress: 'என் முன்னேற்றம்', assess: 'மதிப்பீடுகள்',
      guidance: 'தள வழிகாட்டுதல்', courseRecs: 'படிப்பு பரிந்துரைகள்',
      insights: 'திறன் நுண்ணறிவு', quick: 'விரைவு தகவல்',
    },
  },

  or: {
    tagline: 'ଯାହା ବି ପଚାରନ୍ତୁ',
    greeting: 'ନମସ୍କାର! ମୁଁ ଜ୍ଞାନ 🙏',
    homeSubtitle: 'KarmaSkill ପାଇଁ ଆପଣଙ୍କ AI ସହାୟକ',
    dashSubtitle: n => `ଆପଣଙ୍କର ${n} ସକ୍ରିୟ skill gap ଅଛି।`,
    placeholderDash: 'ଆପଣଙ୍କ ତାଲିମ ବିଷୟରେ ପଚାରନ୍ତୁ…',
    placeholderHome: 'MoSPI, features, login ବିଷୟରେ ପଚାରନ୍ତୁ…',
    tryAsking: 'ଏହା ପଚାରି ଦେଖନ୍ତୁ',
    hintNewline: 'ନୂଆ ଧାଡ଼ି ପାଇଁ Shift + Enter',
    hintMic: 'କହିବା ପାଇଁ mic ଦବାନ୍ତୁ',
    navConfirmDash: l => `ମୁଁ ଆପଣଙ୍କୁ "${l}" କୁ ନେଇଯିବି କି?`,
    navConfirmHome: l => `ମୁଁ ଆପଣଙ୍କୁ "${l}" କୁ ନେଇଯିବି କି?`,
    yes: 'ହଁ, ଚାଲନ୍ତୁ ✈️',
    no: 'ନା',
    error: 'କ୍ଷମା କରନ୍ତୁ, ଏକ ବୈଷୟିକ ସମସ୍ୟା ହେଲା। କିଛି ସମୟ ପରେ ପୁଣି ଚେଷ୍ଟା କରନ୍ତୁ। 🙏',
    bubbleTitle: 'Gyan AI ସହ କଥା ହୁଅନ୍ତୁ',
    languageLabel: 'ଭାଷା',
    ask: {
      gaps: 'ମୋର skill gaps କଣ?',
      firstCourse: 'ମୁଁ ପ୍ରଥମେ କେଉଁ course ନେବି?',
      progress: 'ମୋର progress ଦେଖାନ୍ତୁ',
      assessment: 'Assessment କିପରି ଦେବି?',
      platform: 'ଏହି platform କଣ?',
      recommendations: 'Course recommendations କିପରି କାମ କରେ?',
      gapAnalysis: 'Skill gap analysis କିପରି ହୁଏ?',
      mospi: 'MoSPI ବିଷୟରେ କୁହନ୍ତୁ',
      gdp: 'GDP କିପରି calculate ହୁଏ?',
      usePlatform: 'ଏହି platform କିପରି ବ୍ୟବହାର କରିବି?',
      features: 'Features section ଦେଖାନ୍ତୁ',
      login: 'Login କିପରି କରିବି?',
    },
    label: {
      gaps: 'କୌଶଳ ଅନ୍ତର', courses: 'ମୋର କୋର୍ସ', progress: 'ମୋର ପ୍ରଗତି', assess: 'ମୂଲ୍ୟାଙ୍କନ',
      guidance: 'ପ୍ଲାଟଫର୍ମ ମାର୍ଗଦର୍ଶନ', courseRecs: 'କୋର୍ସ ସୁପାରିଶ',
      insights: 'ଦକ୍ଷତା ଅନ୍ତର୍ଦୃଷ୍ଟି', quick: 'ଦ୍ରୁତ ସୂଚନା',
    },
  },

  bn: {
    tagline: 'যা খুশি জিজ্ঞাসা করুন',
    greeting: 'নমস্কার! আমি জ্ঞান 🙏',
    homeSubtitle: 'KarmaSkill-এর জন্য আপনার AI সহায়ক',
    dashSubtitle: n => `আপনার ${n}টি সক্রিয় skill gap রয়েছে।`,
    placeholderDash: 'আপনার প্রশিক্ষণ সম্পর্কে জিজ্ঞাসা করুন…',
    placeholderHome: 'MoSPI, features, login সম্পর্কে জিজ্ঞাসা করুন…',
    tryAsking: 'এটা জিজ্ঞাসা করে দেখুন',
    hintNewline: 'নতুন লাইনের জন্য Shift + Enter',
    hintMic: 'বলতে mic চাপুন',
    navConfirmDash: l => `আমি কি আপনাকে "${l}"-এ নিয়ে যাব?`,
    navConfirmHome: l => `আমি কি আপনাকে "${l}"-এ নিয়ে যাব?`,
    yes: 'হ্যাঁ, চলুন ✈️',
    no: 'না',
    error: 'দুঃখিত, একটি কারিগরি সমস্যা হয়েছে। কিছুক্ষণ পরে আবার চেষ্টা করুন। 🙏',
    bubbleTitle: 'Gyan AI-এর সঙ্গে কথা বলুন',
    languageLabel: 'ভাষা',
    ask: {
      gaps: 'আমার skill gaps কী কী?',
      firstCourse: 'আমার প্রথমে কোন course নেওয়া উচিত?',
      progress: 'আমার progress দেখাও',
      assessment: 'Assessment কীভাবে দেব?',
      platform: 'এই platform কী?',
      recommendations: 'Course recommendations কীভাবে কাজ করে?',
      gapAnalysis: 'Skill gap analysis কীভাবে হয়?',
      mospi: 'MoSPI সম্পর্কে বলুন',
      gdp: 'GDP কীভাবে calculate হয়?',
      usePlatform: 'এই platform কীভাবে ব্যবহার করব?',
      features: 'Features section দেখাও',
      login: 'Login কীভাবে করব?',
    },
    label: {
      gaps: 'দক্ষতার ঘাটতি', courses: 'আমার কোর্স', progress: 'আমার অগ্রগতি', assess: 'মূল্যায়ন',
      guidance: 'প্ল্যাটফর্ম নির্দেশিকা', courseRecs: 'কোর্স সুপারিশ',
      insights: 'দক্ষতা অন্তর্দৃষ্টি', quick: 'দ্রুত তথ্য',
    },
  },
};

/** Copy for a language, falling back to English for anything unmapped. */
export function chatCopy(code: ChatLanguage): ChatCopy {
  return COPY[code] ?? COPY.en;
}
