/**
 * FILE: src/hooks/useAdminData.ts
 *
 * Fetches live admin roster from /api/admin/v1/users, then computes
 * KPIs and the heatmap entirely from real data. Zero mock/static data.
 */

import { useState, useEffect } from 'react';
import { fetchAllUsers } from '../services/api';

// ─── Shapes the hook exposes ───────────────────────────────────────────────────
export interface AdminRosterRow {
  userId:           string;
  govId:            string;
  firstName:        string;
  lastName:         string;
  email:            string;
  designation:      string;
  department:       string;
  enrollmentStatus: number;   // 0=none, 1=in-progress, 2=completed
  missingSkill:     string | null;
}

export interface AdminKPIs {
  totalOfficials:       number;
  avgMissingSkills:     number;  // avg competencies in PLANNED/IN_PROGRESS per user
  trainingCompliancePct: number; // % with at least one completed course
}

export interface HeatmapEntry {
  competency: string;
  gap:        number;
  color:      [string, string];
}

export interface UseAdminDataResult {
  roster:    AdminRosterRow[];
  kpis:      AdminKPIs;
  heatmap:   HeatmapEntry[];
  isLoading: boolean;
  error:     string | null;
  refetch:   () => void;
}

const GAP_COLORS: [string, string][] = [
  ['#1e3a8a', '#172554'],
  ['#0f766e', '#115e59'],
  ['#2dd4bf', '#0d9488'],
  ['#eab308', '#a16207'],
  ['#f97316', '#c2410c'],
  ['#7c3aed', '#4c1d95'],
];

function levelToNumber(levelStr: string): number {
  const m = (levelStr ?? '').match(/\d+/);
  return m ? parseInt(m[0], 10) : 2;
}

// ─── Hook ──────────────────────────────────────────────────────────────────────
export function useAdminData(): UseAdminDataResult {
  const [roster,    setRoster]    = useState<AdminRosterRow[]>([]);
  const [kpis,      setKpis]      = useState<AdminKPIs>({ totalOfficials: 0, avgMissingSkills: 0, trainingCompliancePct: 0 });
  const [heatmap,   setHeatmap]   = useState<HeatmapEntry[]>([]);
  const [isLoading, setLoading]   = useState(true);
  const [error,     setError]     = useState<string | null>(null);
  const [tick,      setTick]      = useState(0);

  const refetch = () => setTick(t => t + 1);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        // fetchAllUsers() hits /api/admin/v1/users — returns pre-enriched rows
        const raw: any[] = await fetchAllUsers() as any;

        if (cancelled) return;

        // ── Build roster rows ─────────────────────────────────────────────
        const rows: AdminRosterRow[] = raw.map((u: any) => ({
          userId:           u.userId,
          govId:            u.govId ?? u.userId,
          firstName:        u.firstName ?? '',
          lastName:         u.lastName ?? '',
          email:            u.email ?? '',
          designation:      u.designation ?? 'Official',
          department:       u.department ?? 'MoSPI',
          enrollmentStatus: u.enrollmentStatus ?? 0,
          missingSkill:     u.missingSkill ?? null,
        }));

        // ── Compute KPIs from live data ───────────────────────────────────
        const total = rows.length;
        const compliant = rows.filter(r => r.enrollmentStatus === 2).length;
        const compliancePct = total > 0 ? Math.round((compliant / total) * 100) : 0;

        // Avg missing competencies: count PLANNED/IN_PROGRESS per user, average
        const totalMissing = raw.reduce((acc: number, u: any) => {
          const comps: any[] = u.competencies ?? [];
          return acc + comps.filter((c: any) => c.status === 'PLANNED' || c.status === 'IN_PROGRESS').length;
        }, 0);
        const avgMissing = total > 0 ? parseFloat((totalMissing / total).toFixed(1)) : 0;

        // ── Build heatmap from competency deficiency frequency ────────────
        const freqMap: Record<string, number> = {};
        raw.forEach((u: any) => {
          const comps: any[] = u.competencies ?? [];
          comps.forEach((c: any) => {
            if (c.status === 'PLANNED' || c.status === 'IN_PROGRESS') {
              const penalty = c.status === 'PLANNED' ? 1.5 : 1;
              const level = levelToNumber(c.competencyLevel ?? 'Level 2');
              freqMap[c.name] = (freqMap[c.name] ?? 0) + penalty * (4 - level);
            }
          });
        });

        const heatmapEntries: HeatmapEntry[] = Object.entries(freqMap)
          .sort(([, a], [, b]) => b - a)
          .slice(0, 5)
          .map(([comp, score], i) => ({
            competency: comp.length > 20 ? comp.slice(0, 20) + '…' : comp,
            gap:        parseFloat(score.toFixed(1)),
            color:      GAP_COLORS[i % GAP_COLORS.length],
          }));

        setRoster(rows);
        setKpis({ totalOfficials: total, avgMissingSkills: avgMissing, trainingCompliancePct: compliancePct });
        setHeatmap(heatmapEntries);
      } catch (err) {
        if (!cancelled) {
          const msg = err instanceof Error ? err.message : 'Failed to load admin data';
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
