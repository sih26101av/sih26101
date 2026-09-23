# Graph Report - SIH_IGot  (2026-09-23)

## Corpus Check
- 277 files · ~5,006,293 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 6, .service 2, .example 2)

## Summary
- 3180 nodes · 8066 edges · 164 communities (121 shown, 43 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 901 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `97a11b5b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- document_extractor.py
- mediaQuizApi.ts
- _Session
- post
- package.json
- _require_auth
- get_user_enrolments
- ChatWidget.tsx
- karma.py
- Timeline
- KarmaRewardsView.tsx
- test_doc_quiz.py
- Code
- _workforce
- typing
- generate.py
- gemini_json
- What You Must Do When Invoked
- Any
- test_pathway.py
- domain.ts
- extractors.py
- media_io.py
- UserAuth
- compilerOptions
- ai_tools.py
- 🇮🇳 MoSPI Skill Intelligence Platform
- media_quiz.py
- generate
- learning_mode.py
- competency_service.py
- react
- karma_engine.py
- ReplyContext
- recommendation_service.py
- speech.d.ts
- graphify reference: extra exports and benchmark
- resolve_level
- mock_igot_server.py
- compilerOptions
- competency.py
- graphify reference: query, path, explain
- test_irt.py
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
- feedback_service.py
- extract.py
- admin_console.py
- Any
- LearnerDashboard.tsx
- items.py
- estimate_uplift
- generate_mock_data.py
- BaselineAssembler
- igot_adapter.py
- AssessmentPage.tsx
- rag.py
- seed.py
- faker
- services_chat_messages
- services_chat_messages_context
- chatbot.py
- AdminDashboard.tsx
- bn.py
- en.py
- gu.py
- hi.py
- hi_latn.py
- mr.py
- or_.py
- ta.py
- te.py
- api.ts
- CertificateReviewQueue.tsx
- test_proficiency_foresight.py
- mock-igot-server/main.py
- _sunbird_result
- Media (Video / Audio / YouTube) → Evidence-Cited Quiz
- proficiency_service.py
- calibration.py
- QuizQuestionInput.tsx
- test_certificate_evidence.py
- test_chat_messages.py
- build_enrollments
- system_health.py
- numpy
- ingest_telemetry
- workforce_service.py
- main-lms-backend/main.py
- LearningChat.tsx
- practice_assessment.py
- Deploy: backend on Oracle Cloud, frontend on Vercel
- CourseCard.tsx
- Decisions log (made without the user)
- get_enriched_courses
- admin_analytics.py
- QuizSkillImpact.tsx
- DiagnosticSessions
- test_gap_and_recommendation_upgrades.py
- _warm_up
- google_generativeai
- langchain_text_splitters
- mockdata
- pdfplumber
- probe.py
- pptx
- pypdf
- requests
- language_service.py
- _create_schema
- urllib_request
- MockIgotAdapter
- CLAUDE.md
- test_reply_regression.py
- Request
- mock_data_metrics.py
- Admin console tier
- routers
- .__init__
- HybridRecommendationEngine
- safe_eval
- engine
- KarmaEvent
- update.sh
- services
- youtube-access.sh
- lifespan
- vercel.json
- test_chat_endpoint.py
- Code
- Ollama RAG Knowledge Base (Tier 3 — disconnected)
- setup.sh
- services_media_quiz
- services_media_quiz_llm
- services_media_quiz_pipeline
- get_embedder
- Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)
- career_readiness
- Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)
- .award_safe
- _build_workforce_snapshot
- graphify reference: incremental update and cluster-only
- pipeline.py
- chat_actions.py
- mockdata/domain.py
- decay
- MonthlyUsage
- services_media_quiz_question_gen
- services_media_quiz_relevance

## God Nodes (most connected - your core abstractions)
1. `UserAuth` - 107 edges
2. `react` - 57 edges
3. `HybridRecommendationEngine` - 54 edges
4. `_Session` - 52 edges
5. `Code` - 48 edges
6. `Code` - 46 edges
7. `lucide-react` - 40 edges
8. `lmsFetch()` - 40 edges
9. `MockIgotAdapter` - 39 edges
10. `post()` - 39 edges

## Surprising Connections (you probably didn't know these)
- `Code` --references--> `MatchScoreBar()`  [INFERRED]
  docs/features/recommendation-engine.md → frontend/src/components/dashboard/CourseCard.tsx
- ``frontend/src/`` --references--> `RightSidebar()`  [INFERRED]
  ARCHITECTURE.md → frontend/src/components/dashboard/RightSidebar.tsx
- `Code` --references--> `WhyThisLevel()`  [INFERRED]
  docs/features/skill-gap-analysis.md → frontend/src/components/dashboard/SkillGapCard.tsx
- `Admin console tier` --references--> `AdminTab`  [INFERRED]
  docs/features/chatbot-gyan.md → frontend/src/pages/AdminDashboard.tsx
- `Code` --references--> `TabType`  [INFERRED]
  docs/features/chatbot-gyan.md → frontend/src/pages/LearnerDashboard.tsx

## Import Cycles
- None detected.

## Communities (164 total, 43 thin omitted)

### Community 0 - "document_extractor.py"
Cohesion: 0.13
Nodes (31): Code, CertificateExtractionResult, _clamp_level(), DocumentExtractorService, ExtractedCompetency, ExtractionError, frac_by_id(), frac_dictionary() (+23 more)

### Community 1 - "mediaQuizApi.ts"
Cohesion: 0.13
Nodes (21): CONTENT_LABEL, MediaAnalysisCard(), MediaAnswerReview(), pct(), QuestionEvidence(), SOURCE_LABEL, YoutubeLinkInput(), API_BASE_URL (+13 more)

### Community 2 - "_Session"
Cohesion: 0.18
Nodes (12): Code, KarmaEventType, ist_now(), KarmaEngine, Dispatches an eventType to its strategy, then applies the shared rules in…, Idempotency key for an event; None means 'not idempotent' (admin only)., DAILY_LOGIN for today, then any streak milestone the current streak has reached., Per-event-type total points. (+4 more)

### Community 3 - "post"
Cohesion: 0.08
Nodes (44): bcrypt, datetime, Code, fastapi_security, hashlib, jose, get_db(), FastAPI dependency — `db: Session = Depends(get_db)`; closed after the request. (+36 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (43): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+35 more)

### Community 5 - "_require_auth"
Cohesion: 0.14
Nodes (33): get_admin_roster(), get_assessment_outcomes(), get_course_catalog(), get_crosswalk(), get_gsbpm_map(), get_hrms_officials(), get_item_bank(), get_office() (+25 more)

### Community 6 - "get_user_enrolments"
Cohesion: 0.33
Nodes (6): get_user_enrolments(), legacy_user_history(), Merge seed enrolments with any runtime mutations., ICatalogSync.fetchUserHistory() — consumed by MockIgotPlatformAdapter., _user_by_id(), _user_enrolments()

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.07
Nodes (61): AdminChatWidget(), AdminChatWidgetProps, CAPABILITIES, SUGGESTION_KEYS, MessageBubble(), NavConfirmBanner(), renderMarkdown(), TypingIndicator() (+53 more)

### Community 8 - "karma.py"
Cohesion: 0.17
Nodes (21): fastapi_concurrency, admin_adjust_karma(), AdminAdjustRequest, _assert_self_or_admin(), award_karma_event(), _award_response(), CbpClaimRequest, claim_cbp_bonus() (+13 more)

### Community 9 - "Timeline"
Cohesion: 0.11
Nodes (22): dataclasses, Performance, build_chunks(), Chunk, Evidence, fmt_ts(), _make_chunk(), FILE: services/media_quiz/evidence.py… (+14 more)

### Community 10 - "KarmaRewardsView.tsx"
Cohesion: 0.10
Nodes (26): KarmaCard(), PassbookRow(), PILL_ORDER, RightSidebar(), RightSidebarProps, EVENT_META, formatPoints(), KarmaEventMeta (+18 more)

### Community 11 - "test_doc_quiz.py"
Cohesion: 0.13
Nodes (17): Document quiz: extraction (DOCX, OCR), cited multi-type generation, grading…, _chunks(), _mcq(), parametrize, services/doc_quiz — question types, validator, dedup, selection, calibration,…, test_choice_feedback_uses_option_rationale(), test_courses_for_topics_prefers_competency_courses(), test_fill_blank_and_true_false_rules() (+9 more)

### Community 12 - "Code"
Cohesion: 0.14
Nodes (29): Connections, Code, assess_competency(), rows_for(), tag_id(), _completed_courses(), _education_score(), enrollment_course_id() (+21 more)

### Community 13 - "_workforce"
Cohesion: 0.40
Nodes (6): _frac_names(), Draft TPAC agenda items from coverage gaps, capability risk, near-zero-uplift…, capability risk + foresight computed once per snapshot., _snapshot_or_503(), tpac_agenda(), _workforce()

### Community 14 - "typing"
Cohesion: 0.09
Nodes (24): collections, httpx, json, logging, FILE: ai/rag_engine.py…, _correct_tokens(), load_corpus(), FILE: ai/semantic_engine.py… (+16 more)

### Community 15 - "generate.py"
Cohesion: 0.09
Nodes (41): difflib, _call(), _density(), difficulty_quotas(), DocChunk, excerpt(), generate(), _index() (+33 more)

### Community 16 - "gemini_json"
Cohesion: 0.08
Nodes (38): LLM providers (Groq multi-key → Gemini), Exception, gemini_json(), gemini_key(), _groq_json(), llm_configured(), LLMUnavailable, ollama_vision_json() (+30 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "Any"
Cohesion: 0.11
Nodes (14): Measured uplift → coverage learning + training effectiveness (SCIL v6 §6, B5), absorb(), add_step(), advance(), open_ladders(), _PrerequisiteGate, Any, Orders the required rungs of several pathways into one sequence. SCIL v6 §5… (+6 more)

### Community 19 - "test_pathway.py"
Cohesion: 0.06
Nodes (33): test_mandatory_courses_always_included_with_badge(), test_why_recommended_describes_the_level_step(), _edge(), _gap(), _kinds_levels(), Skill-gap levels + level-aware recommendations + learning pathways. Runs on a…, Bug #11: the block used to come back in level order, so a weak course sat above…, Bugs #9/#10: relevance and quality were min-maxed inside the shortlist, so the… (+25 more)

### Community 20 - "domain.ts"
Cohesion: 0.05
Nodes (40): DEFER_REASON, KIND_STYLE, PathwayLadder(), AppliedPrerequisite, CareerCompetency, CareerRoleOption, ColdStartPrior, Competency (+32 more)

### Community 21 - "extractors.py"
Cohesion: 0.10
Nodes (29): concurrent_futures, add_captions(), flush(), _budget(), describe_keyframes(), guarded(), run_batch(), get_whisper() (+21 more)

### Community 22 - "media_io.py"
Cohesion: 0.06
Nodes (57): BaseException, When the wall is the IP itself, _blocked_message(), Caption, _change(), _Collect, cookies_path(), _count_formats() (+49 more)

### Community 23 - "UserAuth"
Cohesion: 0.06
Nodes (45): AuthBase, UserAuth, get_me(), get, Return the current authenticated user's profile. Used by the frontend to re-…, get_achievements(), get_achievements_by_user_id(), get_admin_roster() (+37 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "ai_tools.py"
Cohesion: 0.09
Nodes (33): Code, dotenv, io, is_ollama_available(), Fast, synchronous check — just hits the Ollama /api/tags endpoint. Returns True…, FILE: ai/seed_knowledge.py…, Embeds all baseline knowledge into ChromaDB., seed() (+25 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "media_quiz.py"
Cohesion: 0.10
Nodes (32): fastapi_responses, functools, ImportError, importlib_util, capabilities(), _importable(), MediaMetadata, MediaQuizQuestion (+24 more)

### Community 28 - "generate"
Cohesion: 0.12
Nodes (18): build_crosswalk(), build_frac(), build_gsbpm_map(), build_hrms(), build_prerequisites(), dumps(), dumps_records(), find_cycle() (+10 more)

### Community 29 - "learning_mode.py"
Cohesion: 0.22
Nodes (17): ErrorResponse, _generate_overview(), learning_chat(), LearningChatMessage, LearningChatRequest, LearningChatResponse, LearningCitation, LearningMetadata (+9 more)

### Community 30 - "competency_service.py"
Cohesion: 0.24
Nodes (7): CompetencyCalculator, datetime, FILE: main-lms-backend/services/competency_service.py…, Maps FRAC types from the JSON to calculation categories., Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, test_missing_channels_do_not_drag_the_score_to_zero()

### Community 31 - "react"
Cohesion: 0.05
Nodes (60): Visual design system (shared by every page), App(), DashboardRedirect(), TokenBridge(), AshokaChakra(), CountUp(), GovEmblem(), Reveal() (+52 more)

### Community 32 - "karma_engine.py"
Cohesion: 0.10
Nodes (21): AdminAdjustmentStrategy, AwardResult, CompletionKarmaStrategy, FixedPointsStrategy, IKarmaStrategy, ist_date(), ist_day_start_utc(), KarmaRule (+13 more)

### Community 33 - "ReplyContext"
Cohesion: 0.16
Nodes (19): importlib, Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile(), Any, Everything a reply template may personalise, built once per chat request., ReplyContext, _by_page(), _gap_lines() (+11 more)

### Community 34 - "recommendation_service.py"
Cohesion: 0.13
Nodes (18): _by_score(), _course_summary(), _diagnostic_step(), _fmt_levels(), _interleave_by_level(), BaseModel, FILE: main-lms-backend/services/recommendation_service.py…, Returns deduplicated, level-gated recommendations in gap-priority order. Only… (+10 more)

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
Cohesion: 0.11
Nodes (26): CompetencyOut, CompositeSearchRequest, ContentStateRequest, _course_by_id(), CourseOut, EnrolPayload, get_content_state(), health() (+18 more)

### Community 39 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 40 - "competency.py"
Cohesion: 0.08
Nodes (44): CertificateSubmission, LevelDispute, One uploaded certificate (routers/competency.py). On upload each extracted…, status: OPEN (test started) → CONFIRMED | RAISED | LOWER_THAN_SHOWN once the…, _dispute_view(), DisputeBody, _ensure_can_view(), my_disputes() (+36 more)

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 42 - "test_irt.py"
Cohesion: 0.18
Nodes (18): fisher_information(), laplace_posterior(), next_item(), p_correct(), services/irt_service.py — Tier-1 Bayesian 2PL posterior + adaptive diagnostic…, (mode, sd) of N(prior) × Π 2PL likelihoods, Laplace approximation. responses =…, _bank(), _grid_posterior() (+10 more)

### Community 43 - "Code"
Cohesion: 0.18
Nodes (12): 3. Core data flow, AsyncClient, Code, fetch(), fetch(), fetch(), Pooled client for the running loop — no new TCP connection per call., TTL memo for one user's read. Concurrent callers share one in-flight request;… (+4 more)

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
Cohesion: 0.12
Nodes (29): 7. Mismatches between the mermaid diagram and the code, Base, Conventions, Connections, In / out, Skill Gap Analysis (evidence-based competency baselines), TODOs / edge cases, enum (+21 more)

### Community 54 - "test_admin_chat.py"
Cohesion: 0.15
Nodes (25): ask(), client(), fixture, Gyan on the admin console: routers/admin_chat.py end to end, with the roster,…, Both classifiers answer fixed (intent, confidence) pairs — no embedder., stub_intents(), test_a_department_named_in_the_message_scopes_the_answer(), test_a_shared_surname_asks_which_official() (+17 more)

### Community 58 - "opportunity"
Cohesion: 0.24
Nodes (13): opportunity(), Any, services/gsbpm_service.py — GSBPM scoping (SCIL v6 §1) + opportunity to…, Opportunity to practise a competency in the official's office this cycle (SCIL…, Which competencies are in scope under the officer-hours rule, and why., scope_report(), _sp_name(), subprocess_hours() (+5 more)

### Community 60 - "feedback_service.py"
Cohesion: 0.16
Nodes (17): feedback_summary(), FeedbackBody, my_feedback(), post_feedback(), BaseModel, get, downvoted_ids(), Any (+9 more)

### Community 61 - "extract.py"
Cohesion: 0.13
Nodes (20): extract_docx(), needs_ocr(), _ocr_engine(), ocr_pdf_pages(), OcrUnavailable, ndarray, RuntimeError, FILE: services/doc_quiz/extract.py… (+12 more)

### Community 62 - "admin_console.py"
Cohesion: 0.07
Nodes (69): AdminDailySnapshot, One row per calendar day (UTC): the workforce headline numbers plus the same…, An admin assigning courses (a training plan) to a department or a list of…, A reminder sent by an admin to an official behind on mandatory (ACBP) training., TrainingAssignment, TrainingNudge, AdminChatFilters, AdminChatRequest (+61 more)

### Community 63 - "Any"
Cohesion: 0.16
Nodes (10): Cross-competency prerequisite DAG (SCIL v6 §5, B4), Any, GET a Sunbird endpoint and return its `result` object., GET /api/frac/v1/prerequisites — {count, edges[]} expert-seeded prerequisite…, GET /api/course/v1/assessment/outcomes — {outcomes[], comparisons[]} pre/post θ…, GET /api/assessment/v1/itembank — 2PL items incl. answer keys (server side…, GET /api/hrms/v1/officials — {officials{userId: DOB, superannuationDate,…, GET /api/org/v1/roles — {count, roles[{roleId, officeId, designation, tier,… (+2 more)

### Community 64 - "LearnerDashboard.tsx"
Cohesion: 0.04
Nodes (86): `frontend/src/`, Code, Connections, In / out, Learner Dashboard (frontend shell), Responsive layout (phones 360–430px, tablets 768–1024px), TODOs / edge cases, Opportunity to practise (SCIL v6 §4) (+78 more)

### Community 65 - "items.py"
Cohesion: 0.21
Nodes (29): ast, Document question pipeline (`main-lms-backend/services/doc_quiz/`), Personalised feedback (`items.feedback`), TODOs / edge cases, _build_review(), Type-aware answer review, missed questions first. Each wrong answer gets…, accepted_texts(), answer_display() (+21 more)

### Community 66 - "estimate_uplift"
Cohesion: 0.08
Nodes (43): find_cycle(), infer_edges(), _node(), _norm_sf(), _ols(), Any, ndarray, services/prerequisite_service.py — cross-competency prerequisite DAG (SCIL v6… (+35 more)

### Community 67 - "generate_mock_data.py"
Cohesion: 0.17
Nodes (25): build_catalog(), build_item_bank(), build_offices(), build_officials(), build_role(), build_workplace_evidence(), _course_id(), _covariates() (+17 more)

### Community 68 - "BaselineAssembler"
Cohesion: 0.25
Nodes (7): BaselineAssembler, _normalise_course_map(), Accept {courseId: {compId: level}} or the legacy {courseId: [compId]}., test_verified_cert_lifts_confidence_over_documented(), The old `requiredLevel - 1` cap made every evidence-backed gap permanent., test_completion_evidence_follows_the_crosswalk(), test_evidence_can_close_a_gap()

### Community 69 - "igot_adapter.py"
Cohesion: 0.12
Nodes (12): _competencies(), ILearningPlatformAdapter, _prof_detail(), ABC, adapters/igot_adapter.py — iGOT Platform Adapter…, Safely read a field from profileDetails.professionalDetails[0]., Return the competencies list from profileDetails.competencies., Interface for external learning platform integration. All concrete adapters… (+4 more)

### Community 70 - "AssessmentPage.tsx"
Cohesion: 0.18
Nodes (16): Gyan hand-off (document → quiz or Learning Mode, no second upload), AssessmentPage, AssessmentPage(), DIFFICULTIES, Difficulty, errorText(), formatDate(), guessUploadFormat() (+8 more)

### Community 71 - "rag.py"
Cohesion: 0.09
Nodes (47): Code, Code, Connections, QuizAttempt, Persists every MCQ-quiz submission BEFORE evidence is written. UniqueConstraint…, _chunk_document_text(), _clean_text(), _competency_rows() (+39 more)

### Community 72 - "seed.py"
Cohesion: 0.23
Nodes (12): hash_password(), Return a bcrypt hash of the plain-text password., _derive_password(), _fetch_officials(), main(), auth/seed.py…, Insert the hardcoded admin user. Returns True if inserted, False if already…, Default password = lowercase(firstName) + last 2 digits of the numeric userId… (+4 more)

### Community 76 - "chatbot.py"
Cohesion: 0.20
Nodes (24): Code, classify_intent(), low_confidence_threshold(), Returns (best_intent, confidence). ("general", 0.0) if the embedder is…, admin_chat(), chat(), ChatRequest, ChatResponse (+16 more)

### Community 77 - "AdminDashboard.tsx"
Cohesion: 0.06
Nodes (71): Frontend, AdminDashboard, AdminActions(), AssignForm(), when(), AdminFilterBar(), ExportButton(), facetLabels() (+63 more)

### Community 87 - "api.ts"
Cohesion: 0.05
Nodes (58): AGENDA_TYPE, CapabilityRiskPanel(), ForesightPanel(), GsbpmScopePanel(), pct(), PrerequisitePanel(), PRIORITY_CHIP, RISK_CHIP (+50 more)

### Community 88 - "CertificateReviewQueue.tsx"
Cohesion: 0.17
Nodes (14): CertificateReviewQueue(), Row(), STATUS_CLS, TABS, when(), CertificateUploadZone(), clean(), STATUS_CHIP (+6 more)

### Community 89 - "test_proficiency_foresight.py"
Cohesion: 0.21
Nodes (15): cohort_prior(), population_stats(), Cohort prior for an UNASSESSED competency, with the divergence check., comp → (μ_pop, σ_pop, n) over officials with assessed evidence on it., _hrms(), _official(), SCIL v6 §2 dated decay / expected-shortfall / cold start, and §11 workforce…, _snap() (+7 more)

### Community 90 - "mock-igot-server/main.py"
Cohesion: 0.12
Nodes (23): contextlib, fastapi_middleware_cors, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history() (+15 more)

### Community 91 - "_sunbird_result"
Cohesion: 0.22
Nodes (6): fetch(), GET /api/frac/competencies — the catalogue FRAC set incl. L1–L5 descriptors., GET /api/frac/v1/crosswalk — iGOT dictionary CID id → catalogue FRAC id., GET /api/admin/v1/users Returns: result.users — full list of officials., Safely drill into a Sunbird envelope: data['result']['key1']['key2']..., _sunbird_result()

### Community 92 - "Media (Video / Audio / YouTube) → Evidence-Cited Quiz"
Cohesion: 0.15
Nodes (10): Getting past the bot check, In / out, Media (Video / Audio / YouTube) → Evidence-Cited Quiz, Pipeline, Setup, TODOs / edge cases, Verification, YouTube (+2 more)

### Community 93 - "proficiency_service.py"
Cohesion: 0.19
Nodes (15): cluster_of(), expected_shortfall(), months_between(), office_phase(), _phi(), proficiency_state(), Any, datetime (+7 more)

### Community 94 - "calibration.py"
Cohesion: 0.21
Nodes (14): Difficulty calibration (`services/doc_quiz/calibration.py`), QuizItemStat, Response data per quiz item (services/doc_quiz/calibration.py). itemKey is a…, calibrate(), calibrate_items(), difficulty_from_b(), load_stats(), Any (+6 more)

### Community 95 - "QuizQuestionInput.tsx"
Cohesion: 0.19
Nodes (19): Frontend, emptyAnswer(), hindi(), isAnswered(), pick(), Props, qType(), QuizLang (+11 more)

### Community 96 - "test_certificate_evidence.py"
Cohesion: 0.15
Nodes (15): fastapi_testclient, client(), fixture, Admin console write actions end to end on an in-memory SQLite DB, with the…, test_nudge_only_officials_behind_and_respect_cooldown(), _u(), Certificate upload → EvidenceLog → admin review, end to end on in-memory SQLite…, _rows() (+7 more)

### Community 97 - "test_chat_messages.py"
Cohesion: 0.21
Nodes (13): Loads a language's template table on first use ("or" lives in or_.py; `or` is a…, templates(), _alternatives(), _fields(), parametrize, Catalogue completeness: every language has every template, placeholders are…, test_every_classifier_intent_has_a_reply(), test_every_intent_renders() (+5 more)

### Community 98 - "build_enrollments"
Cohesion: 0.16
Nodes (14): _batch(), build_acbp(), build_enrollments(), build_outcomes(), record(), course_hours(), course_tags(), _fit() (+6 more)

### Community 99 - "system_health.py"
Cohesion: 0.23
Nodes (21): is_embedder_ready(), model_name(), Non-blocking check — True only if the role's model is already loaded., is_semantic_engine_ready(), chat_mode(), get, Which response engine is active; the frontend shows it as a badge., groq_keys() (+13 more)

### Community 100 - "numpy"
Cohesion: 0.10
Nodes (26): _load(), onnx_model_dir(), _OnnxEmbedder, FILE: ai/embedder.py…, A directory written by scripts/download_model.py., sentence-transformers-compatible encoder on onnxruntime + HF `tokenizers`…, get_reranker(), ndarray (+18 more)

### Community 101 - "ingest_telemetry"
Cohesion: 0.29
Nodes (5): field_validator, ingest_telemetry(), Returns a list of validation errors for a single telemetry event., TelemetryBatch, _validate_event()

### Community 102 - "workforce_service.py"
Cohesion: 0.24
Nodes (16): How the parts work, _Phi(), _as_date(), capability_risk(), cell(), foresight(), _level(), _p_capable() (+8 more)

### Community 103 - "main-lms-backend/main.py"
Cohesion: 0.05
Nodes (60): fastapi, auth/database.py…, get_current_user(), auth/dependencies.py…, Decodes the Bearer JWT, looks up the user in auth.db. Raises HTTP 401 for any…, Returns a FastAPI dependency that checks the current user's role. Example:…, require_role(), auth/models.py… (+52 more)

### Community 104 - "LearningChat.tsx"
Cohesion: 0.26
Nodes (12): ChatEntry, LearningChat(), LearningChatProps, fetchWithTimeout(), LearningChatResponse, LearningChatTurn, LearningCitation, LearningMetadata (+4 more)

### Community 105 - "practice_assessment.py"
Cohesion: 0.09
Nodes (38): Practice ability (`main-lms-backend/services/practice_assessment.py`), bump(), courses_for_topics(), latest_practice_value(), link_competency(), media_question_difficulty(), next_difficulty(), normalise_difficulty() (+30 more)

### Community 106 - "Deploy: backend on Oracle Cloud, frontend on Vercel"
Cohesion: 0.22
Nodes (8): 1. Create the VM (Oracle Cloud console), 2. Pick the API hostname, 3. Set up the VM, 4. Frontend on Vercel, Deploy: backend on Oracle Cloud, frontend on Vercel, Troubleshooting, Updating: just `git push` to `main`, YouTube links on the VM

### Community 107 - "CourseCard.tsx"
Cohesion: 0.18
Nodes (14): BADGE_STYLE, CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBar(), MatchScoreBarProps, MODALITY_LABEL, SOURCE_STYLES (+6 more)

### Community 108 - "Decisions log (made without the user)"
Cohesion: 0.25
Nodes (6): Could not do / blocked, Decisions log (made without the user), Noticed but out of scope (not fixed), SCIL v6 — mock data + blocked features: progress report, Status, Catalogue duration in hours, or None for a course not in the catalogue.

### Community 109 - "get_enriched_courses"
Cohesion: 0.33
Nodes (7): composite_search(), _course_tags(), _enriched_view(), get_enriched_courses(), _matches_filters(), Sunbird-style filters: each key → value or list of accepted values., The catalogue in the older "enriched" shape. Query params:…

### Community 110 - "admin_analytics.py"
Cohesion: 0.08
Nodes (48): Backend, overview(), _competency_metrics(), daily_metrics(), by(), dept_compliance(), emerging_skills(), facets() (+40 more)

### Community 111 - "QuizSkillImpact.tsx"
Cohesion: 0.15
Nodes (11): Delta(), DIFF_CLASS, DifficultyChip(), QuizQuestionReview(), QuizRecommendations(), signed(), SkillImpactCard(), TYPE_NAMES (+3 more)

### Community 112 - "DiagnosticSessions"
Cohesion: 0.30
Nodes (5): DiagnosticSessions, public_item(), Any, What the learner sees: no answer key, no parameters., In-memory adaptive sessions (per process). Lost on restart — a session is…

### Community 113 - "test_gap_and_recommendation_upgrades.py"
Cohesion: 0.13
Nodes (20): calculate_baseline(), EvidencePayload, BaseModel, Stateless calculator for one competency, on exactly the scoring path the…, explain_level(), "Why this level" for one competency, built only from numbers the API already…, rater_leniency_offsets(), [{raterId, grantedValue}] → {raterId: {offset, n, mean, grandMean}} (shrunk… (+12 more)

### Community 114 - "_warm_up"
Cohesion: 0.11
Nodes (24): AbstractEventLoop, base64, _build_engine(), Everything slow, off the request path, on the "warm-up" thread's own loop so…, Engine + assembler from one catalogue (sync — run in a thread). Course vectors…, Reload the catalogue on a timer instead of only at restart. Every…, _refresh_catalogue_loop(), _warm_up() (+16 more)

### Community 119 - "probe.py"
Cohesion: 0.12
Nodes (23): _detector(), _limit_threads(), probe(), ProbeResult, ndarray, FILE: services/media_quiz/probe.py…, `regions` — precomputed speech spans (e.g. from YouTube captions) instead of…, RapidOCR's det/cls/rec sub-engines. The attribute names differ across releases… (+15 more)

### Community 123 - "language_service.py"
Cohesion: 0.24
Nodes (11): detect_chat_language(), detect_chat_variant(), detect_chat_variant_or_none(), _devanagari_language(), Small, offline language routing for Gyan chat. This deliberately does *not* use…, Supported ISO 639-1 code for a chat message., The variant the *text itself* signals, or None when it carries no signal. Plain…, Internal language variant: en, hi (Devanagari), hi_latn (romanized Hindi), mr,… (+3 more)

### Community 124 - "_create_schema"
Cohesion: 0.28
Nodes (9): 1. Runtime topology, _create_schema(), _create(), on_event, Return at once so uvicorn binds the port; schema + warm-up run in the…, Create users_auth and the karma/evidence tables if missing (idempotent)., _startup(), migrate_karma_schema() (+1 more)

### Community 126 - "MockIgotAdapter"
Cohesion: 0.20
Nodes (6): MockIgotAdapter, Forget every cached read for this user., The full CBP course catalogue, paged through POST /api/composite/v1/search.…, POST /api/composite/v1/search — Sunbird composite search, every page. `filters`…, Legacy method that maps fetch_user_enrollments to the old simple-mock shape.…, Calls the Sunbird-compliant mock iGOT server (mock_igot_server.py) on port 8001…

### Community 127 - "CLAUDE.md"
Cohesion: 0.06
Nodes (32): CLAUDE.md — index & router, Feature index, graphify, How to use these docs, Run commands, Admin Dashboard, Code, TODOs / edge cases (+24 more)

### Community 128 - "test_reply_regression.py"
Cohesion: 0.31
Nodes (9): ChatHistoryItem, BaseModel, RecommendationContext, SkillGapContext, sample_request(), parametrize, English and Hinglish replies must match the pre-catalogue output, except…, test_endpoint_reply_unchanged() (+1 more)

### Community 129 - "Request"
Cohesion: 0.22
Nodes (9): exception_handler, HTTPException, get_competencies(), get_job_profiles(), http_exc_handler(), GET /api/job-profiles — NCO Job Role Catalogue (Sunbird-compliant). Served from…, The FRAC competencies roles and courses are tagged with (the catalogue id…, _ts_now() (+1 more)

### Community 130 - "mock_data_metrics.py"
Cohesion: 0.31
Nodes (10): _get(), live_metrics(), _login(), main(), offline_metrics(), _pct(), Mock-data quality metrics — run before/after regenerating mock data. cd main-…, Admin bearer header; retried while the backend (--reload) restarts. (+2 more)

### Community 131 - "Admin console tier"
Cohesion: 0.11
Nodes (57): Endpoints (`/api/v1/admin/console`, all take `?department=&grade=&office=`), Admin console tier, _answer_admin(), _nav_action(), _official_reply(), (reply, navigate_action) for an admin-tier intent., behind_facts(), _clean() (+49 more)

### Community 133 - ".__init__"
Cohesion: 0.12
Nodes (12): _clamp01(), _CourseDoc, _parse_level(), Stable hash of a course's embedded text — decides whether a stored vector is…, Bayesian shrinkage toward global prior mean. Returns None if either input is…, Level 3' / 3 / '3' → 3; anything outside 1..5 → None., `catalog` / `frac` / `crosswalk` are the lists served by the mock iGOT server…, Fix the quality scale to the catalogue instead of to the shortlist. Quality… (+4 more)

### Community 134 - "HybridRecommendationEngine"
Cohesion: 0.12
Nodes (18): Before / after metrics, HybridRecommendationEngine, _lex_ref(), _logistic(), ndarray, P(relevant) from the cross-encoder for the top RERANK_TOP_N by RRF; {} if…, (relevance, quality) for a single course scored on its own, with no candidate…, The BM25 score this query gives a *typical matching* course — the median of its… (+10 more)

### Community 135 - "safe_eval"
Cohesion: 0.20
Nodes (10): In / out, RAG Document → Quiz Generator & Grading (quiz ↔ skill gap), Verification, _computed_ok(), expression_numbers(), Evaluate +,-,*,/,**,%, parentheses and a few math functions. Raises ValueError…, Literal numbers used in an expression (for the 'inputs come from the source'…, safe_eval() (+2 more)

### Community 136 - "engine"
Cohesion: 0.26
Nodes (11): test_stored_embeddings_are_reused_only_when_text_matches(), test_tpac_boost_depends_on_provenance(), _course(), engine(), _frac(), fixture, Hashed bag-of-words → L2-normalised vector. Shared words ⇒ positive cosine., _StubEmbedder (+3 more)

### Community 137 - "KarmaEvent"
Cohesion: 0.20
Nodes (6): KarmaEvent, KarmaMonthlyUsage, Immutable ledger entry — one row per karma point award event., Rolling monthly counter for non-CBP COURSE_COMPLETION events. Enforces the…, Seeds an empty ledger from iGOT history; afterwards awards any newly completed…, One-time historical seeder, called when a user's ledger is empty. Derives…

### Community 141 - "lifespan"
Cohesion: 0.33
Nodes (7): lifespan(), _load_json(), _load_json_from_dir(), Any, FastAPI, Load all datasets into memory once at startup, so no request touches the file…, Load a JSON file from ROOT_DIR. Raises RuntimeError on missing file.

### Community 143 - "test_chat_endpoint.py"
Cohesion: 0.44
Nodes (9): _chat(), parametrize, End-to-end /chat behaviour per language through the real multilingual…, test_dark_mode_action(), test_my_courses_navigation(), test_questions_answer_in_chat_without_navigating(), test_recommendations(), test_sidebar_section_navigation() (+1 more)

### Community 144 - "Code"
Cohesion: 0.15
Nodes (11): AI Course Recommendation Engine + Learning Pathways, Code, Connections, In / out, GapEntry, Structured "why recommended": the gap it closes, the level step it covers and…, SCIL v6 §4 tie-break: gaps whose priority is within OPPORTUNITY_TIE_BAND (10%)…, ACBP mandatory courses (the departmental training plan) as recommendations,… (+3 more)

### Community 145 - "Ollama RAG Knowledge Base (Tier 3 — disconnected)"
Cohesion: 0.22
Nodes (8): Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, build_system_prompt(), generate_chat_response(), Runs the full RAG pipeline: 1. Retrieve top-k relevant document chunks from…, Builds a rich system prompt that grounds the LLM in the user's live context.…

### Community 150 - "get_embedder"
Cohesion: 0.09
Nodes (22): Code, Connections, In / out, Shared Embedder (chat + catalog roles), TODOs / edge cases, _Embedder, encode_cached(), get_embedder() (+14 more)

### Community 151 - "Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)"
Cohesion: 0.22
Nodes (7): GSBPM scope — the 80% officer-hours rule (SCIL v6 §1), Reference data loading, TODOs / limits, Used by the admin console, Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight), GET /api/gsbpm/v1/map — GSBPM sub-processes + competency → sub-processes., GET /api/org/v1/offices — {cycle, offices[{officeId, subprocesses[{id,…

### Community 152 - "career_readiness"
Cohesion: 0.33
Nodes (9): career_readiness(), office_ladder(), Any, get, Roles of one office grouped by tier, most junior tier first., readiness = mean over required competencies of min(level, required) / required.…, readiness_for(), _tier() (+1 more)

### Community 153 - "Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)"
Cohesion: 0.25
Nodes (7): 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator

### Community 154 - ".award_safe"
Cohesion: 0.25
Nodes (6): Connections, In / out, Karma Points (gamification), Rules (`RULES` in `karma_engine.py`, served by `GET /karma/rules`), TODOs / edge cases, For server-side hooks (quiz grading, diagnostics): own session, never raises.

### Community 155 - "_build_workforce_snapshot"
Cohesion: 0.25
Nodes (8): Cold start for UNASSESSED competencies, Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8), Foresight, Proficiency belief with dated decay, Workforce snapshot, _build_workforce_snapshot(), Every official's resolved competency rows, for the SCIL v6 population / cohort…, _snapshot_after_schema()

### Community 156 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.29
Nodes (6): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only, data(), files(), fixture

### Community 157 - "pipeline.py"
Cohesion: 0.07
Nodes (39): argparse, asyncio, csv, Code, main(), FILE: scripts/eval_media_quiz.py…, caption_regions(), fact_check() (+31 more)

### Community 158 - "chat_actions.py"
Cohesion: 0.50
Nodes (4): detect_ui_actions(), _mentions(), Detect website theme / language changes requested in any supported chat…, Returns (theme, language): theme in {"dark", "light", "toggle"}, language in…

### Community 160 - "decay"
Cohesion: 0.50
Nodes (4): decay(), (μ_t, σ_t, λ) — relax the belief toward the population prior as evidence ages., test_accuracy_skills_decay_faster_than_procedural(), test_decay_relaxes_toward_the_population_mean_not_zero()

## Knowledge Gaps
- **314 isolated node(s):** `setup.sh script`, `name`, `private`, `version`, `type` (+309 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1125 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **43 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Admin console tier` connect `Admin console tier` to `test_chat_messages.py`, `workforce_service.py`, `ChatWidget.tsx`, `chatbot.py`, `AdminDashboard.tsx`, `get_embedder`, `language_service.py`, `admin_console.py`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `UserAuth` connect `UserAuth` to `test_certificate_evidence.py`, `document_extractor.py`, `post`, `main-lms-backend/main.py`, `seed.py`, `competency.py`, `karma.py`, `rag.py`, `chatbot.py`, `_workforce`, `admin_analytics.py`, `test_admin_chat.py`, `career_readiness`, `feedback_service.py`, `admin_console.py`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `Code` connect `post` to `Admin console tier`, `main-lms-backend/main.py`, `seed.py`, `engine`, `AdminDashboard.tsx`, `UserAuth`, `CLAUDE.md`, `react`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 81 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 81 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `HybridRecommendationEngine` (e.g. with `7. Mismatches between the mermaid diagram and the code` and `Code`) actually correct?**
  _`HybridRecommendationEngine` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `setup.sh script`, `name`, `private` to the rest of the system?**
  _314 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `document_extractor.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1265597147950089 - nodes in this community are weakly interconnected._