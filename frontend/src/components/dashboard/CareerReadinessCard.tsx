/**
 * FILE: src/components/dashboard/CareerReadinessCard.tsx
 *
 * Career readiness against the NEXT role's FRAC requirements
 * (GET /api/v1/learner/{id}/career-readiness): readiness %, the largest gaps
 * for that role, and the office's tier ladder (current → next → after).
 * Readiness = mean over the next role's competencies of min(level, required)/required;
 * unassessed competencies count as 0 and are flagged for a level check.
 */

import React, { useEffect, useState } from "react";
import { CheckCircle2, ChevronRight, TrendingUp, Loader2, HelpCircle } from "lucide-react";
import { RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis } from "recharts";
import { fetchCareerReadiness } from "../../services/api";
import type { CareerReadiness } from "../../types/domain";

interface Props {
  userId: string;
  /** Changes whenever levels change, so readiness refetches after new evidence */
  refreshKey?: string;
}

const TIER_LABEL: Record<string, string> = {
  TIER1_APEX: "Apex", TIER2_SENIOR: "Senior", TIER3_MID: "Middle", TIER4_JUNIOR: "Junior",
};

const CareerReadinessCard: React.FC<Props> = ({ userId, refreshKey }) => {
  const [data, setData] = useState<CareerReadiness | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!userId) return;
    let live = true;
    setError(null);
    fetchCareerReadiness(userId)
      .then(d => { if (live) setData(d); })
      .catch(e => { if (live) setError(e instanceof Error ? e.message : "Unavailable"); });
    return () => { live = false; };
  }, [userId, refreshKey]);

  const target = data?.nextRole;
  const pct = target ? target.readinessPct : data?.currentRole.readinessPct ?? 0;
  const topGaps = (target?.competencies ?? []).filter(c => (c.gap ?? 1) > 0).slice(0, 4);

  return (
    <div className="gov-card gov-card-hover p-6">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-indigo-50 dark:bg-indigo-900/30 flex items-center justify-center">
            <TrendingUp size={15} className="text-indigo-600 dark:text-indigo-400" />
          </div>
          <h3 className="text-slate-900 dark:text-white font-extrabold text-[14px] tracking-tight">Career Readiness</h3>
        </div>
        <span className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800/40 px-2 py-0.5 rounded-full">
          FRAC
        </span>
      </div>

      {!data && !error && (
        <div className="flex items-center justify-center h-[140px] text-slate-400"><Loader2 size={18} className="animate-spin" /></div>
      )}
      {error && <p className="text-[11.5px] text-slate-500 dark:text-slate-400 py-6 text-center">Career readiness is unavailable ({error}).</p>}

      {data && (
        <>
          <div className="relative h-[130px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart cx="50%" cy="50%" innerRadius="72%" outerRadius="100%" startAngle={220} endAngle={-40}
                data={[{ name: "Readiness", value: pct, fill: "url(#careerGrad)" }]} barSize={13}>
                <defs>
                  <linearGradient id="careerGrad" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#6366f1" />
                    <stop offset="100%" stopColor="#a855f7" />
                  </linearGradient>
                </defs>
                <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
                <RadialBar background={{ fill: "#f1f5f9" }} dataKey="value" cornerRadius={8} angleAxisId={0} />
              </RadialBarChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-[26px] font-black leading-none text-indigo-600 dark:text-indigo-400">{pct}%</span>
              <span className="text-[9.5px] text-slate-500 dark:text-slate-400 font-semibold mt-0.5 uppercase tracking-wide">
                {target ? "ready for next role" : "of current role"}
              </span>
            </div>
          </div>

          <p className="text-[11px] text-center text-slate-500 dark:text-slate-400 mb-3">
            {target ? (
              <>Next role: <span className="font-semibold text-indigo-600 dark:text-indigo-400">{target.designation}</span>
                {" "}· {target.metCount}/{target.competencies.length} competencies met</>
            ) : "You are at the top of your office's ladder."}
          </p>

          {topGaps.length > 0 && (
            <ul className="mb-3 space-y-1">
              {topGaps.map(c => (
                <li key={c.competencyId} className="flex items-center justify-between gap-2 text-[11px]">
                  <span className="truncate text-slate-700 dark:text-slate-300" title={c.competencyName}>
                    {c.competencyName}
                    {!c.inCurrentRole && <span className="ml-1 text-[9px] font-bold text-indigo-500">NEW</span>}
                  </span>
                  {c.currentLevel == null ? (
                    <span className="flex items-center gap-0.5 text-violet-600 dark:text-violet-400 shrink-0">
                      <HelpCircle size={10} /> unassessed → L{c.requiredLevel}
                    </span>
                  ) : (
                    <span className="shrink-0 font-mono text-slate-500 dark:text-slate-400">
                      L{c.currentLevel} → L{c.requiredLevel}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          )}

          <div className="border-t border-slate-100 dark:border-slate-700/50 mb-3" />
          <div className="flex items-center gap-2 mb-2">
            <ChevronRight size={13} className="text-slate-400" />
            <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest">Career Pathway</span>
          </div>
          <div className="flex flex-col">
            {data.milestones.map((m, i) => {
              const current = m.status === "current", next = m.status === "next";
              return (
                <div key={m.roleId ?? i} className="flex items-stretch gap-3">
                  <div className="flex flex-col items-center">
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center mt-0.5 border-2 ${
                      current ? "bg-emerald-500 border-emerald-500" : next ? "bg-indigo-600 border-indigo-600"
                        : "bg-white dark:bg-slate-800 border-slate-300 dark:border-slate-600"}`}>
                      {current ? <CheckCircle2 size={11} className="text-white" strokeWidth={3} />
                        : <div className={`w-2 h-2 rounded-full ${next ? "bg-white" : "bg-slate-300 dark:bg-slate-600"}`} />}
                    </div>
                    {i < data.milestones.length - 1 && <div className="w-0.5 flex-1 my-1 bg-slate-200 dark:bg-slate-700" />}
                  </div>
                  <div className={`pb-3 ${m.status === "future" ? "opacity-50" : ""}`}>
                    <p className={`text-[12.5px] font-bold leading-tight ${next ? "text-indigo-700 dark:text-indigo-400" : "text-slate-800 dark:text-slate-200"}`}>
                      {m.designation}
                    </p>
                    <p className="text-[10.5px] text-slate-400 dark:text-slate-500 mt-0.5">
                      {TIER_LABEL[m.tier] ?? m.tier} tier
                      {current && <span className="ml-2 text-emerald-500">✓ Current · {data.currentRole.readinessPct}% of role met</span>}
                      {next && target && <span className="ml-2 text-indigo-500">← Next · {target.readinessPct}% ready</span>}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
          <p className="text-[9.5px] text-slate-400 dark:text-slate-500 mt-1" title={data.method}>
            Levels come from the same evidence as your skill-gap analysis.
          </p>
        </>
      )}
    </div>
  );
};

export default CareerReadinessCard;
