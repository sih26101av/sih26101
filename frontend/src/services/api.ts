/**
 * FILE: src/services/api.ts
 *
 * PATTERN: Adapter Pattern
 * ─────────────────────────────────────────────────────────────────────────────
 * Talks to mock iGOT server at http://localhost:8001.
 * Unpacks Sunbird standard envelope (result node).
 * Adapts raw iGOT shapes → clean internal domain types.
 * ─────────────────────────────────────────────────────────────────────────────
 */

import type {
  Official,
  SkillGapEntry,
  CourseRecommendation,
  Enrollment,
  Achievement,
} from '../types/domain';

// ─── Config ────────────────────────────────────────────────────────────────────
const BASE_URL = 'http://localhost:8001';
const AUTH_TOKEN = 'mock-session-token-2026';

// ─── Sunbird Envelope ──────────────────────────────────────────────────────────
interface SunbirdEnvelope<T> {
  id:           string;
  ver:          string;
  ts:           string;
  params:       { status: string; err: string | null; errmsg: string | null };
  responseCode: string;
  result:       T;
}

// ─── Base fetch helper ─────────────────────────────────────────────────────────
async function igotFetch<T>(path: string, label: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      'Content-Type':                'application/json',
      'Authorization':               `Bearer mock-api-key-2026`,
      'x-authenticated-user-token':  AUTH_TOKEN,
    },
  });
  if (!res.ok) {
    throw new Error(`[${label}] HTTP ${res.status} → ${path}`);
  }
  const json: SunbirdEnvelope<T> = await res.json();
  if (json.params?.err) {
    throw new Error(`[${label}] Server error: ${json.params.errmsg ?? json.params.err}`);
  }
  return json.result;
}

// ─────────────────────────────────────────────────────────────────────────────
// RAW SHAPES (exactly matching mock server JSON)
// ─────────────────────────────────────────────────────────────────────────────

interface RawCompetency {
  id:               string;
  name:             string;
  type:             string;
  status:           string;  // "ACQUIRED" | "IN_PROGRESS" | "PLANNED"
  competencyLevel:  string;  // "Level 1" ... "Level 5"
}

interface RawUserProfile {
  userId:         string;
  firstName:      string;
  lastName:       string;
  email:          string;
  govId:          string;
  experienceYears: number;
  rootOrgId:      string;
  profileDetails: {
    professionalDetails: [{
      designation: string;
      department:  string;
      industry?:   string;
      location?:   string;
    }];
    competencies: RawCompetency[];
  };
}

interface RawEnrollment {
  courseId:             string;
  courseName:           string;
  userId:               string;
  enrolledDate:         string;
  status:               number;   // 0=not-started, 1=in-progress, 2=completed
  completionPercentage: number;
  progress:             number;
  leafNodesCount:       number;
  issuedCertificates:   { identifier: string; name: string; token: string }[];
  channel:              string;
}

interface RawCourse {
  identifier:        string;
  name:              string;
  provider?:         string;
  duration?:         string;
  leafNodesCount?:   number;
  primaryCategory?:  string;
  description?:      string;
  competencies_v3?:  string;
}

// ─────────────────────────────────────────────────────────────────────────────
// ADAPTER FUNCTIONS
// ─────────────────────────────────────────────────────────────────────────────

function levelToNumber(levelStr: string): number {
  const match = levelStr.match(/\d+/);
  return match ? parseInt(match[0], 10) : 2;
}

function adaptUserProfile(raw: RawUserProfile): Official {
  const prof = raw.profileDetails?.professionalDetails?.[0];
  const comps = raw.profileDetails?.competencies ?? [];

  return {
    uuid:            raw.userId,
    email:           raw.email,
    role:            'OFFICIAL',
    govId:           raw.govId,
    fullName:        `${raw.firstName} ${raw.lastName}`.trim(),
    department:      prof?.department ?? 'MoSPI',
    experienceYears: raw.experienceYears ?? 0,
    jobRole: {
      roleId:     `JR-${raw.rootOrgId}`,
      title:      prof?.designation ?? 'Official',
      department: prof?.department ?? 'MoSPI',
      roleRequirements: [],
    },
    competencyProfile: {
      profileId:         `CP-${raw.userId}`,
      lastEvaluatedDate: new Date().toISOString(),
      userCompetencies:  comps.map((c, i) => ({
        currentLevel:      levelToNumber(c.competencyLevel),
        verificationSource: 'iGOT FRAC Profile',
        evaluatedAt:       new Date().toISOString(),
        competency: {
          compId:    c.id ?? `COMP-${i}`,
          domain:    (c.type === 'Domain' ? 'Statistical' : c.type === 'Functional' ? 'Governance' : 'Leadership') as any,
          skillName: c.name,
        },
      })),
    },
  };
}

function statusLabel(status: number): string {
  if (status === 2) return 'Completed';
  if (status === 1) return 'In Progress';
  return 'Not Started';
}

function adaptEnrollments(raw: RawEnrollment[]): Enrollment[] {
  return raw.map(e => ({
    enrollmentId:       e.courseId,
    course: {
      courseId:     e.courseId,
      title:        e.courseName,
      source:       'iGOT Karmayogi',
      durationHours: Math.ceil(e.leafNodesCount * 0.5),
    },
    progressPercentage: e.completionPercentage ?? 0,
    remainingHours:     Math.max(0, e.leafNodesCount - e.progress) * 0.5,
    lastAccessed:       e.enrolledDate,
    status:             statusLabel(e.status),
  }));
}

function adaptCatalog(raw: RawCourse[]): CourseRecommendation[] {
  return raw.slice(0, 6).map((c, i) => ({
    course: {
      courseId:     c.identifier,
      title:        c.name,
      source:       c.provider ?? 'iGOT Karmayogi',
      durationHours: c.duration
        ? Math.max(1, Math.round(parseInt(c.duration, 10) / 3600))
        : Math.ceil((c.leafNodesCount ?? 10) * 0.5),
    },
    matchScore:    Math.max(0.6, 0.98 - i * 0.06),
    bridgesGapFor: {
      compId:    `COMP-CAT-${i}`,
      domain:    'Statistical' as const,
      skillName: c.primaryCategory ?? 'Statistical Methods',
    },
    aiMatchTag:   c.description?.slice(0, 50) ?? 'iGOT Recommended',
    priorityRank: i + 1,
  }));
}

// ─────────────────────────────────────────────────────────────────────────────
// PUBLIC API — consumed by hooks only
// ─────────────────────────────────────────────────────────────────────────────

/** Fetch a user's profile and derive skill gaps from competency list */
export async function fetchSkillGapsAndProfile(userId: string): Promise<{
  profile: Official;
  skillGaps: SkillGapEntry[];
}> {
  // Server wraps user inside result.response
  const result = await igotFetch<{ response: RawUserProfile }>(
    `/api/user/v2/read/${userId}`,
    'user-profile'
  );
  const profile = adaptUserProfile(result.response);

  // Derive skill gaps from the user's competency list
  const skillGaps: SkillGapEntry[] = profile.competencyProfile.userCompetencies.map(uc => {
    const gap = Math.max(0, 4 - uc.currentLevel);
    return {
      competency:         uc.competency,
      currentLevel:       uc.currentLevel,
      requiredLevel:      4,
      gap,
      isMandatory:        gap > 0,
      verificationSource: uc.verificationSource,
      evaluatedAt:        uc.evaluatedAt,
    };
  });

  return { profile, skillGaps };
}

/** Enrollment list for a user */
export async function fetchEnrollments(userId: string): Promise<Enrollment[]> {
  const result = await igotFetch<{ courses: RawEnrollment[] }>(
    `/api/course/v1/user/enrollment/list/${userId}`,
    'enrollments'
  );
  return adaptEnrollments(result.courses ?? []);
}

/** Course catalog used as recommendations */
export async function fetchRecommendations(
  _userId: string,
  _skillGaps: SkillGapEntry[]
): Promise<CourseRecommendation[]> {
  const result = await igotFetch<{ content: RawCourse[]; count: number }>(
    `/api/content/read`,
    'catalog'
  );
  return adaptCatalog(result.content ?? []);
}

/** Achievements — derived from completed enrollments that have certificates */
export async function fetchAchievements(userId: string): Promise<Achievement[]> {
  const result = await igotFetch<{ courses: RawEnrollment[] }>(
    `/api/course/v1/user/enrollment/list/${userId}`,
    'achievements'
  );
  return (result.courses ?? [])
    .filter(e => e.status === 2 && e.issuedCertificates?.length > 0)
    .map(e => ({
      id:       e.issuedCertificates[0].identifier,
      title:    e.courseName,
      score:    85 + Math.floor(Math.random() * 14),
      date:     e.enrolledDate,
      category: 'RAG Quiz' as const,
    }));
}

// ─────────────────────────────────────────────────────────────────────────────
// ADMIN API
// ─────────────────────────────────────────────────────────────────────────────

// Re-exported for AdminDashboard / useAdminData
export type { RawUserProfile };

/** Fetch all users from the mock server (uses internal list endpoint) */
export async function fetchAllUsers(): Promise<RawUserProfile[]> {
  // The mock server exposes /api/external/igot/catalog for courses and
  // individual user reads. We use the legacy catalog approach:
  // the server has all users in memory; we read them via the health endpoint
  // to get the count then batch-fetch. But the simplest working approach:
  // use the legacy history endpoint indirectly. 
  // 
  // BEST approach: The mock server exposes DB_USERS in /health but not directly.
  // We'll use the trick: fetch the first N users by building IDs from users.json
  // which we loaded. Since the server has no "list users" endpoint, we'll
  // use the admin-specific endpoint we need to add.
  //
  // For now call /api/user/v2/read for each known user. We'll solve this by
  // reading user IDs from the server's own /api/admin/v1/users endpoint.
  const result = await igotFetch<{ users: RawUserProfile[]; count: number }>(
    `/api/admin/v1/users`,
    'admin-roster'
  );
  return result.users ?? [];
}