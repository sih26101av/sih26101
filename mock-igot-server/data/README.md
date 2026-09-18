# Mock iGOT data (synthetic)

**Everything in this folder is synthetic.** It is shaped like MoSPI / iGOT
Karmayogi data so the platform can be demonstrated end to end. It is not an
export of any real system. No real official, course or score is described here.

## How it is made

One deterministic generator writes every file:

```bash
cd mock-igot-server
python generate_mock_data.py          # rewrite data/*.json (< 1 s)
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
    descriptions, topic vocabularies, offices, GSBPM map and designations.
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
| `frac_competencies.json` | The 40 catalogue FRAC competencies with L1–L5 descriptors (`children`), `decayClass`, `gsbpm` | `GET /api/frac/competencies` |
| `course_catalog.json` | The one course catalogue (514 courses) | `POST /api/composite/v1/search`, `GET /api/content/read`, `GET /api/courses/enriched`, `GET /api/external/igot/catalog` |
| `userdata.json` | 151 officials: identity, `jobProfile` (`roleId`, `officeId`, `tier`), role competencies with self-reports | `GET /api/user/v2/read/{id}`, `GET /api/admin/v1/users` |
| `roles.json` | 76 role profiles (office × designation) and their required levels | (read at startup) |
| `enrollments.json` | 1,019 enrolments. Status 2 ⇔ 100%, with `completedDate` | `GET /api/course/v1/user/enrollment/list/{id}` |
| `content_states.json` | Leaf-level progress for **in-progress** enrolments only. Completed ones are derived at request time | `POST /api/course/v1/content/state/read` |
| `frac_crosswalk.json` | iGOT dictionary CID id → catalogue FRAC id, keyword rules, `confirmed: false` for all | `GET /api/frac/v1/crosswalk` |
| `gsbpm_map.json` | GSBPM v5.1 phases and sub-processes (+ `OA.*` overarching), FRAC competency → sub-processes | `GET /api/gsbpm/v1/map` |
| `offices.json` | 12 offices: sub-processes run in `FY2026-27-Q2` with officer-hours each, headcount, products | `GET /api/org/v1/offices[/{id}]` |
| `acbp.json` | Annual Capacity Building Plan FY2026-27: org-wide + per-role APAR-linked mandatory courses, learning hours per quarter per official | `GET /api/cbplan/v1/user/{id}` |
| `prerequisites.json` | 18 expert-seeded prerequisite edges (competency@level → competency@level), acyclic | `GET /api/frac/v1/prerequisites` |
| `course_outcomes.json` | Platform-wide, anonymised pre/post θ course assessments + non-taker comparison episodes (one record per line) | `GET /api/course/v1/assessment/outcomes` |
| `workplace_evidence.json` | EvidenceLog-style rows: SUPERVISOR_RATING (lenient + halo), UTILITY (will-use + confirmation), WORK_SAMPLE (auto-graded, 10 competencies), PEER_RATING (never scored) | `GET /api/evidence/v1/user/{id}` |
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

### Roles and officials (A1)

- **Offices:** 12 offices (NAD, PSD, ESD, ISW-ASI, SSD, SDRD, two FOD zones,
  DPD, CAPD, DQAD, NSSTA). An official's office comes from their old
  department string where one maps.
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

- **Courses per cell:** 2 / 3 / 4 courses per competency × level, with
  probability .5 / .4 / .1.
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
  roster).
- `officerHours = headcount × HOURS_PER_OFFICER_QUARTER (480) × weight share ×
  U(0.85, 1.15)`, rounded to 10 h. Field offices (FOD) dominate the 4.x Collect
  phase, so the 80% rule scopes in collection, validation and aggregation first.
- The GSBPM version is **v5.1** (2019). "5.2" was requested, but its
  sub-process list could not be confirmed.

### ACBP: mandatory courses + learning hours (B3)

- **Organisation-wide mandatory course:** the shortest non-classroom L1 course
  on `comp_data_privacy_026` (information security awareness).
- **Role mandatory course:**
  - Junior and mid tiers: the shortest non-classroom L2 course on the office's
    lead subject.
  - Senior and apex tiers: the shortest non-classroom L3 course on the role's
    first behavioural competency.
  - Seven roles have no such course, so only the org-wide course applies to them.
- **`aparLinked: true`** on all mandatory courses.
- **`learningHoursPerQuarter`:** drawn from `LEARNING_HOURS_BY_TIER`
  (junior 16–30, mid 14–30, senior 14–24, apex 14–20). Field-office (FOD)
  staff get 4 h less, with a minimum of 14. Every official therefore has
  ≥ 56 h a year, above the Mission Karmayogi ≥ 50 h/year guidance
  (`KARMAYOGI_MIN_HOURS_PER_YEAR`, quoted in the file's `_meta`).

### Prerequisites + course outcomes (B4 / B5)

**Prerequisites**
- `mockdata/domain.py::EXPERT_PREREQUISITES` holds 18 hand-written edges, each
  with a rationale. `generate_mock_data.find_cycle` checks them together with
  the implicit ladder edges `c@L-1 → c@L`, and generation fails on a cycle.

**Course outcomes** (`course_outcomes.json`) — every effect is **planted**. The
ground truth is in `_truth/planted_effects.json`.

- **Learners:**
  - Every completed roster enrolment gets one record (`learnerId` = `usr_…`).
  - Anonymised iGOT learners (`lrn_…`) are added per course:
    `clip(round(enrollment_count / TAKERS_PER_ENROLMENTS (250)), 2, 30)`.
  - Courses in a planted-precedence group get at least `PLANTED_GROUP_TAKERS =
    18` takers, so the effect is testable.
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
- **Comparison episodes:** `CONTROLS_PER_COMPETENCY = 60` non-takers per
  competency, with pre ~ U(0.1, 4.9) (spread over all ability levels, so every
  course level has comparable non-takers) and a 30–120-day interval.

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
  holds 10 competencies × L2–L4.
  - `WORK_SAMPLE_ATTEMPT_P = 0.5` of eligible officials attempted one at their
    level or the next.
  - score = 100·logistic(2.2·(θ − L)) + N(0, 8); pass at `WORK_SAMPLE_PASS = 70`.
- **Peer ratings (`PEER_RATING`):** on `PEER_RATING_P = 0.15` of role
  competencies, inflated. Shown for context; the backend never scores them.

## Deliberate holes and planted cases

| What | Where | Why |
|---|---|---|
| No L5 course | `comp_gdp_nowcast_011`, `comp_rtt_022`, `comp_cloud_infra_027`, `comp_citizen_039` | Top-of-ladder hole → `partial` / `no_content` paths, coverage-gap detector |
| No L3 course | `comp_spatial_stat_012`, `comp_procurement_021` | Mid-ladder hole → `stretch` step via L4 |
| Out-of-order learners (`N_OUT_OF_ORDER = 5`) | `usr_200142973`, `usr_986342308`, `usr_298435923`, `usr_107156607`, `usr_158531054` | Completed an L4 course while truly at L2 → tests the monotone level floor |
| Profile incomplete | `usr_154849742`, `usr_290725138`, `usr_322272362` | `UNASSESSED` competencies exist |
| Over-claimers (14) | listed in `_truth/planted_effects.json` | Self-report above evidence → LOW + diagnostic |
| Popular, highly rated, ~zero true uplift (`N_POPULAR_ZERO_UPLIFT = 4`) | `do_11323476390042336611`, `do_11328885625274834952`, `do_11363751793697672490`, `do_11379911329280409962` | B5: the measured-uplift estimator should flag them; ratings alone would not |

Thirty-four of the 40 competencies have courses at every level L1–L5.
