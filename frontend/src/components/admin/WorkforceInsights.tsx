/**
 * FILE: src/components/admin/WorkforceInsights.tsx
 *
 * Admin "Insights" tab — SCIL v6 workforce views. Every panel reads one
 * admin-only backend endpoint; every number is computed by backend code over
 * SYNTHETIC mock data, which the page says up front.
 */

import React from 'react';
import { AlertTriangle, FlaskConical, GitBranch, Layers, Route } from 'lucide-react';

import SectionCard from '../shell/SectionCard';
import {
  fetchGsbpmScope, fetchPrerequisiteDag, type GsbpmScopeReport, type PrerequisiteDagReport,
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
  </div>
);

export default WorkforceInsights;
