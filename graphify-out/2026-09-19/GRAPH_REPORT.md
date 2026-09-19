# Graph Report - SIH_IGot  (2026-09-19)

## Corpus Check
- 252 files · ~4,960,517 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .css 1, .example 1)

## Summary
- 2916 nodes · 7120 edges · 170 communities (126 shown, 44 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 814 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `39beb752`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ReplyContext
- QuizQuestionInput.tsx
- Code
- router.py
- package.json
- _require_auth
- get
- ChatWidget.tsx
- karma.py
- KarmaRewardsView.tsx
- Request
- pipeline.py
- Code
- main_backup.py
- generate.py
- validate
- estimate_uplift
- What You Must Do When Invoked
- Any
- test_pathway.py
- domain.ts
- extractors.py
- media_io.py
- rag.py
- compilerOptions
- os
- 🇮🇳 MoSPI Skill Intelligence Platform
- media_quiz.py
- test_irt.py
- Gyan — Multilingual Chat Assistant
- competency_service.py
- LearnerDashboard.tsx
- chatbot.py
- api.ts
- AwardResult
- speech.d.ts
- graphify reference: extra exports and benchmark
- resolve_level
- BaseModel
- compilerOptions
- Competency
- graphify reference: query, path, explain
- karma_engine.py
- get
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- test_mock_data.py
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- models/models.py
- .claude/CLAUDE.md
- extraction-spec.md
- opportunity
- test_chat_messages.py
- test_prerequisites.py
- AssessmentPage.tsx
- Code
- MediaQuizExtras.tsx
- items.py
- probe.py
- generate_mock_data.py
- test_gap_and_recommendation_upgrades.py
- Any
- download_model.py
- generate
- test_doc_quiz.py
- faker
- services_chat_messages
- services_chat_messages_context
- HybridRecommendationEngine
- CareerReadinessCard.tsx
- bn.py
- en.py
- gu.py
- hi.py
- hi_latn.py
- mr.py
- or_.py
- ta.py
- te.py
- build_enrollments
- test_reply_regression.py
- UserAuth
- mock-igot-server/main.py
- 3. Core data flow
- proficiency_service.py
- Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)
- RecommendationFeedback
- upload_certificate
- main-lms-backend/main.py
- CourseCard.tsx
- mock_igot_server.py
- system_health.py
- test_practice_assessment.py
- Code
- workforce_service.py
- BaselineAssembler
- QuizSkillImpact.tsx
- Code
- AdminDashboard.tsx
- DashboardCreator
- Decisions log (made without the user)
- authApi.ts
- admin_analytics.py
- MockIgotAdapter
- LearningChat.tsx
- engine
- _warm_up
- google_generativeai
- langchain_text_splitters
- mockdata
- pdfplumber
- document_extractor.py
- pptx
- pypdf
- requests
- career.py
- get_recommendations_by_user_id
- urllib_request
- KarmaEventType
- models/domain.py
- Document question pipeline (`main-lms-backend/services/doc_quiz/`)
- Random
- .__init__
- graphify reference: incremental update and cluster-only
- safe_eval
- recommendation_service.py
- _build_engine
- useLearnerDashboard.ts
- sunbird_err
- chat
- Ollama RAG Knowledge Base (Tier 3 — disconnected)
- Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)
- _OnnxEmbedder
- admin_console.py
- sys
- client
- CLAUDE.md — index & router
- Authentication & RBAC
- Media (Video / Audio / YouTube) → Evidence-Cited Quiz
- Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)
- typing
- Mock iGOT Karmayogi Integration (Adapter + mock server + mock data)
- services_media_quiz_llm
- services_media_quiz_pipeline
- _sunbird_result
- Learning Mode — NotebookLM-style study chat (AI Assessment Studio)
- useScreenReader.ts
- courses_for_topics
- Skill Gap Analysis (evidence-based competency baselines)
- Certificate / Resume Evidence Extraction
- _fit
- find_cycle
- mockdata/domain.py
- services_media_quiz
- services_media_quiz_question_gen
- services_media_quiz_relevance
- on_event
- Any
- BaseModel
- post
- UploadFile

## God Nodes (most connected - your core abstractions)
1. `UserAuth` - 91 edges
2. `react` - 55 edges
3. `HybridRecommendationEngine` - 46 edges
4. `Code` - 46 edges
5. `Code` - 39 edges
6. `MockIgotAdapter` - 38 edges
7. `lmsFetch()` - 38 edges
8. `Code` - 38 edges
9. `lucide-react` - 38 edges
10. `Code` - 35 edges

## Surprising Connections (you probably didn't know these)
- ``frontend/src/`` --references--> `RightSidebar()`  [INFERRED]
  ARCHITECTURE.md → frontend/src/components/dashboard/RightSidebar.tsx
- `7. Mismatches between the mermaid diagram and the code` --references--> `SkillGapReport`  [INFERRED]
  ARCHITECTURE.md → frontend/src/types/domain.ts
- `Personalised feedback (`items.feedback`)` --references--> `feedback()`  [INFERRED]
  docs/features/rag-quiz-generator.md → main-lms-backend/services/doc_quiz/items.py
- `Code` --references--> `KarmaLevel`  [INFERRED]
  docs/features/karma-points.md → frontend/src/types/domain.ts
- `Code` --references--> `KarmaToday`  [INFERRED]
  docs/features/karma-points.md → frontend/src/types/domain.ts

## Import Cycles
- None detected.

## Communities (170 total, 44 thin omitted)

### Community 0 - "ReplyContext"
Cohesion: 0.16
Nodes (19): importlib, Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile(), Any, Everything a reply template may personalise, built once per chat request., ReplyContext, _by_page(), _gap_lines() (+11 more)

### Community 1 - "QuizQuestionInput.tsx"
Cohesion: 0.19
Nodes (19): Frontend, emptyAnswer(), hindi(), isAnswered(), pick(), Props, qType(), QuizLang (+11 more)

### Community 2 - "Code"
Cohesion: 0.17
Nodes (11): Code, KarmaMonthlyUsage, Rolling monthly counter for non-CBP COURSE_COMPLETION events. Enforces the…, KarmaEngine, Session, Dispatches an eventType to its strategy, then applies the shared rules in…, DAILY_LOGIN for today, then any streak milestone the current streak has reached., Seeds an empty ledger from iGOT history; afterwards awards any newly completed… (+3 more)

### Community 3 - "router.py"
Cohesion: 0.06
Nodes (61): bcrypt, Code, fastapi_security, TokenBridge(), mapRole(), registerLogoutCallback(), setApiToken(), jose (+53 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (42): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+34 more)

### Community 5 - "_require_auth"
Cohesion: 0.15
Nodes (23): get_assessment_outcomes(), get_crosswalk(), get_gsbpm_map(), get_hrms_officials(), get_item_bank(), get_office(), get_offices(), get_prerequisites() (+15 more)

### Community 6 - "get"
Cohesion: 0.14
Nodes (15): get_admin_roster(), get_org_roles(), health(), legacy_catalog(), legacy_frac(), legacy_job_profiles(), legacy_user_history(), get (+7 more)

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.07
Nodes (48): Code, GyanBot(), GyanHero(), LanguageMenu(), LanguageMenuProps, CAPABILITIES, ChatWidgetProps, MessageBubble() (+40 more)

### Community 8 - "karma.py"
Cohesion: 0.18
Nodes (23): fastapi_concurrency, admin_adjust_karma(), AdminAdjustRequest, _assert_self_or_admin(), award_karma_event(), _award_response(), CbpClaimRequest, claim_cbp_bonus() (+15 more)

### Community 9 - "KarmaRewardsView.tsx"
Cohesion: 0.10
Nodes (25): KarmaCard(), PassbookRow(), PILL_ORDER, RightSidebar(), RightSidebarProps, EVENT_META, formatPoints(), KarmaEventMeta (+17 more)

### Community 10 - "Request"
Cohesion: 0.22
Nodes (9): exception_handler, HTTPException, get_competencies(), get_job_profiles(), http_exc_handler(), GET /api/job-profiles — NCO Job Role Catalogue (Sunbird-compliant). Served from…, The FRAC competencies roles and courses are tagged with (the catalogue id…, _ts_now() (+1 more)

### Community 11 - "pipeline.py"
Cohesion: 0.08
Nodes (33): Code, adapters/igot_adapter.py — iGOT Platform Adapter…, main(), FILE: scripts/eval_media_quiz.py…, build_chunks(), slide_windows: [{"t_start", "t_end", "evidence_ids": [ocr/vlm ids of that…, fact_check(), protect_terms() (+25 more)

### Community 12 - "Code"
Cohesion: 0.13
Nodes (30): Connections, Code, rows_for(), tag_id(), _completed_courses(), _education_score(), enrollment_course_id(), is_completed() (+22 more)

### Community 13 - "main_backup.py"
Cohesion: 0.13
Nodes (20): fastapi_middleware_cors, get_achievements(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments(), get_enrollments_by_user_id(), get_profile_by_user_id(), get_recommendations() (+12 more)

### Community 14 - "generate.py"
Cohesion: 0.09
Nodes (42): dataclasses, httpx, json, _call(), _density(), DocChunk, _prompt(), _quantitative() (+34 more)

### Community 15 - "validate"
Cohesion: 0.12
Nodes (18): excerpt(), _index(), _jaccard(), _numberish(), _opts(), plausibility_and_dedup(), quote_in_source(), The sentence(s) of the source that best match the quote — the passage shown to… (+10 more)

### Community 16 - "estimate_uplift"
Cohesion: 0.17
Nodes (19): estimate_uplift(), _features(), _ipw(), Any, ndarray, services/uplift_service.py — measured course uplift (SCIL v6 §6 coverage…, [1, z, z², tenure/10, statistics degree] with z = preθ − (level − 0.5): takers…, Newton–Raphson for an L2-penalised logistic regression (intercept unpenalised). (+11 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "Any"
Cohesion: 0.13
Nodes (13): absorb(), add_step(), advance(), open_ladders(), _parse_level(), _PrerequisiteGate, Any, Orders the required rungs of several pathways into one sequence. SCIL v6 §5… (+5 more)

### Community 19 - "test_pathway.py"
Cohesion: 0.09
Nodes (20): _edge(), _kinds_levels(), Skill-gap levels + level-aware recommendations + learning pathways. Runs on a…, _resolved(), test_already_met_prerequisite_changes_nothing(), test_completed_never_suggested_and_in_progress_is_continued(), test_crosswalked_competency_gets_a_ladder_under_its_own_id(), test_finishing_a_course_never_lowers_the_level() (+12 more)

### Community 20 - "domain.ts"
Cohesion: 0.04
Nodes (72): Code, Opportunity to practise (SCIL v6 §4), CompetencyOverviewTable(), LevelPips(), priorityOf(), Props, DEFER_REASON, KIND_STYLE (+64 more)

### Community 21 - "extractors.py"
Cohesion: 0.06
Nodes (38): concurrent_futures, Performance, capabilities(), get, JSONResponse, Evidence, Append another timeline's records, renumbered after this one's, plus its drop…, Timeline (+30 more)

### Community 22 - "media_io.py"
Cohesion: 0.13
Nodes (25): Caption, _change(), download_youtube(), fetch(), is_youtube_url(), Keyframe, load_audio(), MediaInputError (+17 more)

### Community 23 - "rag.py"
Cohesion: 0.08
Nodes (48): Any, BaseModel, Code, Connections, ErrorResponse, _generate_overview(), learning_chat(), LearningChatMessage (+40 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "os"
Cohesion: 0.09
Nodes (36): Code, dotenv, logging, is_ollama_available(), FILE: ai/rag_engine.py…, Fast, synchronous check — just hits the Ollama /api/tags endpoint. Returns True…, FILE: ai/seed_knowledge.py…, Embeds all baseline knowledge into ChromaDB. (+28 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "media_quiz.py"
Cohesion: 0.23
Nodes (15): importlib_util, MediaMetadata, MediaQuizQuestion, MediaQuizResponse, _process(), BaseModel, on_event, post (+7 more)

### Community 28 - "test_irt.py"
Cohesion: 0.13
Nodes (22): DiagnosticSessions, fisher_information(), laplace_posterior(), next_item(), p_correct(), public_item(), Any, services/irt_service.py — Tier-1 Bayesian 2PL posterior + adaptive diagnostic… (+14 more)

### Community 29 - "Gyan — Multilingual Chat Assistant"
Cohesion: 0.22
Nodes (8): Connections, Gyan — Multilingual Chat Assistant, In / out, TODOs / edge cases, AI Course Recommendation Engine + Learning Pathways, In / out, TODOs / edge cases, _readiness_gate()

### Community 30 - "competency_service.py"
Cohesion: 0.24
Nodes (7): CompetencyCalculator, datetime, FILE: main-lms-backend/services/competency_service.py…, Maps FRAC types from the JSON to calculation categories., Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, test_missing_channels_do_not_drag_the_score_to_zero()

### Community 31 - "LearnerDashboard.tsx"
Cohesion: 0.07
Nodes (49): `frontend/src/`, Visual design system (shared by every page), App(), DashboardRedirect(), LearnerDashboard, ChatWidget(), ProgressView(), AshokaChakra() (+41 more)

### Community 32 - "chatbot.py"
Cohesion: 0.17
Nodes (24): model_name(), low_confidence_threshold(), chat_mode(), ChatResponse, _intent_response(), _intercept(), get, FILE: routers/chatbot.py Multilingual AI Learning Assistant — Gyan (ज्ञान)… (+16 more)

### Community 33 - "api.ts"
Cohesion: 0.05
Nodes (55): AGENDA_TYPE, CapabilityRiskPanel(), ForesightPanel(), GsbpmScopePanel(), pct(), PrerequisitePanel(), PRIORITY_CHIP, RISK_CHIP (+47 more)

### Community 34 - "AwardResult"
Cohesion: 0.12
Nodes (14): AdminAdjustmentStrategy, AwardResult, CompletionKarmaStrategy, FixedPointsStrategy, IKarmaStrategy, ABC, Computes the base points for an event (before the engine's idempotency, per-day…, Awards the rule's fixed points; eligibility is left to the engine. (+6 more)

### Community 35 - "speech.d.ts"
Cohesion: 0.20
Nodes (6): SpeechRecognition, SpeechRecognitionEvent, SpeechRecognitionResult, SpeechRecognitionResultItem, SpeechRecognitionResultList, Window

### Community 36 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 37 - "resolve_level"
Cohesion: 0.26
Nodes (16): Single source of truth for an official's level on one competency. Every…, resolve_level(), fuse_channels(), Weighted mean over the K/A/U/S channels that carry evidence (None → absent)., _assess(), SCIL v6 §3 evidence channels K/A/U/S (knowledge, application, utility,…, _row(), test_confirmed_use_is_a_floor_unconfirmed_is_not() (+8 more)

### Community 38 - "BaseModel"
Cohesion: 0.10
Nodes (21): field_validator, CompetencyOut, ContentStateRequest, CourseOut, EnrolPayload, get_content_state(), ingest_telemetry(), JobProfileOut (+13 more)

### Community 39 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 40 - "Competency"
Cohesion: 0.12
Nodes (19): Competency, answer(), AnswerBody, BaseModel, get, post, Posterior mean → one PRACTICE_ASSESSMENT EvidenceLog row (the existing evidence…, Close the level dispute that started this session (if any): the tested level is… (+11 more)

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 42 - "karma_engine.py"
Cohesion: 0.13
Nodes (14): _create(), ist_date(), ist_day_start_utc(), ist_now(), KarmaRule, migrate_karma_schema(), MonthlyUsage, date (+6 more)

### Community 44 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 45 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 46 - "test_mock_data.py"
Cohesion: 0.08
Nodes (9): Mock-data generator (mock-igot-server/generate_mock_data.py): determinism, one…, _tags(), test_acbp_mandatory_courses_are_short_catalogue_courses(), test_course_outcomes_are_consistent_with_catalogue_and_roster(), test_ladders_are_complete_except_documented_holes(), test_officials_mostly_study_at_or_just_above_their_level(), test_role_competencies_and_tags_use_catalogue_ids(), test_secondary_tags_are_overlaps_at_compatible_levels() (+1 more)

### Community 49 - "models/models.py"
Cohesion: 0.13
Nodes (29): 7. Mismatches between the mermaid diagram and the code, Base, Conventions, TODOs / edge cases, enum, Admin, Assessment, AssessmentSkillMapping (+21 more)

### Community 58 - "opportunity"
Cohesion: 0.24
Nodes (13): opportunity(), Any, services/gsbpm_service.py — GSBPM scoping (SCIL v6 §1) + opportunity to…, Opportunity to practise a competency in the official's office this cycle (SCIL…, Which competencies are in scope under the officer-hours rule, and why., scope_report(), _sp_name(), subprocess_hours() (+5 more)

### Community 60 - "test_chat_messages.py"
Cohesion: 0.23
Nodes (11): Loads a language's template table on first use ("or" lives in or_.py; `or` is a…, templates(), _alternatives(), _fields(), parametrize, Catalogue completeness: every language has every template, placeholders are…, test_every_intent_renders(), test_placeholders_match_english() (+3 more)

### Community 61 - "test_prerequisites.py"
Cohesion: 0.05
Nodes (51): get, _ensure_can_view(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments_by_user_id(), get_frac_competencies(), get_learning_pathway(), get_profile_by_user_id() (+43 more)

### Community 62 - "AssessmentPage.tsx"
Cohesion: 0.16
Nodes (17): Gyan hand-off (document → quiz or Learning Mode, no second upload), AssessmentPage, ShellNavGroup, AssessmentPage(), DIFFICULTIES, Difficulty, errorText(), formatDate() (+9 more)

### Community 63 - "Code"
Cohesion: 0.13
Nodes (13): Code, GSBPM scope — the 80% officer-hours rule (SCIL v6 §1), _competencies(), _prof_detail(), GET a Sunbird endpoint and return its `result` object., GET /api/gsbpm/v1/map — GSBPM sub-processes + competency → sub-processes., GET /api/org/v1/offices — {cycle, offices[{officeId, subprocesses[{id,…, GET /api/assessment/v1/itembank — 2PL items incl. answer keys (server side… (+5 more)

### Community 64 - "MediaQuizExtras.tsx"
Cohesion: 0.14
Nodes (20): CONTENT_LABEL, MediaAnalysisCard(), MediaAnswerReview(), pct(), QuestionEvidence(), SOURCE_LABEL, YoutubeLinkInput(), formatTimestamp() (+12 more)

### Community 65 - "items.py"
Cohesion: 0.26
Nodes (23): ast, _build_review(), Type-aware answer review, missed questions first. Each wrong answer gets…, accepted_texts(), answer_display(), _choice_set(), correct_display(), feedback() (+15 more)

### Community 66 - "probe.py"
Cohesion: 0.11
Nodes (26): needs_ocr(), _ocr_engine(), ocr_pdf_pages(), OcrUnavailable, ndarray, RuntimeError, FILE: services/doc_quiz/extract.py…, (text in reading order, mean confidence, weak lines dropped). (+18 more)

### Community 67 - "generate_mock_data.py"
Cohesion: 0.18
Nodes (24): build_acbp(), build_crosswalk(), build_frac(), build_gsbpm_map(), build_hrms(), build_item_bank(), build_offices(), build_officials() (+16 more)

### Community 68 - "test_gap_and_recommendation_upgrades.py"
Cohesion: 0.09
Nodes (30): calculate_baseline(), EvidencePayload, Stateless calculator for one competency, on exactly the scoring path the…, assess_competency(), explain_level(), datetime, One competency, K/A/U/S fused — the scoring path shared by compute_for_user and…, "Why this level" for one competency, built only from numbers the API already… (+22 more)

### Community 69 - "Any"
Cohesion: 0.19
Nodes (9): ILearningPlatformAdapter, ABC, Any, Interface for external learning platform integration. All concrete adapters…, Return the full CBP course catalog., Return learning history for a user (legacy, by govId or userId)., Return the full user roster (all officials)., Look up a single user by their iGOT userId (usr_...). Returns None if not found. (+1 more)

### Community 70 - "download_model.py"
Cohesion: 0.43
Nodes (6): download(), _fetch(), main(), scripts/download_model.py…, Encode the fixed corpora once so the server's startup is a cache hit., warm()

### Community 71 - "generate"
Cohesion: 0.16
Nodes (16): _generate_questions(), QuizQuestion, Stamp each item with its content key and its response-calibrated difficulty.…, Cited, validated, multi-type questions (services/doc_quiz/generate.py) →…, _with_calibration(), difficulty_quotas(), generate(), _largest_remainder() (+8 more)

### Community 72 - "test_doc_quiz.py"
Cohesion: 0.12
Nodes (22): extract_docx(), Returns (text with section markers, section count)., _table_rows(), _label(), locate_chunks(), Give each chunk an id and a human locator from the page/slide/section markers., _chunks(), _mcq() (+14 more)

### Community 76 - "HybridRecommendationEngine"
Cohesion: 0.13
Nodes (16): Code, _CourseDoc, GapEntry, HybridRecommendationEngine, The id whose FRAC tags / levels / official text drive retrieval., Singleton — built ONCE at app startup. Holds FAISS index + BM25 corpus in…, {courseId: title, primary competency, format, rating, enrolments} for analytics…, Computes and prioritizes skill gaps. priority_k = gap_k * (target_k / 5.0)… (+8 more)

### Community 77 - "CareerReadinessCard.tsx"
Cohesion: 0.14
Nodes (12): CareerReadinessCard(), Props, TIER_LABEL, COLORS, LearningSnapshot(), Props, MyCoursesView(), MyCoursesViewProps (+4 more)

### Community 87 - "build_enrollments"
Cohesion: 0.15
Nodes (14): _batch(), build_enrollments(), build_workplace_evidence(), course_hours(), course_tags(), iso(), _leaf_ids(), _mandatory_entry() (+6 more)

### Community 88 - "test_reply_regression.py"
Cohesion: 0.19
Nodes (18): ChatHistoryItem, ChatRequest, BaseModel, RecommendationContext, SkillGapContext, sample_request(), _chat(), parametrize (+10 more)

### Community 89 - "UserAuth"
Cohesion: 0.13
Nodes (26): AuthBase, Returns a FastAPI dependency that checks the current user's role. Example:…, require_role(), UserAuth, capability_risk(), _frac_names(), gsbpm_scope(), prerequisite_dag() (+18 more)

### Community 90 - "mock-igot-server/main.py"
Cohesion: 0.13
Nodes (22): contextlib, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history(), health() (+14 more)

### Community 91 - "3. Core data flow"
Cohesion: 0.17
Nodes (12): 3. Core data flow, AsyncClient, fetch(), fetch(), fetch(), fetch(), Pooled client for the running loop — no new TCP connection per call., TTL memo for one user's read. Concurrent callers share one in-flight request;… (+4 more)

### Community 92 - "proficiency_service.py"
Cohesion: 0.08
Nodes (38): _load_db_evidence(), iGOT profile competencyLevel ('Level 3') → 3; missing → 0 (no claim)., The LMS's own EvidenceLog rows for one user (sync — run in a worker thread)., Profile + enrollments + EvidenceLog → one resolved row per role competency.…, _resolve_competency_state(), _self_reported_level(), cluster_of(), cohort_prior() (+30 more)

### Community 93 - "Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)"
Cohesion: 0.15
Nodes (13): 1. Runtime topology, 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator (+5 more)

### Community 94 - "RecommendationFeedback"
Cohesion: 0.15
Nodes (20): One learner interaction with a recommended course. `event` ∈ impression | click…, RecommendationFeedback, feedback_summary(), FeedbackBody, my_feedback(), post_feedback(), BaseModel, get (+12 more)

### Community 95 - "upload_certificate"
Cohesion: 0.23
Nodes (15): CertificateSubmission, One uploaded certificate (routers/competency.py). On upload each extracted…, CertificateReview, certificates_for_review(), _find(), my_certificates(), BaseModel, get (+7 more)

### Community 96 - "main-lms-backend/main.py"
Cohesion: 0.07
Nodes (43): asyncio, datetime, fastapi, fastapi_testclient, get_db(), auth/database.py…, FastAPI dependency — `db: Session = Depends(get_db)`; closed after the request., get_current_user() (+35 more)

### Community 97 - "CourseCard.tsx"
Cohesion: 0.18
Nodes (13): BADGE_STYLE, CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps, MODALITY_LABEL, SOURCE_STYLES, matches() (+5 more)

### Community 98 - "mock_igot_server.py"
Cohesion: 0.18
Nodes (17): fastapi_responses, composite_search(), CompositeSearchRequest, _course_tags(), _enriched_view(), get_enriched_courses(), lifespan(), _load_json() (+9 more)

### Community 99 - "system_health.py"
Cohesion: 0.35
Nodes (14): is_embedder_ready(), Non-blocking check — True only if the role's model is already loaded., is_semantic_engine_ready(), basic(), _component(), detailed(), _embedders(), _engine_and_data() (+6 more)

### Community 100 - "test_practice_assessment.py"
Cohesion: 0.21
Nodes (10): link_competency(), Pick which of the learner's ROLE competencies this quiz is evidence for. 1. the…, _tokens(), _one(), _profile(), Quiz → skill-gap bridge: difficulty-aware ability update, weighted score,…, test_failed_quiz_lowers_skill_score_and_passed_quiz_raises_it(), test_link_by_frac_tag() (+2 more)

### Community 101 - "Code"
Cohesion: 0.16
Nodes (16): Code, CertificateReviewQueue(), Row(), STATUS_CLS, TABS, when(), CertificateUploadZone(), clean() (+8 more)

### Community 102 - "workforce_service.py"
Cohesion: 0.11
Nodes (28): Admin Dashboard, Code, How the parts work, TODOs / edge cases, What the synthetic data shows, daily_snapshot_loop(), Started once from main._startup. Waits for the DB, gives the workforce snapshot…, emerging_skills() (+20 more)

### Community 103 - "BaselineAssembler"
Cohesion: 0.18
Nodes (9): Connections, BaselineAssembler, _normalise_course_map(), Accept {courseId: {compId: level}} or the legacy {courseId: [compId]}., {courseId: {compId: FRAC level}} — feeds BaselineAssembler so the Verified…, test_verified_cert_lifts_confidence_over_documented(), The old `requiredLevel - 1` cap made every evidence-backed gap permanent., test_completion_evidence_follows_the_crosswalk() (+1 more)

### Community 104 - "QuizSkillImpact.tsx"
Cohesion: 0.15
Nodes (11): Delta(), DIFF_CLASS, DifficultyChip(), QuizQuestionReview(), QuizRecommendations(), signed(), SkillImpactCard(), TYPE_NAMES (+3 more)

### Community 105 - "Code"
Cohesion: 0.10
Nodes (34): Code, Gemini model, Personalised feedback (`items.feedback`), Practice ability (`main-lms-backend/services/practice_assessment.py`), _competency_rows(), grade_quiz(), Any, _question_difficulties() (+26 more)

### Community 106 - "AdminDashboard.tsx"
Cohesion: 0.06
Nodes (72): Frontend, AdminDashboard, AdminActions(), AssignForm(), when(), AdminFilterBar(), ExportButton(), facetLabels() (+64 more)

### Community 107 - "DashboardCreator"
Cohesion: 0.16
Nodes (4): AdminDashboardCreator, DashboardCreator, OfficialDashboardCreator, TrainerDashboardCreator

### Community 108 - "Decisions log (made without the user)"
Cohesion: 0.18
Nodes (8): Before / after metrics, Could not do / blocked, Decisions log (made without the user), Noticed but out of scope (not fixed), SCIL v6 — mock data + blocked features: progress report, Status, Catalogue duration in hours, or None for a course not in the catalogue., Median cosine between the competency query and the courses NOT tagged with it —…

### Community 109 - "authApi.ts"
Cohesion: 0.31
Nodes (10): AuthProvider(), changePassword(), extractError(), getMe(), login(), LoginResponse, logout(), refresh() (+2 more)

### Community 110 - "admin_analytics.py"
Cohesion: 0.09
Nodes (44): Backend, overview(), _competency_metrics(), daily_metrics(), by(), dept_compliance(), facets(), Filters (+36 more)

### Community 111 - "MockIgotAdapter"
Cohesion: 0.20
Nodes (6): MockIgotAdapter, Forget every cached read for this user., The full CBP course catalogue, paged through POST /api/composite/v1/search.…, POST /api/composite/v1/search — Sunbird composite search, every page. `filters`…, Legacy method that maps fetch_user_enrollments to the old simple-mock shape.…, Calls the Sunbird-compliant mock iGOT server (mock_igot_server.py) on port 8001…

### Community 112 - "LearningChat.tsx"
Cohesion: 0.26
Nodes (12): ChatEntry, LearningChat(), LearningChatProps, fetchWithTimeout(), LearningChatResponse, LearningChatTurn, LearningCitation, LearningMetadata (+4 more)

### Community 113 - "engine"
Cohesion: 0.26
Nodes (11): test_stored_embeddings_are_reused_only_when_text_matches(), test_tpac_boost_depends_on_provenance(), _course(), engine(), _frac(), fixture, Hashed bag-of-words → L2-normalised vector. Shared words ⇒ positive cosine., _StubEmbedder (+3 more)

### Community 114 - "_warm_up"
Cohesion: 0.10
Nodes (18): AbstractEventLoop, Connections, In / out, Shared Embedder (chat + catalog roles), TODOs / edge cases, Measured uplift → coverage learning + training effectiveness (SCIL v6 §6, B5), Workforce snapshot, _build_workforce_snapshot() (+10 more)

### Community 119 - "document_extractor.py"
Cohesion: 0.13
Nodes (29): CertificateExtractionResult, _clamp_level(), DocumentExtractorService, ExtractedCompetency, ExtractionError, frac_by_id(), frac_dictionary(), _gemini_extract() (+21 more)

### Community 123 - "career.py"
Cohesion: 0.15
Nodes (22): LevelDispute, status: OPEN (test started) → CONFIRMED | RAISED | LOWER_THAN_SHOWN once the…, career_readiness(), _dispute_view(), DisputeBody, _ensure_can_view(), my_disputes(), office_ladder() (+14 more)

### Community 124 - "get_recommendations_by_user_id"
Cohesion: 0.19
Nodes (9): get_recommendations_by_user_id(), get_skill_gaps_by_user_id(), _level_to_int(), on_event, Level 3' → 3, 'Level 2' → 2, fallback → 2, Skill-gap analysis for a learner by their iGOT userId., AI-ranked course recommendations personalised by skill gap., Create users_auth table if it doesn't exist yet. (+1 more)

### Community 126 - "KarmaEventType"
Cohesion: 0.20
Nodes (8): Connections, In / out, Karma Points (gamification), Rules (`RULES` in `karma_engine.py`, served by `GET /karma/rules`), TODOs / edge cases, KarmaEventType, Idempotency key for an event; None means 'not idempotent' (admin only)., For server-side hooks (quiz grading, diagnostics): own session, never raises.

### Community 128 - "models/domain.py"
Cohesion: 0.29
Nodes (11): Achievement, AchievementsResponse, Enrollment, EnrollmentsResponse, EvidenceBreakdown, BaseModel, Per-channel evidence values after decay/discount, as used in the fusion formula., Recommendation (+3 more)

### Community 129 - "Document question pipeline (`main-lms-backend/services/doc_quiz/`)"
Cohesion: 0.19
Nodes (15): Difficulty calibration (`services/doc_quiz/calibration.py`), Document question pipeline (`main-lms-backend/services/doc_quiz/`), calibrate(), calibrate_items(), difficulty_from_b(), load_stats(), Any, responses: [{key, correct, llm_difficulty, type, question}] from ONE first… (+7 more)

### Community 130 - "Random"
Cohesion: 0.25
Nodes (11): build_catalog(), _course_id(), _covariates(), _hours_for(), datetime, price collection and quote validation' → 'Price Collection and Quote…, Returns (catalogue, hidden) — hidden holds generator-only facts (planted…, ref_minus() (+3 more)

### Community 131 - ".__init__"
Cohesion: 0.25
Nodes (6): ndarray, Stable hash of a course's embedded text — decides whether a stored vector is…, `catalog` / `frac` / `crosswalk` are the lists served by the mock iGOT server…, Stored vectors whose text hash still matches; encode (disk-memoised) the rest., [(courseId, text_hash, vector)] — what catalogue_store persists., text_hash()

### Community 132 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.29
Nodes (6): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only, data(), files(), fixture

### Community 133 - "safe_eval"
Cohesion: 0.18
Nodes (11): In / out, RAG Document → Quiz Generator & Grading (quiz ↔ skill gap), TODOs / edge cases, Verification, _computed_ok(), expression_numbers(), Evaluate +,-,*,/,**,%, parentheses and a few math functions. Raises ValueError…, Literal numbers used in an expression (for the 'inputs come from the source'… (+3 more)

### Community 134 - "recommendation_service.py"
Cohesion: 0.10
Nodes (21): ndarray, Cross-encoder scores for `passages` against `query`, or None if no reranker., rerank_scores(), _course_summary(), _diagnostic_step(), _fmt_levels(), _interleave_by_level(), BaseModel (+13 more)

### Community 135 - "_build_engine"
Cohesion: 0.27
Nodes (10): _build_engine(), Engine + assembler from one catalogue (sync — run in a thread). Course vectors…, _decode_vec(), _encode_vec(), load_embeddings(), ndarray, {courseId: (text_hash, vector)} for vectors stored under `model`; {} on any…, Upsert (courseId, text_hash, vector) rows; rows already stored with the same… (+2 more)

### Community 136 - "useLearnerDashboard.ts"
Cohesion: 0.08
Nodes (31): Connections, In / out, Learner Dashboard (frontend shell), TODOs / edge cases, formatDate(), ProfileHeader(), ProfileHeaderProps, TAGLINE (+23 more)

### Community 137 - "sunbird_err"
Cohesion: 0.27
Nodes (10): _course_by_id(), get_course_catalog(), get_user_enrolments(), get_user_profile(), get_user_workplace_evidence(), JSONResponse, One official's workplace evidence as EvidenceLog-style rows: SUPERVISOR_RATING…, O(1) lookup via pre-built _COURSE_INDEX. (+2 more)

### Community 138 - "chat"
Cohesion: 0.12
Nodes (19): classify_intent(), Returns (best_intent, confidence). ("general", 0.0) if the embedder is…, chat(), detect_intent_keyword(), post, Multilingual AI Learning Assistant — Gyan (ज्ञान)., load_eval(), main() (+11 more)

### Community 139 - "Ollama RAG Knowledge Base (Tier 3 — disconnected)"
Cohesion: 0.22
Nodes (8): Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, build_system_prompt(), generate_chat_response(), Runs the full RAG pipeline: 1. Retrieve top-k relevant document chunks from…, Builds a rich system prompt that grounds the LLM in the user's live context.…

### Community 140 - "Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)"
Cohesion: 0.22
Nodes (7): Cross-competency prerequisite DAG (SCIL v6 §5, B4), Reference data loading, TODOs / limits, Used by the admin console, Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight), GET /api/frac/v1/prerequisites — {count, edges[]} expert-seeded prerequisite…, GET /api/course/v1/assessment/outcomes — {outcomes[], comparisons[]} pre/post θ…

### Community 141 - "_OnnxEmbedder"
Cohesion: 0.22
Nodes (4): _OnnxEmbedder, ndarray, A directory written by scripts/download_model.py., sentence-transformers-compatible encoder on onnxruntime + HF `tokenizers`…

### Community 142 - "admin_console.py"
Cohesion: 0.08
Nodes (60): csv, Endpoints (`/api/v1/admin/console`, all take `?department=&grade=&office=`), AdminDailySnapshot, One row per calendar day (UTC): the workforce headline numbers plus the same…, An admin assigning courses (a training plan) to a department or a list of…, A reminder sent by an admin to an official behind on mandatory (ACBP) training., TrainingAssignment, TrainingNudge (+52 more)

### Community 143 - "sys"
Cohesion: 0.22
Nodes (4): scripts/quantize_model.py…, main(), seed_data.py — superseded. All mock data now comes from ONE deterministic…, sys

### Community 144 - "client"
Cohesion: 0.50
Nodes (4): client(), roster(), fixture, _u()

### Community 145 - "CLAUDE.md — index & router"
Cohesion: 0.40
Nodes (5): CLAUDE.md — index & router, Feature index, graphify, How to use these docs, Run commands

### Community 146 - "Authentication & RBAC"
Cohesion: 0.40
Nodes (4): Authentication & RBAC, Connections, In / out, Shared database (Neon)

### Community 147 - "Media (Video / Audio / YouTube) → Evidence-Cited Quiz"
Cohesion: 0.25
Nodes (7): In / out, Media (Video / Audio / YouTube) → Evidence-Cited Quiz, Pipeline, Setup, TODOs / edge cases, Verification, YouTube

### Community 148 - "Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)"
Cohesion: 0.50
Nodes (4): Cold start for UNASSESSED competencies, Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8), Foresight, Proficiency belief with dated decay

### Community 149 - "typing"
Cohesion: 0.05
Nodes (56): argparse, base64, collections, difflib, Code, functools, hashlib, io (+48 more)

### Community 150 - "Mock iGOT Karmayogi Integration (Adapter + mock server + mock data)"
Cohesion: 0.33
Nodes (5): Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server + mock data), TODOs / edge cases, Relevance logits, one per (query, passage) pair (higher = better match).

### Community 153 - "_sunbird_result"
Cohesion: 0.25
Nodes (5): GET /api/frac/competencies — the catalogue FRAC set incl. L1–L5 descriptors., GET /api/frac/v1/crosswalk — iGOT dictionary CID id → catalogue FRAC id., GET /api/admin/v1/users Returns: result.users — full list of officials., Safely drill into a Sunbird envelope: data['result']['key1']['key2']..., _sunbird_result()

### Community 154 - "Learning Mode — NotebookLM-style study chat (AI Assessment Studio)"
Cohesion: 0.33
Nodes (5): Connections, In / out, Learning Mode — NotebookLM-style study chat (AI Assessment Studio), TODOs / edge cases, Verification

### Community 155 - "useScreenReader.ts"
Cohesion: 0.53
Nodes (5): chunkText(), extractReadableText(), isHidden(), ScreenReader, useScreenReader()

### Community 156 - "courses_for_topics"
Cohesion: 0.40
Nodes (3): courses_for_topics(), One course per missed question: the catalogue course whose content is closest…, test_courses_for_topics_prefers_competency_courses()

### Community 157 - "Skill Gap Analysis (evidence-based competency baselines)"
Cohesion: 0.50
Nodes (4): Connections, In / out, Skill Gap Analysis (evidence-based competency baselines), TODOs / edge cases

### Community 158 - "Certificate / Resume Evidence Extraction"
Cohesion: 0.67
Nodes (3): Certificate / Resume Evidence Extraction, In / out, TODOs / edge cases

### Community 159 - "_fit"
Cohesion: 0.67
Nodes (3): record(), _fit(), How much of a course's uplift a learner at `pre` can take from a Level-`level`…

### Community 160 - "find_cycle"
Cohesion: 0.67
Nodes (3): find_cycle(), visit(), Cycle in expert edges + the implicit within-competency ladder (c@L-1 → c@L), or…

## Knowledge Gaps
- **302 isolated node(s):** ``mock-igot-server/` — external-system simulator`, `4. Persistence`, `5. Tech stack`, `How to use these docs`, `Feature index` (+297 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1048 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **44 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Code` connect `HybridRecommendationEngine` to `CourseCard.tsx`, `.__init__`, `recommendation_service.py`, `_build_engine`, `useLearnerDashboard.ts`, `BaselineAssembler`, `MockIgotAdapter`, `estimate_uplift`, `_warm_up`, `test_prerequisites.py`, `domain.ts`, `Any`, `opportunity`, `3. Core data flow`, `Gyan — Multilingual Chat Assistant`, `RecommendationFeedback`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `UserAuth` connect `UserAuth` to `main-lms-backend/main.py`, `router.py`, `Competency`, `karma.py`, `Code`, `main_backup.py`, `admin_console.py`, `admin_analytics.py`, `client`, `document_extractor.py`, `rag.py`, `career.py`, `get_recommendations_by_user_id`, `RecommendationFeedback`, `upload_certificate`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `Code` connect `pipeline.py` to `MediaQuizExtras.tsx`, `probe.py`, `Code`, `chat`, `generate.py`, `Media (Video / Audio / YouTube) → Evidence-Cited Quiz`, `extractors.py`, `media_io.py`, `typing`, `AssessmentPage.tsx`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 69 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 69 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `HybridRecommendationEngine` (e.g. with `7. Mismatches between the mermaid diagram and the code` and `Code`) actually correct?**
  _`HybridRecommendationEngine` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 45 inferred relationships involving `Code` (e.g. with `KarmaCard()` and `formatPoints()`) actually correct?**
  _`Code` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects ``mock-igot-server/` — external-system simulator`, `4. Persistence`, `5. Tech stack` to the rest of the system?**
  _302 weakly-connected nodes found - possible documentation gaps or missing edges._