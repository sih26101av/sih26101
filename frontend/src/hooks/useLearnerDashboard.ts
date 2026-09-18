/**
 * FILE: src/hooks/useLearnerDashboard.ts
 *
 * Fetches ALL dashboard data from live FastAPI endpoints.
 * Zero mock data. Zero fallbacks. Pure API.
 *
 * Speed:
 *  - Every endpoint fires at once (recommendations no longer wait for skill gaps).
 *  - Karma is the slowest, least important call; it fills in when it arrives
 *    instead of holding back the whole dashboard.
 *  - Stale-while-revalidate: the last result per officialId is kept in memory,
 *    so re-opening the dashboard (e.g. back from the Assessment Studio) renders
 *    instantly and refreshes silently. The cache is wiped when the session ends.
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import {
  fetchSkillGapsAndProfile,
  fetchRecommendations,
  fetchEnrollments,
  fetchAchievements,
  fetchKarmaLedger,
  onSessionEnd,
} from '../services/api';
import type {
  UseLearnerDashboardResult,
  Official,
  SkillGapEntry,
  CourseRecommendation,
  Enrollment,
  Achievement,
  KarmaLedger,
} from '../types/domain';

interface DashboardData {
  profile: Official;
  skillGaps: SkillGapEntry[];
  recommendations: CourseRecommendation[];
  enrollments: Enrollment[];
  achievements: Achievement[];
  karma: KarmaLedger | null;
}

const _cache = new Map<string, DashboardData>();
// Stable empties so consumers' effects don't re-run on every render before data lands.
const NO_GAPS: SkillGapEntry[] = [];
const NO_RECS: CourseRecommendation[] = [];
const NO_ENROLLMENTS: Enrollment[] = [];
const NO_ACHIEVEMENTS: Achievement[] = [];
onSessionEnd(() => _cache.clear());

export function useLearnerDashboard(officialId: string): UseLearnerDashboardResult {
  const cached = officialId ? _cache.get(officialId) : undefined;
  const [data, setData]           = useState<DashboardData | null>(cached ?? null);
  const [isLoading, setIsLoading] = useState(!cached);
  const [error, setError]         = useState<string | null>(null);
  // Only the newest request may write state (officialId change / quick refetch).
  const requestSeq = useRef(0);

  const load = useCallback(async () => {
    if (!officialId) return;
    const seq = ++requestSeq.current;
    const hasData = _cache.has(officialId);
    if (!hasData) setIsLoading(true);
    setError(null);

    // Karma never throws (null on error) and must not block first paint.
    const karmaPromise = fetchKarmaLedger(officialId);

    try {
      const [{ profile, skillGaps }, recommendations, enrollments, achievements] = await Promise.all([
        fetchSkillGapsAndProfile(officialId),
        fetchRecommendations(officialId, []),
        fetchEnrollments(officialId),
        fetchAchievements(officialId),
      ]);
      if (seq !== requestSeq.current) return;

      const next: DashboardData = {
        profile, skillGaps, recommendations, enrollments, achievements,
        karma: _cache.get(officialId)?.karma ?? null,   // keep the old card until the new one lands
      };
      _cache.set(officialId, next);
      setData(next);
    } catch (err) {
      if (seq !== requestSeq.current) return;
      const msg = err instanceof Error ? err.message : 'Unknown error';
      console.error('[useLearnerDashboard]', msg);
      // With cached data on screen, a failed background refresh stays quiet.
      if (!hasData) setError(msg);
    } finally {
      if (seq === requestSeq.current) setIsLoading(false);
    }

    const karma = await karmaPromise;
    if (seq !== requestSeq.current) return;
    const current = _cache.get(officialId);
    if (current) {
      const next = { ...current, karma };
      _cache.set(officialId, next);
      setData(next);
    }
  }, [officialId]);

  useEffect(() => {
    // New officialId: show its cached data (if any) straight away, then revalidate.
    const hit = officialId ? _cache.get(officialId) : undefined;
    setData(hit ?? null);
    setIsLoading(!hit);
    load();
  }, [officialId, load]);

  return {
    profile:         data?.profile ?? null,
    skillGaps:       data?.skillGaps ?? NO_GAPS,
    recommendations: data?.recommendations ?? NO_RECS,
    enrollments:     data?.enrollments ?? NO_ENROLLMENTS,
    achievements:    data?.achievements ?? NO_ACHIEVEMENTS,
    karma:           data?.karma ?? null,
    isLoading,
    error,
    refetch:         load,
  };
}
