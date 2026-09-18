"""
services/workforce_service.py — admin workforce foresight (SCIL v6 §11)

Pure functions over the workforce SNAPSHOT (every official's resolved
competency rows, built in main._build_workforce_snapshot) and HRMS records:

* capability_risk — per statistical product and each competency critical to
  it: officials on the product team who are capable (displayed FRAC level ≥
  CAPABLE_LEVEL), how many of them retire within 36 months, single-point-of-
  failure flags and a risk band.
* foresight — 36-month projection of the EXPECTED number of capable officials:
  in-service probability (known superannuation dates × annual attrition) ×
  P(θ ≥ CAPABLE_LEVEL) under the dated decay of proficiency_service (no new
  learning assumed).
* tpac_agenda — draft agenda items for the NSSTA Training Programme Advisory
  Committee from catalogue coverage gaps, capability risk, near-zero-uplift
  courses and proposed prerequisites.

Every count of officials in an aggregate is suppressed when it is 1–4
(statistical disclosure control: SUPPRESS_BELOW). Zero is shown. Synthetic data.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from services.proficiency_service import SIGMA_BY_CONFIDENCE, _Phi, decay, months_between

CAPABLE_LEVEL = 3              # FRAC L3: independently carries out the work end to end
SUPPRESS_BELOW = 5             # aggregate cells with 1–4 officials are suppressed
HORIZON_MONTHS = 36
FORESIGHT_MONTHS = (0, 6, 12, 18, 24, 30, 36)
ANNUAL_ATTRITION = 0.03        # transfers / deputation / resignation per year — placeholder, not measured
RISK_ORDER = {"critical": 3, "high": 2, "moderate": 1, "low": 0}


def cell(n: float) -> Dict[str, Any]:
    """A count for an aggregate table: 1–4 are suppressed, 0 and ≥ 5 are shown."""
    n_int = int(round(n))
    if 0 < n_int < SUPPRESS_BELOW:
        return {"value": None, "suppressed": True, "display": f"<{SUPPRESS_BELOW}"}
    return {"value": n_int, "suppressed": False, "display": str(n_int)}


def _as_date(s: str) -> date:
    return date.fromisoformat(s[:10])


def _level(off: Dict[str, Any], comp: str) -> Optional[int]:
    row = next((c for c in off["competencies"] if c["catalogueId"] == comp), None)
    return row["level"] if row else None


def capability_risk(snapshot: Dict[str, Dict[str, Any]], hrms: Dict[str, Any], names: Dict[str, str],
                    today: Optional[date] = None) -> Dict[str, Any]:
    today = today or datetime.now(timezone.utc).date()
    horizon = today + timedelta(days=int(HORIZON_MONTHS * 30.4375))
    officials = hrms.get("officials", {})
    products = hrms.get("products", {})
    critical = hrms.get("productCriticalCompetencies", {})

    out = []
    for pid in sorted(critical):
        team = [uid for uid, h in officials.items() if pid in h.get("products", []) and uid in snapshot]
        rows = []
        for comp in critical[pid]:
            capable = [u for u in team if (_level(snapshot[u], comp) or 0) >= CAPABLE_LEVEL]
            retiring = [u for u in capable if _as_date(officials[u]["superannuationDate"]) <= horizon]
            n, r = len(capable), len(retiring)
            if n == 0:
                risk, why = "critical", "No official on the team is at Level 3+."
            elif n == 1:
                risk, why = "critical", "Single point of failure: one capable official."
            elif r == n:
                risk, why = "critical", "Every capable official retires within 36 months."
            elif n < 3 or r / n >= 0.5:
                risk, why = "high", "Thin bench, or half of it retires within 36 months."
            elif n < SUPPRESS_BELOW:
                risk, why = "moderate", f"Fewer than {SUPPRESS_BELOW} capable officials."
            else:
                risk, why = "low", "Bench of five or more capable officials."
            rows.append({
                "competencyId": comp, "competencyName": names.get(comp, comp),
                "teamSize": cell(len(team)), "capable": cell(n), "retiringWithin36m": cell(r),
                "singlePointOfFailure": n == 1, "risk": risk, "reason": why,
            })
        worst = max(rows, key=lambda x: RISK_ORDER[x["risk"]])["risk"] if rows else "low"
        out.append({"productId": pid, "productName": products.get(pid, pid), "teamSize": cell(len(team)),
                    "risk": worst, "competencies": rows})
    out.sort(key=lambda p: (-RISK_ORDER[p["risk"]], p["productId"]))
    return {
        "asOf": today.isoformat(), "capableLevel": CAPABLE_LEVEL, "horizonMonths": HORIZON_MONTHS,
        "suppression": f"Counts of 1–{SUPPRESS_BELOW - 1} officials are shown as <{SUPPRESS_BELOW}.",
        "products": out,
    }


def _p_capable(row: Dict[str, Any], months_ahead: float, now: datetime,
               population: Dict[str, Any]) -> float:
    conf = row.get("confidence")
    if conf not in SIGMA_BY_CONFIDENCE:
        return 0.0
    pop_mu, pop_sigma, _ = population.get(row["catalogueId"], (2.0, 1.1, 0))
    age = months_between(row["lastEvidenceDate"], now) if row.get("lastEvidenceDate") else None
    mu, sigma = row["mu"], SIGMA_BY_CONFIDENCE[conf]
    if age is not None:
        mu, sigma, _ = decay(mu, sigma, age + months_ahead, row.get("decayClass", "procedural"),
                             pop_mu, pop_sigma)
    return 1.0 - _Phi((CAPABLE_LEVEL - mu) / sigma)


def foresight(snapshot: Dict[str, Dict[str, Any]], hrms: Dict[str, Any], names: Dict[str, str],
              population: Dict[str, Any], now: Optional[datetime] = None) -> Dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    officials = hrms.get("officials", {})
    critical = hrms.get("productCriticalCompetencies", {})
    series = []
    for pid in sorted(critical):
        team = [uid for uid, h in officials.items() if pid in h.get("products", []) and uid in snapshot]
        for comp in critical[pid]:
            points, attrition_only = [], []
            for m in FORESIGHT_MONTHS:
                when = (now + timedelta(days=int(m * 30.4375))).date()
                expected = retained = 0.0
                for uid in team:
                    in_service = _as_date(officials[uid]["superannuationDate"]) >= when
                    if not in_service:
                        continue
                    survive = (1 - ANNUAL_ATTRITION) ** (m / 12)
                    row = next((c for c in snapshot[uid]["competencies"] if c["catalogueId"] == comp), None)
                    if row is None:
                        continue
                    expected += survive * _p_capable(row, m, now, population)
                    retained += survive * (1.0 if (row["level"] or 0) >= CAPABLE_LEVEL else 0.0)
                points.append({"month": m, "expectedCapable": cell(expected)})
                attrition_only.append({"month": m, "expectedCapable": cell(retained)})
            e0 = points[0]["expectedCapable"]["value"]
            e36 = points[-1]["expectedCapable"]["value"]
            series.append({
                "productId": pid, "competencyId": comp, "competencyName": names.get(comp, comp),
                "withDecay": points, "attritionOnly": attrition_only,
                "declining": (e0 or 0) > (e36 or 0) or points[-1]["expectedCapable"]["suppressed"],
            })
    return {
        "asOf": now.date().isoformat(), "months": list(FORESIGHT_MONTHS), "capableLevel": CAPABLE_LEVEL,
        "annualAttrition": ANNUAL_ATTRITION,
        "method": ("Expected capable officials = Σ over the product team of P(in service at t) × "
                   f"P(θ ≥ {CAPABLE_LEVEL}) with θ decayed toward the population mean from the newest dated "
                   "evidence (half-life 6.5 months accuracy / 12 months procedural). In service: before the "
                   f"superannuation date, × (1 − {ANNUAL_ATTRITION})^years other attrition (placeholder rate). "
                   "'Attrition only' counts today's Level-3+ officials who stay. No new learning is assumed."),
        "suppression": f"Values that round to 1–{SUPPRESS_BELOW - 1} are shown as <{SUPPRESS_BELOW}.",
        "series": series,
    }


def tpac_agenda(
    snapshot: Dict[str, Dict[str, Any]], engine, names: Dict[str, str], risk: Dict[str, Any],
    forecast: Dict[str, Any], uplift: Optional[Dict[str, Any]], suggestions: Optional[Dict[str, Any]],
    in_scope: Optional[set] = None,
) -> Dict[str, Any]:
    """Draft TPAC agenda items. Drafts for a committee to discuss — nothing is decided here."""
    in_scope = in_scope or set()
    critical = {c for p in risk.get("products", []) for c in (r["competencyId"] for r in p["competencies"])}
    items: List[Dict[str, Any]] = []

    # 1. Catalogue coverage gaps with demand
    for comp in sorted(engine._frac_map if engine else []):
        have = engine.levels_available(comp)
        for level in range(1, 6):
            if level in have:
                continue
            demand = sum(1 for off in snapshot.values() for c in off["competencies"]
                         if c["catalogueId"] == comp and c["target"] >= level
                         and (c["level"] is None or c["level"] < level))
            if not demand:
                continue
            priority = "high" if comp in critical or comp in in_scope else "medium"
            items.append({
                "type": "coverage_gap", "priority": priority,
                "title": f"Commission a Level-{level} course on {names.get(comp, comp)}",
                "rationale": (f"No catalogue course at Level {level}; officials who still need to reach it: "
                              f"{cell(demand)['display']}."
                              + (" Critical to a statistical product." if comp in critical else "")
                              + (" In GSBPM scope." if comp in in_scope else "")),
                "competencyId": comp, "level": level, "demand": cell(demand),
            })

    # 2. Capability risk, with the 36-month projection
    proj = {(s["productId"], s["competencyId"]): s for s in forecast.get("series", [])}
    for p in risk.get("products", []):
        for r in p["competencies"]:
            if r["risk"] not in ("critical", "high"):
                continue
            s = proj.get((p["productId"], r["competencyId"]))
            end = s["withDecay"][-1]["expectedCapable"]["display"] if s else "?"
            items.append({
                "type": "capability_risk", "priority": "high" if r["risk"] == "critical" else "medium",
                "title": f"Build bench strength in {r['competencyName']} for {p['productName']}",
                "rationale": (f"{r['reason']} Capable now: {r['capable']['display']}; expected capable in 36 "
                              f"months without new training: {end}. Consider an NSSTA TPAC programme and "
                              f"nominations from the {p['productId']} team."),
                "productId": p["productId"], "competencyId": r["competencyId"], "risk": r["risk"],
            })

    # 3. Courses whose measured uplift is ~0
    for c in (uplift or {}).get("courses", []):
        if c.get("misTagFlag"):
            items.append({
                "type": "ineffective_course", "priority": "medium",
                "title": f"Review or replace “{c['title']}”",
                "rationale": (f"Measured uplift {c['measuredUplift']:+.2f} levels (95% CI {c['ci95'][0]:+.2f} to "
                              f"{c['ci95'][1]:+.2f}, {c['n']} learners) despite its FRAC tag and a "
                              f"{c.get('rating') or '—'} rating. Check content against the tag."),
                "courseId": c["courseId"], "competencyId": c["competencyId"],
            })

    # 4. Data-suggested prerequisites awaiting expert review
    for s in (suggestions or {}).get("suggestions", []):
        if s["status"] == "new_suggestion":
            items.append({
                "type": "prerequisite_review", "priority": "low",
                "title": (f"Review proposed prerequisite: {s['from']['competencyName']} L{s['from']['level']} "
                          f"before {s['to']['competencyName']} L{s['to']['level']}"),
                "rationale": (f"Learners who did it first gained {s['effect']:+.2f} levels more "
                              f"(95% CI {s['ci95'][0]:+.2f} to {s['ci95'][1]:+.2f}); observational, not applied."),
            })

    rank = {"high": 0, "medium": 1, "low": 2}
    items.sort(key=lambda i: (rank[i["priority"]], i["type"], i["title"]))
    for n, item in enumerate(items, start=1):
        item["id"] = f"TPAC-{n:03d}"
        item["status"] = "draft"
    return {"items": items, "counts": {t: sum(i["type"] == t for i in items)
                                        for t in ("coverage_gap", "capability_risk", "ineffective_course",
                                                  "prerequisite_review")},
            "note": "Draft agenda generated from synthetic data for committee discussion — nothing here is decided."}
