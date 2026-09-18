# Graph Report - SIH_IGot  (2026-09-18)

## Corpus Check
- 196 files · ~4,879,474 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .css 1, .example 1)

## Summary
- 1844 nodes · 4033 edges · 125 communities (96 shown, 29 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 445 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8d152102`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ReplyContext
- language_service.py
- Code
- router.py
- package.json
- Code
- os
- ChatWidget.tsx
- ILearningPlatformAdapter
- .fetch_user_cbplan
- AdminDashboard.tsx
- models/models.py
- baseline_assembler.py
- api.ts
- authApi.ts
- mock_igot_server.py
- LandingPage.tsx
- What You Must Do When Invoked
- .build_study_plan
- test_pathway.py
- domain.ts
- ._quality_score
- chatbot.py
- test_chat_messages.py
- compilerOptions
- vector_store.py
- 🇮🇳 MoSPI Skill Intelligence Platform
- CourseRecommendation
- test_reply_regression.py
- get_embedder
- CompetencyCalculator
- react
- estimate_uplift
- workforce_service.py
- seed.py
- speech.d.ts
- graphify reference: extra exports and benchmark
- resolve_level
- insights.py
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
- rag.py
- .claude/CLAUDE.md
- extraction-spec.md
- LearnerDashboard.tsx
- SCIL v6 — mock data + blocked features: progress report
- prerequisite_service.py
- .fetch_frac_competencies
- Any
- test_irt.py
- WorkforceInsights.tsx
- `frontend/src/`
- generate_mock_data.py
- _startup
- DashboardCreator
- Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)
- Code
- main-lms-backend/main.py
- faker
- services_chat_messages
- services_chat_messages_context
- HybridRecommendationEngine
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
- karma.py
- semantic_engine.py
- _get
- _sunbird_result
- get_content_state
- ._score_candidates
- _StubEmbedder
- lifespan
- test_chat_endpoint.py
- download_model.py
- _PrerequisiteGate
- RightSidebar.tsx
- grade_quiz
- Mock iGOT Karmayogi Integration (Adapter + mock server + mock data)
- scope_report
- ai_tools.py
- Code
- .fetch_user_enrollments
- diagnostic.py
- .fetch_catalog
- proficiency_service.py
- cohort_prior
- dependencies.py
- LearningPathway.tsx
- typing
- test_proficiency_foresight.py
- mock_data_metrics.py
- Ollama RAG Knowledge Base (Tier 3 — disconnected)
- _build_workforce_snapshot
- get_recommendations_by_user_id
- context.py
- chat_actions.py
- _competencies
- _prof_detail
- mockdata
- routers
- services

## God Nodes (most connected - your core abstractions)
1. `_get()` - 61 edges
2. `UserAuth` - 58 edges
3. `react` - 40 edges
4. `HybridRecommendationEngine` - 37 edges
5. `MockIgotAdapter` - 35 edges
6. `Code` - 33 edges
7. `ReplyContext` - 30 edges
8. `Code` - 28 edges
9. `Code` - 26 edges
10. `_require_auth()` - 25 edges

## Surprising Connections (you probably didn't know these)
- `Code` --references--> `PassbookRow()`  [INFERRED]
  docs/features/karma-points.md → frontend/src/components/dashboard/RightSidebar.tsx
- `Code` --references--> `MonthlyCapBar()`  [INFERRED]
  docs/features/karma-points.md → frontend/src/components/dashboard/RightSidebar.tsx
- `Connections` --references--> `useTheme()`  [INFERRED]
  docs/features/chatbot-gyan.md → frontend/src/hooks/useTheme.tsx
- `1. Runtime topology` --references--> `MockIgotAdapter`  [INFERRED]
  ARCHITECTURE.md → main-lms-backend/adapters/igot_adapter.py
- `TODOs / edge cases` --references--> `MockIgotAdapter`  [INFERRED]
  docs/features/recommendation-engine.md → main-lms-backend/adapters/igot_adapter.py

## Import Cycles
- None detected.

## Communities (125 total, 29 thin omitted)

### Community 0 - "ReplyContext"
Cohesion: 0.19
Nodes (18): functools, importlib, Any, Everything a reply template may personalise, built once per chat request., ReplyContext, _by_page(), _gap_lines(), _greeting() (+10 more)

### Community 1 - "language_service.py"
Cohesion: 0.24
Nodes (9): detect_chat_language(), detect_chat_variant_or_none(), _devanagari_language(), Small, offline language routing for Gyan chat. This deliberately does *not* use…, Supported ISO 639-1 code for a chat message., The variant the *text itself* signals, or None when it carries no signal. Plain…, Pick the reply variant for a message, honouring the UI language picker. A…, resolve_chat_variant() (+1 more)

### Community 2 - "Code"
Cohesion: 0.08
Nodes (34): Code, In / out, Karma Points (gamification), TODOs / edge cases, KarmaEvent, KarmaEventType, KarmaMonthlyUsage, Immutable ledger entry — one row per karma point award event. (+26 more)

### Community 3 - "router.py"
Cohesion: 0.09
Nodes (41): bcrypt, Code, hashlib, jose, change_password(), _clear_refresh_cookie(), login(), logout() (+33 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (42): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+34 more)

### Community 5 - "Code"
Cohesion: 0.12
Nodes (36): Code, JSONResponse, _course_by_id(), get_assessment_outcomes(), get_competencies(), get_course_catalog(), get_gsbpm_map(), get_hrms_officials() (+28 more)

### Community 6 - "os"
Cohesion: 0.16
Nodes (10): json, logging, FILE: ai/rag_engine.py…, scripts/quantize_model.py…, FILE: main-lms-backend/services/recommendation_service.py…, smoke_test.py — End-to-end API test for skill-gaps + recommendations Run from:…, numpy, os (+2 more)

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.08
Nodes (41): GyanBot(), GyanHero(), LanguageMenu(), LanguageMenuProps, CAPABILITIES, MessageBubble(), renderMarkdown(), SUGGESTION_KEYS (+33 more)

### Community 8 - "ILearningPlatformAdapter"
Cohesion: 0.15
Nodes (8): ILearningPlatformAdapter, ABC, Interface for external learning platform integration. All concrete adapters…, Return the full CBP course catalog., Return learning history for a user (legacy, by govId or userId)., Return the full user roster (all officials)., Look up a single user by their iGOT userId (usr_...). Returns None if not found., Return all enrollment records for a user by their iGOT userId (usr_...). Each…

### Community 9 - ".fetch_user_cbplan"
Cohesion: 0.25
Nodes (6): AI Course Recommendation Engine + Learning Pathways, Connections, In / out, TODOs / edge cases, GET /api/cbplan/v1/user/{id} — ACBP mandatory courses + learning hours/quarter.…, {courseId: {compId: FRAC level}} — feeds BaselineAssembler so the Verified…

### Community 10 - "AdminDashboard.tsx"
Cohesion: 0.12
Nodes (27): Code, AdminDashboard, WorkforceInsights(), StatCard(), AdminKPIs, AdminRosterRow, GAP_COLORS, HeatmapEntry (+19 more)

### Community 11 - "models/models.py"
Cohesion: 0.14
Nodes (25): 7. Mismatches between the mermaid diagram and the code, Base, TODOs / edge cases, enum, SkillGapReport, Admin, Assessment, AssessmentSkillMapping (+17 more)

### Community 12 - "baseline_assembler.py"
Cohesion: 0.13
Nodes (27): Code, get_learning_pathway(), Step-by-step learning paths. For every role competency: one course per FRAC…, rows_for(), tag_id(), _education_score(), enrollment_course_id(), is_completed() (+19 more)

### Community 13 - "api.ts"
Cohesion: 0.20
Nodes (15): useLearnerDashboard(), CountCell, CourseUplift, fetchAchievements(), fetchEnrollments(), fetchKarmaLedger(), fetchRecommendations(), fetchSkillGapsAndProfile() (+7 more)

### Community 14 - "authApi.ts"
Cohesion: 0.29
Nodes (10): AuthProvider(), mapRole(), extractError(), getMe(), login(), LoginResponse, logout(), refresh() (+2 more)

### Community 15 - "mock_igot_server.py"
Cohesion: 0.10
Nodes (30): exception_handler, fastapi_responses, HTTPException, CompetencyOut, composite_search(), CompositeSearchRequest, _course_tags(), CourseOut (+22 more)

### Community 16 - "LandingPage.tsx"
Cohesion: 0.16
Nodes (18): Visual design system (shared by every page), formatDate(), ProfileHeader(), AshokaChakra(), CountUp(), GovEmblem(), Reveal(), useInView() (+10 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - ".build_study_plan"
Cohesion: 0.31
Nodes (7): Cross-competency prerequisite DAG (SCIL v6 §5, B4), absorb(), add_step(), advance(), open_ladders(), Orders the required rungs of several pathways into one sequence. SCIL v6 §5…, Does taking `course_id` complete this ladder's next rung?

### Community 19 - "test_pathway.py"
Cohesion: 0.08
Nodes (25): _edge(), _gap(), _kinds_levels(), Skill-gap levels + level-aware recommendations + learning pathways. Runs on a…, _resolved(), test_already_met_prerequisite_changes_nothing(), test_beginner_gets_next_levels_in_order_never_advanced_or_basic(), test_completed_never_suggested_and_in_progress_is_continued() (+17 more)

### Community 20 - "domain.ts"
Cohesion: 0.07
Nodes (27): ProfileHeaderProps, AppliedPrerequisite, BaseUser, ColdStartPrior, Competency, CompetencyCrosswalk, CompetencyProfile, Course (+19 more)

### Community 21 - "._quality_score"
Cohesion: 0.20
Nodes (7): _CourseDoc, _parse_level(), Bayesian shrinkage toward global prior mean. Returns None if either input is…, Level 3' / 3 / '3' → 3; anything outside 1..5 → None., `catalog` / `frac` / `crosswalk` are the lists served by the mock iGOT server…, quality = 0.35*completion_n + 0.35*rating_n + 0.20*pop_n + 0.10*tpac_flag FIX…, _shrunk_rating()

### Community 22 - "chatbot.py"
Cohesion: 0.30
Nodes (16): ChatResponse, _intent_response(), _intercept(), FILE: routers/chatbot.py Multilingual AI Learning Assistant — Gyan (ज्ञान)…, Deterministic handling of English commands the classifier has historically…, _response(), _theme_action(), _ui_action_response() (+8 more)

### Community 23 - "test_chat_messages.py"
Cohesion: 0.23
Nodes (11): Loads a language's template table on first use ("or" lives in or_.py; `or` is a…, templates(), _alternatives(), _fields(), parametrize, Catalogue completeness: every language has every template, placeholders are…, test_every_intent_renders(), test_placeholders_match_english() (+3 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "vector_store.py"
Cohesion: 0.16
Nodes (18): Code, dotenv, FILE: ai/seed_knowledge.py…, Embeds all baseline knowledge into ChromaDB., seed(), add_documents_from_file(), add_text_to_store(), _get_embeddings() (+10 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "CourseRecommendation"
Cohesion: 0.23
Nodes (10): ChatWidgetProps, CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps, SOURCE_STYLES, matches(), Props (+2 more)

### Community 28 - "test_reply_regression.py"
Cohesion: 0.18
Nodes (16): asyncio, chat(), ChatHistoryItem, ChatRequest, detect_intent_keyword(), BaseModel, post, Multilingual AI Learning Assistant — Gyan (ज्ञान). (+8 more)

### Community 29 - "get_embedder"
Cohesion: 0.13
Nodes (16): Code, Connections, In / out, Shared Multilingual Embedder, TODOs / edge cases, _Embedder, get_embedder(), is_embedder_ready() (+8 more)

### Community 30 - "CompetencyCalculator"
Cohesion: 0.22
Nodes (8): CompetencyCalculator, datetime, FILE: main-lms-backend/services/competency_service.py…, Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, Maps FRAC types from the JSON to calculation categories., test_missing_channels_do_not_drag_the_score_to_zero(), math

### Community 31 - "react"
Cohesion: 0.10
Nodes (31): App(), AssessmentPage, DashboardRedirect(), TokenBridge(), ProtectedRoute(), ProtectedRouteProps, AppShell(), AppShellProps (+23 more)

### Community 32 - "estimate_uplift"
Cohesion: 0.17
Nodes (19): estimate_uplift(), _features(), _ipw(), Any, ndarray, services/uplift_service.py — measured course uplift (SCIL v6 §6 coverage…, [1, z, z², tenure/10, statistics degree] with z = preθ − (level − 0.5): takers…, Newton–Raphson for an L2-penalised logistic regression (intercept unpenalised). (+11 more)

### Community 33 - "workforce_service.py"
Cohesion: 0.28
Nodes (14): _as_date(), capability_risk(), cell(), foresight(), _level(), _p_capable(), Any, date (+6 more)

### Community 34 - "seed.py"
Cohesion: 0.14
Nodes (17): auth/database.py…, auth/models.py…, hash_password(), Return a bcrypt hash of the plain-text password., _derive_password(), _fetch_officials(), main(), Session (+9 more)

### Community 35 - "speech.d.ts"
Cohesion: 0.20
Nodes (6): SpeechRecognition, SpeechRecognitionEvent, SpeechRecognitionResult, SpeechRecognitionResultItem, SpeechRecognitionResultList, Window

### Community 36 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 37 - "resolve_level"
Cohesion: 0.35
Nodes (13): Single source of truth for an official's level on one competency. Every…, resolve_level(), _assess(), SCIL v6 §3 evidence channels K/A/U/S (knowledge, application, utility,…, _row(), test_confirmed_use_is_a_floor_unconfirmed_is_not(), test_failed_work_sample_is_evidence_but_not_a_floor(), test_knowledge_only_score_is_unchanged() (+5 more)

### Community 38 - "insights.py"
Cohesion: 0.14
Nodes (19): capability_risk(), _frac_names(), prerequisite_dag(), post, routers/insights.py — admin-only SCIL v6 workforce insights Every number here…, Rebuild the workforce snapshot now (≈ a few seconds)., Per statistical product: capable officials per critical competency, retirements…, 36-month projection of expected capable officials: attrition × dated skill… (+11 more)

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
Cohesion: 0.10
Nodes (17): CLAUDE.md — index & router, Feature index, graphify, How to use these docs, Run commands, Admin Dashboard, Connections, In / out (+9 more)

### Community 43 - "UserAuth"
Cohesion: 0.07
Nodes (30): AuthBase, UserAuth, get_me(), Return the current authenticated user's profile. Used by the frontend to re-…, get_achievements(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments() (+22 more)

### Community 44 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 45 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 46 - "test_mock_data.py"
Cohesion: 0.07
Nodes (15): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only, data(), files(), fixture, Mock-data generator (mock-igot-server/generate_mock_data.py): determinism, one…, _tags() (+7 more)

### Community 49 - "rag.py"
Cohesion: 0.11
Nodes (32): Code, StudioTab, google_generativeai, langchain_text_splitters, _chunk_document_text(), _clean_text(), DocumentMetadata, DocumentUploadResponse (+24 more)

### Community 58 - "LearnerDashboard.tsx"
Cohesion: 0.10
Nodes (18): LearnerDashboard, AssessmentUploadZone(), AssessmentUploadZoneProps, COLORS, LearningSnapshot(), Props, MyCoursesView(), MyCoursesViewProps (+10 more)

### Community 60 - "SCIL v6 — mock data + blocked features: progress report"
Cohesion: 0.20
Nodes (7): Before / after metrics, Could not do / blocked, Decisions log (made without the user), SCIL v6 — mock data + blocked features: progress report, Status, Catalogue duration in hours, or None for a course not in the catalogue., Median cosine between the competency query and the courses NOT tagged with it —…

### Community 61 - "prerequisite_service.py"
Cohesion: 0.14
Nodes (24): find_cycle(), infer_edges(), _node(), _norm_sf(), _ols(), Any, ndarray, services/prerequisite_service.py — cross-competency prerequisite DAG (SCIL v6… (+16 more)

### Community 62 - ".fetch_frac_competencies"
Cohesion: 0.18
Nodes (10): Noticed but out of scope (not fixed), GET /api/frac/competencies — the catalogue FRAC set incl. L1–L5 descriptors., calculate_baseline(), EvidencePayload, BaseModel, post, UploadFile, Calculates the skill baseline score b_k ∈ [0, 5] using the locked 6-term… (+2 more)

### Community 63 - "Any"
Cohesion: 0.16
Nodes (10): GSBPM scope — the 80% officer-hours rule (SCIL v6 §1), Any, GET a Sunbird endpoint and return its `result` object., GET /api/gsbpm/v1/map — GSBPM sub-processes + competency → sub-processes., GET /api/org/v1/offices — {cycle, offices[{officeId, subprocesses[{id,…, GET /api/frac/v1/prerequisites — {count, edges[]} expert-seeded prerequisite…, GET /api/course/v1/assessment/outcomes — {outcomes[], comparisons[]} pre/post θ…, GET /api/assessment/v1/itembank — 2PL items incl. answer keys (server side… (+2 more)

### Community 64 - "test_irt.py"
Cohesion: 0.12
Nodes (24): DiagnosticSessions, fisher_information(), laplace_posterior(), next_item(), p_correct(), public_item(), Any, services/irt_service.py — Tier-1 Bayesian 2PL posterior + adaptive diagnostic… (+16 more)

### Community 65 - "WorkforceInsights.tsx"
Cohesion: 0.11
Nodes (26): AGENDA_TYPE, CapabilityRiskPanel(), ForesightPanel(), GsbpmScopePanel(), pct(), PrerequisitePanel(), PRIORITY_CHIP, RISK_CHIP (+18 more)

### Community 66 - "`frontend/src/`"
Cohesion: 0.14
Nodes (15): `frontend/src/`, ChatWidget(), ProgressView(), ProgressViewProps, Props, RecentActivityList(), relative(), useChatEngine() (+7 more)

### Community 67 - "generate_mock_data.py"
Cohesion: 0.07
Nodes (58): _batch(), build_acbp(), build_catalog(), build_crosswalk(), build_enrollments(), build_frac(), build_gsbpm_map(), build_hrms() (+50 more)

### Community 68 - "_startup"
Cohesion: 0.20
Nodes (12): Measured uplift → coverage learning + training effectiveness (SCIL v6 §6, B5), Reference data loading, TODOs / limits, Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight), on_event, Create users_auth table if it doesn't exist yet., _startup(), on_event (+4 more)

### Community 69 - "DashboardCreator"
Cohesion: 0.16
Nodes (4): AdminDashboardCreator, DashboardCreator, OfficialDashboardCreator, TrainerDashboardCreator

### Community 70 - "Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)"
Cohesion: 0.22
Nodes (8): 1. Runtime topology, 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator

### Community 71 - "Code"
Cohesion: 0.13
Nodes (22): Code, CompetencyOverviewTable(), LevelPips(), priorityOf(), Props, CHANNEL_LABEL, CONFIDENCE_CONFIG, DOMAIN_BADGE (+14 more)

### Community 72 - "main-lms-backend/main.py"
Cohesion: 0.12
Nodes (25): datetime, fastapi, fastapi_middleware_cors, httpx, MockIgotAdapter, adapters/igot_adapter.py — iGOT Platform Adapter…, Calls the Sunbird-compliant mock iGOT server (mock_igot_server.py) on port 8001…, main.py — MoSPI LMS Backend API (Main Orchestrator)… (+17 more)

### Community 76 - "HybridRecommendationEngine"
Cohesion: 0.14
Nodes (13): _course_summary(), _diagnostic_step(), _fmt_levels(), HybridRecommendationEngine, Any, One rung of a ladder. Finishing an in-progress course beats starting a new one., High-uncertainty levels get a short check before a full course (SCIL v6 §2)., Singleton — built ONCE at app startup. Holds FAISS index + BM25 corpus in… (+5 more)

### Community 77 - "document_extractor.py"
Cohesion: 0.21
Nodes (9): Code, CertificateUploadZone(), CertificateExtractionResult, DocumentExtractorService, ExtractedCompetency, BaseModel, FILE: main-lms-backend/services/document_extractor.py…, pypdf (+1 more)

### Community 87 - "EvidenceLog"
Cohesion: 0.33
Nodes (6): Conventions, Certificate / Resume Evidence Extraction, Connections, In / out, TODOs / edge cases, EvidenceLog

### Community 88 - "karma.py"
Cohesion: 0.14
Nodes (19): Authentication & RBAC, Connections, In / out, Shared database (Neon), _assert_self_or_admin(), award_karma_event(), CbpClaimRequest, claim_cbp_bonus() (+11 more)

### Community 89 - "semantic_engine.py"
Cohesion: 0.11
Nodes (25): argparse, difflib, Code, io, model_name(), classify_intent(), _correct_tokens(), _ensure_prototypes() (+17 more)

### Community 90 - "_get"
Cohesion: 0.08
Nodes (32): contextlib, _get(), GET with retries — the dev backend runs with --reload and may restart mid-run,…, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles() (+24 more)

### Community 91 - "_sunbird_result"
Cohesion: 0.25
Nodes (5): GET /api/frac/v1/crosswalk — iGOT dictionary CID id → catalogue FRAC id., GET /api/user/v2/read/{user_id} Returns: result.response — single user object…, GET /api/admin/v1/users Returns: result.users — full list of officials., Safely drill into a Sunbird envelope: data['result']['key1']['key2']..., _sunbird_result()

### Community 92 - "get_content_state"
Cohesion: 0.18
Nodes (9): field_validator, ContentStateRequest, get_admin_roster(), get_content_state(), legacy_user_history(), Merge seed enrolments with any runtime mutations., ICatalogSync.fetchUserHistory() — consumed by MockIgotPlatformAdapter., TelemetryBatch (+1 more)

### Community 93 - "._score_candidates"
Cohesion: 0.18
Nodes (11): GapEntry, _interleave_by_level(), BaseModel, ndarray, The id whose FRAC tags / levels / official text drive retrieval., Best course of each level (ascending), then the second-best of each, … Input…, (query embedding, BM25 scores over the whole corpus), cached., Stage 1 + Stage 2 for a single competency gap. Returns list of (catalog_idx,… (+3 more)

### Community 94 - "_StubEmbedder"
Cohesion: 0.36
Nodes (7): _course(), _frac(), Hashed bag-of-words → L2-normalised vector. Shared words ⇒ positive cosine., _StubEmbedder, test_classroom_cap_defers_the_ladder(), test_curated_crosswalk_is_used_before_embeddings(), test_explicit_non_tpac_flag_is_not_overridden_by_creator_name()

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

### Community 99 - "RightSidebar.tsx"
Cohesion: 0.11
Nodes (19): Connections, In / out, Learner Dashboard (frontend shell), TODOs / edge cases, CareerCard(), EVENT_META, KarmaCard(), milestones (+11 more)

### Community 100 - "grade_quiz"
Cohesion: 0.33
Nodes (5): _detect_skill_name(), grade_quiz(), post, Infers or extracts the skill/competency topic dynamically from the document's…, **Grade Quiz & Sync Competency to Internal DB & Mock iGOT Server** FIX (Bug…

### Community 101 - "Mock iGOT Karmayogi Integration (Adapter + mock server + mock data)"
Cohesion: 0.50
Nodes (4): Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server + mock data), TODOs / edge cases

### Community 102 - "scope_report"
Cohesion: 0.18
Nodes (13): gsbpm_scope(), SCIL v6 §1 — the 80% officer-hours scoping report (whole NSO, or one office)., Any, services/gsbpm_service.py — GSBPM scoping (SCIL v6 §1) + opportunity to…, Which competencies are in scope under the officer-hours rule, and why., scope_report(), _sp_name(), subprocess_hours() (+5 more)

### Community 103 - "ai_tools.py"
Cohesion: 0.17
Nodes (14): is_ollama_available(), Fast, synchronous check — just hits the Ollama /api/tags endpoint. Returns True…, ai_health_check(), HealthResponse, BaseModel, post, UploadFile, FILE: routers/ai_tools.py… (+6 more)

### Community 104 - "Code"
Cohesion: 0.12
Nodes (22): 3. Core data flow, Code, Connections, In / out, Skill Gap Analysis (evidence-based competency baselines), TODOs / edge cases, Opportunity to practise (SCIL v6 §4), PathwayLadder() (+14 more)

### Community 105 - ".fetch_user_enrollments"
Cohesion: 0.40
Nodes (3): Connections, GET /api/course/v1/user/enrollment/list/{user_id} Returns: result.courses —…, Legacy method that maps fetch_user_enrollments to the old simple-mock shape.…

### Community 106 - "diagnostic.py"
Cohesion: 0.23
Nodes (13): get_db(), Yields a database session and ensures it is closed after the request., answer(), AnswerBody, BaseModel, post, routers/diagnostic.py — adaptive "check your level" diagnostic (SCIL v6 §2,…, Posterior mean → one PRACTICE_ASSESSMENT EvidenceLog row (the existing evidence… (+5 more)

### Community 108 - "proficiency_service.py"
Cohesion: 0.23
Nodes (12): expected_shortfall(), months_between(), _phi(), _Phi(), proficiency_state(), datetime, services/proficiency_service.py — probabilistic proficiency state (SCIL v6 §2)…, Belief for an assessed competency, decayed by the age of its newest dated… (+4 more)

### Community 109 - "cohort_prior"
Cohesion: 0.23
Nodes (12): cluster_of(), cohort_prior(), population_stats(), Any, Cohort prior for an UNASSESSED competency, with the divergence check., comp → (μ_pop, σ_pop, n) over officials with assessed evidence on it., tenure_band(), _official() (+4 more)

### Community 110 - "dependencies.py"
Cohesion: 0.20
Nodes (9): fastapi_security, get_current_user(), Session, auth/dependencies.py…, Decodes the Bearer JWT, looks up the user in auth.db. Raises HTTP 401 for any…, Returns a FastAPI dependency that checks the current user's role. Example:…, require_role(), decode_access_token() (+1 more)

### Community 111 - "LearningPathway.tsx"
Cohesion: 0.18
Nodes (8): DEFER_REASON, KIND_STYLE, GapRowProps, LearningPathway, PathwayCourse, PathwayStep, PathwayStepKind, StudyPlan

### Community 112 - "typing"
Cohesion: 0.25
Nodes (7): services/app_state.py — process-wide singletons built in main._startup. Routers…, Any, services/reference_data.py — SCIL v6 reference datasets Loaded ONCE at startup…, Plain holder; every attribute defaults to empty so features degrade, not crash., _read_disk(), ReferenceData, typing

### Community 113 - "test_proficiency_foresight.py"
Cohesion: 0.31
Nodes (9): decay(), (μ_t, σ_t, λ) — relax the belief toward the population prior as evidence ages., _hrms(), SCIL v6 §2 dated decay / expected-shortfall / cold start, and §11 workforce…, _snap(), test_accuracy_skills_decay_faster_than_procedural(), test_decay_relaxes_toward_the_population_mean_not_zero(), test_foresight_declines_with_retirements_and_attrition() (+1 more)

### Community 114 - "mock_data_metrics.py"
Cohesion: 0.36
Nodes (8): collections, live_metrics(), _login(), main(), offline_metrics(), _pct(), Mock-data quality metrics — run before/after regenerating mock data. cd main-…, Admin bearer header; retried while the backend (--reload) restarts.

### Community 115 - "Ollama RAG Knowledge Base (Tier 3 — disconnected)"
Cohesion: 0.22
Nodes (8): Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, build_system_prompt(), generate_chat_response(), Runs the full RAG pipeline: 1. Retrieve top-k relevant document chunks from…, Builds a rich system prompt that grounds the LLM in the user's live context.…

### Community 116 - "_build_workforce_snapshot"
Cohesion: 0.22
Nodes (9): Cold start for UNASSESSED competencies, Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8), Foresight, Proficiency belief with dated decay, Workforce snapshot, _build_workforce_snapshot(), Every official's resolved competency rows, for the SCIL v6 population / cohort…, office_phase() (+1 more)

### Community 117 - "get_recommendations_by_user_id"
Cohesion: 0.33
Nodes (6): get_recommendations_by_user_id(), get_skill_gaps_by_user_id(), _level_to_int(), Level 3' → 3, 'Level 2' → 2, fallback → 2, Skill-gap analysis for a learner by their iGOT userId., AI-ranked course recommendations personalised by skill gap.

### Community 118 - "context.py"
Cohesion: 0.40
Nodes (3): dataclasses, Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile()

### Community 119 - "chat_actions.py"
Cohesion: 0.50
Nodes (4): detect_ui_actions(), _mentions(), Detect website theme / language changes requested in any supported chat…, Returns (theme, language): theme in {"dark", "light", "toggle"}, language in…

## Knowledge Gaps
- **237 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+232 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 719 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MockIgotAdapter` connect `main-lms-backend/main.py` to `_startup`, `Code`, `Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)`, `Code`, `.fetch_user_cbplan`, `ILearningPlatformAdapter`, `models/models.py`, `.fetch_catalog`, `.fetch_user_enrollments`, `EvidenceLog`, `karma.py`, `_sunbird_result`, `SCIL v6 — mock data + blocked features: progress report`, `.fetch_frac_competencies`, `Any`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `Code` connect `Code` to `estimate_uplift`, `_PrerequisiteGate`, `_startup`, `Code`, `main-lms-backend/main.py`, `.fetch_user_cbplan`, `BaselineAssembler`, `baseline_assembler.py`, `api.ts`, `HybridRecommendationEngine`, `.build_study_plan`, `._quality_score`, `._score_candidates`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `Code` connect `semantic_engine.py` to `language_service.py`, ``frontend/src/``, `_startup`, `ChatWidget.tsx`, `CLAUDE.md`, `chatbot.py`, `test_reply_regression.py`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Are the 44 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 44 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `HybridRecommendationEngine` (e.g. with `7. Mismatches between the mermaid diagram and the code` and `Code`) actually correct?**
  _`HybridRecommendationEngine` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `MockIgotAdapter` (e.g. with `1. Runtime topology` and `6. Design patterns actually implemented`) actually correct?**
  _`MockIgotAdapter` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _237 weakly-connected nodes found - possible documentation gaps or missing edges._