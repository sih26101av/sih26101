/**
 * FILE: src/pages/AdminDashboard.tsx
 *
 * Ministry-side dashboard at /admin (role `admin` only).
 *
 * Sections: overview · officials · competencies · analytics · reports.
 * Every figure comes from `useAdminData` (roster → KPIs + shortage heatmap) and
 * `useSkillsData` (FRAC dictionary). The previous version fell back to invented
 * numbers (151 officials, 87% compliance, a static bar chart and a "25k" donut)
 * whenever the API was empty — those are gone; empty data now reads as empty.
 */

import React, { useEffect, useMemo, useState } from 'react';
import {
  Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import {
  AlertTriangle, BarChart3, BookOpen, CheckCircle2, ChevronLeft, ChevronRight,
  Database, Download, FileText, LayoutDashboard, RefreshCcw, ShieldCheck,
  SlidersHorizontal, TrendingUp, Users,
} from 'lucide-react';

import { useTheme } from '../hooks/useTheme';
import { useAdminData } from '../hooks/useAdminData';
import type { AdminRosterRow } from '../hooks/useAdminData';
import { useSkillsData } from '../hooks/useSkillsData';
import type { SkillRow } from '../hooks/useSkillsData';

import AppShell, { type ShellNavGroup } from '../components/shell/AppShell';
import PageHeader from '../components/shell/PageHeader';
import SectionCard, { SectionAction } from '../components/shell/SectionCard';
import StatCard from '../components/shell/StatCard';
import { AshokaChakra } from '../components/gov/GovUI';

type AdminTab = 'dashboard' | 'officials' | 'competencies' | 'analytics' | 'reports';

const ITEMS_PER_PAGE = 10;

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

/** Download rows as a CSV file, quoting every cell. */
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
  return (
    <tr>
      <td>
        <span className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gov-navy/10 text-[11px] font-bold text-gov-navy dark:bg-sky-500/15 dark:text-sky-300">
            {name.charAt(0).toUpperCase()}
          </span>
          <span className="min-w-0">
            <span className="block truncate font-semibold text-gov-ink dark:text-white">{name}</span>
            <span className="block truncate text-[11px] text-slate-400">{employee.email || employee.userId}</span>
          </span>
        </span>
      </td>
      <td className="whitespace-nowrap text-slate-500 dark:text-slate-400">{employee.govId ?? employee.userId}</td>
      <td className="text-slate-500 dark:text-slate-400">{employee.designation}</td>
      <td className="text-slate-500 dark:text-slate-400">{employee.department}</td>
      <td className="font-medium">{employee.missingSkill ?? '—'}</td>
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

/** Live status of one data feed — reflects the actual hook state, nothing simulated. */
const FeedStatus: React.FC<{ label: string; endpoint: string; loading: boolean; error: string | null; count: number }> = ({
  label, endpoint, loading, error, count,
}) => {
  const tone = error ? 'rose' : loading ? 'orange' : 'green';
  const text = error ? 'Unavailable' : loading ? 'Loading…' : `${count} records`;
  return (
    <li className="flex items-center gap-3">
      <span
        className={`h-2.5 w-2.5 flex-shrink-0 rounded-full ${
          tone === 'green' ? 'bg-accent-green' : tone === 'orange' ? 'animate-pulse bg-accent-orange' : 'bg-accent-rose'
        }`}
        aria-hidden="true"
      />
      <span className="min-w-0 flex-1">
        <span className="block text-[12.5px] font-semibold text-gov-ink dark:text-white">{label}</span>
        <span className="block truncate font-mono text-[10.5px] text-slate-400">{endpoint}</span>
      </span>
      <span className={`chip ${tone === 'green' ? STATUS_CHIP['Compliant'] : tone === 'orange' ? STATUS_CHIP['In Progress'] : STATUS_CHIP['Training Required']}`}>
        {text}
      </span>
    </li>
  );
};

// ─── Main ─────────────────────────────────────────────────────────────────────
const AdminDashboard: React.FC = () => {
  const { theme } = useTheme();
  const { roster, kpis, heatmap, isLoading, error, refetch } = useAdminData();
  const { skills, isLoading: isSkillsLoading, error: skillsError, refetch: refetchSkills } = useSkillsData();

  const [activeTab, setActiveTab] = useState<AdminTab>('dashboard');
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<'all' | 0 | 1 | 2>('all');

  useEffect(() => { setCurrentPage(1); }, [searchTerm, activeTab, statusFilter]);

  const isDark = theme === 'dark';
  const axisColor = isDark ? '#94a3b8' : '#64748b';
  const gridColor = isDark ? '#334155' : '#e2e8f0';

  // ── Roster filtering / pagination ──────────────────────────────────────────
  const filteredRoster = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    return roster.filter((emp) => {
      const matchesStatus = statusFilter === 'all' || emp.enrollmentStatus === statusFilter;
      if (!matchesStatus) return false;
      if (!q) return true;
      return (
        `${emp.firstName} ${emp.lastName}`.toLowerCase().includes(q) ||
        (emp.govId ?? emp.userId).toLowerCase().includes(q) ||
        (emp.department ?? '').toLowerCase().includes(q) ||
        (emp.designation ?? '').toLowerCase().includes(q)
      );
    });
  }, [roster, searchTerm, statusFilter]);

  const totalPagesRoster = Math.max(1, Math.ceil(filteredRoster.length / ITEMS_PER_PAGE));
  const currentRoster = useMemo(
    () => filteredRoster.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE),
    [filteredRoster, currentPage],
  );

  // ── FRAC filtering / pagination ────────────────────────────────────────────
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

  // ── Derived analytics (all from the live roster) ───────────────────────────
  const statusCounts = useMemo(() => {
    const counts = { compliant: 0, inProgress: 0, required: 0 };
    roster.forEach((r) => {
      if (r.enrollmentStatus === 2) counts.compliant += 1;
      else if (r.enrollmentStatus === 1) counts.inProgress += 1;
      else counts.required += 1;
    });
    return counts;
  }, [roster]);

  /** Completion rate per department, biggest departments first. */
  const deptCompliance = useMemo(() => {
    const byDept = new Map<string, { total: number; done: number }>();
    roster.forEach((r) => {
      const key = r.department || 'Unspecified';
      const cur = byDept.get(key) ?? { total: 0, done: 0 };
      cur.total += 1;
      if (r.enrollmentStatus === 2) cur.done += 1;
      byDept.set(key, cur);
    });
    return [...byDept.entries()]
      .sort((a, b) => b[1].total - a[1].total)
      .slice(0, 5)
      .map(([dept, v], i) => ({
        dept: dept.length > 18 ? `${dept.slice(0, 18)}…` : dept,
        pct: Math.round((v.done / v.total) * 100),
        headcount: v.total,
        color: ['#0b2a55', '#f97316', '#10b981', '#8b5cf6', '#60a5fa'][i % 5],
      }));
  }, [roster]);

  const needsTraining = useMemo(
    () => roster.filter((r) => r.enrollmentStatus === 0).slice(0, 5),
    [roster],
  );

  // ── Exports ────────────────────────────────────────────────────────────────
  const exportRoster = () =>
    downloadCsv(
      `nso-officials-roster-${new Date().toISOString().slice(0, 10)}.csv`,
      ['Gov ID', 'User ID', 'First Name', 'Last Name', 'Email', 'Designation', 'Department', 'Top Missing Skill', 'Status'],
      filteredRoster.map((r) => [
        r.govId, r.userId, r.firstName, r.lastName, r.email,
        r.designation, r.department, r.missingSkill ?? '', enrollmentLabel(r.enrollmentStatus),
      ]),
    );

  const exportCompetencies = () =>
    downloadCsv(
      `frac-competencies-${new Date().toISOString().slice(0, 10)}.csv`,
      ['Competency ID', 'Name', 'Category', 'Description'],
      filteredSkills.map((s) => [s.competency_id, s.name, s.category, s.description]),
    );

  const exportShortages = () =>
    downloadCsv(
      `competency-shortage-index-${new Date().toISOString().slice(0, 10)}.csv`,
      ['Competency', 'Shortage Index'],
      heatmap.map((h) => [h.competency, h.gap]),
    );

  // ── Nav ────────────────────────────────────────────────────────────────────
  const navGroups: ShellNavGroup[] = [
    {
      items: [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { id: 'officials', label: 'Officials', icon: Users, badge: roster.length || undefined },
        { id: 'competencies', label: 'Competencies', icon: BookOpen, badge: skills.length || undefined },
        { id: 'analytics', label: 'Analytics', icon: BarChart3 },
        { id: 'reports', label: 'Reports', icon: FileText },
      ],
    },
  ];

  const META: Record<AdminTab, { title: string; subtitle: string }> = {
    dashboard:    { title: 'Admin Dashboard',  subtitle: 'Monitor platform usage, track training progress and drive capability development.' },
    officials:    { title: 'Officials',        subtitle: 'The full NSO roster with competency status from iGOT Karmayogi.' },
    competencies: { title: 'FRAC Competencies',subtitle: 'The competency dictionary that every skill gap is measured against.' },
    analytics:    { title: 'Analytics',        subtitle: 'Shortage concentration and departmental training compliance.' },
    reports:      { title: 'Reports',          subtitle: 'Export the current view as CSV for offline analysis.' },
  };

  // ── Shortage bar chart (real heatmap from useAdminData) ────────────────────
  const shortageChart = (height = 300) => (
    heatmap.length === 0 ? (
      <p className="py-14 text-center text-[13px] text-slate-400">
        {isLoading ? 'Loading shortage data…' : 'No competency shortages recorded in the roster.'}
      </p>
    ) : (
      <div style={{ height }} className="w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={heatmap} margin={{ top: 10, right: 10, left: -18, bottom: 16 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={gridColor} />
            <XAxis dataKey="competency" axisLine={false} tickLine={false} tick={{ fill: axisColor, fontSize: 11 }} dy={8} interval={0} />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: axisColor, fontSize: 11 }} />
            <Tooltip
              cursor={{ fill: 'transparent' }}
              formatter={(v) => [String(v), 'Shortage index'] as [string, string]}
              contentStyle={{ borderRadius: 10, fontSize: 12, border: `1px solid ${gridColor}`, background: isDark ? '#0f172a' : '#fff' }}
            />
            <Bar dataKey="gap" radius={[6, 6, 0, 0]} barSize={42}>
              {heatmap.map((entry, i) => <Cell key={i} fill={entry.color[0]} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    )
  );

  const deptChart = (height = 300) => (
    deptCompliance.length === 0 ? (
      <p className="py-14 text-center text-[13px] text-slate-400">
        {isLoading ? 'Loading roster…' : 'No departmental data available.'}
      </p>
    ) : (
      <div style={{ height }} className="w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={deptCompliance} margin={{ top: 18, right: 10, left: -18, bottom: 16 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={gridColor} />
            <XAxis dataKey="dept" axisLine={false} tickLine={false} tick={{ fill: axisColor, fontSize: 11 }} dy={8} interval={0} />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: axisColor, fontSize: 11 }} domain={[0, 100]} unit="%" />
            <Tooltip
              cursor={{ fill: 'transparent' }}
              formatter={(v, _n, item: any) => [`${v}% of ${item?.payload?.headcount} officials`, 'Compliant'] as [string, string]}
              contentStyle={{ borderRadius: 10, fontSize: 12, border: `1px solid ${gridColor}`, background: isDark ? '#0f172a' : '#fff' }}
            />
            <Bar dataKey="pct" radius={[6, 6, 0, 0]} barSize={42}>
              {deptCompliance.map((d, i) => <Cell key={i} fill={d.color} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    )
  );

  return (
    <AppShell
      groups={navGroups}
      activeId={activeTab}
      onNavigate={(id) => setActiveTab(id as AdminTab)}
      userName="Admin"
      userRole="System Administrator"
      notificationCount={statusCounts.required}
      onNotificationsClick={() => { setStatusFilter(0); setActiveTab('officials'); }}
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
            onClick={() => { refetch(); refetchSkills(); }}
            className="panel flex items-center gap-2 px-3.5 py-2 text-[12.5px] font-semibold text-slate-600 transition-colors hover:text-gov-navy dark:text-slate-300 dark:hover:text-white"
          >
            <RefreshCcw size={14} className={isLoading ? 'animate-spin' : ''} /> Refresh
          </button>
        }
      />

      {/* ── Overview ──────────────────────────────────────────────────────── */}
      {activeTab === 'dashboard' && (
        <div className="animate-fade-up space-y-5">
          {error && <ErrorBanner message={error} onRetry={refetch} />}

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard
              index={0} icon={Users} tone="blue" label="Total Officials" value={kpis.totalOfficials}
              caption="Tracked via iGOT Karmayogi" onClick={() => setActiveTab('officials')}
            />
            <StatCard
              index={1} icon={BookOpen} tone="orange" label="FRAC Competencies" value={skills.length}
              caption="In the competency dictionary" onClick={() => setActiveTab('competencies')}
            />
            <StatCard
              index={2} icon={ShieldCheck} tone="green" label="Training Compliance"
              value={`${kpis.trainingCompliancePct}%`} progress={kpis.trainingCompliancePct}
              caption={`${statusCounts.compliant} of ${roster.length || 0} officials compliant`}
            />
            <StatCard
              index={3} icon={AlertTriangle} tone="purple" label="Avg Missing Skills"
              value={kpis.avgMissingSkills} caption="Per official, planned or in progress"
              onClick={() => setActiveTab('analytics')}
            />
          </div>

          <div className="grid grid-cols-1 items-start gap-5 xl:grid-cols-2">
            <SectionCard
              title="Competency Shortage Index"
              subtitle="Weighted by deficiency level across the whole roster"
              action={<SectionAction label="Analytics" onClick={() => setActiveTab('analytics')} />}
            >
              {shortageChart(268)}
            </SectionCard>

            <SectionCard
              title="Compliance by Department"
              subtitle="Share of officials with at least one completed course"
              action={<SectionAction label="Officials" onClick={() => setActiveTab('officials')} />}
            >
              {deptChart(268)}
            </SectionCard>
          </div>

          <div className="grid grid-cols-1 items-start gap-5 xl:grid-cols-2">
            <SectionCard
              title="Officials Needing Training"
              subtitle="No course started yet"
              action={<SectionAction label="View all" onClick={() => { setStatusFilter(0); setActiveTab('officials'); }} />}
            >
              <ul className="space-y-3">
                {needsTraining.map((r) => (
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
                {needsTraining.length === 0 && (
                  <li className="py-8 text-center text-[13px] text-slate-400">
                    {isLoading ? 'Loading roster…' : 'Every official has started at least one course.'}
                  </li>
                )}
              </ul>
            </SectionCard>

            <SectionCard title="Data Sources" subtitle="Live status of the feeds behind this dashboard">
              <ul className="space-y-3.5">
                <FeedStatus label="Officials roster" endpoint="/api/v1/admin/users" loading={isLoading} error={error} count={roster.length} />
                <FeedStatus label="FRAC competencies" endpoint="/api/v1/admin/frac/competencies" loading={isSkillsLoading} error={skillsError} count={skills.length} />
              </ul>
              <div className="mt-4 flex items-center gap-2 rounded-xl border border-gov-line bg-gov-paper px-3.5 py-2.5 text-[11.5px] text-slate-500 dark:border-slate-700/60 dark:bg-slate-800/50 dark:text-slate-400">
                <Database size={14} className="flex-shrink-0 text-gov-blue dark:text-sky-400" aria-hidden="true" />
                Both feeds are proxied through the LMS backend on port 8000 with admin role enforcement.
              </div>
            </SectionCard>
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
                  <h3 className="mb-1 text-[15.5px] font-semibold">Empower a Data-Ready Workforce</h3>
                  <p className="max-w-xl text-[12.5px] leading-relaxed text-white/70">
                    Track progress, identify gaps and enable continuous learning across government.
                  </p>
                </div>
              </div>
              <button type="button" onClick={() => setActiveTab('reports')} className="gov-btn-saffron flex-shrink-0">
                Generate Report <Download size={15} />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Officials ─────────────────────────────────────────────────────── */}
      {activeTab === 'officials' && (
        <div className="animate-fade-up">
          {error && <ErrorBanner message={error} onRetry={refetch} />}
          <SectionCard
            title="Official Roster"
            subtitle={`${filteredRoster.length} of ${roster.length} officials`}
            padded={false}
            action={
              <button
                type="button"
                onClick={exportRoster}
                disabled={filteredRoster.length === 0}
                className="flex items-center gap-2 rounded-lg border border-gov-line px-3.5 py-2 text-[12.5px] font-semibold text-slate-600 transition-colors hover:border-gov-blue/40 hover:text-gov-navy disabled:opacity-50 dark:border-slate-600 dark:text-slate-300 dark:hover:text-white"
              >
                <Download size={14} /> Export CSV
              </button>
            }
          >
            {/* Status filters — replaces the old dead "Filters" button */}
            <div className="flex flex-wrap items-center gap-2 px-5 pb-4">
              <SlidersHorizontal size={14} className="text-slate-400" aria-hidden="true" />
              {([['all', 'All'], [2, 'Compliant'], [1, 'In Progress'], [0, 'Training Required']] as const).map(([value, label]) => (
                <button
                  key={String(value)}
                  type="button"
                  aria-pressed={statusFilter === value}
                  onClick={() => setStatusFilter(value as typeof statusFilter)}
                  className="chip-filter"
                >
                  {label}
                  {value !== 'all' && (
                    <span className="text-slate-400">
                      ({value === 2 ? statusCounts.compliant : value === 1 ? statusCounts.inProgress : statusCounts.required})
                    </span>
                  )}
                </button>
              ))}
            </div>

            <div className="overflow-x-auto">
              <table className="gov-table min-w-[860px]">
                <thead>
                  <tr>
                    <th scope="col">Official</th>
                    <th scope="col">Gov ID</th>
                    <th scope="col">Designation</th>
                    <th scope="col">Department</th>
                    <th scope="col">Top Missing Skill</th>
                    <th scope="col">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {isLoading ? (
                    <TableSkeleton cols={6} />
                  ) : currentRoster.length > 0 ? (
                    currentRoster.map((emp) => <RosterRow key={emp.userId} employee={emp} />)
                  ) : (
                    <tr>
                      <td colSpan={6} className="py-12 text-center text-slate-400">
                        {roster.length === 0 ? 'No officials loaded.' : 'No officials match the current search and filters.'}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {!isLoading && filteredRoster.length > 0 && (
              <Pagination
                page={currentPage} totalPages={totalPagesRoster} totalItems={filteredRoster.length}
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
            subtitle={`${filteredSkills.length} of ${skills.length} competencies loaded`}
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
          {error && <ErrorBanner message={error} onRetry={refetch} />}

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <StatCard index={0} icon={CheckCircle2} tone="green" label="Compliant" value={statusCounts.compliant} />
            <StatCard index={1} icon={TrendingUp} tone="orange" label="In Progress" value={statusCounts.inProgress} />
            <StatCard index={2} icon={AlertTriangle} tone="rose" label="Training Required" value={statusCounts.required} />
          </div>

          <SectionCard
            title="Competency Shortage Index"
            subtitle="Top deficiencies weighted by status (planned ×1.5) and current level"
            action={
              <button
                type="button"
                onClick={exportShortages}
                disabled={heatmap.length === 0}
                className="flex items-center gap-2 rounded-lg border border-gov-line px-3.5 py-2 text-[12.5px] font-semibold text-slate-600 transition-colors hover:border-gov-blue/40 hover:text-gov-navy disabled:opacity-50 dark:border-slate-600 dark:text-slate-300 dark:hover:text-white"
              >
                <Download size={14} /> Export
              </button>
            }
          >
            {shortageChart(330)}
          </SectionCard>

          <SectionCard title="Compliance by Department" subtitle="Five largest departments by headcount">
            {deptChart(330)}
          </SectionCard>
        </div>
      )}

      {/* ── Reports ───────────────────────────────────────────────────────── */}
      {activeTab === 'reports' && (
        <div className="animate-fade-up grid grid-cols-1 gap-5 md:grid-cols-3">
          {[
            {
              title: 'Officials Roster', icon: Users, tone: 'bg-accent-blue-soft text-accent-blue dark:bg-blue-500/15 dark:text-blue-300',
              desc: 'Every official with designation, department, top missing skill and training status. Respects the filters set on the Officials page.',
              count: filteredRoster.length, noun: 'rows', onExport: exportRoster,
            },
            {
              title: 'FRAC Competencies', icon: BookOpen, tone: 'bg-accent-orange-soft text-accent-orange dark:bg-orange-500/15 dark:text-orange-300',
              desc: 'The full competency dictionary with identifiers, categories and descriptions as served by the mock iGOT server.',
              count: filteredSkills.length, noun: 'rows', onExport: exportCompetencies,
            },
            {
              title: 'Shortage Index', icon: BarChart3, tone: 'bg-accent-purple-soft text-accent-purple dark:bg-violet-500/15 dark:text-violet-300',
              desc: 'Aggregate competency shortage scores computed across the roster — the data behind the analytics bar chart.',
              count: heatmap.length, noun: 'competencies', onExport: exportShortages,
            },
          ].map(({ title, icon: Icon, tone, desc, count, noun, onExport }, i) => (
            <div key={title} className="panel animate-fade-up flex flex-col p-5" style={{ animationDelay: `${i * 70}ms` }}>
              <span className={`mb-3.5 flex h-11 w-11 items-center justify-center rounded-xl ${tone}`}>
                <Icon size={20} aria-hidden="true" />
              </span>
              <h3 className="mb-1.5 text-[14.5px] font-semibold text-gov-ink dark:text-white">{title}</h3>
              <p className="mb-4 flex-1 text-[12.5px] leading-relaxed text-slate-500 dark:text-slate-400">{desc}</p>
              <p className="mb-3 text-[11.5px] font-medium text-slate-400">{count} {noun} ready</p>
              <button
                type="button"
                onClick={onExport}
                disabled={count === 0}
                className="gov-btn-primary w-full disabled:opacity-50"
              >
                <Download size={15} /> Download CSV
              </button>
            </div>
          ))}
        </div>
      )}
    </AppShell>
  );
};

export default AdminDashboard;
