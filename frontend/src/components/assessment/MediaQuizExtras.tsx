/**
 * FILE: src/components/assessment/MediaQuizExtras.tsx
 *
 * Assessment Studio add-ons for video / audio / YouTube quizzes:
 *   • YoutubeLinkInput   — URL field shown for the "Paste Text/URL" source.
 *   • MediaAnalysisCard  — what the pipeline detected (content type, probe
 *                          signals, evidence kept/dropped, validator and
 *                          fact-check results) shown above a media quiz.
 *   • MediaAnswerReview  — result screen only (evidence reveals answers):
 *                          correct answers with QuestionEvidence — timestamp,
 *                          cited evidence and "flagged for trainer review".
 * Kept out of AssessmentPage.tsx so the page only needs a few hook-in lines.
 */

import React from "react";
import { AlertTriangle, Clapperboard, Link as LinkIcon, ShieldCheck } from "lucide-react";

import {
  formatTimestamp,
  isYoutubeUrl,
  type MediaEvidence,
  type MediaQuizQuestion,
  type MediaReport,
} from "../../services/mediaQuizApi";

const CONTENT_LABEL: Record<string, string> = {
  narrated_slides: "Narrated slide lecture",
  talking_head: "Talking head / audio lecture",
  silent_screen_demo: "Silent screen demo",
  silent_slides: "Silent slides",
  reject: "Not learnable",
};

const SOURCE_LABEL: Record<string, string> = { asr: "Speech", ocr: "On-screen text", vlm: "Screen description" };

const pct = (v: number | undefined) => `${Math.round((v ?? 0) * 100)}%`;

// ── YouTube link input ─────────────────────────────────────────────────────────

export const YoutubeLinkInput: React.FC<{ value: string; onChange: (v: string) => void }> = ({ value, onChange }) => {
  const invalid = value.trim() !== "" && !isYoutubeUrl(value);
  return (
    <div className="mb-5">
      <label htmlFor="yt-url" className="mb-1.5 block text-[12.5px] font-semibold text-slate-600 dark:text-slate-300">
        YouTube link
      </label>
      <div className="flex items-center gap-2 rounded-xl border border-gov-line px-3 py-2.5 focus-within:border-gov-blue dark:border-slate-700">
        <LinkIcon className="h-4 w-4 flex-shrink-0 text-slate-400" aria-hidden="true" />
        <input
          id="yt-url"
          type="url"
          inputMode="url"
          placeholder="https://www.youtube.com/watch?v=…"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full bg-transparent text-sm text-gov-ink outline-none placeholder:text-slate-400 dark:text-slate-100"
          aria-invalid={invalid}
        />
      </div>
      <p className={`mt-1.5 text-[12px] ${invalid ? "text-accent-rose" : "text-slate-500 dark:text-slate-400"}`}>
        {invalid
          ? "Only youtube.com / youtu.be links are supported."
          : "The video is probed first (speech, on-screen text, screen activity) and only learnable content is used."}
      </p>
    </div>
  );
};

// ── Analysis card ──────────────────────────────────────────────────────────────

export const MediaAnalysisCard: React.FC<{ report: MediaReport; skillName?: string }> = ({ report, skillName }) => {
  const p = report.probe;
  const kept = Object.values(report.evidence?.kept ?? {}).reduce((a, b) => a + b, 0);
  const dropped = Object.values(report.evidence?.dropped ?? {}).reduce((a, b) => a + b, 0);
  const gen = report.generation;
  const fc = report.fact_check;

  const stats: Array<[string, string]> = [
    ["Speech", pct(p.speech_ratio)],
    ["On-screen text", pct(p.text_density)],
    ["Screen activity", pct(p.screen_activity)],
    ["Evidence kept / dropped", `${kept} / ${dropped}`],
    ["Questions rejected by validator", String(gen?.rejected_total ?? 0)],
    ["Flagged for trainer review", String(fc?.flagged ?? 0)],
  ];

  return (
    <div className="panel mb-6 p-5">
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <Clapperboard className="h-5 w-5 text-accent-blue dark:text-sky-300" aria-hidden="true" />
        <span className="text-[14px] font-semibold text-gov-ink dark:text-white">
          {CONTENT_LABEL[report.content_type] ?? report.content_type}
        </span>
        <span className="text-[12px] text-slate-500 dark:text-slate-400">
          · {formatTimestamp(p.duration)} · tools: {p.tools.join(", ") || "none"}
        </span>
        {skillName && (
          <span className="ml-auto rounded-md bg-accent-blue-soft px-2 py-0.5 text-[11.5px] font-semibold text-accent-blue dark:bg-sky-900/30 dark:text-sky-300">
            {skillName}
          </span>
        )}
      </div>
      <dl className="grid grid-cols-2 gap-x-6 gap-y-2 md:grid-cols-3">
        {stats.map(([k, v]) => (
          <div key={k}>
            <dt className="text-[11px] uppercase tracking-wide text-slate-400">{k}</dt>
            <dd className="text-[14px] font-semibold text-gov-ink dark:text-slate-100">{v}</dd>
          </div>
        ))}
      </dl>
      {report.vlm_backend.includes("demo-only") && (
        <p className="mt-3 text-[11.5px] text-slate-500 dark:text-slate-400">
          Screen descriptions use a cloud vision model (demo-only). The offline deployment uses a local Qwen2.5-VL.
        </p>
      )}
    </div>
  );
};

// ── Per-question evidence ──────────────────────────────────────────────────────

export const QuestionEvidence: React.FC<{ question: MediaQuizQuestion; evidence: MediaEvidence[] }> = ({
  question,
  evidence,
}) => {
  const cited = evidence.filter((e) => question.evidence.includes(e.id));
  const flagged = question.review?.status === "flagged";
  return (
    <div className="mt-4 space-y-2 border-t border-gov-line pt-3 text-[12px] dark:border-slate-700">
      <div className="flex flex-wrap items-center gap-2 text-slate-500 dark:text-slate-400">
        {question.t_start != null && (
          <span className="rounded bg-slate-100 px-1.5 py-0.5 font-mono dark:bg-slate-800">
            {formatTimestamp(question.t_start)}–{formatTimestamp(question.t_end)}
          </span>
        )}
        {question.kind === "synthesis" && (
          <span className="rounded bg-violet-50 px-1.5 py-0.5 font-semibold text-violet-700 dark:bg-violet-900/30 dark:text-violet-300">
            Connects multiple sections
          </span>
        )}
        {question.review?.status === "ok" && (
          <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
            <ShieldCheck className="h-3.5 w-3.5" aria-hidden="true" /> Matches reference
          </span>
        )}
      </div>
      {flagged && (
        <p className="flex items-start gap-1.5 rounded-lg bg-amber-50 px-2.5 py-2 text-amber-800 dark:bg-amber-900/20 dark:text-amber-300">
          <AlertTriangle className="mt-0.5 h-3.5 w-3.5 flex-shrink-0" aria-hidden="true" />
          Flagged for trainer review: {question.review.note}
        </p>
      )}
      {cited.length > 0 && (
        <details className="text-slate-500 dark:text-slate-400">
          <summary className="cursor-pointer select-none">Source evidence ({cited.length})</summary>
          <ul className="mt-1.5 space-y-1">
            {cited.map((e) => (
              <li key={e.id}>
                <span className="font-mono">{formatTimestamp(e.t_start)}</span>{" "}
                <span className="font-semibold">{SOURCE_LABEL[e.source] ?? e.source}</span>{" "}
                <span className="text-slate-400">({Math.round(e.confidence * 100)}%)</span>: {e.text}
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
};

// ── Post-quiz review (answers + where they came from) ──────────────────────────
// Shown only on the result screen: evidence and fact-check notes reveal answers.

export const MediaAnswerReview: React.FC<{
  questions: MediaQuizQuestion[];
  evidence: MediaEvidence[];
  answers: number[];
}> = ({ questions, evidence, answers }) => (
  <div className="panel mt-6 p-6 text-left">
    <h3 className="mb-4 text-[15px] font-semibold text-gov-ink dark:text-white">Answer review with source evidence</h3>
    <ol className="space-y-5">
      {questions.map((q, i) => {
        const correct = answers[i] === q.correct_answer;
        return (
          <li key={i}>
            <p className="text-[14px] font-medium text-gov-ink dark:text-slate-100">
              {i + 1}. {q.question}
            </p>
            <p className={`mt-1 text-[13px] ${correct ? "text-accent-green" : "text-accent-rose"}`}>
              {correct ? "✓" : "✗"} Correct answer: {q.options[q.correct_answer]}
            </p>
            {q.explanation && <p className="mt-1 text-[12.5px] text-slate-500 dark:text-slate-400">{q.explanation}</p>}
            <QuestionEvidence question={q} evidence={evidence} />
          </li>
        );
      })}
    </ol>
  </div>
);
