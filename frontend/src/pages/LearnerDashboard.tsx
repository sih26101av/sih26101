/**
 * FILE: src/pages/LearnerDashboard.tsx
 */

import React, { useState } from "react";
import {
  LayoutDashboard, BookOpen, TrendingUp, LogOut, AlertTriangle,
  Sparkles, RefreshCcw, Moon, Sun, Lock, Search, Briefcase, Home
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useLearnerDashboard } from "../hooks/useLearnerDashboard";
import { useTheme } from "../hooks/useTheme";
import { useAuth } from "../context/AuthContext";
import ProfileHeader from "../components/dashboard/ProfileHeader";
import SkillGapCard from "../components/dashboard/SkillGapCard";
import CourseCard from "../components/dashboard/CourseCard";
import AssessmentUploadZone from "../components/dashboard/AssessmentUploadZone";
import MyCoursesView from "../components/dashboard/MyCoursesView";
import ProgressView from "../components/dashboard/ProgressView";

// ─── Loading Skeleton ─────────────────────────────────────────────────────────
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

// ─── Error State ──────────────────────────────────────────────────────────────
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

// ─── Learning Snapshot ─────────────────────────────────────────────────────────
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
    <div className="bg-white dark:bg-slate-800/40 rounded-3xl border border-slate-100 dark:border-slate-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-none p-6 transition-colors duration-300">
      <p className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-4 transition-colors duration-300">
        Learning Snapshot
      </p>
      <div className="grid grid-cols-2 gap-4">
        {stats.map(({ label, value, valueColor, iconBg, icon }) => (
          <div
            key={label}
            className="bg-white dark:bg-slate-800/60 rounded-[20px] shadow-[0_4px_16px_-4px_rgba(0,0,0,0.05)] dark:shadow-none border border-slate-100 dark:border-slate-700/50 p-4 flex flex-col items-center justify-center hover:-translate-y-0.5 transition-all duration-300"
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

// ─── Topbar ────────────────────────────────────────────────────────────────────
type TabType = "dashboard" | "my-courses" | "progress";

const Topbar: React.FC<{
  userName?: string;
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}> = ({ userName, activeTab, onTabChange }) => {
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  return (
    <nav className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border-b border-slate-200/80 dark:border-slate-700/50 px-5 md:px-6 py-2 flex items-center justify-between sticky top-0 z-50 shadow-[0_1px_8px_-2px_rgba(0,0,0,0.06)]">
      {/* Logo */}
      <div
        className="flex items-center gap-2.5 cursor-pointer select-none"
        onClick={() => onTabChange("dashboard")}
      >
        <div className="flex flex-col gap-[3px] w-[5px]">
          <div className="h-[5px] w-[5px] bg-[#FF9933] rounded-full" />
          <div className="h-[5px] w-[5px] bg-slate-400 rounded-full" />
          <div className="h-[5px] w-[5px] bg-[#138808] rounded-full" />
        </div>
        <div>
          <div className="text-slate-900 dark:text-white font-extrabold text-[13px] leading-none tracking-wide">MoSPI</div>
          <div className="text-slate-400 dark:text-slate-500 text-[10px] leading-none mt-[3px]">Skill Intelligence Platform</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="hidden md:flex items-center gap-1 bg-slate-100/80 dark:bg-slate-800/80 rounded-full px-1.5 py-1.5">
        {(
          [
            { id: "dashboard", icon: <LayoutDashboard size={13} />, label: "Dashboard" },
            { id: "my-courses", icon: <BookOpen size={13} />, label: "My Courses" },
            { id: "progress", icon: <TrendingUp size={13} />, label: "Progress" },
          ] as const
        ).map(({ id, icon, label }) => (
          <button
            key={id}
            onClick={() => onTabChange(id)}
            className={`flex items-center gap-1.5 px-4 py-1.5 rounded-full text-xs font-semibold transition-all duration-200 ${
              activeTab === id
                ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm border border-slate-200/80 dark:border-slate-600/50"
                : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
            }`}
          >
            {icon} {label}
          </button>
        ))}
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-3">
        {userName && (
          <span className="text-slate-600 dark:text-slate-300 text-xs font-semibold hidden md:block bg-slate-100/80 dark:bg-slate-800/80 px-3 py-1.5 rounded-full">
            {userName}
          </span>
        )}
        <button
          onClick={() => navigate("/")}
          className="p-1.5 rounded-full text-slate-400 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors flex items-center justify-center"
          title="Go to Home"
        >
          <Home size={15} />
        </button>
        <button
          onClick={toggleTheme}
          className="p-1.5 rounded-full text-slate-400 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          title="Toggle Theme"
        >
          {theme === "dark" ? <Sun size={15} /> : <Moon size={15} />}
        </button>
        <button className="flex items-center gap-1.5 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white text-xs font-semibold transition-colors px-3 py-1.5 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent hover:border-slate-200 dark:hover:border-slate-700">
          <LogOut size={13} /> Sign Out
        </button>
      </div>
    </nav>
  );
};

// ─── Main Dashboard ────────────────────────────────────────────────────────────
const LearnerDashboard: React.FC<{ officialId?: string }> = ({ officialId }) => {
  const { user: authUser } = useAuth();

  // Priority: AuthContext user (set by LoginPage) → prop → first user in users.json
  const userId = authUser?.userId ?? officialId ?? 'usr_720465595';

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
    <div className="min-h-screen bg-[#f8fafc] dark:bg-slate-950 relative transition-colors duration-300" key={retryKey}>
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
                    <AssessmentUploadZone onFileSelect={(f) => console.info("Ready:", f.name)} />
                  </div>
                </div>

                {/* Recommended Courses section */}
                <section className="bg-white/70 dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-white/80 dark:border-slate-700/50 shadow-[0_2px_12px_-2px_rgba(0,0,0,0.05)] transition-colors duration-300">
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
                        No recommendations available — all competencies are met!
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
      </div>
    </div>
  );
};

export default LearnerDashboard;