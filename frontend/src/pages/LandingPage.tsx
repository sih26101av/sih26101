import React from 'react';
import { Link } from 'react-router-dom';
import { Users, BookOpen, Activity, Award, Hash, ArrowRight, Sun, Moon } from 'lucide-react';
import { useTheme } from '../hooks/useTheme';

const LandingPage: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen font-sans flex flex-col relative bg-[#f8fafc] dark:bg-slate-900 transition-colors duration-300 overflow-hidden">
      {/* Background Image Layer */}
      <div 
        className="absolute inset-0 z-0 pointer-events-none opacity-[0.25] dark:opacity-10 dark:invert"
        style={{
          backgroundImage: `url('/bg-new-topo.png')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          transform: 'scale(1.2) translateX(-5%)'
        }}
      />
      <div className="max-w-[1100px] w-full mx-auto px-6 flex flex-col flex-1 relative z-10">
        
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
              <a href="#" className="text-[11px] font-bold text-slate-700 dark:text-slate-300 hover:text-black dark:hover:text-white tracking-wide transition-colors">HOME</a>
              <a href="#" className="text-[11px] font-bold text-slate-700 dark:text-slate-300 hover:text-black dark:hover:text-white tracking-wide transition-colors">ABOUT</a>
              <a href="#" className="text-[11px] font-bold text-slate-700 dark:text-slate-300 hover:text-black dark:hover:text-white tracking-wide transition-colors">FEATURES</a>
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
                DASHBOARD <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <main className="flex-1 flex flex-col lg:flex-row items-center justify-between pt-6 pb-12">
          
          {/* Left Content */}
          <div className="w-full lg:w-[55%] flex flex-col items-start text-left z-10">
            
            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800/80 border border-slate-200/60 dark:border-slate-700 text-slate-600 dark:text-slate-300 text-[11px] font-medium mb-6 shadow-sm transition-colors duration-300">
              <Hash className="w-3 h-3 text-[#f59e0b]" />
              Powered by MoSPI AI Engine
            </div>
            
            <h1 className="text-[2.75rem] md:text-[3.5rem] leading-[1.05] font-extrabold tracking-tight text-[#0f172a] dark:text-white mb-5 uppercase transition-colors duration-300">
              Empowering India's <br/>
              Official Statistical <br/>
              System
            </h1>
            
            <p className="text-[13px] md:text-[14px] text-slate-600 dark:text-slate-400 max-w-[400px] leading-[1.6] mb-8 font-medium transition-colors duration-300">
              A next-generation competency tracking platform. We combine AI-driven skill-gap analysis with personalized iGOT learning pathways.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 mt-2">
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
          <div className="w-full lg:w-[45%] mt-8 lg:mt-0 relative flex justify-center lg:justify-end items-center pointer-events-none">
            <img 
              src="/india-map.png" 
              alt="India Skill Network Map" 
              className="w-full max-w-[450px] object-contain mix-blend-darken dark:mix-blend-screen dark:invert transition-all duration-300"
              style={{ filter: 'drop-shadow(0 25px 25px rgba(0, 0, 0, 0.15)) brightness(1.05)' }} 
            />
          </div>
        </main>

        {/* Metrics Section */}
        <section className="w-full pb-10 z-10 mt-auto">
          <div className="w-full grid grid-cols-2 md:grid-cols-4 bg-white dark:bg-slate-800/80 backdrop-blur-sm shadow-xl shadow-slate-200/40 dark:shadow-none border border-transparent dark:border-slate-700/60 rounded-2xl py-6 px-4 divide-y md:divide-y-0 md:divide-x divide-slate-100 dark:divide-slate-700 transition-colors duration-300">
            
            {/* Metric 1 */}
            <div className="flex flex-col items-center justify-center py-2">
              <Users className="w-5 h-5 text-[#0f172a] dark:text-blue-400 stroke-[1.5] mb-2" />
              <h3 className="text-[22px] font-extrabold text-[#0f172a] dark:text-white tracking-tight leading-none">12.4k</h3>
              <p className="text-[9px] font-bold text-slate-400 dark:text-slate-500 tracking-widest uppercase mt-1.5">Active Users</p>
            </div>

            {/* Metric 2 */}
            <div className="flex flex-col items-center justify-center py-2">
              <BookOpen className="w-5 h-5 text-[#0f172a] dark:text-blue-400 stroke-[1.5] mb-2" />
              <h3 className="text-[22px] font-extrabold text-[#0f172a] dark:text-white tracking-tight leading-none">458</h3>
              <p className="text-[9px] font-bold text-slate-400 dark:text-slate-500 tracking-widest uppercase mt-1.5">Courses Matched</p>
            </div>

            {/* Metric 3 */}
            <div className="flex flex-col items-center justify-center py-2">
              <Activity className="w-5 h-5 text-[#0f172a] dark:text-blue-400 stroke-[1.5] mb-2" />
              <h3 className="text-[22px] font-extrabold text-[#0f172a] dark:text-white tracking-tight leading-none">89k</h3>
              <p className="text-[9px] font-bold text-slate-400 dark:text-slate-500 tracking-widest uppercase mt-1.5">Skill Gaps Resolved</p>
            </div>

            {/* Metric 4 */}
            <div className="flex flex-col items-center justify-center py-2">
              <Award className="w-5 h-5 text-[#0f172a] dark:text-blue-400 stroke-[1.5] mb-2" />
              <h3 className="text-[22px] font-extrabold text-[#0f172a] dark:text-white tracking-tight leading-none">1,240</h3>
              <p className="text-[9px] font-bold text-slate-400 dark:text-slate-500 tracking-widest uppercase mt-1.5">Certifications</p>
            </div>

          </div>
        </section>

      </div>
    </div>
  );
};

export default LandingPage;
