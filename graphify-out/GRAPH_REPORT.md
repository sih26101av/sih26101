# Graph Report - SIH_IGot  (2026-09-19)

## Corpus Check
- 247 files · ~4,955,296 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .css 1, .example 1)

## Summary
- 2860 nodes · 7026 edges · 153 communities (117 shown, 36 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 791 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `92328106`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ReplyContext
- AssessmentPage.tsx
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
- insights.py
- Timeline
- generate.py
- Code
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
- proficiency_service.py
- _warm_up
- competency_service.py
- react
- chatbot.py
- opportunity
- AwardResult
- speech.d.ts
- graphify reference: extra exports and benchmark
- resolve_level
- BaseModel
- compilerOptions
- _create_schema
- graphify reference: query, path, explain
- Admin Dashboard
- main-lms-backend/main.py
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- test_mock_data.py
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- models/models.py
- .claude/CLAUDE.md
- extraction-spec.md
- embedder.py
- test_chat_messages.py
- estimate_uplift
- diagnostic.py
- MockIgotAdapter
- test_irt.py
- items.py
- probe.py
- generate_mock_data.py
- test_gap_and_recommendation_upgrades.py
- Any
- get_embedder
- LearnerDashboard.tsx
- test_doc_quiz.py
- faker
- services_chat_messages
- services_chat_messages_context
- HybridRecommendationEngine
- _db
- bn.py
- en.py
- gu.py
- hi.py
- hi_latn.py
- mr.py
- or_.py
- ta.py
- te.py
- semantic_engine.py
- test_reply_regression.py
- UserAuth
- mock-igot-server/main.py
- Code
- useLearnerDashboard.ts
- catalogue_store.py
- RecommendationFeedback
- upload_certificate
- competency.py
- CourseCard.tsx
- mock_igot_server.py
- system_health.py
- admin_console.py
- MediaQuizExtras.tsx
- workforce_service.py
- routers
- generate
- practice_assessment.py
- AdminDashboard.tsx
- AI Course Recommendation Engine + Learning Pathways
- Decisions log (made without the user)
- test_admin_analytics.py
- admin_analytics.py
- api.ts
- test_proficiency_foresight.py
- engine
- _learner_competency_state
- google_generativeai
- langchain_text_splitters
- mockdata
- pdfplumber
- document_extractor.py
- pptx
- pypdf
- requests
- career_readiness
- sunbird_err
- urllib_request
- .award_safe
- CLAUDE.md
- typing
- calibration.py
- karma_engine.py
- recommendation_service.py
- ai_tools.py
- safe_eval
- reranker.py
- test_certificate_evidence.py
- _sunbird_result
- build_outcomes
- language_service.py
- Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)
- Media (Video / Audio / YouTube) → Evidence-Cited Quiz
- chat
- record_daily_snapshot
- test_chat_endpoint.py
- graphify reference: incremental update and cluster-only
- CLAUDE.md — index & router
- Authentication & RBAC
- chat_actions.py
- Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)
- services
- services_media_quiz
- services_media_quiz_llm
- services_media_quiz_pipeline

## God Nodes (most connected - your core abstractions)
1. `UserAuth` - 101 edges
2. `react` - 54 edges
3. `HybridRecommendationEngine` - 47 edges
4. `Code` - 46 edges
5. `MockIgotAdapter` - 39 edges
6. `Code` - 39 edges
7. `lmsFetch()` - 38 edges
8. `Code` - 38 edges
9. `lucide-react` - 37 edges
10. `Code` - 35 edges

## Surprising Connections (you probably didn't know these)
- ``frontend/src/`` --references--> `RightSidebar()`  [INFERRED]
  ARCHITECTURE.md → frontend/src/components/dashboard/RightSidebar.tsx
- `Code` --references--> `WhyThisLevel()`  [INFERRED]
  docs/features/skill-gap-analysis.md → frontend/src/components/dashboard/SkillGapCard.tsx
- `TODOs / edge cases` --references--> `gradeQuiz()`  [INFERRED]
  docs/features/media-quiz-generator.md → frontend/src/services/api.ts
- `Code` --references--> `KarmaLevel`  [INFERRED]
  docs/features/karma-points.md → frontend/src/types/domain.ts
- `Code` --references--> `KarmaToday`  [INFERRED]
  docs/features/karma-points.md → frontend/src/types/domain.ts

## Import Cycles
- None detected.

## Communities (153 total, 36 thin omitted)

### Community 0 - "ReplyContext"
Cohesion: 0.15
Nodes (20): functools, importlib, Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile(), Any, Everything a reply template may personalise, built once per chat request., ReplyContext, _by_page() (+12 more)

### Community 1 - "AssessmentPage.tsx"
Cohesion: 0.08
Nodes (43): Frontend, AssessmentPage, emptyAnswer(), hindi(), isAnswered(), pick(), Props, qType() (+35 more)

### Community 2 - "Code"
Cohesion: 0.13
Nodes (15): Code, KarmaEvent, KarmaMonthlyUsage, Immutable ledger entry — one row per karma point award event., Rolling monthly counter for non-CBP COURSE_COMPLETION events. Enforces the…, KarmaEngine, MonthlyUsage, Session (+7 more)

### Community 3 - "router.py"
Cohesion: 0.06
Nodes (58): bcrypt, datetime, Code, fastapi_security, jose, change_password(), _clear_refresh_cookie(), get_me() (+50 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (43): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+35 more)

### Community 5 - "_require_auth"
Cohesion: 0.15
Nodes (23): get_assessment_outcomes(), get_crosswalk(), get_gsbpm_map(), get_hrms_officials(), get_item_bank(), get_office(), get_offices(), get_prerequisites() (+15 more)

### Community 6 - "get"
Cohesion: 0.14
Nodes (15): get_admin_roster(), get_org_roles(), health(), legacy_catalog(), legacy_frac(), legacy_job_profiles(), legacy_user_history(), get (+7 more)

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.08
Nodes (48): Code, GyanBot(), GyanHero(), LanguageMenu(), LanguageMenuProps, CAPABILITIES, ChatWidget(), ChatWidgetProps (+40 more)

### Community 8 - "karma.py"
Cohesion: 0.18
Nodes (23): fastapi_concurrency, admin_adjust_karma(), AdminAdjustRequest, _assert_self_or_admin(), award_karma_event(), _award_response(), CbpClaimRequest, claim_cbp_bonus() (+15 more)

### Community 9 - "KarmaRewardsView.tsx"
Cohesion: 0.08
Nodes (31): CareerReadinessCard(), Props, TIER_LABEL, KarmaCard(), PassbookRow(), PILL_ORDER, RightSidebar(), RightSidebarProps (+23 more)

### Community 10 - "Request"
Cohesion: 0.22
Nodes (9): exception_handler, HTTPException, get_competencies(), get_job_profiles(), http_exc_handler(), GET /api/job-profiles — NCO Job Role Catalogue (Sunbird-compliant). Served from…, The FRAC competencies roles and courses are tagged with (the catalogue id…, _ts_now() (+1 more)

### Community 11 - "pipeline.py"
Cohesion: 0.10
Nodes (26): Code, main(), FILE: scripts/eval_media_quiz.py…, caption_regions(), fact_check(), translate_questions(), Media → quiz pipeline (video, audio, YouTube) for the Assessment Studio. Entry…, MediaSource (+18 more)

### Community 12 - "Code"
Cohesion: 0.15
Nodes (25): Connections, Code, rows_for(), tag_id(), _completed_courses(), _education_score(), enrollment_course_id(), is_completed() (+17 more)

### Community 13 - "insights.py"
Cohesion: 0.14
Nodes (22): capability_risk(), _frac_names(), gsbpm_scope(), prerequisite_dag(), get, post, routers/insights.py — admin-only SCIL v6 workforce insights Every number here…, Rebuild the workforce snapshot now (≈ a few seconds). (+14 more)

### Community 14 - "Timeline"
Cohesion: 0.11
Nodes (22): dataclasses, Performance, build_chunks(), Chunk, Evidence, fmt_ts(), _make_chunk(), FILE: services/media_quiz/evidence.py… (+14 more)

### Community 15 - "generate.py"
Cohesion: 0.07
Nodes (50): difflib, Connections, _call(), _density(), difficulty_quotas(), DocChunk, excerpt(), generate() (+42 more)

### Community 16 - "Code"
Cohesion: 0.12
Nodes (27): Code, Gemini model, In / out, Personalised feedback (`items.feedback`), RAG Document → Quiz Generator & Grading (quiz ↔ skill gap), TODOs / edge cases, Verification, _competency_rows() (+19 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "Any"
Cohesion: 0.12
Nodes (13): Measured uplift → coverage learning + training effectiveness (SCIL v6 §6, B5), absorb(), add_step(), advance(), open_ladders(), _PrerequisiteGate, Any, Orders the required rungs of several pathways into one sequence. SCIL v6 §5… (+5 more)

### Community 19 - "test_pathway.py"
Cohesion: 0.08
Nodes (26): test_mandatory_courses_always_included_with_badge(), test_why_recommended_describes_the_level_step(), _edge(), _gap(), _kinds_levels(), Skill-gap levels + level-aware recommendations + learning pathways. Runs on a…, _resolved(), test_already_met_prerequisite_changes_nothing() (+18 more)

### Community 20 - "domain.ts"
Cohesion: 0.04
Nodes (49): DEFER_REASON, KIND_STYLE, PathwayLadder(), LevelCheckModal(), OUTCOME, Props, ProfileHeaderProps, answerDiagnostic() (+41 more)

### Community 21 - "extractors.py"
Cohesion: 0.08
Nodes (40): concurrent_futures, capabilities(), get, JSONResponse, add_captions(), flush(), _budget(), describe_keyframes() (+32 more)

### Community 22 - "media_io.py"
Cohesion: 0.13
Nodes (24): Caption, _change(), download_youtube(), fetch(), is_youtube_url(), load_audio(), MediaInputError, _parse_json3() (+16 more)

### Community 23 - "rag.py"
Cohesion: 0.12
Nodes (27): _chunk_document_text(), _clean_text(), _detect_skill_name(), DocumentMetadata, DocumentUploadResponse, ErrorResponse, _extract_pdf(), _extract_pptx() (+19 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "os"
Cohesion: 0.09
Nodes (31): Code, Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, dotenv, logging, build_system_prompt() (+23 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "media_quiz.py"
Cohesion: 0.20
Nodes (17): importlib_util, MediaMetadata, MediaQuizQuestion, MediaQuizResponse, _process(), BaseModel, on_event, post (+9 more)

### Community 28 - "proficiency_service.py"
Cohesion: 0.15
Nodes (19): cluster_of(), decay(), expected_shortfall(), months_between(), office_phase(), _phi(), proficiency_state(), Any (+11 more)

### Community 29 - "_warm_up"
Cohesion: 0.13
Nodes (16): AbstractEventLoop, 1. Runtime topology, Connections, Gyan — Multilingual Chat Assistant, In / out, TODOs / edge cases, Workforce snapshot, _build_workforce_snapshot() (+8 more)

### Community 30 - "competency_service.py"
Cohesion: 0.24
Nodes (7): CompetencyCalculator, datetime, FILE: main-lms-backend/services/competency_service.py…, Maps FRAC types from the JSON to calculation categories., Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, test_missing_channels_do_not_drag_the_score_to_zero()

### Community 31 - "react"
Cohesion: 0.05
Nodes (60): Visual design system (shared by every page), App(), DashboardRedirect(), TokenBridge(), AshokaChakra(), CountUp(), GovEmblem(), Reveal() (+52 more)

### Community 32 - "chatbot.py"
Cohesion: 0.30
Nodes (16): ChatResponse, _intent_response(), _intercept(), FILE: routers/chatbot.py Multilingual AI Learning Assistant — Gyan (ज्ञान)…, Deterministic handling of English commands the classifier has historically…, _response(), _theme_action(), _ui_action_response() (+8 more)

### Community 33 - "opportunity"
Cohesion: 0.24
Nodes (13): opportunity(), Any, services/gsbpm_service.py — GSBPM scoping (SCIL v6 §1) + opportunity to…, Opportunity to practise a competency in the official's office this cycle (SCIL…, Which competencies are in scope under the officer-hours rule, and why., scope_report(), _sp_name(), subprocess_hours() (+5 more)

### Community 34 - "AwardResult"
Cohesion: 0.14
Nodes (12): AdminAdjustmentStrategy, AwardResult, CompletionKarmaStrategy, IKarmaStrategy, ABC, Computes the base points for an event (before the engine's idempotency, per-day…, +5 on self-registration; MDO-onboarded users are not eligible., +5 per completion; non-CBP completions capped per IST calendar month. (+4 more)

### Community 35 - "speech.d.ts"
Cohesion: 0.20
Nodes (6): SpeechRecognition, SpeechRecognitionEvent, SpeechRecognitionResult, SpeechRecognitionResultItem, SpeechRecognitionResultList, Window

### Community 36 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 37 - "resolve_level"
Cohesion: 0.16
Nodes (22): BaselineAssembler, _normalise_course_map(), Single source of truth for an official's level on one competency. Every…, Accept {courseId: {compId: level}} or the legacy {courseId: [compId]}., resolve_level(), fuse_channels(), Weighted mean over the K/A/U/S channels that carry evidence (None → absent)., _assess() (+14 more)

### Community 38 - "BaseModel"
Cohesion: 0.10
Nodes (21): field_validator, CompetencyOut, ContentStateRequest, CourseOut, EnrolPayload, get_content_state(), ingest_telemetry(), JobProfileOut (+13 more)

### Community 39 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 40 - "_create_schema"
Cohesion: 0.50
Nodes (5): _create_schema(), _create(), Create users_auth and the karma/evidence tables if missing (idempotent)., migrate_karma_schema(), Idempotent upgrade for databases created before the daily-cap rework: adds…

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 42 - "Admin Dashboard"
Cohesion: 0.50
Nodes (4): Admin Dashboard, Code, TODOs / edge cases, What the synthetic data shows

### Community 43 - "main-lms-backend/main.py"
Cohesion: 0.09
Nodes (34): fastapi_middleware_cors, httpx, main.py — MoSPI LMS Backend API (Main Orchestrator)…, get_achievements_by_user_id(), get_admin_roster(), get_enrollments_by_user_id(), get_frac_competencies(), get_profile_by_user_id() (+26 more)

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
Nodes (26): 7. Mismatches between the mermaid diagram and the code, Base, enum, SkillGapReport, Admin, Assessment, AssessmentSkillMapping, BaseUser (+18 more)

### Community 58 - "embedder.py"
Cohesion: 0.10
Nodes (18): hashlib, _Embedder, _load(), onnx_model_dir(), _OnnxEmbedder, ndarray, FILE: ai/embedder.py…, A directory written by scripts/download_model.py. (+10 more)

### Community 60 - "test_chat_messages.py"
Cohesion: 0.21
Nodes (12): Loads a language's template table on first use ("or" lives in or_.py; `or` is a…, templates(), _alternatives(), _fields(), parametrize, Catalogue completeness: every language has every template, placeholders are…, test_every_intent_renders(), test_placeholders_match_english() (+4 more)

### Community 61 - "estimate_uplift"
Cohesion: 0.08
Nodes (43): find_cycle(), infer_edges(), _node(), _norm_sf(), _ols(), Any, ndarray, services/prerequisite_service.py — cross-competency prerequisite DAG (SCIL v6… (+35 more)

### Community 62 - "diagnostic.py"
Cohesion: 0.10
Nodes (30): LevelDispute, status: OPEN (test started) → CONFIRMED | RAISED | LOWER_THAN_SHOWN once the…, _dispute_view(), DisputeBody, my_disputes(), open_dispute(), BaseModel, get (+22 more)

### Community 63 - "MockIgotAdapter"
Cohesion: 0.10
Nodes (18): Cross-competency prerequisite DAG (SCIL v6 §5, B4), GSBPM scope — the 80% officer-hours rule (SCIL v6 §1), Reference data loading, TODOs / limits, Used by the admin console, Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight), MockIgotAdapter, Forget every cached read for this user. (+10 more)

### Community 64 - "test_irt.py"
Cohesion: 0.13
Nodes (23): DiagnosticSessions, fisher_information(), laplace_posterior(), next_item(), p_correct(), public_item(), Any, services/irt_service.py — Tier-1 Bayesian 2PL posterior + adaptive diagnostic… (+15 more)

### Community 65 - "items.py"
Cohesion: 0.24
Nodes (27): ast, Document question pipeline (`main-lms-backend/services/doc_quiz/`), _build_review(), Type-aware answer review, missed questions first. Each wrong answer gets…, accepted_texts(), answer_display(), _choice_set(), correct_display() (+19 more)

### Community 66 - "probe.py"
Cohesion: 0.24
Nodes (10): map_frames(), probe(), ProbeResult, ndarray, FILE: services/media_quiz/probe.py…, fn over items on OCR_WORKERS threads, results in input order., `regions` — precomputed speech spans (e.g. from YouTube captions) instead of…, route() (+2 more)

### Community 67 - "generate_mock_data.py"
Cohesion: 0.13
Nodes (30): _batch(), build_catalog(), build_enrollments(), build_item_bank(), build_offices(), build_officials(), build_role(), build_workplace_evidence() (+22 more)

### Community 68 - "test_gap_and_recommendation_upgrades.py"
Cohesion: 0.13
Nodes (22): calculate_baseline(), EvidencePayload, BaseModel, Stateless calculator for one competency, on exactly the scoring path the…, assess_competency(), explain_level(), Any, One competency, K/A/U/S fused — the scoring path shared by compute_for_user and… (+14 more)

### Community 69 - "Any"
Cohesion: 0.13
Nodes (12): ILearningPlatformAdapter, ABC, Any, The full CBP course catalogue, paged through POST /api/composite/v1/search.…, POST /api/composite/v1/search — Sunbird composite search, every page. `filters`…, Legacy method that maps fetch_user_enrollments to the old simple-mock shape.…, Interface for external learning platform integration. All concrete adapters…, Return the full CBP course catalog. (+4 more)

### Community 70 - "get_embedder"
Cohesion: 0.12
Nodes (20): Code, Connections, In / out, Shared Embedder (chat + catalog roles), TODOs / edge cases, encode_cached(), get_embedder(), Lazily loaded embedder for `role` ("chat" | "catalog"); thread-safe. (+12 more)

### Community 71 - "LearnerDashboard.tsx"
Cohesion: 0.05
Nodes (56): Code, Opportunity to practise (SCIL v6 §4), LearnerDashboard, CompetencyOverviewTable(), LevelPips(), priorityOf(), Props, StudyPlanSummary() (+48 more)

### Community 72 - "test_doc_quiz.py"
Cohesion: 0.11
Nodes (21): _label(), locate_chunks(), Give each chunk an id and a human locator from the page/slide/section markers., Document quiz: extraction (DOCX, OCR), cited multi-type generation, grading…, _chunks(), _mcq(), parametrize, services/doc_quiz — question types, validator, dedup, selection, calibration,… (+13 more)

### Community 76 - "HybridRecommendationEngine"
Cohesion: 0.08
Nodes (31): Code, _course_summary(), _CourseDoc, _fmt_levels(), GapEntry, HybridRecommendationEngine, _interleave_by_level(), BaseModel (+23 more)

### Community 77 - "_db"
Cohesion: 0.12
Nodes (20): A reminder sent by an admin to an official behind on mandatory (ACBP) training., TrainingNudge, AssignmentIn, create_assignment(), create(), _db(), _ensure_self_or_admin(), _last_nudges() (+12 more)

### Community 87 - "semantic_engine.py"
Cohesion: 0.09
Nodes (27): argparse, collections, json, _correct_tokens(), load_corpus(), FILE: ai/semantic_engine.py…, Per-intent confidence for `query`, searched within `lang`'s pool only., Fuzzy-correct English UI vocabulary typos ('dasboard' -> 'dashboard'). (+19 more)

### Community 88 - "test_reply_regression.py"
Cohesion: 0.30
Nodes (10): ChatHistoryItem, ChatRequest, BaseModel, RecommendationContext, SkillGapContext, sample_request(), parametrize, English and Hinglish replies must match the pre-catalogue output, except… (+2 more)

### Community 89 - "UserAuth"
Cohesion: 0.09
Nodes (29): AuthBase, UserAuth, get_achievements(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments(), get_enrollments_by_user_id(), get_profile_by_user_id() (+21 more)

### Community 90 - "mock-igot-server/main.py"
Cohesion: 0.13
Nodes (22): contextlib, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history(), health() (+14 more)

### Community 91 - "Code"
Cohesion: 0.14
Nodes (16): 3. Core data flow, AsyncClient, Code, _competencies(), fetch(), fetch(), fetch(), _prof_detail() (+8 more)

### Community 92 - "useLearnerDashboard.ts"
Cohesion: 0.12
Nodes (20): `frontend/src/`, Connections, In / out, Learner Dashboard (frontend shell), TODOs / edge cases, _cache, NO_ACHIEVEMENTS, NO_ENROLLMENTS (+12 more)

### Community 93 - "catalogue_store.py"
Cohesion: 0.17
Nodes (17): base64, _build_engine(), Engine + assembler from one catalogue (sync — run in a thread). Course vectors…, Reload the catalogue on a timer instead of only at restart. Every…, _refresh_catalogue_loop(), Course, catalogue_fingerprint(), _decode_vec() (+9 more)

### Community 94 - "RecommendationFeedback"
Cohesion: 0.15
Nodes (20): One learner interaction with a recommended course. `event` ∈ impression | click…, RecommendationFeedback, feedback_summary(), FeedbackBody, my_feedback(), post_feedback(), BaseModel, get (+12 more)

### Community 95 - "upload_certificate"
Cohesion: 0.25
Nodes (14): CertificateSubmission, One uploaded certificate (routers/competency.py). On upload each extracted…, CertificateReview, certificates_for_review(), _find(), my_certificates(), get, post (+6 more)

### Community 96 - "competency.py"
Cohesion: 0.10
Nodes (26): fastapi, fastapi_testclient, get_db(), auth/database.py…, FastAPI dependency — `db: Session = Depends(get_db)`; closed after the request., get_current_user(), Session, auth/dependencies.py… (+18 more)

### Community 97 - "CourseCard.tsx"
Cohesion: 0.18
Nodes (13): BADGE_STYLE, CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps, MODALITY_LABEL, SOURCE_STYLES, matches() (+5 more)

### Community 98 - "mock_igot_server.py"
Cohesion: 0.18
Nodes (17): fastapi_responses, composite_search(), CompositeSearchRequest, _course_tags(), _enriched_view(), get_enriched_courses(), lifespan(), _load_json() (+9 more)

### Community 99 - "system_health.py"
Cohesion: 0.26
Nodes (18): is_embedder_ready(), model_name(), Non-blocking check — True only if the role's model is already loaded., is_semantic_engine_ready(), chat_mode(), get, Which response engine is active; the frontend shows it as a badge., basic() (+10 more)

### Community 100 - "admin_console.py"
Cohesion: 0.15
Nodes (34): csv, Endpoints (`/api/v1/admin/console`, all take `?department=&grade=&office=`), An admin assigning courses (a training plan) to a department or a list of…, TrainingAssignment, _assignment_out(), _behind(), _behind_row(), _catalogue() (+26 more)

### Community 101 - "MediaQuizExtras.tsx"
Cohesion: 0.14
Nodes (20): CONTENT_LABEL, MediaAnalysisCard(), MediaAnswerReview(), pct(), QuestionEvidence(), SOURCE_LABEL, YoutubeLinkInput(), formatTimestamp() (+12 more)

### Community 102 - "workforce_service.py"
Cohesion: 0.22
Nodes (17): How the parts work, _Phi(), _as_date(), capability_risk(), cell(), foresight(), _level(), _p_capable() (+9 more)

### Community 104 - "generate"
Cohesion: 0.12
Nodes (18): build_crosswalk(), build_frac(), build_gsbpm_map(), build_hrms(), build_prerequisites(), dumps(), dumps_records(), find_cycle() (+10 more)

### Community 105 - "practice_assessment.py"
Cohesion: 0.08
Nodes (35): Practice ability (`main-lms-backend/services/practice_assessment.py`), courses_for_topics(), latest_practice_value(), link_competency(), media_question_difficulty(), p_correct(), Any, datetime (+27 more)

### Community 106 - "AdminDashboard.tsx"
Cohesion: 0.06
Nodes (71): Frontend, AdminDashboard, AdminActions(), AssignForm(), when(), AdminFilterBar(), ExportButton(), facetLabels() (+63 more)

### Community 107 - "AI Course Recommendation Engine + Learning Pathways"
Cohesion: 0.33
Nodes (5): AI Course Recommendation Engine + Learning Pathways, Connections, In / out, TODOs / edge cases, {courseId: {compId: FRAC level}} — feeds BaselineAssembler so the Verified…

### Community 108 - "Decisions log (made without the user)"
Cohesion: 0.18
Nodes (8): Before / after metrics, Could not do / blocked, Decisions log (made without the user), Noticed but out of scope (not fixed), SCIL v6 — mock data + blocked features: progress report, Status, Catalogue duration in hours, or None for a course not in the catalogue., Median cosine between the competency query and the courses NOT tagged with it —…

### Community 109 - "test_admin_analytics.py"
Cohesion: 0.15
Nodes (17): emerging_skills(), date, datetime, Daily training-rate history rebuilt from dated iGOT course completions, for…, Per FRAC competency, over the (filtered) officials in the workforce snapshot: *…, reconstruct_history(), Admin console aggregates (services/admin_analytics.py): filters, pagination,…, _snap_row() (+9 more)

### Community 110 - "admin_analytics.py"
Cohesion: 0.13
Nodes (30): Backend, overview(), _competency_metrics(), daily_metrics(), by(), dept_compliance(), facets(), Filters (+22 more)

### Community 111 - "api.ts"
Cohesion: 0.04
Nodes (63): CertificateReviewQueue(), Row(), STATUS_CLS, TABS, when(), AGENDA_TYPE, CapabilityRiskPanel(), ForesightPanel() (+55 more)

### Community 112 - "test_proficiency_foresight.py"
Cohesion: 0.17
Nodes (18): iGOT profile competencyLevel ('Level 3') → 3; missing → 0 (no claim)., Profile + enrollments + EvidenceLog → one resolved row per role competency.…, _resolve_competency_state(), _self_reported_level(), cohort_prior(), population_stats(), Cohort prior for an UNASSESSED competency, with the divergence check., comp → (μ_pop, σ_pop, n) over officials with assessed evidence on it. (+10 more)

### Community 113 - "engine"
Cohesion: 0.19
Nodes (14): on_event, Create users_auth table if it doesn't exist yet., _startup(), test_stored_embeddings_are_reused_only_when_text_matches(), test_tpac_boost_depends_on_provenance(), _course(), engine(), _frac() (+6 more)

### Community 114 - "_learner_competency_state"
Cohesion: 0.14
Nodes (14): Connections, In / out, Skill Gap Analysis (evidence-based competency baselines), TODOs / edge cases, _ensure_can_view(), get_learning_pathway(), get_recommendations_by_user_id(), get_skill_gaps_by_user_id() (+6 more)

### Community 119 - "document_extractor.py"
Cohesion: 0.07
Nodes (49): Code, io, extract_docx(), _ocr_engine(), ocr_pdf_pages(), OcrUnavailable, ndarray, RuntimeError (+41 more)

### Community 123 - "career_readiness"
Cohesion: 0.33
Nodes (9): career_readiness(), _ensure_can_view(), office_ladder(), Any, Roles of one office grouped by tier, most junior tier first., readiness = mean over required competencies of min(level, required) / required.…, readiness_for(), _tier() (+1 more)

### Community 124 - "sunbird_err"
Cohesion: 0.27
Nodes (10): _course_by_id(), get_course_catalog(), get_user_enrolments(), get_user_profile(), get_user_workplace_evidence(), JSONResponse, One official's workplace evidence as EvidenceLog-style rows: SUPERVISOR_RATING…, O(1) lookup via pre-built _COURSE_INDEX. (+2 more)

### Community 126 - ".award_safe"
Cohesion: 0.25
Nodes (6): Connections, In / out, Karma Points (gamification), Rules (`RULES` in `karma_engine.py`, served by `GET /karma/rules`), TODOs / edge cases, For server-side hooks (quiz grading, diagnostics): own session, never raises.

### Community 127 - "CLAUDE.md"
Cohesion: 0.24
Nodes (7): Certificate / Resume Evidence Extraction, In / out, TODOs / edge cases, Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server + mock data), TODOs / edge cases

### Community 128 - "typing"
Cohesion: 0.19
Nodes (10): asyncio, adapters/igot_adapter.py — iGOT Platform Adapter…, services/app_state.py — process-wide singletons built in main._warm_up…, Any, services/reference_data.py — SCIL v6 reference datasets Loaded ONCE at startup…, Plain holder; every attribute defaults to empty so features degrade, not crash., _read_disk(), ReferenceData (+2 more)

### Community 129 - "calibration.py"
Cohesion: 0.21
Nodes (13): Difficulty calibration (`services/doc_quiz/calibration.py`), QuizItemStat, Response data per quiz item (services/doc_quiz/calibration.py). itemKey is a…, calibrate(), calibrate_items(), difficulty_from_b(), load_stats(), Any (+5 more)

### Community 130 - "karma_engine.py"
Cohesion: 0.19
Nodes (12): KarmaEventType, FixedPointsStrategy, ist_date(), ist_day_start_utc(), ist_now(), KarmaRule, date, datetime (+4 more)

### Community 131 - "recommendation_service.py"
Cohesion: 0.17
Nodes (11): _diagnostic_step(), _parse_level(), FILE: main-lms-backend/services/recommendation_service.py…, Stable hash of a course's embedded text — decides whether a stored vector is…, High-uncertainty levels get a short check before a full course (SCIL v6 §2)., Bayesian shrinkage toward global prior mean. Returns None if either input is…, Level 3' / 3 / '3' → 3; anything outside 1..5 → None., _shrunk_rating() (+3 more)

### Community 132 - "ai_tools.py"
Cohesion: 0.19
Nodes (13): is_ollama_available(), Fast, synchronous check — just hits the Ollama /api/tags endpoint. Returns True…, ai_health_check(), HealthResponse, BaseModel, get, post, UploadFile (+5 more)

### Community 133 - "safe_eval"
Cohesion: 0.29
Nodes (7): _computed_ok(), expression_numbers(), Evaluate +,-,*,/,**,%, parentheses and a few math functions. Raises ValueError…, Literal numbers used in an expression (for the 'inputs come from the source'…, safe_eval(), ev(), test_safe_eval()

### Community 134 - "reranker.py"
Cohesion: 0.22
Nodes (10): get_reranker(), ndarray, FILE: ai/reranker.py…, Cross-encoder scores for `passages` against `query`, or None if no reranker., Relevance logits, one per (query, passage) pair (higher = better match)., The loaded cross-encoder, or None when disabled / unavailable (logged once)., rerank_scores(), _Reranker (+2 more)

### Community 135 - "test_certificate_evidence.py"
Cohesion: 0.28
Nodes (12): EvidenceLog, Certificate upload → EvidenceLog → admin review, end to end on in-memory SQLite…, _rows(), test_admin_approve_turns_rows_verified(), test_admin_reject_removes_rows(), test_bad_extension_rejected(), test_invalid_document_writes_nothing(), test_llm_ids_are_checked_against_frac() (+4 more)

### Community 136 - "_sunbird_result"
Cohesion: 0.22
Nodes (6): fetch(), GET /api/frac/competencies — the catalogue FRAC set incl. L1–L5 descriptors., GET /api/frac/v1/crosswalk — iGOT dictionary CID id → catalogue FRAC id., GET /api/admin/v1/users Returns: result.users — full list of officials., Safely drill into a Sunbird envelope: data['result']['key1']['key2']..., _sunbird_result()

### Community 137 - "build_outcomes"
Cohesion: 0.24
Nodes (10): build_acbp(), build_outcomes(), record(), course_hours(), course_tags(), _fit(), _mandatory_entry(), _mandatory_pick() (+2 more)

### Community 138 - "language_service.py"
Cohesion: 0.28
Nodes (8): detect_chat_language(), detect_chat_variant_or_none(), _devanagari_language(), Small, offline language routing for Gyan chat. This deliberately does *not* use…, Supported ISO 639-1 code for a chat message., The variant the *text itself* signals, or None when it carries no signal. Plain…, Pick the reply variant for a message, honouring the UI language picker. A…, resolve_chat_variant()

### Community 139 - "Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)"
Cohesion: 0.25
Nodes (7): 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator

### Community 140 - "Media (Video / Audio / YouTube) → Evidence-Cited Quiz"
Cohesion: 0.25
Nodes (7): In / out, Media (Video / Audio / YouTube) → Evidence-Cited Quiz, Pipeline, Setup, TODOs / edge cases, Verification, YouTube

### Community 141 - "chat"
Cohesion: 0.25
Nodes (7): classify_intent(), low_confidence_threshold(), Returns (best_intent, confidence). ("general", 0.0) if the embedder is…, chat(), detect_intent_keyword(), post, Multilingual AI Learning Assistant — Gyan (ज्ञान).

### Community 142 - "record_daily_snapshot"
Cohesion: 0.29
Nodes (8): AdminDailySnapshot, One row per calendar day (UTC): the workforce headline numbers plus the same…, daily_snapshot_loop(), Upsert today's AdminDailySnapshot from the live roster + workforce snapshot., Started once from main._startup. Waits for the DB, gives the workforce snapshot…, record_daily_snapshot(), upsert(), trends_snapshot_now()

### Community 143 - "test_chat_endpoint.py"
Cohesion: 0.50
Nodes (7): _chat(), parametrize, End-to-end /chat behaviour per language through the real multilingual…, test_dark_mode_action(), test_my_courses_navigation(), test_recommendations(), test_skill_gaps()

### Community 144 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.29
Nodes (6): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only, data(), files(), fixture

### Community 145 - "CLAUDE.md — index & router"
Cohesion: 0.33
Nodes (6): CLAUDE.md — index & router, Conventions, Feature index, graphify, How to use these docs, Run commands

### Community 146 - "Authentication & RBAC"
Cohesion: 0.33
Nodes (5): Authentication & RBAC, Connections, In / out, Shared database (Neon), TODOs / edge cases

### Community 147 - "chat_actions.py"
Cohesion: 0.50
Nodes (4): detect_ui_actions(), _mentions(), Detect website theme / language changes requested in any supported chat…, Returns (theme, language): theme in {"dark", "light", "toggle"}, language in…

### Community 148 - "Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)"
Cohesion: 0.50
Nodes (4): Cold start for UNASSESSED competencies, Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8), Foresight, Proficiency belief with dated decay

## Knowledge Gaps
- **294 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+289 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1029 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **36 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `UserAuth` connect `UserAuth` to `router.py`, `test_certificate_evidence.py`, `karma.py`, `insights.py`, `record_daily_snapshot`, `Code`, `rag.py`, `main-lms-backend/main.py`, `models/models.py`, `diagnostic.py`, `_db`, `RecommendationFeedback`, `upload_certificate`, `competency.py`, `admin_console.py`, `admin_analytics.py`, `_learner_competency_state`, `document_extractor.py`, `career_readiness`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `Code` connect `HybridRecommendationEngine` to `CourseCard.tsx`, `opportunity`, `resolve_level`, `get_embedder`, `LearnerDashboard.tsx`, `AI Course Recommendation Engine + Learning Pathways`, `_learner_competency_state`, `_warm_up`, `domain.ts`, `Any`, `estimate_uplift`, `Code`, `useLearnerDashboard.ts`, `catalogue_store.py`, `RecommendationFeedback`, `MockIgotAdapter`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `Code` connect `router.py` to `competency.py`, `AdminDashboard.tsx`, `engine`, `Authentication & RBAC`, `UserAuth`, `react`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 78 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `HybridRecommendationEngine` (e.g. with `7. Mismatches between the mermaid diagram and the code` and `Code`) actually correct?**
  _`HybridRecommendationEngine` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 45 inferred relationships involving `Code` (e.g. with `KarmaCard()` and `formatPoints()`) actually correct?**
  _`Code` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _294 weakly-connected nodes found - possible documentation gaps or missing edges._