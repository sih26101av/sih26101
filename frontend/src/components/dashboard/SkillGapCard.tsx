/**
 * FILE: src/components/dashboard/SkillGapCard.tsx
 */

import React from "react";
import { Target, CheckCircle2, AlertCircle, BookOpen } from "lucide-react";
import type { SkillGapEntry, CompetencyDomain } from "../../types/domain";

interface SkillGapCardProps {
  skillGaps: SkillGapEntry[];
  onFindCourses?: (skillName: string) => void;
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
  HIGH:   { label: 'Verified',   bg: 'bg-emerald-100 dark:bg-emerald-900/30', text: 'text-emerald-700 dark:text-emerald-400', dot: 'bg-emerald-500' },
  MEDIUM: { label: 'Documented', bg: 'bg-amber-100 dark:bg-amber-900/30',   text: 'text-amber-700 dark:text-amber-400',   dot: 'bg-amber-500'   },
  LOW:    { label: 'Inferred',   bg: 'bg-slate-100 dark:bg-slate-700/50',   text: 'text-slate-600 dark:text-slate-400',   dot: 'bg-slate-400'   },
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

const GapRow: React.FC<{ entry: SkillGapEntry; onFindCourses?: (skillName: string) => void }> = ({ entry, onFindCourses }) => {
  const { competency, currentLevel, requiredLevel, gap, isMandatory, confidence, rawScore, evidence } = entry;
  const hasGap = gap > 0;
  const badge = DOMAIN_BADGE[competency.domain] ?? DOMAIN_BADGE.Statistical;
  const conf = CONFIDENCE_CONFIG[confidence ?? 'LOW'];
  const [showEvidence, setShowEvidence] = React.useState(false);

  return (
    <div className="relative rounded-xl p-6 mb-4 bg-white dark:bg-slate-800/40 border border-slate-800 dark:border-slate-700/50 shadow-sm overflow-hidden flex flex-col md:flex-row justify-between items-center gap-4 transition-colors duration-300">

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
            {conf.label} Evidence
          </span>
        </div>

        <h3 className="text-slate-900 dark:text-white font-bold text-[15px] leading-snug mb-1.5 transition-colors duration-300">
          {competency.skillName}
        </h3>
        <p className="text-[11px] text-slate-400 dark:text-slate-500 font-medium mb-1 transition-colors duration-300">Current Level</p>
        <PipStrip current={currentLevel} />

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
          </div>
        )}

        {/* Find Courses button — only shown when there is a gap */}
        {hasGap && onFindCourses && (
          <button
            onClick={() => onFindCourses(competency.skillName)}
            className="mt-3 inline-flex items-center gap-1.5 text-[11px] font-bold px-3 py-1.5 rounded-lg bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-700 hover:bg-blue-100 dark:hover:bg-blue-800/40 transition-all"
          >
            <BookOpen size={12} />
            Find Courses for this Gap →
          </button>
        )}
      </div>

      <div className="flex items-end gap-6 relative z-10">
        <div className="mb-[26px]">
          <TargetRow target={requiredLevel} />
        </div>
        
        <div className="flex flex-col items-center relative">
          <div className="absolute -top-6 right-0">
            {hasGap ? (
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
  );
};


const SkillGapCard: React.FC<SkillGapCardProps> = ({ skillGaps, onFindCourses }) => {
  const withGaps = skillGaps.filter(e => e.gap > 0);
  const met = skillGaps.filter(e => e.gap === 0);

  return (
    <div className="bg-white dark:bg-slate-800/40 rounded-2xl border border-slate-200 dark:border-slate-700/50 shadow-sm p-6 transition-colors duration-300">
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <h2 className="text-slate-900 dark:text-white font-bold text-lg tracking-tight transition-colors duration-300">
            Competency &amp; Skill-Gap Analysis
          </h2>
          <p className="text-slate-500 dark:text-slate-400 text-xs mt-1 transition-colors duration-300">
            6-term formula: Verified · Documented · Tenure · Education · Seniority · Self-Report
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
        </div>
      </div>
      
      <div className="px-1">
        {withGaps.length > 0 && (
          <>
            <div className="flex items-center gap-2 py-2 mb-2">
              <AlertCircle size={14} className="text-[#ef4444] dark:text-red-400 transition-colors duration-300" />
              <span className="text-[11px] font-bold text-[#ef4444] dark:text-red-400 uppercase tracking-widest transition-colors duration-300">Active Gaps</span>
            </div>
            {withGaps.map(e => <GapRow key={e.competency.compId} entry={e} onFindCourses={onFindCourses} />)}
          </>
        )}
        {withGaps.length === 0 && (
          <p className="text-center py-10 text-slate-400 dark:text-slate-500 text-sm transition-colors duration-300">All competencies are met! 🎉</p>
        )}
      </div>
    </div>
  );
};

export default SkillGapCard;