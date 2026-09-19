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
export type LevelBasis =
  'evidence' | 'course_completion' | 'work_sample' | 'applied_at_work' | 'self_report' | 'none';

/** SCIL v6 §3 channels: K knowledge · A application (work sample) · U utility (confirmed use) · S supervisor */
export type EvidenceChannel = 'K' | 'A' | 'U' | 'S';

export interface EvidenceCompleteness {
  present: EvidenceChannel[];
  missing: EvidenceChannel[];
  weights: Record<EvidenceChannel, number>;
  /** "equal placeholder — pending expert AHP elicitation" */
  weightsStatus: string;
}

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
    workSample?: number;
    utility?: number;
    supervisor?: number;
  };
  /** K/A/U/S channel values on the 0–5 scale; null = no evidence in that channel */
  channels?: Record<EvidenceChannel, number | null> | null;
  evidenceCompleteness?: EvidenceCompleteness | null;
  /** number of peer ratings on record — shown for context, never scored */
  peerFeedback?: number;
  /** SCIL v6 §2 belief θ ~ N(μ, σ²) with dated decay (assessed competencies) */
  proficiency?: ProficiencyState | null;
  /** SCIL v6 §2 cold start for UNASSESSED: cohort prior "inferred from role" */
  coldStartPrior?: ColdStartPrior | null;
  /** "Why this level" — what set the level, the floors and channels behind it */
  whyThisLevel?: LevelExplanation | null;
}

export type LevelFactorRole = 'sets_level' | 'floor' | 'contributes' | 'context' | 'absent';

export interface LevelExplanation {
  summary: string;
  basis: LevelBasis;
  factors: { key: string; label: string; value: number; detail: string; role: LevelFactorRole }[];
  caps: string[];
}

export interface ProficiencyState {
  mu: number;
  sigma: number;
  decayedMu: number;
  decayedSigma: number;
  band80: [number, number];
  evidenceAgeMonths: number | null;
  decayClass: 'accuracy' | 'procedural';
  halfLifeMonths: number;
  retention: number;
  populationMu: number;
  /** E[max(0, target − θ)] — expected levels still missing */
  expectedShortfall: number;
  refresherRecommended: boolean;
}

export interface ColdStartPrior {
  label: string;
  mu: number;
  sigma: number;
  band80: [number, number];
  cluster: string;
  source: 'cohort' | 'population';
  pooled: boolean;
  /** null when the cohort is smaller than 5 (suppressed) */
  cohortN: number | null;
  divergence: number | null;
  reason: string;
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
  /** SCIL v6 §6 measured uplift (FRAC levels) from outcome data; upliftFlag → ≈ 0, review */
  measuredUplift?: number | null;
  upliftFlag?: boolean | null;
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
  competencyId?: string;
  courseLevel?: number | null;
  tpacSource?: 'verified' | 'inferred' | 'none';
  measuredUplift?: number | null;
  /** self_paced | virtual_lab | classroom */
  modality?: string | null;
  /** In the official's Annual Capacity Building Plan — always listed first */
  mandatory?: boolean;
  why?: RecommendationWhy | null;
}

export interface RecommendationWhy {
  gap: { competencyId: string; competencyName: string; currentLevel: number; targetLevel: number; gap: number } | null;
  levelStep: { from: number | null; to: number | null; kind: 'next_step' | 'on_the_way' | 'stretch' | 'untagged_level' | 'mandatory' };
  badges: { key: 'mandatory' | 'tpac_verified' | 'tpac_inferred' | 'measured_improvement' | 'under_review'; label: string; value?: number }[];
  summary: string;
}

export type FeedbackEvent = 'impression' | 'click' | 'enrol' | 'thumbs_up' | 'thumbs_down' | 'clear_vote';

// ── Career readiness (/learner/{id}/career-readiness) ────────────────────────
export interface CareerCompetency {
  competencyId: string;
  competencyName: string;
  requiredLevel: number;
  currentLevel: number | null;
  gap: number | null;
  confidence: EvidenceConfidence;
  basis: LevelBasis;
  inCurrentRole: boolean;
}

export interface CareerRoleOption {
  roleId: string;
  designation: string;
  tier: string;
  readinessPct: number;
  metCount: number;
  gapCount: number;
  unassessedCount: number;
  competencies: CareerCompetency[];
}

export interface CareerReadiness {
  currentRole: { roleId: string; designation: string; tier: string; officeId: string; readinessPct: number };
  nextRole: CareerRoleOption | null;
  alternatives: CareerRoleOption[];
  atTopOfLadder: boolean;
  milestones: { roleId: string; designation: string; tier: string; status: 'current' | 'next' | 'future' }[];
  method: string;
}

// ── Adaptive level check (routers/diagnostic.py) + level disputes ────────────
export interface DiagnosticItem {
  itemId: string;
  stem: string;
  options: string[];
  bloom: string;
  level: number;
}

export interface DiagnosticView {
  sessionId: string;
  competencyId: string;
  competencyName: string;
  answered: number;
  maxItems: number;
  posterior: { mu: number; sigma: number };
  done: boolean;
  calibration: string;
  item?: DiagnosticItem;
  dispute?: { disputeId: string; status: DisputeStatus; shownLevel: number | null; claimedLevel: number | null; testedLevel: number };
}

export type DisputeStatus = 'OPEN' | 'CONFIRMED' | 'RAISED' | 'LOWER_THAN_SHOWN' | 'NEEDS_REVIEW';

export interface LevelDispute {
  disputeId: string;
  competencyId: string;
  shownLevel: number | null;
  claimedLevel: number | null;
  status: DisputeStatus;
  testedLevel: number | null;
  sessionId: string | null;
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
  | 'CBP_BONUS'
  | 'DAILY_LOGIN'
  | 'STREAK_BONUS'
  | 'DIAGNOSTIC_COMPLETED'
  | 'ADMIN_ADJUSTMENT';

export interface KarmaTransaction {
  eventId: string;
  eventType: KarmaEventType;
  /** 0 when an action was blocked by a limit (see `note`); negative for admin deductions */
  pointsAwarded: number;
  courseId: string | null;
  isCbp: boolean;
  referenceId: string | null;
  note: string | null;
  createdAt: string;
}

export interface KarmaMonthlyUsage {
  used: number;
  cap: number;
  remaining: number;
}

/** Per-event-type totals (e.g. { COURSE_COMPLETION: 25, ASSESSMENT_PASSED: 10 }) */
export type KarmaBreakdown = Partial<Record<KarmaEventType, number>>;

export interface KarmaLevel {
  rank: number;
  name: string;
  minPoints: number;
  nextName: string | null;
  nextMinPoints: number | null;
  pointsToNext: number;
  progressPct: number;
}

export interface KarmaToday {
  /** Points from daily-capped activities earned today (IST) */
  earned: number;
  totalEarned: number;
  cap: number;
  remaining: number;
  checkedIn: boolean;
  resetsAt: string;
}

export interface KarmaAward {
  eventType: KarmaEventType | null;
  pointsAwarded: number;
  capReached: boolean;
  alreadyClaimed: boolean;
  dailyCapReached: boolean;
  dailyLimitReached: boolean;
  reason: string | null;
}

export interface KarmaLedger {
  userId: string;
  totalPoints: number;
  level: KarmaLevel;
  today: KarmaToday;
  streak: number;
  longestStreak: number;
  rank: { position: number; totalLearners: number; topPercent: number };
  monthlyUsage: KarmaMonthlyUsage;
  breakdown: KarmaBreakdown;
  totalEvents: number;
  ledger: KarmaTransaction[];
  /** Awards made by the check-in that produced this summary (e.g. +1 daily check-in) */
  recentAwards: KarmaAward[];
}

export interface KarmaRule {
  eventType: KarmaEventType;
  points: number;
  title: string;
  how: string;
  frequency: string;
  category: 'engagement' | 'learning' | 'milestone' | 'admin';
  perDay: number | null;
  dailyCapped: boolean;
}

export interface KarmaRules {
  dailyCap: number;
  monthlyCompletionCap: number;
  streakMilestones: { days: number; points: number }[];
  levels: { name: string; minPoints: number }[];
  rules: KarmaRule[];
  timezone: string;
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