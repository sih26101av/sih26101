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
- Bug #9 read path: PRACTICE_ASSESSMENT rows from EvidenceLog feed the
  documented evidence channel (same decay logic as DOCUMENTED_CERT). They are a
  running practice ability, so the LATEST row counts (not the max).
- Verified channel is level-aware: a COMPLETED course tagged with this
  competency at FRAC "Level N" credits N. Partial progress credits nothing
  (a 10%-watched course used to count as verified and flip confidence to HIGH).
- currentLevel is floor(b_k) on the 0-5 FRAC scale. The old `requiredLevel - 1`
  cap is gone — it made every evidence-backed gap impossible to close.
- resolve_level() is the single place that decides the level shown to the
  learner AND used by the recommendation/pathway engine, so the dashboard and
  recommendations can no longer disagree.
"""
from __future__ import annotations
import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from services.practice_assessment import latest_practice_value
from services.competency_service import (
    CHANNEL_WEIGHTS, CHANNEL_WEIGHTS_STATUS, CompetencyCalculator, fuse_channels,
)

_calculator = CompetencyCalculator()

# Anti-gaming ceilings by confidence tier (same values as CompetencyCalculator).
_CONFIDENCE_CEILING = {"HIGH": 5.0, "MEDIUM": 3.5, "LOW": 2.5, "UNASSESSED": 0.0}

# Credit for a completed course whose FRAC tag carries no level (legacy maps).
_UNLEVELLED_COMPLETION_CREDIT = 3.5

_CONFIDENCE_RANK = {"UNASSESSED": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}

_TIER_SENIORITY = {
    "TIER1_SENIOR": 4.5, "TIER2_UPPER": 3.5, "TIER3_MID": 2.5,
    "TIER4_JUNIOR": 1.5, "TIER5_ENTRY": 0.5,
    # tier names the iGOT profiles actually carry (same seniority bands)
    "TIER1_APEX": 4.5, "TIER2_SENIOR": 3.5,
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


def enrollment_course_id(e: Dict) -> str:
    return e.get("courseId") or e.get("contentId") or ""


def is_completed(e: Dict) -> bool:
    """iGOT/Sunbird marks completion as status 2 or 100% progress."""
    return e.get("status") == 2 or float(e.get("completionPercentage") or 0) >= 100


def _verified_from_enrollments(
    enrollments: list, comp_id: str, course_comp_map: Dict[str, Dict[str, Optional[int]]],
) -> Tuple[float, int]:
    """
    Returns (verified_value, completed_level) for one competency.

    FIX (Bug #2): STRICTLY comp-id-tag-matched — an enrollment only counts if
    the course is tagged with this comp_id. No general-engagement fallback.

    Only COMPLETED courses count. The credit is the FRAC level the course is
    tagged at for this competency: finishing a "Level 3" course is evidence of
    Level 3, not of a flat 3.5 regardless of what the course teaches.
    completed_level is the highest such level (0 if none) and acts as an
    evidence floor in resolve_level().
    """
    best, completed_level = 0.0, 0
    for e in enrollments:
        cid = enrollment_course_id(e)
        if not cid or not is_completed(e):
            continue
        tags = course_comp_map.get(cid, {})
        if comp_id not in tags:
            continue
        level = tags[comp_id]
        if level:
            best = max(best, float(level))
            completed_level = max(completed_level, int(level))
        else:
            best = max(best, _UNLEVELLED_COMPLETION_CREDIT)
    return round(best, 2), completed_level


def resolve_level(assessment: Dict, self_reported_level: int = 0) -> Dict:
    """
    Single source of truth for an official's level on one competency.

    Every evidence source in this system is a *floor*: completing a Level-N
    course, passing a practice quiz or holding a certificate shows the official
    can do at least that much — none of them shows they can do less. So the
    displayed level is the highest floor, which makes it monotone: doing more
    learning can never lower it (it used to — finishing a course could turn a
    gap of 0 into a gap of 3).

    Self-report is a claim, not evidence. It still counts as a floor (an
    official who claims Level 4 is not shown as Level 1), but when it is the
    thing setting the level the confidence is LOW with basis "self_report", and
    the pathway engine puts a diagnostic check first.

    Returns {"level", "confidence", "basis", "evidenceLevel"}; level is None
    only when there is no evidence and no claim at all (UNASSESSED).
    """
    formula_level = assessment.get("currentLevel")          # None when UNASSESSED
    formula_conf  = assessment.get("confidence", "UNASSESSED")

    evidence_level: Optional[int] = None
    confidence, basis = "UNASSESSED", "none"
    if formula_level is not None:
        evidence_level, confidence, basis = formula_level, formula_conf, "evidence"
    # Demonstrated-level floors: a completed Level-N course, a passed Level-N work
    # sample (SCIL v6 §3 A), a supervisor-confirmed use of a Level-N course (U).
    # A supervisor rating is NOT a floor — raters are lenient — it only enters
    # the fused estimate above.
    for floor, conf, why in (
        (int(assessment.get("completedLevel") or 0), "HIGH", "course_completion"),
        (int(assessment.get("workSampleLevel") or 0), "HIGH", "work_sample"),
        (int(assessment.get("appliedLevel") or 0), "MEDIUM", "applied_at_work"),
    ):
        if floor and (evidence_level is None or floor > evidence_level):
            evidence_level, confidence, basis = floor, conf, why

    if self_reported_level and (evidence_level is None or self_reported_level > evidence_level):
        return {"level": self_reported_level, "confidence": "LOW",
                "basis": "self_report", "evidenceLevel": evidence_level}
    return {"level": evidence_level, "confidence": confidence,
            "basis": basis, "evidenceLevel": evidence_level}


def _row_type(r: Dict) -> str:
    return r.get("evidence_type") or r.get("evidenceType") or ""


def _row_value(r: Dict) -> float:
    return float(r.get("granted_value") or r.get("grantedValue") or 0)


def _row_date(r: Dict) -> str:
    d = r.get("issue_date") or r.get("issueDate") or ""
    return d.isoformat() if isinstance(d, datetime) else str(d)


def _workplace_channels(rows: List[Dict]) -> Dict[str, Any]:
    """
    SCIL v6 §3 workplace channels for one competency, on the 0–5 level scale:
      A — work samples: a passed Level-L sample shows L; a failed one shows
          "not yet L" (L − 0.5). Channel value = the best attempt.
      U — utility: the highest course level whose use the supervisor confirmed.
      S — supervisor rating (1–5), the most recent one.
    Peer ratings are counted for display only — never a channel.
    """
    a_vals, ws_floor, u_floor, s_latest, peer = [], 0, 0, None, 0
    for r in rows:
        etype, meta = _row_type(r), r.get("meta") or {}
        if etype == "WORK_SAMPLE":
            level = int(meta.get("level") or _row_value(r))
            passed = bool(meta.get("passed"))
            a_vals.append(float(level) if passed else max(0.0, level - 0.5))
            if passed:
                ws_floor = max(ws_floor, level)
        elif etype == "UTILITY":
            if meta.get("confirmed") and _row_value(r) > 0:
                u_floor = max(u_floor, int(_row_value(r)))
        elif etype == "SUPERVISOR_RATING":
            if s_latest is None or _row_date(r) > _row_date(s_latest):
                s_latest = r
        elif etype == "PEER_RATING":
            peer += 1
    return {
        "A": max(a_vals) if a_vals else None,
        "U": float(u_floor) if u_floor else None,
        "S": _row_value(s_latest) if s_latest is not None else None,
        "workSampleLevel": ws_floor,
        "appliedLevel": u_floor,
        "peer": peer,
    }


_DATED_EVIDENCE = {"VERIFIED_IGOT", "DOCUMENTED_CERT", "PRACTICE_ASSESSMENT", "WORK_SAMPLE",
                   "SUPERVISOR_RATING", "UTILITY"}


def _last_evidence_date(enrollments: list, tag: str, course_map: Dict[str, Dict[str, Optional[int]]],
                        rows: List[Dict]) -> Optional[str]:
    """ISO date of the newest DATED, objective evidence (SCIL v6 §2 decay clock). Tenure,
    education, self-report and peer ratings are undated priors / context — they don't count."""
    dates = [str(e.get("completedDate") or e.get("enrolledDate") or "")
             for e in enrollments
             if is_completed(e) and tag in course_map.get(enrollment_course_id(e), {})]
    for r in rows:
        etype = _row_type(r)
        if etype not in _DATED_EVIDENCE:
            continue
        if etype == "UTILITY" and not (r.get("meta") or {}).get("confirmed"):
            continue
        dates.append(_row_date(r))
    dates = [d for d in dates if d]
    return max(dates)[:10] if dates else None


def _normalise_course_map(course_comp_map: Dict) -> Dict[str, Dict[str, Optional[int]]]:
    """Accept {courseId: {compId: level}} or the legacy {courseId: [compId]}."""
    out: Dict[str, Dict[str, Optional[int]]] = {}
    for course_id, tags in (course_comp_map or {}).items():
        out[course_id] = dict(tags) if isinstance(tags, dict) else {c: None for c in tags}
    return out


class BaselineAssembler:
    def __init__(self, course_comp_map: Dict):
        # {courseId: {compId: FRAC level (1-5) or None}}
        self._course_comp_map = _normalise_course_map(course_comp_map)

    def compute_for_user(
        self,
        user: Dict[str, Any],
        enrollments: List[Dict],
        db_evidence: Optional[List[Dict]] = None,
        now: Optional[datetime] = None,
        comp_aliases: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Dict]:
        """
        `comp_aliases` maps a role competency id to the catalogue FRAC id it is
        crosswalked to (recommendation engine's crosswalk()). Course tags,
        adjacency and evidence rows are then read under both ids, so finishing
        a course from the competency's learning pathway moves its level.
        """
        comp_aliases = comp_aliases or {}
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

        def tag_id(cid: str) -> str:
            return comp_aliases.get(cid) or cid

        def rows_for(cid: str) -> List[Dict]:
            alias = tag_id(cid)
            return db_idx.get(cid, []) + (db_idx.get(alias, []) if alias != cid else [])

        # ── Pass 1: compute Verified for every competency first ────────────────
        # We need the full verified_scores_by_comp dict before computing synergy
        # in Pass 2, because synergy depends on adjacent comps' Verified scores.
        # Keyed by catalogue (tag) id — the id space ADJACENT_COMPETENCIES uses.
        verified_scores_by_comp: Dict[str, float] = {}
        completed_levels: Dict[str, int] = {}
        for c in comps:
            cid  = c.get("id", "")
            vs, completed_levels[cid] = _verified_from_enrollments(
                enrollments, tag_id(cid), self._course_comp_map
            )
            for r in rows_for(cid):
                if r.get("evidence_type") == "VERIFIED_IGOT":
                    vs = max(vs, float(r.get("granted_value") or 0))
            verified_scores_by_comp[tag_id(cid)] = max(vs, verified_scores_by_comp.get(tag_id(cid), 0.0))

        # ── Pass 2: full 6-term fusion with adjacency synergy ─────────────────
        results: Dict[str, Dict] = {}
        for comp in comps:
            cid   = comp.get("id", "")
            ftype = comp.get("type", "Functional")
            name  = (comp.get("name") or "").strip()
            cat   = _map_category(ftype)

            vs    = verified_scores_by_comp.get(tag_id(cid), 0.0)

            # DocumentedScore — the best certificate, or the learner's CURRENT
            # practice ability, whichever is higher. Practice rows (quizzes, the
            # adaptive diagnostic) are a running rating that goes up and down
            # with performance (services/practice_assessment.py), so only the
            # latest one counts — a max would make a failed quiz invisible.
            ds, doc_date = 0.0, None
            for r in rows_for(cid):
                etype = r.get("evidence_type") or r.get("evidenceType", "")
                if etype == "DOCUMENTED_CERT":
                    val = float(r.get("granted_value") or r.get("grantedValue") or 0)
                    if val > ds:
                        ds = val
                        rd = r.get("issue_date") or r.get("issueDate")
                        if rd:
                            doc_date = (
                                rd if isinstance(rd, datetime)
                                else datetime.fromisoformat(str(rd))
                            )
            practice, practice_date = latest_practice_value(rows_for(cid))
            if practice > ds:
                ds, doc_date = practice, practice_date

            # TenureScore
            ts  = _tenure_score(career, exp_years, cat, name)

            # SelfReportedScore
            srs = max(
                (
                    float(r.get("granted_value") or r.get("grantedValue") or 0)
                    for r in rows_for(cid)
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
                comp_id=tag_id(cid),                    # Bug #4 (catalogue id space)
            )

            # ── SCIL v6 §3: fuse K (this b_k) with the workplace channels A/U/S ──
            work = _workplace_channels(rows_for(cid))
            knowledge = None if conf == "UNASSESSED" else b_k
            fused = fuse_channels({"K": knowledge, "A": work["A"], "U": work["U"], "S": work["S"]})
            # Confidence from the strongest OBJECTIVE channel: a passed work sample
            # is demonstrated performance (HIGH); supervisor-confirmed use lifts a
            # LOW/UNASSESSED estimate to MEDIUM; a supervisor rating alone is LOW.
            # The anti-gaming ceilings still apply, so a lenient rater with no
            # objective evidence behind them cannot lift the level above 2.5.
            if work["workSampleLevel"]:
                conf = "HIGH"
            elif work["appliedLevel"] and conf in ("LOW", "UNASSESSED"):
                conf = "MEDIUM"
            elif fused is not None and conf == "UNASSESSED":
                conf = "LOW"
            score = 0.0 if fused is None else min(fused, _CONFIDENCE_CEILING[conf])

            # FIX (Bug #1): UNASSESSED → currentLevel = None, never fabricated.
            # Otherwise the highest FRAC level fully reached. The score is on the
            # 0-5 level scale (channels are renormalised) and bounded by the
            # confidence ceiling, so no further rescaling or capping.
            current_level = None if conf == "UNASSESSED" else max(0, min(5, int(score)))

            channels = {"K": knowledge, "A": work["A"], "U": work["U"], "S": work["S"]}
            results[cid] = {
                "score":      round(score, 3),
                "knowledgeScore": b_k,
                "confidence": conf,
                "currentLevel":   current_level,          # None when UNASSESSED
                "completedLevel": completed_levels.get(cid, 0),
                "workSampleLevel": work["workSampleLevel"],   # evidence floor (passed work sample)
                "appliedLevel":    work["appliedLevel"],      # evidence floor (supervisor-confirmed use)
                "channels": {k: (round(v, 3) if v is not None else None) for k, v in channels.items()},
                "completeness": {
                    "present": [k for k, v in channels.items() if v is not None],
                    "missing": [k for k, v in channels.items() if v is None],
                    "weights": CHANNEL_WEIGHTS, "weightsStatus": CHANNEL_WEIGHTS_STATUS,
                },
                "peerFeedback": work["peer"],
                "lastEvidenceDate": _last_evidence_date(enrollments, tag_id(cid), self._course_comp_map,
                                                        rows_for(cid)),
                "_evidence": {
                    "verified":   round(vs, 3),
                    "documented": round(ds, 3),
                    "tenure":     round(ts, 3),
                    "selfReport": round(srs, 3),
                    "education":  round(es, 3),
                    "seniority":  round(sen, 3),
                    "workSample": round(work["A"] or 0.0, 3),
                    "utility":    round(work["U"] or 0.0, 3),
                    "supervisor": round(work["S"] or 0.0, 3),
                },
            }
        return results



