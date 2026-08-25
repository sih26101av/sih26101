from pydantic import BaseModel
from typing import List

class SkillGap(BaseModel):
    competencyId: str
    skillName: str
    domain: str
    currentLevel: int
    targetLevel: int
    gapScore: int

class SkillGapResponse(BaseModel):
    officialId: str
    jobRole: str
    department: str
    skillGaps: List[SkillGap]

class Recommendation(BaseModel):
    courseId: str
    title: str
    provider: str
    durationHours: float
    matchReason: str
    tags: List[str]

class RecommendationResponse(BaseModel):
    status: str
    recommendations: List[Recommendation]

class Enrollment(BaseModel):
    enrollmentId: str
    courseId: str
    courseTitle: str
    provider: str
    durationHours: float
    progressPercentage: int
    remainingHours: float
    lastAccessed: str
    status: str

class EnrollmentsResponse(BaseModel):
    status: str
    enrollments: List[Enrollment]

class Achievement(BaseModel):
    id: str
    title: str
    score: int
    date: str
    category: str  # "RAG Quiz" | "External Certification"

class AchievementsResponse(BaseModel):
    status: str
    achievements: List[Achievement]