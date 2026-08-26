"""
seed_data.py — MoSPI iGOT Karmayogi Data Synthesizer
=====================================================
Generates realistic, high-fidelity mock data adhering strictly to the
Sunbird / FRAC architecture report.  Run once before starting the server.

Output files (written to ./data/):
  frac_competencies.json   — 40 FRAC competency objects
  course_catalog.json      — 200 CBP course objects
  users.json               — 150 official user profiles
  enrollments.json         — UserEnrolment records for every user

Usage:
  pip install faker
  python seed_data.py
"""

import json
import random
import uuid
import os
from datetime import datetime, timedelta, timezone
from faker import Faker

fake = Faker("en_IN")
random.seed(42)
Faker.seed(42)

# ─────────────────────────────────────────────────────────────
# Helper utilities
# ─────────────────────────────────────────────────────────────

def iso_ts(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

def rand_past_dt(days_back: int = 365) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=random.randint(1, days_back))

def do_id() -> str:
    """Generate a Sunbird content-object identifier."""
    return "do_" + str(random.randint(1130000000000, 1139999999999))

def usr_id() -> str:
    return "usr_" + str(random.randint(100000000, 999999999))

def batch_id(course_id: str) -> str:
    return "batch_" + course_id[3:] + "_01"

# ─────────────────────────────────────────────────────────────
# 1. FRAC Competency Dictionary (~40 competencies)
# ─────────────────────────────────────────────────────────────

FRAC_DEFINITIONS = [
    # Statistical / Domain competencies (MoSPI-specific)
    ("comp_nat_accounts_001",  "National Accounts Framework (SNA 2008)",         "Domain"),
    ("comp_survey_design_002", "Survey Design & Sampling Methodology",            "Domain"),
    ("comp_price_stats_003",   "Price Statistics & CPI Construction",             "Domain"),
    ("comp_index_numbers_004", "Index Number Theory & Practice",                  "Domain"),
    ("comp_ml_stats_005",      "Machine Learning for Official Statistics",         "Domain"),
    ("comp_big_data_006",      "Big Data Integration in NSS Surveys",             "Domain"),
    ("comp_econ_census_007",   "Economic Census Planning & Execution",            "Domain"),
    ("comp_dem_analysis_008",  "Demographic Analysis & Population Estimation",    "Domain"),
    ("comp_agri_stats_009",    "Agricultural Statistics & Crop Forecasting",      "Domain"),
    ("comp_industry_stats_010","Industrial Statistics & ASI Methodology",         "Domain"),
    ("comp_gdp_nowcast_011",   "GDP Nowcasting Techniques",                       "Domain"),
    ("comp_spatial_stat_012",  "Spatial Statistics & GIS for Surveys",            "Domain"),
    ("comp_time_series_013",   "Time Series Analysis & Seasonal Adjustment",      "Domain"),
    ("comp_poverty_014",       "Poverty Measurement & Welfare Indicators",        "Domain"),
    ("comp_sdg_monitor_015",   "SDG Monitoring & Voluntary National Review",      "Domain"),
    # Functional competencies (cross-cutting)
    ("comp_data_gov_016",      "Data Governance & Quality Assurance",             "Functional"),
    ("comp_python_stats_017",  "Python for Statistical Computing",                "Functional"),
    ("comp_r_analytics_018",   "R for Advanced Analytics",                        "Functional"),
    ("comp_data_viz_019",      "Data Visualization & Dashboard Design",           "Functional"),
    ("comp_report_writing_020","Report Writing for Statistical Publications",     "Functional"),
    ("comp_procurement_021",   "Government Procurement & GFR Compliance",         "Functional"),
    ("comp_rtt_022",           "Right to Information & Transparency",             "Functional"),
    ("comp_e_gov_023",         "e-Governance Platforms & Digital Services",       "Functional"),
    ("comp_project_mgmt_024",  "Project Management in Government Context",        "Functional"),
    ("comp_public_fin_025",    "Public Financial Management & Budget Analysis",   "Functional"),
    ("comp_data_privacy_026",  "Data Privacy, Security & IT Act Compliance",      "Functional"),
    ("comp_cloud_infra_027",   "Cloud Infrastructure for Statistical Systems",    "Functional"),
    ("comp_api_int_028",       "API Integration & Interoperability Standards",    "Functional"),
    ("comp_db_design_029",     "Database Design & SQL for Statistical Databases", "Functional"),
    ("comp_statistical_sw_030","Statistical Software Proficiency (SPSS / SAS)",   "Functional"),
    # Behavioural competencies
    ("comp_strategic_031",     "Strategic Thinking",                              "Behavioural"),
    ("comp_leadership_032",    "Leadership & Team Management",                    "Behavioural"),
    ("comp_comm_032",          "Effective Communication & Stakeholder Engagement","Behavioural"),
    ("comp_prob_solve_033",    "Problem Solving & Critical Analysis",             "Behavioural"),
    ("comp_integrity_034",     "Integrity, Ethics & Public Service Values",       "Behavioural"),
    ("comp_change_mgmt_035",   "Change Management & Adaptability",                "Behavioural"),
    ("comp_collab_036",        "Collaboration & Interpersonal Effectiveness",     "Behavioural"),
    ("comp_decision_037",      "Decision Making Under Uncertainty",               "Behavioural"),
    ("comp_innov_038",         "Innovation & Creative Problem Solving",           "Behavioural"),
    ("comp_citizen_039",       "Citizen-Centric Service Delivery",                "Behavioural"),
]

LEVEL_TEMPLATES = {
    "Domain": [
        "Demonstrates foundational awareness of {name} concepts and terminology.",
        "Applies {name} principles under supervision in routine statistical tasks.",
        "Independently executes {name} workflows and interprets outputs.",
        "Leads {name} projects; mentors junior officers and reviews methodology.",
        "Recognized expert in {name}; shapes national policy and research agenda.",
    ],
    "Functional": [
        "Aware of {name} tools and processes; requires significant guidance.",
        "Operates {name} tools for standard tasks with occasional support.",
        "Proficient in {name}; handles complex scenarios independently.",
        "Advanced practitioner; trains peers and improves {name} processes.",
        "Subject matter expert; defines organizational standards for {name}.",
    ],
    "Behavioural": [
        "Demonstrates basic awareness of {name} in day-to-day interactions.",
        "Applies {name} skills in familiar, structured situations.",
        "Consistently demonstrates {name} across varied and ambiguous situations.",
        "Role-models {name}; actively coaches others to develop this capability.",
        "Institutionalizes {name}; influences culture and organizational strategy.",
    ],
}

def build_frac_competencies() -> list:
    competencies = []
    for comp_id, name, comp_type in FRAC_DEFINITIONS:
        children = []
        templates = LEVEL_TEMPLATES[comp_type]
        for lvl in range(1, 6):
            children.append({
                "id": f"{comp_id}_lvl_{lvl}",
                "type": "CompetencyLevel",
                "name": f"Level {lvl}",
                "level": lvl,
                "description": templates[lvl - 1].format(name=name),
            })
        competencies.append({
            "id": comp_id,
            "type": "Competency",
            "name": name,
            "description": fake.paragraph(nb_sentences=2),
            "competencyType": comp_type,
            "source": "FRAC_Dictionary_v1",
            "status": "Live",
            "children": children,
        })
    return competencies


# ─────────────────────────────────────────────────────────────
# 2. Course Catalog — 200 CBP courses
# ─────────────────────────────────────────────────────────────

COURSE_PREFIXES = [
    "Fundamentals of", "Advanced", "Applied", "Introduction to",
    "Mastering", "Essentials of", "Practical", "Workshop on",
    "Certification in", "Deep Dive into", "Refresher:", "Executive Programme on",
]

MOSPI_TOPICS = [
    "National Accounts Statistics", "Survey Methodology",
    "Price & Consumer Statistics", "Big Data in Governance",
    "Machine Learning for Policy", "Data Governance",
    "Statistical Computing with Python", "R for Data Analysis",
    "Economic Census Operations", "Agricultural Statistics",
    "Industrial Statistics", "GDP Estimation Techniques",
    "SDG Indicator Monitoring", "Poverty & Social Statistics",
    "Demographic Methods", "Spatial Analysis for Surveys",
    "Time Series Econometrics", "Data Visualization",
    "Government Financial Management", "Public Procurement & GFR",
    "Right to Information Act", "e-Governance & Digital India",
    "Data Privacy & IT Act", "Cloud Computing for Statistics",
    "Database Administration for NSS", "Leadership in Public Service",
    "Strategic Planning for MoSPI", "Communication for Officials",
    "Decision Making Under Uncertainty", "Ethics in Government",
]

ORGANIZATIONS = [
    "Ministry of Statistics and Programme Implementation",
    "National Statistical Office",
    "Central Statistics Office",
    "National Academy of Statistical Administration",
    "iGOT Karmayogi Platform",
    "NITI Aayog — Statistics Division",
    "Department of Personnel and Training",
]

CHANNELS = [
    "igot-mdo-mospi-01",
    "igot-mdo-nasa-02",
    "igot-mdo-cso-03",
    "igot-mdo-dopt-04",
]


def build_course_catalog(competencies: list) -> list:
    comp_ids = [c["id"] for c in competencies]
    courses = []
    used_ids: set = set()

    for i in range(200):
        cid = do_id()
        while cid in used_ids:
            cid = do_id()
        used_ids.add(cid)

        prefix = random.choice(COURSE_PREFIXES)
        topic = random.choice(MOSPI_TOPICS)
        name = f"{prefix} {topic}"

        leaf_count = random.randint(8, 30)
        child_nodes = [do_id() for _ in range(leaf_count)]

        # Pick 1-3 competencies for this course
        course_comps_raw = random.sample(competencies, k=random.randint(1, 3))
        competencies_v3_list = []
        for cc in course_comps_raw:
            level = random.choice(cc["children"])
            competencies_v3_list.append({
                "id": cc["id"],
                "name": cc["name"],
                "competencyType": cc["competencyType"],
                "competencyLevel": level["name"],
            })

        courses.append({
            "identifier": cid,
            "name": name,
            "description": fake.paragraph(nb_sentences=3),
            "channel": random.choice(CHANNELS),
            "contentType": "Course",
            "mimeType": "application/vnd.ekstep.content-collection",
            "status": "Live",
            "versionKey": str(random.randint(1590000000000, 1699999999999)),
            "primaryCategory": "Course",
            "duration": str(random.randint(60, 480)),      # minutes, as string per Sunbird spec
            "leafNodesCount": leaf_count,
            "creator": random.choice(ORGANIZATIONS),
            "organisation": [random.choice(ORGANIZATIONS)],
            "competencies_v3": json.dumps(competencies_v3_list),  # stringified per FRAC spec
            "childNodes": child_nodes,
            "objectType": "Content",
            "compatibilityLevel": random.randint(1, 5),
            "audience": ["Learner"],
            "language": ["English"],
            "createdOn": iso_ts(rand_past_dt(500)),
            "lastPublishedOn": iso_ts(rand_past_dt(30)),
        })
    return courses


# ─────────────────────────────────────────────────────────────
# 3. Users — 150 MoSPI Officials
# ─────────────────────────────────────────────────────────────

DESIGNATIONS = [
    "Deputy Director", "Director", "Joint Director", "Senior Statistical Officer",
    "Statistical Officer", "Joint Secretary", "Under Secretary",
    "Assistant Director General", "Director General", "Data Analyst",
]

DEPARTMENTS = [
    "National Accounts Division", "Price Statistics Division",
    "Survey Coordination Division", "Economic Statistics Division",
    "Social Statistics Division", "IT & Data Management Division",
    "Training & Capacity Building Division", "International Cooperation Division",
]

GOV_EMAIL_DOMAINS = ["mospi.gov.in", "nso.gov.in", "nasa.gov.in", "nic.in"]

ORG_IDS = [
    "org_mospi_001", "org_nso_002", "org_nasa_003",
    "org_cso_004", "org_dopt_005",
]
ORG_NAMES = [
    "Ministry of Statistics and Programme Implementation",
    "National Statistical Office",
    "National Academy of Statistical Administration",
    "Central Statistics Office",
    "Department of Personnel and Training",
]


def build_users(competencies: list) -> list:
    users = []
    used_ids: set = set()

    for _ in range(150):
        uid = usr_id()
        while uid in used_ids:
            uid = usr_id()
        used_ids.add(uid)

        fn = fake.first_name()
        ln = fake.last_name()
        designation = random.choice(DESIGNATIONS)
        department = random.choice(DEPARTMENTS)
        org_idx = random.randint(0, len(ORG_IDS) - 1)
        org_id = ORG_IDS[org_idx]
        org_name = ORG_NAMES[org_idx]

        # Assign 2-5 competencies with random current levels
        user_comps_raw = random.sample(competencies, k=random.randint(2, 5))
        profile_competencies = []
        for uc in user_comps_raw:
            lvl = random.choice(uc["children"])
            status = random.choice(["ACQUIRED", "IN_PROGRESS", "PLANNED"])
            profile_competencies.append({
                "id": uc["id"],
                "name": uc["name"],
                "type": uc["competencyType"],
                "status": status,
                "competencyLevel": lvl["name"],
            })

        users.append({
            "id": uid,
            "userId": uid,
            "firstName": fn,
            "lastName": ln,
            "email": f"{fn.lower()}.{ln.lower()}@{random.choice(GOV_EMAIL_DOMAINS)}",
            "status": 1,
            "channel": random.choice(CHANNELS),
            "rootOrgId": org_id,
            "roles": ["PUBLIC"],
            "organisations": [
                {
                    "organisationId": org_id,
                    "roles": random.sample(["PUBLIC", "CONTENT_REVIEWER", "CONTENT_CREATOR"], k=random.randint(1, 2)),
                    "orgName": org_name,
                    "isDeleted": False,
                    "hashTagId": org_id,
                }
            ],
            "profileDetails": {
                "professionalDetails": [
                    {
                        "designation": designation,
                        "department": department,
                        "industry": "Government Administration",
                        "location": fake.city(),
                    }
                ],
                "competencies": profile_competencies,
            },
            "govId": "EMP-" + str(random.randint(1000, 9999)),
            "experienceYears": random.randint(1, 30),
            "createdDate": iso_ts(rand_past_dt(1000)),
        })

    # Inject our known demo user
    users.append({
        "id": "usr_EMP8472",
        "userId": "usr_EMP8472",
        "firstName": "Priya",
        "lastName": "Sharma",
        "email": "priya.sharma@mospi.gov.in",
        "status": 1,
        "channel": "igot-mdo-mospi-01",
        "rootOrgId": "org_mospi_001",
        "roles": ["PUBLIC"],
        "organisations": [
            {
                "organisationId": "org_mospi_001",
                "roles": ["PUBLIC", "CONTENT_REVIEWER"],
                "orgName": "Ministry of Statistics and Programme Implementation",
                "isDeleted": False,
                "hashTagId": "org_mospi_001",
            }
        ],
        "profileDetails": {
            "professionalDetails": [
                {
                    "designation": "Deputy Director",
                    "department": "National Accounts Division",
                    "industry": "Government Administration",
                    "location": "New Delhi",
                }
            ],
            "competencies": [
                {"id": "comp_nat_accounts_001", "name": "National Accounts Framework (SNA 2008)",      "type": "Domain",       "status": "IN_PROGRESS",  "competencyLevel": "Level 2"},
                {"id": "comp_survey_design_002","name": "Survey Design & Sampling Methodology",        "type": "Domain",       "status": "ACQUIRED",     "competencyLevel": "Level 3"},
                {"id": "comp_data_viz_019",     "name": "Data Visualization & Dashboard Design",       "type": "Functional",   "status": "ACQUIRED",     "competencyLevel": "Level 2"},
                {"id": "comp_strategic_031",    "name": "Strategic Thinking",                          "type": "Behavioural",  "status": "IN_PROGRESS",  "competencyLevel": "Level 1"},
                {"id": "comp_ml_stats_005",     "name": "Machine Learning for Official Statistics",    "type": "Domain",       "status": "PLANNED",      "competencyLevel": "Level 1"},
            ],
        },
        "govId": "EMP-8472",
        "experienceYears": 8,
        "createdDate": "2018-04-01T09:00:00.000Z",
    })

    return users


# ─────────────────────────────────────────────────────────────
# 4. Enrolments — realistic UserEnrolment records
# ─────────────────────────────────────────────────────────────

def build_enrollments(users: list, courses: list) -> list:
    all_enrollments = []
    course_pool = courses

    for user in users:
        uid = user["userId"]
        num_courses = random.randint(2, 6)
        enrolled_courses = random.sample(course_pool, k=min(num_courses, len(course_pool)))

        for course in enrolled_courses:
            enroll_dt = rand_past_dt(400)
            leaf_count = course["leafNodesCount"]
            status_roll = random.random()

            if status_roll > 0.6:
                # COMPLETED
                macro_status = 2
                progress = leaf_count
                completion_pct = 100
                last_content_status = 2
                certs = [{
                    "identifier": "cert_" + str(random.randint(100000, 999999)),
                    "name": "Completion Certificate",
                    "token": str(uuid.uuid4())[:8].upper()
                }]
            elif status_roll > 0.25:
                # IN_PROGRESS
                macro_status = 1
                progress = random.randint(1, leaf_count - 1)
                completion_pct = round((progress / leaf_count) * 100)
                last_content_status = 1
                certs = []
            else:
                # NOT STARTED
                macro_status = 0
                progress = 0
                completion_pct = 0
                last_content_status = 0
                certs = []

            last_read_node = random.choice(course["childNodes"]) if course["childNodes"] else "do_000000000000"

            record = {
                "active": True,
                "courseId": course["identifier"],
                "courseName": course["name"],
                "contentId": course["identifier"],
                "batchId": batch_id(course["identifier"]),
                "userId": uid,
                "enrolledDate": iso_ts(enroll_dt),
                "status": macro_status,
                "completionPercentage": completion_pct,
                "progress": progress,
                "leafNodesCount": leaf_count,
                "lastReadContentId": last_read_node,
                "lastReadContentStatus": last_content_status,
                "issuedCertificates": certs,
                "channel": user["channel"],
            }
            all_enrollments.append(record)

    # Inject rich demo enrolments for EMP-8472
    demo_uid = "usr_EMP8472"
    # Remove any auto-generated records for demo user first
    all_enrollments = [e for e in all_enrollments if e["userId"] != demo_uid]

    # Find specific courses by competency relevance
    sna_course  = next((c for c in courses if "National Accounts" in c["name"]), courses[0])
    ml_course   = next((c for c in courses if "Machine Learning" in c["name"]), courses[1])
    surv_course = next((c for c in courses if "Survey" in c["name"]), courses[2])
    viz_course  = next((c for c in courses if "Visualization" in c["name"]), courses[3])
    gdp_course  = next((c for c in courses if "GDP" in c["name"]), courses[4])

    demo_enrollments = [
        # SNA course — IN_PROGRESS (matches skill gap)
        {
            "active": True, "courseId": sna_course["identifier"], "courseName": sna_course["name"],
            "contentId": sna_course["identifier"], "batchId": batch_id(sna_course["identifier"]),
            "userId": demo_uid, "enrolledDate": "2026-06-01T09:00:00.000Z",
            "status": 1, "completionPercentage": 65,
            "progress": int(sna_course["leafNodesCount"] * 0.65),
            "leafNodesCount": sna_course["leafNodesCount"],
            "lastReadContentId": sna_course["childNodes"][2] if len(sna_course["childNodes"]) > 2 else sna_course["childNodes"][0],
            "lastReadContentStatus": 1, "issuedCertificates": [], "channel": "igot-mdo-mospi-01",
        },
        # Survey course — COMPLETED
        {
            "active": True, "courseId": surv_course["identifier"], "courseName": surv_course["name"],
            "contentId": surv_course["identifier"], "batchId": batch_id(surv_course["identifier"]),
            "userId": demo_uid, "enrolledDate": "2025-10-01T09:00:00.000Z",
            "status": 2, "completionPercentage": 100,
            "progress": surv_course["leafNodesCount"],
            "leafNodesCount": surv_course["leafNodesCount"],
            "lastReadContentId": surv_course["childNodes"][-1],
            "lastReadContentStatus": 2,
            "issuedCertificates": [{"identifier": "cert_SURV2025", "name": "Completion Certificate", "token": "SURV-4892"}],
            "channel": "igot-mdo-mospi-01",
        },
        # Data Viz — COMPLETED
        {
            "active": True, "courseId": viz_course["identifier"], "courseName": viz_course["name"],
            "contentId": viz_course["identifier"], "batchId": batch_id(viz_course["identifier"]),
            "userId": demo_uid, "enrolledDate": "2025-08-10T09:00:00.000Z",
            "status": 2, "completionPercentage": 100,
            "progress": viz_course["leafNodesCount"],
            "leafNodesCount": viz_course["leafNodesCount"],
            "lastReadContentId": viz_course["childNodes"][-1],
            "lastReadContentStatus": 2,
            "issuedCertificates": [{"identifier": "cert_VIZ2025", "name": "Completion Certificate", "token": "VIZD-3301"}],
            "channel": "igot-mdo-mospi-01",
        },
        # ML course — NOT STARTED
        {
            "active": True, "courseId": ml_course["identifier"], "courseName": ml_course["name"],
            "contentId": ml_course["identifier"], "batchId": batch_id(ml_course["identifier"]),
            "userId": demo_uid, "enrolledDate": "2026-08-20T09:00:00.000Z",
            "status": 0, "completionPercentage": 0,
            "progress": 0,
            "leafNodesCount": ml_course["leafNodesCount"],
            "lastReadContentId": "", "lastReadContentStatus": 0, "issuedCertificates": [],
            "channel": "igot-mdo-mospi-01",
        },
        # GDP course — IN_PROGRESS
        {
            "active": True, "courseId": gdp_course["identifier"], "courseName": gdp_course["name"],
            "contentId": gdp_course["identifier"], "batchId": batch_id(gdp_course["identifier"]),
            "userId": demo_uid, "enrolledDate": "2026-07-05T09:00:00.000Z",
            "status": 1, "completionPercentage": 30,
            "progress": max(1, int(gdp_course["leafNodesCount"] * 0.30)),
            "leafNodesCount": gdp_course["leafNodesCount"],
            "lastReadContentId": gdp_course["childNodes"][1] if len(gdp_course["childNodes"]) > 1 else gdp_course["childNodes"][0],
            "lastReadContentStatus": 1, "issuedCertificates": [], "channel": "igot-mdo-mospi-01",
        },
    ]
    all_enrollments.extend(demo_enrollments)
    return all_enrollments


# ─────────────────────────────────────────────────────────────
# 5. Build content-state snapshots (granular leaf-level progress)
# ─────────────────────────────────────────────────────────────

def build_content_states(enrollments: list, courses: list) -> dict:
    """
    Produces a lookup: (userId, courseId, batchId) -> contentList snapshot.
    This is used by the POST /api/course/v1/content/state/read endpoint.
    """
    course_map = {c["identifier"]: c for c in courses}
    states: dict = {}

    MIME_TYPES = ["video/mp4", "application/pdf", "video/webm", "text/html", "application/epub"]

    for enrol in enrollments:
        uid   = enrol["userId"]
        cid   = enrol["courseId"]
        bid   = enrol["batchId"]
        key   = f"{uid}|{cid}|{bid}"
        course = course_map.get(cid)
        if not course:
            continue

        progress      = enrol["progress"]
        leaf_count    = enrol["leafNodesCount"]
        child_nodes   = course["childNodes"]
        content_list  = []

        for idx, node_id in enumerate(child_nodes):
            if idx < progress:
                # consumed
                mime = random.choice(MIME_TYPES)
                max_sz = random.randint(10000, 90000)
                content_list.append({
                    "contentId": node_id,
                    "status": 2,
                    "completionPercentage": 100,
                    "lastAccessTime": iso_ts(rand_past_dt(60)),
                    "progressdetails": {"max_size": max_sz, "current_size": max_sz, "mimeType": mime},
                })
            elif idx == progress and enrol["status"] == 1:
                # currently reading
                mime = random.choice(MIME_TYPES)
                max_sz = random.randint(10000, 90000)
                curr_sz = random.randint(1, max_sz - 1)
                content_list.append({
                    "contentId": node_id,
                    "status": 1,
                    "completionPercentage": round((curr_sz / max_sz) * 100),
                    "lastAccessTime": iso_ts(rand_past_dt(5)),
                    "progressdetails": {"max_size": max_sz, "current_size": curr_sz, "mimeType": mime},
                })

        states[key] = {
            "contentList": content_list,
            "lastReadContentId": enrol["lastReadContentId"],
            "completionPercentage": enrol["completionPercentage"],
            "courseId": cid,
            "batchId": bid,
        }
    return states


# ─────────────────────────────────────────────────────────────
# 6. Main — generate and persist all data
# ─────────────────────────────────────────────────────────────

def main():
    os.makedirs("data", exist_ok=True)

    print("⏳  Generating FRAC competencies …")
    competencies = build_frac_competencies()
    with open("data/frac_competencies.json", "w", encoding="utf-8") as f:
        json.dump(competencies, f, indent=2, ensure_ascii=False)
    print(f"✅  {len(competencies)} FRAC competencies → data/frac_competencies.json")

    print("⏳  Generating course catalog (200 CBPs) …")
    courses = build_course_catalog(competencies)
    with open("data/course_catalog.json", "w", encoding="utf-8") as f:
        json.dump(courses, f, indent=2, ensure_ascii=False)
    print(f"✅  {len(courses)} courses → data/course_catalog.json")

    print("⏳  Generating user profiles (150 officials + demo user) …")
    users = build_users(competencies)
    with open("data/users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)
    print(f"✅  {len(users)} users → data/users.json")

    print("⏳  Generating enrolment histories …")
    enrollments = build_enrollments(users, courses)
    with open("data/enrollments.json", "w", encoding="utf-8") as f:
        json.dump(enrollments, f, indent=2, ensure_ascii=False)
    print(f"✅  {len(enrollments)} enrolment records → data/enrollments.json")

    print("⏳  Pre-computing content state snapshots …")
    states = build_content_states(enrollments, courses)
    with open("data/content_states.json", "w", encoding="utf-8") as f:
        json.dump(states, f, indent=2, ensure_ascii=False)
    print(f"✅  {len(states)} content-state snapshots → data/content_states.json")

    print("\n🎉  Data synthesis complete. Run mock_igot_server.py next.")


if __name__ == "__main__":
    main()
