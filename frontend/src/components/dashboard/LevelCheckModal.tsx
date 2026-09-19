/**
 * FILE: src/components/dashboard/LevelCheckModal.tsx
 *
 * "I disagree with this level" → records a level dispute and runs the adaptive
 * level check (2PL IRT, routers/diagnostic.py) in place. When the check ends the
 * dispute is closed as confirmed / raised / lower than shown, and `onFinished`
 * lets the dashboard refetch so the new evidence shows at once.
 */

import React, { useState } from 'react';
import { X, ClipboardCheck, Loader2, CheckCircle2, ArrowUpCircle, AlertTriangle } from 'lucide-react';
import { answerDiagnostic, openLevelDispute } from '../../services/api';
import type { DiagnosticView, LevelDispute } from '../../types/domain';

interface Props {
  competencyId: string;
  competencyName: string;
  shownLevel: number | null;
  onClose: () => void;
  onFinished: () => void;
}

const OUTCOME: Record<string, { title: string; tone: string; Icon: typeof CheckCircle2 }> = {
  CONFIRMED:        { title: 'Level confirmed',         tone: 'text-emerald-600 dark:text-emerald-400', Icon: CheckCircle2 },
  RAISED:           { title: 'Your level goes up',      tone: 'text-indigo-600 dark:text-indigo-400',   Icon: ArrowUpCircle },
  LOWER_THAN_SHOWN: { title: 'The test scored lower',   tone: 'text-amber-600 dark:text-amber-400',     Icon: AlertTriangle },
};

const LevelCheckModal: React.FC<Props> = ({ competencyId, competencyName, shownLevel, onClose, onFinished }) => {
  const [claimed, setClaimed] = useState<number | null>(shownLevel != null ? Math.min(5, shownLevel + 1) : null);
  const [reason, setReason] = useState('');
  const [dispute, setDispute] = useState<LevelDispute | null>(null);
  const [view, setView] = useState<DiagnosticView | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const start = async () => {
    setBusy(true); setError(null);
    try {
      const res = await openLevelDispute(competencyId, claimed, reason.trim());
      setDispute(res.dispute);
      setView(res.session);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not start the level check.');
    } finally {
      setBusy(false);
    }
  };

  const answer = async (optionIndex: number) => {
    if (!view?.item) return;
    setBusy(true); setError(null);
    try {
      const next = await answerDiagnostic(view.sessionId, view.item.itemId, optionIndex);
      setView(next);
      if (next.done) onFinished();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not submit the answer.');
    } finally {
      setBusy(false);
    }
  };

  const outcome = view?.done && view.dispute ? OUTCOME[view.dispute.status] : null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4" role="dialog" aria-modal="true">
      <div className="w-full max-w-lg rounded-xl bg-white dark:bg-slate-900 border border-gov-line dark:border-slate-700 shadow-gov-lg">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-2">
            <ClipboardCheck size={16} className="text-violet-600 dark:text-violet-400" />
            <h3 className="text-[14px] font-bold text-slate-900 dark:text-white">Check your level · {competencyName}</h3>
          </div>
          <button onClick={onClose} aria-label="Close" className="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200">
            <X size={16} />
          </button>
        </div>

        <div className="px-5 py-4 text-[12.5px] text-slate-700 dark:text-slate-300">
          {error && <p className="mb-3 rounded-md bg-red-50 dark:bg-red-900/20 px-3 py-2 text-red-700 dark:text-red-300">{error}</p>}

          {!dispute && (
            <>
              <p className="mb-3">
                We show Level <b>{shownLevel ?? '—'}</b>. If you think that is wrong, take a short adaptive test
                (about 5–10 questions). The result is added to your evidence like a quiz.
              </p>
              <label className="block text-[11px] font-semibold text-slate-500 dark:text-slate-400 mb-1">What level do you think you are?</label>
              <div className="flex gap-1.5 mb-3">
                {[1, 2, 3, 4, 5].map(l => (
                  <button key={l} onClick={() => setClaimed(l)}
                    className={`w-9 h-8 rounded-md text-[12px] font-bold border ${claimed === l
                      ? 'bg-violet-600 text-white border-violet-600'
                      : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700'}`}>
                    {l}
                  </button>
                ))}
              </div>
              <label className="block text-[11px] font-semibold text-slate-500 dark:text-slate-400 mb-1">Why? (optional)</label>
              <textarea value={reason} onChange={e => setReason(e.target.value)} maxLength={500} rows={2}
                placeholder="e.g. I compile this index every month"
                className="w-full rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-2.5 py-1.5 text-[12px]" />
              <button onClick={start} disabled={busy} className="gov-btn-primary w-full mt-3">
                {busy ? <Loader2 size={14} className="animate-spin" /> : <ClipboardCheck size={14} />} Start the level check
              </button>
            </>
          )}

          {dispute && !view && (
            <p>
              There are no test questions for this competency yet, so your disagreement has been recorded for a
              reviewer (status: <b>{dispute.status.replace(/_/g, ' ').toLowerCase()}</b>).
            </p>
          )}

          {view && !view.done && view.item && (
            <>
              <p className="text-[11px] text-slate-400 mb-2">
                Question {view.answered + 1} (up to {view.maxItems}) · Level {view.item.level} · {view.item.bloom}
              </p>
              <p className="font-semibold text-slate-900 dark:text-white mb-3">{view.item.stem}</p>
              <div className="space-y-1.5">
                {view.item.options.map((opt, i) => (
                  <button key={i} onClick={() => answer(i)} disabled={busy}
                    className="w-full text-left rounded-md border border-slate-200 dark:border-slate-700 px-3 py-2 hover:border-violet-400 hover:bg-violet-50 dark:hover:bg-violet-900/20 disabled:opacity-60">
                    {opt}
                  </button>
                ))}
              </div>
              <p className="mt-3 text-[10px] text-slate-400">{view.calibration}</p>
            </>
          )}

          {view?.done && (
            <div className="text-center py-2">
              {outcome ? (
                <>
                  <outcome.Icon size={28} className={`mx-auto mb-2 ${outcome.tone}`} />
                  <p className={`font-bold text-[14px] ${outcome.tone}`}>{outcome.title}</p>
                  <p className="mt-1">
                    Shown Level {view.dispute?.shownLevel ?? '—'} · you said {view.dispute?.claimedLevel ?? '—'} ·
                    the test estimates Level <b>{view.dispute?.testedLevel}</b>.
                  </p>
                  {view.dispute?.status === 'LOWER_THAN_SHOWN' && (
                    <p className="mt-1 text-[11px] text-slate-500">
                      Completed courses and passed work samples still count as a minimum, so your level cannot drop below them.
                    </p>
                  )}
                </>
              ) : (
                <p>Level check finished — estimated ability {view.posterior.mu.toFixed(1)}.</p>
              )}
              <button onClick={onClose} className="gov-btn-primary mt-4 w-full">Done</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LevelCheckModal;
