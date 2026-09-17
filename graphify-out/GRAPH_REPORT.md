# Graph Report - SIH_IGot  (2026-09-18)

## Corpus Check
- 122 files · ~4,734,485 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .css 1, .example 1)

## Summary
- 1154 nodes · 2355 edges · 67 communities (54 shown, 13 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 291 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dcfb1c87`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- rag.py
- Code
- document_extractor.py
- router.py
- package.json
- igot_adapter.py
- main_backup.py
- ChatWidget.tsx
- App.tsx
- Code
- AdminDashboard.tsx
- authApi.ts
- CLAUDE.md
- mock-igot-server/main.py
- UserAuth
- mock_igot_server.py
- seed_data.py
- What You Must Do When Invoked
- domain.ts
- MockIgotAdapter
- main-lms-backend/main.py
- Code
- chatbot.py
- RightSidebar.tsx
- compilerOptions
- ai_tools.py
- 🇮🇳 MoSPI Skill Intelligence Platform
- recommendation_service.py
- domain.py
- competency.py
- dependencies.py
- DashboardFactory.ts
- Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)
- get_embedder
- speech.d.ts
- graphify reference: extra exports and benchmark
- download_model.py
- compilerOptions
- graphify reference: query, path, explain
- is_semantic_engine_ready
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
- `frontend/src/`
- api.ts
- chatApi.ts
- CourseCard.tsx
- LearnerDashboard.tsx
- RecentActivityList.tsx
- semantic_engine.py

## God Nodes (most connected - your core abstractions)
1. `UserAuth` - 42 edges
2. `react` - 35 edges
3. `Code` - 30 edges
4. `Code` - 24 edges
5. `lucide-react` - 21 edges
6. ``frontend/src/`` - 21 edges
7. `MockIgotAdapter` - 20 edges
8. `Code` - 19 edges
9. `Code` - 18 edges
10. `EvidenceLog` - 17 edges

## Surprising Connections (you probably didn't know these)
- `Code` --references--> `PassbookRow()`  [INFERRED]
  docs/features/karma-points.md → frontend/src/components/dashboard/RightSidebar.tsx
- `Code` --references--> `MonthlyCapBar()`  [INFERRED]
  docs/features/karma-points.md → frontend/src/components/dashboard/RightSidebar.tsx
- `Code` --references--> `StatTone`  [INFERRED]
  docs/features/learner-dashboard.md → frontend/src/components/shell/StatCard.tsx
- `Connections` --references--> `useTheme()`  [INFERRED]
  docs/features/chatbot-gyan.md → frontend/src/hooks/useTheme.tsx
- `Code` --references--> `StudioPromo()`  [INFERRED]
  docs/features/learner-dashboard.md → frontend/src/pages/LearnerDashboard.tsx

## Import Cycles
- None detected.

## Communities (67 total, 13 thin omitted)

### Community 0 - "rag.py"
Cohesion: 0.10
Nodes (35): asyncio, Code, StudioTab, google_generativeai, io, langchain_text_splitters, _chunk_document_text(), _clean_text() (+27 more)

### Community 1 - "Code"
Cohesion: 0.08
Nodes (35): dataclasses, Code, In / out, Karma Points (gamification), TODOs / edge cases, KarmaEvent, KarmaEventType, KarmaMonthlyUsage (+27 more)

### Community 2 - "document_extractor.py"
Cohesion: 0.21
Nodes (9): Code, CertificateUploadZone(), CertificateExtractionResult, DocumentExtractorService, ExtractedCompetency, BaseModel, FILE: main-lms-backend/services/document_extractor.py…, pypdf (+1 more)

### Community 3 - "router.py"
Cohesion: 0.06
Nodes (58): bcrypt, datetime, Code, fastapi_security, jose, change_password(), _clear_refresh_cookie(), get_me() (+50 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (43): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+35 more)

### Community 5 - "igot_adapter.py"
Cohesion: 0.14
Nodes (12): ILearningPlatformAdapter, _prof_detail(), ABC, Any, adapters/igot_adapter.py — iGOT Platform Adapter…, Safely read a field from profileDetails.professionalDetails[0]., Interface for external learning platform integration. All concrete adapters…, Return the full CBP course catalog. (+4 more)

### Community 6 - "main_backup.py"
Cohesion: 0.10
Nodes (28): get_achievements(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments(), get_enrollments_by_user_id(), get_profile_by_user_id(), get_recommendations(), get_recommendations_by_user_id() (+20 more)

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.20
Nodes (13): ChatWidgetProps, MessageBubble(), renderMarkdown(), SUGGESTIONS_EN, SUGGESTIONS_HI, SkillGapCardProps, PendingNavAction, UseChatEngineOptions (+5 more)

### Community 8 - "App.tsx"
Cohesion: 0.11
Nodes (25): AdminDashboard, App(), AssessmentPage, DashboardRedirect(), LearnerDashboard, ProtectedRoute(), ProtectedRouteProps, AppShell() (+17 more)

### Community 9 - "Code"
Cohesion: 0.18
Nodes (13): Code, CompetencyOverviewTable(), LevelPips(), priorityOf(), Props, CONFIDENCE_CONFIG, DOMAIN_BADGE, EvidenceBar() (+5 more)

### Community 10 - "AdminDashboard.tsx"
Cohesion: 0.13
Nodes (25): Code, StatCard(), AdminKPIs, AdminRosterRow, GAP_COLORS, HeatmapEntry, levelToNumber(), useAdminData() (+17 more)

### Community 11 - "authApi.ts"
Cohesion: 0.29
Nodes (10): AuthProvider(), mapRole(), extractError(), getMe(), login(), LoginResponse, logout(), refresh() (+2 more)

### Community 12 - "CLAUDE.md"
Cohesion: 0.05
Nodes (38): CLAUDE.md — index & router, Feature index, graphify, How to use these docs, Run commands, Admin Dashboard, Connections, In / out (+30 more)

### Community 13 - "mock-igot-server/main.py"
Cohesion: 0.13
Nodes (22): contextlib, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history(), health() (+14 more)

### Community 14 - "UserAuth"
Cohesion: 0.17
Nodes (18): AuthBase, UserAuth, _assert_self_or_admin(), award_karma_event(), CbpClaimRequest, claim_cbp_bonus(), get_karma_ledger(), KarmaEventRequest (+10 more)

### Community 15 - "mock_igot_server.py"
Cohesion: 0.05
Nodes (71): Code, Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server), TODOs / edge cases, exception_handler, fastapi_responses, field_validator (+63 more)

### Community 16 - "seed_data.py"
Cohesion: 0.13
Nodes (25): faker, hashlib, enrich_course(), main(), FILE: mock-igot-server/enrich_catalog.py…, Returns a deterministic RNG seeded by the course identifier hash., Add quality fields to a course dict (in-place, idempotent)., _seeded_rng() (+17 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "domain.ts"
Cohesion: 0.13
Nodes (15): ProfileHeaderProps, BaseUser, Competency, CompetencyProfile, Course, JobRole, KarmaBreakdown, KarmaMonthlyUsage (+7 more)

### Community 19 - "MockIgotAdapter"
Cohesion: 0.16
Nodes (10): Connections, MockIgotAdapter, GET /api/content/read Returns: result.content — list of Sunbird course objects., GET /api/user/v2/read/{user_id} Returns: result.response — single user object…, GET /api/course/v1/user/enrollment/list/{user_id} Returns: result.courses —…, GET /api/admin/v1/users Returns: result.users — full list of officials., Legacy method that maps fetch_user_enrollments to the old simple-mock shape.…, Safely drill into a Sunbird envelope: data['result']['key1']['key2']... (+2 more)

### Community 20 - "main-lms-backend/main.py"
Cohesion: 0.10
Nodes (24): fastapi_middleware_cors, httpx, json, get_db(), Yields a database session and ensures it is closed after the request., get_achievements_by_user_id(), get_admin_roster(), get_enrollments_by_user_id() (+16 more)

### Community 21 - "Code"
Cohesion: 0.14
Nodes (16): Code, on_event, Create users_auth table and karma tables if they don't exist yet., _startup(), _CourseDoc, GapEntry, HybridRecommendationEngine, BaseModel (+8 more)

### Community 22 - "chatbot.py"
Cohesion: 0.21
Nodes (22): Code, Maps a list of skill gap dicts (from ChatRequest) into a flat numeric feature…, vectorize_profile(), chat(), ChatHistoryItem, ChatRequest, ChatResponse, detect_intent_keyword() (+14 more)

### Community 23 - "RightSidebar.tsx"
Cohesion: 0.11
Nodes (19): Connections, In / out, Learner Dashboard (frontend shell), TODOs / edge cases, CareerCard(), EVENT_META, KarmaCard(), milestones (+11 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "ai_tools.py"
Cohesion: 0.06
Nodes (42): Code, Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, dotenv, build_system_prompt(), generate_chat_response() (+34 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "recommendation_service.py"
Cohesion: 0.19
Nodes (10): logging, FILE: ai/embedder.py…, FILE: ai/rag_engine.py…, scripts/quantize_model.py…, FILE: main-lms-backend/services/recommendation_service.py…, numpy, os, rank_bm25 (+2 more)

### Community 28 - "domain.py"
Cohesion: 0.29
Nodes (11): Achievement, AchievementsResponse, Enrollment, EnrollmentsResponse, EvidenceBreakdown, BaseModel, Per-channel evidence values after decay/discount, as used in the fusion formula., Recommendation (+3 more)

### Community 29 - "competency.py"
Cohesion: 0.22
Nodes (10): calculate_baseline(), EvidencePayload, BaseModel, post, UploadFile, FILE: main-lms-backend/routers/competency.py…, Calculates the skill baseline score b_k ∈ [0, 5] using the locked 6-term…, Accepts a PDF certificate or resume from the React frontend. Extracts text →… (+2 more)

### Community 30 - "dependencies.py"
Cohesion: 0.15
Nodes (13): fastapi, auth/database.py…, get_current_user(), Session, auth/dependencies.py…, Decodes the Bearer JWT, looks up the user in auth.db. Raises HTTP 401 for any…, Returns a FastAPI dependency that checks the current user's role. Example:…, require_role() (+5 more)

### Community 31 - "DashboardFactory.ts"
Cohesion: 0.14
Nodes (7): AdminDashboardCreator, DashboardCreator, DashboardFactory, DashboardProps, IDashboard, OfficialDashboardCreator, TrainerDashboardCreator

### Community 32 - "Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)"
Cohesion: 0.22
Nodes (8): 1. Runtime topology, 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator

### Community 34 - "get_embedder"
Cohesion: 0.16
Nodes (13): Code, Connections, In / out, Shared Multilingual Embedder, TODOs / edge cases, get_embedder(), is_embedder_ready(), _OnnxEmbedder (+5 more)

### Community 35 - "speech.d.ts"
Cohesion: 0.20
Nodes (6): SpeechRecognition, SpeechRecognitionEvent, SpeechRecognitionResult, SpeechRecognitionResultItem, SpeechRecognitionResultList, Window

### Community 36 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 38 - "download_model.py"
Cohesion: 0.28
Nodes (7): _download_from_hf(), _download_from_url(), main(), scripts/download_model.py…, Download from HuggingFace Hub using huggingface_hub library., Fallback: download via urllib (no extra deps)., urllib_request

### Community 39 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 43 - "is_semantic_engine_ready"
Cohesion: 0.40
Nodes (5): is_semantic_engine_ready(), True if the shared embedder is loaded AND prototypes are encoded., chat_mode(), get, Returns which response engine is currently active. Frontend can use this to…

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
Cohesion: 0.18
Nodes (18): Visual design system (shared by every page), formatDate(), ProfileHeader(), AshokaChakra(), CountUp(), GovEmblem(), Reveal(), useInView() (+10 more)

### Community 62 - "EvidenceLog"
Cohesion: 0.16
Nodes (13): 3. Core data flow, Conventions, Certificate / Resume Evidence Extraction, Connections, In / out, TODOs / edge cases, Connections, In / out (+5 more)

### Community 63 - "grade_quiz"
Cohesion: 0.18
Nodes (9): Authentication & RBAC, Connections, In / out, TODOs / edge cases, _detect_skill_name(), grade_quiz(), post, Infers or extracts the skill/competency topic dynamically from the document's… (+1 more)

### Community 64 - "`frontend/src/`"
Cohesion: 0.12
Nodes (16): `frontend/src/`, ChatWidget(), ProgressView(), HomeChatWidgetProps, MessageBubble(), renderMarkdown(), SUGGESTIONS_EN, SUGGESTIONS_HI (+8 more)

### Community 65 - "api.ts"
Cohesion: 0.20
Nodes (17): TokenBridge(), Props, MyCoursesViewProps, useLearnerDashboard(), awardKarmaEvent(), fetchAchievements(), fetchEnrollments(), fetchKarmaLedger() (+9 more)

### Community 66 - "chatApi.ts"
Cohesion: 0.29
Nodes (10): buildLocalReply(), ChatApiPayload, detectIntent(), detectLanguage(), fmtGaps(), fmtRecs(), HINGLISH_WORDS, INTENT_PATTERNS (+2 more)

### Community 68 - "CourseCard.tsx"
Cohesion: 0.24
Nodes (8): CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps, SOURCE_STYLES, matches(), Props, RecommendationsPanel()

### Community 69 - "LearnerDashboard.tsx"
Cohesion: 0.11
Nodes (14): AssessmentUploadZone(), AssessmentUploadZoneProps, COLORS, LearningSnapshot(), MyCoursesView(), PageHeader(), PageHeaderProps, SectionAction() (+6 more)

### Community 70 - "RecentActivityList.tsx"
Cohesion: 0.47
Nodes (5): ProgressViewProps, Props, RecentActivityList(), relative(), Achievement

### Community 71 - "semantic_engine.py"
Cohesion: 0.24
Nodes (9): collections, difflib, classify_intent(), _correct_tokens(), _ensure_prototypes(), FILE: ai/semantic_engine.py…, Encode all intent prototype phrases once, via the shared singleton embedder., Classify the user query into one of the intent categories. Steps: 1. Fuzzy-… (+1 more)

## Knowledge Gaps
- **211 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+206 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 494 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Code` connect `router.py` to `api.ts`, `authApi.ts`, `UserAuth`, `main-lms-backend/main.py`, `dependencies.py`, `grade_quiz`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Why does `UserAuth` connect `UserAuth` to `rag.py`, `router.py`, `main_backup.py`, `main-lms-backend/main.py`, `dependencies.py`, `grade_quiz`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Why does `Code` connect `rag.py` to `App.tsx`, `models/models.py`, `CLAUDE.md`, `EvidenceLog`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `Code` (e.g. with `AssessmentUploadZone()` and `ChatWidget()`) actually correct?**
  _`Code` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `Code` (e.g. with `KarmaCard()` and `MonthlyCapBar()`) actually correct?**
  _`Code` has 23 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _211 weakly-connected nodes found - possible documentation gaps or missing edges._