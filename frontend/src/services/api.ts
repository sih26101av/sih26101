/**
 * FILE: src/services/api.ts
 *
 * PATTERN: Adapter Pattern
 * ─────────────────────────────────────────────────────────────────────────────
 * Two distinct fetch helpers:
 *
 * 1. igotFetch — talks directly to the mock iGOT server (port 8001) using
 *    Sunbird-style headers. Used for learner profile/enrollment data that the
 *    frontend still fetches directly. Untouched from the original.
 *
 * 2. lmsFetch — talks to My App Backend (port 8000). Injects the JWT access
 *    token from AuthContext. On 401, silently calls /auth/refresh and retries
 *    the request ONCE. If refresh also fails, calls logout() and redirects
 *    to /login.
 *
 * Token access strategy
 * ─────────────────────
 * AuthContext lives in React; api.ts is a plain module. We bridge them via
 * a module-level token store that AuthContext writes to via setApiToken().
 * This avoids prop-drilling or context-in-service anti-patterns.
 * ─────────────────────────────────────────────────────────────────────────────
 */

import type {
  Official,
  SkillGapEntry,
  CourseRecommendation,
  Enrollment,
  Achievement,
} from '../types/domain';
import { refresh } from './authApi';

// ── Config ─────────────────────────────────────────────────────────────────────
const IGOT_BASE_URL = 'http://localhost:8001';
const LMS_BASE_URL  = 'http://localhost:8000';
const AUTH_TOKEN    = 'mock-session-token-2026';

// ── Module-level token store (written by AuthContext on login/refresh) ──────────
let _accessToken: string | null = null;
let _onLogout: (() => void) | null = null;

/**
 * Called by AuthContext immediately after login or a successful token refresh.
 * This keeps the access token in memory without exposing it to the DOM.
 */
export function setApiToken(token: string | null): void {
  _accessToken = token;
}

/**
 * Called by AuthContext on mount to register the logout callback.
 * The interceptor calls this when a refresh fails so we cleanly log out.
 */
export function registerLogoutCallback(cb: () => void): void {
  _onLogout = cb;
}

// ── Sunbird Envelope ───────────────────────────────────────────────────────────
interface SunbirdEnvelope<T> {
  id:           string;
  ver:          string;
  ts:           string;
  params:       { status: string; err: string | null; errmsg: string | null };
  responseCode: string;
  result:       T;
}

// ── igotFetch — direct to mock iGOT server (port 8001) ───────────────────────
async function igotFetch<T>(path: string, label: string): Promise<T> {
  const res = await fetch(`${IGOT_BASE_URL}${path}`, {
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

// ── lmsFetch — to My App Backend (port 8000), with 401 interceptor ────────────
/**
 * Fetches from the LMS backend with automatic JWT injection and 401 retry.
 *
 * On 401:
 *  1. Calls /auth/refresh (uses the httpOnly cookie automatically).
 *  2. Updates the in-memory token via setApiToken().
 *  3. Retries the original request once with the new token.
 *  4. If the retry still fails, calls _onLogout() and throws.
 */
async function lmsFetch<T>(
  path: string,
  label: string,
  options: RequestInit = {},
): Promise<T> {
  const makeHeaders = (token: string | null) => ({
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers as Record<string, string> ?? {}),
  });

  const doRequest = (token: string | null) =>
    fetch(`${LMS_BASE_URL}${path}`, {
      ...options,
      headers: makeHeaders(token),
      credentials: 'include',
    });

  let res = await doRequest(_accessToken);

  // ── 401 interceptor ─────────────────────────────────────────────────────────
  if (res.status === 401) {
    try {
      const { access_token } = await refresh();
      setApiToken(access_token);
      res = await doRequest(access_token);
    } catch {
      // Refresh failed — session is dead
      _onLogout?.();
      // Redirect to login (can't use React Router here — plain navigate)
      window.location.href = '/login';
      throw new Error(`[${label}] Session expired. Please log in again.`);
    }
  }

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body?.detail ?? detail;
    } catch { /* ignore */ }
    throw new Error(`[${label}] ${detail}`);
  }

  // Handle 204 No Content
  const contentType = res.headers.get('content-type') ?? '';
  if (res.status === 204 || !contentType.includes('application/json')) {
    return undefined as unknown as T;
  }

  return res.json() as Promise<T>;
}

// ─────────────────────────────────────────────────────────────────────────────
// RAW SHAPES (exactly matching mock server JSON)
// ─────────────────────────────────────────────────────────────────────────────

interface RawCompetency {
  id:               string;
  name:             string;
  type:             string;
  status:           string;
  competencyLevel:  string;
}

interface RawUserProfile {
  userId:          string;
  firstName:       string;
  lastName:        string;
  email:           string;
  govId:           string;
  experienceYears: number;
  rootOrgId:       string;
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
  status:               number;
  completionPercentage: number;
  progress:             number;
  leafNodesCount:       number;
  issuedCertificates:   { identifier: string; name: string; token: string }[];
  channel:              string;
}

interface RawCourse {
  identifier:       string;
  name:             string;
  provider?:        string;
  duration?:        string;
  leafNodesCount?:  number;
  primaryCategory?: string;
  description?:     string;
  competencies_v3?: string;
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

export async function fetchSkillGapsAndProfile(userId: string): Promise<{
  profile: Official;
  skillGaps: SkillGapEntry[];
}> {
  const result = await igotFetch<{ response: RawUserProfile }>(
    `/api/user/v2/read/${userId}`,
    'user-profile'
  );
  const profile = adaptUserProfile(result.response);

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

export async function fetchEnrollments(userId: string): Promise<Enrollment[]> {
  const result = await igotFetch<{ courses: RawEnrollment[] }>(
    `/api/course/v1/user/enrollment/list/${userId}`,
    'enrollments'
  );
  return adaptEnrollments(result.courses ?? []);
}

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
// ADMIN API — routed through My App Backend (authenticated + role=admin)
// ─────────────────────────────────────────────────────────────────────────────

export type { RawUserProfile };

/**
 * Fetch all users via the LMS backend's admin proxy endpoint.
 * The backend enforces role=admin before proxying to the mock server.
 */
export async function fetchAllUsers(): Promise<RawUserProfile[]> {
  const result = await lmsFetch<{ users: RawUserProfile[]; count: number }>(
    '/api/v1/admin/users',
    'admin-roster'
  );
  return result.users ?? [];
}