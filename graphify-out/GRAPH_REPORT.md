# Graph Report - SIH_IGot  (2026-09-19)

## Corpus Check
- 217 files · ~4,910,563 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .css 1, .example 1)

## Summary
- 2218 nodes · 5077 edges · 120 communities (87 shown, 33 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 590 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `10c47fef`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ReplyContext
- AssessmentPage.tsx
- Code
- router.py
- package.json
- _get
- Code
- ChatWidget.tsx
- UserAuth
- KarmaRewardsView.tsx
- AdminDashboard.tsx
- pipeline.py
- baseline_assembler.py
- insights.py
- Timeline
- BaseModel
- question_gen.py
- What You Must Do When Invoked
- HybridRecommendationEngine
- test_pathway.py
- domain.ts
- extractors.py
- media_io.py
- rag.py
- compilerOptions
- ai_tools.py
- 🇮🇳 MoSPI Skill Intelligence Platform
- _process
- proficiency_service.py
- 1. Runtime topology
- CompetencyCalculator
- react
- chatbot.py
- opportunity
- _seed_officials
- speech.d.ts
- graphify reference: extra exports and benchmark
- resolve_level
- test_practice_assessment.py
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
- models/models.py
- .claude/CLAUDE.md
- extraction-spec.md
- DashboardCreator
- test_chat_messages.py
- prerequisite_service.py
- main-lms-backend/main.py
- MockIgotAdapter
- test_irt.py
- api.ts
- probe.py
- generate_mock_data.py
- engine
- Any
- _warm_up
- LearnerDashboard.tsx
- upload_certificate
- faker
- services_chat_messages
- services_chat_messages_context
- recommendation_service.py
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
- chat
- list_attempts
- mock-igot-server/main.py
- Code
- _user_enrolments
- Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)
- os
- mock_igot_server.py
- test_chat_endpoint.py
- CourseRecommendation
- lifespan
- semantic_engine.py
- mock_data_metrics.py
- Admin Dashboard
- authApi.ts
- routers
- services
- practice_assessment.py
- relevance.py
- EvidenceLog
- Ollama RAG Knowledge Base (Tier 3 — disconnected)
- google_generativeai
- langchain_text_splitters
- mockdata
- pdfplumber
- estimate_uplift
- pptx
- pypdf
- requests
- urllib_request
- CLAUDE.md — index & router
- _Embedder

## God Nodes (most connected - your core abstractions)
1. `_get()` - 65 edges
2. `UserAuth` - 62 edges
3. `Code` - 46 edges
4. `react` - 44 edges
5. `HybridRecommendationEngine` - 39 edges
6. `MockIgotAdapter` - 38 edges
7. `Code` - 37 edges
8. `ReplyContext` - 30 edges
9. `Code` - 30 edges
10. `Timeline` - 29 edges

## Surprising Connections (you probably didn't know these)
- `Code` --references--> `StatTone`  [INFERRED]
  docs/features/learner-dashboard.md → frontend/src/components/shell/StatCard.tsx
- `TODOs / edge cases` --references--> `gradeQuiz()`  [INFERRED]
  docs/features/media-quiz-generator.md → frontend/src/services/api.ts
- `7. Mismatches between the mermaid diagram and the code` --references--> `SkillGapReport`  [INFERRED]
  ARCHITECTURE.md → frontend/src/types/domain.ts
- `Code` --references--> `KarmaLevel`  [INFERRED]
  docs/features/karma-points.md → frontend/src/types/domain.ts
- `Code` --references--> `KarmaToday`  [INFERRED]
  docs/features/karma-points.md → frontend/src/types/domain.ts

## Import Cycles
- None detected.

## Communities (120 total, 33 thin omitted)

### Community 0 - "ReplyContext"
Cohesion: 0.16
Nodes (19): importlib, Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile(), Any, Everything a reply template may personalise, built once per chat request., ReplyContext, _by_page(), _gap_lines() (+11 more)

### Community 1 - "AssessmentPage.tsx"
Cohesion: 0.06
Nodes (50): Code, In / out, Media (Video / Audio / YouTube) → Evidence-Cited Quiz, Pipeline, Setup, TODOs / edge cases, Verification, Practice ability (`main-lms-backend/services/practice_assessment.py`) (+42 more)

### Community 2 - "Code"
Cohesion: 0.06
Nodes (45): Code, Connections, In / out, Karma Points (gamification), Rules (`RULES` in `karma_engine.py`, served by `GET /karma/rules`), TODOs / edge cases, KarmaEventType, KarmaMonthlyUsage (+37 more)

### Community 3 - "router.py"
Cohesion: 0.08
Nodes (47): bcrypt, datetime, Code, jose, change_password(), _clear_refresh_cookie(), get_me(), login() (+39 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (43): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+35 more)

### Community 5 - "_get"
Cohesion: 0.13
Nodes (37): _get(), GET with retries — the dev backend runs with --reload and may restart mid-run,…, get_admin_roster(), get_assessment_outcomes(), get_competencies(), get_course_catalog(), get_crosswalk(), get_gsbpm_map() (+29 more)

### Community 6 - "Code"
Cohesion: 0.28
Nodes (6): Code, CertificateUploadZone(), CertificateExtractionResult, DocumentExtractorService, ExtractedCompetency, BaseModel

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.08
Nodes (45): `frontend/src/`, Code, GyanBot(), GyanHero(), LanguageMenu(), LanguageMenuProps, CAPABILITIES, ChatWidget() (+37 more)

### Community 8 - "UserAuth"
Cohesion: 0.12
Nodes (33): AuthBase, Connections, fastapi_concurrency, get_current_user(), Session, Decodes the Bearer JWT, looks up the user in auth.db. Raises HTTP 401 for any…, UserAuth, _ensure_can_view() (+25 more)

### Community 9 - "KarmaRewardsView.tsx"
Cohesion: 0.09
Nodes (27): TODOs / edge cases, CareerCard(), KarmaCard(), milestones, MilestoneStep, MilestoneStepper(), PassbookRow(), PILL_ORDER (+19 more)

### Community 10 - "AdminDashboard.tsx"
Cohesion: 0.13
Nodes (26): Code, AdminDashboard, StatCard(), AdminKPIs, AdminRosterRow, GAP_COLORS, HeatmapEntry, levelToNumber() (+18 more)

### Community 11 - "pipeline.py"
Cohesion: 0.11
Nodes (23): argparse, csv, main(), FILE: scripts/eval_media_quiz.py…, caption_regions(), needs_vlm(), Media → quiz pipeline (video, audio, YouTube) for the Assessment Studio. Entry…, MediaSource (+15 more)

### Community 12 - "baseline_assembler.py"
Cohesion: 0.13
Nodes (27): Code, get_learning_pathway(), Step-by-step learning paths. For every role competency: one course per FRAC…, rows_for(), tag_id(), _education_score(), enrollment_course_id(), is_completed() (+19 more)

### Community 13 - "insights.py"
Cohesion: 0.13
Nodes (21): capability_risk(), _frac_names(), gsbpm_scope(), prerequisite_dag(), post, routers/insights.py — admin-only SCIL v6 workforce insights Every number here…, Rebuild the workforce snapshot now (≈ a few seconds)., Per statistical product: capable officials per critical competency, retirements… (+13 more)

### Community 14 - "Timeline"
Cohesion: 0.15
Nodes (8): Interpreter guard for subcommands, build_chunks(), Evidence, _make_chunk(), FILE: services/media_quiz/evidence.py…, slide_windows: [{"t_start", "t_end", "evidence_ids": [ocr/vlm ids of that…, _tag(), Timeline

### Community 15 - "BaseModel"
Cohesion: 0.14
Nodes (13): field_validator, CompetencyOut, ContentStateRequest, _course_by_id(), CourseOut, get_content_state(), JobProfileOut, BaseModel (+5 more)

### Community 16 - "question_gen.py"
Cohesion: 0.18
Nodes (21): Chunk, fmt_ts(), fact_check(), _match(), protect_terms(), FILE: services/media_quiz/fact_check.py…, _reference(), restore_terms() (+13 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents) (+15 more)

### Community 18 - "HybridRecommendationEngine"
Cohesion: 0.10
Nodes (21): 3. Core data flow, Code, Connections, HybridRecommendationEngine, absorb(), add_step(), advance(), open_ladders() (+13 more)

### Community 19 - "test_pathway.py"
Cohesion: 0.08
Nodes (25): _edge(), _gap(), _kinds_levels(), Skill-gap levels + level-aware recommendations + learning pathways. Runs on a…, _resolved(), test_already_met_prerequisite_changes_nothing(), test_beginner_gets_next_levels_in_order_never_advanced_or_basic(), test_completed_never_suggested_and_in_progress_is_continued() (+17 more)

### Community 20 - "domain.ts"
Cohesion: 0.05
Nodes (45): DEFER_REASON, KIND_STYLE, PathwayLadder(), COLORS, LearningSnapshot(), Props, MyCoursesView(), MyCoursesViewProps (+37 more)

### Community 21 - "extractors.py"
Cohesion: 0.10
Nodes (37): capabilities(), JSONResponse, add_captions(), flush(), _budget(), describe_keyframes(), guarded(), run_batch() (+29 more)

### Community 22 - "media_io.py"
Cohesion: 0.12
Nodes (26): YouTube, Caption, _change(), download_youtube(), fetch(), is_youtube_url(), Keyframe, load_audio() (+18 more)

### Community 23 - "rag.py"
Cohesion: 0.11
Nodes (36): Code, Assessment, Competency, CompetencyProfile, UserCompetency, _chunk_document_text(), _clean_text(), _detect_skill_name() (+28 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "ai_tools.py"
Cohesion: 0.10
Nodes (30): Code, is_ollama_available(), Fast, synchronous check — just hits the Ollama /api/tags endpoint. Returns True…, FILE: ai/seed_knowledge.py…, Embeds all baseline knowledge into ChromaDB., seed(), add_documents_from_file(), add_text_to_store() (+22 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "_process"
Cohesion: 0.29
Nodes (11): MediaMetadata, MediaQuizQuestion, MediaQuizResponse, _process(), BaseModel, post, UploadFile, upload_media() (+3 more)

### Community 28 - "proficiency_service.py"
Cohesion: 0.07
Nodes (56): Cold start for UNASSESSED competencies, Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8), Foresight, Proficiency belief with dated decay, iGOT profile competencyLevel ('Level 3') → 3; missing → 0 (no claim)., Profile + enrollments + EvidenceLog → one resolved row per role competency.…, _resolve_competency_state(), _self_reported_level() (+48 more)

### Community 29 - "1. Runtime topology"
Cohesion: 0.12
Nodes (17): 1. Runtime topology, Connections, Gyan — Multilingual Chat Assistant, In / out, TODOs / edge cases, AI Course Recommendation Engine + Learning Pathways, In / out, TODOs / edge cases (+9 more)

### Community 30 - "CompetencyCalculator"
Cohesion: 0.22
Nodes (8): CompetencyCalculator, datetime, FILE: main-lms-backend/services/competency_service.py…, Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, Maps FRAC types from the JSON to calculation categories., test_missing_channels_do_not_drag_the_score_to_zero(), math

### Community 31 - "react"
Cohesion: 0.06
Nodes (54): Connections, In / out, Learner Dashboard (frontend shell), Visual design system (shared by every page), App(), DashboardRedirect(), TokenBridge(), AshokaChakra() (+46 more)

### Community 32 - "chatbot.py"
Cohesion: 0.22
Nodes (19): ChatResponse, _intent_response(), _intercept(), FILE: routers/chatbot.py Multilingual AI Learning Assistant — Gyan (ज्ञान)…, Deterministic handling of English commands the classifier has historically…, _response(), _theme_action(), _ui_action_response() (+11 more)

### Community 33 - "opportunity"
Cohesion: 0.24
Nodes (13): opportunity(), Any, services/gsbpm_service.py — GSBPM scoping (SCIL v6 §1) + opportunity to…, Opportunity to practise a competency in the official's office this cycle (SCIL…, Which competencies are in scope under the officer-hours rule, and why., scope_report(), _sp_name(), subprocess_hours() (+5 more)

### Community 34 - "_seed_officials"
Cohesion: 0.22
Nodes (10): _derive_password(), _fetch_officials(), main(), Session, Insert the hardcoded admin user. Returns True if inserted, False if already…, Default password = lowercase(firstName) + last 2 digits of the numeric userId…, Call the mock iGOT server's admin roster endpoint., Insert learner rows. Returns (inserted, skipped). (+2 more)

### Community 35 - "speech.d.ts"
Cohesion: 0.20
Nodes (6): SpeechRecognition, SpeechRecognitionEvent, SpeechRecognitionResult, SpeechRecognitionResultItem, SpeechRecognitionResultList, Window

### Community 36 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 37 - "resolve_level"
Cohesion: 0.35
Nodes (13): Single source of truth for an official's level on one competency. Every…, resolve_level(), _assess(), SCIL v6 §3 evidence channels K/A/U/S (knowledge, application, utility,…, _row(), test_confirmed_use_is_a_floor_unconfirmed_is_not(), test_failed_work_sample_is_evidence_but_not_a_floor(), test_knowledge_only_score_is_unchanged() (+5 more)

### Community 38 - "test_practice_assessment.py"
Cohesion: 0.18
Nodes (12): link_competency(), Pick which of the learner's ROLE competencies this quiz is evidence for. 1. the…, _tokens(), _one(), _profile(), Quiz → skill-gap bridge: difficulty-aware ability update, weighted score,…, test_failed_quiz_lowers_skill_score_and_passed_quiz_raises_it(), test_link_by_frac_tag() (+4 more)

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
Cohesion: 0.15
Nodes (11): Authentication & RBAC, In / out, Shared database (Neon), Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server + mock data), TODOs / edge cases, Connections (+3 more)

### Community 43 - "main_backup.py"
Cohesion: 0.07
Nodes (36): fastapi_middleware_cors, get_achievements(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments(), get_enrollments_by_user_id(), get_profile_by_user_id(), get_recommendations() (+28 more)

### Community 44 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 45 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 46 - "test_mock_data.py"
Cohesion: 0.06
Nodes (17): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only, Any, _read_disk(), data(), files(), fixture (+9 more)

### Community 49 - "models/models.py"
Cohesion: 0.16
Nodes (21): 7. Mismatches between the mermaid diagram and the code, Base, Conventions, TODOs / edge cases, enum, Admin, AssessmentSkillMapping, BaseUser (+13 more)

### Community 58 - "DashboardCreator"
Cohesion: 0.16
Nodes (4): AdminDashboardCreator, DashboardCreator, OfficialDashboardCreator, TrainerDashboardCreator

### Community 60 - "test_chat_messages.py"
Cohesion: 0.23
Nodes (11): Loads a language's template table on first use ("or" lives in or_.py; `or` is a…, templates(), _alternatives(), _fields(), parametrize, Catalogue completeness: every language has every template, placeholders are…, test_every_intent_renders(), test_placeholders_match_english() (+3 more)

### Community 61 - "prerequisite_service.py"
Cohesion: 0.13
Nodes (25): find_cycle(), infer_edges(), _node(), _norm_sf(), _ols(), Any, ndarray, services/prerequisite_service.py — cross-competency prerequisite DAG (SCIL v6… (+17 more)

### Community 62 - "main-lms-backend/main.py"
Cohesion: 0.06
Nodes (38): asyncio, fastapi, fastapi_security, json, get_db(), Yields a database session and ensures it is closed after the request., auth/dependencies.py…, Returns a FastAPI dependency that checks the current user's role. Example:… (+30 more)

### Community 63 - "MockIgotAdapter"
Cohesion: 0.13
Nodes (14): Cross-competency prerequisite DAG (SCIL v6 §5, B4), GSBPM scope — the 80% officer-hours rule (SCIL v6 §1), TODOs / limits, Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight), MockIgotAdapter, Forget every cached read for this user., GET a Sunbird endpoint and return its `result` object., GET /api/gsbpm/v1/map — GSBPM sub-processes + competency → sub-processes. (+6 more)

### Community 64 - "test_irt.py"
Cohesion: 0.13
Nodes (23): DiagnosticSessions, fisher_information(), laplace_posterior(), next_item(), p_correct(), public_item(), Any, services/irt_service.py — Tier-1 Bayesian 2PL posterior + adaptive diagnostic… (+15 more)

### Community 65 - "api.ts"
Cohesion: 0.06
Nodes (55): AGENDA_TYPE, CapabilityRiskPanel(), ForesightPanel(), GsbpmScopePanel(), pct(), PrerequisitePanel(), PRIORITY_CHIP, RISK_CHIP (+47 more)

### Community 66 - "probe.py"
Cohesion: 0.24
Nodes (11): dataclasses, get_ocr(), probe(), ProbeResult, ndarray, FILE: services/media_quiz/probe.py…, `regions` — precomputed speech spans (e.g. from YouTube captions) instead of…, Shared RapidOCR engine (PaddleOCR det/cls/rec models on ONNX Runtime). (+3 more)

### Community 67 - "generate_mock_data.py"
Cohesion: 0.07
Nodes (58): _batch(), build_acbp(), build_catalog(), build_crosswalk(), build_enrollments(), build_frac(), build_gsbpm_map(), build_hrms() (+50 more)

### Community 68 - "engine"
Cohesion: 0.19
Nodes (13): Reference data loading, on_event, Create users_auth table if it doesn't exist yet., _startup(), _course(), engine(), _frac(), fixture (+5 more)

### Community 69 - "Any"
Cohesion: 0.13
Nodes (12): ILearningPlatformAdapter, ABC, Any, The full CBP course catalogue, paged through POST /api/composite/v1/search.…, POST /api/composite/v1/search — Sunbird composite search, every page. `filters`…, Legacy method that maps fetch_user_enrollments to the old simple-mock shape.…, Interface for external learning platform integration. All concrete adapters…, Return the full CBP course catalog. (+4 more)

### Community 70 - "_warm_up"
Cohesion: 0.20
Nodes (9): AbstractEventLoop, Measured uplift → coverage learning + training effectiveness (SCIL v6 §6, B5), Workforce snapshot, _build_workforce_snapshot(), Everything slow, off the request path, on the "warm-up" thread's own loop so…, Every official's resolved competency rows, for the SCIL v6 population / cohort…, _warm_up(), _snapshot_after_schema() (+1 more)

### Community 71 - "LearnerDashboard.tsx"
Cohesion: 0.06
Nodes (46): Code, Opportunity to practise (SCIL v6 §4), LearnerDashboard, AssessmentUploadZone(), AssessmentUploadZoneProps, CompetencyOverviewTable(), LevelPips(), priorityOf() (+38 more)

### Community 72 - "upload_certificate"
Cohesion: 0.22
Nodes (9): Noticed but out of scope (not fixed), calculate_baseline(), EvidencePayload, BaseModel, post, UploadFile, Calculates the skill baseline score b_k ∈ [0, 5] using the locked 6-term…, Accepts a PDF certificate or resume from the React frontend. Extracts text →… (+1 more)

### Community 76 - "recommendation_service.py"
Cohesion: 0.08
Nodes (25): _course_summary(), _CourseDoc, _diagnostic_step(), _fmt_levels(), GapEntry, _interleave_by_level(), BaseModel, ndarray (+17 more)

### Community 77 - "_sunbird_result"
Cohesion: 0.25
Nodes (5): GET /api/frac/competencies — the catalogue FRAC set incl. L1–L5 descriptors., GET /api/frac/v1/crosswalk — iGOT dictionary CID id → catalogue FRAC id., GET /api/admin/v1/users Returns: result.users — full list of officials., Safely drill into a Sunbird envelope: data['result']['key1']['key2']..., _sunbird_result()

### Community 87 - "language_service.py"
Cohesion: 0.24
Nodes (11): detect_chat_language(), detect_chat_variant(), detect_chat_variant_or_none(), _devanagari_language(), Small, offline language routing for Gyan chat. This deliberately does *not* use…, Supported ISO 639-1 code for a chat message., The variant the *text itself* signals, or None when it carries no signal. Plain…, Internal language variant: en, hi (Devanagari), hi_latn (romanized Hindi), mr,… (+3 more)

### Community 88 - "chat"
Cohesion: 0.20
Nodes (15): chat(), ChatHistoryItem, ChatRequest, detect_intent_keyword(), BaseModel, post, Multilingual AI Learning Assistant — Gyan (ज्ञान)., RecommendationContext (+7 more)

### Community 89 - "list_attempts"
Cohesion: 0.22
Nodes (8): _competency_rows(), list_attempts(), Any, _question_difficulties(), The learner's resolved role competencies (same rows the skill-gap view shows),…, Assessment Studio history: QuizAttempt rows joined with their practice evidence…, Per-question difficulty: the question's own tag, else the quiz's target…, _row_snapshot()

### Community 90 - "mock-igot-server/main.py"
Cohesion: 0.12
Nodes (21): contextlib, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history(), health() (+13 more)

### Community 91 - "Code"
Cohesion: 0.13
Nodes (16): AsyncClient, Code, _competencies(), fetch(), fetch(), fetch(), fetch(), _prof_detail() (+8 more)

### Community 92 - "_user_enrolments"
Cohesion: 0.50
Nodes (4): legacy_user_history(), Merge seed enrolments with any runtime mutations., ICatalogSync.fetchUserHistory() — consumed by MockIgotPlatformAdapter., _user_enrolments()

### Community 93 - "Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)"
Cohesion: 0.25
Nodes (7): 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator

### Community 94 - "os"
Cohesion: 0.08
Nodes (26): base64, dotenv, httpx, importlib_util, io, logging, adapters/igot_adapter.py — iGOT Platform Adapter…, FILE: ai/rag_engine.py… (+18 more)

### Community 95 - "mock_igot_server.py"
Cohesion: 0.09
Nodes (31): exception_handler, fastapi_responses, HTTPException, composite_search(), CompositeSearchRequest, _course_tags(), _enriched_view(), EnrolPayload (+23 more)

### Community 96 - "test_chat_endpoint.py"
Cohesion: 0.42
Nodes (8): fastapi_testclient, _chat(), parametrize, End-to-end /chat behaviour per language through the real multilingual…, test_dark_mode_action(), test_my_courses_navigation(), test_recommendations(), test_skill_gaps()

### Community 97 - "CourseRecommendation"
Cohesion: 0.23
Nodes (10): ChatWidgetProps, CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps, SOURCE_STYLES, matches(), Props (+2 more)

### Community 98 - "lifespan"
Cohesion: 0.33
Nodes (7): lifespan(), _load_json(), _load_json_from_dir(), Any, FastAPI, Load all datasets into memory once at startup, so no request touches the file…, Load a JSON file from ROOT_DIR. Raises RuntimeError on missing file.

### Community 99 - "semantic_engine.py"
Cohesion: 0.08
Nodes (40): difflib, hashlib, encode_cached(), get_embedder(), is_embedder_ready(), _load(), model_name(), onnx_model_dir() (+32 more)

### Community 100 - "mock_data_metrics.py"
Cohesion: 0.31
Nodes (9): collections, live_metrics(), _login(), main(), offline_metrics(), _pct(), Mock-data quality metrics — run before/after regenerating mock data. cd main-…, Admin bearer header; retried while the backend (--reload) restarts. (+1 more)

### Community 101 - "Admin Dashboard"
Cohesion: 0.50
Nodes (4): Admin Dashboard, Connections, In / out, TODOs / edge cases

### Community 102 - "authApi.ts"
Cohesion: 0.29
Nodes (10): AuthProvider(), mapRole(), extractError(), getMe(), login(), LoginResponse, logout(), refresh() (+2 more)

### Community 105 - "practice_assessment.py"
Cohesion: 0.14
Nodes (27): grade_quiz(), **Grade Quiz → Skill Gap** - user_id comes from the JWT…, Sync DB work for /grade (runs in a worker thread). First submission of a quiz →…, _record_attempt(), bump(), latest_practice_value(), media_question_difficulty(), next_difficulty() (+19 more)

### Community 108 - "relevance.py"
Cohesion: 0.17
Nodes (10): Before / after metrics, Could not do / blocked, Decisions log (made without the user), SCIL v6 — mock data + blocked features: progress report, Status, functools, competency_name(), frac_competencies() (+2 more)

### Community 109 - "EvidenceLog"
Cohesion: 0.16
Nodes (13): Certificate / Resume Evidence Extraction, Connections, In / out, TODOs / edge cases, Connections, In / out, Skill Gap Analysis (evidence-based competency baselines), TODOs / edge cases (+5 more)

### Community 111 - "Ollama RAG Knowledge Base (Tier 3 — disconnected)"
Cohesion: 0.22
Nodes (8): Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, build_system_prompt(), generate_chat_response(), Runs the full RAG pipeline: 1. Retrieve top-k relevant document chunks from…, Builds a rich system prompt that grounds the LLM in the user's live context.…

### Community 119 - "estimate_uplift"
Cohesion: 0.17
Nodes (19): estimate_uplift(), _features(), _ipw(), Any, ndarray, services/uplift_service.py — measured course uplift (SCIL v6 §6 coverage…, [1, z, z², tenure/10, statistics degree] with z = preθ − (level − 0.5): takers…, Newton–Raphson for an L2-penalised logistic regression (intercept unpenalised). (+11 more)

### Community 126 - "CLAUDE.md — index & router"
Cohesion: 0.40
Nodes (5): CLAUDE.md — index & router, Feature index, graphify, How to use these docs, Run commands

### Community 128 - "_Embedder"
Cohesion: 0.10
Nodes (12): Code, Connections, In / out, Shared Embedder (chat + catalog roles), TODOs / edge cases, _Embedder, _OnnxEmbedder, ndarray (+4 more)

## Knowledge Gaps
- **254 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+249 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 826 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Code` connect `ChatWidget.tsx` to `chatbot.py`, `semantic_engine.py`, `engine`, `language_service.py`, `chat`, `1. Runtime topology`, `react`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Why does `Code` connect `HybridRecommendationEngine` to `api.ts`, `opportunity`, `_warm_up`, `LearnerDashboard.tsx`, `UserAuth`, `BaselineAssembler`, `baseline_assembler.py`, `recommendation_service.py`, `domain.ts`, `estimate_uplift`, `1. Runtime topology`, `MockIgotAdapter`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `HybridRecommendationEngine` connect `HybridRecommendationEngine` to `_Embedder`, `semantic_engine.py`, `mock_data_metrics.py`, `engine`, `_warm_up`, `recommendation_service.py`, `relevance.py`, `models/models.py`, `Code`, `main-lms-backend/main.py`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 48 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 45 inferred relationships involving `Code` (e.g. with `KarmaCard()` and `formatPoints()`) actually correct?**
  _`Code` has 45 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `HybridRecommendationEngine` (e.g. with `7. Mismatches between the mermaid diagram and the code` and `Code`) actually correct?**
  _`HybridRecommendationEngine` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _254 weakly-connected nodes found - possible documentation gaps or missing edges._