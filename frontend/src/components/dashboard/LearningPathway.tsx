/**
 * FILE: src/components/dashboard/LearningPathway.tsx
 *
 * Level-by-level learning path for one competency ("first this course, then
 * that one") and the study order across all gaps.
 * Data: GET /api/v1/learner/{id}/pathway (services/api.ts::fetchLearningPathways).
 */

import React from "react";
import { Link } from "react-router-dom";
import {
  AlertTriangle, BookOpen, Briefcase, ChevronDown, ChevronUp, ClipboardCheck, Clock,
  ListOrdered, PlayCircle, ShieldCheck, Sparkles, TrendingUp,
} from "lucide-react";
import type {
  LearningPathway, PathwayCourse, PathwayStep, PathwayStepKind, StudyPlan,
} from "../../types/domain";

const KIND_STYLE: Record<PathwayStepKind, { label: string; Icon: React.ElementType; dot: string; chip: string }> = {
  diagnostic: { label: "Check your level", Icon: ClipboardCheck, dot: "bg-violet-500",  chip: "bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300" },
  bridge:     { label: "Optional bridge",  Icon: BookOpen,       dot: "bg-slate-400",   chip: "bg-slate-100 dark:bg-slate-700/50 text-slate-600 dark:text-slate-300" },
  course:     { label: "Next level",       Icon: BookOpen,       dot: "bg-blue-500",    chip: "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300" },
  continue:   { label: "Continue",         Icon: PlayCircle,     dot: "bg-emerald-500", chip: "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300" },
  stretch:    { label: "Stretch step",     Icon: TrendingUp,     dot: "bg-amber-500",   chip: "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300" },
  optional:   { label: "Go further",       Icon: Sparkles,       dot: "bg-sky-400",     chip: "bg-sky-100 dark:bg-sky-900/30 text-sky-700 dark:text-sky-300" },
};

const CourseMeta: React.FC<{ course: PathwayCourse; hours: number | null }> = ({ course, hours }) => (
  <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[10px] text-slate-500 dark:text-slate-400">
    <span>{course.provider}</span>
    <span className="inline-flex items-center gap-1">
      <Clock size={10} /> {hours ?? course.durationHours}h
      {course.progressPercentage > 0 && ` left (${Math.round(course.progressPercentage)}% done)`}
    </span>
    {course.courseLevel != null && <span>FRAC Level {course.courseLevel}</span>}
    {course.isTpac && (
      <span className="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-semibold">
        <ShieldCheck size={10} /> NSSTA
      </span>
    )}
    {course.tagSupported === false && (
      <span className="inline-flex items-center gap-1 text-amber-600 dark:text-amber-400 font-semibold">
        <AlertTriangle size={10} /> Tag under review
      </span>
    )}
  </div>
);

const StepRow: React.FC<{ step: PathwayStep; isLast: boolean }> = ({ step, isLast }) => {
  const style = KIND_STYLE[step.kind];
  const { Icon } = style;
  return (
    <li className="relative pl-7 pb-4">
      {!isLast && <span className="absolute left-[9px] top-5 bottom-0 w-px bg-slate-200 dark:bg-slate-700" />}
      <span className={`absolute left-0 top-0.5 w-[19px] h-[19px] rounded-full flex items-center justify-center text-white ${style.dot}`}>
        <Icon size={11} />
      </span>

      <div className="flex flex-wrap items-center gap-2 mb-1">
        <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500">Step {step.order}</span>
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${style.chip}`}>{style.label}</span>
        {step.kind !== "diagnostic" && (
          <span className="text-[10px] font-mono text-slate-500 dark:text-slate-400">
            L{step.fromLevel} → L{step.toLevel}
          </span>
        )}
      </div>

      {step.course ? (
        <>
          <p className="text-[13px] font-semibold text-slate-800 dark:text-slate-100 leading-snug">{step.course.title}</p>
          <CourseMeta course={step.course} hours={step.hours} />
        </>
      ) : (
        <Link
          to="/assessment"
          className="inline-flex items-center gap-1.5 text-[11px] font-bold text-violet-700 dark:text-violet-300 hover:underline"
        >
          <ClipboardCheck size={12} /> Take the practice assessment →
        </Link>
      )}

      <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">{step.reason}</p>
      {step.levelDescriptor && step.kind !== "diagnostic" && (
        <p className="text-[11px] text-slate-600 dark:text-slate-300 mt-1 italic">
          After this: {step.levelDescriptor}
        </p>
      )}
      {step.alternatives.length > 0 && (
        <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-1">
          Alternatives: {step.alternatives.map(a => a.title).join(" · ")}
        </p>
      )}
    </li>
  );
};

export const PathwayLadder: React.FC<{ pathway: LearningPathway }> = ({ pathway }) => {
  const [showBridge, setShowBridge] = React.useState(false);
  const bridge = pathway.steps.filter(s => s.kind === "bridge");
  const visible = pathway.steps.filter(s => s.kind !== "bridge" || showBridge);

  return (
    <div className="mt-4 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50/60 dark:bg-slate-900/30 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
        <p className="text-[12px] font-bold text-slate-700 dark:text-slate-200">
          Learning path · Level {pathway.startLevel} → {pathway.targetLevel}
        </p>
        {pathway.totalHours > 0 && (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-slate-500 dark:text-slate-400">
            <Clock size={11} /> {pathway.totalHours}h to target
          </span>
        )}
      </div>

      {pathway.crosswalk?.method === "semantic_crosswalk" && (
        <p className="text-[10px] text-slate-500 dark:text-slate-400 mb-2">
          Courses come from the catalogue competency “{pathway.crosswalk.catalogueName}”, matched by name
          similarity ({(pathway.crosswalk.similarity ?? 0).toFixed(2)}) — not yet confirmed by a reviewer.
        </p>
      )}
      {pathway.message && (
        <p className="text-[11px] text-amber-700 dark:text-amber-400 mb-2 flex items-start gap-1.5">
          <AlertTriangle size={12} className="mt-0.5 shrink-0" /> {pathway.message}
        </p>
      )}
      {pathway.coverageGaps.length > 0 && pathway.status !== "no_content" && (
        <p className="text-[10px] text-slate-500 dark:text-slate-400 mb-2">
          No catalogue course exists at Level {pathway.coverageGaps.join(", ")}; the path bridges it with a stretch step.
        </p>
      )}
      {bridge.length > 0 && (
        <button
          onClick={() => setShowBridge(v => !v)}
          className="mb-3 inline-flex items-center gap-1 text-[10px] font-semibold text-blue-600 dark:text-blue-400 hover:underline"
        >
          {showBridge ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
          {showBridge ? "Hide" : "Show"} {bridge.length} bridge course{bridge.length > 1 ? "s" : ""} for your
          self-reported levels ({pathway.bridgeHours}h)
        </button>
      )}

      {visible.length > 0 && (
        <ol className="mt-1">
          {visible.map((s, i) => <StepRow key={s.order} step={s} isLast={i === visible.length - 1} />)}
        </ol>
      )}
    </div>
  );
};

export const StudyPlanSummary: React.FC<{ plan: StudyPlan; maxSteps?: number }> = ({ plan, maxSteps = 5 }) => {
  const [expanded, setExpanded] = React.useState(false);
  if (plan.steps.length === 0 && plan.diagnostics.length === 0) return null;
  const steps = expanded ? plan.steps : plan.steps.slice(0, maxSteps);

  return (
    <div className="mb-6 rounded-xl border border-blue-100 dark:border-blue-900/50 bg-blue-50/50 dark:bg-blue-950/20 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
        <p className="flex items-center gap-2 text-[13px] font-bold text-slate-800 dark:text-slate-100">
          <ListOrdered size={15} className="text-blue-600 dark:text-blue-400" /> Suggested study order
        </p>
        {plan.totalHours > 0 && (
          <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">
            {plan.steps.length} course{plan.steps.length === 1 ? "" : "s"} · {plan.totalHours}h
          </span>
        )}
      </div>

      {plan.diagnostics.length > 0 && (
        <p className="text-[11px] text-violet-700 dark:text-violet-300 mb-2">
          First, confirm your level in {plan.diagnostics.length} competenc{plan.diagnostics.length === 1 ? "y" : "ies"}{" "}
          (<Link to="/assessment" className="font-semibold hover:underline">practice assessment</Link>):{" "}
          {plan.diagnostics.map(d => d.competencyName).join(", ")}.
        </p>
      )}

      {steps.length > 0 && (
        <ol className="space-y-1.5">
          {steps.map(s => (
            <li key={s.order} className="flex gap-2 text-[12px]">
              <span className="w-5 shrink-0 text-right font-bold text-blue-600 dark:text-blue-400">{s.order}.</span>
              <span className="text-slate-700 dark:text-slate-200">
                <span className="font-semibold">{s.title}</span>
                <span className="text-slate-400 dark:text-slate-500"> · {s.hours}h → </span>
                <span className="text-slate-500 dark:text-slate-400">
                  {s.advances.map(a => `${a.competencyName} L${a.toLevel}`).join(" · ")}
                </span>
                {s.selectedBy === "opportunity_tie_break" && (
                  <span
                    title="Near-tie on levels gained per hour: this gap came first because your office practises it more this cycle."
                    className="ml-1.5 inline-flex items-center gap-1 rounded-full bg-emerald-50 px-1.5 py-px text-[9px] font-bold text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300"
                  >
                    <Briefcase size={9} /> practise at work
                  </span>
                )}
              </span>
            </li>
          ))}
        </ol>
      )}
      {plan.steps.length > maxSteps && (
        <button
          onClick={() => setExpanded(v => !v)}
          className="mt-2 text-[10px] font-semibold text-blue-600 dark:text-blue-400 hover:underline"
        >
          {expanded ? "Show fewer" : `Show all ${plan.steps.length} courses`}
        </button>
      )}
      <p className="mt-2 text-[10px] text-slate-400 dark:text-slate-500">
        Ordered by level gained per hour on your highest-priority gaps; each competency's levels stay in order.
        Near-ties (within 10%) go to the gap you can practise at work this cycle.
      </p>
    </div>
  );
};
