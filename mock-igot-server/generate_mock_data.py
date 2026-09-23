"""
generate_mock_data.py — the ONE deterministic generator for the mock iGOT data
===============================================================================

    cd mock-igot-server
    python generate_mock_data.py            # writes data/*.json + data/MANIFEST.json
    python generate_mock_data.py --check    # regenerate in memory, diff against disk

Every file it writes is SYNTHETIC (labelled in data/MANIFEST.json and, for
dict-shaped files, in a top-level "_meta"). Same seed ⇒ byte-identical output:
  * one fixed SEED; every section draws from its own random.Random(f"{SEED}:{section}")
    stream, so adding a section never reshuffles another;
  * a fixed REF_DATE instead of "now";
  * no set iteration without sorting; floats rounded before writing.

Inputs: mockdata/domain.py (hand-written domain content), mockdata/roster_seed.json
(frozen identities), competencies.json (the real iGOT competency dictionary, read
only for the crosswalk). See data/README.md for distributions and deliberate holes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import re
import sys
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from mockdata import domain as D  # noqa: E402

SEED = 20260918
REF_DATE = date(2026, 9, 15)          # "today" in the synthetic world
GENERATOR = "mock-igot-server/generate_mock_data.py"
DATA_DIR = os.path.join(HERE, "data")

# ── Distribution constants (each documented in data/README.md) ──────────────
MISSING_QUALITY_P = 0.10          # A3: share of courses missing each quality field
SELF_REPORT_MISSING_P = 0.10      # A1: role competencies with no self-report
OVERCLAIMER_P = 0.10              # A1: share of officials who over-claim
SECONDARY_TAG_P = 0.22            # A2: chance a course carries an overlap tag
HISTORY_YEARS = 3                 # A5: completions spread over the last 3 years
N_OUT_OF_ORDER = 5                # A5: officials who took a course above their level first
N_PROFILE_INCOMPLETE = 3          # A1: new recruits with no HRMS history → UNASSESSED exists
N_POPULAR_ZERO_UPLIFT = 4         # B5: popular, highly rated courses with ~0 true uplift


def rng_for(section: str) -> random.Random:
    return random.Random(f"{SEED}:{section}")


def weighted(rng: random.Random, weights: dict):
    keys = list(weights)
    return rng.choices(keys, weights=[weights[k] for k in keys], k=1)[0]


def iso(d) -> str:
    if isinstance(d, date) and not isinstance(d, datetime):
        d = datetime(d.year, d.month, d.day, 9, 0, tzinfo=timezone.utc)
    return d.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def ref_minus(days: float, rng: random.Random | None = None) -> datetime:
    base = datetime(REF_DATE.year, REF_DATE.month, REF_DATE.day, 9, 0, tzinfo=timezone.utc)
    minutes = rng.randint(0, 8 * 60) if rng else 0
    return base - timedelta(days=days) + timedelta(minutes=minutes)


# ─────────────────────────────────────────────────────────────────────────────
# FRAC competencies
# ─────────────────────────────────────────────────────────────────────────────

def build_frac() -> list:
    out = []
    for cid, name, ctype, decay, desc, _topics in D.COMPETENCIES:
        out.append({
            "id": cid,
            "type": "Competency",
            "name": name,
            "description": desc,
            "competencyType": ctype,
            "source": "FRAC_Dictionary_v1",
            "status": "Live",
            "decayClass": decay,
            "gsbpm": D.GSBPM_MAP[cid],
            "children": [
                {"id": f"{cid}_lvl_{lvl}", "type": "CompetencyLevel", "name": f"Level {lvl}", "level": lvl,
                 "description": D.LEVEL_TEMPLATES[ctype][lvl - 1].format(short=D.SHORT_NAMES[cid].lower()
                                                                         if ctype == "Behavioural"
                                                                         else D.SHORT_NAMES[cid])}
                for lvl in range(1, 6)
            ],
        })
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Course catalogue (A2 + A3)
# ─────────────────────────────────────────────────────────────────────────────

_ARTICLE = {"micro_learning": "A short", "self_paced_course": "A", "nssta_workshop": "An",
            "tpac_programme": "An"}


def _hours_for(rng: random.Random, fmt: str, level: int) -> float:
    (lo, hi), _ = D.FORMATS[fmt]
    # higher levels lean longer: u^exp with a smaller exponent pushes u towards 1
    u = rng.random() ** max(0.4, 1.6 - 0.25 * level)
    h = lo + (hi - lo) * u
    if fmt == "tpac_programme":
        return float(max(4, min(10, round(h / 6))) * 6)       # whole 6-hour training days
    if fmt == "nssta_workshop":
        return round(h * 2) / 2
    return round(h * 4) / 4


_SMALL_WORDS = {"and", "or", "of", "the", "in", "for", "with", "to", "a", "an", "on", "by", "from", "under"}


def _title_case(text: str) -> str:
    """'price collection and quote validation' → 'Price Collection and Quote Validation';
    words that already carry capitals (CPI, GeM, X-13ARIMA-SEATS) are kept."""
    words = text.split()
    out = []
    for i, w in enumerate(words):
        if any(ch.isupper() for ch in w):
            out.append(w)
        elif i > 0 and w in _SMALL_WORDS:
            out.append(w)
        else:
            out.append(w[0].upper() + w[1:])
    return " ".join(out)


def _course_id(rng: random.Random, used: set) -> str:
    while True:
        cid = "do_113" + "".join(str(rng.randint(0, 9)) for _ in range(17))
        if cid not in used:
            used.add(cid)
            return cid


def build_catalog(frac: list) -> tuple[list, dict]:
    """Returns (catalogue, hidden) — hidden holds generator-only facts (planted effects)."""
    rng = rng_for("catalog")
    frac_by_id = {c["id"]: c for c in frac}
    comp_meta = {c[0]: c for c in D.COMPETENCIES}
    used_ids: set = set()
    used_titles: set = set()
    courses = []

    for cid, name, ctype, _decay, _desc, topics in D.COMPETENCIES:
        topic_order = topics[:]
        rng.shuffle(topic_order)
        t_ptr = 0
        for level in range(1, 6):
            if level in D.LADDER_HOLES.get(cid, []):
                continue
            n = weighted(rng, D.COURSES_PER_CELL[D.CATALOG_DEPTH[cid]])
            for _k in range(n):
                topic = topic_order[t_ptr % len(topic_order)]
                topic2 = topic_order[(t_ptr + 1) % len(topic_order)]
                t_ptr += 1
                fmt = weighted(rng, D.FORMAT_BY_LEVEL[level])
                hours = _hours_for(rng, fmt, level)
                modality = weighted(rng, D.FORMATS[fmt][1])

                word = rng.choice(D.LEVEL_TITLE_WORDS[level])
                cap_topic = _title_case(topic)
                if rng.random() < 0.5:
                    sep = " —" if word.endswith(":") else ":"
                    title = f"{word} {D.SHORT_NAMES[cid]}{sep} {cap_topic}"
                else:
                    title = f"{word} {cap_topic}"
                base, suffix = title, 2
                while title in used_titles:
                    title = f"{base} (Part {suffix})"
                    suffix += 1
                used_titles.add(title)

                tags = [{"id": cid, "name": name, "competencyType": ctype,
                         "competencyLevel": f"Level {level}", "primary": True}]
                extra = ""
                overlaps = [o for o in D.OVERLAP.get(cid, [])]
                if overlaps and rng.random() < SECONDARY_TAG_P:
                    sec = rng.choice(overlaps)
                    sec_level = max(1, level - (1 if rng.random() < 0.5 else 0))
                    if sec_level not in D.LADDER_HOLES.get(sec, []):
                        smeta = comp_meta[sec]
                        stopic = rng.choice(smeta[5])
                        tags.append({"id": sec, "name": smeta[1], "competencyType": smeta[2],
                                     "competencyLevel": f"Level {sec_level}", "primary": False})
                        extra = (f" It also covers {stopic} for {D.SHORT_NAMES[sec]}"
                                 f" ({smeta[1]}, Level {sec_level}).")

                descriptor = frac_by_id[cid]["children"][level - 1]["description"]
                description = (
                    f"{_ARTICLE[fmt]} {D.FORMAT_LABEL[fmt]} on {name} for {D.LEVEL_AUDIENCE[level]}. "
                    f"Covers {topic} and {topic2}.{extra} "
                    f"Outcome (FRAC Level {level}): {descriptor}"
                )

                nssta = fmt in ("nssta_workshop", "tpac_programme") or (
                    fmt == "self_paced_course" and rng.random() < 0.12)
                if nssta:
                    creator, channel = D.NSSTA_CREATOR, "igot-mdo-nssta-02"
                else:
                    creator, channel = rng.choice(D.IGOT_PROVIDERS)
                is_tpac = fmt == "tpac_programme"

                leaf = max(2, round(hours * 60 / rng.uniform(20, 40)))
                identifier = _course_id(rng, used_ids)

                # Quality — latent course quality q drives rating and completion.
                q = rng.gauss(0, 1)
                enroll = int(math.exp(rng.gauss(math.log(700 / level ** 0.5), 1.0)))
                if modality == "classroom":
                    enroll = min(enroll, rng.randint(40, 450))
                enroll = max(8, enroll)
                rating = round(min(4.9, max(3.0, 3.95 + 0.35 * q + rng.gauss(0, 0.18))), 2)
                rating_count = max(1, int(enroll * rng.uniform(0.01, 0.12) * math.exp(rng.gauss(0, 0.6))))
                completion = round(min(0.9, max(0.25, 0.86 - 0.009 * hours + 0.04 * q + rng.gauss(0, 0.05))), 3)

                created = ref_minus(rng.randint(200, 1500), rng)
                published = min(ref_minus(rng.randint(5, 180), rng), ref_minus(0))
                course = {
                    "identifier": identifier,
                    "name": title,
                    "description": description,
                    "channel": channel,
                    "contentType": "Course",
                    "mimeType": "application/vnd.ekstep.content-collection",
                    "status": "Live",
                    "primaryCategory": "Course",
                    "duration": str(int(round(hours * 3600))),       # seconds (Sunbird)
                    "leafNodesCount": leaf,
                    "creator": creator,
                    "organisation": [creator],
                    "competencies_v3": json.dumps(tags, ensure_ascii=False),
                    "objectType": "Content",
                    "audience": ["Learner"],
                    "language": ["English", "Hindi"] if rng.random() < 0.25 else ["English"],
                    "format": fmt,
                    "modality": modality,
                    "level": level,
                    "createdOn": iso(created),
                    "lastPublishedOn": iso(max(published, created)),
                    "rating": rating,
                    "rating_count": rating_count,
                    "enrollment_count": enroll,
                    "completion_rate": completion,
                    "is_tpac": is_tpac,
                }
                courses.append(course)

    # B5 plant: a few popular, highly-rated self-paced courses whose true
    # uplift will be ~0 (the ratings/popularity are made to look great).
    prng = rng_for("catalog:zero-uplift")
    # Plant them on the deep subjects: a flagship course with thousands of
    # enrolments is what the measured-uplift estimator has to be able to doubt,
    # and only a "core" competency carries enough outcome records to do it.
    pool = [c for c in courses if c["format"] == "self_paced_course" and c["level"] in (2, 3)
            and json.loads(c["competencies_v3"])[0]["competencyType"] == "Domain"
            and D.CATALOG_DEPTH[json.loads(c["competencies_v3"])[0]["id"]] == "core"]
    planted = prng.sample(pool, N_POPULAR_ZERO_UPLIFT)
    for c in planted:
        c["rating"] = round(prng.uniform(4.55, 4.85), 2)
        c["enrollment_count"] = prng.randint(6000, 16000)
        c["rating_count"] = int(c["enrollment_count"] * prng.uniform(0.08, 0.14))
        c["completion_rate"] = round(prng.uniform(0.78, 0.88), 3)

    # A3: ~10% of each quality field missing (missing ≠ default in the engine).
    mrng = rng_for("catalog:missing")
    planted_ids = {c["identifier"] for c in planted}
    for c in courses:
        if c["identifier"] in planted_ids:
            continue
        if mrng.random() < MISSING_QUALITY_P:
            del c["rating"], c["rating_count"]
        if mrng.random() < MISSING_QUALITY_P:
            del c["enrollment_count"]
        if mrng.random() < MISSING_QUALITY_P:
            del c["completion_rate"]

    courses.sort(key=lambda c: c["identifier"])
    hidden = {"zeroUpliftCourses": sorted(planted_ids)}
    return courses, hidden


def course_tags(course: dict) -> list:
    return json.loads(course["competencies_v3"])


def course_hours(course: dict) -> float:
    return int(course["duration"]) / 3600.0


# ─────────────────────────────────────────────────────────────────────────────
# iGOT dictionary → catalogue crosswalk (A1)
# ─────────────────────────────────────────────────────────────────────────────

def build_crosswalk(igot_dictionary: list) -> dict:
    rules = [(re.compile(p, re.I), fid) for p, fid in D.CROSSWALK_RULES]
    entries = []
    for comp in sorted(igot_dictionary, key=lambda c: c["competency_id"]):
        name = comp.get("name") or ""
        hit = next(((p.pattern, fid) for p, fid in rules if p.search(name)), None)
        entries.append({
            "cidId": comp["competency_id"],
            "cidName": name,
            "fracId": hit[1] if hit else None,
            "confirmed": False,
            "method": "keyword_rule" if hit else "none",
            "rule": hit[0] if hit else None,
        })
    return {
        "_meta": {"synthetic": True, "generator": GENERATOR, "seed": SEED,
                  "note": "Keyword-rule crosswalk from the iGOT competency dictionary (competencies.json, "
                          "CID ids) to the 40 catalogue FRAC ids. No mapping has been confirmed by a "
                          "human reviewer (confirmed=false for all); fracId=null means no rule matched."},
        "mappings": entries,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Offices, roles and officials (A1)
# ─────────────────────────────────────────────────────────────────────────────

def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _designation(rng: random.Random, tier: str, exp: int) -> str:
    if tier == "TIER1_APEX":
        return "Additional Director General" if exp >= 26 else "Deputy Director General"
    if tier == "TIER2_SENIOR":
        return "Director" if exp >= 17 else "Joint Director"
    if tier == "TIER3_MID":
        if exp < 5:
            return "Assistant Director" if rng.random() < 0.6 else "Senior Statistical Officer"
        return "Deputy Director" if rng.random() < 0.7 else "Senior Statistical Officer"
    return "Junior Statistical Officer" if (exp >= 6 or rng.random() < 0.6) else "Statistical Investigator Grade-I"


def build_role(office_id: str, designation: str, tier: str) -> dict:
    rng = rng_for(f"role:{office_id}:{designation}")
    office = next(o for o in D.OFFICES if o[0] == office_id)
    core = dict(office[6])
    n_dom = {"TIER4_JUNIOR": (2, 3), "TIER3_MID": (2, 3), "TIER2_SENIOR": (2, 3), "TIER1_APEX": (1, 2)}[tier]
    n_fun = {"TIER4_JUNIOR": (2, 3), "TIER3_MID": (1, 3), "TIER2_SENIOR": (1, 2), "TIER1_APEX": (1, 2)}[tier]
    n_beh = {"TIER4_JUNIOR": (1, 2), "TIER3_MID": (1, 2), "TIER2_SENIOR": (2, 2), "TIER1_APEX": (2, 3)}[tier]

    # every role in an office requires the office's lead subject (highest weight)
    lead = max(core, key=lambda c: core[c])
    comps: list = [lead]
    pool = {c: w for c, w in core.items() if c != lead}
    for _ in range(min(len(pool), rng.randint(*n_dom) - 1)):
        pick = weighted(rng, pool)
        comps.append(pick)
        pool.pop(pick)
    fun_pool = [f for f in D.OFFICE_FUNCTIONAL[office_id] if f not in comps]
    if tier in ("TIER2_SENIOR", "TIER1_APEX"):
        fun_pool = [f for f in ["comp_project_mgmt_024", "comp_public_fin_025", "comp_data_gov_016"]
                    if f in D.OFFICE_FUNCTIONAL[office_id] or rng.random() < 0.5] + fun_pool
        fun_pool = list(dict.fromkeys(fun_pool))
    comps += rng.sample(fun_pool, min(len(fun_pool), rng.randint(*n_fun)))
    beh_pool = D.BEHAVIOURAL_BY_TIER[tier]
    comps += rng.sample(beh_pool, min(len(beh_pool), rng.randint(*n_beh)))
    comps = list(dict.fromkeys(comps))[:8]

    type_of = {c[0]: c[2] for c in D.COMPETENCIES}
    required = []
    for i, cid in enumerate(comps):
        lvl = weighted(rng, D.REQUIRED_LEVEL_BY_TIER[tier])
        if i == 0 and tier in ("TIER2_SENIOR", "TIER1_APEX"):
            lvl = max(lvl, 4)                        # the role's lead subject is expert-level
        if type_of[cid] == "Behavioural" and tier == "TIER1_APEX":
            lvl = max(lvl, 4)
        required.append({"id": cid, "requiredLevel": int(lvl)})
    return {
        "roleId": f"role_{office_id[4:]}_{_slug(designation)}",
        "officeId": office_id,
        "designation": designation,
        "tier": tier,
        "competencies": required,
    }


def build_officials(roster_seed: list, catalog: list) -> tuple[list, list, dict]:
    """→ (userdata, roles, truth). truth = latent true level per (user, comp)."""
    comp_meta = {c[0]: c for c in D.COMPETENCIES}
    office_by_legacy: dict = {}
    for o in D.OFFICES:
        for legacy in o[3]:
            office_by_legacy.setdefault(legacy, []).append(o[0])
    office_meta = {o[0]: o for o in D.OFFICES}

    roles: dict = {}
    users, truth = [], {}
    rng_over = rng_for("officials:overclaimers")
    overclaimers = {s["userId"] for s in roster_seed if rng_over.random() < OVERCLAIMER_P}
    # Profile-incomplete new recruits: the three most junior officials by experience.
    juniors = sorted((s for s in roster_seed if s["tier"] == "TIER4_JUNIOR"),
                     key=lambda s: (s["experienceYears"], s["userId"]))
    incomplete = {s["userId"] for s in juniors[:N_PROFILE_INCOMPLETE]}

    for seed in roster_seed:
        uid = seed["userId"]
        rng = rng_for(f"official:{uid}")
        tier = seed["tier"]
        exp = int(seed["experienceYears"])
        candidates = office_by_legacy.get(seed["legacyDepartment"]) or [o[0] for o in D.OFFICES]
        office_id = rng.choice(sorted(candidates))
        if uid == "usr_EMP8472":
            office_id = "off_nad"                      # demo official: National Accounts
        designation = _designation(rng, tier, exp)
        if uid == "usr_EMP8472":
            designation = "Deputy Director"
        role_key = (office_id, designation)
        if role_key not in roles:
            roles[role_key] = build_role(office_id, designation, tier)
        role = roles[role_key]
        office = office_meta[office_id]

        education, career = seed["education"], seed["careerHistory"]
        if uid in incomplete:
            exp, education, career = 0, [], []

        comps, user_truth = [], {}
        for req in role["competencies"]:
            cid, target = req["id"], req["requiredLevel"]
            gap = weighted(rng, {0: 0.22, 1: 0.40, 2: 0.26, 3: 0.12})
            if tier in ("TIER1_APEX", "TIER2_SENIOR") and gap == 3:
                gap = 1
            true_level = max(0, min(5, target - gap))
            if gap == 0 and rng.random() < 0.2:
                true_level = min(5, target + 1)
            if uid in incomplete:
                true_level = min(true_level, 1)
            theta = round(true_level + rng.uniform(0.1, 0.9), 3)
            user_truth[cid] = {"trueLevel": true_level, "theta": theta, "target": target}

            entry = {"id": cid, "name": comp_meta[cid][1], "type": comp_meta[cid][2],
                     "requiredLevel": target, "isRoleRequired": True}
            no_claim = rng.random() < SELF_REPORT_MISSING_P or (uid in incomplete and rng.random() < 0.7)
            if not no_claim:
                if uid in overclaimers and rng.random() < 0.7:
                    claim = true_level + rng.choice([1, 1, 2])
                else:
                    claim = true_level + weighted(rng, {-1: 0.2, 0: 0.6, 1: 0.2})
                claim = max(1, min(5, claim))
                entry["competencyLevel"] = f"Level {claim}"
            comps.append(entry)
        truth[uid] = user_truth

        user = {
            "id": uid,
            "userId": uid,
            "firstName": seed["firstName"],
            "lastName": seed["lastName"],
            "email": seed["email"],
            "status": 1,
            "govId": seed["govId"],
            "experienceYears": exp,
            "roles": ["PUBLIC"],
            "rootOrgId": seed["rootOrgId"],
            "jobProfile": {
                "position_id": role["roleId"],
                "nco_code": "",
                "title": designation,
                "tier": tier,
                "roleId": role["roleId"],
                "officeId": office_id,
            },
            "education": education,
            "careerHistory": career,
            "competencies": comps,
            "profileDetails": {
                "competencies": comps,
                "professionalDetails": [{
                    "designation": designation,
                    "department": office[1],
                    "location": office[2],
                    "industry": "Government Administration",
                }],
            },
        }
        if uid in incomplete:
            user["profileStatus"] = "HRMS_SYNC_PENDING"
        users.append(user)

    role_list = sorted(roles.values(), key=lambda r: r["roleId"])
    return users, role_list, {"truth": truth, "overclaimers": sorted(overclaimers),
                              "profileIncomplete": sorted(incomplete)}


# ─────────────────────────────────────────────────────────────────────────────
# Enrollments + content states (A5)
# ─────────────────────────────────────────────────────────────────────────────

def _batch(course_id: str) -> str:
    return "batch_" + course_id[3:] + "_01"


def _leaf_ids(course: dict) -> list:
    return [f"{course['identifier']}_{i:03d}" for i in range(1, course["leafNodesCount"] + 1)]


def build_enrollments(users: list, catalog: list, facts: dict) -> tuple[list, dict, dict]:
    """→ (enrollments, content_states, planted)."""
    by_comp_level: dict = {}
    by_id = {c["identifier"]: c for c in catalog}
    for c in catalog:
        for t in course_tags(c):
            if t.get("primary"):
                lvl = int(t["competencyLevel"].split()[-1])
                by_comp_level.setdefault((t["id"], lvl), []).append(c["identifier"])
    for k in by_comp_level:
        by_comp_level[k].sort()

    truth = facts["truth"]
    ooo_rng = rng_for("enrollments:out-of-order")
    eligible = sorted(u["userId"] for u in users
                      if any(t["trueLevel"] <= 2 and t["target"] >= 4 for t in truth[u["userId"]].values()))
    out_of_order = set(ooo_rng.sample(eligible, min(N_OUT_OF_ORDER, len(eligible))))

    enrollments, states = [], {}
    planted = {"outOfOrder": []}
    window = HISTORY_YEARS * 365

    for user in users:
        uid = user["userId"]
        rng = rng_for(f"enrollments:{uid}")
        taken: set = set()
        records = []

        def pick(comp: str, level: int):
            ids = [i for i in by_comp_level.get((comp, level), []) if i not in taken]
            return rng.choice(ids) if ids else None

        # completed history on role competencies (levels ≤ true level)
        history = []
        for cid, t in truth[uid].items():
            ctype = next(c[2] for c in D.COMPETENCIES if c[0] == cid)
            if t["trueLevel"] == 0 or rng.random() > (0.35 if ctype == "Behavioural" else 0.6):
                continue
            for lvl in range(1, t["trueLevel"] + 1):
                p = 0.75 if lvl == t["trueLevel"] else (0.5 if lvl == t["trueLevel"] - 1 else 0.15)
                if rng.random() < p:
                    course = pick(cid, lvl)
                    if course:
                        taken.add(course)
                        history.append((lvl, course))
        # out-of-order plant: a course two levels above the true level, done first
        if uid in out_of_order:
            cands = sorted(cid for cid, t in truth[uid].items() if t["trueLevel"] <= 2 and t["target"] >= 4)
            cid = ooo_rng.choice(cands)
            lvl = min(5, truth[uid][cid]["trueLevel"] + 2)
            course = pick(cid, lvl) or pick(cid, lvl + 1 if lvl < 5 else lvl)
            if course:
                taken.add(course)
                history.append((0, course))            # sort key 0 → taken earliest
                planted["outOfOrder"].append({"userId": uid, "competencyId": cid, "courseId": course,
                                              "courseLevel": lvl, "trueLevel": truth[uid][cid]["trueLevel"]})
        # a few non-role courses (general interest, low level)
        for _ in range(rng.choice([0, 1, 1, 2, 3])):
            comp = rng.choice(D.COMPETENCIES)[0]
            if comp in truth[uid]:
                continue
            course = pick(comp, rng.choice([1, 1, 2]))
            if course:
                taken.add(course)
                history.append((1, course))

        # dates: ascending by level so lower rungs come first
        history.sort(key=lambda h: h[0])
        days = sorted((rng.uniform(10, window) for _ in history), reverse=True)
        for (lvl, course_id), d_ago in zip(history, days):
            course = by_id[course_id]
            completed = ref_minus(d_ago, rng)
            span = math.ceil(course_hours(course) / 6) + rng.randint(0, 30)
            enrolled = completed - timedelta(days=span)
            records.append(("done", course, enrolled, completed))

        # in-progress / not-started on current gaps (the next rung up)
        for cid, t in truth[uid].items():
            if t["trueLevel"] >= t["target"]:
                continue
            r = rng.random()
            if r < 0.35:
                course = pick(cid, t["trueLevel"] + 1)
                if course:
                    taken.add(course)
                    records.append(("doing", by_id[course], ref_minus(rng.uniform(5, 180), rng), None))
            elif r < 0.45:
                course = pick(cid, min(5, t["trueLevel"] + 1))
                if course:
                    taken.add(course)
                    records.append(("todo", by_id[course], ref_minus(rng.uniform(1, 90), rng), None))

        for kind, course, enrolled, completed in records:
            cid = course["identifier"]
            leaf = course["leafNodesCount"]
            leaves = _leaf_ids(course)
            if kind == "done":
                status, progress, pct = 2, leaf, 100
                last, last_status = leaves[-1], 2
                certs = [{"identifier": "cert_" + hashlib.sha1(f"{uid}{cid}".encode()).hexdigest()[:10],
                          "name": "Completion Certificate",
                          "token": hashlib.sha1(f"{cid}{uid}".encode()).hexdigest()[:8].upper(),
                          "lastIssuedOn": iso(completed)}]
            elif kind == "doing":
                status = 1
                progress = rng.randint(1, leaf - 1)
                pct = min(99, max(1, round(progress / leaf * 100)))
                last, last_status, certs = leaves[progress], 1, []
            else:
                status, progress, pct, last, last_status, certs = 0, 0, 0, "", 0, []
            rec = {
                "active": True,
                "courseId": cid,
                "courseName": course["name"],
                "contentId": cid,
                "batchId": _batch(cid),
                "userId": uid,
                "enrolledDate": iso(enrolled),
                "status": status,
                "completionPercentage": pct,
                "progress": progress,
                "leafNodesCount": leaf,
                "lastReadContentId": last,
                "lastReadContentStatus": last_status,
                "issuedCertificates": certs,
                "channel": course["channel"],
            }
            if status == 2:
                rec["completedDate"] = iso(completed)
            enrollments.append(rec)

            if status == 1:
                clist = []
                t0 = enrolled
                for i in range(progress + 1):
                    access = t0 + timedelta(days=(REF_DATE - enrolled.date()).days * (i + 1) / (progress + 2))
                    done = i < progress
                    size = rng.randint(10000, 90000)
                    clist.append({
                        "contentId": leaves[i],
                        "status": 2 if done else 1,
                        "completionPercentage": 100 if done else rng.randint(5, 95),
                        "lastAccessTime": iso(access),
                        })
                    if not done:   # Sunbird progress details only for the module being read
                        clist[-1]["progressdetails"] = {
                            "max_size": size, "current_size": rng.randint(1, size - 1),
                            "mimeType": rng.choice(["video/mp4", "application/pdf", "text/html"])}
                states[f"{uid}|{cid}|{_batch(cid)}"] = {
                    "contentList": clist,
                    "lastReadContentId": last,
                    "completionPercentage": pct,
                    "courseId": cid,
                    "batchId": _batch(cid),
                }

    enrollments.sort(key=lambda e: (e["userId"], e["enrolledDate"], e["courseId"]))
    states = {k: states[k] for k in sorted(states)}

    # Profile competency status is the official's own declaration (as on iGOT):
    # ACQUIRED when the self-claim meets the requirement, IN_PROGRESS when a
    # course tagged with it is under way, otherwise PLANNED.
    doing = {(e["userId"], t["id"]) for e in enrollments if e["status"] == 1
             for t in course_tags(by_id[e["courseId"]]) if t.get("primary")}
    for user in users:
        for comp in user["competencies"]:
            claim = int((comp.get("competencyLevel") or "Level 0").split()[-1])
            comp["status"] = ("ACQUIRED" if claim >= comp["requiredLevel"] else
                              "IN_PROGRESS" if (user["userId"], comp["id"]) in doing else "PLANNED")
    return enrollments, states, planted


# ─────────────────────────────────────────────────────────────────────────────
# GSBPM ontology + office workload (B1 / B2)
# ─────────────────────────────────────────────────────────────────────────────

CYCLE_ID = "FY2026-27-Q2"
CYCLE_LABEL = "FY 2026-27 Q2 (Jul–Sep 2026)"
HOURS_PER_OFFICER_QUARTER = 480     # ~60 working days × 8 h of productive time per quarter


def build_gsbpm_map() -> dict:
    return {
        "_meta": meta("GSBPM sub-processes and which FRAC competency is exercised in which sub-process. "
                      "Sub-process list is GSBPM v5.1 (requested: 5.2 — see the decisions log); OA.* are "
                      "GSBPM overarching processes, which GSBPM does not number."),
        "version": "5.1",
        "phases": D.GSBPM_PHASES,
        "subprocesses": {sid: {"name": name, "phase": sid.split(".")[0]}
                         for sid, name in D.GSBPM_SUBPROCESSES.items()},
        "competencies": {cid: D.GSBPM_MAP[cid] for cid, *_ in D.COMPETENCIES},
    }


def build_offices(users: list) -> dict:
    rng = rng_for("offices")
    roster = {}
    for u in users:
        roster[u["jobProfile"]["officeId"]] = roster.get(u["jobProfile"]["officeId"], 0) + 1
    offices = []
    for oid, name, location, _legacy, products, weights, _core in D.OFFICES:
        head = D.OFFICE_HEADCOUNT[oid]
        total_w = sum(weights.values())
        subs = []
        for sid in sorted(weights):
            hours = head * HOURS_PER_OFFICER_QUARTER * weights[sid] / total_w * rng.uniform(0.85, 1.15)
            subs.append({"id": sid, "name": D.GSBPM_SUBPROCESSES[sid], "officerHours": int(round(hours, -1))})
        offices.append({
            "officeId": oid,
            "name": name,
            "location": location,
            "products": products,
            "headcount": head,
            "rosterOfficials": roster.get(oid, 0),
            "cycle": CYCLE_ID,
            "subprocesses": subs,
            "totalOfficerHours": sum(s["officerHours"] for s in subs),
        })
    return {
        "_meta": meta(f"Office workload for {CYCLE_LABEL}: which GSBPM sub-processes each office runs and "
                      f"the officer-hours spent on each (headcount × {HOURS_PER_OFFICER_QUARTER} h × share)."),
        "cycle": {"id": CYCLE_ID, "label": CYCLE_LABEL, "hoursPerOfficer": HOURS_PER_OFFICER_QUARTER},
        "offices": offices,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Annual Capacity Building Plan: mandatory courses + learning hours (B3)
# ─────────────────────────────────────────────────────────────────────────────

ACBP_CYCLE = "FY2026-27"
KARMAYOGI_MIN_HOURS_PER_YEAR = 50     # Mission Karmayogi guidance: ≥ 50 learning hours a year
LEARNING_HOURS_BY_TIER = {            # available hours per quarter (choices)
    "TIER4_JUNIOR": [16, 20, 24, 30], "TIER3_MID": [14, 16, 20, 24, 30],
    "TIER2_SENIOR": [14, 16, 20, 24], "TIER1_APEX": [14, 16, 20],
}
ORG_MANDATORY_COMPETENCY = "comp_data_privacy_026"   # information-security awareness, all staff


def _mandatory_pick(catalog: list, comp: str, levels: tuple, exclude=()) -> dict | None:
    """Shortest non-classroom course with `comp` as its primary tag at one of `levels`."""
    cands = [c for c in catalog if c["modality"] != "classroom" and c["identifier"] not in exclude
             and any(t["id"] == comp and t.get("primary") and int(t["competencyLevel"][-1]) in levels
                     for t in course_tags(c))]
    return min(cands, key=lambda c: (int(c["duration"]), c["identifier"])) if cands else None


def _mandatory_entry(course: dict, comp: str, reason: str) -> dict:
    level = next(int(t["competencyLevel"][-1]) for t in course_tags(course) if t["id"] == comp)
    return {"courseId": course["identifier"], "title": course["name"], "competencyId": comp,
            "level": level, "hours": round(course_hours(course), 2), "aparLinked": True, "reason": reason}


def build_acbp(roles: list, users: list, catalog: list) -> dict:
    org_course = _mandatory_pick(catalog, ORG_MANDATORY_COMPETENCY, (1,))
    org = [_mandatory_entry(org_course, ORG_MANDATORY_COMPETENCY,
                            "Organisation-wide ACBP course (information security and data privacy)")]
    type_of = {c[0]: c[2] for c in D.COMPETENCIES}
    role_plans = {}
    for role in roles:
        comps = [c["id"] for c in role["competencies"]]
        if role["tier"] in ("TIER4_JUNIOR", "TIER3_MID"):
            comp, levels, why = comps[0], (2,), "Role ACBP course on the office's lead subject"
        else:
            comp = next((c for c in comps if type_of[c] == "Behavioural"), comps[0])
            levels, why = (3,), "Role ACBP course for senior officers"
        course = _mandatory_pick(catalog, comp, levels, exclude={org_course["identifier"]})
        role_plans[role["roleId"]] = {
            "mandatoryCourses": [_mandatory_entry(course, comp, why)] if course else [],
        }
    officials = {}
    for u in users:
        rng = rng_for(f"acbp:{u['userId']}")
        tier = u["jobProfile"]["tier"]
        hours = rng.choice(LEARNING_HOURS_BY_TIER[tier])
        if u["jobProfile"]["officeId"].startswith("off_fod"):
            # field staff: survey rounds leave less time, but never below the
            # Karmayogi floor (14 h/quarter = 56 h/year ≥ 50 h/year)
            hours = max(14, hours - 4)
        officials[u["userId"]] = {"roleId": u["jobProfile"]["roleId"], "learningHoursPerQuarter": hours}
    return {
        "_meta": meta(f"Annual Capacity Building Plan {ACBP_CYCLE}: APAR-linked mandatory courses (organisation-"
                      f"wide + per role) and each official's available learning hours per quarter "
                      f"(Mission Karmayogi guidance ≥ {KARMAYOGI_MIN_HOURS_PER_YEAR} h/year)."),
        "cycle": ACBP_CYCLE,
        "organisationMandatory": org,
        "roles": role_plans,
        "officials": officials,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Cross-competency prerequisite DAG (B4)
# ─────────────────────────────────────────────────────────────────────────────

def find_cycle(edges: list) -> list | None:
    """Cycle in expert edges + the implicit within-competency ladder (c@L-1 → c@L), or None."""
    graph: dict = {}
    nodes = set()
    for e in edges:
        a = (e["from"]["competencyId"], e["from"]["level"])
        b = (e["to"]["competencyId"], e["to"]["level"])
        graph.setdefault(a, set()).add(b)
        nodes |= {a, b}
    for comp, _lvl in sorted(nodes):
        for lvl in range(1, 5):
            graph.setdefault((comp, lvl), set()).add((comp, lvl + 1))
            nodes |= {(comp, lvl), (comp, lvl + 1)}
    state: dict = {}
    stack: list = []

    def visit(n):
        state[n] = 1
        stack.append(n)
        for m in sorted(graph.get(n, ())):
            if state.get(m) == 1:
                return stack[stack.index(m):] + [m]
            if m not in state:
                found = visit(m)
                if found:
                    return found
        state[n] = 2
        stack.pop()
        return None

    for n in sorted(nodes):
        if n not in state:
            found = visit(n)
            if found:
                return [f"{c}@L{l}" for c, l in found]
    return None


def build_prerequisites() -> dict:
    edges = [
        {"id": f"pre_{i:03d}", "from": {"competencyId": a, "level": la}, "to": {"competencyId": b, "level": lb},
         "source": "expert", "rationale": why}
        for i, (a, la, b, lb, why) in enumerate(D.EXPERT_PREREQUISITES, start=1)
    ]
    cycle = find_cycle(edges)
    if cycle:
        raise ValueError(f"EXPERT_PREREQUISITES contain a cycle: {' → '.join(cycle)}")
    return {
        "_meta": meta("Expert-seeded cross-competency prerequisite edges: `from` (competency at level) must be "
                      "reached before `to`. Hand-written for the demo, not elicited from a real panel. "
                      "Checked acyclic together with the within-competency level ladders."),
        "edges": edges,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Course outcome assessments (B4 inference + B5 measured uplift)
# Platform-wide, anonymised: pre/post θ for course takers + comparison
# episodes for non-takers. Every effect below is PLANTED and recorded in
# _truth/planted_effects.json, so estimators can be checked for recovery.
# ─────────────────────────────────────────────────────────────────────────────

TRUE_UPLIFT_MEAN, TRUE_UPLIFT_SD = 0.55, 0.15   # most courses: ~half a FRAC level
MATURATION_BASE = 0.03       # growth over one assessment interval without a course (on-the-job practice)
MATURATION_SLOPE = 0.05      # … per level of prior ability: strong officers grow faster → confounds naive estimates
ASSESSMENT_NOISE_SD = 0.20   # measurement error of each θ assessment
TAKERS_PER_ENROLMENTS = 250  # one outcome record per 250 platform enrolments …
TAKERS_MIN = 2                   # … clipped to [2, TAKERS_MAX[depth]] learners per course
TAKERS_MAX = {"core": 30, "standard": 14, "thin": 8}        # niche courses have fewer learners on the platform
CONTROLS_PER_COMPETENCY = {"core": 60, "standard": 20, "thin": 10}
CONTROLS_PLANTED_COMPETENCY = 150   # competencies carrying a planted zero-uplift course (see below)
PLANTED_ZERO_TAKERS = 60            # takers on a planted zero-uplift course: these have 6k-16k enrolments,
                                    # so the [2, TAKERS_MAX] clip is what would otherwise hold them back
# ^ non-taker comparison episodes per competency, spread over all ability levels. The uplift estimator needs a
#   comparison group per competency; the deep subjects carry enough of them for a usable confidence interval,
#   the long tail only enough to show the interval widening.
PLANTED_GROUP_TAKERS = 18        # min platform takers per course in a planted-precedence group
PLANTED_PRIOR_SHARE = 0.5        # share of those takers who did the planted prerequisite first
EDU_FIELDS = {"statistics": 0.3, "economics": 0.25, "mathematics": 0.1, "computer science": 0.1,
              "public administration": 0.15, "other": 0.1}


def _fit(pre: float, level: int) -> float:
    """How much of a course's uplift a learner at `pre` can take from a Level-`level` course."""
    if pre >= level:
        return 0.3          # already there: little to learn
    if pre < level - 2:
        return 0.5          # far too hard (out-of-order)
    return 1.0


def _covariates(rng: random.Random, pre: float) -> dict:
    return {
        "tenureYears": int(min(35, max(1, round(3 + 5 * pre + rng.gauss(0, 4))))),
        "education": weighted(rng, EDU_FIELDS),
        "priorLevel": int(min(5, max(0, math.floor(pre)))),
    }


def build_outcomes(catalog: list, enrollments: list, users: list, facts: dict, hidden: dict,
                   ooo: list) -> tuple[dict, dict]:
    rng = rng_for("outcomes")
    by_id = {c["identifier"]: c for c in catalog}
    zero = set(hidden["zeroUpliftCourses"])
    true_uplift = {}
    for c in sorted(catalog, key=lambda c: c["identifier"]):
        u = rng.gauss(0.02, 0.02) if c["identifier"] in zero else rng.gauss(TRUE_UPLIFT_MEAN, TRUE_UPLIFT_SD)
        true_uplift[c["identifier"]] = round(min(1.0, max(-0.05 if c["identifier"] in zero else 0.2, u)), 3)
    precedence = {(b, lvl): (a, bonus) for a, b, lvl, bonus in D.PLANTED_PRECEDENCE}
    primary = {cid: next(t for t in course_tags(c) if t.get("primary")) for cid, c in by_id.items()}
    ooo_pairs = {(p["userId"], p["courseId"]) for p in ooo}

    def record(learner, course_id, pre, prior, enrolled, completed, cov):
        tag = primary[course_id]
        comp, level = tag["id"], int(tag["competencyLevel"][-1])
        gain = true_uplift[course_id] * _fit(pre, level)
        bonus_rule = precedence.get((comp, level))
        if bonus_rule and any(p["competencyId"] == bonus_rule[0] for p in prior):
            gain += bonus_rule[1]
        growth = MATURATION_BASE + MATURATION_SLOPE * pre
        pre_obs = pre + rng.gauss(0, ASSESSMENT_NOISE_SD)
        post_obs = pre + growth + gain + rng.gauss(0, ASSESSMENT_NOISE_SD)
        # pre-assessment at enrolment, post-assessment 1–4 weeks after completion
        return {
            "learnerId": learner, "courseId": course_id, "competencyId": comp, "courseLevel": level,
            "enrolled": enrolled.date().isoformat(), "completed": completed.date().isoformat(),
            "preTheta": round(pre_obs, 2), "postTheta": round(post_obs, 2),
            "covariates": cov, "priorCompleted": prior,
        }

    outcomes = []
    # 1. the roster's own completions (history from enrollments.json)
    done = sorted((e for e in enrollments if e["status"] == 2), key=lambda e: (e["userId"], e["completedDate"]))
    users_by_id = {u["userId"]: u for u in users}
    for e in done:
        tag = primary[e["courseId"]]
        level = int(tag["competencyLevel"][-1])
        if (e["userId"], e["courseId"]) in ooo_pairs:
            pre = facts["truth"][e["userId"]][tag["id"]]["theta"] - 0.3
        else:
            pre = level - 1 + rng.uniform(0.15, 0.85)
        prior = {}
        for p in done:
            if p["userId"] == e["userId"] and p["completedDate"] < e["enrolledDate"]:
                pt = primary[p["courseId"]]
                prior[pt["id"]] = max(prior.get(pt["id"], 0), int(pt["competencyLevel"][-1]))
        u = users_by_id[e["userId"]]
        edu = ((u.get("education") or [{}])[0].get("degree") or "other").lower()
        cov = {"tenureYears": max(1, int(u.get("experienceYears") or 1)),
               "education": next((f for f in EDU_FIELDS if f.split()[0] in edu), "other"),
               "priorLevel": int(min(5, max(0, math.floor(pre))))}
        enrolled = datetime.fromisoformat(e["enrolledDate"].replace("Z", "+00:00"))
        completed = datetime.fromisoformat(e["completedDate"].replace("Z", "+00:00"))
        outcomes.append(record(e["userId"], e["courseId"], pre,
                               [{"competencyId": k, "level": v} for k, v in sorted(prior.items())],
                               enrolled, completed, cov))

    # 2. other iGOT learners (anonymised) — volume follows platform enrolments
    comps = [c[0] for c in D.COMPETENCIES]
    for c in sorted(catalog, key=lambda c: c["identifier"]):
        tag = primary[c["identifier"]]
        comp, level = tag["id"], int(tag["competencyLevel"][-1])
        cap = TAKERS_MAX[D.CATALOG_DEPTH[comp]]
        n = int(min(cap, max(TAKERS_MIN, round((c.get("enrollment_count") or 500) / TAKERS_PER_ENROLMENTS))))
        if c["identifier"] in zero:
            n = PLANTED_ZERO_TAKERS
        rule = precedence.get((comp, level))
        if rule:
            n = max(n, PLANTED_GROUP_TAKERS)       # enough learners for the planted effect to be testable
        for k in range(n):
            learner = "lrn_" + hashlib.sha1(f"{c['identifier']}:{k}".encode()).hexdigest()[:10]
            pre = level - 1 + rng.uniform(0.15, 0.85)
            prior = {}
            for other in rng.sample(comps, rng.randint(0, 3)):
                if other != comp:
                    prior[other] = rng.randint(1, 3)
            if rule and rng.random() < PLANTED_PRIOR_SHARE:
                prior[rule[0]] = max(prior.get(rule[0], 0), rng.randint(1, 3))
            completed = ref_minus(rng.uniform(20, HISTORY_YEARS * 365), rng)
            enrolled = completed - timedelta(days=math.ceil(course_hours(c) / 6) + rng.randint(0, 30))
            outcomes.append(record(learner, c["identifier"], pre,
                                   [{"competencyId": k2, "level": v} for k2, v in sorted(prior.items())],
                                   enrolled, completed, _covariates(rng, pre)))

    # 3. comparison episodes: learners with the competency who took no course on it
    #    The four planted zero-uplift courses are the point of the whole file, so
    #    their competency gets a comparison group big enough that the estimator's
    #    confidence interval is driven by the (absent) effect and not by how few
    #    non-takers happened to sit near the takers' ability.
    planted_comps = {primary[cid]["id"] for cid in zero}
    comparisons = []
    for comp in comps:
        n_controls = max(CONTROLS_PER_COMPETENCY[D.CATALOG_DEPTH[comp]],
                         CONTROLS_PLANTED_COMPETENCY if comp in planted_comps else 0)
        for k in range(n_controls):
            pre = rng.uniform(0.1, 4.9)
            growth = MATURATION_BASE + MATURATION_SLOPE * pre
            end = ref_minus(rng.uniform(20, HISTORY_YEARS * 365), rng)
            start = end - timedelta(days=rng.randint(30, 120))
            comparisons.append({
                "learnerId": "lrn_" + hashlib.sha1(f"ctl:{comp}:{k}".encode()).hexdigest()[:10],
                "competencyId": comp,
                "preDate": start.date().isoformat(), "postDate": end.date().isoformat(),
                "preTheta": round(pre + rng.gauss(0, ASSESSMENT_NOISE_SD), 2),
                "postTheta": round(pre + growth + rng.gauss(0, ASSESSMENT_NOISE_SD), 2),
                "covariates": _covariates(rng, pre),
            })

    doc = {
        "_meta": meta("Course outcome assessments (synthetic, platform-wide, anonymised): pre/post θ on the "
                      "FRAC level scale for course takers, plus comparison episodes for learners who took no "
                      "course on the competency. Contains PLANTED effects (see data/README.md) — estimates "
                      "computed on it demonstrate the method; they validate nothing."),
        "scale": "theta on the FRAC level scale (0-5)",
        "outcomes": outcomes,
        "comparisons": comparisons,
    }
    truth = {
        "trueUplift": true_uplift,
        "maturation": {"base": MATURATION_BASE, "slopePerLevel": MATURATION_SLOPE},
        "plantedPrecedence": [{"before": a, "then": b, "level": lvl, "bonus": bonus}
                              for a, b, lvl, bonus in D.PLANTED_PRECEDENCE],
    }
    return doc, truth


# ─────────────────────────────────────────────────────────────────────────────
# Workplace evidence channels (B6): Supervisor, Utility, Application + peer
# EvidenceLog-style rows. Supervisor ratings are deliberately biased.
# ─────────────────────────────────────────────────────────────────────────────

SUPERVISOR_COVERAGE = 0.85          # share of role competencies rated in the last APAR cycle
SUPERVISOR_LENIENCY_MEAN = 0.4      # raters are lenient on average (+0.4 level) …
SUPERVISOR_LENIENCY_SD = 0.3        # … and differ from one another
SUPERVISOR_HALO_SD = 0.4            # one overall impression per official, shared by all their ratings
SUPERVISOR_NOISE_SD = 0.4           # item-level noise
APAR_CYCLE_END = date(2026, 4, 30)  # last annual appraisal (APAR) cycle
UTILITY_WINDOW_DAYS = 90            # "will use within 90 days", confirmed by the supervisor afterwards
UTILITY_YES_IN_ROLE, UTILITY_YES_OFF_ROLE = 0.75, 0.3
UTILITY_CONFIRM_BY_OPPORTUNITY = {"High": 0.85, "Medium": 0.65, "Low": 0.35}
WORK_SAMPLE_ATTEMPT_P = 0.5         # officials with a gradable competency who attempted a work sample
WORK_SAMPLE_PASS = 70               # pass mark (0–100)
PEER_RATING_P = 0.15                # officials with peer feedback on a competency (never scored)


def _office_opportunity(office_id: str, comp: str) -> str:
    """Same bands as the backend's gsbpm_service.opportunity, on the office's sub-process weights."""
    office = next(o for o in D.OFFICES if o[0] == office_id)
    weights = office[5]
    share = sum(w for s, w in weights.items() if s in set(D.GSBPM_MAP[comp])) / sum(weights.values())
    return "High" if share >= 0.20 else "Medium" if share >= 0.05 else "Low"


def build_workplace_evidence(users: list, enrollments: list, catalog: list, facts: dict) -> tuple[dict, dict]:
    truth = facts["truth"]
    by_id = {c["identifier"]: c for c in catalog}
    rows = []
    supervisors = {}
    leniency = {}
    for u in users:
        uid, office = u["userId"], u["jobProfile"]["officeId"]
        rng = rng_for(f"evidence:{uid}")
        sup = f"sup_{office[4:]}_{zlib_short(uid) % 4 + 1}"          # 4 reporting officers per office
        supervisors[uid] = sup
        if sup not in leniency:
            leniency[sup] = round(rng_for(f"leniency:{sup}").gauss(SUPERVISOR_LENIENCY_MEAN, SUPERVISOR_LENIENCY_SD), 3)
        halo = rng.gauss(0, SUPERVISOR_HALO_SD)
        # new recruits (HRMS sync pending) have had no APAR cycle and no work sample yet
        new_recruit = u.get("profileStatus") == "HRMS_SYNC_PENDING"
        rated_on = datetime(APAR_CYCLE_END.year, APAR_CYCLE_END.month, APAR_CYCLE_END.day, 9, 0,
                            tzinfo=timezone.utc) + timedelta(days=rng.randint(0, 45))

        for comp in u["competencies"]:
            cid = comp["id"]
            t = truth[uid][cid]
            # S — supervisor rating: one structured item on the FRAC descriptors, 1–5
            if not new_recruit and rng.random() < SUPERVISOR_COVERAGE:
                raw = t["theta"] + leniency[sup] + halo + rng.gauss(0, SUPERVISOR_NOISE_SD)
                rows.append({"userId": uid, "compId": cid, "evidenceType": "SUPERVISOR_RATING",
                             "grantedValue": int(min(5, max(1, round(raw)))), "issueDate": iso(rated_on),
                             "source": "APAR-SPARROW", "meta": {"raterId": sup, "cycle": "2025-26"}})
            # A — auto-graded work sample at the next level (or the current one)
            tasks = D.WORK_SAMPLE_TASKS.get(cid)
            if tasks and not new_recruit and rng.random() < WORK_SAMPLE_ATTEMPT_P:
                level = min(4, max(2, t["trueLevel"] + (1 if rng.random() < 0.5 else 0)))
                p = 1 / (1 + math.exp(-2.2 * (t["theta"] - level)))
                score = int(min(100, max(0, round(100 * p + rng.gauss(0, 8)))))
                when = ref_minus(rng.uniform(15, 540), rng)
                rows.append({"userId": uid, "compId": cid, "evidenceType": "WORK_SAMPLE",
                             "grantedValue": level, "issueDate": iso(when), "source": "LMS-work-sample",
                             "meta": {"taskId": f"ws_{cid[5:]}_L{level}", "task": tasks[level], "level": level,
                                      "score": score, "passMark": WORK_SAMPLE_PASS,
                                      "passed": score >= WORK_SAMPLE_PASS, "grader": "auto"}})
            # peer feedback — recorded, never scored
            if rng.random() < PEER_RATING_P:
                rows.append({"userId": uid, "compId": cid, "evidenceType": "PEER_RATING",
                             "grantedValue": int(min(5, max(1, round(t["theta"] + rng.gauss(0.6, 0.8))))),
                             "issueDate": iso(ref_minus(rng.uniform(10, 300), rng)), "source": "360-feedback"})

        # U — utility item on course completion, supervisor confirmation after 90 days
        role = {c["id"] for c in u["competencies"]}
        for e in enrollments:
            if e["userId"] != uid or e["status"] != 2:
                continue
            completed = datetime.fromisoformat(e["completedDate"].replace("Z", "+00:00"))
            if (ref_minus(0) - completed).days > 2 * 365:
                continue
            tag = next(t2 for t2 in course_tags(by_id[e["courseId"]]) if t2.get("primary"))
            comp, level = tag["id"], int(tag["competencyLevel"][-1])
            in_role = comp in role
            will_use = rng.random() < (UTILITY_YES_IN_ROLE if in_role else UTILITY_YES_OFF_ROLE)
            due = completed + timedelta(days=UTILITY_WINDOW_DAYS)
            if not will_use:
                confirmed = None
            elif due > ref_minus(0):
                confirmed = None                                  # confirmation not due yet
            else:
                p = UTILITY_CONFIRM_BY_OPPORTUNITY[_office_opportunity(u["jobProfile"]["officeId"], comp)]
                confirmed = rng.random() < (p if in_role else p / 2)
            rows.append({"userId": uid, "compId": comp, "evidenceType": "UTILITY",
                         "grantedValue": level if confirmed else 0, "issueDate": iso(due if confirmed else completed),
                         "source": "LMS-utility-survey",
                         "meta": {"courseId": e["courseId"], "courseLevel": level, "willUse": will_use,
                                  "confirmed": confirmed, "due": due.date().isoformat()}})
    rows.sort(key=lambda r: (r["userId"], r["compId"], r["evidenceType"], r["issueDate"]))
    doc = {
        "_meta": meta("Workplace evidence (EvidenceLog-style rows): SUPERVISOR_RATING (APAR, lenient + halo "
                      "bias built in), UTILITY (will-use-within-90-days + supervisor confirmation), WORK_SAMPLE "
                      "(auto-graded tasks, 10 competencies), PEER_RATING (context only — never scored)."),
        "supervisorItem": "Rate the officer's current proficiency in this competency against the FRAC level "
                          "descriptors (1–5).",
        "utilityItem": "I will use what this course taught within 90 days (yes/no); the reporting officer confirms "
                       "the use after 90 days.",
        "peerNote": "Peer ratings are shown for context and never scored.",
        "supervisors": supervisors,
        "rows": rows,
    }
    return doc, {"supervisorLeniency": dict(sorted(leniency.items())),
                 "supervisorBias": {"leniencyMean": SUPERVISOR_LENIENCY_MEAN, "leniencySd": SUPERVISOR_LENIENCY_SD,
                                    "haloSd": SUPERVISOR_HALO_SD, "noiseSd": SUPERVISOR_NOISE_SD}}


# ─────────────────────────────────────────────────────────────────────────────
# HRMS: dates of birth / joining, superannuation, product assignment (B8)
# ─────────────────────────────────────────────────────────────────────────────

RETIREMENT_AGE = 60                 # Central Government superannuation age
ENTRY_AGE_RANGE = (22, 31)          # age at joining the service


def _last_day_of_month(d: date) -> date:
    nxt = date(d.year + (d.month == 12), d.month % 12 + 1, 1)
    return nxt - timedelta(days=1)


def build_hrms(users: list) -> dict:
    offices = {o[0]: o for o in D.OFFICES}
    officials = {}
    for u in users:
        rng = rng_for(f"hrms:{u['userId']}")
        exp = int(u["experienceYears"])
        age = min(59.7, rng.uniform(*ENTRY_AGE_RANGE) + exp)          # still in service today
        dob = REF_DATE - timedelta(days=int(age * 365.25))
        doj = REF_DATE - timedelta(days=int(exp * 365.25) + rng.randint(0, 180))
        sixty = date(dob.year + RETIREMENT_AGE, dob.month, min(dob.day, 28))
        products = offices[u["jobProfile"]["officeId"]][4]
        k = min(len(products), rng.choice([1, 1, 2]))
        officials[u["userId"]] = {
            "dateOfBirth": dob.isoformat(),
            "dateOfJoining": doj.isoformat(),
            # GoI rule: retire on the afternoon of the last day of the month of the 60th birthday
            "superannuationDate": _last_day_of_month(sixty).isoformat(),
            "products": sorted(rng.sample(products, k)) if k else [],
            "serviceStatus": "in_service",
        }
    return {
        "_meta": meta("HRMS-style service records: date of birth / joining, superannuation date "
                      f"(age {RETIREMENT_AGE}, last day of the month), statistical products each official "
                      "works on. Synthetic."),
        "asOf": REF_DATE.isoformat(),
        "retirementAge": RETIREMENT_AGE,
        "products": D.PRODUCTS,
        "productCriticalCompetencies": D.PRODUCT_CRITICAL,
        "officials": officials,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Item bank (B7): 2PL MCQ items per competency × level + response logs.
# Parameters are SIMULATED, not calibrated on real respondents.
# ─────────────────────────────────────────────────────────────────────────────

ITEMS_PER_LEVEL = 3                    # 3 × 5 levels = 15 items per competency (the CAT maximum)
ITEMS_PER_LEVEL_THIN = 2               # niche subjects: a smaller bank (10 items, still above the CAT floor)
ITEM_A_RANGE = (0.8, 2.0)              # discrimination on the level scale
ITEM_B_SD = 0.35                       # difficulty b ~ N(level − 0.5, 0.35)
RESPONSES_PER_OFFICIAL = 8             # synthetic response log size
BLOOM = {1: "Remember", 2: "Understand", 3: "Apply", 4: "Analyse", 5: "Evaluate"}
STEMS = {
    1: "Which statement correctly describes {topic} in {short}?",
    2: "What is the main purpose of {topic} in {short} work?",
    3: "You must apply {topic} to a new {short} dataset. Which step comes first?",
    4: "A {short} estimate built with {topic} disagrees with a related series. What is the most likely cause?",
    5: "Two approaches to {topic} give different {short} results. Which criterion should decide between them?",
}


def build_item_bank(users: list, facts: dict) -> dict:
    rng = rng_for("itembank")
    items = []
    for cid, _name, _ctype, _decay, _desc, topics in D.COMPETENCIES:
        short = D.SHORT_NAMES[cid]
        per_level = ITEMS_PER_LEVEL_THIN if D.CATALOG_DEPTH[cid] == "thin" else ITEMS_PER_LEVEL
        for level in range(1, 6):
            for k in range(per_level):
                topic = topics[(level * per_level + k) % len(topics)]
                others = [t for t in topics if t != topic]
                distractors = rng.sample(others, 3)
                options = [f"The standard treatment of {topic}"] + [f"The treatment of {d}" for d in distractors]
                order = list(range(4))
                rng.shuffle(order)
                items.append({
                    "itemId": f"it_{cid[5:]}_L{level}_{k + 1}",
                    "competencyId": cid, "level": level, "bloom": BLOOM[level],
                    "stem": STEMS[level].format(topic=topic, short=short),
                    "options": [options[i] for i in order],
                    "answerIndex": order.index(0),
                    "a": round(rng.uniform(*ITEM_A_RANGE), 3),
                    "b": round(level - 0.5 + rng.gauss(0, ITEM_B_SD), 3),
                    "calibration": "synthetic",
                })
    by_comp: dict = {}
    for it in items:
        by_comp.setdefault(it["competencyId"], []).append(it)

    rrng = rng_for("itembank:responses")
    responses = []
    for u in users:
        comp = rrng.choice(u["competencies"])["id"]
        theta = facts["truth"][u["userId"]][comp]["theta"]
        for it in rrng.sample(by_comp[comp], RESPONSES_PER_OFFICIAL):
            p = 1 / (1 + math.exp(-it["a"] * (theta - it["b"])))
            responses.append({"learnerId": u["userId"], "itemId": it["itemId"],
                              "correct": int(rrng.random() < p),
                              "date": ref_minus(rrng.uniform(5, 400)).date().isoformat()})
    return {
        "_meta": meta("MCQ item bank with 2PL parameters (a = discrimination, b = difficulty on the FRAC level "
                      "scale) and Bloom level, plus response logs simulated FROM THOSE SAME PARAMETERS. "
                      "Calibrated on synthetic data — demo only. Stems/options are placeholders. No accuracy "
                      "metric computed on these responses means anything: it would be circular."),
        "model": "2PL: P(correct | theta) = 1 / (1 + exp(-a (theta - b)))",
        "calibration": "synthetic — demo only",
        "items": items,
        "responses": responses,
    }


def zlib_short(text: str) -> int:
    return int(hashlib.sha1(text.encode()).hexdigest()[:8], 16)


def dumps_records(doc: dict, list_keys: tuple) -> str:
    """JSON with the big record lists written one record per line."""
    parts = []
    for k, v in doc.items():
        if k in list_keys:
            rows = ",\n".join("  " + json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in v)
            parts.append(f"{json.dumps(k)}: [\n{rows}\n]")
        else:
            parts.append(f"{json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}")
    return "{\n" + ",\n".join(parts) + "\n}\n"


# ─────────────────────────────────────────────────────────────────────────────
# Writing
# ─────────────────────────────────────────────────────────────────────────────

def dumps(obj, compact: bool = False) -> str:
    if compact:   # one record per line — large, rarely hand-read files
        if isinstance(obj, dict):
            body = ",\n".join(f"{json.dumps(k)}:{json.dumps(v, ensure_ascii=False, separators=(',', ':'))}"
                              for k, v in obj.items())
            return "{\n" + body + "\n}\n"
        body = ",\n".join(json.dumps(v, ensure_ascii=False, separators=(",", ":")) for v in obj)
        return "[\n" + body + "\n]\n"
    return json.dumps(obj, ensure_ascii=False, indent=1) + "\n"


def meta(note: str) -> dict:
    return {"synthetic": True, "generator": GENERATOR, "seed": SEED, "referenceDate": REF_DATE.isoformat(),
            "note": note}


def generate() -> dict:
    """Build every file in memory → {relative path: text}."""
    with open(os.path.join(HERE, "mockdata", "roster_seed.json"), encoding="utf-8") as fh:
        roster_seed = json.load(fh)["officials"]
    with open(os.path.join(HERE, "competencies.json"), encoding="utf-8") as fh:
        igot_dictionary = json.load(fh)

    frac = build_frac()
    catalog, hidden = build_catalog(frac)
    users, roles, facts = build_officials(roster_seed, catalog)
    enrollments, states, planted = build_enrollments(users, catalog, facts)
    outcomes, outcome_truth = build_outcomes(catalog, enrollments, users, facts, hidden, planted["outOfOrder"])
    workplace, workplace_truth = build_workplace_evidence(users, enrollments, catalog, facts)

    files = {
        "frac_competencies.json": dumps(frac),
        "course_catalog.json": dumps(catalog),
        "userdata.json": dumps(users, compact=True),
        "enrollments.json": dumps(enrollments, compact=True),
        "content_states.json": dumps(states, compact=True),
        "frac_crosswalk.json": dumps(build_crosswalk(igot_dictionary)),
        "gsbpm_map.json": dumps(build_gsbpm_map()),
        "offices.json": dumps(build_offices(users)),
        "acbp.json": dumps(build_acbp(roles, users, catalog)),
        "prerequisites.json": dumps(build_prerequisites()),
        "course_outcomes.json": dumps_records(outcomes, ("outcomes", "comparisons")),
        "workplace_evidence.json": dumps_records(workplace, ("rows",)),
        "hrms.json": dumps(build_hrms(users)),
        "item_bank.json": dumps_records(build_item_bank(users, facts), ("items", "responses")),
        "roles.json": dumps({"_meta": meta("Role (office × designation) competency profiles; requiredLevel "
                                           "drawn from the designation tier."), "roles": roles}),
        "_truth/planted_effects.json": dumps({
            "_meta": meta("GROUND TRUTH for tests and recovery checks only. The mock server never serves "
                          "this file and the backend never reads it."),
            "overclaimers": facts["overclaimers"],
            "profileIncomplete": facts["profileIncomplete"],
            "outOfOrder": planted["outOfOrder"],
            "zeroUpliftCourses": hidden["zeroUpliftCourses"],
            "trueLevels": facts["truth"],
            **outcome_truth,
            **workplace_truth,
        }),
    }
    manifest = {
        "_meta": meta("Every file listed here is synthetic, produced by the generator below. List-shaped "
                      "files keep their original format; this manifest is their synthetic-data label."),
        "files": {
            name: {"synthetic": True, "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                   "bytes": len(text.encode("utf-8"))}
            for name, text in sorted(files.items())
        },
    }
    files["MANIFEST.json"] = dumps(manifest)
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--check", action="store_true", help="compare with files on disk, write nothing")
    args = ap.parse_args()
    files = generate()
    if args.check:
        stale = []
        for name, text in files.items():
            path = os.path.join(DATA_DIR, name)
            if not os.path.exists(path) or open(path, encoding="utf-8", newline="").read() != text:
                stale.append(name)
        print("up to date" if not stale else "stale: " + ", ".join(stale))
        return 1 if stale else 0
    for name, text in files.items():
        path = os.path.join(DATA_DIR, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print(f"  {name:36s} {len(text.encode('utf-8')) / 1024:8.1f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
