from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Enum, JSON
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
