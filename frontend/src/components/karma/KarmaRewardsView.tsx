/**
 * FILE: src/components/karma/KarmaRewardsView.tsx
 *
 * The "Karma & Rewards" tab of the learner dashboard.
 *   1. Check-in banner      — awards made by today's check-in (+1, streak bonus, iGOT sync)
 *   2. Stat tiles           — balance + level, today vs daily cap, streak, rank
 *   3. Level ladder         — progress to the next level
 *   4. How to earn          — rendered from GET /karma/rules (no hardcoded points)
 *   5. Rules & limits       — daily cap, per-activity limits, monthly cap, streak milestones
 *   6. Passbook             — full history, filter by activity, load more
 *   7. FAQ
 */

import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  Flame, Trophy, Target, Crown, CalendarCheck, Gift, Loader2, AlertCircle, Info,
  ShieldCheck, ListFilter, ChevronDown, Sparkles, Medal, BarChart2,
} from "lucide-react";
import { claimCbpBonus, fetchKarmaHistory, fetchKarmaLedger, fetchKarmaRules } from "../../services/api";
import type {
  KarmaEventType, KarmaLedger, KarmaRule, KarmaRules, KarmaTransaction,
} from "../../types/domain";
import { EVENT_META, formatPoints, metaFor } from "./karmaMeta";

interface Props {
  karma: KarmaLedger | null;
  userId: string;
}

const PAGE = 20;

const CATEGORY_LABEL: Record<KarmaRule["category"], { title: string; blurb: string }> = {
  learning:   { title: "Learning",   blurb: "The main way to earn — prove what you know." },
  engagement: { title: "Engagement", blurb: "Small, steady rewards for showing up." },
  milestone:  { title: "Milestones", blurb: "One-time and CBP bonuses." },
  admin:      { title: "Administrative", blurb: "" },
};

function timeUntil(iso: string): string {
  const ms = new Date(iso).getTime() - Date.now();
  if (!Number.isFinite(ms) || ms <= 0) return "soon";
  const h = Math.floor(ms / 3_600_000);
  const m = Math.floor((ms % 3_600_000) / 60_000);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

function fmtDate(iso: string): string {
  const d = new Date(iso);
  return `${d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })} · ${d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}`;
}


// ─── Small building blocks ─────────────────────────────────────────────────────

const Bar: React.FC<{ pct: number; tone?: "indigo" | "emerald" | "orange" | "red" }> = ({ pct, tone = "indigo" }) => {
  const color = { indigo: "bg-indigo-500", emerald: "bg-emerald-500", orange: "bg-orange-400", red: "bg-red-400" }[tone];
  return (
    <div className="h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
      <div className={`h-full rounded-full transition-all duration-700 ${color}`} style={{ width: `${Math.max(0, Math.min(100, pct))}%` }} />
    </div>
  );
};

const StatTile: React.FC<{ icon: React.ReactNode; label: string; children: React.ReactNode }> = ({ icon, label, children }) => (
  <div className="gov-card p-4 sm:p-5 flex flex-col gap-2 min-w-0">
    <div className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400">
      {icon}{label}
    </div>
    {children}
  </div>
);

const SectionTitle: React.FC<{ icon: React.ReactNode; title: string; subtitle?: string }> = ({ icon, title, subtitle }) => (
  <div className="flex items-start gap-2.5 mb-4">
    <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-900/30 flex items-center justify-center text-indigo-600 dark:text-indigo-400 flex-shrink-0">
      {icon}
    </div>
    <div>
      <h3 className="text-slate-900 dark:text-white font-extrabold text-[15px] tracking-tight">{title}</h3>
      {subtitle && <p className="text-[12px] text-slate-500 dark:text-slate-400 mt-0.5">{subtitle}</p>}
    </div>
  </div>
);


// ─── How to earn ───────────────────────────────────────────────────────────────

const RuleCard: React.FC<{ rule: KarmaRule; earned: number }> = ({ rule, earned }) => {
  const meta = metaFor(rule.eventType);
  const pts = rule.eventType === "STREAK_BONUS" ? "+5 to +50" : `+${rule.points}`;
  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-700/60 p-4 flex gap-3 bg-white/60 dark:bg-slate-800/40">
      <div className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 border ${meta.colorClasses}`}>
        {meta.icon}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <p className="text-[13px] font-bold text-slate-800 dark:text-slate-100">{rule.title}</p>
          <span className="text-[13px] font-black text-emerald-600 dark:text-emerald-400 whitespace-nowrap">{pts} KP</span>
        </div>
        <p className="text-[12px] text-slate-600 dark:text-slate-400 mt-0.5 leading-snug">{rule.how}</p>
        <div className="flex flex-wrap items-center gap-1.5 mt-2">
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700/60 text-slate-600 dark:text-slate-300">
            {rule.frequency}
          </span>
          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${rule.dailyCapped
            ? "bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400"
            : "bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400"}`}>
            {rule.dailyCapped ? "Counts toward daily cap" : "Cap-exempt"}
          </span>
          {earned !== 0 && (
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-900/20 text-indigo-700 dark:text-indigo-300">
              You've earned {formatPoints(earned)}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

const HowToEarn: React.FC<{ rules: KarmaRules | null; error: boolean; breakdown: KarmaLedger["breakdown"] }> = ({ rules, error, breakdown }) => {
  if (error) return <p className="text-[12px] text-red-500">Could not load the earning rules. Please refresh.</p>;
  if (!rules) return <div className="flex items-center gap-2 text-slate-400 text-sm"><Loader2 size={16} className="animate-spin" />Loading rules…</div>;
  const groups = (["learning", "engagement", "milestone"] as const).map((cat) => ({
    cat, items: rules.rules.filter((r) => r.category === cat),
  }));
  return (
    <div className="flex flex-col gap-5">
      {groups.map(({ cat, items }) => items.length > 0 && (
        <div key={cat}>
          <p className="text-[11px] font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400">{CATEGORY_LABEL[cat].title}</p>
          <p className="text-[12px] text-slate-400 dark:text-slate-500 mb-2">{CATEGORY_LABEL[cat].blurb}</p>
          <div className="grid gap-3 md:grid-cols-2">
            {items.map((r) => <RuleCard key={r.eventType} rule={r} earned={breakdown[r.eventType] ?? 0} />)}
          </div>
        </div>
      ))}
    </div>
  );
};


// ─── Rules & limits ────────────────────────────────────────────────────────────

const RulesAndLimits: React.FC<{ rules: KarmaRules | null; karma: KarmaLedger }> = ({ rules, karma }) => {
  const dailyCap = rules?.dailyCap ?? karma.today.cap;
  const limited = rules?.rules.filter((r) => r.perDay && r.eventType !== "DAILY_LOGIN") ?? [];
  const m = karma.monthlyUsage;
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <div className="rounded-xl border border-slate-200 dark:border-slate-700/60 p-4">
        <p className="text-[13px] font-bold text-slate-800 dark:text-slate-100 mb-1">Daily cap: {dailyCap} KP</p>
        <p className="text-[12px] text-slate-600 dark:text-slate-400 leading-snug mb-3">
          Learning and engagement activities can earn at most {dailyCap} KP per day. An award that would cross the cap
          is trimmed to what is left; anything above it is <b>not carried over</b>. Check-ins, streak, one-time,
          CBP and admin awards are exempt. The day resets at midnight IST.
        </p>
        <div className="flex items-center justify-between text-[11px] font-bold text-slate-500 dark:text-slate-400 mb-1">
          <span>Today</span><span>{karma.today.earned} / {dailyCap} KP</span>
        </div>
        <Bar pct={(karma.today.earned / dailyCap) * 100} tone={karma.today.remaining === 0 ? "red" : "indigo"} />
      </div>

      <div className="rounded-xl border border-slate-200 dark:border-slate-700/60 p-4">
        <p className="text-[13px] font-bold text-slate-800 dark:text-slate-100 mb-1">
          Monthly course limit: {m.cap} non-CBP completions
        </p>
        <p className="text-[12px] text-slate-600 dark:text-slate-400 leading-snug mb-3">
          Following iGOT Karmayogi rules, only {m.cap} non-CBP course completions earn points each calendar month.
          Courses mandated in your Capacity Building Plan always earn, and also earn the +10 CBP bonus.
        </p>
        <div className="flex items-center justify-between text-[11px] font-bold text-slate-500 dark:text-slate-400 mb-1">
          <span>This month</span><span>{m.used} / {m.cap}</span>
        </div>
        <Bar pct={(m.used / m.cap) * 100} tone={m.remaining === 0 ? "red" : m.used / m.cap >= 0.75 ? "orange" : "emerald"} />
      </div>

      <div className="rounded-xl border border-slate-200 dark:border-slate-700/60 p-4">
        <p className="text-[13px] font-bold text-slate-800 dark:text-slate-100 mb-2">Per-activity daily limits</p>
        <ul className="text-[12px] text-slate-600 dark:text-slate-400 space-y-1">
          {limited.map((r) => (
            <li key={r.eventType} className="flex justify-between gap-2">
              <span>{r.title}</span><span className="font-semibold">max {r.perDay} / day</span>
            </li>
          ))}
          <li className="flex justify-between gap-2"><span>Daily check-in</span><span className="font-semibold">1 / day</span></li>
        </ul>
      </div>

      <div className="rounded-xl border border-slate-200 dark:border-slate-700/60 p-4">
        <p className="text-[13px] font-bold text-slate-800 dark:text-slate-100 mb-2">Streak milestones</p>
        <div className="flex flex-wrap gap-2 mb-2">
          {(rules?.streakMilestones ?? []).map((s) => (
            <span key={s.days} className={`text-[11px] font-bold px-2.5 py-1 rounded-full border ${karma.streak >= s.days
              ? "bg-rose-50 dark:bg-rose-900/20 border-rose-200 dark:border-rose-800/40 text-rose-600"
              : "border-slate-200 dark:border-slate-700 text-slate-500"}`}>
              {s.days} days → +{s.points} KP
            </span>
          ))}
        </div>
        <p className="text-[12px] text-slate-600 dark:text-slate-400 leading-snug">
          A day counts when you check in or earn any Karma. Missing a full day resets your streak, and each
          milestone can be earned again on a new streak.
        </p>
      </div>
    </div>
  );
};


// ─── Passbook ──────────────────────────────────────────────────────────────────

const PassbookRow: React.FC<{ e: KarmaTransaction }> = ({ e }) => {
  const meta = metaFor(e.eventType);
  const blocked = e.pointsAwarded === 0;
  return (
    <div className={`flex items-center gap-3 py-2.5 border-b border-slate-100 dark:border-slate-700/40 last:border-0 ${blocked ? "opacity-70" : ""}`}>
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 border ${meta.colorClasses}`}>{meta.icon}</div>
      <div className="flex-1 min-w-0">
        <p className="text-[12px] font-semibold text-slate-700 dark:text-slate-200 truncate">
          {meta.label}{e.isCbp && <span className="ml-1 text-orange-500">★ CBP</span>}
        </p>
        <p className="text-[11px] text-slate-400 truncate">
          {fmtDate(e.createdAt)}{e.note ? ` · ${e.note}` : ""}
        </p>
      </div>
      <span className={`text-[14px] font-black flex-shrink-0 ${e.pointsAwarded > 0 ? "text-emerald-600 dark:text-emerald-400" : e.pointsAwarded < 0 ? "text-red-500" : "text-slate-400"}`}>
        {formatPoints(e.pointsAwarded)}
      </span>
    </div>
  );
};


// ─── FAQ ───────────────────────────────────────────────────────────────────────

const FAQ_ITEMS: [string, string][] = [
  ["Are my Karma Points saved permanently?",
   "Yes. Every award is written as an immutable entry in your passbook on the server, and your balance is the sum of those entries. It is the same on every device and survives logouts."],
  ["Why did an activity show 0 KP?",
   "It hit a limit: the daily cap, a per-activity daily limit or the monthly course limit. The passbook note says which. The activity is still recorded, but it cannot be re-done later for points."],
  ["Can I earn twice for the same quiz or course?",
   "No. Each quiz, diagnostic, course completion, course rating and CBP bonus earns once. Retaking a quiz updates your score but not your points."],
  ["When does the day reset?",
   "At midnight India Standard Time (IST). Monthly limits reset on the 1st of each month, IST."],
  ["How are points awarded for quizzes?",
   "Automatically. When you pass a quiz with 70% or more, or finish a diagnostic, the platform credits you. Points cannot be claimed manually, so nobody can game them."],
  ["Can points be removed?",
   "Only by an administrator, to correct a mistake, and always with a reason that appears in your passbook. A balance can never go below zero."],
];


// ─── Main view ─────────────────────────────────────────────────────────────────

const KarmaRewardsView: React.FC<Props> = ({ karma: initial, userId }) => {
  const [karma, setKarma] = useState<KarmaLedger | null>(initial);
  const [loadFailed, setLoadFailed] = useState(false);
  const [rules, setRules] = useState<KarmaRules | null>(null);
  const [rulesError, setRulesError] = useState(false);
  const [extra, setExtra] = useState<KarmaTransaction[]>([]);
  const [loadingMore, setLoadingMore] = useState(false);
  const [filter, setFilter] = useState<KarmaEventType | "ALL">("ALL");
  const [claiming, setClaiming] = useState<string | null>(null);
  const [claimMsg, setClaimMsg] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const fresh = await fetchKarmaLedger(userId, PAGE);   // idempotent daily check-in
    if (fresh) { setKarma(fresh); setExtra([]); setLoadFailed(false); }
    else setLoadFailed(true);
  }, [userId]);

  useEffect(() => { if (initial) setKarma((k) => k ?? initial); }, [initial]);
  useEffect(() => {
    refresh();
    fetchKarmaRules().then(setRules).catch(() => setRulesError(true));
  }, [refresh]);

  const entries = useMemo(() => [...(karma?.ledger ?? []), ...extra], [karma, extra]);
  const shown = filter === "ALL" ? entries : entries.filter((e) => e.eventType === filter);
  const hasMore = karma ? entries.length < karma.totalEvents : false;

  // CBP completions without a CBP bonus in the loaded history
  const claimable = useMemo(() => {
    const claimed = new Set(entries.filter((e) => e.eventType === "CBP_BONUS").map((e) => e.courseId));
    return entries.filter((e) => e.eventType === "COURSE_COMPLETION" && e.isCbp && e.courseId && !claimed.has(e.courseId));
  }, [entries]);

  const loadMore = async () => {
    if (!karma) return;
    setLoadingMore(true);
    try {
      const page = await fetchKarmaHistory(userId, PAGE, entries.length);
      setExtra((x) => [...x, ...page.ledger]);
    } finally {
      setLoadingMore(false);
    }
  };

  const claim = async (courseId: string) => {
    setClaiming(courseId);
    setClaimMsg(null);
    try {
      const r = await claimCbpBonus(userId, courseId);
      setClaimMsg(r.pointsAwarded > 0 ? `+${r.pointsAwarded} KP CBP bonus added.` : (r.reason ?? "Already claimed."));
      await refresh();
    } catch (err) {
      setClaimMsg(err instanceof Error ? err.message : "Claim failed. Please try again.");
    } finally {
      setClaiming(null);
    }
  };

  if (!karma) {
    return (
      <div className="gov-card p-8 flex items-center justify-center gap-2 text-slate-400">
        {loadFailed
          ? <><AlertCircle size={18} className="text-red-400" /><span className="text-sm">Karma service is unavailable right now. Please try again shortly.</span></>
          : <><Loader2 size={18} className="animate-spin" /><span className="text-sm">Loading your Karma…</span></>}
      </div>
    );
  }

  const { level, today, rank } = karma;
  const nextMilestone = rules?.streakMilestones.find((s) => s.days > karma.streak);
  const newAwards = karma.recentAwards.filter((a) => a.pointsAwarded > 0);

  return (
    <div className="flex flex-col gap-5">

      {/* 1. Check-in banner */}
      {newAwards.length > 0 && (
        <div className="rounded-xl border border-emerald-200 dark:border-emerald-800/50 bg-emerald-50 dark:bg-emerald-900/20 px-4 py-3 flex items-center gap-3">
          <Sparkles size={18} className="text-emerald-600 flex-shrink-0" />
          <p className="text-[13px] text-emerald-800 dark:text-emerald-300">
            <b>Welcome back!</b>{" "}
            {newAwards.map((a) => `${formatPoints(a.pointsAwarded)} ${a.eventType ? EVENT_META[a.eventType].label : "KP"}`).join(" · ")}
          </p>
        </div>
      )}

      {/* 2. Stat tiles */}
      <div className="grid gap-3 grid-cols-2 sm:gap-4 xl:grid-cols-4">
        <StatTile icon={<Trophy size={13} className="text-indigo-500" />} label="Balance">
          <div className="flex items-baseline gap-1.5">
            <span className="text-[36px] font-black leading-none bg-gradient-to-br from-indigo-600 to-purple-500 dark:from-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
              {karma.totalPoints}
            </span>
            <span className="text-[14px] font-bold text-slate-500">KP</span>
          </div>
          <p className="text-[12px] text-slate-500 dark:text-slate-400">Level {level.rank} · <b className="text-indigo-600 dark:text-indigo-400">{level.name}</b></p>
        </StatTile>

        <StatTile icon={<Target size={13} className="text-amber-500" />} label="Today">
          <p className="text-[22px] font-black text-slate-800 dark:text-white leading-none">
            {today.earned}<span className="text-[13px] font-bold text-slate-400"> / {today.cap} KP</span>
          </p>
          <Bar pct={(today.earned / today.cap) * 100} tone={today.remaining === 0 ? "red" : "indigo"} />
          <p className="text-[11px] text-slate-500 dark:text-slate-400">
            {today.remaining === 0 ? "Daily cap reached" : `${today.remaining} KP left`} · resets in {timeUntil(today.resetsAt)}
          </p>
        </StatTile>

        <StatTile icon={<Flame size={13} className="text-orange-500" />} label="Streak">
          <p className="text-[22px] font-black text-slate-800 dark:text-white leading-none">
            {karma.streak}<span className="text-[13px] font-bold text-slate-400"> {karma.streak === 1 ? "day" : "days"}</span>
          </p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400">Longest: {karma.longestStreak} days</p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 flex items-center gap-1">
            <CalendarCheck size={11} className={today.checkedIn ? "text-emerald-500" : "text-slate-400"} />
            {today.checkedIn ? "Checked in today" : "Not checked in yet"}
            {nextMilestone && ` · ${nextMilestone.days - karma.streak}d to +${nextMilestone.points}`}
          </p>
        </StatTile>

        <StatTile icon={<Medal size={13} className="text-fuchsia-500" />} label="Rank">
          <p className="text-[22px] font-black text-slate-800 dark:text-white leading-none">
            #{rank.position}<span className="text-[13px] font-bold text-slate-400"> of {rank.totalLearners}</span>
          </p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400">Top {rank.topPercent}% of learners</p>
        </StatTile>
      </div>

      {/* 3. Level ladder */}
      <div className="gov-card p-4 sm:p-6">
        <SectionTitle icon={<Crown size={16} />} title={`Level ${level.rank}: ${level.name}`}
          subtitle={level.nextName ? `${level.pointsToNext} KP to reach ${level.nextName}` : "Top level reached. Well done, Karmayogi!"} />
        <Bar pct={level.progressPct} />
        {rules && (
          <div className="mt-4 grid grid-cols-3 md:grid-cols-6 gap-2">
            {rules.levels.map((l, i) => {
              const reached = karma.totalPoints >= l.minPoints;
              return (
                <div key={l.name} className={`rounded-lg border px-2 py-2 text-center ${i + 1 === level.rank
                  ? "border-indigo-400 bg-indigo-50 dark:bg-indigo-900/30"
                  : reached ? "border-emerald-200 dark:border-emerald-800/50" : "border-slate-200 dark:border-slate-700 opacity-60"}`}>
                  <p className="text-[11px] font-bold text-slate-700 dark:text-slate-200">{l.name}</p>
                  <p className="text-[10px] text-slate-500">{l.minPoints}+ KP</p>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 4. How to earn */}
      <div className="gov-card p-4 sm:p-6">
        <SectionTitle icon={<Info size={16} />} title="How to earn Karma Points"
          subtitle="Karma Points reward real learning on iGOT Karmayogi and this platform. Points appear in your passbook as soon as you earn them." />
        <HowToEarn rules={rules} error={rulesError} breakdown={karma.breakdown} />
      </div>

      {/* 5. Rules & limits */}
      <div className="gov-card p-4 sm:p-6">
        <SectionTitle icon={<ShieldCheck size={16} />} title="Rules & limits"
          subtitle="These limits keep Karma fair and stop anyone from farming points." />
        <RulesAndLimits rules={rules} karma={karma} />
      </div>

      {/* CBP claim */}
      {claimable.length > 0 && (
        <div className="gov-card p-4 sm:p-6">
          <SectionTitle icon={<Gift size={16} />} title="Unclaimed CBP bonuses"
            subtitle="You completed these CBP-mandated courses. Claim +10 KP for each." />
          <div className="flex flex-col gap-2">
            {claimable.map((c) => (
              <div key={c.eventId} className="flex items-center justify-between gap-3 rounded-lg border border-orange-200 dark:border-orange-800/40 px-3 py-2">
                <span className="text-[12px] font-semibold text-slate-700 dark:text-slate-200 truncate">{c.note && !c.note.startsWith("Imported") ? c.note : c.courseId}</span>
                <button onClick={() => claim(c.courseId!)} disabled={claiming !== null}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-orange-50 dark:bg-orange-900/20 border border-orange-300 dark:border-orange-700 text-orange-700 dark:text-orange-400 text-[12px] font-bold hover:bg-orange-100 disabled:opacity-60">
                  {claiming === c.courseId ? <Loader2 size={12} className="animate-spin" /> : <Gift size={12} />} Claim +10
                </button>
              </div>
            ))}
          </div>
          {claimMsg && <p className="text-[12px] mt-2 text-slate-500 dark:text-slate-400">{claimMsg}</p>}
        </div>
      )}

      {/* 6. Passbook */}
      <div className="gov-card p-4 sm:p-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <SectionTitle icon={<BarChart2 size={16} />} title="Karma passbook"
            subtitle={`${karma.totalEvents} entries · every point you've earned, with the reason`} />
          <label className="flex items-center gap-2 text-[12px] text-slate-500">
            <ListFilter size={14} />
            <select value={filter} onChange={(e) => setFilter(e.target.value as KarmaEventType | "ALL")}
              className="rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-2 py-1 text-[12px] text-slate-700 dark:text-slate-200">
              <option value="ALL">All activity</option>
              {(Object.keys(EVENT_META) as KarmaEventType[]).map((t) => (
                <option key={t} value={t}>{EVENT_META[t].label}</option>
              ))}
            </select>
          </label>
        </div>
        {shown.length === 0 ? (
          <p className="text-[12px] text-slate-400 py-4 text-center">
            {entries.length === 0 ? "No Karma yet. Pass a quiz or complete a course to start earning!" : "No entries of this type in the loaded history."}
          </p>
        ) : (
          <div>{shown.map((e) => <PassbookRow key={e.eventId} e={e} />)}</div>
        )}
        {hasMore && (
          <button onClick={loadMore} disabled={loadingMore}
            className="mt-3 w-full flex items-center justify-center gap-2 py-2 rounded-lg border border-slate-200 dark:border-slate-700 text-[12px] font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-60">
            {loadingMore ? <Loader2 size={13} className="animate-spin" /> : <ChevronDown size={13} />} Load older entries
          </button>
        )}
      </div>

      {/* 7. FAQ */}
      <div className="gov-card p-4 sm:p-6">
        <SectionTitle icon={<Info size={16} />} title="Frequently asked questions" />
        <div className="flex flex-col divide-y divide-slate-100 dark:divide-slate-700/50">
          {FAQ_ITEMS.map(([q, a]) => (
            <details key={q} className="group py-2.5">
              <summary className="cursor-pointer list-none flex items-center justify-between text-[13px] font-semibold text-slate-700 dark:text-slate-200">
                {q}
                <ChevronDown size={14} className="text-slate-400 transition-transform group-open:rotate-180" />
              </summary>
              <p className="text-[12px] text-slate-600 dark:text-slate-400 mt-1.5 leading-relaxed">{a}</p>
            </details>
          ))}
        </div>
      </div>
    </div>
  );
};

export default KarmaRewardsView;
