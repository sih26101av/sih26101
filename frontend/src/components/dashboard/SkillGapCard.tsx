/**
 * FILE: src/components/dashboard/SkillGapCard.tsx
 */

import React from "react";
import { Target, CheckCircle2, AlertCircle, BookOpen, Route, HelpCircle, Briefcase } from "lucide-react";
import type { SkillGapEntry, CompetencyDomain, LearningPathway, StudyPlan } from "../../types/domain";
import { fetchLearningPathways } from "../../services/api";
import { PathwayLadder, StudyPlanSummary } from "./LearningPathway";

interface SkillGapCardProps {
  skillGaps: SkillGapEntry[];
  onFindCourses?: (skillName: string) => void;
  /** iGOT userId — enables the level-by-level learning paths */
  officialId?: string;
}

const DOMAIN_BADGE: Record<string, string> = {
  Statistical: "bg-[#dbeafe] dark:bg-blue-900/40 text-[#2563eb] dark:text-blue-400 border border-[#bfdbfe] dark:border-blue-800",
  Technical:   "bg-[#f3e8ff] dark:bg-purple-900/40 text-[#7c3aed] dark:text-purple-400 border border-[#e9d5ff] dark:border-purple-800",
  Governance:  "bg-[#dcfce7] dark:bg-green-900/40 text-[#16a34a] dark:text-green-400 border border-[#bbf7d0] dark:border-green-800",
  Leadership:  "bg-[#fef3c7] dark:bg-amber-900/40 text-[#d97706] dark:text-amber-400 border border-[#fde68a] dark:border-amber-800",
  Functional:  "bg-[#dbeafe] dark:bg-blue-900/40 text-[#2563eb] dark:text-blue-400 border border-[#bfdbfe] dark:border-blue-800",
  Domain:      "bg-[#f3e8ff] dark:bg-purple-900/40 text-[#7c3aed] dark:text-purple-400 border border-[#e9d5ff] dark:border-purple-800",
};

const LevelBox: React.FC<{ filled: boolean }> = ({ filled }) => (
  <div
    className={`w-[26px] h-[14px] rounded-sm border border-slate-800 dark:border-slate-500 transition-colors duration-300 ${
      filled ? "bg-[#bfdbfe]" : "bg-[#f8fafc]"
    }`}
  />
);

const PipStrip: React.FC<{ current: number }> = ({ current }) => {
  return (
    <div className="flex items-center gap-1.5 mt-1">
      {Array.from({ length: 5 }, (_, i) => (
        <LevelBox key={i} filled={i < current} />
      ))}
      <span className="ml-1.5 text-[11px] font-bold text-slate-500 dark:text-slate-400">{current}/5</span>
    </div>
  );
};

const TargetRow: React.FC<{ target: number }> = ({ target }) => (
  <div className="flex items-center gap-1.5">
    {Array.from({ length: 5 }, (_, i) => (
      <LevelBox key={i} filled={i < target} />
    ))}
  </div>
);

const ExactGlassGauge: React.FC<{ target: number; domain?: CompetencyDomain }> = ({ target }) => {
  const getSlicePath = (startDeg: number, endDeg: number) => {
    const or = 76, ir = 54, cx = 100, cy = 100;
    const polar = (r: number, deg: number) => {
      const rad = ((deg - 180) * Math.PI) / 180;
      return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
    };
    const p1 = polar(or, startDeg); const p2 = polar(or, endDeg);
    const p3 = polar(ir, endDeg); const p4 = polar(ir, startDeg);
    return `M ${p1.x} ${p1.y} A ${or} ${or} 0 0 1 ${p2.x} ${p2.y} L ${p3.x} ${p3.y} A ${ir} ${ir} 0 0 0 ${p4.x} ${p4.y} Z`;
  };
  
  return (
    <div className="relative w-[180px] h-[90px] flex justify-center items-end">
      <svg width="180" height="90" viewBox="10 10 180 90" className="absolute bottom-0 overflow-visible">
        <g>
          {Array.from({ length: 5 }).map((_, i) => {
            const start = i * 36; const end = start + 36;
            const isFilled = i < target;
            return (
              <path
                key={i}
                d={getSlicePath(start, end)}
                className={`transition-colors duration-300 stroke-slate-400 ${
                  isFilled ? "fill-[#bfdbfe]" : "fill-[#f1f5f9]"
                }`}
                strokeWidth="1.2"
                strokeLinejoin="round"
              />
            );
          })}
        </g>
      </svg>
      <div className="absolute bottom-[2px] text-slate-800 dark:text-slate-200 transition-colors duration-300">
        <Target size={22} strokeWidth={1.5} />
      </div>
    </div>
  );
};

const CONFIDENCE_CONFIG = {
  HIGH:       { label: 'Verified',   bg: 'bg-emerald-100 dark:bg-emerald-900/30', text: 'text-emerald-700 dark:text-emerald-400', dot: 'bg-emerald-500' },
  MEDIUM:     { label: 'Documented', bg: 'bg-amber-100 dark:bg-amber-900/30',   text: 'text-amber-700 dark:text-amber-400',   dot: 'bg-amber-500'   },
  LOW:        { label: 'Inferred',   bg: 'bg-slate-100 dark:bg-slate-700/50',   text: 'text-slate-600 dark:text-slate-400',   dot: 'bg-slate-400'   },
  UNASSESSED: { label: 'No',         bg: 'bg-violet-100 dark:bg-violet-900/30', text: 'text-violet-700 dark:text-violet-300', dot: 'bg-violet-500'  },
};

// SCIL v6 §4 — opportunity to practise at work this cycle (badge + tie-break only).
const OPPORTUNITY_STYLE: Record<string, string> = {
  High:   'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800',
  Medium: 'bg-sky-50 dark:bg-sky-900/20 text-sky-700 dark:text-sky-300 border border-sky-200 dark:border-sky-800',
  Low:    'bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-700',
};

const OpportunityBadge: React.FC<{ opportunity: NonNullable<SkillGapEntry['opportunity']>; hasGap: boolean }> = ({ opportunity, hasGap }) => {
  const { level, share, officeName, cycle, subprocesses } = opportunity;
  const where = subprocesses.length
    ? subprocesses.map(s => `${s.id} ${s.name}`).join(', ')
    : 'none of the GSBPM sub-processes where it is used';
  const title = `${officeName} spends ${(share * 100).toFixed(0)}% of its officer-hours in ${cycle ?? 'this cycle'} on ${where}. ` +
    'Used only to order near-equal study steps; it never hides a gap.';
  return (
    <span title={title} className={`flex items-center gap-1 text-[10px] font-semibold px-2.5 py-0.5 rounded-full ${OPPORTUNITY_STYLE[level]}`}>
      <Briefcase size={10} />
      Opportunity to practise: {level} this cycle{level === 'Low' && hasGap ? ' → queued' : ''}
    </span>
  );
};

// SCIL v6 §3 evidence channels — which ones carry evidence for this competency.
const CHANNEL_LABEL: Record<string, string> = {
  K: 'Knowledge (courses, certificates, quizzes)',
  A: 'Application (auto-graded work sample)',
  U: 'Utility (use at work, confirmed by supervisor)',
  S: 'Supervisor rating (APAR)',
};

const EvidenceCompletenessRow: React.FC<{ entry: SkillGapEntry }> = ({ entry }) => {
  const c = entry.evidenceCompleteness;
  if (!c) return null;
  const all = ['K', 'A', 'U', 'S'] as const;
  return (
    <div
      className="flex flex-wrap items-center gap-1.5 mt-2"
      title={`Channel weights: ${all.map(k => `${k} ${c.weights[k]}`).join(' · ')} — ${c.weightsStatus}.`}
    >
      <span className="text-[10px] text-slate-400 dark:text-slate-500 font-medium">
        Evidence {c.present.length}/4:
      </span>
      {all.map(k => {
        const on = c.present.includes(k);
        return (
          <span
            key={k}
            title={`${CHANNEL_LABEL[k]}: ${on ? `level ${entry.channels?.[k]?.toFixed(1)}` : 'no evidence yet'}`}
            className={`text-[9px] font-bold w-5 h-5 rounded-full flex items-center justify-center border ${on
              ? 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800'
              : 'bg-slate-50 dark:bg-slate-800 text-slate-300 dark:text-slate-600 border-slate-200 dark:border-slate-700'}`}
          >
            {k}
          </span>
        );
      })}
      {(entry.peerFeedback ?? 0) > 0 && (
        <span className="text-[10px] text-slate-400 dark:text-slate-500">
          · {entry.peerFeedback} peer rating{entry.peerFeedback === 1 ? '' : 's'} (context only, not scored)
        </span>
      )}
    </div>
  );
};

const EvidenceBar: React.FC<{ label: string; value: number; max?: number; color: string }> = ({ label, value, max = 5, color }) => {
  const pct = Math.min(100, (value / max) * 100);
  return (
    <div className="flex items-center gap-2 text-[10px]">
      <span className="w-[72px] text-slate-400 dark:text-slate-500 font-medium shrink-0">{label}</span>
      <div className="flex-1 h-[5px] bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all duration-300 ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="w-[24px] text-right text-slate-500 dark:text-slate-400 font-mono">{value.toFixed(1)}</span>
    </div>
  );
};

interface GapRowProps {
  entry: SkillGapEntry;
  onFindCourses?: (skillName: string) => void;
  pathway?: LearningPathway;
  pathwayLoading?: boolean;
}

const GapRow: React.FC<GapRowProps> = ({ entry, onFindCourses, pathway, pathwayLoading }) => {
  const { competency, currentLevel, requiredLevel, gap, isMandatory, confidence, basis, rawScore, evidence } = entry;
  const unassessed = confidence === 'UNASSESSED';
  const hasGap = !unassessed && gap > 0;
  const badge = DOMAIN_BADGE[competency.domain] ?? DOMAIN_BADGE.Statistical;
  const conf = CONFIDENCE_CONFIG[confidence ?? 'LOW'];
  const confLabel = basis === 'self_report' ? 'Self-reported'
    : basis === 'work_sample' ? 'Work-sample'
    : basis === 'applied_at_work' ? 'Applied-at-work'
    : conf.label;
  const [showEvidence, setShowEvidence] = React.useState(false);
  const [showPath, setShowPath] = React.useState(false);
  const pathSteps = pathway?.steps.filter(s => s.kind !== 'bridge').length ?? 0;
  const borderTone = unassessed
    ? 'border-l-violet-400'
    : hasGap ? (isMandatory ? 'border-l-gov-saffron' : 'border-l-red-500') : 'border-l-gov-green';

  return (
    <div className={`relative rounded-xl p-6 mb-4 bg-white dark:bg-slate-800/40 border border-gov-line dark:border-slate-700/50 border-l-4 ${borderTone} shadow-sm hover:shadow-gov overflow-hidden transition-all duration-300`}>
    <div className="flex flex-col md:flex-row justify-between items-center gap-4">

      <div className="flex-1 relative z-10 w-full">
        <div className="flex flex-wrap items-center gap-2 mb-3">
          <span className={`text-[11px] font-bold px-3 py-0.5 rounded-full transition-colors duration-300 ${badge}`}>
            {competency.domain}
          </span>
          {isMandatory && (
            <span className="text-[11px] font-bold px-3 py-0.5 rounded-full bg-[#ffedd5] dark:bg-orange-900/40 text-[#ea580c] dark:text-orange-400 border border-[#fed7aa] dark:border-orange-800 transition-colors duration-300">
              &amp; Mandatory
            </span>
          )}
          {/* Confidence badge */}
          <span className={`flex items-center gap-1.5 text-[10px] font-bold px-2.5 py-0.5 rounded-full ${conf.bg} ${conf.text}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${conf.dot}`} />
            {confLabel} Evidence
          </span>
          {entry.opportunity && <OpportunityBadge opportunity={entry.opportunity} hasGap={hasGap} />}
        </div>

        <h3 className="text-slate-900 dark:text-white font-bold text-[15px] leading-snug mb-1.5 transition-colors duration-300">
          {competency.skillName}
        </h3>
        <p className="text-[11px] text-slate-400 dark:text-slate-500 font-medium mb-1 transition-colors duration-300">Current Level</p>
        {unassessed ? (
          <p className="text-[12px] font-semibold text-violet-700 dark:text-violet-300 mt-1">
            Not yet assessed — no evidence for this competency
          </p>
        ) : (
          <PipStrip current={currentLevel} />
        )}
        {basis === 'self_report' && entry.evidenceLevel != null && (
          <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-1">
            Evidence so far supports Level {entry.evidenceLevel}
          </p>
        )}

        {/* b_k raw score */}
        {rawScore !== undefined && (
          <div className="flex items-center gap-2 mt-2">
            <div className="flex-1 h-[5px] bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden max-w-[140px]">
              <div
                className="h-full rounded-full bg-blue-400 dark:bg-blue-500 transition-all duration-500"
                style={{ width: `${(rawScore / 5) * 100}%` }}
              />
            </div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 font-mono">b_k = {rawScore.toFixed(2)}/5</span>
          </div>
        )}

        <EvidenceCompletenessRow entry={entry} />

        {/* SCIL v6 §2 — belief with dated decay, or the cold-start cohort prior */}
        {entry.proficiency && (
          <p
            className="text-[10px] text-slate-500 dark:text-slate-400 mt-1.5"
            title={`θ ~ N(${entry.proficiency.decayedMu}, ${entry.proficiency.decayedSigma}²). Evidence decays toward the population mean (${entry.proficiency.populationMu}) with a ${entry.proficiency.halfLifeMonths}-month half-life (${entry.proficiency.decayClass} skill).`}
          >
            Estimated now: {entry.proficiency.decayedMu.toFixed(1)}{' '}
            (likely {entry.proficiency.band80[0]}–{entry.proficiency.band80[1]})
            {entry.proficiency.evidenceAgeMonths != null && ` · newest evidence ${Math.round(entry.proficiency.evidenceAgeMonths)} months old`}
            {' · '}expected shortfall {entry.proficiency.expectedShortfall.toFixed(1)} level{entry.proficiency.expectedShortfall === 1 ? '' : 's'}
            {entry.proficiency.refresherRecommended && (
              <span className="ml-1.5 font-semibold text-amber-600 dark:text-amber-400">· refresher suggested</span>
            )}
          </p>
        )}
        {unassessed && entry.coldStartPrior && (
          <p className="text-[10.5px] text-violet-600 dark:text-violet-300 mt-1.5" title={entry.coldStartPrior.reason}>
            Inferred from role — unassessed: about Level {entry.coldStartPrior.mu.toFixed(1)}{' '}
            (likely {entry.coldStartPrior.band80[0]}–{entry.coldStartPrior.band80[1]},{' '}
            {entry.coldStartPrior.source === 'cohort'
              ? `officials in ${entry.coldStartPrior.cluster}`
              : 'all officials — cohort prior not used'}). Not used as your level.
          </p>
        )}

        {/* Evidence breakdown toggle */}
        {evidence && (
          <button
            onClick={() => setShowEvidence(v => !v)}
            className="mt-2 text-[10px] text-blue-500 dark:text-blue-400 font-semibold hover:underline"
          >
            {showEvidence ? '▲ Hide' : '▼ Evidence breakdown'}
          </button>
        )}
        {showEvidence && evidence && (
          <div className="mt-2 space-y-1 pr-4">
            <EvidenceBar label="Verified"    value={evidence.verified}    color="bg-emerald-400 dark:bg-emerald-500" />
            <EvidenceBar label="Documented"  value={evidence.documented}  color="bg-amber-400 dark:bg-amber-500" />
            <EvidenceBar label="Tenure"      value={evidence.tenure}      color="bg-indigo-400 dark:bg-indigo-500" />
            <EvidenceBar label="Education"   value={evidence.education}   color="bg-purple-400 dark:bg-purple-500" />
            <EvidenceBar label="Seniority"   value={evidence.seniority}   color="bg-sky-400 dark:bg-sky-500" />
            <EvidenceBar label="Self-Report" value={evidence.selfReport}  color="bg-rose-400 dark:bg-rose-500" />
            <EvidenceBar label="Work sample" value={evidence.workSample ?? 0} color="bg-teal-400 dark:bg-teal-500" />
            <EvidenceBar label="Used at work" value={evidence.utility ?? 0}  color="bg-lime-400 dark:bg-lime-500" />
            <EvidenceBar label="Supervisor"  value={evidence.supervisor ?? 0} color="bg-orange-400 dark:bg-orange-500" />
            <p className="text-[9.5px] text-slate-400 dark:text-slate-500 pt-1">
              The first six feed the knowledge channel K; K, work sample, use at work and supervisor are fused
              with equal placeholder weights (0.25 each) until an expert AHP elicitation sets them.
              Supervisor ratings are not corrected for rater leniency.
            </p>
          </div>
        )}

        <div className="mt-3 flex flex-wrap gap-2">
          {/* Learning path — step-by-step, lowest level first */}
          {(pathway || pathwayLoading) && (
            <button
              onClick={() => setShowPath(v => !v)}
              disabled={!pathway}
              className="inline-flex items-center gap-1.5 text-[11px] font-bold px-3 py-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-700 hover:bg-indigo-100 dark:hover:bg-indigo-800/40 disabled:opacity-60 transition-all"
            >
              <Route size={12} />
              {!pathway
                ? 'Building learning path…'
                : showPath
                  ? 'Hide learning path'
                  : `View learning path${pathSteps ? ` (${pathSteps} step${pathSteps > 1 ? 's' : ''}${pathway.totalHours ? ` · ${pathway.totalHours}h` : ''})` : ''}`}
            </button>
          )}
          {/* Find Courses button — only shown when there is a gap */}
          {hasGap && onFindCourses && (
            <button
              onClick={() => onFindCourses(competency.skillName)}
              className="inline-flex items-center gap-1.5 text-[11px] font-bold px-3 py-1.5 rounded-lg bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-700 hover:bg-blue-100 dark:hover:bg-blue-800/40 transition-all"
            >
              <BookOpen size={12} />
              Find Courses for this Gap →
            </button>
          )}
        </div>
      </div>

      <div className="flex items-end gap-6 relative z-10">
        <div className="mb-[26px]">
          <TargetRow target={requiredLevel} />
        </div>
        
        <div className="flex flex-col items-center relative">
          <div className="absolute -top-6 right-0">
            {unassessed ? (
              <span className="flex items-center gap-1.5 text-[11px] font-bold bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 px-3 py-1 rounded-full">
                <HelpCircle size={12} /> Unknown
              </span>
            ) : hasGap ? (
              <span className="flex items-center gap-1.5 text-[11px] font-bold bg-[#fee2e2] dark:bg-red-900/30 text-[#ef4444] dark:text-red-400 px-3 py-1 rounded-full transition-colors duration-300">
                <AlertCircle size={12} className="text-[#ef4444] dark:text-red-400" /> Gap -{gap}
              </span>
            ) : (
              <span className="flex items-center gap-1.5 text-[11px] font-bold bg-[#dcfce7] dark:bg-green-900/30 text-[#15803d] dark:text-green-400 px-3 py-1 rounded-full transition-colors duration-300">
                <CheckCircle2 size={12} /> Met
              </span>
            )}
          </div>
          <ExactGlassGauge target={requiredLevel} domain={competency.domain} />
          <p className="text-[12px] text-slate-800 dark:text-slate-300 mt-2 font-bold tracking-wide transition-colors duration-300">
            Target Level: {requiredLevel}/5
          </p>
        </div>
      </div>
    </div>
      {showPath && pathway && <PathwayLadder pathway={pathway} />}
    </div>
  );
};


const SkillGapCard: React.FC<SkillGapCardProps> = ({ skillGaps, onFindCourses, officialId }) => {
  const unassessed = skillGaps.filter(e => e.confidence === 'UNASSESSED');
  const withGaps = skillGaps.filter(e => e.confidence !== 'UNASSESSED' && e.gap > 0);
  const met = skillGaps.filter(e => e.confidence !== 'UNASSESSED' && e.gap === 0);

  // One call returns every competency's path plus the cross-gap study order.
  // Re-fetched when any level changes (quiz passed, course completed) so the
  // path never contradicts the card it sits in.
  const levelSignature = skillGaps.map(g => `${g.competency.compId}:${g.currentLevel}`).join('|');
  const [pathways, setPathways] = React.useState<Record<string, LearningPathway>>({});
  const [plan, setPlan] = React.useState<StudyPlan | null>(null);
  const [pathLoading, setPathLoading] = React.useState(false);
  React.useEffect(() => {
    if (!officialId) return;
    let cancelled = false;
    setPathLoading(true);
    fetchLearningPathways(officialId)
      .then(({ pathways: list, studyPlan }) => {
        if (cancelled) return;
        setPathways(Object.fromEntries(list.map(p => [p.competencyId, p])));
        setPlan(studyPlan);
      })
      .catch(err => console.error('[SkillGapCard] learning pathway', err))
      .finally(() => { if (!cancelled) setPathLoading(false); });
    return () => { cancelled = true; };
  }, [officialId, levelSignature]);

  const row = (e: SkillGapEntry) => (
    <GapRow
      key={e.competency.compId}
      entry={e}
      onFindCourses={onFindCourses}
      pathway={pathways[e.competency.compId]}
      pathwayLoading={pathLoading}
    />
  );

  return (
    <div className="gov-card p-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <h2 className="gov-heading text-[20px]">
            Competency &amp; Skill-Gap Analysis
          </h2>
          <p className="text-slate-500 dark:text-slate-400 text-xs mt-1.5 pl-4">
            6-term formula: Verified · Documented · Tenure · Education · Seniority · Self-Report · level-by-level learning paths
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
          <span className="font-medium">Competency Status:</span>
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-[#fee2e2] dark:bg-red-900/30 text-[#ef4444] dark:text-red-400 transition-colors duration-300">
            {withGaps.length} Active Gaps
          </span>
          <span className="text-slate-300 dark:text-slate-600">|</span>
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-[#dcfce7] dark:bg-green-900/30 text-[#15803d] dark:text-green-400 transition-colors duration-300">
            {met.length} Met
          </span>
          {unassessed.length > 0 && (
            <>
              <span className="text-slate-300 dark:text-slate-600">|</span>
              <span className="text-xs font-bold px-3 py-1 rounded-full bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300">
                {unassessed.length} Unassessed
              </span>
            </>
          )}
        </div>
      </div>

      {plan && <StudyPlanSummary plan={plan} />}

      <div className="px-1">
        {withGaps.length > 0 && (
          <>
            <div className="flex items-center gap-2 py-2 mb-2">
              <AlertCircle size={14} className="text-[#ef4444] dark:text-red-400 transition-colors duration-300" />
              <span className="text-[11px] font-bold text-[#ef4444] dark:text-red-400 uppercase tracking-widest transition-colors duration-300">Active Gaps</span>
            </div>
            {withGaps.map(row)}
          </>
        )}
        {withGaps.length === 0 && unassessed.length === 0 && (
          <p className="text-center py-10 text-slate-400 dark:text-slate-500 text-sm transition-colors duration-300">All competencies are met! 🎉</p>
        )}
        {unassessed.length > 0 && (
          <>
            <div className="flex items-center gap-2 py-2 mb-2 mt-2">
              <HelpCircle size={14} className="text-violet-600 dark:text-violet-400" />
              <span className="text-[11px] font-bold text-violet-700 dark:text-violet-300 uppercase tracking-widest">Not Yet Assessed</span>
            </div>
            {unassessed.map(row)}
          </>
        )}
      </div>
    </div>
  );
};

export default SkillGapCard;