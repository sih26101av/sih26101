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
