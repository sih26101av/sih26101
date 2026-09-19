/**
 * FILE: src/components/admin/EmergingSkills.tsx
 *
 * "What should NSSTA train next year?" — GET /api/v1/admin/console/emerging-skills.
 * Per FRAC competency: officials whose role requires it, supply today, and the
 * expected supply in 36 months (retirement + attrition + dated skill decay, no
 * new learning), ranked by the 36-month shortfall weighted for GSBPM scope and
 * product criticality. Synthetic data; counts of 1–4 are suppressed.
 */

import React from 'react';
import {
  Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import { Download, FileText, GraduationCap, TrendingUp } from 'lucide-react';

import SectionCard from '../shell/SectionCard';
import { useTheme } from '../../hooks/useTheme';
import { filterKey, useAsync } from '../../hooks/useAdminData';
import { downloadAdminCsv, fetchEmergingSkills, type AdminFilters, type CountCell, type EmergingSkill } from '../../services/api';
import { ExportButton } from './AdminFilterBar';
import { printReport } from './adminReport';

const SERIES_LIGHT = ['#1d4ed8', '#ea580c', '#0d9488'];
const SERIES_DARK = ['#3b82f6', '#ea580c', '#0d9488'];

const Cell: React.FC<{ c: CountCell }> = ({ c }) => (
  <span className={c.suppressed ? 'text-slate-400' : 'tabular-nums'} title={c.suppressed ? 'Suppressed: 1–4 officials' : undefined}>
    {c.display}
  </span>
);

const short = (s: string) => (s.length > 26 ? `${s.slice(0, 25)}…` : s);

const EmergingSkills: React.FC<{ filters: AdminFilters; filterText: string }> = ({ filters, filterText }) => {
  const { theme } = useTheme();
  const dark = theme === 'dark';
  const colors = dark ? SERIES_DARK : SERIES_LIGHT;
  const axis = dark ? '#94a3b8' : '#64748b';
  const grid = dark ? '#334155' : '#e2e8f0';
  const [onlyShortlist, setOnlyShortlist] = React.useState(false);
  const { data, isLoading, error } = useAsync(() => fetchEmergingSkills(filters), filterKey(filters));

  const items = data?.items ?? [];
  const shortlist = items.filter((i) => i.trainNextYear);
  const table = onlyShortlist ? shortlist : items;
  const chartData = shortlist.map((i) => ({
    name: short(i.competencyName), full: i.competencyName,
    required: i.required.value, supplyNow: i.supplyNow.value, expected36: i.expectedSupply36.value,
  }));

  const exportPdf = () => {
    if (!data) return;
    printReport('Emerging skills — NSSTA training priorities', filterText, [
      {
        heading: `Train next year (top ${shortlist.length})`,
        note: data.method,
        columns: ['#', 'Competency', 'Required', 'Supply now', 'Expected in 36 m', 'Shortfall 36 m', 'Action'],
        rows: shortlist.map((i) => [i.rank, i.competencyName, i.required.display, i.supplyNow.display,
          i.expectedSupply36.display, i.shortfall36.display, i.recommendedAction]),
      },
      {
        heading: 'All competencies',
        columns: ['#', 'Competency', 'Required', 'Supply now', 'Shortfall now', 'Shortfall 36 m', 'Rising', 'GSBPM scope', 'Critical', 'Priority'],
        rows: items.map((i) => [i.rank, i.competencyName, i.required.display, i.supplyNow.display, i.shortfallNow.display,
          i.shortfall36.display, i.rising ? 'yes' : '', i.inScope ? 'yes' : '', i.critical ? 'yes' : '', i.priorityScore]),
      },
    ]);
  };

  return (
    <div className="animate-fade-up space-y-5">
      <SectionCard
        title="Train next year"
        subtitle={data ? `${shortlist.length} priorities over ${data.officials} officials · ${data.horizonMonths}-month horizon` : 'Required vs supply vs forecast'}
        action={
          <div className="flex gap-2">
            <ExportButton label="CSV" icon={Download} disabled={!items.length} onClick={() => downloadAdminCsv('emerging-skills', filters)} />
            <ExportButton label="PDF" icon={FileText} disabled={!items.length} onClick={exportPdf} />
          </div>
        }
      >
        {isLoading && <p className="py-10 text-center text-[12.5px] text-slate-400">Computing forecast…</p>}
        {error && <p className="py-10 text-center text-[12.5px] text-rose-600 dark:text-rose-400">{error}</p>}
        {data && shortlist.length === 0 && (
          <p className="py-10 text-center text-[12.5px] text-slate-400">No competency is forecast to fall short for these officials.</p>
        )}
        {shortlist.length > 0 && (
          <>
            <ol className="mb-5 grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
              {shortlist.slice(0, 6).map((i) => (
                <li key={i.competencyId} className="rounded-xl border border-gov-line p-3.5 dark:border-slate-700">
                  <div className="flex items-start gap-2">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-gov-navy text-[11px] font-bold text-white dark:bg-sky-500/30">
                      {i.rank}
                    </span>
                    <span className="min-w-0">
                      <span className="block text-[13px] font-semibold text-gov-ink dark:text-white">{i.competencyName}</span>
                      <span className="mt-0.5 block text-[11.5px] text-slate-500 dark:text-slate-400">
                        Short by <Cell c={i.shortfall36} /> in 36 m (today <Cell c={i.shortfallNow} />) of <Cell c={i.required} /> required
                      </span>
                    </span>
                  </div>
                  <p className="mt-2 flex items-start gap-1.5 text-[11.5px] text-slate-600 dark:text-slate-300">
                    <GraduationCap size={13} className="mt-0.5 shrink-0" aria-hidden="true" /> {i.recommendedAction}
                  </p>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {i.rising && <span className="chip bg-accent-rose-soft text-accent-rose dark:bg-rose-500/15 dark:text-rose-300"><TrendingUp size={11} /> Rising gap</span>}
                    {i.inScope && <span className="chip bg-accent-blue-soft text-accent-blue dark:bg-blue-500/15 dark:text-blue-300">GSBPM core</span>}
                    {i.critical && <span className="chip bg-accent-purple-soft text-accent-purple dark:bg-violet-500/15 dark:text-violet-300">Product-critical</span>}
                  </div>
                </li>
              ))}
            </ol>

            <p className="mb-2 text-[12px] font-semibold text-slate-600 dark:text-slate-300">Officials: required vs supply today vs expected in 36 months</p>
            <div style={{ height: Math.max(240, chartData.length * 44) }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical" margin={{ top: 4, right: 16, left: 8, bottom: 4 }} barGap={2}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke={grid} />
                  <XAxis type="number" axisLine={false} tickLine={false} tick={{ fill: axis, fontSize: 11 }} allowDecimals={false} />
                  <YAxis type="category" dataKey="name" width={170} axisLine={false} tickLine={false} tick={{ fill: axis, fontSize: 11 }} />
                  <Tooltip
                    cursor={{ fill: dark ? '#1e293b' : '#f1f5f9' }}
                    labelFormatter={(_l, p) => (p?.[0]?.payload?.full ?? '') as string}
                    formatter={(v) => (v == null ? '<5 (suppressed)' : String(v))}
                    contentStyle={{ borderRadius: 10, fontSize: 12, border: `1px solid ${grid}`, background: dark ? '#0f172a' : '#fff' }}
                  />
                  <Legend wrapperStyle={{ fontSize: 11.5, color: axis }} />
                  <Bar dataKey="required" name="Required" fill={colors[0]} radius={[0, 4, 4, 0]} barSize={9} />
                  <Bar dataKey="supplyNow" name="Supply today" fill={colors[1]} radius={[0, 4, 4, 0]} barSize={9} />
                  <Bar dataKey="expected36" name="Expected in 36 m" fill={colors[2]} radius={[0, 4, 4, 0]} barSize={9} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        )}
      </SectionCard>

      <SectionCard
        title="All competencies"
        subtitle="Ranked by priority = 36-month shortfall × 1.25 if GSBPM core × 1.25 if product-critical"
        padded={false}
        action={
          <label className="flex items-center gap-2 text-[12px] text-slate-600 dark:text-slate-300">
            <input type="checkbox" checked={onlyShortlist} onChange={(e) => setOnlyShortlist(e.target.checked)} />
            Shortlist only
          </label>
        }
      >
        <div className="overflow-x-auto">
          <table className="gov-table min-w-[980px]">
            <thead>
              <tr>
                <th scope="col">#</th>
                <th scope="col">Competency</th>
                <th scope="col">Required</th>
                <th scope="col">Supply today</th>
                <th scope="col">Expected 36 m</th>
                <th scope="col">Shortfall now → 36 m</th>
                <th scope="col">Catalogue gaps</th>
                <th scope="col">Priority</th>
                <th scope="col">Recommended action</th>
              </tr>
            </thead>
            <tbody>
              {table.map((i: EmergingSkill) => (
                <tr key={i.competencyId}>
                  <td className="tabular-nums text-slate-500">{i.rank}</td>
                  <td>
                    <span className="block font-semibold text-gov-ink dark:text-white">{i.competencyName}</span>
                    <span className="text-[11px] text-slate-400">
                      Target ≈ L{i.avgTargetLevel}{i.inScope ? ' · GSBPM core' : ''}{i.critical ? ' · product-critical' : ''}
                    </span>
                  </td>
                  <td><Cell c={i.required} /></td>
                  <td><Cell c={i.supplyNow} />{i.coveragePct != null && <span className="text-[11px] text-slate-400"> ({i.coveragePct}%)</span>}</td>
                  <td><Cell c={i.expectedSupply36} />{i.coverage36Pct != null && <span className="text-[11px] text-slate-400"> ({i.coverage36Pct}%)</span>}</td>
                  <td>
                    <Cell c={i.shortfallNow} /> → <Cell c={i.shortfall36} />
                    {i.rising && <span className="ml-1 text-[11px] font-semibold text-accent-rose">▲ rising</span>}
                  </td>
                  <td className="text-[12px]">
                    {i.missingCatalogueLevels.length ? `No course at L${i.missingCatalogueLevels.join(', L')}` : '—'}
                    {i.flaggedCourses > 0 && <span className="block text-[11px] text-accent-orange">{i.flaggedCourses} low-uplift course(s)</span>}
                  </td>
                  <td className="tabular-nums font-semibold">
                    {i.priorityScore}
                    {i.trainNextYear && <span className="ml-1.5 chip bg-gov-navy/10 text-gov-navy dark:bg-sky-500/15 dark:text-sky-300">Next year</span>}
                  </td>
                  <td className="max-w-xs text-[12px] text-slate-600 dark:text-slate-300">{i.recommendedAction}</td>
                </tr>
              ))}
              {data && table.length === 0 && (
                <tr><td colSpan={9} className="py-10 text-center text-slate-400">No competencies for these filters.</td></tr>
              )}
            </tbody>
          </table>
        </div>
        {data && (
          <div className="space-y-1 border-t border-gov-line px-5 py-3 text-[11px] text-slate-400 dark:border-slate-800">
            <p>{data.method}</p>
            <p>{data.suppression}</p>
          </div>
        )}
      </SectionCard>
    </div>
  );
};

export default EmergingSkills;
