# Graph Report - SIH_IGot  (2026-09-19)

## Corpus Check
- 254 files · ~4,962,657 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .css 1, .example 1)

## Summary
- 2940 nodes · 7280 edges · 162 communities (124 shown, 38 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 822 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5fe9d438`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ReplyContext
- AssessmentPage.tsx
- Code
- Code
- package.json
- _require_auth
- sunbird_ok
- ChatWidget.tsx
- karma.py
- KarmaRewardsView.tsx
- Request
- pipeline.py
- Code
- UserAuth
- Media (Video / Audio / YouTube) → Evidence-Cited Quiz
- generate.py
- gemini_json
- What You Must Do When Invoked
- Any
- test_pathway.py
- domain.ts
- extractors.py
- media_io.py
- learning_mode.py
- compilerOptions
- ai_tools.py
- 🇮🇳 MoSPI Skill Intelligence Platform
- media_quiz.py
- test_irt.py
- Code
- CompetencyCalculator
- react
- typing
- api.ts
- AwardResult
- speech.d.ts
- graphify reference: extra exports and benchmark
- resolve_level
- BaseModel
- compilerOptions
- diagnostic.py
- graphify reference: query, path, explain
- karma_engine.py
- _resolve_competency_state
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- test_mock_data.py
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- models/models.py
- .claude/CLAUDE.md
- extraction-spec.md
- opportunity
- test_admin_analytics.py
- estimate_uplift
- admin_console.py
- Code
- Code
- items.py
- probe.py
- generate_mock_data.py
- test_gap_and_recommendation_upgrades.py
- Any
- LearnerDashboard.tsx
- rag.py
- test_doc_quiz.py
- faker
- services_chat_messages
- services_chat_messages_context
- HybridRecommendationEngine
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
- WorkforceInsights.tsx
- get_learning_pathway
- insights.py
- mock-igot-server/main.py
- .fetch_user_cbplan
- proficiency_service.py
- Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)
- summary
- competency.py
- test_certificate_evidence.py
- CourseCard.tsx
- lifespan
- system_health.py
- chatbot.py
- CertificateReviewQueue.tsx
- workforce_service.py
- BaselineAssembler
- sample_request
- practice_assessment.py
- EmergingSkills.tsx
- DashboardCreator
- Decisions log (made without the user)
- mock_igot_server.py
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
- Code
- urllib_request
- .award_safe
- CLAUDE.md
- main-lms-backend/main.py
- calibration.py
- _create_schema
- Admin Dashboard
- routers
- safe_eval
- recommendation_service.py
- catalogue_store.py
- useLearnerDashboard.ts
- lmsFetch
- mock_data_metrics.py
- services
- seed.py
- test_chat_messages.py
- _roster
- get
- test_proficiency_foresight.py
- TrendsPanel.tsx
- Authentication & RBAC
- Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)
- CertificateUploadZone.tsx
- logging
- rerank_scores
- services_media_quiz_llm
- services_media_quiz_pipeline
- pydantic
- .__init__
- _sunbird_result
- ._quality_score
- dataclasses
- chat_actions.py
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
9. `post()` - 38 edges
10. `Code` - 38 edges

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

## Communities (162 total, 38 thin omitted)

### Community 0 - "ReplyContext"
Cohesion: 0.20
Nodes (17): importlib, Any, Everything a reply template may personalise, built once per chat request., ReplyContext, _by_page(), _gap_lines(), _greeting(), _landing_section() (+9 more)

### Community 1 - "AssessmentPage.tsx"
Cohesion: 0.05
Nodes (65): Gyan hand-off (document → quiz or Learning Mode, no second upload), Frontend, AssessmentPage, CONTENT_LABEL, MediaAnalysisCard(), MediaAnswerReview(), pct(), QuestionEvidence() (+57 more)

### Community 2 - "Code"
Cohesion: 0.15
Nodes (15): Code, KarmaMonthlyUsage, Rolling monthly counter for non-CBP COURSE_COMPLETION events. Enforces the…, ist_now(), KarmaEngine, Session, Dispatches an eventType to its strategy, then applies the shared rules in…, Idempotency key for an event; None means 'not idempotent' (admin only). (+7 more)

### Community 3 - "Code"
Cohesion: 0.10
Nodes (31): bcrypt, Code, jose, change_password(), _clear_refresh_cookie(), login(), logout(), Response (+23 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (42): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+34 more)

### Community 5 - "_require_auth"
Cohesion: 0.16
Nodes (18): get_assessment_outcomes(), get_gsbpm_map(), get_hrms_officials(), get_office(), get_offices(), get_prerequisites(), get_supervisor_ratings(), get_user_cbplan() (+10 more)

### Community 6 - "sunbird_ok"
Cohesion: 0.21
Nodes (16): _course_by_id(), get_admin_roster(), get_content_state(), get_course_catalog(), get_user_enrolments(), get_user_profile(), get_user_workplace_evidence(), JSONResponse (+8 more)

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.07
Nodes (50): GyanBot(), GyanHero(), LanguageMenu(), LanguageMenuProps, CAPABILITIES, ChatWidget(), ChatWidgetProps, MessageBubble() (+42 more)

### Community 8 - "karma.py"
Cohesion: 0.17
Nodes (24): fastapi_concurrency, KarmaEvent, Immutable ledger entry — one row per karma point award event., admin_adjust_karma(), AdminAdjustRequest, _assert_self_or_admin(), award_karma_event(), _award_response() (+16 more)

### Community 9 - "KarmaRewardsView.tsx"
Cohesion: 0.10
Nodes (26): KarmaCard(), PassbookRow(), PILL_ORDER, RightSidebar(), RightSidebarProps, EVENT_META, formatPoints(), KarmaEventMeta (+18 more)

### Community 10 - "Request"
Cohesion: 0.20
Nodes (10): exception_handler, HTTPException, get_competencies(), get_item_bank(), get_job_profiles(), http_exc_handler(), 2PL MCQ item bank (a, b on the FRAC level scale, Bloom level, answer key).…, GET /api/job-profiles — NCO Job Role Catalogue (Sunbird-compliant). Served from… (+2 more)

### Community 11 - "pipeline.py"
Cohesion: 0.07
Nodes (46): Code, build_chunks(), Chunk, Evidence, fmt_ts(), _make_chunk(), FILE: services/media_quiz/evidence.py…, slide_windows: [{"t_start", "t_end", "evidence_ids": [ocr/vlm ids of that… (+38 more)

### Community 12 - "Code"
Cohesion: 0.14
Nodes (28): Connections, Code, assess_competency(), rows_for(), tag_id(), _completed_courses(), _education_score(), enrollment_course_id() (+20 more)

### Community 13 - "UserAuth"
Cohesion: 0.08
Nodes (33): AuthBase, UserAuth, get_me(), get, Return the current authenticated user's profile. Used by the frontend to re-…, get_achievements(), get_achievements_by_user_id(), get_admin_roster() (+25 more)

### Community 14 - "Media (Video / Audio / YouTube) → Evidence-Cited Quiz"
Cohesion: 0.15
Nodes (9): In / out, Media (Video / Audio / YouTube) → Evidence-Cited Quiz, Performance, Pipeline, Setup, TODOs / edge cases, Verification, YouTube (+1 more)

### Community 15 - "generate.py"
Cohesion: 0.09
Nodes (41): difflib, _call(), _density(), difficulty_quotas(), DocChunk, excerpt(), generate(), _index() (+33 more)

### Community 16 - "gemini_json"
Cohesion: 0.12
Nodes (29): LLM providers (Groq multi-key → Gemini), gemini_json(), gemini_key(), _groq_json(), llm_configured(), LLMUnavailable, ollama_vision_json(), parse_json() (+21 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "Any"
Cohesion: 0.16
Nodes (10): absorb(), add_step(), advance(), open_ladders(), _PrerequisiteGate, Any, Orders the required rungs of several pathways into one sequence. SCIL v6 §5…, Does taking `course_id` complete this ladder's next rung? (+2 more)

### Community 19 - "test_pathway.py"
Cohesion: 0.08
Nodes (26): test_mandatory_courses_always_included_with_badge(), test_why_recommended_describes_the_level_step(), _edge(), _gap(), _kinds_levels(), Skill-gap levels + level-aware recommendations + learning pathways. Runs on a…, _resolved(), test_already_met_prerequisite_changes_nothing() (+18 more)

### Community 20 - "domain.ts"
Cohesion: 0.05
Nodes (46): DEFER_REASON, KIND_STYLE, PathwayLadder(), formatDate(), ProfileHeader(), ProfileHeaderProps, TAGLINE, AppliedPrerequisite (+38 more)

### Community 21 - "extractors.py"
Cohesion: 0.09
Nodes (35): concurrent_futures, capabilities(), get, JSONResponse, add_captions(), flush(), _budget(), caption_regions() (+27 more)

### Community 22 - "media_io.py"
Cohesion: 0.13
Nodes (23): Caption, _change(), download_youtube(), fetch(), is_youtube_url(), load_audio(), MediaInputError, _parse_json3() (+15 more)

### Community 23 - "learning_mode.py"
Cohesion: 0.11
Nodes (36): Code, Code, Connections, In / out, Personalised feedback (`items.feedback`), RAG Document → Quiz Generator & Grading (quiz ↔ skill gap), Verification, ErrorResponse (+28 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "ai_tools.py"
Cohesion: 0.07
Nodes (39): Code, Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, build_system_prompt(), generate_chat_response(), is_ollama_available() (+31 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "media_quiz.py"
Cohesion: 0.10
Nodes (27): csv, fastapi_responses, importlib_util, MediaMetadata, MediaQuizQuestion, MediaQuizResponse, _process(), BaseModel (+19 more)

### Community 28 - "test_irt.py"
Cohesion: 0.13
Nodes (22): DiagnosticSessions, fisher_information(), laplace_posterior(), next_item(), p_correct(), public_item(), Any, services/irt_service.py — Tier-1 Bayesian 2PL posterior + adaptive diagnostic… (+14 more)

### Community 29 - "Code"
Cohesion: 0.20
Nodes (8): AI Course Recommendation Engine + Learning Pathways, Code, Connections, In / out, TODOs / edge cases, The id whose FRAC tags / levels / official text drive retrieval., {courseId: {compId: FRAC level}} — feeds BaselineAssembler so the Verified…, {courseId: title, primary competency, format, rating, enrolments} for analytics…

### Community 30 - "CompetencyCalculator"
Cohesion: 0.29
Nodes (6): CompetencyCalculator, datetime, Maps FRAC types from the JSON to calculation categories., Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, test_missing_channels_do_not_drag_the_score_to_zero()

### Community 31 - "react"
Cohesion: 0.07
Nodes (52): Visual design system (shared by every page), AdminDashboard, App(), DashboardRedirect(), TokenBridge(), AshokaChakra(), CountUp(), GovEmblem() (+44 more)

### Community 32 - "typing"
Cohesion: 0.09
Nodes (24): asyncio, dotenv, Exception, httpx, json, adapters/igot_adapter.py — iGOT Platform Adapter…, FILE: ai/rag_engine.py…, _family() (+16 more)

### Community 33 - "api.ts"
Cohesion: 0.07
Nodes (30): LevelCheckModal(), OUTCOME, Props, answerDiagnostic(), AssignmentInput, awardKarmaEvent(), BehindRow, CatalogueCourse (+22 more)

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
Cohesion: 0.26
Nodes (16): Single source of truth for an official's level on one competency. Every…, resolve_level(), fuse_channels(), Weighted mean over the K/A/U/S channels that carry evidence (None → absent)., _assess(), SCIL v6 §3 evidence channels K/A/U/S (knowledge, application, utility,…, _row(), test_confirmed_use_is_a_floor_unconfirmed_is_not() (+8 more)

### Community 38 - "BaseModel"
Cohesion: 0.14
Nodes (13): field_validator, CompetencyOut, ContentStateRequest, CourseOut, ingest_telemetry(), JobProfileOut, BaseModel, Mirrors the authentic courses.json schema. (+5 more)

### Community 39 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 40 - "diagnostic.py"
Cohesion: 0.15
Nodes (20): LevelDispute, status: OPEN (test started) → CONFIRMED | RAISED | LOWER_THAN_SHOWN once the…, answer(), AnswerBody, BaseModel, get, routers/diagnostic.py — adaptive "check your level" diagnostic (SCIL v6 §2,…, Posterior mean → one PRACTICE_ASSESSMENT EvidenceLog row (the existing evidence… (+12 more)

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 42 - "karma_engine.py"
Cohesion: 0.18
Nodes (11): KarmaEventType, FixedPointsStrategy, ist_date(), ist_day_start_utc(), KarmaRule, MonthlyUsage, date, datetime (+3 more)

### Community 43 - "_resolve_competency_state"
Cohesion: 0.13
Nodes (19): Cold start for UNASSESSED competencies, Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8), Foresight, Proficiency belief with dated decay, _load_db_evidence(), iGOT profile competencyLevel ('Level 3') → 3; missing → 0 (no claim)., The LMS's own EvidenceLog rows for one user (sync — run in a worker thread)., Profile + enrollments + EvidenceLog → one resolved row per role competency.… (+11 more)

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
Cohesion: 0.09
Nodes (36): 7. Mismatches between the mermaid diagram and the code, Base, Conventions, TODOs / edge cases, Connections, In / out, Skill Gap Analysis (evidence-based competency baselines), TODOs / edge cases (+28 more)

### Community 58 - "opportunity"
Cohesion: 0.24
Nodes (13): opportunity(), Any, services/gsbpm_service.py — GSBPM scoping (SCIL v6 §1) + opportunity to…, Opportunity to practise a competency in the official's office this cycle (SCIL…, Which competencies are in scope under the officer-hours rule, and why., scope_report(), _sp_name(), subprocess_hours() (+5 more)

### Community 60 - "test_admin_analytics.py"
Cohesion: 0.14
Nodes (18): emerging_skills(), date, datetime, Daily training-rate history rebuilt from dated iGOT course completions, for…, Per FRAC competency, over the (filtered) officials in the workforce snapshot: *…, reconstruct_history(), Admin console aggregates (services/admin_analytics.py): filters, pagination,…, _snap_row() (+10 more)

### Community 61 - "estimate_uplift"
Cohesion: 0.08
Nodes (43): find_cycle(), infer_edges(), _node(), _norm_sf(), _ols(), Any, ndarray, services/prerequisite_service.py — cross-competency prerequisite DAG (SCIL v6… (+35 more)

### Community 62 - "admin_console.py"
Cohesion: 0.09
Nodes (39): AdminDailySnapshot, One row per calendar day (UTC): the workforce headline numbers plus the same…, An admin assigning courses (a training plan) to a department or a list of…, A reminder sent by an admin to an official behind on mandatory (ACBP) training., TrainingAssignment, TrainingNudge, _assignment_out(), AssignmentIn (+31 more)

### Community 63 - "Code"
Cohesion: 0.13
Nodes (13): Code, Cross-competency prerequisite DAG (SCIL v6 §5, B4), _competencies(), _prof_detail(), GET a Sunbird endpoint and return its `result` object., GET /api/frac/v1/prerequisites — {count, edges[]} expert-seeded prerequisite…, GET /api/course/v1/assessment/outcomes — {outcomes[], comparisons[]} pre/post θ…, GET /api/assessment/v1/itembank — 2PL items incl. answer keys (server side… (+5 more)

### Community 64 - "Code"
Cohesion: 0.07
Nodes (35): Code, Opportunity to practise (SCIL v6 §4), CareerReadinessCard(), Props, TIER_LABEL, CompetencyOverviewTable(), LevelPips(), priorityOf() (+27 more)

### Community 65 - "items.py"
Cohesion: 0.23
Nodes (28): ast, Document question pipeline (`main-lms-backend/services/doc_quiz/`), TODOs / edge cases, _build_review(), Type-aware answer review, missed questions first. Each wrong answer gets…, accepted_texts(), answer_display(), _choice_set() (+20 more)

### Community 66 - "probe.py"
Cohesion: 0.09
Nodes (28): needs_ocr(), _ocr_engine(), ocr_pdf_pages(), OcrUnavailable, ndarray, RuntimeError, FILE: services/doc_quiz/extract.py…, (text in reading order, mean confidence, weak lines dropped). (+20 more)

### Community 67 - "generate_mock_data.py"
Cohesion: 0.07
Nodes (58): _batch(), build_acbp(), build_catalog(), build_crosswalk(), build_enrollments(), build_frac(), build_gsbpm_map(), build_hrms() (+50 more)

### Community 68 - "test_gap_and_recommendation_upgrades.py"
Cohesion: 0.12
Nodes (22): calculate_baseline(), CertificateReview, EvidencePayload, BaseModel, Stateless calculator for one competency, on exactly the scoring path the…, explain_level(), "Why this level" for one competency, built only from numbers the API already…, correct_supervisor_rating() (+14 more)

### Community 69 - "Any"
Cohesion: 0.19
Nodes (9): ILearningPlatformAdapter, ABC, Any, Interface for external learning platform integration. All concrete adapters…, Return the full CBP course catalog., Return learning history for a user (legacy, by govId or userId)., Return the full user roster (all officials)., Look up a single user by their iGOT userId (usr_...). Returns None if not found. (+1 more)

### Community 70 - "LearnerDashboard.tsx"
Cohesion: 0.08
Nodes (27): LearnerDashboard, COLORS, LearningSnapshot(), Props, MyCoursesView(), MyCoursesViewProps, ProgressView(), ProgressViewProps (+19 more)

### Community 71 - "rag.py"
Cohesion: 0.18
Nodes (18): _detect_skill_name(), DocumentMetadata, DocumentUploadResponse, ErrorResponse, _generate_questions(), GradeRequest, GradeResponse, BaseModel (+10 more)

### Community 72 - "test_doc_quiz.py"
Cohesion: 0.10
Nodes (22): extract_docx(), Returns (text with section markers, section count)., _table_rows(), Document quiz: extraction (DOCX, OCR), cited multi-type generation, grading…, _chunks(), _mcq(), parametrize, services/doc_quiz — question types, validator, dedup, selection, calibration,… (+14 more)

### Community 76 - "HybridRecommendationEngine"
Cohesion: 0.17
Nodes (11): GapEntry, HybridRecommendationEngine, Singleton — built ONCE at app startup. Holds FAISS index + BM25 corpus in…, Computes and prioritizes skill gaps. priority_k = gap_k * (target_k / 5.0)…, (query embedding, BM25 scores over the whole corpus), cached., Stage 1 + Stage 2 for a single competency gap. Returns list of (catalog_idx,…, Retrieve (tag + level filtered), drop excluded courses, then score final =…, Cross-encoder scores of the top RERANK_TOP_N by RRF, min-max normalised; {} if… (+3 more)

### Community 77 - "AdminDashboard.tsx"
Cohesion: 0.10
Nodes (23): WorkforceInsights(), AsyncState, useAdminFacets(), useAdminRoster(), SkillRow, useSkillsData(), AdminDashboard(), AdminTab (+15 more)

### Community 87 - "WorkforceInsights.tsx"
Cohesion: 0.11
Nodes (24): AGENDA_TYPE, CapabilityRiskPanel(), ForesightPanel(), GsbpmScopePanel(), pct(), PrerequisitePanel(), PRIORITY_CHIP, RISK_CHIP (+16 more)

### Community 88 - "get_learning_pathway"
Cohesion: 0.20
Nodes (8): _ensure_can_view(), get_learning_pathway(), get_recommendations_by_user_id(), get_skill_gaps_by_user_id(), A learner may only read their own competency data; admins may read anyone's., Skill-gap analysis on the 6-term baseline formula — a weighted mean over the…, Level-gated hybrid recommendations: Stage 0 — gap prioritisation (priority_k =…, Step-by-step learning paths. For every role competency: one course per FRAC…

### Community 89 - "insights.py"
Cohesion: 0.15
Nodes (21): capability_risk(), _frac_names(), gsbpm_scope(), prerequisite_dag(), get, routers/insights.py — admin-only SCIL v6 workforce insights Every number here…, Rebuild the workforce snapshot now (≈ a few seconds)., Per statistical product: capable officials per critical competency, retirements… (+13 more)

### Community 90 - "mock-igot-server/main.py"
Cohesion: 0.12
Nodes (23): contextlib, fastapi_middleware_cors, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history() (+15 more)

### Community 91 - ".fetch_user_cbplan"
Cohesion: 0.17
Nodes (11): AsyncClient, fetch(), fetch(), fetch(), fetch(), Pooled client for the running loop — no new TCP connection per call., TTL memo for one user's read. Concurrent callers share one in-flight request;…, GET /api/evidence/v1/user/{id} — EvidenceLog-style workplace evidence rows ([]… (+3 more)

### Community 92 - "proficiency_service.py"
Cohesion: 0.19
Nodes (15): cluster_of(), expected_shortfall(), months_between(), office_phase(), _phi(), proficiency_state(), Any, datetime (+7 more)

### Community 93 - "Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)"
Cohesion: 0.25
Nodes (7): 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator

### Community 94 - "summary"
Cohesion: 0.17
Nodes (17): feedback_summary(), FeedbackBody, my_feedback(), post_feedback(), BaseModel, get, Session, downvoted_ids() (+9 more)

### Community 95 - "competency.py"
Cohesion: 0.29
Nodes (14): CertificateSubmission, One uploaded certificate (routers/competency.py). On upload each extracted…, certificates_for_review(), _find(), my_certificates(), get, Session, UploadFile (+6 more)

### Community 96 - "test_certificate_evidence.py"
Cohesion: 0.09
Nodes (32): fastapi, fastapi_security, fastapi_testclient, get_db(), auth/database.py…, FastAPI dependency — `db: Session = Depends(get_db)`; closed after the request., get_current_user(), Session (+24 more)

### Community 97 - "CourseCard.tsx"
Cohesion: 0.18
Nodes (13): BADGE_STYLE, CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps, MODALITY_LABEL, SOURCE_STYLES, matches() (+5 more)

### Community 98 - "lifespan"
Cohesion: 0.33
Nodes (7): lifespan(), _load_json(), _load_json_from_dir(), Any, FastAPI, Load all datasets into memory once at startup, so no request touches the file…, Load a JSON file from ROOT_DIR. Raises RuntimeError on missing file.

### Community 99 - "system_health.py"
Cohesion: 0.26
Nodes (18): is_semantic_engine_ready(), chat_mode(), get, Which response engine is active; the frontend shows it as a badge., groq_keys(), basic(), _component(), detailed() (+10 more)

### Community 100 - "chatbot.py"
Cohesion: 0.25
Nodes (20): low_confidence_threshold(), chat(), ChatRequest, ChatResponse, detect_intent_keyword(), _intent_response(), _intercept(), FILE: routers/chatbot.py Multilingual AI Learning Assistant — Gyan (ज्ञान)… (+12 more)

### Community 101 - "CertificateReviewQueue.tsx"
Cohesion: 0.16
Nodes (15): CertificateReviewQueue(), Row(), STATUS_CLS, TABS, when(), STATUS, SystemHealthPanel(), SectionAction() (+7 more)

### Community 102 - "workforce_service.py"
Cohesion: 0.24
Nodes (16): How the parts work, _Phi(), _as_date(), capability_risk(), cell(), foresight(), _level(), _p_capable() (+8 more)

### Community 103 - "BaselineAssembler"
Cohesion: 0.25
Nodes (7): BaselineAssembler, _normalise_course_map(), Accept {courseId: {compId: level}} or the legacy {courseId: [compId]}., test_verified_cert_lifts_confidence_over_documented(), The old `requiredLevel - 1` cap made every evidence-backed gap permanent., test_completion_evidence_follows_the_crosswalk(), test_evidence_can_close_a_gap()

### Community 104 - "sample_request"
Cohesion: 0.21
Nodes (15): ChatHistoryItem, BaseModel, RecommendationContext, SkillGapContext, sample_request(), _chat(), parametrize, End-to-end /chat behaviour per language through the real multilingual… (+7 more)

### Community 105 - "practice_assessment.py"
Cohesion: 0.07
Nodes (49): datetime, Practice ability (`main-lms-backend/services/practice_assessment.py`), _competency_rows(), grade_quiz(), Any, _question_difficulties(), The learner's resolved role competencies (same rows the skill-gap view shows),…, **Grade Quiz → Skill Gap** - user_id comes from the JWT… (+41 more)

### Community 106 - "EmergingSkills.tsx"
Cohesion: 0.13
Nodes (20): Frontend, AdminFilterBar(), ExportButton(), facetLabels(), describeFilters(), esc(), printReport(), ReportSection (+12 more)

### Community 107 - "DashboardCreator"
Cohesion: 0.16
Nodes (4): AdminDashboardCreator, DashboardCreator, OfficialDashboardCreator, TrainerDashboardCreator

### Community 108 - "Decisions log (made without the user)"
Cohesion: 0.18
Nodes (8): Before / after metrics, Could not do / blocked, Decisions log (made without the user), Noticed but out of scope (not fixed), SCIL v6 — mock data + blocked features: progress report, Status, Catalogue duration in hours, or None for a course not in the catalogue., Median cosine between the competency query and the courses NOT tagged with it —…

### Community 109 - "mock_igot_server.py"
Cohesion: 0.19
Nodes (15): composite_search(), CompositeSearchRequest, _course_tags(), _enriched_view(), EnrolPayload, get_enriched_courses(), legacy_enroll_user(), legacy_push_score() (+7 more)

### Community 110 - "admin_analytics.py"
Cohesion: 0.13
Nodes (29): Backend, overview(), _competency_metrics(), daily_metrics(), by(), dept_compliance(), facets(), Filters (+21 more)

### Community 111 - "MockIgotAdapter"
Cohesion: 0.20
Nodes (6): MockIgotAdapter, Forget every cached read for this user., The full CBP course catalogue, paged through POST /api/composite/v1/search.…, POST /api/composite/v1/search — Sunbird composite search, every page. `filters`…, Legacy method that maps fetch_user_enrollments to the old simple-mock shape.…, Calls the Sunbird-compliant mock iGOT server (mock_igot_server.py) on port 8001…

### Community 112 - "LearningChat.tsx"
Cohesion: 0.26
Nodes (12): ChatEntry, LearningChat(), LearningChatProps, fetchWithTimeout(), LearningChatResponse, LearningChatTurn, LearningCitation, LearningMetadata (+4 more)

### Community 113 - "engine"
Cohesion: 0.19
Nodes (14): on_event, Create users_auth table if it doesn't exist yet., _startup(), test_stored_embeddings_are_reused_only_when_text_matches(), test_tpac_boost_depends_on_provenance(), _course(), engine(), _frac() (+6 more)

### Community 114 - "_warm_up"
Cohesion: 0.15
Nodes (13): AbstractEventLoop, 3. Core data flow, Measured uplift → coverage learning + training effectiveness (SCIL v6 §6, B5), Workforce snapshot, _build_workforce_snapshot(), _learner_competency_state(), Everything slow, off the request path, on the "warm-up" thread's own loop so…, Every official's resolved competency rows, for the SCIL v6 population / cohort… (+5 more)

### Community 119 - "document_extractor.py"
Cohesion: 0.12
Nodes (32): Code, io, CertificateExtractionResult, _clamp_level(), DocumentExtractorService, ExtractedCompetency, ExtractionError, frac_by_id() (+24 more)

### Community 123 - "career.py"
Cohesion: 0.18
Nodes (19): career_readiness(), _dispute_view(), DisputeBody, _ensure_can_view(), my_disputes(), office_ladder(), open_dispute(), Any (+11 more)

### Community 124 - "Code"
Cohesion: 0.18
Nodes (14): Code, classify_intent(), Returns (best_intent, confidence). ("general", 0.0) if the embedder is…, detect_chat_language(), detect_chat_variant(), detect_chat_variant_or_none(), _devanagari_language(), Small, offline language routing for Gyan chat. This deliberately does *not* use… (+6 more)

### Community 126 - ".award_safe"
Cohesion: 0.25
Nodes (6): Connections, In / out, Karma Points (gamification), Rules (`RULES` in `karma_engine.py`, served by `GET /karma/rules`), TODOs / edge cases, For server-side hooks (quiz grading, diagnostics): own session, never raises.

### Community 127 - "CLAUDE.md"
Cohesion: 0.08
Nodes (22): CLAUDE.md — index & router, Feature index, graphify, How to use these docs, Run commands, Certificate / Resume Evidence Extraction, In / out, TODOs / edge cases (+14 more)

### Community 128 - "main-lms-backend/main.py"
Cohesion: 0.08
Nodes (35): 1. Runtime topology, get_achievements_by_user_id(), get_admin_roster(), get_enrollments_by_user_id(), get_frac_competencies(), get_profile_by_user_id(), health(), _level_to_int() (+27 more)

### Community 129 - "calibration.py"
Cohesion: 0.23
Nodes (13): Difficulty calibration (`services/doc_quiz/calibration.py`), QuizItemStat, Response data per quiz item (services/doc_quiz/calibration.py). itemKey is a…, calibrate(), calibrate_items(), difficulty_from_b(), load_stats(), Any (+5 more)

### Community 130 - "_create_schema"
Cohesion: 0.50
Nodes (5): _create_schema(), _create(), Create users_auth and the karma/evidence tables if missing (idempotent)., migrate_karma_schema(), Idempotent upgrade for databases created before the daily-cap rework: adds…

### Community 131 - "Admin Dashboard"
Cohesion: 0.50
Nodes (4): Admin Dashboard, Code, TODOs / edge cases, What the synthetic data shows

### Community 133 - "safe_eval"
Cohesion: 0.29
Nodes (7): _computed_ok(), expression_numbers(), Evaluate +,-,*,/,**,%, parentheses and a few math functions. Raises ValueError…, Literal numbers used in an expression (for the 'inputs come from the source'…, safe_eval(), ev(), test_safe_eval()

### Community 134 - "recommendation_service.py"
Cohesion: 0.12
Nodes (18): _course_summary(), _diagnostic_step(), _fmt_levels(), _interleave_by_level(), BaseModel, FILE: main-lms-backend/services/recommendation_service.py…, Returns deduplicated, level-gated recommendations in gap-priority order. Only…, Step-by-step path for one competency: one course per FRAC level from current+1… (+10 more)

### Community 135 - "catalogue_store.py"
Cohesion: 0.16
Nodes (17): base64, hashlib, _build_engine(), Engine + assembler from one catalogue (sync — run in a thread). Course vectors…, Reload the catalogue on a timer instead of only at restart. Every…, _refresh_catalogue_loop(), catalogue_fingerprint(), _decode_vec() (+9 more)

### Community 136 - "useLearnerDashboard.ts"
Cohesion: 0.12
Nodes (20): `frontend/src/`, Connections, In / out, Learner Dashboard (frontend shell), TODOs / edge cases, _cache, NO_ACHIEVEMENTS, NO_ENROLLMENTS (+12 more)

### Community 137 - "lmsFetch"
Cohesion: 0.28
Nodes (15): AdminActions(), AssignForm(), when(), consoleQs(), createAssignment(), downloadAdminCsv(), fetchAdminOverview(), fetchAdminTrends() (+7 more)

### Community 138 - "mock_data_metrics.py"
Cohesion: 0.15
Nodes (14): argparse, collections, _get(), live_metrics(), _login(), main(), offline_metrics(), _pct() (+6 more)

### Community 140 - "seed.py"
Cohesion: 0.22
Nodes (13): hash_password(), Return a bcrypt hash of the plain-text password., _derive_password(), _fetch_officials(), main(), Session, auth/seed.py…, Insert the hardcoded admin user. Returns True if inserted, False if already… (+5 more)

### Community 141 - "test_chat_messages.py"
Cohesion: 0.23
Nodes (11): Loads a language's template table on first use ("or" lives in or_.py; `or` is a…, templates(), _alternatives(), _fields(), parametrize, Catalogue completeness: every language has every template, placeholders are…, test_every_intent_renders(), test_placeholders_match_english() (+3 more)

### Community 142 - "_roster"
Cohesion: 0.23
Nodes (21): Endpoints (`/api/v1/admin/console`, all take `?department=&grade=&office=`), _behind(), _csv(), _emerging(), emerging_skills(), export_csv(), filter_options(), _filters() (+13 more)

### Community 143 - "get"
Cohesion: 0.14
Nodes (14): get_crosswalk(), get_org_roles(), health(), legacy_catalog(), legacy_frac(), legacy_job_profiles(), legacy_user_history(), get (+6 more)

### Community 144 - "test_proficiency_foresight.py"
Cohesion: 0.27
Nodes (10): decay(), (μ_t, σ_t, λ) — relax the belief toward the population prior as evidence ages., _hrms(), SCIL v6 §2 dated decay / expected-shortfall / cold start, and §11 workforce…, _snap(), test_accuracy_skills_decay_faster_than_procedural(), test_counts_of_one_to_four_are_suppressed(), test_decay_relaxes_toward_the_population_mean_not_zero() (+2 more)

### Community 145 - "TrendsPanel.tsx"
Cohesion: 0.24
Nodes (9): fmtDate(), RANGES, RATE_SERIES, SERIES_DARK, SERIES_LIGHT, TrendsPanel(), recordAdminSnapshot(), TrendPoint (+1 more)

### Community 146 - "Authentication & RBAC"
Cohesion: 0.40
Nodes (4): Authentication & RBAC, Connections, In / out, Shared database (Neon)

### Community 147 - "Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)"
Cohesion: 0.22
Nodes (7): GSBPM scope — the 80% officer-hours rule (SCIL v6 §1), Reference data loading, TODOs / limits, Used by the admin console, Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight), GET /api/gsbpm/v1/map — GSBPM sub-processes + competency → sub-processes., GET /api/org/v1/offices — {cycle, offices[{officeId, subprocesses[{id,…

### Community 148 - "CertificateUploadZone.tsx"
Cohesion: 0.31
Nodes (7): CertificateUploadZone(), clean(), STATUS_CHIP, CertificateStatus, CertificateSubmission, fetchMyCertificates(), uploadCertificate()

### Community 149 - "logging"
Cohesion: 0.05
Nodes (54): Code, Connections, In / out, Shared Embedder (chat + catalog roles), TODOs / edge cases, functools, logging, _Embedder (+46 more)

### Community 150 - "rerank_scores"
Cohesion: 0.67
Nodes (3): ndarray, Cross-encoder scores for `passages` against `query`, or None if no reranker., rerank_scores()

### Community 153 - "pydantic"
Cohesion: 0.31
Nodes (8): ChangePasswordRequest, Config, BaseModel, auth/schemas.py…, RefreshResponse, TokenResponse, UserAuthOut, pydantic

### Community 154 - ".__init__"
Cohesion: 0.25
Nodes (6): ndarray, Stable hash of a course's embedded text — decides whether a stored vector is…, `catalog` / `frac` / `crosswalk` are the lists served by the mock iGOT server…, Stored vectors whose text hash still matches; encode (disk-memoised) the rest., [(courseId, text_hash, vector)] — what catalogue_store persists., text_hash()

### Community 155 - "_sunbird_result"
Cohesion: 0.25
Nodes (5): GET /api/frac/competencies — the catalogue FRAC set incl. L1–L5 descriptors., GET /api/frac/v1/crosswalk — iGOT dictionary CID id → catalogue FRAC id., GET /api/admin/v1/users Returns: result.users — full list of officials., Safely drill into a Sunbird envelope: data['result']['key1']['key2']..., _sunbird_result()

### Community 156 - "._quality_score"
Cohesion: 0.25
Nodes (6): _CourseDoc, _parse_level(), Bayesian shrinkage toward global prior mean. Returns None if either input is…, Level 3' / 3 / '3' → 3; anything outside 1..5 → None., quality = 0.35*completion_n + 0.35*rating_n + 0.20*pop_n + 0.10*tpac_flag FIX…, _shrunk_rating()

### Community 157 - "dataclasses"
Cohesion: 0.40
Nodes (3): dataclasses, Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile()

### Community 158 - "chat_actions.py"
Cohesion: 0.50
Nodes (4): detect_ui_actions(), _mentions(), Detect website theme / language changes requested in any supported chat…, Returns (theme, language): theme in {"dark", "light", "toggle"}, language in…

## Knowledge Gaps
- **300 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+295 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1053 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `UserAuth` connect `UserAuth` to `test_certificate_evidence.py`, `main-lms-backend/main.py`, `Code`, `rag.py`, `diagnostic.py`, `karma.py`, `practice_assessment.py`, `seed.py`, `_roster`, `admin_analytics.py`, `models/models.py`, `document_extractor.py`, `summary`, `get_learning_pathway`, `insights.py`, `career.py`, `admin_console.py`, `competency.py`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `Code` connect `Code` to `api.ts`, `_create_schema`, `AwardResult`, `karma.py`, `KarmaRewardsView.tsx`, `diagnostic.py`, `practice_assessment.py`, `karma_engine.py`, `domain.ts`, `.fetch_user_cbplan`, `.award_safe`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `Code` connect `Code` to `test_certificate_evidence.py`, `lmsFetch`, `seed.py`, `UserAuth`, `engine`, `Authentication & RBAC`, `react`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 78 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `HybridRecommendationEngine` (e.g. with `7. Mismatches between the mermaid diagram and the code` and `Code`) actually correct?**
  _`HybridRecommendationEngine` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 45 inferred relationships involving `Code` (e.g. with `KarmaCard()` and `formatPoints()`) actually correct?**
  _`Code` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _300 weakly-connected nodes found - possible documentation gaps or missing edges._