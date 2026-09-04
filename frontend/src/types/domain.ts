/**
 * FILE: src/types/domain.ts
 * SOURCE OF TRUTH: mospi-competency-platform.mermaid
 * All interfaces map 1-to-1 with the Mermaid UML diagram.
 */

export type UserRole = 'OFFICIAL' | 'ADMIN' | 'TRAINER';
export type CompetencyDomain = 'Statistical' | 'Technical' | 'Governance' | 'Leadership';

export interface BaseUser {
  uuid: string;
  email: string;
  role: UserRole;
}

export interface Competency {
  compId: string;
  domain: CompetencyDomain;
  skillName: string;
}

export interface RoleRequirement {
  requirementId: string;
  requiredLevel: number;
  isMandatory: boolean;
  validityMonths: number;
  competency: Competency;
}

export interface JobRole {
  roleId: string;
  title: string;
  department: string;
  roleRequirements: RoleRequirement[];
}

export interface UserCompetency {
  currentLevel: number;
  verificationSource: string;
  evaluatedAt: string;
  competency: Competency;
}

export interface CompetencyProfile {
  profileId: string;
  lastEvaluatedDate: string;
  userCompetencies: UserCompetency[];
}

export interface Official extends BaseUser {
  govId: string;
  department: string;
  experienceYears: number;
  fullName: string;
  jobRole: JobRole;
  competencyProfile: CompetencyProfile;
}

export interface Course {
  courseId: string;
  title: string;
  source: string;
  durationHours: number;
  embeddingModelVersion?: string;
  thumbnailUrl?: string;
}

export interface SkillGapEntry {
  competency: Competency;
  currentLevel: number;
  requiredLevel: number;
  gap: number;
  isMandatory: boolean;
  verificationSource: string;
  evaluatedAt: string;
}

export interface SkillGapReport {
  gaps: SkillGapEntry[];
}

export interface CourseRecommendation {
  course: Course;
  matchScore: number;
  bridgesGapFor: Competency;
  aiMatchTag: string;
  priorityRank: number;
}

// Enrollment - maps to the /api/v1/users/{id}/enrollments response
export interface Enrollment {
  enrollmentId: string;
  course: Course;
  progressPercentage: number;
  remainingHours: number;
  lastAccessed: string;
  status: string;
}

// Achievement - maps to the /api/v1/users/{id}/achievements response
export interface Achievement {
  id: string;
  title: string;
  score: number;
  date: string;
  category: 'RAG Quiz' | 'External Certification';
}

// ─── Karma Points — iGOT Karmayogi gamification layer ────────────────────────

export type KarmaEventType =
  | 'SELF_REGISTRATION'
  | 'FIRST_ENROLLMENT'
  | 'COURSE_COMPLETION'
  | 'ASSESSMENT_PASSED'
  | 'COURSE_RATED'
  | 'CBP_BONUS';

export interface KarmaTransaction {
  eventId: string;
  eventType: KarmaEventType;
  pointsAwarded: number;
  courseId: string | null;
  isCbp: boolean;
  createdAt: string;
}

export interface KarmaMonthlyUsage {
  used: number;
  cap: number;
  remaining: number;
}

/** Per-event-type totals (e.g. { COURSE_COMPLETION: 25, ASSESSMENT_PASSED: 10 }) */
export type KarmaBreakdown = Partial<Record<KarmaEventType, number>>;

export interface KarmaLedger {
  userId: string;
  totalPoints: number;
  streak: number;
  monthlyUsage: KarmaMonthlyUsage;
  breakdown: KarmaBreakdown;
  ledger: KarmaTransaction[];
}

// ─────────────────────────────────────────────────────────────────────────────

export interface UseLearnerDashboardResult {
  profile: Official | null;
  skillGaps: SkillGapEntry[];
  recommendations: CourseRecommendation[];
  enrollments: Enrollment[];
  achievements: Achievement[];
  karma: KarmaLedger | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}