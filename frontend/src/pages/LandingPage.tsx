import React, { useState } from 'react';
import { Search, Settings, User, BookOpen, Activity, Award, Cpu, TabletSmartphone, Route, Moon, Sun, BrainCircuit, BookOpenCheck, FileQuestion, RefreshCw, Shield, LayoutDashboard } from 'lucide-react';
import { useTheme } from '../hooks/useTheme';
import LoginPage from './LoginPage';
import HomeChatWidget from '../components/home/HomeChatWidget';


const translations: Record<string, React.ReactNode> = {
  "MoSPI": <>सांख्यिकी और कार्यक्रम कार्यान्वयन<br />मंत्रालय (MoSPI)</>,
  "SIP": "कौशल बुद्धिमत्ता मंच",
  "Home": "होम",
  "About": "के बारे में",
  "Features": "विशेषताएँ",
  "Contact": "संपर्क",
  "Eng_Hi": "Eng | हिंदी",
  "OFFICIAL_LOGIN": "अधिकारी लॉगिन",
  "ADMIN_PORTAL": "एडमिन पोर्टल",
  "Powered": "MoSPI एआई इंजन द्वारा संचालित",
  "Empowering": <>भारत की आधिकारिक सांख्यिकीय<br/>प्रणाली को सशक्त बनाना</>,
  "Hero_Desc": "एक अगली पीढ़ी का क्षमता ट्रैकिंग मंच। हम एआई-संचालित कौशल-अंतर विश्लेषण को व्यक्तिगत iGOT सीखने के मार्गों के साथ जोड़ते हैं।",
  "LOGIN_AS": "अधिकारी के रूप में लॉगिन करें",
  "Capabilities": "प्लेटफ़ॉर्म क्षमताएं",
  "Skill_Analysis": "कौशल विश्लेषण",
  "Skill_Analysis_Desc": <>सुसंगत विश्लेषण की<br/>गणना करें।</>,
  "iGOT_Learning": "iGOT लर्निंग",
  "iGOT_Learning_Desc": <>लिंक किए गए<br/>पाठ्यक्रम पुस्तकें।</>,
  "Career_Pathways": "करियर पाथवे",
  "Career_Pathways_Desc": <>एकीकृत रोडमैप और<br/>करियर पाथवे।</>,
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
  "Footer_1": "सांख्यिकी और कार्यक्रम कार्यान्वयन मंत्रालय (MoSPI) | भारत सरकार",
  "Privacy": "गोपनीयता नीति",
  "Terms": "नियम",
  "Help": "मदद और अक्सर पूछे जाने वाले प्रश्न"
};

const LandingPage: React.FC = () => {

  const { theme, toggleTheme } = useTheme();
  const [lang, setLang] = useState<'en' | 'hi'>('en');
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);

  
  const t = (key: string, enText: string | React.ReactNode) => {
    return lang === 'en' ? enText : translations[key] || enText;
  };


  const scrollToSection = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
    e.preventDefault();
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    } else if (id === 'home') {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <div className="font-sans relative bg-[#fafaf9] dark:bg-[#0f172a] text-[#333] dark:text-[#e2e8f0] overflow-x-hidden transition-colors duration-300">
      <div className="min-h-screen flex flex-col pb-[100px] md:pb-[42px]">
      {/* Background Image Layer */}
      <div 
        className="fixed inset-0 z-0 pointer-events-none"
        style={{
          backgroundImage: `url(${theme === 'dark' ? '/hero-bg-dark.png' : '/hero-bg-topo.png'})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          opacity: 1 // Match the first image exactly
        }}
      />

      {/* Top Navbar */}
      <header className="relative z-10 w-full bg-[#fdfdfc] dark:bg-[#1e293b] py-[12px] px-6 md:px-12 flex items-center justify-between shadow-[0_1px_4px_rgba(0,0,0,0.06)] dark:shadow-[0_1px_4px_rgba(0,0,0,0.5)] transition-colors duration-300">
        {/* Left: Logo Text */}
        <div className="flex items-center gap-3">
          <div className="flex flex-col justify-center">
            <div className="font-bold text-[#1f2d4d] dark:text-white text-[15.5px] leading-[1.2]">
              {t('MoSPI', <>Ministry of Statistics & <br /> Programme Implementation (MoSPI)</>)}
            </div>
            <div className="text-[9px] text-[#6b7280] dark:text-[#94a3b8] font-bold tracking-[0.15em] uppercase mt-0.5">
              {t('SIP', 'Skill Intelligence Platform')}
            </div>
          </div>
        </div>

        {/* Center Nav & Right Actions */}
        <div className="flex items-center gap-9">
          <nav className="hidden lg:flex items-center gap-6 text-[11px] font-bold text-[#555] dark:text-[#cbd5e1] tracking-wide uppercase">
            <a href="#" onClick={(e) => scrollToSection(e, 'home')} className="hover:text-[#1f2d4d] dark:hover:text-white transition-colors">{t('Home', 'Home')}</a>
            <a href="#about" onClick={(e) => scrollToSection(e, 'about')} className="hover:text-[#1f2d4d] dark:hover:text-white transition-colors">{t('About', 'About')}</a>
            <a href="#features" onClick={(e) => scrollToSection(e, 'features')} className="hover:text-[#1f2d4d] dark:hover:text-white transition-colors">{t('Features', 'Features')}</a>
            <a href="#contact" className="hover:text-[#1f2d4d] dark:hover:text-white transition-colors">{t('Contact', 'Contact')}</a>
          </nav>
          
          <div className="hidden lg:flex items-center gap-4 text-[#555] dark:text-[#cbd5e1]">
            <button aria-label="Search"><Search size={16} strokeWidth={2.5} /></button>
            <span className="text-[12px] font-bold px-1.5 border-r border-[#d1d5db] dark:border-[#475569] flex gap-1.5">
              <button onClick={() => setLang('en')} className={lang === 'en' ? 'text-[#1f2d4d] dark:text-white' : 'hover:text-[#1f2d4d] dark:hover:text-white transition-colors'}>Eng</button>
              <span>|</span>
              <button onClick={() => setLang('hi')} className={lang === 'hi' ? 'text-[#1f2d4d] dark:text-white' : 'hover:text-[#1f2d4d] dark:hover:text-white transition-colors'}>हिंदी</button>
            </span>
            <button aria-label="Toggle Theme" onClick={toggleTheme} className="hover:text-[#1f2d4d] dark:hover:text-white transition-colors">
              {theme === 'dark' ? <Sun size={16} strokeWidth={2.5} /> : <Moon size={16} strokeWidth={2.5} />}
            </button>
            <button aria-label="Settings"><Settings size={16} strokeWidth={2.5} /></button>
          </div>

          <div className="flex items-center gap-3 ml-2">
            <button onClick={() => setIsLoginModalOpen(true)} className="px-5 py-[9px] bg-[#1f2d4d] dark:bg-[#3b82f6] text-white text-[11px] font-bold rounded-[6px] hover:bg-[#2c3d63] dark:hover:bg-[#2563eb] transition-colors tracking-wide leading-none shadow-sm">
              OFFICIAL LOGIN
            </button>
            <button onClick={() => setIsLoginModalOpen(true)} className="px-5 py-[8px] bg-white dark:bg-transparent border-[1.5px] border-[#1f2d4d] dark:border-white text-[#1f2d4d] dark:text-white text-[11px] font-bold rounded-[6px] hover:bg-[#f8fafc] dark:hover:bg-white/10 transition-colors tracking-wide leading-none">
              ADMIN PORTAL
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="relative z-10 flex-1 w-full max-w-[1400px] mx-auto px-6 md:px-[60px] grid grid-cols-1 lg:grid-cols-[1.1fr_0.9fr] items-center gap-6 py-6 md:py-[30px]">
        
        {/* Left Column */}
        <div className="flex flex-col items-start z-10">
          <div className="inline-flex items-center px-[14px] py-[6px] rounded-full bg-[#eef0f3] dark:bg-[#1e293b] text-[#555] dark:text-[#cbd5e1] text-[11px] font-bold mb-4 tracking-wide shadow-sm transition-colors duration-300">
            <span className="text-[#666] dark:text-[#94a3b8] mr-1.5 text-[14px] font-black leading-none">#</span> {t('Powered', 'Powered by MoSPI AI Engine')}
          </div>
          
          <h1 className="text-[44px] md:text-[56px] leading-[1.08] font-[800] tracking-tight text-[#1a1a1a] dark:text-white mb-4 w-[110%] uppercase transition-colors duration-300">
            {t('Empowering', <>EMPOWERING INDIA'S <br/>OFFICIAL STATISTICAL <br/>SYSTEM</>)}
          </h1>
          
          <p className="text-[15.5px] text-[#444] dark:text-[#cbd5e1] max-w-[520px] leading-[1.6] font-medium mb-6 transition-colors duration-300">
            A next-generation competency tracking platform. We combine AI-driven skill-gap analysis with personalized iGOT learning pathways.
          </p>
          
          <div className="flex gap-[16px] mb-8">
            <button onClick={() => setIsLoginModalOpen(true)} className="px-[30px] py-[13px] bg-[#1f2d4d] dark:bg-[#3b82f6] text-white text-[13px] font-bold rounded-[6px] hover:bg-[#2c3d63] dark:hover:bg-[#2563eb] transition-colors tracking-wide leading-none shadow-md">
              LOGIN AS OFFICIAL
            </button>
            <button onClick={() => setIsLoginModalOpen(true)} className="px-[30px] py-[11.5px] bg-white dark:bg-transparent border-[1.5px] border-[#1f2d4d] dark:border-white text-[#1f2d4d] dark:text-white text-[13px] font-bold rounded-[6px] hover:bg-[#f8fafc] dark:hover:bg-white/10 transition-colors tracking-wide leading-none shadow-sm">
              ADMIN PORTAL
            </button>
          </div>

          {/* Capabilities */}
          <div className="w-full">
            <h4 className="text-[12px] font-bold text-[#222] dark:text-[#e2e8f0] tracking-[0.03em] mb-4 uppercase transition-colors duration-300">{t('Capabilities', 'Platform Capabilities')}</h4>
            <div className="flex items-start gap-9">
              
              <div className="flex gap-2.5">
                <div className="font-medium text-[15px] text-[#555] dark:text-[#94a3b8] pt-[1px] transition-colors duration-300">1.</div>
                <div className="relative w-8 h-8 flex items-center justify-center text-[#1f2d4d] dark:text-[#60a5fa] transition-colors duration-300">
                  <Cpu className="w-8 h-8 absolute inset-0 stroke-[1.2]" />
                  <span className="text-[9px] font-bold mt-[2px]">AI</span>
                </div>
                <div className="flex flex-col justify-start mt-[2px]">
                  <h5 className="font-bold text-[13.5px] text-[#111] dark:text-white mb-0.5 leading-none transition-colors duration-300">{t('Skill_Analysis', 'Skill Analysis')}</h5>
                  <p className="text-[11.5px] text-[#666] dark:text-[#94a3b8] leading-[1.3] transition-colors duration-300">{t('Skill_Analysis_Desc', <>Compute answer of<br/>soillfstent analysis.</>)}</p>
                </div>
              </div>
              
              <div className="flex gap-2.5">
                <div className="font-medium text-[15px] text-[#555] dark:text-[#94a3b8] pt-[1px] transition-colors duration-300">2.</div>
                <div className="relative w-8 h-8 flex items-center justify-center text-[#1f2d4d] dark:text-[#60a5fa] transition-colors duration-300">
                  <BookOpen className="w-8 h-8 absolute inset-0 stroke-[1.2]" />
                  <TabletSmartphone className="w-4 h-4 absolute bottom-[-2px] right-[-4px] bg-[#fafaf9] dark:bg-[#0f172a] rounded-[2px] stroke-[1.5] transition-colors duration-300" />
                </div>
                <div className="flex flex-col justify-start mt-[2px]">
                  <h5 className="font-bold text-[13.5px] text-[#111] dark:text-white mb-0.5 leading-none transition-colors duration-300">{t('iGOT_Learning', 'iGOT Learning')}</h5>
                  <p className="text-[11.5px] text-[#666] dark:text-[#94a3b8] leading-[1.3] transition-colors duration-300">{t('iGOT_Learning_Desc', <>Linked control-linked<br/>course books.</>)}</p>
                </div>
              </div>
              
              <div className="flex gap-2.5">
                <div className="font-medium text-[15px] text-[#555] dark:text-[#94a3b8] pt-[1px] transition-colors duration-300">3.</div>
                <Route className="w-8 h-8 text-[#1f2d4d] dark:text-[#60a5fa] stroke-[1.2] transition-colors duration-300" />
                <div className="flex flex-col justify-start mt-[2px]">
                  <h5 className="font-bold text-[13.5px] text-[#111] dark:text-white mb-0.5 leading-none transition-colors duration-300">{t('Career_Pathways', 'Career Pathways')}</h5>
                  <p className="text-[11.5px] text-[#666] dark:text-[#94a3b8] leading-[1.3] transition-colors duration-300">{t('Career_Pathways_Desc', <>Integratat roadmap and<br/>careeer pathways.</>)}</p>
                </div>
              </div>

            </div>
          </div>
        </div>

        {/* Right Column: (Map image removed as it is now baked into the background) */}
        <div className="relative flex flex-col justify-center items-end h-full mt-[-20px]">
        </div>
      </main>

      {/* Metrics Bar */}
      <section className="relative z-20 w-full bg-[#f1f2f4] dark:bg-[#1e293b] border-t border-[#e2e4e8] dark:border-[#334155] transition-colors duration-300">
        <div className="w-full max-w-[1440px] mx-auto grid grid-cols-2 md:grid-cols-4 divide-x divide-[#dce0e6] dark:divide-[#334155] py-[16px] transition-colors duration-300">
          <div className="flex flex-col items-center justify-center text-center">
            <User className="w-6 h-6 text-[#1f2d4d] dark:text-[#60a5fa] mb-1.5 stroke-[1.5] transition-colors duration-300" />
            <h3 className="text-[28px] font-[800] text-[#111] dark:text-white leading-none mb-1 transition-colors duration-300">12.4k</h3>
            <p className="text-[10px] font-bold text-[#666] dark:text-[#94a3b8] tracking-widest uppercase transition-colors duration-300">{t('Active_Users', 'Active Users')}</p>
          </div>
          <div className="flex flex-col items-center justify-center text-center">
            <BookOpen className="w-6 h-6 text-[#1f2d4d] dark:text-[#60a5fa] mb-1.5 stroke-[1.5] transition-colors duration-300" />
            <h3 className="text-[28px] font-[800] text-[#111] dark:text-white leading-none mb-1 transition-colors duration-300">458</h3>
            <p className="text-[10px] font-bold text-[#666] dark:text-[#94a3b8] tracking-widest uppercase transition-colors duration-300">{t('Courses_Matched', 'Courses Matched')}</p>
          </div>
          <div className="flex flex-col items-center justify-center text-center">
            <Activity className="w-6 h-6 text-[#1f2d4d] dark:text-[#60a5fa] mb-1.5 stroke-[1.5] transition-colors duration-300" />
            <h3 className="text-[28px] font-[800] text-[#111] dark:text-white leading-none mb-1 transition-colors duration-300">89k</h3>
            <p className="text-[10px] font-bold text-[#666] dark:text-[#94a3b8] tracking-widest uppercase transition-colors duration-300">{t('Skill_Gaps_Resolved', 'Skill Gaps Resolved')}</p>
          </div>
          <div className="flex flex-col items-center justify-center text-center">
            <Award className="w-6 h-6 text-[#1f2d4d] dark:text-[#60a5fa] mb-1.5 stroke-[1.5] transition-colors duration-300" />
            <h3 className="text-[28px] font-[800] text-[#111] dark:text-white leading-none mb-1 transition-colors duration-300">1,240</h3>
            <p className="text-[10px] font-bold text-[#666] dark:text-[#94a3b8] tracking-widest uppercase transition-colors duration-300">{t('Certifications', 'Certifications')}</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="fixed bottom-0 left-0 right-0 z-50 w-full bg-[#1f2d4d] dark:bg-[#0f172a] py-[12px] px-6 md:px-12 flex flex-col md:flex-row items-center justify-between text-white/90 text-[11.5px] font-medium tracking-wide transition-colors duration-300 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)]">
        <div>
          {t('Footer_1', 'Ministry of Statistics and Programme Implementation (MoSPI) | Government of India')}
        </div>
        <div className="flex items-center gap-7 mt-4 md:mt-0">
          <a href="#" className="hover:text-white transition-colors">{t('Privacy', 'Privacy Policy')}</a>
          <a href="#" className="hover:text-white transition-colors">{t('Terms', 'Terms')}</a>
          <a href="#" className="hover:text-white transition-colors">{t('Help', 'Help & FAQ')}</a>
          <div className="flex items-center gap-2 border-l border-white/30 pl-5 ml-1">
            <div className="font-black text-[22px] text-white tracking-widest leading-none">NIC</div>
            <div className="flex flex-col leading-[0.85] text-[6px] text-white/80 uppercase">
              <span>National</span>
              <span>Informatics</span>
              <span>Centre</span>
            </div>
          </div>
        </div>
      </footer>
      </div>

      {/* Features Section */}
      <section id="features" className="relative z-20 w-full bg-[#F2F0EF]/85 dark:bg-[#0f172a]/90 backdrop-blur-md py-16 md:py-24 transition-colors duration-300">
        <div className="max-w-[1400px] mx-auto px-6 md:px-[60px]">
          <h2 className="text-[28px] md:text-[36px] font-[800] text-center text-[#1a1a1a] dark:text-white mb-12 md:mb-16 tracking-tight transition-colors duration-300 uppercase drop-shadow-sm">
            {t('Key_Features', 'Key Features of MoSPI Skill Enhancement')}
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            
            {/* Feature 1 */}
            <div className="bg-white/95 dark:bg-[#1e293b]/90 backdrop-blur-sm rounded-xl p-8 shadow-md border border-[#e2e8f0]/80 dark:border-[#334155]/80 transition-colors duration-300">
              <div className="flex flex-col items-center text-center mb-6">
                <div className="w-16 h-16 bg-[#e0e7ff] dark:bg-[#312e81] text-[#3730a3] dark:text-[#a5b4fc] rounded-full flex items-center justify-center mb-4 transition-colors duration-300 shadow-sm">
                  <BrainCircuit size={32} strokeWidth={1.5} />
                </div>
                <h3 className="text-[17px] font-bold text-[#111] dark:text-white uppercase leading-tight transition-colors duration-300">{t('AI_Driven', <>AI-Driven Skill<br/>Gap Analysis</>)}</h3>
              </div>
              <ul className="text-[13.5px] text-[#444] dark:text-[#cbd5e1] space-y-3 leading-[1.5] transition-colors duration-300 list-disc pl-4 text-left">
                <li>{t('AI_Driven_1', 'Calculates precise mathematical gaps between an official\'s current knowledge and the target proficiency required for their National Classification of Occupations (NCO-2015) designation.')}</li>
                <li>{t('AI_Driven_2', 'Cross-references user profiles against the 338 official Framework of Roles, Activities, and Competencies (FRAC) standards.')}</li>
              </ul>
            </div>

            {/* Feature 2 */}
            <div className="bg-white/95 dark:bg-[#1e293b]/90 backdrop-blur-sm rounded-xl p-8 shadow-md border border-[#e2e8f0]/80 dark:border-[#334155]/80 transition-colors duration-300">
              <div className="flex flex-col items-center text-center mb-6">
                <div className="w-16 h-16 bg-[#e0e7ff] dark:bg-[#312e81] text-[#3730a3] dark:text-[#a5b4fc] rounded-full flex items-center justify-center mb-4 transition-colors duration-300 shadow-sm">
                  <BookOpenCheck size={32} strokeWidth={1.5} />
                </div>
                <h3 className="text-[17px] font-bold text-[#111] dark:text-white uppercase leading-tight transition-colors duration-300">{t('Intelligent_iGOT', <>Intelligent iGOT<br/>Course Mapping</>)}</h3>
              </div>
              <ul className="text-[13.5px] text-[#444] dark:text-[#cbd5e1] space-y-3 leading-[1.5] transition-colors duration-300 list-disc pl-4 text-left">
                <li>{t('Intelligent_iGOT_1', 'Eliminates manual catalog searching by programmatically recommending the exact iGOT Sunbird courses needed to bridge identified competency gaps.')}</li>
                <li>{t('Intelligent_iGOT_2', 'Filters over 8,000 authentic government training modules based on the official\'s specific career trajectory and missing skills.')}</li>
              </ul>
            </div>

            {/* Feature 3 */}
            <div className="bg-white/95 dark:bg-[#1e293b]/90 backdrop-blur-sm rounded-xl p-8 shadow-md border border-[#e2e8f0]/80 dark:border-[#334155]/80 transition-colors duration-300">
              <div className="flex flex-col items-center text-center mb-6">
                <div className="w-16 h-16 bg-[#e0e7ff] dark:bg-[#312e81] text-[#3730a3] dark:text-[#a5b4fc] rounded-full flex items-center justify-center mb-4 transition-colors duration-300 shadow-sm">
                  <FileQuestion size={32} strokeWidth={1.5} />
                </div>
                <h3 className="text-[17px] font-bold text-[#111] dark:text-white uppercase leading-tight transition-colors duration-300">{t('Auto_RAG', <>Automated RAG<br/>Document-to-Quiz</>)}</h3>
              </div>
              <ul className="text-[13.5px] text-[#444] dark:text-[#cbd5e1] space-y-3 leading-[1.5] transition-colors duration-300 list-disc pl-4 text-left">
                <li>{t('Auto_RAG_1', 'Allows officials to upload standard government documents (PDF, PPTX, DOCX) to instantly generate custom multiple-choice assessments.')}</li>
                <li>{t('Auto_RAG_2', 'Evaluates domain knowledge dynamically without requiring pre-authored tests from administrators.')}</li>
              </ul>
            </div>

            {/* Feature 4 */}
            <div className="bg-white/95 dark:bg-[#1e293b]/90 backdrop-blur-sm rounded-xl p-8 shadow-md border border-[#e2e8f0]/80 dark:border-[#334155]/80 transition-colors duration-300">
              <div className="flex flex-col items-center text-center mb-6">
                <div className="w-16 h-16 bg-[#e0e7ff] dark:bg-[#312e81] text-[#3730a3] dark:text-[#a5b4fc] rounded-full flex items-center justify-center mb-4 transition-colors duration-300 shadow-sm">
                  <RefreshCw size={32} strokeWidth={1.5} />
                </div>
                <h3 className="text-[17px] font-bold text-[#111] dark:text-white uppercase leading-tight transition-colors duration-300">{t('Real_Time', <>Real-Time Karmayogi<br/>Synchronization</>)}</h3>
              </div>
              <ul className="text-[13.5px] text-[#444] dark:text-[#cbd5e1] space-y-3 leading-[1.5] transition-colors duration-300 list-disc pl-4 text-left">
                <li>{t('Real_Time_1', 'Automatically communicates with the iGOT portal backend to log achievements.')}</li>
                <li>{t('Real_Time_2', 'Upgrades an official\'s FRAC competency level on the national registry the moment they score 70% or higher on an assessment.')}</li>
              </ul>
            </div>

            {/* Feature 5 */}
            <div className="bg-white/95 dark:bg-[#1e293b]/90 backdrop-blur-sm rounded-xl p-8 shadow-md border border-[#e2e8f0]/80 dark:border-[#334155]/80 transition-colors duration-300">
              <div className="flex flex-col items-center text-center mb-6">
                <div className="w-16 h-16 bg-[#e0e7ff] dark:bg-[#312e81] text-[#3730a3] dark:text-[#a5b4fc] rounded-full flex items-center justify-center mb-4 transition-colors duration-300 shadow-sm">
                  <Shield size={32} strokeWidth={1.5} />
                </div>
                <h3 className="text-[17px] font-bold text-[#111] dark:text-white uppercase leading-tight transition-colors duration-300">{t('Air_Gapped', <>Air-Gapped NLP<br/>Assistant</>)}</h3>
              </div>
              <ul className="text-[13.5px] text-[#444] dark:text-[#cbd5e1] space-y-3 leading-[1.5] transition-colors duration-300 list-disc pl-4 text-left">
                <li>{t('Air_Gapped_1', 'Provides an interactive, zero-latency chat interface for navigating courses, analyzing gaps, and triggering assessments.')}</li>
                <li>{t('Air_Gapped_2', 'Utilizes a secure, embedded deterministic intent-routing engine (no external API keys) to guarantee 100% data sovereignty for sensitive MoSPI environments.')}</li>
              </ul>
            </div>

            {/* Feature 6 */}
            <div className="bg-white/95 dark:bg-[#1e293b]/90 backdrop-blur-sm rounded-xl p-8 shadow-md border border-[#e2e8f0]/80 dark:border-[#334155]/80 transition-colors duration-300">
              <div className="flex flex-col items-center text-center mb-6">
                <div className="w-16 h-16 bg-[#e0e7ff] dark:bg-[#312e81] text-[#3730a3] dark:text-[#a5b4fc] rounded-full flex items-center justify-center mb-4 transition-colors duration-300 shadow-sm">
                  <LayoutDashboard size={32} strokeWidth={1.5} />
                </div>
                <h3 className="text-[17px] font-bold text-[#111] dark:text-white uppercase leading-tight transition-colors duration-300">{t('Dashboard', <>Ministry-Wide Analytics<br/>Dashboard</>)}</h3>
              </div>
              <ul className="text-[13.5px] text-[#444] dark:text-[#cbd5e1] space-y-3 leading-[1.5] transition-colors duration-300 list-disc pl-4 text-left">
                <li>{t('Dashboard_1', 'Aggregates training telemetry to give administrators a macro-view of capacity building across different MoSPI wings (NSO, CSO).')}</li>
                <li>{t('Dashboard_2', 'Visualizes resolved skill gaps, active certifications, and departmental readiness in real-time.')}</li>
              </ul>
            </div>

          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="relative z-20 w-full bg-[#F2F0EF]/85 dark:bg-[#0f172a]/90 backdrop-blur-md pt-16 pb-28 md:pt-24 md:pb-32 border-t border-[#e2e4e8]/60 dark:border-[#334155]/60 transition-colors duration-300">
        <div className="max-w-[1400px] mx-auto px-6 md:px-[60px]">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">
            
            {/* Left: Mission & Vision */}
            <div className="flex flex-col">
              <div className="inline-flex items-center px-4 py-1.5 rounded-full bg-[#e0e7ff] dark:bg-[#1e293b] text-[#3730a3] dark:text-[#a5b4fc] text-[11px] font-bold mb-6 tracking-widest uppercase shadow-sm transition-colors duration-300 w-max">
                {t('About_Platform', 'About The Platform')}
              </div>
              <h2 className="text-[32px] md:text-[42px] font-[800] text-[#1a1a1a] dark:text-white mb-6 leading-[1.1] tracking-tight transition-colors duration-300 uppercase">
                {t('Transforming', <>Transforming India's <br/> Statistical Workforce</>)}
              </h2>
              <p className="text-[15.5px] text-[#444] dark:text-[#cbd5e1] leading-[1.7] font-medium mb-6 transition-colors duration-300">
                Rooted in the mandate of Mission Karmayogi, the MoSPI {t('SIP', 'Skill Intelligence Platform')} is a next-generation capacity-building ecosystem. It transitions civil servants from a rule-based to a role-based framework by aligning specific operational duties with standardized national competencies.
              </p>
              
              <div className="bg-[#f4f5f7] dark:bg-[#1e293b] p-6 rounded-xl border border-[#e2e8f0] dark:border-[#334155] transition-colors duration-300">
                <h4 className="text-[14px] font-bold text-[#111] dark:text-white uppercase mb-3 transition-colors duration-300">{t('Our_Mission', 'Our Mission')}</h4>
                <p className="text-[14px] text-[#555] dark:text-[#94a3b8] leading-[1.6] transition-colors duration-300">
                  To modernize the Ministry of Statistics and Programme Implementation (MoSPI) by providing an intelligent, data-sovereign infrastructure that autonomously identifies skill gaps, curates personalized learning pathways, and evaluates domain mastery in real-time.
                </p>
              </div>

              <div className="mt-8 px-2">
                <h4 className="text-[14px] font-bold text-[#111] dark:text-white uppercase mb-3 transition-colors duration-300 flex items-center gap-2">
                  <Shield size={16} className="text-[#1f2d4d] dark:text-[#60a5fa]" strokeWidth={2.5} /> {t('Built_For', 'Built for Sovereignty & Security')}
                </h4>
                <p className="text-[14.5px] text-[#555] dark:text-[#94a3b8] leading-[1.6] transition-colors duration-300">
                  Operating within the sensitive environment of the national statistical system requires uncompromising data security. Our completely air-gapped, deterministic intent-routing NLP engine ensures all interactions, evaluations, and telemetry remain strictly within the government intranet without reliance on external commercial API keys.
                </p>
              </div>
            </div>

            {/* Right: Architecture Pillars */}
            <div className="flex flex-col gap-5 lg:mt-[72px]">
              <h3 className="text-[18px] font-bold text-[#111] dark:text-white uppercase mb-2 transition-colors duration-300 px-1">
                {t('Arch', 'Architecture of Continuous Learning')}
              </h3>
              
              <div className="flex gap-5 items-start bg-white dark:bg-[#1e293b]/50 p-6 rounded-xl border border-[#e2e8f0] dark:border-[#334155] shadow-sm transition-colors duration-300">
                <div className="w-12 h-12 shrink-0 bg-[#f8fafc] dark:bg-[#0f172a] text-[#1f2d4d] dark:text-[#60a5fa] rounded-full flex items-center justify-center font-black text-[18px] border border-[#e2e8f0] dark:border-[#334155] transition-colors duration-300 shadow-inner">1</div>
                <div>
                  <h4 className="text-[15px] font-bold text-[#111] dark:text-white uppercase mb-2 transition-colors duration-300">{t('FRAC', 'FRAC-Aligned Framework')}</h4>
                  <p className="text-[13.5px] text-[#555] dark:text-[#cbd5e1] leading-[1.6] transition-colors duration-300">
                    We map authentic National Classification of Occupations (NCO-2015) job profiles directly to the 338 standardized competencies defined by FRAC. This ensures every learning recommendation is mathematically targeted to an official's actual career trajectory.
                  </p>
                </div>
              </div>

              <div className="flex gap-5 items-start bg-white dark:bg-[#1e293b]/50 p-6 rounded-xl border border-[#e2e8f0] dark:border-[#334155] shadow-sm transition-colors duration-300">
                <div className="w-12 h-12 shrink-0 bg-[#f8fafc] dark:bg-[#0f172a] text-[#1f2d4d] dark:text-[#60a5fa] rounded-full flex items-center justify-center font-black text-[18px] border border-[#e2e8f0] dark:border-[#334155] transition-colors duration-300 shadow-inner">2</div>
                <div>
                  <h4 className="text-[15px] font-bold text-[#111] dark:text-white uppercase mb-2 transition-colors duration-300">{t('iGOT', 'Intelligent iGOT Integration')}</h4>
                  <p className="text-[13.5px] text-[#555] dark:text-[#cbd5e1] leading-[1.6] transition-colors duration-300">
                    By deeply integrating with the national iGOT Sunbird registry, we sift through over 8,000 official training modules to recommend precise courses needed to bridge identified gaps, while automatically syncing new achievements back to the central government database.
                  </p>
                </div>
              </div>

              <div className="flex gap-5 items-start bg-white dark:bg-[#1e293b]/50 p-6 rounded-xl border border-[#e2e8f0] dark:border-[#334155] shadow-sm transition-colors duration-300">
                <div className="w-12 h-12 shrink-0 bg-[#f8fafc] dark:bg-[#0f172a] text-[#1f2d4d] dark:text-[#60a5fa] rounded-full flex items-center justify-center font-black text-[18px] border border-[#e2e8f0] dark:border-[#334155] transition-colors duration-300 shadow-inner">3</div>
                <div>
                  <h4 className="text-[15px] font-bold text-[#111] dark:text-white uppercase mb-2 transition-colors duration-300">{t('Dynamic_AI', 'Dynamic AI Evaluation')}</h4>
                  <p className="text-[13.5px] text-[#555] dark:text-[#cbd5e1] leading-[1.6] transition-colors duration-300">
                    Through our proprietary Retrieval-Augmented Generation (RAG) pipeline, the platform allows departments to instantly generate custom assessments from internal policy documents, presentations, and manuals, ensuring officials are tested on the most relevant departmental knowledge.
                  </p>
                </div>
              </div>

            </div>
          </div>
        </div>
      </section>

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
      />
    </div>
  );
};

export default LandingPage;
