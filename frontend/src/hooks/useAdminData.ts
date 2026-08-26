/**
 * FILE: src/hooks/useAdminData.ts
 *
 * Custom hook: fetches the live admin roster from the mock iGOT server
 * and derives all KPI metrics computationally from the raw user data.
 *
 * SOLID: Single Responsibility — this hook ONLY owns data fetching + computation.
 * AdminDashboard.tsx owns only rendering.
 */

import { useState, useEffect } from 'react';
import { fetchAdminRoster } from '../services/api';
import type { RawAdminUser } from '../services/api';

// ─── Derived KPIs (computed from fetched data) ─────────────────────────────────
export interface AdminKPIs {
  totalOfficials: number;
  avgSkillGapScore: number;
  trainingCompliancePct: number;
}

// ─── Heatmap entry for the Recharts BarChart ───────────────────────────────────
export interface HeatmapEntry {
  competency: string;
  gap: number;
  color: [string, string];
}

const GAP_COLORS: [string, string][] = [
  ['#1e3a8a', '#172554'],
  ['#0f766e', '#115e59'],
  ['#2dd4bf', '#0d9488'],
  ['#eab308', '#84cc16'],
  ['#f97316', '#ea580c'],
  ['#7c3aed', '#4c1d95'],
];

// ─── Hook ──────────────────────────────────────────────────────────────────────
export interface UseAdminDataResult {
  roster:      RawAdminUser[];
  kpis:        AdminKPIs;
  heatmap:     HeatmapEntry[];
  isLoading:   boolean;
  error:       string | null;
  refetch:     () => void;
}

export function useAdminData(): UseAdminDataResult {
  const [roster, setRoster]     = useState<RawAdminUser[]>([]);
  const [kpis, setKpis]         = useState<AdminKPIs>({ totalOfficials: 0, avgSkillGapScore: 0, trainingCompliancePct: 0 });
  const [heatmap, setHeatmap]   = useState<HeatmapEntry[]>([]);
  const [isLoading, setLoading] = useState(true);
  const [error, setError]       = useState<string | null>(null);
  const [tick, setTick]         = useState(0);

  const refetch = () => setTick(t => t + 1);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const users = await fetchAdminRoster();
        if (cancelled) return;

        // ── Compute KPIs ───────────────────────────────────────────────────
        const total = users.length;

        // Compliance: officials with enrollmentStatus === 2 (completed)
        const compliant = users.filter(u => u.enrollmentStatus === 2).length;
        const compliancePct = total > 0 ? Math.round((compliant / total) * 100) : 0;

        // Avg skill gap: count missing skills per user, average across all
        const avgGap =
          total > 0
            ? parseFloat(
                (
                  users.reduce((acc, u) => {
                    const missing = u.missingSkill ? 1 : 0;
                    return acc + missing;
                  }, 0) / total
                ).toFixed(1)
              )
            : 0;

        // ── Compute Heatmap ────────────────────────────────────────────────
        // Count frequency of each missing/deficient competency across all users
        const freqMap: Record<string, number> = {};
        users.forEach(u => {
          if (u.missingSkill) {
            freqMap[u.missingSkill] = (freqMap[u.missingSkill] ?? 0) + 1;
          }
          // Parse competencies_v3 for deeper signal
          if (u.competencies_v3) {
            try {
              const parsed: { name?: string; status?: string }[] = JSON.parse(u.competencies_v3);
              parsed
                .filter(c => c.status === 'deficit' || c.status === 'in-progress')
                .forEach(c => {
                  const name = c.name ?? 'Unknown';
                  freqMap[name] = (freqMap[name] ?? 0) + 0.5;
                });
            } catch { /* silently skip bad JSON */ }
          }
        });

        // Take top 5 competencies with the highest deficiency frequency
        const heatmapData: HeatmapEntry[] = Object.entries(freqMap)
          .sort(([, a], [, b]) => b - a)
          .slice(0, 5)
          .map(([comp, count], i) => ({
            competency: comp,
            gap: parseFloat(count.toFixed(1)),
            color: GAP_COLORS[i % GAP_COLORS.length],
          }));

        setRoster(users);
        setKpis({ totalOfficials: total, avgSkillGapScore: avgGap, trainingCompliancePct: compliancePct });
        setHeatmap(heatmapData);
      } catch (err) {
        if (!cancelled) {
          const msg = err instanceof Error ? err.message : 'Unknown error loading admin data';
          console.error('[useAdminData]', msg);
          setError(msg);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    load();
    return () => { cancelled = true; };
  }, [tick]);

  return { roster, kpis, heatmap, isLoading, error, refetch };
}
