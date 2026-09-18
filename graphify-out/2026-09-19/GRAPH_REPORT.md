# Graph Report - SIH_IGot  (2026-09-19)

## Corpus Check
- 214 files · ~4,904,357 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .css 1, .example 1)

## Summary
- 2150 nodes · 4866 edges · 119 communities (84 shown, 35 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 529 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e5218726`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ReplyContext
- AssessmentPage.tsx
- karma.py
- Code
- package.json
- _get
- competency.py
- ChatWidget.tsx
- main_backup.py
- KarmaRewardsView.tsx
- AdminDashboard.tsx
- Media (Video / Audio / YouTube) → Evidence-Cited Quiz
- baseline_assembler.py
- UserAuth
- pipeline.py
- mock_igot_server.py
- LandingPage.tsx
- What You Must Do When Invoked
- .build_study_plan
- test_pathway.py
- domain.ts
- extractors.py
- media_io.py
- Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)
- compilerOptions
- ai_tools.py
- 🇮🇳 MoSPI Skill Intelligence Platform
- media_quiz.py
- Ollama RAG Knowledge Base (Tier 3 — disconnected)
- _warm_up
- CompetencyCalculator
- react
- models/models.py
- proficiency_service.py
- seed.py
- speech.d.ts
- graphify reference: extra exports and benchmark
- resolve_level
- os
- compilerOptions
- BaselineAssembler
- graphify reference: query, path, explain
- CLAUDE.md
- main-lms-backend/main.py
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- test_mock_data.py
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- rag.py
- .claude/CLAUDE.md
- extraction-spec.md
- LearnerDashboard.tsx
- EvidenceLog
- estimate_uplift
- diagnostic.py
- MockIgotAdapter
- test_irt.py
- api.ts
- Code
- generate_mock_data.py
- engine
- Any
- QuizAttempt
- Code
- get_enriched_courses
- faker
- services_chat_messages
- services_chat_messages_context
- HybridRecommendationEngine
- _sunbird_result
- bn.py
- en.py
- gu.py
- hi.py
- hi_latn.py
- mr.py
- or_.py
- ta.py
- te.py
- language_service.py
- grade_quiz
- chatbot.py
- mock-igot-server/main.py
- 3. Core data flow
- _user_enrolments
- ._score_candidates
- Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)
- lifespan
- RAG Document → Quiz Generator & Grading
- CourseRecommendation
- ._quality_score
- recommendation_service.py
- json
- Code
- authApi.ts
- router.py
- question_gen.py
- Decisions log (made without the user)
- Timeline
- health
- .fetch_catalog
- google_generativeai
- langchain_text_splitters
- mockdata
- pdfplumber
- pptx
- pypdf
- requests
- routers
- services
- urllib_request

## God Nodes (most connected - your core abstractions)
1. `_get()` - 64 edges
2. `UserAuth` - 61 edges
3. `react` - 43 edges
4. `HybridRecommendationEngine` - 39 edges
5. `MockIgotAdapter` - 38 edges
6. `Code` - 37 edges
7. `ReplyContext` - 30 edges
8. `Code` - 30 edges
9. `Timeline` - 29 edges
10. `lucide-react` - 27 edges

## Surprising Connections (you probably didn't know these)
- `Code` --references--> `MonthlyCapBar()`  [INFERRED]
  docs/features/karma-points.md → frontend/src/components/dashboard/RightSidebar.tsx
- `Code` --references--> `StatTone`  [INFERRED]
  docs/features/learner-dashboard.md → frontend/src/components/shell/StatCard.tsx
- `Code` --references--> `StudioTab`  [INFERRED]
  docs/features/rag-quiz-generator.md → frontend/src/pages/AssessmentPage.tsx
- `Code` --references--> `SidebarHelp()`  [INFERRED]
  docs/features/learner-dashboard.md → frontend/src/pages/LearnerDashboard.tsx
- `Code` --references--> `SidebarArt()`  [INFERRED]
  docs/features/learner-dashboard.md → frontend/src/pages/LearnerDashboard.tsx

## Import Cycles
- None detected.

## Communities (119 total, 35 thin omitted)

### Community 0 - "ReplyContext"
Cohesion: 0.06
Nodes (68): fastapi_testclient, functools, importlib, Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile(), chat(), ChatHistoryItem, ChatRequest (+60 more)

### Community 1 - "AssessmentPage.tsx"
Cohesion: 0.11
Nodes (30): CONTENT_LABEL, MediaAnalysisCard(), MediaAnswerReview(), pct(), QuestionEvidence(), SOURCE_LABEL, YoutubeLinkInput(), PageHeader() (+22 more)

### Community 2 - "karma.py"
Cohesion: 0.05
Nodes (62): Code, KarmaEvent, KarmaEventType, KarmaMonthlyUsage, Immutable ledger entry — one row per karma point award event., Rolling monthly counter for non-CBP COURSE_COMPLETION events. Enforces the…, admin_adjust_karma(), AdminAdjustRequest (+54 more)

### Community 3 - "Code"
Cohesion: 0.08
Nodes (39): bcrypt, Code, TokenBridge(), mapRole(), registerLogoutCallback(), setApiToken(), hashlib, jose (+31 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (43): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+35 more)

### Community 5 - "_get"
Cohesion: 0.13
Nodes (37): _get(), GET with retries — the dev backend runs with --reload and may restart mid-run,…, get_admin_roster(), get_assessment_outcomes(), get_competencies(), get_course_catalog(), get_crosswalk(), get_gsbpm_map() (+29 more)

### Community 6 - "competency.py"
Cohesion: 0.11
Nodes (20): datetime, Code, Noticed but out of scope (not fixed), CertificateUploadZone(), calculate_baseline(), EvidencePayload, BaseModel, post (+12 more)

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.09
Nodes (43): Code, GyanBot(), GyanHero(), LanguageMenu(), LanguageMenuProps, CAPABILITIES, ChatWidget(), MessageBubble() (+35 more)

### Community 8 - "main_backup.py"
Cohesion: 0.09
Nodes (25): fastapi_middleware_cors, get_achievements(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments(), get_enrollments_by_user_id(), get_profile_by_user_id(), get_recommendations() (+17 more)

### Community 9 - "KarmaRewardsView.tsx"
Cohesion: 0.10
Nodes (28): KarmaCard(), milestones, MilestoneStep, MonthlyCapBar(), PassbookRow(), PILL_ORDER, RightSidebarProps, EVENT_META (+20 more)

### Community 10 - "AdminDashboard.tsx"
Cohesion: 0.13
Nodes (25): Code, AdminDashboard, StatCard(), AdminKPIs, AdminRosterRow, GAP_COLORS, HeatmapEntry, levelToNumber() (+17 more)

### Community 11 - "Media (Video / Audio / YouTube) → Evidence-Cited Quiz"
Cohesion: 0.22
Nodes (8): In / out, Media (Video / Audio / YouTube) → Evidence-Cited Quiz, Pipeline, Setup, TODOs / edge cases, Verification, YouTube, reject()

### Community 12 - "baseline_assembler.py"
Cohesion: 0.15
Nodes (25): Code, rows_for(), tag_id(), _education_score(), enrollment_course_id(), is_completed(), _last_evidence_date(), _map_category() (+17 more)

### Community 13 - "UserAuth"
Cohesion: 0.12
Nodes (25): AuthBase, Returns a FastAPI dependency that checks the current user's role. Example:…, require_role(), UserAuth, capability_risk(), _frac_names(), gsbpm_scope(), prerequisite_dag() (+17 more)

### Community 14 - "pipeline.py"
Cohesion: 0.09
Nodes (32): csv, main(), FILE: scripts/eval_media_quiz.py…, caption_regions(), needs_vlm(), fact_check(), _match(), protect_terms() (+24 more)

### Community 15 - "mock_igot_server.py"
Cohesion: 0.08
Nodes (36): exception_handler, field_validator, HTTPException, CompetencyOut, CompositeSearchRequest, ContentStateRequest, _course_by_id(), CourseOut (+28 more)

### Community 16 - "LandingPage.tsx"
Cohesion: 0.14
Nodes (20): Visual design system (shared by every page), AshokaChakra(), CountUp(), GovEmblem(), Reveal(), useInView(), StatCardProps, StatTone (+12 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents) (+15 more)

### Community 18 - ".build_study_plan"
Cohesion: 0.13
Nodes (13): _diagnostic_step(), absorb(), add_step(), advance(), open_ladders(), _PrerequisiteGate, Any, Orders the required rungs of several pathways into one sequence. SCIL v6 §5… (+5 more)

### Community 19 - "test_pathway.py"
Cohesion: 0.09
Nodes (23): _edge(), _gap(), _kinds_levels(), Skill-gap levels + level-aware recommendations + learning pathways. Runs on a…, _resolved(), test_already_met_prerequisite_changes_nothing(), test_beginner_gets_next_levels_in_order_never_advanced_or_basic(), test_completed_never_suggested_and_in_progress_is_continued() (+15 more)

### Community 20 - "domain.ts"
Cohesion: 0.04
Nodes (52): DEFER_REASON, KIND_STYLE, formatDate(), ProfileHeader(), ProfileHeaderProps, TAGLINE, ProgressViewProps, Props (+44 more)

### Community 21 - "extractors.py"
Cohesion: 0.10
Nodes (32): capabilities(), JSONResponse, add_captions(), flush(), _budget(), describe_keyframes(), guarded(), run_batch() (+24 more)

### Community 22 - "media_io.py"
Cohesion: 0.13
Nodes (24): Caption, _change(), download_youtube(), fetch(), is_youtube_url(), Keyframe, load_audio(), MediaInputError (+16 more)

### Community 23 - "Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)"
Cohesion: 0.25
Nodes (7): 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "ai_tools.py"
Cohesion: 0.10
Nodes (31): Code, dotenv, is_ollama_available(), Fast, synchronous check — just hits the Ollama /api/tags endpoint. Returns True…, FILE: ai/seed_knowledge.py…, Embeds all baseline knowledge into ChromaDB., seed(), add_documents_from_file() (+23 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "media_quiz.py"
Cohesion: 0.21
Nodes (16): fastapi_responses, importlib_util, MediaMetadata, MediaQuizQuestion, MediaQuizResponse, _process(), BaseModel, post (+8 more)

### Community 28 - "Ollama RAG Knowledge Base (Tier 3 — disconnected)"
Cohesion: 0.22
Nodes (8): Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, build_system_prompt(), generate_chat_response(), Runs the full RAG pipeline: 1. Retrieve top-k relevant document chunks from…, Builds a rich system prompt that grounds the LLM in the user's live context.…

### Community 29 - "_warm_up"
Cohesion: 0.10
Nodes (20): AbstractEventLoop, 1. Runtime topology, Connections, Gyan — Multilingual Chat Assistant, In / out, TODOs / edge cases, Connections, In / out (+12 more)

### Community 30 - "CompetencyCalculator"
Cohesion: 0.22
Nodes (8): CompetencyCalculator, datetime, FILE: main-lms-backend/services/competency_service.py…, Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, Maps FRAC types from the JSON to calculation categories., test_missing_channels_do_not_drag_the_score_to_zero(), math

### Community 31 - "react"
Cohesion: 0.09
Nodes (22): App(), AssessmentPage, DashboardRedirect(), ProtectedRoute(), ProtectedRouteProps, AuthContext, AuthContextType, AuthUser (+14 more)

### Community 32 - "models/models.py"
Cohesion: 0.16
Nodes (22): 7. Mismatches between the mermaid diagram and the code, Base, enum, SkillGapReport, Admin, Assessment, AssessmentSkillMapping, BaseUser (+14 more)

### Community 33 - "proficiency_service.py"
Cohesion: 0.07
Nodes (57): Cold start for UNASSESSED competencies, Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8), Foresight, Proficiency belief with dated decay, iGOT profile competencyLevel ('Level 3') → 3; missing → 0 (no claim)., Profile + enrollments + EvidenceLog → one resolved row per role competency.…, _resolve_competency_state(), _self_reported_level() (+49 more)

### Community 34 - "seed.py"
Cohesion: 0.20
Nodes (14): httpx, hash_password(), Return a bcrypt hash of the plain-text password., _derive_password(), _fetch_officials(), main(), Session, auth/seed.py… (+6 more)

### Community 35 - "speech.d.ts"
Cohesion: 0.20
Nodes (6): SpeechRecognition, SpeechRecognitionEvent, SpeechRecognitionResult, SpeechRecognitionResultItem, SpeechRecognitionResultList, Window

### Community 36 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 37 - "resolve_level"
Cohesion: 0.28
Nodes (15): Single source of truth for an official's level on one competency. Every…, resolve_level(), _assess(), SCIL v6 §3 evidence channels K/A/U/S (knowledge, application, utility,…, _row(), test_confirmed_use_is_a_floor_unconfirmed_is_not(), test_failed_work_sample_is_evidence_but_not_a_floor(), test_knowledge_only_score_is_unchanged() (+7 more)

### Community 38 - "os"
Cohesion: 0.15
Nodes (13): asyncio, base64, logging, FILE: ai/rag_engine.py…, scripts/quantize_model.py…, services/app_state.py — process-wide singletons built in main._warm_up…, FILE: services/media_quiz/llm.py…, services/reference_data.py — SCIL v6 reference datasets Loaded ONCE at startup… (+5 more)

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
Cohesion: 0.22
Nodes (8): Admin Dashboard, Connections, In / out, TODOs / edge cases, Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server + mock data), TODOs / edge cases

### Community 43 - "main-lms-backend/main.py"
Cohesion: 0.07
Nodes (35): _ensure_can_view(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments_by_user_id(), get_frac_competencies(), get_learning_pathway(), get_profile_by_user_id(), get_recommendations_by_user_id() (+27 more)

### Community 44 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 45 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 46 - "test_mock_data.py"
Cohesion: 0.06
Nodes (17): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only, Any, _read_disk(), data(), files(), fixture (+9 more)

### Community 49 - "rag.py"
Cohesion: 0.15
Nodes (27): Code, _chunk_document_text(), _clean_text(), DocumentMetadata, DocumentUploadResponse, ErrorResponse, _extract_pdf(), _extract_pptx() (+19 more)

### Community 58 - "LearnerDashboard.tsx"
Cohesion: 0.08
Nodes (26): LearnerDashboard, COLORS, LearningSnapshot(), Props, MyCoursesView(), MyCoursesViewProps, ProgressView(), AppShell() (+18 more)

### Community 60 - "EvidenceLog"
Cohesion: 0.15
Nodes (13): Certificate / Resume Evidence Extraction, Connections, In / out, TODOs / edge cases, Connections, In / out, Karma Points (gamification), TODOs / edge cases (+5 more)

### Community 61 - "estimate_uplift"
Cohesion: 0.06
Nodes (57): Cross-competency prerequisite DAG (SCIL v6 §5, B4), opportunity(), Any, services/gsbpm_service.py — GSBPM scoping (SCIL v6 §1) + opportunity to…, Opportunity to practise a competency in the official's office this cycle (SCIL…, Which competencies are in scope under the officer-hours rule, and why., scope_report(), _sp_name() (+49 more)

### Community 62 - "diagnostic.py"
Cohesion: 0.20
Nodes (14): get_current_user(), Session, Decodes the Bearer JWT, looks up the user in auth.db. Raises HTTP 401 for any…, answer(), AnswerBody, BaseModel, post, routers/diagnostic.py — adaptive "check your level" diagnostic (SCIL v6 §2,… (+6 more)

### Community 63 - "MockIgotAdapter"
Cohesion: 0.17
Nodes (8): MockIgotAdapter, Forget every cached read for this user., GET a Sunbird endpoint and return its `result` object., GET /api/frac/v1/prerequisites — {count, edges[]} expert-seeded prerequisite…, GET /api/course/v1/assessment/outcomes — {outcomes[], comparisons[]} pre/post θ…, GET /api/assessment/v1/itembank — 2PL items incl. answer keys (server side…, GET /api/hrms/v1/officials — {officials{userId: DOB, superannuationDate,…, Calls the Sunbird-compliant mock iGOT server (mock_igot_server.py) on port 8001…

### Community 64 - "test_irt.py"
Cohesion: 0.13
Nodes (23): DiagnosticSessions, fisher_information(), laplace_posterior(), next_item(), p_correct(), public_item(), Any, services/irt_service.py — Tier-1 Bayesian 2PL posterior + adaptive diagnostic… (+15 more)

### Community 65 - "api.ts"
Cohesion: 0.08
Nodes (37): AGENDA_TYPE, CapabilityRiskPanel(), ForesightPanel(), GsbpmScopePanel(), pct(), PrerequisitePanel(), PRIORITY_CHIP, RISK_CHIP (+29 more)

### Community 66 - "Code"
Cohesion: 0.23
Nodes (12): Code, VideoScan, get_ocr(), probe(), ProbeResult, ndarray, FILE: services/media_quiz/probe.py…, `regions` — precomputed speech spans (e.g. from YouTube captions) instead of… (+4 more)

### Community 67 - "generate_mock_data.py"
Cohesion: 0.07
Nodes (58): _batch(), build_acbp(), build_catalog(), build_crosswalk(), build_enrollments(), build_frac(), build_gsbpm_map(), build_hrms() (+50 more)

### Community 68 - "engine"
Cohesion: 0.14
Nodes (17): on_event, Create users_auth table if it doesn't exist yet., _startup(), _create_schema(), _create(), Create users_auth and the karma/evidence tables if missing (idempotent)., migrate_karma_schema(), Idempotent upgrade for databases created before the daily-cap rework: adds… (+9 more)

### Community 69 - "Any"
Cohesion: 0.17
Nodes (10): ILearningPlatformAdapter, ABC, Any, adapters/igot_adapter.py — iGOT Platform Adapter…, Interface for external learning platform integration. All concrete adapters…, Return the full CBP course catalog., Return learning history for a user (legacy, by govId or userId)., Return the full user roster (all officials). (+2 more)

### Community 70 - "QuizAttempt"
Cohesion: 0.25
Nodes (8): CLAUDE.md — index & router, Conventions, Feature index, graphify, How to use these docs, Run commands, QuizAttempt, Persists every MCQ-quiz submission BEFORE evidence is written. UniqueConstraint…

### Community 71 - "Code"
Cohesion: 0.07
Nodes (42): `frontend/src/`, Code, Connections, In / out, Learner Dashboard (frontend shell), TODOs / edge cases, Code, Opportunity to practise (SCIL v6 §4) (+34 more)

### Community 72 - "get_enriched_courses"
Cohesion: 0.33
Nodes (7): composite_search(), _course_tags(), _enriched_view(), get_enriched_courses(), _matches_filters(), Sunbird-style filters: each key → value or list of accepted values., The catalogue in the older "enriched" shape. Query params:…

### Community 76 - "HybridRecommendationEngine"
Cohesion: 0.19
Nodes (8): _fmt_levels(), HybridRecommendationEngine, One rung of a ladder. Finishing an in-progress course beats starting a new one., Singleton — built ONCE at app startup. Holds FAISS index + BM25 corpus in…, {courseId: title, primary competency, format, rating, enrolments} for analytics…, FRAC levels at which the catalogue has at least one course for comp_id., Computes and prioritizes skill gaps. priority_k = gap_k * (target_k / 5.0)…, Step-by-step path for one competency: one course per FRAC level from current+1…

### Community 77 - "_sunbird_result"
Cohesion: 0.22
Nodes (6): fetch(), GET /api/frac/competencies — the catalogue FRAC set incl. L1–L5 descriptors., GET /api/frac/v1/crosswalk — iGOT dictionary CID id → catalogue FRAC id., GET /api/admin/v1/users Returns: result.users — full list of officials., Safely drill into a Sunbird envelope: data['result']['key1']['key2']..., _sunbird_result()

### Community 87 - "language_service.py"
Cohesion: 0.24
Nodes (11): detect_chat_language(), detect_chat_variant(), detect_chat_variant_or_none(), _devanagari_language(), Small, offline language routing for Gyan chat. This deliberately does *not* use…, Supported ISO 639-1 code for a chat message., The variant the *text itself* signals, or None when it carries no signal. Plain…, Internal language variant: en, hi (Devanagari), hi_latn (romanized Hindi), mr,… (+3 more)

### Community 88 - "grade_quiz"
Cohesion: 0.17
Nodes (10): Authentication & RBAC, Connections, In / out, Shared database (Neon), TODOs / edge cases, _detect_skill_name(), grade_quiz(), post (+2 more)

### Community 89 - "chatbot.py"
Cohesion: 0.09
Nodes (30): difflib, is_embedder_ready(), model_name(), Non-blocking check — True only if the role's model is already loaded., classify_intent(), _correct_tokens(), _ensure_prototypes(), is_semantic_engine_ready() (+22 more)

### Community 90 - "mock-igot-server/main.py"
Cohesion: 0.12
Nodes (21): contextlib, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history(), health() (+13 more)

### Community 91 - "3. Core data flow"
Cohesion: 0.11
Nodes (17): 3. Core data flow, AsyncClient, AI Course Recommendation Engine + Learning Pathways, In / out, TODOs / edge cases, fetch(), fetch(), fetch() (+9 more)

### Community 92 - "_user_enrolments"
Cohesion: 0.50
Nodes (4): legacy_user_history(), Merge seed enrolments with any runtime mutations., ICatalogSync.fetchUserHistory() — consumed by MockIgotPlatformAdapter., _user_enrolments()

### Community 93 - "._score_candidates"
Cohesion: 0.16
Nodes (12): _course_summary(), GapEntry, _interleave_by_level(), BaseModel, ndarray, The id whose FRAC tags / levels / official text drive retrieval., Best course of each level (ascending), then the second-best of each, … Input…, (query embedding, BM25 scores over the whole corpus), cached. (+4 more)

### Community 94 - "Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)"
Cohesion: 0.33
Nodes (5): Measured uplift → coverage learning + training effectiveness (SCIL v6 §6, B5), Reference data loading, TODOs / limits, Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight), Attach per-course measured uplift (uplift_service.estimate_uplift) — SCIL v6 §6.

### Community 95 - "lifespan"
Cohesion: 0.33
Nodes (7): lifespan(), _load_json(), _load_json_from_dir(), Any, FastAPI, Load all datasets into memory once at startup, so no request touches the file…, Load a JSON file from ROOT_DIR. Raises RuntimeError on missing file.

### Community 96 - "RAG Document → Quiz Generator & Grading"
Cohesion: 0.40
Nodes (4): Connections, In / out, RAG Document → Quiz Generator & Grading, TODOs / edge cases

### Community 97 - "CourseRecommendation"
Cohesion: 0.23
Nodes (10): ChatWidgetProps, CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps, SOURCE_STYLES, matches(), Props (+2 more)

### Community 98 - "._quality_score"
Cohesion: 0.50
Nodes (3): Bayesian shrinkage toward global prior mean. Returns None if either input is…, quality = 0.35*completion_n + 0.35*rating_n + 0.20*pop_n + 0.10*tpac_flag FIX…, _shrunk_rating()

### Community 99 - "recommendation_service.py"
Cohesion: 0.09
Nodes (24): Code, _Embedder, encode_cached(), get_embedder(), _load(), onnx_model_dir(), _OnnxEmbedder, ndarray (+16 more)

### Community 100 - "json"
Cohesion: 0.14
Nodes (16): argparse, collections, io, json, load_eval(), main(), Benchmark Gyan's intent classifier on the held-out multilingual set. python…, live_metrics() (+8 more)

### Community 101 - "Code"
Cohesion: 0.22
Nodes (8): Code, GSBPM scope — the 80% officer-hours rule (SCIL v6 §1), _competencies(), _prof_detail(), GET /api/gsbpm/v1/map — GSBPM sub-processes + competency → sub-processes., GET /api/org/v1/offices — {cycle, offices[{officeId, subprocesses[{id,…, Safely read a field from profileDetails.professionalDetails[0]., Return the competencies list from profileDetails.competencies.

### Community 102 - "authApi.ts"
Cohesion: 0.31
Nodes (10): AuthProvider(), changePassword(), extractError(), getMe(), login(), LoginResponse, logout(), refresh() (+2 more)

### Community 106 - "router.py"
Cohesion: 0.14
Nodes (19): fastapi, fastapi_security, get_db(), auth/database.py…, Yields a database session and ensures it is closed after the request., auth/dependencies.py…, auth/models.py…, get_me() (+11 more)

### Community 107 - "question_gen.py"
Cohesion: 0.24
Nodes (17): Chunk, fmt_ts(), gemini_json(), ollama_vision_json(), parse_json(), Any, _chunk_pass(), _coerce() (+9 more)

### Community 108 - "Decisions log (made without the user)"
Cohesion: 0.20
Nodes (7): Before / after metrics, Could not do / blocked, Decisions log (made without the user), SCIL v6 — mock data + blocked features: progress report, Status, Catalogue duration in hours, or None for a course not in the catalogue., Median cosine between the competency query and the courses NOT tagged with it —…

### Community 110 - "Timeline"
Cohesion: 0.14
Nodes (9): Interpreter guard for subcommands, dataclasses, build_chunks(), Evidence, _make_chunk(), FILE: services/media_quiz/evidence.py…, slide_windows: [{"t_start", "t_end", "evidence_ids": [ocr/vlm ids of that…, _tag() (+1 more)

## Knowledge Gaps
- **256 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+251 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 811 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `UserAuth` connect `UserAuth` to `seed.py`, `Code`, `karma.py`, `main_backup.py`, `router.py`, `main-lms-backend/main.py`, `rag.py`, `grade_quiz`, `diagnostic.py`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `Code` connect `Code` to `seed.py`, `engine`, `KarmaRewardsView.tsx`, `router.py`, `UserAuth`, `grade_quiz`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `Code` connect `ChatWidget.tsx` to `ReplyContext`, `engine`, `language_service.py`, `chatbot.py`, `_warm_up`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `HybridRecommendationEngine` (e.g. with `7. Mismatches between the mermaid diagram and the code` and `Code`) actually correct?**
  _`HybridRecommendationEngine` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _256 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ReplyContext` be split into smaller, more focused modules?**
  _Cohesion score 0.058333333333333334 - nodes in this community are weakly interconnected._