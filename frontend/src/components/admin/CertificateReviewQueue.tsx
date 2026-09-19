/**
 * FILE: src/components/admin/CertificateReviewQueue.tsx
 *
 * Admin review of external certificates (routers/competency.py).
 * A learner's upload already counts as DOCUMENTED evidence (MEDIUM confidence).
 * Approving it turns those EvidenceLog rows into VERIFIED_CERT (verified channel,
 * HIGH confidence). Rejecting it deletes them, so the official's gap returns.
 */

import React from 'react';
import { CheckCircle2, FileText, XCircle } from 'lucide-react';

import SectionCard from '../shell/SectionCard';
import { useAsync } from '../../hooks/useAdminData';
import {
  fetchCertificateReviews, reviewCertificate,
  type CertificateStatus, type CertificateSubmission,
} from '../../services/api';

const TABS: (CertificateStatus | 'ALL')[] = ['PENDING', 'VERIFIED', 'REJECTED', 'ALL'];
const STATUS_CLS: Record<CertificateStatus, string> = {
  PENDING: 'bg-accent-orange-soft text-accent-orange dark:bg-orange-500/15 dark:text-orange-300',
  VERIFIED: 'bg-accent-green-soft text-accent-green dark:bg-emerald-500/15 dark:text-emerald-300',
  REJECTED: 'bg-accent-rose-soft text-accent-rose dark:bg-rose-500/15 dark:text-rose-300',
};
const when = (iso: string | null) => (iso ? new Date(iso).toLocaleDateString(undefined, { dateStyle: 'medium' }) : '—');

const Row: React.FC<{ cert: CertificateSubmission; onDone: () => void }> = ({ cert, onDone }) => {
  const [note, setNote] = React.useState('');
  const [busy, setBusy] = React.useState(false);
  const [err, setErr] = React.useState<string | null>(null);

  const decide = async (decision: 'approve' | 'reject') => {
    setBusy(true);
    setErr(null);
    try {
      await reviewCertificate(cert.id, decision, note);
      onDone();
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Review failed');
    } finally {
      setBusy(false);
    }
  };

  return (
    <li className="rounded-xl border border-gov-line p-3.5 dark:border-slate-700/50">
      <div className="flex flex-wrap items-start gap-2">
        <FileText size={15} className="mt-0.5 text-slate-400" aria-hidden="true" />
        <div className="min-w-0 flex-1">
          <p className="truncate text-[13px] font-semibold text-gov-ink dark:text-white">{cert.filename}</p>
          <p className="text-[11.5px] text-slate-500 dark:text-slate-400">
            {cert.userId} · {cert.issuingOrganization ?? 'issuer not found'} · {when(cert.createdAt)} · via {cert.extractor}
          </p>
        </div>
        <span className={`rounded-full px-2 py-0.5 text-[10.5px] font-semibold ${STATUS_CLS[cert.status]}`}>
          {cert.status === 'PENDING' ? 'Documented' : cert.status === 'VERIFIED' ? 'Verified' : 'Rejected'}
        </span>
      </div>

      <ul className="mt-2 space-y-1">
        {cert.competencies.map((c) => (
          <li key={c.competency_id} className="text-[12px] text-slate-600 dark:text-slate-300">
            <span className="font-semibold">{c.competency_name}</span> · Level {Math.round(c.extracted_level)}
            {c.issue_date ? ` · issued ${c.issue_date}` : ''}
            {c.match_score != null ? ` · match ${c.match_score.toFixed(2)}` : ''}
            {c.justification && <span className="block text-[11.5px] text-slate-400">{c.justification}</span>}
          </li>
        ))}
      </ul>

      {cert.status === 'PENDING' ? (
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <input
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Note (optional, shown to the official on rejection)"
            aria-label={`Review note for ${cert.filename}`}
            className="min-w-[12rem] flex-1 rounded-lg border border-gov-line bg-white px-3 py-1.5 text-[12.5px] text-slate-700 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
          <button
            type="button" disabled={busy} onClick={() => decide('approve')}
            className="flex items-center gap-1.5 rounded-lg bg-accent-green px-3 py-1.5 text-[12.5px] font-semibold text-white hover:bg-emerald-600 disabled:opacity-60"
          >
            <CheckCircle2 size={14} aria-hidden="true" /> Approve
          </button>
          <button
            type="button" disabled={busy} onClick={() => decide('reject')}
            className="flex items-center gap-1.5 rounded-lg border border-accent-rose px-3 py-1.5 text-[12.5px] font-semibold text-accent-rose hover:bg-accent-rose-soft disabled:opacity-60 dark:hover:bg-rose-500/10"
          >
            <XCircle size={14} aria-hidden="true" /> Reject
          </button>
        </div>
      ) : (
        <p className="mt-2 text-[11.5px] text-slate-400">
          {cert.reviewedBy ? `Reviewed by ${cert.reviewedBy} on ${when(cert.reviewedAt)}` : ''}
          {cert.reviewNote ? ` · “${cert.reviewNote}”` : ''}
        </p>
      )}
      {err && <p className="mt-1.5 text-[11.5px] text-accent-rose">{err}</p>}
    </li>
  );
};

const CertificateReviewQueue: React.FC = () => {
  const [status, setStatus] = React.useState<CertificateStatus | 'ALL'>('PENDING');
  const q = useAsync(() => fetchCertificateReviews(status), `certs|${status}`);
  const certs = q.data?.certificates ?? [];

  return (
    <SectionCard
      title="Certificate verification"
      subtitle={`${q.data?.pendingCount ?? 0} awaiting review · approval moves evidence from documented to verified`}
    >
      <div className="mb-3 flex flex-wrap gap-1.5" role="tablist" aria-label="Certificate status">
        {TABS.map((t) => (
          <button
            key={t} type="button" role="tab" aria-selected={status === t} onClick={() => setStatus(t)}
            className={`rounded-full px-3 py-1 text-[11.5px] font-semibold ${
              status === t ? 'bg-gov-ink text-white dark:bg-white dark:text-gov-ink'
                : 'bg-gov-paper text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'}`}
          >
            {t === 'ALL' ? 'All' : t.charAt(0) + t.slice(1).toLowerCase()}
          </button>
        ))}
      </div>
      {q.error && <p className="text-[12.5px] text-accent-rose">{q.error}</p>}
      {q.isLoading && !q.data ? (
        <p className="text-[12.5px] text-slate-500">Loading…</p>
      ) : certs.length === 0 ? (
        <p className="text-[12.5px] text-slate-500 dark:text-slate-400">No certificates here.</p>
      ) : (
        <ul className="space-y-2.5">
          {certs.map((c) => <Row key={c.id} cert={c} onDone={q.refetch} />)}
        </ul>
      )}
    </SectionCard>
  );
};

export default CertificateReviewQueue;
