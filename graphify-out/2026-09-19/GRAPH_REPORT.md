# Graph Report - SIH_IGot  (2026-09-19)

## Corpus Check
- 254 files · ~4,962,412 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .css 1, .example 1)

## Summary
- 2939 nodes · 7278 edges · 154 communities (115 shown, 39 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 821 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5fe9d438`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- chatbot.py
- AssessmentPage.tsx
- Code
- router.py
- package.json
- _require_auth
- _user_enrolments
- HomeChatWidget.tsx
- karma.py
- lucide-react
- Request
- pipeline.py
- Code
- UserAuth
- Timeline
- generate.py
- gemini_json
- What You Must Do When Invoked
- .build_study_plan
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
- Gyan — Multilingual Chat Assistant
- CompetencyCalculator
- react
- providers.py
- api.ts
- AwardResult
- speech.d.ts
- graphify reference: extra exports and benchmark
- resolve_level
- post
- compilerOptions
- diagnostic.py
- graphify reference: query, path, explain
- karma_engine.py
- test_proficiency_foresight.py
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- test_mock_data.py
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- rag.py
- .claude/CLAUDE.md
- extraction-spec.md
- opportunity
- test_admin_analytics.py
- estimate_uplift
- _db
- MockIgotAdapter
- devDependencies
- items.py
- extract.py
- generate_mock_data.py
- test_gap_and_recommendation_upgrades.py
- igot_adapter.py
- ChatWidget.tsx
- _generate_questions
- test_doc_quiz.py
- faker
- services_chat_messages
- services_chat_messages_context
- HybridRecommendationEngine
- probe.py
- bn.py
- en.py
- gu.py
- hi.py
- hi_latn.py
- mr.py
- or_.py
- ta.py
- te.py
- chatApi.ts
- get_learning_pathway
- insights.py
- mock-igot-server/main.py
- Any
- proficiency_service.py
- Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)
- services/__init__.py
- competency.py
- test_certificate_evidence.py
- CourseCard.tsx
- mock_igot_server.py
- system_health.py
- useChatEngine.ts
- record_daily_snapshot
- workforce_service.py
- BaselineAssembler
- dependencies
- practice_assessment.py
- AdminDashboard.tsx
- DashboardCreator
- Decisions log (made without the user)
- get_enriched_courses
- admin_analytics.py
- .fetch_catalog
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
- scripts
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
- _build_engine
- useLearnerDashboard.ts
- _course_by_id
- mock_data_metrics.py
- services
- _OnnxEmbedder
- admin_console.py
- typing
- CLAUDE.md — index & router
- Authentication & RBAC
- Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)
- get_embedder
- reranker.py
- services_media_quiz_llm
- services_media_quiz_pipeline
- Learning Mode — NotebookLM-style study chat (AI Assessment Studio)
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
- `Code` --references--> `WhyThisLevel()`  [INFERRED]
  docs/features/skill-gap-analysis.md → frontend/src/components/dashboard/SkillGapCard.tsx
- `Code` --references--> `StatTone`  [INFERRED]
  docs/features/learner-dashboard.md → frontend/src/components/shell/StatCard.tsx
- `TODOs / edge cases` --references--> `gradeQuiz()`  [INFERRED]
  docs/features/media-quiz-generator.md → frontend/src/services/api.ts
- `7. Mismatches between the mermaid diagram and the code` --references--> `SkillGapReport`  [INFERRED]
  ARCHITECTURE.md → frontend/src/types/domain.ts
- `Code` --references--> `KarmaLevel`  [INFERRED]
  docs/features/karma-points.md → frontend/src/types/domain.ts

## Import Cycles
- None detected.

## Communities (154 total, 39 thin omitted)

### Community 0 - "chatbot.py"
Cohesion: 0.05
Nodes (83): Code, importlib, classify_intent(), Returns (best_intent, confidence). ("general", 0.0) if the embedder is…, Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile(), chat(), ChatHistoryItem (+75 more)

### Community 1 - "AssessmentPage.tsx"
Cohesion: 0.05
Nodes (65): Gyan hand-off (document → quiz or Learning Mode, no second upload), Frontend, CONTENT_LABEL, MediaAnalysisCard(), MediaAnswerReview(), pct(), QuestionEvidence(), SOURCE_LABEL (+57 more)

### Community 2 - "Code"
Cohesion: 0.15
Nodes (15): Code, KarmaMonthlyUsage, Rolling monthly counter for non-CBP COURSE_COMPLETION events. Enforces the…, ist_now(), KarmaEngine, Session, Dispatches an eventType to its strategy, then applies the shared rules in…, Idempotency key for an event; None means 'not idempotent' (admin only). (+7 more)

### Community 3 - "router.py"
Cohesion: 0.06
Nodes (58): bcrypt, Code, fastapi_security, jose, change_password(), _clear_refresh_cookie(), get_me(), login() (+50 more)

### Community 4 - "package.json"
Cohesion: 0.11
Nodes (17): name, private, type, version, autoprefixer, eslint, eslint-plugin-react-hooks, eslint-plugin-react-refresh (+9 more)

### Community 5 - "_require_auth"
Cohesion: 0.14
Nodes (34): get_assessment_outcomes(), get_crosswalk(), get_gsbpm_map(), get_hrms_officials(), get_item_bank(), get_office(), get_offices(), get_org_roles() (+26 more)

### Community 6 - "_user_enrolments"
Cohesion: 0.40
Nodes (5): get_admin_roster(), legacy_user_history(), Merge seed enrolments with any runtime mutations., ICatalogSync.fetchUserHistory() — consumed by MockIgotPlatformAdapter., _user_enrolments()

### Community 7 - "HomeChatWidget.tsx"
Cohesion: 0.14
Nodes (18): LanguageMenu(), LanguageMenuProps, VoiceButton(), CAPABILITIES, HomeChatWidgetProps, MessageBubble(), renderMarkdown(), SUGGESTIONS (+10 more)

### Community 8 - "karma.py"
Cohesion: 0.17
Nodes (24): fastapi_concurrency, KarmaEvent, Immutable ledger entry — one row per karma point award event., admin_adjust_karma(), AdminAdjustRequest, _assert_self_or_admin(), award_karma_event(), _award_response() (+16 more)

### Community 9 - "lucide-react"
Cohesion: 0.09
Nodes (30): CareerReadinessCard(), Props, TIER_LABEL, KarmaCard(), PassbookRow(), PILL_ORDER, RightSidebarProps, EVENT_META (+22 more)

### Community 10 - "Request"
Cohesion: 0.22
Nodes (9): exception_handler, HTTPException, get_competencies(), get_job_profiles(), http_exc_handler(), GET /api/job-profiles — NCO Job Role Catalogue (Sunbird-compliant). Served from…, The FRAC competencies roles and courses are tagged with (the catalogue id…, _ts_now() (+1 more)

### Community 11 - "pipeline.py"
Cohesion: 0.09
Nodes (32): Code, main(), FILE: scripts/eval_media_quiz.py…, fact_check(), _match(), protect_terms(), FILE: services/media_quiz/fact_check.py…, Translate strings with glossary terms protected as ⟦Tn⟧. Returns (translations… (+24 more)

### Community 12 - "Code"
Cohesion: 0.12
Nodes (32): Code, assess_competency(), rows_for(), tag_id(), _completed_courses(), _education_score(), enrollment_course_id(), explain_level() (+24 more)

### Community 13 - "UserAuth"
Cohesion: 0.09
Nodes (30): AuthBase, UserAuth, get_achievements(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments(), get_enrollments_by_user_id(), get_profile_by_user_id() (+22 more)

### Community 14 - "Timeline"
Cohesion: 0.08
Nodes (28): In / out, Media (Video / Audio / YouTube) → Evidence-Cited Quiz, Performance, Pipeline, Setup, TODOs / edge cases, Verification, YouTube (+20 more)

### Community 15 - "generate.py"
Cohesion: 0.09
Nodes (42): _call(), _density(), difficulty_quotas(), DocChunk, excerpt(), generate(), _index(), _jaccard() (+34 more)

### Community 16 - "gemini_json"
Cohesion: 0.15
Nodes (23): gemini_json(), _groq_json(), llm_configured(), LLMUnavailable, ollama_vision_json(), parse_json(), Any, RuntimeError (+15 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - ".build_study_plan"
Cohesion: 0.25
Nodes (6): absorb(), add_step(), advance(), open_ladders(), Orders the required rungs of several pathways into one sequence. SCIL v6 §5…, Does taking `course_id` complete this ladder's next rung?

### Community 19 - "test_pathway.py"
Cohesion: 0.09
Nodes (21): hashlib, _edge(), _kinds_levels(), Skill-gap levels + level-aware recommendations + learning pathways. Runs on a…, _resolved(), test_already_met_prerequisite_changes_nothing(), test_completed_never_suggested_and_in_progress_is_continued(), test_crosswalked_competency_gets_a_ladder_under_its_own_id() (+13 more)

### Community 20 - "domain.ts"
Cohesion: 0.03
Nodes (95): Code, Opportunity to practise (SCIL v6 §4), CompetencyOverviewTable(), LevelPips(), priorityOf(), Props, DEFER_REASON, KIND_STYLE (+87 more)

### Community 21 - "extractors.py"
Cohesion: 0.09
Nodes (35): concurrent_futures, capabilities(), get, JSONResponse, add_captions(), flush(), _budget(), caption_regions() (+27 more)

### Community 22 - "media_io.py"
Cohesion: 0.13
Nodes (24): Caption, _change(), download_youtube(), fetch(), is_youtube_url(), Keyframe, load_audio(), MediaInputError (+16 more)

### Community 23 - "learning_mode.py"
Cohesion: 0.10
Nodes (42): Code, Code, Connections, Personalised feedback (`items.feedback`), ErrorResponse, _generate_overview(), learning_chat(), LearningChatMessage (+34 more)

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
Cohesion: 0.21
Nodes (16): importlib_util, MediaMetadata, MediaQuizQuestion, MediaQuizResponse, _process(), BaseModel, on_event, UploadFile (+8 more)

### Community 28 - "test_irt.py"
Cohesion: 0.13
Nodes (22): DiagnosticSessions, fisher_information(), laplace_posterior(), next_item(), p_correct(), public_item(), Any, services/irt_service.py — Tier-1 Bayesian 2PL posterior + adaptive diagnostic… (+14 more)

### Community 29 - "Gyan — Multilingual Chat Assistant"
Cohesion: 0.22
Nodes (8): Connections, Gyan — Multilingual Chat Assistant, In / out, TODOs / edge cases, AI Course Recommendation Engine + Learning Pathways, In / out, TODOs / edge cases, _readiness_gate()

### Community 30 - "CompetencyCalculator"
Cohesion: 0.29
Nodes (6): CompetencyCalculator, datetime, Maps FRAC types from the JSON to calculation categories., Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, test_missing_channels_do_not_drag_the_score_to_zero()

### Community 31 - "react"
Cohesion: 0.05
Nodes (63): Visual design system (shared by every page), AdminDashboard, App(), AssessmentPage, DashboardRedirect(), LearnerDashboard, TokenBridge(), AshokaChakra() (+55 more)

### Community 32 - "providers.py"
Cohesion: 0.11
Nodes (19): dataclasses, LLM providers (Groq multi-key → Gemini), Exception, _family(), GroqProvider, _Key, parse_json_object(), ProviderError (+11 more)

### Community 33 - "api.ts"
Cohesion: 0.04
Nodes (74): AGENDA_TYPE, CapabilityRiskPanel(), ForesightPanel(), GsbpmScopePanel(), pct(), PrerequisitePanel(), PRIORITY_CHIP, RISK_CHIP (+66 more)

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

### Community 38 - "post"
Cohesion: 0.11
Nodes (19): field_validator, post(), CompetencyOut, composite_search(), CompositeSearchRequest, ContentStateRequest, CourseOut, get_content_state() (+11 more)

### Community 39 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 40 - "diagnostic.py"
Cohesion: 0.18
Nodes (17): answer(), AnswerBody, BaseModel, get, routers/diagnostic.py — adaptive "check your level" diagnostic (SCIL v6 §2,…, Posterior mean → one PRACTICE_ASSESSMENT EvidenceLog row (the existing evidence…, Close the level dispute that started this session (if any): the tested level is…, Start an adaptive session for one role competency (also used by level disputes). (+9 more)

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 42 - "karma_engine.py"
Cohesion: 0.18
Nodes (11): KarmaEventType, FixedPointsStrategy, ist_date(), ist_day_start_utc(), KarmaRule, MonthlyUsage, date, datetime (+3 more)

### Community 43 - "test_proficiency_foresight.py"
Cohesion: 0.17
Nodes (18): iGOT profile competencyLevel ('Level 3') → 3; missing → 0 (no claim)., Profile + enrollments + EvidenceLog → one resolved row per role competency.…, _resolve_competency_state(), _self_reported_level(), cohort_prior(), population_stats(), Cohort prior for an UNASSESSED competency, with the divergence check., comp → (μ_pop, σ_pop, n) over officials with assessed evidence on it. (+10 more)

### Community 44 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 45 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 46 - "test_mock_data.py"
Cohesion: 0.06
Nodes (17): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only, Any, _read_disk(), data(), files(), fixture (+9 more)

### Community 49 - "rag.py"
Cohesion: 0.08
Nodes (45): 7. Mismatches between the mermaid diagram and the code, Base, Conventions, enum, Admin, Assessment, AssessmentSkillMapping, BaseUser (+37 more)

### Community 58 - "opportunity"
Cohesion: 0.17
Nodes (17): Connections, In / out, Skill Gap Analysis (evidence-based competency baselines), TODOs / edge cases, opportunity(), Any, services/gsbpm_service.py — GSBPM scoping (SCIL v6 §1) + opportunity to…, Opportunity to practise a competency in the official's office this cycle (SCIL… (+9 more)

### Community 60 - "test_admin_analytics.py"
Cohesion: 0.15
Nodes (17): emerging_skills(), date, datetime, Daily training-rate history rebuilt from dated iGOT course completions, for…, Per FRAC competency, over the (filtered) officials in the workforce snapshot: *…, reconstruct_history(), Admin console aggregates (services/admin_analytics.py): filters, pagination,…, _snap_row() (+9 more)

### Community 61 - "estimate_uplift"
Cohesion: 0.08
Nodes (43): find_cycle(), infer_edges(), _node(), _norm_sf(), _ols(), Any, ndarray, services/prerequisite_service.py — cross-competency prerequisite DAG (SCIL v6… (+35 more)

### Community 62 - "_db"
Cohesion: 0.14
Nodes (15): A reminder sent by an admin to an official behind on mandatory (ACBP) training., TrainingNudge, _db(), _ensure_self_or_admin(), _last_nudges(), mark_nudge_read(), my_training_actions(), Run fn(session) in the threadpool with a committed-or-rolled-back session. (+7 more)

### Community 63 - "MockIgotAdapter"
Cohesion: 0.10
Nodes (21): Code, Cross-competency prerequisite DAG (SCIL v6 §5, B4), GSBPM scope — the 80% officer-hours rule (SCIL v6 §1), Reference data loading, TODOs / limits, Used by the admin console, Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight), _competencies() (+13 more)

### Community 64 - "devDependencies"
Cohesion: 0.14
Nodes (14): devDependencies, autoprefixer, eslint, eslint-plugin-react-hooks, eslint-plugin-react-refresh, postcss, tailwindcss, @types/react (+6 more)

### Community 65 - "items.py"
Cohesion: 0.24
Nodes (27): ast, Document question pipeline (`main-lms-backend/services/doc_quiz/`), _build_review(), Type-aware answer review, missed questions first. Each wrong answer gets…, accepted_texts(), answer_display(), _choice_set(), correct_display() (+19 more)

### Community 66 - "extract.py"
Cohesion: 0.17
Nodes (15): needs_ocr(), _ocr_engine(), ocr_pdf_pages(), OcrUnavailable, ndarray, RuntimeError, FILE: services/doc_quiz/extract.py…, (text in reading order, mean confidence, weak lines dropped). (+7 more)

### Community 67 - "generate_mock_data.py"
Cohesion: 0.07
Nodes (58): _batch(), build_acbp(), build_catalog(), build_crosswalk(), build_enrollments(), build_frac(), build_gsbpm_map(), build_hrms() (+50 more)

### Community 68 - "test_gap_and_recommendation_upgrades.py"
Cohesion: 0.10
Nodes (26): calculate_baseline(), CertificateReview, EvidencePayload, BaseModel, Stateless calculator for one competency, on exactly the scoring path the…, correct_supervisor_rating(), rater_leniency_offsets(), FILE: main-lms-backend/services/competency_service.py… (+18 more)

### Community 69 - "igot_adapter.py"
Cohesion: 0.12
Nodes (11): ILearningPlatformAdapter, _prof_detail(), ABC, adapters/igot_adapter.py — iGOT Platform Adapter…, Safely read a field from profileDetails.professionalDetails[0]., Interface for external learning platform integration. All concrete adapters…, Return the full CBP course catalog., Return learning history for a user (legacy, by govId or userId). (+3 more)

### Community 70 - "ChatWidget.tsx"
Cohesion: 0.20
Nodes (9): GyanBot(), GyanHero(), CAPABILITIES, MessageBubble(), renderMarkdown(), SUGGESTION_KEYS, PendingStudioUpload, setPendingStudioUpload() (+1 more)

### Community 71 - "_generate_questions"
Cohesion: 0.25
Nodes (9): _competency_rows(), _generate_questions(), Any, QuizQuestion, The learner's resolved role competencies (same rows the skill-gap view shows),…, Stamp each item with its content key and its response-calibrated difficulty.…, Cited, validated, multi-type questions (services/doc_quiz/generate.py) →…, _row_snapshot() (+1 more)

### Community 72 - "test_doc_quiz.py"
Cohesion: 0.13
Nodes (17): Document quiz: extraction (DOCX, OCR), cited multi-type generation, grading…, _chunks(), _mcq(), parametrize, services/doc_quiz — question types, validator, dedup, selection, calibration,…, test_choice_feedback_uses_option_rationale(), test_courses_for_topics_prefers_competency_courses(), test_fill_blank_and_true_false_rules() (+9 more)

### Community 76 - "HybridRecommendationEngine"
Cohesion: 0.11
Nodes (19): Code, _CourseDoc, GapEntry, HybridRecommendationEngine, Returns deduplicated, level-gated recommendations in gap-priority order. Only…, The id whose FRAC tags / levels / official text drive retrieval., Singleton — built ONCE at app startup. Holds FAISS index + BM25 corpus in…, [(courseId, text_hash, vector)] — what catalogue_store persists. (+11 more)

### Community 77 - "probe.py"
Cohesion: 0.22
Nodes (10): VideoScan, probe(), ProbeResult, ndarray, FILE: services/media_quiz/probe.py…, `regions` — precomputed speech spans (e.g. from YouTube captions) instead of…, route(), speech_regions() (+2 more)

### Community 87 - "chatApi.ts"
Cohesion: 0.29
Nodes (10): buildLocalReply(), ChatApiPayload, detectIntent(), detectLanguage(), fmtGaps(), fmtRecs(), HINGLISH_WORDS, INTENT_PATTERNS (+2 more)

### Community 88 - "get_learning_pathway"
Cohesion: 0.20
Nodes (8): _ensure_can_view(), get_learning_pathway(), get_recommendations_by_user_id(), get_skill_gaps_by_user_id(), A learner may only read their own competency data; admins may read anyone's., Skill-gap analysis on the 6-term baseline formula — a weighted mean over the…, Level-gated hybrid recommendations: Stage 0 — gap prioritisation (priority_k =…, Step-by-step learning paths. For every role competency: one course per FRAC…

### Community 89 - "insights.py"
Cohesion: 0.15
Nodes (21): capability_risk(), _frac_names(), gsbpm_scope(), prerequisite_dag(), get, routers/insights.py — admin-only SCIL v6 workforce insights Every number here…, Rebuild the workforce snapshot now (≈ a few seconds)., Per statistical product: capable officials per critical competency, retirements… (+13 more)

### Community 90 - "mock-igot-server/main.py"
Cohesion: 0.13
Nodes (21): enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history(), health(), lifespan() (+13 more)

### Community 91 - "Any"
Cohesion: 0.12
Nodes (18): AsyncClient, fetch(), fetch(), fetch(), fetch(), Any, Pooled client for the running loop — no new TCP connection per call., TTL memo for one user's read. Concurrent callers share one in-flight request;… (+10 more)

### Community 92 - "proficiency_service.py"
Cohesion: 0.15
Nodes (19): cluster_of(), decay(), expected_shortfall(), months_between(), office_phase(), _phi(), proficiency_state(), Any (+11 more)

### Community 93 - "Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)"
Cohesion: 0.17
Nodes (11): 1. Runtime topology, 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator (+3 more)

### Community 94 - "services/__init__.py"
Cohesion: 0.15
Nodes (20): feedback_summary(), FeedbackBody, my_feedback(), post_feedback(), BaseModel, get, Session, routers/recommendation_feedback.py — log clicks, enrolments and thumbs on… (+12 more)

### Community 95 - "competency.py"
Cohesion: 0.24
Nodes (14): datetime, certificates_for_review(), _find(), my_certificates(), get, Session, UploadFile, FILE: main-lms-backend/routers/competency.py… (+6 more)

### Community 96 - "test_certificate_evidence.py"
Cohesion: 0.10
Nodes (22): contextlib, fastapi_testclient, get_db(), auth/database.py…, FastAPI dependency — `db: Session = Depends(get_db)`; closed after the request., auth/models.py…, services/app_state.py — process-wide singletons built in main._warm_up…, Plain holder; every attribute defaults to empty so features degrade, not crash. (+14 more)

### Community 97 - "CourseCard.tsx"
Cohesion: 0.20
Nodes (12): BADGE_STYLE, CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps, MODALITY_LABEL, SOURCE_STYLES, matches() (+4 more)

### Community 98 - "mock_igot_server.py"
Cohesion: 0.14
Nodes (17): fastapi_responses, legacy_catalog(), legacy_frac(), legacy_job_profiles(), legacy_push_score(), lifespan(), _load_json(), _load_json_from_dir() (+9 more)

### Community 99 - "system_health.py"
Cohesion: 0.23
Nodes (20): is_embedder_ready(), Non-blocking check — True only if the role's model is already loaded., is_semantic_engine_ready(), chat_mode(), get, Which response engine is active; the frontend shows it as a badge., groq_keys(), basic() (+12 more)

### Community 100 - "useChatEngine.ts"
Cohesion: 0.36
Nodes (8): ChatWidgetProps, Props, PendingNavAction, UseChatEngineOptions, UseChatEngineReturn, ChatMessage, NavigateAction, CourseRecommendation

### Community 101 - "record_daily_snapshot"
Cohesion: 0.29
Nodes (8): AdminDailySnapshot, One row per calendar day (UTC): the workforce headline numbers plus the same…, daily_snapshot_loop(), Upsert today's AdminDailySnapshot from the live roster + workforce snapshot., Started once from main._startup. Waits for the DB, gives the workforce snapshot…, record_daily_snapshot(), upsert(), trends_snapshot_now()

### Community 102 - "workforce_service.py"
Cohesion: 0.22
Nodes (17): How the parts work, _Phi(), _as_date(), capability_risk(), cell(), foresight(), _level(), _p_capable() (+9 more)

### Community 103 - "BaselineAssembler"
Cohesion: 0.18
Nodes (9): Connections, BaselineAssembler, _normalise_course_map(), Accept {courseId: {compId: level}} or the legacy {courseId: [compId]}., {courseId: {compId: FRAC level}} — feeds BaselineAssembler so the Verified…, test_verified_cert_lifts_confidence_over_documented(), The old `requiredLevel - 1` cap made every evidence-backed gap permanent., test_completion_evidence_follows_the_crosswalk() (+1 more)

### Community 104 - "dependencies"
Cohesion: 0.33
Nodes (6): dependencies, lucide-react, react, react-dom, react-router-dom, recharts

### Community 105 - "practice_assessment.py"
Cohesion: 0.08
Nodes (42): Practice ability (`main-lms-backend/services/practice_assessment.py`), grade_quiz(), _question_difficulties(), **Grade Quiz → Skill Gap** - user_id comes from the JWT…, Per-question difficulty for grading, calibrated from response data…, bump(), courses_for_topics(), latest_practice_value() (+34 more)

### Community 106 - "AdminDashboard.tsx"
Cohesion: 0.07
Nodes (68): Frontend, AdminActions(), AssignForm(), when(), AdminFilterBar(), ExportButton(), facetLabels(), describeFilters() (+60 more)

### Community 107 - "DashboardCreator"
Cohesion: 0.16
Nodes (4): AdminDashboardCreator, DashboardCreator, OfficialDashboardCreator, TrainerDashboardCreator

### Community 108 - "Decisions log (made without the user)"
Cohesion: 0.18
Nodes (8): Before / after metrics, Could not do / blocked, Decisions log (made without the user), Noticed but out of scope (not fixed), SCIL v6 — mock data + blocked features: progress report, Status, Catalogue duration in hours, or None for a course not in the catalogue., Median cosine between the competency query and the courses NOT tagged with it —…

### Community 109 - "get_enriched_courses"
Cohesion: 0.40
Nodes (6): _course_tags(), _enriched_view(), get_enriched_courses(), _matches_filters(), Sunbird-style filters: each key → value or list of accepted values., The catalogue in the older "enriched" shape. Query params:…

### Community 110 - "admin_analytics.py"
Cohesion: 0.13
Nodes (30): Backend, overview(), _competency_metrics(), daily_metrics(), by(), dept_compliance(), facets(), Filters (+22 more)

### Community 112 - "LearningChat.tsx"
Cohesion: 0.26
Nodes (12): ChatEntry, LearningChat(), LearningChatProps, fetchWithTimeout(), LearningChatResponse, LearningChatTurn, LearningCitation, LearningMetadata (+4 more)

### Community 113 - "engine"
Cohesion: 0.20
Nodes (13): on_event, Create users_auth table if it doesn't exist yet., _startup(), test_stored_embeddings_are_reused_only_when_text_matches(), _course(), engine(), _frac(), fixture (+5 more)

### Community 114 - "_warm_up"
Cohesion: 0.10
Nodes (20): AbstractEventLoop, 3. Core data flow, Connections, In / out, Shared Embedder (chat + catalog roles), TODOs / edge cases, Workforce snapshot, _build_workforce_snapshot() (+12 more)

### Community 119 - "document_extractor.py"
Cohesion: 0.11
Nodes (35): Code, CertificateExtractionResult, _clamp_level(), DocumentExtractorService, ExtractedCompetency, ExtractionError, frac_by_id(), frac_dictionary() (+27 more)

### Community 123 - "career.py"
Cohesion: 0.18
Nodes (19): LevelDispute, status: OPEN (test started) → CONFIRMED | RAISED | LOWER_THAN_SHOWN once the…, career_readiness(), _dispute_view(), DisputeBody, _ensure_can_view(), my_disputes(), office_ladder() (+11 more)

### Community 124 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, preview

### Community 126 - ".award_safe"
Cohesion: 0.25
Nodes (6): Connections, In / out, Karma Points (gamification), Rules (`RULES` in `karma_engine.py`, served by `GET /karma/rules`), TODOs / edge cases, For server-side hooks (quiz grading, diagnostics): own session, never raises.

### Community 127 - "CLAUDE.md"
Cohesion: 0.24
Nodes (7): Certificate / Resume Evidence Extraction, Connections, In / out, TODOs / edge cases, Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server + mock data)

### Community 128 - "main-lms-backend/main.py"
Cohesion: 0.07
Nodes (42): fastapi, fastapi_middleware_cors, httpx, get_current_user(), Session, auth/dependencies.py…, Decodes the Bearer JWT, looks up the user in auth.db. Raises HTTP 401 for any…, Returns a FastAPI dependency that checks the current user's role. Example:… (+34 more)

### Community 129 - "calibration.py"
Cohesion: 0.23
Nodes (12): Difficulty calibration (`services/doc_quiz/calibration.py`), calibrate(), calibrate_items(), difficulty_from_b(), load_stats(), Any, FILE: services/doc_quiz/calibration.py…, responses: [{key, correct, llm_difficulty, type, question}] from ONE first… (+4 more)

### Community 130 - "_create_schema"
Cohesion: 0.50
Nodes (5): _create_schema(), _create(), Create users_auth and the karma/evidence tables if missing (idempotent)., migrate_karma_schema(), Idempotent upgrade for databases created before the daily-cap rework: adds…

### Community 131 - "Admin Dashboard"
Cohesion: 0.50
Nodes (4): Admin Dashboard, Code, TODOs / edge cases, What the synthetic data shows

### Community 133 - "safe_eval"
Cohesion: 0.18
Nodes (11): In / out, RAG Document → Quiz Generator & Grading (quiz ↔ skill gap), TODOs / edge cases, Verification, _computed_ok(), expression_numbers(), Evaluate +,-,*,/,**,%, parentheses and a few math functions. Raises ValueError…, Literal numbers used in an expression (for the 'inputs come from the source'… (+3 more)

### Community 134 - "recommendation_service.py"
Cohesion: 0.08
Nodes (26): Measured uplift → coverage learning + training effectiveness (SCIL v6 §6, B5), _course_summary(), _diagnostic_step(), _fmt_levels(), _interleave_by_level(), _parse_level(), _PrerequisiteGate, Any (+18 more)

### Community 135 - "_build_engine"
Cohesion: 0.31
Nodes (9): _build_engine(), Engine + assembler from one catalogue (sync — run in a thread). Course vectors…, _decode_vec(), _encode_vec(), load_embeddings(), ndarray, {courseId: (text_hash, vector)} for vectors stored under `model`; {} on any…, Upsert (courseId, text_hash, vector) rows; rows already stored with the same… (+1 more)

### Community 136 - "useLearnerDashboard.ts"
Cohesion: 0.11
Nodes (25): `frontend/src/`, Connections, In / out, Learner Dashboard (frontend shell), TODOs / edge cases, ChatWidget(), RightSidebar(), HomeChatWidget() (+17 more)

### Community 137 - "_course_by_id"
Cohesion: 0.40
Nodes (5): _course_by_id(), EnrolPayload, get_course_catalog(), legacy_enroll_user(), O(1) lookup via pre-built _COURSE_INDEX.

### Community 138 - "mock_data_metrics.py"
Cohesion: 0.16
Nodes (16): argparse, collections, io, load_eval(), main(), Benchmark Gyan's intent classifier on the held-out multilingual set. python…, _get(), live_metrics() (+8 more)

### Community 141 - "_OnnxEmbedder"
Cohesion: 0.22
Nodes (4): _OnnxEmbedder, ndarray, A directory written by scripts/download_model.py., sentence-transformers-compatible encoder on onnxruntime + HF `tokenizers`…

### Community 142 - "admin_console.py"
Cohesion: 0.14
Nodes (38): csv, Endpoints (`/api/v1/admin/console`, all take `?department=&grade=&office=`), An admin assigning courses (a training plan) to a department or a list of…, TrainingAssignment, _assignment_out(), AssignmentIn, _behind(), _behind_row() (+30 more)

### Community 143 - "typing"
Cohesion: 0.11
Nodes (19): asyncio, base64, dotenv, functools, json, logging, FILE: ai/rag_engine.py…, scripts/quantize_model.py… (+11 more)

### Community 145 - "CLAUDE.md — index & router"
Cohesion: 0.40
Nodes (5): CLAUDE.md — index & router, Feature index, graphify, How to use these docs, Run commands

### Community 146 - "Authentication & RBAC"
Cohesion: 0.33
Nodes (5): Authentication & RBAC, Connections, In / out, Shared database (Neon), TODOs / edge cases

### Community 148 - "Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)"
Cohesion: 0.50
Nodes (4): Cold start for UNASSESSED competencies, Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8), Foresight, Proficiency belief with dated decay

### Community 149 - "get_embedder"
Cohesion: 0.09
Nodes (32): difflib, Code, _Embedder, encode_cached(), get_embedder(), _load(), model_name(), onnx_model_dir() (+24 more)

### Community 150 - "reranker.py"
Cohesion: 0.20
Nodes (11): TODOs / edge cases, get_reranker(), ndarray, FILE: ai/reranker.py…, Cross-encoder scores for `passages` against `query`, or None if no reranker., Relevance logits, one per (query, passage) pair (higher = better match)., The loaded cross-encoder, or None when disabled / unavailable (logged once)., rerank_scores() (+3 more)

### Community 154 - "Learning Mode — NotebookLM-style study chat (AI Assessment Studio)"
Cohesion: 0.33
Nodes (5): Connections, In / out, Learning Mode — NotebookLM-style study chat (AI Assessment Studio), TODOs / edge cases, Verification

## Knowledge Gaps
- **300 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+295 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1052 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **39 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `UserAuth` connect `UserAuth` to `main-lms-backend/main.py`, `test_certificate_evidence.py`, `router.py`, `record_daily_snapshot`, `diagnostic.py`, `karma.py`, `practice_assessment.py`, `admin_console.py`, `admin_analytics.py`, `rag.py`, `document_extractor.py`, `services/__init__.py`, `get_learning_pathway`, `insights.py`, `career.py`, `_db`, `competency.py`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Why does `Code` connect `Code` to `api.ts`, `_create_schema`, `AwardResult`, `useLearnerDashboard.ts`, `lucide-react`, `karma.py`, `diagnostic.py`, `practice_assessment.py`, `karma_engine.py`, `domain.ts`, `Any`, `.award_safe`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `Code` connect `pipeline.py` to `chatbot.py`, `AssessmentPage.tsx`, `practice_assessment.py`, `probe.py`, `Timeline`, `generate.py`, `gemini_json`, `media_io.py`, `media_quiz.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 78 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `HybridRecommendationEngine` (e.g. with `7. Mismatches between the mermaid diagram and the code` and `Code`) actually correct?**
  _`HybridRecommendationEngine` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 45 inferred relationships involving `Code` (e.g. with `KarmaCard()` and `formatPoints()`) actually correct?**
  _`Code` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _300 weakly-connected nodes found - possible documentation gaps or missing edges._