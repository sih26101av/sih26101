/**
 * FILE: src/components/dashboard/SkillGapCard.tsx
 */

import React from "react";
import { Target, CheckCircle2, Shield, Users, Lightbulb, LucideIcon, Hexagon, AlertCircle } from "lucide-react";
import type { SkillGapEntry, CompetencyDomain } from "../../types/domain";

interface SkillGapCardProps { skillGaps: SkillGapEntry[]; }

const DOMAIN_ICONS: Record<CompetencyDomain, LucideIcon> = {
  Statistical: Users,
  Governance: Shield,
  Technical: Lightbulb,
  Leadership: Target,
};

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

const ExactGlassGauge: React.FC<{ target: number; domain: CompetencyDomain }> = ({ target, domain }) => {
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

const GapRow: React.FC<{ entry: SkillGapEntry }> = ({ entry }) => {
  const { competency, currentLevel, requiredLevel, gap, isMandatory, verificationSource } = entry;
  const hasGap = gap > 0;
  const badge = DOMAIN_BADGE[competency.domain] ?? DOMAIN_BADGE.Statistical;

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
        </div>

        <h3 className="text-slate-900 dark:text-white font-bold text-[15px] leading-snug mb-1.5 transition-colors duration-300">
          {competency.skillName}
        </h3>
        <p className="text-[11px] text-slate-400 dark:text-slate-500 font-medium mb-1 transition-colors duration-300">Current Level</p>
        <PipStrip current={currentLevel} />
        <div className="flex items-center gap-1.5 text-[11px] text-emerald-600 dark:text-emerald-400 mt-2 font-medium transition-colors duration-300">
          <CheckCircle2 size={12} className="text-emerald-500 dark:text-emerald-400" />
          <span>Verified via {verificationSource}</span>
        </div>
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

const SkillGapCard: React.FC<SkillGapCardProps> = ({ skillGaps }) => {
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
            Computed by SkillGapEngine — benchmarked against Job Role
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
            {withGaps.map(e => <GapRow key={e.competency.compId} entry={e} />)}
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