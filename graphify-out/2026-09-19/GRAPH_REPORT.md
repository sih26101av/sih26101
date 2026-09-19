# Graph Report - SIH_IGot  (2026-09-19)

## Corpus Check
- 214 files · ~4,905,207 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .css 1, .example 1)

## Summary
- 2162 nodes · 4863 edges · 135 communities (98 shown, 37 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 554 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ae901846`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ReplyContext
- AssessmentPage.tsx
- Code
- router.py
- package.json
- _require_auth
- typing
- ChatWidget.tsx
- karma.py
- KarmaRewardsView.tsx
- AdminDashboard.tsx
- pipeline.py
- baseline_assembler.py
- UserAuth
- Timeline
- BaseModel
- useScreenReader.ts
- What You Must Do When Invoked
- .build_study_plan
- test_pathway.py
- domain.ts
- extractors.py
- media_io.py
- Code
- compilerOptions
- os
- 🇮🇳 MoSPI Skill Intelligence Platform
- media_quiz.py
- proficiency_service.py
- 3. Core data flow
- CompetencyCalculator
- react
- chatbot.py
- karma_engine.py
- seed.py
- speech.d.ts
- graphify reference: extra exports and benchmark
- resolve_level
- get_learning_pathway
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
- rag.py
- .claude/CLAUDE.md
- extraction-spec.md
- DashboardCreator
- test_chat_messages.py
- prerequisite_service.py
- main-lms-backend/main.py
- Any
- test_irt.py
- api.ts
- probe.py
- generate_mock_data.py
- engine
- igot_adapter.py
- AwardResult
- LearnerDashboard.tsx
- get_enriched_courses
- faker
- services_chat_messages
- services_chat_messages_context
- RecommendationResult
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
- test_reply_regression.py
- chat_actions.py
- _get
- Code
- _user_enrolments
- HybridRecommendationEngine
- llm.py
- mock_igot_server.py
- test_chat_endpoint.py
- CourseCard.tsx
- Code
- embedder.py
- mock_data_metrics.py
- semantic_engine.py
- authApi.ts
- MockIgotAdapter
- _PrerequisiteGate
- grade_quiz
- dependencies.py
- ai_tools.py
- Decisions log (made without the user)
- EvidenceLog
- recommendation_service.py
- Ollama RAG Knowledge Base (Tier 3 — disconnected)
- Request
- .award_safe
- ingest_telemetry
- google_generativeai
- langchain_text_splitters
- mockdata
- pdfplumber
- relevance.py
- pptx
- pypdf
- requests
- .build_pathway
- Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)
- urllib_request
- CLAUDE.md — index & router
- RAG Document → Quiz Generator & Grading
- Shared Embedder (chat + catalog roles)
- .from_dir
- on_event
- JSONResponse
- date
- datetime

## God Nodes (most connected - your core abstractions)
1. `_get()` - 51 edges
2. `Code` - 46 edges
3. `react` - 43 edges
4. `HybridRecommendationEngine` - 39 edges
5. `MockIgotAdapter` - 38 edges
6. `Code` - 37 edges
7. `UserAuth` - 36 edges
8. `Code` - 30 edges
9. `ReplyContext` - 30 edges
10. `Timeline` - 29 edges

## Surprising Connections (you probably didn't know these)
- `Code` --references--> `KarmaLevel`  [INFERRED]
  docs/features/karma-points.md → frontend/src/types/domain.ts
- `Code` --references--> `KarmaToday`  [INFERRED]
  docs/features/karma-points.md → frontend/src/types/domain.ts
- `TODOs / edge cases` --references--> `EvidenceLog`  [INFERRED]
  docs/features/karma-points.md → main-lms-backend/models/models.py
- `Code` --references--> `LearningSnapshot()`  [INFERRED]
  docs/features/learner-dashboard.md → frontend/src/components/dashboard/LearningSnapshot.tsx
- `Code` --references--> `StatTone`  [INFERRED]
  docs/features/learner-dashboard.md → frontend/src/components/shell/StatCard.tsx

## Import Cycles
- None detected.

## Communities (135 total, 37 thin omitted)

### Community 0 - "ReplyContext"
Cohesion: 0.16
Nodes (19): importlib, Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile(), Any, Everything a reply template may personalise, built once per chat request., ReplyContext, _by_page(), _gap_lines() (+11 more)

### Community 1 - "AssessmentPage.tsx"
Cohesion: 0.09
Nodes (36): Code, In / out, Media (Video / Audio / YouTube) → Evidence-Cited Quiz, Pipeline, Setup, TODOs / edge cases, Verification, AssessmentPage (+28 more)

### Community 2 - "Code"
Cohesion: 0.15
Nodes (14): Code, KarmaEvent, KarmaMonthlyUsage, Immutable ledger entry — one row per karma point award event., Rolling monthly counter for non-CBP COURSE_COMPLETION events. Enforces the…, KarmaEngine, Session, Dispatches an eventType to its strategy, then applies the shared rules in… (+6 more)

### Community 3 - "router.py"
Cohesion: 0.09
Nodes (42): bcrypt, Code, jose, get_db(), Yields a database session and ensures it is closed after the request., change_password(), _clear_refresh_cookie(), login() (+34 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (43): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+35 more)

### Community 5 - "_require_auth"
Cohesion: 0.14
Nodes (29): get_assessment_outcomes(), get_course_catalog(), get_crosswalk(), get_gsbpm_map(), get_hrms_officials(), get_item_bank(), get_office(), get_offices() (+21 more)

### Community 6 - "typing"
Cohesion: 0.12
Nodes (19): Code, Noticed but out of scope (not fixed), CertificateUploadZone(), calculate_baseline(), EvidencePayload, BaseModel, post, UploadFile (+11 more)

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.08
Nodes (52): `frontend/src/`, Code, GyanBot(), GyanHero(), LanguageMenu(), LanguageMenuProps, CAPABILITIES, ChatWidget() (+44 more)

### Community 8 - "karma.py"
Cohesion: 0.19
Nodes (24): fastapi_concurrency, admin_adjust_karma(), AdminAdjustRequest, _assert_self_or_admin(), award_karma_event(), _award_response(), CbpClaimRequest, claim_cbp_bonus() (+16 more)

### Community 9 - "KarmaRewardsView.tsx"
Cohesion: 0.10
Nodes (26): KarmaCard(), milestones, MilestoneStep, PassbookRow(), PILL_ORDER, RightSidebarProps, EVENT_META, formatPoints() (+18 more)

### Community 10 - "AdminDashboard.tsx"
Cohesion: 0.08
Nodes (34): Code, AdminDashboard, PageHeader(), PageHeaderProps, SectionAction(), SectionCard(), SectionCardProps, StatCard() (+26 more)

### Community 11 - "pipeline.py"
Cohesion: 0.09
Nodes (32): csv, functools, main(), FILE: scripts/eval_media_quiz.py…, build_chunks(), slide_windows: [{"t_start", "t_end", "evidence_ids": [ocr/vlm ids of that…, fact_check(), _match() (+24 more)

### Community 12 - "baseline_assembler.py"
Cohesion: 0.15
Nodes (25): Code, rows_for(), tag_id(), _education_score(), enrollment_course_id(), is_completed(), _last_evidence_date(), _map_category() (+17 more)

### Community 13 - "UserAuth"
Cohesion: 0.13
Nodes (23): AuthBase, UserAuth, capability_risk(), _frac_names(), gsbpm_scope(), prerequisite_dag(), post, routers/insights.py — admin-only SCIL v6 workforce insights Every number here… (+15 more)

### Community 14 - "Timeline"
Cohesion: 0.13
Nodes (19): Interpreter guard for subcommands, dataclasses, Chunk, Evidence, fmt_ts(), _make_chunk(), FILE: services/media_quiz/evidence.py…, _tag() (+11 more)

### Community 15 - "BaseModel"
Cohesion: 0.13
Nodes (16): CompetencyOut, ContentStateRequest, _course_by_id(), CourseOut, EnrolPayload, get_content_state(), JobProfileOut, legacy_enroll_user() (+8 more)

### Community 16 - "useScreenReader.ts"
Cohesion: 0.53
Nodes (5): chunkText(), extractReadableText(), isHidden(), ScreenReader, useScreenReader()

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents) (+15 more)

### Community 18 - ".build_study_plan"
Cohesion: 0.21
Nodes (9): Cross-competency prerequisite DAG (SCIL v6 §5, B4), absorb(), add_step(), advance(), open_ladders(), Any, Orders the required rungs of several pathways into one sequence. SCIL v6 §5…, Does taking `course_id` complete this ladder's next rung? (+1 more)

### Community 19 - "test_pathway.py"
Cohesion: 0.08
Nodes (26): hashlib, _edge(), _gap(), _kinds_levels(), Skill-gap levels + level-aware recommendations + learning pathways. Runs on a…, _resolved(), test_already_met_prerequisite_changes_nothing(), test_beginner_gets_next_levels_in_order_never_advanced_or_basic() (+18 more)

### Community 20 - "domain.ts"
Cohesion: 0.05
Nodes (52): Code, Opportunity to practise (SCIL v6 §4), CompetencyOverviewTable(), LevelPips(), priorityOf(), Props, DEFER_REASON, KIND_STYLE (+44 more)

### Community 21 - "extractors.py"
Cohesion: 0.12
Nodes (24): add_captions(), flush(), _budget(), caption_regions(), get_whisper(), lang_of(), needs_vlm(), ocr_keyframes() (+16 more)

### Community 22 - "media_io.py"
Cohesion: 0.11
Nodes (26): YouTube, Caption, _change(), download_youtube(), fetch(), is_youtube_url(), Keyframe, load_audio() (+18 more)

### Community 23 - "Code"
Cohesion: 0.13
Nodes (25): Code, _chunk_document_text(), _clean_text(), DocumentMetadata, DocumentUploadResponse, ErrorResponse, _extract_pdf(), _extract_pptx() (+17 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "os"
Cohesion: 0.12
Nodes (22): Code, dotenv, logging, FILE: ai/rag_engine.py…, FILE: ai/seed_knowledge.py…, Embeds all baseline knowledge into ChromaDB., seed(), add_text_to_store() (+14 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "media_quiz.py"
Cohesion: 0.21
Nodes (16): fastapi_responses, importlib_util, MediaMetadata, MediaQuizQuestion, MediaQuizResponse, _process(), BaseModel, post (+8 more)

### Community 28 - "proficiency_service.py"
Cohesion: 0.06
Nodes (58): Cold start for UNASSESSED competencies, Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8), Foresight, Proficiency belief with dated decay, Workforce snapshot, iGOT profile competencyLevel ('Level 3') → 3; missing → 0 (no claim)., Profile + enrollments + EvidenceLog → one resolved row per role competency.…, _resolve_competency_state() (+50 more)

### Community 29 - "3. Core data flow"
Cohesion: 0.10
Nodes (23): AbstractEventLoop, 1. Runtime topology, 3. Core data flow, Connections, Gyan — Multilingual Chat Assistant, In / out, TODOs / edge cases, _build_workforce_snapshot() (+15 more)

### Community 30 - "CompetencyCalculator"
Cohesion: 0.22
Nodes (8): CompetencyCalculator, datetime, FILE: main-lms-backend/services/competency_service.py…, Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, Maps FRAC types from the JSON to calculation categories., test_missing_channels_do_not_drag_the_score_to_zero(), math

### Community 31 - "react"
Cohesion: 0.09
Nodes (39): Visual design system (shared by every page), App(), DashboardRedirect(), TokenBridge(), AshokaChakra(), CountUp(), GovEmblem(), Reveal() (+31 more)

### Community 32 - "chatbot.py"
Cohesion: 0.24
Nodes (20): chat(), ChatRequest, ChatResponse, detect_intent_keyword(), _intent_response(), _intercept(), post, FILE: routers/chatbot.py Multilingual AI Learning Assistant — Gyan (ज्ञान)… (+12 more)

### Community 33 - "karma_engine.py"
Cohesion: 0.14
Nodes (14): date, datetime, KarmaEventType, FixedPointsStrategy, ist_date(), ist_day_start_utc(), ist_now(), KarmaRule (+6 more)

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

### Community 38 - "get_learning_pathway"
Cohesion: 0.13
Nodes (22): _ensure_can_view(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments_by_user_id(), get_frac_competencies(), get_learning_pathway(), get_profile_by_user_id(), get_recommendations_by_user_id() (+14 more)

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
Cohesion: 0.22
Nodes (8): Admin Dashboard, Connections, In / out, TODOs / edge cases, Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server + mock data), TODOs / edge cases

### Community 43 - "main_backup.py"
Cohesion: 0.09
Nodes (30): fastapi_middleware_cors, get_achievements(), get_achievements_by_user_id(), get_enrollments(), get_enrollments_by_user_id(), get_profile_by_user_id(), get_recommendations_by_user_id(), get_skill_gaps_by_user_id() (+22 more)

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
Cohesion: 0.13
Nodes (28): 7. Mismatches between the mermaid diagram and the code, Base, Conventions, enum, SkillGapReport, Admin, Assessment, AssessmentSkillMapping (+20 more)

### Community 58 - "DashboardCreator"
Cohesion: 0.16
Nodes (4): AdminDashboardCreator, DashboardCreator, OfficialDashboardCreator, TrainerDashboardCreator

### Community 60 - "test_chat_messages.py"
Cohesion: 0.23
Nodes (11): Loads a language's template table on first use ("or" lives in or_.py; `or` is a…, templates(), _alternatives(), _fields(), parametrize, Catalogue completeness: every language has every template, placeholders are…, test_every_intent_renders(), test_placeholders_match_english() (+3 more)

### Community 61 - "prerequisite_service.py"
Cohesion: 0.06
Nodes (56): opportunity(), Any, services/gsbpm_service.py — GSBPM scoping (SCIL v6 §1) + opportunity to…, Opportunity to practise a competency in the official's office this cycle (SCIL…, Which competencies are in scope under the officer-hours rule, and why., scope_report(), _sp_name(), subprocess_hours() (+48 more)

### Community 62 - "main-lms-backend/main.py"
Cohesion: 0.09
Nodes (28): asyncio, fastapi, httpx, json, _level_to_int(), main.py — MoSPI LMS Backend API (Main Orchestrator)…, Level 3' → 3, 'Level 2' → 2, fallback → 2, answer() (+20 more)

### Community 63 - "Any"
Cohesion: 0.18
Nodes (8): Any, GET a Sunbird endpoint and return its `result` object., GET /api/org/v1/offices — {cycle, offices[{officeId, subprocesses[{id,…, GET /api/frac/v1/prerequisites — {count, edges[]} expert-seeded prerequisite…, GET /api/course/v1/assessment/outcomes — {outcomes[], comparisons[]} pre/post θ…, GET /api/assessment/v1/itembank — 2PL items incl. answer keys (server side…, GET /api/hrms/v1/officials — {officials{userId: DOB, superannuationDate,…, Return the full CBP course catalog.

### Community 64 - "test_irt.py"
Cohesion: 0.13
Nodes (23): DiagnosticSessions, fisher_information(), laplace_posterior(), next_item(), p_correct(), public_item(), Any, services/irt_service.py — Tier-1 Bayesian 2PL posterior + adaptive diagnostic… (+15 more)

### Community 65 - "api.ts"
Cohesion: 0.08
Nodes (40): AGENDA_TYPE, CapabilityRiskPanel(), ForesightPanel(), GsbpmScopePanel(), pct(), PrerequisitePanel(), PRIORITY_CHIP, RISK_CHIP (+32 more)

### Community 66 - "probe.py"
Cohesion: 0.27
Nodes (10): get_ocr(), probe(), ProbeResult, ndarray, FILE: services/media_quiz/probe.py…, `regions` — precomputed speech spans (e.g. from YouTube captions) instead of…, Shared RapidOCR engine (PaddleOCR det/cls/rec models on ONNX Runtime)., route() (+2 more)

### Community 67 - "generate_mock_data.py"
Cohesion: 0.07
Nodes (58): _batch(), build_acbp(), build_catalog(), build_crosswalk(), build_enrollments(), build_frac(), build_gsbpm_map(), build_hrms() (+50 more)

### Community 68 - "engine"
Cohesion: 0.21
Nodes (12): on_event, Create users_auth table if it doesn't exist yet., _startup(), _course(), engine(), _frac(), fixture, Hashed bag-of-words → L2-normalised vector. Shared words ⇒ positive cosine. (+4 more)

### Community 69 - "igot_adapter.py"
Cohesion: 0.09
Nodes (19): 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator, _competencies() (+11 more)

### Community 70 - "AwardResult"
Cohesion: 0.14
Nodes (12): AdminAdjustmentStrategy, AwardResult, CompletionKarmaStrategy, IKarmaStrategy, ABC, Computes the base points for an event (before the engine's idempotency, per-day…, +5 on self-registration; MDO-onboarded users are not eligible., +5 per completion; non-CBP completions capped per IST calendar month. (+4 more)

### Community 71 - "LearnerDashboard.tsx"
Cohesion: 0.05
Nodes (47): Connections, In / out, Learner Dashboard (frontend shell), TODOs / edge cases, LearnerDashboard, AssessmentUploadZone(), AssessmentUploadZoneProps, COLORS (+39 more)

### Community 72 - "get_enriched_courses"
Cohesion: 0.29
Nodes (8): composite_search(), CompositeSearchRequest, _course_tags(), _enriched_view(), get_enriched_courses(), _matches_filters(), Sunbird-style filters: each key → value or list of accepted values., The catalogue in the older "enriched" shape. Query params:…

### Community 76 - "RecommendationResult"
Cohesion: 0.18
Nodes (9): Measured uplift → coverage learning + training effectiveness (SCIL v6 §6, B5), _course_summary(), _interleave_by_level(), BaseModel, One rung of a ladder. Finishing an in-progress course beats starting a new one., Best course of each level (ascending), then the second-best of each, … Input…, Attach per-course measured uplift (uplift_service.estimate_uplift) — SCIL v6 §6., Returns deduplicated, level-gated recommendations in gap-priority order. Only… (+1 more)

### Community 77 - "_sunbird_result"
Cohesion: 0.25
Nodes (5): GET /api/frac/competencies — the catalogue FRAC set incl. L1–L5 descriptors., GET /api/frac/v1/crosswalk — iGOT dictionary CID id → catalogue FRAC id., GET /api/admin/v1/users Returns: result.users — full list of officials., Safely drill into a Sunbird envelope: data['result']['key1']['key2']..., _sunbird_result()

### Community 87 - "language_service.py"
Cohesion: 0.24
Nodes (11): detect_chat_language(), detect_chat_variant(), detect_chat_variant_or_none(), _devanagari_language(), Small, offline language routing for Gyan chat. This deliberately does *not* use…, Supported ISO 639-1 code for a chat message., The variant the *text itself* signals, or None when it carries no signal. Plain…, Internal language variant: en, hi (Devanagari), hi_latn (romanized Hindi), mr,… (+3 more)

### Community 88 - "test_reply_regression.py"
Cohesion: 0.31
Nodes (9): ChatHistoryItem, BaseModel, RecommendationContext, SkillGapContext, sample_request(), parametrize, English and Hinglish replies must match the pre-catalogue output, except…, test_endpoint_reply_unchanged() (+1 more)

### Community 89 - "chat_actions.py"
Cohesion: 0.50
Nodes (4): detect_ui_actions(), _mentions(), Detect website theme / language changes requested in any supported chat…, Returns (theme, language): theme in {"dark", "light", "toggle"}, language in…

### Community 90 - "_get"
Cohesion: 0.08
Nodes (32): contextlib, get_me(), Return the current authenticated user's profile. Used by the frontend to re-…, get_admin_roster(), get_recommendations(), get_skill_gaps(), Skill Gap Engine: dynamically computes competency gaps from iGOT history.…, Recommendation Engine: returns courses from iGOT catalog bridging the user's… (+24 more)

### Community 91 - "Code"
Cohesion: 0.18
Nodes (12): AsyncClient, Code, fetch(), fetch(), fetch(), fetch(), Pooled client for the running loop — no new TCP connection per call., TTL memo for one user's read. Concurrent callers share one in-flight request;… (+4 more)

### Community 92 - "_user_enrolments"
Cohesion: 0.40
Nodes (5): get_admin_roster(), legacy_user_history(), Merge seed enrolments with any runtime mutations., ICatalogSync.fetchUserHistory() — consumed by MockIgotPlatformAdapter., _user_enrolments()

### Community 93 - "HybridRecommendationEngine"
Cohesion: 0.24
Nodes (8): Before / after metrics, HybridRecommendationEngine, ndarray, Singleton — built ONCE at app startup. Holds FAISS index + BM25 corpus in…, (query embedding, BM25 scores over the whole corpus), cached., Median cosine between the competency query and the courses NOT tagged with it —…, Stage 1 + Stage 2 for a single competency gap. Returns list of (catalog_idx,…, Retrieve (tag + level filtered), drop excluded courses, then score final =…

### Community 94 - "llm.py"
Cohesion: 0.18
Nodes (18): base64, JSONResponse, capabilities(), get, describe_keyframes(), guarded(), run_batch(), vlm_backend() (+10 more)

### Community 95 - "mock_igot_server.py"
Cohesion: 0.15
Nodes (16): legacy_catalog(), legacy_frac(), legacy_job_profiles(), legacy_push_score(), lifespan(), _load_json(), _load_json_from_dir(), Any (+8 more)

### Community 96 - "test_chat_endpoint.py"
Cohesion: 0.42
Nodes (8): fastapi_testclient, _chat(), parametrize, End-to-end /chat behaviour per language through the real multilingual…, test_dark_mode_action(), test_my_courses_navigation(), test_recommendations(), test_skill_gaps()

### Community 97 - "CourseCard.tsx"
Cohesion: 0.24
Nodes (8): CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps, SOURCE_STYLES, matches(), Props, RecommendationsPanel()

### Community 98 - "Code"
Cohesion: 0.22
Nodes (7): Code, Connections, GapEntry, The id whose FRAC tags / levels / official text drive retrieval., {courseId: {compId: FRAC level}} — feeds BaselineAssembler so the Verified…, {courseId: title, primary competency, format, rating, enrolments} for analytics…, Computes and prioritizes skill gaps. priority_k = gap_k * (target_k / 5.0)…

### Community 99 - "embedder.py"
Cohesion: 0.12
Nodes (23): Code, _Embedder, encode_cached(), get_embedder(), _load(), model_name(), onnx_model_dir(), _OnnxEmbedder (+15 more)

### Community 100 - "mock_data_metrics.py"
Cohesion: 0.17
Nodes (14): argparse, collections, io, load_eval(), main(), Benchmark Gyan's intent classifier on the held-out multilingual set. python…, live_metrics(), _login() (+6 more)

### Community 101 - "semantic_engine.py"
Cohesion: 0.14
Nodes (16): difflib, is_embedder_ready(), Non-blocking check — True only if the role's model is already loaded., classify_intent(), _correct_tokens(), is_semantic_engine_ready(), load_corpus(), low_confidence_threshold() (+8 more)

### Community 102 - "authApi.ts"
Cohesion: 0.29
Nodes (10): AuthProvider(), mapRole(), extractError(), getMe(), login(), LoginResponse, logout(), refresh() (+2 more)

### Community 103 - "MockIgotAdapter"
Cohesion: 0.15
Nodes (9): AI Course Recommendation Engine + Learning Pathways, In / out, TODOs / edge cases, MockIgotAdapter, Forget every cached read for this user., The full CBP course catalogue, paged through POST /api/composite/v1/search.…, POST /api/composite/v1/search — Sunbird composite search, every page. `filters`…, Legacy method that maps fetch_user_enrollments to the old simple-mock shape.… (+1 more)

### Community 104 - "_PrerequisiteGate"
Cohesion: 0.33
Nodes (3): _PrerequisiteGate, Cross-competency prerequisite DAG for build_study_plan (SCIL v6 §5, B4). A rung…, Edges that changed or annotate the plan: ordered (waited, then met), blocked,…

### Community 105 - "grade_quiz"
Cohesion: 0.12
Nodes (14): Authentication & RBAC, Connections, In / out, Shared database (Neon), TODOs / edge cases, Posterior mean → one PRACTICE_ASSESSMENT EvidenceLog row (the existing evidence…, _write_evidence(), _detect_skill_name() (+6 more)

### Community 106 - "dependencies.py"
Cohesion: 0.20
Nodes (9): fastapi_security, get_current_user(), Session, auth/dependencies.py…, Decodes the Bearer JWT, looks up the user in auth.db. Raises HTTP 401 for any…, Returns a FastAPI dependency that checks the current user's role. Example:…, require_role(), decode_access_token() (+1 more)

### Community 107 - "ai_tools.py"
Cohesion: 0.17
Nodes (15): is_ollama_available(), Fast, synchronous check — just hits the Ollama /api/tags endpoint. Returns True…, add_documents_from_file(), Ingests a PDF file into the vector store. Returns the number of chunks added.…, ai_health_check(), HealthResponse, BaseModel, post (+7 more)

### Community 108 - "Decisions log (made without the user)"
Cohesion: 0.29
Nodes (5): Could not do / blocked, Decisions log (made without the user), SCIL v6 — mock data + blocked features: progress report, Status, Catalogue duration in hours, or None for a course not in the catalogue.

### Community 109 - "EvidenceLog"
Cohesion: 0.20
Nodes (11): Certificate / Resume Evidence Extraction, Connections, In / out, TODOs / edge cases, Connections, In / out, Skill Gap Analysis (evidence-based competency baselines), TODOs / edge cases (+3 more)

### Community 110 - "recommendation_service.py"
Cohesion: 0.22
Nodes (8): _CourseDoc, _parse_level(), FILE: main-lms-backend/services/recommendation_service.py…, Bayesian shrinkage toward global prior mean. Returns None if either input is…, Level 3' / 3 / '3' → 3; anything outside 1..5 → None., quality = 0.35*completion_n + 0.35*rating_n + 0.20*pop_n + 0.10*tpac_flag FIX…, _shrunk_rating(), rank_bm25

### Community 111 - "Ollama RAG Knowledge Base (Tier 3 — disconnected)"
Cohesion: 0.22
Nodes (8): Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, build_system_prompt(), generate_chat_response(), Runs the full RAG pipeline: 1. Retrieve top-k relevant document chunks from…, Builds a rich system prompt that grounds the LLM in the user's live context.…

### Community 112 - "Request"
Cohesion: 0.22
Nodes (9): exception_handler, HTTPException, get_competencies(), get_job_profiles(), http_exc_handler(), GET /api/job-profiles — NCO Job Role Catalogue (Sunbird-compliant). Served from…, The FRAC competencies roles and courses are tagged with (the catalogue id…, _ts_now() (+1 more)

### Community 113 - ".award_safe"
Cohesion: 0.25
Nodes (6): Connections, In / out, Karma Points (gamification), Rules (`RULES` in `karma_engine.py`, served by `GET /karma/rules`), TODOs / edge cases, For server-side hooks (quiz grading, diagnostics): own session, never raises.

### Community 114 - "ingest_telemetry"
Cohesion: 0.33
Nodes (5): field_validator, ingest_telemetry(), Returns a list of validation errors for a single telemetry event., TelemetryBatch, _validate_event()

### Community 119 - "relevance.py"
Cohesion: 0.38
Nodes (6): competency_name(), frac_competencies(), FILE: services/media_quiz/relevance.py…, Sets chunk.relevance / chunk.competency_id, keeps the MAX_CHUNKS most relevant…, score_chunks(), numpy

### Community 123 - ".build_pathway"
Cohesion: 0.29
Nodes (5): _diagnostic_step(), _fmt_levels(), High-uncertainty levels get a short check before a full course (SCIL v6 §2)., FRAC levels at which the catalogue has at least one course for comp_id., Step-by-step path for one competency: one course per FRAC level from current+1…

### Community 124 - "Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)"
Cohesion: 0.33
Nodes (5): GSBPM scope — the 80% officer-hours rule (SCIL v6 §1), Reference data loading, TODOs / limits, Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight), GET /api/gsbpm/v1/map — GSBPM sub-processes + competency → sub-processes.

### Community 126 - "CLAUDE.md — index & router"
Cohesion: 0.40
Nodes (5): CLAUDE.md — index & router, Feature index, graphify, How to use these docs, Run commands

### Community 127 - "RAG Document → Quiz Generator & Grading"
Cohesion: 0.40
Nodes (4): Connections, In / out, RAG Document → Quiz Generator & Grading, TODOs / edge cases

### Community 128 - "Shared Embedder (chat + catalog roles)"
Cohesion: 0.40
Nodes (4): Connections, In / out, Shared Embedder (chat + catalog roles), TODOs / edge cases

## Knowledge Gaps
- **253 isolated node(s):** ``mock-igot-server/` — external-system simulator`, `4. Persistence`, `5. Tech stack`, `How to use these docs`, `Feature index` (+248 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 814 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **37 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Code` connect `Code` to `api.ts`, `karma_engine.py`, `AwardResult`, `karma.py`, `KarmaRewardsView.tsx`, `grade_quiz`, `.award_safe`, `domain.ts`, `Code`, `3. Core data flow`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `Code` connect `router.py` to `api.ts`, `seed.py`, `engine`, `authApi.ts`, `grade_quiz`, `dependencies.py`, `UserAuth`, `react`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `MockIgotAdapter` connect `MockIgotAdapter` to `Code`, `igot_adapter.py`, `typing`, `karma.py`, `main_backup.py`, `Decisions log (made without the user)`, `_sunbird_result`, `rag.py`, `Code`, `Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)`, `3. Core data flow`, `main-lms-backend/main.py`, `Any`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `Code` (e.g. with `KarmaCard()` and `formatPoints()`) actually correct?**
  _`Code` has 45 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `HybridRecommendationEngine` (e.g. with `7. Mismatches between the mermaid diagram and the code` and `Code`) actually correct?**
  _`HybridRecommendationEngine` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects ``mock-igot-server/` — external-system simulator`, `4. Persistence`, `5. Tech stack` to the rest of the system?**
  _253 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `AssessmentPage.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.08974358974358974 - nodes in this community are weakly interconnected._