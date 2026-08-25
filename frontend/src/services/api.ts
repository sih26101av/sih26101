/**
 * FILE: src/services/api.ts
 *
 * Adapter Layer: fetches raw JSON from FastAPI backend and maps it
 * into clean internal domain types. UI components never see raw API shapes.
 */

import type {
  Official,
  SkillGapEntry,
  CourseRecommendation,
  Enrollment,
  Achievement,
} from '../types/domain';

// ─── Raw shapes (exactly what the backend sends) ──────────────────────────────

interface RawSkillGap {
  competencyId: string;
  skillName: string;
  domain: string;
  currentLevel: number;
  targetLevel: number;
  gapScore: number;
}

interface RawSkillGapsResponse {
  officialId: string;
  jobRole: string;
  department: string;
  skillGaps: RawSkillGap[];
}

interface RawRecommendation {
  courseId: string;
  title: string;
  provider: string;
  durationHours: number;
  matchReason: string;
  tags: string[];
}

interface RawRecommendationsResponse {
  status: string;
  recommendations: RawRecommendation[];
}

interface RawEnrollment {
  enrollmentId: string;
  courseId: string;
  courseTitle: string;
  provider: string;
  durationHours: number;
  progressPercentage: number;
  remainingHours: number;
  lastAccessed: string;
  status: string;
}

interface RawEnrollmentsResponse {
  status: string;
  enrollments: RawEnrollment[];
}

interface RawAchievement {
  id: string;
  title: string;
  score: number;
  date: string;
  category: string;
}

interface RawAchievementsResponse {
  status: string;
  achievements: RawAchievement[];
}

// ─── Adapter functions ────────────────────────────────────────────────────────

function adaptSkillGapsResponse(raw: RawSkillGapsResponse): {
  profile: Official;
  skillGaps: SkillGapEntry[];
} {
  const profile: Official = {
    uuid: raw.officialId,
    email: `${raw.officialId.toLowerCase()}@mospi.gov.in`,
    role: 'OFFICIAL',
    govId: raw.officialId,
    fullName: raw.officialId,
    department: raw.department,
    experienceYears: 0,
    jobRole: {
      roleId: 'JR-001',
      title: raw.jobRole,
      department: raw.department,
      roleRequirements: [],
    },
    competencyProfile: {
      profileId: `CP-${raw.officialId}`,
      lastEvaluatedDate: new Date().toISOString(),
      userCompetencies: raw.skillGaps.map(gap => ({
        currentLevel: gap.currentLevel,
        verificationSource: 'FRAC Assessment',
        evaluatedAt: new Date().toISOString(),
        competency: {
          compId: gap.competencyId,
          domain: gap.domain as any,
          skillName: gap.skillName,
        },
      })),
    },
  };

  const skillGaps: SkillGapEntry[] = raw.skillGaps.map(gap => ({
    competency: {
      compId: gap.competencyId,
      domain: gap.domain as any,
      skillName: gap.skillName,
    },
    currentLevel: gap.currentLevel,
    requiredLevel: gap.targetLevel,
    gap: gap.gapScore,
    isMandatory: gap.gapScore > 0,
    verificationSource: 'FRAC Assessment',
    evaluatedAt: new Date().toISOString(),
  }));

  return { profile, skillGaps };
}

function adaptRecommendationsResponse(
  raw: RawRecommendationsResponse,
  skillGaps: SkillGapEntry[]
): CourseRecommendation[] {
  return raw.recommendations.map((rec, index) => {
    const matchedGap = skillGaps.find(g =>
      rec.tags?.some(
        tag =>
          g.competency.domain.toLowerCase().includes(tag.toLowerCase()) ||
          g.competency.skillName.toLowerCase().includes(tag.toLowerCase())
      )
    ) ?? skillGaps[0];

    const bridgesGapFor = matchedGap?.competency ?? {
      compId: 'UNKNOWN',
      domain: 'Statistical' as any,
      skillName: 'General Competency',
    };

    return {
      course: {
        courseId: rec.courseId,
        title: rec.title,
        source: rec.provider,
        durationHours: rec.durationHours,
      },
      matchScore: Math.max(0.6, 1 - index * 0.08),
      bridgesGapFor,
      aiMatchTag: rec.matchReason,
      priorityRank: index + 1,
    };
  });
}

function adaptEnrollmentsResponse(raw: RawEnrollmentsResponse): Enrollment[] {
  return raw.enrollments.map(e => ({
    enrollmentId: e.enrollmentId,
    course: {
      courseId: e.courseId,
      title: e.courseTitle,
      source: e.provider,
      durationHours: e.durationHours,
    },
    progressPercentage: e.progressPercentage,
    remainingHours: e.remainingHours,
    lastAccessed: e.lastAccessed,
    status: e.status,
  }));
}

function adaptAchievementsResponse(raw: RawAchievementsResponse): Achievement[] {
  return raw.achievements.map(a => ({
    id: a.id,
    title: a.title,
    score: a.score,
    date: a.date,
    category: a.category as 'RAG Quiz' | 'External Certification',
  }));
}

// ─── Public API functions ─────────────────────────────────────────────────────

async function apiFetch<T>(url: string, label: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`[${label}] API returned ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export async function fetchSkillGapsAndProfile(officialId: string): Promise<{
  profile: Official;
  skillGaps: SkillGapEntry[];
}> {
  const raw = await apiFetch<RawSkillGapsResponse>(
    `/api/v1/users/${officialId}/skill-gaps`,
    'skill-gaps'
  );
  return adaptSkillGapsResponse(raw);
}

export async function fetchRecommendations(
  officialId: string,
  skillGaps: SkillGapEntry[]
): Promise<CourseRecommendation[]> {
  const raw = await apiFetch<RawRecommendationsResponse>(
    `/api/v1/recommendations/${officialId}`,
    'recommendations'
  );
  return adaptRecommendationsResponse(raw, skillGaps);
}

export async function fetchEnrollments(officialId: string): Promise<Enrollment[]> {
  const raw = await apiFetch<RawEnrollmentsResponse>(
    `/api/v1/users/${officialId}/enrollments`,
    'enrollments'
  );
  return adaptEnrollmentsResponse(raw);
}

export async function fetchAchievements(officialId: string): Promise<Achievement[]> {
  const raw = await apiFetch<RawAchievementsResponse>(
    `/api/v1/users/${officialId}/achievements`,
    'achievements'
  );
  return adaptAchievementsResponse(raw);
}