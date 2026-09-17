# Graph Report - SIH_IGot  (2026-09-18)

## Corpus Check
- 168 files · ~4,815,820 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .css 1, .example 1)

## Summary
- 1289 nodes · 2698 edges · 82 communities (59 shown, 23 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 320 edges (avg confidence: 0.95)
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
- main_backup.py
- mock-igot-server/main.py
- _assert_self_or_admin
- _require_auth
- seed_data.py
- What You Must Do When Invoked
- domain.ts
- lifespan
- mock_igot_server.py
- Code
- chatbot.py
- test_chat_messages.py
- compilerOptions
- ai_tools.py
- 🇮🇳 MoSPI Skill Intelligence Platform
- os
- test_reply_regression.py
- get_embedder
- main-lms-backend/main.py
- download_model.py
- semantic_engine.py
- MockIgotAdapter
- CompetencyCalculator
- speech.d.ts
- graphify reference: extra exports and benchmark
- enrich_catalog.py
- CourseRecommendation
- compilerOptions
- BaselineAssembler
- graphify reference: query, path, explain
- CLAUDE.md
- Authentication & RBAC
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- rag.py
- .claude/CLAUDE.md
- extraction-spec.md
- lucide-react
- language_service.py
- eval_intents.py
- karma.py
- api.ts
- test_chat_endpoint.py
- ingest_telemetry
- CLAUDE.md — index & router
- Mock iGOT Karmayogi Integration (Adapter + mock server)
- RAG Document → Quiz Generator & Grading
- typing
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
2. `react` - 38 edges
3. `ReplyContext` - 30 edges
4. `Code` - 30 edges
5. `Code` - 24 edges
6. `lucide-react` - 22 edges
7. ``frontend/src/`` - 21 edges
8. `MockIgotAdapter` - 20 edges
9. `Code` - 19 edges
10. `Code` - 19 edges

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

## Communities (82 total, 23 thin omitted)

### Community 0 - "ReplyContext"
Cohesion: 0.19
Nodes (18): functools, importlib, Any, Everything a reply template may personalise, built once per chat request., ReplyContext, _by_page(), _gap_lines(), _greeting() (+10 more)

### Community 1 - "Code"
Cohesion: 0.08
Nodes (35): dataclasses, Code, In / out, Karma Points (gamification), TODOs / edge cases, KarmaEvent, KarmaEventType, KarmaMonthlyUsage (+27 more)

### Community 2 - "Code"
Cohesion: 0.23
Nodes (11): Code, _education_score(), _map_category(), Any, datetime, services/baseline_assembler.py Evidence Assembly Layer — gathers 6 evidence…, FIX (Bug #2): STRICTLY comp-id-tag-matched. Stage 2 general engagement fallback…, _tenure_score() (+3 more)

### Community 3 - "router.py"
Cohesion: 0.06
Nodes (63): bcrypt, Code, fastapi_security, TokenBridge(), awardKarmaEvent(), lmsFetch(), registerLogoutCallback(), setApiToken() (+55 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (43): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+35 more)

### Community 5 - "ILearningPlatformAdapter"
Cohesion: 0.05
Nodes (33): 1. Runtime topology, 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator (+25 more)

### Community 6 - "UserAuth"
Cohesion: 0.11
Nodes (25): AuthBase, UserAuth, get_achievements(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments(), get_enrollments_by_user_id(), get_profile_by_user_id() (+17 more)

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.08
Nodes (46): `frontend/src/`, GyanBot(), GyanHero(), LanguageMenu(), LanguageMenuProps, CAPABILITIES, ChatWidget(), MessageBubble() (+38 more)

### Community 8 - "react"
Cohesion: 0.09
Nodes (34): App(), AssessmentPage, DashboardRedirect(), ProtectedRoute(), ProtectedRouteProps, AppShell(), AppShellProps, ShellNavGroup (+26 more)

### Community 9 - "LearnerDashboard.tsx"
Cohesion: 0.09
Nodes (28): Code, LearnerDashboard, AssessmentUploadZone(), AssessmentUploadZoneProps, CompetencyOverviewTable(), LevelPips(), priorityOf(), Props (+20 more)

### Community 10 - "AdminDashboard.tsx"
Cohesion: 0.08
Nodes (28): Code, AdminDashboard, AdminKPIs, AdminRosterRow, GAP_COLORS, HeatmapEntry, levelToNumber(), useAdminData() (+20 more)

### Community 11 - "authApi.ts"
Cohesion: 0.29
Nodes (10): AuthProvider(), mapRole(), extractError(), getMe(), login(), LoginResponse, logout(), refresh() (+2 more)

### Community 12 - "main_backup.py"
Cohesion: 0.21
Nodes (15): on_event, main.py — MoSPI LMS Backend API (Main Orchestrator)…, Create users_auth table if it doesn't exist yet., _startup(), Achievement, AchievementsResponse, Enrollment, EnrollmentsResponse (+7 more)

### Community 13 - "mock-igot-server/main.py"
Cohesion: 0.12
Nodes (24): contextlib, fastapi_middleware_cors, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history() (+16 more)

### Community 14 - "_assert_self_or_admin"
Cohesion: 0.16
Nodes (16): Connections, _assert_self_or_admin(), award_karma_event(), CbpClaimRequest, claim_cbp_bonus(), get_karma_ledger(), KarmaEventRequest, BaseModel (+8 more)

### Community 15 - "_require_auth"
Cohesion: 0.16
Nodes (26): Code, JSONResponse, _competencies(), Return the competencies list from profileDetails.competencies., _course_by_id(), get_admin_roster(), get_competencies(), get_course_catalog() (+18 more)

### Community 16 - "seed_data.py"
Cohesion: 0.25
Nodes (16): faker, batch_id(), build_content_states(), build_course_catalog(), build_enrollments(), build_frac_competencies(), build_users(), do_id() (+8 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "domain.ts"
Cohesion: 0.08
Nodes (26): COLORS, LearningSnapshot(), Props, MyCoursesView(), MyCoursesViewProps, ProfileHeaderProps, ProgressViewProps, Props (+18 more)

### Community 19 - "lifespan"
Cohesion: 0.33
Nodes (7): lifespan(), _load_json(), _load_json_from_dir(), Any, FastAPI, Load all datasets into memory once at startup. courses.json is large (~27 MB /…, Load a JSON file from ROOT_DIR. Raises RuntimeError on missing file.

### Community 20 - "mock_igot_server.py"
Cohesion: 0.09
Nodes (29): exception_handler, fastapi_responses, HTTPException, CompetencyOut, ContentStateRequest, CourseOut, EnrolPayload, get_content_state() (+21 more)

### Community 21 - "Code"
Cohesion: 0.18
Nodes (13): Code, _CourseDoc, GapEntry, HybridRecommendationEngine, BaseModel, Bayesian shrinkage toward global prior mean. Returns None if either input is…, Singleton — built ONCE at app startup. Holds FAISS index + BM25 corpus in…, Computes and prioritizes skill gaps. priority_k = gap_k * (target_k / 5.0)… (+5 more)

### Community 22 - "chatbot.py"
Cohesion: 0.30
Nodes (16): ChatResponse, _intent_response(), _intercept(), FILE: routers/chatbot.py Multilingual AI Learning Assistant — Gyan (ज्ञान)…, Deterministic handling of English commands the classifier has historically…, _response(), _theme_action(), _ui_action_response() (+8 more)

### Community 23 - "test_chat_messages.py"
Cohesion: 0.21
Nodes (12): Loads a language's template table on first use ("or" lives in or_.py; `or` is a…, templates(), _alternatives(), _fields(), parametrize, Catalogue completeness: every language has every template, placeholders are…, test_every_intent_renders(), test_placeholders_match_english() (+4 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "ai_tools.py"
Cohesion: 0.06
Nodes (45): asyncio, Code, Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, dotenv, io (+37 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "os"
Cohesion: 0.18
Nodes (10): json, logging, FILE: ai/embedder.py…, scripts/quantize_model.py…, FILE: main-lms-backend/services/recommendation_service.py…, smoke_test.py — End-to-end API test for skill-gaps + recommendations Run from:…, numpy, os (+2 more)

### Community 28 - "test_reply_regression.py"
Cohesion: 0.20
Nodes (15): chat(), ChatHistoryItem, ChatRequest, detect_intent_keyword(), BaseModel, post, Multilingual AI Learning Assistant — Gyan (ज्ञान)., RecommendationContext (+7 more)

### Community 29 - "get_embedder"
Cohesion: 0.14
Nodes (12): Connections, In / out, Shared Multilingual Embedder, TODOs / edge cases, _Embedder, get_embedder(), _load(), _OnnxEmbedder (+4 more)

### Community 30 - "main-lms-backend/main.py"
Cohesion: 0.11
Nodes (20): Returns a FastAPI dependency that checks the current user's role. Example:…, require_role(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments_by_user_id(), get_frac_competencies(), get_profile_by_user_id(), get_recommendations_by_user_id() (+12 more)

### Community 31 - "download_model.py"
Cohesion: 0.28
Nodes (7): _download_from_hf(), _download_from_url(), main(), scripts/download_model.py…, Download from HuggingFace Hub using huggingface_hub library., Fallback: download via urllib (no extra deps)., urllib_request

### Community 32 - "semantic_engine.py"
Cohesion: 0.11
Nodes (25): difflib, Code, Code, is_embedder_ready(), model_name(), Non-blocking check — True only if the role's model is already loaded., classify_intent(), _correct_tokens() (+17 more)

### Community 33 - "MockIgotAdapter"
Cohesion: 0.14
Nodes (14): httpx, MockIgotAdapter, adapters/igot_adapter.py — iGOT Platform Adapter…, Calls the Sunbird-compliant mock iGOT server (mock_igot_server.py) on port 8001…, calculate_baseline(), EvidencePayload, BaseModel, post (+6 more)

### Community 34 - "CompetencyCalculator"
Cohesion: 0.33
Nodes (5): CompetencyCalculator, datetime, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, Maps FRAC types from the JSON to calculation categories., Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…

### Community 35 - "speech.d.ts"
Cohesion: 0.20
Nodes (6): SpeechRecognition, SpeechRecognitionEvent, SpeechRecognitionResult, SpeechRecognitionResultItem, SpeechRecognitionResultList, Window

### Community 36 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 37 - "enrich_catalog.py"
Cohesion: 0.36
Nodes (7): enrich_course(), main(), FILE: mock-igot-server/enrich_catalog.py…, Returns a deterministic RNG seeded by the course identifier hash., Add quality fields to a course dict (in-place, idempotent)., _seeded_rng(), Random

### Community 38 - "CourseRecommendation"
Cohesion: 0.23
Nodes (10): ChatWidgetProps, CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps, SOURCE_STYLES, matches(), Props (+2 more)

### Community 39 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 40 - "BaselineAssembler"
Cohesion: 0.29
Nodes (5): AI Course Recommendation Engine, Connections, In / out, TODOs / edge cases, BaselineAssembler

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 42 - "CLAUDE.md"
Cohesion: 0.18
Nodes (8): Admin Dashboard, Connections, In / out, TODOs / edge cases, Connections, Gyan — Multilingual Chat Assistant, In / out, TODOs / edge cases

### Community 43 - "Authentication & RBAC"
Cohesion: 0.50
Nodes (3): Authentication & RBAC, In / out, TODOs / edge cases

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
Nodes (73): 3. Core data flow, 7. Mismatches between the mermaid diagram and the code, Base, Conventions, datetime, Certificate / Resume Evidence Extraction, Connections, In / out (+65 more)

### Community 61 - "lucide-react"
Cohesion: 0.18
Nodes (17): Visual design system (shared by every page), formatDate(), ProfileHeader(), AshokaChakra(), CountUp(), GovEmblem(), Reveal(), useInView() (+9 more)

### Community 62 - "language_service.py"
Cohesion: 0.28
Nodes (8): detect_chat_language(), detect_chat_variant_or_none(), _devanagari_language(), Small, offline language routing for Gyan chat. This deliberately does *not* use…, Supported ISO 639-1 code for a chat message., The variant the *text itself* signals, or None when it carries no signal. Plain…, Pick the reply variant for a message, honouring the UI language picker. A…, resolve_chat_variant()

### Community 63 - "eval_intents.py"
Cohesion: 0.28
Nodes (7): argparse, collections, load_eval(), main(), Benchmark Gyan's intent classifier on the held-out multilingual set. python…, detect_chat_variant(), Internal language variant: en, hi (Devanagari), hi_latn (romanized Hindi), mr,…

### Community 64 - "karma.py"
Cohesion: 0.18
Nodes (14): fastapi, get_db(), auth/database.py…, Yields a database session and ensures it is closed after the request., get_current_user(), Session, auth/dependencies.py…, Decodes the Bearer JWT, looks up the user in auth.db. Raises HTTP 401 for any… (+6 more)

### Community 65 - "api.ts"
Cohesion: 0.09
Nodes (32): Connections, In / out, Learner Dashboard (frontend shell), TODOs / edge cases, CareerCard(), EVENT_META, KarmaCard(), milestones (+24 more)

### Community 66 - "test_chat_endpoint.py"
Cohesion: 0.42
Nodes (8): fastapi_testclient, _chat(), parametrize, End-to-end /chat behaviour per language through the real multilingual…, test_dark_mode_action(), test_my_courses_navigation(), test_recommendations(), test_skill_gaps()

### Community 70 - "ingest_telemetry"
Cohesion: 0.33
Nodes (5): field_validator, ingest_telemetry(), Returns a list of validation errors for a single telemetry event., TelemetryBatch, _validate_event()

### Community 71 - "CLAUDE.md — index & router"
Cohesion: 0.40
Nodes (5): CLAUDE.md — index & router, Feature index, graphify, How to use these docs, Run commands

### Community 73 - "Mock iGOT Karmayogi Integration (Adapter + mock server)"
Cohesion: 0.40
Nodes (4): Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server), TODOs / edge cases

### Community 74 - "RAG Document → Quiz Generator & Grading"
Cohesion: 0.40
Nodes (4): Connections, In / out, RAG Document → Quiz Generator & Grading, TODOs / edge cases

### Community 75 - "typing"
Cohesion: 0.22
Nodes (7): Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile(), detect_ui_actions(), _mentions(), Detect website theme / language changes requested in any supported chat…, Returns (theme, language): theme in {"dark", "light", "toggle"}, language in…, typing

## Knowledge Gaps
- **215 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+210 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 536 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Code` connect `semantic_engine.py` to `ChatWidget.tsx`, `CLAUDE.md`, `chatbot.py`, `test_reply_regression.py`, `language_service.py`, `eval_intents.py`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Why does `UserAuth` connect `UserAuth` to `karma.py`, `router.py`, `main_backup.py`, `_assert_self_or_admin`, `rag.py`, `main-lms-backend/main.py`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `Code` connect `router.py` to `authApi.ts`, `karma.py`, `Authentication & RBAC`, `UserAuth`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `ReplyContext` (e.g. with `chat()` and `_intent_response()`) actually correct?**
  _`ReplyContext` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `Code` (e.g. with `AssessmentUploadZone()` and `ChatWidget()`) actually correct?**
  _`Code` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `Code` (e.g. with `KarmaCard()` and `MonthlyCapBar()`) actually correct?**
  _`Code` has 23 INFERRED edges - model-reasoned connections that need verification._