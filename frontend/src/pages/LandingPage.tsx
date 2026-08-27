import React from 'react';
import { Link } from 'react-router-dom';
import { Users, BookOpen, Activity, Award, Hash, ArrowRight, Sun, Moon, Radar, Database, LineChart, Quote } from 'lucide-react';
import { useTheme } from '../hooks/useTheme';

const LandingPage: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  const handleScroll = (e: React.MouseEvent<HTMLAnchorElement, MouseEvent>, id: string) => {
    e.preventDefault();
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="font-sans relative bg-[#f8fafc] dark:bg-slate-900 transition-colors duration-300 overflow-x-hidden text-slate-600 dark:text-slate-400">
      
      {/* Background Image Layer - Fixed to flow seamlessly */}
      <div 
        className="fixed inset-0 z-0 pointer-events-none opacity-[0.25] dark:opacity-10 dark:invert"
        style={{
          backgroundImage: `url('/bg-new-topo.png')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          transform: 'scale(1.2) translateX(-5%)'
        }}
      />

      {/* Hero Container (Full Screen) */}
      <div className="min-h-screen flex flex-col relative z-10">
        <div className="max-w-[1440px] w-full mx-auto px-6 md:px-12 flex flex-col flex-1 relative">
          
          {/* Navbar */}
          <header className="py-8 flex items-center justify-between">
            {/* Logo Block */}
            <div className="flex flex-col cursor-default">
              <div className="flex items-center gap-1.5">
                <div className="flex flex-col gap-[3px] justify-center mt-0.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#0f172a] dark:bg-white transition-colors duration-300"></div>
                  <div className="w-1.5 h-1.5 rounded-full bg-[#16A34A]"></div>
                </div>
                <span className="font-bold text-[22px] text-[#0f172a] dark:text-white tracking-tight leading-none transition-colors duration-300">MoSPI</span>
              </div>
              <span className="text-[8px] text-slate-400 font-semibold tracking-wide uppercase mt-1 pl-3">
                Skill Intelligence Platform
              </span>
            </div>
            
            {/* Nav & Action */}
            <div className="flex items-center gap-8">
              <nav className="hidden md:flex items-center gap-6">
                <a href="#" onClick={(e) => handleScroll(e, 'hero')} className="text-[11px] font-bold text-slate-700 dark:text-slate-300 hover:text-black dark:hover:text-white tracking-wide transition-colors">HOME</a>
                <a href="#about" onClick={(e) => handleScroll(e, 'about')} className="text-[11px] font-bold text-slate-700 dark:text-slate-300 hover:text-black dark:hover:text-white tracking-wide transition-colors">ABOUT</a>
                <a href="#features" onClick={(e) => handleScroll(e, 'features')} className="text-[11px] font-bold text-slate-700 dark:text-slate-300 hover:text-black dark:hover:text-white tracking-wide transition-colors">FEATURES</a>
              </nav>

              <div className="flex items-center gap-4">
                <button 
                  onClick={toggleTheme}
                  className="p-2 rounded-full text-slate-500 hover:bg-slate-200 dark:text-slate-400 dark:hover:bg-slate-800 transition-colors"
                  aria-label="Toggle Theme"
                >
                  {theme === 'light' ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
                </button>

                <Link 
                  to="/login" 
                  className="flex items-center gap-1.5 px-4 py-2 bg-[#e0f2fe] dark:bg-blue-900/40 hover:bg-[#bae6fd] dark:hover:bg-blue-800/60 text-[#0369a1] dark:text-blue-300 text-[11px] font-bold rounded-md shadow-sm transition-all"
                >
                  Sign In <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          </header>

          {/* Hero Section */}
          <main id="hero" className="flex-1 w-full grid grid-cols-1 lg:grid-cols-12 items-center gap-8 lg:gap-4 pt-6 pb-12">
            
            {/* Left Content */}
            <div className="lg:col-span-5 flex flex-col items-start text-left z-10">
              
              <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800/80 border border-slate-200/60 dark:border-slate-700 text-slate-600 dark:text-slate-300 text-[11px] font-medium mb-6 shadow-sm transition-colors duration-300">
                <Hash className="w-3 h-3 text-[#f59e0b]" />
                Powered by MoSPI AI Engine
              </div>
              
              <h1 className="text-5xl md:text-6xl lg:text-7xl leading-[1.05] font-extrabold tracking-tighter text-[#0f172a] dark:text-white mb-6 uppercase transition-colors duration-300">
                Empowering India's <br/>
                Official Statistical <br/>
                System
              </h1>
              
              <p className="text-[13px] md:text-[14px] text-slate-600 dark:text-slate-400 max-w-md leading-[1.6] font-medium transition-colors duration-300">
                A next-generation competency tracking platform. We combine AI-driven skill-gap analysis with personalized iGOT learning pathways.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 mt-12">
                <Link
                  to="/login"
                  className="px-7 py-2.5 bg-gradient-to-b from-[#2b4c7e] to-[#0d1b2a] dark:from-blue-600 dark:to-blue-900 border border-[#0d1b2a] dark:border-blue-900 text-white text-[13px] font-bold rounded-[6px] shadow-[0_10px_20px_-8px_rgba(13,27,42,0.8),inset_0_1px_1px_rgba(255,255,255,0.3)] hover:from-[#3a5d91] hover:to-[#162a42] transition-all text-center"
                  style={{ textShadow: '0 1px 2px rgba(0,0,0,0.6)' }}
                >
                  Login as Official
                </Link>
                <Link
                  to="/login"
                  className="px-7 py-2.5 bg-gradient-to-b from-white to-[#f1f5f9] dark:from-slate-800 dark:to-slate-900 border border-[#e2e8f0] dark:border-slate-700 text-slate-700 dark:text-slate-200 text-[13px] font-bold rounded-[6px] shadow-[0_8px_16px_-6px_rgba(148,163,184,0.4),inset_0_1px_0_rgba(255,255,255,1)] dark:shadow-none hover:to-[#e2e8f0] dark:hover:to-slate-800 transition-all text-center"
                >
                  Admin Portal
                </Link>
              </div>
            </div>

            {/* Right Content - Map Image */}
            <div className="lg:col-span-7 relative flex justify-center lg:justify-end items-center pointer-events-none mt-8 lg:mt-0">
              <img 
                src="/india-map.png" 
                alt="India Skill Network Map" 
                className="w-full max-w-[550px] object-contain mix-blend-darken dark:mix-blend-screen dark:invert transition-all duration-300"
                style={{ filter: 'drop-shadow(0 25px 25px rgba(0, 0, 0, 0.15)) brightness(1.05)' }} 
              />
            </div>
          </main>
        </div>

        {/* Metrics Section */}
        <section className="relative z-20 w-full mt-auto bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-t border-slate-200 dark:border-slate-800 transition-colors duration-300">
          <div className="w-full max-w-[1440px] mx-auto grid grid-cols-2 md:grid-cols-4">
            {/* Metric 1 */}
            <div className="flex flex-col items-center justify-center py-6">
              <Users className="w-5 h-5 text-[#0f172a] dark:text-blue-400 stroke-[1.5] mb-1.5" />
              <h3 className="text-[22px] font-extrabold text-[#0f172a] dark:text-white tracking-tight leading-none">12.4k</h3>
              <p className="text-[9px] font-bold text-slate-400 dark:text-slate-500 tracking-widest uppercase mt-1">Active Users</p>
            </div>
            {/* Metric 2 */}
            <div className="flex flex-col items-center justify-center py-6 border-l border-slate-200 dark:border-slate-800">
              <BookOpen className="w-5 h-5 text-[#0f172a] dark:text-blue-400 stroke-[1.5] mb-1.5" />
              <h3 className="text-[22px] font-extrabold text-[#0f172a] dark:text-white tracking-tight leading-none">458</h3>
              <p className="text-[9px] font-bold text-slate-400 dark:text-slate-500 tracking-widest uppercase mt-1">Courses Matched</p>
            </div>
            {/* Metric 3 */}
            <div className="flex flex-col items-center justify-center py-6 border-t md:border-t-0 md:border-l border-slate-200 dark:border-slate-800">
              <Activity className="w-5 h-5 text-[#0f172a] dark:text-blue-400 stroke-[1.5] mb-1.5" />
              <h3 className="text-[22px] font-extrabold text-[#0f172a] dark:text-white tracking-tight leading-none">89k</h3>
              <p className="text-[9px] font-bold text-slate-400 dark:text-slate-500 tracking-widest uppercase mt-1">Skill Gaps Resolved</p>
            </div>
            {/* Metric 4 */}
            <div className="flex flex-col items-center justify-center py-6 border-t md:border-t-0 border-l border-slate-200 dark:border-slate-800">
              <Award className="w-5 h-5 text-[#0f172a] dark:text-blue-400 stroke-[1.5] mb-1.5" />
              <h3 className="text-[22px] font-extrabold text-[#0f172a] dark:text-white tracking-tight leading-none">1,240</h3>
              <p className="text-[9px] font-bold text-slate-400 dark:text-slate-500 tracking-widest uppercase mt-1">Certifications</p>
            </div>
          </div>
        </section>
      </div>

      {/* About Section */}
      <section id="about" className="relative z-10 w-full py-24 px-6 md:px-12 bg-white/70 dark:bg-slate-900/70 border-t border-slate-200 dark:border-slate-800">
        <div className="max-w-[1440px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-20 items-center">
          <div className="lg:col-span-5 relative">
            <div className="absolute -inset-4 bg-slate-100 dark:bg-slate-800/50 rounded-2xl -z-10 transform -rotate-1"></div>
            <div className="bg-white dark:bg-slate-800 p-8 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
              <Quote className="w-8 h-8 text-blue-500/30 mb-4" />
              <p className="text-[17px] font-medium leading-relaxed text-slate-800 dark:text-slate-200">
                "Capacity building is not merely about accumulating hours of training. It is about fundamentally transforming how the machinery of government operates by empowering the individual."
              </p>
              <div className="mt-6 flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center">
                  <div className="w-4 h-4 rounded-full bg-blue-600 dark:bg-blue-400" />
                </div>
                <div>
                  <div className="text-[12px] font-bold text-slate-900 dark:text-white uppercase tracking-wider">Mission Karmayogi</div>
                  <div className="text-[11px] font-medium text-slate-500">Capacity Building Commission</div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="lg:col-span-7 flex flex-col items-start">
            <h2 className="text-3xl md:text-5xl font-extrabold tracking-tight text-slate-900 dark:text-white mb-6 uppercase">
              Aligning with <br/> Mission Karmayogi
            </h2>
            <p className="text-[15px] leading-relaxed max-w-2xl text-slate-600 dark:text-slate-400">
              Built for the Ministry of Statistics and Programme Implementation (MoSPI), this platform integrates directly with the Sunbird ecosystem to transition government capacity building from rule-based training to role-based competency development.
            </p>
            <p className="text-[15px] leading-relaxed max-w-2xl mt-4 text-slate-600 dark:text-slate-400">
              Through continuous assessment and real-time mapping against the national FRAC dictionary, we ensure that every official has a dynamic, personalized pathway to excellence.
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative z-10 w-full py-24 px-6 md:px-12 bg-slate-50/80 dark:bg-slate-950/80 border-t border-slate-200 dark:border-slate-800">
        <div className="max-w-[1440px] mx-auto">
          <div className="mb-16">
            <h2 className="text-3xl md:text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white uppercase mb-4">
              Enterprise Digital India <br/> Architecture
            </h2>
            <p className="text-[14px] font-medium text-slate-500 max-w-xl leading-relaxed">
              Leveraging the power of the national infrastructure to deliver precision capacity building at scale.
            </p>
          </div>

          {/* Bento Box Layout */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            {/* Feature 1 (Spans 2 columns on large screens) */}
            <div className="lg:col-span-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-8 md:p-10 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-blue-50 dark:bg-blue-900/20 rounded-lg flex items-center justify-center mb-6">
                <Radar className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="text-[18px] font-bold text-slate-900 dark:text-white tracking-tight mb-3">
                AI-Driven FRAC Mapping
              </h3>
              <p className="text-[14px] leading-relaxed text-slate-600 dark:text-slate-400 max-w-md">
                Real-time parsing of the Framework of Roles, Activities, and Competencies to identify exact proficiency deficits. Maps organizational goals directly to individual skill graphs.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-8 md:p-10 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg flex items-center justify-center mb-6">
                <Database className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
              </div>
              <h3 className="text-[18px] font-bold text-slate-900 dark:text-white tracking-tight mb-3">
                Semantic CBP Recommendations
              </h3>
              <p className="text-[14px] leading-relaxed text-slate-600 dark:text-slate-400">
                Vector-based matching against the national iGOT catalog to deliver hyper-personalized Competency Building Products.
              </p>
            </div>

            {/* Feature 3 (Full width or standard span) */}
            <div className="lg:col-span-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-8 md:p-10 shadow-sm hover:shadow-md transition-shadow flex flex-col md:flex-row items-start md:items-center gap-6 md:gap-12">
              <div className="flex-shrink-0 w-12 h-12 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg flex items-center justify-center">
                <LineChart className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
              </div>
              <div>
                <h3 className="text-[18px] font-bold text-slate-900 dark:text-white tracking-tight mb-3">
                  Sunbird Telemetry v3.1 Integration
                </h3>
                <p className="text-[14px] leading-relaxed text-slate-600 dark:text-slate-400 max-w-3xl">
                  Granular tracking of learner engagement and Item Response Theory (IRT) assessment grading. Ensures transparent auditing and robust data lakes for predictive capacity modeling across government departments.
                </p>
              </div>
            </div>

          </div>
        </div>
      </section>

    </div>
  );
};

export default LandingPage;
