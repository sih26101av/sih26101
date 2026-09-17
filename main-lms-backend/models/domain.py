from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# ─────────────────────────────────────────────────────────────────────────────
# CONFIDENCE TIER
# UNASSESSED: all six evidence channels are zero — no fabricated level returned
# LOW:        only Tenure / Education / SelfReport / Seniority fired
# MEDIUM:     Documented certificate evidence present
# HIGH:       Verified iGOT / NSSTA enrollment completion present
# ─────────────────────────────────────────────────────────────────────────────
Confidence = Literal["UNASSESSED", "LOW", "MEDIUM", "HIGH"]


class EvidenceBreakdown(BaseModel):
    """Per-channel evidence values after decay/discount, as used in the fusion formula."""
    verified:    float = 0.0
    documented:  float = 0.0
    tenure:      float = 0.0
    selfReport:  float = 0.0
    education:   float = 0.0
    seniority:   float = 0.0


class SkillGap(BaseModel):
    competencyId: str
    skillName:    str
    domain:       str
    # FIX (Bug #1): None when confidence == "UNASSESSED" — never fabricated
    currentLevel: Optional[int] = None
    targetLevel:  int
    # FIX (Bug #1): None when UNASSESSED — not conflated with "no gap"
    gapScore:     Optional[int] = None
    confidence:   Confidence = "LOW"
    rawScore:     float = 0.0
    evidence:     EvidenceBreakdown = Field(default_factory=EvidenceBreakdown)


class SkillGapResponse(BaseModel):
    userId:           str
    govId:            Optional[str] = None
    jobRole:          Optional[str] = None
    department:       Optional[str] = None
    totalCourses:     int = 0
    completedCourses: int = 0
    skillGaps:        List[SkillGap]


class Recommendation(BaseModel):
    courseId:       str
    title:          str
    provider:       str
    durationHours:  float
    matchReason:    str
    tags:           List[str]
    # Extended fields for scored recommendations
    finalScore:     Optional[float] = None
    relevanceScore: Optional[float] = None
    qualityScore:   Optional[float] = None
    isTpac:         bool = False
    competencyId:   Optional[str] = None
    competencyName: Optional[str] = None
    priorityRank:   Optional[int] = None
    matchReasons:   List[str] = Field(default_factory=list)
    # FIX (Bug #6): distinguishes verified TPAC from inferred TPAC
    # "frac_tag" = course found via FRAC tag; "semantic_fallback" = no tagged course exists
    matchType:   Optional[str] = None   # "frac_tag" | "semantic_fallback"
    # "verified" = is_tpac field present in catalog; "inferred" = creator name match; "none"
    tpacSource:  Optional[str] = None   # "verified" | "inferred" | "none"


class RecommendationResponse(BaseModel):
    status:          str
    officialId:      Optional[str] = None
    skillGaps:       List[dict] = Field(default_factory=list)
    recommendations: List[Recommendation]


class Enrollment(BaseModel):
    enrollmentId:       str
    courseId:           str
    courseTitle:        str
    provider:           str
    durationHours:      float
    progressPercentage: int
    remainingHours:     float
    lastAccessed:       str
    status:             str


class EnrollmentsResponse(BaseModel):
    status:      str
    enrollments: List[Enrollment]


class Achievement(BaseModel):
    id:       str
    title:    str
    score:    int
    date:     str
    category: str  # "RAG Quiz" | "External Certification"


class AchievementsResponse(BaseModel):
    status:       str
    achievements: List[Achievement]