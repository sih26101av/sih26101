/**
 * FILE: src/pages/LearnerDashboard.tsx
 */

import React, { useState } from "react";
import {
  LayoutDashboard, BookOpen, TrendingUp, LogOut, AlertTriangle,
  Sparkles, RefreshCcw, Moon, Sun, Lock, Search, Briefcase, Home, Bot
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useLearnerDashboard } from "../hooks/useLearnerDashboard";
import { useTheme } from "../hooks/useTheme";
import { useAuth } from "../context/AuthContext";
import ProfileHeader from "../components/dashboard/ProfileHeader";
import SkillGapCard from "../components/dashboard/SkillGapCard";
import CourseCard from "../components/dashboard/CourseCard";
import MyCoursesView from "../components/dashboard/MyCoursesView";
import ProgressView from "../components/dashboard/ProgressView";
import ChatWidget from "../components/dashboard/ChatWidget";

// â”€â”€â”€ Loading Skeleton â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
const LoadingSkeleton: React.FC = () => (
  <div className="animate-pulse space-y-5 p-6">
    <div className="h-28 bg-white/60 rounded-2xl shadow-sm" />
    <div className="grid grid-cols-3 gap-5">
      <div className="col-span-2 h-96 bg-white/60 rounded-2xl shadow-sm" />
      <div className="space-y-4">
        <div className="h-48 bg-white/60 rounded-2xl shadow-sm" />
        <div className="h-44 bg-white/60 rounded-2xl shadow-sm" />
      </div>
    </div>
  </div>
);

// â”€â”€â”€ Error State â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
const ErrorState: React.FC<{ message: string; onRetry: () => void }> = ({ message, onRetry }) => (
  <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 p-6">
    <div className="w-16 h-16 rounded-full bg-red-50 border border-red-100 flex items-center justify-center shadow-sm">
      <AlertTriangle size={30} className="text-red-500" />
    </div>
    <h2 className="text-slate-800 font-bold text-lg">Failed to Load Dashboard</h2>
    <p className="text-slate-500 text-sm max-w-sm text-center">{message}</p>
    <button
      onClick={onRetry}
      className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white font-semibold rounded-xl text-sm shadow-md hover:bg-blue-700 transition-colors"
    >
      <RefreshCcw size={14} /> Retry
    </button>
  </div>
);

// â”€â”€â”€ Learning Snapshot â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
const StatsSummary: React.FC<{
  totalCompetencies: number;
  activeGaps: number;
  mandatoryGaps: number;
  recommendedCourses: number;
}> = ({ totalCompetencies, activeGaps, mandatoryGaps, recommendedCourses }) => {
  const stats = [
    {
      label: "Competencies",
      value: totalCompetencies,
      valueColor: "text-slate-900 dark:text-white",
      iconBg: "bg-[#eff6ff] dark:bg-blue-900/30",
      icon: <Briefcase size={20} className="text-slate-700 dark:text-blue-400" />,
    },
    {
      label: "Active Gaps",
      value: activeGaps,
      valueColor: "text-[#7f1d1d] dark:text-red-400",
      iconBg: "bg-[#fee2e2] dark:bg-red-900/30",
      icon: <AlertTriangle size={20} className="text-[#991b1b] dark:text-red-400" />,
    },
    {
      label: "Mandatory Gaps",
      value: mandatoryGaps,
      valueColor: "text-[#d97706] dark:text-orange-400",
      iconBg: "bg-[#f1f5f9] dark:bg-slate-700/50",
      icon: <Lock size={20} className="text-slate-600 dark:text-orange-400" />,
    },
    {
      label: "Recommendations",
      value: recommendedCourses,
      valueColor: "text-[#2563eb] dark:text-blue-400",
      iconBg: "bg-[#eff6ff] dark:bg-blue-900/30",
      icon: <Search size={20} className="text-slate-700 dark:text-blue-400" />,
    },
  ];

  return (
    <div className="bg-white dark:bg-slate-800/40 rounded-2xl border border-slate-200 dark:border-slate-700/50 shadow-sm p-6 transition-colors duration-300">
      <p className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-4 transition-colors duration-300">
        Learning Snapshot
      </p>
      <div className="grid grid-cols-2 gap-4">
        {stats.map(({ label, value, valueColor, iconBg, icon }) => (
          <div
            key={label}
            className="bg-white dark:bg-slate-800/60 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700/50 p-4 flex flex-col items-center justify-center hover:-translate-y-0.5 transition-all duration-300"
          >
            <div className="flex items-center gap-4 w-full justify-center mb-1.5">
              <div className={`w-[42px] h-[42px] rounded-[12px] flex items-center justify-center transition-colors duration-300 ${iconBg}`}>
                {icon}
              </div>
              <span className={`text-[32px] font-black leading-none transition-colors duration-300 ${valueColor}`}>{value}</span>
            </div>
            <span className="text-[12px] font-semibold text-slate-700 dark:text-slate-300 transition-colors duration-300">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// â”€â”€â”€ Topbar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
type TabType = "dashboard" | "my-courses" | "progress";

const Topbar: React.FC<{
  userName?: string;
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}> = ({ userName, activeTab, onTabChange }) => {
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  return (
    <nav className="bg-[#1e293b] px-6 py-3 flex items-center justify-between sticky top-0 z-50 shadow-md">
      {/* Logo and Title */}
      <div
        className="flex items-center gap-3 cursor-pointer select-none"
        onClick={() => onTabChange("dashboard")}
      >
        <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center overflow-hidden">
          {/* Placeholder for the emblem */}
          <div className="w-6 h-6 border-[1.5px] border-slate-400 rounded-full flex flex-col items-center justify-center">
             <div className="w-1 h-1 bg-slate-400 rounded-full mb-[1px]"></div>
             <div className="w-3 h-1.5 border border-slate-400 rounded-t-full"></div>
          </div>
        </div>
        <div className="text-white font-semibold text-lg tracking-wide">
          National Statistical Office (NSO) Training Portal
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-3 text-white">
        <button
          onClick={() => navigate("/")}
          className="p-1.5 rounded-full hover:bg-white/10 transition-colors"
          title="Go to Home"
        >
          <Home size={18} />
        </button>
        <button
          onClick={toggleTheme}
          className="p-1.5 rounded-full hover:bg-white/10 transition-colors"
          title="Toggle Theme"
        >
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <button className="p-1.5 hover:bg-white/10 rounded-full transition-colors" title="Search">
          <Search size={18} />
        </button>
        <button className="w-8 h-8 rounded-full bg-slate-200 text-slate-800 flex items-center justify-center hover:bg-white transition-colors relative">
          <div className="w-[11px] h-[11px] border-[1.5px] border-current rounded-full absolute top-[6px]"></div>
          <div className="w-[18px] h-[8px] border-[1.5px] border-current rounded-t-full absolute bottom-[4px]"></div>
        </button>
      </div>
    </nav>
  );
};

// Sign Out button reads its own auth context instance
const TopbarSignOut: React.FC = () => {
  const { logout } = useAuth();
  const navigate   = useNavigate();
  const handleSignOut = async () => {
    await logout();
    navigate("/login", { replace: true });
  };
  return (
    <button
      onClick={handleSignOut}
      className="flex items-center gap-1.5 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white text-xs font-semibold transition-colors px-3 py-1.5 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent hover:border-slate-200 dark:hover:border-slate-700"
    >
      <LogOut size={13} /> Sign Out
    </button>
  );
};

// ——— Main Dashboard ————————————————————————————————————————————————————————————————————————
const LearnerDashboard: React.FC<{ officialId?: string }> = ({ officialId }) => {
  const { user: authUser } = useAuth();
  const navigate = useNavigate();

  // Priority: AuthContext user → prop → first real user from mock server
  const userId = authUser?.username ?? officialId ?? 'usr_720465595';


  const { profile, skillGaps, recommendations, enrollments, achievements, isLoading, error } =
    useLearnerDashboard(userId);
  const [retryKey, setRetryKey] = useState(0);
  const [activeTab, setActiveTab] = useState<TabType>("dashboard");

  const activeGaps = skillGaps.filter((g) => g.gap > 0);
  const mandatoryGaps = activeGaps.filter((g) => g.isMandatory);
  const totalAssessed = profile?.competencyProfile.userCompetencies.length ?? 0;
  const sortedRecs = [...recommendations].sort((a, b) => a.priorityRank - b.priorityRank);

  if (error) {
    return (
      <div className="min-h-screen bg-[#eef2f7] relative" key={retryKey}>
        <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: 'url("/bg-mesh.png")', backgroundSize: "cover", backgroundPosition: "center", backgroundRepeat: "no-repeat", opacity: 0.6 }} />
        <div className="relative z-10 flex flex-col min-h-screen">
          <Topbar activeTab={activeTab} onTabChange={setActiveTab} />
          <ErrorState message={error} onRetry={() => setRetryKey((k) => k + 1)} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F2F0EF] dark:bg-slate-950 relative transition-colors duration-300" key={retryKey}>
      {/* Network Mesh Background */}
      <div
        className="absolute inset-0 z-0 pointer-events-none"
        style={{
          backgroundImage: 'url("/bg-mesh.png")',
          backgroundSize: "cover",
          backgroundPosition: "top right",
          backgroundRepeat: "no-repeat",
          opacity: 0.5,
        }}
      />

      <div className="relative z-10 flex flex-col min-h-screen">
        <Topbar userName={profile?.govId} activeTab={activeTab} onTabChange={setActiveTab} />


        {isLoading || !profile ? (
          <LoadingSkeleton />
        ) : (
          <main className="flex-1 w-full max-w-[1440px] mx-auto px-6 py-6 space-y-6">
            <ProfileHeader profile={profile} totalAssessed={totalAssessed} />

            {activeTab === "dashboard" && (
              <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                {/* Main 2-col grid using 2/3 and 1/3 ratio */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                  {/* Left: Skill Gap */}
                  <div className="lg:col-span-2">
                    <SkillGapCard skillGaps={skillGaps} />
                  </div>
                  {/* Right: Stats + AI Zone */}
                  <div className="flex flex-col gap-6 lg:col-span-1">
                    <StatsSummary
                      totalCompetencies={totalAssessed}
                      activeGaps={activeGaps.length}
                      mandatoryGaps={mandatoryGaps.length}
                      recommendedCourses={recommendations.length}
                    />
                    <div className="bg-white dark:bg-slate-800/40 rounded-2xl border border-slate-200 dark:border-slate-700/50 shadow-sm p-6 flex flex-col gap-5 transition-colors duration-300 h-full justify-between">
                      <div>
                        <div className="flex items-center gap-4 mb-4">
                          <div className="w-[44px] h-[44px] rounded-[14px] bg-[#eef2ff] dark:bg-blue-900/40 flex items-center justify-center flex-shrink-0 transition-colors duration-300">
                            <Bot size={22} className="text-blue-800 dark:text-blue-400 transition-colors duration-300" />
                          </div>
                          <div>
                            <h3 className="text-slate-900 dark:text-white font-extrabold text-[15px] leading-tight tracking-tight mb-0.5 transition-colors duration-300">AI Assessment Studio</h3>
                            <p className="text-slate-500 dark:text-slate-400 text-[12px] transition-colors duration-300">Upload MoSPI training documents to auto-generate custom assessments.</p>
                          </div>
                        </div>
                      </div>
                      
                      <button
                        onClick={() => navigate("/assessment")}
                        className="relative w-full bg-white dark:bg-slate-800 text-blue-900 dark:text-white border-2 border-blue-900 dark:border-blue-700 font-bold text-[14px] py-2.5 rounded-[12px] flex items-center justify-center gap-2 transition-all duration-300 hover:bg-blue-50 dark:hover:bg-slate-700"
                      >
                        <Bot size={18} className="text-blue-900 dark:text-blue-200 relative z-10 transition-colors duration-300" />
                        <span className="relative z-10">Open Assessment Studio</span>
                      </button>
                    </div>
                  </div>
                </div>

                {/* Recommended Courses section */}
                <section className="bg-[#F2F0EF] dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-white/80 dark:border-slate-700/50 shadow-[0_2px_12px_-2px_rgba(0,0,0,0.05)] transition-colors duration-300">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-5 gap-3">
                    <div>
                      <h2 className="text-slate-900 dark:text-white font-extrabold text-lg flex items-center gap-2">
                        <Sparkles size={18} className="text-blue-500 dark:text-blue-400" />
                        AI Recommended Learning Pathway
                      </h2>
                      <p className="text-slate-400 dark:text-slate-500 text-xs mt-1">
                        Directly addresses your active competency gaps
                      </p>
                    </div>
                    <span className="text-xs font-bold text-slate-500 dark:text-slate-400 bg-white dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600/50 px-3 py-1.5 rounded-full shadow-sm whitespace-nowrap">
                      {sortedRecs.length} Courses Found
                    </span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {sortedRecs.map((rec) => (
                      <CourseCard key={rec.course.courseId} recommendation={rec} />
                    ))}
                    {sortedRecs.length === 0 && (
                      <p className="col-span-4 text-center text-slate-400 dark:text-slate-500 text-sm py-8">
                        No recommendations available â€” all competencies are met!
                      </p>
                    )}
                  </div>
                </section>
              </div>
            )}

            {activeTab === "my-courses" && <MyCoursesView enrollments={enrollments} />}
            {activeTab === "progress" && <ProgressView achievements={achievements} skillGaps={skillGaps} />}

            <footer className="text-center py-6 mt-4">
              <p className="text-[11px] font-medium text-slate-400 dark:text-slate-500">
                MoSPI Skill Intelligence Platform &middot; Powered by iGOT Karmayogi
              </p>
            </footer>
          </main>
        )}

        {/* ── Gyan AI Chat Widget ──────────────────────────────────────────── */}
        {profile && (
          <ChatWidget
            officialId={userId}
            fullName={profile.fullName}
            govId={profile.govId}
            jobRole={profile.jobRole.title}
            department={profile.department}
            skillGaps={skillGaps}
            recommendations={recommendations}
          />
        )}
      </div>
    </div>
  );
};

export default LearnerDashboard;
