"""
Mock-data generator (mock-igot-server/generate_mock_data.py): determinism,
one id space, enrollment consistency, catalogue shape.

    pytest tests/test_mock_data.py
"""
import collections
import json
import os
import sys

import pytest

MOCK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "mock-igot-server"))
sys.path.insert(0, MOCK_DIR)

import generate_mock_data as gen  # noqa: E402
from mockdata import domain as D  # noqa: E402


@pytest.fixture(scope="module")
def files():
    return gen.generate()


@pytest.fixture(scope="module")
def data(files):
    return {name: json.loads(text) for name, text in files.items()}


def _tags(course):
    return json.loads(course["competencies_v3"])


# ── Determinism ────────────────────────────────────────────────────────────────

def test_generation_is_byte_identical(files):
    assert gen.generate() == files


def test_committed_data_matches_the_generator(files):
    for name, text in files.items():
        with open(os.path.join(gen.DATA_DIR, name), encoding="utf-8", newline="") as fh:
            assert fh.read() == text, f"data/{name} is stale — run python generate_mock_data.py"


def test_every_file_is_labelled_synthetic(data):
    listed = data["MANIFEST.json"]["files"]
    assert set(listed) == set(data) - {"MANIFEST.json"}
    assert all(v["synthetic"] for v in listed.values())
    for name, obj in data.items():
        if isinstance(obj, dict) and name not in ("content_states.json",):
            assert obj["_meta"]["synthetic"] is True, name


# ── One competency id space (A1) ──────────────────────────────────────────────

def test_role_competencies_and_tags_use_catalogue_ids(data):
    frac_ids = {c["id"] for c in data["frac_competencies.json"]}
    assert len(frac_ids) == 40
    for u in data["userdata.json"]:
        assert u["competencies"] == u["profileDetails"]["competencies"]
        assert {c["id"] for c in u["competencies"]} <= frac_ids
        assert 4 <= len(u["competencies"]) <= 8
    for c in data["course_catalog.json"]:
        assert {t["id"] for t in _tags(c)} <= frac_ids


def test_required_levels_follow_the_tier(data):
    by_tier = collections.defaultdict(list)
    for u in data["userdata.json"]:
        by_tier[u["jobProfile"]["tier"]] += [c["requiredLevel"] for c in u["competencies"]]
    junior = by_tier["TIER4_JUNIOR"]
    assert sum(2 <= r <= 3 for r in junior) / len(junior) >= 0.9
    senior = by_tier["TIER2_SENIOR"] + by_tier["TIER1_APEX"]
    assert sum(3 <= r <= 5 for r in senior) / len(senior) >= 0.95


def test_self_reports_are_noisy_with_gaps_and_overclaimers(data):
    truth = data["_truth/planted_effects.json"]
    comps = [(u["userId"], c) for u in data["userdata.json"] for c in u["competencies"]]
    missing = sum("competencyLevel" not in c for _, c in comps) / len(comps)
    assert 0.07 <= missing <= 0.15
    assert 0.05 <= len(truth["overclaimers"]) / len(data["userdata.json"]) <= 0.16
    close = [abs(int(c["competencyLevel"][-1]) - truth["trueLevels"][uid][c["id"]]["trueLevel"]) <= 1
             for uid, c in comps if "competencyLevel" in c and uid not in truth["overclaimers"]]
    assert sum(close) / len(close) >= 0.95


def test_roles_and_offices_are_consistent(data):
    roles = {r["roleId"]: r for r in data["roles.json"]["roles"]}
    offices = {o[0] for o in D.OFFICES}
    for u in data["userdata.json"]:
        role = roles[u["jobProfile"]["roleId"]]
        assert u["jobProfile"]["officeId"] == role["officeId"] in offices
        assert [c["id"] for c in u["competencies"]] == [c["id"] for c in role["competencies"]]


def test_crosswalk_rules_are_never_marked_confirmed(data):
    maps = data["frac_crosswalk.json"]["mappings"]
    assert len(maps) == 331
    assert not any(m["confirmed"] for m in maps)
    assert all((m["fracId"] is None) == (m["method"] == "none") for m in maps)


# ── Catalogue (A2 / A3) ──────────────────────────────────────────────────────

def test_ladders_are_complete_except_documented_holes(data):
    levels = collections.defaultdict(set)
    for c in data["course_catalog.json"]:
        for t in _tags(c):
            levels[t["id"]].add(int(t["competencyLevel"][-1]))
    holes = {cid: sorted(set(range(1, 6)) - lv) for cid, lv in levels.items() if lv != set(range(1, 6))}
    assert holes == {k: sorted(v) for k, v in D.LADDER_HOLES.items()}
    assert sum(1 for lv in levels.values() if lv == set(range(1, 6))) >= 34


def test_title_level_words_match_the_tag_level(data):
    for c in data["course_catalog.json"]:
        primary = next(t for t in _tags(c) if t["primary"])
        level = int(primary["competencyLevel"][-1])
        assert level == c["level"]
        assert any(c["name"].startswith(w) for w in D.LEVEL_TITLE_WORDS[level]), c["name"]


def test_secondary_tags_are_overlaps_at_compatible_levels(data):
    shared = 0
    for c in data["course_catalog.json"]:
        tags = _tags(c)
        primary = next(t for t in tags if t["primary"])
        for t in tags:
            if t["primary"]:
                continue
            shared += 1
            assert t["id"] in D.OVERLAP[primary["id"]]
            assert int(t["competencyLevel"][-1]) <= int(primary["competencyLevel"][-1])
            assert int(t["competencyLevel"][-1]) not in D.LADDER_HOLES.get(t["id"], [])
    assert shared >= 20


def test_durations_modules_and_modality_are_realistic(data):
    for c in data["course_catalog.json"]:
        hours = int(c["duration"]) / 3600
        lo, hi = D.FORMATS[c["format"]][0]
        assert lo - 1e-9 <= hours <= hi + 1e-9, (c["format"], hours)
        minutes_per_module = hours * 60 / c["leafNodesCount"]
        assert 15 <= minutes_per_module <= 45 or c["leafNodesCount"] == 2
        assert c["modality"] in D.FORMATS[c["format"]][1]
        assert c["is_tpac"] == (c["format"] == "tpac_programme")
        if c["is_tpac"]:
            assert c["creator"] == D.NSSTA_CREATOR


def test_quality_fields_in_range_and_sometimes_missing(data):
    cat = data["course_catalog.json"]
    for c in cat:
        if "rating" in c:
            assert 3.0 <= c["rating"] <= 4.9 and c["rating_count"] >= 1
        if "completion_rate" in c:
            assert 0.25 <= c["completion_rate"] <= 0.9
    for field in ("rating", "enrollment_count", "completion_rate"):
        share = sum(field not in c for c in cat) / len(cat)
        assert 0.05 <= share <= 0.15, field


def test_planted_zero_uplift_courses_look_popular(data):
    by_id = {c["identifier"]: c for c in data["course_catalog.json"]}
    planted = data["_truth/planted_effects.json"]["zeroUpliftCourses"]
    assert len(planted) == gen.N_POPULAR_ZERO_UPLIFT
    for cid in planted:
        assert by_id[cid]["rating"] >= 4.5 and by_id[cid]["enrollment_count"] >= 6000


# ── Enrollments (A5) ─────────────────────────────────────────────────────────

def test_status_and_completion_are_consistent(data):
    for e in data["enrollments.json"]:
        assert (e["status"] == 2) == (e["completionPercentage"] == 100)
        assert ("completedDate" in e) == (e["status"] == 2)
        if e["status"] == 1:
            assert 0 < e["completionPercentage"] < 100 and 0 < e["progress"] < e["leafNodesCount"]
        if e["status"] == 0:
            assert e["completionPercentage"] == 0 and e["progress"] == 0
        if e["status"] == 2:
            assert e["completedDate"] >= e["enrolledDate"]
            assert e["progress"] == e["leafNodesCount"]


def test_enrollments_reference_the_catalogue_and_real_users(data):
    courses = {c["identifier"]: c for c in data["course_catalog.json"]}
    users = {u["userId"] for u in data["userdata.json"]}
    for e in data["enrollments.json"]:
        assert e["courseId"] in courses and e["userId"] in users
        assert e["leafNodesCount"] == courses[e["courseId"]]["leafNodesCount"]
    pairs = [(e["userId"], e["courseId"]) for e in data["enrollments.json"]]
    assert len(pairs) == len(set(pairs))


def test_completions_span_three_years(data):
    dates = sorted(e["completedDate"] for e in data["enrollments.json"] if e["status"] == 2)
    assert dates[0] < "2023-12-31" and dates[-1] > "2026-06-01"
    assert dates[-1] <= gen.REF_DATE.isoformat() + "T23:59:59"


def test_content_states_only_for_in_progress(data):
    in_progress = {f"{e['userId']}|{e['courseId']}|{e['batchId']}"
                   for e in data["enrollments.json"] if e["status"] == 1}
    assert set(data["content_states.json"]) == in_progress


def test_officials_mostly_study_at_or_just_above_their_level(data):
    truth = data["_truth/planted_effects.json"]
    courses = {c["identifier"]: c for c in data["course_catalog.json"]}
    ok = total = 0
    for e in data["enrollments.json"]:
        primary = next(t for t in _tags(courses[e["courseId"]]) if t["primary"])
        t = truth["trueLevels"][e["userId"]].get(primary["id"])
        if t is None:
            continue
        total += 1
        ok += int(primary["competencyLevel"][-1]) <= t["trueLevel"] + 1
    assert ok / total >= 0.97
    assert len(truth["outOfOrder"]) == gen.N_OUT_OF_ORDER
    for plant in truth["outOfOrder"]:
        assert plant["courseLevel"] >= plant["trueLevel"] + 2


def test_acbp_mandatory_courses_are_short_catalogue_courses(data):
    acbp = data["acbp.json"]
    courses = {c["identifier"]: c for c in data["course_catalog.json"]}
    roles = {r["roleId"] for r in data["roles.json"]["roles"]}
    assert set(acbp["roles"]) == roles
    mandatory = acbp["organisationMandatory"] + [m for r in acbp["roles"].values() for m in r["mandatoryCourses"]]
    for m in mandatory:
        c = courses[m["courseId"]]
        assert c["modality"] != "classroom" and m["aparLinked"] is True
        assert any(t["id"] == m["competencyId"] for t in _tags(c))
    users = {u["userId"]: u for u in data["userdata.json"]}
    assert set(acbp["officials"]) == set(users)
    for uid, o in acbp["officials"].items():
        assert o["roleId"] == users[uid]["jobProfile"]["roleId"]
        assert o["learningHoursPerQuarter"] * 4 >= gen.KARMAYOGI_MIN_HOURS_PER_YEAR


def test_expert_prerequisites_are_acyclic_and_use_catalogue_ids(data):
    frac_ids = {c["id"] for c in data["frac_competencies.json"]}
    edges = data["prerequisites.json"]["edges"]
    assert gen.find_cycle(edges) is None
    for e in edges:
        assert {e["from"]["competencyId"], e["to"]["competencyId"]} <= frac_ids
        assert e["source"] == "expert" and e["rationale"]


def test_course_outcomes_are_consistent_with_catalogue_and_roster(data):
    doc = data["course_outcomes.json"]
    courses = {c["identifier"]: c for c in data["course_catalog.json"]}
    done = {(e["userId"], e["courseId"]) for e in data["enrollments.json"] if e["status"] == 2}
    roster = [o for o in doc["outcomes"] if o["learnerId"].startswith("usr_")]
    assert {(o["learnerId"], o["courseId"]) for o in roster} == done          # every roster completion, nothing else
    for o in doc["outcomes"]:
        primary = next(t for t in _tags(courses[o["courseId"]]) if t["primary"])
        assert o["competencyId"] == primary["id"] and o["courseLevel"] == int(primary["competencyLevel"][-1])
        assert o["enrolled"] <= o["completed"]
    assert len(doc["comparisons"]) == 40 * gen.CONTROLS_PER_COMPETENCY
    truth = data["_truth/planted_effects.json"]
    for cid in truth["zeroUpliftCourses"]:
        assert sum(o["courseId"] == cid for o in doc["outcomes"]) >= 20      # popular → enough data
        assert abs(truth["trueUplift"][cid]) < 0.1
    others = [u for c, u in truth["trueUplift"].items() if c not in truth["zeroUpliftCourses"]]
    assert min(others) >= 0.2                                                # most courses help


def test_workplace_evidence_channels_have_the_planted_properties(data):
    rows = data["workplace_evidence.json"]["rows"]
    truth = data["_truth/planted_effects.json"]
    role = {(u["userId"], c["id"]) for u in data["userdata.json"] for c in u["competencies"]}
    sup = [r for r in rows if r["evidenceType"] == "SUPERVISOR_RATING"]
    assert all((r["userId"], r["compId"]) in role and 1 <= r["grantedValue"] <= 5 for r in sup)
    bias = sum(r["grantedValue"] - truth["trueLevels"][r["userId"]][r["compId"]]["theta"] for r in sup) / len(sup)
    assert bias > 0.2                                                   # lenient on average
    ws = [r for r in rows if r["evidenceType"] == "WORK_SAMPLE"]
    assert {r["compId"] for r in ws} <= set(D.WORK_SAMPLE_TASKS)
    assert all(r["meta"]["passed"] == (r["meta"]["score"] >= gen.WORK_SAMPLE_PASS) for r in ws)
    for r in (r for r in rows if r["evidenceType"] == "UTILITY"):
        if r["meta"]["confirmed"]:
            assert r["meta"]["willUse"] and r["grantedValue"] == r["meta"]["courseLevel"]
            assert r["meta"]["due"] <= gen.REF_DATE.isoformat()
        else:
            assert r["grantedValue"] == 0
    assert any(r["evidenceType"] == "PEER_RATING" for r in rows)


def test_hrms_retirement_dates_and_products_are_consistent(data):
    from datetime import date as _date
    hrms = data["hrms.json"]
    users = {u["userId"]: u for u in data["userdata.json"]}
    office_products = {o[0]: set(o[4]) for o in D.OFFICES}
    assert set(hrms["officials"]) == set(users)
    for uid, h in hrms["officials"].items():
        dob, sup = _date.fromisoformat(h["dateOfBirth"]), _date.fromisoformat(h["superannuationDate"])
        assert sup.year == dob.year + gen.RETIREMENT_AGE and sup.month == dob.month
        assert (sup.replace(day=1) + __import__("datetime").timedelta(days=32)).replace(day=1) \
            - __import__("datetime").timedelta(days=1) == sup                     # last day of the month
        assert sup > gen.REF_DATE                                                  # everyone still in service
        assert set(h["products"]) <= office_products[users[uid]["jobProfile"]["officeId"]]
    assert set(hrms["productCriticalCompetencies"]) == set(hrms["products"])


def test_profile_incomplete_officials_exist_for_unassessed(data):
    incomplete = set(data["_truth/planted_effects.json"]["profileIncomplete"])
    assert len(incomplete) == gen.N_PROFILE_INCOMPLETE
    for u in data["userdata.json"]:
        if u["userId"] in incomplete:
            assert u["education"] == [] and u["careerHistory"] == [] and u["experienceYears"] == 0
