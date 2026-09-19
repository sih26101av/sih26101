/**
 * FILE: src/components/assessment/QuizSkillImpact.tsx
 *
 * Result-screen panels for the Assessment Studio, fed by /api/v1/rag/grade:
 *  - SkillImpactCard      — linked role competency, practice ability and skill
 *                           score / level before → after, per-question moves
 *  - QuizRecommendations  — next difficulty, focus topics, courses
 *  - QuizQuestionReview   — each question with difficulty, your answer, the
 *                           correct answer and the explanation (missed first)
 */

import React from "react";
import { ArrowDownRight, ArrowRight, ArrowUpRight, BookOpen, CheckCircle, Target, XCircle } from "lucide-react";
import type { QuizDifficulty, QuizGradeResult, QuizQuestionReview as ReviewRow } from "../../services/api";

const DIFF_CLASS: Record<QuizDifficulty, string> = {
  Easy: "bg-accent-green-soft text-accent-green dark:bg-emerald-500/15 dark:text-emerald-300",
  Medium: "bg-accent-blue-soft text-accent-blue dark:bg-sky-500/15 dark:text-sky-300",
  Hard: "bg-accent-rose-soft text-accent-rose dark:bg-rose-500/15 dark:text-rose-300",
};

export const DifficultyChip: React.FC<{ difficulty?: string | null }> = ({ difficulty }) => {
  const d = (difficulty ?? "Medium") as QuizDifficulty;
  return <span className={`chip ${DIFF_CLASS[d] ?? DIFF_CLASS.Medium}`}>{d}</span>;
};

const signed = (n: number, digits = 2) => `${n >= 0 ? "+" : ""}${n.toFixed(digits)}`;

const Delta: React.FC<{ value?: number; digits?: number }> = ({ value, digits = 2 }) => {
  if (value === undefined || value === null) return null;
  const up = value > 0.0005, down = value < -0.0005;
  const Icon = up ? ArrowUpRight : down ? ArrowDownRight : ArrowRight;
  const tone = up ? "text-accent-green" : down ? "text-accent-rose" : "text-slate-400";
  return (
    <span className={`inline-flex items-center gap-0.5 text-[12.5px] font-semibold tabular-nums ${tone}`}>
      <Icon className="h-3.5 w-3.5" aria-hidden="true" /> {signed(value, digits)}
    </span>
  );
};

const Stat: React.FC<{ label: string; before?: string; after?: string; delta?: React.ReactNode }> = ({ label, before, after, delta }) => (
  <div className="rounded-xl border border-gov-line bg-gov-paper p-4 dark:border-slate-700 dark:bg-slate-900/50">
    <p className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">{label}</p>
    <p className="text-[18px] font-bold tabular-nums text-gov-ink dark:text-white">
      {before !== undefined && before !== after && <span className="text-slate-400">{before} → </span>}
      {after ?? "—"}
    </p>
    {delta}
  </div>
);

export const SkillImpactCard: React.FC<{ result: QuizGradeResult }> = ({ result }) => {
  const impact = result.skillImpact;
  if (!impact) return null;
  const { before, after } = impact;
  const lvl = (n?: number | null) => (n === null || n === undefined ? "—" : `L${n}`);

  return (
    <section className="panel mt-5 p-6 text-left" aria-labelledby="skill-impact-title">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-2">
        <div>
          <h3 id="skill-impact-title" className="text-[15px] font-semibold text-gov-ink dark:text-white">
            Impact on your skill gap
          </h3>
          <p className="text-[12.5px] text-slate-500 dark:text-slate-400">
            {impact.competencyName ?? "Unlinked topic"}
            {impact.linkedToSkillGap
              ? ` · matched to your role competency (${impact.linkMethod.replace("_", " ")})`
              : " · not one of your role competencies"}
          </p>
        </div>
        {result.difficulty && <DifficultyChip difficulty={result.difficulty} />}
      </div>

      {impact.recorded && impact.abilityAfter !== undefined ? (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <Stat
            label="Practice ability"
            before={impact.abilityBefore?.toFixed(2)}
            after={impact.abilityAfter.toFixed(2)}
            delta={<Delta value={impact.abilityDelta} />}
          />
          {impact.linkedToSkillGap && (
            <>
              <Stat
                label="Skill score (0–5)"
                before={before.score?.toFixed(2)}
                after={after.score?.toFixed(2)}
                delta={<Delta value={impact.scoreDelta} />}
              />
              <Stat
                label="Level / target"
                before={`${lvl(before.level)} / ${lvl(before.targetLevel)}`}
                after={`${lvl(after.level)} / ${lvl(after.targetLevel)}`}
                delta={
                  <span className="text-[12px] text-slate-500 dark:text-slate-400">
                    {after.gap ? `Gap ${after.gap} level${after.gap === 1 ? "" : "s"}` : after.level !== null && after.level !== undefined ? "Target met" : "Not yet assessed"}
                  </span>
                }
              />
            </>
          )}
        </div>
      ) : (
        <p className="rounded-xl border border-gov-line bg-gov-paper px-4 py-3 text-[12.5px] text-slate-500 dark:border-slate-700 dark:bg-slate-800/50 dark:text-slate-400">
          {impact.note ?? "No practice evidence was recorded for this attempt."}
        </p>
      )}

      {impact.perQuestion && impact.perQuestion.length > 0 && (
        <div className="mt-4">
          <p className="mb-2 text-[11.5px] font-semibold uppercase tracking-wider text-slate-400">How each answer moved your ability</p>
          <ol className="flex flex-wrap gap-2">
            {impact.perQuestion.map((q, i) => (
              <li
                key={i}
                title={`Expected ${(q.expected * 100).toFixed(0)}% chance of answering correctly`}
                className="flex items-center gap-1.5 rounded-lg border border-gov-line px-2.5 py-1.5 text-[12px] dark:border-slate-700"
              >
                <span className="font-semibold text-slate-500">Q{i + 1}</span>
                {q.correct
                  ? <CheckCircle className="h-3.5 w-3.5 text-accent-green" aria-label="correct" />
                  : <XCircle className="h-3.5 w-3.5 text-accent-rose" aria-label="wrong" />}
                <DifficultyChip difficulty={q.difficulty} />
                <Delta value={q.delta} digits={3} />
              </li>
            ))}
          </ol>
          <p className="mt-2 text-[11.5px] leading-relaxed text-slate-400">
            Missing an easy question costs more than missing a hard one; solving a hard question earns more than an easy one.
            Your skill score blends this practice ability with your other evidence, so it moves by a smaller amount.
          </p>
        </div>
      )}
    </section>
  );
};

export const QuizRecommendations: React.FC<{ result: QuizGradeResult; onRetry?: (d: QuizDifficulty) => void }> = ({ result, onRetry }) => {
  const rec = result.recommendations;
  if (!rec) return null;
  return (
    <section className="panel mt-5 p-6 text-left" aria-labelledby="quiz-rec-title">
      <h3 id="quiz-rec-title" className="mb-1 flex items-center gap-2 text-[15px] font-semibold text-gov-ink dark:text-white">
        <Target className="h-4 w-4 text-accent-blue" aria-hidden="true" /> What to do next
      </h3>
      <p className="mb-4 text-[13px] text-slate-600 dark:text-slate-300">{rec.summary}</p>

      <div className="mb-4 flex flex-wrap items-center gap-2 text-[13px]">
        <span className="text-slate-500 dark:text-slate-400">Next quiz:</span>
        <DifficultyChip difficulty={rec.nextDifficulty} />
        <span className="text-slate-500 dark:text-slate-400">{rec.nextDifficultyReason}</span>
        {onRetry && (
          <button type="button" className="gov-btn-outline !px-3 !py-1.5 !text-[12px]" onClick={() => onRetry(rec.nextDifficulty)}>
            New quiz at {rec.nextDifficulty}
          </button>
        )}
      </div>

      {rec.focusTopics.length > 0 && (
        <div className="mb-4">
          <p className="mb-1.5 text-[11.5px] font-semibold uppercase tracking-wider text-slate-400">Focus topics (from questions you missed)</p>
          <ul className="list-disc space-y-1 pl-5 text-[13px] text-slate-600 dark:text-slate-300">
            {rec.focusTopics.map((t, i) => <li key={i}>{t}</li>)}
          </ul>
        </div>
      )}

      {rec.courses.length > 0 && (
        <div>
          <p className="mb-1.5 text-[11.5px] font-semibold uppercase tracking-wider text-slate-400">Recommended iGOT courses</p>
          <ul className="space-y-2">
            {rec.courses.map((c) => (
              <li key={c.courseId} className="flex items-center gap-3 rounded-xl border border-gov-line px-3.5 py-2.5 dark:border-slate-700">
                <BookOpen className="h-4 w-4 flex-shrink-0 text-accent-blue" aria-hidden="true" />
                <span className="min-w-0 flex-1 truncate text-[13px] font-medium text-gov-ink dark:text-white">{c.title}</span>
                <span className="whitespace-nowrap text-[11.5px] text-slate-400">
                  {c.level ? `Level ${c.level}` : ""}{c.durationHours ? ` · ${c.durationHours} h` : ""}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
};

export const QuizQuestionReview: React.FC<{ rows: ReviewRow[] }> = ({ rows }) => (
  <section className="panel mt-5 p-6 text-left" aria-labelledby="quiz-review-title">
    <h3 id="quiz-review-title" className="mb-4 text-[15px] font-semibold text-gov-ink dark:text-white">Answer review</h3>
    <ol className="space-y-3">
      {rows.map((r) => (
        <li key={r.index} className={`rounded-xl border p-4 ${r.correct ? "border-gov-line dark:border-slate-700" : "border-accent-rose/30 bg-accent-rose-soft/40 dark:border-rose-800/40 dark:bg-rose-900/10"}`}>
          <div className="mb-1.5 flex items-start gap-2">
            {r.correct
              ? <CheckCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-accent-green" aria-label="correct" />
              : <XCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-accent-rose" aria-label="wrong" />}
            <p className="flex-1 text-[13.5px] font-medium text-gov-ink dark:text-white">
              <span className="mr-1.5 text-slate-400">{r.index + 1}.</span>{r.question}
            </p>
            <DifficultyChip difficulty={r.difficulty} />
          </div>
          {!r.correct && r.yourAnswer && (
            <p className="pl-6 text-[12.5px] text-accent-rose">Your answer: {r.yourAnswer}</p>
          )}
          <p className="pl-6 text-[12.5px] text-accent-green">Correct answer: {r.correctAnswer}</p>
          {r.explanation && <p className="mt-1 pl-6 text-[12.5px] leading-relaxed text-slate-500 dark:text-slate-400">{r.explanation}</p>}
        </li>
      ))}
    </ol>
  </section>
);
