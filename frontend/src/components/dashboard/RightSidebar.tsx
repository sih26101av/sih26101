/**
 * FILE: src/components/dashboard/RightSidebar.tsx
 *
 * Two-card right sidebar for the Learner Dashboard:
 * 1. KarmaCard   — FULLY LIVE. Reads from the /api/v1/learner/{id}/karma endpoint.
 *                  Displays: total KP, monthly cap bar, per-event breakdown pills,
 *                  scrollable passbook (last 10 events), streak, CBP claim CTA.
 * 2. CareerReadinessCard — LIVE readiness for the next role (gaps against its FRAC
 *                  requirements) + the office's tier ladder. Replaces the static 82% card.
 */

import React, { useState } from "react";
import {
  Flame, Clock, ChevronRight, BarChart2, Gift, Loader2, AlertCircle,
} from "lucide-react";
import { claimCbpBonus } from "../../services/api";
import CareerReadinessCard from "./CareerReadinessCard";
import type { KarmaLedger, KarmaEventType } from "../../types/domain";
import { EVENT_META, formatPoints, metaFor } from "../karma/karmaMeta";


// ─── Types ────────────────────────────────────────────────────────────────────

interface RightSidebarProps {
  karma: KarmaLedger | null;
  userId: string;
}

// Canonical display order for the breakdown pills
const PILL_ORDER: KarmaEventType[] = [
  "DAILY_LOGIN",
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
  const meta = metaFor(eventType);
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
      <span className={`text-[13px] font-black flex-shrink-0 ${points > 0 ? "text-emerald-600 dark:text-emerald-400" : "text-slate-400"}`}>
        {formatPoints(points)}
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
    <div className="gov-card gov-card-hover p-6">

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
                    {earned > 0 ? `+${earned}` : "—"}
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


// ─── Exported RightSidebar ────────────────────────────────────────────────────

const RightSidebar: React.FC<RightSidebarProps> = ({ karma, userId }) => (
  <div className="flex flex-col gap-5">
    <KarmaCard karma={karma} userId={userId} />
    <CareerReadinessCard userId={userId} />
  </div>
);

export default RightSidebar;
