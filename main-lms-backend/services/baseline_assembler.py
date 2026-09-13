"""
services/baseline_assembler.py
Evidence Assembly Layer - gathers 6 evidence terms and calls CompetencyCalculator.
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
    return "GENERIC_BEHAVIOURAL" if frac_type.lower() in ("behavioural","generic") else "DOMAIN_TECHNICAL"


def _education_score(education: list, cat: str) -> float:
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


def _enrollment_weighted_score(enrollments: list) -> float:
    """
    Returns a score [0, 3.5] based on the USER's actual iGOT engagement:
      - Total weighted completion: SUM(completionPct) / (N_enrolled * 100) * 3.5
    This varies realistically:
      - 5 courses all at 100%  → 3.5
      - 3 courses at 100/57/0 → (157/300)*3.5 = 1.83
      - 10 courses avg 30%    → 0.30 * 3.5 = 1.05
      - 0 courses or all 0%   → 0.0
    """
    if not enrollments:
        return 0.0
    total_pct = sum(float(e.get("completionPercentage") or 0) for e in enrollments)
    max_possible = len(enrollments) * 100
    fraction = total_pct / max_possible if max_possible > 0 else 0.0
    return round(fraction * 3.5, 2)


def _verified_from_enrollments(enrollments: list, comp_id: str, course_comp_map: dict) -> float:
    """
    Stage 1: Exact comp_id → course match (max 3.5, comp-specific).
    Stage 2: General engagement fallback using weighted-average completion.
             Score is the same scale (0-3.5) but confidence stays driven by
             the same vs > 0 check — so HIGH vs LOW still distinguishes cases.

    The key fix: every user gets a DIFFERENT fallback score based on their
    actual enrollment history, not a flat max_pct. This produces realistic
    variation (0.0 to 3.5) across the 151 mock users.
    """
    completed = {}
    for e in enrollments:
        pct = float(e.get("completionPercentage") or 0)
        cid = e.get("courseId") or e.get("contentId") or ""
        if cid:
            completed[cid] = max(completed.get(cid, 0.0), pct)

    # Stage 1: comp-specific (best quality)
    best = 0.0
    for course_id, pct in completed.items():
        if comp_id in course_comp_map.get(course_id, []):
            best = max(best, (pct / 100.0) * 3.5)

    # Stage 2: general fallback — different for every user based on their engagement
    if best == 0.0:
        best = _enrollment_weighted_score(enrollments)

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
        now = now or datetime.utcnow()
        db_evidence = db_evidence or []
        exp_years   = int(user.get("experienceYears") or 0)
        job_profile = user.get("jobProfile") or {}
        education   = user.get("education") or []
        career      = user.get("careerHistory") or []

        raw = user.get("competencies") or (user.get("profileDetails") or {}).get("competencies") or []
        seen, comps = set(), []
        for c in raw:
            cid = c.get("id","")
            if cid and cid not in seen:
                seen.add(cid); comps.append(c)

        db_idx: Dict[str, List[Dict]] = {}
        for row in db_evidence:
            k = row.get("comp_id") or row.get("compId","")
            if k: db_idx.setdefault(k, []).append(row)

        # First pass: count verified per category for synergy
        verified_counts: Dict[str, int] = {}
        for c in comps:
            cat = _map_category(c.get("type","Functional"))
            vs = _verified_from_enrollments(enrollments, c.get("id",""), self._course_comp_map)
            for r in db_idx.get(c.get("id",""), []):
                if r.get("evidence_type") == "VERIFIED_IGOT":
                    vs = max(vs, float(r.get("granted_value") or 0))
            if vs > 0:
                verified_counts[cat] = verified_counts.get(cat, 0) + 1

        results: Dict[str, Dict] = {}
        for comp in comps:
            cid      = comp.get("id","")
            ftype    = comp.get("type","Functional")
            name     = (comp.get("name") or "").strip()
            cat      = _map_category(ftype)
            req      = int(comp.get("requiredLevel") or 3)

            # VerifiedScore
            vs = _verified_from_enrollments(enrollments, cid, self._course_comp_map)
            for r in db_idx.get(cid, []):
                if r.get("evidence_type") == "VERIFIED_IGOT":
                    vs = max(vs, float(r.get("granted_value") or 0))

            # DocumentedScore
            ds, doc_date = 0.0, None
            for r in db_idx.get(cid, []):
                if r.get("evidence_type") == "DOCUMENTED_CERT":
                    val = float(r.get("granted_value") or 0)
                    if val > ds:
                        ds = val
                        rd = r.get("issue_date")
                        if rd:
                            doc_date = rd if isinstance(rd, datetime) else datetime.fromisoformat(str(rd))

            # TenureScore
            ts = _tenure_score(career, exp_years, cat, name)

            # SelfReportedScore
            srs = max((float(r.get("granted_value") or 0) for r in db_idx.get(cid, []) if r.get("evidence_type")=="SELF_REPORT"), default=0.0)

            # EducationMatchScore
            es = _education_score(education, cat)

            # SeniorityPrior (0 for DOMAIN/TECHNICAL per spec)
            tier = (job_profile.get("tier") or "TIER4_JUNIOR").upper()
            sen  = _TIER_SENIORITY.get(tier, 1.5) if cat == "GENERIC_BEHAVIOURAL" else 0.0

            b_k, conf = _calculator.calculate_baseline(
                frac_type=ftype,
                evidence_data={"verified": vs, "documented": ds, "doc_date": doc_date,
                               "tenure": ts, "self_report": srs, "education": es, "seniority": sen},
                verified_count_in_category=verified_counts.get(cat, 0),
                current_time=now,
            )

            # currentLevel: normalize b_k relative to the active ceiling so the displayed
            # level reflects "how far along within the possible range" not just the raw floor.
            # - HIGH confidence (verified): ceiling=5.0 → int(b_k) is the true absolute level
            # - MEDIUM (documented):        ceiling=3.5 → scale b_k to [0, req-1]
            # - LOW (inferred only):        ceiling=2.5 → scale b_k to [0, req-1]
            # Always capped at req-1 so there's always a visible gap.
            if conf == "HIGH":
                ceiling = 5.0
            elif conf == "MEDIUM":
                ceiling = 3.5
            else:
                ceiling = 2.5

            if b_k <= 0:
                current_level = 0
            elif conf == "HIGH":
                # Absolute scale — int floor is correct
                current_level = min(int(b_k), req - 1)
            else:
                # Ceiling-relative: shows how far the user is within the inferred range
                normalized = (b_k / ceiling) * (req - 1)
                current_level = min(round(normalized), req - 1)

            results[cid] = {
                "score": b_k, "confidence": conf, "currentLevel": current_level,
                "_evidence": {"verified": round(vs, 3), "documented": round(ds, 3),
                              "tenure": round(ts, 3), "selfReport": round(srs, 3),
                              "education": round(es, 3), "seniority": round(sen, 3)},
            }
        return results
