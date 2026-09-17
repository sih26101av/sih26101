# Graph Report - SIH_IGot  (2026-09-17)

## Corpus Check
- 114 files · ~4,729,475 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .css 1, .example 1)

## Summary
- 1114 nodes · 2231 edges · 72 communities (59 shown, 13 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 275 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dcfb1c87`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- rag.py
- Code
- competency.py
- Code
- package.json
- MockIgotAdapter
- get
- ChatWidget.tsx
- App.tsx
- LearnerDashboard.tsx
- AdminDashboard.tsx
- AuthContext.tsx
- CLAUDE.md
- mock-igot-server/main.py
- karma.py
- mock_igot_server.py
- seed_data.py
- What You Must Do When Invoked
- domain.ts
- _require_auth
- UserAuth
- Code
- chatbot.py
- RightSidebar.tsx
- compilerOptions
- ai_tools.py
- 🇮🇳 MoSPI Skill Intelligence Platform
- recommendation_service.py
- main-lms-backend/main.py
- vector_store.py
- main_backup.py
- DashboardFactory.ts
- seed.py
- get
- get_embedder
- speech.d.ts
- graphify reference: extra exports and benchmark
- rag_engine.py
- os
- compilerOptions
- lifespan
- graphify reference: query, path, explain
- Mock iGOT Karmayogi Integration (Adapter + mock server)
- chat_mode
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- models/models.py
- .claude/CLAUDE.md
- extraction-spec.md
- react
- EvidenceLog
- grade_quiz
- HomeChatWidget.tsx
- api.ts
- chatApi.ts
- enrich_catalog.py
- CourseCard.tsx
- MyCoursesView.tsx
- ProgressView.tsx
- classify_intent

## God Nodes (most connected - your core abstractions)
1. `UserAuth` - 42 edges
2. `react` - 27 edges
3. `Code` - 24 edges
4. `Code` - 22 edges
5. ``frontend/src/`` - 21 edges
6. `MockIgotAdapter` - 20 edges
7. `Code` - 18 edges
8. `useAuth()` - 17 edges
9. `useTheme()` - 17 edges
10. `EvidenceLog` - 17 edges

## Surprising Connections (you probably didn't know these)
- `Code` --references--> `PassbookRow()`  [INFERRED]
  docs/features/karma-points.md → frontend/src/components/dashboard/RightSidebar.tsx
- `Code` --references--> `MonthlyCapBar()`  [INFERRED]
  docs/features/karma-points.md → frontend/src/components/dashboard/RightSidebar.tsx
- `Connections` --references--> `useTheme()`  [INFERRED]
  docs/features/chatbot-gyan.md → frontend/src/hooks/useTheme.tsx
- `7. Mismatches between the mermaid diagram and the code` --references--> `SkillGapReport`  [INFERRED]
  ARCHITECTURE.md → frontend/src/types/domain.ts
- `TODOs / edge cases` --references--> `MockIgotAdapter`  [INFERRED]
  docs/features/recommendation-engine.md → main-lms-backend/adapters/igot_adapter.py

## Import Cycles
- None detected.

## Communities (72 total, 13 thin omitted)

### Community 0 - "rag.py"
Cohesion: 0.10
Nodes (34): asyncio, Code, google_generativeai, io, langchain_text_splitters, _chunk_document_text(), _clean_text(), DocumentMetadata (+26 more)

### Community 1 - "Code"
Cohesion: 0.08
Nodes (34): Code, In / out, Karma Points (gamification), TODOs / edge cases, KarmaEvent, KarmaEventType, KarmaMonthlyUsage, Immutable ledger entry — one row per karma point award event. (+26 more)

### Community 2 - "competency.py"
Cohesion: 0.06
Nodes (36): datetime, Code, Code, CertificateUploadZone(), calculate_baseline(), EvidencePayload, BaseModel, post (+28 more)

### Community 3 - "Code"
Cohesion: 0.08
Nodes (39): bcrypt, Code, TokenBridge(), awardKarmaEvent(), lmsFetch(), registerLogoutCallback(), setApiToken(), jose (+31 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (43): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+35 more)

### Community 5 - "MockIgotAdapter"
Cohesion: 0.07
Nodes (30): 1. Runtime topology, 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator (+22 more)

### Community 6 - "get"
Cohesion: 0.09
Nodes (23): get_achievements(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments(), get_enrollments_by_user_id(), get_profile_by_user_id(), get_recommendations(), get_recommendations_by_user_id() (+15 more)

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.21
Nodes (12): ChatWidgetProps, MessageBubble(), renderMarkdown(), SUGGESTIONS_EN, SUGGESTIONS_HI, PendingNavAction, UseChatEngineOptions, UseChatEngineReturn (+4 more)

### Community 8 - "App.tsx"
Cohesion: 0.16
Nodes (14): App(), AssessmentPage, DashboardRedirect(), ProtectedRoute(), useAuth(), Theme, ThemeContext, ThemeContextType (+6 more)

### Community 9 - "LearnerDashboard.tsx"
Cohesion: 0.11
Nodes (26): `frontend/src/`, Code, LearnerDashboard, ChatWidget(), formatDate(), ProfileHeader(), ProgressView(), CONFIDENCE_CONFIG (+18 more)

### Community 10 - "AdminDashboard.tsx"
Cohesion: 0.14
Nodes (21): Code, AdminDashboard, AdminKPIs, AdminRosterRow, GAP_COLORS, HeatmapEntry, levelToNumber(), useAdminData() (+13 more)

### Community 11 - "AuthContext.tsx"
Cohesion: 0.18
Nodes (16): ProtectedRouteProps, AuthContext, AuthContextType, AuthProvider(), AuthUser, mapRole(), UserRole, changePassword() (+8 more)

### Community 12 - "CLAUDE.md"
Cohesion: 0.06
Nodes (24): CLAUDE.md — index & router, Feature index, graphify, How to use these docs, Run commands, Admin Dashboard, Connections, In / out (+16 more)

### Community 13 - "mock-igot-server/main.py"
Cohesion: 0.11
Nodes (26): contextlib, fastapi_middleware_cors, json, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles() (+18 more)

### Community 14 - "karma.py"
Cohesion: 0.19
Nodes (16): _assert_self_or_admin(), award_karma_event(), CbpClaimRequest, claim_cbp_bonus(), get_karma_ledger(), KarmaEventRequest, BaseModel, get (+8 more)

### Community 15 - "mock_igot_server.py"
Cohesion: 0.12
Nodes (23): fastapi_responses, field_validator, CompetencyOut, ContentStateRequest, CourseOut, EnrolPayload, get_content_state(), ingest_telemetry() (+15 more)

### Community 16 - "seed_data.py"
Cohesion: 0.23
Nodes (17): faker, batch_id(), build_content_states(), build_course_catalog(), build_enrollments(), build_frac_competencies(), build_users(), do_id() (+9 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "domain.ts"
Cohesion: 0.13
Nodes (15): ProfileHeaderProps, BaseUser, Competency, CompetencyProfile, Course, JobRole, KarmaBreakdown, KarmaMonthlyUsage (+7 more)

### Community 19 - "_require_auth"
Cohesion: 0.15
Nodes (24): Code, exception_handler, HTTPException, JSONResponse, _competencies(), Return the competencies list from profileDetails.competencies., _course_by_id(), get_competencies() (+16 more)

### Community 20 - "UserAuth"
Cohesion: 0.11
Nodes (22): AuthBase, get_db(), Yields a database session and ensures it is closed after the request., UserAuth, get_me(), get, Return the current authenticated user's profile. Used by the frontend to re-…, get_achievements_by_user_id() (+14 more)

### Community 21 - "Code"
Cohesion: 0.14
Nodes (16): Code, on_event, Create users_auth table and karma tables if they don't exist yet., _startup(), _CourseDoc, GapEntry, HybridRecommendationEngine, BaseModel (+8 more)

### Community 22 - "chatbot.py"
Cohesion: 0.21
Nodes (22): Code, Maps a list of skill gap dicts (from ChatRequest) into a flat numeric feature…, vectorize_profile(), chat(), ChatHistoryItem, ChatRequest, ChatResponse, detect_intent_keyword() (+14 more)

### Community 23 - "RightSidebar.tsx"
Cohesion: 0.14
Nodes (16): TODOs / edge cases, CareerCard(), EVENT_META, KarmaCard(), milestones, MilestoneStep, MilestoneStepper(), MonthlyCapBar() (+8 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "ai_tools.py"
Cohesion: 0.13
Nodes (18): is_ollama_available(), Fast, synchronous check — just hits the Ollama /api/tags endpoint. Returns True…, add_documents_from_file(), Ingests a PDF file into the vector store. Returns the number of chunks added.…, ai_health_check(), HealthResponse, BaseModel, get (+10 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "recommendation_service.py"
Cohesion: 0.18
Nodes (14): collections, dataclasses, difflib, logging, is_embedder_ready(), FILE: ai/embedder.py…, Non-blocking check — True only if the singleton is already loaded., is_semantic_engine_ready() (+6 more)

### Community 28 - "main-lms-backend/main.py"
Cohesion: 0.21
Nodes (14): _level_to_int(), main.py — MoSPI LMS Backend API (Main Orchestrator)…, Level 3' → 3, 'Level 2' → 2, fallback → 2, Achievement, AchievementsResponse, Enrollment, EnrollmentsResponse, EvidenceBreakdown (+6 more)

### Community 29 - "vector_store.py"
Cohesion: 0.21
Nodes (14): Code, dotenv, FILE: ai/seed_knowledge.py…, Embeds all baseline knowledge into ChromaDB., seed(), add_text_to_store(), _get_embeddings(), get_store() (+6 more)

### Community 30 - "main_backup.py"
Cohesion: 0.12
Nodes (21): fastapi, fastapi_security, get_current_user(), Session, auth/dependencies.py…, Decodes the Bearer JWT, looks up the user in auth.db. Raises HTTP 401 for any…, Returns a FastAPI dependency that checks the current user's role. Example:…, require_role() (+13 more)

### Community 31 - "DashboardFactory.ts"
Cohesion: 0.14
Nodes (7): AdminDashboardCreator, DashboardCreator, DashboardFactory, DashboardProps, IDashboard, OfficialDashboardCreator, TrainerDashboardCreator

### Community 32 - "seed.py"
Cohesion: 0.13
Nodes (18): httpx, auth/database.py…, hash_password(), Return a bcrypt hash of the plain-text password., _derive_password(), _fetch_officials(), main(), Session (+10 more)

### Community 33 - "get"
Cohesion: 0.17
Nodes (13): get_admin_roster(), health(), legacy_catalog(), legacy_frac(), legacy_job_profiles(), legacy_user_history(), get, Merge seed enrolments with any runtime mutations. (+5 more)

### Community 34 - "get_embedder"
Cohesion: 0.19
Nodes (11): Code, Connections, In / out, Shared Multilingual Embedder, TODOs / edge cases, get_embedder(), _OnnxEmbedder, Returns the singleton embedder, loading it on the first call. • Thread-safe for… (+3 more)

### Community 35 - "speech.d.ts"
Cohesion: 0.20
Nodes (6): SpeechRecognition, SpeechRecognitionEvent, SpeechRecognitionResult, SpeechRecognitionResultItem, SpeechRecognitionResultList, Window

### Community 36 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 37 - "rag_engine.py"
Cohesion: 0.18
Nodes (11): Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, build_system_prompt(), generate_chat_response(), FILE: ai/rag_engine.py…, Runs the full RAG pipeline: 1. Retrieve top-k relevant document chunks from… (+3 more)

### Community 38 - "os"
Cohesion: 0.16
Nodes (10): _download_from_hf(), _download_from_url(), main(), scripts/download_model.py…, Download from HuggingFace Hub using huggingface_hub library., Fallback: download via urllib (no extra deps)., scripts/quantize_model.py…, os (+2 more)

### Community 39 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 40 - "lifespan"
Cohesion: 0.33
Nodes (7): lifespan(), _load_json(), _load_json_from_dir(), Any, FastAPI, Load all datasets into memory once at startup. courses.json is large (~27 MB /…, Load a JSON file from ROOT_DIR. Raises RuntimeError on missing file.

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 42 - "Mock iGOT Karmayogi Integration (Adapter + mock server)"
Cohesion: 0.40
Nodes (4): Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server), TODOs / edge cases

### Community 43 - "chat_mode"
Cohesion: 0.67
Nodes (3): chat_mode(), get, Returns which response engine is currently active. Frontend can use this to…

### Community 44 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 45 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 46 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 49 - "models/models.py"
Cohesion: 0.17
Nodes (21): 7. Mismatches between the mermaid diagram and the code, Base, enum, Admin, Assessment, AssessmentSkillMapping, BaseUser, Competency (+13 more)

### Community 61 - "react"
Cohesion: 0.25
Nodes (13): Visual design system (shared by landing, login, change-password, learner dashboard), AssessmentUploadZone(), AssessmentUploadZoneProps, AshokaChakra(), CountUp(), GovEmblem(), Reveal(), useInView() (+5 more)

### Community 62 - "EvidenceLog"
Cohesion: 0.16
Nodes (13): 3. Core data flow, Conventions, Certificate / Resume Evidence Extraction, Connections, In / out, TODOs / edge cases, Connections, In / out (+5 more)

### Community 63 - "grade_quiz"
Cohesion: 0.18
Nodes (9): Authentication & RBAC, Connections, In / out, TODOs / edge cases, _detect_skill_name(), grade_quiz(), post, Infers or extracts the skill/competency topic dynamically from the document's… (+1 more)

### Community 64 - "HomeChatWidget.tsx"
Cohesion: 0.22
Nodes (7): HomeChatWidget(), HomeChatWidgetProps, MessageBubble(), renderMarkdown(), SUGGESTIONS_EN, SUGGESTIONS_HI, useChatEngine()

### Community 65 - "api.ts"
Cohesion: 0.38
Nodes (9): useLearnerDashboard(), fetchAchievements(), fetchEnrollments(), fetchKarmaLedger(), fetchRecommendations(), fetchSkillGapsAndProfile(), levelToNumber(), RawCompetency (+1 more)

### Community 66 - "chatApi.ts"
Cohesion: 0.29
Nodes (10): buildLocalReply(), ChatApiPayload, detectIntent(), detectLanguage(), fmtGaps(), fmtRecs(), HINGLISH_WORDS, INTENT_PATTERNS (+2 more)

### Community 67 - "enrich_catalog.py"
Cohesion: 0.31
Nodes (8): hashlib, enrich_course(), main(), FILE: mock-igot-server/enrich_catalog.py…, Returns a deterministic RNG seeded by the course identifier hash., Add quality fields to a course dict (in-place, idempotent)., _seeded_rng(), Random

### Community 68 - "CourseCard.tsx"
Cohesion: 0.33
Nodes (5): CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps, SOURCE_STYLES

### Community 69 - "MyCoursesView.tsx"
Cohesion: 0.40
Nodes (3): MyCoursesView(), MyCoursesViewProps, Enrollment

### Community 70 - "ProgressView.tsx"
Cohesion: 0.40
Nodes (3): ProgressViewProps, Achievement, recharts

### Community 71 - "classify_intent"
Cohesion: 0.33
Nodes (6): classify_intent(), _correct_tokens(), _ensure_prototypes(), Encode all intent prototype phrases once, via the shared singleton embedder., Classify the user query into one of the intent categories. Steps: 1. Fuzzy-…, Apply difflib fuzzy correction on each token to catch common typos like…

## Knowledge Gaps
- **202 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+197 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 484 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Code` connect `Code` to `seed.py`, `AuthContext.tsx`, `UserAuth`, `grade_quiz`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `UserAuth` connect `UserAuth` to `seed.py`, `rag.py`, `Code`, `get`, `karma.py`, `main-lms-backend/main.py`, `main_backup.py`, `grade_quiz`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `MockIgotAdapter` connect `MockIgotAdapter` to `competency.py`, `Mock iGOT Karmayogi Integration (Adapter + mock server)`, `CLAUDE.md`, `karma.py`, `models/models.py`, `_require_auth`, `main_backup.py`, `main-lms-backend/main.py`, `EvidenceLog`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `Code` (e.g. with `KarmaCard()` and `MonthlyCapBar()`) actually correct?**
  _`Code` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `Code` (e.g. with `AssessmentUploadZone()` and `ChatWidget()`) actually correct?**
  _`Code` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving ``frontend/src/`` (e.g. with `AssessmentUploadZone()` and `ChatWidget()`) actually correct?**
  _``frontend/src/`` has 20 INFERRED edges - model-reasoned connections that need verification._