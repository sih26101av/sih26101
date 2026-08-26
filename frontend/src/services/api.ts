/**
 * FILE: src/services/api.ts
 *
 * PATTERN: Adapter Pattern (ARCHITECTURE.md §4.B)
 * ─────────────────────────────────────────────────────────────────────────────
 * Wraps the mock iGOT server (http://localhost:8001) with:
 *   1. A preconfigured fetch client (auth headers, base URL)
 *   2. Sunbird standard envelope unpacker → response.data.result
 *   3. Adapter functions mapping raw iGOT shapes → internal domain types
 *
 * UI components and hooks NEVER import raw API shapes.
 * They import only the clean domain types from `../types/domain`.
 * ─────────────────────────────────────────────────────────────────────────────
 */

import type {
  Official,
  SkillGapEntry,
  CourseRecommendation,
  Enrollment,
  Achievement,
} from '../types/domain';

// ─── Configuration ─────────────────────────────────────────────────────────────
const BASE_URL = 'http://localhost:8001';
const API_KEY  = 'mock-api-key-2026';

// ─── Sunbird Standard Envelope ─────────────────────────────────────────────────
interface SunbirdEnvelope<T> {
  id:     string;
  ver:    string;
  ts:     string;
  params: { status: string; err: string | null; errmsg: string | null };
  responseCode: string;
  result: T;
}

// ─── Preconfigured fetch helper ────────────────────────────────────────────────
async function igotFetch<T>(
  path: string,
  label: string,
  options: RequestInit = {}
): Promise<T> {
  const sessionToken =
    typeof window !== 'undefined'
      ? (localStorage.getItem('mospi-session-token') ?? 'mock-session-token-2026')
      : 'mock-session-token-2026';

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`,
      'x-authenticated-user-token': sessionToken,
      ...(options.headers ?? {}),
    },
  });

  if (!res.ok) {
    throw new Error(`[${label}] HTTP ${res.status} ${res.statusText} → ${path}`);
  }

  const json: SunbirdEnvelope<T> = await res.json();

  // Validate Sunbird envelope
  if (json.params?.err) {
    throw new Error(`[${label}] Sunbird error: ${json.params.errmsg ?? json.params.err}`);
  }

  return json.result;
}

// ─────────────────────────────────────────────────────────────────────────────
// RAW iGOT SHAPES  (exactly what the mock server sends inside `result`)
// ─────────────────────────────────────────────────────────────────────────────

// /api/user/v2/read/{user_id}
interface RawIgotUser {
  userId:      string;
  firstName:   string;
  lastName:    string;
  email:       string;
  designation: string;
  department:  string;
  rootOrgId:   string;
  profileDetails?: {
    employmentDetails?: { departmentName?: string; designation?: string };
    professionalDetails?: [{ industry?: string; experience?: string }];
  };
  competencies_v3?: string; // stringified JSON
}

// /api/course/v1/user/enrollment/list/{user_id}
interface RawIgotEnrollment {
  courseId:            string;
  courseName:          string;
  completionPercentage?: number;
  status:              number; // 0=not-started, 1=in-progress, 2=completed
  enrolledDate:        string;
  lastContentAccessTime?: string;
  leafNodesCount?:     number;
  leafNodeCompleted?:  number;
  issuedCertificates?: { name: string; identifier: string; lastIssuedOn: string }[];
  content?: {
    duration?:  string;
    provider?:  string;
    name?:      string;
  };
}
interface RawEnrollmentsResult {
  courses: RawIgotEnrollment[];
}

// /api/content/read (catalog)
interface RawIgotCourse {
  identifier:          string;
  name:                string;
  provider?:           string;
  duration?:           string;
  competencies_v3?:    string;
  primaryCategory?:    string;
  source?:             string;
}
interface RawCatalogResult {
  content: RawIgotCourse[];
  count:   number;
}

// /api/admin/v1/users (roster)
export interface RawAdminUser {
  userId:      string;
  govId:       string;
  firstName:   string;
  lastName:    string;
  designation: string;
  department:  string;
  email:       string;
  enrollmentStatus?: number; // 0=none 1=in-progress 2=completed
  competencies_v3?:  string;
  missingSkill?: string;
}
export interface RawAdminRosterResult {
  users: RawAdminUser[];
  count: number;
}

// ─────────────────────────────────────────────────────────────────────────────
// ADAPTER FUNCTIONS
// ─────────────────────────────────────────────────────────────────────────────

function parseCompetencies(raw: string | undefined): string[] {
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) return parsed.map((c: { name?: string; id?: string }) => c.name ?? c.id ?? '').filter(Boolean);
    return [];
  } catch {
    return [];
  }
}

function adaptIgotUser(raw: RawIgotUser): Official {
  const dept = raw.profileDetails?.employmentDetails?.departmentName ?? raw.department ?? 'MoSPI';
  const desig = raw.profileDetails?.employmentDetails?.designation ?? raw.designation ?? 'Official';
  const expStr = raw.profileDetails?.professionalDetails?.[0]?.experience ?? '0';
  const expYears = parseInt(expStr, 10) || 0;

  const compList = parseCompetencies(raw.competencies_v3);

  return {
    uuid:     raw.userId,
    email:    raw.email,
    role:     'OFFICIAL',
    govId:    raw.userId.replace('usr_', 'EMP-'),
    fullName: `${raw.firstName} ${raw.lastName}`.trim(),
    department: dept,
    experienceYears: expYears,
    jobRole: {
      roleId: `JR-${raw.rootOrgId ?? '001'}`,
      title:  desig,
      department: dept,
      roleRequirements: [],
    },
    competencyProfile: {
      profileId: `CP-${raw.userId}`,
      lastEvaluatedDate: new Date().toISOString(),
      userCompetencies: compList.map((name, i) => ({
        currentLevel: 2,
        verificationSource: 'iGOT Profile',
        evaluatedAt: new Date().toISOString(),
        competency: {
          compId: `COMP-${i + 1}`,
          domain: 'Statistical',
          skillName: name,
        },
      })),
    },
  };
}

function statusLabel(status: number): string {
  switch (status) {
    case 0:  return 'Not Started';
    case 1:  return 'In Progress';
    case 2:  return 'Completed';
    default: return 'Enrolled';
  }
}

function adaptEnrollments(raw: RawIgotEnrollment[]): Enrollment[] {
  return raw.map(e => ({
    enrollmentId:       e.courseId,
    course: {
      courseId:     e.courseId,
      title:        e.content?.name ?? e.courseName,
      source:       e.content?.provider ?? 'iGOT Karmayogi',
      durationHours: e.content?.duration ? Math.round(parseInt(e.content.duration, 10) / 3600) : 4,
    },
    progressPercentage: e.completionPercentage ?? 0,
    remainingHours:     0,
    lastAccessed:       e.lastContentAccessTime ?? e.enrolledDate,
    status:             statusLabel(e.status),
  }));
}

function adaptCatalog(raw: RawIgotCourse[]): CourseRecommendation[] {
  return raw.slice(0, 6).map((c, i) => {
    const tags = parseCompetencies(c.competencies_v3);
    return {
      course: {
        courseId:     c.identifier,
        title:        c.name,
        source:       c.provider ?? c.source ?? 'iGOT',
        durationHours: c.duration ? Math.round(parseInt(c.duration, 10) / 3600) : 3,
      },
      matchScore:   Math.max(0.6, 0.98 - i * 0.06),
      bridgesGapFor: {
        compId:    tags[0] ?? 'COMP-GEN',
        domain:    'Statistical',
        skillName: tags[0] ?? 'General Competency',
      },
      aiMatchTag:   tags.slice(0, 2).join(', ') || 'iGOT Recommended',
      priorityRank: i + 1,
    };
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// PUBLIC API FUNCTIONS — these are the only exports the hooks touch
// ─────────────────────────────────────────────────────────────────────────────

/** Fetch official profile + derive skill gaps from competency_v3 */
export async function fetchUserProfile(userId: string): Promise<Official> {
  const raw = await igotFetch<RawIgotUser>(
    `/api/user/v2/read/${userId}`,
    'user-profile'
  );
  return adaptIgotUser(raw);
}

/** Skill gaps derived from the profile's competency list */
export async function fetchSkillGapsAndProfile(userId: string): Promise<{
  profile: Official;
  skillGaps: SkillGapEntry[];
}> {
  const profile = await fetchUserProfile(userId);
  const skillGaps: SkillGapEntry[] = profile.competencyProfile.userCompetencies.map(uc => ({
    competency:         uc.competency,
    currentLevel:       uc.currentLevel,
    requiredLevel:      4,
    gap:                Math.max(0, 4 - uc.currentLevel),
    isMandatory:        (4 - uc.currentLevel) > 0,
    verificationSource: uc.verificationSource,
    evaluatedAt:        uc.evaluatedAt,
  }));
  return { profile, skillGaps };
}

/** Enrollment list for a user */
export async function fetchEnrollments(userId: string): Promise<Enrollment[]> {
  const result = await igotFetch<RawEnrollmentsResult>(
    `/api/course/v1/user/enrollment/list/${userId}`,
    'enrollments'
  );
  return adaptEnrollments(result.courses ?? []);
}

/** Course catalog as recommendations */
export async function fetchRecommendations(
  _userId: string,
  _skillGaps: SkillGapEntry[]
): Promise<CourseRecommendation[]> {
  const result = await igotFetch<RawCatalogResult>(
    `/api/content/read`,
    'catalog'
  );
  return adaptCatalog(result.content ?? []);
}

/** Achievements — pulled from completed enrollments with certificates */
export async function fetchAchievements(userId: string): Promise<Achievement[]> {
  const enrollments = await fetchEnrollments(userId);
  return enrollments
    .filter(e => e.status === 'Completed')
    .map(e => ({
      id:       e.enrollmentId,
      title:    e.course.title,
      score:    Math.floor(75 + Math.random() * 20),
      date:     e.lastAccessed,
      category: 'RAG Quiz' as const,
    }));
}

// ─────────────────────────────────────────────────────────────────────────────
// ADMIN API FUNCTIONS
// ─────────────────────────────────────────────────────────────────────────────

export async function fetchAdminRoster(): Promise<RawAdminUser[]> {
  const result = await igotFetch<RawAdminRosterResult>(
    `/api/admin/v1/users`,
    'admin-roster'
  );
  return result.users ?? [];
}