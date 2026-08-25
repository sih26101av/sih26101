/**
 * FILE: src/pages/LearnerDashboard.tsx
 * Zero mock data. All data comes from useLearnerDashboard hook -> FastAPI backend.
 */

import React, { useState } from 'react';
import { LayoutDashboard, BookOpen, TrendingUp, LogOut, AlertTriangle, Sparkles, RefreshCcw, Moon, Sun } from 'lucide-react';
import { useLearnerDashboard } from '../hooks/useLearnerDashboard';
import { useTheme } from '../hooks/useTheme';
import ProfileHeader from '../components/dashboard/ProfileHeader';
import SkillGapCard from '../components/dashboard/SkillGapCard';
import CourseCard from '../components/dashboard/CourseCard';
import AssessmentUploadZone from '../components/dashboard/AssessmentUploadZone';
import MyCoursesView from '../components/dashboard/MyCoursesView';
import ProgressView from '../components/dashboard/ProgressView';

const LoadingSkeleton: React.FC = () => (
  <div className="animate-pulse space-y-4 p-6">
    <div className="h-36 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
    <div className="grid grid-cols-3 gap-4">
      <div className="col-span-2 h-96 bg-slate-100 dark:bg-slate-800/50 rounded-2xl" />
      <div className="space-y-4">
        <div className="h-28 bg-slate-100 dark:bg-slate-800/50 rounded-2xl" />
        <div className="h-64 bg-slate-100 dark:bg-slate-800/50 rounded-2xl" />
      </div>
    </div>
  </div>
);

const ErrorState: React.FC<{ message: string; onRetry: () => void }> = ({ message, onRetry }) => (
  <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 p-6">
    <div className="w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
      <AlertTriangle size={32} className="text-red-500 dark:text-red-400" />
    </div>
    <h2 className="text-slate-700 dark:text-slate-200 font-bold text-xl">Failed to Load Dashboard</h2>
    <p className="text-slate-500 dark:text-slate-400 text-sm text-center max-w-sm font-mono text-xs bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/50 rounded-lg p-3">{message}</p>
    <button onClick={onRetry} className="flex items-center gap-2 px-5 py-2.5 bg-blue-800 dark:bg-blue-700 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 transition-colors">
      <RefreshCcw size={14} /> Retry
    </button>
  </div>
);

const StatsSummary: React.FC<{ totalCompetencies: number; activeGaps: number; mandatoryGaps: number; recommendedCourses: number }> = (
  { totalCompetencies, activeGaps, mandatoryGaps, recommendedCourses }
) => {
  const stats = [
    { label: 'Competencies',      value: totalCompetencies,  color: 'text-slate-800 dark:text-slate-200' },
    { label: 'Active Gaps',       value: activeGaps,         color: 'text-red-600 dark:text-red-400' },
    { label: 'Mandatory Gaps',    value: mandatoryGaps,      color: 'text-orange-600 dark:text-orange-400' },
    { label: 'Recommendations',   value: recommendedCourses, color: 'text-blue-700 dark:text-blue-400' },
  ];
  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-4 transition-colors">
      <h3 className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-3">Learning Snapshot</h3>
      <div className="grid grid-cols-2 gap-3">
        {stats.map(({ label, value, color }) => (
          <div key={label} className="bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 rounded-xl p-3 text-center transition-colors">
            <div className={`text-2xl font-extrabold ${color}`}>{value}</div>
            <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 leading-tight">{label}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

type TabType = 'dashboard' | 'my-courses' | 'progress';

const Topbar: React.FC<{ userName?: string; activeTab: TabType; onTabChange: (tab: TabType) => void }> = ({ userName, activeTab, onTabChange }) => {
  const { theme, toggleTheme } = useTheme();
  return (
    <nav className="bg-slate-900 dark:bg-slate-950 border-b border-slate-800 px-6 py-3 flex items-center justify-between sticky top-0 z-50 shadow-md">
      <div className="flex items-center gap-3 cursor-pointer" onClick={() => onTabChange('dashboard')}>
        <div className="flex flex-col gap-0.5 w-1.5">
          <div className="h-1.5 bg-orange-500 rounded-full" />
          <div className="h-1.5 bg-white rounded-full" />
          <div className="h-1.5 bg-green-500 rounded-full" />
        </div>
        <div>
          <div className="text-white font-bold text-sm leading-none">MoSPI</div>
          <div className="text-slate-400 text-xs leading-none mt-0.5">Skill Intelligence Platform</div>
        </div>
      </div>

      <div className="hidden md:flex items-center gap-1">
        {([
          { id: 'dashboard',  icon: <LayoutDashboard size={14} />, label: 'Dashboard' },
          { id: 'my-courses', icon: <BookOpen size={14} />,        label: 'My Courses' },
          { id: 'progress',   icon: <TrendingUp size={14} />,      label: 'Progress' },
        ] as const).map(({ id, icon, label }) => (
          <button
            key={id}
            onClick={() => onTabChange(id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors duration-150
              ${activeTab === id ? 'bg-blue-800 text-white shadow-sm ring-1 ring-blue-700/50' : 'text-slate-400 hover:text-white hover:bg-slate-800/80'}`}
          >
            {icon}{label}
          </button>
        ))}
      </div>

      <div className="flex items-center gap-3">
        {userName && <span className="text-slate-400 text-xs hidden md:block">{userName}</span>}
        <button onClick={toggleTheme} className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors" title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}>
          {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
        </button>
        <button className="flex items-center gap-1.5 text-slate-400 hover:text-white text-xs transition-colors px-2 py-1.5 rounded-lg hover:bg-slate-800">
          <LogOut size={13} /> Sign Out
        </button>
      </div>
    </nav>
  );
};

const LearnerDashboard: React.FC<{ officialId?: string }> = ({ officialId = 'EMP-8472' }) => {
  const { profile, skillGaps, recommendations, enrollments, achievements, isLoading, error } = useLearnerDashboard(officialId);
  const [retryKey, setRetryKey] = useState(0);
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors">
        <Topbar activeTab={activeTab} onTabChange={setActiveTab} />
        <ErrorState message={error} onRetry={() => setRetryKey(k => k + 1)} />
      </div>
    );
  }

  const activeGaps    = skillGaps.filter(g => g.gap > 0);
  const mandatoryGaps = activeGaps.filter(g => g.isMandatory);
  const totalAssessed = profile?.competencyProfile.userCompetencies.length ?? 0;
  const sortedRecs    = [...recommendations].sort((a, b) => a.priorityRank - b.priorityRank);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors" key={retryKey}>
      <Topbar userName={profile?.govId} activeTab={activeTab} onTabChange={setActiveTab} />

      {isLoading || !profile ? (
        <LoadingSkeleton />
      ) : (
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
          <ProfileHeader profile={profile} totalAssessed={totalAssessed} />

          {activeTab === 'dashboard' && (
            <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                <div className="lg:col-span-2">
                  <SkillGapCard skillGaps={skillGaps} />
                </div>
                <div className="flex flex-col gap-5">
                  <StatsSummary
                    totalCompetencies={totalAssessed}
                    activeGaps={activeGaps.length}
                    mandatoryGaps={mandatoryGaps.length}
                    recommendedCourses={recommendations.length}
                  />
                  <AssessmentUploadZone onFileSelect={(f) => console.info('Ready:', f.name)} />
                </div>
              </div>
              <section>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-slate-900 dark:text-white font-bold text-lg flex items-center gap-2">
                      <Sparkles size={18} className="text-blue-600 dark:text-blue-500" /> Personalized AI Learning Pathway
                    </h2>
                    <p className="text-slate-500 dark:text-slate-400 text-xs mt-0.5">Generated by HybridRecommendationStrategy · Ranked by relevance</p>
                  </div>
                  <span className="text-xs text-slate-400 dark:text-slate-500 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-3 py-1 rounded-full">{sortedRecs.length} courses found</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  {sortedRecs.map((rec) => <CourseCard key={rec.course.courseId} recommendation={rec} />)}
                </div>
              </section>
            </div>
          )}

          {/* Live data — no MOCK_ constants anywhere */}
          {activeTab === 'my-courses' && <MyCoursesView enrollments={enrollments} />}
          {activeTab === 'progress'   && <ProgressView achievements={achievements} skillGaps={skillGaps} />}

          <footer className="text-center py-6 border-t border-slate-200 dark:border-slate-800 mt-8 transition-colors">
            <p className="text-xs text-slate-400 dark:text-slate-500">
              Ministry of Statistics and Programme Implementation (MoSPI) · AI-Enabled Skill Intelligence Platform · SIH 2024 Prototype
            </p>
            <p className="text-xs text-slate-300 dark:text-slate-600 mt-1">
              All data sourced live from FastAPI (port 8000) via <span className="font-mono">IgotPlatformAdapter</span>
            </p>
          </footer>
        </main>
      )}
    </div>
  );
};

export default LearnerDashboard;