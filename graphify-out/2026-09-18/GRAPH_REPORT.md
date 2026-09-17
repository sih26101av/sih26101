# Graph Report - SIH_IGot  (2026-09-18)

## Corpus Check
- 166 files · ~4,813,170 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .css 1, .example 1)

## Summary
- 1279 nodes · 2651 edges · 87 communities (63 shown, 24 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 318 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4240632f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ReplyContext
- Code
- Code
- router.py
- package.json
- ILearningPlatformAdapter
- UserAuth
- ChatWidget.tsx
- react
- LearnerDashboard.tsx
- AdminDashboard.tsx
- authApi.ts
- AssessmentPage.tsx
- mock-igot-server/main.py
- _assert_self_or_admin
- _require_auth
- seed_data.py
- What You Must Do When Invoked
- domain.ts
- mock_igot_server.py
- BaseModel
- recommendation_service.py
- chatbot.py
- test_chat_messages.py
- compilerOptions
- logging
- 🇮🇳 MoSPI Skill Intelligence Platform
- os
- test_reply_regression.py
- get_embedder
- main-lms-backend/main.py
- DashboardCreator
- Code
- MockIgotAdapter
- CompetencyCalculator
- speech.d.ts
- graphify reference: extra exports and benchmark
- calculate_baseline
- CourseCard.tsx
- compilerOptions
- semantic_engine.py
- graphify reference: query, path, explain
- CLAUDE.md
- ai_tools.py
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- rag.py
- .claude/CLAUDE.md
- extraction-spec.md
- `frontend/src/`
- language_service.py
- eval_intents.py
- get_current_user
- api.ts
- test_chat_endpoint.py
- useScreenReader.ts
- get_enriched_courses
- MyCoursesView.tsx
- ingest_telemetry
- CLAUDE.md — index & router
- Gyan — Multilingual Chat Assistant
- Mock iGOT Karmayogi Integration (Adapter + mock server)
- RAG Document → Quiz Generator & Grading
- chat_actions.py
- _competencies
- _prof_detail
- bn.py
- en.py
- gu.py
- hi.py
- hi_latn.py
- mr.py
- or_.py
- ta.py
- te.py

## God Nodes (most connected - your core abstractions)
1. `UserAuth` - 42 edges
2. `react` - 37 edges
3. `ReplyContext` - 30 edges
4. `Code` - 30 edges
5. `Code` - 24 edges
6. `lucide-react` - 21 edges
7. ``frontend/src/`` - 21 edges
8. `MockIgotAdapter` - 20 edges
9. `Code` - 19 edges
10. `Code` - 18 edges

## Surprising Connections (you probably didn't know these)
- `Code` --references--> `PassbookRow()`  [INFERRED]
  docs/features/karma-points.md → frontend/src/components/dashboard/RightSidebar.tsx
- `Code` --references--> `MonthlyCapBar()`  [INFERRED]
  docs/features/karma-points.md → frontend/src/components/dashboard/RightSidebar.tsx
- `Code` --references--> `StatTone`  [INFERRED]
  docs/features/learner-dashboard.md → frontend/src/components/shell/StatCard.tsx
- `Connections` --references--> `useTheme()`  [INFERRED]
  docs/features/chatbot-gyan.md → frontend/src/hooks/useTheme.tsx
- `7. Mismatches between the mermaid diagram and the code` --references--> `SkillGapReport`  [INFERRED]
  ARCHITECTURE.md → frontend/src/types/domain.ts

## Import Cycles
- None detected.

## Communities (87 total, 24 thin omitted)

### Community 0 - "ReplyContext"
Cohesion: 0.15
Nodes (20): functools, importlib, Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile(), Any, Everything a reply template may personalise, built once per chat request., ReplyContext, _by_page() (+12 more)

### Community 1 - "Code"
Cohesion: 0.08
Nodes (34): Code, In / out, Karma Points (gamification), TODOs / edge cases, KarmaEvent, KarmaEventType, KarmaMonthlyUsage, Immutable ledger entry — one row per karma point award event. (+26 more)

### Community 2 - "Code"
Cohesion: 0.24
Nodes (11): Connections, Code, BaselineAssembler, _education_score(), _map_category(), Any, datetime, services/baseline_assembler.py Evidence Assembly Layer — gathers 6 evidence… (+3 more)

### Community 3 - "router.py"
Cohesion: 0.06
Nodes (57): bcrypt, datetime, Code, jose, change_password(), _clear_refresh_cookie(), get_me(), login() (+49 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (43): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+35 more)

### Community 5 - "ILearningPlatformAdapter"
Cohesion: 0.06
Nodes (30): 1. Runtime topology, 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator (+22 more)

### Community 6 - "UserAuth"
Cohesion: 0.08
Nodes (40): AuthBase, UserAuth, get_achievements(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments(), get_enrollments_by_user_id(), get_profile_by_user_id() (+32 more)

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.08
Nodes (34): GyanBot(), GyanHero(), CAPABILITIES, ChatWidgetProps, MessageBubble(), renderMarkdown(), SUGGESTIONS_EN, SUGGESTIONS_HI (+26 more)

### Community 8 - "react"
Cohesion: 0.11
Nodes (19): AdminDashboard, App(), DashboardRedirect(), LearnerDashboard, ProtectedRouteProps, AuthContext, AuthContextType, AuthUser (+11 more)

### Community 9 - "LearnerDashboard.tsx"
Cohesion: 0.08
Nodes (30): Code, Connections, In / out, Learner Dashboard (frontend shell), TODOs / edge cases, AssessmentUploadZone(), AssessmentUploadZoneProps, CompetencyOverviewTable() (+22 more)

### Community 10 - "AdminDashboard.tsx"
Cohesion: 0.11
Nodes (28): Code, StatCard(), StatCardProps, StatTone, TONES, AdminKPIs, AdminRosterRow, GAP_COLORS (+20 more)

### Community 11 - "authApi.ts"
Cohesion: 0.29
Nodes (9): AuthProvider(), mapRole(), extractError(), getMe(), login(), LoginResponse, logout(), RefreshResponse (+1 more)

### Community 12 - "AssessmentPage.tsx"
Cohesion: 0.24
Nodes (8): AssessmentPage, ShellNavGroup, PageHeader(), PageHeaderProps, AssessmentPage(), DIFFICULTIES, Difficulty, formatDate()

### Community 13 - "mock-igot-server/main.py"
Cohesion: 0.12
Nodes (23): fastapi_middleware_cors, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history(), health() (+15 more)

### Community 14 - "_assert_self_or_admin"
Cohesion: 0.17
Nodes (15): _assert_self_or_admin(), award_karma_event(), CbpClaimRequest, claim_cbp_bonus(), get_karma_ledger(), KarmaEventRequest, BaseModel, get (+7 more)

### Community 15 - "_require_auth"
Cohesion: 0.22
Nodes (19): Code, JSONResponse, _course_by_id(), get_admin_roster(), get_competencies(), get_course_catalog(), get_user_enrolments(), get_user_profile() (+11 more)

### Community 16 - "seed_data.py"
Cohesion: 0.14
Nodes (24): faker, hashlib, enrich_course(), main(), FILE: mock-igot-server/enrich_catalog.py…, Returns a deterministic RNG seeded by the course identifier hash., Add quality fields to a course dict (in-place, idempotent)., _seeded_rng() (+16 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "domain.ts"
Cohesion: 0.10
Nodes (22): formatDate(), ProfileHeader(), ProfileHeaderProps, ProgressViewProps, Props, RecentActivityList(), relative(), Achievement (+14 more)

### Community 19 - "mock_igot_server.py"
Cohesion: 0.14
Nodes (17): contextlib, fastapi_responses, health(), legacy_catalog(), legacy_frac(), legacy_job_profiles(), lifespan(), _load_json() (+9 more)

### Community 20 - "BaseModel"
Cohesion: 0.13
Nodes (16): CompetencyOut, ContentStateRequest, CourseOut, EnrolPayload, get_content_state(), JobProfileOut, legacy_enroll_user(), legacy_push_score() (+8 more)

### Community 21 - "recommendation_service.py"
Cohesion: 0.14
Nodes (17): dataclasses, Code, _CourseDoc, GapEntry, HybridRecommendationEngine, BaseModel, FILE: main-lms-backend/services/recommendation_service.py…, Bayesian shrinkage toward global prior mean. Returns None if either input is… (+9 more)

### Community 22 - "chatbot.py"
Cohesion: 0.24
Nodes (20): chat(), ChatRequest, ChatResponse, detect_intent_keyword(), _intent_response(), _intercept(), post, FILE: routers/chatbot.py Multilingual AI Learning Assistant — Gyan (ज्ञान)… (+12 more)

### Community 23 - "test_chat_messages.py"
Cohesion: 0.23
Nodes (11): Loads a language's template table on first use ("or" lives in or_.py; `or` is a…, templates(), _alternatives(), _fields(), parametrize, Catalogue completeness: every language has every template, placeholders are…, test_every_intent_renders(), test_placeholders_match_english() (+3 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "logging"
Cohesion: 0.06
Nodes (41): Code, Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, dotenv, logging, build_system_prompt() (+33 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "os"
Cohesion: 0.22
Nodes (6): httpx, json, scripts/quantize_model.py…, smoke_test.py — End-to-end API test for skill-gaps + recommendations Run from:…, os, sys

### Community 28 - "test_reply_regression.py"
Cohesion: 0.27
Nodes (10): asyncio, ChatHistoryItem, BaseModel, RecommendationContext, SkillGapContext, sample_request(), parametrize, English and Hinglish replies must match the pre-catalogue output, except… (+2 more)

### Community 29 - "get_embedder"
Cohesion: 0.14
Nodes (14): Code, Connections, In / out, Shared Multilingual Embedder, TODOs / edge cases, _Embedder, get_embedder(), _load() (+6 more)

### Community 30 - "main-lms-backend/main.py"
Cohesion: 0.09
Nodes (30): fastapi, fastapi_security, get_db(), auth/database.py…, Yields a database session and ensures it is closed after the request., auth/dependencies.py…, Returns a FastAPI dependency that checks the current user's role. Example:…, require_role() (+22 more)

### Community 31 - "DashboardCreator"
Cohesion: 0.16
Nodes (4): AdminDashboardCreator, DashboardCreator, OfficialDashboardCreator, TrainerDashboardCreator

### Community 32 - "Code"
Cohesion: 0.18
Nodes (12): Code, classify_intent(), _correct_tokens(), _ensure_prototypes(), Encode all prototype phrases once, via the shared singleton embedder., Per-intent confidence for `query`, searched within `lang`'s pool only., Returns (best_intent, confidence). ("general", 0.0) if the embedder is…, Fuzzy-correct English UI vocabulary typos ('dasboard' -> 'dashboard'). (+4 more)

### Community 33 - "MockIgotAdapter"
Cohesion: 0.21
Nodes (9): MockIgotAdapter, adapters/igot_adapter.py — iGOT Platform Adapter…, Calls the Sunbird-compliant mock iGOT server (mock_igot_server.py) on port 8001…, FILE: main-lms-backend/routers/competency.py…, FILE: main-lms-backend/services/document_extractor.py…, pydantic, pypdf, requests (+1 more)

### Community 34 - "CompetencyCalculator"
Cohesion: 0.24
Nodes (7): CompetencyCalculator, datetime, FILE: main-lms-backend/services/competency_service.py…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, Maps FRAC types from the JSON to calculation categories., Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, math

### Community 35 - "speech.d.ts"
Cohesion: 0.20
Nodes (6): SpeechRecognition, SpeechRecognitionEvent, SpeechRecognitionResult, SpeechRecognitionResultItem, SpeechRecognitionResultList, Window

### Community 36 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 37 - "calculate_baseline"
Cohesion: 0.25
Nodes (8): calculate_baseline(), EvidencePayload, BaseModel, post, UploadFile, Calculates the skill baseline score b_k ∈ [0, 5] using the locked 6-term…, Accepts a PDF certificate or resume from the React frontend. Extracts text →…, upload_certificate()

### Community 38 - "CourseCard.tsx"
Cohesion: 0.27
Nodes (7): CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps, SOURCE_STYLES, matches(), RecommendationsPanel()

### Community 39 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 40 - "semantic_engine.py"
Cohesion: 0.21
Nodes (12): difflib, is_embedder_ready(), model_name(), Non-blocking check — True only if the role's model is already loaded., is_semantic_engine_ready(), load_corpus(), low_confidence_threshold(), FILE: ai/semantic_engine.py… (+4 more)

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 42 - "CLAUDE.md"
Cohesion: 0.20
Nodes (7): Admin Dashboard, Connections, In / out, TODOs / edge cases, AI Course Recommendation Engine, In / out, TODOs / edge cases

### Community 43 - "ai_tools.py"
Cohesion: 0.22
Nodes (10): HealthResponse, BaseModel, post, UploadFile, FILE: routers/ai_tools.py…, Accepts a PDF file, embeds it into the local ChromaDB vector store using nomic-…, upload_knowledge_document(), UploadKnowledgeResponse (+2 more)

### Community 44 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 45 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 46 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 49 - "rag.py"
Cohesion: 0.05
Nodes (72): 3. Core data flow, 7. Mismatches between the mermaid diagram and the code, Base, Conventions, Certificate / Resume Evidence Extraction, Connections, In / out, TODOs / edge cases (+64 more)

### Community 61 - "`frontend/src/`"
Cohesion: 0.14
Nodes (27): `frontend/src/`, Visual design system (shared by every page), ChatWidget(), ProgressView(), AshokaChakra(), CountUp(), GovEmblem(), Reveal() (+19 more)

### Community 62 - "language_service.py"
Cohesion: 0.24
Nodes (10): detect_chat_language(), detect_chat_variant_or_none(), _devanagari_language(), Small, offline language routing for Gyan chat. This deliberately does *not* use…, Supported ISO 639-1 code for a chat message., The variant the *text itself* signals, or None when it carries no signal. Plain…, Pick the reply variant for a message, honouring the UI language picker. A…, resolve_chat_variant() (+2 more)

### Community 63 - "eval_intents.py"
Cohesion: 0.24
Nodes (8): argparse, collections, io, load_eval(), main(), Benchmark Gyan's intent classifier on the held-out multilingual set. python…, detect_chat_variant(), Internal language variant: en, hi (Devanagari), hi_latn (romanized Hindi), mr,…

### Community 64 - "get_current_user"
Cohesion: 0.20
Nodes (9): Authentication & RBAC, Connections, In / out, TODOs / edge cases, get_current_user(), Session, Decodes the Bearer JWT, looks up the user in auth.db. Raises HTTP 401 for any…, decode_access_token() (+1 more)

### Community 65 - "api.ts"
Cohesion: 0.12
Nodes (26): TokenBridge(), EVENT_META, KarmaCard(), milestones, MilestoneStep, MonthlyCapBar(), PassbookRow(), PILL_ORDER (+18 more)

### Community 66 - "test_chat_endpoint.py"
Cohesion: 0.36
Nodes (9): fastapi_testclient, _chat(), parametrize, End-to-end /chat behaviour per language through the real multilingual…, test_dark_mode_action(), test_my_courses_navigation(), test_recommendations(), test_skill_gaps() (+1 more)

### Community 67 - "useScreenReader.ts"
Cohesion: 0.53
Nodes (5): chunkText(), extractReadableText(), isHidden(), ScreenReader, useScreenReader()

### Community 68 - "get_enriched_courses"
Cohesion: 0.22
Nodes (9): exception_handler, HTTPException, get_enriched_courses(), get_job_profiles(), http_exc_handler(), Returns courses from courses_1.json — the 754 English iGOT courses with…, GET /api/job-profiles — NCO Job Role Catalogue (Sunbird-compliant). Served from…, _ts_now() (+1 more)

### Community 69 - "MyCoursesView.tsx"
Cohesion: 0.22
Nodes (7): COLORS, LearningSnapshot(), Props, MyCoursesView(), MyCoursesViewProps, Enrollment, recharts

### Community 70 - "ingest_telemetry"
Cohesion: 0.33
Nodes (5): field_validator, ingest_telemetry(), Returns a list of validation errors for a single telemetry event., TelemetryBatch, _validate_event()

### Community 71 - "CLAUDE.md — index & router"
Cohesion: 0.40
Nodes (5): CLAUDE.md — index & router, Feature index, graphify, How to use these docs, Run commands

### Community 72 - "Gyan — Multilingual Chat Assistant"
Cohesion: 0.40
Nodes (4): Connections, Gyan — Multilingual Chat Assistant, In / out, TODOs / edge cases

### Community 73 - "Mock iGOT Karmayogi Integration (Adapter + mock server)"
Cohesion: 0.40
Nodes (4): Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server), TODOs / edge cases

### Community 74 - "RAG Document → Quiz Generator & Grading"
Cohesion: 0.40
Nodes (4): Connections, In / out, RAG Document → Quiz Generator & Grading, TODOs / edge cases

### Community 75 - "chat_actions.py"
Cohesion: 0.50
Nodes (4): detect_ui_actions(), _mentions(), Detect website theme / language changes requested in any supported chat…, Returns (theme, language): theme in {"dark", "light", "toggle"}, language in…

## Knowledge Gaps
- **215 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+210 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 538 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Code` connect `Code` to `ChatWidget.tsx`, `semantic_engine.py`, `Gyan — Multilingual Chat Assistant`, `chatbot.py`, ``frontend/src/``, `language_service.py`, `eval_intents.py`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `UserAuth` connect `UserAuth` to `get_current_user`, `router.py`, `_assert_self_or_admin`, `rag.py`, `main-lms-backend/main.py`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Why does `Code` connect `router.py` to `get_current_user`, `api.ts`, `UserAuth`, `authApi.ts`, `main-lms-backend/main.py`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `ReplyContext` (e.g. with `chat()` and `_intent_response()`) actually correct?**
  _`ReplyContext` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `Code` (e.g. with `AssessmentUploadZone()` and `ChatWidget()`) actually correct?**
  _`Code` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `Code` (e.g. with `KarmaCard()` and `MonthlyCapBar()`) actually correct?**
  _`Code` has 23 INFERRED edges - model-reasoned connections that need verification._