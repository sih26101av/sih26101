/**
 * FILE: src/components/dashboard/CertificateUploadZone.tsx
 *
 * External certificate → FRAC evidence (POST /api/v1/competencies/upload-certificate).
 * An upload is recorded at once as DOCUMENTED evidence (MEDIUM confidence), so the
 * skill gap moves straight away; `onUploaded` lets the dashboard refetch. An admin
 * approval later turns it into VERIFIED evidence (HIGH confidence).
 */

import React, { useCallback, useEffect, useRef, useState } from "react";
import { Award, FileText, Loader2, Upload } from "lucide-react";

import {
  fetchMyCertificates, uploadCertificate,
  type CertificateStatus, type CertificateSubmission,
} from "../../services/api";

const STATUS_CHIP: Record<CertificateStatus, { label: string; cls: string }> = {
  PENDING: {
    label: "Documented · awaiting review",
    cls: "bg-accent-orange-soft text-accent-orange dark:bg-orange-500/15 dark:text-orange-300",
  },
  VERIFIED: {
    label: "Verified",
    cls: "bg-accent-green-soft text-accent-green dark:bg-emerald-500/15 dark:text-emerald-300",
  },
  REJECTED: {
    label: "Rejected",
    cls: "bg-accent-rose-soft text-accent-rose dark:bg-rose-500/15 dark:text-rose-300",
  },
};

const clean = (msg: string) => msg.replace(/^\[[^\]]+\]\s*/, "");

const CertificateRow: React.FC<{ cert: CertificateSubmission }> = ({ cert }) => {
  const chip = STATUS_CHIP[cert.status];
  return (
    <li className="rounded-xl border border-gov-line p-3 dark:border-slate-700/50">
      <div className="flex items-start gap-2">
        <FileText size={15} className="mt-0.5 flex-shrink-0 text-slate-400" aria-hidden="true" />
        <div className="min-w-0 flex-1">
          <p className="truncate text-[13px] font-semibold text-gov-ink dark:text-white">{cert.filename}</p>
          {cert.issuingOrganization && (
            <p className="text-[11.5px] text-slate-500 dark:text-slate-400">{cert.issuingOrganization}</p>
          )}
        </div>
        <span className={`flex-shrink-0 rounded-full px-2 py-0.5 text-[10.5px] font-semibold ${chip.cls}`}>
          {chip.label}
        </span>
      </div>
      {cert.competencies.length > 0 && (
        <ul className="mt-2 flex flex-wrap gap-1.5">
          {cert.competencies.map((c) => (
            <li
              key={c.competency_id}
              title={c.justification}
              className="rounded-md bg-gov-paper px-2 py-0.5 text-[11.5px] text-slate-600 dark:bg-slate-800/60 dark:text-slate-300"
            >
              {c.competency_name} · L{Math.round(c.extracted_level)}
              {c.issue_date ? ` · ${c.issue_date.slice(0, 4)}` : ""}
            </li>
          ))}
        </ul>
      )}
      {cert.status === "REJECTED" && cert.reviewNote && (
        <p className="mt-2 text-[11.5px] text-accent-rose">Reviewer: {cert.reviewNote}</p>
      )}
    </li>
  );
};

const CertificateUploadZone: React.FC<{ onUploaded?: () => void }> = ({ onUploaded }) => {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const [certs, setCerts] = useState<CertificateSubmission[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadCerts = useCallback(() => {
    fetchMyCertificates().then(setCerts).catch(() => { /* list is optional */ });
  }, []);
  useEffect(loadCerts, [loadCerts]);

  const handleUpload = async () => {
    if (!file) {
      fileInputRef.current?.click();
      return;
    }
    setBusy(true);
    setMsg(null);
    try {
      const r = await uploadCertificate(file);
      setMsg({ ok: r.status !== "no_evidence", text: r.message });
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      if (r.status === "success") {
        loadCerts();
        onUploaded?.();
      }
    } catch (e) {
      setMsg({ ok: false, text: clean(e instanceof Error ? e.message : "Upload failed") });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-4">
        <span className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl bg-accent-green-soft dark:bg-emerald-500/15">
          <Award size={22} className="text-accent-green dark:text-emerald-300" aria-hidden="true" />
        </span>
        <div>
          <h3 className="mb-0.5 text-[14.5px] font-semibold leading-tight text-gov-ink dark:text-white">External Certificates</h3>
          <p className="text-[12px] text-slate-500 dark:text-slate-400">
            Upload non-iGOT certificates (PDF/Image). Matched FRAC skills count as documented
            evidence at once and become verified after admin review.
          </p>
        </div>
      </div>

      <input
        type="file"
        className="hidden"
        ref={fileInputRef}
        accept=".pdf,.png,.jpg,.jpeg,.webp"
        aria-label="Choose a certificate file"
        onChange={(e) => { setFile(e.target.files?.[0] || null); setMsg(null); }}
      />

      {file && (
        <div className="flex animate-fade-in items-center gap-2 rounded-xl border border-gov-line bg-gov-paper p-3 text-sm dark:border-slate-700/50 dark:bg-slate-800/60">
          <FileText size={16} className="flex-shrink-0 text-accent-green" aria-hidden="true" />
          <span className="flex-1 truncate font-medium text-slate-700 dark:text-slate-300">{file.name}</span>
          <button
            type="button"
            onClick={() => setFile(null)}
            disabled={busy}
            className="font-bold text-slate-400 hover:text-accent-rose"
            aria-label={`Remove ${file.name}`}
          >
            &times;
          </button>
        </div>
      )}

      <button
        type="button"
        onClick={handleUpload}
        disabled={busy}
        className={`flex w-full items-center justify-center gap-2 rounded-xl border-[1.5px] border-dashed py-2.5 text-[13.5px] font-semibold transition-all duration-300 disabled:opacity-70 ${
          file
            ? "border-solid border-accent-green bg-accent-green text-white hover:bg-emerald-600"
            : "border-accent-green/50 bg-accent-green/[0.05] text-accent-green hover:border-accent-green hover:bg-accent-green/10 dark:text-emerald-300"
        }`}
      >
        {busy ? <Loader2 size={17} className="animate-spin" aria-hidden="true" /> : <Upload size={17} aria-hidden="true" />}
        {busy ? "Reading certificate…" : file ? "Submit for Verification" : "Upload Certificate"}
      </button>

      {msg && (
        <p role="status" className={`text-[12.5px] ${msg.ok ? "text-accent-green dark:text-emerald-300" : "text-accent-rose"}`}>
          {msg.text}
        </p>
      )}

      {certs.length > 0 && (
        <div>
          <h4 className="mb-2 text-[12px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Your submissions
          </h4>
          <ul className="flex flex-col gap-2">
            {certs.map((c) => <CertificateRow key={c.id} cert={c} />)}
          </ul>
        </div>
      )}
    </div>
  );
};

export default CertificateUploadZone;
