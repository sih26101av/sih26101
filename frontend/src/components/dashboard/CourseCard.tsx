/**
 * FILE: src/components/dashboard/CourseCard.tsx
 */

import React from 'react';
import { Clock, ExternalLink, Sparkles, Target } from 'lucide-react';
import type { CourseRecommendation } from '../../types/domain';

interface CourseCardProps { recommendation: CourseRecommendation; }

const SOURCE_STYLES: Record<string, { badge: string; label: string }> = {
  'iGOT Karmayogi': { badge: 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-800 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800/50', label: 'iGOT Karmayogi' },
  NSSTA: { badge: 'bg-teal-100 dark:bg-teal-900/30 text-teal-800 dark:text-teal-300 border-teal-200 dark:border-teal-800/50', label: 'NSSTA' },
  'MoSPI Internal': { badge: 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300 border-orange-200 dark:border-orange-800/50', label: 'MoSPI Internal' },
};
const getSourceStyle = (s: string) => SOURCE_STYLES[s] ?? { badge: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700', label: s };

const MatchScoreBar: React.FC<{ score: number }> = ({ score }) => {
  const pct = Math.round(score * 100);
  const color = pct >= 90 ? 'bg-green-500' : pct >= 75 ? 'bg-blue-500' : 'bg-amber-400';
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all duration-700`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-bold text-slate-600 dark:text-slate-400 w-10 text-right">{pct}%</span>
    </div>
  );
};

const CourseCard: React.FC<CourseCardProps> = ({ recommendation }) => {
  const { course, matchScore, bridgesGapFor, aiMatchTag, priorityRank } = recommendation;
  const sourceStyle = getSourceStyle(course.source);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-800 dark:border-slate-800 shadow-sm hover:shadow-md hover:border-blue-600 dark:hover:border-blue-500 transition-all duration-200 flex flex-col h-full">
      <div className="px-4 pt-4 flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="w-7 h-7 rounded-full bg-blue-900 dark:bg-blue-800 text-white text-xs font-bold flex items-center justify-center flex-shrink-0 shadow">{priorityRank}</span>
          <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${sourceStyle.badge}`}>{sourceStyle.label}</span>
        </div>
        <span className="flex items-center gap-1 text-xs text-slate-400 dark:text-slate-500"><Clock size={11} /> {course.durationHours}h</span>
      </div>

      <div className="px-4 py-3 flex-1">
        <h3 className="text-slate-800 dark:text-slate-100 font-bold text-sm leading-snug mb-3">{course.title}</h3>
        <div className="mb-2">
          <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1">
            <span className="flex items-center gap-1"><Sparkles size={11} className="text-blue-500" /> AI Recommendation Match</span>
          </div>
          <MatchScoreBar score={matchScore} />
        </div>
        <div className="flex items-start gap-1.5 text-xs text-slate-500 dark:text-slate-400 mt-2">
          <Target size={12} className="mt-0.5 flex-shrink-0 text-blue-500" />
          <span>Addresses gap in <span className="font-semibold text-slate-700 dark:text-slate-300">{bridgesGapFor.skillName}</span></span>
        </div>
      </div>

      <div className="mx-4 mb-4">
        <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-100 dark:border-blue-900/50 rounded-lg px-3 py-2">
          <p className="text-xs text-blue-800 dark:text-blue-300 leading-relaxed">
            <span className="font-semibold">Why this course? </span>{aiMatchTag}
          </p>
        </div>
      </div>

      <div className="px-4 pb-4">
        <button className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-blue-800 dark:bg-blue-700 hover:bg-blue-700 dark:hover:bg-blue-600 text-white text-sm font-semibold rounded-lg transition-colors duration-150 group shadow-sm">
          <ExternalLink size={14} className="group-hover:translate-x-0.5 transition-transform" />
          {course.source === 'iGOT Karmayogi' ? 'Enroll on iGOT' : 'Enroll Now'}
        </button>
      </div>
    </div>
  );
};

export default CourseCard;
