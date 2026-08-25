/**
 * FILE: src/components/dashboard/SkillGapCard.tsx
 */

import React from 'react';
import { AlertTriangle, CheckCircle2, Lock, ShieldAlert } from 'lucide-react';
import type { SkillGapEntry, CompetencyDomain } from '../../types/domain';

interface SkillGapCardProps { skillGaps: SkillGapEntry[]; }

const DOMAIN_STYLES: Record<CompetencyDomain, { badge: string; pip: string }> = {
  Statistical: { badge: 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 border-blue-200 dark:border-blue-800/50',  pip: 'bg-blue-600 dark:bg-blue-500' },
  Technical:   { badge: 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 border-purple-200 dark:border-purple-800/50', pip: 'bg-purple-600 dark:bg-purple-500' },
  Governance:  { badge: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800/50', pip: 'bg-emerald-600 dark:bg-emerald-500' },
  Leadership:  { badge: 'bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-300 border-amber-200 dark:border-amber-800/50', pip: 'bg-amber-500' },
};

const PipStrip: React.FC<{ current: number; required: number; domain: CompetencyDomain }> = ({ current, required, domain }) => {
  const { pip } = DOMAIN_STYLES[domain] ?? DOMAIN_STYLES.Statistical;
  return (
    <div className="flex items-center gap-1">
      {Array.from({ length: 5 }, (_, i) => {
        const level = i + 1;
        const isFilled = level <= current;
        const isGap = level > current && level <= required;
        return (
          <div key={level} title={`Level ${level}`}
            className={`w-5 h-5 rounded-sm transition-all ${
              isFilled ? `${pip} shadow-sm` : isGap ? 'bg-red-200 dark:bg-red-900/40 border-2 border-red-400 dark:border-red-500/50' : 'bg-slate-200 dark:bg-slate-800 border border-slate-300 dark:border-slate-700'
            }`} />
        );
      })}
      <span className="ml-2 text-xs text-slate-500 font-mono">{current}/{required}</span>
    </div>
  );
};

const GapRow: React.FC<{ entry: SkillGapEntry }> = ({ entry }) => {
  const { competency, currentLevel, requiredLevel, gap, isMandatory, verificationSource } = entry;
  const hasGap = gap > 0;
  const domainStyle = DOMAIN_STYLES[competency.domain] ?? DOMAIN_STYLES.Statistical;

  return (
    <div className={`rounded-xl border p-4 transition-all hover:shadow-md ${hasGap ? 'bg-red-50/60 dark:bg-red-950/20 border-red-200 dark:border-red-900/30' : 'bg-green-50/40 dark:bg-green-950/20 border-green-200 dark:border-green-900/30'}`}>
      <div className="flex flex-wrap items-start justify-between gap-2 mb-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${domainStyle.badge}`}>{competency.domain}</span>
          {isMandatory && <span className="flex items-center gap-1 text-xs bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400 border border-orange-200 dark:border-orange-800/50 px-2.5 py-0.5 rounded-full font-semibold"><Lock size={10} /> Mandatory</span>}
        </div>
        {hasGap ? (
          <span className="flex items-center gap-1 text-xs font-bold bg-red-600 dark:bg-red-700 text-white px-3 py-1 rounded-full shadow-sm"><ShieldAlert size={12} /> Gap: -{gap}</span>
        ) : (
          <span className="flex items-center gap-1 text-xs font-bold bg-green-600 dark:bg-green-700 text-white px-3 py-1 rounded-full shadow-sm"><CheckCircle2 size={12} /> Met</span>
        )}
      </div>
      <p className="text-slate-800 dark:text-slate-200 font-semibold text-sm mb-3 leading-snug">{competency.skillName}</p>
      <div className="mb-3">
        <div className="flex items-center justify-between text-xs text-slate-500 mb-1.5">
          <span>Current Level</span><span>Target Level: {requiredLevel}/5</span>
        </div>
        <PipStrip current={currentLevel} required={requiredLevel} domain={competency.domain} />
      </div>
      <div className="flex items-center gap-1.5 text-xs text-slate-400 dark:text-slate-500 mt-1">
        <CheckCircle2 size={11} /><span>Verified via <span className="font-medium text-slate-600 dark:text-slate-400">{verificationSource}</span></span>
      </div>
    </div>
  );
};

const SkillGapCard: React.FC<SkillGapCardProps> = ({ skillGaps }) => {
  const withGaps = skillGaps.filter(e => e.gap > 0);
  const met = skillGaps.filter(e => e.gap === 0);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden transition-colors">
      <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-gradient-to-r from-slate-50 to-white dark:from-slate-900 dark:to-slate-900">
        <div>
          <h2 className="text-slate-900 dark:text-white font-bold text-lg">Competency &amp; Skill-Gap Analysis</h2>
          <p className="text-slate-500 dark:text-slate-400 text-xs mt-0.5">Computed by SkillGapEngine — benchmarked against Job Role</p>
        </div>
        <div className="flex gap-2">
          <SummaryChip label="Gaps" count={withGaps.length} variant="red" />
          <SummaryChip label="Met" count={met.length} variant="green" />
        </div>
      </div>
      <div className="p-5 space-y-3">
        {withGaps.length > 0 && (
          <><SectionDivider icon={<AlertTriangle size={13} className="text-red-500" />} label="Active Gaps" />{withGaps.map(e => <GapRow key={e.competency.compId} entry={e} />)}</>
        )}
        {met.length > 0 && (
          <><SectionDivider icon={<CheckCircle2 size={13} className="text-green-600" />} label="Competencies Met" />{met.map(e => <GapRow key={e.competency.compId} entry={e} />)}</>
        )}
      </div>
    </div>
  );
};

const SummaryChip: React.FC<{ label: string; count: number; variant: 'red'|'green' }> = ({ label, count, variant }) => {
  const cls = variant === 'red' ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 border-red-200 dark:border-red-800/50' : 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 border-green-200 dark:border-green-800/50';
  return <span className={`text-xs font-bold px-3 py-1 rounded-full border ${cls}`}>{count} {label}</span>;
};

const SectionDivider: React.FC<{ icon: React.ReactNode; label: string }> = ({ icon, label }) => (
  <div className="flex items-center gap-2 py-1">
    {icon}
    <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{label}</span>
    <div className="flex-1 h-px bg-slate-100 dark:bg-slate-800" />
  </div>
);

export default SkillGapCard;
