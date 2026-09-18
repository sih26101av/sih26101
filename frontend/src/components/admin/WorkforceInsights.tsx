/**
 * FILE: src/components/admin/WorkforceInsights.tsx
 *
 * Admin "Insights" tab — SCIL v6 workforce views. Every panel reads one
 * admin-only backend endpoint; every number is computed by backend code over
 * SYNTHETIC mock data, which the page says up front.
 */

import React from 'react';
import { AlertTriangle, FlaskConical, GitBranch, Layers, Route, Telescope } from 'lucide-react';

import SectionCard from '../shell/SectionCard';
import {
  fetchCapabilityRisk, fetchForesight, fetchGsbpmScope, fetchPrerequisiteDag, fetchTpacAgenda,
  fetchTrainingEffectiveness,
  type CapabilityRiskReport, type CountCell, type ForesightReport, type GsbpmScopeReport,
  type PrerequisiteDagReport, type RiskBand, type TpacAgenda, type TrainingEffectivenessReport,
} from '../../services/api';

// ─── Small shared helpers ─────────────────────────────────────────────────────

export function useInsight<T>(load: () => Promise<T>, deps: React.DependencyList) {
  const [data, setData] = React.useState<T | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(true);
  React.useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    load()
      .then((d) => { if (!cancelled) setData(d); })
      .catch((e: Error) => { if (!cancelled) setError(e.message); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  return { data, error, loading };
}

export const PanelState: React.FC<{ loading: boolean; error: string | null; empty?: boolean }> = ({
  loading, error, empty,
}) => {
  if (loading) return <p className="py-8 text-center text-[12.5px] text-slate-400">Loading…</p>;
  if (error) {
    return (
      <p className="flex items-center justify-center gap-2 py-8 text-[12.5px] text-rose-600 dark:text-rose-400">
        <AlertTriangle size={14} /> {error}
      </p>
    );
  }
  if (empty) return <p className="py-8 text-center text-[12.5px] text-slate-400">No data.</p>;
  return null;
};

const pct = (x: number, digits = 0) => `${(x * 100).toFixed(digits)}%`;

// ─── GSBPM 80% officer-hours scoping (SCIL v6 §1) ─────────────────────────────

const GsbpmScopePanel: React.FC = () => {
  const [officeId, setOfficeId] = React.useState<string>('');
  const [showOut, setShowOut] = React.useState(false);
  const { data, error, loading } = useInsight<GsbpmScopeReport>(
    () => fetchGsbpmScope(officeId || undefined), [officeId],
  );

  const comps = data ? data.competencies.filter((c) => c.inScope || showOut) : [];

  return (
    <SectionCard
      title="GSBPM scope — 80% officer-hours rule"
      subtitle="Which competencies matter, from the GSBPM sub-processes that take 80% of officer-hours this cycle"
      action={
        <select
          value={officeId}
          onChange={(e) => setOfficeId(e.target.value)}
          className="rounded-lg border border-gov-line bg-white px-2.5 py-1.5 text-[12px] text-slate-700 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        >
          <option value="">Whole NSO</option>
          {data?.offices.map((o) => <option key={o.officeId} value={o.officeId}>{o.name}</option>)}
        </select>
      }
    >
      <PanelState loading={loading && !data} error={error} />
      {data && (
        <div className="space-y-4">
          <p className="text-[12.5px] text-slate-600 dark:text-slate-300">
            <span className="font-semibold">{data.coreSubprocesses.length} core sub-processes</span> cover{' '}
            {pct(data.coreShare, 1)} of {data.totalOfficerHours.toLocaleString('en-IN')} officer-hours
            ({data.cycle.label ?? 'this cycle'}) →{' '}
            <span className="font-semibold text-emerald-700 dark:text-emerald-400">{data.inScopeCount} competencies in scope</span>,{' '}
            <span className="font-semibold text-slate-500">{data.outOfScopeCount} out</span>.
          </p>

          <div className="grid grid-cols-1 gap-1.5 md:grid-cols-2">
            {data.coreSubprocesses.map((s) => (
              <div key={s.id} className="flex items-center gap-2 text-[11.5px]">
                <span className="w-12 shrink-0 font-mono text-slate-500">{s.id}</span>
                <span className="w-44 shrink-0 truncate text-slate-700 dark:text-slate-200" title={s.name}>{s.name}</span>
                <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
                  <div className="h-full rounded-full bg-gov-blue" style={{ width: pct(Math.min(1, s.share / (data.coreSubprocesses[0]?.share || 1))) }} />
                </div>
                <span className="w-10 shrink-0 text-right font-mono text-slate-500">{pct(s.share)}</span>
              </div>
            ))}
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-[12px]">
              <thead>
                <tr className="border-b border-gov-line text-[11px] uppercase tracking-wide text-slate-400 dark:border-slate-700">
                  <th className="py-2 pr-3 font-semibold">Competency</th>
                  <th className="py-2 pr-3 font-semibold">Scope</th>
                  <th className="py-2 pr-3 font-semibold">Hours share</th>
                  <th className="py-2 font-semibold">Why</th>
                </tr>
              </thead>
              <tbody>
                {comps.map((c) => (
                  <tr key={c.competencyId} className="border-b border-gov-line/60 align-top dark:border-slate-700/60">
                    <td className="py-2 pr-3 font-medium text-slate-800 dark:text-slate-100">{c.competencyName}</td>
                    <td className="py-2 pr-3">
                      <span className={`rounded-full px-2 py-0.5 text-[10.5px] font-bold ${c.inScope
                        ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300'
                        : 'bg-slate-100 text-slate-500 dark:bg-slate-700/60 dark:text-slate-400'}`}>
                        {c.inScope ? 'In scope' : 'Out'}
                      </span>
                    </td>
                    <td className="py-2 pr-3 font-mono text-slate-600 dark:text-slate-300">{pct(c.share, 1)}</td>
                    <td className="py-2 text-[11.5px] text-slate-500 dark:text-slate-400">{c.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <button
            type="button"
            onClick={() => setShowOut((v) => !v)}
            className="text-[11.5px] font-semibold text-gov-blue hover:underline"
          >
            {showOut ? 'Hide' : 'Show'} the {data.outOfScopeCount} out-of-scope competencies
          </button>
          <p className="text-[10.5px] text-slate-400">{data.method}</p>
        </div>
      )}
    </SectionCard>
  );
};

// ─── Prerequisite DAG + data-driven suggestions (SCIL v6 §5) ─────────────────

const PrerequisitePanel: React.FC = () => {
  const { data, error, loading } = useInsight<PrerequisiteDagReport>(fetchPrerequisiteDag, []);
  const inf = data?.inference;
  return (
    <SectionCard
      title="Prerequisite DAG"
      subtitle="Expert-seeded edges the study plan enforces, and edges suggested by outcome data for review"
    >
      <PanelState loading={loading} error={error} />
      {data && (
        <div className="space-y-4">
          <p className="flex items-center gap-2 text-[12.5px] text-slate-600 dark:text-slate-300">
            {data.validation.rejected ? (
              <span className="font-semibold text-rose-600 dark:text-rose-400">
                Cycle found — all {data.validation.received} edges rejected: {data.validation.cycle?.join(' → ')}
              </span>
            ) : (
              <span>
                <span className="font-semibold">{data.edges.length} expert edges</span> — acyclic with the level
                ladders, enforced in every study plan.
              </span>
            )}
          </p>
          <div className="max-h-64 overflow-y-auto">
            <table className="w-full text-left text-[12px]">
              <tbody>
                {data.edges.map((e) => (
                  <tr key={e.id} className="border-b border-gov-line/60 align-top dark:border-slate-700/60">
                    <td className="py-1.5 pr-3 font-medium text-slate-800 dark:text-slate-100">
                      {e.fromName} <span className="font-mono text-slate-400">L{e.from.level}</span>
                    </td>
                    <td className="py-1.5 pr-3 text-slate-400">→</td>
                    <td className="py-1.5 pr-3 font-medium text-slate-800 dark:text-slate-100">
                      {e.toName} <span className="font-mono text-slate-400">L{e.to.level}</span>
                    </td>
                    <td className="py-1.5 text-[11.5px] text-slate-500 dark:text-slate-400">{e.rationale}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div>
            <p className="mb-1 flex items-center gap-2 text-[12.5px] font-semibold text-slate-700 dark:text-slate-200">
              <GitBranch size={14} /> Suggested from outcome data — for expert review, never applied automatically
            </p>
            {!inf ? (
              <p className="text-[12px] text-slate-400">No outcome data loaded.</p>
            ) : inf.suggestions.length === 0 ? (
              <p className="text-[12px] text-slate-400">No pair passed the test ({inf.testedPairs} tested).</p>
            ) : (
              <table className="w-full text-left text-[12px]">
                <thead>
                  <tr className="border-b border-gov-line text-[11px] uppercase tracking-wide text-slate-400 dark:border-slate-700">
                    <th className="py-2 pr-3 font-semibold">Before</th>
                    <th className="py-2 pr-3 font-semibold">Then</th>
                    <th className="py-2 pr-3 font-semibold">Extra gain (95% CI)</th>
                    <th className="py-2 pr-3 font-semibold">n with / without</th>
                    <th className="py-2 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {inf.suggestions.map((s) => (
                    <tr key={`${s.from.competencyId}-${s.to.competencyId}-${s.to.level}`}
                        className="border-b border-gov-line/60 dark:border-slate-700/60">
                      <td className="py-2 pr-3">{s.from.competencyName} L{s.from.level}</td>
                      <td className="py-2 pr-3">{s.to.competencyName} L{s.to.level}</td>
                      <td className="py-2 pr-3 font-mono">+{s.effect.toFixed(2)} [{s.ci95[0].toFixed(2)}, {s.ci95[1].toFixed(2)}]</td>
                      <td className="py-2 pr-3 font-mono">{s.nWith} / {s.nWithout}</td>
                      <td className="py-2">
                        <span className={`rounded-full px-2 py-0.5 text-[10.5px] font-bold ${s.status === 'new_suggestion'
                          ? 'bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300'
                          : 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300'}`}>
                          {s.status === 'new_suggestion' ? 'New — review' : 'Supports expert edge'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            {inf && <p className="mt-2 text-[10.5px] text-slate-400">{inf.testedPairs} pairs tested. {inf.method}</p>}
          </div>
        </div>
      )}
    </SectionCard>
  );
};

// ─── Training effectiveness: measured uplift (SCIL v6 §6) ────────────────────

/** A CI whisker on a shared −0.5 … +1.25 level axis, with the point estimate. */
const UpliftBar: React.FC<{ value: number; ci: [number, number]; flagged: boolean }> = ({ value, ci, flagged }) => {
  const lo = -0.5, hi = 1.25;
  const x = (v: number) => `${((Math.min(hi, Math.max(lo, v)) - lo) / (hi - lo)) * 100}%`;
  return (
    <div className="relative h-3 w-40 rounded bg-slate-100 dark:bg-slate-700" title={`[${ci[0]}, ${ci[1]}]`}>
      <div className="absolute top-0 h-full w-px bg-slate-400" style={{ left: x(0) }} />
      <div className={`absolute top-1 h-1 rounded ${flagged ? 'bg-rose-300' : 'bg-blue-300'}`}
           style={{ left: x(ci[0]), width: `calc(${x(ci[1])} - ${x(ci[0])})` }} />
      <div className={`absolute top-0 h-3 w-1 rounded ${flagged ? 'bg-rose-600' : 'bg-gov-blue'}`}
           style={{ left: `calc(${x(value)} - 2px)` }} />
    </div>
  );
};

const TrainingEffectivenessPanel: React.FC = () => {
  const [flaggedOnly, setFlaggedOnly] = React.useState(false);
  const [minLearners, setMinLearners] = React.useState(10);
  const [order, setOrder] = React.useState<'desc' | 'asc'>('asc');
  const [limit, setLimit] = React.useState(15);
  const { data, error, loading } = useInsight<TrainingEffectivenessReport>(
    () => fetchTrainingEffectiveness({ flaggedOnly, minLearners }), [flaggedOnly, minLearners],
  );
  const rows = data
    ? [...data.courses].sort((a, b) => (order === 'asc' ? 1 : -1) * (a.measuredUplift - b.measuredUplift))
    : [];

  return (
    <SectionCard
      title="Training effectiveness — measured uplift"
      subtitle="Levels gained per course from pre/post assessments, propensity-weighted against non-takers and shrunk to the level prior"
      action={
        <div className="flex flex-wrap items-center gap-2 text-[12px]">
          <label className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
            <input type="checkbox" checked={flaggedOnly} onChange={(e) => setFlaggedOnly(e.target.checked)} />
            Flagged only
          </label>
          <select value={minLearners} onChange={(e) => setMinLearners(Number(e.target.value))}
                  className="rounded-lg border border-gov-line bg-white px-2 py-1 dark:border-slate-600 dark:bg-slate-800">
            {[0, 5, 10, 20].map((n) => <option key={n} value={n}>n ≥ {n}</option>)}
          </select>
          <button type="button" onClick={() => setOrder((o) => (o === 'asc' ? 'desc' : 'asc'))}
                  className="rounded-lg border border-gov-line px-2 py-1 font-semibold dark:border-slate-600">
            {order === 'asc' ? 'Lowest first' : 'Highest first'}
          </button>
        </div>
      }
    >
      <PanelState loading={loading && !data} error={error} />
      {data && (
        <div className="space-y-3">
          <p className="text-[12.5px] text-slate-600 dark:text-slate-300">
            {data.summary.courses} courses · {data.summary.learnerRecords.toLocaleString('en-IN')} learner records ·{' '}
            {data.summary.comparisonEpisodes.toLocaleString('en-IN')} comparison episodes · median uplift{' '}
            {data.summary.medianMeasuredUplift.toFixed(2)} levels ·{' '}
            <span className="font-semibold text-rose-600 dark:text-rose-400">{data.summary.flagged} flagged</span>{' '}
            (declared relevance, near-zero uplift)
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-[12px]">
              <thead>
                <tr className="border-b border-gov-line text-[11px] uppercase tracking-wide text-slate-400 dark:border-slate-700">
                  <th className="py-2 pr-3 font-semibold">Course</th>
                  <th className="py-2 pr-3 font-semibold">n</th>
                  <th className="py-2 pr-3 font-semibold">Naive / IPW</th>
                  <th className="py-2 pr-3 font-semibold">Measured uplift (95% CI)</th>
                  <th className="py-2 pr-3 font-semibold">Rating · enrolments</th>
                  <th className="py-2 font-semibold">Flag</th>
                </tr>
              </thead>
              <tbody>
                {rows.slice(0, limit).map((c) => (
                  <tr key={c.courseId} className="border-b border-gov-line/60 align-top dark:border-slate-700/60">
                    <td className="py-2 pr-3">
                      <p className="font-medium text-slate-800 dark:text-slate-100">{c.title}</p>
                      <p className="text-[10.5px] text-slate-400">{c.competencyName} · L{c.courseLevel}</p>
                    </td>
                    <td className="py-2 pr-3 font-mono">{c.n}</td>
                    <td className="py-2 pr-3 font-mono text-slate-500">{c.naiveUplift.toFixed(2)} / {c.ipwUplift.toFixed(2)}</td>
                    <td className="py-2 pr-3">
                      <div className="flex items-center gap-2">
                        <UpliftBar value={c.measuredUplift} ci={c.ci95} flagged={c.misTagFlag} />
                        <span className="font-mono">{c.measuredUplift.toFixed(2)}</span>
                        <span className="font-mono text-[10.5px] text-slate-400">[{c.ci95[0].toFixed(2)}, {c.ci95[1].toFixed(2)}]</span>
                      </div>
                    </td>
                    <td className="py-2 pr-3 font-mono text-slate-500">
                      {c.rating != null ? c.rating.toFixed(2) : '—'} · {c.enrollmentCount?.toLocaleString('en-IN') ?? '—'}
                    </td>
                    <td className="py-2">
                      {c.misTagFlag && (
                        <span title={c.flagReason ?? undefined}
                              className="rounded-full bg-rose-50 px-2 py-0.5 text-[10.5px] font-bold text-rose-700 dark:bg-rose-900/30 dark:text-rose-300">
                          Review tag
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {rows.length > limit && (
            <button type="button" onClick={() => setLimit((l) => l + 25)}
                    className="text-[11.5px] font-semibold text-gov-blue hover:underline">
              Show more ({rows.length - limit} left)
            </button>
          )}
          <p className="text-[10.5px] text-slate-400">{data.method}</p>
          <p className="text-[10.5px] text-amber-600 dark:text-amber-400">{data.dataNote}</p>
        </div>
      )}
    </SectionCard>
  );
};

// ─── Workforce foresight (SCIL v6 §11) ───────────────────────────────────────

const RISK_CHIP: Record<RiskBand, string> = {
  critical: 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300',
  high:     'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300',
  moderate: 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300',
  low:      'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300',
};

const Cell: React.FC<{ c: CountCell }> = ({ c }) => (
  <span className={`font-mono ${c.suppressed ? 'text-slate-400' : ''}`}
        title={c.suppressed ? 'Suppressed: fewer than 5 officials' : undefined}>
    {c.display}
  </span>
);

const CapabilityRiskPanel: React.FC = () => {
  const { data, error, loading } = useInsight<CapabilityRiskReport>(fetchCapabilityRisk, []);
  return (
    <SectionCard
      title="Capability risk by statistical product"
      subtitle="Officials at Level 3+ on each competency critical to a product, retirements in 36 months, single points of failure"
    >
      <PanelState loading={loading} error={error} />
      {data && (
        <div className="space-y-3">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-[12px]">
              <thead>
                <tr className="border-b border-gov-line text-[11px] uppercase tracking-wide text-slate-400 dark:border-slate-700">
                  <th className="py-2 pr-3 font-semibold">Product</th>
                  <th className="py-2 pr-3 font-semibold">Critical competency</th>
                  <th className="py-2 pr-3 font-semibold">Team</th>
                  <th className="py-2 pr-3 font-semibold">Capable (L{data.capableLevel}+)</th>
                  <th className="py-2 pr-3 font-semibold">Retire ≤ {data.horizonMonths} mo</th>
                  <th className="py-2 font-semibold">Risk</th>
                </tr>
              </thead>
              <tbody>
                {data.products.flatMap((p) => p.competencies.map((r, i) => (
                  <tr key={`${p.productId}-${r.competencyId}`} className="border-b border-gov-line/60 align-top dark:border-slate-700/60">
                    <td className="py-2 pr-3 font-medium text-slate-800 dark:text-slate-100">
                      {i === 0 ? <>{p.productName} <span className="text-[10.5px] text-slate-400">({p.productId})</span></> : ''}
                    </td>
                    <td className="py-2 pr-3">{r.competencyName}</td>
                    <td className="py-2 pr-3"><Cell c={r.teamSize} /></td>
                    <td className="py-2 pr-3"><Cell c={r.capable} /></td>
                    <td className="py-2 pr-3"><Cell c={r.retiringWithin36m} /></td>
                    <td className="py-2">
                      <span title={r.reason} className={`rounded-full px-2 py-0.5 text-[10.5px] font-bold ${RISK_CHIP[r.risk]}`}>
                        {r.singlePointOfFailure ? 'single point of failure' : r.risk}
                      </span>
                    </td>
                  </tr>
                )))}
              </tbody>
            </table>
          </div>
          <p className="text-[10.5px] text-slate-400">{data.suppression} As of {data.asOf}.</p>
        </div>
      )}
    </SectionCard>
  );
};

const ForesightPanel: React.FC = () => {
  const { data, error, loading } = useInsight<ForesightReport>(fetchForesight, []);
  const [onlyDeclining, setOnlyDeclining] = React.useState(true);
  const rows = data ? data.series.filter((s) => !onlyDeclining || s.declining) : [];
  return (
    <SectionCard
      title="36-month foresight — attrition × skill decay"
      subtitle="Expected capable officials per product and critical competency if no new training happens"
      action={
        <label className="flex items-center gap-1.5 text-[12px] text-slate-600 dark:text-slate-300">
          <input type="checkbox" checked={onlyDeclining} onChange={(e) => setOnlyDeclining(e.target.checked)} />
          Declining only
        </label>
      }
    >
      <PanelState loading={loading} error={error} />
      {data && (
        <div className="space-y-3">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-[12px]">
              <thead>
                <tr className="border-b border-gov-line text-[11px] uppercase tracking-wide text-slate-400 dark:border-slate-700">
                  <th className="py-2 pr-3 font-semibold">Product · competency</th>
                  <th className="py-2 pr-3 font-semibold">Series</th>
                  {data.months.map((m) => <th key={m} className="py-2 pr-2 text-right font-semibold">{m} mo</th>)}
                </tr>
              </thead>
              <tbody>
                {rows.flatMap((s) => [
                  <tr key={`${s.productId}-${s.competencyId}-d`} className="align-top">
                    <td rowSpan={2} className="border-b border-gov-line/60 py-2 pr-3 dark:border-slate-700/60">
                      <span className="font-medium text-slate-800 dark:text-slate-100">{s.productId}</span>{' '}
                      <span className="text-slate-500">{s.competencyName}</span>
                    </td>
                    <td className="py-1 pr-3 text-[11px] text-slate-500">attrition + decay</td>
                    {s.withDecay.map((p) => <td key={p.month} className="py-1 pr-2 text-right"><Cell c={p.expectedCapable} /></td>)}
                  </tr>,
                  <tr key={`${s.productId}-${s.competencyId}-a`} className="border-b border-gov-line/60 dark:border-slate-700/60">
                    <td className="py-1 pr-3 text-[11px] text-slate-400">attrition only</td>
                    {s.attritionOnly.map((p) => <td key={p.month} className="py-1 pr-2 text-right text-slate-400"><Cell c={p.expectedCapable} /></td>)}
                  </tr>,
                ])}
              </tbody>
            </table>
          </div>
          <p className="text-[10.5px] text-slate-400">{data.method} {data.suppression}</p>
        </div>
      )}
    </SectionCard>
  );
};

const PRIORITY_CHIP: Record<string, string> = {
  high: 'bg-rose-50 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300',
  medium: 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300',
  low: 'bg-slate-100 text-slate-500 dark:bg-slate-700/60 dark:text-slate-400',
};
const AGENDA_TYPE: Record<string, string> = {
  coverage_gap: 'Coverage gap', capability_risk: 'Capability risk',
  ineffective_course: 'Course review', prerequisite_review: 'Prerequisite review',
};

const TpacAgendaPanel: React.FC = () => {
  const { data, error, loading } = useInsight<TpacAgenda>(fetchTpacAgenda, []);
  return (
    <SectionCard title="Draft TPAC agenda" subtitle="Generated drafts for the NSSTA training programme committee — nothing here is decided">
      <PanelState loading={loading} error={error} empty={!!data && data.items.length === 0} />
      {data && data.items.length > 0 && (
        <ol className="space-y-2.5">
          {data.items.map((i) => (
            <li key={i.id} className="rounded-lg border border-gov-line p-3 dark:border-slate-700">
              <div className="mb-1 flex flex-wrap items-center gap-2">
                <span className="font-mono text-[10.5px] text-slate-400">{i.id}</span>
                <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${PRIORITY_CHIP[i.priority]}`}>{i.priority}</span>
                <span className="text-[10.5px] font-semibold uppercase tracking-wide text-slate-400">{AGENDA_TYPE[i.type]}</span>
                <span className="text-[10.5px] text-slate-400">· {i.status}</span>
              </div>
              <p className="text-[12.5px] font-semibold text-slate-800 dark:text-slate-100">{i.title}</p>
              <p className="mt-0.5 text-[11.5px] text-slate-500 dark:text-slate-400">{i.rationale}</p>
            </li>
          ))}
        </ol>
      )}
      {data && <p className="mt-3 text-[10.5px] text-slate-400">{data.note}</p>}
    </SectionCard>
  );
};

// ─── Page ─────────────────────────────────────────────────────────────────────

const WorkforceInsights: React.FC = () => (
  <div className="animate-fade-up space-y-5">
    <div className="flex items-start gap-2.5 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-[12.5px] text-amber-800 dark:border-amber-800/60 dark:bg-amber-900/20 dark:text-amber-300">
      <FlaskConical size={16} className="mt-0.5 shrink-0" />
      <p>
        <span className="font-semibold">Synthetic data — demo only.</span> These views run the real SCIL v6
        computations on mock data from the generator in <code>mock-igot-server/</code>. They show how the
        platform would reason; they say nothing about real officials, courses or offices.
      </p>
    </div>
    <div className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-slate-400">
      <Layers size={13} /> Capability scope
    </div>
    <GsbpmScopePanel />
    <div className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-slate-400">
      <Route size={13} /> Learning design
    </div>
    <PrerequisitePanel />
    <TrainingEffectivenessPanel />
    <div className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-slate-400">
      <Telescope size={13} /> Workforce foresight
    </div>
    <CapabilityRiskPanel />
    <ForesightPanel />
    <TpacAgendaPanel />
  </div>
);

export default WorkforceInsights;
