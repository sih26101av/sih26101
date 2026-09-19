/**
 * FILE: src/components/admin/AdminActions.tsx
 *
 * Admin write actions (routers/admin_console.py):
 *  • Assign a training plan — courses from the catalogue, to a department
 *    (narrowed by the current grade / office filters) or to officials selected
 *    in the mandatory-training table. Progress is tracked from iGOT completions.
 *  • Nudge officials behind on mandatory (ACBP) training — the selected ones,
 *    or everyone behind within the current filters. A 24 h cooldown per
 *    official is enforced by the server.
 * Assignments and nudges are stored in the LMS DB and served to the learner at
 * GET /api/v1/learner/{userId}/training-actions.
 */

import React from 'react';
import { BellRing, CheckCircle2, Download, FileText, Plus, Search, Send, X } from 'lucide-react';

import SectionCard from '../shell/SectionCard';
import { filterKey, useAsync } from '../../hooks/useAdminData';
import {
  createAssignment, downloadAdminCsv, fetchAssignments, fetchMandatoryBehind, fetchNudgeLog,
  searchCatalogueCourses, sendNudges,
  type AdminFacets, type AdminFilters, type CatalogueCourse, type NudgeResult,
} from '../../services/api';
import { ExportButton } from './AdminFilterBar';
import { printReport } from './adminReport';

const PAGE = 10;
const INPUT =
  'w-full rounded-lg border border-gov-line bg-white px-3 py-2 text-[12.5px] text-slate-700 ' +
  'dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200';
const LABEL = 'mb-1 block text-[11.5px] font-semibold text-slate-600 dark:text-slate-300';

const when = (iso: string | null) => (iso ? new Date(iso).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' }) : '—');

// ─── Assign a training plan ───────────────────────────────────────────────────

const AssignForm: React.FC<{
  filters: AdminFilters; facets: AdminFacets | null; selected: string[]; onDone: () => void;
}> = ({ filters, facets, selected, onDone }) => {
  const [title, setTitle] = React.useState('');
  const [scope, setScope] = React.useState<'department' | 'officials'>('department');
  const [department, setDepartment] = React.useState(filters.department ?? '');
  const [dueDate, setDueDate] = React.useState('');
  const [note, setNote] = React.useState('');
  const [q, setQ] = React.useState('');
  const [debounced, setDebounced] = React.useState('');
  const [courses, setCourses] = React.useState<CatalogueCourse[]>([]);
  const [busy, setBusy] = React.useState(false);
  const [msg, setMsg] = React.useState<{ ok: boolean; text: string } | null>(null);

  React.useEffect(() => { if (filters.department) setDepartment(filters.department); }, [filters.department]);
  React.useEffect(() => { const t = setTimeout(() => setDebounced(q), 300); return () => clearTimeout(t); }, [q]);
  const results = useAsync(() => (debounced.trim().length >= 2
    ? searchCatalogueCourses(debounced) : Promise.resolve({ courses: [], total: 0 })), `course|${debounced}`);

  const narrowing = [filters.grade && 'grade', filters.office && 'office'].filter(Boolean).join(' and ');
  const canSubmit = title.trim().length >= 3 && courses.length > 0
    && (scope === 'department' ? Boolean(department) : selected.length > 0);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setMsg(null);
    try {
      const out = await createAssignment({
        title: title.trim(), scope, courseIds: courses.map((c) => c.courseId),
        dueDate: dueDate || undefined, note: note.trim() || undefined,
        ...(scope === 'department'
          ? { department, grade: filters.grade, office: filters.office }
          : { userIds: selected }),
      });
      setMsg({ ok: true, text: `Assigned “${out.title}” to ${out.assignees} official(s).` });
      setTitle(''); setCourses([]); setNote(''); setDueDate('');
      onDone();
    } catch (err) {
      setMsg({ ok: false, text: err instanceof Error ? err.message : 'Assignment failed' });
    } finally {
      setBusy(false);
    }
  };

  return (
    <SectionCard title="Assign a training plan" subtitle="Courses from the iGOT catalogue, to a department or selected officials">
      <form onSubmit={submit} className="space-y-3.5">
        <div>
          <label className={LABEL} htmlFor="plan-title">Plan name</label>
          <input id="plan-title" className={INPUT} value={title} onChange={(e) => setTitle(e.target.value)}
                 placeholder="e.g. CPI base revision readiness, FY2026-27" maxLength={160} />
        </div>

        <fieldset>
          <legend className={LABEL}>Assign to</legend>
          <div className="flex flex-wrap gap-2">
            {(['department', 'officials'] as const).map((s) => (
              <button key={s} type="button" aria-pressed={scope === s} onClick={() => setScope(s)} className="chip-filter">
                {s === 'department' ? 'A department' : `Selected officials (${selected.length})`}
              </button>
            ))}
          </div>
          {scope === 'department' ? (
            <>
              <select aria-label="Department" className={`${INPUT} mt-2`} value={department} onChange={(e) => setDepartment(e.target.value)}>
                <option value="">Choose a department…</option>
                {facets?.departments.map((d) => <option key={d.value} value={d.value}>{d.label} ({d.count})</option>)}
              </select>
              {narrowing && <p className="mt-1 text-[11px] text-slate-400">Narrowed by the current {narrowing} filter.</p>}
            </>
          ) : (
            <p className="mt-2 text-[11.5px] text-slate-500 dark:text-slate-400">
              {selected.length ? `${selected.length} official(s) ticked in the mandatory-training table.`
                : 'Tick officials in the mandatory-training table first.'}
            </p>
          )}
        </fieldset>

        <div>
          <label className={LABEL} htmlFor="course-q">Courses</label>
          <div className="relative">
            <Search size={14} className="pointer-events-none absolute left-3 top-2.5 text-slate-400" aria-hidden="true" />
            <input id="course-q" className={`${INPUT} pl-8`} value={q} onChange={(e) => setQ(e.target.value)}
                   placeholder="Search by title or competency (2+ letters)" />
          </div>
          {results.data && results.data.courses.length > 0 && (
            <ul className="mt-1.5 max-h-44 overflow-y-auto rounded-lg border border-gov-line dark:border-slate-700">
              {results.data.courses.filter((c) => !courses.some((x) => x.courseId === c.courseId)).map((c) => (
                <li key={c.courseId}>
                  <button type="button" onClick={() => setCourses((cs) => [...cs, c].slice(0, 25))}
                          className="flex w-full items-start gap-2 px-3 py-2 text-left text-[12px] hover:bg-slate-50 dark:hover:bg-slate-800">
                    <Plus size={13} className="mt-0.5 shrink-0 text-gov-blue" aria-hidden="true" />
                    <span className="min-w-0">
                      <span className="block font-medium text-gov-ink dark:text-white">{c.title}</span>
                      <span className="block text-[11px] text-slate-400">{c.hours ?? '?'} h · {c.competencies.join(', ')}</span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
          {courses.length > 0 && (
            <ul className="mt-2 flex flex-wrap gap-1.5">
              {courses.map((c) => (
                <li key={c.courseId} className="chip bg-accent-blue-soft text-accent-blue dark:bg-blue-500/15 dark:text-blue-300">
                  {c.title}
                  <button type="button" aria-label={`Remove ${c.title}`} onClick={() => setCourses((cs) => cs.filter((x) => x.courseId !== c.courseId))}>
                    <X size={11} />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div>
            <label className={LABEL} htmlFor="due">Due date (optional)</label>
            <input id="due" type="date" className={INPUT} value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
          </div>
          <div>
            <label className={LABEL} htmlFor="note">Note (optional)</label>
            <input id="note" className={INPUT} value={note} onChange={(e) => setNote(e.target.value)} maxLength={500} />
          </div>
        </div>

        {msg && (
          <p className={`text-[12px] ${msg.ok ? 'text-accent-green' : 'text-rose-600 dark:text-rose-400'}`}>{msg.text}</p>
        )}
        <button type="submit" disabled={!canSubmit || busy} className="gov-btn-primary w-full disabled:opacity-50">
          <Send size={14} /> {busy ? 'Assigning…' : 'Assign plan'}
        </button>
      </form>
    </SectionCard>
  );
};

// ─── Main ─────────────────────────────────────────────────────────────────────

const AdminActions: React.FC<{ filters: AdminFilters; facets: AdminFacets | null; filterText: string }> = ({
  filters, facets, filterText,
}) => {
  const [page, setPage] = React.useState(1);
  const [selected, setSelected] = React.useState<string[]>([]);
  const [message, setMessage] = React.useState('');
  const [sending, setSending] = React.useState(false);
  const [result, setResult] = React.useState<NudgeResult | null>(null);
  const [version, setVersion] = React.useState(0);
  const fk = filterKey(filters);

  React.useEffect(() => { setPage(1); setSelected([]); }, [fk]);
  const behind = useAsync(() => fetchMandatoryBehind(filters, page, PAGE), `${fk}|${page}|${version}`);
  const assignments = useAsync(fetchAssignments, `assign|${version}`);
  const log = useAsync(() => fetchNudgeLog(15), `log|${version}`);
  const bump = () => setVersion((v) => v + 1);

  const rows = behind.data?.items ?? [];
  const total = behind.data?.total ?? 0;
  const toggle = (id: string) => setSelected((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]));
  const allOnPage = rows.length > 0 && rows.every((r) => selected.includes(r.userId));

  const nudge = async (userIds?: string[]) => {
    if (!userIds && !confirm(`Nudge all ${total} official(s) behind on mandatory training within the current filters?`)) return;
    setSending(true);
    setResult(null);
    try {
      setResult(await sendNudges({ ...filters, userIds, message: message.trim() || undefined }));
      setSelected([]);
      bump();
    } catch (e) {
      setResult({ sent: 0, skipped: [], message: e instanceof Error ? e.message : 'Nudge failed' });
    } finally {
      setSending(false);
    }
  };

  const exportPdf = async () => {
    const all = await fetchMandatoryBehind(filters, 1, 200);
    printReport('Officials behind on mandatory training', filterText, [{
      heading: `${all.total} official(s) with pending ACBP courses`,
      note: all.total > 200 ? 'First 200 rows — use the CSV export for the full list.' : undefined,
      columns: ['Gov ID', 'Name', 'Department', 'Grade', 'Done', 'Pending courses', 'Last nudged'],
      rows: all.items.map((r) => [r.govId, r.name, r.department, r.gradeLabel, `${r.completed}/${r.total}`,
        r.pending.map((p) => p.title).join('; '), r.lastNudgedAt ? when(r.lastNudgedAt) : '—']),
    }]);
  };

  const m = behind.data?.summary;

  return (
    <div className="animate-fade-up space-y-5">
      <div className="grid grid-cols-1 items-start gap-5 xl:grid-cols-5">
        <div className="xl:col-span-2">
          <AssignForm filters={filters} facets={facets} selected={selected} onDone={bump} />
        </div>

        <div className="xl:col-span-3">
          <SectionCard
            title="Behind on mandatory training"
            subtitle={m ? `${m.behind} of ${m.officialsWithPlan} officials · ${m.coursesCompleted}/${m.coursesAssigned} ACBP courses done (${m.completionPct ?? 0}%)` : 'APAR-linked ACBP courses this cycle'}
            padded={false}
            action={
              <div className="flex gap-2">
                <ExportButton label="CSV" icon={Download} disabled={!total} onClick={() => downloadAdminCsv('mandatory-behind', filters)} />
                <ExportButton label="PDF" icon={FileText} disabled={!total} onClick={exportPdf} />
              </div>
            }
          >
            <div className="space-y-2 px-5 pb-3">
              <textarea
                aria-label="Nudge message"
                className={`${INPUT} h-16 resize-none`}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                maxLength={500}
                placeholder="Message (optional) — default: a reminder that mandatory ACBP courses are pending."
              />
              <div className="flex flex-wrap items-center gap-2">
                <button type="button" disabled={!selected.length || sending} onClick={() => nudge(selected)}
                        className="gov-btn-primary disabled:opacity-50">
                  <BellRing size={14} /> Nudge selected ({selected.length})
                </button>
                <button type="button" disabled={!total || sending} onClick={() => nudge()}
                        className="rounded-lg border border-gov-line px-3.5 py-2 text-[12.5px] font-semibold text-slate-600 hover:text-gov-navy disabled:opacity-50 dark:border-slate-600 dark:text-slate-300 dark:hover:text-white">
                  Nudge all {total} in view
                </button>
                {result && (
                  <span className="text-[12px] text-slate-600 dark:text-slate-300">
                    <CheckCircle2 size={13} className="mr-1 inline text-accent-green" aria-hidden="true" />
                    Sent {result.sent}{result.skipped.length ? ` · skipped ${result.skipped.length} (nudged in the last 24 h or not behind)` : ''}
                  </span>
                )}
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="gov-table min-w-[760px]">
                <thead>
                  <tr>
                    <th scope="col" className="w-8">
                      <input type="checkbox" aria-label="Select all on this page" checked={allOnPage}
                             onChange={() => setSelected((s) => (allOnPage
                               ? s.filter((id) => !rows.some((r) => r.userId === id))
                               : [...new Set([...s, ...rows.map((r) => r.userId)])]))} />
                    </th>
                    <th scope="col">Official</th>
                    <th scope="col">Department · grade</th>
                    <th scope="col">Done</th>
                    <th scope="col">Pending</th>
                    <th scope="col">Last nudged</th>
                  </tr>
                </thead>
                <tbody>
                  {behind.isLoading && !behind.data && (
                    <tr><td colSpan={6} className="py-10 text-center text-slate-400">Loading…</td></tr>
                  )}
                  {behind.error && (
                    <tr><td colSpan={6} className="py-10 text-center text-rose-600">{behind.error}</td></tr>
                  )}
                  {rows.map((r) => (
                    <tr key={r.userId}>
                      <td><input type="checkbox" aria-label={`Select ${r.name}`} checked={selected.includes(r.userId)} onChange={() => toggle(r.userId)} /></td>
                      <td>
                        <span className="block font-semibold text-gov-ink dark:text-white">{r.name}</span>
                        <span className="text-[11px] text-slate-400">{r.govId} · {r.designation}</span>
                      </td>
                      <td className="text-[12px] text-slate-500 dark:text-slate-400">{r.department}<br />{r.gradeLabel}</td>
                      <td className="tabular-nums">{r.completed}/{r.total}</td>
                      <td className="max-w-xs text-[12px]">{r.pending.map((p) => p.title).join('; ')}</td>
                      <td className="whitespace-nowrap text-[12px] text-slate-500">{when(r.lastNudgedAt)}</td>
                    </tr>
                  ))}
                  {behind.data && rows.length === 0 && (
                    <tr><td colSpan={6} className="py-10 text-center text-slate-400">Nobody in this view is behind on mandatory training.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
            {behind.data && behind.data.totalPages > 1 && (
              <div className="flex items-center justify-between border-t border-gov-line px-5 py-3 text-[12px] text-slate-500 dark:border-slate-800">
                <span>Page {behind.data.page} of {behind.data.totalPages} · {total} officials</span>
                <span className="flex gap-2">
                  <button type="button" className="chip-filter" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Previous</button>
                  <button type="button" className="chip-filter" disabled={page >= behind.data.totalPages} onClick={() => setPage((p) => p + 1)}>Next</button>
                </span>
              </div>
            )}
          </SectionCard>
        </div>
      </div>

      <div className="grid grid-cols-1 items-start gap-5 xl:grid-cols-2">
        <SectionCard title="Assigned training plans" subtitle="Completion tracked from iGOT course completions">
          {assignments.error && <p className="text-[12.5px] text-rose-600">{assignments.error}</p>}
          <ul className="space-y-3">
            {(assignments.data?.assignments ?? []).map((a) => (
              <li key={a.assignmentId} className="rounded-xl border border-gov-line p-3 dark:border-slate-700">
                <div className="flex items-start justify-between gap-2">
                  <span className="min-w-0">
                    <span className="block text-[13px] font-semibold text-gov-ink dark:text-white">{a.title}</span>
                    <span className="block text-[11px] text-slate-400">
                      {a.scope === 'department' ? a.department : 'Selected officials'} · {a.assignees} official(s) · {a.courses.length} course(s)
                      {a.dueDate ? ` · due ${a.dueDate}` : ''} · by {a.createdBy}
                    </span>
                  </span>
                  {a.overdue && <span className="chip bg-accent-rose-soft text-accent-rose dark:bg-rose-500/15 dark:text-rose-300">Overdue</span>}
                </div>
                <div className="mt-2 flex items-center gap-2">
                  <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700"
                       role="progressbar" aria-valuenow={a.progress.completionPct} aria-valuemin={0} aria-valuemax={100}>
                    <div className="h-full rounded-full bg-accent-green" style={{ width: `${a.progress.completionPct}%` }} />
                  </div>
                  <span className="text-[11px] tabular-nums text-slate-500">
                    {a.progress.completedAll}/{a.assignees} finished ({a.progress.completionPct}%)
                  </span>
                </div>
              </li>
            ))}
            {assignments.data && assignments.data.assignments.length === 0 && (
              <li className="py-6 text-center text-[12.5px] text-slate-400">No plans assigned yet.</li>
            )}
          </ul>
        </SectionCard>

        <SectionCard title="Recent nudges" subtitle="Reminders sent to officials (visible to them on their training-actions feed)">
          {log.error && <p className="text-[12.5px] text-rose-600">{log.error}</p>}
          <ul className="divide-y divide-gov-line dark:divide-slate-800">
            {(log.data?.nudges ?? []).map((n) => (
              <li key={n.nudgeId} className="flex items-start gap-3 py-2.5">
                <BellRing size={14} className="mt-0.5 shrink-0 text-accent-orange" aria-hidden="true" />
                <span className="min-w-0 flex-1">
                  <span className="block text-[12.5px] font-semibold text-gov-ink dark:text-white">{n.name}</span>
                  <span className="block truncate text-[11px] text-slate-400">{n.department} · {n.pendingCourses.length} pending · by {n.createdBy}</span>
                </span>
                <span className="text-right text-[11px] text-slate-400">
                  {when(n.createdAt)}<br />{n.readAt ? 'Read' : 'Unread'}
                </span>
              </li>
            ))}
            {log.data && log.data.nudges.length === 0 && (
              <li className="py-6 text-center text-[12.5px] text-slate-400">No nudges sent yet.</li>
            )}
          </ul>
        </SectionCard>
      </div>
    </div>
  );
};

export default AdminActions;
