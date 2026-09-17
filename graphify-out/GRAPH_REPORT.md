# Graph Report - SIH_IGot  (2026-09-18)

## Corpus Check
- 124 files · ~4,777,566 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .css 1, .example 1)

## Summary
- 1165 nodes · 2384 edges · 75 communities (61 shown, 14 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 293 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `be80ff71`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- rag.py
- Code
- Code
- router.py
- package.json
- MockIgotAdapter
- UserAuth
- ChatWidget.tsx
- App.tsx
- Code
- AdminDashboard.tsx
- authApi.ts
- CLAUDE.md
- mock-igot-server/main.py
- _assert_self_or_admin
- mock_igot_server.py
- seed_data.py
- What You Must Do When Invoked
- domain.ts
- LearnerDashboard.tsx
- main-lms-backend/main.py
- Code
- chatbot.py
- RightSidebar.tsx
- compilerOptions
- vector_store.py
- 🇮🇳 MoSPI Skill Intelligence Platform
- recommendation_service.py
- domain.py
- Code
- karma.py
- DashboardFactory.ts
- ai_tools.py
- pydantic
- seed.py
- speech.d.ts
- graphify reference: extra exports and benchmark
- competency.py
- json
- compilerOptions
- Ollama RAG Knowledge Base (Tier 3 — disconnected)
- graphify reference: query, path, explain
- CompetencyCalculator
- `frontend/src/`
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- models/models.py
- .claude/CLAUDE.md
- extraction-spec.md
- lucide-react
- EvidenceLog
- grade_quiz
- ProgressView.tsx
- api.ts
- BaselineAssembler
- useScreenReader.ts
- CLAUDE.md — index & router
- MyCoursesView.tsx
- RAG Document → Quiz Generator & Grading
- Authentication & RBAC
- Learner Dashboard (frontend shell)
- require_role
- _startup

## God Nodes (most connected - your core abstractions)
1. `UserAuth` - 42 edges
2. `react` - 37 edges
3. `Code` - 30 edges
4. `Code` - 24 edges
5. `lucide-react` - 21 edges
6. ``frontend/src/`` - 21 edges
7. `MockIgotAdapter` - 20 edges
8. `Code` - 19 edges
9. `Code` - 18 edges
10. `Code` - 18 edges

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

## Communities (75 total, 14 thin omitted)

### Community 0 - "rag.py"
Cohesion: 0.12
Nodes (19): asyncio, google_generativeai, io, langchain_text_splitters, _clean_text(), _extract_pdf(), _extract_pptx(), _extract_txt() (+11 more)

### Community 1 - "Code"
Cohesion: 0.08
Nodes (34): Code, In / out, Karma Points (gamification), TODOs / edge cases, KarmaEvent, KarmaEventType, KarmaMonthlyUsage, Immutable ledger entry — one row per karma point award event. (+26 more)

### Community 2 - "Code"
Cohesion: 0.23
Nodes (11): Code, _education_score(), _map_category(), Any, datetime, services/baseline_assembler.py Evidence Assembly Layer — gathers 6 evidence…, FIX (Bug #2): STRICTLY comp-id-tag-matched. Stage 2 general engagement fallback…, _tenure_score() (+3 more)

### Community 3 - "router.py"
Cohesion: 0.08
Nodes (47): bcrypt, datetime, Code, fastapi_security, jose, change_password(), _clear_refresh_cookie(), get_me() (+39 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (43): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+35 more)

### Community 5 - "MockIgotAdapter"
Cohesion: 0.06
Nodes (32): 1. Runtime topology, 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator (+24 more)

### Community 6 - "UserAuth"
Cohesion: 0.12
Nodes (27): AuthBase, fastapi_middleware_cors, UserAuth, get_achievements(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments(), get_enrollments_by_user_id() (+19 more)

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.07
Nodes (38): GyanBot(), GyanHero(), CAPABILITIES, ChatWidgetProps, MessageBubble(), renderMarkdown(), SUGGESTIONS_EN, SUGGESTIONS_HI (+30 more)

### Community 8 - "App.tsx"
Cohesion: 0.14
Nodes (18): AdminDashboard, App(), AssessmentPage, DashboardRedirect(), LearnerDashboard, TokenBridge(), ProtectedRoute(), ProtectedRouteProps (+10 more)

### Community 9 - "Code"
Cohesion: 0.16
Nodes (17): Code, CompetencyOverviewTable(), LevelPips(), priorityOf(), Props, CONFIDENCE_CONFIG, DOMAIN_BADGE, EvidenceBar() (+9 more)

### Community 10 - "AdminDashboard.tsx"
Cohesion: 0.13
Nodes (25): Code, StatCard(), AdminKPIs, AdminRosterRow, GAP_COLORS, HeatmapEntry, levelToNumber(), useAdminData() (+17 more)

### Community 11 - "authApi.ts"
Cohesion: 0.27
Nodes (11): AuthProvider(), mapRole(), changePassword(), extractError(), getMe(), login(), LoginResponse, logout() (+3 more)

### Community 12 - "CLAUDE.md"
Cohesion: 0.18
Nodes (8): Admin Dashboard, Connections, In / out, TODOs / edge cases, Connections, Gyan — Multilingual Chat Assistant, In / out, TODOs / edge cases

### Community 13 - "mock-igot-server/main.py"
Cohesion: 0.13
Nodes (22): contextlib, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history(), health() (+14 more)

### Community 14 - "_assert_self_or_admin"
Cohesion: 0.16
Nodes (16): Connections, _assert_self_or_admin(), award_karma_event(), CbpClaimRequest, claim_cbp_bonus(), get_karma_ledger(), KarmaEventRequest, BaseModel (+8 more)

### Community 15 - "mock_igot_server.py"
Cohesion: 0.05
Nodes (69): Code, Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server), TODOs / edge cases, exception_handler, fastapi_responses, field_validator (+61 more)

### Community 16 - "seed_data.py"
Cohesion: 0.14
Nodes (24): faker, hashlib, enrich_course(), main(), FILE: mock-igot-server/enrich_catalog.py…, Returns a deterministic RNG seeded by the course identifier hash., Add quality fields to a course dict (in-place, idempotent)., _seeded_rng() (+16 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "domain.ts"
Cohesion: 0.14
Nodes (14): ProfileHeaderProps, BaseUser, Competency, CompetencyProfile, Course, JobRole, KarmaBreakdown, KarmaMonthlyUsage (+6 more)

### Community 19 - "LearnerDashboard.tsx"
Cohesion: 0.12
Nodes (20): AssessmentUploadZone(), AssessmentUploadZoneProps, AppShell(), AppShellProps, ShellNavGroup, ShellNavItem, PageHeader(), PageHeaderProps (+12 more)

### Community 20 - "main-lms-backend/main.py"
Cohesion: 0.12
Nodes (19): get_achievements_by_user_id(), get_admin_roster(), get_enrollments_by_user_id(), get_frac_competencies(), get_profile_by_user_id(), get_recommendations_by_user_id(), get_skill_gaps_by_user_id(), _level_to_int() (+11 more)

### Community 21 - "Code"
Cohesion: 0.08
Nodes (27): Code, Code, Connections, In / out, Shared Multilingual Embedder, TODOs / edge cases, get_embedder(), _OnnxEmbedder (+19 more)

### Community 22 - "chatbot.py"
Cohesion: 0.10
Nodes (38): collections, difflib, Code, is_embedder_ready(), Non-blocking check — True only if the singleton is already loaded., classify_intent(), _correct_tokens(), _ensure_prototypes() (+30 more)

### Community 23 - "RightSidebar.tsx"
Cohesion: 0.14
Nodes (16): TODOs / edge cases, CareerCard(), EVENT_META, KarmaCard(), milestones, MilestoneStep, MilestoneStepper(), MonthlyCapBar() (+8 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "vector_store.py"
Cohesion: 0.18
Nodes (16): Code, Embeds all baseline knowledge into ChromaDB., seed(), add_documents_from_file(), add_text_to_store(), _get_embeddings(), get_retriever(), get_store() (+8 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "recommendation_service.py"
Cohesion: 0.17
Nodes (12): dataclasses, dotenv, logging, FILE: ai/embedder.py…, FILE: ai/rag_engine.py…, FILE: ai/seed_knowledge.py…, scripts/quantize_model.py…, FILE: main-lms-backend/services/recommendation_service.py… (+4 more)

### Community 28 - "domain.py"
Cohesion: 0.29
Nodes (11): Achievement, AchievementsResponse, Enrollment, EnrollmentsResponse, EvidenceBreakdown, BaseModel, Per-channel evidence values after decay/discount, as used in the fusion formula., Recommendation (+3 more)

### Community 29 - "Code"
Cohesion: 0.18
Nodes (17): Code, StudioTab, _chunk_document_text(), DocumentMetadata, DocumentUploadResponse, ErrorResponse, _generate_mcqs_from_text(), GradeRequest (+9 more)

### Community 30 - "karma.py"
Cohesion: 0.18
Nodes (14): fastapi, get_db(), auth/database.py…, Yields a database session and ensures it is closed after the request., get_current_user(), Session, auth/dependencies.py…, Decodes the Bearer JWT, looks up the user in auth.db. Raises HTTP 401 for any… (+6 more)

### Community 31 - "DashboardFactory.ts"
Cohesion: 0.15
Nodes (6): AdminDashboardCreator, DashboardCreator, DashboardProps, IDashboard, OfficialDashboardCreator, TrainerDashboardCreator

### Community 32 - "ai_tools.py"
Cohesion: 0.16
Nodes (15): is_ollama_available(), Fast, synchronous check — just hits the Ollama /api/tags endpoint. Returns True…, ai_health_check(), HealthResponse, BaseModel, get, post, UploadFile (+7 more)

### Community 33 - "pydantic"
Cohesion: 0.21
Nodes (9): Code, CertificateUploadZone(), CertificateExtractionResult, DocumentExtractorService, ExtractedCompetency, BaseModel, FILE: main-lms-backend/services/document_extractor.py…, pydantic (+1 more)

### Community 34 - "seed.py"
Cohesion: 0.22
Nodes (12): httpx, _derive_password(), _fetch_officials(), main(), Session, auth/seed.py…, Insert the hardcoded admin user. Returns True if inserted, False if already…, Default password = lowercase(firstName) + last 2 digits of the numeric userId… (+4 more)

### Community 35 - "speech.d.ts"
Cohesion: 0.20
Nodes (6): SpeechRecognition, SpeechRecognitionEvent, SpeechRecognitionResult, SpeechRecognitionResultItem, SpeechRecognitionResultList, Window

### Community 36 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 37 - "competency.py"
Cohesion: 0.22
Nodes (10): calculate_baseline(), EvidencePayload, BaseModel, post, UploadFile, FILE: main-lms-backend/routers/competency.py…, Calculates the skill baseline score b_k ∈ [0, 5] using the locked 6-term…, Accepts a PDF certificate or resume from the React frontend. Extracts text →… (+2 more)

### Community 38 - "json"
Cohesion: 0.18
Nodes (10): json, _download_from_hf(), _download_from_url(), main(), scripts/download_model.py…, Download from HuggingFace Hub using huggingface_hub library., Fallback: download via urllib (no extra deps)., smoke_test.py — End-to-end API test for skill-gaps + recommendations Run from:… (+2 more)

### Community 39 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 40 - "Ollama RAG Knowledge Base (Tier 3 — disconnected)"
Cohesion: 0.22
Nodes (8): Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, build_system_prompt(), generate_chat_response(), Runs the full RAG pipeline: 1. Retrieve top-k relevant document chunks from…, Builds a rich system prompt that grounds the LLM in the user's live context.…

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 42 - "CompetencyCalculator"
Cohesion: 0.33
Nodes (5): CompetencyCalculator, datetime, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, Maps FRAC types from the JSON to calculation categories., Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…

### Community 43 - "`frontend/src/`"
Cohesion: 0.52
Nodes (7): `frontend/src/`, ChatWidget(), ProgressView(), HomeChatWidget(), useChatEngine(), useTheme(), LandingPage()

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
Cohesion: 0.16
Nodes (22): 7. Mismatches between the mermaid diagram and the code, Base, enum, Admin, Assessment, AssessmentSkillMapping, BaseUser, Competency (+14 more)

### Community 61 - "lucide-react"
Cohesion: 0.20
Nodes (15): Visual design system (shared by every page), formatDate(), ProfileHeader(), AshokaChakra(), CountUp(), GovEmblem(), Reveal(), useInView() (+7 more)

### Community 62 - "EvidenceLog"
Cohesion: 0.16
Nodes (13): 3. Core data flow, Conventions, Certificate / Resume Evidence Extraction, Connections, In / out, TODOs / edge cases, Connections, In / out (+5 more)

### Community 63 - "grade_quiz"
Cohesion: 0.33
Nodes (5): _detect_skill_name(), grade_quiz(), post, Infers or extracts the skill/competency topic dynamically from the document's…, **Grade Quiz & Sync Competency to Internal DB & Mock iGOT Server** FIX (Bug…

### Community 64 - "ProgressView.tsx"
Cohesion: 0.18
Nodes (9): ProgressViewProps, Props, RecentActivityList(), relative(), Theme, ThemeContext, ThemeContextType, ThemeProvider() (+1 more)

### Community 65 - "api.ts"
Cohesion: 0.27
Nodes (13): useLearnerDashboard(), awardKarmaEvent(), fetchAchievements(), fetchEnrollments(), fetchKarmaLedger(), fetchRecommendations(), fetchSkillGapsAndProfile(), levelToNumber() (+5 more)

### Community 66 - "BaselineAssembler"
Cohesion: 0.29
Nodes (5): AI Course Recommendation Engine, Connections, In / out, TODOs / edge cases, BaselineAssembler

### Community 67 - "useScreenReader.ts"
Cohesion: 0.53
Nodes (5): chunkText(), extractReadableText(), isHidden(), ScreenReader, useScreenReader()

### Community 68 - "CLAUDE.md — index & router"
Cohesion: 0.40
Nodes (5): CLAUDE.md — index & router, Feature index, graphify, How to use these docs, Run commands

### Community 69 - "MyCoursesView.tsx"
Cohesion: 0.22
Nodes (7): COLORS, LearningSnapshot(), Props, MyCoursesView(), MyCoursesViewProps, Enrollment, recharts

### Community 70 - "RAG Document → Quiz Generator & Grading"
Cohesion: 0.40
Nodes (4): Connections, In / out, RAG Document → Quiz Generator & Grading, TODOs / edge cases

### Community 71 - "Authentication & RBAC"
Cohesion: 0.50
Nodes (3): Authentication & RBAC, In / out, TODOs / edge cases

### Community 72 - "Learner Dashboard (frontend shell)"
Cohesion: 0.67
Nodes (3): Connections, In / out, Learner Dashboard (frontend shell)

### Community 74 - "_startup"
Cohesion: 0.67
Nodes (3): on_event, Create users_auth table if it doesn't exist yet., _startup()

## Knowledge Gaps
- **214 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+209 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 497 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Code` connect `router.py` to `api.ts`, `UserAuth`, `Authentication & RBAC`, `App.tsx`, `authApi.ts`, `karma.py`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `UserAuth` connect `UserAuth` to `rag.py`, `seed.py`, `router.py`, `require_role`, `_assert_self_or_admin`, `main-lms-backend/main.py`, `karma.py`, `grade_quiz`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `Code` connect `Code` to `rag.py`, `RAG Document → Quiz Generator & Grading`, `models/models.py`, `LearnerDashboard.tsx`, `EvidenceLog`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `Code` (e.g. with `AssessmentUploadZone()` and `ChatWidget()`) actually correct?**
  _`Code` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `Code` (e.g. with `KarmaCard()` and `MonthlyCapBar()`) actually correct?**
  _`Code` has 23 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _214 weakly-connected nodes found - possible documentation gaps or missing edges._