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
} from '../services/api';
import type {
  UseLearnerDashboardResult,
  Official,
  SkillGapEntry,
  CourseRecommendation,
  Enrollment,
  Achievement,
} from '../types/domain';

export function useLearnerDashboard(officialId: string): UseLearnerDashboardResult {
  const [profile, setProfile]                 = useState<Official | null>(null);
  const [skillGaps, setSkillGaps]             = useState<SkillGapEntry[]>([]);
  const [recommendations, setRecommendations] = useState<CourseRecommendation[]>([]);
  const [enrollments, setEnrollments]         = useState<Enrollment[]>([]);
  const [achievements, setAchievements]       = useState<Achievement[]>([]);
  const [isLoading, setIsLoading]             = useState(true);
  const [error, setError]                     = useState<string | null>(null);

  useEffect(() => {
    if (!officialId) return;
    let cancelled = false;

    const load = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Step 1: skill gaps + profile (sequential — recs depend on gaps)
        const { profile: p, skillGaps: g } = await fetchSkillGapsAndProfile(officialId);

        // Step 2: remaining 3 endpoints fire concurrently
        const [recs, enrs, achs] = await Promise.all([
          fetchRecommendations(officialId, g),
          fetchEnrollments(officialId),
          fetchAchievements(officialId),
        ]);

        if (!cancelled) {
          setProfile(p);
          setSkillGaps(g);
          setRecommendations(recs);
          setEnrollments(enrs);
          setAchievements(achs);
        }
      } catch (err) {
        if (!cancelled) {
          const msg = err instanceof Error ? err.message : 'Unknown error';
          console.error('[useLearnerDashboard]', msg);
          setError(msg);
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    load();
    return () => { cancelled = true; };
  }, [officialId]);

  return { profile, skillGaps, recommendations, enrollments, achievements, isLoading, error };
}