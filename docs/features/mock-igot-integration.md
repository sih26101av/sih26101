# Mock iGOT Karmayogi Integration (Adapter + mock server + mock data)

Simulates the external iGOT Karmayogi / Sunbird platform as a separate process, so
the backend integrates over HTTP exactly as it would against production. All the
data it serves is **synthetic**: one deterministic generator writes it (see
`mock-igot-server/data/README.md`).

The **course catalogue** is the one part that no longer has to be simulated —
iGOT serves its content APIs publicly, so it can be read from the real portal.
See [Live iGOT](#live-igot-the-real-portal) for what is open, what still needs a
platform key, and how to switch.

## Code

**Adapter (backend side)** — `main-lms-backend/adapters/igot_adapter.py`
- `ILearningPlatformAdapter` (ABC): `fetch_catalog`, `fetch_user_history`,
  `fetch_user_roster`, `fetch_user_by_id`, `fetch_user_enrollments`.
- `MockIgotAdapter`:
  - httpx calls to `IGOT_MOCK_BASE_URL` (default `http://localhost:8001`), header
    `x-authenticated-user-token: IGOT_MOCK_TOKEN` (default `mock-api-key-2026`).
  - Unwraps the Sunbird envelope via `_sunbird_result(data, *keys)`.
  - `fetch_catalog()` → `search_catalog(filters)` pages through
    `POST /api/composite/v1/search` (`_SEARCH_PAGE = 500`) and returns every
    course.
  - `fetch_frac_competencies()` and `fetch_frac_crosswalk()` load the FRAC set and
    the crosswalk.
  - `fetch_user_by_id` returns `None` on 404; `fetch_user_enrollments` returns
    `[]` on 404.
  - Per-user reads (`fetch_user_by_id`, `fetch_user_enrollments`,
    `fetch_user_evidence`, `fetch_user_cbplan`) use a pooled keep-alive
    `httpx.AsyncClient` (one per event loop, `_client()`) and a TTL memo
    (`_cached`, `IGOT_USER_CACHE_SECONDS`, default 30) that also merges concurrent
    duplicate calls; errors are not cached. `invalidate_user(id)` drops one user.
    Results are shared objects — callers must not mutate them. Catalogue /
    reference reads still open a client per call (startup only).
- Helpers `_prof_detail` and `_competencies` read `profileDetails.*`.
- Instantiated as a module-level singleton in `main.py`, `routers/karma.py` and
  `routers/competency.py`.

**Mock server** — `mock-igot-server/mock_igot_server.py` (v4, the one to run)
- **Startup:** `lifespan` loads from `data/`: `course_catalog.json` (**the one
  catalogue**), `frac_competencies.json`, `frac_crosswalk.json`, `roles.json`,
  `userdata.json`, `enrollments.json` and `content_states.json`. From the folder
  root it loads `competencies.json` (the iGOT CID dictionary) and
  `jobprofiles.json`. It builds `_COURSE_INDEX` and `_USER_INDEX`.
  `courses.json` / `courses_1.json` are **no longer loaded**.
- **Envelope and auth:** factories `sunbird_ok` / `sunbird_err`; `_require_auth`
  rejects a missing token.
- **Helpers:** `_user_by_id`, `_course_by_id`, `_user_enrolments`,
  `_course_tags`, `_matches_filters`.
- **Catalogue endpoints** (all serve the same catalogue):
  - `POST /api/composite/v1/search` — Sunbird composite search:
    `{"request": {"filters", "limit" ≤ 1000, "offset", "fields"}}`. Filters take
    any course field, plus `competencies_v3.id`.
  - `GET /api/content/read` — paginated, or `?identifier=` for one course.
  - `GET /api/courses/enriched` — the same courses in the older "enriched" shape.
  - `GET /api/external/igot/catalog` (legacy).
- **FRAC endpoints:**
  - `GET /api/frac/competencies` — the 205 catalogue competencies. Each item has
    the admin shape (`competency_id, name, category, description`) plus the full
    FRAC record (`id, competencyType, children, decayClass, gsbpm`).
    `?dictionary=igot` returns the 331-entry CID dictionary instead.
  - `GET /api/frac/v1/crosswalk` — CID → catalogue id, all `confirmed: false`.
- **SCIL v6 reference endpoints** (`REFERENCE_FILES` → `DB_REF`, 404
  `ERR_DATA_NOT_LOADED` when a file is missing; see
  [workforce-insights.md](workforce-insights.md)):
  - `GET /api/gsbpm/v1/map`
  - `GET /api/org/v1/offices`
  - `GET /api/org/v1/offices/{officeId}`
  - `GET /api/frac/v1/prerequisites` — expert prerequisite edges
    (`fetch_prerequisites()`).
  - `GET /api/course/v1/assessment/outcomes?competencyId=&courseId=` — course
    pre/post θ assessments + non-taker comparison episodes
    (`fetch_course_outcomes()`).
  - `GET /api/hrms/v1/officials` — HRMS-style service records + product
    assignment + product → critical competencies (`fetch_hrms()`, loaded at
    startup into `ReferenceData.hrms`).
  - `GET /api/evidence/v1/user/{userId}` — workplace evidence rows
    (supervisor / utility / work sample / peer), EvidenceLog-shaped
    (`fetch_user_evidence()`, merged into the baseline per request).
  - `GET /api/cbplan/v1/user/{userId}` — one official's ACBP: the
    organisation-wide + role mandatory (APAR-linked) courses,
    `learningHoursPerQuarter`, `cycle`. Adapter: `fetch_user_cbplan()` (None on
    404), read per request by `/pathway` and `/recommendations` (mandatory
    courses are always recommended).
  - `GET /api/org/v1/roles` — role competency profiles per office and tier
    (`roles.json`); `fetch_roles()` → `ReferenceData.roles`, the career ladder
    for `/career-readiness`.
  - `GET /api/evidence/v1/supervisor-ratings` — every APAR rating
    `{raterId, compId, grantedValue, cycle}` (ratee ids dropped);
    `fetch_supervisor_ratings()` → `ReferenceData.rater_offsets` (per-rater
    leniency correction).
  - The adapter reads them with `_get_result(path)`, `fetch_gsbpm_map()` and
    `fetch_offices()`.
- **Users and enrolments:**
  - `GET /api/user/v2/read/{user_id}`
  - `GET /api/course/v1/user/enrollment/list/{user_id}`
  - `POST /api/course/v1/content/state/read` — completed enrolments have no
    stored snapshot; their all-done leaf list is derived at request time.
  - `GET /api/admin/v1/users` — also returns `grade` (job-profile tier),
    `officeId` / `officeName`, `roleId`, `completedCourseIds`, `completions`
    (`[{courseId, completedDate}]`, first completion per course) and `mandatory`
    (`{cycle, total, courseIds, completed, pending[]}` from `data/acbp.json` against
    completed enrolments; `null` if the official has no ACBP entry) for the
    admin console.
- **Other:** `POST /v1/telemetry`, `GET /api/job-profiles`, `GET /health`.
- **Legacy endpoints** kept for older callers: `/api/external/igot/*` and
  `POST /competencies/update` (the RAG grading sync target).
- **Runtime stores (in memory):** `TELEMETRY_STORE`, `SEEN_MIDS`,
  `SCORE_PUSH_LOG`, `ENROLL_MUTATIONS`.

**Mock data generator** — `mock-igot-server/generate_mock_data.py`
- One seeded, deterministic generator (`SEED = 20260918`,
  `REF_DATE = 2026-09-15`, one RNG stream per section). `--check` diffs against
  disk.
- **Inputs:**
  - `mockdata/domain.py` — hand-written competencies, topics, offices, GSBPM map,
    overlaps and ladder holes. Its last section merges in the dictionary
    extension and adds the office pools, holes, crosswalk rules and prerequisite
    edges the new families need.
  - `mockdata/domain_extra.py` — competencies 041-205 in six families, each with
    its own short name, description, topics, GSBPM sub-processes, overlaps and
    catalogue depth (`core` / `standard` / `thin`, which sets how many courses,
    items and comparison episodes it gets).
  - `mockdata/roster_seed.json` — frozen identities.
  - `competencies.json` — for the crosswalk.
- **Builders:** `build_frac`, `build_catalog`, `build_crosswalk`,
  `build_officials` (roles + latent true levels + self-reports) and
  `build_enrollments` (history + content states + profile `status`).
- **Output:** `data/MANIFEST.json` labels every file `synthetic: true` with a
  sha256. `data/_truth/planted_effects.json` is ground truth for tests only (never
  served).
- `seed_data.py` is a shim that calls the generator.

**Backend warm-up** (`main.py::_warm_up`, background thread after the port binds) loads catalogue + FRAC + crosswalk
through the adapter. The catalogue goes through `services/catalogue_source.py`,
which serves it from the mock server or the real portal depending on
`IGOT_CATALOGUE_SOURCE` (see [Live iGOT](#live-igot-the-real-portal)); the FRAC
set and its crosswalk always come from the mock. If the mock server is down, it
logs a warning and `HybridRecommendationEngine` reads the same generated files
from disk (`catalog_source` = `"adapter"` or `"disk"`). `_refresh_catalogue_loop`
re-reads the same source every `CATALOGUE_REFRESH_SECONDS`.

**Backend proxies** (`main-lms-backend/main.py`, admin-only):
`GET /api/v1/admin/users` and `GET /api/v1/admin/frac/competencies` forward to
the mock server.

## In / out

- **Out of the mock server:** Sunbird envelopes
  `{id, ver, ts, params, responseCode, result}`.
- **Into the backend:** plain dicts.
  - User profiles: `profileDetails.professionalDetails[0]` (designation,
    department = office division, location), `competencies[]`
    (`id, name, type, requiredLevel, isRoleRequired, competencyLevel?, status`;
    top-level and `profileDetails` copies are identical), `careerHistory`,
    `education`, and `jobProfile` (`title, tier, roleId, officeId`).
  - Enrolments: `courseId`, `courseName`, `status` 0/1/2 (2 ⇔ 100%),
    `completionPercentage`, `leafNodesCount`, `enrolledDate`, `completedDate`
    (status 2 only), `issuedCertificates` and `channel`.
- **Courses:**
  - `identifier`, `name`, `description`
  - `duration` (**seconds**, string), `leafNodesCount`
  - `competencies_v3` (JSON string: `id, name, competencyType,
    competencyLevel "Level N", primary`)
  - `format`, `modality`, `level`, `is_tpac`, `creator`, `channel`
  - `rating`, `rating_count`, `enrollment_count`, `completion_rate` — each
    optional; about 10% of each is missing.

## Live iGOT (the real portal)

The mock exists so the backend integrates over HTTP exactly as it would against
production. For the **course catalogue** that is no longer a simulation: the real
platform serves its content APIs openly, so the catalogue can come from
`https://portal.igotkarmayogi.gov.in` today, with no credentials.

**What is open and what is not** (verified 2026-09-23):

| Endpoint | | |
|---|---|---|
| `POST /api/content/v1/search` | **200** | 5,166 Live courses, `competencies_v6` inline |
| `GET /api/content/v1/read/{id}` | **200** | the full ~94-field record |
| `GET /api/course/v1/hierarchy/{id}` | **200** | module / leaf tree |
| `GET /api/framework/v1/read/kcmfinal_fw` | **200** | the KCM: 3 areas, 146 themes, 601 sub-themes |
| `GET /api/channel/v1/read/{id}` | **200** | provider org |
| `POST /api/composite/v1/search` | **401** | Kong — the endpoint `MockIgotAdapter` imitates |
| `GET /api/user/v2/read/{id}` | **401** | personal data |
| `GET /api/course/v1/user/enrollment/list/{id}` | **401** | personal data |
| `POST /api/user/v1/search` | **401** | personal data |

The boundary is content vs. person. Everything behind the 401 needs a Kong
consumer key issued by **Karmayogi Bharat** (the Section-8 SPV under DoPT that
operates iGOT). There is no self-serve developer portal — integrations such as
eHRMS 2.0 and the state onboardings went through formal MoUs, so the route is
MoSPI DIID → Karmayogi Bharat. Until such a key exists, users, enrolments, ACBP,
evidence and the FRAC dictionary all keep coming from the mock server.

**Code**

- `main-lms-backend/adapters/live_igot_adapter.py` — `LiveIgotAdapter`,
  read-only over the public content APIs. `fetch_catalog()` pages
  `/api/content/v1/search` and normalises each record; `fetch_course()`,
  `fetch_course_hierarchy()` and `fetch_kcm_framework()` read the rest. The
  pager halves its page size on a read timeout (a big page is slow to assemble,
  not broken). Every per-user method raises `NotImplementedError` rather than
  returning an empty list, so a wiring mistake cannot look like "this official
  has no enrolments".
- `main-lms-backend/services/catalogue_source.py` — picks the catalogue from
  `IGOT_CATALOGUE_SOURCE` (`mock` default, or `live`). In `live` mode it tries
  the portal, then the last harvest on disk, then the mock; `describe()` reports
  what actually resolved (`live-api` / `live-disk` / `mock`) and the startup log
  prints it, so nothing ever implies data is live when it is not.
- `main-lms-backend/services/kcm_crosswalk.py` — the KCM → FRAC bridge (below).
- `main-lms-backend/scripts/fetch_live_catalog.py` — harvests catalogue + KCM +
  crosswalk into `main-lms-backend/data/live/` (gitignored). Run it on a
  schedule; the files are the offline fallback.

**Two fields that do not exist upstream.** `enrollment_count` and
`completion_rate` are mock inventions — they are learner-behaviour aggregates
and sit behind the 401. Live courses carry neither, and `normalise_course()`
omits them rather than inventing a value. The ranker already copes: a course
missing a quality field takes the catalogue mean (`_build_quality_norms`), not
the zero it never earned. `is_tpac` is likewise absent, so live courses fall
through to the `NSSTA_CREATORS` name heuristic.

**Competency tags: v3 is effectively dead.** The mock tags courses with
`competencies_v3` (CID ids, a JSON *string*). Production has moved to
`competencies_v6` — the Karmayogi Competency Model — on **5,163 of 5,166** live
courses, returned inline by search. `competencies_v3` survived on only 1 of 25
sampled full reads. `_parse_catalog` therefore reads v6, but only when v3 gave
nothing, so mock data behaves exactly as before.

**The crosswalk, and why most of the KCM maps to nothing.** v6 tags reference
KCM theme refIds (`COMTHEME-000225`); gaps, roles and ACBP all speak the
catalogue FRAC id space. `kcm_crosswalk.build_crosswalk()` embeds both sides
with the shared model and keeps each theme's nearest FRAC competency above a
threshold; `apply_crosswalk()` stamps the winner onto the tag as `fracId`.

The threshold is `max(p99 of FRAC self-similarity, 0.55)`, and the floor is the
part that matters. Measured against the live KCM:

| threshold | themes mapped | weakest survivor |
|---|---|---|
| 0.294 (p80) | 145 / 146 | "Escalator and Travelator Maintenance" → "Establishment, Service Rules & Cadre Management" |
| 0.50 | 68 | "Gender-sensitive Disaggregation" → "Disaster Preparedness" |
| **0.55** | **31** | "Data Protection" → "Data Privacy, Security & IT Act Compliance" |
| 0.70 | 4 | "Project Management" → "Project Management in Government Context" |

The KCM describes the whole civil service; this FRAC set is written for official
statistics. Roughly 30 themes have a real counterpart, and **828 of 5,166** live
courses end up reachable by a competency gap. That is the honest number — a
lower threshold does not find more courses, it invents mappings. Every rule is
written `confirmed: false`, matching `data/frac_crosswalk.json`: these are
machine proposals for the confirmation queue SCIL v6 asks for.

**Linking out to the portal.** In `live` mode a course can be opened on iGOT
itself: `https://portal.igotkarmayogi.gov.in/app/toc/<identifier>/overview`.
The backend puts that on `courseUrl` for recommendations
(`/api/v1/learner/{id}/recommendations`) and enrolments
(`/api/v1/learner/{id}/enrollments`); `CourseCard` and `MyCoursesView` render a
real `<a target="_blank">` when it is present and keep the old inert button when
it is not.

`courseUrl` is set by `catalogue_source.live_course_url()`, which requires the
id to be **in the live catalogue** — not merely to look like one. This matters:
the mock generator mints ids in iGOT's own `do_<digits>` shape, and **none of
the 1,785 mock courses is a real one** (measured overlap with the live 5,166 is
exactly zero). A pattern match would therefore put a 404 behind every synthetic
enrolment. Measured on a seeded learner in `live` mode: 15 of 17 recommendations
carry a working link (all 15 verified 200), the other two being ACBP mandatory
courses that come from the mock plan, and 0 of 6 enrolments carry one.

That asymmetry is the honest state of `live` mode — the catalogue is real, the
learner's history is not. Making "My Courses" link out too means regenerating
`mock-igot-server/data/enrollments.json` against live course ids, which is a
data-generation task (`generate_mock_data.py`), not an adapter one.

**Running it**

```bash
cd main-lms-backend
python -m scripts.fetch_live_catalog      # ~5.2k courses + KCM + crosswalk
# then set IGOT_CATALOGUE_SOURCE=live in .env and restart the backend
```

The first engine build over the live catalogue embeds 5,166 unseen descriptions
and takes ~10 min; after that `services/catalogue_store.py` reuses the vectors
from Neon and the disk cache, so restarts are fast.

## Connections

- Every learner endpoint, the baseline assembler, karma seeding and
  `auth/seed.py` depend on this server being up. Skill-gap and recommendation
  endpoints return a `503` with the exact start command when it is unreachable.
- The recommendation engine falls back to disk at startup.
- After regenerating `data/`, restart (or touch) the mock server, then the backend.

## TODOs / edge cases

- The interface is a single fat port. The mermaid's `ICatalogSync` /
  `IScorePublisher` split and the score-push method are not implemented (see
  `ARCHITECTURE.md` §7).
- Mock CORS is `allow_origins=["*"]`, and any non-empty token passes
  `_require_auth`.
- All writes to the mock server (`enroll`, `score`, `/competencies/update`) are
  in memory and lost on restart.
- Two mock servers live in the folder. Run `mock_igot_server.py`, not `main.py`
  (the legacy one still reads `courses.json`).
- `courses.json` / `courses_1.json` (about 50 MB of real iGOT exports) stay on
  disk for reference but are unused — they are an old dump of the same
  `/api/content/v1/search` that `scripts/fetch_live_catalog.py` now reads live.
  Delete them with `git rm` if they are not needed.
- Every crosswalk rule is unconfirmed — both `data/frac_crosswalk.json` and the
  generated `data/live/live_kcm_crosswalk.json`. SCIL v6 wants a human
  confirmation queue; the KCM rules carry a `similarity` to triage by.
- In `live` mode the ranker's quality composite runs on ratings alone, because
  iGOT publishes no enrolment or completion aggregates. Worth saying out loud
  wherever the UI explains why a course was recommended.
- Only ~828 of the 5,166 live courses map onto a FRAC competency, so `live` mode
  ranks over a much thinner effective pool than the mock. That is the real
  overlap between the KCM and official statistics, not a bug to tune away.
