import React, { useEffect, useState } from 'react';
import {
  User, Users, BookOpen, Activity, Award, Route, BrainCircuit, BookOpenCheck,
  FileQuestion, RefreshCw, Shield, LayoutDashboard, ArrowRight, Megaphone,
  ChevronRight, BarChart3, Menu, X, Pause, Play,
} from 'lucide-react';
import { useScreenReader } from '../hooks/useScreenReader';
import { usePageTitle } from '../hooks/usePageTitle';
import { useAccessibility } from '../context/AccessibilityContext';
import GovUtilityBar from '../components/gov/GovUtilityBar';
import GovFooter from '../components/gov/GovFooter';
import LoginPage from './LoginPage';
import HomeChatWidget from '../components/home/HomeChatWidget';
import { AshokaChakra, GovEmblem, Reveal, CountUp } from '../components/gov/GovUI';


const translations: Record<string, React.ReactNode> = {
  "MoSPI": <>सांख्यिकी और कार्यक्रम कार्यान्वयन<br />मंत्रालय (MoSPI)</>,
  "SIP": "कौशल बुद्धिमत्ता मंच",
  "GoI": "भारत सरकार",
  "Skip": "मुख्य सामग्री पर जाएं",
  "Home": "होम",
  "About": "के बारे में",
  "Features": "विशेषताएँ",
  "Contact": "संपर्क",
  "Eng_Hi": "Eng | हिंदी",
  "SR_Label": "स्क्रीन रीडर",
  "SR_On": "पढ़ना रोकें",
  "SR_Start": "यह पृष्ठ सुनें",
  "SR_Stop": "पढ़ना बंद करें",
  "OFFICIAL_LOGIN": "अधिकारी लॉगिन",
  "ADMIN_PORTAL": "एडमिन पोर्टल",
  "Whats_New": "नया क्या है",
  "Powered": "MoSPI एआई इंजन द्वारा संचालित",
  "Empowering": <>भारत की आधिकारिक सांख्यिकीय<br/>प्रणाली को सशक्त बनाना</>,
  "Hero_Desc": "एक अगली पीढ़ी का क्षमता ट्रैकिंग मंच। हम एआई-संचालित कौशल-अंतर विश्लेषण को व्यक्तिगत iGOT सीखने के मार्गों के साथ जोड़ते हैं।",
  "LOGIN_AS": "अधिकारी के रूप में लॉगिन करें",
  "Building": <>एक अधिक सक्षम<br /><span className="text-white/85">सांख्यिकीय कार्यबल का निर्माण</span></>,
  "Assess_Gaps": "कौशल अंतर का आकलन",
  "Assess_Gaps_Desc": "लक्षित शिक्षण के लिए डेटा-संचालित विश्लेषण",
  "Personalised": "व्यक्तिगत शिक्षण",
  "Personalised_Desc": "भूमिका-आधारित पाठ्यक्रम अनुशंसाएँ",
  "Governance": "सुदृढ़ अभिशासन",
  "Governance_Desc": "एक भविष्य-तैयार सांख्यिकीय पारिस्थितिकी तंत्र",
  "Capabilities": "प्लेटफ़ॉर्म क्षमताएं",
  "Skill_Analysis": "कौशल विश्लेषण",
  "Skill_Analysis_Desc": "साक्ष्य-आधारित दक्षता आधाररेखा की गणना।",
  "iGOT_Learning": "iGOT लर्निंग",
  "iGOT_Learning_Desc": "अंतराल से जुड़े iGOT पाठ्यक्रम।",
  "Career_Pathways": "करियर पाथवे",
  "Career_Pathways_Desc": "भूमिका-आधारित करियर रोडमैप।",
  "Active_Users": "सक्रिय उपयोगकर्ता",
  "Courses_Matched": "कोर्स मिलान",
  "Skill_Gaps_Resolved": "कौशल अंतर हल",
  "Certifications": "प्रमाणपत्र",
  "Key_Features": "MoSPI कौशल संवर्धन की मुख्य विशेषताएं",
  "AI_Driven": <>एआई-संचालित कौशल<br/>अंतर विश्लेषण</>,
  "AI_Driven_1": "किसी अधिकारी के वर्तमान ज्ञान और उनके राष्ट्रीय व्यवसाय वर्गीकरण (NCO-2015) पदनाम के लिए आवश्यक लक्ष्य प्रवीणता के बीच सटीक गणितीय अंतर की गणना करता है।",
  "AI_Driven_2": "338 आधिकारिक भूमिकाओं, गतिविधियों और दक्षताओं (FRAC) मानकों के खिलाफ उपयोगकर्ता प्रोफाइल का मिलान करता है।",
  "Intelligent_iGOT": <>बुद्धिमान iGOT<br/>कोर्स मैपिंग</>,
  "Intelligent_iGOT_1": "पहचाने गए कौशल अंतराल को पाटने के लिए आवश्यक सटीक iGOT Sunbird पाठ्यक्रमों की प्रोग्रामेटिक सिफारिश करके मैनुअल कैटलॉग खोज को समाप्त करता है।",
  "Intelligent_iGOT_2": "अधिकारी के विशिष्ट कैरियर पथ और लापता कौशल के आधार पर 8,000 से अधिक प्रामाणिक सरकारी प्रशिक्षण मॉड्यूल को फ़िल्टर करता है।",
  "Auto_RAG": <>स्वचालित RAG<br/>दस्तावेज़-से-क्विज़</>,
  "Auto_RAG_1": "अधिकारियों को कस्टम बहुविकल्पीय आकलन तुरंत उत्पन्न करने के लिए मानक सरकारी दस्तावेज़ (PDF, PPTX, DOCX) अपलोड करने की अनुमति देता है।",
  "Auto_RAG_2": "प्रशासकों से पूर्व-लिखित परीक्षणों की आवश्यकता के बिना गतिशील रूप से डोमेन ज्ञान का मूल्यांकन करता है।",
  "Real_Time": <>रीयल-टाइम कर्मयोगी<br/>सिंक्रनाइज़ेशन</>,
  "Real_Time_1": "उपलब्धियों को लॉग करने के लिए स्वचालित रूप से iGOT पोर्टल बैकएंड के साथ संवाद करता है।",
  "Real_Time_2": "एक मूल्यांकन पर 70% या उससे अधिक स्कोर करने के तुरंत बाद राष्ट्रीय रजिस्ट्री पर एक अधिकारी के FRAC योग्यता स्तर को अपग्रेड करता है।",
  "Air_Gapped": <>एयर-गैप्ड NLP<br/>सहायक</>,
  "Air_Gapped_1": "पाठ्यक्रमों को नेविगेट करने, अंतराल का विश्लेषण करने और आकलन को ट्रिगर करने के लिए एक इंटरैक्टिव, शून्य-विलंबता चैट इंटरफ़ेस प्रदान करता है।",
  "Air_Gapped_2": "संवेदनशील MoSPI वातावरण के लिए 100% डेटा संप्रभुता की गारंटी देने के लिए एक सुरक्षित, एम्बेडेड नियतात्मक आशय-रूटिंग इंजन का उपयोग करता है।",
  "Dashboard": <>मंत्रालय-व्यापी एनालिटिक्स<br/>डैशबोर्ड</>,
  "Dashboard_1": "विभिन्न MoSPI विंग (NSO, CSO) में क्षमता निर्माण का मैक्रो-व्यू देने के लिए प्रशिक्षण टेलीमेट्री को एकत्र करता है।",
  "Dashboard_2": "वास्तविक समय में हल किए गए कौशल अंतराल, सक्रिय प्रमाणपत्रों और विभागीय तत्परता की कल्पना करता है।",
  "About_Platform": "प्लेटफ़ॉर्म के बारे में",
  "Transforming": <>भारत के सांख्यिकीय<br/>कार्यबल को बदलना</>,
  "Rooted": "मिशन कर्मयोगी के जनादेश में निहित, MoSPI कौशल इंटेलिजेंस प्लेटफ़ॉर्म एक अगली पीढ़ी का क्षमता निर्माण पारिस्थितिकी तंत्र है। यह विशिष्ट परिचालन कर्तव्यों को मानकीकृत राष्ट्रीय दक्षताओं के साथ संरेखित करके सिविल सेवकों को नियम-आधारित से भूमिका-आधारित ढांचे में बदल देता है।",
  "Our_Mission": "हमारा मिशन",
  "Our_Mission_Desc": "एक बुद्धिमान, डेटा-संप्रभु बुनियादी ढांचा प्रदान करके सांख्यिकी और कार्यक्रम कार्यान्वयन मंत्रालय (MoSPI) का आधुनिकीकरण करना जो स्वायत्त रूप से कौशल अंतराल की पहचान करता है, व्यक्तिगत सीखने के मार्ग तैयार करता है, और वास्तविक समय में डोमेन महारत का मूल्यांकन करता है।",
  "Built_For": "संप्रभुता और सुरक्षा के लिए निर्मित",
  "Built_For_Desc": "राष्ट्रीय सांख्यिकीय प्रणाली के संवेदनशील वातावरण के भीतर काम करने के लिए समझौताहीन डेटा सुरक्षा की आवश्यकता होती है। हमारा पूरी तरह से एयर-गैप्ड, नियतात्मक आशय-रूटिंग एनएलपी इंजन सुनिश्चित करता है कि सभी इंटरैक्शन, मूल्यांकन और टेलीमेट्री बाहरी वाणिज्यिक एपीआई कुंजी पर निर्भरता के बिना सरकारी इंट्रानेट के भीतर सख्ती से रहें।",
  "Arch": "सतत शिक्षा की वास्तुकला",
  "FRAC": "FRAC-संरेखित ढांचा",
  "FRAC_Desc": "हम प्रामाणिक राष्ट्रीय व्यवसाय वर्गीकरण (NCO-2015) नौकरी प्रोफाइल को सीधे FRAC द्वारा परिभाषित 338 मानकीकृत दक्षताओं से मैप करते हैं। यह सुनिश्चित करता है कि हर सीखने की सिफारिश गणितीय रूप से एक अधिकारी के वास्तविक कैरियर पथ पर लक्षित है।",
  "iGOT": "बुद्धिमान iGOT एकीकरण",
  "iGOT_Desc": "राष्ट्रीय iGOT सनबर्ड रजिस्ट्री के साथ गहराई से एकीकृत करके, हम पहचाने गए अंतराल को पाटने के लिए आवश्यक सटीक पाठ्यक्रमों की सिफारिश करने के लिए 8,000 से अधिक आधिकारिक प्रशिक्षण मॉड्यूल के माध्यम से छानते हैं, जबकि स्वचालित रूप से नई उपलब्धियों को केंद्र सरकार के डेटाबेस में सिंक करते हैं।",
  "Dynamic_AI": "गतिशील एआई मूल्यांकन",
  "Dynamic_AI_Desc": "हमारे मालिकाना RAG पाइपलाइन के माध्यम से, प्लेटफ़ॉर्म विभागों को आंतरिक नीति दस्तावेजों, प्रस्तुतियों और मैनुअल से तुरंत कस्टम मूल्यांकन उत्पन्न करने की अनुमति देता है, यह सुनिश्चित करता है कि अधिकारियों को सबसे प्रासंगिक विभागीय ज्ञान पर परीक्षण किया जाए।",
  "Quick_Links": "त्वरित लिंक",
  "Related_Portals": "संबंधित पोर्टल",
  "Contact_Us": "संपर्क करें",
  "Footer_1": "सांख्यिकी और कार्यक्रम कार्यान्वयन मंत्रालय (MoSPI) | भारत सरकार",
  "Privacy": "गोपनीयता नीति",
  "Terms": "नियम",
  "Help": "मदद और अक्सर पूछे जाने वाले प्रश्न"
};

const NEWS_ITEMS = [
  'AI-generated assessments now available for NSO training documents',
  'FRAC competency baselines refreshed with evidence-weighted scoring',
  'New iGOT Karmayogi courses mapped for Official Statistics & Survey Methods',
  'Gyan assistant now supports Hindi and English',
];

const LandingPage: React.FC = () => {

  // Text size, contrast and language are portal-wide preferences — they live in
  // AccessibilityContext so the choice follows the user into the dashboards.
  const { lang, setLang } = useAccessibility();
  const screenReader = useScreenReader(lang);
  usePageTitle(
    undefined,
    'KarmaSkill — the MoSPI Skill Intelligence Platform: evidence-based competency baselines, skill-gap analysis and iGOT Karmayogi learning pathways for officials of the National Statistical System.'
  );
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [tickerPaused, setTickerPaused] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 120);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const t = (key: string, enText: string | React.ReactNode) => {
    return lang === 'en' ? enText : translations[key] || enText;
  };


  const scrollToSection = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
    e.preventDefault();
    setMobileNavOpen(false);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    } else if (id === 'home') {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const navItems: { id: string; key: string; label: string }[] = [
    { id: 'home', key: 'Home', label: 'Home' },
    { id: 'about', key: 'About', label: 'About' },
    { id: 'features', key: 'Features', label: 'Features' },
    { id: 'contact', key: 'Contact', label: 'Contact' },
  ];

  const capabilities = [
    { icon: BrainCircuit, key: 'Skill_Analysis', title: 'Skill Analysis', dKey: 'Skill_Analysis_Desc', desc: 'Evidence-based competency baselines.' },
    { icon: BookOpen, key: 'iGOT_Learning', title: 'iGOT Learning', dKey: 'iGOT_Learning_Desc', desc: 'Gap-linked iGOT courses.' },
    { icon: Route, key: 'Career_Pathways', title: 'Career Pathways', dKey: 'Career_Pathways_Desc', desc: 'Role-based career roadmaps.' },
  ];

  const stats = [
    { icon: User, end: 12.4, decimals: 1, suffix: 'k', key: 'Active_Users', label: 'Active Users' },
    { icon: BookOpen, end: 458, decimals: 0, suffix: '', key: 'Courses_Matched', label: 'Courses Matched' },
    { icon: Activity, end: 89, decimals: 0, suffix: 'k', key: 'Skill_Gaps_Resolved', label: 'Skill Gaps Resolved' },
    { icon: Award, end: 1240, decimals: 0, suffix: '', key: 'Certifications', label: 'Certifications' },
  ];

  const features = [
    { icon: BrainCircuit, key: 'AI_Driven', title: <>AI-Driven Skill<br/>Gap Analysis</>, points: [
      ['AI_Driven_1', 'Calculates precise mathematical gaps between an official\'s current knowledge and the target proficiency required for their National Classification of Occupations (NCO-2015) designation.'],
      ['AI_Driven_2', 'Cross-references user profiles against the 338 official Framework of Roles, Activities, and Competencies (FRAC) standards.'],
    ] },
    { icon: BookOpenCheck, key: 'Intelligent_iGOT', title: <>Intelligent iGOT<br/>Course Mapping</>, points: [
      ['Intelligent_iGOT_1', 'Eliminates manual catalog searching by programmatically recommending the exact iGOT Sunbird courses needed to bridge identified competency gaps.'],
      ['Intelligent_iGOT_2', 'Filters over 8,000 authentic government training modules based on the official\'s specific career trajectory and missing skills.'],
    ] },
    { icon: FileQuestion, key: 'Auto_RAG', title: <>Automated RAG<br/>Document-to-Quiz</>, points: [
      ['Auto_RAG_1', 'Allows officials to upload standard government documents (PDF, PPTX, DOCX) to instantly generate custom multiple-choice assessments.'],
      ['Auto_RAG_2', 'Evaluates domain knowledge dynamically without requiring pre-authored tests from administrators.'],
    ] },
    { icon: RefreshCw, key: 'Real_Time', title: <>Real-Time Karmayogi<br/>Synchronization</>, points: [
      ['Real_Time_1', 'Automatically communicates with the iGOT portal backend to log achievements.'],
      ['Real_Time_2', 'Upgrades an official\'s FRAC competency level on the national registry the moment they score 70% or higher on an assessment.'],
    ] },
    { icon: Shield, key: 'Air_Gapped', title: <>Air-Gapped NLP<br/>Assistant</>, points: [
      ['Air_Gapped_1', 'Provides an interactive, zero-latency chat interface for navigating courses, analyzing gaps, and triggering assessments.'],
      ['Air_Gapped_2', 'Utilizes a secure, embedded deterministic intent-routing engine (no external API keys) to guarantee 100% data sovereignty for sensitive MoSPI environments.'],
    ] },
    { icon: LayoutDashboard, key: 'Dashboard', title: <>Ministry-Wide Analytics<br/>Dashboard</>, points: [
      ['Dashboard_1', 'Aggregates training telemetry to give administrators a macro-view of capacity building across different MoSPI wings (NSO, CSO).'],
      ['Dashboard_2', 'Visualizes resolved skill gaps, active certifications, and departmental readiness in real-time.'],
    ] },
  ] as const;

  const pillars = [
    { key: 'FRAC', title: 'FRAC-Aligned Framework', dKey: 'FRAC_Desc', desc: 'We map authentic National Classification of Occupations (NCO-2015) job profiles directly to the 338 standardized competencies defined by FRAC. This ensures every learning recommendation is mathematically targeted to an official\'s actual career trajectory.' },
    { key: 'iGOT', title: 'Intelligent iGOT Integration', dKey: 'iGOT_Desc', desc: 'By deeply integrating with the national iGOT Sunbird registry, we sift through over 8,000 official training modules to recommend precise courses needed to bridge identified gaps, while automatically syncing new achievements back to the central government database.' },
    { key: 'Dynamic_AI', title: 'Dynamic AI Evaluation', dKey: 'Dynamic_AI_Desc', desc: 'Through our proprietary Retrieval-Augmented Generation (RAG) pipeline, the platform allows departments to instantly generate custom assessments from internal policy documents, presentations, and manuals, ensuring officials are tested on the most relevant departmental knowledge.' },
  ];

  // Hero outcome rail — what the platform delivers, not simulated metrics
  const outcomes = [
    {
      icon: Users, key: 'Assess_Gaps', title: 'Assess Skill Gaps',
      dKey: 'Assess_Gaps_Desc', desc: 'Data-driven analysis for targeted learning',
      ring: 'border-gov-saffron', tint: 'bg-gov-saffron-deep',
    },
    {
      icon: BookOpen, key: 'Personalised', title: 'Personalized Learning',
      dKey: 'Personalised_Desc', desc: 'Role-based course recommendations',
      ring: 'border-[#60a5fa]', tint: 'bg-[#2563eb]',
    },
    {
      icon: BarChart3, key: 'Governance', title: 'Stronger Governance',
      dKey: 'Governance_Desc', desc: 'A future-ready statistical ecosystem',
      ring: 'border-[#4ade80]', tint: 'bg-gov-green',
    },
  ];

  return (
    <div className="font-sans relative bg-gov-paper dark:bg-[#07111f] text-slate-700 dark:text-slate-200 overflow-x-hidden transition-colors duration-300">
      <a href="#main" className="skip-link">{t('Skip', 'Skip to main content')}</a>

      {/* ── GoI utility strip: identity + the statutory accessibility controls,
             shared with the policy pages and the dashboards. ─────────────── */}
      <GovUtilityBar mainId="main" screenReader={screenReader} />
      <div className="tricolor-strip" />

      {/* ── Ministry header ─────────────────────────────────────────────── */}
      <header role="banner" className="relative z-20 bg-white dark:bg-[#0b1628] border-b border-gov-line dark:border-slate-800 transition-colors duration-300">
        <div className="max-w-[1320px] mx-auto px-4 md:px-8 py-4 flex items-center justify-between gap-6">
          <a href="#" onClick={(e) => scrollToSection(e, 'home')} className="flex items-center gap-4 group">
            <GovEmblem size={58} className="transition-transform duration-500 group-hover:scale-105" />
            <div className="flex flex-col">
              <span className="text-[10.5px] font-bold uppercase tracking-[0.14em] text-gov-blue dark:text-sky-300 leading-tight">
                Ministry of Statistics &amp; Programme Implementation
              </span>
              <span className="font-serif font-bold text-gov-ink dark:text-white text-[20px] md:text-[26px] leading-tight">
                KarmaSkill
              </span>
              <span className="text-[10px] text-slate-500 dark:text-slate-400 font-bold tracking-[0.18em] uppercase mt-0.5">
                {t('SIP', 'Skill Intelligence Platform')} · {t('GoI', 'Government of India')}
              </span>
            </div>
          </a>

          <div className="hidden lg:flex items-center gap-5">
            <div className="flex items-center gap-3 pr-5 border-r border-gov-line dark:border-slate-700">
              <div className="text-right leading-tight">
                <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400">In partnership with</div>
                <div className="font-serif font-bold text-gov-navy dark:text-sky-300 text-[14px]">iGOT Karmayogi</div>
              </div>
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gov-saffron via-white to-gov-green p-[2px]">
                <div className="w-full h-full rounded-full bg-white dark:bg-[#0b1628] flex items-center justify-center font-black text-[11px] text-gov-navy dark:text-white">MK</div>
              </div>
            </div>
            <button onClick={() => setIsLoginModalOpen(true)} className="gov-btn-primary">
              <User size={15} /> {t('OFFICIAL_LOGIN', 'Official Login')}
            </button>
            <button onClick={() => setIsLoginModalOpen(true)} className="gov-btn-outline">
              <Shield size={15} /> {t('ADMIN_PORTAL', 'Admin Portal')}
            </button>
          </div>

          <button
            className="lg:hidden p-2 rounded-lg text-gov-navy dark:text-white hover:bg-slate-100 dark:hover:bg-slate-800"
            onClick={() => setMobileNavOpen(v => !v)}
            aria-expanded={mobileNavOpen}
            aria-controls="primary-nav"
            aria-label={mobileNavOpen ? 'Close menu' : 'Open menu'}
          >
            {mobileNavOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </header>

      {/* ── Primary navigation (sticky) ─────────────────────────────────── */}
      <nav aria-label="Primary" className={`sticky top-0 z-40 bg-gov-navy text-white transition-shadow duration-300 ${scrolled ? 'shadow-gov-lg' : ''}`}>
        <div className="max-w-[1320px] mx-auto px-4 md:px-8 flex items-center justify-between">
          <ul id="primary-nav" className={`${mobileNavOpen ? 'flex' : 'hidden'} lg:flex flex-col lg:flex-row w-full lg:w-auto py-2 lg:py-0`}>
            {navItems.map(item => (
              <li key={item.id}>
                <a
                  href={`#${item.id}`}
                  onClick={(e) => scrollToSection(e, item.id)}
                  className="block px-4 lg:px-5 py-3 text-[13px] font-semibold tracking-wide text-white/85 hover:text-white hover:bg-white/5 transition-colors"
                >
                  <span className="nav-link">{t(item.key, item.label)}</span>
                </a>
              </li>
            ))}
            <li className="lg:hidden flex gap-2 px-4 py-3">
              <button onClick={() => setIsLoginModalOpen(true)} className="gov-btn-saffron flex-1">{t('OFFICIAL_LOGIN', 'Official Login')}</button>
              <button onClick={() => setIsLoginModalOpen(true)} className="flex-1 rounded-lg border border-white/60 text-[13px] font-bold">{t('ADMIN_PORTAL', 'Admin Portal')}</button>
            </li>
          </ul>
          <div className={`hidden lg:flex items-center gap-3 transition-all duration-500 ${scrolled ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-1 pointer-events-none'}`}>
            <button onClick={() => setIsLoginModalOpen(true)} className="gov-btn-saffron !py-1.5 !text-[12px]">
              {t('OFFICIAL_LOGIN', 'Official Login')} <ArrowRight size={13} />
            </button>
          </div>
        </div>
      </nav>

      {/* ── What's New ticker ─────────────────────────────────────────────
             WCAG 2.2.2: content that moves for more than five seconds needs a
             way to stop it, so the strip carries a pause control as well as
             pausing on hover and on keyboard focus. The marquee duplicates the
             items to loop seamlessly — the second copy is hidden from assistive
             technology so the headlines are announced once. */}
      <section aria-label={t('Whats_New', "What's New") as string} className="relative z-10 bg-white dark:bg-[#0b1628] border-b border-gov-line dark:border-slate-800 transition-colors duration-300">
        <div className="max-w-[1320px] mx-auto flex items-stretch">
          <h2 className="flex items-center gap-2 bg-gov-saffron text-gov-ink px-4 md:px-5 text-[12px] font-bold uppercase tracking-wider shrink-0 [clip-path:polygon(0_0,100%_0,calc(100%-10px)_100%,0_100%)] pr-6">
            <Megaphone size={14} aria-hidden="true" /> {t('Whats_New', "What's New")}
          </h2>
          <div className="relative flex-1 overflow-hidden py-2.5 group [mask-image:linear-gradient(90deg,transparent,black_4%,black_96%,transparent)]">
            <ul
              className="flex w-max animate-marquee group-hover:[animation-play-state:paused] focus-within:[animation-play-state:paused]"
              style={tickerPaused ? { animationPlayState: 'paused' } : undefined}
            >
              {[...NEWS_ITEMS, ...NEWS_ITEMS].map((n, i) => (
                <li
                  key={i}
                  aria-hidden={i >= NEWS_ITEMS.length ? 'true' : undefined}
                  className="flex items-center gap-2 px-8 text-[12.5px] font-medium text-slate-600 dark:text-slate-300 whitespace-nowrap"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-gov-green" aria-hidden="true" /> {n}
                  {i % NEWS_ITEMS.length === 0 && <span className="ml-1 text-[9px] font-black px-1.5 py-0.5 rounded bg-red-600 text-white">NEW</span>}
                </li>
              ))}
            </ul>
          </div>
          <button
            type="button"
            onClick={() => setTickerPaused(p => !p)}
            aria-pressed={tickerPaused}
            className="shrink-0 px-3 text-slate-500 hover:text-gov-navy dark:text-slate-400 dark:hover:text-white transition-colors"
            title={tickerPaused ? 'Resume the headlines' : 'Pause the headlines'}
            aria-label={tickerPaused ? 'Resume the scrolling headlines' : 'Pause the scrolling headlines'}
          >
            {tickerPaused ? <Play size={14} aria-hidden="true" /> : <Pause size={14} aria-hidden="true" />}
          </button>
        </div>
      </section>

      <main id="main" tabIndex={-1}>
        {/* ── Hero ───────────────────────────────────────────────────────── */}
        <section id="home" className="relative overflow-hidden bg-gov-navy text-white">
          {/* Hero artwork (chakra, growth bars, orbit arc) — gradient stays behind it
              so the section still reads correctly if the image fails to load. */}
          <div className="absolute inset-0 bg-gradient-to-br from-gov-ink via-gov-navy to-gov-blue" />
          <div
            aria-hidden="true"
            className="absolute inset-0 bg-cover bg-center bg-no-repeat"
            style={{ backgroundImage: 'url("/hero-bg-blue.png")' }}
          />
          {/* Left-side scrim keeps the headline legible over the artwork */}
          <div className="absolute inset-0 bg-gradient-to-r from-gov-ink/80 via-gov-ink/35 to-transparent" />

          <div className="relative max-w-[1320px] mx-auto px-4 md:px-8 py-16 md:py-24 grid grid-cols-1 lg:grid-cols-[1.15fr_0.85fr] gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 border border-white/15 backdrop-blur text-[11.5px] font-semibold mb-6 animate-fade-up">
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full rounded-full bg-gov-saffron opacity-75 animate-ping" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-gov-saffron" />
                </span>
                KarmaSkill · {t('Powered', 'Powered by MoSPI AI Engine')}
              </div>

              <h1 className="font-serif text-[36px] sm:text-[46px] md:text-[56px] leading-[1.1] font-black tracking-tight mb-6 animate-fade-up [animation-delay:120ms]">
                {lang === 'en' ? (
                  <>Empowering India&apos;s <span className="bg-gradient-to-r from-gov-saffron via-[#ffd08a] to-[#86efac] bg-clip-text text-transparent">Official Statistical</span> System</>
                ) : translations['Empowering']}
              </h1>

              <p className="text-[16px] md:text-[17px] text-white/80 max-w-[560px] leading-[1.7] mb-8 animate-fade-up [animation-delay:240ms]">
                {t('Hero_Desc', 'A next-generation competency tracking platform. We combine AI-driven skill-gap analysis with personalized iGOT learning pathways.')}
              </p>

              <div className="flex flex-wrap gap-3 mb-12 animate-fade-up [animation-delay:360ms]">
                <button onClick={() => setIsLoginModalOpen(true)} className="gov-btn-saffron !px-7 !py-3.5 !text-[14px] group">
                  {t('LOGIN_AS', 'Login as Official')} <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />
                </button>
                <button onClick={() => setIsLoginModalOpen(true)} className="inline-flex items-center gap-2 px-7 py-3.5 rounded-lg border-[1.5px] border-white/60 text-white text-[14px] font-bold hover:bg-white hover:text-gov-ink transition-all duration-300">
                  <Shield size={16} /> {t('ADMIN_PORTAL', 'Admin Portal')}
                </button>
              </div>

              <div className="animate-fade-up [animation-delay:480ms]">
                <h4 className="text-[11px] font-bold text-white/60 tracking-[0.2em] mb-4 uppercase">{t('Capabilities', 'Platform Capabilities')}</h4>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
                  {capabilities.map(({ icon: Icon, key, title, dKey, desc }) => (
                    <a
                      key={key}
                      href="#features"
                      onClick={(e) => scrollToSection(e, 'features')}
                      className="group/cap relative flex flex-col gap-3 rounded-xl border border-white/10 bg-white/[0.06] p-4 pb-9 text-left transition-all duration-300 hover:-translate-y-0.5 hover:border-white/25 hover:bg-white/[0.12]"
                    >
                      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-white/10 text-gov-saffron transition-colors duration-300 group-hover/cap:bg-gov-saffron group-hover/cap:text-gov-ink">
                        <Icon size={19} aria-hidden="true" />
                      </span>
                      <span>
                        <span className="block text-[14px] font-bold leading-tight">{t(key, title)}</span>
                        <span className="mt-1 block text-[11.5px] leading-snug text-white/65">{t(dKey, desc)}</span>
                      </span>
                      <ArrowRight
                        size={15}
                        aria-hidden="true"
                        className="absolute bottom-3.5 right-4 text-white/40 transition-all duration-300 group-hover/cap:translate-x-0.5 group-hover/cap:text-gov-saffron"
                      />
                    </a>
                  ))}
                </div>
              </div>
            </div>

            {/* Outcome rail — what the platform is for */}
            <div className="relative hidden lg:block animate-fade-in [animation-delay:400ms]">
              <h4 className="text-[12.5px] font-bold uppercase tracking-[0.18em] text-white/55 leading-relaxed mb-7">
                {t('Building', <>Building a more<br /><span className="text-white/85">competent statistical workforce</span></>)}
              </h4>

              <ol className="relative space-y-5 pl-2">
                {/* Curved connector echoing the orbit arc in the hero artwork */}
                <svg
                  aria-hidden="true"
                  className="pointer-events-none absolute left-0 top-0 h-full w-[60px] overflow-visible"
                  viewBox="0 0 60 300"
                  preserveAspectRatio="none"
                >
                  <path
                    d="M29 34 C -6 110, -6 190, 29 266"
                    fill="none"
                    stroke="url(#railGrad)"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                  />
                  <defs>
                    <linearGradient id="railGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#ff9933" stopOpacity="0.7" />
                      <stop offset="50%" stopColor="#ffffff" stopOpacity="0.35" />
                      <stop offset="100%" stopColor="#4ade80" stopOpacity="0.7" />
                    </linearGradient>
                  </defs>
                </svg>
                {outcomes.map(({ icon: Icon, key, title, dKey, desc, ring, tint }, i) => (
                  <li
                    key={key}
                    className="relative flex items-center gap-4 animate-fade-up"
                    style={{ animationDelay: `${520 + i * 140}ms` }}
                  >
                    <span className={`relative z-10 flex h-[58px] w-[58px] shrink-0 items-center justify-center rounded-full border-[3px] ${ring} ${tint} shadow-gov-lg`}>
                      <Icon size={25} className="text-white" strokeWidth={1.9} aria-hidden="true" />
                    </span>
                    <span className="flex-1 rounded-xl border border-white/10 bg-white/[0.07] px-5 py-3.5 backdrop-blur transition-all duration-300 hover:border-white/25 hover:bg-white/[0.12]">
                      <span className="block text-[14.5px] font-bold leading-tight">{t(key, title)}</span>
                      <span className="mt-1 block text-[12px] leading-snug text-white/65">{t(dKey, desc)}</span>
                    </span>
                  </li>
                ))}
              </ol>
            </div>
          </div>
          <div className="tricolor-strip opacity-90" />
        </section>

        {/* ── Metrics ────────────────────────────────────────────────────── */}
        <section className="relative z-10 -mt-px bg-white dark:bg-[#0b1628] border-b border-gov-line dark:border-slate-800 transition-colors duration-300">
          <div className="max-w-[1320px] mx-auto grid grid-cols-2 md:grid-cols-4">
            {stats.map(({ icon: Icon, end, decimals, suffix, key, label }, i) => (
              <Reveal key={key} delay={i * 90} className={`group flex items-center justify-center gap-4 py-8 px-4 ${i > 0 ? 'md:border-l' : ''} ${i % 2 === 1 ? 'border-l md:border-l' : ''} ${i > 1 ? 'border-t md:border-t-0' : ''} border-gov-line dark:border-slate-800`}>
                <div className="w-12 h-12 rounded-xl bg-gov-navy/5 dark:bg-sky-400/10 text-gov-navy dark:text-sky-300 flex items-center justify-center transition-all duration-300 group-hover:bg-gov-navy group-hover:text-white group-hover:-rotate-6">
                  <Icon size={22} />
                </div>
                <div>
                  <CountUp end={end} decimals={decimals} suffix={suffix} className="block font-serif text-[28px] md:text-[32px] font-black text-gov-ink dark:text-white leading-none" />
                  <p className="text-[10.5px] font-bold text-slate-500 dark:text-slate-400 tracking-[0.15em] uppercase mt-1.5">{t(key, label)}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </section>

        {/* ── Features ───────────────────────────────────────────────────── */}
        <section id="features" className="relative gov-page-bg py-20 md:py-28 scroll-mt-12 transition-colors duration-300">
          <div className="max-w-[1320px] mx-auto px-4 md:px-8">
            <Reveal className="text-center max-w-3xl mx-auto mb-14">
              <span className="gov-eyebrow justify-center"><span className="w-6 h-px bg-current" /> {t('Features', 'Features')} <span className="w-6 h-px bg-current" /></span>
              <h2 className="font-serif text-[28px] md:text-[40px] font-black text-gov-ink dark:text-white mt-3 leading-tight tracking-tight">
                {t('Key_Features', 'Key Features of MoSPI Skill Enhancement')}
              </h2>
              <div className="mx-auto mt-5 w-24 h-1 rounded-full bg-gradient-to-r from-gov-saffron via-white to-gov-green shadow-sm" />
            </Reveal>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {features.map(({ icon: Icon, key, title, points }, i) => (
                <Reveal key={key} delay={(i % 3) * 110}>
                  <div className="gov-card gov-card-hover group h-full p-7 overflow-hidden">
                    <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-gov-saffron via-gov-gold to-gov-green origin-left scale-x-0 group-hover:scale-x-100 transition-transform duration-500" />
                    <div className="absolute -right-10 -bottom-10 text-gov-navy/[0.04] dark:text-white/[0.04] transition-transform duration-700 group-hover:rotate-45">
                      <AshokaChakra size={160} />
                    </div>
                    <div className="flex items-center gap-4 mb-5">
                      <div className="w-14 h-14 shrink-0 rounded-xl bg-gov-navy text-white flex items-center justify-center shadow-gov transition-all duration-300 group-hover:bg-gov-saffron group-hover:text-gov-ink group-hover:scale-105">
                        <Icon size={26} strokeWidth={1.7} />
                      </div>
                      <div>
                        <div className="text-[11px] font-bold text-slate-400 tracking-widest">0{i + 1}</div>
                        <h3 className="text-[16.5px] font-bold text-gov-ink dark:text-white leading-snug">{t(key, title)}</h3>
                      </div>
                    </div>
                    <ul className="relative space-y-3 text-[13.5px] text-slate-600 dark:text-slate-300 leading-[1.65]">
                      {points.map(([pk, pt]) => (
                        <li key={pk} className="flex gap-2.5">
                          <ChevronRight size={16} className="mt-[3px] shrink-0 text-gov-saffron-deep" />
                          <span>{t(pk, pt)}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        {/* ── About ──────────────────────────────────────────────────────── */}
        <section id="about" className="relative bg-white dark:bg-[#0b1628] py-20 md:py-28 border-t border-gov-line dark:border-slate-800 scroll-mt-12 transition-colors duration-300">
          <div className="max-w-[1320px] mx-auto px-4 md:px-8 grid grid-cols-1 lg:grid-cols-2 gap-14 items-start">
            <Reveal>
              <span className="gov-eyebrow"><span className="w-6 h-px bg-current" /> {t('About_Platform', 'About The Platform')}</span>
              <h2 className="font-serif text-[30px] md:text-[42px] font-black text-gov-ink dark:text-white mt-3 mb-6 leading-[1.12] tracking-tight">
                {t('Transforming', <>Transforming India&apos;s Statistical Workforce</>)}
              </h2>
              <p className="text-[15.5px] text-slate-600 dark:text-slate-300 leading-[1.8] mb-8">
                {t('Rooted', 'Rooted in the mandate of Mission Karmayogi, the MoSPI Skill Intelligence Platform is a next-generation capacity-building ecosystem. It transitions civil servants from a rule-based to a role-based framework by aligning specific operational duties with standardized national competencies.')}
              </p>

              <div className="relative rounded-2xl bg-gradient-to-br from-gov-navy to-gov-blue text-white p-7 overflow-hidden shadow-gov-lg">
                <div className="absolute -right-12 -top-12 text-white/10"><AshokaChakra size={180} className="animate-spin-slow" /></div>
                <h4 className="relative text-[12px] font-bold uppercase tracking-[0.2em] text-gov-saffron mb-3">{t('Our_Mission', 'Our Mission')}</h4>
                <p className="relative text-[15px] leading-[1.75] text-white/90">
                  {t('Our_Mission_Desc', 'To modernize the Ministry of Statistics and Programme Implementation (MoSPI) by providing an intelligent, data-sovereign infrastructure that autonomously identifies skill gaps, curates personalized learning pathways, and evaluates domain mastery in real-time.')}
                </p>
              </div>

              <div className="mt-8 flex gap-4 p-5 rounded-2xl border border-gov-green/25 bg-gov-green/[0.05]">
                <div className="w-11 h-11 shrink-0 rounded-xl bg-gov-green text-white flex items-center justify-center"><Shield size={20} /></div>
                <div>
                  <h4 className="text-[15px] font-bold text-gov-ink dark:text-white mb-1.5">{t('Built_For', 'Built for Sovereignty & Security')}</h4>
                  <p className="text-[14px] text-slate-600 dark:text-slate-400 leading-[1.7]">
                    {t('Built_For_Desc', 'Operating within the sensitive environment of the national statistical system requires uncompromising data security. Our completely air-gapped, deterministic intent-routing NLP engine ensures all interactions, evaluations, and telemetry remain strictly within the government intranet without reliance on external commercial API keys.')}
                  </p>
                </div>
              </div>
            </Reveal>

            <div className="lg:pt-14">
              <Reveal>
                <h3 className="gov-heading text-[20px] mb-8">{t('Arch', 'Architecture of Continuous Learning')}</h3>
              </Reveal>
              <ol className="relative space-y-6 before:absolute before:left-[23px] before:top-3 before:bottom-3 before:w-[2px] before:bg-gradient-to-b before:from-gov-saffron before:via-gov-gold before:to-gov-green">
                {pillars.map(({ key, title, dKey, desc }, i) => (
                  <Reveal as="li" key={key} delay={i * 140} className="relative flex gap-5">
                    <div className="relative z-10 w-12 h-12 shrink-0 rounded-full bg-white dark:bg-[#0b1628] border-2 border-gov-navy dark:border-sky-400 text-gov-navy dark:text-sky-300 flex items-center justify-center font-serif font-black text-[18px] shadow-gov">
                      {i + 1}
                    </div>
                    <div className="gov-card gov-card-hover flex-1 p-6">
                      <h4 className="text-[15.5px] font-bold text-gov-ink dark:text-white mb-2">{t(key, title)}</h4>
                      <p className="text-[13.5px] text-slate-600 dark:text-slate-300 leading-[1.7]">{t(dKey, desc)}</p>
                    </div>
                  </Reveal>
                ))}
              </ol>
            </div>
          </div>
        </section>
      </main>

      {/* ── Footer ───────────────────────────────────────────────────────────
             The columns after the brand block (Website Policies, Related
             Portals, Web Information Manager) and the statutory lines beneath
             them come from GovFooter, shared with the policy pages. ─────── */}
      <GovFooter
        id="contact"
        brand={
          <div>
            <div className="flex items-center gap-3 mb-4">
              <GovEmblem size={46} />
              <div>
                <div className="font-serif font-bold text-white text-[18px] leading-tight">KarmaSkill</div>
                <div className="text-[11px] text-white/55 font-bold uppercase tracking-[0.14em]">
                  Ministry of Statistics &amp; Programme Implementation
                </div>
              </div>
            </div>
            <p className="text-[13px] leading-[1.7] text-white/60 mb-5">
              KarmaSkill, the {t('SIP', 'Skill Intelligence Platform')} — evidence-based competency baselines,
              skill-gap analysis and iGOT learning pathways for officials of the National Statistical System.
            </p>
            <h2 className="text-white text-[12px] font-bold uppercase tracking-[0.16em] mb-3">
              {t('Quick_Links', 'Quick Links')}
            </h2>
            <ul className="space-y-2 text-[13px]">
              {navItems.slice(0, 3).map(item => (
                <li key={item.id}>
                  <a href={`#${item.id}`} onClick={(e) => scrollToSection(e, item.id)} className="inline-flex items-center gap-1.5 hover:text-gov-saffron hover:underline">
                    <ChevronRight size={13} aria-hidden="true" /> {t(item.key, item.label)}
                  </a>
                </li>
              ))}
              <li>
                <button onClick={() => setIsLoginModalOpen(true)} className="inline-flex items-center gap-1.5 hover:text-gov-saffron hover:underline">
                  <ChevronRight size={13} aria-hidden="true" /> {t('OFFICIAL_LOGIN', 'Official Login')}
                </button>
              </li>
            </ul>
          </div>
        }
      />

      {/* Login Modal Overlay */}
      {isLoginModalOpen && (
        <LoginPage isModal onClose={() => setIsLoginModalOpen(false)} />
      )}

      {/* Gyan AI — Homepage Chat Widget */}
      <HomeChatWidget
        onScrollToSection={(id) => {
          if (id === 'home') window.scrollTo({ top: 0, behavior: 'smooth' });
          else document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
        }}
        onOpenLogin={() => setIsLoginModalOpen(true)}
        lang={lang}
        onLanguageChange={(l) => { screenReader.stop(); setLang(l); }}
      />
    </div>
  );
};

export default LandingPage;
