# Graph Report - SIH_IGot  (2026-09-18)

## Corpus Check
- 196 files · ~4,879,677 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .css 1, .example 1)

## Summary
- 1854 nodes · 4007 edges · 107 communities (74 shown, 33 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 443 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e5218726`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ReplyContext
- language_service.py
- models/models.py
- router.py
- package.json
- _require_auth
- rag.py
- ChatWidget.tsx
- ILearningPlatformAdapter
- .fetch_user_cbplan
- AdminDashboard.tsx
- get_enriched_courses
- baseline_assembler.py
- ABC
- AuthContext.tsx
- mock_igot_server.py
- useScreenReader.ts
- What You Must Do When Invoked
- .build_study_plan
- test_pathway.py
- domain.ts
- Session
- chatbot.py
- test_chat_messages.py
- compilerOptions
- os
- 🇮🇳 MoSPI Skill Intelligence Platform
- CourseRecommendation
- test_reply_regression.py
- on_event
- CompetencyCalculator
- LearnerDashboard.tsx
- estimate_uplift
- proficiency_service.py
- database.py
- speech.d.ts
- graphify reference: extra exports and benchmark
- resolve_level
- compilerOptions
- BaselineAssembler
- graphify reference: query, path, explain
- CLAUDE.md
- UserAuth
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- test_mock_data.py
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- Code
- .claude/CLAUDE.md
- extraction-spec.md
- MyCoursesView.tsx
- EvidenceLog
- prerequisite_service.py
- .fetch_frac_competencies
- MockIgotAdapter
- test_irt.py
- api.ts
- ProgressView.tsx
- generate_mock_data.py
- _startup
- App.tsx
- fixture
- Code
- models/domain.py
- faker
- services_chat_messages
- services_chat_messages_context
- date
- Code
- bn.py
- en.py
- gu.py
- hi.py
- hi_latn.py
- mr.py
- or_.py
- ta.py
- te.py
- datetime
- karma.py
- recommendation_service.py
- mock-igot-server/main.py
- Any
- BaseModel
- HybridRecommendationEngine
- FastAPI
- lifespan
- test_chat_endpoint.py
- download_model.py
- RightSidebar.tsx
- Code
- main-lms-backend/main.py
- .fetch_user_enrollments
- diagnostic.py
- .fetch_catalog
- app_state.py
- chat_actions.py

## God Nodes (most connected - your core abstractions)
1. `UserAuth` - 40 edges
2. `react` - 40 edges
3. `HybridRecommendationEngine` - 36 edges
4. `MockIgotAdapter` - 35 edges
5. `Code` - 33 edges
6. `ReplyContext` - 30 edges
7. `_get()` - 30 edges
8. `Code` - 28 edges
9. `Code` - 26 edges
10. `_require_auth()` - 25 edges

## Surprising Connections (you probably didn't know these)
- `1. Runtime topology` --references--> `MockIgotAdapter`  [INFERRED]
  ARCHITECTURE.md → main-lms-backend/adapters/igot_adapter.py
- `Code` --references--> `MonthlyCapBar()`  [INFERRED]
  docs/features/karma-points.md → frontend/src/components/dashboard/RightSidebar.tsx
- `Code` --references--> `PassbookRow()`  [INFERRED]
  docs/features/karma-points.md → frontend/src/components/dashboard/RightSidebar.tsx
- `TODOs / edge cases` --references--> `MockIgotAdapter`  [INFERRED]
  docs/features/recommendation-engine.md → main-lms-backend/adapters/igot_adapter.py
- `Workforce snapshot` --references--> `_build_workforce_snapshot()`  [INFERRED]
  docs/features/workforce-insights.md → main-lms-backend/main.py

## Import Cycles
- None detected.

## Communities (107 total, 33 thin omitted)

### Community 0 - "ReplyContext"
Cohesion: 0.15
Nodes (20): functools, importlib, Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile(), Any, Everything a reply template may personalise, built once per chat request., ReplyContext, _by_page() (+12 more)

### Community 1 - "language_service.py"
Cohesion: 0.25
Nodes (10): detect_chat_language(), detect_chat_variant(), detect_chat_variant_or_none(), _devanagari_language(), Small, offline language routing for Gyan chat. This deliberately does *not* use…, Supported ISO 639-1 code for a chat message., The variant the *text itself* signals, or None when it carries no signal. Plain…, Internal language variant: en, hi (Devanagari), hi_latn (romanized Hindi), mr,… (+2 more)

### Community 2 - "models/models.py"
Cohesion: 0.05
Nodes (59): 7. Mismatches between the mermaid diagram and the code, Base, Conventions, Code, In / out, Karma Points (gamification), TODOs / edge cases, enum (+51 more)

### Community 3 - "router.py"
Cohesion: 0.09
Nodes (44): bcrypt, Code, jose, get_db(), Yields a database session and ensures it is closed after the request., change_password(), _clear_refresh_cookie(), login() (+36 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (43): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+35 more)

### Community 5 - "_require_auth"
Cohesion: 0.14
Nodes (34): JSONResponse, get_admin_roster(), get_assessment_outcomes(), get_competencies(), get_course_catalog(), get_crosswalk(), get_gsbpm_map(), get_hrms_officials() (+26 more)

### Community 6 - "rag.py"
Cohesion: 0.10
Nodes (22): asyncio, datetime, FastAPI, google_generativeai, httpx, json, langchain_text_splitters, adapters/igot_adapter.py — iGOT Platform Adapter… (+14 more)

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.08
Nodes (44): Code, GyanBot(), GyanHero(), LanguageMenu(), LanguageMenuProps, CAPABILITIES, ChatWidget(), ChatWidgetProps (+36 more)

### Community 8 - "ILearningPlatformAdapter"
Cohesion: 0.11
Nodes (15): ABC, 1. Runtime topology, 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator (+7 more)

### Community 9 - ".fetch_user_cbplan"
Cohesion: 0.40
Nodes (4): AI Course Recommendation Engine + Learning Pathways, In / out, TODOs / edge cases, GET /api/cbplan/v1/user/{id} — ACBP mandatory courses + learning hours/quarter.…

### Community 10 - "AdminDashboard.tsx"
Cohesion: 0.10
Nodes (34): `frontend/src/`, Admin Dashboard, Code, Connections, In / out, TODOs / edge cases, WorkforceInsights(), ProgressView() (+26 more)

### Community 11 - "get_enriched_courses"
Cohesion: 0.33
Nodes (7): composite_search(), _course_tags(), _enriched_view(), get_enriched_courses(), _matches_filters(), Sunbird-style filters: each key → value or list of accepted values., The catalogue in the older "enriched" shape. Query params:…

### Community 12 - "baseline_assembler.py"
Cohesion: 0.15
Nodes (25): Code, rows_for(), tag_id(), _education_score(), enrollment_course_id(), is_completed(), _last_evidence_date(), _map_category() (+17 more)

### Community 14 - "AuthContext.tsx"
Cohesion: 0.16
Nodes (17): ProtectedRoute(), ProtectedRouteProps, AuthContext, AuthContextType, AuthProvider(), AuthUser, mapRole(), UserRole (+9 more)

### Community 15 - "mock_igot_server.py"
Cohesion: 0.11
Nodes (23): exception_handler, fastapi_responses, HTTPException, EnrolPayload, health(), http_exc_handler(), ingest_telemetry(), legacy_catalog() (+15 more)

### Community 16 - "useScreenReader.ts"
Cohesion: 0.53
Nodes (5): chunkText(), extractReadableText(), isHidden(), ScreenReader, useScreenReader()

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - ".build_study_plan"
Cohesion: 0.11
Nodes (16): Cross-competency prerequisite DAG (SCIL v6 §5, B4), _diagnostic_step(), absorb(), add_step(), advance(), open_ladders(), _parse_level(), _PrerequisiteGate (+8 more)

### Community 19 - "test_pathway.py"
Cohesion: 0.08
Nodes (23): hashlib, _edge(), _gap(), _kinds_levels(), Skill-gap levels + level-aware recommendations + learning pathways. Runs on a…, _resolved(), test_already_met_prerequisite_changes_nothing(), test_beginner_gets_next_levels_in_order_never_advanced_or_basic() (+15 more)

### Community 20 - "domain.ts"
Cohesion: 0.06
Nodes (34): DEFER_REASON, KIND_STYLE, PathwayLadder(), ProfileHeaderProps, AppliedPrerequisite, BaseUser, ColdStartPrior, Competency (+26 more)

### Community 22 - "chatbot.py"
Cohesion: 0.23
Nodes (20): chat(), ChatRequest, ChatResponse, detect_intent_keyword(), _intent_response(), _intercept(), post, FILE: routers/chatbot.py Multilingual AI Learning Assistant — Gyan (ज्ञान)… (+12 more)

### Community 23 - "test_chat_messages.py"
Cohesion: 0.20
Nodes (14): Localized reply for `intent`; unknown intents get the page's fallback reply., Loads a language's template table on first use ("or" lives in or_.py; `or` is a…, render(), templates(), _alternatives(), _fields(), parametrize, Catalogue completeness: every language has every template, placeholders are… (+6 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "os"
Cohesion: 0.06
Nodes (44): Code, Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, dotenv, logging, build_system_prompt() (+36 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "CourseRecommendation"
Cohesion: 0.26
Nodes (9): CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps, SOURCE_STYLES, matches(), Props, RecommendationsPanel() (+1 more)

### Community 28 - "test_reply_regression.py"
Cohesion: 0.27
Nodes (9): ChatHistoryItem, BaseModel, RecommendationContext, SkillGapContext, sample_request(), parametrize, English and Hinglish replies must match the pre-catalogue output, except…, test_endpoint_reply_unchanged() (+1 more)

### Community 30 - "CompetencyCalculator"
Cohesion: 0.22
Nodes (8): CompetencyCalculator, datetime, FILE: main-lms-backend/services/competency_service.py…, Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, Maps FRAC types from the JSON to calculation categories., test_missing_channels_do_not_drag_the_score_to_zero(), math

### Community 31 - "LearnerDashboard.tsx"
Cohesion: 0.09
Nodes (39): Visual design system (shared by every page), AssessmentUploadZone(), AssessmentUploadZoneProps, formatDate(), ProfileHeader(), AshokaChakra(), CountUp(), GovEmblem() (+31 more)

### Community 32 - "estimate_uplift"
Cohesion: 0.09
Nodes (32): opportunity(), Any, services/gsbpm_service.py — GSBPM scoping (SCIL v6 §1) + opportunity to…, Opportunity to practise a competency in the official's office this cycle (SCIL…, Which competencies are in scope under the officer-hours rule, and why., scope_report(), _sp_name(), subprocess_hours() (+24 more)

### Community 33 - "proficiency_service.py"
Cohesion: 0.07
Nodes (53): Cold start for UNASSESSED competencies, Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8), Foresight, Proficiency belief with dated decay, Workforce snapshot, cluster_of(), cohort_prior(), decay() (+45 more)

### Community 34 - "database.py"
Cohesion: 0.15
Nodes (15): auth/database.py…, auth/models.py…, _derive_password(), _fetch_officials(), main(), auth/seed.py…, Insert the hardcoded admin user. Returns True if inserted, False if already…, Default password = lowercase(firstName) + last 2 digits of the numeric userId… (+7 more)

### Community 35 - "speech.d.ts"
Cohesion: 0.20
Nodes (6): SpeechRecognition, SpeechRecognitionEvent, SpeechRecognitionResult, SpeechRecognitionResultItem, SpeechRecognitionResultList, Window

### Community 36 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 37 - "resolve_level"
Cohesion: 0.28
Nodes (15): Single source of truth for an official's level on one competency. Every…, resolve_level(), _assess(), SCIL v6 §3 evidence channels K/A/U/S (knowledge, application, utility,…, _row(), test_confirmed_use_is_a_floor_unconfirmed_is_not(), test_failed_work_sample_is_evidence_but_not_a_floor(), test_knowledge_only_score_is_unchanged() (+7 more)

### Community 39 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 40 - "BaselineAssembler"
Cohesion: 0.20
Nodes (8): Connections, BaselineAssembler, _normalise_course_map(), Accept {courseId: {compId: level}} or the legacy {courseId: [compId]}., {courseId: {compId: FRAC level}} — feeds BaselineAssembler so the Verified…, The old `requiredLevel - 1` cap made every evidence-backed gap permanent., test_completion_evidence_follows_the_crosswalk(), test_evidence_can_close_a_gap()

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 42 - "CLAUDE.md"
Cohesion: 0.10
Nodes (17): CLAUDE.md — index & router, Feature index, graphify, How to use these docs, Run commands, Authentication & RBAC, In / out, Shared database (Neon) (+9 more)

### Community 43 - "UserAuth"
Cohesion: 0.07
Nodes (52): AuthBase, Returns a FastAPI dependency that checks the current user's role. Example:…, require_role(), UserAuth, get_me(), Return the current authenticated user's profile. Used by the frontend to re-…, get_achievements(), get_achievements_by_user_id() (+44 more)

### Community 44 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 45 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 46 - "test_mock_data.py"
Cohesion: 0.07
Nodes (16): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only, fixture, data(), files(), Mock-data generator (mock-igot-server/generate_mock_data.py): determinism, one…, _tags() (+8 more)

### Community 49 - "Code"
Cohesion: 0.10
Nodes (30): Code, StudioTab, _chunk_document_text(), _clean_text(), _detect_skill_name(), DocumentMetadata, DocumentUploadResponse, ErrorResponse (+22 more)

### Community 58 - "MyCoursesView.tsx"
Cohesion: 0.22
Nodes (7): COLORS, LearningSnapshot(), Props, MyCoursesView(), MyCoursesViewProps, Enrollment, recharts

### Community 60 - "EvidenceLog"
Cohesion: 0.12
Nodes (15): Certificate / Resume Evidence Extraction, Connections, In / out, TODOs / edge cases, Connections, In / out, Skill Gap Analysis (evidence-based competency baselines), TODOs / edge cases (+7 more)

### Community 61 - "prerequisite_service.py"
Cohesion: 0.14
Nodes (24): find_cycle(), infer_edges(), _node(), _norm_sf(), _ols(), Any, ndarray, services/prerequisite_service.py — cross-competency prerequisite DAG (SCIL v6… (+16 more)

### Community 62 - ".fetch_frac_competencies"
Cohesion: 0.18
Nodes (10): Noticed but out of scope (not fixed), GET /api/frac/competencies — the catalogue FRAC set incl. L1–L5 descriptors., calculate_baseline(), EvidencePayload, BaseModel, post, UploadFile, Calculates the skill baseline score b_k ∈ [0, 5] using the locked 6-term… (+2 more)

### Community 63 - "MockIgotAdapter"
Cohesion: 0.16
Nodes (10): GSBPM scope — the 80% officer-hours rule (SCIL v6 §1), MockIgotAdapter, GET a Sunbird endpoint and return its `result` object., GET /api/gsbpm/v1/map — GSBPM sub-processes + competency → sub-processes., GET /api/org/v1/offices — {cycle, offices[{officeId, subprocesses[{id,…, GET /api/frac/v1/prerequisites — {count, edges[]} expert-seeded prerequisite…, GET /api/course/v1/assessment/outcomes — {outcomes[], comparisons[]} pre/post θ…, GET /api/assessment/v1/itembank — 2PL items incl. answer keys (server side… (+2 more)

### Community 64 - "test_irt.py"
Cohesion: 0.13
Nodes (23): DiagnosticSessions, fisher_information(), laplace_posterior(), next_item(), p_correct(), public_item(), Any, services/irt_service.py — Tier-1 Bayesian 2PL posterior + adaptive diagnostic… (+15 more)

### Community 65 - "api.ts"
Cohesion: 0.09
Nodes (40): AGENDA_TYPE, CapabilityRiskPanel(), ForesightPanel(), GsbpmScopePanel(), pct(), PrerequisitePanel(), PRIORITY_CHIP, RISK_CHIP (+32 more)

### Community 66 - "ProgressView.tsx"
Cohesion: 0.31
Nodes (5): ProgressViewProps, Props, RecentActivityList(), relative(), Achievement

### Community 67 - "generate_mock_data.py"
Cohesion: 0.08
Nodes (57): date, _batch(), build_acbp(), build_catalog(), build_crosswalk(), build_enrollments(), build_frac(), build_gsbpm_map() (+49 more)

### Community 68 - "_startup"
Cohesion: 0.12
Nodes (20): Measured uplift → coverage learning + training effectiveness (SCIL v6 §6, B5), Reference data loading, TODOs / limits, Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight), on_event, Create users_auth table if it doesn't exist yet., _startup(), Create users_auth table and karma tables if they don't exist yet. (+12 more)

### Community 69 - "App.tsx"
Cohesion: 0.07
Nodes (21): AdminDashboard, App(), AssessmentPage, DashboardRedirect(), LearnerDashboard, TokenBridge(), Theme, ThemeContext (+13 more)

### Community 71 - "Code"
Cohesion: 0.11
Nodes (26): Code, Opportunity to practise (SCIL v6 §4), CompetencyOverviewTable(), LevelPips(), priorityOf(), Props, StudyPlanSummary(), CHANNEL_LABEL (+18 more)

### Community 72 - "models/domain.py"
Cohesion: 0.29
Nodes (11): Achievement, AchievementsResponse, Enrollment, EnrollmentsResponse, EvidenceBreakdown, BaseModel, Per-channel evidence values after decay/discount, as used in the fusion formula., Recommendation (+3 more)

### Community 77 - "Code"
Cohesion: 0.28
Nodes (6): Code, CertificateUploadZone(), CertificateExtractionResult, DocumentExtractorService, ExtractedCompetency, BaseModel

### Community 88 - "karma.py"
Cohesion: 0.12
Nodes (23): Connections, fastapi_security, get_current_user(), Session, auth/dependencies.py…, Decodes the Bearer JWT, looks up the user in auth.db. Raises HTTP 401 for any…, decode_access_token(), Decode and validate a JWT. Raises ValueError with a human-readable message on… (+15 more)

### Community 89 - "recommendation_service.py"
Cohesion: 0.05
Nodes (51): argparse, collections, dataclasses, difflib, Code, Connections, In / out, Shared Multilingual Embedder (+43 more)

### Community 90 - "mock-igot-server/main.py"
Cohesion: 0.11
Nodes (23): contextlib, fastapi_middleware_cors, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history() (+15 more)

### Community 91 - "Any"
Cohesion: 0.19
Nodes (8): Any, GET /api/evidence/v1/user/{id} — EvidenceLog-style workplace evidence rows ([]…, GET /api/frac/v1/crosswalk — iGOT dictionary CID id → catalogue FRAC id., GET /api/user/v2/read/{user_id} Returns: result.response — single user object…, GET /api/admin/v1/users Returns: result.users — full list of officials., Safely drill into a Sunbird envelope: data['result']['key1']['key2']..., Return the full CBP course catalog., _sunbird_result()

### Community 92 - "BaseModel"
Cohesion: 0.16
Nodes (11): field_validator, CompetencyOut, CompositeSearchRequest, ContentStateRequest, CourseOut, JobProfileOut, BaseModel, Mirrors the authentic courses.json schema. (+3 more)

### Community 93 - "HybridRecommendationEngine"
Cohesion: 0.09
Nodes (27): Code, _course_summary(), _CourseDoc, _fmt_levels(), GapEntry, HybridRecommendationEngine, _interleave_by_level(), BaseModel (+19 more)

### Community 95 - "lifespan"
Cohesion: 0.40
Nodes (6): lifespan(), _load_json(), _load_json_from_dir(), Any, Load all datasets into memory once at startup, so no request touches the file…, Load a JSON file from ROOT_DIR. Raises RuntimeError on missing file.

### Community 96 - "test_chat_endpoint.py"
Cohesion: 0.42
Nodes (8): fastapi_testclient, _chat(), parametrize, End-to-end /chat behaviour per language through the real multilingual…, test_dark_mode_action(), test_my_courses_navigation(), test_recommendations(), test_skill_gaps()

### Community 97 - "download_model.py"
Cohesion: 0.28
Nodes (7): _download_from_hf(), _download_from_url(), main(), scripts/download_model.py…, Download from HuggingFace Hub using huggingface_hub library., Fallback: download via urllib (no extra deps)., urllib_request

### Community 99 - "RightSidebar.tsx"
Cohesion: 0.11
Nodes (19): Connections, In / out, Learner Dashboard (frontend shell), TODOs / edge cases, CareerCard(), EVENT_META, KarmaCard(), milestones (+11 more)

### Community 101 - "Code"
Cohesion: 0.13
Nodes (18): Code, Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server + mock data), TODOs / edge cases, _competencies(), _prof_detail(), Safely read a field from profileDetails.professionalDetails[0]. (+10 more)

### Community 104 - "main-lms-backend/main.py"
Cohesion: 0.11
Nodes (31): 3. Core data flow, _build_workforce_snapshot(), _ensure_can_view(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments_by_user_id(), get_frac_competencies(), get_learning_pathway() (+23 more)

### Community 105 - ".fetch_user_enrollments"
Cohesion: 0.40
Nodes (3): Connections, GET /api/course/v1/user/enrollment/list/{user_id} Returns: result.courses —…, Legacy method that maps fetch_user_enrollments to the old simple-mock shape.…

### Community 106 - "diagnostic.py"
Cohesion: 0.22
Nodes (15): Competency, answer(), AnswerBody, BaseModel, get, post, UserAuth, routers/diagnostic.py — adaptive "check your level" diagnostic (SCIL v6 §2,… (+7 more)

### Community 112 - "app_state.py"
Cohesion: 0.29
Nodes (5): services/app_state.py — process-wide singletons built in main._startup. Routers…, Any, Plain holder; every attribute defaults to empty so features degrade, not crash., _read_disk(), ReferenceData

### Community 119 - "chat_actions.py"
Cohesion: 0.50
Nodes (4): detect_ui_actions(), _mentions(), Detect website theme / language changes requested in any supported chat…, Returns (theme, language): theme in {"dark", "light", "toggle"}, language in…

## Knowledge Gaps
- **240 isolated node(s):** ``mock-igot-server/` — external-system simulator`, `4. Persistence`, `5. Tech stack`, `How to use these docs`, `Feature index` (+235 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 728 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Code` connect `ChatWidget.tsx` to `language_service.py`, `_startup`, `CLAUDE.md`, `chatbot.py`, `recommendation_service.py`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `Code` connect `HybridRecommendationEngine` to `estimate_uplift`, `api.ts`, `_startup`, `Code`, `main-lms-backend/main.py`, `.fetch_user_cbplan`, `BaselineAssembler`, `.build_study_plan`, `domain.ts`, `MockIgotAdapter`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Why does `Code` connect `router.py` to `api.ts`, `_startup`, `App.tsx`, `CLAUDE.md`, `UserAuth`, `AuthContext.tsx`, `karma.py`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `HybridRecommendationEngine` (e.g. with `7. Mismatches between the mermaid diagram and the code` and `Code`) actually correct?**
  _`HybridRecommendationEngine` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `MockIgotAdapter` (e.g. with `1. Runtime topology` and `6. Design patterns actually implemented`) actually correct?**
  _`MockIgotAdapter` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `Code` (e.g. with `AssessmentUploadZone()` and `ChatWidget()`) actually correct?**
  _`Code` has 32 INFERRED edges - model-reasoned connections that need verification._