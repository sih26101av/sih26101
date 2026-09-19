# Graph Report - SIH_IGot  (2026-09-19)

## Corpus Check
- 252 files · ~4,960,123 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .css 1, .example 1)

## Summary
- 2908 nodes · 7162 edges · 165 communities (127 shown, 38 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 812 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1b11c5b0`
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
- claim_cbp_bonus
- KarmaRewardsView.tsx
- Request
- pipeline.py
- Code
- UserAuth
- Timeline
- generate.py
- useSkillsData.ts
- What You Must Do When Invoked
- 3. Core data flow
- test_pathway.py
- domain.ts
- extractors.py
- media_io.py
- learning_mode.py
- compilerOptions
- vector_store.py
- 🇮🇳 MoSPI Skill Intelligence Platform
- media_quiz.py
- proficiency_service.py
- Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)
- competency_service.py
- LearnerDashboard.tsx
- chatbot.py
- api.ts
- AwardResult
- speech.d.ts
- graphify reference: extra exports and benchmark
- resolve_level
- mock_igot_server.py
- compilerOptions
- question_gen.py
- graphify reference: query, path, explain
- Admin Dashboard
- _learner_competency_state
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- test_mock_data.py
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- rag.py
- .claude/CLAUDE.md
- extraction-spec.md
- opportunity
- test_chat_messages.py
- estimate_uplift
- AssessmentPage.tsx
- MockIgotAdapter
- MediaQuizExtras.tsx
- items.py
- probe.py
- generate_mock_data.py
- test_gap_and_recommendation_upgrades.py
- Any
- get_embedder
- Code
- test_doc_quiz.py
- faker
- services_chat_messages
- services_chat_messages_context
- HybridRecommendationEngine
- lmsFetch
- bn.py
- en.py
- gu.py
- hi.py
- hi_latn.py
- mr.py
- or_.py
- ta.py
- te.py
- json
- chat
- Random
- mock-igot-server/main.py
- Code
- useLearnerDashboard.ts
- generate
- services/__init__.py
- competency.py
- test_certificate_evidence.py
- CourseCard.tsx
- lifespan
- system_health.py
- admin_console.py
- CertificateReviewQueue.tsx
- workforce_service.py
- SectionCard.tsx
- QuizSkillImpact.tsx
- practice_assessment.py
- AdminDashboard.tsx
- DashboardCreator
- Decisions log (made without the user)
- test_admin_analytics.py
- admin_analytics.py
- WorkforceInsights.tsx
- LearningChat.tsx
- _StubEmbedder
- _warm_up
- google_generativeai
- langchain_text_splitters
- mockdata
- pdfplumber
- document_extractor.py
- pptx
- pypdf
- requests
- diagnostic.py
- seed.py
- urllib_request
- KarmaEventType
- CLAUDE.md
- main-lms-backend/main.py
- calibration.py
- karma_engine.py
- recommendation_service.py
- ._load
- safe_eval
- reranker.py
- BaselineAssembler
- lucide-react
- authApi.ts
- Code
- build_outcomes
- TrendsPanel.tsx
- ingest_telemetry
- _db
- test_chat_endpoint.py
- Media (Video / Audio / YouTube) → Evidence-Cited Quiz
- CLAUDE.md — index & router
- Authentication & RBAC
- chat_actions.py
- Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)
- numpy
- Mock iGOT Karmayogi Integration (Adapter + mock server + mock data)
- services_media_quiz_llm
- services_media_quiz_pipeline
- _sunbird_result
- Learning Mode — NotebookLM-style study chat (AI Assessment Studio)
- CareerReadinessCard.tsx
- get_enriched_courses
- _create_schema
- facets
- reconstruct_history
- routers
- services
- services_media_quiz
- services_media_quiz_question_gen
- services_media_quiz_relevance

## God Nodes (most connected - your core abstractions)
1. `UserAuth` - 101 edges
2. `react` - 55 edges
3. `HybridRecommendationEngine` - 47 edges
4. `Code` - 46 edges
5. `MockIgotAdapter` - 39 edges
6. `Code` - 39 edges
7. `lucide-react` - 38 edges
8. `lmsFetch()` - 38 edges
9. `Code` - 38 edges
10. `Code` - 35 edges

## Surprising Connections (you probably didn't know these)
- ``frontend/src/`` --references--> `RightSidebar()`  [INFERRED]
  ARCHITECTURE.md → frontend/src/components/dashboard/RightSidebar.tsx
- `Code` --references--> `WhyThisLevel()`  [INFERRED]
  docs/features/skill-gap-analysis.md → frontend/src/components/dashboard/SkillGapCard.tsx
- `Code` --references--> `StatTone`  [INFERRED]
  docs/features/learner-dashboard.md → frontend/src/components/shell/StatCard.tsx
- `TODOs / edge cases` --references--> `gradeQuiz()`  [INFERRED]
  docs/features/media-quiz-generator.md → frontend/src/services/api.ts
- `7. Mismatches between the mermaid diagram and the code` --references--> `SkillGapReport`  [INFERRED]
  ARCHITECTURE.md → frontend/src/types/domain.ts

## Import Cycles
- None detected.

## Communities (165 total, 38 thin omitted)

### Community 0 - "ReplyContext"
Cohesion: 0.16
Nodes (19): importlib, Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile(), Any, Everything a reply template may personalise, built once per chat request., ReplyContext, _by_page(), _gap_lines() (+11 more)

### Community 1 - "QuizQuestionInput.tsx"
Cohesion: 0.19
Nodes (19): Frontend, emptyAnswer(), hindi(), isAnswered(), pick(), Props, qType(), QuizLang (+11 more)

### Community 2 - "Code"
Cohesion: 0.14
Nodes (14): Code, KarmaEvent, KarmaMonthlyUsage, Immutable ledger entry — one row per karma point award event., Rolling monthly counter for non-CBP COURSE_COMPLETION events. Enforces the…, KarmaEngine, MonthlyUsage, Session (+6 more)

### Community 3 - "router.py"
Cohesion: 0.08
Nodes (47): bcrypt, datetime, Code, hashlib, jose, get_db(), FastAPI dependency — `db: Session = Depends(get_db)`; closed after the request., change_password() (+39 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (43): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+35 more)

### Community 5 - "_require_auth"
Cohesion: 0.16
Nodes (25): get_assessment_outcomes(), get_gsbpm_map(), get_hrms_officials(), get_office(), get_offices(), get_prerequisites(), get_supervisor_ratings(), get_user_cbplan() (+17 more)

### Community 6 - "get"
Cohesion: 0.12
Nodes (18): get_admin_roster(), get_crosswalk(), get_org_roles(), get_user_enrolments(), health(), legacy_catalog(), legacy_frac(), legacy_job_profiles() (+10 more)

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.07
Nodes (49): `frontend/src/`, GyanBot(), GyanHero(), LanguageMenu(), LanguageMenuProps, CAPABILITIES, ChatWidget(), ChatWidgetProps (+41 more)

### Community 8 - "claim_cbp_bonus"
Cohesion: 0.18
Nodes (19): admin_adjust_karma(), AdminAdjustRequest, _assert_self_or_admin(), award_karma_event(), _award_response(), CbpClaimRequest, claim_cbp_bonus(), _enrollments_or_503() (+11 more)

### Community 9 - "KarmaRewardsView.tsx"
Cohesion: 0.10
Nodes (25): KarmaCard(), PassbookRow(), PILL_ORDER, RightSidebar(), RightSidebarProps, EVENT_META, formatPoints(), KarmaEventMeta (+17 more)

### Community 10 - "Request"
Cohesion: 0.18
Nodes (11): exception_handler, HTTPException, get_competencies(), get_item_bank(), get_job_profiles(), http_exc_handler(), 2PL MCQ item bank (a, b on the FRAC level scale, Bloom level, answer key).…, GET /api/job-profiles — NCO Job Role Catalogue (Sunbird-compliant). Served from… (+3 more)

### Community 11 - "pipeline.py"
Cohesion: 0.10
Nodes (29): csv, Code, main(), FILE: scripts/eval_media_quiz.py…, build_chunks(), slide_windows: [{"t_start", "t_end", "evidence_ids": [ocr/vlm ids of that…, fact_check(), translate_questions() (+21 more)

### Community 12 - "Code"
Cohesion: 0.17
Nodes (22): Code, rows_for(), tag_id(), _completed_courses(), _education_score(), enrollment_course_id(), _last_evidence_date(), _map_category() (+14 more)

### Community 13 - "UserAuth"
Cohesion: 0.06
Nodes (49): AuthBase, Returns a FastAPI dependency that checks the current user's role. Example:…, require_role(), UserAuth, get_achievements(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments() (+41 more)

### Community 14 - "Timeline"
Cohesion: 0.15
Nodes (7): Performance, Evidence, _make_chunk(), FILE: services/media_quiz/evidence.py…, Append another timeline's records, renumbered after this one's, plus its drop…, _tag(), Timeline

### Community 15 - "generate.py"
Cohesion: 0.09
Nodes (37): _generate_questions(), Cited, validated, multi-type questions (services/doc_quiz/generate.py) →…, _call(), _density(), difficulty_quotas(), DocChunk, excerpt(), generate() (+29 more)

### Community 16 - "useSkillsData.ts"
Cohesion: 0.50
Nodes (4): SkillRow, useSkillsData(), fetchCompetencies(), FracCompetency

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "3. Core data flow"
Cohesion: 0.12
Nodes (14): 3. Core data flow, absorb(), add_step(), advance(), open_ladders(), _parse_level(), _PrerequisiteGate, Any (+6 more)

### Community 19 - "test_pathway.py"
Cohesion: 0.07
Nodes (27): test_mandatory_courses_always_included_with_badge(), test_why_recommended_describes_the_level_step(), _edge(), _gap(), _kinds_levels(), Skill-gap levels + level-aware recommendations + learning pathways. Runs on a…, _resolved(), test_already_met_prerequisite_changes_nothing() (+19 more)

### Community 20 - "domain.ts"
Cohesion: 0.05
Nodes (40): DEFER_REASON, KIND_STYLE, PathwayLadder(), AppliedPrerequisite, CareerCompetency, CareerRoleOption, ColdStartPrior, Competency (+32 more)

### Community 21 - "extractors.py"
Cohesion: 0.09
Nodes (34): concurrent_futures, capabilities(), get, JSONResponse, add_captions(), flush(), _budget(), caption_regions() (+26 more)

### Community 22 - "media_io.py"
Cohesion: 0.13
Nodes (24): Caption, _change(), download_youtube(), fetch(), is_youtube_url(), Keyframe, load_audio(), MediaInputError (+16 more)

### Community 23 - "learning_mode.py"
Cohesion: 0.08
Nodes (47): Code, Code, Connections, Gemini model, Personalised feedback (`items.feedback`), ErrorResponse, _generate_overview(), learning_chat() (+39 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "vector_store.py"
Cohesion: 0.07
Nodes (36): Code, Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, build_system_prompt(), generate_chat_response(), Runs the full RAG pipeline: 1. Retrieve top-k relevant document chunks from… (+28 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "media_quiz.py"
Cohesion: 0.17
Nodes (20): fastapi_responses, importlib_util, MediaMetadata, MediaQuizQuestion, MediaQuizResponse, _process(), BaseModel, on_event (+12 more)

### Community 28 - "proficiency_service.py"
Cohesion: 0.06
Nodes (56): DiagnosticSessions, fisher_information(), laplace_posterior(), next_item(), p_correct(), public_item(), Any, services/irt_service.py — Tier-1 Bayesian 2PL posterior + adaptive diagnostic… (+48 more)

### Community 29 - "Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)"
Cohesion: 0.11
Nodes (16): 1. Runtime topology, 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator (+8 more)

### Community 30 - "competency_service.py"
Cohesion: 0.24
Nodes (7): CompetencyCalculator, datetime, FILE: main-lms-backend/services/competency_service.py…, Maps FRAC types from the JSON to calculation categories., Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, test_missing_channels_do_not_drag_the_score_to_zero()

### Community 31 - "LearnerDashboard.tsx"
Cohesion: 0.06
Nodes (52): Visual design system (shared by every page), App(), DashboardRedirect(), LearnerDashboard, AshokaChakra(), CountUp(), GovEmblem(), Reveal() (+44 more)

### Community 32 - "chatbot.py"
Cohesion: 0.33
Nodes (15): ChatResponse, _intent_response(), _intercept(), FILE: routers/chatbot.py Multilingual AI Learning Assistant — Gyan (ज्ञान)…, Deterministic handling of English commands the classifier has historically…, _response(), _theme_action(), _ui_action_response() (+7 more)

### Community 33 - "api.ts"
Cohesion: 0.06
Nodes (34): TokenBridge(), LevelCheckModal(), OUTCOME, Props, answerDiagnostic(), AssignmentInput, awardKarmaEvent(), BehindRow (+26 more)

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

### Community 38 - "mock_igot_server.py"
Cohesion: 0.15
Nodes (22): CompetencyOut, composite_search(), CompositeSearchRequest, ContentStateRequest, _course_by_id(), CourseOut, EnrolPayload, get_content_state() (+14 more)

### Community 39 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 40 - "question_gen.py"
Cohesion: 0.13
Nodes (28): Chunk, fmt_ts(), _match(), protect_terms(), FILE: services/media_quiz/fact_check.py…, Translate strings with glossary terms protected as ⟦Tn⟧. Returns (translations…, _reference(), restore_terms() (+20 more)

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 42 - "Admin Dashboard"
Cohesion: 0.22
Nodes (9): Admin Dashboard, Code, Endpoints (`/api/v1/admin/console`, all take `?department=&grade=&office=`), TODOs / edge cases, What the synthetic data shows, client(), roster(), fixture (+1 more)

### Community 43 - "_learner_competency_state"
Cohesion: 0.09
Nodes (26): Connections, _ensure_can_view(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments_by_user_id(), get_frac_competencies(), get_learning_pathway(), get_profile_by_user_id() (+18 more)

### Community 44 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 45 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 46 - "test_mock_data.py"
Cohesion: 0.08
Nodes (9): Mock-data generator (mock-igot-server/generate_mock_data.py): determinism, one…, _tags(), test_acbp_mandatory_courses_are_short_catalogue_courses(), test_course_outcomes_are_consistent_with_catalogue_and_roster(), test_ladders_are_complete_except_documented_holes(), test_officials_mostly_study_at_or_just_above_their_level(), test_role_competencies_and_tags_use_catalogue_ids(), test_secondary_tags_are_overlaps_at_compatible_levels() (+1 more)

### Community 49 - "rag.py"
Cohesion: 0.13
Nodes (27): 7. Mismatches between the mermaid diagram and the code, Base, enum, Admin, Assessment, AssessmentSkillMapping, BaseUser, CompetencyProfile (+19 more)

### Community 58 - "opportunity"
Cohesion: 0.15
Nodes (18): AI Course Recommendation Engine + Learning Pathways, Connections, In / out, TODOs / edge cases, opportunity(), Any, services/gsbpm_service.py — GSBPM scoping (SCIL v6 §1) + opportunity to…, Opportunity to practise a competency in the official's office this cycle (SCIL… (+10 more)

### Community 60 - "test_chat_messages.py"
Cohesion: 0.21
Nodes (12): Loads a language's template table on first use ("or" lives in or_.py; `or` is a…, templates(), _alternatives(), _fields(), parametrize, Catalogue completeness: every language has every template, placeholders are…, test_every_intent_renders(), test_placeholders_match_english() (+4 more)

### Community 61 - "estimate_uplift"
Cohesion: 0.07
Nodes (44): Cross-competency prerequisite DAG (SCIL v6 §5, B4), find_cycle(), infer_edges(), _node(), _norm_sf(), _ols(), Any, ndarray (+36 more)

### Community 62 - "AssessmentPage.tsx"
Cohesion: 0.17
Nodes (18): Gyan hand-off (document → quiz or Learning Mode, no second upload), AssessmentPage, AssessmentPage(), DIFFICULTIES, Difficulty, errorText(), formatDate(), guessUploadFormat() (+10 more)

### Community 63 - "MockIgotAdapter"
Cohesion: 0.10
Nodes (17): GSBPM scope — the 80% officer-hours rule (SCIL v6 §1), Reference data loading, TODOs / limits, Used by the admin console, Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight), MockIgotAdapter, Forget every cached read for this user., GET a Sunbird endpoint and return its `result` object. (+9 more)

### Community 64 - "MediaQuizExtras.tsx"
Cohesion: 0.16
Nodes (17): CONTENT_LABEL, MediaAnalysisCard(), MediaAnswerReview(), pct(), QuestionEvidence(), SOURCE_LABEL, YoutubeLinkInput(), formatTimestamp() (+9 more)

### Community 65 - "items.py"
Cohesion: 0.24
Nodes (27): ast, Document question pipeline (`main-lms-backend/services/doc_quiz/`), _build_review(), Type-aware answer review, missed questions first. Each wrong answer gets…, accepted_texts(), answer_display(), _choice_set(), correct_display() (+19 more)

### Community 66 - "probe.py"
Cohesion: 0.10
Nodes (27): dataclasses, _ocr_engine(), ocr_pdf_pages(), OcrUnavailable, ndarray, RuntimeError, FILE: services/doc_quiz/extract.py…, (text in reading order, mean confidence, weak lines dropped). (+19 more)

### Community 67 - "generate_mock_data.py"
Cohesion: 0.16
Nodes (16): _batch(), build_enrollments(), build_item_bank(), build_workplace_evidence(), iso(), _leaf_ids(), main(), _office_opportunity() (+8 more)

### Community 68 - "test_gap_and_recommendation_upgrades.py"
Cohesion: 0.12
Nodes (24): calculate_baseline(), EvidencePayload, BaseModel, Stateless calculator for one competency, on exactly the scoring path the…, assess_competency(), explain_level(), datetime, One competency, K/A/U/S fused — the scoring path shared by compute_for_user and… (+16 more)

### Community 69 - "Any"
Cohesion: 0.13
Nodes (12): ILearningPlatformAdapter, ABC, Any, The full CBP course catalogue, paged through POST /api/composite/v1/search.…, POST /api/composite/v1/search — Sunbird composite search, every page. `filters`…, Legacy method that maps fetch_user_enrollments to the old simple-mock shape.…, Interface for external learning platform integration. All concrete adapters…, Return the full CBP course catalog. (+4 more)

### Community 70 - "get_embedder"
Cohesion: 0.08
Nodes (34): difflib, Code, _Embedder, encode_cached(), get_embedder(), _load(), model_name(), onnx_model_dir() (+26 more)

### Community 71 - "Code"
Cohesion: 0.09
Nodes (30): Code, Opportunity to practise (SCIL v6 §4), CompetencyOverviewTable(), LevelPips(), priorityOf(), Props, StudyPlanSummary(), CHANNEL_LABEL (+22 more)

### Community 72 - "test_doc_quiz.py"
Cohesion: 0.09
Nodes (24): _opts(), Returns a normalised question dict or None (reason counted in stats)., translate(), validate(), _why_list(), Document quiz: extraction (DOCX, OCR), cited multi-type generation, grading…, has_blank(), with_canonical_blank() (+16 more)

### Community 76 - "HybridRecommendationEngine"
Cohesion: 0.10
Nodes (21): Code, _CourseDoc, GapEntry, HybridRecommendationEngine, ndarray, The id whose FRAC tags / levels / official text drive retrieval., Singleton — built ONCE at app startup. Holds FAISS index + BM25 corpus in…, `catalog` / `frac` / `crosswalk` are the lists served by the mock iGOT server… (+13 more)

### Community 77 - "lmsFetch"
Cohesion: 0.30
Nodes (14): AdminActions(), AssignForm(), when(), consoleQs(), createAssignment(), downloadAdminCsv(), fetchAdminTrends(), fetchAssignments() (+6 more)

### Community 87 - "json"
Cohesion: 0.13
Nodes (18): argparse, collections, io, json, load_eval(), main(), Benchmark Gyan's intent classifier on the held-out multilingual set. python…, _get() (+10 more)

### Community 88 - "chat"
Cohesion: 0.20
Nodes (15): low_confidence_threshold(), chat(), ChatHistoryItem, ChatRequest, detect_intent_keyword(), BaseModel, post, Multilingual AI Learning Assistant — Gyan (ज्ञान). (+7 more)

### Community 89 - "Random"
Cohesion: 0.19
Nodes (16): build_catalog(), build_offices(), build_officials(), build_role(), _course_id(), _covariates(), _designation(), _hours_for() (+8 more)

### Community 90 - "mock-igot-server/main.py"
Cohesion: 0.13
Nodes (22): contextlib, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history(), health() (+14 more)

### Community 91 - "Code"
Cohesion: 0.13
Nodes (16): AsyncClient, Code, _competencies(), fetch(), fetch(), fetch(), fetch(), _prof_detail() (+8 more)

### Community 92 - "useLearnerDashboard.ts"
Cohesion: 0.14
Nodes (17): Connections, In / out, Learner Dashboard (frontend shell), TODOs / edge cases, _cache, NO_ACHIEVEMENTS, NO_ENROLLMENTS, NO_GAPS (+9 more)

### Community 93 - "generate"
Cohesion: 0.15
Nodes (16): build_crosswalk(), build_frac(), build_gsbpm_map(), build_hrms(), build_prerequisites(), dumps(), dumps_records(), find_cycle() (+8 more)

### Community 94 - "services/__init__.py"
Cohesion: 0.13
Nodes (23): One learner interaction with a recommended course. `event` ∈ impression | click…, RecommendationFeedback, feedback_summary(), FeedbackBody, my_feedback(), post_feedback(), BaseModel, get (+15 more)

### Community 95 - "competency.py"
Cohesion: 0.15
Nodes (24): CertificateSubmission, Competency, EvidenceLog, One uploaded certificate (routers/competency.py). On upload each extracted…, CertificateReview, certificates_for_review(), _find(), my_certificates() (+16 more)

### Community 96 - "test_certificate_evidence.py"
Cohesion: 0.10
Nodes (24): dotenv, fastapi_security, fastapi_testclient, auth/database.py…, get_current_user(), Session, auth/dependencies.py…, Decodes the Bearer JWT, looks up the user in auth.db. Raises HTTP 401 for any… (+16 more)

### Community 97 - "CourseCard.tsx"
Cohesion: 0.19
Nodes (14): BADGE_STYLE, CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps, MODALITY_LABEL, SOURCE_STYLES, matches() (+6 more)

### Community 98 - "lifespan"
Cohesion: 0.33
Nodes (7): lifespan(), _load_json(), _load_json_from_dir(), Any, FastAPI, Load all datasets into memory once at startup, so no request touches the file…, Load a JSON file from ROOT_DIR. Raises RuntimeError on missing file.

### Community 99 - "system_health.py"
Cohesion: 0.26
Nodes (17): is_embedder_ready(), Non-blocking check — True only if the role's model is already loaded., is_semantic_engine_ready(), chat_mode(), get, Which response engine is active; the frontend shows it as a badge., basic(), _component() (+9 more)

### Community 100 - "admin_console.py"
Cohesion: 0.16
Nodes (32): fastapi_concurrency, An admin assigning courses (a training plan) to a department or a list of…, TrainingAssignment, _assignment_out(), _behind(), _behind_row(), _catalogue(), course_search() (+24 more)

### Community 101 - "CertificateReviewQueue.tsx"
Cohesion: 0.17
Nodes (14): CertificateReviewQueue(), Row(), STATUS_CLS, TABS, when(), CertificateUploadZone(), clean(), STATUS_CHIP (+6 more)

### Community 102 - "workforce_service.py"
Cohesion: 0.24
Nodes (16): How the parts work, _Phi(), _as_date(), capability_risk(), cell(), foresight(), _level(), _p_capable() (+8 more)

### Community 103 - "SectionCard.tsx"
Cohesion: 0.24
Nodes (7): STATUS, SystemHealthPanel(), SectionAction(), SectionCard(), SectionCardProps, fetchSystemHealth(), HealthStatus

### Community 104 - "QuizSkillImpact.tsx"
Cohesion: 0.15
Nodes (11): Delta(), DIFF_CLASS, DifficultyChip(), QuizQuestionReview(), QuizRecommendations(), signed(), SkillImpactCard(), TYPE_NAMES (+3 more)

### Community 105 - "practice_assessment.py"
Cohesion: 0.07
Nodes (50): Practice ability (`main-lms-backend/services/practice_assessment.py`), QuizAttempt, Persists every MCQ-quiz submission BEFORE evidence is written. UniqueConstraint…, _competency_rows(), grade_quiz(), Any, _question_difficulties(), The learner's resolved role competencies (same rows the skill-gap view shows),… (+42 more)

### Community 106 - "AdminDashboard.tsx"
Cohesion: 0.08
Nodes (41): Frontend, AdminDashboard, AdminFilterBar(), ExportButton(), facetLabels(), describeFilters(), esc(), printReport() (+33 more)

### Community 107 - "DashboardCreator"
Cohesion: 0.16
Nodes (4): AdminDashboardCreator, DashboardCreator, OfficialDashboardCreator, TrainerDashboardCreator

### Community 108 - "Decisions log (made without the user)"
Cohesion: 0.22
Nodes (7): Before / after metrics, Could not do / blocked, Decisions log (made without the user), Noticed but out of scope (not fixed), SCIL v6 — mock data + blocked features: progress report, Status, Catalogue duration in hours, or None for a course not in the catalogue.

### Community 109 - "test_admin_analytics.py"
Cohesion: 0.20
Nodes (15): emerging_skills(), datetime, Per FRAC competency, over the (filtered) officials in the workforce snapshot: *…, Admin console aggregates (services/admin_analytics.py): filters, pagination,…, _snap_row(), test_department_compliance_suppresses_small_departments(), test_emerging_skills_forecasts_shortfall_from_retirement_and_ranks_by_priority(), test_emerging_skills_recommends_commissioning_missing_catalogue_levels() (+7 more)

### Community 110 - "admin_analytics.py"
Cohesion: 0.15
Nodes (28): Backend, overview(), _competency_metrics(), daily_metrics(), by(), dept_compliance(), Filters, heatmap() (+20 more)

### Community 111 - "WorkforceInsights.tsx"
Cohesion: 0.10
Nodes (25): AGENDA_TYPE, CapabilityRiskPanel(), ForesightPanel(), GsbpmScopePanel(), pct(), PrerequisitePanel(), PRIORITY_CHIP, RISK_CHIP (+17 more)

### Community 112 - "LearningChat.tsx"
Cohesion: 0.27
Nodes (11): ChatEntry, LearningChat(), LearningChatProps, LearningChatResponse, LearningChatTurn, LearningCitation, LearningMetadata, LearningStartResponse (+3 more)

### Community 113 - "_StubEmbedder"
Cohesion: 0.31
Nodes (9): test_stored_embeddings_are_reused_only_when_text_matches(), test_tpac_boost_depends_on_provenance(), _course(), _frac(), Hashed bag-of-words → L2-normalised vector. Shared words ⇒ positive cosine., _StubEmbedder, test_classroom_cap_defers_the_ladder(), test_curated_crosswalk_is_used_before_embeddings() (+1 more)

### Community 114 - "_warm_up"
Cohesion: 0.08
Nodes (30): AbstractEventLoop, base64, Connections, In / out, Shared Embedder (chat + catalog roles), TODOs / edge cases, Measured uplift → coverage learning + training effectiveness (SCIL v6 §6, B5), Workforce snapshot (+22 more)

### Community 119 - "document_extractor.py"
Cohesion: 0.13
Nodes (31): Code, CertificateExtractionResult, _clamp_level(), DocumentExtractorService, ExtractedCompetency, ExtractionError, frac_by_id(), frac_dictionary() (+23 more)

### Community 123 - "diagnostic.py"
Cohesion: 0.09
Nodes (36): LevelDispute, status: OPEN (test started) → CONFIRMED | RAISED | LOWER_THAN_SHOWN once the…, career_readiness(), _dispute_view(), DisputeBody, _ensure_can_view(), my_disputes(), office_ladder() (+28 more)

### Community 124 - "seed.py"
Cohesion: 0.15
Nodes (18): hash_password(), Return a bcrypt hash of the plain-text password., _derive_password(), _fetch_officials(), main(), Session, auth/seed.py…, Insert the hardcoded admin user. Returns True if inserted, False if already… (+10 more)

### Community 126 - "KarmaEventType"
Cohesion: 0.20
Nodes (8): Connections, In / out, Karma Points (gamification), Rules (`RULES` in `karma_engine.py`, served by `GET /karma/rules`), TODOs / edge cases, KarmaEventType, Idempotency key for an event; None means 'not idempotent' (admin only)., For server-side hooks (quiz grading, diagnostics): own session, never raises.

### Community 127 - "CLAUDE.md"
Cohesion: 0.24
Nodes (7): Certificate / Resume Evidence Extraction, Connections, In / out, TODOs / edge cases, In / out, Skill Gap Analysis (evidence-based competency baselines), TODOs / edge cases

### Community 128 - "main-lms-backend/main.py"
Cohesion: 0.07
Nodes (44): asyncio, fastapi, fastapi_middleware_cors, httpx, logging, adapters/igot_adapter.py — iGOT Platform Adapter…, is_ollama_available(), FILE: ai/rag_engine.py… (+36 more)

### Community 129 - "calibration.py"
Cohesion: 0.16
Nodes (17): Difficulty calibration (`services/doc_quiz/calibration.py`), QuizItemStat, Response data per quiz item (services/doc_quiz/calibration.py). itemKey is a…, Stamp each item with its content key and its response-calibrated difficulty.…, _with_calibration(), calibrate(), calibrate_items(), difficulty_from_b() (+9 more)

### Community 130 - "karma_engine.py"
Cohesion: 0.20
Nodes (11): ist_date(), ist_day_start_utc(), ist_now(), KarmaRule, date, datetime, services/karma_engine.py…, Capped points earned today (IST) against DAILY_CAP, plus all points today. (+3 more)

### Community 131 - "recommendation_service.py"
Cohesion: 0.11
Nodes (20): _course_summary(), _diagnostic_step(), _fmt_levels(), _interleave_by_level(), BaseModel, FILE: main-lms-backend/services/recommendation_service.py…, Returns deduplicated, level-gated recommendations in gap-priority order. Only…, Step-by-step path for one competency: one course per FRAC level from current+1… (+12 more)

### Community 132 - "._load"
Cohesion: 0.22
Nodes (8): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only, Any, _read_disk(), data(), files(), fixture

### Community 133 - "safe_eval"
Cohesion: 0.18
Nodes (11): In / out, RAG Document → Quiz Generator & Grading (quiz ↔ skill gap), TODOs / edge cases, Verification, _computed_ok(), expression_numbers(), Evaluate +,-,*,/,**,%, parentheses and a few math functions. Raises ValueError…, Literal numbers used in an expression (for the 'inputs come from the source'… (+3 more)

### Community 134 - "reranker.py"
Cohesion: 0.20
Nodes (11): get_reranker(), ndarray, FILE: ai/reranker.py…, Cross-encoder scores for `passages` against `query`, or None if no reranker., Relevance logits, one per (query, passage) pair (higher = better match)., The loaded cross-encoder, or None when disabled / unavailable (logged once)., rerank_scores(), _Reranker (+3 more)

### Community 135 - "BaselineAssembler"
Cohesion: 0.25
Nodes (7): BaselineAssembler, _normalise_course_map(), Accept {courseId: {compId: level}} or the legacy {courseId: [compId]}., test_verified_cert_lifts_confidence_over_documented(), The old `requiredLevel - 1` cap made every evidence-backed gap permanent., test_completion_evidence_follows_the_crosswalk(), test_evidence_can_close_a_gap()

### Community 136 - "lucide-react"
Cohesion: 0.10
Nodes (20): COLORS, LearningSnapshot(), Props, MyCoursesView(), MyCoursesViewProps, formatDate(), ProfileHeader(), ProfileHeaderProps (+12 more)

### Community 137 - "authApi.ts"
Cohesion: 0.27
Nodes (11): AuthProvider(), mapRole(), changePassword(), extractError(), getMe(), login(), LoginResponse, logout() (+3 more)

### Community 138 - "Code"
Cohesion: 0.23
Nodes (12): Code, detect_chat_language(), detect_chat_variant(), detect_chat_variant_or_none(), _devanagari_language(), Small, offline language routing for Gyan chat. This deliberately does *not* use…, Supported ISO 639-1 code for a chat message., The variant the *text itself* signals, or None when it carries no signal. Plain… (+4 more)

### Community 139 - "build_outcomes"
Cohesion: 0.24
Nodes (10): build_acbp(), build_outcomes(), record(), course_hours(), course_tags(), _fit(), _mandatory_entry(), _mandatory_pick() (+2 more)

### Community 140 - "TrendsPanel.tsx"
Cohesion: 0.28
Nodes (8): fmtDate(), RANGES, RATE_SERIES, SERIES_DARK, SERIES_LIGHT, TrendsPanel(), recordAdminSnapshot(), TrendPoint

### Community 141 - "ingest_telemetry"
Cohesion: 0.29
Nodes (5): field_validator, ingest_telemetry(), Returns a list of validation errors for a single telemetry event., TelemetryBatch, _validate_event()

### Community 142 - "_db"
Cohesion: 0.09
Nodes (27): AdminDailySnapshot, One row per calendar day (UTC): the workforce headline numbers plus the same…, A reminder sent by an admin to an official behind on mandatory (ACBP) training., TrainingNudge, AssignmentIn, create_assignment(), create(), daily_snapshot_loop() (+19 more)

### Community 143 - "test_chat_endpoint.py"
Cohesion: 0.50
Nodes (7): _chat(), parametrize, End-to-end /chat behaviour per language through the real multilingual…, test_dark_mode_action(), test_my_courses_navigation(), test_recommendations(), test_skill_gaps()

### Community 144 - "Media (Video / Audio / YouTube) → Evidence-Cited Quiz"
Cohesion: 0.25
Nodes (7): In / out, Media (Video / Audio / YouTube) → Evidence-Cited Quiz, Pipeline, Setup, TODOs / edge cases, Verification, YouTube

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

### Community 149 - "numpy"
Cohesion: 0.32
Nodes (7): functools, competency_name(), frac_competencies(), FILE: services/media_quiz/relevance.py…, Sets chunk.relevance / chunk.competency_id, keeps the MAX_CHUNKS most relevant…, score_chunks(), numpy

### Community 150 - "Mock iGOT Karmayogi Integration (Adapter + mock server + mock data)"
Cohesion: 0.50
Nodes (4): Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server + mock data), TODOs / edge cases

### Community 153 - "_sunbird_result"
Cohesion: 0.25
Nodes (5): GET /api/frac/competencies — the catalogue FRAC set incl. L1–L5 descriptors., GET /api/frac/v1/crosswalk — iGOT dictionary CID id → catalogue FRAC id., GET /api/admin/v1/users Returns: result.users — full list of officials., Safely drill into a Sunbird envelope: data['result']['key1']['key2']..., _sunbird_result()

### Community 154 - "Learning Mode — NotebookLM-style study chat (AI Assessment Studio)"
Cohesion: 0.33
Nodes (5): Connections, In / out, Learning Mode — NotebookLM-style study chat (AI Assessment Studio), TODOs / edge cases, Verification

### Community 155 - "CareerReadinessCard.tsx"
Cohesion: 0.40
Nodes (5): CareerReadinessCard(), Props, TIER_LABEL, fetchCareerReadiness(), CareerReadiness

### Community 156 - "get_enriched_courses"
Cohesion: 0.40
Nodes (6): _course_tags(), _enriched_view(), get_enriched_courses(), _matches_filters(), Sunbird-style filters: each key → value or list of accepted values., The catalogue in the older "enriched" shape. Query params:…

### Community 157 - "_create_schema"
Cohesion: 0.50
Nodes (5): _create_schema(), _create(), Create users_auth and the karma/evidence tables if missing (idempotent)., migrate_karma_schema(), Idempotent upgrade for databases created before the daily-cap rework: adds…

### Community 158 - "facets"
Cohesion: 0.50
Nodes (3): filter_options(), facets(), Filter options with headcounts, from the whole (unfiltered) roster.

### Community 159 - "reconstruct_history"
Cohesion: 0.50
Nodes (3): date, Daily training-rate history rebuilt from dated iGOT course completions, for…, reconstruct_history()

## Knowledge Gaps
- **301 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+296 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1041 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `UserAuth` connect `UserAuth` to `test_certificate_evidence.py`, `main-lms-backend/main.py`, `router.py`, `admin_console.py`, `claim_cbp_bonus`, `practice_assessment.py`, `Admin Dashboard`, `_learner_competency_state`, `_db`, `admin_analytics.py`, `rag.py`, `document_extractor.py`, `services/__init__.py`, `diagnostic.py`, `seed.py`, `facets`, `competency.py`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `Code` connect `router.py` to `test_certificate_evidence.py`, `api.ts`, `authApi.ts`, `UserAuth`, `lmsFetch`, `Authentication & RBAC`, `seed.py`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `Code` connect `HybridRecommendationEngine` to `CourseCard.tsx`, `recommendation_service.py`, `Code`, `BaselineAssembler`, `_learner_competency_state`, `_warm_up`, `3. Core data flow`, `domain.ts`, `opportunity`, `Code`, `useLearnerDashboard.ts`, `estimate_uplift`, `services/__init__.py`, `MockIgotAdapter`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 78 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `HybridRecommendationEngine` (e.g. with `7. Mismatches between the mermaid diagram and the code` and `Code`) actually correct?**
  _`HybridRecommendationEngine` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 45 inferred relationships involving `Code` (e.g. with `KarmaCard()` and `formatPoints()`) actually correct?**
  _`Code` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _301 weakly-connected nodes found - possible documentation gaps or missing edges._