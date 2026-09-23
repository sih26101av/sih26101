# Mock iGOT data (synthetic)

**Everything in this folder is synthetic.** It is shaped like MoSPI / iGOT
Karmayogi data so the platform can be demonstrated end to end. It is not an
export of any real system. No real official, course or score is described here.

## How it is made

One deterministic generator writes every file:

```bash
cd mock-igot-server
python generate_mock_data.py          # rewrite data/*.json (~2 s)
python generate_mock_data.py --check  # exit 1 if a file on disk is stale
```

- **Seed:** `SEED = 20260918`. Each section draws from its own
  `random.Random(f"{SEED}:{section}")` stream, so adding a section never
  reshuffles another.
- **Reference date:** `REF_DATE = 2026-09-15` stands in for "today". Nothing
  reads the clock.
- **Byte-identical:** running the generator twice gives identical bytes. This is
  enforced by `main-lms-backend/tests/test_mock_data.py`, which also fails if the
  committed files are stale.
- **Labels:** `MANIFEST.json` lists every generated file with
  `synthetic: true`, its sha256 and its size. Dict-shaped files also carry a
  top-level `"_meta": {"synthetic": true, "generator", "seed", ...}`.
  List-shaped files (`userdata`, `enrollments`, `course_catalog`,
  `frac_competencies`) keep their original list format, so the manifest is
  their label.
- **Inputs:**
  - `mockdata/domain.py` holds hand-written domain text: competency
    descriptions, topic vocabularies, offices, GSBPM map and designations. Its
    last section merges in the FRAC dictionary extension and adds the pools,
    holes, crosswalk rules and prerequisite edges the new families need.
  - `mockdata/domain_extra.py` holds competencies 041-205 — six hand-written
    families (subject-matter statistics, macro accounts and prices, statistical
    methodology, data/technology, public administration, behavioural). Each
    entry carries its own short name, description, topic vocabulary, GSBPM
    sub-processes, legitimate content overlaps and catalogue depth.
  - `mockdata/roster_seed.json` holds frozen identities (userId, names, email,
    govId, experience, education, career history, tier). It was extracted once
    from the pre-v6 `userdata.json`, so user ids and the default passwords
    (`lowercase(firstName)` + last 2 digits of the userId) still work.
  - `../competencies.json` is the iGOT competency dictionary. It is read only
    to build the crosswalk.
- **Retired generators:** `seed_data.py` now just calls the generator.
  `enrich_catalog.py` and `generate_userdata.py` were removed.

## Files

| File | What | Served by the mock server at |
|---|---|---|
| `frac_competencies.json` | The 205 catalogue FRAC competencies with L1–L5 descriptors (`children`), `decayClass`, `gsbpm` | `GET /api/frac/competencies` |
| `course_catalog.json` | The one course catalogue (1,785 courses) | `POST /api/composite/v1/search`, `GET /api/content/read`, `GET /api/courses/enriched`, `GET /api/external/igot/catalog` |
| `userdata.json` | 151 officials: identity, `jobProfile` (`roleId`, `officeId`, `tier`), role competencies with self-reports | `GET /api/user/v2/read/{id}`, `GET /api/admin/v1/users` |
| `roles.json` | 81 role profiles (office × designation) and their required levels | (read at startup) |
| `enrollments.json` | 988 enrolments. Status 2 ⇔ 100%, with `completedDate` | `GET /api/course/v1/user/enrollment/list/{id}` |
| `content_states.json` | Leaf-level progress for **in-progress** enrolments only. Completed ones are derived at request time | `POST /api/course/v1/content/state/read` |
| `frac_crosswalk.json` | iGOT dictionary CID id → catalogue FRAC id, keyword rules, `confirmed: false` for all | `GET /api/frac/v1/crosswalk` |
| `gsbpm_map.json` | GSBPM v5.1 phases and sub-processes (+ `OA.*` overarching), FRAC competency → sub-processes | `GET /api/gsbpm/v1/map` |
| `offices.json` | 16 offices: sub-processes run in `FY2026-27-Q2` with officer-hours each, headcount, products | `GET /api/org/v1/offices[/{id}]` |
| `acbp.json` | Annual Capacity Building Plan FY2026-27: org-wide + per-role APAR-linked mandatory courses, learning hours per quarter per official | `GET /api/cbplan/v1/user/{id}` |
| `prerequisites.json` | 43 expert-seeded prerequisite edges (competency@level → competency@level), acyclic | `GET /api/frac/v1/prerequisites` |
| `course_outcomes.json` | Platform-wide, anonymised pre/post θ course assessments + non-taker comparison episodes (one record per line) | `GET /api/course/v1/assessment/outcomes` |
| `hrms.json` | HRMS-style records: DOB, joining, superannuation (60, month end), products each official works on; product → critical competencies | `GET /api/hrms/v1/officials` |
| `item_bank.json` | 2,770 MCQ items (2PL `a`/`b`, Bloom level) per competency × level, plus a synthetic response log. **Calibrated on synthetic data — demo only** | `GET /api/assessment/v1/itembank` |
| `workplace_evidence.json` | EvidenceLog-style rows: SUPERVISOR_RATING (lenient + halo), UTILITY (will-use + confirmation), WORK_SAMPLE (auto-graded, 15 competencies), PEER_RATING (never scored) | `GET /api/evidence/v1/user/{id}` |
| `_truth/planted_effects.json` | **Ground truth for tests only**: latent true levels and planted effects. The server never serves it and the backend never reads it | (not served) |
| `MANIFEST.json` | Synthetic-data label + hashes | (not served) |

**No longer loaded:**
- `../courses.json` and `../courses_1.json` are real iGOT catalogue exports.
  They used to be served next to `course_catalog.json`, so the catalogue the
  engine ranked could drift from the one the server served. They stay on disk
  as reference only; nothing loads them apart from the legacy `../main.py`.
- `data/users.json` was the old `seed_data.py` output. It had different names
  for the same user ids and nothing read it, so it was deleted.

## Distributions (named constants live in `generate_mock_data.py` / `mockdata/domain.py`)

### The FRAC dictionary (205 competencies)

The catalogue is one flat competency space. The first 40 ids
(`comp_nat_accounts_001` … `comp_citizen_039`, listed in
`domain.CORE_COMPETENCY_IDS`) are the original set and never move; 165 more
(`…_041` … `…_205`) come from `mockdata/domain_extra.py` in six families:

| Family | Count | Examples |
|---|---|---|
| Subject-matter statistics | 39 | labour force, education, health, gender, energy, environment, trade, MSME, time use, population census, business register |
| Macro accounts & prices | 21 | supply-use tables, quarterly national accounts, regional accounts, government finance statistics, producer prices, deflators, PPP |
| Statistical methodology & field operations | 35 | small area estimation, calibration, imputation, record linkage, disclosure control, questionnaire design, CAPI, field supervision, tabulation |
| Data engineering, platforms & applied AI | 35 | data engineering, warehousing, DevOps, containers, cybersecurity, NLP, satellite imagery, MLOps, AI governance, differential privacy |
| Public administration, law & programme management | 20 | parliament work, vigilance, establishment rules, audit, litigation, grievances, records, training design, M&E, risk |
| Behavioural | 15 | emotional intelligence, negotiation, resilience, coaching, inclusion, attention to detail, systems thinking, feedback |

By FRAC category the whole dictionary is 103 Domain, 77 Functional and 25
Behavioural competencies (the original 40 were 15 / 15 / 10).

**Catalogue depth (`domain.CATALOG_DEPTH`)** is what keeps a five-fold bigger
dictionary from meaning a five-fold bigger everything. Each competency is
`core` (the original 40), `standard` (104) or `thin` (61), and the depth drives
courses per level, item-bank size and how many comparison episodes the outcome
file carries. Real catalogues are deepest where demand is; the long tail is
thin on purpose.

### Roles and officials (A1)

- **Offices:** 16 offices (NAD, PSD, ESD, ISW-ASI, SSD, SDRD, two FOD zones,
  DPD, CAPD, DQAD, NSSTA, plus IPMD — Infrastructure & Project Monitoring,
  DSL — Data Science & Emerging Technology Lab (Bengaluru), INTL —
  International Cooperation & Statistical Standards, and ADMIN —
  Administration, Establishment & Vigilance). An official's office comes from
  their old department string where one maps; the four new divisions share the
  MoSPI and IT department strings with the older ones, so the roster fans out
  across all 16.
- **Office subject pools:** each office's `core` dict in `domain.OFFICES` names
  the subjects it owns, extended by `OFFICE_CORE_EXTRA` (e.g. SSD picks up the
  social-statistics family, SDRD the survey-methodology family, DPD the data
  engineering family, FOD the field-operations family). 118 of the 205
  competencies are required by at least one role; the rest exist in the
  dictionary and the catalogue without being anybody's job requirement, which
  is what a real FRAC slice looks like.
- **Designation:** set by tier and experience (ISS/SSS ladder).
- **Role competencies:** 4–8 per role. Every role requires its office's lead
  subject. Then it draws 1–2 more domain, 1–3 functional and 1–3 behavioural
  competencies (by tier).
- **`requiredLevel` by tier (`REQUIRED_LEVEL_BY_TIER`):**

  | Tier | L1 | L2 | L3 | L4 | L5 |
  |---|---|---|---|---|---|
  | junior | 5% | 55% | 40% | – | – |
  | mid | – | 20% | 55% | 25% | – |
  | senior | – | – | 25% | 55% | 20% |
  | apex | – | – | 10% | 45% | 45% |

  A senior or apex role's lead subject is at least L4.
- **Latent true level:** the gap to target is 0 / 1 / 2 / 3 with probability
  .22 / .40 / .26 / .12. Senior officials never have a gap of 3. 20% of those
  who meet their target exceed it by one level.
- **Self-report (`competencyLevel`):**
  - Truth ±1 with probability .2 / .6 / .2.
  - `OVERCLAIMER_P = 0.10`: about 10% of officials over-claim by 1–2 levels on
    about 70% of their competencies.
  - `SELF_REPORT_MISSING_P = 0.10`: about 10% of competencies have no
    self-report.
- **`status`:** the official's own declaration. `ACQUIRED` if the claim meets
  the requirement, `IN_PROGRESS` if a course on it is under way, else `PLANNED`.
- **Profile-incomplete officials (`N_PROFILE_INCOMPLETE = 3`):** the three most
  junior officials have no education or career history (`profileStatus:
  HRMS_SYNC_PENDING`). This is what makes `UNASSESSED` reachable: every other
  profile has tenure and education evidence.

### Catalogue (A2 / A3)

- **Courses per cell (`domain.COURSES_PER_CELL`, by catalogue depth):**

  | Depth | Courses per competency × level | Courses per competency (min / median / max) |
  |---|---|---|
  | `core` (40) | 2 / 3 / 4 with probability .5 / .4 / .1 | 8 / 12 / 18 |
  | `standard` (104) | 1 / 2 / 3 with probability .35 / .50 / .15 | 5 / 9 / 13 |
  | `thin` (61) | 1 / 2 with probability .70 / .30 | 3 / 5 / 9 |

  That is 1,785 courses over 981 of the 1,025 competency × level cells.
- **Titles and descriptions:** built from each competency's own topic
  vocabulary. Every description quotes the FRAC level descriptor of its tag.
- **Level words in titles:** Introduction / Basics / Getting Started → L1;
  Fundamentals / Essentials / Foundations → L2; Applied / Practitioner /
  Hands-on → L3; Advanced → L4; Masterclass / Leading Practice → L5.
- **Secondary tags:** `SECONDARY_TAG_P = 0.22`, only between pairs in `OVERLAP`
  (real content overlap). The secondary level is the same as the primary or one
  lower, and never falls in a hole. The description names the secondary topic.
- **Formats (`FORMAT_BY_LEVEL`) and hours:**

  | Format | Hours | Modality |
  |---|---|---|
  | `micro_learning` | 0.5–2 | self_paced |
  | `self_paced_course` | 2–8 | self_paced |
  | `nssta_workshop` | 6–16 | virtual_lab 60% / classroom 40% |
  | `tpac_programme` | 24–60, in whole 6-h days | classroom 80% / virtual_lab 20% |

  Higher levels lean longer: `u ** max(0.4, 1.6 − 0.25·level)`.
- **Modules:** `leafNodesCount` = hours × 60 / U(20, 40) minutes per module.
- **Quality fields:**
  - rating 3.0–4.9, driven by a latent course quality.
  - rating_count = enrolments × U(1%, 12%) × lognormal noise, so most counts
    are small and a few are large.
  - enrollment_count is lognormal around 700/√level, and ≤ 450 for classroom
    courses.
  - completion_rate is 0.25–0.9 and falls with hours.
  - `MISSING_QUALITY_P = 0.10`: each field is missing independently.
- **TPAC:** `is_tpac = true` only on NSSTA TPAC programmes. NSSTA workshops and
  self-paced courses say `is_tpac: false` explicitly.

### Enrolments (A5)

- **Completed history:** on 60% of a role's domain/functional competencies and
  35% of its behavioural ones. It covers levels up to the true level: the top
  level with p .75, the one below with p .5, lower ones with p .15.
- **Dates:** completion dates are spread over `HISTORY_YEARS = 3`, with lower
  levels first. `enrolledDate` = `completedDate` − (course days + 0–30 days).
- **Current gaps:** 35% have an in-progress course at true level + 1, and 10%
  have one enrolled but not started.
- **Extras:** 0–3 general-interest courses at L1–L2.

### GSBPM + office workload (B1 / B2)

- `mockdata/domain.py::GSBPM_MAP` lists each competency's sub-processes. These
  are hand-designed, e.g. National Accounts → 5.1, 5.5, 5.7, 6.1–6.3, OA.SM.
- `OFFICES[...]` gives relative sub-process weights per office, and
  `OFFICE_HEADCOUNT` its sanctioned strength (all staff, not only the 151 on the
  roster). The four newer divisions are IPMD 60, DSL 40, INTL 25, ADMIN 90.
- `officerHours = headcount × HOURS_PER_OFFICER_QUARTER (480) × weight share ×
  U(0.85, 1.15)`, rounded to 10 h. Field offices (FOD) dominate the 4.x Collect
  phase, so the 80% rule scopes in collection, validation and aggregation first.
- The GSBPM version is **v5.1** (2019). "5.2" was requested, but its
  sub-process list could not be confirmed.
- On the generated data 15 sub-processes cover 81.1% of 818,570 officer-hours;
  172 of the 205 competencies are in scope and 33 are out.

### ACBP: mandatory courses + learning hours (B3)

- **Organisation-wide mandatory course:** the shortest non-classroom L1 course
  on `comp_data_privacy_026` (information security awareness).
- **Role mandatory course:**
  - Junior and mid tiers: the shortest non-classroom L2 course on the office's
    lead subject.
  - Senior and apex tiers: the shortest non-classroom L3 course on the role's
    first behavioural competency.
  - One role (`role_dsl_joint_director`, whose first behavioural competency has
    no L3 course) has no such course, so only the org-wide course applies to it.
- **`aparLinked: true`** on all mandatory courses.
- **`learningHoursPerQuarter`:** drawn from `LEARNING_HOURS_BY_TIER`
  (junior 16–30, mid 14–30, senior 14–24, apex 14–20). Field-office (FOD)
  staff get 4 h less, with a minimum of 14. Every official therefore has
  ≥ 56 h a year, above the Mission Karmayogi ≥ 50 h/year guidance
  (`KARMAYOGI_MIN_HOURS_PER_YEAR`, quoted in the file's `_meta`).

### Prerequisites + course outcomes (B4 / B5)

**Prerequisites**
- `mockdata/domain.py::EXPERT_PREREQUISITES` holds 43 hand-written edges (18
  original + 25 across the new families), each with a rationale. `generate_mock_data.find_cycle` checks them together with
  the implicit ladder edges `c@L-1 → c@L`, and generation fails on a cycle.

**Course outcomes** (`course_outcomes.json`) — every effect is **planted**. The
ground truth is in `_truth/planted_effects.json`.

- **Learners:**
  - Every completed roster enrolment gets one record (`learnerId` = `usr_…`).
  - Anonymised iGOT learners (`lrn_…`) are added per course:
    `clip(round(enrollment_count / TAKERS_PER_ENROLMENTS (250)), 2, TAKERS_MAX)`,
    where `TAKERS_MAX` is 30 / 14 / 8 by catalogue depth — a niche course has
    fewer learners on the platform, so its uplift interval is wider.
  - Courses in a planted-precedence group get at least `PLANTED_GROUP_TAKERS =
    18` takers, so the effect is testable.
  - The four planted zero-uplift courses get `PLANTED_ZERO_TAKERS = 60`. They
    carry 6k–16k enrolments, so the clip above is the only thing that would
    hold them back, and the estimator needs the volume to doubt them.
- **Pre-course ability:**
  - Normal cases: `pre = level − 1 + U(0.15, 0.85)`.
  - Out-of-order roster learners: their latent θ − 0.3.
- **True course uplift:**
  - `N(TRUE_UPLIFT_MEAN = 0.55, TRUE_UPLIFT_SD = 0.15)`, clipped to
    [0.2, 1.0], so most courses help by about half a level.
  - The 4 planted popular courses get `N(0.02, 0.02)`, i.e. about zero.
- **Fit:** a learner gets 30% of the uplift if already at the course's level,
  and 50% if more than 2 levels below it.
- **Maturation (the confounder):**
  `MATURATION_BASE + MATURATION_SLOPE·pre = 0.03 + 0.05·pre`. Strong officers
  grow faster even without a course, and they are the ones who take advanced
  courses, so a naive takers-vs-non-takers comparison overstates uplift for
  advanced courses.
- **Covariates:** tenure ≈ 3 + 5·pre + N(0, 4); `education`; `priorLevel` =
  ⌊pre⌋.
- **Measurement noise:** `ASSESSMENT_NOISE_SD = 0.20` on each θ.
- **Planted precedence** (`PLANTED_PRECEDENCE`):
  - SPSS/SAS before Survey Design L3: +0.35. This is not an expert edge.
  - Index Numbers before Price Statistics L3: +0.25. This backs an expert edge.
  - `PLANTED_PRIOR_SHARE = 0.5` of those groups did the prerequisite first.
- **Comparison episodes:** `CONTROLS_PER_COMPETENCY` non-takers per competency
  — 60 / 20 / 10 by catalogue depth — with pre ~ U(0.1, 4.9) (spread over all
  ability levels, so every course level has comparable non-takers) and a
  30–120-day interval. A competency carrying one of the planted zero-uplift
  courses gets `CONTROLS_PLANTED_COMPETENCY = 150` instead, so that demo's
  confidence interval is driven by the (absent) effect rather than by how few
  non-takers happened to sit near the takers' ability.

### Workplace evidence (B6)

All values below are named constants in `generate_mock_data.py`.

- **Supervisor ratings (`SUPERVISOR_RATING`):**
  - Each official has one of 4 reporting officers in their office
    (`supervisors` map).
  - `SUPERVISOR_COVERAGE = 0.85` of role competencies are rated in the
    2025-26 APAR cycle (dated May–June 2026).
  - rating = round(θ + leniency_rater + halo_official + noise), clipped to 1–5,
    where:
    - leniency ~ N(`SUPERVISOR_LENIENCY_MEAN = 0.4`, `SUPERVISOR_LENIENCY_SD = 0.3`)
      per rater;
    - halo ~ N(0, `SUPERVISOR_HALO_SD = 0.4`), shared by all of an official's
      ratings;
    - noise ~ N(0, `SUPERVISOR_NOISE_SD = 0.4`).
  - Each rater's true leniency is in `_truth/`.
- **Utility (`UTILITY`)**, one row per completed course in the last 2 years:
  - "will use within `UTILITY_WINDOW_DAYS = 90`": yes with p .75 for a role
    competency, .3 otherwise.
  - Supervisor confirmation (once 90 days have passed): p = .85 / .65 / .35
    for High / Medium / Low opportunity to practise in the official's office,
    halved off-role.
  - `grantedValue` = course level if confirmed, else 0.
- **Work samples (`WORK_SAMPLE`):** `mockdata/domain.py::WORK_SAMPLE_TASKS`
  holds 15 competencies × L2–L4 (the original 10 plus labour force statistics,
  survey weighting, small area estimation, data engineering and tabulation).
  - `WORK_SAMPLE_ATTEMPT_P = 0.5` of eligible officials attempted one at their
    level or the next.
  - score = 100·logistic(2.2·(θ − L)) + N(0, 8); pass at `WORK_SAMPLE_PASS = 70`.
- **Peer ratings (`PEER_RATING`):** on `PEER_RATING_P = 0.15` of role
  competencies, inflated. Shown for context; the backend never scores them.

- New recruits (`profileStatus: HRMS_SYNC_PENDING`) have had no APAR cycle and
  no work sample, so their non-behavioural competencies stay UNASSESSED. This
  is what exercises the cold-start cohort prior.

### Item bank (B7)

- `ITEMS_PER_LEVEL = 3` items per competency × level, or
  `ITEMS_PER_LEVEL_THIN = 2` for a `thin` competency — 2,770 items in all. Even
  the thin banks hold 10 items, above `RESPONSES_PER_OFFICIAL = 8` and enough
  for the adaptive diagnostic's stopping rule to be reached on σ rather than on
  running out of items.
- Discrimination `a ~ U(0.8, 2.0)`, difficulty `b ~ N(level − 0.5, 0.35)`,
  Bloom level by FRAC level. Stems and options are placeholders built from the
  competency's topic vocabulary.
- **The parameters are simulated and the response log is simulated from those
  same parameters.** Any accuracy metric computed on it would be circular; the
  file says so in its `_meta` and every screen that uses it is labelled
  "calibrated on synthetic data — demo only".

### HRMS + decay classes (B8)

- **Ages and dates:**
  - Age = U(`ENTRY_AGE_RANGE` 22–31) + experience, capped at 59.7, so everyone
    is in service on `REF_DATE`.
  - Superannuation = last day of the month of the 60th birthday
    (`RETIREMENT_AGE`). 9 officials retire within 36 months, 3 within 12.
- **Products:** 1–2 of the office's statistical products per official (none
  for NSSTA). `PRODUCT_CRITICAL` in `mockdata/domain.py` lists each product's
  critical competencies.
- **Decay classes:** `frac_competencies.json::decayClass` is `accuracy`
  (methods and tools that go stale) or `procedural` (practised routines and
  behaviours). It is hand-assigned per competency in `mockdata/domain.py`.

## Deliberate holes and planted cases

Ladder holes live in `domain.LADDER_HOLES` and are the single source of truth:
`test_mock_data.py` fails if the catalogue's actual holes differ from that dict
by one cell. 166 of the 205 competencies have courses at every level L1–L5; the
other 39 are listed below.

| What | Where | Why |
|---|---|---|
| No L5 course (29) | `comp_gdp_nowcast_011`, `comp_rtt_022`, `comp_cloud_infra_027`, `comp_citizen_039`, `comp_wage_stats_042`, `comp_child_stats_048`, `comp_disability_stats_049`, `comp_elderly_stats_050`, `comp_water_sanitation_052`, `comp_forest_stats_056`, `comp_transport_stats_057`, `comp_mining_stats_063`, `comp_capital_mkt_066`, `comp_ecommerce_stats_069`, `comp_crime_stats_071`, `comp_migration_stats_073`, `comp_ppp_089`, `comp_horticulture_096`, `comp_exp_design_109`, `comp_nosql_140`, `comp_sre_152`, `comp_mobile_data_159`, `comp_julia_matlab_165`, `comp_enterprise_arch_170`, `comp_rajbhasha_172`, `comp_pension_175`, `comp_social_media_185`, `comp_gender_budget_186`, `comp_disaster_mgmt_190` | Top-of-ladder hole → `partial` / `no_content` paths, coverage-gap detector |
| No L4 **and** L5 course (3) | `comp_insurance_stats_065`, `comp_mplads_099`, `comp_event_mgmt_183` | The only cases a senior-level gap can hit with nothing at all → `no_content` |
| No L3 course (2) | `comp_spatial_stat_012`, `comp_procurement_021` | Mid-ladder hole → `stretch` step via L4 |
| No L1 course (3) | `comp_service_price_092`, `comp_bayesian_107`, `comp_synthetic_data_160` | Specialist subject with no introductory course — the ladder starts at L2 |
| No L1 **and** L5 course (2) | `comp_mixed_mode_117`, `comp_dp_161` | Both ends missing |
| Out-of-order learners (`N_OUT_OF_ORDER = 5`) | `usr_107156607`, `usr_952762961`, `usr_291794383`, `usr_935386554`, `usr_226507324` | Completed an L4 course while truly at L2 → tests the monotone level floor |
| Profile incomplete | `usr_154849742`, `usr_290725138`, `usr_322272362` | `UNASSESSED` competencies exist |
| Over-claimers (14) | listed in `_truth/planted_effects.json` | Self-report above evidence → LOW + diagnostic |
| Popular, highly rated, ~zero true uplift (`N_POPULAR_ZERO_UPLIFT = 4`) | `do_11307047532128943181`, `do_11368863700416458517`, `do_11379891468734557044`, `do_11379911329280409962` | B5: the measured-uplift estimator should flag them; ratings alone would not. Planted only on `core` competencies, which carry the taker and comparison volume needed to doubt a popular course |

Across the 151-official roster these holes are what `no_content` comes from:
99.1% of the roster's competency gaps have a course at every level they need,
0.6% have some of them, and 0.3% (two cases, on `comp_mplads_099` and
`comp_event_mgmt_183`) have none.
