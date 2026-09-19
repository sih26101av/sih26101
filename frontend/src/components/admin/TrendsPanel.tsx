/**
 * FILE: src/components/admin/TrendsPanel.tsx
 *
 * Workforce trends (GET /api/v1/admin/console/trends). One point per day:
 * stored daily snapshots where they exist, and — for every earlier day —
 * training rates reconstructed from dated iGOT course completions, so the
 * chart has history from day one. Competency levels (share at target, average
 * level) only exist on stored snapshot days and build up from deployment.
 *
 * Charts use one y-scale each: training rates (%), weekly course completions
 * (count) and average FRAC level (0–5).
 */

import React from 'react';
import {
  Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import { Camera, Download } from 'lucide-react';

import SectionCard from '../shell/SectionCard';
import { useTheme } from '../../hooks/useTheme';
import { filterKey, useAsync } from '../../hooks/useAdminData';
import {
  downloadAdminCsv, fetchAdminTrends, recordAdminSnapshot, type AdminFilters, type TrendPoint,
} from '../../services/api';
import { ExportButton } from './AdminFilterBar';

// Validated with the dataviz palette checker (light and dark surfaces), fixed order.
const SERIES_LIGHT = ['#1d4ed8', '#ea580c', '#0d9488'];
const SERIES_DARK = ['#3b82f6', '#ea580c', '#0d9488'];

const RATE_SERIES: { key: keyof TrendPoint; label: string }[] = [
  // Rolling 12-month rate, not the cumulative "ever completed" share (that one saturates at 100%).
  { key: 'trainedLast12mPct', label: 'Trained in last 12 months' },
  { key: 'mandatoryCompletionPct', label: 'Mandatory (ACBP) completion' },
  { key: 'atTargetPct', label: 'Competencies at target (snapshots)' },
];

const RANGES = [30, 90, 365] as const;

const fmtDate = (d: string) => new Date(`${d}T00:00:00`).toLocaleDateString(undefined, { day: 'numeric', month: 'short' });

const TrendsPanel: React.FC<{ filters: AdminFilters; compact?: boolean }> = ({ filters, compact }) => {
  const { theme } = useTheme();
  const dark = theme === 'dark';
  const colors = dark ? SERIES_DARK : SERIES_LIGHT;
  const axis = dark ? '#94a3b8' : '#64748b';
  const grid = dark ? '#334155' : '#e2e8f0';
  const surface = dark ? '#0f172a' : '#fff';
  const [days, setDays] = React.useState<number>(90);
  const [recording, setRecording] = React.useState(false);
  const { data, isLoading, error, refetch } = useAsync(
    () => fetchAdminTrends(filters, days), `${filterKey(filters)}|${days}`,
  );

  const all = data?.points ?? [];
  const points = all.filter((p) => !p.suppressed);
  const suppressed = all.length > 0 && points.length === 0;
  const live = points.filter((p) => !p.reconstructed);
  const weekly = (data?.weeklyCompletions ?? []).filter((w) => w.completions != null);
  const tooltipStyle = { borderRadius: 10, fontSize: 12, border: `1px solid ${grid}`, background: surface };
  const height = compact ? 220 : 260;
  const liveDot = { r: 4, strokeWidth: 2, fill: surface };
  const firstLive = data?.firstLiveSnapshot;
  const showMarker = firstLive && points.length > 0 && firstLive > points[0].date;

  const record = async () => {
    setRecording(true);
    try { await recordAdminSnapshot(); refetch(); } finally { setRecording(false); }
  };

  const tooltipLabel = (d: unknown, payload: readonly { payload?: TrendPoint }[] | undefined) => {
    const p = payload?.[0]?.payload;
    return `${fmtDate(String(d))}${p ? (p.reconstructed ? ' · from course completions' : ' · daily snapshot') : ''}`;
  };

  const empty = (
    <p className="py-12 text-center text-[13px] text-slate-400">
      {isLoading ? 'Loading trends…' : error ? error
        : suppressed ? 'Fewer than 5 officials match these filters — trend suppressed.'
        : 'No officials match these filters.'}
    </p>
  );

  return (
    <SectionCard
      title="Workforce trends"
      subtitle={`Last ${days === 365 ? '12 months' : `${days} days`} · ${data?.scope ? `${data.scope.dimension}: ${data.scope.value}` : 'whole NSO'}`}
      action={
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex rounded-lg border border-gov-line p-0.5 dark:border-slate-600" role="group" aria-label="Time range">
            {RANGES.map((r) => (
              <button
                key={r} type="button" aria-pressed={days === r} onClick={() => setDays(r)}
                className={`rounded-md px-2.5 py-1 text-[11.5px] font-semibold ${days === r
                  ? 'bg-gov-navy text-white dark:bg-sky-500/30' : 'text-slate-500 dark:text-slate-400'}`}
              >
                {r === 365 ? '1y' : `${r}d`}
              </button>
            ))}
          </div>
          {!compact && (
            <>
              <ExportButton label={recording ? 'Recording…' : 'Snapshot now'} icon={Camera} onClick={record} />
              <ExportButton label="CSV" icon={Download} disabled={!points.length}
                            onClick={() => downloadAdminCsv('trends', filters, { days })} />
            </>
          )}
        </div>
      }
    >
      {points.length === 0 ? empty : (
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
          <div className="xl:col-span-2">
            <p className="mb-2 text-[12px] font-semibold text-slate-600 dark:text-slate-300">Training rates (%)</p>
            <div style={{ height }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={points} margin={{ top: 8, right: 12, left: -16, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={grid} />
                  <XAxis dataKey="date" tickFormatter={fmtDate} axisLine={false} tickLine={false}
                         tick={{ fill: axis, fontSize: 11 }} minTickGap={32} />
                  <YAxis domain={[0, 100]} unit="%" axisLine={false} tickLine={false} tick={{ fill: axis, fontSize: 11 }} />
                  <Tooltip contentStyle={tooltipStyle} labelFormatter={tooltipLabel}
                           formatter={(v) => (v == null ? '—' : `${v}%`)} />
                  <Legend iconType="plainline" wrapperStyle={{ fontSize: 11.5, color: axis }} />
                  {showMarker && (
                    <ReferenceLine x={firstLive!} stroke={axis} strokeDasharray="4 4"
                                   label={{ value: 'daily snapshots', position: 'insideTopLeft', fill: axis, fontSize: 10.5 }} />
                  )}
                  {RATE_SERIES.map((s, i) => (
                    <Line key={s.key} type="monotone" dataKey={s.key} name={s.label} stroke={colors[i]}
                          strokeWidth={2} isAnimationActive={false}
                          // Snapshot-only series has a point per live day; always mark them.
                          dot={s.key === 'atTargetPct' || points.length <= 31 ? liveDot : false}
                          activeDot={{ r: 5 }} connectNulls={s.key !== 'atTargetPct' || live.length > 1} />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="space-y-5">
              <div>
                <p className="mb-2 text-[12px] font-semibold text-slate-600 dark:text-slate-300">Course completions per week</p>
                <div style={{ height: live.length > 1 && !compact ? 120 : height }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={weekly} margin={{ top: 4, right: 8, left: -24, bottom: 0 }} barCategoryGap={2}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={grid} />
                      <XAxis dataKey="weekStart" tickFormatter={fmtDate} axisLine={false} tickLine={false}
                             tick={{ fill: axis, fontSize: 11 }} minTickGap={24} />
                      <YAxis allowDecimals={false} axisLine={false} tickLine={false} tick={{ fill: axis, fontSize: 11 }} />
                      <Tooltip contentStyle={tooltipStyle} cursor={{ fill: dark ? '#1e293b' : '#f1f5f9' }}
                               labelFormatter={(d) => `Week of ${fmtDate(String(d))}`}
                               formatter={(v) => [String(v), 'Completions']} />
                      <Bar dataKey="completions" fill={colors[2]} radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
              {compact ? null : live.length > 1 ? (
                <div>
                  <p className="mb-2 text-[12px] font-semibold text-slate-600 dark:text-slate-300">Average competency level (FRAC 0–5)</p>
                  <div style={{ height: 120 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={live} margin={{ top: 4, right: 8, left: -24, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={grid} />
                        <XAxis dataKey="date" tickFormatter={fmtDate} axisLine={false} tickLine={false}
                               tick={{ fill: axis, fontSize: 11 }} minTickGap={24} />
                        <YAxis domain={[0, 5]} axisLine={false} tickLine={false} tick={{ fill: axis, fontSize: 11 }} />
                        <Tooltip contentStyle={tooltipStyle} labelFormatter={(d) => fmtDate(String(d))}
                                 formatter={(v) => [v == null ? '—' : String(v), 'Avg level']} />
                        <Line type="monotone" dataKey="avgLevel" stroke={colors[0]} strokeWidth={2}
                              dot={live.length <= 31 ? liveDot : false} connectNulls isAnimationActive={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              ) : (
                <p className="rounded-xl border border-gov-line px-3.5 py-2.5 text-[12px] text-slate-500 dark:border-slate-700 dark:text-slate-400">
                  Average competency level today:{' '}
                  <span className="font-semibold text-gov-ink dark:text-white">{live[0]?.avgLevel ?? '—'}</span>
                  {' '}— its line starts once a second daily snapshot is recorded.
                </p>
              )}
          </div>
        </div>
      )}
      {data && points.length > 0 && !compact && <p className="mt-3 text-[11px] text-slate-400">{data.note}</p>}
    </SectionCard>
  );
};

export default TrendsPanel;
