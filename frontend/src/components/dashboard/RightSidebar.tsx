/**
 * FILE: src/components/dashboard/RightSidebar.tsx
 *
 * Two-card right sidebar for the Learner Dashboard:
 * 1. iGOT Karma Points & Gamification
 * 2. Career Readiness (FRAC Role Match) with Recharts Radial/Donut Chart + Milestone Stepper
 */

import React from "react";
import {
  Flame, CheckCircle2, Clock, ChevronRight, Star, Zap, Award, TrendingUp,
} from "lucide-react";
import {
  RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis
} from "recharts";

// ─── Types ─────────────────────────────────────────────────────────────────────
interface KarmaActivity {
  label: string;
  points: number;
  icon: React.ReactNode;
  color: string;
}

interface MilestoneStep {
  role: string;
  status: "completed" | "active" | "future";
  level: string;
}

// ─── Static Data ───────────────────────────────────────────────────────────────
const karmaActivities: KarmaActivity[] = [
  { label: "Registration Bonus",      points: 5,  icon: <Star size={12} />,   color: "text-amber-500 bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800/40" },
  { label: "Course Completion",       points: 5,  icon: <CheckCircle2 size={12} />, color: "text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800/40" },
  { label: "Course Feedback",         points: 2,  icon: <Zap size={12} />,    color: "text-blue-600 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800/40" },
  { label: "Daily Login Streak",      points: 1,  icon: <Flame size={12} />,  color: "text-orange-500 bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800/40" },
  { label: "Assessment Completed",    points: 10, icon: <Award size={12} />,  color: "text-fuchsia-600 bg-fuchsia-50 dark:bg-fuchsia-900/20 border-fuchsia-200 dark:border-fuchsia-800/40" },
];

const totalKP = karmaActivities.reduce((s, a) => s + a.points, 0) + 102;

const milestones: MilestoneStep[] = [
  { role: "Junior Statistical Officer", level: "Level 6",  status: "completed" },
  { role: "Senior Statistical Officer", level: "Level 7",  status: "active"    },
  { role: "Deputy Director (Stats)",    level: "Level 8",  status: "future"    },
];

const CAREER_MATCH_PCT = 82;

// ─── Donut Center Label ─────────────────────────────────────────────────────────
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

// ─── Milestone Stepper ──────────────────────────────────────────────────────────
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
            <p className={`text-[13px] font-bold leading-tight ${
              isActive ? "text-indigo-700 dark:text-indigo-400" : "text-slate-800 dark:text-slate-200"
            }`}>
              {m.role}
            </p>
            <p className={`text-[11px] font-medium mt-0.5 ${
              isActive ? "text-indigo-400 dark:text-indigo-500" : "text-slate-400 dark:text-slate-500"
            }`}>
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

// ─── Card 1: Karma Points ──────────────────────────────────────────────────────
const KarmaCard: React.FC = () => (
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
    <div className="flex items-baseline gap-1.5 mb-1">
      <span className="text-[42px] font-black leading-none bg-gradient-to-br from-indigo-600 to-purple-500 dark:from-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
        {totalKP}
      </span>
      <span className="text-[16px] font-bold text-slate-500 dark:text-slate-400">KP</span>
    </div>
    <p className="text-[11px] text-slate-400 dark:text-slate-500 mb-4">Total verified Karma Points earned</p>

    {/* Activity Pills */}
    <div className="flex flex-col gap-2">
      {karmaActivities.map((a) => (
        <div key={a.label} className={`flex items-center justify-between text-[12px] font-semibold px-3 py-1.5 rounded-lg border ${a.color} transition-colors duration-300`}>
          <span className="flex items-center gap-1.5">
            {a.icon}
            {a.label}
          </span>
          <span className="font-black">+{a.points}</span>
        </div>
      ))}
    </div>

    {/* Streak */}
    <div className="mt-4 flex items-center gap-2 pt-3 border-t border-slate-100 dark:border-slate-700/50">
      <Flame size={14} className="text-orange-400" />
      <span className="text-[12px] font-bold text-slate-700 dark:text-slate-300">
        Current Streak: <span className="text-orange-500">3 Days</span>
      </span>
      <Clock size={12} className="text-slate-400 ml-auto" />
      <span className="text-[11px] text-slate-400 dark:text-slate-500">Resets daily</span>
    </div>
  </div>
);

// ─── Card 2: Career Readiness ──────────────────────────────────────────────────
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
            {/* Track (background ring) */}
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

      {/* Divider */}
      <div className="border-t border-slate-100 dark:border-slate-700/50 mb-3" />

      {/* Milestone Stepper */}
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

// ─── Exported RightSidebar ─────────────────────────────────────────────────────
const RightSidebar: React.FC = () => (
  <div className="flex flex-col gap-5">
    <KarmaCard />
    <CareerCard />
  </div>
);

export default RightSidebar;
