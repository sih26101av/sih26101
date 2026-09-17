/**
 * FILE: src/components/dashboard/LearningSnapshot.tsx
 *
 * Donut of the learner's enrollment mix (completed / in progress / not started),
 * derived entirely from the live `enrollments` payload. The centre figure is the
 * mean progress across all enrolled courses.
 */

import React, { useMemo } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import type { Enrollment } from '../../types/domain';

const COLORS = {
  completed: '#0b2a55',   // gov navy
  inProgress: '#f97316',  // accent orange
  notStarted: '#cbd5e1',  // slate 300
};

interface Props { enrollments: Enrollment[]; }

const LearningSnapshot: React.FC<Props> = ({ enrollments }) => {
  const { data, overall, total } = useMemo(() => {
    const completed = enrollments.filter((e) => e.progressPercentage >= 100).length;
    const notStarted = enrollments.filter((e) => e.progressPercentage <= 0).length;
    const inProgress = enrollments.length - completed - notStarted;
    const mean = enrollments.length
      ? Math.round(enrollments.reduce((s, e) => s + e.progressPercentage, 0) / enrollments.length)
      : 0;
    return {
      total: enrollments.length,
      overall: mean,
      data: [
        { name: 'Completed', value: completed, color: COLORS.completed },
        { name: 'In Progress', value: inProgress, color: COLORS.inProgress },
        { name: 'Not Started', value: notStarted, color: COLORS.notStarted },
      ],
    };
  }, [enrollments]);

  if (total === 0) {
    return (
      <p className="py-8 text-center text-[13px] text-slate-400 dark:text-slate-500">
        No enrolments yet — start a recommended course to begin tracking progress.
      </p>
    );
  }

  return (
    <div className="flex items-center gap-5">
      <div className="relative h-[136px] w-[136px] flex-shrink-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              innerRadius={46}
              outerRadius={66}
              paddingAngle={2}
              stroke="none"
              startAngle={90}
              endAngle={-270}
              isAnimationActive
            >
              {data.map((d) => <Cell key={d.name} fill={d.color} />)}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-[22px] font-bold leading-none text-gov-ink dark:text-white">{overall}%</span>
          <span className="mt-1 text-[10px] font-medium text-slate-400">Overall Progress</span>
        </div>
      </div>

      <ul className="min-w-0 flex-1 space-y-2.5">
        {data.map((d) => (
          <li key={d.name} className="flex items-center gap-2.5 text-[12.5px]">
            <span className="h-2.5 w-2.5 flex-shrink-0 rounded-full" style={{ background: d.color }} aria-hidden="true" />
            <span className="flex-1 truncate text-slate-600 dark:text-slate-300">{d.name}</span>
            <span className="font-semibold tabular-nums text-gov-ink dark:text-white">{d.value}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default LearningSnapshot;
