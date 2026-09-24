/**
 * FILE: src/components/assessment/QuizQuestionInput.tsx
 *
 * One quiz question, any objective type (routers/rag.py + services/doc_quiz):
 *   mcq · true_false   → radio options          answer: number
 *   multi_select       → checkboxes             answer: number[]
 *   fill_blank         → text input in the stem answer: string
 *   numeric            → number input + unit    answer: string (parsed server-side)
 * Media quizzes carry no `type` and render as mcq.
 *
 * `lang` = "en" | "hi" | "bi": Hindi text comes from question.translations.hi;
 * "bi" shows English with the Hindi underneath.
 */

import React from "react";
import type { DocQuizQuestion, QuizAnswer, QuizQuestionType } from "../../services/api";
import { DifficultyChip } from "./QuizSkillImpact";

export type QuizLang = "en" | "hi" | "bi";

export const TYPE_LABEL: Record<QuizQuestionType, string> = {
  mcq: "Multiple choice",
  true_false: "True / False",
  multi_select: "Select all that apply",
  fill_blank: "Fill in the blank",
  numeric: "Numeric",
};

export const qType = (q: { type?: string | null }): QuizQuestionType =>
  (q.type && q.type in TYPE_LABEL ? q.type : "mcq") as QuizQuestionType;

export const emptyAnswer = (q: DocQuizQuestion): QuizAnswer => {
  const t = qType(q);
  if (t === "multi_select") return [];
  if (t === "fill_blank" || t === "numeric") return "";
  return -1;
};

export const isAnswered = (q: DocQuizQuestion, a: QuizAnswer): boolean => {
  const t = qType(q);
  if (t === "multi_select") return Array.isArray(a) && a.length > 0;
  if (t === "fill_blank" || t === "numeric") return typeof a === "string" && a.trim() !== "";
  return typeof a === "number" && a >= 0;
};

export const TypeChip: React.FC<{ type?: string | null }> = ({ type }) => (
  <span className="chip bg-slate-100 text-slate-600 dark:bg-slate-700/60 dark:text-slate-300">{TYPE_LABEL[qType({ type })]}</span>
);

const hindi = (q: DocQuizQuestion) => q.translations?.hi;

/** Text in the chosen language; "bi" returns [english, hindi]. */
const pick = (en: string, hi: string | undefined, lang: QuizLang): [string, string | null] => {
  if (!hi || lang === "en") return [en, null];
  if (lang === "hi") return [hi, null];
  return [en, hi === en ? null : hi];
};

const BLANK_RE = /_{3,}/;

const Stem: React.FC<{ text: string; blank?: React.ReactNode }> = ({ text, blank }) => {
  if (!blank || !BLANK_RE.test(text)) return <>{text}</>;
  const [a, b] = text.split(BLANK_RE, 2);
  return <>{a}{blank}{b}</>;
};

interface Props {
  q: DocQuizQuestion;
  index: number;
  answer: QuizAnswer;
  onChange: (a: QuizAnswer) => void;
  lang?: QuizLang;
  compact?: boolean;
}

const QuizQuestionInput: React.FC<Props> = ({ q, index, answer, onChange, lang = "en", compact = false }) => {
  const t = qType(q);
  const tr = hindi(q);
  const [stem, stemHi] = pick(q.question, tr?.question, lang);
  const options = q.options ?? [];
  const optText = (i: number) => pick(options[i], tr?.options?.[i], lang);
  const unit = pick(q.unit ?? "", tr?.unit, lang)[0];
  const name = `q-${index}`;

  const optionBox = (i: number, selected: boolean, control: React.ReactNode) => {
    const [en, hi] = optText(i);
    return (
      <label
        key={i}
        className={`flex cursor-pointer items-center gap-4 rounded-xl border-2 transition-all ${compact ? "p-3" : "p-4"} ${
          selected
            ? "border-gov-navy bg-accent-blue-soft dark:border-sky-500 dark:bg-sky-900/20"
            : "border-gov-line hover:border-gov-blue/40 dark:border-slate-700 dark:hover:border-slate-600"
        }`}
      >
        {control}
        <span className={`font-medium ${compact ? "text-sm" : ""} ${selected ? "text-gov-navy dark:text-sky-100" : "text-slate-700 dark:text-slate-300"}`}>
          {en}
          {hi && <span className="block text-[12.5px] font-normal text-slate-500 dark:text-slate-400">{hi}</span>}
        </span>
      </label>
    );
  };

  const textInput = (
    <input
      type="text"
      inputMode={t === "numeric" ? "decimal" : "text"}
      aria-label={t === "numeric" ? `Answer to question ${index + 1}` : `Missing word for question ${index + 1}`}
      value={typeof answer === "string" ? answer : ""}
      onChange={(e) => onChange(e.target.value)}
      placeholder={t === "numeric" ? "Enter a number" : "type the missing term"}
      className={`rounded-lg border-2 border-gov-line bg-white px-3 py-1.5 text-[15px] font-medium text-gov-ink outline-none focus:border-gov-navy dark:border-slate-600 dark:bg-slate-900 dark:text-white dark:focus:border-sky-500 ${
        t === "numeric" ? "w-44" : "mx-1 w-48"
      }`}
    />
  );

  return (
    // min-w-0: a fieldset defaults to min-width: min-content, so one long word would
    // widen the card past its column.
    <fieldset className={`min-w-0 ${compact ? "rounded-xl border border-slate-100 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800/60" : "panel p-6 md:p-7"}`}>
      {/* A <legend> is drawn straddling the fieldset's top border, so a question that
          wraps to two lines (common for video-generated ones) had its first line
          above the card. Floating it lays it out inside the card like any block,
          and keeps the fieldset/legend grouping for screen readers. */}
      <legend className={`float-left w-full ${compact ? "mb-3 text-[14.5px]" : "mb-5 text-[16.5px]"} font-semibold text-gov-ink dark:text-slate-100`}>
        <span className="mr-3 text-slate-400">{index + 1}.</span>
        {t === "fill_blank" ? <Stem text={stem} blank={textInput} /> : stem}
        <span className="ml-2 inline-flex flex-wrap gap-1.5 align-middle">
          <TypeChip type={t} />
          {q.difficulty && <DifficultyChip difficulty={q.difficulty} />}
        </span>
        {stemHi && <span className="mt-1 block text-[14px] font-normal text-slate-500 dark:text-slate-400">{stemHi}</span>}
      </legend>
      <div className="clear-both" aria-hidden="true" />

      {(t === "mcq" || t === "true_false") && (
        <div className={t === "true_false" ? "grid grid-cols-2 gap-3" : "space-y-3"} role="radiogroup">
          {options.map((_, i) => {
            const selected = answer === i;
            return optionBox(i, selected, (
              <>
                <input type="radio" name={name} className="sr-only" checked={selected} onChange={() => onChange(i)} />
                <span className={`flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full border-2 ${selected ? "border-gov-navy dark:border-sky-400" : "border-slate-300 dark:border-slate-600"}`}>
                  {selected && <span className="h-2.5 w-2.5 rounded-full bg-gov-navy dark:bg-sky-400" />}
                </span>
              </>
            ));
          })}
        </div>
      )}

      {t === "multi_select" && (
        <div className="space-y-3">
          <p className="text-[12px] font-medium text-slate-500 dark:text-slate-400">Select every correct option — all must be right to score.</p>
          {options.map((_, i) => {
            const chosen = Array.isArray(answer) ? answer : [];
            const selected = chosen.includes(i);
            const toggle = () => onChange(selected ? chosen.filter((x) => x !== i) : [...chosen, i].sort((a, b) => a - b));
            return optionBox(i, selected, (
              <>
                <input type="checkbox" className="sr-only" checked={selected} onChange={toggle} />
                <span className={`flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-md border-2 ${selected ? "border-gov-navy bg-gov-navy dark:border-sky-400 dark:bg-sky-400" : "border-slate-300 dark:border-slate-600"}`}>
                  {selected && <span className="text-[11px] font-bold leading-none text-white dark:text-slate-900">✓</span>}
                </span>
              </>
            ));
          })}
        </div>
      )}

      {t === "fill_blank" && !BLANK_RE.test(stem) && <div>{textInput}</div>}

      {t === "numeric" && (
        <div className="flex items-center gap-2.5">
          {textInput}
          {unit && <span className="text-[14px] font-semibold text-slate-500 dark:text-slate-400">{unit}</span>}
        </div>
      )}
    </fieldset>
  );
};

export default QuizQuestionInput;
