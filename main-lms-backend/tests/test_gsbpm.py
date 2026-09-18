"""
GSBPM scoping (SCIL v6 §1) and opportunity to practise (§4).

    pytest tests/test_gsbpm.py
"""
import json
import os

from services import gsbpm_service as gs

GSBPM = {
    "subprocesses": {"4.3": {"name": "Run collection"}, "5.3": {"name": "Review and validate"},
                     "7.2": {"name": "Produce dissemination products"}, "OA.FM": {"name": "Finance"}},
    "competencies": {"c_collect": ["4.3"], "c_finance": ["OA.FM"], "c_publish": ["7.2", "5.3"],
                     "c_nowhere": ["2.4"]},
}
OFFICE = {"officeId": "off_x", "name": "X", "totalOfficerHours": 100, "subprocesses": [
    {"id": "4.3", "officerHours": 60}, {"id": "5.3", "officerHours": 25},
    {"id": "7.2", "officerHours": 10}, {"id": "OA.FM", "officerHours": 5}]}


def test_core_is_the_smallest_set_reaching_80_percent_of_hours():
    rep = gs.scope_report(GSBPM, {"off_x": OFFICE})
    assert [c["id"] for c in rep["coreSubprocesses"]] == ["4.3", "5.3"]
    assert rep["coreShare"] == 0.85 and rep["threshold"] == gs.SCOPE_OFFICER_HOURS_SHARE
    scope = {c["competencyId"]: c["inScope"] for c in rep["competencies"]}
    assert scope == {"c_collect": True, "c_publish": True, "c_finance": False, "c_nowhere": False}
    publish = next(c for c in rep["competencies"] if c["competencyId"] == "c_publish")
    assert publish["coreSubprocesses"] == ["5.3"] and "25%" in publish["reason"]
    assert rep["inScopeCount"] == 2 and rep["outOfScopeCount"] == 2


def test_scope_threshold_is_a_parameter_not_a_count():
    rep = gs.scope_report(GSBPM, {"off_x": OFFICE}, share=0.5)
    assert [c["id"] for c in rep["coreSubprocesses"]] == ["4.3"]


def test_opportunity_bands_follow_the_office_hour_share():
    lvl = lambda subs: gs.opportunity(OFFICE, subs, GSBPM)["level"]
    assert lvl(["4.3"]) == "High"          # 60%
    assert lvl(["7.2"]) == "Medium"        # 10%
    assert lvl(["OA.FM"]) == "Medium"      # 5% (boundary is inclusive)
    assert lvl(["2.4"]) == "Low"           # the office doesn't run it
    opp = gs.opportunity(OFFICE, ["7.2", "5.3"], GSBPM)
    assert opp["share"] == 0.35 and {s["id"] for s in opp["subprocesses"]} == {"7.2", "5.3"}
    assert gs.opportunity(None, ["4.3"], GSBPM) is None


def test_generated_reference_data_scopes_most_competencies():
    data = os.path.join(os.path.dirname(__file__), "..", "..", "mock-igot-server", "data")
    with open(os.path.join(data, "gsbpm_map.json"), encoding="utf-8") as fh:
        gsbpm = json.load(fh)
    with open(os.path.join(data, "offices.json"), encoding="utf-8") as fh:
        offices = {o["officeId"]: o for o in json.load(fh)["offices"]}
    rep = gs.scope_report(gsbpm, offices)
    assert 0.80 <= rep["coreShare"] < 0.90
    assert 0 < rep["outOfScopeCount"] < rep["inScopeCount"]
    opp = lambda office, comp: gs.opportunity(offices[office], gsbpm["competencies"][comp], gsbpm)["level"]
    # national accounts: practised daily in NAD, hardly at all in a field-operations zone
    assert opp("off_nad", "comp_nat_accounts_001") == "High"
    assert opp("off_fod_north", "comp_nat_accounts_001") == "Low"
