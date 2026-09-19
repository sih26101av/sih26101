/**
 * FILE: src/components/dashboard/RecommendationsPanel.tsx
 *
 * The AI recommendation grid, shared by the dashboard overview (top N) and the
 * full Recommendations section. Owns the "filtered by competency" behaviour that
 * SkillGapCard / CompetencyOverviewTable trigger via `onFindCourses`.
 */

import React, { useEffect, useMemo, useState } from 'react';
import { Sparkles } from 'lucide-react';
import CourseCard from './CourseCard';
import { fetchMyRecommendationVotes, sendRecommendationFeedback } from '../../services/api';
import type { CourseRecommendation, FeedbackEvent } from '../../types/domain';

interface Props {
  recommendations: CourseRecommendation[];
  /** Competency name to filter by; '' shows everything. */
  filter: string;
  onClearFilter: () => void;
  /** Cap the grid (dashboard overview shows a preview). */
  limit?: number;
  /** Tailwind grid classes for the card grid. */
  gridClassName?: string;
}

/** A recommendation matches if the title, bridged competency or a reason mentions the term. */
const matches = (rec: CourseRecommendation, term: string): boolean => {
  const t = term.toLowerCase();
  return (
    rec.course.title.toLowerCase().includes(t) ||
    rec.bridgesGapFor?.skillName?.toLowerCase().includes(t) ||
    rec.matchReasons?.some((m) => m.toLowerCase().includes(t))
  );
};

const RecommendationsPanel: React.FC<Props> = ({
  recommendations, filter, onClearFilter, limit,
  gridClassName = 'grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3',
}) => {
  const sorted = useMemo(
    () => [...recommendations].sort((a, b) => a.priorityRank - b.priorityRank),
    [recommendations],
  );

  // Thumbs state + interaction logging (clicks, enrolments, votes).
  const [votes, setVotes] = useState<Record<string, 'up' | 'down'>>({});
  useEffect(() => {
    let live = true;
    fetchMyRecommendationVotes().then(v => { if (live) setVotes(v); });
    return () => { live = false; };
  }, []);
  const onFeedback = (rec: CourseRecommendation, event: FeedbackEvent) => {
    const id = rec.course.courseId;
    if (event === 'thumbs_up' || event === 'thumbs_down' || event === 'clear_vote') {
      setVotes(v => {                                   // optimistic
        const next = { ...v };
        if (event === 'clear_vote') delete next[id]; else next[id] = event === 'thumbs_up' ? 'up' : 'down';
        return next;
      });
    }
    sendRecommendationFeedback(rec, event, { surface: limit ? 'overview' : 'recommendations' })
      .then(v => { if (v) setVotes(v); });
  };

  const matched = filter ? sorted.filter((r) => matches(r, filter)) : sorted;
  // A filter that matches nothing falls back to the full list rather than an empty grid.
  const fellBack = Boolean(filter) && matched.length === 0 && sorted.length > 0;
  const shown = (fellBack ? sorted : matched).slice(0, limit ?? undefined);

  if (sorted.length === 0) {
    return (
      <p className="py-10 text-center text-[13px] text-slate-400 dark:text-slate-500">
        No recommendations available — all competency requirements are currently met.
      </p>
    );
  }

  return (
    <>
      {filter && (
        <div className="mb-4 flex flex-wrap items-center gap-2">
          <span className="animate-scale-in flex items-center gap-1.5 rounded-full border border-gov-saffron/40 bg-gov-saffron/10 px-3 py-1.5 text-[11.5px] font-semibold text-gov-saffron-deep dark:text-gov-saffron">
            <Sparkles size={12} aria-hidden="true" />
            Filtered: {filter}
            <button
              type="button"
              onClick={onClearFilter}
              className="ml-1 font-bold leading-none hover:text-gov-ink dark:hover:text-white"
              aria-label="Clear competency filter"
            >
              ×
            </button>
          </span>
          {fellBack && (
            <span className="text-[11.5px] text-slate-500 dark:text-slate-400">
              No exact match for “{filter}” — showing the full pathway instead.
            </span>
          )}
        </div>
      )}

      <div className={gridClassName}>
        {shown.map((rec, i) => (
          <div key={rec.course.courseId} className="animate-fade-up" style={{ animationDelay: `${Math.min(i, 8) * 70}ms` }}>
            <CourseCard recommendation={rec} vote={votes[rec.course.courseId]} onFeedback={onFeedback} />
          </div>
        ))}
      </div>
    </>
  );
};

export default RecommendationsPanel;
