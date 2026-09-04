/**
 * FILE: src/components/dashboard/RightSidebar.tsx
 *
 * Two-card right sidebar for the Learner Dashboard:
 * 1. KarmaCard   — FULLY LIVE. Reads from the /api/v1/learner/{id}/karma endpoint.
 *                  Displays: total KP, monthly cap bar, per-event breakdown pills,
 *                  scrollable passbook (last 10 events), streak, CBP claim CTA.
 * 2. CareerCard  — FRAC Role Match donut chart + Career Pathway milestone stepper.
 */

import React, { useState } from "react";
import {
  Flame, CheckCircle2, Clock, ChevronRight, Star, Zap, Award, TrendingUp,
  BookOpen, BarChart2, Gift, Loader2, AlertCircle,
} from "lucide-react";
import {
  RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis,
} from "recharts";
import { claimCbpBonus } from "../../services/api";
import type { KarmaLedger, KarmaEventType } from "../../types/domain";


// ─── Types ────────────────────────────────────────────────────────────────────

interface RightSidebarProps {
  karma: KarmaLedger | null;
  userId: string;
}

interface MilestoneStep {
  role: string;
  status: "completed" | "active" | "future";
  level: string;
}


// ─── Static career data ───────────────────────────────────────────────────────

const milestones: MilestoneStep[] = [
  { role: "Junior Statistical Officer", level: "Level 6",  status: "completed" },
  { role: "Senior Statistical Officer", level: "Level 7",  status: "active"    },
  { role: "Deputy Director (Stats)",    level: "Level 8",  status: "future"    },
];

const CAREER_MATCH_PCT = 82;


// ─── Event type → display config ─────────────────────────────────────────────

const EVENT_META: Record<KarmaEventType, { label: string; icon: React.ReactNode; colorClasses: string; pts: number }> = {
  SELF_REGISTRATION: {
    label: "Registration Bonus",
    pts: 5,
    icon: <Star size={12} />,
    colorClasses: "text-amber-500 bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800/40",
  },
  FIRST_ENROLLMENT: {
    label: "First Enrollment",
    pts: 5,
    icon: <BookOpen size={12} />,
    colorClasses: "text-sky-600 bg-sky-50 dark:bg-sky-900/20 border-sky-200 dark:border-sky-800/40",
  },
  COURSE_COMPLETION: {
    label: "Course Completion",
    pts: 5,
    icon: <CheckCircle2 size={12} />,
    colorClasses: "text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800/40",
  },
  ASSESSMENT_PASSED: {
    label: "Assessment Passed",
    pts: 5,
    icon: <Award size={12} />,
    colorClasses: "text-fuchsia-600 bg-fuchsia-50 dark:bg-fuchsia-900/20 border-fuchsia-200 dark:border-fuchsia-800/40",
  },
  COURSE_RATED: {
    label: "Course Feedback",
    pts: 2,
    icon: <Zap size={12} />,
    colorClasses: "text-blue-600 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800/40",
  },
  CBP_BONUS: {
    label: "CBP Mandated Bonus",
    pts: 10,
    icon: <Gift size={12} />,
    colorClasses: "text-orange-600 bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800/40",
  },
};

// Canonical display order for the breakdown pills
const PILL_ORDER: KarmaEventType[] = [
  "SELF_REGISTRATION",
  "COURSE_COMPLETION",
  "ASSESSMENT_PASSED",
  "COURSE_RATED",
  "CBP_BONUS",
];


// ─── Passbook row ─────────────────────────────────────────────────────────────

const PassbookRow: React.FC<{
  eventType: KarmaEventType;
  points: number;
  createdAt: string;
  isCbp: boolean;
}> = ({ eventType, points, createdAt, isCbp }) => {
  const meta = EVENT_META[eventType] ?? EVENT_META.COURSE_COMPLETION;
  const date = new Date(createdAt);
  const dateStr = date.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
  const timeStr = date.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });

  return (
    <div className="flex items-center justify-between gap-2 py-2 border-b border-slate-100 dark:border-slate-700/40 last:border-0">
      <div className={`w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0 border ${meta.colorClasses}`}>
        {meta.icon}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-[11px] font-semibold text-slate-700 dark:text-slate-300 truncate">
          {meta.label}{isCbp && <span className="ml-1 text-orange-500">★ CBP</span>}
        </p>
        <p className="text-[10px] text-slate-400">{dateStr} · {timeStr}</p>
      </div>
      <span className="text-[13px] font-black text-emerald-600 dark:text-emerald-400 flex-shrink-0">
        +{points}
      </span>
    </div>
  );
};


// ─── Monthly Cap Bar ──────────────────────────────────────────────────────────

const MonthlyCapBar: React.FC<{ used: number; cap: number }> = ({ used, cap }) => {
  const pct = Math.min(100, (used / cap) * 100);
  const isFull = used >= cap;
  return (
    <div className="mt-3 mb-1">
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest">
          Monthly Free Courses
        </span>
        <span className={`text-[11px] font-black ${isFull ? "text-red-500" : "text-slate-700 dark:text-slate-300"}`}>
          {used} / {cap}
        </span>
      </div>
      <div className="h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${
            isFull
              ? "bg-red-400"
              : pct >= 75
              ? "bg-orange-400"
              : "bg-emerald-400"
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
      {isFull && (
        <p className="text-[10px] text-red-500 font-semibold mt-1">
          Cap reached — CBP courses still earn points!
        </p>
      )}
    </div>
  );
};


// ─── Card 1: Live Karma Card ──────────────────────────────────────────────────

const KarmaCard: React.FC<{ karma: KarmaLedger | null; userId: string }> = ({ karma, userId }) => {
  const [claimLoading, setClaimLoading] = useState(false);
  const [claimMsg, setClaimMsg] = useState<string | null>(null);
  const [showPassbook, setShowPassbook] = useState(false);

  const isLoading = karma === null;
  const total  = karma?.totalPoints ?? 0;
  const streak = karma?.streak ?? 0;
  const monthly = karma?.monthlyUsage ?? { used: 0, cap: 4, remaining: 4 };
  const ledger  = karma?.ledger ?? [];
  const breakdown = karma?.breakdown ?? {};

  // Find any completed CBP course not yet claimed — use first courseId from ledger
  const claimableCourse = ledger.find(
    (e) => e.eventType === "COURSE_COMPLETION" && e.isCbp && e.courseId
  );

  const handleCbpClaim = async () => {
    if (!claimableCourse?.courseId) return;
    setClaimLoading(true);
    setClaimMsg(null);
    try {
      const res = await claimCbpBonus(userId, claimableCourse.courseId);
      setClaimMsg(
        res.alreadyClaimed
          ? "Already claimed for this course."
          : `+${res.pointsAwarded} KP added! New balance: ${res.newBalance}`
      );
    } catch {
      setClaimMsg("Claim failed. Please try again.");
    } finally {
      setClaimLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-slate-800/40 rounded-2xl border border-slate-200 dark:border-slate-700/50 shadow-sm p-7 transition-colors duration-300">

      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-orange-50 dark:bg-orange-900/30 flex items-center justify-center">
            <Flame size={15} className="text-orange-500" />
          </div>
          <h3 className="text-slate-900 dark:text-white font-extrabold text-[14px] tracking-tight">
            Karma Points &amp; Activity
          </h3>
        </div>
        <span className="text-[10px] font-bold text-orange-500 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800/40 px-2 py-0.5 rounded-full">
          iGOT
        </span>
      </div>

      {/* Total */}
      {isLoading ? (
        <div className="flex items-center gap-2 mb-4">
          <Loader2 size={20} className="text-indigo-400 animate-spin" />
          <span className="text-sm text-slate-400">Loading karma…</span>
        </div>
      ) : (
        <>
          <div className="flex items-baseline gap-1.5 mb-0.5">
            <span className="text-[42px] font-black leading-none bg-gradient-to-br from-indigo-600 to-purple-500 dark:from-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
              {total}
            </span>
            <span className="text-[16px] font-bold text-slate-500 dark:text-slate-400">KP</span>
          </div>
          <p className="text-[11px] text-slate-400 dark:text-slate-500 mb-3">Total verified Karma Points earned</p>

          {/* Monthly cap bar */}
          <MonthlyCapBar used={monthly.used} cap={monthly.cap} />

          {/* Breakdown pills */}
          <div className="flex flex-col gap-2 mt-4">
            {PILL_ORDER.map((type) => {
              const meta = EVENT_META[type];
              const earned = breakdown[type] ?? 0;
              return (
                <div
                  key={type}
                  className={`flex items-center justify-between text-[12px] font-semibold px-3 py-1.5 rounded-lg border ${meta.colorClasses} transition-colors duration-300`}
                >
                  <span className="flex items-center gap-1.5">
                    {meta.icon}
                    {meta.label}
                  </span>
                  <span className="font-black">
                    {earned > 0 ? `+${earned}` : `+${meta.pts} each`}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Streak */}
          <div className="mt-4 flex items-center gap-2 pt-3 border-t border-slate-100 dark:border-slate-700/50">
            <Flame size={14} className="text-orange-400" />
            <span className="text-[12px] font-bold text-slate-700 dark:text-slate-300">
              Streak:{" "}
              <span className="text-orange-500">{streak} {streak === 1 ? "Day" : "Days"}</span>
            </span>
            <Clock size={12} className="text-slate-400 ml-auto" />
            <span className="text-[11px] text-slate-400 dark:text-slate-500">Resets daily</span>
          </div>

          {/* CBP Claim CTA */}
          {claimableCourse && (
            <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-700/50">
              <button
                onClick={handleCbpClaim}
                disabled={claimLoading}
                className="w-full flex items-center justify-center gap-2 py-2 rounded-xl bg-orange-50 dark:bg-orange-900/20 border border-orange-300 dark:border-orange-700 text-orange-700 dark:text-orange-400 text-[12px] font-bold hover:bg-orange-100 dark:hover:bg-orange-900/40 transition-colors disabled:opacity-60"
              >
                {claimLoading
                  ? <Loader2 size={13} className="animate-spin" />
                  : <Gift size={13} />}
                Claim +10 CBP Bonus
              </button>
              {claimMsg && (
                <p className="text-[11px] mt-1.5 text-center text-slate-500 dark:text-slate-400">{claimMsg}</p>
              )}
            </div>
          )}

          {/* Passbook Toggle */}
          {ledger.length > 0 && (
            <div className="mt-3">
              <button
                onClick={() => setShowPassbook((v) => !v)}
                className="w-full flex items-center justify-between text-[11px] font-bold text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors pt-2 border-t border-slate-100 dark:border-slate-700/50"
              >
                <span className="flex items-center gap-1.5">
                  <BarChart2 size={12} />
                  Learner Passbook ({ledger.length} events)
                </span>
                <ChevronRight
                  size={13}
                  className={`transition-transform duration-200 ${showPassbook ? "rotate-90" : ""}`}
                />
              </button>
              {showPassbook && (
                <div className="mt-2 max-h-48 overflow-y-auto pr-1 custom-scrollbar">
                  {ledger.map((entry) => (
                    <PassbookRow
                      key={entry.eventId}
                      eventType={entry.eventType}
                      points={entry.pointsAwarded}
                      createdAt={entry.createdAt}
                      isCbp={entry.isCbp}
                    />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Empty state */}
          {ledger.length === 0 && (
            <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-700/50 text-center">
              <AlertCircle size={20} className="mx-auto text-slate-300 mb-1" />
              <p className="text-[11px] text-slate-400">No events yet. Complete a course to start earning!</p>
            </div>
          )}
        </>
      )}
    </div>
  );
};


// ─── Donut Center Label ────────────────────────────────────────────────────────

const DonutCenterLabel: React.FC<{ value: number }> = ({ value }) => (
  <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
    <span className="text-[28px] font-black leading-none bg-gradient-to-br from-indigo-600 to-fuchsia-500 bg-clip-text text-transparent dark:from-indigo-400 dark:to-fuchsia-400">
      {value}%
    </span>
    <span className="text-[10px] text-slate-500 dark:text-slate-400 font-semibold mt-0.5 tracking-wide uppercase">
      FRAC Match
    </span>
  </div>
);


// ─── Milestone Stepper ─────────────────────────────────────────────────────────

const MilestoneStepper: React.FC = () => (
  <div className="flex flex-col gap-0 mt-2">
    {milestones.map((m, i) => {
      const isCompleted = m.status === "completed";
      const isActive    = m.status === "active";
      const isFuture    = m.status === "future";
      return (
        <div key={i} className="flex items-stretch gap-3">
          {/* Spine */}
          <div className="flex flex-col items-center">
            <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 border-2 transition-colors duration-300 ${
              isCompleted ? "bg-emerald-500 border-emerald-500" :
              isActive    ? "bg-indigo-600 border-indigo-600" :
                            "bg-white dark:bg-slate-800 border-slate-300 dark:border-slate-600"
            }`}>
              {isCompleted && <CheckCircle2 size={11} className="text-white" strokeWidth={3} />}
              {isActive    && <div className="w-2 h-2 bg-white rounded-full" />}
              {isFuture    && <div className="w-2 h-2 bg-slate-300 dark:bg-slate-600 rounded-full" />}
            </div>
            {i < milestones.length - 1 && (
              <div className={`w-0.5 flex-1 my-1 ${isCompleted ? "bg-emerald-300 dark:bg-emerald-700" : "bg-slate-200 dark:bg-slate-700"}`} />
            )}
          </div>

          {/* Text */}
          <div className={`pb-4 transition-opacity duration-300 ${isFuture ? "opacity-40" : "opacity-100"}`}>
            <p className={`text-[13px] font-bold leading-tight ${isActive ? "text-indigo-700 dark:text-indigo-400" : "text-slate-800 dark:text-slate-200"}`}>
              {m.role}
            </p>
            <p className={`text-[11px] font-medium mt-0.5 ${isActive ? "text-indigo-400 dark:text-indigo-500" : "text-slate-400 dark:text-slate-500"}`}>
              {m.level}
              {isCompleted && <span className="ml-2 text-emerald-500">✓ Current</span>}
              {isActive    && <span className="ml-2 text-indigo-500">← Target</span>}
            </p>
          </div>
        </div>
      );
    })}
  </div>
);


// ─── Card 2: Career Readiness ─────────────────────────────────────────────────

const CareerCard: React.FC = () => {
  const chartData = [{ name: "Match", value: CAREER_MATCH_PCT, fill: "url(#careerGrad)" }];

  return (
    <div className="bg-white dark:bg-slate-800/40 rounded-2xl border border-slate-200 dark:border-slate-700/50 shadow-sm p-7 transition-colors duration-300">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-indigo-50 dark:bg-indigo-900/30 flex items-center justify-center">
            <TrendingUp size={15} className="text-indigo-600 dark:text-indigo-400" />
          </div>
          <h3 className="text-slate-900 dark:text-white font-extrabold text-[14px] tracking-tight">
            Career Readiness
          </h3>
        </div>
        <span className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800/40 px-2 py-0.5 rounded-full">
          FRAC
        </span>
      </div>

      {/* Donut Chart */}
      <div className="relative h-[140px] w-full mb-2">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            cx="50%"
            cy="50%"
            innerRadius="70%"
            outerRadius="100%"
            startAngle={220}
            endAngle={-40}
            data={chartData}
            barSize={14}
          >
            <defs>
              <linearGradient id="careerGrad" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%"   stopColor="#6366f1" />
                <stop offset="100%" stopColor="#a855f7" />
              </linearGradient>
            </defs>
            <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
            <RadialBar
              background={{ fill: "#f1f5f9" }}
              dataKey="value"
              cornerRadius={8}
              angleAxisId={0}
            />
          </RadialBarChart>
        </ResponsiveContainer>
        <DonutCenterLabel value={CAREER_MATCH_PCT} />
      </div>

      <p className="text-[11px] text-center text-slate-400 dark:text-slate-500 mb-4">
        FRAC Competency Match · <span className="font-semibold text-indigo-500">Senior Statistical Officer</span>
      </p>

      <div className="border-t border-slate-100 dark:border-slate-700/50 mb-3" />

      <div className="flex items-center gap-2 mb-3">
        <ChevronRight size={13} className="text-slate-400" />
        <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest">
          Career Pathway
        </span>
      </div>
      <MilestoneStepper />
    </div>
  );
};


// ─── Exported RightSidebar ────────────────────────────────────────────────────

const RightSidebar: React.FC<RightSidebarProps> = ({ karma, userId }) => (
  <div className="flex flex-col gap-5">
    <KarmaCard karma={karma} userId={userId} />
    <CareerCard />
  </div>
);

export default RightSidebar;
