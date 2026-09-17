/**
 * FILE: src/components/dashboard/RecentActivityList.tsx
 *
 * "Recent Activity" feed built from the learner's real achievements
 * (RAG quiz passes + external certifications). No synthetic events.
 */

import React from 'react';
import { Award, FileCheck2 } from 'lucide-react';
import type { Achievement } from '../../types/domain';

/** "2 days ago" / "3 weeks ago" — falls back to the raw date on a bad value. */
const relative = (iso: string): string => {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return iso;
  const days = Math.floor((Date.now() - then) / 86_400_000);
  if (days <= 0) return 'Today';
  if (days === 1) return 'Yesterday';
  if (days < 7) return `${days} days ago`;
  if (days < 30) return `${Math.floor(days / 7)} week${days < 14 ? '' : 's'} ago`;
  return new Date(then).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
};

interface Props { achievements: Achievement[]; limit?: number; }

const RecentActivityList: React.FC<Props> = ({ achievements, limit = 4 }) => {
  const items = [...achievements]
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    .slice(0, limit);

  if (items.length === 0) {
    return (
      <p className="py-8 text-center text-[13px] text-slate-400 dark:text-slate-500">
        No activity yet — pass an assessment or upload a certificate to build your record.
      </p>
    );
  }

  return (
    <ul className="space-y-3">
      {items.map((a) => {
        const isQuiz = a.category === 'RAG Quiz';
        return (
          <li key={a.id} className="flex items-start gap-3">
            <span
              className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg ${
                isQuiz
                  ? 'bg-accent-blue-soft text-accent-blue dark:bg-blue-500/15 dark:text-blue-300'
                  : 'bg-accent-green-soft text-accent-green dark:bg-emerald-500/15 dark:text-emerald-300'
              }`}
            >
              {isQuiz ? <FileCheck2 size={15} aria-hidden="true" /> : <Award size={15} aria-hidden="true" />}
            </span>
            <span className="min-w-0 flex-1 leading-tight">
              <span className="block truncate text-[12.5px] font-semibold text-gov-ink dark:text-white">{a.title}</span>
              <span className="mt-0.5 block text-[11px] text-slate-400">
                {a.category} · Score {a.score}%
              </span>
            </span>
            <span className="flex-shrink-0 whitespace-nowrap text-[11px] text-slate-400">{relative(a.date)}</span>
          </li>
        );
      })}
    </ul>
  );
};

export default RecentActivityList;
