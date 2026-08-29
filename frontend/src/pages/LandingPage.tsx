import React from 'react';
import { Link } from 'react-router-dom';
import { Search, Settings, User, BookOpen, Activity, Award, Cpu, TabletSmartphone, Route, Moon, Sun, BrainCircuit, BookOpenCheck, FileQuestion, RefreshCw, Shield, LayoutDashboard } from 'lucide-react';
import { useTheme } from '../hooks/useTheme';

const LandingPage: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

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
      <div className="min-h-screen flex flex-col">
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
              Ministry of Statistics & <br /> Programme Implementation (MoSPI)
            </div>
            <div className="text-[9px] text-[#6b7280] dark:text-[#94a3b8] font-bold tracking-[0.15em] uppercase mt-0.5">
              Skill Intelligence Platform
            </div>
          </div>
        </div>

        {/* Center Nav & Right Actions */}
        <div className="flex items-center gap-9">
          <nav className="hidden lg:flex items-center gap-6 text-[11px] font-bold text-[#555] dark:text-[#cbd5e1] tracking-wide uppercase">
            <a href="#" onClick={(e) => scrollToSection(e, 'home')} className="hover:text-[#1f2d4d] dark:hover:text-white transition-colors">Home</a>
            <a href="#about" onClick={(e) => scrollToSection(e, 'about')} className="hover:text-[#1f2d4d] dark:hover:text-white transition-colors">About</a>
            <a href="#features" onClick={(e) => scrollToSection(e, 'features')} className="hover:text-[#1f2d4d] dark:hover:text-white transition-colors">Features</a>
            <a href="#contact" className="hover:text-[#1f2d4d] dark:hover:text-white transition-colors">Contact</a>
          </nav>
          
          <div className="hidden lg:flex items-center gap-4 text-[#555] dark:text-[#cbd5e1]">
            <button aria-label="Search"><Search size={16} strokeWidth={2.5} /></button>
            <span className="text-[12px] font-bold px-1.5 border-r border-[#d1d5db] dark:border-[#475569]">Eng | हिंदी</span>
            <button aria-label="Toggle Theme" onClick={toggleTheme} className="hover:text-[#1f2d4d] dark:hover:text-white transition-colors">
              {theme === 'dark' ? <Sun size={16} strokeWidth={2.5} /> : <Moon size={16} strokeWidth={2.5} />}
            </button>
            <button aria-label="Settings"><Settings size={16} strokeWidth={2.5} /></button>
          </div>

          <div className="flex items-center gap-3 ml-2">
            <Link to="/login" className="px-5 py-[9px] bg-[#1f2d4d] dark:bg-[#3b82f6] text-white text-[11px] font-bold rounded-[6px] hover:bg-[#2c3d63] dark:hover:bg-[#2563eb] transition-colors tracking-wide leading-none shadow-sm">
              OFFICIAL LOGIN
            </Link>
            <Link to="/login" className="px-5 py-[8px] bg-white dark:bg-transparent border-[1.5px] border-[#1f2d4d] dark:border-white text-[#1f2d4d] dark:text-white text-[11px] font-bold rounded-[6px] hover:bg-[#f8fafc] dark:hover:bg-white/10 transition-colors tracking-wide leading-none">
              ADMIN PORTAL
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="relative z-10 flex-1 w-full max-w-[1400px] mx-auto px-6 md:px-[60px] grid grid-cols-1 lg:grid-cols-[1.1fr_0.9fr] items-center gap-6 py-6 md:py-[30px]">
        
        {/* Left Column */}
        <div className="flex flex-col items-start z-10">
          <div className="inline-flex items-center px-[14px] py-[6px] rounded-full bg-[#eef0f3] dark:bg-[#1e293b] text-[#555] dark:text-[#cbd5e1] text-[11px] font-bold mb-4 tracking-wide shadow-sm transition-colors duration-300">
            <span className="text-[#666] dark:text-[#94a3b8] mr-1.5 text-[14px] font-black leading-none">#</span> Powered by MoSPI AI Engine
          </div>
          
          <h1 className="text-[44px] md:text-[56px] leading-[1.08] font-[800] tracking-tight text-[#1a1a1a] dark:text-white mb-4 w-[110%] uppercase transition-colors duration-300">
            EMPOWERING INDIA'S <br/>
            OFFICIAL STATISTICAL <br/>
            SYSTEM
          </h1>
          
          <p className="text-[15.5px] text-[#444] dark:text-[#cbd5e1] max-w-[520px] leading-[1.6] font-medium mb-6 transition-colors duration-300">
            A next-generation competency tracking platform. We combine AI-driven skill-gap analysis with personalized iGOT learning pathways.
          </p>
          
          <div className="flex gap-[16px] mb-8">
            <Link to="/login" className="px-[30px] py-[13px] bg-[#1f2d4d] dark:bg-[#3b82f6] text-white text-[13px] font-bold rounded-[6px] hover:bg-[#2c3d63] dark:hover:bg-[#2563eb] transition-colors tracking-wide leading-none shadow-md">
              LOGIN AS OFFICIAL
            </Link>
            <Link to="/login" className="px-[30px] py-[11.5px] bg-white dark:bg-transparent border-[1.5px] border-[#1f2d4d] dark:border-white text-[#1f2d4d] dark:text-white text-[13px] font-bold rounded-[6px] hover:bg-[#f8fafc] dark:hover:bg-white/10 transition-colors tracking-wide leading-none shadow-sm">
              ADMIN PORTAL
            </Link>
          </div>

          {/* Capabilities */}
          <div className="w-full">
            <h4 className="text-[12px] font-bold text-[#222] dark:text-[#e2e8f0] tracking-[0.03em] mb-4 uppercase transition-colors duration-300">Platform Capabilities</h4>
            <div className="flex items-start gap-9">
              
              <div className="flex gap-2.5">
                <div className="font-medium text-[15px] text-[#555] dark:text-[#94a3b8] pt-[1px] transition-colors duration-300">1.</div>
                <div className="relative w-8 h-8 flex items-center justify-center text-[#1f2d4d] dark:text-[#60a5fa] transition-colors duration-300">
                  <Cpu className="w-8 h-8 absolute inset-0 stroke-[1.2]" />
                  <span className="text-[9px] font-bold mt-[2px]">AI</span>
                </div>
                <div className="flex flex-col justify-start mt-[2px]">
                  <h5 className="font-bold text-[13.5px] text-[#111] dark:text-white mb-0.5 leading-none transition-colors duration-300">Skill Analysis</h5>
                  <p className="text-[11.5px] text-[#666] dark:text-[#94a3b8] leading-[1.3] transition-colors duration-300">Compute answer of<br/>soillfstent analysis.</p>
                </div>
              </div>
              
              <div className="flex gap-2.5">
                <div className="font-medium text-[15px] text-[#555] dark:text-[#94a3b8] pt-[1px] transition-colors duration-300">2.</div>
                <div className="relative w-8 h-8 flex items-center justify-center text-[#1f2d4d] dark:text-[#60a5fa] transition-colors duration-300">
                  <BookOpen className="w-8 h-8 absolute inset-0 stroke-[1.2]" />
                  <TabletSmartphone className="w-4 h-4 absolute bottom-[-2px] right-[-4px] bg-[#fafaf9] dark:bg-[#0f172a] rounded-[2px] stroke-[1.5] transition-colors duration-300" />
                </div>
                <div className="flex flex-col justify-start mt-[2px]">
                  <h5 className="font-bold text-[13.5px] text-[#111] dark:text-white mb-0.5 leading-none transition-colors duration-300">iGOT Learning</h5>
                  <p className="text-[11.5px] text-[#666] dark:text-[#94a3b8] leading-[1.3] transition-colors duration-300">Linked control-linked<br/>course books.</p>
                </div>
              </div>
              
              <div className="flex gap-2.5">
                <div className="font-medium text-[15px] text-[#555] dark:text-[#94a3b8] pt-[1px] transition-colors duration-300">3.</div>
                <Route className="w-8 h-8 text-[#1f2d4d] dark:text-[#60a5fa] stroke-[1.2] transition-colors duration-300" />
                <div className="flex flex-col justify-start mt-[2px]">
                  <h5 className="font-bold text-[13.5px] text-[#111] dark:text-white mb-0.5 leading-none transition-colors duration-300">Career Pathways</h5>
                  <p className="text-[11.5px] text-[#666] dark:text-[#94a3b8] leading-[1.3] transition-colors duration-300">Integratat roadmap and<br/>careeer pathways.</p>
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
            <p className="text-[10px] font-bold text-[#666] dark:text-[#94a3b8] tracking-widest uppercase transition-colors duration-300">Active Users</p>
          </div>
          <div className="flex flex-col items-center justify-center text-center">
            <BookOpen className="w-6 h-6 text-[#1f2d4d] dark:text-[#60a5fa] mb-1.5 stroke-[1.5] transition-colors duration-300" />
            <h3 className="text-[28px] font-[800] text-[#111] dark:text-white leading-none mb-1 transition-colors duration-300">458</h3>
            <p className="text-[10px] font-bold text-[#666] dark:text-[#94a3b8] tracking-widest uppercase transition-colors duration-300">Courses Matched</p>
          </div>
          <div className="flex flex-col items-center justify-center text-center">
            <Activity className="w-6 h-6 text-[#1f2d4d] dark:text-[#60a5fa] mb-1.5 stroke-[1.5] transition-colors duration-300" />
            <h3 className="text-[28px] font-[800] text-[#111] dark:text-white leading-none mb-1 transition-colors duration-300">89k</h3>
            <p className="text-[10px] font-bold text-[#666] dark:text-[#94a3b8] tracking-widest uppercase transition-colors duration-300">Skill Gaps Resolved</p>
          </div>
          <div className="flex flex-col items-center justify-center text-center">
            <Award className="w-6 h-6 text-[#1f2d4d] dark:text-[#60a5fa] mb-1.5 stroke-[1.5] transition-colors duration-300" />
            <h3 className="text-[28px] font-[800] text-[#111] dark:text-white leading-none mb-1 transition-colors duration-300">1,240</h3>
            <p className="text-[10px] font-bold text-[#666] dark:text-[#94a3b8] tracking-widest uppercase transition-colors duration-300">Certifications</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-20 w-full bg-[#1f2d4d] dark:bg-[#0f172a] py-[12px] px-6 md:px-12 flex flex-col md:flex-row items-center justify-between text-white/90 text-[11.5px] font-medium tracking-wide transition-colors duration-300">
        <div>
          Ministry of Statistics and Programme Implementation (MoSPI) | Government of India
        </div>
        <div className="flex items-center gap-7 mt-4 md:mt-0">
          <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
          <a href="#" className="hover:text-white transition-colors">Terms</a>
          <a href="#" className="hover:text-white transition-colors">Help & FAQ</a>
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
            Key Features of MoSPI Skill Enhancement
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            
            {/* Feature 1 */}
            <div className="bg-white/95 dark:bg-[#1e293b]/90 backdrop-blur-sm rounded-xl p-8 shadow-md border border-[#e2e8f0]/80 dark:border-[#334155]/80 transition-colors duration-300">
              <div className="flex flex-col items-center text-center mb-6">
                <div className="w-16 h-16 bg-[#e0e7ff] dark:bg-[#312e81] text-[#3730a3] dark:text-[#a5b4fc] rounded-full flex items-center justify-center mb-4 transition-colors duration-300 shadow-sm">
                  <BrainCircuit size={32} strokeWidth={1.5} />
                </div>
                <h3 className="text-[17px] font-bold text-[#111] dark:text-white uppercase leading-tight transition-colors duration-300">AI-Driven Skill<br/>Gap Analysis</h3>
              </div>
              <ul className="text-[13.5px] text-[#444] dark:text-[#cbd5e1] space-y-3 leading-[1.5] transition-colors duration-300 list-disc pl-4 text-left">
                <li>Calculates precise mathematical gaps between an official's current knowledge and the target proficiency required for their National Classification of Occupations (NCO-2015) designation.</li>
                <li>Cross-references user profiles against the 338 official Framework of Roles, Activities, and Competencies (FRAC) standards.</li>
              </ul>
            </div>

            {/* Feature 2 */}
            <div className="bg-white/95 dark:bg-[#1e293b]/90 backdrop-blur-sm rounded-xl p-8 shadow-md border border-[#e2e8f0]/80 dark:border-[#334155]/80 transition-colors duration-300">
              <div className="flex flex-col items-center text-center mb-6">
                <div className="w-16 h-16 bg-[#e0e7ff] dark:bg-[#312e81] text-[#3730a3] dark:text-[#a5b4fc] rounded-full flex items-center justify-center mb-4 transition-colors duration-300 shadow-sm">
                  <BookOpenCheck size={32} strokeWidth={1.5} />
                </div>
                <h3 className="text-[17px] font-bold text-[#111] dark:text-white uppercase leading-tight transition-colors duration-300">Intelligent iGOT<br/>Course Mapping</h3>
              </div>
              <ul className="text-[13.5px] text-[#444] dark:text-[#cbd5e1] space-y-3 leading-[1.5] transition-colors duration-300 list-disc pl-4 text-left">
                <li>Eliminates manual catalog searching by programmatically recommending the exact iGOT Sunbird courses needed to bridge identified competency gaps.</li>
                <li>Filters over 8,000 authentic government training modules based on the official's specific career trajectory and missing skills.</li>
              </ul>
            </div>

            {/* Feature 3 */}
            <div className="bg-white/95 dark:bg-[#1e293b]/90 backdrop-blur-sm rounded-xl p-8 shadow-md border border-[#e2e8f0]/80 dark:border-[#334155]/80 transition-colors duration-300">
              <div className="flex flex-col items-center text-center mb-6">
                <div className="w-16 h-16 bg-[#e0e7ff] dark:bg-[#312e81] text-[#3730a3] dark:text-[#a5b4fc] rounded-full flex items-center justify-center mb-4 transition-colors duration-300 shadow-sm">
                  <FileQuestion size={32} strokeWidth={1.5} />
                </div>
                <h3 className="text-[17px] font-bold text-[#111] dark:text-white uppercase leading-tight transition-colors duration-300">Automated RAG<br/>Document-to-Quiz</h3>
              </div>
              <ul className="text-[13.5px] text-[#444] dark:text-[#cbd5e1] space-y-3 leading-[1.5] transition-colors duration-300 list-disc pl-4 text-left">
                <li>Allows officials to upload standard government documents (PDF, PPTX, DOCX) to instantly generate custom multiple-choice assessments.</li>
                <li>Evaluates domain knowledge dynamically without requiring pre-authored tests from administrators.</li>
              </ul>
            </div>

            {/* Feature 4 */}
            <div className="bg-white/95 dark:bg-[#1e293b]/90 backdrop-blur-sm rounded-xl p-8 shadow-md border border-[#e2e8f0]/80 dark:border-[#334155]/80 transition-colors duration-300">
              <div className="flex flex-col items-center text-center mb-6">
                <div className="w-16 h-16 bg-[#e0e7ff] dark:bg-[#312e81] text-[#3730a3] dark:text-[#a5b4fc] rounded-full flex items-center justify-center mb-4 transition-colors duration-300 shadow-sm">
                  <RefreshCw size={32} strokeWidth={1.5} />
                </div>
                <h3 className="text-[17px] font-bold text-[#111] dark:text-white uppercase leading-tight transition-colors duration-300">Real-Time Karmayogi<br/>Synchronization</h3>
              </div>
              <ul className="text-[13.5px] text-[#444] dark:text-[#cbd5e1] space-y-3 leading-[1.5] transition-colors duration-300 list-disc pl-4 text-left">
                <li>Automatically communicates with the iGOT portal backend to log achievements.</li>
                <li>Upgrades an official's FRAC competency level on the national registry the moment they score 70% or higher on an assessment.</li>
              </ul>
            </div>

            {/* Feature 5 */}
            <div className="bg-white/95 dark:bg-[#1e293b]/90 backdrop-blur-sm rounded-xl p-8 shadow-md border border-[#e2e8f0]/80 dark:border-[#334155]/80 transition-colors duration-300">
              <div className="flex flex-col items-center text-center mb-6">
                <div className="w-16 h-16 bg-[#e0e7ff] dark:bg-[#312e81] text-[#3730a3] dark:text-[#a5b4fc] rounded-full flex items-center justify-center mb-4 transition-colors duration-300 shadow-sm">
                  <Shield size={32} strokeWidth={1.5} />
                </div>
                <h3 className="text-[17px] font-bold text-[#111] dark:text-white uppercase leading-tight transition-colors duration-300">Air-Gapped NLP<br/>Assistant</h3>
              </div>
              <ul className="text-[13.5px] text-[#444] dark:text-[#cbd5e1] space-y-3 leading-[1.5] transition-colors duration-300 list-disc pl-4 text-left">
                <li>Provides an interactive, zero-latency chat interface for navigating courses, analyzing gaps, and triggering assessments.</li>
                <li>Utilizes a secure, embedded deterministic intent-routing engine (no external API keys) to guarantee 100% data sovereignty for sensitive MoSPI environments.</li>
              </ul>
            </div>

            {/* Feature 6 */}
            <div className="bg-white/95 dark:bg-[#1e293b]/90 backdrop-blur-sm rounded-xl p-8 shadow-md border border-[#e2e8f0]/80 dark:border-[#334155]/80 transition-colors duration-300">
              <div className="flex flex-col items-center text-center mb-6">
                <div className="w-16 h-16 bg-[#e0e7ff] dark:bg-[#312e81] text-[#3730a3] dark:text-[#a5b4fc] rounded-full flex items-center justify-center mb-4 transition-colors duration-300 shadow-sm">
                  <LayoutDashboard size={32} strokeWidth={1.5} />
                </div>
                <h3 className="text-[17px] font-bold text-[#111] dark:text-white uppercase leading-tight transition-colors duration-300">Ministry-Wide Analytics<br/>Dashboard</h3>
              </div>
              <ul className="text-[13.5px] text-[#444] dark:text-[#cbd5e1] space-y-3 leading-[1.5] transition-colors duration-300 list-disc pl-4 text-left">
                <li>Aggregates training telemetry to give administrators a macro-view of capacity building across different MoSPI wings (NSO, CSO).</li>
                <li>Visualizes resolved skill gaps, active certifications, and departmental readiness in real-time.</li>
              </ul>
            </div>

          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="relative z-20 w-full bg-[#F2F0EF]/85 dark:bg-[#0f172a]/90 backdrop-blur-md py-16 md:py-24 border-t border-[#e2e4e8]/60 dark:border-[#334155]/60 transition-colors duration-300">
        <div className="max-w-[1400px] mx-auto px-6 md:px-[60px]">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">
            
            {/* Left: Mission & Vision */}
            <div className="flex flex-col">
              <div className="inline-flex items-center px-4 py-1.5 rounded-full bg-[#e0e7ff] dark:bg-[#1e293b] text-[#3730a3] dark:text-[#a5b4fc] text-[11px] font-bold mb-6 tracking-widest uppercase shadow-sm transition-colors duration-300 w-max">
                About The Platform
              </div>
              <h2 className="text-[32px] md:text-[42px] font-[800] text-[#1a1a1a] dark:text-white mb-6 leading-[1.1] tracking-tight transition-colors duration-300 uppercase">
                Transforming India's <br/> Statistical Workforce
              </h2>
              <p className="text-[15.5px] text-[#444] dark:text-[#cbd5e1] leading-[1.7] font-medium mb-6 transition-colors duration-300">
                Rooted in the mandate of Mission Karmayogi, the MoSPI Skill Intelligence Platform is a next-generation capacity-building ecosystem. It transitions civil servants from a rule-based to a role-based framework by aligning specific operational duties with standardized national competencies.
              </p>
              
              <div className="bg-[#f4f5f7] dark:bg-[#1e293b] p-6 rounded-xl border border-[#e2e8f0] dark:border-[#334155] transition-colors duration-300">
                <h4 className="text-[14px] font-bold text-[#111] dark:text-white uppercase mb-3 transition-colors duration-300">Our Mission</h4>
                <p className="text-[14px] text-[#555] dark:text-[#94a3b8] leading-[1.6] transition-colors duration-300">
                  To modernize the Ministry of Statistics and Programme Implementation (MoSPI) by providing an intelligent, data-sovereign infrastructure that autonomously identifies skill gaps, curates personalized learning pathways, and evaluates domain mastery in real-time.
                </p>
              </div>

              <div className="mt-8 px-2">
                <h4 className="text-[14px] font-bold text-[#111] dark:text-white uppercase mb-3 transition-colors duration-300 flex items-center gap-2">
                  <Shield size={16} className="text-[#1f2d4d] dark:text-[#60a5fa]" strokeWidth={2.5} /> Built for Sovereignty & Security
                </h4>
                <p className="text-[14.5px] text-[#555] dark:text-[#94a3b8] leading-[1.6] transition-colors duration-300">
                  Operating within the sensitive environment of the national statistical system requires uncompromising data security. Our completely air-gapped, deterministic intent-routing NLP engine ensures all interactions, evaluations, and telemetry remain strictly within the government intranet without reliance on external commercial API keys.
                </p>
              </div>
            </div>

            {/* Right: Architecture Pillars */}
            <div className="flex flex-col gap-5 lg:mt-[72px]">
              <h3 className="text-[18px] font-bold text-[#111] dark:text-white uppercase mb-2 transition-colors duration-300 px-1">
                Architecture of Continuous Learning
              </h3>
              
              <div className="flex gap-5 items-start bg-white dark:bg-[#1e293b]/50 p-6 rounded-xl border border-[#e2e8f0] dark:border-[#334155] shadow-sm transition-colors duration-300">
                <div className="w-12 h-12 shrink-0 bg-[#f8fafc] dark:bg-[#0f172a] text-[#1f2d4d] dark:text-[#60a5fa] rounded-full flex items-center justify-center font-black text-[18px] border border-[#e2e8f0] dark:border-[#334155] transition-colors duration-300 shadow-inner">1</div>
                <div>
                  <h4 className="text-[15px] font-bold text-[#111] dark:text-white uppercase mb-2 transition-colors duration-300">FRAC-Aligned Framework</h4>
                  <p className="text-[13.5px] text-[#555] dark:text-[#cbd5e1] leading-[1.6] transition-colors duration-300">
                    We map authentic National Classification of Occupations (NCO-2015) job profiles directly to the 338 standardized competencies defined by FRAC. This ensures every learning recommendation is mathematically targeted to an official's actual career trajectory.
                  </p>
                </div>
              </div>

              <div className="flex gap-5 items-start bg-white dark:bg-[#1e293b]/50 p-6 rounded-xl border border-[#e2e8f0] dark:border-[#334155] shadow-sm transition-colors duration-300">
                <div className="w-12 h-12 shrink-0 bg-[#f8fafc] dark:bg-[#0f172a] text-[#1f2d4d] dark:text-[#60a5fa] rounded-full flex items-center justify-center font-black text-[18px] border border-[#e2e8f0] dark:border-[#334155] transition-colors duration-300 shadow-inner">2</div>
                <div>
                  <h4 className="text-[15px] font-bold text-[#111] dark:text-white uppercase mb-2 transition-colors duration-300">Intelligent iGOT Integration</h4>
                  <p className="text-[13.5px] text-[#555] dark:text-[#cbd5e1] leading-[1.6] transition-colors duration-300">
                    By deeply integrating with the national iGOT Sunbird registry, we sift through over 8,000 official training modules to recommend precise courses needed to bridge identified gaps, while automatically syncing new achievements back to the central government database.
                  </p>
                </div>
              </div>

              <div className="flex gap-5 items-start bg-white dark:bg-[#1e293b]/50 p-6 rounded-xl border border-[#e2e8f0] dark:border-[#334155] shadow-sm transition-colors duration-300">
                <div className="w-12 h-12 shrink-0 bg-[#f8fafc] dark:bg-[#0f172a] text-[#1f2d4d] dark:text-[#60a5fa] rounded-full flex items-center justify-center font-black text-[18px] border border-[#e2e8f0] dark:border-[#334155] transition-colors duration-300 shadow-inner">3</div>
                <div>
                  <h4 className="text-[15px] font-bold text-[#111] dark:text-white uppercase mb-2 transition-colors duration-300">Dynamic AI Evaluation</h4>
                  <p className="text-[13.5px] text-[#555] dark:text-[#cbd5e1] leading-[1.6] transition-colors duration-300">
                    Through our proprietary Retrieval-Augmented Generation (RAG) pipeline, the platform allows departments to instantly generate custom assessments from internal policy documents, presentations, and manuals, ensuring officials are tested on the most relevant departmental knowledge.
                  </p>
                </div>
              </div>

            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
