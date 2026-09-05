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
  KarmaLedger,
  KarmaEventType,
} from '../types/domain';
import { refresh } from './authApi';

// ── Config ─────────────────────────────────────────────────────────────────────
const LMS_BASE_URL  = 'http://localhost:8000';

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

// ── RAW SHAPES (used in lmsFetch generic types) ───────────────────────────────
interface RawCompetency {
  id:               string;
  name:             string;
  type:             string;
  status:           string;
  competencyLevel:  string;
}

// ── Shared helpers ─────────────────────────────────────────────────────────────
function levelToNumber(levelStr: string): number {
  const match = levelStr?.match(/\d+/);
  return match ? parseInt(match[0], 10) : 2;
}


// ─────────────────────────────────────────────────────────────────────────────
// lmsFetch — My App Backend (port 8000), with JWT injection + 401 interceptor
// ─────────────────────────────────────────────────────────────────────────────
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


// ── Admin roster user shape (from /api/admin/v1/users via backend proxy) ──────
interface RawUserProfile {
  userId:            string;
  govId:             string;
  firstName:         string;
  lastName:          string;
  email:             string;
  designation?:      string;
  department?:       string;
  competencies?:     RawCompetency[];
  enrollmentStatus?: number;
  missingSkill?:     string;
}

// ─────────────────────────────────────────────────────────────────────────────
// PUBLIC API — consumed by hooks only
// ─────────────────────────────────────────────────────────────────────────────

export async function fetchSkillGapsAndProfile(userId: string): Promise<{
  profile: Official;
  skillGaps: SkillGapEntry[];
}> {
  // Both calls go through My App Backend (authenticated, userId-based)
  const [profileRaw, gapsRaw] = await Promise.all([
    lmsFetch<{
      userId: string; govId: string; firstName: string; lastName: string;
      email: string; designation: string; department: string;
      competencies: RawCompetency[];
    }>(`/api/v1/profile/${userId}`, 'user-profile'),
    lmsFetch<{
      userId: string; govId: string; jobRole: string; department: string;
      skillGaps: { competencyId: string; skillName: string; domain: string;
                   currentLevel: number; targetLevel: number; gapScore: number }[];
    }>(`/api/v1/learner/${userId}/skill-gaps`, 'skill-gaps'),
  ]);

  const profile: Official = {
    uuid:            profileRaw.userId,
    email:           profileRaw.email ?? '',
    role:            'OFFICIAL',
    govId:           profileRaw.govId ?? profileRaw.userId,
    fullName:        `${profileRaw.firstName ?? ''} ${profileRaw.lastName ?? ''}`.trim(),
    department:      profileRaw.department ?? 'MoSPI',
    experienceYears: 0,
    jobRole: {
      roleId:           `JR-${profileRaw.govId}`,
      title:            profileRaw.designation ?? 'Official',
      department:       profileRaw.department ?? 'MoSPI',
      roleRequirements: [],
    },
    competencyProfile: {
      profileId:         `CP-${profileRaw.userId}`,
      lastEvaluatedDate: new Date().toISOString(),
      userCompetencies:  (profileRaw.competencies ?? []).map((c, i) => ({
        currentLevel:       levelToNumber(c.competencyLevel),
        verificationSource: 'iGOT FRAC Profile',
        evaluatedAt:        new Date().toISOString(),
        competency: {
          compId:    c.id ?? `COMP-${i}`,
          domain:    (c.type === 'Domain' ? 'Statistical' : c.type === 'Functional' ? 'Governance' : 'Leadership') as any,
          skillName: c.name,
        },
      })),
    },
  };

  const skillGaps: SkillGapEntry[] = gapsRaw.skillGaps.map(g => ({
    competency:         { compId: g.competencyId, domain: g.domain as any, skillName: g.skillName },
    currentLevel:       g.currentLevel,
    requiredLevel:      g.targetLevel,
    gap:                g.gapScore,
    isMandatory:        g.gapScore > 0,
    verificationSource: 'iGOT FRAC Profile',
    evaluatedAt:        new Date().toISOString(),
  }));

  return { profile, skillGaps };
}

export async function fetchEnrollments(userId: string): Promise<Enrollment[]> {
  const result = await lmsFetch<{
    status: string;
    enrollments: {
      enrollmentId: string; courseId: string; courseTitle: string; provider: string;
      durationHours: number; progressPercentage: number; remainingHours: number;
      lastAccessed: string; status: string;
    }[];
  }>(`/api/v1/learner/${userId}/enrollments`, 'enrollments');

  return (result.enrollments ?? []).map(e => ({
    enrollmentId:       e.enrollmentId,
    course: {
      courseId:     e.courseId,
      title:        e.courseTitle,
      source:       e.provider,
      durationHours: e.durationHours,
    },
    progressPercentage: e.progressPercentage,
    remainingHours:     e.remainingHours,
    lastAccessed:       e.lastAccessed,
    status:             e.status,
  }));
}

export async function fetchRecommendations(
  userId: string,
  _skillGaps: SkillGapEntry[]
): Promise<CourseRecommendation[]> {
  const result = await lmsFetch<{
    status: string;
    recommendations: {
      courseId:       string;
      title:          string;
      provider:       string;
      durationHours:  number;
      finalScore:     number;
      relevanceScore: number;
      qualityScore:   number;
      isTpac:         boolean;
      competencyId:   string;
      competencyName: string;
      priorityRank:   number;
      matchReasons:   string[];
      // legacy fallbacks (always present on backend)
      matchReason:    string;
      tags:           string[];
    }[];
  }>(`/api/v1/learner/${userId}/recommendations`, 'recommendations');

  return (result.recommendations ?? []).map((r) => ({
    course: {
      courseId:      r.courseId,
      title:         r.title,
      source:        r.provider,
      durationHours: r.durationHours,
    },
    // finalScore from backend — no more fabricated client-side value
    matchScore:     r.finalScore ?? 0,
    finalScore:     r.finalScore ?? 0,
    relevanceScore: r.relevanceScore ?? 0,
    qualityScore:   r.qualityScore ?? 0,
    isTpac:         r.isTpac ?? false,
    bridgesGapFor: {
      compId:    r.competencyId ?? `COMP-${r.priorityRank}`,
      domain:    'Statistical' as const,
      skillName: r.competencyName ?? (r.tags?.[0] ?? 'General'),
    },
    aiMatchTag:   r.matchReasons?.[0] ?? r.matchReason ?? '',
    matchReasons: r.matchReasons ?? (r.matchReason ? [r.matchReason] : []),
    priorityRank: r.priorityRank,
  }));
}

export async function fetchAchievements(userId: string): Promise<Achievement[]> {
  const result = await lmsFetch<{
    status: string;
    achievements: Achievement[];
  }>(`/api/v1/learner/${userId}/achievements`, 'achievements');
  return result.achievements ?? [];
}


// ─────────────────────────────────────────────────────────────────────────────
// ADMIN API — routed through My App Backend (authenticated + role=admin)
// ─────────────────────────────────────────────────────────────────────────────




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

/**
 * Fetch the FRAC competency dictionary via the LMS backend's admin proxy endpoint.
 * The backend enforces role=admin before proxying to the mock server with auth.
 */
export interface FracCompetency {
  competency_id: string;
  name:          string;
  category:      string;
  description:   string;
}

export async function fetchCompetencies(): Promise<FracCompetency[]> {
  const result = await lmsFetch<{ competencies: FracCompetency[]; count: number }>(
    '/api/v1/admin/frac/competencies',
    'frac-competencies'
  );
  return result.competencies ?? [];
}


// ─────────────────────────────────────────────────────────────────────────────
// KARMA POINTS API
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Fetches the full Karma Points ledger for a learner.
 * Returns totalPoints, streak, monthlyUsage, breakdown, and the 10 most recent
 * transactions. Returns null (never throws) on error so the dashboard degrades
 * gracefully if the karma service is unavailable.
 */
export async function fetchKarmaLedger(userId: string): Promise<KarmaLedger | null> {
  try {
    return await lmsFetch<KarmaLedger>(
      `/api/v1/learner/${userId}/karma`,
      'karma-ledger',
    );
  } catch {
    return null;
  }
}

/**
 * Awards Karma Points for a specific user action.
 * Follows the Strategy pattern on the backend — the engine picks the right
 * strategy and enforces all iGOT rules (cap, idempotency, etc.).
 */
export async function awardKarmaEvent(
  userId: string,
  eventType: KarmaEventType,
  options: { courseId?: string; isCbp?: boolean; is_mdo_onboarded?: boolean } = {},
): Promise<{ pointsAwarded: number; capReached: boolean; newBalance: number }> {
  return lmsFetch(
    `/api/v1/learner/${userId}/karma/event`,
    'karma-award',
    {
      method: 'POST',
      body: JSON.stringify({
        eventType,
        courseId: options.courseId ?? null,
        isCbp: options.isCbp ?? false,
        is_mdo_onboarded: options.is_mdo_onboarded ?? false,
      }),
    },
  );
}

/**
 * Retroactive CBP +10 claim. Idempotent — safe to call multiple times.
 */
export async function claimCbpBonus(
  userId: string,
  courseId: string,
): Promise<{ pointsAwarded: number; alreadyClaimed: boolean; newBalance: number }> {
  return lmsFetch(
    `/api/v1/learner/${userId}/karma/claim-cbp-bonus`,
    'karma-cbp-claim',
    {
      method: 'POST',
      body: JSON.stringify({ courseId }),
    },
  );
}