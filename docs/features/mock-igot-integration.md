# Mock iGOT Karmayogi Integration (Adapter + mock server)

Simulates the external iGOT Karmayogi / Sunbird platform as a separate process, so
the backend integrates over HTTP exactly as it would against production.

## Code

**Adapter (backend side)** — `main-lms-backend/adapters/igot_adapter.py`
- `ILearningPlatformAdapter` (ABC): `fetch_catalog`, `fetch_user_history`,
  `fetch_user_roster`, `fetch_user_by_id`, `fetch_user_enrollments`.
- `MockIgotAdapter` — httpx calls to `http://localhost:8001`, header
  `x-authenticated-user-token: mock-api-key-2026`, unwraps the Sunbird envelope via
  `_sunbird_result(data, *keys)`. `fetch_user_by_id` returns `None` on 404;
  `fetch_user_enrollments` returns `[]` on 404.
- Helpers `_prof_detail`, `_competencies` read `profileDetails.*`.
- Instantiated as a module-level singleton in `main.py`, `routers/karma.py`,
  `routers/competency.py`.

**Mock server** — `mock-igot-server/mock_igot_server.py` (v4, the one to run)
- `lifespan` loads into memory: `courses.json` (filtered to ASCII-titled courses),
  `courses_1.json` (FRAC-enriched), `competencies.json`, `jobprofiles.json`, and from
  `data/`: `userdata.json`, `enrollments.json`, `content_states.json`. Builds
  `_COURSE_INDEX` / `_ENRICHED_INDEX`.
- Envelope factories `sunbird_ok` / `sunbird_err`; `_require_auth` rejects a missing
  token; `_user_by_id`, `_course_by_id`, `_user_enrolments` lookups.
- Sunbird-shaped endpoints: `GET /api/content/read` (paginated, `?identifier=`),
  `GET /api/courses/enriched`, `GET /api/user/v2/read/{user_id}`,
  `GET /api/course/v1/user/enrollment/list/{user_id}`,
  `POST /api/course/v1/content/state/read`, `POST /v1/telemetry` (validates `eid`
  against `VALID_EIDS` and telemetry version), `GET /api/admin/v1/users`,
  `GET /api/frac/competencies`, `GET /api/job-profiles`, `GET /health`.
- Legacy/simple endpoints kept for older callers: `/api/external/igot/*`
  (catalog, frac, job-profiles, user history, score push, enroll) and
  `POST /competencies/update` (the RAG grading sync target).
- Runtime mutable stores: `TELEMETRY_STORE`, `SEEN_MIDS`, `SCORE_PUSH_LOG`,
  `ENROLL_MUTATIONS`.
- Support scripts: `seed_data.py`, `enrich_catalog.py`, `generate_userdata.py` (empty),
  `test_lang.py`. `main.py` in the same folder is an **older, simpler mock** — not used.

**Backend proxies** (`main-lms-backend/main.py`, admin-only):
`GET /api/v1/admin/users` and `GET /api/v1/admin/frac/competencies` forward to the
mock server with the token and unwrap `result`, so the browser never calls :8001
directly for admin data.

## In / out

- Out of the mock server: Sunbird envelopes `{id, ver, ts, params, responseCode, result}`.
- Into the backend: plain dicts — user profiles (`profileDetails.professionalDetails[0]`,
  `profileDetails.competencies[]`, `careerHistory`, `education`, `jobProfile.tier`),
  enrollments (`courseId`, `courseName`, `status` 0/1/2, `completionPercentage`,
  `leafNodesCount`, `enrolledDate`, `issuedCertificates`, `channel`).

## Connections

Every learner endpoint, the baseline assembler, karma seeding and `auth/seed.py`
depend on this server being up. Skill-gap and recommendation endpoints return a
`503` with the exact start command when it is unreachable.

## TODOs / edge cases

- The recommendation engine reads `data/course_catalog.json` **from disk** instead of
  calling the adapter, so the catalog the engine ranks over is not the one the mock
  server serves (`courses.json` / `courses_1.json`). Drift between them is invisible.
- `MockIgotAdapter` hardcodes `base_url` and `token` in `__init__` and ignores
  `IGOT_MOCK_BASE_URL` / `IGOT_MOCK_TOKEN` (only `main.py`'s admin proxies read those).
- The interface is a single fat port; the mermaid's `ICatalogSync` / `IScorePublisher`
  split and the score-push method are not implemented (see `ARCHITECTURE.md` §7).
- Mock CORS is `allow_origins=["*"]`; any non-empty token passes `_require_auth`.
- All writes to the mock server (`enroll`, `score`, `/competencies/update`) are
  in-memory and lost on restart.
- Two mock servers live in the folder; run `mock_igot_server.py`, not `main.py`.
