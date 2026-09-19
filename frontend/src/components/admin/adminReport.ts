/**
 * FILE: src/components/admin/adminReport.ts
 *
 * PDF export for the admin console without a PDF library: builds a plain,
 * print-styled HTML report in a new window and opens the browser's print
 * dialog ("Save as PDF"). CSV exports are built on the server
 * (downloadAdminCsv in services/api.ts).
 */

import type { AdminFilters } from '../../services/api';

export interface ReportSection {
  heading: string;
  columns: string[];
  rows: (string | number | null | undefined)[][];
  note?: string;
}

const esc = (v: unknown) =>
  String(v ?? '—').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]!));

export function describeFilters(f: AdminFilters, labels: Partial<Record<keyof AdminFilters, string>> = {}): string {
  const parts = (['department', 'grade', 'office'] as const)
    .filter((k) => f[k])
    .map((k) => `${k[0].toUpperCase()}${k.slice(1)}: ${labels[k] ?? f[k]}`);
  return parts.length ? parts.join(' · ') : 'Whole NSO (no filters)';
}

/** Open a printable report; returns false if the pop-up was blocked. */
export function printReport(title: string, filterText: string, sections: ReportSection[]): boolean {
  const w = window.open('', '_blank', 'width=1000,height=800');
  if (!w) return false;
  const body = sections.map((s) => `
    <h2>${esc(s.heading)}</h2>
    ${s.note ? `<p class="note">${esc(s.note)}</p>` : ''}
    <table>
      <thead><tr>${s.columns.map((c) => `<th>${esc(c)}</th>`).join('')}</tr></thead>
      <tbody>${s.rows.length
        ? s.rows.map((r) => `<tr>${r.map((v) => `<td>${esc(v)}</td>`).join('')}</tr>`).join('')
        : `<tr><td colspan="${s.columns.length}">No rows.</td></tr>`}</tbody>
    </table>`).join('');
  w.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>${esc(title)}</title>
    <style>
      body { font: 11px/1.45 system-ui, -apple-system, 'Segoe UI', sans-serif; color: #0f172a; margin: 24px; }
      header { border-bottom: 2px solid #0b2a55; padding-bottom: 8px; margin-bottom: 16px; }
      h1 { font-size: 18px; margin: 0 0 2px; color: #0b2a55; }
      h2 { font-size: 13px; margin: 18px 0 6px; color: #0b2a55; }
      .meta, .note { color: #475569; margin: 2px 0; }
      table { border-collapse: collapse; width: 100%; page-break-inside: auto; }
      tr { page-break-inside: avoid; }
      th, td { border: 1px solid #cbd5e1; padding: 4px 6px; text-align: left; vertical-align: top; }
      th { background: #f1f5f9; font-weight: 600; }
      footer { margin-top: 20px; color: #64748b; font-size: 10px; }
      @page { margin: 14mm; }
    </style></head><body>
    <header>
      <h1>${esc(title)}</h1>
      <p class="meta">Ministry of Statistics and Programme Implementation · NSO skill intelligence console</p>
      <p class="meta">${esc(filterText)} · Generated ${esc(new Date().toLocaleString())}</p>
    </header>
    ${body}
    <footer>Computed on synthetic mock iGOT data — demo only. Counts of 1–4 officials are suppressed as “&lt;5”.</footer>
    <script>window.onload = () => { window.focus(); window.print(); };</script>
    </body></html>`);
  w.document.close();
  return true;
}
