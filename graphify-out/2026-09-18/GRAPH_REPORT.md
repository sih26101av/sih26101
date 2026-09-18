# Graph Report - SIH_IGot  (2026-09-18)

## Corpus Check
- 193 files · ~4,876,371 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .css 1, .example 1)

## Summary
- 1801 nodes · 3872 edges · 114 communities (83 shown, 31 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 427 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8d152102`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ReplyContext
- language_service.py
- Code
- Code
- package.json
- _get
- rag.py
- ChatWidget.tsx
- Any
- Code
- Code
- models/models.py
- baseline_assembler.py
- api.ts
- authApi.ts
- mock_igot_server.py
- lucide-react
- What You Must Do When Invoked
- .build_study_plan
- test_pathway.py
- domain.ts
- .__init__
- chatbot.py
- test_chat_messages.py
- compilerOptions
- os
- 🇮🇳 MoSPI Skill Intelligence Platform
- CourseCard.tsx
- test_reply_regression.py
- semantic_engine.py
- CompetencyCalculator
- react
- mock_data_metrics.py
- proficiency_service.py
- seed.py
- speech.d.ts
- graphify reference: extra exports and benchmark
- resolve_level
- post
- compilerOptions
- BaselineAssembler
- graphify reference: query, path, explain
- CLAUDE.md
- main_backup.py
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- test_mock_data.py
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- Code
- .claude/CLAUDE.md
- extraction-spec.md
- LearnerDashboard.tsx
- SCIL v6 — mock data + blocked features: progress report
- prerequisite_service.py
- .fetch_frac_competencies
- MockIgotAdapter
- Authentication & RBAC
- WorkforceInsights.tsx
- AdminDashboard.tsx
- generate_mock_data.py
- 3. Core data flow
- DashboardCreator
- Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)
- Code
- main-lms-backend/main.py
- faker
- services_chat_messages
- services_chat_messages_context
- Any
- document_extractor.py
- bn.py
- en.py
- gu.py
- hi.py
- hi_latn.py
- mr.py
- or_.py
- ta.py
- te.py
- EvidenceLog
- _assert_self_or_admin
- QuizAttempt
- mock-igot-server/main.py
- _sunbird_result
- ingest_telemetry
- HybridRecommendationEngine
- engine
- lifespan
- test_chat_endpoint.py
- download_model.py
- _PrerequisiteGate
- RecentActivityList.tsx
- grade_quiz
- Code
- _user_enrolments
- Gyan — Multilingual Chat Assistant
- _learner_competency_state
- .fetch_user_enrollments
- RAG Document → Quiz Generator & Grading
- .fetch_catalog
- on_event
- BaseModel
- ndarray
- fixture

## God Nodes (most connected - your core abstractions)
1. `_get()` - 44 edges
2. `react` - 40 edges
3. `HybridRecommendationEngine` - 37 edges
4. `UserAuth` - 34 edges
5. `MockIgotAdapter` - 33 edges
6. `Code` - 33 edges
7. `ReplyContext` - 30 edges
8. `Code` - 28 edges
9. `Code` - 26 edges
10. `_require_auth()` - 24 edges

## Surprising Connections (you probably didn't know these)
- `1. Runtime topology` --references--> `MockIgotAdapter`  [INFERRED]
  ARCHITECTURE.md → main-lms-backend/adapters/igot_adapter.py
- `7. Mismatches between the mermaid diagram and the code` --references--> `SkillGapReport`  [INFERRED]
  ARCHITECTURE.md → frontend/src/types/domain.ts
- `TODOs / edge cases` --references--> `_require_auth()`  [INFERRED]
  docs/features/mock-igot-integration.md → mock-igot-server/mock_igot_server.py
- `Connections` --references--> `BaselineAssembler`  [INFERRED]
  docs/features/rag-quiz-generator.md → main-lms-backend/services/baseline_assembler.py
- `TODOs / edge cases` --references--> `MockIgotAdapter`  [INFERRED]
  docs/features/recommendation-engine.md → main-lms-backend/adapters/igot_adapter.py

## Import Cycles
- None detected.

## Communities (114 total, 31 thin omitted)

### Community 0 - "ReplyContext"
Cohesion: 0.15
Nodes (20): functools, importlib, Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile(), Any, Everything a reply template may personalise, built once per chat request., ReplyContext, _by_page() (+12 more)

### Community 1 - "language_service.py"
Cohesion: 0.17
Nodes (13): load_eval(), main(), detect_chat_language(), detect_chat_variant(), detect_chat_variant_or_none(), _devanagari_language(), Small, offline language routing for Gyan chat. This deliberately does *not* use…, Supported ISO 639-1 code for a chat message. (+5 more)

### Community 2 - "Code"
Cohesion: 0.05
Nodes (45): Code, In / out, Karma Points (gamification), TODOs / edge cases, TODOs / edge cases, CareerCard(), EVENT_META, KarmaCard() (+37 more)

### Community 3 - "Code"
Cohesion: 0.10
Nodes (34): bcrypt, Code, jose, change_password(), _clear_refresh_cookie(), login(), logout(), post (+26 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (43): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+35 more)

### Community 5 - "_get"
Cohesion: 0.14
Nodes (35): JSONResponse, _get(), GET with retries — the dev backend runs with --reload and may restart mid-run,…, get_admin_roster(), get_assessment_outcomes(), get_competencies(), get_course_catalog(), get_crosswalk() (+27 more)

### Community 6 - "rag.py"
Cohesion: 0.07
Nodes (28): asyncio, dataclasses, datetime, google_generativeai, httpx, io, json, langchain_text_splitters (+20 more)

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.08
Nodes (45): GyanBot(), GyanHero(), LanguageMenu(), LanguageMenuProps, CAPABILITIES, ChatWidget(), ChatWidgetProps, MessageBubble() (+37 more)

### Community 8 - "Any"
Cohesion: 0.19
Nodes (9): ILearningPlatformAdapter, ABC, Any, Interface for external learning platform integration. All concrete adapters…, Return the full CBP course catalog., Return learning history for a user (legacy, by govId or userId)., Return the full user roster (all officials)., Look up a single user by their iGOT userId (usr_...). Returns None if not found. (+1 more)

### Community 9 - "Code"
Cohesion: 0.20
Nodes (8): AI Course Recommendation Engine + Learning Pathways, Code, Connections, In / out, TODOs / edge cases, The id whose FRAC tags / levels / official text drive retrieval., {courseId: {compId: FRAC level}} — feeds BaselineAssembler so the Verified…, {courseId: title, primary competency, format, rating, enrolments} for analytics…

### Community 10 - "Code"
Cohesion: 0.17
Nodes (14): Code, AdminKPIs, AdminRosterRow, GAP_COLORS, HeatmapEntry, levelToNumber(), useAdminData(), UseAdminDataResult (+6 more)

### Community 11 - "models/models.py"
Cohesion: 0.17
Nodes (22): 7. Mismatches between the mermaid diagram and the code, Base, enum, Admin, Assessment, AssessmentSkillMapping, BaseUser, Competency (+14 more)

### Community 12 - "baseline_assembler.py"
Cohesion: 0.17
Nodes (22): Code, rows_for(), tag_id(), _education_score(), enrollment_course_id(), is_completed(), _last_evidence_date(), _map_category() (+14 more)

### Community 13 - "api.ts"
Cohesion: 0.15
Nodes (19): useLearnerDashboard(), SkillRow, CountCell, CourseUplift, fetchAchievements(), fetchCompetencies(), fetchEnrollments(), fetchKarmaLedger() (+11 more)

### Community 14 - "authApi.ts"
Cohesion: 0.27
Nodes (11): AuthProvider(), mapRole(), changePassword(), extractError(), getMe(), login(), LoginResponse, logout() (+3 more)

### Community 15 - "mock_igot_server.py"
Cohesion: 0.09
Nodes (33): exception_handler, fastapi_responses, HTTPException, CompetencyOut, composite_search(), CompositeSearchRequest, ContentStateRequest, _course_by_id() (+25 more)

### Community 16 - "lucide-react"
Cohesion: 0.17
Nodes (18): Visual design system (shared by every page), formatDate(), ProfileHeader(), AshokaChakra(), CountUp(), GovEmblem(), Reveal(), useInView() (+10 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - ".build_study_plan"
Cohesion: 0.20
Nodes (9): Cross-competency prerequisite DAG (SCIL v6 §5, B4), TODOs / limits, Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight), absorb(), add_step(), advance(), open_ladders(), Orders the required rungs of several pathways into one sequence. SCIL v6 §5… (+1 more)

### Community 19 - "test_pathway.py"
Cohesion: 0.08
Nodes (26): hashlib, _edge(), _gap(), _kinds_levels(), Skill-gap levels + level-aware recommendations + learning pathways. Runs on a…, _resolved(), test_already_met_prerequisite_changes_nothing(), test_beginner_gets_next_levels_in_order_never_advanced_or_basic() (+18 more)

### Community 20 - "domain.ts"
Cohesion: 0.06
Nodes (35): DEFER_REASON, KIND_STYLE, PathwayLadder(), ProfileHeaderProps, AppliedPrerequisite, BaseUser, ColdStartPrior, Competency (+27 more)

### Community 21 - ".__init__"
Cohesion: 0.33
Nodes (4): _CourseDoc, _parse_level(), Level 3' / 3 / '3' → 3; anything outside 1..5 → None., `catalog` / `frac` / `crosswalk` are the lists served by the mock iGOT server…

### Community 22 - "chatbot.py"
Cohesion: 0.21
Nodes (20): ChatResponse, _intent_response(), _intercept(), FILE: routers/chatbot.py Multilingual AI Learning Assistant — Gyan (ज्ञान)…, Deterministic handling of English commands the classifier has historically…, _response(), _theme_action(), _ui_action_response() (+12 more)

### Community 23 - "test_chat_messages.py"
Cohesion: 0.23
Nodes (11): Loads a language's template table on first use ("or" lives in or_.py; `or` is a…, templates(), _alternatives(), _fields(), parametrize, Catalogue completeness: every language has every template, placeholders are…, test_every_intent_renders(), test_placeholders_match_english() (+3 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "os"
Cohesion: 0.07
Nodes (44): Code, Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, dotenv, logging, build_system_prompt() (+36 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "CourseCard.tsx"
Cohesion: 0.24
Nodes (8): CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps, SOURCE_STYLES, matches(), Props, RecommendationsPanel()

### Community 28 - "test_reply_regression.py"
Cohesion: 0.20
Nodes (15): chat(), ChatHistoryItem, ChatRequest, detect_intent_keyword(), BaseModel, post, Multilingual AI Learning Assistant — Gyan (ज्ञान)., RecommendationContext (+7 more)

### Community 29 - "semantic_engine.py"
Cohesion: 0.08
Nodes (34): difflib, Code, Code, Connections, In / out, Shared Multilingual Embedder, TODOs / edge cases, _Embedder (+26 more)

### Community 30 - "CompetencyCalculator"
Cohesion: 0.22
Nodes (8): CompetencyCalculator, datetime, FILE: main-lms-backend/services/competency_service.py…, Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, Maps FRAC types from the JSON to calculation categories., test_missing_channels_do_not_drag_the_score_to_zero(), math

### Community 31 - "react"
Cohesion: 0.11
Nodes (28): App(), AssessmentPage, DashboardRedirect(), TokenBridge(), ProtectedRoute(), ProtectedRouteProps, AppShell(), AppShellProps (+20 more)

### Community 32 - "mock_data_metrics.py"
Cohesion: 0.10
Nodes (30): argparse, collections, live_metrics(), _login(), main(), offline_metrics(), _pct(), Mock-data quality metrics — run before/after regenerating mock data. cd main-… (+22 more)

### Community 33 - "proficiency_service.py"
Cohesion: 0.07
Nodes (52): Cold start for UNASSESSED competencies, Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8), Foresight, Proficiency belief with dated decay, cluster_of(), cohort_prior(), decay(), expected_shortfall() (+44 more)

### Community 34 - "seed.py"
Cohesion: 0.22
Nodes (13): hash_password(), Return a bcrypt hash of the plain-text password., _derive_password(), _fetch_officials(), main(), Session, auth/seed.py…, Insert the hardcoded admin user. Returns True if inserted, False if already… (+5 more)

### Community 35 - "speech.d.ts"
Cohesion: 0.20
Nodes (6): SpeechRecognition, SpeechRecognitionEvent, SpeechRecognitionResult, SpeechRecognitionResultItem, SpeechRecognitionResultList, Window

### Community 36 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 37 - "resolve_level"
Cohesion: 0.26
Nodes (16): Single source of truth for an official's level on one competency. Every…, resolve_level(), fuse_channels(), Weighted mean over the K/A/U/S channels that carry evidence (None → absent)., _assess(), SCIL v6 §3 evidence channels K/A/U/S (knowledge, application, utility,…, _row(), test_confirmed_use_is_a_floor_unconfirmed_is_not() (+8 more)

### Community 39 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 40 - "BaselineAssembler"
Cohesion: 0.29
Nodes (6): BaselineAssembler, _normalise_course_map(), Accept {courseId: {compId: level}} or the legacy {courseId: [compId]}., The old `requiredLevel - 1` cap made every evidence-backed gap permanent., test_completion_evidence_follows_the_crosswalk(), test_evidence_can_close_a_gap()

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 42 - "CLAUDE.md"
Cohesion: 0.23
Nodes (7): Admin Dashboard, Connections, In / out, TODOs / edge cases, Connections, In / out, Learner Dashboard (frontend shell)

### Community 43 - "main_backup.py"
Cohesion: 0.08
Nodes (38): AuthBase, Returns a FastAPI dependency that checks the current user's role. Example:…, require_role(), UserAuth, get_achievements(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments() (+30 more)

### Community 44 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 45 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 46 - "test_mock_data.py"
Cohesion: 0.06
Nodes (20): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only, fixture, Any, Plain holder; every attribute defaults to empty so features degrade, not crash., _read_disk(), ReferenceData (+12 more)

### Community 49 - "Code"
Cohesion: 0.13
Nodes (25): Code, StudioTab, _chunk_document_text(), _clean_text(), DocumentMetadata, DocumentUploadResponse, ErrorResponse, _extract_pdf() (+17 more)

### Community 58 - "LearnerDashboard.tsx"
Cohesion: 0.10
Nodes (17): LearnerDashboard, AssessmentUploadZone(), AssessmentUploadZoneProps, COLORS, LearningSnapshot(), Props, MyCoursesView(), MyCoursesViewProps (+9 more)

### Community 60 - "SCIL v6 — mock data + blocked features: progress report"
Cohesion: 0.25
Nodes (6): Before / after metrics, Could not do / blocked, Decisions log (made without the user), SCIL v6 — mock data + blocked features: progress report, Status, Catalogue duration in hours, or None for a course not in the catalogue.

### Community 61 - "prerequisite_service.py"
Cohesion: 0.05
Nodes (59): capability_risk(), _frac_names(), gsbpm_scope(), prerequisite_dag(), get, UserAuth, Rebuild the workforce snapshot now (≈ a few seconds)., Per statistical product: capable officials per critical competency, retirements… (+51 more)

### Community 62 - ".fetch_frac_competencies"
Cohesion: 0.18
Nodes (10): Noticed but out of scope (not fixed), GET /api/frac/competencies — the catalogue FRAC set incl. L1–L5 descriptors., calculate_baseline(), EvidencePayload, BaseModel, post, UploadFile, Calculates the skill baseline score b_k ∈ [0, 5] using the locked 6-term… (+2 more)

### Community 63 - "MockIgotAdapter"
Cohesion: 0.15
Nodes (10): GSBPM scope — the 80% officer-hours rule (SCIL v6 §1), MockIgotAdapter, GET a Sunbird endpoint and return its `result` object., GET /api/gsbpm/v1/map — GSBPM sub-processes + competency → sub-processes., GET /api/org/v1/offices — {cycle, offices[{officeId, subprocesses[{id,…, GET /api/frac/v1/prerequisites — {count, edges[]} expert-seeded prerequisite…, GET /api/course/v1/assessment/outcomes — {outcomes[], comparisons[]} pre/post θ…, GET /api/hrms/v1/officials — {officials{userId: DOB, superannuationDate,… (+2 more)

### Community 64 - "Authentication & RBAC"
Cohesion: 0.40
Nodes (4): Authentication & RBAC, In / out, TODOs / edge cases, Trainer

### Community 65 - "WorkforceInsights.tsx"
Cohesion: 0.11
Nodes (26): AGENDA_TYPE, CapabilityRiskPanel(), ForesightPanel(), GsbpmScopePanel(), pct(), PrerequisitePanel(), PRIORITY_CHIP, RISK_CHIP (+18 more)

### Community 66 - "AdminDashboard.tsx"
Cohesion: 0.14
Nodes (17): `frontend/src/`, AdminDashboard, ProgressView(), useSkillsData(), Theme, ThemeContext, ThemeContextType, ThemeProvider() (+9 more)

### Community 67 - "generate_mock_data.py"
Cohesion: 0.07
Nodes (57): _batch(), build_acbp(), build_catalog(), build_crosswalk(), build_enrollments(), build_frac(), build_gsbpm_map(), build_hrms() (+49 more)

### Community 68 - "3. Core data flow"
Cohesion: 0.17
Nodes (10): 3. Core data flow, Reference data loading, Workforce snapshot, GET /api/cbplan/v1/user/{id} — ACBP mandatory courses + learning hours/quarter.…, _build_workforce_snapshot(), Every official's resolved competency rows, for the SCIL v6 population / cohort…, Create users_auth table and karma tables if they don't exist yet., _startup() (+2 more)

### Community 69 - "DashboardCreator"
Cohesion: 0.16
Nodes (4): AdminDashboardCreator, DashboardCreator, OfficialDashboardCreator, TrainerDashboardCreator

### Community 70 - "Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)"
Cohesion: 0.22
Nodes (8): 1. Runtime topology, 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator

### Community 71 - "Code"
Cohesion: 0.09
Nodes (29): Code, Opportunity to practise (SCIL v6 §4), CompetencyOverviewTable(), LevelPips(), priorityOf(), Props, StudyPlanSummary(), RightSidebar() (+21 more)

### Community 72 - "main-lms-backend/main.py"
Cohesion: 0.10
Nodes (31): fastapi, fastapi_middleware_cors, fastapi_security, get_db(), auth/database.py…, Yields a database session and ensures it is closed after the request., get_current_user(), Session (+23 more)

### Community 76 - "Any"
Cohesion: 0.16
Nodes (13): BaseModel, Measured uplift → coverage learning + training effectiveness (SCIL v6 §6, B5), _course_summary(), _diagnostic_step(), _fmt_levels(), _interleave_by_level(), Any, One rung of a ladder. Finishing an in-progress course beats starting a new one. (+5 more)

### Community 77 - "document_extractor.py"
Cohesion: 0.21
Nodes (9): Code, CertificateUploadZone(), CertificateExtractionResult, DocumentExtractorService, ExtractedCompetency, BaseModel, FILE: main-lms-backend/services/document_extractor.py…, pypdf (+1 more)

### Community 87 - "EvidenceLog"
Cohesion: 0.24
Nodes (9): Certificate / Resume Evidence Extraction, Connections, In / out, TODOs / edge cases, Connections, In / out, Skill Gap Analysis (evidence-based competency baselines), TODOs / edge cases (+1 more)

### Community 88 - "_assert_self_or_admin"
Cohesion: 0.17
Nodes (15): Connections, _assert_self_or_admin(), award_karma_event(), CbpClaimRequest, claim_cbp_bonus(), get_karma_ledger(), KarmaEventRequest, BaseModel (+7 more)

### Community 89 - "QuizAttempt"
Cohesion: 0.25
Nodes (8): CLAUDE.md — index & router, Conventions, Feature index, graphify, How to use these docs, Run commands, QuizAttempt, Persists every MCQ-quiz submission BEFORE evidence is written. UniqueConstraint…

### Community 90 - "mock-igot-server/main.py"
Cohesion: 0.12
Nodes (21): contextlib, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history(), health() (+13 more)

### Community 91 - "_sunbird_result"
Cohesion: 0.25
Nodes (5): GET /api/frac/v1/crosswalk — iGOT dictionary CID id → catalogue FRAC id., GET /api/user/v2/read/{user_id} Returns: result.response — single user object…, GET /api/admin/v1/users Returns: result.users — full list of officials., Safely drill into a Sunbird envelope: data['result']['key1']['key2']..., _sunbird_result()

### Community 92 - "ingest_telemetry"
Cohesion: 0.33
Nodes (5): field_validator, ingest_telemetry(), Returns a list of validation errors for a single telemetry event., TelemetryBatch, _validate_event()

### Community 93 - "HybridRecommendationEngine"
Cohesion: 0.14
Nodes (14): GapEntry, HybridRecommendationEngine, Bayesian shrinkage toward global prior mean. Returns None if either input is…, Singleton — built ONCE at app startup. Holds FAISS index + BM25 corpus in…, FRAC levels at which the catalogue has at least one course for comp_id., Computes and prioritizes skill gaps. priority_k = gap_k * (target_k / 5.0)…, (query embedding, BM25 scores over the whole corpus), cached., Median cosine between the competency query and the courses NOT tagged with it —… (+6 more)

### Community 94 - "engine"
Cohesion: 0.21
Nodes (12): on_event, Create users_auth table if it doesn't exist yet., _startup(), _course(), engine(), _frac(), fixture, Hashed bag-of-words → L2-normalised vector. Shared words ⇒ positive cosine. (+4 more)

### Community 95 - "lifespan"
Cohesion: 0.33
Nodes (7): lifespan(), _load_json(), _load_json_from_dir(), Any, FastAPI, Load all datasets into memory once at startup, so no request touches the file…, Load a JSON file from ROOT_DIR. Raises RuntimeError on missing file.

### Community 96 - "test_chat_endpoint.py"
Cohesion: 0.42
Nodes (8): fastapi_testclient, _chat(), parametrize, End-to-end /chat behaviour per language through the real multilingual…, test_dark_mode_action(), test_my_courses_navigation(), test_recommendations(), test_skill_gaps()

### Community 97 - "download_model.py"
Cohesion: 0.28
Nodes (7): _download_from_hf(), _download_from_url(), main(), scripts/download_model.py…, Download from HuggingFace Hub using huggingface_hub library., Fallback: download via urllib (no extra deps)., urllib_request

### Community 98 - "_PrerequisiteGate"
Cohesion: 0.33
Nodes (3): _PrerequisiteGate, Cross-competency prerequisite DAG for build_study_plan (SCIL v6 §5, B4). A rung…, Edges that changed or annotate the plan: ordered (waited, then met), blocked,…

### Community 99 - "RecentActivityList.tsx"
Cohesion: 0.47
Nodes (5): ProgressViewProps, Props, RecentActivityList(), relative(), Achievement

### Community 100 - "grade_quiz"
Cohesion: 0.33
Nodes (5): _detect_skill_name(), grade_quiz(), post, Infers or extracts the skill/competency topic dynamically from the document's…, **Grade Quiz & Sync Competency to Internal DB & Mock iGOT Server** FIX (Bug…

### Community 101 - "Code"
Cohesion: 0.15
Nodes (15): Code, Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server + mock data), TODOs / edge cases, _competencies(), _prof_detail(), Safely read a field from profileDetails.professionalDetails[0]. (+7 more)

### Community 102 - "_user_enrolments"
Cohesion: 0.50
Nodes (4): legacy_user_history(), Merge seed enrolments with any runtime mutations., ICatalogSync.fetchUserHistory() — consumed by MockIgotPlatformAdapter., _user_enrolments()

### Community 103 - "Gyan — Multilingual Chat Assistant"
Cohesion: 0.40
Nodes (4): Connections, Gyan — Multilingual Chat Assistant, In / out, TODOs / edge cases

### Community 104 - "_learner_competency_state"
Cohesion: 0.13
Nodes (24): _ensure_can_view(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments_by_user_id(), get_frac_competencies(), get_learning_pathway(), get_profile_by_user_id(), get_recommendations_by_user_id() (+16 more)

### Community 105 - ".fetch_user_enrollments"
Cohesion: 0.40
Nodes (3): Connections, GET /api/course/v1/user/enrollment/list/{user_id} Returns: result.courses —…, Legacy method that maps fetch_user_enrollments to the old simple-mock shape.…

### Community 106 - "RAG Document → Quiz Generator & Grading"
Cohesion: 0.40
Nodes (4): Connections, In / out, RAG Document → Quiz Generator & Grading, TODOs / edge cases

## Knowledge Gaps
- **236 isolated node(s):** ``mock-igot-server/` — external-system simulator`, `4. Persistence`, `5. Tech stack`, `In / out`, `Connections` (+231 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 710 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `HybridRecommendationEngine` connect `HybridRecommendationEngine` to `mock_data_metrics.py`, `3. Core data flow`, `Code`, `rag.py`, `main-lms-backend/main.py`, `Code`, `models/models.py`, `Any`, `.build_study_plan`, `.__init__`, `SCIL v6 — mock data + blocked features: progress report`, `engine`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `Code` connect `Code` to `mock_data_metrics.py`, `_PrerequisiteGate`, `3. Core data flow`, `Code`, `_learner_competency_state`, `BaselineAssembler`, `Any`, `api.ts`, `.build_study_plan`, `domain.ts`, `HybridRecommendationEngine`, `.__init__`, `prerequisite_service.py`, `MockIgotAdapter`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `Code` connect `semantic_engine.py` to `language_service.py`, `ChatWidget.tsx`, `Gyan — Multilingual Chat Assistant`, `chatbot.py`, `test_reply_regression.py`, `engine`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `HybridRecommendationEngine` (e.g. with `7. Mismatches between the mermaid diagram and the code` and `Code`) actually correct?**
  _`HybridRecommendationEngine` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `MockIgotAdapter` (e.g. with `1. Runtime topology` and `6. Design patterns actually implemented`) actually correct?**
  _`MockIgotAdapter` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects ``mock-igot-server/` — external-system simulator`, `4. Persistence`, `5. Tech stack` to the rest of the system?**
  _236 weakly-connected nodes found - possible documentation gaps or missing edges._