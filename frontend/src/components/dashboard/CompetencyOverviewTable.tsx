/**
 * FILE: src/components/dashboard/CompetencyOverviewTable.tsx
 *
 * Compact "Competency & Skill-Gap Analysis" table for the dashboard overview —
 * the scannable summary of the same `SkillGapEntry[]` that SkillGapCard renders
 * in full detail on the Skill-Gap Centre section.
 *
 * All values are derived from the live skill-gap payload; nothing is hardcoded.
 */

import React, { useMemo, useState } from 'react';
import { ArrowRight } from 'lucide-react';
import type { SkillGapEntry, CompetencyDomain } from '../../types/domain';

const MAX_LEVEL = 5;

/** Priority bucket derived from gap size + mandatory flag. */
const priorityOf = (entry: SkillGapEntry) => {
  if (entry.gap <= 0) return { label: 'Met', cls: 'bg-accent-green-soft text-accent-green dark:bg-emerald-500/15 dark:text-emerald-300' };
  if (entry.gap >= 4 || (entry.isMandatory && entry.gap >= 3)) {
    return { label: 'High Priority', cls: 'bg-accent-rose-soft text-accent-rose dark:bg-rose-500/15 dark:text-rose-300' };
  }
  if (entry.gap >= 2) return { label: 'Medium', cls: 'bg-accent-orange-soft text-accent-orange dark:bg-orange-500/15 dark:text-orange-300' };
  return { label: 'Low', cls: 'bg-accent-blue-soft text-accent-blue dark:bg-blue-500/15 dark:text-blue-300' };
};

/** Five boxes; `filled` of them tinted. */
const LevelPips: React.FC<{ level: number; tone: 'current' | 'target' }> = ({ level, tone }) => (
  <span className="inline-flex items-center gap-2">
    <span className="flex gap-[3px]" role="img" aria-label={`Level ${level} of ${MAX_LEVEL}`}>
      {Array.from({ length: MAX_LEVEL }, (_, i) => (
        <span
          key={i}
          className={`h-[11px] w-[11px] rounded-[3px] border ${
            i < level
              ? tone === 'current'
                ? 'border-accent-blue bg-accent-blue'
                : 'border-gov-navy bg-gov-navy dark:border-sky-400 dark:bg-sky-400'
              : 'border-slate-200 bg-slate-50 dark:border-slate-600 dark:bg-slate-700/50'
          }`}
        />
      ))}
    </span>
    <span className="text-[11.5px] font-semibold tabular-nums text-slate-500 dark:text-slate-400">
      {level}/{MAX_LEVEL}
    </span>
  </span>
);

interface Props {
  skillGaps: SkillGapEntry[];
  /** Jumps to the recommendation list filtered by this competency. */
  onFindCourses: (skillName: string) => void;
  /** "View Detailed Analysis →" — opens the Skill-Gap Centre. */
  onViewDetailed: () => void;
  /** How many rows to show before the "show all" toggle. */
  previewCount?: number;
}

const CompetencyOverviewTable: React.FC<Props> = ({
  skillGaps, onFindCourses, onViewDetailed, previewCount = 5,
}) => {
  const [domain, setDomain] = useState<CompetencyDomain | 'all'>('all');
  const [expanded, setExpanded] = useState(false);

  // Domain tabs with live counts, built only from domains actually present.
  const domains = useMemo(() => {
    const counts = new Map<CompetencyDomain, number>();
    skillGaps.forEach((g) => counts.set(g.competency.domain, (counts.get(g.competency.domain) ?? 0) + 1));
    return [...counts.entries()].sort((a, b) => b[1] - a[1]);
  }, [skillGaps]);

  // Worst gaps first, so the first viewport shows what matters.
  const filtered = useMemo(() => {
    const rows = domain === 'all' ? skillGaps : skillGaps.filter((g) => g.competency.domain === domain);
    return [...rows].sort((a, b) => b.gap - a.gap || Number(b.isMandatory) - Number(a.isMandatory));
  }, [skillGaps, domain]);

  const visible = expanded ? filtered : filtered.slice(0, previewCount);

  return (
    <section className="panel">
      <div className="panel-head">
        <div className="min-w-0">
          <h2 className="panel-title">Competency &amp; Skill-Gap Analysis</h2>
          <p className="mt-1 pl-3 text-[12px] text-slate-500 dark:text-slate-400">
            6-term formula: Verified · Documented · Tenure · Education · Seniority · Self-Report
          </p>
        </div>
        <button
          type="button"
          onClick={onViewDetailed}
          className="group inline-flex items-center gap-1.5 rounded-lg px-2 py-1 text-[12.5px] font-semibold text-gov-blue transition-colors hover:text-gov-navy dark:text-sky-400"
        >
          View Detailed Analysis
          <ArrowRight size={14} className="transition-transform group-hover:translate-x-0.5" />
        </button>
      </div>

      {/* Domain filters */}
      <div className="flex flex-wrap gap-2 px-5 pb-4">
        <button
          type="button"
          aria-pressed={domain === 'all'}
          onClick={() => { setDomain('all'); setExpanded(false); }}
          className="chip-filter"
        >
          All ({skillGaps.length})
        </button>
        {domains.map(([d, n]) => (
          <button
            key={d}
            type="button"
            aria-pressed={domain === d}
            onClick={() => { setDomain(d); setExpanded(false); }}
            className="chip-filter"
          >
            {d} ({n})
          </button>
        ))}
      </div>

      {/* Table (scrolls horizontally on small screens) */}
      <div className="overflow-x-auto">
        <table className="gov-table min-w-[660px]">
          <thead>
            <tr>
              <th scope="col">Competency</th>
              <th scope="col">Current Level</th>
              <th scope="col">Target Level</th>
              <th scope="col">Gap</th>
              <th scope="col">Status</th>
              <th scope="col"><span className="sr-only">Find courses</span></th>
            </tr>
          </thead>
          <tbody>
            {visible.map((entry) => {
              const p = priorityOf(entry);
              return (
                <tr key={entry.competency.compId}>
                  <td className="max-w-[230px]">
                    <span className="block font-semibold text-gov-ink dark:text-white">{entry.competency.skillName}</span>
                    <span className="mt-0.5 flex items-center gap-1.5 text-[11px] text-slate-400">
                      {entry.competency.domain}
                      {entry.isMandatory && (
                        <span className="chip bg-gov-saffron/15 !px-1.5 !py-0 text-[10px] text-gov-saffron-deep dark:text-gov-saffron">
                          Mandatory
                        </span>
                      )}
                    </span>
                  </td>
                  <td><LevelPips level={entry.currentLevel} tone="current" /></td>
                  <td><LevelPips level={entry.requiredLevel} tone="target" /></td>
                  <td>
                    <span className={`chip ${entry.gap > 0 ? 'bg-accent-rose-soft text-accent-rose dark:bg-rose-500/15 dark:text-rose-300' : 'bg-accent-green-soft text-accent-green dark:bg-emerald-500/15 dark:text-emerald-300'}`}>
                      {entry.gap}
                    </span>
                  </td>
                  <td><span className={`chip ${p.cls}`}>{p.label}</span></td>
                  <td className="text-right">
                    <button
                      type="button"
                      onClick={() => onFindCourses(entry.competency.skillName)}
                      title={`Find courses for ${entry.competency.skillName}`}
                      aria-label={`Find courses for ${entry.competency.skillName}`}
                      className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-gov-blue/10 hover:text-gov-navy dark:hover:text-white"
                    >
                      <ArrowRight size={16} />
                    </button>
                  </td>
                </tr>
              );
            })}

            {visible.length === 0 && (
              <tr>
                <td colSpan={6} className="py-10 text-center text-slate-400">
                  No competencies assessed in this domain yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {filtered.length > previewCount && (
        <div className="border-t border-gov-line px-5 py-3 text-center dark:border-slate-800">
          <button
            type="button"
            onClick={() => setExpanded((e) => !e)}
            className="text-[12.5px] font-semibold text-gov-blue transition-colors hover:text-gov-navy dark:text-sky-400"
          >
            {expanded ? 'Show less' : `Show all ${filtered.length} competencies`}
          </button>
        </div>
      )}
    </section>
  );
};

export default CompetencyOverviewTable;
