"""
Mock-data quality metrics — run before/after regenerating mock data.

    cd main-lms-backend
    python -m scripts.mock_data_metrics                 # offline + live (servers up)
    python -m scripts.mock_data_metrics --offline       # catalogue-only metrics
    python -m scripts.mock_data_metrics --out FILE.json

Offline (engine built from the catalogue the backend would use):
  * tag-support rate: share of (course, competency) tags whose course text is
    closer to the competency than the median UNtagged course
    (HybridRecommendationEngine._tag_support_threshold — the existing check)
  * L1–L5 ladder coverage per catalogue competency
  * duration distribution (overall and per `format` when the field exists)

Live (needs mock :8001 and backend :8000; logs in as admin/admin123):
  * share of served role competencies whose id is a catalogue id
  * crosswalk method mix
  * /pathway status mix + totalHours over N users
  * dashboard-vs-recommendations gap mismatches and level-gate violations
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import statistics
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

MOCK = os.getenv("IGOT_MOCK_BASE_URL", "http://localhost:8001")
API = "http://localhost:8000"
HDR = {"x-authenticated-user-token": os.getenv("IGOT_MOCK_TOKEN", "mock-api-key-2026")}


def _pct(values, q):
    return round(float(np.percentile(values, q)), 2) if values else None


def offline_metrics(catalog: list | None = None) -> dict:
    from services.recommendation_service import HybridRecommendationEngine
    eng = HybridRecommendationEngine(catalog=catalog) if catalog is not None else HybridRecommendationEngine()

    supported = total = 0
    per_comp_unsupported = collections.Counter()
    for comp_id, idxs in eng._comp_index.items():
        if comp_id not in eng._frac_map:
            continue
        q_emb, _ = eng._query_signals(comp_id, f"{eng._frac_map[comp_id]['name']}. "
                                               f"{eng._frac_map[comp_id]['description']}".strip())
        thr = eng._tag_support_threshold(comp_id, q_emb)
        for i in idxs:
            total += 1
            if float(eng._embeddings[i] @ q_emb[0]) > thr:
                supported += 1
            else:
                per_comp_unsupported[comp_id] += 1

    ladder = {}
    for comp_id in eng._frac_map:
        lv = eng.levels_available(comp_id)
        counts = collections.Counter(
            eng._catalog[i].comp_levels.get(comp_id) for i in eng._comp_index.get(comp_id, [])
        )
        ladder[comp_id] = {"levels": sorted(lv), "missing": [l for l in range(1, 6) if l not in lv],
                           "perLevel": {str(l): counts.get(l, 0) for l in range(1, 6)}}
    full = sum(1 for v in ladder.values() if not v["missing"])

    durs = [d.duration_hrs for d in eng._catalog]
    by_fmt = collections.defaultdict(list)
    raw = catalog
    if raw is None:
        from services.recommendation_service import _DEFAULT_CATALOG
        with open(os.path.normpath(_DEFAULT_CATALOG), encoding="utf-8") as fh:
            raw = json.load(fh)
        if isinstance(raw, dict):
            raw = raw.get("content", [])
    for item, doc in zip(raw, eng._catalog):
        by_fmt[item.get("format") or "unspecified"].append(doc.duration_hrs)

    return {
        "courses": len(eng._catalog),
        "catalogueCompetencies": len(eng._frac_map),
        "tags": total,
        "tagSupportRate": round(supported / total, 3) if total else None,
        "unsupportedTags": total - supported,
        "fullLadderCompetencies": full,
        "competenciesMissingL1": sum(1 for v in ladder.values() if 1 in v["missing"]),
        "competenciesWithHoles": {k: v["missing"] for k, v in ladder.items() if v["missing"]},
        "durationHours": {"min": round(min(durs), 2), "median": _pct(durs, 50),
                          "p90": _pct(durs, 90), "max": round(max(durs), 2)},
        "durationHoursByFormat": {
            f: {"n": len(v), "min": round(min(v), 2), "median": _pct(v, 50), "p90": _pct(v, 90),
                "max": round(max(v), 2)}
            for f, v in sorted(by_fmt.items())
        },
    }


_AUTH: dict = {}


def _login() -> dict:
    """Admin bearer header; retried while the backend (--reload) restarts."""
    import time
    import httpx
    for attempt in range(12):
        try:
            tok = httpx.post(f"{API}/auth/login", data={"username": "admin", "password": "admin123"},
                             timeout=30).json()["access_token"]
            _AUTH.update({"Authorization": f"Bearer {tok}"})
            return _AUTH
        except (httpx.TransportError, KeyError, ValueError):
            if attempt == 11:
                raise
            time.sleep(10)


def _get(url: str, headers: dict | None = None):
    """GET with retries — the dev backend runs with --reload and may restart
    mid-run, and the admin access token expires during long runs (→ re-login)."""
    import time
    import httpx
    for attempt in range(6):
        try:
            resp = httpx.get(url, timeout=180, headers=headers)
            if resp.status_code == 401 and headers is _AUTH:
                _login()
                continue
            resp.raise_for_status()
            return resp.json()
        except (httpx.TransportError, httpx.HTTPStatusError):
            if attempt == 5:
                raise
            time.sleep(10)
    raise RuntimeError(f"GET {url} kept failing")


def live_metrics(n_users: int = 20) -> dict:
    import httpx
    roster = _get(f"{MOCK}/api/admin/v1/users", headers=HDR)["result"]["users"]
    frac = _get(f"{MOCK}/api/frac/competencies", headers=HDR)["result"]
    catalogue_ids = set()
    try:
        from services.recommendation_service import _DEFAULT_FRAC
        with open(os.path.normpath(_DEFAULT_FRAC), encoding="utf-8") as fh:
            fr = json.load(fh)
        catalogue_ids = {c["id"] for c in (fr["competencies"] if isinstance(fr, dict) else fr)}
    except Exception:
        pass

    served = [c for u in roster for c in (u.get("competencies") or [])]
    in_cat = sum(1 for c in served if c.get("id") in catalogue_ids)

    auth = _login()

    users = [u["userId"] for u in roster][:n_users]
    status_mix = collections.Counter()
    xw_mix = collections.Counter()
    hours, plan_hours, mismatches, gate_violations = [], [], 0, 0
    no_content_comps = collections.Counter()
    opp_mix = collections.Counter()
    plan_steps = tie_breaks = mandatory_steps = 0
    prereq_mix = collections.Counter()
    for uid in users:
        sg = _get(f"{API}/api/v1/learner/{uid}/skill-gaps", headers=auth)
        rec = _get(f"{API}/api/v1/learner/{uid}/recommendations", headers=auth)
        pw = _get(f"{API}/api/v1/learner/{uid}/pathway?unbudgeted=true", headers=auth)
        dash = {g["competencyId"]: (g["currentLevel"], g["targetLevel"]) for g in sg.get("skillGaps", [])}
        for g in rec.get("skillGaps", []):
            cur, tgt = dash.get(g["competencyId"], (None, None))
            if cur is None or int(g["currentLevel"]) != cur or int(g["targetLevel"]) != tgt:
                mismatches += 1
        gap_cur = {g["competencyId"]: g["currentLevel"] for g in rec.get("skillGaps", [])}
        for r in rec.get("recommendations", []):
            lvl, cur = r.get("courseLevel"), gap_cur.get(r["competencyId"])
            if lvl is not None and cur is not None and lvl <= cur:
                gate_violations += 1
        for g in sg.get("skillGaps", []):
            xw_mix[(g.get("crosswalk") or {}).get("method", "none")] += 1
            if g.get("gapScore"):
                opp_mix[(g.get("opportunity") or {}).get("level", "none")] += 1
        for a in pw.get("studyPlan", {}).get("prerequisitesApplied", []):
            prereq_mix[a["status"]] += 1
        mandatory_steps += sum(1 for s in pw.get("studyPlan", {}).get("steps", []) if s.get("mandatory"))
        for s in pw.get("studyPlan", {}).get("steps", []):
            plan_steps += 1
            tie_breaks += s.get("selectedBy") == "opportunity_tie_break"
        for p in pw.get("pathways", []):
            status_mix[p["status"]] += 1
            if p["status"] == "no_content":
                no_content_comps[p["catalogueCompetencyId"]] += 1
            if p["status"] in ("ready", "partial"):
                hours.append(p["totalHours"])
        plan_hours.append(pw.get("studyPlan", {}).get("totalHours", 0))

    return {
        "rosterUsers": len(roster),
        "fracServed": frac.get("count"),
        "servedRoleCompetencies": len(served),
        "servedInCatalogueShare": round(in_cat / len(served), 3) if served else None,
        "usersSampled": len(users),
        "crosswalkMethodMix": dict(xw_mix),
        "opportunityMixOnGaps": dict(opp_mix),
        "studyPlanSteps": plan_steps,
        "opportunityTieBreaks": tie_breaks,
        "mandatoryPlanSteps": mandatory_steps,
        "prerequisiteEffects": dict(prereq_mix),
        "pathwayStatusMix": dict(status_mix),
        "noContentCompetencies": dict(no_content_comps),
        "pathwayTotalHours": {"n": len(hours), "min": min(hours) if hours else None,
                              "median": _pct(hours, 50), "p90": _pct(hours, 90),
                              "max": max(hours) if hours else None},
        "studyPlanTotalHours": {"median": _pct(plan_hours, 50), "max": max(plan_hours) if plan_hours else None},
        "dashboardVsRecommendationMismatches": mismatches,
        "levelGateViolations": gate_violations,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--users", type=int, default=20)
    ap.add_argument("--out")
    args = ap.parse_args()
    out = {"offline": offline_metrics()}
    if not args.offline:
        out["live"] = live_metrics(args.users)
    text = json.dumps(out, indent=2)
    print(text)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)


if __name__ == "__main__":
    main()
