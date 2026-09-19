/**
 * FILE: src/pages/AdminDashboard.tsx
 *
 * Ministry-side dashboard at /admin (role `admin` only).
 *
 * Sections: overview · officials · competencies · analytics · emerging skills ·
 * actions · insights · reports. KPIs, the shortage heatmap, departmental
 * compliance, roster pages, trends and exports are all computed on the server
 * (routers/admin_console.py) — the browser never aggregates the whole roster.
 * One filter row (department · grade · office) drives every per-official view
 * and every export. `insights` renders components/admin/WorkforceInsights
 * (SCIL v6 views; the office filter feeds its GSBPM panel). Empty data reads
 * as empty — no invented fallback numbers.
 */

import React, { useEffect, useMemo, useState } from 'react';
import {
  Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import {
  AlertTriangle, BarChart3, BellRing, BookOpen, Building2, CheckCircle2, ChevronLeft, ChevronRight,
  ClipboardCheck, Download, FileText, LayoutDashboard, LineChart as LineChartIcon, Lightbulb, RefreshCcw,
  ShieldCheck, SlidersHorizontal, Sparkles, TrendingUp, Users,
} from 'lucide-react';

import { useTheme } from '../hooks/useTheme';
import { useAdminFacets, useAdminOverview, useAdminRoster } from '../hooks/useAdminData';
import type { AdminRosterRow } from '../hooks/useAdminData';
import { useSkillsData } from '../hooks/useSkillsData';
import type { SkillRow } from '../hooks/useSkillsData';
import {
  downloadAdminCsv, fetchAdminRoster, fetchAdminTrends, fetchEmergingSkills, fetchMandatoryBehind,
  type AdminExportKind, type AdminFilters,
} from '../services/api';

import AppShell, { type ShellNavGroup } from '../components/shell/AppShell';
import PageHeader from '../components/shell/PageHeader';
import SectionCard, { SectionAction } from '../components/shell/SectionCard';
import StatCard from '../components/shell/StatCard';
import { AshokaChakra } from '../components/gov/GovUI';
import WorkforceInsights from '../components/admin/WorkforceInsights';
import AdminFilterBar, { ExportButton, facetLabels } from '../components/admin/AdminFilterBar';
import TrendsPanel from '../components/admin/TrendsPanel';
import SystemHealthPanel from '../components/admin/SystemHealthPanel';
import EmergingSkills from '../components/admin/EmergingSkills';
import AdminActions from '../components/admin/AdminActions';
import CertificateReviewQueue from '../components/admin/CertificateReviewQueue';
import { describeFilters, printReport, type ReportSection } from '../components/admin/adminReport';

type AdminTab = 'dashboard' | 'officials' | 'competencies' | 'analytics' | 'emerging' | 'actions' | 'insights' | 'reports';

const ITEMS_PER_PAGE = 10;
const PDF_ROW_CAP = 200;
// Validated with the dataviz palette checker; fixed order, one hue per measure.
const BAR_LIGHT = ['#1d4ed8', '#ea580c'];
const BAR_DARK = ['#3b82f6', '#ea580c'];

// ─── Status helpers ───────────────────────────────────────────────────────────
function enrollmentLabel(status: number | undefined): string {
  if (status === 2) return 'Compliant';
  if (status === 1) return 'In Progress';
  return 'Training Required';
}

const STATUS_CHIP: Record<string, string> = {
  'Compliant':        'bg-accent-green-soft text-accent-green dark:bg-emerald-500/15 dark:text-emerald-300',
  'In Progress':      'bg-accent-orange-soft text-accent-orange dark:bg-orange-500/15 dark:text-orange-300',
  'Training Required':'bg-accent-rose-soft text-accent-rose dark:bg-rose-500/15 dark:text-rose-300',
};

/** Download rows as a CSV file, quoting every cell (FRAC dictionary only — the rest is server-built). */
function downloadCsv(filename: string, headers: string[], rows: (string | number)[][]) {
  const esc = (v: string | number) => `"${String(v ?? '').replace(/"/g, '""')}"`;
  const csv = [headers, ...rows].map((r) => r.map(esc).join(',')).join('\r\n');
  const url = URL.createObjectURL(new Blob([`﻿${csv}`], { type: 'text/csv;charset=utf-8;' }));
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// ─── Shared bits ──────────────────────────────────────────────────────────────
const ErrorBanner: React.FC<{ message: string; onRetry: () => void }> = ({ message, onRetry }) => (
  <div className="mb-5 flex items-center gap-4 rounded-2xl border border-red-200 bg-red-50 p-5 text-sm dark:border-red-700/50 dark:bg-red-900/20">
    <AlertTriangle className="h-5 w-5 flex-shrink-0 text-accent-rose" aria-hidden="true" />
    <div className="flex-1">
      <p className="font-semibold text-red-700 dark:text-red-400">Failed to load data</p>
      <p className="mt-0.5 text-xs text-red-600 dark:text-red-500">{message}</p>
    </div>
    <button
      onClick={onRetry}
      className="flex items-center gap-1.5 rounded-lg bg-red-100 px-4 py-2 text-xs font-semibold text-red-700 transition-colors hover:bg-red-200 dark:bg-red-800/50 dark:text-red-300 dark:hover:bg-red-700/50"
    >
      <RefreshCcw className="h-3.5 w-3.5" /> Retry
    </button>
  </div>
);

const Pagination: React.FC<{
  page: number; totalPages: number; totalItems: number; noun: string;
  onChange: (page: number) => void;
}> = ({ page, totalPages, totalItems, noun, onChange }) => (
  <div className="flex flex-col items-center justify-between gap-3 border-t border-gov-line px-5 py-3.5 sm:flex-row dark:border-slate-800">
    <p className="text-[12.5px] text-slate-500 dark:text-slate-400">
      Showing <span className="font-semibold text-slate-700 dark:text-slate-200">{(page - 1) * ITEMS_PER_PAGE + 1}</span>
      {' '}to <span className="font-semibold text-slate-700 dark:text-slate-200">{Math.min(page * ITEMS_PER_PAGE, totalItems)}</span>
      {' '}of <span className="font-semibold text-slate-700 dark:text-slate-200">{totalItems}</span> {noun}
    </p>
    <div className="flex items-center gap-2">
      <button
        onClick={() => onChange(Math.max(1, page - 1))}
        disabled={page === 1}
        className="flex items-center gap-1 rounded-lg border border-gov-line px-3 py-1.5 text-[12.5px] font-medium text-slate-600 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-700"
      >
        <ChevronLeft className="h-4 w-4" /> Previous
      </button>
      <span className="px-2 text-[12.5px] font-medium text-slate-600 dark:text-slate-400">
        Page {page} of {totalPages}
      </span>
      <button
        onClick={() => onChange(Math.min(totalPages, page + 1))}
        disabled={page === totalPages}
        className="flex items-center gap-1 rounded-lg border border-gov-line px-3 py-1.5 text-[12.5px] font-medium text-slate-600 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-700"
      >
        Next <ChevronRight className="h-4 w-4" />
      </button>
    </div>
  </div>
);

const TableSkeleton: React.FC<{ cols: number }> = ({ cols }) => (
  <>
    {Array.from({ length: 5 }, (_, i) => (
      <tr key={i} className="animate-pulse">
        {Array.from({ length: cols }, (_, j) => (
          <td key={j} className="px-4 py-4"><div className="h-4 w-full rounded bg-slate-100 dark:bg-slate-700" /></td>
        ))}
      </tr>
    ))}
  </>
);

const RosterRow: React.FC<{ employee: AdminRosterRow }> = ({ employee }) => {
  const label = enrollmentLabel(employee.enrollmentStatus);
  const name = `${employee.firstName} ${employee.lastName}`.trim() || employee.govId;
  const m = employee.mandatory;
  return (
    <tr>
      <td>
        <span className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gov-navy/10 text-[11px] font-bold text-gov-navy dark:bg-sky-500/15 dark:text-sky-300">
            {name.charAt(0).toUpperCase()}
          </span>
          <span className="min-w-0">
            <span className="block truncate font-semibold text-gov-ink dark:text-white">{name}</span>
            <span className="block truncate text-[11px] text-slate-400">{employee.govId} · {employee.email || employee.userId}</span>
          </span>
        </span>
      </td>
      <td className="text-slate-500 dark:text-slate-400">
        {employee.designation}
        <span className="block text-[11px] text-slate-400">{employee.gradeLabel}</span>
      </td>
      <td className="text-slate-500 dark:text-slate-400">{employee.department}</td>
      <td className="font-medium">{employee.missingSkill ?? '—'}</td>
      <td className="whitespace-nowrap tabular-nums">
        {m ? `${m.completed}/${m.total}` : '—'}
      </td>
      <td><span className={`chip ${STATUS_CHIP[label]}`}>{label}</span></td>
    </tr>
  );
};

const SkillTableRow: React.FC<{ skill: SkillRow }> = ({ skill }) => (
  <tr>
    <td className="whitespace-nowrap font-mono text-[12px] font-semibold text-gov-ink dark:text-white">{skill.competency_id}</td>
    <td className="font-semibold text-gov-ink dark:text-white">{skill.name}</td>
    <td><span className="chip bg-accent-blue-soft text-accent-blue dark:bg-blue-500/15 dark:text-blue-300">{skill.category}</span></td>
    <td className="max-w-md truncate text-slate-500 dark:text-slate-400">{skill.description}</td>
  </tr>
);

// ─── Main ─────────────────────────────────────────────────────────────────────
const AdminDashboard: React.FC = () => {
  const { theme } = useTheme();
  const [filters, setFilters] = useState<AdminFilters>({});
  const [activeTab, setActiveTab] = useState<AdminTab>('dashboard');
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<'all' | 0 | 1 | 2>('all');

  const facets = useAdminFacets();
  const overview = useAdminOverview(filters);
  const roster = useAdminRoster(filters, currentPage, ITEMS_PER_PAGE, debouncedSearch, statusFilter);
  const { skills, isLoading: isSkillsLoading, error: skillsError, refetch: refetchSkills } = useSkillsData();

  useEffect(() => { const t = setTimeout(() => setDebouncedSearch(searchTerm), 300); return () => clearTimeout(t); }, [searchTerm]);
  useEffect(() => { setCurrentPage(1); }, [debouncedSearch, activeTab, statusFilter, filters]);

  const isDark = theme === 'dark';
  const axisColor = isDark ? '#94a3b8' : '#64748b';
  const gridColor = isDark ? '#334155' : '#e2e8f0';
  const bars = isDark ? BAR_DARK : BAR_LIGHT;
  const tooltipStyle = { borderRadius: 10, fontSize: 12, border: `1px solid ${gridColor}`, background: isDark ? '#0f172a' : '#fff' };

  const ov = overview.data;
  const kpis = ov?.kpis;
  const statusCounts = ov?.statusCounts ?? { compliant: 0, inProgress: 0, required: 0 };
  const heatmap = useMemo(
    () => (ov?.heatmap ?? []).map((h) => ({ ...h, label: h.competency.length > 20 ? `${h.competency.slice(0, 20)}…` : h.competency })),
    [ov],
  );
  const deptCompliance = useMemo(
    () => (ov?.deptCompliance ?? []).filter((d) => !d.suppressed)
      .map((d) => ({ ...d, label: d.dept.length > 18 ? `${d.dept.slice(0, 18)}…` : d.dept })),
    [ov],
  );
  const labels = facetLabels(facets.data, filters);
  const filterText = describeFilters(filters, labels);
  const refetchAll = () => { overview.refetch(); roster.refetch(); facets.refetch(); refetchSkills(); };

  // ── FRAC filtering / pagination (the dictionary is small and not per-official) ──
  const filteredSkills = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return skills;
    return skills.filter(
      (s) =>
        s.name.toLowerCase().includes(q) ||
        s.category.toLowerCase().includes(q) ||
        s.competency_id.toLowerCase().includes(q) ||
        s.description.toLowerCase().includes(q),
    );
  }, [skills, searchTerm]);
  const totalPagesSkills = Math.max(1, Math.ceil(filteredSkills.length / ITEMS_PER_PAGE));
  const currentSkills = useMemo(
    () => filteredSkills.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE),
    [filteredSkills, currentPage],
  );

  // ── Exports: CSV from the server, PDF via the browser's print dialog ────────
  const csv = (kind: AdminExportKind, extra: Record<string, string | number | undefined> = {}) =>
    downloadAdminCsv(kind, filters, extra);
  const rosterExtra = { search: debouncedSearch, status: statusFilter === 'all' ? undefined : statusFilter };

  const exportCompetencies = () =>
    downloadCsv(
      `frac-competencies-${new Date().toISOString().slice(0, 10)}.csv`,
      ['Competency ID', 'Name', 'Category', 'Description'],
      filteredSkills.map((s) => [s.competency_id, s.name, s.category, s.description]),
    );

  const pdf = async (kind: AdminExportKind) => {
    let title = '';
    let sections: ReportSection[] = [];
    if (kind === 'roster') {
      const r = await fetchAdminRoster(filters, 1, PDF_ROW_CAP, debouncedSearch, rosterExtra.status);
      title = 'NSO officials roster';
      sections = [{
        heading: `${r.total} official(s)`,
        note: r.total > PDF_ROW_CAP ? `First ${PDF_ROW_CAP} rows — use the CSV export for the full list.` : undefined,
        columns: ['Gov ID', 'Name', 'Designation', 'Grade', 'Department', 'Top missing skill', 'Mandatory', 'Status'],
        rows: r.items.map((e) => [e.govId, `${e.firstName} ${e.lastName}`, e.designation, e.gradeLabel, e.department,
          e.missingSkill, e.mandatory ? `${e.mandatory.completed}/${e.mandatory.total}` : '—', e.statusLabel]),
      }];
    } else if (kind === 'mandatory-behind') {
      const r = await fetchMandatoryBehind(filters, 1, PDF_ROW_CAP);
      title = 'Officials behind on mandatory training';
      sections = [{
        heading: `${r.total} official(s) with pending ACBP courses`,
        columns: ['Gov ID', 'Name', 'Department', 'Grade', 'Done', 'Pending courses'],
        rows: r.items.map((b) => [b.govId, b.name, b.department, b.gradeLabel, `${b.completed}/${b.total}`,
          b.pending.map((p) => p.title).join('; ')]),
      }];
    } else if (kind === 'emerging-skills') {
      const e = await fetchEmergingSkills(filters);
      title = 'Emerging skills — NSSTA training priorities';
      sections = [{
        heading: 'Required vs supply vs 36-month forecast', note: e.method,
        columns: ['#', 'Competency', 'Required', 'Supply now', 'Expected 36 m', 'Shortfall 36 m', 'Next year', 'Action'],
        rows: e.items.map((i) => [i.rank, i.competencyName, i.required.display, i.supplyNow.display,
          i.expectedSupply36.display, i.shortfall36.display, i.trainNextYear ? 'yes' : '', i.recommendedAction]),
      }];
    } else if (kind === 'trends') {
      const t = await fetchAdminTrends(filters, 365);
      title = 'Workforce trends';
      sections = [{
        heading: 'Daily snapshots (last 12 months)', note: t.note,
        columns: ['Date', 'Officials', 'Compliance %', 'Mandatory %', 'Avg level', 'At target %', 'Avg missing skills'],
        rows: t.points.map((p) => p.suppressed ? [p.date, '<5', '—', '—', '—', '—', '—']
          : [p.date, p.officials, p.compliancePct, p.mandatoryCompletionPct, p.avgLevel, p.atTargetPct, p.avgMissingSkills]),
      }];
    } else if (kind === 'departments') {
      title = 'Training compliance by department';
      sections = [{
        heading: 'Departments', note: 'Departments with fewer than 5 officials show no percentages.',
        columns: ['Department', 'Headcount', 'Compliance %', 'Mandatory completion %', 'Behind mandatory'],
        rows: (ov?.deptCompliance ?? []).map((d) => [d.dept, d.headcount, d.pct, d.mandatoryPct, d.behindMandatory.display]),
      }];
    } else {
      title = 'Competency shortage index';
      sections = [{
        heading: 'Top shortages', note: 'Weight 1.5 planned / 1 in progress × (4 − current level), summed over officials.',
        columns: ['Competency', 'Shortage index', 'Officials'],
        rows: (ov?.heatmap ?? []).map((h) => [h.competency, h.gap, h.officials.display]),
      }];
    }
    if (!printReport(title, filterText, sections)) alert('Allow pop-ups for this site to export a PDF.');
  };

  // ── Nav ────────────────────────────────────────────────────────────────────
  const navGroups: ShellNavGroup[] = [
    {
      items: [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { id: 'officials', label: 'Officials', icon: Users, badge: kpis?.totalOfficials || undefined },
        { id: 'competencies', label: 'Competencies', icon: BookOpen, badge: skills.length || undefined },
        { id: 'analytics', label: 'Analytics', icon: BarChart3 },
        { id: 'emerging', label: 'Emerging Skills', icon: Sparkles },
        { id: 'actions', label: 'Actions', icon: ClipboardCheck, badge: kpis?.mandatory.behind || undefined },
        { id: 'insights', label: 'Insights', icon: Lightbulb },
        { id: 'reports', label: 'Reports', icon: FileText },
      ],
    },
  ];

  const META: Record<AdminTab, { title: string; subtitle: string }> = {
    dashboard:    { title: 'Admin Dashboard',  subtitle: 'Monitor training progress, workforce trends and service health.' },
    officials:    { title: 'Officials',        subtitle: 'The NSO roster with competency and mandatory-training status from iGOT Karmayogi.' },
    competencies: { title: 'FRAC Competencies',subtitle: 'The competency dictionary that every skill gap is measured against.' },
    analytics:    { title: 'Analytics',        subtitle: 'Shortage concentration, departmental compliance and trends over time.' },
    emerging:     { title: 'Emerging Skills',  subtitle: 'Required competencies vs current supply vs the 36-month forecast — what NSSTA should train next year.' },
    actions:      { title: 'Actions',          subtitle: 'Assign training plans to departments and nudge officials behind on mandatory training.' },
    insights:     { title: 'Workforce Insights', subtitle: 'SCIL v6 views: GSBPM scope, training effectiveness and capability risk (synthetic data).' },
    reports:      { title: 'Reports',          subtitle: 'Export any view as CSV or PDF — every export respects the filters above.' },
  };

  // ── Charts ─────────────────────────────────────────────────────────────────
  const shortageChart = (height = 300) => (
    heatmap.length === 0 ? (
      <p className="py-14 text-center text-[13px] text-slate-400">
        {overview.isLoading ? 'Loading shortage data…' : 'No competency shortages recorded for these officials.'}
      </p>
    ) : (
      <div style={{ height }} className="w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={heatmap} margin={{ top: 10, right: 10, left: -18, bottom: 16 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={gridColor} />
            <XAxis dataKey="label" axisLine={false} tickLine={false} tick={{ fill: axisColor, fontSize: 11 }} dy={8} interval={0} />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: axisColor, fontSize: 11 }} />
            <Tooltip
              cursor={{ fill: isDark ? '#1e293b' : '#f1f5f9' }}
              labelFormatter={(_l, p) => (p?.[0]?.payload?.competency ?? '') as string}
              formatter={(v, _n, item: any) => [`${v} (${item?.payload?.officials?.display} officials)`, 'Shortage index'] as [string, string]}
              contentStyle={tooltipStyle}
            />
            <Bar dataKey="gap" fill={bars[0]} radius={[4, 4, 0, 0]} barSize={34} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    )
  );

  const deptChart = (height = 300, top?: number) => {
    const data = top ? deptCompliance.slice(0, top) : deptCompliance;
    return data.length === 0 ? (
      <p className="py-14 text-center text-[13px] text-slate-400">
        {overview.isLoading ? 'Loading…' : 'No department with 5 or more officials in this view.'}
      </p>
    ) : (
      <div style={{ height }} className="w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 18, right: 10, left: -18, bottom: 16 }} barGap={2}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={gridColor} />
            <XAxis dataKey="label" axisLine={false} tickLine={false} tick={{ fill: axisColor, fontSize: 11 }} dy={8} interval={0} />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: axisColor, fontSize: 11 }} domain={[0, 100]} unit="%" />
            <Tooltip
              cursor={{ fill: isDark ? '#1e293b' : '#f1f5f9' }}
              labelFormatter={(_l, p) => {
                const d = p?.[0]?.payload;
                return d ? `${d.dept} · ${d.headcount} officials` : '';
              }}
              formatter={(v) => (v == null ? '—' : `${v}%`)}
              contentStyle={tooltipStyle}
            />
            <Legend wrapperStyle={{ fontSize: 11.5, color: axisColor }} />
            <Bar dataKey="pct" name="Completed ≥1 course" fill={bars[0]} radius={[4, 4, 0, 0]} barSize={18} />
            <Bar dataKey="mandatoryPct" name="Mandatory (ACBP) completion" fill={bars[1]} radius={[4, 4, 0, 0]} barSize={18} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const exportButtons = (kind: AdminExportKind, extra: Record<string, string | number | undefined> = {}) => (
    <>
      <ExportButton label="CSV" icon={Download} onClick={() => csv(kind, extra)} />
      <ExportButton label="PDF" icon={FileText} onClick={() => pdf(kind)} />
    </>
  );

  const filterBar = (actions?: React.ReactNode, note?: string) => (
    <AdminFilterBar facets={facets.data} value={filters} onChange={setFilters} actions={actions} note={note} />
  );

  return (
    <AppShell
      groups={navGroups}
      activeId={activeTab}
      onNavigate={(id) => setActiveTab(id as AdminTab)}
      userName="Admin"
      userRole="System Administrator"
      notificationCount={kpis?.mandatory.behind ?? 0}
      onNotificationsClick={() => setActiveTab('actions')}
      searchValue={searchTerm}
      onSearchChange={(v) => {
        setSearchTerm(v);
        if (v && activeTab !== 'officials' && activeTab !== 'competencies') setActiveTab('officials');
      }}
      searchPlaceholder="Search officials, competencies…"
      sidebarFooter={
        <div className="rounded-xl border border-gov-line bg-gov-paper p-4 text-center dark:border-slate-700/60 dark:bg-slate-800/50">
          <p className="text-[12.5px] font-semibold text-gov-ink dark:text-white">Data for a Better India</p>
          <p className="mt-1 text-[10.5px] uppercase tracking-[0.12em] text-slate-400">Empower · Train · Transform</p>
        </div>
      }
    >
      <PageHeader
        title={META[activeTab].title}
        subtitle={META[activeTab].subtitle}
        breadcrumb={['Home', 'Admin', META[activeTab].title]}
        actions={
          <button
            type="button"
            onClick={refetchAll}
            className="panel flex items-center gap-2 px-3.5 py-2 text-[12.5px] font-semibold text-slate-600 transition-colors hover:text-gov-navy dark:text-slate-300 dark:hover:text-white"
          >
            <RefreshCcw size={14} className={overview.isLoading ? 'animate-spin' : ''} /> Refresh
          </button>
        }
      />

      {/* One filter row for every per-official view; the FRAC dictionary is not per-official. */}
      {activeTab !== 'competencies' && activeTab !== 'officials' && activeTab !== 'analytics' && filterBar(
        undefined,
        activeTab === 'insights' ? 'Office feeds the GSBPM scope panel; product-level views are NSO-wide.' : undefined,
      )}

      {/* ── Overview ──────────────────────────────────────────────────────── */}
      {activeTab === 'dashboard' && (
        <div className="animate-fade-up space-y-5">
          {overview.error && <ErrorBanner message={overview.error} onRetry={overview.refetch} />}

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard
              index={0} icon={Users} tone="blue" label="Officials" value={kpis?.totalOfficials ?? '—'}
              caption={filterText} onClick={() => setActiveTab('officials')}
            />
            <StatCard
              index={1} icon={ShieldCheck} tone="green" label="Training Compliance"
              value={kpis ? `${kpis.trainingCompliancePct}%` : '—'} progress={kpis?.trainingCompliancePct}
              caption={`${statusCounts.compliant} with at least one completed course`}
            />
            <StatCard
              index={2} icon={BellRing} tone="orange" label="Mandatory (ACBP) Completion"
              value={kpis?.mandatory.completionPct != null ? `${kpis.mandatory.completionPct}%` : '—'}
              progress={kpis?.mandatory.completionPct ?? undefined}
              caption={kpis ? `${kpis.mandatory.behind} officials behind — assign or nudge` : undefined}
              onClick={() => setActiveTab('actions')}
            />
            <StatCard
              index={3} icon={AlertTriangle} tone="purple" label="Avg Missing Skills"
              value={kpis?.avgMissingSkills ?? '—'} caption="Per official, planned or in progress"
              onClick={() => setActiveTab('analytics')}
            />
          </div>

          <TrendsPanel filters={filters} compact />

          <div className="grid grid-cols-1 items-start gap-5 xl:grid-cols-2">
            <SectionCard
              title="Competency Shortage Index"
              subtitle="Weighted by deficiency level, computed on the server"
              action={<SectionAction label="Analytics" onClick={() => setActiveTab('analytics')} />}
            >
              {shortageChart(268)}
            </SectionCard>

            <SectionCard
              title="Compliance by Department"
              subtitle="Five largest departments in view"
              action={<SectionAction label="Analytics" onClick={() => setActiveTab('analytics')} />}
            >
              {deptChart(268, 5)}
            </SectionCard>
          </div>

          <div className="grid grid-cols-1 items-start gap-5 xl:grid-cols-2">
            <SectionCard
              title="Officials Needing Training"
              subtitle="No course started yet"
              action={<SectionAction label="View all" onClick={() => { setStatusFilter(0); setActiveTab('officials'); }} />}
            >
              <ul className="space-y-3">
                {(ov?.needsTraining ?? []).map((r) => (
                  <li key={r.userId} className="flex items-center gap-3">
                    <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-accent-rose-soft text-[11px] font-bold text-accent-rose dark:bg-rose-500/15 dark:text-rose-300">
                      {(r.firstName || r.govId).charAt(0).toUpperCase()}
                    </span>
                    <span className="min-w-0 flex-1 leading-tight">
                      <span className="block truncate text-[12.5px] font-semibold text-gov-ink dark:text-white">
                        {`${r.firstName} ${r.lastName}`.trim() || r.govId}
                      </span>
                      <span className="block truncate text-[11px] text-slate-400">{r.designation} · {r.department}</span>
                    </span>
                    {r.missingSkill && (
                      <span className="chip hidden bg-slate-100 text-slate-600 sm:inline-flex dark:bg-slate-700 dark:text-slate-300">
                        {r.missingSkill}
                      </span>
                    )}
                  </li>
                ))}
                {ov && ov.needsTraining.length === 0 && (
                  <li className="py-8 text-center text-[13px] text-slate-400">Every official in view has started at least one course.</li>
                )}
                {!ov && <li className="py-8 text-center text-[13px] text-slate-400">Loading roster…</li>}
              </ul>
            </SectionCard>

            <SystemHealthPanel compact />
          </div>

          {/* CTA banner */}
          <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-gov-ink via-gov-navy to-gov-blue p-6 text-white shadow-gov-lg">
            <div className="pointer-events-none absolute -right-8 -bottom-16 text-white/10">
              <AshokaChakra size={180} className="animate-spin-slow" />
            </div>
            <div className="relative flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
              <div className="flex items-start gap-4">
                <span className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl border border-white/20 bg-white/10">
                  <TrendingUp size={22} className="text-gov-saffron" aria-hidden="true" />
                </span>
                <div>
                  <h3 className="mb-1 text-[15.5px] font-semibold">What should NSSTA train next year?</h3>
                  <p className="max-w-xl text-[12.5px] leading-relaxed text-white/70">
                    Compare required competencies with today's supply and the 36-month forecast.
                  </p>
                </div>
              </div>
              <button type="button" onClick={() => setActiveTab('emerging')} className="gov-btn-saffron flex-shrink-0">
                Emerging skills <Sparkles size={15} />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Officials ─────────────────────────────────────────────────────── */}
      {activeTab === 'officials' && (
        <div className="animate-fade-up">
          {filterBar(exportButtons('roster', rosterExtra))}
          {roster.error && <ErrorBanner message={roster.error} onRetry={roster.refetch} />}
          <SectionCard
            title="Official Roster"
            subtitle={roster.data ? `${roster.data.total} officials match` : 'Loading…'}
            padded={false}
          >
            <div className="flex flex-wrap items-center gap-2 px-5 pb-4">
              <SlidersHorizontal size={14} className="text-slate-400" aria-hidden="true" />
              {([['all', 'All'], [2, 'Compliant'], [1, 'In Progress'], [0, 'Training Required']] as const).map(([value, label]) => {
                const c = roster.data?.statusCounts;
                return (
                  <button
                    key={String(value)}
                    type="button"
                    aria-pressed={statusFilter === value}
                    onClick={() => setStatusFilter(value as typeof statusFilter)}
                    className="chip-filter"
                  >
                    {label}
                    {value !== 'all' && c && (
                      <span className="text-slate-400">
                        ({value === 2 ? c.compliant : value === 1 ? c.inProgress : c.required})
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            <div className="overflow-x-auto">
              <table className="gov-table min-w-[900px]">
                <thead>
                  <tr>
                    <th scope="col">Official</th>
                    <th scope="col">Designation · grade</th>
                    <th scope="col">Department</th>
                    <th scope="col">Top Missing Skill</th>
                    <th scope="col">Mandatory</th>
                    <th scope="col">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {roster.isLoading && !roster.data ? (
                    <TableSkeleton cols={6} />
                  ) : roster.data && roster.data.items.length > 0 ? (
                    roster.data.items.map((emp) => <RosterRow key={emp.userId} employee={emp} />)
                  ) : (
                    <tr>
                      <td colSpan={6} className="py-12 text-center text-slate-400">
                        No officials match the current search and filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {roster.data && roster.data.total > 0 && (
              <Pagination
                page={roster.data.page} totalPages={roster.data.totalPages} totalItems={roster.data.total}
                noun="officials" onChange={setCurrentPage}
              />
            )}
          </SectionCard>
        </div>
      )}

      {/* ── Competencies ──────────────────────────────────────────────────── */}
      {activeTab === 'competencies' && (
        <div className="animate-fade-up">
          {skillsError && <ErrorBanner message={skillsError} onRetry={refetchSkills} />}
          <SectionCard
            title="FRAC Competencies"
            subtitle={`${filteredSkills.length} of ${skills.length} competencies loaded · the dictionary is ministry-wide, so the department / grade / office filters don't apply`}
            padded={false}
            action={
              <button
                type="button"
                onClick={exportCompetencies}
                disabled={filteredSkills.length === 0}
                className="flex items-center gap-2 rounded-lg border border-gov-line px-3.5 py-2 text-[12.5px] font-semibold text-slate-600 transition-colors hover:border-gov-blue/40 hover:text-gov-navy disabled:opacity-50 dark:border-slate-600 dark:text-slate-300 dark:hover:text-white"
              >
                <Download size={14} /> Export CSV
              </button>
            }
          >
            <div className="overflow-x-auto">
              <table className="gov-table min-w-[720px]">
                <thead>
                  <tr>
                    <th scope="col">Competency ID</th>
                    <th scope="col">Name</th>
                    <th scope="col">Category</th>
                    <th scope="col">Description</th>
                  </tr>
                </thead>
                <tbody>
                  {isSkillsLoading ? (
                    <TableSkeleton cols={4} />
                  ) : currentSkills.length > 0 ? (
                    currentSkills.map((skill) => <SkillTableRow key={skill.competency_id} skill={skill} />)
                  ) : (
                    <tr>
                      <td colSpan={4} className="py-12 text-center text-slate-400">
                        {skills.length === 0 ? 'No competencies loaded — check the mock iGOT server.' : 'No competencies match your search.'}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {!isSkillsLoading && filteredSkills.length > 0 && (
              <Pagination
                page={currentPage} totalPages={totalPagesSkills} totalItems={filteredSkills.length}
                noun="competencies" onChange={setCurrentPage}
              />
            )}
          </SectionCard>
        </div>
      )}

      {/* ── Analytics ─────────────────────────────────────────────────────── */}
      {activeTab === 'analytics' && (
        <div className="animate-fade-up space-y-5">
          {filterBar()}
          {overview.error && <ErrorBanner message={overview.error} onRetry={overview.refetch} />}

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <StatCard index={0} icon={CheckCircle2} tone="green" label="Compliant" value={statusCounts.compliant} />
            <StatCard index={1} icon={TrendingUp} tone="orange" label="In Progress" value={statusCounts.inProgress} />
            <StatCard index={2} icon={AlertTriangle} tone="rose" label="Training Required" value={statusCounts.required} />
          </div>

          <TrendsPanel filters={filters} />

          <SectionCard
            title="Competency Shortage Index"
            subtitle="Top deficiencies weighted by status (planned ×1.5) and current level"
            action={<div className="flex gap-2">{exportButtons('shortages')}</div>}
          >
            {shortageChart(330)}
          </SectionCard>

          <SectionCard
            title="Compliance by Department"
            subtitle="Every department with 5+ officials in view (smaller ones are suppressed)"
            action={<div className="flex gap-2">{exportButtons('departments')}</div>}
          >
            {deptChart(330)}
          </SectionCard>
        </div>
      )}

      {/* ── Emerging skills ──────────────────────────────────────────────── */}
      {activeTab === 'emerging' && <EmergingSkills filters={filters} filterText={filterText} />}

      {/* ── Actions ──────────────────────────────────────────────────────── */}
      {activeTab === 'actions' && (
        <div className="space-y-5">
          <AdminActions filters={filters} facets={facets.data} filterText={filterText} />
          <CertificateReviewQueue />
        </div>
      )}

      {/* ── Insights (SCIL v6) ─────────────────────────────────────────────── */}
      {activeTab === 'insights' && <WorkforceInsights office={filters.office} />}

      {/* ── Reports ───────────────────────────────────────────────────────── */}
      {activeTab === 'reports' && (
        <div className="animate-fade-up grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
          {([
            { kind: 'roster', title: 'Officials Roster', icon: Users, tone: 'bg-accent-blue-soft text-accent-blue dark:bg-blue-500/15 dark:text-blue-300',
              desc: 'Every official with grade, department, top missing skill, mandatory progress and training status. Uses the Officials search and status chip too.' },
            { kind: 'mandatory-behind', title: 'Behind on Mandatory Training', icon: BellRing, tone: 'bg-accent-orange-soft text-accent-orange dark:bg-orange-500/15 dark:text-orange-300',
              desc: 'Officials with pending APAR-linked ACBP courses this cycle, the courses pending and when they were last nudged.' },
            { kind: 'emerging-skills', title: 'Emerging Skills', icon: Sparkles, tone: 'bg-accent-purple-soft text-accent-purple dark:bg-violet-500/15 dark:text-violet-300',
              desc: 'Required vs supply vs 36-month forecast per competency, ranked — the NSSTA "train next year" list.' },
            { kind: 'trends', title: 'Workforce Trends', icon: LineChartIcon, tone: 'bg-accent-green-soft text-accent-green dark:bg-emerald-500/15 dark:text-emerald-300',
              desc: 'Daily snapshots: compliance, mandatory completion, average competency level and share at target.' },
            { kind: 'departments', title: 'Department Compliance', icon: Building2, tone: 'bg-gov-navy/[0.08] text-gov-navy dark:bg-sky-500/15 dark:text-sky-300',
              desc: 'Headcount, compliance and mandatory completion per department; small departments are suppressed.' },
            { kind: 'shortages', title: 'Shortage Index', icon: BarChart3, tone: 'bg-accent-rose-soft text-accent-rose dark:bg-rose-500/15 dark:text-rose-300',
              desc: 'Aggregate competency shortage scores — the data behind the analytics bar chart.' },
          ] as const).map(({ kind, title, icon: Icon, tone, desc }, i) => (
            <div key={kind} className="panel animate-fade-up flex flex-col p-5" style={{ animationDelay: `${i * 70}ms` }}>
              <span className={`mb-3.5 flex h-11 w-11 items-center justify-center rounded-xl ${tone}`}>
                <Icon size={20} aria-hidden="true" />
              </span>
              <h3 className="mb-1.5 text-[14.5px] font-semibold text-gov-ink dark:text-white">{title}</h3>
              <p className="mb-4 flex-1 text-[12.5px] leading-relaxed text-slate-500 dark:text-slate-400">{desc}</p>
              <p className="mb-3 text-[11.5px] font-medium text-slate-400">{filterText}</p>
              <div className="flex gap-2">
                <ExportButton label="Download CSV" icon={Download}
                              onClick={() => csv(kind, kind === 'roster' ? rosterExtra : kind === 'trends' ? { days: 365 } : {})} />
                <ExportButton label="PDF" icon={FileText} onClick={() => pdf(kind)} />
              </div>
            </div>
          ))}
        </div>
      )}
    </AppShell>
  );
};

export default AdminDashboard;
