/**
 * FILE: src/components/admin/AdminFilterBar.tsx
 *
 * The one filter row shared by every admin view: department, grade (service
 * tier) and office. Options and headcounts come from
 * GET /api/v1/admin/console/filters; the values are passed to every console
 * endpoint so all views and exports agree.
 */

import React from 'react';
import { Filter, X } from 'lucide-react';

import type { AdminFacets, AdminFilters, FacetOption } from '../../services/api';

const SELECT =
  'min-w-0 flex-1 rounded-lg border border-gov-line bg-white px-2.5 py-1.5 text-[12.5px] text-slate-700 ' +
  'sm:flex-none sm:w-52 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200';

const FacetSelect: React.FC<{
  label: string; value?: string; options: FacetOption[]; onChange: (v?: string) => void;
}> = ({ label, value, options, onChange }) => (
  <label className="flex w-full min-w-0 items-center gap-2 sm:w-auto sm:flex-1 md:flex-none">
    <span className="sr-only">{label}</span>
    <select
      aria-label={label}
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value || undefined)}
      className={SELECT}
    >
      <option value="">All {label.toLowerCase()}s</option>
      {options.map((o) => (
        <option key={o.value} value={o.value}>{o.label} ({o.count})</option>
      ))}
    </select>
  </label>
);

export function facetLabels(facets: AdminFacets | null, f: AdminFilters) {
  const find = (opts: FacetOption[] | undefined, v?: string) => opts?.find((o) => o.value === v)?.label ?? v;
  return {
    department: f.department,
    grade: find(facets?.grades, f.grade),
    office: find(facets?.offices, f.office),
  };
}

const AdminFilterBar: React.FC<{
  facets: AdminFacets | null;
  value: AdminFilters;
  onChange: (f: AdminFilters) => void;
  actions?: React.ReactNode;
  note?: string;
}> = ({ facets, value, onChange, actions, note }) => {
  const active = Boolean(value.department || value.grade || value.office);
  return (
    <div className="panel mb-5 flex flex-col gap-3 p-3.5 lg:flex-row lg:items-center">
      <div className="grid flex-1 grid-cols-1 gap-2 sm:flex sm:flex-wrap sm:items-center">
        <Filter size={14} className="hidden text-slate-400 sm:block" aria-hidden="true" />
        <FacetSelect label="Department" value={value.department} options={facets?.departments ?? []}
                     onChange={(department) => onChange({ ...value, department })} />
        <FacetSelect label="Grade" value={value.grade} options={facets?.grades ?? []}
                     onChange={(grade) => onChange({ ...value, grade })} />
        <FacetSelect label="Office" value={value.office} options={facets?.offices ?? []}
                     onChange={(office) => onChange({ ...value, office })} />
        {active && (
          <button
            type="button"
            onClick={() => onChange({})}
            className="flex items-center justify-center gap-1 rounded-lg px-2 py-1.5 text-[12px] font-semibold text-slate-500 hover:text-gov-navy dark:text-slate-400 dark:hover:text-white"
          >
            <X size={13} /> Clear
          </button>
        )}
        {note && <span className="text-[11px] text-slate-400">{note}</span>}
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </div>
  );
};

export const ExportButton: React.FC<{
  label: string; icon: React.ElementType; onClick: () => void | Promise<void>; disabled?: boolean;
}> = ({ label, icon: Icon, onClick, disabled }) => {
  const [busy, setBusy] = React.useState(false);
  return (
    <button
      type="button"
      disabled={disabled || busy}
      onClick={async () => {
        setBusy(true);
        try { await onClick(); } catch (e) { alert(e instanceof Error ? e.message : 'Export failed'); }
        finally { setBusy(false); }
      }}
      className="flex items-center gap-1.5 rounded-lg border border-gov-line px-3 py-1.5 text-[12px] font-semibold text-slate-600 transition-colors hover:border-gov-blue/40 hover:text-gov-navy disabled:opacity-50 dark:border-slate-600 dark:text-slate-300 dark:hover:text-white"
    >
      <Icon size={13} className={busy ? 'animate-pulse' : ''} /> {label}
    </button>
  );
};

export default AdminFilterBar;
