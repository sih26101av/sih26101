import { useState, useEffect } from 'react';

export interface SkillRow {
  competency_id: string;
  name: string;
  category: string;
  description: string;
}

export function useSkillsData() {
  const [skills, setSkills] = useState<SkillRow[]>([]);
  const [isLoading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSkills = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('http://localhost:8001/api/frac/competencies');
      if (!res.ok) throw new Error('Failed to fetch skills');
      const body = await res.json();
      setSkills(body.result?.competencies || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch skills data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSkills();
  }, []);

  return { skills, isLoading, error, refetch: fetchSkills };
}
