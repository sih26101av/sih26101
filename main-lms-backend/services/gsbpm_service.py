"""
services/gsbpm_service.py — GSBPM scoping (SCIL v6 §1) + opportunity to practise (§4)

Two computed, auditable outputs over synthetic reference data:

1. scope_report — the 80% officer-hours rule. Rank GSBPM sub-processes by the
   officer-hours offices spend on them this cycle, take the smallest set that
   covers SCOPE_OFFICER_HOURS_SHARE of all hours ("core" sub-processes), and
   put a competency in scope if it is exercised in at least one of them. The
   report says which sub-processes and how many hours justify each decision;
   nothing is a hard-coded count.

2. opportunity — for one official's office and one competency: the share of the
   office's officer-hours spent in the sub-processes where the competency is
   exercised → Low / Medium / High. It is a badge and an ORDINAL tie-breaker
   in the study plan (see recommendation_service.build_study_plan). It is never
   a score multiplier and never hides a gap.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

# Share of all officer-hours the "core" GSBPM sub-processes must cover (SCIL v6 §1's 80% rule).
SCOPE_OFFICER_HOURS_SHARE = 0.80
# Opportunity bands: share of the office's officer-hours in the competency's sub-processes.
# ≥20% ≈ one working day a week or more; 5–20% ≈ a few days a month; <5% ≈ rarely.
OPPORTUNITY_HIGH_SHARE = 0.20
OPPORTUNITY_MEDIUM_SHARE = 0.05
OPPORTUNITY_RANK = {"High": 3, "Medium": 2, "Low": 1}


def subprocess_hours(offices: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    hours: Dict[str, int] = {}
    for office in offices:
        for sp in office.get("subprocesses", []):
            hours[sp["id"]] = hours.get(sp["id"], 0) + int(sp.get("officerHours") or 0)
    return hours


def _sp_name(gsbpm: Dict[str, Any], sid: str) -> str:
    return (gsbpm.get("subprocesses", {}).get(sid) or {}).get("name", sid)


def scope_report(
    gsbpm: Dict[str, Any],
    offices: Dict[str, Dict[str, Any]],
    names: Optional[Dict[str, str]] = None,
    share: float = SCOPE_OFFICER_HOURS_SHARE,
    office_id: Optional[str] = None,
    cycle: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Which competencies are in scope under the officer-hours rule, and why."""
    names = names or {}
    pool = [offices[office_id]] if office_id else list(offices.values())
    hours = subprocess_hours(pool)
    total = sum(hours.values())

    ranked = sorted(hours.items(), key=lambda kv: (-kv[1], kv[0]))
    core: List[Dict[str, Any]] = []
    cumulative = 0
    for sid, h in ranked:
        if total and cumulative >= share * total:
            break
        cumulative += h
        core.append({"id": sid, "name": _sp_name(gsbpm, sid), "officerHours": h,
                     "share": round(h / total, 4) if total else 0.0,
                     "cumulativeShare": round(cumulative / total, 4) if total else 0.0})
    core_ids = {c["id"] for c in core}

    comps = []
    for cid, subs in sorted(gsbpm.get("competencies", {}).items()):
        in_core = [s for s in subs if s in core_ids]
        covered = sum(hours.get(s, 0) for s in in_core)
        name = names.get(cid, cid)
        if in_core:
            reason = (f"Exercised in {len(in_core)} core sub-process(es) — "
                      + ", ".join(f"{s} {_sp_name(gsbpm, s)}" for s in in_core)
                      + f" — {covered / total:.0%} of officer-hours.")
        else:
            reason = ("Only exercised in " + ", ".join(f"{s} {_sp_name(gsbpm, s)}" for s in subs)
                      + f", outside the sub-processes that make up {share:.0%} of officer-hours.")
        comps.append({
            "competencyId": cid, "competencyName": name, "inScope": bool(in_core),
            "subprocesses": subs, "coreSubprocesses": in_core,
            "officerHours": covered, "share": round(covered / total, 4) if total else 0.0,
            "reason": reason,
        })
    comps.sort(key=lambda c: (not c["inScope"], -c["share"], c["competencyId"]))

    return {
        "cycle": cycle or {},
        "officeId": office_id,
        "threshold": share,
        "totalOfficerHours": total,
        "coreSubprocesses": core,
        "coreShare": round(cumulative / total, 4) if total else 0.0,
        "inScopeCount": sum(c["inScope"] for c in comps),
        "outOfScopeCount": sum(not c["inScope"] for c in comps),
        "competencies": comps,
        "method": (f"GSBPM sub-processes ranked by officer-hours; the smallest set covering "
                   f"{share:.0%} of hours is 'core'; a competency is in scope if it is exercised in "
                   f"a core sub-process (SCIL v6 §1). Computed on synthetic office workload data."),
    }


def opportunity(
    office: Optional[Dict[str, Any]],
    comp_subprocesses: List[str],
    gsbpm: Dict[str, Any],
    cycle: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Opportunity to practise a competency in the official's office this cycle (SCIL v6 §4)."""
    if not office or not comp_subprocesses:
        return None
    total = int(office.get("totalOfficerHours") or 0) or sum(
        int(s.get("officerHours") or 0) for s in office.get("subprocesses", []))
    wanted = set(comp_subprocesses)
    hits = [s for s in office.get("subprocesses", []) if s["id"] in wanted]
    covered = sum(int(s.get("officerHours") or 0) for s in hits)
    frac = covered / total if total else 0.0
    level = ("High" if frac >= OPPORTUNITY_HIGH_SHARE else
             "Medium" if frac >= OPPORTUNITY_MEDIUM_SHARE else "Low")
    return {
        "level": level,
        "share": round(frac, 4),
        "officerHours": covered,
        "officeId": office.get("officeId"),
        "officeName": office.get("name"),
        "cycle": (cycle or {}).get("label") or office.get("cycle"),
        "subprocesses": [{"id": s["id"], "name": _sp_name(gsbpm, s["id"]),
                          "officerHours": s.get("officerHours")} for s in hits],
    }
