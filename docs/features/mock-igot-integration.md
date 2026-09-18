# Mock iGOT Karmayogi Integration (Adapter + mock server + mock data)

Simulates the external iGOT Karmayogi / Sunbird platform as a separate process, so
the backend integrates over HTTP exactly as it would against production. All the
data it serves is **synthetic**: one deterministic generator writes it (see
`mock-igot-server/data/README.md`).

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
  - `GET /api/frac/competencies` — the 40 catalogue competencies. Each item has
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
    404), read per request by `/pathway`.
  - The adapter reads them with `_get_result(path)`, `fetch_gsbpm_map()` and
    `fetch_offices()`.
- **Users and enrolments:**
  - `GET /api/user/v2/read/{user_id}`
  - `GET /api/course/v1/user/enrollment/list/{user_id}`
  - `POST /api/course/v1/content/state/read` — completed enrolments have no
    stored snapshot; their all-done leaf list is derived at request time.
  - `GET /api/admin/v1/users`
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
    overlaps and ladder holes.
  - `mockdata/roster_seed.json` — frozen identities.
  - `competencies.json` — for the crosswalk.
- **Builders:** `build_frac`, `build_catalog`, `build_crosswalk`,
  `build_officials` (roles + latent true levels + self-reports) and
  `build_enrollments` (history + content states + profile `status`).
- **Output:** `data/MANIFEST.json` labels every file `synthetic: true` with a
  sha256. `data/_truth/planted_effects.json` is ground truth for tests only (never
  served).
- `seed_data.py` is a shim that calls the generator.

**Backend startup** (`main.py::_startup`) loads catalogue + FRAC + crosswalk
through the adapter. If the mock server is down, it logs a warning and
`HybridRecommendationEngine` reads the same generated files from disk
(`catalog_source` = `"adapter"` or `"disk"`).

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
  disk for reference but are unused. Delete them with `git rm` if they are not
  needed.
- Every crosswalk rule is unconfirmed. SCIL v6 wants a human confirmation queue.
