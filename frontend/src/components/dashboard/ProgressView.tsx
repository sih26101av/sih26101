/**
 * FILE: src/components/dashboard/ProgressView.tsx
 * Uses the shared Achievement type from domain.ts - no local mock data.
 */

import React, { useMemo } from 'react';
import { Target, Trophy, ChevronRight, Activity } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import type { SkillGapEntry, Achievement } from '../../types/domain';
import { useTheme } from '../../hooks/useTheme';

interface ProgressViewProps {
  achievements: Achievement[];
  skillGaps: SkillGapEntry[];
}

const AchievementRow: React.FC<{ achievement: Achievement; isLast: boolean }> = ({ achievement, isLast }) => {
  const isQuiz = achievement.category === 'RAG Quiz';
  return (
    <div className="relative flex items-start gap-4 pb-6 group">
      {!isLast && <div className="absolute left-5 top-10 bottom-0 w-px bg-slate-200 dark:bg-slate-700 group-hover:bg-blue-300 dark:group-hover:bg-blue-600 transition-colors" />}
      <div className={`relative z-10 w-10 h-10 rounded-full flex items-center justify-center border-4 border-white dark:border-slate-900 shadow-sm flex-shrink-0
        ${isQuiz ? 'bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400' : 'bg-emerald-100 dark:bg-emerald-900/40 text-emerald-600 dark:text-emerald-400'}`}>
        {isQuiz ? <Target size={16} /> : <Trophy size={16} />}
      </div>
      <div className="flex-1 bg-[#F2F0EF] dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm group-hover:border-blue-200 dark:group-hover:border-blue-800 transition-all">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-1">
          <h4 className="text-slate-800 dark:text-slate-200 font-bold text-sm">Passed {achievement.category}: {achievement.title}</h4>
          <span className="text-xs font-semibold px-2 py-1 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded-lg whitespace-nowrap">
            Score: {achievement.score}%
          </span>
        </div>
        <p className="text-xs text-slate-400 dark:text-slate-500 font-medium">
          {new Date(achievement.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
        </p>
      </div>
    </div>
  );
};

const CustomTooltip = ({ active, payload, theme }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const isDark = theme === 'dark';
    return (
      <div className={`p-3 rounded-lg shadow-lg border text-xs ${isDark ? 'bg-slate-800 border-slate-700 text-slate-200' : 'bg-white border-slate-200 text-slate-700'}`}>
        <p className="font-bold mb-2 break-words max-w-[200px]">{data.fullSubject}</p>
        <div className="space-y-1">
          <p className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-blue-500"></span><span className="font-medium">Current:</span> {data.Current}/5</p>
          <p className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-slate-400"></span><span className="font-medium">Target:</span> {data.Target}/5</p>
        </div>
        {data.Target > data.Current && (
          <p className="mt-2 pt-2 border-t border-slate-200 dark:border-slate-700 text-orange-500 dark:text-orange-400 font-semibold">
            Gap: {data.Target - data.Current} level(s)
          </p>
        )}
      </div>
    );
  }
  return null;
};

const ProgressView: React.FC<ProgressViewProps> = ({ achievements, skillGaps }) => {
  const { theme } = useTheme();

  const radarData = useMemo(() => skillGaps.map(gap => ({
    subject: gap.competency.skillName.length > 20 ? gap.competency.skillName.substring(0, 18) + '…' : gap.competency.skillName,
    fullSubject: gap.competency.skillName,
    Current: gap.currentLevel,
    Target: gap.requiredLevel,
    fullMark: 5,
  })), [skillGaps]);

  const textColor = theme === 'dark' ? '#94a3b8' : '#64748b';
  const gridColor = theme === 'dark' ? '#334155' : '#e2e8f0';

  return (
    <div className="animate-in fade-in slide-in-from-bottom-2 duration-300 space-y-6">
      <div className="mb-2">
        <h2 className="text-xl font-bold text-slate-900 dark:text-white">Learning Progress & Analytics</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">All data sourced live from the FastAPI backend.</p>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-[#F2F0EF] dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden flex flex-col h-[400px]">
          <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 flex items-center justify-between">
            <h3 className="text-slate-800 dark:text-slate-200 font-bold text-sm flex items-center gap-2">
              <Activity size={16} className="text-blue-600 dark:text-blue-500" />Competency Radar
            </h3>
            <span className="text-xs text-slate-400 dark:text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-full border border-slate-200 dark:border-slate-700">Live Data</span>
          </div>
          <div className="flex-1 p-2 flex flex-col items-center justify-center bg-slate-50/30 dark:bg-slate-950/20">
            {radarData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                  <PolarGrid stroke={gridColor} />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: textColor, fontSize: 11, fontWeight: 500 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 5]} tick={{ fill: textColor, fontSize: 10 }} tickCount={6} stroke={gridColor} />
                  <Tooltip content={<CustomTooltip theme={theme} />} />
                  <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} iconType="circle" />
                  <Radar name="Target Level"  dataKey="Target"  stroke="#94a3b8" fill="#94a3b8" fillOpacity={0.15} strokeDasharray="4 4" />
                  <Radar name="Current Level" dataKey="Current" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.4} />
                </RadarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-slate-400 text-sm">No competency data available.</p>
            )}
          </div>
        </div>

        <div className="bg-[#F2F0EF] dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden flex flex-col h-[400px]">
          <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 flex items-center justify-between sticky top-0 z-10">
            <h3 className="text-slate-800 dark:text-slate-200 font-bold text-sm flex items-center gap-2"><Trophy size={16} className="text-amber-500" />Recent Achievements</h3>
            <button className="text-xs text-blue-600 dark:text-blue-400 font-semibold hover:underline flex items-center">View All <ChevronRight size={14} /></button>
          </div>
          <div className="flex-1 p-5 overflow-y-auto custom-scrollbar">
            {achievements.length > 0 ? (
              <div className="pt-2">{achievements.map((a, i) => <AchievementRow key={a.id} achievement={a} isLast={i === achievements.length - 1} />)}</div>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-400 dark:text-slate-500">
                <Target size={32} className="mb-2 opacity-50" />
                <p className="text-sm">No achievements yet.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressView;