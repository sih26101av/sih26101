/**
 * FILE: src/components/dashboard/MyCoursesView.tsx
 * Uses the shared Enrollment type from domain.ts - no local mock data.
 */

import React from 'react';
import { PlayCircle, Clock, CheckCircle2 } from 'lucide-react';
import type { Enrollment } from '../../types/domain';

interface MyCoursesViewProps { enrollments: Enrollment[]; }

const ProgressBar: React.FC<{ progress: number }> = ({ progress }) => (
  <div className="flex items-center gap-3">
    <div className="flex-1 h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden border border-slate-200 dark:border-slate-700">
      <div className="h-full bg-blue-600 dark:bg-blue-500 rounded-full transition-all duration-700 relative" style={{ width: `${progress}%` }}>
        <div className="absolute inset-0 bg-white/20 w-full h-full" />
      </div>
    </div>
    <span className="text-xs font-bold text-slate-700 dark:text-slate-300 w-9 text-right">{progress}%</span>
  </div>
);

const EnrolledCourseCard: React.FC<{ enrollment: Enrollment }> = ({ enrollment }) => {
  const { course, progressPercentage, remainingHours, lastAccessed } = enrollment;
  const isIGOT = course.source === 'iGOT Karmayogi';
  const providerClass = isIGOT
    ? 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-800 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800/50'
    : 'bg-teal-100 dark:bg-teal-900/30 text-teal-800 dark:text-teal-300 border-teal-200 dark:border-teal-800/50';

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md transition-all duration-200 flex flex-col overflow-hidden">
      <div className={`h-1.5 w-full ${isIGOT ? 'bg-indigo-500' : 'bg-teal-500'}`} />
      <div className="p-5 flex-1 flex flex-col">
        <div className="flex items-start justify-between gap-2 mb-3">
          <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${providerClass}`}>{course.source}</span>
          <span className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 font-medium">
            <Clock size={13} className="text-slate-400" />{remainingHours}h remaining
          </span>
        </div>
        <h3 className="text-slate-900 dark:text-slate-100 font-bold text-base leading-snug mb-4 flex-1">{course.title}</h3>
        <div className="mb-4">
          <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1.5">
            <span>Course Progress</span>
          </div>
          <ProgressBar progress={progressPercentage} />
        </div>
        <div className="mt-auto pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between gap-3">
          <span className="text-xs text-slate-400 dark:text-slate-500">
            Last accessed: {lastAccessed ? new Date(lastAccessed).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : 'N/A'}
          </span>
          <button className="flex items-center gap-1.5 px-4 py-2 bg-slate-900 dark:bg-slate-800 hover:bg-slate-800 dark:hover:bg-slate-700 text-white text-sm font-semibold rounded-lg transition-colors shadow-sm whitespace-nowrap">
            <PlayCircle size={16} />Continue
          </button>
        </div>
      </div>
    </div>
  );
};

const MyCoursesView: React.FC<MyCoursesViewProps> = ({ enrollments }) => (
  <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
    <div className="mb-6">
      <h2 className="text-xl font-bold text-slate-900 dark:text-white">Active Enrollments</h2>
      <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
        Data fetched live from iGOT Karmayogi via the Platform Adapter.
      </p>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {enrollments.map(enr => <EnrolledCourseCard key={enr.enrollmentId} enrollment={enr} />)}
    </div>
    {enrollments.length === 0 && (
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-8 flex flex-col items-center justify-center text-center shadow-sm">
        <CheckCircle2 size={40} className="text-green-500 dark:text-green-400 mb-3" />
        <h3 className="text-slate-800 dark:text-slate-200 font-bold text-lg">You are all caught up!</h3>
        <p className="text-slate-500 dark:text-slate-400 text-sm max-w-sm mt-1">
          No active courses. Check the Dashboard for AI-recommended courses.
        </p>
      </div>
    )}
  </div>
);

export default MyCoursesView;