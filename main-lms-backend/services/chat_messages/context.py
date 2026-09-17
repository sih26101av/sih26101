from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ReplyContext:
    """Everything a reply template may personalise, built once per chat request."""

    page: str                      # "home" | "dashboard"
    role: str
    dept: str
    message: str = ""
    full_name: Optional[str] = None
    gov_id: Optional[str] = None
    gaps: list[Any] = field(default_factory=list)   # SkillGapContext-like
    recs: list[Any] = field(default_factory=list)   # RecommendationContext-like

    @classmethod
    def from_request(cls, req: Any) -> "ReplyContext":
        return cls(
            page="home" if (req.context or "dashboard") == "home" else "dashboard",
            role=req.job_role or "Statistical Official",
            dept=req.department or "MoSPI",
            message=req.message,
            full_name=req.full_name or None,
            gov_id=req.gov_id or None,
            gaps=list(req.skill_gaps),
            recs=list(req.recommendations),
        )

    @property
    def active_gaps(self) -> list[Any]:
        return [g for g in self.gaps if g.gapScore > 0]

    @property
    def sorted_active_gaps(self) -> list[Any]:
        return sorted(self.active_gaps, key=lambda g: -g.gapScore)

    @property
    def top_gap(self) -> Optional[Any]:
        ranked = self.sorted_active_gaps
        return ranked[0] if ranked else None

    @property
    def stats(self) -> dict:
        from ai.semantic_engine import vectorize_profile

        return vectorize_profile([
            {"skillName": g.skillName, "domain": g.domain, "currentLevel": g.currentLevel,
             "targetLevel": g.targetLevel, "gapScore": g.gapScore}
            for g in self.gaps
        ])
