"""
Admin console aggregates (services/admin_analytics.py): filters, pagination,
KPIs, mandatory progress, trend points with small-cell suppression, and the
emerging-skills required-vs-supply-vs-forecast ranking.

    pytest tests/test_admin_analytics.py
"""
from datetime import datetime, timezone

from services import admin_analytics as aa

NOW = datetime(2026, 9, 15, tzinfo=timezone.utc)


def _user(i, dept="NAD", grade="TIER3_MID", office="off_nad", status=2, mandatory=(1, 1), comps=None):
    done, total = mandatory
    return aa.normalise({
        "userId": f"usr_{i}", "govId": f"EMP-{i}", "firstName": f"F{i}", "lastName": "L",
        "department": dept, "grade": grade, "officeId": office, "officeName": office.upper(),
        "enrollmentStatus": status, "missingSkill": None,
        "competencies": comps or [], "completedCourseIds": [],
        "mandatory": {"cycle": "FY", "total": total, "completed": done,
                      "pending": [{"courseId": f"c{k}", "title": f"C{k}"} for k in range(total - done)]},
    })


def test_filters_combine_and_facets_count_the_whole_roster():
    rows = [_user(1), _user(2, dept="PSD"), _user(3, dept="PSD", grade="TIER1_APEX", office="off_psd")]
    assert [r["userId"] for r in aa.apply_filters(rows, aa.Filters(department="PSD"))] == ["usr_2", "usr_3"]
    assert [r["userId"] for r in aa.apply_filters(rows, aa.Filters("PSD", "TIER1_APEX", "off_psd"))] == ["usr_3"]
    f = aa.facets(rows)
    assert {d["value"]: d["count"] for d in f["departments"]} == {"NAD": 1, "PSD": 2}
    assert f["grades"][0]["value"] == "TIER1_APEX" and f["grades"][0]["label"].startswith("Tier 1")


def test_paginate_clamps_page_and_reports_totals():
    p = aa.paginate(list(range(23)), page=9, page_size=10)
    assert p["page"] == 3 and p["totalPages"] == 3 and p["items"] == [20, 21, 22] and p["total"] == 23
    assert aa.paginate([], 1, 10)["totalPages"] == 1


def test_kpis_and_mandatory_progress():
    rows = [_user(1, status=2, mandatory=(2, 2)), _user(2, status=0, mandatory=(0, 2)),
            _user(3, status=1, mandatory=(1, 2))]
    k = aa.kpis(rows)
    assert k["totalOfficials"] == 3 and k["trainingCompliancePct"] == 33
    assert k["mandatory"]["behind"] == 2
    assert k["mandatory"]["completionPct"] == 50.0
    assert aa.is_behind_mandatory(rows[1]) and not aa.is_behind_mandatory(rows[0])


def test_heatmap_weights_planned_over_in_progress():
    comps = [{"name": "A", "status": "PLANNED", "competencyLevel": "Level 1"},
             {"name": "B", "status": "IN_PROGRESS", "competencyLevel": "Level 1"},
             {"name": "C", "status": "ACQUIRED", "competencyLevel": "Level 1"}]
    h = aa.heatmap([_user(1, comps=comps)])
    assert [e["competency"] for e in h] == ["A", "B"]
    assert h[0]["gap"] == 4.5 and h[1]["gap"] == 3.0


def test_department_compliance_suppresses_small_departments():
    rows = [_user(i) for i in range(6)] + [_user(10, dept="Tiny", status=0)]
    d = {x["dept"]: x for x in aa.dept_compliance(rows)}
    assert d["NAD"]["pct"] == 100 and not d["NAD"]["suppressed"]
    assert d["Tiny"]["pct"] is None and d["Tiny"]["suppressed"]


def test_trend_point_uses_the_most_specific_breakdown_and_suppresses_small_groups():
    rows = [_user(i) for i in range(6)] + [_user(i, dept="PSD", office="off_psd") for i in range(10, 13)]
    stored = aa.daily_metrics(rows, snapshot=None)
    assert stored["overall"]["officials"] == 9 and stored["overall"]["avgLevel"] is None
    p = aa.trend_point("2026-09-15", stored, aa.Filters(department="NAD"))
    assert p["officials"] == 6 and p["compliancePct"] == 100
    small = aa.trend_point("2026-09-15", stored, aa.Filters(department="NAD", office="off_psd"))
    assert small == {"date": "2026-09-15", "officials": 3, "suppressed": True,   # office wins; 3 < 5
                     "reconstructed": False}
    assert aa.trend_point("2026-09-15", stored, aa.Filters(department="Nope")) is None


def _snap_row(level, target, mu, conf="HIGH", last="2026-09-01"):
    return {"catalogueId": "comp_x", "competencyId": "comp_x", "level": level, "target": target,
            "confidence": conf, "mu": mu, "lastEvidenceDate": last, "decayClass": "procedural"}


def test_emerging_skills_forecasts_shortfall_from_retirement_and_ranks_by_priority():
    rows = [_user(i) for i in range(8)]
    snapshot = {r["userId"]: {"competencies": [_snap_row(3, 3, 3.6)]} for r in rows}
    # Half the capable bench retires within 36 months.
    hrms = {"officials": {f"usr_{i}": {"superannuationDate": "2027-06-30" if i < 4 else "2045-01-31"}
                          for i in range(8)}}
    out = aa.emerging_skills(rows, snapshot, hrms, {"comp_x": "Index Numbers"}, {"comp_x": (2.0, 1.0, 8)},
                             in_scope={"comp_x"}, critical=set(), levels_available=lambda c: {1, 2, 3},
                             flagged_courses={}, now=NOW)
    item = out["items"][0]
    assert item["required"]["value"] == 8 and item["supplyNow"]["value"] == 8
    assert item["shortfallNow"]["value"] == 0
    assert item["expectedSupply36"]["value"] is None or item["expectedSupply36"]["value"] <= 4
    assert item["rising"] and item["trainNextYear"] and out["shortlist"] == ["comp_x"]
    assert item["retiringCapable"]["display"] == "<5"
    assert item["priorityScore"] > 0 and item["inScope"]


def test_emerging_skills_recommends_commissioning_missing_catalogue_levels():
    rows = [_user(i) for i in range(5)]
    snapshot = {r["userId"]: {"competencies": [_snap_row(1, 4, 1.0)]} for r in rows}
    out = aa.emerging_skills(rows, snapshot, {}, {}, {}, set(), set(), lambda c: {1, 2}, {}, now=NOW)
    item = out["items"][0]
    assert item["missingCatalogueLevels"] == [3, 4]
    assert item["recommendedAction"].startswith("Commission")
    assert item["shortfallNow"]["value"] == 5 and item["coveragePct"] == 0


def test_reconstructed_history_follows_dated_completions():
    from datetime import date
    rows = [_user(i) for i in range(5)]
    for i, r in enumerate(rows):
        r["completions"] = {"do_x": f"2026-09-0{i + 1}"}             # first completions on 1st…5th Sept
        r["mandatory"] = {"total": 1, "completed": 1 if i == 0 else 0, "courseIds": ["do_x" if i == 0 else "do_m"],
                          "pending": []}
    out = aa.reconstruct_history(rows, date(2026, 8, 31), date(2026, 9, 5))
    pts = {p["date"]: p for p in out["points"]}
    assert len(pts) == 6 and all(p["reconstructed"] for p in pts.values())
    assert pts["2026-08-31"]["compliancePct"] == 0 and pts["2026-09-03"]["compliancePct"] == 60
    assert pts["2026-09-05"]["compliancePct"] == 100
    assert pts["2026-08-31"]["mandatoryCompletionPct"] == 0 and pts["2026-09-01"]["mandatoryCompletionPct"] == 20
    assert out["weeklyCompletions"] == [{"weekStart": "2026-08-31", "completions": 5}]
    small = aa.reconstruct_history(rows[:3], date(2026, 9, 1), date(2026, 9, 1))
    assert small["points"][0]["suppressed"] and small["weeklyCompletions"][0]["completions"] is None
