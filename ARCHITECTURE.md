# Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)

AI-driven LMS layer over iGOT Karmayogi: computes evidence-based competency
baselines for government statistical officials, derives skill gaps against FRAC
role requirements, recommends courses, generates quizzes from training documents,
and answers questions through a bilingual assistant.

> This file describes the **actual code**. Section 7 lists where the code
> diverges from `mospi-competency-platform.mermaid` (the intended design).

---

## 1. Runtime topology

Three processes, started independently:

| # | Service | Path | Port | Role |
|---|---------|------|------|------|
| 1 | Mock iGOT Karmayogi API | `mock-igot-server/mock_igot_server.py` | 8001 | Sunbird-shaped external system of record (users, enrollments, catalog, FRAC dictionary) |
| 2 | LMS backend (orchestrator) | `main-lms-backend/main.py` | 8000 | Owns auth/RBAC + all AI engines; the only service the browser is meant to talk to |
| 3 | React frontend | `frontend/` (Vite) | 5173 | Learner + Admin dashboards, chat widgets, quiz UI |

```
Browser ──JWT──► :8000 LMS backend ──x-authenticated-user-token──► :8001 Mock iGOT
   │                  │
   │                  ├─ FAISS + BM25 (in-process, built at startup)
   │                  ├─ ONNX INT8 multilingual embedder (singleton)
   │                  ├─ Neon Postgres via DATABASE_URL (auth, evidence, quiz attempts, karma; SQLite auth.db fallback)
   │                  └─ Google Gemini (cloud, quiz generation + Hindi translation)
   └─ /api/* proxied to :8000 by Vite dev server (chat only; most calls are absolute URLs)
```

**Startup is non-blocking.** `main._startup` returns immediately so uvicorn
binds the port (~3 s, just imports). Two background jobs follow:
`_create_schema` (auth DB `create_all` → `app_state.db_ready`) and `_warm_up`
on its own thread + event loop (ONNX embedders, intent prototypes, catalogue,
`ReferenceData`, recommendation engine, assembler, uplift → `app_state.ready`,
then the workforce snapshot). `_readiness_gate` middleware holds each request
only for what it needs: every route waits for the schema; routes that read the
engine / reference data / chat embedder also wait for warm-up. Auth, karma and
RAG don't. `GET /health` never waits and reports both states. Heavy libraries
(LangChain, Gemini, PDF/PPTX parsers) are imported inside the functions that use
them, and corpus embeddings are memoised on disk (`ai/embedder.encode_cached`).

During warm-up the backend loads the course catalogue, FRAC set and crosswalk from
port 8001 through `MockIgotAdapter` (`POST /api/composite/v1/search`), falling
back to the same generated files in `mock-igot-server/data/` with a logged
warning when the mock is down. Everything user-specific is fetched over HTTP per
request. All mock data is synthetic and comes from one deterministic generator,
`mock-igot-server/generate_mock_data.py`.

---

## 2. Folder map

### `main-lms-backend/` — FastAPI orchestrator
| Path | Responsibility |
|------|----------------|
| `main.py` | App bootstrap, CORS, router registration, startup singletons (`_rec_engine`, `_assembler`), learner endpoints (profile, skill-gaps, enrollments, recommendations, pathway, achievements), admin proxies |
| `auth/` | JWT access tokens + httpOnly refresh cookie, bcrypt hashing, `users_auth` table, RBAC dependencies, `seed.py` (one-shot user seeding from the mock server) |
| `adapters/` | `ILearningPlatformAdapter` port + `MockIgotAdapter` HTTP adapter to port 8001 |
| `services/` | `competency_service.py` (6-term baseline formula), `baseline_assembler.py` (evidence gathering), `recommendation_service.py` (3-stage hybrid engine), `karma_engine.py` (Strategy-based points), `document_extractor.py` (certificate → FRAC: Gemini, else OCR + e5), `media_quiz/` (probe → route → evidence timeline → cited MCQs) |
| `ai/` | `embedder.py` (shared ONNX/sentence-transformers singleton), `semantic_engine.py` (chatbot intent classifier), `rag_engine.py` + `vector_store.py` + `seed_knowledge.py` (Ollama/ChromaDB — **disconnected**, Tier 3) |
| `routers/` | `chatbot.py` (Gyan), `rag.py` (document→quiz + grading), `media_quiz.py` (video/audio/YouTube→quiz, mounted at `/api/v1/rag/media`), `learning_mode.py` (NotebookLM-style study chat over an uploaded document, mounted at `/api/v1/rag/learning`), `competency.py` (certificate upload + admin verification, baseline calc), `career.py` (next-role career readiness, level disputes), `recommendation_feedback.py` (clicks / enrolments / thumbs), `diagnostic.py` (adaptive level check), `karma.py`, `ai_tools.py` (Ollama/Chroma health + knowledge upload), `insights.py` (SCIL v6 admin views), `admin_console.py` (admin KPIs / roster pages / trends / assignments / nudges / emerging skills / system health / CSV exports) |
| `models/` | `models.py` (SQLAlchemy domain + evidence/quiz/karma tables), `domain.py` (Pydantic response schemas) |
| `scripts/` | `download_model.py` (build step: ONNX exports → `ai/.cache/onnx/`, pre-warms `ai/.cache/emb/`), `quantize_model.py` (legacy `model_int8.onnx`), `eval_intents.py` |

### `mock-igot-server/` — external-system simulator
`mock_igot_server.py` (v4, Sunbird envelopes, in-memory stores loaded in `lifespan`)
is the server actually used. `main.py` is an older simple mock kept alongside.
`generate_mock_data.py` (+ `mockdata/`) is the one seeded generator for everything
in `data/` (see `data/README.md`). Root `competencies.json` (iGOT CID dictionary)
and `jobprofiles.json` are still served; `courses.json` / `courses_1.json` are
unused reference exports.

### `frontend/src/`
| Path | Responsibility |
|------|----------------|
| `App.tsx` | Routes + guards (`/`, `/login`, `/change-password`, `/dashboard/:officialId`, `/admin`, `/trainer`, `/assessment`) |
| `context/AuthContext.tsx` | Token state, silent refresh on mount, role mapping (`learner` → `official`) |
| `services/` | `api.ts` (`lmsFetch` with JWT + 401-retry interceptor), `authApi.ts`, `chatApi.ts` (with offline client-side reply fallback) |
| `hooks/` | `useLearnerDashboard`, `useAdminData`, `useSkillsData`, `useChatEngine`, `useTheme` |
| `pages/` | `LandingPage`, `LoginPage`, `ChangePasswordPage`, `LearnerDashboard`, `AdminDashboard`, `AssessmentPage` |
| `components/dashboard/` | `SkillGapCard` (+ `LearningPathway`), `CourseCard`, `MyCoursesView`, `ProgressView`, `ProfileHeader`, `RightSidebar` (legacy karma card, unmounted); `components/karma/` (`KarmaRewardsView`, `karmaMeta`), `AssessmentUploadZone`, `ChatWidget` |
| `patterns/DashboardFactory.ts` | Role → dashboard/route resolution |

`node/`, `node-v20.17.0-win-x64/`, `node.zip` are a vendored Node runtime, not app code.

---

## 3. Core data flow

**Skill gaps** (`GET /api/v1/learner/{id}/skill-gaps`) — all three learner
competency endpoints below share `main.py::_learner_competency_state` and are
self-or-admin only (`_ensure_can_view`).
1. `MockIgotAdapter.fetch_user_by_id` + `fetch_user_enrollments` → :8001
2. `EvidenceLog` rows for that iGOT userId → auth DB (Neon)
3. `HybridRecommendationEngine.crosswalk` maps each role competency to the
   catalogue FRAC competency that serves it (exact id, or unconfirmed name match)
4. `BaselineAssembler.compute_for_user` gathers 6 evidence channels (completed
   courses credited at their FRAC tag level) and calls
   `CompetencyCalculator.calculate_baseline` → weighted mean over the channels
   present (weights `0.45·Verified 0.15·Documented 0.20·Tenure 0.10·SelfReport
   0.05·Education 0.05·Seniority`), plus adjacency synergy, recency decay,
   confidence-derived ceilings (verified → 5.0/HIGH, documented → 3.5/MEDIUM,
   else 2.5/LOW, all-zero → UNASSESSED)
5. `baseline_assembler.resolve_level` merges evidence floors with the iGOT
   self-reported level → `{currentLevel, targetLevel, gapScore, confidence, basis,
   evidenceLevel, rawScore, evidence{}, crosswalk}`

**Recommendations** (`GET /api/v1/learner/{id}/recommendations`)
Same resolved levels → `calculate_gaps` (Stage 0 priority `gap·target/5`, UNASSESSED
skipped → `needsDiagnostic`) → `get_recommendations`: FRAC-tag + level filter
`current < courseLevel ≤ target` (Stage 1) → dense + BM25 sparse + RRF fusion +
TPAC boost (Stage 2) → `0.6·relevance + 0.4·quality` (Stage 3), interleaved by
level, concatenated in gap-priority order.

**Learning pathway** (`GET /api/v1/learner/{id}/pathway`)
Same resolved levels → `build_pathway` per competency (one course per FRAC level,
diagnostic / bridge / continue / stretch steps) → `build_study_plan` (greedy
priority-weighted levels per hour across all ladders, optional hours budget) →
`SkillGapCard` "View learning path" + "Suggested study order".

**Document → quiz → evidence** (`POST /api/v1/rag/upload`, `/grade`)
Upload (with `difficulty`, `num_questions` 3–20, `question_types`, `language`
en/hi/bi) → pdfplumber/pypdf/python-pptx/python-docx extraction, with RapidOCR
on scanned PDF pages → LangChain chunking → `services/doc_quiz`: Gemini writes
MCQ / True-False / multi-select / fill-in / numeric questions, each citing a
verbatim quote from its chunk → validator (grounding, numbers, computed answers,
distractor plausibility), e5 dedup, and the media pipeline's fact-check and
term-protected Hindi translation (`services/media_quiz/fact_check.py`, shared) →
in-memory `QUIZ_STORE`. Each item's difficulty is calibrated from first-attempt
response data (`quiz_item_stats`, ability-adjusted p-values), else the LLM's tag.
Grade (JWT required) → link the quiz to one of the learner's role competencies
(via `app_state.competency_state`, FRAC tag → e5 → keywords) → difficulty-aware
practice-ability update (`services/practice_assessment.py`) → `QuizAttempt`
(unique on userId+quizId) + on the first attempt, **pass or fail**, one
`EvidenceLog` `PRACTICE_ASSESSMENT` row = the new ability → the assembler reads
the latest one into the documented channel → re-resolved skill gap returned as
`skillImpact`. A pass also awards karma and POSTs to the mock's `/competencies/update`.
The review explains each wrong answer, cites the source passage, and links a
catalogue course for the missed point (`practice_assessment.courses_for_topics`,
reusing the recommender's catalogue embeddings).

**Media → quiz → evidence** (`POST /api/v1/rag/media/upload`, `/youtube`)
Probe (Silero VAD speech ratio, OCR-detector text density, screen activity) →
route (narrated slides / talking head / silent demo / silent slides / reject) →
ASR / OCR / VLM onto one confidence-scored evidence timeline → multilingual-e5
relevance vs FRAC (also picks the quiz's `competency_id`) → Gemini MCQs that cite
evidence ids → validator + fact-check. Writes into the same `QUIZ_STORE`, so the
document path's `/grade` → `EvidenceLog` flow applies unchanged
(`docs/features/media-quiz-generator.md`).

**SCIL v6 layers** (see `docs/features/workforce-insights.md`). Every input is
synthetic mock data.

- **Startup.** `ReferenceData.load(adapter)` reads the GSBPM map, office
  workload, prerequisites, course outcomes and HRMS (disk fallback per file).
  `uplift_service.estimate_uplift` then gives the engine its measured-uplift
  flags. A background `_build_workforce_snapshot` runs every official through
  `_learner_competency_state` for the population / cohort statistics.
- **Per learner request**, `_learner_competency_state` (memoised ~30 s per user,
  invalidated by `app_state.invalidate_user` on every `EvidenceLog` write; iGOT
  per-user reads are TTL-cached in the adapter) adds:
  - workplace evidence rows (`fetch_user_evidence`), fused as K/A/U/S;
  - `opportunity` from the office's GSBPM sub-processes;
  - `proficiency` (dated decay) and `coldStartPrior` (UNASSESSED).
- **`/pathway`** adds the ACBP (`fetch_user_cbplan`: mandatory courses and
  quarterly budget) and the prerequisite DAG to `build_study_plan`.
- **Admin views** are in `routers/insights.py` under `/api/v1/admin/…`: GSBPM
  scope, prerequisites, training effectiveness, capability risk, foresight
  and the TPAC agenda. They are rendered by `WorkforceInsights.tsx`.
- **Admin console** (`routers/admin_console.py`, `/api/v1/admin/console/…`)
  aggregates the mock roster on the server (KPIs, heatmap, pages, filters by
  department / grade / office), stores a daily trend snapshot, assignments and
  nudges in the auth DB (`admin_daily_snapshots`, `training_assignments`,
  `training_nudges`), reads the workforce snapshot for the emerging-skills
  forecast, and extends `/health` (`services/system_health.py`) with live
  probes. Learners read what admins sent them at
  `GET /api/v1/learner/{id}/training-actions` (no learner UI yet).

**Chat** (`POST /api/v1/chat`) — frontend posts profile context (gaps, recs, role);
backend runs regex intercepts → semantic intent classification → templated reply,
optionally returning `navigate_action(s)` the frontend executes (tab switch,
scroll, theme, language, login modal).

**Chat → Assessment Studio hand-off** — Gyan stays offline (no LLM key), so it
never reads an attached document itself. The learner attaches a file in the
chat widget and picks "Generate a quiz" or "Help me study this"; the frontend
stores the `File` in a module singleton (`services/pendingStudioUpload.ts`) and
sends a `redirect` `navigate_action` to `/assessment`. On mount, the Assessment
Studio consumes that singleton and either auto-runs `/api/v1/rag/upload` (quiz)
or `/api/v1/rag/learning/start` (Learning Mode) — the learner never re-uploads.
See `docs/features/chatbot-gyan.md` and `docs/features/learning-mode.md`.

---

## 4. Persistence

One shared **Neon Postgres** database (`DATABASE_URL` in `main-lms-backend/.env`;
see `docs/features/auth-and-rbac.md`) so every teammate/deployment has the same users.
Falls back to SQLite `main-lms-backend/auth.db` when `DATABASE_URL` is unset. Tables
are auto-created at startup (`create_all`, no migrations):
- `users_auth` — `AuthBase` (auth/models.py)
- Everything else — `Base` (models/models.py): domain tables from the UML,
  plus `evidence_log`, `quiz_attempts`, `quiz_item_stats`, `karma_events`, `karma_monthly_usage`

Identity note: `EvidenceLog.userId` and `QuizAttempt.userId` intentionally store
the **iGOT userId** (`usr_…`), not `users.uuid`. Auth usernames are also iGOT
userIds, so the JWT subject is the canonical identity across the platform.

---

## 5. Tech stack

**Backend** — FastAPI, SQLAlchemy 2, Pydantic v2, httpx, python-jose + bcrypt,
faiss-cpu, rank-bm25, numpy, onnxruntime + tokenizers (no PyTorch in production;
sentence-transformers fallback via `requirements-dev.txt`), google-generativeai, langchain-text-splitters,
pdfplumber/pypdf/python-pptx, chromadb + langchain-ollama (disconnected path).

**Frontend** — React 18, TypeScript, Vite 5, React Router 6, Tailwind, Recharts,
lucide-react. No state library; hooks + context only.

**Models** — `paraphrase-multilingual-MiniLM-L12-v2` (384-dim, ONNX INT8 preferred)
for both chat intents and course search; Gemini (`GEMINI_MODEL`) for MCQs;
Gemini (or RapidOCR + multilingual-e5 offline) for certificate parsing.

**Env vars** (`main-lms-backend/.env`, see `.env.example`): `IGOT_MOCK_BASE_URL`,
`IGOT_MOCK_TOKEN`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `IGOT_COMPETENCIES_UPDATE_URL`,
`OLLAMA_*`, `CHROMA_DB_DIR`, `CHUNK_SIZE`, `CHUNK_OVERLAP`.

---

## 6. Design patterns actually implemented

| Pattern | Where |
|---------|-------|
| Adapter / Port | `adapters/igot_adapter.py` (`ILearningPlatformAdapter` → `MockIgotAdapter`) |
| Strategy | `services/karma_engine.py` (`IKarmaStrategy` + fixed-points default and 4 specialised strategies, rule table `RULES`) |
| Factory | `frontend/src/patterns/DashboardFactory.ts` |
| Singleton | `ai/embedder.py`, startup `_rec_engine` / `_assembler` |
| Layered fallback | Chat Tier 1 semantic → Tier 2 template → (Tier 3 Ollama, disconnected); embedder ONNX → PyTorch; PDF pdfplumber → pypdf; PPTX python-pptx → raw XML |

---

## 7. Mismatches between the mermaid diagram and the code

Called out explicitly — the diagram is the intended design, not a description of
what runs today.

1. **ISP split adapters missing.** The diagram specifies `ICatalogSync` and
   `IScorePublisher` as separate interfaces with `IgotPlatformAdapter`,
   `NsstaPlatformAdapter`, `InMemoryLearningPlatformAdapter`. The code has one
   fat interface `ILearningPlatformAdapter` (5 read methods, no score-push
   method) and one implementation, `MockIgotAdapter`. Score push happens inline
   via `httpx` in `routers/rag.py`.
2. **Observer / EventBus / Transactional Outbox not implemented.** `OutboxEntry`
   exists as a table in `models/models.py` but is never written or read. There is
   no `EventBus`, `IEventListener`, `LocalProfileUpdater`, `AdminAuditLogger`,
   `IGotSyncOutboxPublisher` or `OutboxWorker`. iGOT sync is a synchronous,
   best-effort HTTP call inside the grading request; a failure is swallowed and
   reported as `synced_to_igot: false`. Karma awards on quiz pass / diagnostic
   finish are likewise direct calls (`karma_engine.award_safe`) from the grading
   code, not events.
3. **Recommendation Strategy interface not implemented.** No
   `IRecommendationStrategy` / `VectorSearchStrategy` / `SkillGapRuleStrategy` /
   `HybridRecommendationStrategy` / `RecommendationEngine.setStrategy`. Instead a
   single concrete `HybridRecommendationEngine` hardcodes the dense+sparse+RRF
   pipeline. `IVectorStore` is likewise absent — FAISS is used directly.
4. **Factory/Builder for documents not implemented.** No `IDocumentParser`,
   `PdfParser`, `PptParser`, `TextParser`, `DocumentParserFactory`, or
   `AssessmentBuilder`. `routers/rag.py` dispatches on file extension with
   `if/elif` (DOCX and scanned-PDF OCR live in `services/doc_quiz/extract.py`);
   question building is a pipeline module (`services/doc_quiz/generate.py`),
   not a Builder class.
5. **`SkillGapEngine` / `SkillGapReport` don't exist as named classes.** That role
   is played by `BaselineAssembler` + `CompetencyCalculator` + inline logic in
   `main.py`, which produce a JSON payload rather than a `SkillGapReport` type.
6. **Repository layer absent.** No `IUserCompetencyRepository`,
   `IAssessmentRepository`, `ICourseRepository`. Routers query SQLAlchemy
   sessions directly; the course catalog is a JSON file read at startup, not a
   repository.
7. **Course vectors are persisted, but only as a cache.** `services/catalogue_store.py`
   writes `Course.syllabusVectorEmbedding` (base64 float32) and
   `embeddingModelVersion` (`<model>|<text hash>`), and reuses them when the
   engine is built. The catalogue itself still comes from the mock server,
   re-checked every `CATALOGUE_REFRESH_SECONDS`. `CourseSkillMapping` stays
   unused (tags are read from the catalogue).
8. **The UML domain tables are largely dormant.** `Official`, `JobRole`,
   `RoleRequirement`, `UserCompetency`, `CourseSkillMapping`,
   `AssessmentSkillMapping` are created but barely written. Live user, role and
   competency data comes from the mock iGOT server, not from these tables. Only
   the RAG grading path writes `CompetencyProfile`/`UserCompetency`, and it
   overloads `CompetencyProfile.profileId` to hold an iGOT userId.
9. **The evidence model is richer than the diagram.** `EvidenceLog`,
   `QuizAttempt`, `QuizItemStat` (per-item response data for difficulty
   calibration), `CertificateSubmission` (admin documented → verified review),
   `KarmaEvent`, `KarmaMonthlyUsage` and the whole 6-term baseline
   formula have no counterpart in the mermaid file; the diagram's
   `UserCompetency.verificationSource` is the only nod to evidence provenance.
10. **Roles diverge.** The diagram has `BaseUser → Official | Admin | Trainer`.
    Auth seeds only `learner` and `admin` (`auth/seed.py`), and the frontend maps
    `learner → official`. `/trainer` renders the learner dashboard.

Known integration bugs (not diagram-related) are recorded in the relevant
`docs/features/*.md` files.
