# Graph Report - SIH_IGot  (2026-09-19)

## Corpus Check
- 214 files · ~4,905,207 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .css 1, .example 1)

## Summary
- 2152 nodes · 4901 edges · 121 communities (86 shown, 35 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 564 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e5218726`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ReplyContext
- AssessmentPage.tsx
- Code
- router.py
- package.json
- _get
- os
- ChatWidget.tsx
- karma.py
- KarmaRewardsView.tsx
- AdminDashboard.tsx
- useLearnerDashboard.ts
- baseline_assembler.py
- insights.py
- pipeline.py
- BaseModel
- useScreenReader.ts
- What You Must Do When Invoked
- .build_study_plan
- test_pathway.py
- domain.ts
- extractors.py
- media_io.py
- opportunity
- compilerOptions
- ai_tools.py
- 🇮🇳 MoSPI Skill Intelligence Platform
- media_quiz.py
- test_proficiency_foresight.py
- _warm_up
- CompetencyCalculator
- react
- chatbot.py
- proficiency_service.py
- seed.py
- speech.d.ts
- graphify reference: extra exports and benchmark
- resolve_level
- 3. Core data flow
- compilerOptions
- _normalise_course_map
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
- DashboardCreator
- test_chat_messages.py
- estimate_uplift
- UserAuth
- MockIgotAdapter
- test_irt.py
- api.ts
- probe.py
- generate_mock_data.py
- engine
- ILearningPlatformAdapter
- workforce_service.py
- LearnerDashboard.tsx
- get_enriched_courses
- faker
- services_chat_messages
- services_chat_messages_context
- Any
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
- Code
- test_reply_regression.py
- chat_actions.py
- mock-igot-server/main.py
- Any
- _user_enrolments
- HybridRecommendationEngine
- .fetch_frac_competencies
- mock_igot_server.py
- test_chat_endpoint.py
- CourseRecommendation
- Code
- recommendation_service.py
- mock_data_metrics.py
- Code
- authApi.ts
- 1. Runtime topology
- _PrerequisiteGate
- Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)
- dependencies.py
- _resolve_competency_state
- Decisions log (made without the user)
- decay
- health
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
3. `Code` - 46 edges
4. `react` - 43 edges
5. `HybridRecommendationEngine` - 39 edges
6. `MockIgotAdapter` - 38 edges
7. `Code` - 37 edges
8. `ReplyContext` - 30 edges
9. `Code` - 30 edges
10. `Timeline` - 29 edges

## Surprising Connections (you probably didn't know these)
- `Code` --references--> `StatTone`  [INFERRED]
  docs/features/learner-dashboard.md → frontend/src/components/shell/StatCard.tsx
- `Code` --references--> `StudioTab`  [INFERRED]
  docs/features/rag-quiz-generator.md → frontend/src/pages/AssessmentPage.tsx
- `7. Mismatches between the mermaid diagram and the code` --references--> `SkillGapReport`  [INFERRED]
  ARCHITECTURE.md → frontend/src/types/domain.ts
- `Code` --references--> `KarmaLevel`  [INFERRED]
  docs/features/karma-points.md → frontend/src/types/domain.ts
- `Code` --references--> `KarmaToday`  [INFERRED]
  docs/features/karma-points.md → frontend/src/types/domain.ts

## Import Cycles
- None detected.

## Communities (121 total, 35 thin omitted)

### Community 0 - "ReplyContext"
Cohesion: 0.16
Nodes (19): importlib, Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile(), Any, Everything a reply template may personalise, built once per chat request., ReplyContext, _by_page(), _gap_lines() (+11 more)

### Community 1 - "AssessmentPage.tsx"
Cohesion: 0.12
Nodes (29): Code, AssessmentPage, CONTENT_LABEL, MediaAnalysisCard(), MediaAnswerReview(), pct(), QuestionEvidence(), SOURCE_LABEL (+21 more)

### Community 2 - "Code"
Cohesion: 0.06
Nodes (49): Code, Connections, In / out, Karma Points (gamification), Rules (`RULES` in `karma_engine.py`, served by `GET /karma/rules`), TODOs / edge cases, _create_schema(), _create() (+41 more)

### Community 3 - "router.py"
Cohesion: 0.08
Nodes (47): bcrypt, datetime, Code, TokenBridge(), registerLogoutCallback(), setApiToken(), hashlib, jose (+39 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (42): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+34 more)

### Community 5 - "_get"
Cohesion: 0.13
Nodes (36): _get(), GET with retries — the dev backend runs with --reload and may restart mid-run,…, get_assessment_outcomes(), get_competencies(), get_course_catalog(), get_crosswalk(), get_gsbpm_map(), get_hrms_officials() (+28 more)

### Community 6 - "os"
Cohesion: 0.13
Nodes (16): asyncio, Code, CertificateUploadZone(), adapters/igot_adapter.py — iGOT Platform Adapter…, FILE: ai/rag_engine.py…, FILE: main-lms-backend/routers/competency.py…, services/app_state.py — process-wide singletons built in main._warm_up…, CertificateExtractionResult (+8 more)

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.08
Nodes (47): `frontend/src/`, GyanBot(), GyanHero(), LanguageMenu(), LanguageMenuProps, CAPABILITIES, ChatWidget(), MessageBubble() (+39 more)

### Community 8 - "karma.py"
Cohesion: 0.19
Nodes (22): fastapi_concurrency, admin_adjust_karma(), AdminAdjustRequest, _assert_self_or_admin(), award_karma_event(), _award_response(), CbpClaimRequest, claim_cbp_bonus() (+14 more)

### Community 9 - "KarmaRewardsView.tsx"
Cohesion: 0.10
Nodes (22): KarmaCard(), milestones, MilestoneStep, PassbookRow(), PILL_ORDER, RightSidebarProps, EVENT_META, formatPoints() (+14 more)

### Community 10 - "AdminDashboard.tsx"
Cohesion: 0.09
Nodes (32): Code, AdminDashboard, SectionAction(), SectionCard(), SectionCardProps, StatCard(), StatCardProps, StatTone (+24 more)

### Community 11 - "useLearnerDashboard.ts"
Cohesion: 0.11
Nodes (20): Connections, In / out, Learner Dashboard (frontend shell), TODOs / edge cases, CareerCard(), MilestoneStepper(), RightSidebar(), _cache (+12 more)

### Community 12 - "baseline_assembler.py"
Cohesion: 0.15
Nodes (25): Code, rows_for(), tag_id(), _education_score(), enrollment_course_id(), is_completed(), _last_evidence_date(), _map_category() (+17 more)

### Community 13 - "insights.py"
Cohesion: 0.14
Nodes (19): capability_risk(), _frac_names(), prerequisite_dag(), post, routers/insights.py — admin-only SCIL v6 workforce insights Every number here…, Rebuild the workforce snapshot now (≈ a few seconds)., Per statistical product: capable officials per critical competency, retirements…, 36-month projection of expected capable officials: attrition × dated skill… (+11 more)

### Community 14 - "pipeline.py"
Cohesion: 0.07
Nodes (46): Interpreter guard for subcommands, csv, dataclasses, main(), FILE: scripts/eval_media_quiz.py…, build_chunks(), Chunk, Evidence (+38 more)

### Community 15 - "BaseModel"
Cohesion: 0.10
Nodes (22): field_validator, CompetencyOut, CompositeSearchRequest, ContentStateRequest, _course_by_id(), CourseOut, EnrolPayload, get_content_state() (+14 more)

### Community 16 - "useScreenReader.ts"
Cohesion: 0.53
Nodes (5): chunkText(), extractReadableText(), isHidden(), ScreenReader, useScreenReader()

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents) (+15 more)

### Community 18 - ".build_study_plan"
Cohesion: 0.25
Nodes (6): absorb(), add_step(), advance(), open_ladders(), Orders the required rungs of several pathways into one sequence. SCIL v6 §5…, Does taking `course_id` complete this ladder's next rung?

### Community 19 - "test_pathway.py"
Cohesion: 0.08
Nodes (25): _edge(), _gap(), _kinds_levels(), Skill-gap levels + level-aware recommendations + learning pathways. Runs on a…, _resolved(), test_already_met_prerequisite_changes_nothing(), test_beginner_gets_next_levels_in_order_never_advanced_or_basic(), test_completed_never_suggested_and_in_progress_is_continued() (+17 more)

### Community 20 - "domain.ts"
Cohesion: 0.06
Nodes (37): DEFER_REASON, KIND_STYLE, PathwayLadder(), formatDate(), ProfileHeader(), ProfileHeaderProps, TAGLINE, AppliedPrerequisite (+29 more)

### Community 21 - "extractors.py"
Cohesion: 0.07
Nodes (48): base64, functools, capabilities(), JSONResponse, flush(), _budget(), caption_regions(), describe_keyframes() (+40 more)

### Community 22 - "media_io.py"
Cohesion: 0.13
Nodes (24): Caption, _change(), download_youtube(), fetch(), is_youtube_url(), Keyframe, load_audio(), MediaInputError (+16 more)

### Community 23 - "opportunity"
Cohesion: 0.18
Nodes (15): gsbpm_scope(), SCIL v6 §1 — the 80% officer-hours scoping report (whole NSO, or one office)., opportunity(), Any, services/gsbpm_service.py — GSBPM scoping (SCIL v6 §1) + opportunity to…, Opportunity to practise a competency in the official's office this cycle (SCIL…, Which competencies are in scope under the officer-hours rule, and why., scope_report() (+7 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "ai_tools.py"
Cohesion: 0.07
Nodes (41): Code, Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, dotenv, io, build_system_prompt() (+33 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "media_quiz.py"
Cohesion: 0.27
Nodes (13): importlib_util, MediaMetadata, MediaQuizQuestion, MediaQuizResponse, _process(), BaseModel, post, UploadFile (+5 more)

### Community 28 - "test_proficiency_foresight.py"
Cohesion: 0.21
Nodes (15): cohort_prior(), population_stats(), Cohort prior for an UNASSESSED competency, with the divergence check., comp → (μ_pop, σ_pop, n) over officials with assessed evidence on it., _hrms(), _official(), SCIL v6 §2 dated decay / expected-shortfall / cold start, and §11 workforce…, _snap() (+7 more)

### Community 29 - "_warm_up"
Cohesion: 0.18
Nodes (11): AbstractEventLoop, Workforce snapshot, _build_workforce_snapshot(), Everything slow, off the request path, on the "warm-up" thread's own loop so…, Every official's resolved competency rows, for the SCIL v6 population / cohort…, _warm_up(), _snapshot_after_schema(), Any (+3 more)

### Community 30 - "CompetencyCalculator"
Cohesion: 0.22
Nodes (8): CompetencyCalculator, datetime, FILE: main-lms-backend/services/competency_service.py…, Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, Maps FRAC types from the JSON to calculation categories., test_missing_channels_do_not_drag_the_score_to_zero(), math

### Community 31 - "react"
Cohesion: 0.10
Nodes (35): Visual design system (shared by every page), App(), DashboardRedirect(), AshokaChakra(), CountUp(), GovEmblem(), Reveal(), useInView() (+27 more)

### Community 32 - "chatbot.py"
Cohesion: 0.33
Nodes (15): ChatResponse, _intent_response(), _intercept(), FILE: routers/chatbot.py Multilingual AI Learning Assistant — Gyan (ज्ञान)…, Deterministic handling of English commands the classifier has historically…, _response(), _theme_action(), _ui_action_response() (+7 more)

### Community 33 - "proficiency_service.py"
Cohesion: 0.17
Nodes (17): cluster_of(), expected_shortfall(), months_between(), office_phase(), _phi(), _Phi(), proficiency_state(), Any (+9 more)

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
Cohesion: 0.25
Nodes (17): BaselineAssembler, Single source of truth for an official's level on one competency. Every…, resolve_level(), _assess(), SCIL v6 §3 evidence channels K/A/U/S (knowledge, application, utility,…, _row(), test_confirmed_use_is_a_floor_unconfirmed_is_not(), test_failed_work_sample_is_evidence_but_not_a_floor() (+9 more)

### Community 38 - "3. Core data flow"
Cohesion: 0.18
Nodes (12): 3. Core data flow, _ensure_can_view(), get_learning_pathway(), get_recommendations_by_user_id(), get_skill_gaps_by_user_id(), _learner_competency_state(), A learner may only read their own competency data; admins may read anyone's., Memoised _resolve_competency_state. Concurrent callers (the dashboard's /skill-… (+4 more)

### Community 39 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 42 - "CLAUDE.md"
Cohesion: 0.05
Nodes (33): CLAUDE.md — index & router, Feature index, graphify, How to use these docs, Run commands, Admin Dashboard, Connections, In / out (+25 more)

### Community 43 - "main-lms-backend/main.py"
Cohesion: 0.06
Nodes (42): fastapi_middleware_cors, get_achievements(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments_by_user_id(), get_profile_by_user_id(), get_recommendations_by_user_id(), get_skill_gaps_by_user_id() (+34 more)

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
Cohesion: 0.05
Nodes (74): 7. Mismatches between the mermaid diagram and the code, Base, Conventions, Authentication & RBAC, Connections, In / out, Shared database (Neon), TODOs / edge cases (+66 more)

### Community 58 - "DashboardCreator"
Cohesion: 0.16
Nodes (4): AdminDashboardCreator, DashboardCreator, OfficialDashboardCreator, TrainerDashboardCreator

### Community 60 - "test_chat_messages.py"
Cohesion: 0.23
Nodes (11): Loads a language's template table on first use ("or" lives in or_.py; `or` is a…, templates(), _alternatives(), _fields(), parametrize, Catalogue completeness: every language has every template, placeholders are…, test_every_intent_renders(), test_placeholders_match_english() (+3 more)

### Community 61 - "estimate_uplift"
Cohesion: 0.08
Nodes (43): find_cycle(), infer_edges(), _node(), _norm_sf(), _ols(), Any, ndarray, services/prerequisite_service.py — cross-competency prerequisite DAG (SCIL v6… (+35 more)

### Community 62 - "UserAuth"
Cohesion: 0.11
Nodes (25): AuthBase, get_db(), Yields a database session and ensures it is closed after the request., UserAuth, get_enrollments(), get_recommendations(), get_skill_gaps(), Skill Gap Engine: dynamically computes competency gaps from iGOT history.… (+17 more)

### Community 63 - "MockIgotAdapter"
Cohesion: 0.11
Nodes (15): Cross-competency prerequisite DAG (SCIL v6 §5, B4), GSBPM scope — the 80% officer-hours rule (SCIL v6 §1), TODOs / limits, Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight), MockIgotAdapter, Forget every cached read for this user., The full CBP course catalogue, paged through POST /api/composite/v1/search.…, POST /api/composite/v1/search — Sunbird composite search, every page. `filters`… (+7 more)

### Community 64 - "test_irt.py"
Cohesion: 0.13
Nodes (23): DiagnosticSessions, fisher_information(), laplace_posterior(), next_item(), p_correct(), public_item(), Any, services/irt_service.py — Tier-1 Bayesian 2PL posterior + adaptive diagnostic… (+15 more)

### Community 65 - "api.ts"
Cohesion: 0.08
Nodes (43): AGENDA_TYPE, CapabilityRiskPanel(), ForesightPanel(), GsbpmScopePanel(), pct(), PrerequisitePanel(), PRIORITY_CHIP, RISK_CHIP (+35 more)

### Community 66 - "probe.py"
Cohesion: 0.26
Nodes (11): VideoScan, get_ocr(), probe(), ProbeResult, ndarray, FILE: services/media_quiz/probe.py…, `regions` — precomputed speech spans (e.g. from YouTube captions) instead of…, Shared RapidOCR engine (PaddleOCR det/cls/rec models on ONNX Runtime). (+3 more)

### Community 67 - "generate_mock_data.py"
Cohesion: 0.07
Nodes (58): _batch(), build_acbp(), build_catalog(), build_crosswalk(), build_enrollments(), build_frac(), build_gsbpm_map(), build_hrms() (+50 more)

### Community 68 - "engine"
Cohesion: 0.19
Nodes (13): Reference data loading, on_event, Create users_auth table if it doesn't exist yet., _startup(), _course(), engine(), _frac(), fixture (+5 more)

### Community 69 - "ILearningPlatformAdapter"
Cohesion: 0.10
Nodes (15): 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator, ILearningPlatformAdapter (+7 more)

### Community 70 - "workforce_service.py"
Cohesion: 0.31
Nodes (13): _as_date(), capability_risk(), cell(), foresight(), _level(), _p_capable(), Any, date (+5 more)

### Community 71 - "LearnerDashboard.tsx"
Cohesion: 0.06
Nodes (49): Code, Opportunity to practise (SCIL v6 §4), LearnerDashboard, AssessmentUploadZone(), AssessmentUploadZoneProps, CompetencyOverviewTable(), LevelPips(), priorityOf() (+41 more)

### Community 72 - "get_enriched_courses"
Cohesion: 0.33
Nodes (7): composite_search(), _course_tags(), _enriched_view(), get_enriched_courses(), _matches_filters(), Sunbird-style filters: each key → value or list of accepted values., The catalogue in the older "enriched" shape. Query params:…

### Community 76 - "Any"
Cohesion: 0.16
Nodes (13): Measured uplift → coverage learning + training effectiveness (SCIL v6 §6, B5), _course_summary(), _diagnostic_step(), _fmt_levels(), _interleave_by_level(), Any, BaseModel, One rung of a ladder. Finishing an in-progress course beats starting a new one. (+5 more)

### Community 77 - "_sunbird_result"
Cohesion: 0.29
Nodes (5): fetch(), GET /api/frac/v1/crosswalk — iGOT dictionary CID id → catalogue FRAC id., GET /api/admin/v1/users Returns: result.users — full list of officials., Safely drill into a Sunbird envelope: data['result']['key1']['key2']..., _sunbird_result()

### Community 87 - "Code"
Cohesion: 0.12
Nodes (21): Code, classify_intent(), low_confidence_threshold(), Returns (best_intent, confidence). ("general", 0.0) if the embedder is…, chat(), detect_intent_keyword(), post, Multilingual AI Learning Assistant — Gyan (ज्ञान). (+13 more)

### Community 88 - "test_reply_regression.py"
Cohesion: 0.30
Nodes (10): ChatHistoryItem, ChatRequest, BaseModel, RecommendationContext, SkillGapContext, sample_request(), parametrize, English and Hinglish replies must match the pre-catalogue output, except… (+2 more)

### Community 89 - "chat_actions.py"
Cohesion: 0.50
Nodes (4): detect_ui_actions(), _mentions(), Detect website theme / language changes requested in any supported chat…, Returns (theme, language): theme in {"dark", "light", "toggle"}, language in…

### Community 90 - "mock-igot-server/main.py"
Cohesion: 0.12
Nodes (21): contextlib, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history(), health() (+13 more)

### Community 91 - "Any"
Cohesion: 0.17
Nodes (12): AsyncClient, fetch(), fetch(), fetch(), Any, Pooled client for the running loop — no new TCP connection per call., TTL memo for one user's read. Concurrent callers share one in-flight request;…, GET /api/evidence/v1/user/{id} — EvidenceLog-style workplace evidence rows ([]… (+4 more)

### Community 92 - "_user_enrolments"
Cohesion: 0.40
Nodes (5): get_admin_roster(), legacy_user_history(), Merge seed enrolments with any runtime mutations., ICatalogSync.fetchUserHistory() — consumed by MockIgotPlatformAdapter., _user_enrolments()

### Community 93 - "HybridRecommendationEngine"
Cohesion: 0.17
Nodes (12): Before / after metrics, GapEntry, HybridRecommendationEngine, ndarray, Singleton — built ONCE at app startup. Holds FAISS index + BM25 corpus in…, FRAC levels at which the catalogue has at least one course for comp_id., Computes and prioritizes skill gaps. priority_k = gap_k * (target_k / 5.0)…, (query embedding, BM25 scores over the whole corpus), cached. (+4 more)

### Community 94 - ".fetch_frac_competencies"
Cohesion: 0.18
Nodes (10): Noticed but out of scope (not fixed), GET /api/frac/competencies — the catalogue FRAC set incl. L1–L5 descriptors., calculate_baseline(), EvidencePayload, BaseModel, post, UploadFile, Calculates the skill baseline score b_k ∈ [0, 5] using the locked 6-term… (+2 more)

### Community 95 - "mock_igot_server.py"
Cohesion: 0.11
Nodes (22): exception_handler, fastapi_responses, HTTPException, health(), http_exc_handler(), legacy_catalog(), legacy_frac(), legacy_job_profiles() (+14 more)

### Community 96 - "test_chat_endpoint.py"
Cohesion: 0.36
Nodes (9): fastapi_testclient, _chat(), parametrize, End-to-end /chat behaviour per language through the real multilingual…, test_dark_mode_action(), test_my_courses_navigation(), test_recommendations(), test_skill_gaps() (+1 more)

### Community 97 - "CourseRecommendation"
Cohesion: 0.23
Nodes (10): ChatWidgetProps, CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps, SOURCE_STYLES, matches(), Props (+2 more)

### Community 98 - "Code"
Cohesion: 0.13
Nodes (11): Code, Connections, _CourseDoc, _parse_level(), The id whose FRAC tags / levels / official text drive retrieval., Bayesian shrinkage toward global prior mean. Returns None if either input is…, Level 3' / 3 / '3' → 3; anything outside 1..5 → None., {courseId: {compId: FRAC level}} — feeds BaselineAssembler so the Verified… (+3 more)

### Community 99 - "recommendation_service.py"
Cohesion: 0.06
Nodes (47): difflib, Code, json, logging, _Embedder, encode_cached(), get_embedder(), is_embedder_ready() (+39 more)

### Community 100 - "mock_data_metrics.py"
Cohesion: 0.13
Nodes (14): argparse, collections, httpx, Benchmark Gyan's intent classifier on the held-out multilingual set. python…, live_metrics(), _login(), main(), offline_metrics() (+6 more)

### Community 101 - "Code"
Cohesion: 0.29
Nodes (6): Code, _competencies(), _prof_detail(), GET /api/hrms/v1/officials — {officials{userId: DOB, superannuationDate,…, Safely read a field from profileDetails.professionalDetails[0]., Return the competencies list from profileDetails.competencies.

### Community 102 - "authApi.ts"
Cohesion: 0.27
Nodes (11): AuthProvider(), mapRole(), changePassword(), extractError(), getMe(), login(), LoginResponse, logout() (+3 more)

### Community 103 - "1. Runtime topology"
Cohesion: 0.25
Nodes (8): 1. Runtime topology, AI Course Recommendation Engine + Learning Pathways, In / out, TODOs / edge cases, on_event, Return at once so uvicorn binds the port; schema + warm-up run in the…, _readiness_gate(), _startup()

### Community 104 - "_PrerequisiteGate"
Cohesion: 0.33
Nodes (3): _PrerequisiteGate, Cross-competency prerequisite DAG for build_study_plan (SCIL v6 §5, B4). A rung…, Edges that changed or annotate the plan: ordered (waited, then met), blocked,…

### Community 105 - "Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)"
Cohesion: 0.50
Nodes (4): Cold start for UNASSESSED competencies, Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8), Foresight, Proficiency belief with dated decay

### Community 106 - "dependencies.py"
Cohesion: 0.18
Nodes (10): fastapi, fastapi_security, get_current_user(), Session, auth/dependencies.py…, Decodes the Bearer JWT, looks up the user in auth.db. Raises HTTP 401 for any…, Returns a FastAPI dependency that checks the current user's role. Example:…, require_role() (+2 more)

### Community 107 - "_resolve_competency_state"
Cohesion: 0.50
Nodes (4): iGOT profile competencyLevel ('Level 3') → 3; missing → 0 (no claim)., Profile + enrollments + EvidenceLog → one resolved row per role competency.…, _resolve_competency_state(), _self_reported_level()

### Community 108 - "Decisions log (made without the user)"
Cohesion: 0.29
Nodes (5): Could not do / blocked, Decisions log (made without the user), SCIL v6 — mock data + blocked features: progress report, Status, Catalogue duration in hours, or None for a course not in the catalogue.

### Community 109 - "decay"
Cohesion: 0.50
Nodes (4): decay(), (μ_t, σ_t, λ) — relax the belief toward the population prior as evidence ages., test_accuracy_skills_decay_faster_than_procedural(), test_decay_relaxes_toward_the_population_mean_not_zero()

## Knowledge Gaps
- **253 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+248 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 809 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `UserAuth` connect `UserAuth` to `seed.py`, `router.py`, `3. Core data flow`, `karma.py`, `dependencies.py`, `main-lms-backend/main.py`, `insights.py`, `rag.py`, `opportunity`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `Code` connect `Code` to `chatbot.py`, `recommendation_service.py`, `engine`, `ChatWidget.tsx`, `CLAUDE.md`, `test_reply_regression.py`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `Code` connect `Code` to `api.ts`, `karma.py`, `KarmaRewardsView.tsx`, `useLearnerDashboard.ts`, `rag.py`, `domain.ts`, `Any`, `UserAuth`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 45 inferred relationships involving `Code` (e.g. with `KarmaCard()` and `formatPoints()`) actually correct?**
  _`Code` has 45 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `HybridRecommendationEngine` (e.g. with `7. Mismatches between the mermaid diagram and the code` and `Code`) actually correct?**
  _`HybridRecommendationEngine` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _253 weakly-connected nodes found - possible documentation gaps or missing edges._