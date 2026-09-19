from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Enum, JSON, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
import uuid
import enum
from datetime import datetime

Base = declarative_base()

class UserRole(enum.Enum):
    ADMIN = "admin"
    TRAINER = "trainer"
    OFFICIAL = "official"

class BaseUser(Base):
    __tablename__ = "users"
    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    passwordHash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    
    # Polymorphic setup
    type = Column(String)
    __mapper_args__ = {
        'polymorphic_identity': 'baseuser',
        'polymorphic_on': type
    }

class JobRole(Base):
    __tablename__ = "job_roles"
    roleId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    department = Column(String, nullable=False)

    requirements = relationship("RoleRequirement", back_populates="job_role", cascade="all, delete-orphan")

class CompetencyProfile(Base):
    __tablename__ = "competency_profiles"
    profileId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    lastEvaluatedDate = Column(DateTime, nullable=True)
    current_level = Column(Integer, nullable=True, default=1)
    skill_name = Column(String, nullable=True, default="National Accounts")
    target_level = Column(Integer, nullable=True, default=4)

    user_competencies = relationship("UserCompetency", back_populates="profile", cascade="all, delete-orphan")
    official = relationship("Official", back_populates="competency_profile", uselist=False)

class Official(BaseUser):
    __tablename__ = "officials"
    uuid = Column(String, ForeignKey("users.uuid"), primary_key=True)
    govId = Column(String, unique=True, nullable=False)
    department = Column(String, nullable=False)
    experienceYears = Column(Integer, nullable=False, default=0)
    
    jobRoleId = Column(String, ForeignKey("job_roles.roleId"), nullable=True)
    competencyProfileId = Column(String, ForeignKey("competency_profiles.profileId"), nullable=True, unique=True)
    
    jobRole = relationship("JobRole")
    competency_profile = relationship("CompetencyProfile", back_populates="official", uselist=False)

    __mapper_args__ = {
        'polymorphic_identity': 'official',
    }

class Admin(BaseUser):
    __tablename__ = "admins"
    uuid = Column(String, ForeignKey("users.uuid"), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

class Trainer(BaseUser):
    __tablename__ = "trainers"
    uuid = Column(String, ForeignKey("users.uuid"), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity': 'trainer',
    }

class Competency(Base):
    __tablename__ = "competencies"
    compId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    domain = Column(String, nullable=False)
    skillName = Column(String, nullable=False)

class RoleRequirement(Base):
    __tablename__ = "role_requirements"
    requirementId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    requiredLevel = Column(Integer, nullable=False)
    isMandatory = Column(Boolean, default=True)
    validityMonths = Column(Integer, nullable=True)
    
    jobRoleId = Column(String, ForeignKey("job_roles.roleId"))
    compId = Column(String, ForeignKey("competencies.compId"))

    job_role = relationship("JobRole", back_populates="requirements")
    competency = relationship("Competency")

class UserCompetency(Base):
    __tablename__ = "user_competencies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    currentLevel = Column(Integer, nullable=False)
    verificationSource = Column(String, nullable=False)
    evaluatedAt = Column(DateTime, default=datetime.utcnow)
    
    profileId = Column(String, ForeignKey("competency_profiles.profileId"))
    compId = Column(String, ForeignKey("competencies.compId"))

    profile = relationship("CompetencyProfile", back_populates="user_competencies")
    competency = relationship("Competency")

class Course(Base):
    __tablename__ = "courses"
    courseId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String, nullable=False)
    syllabusVectorEmbedding = Column(String) # Handled as String for simplicity; pgvector/numpy integration possible later
    embeddingModelVersion = Column(String, nullable=True)

    skill_mappings = relationship("CourseSkillMapping", back_populates="course", cascade="all, delete-orphan")

class CourseSkillMapping(Base):
    __tablename__ = "course_skill_mappings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    proficiencyLevelTaught = Column(Integer, nullable=False)
    
    courseId = Column(String, ForeignKey("courses.courseId"))
    compId = Column(String, ForeignKey("competencies.compId"))

    course = relationship("Course", back_populates="skill_mappings")
    competency = relationship("Competency")

class Assessment(Base):
    __tablename__ = "assessments"
    assessmentId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    passingScore = Column(Float, nullable=False)
    sourceDocumentId = Column(String, nullable=True)

    skill_mappings = relationship("AssessmentSkillMapping", back_populates="assessment", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="assessment", cascade="all, delete-orphan")

class AssessmentSkillMapping(Base):
    __tablename__ = "assessment_skill_mappings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    weightage = Column(Float, nullable=False)
    
    assessmentId = Column(String, ForeignKey("assessments.assessmentId"))
    compId = Column(String, ForeignKey("competencies.compId"))

    assessment = relationship("Assessment", back_populates="skill_mappings")
    competency = relationship("Competency")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String, nullable=False)
    options = Column(JSON, nullable=False) # List of Strings
    correctOptionId = Column(String, nullable=False)
    aiExplanation = Column(String, nullable=True)

    assessmentId = Column(String, ForeignKey("assessments.assessmentId"))
    compId = Column(String, ForeignKey("competencies.compId"), nullable=True)

    assessment = relationship("Assessment", back_populates="questions")
    competency = relationship("Competency")

class OutboxEntry(Base):
    __tablename__ = "outbox_entries"
    eventId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    payload = Column(String, nullable=False) # JSON string
    status = Column(String, nullable=False, default="PENDING")
    retryCount = Column(Integer, nullable=False, default=0)



# ─────────────────────────────────────────────────────────────────────────────
# EVIDENCE LOG — canonical evidence store for all competency evidence channels
# ─────────────────────────────────────────────────────────────────────────────
# evidenceType values:
#   'VERIFIED_IGOT'       — iGOT/NSSTA enrollment completion, FRAC-tag-matched
#   'DOCUMENTED_CERT'     — uploaded certificate awaiting admin review (grantedValue = cert level 1-5)
#   'VERIFIED_CERT'       — the same row after an admin approved the certificate;
#                           read by the VERIFIED channel (see CertificateSubmission)
#   'TENURE'              — career history evidence
#   'SELF_REPORT'         — user-declared level (0.6x reliability discount applied)
#   'PRACTICE_ASSESSMENT' — RAG quiz pass; keyed by iGOT userId, feeds into the
#                           documented channel of CompetencyCalculator.

class EvidenceLog(Base):
    __tablename__ = "evidence_log"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # FIX (Bug #9): userId stores the iGOT userId string (e.g. "usr_720465595"),
    # NOT a FK to users.uuid (which is an internal UUID unrelated to iGOT IDs).
    # BaselineAssembler.compute_for_user queries this table by iGOT userId.
    # Removing the FK prevents constraint violations when evidence is written for
    # iGOT users that do not yet have a row in the internal auth.db users table.
    userId = Column(String, nullable=False, index=True)  # iGOT userId — canonical identity

    compId = Column(String, ForeignKey("competencies.compId"), nullable=False, index=True)

    # 'VERIFIED_IGOT', 'DOCUMENTED_CERT', 'VERIFIED_CERT', 'TENURE', 'SELF_REPORT', 'PRACTICE_ASSESSMENT'
    evidenceType = Column(String, nullable=False)

    grantedValue = Column(Float, nullable=False)  # 1.0 to 5.0
    issueDate = Column(DateTime, nullable=True)   # Drives recency decay multiplier

    # Stores LLM reasoning, issuing organization, or iGOT course IDs
    metadata_payload = Column(JSON, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow)

    competency = relationship("Competency")


# ─────────────────────────────────────────────────────────────────────────────
# CERTIFICATE SUBMISSION — external certificate awaiting / after admin review
# ─────────────────────────────────────────────────────────────────────────────

class CertificateSubmission(Base):
    """
    One uploaded certificate (routers/competency.py). On upload each extracted
    competency gets a DOCUMENTED_CERT EvidenceLog row (MEDIUM confidence) whose
    id is kept in `evidenceIds`. An admin then decides:
      approve → status VERIFIED, rows become VERIFIED_CERT (verified channel, HIGH)
      reject  → status REJECTED, rows are deleted (the gap goes back)
    (userId, sha256) is unique, so re-uploading the same file is a no-op.
    """
    __tablename__ = "certificate_submissions"
    __table_args__ = (UniqueConstraint("userId", "sha256", name="uq_user_certificate"),)

    id                  = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    userId              = Column(String, nullable=False, index=True)   # iGOT userId
    filename            = Column(String, nullable=False)
    sha256              = Column(String, nullable=False)
    issuingOrganization = Column(String, nullable=True)
    extractor           = Column(String, nullable=False)               # 'gemini' | 'ocr+e5'
    extraction          = Column(JSON, nullable=False)                 # CertificateExtractionResult
    evidenceIds         = Column(JSON, nullable=False, default=list)
    status              = Column(String, nullable=False, default="PENDING", index=True)
    reviewedBy          = Column(String, nullable=True)
    reviewNote          = Column(String, nullable=True)
    createdAt           = Column(DateTime, default=datetime.utcnow)
    reviewedAt          = Column(DateTime, nullable=True)


# ─────────────────────────────────────────────────────────────────────────────
# QUIZ ATTEMPT — idempotency table for RAG quiz grading (Bug #10)
# ─────────────────────────────────────────────────────────────────────────────

class QuizAttempt(Base):
    """
    Persists every MCQ-quiz submission BEFORE evidence is written.
    UniqueConstraint on (userId, quizId) makes grading idempotent:
      - First submission  → writes EvidenceLog row, sets evidenceWritten=True
      - Later submissions → re-scored for UX, NO second EvidenceLog row written
    userId here is the iGOT userId string from current_user.username (JWT auth).
    """
    __tablename__ = "quiz_attempts"
    __table_args__ = (UniqueConstraint("userId", "quizId", name="uq_user_quiz_attempt"),)

    attemptId       = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    userId          = Column(String, nullable=False, index=True)  # iGOT userId
    quizId          = Column(String, nullable=False, index=True)
    compId          = Column(String, nullable=True)   # competency targeted by this quiz
    answers         = Column(JSON, nullable=False)
    score           = Column(Float, nullable=False)   # 0–100
    passed          = Column(Boolean, nullable=False)
    evidenceWritten = Column(Boolean, default=False)  # True once EvidenceLog row created
    gradedAt        = Column(DateTime, default=datetime.utcnow)


class QuizItemStat(Base):
    """
    Response data per quiz item (services/doc_quiz/calibration.py). itemKey is a hash
    of the item's content (doc_quiz.items.item_key), so the counts survive new quiz ids
    and restarts. Only first submissions are counted: a re-submission after seeing the
    answers would bias the p-value. thetaSum (respondents' practice ability before the
    quiz) lets the calibration separate item difficulty from who happened to answer.
    """
    __tablename__ = "quiz_item_stats"

    itemKey         = Column(String, primary_key=True)
    questionType    = Column(String, nullable=True)
    llmDifficulty   = Column(String, nullable=True)
    responses       = Column(Integer, nullable=False, default=0)
    correctCount    = Column(Integer, nullable=False, default=0)
    thetaSum        = Column(Float, nullable=False, default=0.0)
    sampleQuestion  = Column(String, nullable=True)
    firstSeen       = Column(DateTime, default=datetime.utcnow)
    lastSeen        = Column(DateTime, default=datetime.utcnow)



# ─────────────────────────────────────────────────────────────────────────────
# KARMA / GAMIFICATION MODELS — iGOT Karmayogi Points Layer
# Supports the Observer pattern: AssessmentPassedEvent → KarmaEngine → KarmaEvent
# ─────────────────────────────────────────────────────────────────────────────

class KarmaEventType(enum.Enum):
    SELF_REGISTRATION = "SELF_REGISTRATION"
    FIRST_ENROLLMENT  = "FIRST_ENROLLMENT"
    COURSE_COMPLETION = "COURSE_COMPLETION"
    ASSESSMENT_PASSED = "ASSESSMENT_PASSED"
    COURSE_RATED      = "COURSE_RATED"
    CBP_BONUS         = "CBP_BONUS"
    # Added with the daily-cap / streak rework (migrated by karma_engine.migrate_karma_schema)
    DAILY_LOGIN          = "DAILY_LOGIN"
    STREAK_BONUS         = "STREAK_BONUS"
    DIAGNOSTIC_COMPLETED = "DIAGNOSTIC_COMPLETED"
    ADMIN_ADJUSTMENT     = "ADMIN_ADJUSTMENT"


class KarmaEvent(Base):
    """Immutable ledger entry — one row per karma point award event."""
    __tablename__ = "karma_events"

    eventId       = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    userId        = Column(String, nullable=False, index=True)  # iGOT userId (no FK — see EvidenceLog)
    eventType     = Column(Enum(KarmaEventType), nullable=False)
    pointsAwarded = Column(Integer, nullable=False, default=0)
    courseId      = Column(String, nullable=True)   # optional course reference
    isCbp         = Column(Boolean, default=False)  # True if CBP-mandated course
    createdAt     = Column(DateTime, default=datetime.utcnow)
    # Idempotency key (quizId, courseId, IST date, "once", ...). Unique per
    # (userId, eventType) when not NULL — partial index made by migrate_karma_schema.
    referenceId   = Column(String, nullable=True)
    note          = Column(String, nullable=True)   # passbook text, e.g. "Daily cap reached"


class KarmaMonthlyUsage(Base):
    """
    Rolling monthly counter for non-CBP COURSE_COMPLETION events.
    Enforces the 4-completions-per-calendar-month cap.
    """
    __tablename__ = "karma_monthly_usage"

    id                = Column(Integer, primary_key=True, autoincrement=True)
    userId            = Column(String, nullable=False, index=True)  # iGOT userId (no FK — see EvidenceLog)
    year              = Column(Integer, nullable=False)
    month             = Column(Integer, nullable=False)   # 1–12
    nonCbpCompletions = Column(Integer, nullable=False, default=0)


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN CONSOLE — daily workforce snapshots, training assignments, nudges
# (routers/admin_console.py). Created by main._create_schema like the tables above.
# ─────────────────────────────────────────────────────────────────────────────

class AdminDailySnapshot(Base):
    """
    One row per calendar day (UTC): the workforce headline numbers plus the same
    numbers broken down by department / grade / office, so trend charts can be
    filtered. Upserted by admin_console.record_daily_snapshot — history starts
    the day the feature is deployed; nothing is back-filled.
    """
    __tablename__ = "admin_daily_snapshots"

    snapshotDate = Column(String, primary_key=True)          # YYYY-MM-DD
    metrics      = Column(JSON, nullable=False)              # {overall{…}, byDepartment{}, byGrade{}, byOffice{}}
    createdAt    = Column(DateTime, default=datetime.utcnow)


class TrainingAssignment(Base):
    """An admin assigning courses (a training plan) to a department or a list of officials."""
    __tablename__ = "training_assignments"

    assignmentId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title        = Column(String, nullable=False)            # plan name
    scope        = Column(String, nullable=False)            # "department" | "officials"
    department   = Column(String, nullable=True)
    courses      = Column(JSON, nullable=False)              # [{courseId, title, hours}]
    assigneeIds  = Column(JSON, nullable=False)              # iGOT userIds resolved at creation
    dueDate      = Column(String, nullable=True)             # YYYY-MM-DD
    note         = Column(String, nullable=True)
    createdBy    = Column(String, nullable=False)            # admin username
    createdAt    = Column(DateTime, default=datetime.utcnow)


class TrainingNudge(Base):
    """A reminder sent by an admin to an official behind on mandatory (ACBP) training."""
    __tablename__ = "training_nudges"

    nudgeId      = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    userId       = Column(String, nullable=False, index=True)  # iGOT userId
    message      = Column(String, nullable=False)
    pendingCourses = Column(JSON, nullable=True)            # [{courseId, title}] at send time
    createdBy    = Column(String, nullable=False)
    createdAt    = Column(DateTime, default=datetime.utcnow, index=True)
    readAt       = Column(DateTime, nullable=True)


# ─────────────────────────────────────────────────────────────────────────────
# RECOMMENDATION FEEDBACK — clicks, enrolments, thumbs up/down (logged per event)
# ─────────────────────────────────────────────────────────────────────────────

class RecommendationFeedback(Base):
    """
    One learner interaction with a recommended course. `event` ∈ impression |
    click | enrol | thumbs_up | thumbs_down | clear_vote. The rank / score /
    competency at the time are kept so ranking changes can later be evaluated
    offline (click-through by rank, bandit logging). userId = iGOT userId.
    """
    __tablename__ = "recommendation_feedback"
    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    userId       = Column(String, nullable=False, index=True)
    courseId     = Column(String, nullable=False, index=True)
    competencyId = Column(String, nullable=True)
    event        = Column(String, nullable=False)
    rank         = Column(Integer, nullable=True)
    finalScore   = Column(Float, nullable=True)
    context      = Column(JSON, nullable=True)       # {mandatory, courseLevel, surface, …}
    createdAt    = Column(DateTime, default=datetime.utcnow, index=True)


# ─────────────────────────────────────────────────────────────────────────────
# LEVEL DISPUTE — a learner disagrees with a computed level → adaptive level test
# ─────────────────────────────────────────────────────────────────────────────

class LevelDispute(Base):
    """
    status: OPEN (test started) → CONFIRMED | RAISED | LOWER_THAN_SHOWN once the
    adaptive diagnostic finishes, or NEEDS_REVIEW when no test items exist.
    The diagnostic writes the usual PRACTICE_ASSESSMENT evidence row; this table
    only records the disagreement and its outcome.
    """
    __tablename__ = "level_disputes"
    id            = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    userId        = Column(String, nullable=False, index=True)
    competencyId  = Column(String, nullable=False)
    shownLevel    = Column(Integer, nullable=True)
    claimedLevel  = Column(Integer, nullable=True)
    reason        = Column(String, nullable=True)
    status        = Column(String, nullable=False, default="OPEN")
    sessionId     = Column(String, nullable=True, index=True)
    testedLevel   = Column(Integer, nullable=True)
    createdAt     = Column(DateTime, default=datetime.utcnow)
    resolvedAt    = Column(DateTime, nullable=True)
