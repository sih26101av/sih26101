/**
 * FILE: src/hooks/useLearnerDashboard.ts
 *
 * Fetches ALL dashboard data from live FastAPI endpoints.
 * Zero mock data. Zero fallbacks. Pure API.
 */

import { useState, useEffect } from 'react';
import {
  fetchSkillGapsAndProfile,
  fetchRecommendations,
  fetchEnrollments,
  fetchAchievements,
  fetchKarmaLedger,
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

export function useLearnerDashboard(officialId: string): UseLearnerDashboardResult {
  const [profile, setProfile]                 = useState<Official | null>(null);
  const [skillGaps, setSkillGaps]             = useState<SkillGapEntry[]>([]);
  const [recommendations, setRecommendations] = useState<CourseRecommendation[]>([]);
  const [enrollments, setEnrollments]         = useState<Enrollment[]>([]);
  const [achievements, setAchievements]       = useState<Achievement[]>([]);
  const [karma, setKarma]                     = useState<KarmaLedger | null>(null);
  const [isLoading, setIsLoading]             = useState(true);
  const [error, setError]                     = useState<string | null>(null);

  const load = async () => {
    if (!officialId) return;
    setIsLoading(true);
    setError(null);
    try {
      // Step 1: skill gaps + profile (sequential — recs depend on gaps)
      const { profile: p, skillGaps: g } = await fetchSkillGapsAndProfile(officialId);

      // Step 2: remaining 4 endpoints fire concurrently (karma is non-blocking)
      const [recs, enrs, achs, karmaData] = await Promise.all([
        fetchRecommendations(officialId, g),
        fetchEnrollments(officialId),
        fetchAchievements(officialId),
        fetchKarmaLedger(officialId),  // null on error, never throws
      ]);

      setProfile(p);
      setSkillGaps(g);
      setRecommendations(recs);
      setEnrollments(enrs);
      setAchievements(achs);
      setKarma(karmaData);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Unknown error';
      console.error('[useLearnerDashboard]', msg);
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [officialId]);

  return { profile, skillGaps, recommendations, enrollments, achievements, karma, isLoading, error, refetch: load };
}
