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
  KarmaAward,
  KarmaRules,
  EvidenceConfidence,
  LearningPathwayResponse,
  RecommendationWhy,
  FeedbackEvent,
  CareerReadiness,
  LevelDispute,
  DiagnosticView,
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
  // Session ended → drop per-user client caches so the next login never sees them.
  if (token === null) _sessionClearers.forEach((clear) => clear());
}

const _sessionClearers = new Set<() => void>();

/** Register a cache to wipe when the session ends (token set to null). */
export function onSessionEnd(clear: () => void): void {
  _sessionClearers.add(clear);
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

  // FormData bodies set their own multipart boundary header.
  const isForm = typeof FormData !== 'undefined' && options.body instanceof FormData;
  const makeHeaders = (token: string | null) => ({
    ...(isForm ? {} : { 'Content-Type': 'application/json' }),
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
          // Backend now sends correct domain strings — pass through with safe fallback
          domain:    (c.type === 'Domain'      ? 'Statistical'
                    : c.type === 'Functional'  ? 'Governance'
                    : c.type === 'Behavioural' ? 'Leadership'
                    : c.type === 'Technical'   ? 'Technical'
                    : 'Statistical') as any,
          skillName: c.name,
        },
      })),
    },
  };

  // Backend now returns correct domain strings, confidence tags, b_k rawScore, and evidence breakdown
  const skillGaps: SkillGapEntry[] = (gapsRaw.skillGaps ?? []).map((g: any) => ({
    competency: {
      compId:    g.competencyId,
      domain:    (g.domain as any) ?? 'Statistical',
      skillName: g.skillName,
    },
    currentLevel:       g.currentLevel,
    requiredLevel:      g.targetLevel,
    gap:                g.gapScore,
    isMandatory:        g.gapScore > 0,
    verificationSource: 'iGOT FRAC Profile',
    evaluatedAt:        new Date().toISOString(),
    confidence:         g.confidence as EvidenceConfidence | undefined,
    basis:              g.basis,
    evidenceLevel:      g.evidenceLevel ?? null,
    crosswalk:          g.crosswalk ?? null,
    opportunity:        g.opportunity ?? null,
    channels:           g.channels ?? null,
    evidenceCompleteness: g.evidenceCompleteness ?? null,
    peerFeedback:       g.peerFeedback ?? 0,
    proficiency:        g.proficiency ?? null,
    coldStartPrior:     g.coldStartPrior ?? null,
    whyThisLevel:       g.whyThisLevel ?? null,
    rawScore:           g.rawScore,
    evidence:           g.evidence,
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
      courseLevel?:   number | null;
      tpacSource?:    'verified' | 'inferred' | 'none';
      measuredUplift?: number | null;
      modality?:      string | null;
      mandatory?:     boolean;
      why?:           RecommendationWhy | null;
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
    competencyId:   r.competencyId,
    courseLevel:    r.courseLevel ?? null,
    tpacSource:     r.tpacSource,
    measuredUplift: r.measuredUplift ?? null,
    modality:       r.modality ?? null,
    mandatory:      r.mandatory ?? false,
    why:            r.why ?? null,
  }));
}

// ── Recommendation feedback (clicks, enrolments, thumbs) ─────────────────────
/** Logs one interaction; returns the learner's current votes. Never throws (feedback is best-effort). */
export async function sendRecommendationFeedback(
  rec: CourseRecommendation,
  event: FeedbackEvent,
  context: Record<string, unknown> = {},
): Promise<Record<string, 'up' | 'down'> | null> {
  try {
    const res = await lmsFetch<{ votes: Record<string, 'up' | 'down'> }>(
      '/api/v1/recommendations/feedback', 'recommendation-feedback', {
        method: 'POST',
        body: JSON.stringify({
          courseId: rec.course.courseId, event, competencyId: rec.competencyId ?? rec.bridgesGapFor.compId,
          rank: rec.priorityRank, finalScore: rec.finalScore,
          context: { mandatory: rec.mandatory ?? false, courseLevel: rec.courseLevel ?? null, ...context },
        }),
      });
    return res?.votes ?? null;
  } catch (err) {
    console.warn('[feedback]', err);
    return null;
  }
}

export async function fetchMyRecommendationVotes(): Promise<Record<string, 'up' | 'down'>> {
  try {
    const res = await lmsFetch<{ votes: Record<string, 'up' | 'down'> }>(
      '/api/v1/recommendations/feedback/mine', 'recommendation-votes');
    return res?.votes ?? {};
  } catch {
    return {};
  }
}

// ── Career readiness ─────────────────────────────────────────────────────────
export async function fetchCareerReadiness(userId: string, targetRoleId?: string): Promise<CareerReadiness> {
  const q = targetRoleId ? `?targetRoleId=${encodeURIComponent(targetRoleId)}` : '';
  return lmsFetch<CareerReadiness>(`/api/v1/learner/${userId}/career-readiness${q}`, 'career-readiness');
}

// ── Level disputes → adaptive level check ───────────────────────────────────
export async function openLevelDispute(
  competencyId: string, claimedLevel: number | null, reason: string,
): Promise<{ dispute: LevelDispute; session: DiagnosticView | null }> {
  return lmsFetch('/api/v1/level-disputes', 'level-dispute', {
    method: 'POST',
    body: JSON.stringify({ competencyId, claimedLevel, reason: reason || null }),
  });
}

export async function answerDiagnostic(sessionId: string, itemId: string, optionIndex: number): Promise<DiagnosticView> {
  return lmsFetch(`/api/v1/diagnostic/${sessionId}/answer`, 'diagnostic-answer', {
    method: 'POST',
    body: JSON.stringify({ itemId, optionIndex }),
  });
}

/**
 * Level-by-level learning paths for every role competency plus one study
 * order across them. `competencyId` narrows to one path; `budgetHours` caps
 * the study plan (ladders that don't fit come back under studyPlan.deferred).
 */
export async function fetchLearningPathways(
  userId: string,
  opts: { competencyId?: string; budgetHours?: number; unbudgeted?: boolean } = {},
): Promise<LearningPathwayResponse> {
  const params = new URLSearchParams();
  if (opts.competencyId) params.set('competencyId', opts.competencyId);
  if (opts.budgetHours && opts.budgetHours > 0) params.set('budgetHours', String(opts.budgetHours));
  if (opts.unbudgeted) params.set('unbudgeted', 'true');
  const qs = params.toString();
  const result = await lmsFetch<{ status: string } & LearningPathwayResponse>(
    `/api/v1/learner/${userId}/pathway${qs ? `?${qs}` : ''}`,
    'pathway',
  );
  return { pathways: result.pathways ?? [], studyPlan: result.studyPlan };
}

export async function fetchAchievements(userId: string): Promise<Achievement[]> {
  const result = await lmsFetch<{
    status: string;
    achievements: Achievement[];
  }>(`/api/v1/learner/${userId}/achievements`, 'achievements');
  return result.achievements ?? [];
}


// ─────────────────────────────────────────────────────────────────────────────
// ASSESSMENT STUDIO — quiz grading ↔ skill gap (routers/rag.py)
// ─────────────────────────────────────────────────────────────────────────────

export type QuizDifficulty = 'Easy' | 'Medium' | 'Hard';

export interface SkillSnapshot {
  level: number | null;
  score: number;
  confidence: string | null;
  basis: string | null;
  targetLevel: number | null;
  gap: number | null;
}

export interface QuizSkillImpact {
  recorded: boolean;
  linkedToSkillGap: boolean;
  competencyId: string | null;
  competencyName: string | null;
  linkMethod: string;
  before: Partial<SkillSnapshot>;
  after: Partial<SkillSnapshot>;
  abilityBefore?: number;
  abilityAfter?: number;
  abilityDelta?: number;
  scoreDelta?: number;
  levelDelta?: number;
  perQuestion?: { difficulty: QuizDifficulty; correct: boolean; expected: number; delta: number }[];
  note?: string;
}

export type QuizQuestionType = 'mcq' | 'true_false' | 'multi_select' | 'fill_blank' | 'numeric';

/** Per question: option index (mcq, true_false), indices (multi_select), text (fill_blank, numeric). */
export type QuizAnswer = number | number[] | string | null;

export interface QuizCitation {
  chunkId: string;
  locator: string;   // "Page 4" | "Slide 2" | "Section 3: Price collection"
  quote: string;     // verbatim sentence from the source
  passage: string;   // surrounding source passage
}

export interface ItemCalibration {
  difficulty: QuizDifficulty;
  source: 'llm_tag' | 'response_data';
  llmDifficulty: QuizDifficulty;
  responses: number;
  pValue?: number;
  b?: number;
  calibratedDifficulty?: QuizDifficulty;
  agreesWithLlm?: boolean;
}

/** A question as returned by POST /api/v1/rag/upload (media quizzes: mcq fields only). */
export interface DocQuizQuestion {
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
  difficulty?: QuizDifficulty | null;
  type?: QuizQuestionType;
  correct_answers?: number[] | null;
  unit?: string | null;
  citations?: QuizCitation[] | null;
  calibration?: ItemCalibration | null;
  translations?: {
    hi?: { question?: string; options?: string[]; explanation?: string; unit?: string; solution?: string };
  } | null;
}

export interface QuizQuestionReview {
  index: number;
  type?: QuizQuestionType;
  question: string;
  difficulty: QuizDifficulty;
  correct: boolean;
  yourAnswer: string | null;
  correctAnswer: string | null;
  explanation: string;
  /** Why THIS answer is wrong (empty when correct). */
  feedback?: string;
  solution?: string | null;
  /** The exact source passage supporting the correct answer (document quizzes). */
  source?: QuizCitation | null;
  /** A catalogue course for the missed point. */
  course?: { courseId: string; title: string; level: number | null; durationHours: number | null; rating: number | null; fromCompetency?: boolean } | null;
  calibration?: ItemCalibration | null;
  review?: { status: string; note?: string } | null;
  translation?: { question?: string; explanation?: string } | null;
}

export interface QuizGradeResult {
  quiz_id: string;
  score: number;
  passed: boolean;
  correct_count: number;
  total_questions: number;
  message: string;
  evidenceWritten: boolean | null;
  karmaAwarded: number | null;
  difficulty: QuizDifficulty | null;
  weighted_score: number | null;
  skillImpact: QuizSkillImpact | null;
  questionReview: QuizQuestionReview[] | null;
  recommendations: {
    nextDifficulty: QuizDifficulty;
    nextDifficultyReason: string;
    focusTopics: string[];
    courses: { courseId: string; title: string; level: number | null; durationHours: number | null; rating: number | null }[];
    summary: string;
  } | null;
}

export interface QuizAttemptRecord {
  id: string;
  quizId: string;
  title: string;
  date: string | null;
  score: number;
  passed: boolean;
  weightedScore: number | null;
  difficulty: QuizDifficulty | null;
  competencyId: string | null;
  competencyName: string | null;
  abilityBefore: number | null;
  abilityAfter: number | null;
}

/** Grade a quiz with the learner's JWT (the backend derives the user from it). */
export async function gradeQuiz(quizId: string, answers: QuizAnswer[]): Promise<QuizGradeResult> {
  return lmsFetch<QuizGradeResult>('/api/v1/rag/grade', 'grade', {
    method: 'POST',
    body: JSON.stringify({ quiz_id: quizId, answers }),
  });
}

/** The signed-in learner's graded quiz attempts, newest first. */
export async function fetchQuizAttempts(): Promise<QuizAttemptRecord[]> {
  const result = await lmsFetch<{ attempts: QuizAttemptRecord[] }>('/api/v1/rag/attempts', 'quiz attempts');
  return result?.attempts ?? [];
}


// ─────────────────────────────────────────────────────────────────────────────
// CERTIFICATES — external certificate → FRAC evidence (routers/competency.py)
// Upload writes DOCUMENTED evidence at once; an admin approval makes it VERIFIED.
// ─────────────────────────────────────────────────────────────────────────────

export type CertificateStatus = 'PENDING' | 'VERIFIED' | 'REJECTED';

export interface CertificateCompetency {
  competency_id: string;
  competency_name: string;
  extracted_level: number;
  issue_date: string | null;
  justification: string;
  match_score?: number | null;
}

export interface CertificateSubmission {
  id: string;
  filename: string;
  issuingOrganization: string | null;
  extractor: string;
  status: CertificateStatus;
  verification: 'documented' | 'verified' | 'rejected';
  competencies: CertificateCompetency[];
  reviewNote: string | null;
  createdAt: string | null;
  reviewedAt: string | null;
  // Admin view only
  userId?: string;
  reviewedBy?: string | null;
  isValidCredential?: boolean;
}

export interface CertificateUploadResult {
  status: 'success' | 'duplicate' | 'no_evidence';
  message: string;
  certificate?: CertificateSubmission | null;
}

export async function uploadCertificate(file: File): Promise<CertificateUploadResult> {
  const form = new FormData();
  form.append('file', file);
  return lmsFetch<CertificateUploadResult>('/api/v1/competencies/upload-certificate', 'certificate upload', {
    method: 'POST',
    body: form,
  });
}

export async function fetchMyCertificates(): Promise<CertificateSubmission[]> {
  const r = await lmsFetch<{ certificates: CertificateSubmission[] }>('/api/v1/competencies/certificates', 'certificates');
  return r?.certificates ?? [];
}

export const fetchCertificateReviews = (status: CertificateStatus | 'ALL' = 'PENDING') =>
  lmsFetch<{ certificates: CertificateSubmission[]; pendingCount: number }>(
    `/api/v1/competencies/certificates/review?status=${status}`, 'certificate review');

export const reviewCertificate = (id: string, decision: 'approve' | 'reject', note?: string) =>
  lmsFetch<{ status: string; certificate: CertificateSubmission }>(
    `/api/v1/competencies/certificates/${encodeURIComponent(id)}/review`, 'certificate review', {
      method: 'POST',
      body: JSON.stringify({ decision, note: note || null }),
    });


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
// ADMIN INSIGHTS (SCIL v6) — computed on synthetic mock data
// ─────────────────────────────────────────────────────────────────────────────

export interface GsbpmScopeReport {
  cycle: { id?: string; label?: string };
  officeId: string | null;
  threshold: number;
  totalOfficerHours: number;
  coreShare: number;
  inScopeCount: number;
  outOfScopeCount: number;
  coreSubprocesses: { id: string; name: string; officerHours: number; share: number; cumulativeShare: number }[];
  competencies: {
    competencyId: string; competencyName: string; inScope: boolean; subprocesses: string[];
    coreSubprocesses: string[]; officerHours: number; share: number; reason: string;
  }[];
  offices: { officeId: string; name: string; totalOfficerHours: number }[];
  method: string;
  dataNote: string;
}

/** SCIL v6 §1 — 80% officer-hours scoping report (whole NSO, or one office). */
export async function fetchGsbpmScope(officeId?: string): Promise<GsbpmScopeReport> {
  const qs = officeId ? `?officeId=${encodeURIComponent(officeId)}` : '';
  return lmsFetch<GsbpmScopeReport>(`/api/v1/admin/gsbpm/scope${qs}`, 'gsbpm-scope');
}

export interface PrerequisiteEdge {
  id: string;
  from: { competencyId: string; level: number };
  to: { competencyId: string; level: number };
  fromName: string;
  toName: string;
  source: string;
  rationale?: string;
}

export interface PrerequisiteSuggestion {
  from: { competencyId: string; competencyName: string; level: number };
  to: { competencyId: string; competencyName: string; level: number };
  effect: number;
  ci95: [number, number];
  pValue: number;
  nWith: number;
  nWithout: number;
  status: 'new_suggestion' | 'supports_expert_edge';
  expertEdgeId: string | null;
  applied: false;
}

export interface PrerequisiteDagReport {
  edges: PrerequisiteEdge[];
  validation: { cycle: string[] | null; rejected: boolean; invalid: number; received: number };
  enforced: boolean;
  inference: {
    testedPairs: number; fdr: number; minEffect: number; minGroup: number;
    suggestions: PrerequisiteSuggestion[]; method: string;
  } | null;
  dataNote: string;
}

export interface CourseUplift {
  courseId: string;
  title: string;
  competencyId: string;
  competencyName: string;
  courseLevel: number;
  format: string | null;
  rating: number | null;
  enrollmentCount: number | null;
  n: number;
  controls: number;
  controlsEffectiveN: number;
  naiveUplift: number;
  ipwUplift: number;
  prior: number;
  measuredUplift: number;
  ci95: [number, number];
  ipwCi95: [number, number];
  misTagFlag: boolean;
  flagReason: string | null;
}

export interface TrainingEffectivenessReport {
  summary: {
    courses: number; learnerRecords: number; comparisonEpisodes: number; flagged: number;
    medianMeasuredUplift: number; priorsByLevel: Record<string, number>;
  };
  courses: CourseUplift[];
  constants: Record<string, number | number[]>;
  method: string;
  dataNote: string;
}

/** SCIL v6 §6 — courses by measured uplift with CIs and the mis-tag flag. */
export async function fetchTrainingEffectiveness(
  opts: { competencyId?: string; flaggedOnly?: boolean; minLearners?: number } = {},
): Promise<TrainingEffectivenessReport> {
  const params = new URLSearchParams();
  if (opts.competencyId) params.set('competencyId', opts.competencyId);
  if (opts.flaggedOnly) params.set('flaggedOnly', 'true');
  if (opts.minLearners) params.set('minLearners', String(opts.minLearners));
  const qs = params.toString();
  return lmsFetch<TrainingEffectivenessReport>(
    `/api/v1/admin/training-effectiveness${qs ? `?${qs}` : ''}`, 'training-effectiveness',
  );
}

/** A suppressed-aware count: 1–4 officials are shown as "<5". */
export interface CountCell { value: number | null; suppressed: boolean; display: string }

export interface CapabilityRiskReport {
  asOf: string;
  capableLevel: number;
  horizonMonths: number;
  suppression: string;
  products: {
    productId: string; productName: string; teamSize: CountCell; risk: RiskBand;
    competencies: {
      competencyId: string; competencyName: string; teamSize: CountCell; capable: CountCell;
      retiringWithin36m: CountCell; singlePointOfFailure: boolean; risk: RiskBand; reason: string;
    }[];
  }[];
  dataNote: string;
}

export type RiskBand = 'critical' | 'high' | 'moderate' | 'low';

export interface ForesightReport {
  asOf: string;
  months: number[];
  capableLevel: number;
  annualAttrition: number;
  method: string;
  suppression: string;
  series: {
    productId: string; competencyId: string; competencyName: string; declining: boolean;
    withDecay: { month: number; expectedCapable: CountCell }[];
    attritionOnly: { month: number; expectedCapable: CountCell }[];
  }[];
  dataNote: string;
}

export interface TpacAgenda {
  items: {
    id: string; type: 'coverage_gap' | 'capability_risk' | 'ineffective_course' | 'prerequisite_review';
    priority: 'high' | 'medium' | 'low'; title: string; rationale: string; status: 'draft';
  }[];
  counts: Record<string, number>;
  note: string;
  dataNote: string;
}

/** SCIL v6 §11 — capability risk per statistical product (counts of 1–4 suppressed). */
export async function fetchCapabilityRisk(): Promise<CapabilityRiskReport> {
  return lmsFetch<CapabilityRiskReport>('/api/v1/admin/workforce/capability-risk', 'capability-risk');
}

/** SCIL v6 §11 — 36-month attrition × decay projection. */
export async function fetchForesight(): Promise<ForesightReport> {
  return lmsFetch<ForesightReport>('/api/v1/admin/workforce/foresight', 'foresight');
}

/** SCIL v6 §11 — draft TPAC agenda items. */
export async function fetchTpacAgenda(): Promise<TpacAgenda> {
  return lmsFetch<TpacAgenda>('/api/v1/admin/workforce/tpac-agenda', 'tpac-agenda');
}

/** SCIL v6 §5 — enforced expert prerequisite DAG + data-driven suggestions (never applied). */
export async function fetchPrerequisiteDag(): Promise<PrerequisiteDagReport> {
  return lmsFetch<PrerequisiteDagReport>('/api/v1/admin/prerequisites', 'prerequisites');
}

// ─────────────────────────────────────────────────────────────────────────────
// ADMIN CONSOLE — server-side KPIs, trends, actions (routers/admin_console.py)
// Every view takes the same filters: department, grade (service tier), office (officeId).
// ─────────────────────────────────────────────────────────────────────────────

export interface AdminFilters { department?: string; grade?: string; office?: string }

const CONSOLE = '/api/v1/admin/console';

function consoleQs(filters: AdminFilters = {}, extra: Record<string, string | number | undefined> = {}): string {
  const qs = new URLSearchParams();
  Object.entries({ ...filters, ...extra }).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') qs.set(k, String(v));
  });
  const s = qs.toString();
  return s ? `?${s}` : '';
}

export interface FacetOption { value: string; label: string; count: number }
export interface AdminFacets { departments: FacetOption[]; grades: FacetOption[]; offices: FacetOption[] }

export interface MandatoryProgress {
  cycle: string; total: number; completed: number;
  pending: { courseId: string; title: string; hours?: number }[];
}

export interface AdminRosterRow {
  userId: string; govId: string; firstName: string; lastName: string; email: string;
  designation: string; department: string; grade: string | null; gradeLabel: string;
  officeId: string | null; officeName: string; enrollmentStatus: number; statusLabel: string;
  missingSkill: string | null; missingCount: number; mandatory: MandatoryProgress | null;
}

export interface StatusCounts { compliant: number; inProgress: number; required: number }

export interface MandatorySummary {
  officialsWithPlan: number; behind: number; coursesAssigned: number; coursesCompleted: number;
  completionPct: number | null;
}

export interface AdminOverview {
  filters: AdminFilters;
  kpis: {
    totalOfficials: number; trainingCompliancePct: number; avgMissingSkills: number;
    mandatory: MandatorySummary; suppressed: boolean;
  };
  statusCounts: StatusCounts;
  heatmap: { competency: string; gap: number; officials: CountCell }[];
  deptCompliance: {
    dept: string; headcount: number; suppressed: boolean; pct: number | null;
    mandatoryPct: number | null; behindMandatory: CountCell;
  }[];
  needsTraining: AdminRosterRow[];
  asOf: string;
}

export interface Page<T> { items: T[]; total: number; page: number; pageSize: number; totalPages: number }

export interface TrendPoint {
  date: string; officials: number; suppressed?: boolean;
  /** true = rebuilt from dated iGOT completions (training rates only); false = stored daily snapshot */
  reconstructed?: boolean;
  compliancePct?: number | null; mandatoryCompletionPct?: number | null; behindMandatory?: number;
  avgMissingSkills?: number | null; avgLevel?: number | null; atTargetPct?: number | null;
  assessedPct?: number | null;
}

export interface TrendsReport {
  days: number; filters: AdminFilters; scope: { dimension: string; value: string } | null;
  points: TrendPoint[]; note: string;
  weeklyCompletions: { weekStart: string; completions: number | null }[];
  liveSnapshots: number; firstLiveSnapshot: string | null;
}

export interface CatalogueCourse { courseId: string; title: string; hours: number | null; competencies: string[] }

export interface TrainingAssignment {
  assignmentId: string; title: string; scope: 'department' | 'officials'; department: string | null;
  courses: { courseId: string; title: string; hours: number | null }[]; assignees: number;
  dueDate: string | null; note: string | null; createdBy: string; createdAt: string | null;
  progress: { completedAll: number; completedSome: number; completionPct: number }; overdue: boolean;
}

export interface AssignmentInput {
  title: string; scope: 'department' | 'officials'; department?: string; grade?: string; office?: string;
  userIds?: string[]; courseIds: string[]; dueDate?: string; note?: string;
}

export interface BehindRow {
  userId: string; govId: string; name: string; designation: string; department: string;
  grade: string | null; gradeLabel: string; officeName: string; completed: number; total: number;
  pending: { courseId: string; title: string; hours?: number }[]; lastNudgedAt: string | null;
}

export interface NudgeLogEntry {
  nudgeId: string; userId: string; name: string; department: string | null; message: string;
  pendingCourses: { courseId: string; title: string }[]; createdBy: string; createdAt: string; readAt: string | null;
}

export interface NudgeResult { sent: number; skipped: { userId: string; reason: string }[]; message: string }

export interface EmergingSkill {
  rank: number; competencyId: string; competencyName: string; required: CountCell; avgTargetLevel: number;
  supplyNow: CountCell; expectedSupplyNow: CountCell; expectedSupply36: CountCell; retiringCapable: CountCell;
  shortfallNow: CountCell; shortfall36: CountCell; coveragePct: number | null; coverage36Pct: number | null;
  rising: boolean; inScope: boolean; critical: boolean; missingCatalogueLevels: number[];
  flaggedCourses: number; priorityScore: number; recommendedAction: string; trainNextYear: boolean;
}

export interface EmergingSkillsReport {
  asOf: string; horizonMonths: number; officials: number; items: EmergingSkill[]; shortlist: string[];
  method: string; suppression: string; filters: AdminFilters; dataNote: string;
}

export type HealthStatus = 'ok' | 'degraded' | 'down' | 'unknown';
export interface SystemHealth {
  overall: 'ok' | 'degraded' | 'down'; checkedAt: string; lastDailySnapshot: string | null;
  health: { status: string; ready: boolean; recommendationEngine: boolean; chatSemantic: boolean; workforceSnapshot: string };
  components: { id: string; label: string; status: HealthStatus; detail: string; latencyMs?: number; model?: string }[];
}

export const fetchAdminFacets = () => lmsFetch<AdminFacets>(`${CONSOLE}/filters`, 'admin-filters');

export const fetchAdminOverview = (f: AdminFilters) =>
  lmsFetch<AdminOverview>(`${CONSOLE}/overview${consoleQs(f)}`, 'admin-overview');

export const fetchAdminRoster = (
  f: AdminFilters, page: number, pageSize: number, search: string, status?: number,
) => lmsFetch<Page<AdminRosterRow> & { statusCounts: StatusCounts }>(
  `${CONSOLE}/roster${consoleQs(f, { page, pageSize, search, status })}`, 'admin-roster-page');

export const fetchAdminTrends = (f: AdminFilters, days = 90) =>
  lmsFetch<TrendsReport>(`${CONSOLE}/trends${consoleQs(f, { days })}`, 'admin-trends');

export const recordAdminSnapshot = () =>
  lmsFetch<{ date: string }>(`${CONSOLE}/trends/snapshot`, 'admin-snapshot', { method: 'POST' });

export const searchCatalogueCourses = (q: string) =>
  lmsFetch<{ courses: CatalogueCourse[]; total: number }>(`${CONSOLE}/courses${consoleQs({}, { q })}`, 'course-search');

export const fetchAssignments = () =>
  lmsFetch<{ assignments: TrainingAssignment[] }>(`${CONSOLE}/assignments`, 'assignments');

export const createAssignment = (body: AssignmentInput) =>
  lmsFetch<TrainingAssignment>(`${CONSOLE}/assignments`, 'assign', { method: 'POST', body: JSON.stringify(body) });

export const fetchMandatoryBehind = (f: AdminFilters, page: number, pageSize: number, search = '') =>
  lmsFetch<Page<BehindRow> & { summary: MandatorySummary }>(
    `${CONSOLE}/mandatory-behind${consoleQs(f, { page, pageSize, search })}`, 'mandatory-behind');

export const sendNudges = (body: AdminFilters & { userIds?: string[]; message?: string; force?: boolean }) =>
  lmsFetch<NudgeResult>(`${CONSOLE}/nudges`, 'nudge', { method: 'POST', body: JSON.stringify(body) });

export const fetchNudgeLog = (limit = 20) =>
  lmsFetch<{ nudges: NudgeLogEntry[] }>(`${CONSOLE}/nudges?limit=${limit}`, 'nudge-log');

export const fetchEmergingSkills = (f: AdminFilters) =>
  lmsFetch<EmergingSkillsReport>(`${CONSOLE}/emerging-skills${consoleQs(f)}`, 'emerging-skills');

export const fetchSystemHealth = (probeGemini = false) =>
  lmsFetch<SystemHealth>(`${CONSOLE}/system-health${probeGemini ? '?probeGemini=true' : ''}`, 'system-health');

export type AdminExportKind = 'roster' | 'mandatory-behind' | 'emerging-skills' | 'trends' | 'departments' | 'shortages';

/** Download a server-built CSV (same filters as the view) through the authenticated client. */
export async function downloadAdminCsv(
  kind: AdminExportKind, f: AdminFilters, extra: Record<string, string | number | undefined> = {},
): Promise<void> {
  const path = `${CONSOLE}/export/${kind}.csv${consoleQs(f, extra)}`;
  const send = (token: string | null) => fetch(`${LMS_BASE_URL}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {}, credentials: 'include',
  });
  let res = await send(_accessToken);
  if (res.status === 401) {
    const { access_token } = await refresh();
    setApiToken(access_token);
    res = await send(access_token);
  }
  if (!res.ok) throw new Error(`[export-${kind}] HTTP ${res.status}`);
  const name = /filename="([^"]+)"/.exec(res.headers.get('content-disposition') ?? '')?.[1] ?? `${kind}.csv`;
  const url = URL.createObjectURL(await res.blob());
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}

// ─────────────────────────────────────────────────────────────────────────────
// KARMA POINTS API
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Daily check-in + full Karma summary. The backend syncs new iGOT completions,
 * awards the once-a-day check-in and streak milestones (idempotent per IST day)
 * and returns the summary with `recentAwards`. Returns null (never throws) so
 * the dashboard degrades gracefully if the karma service is unavailable.
 */
export async function fetchKarmaLedger(userId: string, limit = 20): Promise<KarmaLedger | null> {
  try {
    return await lmsFetch<KarmaLedger>(
      `/api/v1/learner/${userId}/karma/check-in?limit=${limit}`,
      'karma-ledger',
      { method: 'POST' },
    );
  } catch {
    return null;
  }
}

/** Passbook page (read-only; no check-in side effects). */
export async function fetchKarmaHistory(userId: string, limit = 20, offset = 0): Promise<KarmaLedger> {
  return lmsFetch<KarmaLedger>(
    `/api/v1/learner/${userId}/karma?limit=${limit}&offset=${offset}`,
    'karma-history',
  );
}

/** Earning rules, daily cap, streak milestones and levels — drives "How to earn". */
export async function fetchKarmaRules(): Promise<KarmaRules> {
  return lmsFetch<KarmaRules>('/api/v1/karma/rules', 'karma-rules');
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
): Promise<KarmaAward & { newBalance: number }> {
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
): Promise<KarmaAward & { newBalance: number }> {
  return lmsFetch(
    `/api/v1/learner/${userId}/karma/claim-cbp-bonus`,
    'karma-cbp-claim',
    {
      method: 'POST',
      body: JSON.stringify({ courseId }),
    },
  );
}