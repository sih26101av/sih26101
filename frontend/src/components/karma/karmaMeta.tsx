/**
 * FILE: src/components/karma/karmaMeta.tsx
 *
 * Display config (label, icon, colours) per Karma event type — shared by the
 * Karma & Rewards page and the compact KarmaCard. Point values are NOT kept
 * here; they come from GET /api/v1/karma/rules.
 */

import React from "react";
import {
  Star, BookOpen, CheckCircle2, Award, Zap, Gift, CalendarCheck, Flame, Brain, Settings2,
} from "lucide-react";
import type { KarmaEventType } from "../../types/domain";

export interface KarmaEventMeta {
  label: string;
  icon: React.ReactNode;
  colorClasses: string;
}

export const EVENT_META: Record<KarmaEventType, KarmaEventMeta> = {
  DAILY_LOGIN: {
    label: "Daily Check-in",
    icon: <CalendarCheck size={12} />,
    colorClasses: "text-teal-600 bg-teal-50 dark:bg-teal-900/20 border-teal-200 dark:border-teal-800/40",
  },
  STREAK_BONUS: {
    label: "Streak Bonus",
    icon: <Flame size={12} />,
    colorClasses: "text-rose-600 bg-rose-50 dark:bg-rose-900/20 border-rose-200 dark:border-rose-800/40",
  },
  SELF_REGISTRATION: {
    label: "Registration Bonus",
    icon: <Star size={12} />,
    colorClasses: "text-amber-500 bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800/40",
  },
  FIRST_ENROLLMENT: {
    label: "First Enrolment",
    icon: <BookOpen size={12} />,
    colorClasses: "text-sky-600 bg-sky-50 dark:bg-sky-900/20 border-sky-200 dark:border-sky-800/40",
  },
  COURSE_COMPLETION: {
    label: "Course Completion",
    icon: <CheckCircle2 size={12} />,
    colorClasses: "text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800/40",
  },
  ASSESSMENT_PASSED: {
    label: "Assessment Passed",
    icon: <Award size={12} />,
    colorClasses: "text-fuchsia-600 bg-fuchsia-50 dark:bg-fuchsia-900/20 border-fuchsia-200 dark:border-fuchsia-800/40",
  },
  DIAGNOSTIC_COMPLETED: {
    label: "Diagnostic Completed",
    icon: <Brain size={12} />,
    colorClasses: "text-violet-600 bg-violet-50 dark:bg-violet-900/20 border-violet-200 dark:border-violet-800/40",
  },
  COURSE_RATED: {
    label: "Course Feedback",
    icon: <Zap size={12} />,
    colorClasses: "text-blue-600 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800/40",
  },
  CBP_BONUS: {
    label: "CBP Mandated Bonus",
    icon: <Gift size={12} />,
    colorClasses: "text-orange-600 bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800/40",
  },
  ADMIN_ADJUSTMENT: {
    label: "Admin Adjustment",
    icon: <Settings2 size={12} />,
    colorClasses: "text-slate-600 bg-slate-50 dark:bg-slate-800/60 border-slate-200 dark:border-slate-700",
  },
};

export const metaFor = (t: KarmaEventType): KarmaEventMeta =>
  EVENT_META[t] ?? EVENT_META.COURSE_COMPLETION;

/** "+5", "−3" or "0" */
export const formatPoints = (p: number): string => (p > 0 ? `+${p}` : p < 0 ? `−${-p}` : "0");
