# Graph Report - SIH_IGot  (2026-09-17)

## Corpus Check
- 113 files · ~4,727,615 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .css 1, .example 1)

## Summary
- 1105 nodes · 2196 edges · 61 communities (48 shown, 13 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 269 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dcfb1c87`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- rag.py
- Code
- competency.py
- router.py
- package.json
- MockIgotAdapter
- main_backup.py
- ChatWidget.tsx
- App.tsx
- LearnerDashboard.tsx
- AdminDashboard.tsx
- api.ts
- CLAUDE.md
- mock-igot-server/main.py
- karma.py
- mock_igot_server.py
- seed_data.py
- What You Must Do When Invoked
- domain.ts
- _require_auth
- UserAuth
- recommendation_service.py
- chatbot.py
- RightSidebar.tsx
- compilerOptions
- ai_tools.py
- 🇮🇳 MoSPI Skill Intelligence Platform
- semantic_engine.py
- main-lms-backend/main.py
- vector_store.py
- os
- DashboardCreator
- seed.py
- get
- _OnnxEmbedder
- speech.d.ts
- graphify reference: extra exports and benchmark
- Ollama RAG Knowledge Base (Tier 3 — disconnected)
- download_model.py
- compilerOptions
- lifespan
- graphify reference: query, path, explain
- Mock iGOT Karmayogi Integration (Adapter + mock server)
- is_semantic_engine_ready
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- _startup
- .claude/CLAUDE.md
- extraction-spec.md

## God Nodes (most connected - your core abstractions)
1. `UserAuth` - 42 edges
2. `react` - 26 edges
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

## Communities (61 total, 13 thin omitted)

### Community 0 - "rag.py"
Cohesion: 0.05
Nodes (74): 3. Core data flow, 7. Mismatches between the mermaid diagram and the code, asyncio, Base, Conventions, Certificate / Resume Evidence Extraction, Connections, In / out (+66 more)

### Community 1 - "Code"
Cohesion: 0.08
Nodes (34): Code, In / out, Karma Points (gamification), TODOs / edge cases, KarmaEvent, KarmaEventType, KarmaMonthlyUsage, Immutable ledger entry — one row per karma point award event. (+26 more)

### Community 2 - "competency.py"
Cohesion: 0.06
Nodes (37): Code, Code, CertificateUploadZone(), calculate_baseline(), EvidencePayload, BaseModel, post, UploadFile (+29 more)

### Community 3 - "router.py"
Cohesion: 0.09
Nodes (43): bcrypt, datetime, Code, jose, change_password(), _clear_refresh_cookie(), login(), logout() (+35 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (43): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+35 more)

### Community 5 - "MockIgotAdapter"
Cohesion: 0.07
Nodes (30): 1. Runtime topology, 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator (+22 more)

### Community 6 - "main_backup.py"
Cohesion: 0.07
Nodes (36): fastapi, fastapi_security, auth/database.py…, auth/dependencies.py…, Returns a FastAPI dependency that checks the current user's role. Example:…, require_role(), auth/models.py…, get_achievements() (+28 more)

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.09
Nodes (30): ChatWidget(), ChatWidgetProps, MessageBubble(), renderMarkdown(), SUGGESTIONS_EN, SUGGESTIONS_HI, HomeChatWidget(), HomeChatWidgetProps (+22 more)

### Community 8 - "App.tsx"
Cohesion: 0.12
Nodes (26): App(), AssessmentPage, DashboardRedirect(), ProtectedRoute(), ProtectedRouteProps, AuthContext, AuthContextType, AuthUser (+18 more)

### Community 9 - "LearnerDashboard.tsx"
Cohesion: 0.08
Nodes (27): Code, LearnerDashboard, AssessmentUploadZone(), AssessmentUploadZoneProps, CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps (+19 more)

### Community 10 - "AdminDashboard.tsx"
Cohesion: 0.13
Nodes (26): `frontend/src/`, Code, AdminDashboard, ProgressView(), AdminKPIs, AdminRosterRow, GAP_COLORS, HeatmapEntry (+18 more)

### Community 11 - "api.ts"
Cohesion: 0.13
Nodes (25): TokenBridge(), AuthProvider(), mapRole(), useLearnerDashboard(), awardKarmaEvent(), fetchAchievements(), fetchEnrollments(), fetchKarmaLedger() (+17 more)

### Community 12 - "CLAUDE.md"
Cohesion: 0.07
Nodes (21): CLAUDE.md — index & router, Feature index, graphify, How to use these docs, Run commands, Admin Dashboard, Connections, In / out (+13 more)

### Community 13 - "mock-igot-server/main.py"
Cohesion: 0.11
Nodes (26): contextlib, fastapi_middleware_cors, json, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles() (+18 more)

### Community 14 - "karma.py"
Cohesion: 0.11
Nodes (25): Authentication & RBAC, Connections, In / out, TODOs / edge cases, get_current_user(), Session, Decodes the Bearer JWT, looks up the user in auth.db. Raises HTTP 401 for any…, decode_access_token() (+17 more)

### Community 15 - "mock_igot_server.py"
Cohesion: 0.12
Nodes (23): fastapi_responses, field_validator, CompetencyOut, ContentStateRequest, CourseOut, EnrolPayload, get_content_state(), ingest_telemetry() (+15 more)

### Community 16 - "seed_data.py"
Cohesion: 0.14
Nodes (24): faker, hashlib, enrich_course(), main(), FILE: mock-igot-server/enrich_catalog.py…, Returns a deterministic RNG seeded by the course identifier hash., Add quality fields to a course dict (in-place, idempotent)., _seeded_rng() (+16 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "domain.ts"
Cohesion: 0.10
Nodes (20): formatDate(), ProfileHeader(), ProfileHeaderProps, ProgressViewProps, Achievement, BaseUser, Competency, CompetencyProfile (+12 more)

### Community 19 - "_require_auth"
Cohesion: 0.15
Nodes (24): Code, exception_handler, HTTPException, JSONResponse, _competencies(), Return the competencies list from profileDetails.competencies., _course_by_id(), get_competencies() (+16 more)

### Community 20 - "UserAuth"
Cohesion: 0.11
Nodes (22): AuthBase, get_db(), Yields a database session and ensures it is closed after the request., UserAuth, get_me(), get, Return the current authenticated user's profile. Used by the frontend to re-…, get_achievements_by_user_id() (+14 more)

### Community 21 - "recommendation_service.py"
Cohesion: 0.15
Nodes (16): dataclasses, Code, _CourseDoc, GapEntry, HybridRecommendationEngine, BaseModel, FILE: main-lms-backend/services/recommendation_service.py…, Bayesian shrinkage toward global prior mean. Returns None if either input is… (+8 more)

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
Cohesion: 0.14
Nodes (17): is_ollama_available(), Fast, synchronous check — just hits the Ollama /api/tags endpoint. Returns True…, add_documents_from_file(), Ingests a PDF file into the vector store. Returns the number of chunks added.…, ai_health_check(), HealthResponse, BaseModel, get (+9 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "semantic_engine.py"
Cohesion: 0.17
Nodes (15): collections, difflib, get_embedder(), is_embedder_ready(), FILE: ai/embedder.py…, Returns the singleton embedder, loading it on the first call. • Thread-safe for…, Non-blocking check — True only if the singleton is already loaded., classify_intent() (+7 more)

### Community 28 - "main-lms-backend/main.py"
Cohesion: 0.21
Nodes (14): _level_to_int(), main.py — MoSPI LMS Backend API (Main Orchestrator)…, Level 3' → 3, 'Level 2' → 2, fallback → 2, Achievement, AchievementsResponse, Enrollment, EnrollmentsResponse, EvidenceBreakdown (+6 more)

### Community 29 - "vector_store.py"
Cohesion: 0.21
Nodes (14): Code, Embeds all baseline knowledge into ChromaDB., seed(), add_text_to_store(), _get_embeddings(), get_retriever(), get_store(), get_store_stats() (+6 more)

### Community 30 - "os"
Cohesion: 0.19
Nodes (8): dotenv, logging, FILE: ai/rag_engine.py…, FILE: ai/seed_knowledge.py…, scripts/quantize_model.py…, smoke_test.py — End-to-end API test for skill-gaps + recommendations Run from:…, os, sys

### Community 31 - "DashboardCreator"
Cohesion: 0.16
Nodes (4): AdminDashboardCreator, DashboardCreator, OfficialDashboardCreator, TrainerDashboardCreator

### Community 32 - "seed.py"
Cohesion: 0.22
Nodes (12): httpx, _derive_password(), _fetch_officials(), main(), Session, auth/seed.py…, Insert the hardcoded admin user. Returns True if inserted, False if already…, Default password = lowercase(firstName) + last 2 digits of the numeric userId… (+4 more)

### Community 33 - "get"
Cohesion: 0.17
Nodes (13): get_admin_roster(), health(), legacy_catalog(), legacy_frac(), legacy_job_profiles(), legacy_user_history(), get, Merge seed enrolments with any runtime mutations. (+5 more)

### Community 34 - "_OnnxEmbedder"
Cohesion: 0.20
Nodes (9): Code, Connections, In / out, Shared Multilingual Embedder, TODOs / edge cases, _OnnxEmbedder, Lightweight ONNX runtime embedder — no PyTorch needed at inference time.…, Encode sentences into L2-normalised float32 embeddings. API-compatible with… (+1 more)

### Community 35 - "speech.d.ts"
Cohesion: 0.20
Nodes (6): SpeechRecognition, SpeechRecognitionEvent, SpeechRecognitionResult, SpeechRecognitionResultItem, SpeechRecognitionResultList, Window

### Community 36 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 37 - "Ollama RAG Knowledge Base (Tier 3 — disconnected)"
Cohesion: 0.22
Nodes (8): Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, build_system_prompt(), generate_chat_response(), Runs the full RAG pipeline: 1. Retrieve top-k relevant document chunks from…, Builds a rich system prompt that grounds the LLM in the user's live context.…

### Community 38 - "download_model.py"
Cohesion: 0.28
Nodes (7): _download_from_hf(), _download_from_url(), main(), scripts/download_model.py…, Download from HuggingFace Hub using huggingface_hub library., Fallback: download via urllib (no extra deps)., urllib_request

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

### Community 49 - "_startup"
Cohesion: 0.67
Nodes (3): on_event, Create users_auth table and karma tables if they don't exist yet., _startup()

## Knowledge Gaps
- **200 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+195 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 482 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Code` connect `router.py` to `api.ts`, `UserAuth`, `karma.py`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Why does `UserAuth` connect `UserAuth` to `seed.py`, `rag.py`, `router.py`, `main_backup.py`, `karma.py`, `main-lms-backend/main.py`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `Code` connect `Code` to `api.ts`, `karma.py`, `RightSidebar.tsx`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `Code` (e.g. with `KarmaCard()` and `MonthlyCapBar()`) actually correct?**
  _`Code` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `Code` (e.g. with `AssessmentUploadZone()` and `ChatWidget()`) actually correct?**
  _`Code` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving ``frontend/src/`` (e.g. with `AssessmentUploadZone()` and `ChatWidget()`) actually correct?**
  _``frontend/src/`` has 20 INFERRED edges - model-reasoned connections that need verification._