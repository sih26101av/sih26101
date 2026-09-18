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

export type EvidenceConfidence = 'HIGH' | 'MEDIUM' | 'LOW' | 'UNASSESSED';

/** Which evidence set the displayed level (backend resolve_level). */
export type LevelBasis = 'evidence' | 'course_completion' | 'self_report' | 'none';

/** Catalogue FRAC competency that serves a role competency (backend crosswalk). */
export interface CompetencyCrosswalk {
  catalogueId: string;
  catalogueName: string;
  method: 'exact' | 'curated_crosswalk' | 'semantic_crosswalk';
  /** null for exact / curated mappings */
  similarity: number | null;
  /** curated mappings only: has a human confirmed it? */
  confirmed?: boolean;
}

/** SCIL v6 §4 — how much the official's office works in this competency's
 *  GSBPM sub-processes this cycle. Badge + ordinal study-plan tie-break only. */
export type OpportunityLevel = 'Low' | 'Medium' | 'High';

export interface PracticeOpportunity {
  level: OpportunityLevel;
  /** share of the office's officer-hours in the competency's sub-processes */
  share: number;
  officerHours: number;
  officeId: string;
  officeName: string;
  cycle: string;
  subprocesses: { id: string; name: string; officerHours: number }[];
}

export interface SkillGapEntry {
  competency: Competency;
  /** null at runtime when confidence is UNASSESSED */
  currentLevel: number;
  requiredLevel: number;
  /** null at runtime when confidence is UNASSESSED */
  gap: number;
  isMandatory: boolean;
  verificationSource: string;
  evaluatedAt: string;
  confidence?: EvidenceConfidence;
  basis?: LevelBasis;
  evidenceLevel?: number | null;
  crosswalk?: CompetencyCrosswalk | null;
  opportunity?: PracticeOpportunity | null;
  rawScore?: number;
  evidence?: {
    verified: number;
    documented: number;
    tenure: number;
    selfReport: number;
    education: number;
    seniority: number;
  };
}

export interface SkillGapReport {
  gaps: SkillGapEntry[];
}

// ── Learning pathway — GET /api/v1/learner/{id}/pathway ─────────────────────

export type PathwayStepKind = 'diagnostic' | 'bridge' | 'course' | 'continue' | 'stretch' | 'optional';

export interface PathwayCourse {
  courseId: string;
  title: string;
  provider: string;
  durationHours: number;
  /** FRAC level the course is tagged at for this competency */
  courseLevel: number | null;
  isTpac: boolean;
  tpacSource: string | null;
  finalScore: number | null;
  relevanceScore: number | null;
  qualityScore: number | null;
  /** false → course text doesn't support its FRAC tag; flagged for review */
  tagSupported: boolean | null;
  progressPercentage: number;
}

export interface PathwayStep {
  order: number;
  kind: PathwayStepKind;
  fromLevel: number;
  toLevel: number;
  /** FRAC levels this step closes (more than one on a stretch step) */
  covers: number[];
  /** FRAC proficiency descriptor for toLevel */
  levelDescriptor: string;
  course: PathwayCourse | null;
  hours: number | null;
  reason: string;
  alternatives: PathwayCourse[];
  action?: 'practice_assessment';
  /** the course is an APAR-linked mandatory ACBP course */
  mandatory?: boolean;
  /** cross-competency prerequisites this step depends on (SCIL v6 §5) */
  prerequisites?: StepPrerequisite[];
}

export interface StepPrerequisite {
  competencyId: string;
  competencyName: string;
  level: number;
  currentLevel: number | null;
  /** null → the official's level on it is unknown (advisory only) */
  met: boolean | null;
  rationale?: string;
  source: string;
}

export interface AppliedPrerequisite {
  edgeId: string | null;
  from: { competencyId: string; competencyName: string; level: number };
  to: { competencyId: string; competencyName: string; level: number };
  /** ordered: the rung waited, then ran after its prerequisite · blocked: never met in this plan · advisory: level unknown */
  status: 'ordered' | 'blocked' | 'advisory';
}

export interface LearningPathway {
  competencyId: string;
  catalogueCompetencyId: string;
  crosswalk: CompetencyCrosswalk | null;
  message: string | null;
  competencyName: string;
  currentLevel: number | null;
  startLevel: number;
  targetLevel: number;
  gap: number;
  priorityScore: number;
  confidence: EvidenceConfidence;
  basis: LevelBasis;
  evidenceLevel: number | null;
  status: 'ready' | 'partial' | 'no_content' | 'met';
  needsDiagnostic: boolean;
  steps: PathwayStep[];
  totalHours: number;
  bridgeHours: number;
  coverageGaps: number[];
  unreachableLevels: number[];
  tagReviewFlags: string[];
  opportunity?: PracticeOpportunity | null;
}

export interface MandatoryCourse {
  courseId: string;
  title: string;
  competencyId: string;
  level: number;
  hours: number;
  aparLinked: boolean;
  reason: string;
  status: 'scheduled' | 'in_progress' | 'completed';
}

export interface StudyPlanStep {
  order: number;
  courseId: string;
  title: string;
  provider: string;
  isTpac: boolean;
  kind: PathwayStepKind | 'mandatory';
  mandatory?: boolean;
  modality?: 'self_paced' | 'virtual_lab' | 'classroom' | null;
  reason?: string;
  hours: number;
  cumulativeHours: number;
  advances: {
    competencyId: string;
    competencyName: string;
    fromLevel: number;
    toLevel: number;
    covers: number[];
  }[];
  opportunity?: OpportunityLevel | null;
  /** 'opportunity_tie_break' → a near-tie on level-per-hour went to the practisable gap */
  selectedBy?: 'gain_per_hour' | 'opportunity_tie_break' | 'mandatory_acbp';
}

export interface StudyPlan {
  budgetHours: number | null;
  totalHours: number;
  /** quarterly_hours → this quarter's plan from the ACBP; query → ?budgetHours; none → unbudgeted */
  budgetSource?: 'quarterly_hours' | 'query' | 'none';
  learningHoursPerQuarter?: number | null;
  acbpCycle?: string | null;
  overBudget?: boolean;
  classroomCapHours?: number | null;
  classroomHours?: number;
  mandatory?: MandatoryCourse[];
  prerequisitesApplied?: AppliedPrerequisite[];
  diagnostics: { competencyId: string; competencyName: string; reason: string }[];
  steps: StudyPlanStep[];
  deferred: {
    competencyId: string;
    competencyName: string;
    remainingSteps: number;
    remainingHours: number;
    reason: string;
  }[];
  method: string;
}

export interface LearningPathwayResponse {
  pathways: LearningPathway[];
  studyPlan: StudyPlan;
}

export interface CourseRecommendation {
  course: Course;
  /** Backward-compat alias for finalScore — used by MatchScoreBar */
  matchScore: number;
  /** 0.6*relevanceScore + 0.4*qualityScore ∈ [0,1] */
  finalScore: number;
  /** RRF score normalised to [0,1] */
  relevanceScore: number;
  /** 0.35*completion + 0.35*wilsonRating + 0.20*logPop + 0.10*tpac ∈ [0,1] */
  qualityScore: number;
  /** True if course is NSSTA/TPAC-vetted */
  isTpac: boolean;
  bridgesGapFor: Competency;
  /** First element of matchReasons (legacy) */
  aiMatchTag: string;
  /** Human-readable chips explaining the recommendation */
  matchReasons: string[];
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