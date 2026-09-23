/**
 * FILE: src/components/dashboard/CourseCard.tsx
 *
 * Displays a single AI-recommended course card with:
 *  - Priority rank badge + source badge
 *  - NSSTA TPAC-vetted shield badge (when isTpac === true)
 *  - MatchScoreBar showing finalScore (real backend value)
 *  - Score breakdown tooltip: Relevance % | Quality %
 *  - Match reason chips (matchReasons[])
 *  - "Mandatory" badge for ACBP courses and a structured "why recommended"
 *    (gap it closes, level step, TPAC / measured-improvement badges)
 *  - Thumbs up / down; title clicks and Enroll are logged as feedback
 *  - Enroll CTA button
 */

import React, { useState } from 'react';
import { Clock, ExternalLink, Sparkles, Target, ShieldCheck, Info, Lock, ThumbsUp, ThumbsDown, TrendingUp, ArrowUpRight } from 'lucide-react';
import type { CourseRecommendation, FeedbackEvent } from '../../types/domain';

interface CourseCardProps {
  recommendation: CourseRecommendation;
  /** The learner's current vote on this course */
  vote?: 'up' | 'down';
  /** Log an interaction (click, enrol, thumbs) — RecommendationsPanel owns the state */
  onFeedback?: (rec: CourseRecommendation, event: FeedbackEvent) => void;
}

const MODALITY_LABEL: Record<string, string> = {
  self_paced: 'Self-paced', classroom: 'Classroom', virtual_lab: 'Virtual lab',
};

const BADGE_STYLE: Record<string, string> = {
  mandatory:            'bg-orange-50 dark:bg-orange-900/20 text-orange-700 dark:text-orange-300 border-orange-300 dark:border-orange-700',
  tpac_verified:        'bg-teal-50 dark:bg-teal-900/20 text-teal-700 dark:text-teal-300 border-teal-300 dark:border-teal-700',
  tpac_inferred:        'bg-teal-50/50 dark:bg-teal-900/10 text-teal-600 dark:text-teal-400 border-teal-200 dark:border-teal-800 border-dashed',
  measured_improvement: 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300 border-emerald-300 dark:border-emerald-700',
  under_review:         'bg-slate-50 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border-slate-300 dark:border-slate-600',
};

const SOURCE_STYLES: Record<string, { badge: string; label: string }> = {
  'iGOT Karmayogi':  { badge: 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-800 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800/50',  label: 'iGOT Karmayogi' },
  NSSTA:             { badge: 'bg-teal-100 dark:bg-teal-900/30 text-teal-800 dark:text-teal-300 border-teal-200 dark:border-teal-800/50',                label: 'NSSTA' },
  'MoSPI Internal':  { badge: 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300 border-orange-200 dark:border-orange-800/50',   label: 'MoSPI Internal' },
};
const getSourceStyle = (s: string) =>
  SOURCE_STYLES[s] ?? { badge: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700', label: s };

// ── Score bar with inline breakdown tooltip ────────────────────────────────────
interface MatchScoreBarProps {
  score:         number;   // finalScore ∈ [0,1]
  relevance:     number;
  quality:       number;
}

// The backend score is now an absolute scale (a course scores the same whatever
// it is shown next to), so the bands mean something fixed: 80+ is a strong match
// for this competency and level, 65+ solid, below that worth a second look.
const MatchScoreBar: React.FC<MatchScoreBarProps> = ({ score, relevance, quality }) => {
  const [showTip, setShowTip] = useState(false);
  const pct     = Math.round(score    * 100);
  const relPct  = Math.round(relevance * 100);
  const qualPct = Math.round(quality   * 100);
  const color   = pct >= 80 ? 'bg-green-500' : pct >= 65 ? 'bg-blue-500' : 'bg-amber-400';

  return (
    <div className="relative">
      <div className="flex items-center gap-2">
        <div className="flex-1 h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${color} transition-all duration-700`}
            style={{ width: `${pct}%` }}
          />
        </div>
        <span className="text-xs font-bold text-slate-600 dark:text-slate-400 w-10 text-right">{pct}%</span>
        {/* Info button to toggle score breakdown */}
        <button
          onClick={() => setShowTip(t => !t)}
          className="text-slate-400 hover:text-blue-500 transition-colors"
          title="Score breakdown"
          aria-label="Show score breakdown"
        >
          <Info size={12} />
        </button>
      </div>

      {/* Score breakdown tooltip */}
      {showTip && (
        <div className="absolute right-0 top-5 z-10 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg px-3 py-2 text-xs whitespace-nowrap">
          <p className="font-semibold text-slate-700 dark:text-slate-200 mb-1">Score Breakdown</p>
          <div className="flex gap-3">
            <span className="text-blue-600 dark:text-blue-400">
              Relevance <span className="font-bold">{relPct}%</span>
            </span>
            <span className="text-green-600 dark:text-green-400">
              Quality <span className="font-bold">{qualPct}%</span>
            </span>
          </div>
          <p className="text-slate-400 mt-1">Final = 60% Relevance + 40% Quality</p>
        </div>
      )}
    </div>
  );
};

// ── Main Card ─────────────────────────────────────────────────────────────────
const CourseCard: React.FC<CourseCardProps> = ({ recommendation, vote, onFeedback }) => {
  const {
    course,
    finalScore,
    relevanceScore,
    qualityScore,
    isTpac,
    bridgesGapFor,
    matchReasons,
    aiMatchTag,
    priorityRank,
    mandatory,
    why,
    modality,
  } = recommendation;

  const sourceStyle = getSourceStyle(course.source);
  const badges = why?.badges ?? [];
  const toggleVote = (dir: 'up' | 'down') =>
    onFeedback?.(recommendation, vote === dir ? 'clear_vote' : dir === 'up' ? 'thumbs_up' : 'thumbs_down');

  return (
    <div className="group relative bg-white dark:bg-slate-900 rounded-xl border border-gov-line dark:border-slate-700/70 shadow-gov hover:shadow-gov-lg hover:-translate-y-1 hover:border-gov-blue/40 dark:hover:border-sky-500/50 transition-all duration-300 flex flex-col h-full overflow-hidden">
      <div className="h-1 w-full bg-gradient-to-r from-gov-saffron via-gov-gold to-gov-green origin-left scale-x-[0.25] group-hover:scale-x-100 transition-transform duration-500" />

      {/* ── Header: rank + source badge + TPAC badge + duration ── */}
      <div className="px-4 pt-4 flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="w-7 h-7 rounded-lg bg-gov-navy dark:bg-sky-700 text-white text-xs font-black flex items-center justify-center flex-shrink-0 shadow-gov transition-transform duration-300 group-hover:scale-110">
            {priorityRank}
          </span>
          <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${sourceStyle.badge}`}>
            {sourceStyle.label}
          </span>
          {mandatory && (
            <span className="flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded-full border bg-orange-50 dark:bg-orange-900/20 text-orange-700 dark:text-orange-300 border-orange-300 dark:border-orange-700">
              <Lock size={11} className="flex-shrink-0" />
              Mandatory
            </span>
          )}
          {/* NSSTA TPAC-vetted badge (the structured "why" badges replace it when present) */}
          {isTpac && !why && (
            <span className="flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full border bg-teal-50 dark:bg-teal-900/20 text-teal-700 dark:text-teal-300 border-teal-300 dark:border-teal-700">
              <ShieldCheck size={11} className="flex-shrink-0" />
              NSSTA Vetted
            </span>
          )}
        </div>
        <span className="flex items-center gap-1 text-xs text-slate-400 dark:text-slate-500 flex-shrink-0">
          <Clock size={11} /> {course.durationHours}h
        </span>
      </div>

      {/* ── Body: title + score bar + competency gap ── */}
      <div className="px-4 py-3 flex-1">
        <h3
          onClick={() => onFeedback?.(recommendation, 'click')}
          className="cursor-pointer text-gov-ink dark:text-slate-100 font-bold text-sm leading-snug mb-1 group-hover:text-gov-blue dark:group-hover:text-sky-300 transition-colors"
        >
          {course.title}
        </h3>
        <p className="text-[10.5px] text-slate-400 dark:text-slate-500 mb-3">
          {modality ? (MODALITY_LABEL[modality] ?? modality) : 'Online'}
          {recommendation.courseLevel ? ` · FRAC Level ${recommendation.courseLevel}` : ''}
        </p>

        {/* Score bar with breakdown */}
        <div className="mb-2">
          <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1">
            <span className="flex items-center gap-1">
              <Sparkles size={11} className="text-blue-500" /> AI Recommendation Score
            </span>
          </div>
          <MatchScoreBar
            score={finalScore ?? recommendation.matchScore}
            relevance={relevanceScore ?? 0}
            quality={qualityScore ?? 0}
          />
          {mandatory && (
            /* A mandatory course is listed first because the ACBP requires it —
               not because it scored highest. Say so, so the rank reads honestly. */
            <p className="mt-1 text-[10px] text-slate-400 dark:text-slate-500">
              Listed first because your ACBP requires it, not because of this score.
            </p>
          )}
        </div>

        {/* Gap link */}
        <div className="flex items-start gap-1.5 text-xs text-slate-500 dark:text-slate-400 mt-2">
          <Target size={12} className="mt-0.5 flex-shrink-0 text-blue-500" />
          <span>
            Addresses gap in{' '}
            <span className="font-semibold text-slate-700 dark:text-slate-300">
              {bridgesGapFor.skillName}
            </span>
          </span>
        </div>
      </div>

      {/* ── Match reason + reason chips ── */}
      <div className="mx-4 mb-3">
        <div className="bg-gov-paper dark:bg-slate-800/60 border-l-[3px] border-gov-saffron rounded-md px-3 py-2">
          <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
            <span className="font-semibold">Why recommended? </span>
            {why?.summary || aiMatchTag || matchReasons?.[0] || 'Matched by FRAC competency tag.'}
          </p>
          {why?.gap && why.levelStep.to != null && (
            <p className="mt-1 flex items-center gap-1 text-[10.5px] text-slate-500 dark:text-slate-400">
              <TrendingUp size={11} className="text-indigo-500" />
              Level {why.levelStep.from} <ArrowUpRight size={10} /> {why.levelStep.to}
              <span className="text-slate-400"> · target {why.gap.targetLevel}</span>
            </p>
          )}
          {badges.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1.5">
              {badges.map(b => (
                <span key={b.key} className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full border ${BADGE_STYLE[b.key] ?? BADGE_STYLE.under_review}`}>
                  {b.key === 'tpac_verified' && <ShieldCheck size={10} className="inline -mt-px mr-0.5" />}
                  {b.label}
                </span>
              ))}
            </div>
          )}
          {/* Extra reason chips (legacy — only when there is no structured "why") */}
          {!why && matchReasons && matchReasons.length > 1 && (
            <div className="flex flex-wrap gap-1 mt-1.5">
              {matchReasons.slice(1).map((reason, i) => (
                <span
                  key={i}
                  className="text-[10px] px-1.5 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800"
                >
                  {reason}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ── CTA ── */}
      <div className="px-4 pb-4 flex items-center gap-2">
        <button className="gov-btn-primary flex-1" onClick={() => onFeedback?.(recommendation, 'enrol')}>
          <ExternalLink size={14} className="group-hover:translate-x-0.5 transition-transform" />
          {course.source === 'iGOT Karmayogi' ? 'Enroll on iGOT' : 'Enroll Now'}
        </button>
        {onFeedback && (
          <>
            <button
              onClick={() => toggleVote('up')}
              aria-pressed={vote === 'up'}
              aria-label="Useful recommendation"
              title="Useful recommendation"
              className={`p-2 rounded-lg border transition-colors ${vote === 'up'
                ? 'bg-emerald-50 dark:bg-emerald-900/30 border-emerald-300 text-emerald-600'
                : 'border-slate-200 dark:border-slate-700 text-slate-400 hover:text-emerald-600'}`}
            >
              <ThumbsUp size={14} />
            </button>
            <button
              onClick={() => toggleVote('down')}
              aria-pressed={vote === 'down'}
              aria-label="Not useful"
              title={mandatory ? 'Not useful (mandatory courses stay in your plan)' : "Not useful — don't recommend this again"}
              className={`p-2 rounded-lg border transition-colors ${vote === 'down'
                ? 'bg-rose-50 dark:bg-rose-900/30 border-rose-300 text-rose-600'
                : 'border-slate-200 dark:border-slate-700 text-slate-400 hover:text-rose-600'}`}
            >
              <ThumbsDown size={14} />
            </button>
          </>
        )}
      </div>
      {vote === 'down' && !mandatory && (
        <p className="px-4 pb-3 -mt-2 text-[10.5px] text-rose-600 dark:text-rose-400">
          Thanks — this course won’t be recommended to you again.
        </p>
      )}
    </div>
  );
};

export default CourseCard;
