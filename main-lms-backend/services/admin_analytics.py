"""
services/admin_analytics.py — server-side aggregates for the admin console

Pure functions over the admin roster (mock iGOT /api/admin/v1/users, one row
per official) and, where competency levels are needed, the workforce SNAPSHOT
(main._build_workforce_snapshot). routers/admin_console.py wires them to HTTP.

These used to run in the browser over the whole roster on every load
(frontend/src/hooks/useAdminData.ts); now the browser gets one page or one
aggregate. Filters (department, grade, office) apply to every function.

Small-cell rule: aggregates over fewer than SUPPRESS_BELOW officials report
`suppressed: true` and hide their percentages — the same disclosure control the
workforce foresight views use (workforce_service.SUPPRESS_BELOW).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from statistics import mean
from typing import Any, Callable, Dict, Iterable, List, Optional, Set

from services.workforce_service import ANNUAL_ATTRITION, SUPPRESS_BELOW, _p_capable, cell

GRADE_LABELS = {
    "TIER1_APEX":   "Tier 1 · Apex (SAG and above)",
    "TIER2_SENIOR": "Tier 2 · Senior (JAG / DDG)",
    "TIER3_MID":    "Tier 3 · Middle (DD / AD)",
    "TIER4_JUNIOR": "Tier 4 · Junior (SSO / JSO)",
}

STATUS_LABELS = {2: "Compliant", 1: "In Progress", 0: "Training Required"}

EMERGING_HORIZON_MONTHS = 36
EMERGING_SCOPE_WEIGHT = 1.25      # competency is exercised in the GSBPM core (80% of officer-hours)
EMERGING_CRITICAL_WEIGHT = 1.25   # competency is critical to a statistical product
EMERGING_SHORTLIST = 10           # "what should NSSTA train next year" — top-N by priority


# ── Roster rows ────────────────────────────────────────────────────────────────

def _level_num(level: Optional[str]) -> int:
    digits = "".join(ch for ch in (level or "") if ch.isdigit())
    return int(digits) if digits else 2


def normalise(u: Dict[str, Any]) -> Dict[str, Any]:
    """One mock-roster user → the row shape every admin view uses."""
    comps = u.get("competencies") or []
    missing = [c for c in comps if c.get("status") in ("PLANNED", "IN_PROGRESS")]
    grade = u.get("grade")
    return {
        "userId": u["userId"],
        "govId": u.get("govId") or u["userId"],
        "firstName": u.get("firstName") or "",
        "lastName": u.get("lastName") or "",
        "email": u.get("email") or "",
        "designation": u.get("designation") or "Official",
        "department": u.get("department") or "Unspecified",
        "grade": grade,
        "gradeLabel": GRADE_LABELS.get(grade or "", grade or "Unspecified"),
        "officeId": u.get("officeId"),
        "officeName": u.get("officeName") or u.get("officeId") or "Unspecified",
        "enrollmentStatus": int(u.get("enrollmentStatus") or 0),
        "missingSkill": u.get("missingSkill"),
        "missingCount": len(missing),
        "completedCourseIds": u.get("completedCourseIds") or [],
        # courseId → first completion date (YYYY-MM-DD), for reconstructed trend history
        "completions": {c["courseId"]: c["completedDate"] for c in (u.get("completions") or [])
                        if c.get("completedDate")},
        "mandatory": u.get("mandatory"),
        "competencies": comps,
    }


def public_row(r: Dict[str, Any]) -> Dict[str, Any]:
    """Roster row for the API — without the bulky competency list."""
    out = {k: v for k, v in r.items() if k not in ("competencies", "completedCourseIds", "completions")}
    out["statusLabel"] = STATUS_LABELS.get(r["enrollmentStatus"], "Training Required")
    return out


@dataclass(frozen=True)
class Filters:
    department: Optional[str] = None
    grade: Optional[str] = None
    office: Optional[str] = None      # officeId

    def active(self) -> Dict[str, str]:
        return {k: v for k, v in (("department", self.department), ("grade", self.grade),
                                  ("office", self.office)) if v}

    def match(self, r: Dict[str, Any]) -> bool:
        return ((not self.department or r["department"] == self.department)
                and (not self.grade or r["grade"] == self.grade)
                and (not self.office or r["officeId"] == self.office))


def apply_filters(rows: Iterable[Dict[str, Any]], f: Filters) -> List[Dict[str, Any]]:
    return [r for r in rows if f.match(r)]


def search(rows: Iterable[Dict[str, Any]], q: str) -> List[Dict[str, Any]]:
    q = (q or "").strip().lower()
    if not q:
        return list(rows)
    return [r for r in rows if q in f"{r['firstName']} {r['lastName']}".lower()
            or q in r["govId"].lower() or q in r["userId"].lower()
            or q in r["department"].lower() or q in r["designation"].lower()
            or q in (r["missingSkill"] or "").lower()]


def paginate(items: List[Any], page: int, page_size: int) -> Dict[str, Any]:
    page_size = max(1, min(page_size, 200))
    total = len(items)
    total_pages = max(1, math.ceil(total / page_size))
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    return {"items": items[start:start + page_size], "total": total, "page": page,
            "pageSize": page_size, "totalPages": total_pages}


def facets(rows: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Filter options with headcounts, from the whole (unfiltered) roster."""
    def count(key: str, label: Callable[[Dict[str, Any]], str]):
        seen: Dict[str, Dict[str, Any]] = {}
        for r in rows:
            v = r[key]
            if not v:
                continue
            seen.setdefault(v, {"value": v, "label": label(r), "count": 0})["count"] += 1
        return sorted(seen.values(), key=lambda o: o["label"])
    return {
        "departments": count("department", lambda r: r["department"]),
        "grades": sorted(count("grade", lambda r: r["gradeLabel"]), key=lambda o: o["value"]),
        "offices": count("officeId", lambda r: r["officeName"]),
    }


# ── KPIs, heatmap, departmental compliance ─────────────────────────────────────

def status_counts(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    return {"compliant": sum(r["enrollmentStatus"] == 2 for r in rows),
            "inProgress": sum(r["enrollmentStatus"] == 1 for r in rows),
            "required": sum(r["enrollmentStatus"] == 0 for r in rows)}


def is_behind_mandatory(r: Dict[str, Any]) -> bool:
    m = r.get("mandatory")
    return bool(m and m["completed"] < m["total"])


def mandatory_summary(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    with_plan = [r for r in rows if r.get("mandatory") and r["mandatory"]["total"]]
    total = sum(r["mandatory"]["total"] for r in with_plan)
    done = sum(r["mandatory"]["completed"] for r in with_plan)
    return {
        "officialsWithPlan": len(with_plan),
        "behind": sum(is_behind_mandatory(r) for r in with_plan),
        "coursesAssigned": total,
        "coursesCompleted": done,
        "completionPct": round(100 * done / total, 1) if total else None,
    }


def kpis(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    n = len(rows)
    sc = status_counts(rows)
    return {
        "totalOfficials": n,
        "trainingCompliancePct": round(100 * sc["compliant"] / n) if n else 0,
        "avgMissingSkills": round(sum(r["missingCount"] for r in rows) / n, 1) if n else 0,
        "mandatory": mandatory_summary(rows),
        "suppressed": 0 < n < SUPPRESS_BELOW,
    }


def heatmap(rows: List[Dict[str, Any]], top: int = 8) -> List[Dict[str, Any]]:
    """
    Competency shortage index (same formula the browser used): for every
    PLANNED / IN_PROGRESS competency, weight (1.5 planned, 1 in progress) ×
    (4 − current level), summed over officials.
    """
    score: Dict[str, float] = {}
    officials: Dict[str, int] = {}
    for r in rows:
        for c in r["competencies"]:
            if c.get("status") not in ("PLANNED", "IN_PROGRESS"):
                continue
            w = 1.5 if c["status"] == "PLANNED" else 1.0
            name = c.get("name") or c.get("id") or "?"
            score[name] = score.get(name, 0.0) + w * (4 - _level_num(c.get("competencyLevel") or "Level 2"))
            officials[name] = officials.get(name, 0) + 1
    ranked = sorted(score.items(), key=lambda kv: -kv[1])[:top]
    return [{"competency": name, "gap": round(s, 1), "officials": cell(officials[name])}
            for name, s in ranked]


def dept_compliance(rows: List[Dict[str, Any]], top: Optional[int] = None) -> List[Dict[str, Any]]:
    """Share of officials with a completed course, per department (biggest first)."""
    by: Dict[str, List[int]] = {}
    for r in rows:
        by.setdefault(r["department"], []).append(r["enrollmentStatus"])
    out = []
    for dept, statuses in sorted(by.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        n = len(statuses)
        small = n < SUPPRESS_BELOW
        m = mandatory_summary([r for r in rows if r["department"] == dept])
        out.append({
            "dept": dept, "headcount": n, "suppressed": small,
            "pct": None if small else round(100 * sum(s == 2 for s in statuses) / n),
            "mandatoryPct": None if small else m["completionPct"],
            "behindMandatory": cell(m["behind"]),
        })
    return out[:top] if top else out


# ── Daily snapshot metrics (trend charts) ──────────────────────────────────────

def _competency_metrics(uids: Set[str], snapshot: Optional[Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
    if not snapshot:
        return {"avgLevel": None, "atTargetPct": None, "assessedPct": None}
    rows = [c for uid in uids if uid in snapshot for c in snapshot[uid]["competencies"]]
    levelled = [c for c in rows if c.get("level") is not None]
    return {
        "avgLevel": round(mean(c["level"] for c in levelled), 2) if levelled else None,
        "atTargetPct": round(100 * sum(c["level"] >= c["target"] for c in levelled if c.get("target"))
                             / len(rows), 1) if rows else None,
        "assessedPct": round(100 * sum(c.get("confidence") not in (None, "UNASSESSED") for c in rows)
                             / len(rows), 1) if rows else None,
    }


def metrics(rows: List[Dict[str, Any]], snapshot: Optional[Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
    n = len(rows)
    k = kpis(rows)
    return {
        "officials": n,
        "compliancePct": k["trainingCompliancePct"] if n else None,
        "mandatoryCompletionPct": k["mandatory"]["completionPct"],
        "behindMandatory": k["mandatory"]["behind"],
        "avgMissingSkills": k["avgMissingSkills"] if n else None,
        **_competency_metrics({r["userId"] for r in rows}, snapshot),
    }


def daily_metrics(rows: List[Dict[str, Any]], snapshot: Optional[Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
    """Everything one AdminDailySnapshot row stores: overall + one breakdown per filter dimension."""
    def by(key: str) -> Dict[str, Any]:
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for r in rows:
            if r[key]:
                groups.setdefault(r[key], []).append(r)
        return {k: metrics(v, snapshot) for k, v in groups.items()}
    return {"overall": metrics(rows, snapshot), "byDepartment": by("department"),
            "byGrade": by("grade"), "byOffice": by("officeId"),
            "workforceSnapshot": bool(snapshot)}


def trend_point(snapshot_date: str, stored: Dict[str, Any], f: Filters) -> Optional[Dict[str, Any]]:
    """
    One day's numbers for the active filter. Stored breakdowns are one-dimensional,
    so with several filters the most specific stored dimension is used
    (office > department > grade) — the response says which.
    """
    for dim, key, value in (("office", "byOffice", f.office), ("department", "byDepartment", f.department),
                            ("grade", "byGrade", f.grade)):
        if value:
            m = (stored.get(key) or {}).get(value)
            if m is None:
                return None
            break
    else:
        m = stored.get("overall")
    if not m:
        return None
    point = {"date": snapshot_date, "reconstructed": False, **m}
    if 0 < (m.get("officials") or 0) < SUPPRESS_BELOW:
        point = {"date": snapshot_date, "officials": m["officials"], "suppressed": True, "reconstructed": False}
    return point


def trend_dimension(f: Filters) -> Optional[Dict[str, str]]:
    for dim, value in (("office", f.office), ("department", f.department), ("grade", f.grade)):
        if value:
            return {"dimension": dim, "value": value}
    return None


def reconstruct_history(rows: List[Dict[str, Any]], start: date, end: date) -> Dict[str, Any]:
    """
    Daily training-rate history rebuilt from dated iGOT course completions, for
    days with no stored snapshot (history before the snapshot job existed):

    * compliancePct — officials with a completed course on or before the day;
    * mandatoryCompletionPct — current-cycle ACBP courses completed by the day,
      over all ACBP courses assigned (the plan is taken as fixed);
    * weekly course completions (activity), Monday-start weeks.

    The population is today's (filtered) roster — joiners and leavers are not
    back-dated. Competency levels are NOT reconstructed: they come only from
    stored daily snapshots. Groups under SUPPRESS_BELOW are suppressed.
    """
    n = len(rows)
    first_done = sorted(min(r["completions"].values()) for r in rows if r.get("completions"))
    mand_dates, mand_total = [], 0
    for r in rows:
        m = r.get("mandatory")
        if m and m.get("total"):
            mand_total += m["total"]
            mand_dates += [r["completions"][c] for c in m.get("courseIds", []) if c in r["completions"]]
    mand_dates.sort()
    all_dates = sorted(d for r in rows for d in r.get("completions", {}).values())

    def count_upto(sorted_dates: List[str], day: str) -> int:
        lo, hi = 0, len(sorted_dates)
        while lo < hi:
            mid = (lo + hi) // 2
            if sorted_dates[mid] <= day:
                lo = mid + 1
            else:
                hi = mid
        return lo

    points = []
    day = start
    while day <= end:
        iso = day.isoformat()
        if 0 < n < SUPPRESS_BELOW:
            points.append({"date": iso, "officials": n, "suppressed": True, "reconstructed": True})
        elif n:
            points.append({
                "date": iso, "officials": n, "reconstructed": True,
                "compliancePct": round(100 * count_upto(first_done, iso) / n, 1),
                "mandatoryCompletionPct": (round(100 * count_upto(mand_dates, iso) / mand_total, 1)
                                           if mand_total else None),
            })
        day += timedelta(days=1)

    weeks: Dict[str, int] = {}
    week0 = start - timedelta(days=start.weekday())
    for d in all_dates:
        if week0.isoformat() <= d <= end.isoformat():
            day_ = date.fromisoformat(d)
            key = (day_ - timedelta(days=day_.weekday())).isoformat()
            weeks[key] = weeks.get(key, 0) + 1
    activity = []
    wk = week0
    while wk <= end:
        activity.append({"weekStart": wk.isoformat(),
                         "completions": None if 0 < n < SUPPRESS_BELOW else weeks.get(wk.isoformat(), 0)})
        wk += timedelta(days=7)
    return {"points": points, "weeklyCompletions": activity}


# ── Emerging skills: required vs supply vs 36-month forecast ───────────────────

def emerging_skills(
    rows: List[Dict[str, Any]],
    snapshot: Dict[str, Dict[str, Any]],
    hrms: Dict[str, Any],
    names: Dict[str, str],
    population: Dict[str, Any],
    in_scope: Set[str],
    critical: Set[str],
    levels_available: Callable[[str], Set[int]],
    flagged_courses: Dict[str, int],
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Per FRAC competency, over the (filtered) officials in the workforce snapshot:

    * required  — officials whose role profile sets a target level on it;
    * supplyNow — of those, officials whose displayed level already meets the target;
    * expected36 — Σ P(in service in 36 months) × P(θ ≥ own target) with θ decayed
      from the newest dated evidence (workforce_service._p_capable). In service:
      superannuation date after the horizon × (1 − ANNUAL_ATTRITION)^3. No new
      learning is assumed, and the role requirement is held constant — posts
      still need the competency after their holders leave;
    * shortfallNow / shortfall36 = required − supply; `rising` when the 36-month
      shortfall exceeds today's by at least one official.

    Priority = shortfall36 × 1.25 if in GSBPM scope × 1.25 if critical to a
    statistical product. The top EMERGING_SHORTLIST with a shortfall answer
    "what should NSSTA train next year". Counts of 1–4 are suppressed.
    """
    now = now or datetime.now(timezone.utc)
    horizon = (now + timedelta(days=int(EMERGING_HORIZON_MONTHS * 30.4375))).date()
    survive = (1 - ANNUAL_ATTRITION) ** (EMERGING_HORIZON_MONTHS / 12)
    officials = hrms.get("officials", {}) if hrms else {}

    def in_service(uid: str) -> float:
        h = officials.get(uid)
        if h and h.get("superannuationDate") and date.fromisoformat(h["superannuationDate"][:10]) < horizon:
            return 0.0
        return survive

    acc: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        off = snapshot.get(r["userId"])
        if not off:
            continue
        p_stay = in_service(r["userId"])
        for c in off["competencies"]:
            target = c.get("target") or 0
            if target < 1:
                continue
            a = acc.setdefault(c["catalogueId"], {"required": 0, "supplyNow": 0, "expectedNow": 0.0,
                                                  "expected36": 0.0, "retiring": 0, "neededLevels": set(),
                                                  "targets": []})
            a["required"] += 1
            a["targets"].append(target)
            level = c.get("level") or 0
            if level >= target:
                a["supplyNow"] += 1
                if p_stay == 0.0:
                    a["retiring"] += 1
            else:
                a["neededLevels"].update(range(level + 1, target + 1))
            a["expectedNow"] += _p_capable(c, 0, now, population, threshold=target)
            a["expected36"] += p_stay * _p_capable(c, EMERGING_HORIZON_MONTHS, now, population, threshold=target)

    items = []
    for comp, a in acc.items():
        req = a["required"]
        short_now = max(0, req - a["supplyNow"])
        short36 = max(0.0, req - a["expected36"])
        missing_levels = sorted(a["neededLevels"] - set(levels_available(comp)))
        weight = (EMERGING_SCOPE_WEIGHT if comp in in_scope else 1.0) * \
                 (EMERGING_CRITICAL_WEIGHT if comp in critical else 1.0)
        if missing_levels:
            action = f"Commission course(s) at Level {', '.join(map(str, missing_levels))} — none in the catalogue"
        elif flagged_courses.get(comp):
            action = "Review existing courses first — measured uplift is near zero"
        elif short36 >= 1:
            action = "Run an NSSTA cohort programme on existing catalogue courses"
        else:
            action = "Monitor — supply meets the requirement"
        items.append({
            "competencyId": comp, "competencyName": names.get(comp, comp),
            "required": cell(req), "avgTargetLevel": round(mean(a["targets"]), 1),
            "supplyNow": cell(a["supplyNow"]), "expectedSupplyNow": cell(a["expectedNow"]),
            "expectedSupply36": cell(a["expected36"]),
            "retiringCapable": cell(a["retiring"]),
            "shortfallNow": cell(short_now), "shortfall36": cell(short36),
            "coveragePct": None if req < SUPPRESS_BELOW else round(100 * a["supplyNow"] / req),
            "coverage36Pct": None if req < SUPPRESS_BELOW else round(100 * a["expected36"] / req),
            "rising": short36 - short_now >= 1,
            "inScope": comp in in_scope, "critical": comp in critical,
            "missingCatalogueLevels": missing_levels,
            "flaggedCourses": flagged_courses.get(comp, 0),
            "priorityScore": round(short36 * weight, 2),
            "recommendedAction": action,
        })
    items.sort(key=lambda i: (-i["priorityScore"], i["competencyName"]))
    shortlist = [i["competencyId"] for i in items if i["shortfall36"]["value"] != 0][:EMERGING_SHORTLIST]
    for rank, i in enumerate(items, start=1):
        i["rank"] = rank
        i["trainNextYear"] = i["competencyId"] in shortlist
    return {
        "asOf": now.date().isoformat(),
        "horizonMonths": EMERGING_HORIZON_MONTHS,
        "officials": sum(1 for r in rows if r["userId"] in snapshot),
        "items": items,
        "shortlist": shortlist,
        "method": (
            "Required = officials whose role sets a target level on the competency. Supply now = those whose "
            "displayed FRAC level meets it. Expected supply in 36 months = Σ P(in service) × P(θ ≥ target), θ "
            "decayed from the newest dated evidence (half-life 6.5 months accuracy / 12 procedural); in service = "
            f"before superannuation × (1 − {ANNUAL_ATTRITION})^3 other attrition (placeholder rate). No new "
            "learning is assumed and role requirements are held constant. Priority = 36-month shortfall × "
            f"{EMERGING_SCOPE_WEIGHT} if in GSBPM scope × {EMERGING_CRITICAL_WEIGHT} if critical to a product."),
        "suppression": f"Counts of 1–{SUPPRESS_BELOW - 1} officials are shown as <{SUPPRESS_BELOW}.",
    }
