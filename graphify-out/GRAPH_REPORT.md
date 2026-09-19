# Graph Report - SIH_IGot  (2026-09-19)

## Corpus Check
- 252 files · ~4,960,517 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .css 1, .example 1)

## Summary
- 2909 nodes · 7166 edges · 160 communities (121 shown, 39 thin omitted)
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
- lucide-react
- Request
- pipeline.py
- Code
- UserAuth
- Timeline
- generate.py
- karma.py
- What You Must Do When Invoked
- Any
- test_pathway.py
- domain.ts
- extractors.py
- media_io.py
- learning_mode.py
- compilerOptions
- os
- 🇮🇳 MoSPI Skill Intelligence Platform
- media_quiz.py
- test_irt.py
- 1. Runtime topology
- CompetencyCalculator
- react
- chatbot.py
- api.ts
- karma_engine.py
- speech.d.ts
- graphify reference: extra exports and benchmark
- resolve_level
- mock_igot_server.py
- compilerOptions
- Code
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
- numpy
- AssessmentPage.tsx
- MockIgotAdapter
- MediaQuizExtras.tsx
- items.py
- probe.py
- generate_mock_data.py
- test_gap_and_recommendation_upgrades.py
- ILearningPlatformAdapter
- semantic_engine.py
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
- mock_data_metrics.py
- test_reply_regression.py
- insights.py
- mock-igot-server/main.py
- Any
- proficiency_service.py
- Session
- feedback_service.py
- competency.py
- test_certificate_evidence.py
- CourseCard.tsx
- lifespan
- system_health.py
- _roster
- CertificateUploadZone.tsx
- workforce_service.py
- CertificateReviewQueue.tsx
- QuizSkillImpact.tsx
- practice_assessment.py
- AdminDashboard.tsx
- DashboardFactory.ts
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
- .award_safe
- CLAUDE.md
- main-lms-backend/main.py
- QuizItemStat
- test_proficiency_foresight.py
- .__init__
- ._load
- safe_eval
- reranker.py
- useAdminData.ts
- LearnerDashboard.tsx
- _tags
- language_service.py
- .seed_from_enrollments
- TrendsPanel.tsx
- ingest_telemetry
- admin_console.py
- test_chat_endpoint.py
- client
- CLAUDE.md — index & router
- Authentication & RBAC
- chat_actions.py
- _build_workforce_snapshot
- recommendation_service.py
- services_media_quiz_llm
- services_media_quiz_pipeline
- ._client
- Learning Mode — NotebookLM-style study chat (AI Assessment Studio)
- get_enriched_courses
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
- `Code` --references--> `WhyThisLevel()`  [INFERRED]
  docs/features/skill-gap-analysis.md → frontend/src/components/dashboard/SkillGapCard.tsx
- `Code` --references--> `StatTone`  [INFERRED]
  docs/features/learner-dashboard.md → frontend/src/components/shell/StatCard.tsx
- `Frontend` --references--> `QuizCitation`  [INFERRED]
  docs/features/rag-quiz-generator.md → frontend/src/services/api.ts
- `Frontend` --references--> `ItemCalibration`  [INFERRED]
  docs/features/rag-quiz-generator.md → frontend/src/services/api.ts
- `TODOs / edge cases` --references--> `gradeQuiz()`  [INFERRED]
  docs/features/media-quiz-generator.md → frontend/src/services/api.ts

## Import Cycles
- None detected.

## Communities (160 total, 39 thin omitted)

### Community 0 - "ReplyContext"
Cohesion: 0.16
Nodes (19): importlib, Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile(), Any, Everything a reply template may personalise, built once per chat request., ReplyContext, _by_page(), _gap_lines() (+11 more)

### Community 1 - "QuizQuestionInput.tsx"
Cohesion: 0.22
Nodes (17): Frontend, emptyAnswer(), hindi(), isAnswered(), pick(), Props, qType(), QuizLang (+9 more)

### Community 2 - "Code"
Cohesion: 0.14
Nodes (14): Code, ist_date(), ist_day_start_utc(), ist_now(), KarmaEngine, MonthlyUsage, date, datetime (+6 more)

### Community 3 - "router.py"
Cohesion: 0.09
Nodes (40): bcrypt, Code, jose, change_password(), _clear_refresh_cookie(), login(), logout(), post (+32 more)

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
Cohesion: 0.08
Nodes (48): GyanBot(), GyanHero(), LanguageMenu(), LanguageMenuProps, CAPABILITIES, ChatWidget(), ChatWidgetProps, MessageBubble() (+40 more)

### Community 8 - "claim_cbp_bonus"
Cohesion: 0.16
Nodes (21): admin_adjust_karma(), AdminAdjustRequest, _assert_self_or_admin(), award_karma_event(), _award_response(), CbpClaimRequest, claim_cbp_bonus(), _enrollments_or_503() (+13 more)

### Community 9 - "lucide-react"
Cohesion: 0.10
Nodes (26): KarmaCard(), PassbookRow(), PILL_ORDER, RightSidebarProps, EVENT_META, formatPoints(), KarmaEventMeta, metaFor() (+18 more)

### Community 10 - "Request"
Cohesion: 0.18
Nodes (11): exception_handler, HTTPException, get_competencies(), get_item_bank(), get_job_profiles(), http_exc_handler(), 2PL MCQ item bank (a, b on the FRAC level scale, Bloom level, answer key).…, GET /api/job-profiles — NCO Job Role Catalogue (Sunbird-compliant). Served from… (+3 more)

### Community 11 - "pipeline.py"
Cohesion: 0.10
Nodes (24): csv, main(), FILE: scripts/eval_media_quiz.py…, caption_regions(), fact_check(), Media → quiz pipeline (video, audio, YouTube) for the Assessment Studio. Entry…, MediaSource, What the pipeline processes: one uploaded file, or YouTube's separate parts. (+16 more)

### Community 12 - "Code"
Cohesion: 0.15
Nodes (26): Connections, Code, rows_for(), tag_id(), _completed_courses(), _education_score(), enrollment_course_id(), is_completed() (+18 more)

### Community 13 - "UserAuth"
Cohesion: 0.10
Nodes (28): AuthBase, UserAuth, get_me(), get, Return the current authenticated user's profile. Used by the frontend to re-…, get_achievements(), get_achievements_by_user_id(), get_admin_roster() (+20 more)

### Community 14 - "Timeline"
Cohesion: 0.11
Nodes (22): dataclasses, Performance, build_chunks(), Chunk, Evidence, fmt_ts(), _make_chunk(), FILE: services/media_quiz/evidence.py… (+14 more)

### Community 15 - "generate.py"
Cohesion: 0.08
Nodes (42): _generate_questions(), Cited, validated, multi-type questions (services/doc_quiz/generate.py) →…, _call(), _density(), difficulty_quotas(), DocChunk, excerpt(), generate() (+34 more)

### Community 16 - "karma.py"
Cohesion: 0.13
Nodes (18): contextlib, fastapi_security, get_db(), auth/database.py…, FastAPI dependency — `db: Session = Depends(get_db)`; closed after the request., get_current_user(), Session, auth/dependencies.py… (+10 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "Any"
Cohesion: 0.09
Nodes (19): _course_summary(), _diagnostic_step(), _fmt_levels(), absorb(), add_step(), advance(), open_ladders(), _parse_level() (+11 more)

### Community 19 - "test_pathway.py"
Cohesion: 0.09
Nodes (21): _edge(), _kinds_levels(), Skill-gap levels + level-aware recommendations + learning pathways. Runs on a…, _resolved(), test_already_met_prerequisite_changes_nothing(), test_completed_never_suggested_and_in_progress_is_continued(), test_crosswalked_competency_gets_a_ladder_under_its_own_id(), test_finishing_a_course_never_lowers_the_level() (+13 more)

### Community 20 - "domain.ts"
Cohesion: 0.05
Nodes (40): DEFER_REASON, KIND_STYLE, PathwayLadder(), AppliedPrerequisite, CareerCompetency, CareerRoleOption, ColdStartPrior, Competency (+32 more)

### Community 21 - "extractors.py"
Cohesion: 0.09
Nodes (33): concurrent_futures, capabilities(), get, JSONResponse, add_captions(), flush(), _budget(), describe_keyframes() (+25 more)

### Community 22 - "media_io.py"
Cohesion: 0.09
Nodes (32): In / out, Media (Video / Audio / YouTube) → Evidence-Cited Quiz, Pipeline, Setup, TODOs / edge cases, Verification, YouTube, Caption (+24 more)

### Community 23 - "learning_mode.py"
Cohesion: 0.08
Nodes (48): Code, Code, Connections, Difficulty calibration (`services/doc_quiz/calibration.py`), Gemini model, Personalised feedback (`items.feedback`), ErrorResponse, _generate_overview() (+40 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "os"
Cohesion: 0.05
Nodes (51): Code, Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, dotenv, io, logging (+43 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "media_quiz.py"
Cohesion: 0.17
Nodes (20): fastapi_responses, importlib_util, MediaMetadata, MediaQuizQuestion, MediaQuizResponse, _process(), BaseModel, on_event (+12 more)

### Community 28 - "test_irt.py"
Cohesion: 0.13
Nodes (23): DiagnosticSessions, fisher_information(), laplace_posterior(), next_item(), p_correct(), public_item(), Any, services/irt_service.py — Tier-1 Bayesian 2PL posterior + adaptive diagnostic… (+15 more)

### Community 29 - "1. Runtime topology"
Cohesion: 0.15
Nodes (12): 1. Runtime topology, Connections, Gyan — Multilingual Chat Assistant, In / out, TODOs / edge cases, AI Course Recommendation Engine + Learning Pathways, In / out, TODOs / edge cases (+4 more)

### Community 30 - "CompetencyCalculator"
Cohesion: 0.29
Nodes (6): CompetencyCalculator, datetime, Maps FRAC types from the JSON to calculation categories., Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, test_missing_channels_do_not_drag_the_score_to_zero()

### Community 31 - "react"
Cohesion: 0.06
Nodes (57): Visual design system (shared by every page), App(), DashboardRedirect(), LearnerDashboard, TokenBridge(), AshokaChakra(), CountUp(), GovEmblem() (+49 more)

### Community 32 - "chatbot.py"
Cohesion: 0.23
Nodes (21): low_confidence_threshold(), chat(), ChatRequest, ChatResponse, detect_intent_keyword(), _intent_response(), _intercept(), post (+13 more)

### Community 33 - "api.ts"
Cohesion: 0.06
Nodes (35): LevelCheckModal(), OUTCOME, Props, SkillRow, useSkillsData(), answerDiagnostic(), AssignmentInput, BehindRow (+27 more)

### Community 34 - "karma_engine.py"
Cohesion: 0.12
Nodes (22): _create_schema(), _create(), Create users_auth and the karma/evidence tables if missing (idempotent)., KarmaEventType, AdminAdjustmentStrategy, CompletionKarmaStrategy, FixedPointsStrategy, IKarmaStrategy (+14 more)

### Community 35 - "speech.d.ts"
Cohesion: 0.20
Nodes (6): SpeechRecognition, SpeechRecognitionEvent, SpeechRecognitionResult, SpeechRecognitionResultItem, SpeechRecognitionResultList, Window

### Community 36 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 37 - "resolve_level"
Cohesion: 0.15
Nodes (23): BaselineAssembler, _normalise_course_map(), Single source of truth for an official's level on one competency. Every…, Accept {courseId: {compId: level}} or the legacy {courseId: [compId]}., resolve_level(), fuse_channels(), Weighted mean over the K/A/U/S channels that carry evidence (None → absent)., test_verified_cert_lifts_confidence_over_documented() (+15 more)

### Community 38 - "mock_igot_server.py"
Cohesion: 0.15
Nodes (22): CompetencyOut, composite_search(), CompositeSearchRequest, ContentStateRequest, _course_by_id(), CourseOut, EnrolPayload, get_content_state() (+14 more)

### Community 39 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 40 - "Code"
Cohesion: 0.14
Nodes (22): base64, Code, functools, _match(), protect_terms(), FILE: services/media_quiz/fact_check.py…, Translate strings with glossary terms protected as ⟦Tn⟧. Returns (translations…, _reference() (+14 more)

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 42 - "Admin Dashboard"
Cohesion: 0.50
Nodes (4): Admin Dashboard, Code, TODOs / edge cases, What the synthetic data shows

### Community 43 - "_learner_competency_state"
Cohesion: 0.08
Nodes (27): _ensure_can_view(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments_by_user_id(), get_frac_competencies(), get_learning_pathway(), get_profile_by_user_id(), get_recommendations_by_user_id() (+19 more)

### Community 44 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 45 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 49 - "rag.py"
Cohesion: 0.08
Nodes (45): 7. Mismatches between the mermaid diagram and the code, Base, Conventions, TODOs / edge cases, Connections, In / out, Skill Gap Analysis (evidence-based competency baselines), TODOs / edge cases (+37 more)

### Community 58 - "opportunity"
Cohesion: 0.24
Nodes (13): opportunity(), Any, services/gsbpm_service.py — GSBPM scoping (SCIL v6 §1) + opportunity to…, Opportunity to practise a competency in the official's office this cycle (SCIL…, Which competencies are in scope under the officer-hours rule, and why., scope_report(), _sp_name(), subprocess_hours() (+5 more)

### Community 60 - "test_chat_messages.py"
Cohesion: 0.23
Nodes (11): Loads a language's template table on first use ("or" lives in or_.py; `or` is a…, templates(), _alternatives(), _fields(), parametrize, Catalogue completeness: every language has every template, placeholders are…, test_every_intent_renders(), test_placeholders_match_english() (+3 more)

### Community 61 - "numpy"
Cohesion: 0.08
Nodes (44): find_cycle(), infer_edges(), _node(), _norm_sf(), _ols(), Any, ndarray, services/prerequisite_service.py — cross-competency prerequisite DAG (SCIL v6… (+36 more)

### Community 62 - "AssessmentPage.tsx"
Cohesion: 0.17
Nodes (18): Gyan hand-off (document → quiz or Learning Mode, no second upload), AssessmentPage, AssessmentPage(), DIFFICULTIES, Difficulty, errorText(), formatDate(), guessUploadFormat() (+10 more)

### Community 63 - "MockIgotAdapter"
Cohesion: 0.09
Nodes (23): Code, Cross-competency prerequisite DAG (SCIL v6 §5, B4), GSBPM scope — the 80% officer-hours rule (SCIL v6 §1), Reference data loading, TODOs / limits, Used by the admin console, Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight), _competencies() (+15 more)

### Community 64 - "MediaQuizExtras.tsx"
Cohesion: 0.16
Nodes (17): CONTENT_LABEL, MediaAnalysisCard(), MediaAnswerReview(), pct(), QuestionEvidence(), SOURCE_LABEL, YoutubeLinkInput(), formatTimestamp() (+9 more)

### Community 65 - "items.py"
Cohesion: 0.24
Nodes (27): ast, Document question pipeline (`main-lms-backend/services/doc_quiz/`), _build_review(), Type-aware answer review, missed questions first. Each wrong answer gets…, accepted_texts(), answer_display(), _choice_set(), correct_display() (+19 more)

### Community 66 - "probe.py"
Cohesion: 0.12
Nodes (20): _ocr_engine(), ocr_pdf_pages(), OcrUnavailable, ndarray, RuntimeError, (text in reading order, mean confidence, weak lines dropped)., OCR the given 1-based pages. Returns ({page: text}, report)., _read() (+12 more)

### Community 67 - "generate_mock_data.py"
Cohesion: 0.07
Nodes (58): _batch(), build_acbp(), build_catalog(), build_crosswalk(), build_enrollments(), build_frac(), build_gsbpm_map(), build_hrms() (+50 more)

### Community 68 - "test_gap_and_recommendation_upgrades.py"
Cohesion: 0.09
Nodes (30): calculate_baseline(), CertificateReview, EvidencePayload, BaseModel, Stateless calculator for one competency, on exactly the scoring path the…, assess_competency(), explain_level(), datetime (+22 more)

### Community 69 - "ILearningPlatformAdapter"
Cohesion: 0.10
Nodes (15): 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator, ILearningPlatformAdapter (+7 more)

### Community 70 - "semantic_engine.py"
Cohesion: 0.11
Nodes (22): difflib, Code, classify_intent(), _correct_tokens(), _ensure_prototypes(), load_corpus(), FILE: ai/semantic_engine.py…, Encode all prototype phrases once, via the shared singleton embedder. (+14 more)

### Community 71 - "Code"
Cohesion: 0.09
Nodes (30): Code, Opportunity to practise (SCIL v6 §4), CompetencyOverviewTable(), LevelPips(), priorityOf(), Props, StudyPlanSummary(), CHANNEL_LABEL (+22 more)

### Community 72 - "test_doc_quiz.py"
Cohesion: 0.13
Nodes (17): Document quiz: extraction (DOCX, OCR), cited multi-type generation, grading…, _chunks(), _mcq(), parametrize, services/doc_quiz — question types, validator, dedup, selection, calibration,…, test_choice_feedback_uses_option_rationale(), test_courses_for_topics_prefers_competency_courses(), test_fill_blank_and_true_false_rules() (+9 more)

### Community 76 - "HybridRecommendationEngine"
Cohesion: 0.08
Nodes (28): Code, Connections, _CourseDoc, GapEntry, HybridRecommendationEngine, _interleave_by_level(), BaseModel, Returns deduplicated, level-gated recommendations in gap-priority order. Only… (+20 more)

### Community 77 - "lmsFetch"
Cohesion: 0.24
Nodes (16): AdminActions(), AssignForm(), when(), filterKey(), awardKarmaEvent(), CatalogueCourse, consoleQs(), createAssignment() (+8 more)

### Community 87 - "mock_data_metrics.py"
Cohesion: 0.24
Nodes (12): argparse, collections, _get(), live_metrics(), _login(), main(), offline_metrics(), _pct() (+4 more)

### Community 88 - "test_reply_regression.py"
Cohesion: 0.27
Nodes (10): ChatHistoryItem, BaseModel, RecommendationContext, SkillGapContext, sample_request(), parametrize, English and Hinglish replies must match the pre-catalogue output, except…, test_endpoint_reply_unchanged() (+2 more)

### Community 89 - "insights.py"
Cohesion: 0.14
Nodes (22): capability_risk(), _frac_names(), gsbpm_scope(), prerequisite_dag(), get, post, routers/insights.py — admin-only SCIL v6 workforce insights Every number here…, Rebuild the workforce snapshot now (≈ a few seconds). (+14 more)

### Community 90 - "mock-igot-server/main.py"
Cohesion: 0.14
Nodes (21): enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history(), health(), lifespan() (+13 more)

### Community 91 - "Any"
Cohesion: 0.18
Nodes (11): 3. Core data flow, fetch(), Any, TTL memo for one user's read. Concurrent callers share one in-flight request;…, The full CBP course catalogue, paged through POST /api/composite/v1/search.…, POST /api/composite/v1/search — Sunbird composite search, every page. `filters`…, GET /api/evidence/v1/user/{id} — EvidenceLog-style workplace evidence rows ([]…, GET /api/cbplan/v1/user/{id} — ACBP mandatory courses + learning hours/quarter.… (+3 more)

### Community 92 - "proficiency_service.py"
Cohesion: 0.15
Nodes (19): cluster_of(), decay(), expected_shortfall(), months_between(), office_phase(), _phi(), proficiency_state(), Any (+11 more)

### Community 93 - "Session"
Cohesion: 0.21
Nodes (4): AwardResult, Session, DAILY_LOGIN for today, then any streak milestone the current streak has reached., Seeds an empty ledger from iGOT history; afterwards awards any newly completed…

### Community 94 - "feedback_service.py"
Cohesion: 0.14
Nodes (20): feedback_summary(), FeedbackBody, my_feedback(), post_feedback(), BaseModel, get, post, Session (+12 more)

### Community 95 - "competency.py"
Cohesion: 0.24
Nodes (16): CertificateSubmission, One uploaded certificate (routers/competency.py). On upload each extracted…, certificates_for_review(), _find(), my_certificates(), get, post, Session (+8 more)

### Community 96 - "test_certificate_evidence.py"
Cohesion: 0.13
Nodes (17): datetime, fastapi_testclient, FILE: services/doc_quiz/calibration.py…, Admin console write actions end to end on an in-memory SQLite DB, with the…, test_nudge_only_officials_behind_and_respect_cooldown(), Certificate upload → EvidenceLog → admin review, end to end on in-memory SQLite…, _rows(), test_admin_approve_turns_rows_verified() (+9 more)

### Community 97 - "CourseCard.tsx"
Cohesion: 0.18
Nodes (13): BADGE_STYLE, CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps, MODALITY_LABEL, SOURCE_STYLES, matches() (+5 more)

### Community 98 - "lifespan"
Cohesion: 0.33
Nodes (7): lifespan(), _load_json(), _load_json_from_dir(), Any, FastAPI, Load all datasets into memory once at startup, so no request touches the file…, Load a JSON file from ROOT_DIR. Raises RuntimeError on missing file.

### Community 99 - "system_health.py"
Cohesion: 0.22
Nodes (20): is_embedder_ready(), model_name(), Non-blocking check — True only if the role's model is already loaded., is_semantic_engine_ready(), health(), Liveness + warm-up state. Cheap: use it as the Render health check / keep-alive…, chat_mode(), get (+12 more)

### Community 100 - "_roster"
Cohesion: 0.23
Nodes (21): Endpoints (`/api/v1/admin/console`, all take `?department=&grade=&office=`), _behind(), _csv(), _emerging(), emerging_skills(), export_csv(), filter_options(), _filters() (+13 more)

### Community 101 - "CertificateUploadZone.tsx"
Cohesion: 0.31
Nodes (7): CertificateUploadZone(), clean(), STATUS_CHIP, CertificateStatus, CertificateSubmission, fetchMyCertificates(), uploadCertificate()

### Community 102 - "workforce_service.py"
Cohesion: 0.22
Nodes (17): How the parts work, _Phi(), _as_date(), capability_risk(), cell(), foresight(), _level(), _p_capable() (+9 more)

### Community 103 - "CertificateReviewQueue.tsx"
Cohesion: 0.16
Nodes (15): CertificateReviewQueue(), Row(), STATUS_CLS, TABS, when(), STATUS, SystemHealthPanel(), SectionAction() (+7 more)

### Community 104 - "QuizSkillImpact.tsx"
Cohesion: 0.15
Nodes (11): Delta(), DIFF_CLASS, DifficultyChip(), QuizQuestionReview(), QuizRecommendations(), signed(), SkillImpactCard(), TYPE_NAMES (+3 more)

### Community 105 - "practice_assessment.py"
Cohesion: 0.07
Nodes (48): Practice ability (`main-lms-backend/services/practice_assessment.py`), _competency_rows(), grade_quiz(), Any, _question_difficulties(), The learner's resolved role competencies (same rows the skill-gap view shows),…, **Grade Quiz → Skill Gap** - user_id comes from the JWT…, Per-question difficulty for grading, calibrated from response data… (+40 more)

### Community 106 - "AdminDashboard.tsx"
Cohesion: 0.09
Nodes (31): Frontend, AdminDashboard, AdminFilterBar(), ExportButton(), facetLabels(), describeFilters(), esc(), printReport() (+23 more)

### Community 107 - "DashboardFactory.ts"
Cohesion: 0.14
Nodes (7): AdminDashboardCreator, DashboardCreator, DashboardFactory, DashboardProps, IDashboard, OfficialDashboardCreator, TrainerDashboardCreator

### Community 108 - "Decisions log (made without the user)"
Cohesion: 0.18
Nodes (8): Before / after metrics, Could not do / blocked, Decisions log (made without the user), Noticed but out of scope (not fixed), SCIL v6 — mock data + blocked features: progress report, Status, Catalogue duration in hours, or None for a course not in the catalogue., Median cosine between the competency query and the courses NOT tagged with it —…

### Community 109 - "test_admin_analytics.py"
Cohesion: 0.15
Nodes (18): emerging_skills(), date, datetime, Daily training-rate history rebuilt from dated iGOT course completions, for…, Per FRAC competency, over the (filtered) officials in the workforce snapshot: *…, reconstruct_history(), Admin console aggregates (services/admin_analytics.py): filters, pagination,…, _snap_row() (+10 more)

### Community 110 - "admin_analytics.py"
Cohesion: 0.13
Nodes (29): Backend, overview(), _competency_metrics(), daily_metrics(), by(), dept_compliance(), facets(), Filters (+21 more)

### Community 111 - "WorkforceInsights.tsx"
Cohesion: 0.10
Nodes (25): AGENDA_TYPE, CapabilityRiskPanel(), ForesightPanel(), GsbpmScopePanel(), pct(), PrerequisitePanel(), PRIORITY_CHIP, RISK_CHIP (+17 more)

### Community 112 - "LearningChat.tsx"
Cohesion: 0.26
Nodes (12): ChatEntry, LearningChat(), LearningChatProps, fetchWithTimeout(), LearningChatResponse, LearningChatTurn, LearningCitation, LearningMetadata (+4 more)

### Community 113 - "_StubEmbedder"
Cohesion: 0.31
Nodes (9): test_stored_embeddings_are_reused_only_when_text_matches(), test_tpac_boost_depends_on_provenance(), _course(), _frac(), Hashed bag-of-words → L2-normalised vector. Shared words ⇒ positive cosine., _StubEmbedder, test_classroom_cap_defers_the_ladder(), test_curated_crosswalk_is_used_before_embeddings() (+1 more)

### Community 114 - "_warm_up"
Cohesion: 0.12
Nodes (19): AbstractEventLoop, Measured uplift → coverage learning + training effectiveness (SCIL v6 §6, B5), _build_engine(), Everything slow, off the request path, on the "warm-up" thread's own loop so…, Engine + assembler from one catalogue (sync — run in a thread). Course vectors…, Reload the catalogue on a timer instead of only at restart. Every…, _refresh_catalogue_loop(), _warm_up() (+11 more)

### Community 119 - "document_extractor.py"
Cohesion: 0.13
Nodes (31): Code, CertificateExtractionResult, _clamp_level(), DocumentExtractorService, ExtractedCompetency, ExtractionError, frac_by_id(), frac_dictionary() (+23 more)

### Community 123 - "diagnostic.py"
Cohesion: 0.09
Nodes (38): LevelDispute, status: OPEN (test started) → CONFIRMED | RAISED | LOWER_THAN_SHOWN once the…, career_readiness(), _dispute_view(), DisputeBody, _ensure_can_view(), my_disputes(), office_ladder() (+30 more)

### Community 124 - "seed.py"
Cohesion: 0.15
Nodes (18): hash_password(), Return a bcrypt hash of the plain-text password., _derive_password(), _fetch_officials(), main(), Session, auth/seed.py…, Insert the hardcoded admin user. Returns True if inserted, False if already… (+10 more)

### Community 126 - ".award_safe"
Cohesion: 0.25
Nodes (6): Connections, In / out, Karma Points (gamification), Rules (`RULES` in `karma_engine.py`, served by `GET /karma/rules`), TODOs / edge cases, For server-side hooks (quiz grading, diagnostics): own session, never raises.

### Community 127 - "CLAUDE.md"
Cohesion: 0.27
Nodes (6): Certificate / Resume Evidence Extraction, In / out, TODOs / edge cases, Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server + mock data)

### Community 128 - "main-lms-backend/main.py"
Cohesion: 0.10
Nodes (31): asyncio, fastapi, fastapi_middleware_cors, hashlib, httpx, json, adapters/igot_adapter.py — iGOT Platform Adapter…, main.py — MoSPI LMS Backend API (Main Orchestrator)… (+23 more)

### Community 129 - "QuizItemStat"
Cohesion: 0.18
Nodes (14): QuizItemStat, Response data per quiz item (services/doc_quiz/calibration.py). itemKey is a…, Stamp each item with its content key and its response-calibrated difficulty.…, _with_calibration(), calibrate(), calibrate_items(), difficulty_from_b(), load_stats() (+6 more)

### Community 130 - "test_proficiency_foresight.py"
Cohesion: 0.23
Nodes (14): cohort_prior(), population_stats(), Cohort prior for an UNASSESSED competency, with the divergence check., comp → (μ_pop, σ_pop, n) over officials with assessed evidence on it., _hrms(), _official(), SCIL v6 §2 dated decay / expected-shortfall / cold start, and §11 workforce…, _snap() (+6 more)

### Community 131 - ".__init__"
Cohesion: 0.14
Nodes (11): Code, Connections, In / out, Shared Embedder (chat + catalog roles), TODOs / edge cases, ndarray, Stable hash of a course's embedded text — decides whether a stored vector is…, `catalog` / `frac` / `crosswalk` are the lists served by the mock iGOT server… (+3 more)

### Community 132 - "._load"
Cohesion: 0.22
Nodes (8): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only, Any, _read_disk(), data(), files(), fixture

### Community 133 - "safe_eval"
Cohesion: 0.18
Nodes (11): In / out, RAG Document → Quiz Generator & Grading (quiz ↔ skill gap), TODOs / edge cases, Verification, _computed_ok(), expression_numbers(), Evaluate +,-,*,/,**,%, parentheses and a few math functions. Raises ValueError…, Literal numbers used in an expression (for the 'inputs come from the source'… (+3 more)

### Community 134 - "reranker.py"
Cohesion: 0.18
Nodes (12): TODOs / edge cases, get_reranker(), ndarray, FILE: ai/reranker.py…, Cross-encoder scores for `passages` against `query`, or None if no reranker., Relevance logits, one per (query, passage) pair (higher = better match)., The loaded cross-encoder, or None when disabled / unavailable (logged once)., rerank_scores() (+4 more)

### Community 135 - "useAdminData.ts"
Cohesion: 0.24
Nodes (9): AsyncState, useAdminFacets(), useAdminOverview(), AdminOverview, AdminRosterRow, fetchAdminFacets(), fetchAdminOverview(), Page (+1 more)

### Community 136 - "LearnerDashboard.tsx"
Cohesion: 0.05
Nodes (48): `frontend/src/`, Connections, In / out, Learner Dashboard (frontend shell), TODOs / edge cases, CareerReadinessCard(), Props, TIER_LABEL (+40 more)

### Community 137 - "_tags"
Cohesion: 0.25
Nodes (8): _tags(), test_acbp_mandatory_courses_are_short_catalogue_courses(), test_course_outcomes_are_consistent_with_catalogue_and_roster(), test_ladders_are_complete_except_documented_holes(), test_officials_mostly_study_at_or_just_above_their_level(), test_role_competencies_and_tags_use_catalogue_ids(), test_secondary_tags_are_overlaps_at_compatible_levels(), test_title_level_words_match_the_tag_level()

### Community 138 - "language_service.py"
Cohesion: 0.24
Nodes (11): detect_chat_language(), detect_chat_variant(), detect_chat_variant_or_none(), _devanagari_language(), Small, offline language routing for Gyan chat. This deliberately does *not* use…, Supported ISO 639-1 code for a chat message., The variant the *text itself* signals, or None when it carries no signal. Plain…, Internal language variant: en, hi (Devanagari), hi_latn (romanized Hindi), mr,… (+3 more)

### Community 139 - ".seed_from_enrollments"
Cohesion: 0.40
Nodes (3): KarmaMonthlyUsage, Rolling monthly counter for non-CBP COURSE_COMPLETION events. Enforces the…, One-time historical seeder, called when a user's ledger is empty. Derives…

### Community 140 - "TrendsPanel.tsx"
Cohesion: 0.27
Nodes (9): fmtDate(), RANGES, RATE_SERIES, SERIES_DARK, SERIES_LIGHT, TrendsPanel(), fetchAdminTrends(), recordAdminSnapshot() (+1 more)

### Community 141 - "ingest_telemetry"
Cohesion: 0.29
Nodes (5): field_validator, ingest_telemetry(), Returns a list of validation errors for a single telemetry event., TelemetryBatch, _validate_event()

### Community 142 - "admin_console.py"
Cohesion: 0.09
Nodes (41): fastapi_concurrency, AdminDailySnapshot, One row per calendar day (UTC): the workforce headline numbers plus the same…, An admin assigning courses (a training plan) to a department or a list of…, A reminder sent by an admin to an official behind on mandatory (ACBP) training., TrainingAssignment, TrainingNudge, _assignment_out() (+33 more)

### Community 143 - "test_chat_endpoint.py"
Cohesion: 0.50
Nodes (7): _chat(), parametrize, End-to-end /chat behaviour per language through the real multilingual…, test_dark_mode_action(), test_my_courses_navigation(), test_recommendations(), test_skill_gaps()

### Community 144 - "client"
Cohesion: 0.50
Nodes (4): client(), roster(), fixture, _u()

### Community 145 - "CLAUDE.md — index & router"
Cohesion: 0.40
Nodes (5): CLAUDE.md — index & router, Feature index, graphify, How to use these docs, Run commands

### Community 146 - "Authentication & RBAC"
Cohesion: 0.40
Nodes (4): Authentication & RBAC, Connections, In / out, Shared database (Neon)

### Community 147 - "chat_actions.py"
Cohesion: 0.50
Nodes (4): detect_ui_actions(), _mentions(), Detect website theme / language changes requested in any supported chat…, Returns (theme, language): theme in {"dark", "light", "toggle"}, language in…

### Community 148 - "_build_workforce_snapshot"
Cohesion: 0.25
Nodes (8): Cold start for UNASSESSED competencies, Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8), Foresight, Proficiency belief with dated decay, Workforce snapshot, _build_workforce_snapshot(), Every official's resolved competency rows, for the SCIL v6 population / cohort…, _snapshot_after_schema()

### Community 149 - "recommendation_service.py"
Cohesion: 0.10
Nodes (22): _Embedder, encode_cached(), get_embedder(), _load(), onnx_model_dir(), _OnnxEmbedder, ndarray, FILE: ai/embedder.py… (+14 more)

### Community 153 - "._client"
Cohesion: 0.15
Nodes (10): AsyncClient, fetch(), fetch(), fetch(), Pooled client for the running loop — no new TCP connection per call., GET /api/frac/competencies — the catalogue FRAC set incl. L1–L5 descriptors., GET /api/frac/v1/crosswalk — iGOT dictionary CID id → catalogue FRAC id., GET /api/admin/v1/users Returns: result.users — full list of officials. (+2 more)

### Community 154 - "Learning Mode — NotebookLM-style study chat (AI Assessment Studio)"
Cohesion: 0.33
Nodes (5): Connections, In / out, Learning Mode — NotebookLM-style study chat (AI Assessment Studio), TODOs / edge cases, Verification

### Community 156 - "get_enriched_courses"
Cohesion: 0.40
Nodes (6): _course_tags(), _enriched_view(), get_enriched_courses(), _matches_filters(), Sunbird-style filters: each key → value or list of accepted values., The catalogue in the older "enriched" shape. Query params:…

## Knowledge Gaps
- **301 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+296 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1041 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **39 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `UserAuth` connect `UserAuth` to `main-lms-backend/main.py`, `test_certificate_evidence.py`, `router.py`, `_roster`, `claim_cbp_bonus`, `practice_assessment.py`, `_learner_competency_state`, `admin_console.py`, `admin_analytics.py`, `karma.py`, `rag.py`, `client`, `document_extractor.py`, `insights.py`, `diagnostic.py`, `seed.py`, `feedback_service.py`, `competency.py`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Why does `Code` connect `Code` to `karma_engine.py`, `claim_cbp_bonus`, `lucide-react`, `practice_assessment.py`, `diagnostic.py`, `.seed_from_enrollments`, `lmsFetch`, `rag.py`, `domain.ts`, `Any`, `Session`, `.award_safe`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `Code` connect `router.py` to `UserAuth`, `lmsFetch`, `karma.py`, `Authentication & RBAC`, `seed.py`, `react`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 78 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `HybridRecommendationEngine` (e.g. with `7. Mismatches between the mermaid diagram and the code` and `Code`) actually correct?**
  _`HybridRecommendationEngine` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 45 inferred relationships involving `Code` (e.g. with `KarmaCard()` and `formatPoints()`) actually correct?**
  _`Code` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _301 weakly-connected nodes found - possible documentation gaps or missing edges._