/**
 * FILE: src/components/admin/SystemHealthPanel.tsx
 *
 * GET /api/v1/admin/console/system-health — the backend's /health payload plus
 * live probes: iGOT connection, auth DB, recommendation engine, reference
 * data, workforce snapshot, embedders and Gemini. Gemini is only called on
 * "Live check" (it costs an external request). Status is shown as icon +
 * label, never colour alone.
 */

import React from 'react';
import { AlertTriangle, CheckCircle2, HelpCircle, RefreshCcw, XCircle } from 'lucide-react';

import SectionCard from '../shell/SectionCard';
import { useAsync } from '../../hooks/useAdminData';
import { fetchSystemHealth, type HealthStatus } from '../../services/api';

const STATUS: Record<HealthStatus, { icon: React.ElementType; label: string; cls: string }> = {
  ok:       { icon: CheckCircle2, label: 'OK',       cls: 'bg-accent-green-soft text-accent-green dark:bg-emerald-500/15 dark:text-emerald-300' },
  degraded: { icon: AlertTriangle, label: 'Degraded', cls: 'bg-accent-orange-soft text-accent-orange dark:bg-orange-500/15 dark:text-orange-300' },
  down:     { icon: XCircle,      label: 'Down',     cls: 'bg-accent-rose-soft text-accent-rose dark:bg-rose-500/15 dark:text-rose-300' },
  unknown:  { icon: HelpCircle,   label: 'Unknown',  cls: 'bg-slate-100 text-slate-500 dark:bg-slate-700 dark:text-slate-300' },
};

export const StatusChip: React.FC<{ status: HealthStatus }> = ({ status }) => {
  const s = STATUS[status] ?? STATUS.unknown;
  return (
    <span className={`chip inline-flex items-center gap-1 ${s.cls}`}>
      <s.icon size={12} aria-hidden="true" /> {s.label}
    </span>
  );
};

const SystemHealthPanel: React.FC<{ compact?: boolean }> = ({ compact }) => {
  const [probe, setProbe] = React.useState(0);          // >0 → include the Gemini probe
  const { data, isLoading, error, refetch } = useAsync(() => fetchSystemHealth(probe > 0), `health|${probe}`);
  const components = data?.components ?? [];
  const shown = compact ? components.filter((c) => ['igot', 'database', 'engine', 'embedder_catalog', 'embedder_chat', 'groq', 'gemini'].includes(c.id)) : components;

  return (
    <SectionCard
      title="System health"
      subtitle={data ? `Checked ${new Date(data.checkedAt).toLocaleTimeString()}` : 'Live service status'}
      action={
        <div className="flex items-center gap-2">
          {data && <StatusChip status={data.overall} />}
          <button
            type="button"
            onClick={() => (probe ? refetch() : setProbe(1))}
            disabled={isLoading}
            className="flex items-center gap-1.5 rounded-lg border border-gov-line px-3 py-1.5 text-[12px] font-semibold text-slate-600 hover:text-gov-navy disabled:opacity-50 dark:border-slate-600 dark:text-slate-300 dark:hover:text-white"
            title="Re-run every probe, including a live Gemini call"
          >
            <RefreshCcw size={13} className={isLoading ? 'animate-spin' : ''} /> Live check
          </button>
        </div>
      }
    >
      {error && <p className="py-6 text-center text-[12.5px] text-rose-600 dark:text-rose-400">{error}</p>}
      {!error && !data && <p className="py-6 text-center text-[12.5px] text-slate-400">Probing services…</p>}
      <ul className="divide-y divide-gov-line dark:divide-slate-800">
        {shown.map((c) => (
          <li key={c.id} className="flex items-start gap-3 py-2.5">
            <span className="min-w-0 flex-1">
              <span className="block text-[12.5px] font-semibold text-gov-ink dark:text-white">{c.label}</span>
              <span className="block text-[11.5px] text-slate-500 dark:text-slate-400">{c.detail}</span>
            </span>
            {c.latencyMs != null && <span className="mt-0.5 text-[11px] tabular-nums text-slate-400">{c.latencyMs} ms</span>}
            <StatusChip status={c.status} />
          </li>
        ))}
      </ul>
      {data && !compact && (
        <p className="mt-3 text-[11px] text-slate-400">
          Last daily workforce snapshot: {data.lastDailySnapshot ?? 'none yet'} · /health: ready={String(data.health.ready)},
          snapshot={data.health.workforceSnapshot}
        </p>
      )}
    </SectionCard>
  );
};

export default SystemHealthPanel;
