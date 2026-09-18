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
            n = weighted(rng, {2: 0.5, 3: 0.4, 4: 0.1})
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
    pool = [c for c in courses if c["format"] == "self_paced_course" and c["level"] in (2, 3)
            and json.loads(c["competencies_v3"])[0]["competencyType"] == "Domain"]
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
                        "progressdetails": {"max_size": size,
                                            "current_size": size if done else rng.randint(1, size - 1),
                                            "mimeType": rng.choice(["video/mp4", "application/pdf", "text/html"])},
                    })
                clist[-1]["completionPercentage"] = clist[-1]["completionPercentage"]
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

    files = {
        "frac_competencies.json": dumps(frac),
        "course_catalog.json": dumps(catalog),
        "userdata.json": dumps(users),
        "enrollments.json": dumps(enrollments),
        "content_states.json": dumps(states, compact=True),
        "frac_crosswalk.json": dumps(build_crosswalk(igot_dictionary)),
        "gsbpm_map.json": dumps(build_gsbpm_map()),
        "offices.json": dumps(build_offices(users)),
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
