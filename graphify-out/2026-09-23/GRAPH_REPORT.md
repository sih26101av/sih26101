# Graph Report - SIH_IGot  (2026-09-23)

## Corpus Check
- 295 files · ~5,027,120 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 6, .service 2, .example 2)

## Summary
- 3401 nodes · 8633 edges · 171 communities (125 shown, 46 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 950 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0b0073a9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_live_catalogue.py
- mediaQuizApi.ts
- _Session
- router.py
- package.json
- _require_auth
- _user_enrolments
- Admin console tier
- karma.py
- Timeline
- ytrelay.py
- test_doc_quiz.py
- Code
- UserAuth
- download_model.py
- generate.py
- gemini_json
- What You Must Do When Invoked
- 3. Core data flow
- test_pathway.py
- domain.ts
- extractors.py
- _fetch_youtube
- LiveIgotAdapter
- compilerOptions
- ai_tools.py
- 🇮🇳 MoSPI Skill Intelligence Platform
- media_quiz.py
- WorkforceInsights.tsx
- admin_chat_data.py
- competency_service.py
- react
- AwardResult
- chat_messages/__init__.py
- test_irt.py
- speech.d.ts
- graphify reference: extra exports and benchmark
- resolve_level
- mock_igot_server.py
- compilerOptions
- apply_crosswalk
- graphify reference: query, path, explain
- irt_service.py
- Code
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- test_mock_data.py
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- models/models.py
- .claude/CLAUDE.md
- extraction-spec.md
- test_admin_chat.py
- opportunity
- test_certificate_evidence.py
- media_io.py
- admin_console.py
- MockIgotAdapter
- LearnerDashboard.tsx
- items.py
- numpy
- Random
- ExtractionError
- Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)
- AssessmentPage.tsx
- rag.py
- kcm_crosswalk.py
- faker
- CourseCard.tsx
- get_embedder
- chatbot.py
- api.ts
- bn.py
- en.py
- gu.py
- hi.py
- hi_latn.py
- mr.py
- or_.py
- ta.py
- te.py
- catalogue_source.py
- CertificateUploadZone.tsx
- proficiency_service.py
- post
- Any
- Media (Video / Audio / YouTube) → Evidence-Cited Quiz
- Keyframe
- calibration.py
- QuizQuestionInput.tsx
- workforce_service.py
- ReplyContext
- Mock iGOT Karmayogi Integration (Adapter + mock server + mock data)
- system_health.py
- Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)
- karma_engine.py
- competency.py
- typing
- LearningChat.tsx
- practice_assessment.py
- Deploy: backend on Oracle Cloud, frontend on Vercel
- warm_up
- Decisions log (made without the user)
- get_enriched_courses
- admin_analytics.py
- QuizSkillImpact.tsx
- App.tsx
- test_proficiency_foresight.py
- BaselineAssembler
- google_generativeai
- langchain_text_splitters
- _resolve_competency_state
- pdfplumber
- probe.py
- pptx
- pypdf
- requests
- admin_chat
- _warm_up
- urllib_request
- youtube_diagnosis
- CLAUDE.md
- test_chat_endpoint.py
- extract.py
- generate
- _answer_admin
- ProviderError
- test_per_user_reads_refuse_rather_than_return_empty
- HybridRecommendationEngine
- safe_eval
- test_gap_and_recommendation_upgrades.py
- generate_mock_data.py
- update.sh
- CLAUDE.md — index & router
- youtube-access.sh
- .award_safe
- vercel.json
- Authentication & RBAC
- AI Course Recommendation Engine + Learning Pathways
- Learning Mode — NotebookLM-style study chat (AI Assessment Studio)
- setup.sh
- services_media_quiz
- services_media_quiz_llm
- services_media_quiz_pipeline
- ._load
- _Attempt
- main-lms-backend/main.py
- engine
- ingest_telemetry
- _fit
- _create_schema
- pipeline.py
- seed_data.py
- mockdata/domain.py
- services_media_quiz_question_gen
- services_media_quiz_relevance
- document_extractor.py
- ai
- frontend_src_hooks_useadmindata_adminrosterrow
- mockdata
- routers
- services
- services_chat_messages
- services_chat_messages_context

## God Nodes (most connected - your core abstractions)
1. `UserAuth` - 107 edges
2. `react` - 66 edges
3. `HybridRecommendationEngine` - 55 edges
4. `_Session` - 52 edges
5. `Code` - 48 edges
6. `Code` - 46 edges
7. `lucide-react` - 45 edges
8. `lmsFetch()` - 40 edges
9. `MockIgotAdapter` - 40 edges
10. `Code` - 40 edges

## Surprising Connections (you probably didn't know these)
- `Code` --references--> `MatchScoreBar()`  [INFERRED]
  docs/features/recommendation-engine.md → frontend/src/components/dashboard/CourseCard.tsx
- ``frontend/src/`` --references--> `RightSidebar()`  [INFERRED]
  ARCHITECTURE.md → frontend/src/components/dashboard/RightSidebar.tsx
- `Code` --references--> `TabType`  [INFERRED]
  docs/features/chatbot-gyan.md → frontend/src/pages/LearnerDashboard.tsx
- `TODOs / edge cases` --references--> `gradeQuiz()`  [INFERRED]
  docs/features/media-quiz-generator.md → frontend/src/services/api.ts
- `7. Mismatches between the mermaid diagram and the code` --references--> `SkillGapReport`  [INFERRED]
  ARCHITECTURE.md → frontend/src/types/domain.ts

## Import Cycles
- None detected.

## Communities (171 total, 46 thin omitted)

### Community 0 - "test_live_catalogue.py"
Cohesion: 0.10
Nodes (21): _as_list(), course_url(), _first_str(), normalise_course(), Upstream returns some fields as a bare string and others as a list., One upstream content record → the dict shape `_parse_catalog` consumes.…, The learner-facing page for a course on the real portal:…, Live iGOT catalogue: record normalisation, competencies_v6 parsing and the KCM… (+13 more)

### Community 1 - "mediaQuizApi.ts"
Cohesion: 0.14
Nodes (20): CONTENT_LABEL, MediaAnalysisCard(), MediaAnswerReview(), pct(), QuestionEvidence(), SOURCE_LABEL, YoutubeLinkInput(), formatTimestamp() (+12 more)

### Community 2 - "_Session"
Cohesion: 0.13
Nodes (16): Code, KarmaMonthlyUsage, Rolling monthly counter for non-CBP COURSE_COMPLETION events. Enforces the…, ist_now(), KarmaEngine, MonthlyUsage, Dispatches an eventType to its strategy, then applies the shared rules in…, Idempotency key for an event; None means 'not idempotent' (admin only). (+8 more)

### Community 3 - "router.py"
Cohesion: 0.06
Nodes (54): bcrypt, Code, fastapi_security, jose, change_password(), _clear_refresh_cookie(), get_me(), login() (+46 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (43): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+35 more)

### Community 5 - "_require_auth"
Cohesion: 0.13
Nodes (39): get_assessment_outcomes(), get_competencies(), get_course_catalog(), get_crosswalk(), get_gsbpm_map(), get_hrms_officials(), get_item_bank(), get_job_profiles() (+31 more)

### Community 6 - "_user_enrolments"
Cohesion: 0.40
Nodes (5): get_admin_roster(), legacy_user_history(), Merge seed enrolments with any runtime mutations., ICatalogSync.fetchUserHistory() — consumed by MockIgotPlatformAdapter., _user_enrolments()

### Community 7 - "Admin console tier"
Cohesion: 0.06
Nodes (67): Admin console tier, AdminChatWidget(), AdminChatWidgetProps, CAPABILITIES, SUGGESTION_KEYS, MessageBubble(), NavConfirmBanner(), renderMarkdown() (+59 more)

### Community 8 - "karma.py"
Cohesion: 0.16
Nodes (23): fastapi_concurrency, KarmaEvent, Immutable ledger entry — one row per karma point award event., admin_adjust_karma(), AdminAdjustRequest, _assert_self_or_admin(), award_karma_event(), _award_response() (+15 more)

### Community 9 - "Timeline"
Cohesion: 0.17
Nodes (4): Performance, Evidence, Append another timeline's records, renumbered after this one's, plus its drop…, Timeline

### Community 10 - "ytrelay.py"
Cohesion: 0.09
Nodes (35): concurrent_futures, _benched(), candidates(), _clean(), _client(), diagnosis(), _discover(), download() (+27 more)

### Community 11 - "test_doc_quiz.py"
Cohesion: 0.13
Nodes (17): Document quiz: extraction (DOCX, OCR), cited multi-type generation, grading…, _chunks(), _mcq(), parametrize, services/doc_quiz — question types, validator, dedup, selection, calibration,…, test_choice_feedback_uses_option_rationale(), test_courses_for_topics_prefers_competency_courses(), test_fill_blank_and_true_false_rules() (+9 more)

### Community 12 - "Code"
Cohesion: 0.15
Nodes (26): Connections, Code, WhyThisLevel(), rows_for(), tag_id(), _completed_courses(), _education_score(), enrollment_course_id() (+18 more)

### Community 13 - "UserAuth"
Cohesion: 0.08
Nodes (43): AuthBase, fastapi, auth/dependencies.py…, Returns a FastAPI dependency that checks the current user's role. Example:…, require_role(), UserAuth, career_readiness(), _dispute_view() (+35 more)

### Community 14 - "download_model.py"
Cohesion: 0.14
Nodes (20): onnx_model_dir(), get_reranker(), ndarray, FILE: ai/reranker.py…, Cross-encoder scores for `passages` against `query`, or None if no reranker., Relevance logits, one per (query, passage) pair (higher = better match)., The loaded cross-encoder, or None when disabled / unavailable (logged once)., rerank_scores() (+12 more)

### Community 15 - "generate.py"
Cohesion: 0.08
Nodes (44): _generate_questions(), Cited, validated, multi-type questions (services/doc_quiz/generate.py) →…, _call(), _density(), difficulty_quotas(), DocChunk, excerpt(), generate() (+36 more)

### Community 16 - "gemini_json"
Cohesion: 0.13
Nodes (26): LLM providers (Groq multi-key → Gemini), gemini_json(), gemini_key(), _groq_json(), llm_configured(), ollama_vision_json(), parse_json(), Any (+18 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "3. Core data flow"
Cohesion: 0.07
Nodes (23): 3. Core data flow, _course_summary(), _diagnostic_step(), _fmt_levels(), absorb(), add_step(), advance(), open_ladders() (+15 more)

### Community 19 - "test_pathway.py"
Cohesion: 0.07
Nodes (31): test_mandatory_courses_always_included_with_badge(), test_why_recommended_describes_the_level_step(), _edge(), _gap(), _kinds_levels(), Skill-gap levels + level-aware recommendations + learning pathways. Runs on a…, Bug #11: the block used to come back in level order, so a weak course sat above…, Bugs #9/#10: relevance and quality were min-maxed inside the shortlist, so the… (+23 more)

### Community 20 - "domain.ts"
Cohesion: 0.03
Nodes (77): CareerReadinessCard(), Props, TIER_LABEL, DEFER_REASON, KIND_STYLE, PathwayLadder(), LevelCheckModal(), OUTCOME (+69 more)

### Community 21 - "extractors.py"
Cohesion: 0.11
Nodes (28): add_captions(), flush(), _budget(), caption_regions(), describe_keyframes(), guarded(), run_batch(), get_whisper() (+20 more)

### Community 22 - "_fetch_youtube"
Cohesion: 0.13
Nodes (22): BaseException, _blocked_message(), cookies_path(), _fetch_youtube(), fetch(), has_cookies(), _is_blocked(), _is_fatal() (+14 more)

### Community 23 - "LiveIgotAdapter"
Cohesion: 0.14
Nodes (12): Live iGOT (the real portal), LiveIgotAdapter, Any, AsyncClient, Pooled client per event loop — the warm-up thread runs its own., Every Live course, normalised to the internal catalogue shape. Pages POST…, POST /api/content/v1/search — every page, raw upstream records. `filters` takes…, One page, with the retry matched to the failure: * read timeout, or a… (+4 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "ai_tools.py"
Cohesion: 0.07
Nodes (40): Code, Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, dotenv, build_system_prompt(), generate_chat_response() (+32 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "media_quiz.py"
Cohesion: 0.12
Nodes (29): fastapi_responses, ImportError, importlib_util, _cached_result(), capabilities(), _importable(), MediaMetadata, MediaQuizQuestion (+21 more)

### Community 28 - "WorkforceInsights.tsx"
Cohesion: 0.10
Nodes (26): AGENDA_TYPE, CapabilityRiskPanel(), ForesightPanel(), GsbpmScopePanel(), pct(), PrerequisitePanel(), PRIORITY_CHIP, RISK_CHIP (+18 more)

### Community 29 - "admin_chat_data.py"
Cohesion: 0.15
Nodes (23): behind_facts(), _clean(), competency_names(), department_facts(), find_officials(), _full_name(), learner_db_facts(), _name_tokens() (+15 more)

### Community 30 - "competency_service.py"
Cohesion: 0.24
Nodes (7): CompetencyCalculator, datetime, FILE: main-lms-backend/services/competency_service.py…, Maps FRAC types from the JSON to calculation categories., Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, test_missing_channels_do_not_drag_the_score_to_zero()

### Community 31 - "react"
Cohesion: 0.06
Nodes (65): `frontend/src/`, Accessibility preferences, GIGW compliance & accessibility (frontend chrome), Other GIGW / WCAG work applied across the app, Statutory pages, The chrome, and where it comes from, TODO, Verifying a change here (+57 more)

### Community 32 - "AwardResult"
Cohesion: 0.14
Nodes (12): AdminAdjustmentStrategy, AwardResult, CompletionKarmaStrategy, IKarmaStrategy, ABC, Computes the base points for an event (before the engine's idempotency, per-day…, +5 on self-registration; MDO-onboarded users are not eligible., +5 per completion; non-CBP completions capped per IST calendar month. (+4 more)

### Community 33 - "chat_messages/__init__.py"
Cohesion: 0.14
Nodes (23): functools, importlib, _intercept(), Deterministic handling of English commands the classifier has historically…, _by_page(), _gap_lines(), _greeting(), _landing_section() (+15 more)

### Community 34 - "test_irt.py"
Cohesion: 0.27
Nodes (12): laplace_posterior(), (mode, sd) of N(prior) × Π 2PL likelihoods, Laplace approximation. responses =…, _bank(), _grid_posterior(), Tier-1 2PL posterior + adaptive diagnostic (SCIL v6 §2). pytest…, _run(), test_answering_the_wrong_item_or_after_the_end_is_rejected(), test_correct_answers_move_the_estimate_up_wrong_ones_down() (+4 more)

### Community 35 - "speech.d.ts"
Cohesion: 0.20
Nodes (6): SpeechRecognition, SpeechRecognitionEvent, SpeechRecognitionResult, SpeechRecognitionResultItem, SpeechRecognitionResultList, Window

### Community 36 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 37 - "resolve_level"
Cohesion: 0.22
Nodes (18): Single source of truth for an official's level on one competency. Every…, resolve_level(), fuse_channels(), Weighted mean over the K/A/U/S channels that carry evidence (None → absent)., _assess(), SCIL v6 §3 evidence channels K/A/U/S (knowledge, application, utility,…, _row(), test_confirmed_use_is_a_floor_unconfirmed_is_not() (+10 more)

### Community 38 - "mock_igot_server.py"
Cohesion: 0.08
Nodes (35): exception_handler, HTTPException, CompetencyOut, CompositeSearchRequest, ContentStateRequest, _course_by_id(), CourseOut, EnrolPayload (+27 more)

### Community 39 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 40 - "apply_crosswalk"
Cohesion: 0.19
Nodes (13): apply_crosswalk(), Any, Rewrite each live course's `competencies_v6` theme refIds to catalogue FRAC ids…, _engine(), Unmapped is not the same as untagged: the course is still indexed, just under a…, Mock data and the minority of live courses that kept CID tags must behave…, One competencies_v6 tag, in the shape /api/content/v1/search returns., test_apply_crosswalk_stamps_frac_ids_in_place_and_leaves_the_rest() (+5 more)

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 42 - "irt_service.py"
Cohesion: 0.22
Nodes (10): DiagnosticSessions, fisher_information(), next_item(), p_correct(), public_item(), Any, services/irt_service.py — Tier-1 Bayesian 2PL posterior + adaptive diagnostic…, What the learner sees: no answer key, no parameters. (+2 more)

### Community 43 - "Code"
Cohesion: 0.13
Nodes (16): Code, _competencies(), fetch(), fetch(), fetch(), fetch(), _prof_detail(), AsyncClient (+8 more)

### Community 44 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 45 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 46 - "test_mock_data.py"
Cohesion: 0.09
Nodes (9): Mock-data generator (mock-igot-server/generate_mock_data.py): determinism, one…, _tags(), test_acbp_mandatory_courses_are_short_catalogue_courses(), test_course_outcomes_are_consistent_with_catalogue_and_roster(), test_ladders_are_complete_except_documented_holes(), test_officials_mostly_study_at_or_just_above_their_level(), test_role_competencies_and_tags_use_catalogue_ids(), test_secondary_tags_are_overlaps_at_compatible_levels() (+1 more)

### Community 49 - "models/models.py"
Cohesion: 0.08
Nodes (40): 7. Mismatches between the mermaid diagram and the code, Base, Conventions, TODOs / edge cases, Connections, In / out, Skill Gap Analysis (evidence-based competency baselines), TODOs / edge cases (+32 more)

### Community 54 - "test_admin_chat.py"
Cohesion: 0.16
Nodes (24): ask(), client(), fixture, Gyan on the admin console: routers/admin_chat.py end to end, with the roster,…, Both classifiers answer fixed (intent, confidence) pairs — no embedder., stub_intents(), test_a_department_named_in_the_message_scopes_the_answer(), test_a_shared_surname_asks_which_official() (+16 more)

### Community 58 - "opportunity"
Cohesion: 0.24
Nodes (13): opportunity(), Any, services/gsbpm_service.py — GSBPM scoping (SCIL v6 §1) + opportunity to…, Opportunity to practise a competency in the official's office this cycle (SCIL…, Which competencies are in scope under the officer-hours rule, and why., scope_report(), _sp_name(), subprocess_hours() (+5 more)

### Community 60 - "test_certificate_evidence.py"
Cohesion: 0.07
Nodes (41): fastapi_testclient, get_db(), auth/database.py…, FastAPI dependency — `db: Session = Depends(get_db)`; closed after the request., auth/models.py…, feedback_summary(), FeedbackBody, my_feedback() (+33 more)

### Community 61 - "media_io.py"
Cohesion: 0.11
Nodes (30): _cache_dir(), cache_load(), _cache_root(), cache_store(), _cache_sweep(), Caption, _check_duration(), _download_dir() (+22 more)

### Community 62 - "admin_console.py"
Cohesion: 0.07
Nodes (69): AdminDailySnapshot, One row per calendar day (UTC): the workforce headline numbers plus the same…, An admin assigning courses (a training plan) to a department or a list of…, A reminder sent by an admin to an official behind on mandatory (ACBP) training., TrainingAssignment, TrainingNudge, AdminChatFilters, AdminChatRequest (+61 more)

### Community 63 - "MockIgotAdapter"
Cohesion: 0.10
Nodes (18): Cross-competency prerequisite DAG (SCIL v6 §5, B4), GSBPM scope — the 80% officer-hours rule (SCIL v6 §1), Reference data loading, TODOs / limits, Used by the admin console, Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight), MockIgotAdapter, Forget every cached read for this user. (+10 more)

### Community 64 - "LearnerDashboard.tsx"
Cohesion: 0.04
Nodes (82): Admin Dashboard, Code, TODOs / edge cases, What the synthetic data shows, Code, Connections, In / out, Learner Dashboard (frontend shell) (+74 more)

### Community 65 - "items.py"
Cohesion: 0.23
Nodes (28): ast, Document question pipeline (`main-lms-backend/services/doc_quiz/`), TODOs / edge cases, _build_review(), Type-aware answer review, missed questions first. Each wrong answer gets…, accepted_texts(), answer_display(), _choice_set() (+20 more)

### Community 66 - "numpy"
Cohesion: 0.06
Nodes (54): _get(), live_metrics(), _login(), main(), offline_metrics(), _pct(), Mock-data quality metrics — run before/after regenerating mock data. cd main-…, Admin bearer header; retried while the backend (--reload) restarts. (+46 more)

### Community 67 - "Random"
Cohesion: 0.21
Nodes (15): build_catalog(), build_officials(), build_role(), _course_id(), _covariates(), _designation(), _hours_for(), price collection and quote validation' → 'Price Collection and Quote… (+7 more)

### Community 68 - "ExtractionError"
Cohesion: 0.24
Nodes (10): DocumentExtractorService, ExtractionError, _gemini_extract(), _ocr(), _pdf_text_and_images(), ValueError, Text layer + (for scans) the embedded page images of the first pages., `await extract(data, filename)` — Gemini if configured, else OCR + e5. (+2 more)

### Community 69 - "Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)"
Cohesion: 0.12
Nodes (17): 1. Runtime topology, 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator (+9 more)

### Community 70 - "AssessmentPage.tsx"
Cohesion: 0.19
Nodes (15): Gyan hand-off (document → quiz or Learning Mode, no second upload), AssessmentPage(), DIFFICULTIES, Difficulty, errorText(), formatDate(), guessUploadFormat(), LANGUAGES (+7 more)

### Community 71 - "rag.py"
Cohesion: 0.07
Nodes (57): Code, Code, Connections, Personalised feedback (`items.feedback`), ErrorResponse, _generate_overview(), learning_chat(), LearningChatMessage (+49 more)

### Community 72 - "kcm_crosswalk.py"
Cohesion: 0.24
Nodes (9): main(), _write(), build_crosswalk(), _derive_threshold(), ndarray, services/kcm_crosswalk.py — Karmayogi Competency Model → catalogue FRAC ids…, How close is "close enough"? Take the distribution of cosines between DISTINCT…, Propose KCM theme → FRAC competency mappings. `kcm_terms` are the framework's… (+1 more)

### Community 74 - "CourseCard.tsx"
Cohesion: 0.18
Nodes (14): BADGE_STYLE, CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBar(), MatchScoreBarProps, MODALITY_LABEL, SOURCE_STYLES (+6 more)

### Community 75 - "get_embedder"
Cohesion: 0.06
Nodes (36): collections, difflib, Code, _Embedder, encode_cached(), get_embedder(), _load(), _OnnxEmbedder (+28 more)

### Community 76 - "chatbot.py"
Cohesion: 0.23
Nodes (16): ChatHistoryItem, ChatRequest, ChatResponse, _intent_response(), BaseModel, FILE: routers/chatbot.py Multilingual AI Learning Assistant — Gyan (ज्ञान)…, RecommendationContext, _response() (+8 more)

### Community 77 - "api.ts"
Cohesion: 0.04
Nodes (102): Frontend, AdminActions(), AssignForm(), when(), AdminFilterBar(), ExportButton(), facetLabels(), describeFilters() (+94 more)

### Community 87 - "catalogue_source.py"
Cohesion: 0.19
Nodes (14): _apply_crosswalk(), configured_source(), fetch(), is_live(), _load_disk_catalogue(), Any, services/catalogue_source.py — where the course catalogue comes from The…, The catalogue to rank over, plus the resolved source label. Raises only if… (+6 more)

### Community 88 - "CertificateUploadZone.tsx"
Cohesion: 0.31
Nodes (7): CertificateUploadZone(), clean(), STATUS_CHIP, CertificateStatus, CertificateSubmission, fetchMyCertificates(), uploadCertificate()

### Community 89 - "proficiency_service.py"
Cohesion: 0.16
Nodes (17): cluster_of(), cohort_prior(), expected_shortfall(), months_between(), office_phase(), _phi(), proficiency_state(), Any (+9 more)

### Community 90 - "post"
Cohesion: 0.12
Nodes (24): contextlib, post(), enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history() (+16 more)

### Community 91 - "Any"
Cohesion: 0.09
Nodes (17): ILearningPlatformAdapter, ABC, Any, The full CBP course catalogue, paged through POST /api/composite/v1/search.…, POST /api/composite/v1/search — Sunbird composite search, every page. `filters`…, GET /api/frac/competencies — the catalogue FRAC set incl. L1–L5 descriptors., GET /api/frac/v1/crosswalk — iGOT dictionary CID id → catalogue FRAC id., GET /api/admin/v1/users Returns: result.users — full list of officials. (+9 more)

### Community 92 - "Media (Video / Audio / YouTube) → Evidence-Cited Quiz"
Cohesion: 0.29
Nodes (6): In / out, Media (Video / Audio / YouTube) → Evidence-Cited Quiz, Pipeline, Setup, TODOs / edge cases, Verification

### Community 93 - "Keyframe"
Cohesion: 0.31
Nodes (9): _change(), Keyframe, load_audio(), ndarray, (share of pixels changed, share of the frame covered by their bounding box)., _resize(), scan_video(), _select_keyframes() (+1 more)

### Community 94 - "calibration.py"
Cohesion: 0.21
Nodes (13): Difficulty calibration (`services/doc_quiz/calibration.py`), calibrate(), calibrate_items(), difficulty_from_b(), load_stats(), Any, FILE: services/doc_quiz/calibration.py…, responses: [{key, correct, llm_difficulty, type, question}] from ONE first… (+5 more)

### Community 95 - "QuizQuestionInput.tsx"
Cohesion: 0.16
Nodes (21): Frontend, emptyAnswer(), hindi(), isAnswered(), pick(), Props, qType(), QuizLang (+13 more)

### Community 96 - "workforce_service.py"
Cohesion: 0.24
Nodes (16): How the parts work, _Phi(), _as_date(), capability_risk(), cell(), foresight(), _level(), _p_capable() (+8 more)

### Community 97 - "ReplyContext"
Cohesion: 0.12
Nodes (22): Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile(), Any, Everything a reply template may personalise, built once per chat request., ReplyContext, Localized reply for `intent`; unknown intents get the page's fallback reply., render(), _alternatives() (+14 more)

### Community 98 - "Mock iGOT Karmayogi Integration (Adapter + mock server + mock data)"
Cohesion: 0.50
Nodes (4): Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server + mock data), TODOs / edge cases

### Community 99 - "system_health.py"
Cohesion: 0.21
Nodes (22): is_embedder_ready(), model_name(), Non-blocking check — True only if the role's model is already loaded., is_semantic_engine_ready(), admin_chat_mode(), get, chat_mode(), get (+14 more)

### Community 100 - "Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)"
Cohesion: 0.50
Nodes (4): Cold start for UNASSESSED competencies, Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8), Foresight, Proficiency belief with dated decay

### Community 101 - "karma_engine.py"
Cohesion: 0.21
Nodes (10): KarmaEventType, FixedPointsStrategy, ist_date(), ist_day_start_utc(), KarmaRule, date, datetime, services/karma_engine.py… (+2 more)

### Community 102 - "competency.py"
Cohesion: 0.09
Nodes (33): datetime, CertificateSubmission, One uploaded certificate (routers/competency.py). On upload each extracted…, certificates_for_review(), _find(), my_certificates(), get, UploadFile (+25 more)

### Community 103 - "typing"
Cohesion: 0.08
Nodes (38): asyncio, dataclasses, httpx, json, logging, adapters/igot_adapter.py — iGOT Platform Adapter…, adapters/live_igot_adapter.py — the REAL iGOT Karmayogi platform (read-only)…, FILE: ai/rag_engine.py… (+30 more)

### Community 104 - "LearningChat.tsx"
Cohesion: 0.26
Nodes (12): ChatEntry, LearningChat(), LearningChatProps, fetchWithTimeout(), LearningChatResponse, LearningChatTurn, LearningCitation, LearningMetadata (+4 more)

### Community 105 - "practice_assessment.py"
Cohesion: 0.08
Nodes (42): Practice ability (`main-lms-backend/services/practice_assessment.py`), grade_quiz(), _question_difficulties(), **Grade Quiz → Skill Gap** - user_id comes from the JWT…, Per-question difficulty for grading, calibrated from response data…, bump(), courses_for_topics(), latest_practice_value() (+34 more)

### Community 106 - "Deploy: backend on Oracle Cloud, frontend on Vercel"
Cohesion: 0.22
Nodes (8): 1. Create the VM (Oracle Cloud console), 2. Pick the API hostname, 3. Set up the VM, 4. Frontend on Vercel, Deploy: backend on Oracle Cloud, frontend on Vercel, Troubleshooting, Updating: just `git push` to `main`, YouTube links on the VM

### Community 107 - "warm_up"
Cohesion: 0.29
Nodes (8): on_event, _warm_media_models(), Load the CPU models (RapidOCR, Silero VAD, Whisper, e5) off the request path,…, warm_up(), e5(), frac(), competency_name(), frac_competencies()

### Community 108 - "Decisions log (made without the user)"
Cohesion: 0.22
Nodes (7): Before / after metrics, Could not do / blocked, Decisions log (made without the user), Noticed but out of scope (not fixed), SCIL v6 — mock data + blocked features: progress report, Status, Catalogue duration in hours, or None for a course not in the catalogue.

### Community 109 - "get_enriched_courses"
Cohesion: 0.33
Nodes (7): composite_search(), _course_tags(), _enriched_view(), get_enriched_courses(), _matches_filters(), Sunbird-style filters: each key → value or list of accepted values., The catalogue in the older "enriched" shape. Query params:…

### Community 110 - "admin_analytics.py"
Cohesion: 0.08
Nodes (48): Backend, overview(), _competency_metrics(), daily_metrics(), by(), dept_compliance(), emerging_skills(), facets() (+40 more)

### Community 111 - "QuizSkillImpact.tsx"
Cohesion: 0.17
Nodes (10): Delta(), DIFF_CLASS, QuizQuestionReview(), QuizRecommendations(), signed(), SkillImpactCard(), TYPE_NAMES, QuizDifficulty (+2 more)

### Community 112 - "App.tsx"
Cohesion: 0.06
Nodes (34): AdminDashboard, App(), AssessmentPage, DashboardRedirect(), LearnerDashboard, TokenBridge(), ProtectedRoute(), ProtectedRouteProps (+26 more)

### Community 113 - "test_proficiency_foresight.py"
Cohesion: 0.18
Nodes (17): decay(), population_stats(), (μ_t, σ_t, λ) — relax the belief toward the population prior as evidence ages., comp → (μ_pop, σ_pop, n) over officials with assessed evidence on it., _hrms(), _official(), SCIL v6 §2 dated decay / expected-shortfall / cold start, and §11 workforce…, _snap() (+9 more)

### Community 114 - "BaselineAssembler"
Cohesion: 0.25
Nodes (7): BaselineAssembler, _normalise_course_map(), Accept {courseId: {compId: level}} or the legacy {courseId: [compId]}., test_verified_cert_lifts_confidence_over_documented(), The old `requiredLevel - 1` cap made every evidence-backed gap permanent., test_completion_evidence_follows_the_crosswalk(), test_evidence_can_close_a_gap()

### Community 117 - "_resolve_competency_state"
Cohesion: 0.33
Nodes (6): _load_db_evidence(), iGOT profile competencyLevel ('Level 3') → 3; missing → 0 (no claim)., The LMS's own EvidenceLog rows for one user (sync — run in a worker thread)., Profile + enrollments + EvidenceLog → one resolved row per role competency.…, _resolve_competency_state(), _self_reported_level()

### Community 119 - "probe.py"
Cohesion: 0.11
Nodes (24): VideoScan, _detector(), _limit_threads(), probe(), ProbeResult, ndarray, FILE: services/media_quiz/probe.py…, `regions` — precomputed speech spans (e.g. from YouTube captions) instead of… (+16 more)

### Community 123 - "admin_chat"
Cohesion: 0.15
Nodes (18): Code, classify_intent(), low_confidence_threshold(), Returns (best_intent, confidence). ("general", 0.0) if the embedder is…, admin_chat(), chat(), detect_intent_keyword(), Multilingual AI Learning Assistant — Gyan (ज्ञान). (+10 more)

### Community 124 - "_warm_up"
Cohesion: 0.07
Nodes (33): AbstractEventLoop, base64, Connections, In / out, Shared Embedder (chat + catalog roles), TODOs / edge cases, Measured uplift → coverage learning + training effectiveness (SCIL v6 §6, B5), Workforce snapshot (+25 more)

### Community 126 - "youtube_diagnosis"
Cohesion: 0.11
Nodes (11): _Collect, _count_formats(), _pick_captions(), _pot_provider_installed(), `ignore_no_formats_error` stops yt-dlp raising, but the reason — "Sign in to…, (url of a json3 track, kind, lang) — manual subtitles first, then original-…, (video-only/muxed formats we could use for frames, audio-bearing formats)., What can this host actually do with YouTube? Reports the yt-dlp version, the… (+3 more)

### Community 127 - "CLAUDE.md"
Cohesion: 0.30
Nodes (3): Certificate / Resume Evidence Extraction, In / out, TODOs / edge cases

### Community 128 - "test_chat_endpoint.py"
Cohesion: 0.44
Nodes (9): _chat(), parametrize, End-to-end /chat behaviour per language through the real multilingual…, test_dark_mode_action(), test_my_courses_navigation(), test_questions_answer_in_chat_without_navigating(), test_recommendations(), test_sidebar_section_navigation() (+1 more)

### Community 129 - "extract.py"
Cohesion: 0.16
Nodes (17): io, needs_ocr(), _ocr_engine(), ocr_pdf_pages(), OcrUnavailable, ndarray, RuntimeError, FILE: services/doc_quiz/extract.py… (+9 more)

### Community 130 - "generate"
Cohesion: 0.15
Nodes (17): build_crosswalk(), build_frac(), build_gsbpm_map(), build_hrms(), build_offices(), build_prerequisites(), dumps(), dumps_records() (+9 more)

### Community 131 - "_answer_admin"
Cohesion: 0.23
Nodes (33): Endpoints (`/api/v1/admin/console`, all take `?department=&grade=&office=`), _answer_admin(), _nav_action(), _official_reply(), (reply, navigate_action) for an admin-tier intent., ambiguous(), assignments(), _bullet() (+25 more)

### Community 132 - "ProviderError"
Cohesion: 0.14
Nodes (11): Exception, _family(), GroqProvider, _Key, parse_json_object(), ProviderError, Response, A provider could not produce a usable JSON answer. (+3 more)

### Community 133 - "test_per_user_reads_refuse_rather_than_return_empty"
Cohesion: 0.67
Nodes (3): parametrize, A wiring mistake must not look like "this official has no enrolments"., test_per_user_reads_refuse_rather_than_return_empty()

### Community 134 - "HybridRecommendationEngine"
Cohesion: 0.07
Nodes (40): Code, _by_score(), _clamp01(), _CourseDoc, GapEntry, HybridRecommendationEngine, _interleave_by_level(), _lex_ref() (+32 more)

### Community 135 - "safe_eval"
Cohesion: 0.20
Nodes (10): In / out, RAG Document → Quiz Generator & Grading (quiz ↔ skill gap), Verification, _computed_ok(), expression_numbers(), Evaluate +,-,*,/,**,%, parentheses and a few math functions. Raises ValueError…, Literal numbers used in an expression (for the 'inputs come from the source'…, safe_eval() (+2 more)

### Community 136 - "test_gap_and_recommendation_upgrades.py"
Cohesion: 0.10
Nodes (27): calculate_baseline(), CertificateReview, EvidencePayload, BaseModel, Stateless calculator for one competency, on exactly the scoring path the…, assess_competency(), explain_level(), datetime (+19 more)

### Community 137 - "generate_mock_data.py"
Cohesion: 0.18
Nodes (20): _batch(), build_acbp(), build_enrollments(), build_item_bank(), build_outcomes(), build_workplace_evidence(), course_hours(), course_tags() (+12 more)

### Community 139 - "CLAUDE.md — index & router"
Cohesion: 0.40
Nodes (5): CLAUDE.md — index & router, Feature index, graphify, How to use these docs, Run commands

### Community 141 - ".award_safe"
Cohesion: 0.25
Nodes (6): Connections, In / out, Karma Points (gamification), Rules (`RULES` in `karma_engine.py`, served by `GET /karma/rules`), TODOs / edge cases, For server-side hooks (quiz grading, diagnostics): own session, never raises.

### Community 143 - "Authentication & RBAC"
Cohesion: 0.40
Nodes (4): Authentication & RBAC, Connections, In / out, Shared database (Neon)

### Community 144 - "AI Course Recommendation Engine + Learning Pathways"
Cohesion: 0.40
Nodes (4): AI Course Recommendation Engine + Learning Pathways, Connections, In / out, {courseId: {compId: FRAC level}} — feeds BaselineAssembler so the Verified…

### Community 145 - "Learning Mode — NotebookLM-style study chat (AI Assessment Studio)"
Cohesion: 0.33
Nodes (5): Connections, In / out, Learning Mode — NotebookLM-style study chat (AI Assessment Studio), TODOs / edge cases, Verification

### Community 150 - "._load"
Cohesion: 0.22
Nodes (8): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only, Any, _read_disk(), data(), files(), fixture

### Community 151 - "_Attempt"
Cohesion: 0.18
Nodes (11): Getting past the bot check, When the wall is the IP itself, YouTube, _Attempt, fetch_watch_page(), parse_player_response(), What one player client managed to get. A client is useful if it returned…, (html, final url) for a plain watch-page GET — a different surface from the… (+3 more)

### Community 152 - "main-lms-backend/main.py"
Cohesion: 0.04
Nodes (70): fastapi_middleware_cors, get_current_user(), Decodes the Bearer JWT, looks up the user in auth.db. Raises HTTP 401 for any…, decode_access_token(), Decode and validate a JWT. Raises ValueError with a human-readable message on…, get_achievements(), get_achievements_by_user_id(), get_admin_roster() (+62 more)

### Community 153 - "engine"
Cohesion: 0.19
Nodes (14): on_event, Create users_auth table if it doesn't exist yet., _startup(), test_stored_embeddings_are_reused_only_when_text_matches(), test_tpac_boost_depends_on_provenance(), _course(), engine(), _frac() (+6 more)

### Community 154 - "ingest_telemetry"
Cohesion: 0.33
Nodes (5): field_validator, ingest_telemetry(), Returns a list of validation errors for a single telemetry event., TelemetryBatch, _validate_event()

### Community 155 - "_fit"
Cohesion: 0.67
Nodes (3): record(), _fit(), How much of a course's uplift a learner at `pre` can take from a Level-`level`…

### Community 156 - "_create_schema"
Cohesion: 0.50
Nodes (5): _create_schema(), _create(), Create users_auth and the karma/evidence tables if missing (idempotent)., migrate_karma_schema(), Idempotent upgrade for databases created before the daily-cap rework: adds…

### Community 157 - "pipeline.py"
Cohesion: 0.08
Nodes (36): argparse, csv, Code, main(), FILE: scripts/eval_media_quiz.py…, build_chunks(), Chunk, _make_chunk() (+28 more)

### Community 165 - "document_extractor.py"
Cohesion: 0.18
Nodes (21): Code, CertificateExtractionResult, _clamp_level(), ExtractedCompetency, frac_by_id(), frac_dictionary(), _issuer(), _level() (+13 more)

## Knowledge Gaps
- **325 isolated node(s):** `setup.sh script`, `name`, `private`, `version`, `type` (+320 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1208 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **46 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Admin console tier` connect `Admin console tier` to `workforce_service.py`, `chat_messages/__init__.py`, `ReplyContext`, `_answer_admin`, `get_embedder`, `api.ts`, `admin_chat`, `admin_chat_data.py`, `admin_console.py`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Why does `UserAuth` connect `UserAuth` to `router.py`, `system_health.py`, `document_extractor.py`, `competency.py`, `rag.py`, `karma.py`, `practice_assessment.py`, `admin_analytics.py`, `models/models.py`, `test_admin_chat.py`, `main-lms-backend/main.py`, `admin_chat`, `test_certificate_evidence.py`, `admin_console.py`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `Code` connect `HybridRecommendationEngine` to `LearnerDashboard.tsx`, `numpy`, `_answer_admin`, `CourseCard.tsx`, `Code`, `get_embedder`, `test_certificate_evidence.py`, `AI Course Recommendation Engine + Learning Pathways`, `models/models.py`, `BaselineAssembler`, `3. Core data flow`, `domain.ts`, `main-lms-backend/main.py`, `opportunity`, `_warm_up`, `MockIgotAdapter`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 81 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 81 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `HybridRecommendationEngine` (e.g. with `7. Mismatches between the mermaid diagram and the code` and `Code`) actually correct?**
  _`HybridRecommendationEngine` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `setup.sh script`, `name`, `private` to the rest of the system?**
  _325 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_live_catalogue.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._