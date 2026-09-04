import { useState, useEffect } from 'react';
import { fetchCompetencies, FracCompetency } from '../services/api';

// Re-export as SkillRow so AdminDashboard.tsx doesn't need changes
export type SkillRow = FracCompetency;

export function useSkillsData() {
  const [skills, setSkills] = useState<SkillRow[]>([]);
  const [isLoading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);

  const refetch = () => setTick(t => t + 1);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const competencies = await fetchCompetencies();
        if (!cancelled) setSkills(competencies);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to fetch skills data');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    load();
    return () => { cancelled = true; };
  }, [tick]);

  return { skills, isLoading, error, refetch };
}
