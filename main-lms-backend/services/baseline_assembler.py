"""
services/baseline_assembler.py
Evidence Assembly Layer — gathers 6 evidence terms and calls CompetencyCalculator.

Changes vs prior version:
- Bug #2 fix: _verified_from_enrollments NO LONGER falls back to a general
  engagement score when no FRAC-tag-matched completion exists. Stage 2
  (_enrollment_weighted_score) is removed entirely. If a user has zero
  completions of courses actually tagged with this comp_id, Verified = 0.0.
- Bug #4 fix: two-pass computation. Pass 1 builds verified_scores_by_comp
  dict; Pass 2 calls CompetencyCalculator.compute_synergy() which uses the
  explicit ADJACENT_COMPETENCIES table instead of a blanket category count.
- Bug #1 fix: when confidence == "UNASSESSED", currentLevel is set to None,
  never fabricated.
- Bug #9 read path: PRACTICE_ASSESSMENT rows from EvidenceLog are treated as
  the documented evidence channel (same decay logic as DOCUMENTED_CERT).
"""
from __future__ import annotations
import math
from datetime import datetime
from typing import Any, Dict, List, Optional
from services.competency_service import CompetencyCalculator

_calculator = CompetencyCalculator()

_TIER_SENIORITY = {
    "TIER1_SENIOR": 4.5, "TIER2_UPPER": 3.5, "TIER3_MID": 2.5,
    "TIER4_JUNIOR": 1.5, "TIER5_ENTRY": 0.5,
}

_EDU_RELEVANCE = {
    "statistics":   {"DOMAIN_TECHNICAL": 4.5, "GENERIC_BEHAVIOURAL": 1.0},
    "economics":    {"DOMAIN_TECHNICAL": 3.5, "GENERIC_BEHAVIOURAL": 1.5},
    "mathematics":  {"DOMAIN_TECHNICAL": 3.5, "GENERIC_BEHAVIOURAL": 0.5},
    "computer":     {"DOMAIN_TECHNICAL": 4.0, "GENERIC_BEHAVIOURAL": 1.0},
    "data":         {"DOMAIN_TECHNICAL": 4.0, "GENERIC_BEHAVIOURAL": 1.0},
    "engineering":  {"DOMAIN_TECHNICAL": 3.0, "GENERIC_BEHAVIOURAL": 1.0},
    "management":   {"DOMAIN_TECHNICAL": 1.5, "GENERIC_BEHAVIOURAL": 3.5},
    "public admin": {"DOMAIN_TECHNICAL": 1.0, "GENERIC_BEHAVIOURAL": 4.0},
    "law":          {"DOMAIN_TECHNICAL": 1.0, "GENERIC_BEHAVIOURAL": 3.5},
    "science":      {"DOMAIN_TECHNICAL": 2.5, "GENERIC_BEHAVIOURAL": 1.0},
    "arts":         {"DOMAIN_TECHNICAL": 0.5, "GENERIC_BEHAVIOURAL": 2.0},
    "commerce":     {"DOMAIN_TECHNICAL": 2.0, "GENERIC_BEHAVIOURAL": 2.0},
}
_EDU_DEFAULT = {"DOMAIN_TECHNICAL": 1.0, "GENERIC_BEHAVIOURAL": 1.5}


def _map_category(frac_type: str) -> str:
    return "GENERIC_BEHAVIOURAL" if frac_type.lower() in ("behavioural", "generic") else "DOMAIN_TECHNICAL"


def _education_score(education: list, cat: str) -> float:
    if not education:
        return 0.0
    best = 0.0
    for edu in education:
        degree = (edu.get("degree") or "").lower()
        for kw, sc in _EDU_RELEVANCE.items():
            if kw in degree:
                best = max(best, sc.get(cat, 0.0))
    return best if best > 0 else _EDU_DEFAULT.get(cat, 1.0)



def _tenure_score(career_history: list, exp_years: int, cat: str, comp_name: str) -> float:
    if not career_history:
        return round(min((min(exp_years or 0, 20) / 20.0) * 3.0, 5.0), 2)
    kw = set((comp_name or "").lower().split())
    total = 0.0
    for p in career_history:
        dur = float(p.get("duration_years") or 0)
        if dur <= 0:
            continue
        title = (p.get("title") or "").lower()
        if cat == "DOMAIN_TECHNICAL":
            overlap = len(kw & set(title.split()))
            rel = min(1.0, 0.3 + 0.2 * overlap)
        else:
            rel = 1.0
        years_ago = max(0, (exp_years or 0) - dur)
        decay = max(0.3, math.exp(-years_ago / 5.0))
        total += dur * rel * decay
    return round(min((total / 10.0) * 4.0, 5.0), 2)


def _verified_from_enrollments(enrollments: list, comp_id: str, course_comp_map: dict) -> float:
    """
    FIX (Bug #2): STRICTLY comp-id-tag-matched. Stage 2 general engagement
    fallback is REMOVED. If no enrolled course is actually tagged with this
    comp_id, returns 0.0 — this competency's Verified channel is empty.

    No fallback preserves the evidence hierarchy:
      Verified > Documented > Tenure > Self-report > Education > Seniority
    A user with unrelated enrollments no longer gets an inflated Verified
    score, which was previously promoting them to HIGH confidence incorrectly.
    """
    best = 0.0
    for e in enrollments:
        pct = float(e.get("completionPercentage") or 0)
        cid = e.get("courseId") or e.get("contentId") or ""
        if not cid:
            continue
        # Only credit if this course is actually tagged with the target comp_id
        if comp_id in course_comp_map.get(cid, []):
            best = max(best, (pct / 100.0) * 3.5)
    return round(best, 2)


class BaselineAssembler:
    def __init__(self, course_comp_map: Dict[str, List[str]]):
        self._course_comp_map = course_comp_map

    def compute_for_user(
        self,
        user: Dict[str, Any],
        enrollments: List[Dict],
        db_evidence: Optional[List[Dict]] = None,
        now: Optional[datetime] = None,
    ) -> Dict[str, Dict]:
        now        = now or datetime.utcnow()
        db_evidence = db_evidence or []
        exp_years  = int(user.get("experienceYears") or 0)
        job_profile = user.get("jobProfile") or {}
        education  = user.get("education") or []
        career     = user.get("careerHistory") or []

        raw = (
            user.get("competencies")
            or (user.get("profileDetails") or {}).get("competencies")
            or []
        )
        seen, comps = set(), []
        for c in raw:
            cid = c.get("id", "")
            if cid and cid not in seen:
                seen.add(cid)
                comps.append(c)

        # Index DB evidence rows by comp_id for fast lookup
        db_idx: Dict[str, List[Dict]] = {}
        for row in db_evidence:
            k = row.get("comp_id") or row.get("compId", "")
            if k:
                db_idx.setdefault(k, []).append(row)

        # ── Pass 1: compute Verified for every competency first ────────────────
        # We need the full verified_scores_by_comp dict before computing synergy
        # in Pass 2, because synergy depends on adjacent comps' Verified scores.
        verified_scores_by_comp: Dict[str, float] = {}
        for c in comps:
            cid  = c.get("id", "")
            vs   = _verified_from_enrollments(enrollments, cid, self._course_comp_map)
            for r in db_idx.get(cid, []):
                if r.get("evidence_type") == "VERIFIED_IGOT":
                    vs = max(vs, float(r.get("granted_value") or 0))
            verified_scores_by_comp[cid] = vs

        # ── Pass 2: full 6-term fusion with adjacency synergy ─────────────────
        results: Dict[str, Dict] = {}
        for comp in comps:
            cid   = comp.get("id", "")
            ftype = comp.get("type", "Functional")
            name  = (comp.get("name") or "").strip()
            cat   = _map_category(ftype)
            req   = int(comp.get("requiredLevel") or 3)

            vs    = verified_scores_by_comp.get(cid, 0.0)

            # DocumentedScore — Bug #9 read path: include PRACTICE_ASSESSMENT rows
            # in the documented channel so quiz-derived evidence feeds the formula.
            ds, doc_date = 0.0, None
            for r in db_idx.get(cid, []):
                etype = r.get("evidence_type") or r.get("evidenceType", "")
                if etype in ("DOCUMENTED_CERT", "PRACTICE_ASSESSMENT"):
                    val = float(r.get("granted_value") or r.get("grantedValue") or 0)
                    if val > ds:
                        ds = val
                        rd = r.get("issue_date") or r.get("issueDate")
                        if rd:
                            doc_date = (
                                rd if isinstance(rd, datetime)
                                else datetime.fromisoformat(str(rd))
                            )

            # TenureScore
            ts  = _tenure_score(career, exp_years, cat, name)

            # SelfReportedScore
            srs = max(
                (
                    float(r.get("granted_value") or r.get("grantedValue") or 0)
                    for r in db_idx.get(cid, [])
                    if (r.get("evidence_type") or r.get("evidenceType", "")) == "SELF_REPORT"
                ),
                default=0.0,
            )

            # EducationMatchScore
            es  = _education_score(education, cat)

            # SeniorityPrior (0 for DOMAIN/TECHNICAL per spec)
            tier = (job_profile.get("tier") or "TIER4_JUNIOR").upper()
            sen  = _TIER_SENIORITY.get(tier, 1.5) if cat == "GENERIC_BEHAVIOURAL" else 0.0

            # FIX (Bug #4): pass comp_id and verified_scores_by_comp so the
            # calculator uses the explicit adjacency table, not a blanket count.
            b_k, conf = _calculator.calculate_baseline(
                frac_type=ftype,
                evidence_data={
                    "verified": vs, "documented": ds, "doc_date": doc_date,
                    "tenure": ts, "self_report": srs, "education": es, "seniority": sen,
                },
                verified_count_in_category=0,           # unused when comp_id supplied
                current_time=now,
                verified_scores_by_comp=verified_scores_by_comp,  # Bug #4
                comp_id=cid,                            # Bug #4
            )

            # FIX (Bug #1): UNASSESSED → currentLevel = None, never fabricated.
            if conf == "UNASSESSED":
                current_level = None
            else:
                # Ceiling-relative scaling so displayed level reflects "how far
                # along within the possible range", not just the raw floor.
                if conf == "HIGH":
                    ceiling = 5.0
                    current_level = min(int(b_k), req - 1)
                elif conf == "MEDIUM":
                    ceiling = 3.5
                    normalized = (b_k / ceiling) * (req - 1)
                    current_level = min(round(normalized), req - 1)
                else:  # LOW
                    ceiling = 2.5
                    if b_k <= 0:
                        current_level = 0
                    else:
                        normalized = (b_k / ceiling) * (req - 1)
                        current_level = min(round(normalized), req - 1)

            results[cid] = {
                "score":      b_k,
                "confidence": conf,
                "currentLevel": current_level,  # None when UNASSESSED
                "_evidence": {
                    "verified":   round(vs, 3),
                    "documented": round(ds, 3),
                    "tenure":     round(ts, 3),
                    "selfReport": round(srs, 3),
                    "education":  round(es, 3),
                    "seniority":  round(sen, 3),
                },
            }
        return results



