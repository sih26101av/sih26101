# Graph Report - SIH_IGot  (2026-09-20)

## Corpus Check
- 261 files · ~4,974,119 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 6, .service 2, .example 2)

## Summary
- 3026 nodes · 7478 edges · 155 communities (112 shown, 43 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 845 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fbcc221b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_chat_messages.py
- AssessmentPage.tsx
- _Session
- router.py
- package.json
- _require_auth
- sunbird_ok
- ChatWidget.tsx
- post
- karma_engine.py
- Request
- pipeline.py
- Code
- UserAuth
- typing
- generate.py
- gemini_json
- What You Must Do When Invoked
- 3. Core data flow
- test_pathway.py
- domain.ts
- extractors.py
- media_io.py
- main-lms-backend/main.py
- compilerOptions
- vector_store.py
- 🇮🇳 MoSPI Skill Intelligence Platform
- media_quiz.py
- DiagnosticSessions
- Code
- competency_service.py
- react
- test_proficiency_foresight.py
- ReplyContext
- chatbot.py
- speech.d.ts
- graphify reference: extra exports and benchmark
- resolve_level
- BaseModel
- compilerOptions
- career.py
- graphify reference: query, path, explain
- language_service.py
- providers.py
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
- _roster
- MockIgotAdapter
- LearnerDashboard.tsx
- items.py
- prerequisite_service.py
- generate_mock_data.py
- BaselineAssembler
- ILearningPlatformAdapter
- ai_tools.py
- rag.py
- test_doc_quiz.py
- faker
- services_chat_messages
- services_chat_messages_context
- .__init__
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
- learning_mode.py
- seed.py
- mock-igot-server/main.py
- Code
- Media (Video / Audio / YouTube) → Evidence-Cited Quiz
- admin_console.py
- feedback_service.py
- competency.py
- test_certificate_evidence.py
- CourseCard.tsx
- lifespan
- system_health.py
- reranker.py
- test_reply_regression.py
- proficiency_service.py
- test_chat_endpoint.py
- extract.py
- practice_assessment.py
- Deploy: backend on Oracle Cloud, frontend on Vercel
- .award_safe
- Decisions log (made without the user)
- mock_igot_server.py
- admin_analytics.py
- test_irt.py
- CLAUDE.md — index & router
- test_gap_and_recommendation_upgrades.py
- _warm_up
- google_generativeai
- langchain_text_splitters
- mockdata
- pdfplumber
- document_extractor.py
- pptx
- pypdf
- requests
- Learning Mode — NotebookLM-style study chat (AI Assessment Studio)
- irt_service.py
- urllib_request
- graphify reference: incremental update and cluster-only
- CLAUDE.md
- Shared Embedder (chat + catalog roles)
- calibration.py
- _create_schema
- client
- routers
- chat_actions.py
- HybridRecommendationEngine
- Mock iGOT Karmayogi Integration (Adapter + mock server + mock data)
- engine
- ist_day_start_utc
- update.sh
- services
- youtube-access.sh
- reconstruct_history
- vercel.json
- get
- MonthlyUsage
- Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)
- setup.sh
- services_media_quiz
- services_media_quiz_llm
- services_media_quiz_pipeline
- get_embedder
- Any
- Timeline
- services_media_quiz_question_gen
- services_media_quiz_relevance

## God Nodes (most connected - your core abstractions)
1. `UserAuth` - 101 edges
2. `react` - 55 edges
3. `_Session` - 52 edges
4. `HybridRecommendationEngine` - 47 edges
5. `Code` - 46 edges
6. `MockIgotAdapter` - 39 edges
7. `Code` - 39 edges
8. `lucide-react` - 38 edges
9. `lmsFetch()` - 38 edges
10. `post()` - 38 edges

## Surprising Connections (you probably didn't know these)
- ``frontend/src/`` --references--> `RightSidebar()`  [INFERRED]
  ARCHITECTURE.md → frontend/src/components/dashboard/RightSidebar.tsx
- `Code` --references--> `WhyThisLevel()`  [INFERRED]
  docs/features/skill-gap-analysis.md → frontend/src/components/dashboard/SkillGapCard.tsx
- `Code` --references--> `TabType`  [INFERRED]
  docs/features/chatbot-gyan.md → frontend/src/pages/LearnerDashboard.tsx
- `TODOs / edge cases` --references--> `gradeQuiz()`  [INFERRED]
  docs/features/media-quiz-generator.md → frontend/src/services/api.ts
- `7. Mismatches between the mermaid diagram and the code` --references--> `SkillGapReport`  [INFERRED]
  ARCHITECTURE.md → frontend/src/types/domain.ts

## Import Cycles
- None detected.

## Communities (155 total, 43 thin omitted)

### Community 0 - "test_chat_messages.py"
Cohesion: 0.23
Nodes (11): Loads a language's template table on first use ("or" lives in or_.py; `or` is a…, templates(), _alternatives(), _fields(), parametrize, Catalogue completeness: every language has every template, placeholders are…, test_every_intent_renders(), test_placeholders_match_english() (+3 more)

### Community 1 - "AssessmentPage.tsx"
Cohesion: 0.04
Nodes (80): Gyan hand-off (document → quiz or Learning Mode, no second upload), Frontend, AssessmentPage, ChatEntry, LearningChat(), LearningChatProps, CONTENT_LABEL, MediaAnalysisCard() (+72 more)

### Community 2 - "_Session"
Cohesion: 0.15
Nodes (14): Code, KarmaEventType, ist_now(), KarmaEngine, Dispatches an eventType to its strategy, then applies the shared rules in…, Idempotency key for an event; None means 'not idempotent' (admin only)., DAILY_LOGIN for today, then any streak milestone the current streak has reached., Seeds an empty ledger from iGOT history; afterwards awards any newly completed… (+6 more)

### Community 3 - "router.py"
Cohesion: 0.07
Nodes (46): bcrypt, datetime, Code, jose, get_db(), FastAPI dependency — `db: Session = Depends(get_db)`; closed after the request., change_password(), _clear_refresh_cookie() (+38 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (43): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+35 more)

### Community 5 - "_require_auth"
Cohesion: 0.16
Nodes (18): get_assessment_outcomes(), get_gsbpm_map(), get_hrms_officials(), get_office(), get_offices(), get_prerequisites(), get_supervisor_ratings(), get_user_cbplan() (+10 more)

### Community 6 - "sunbird_ok"
Cohesion: 0.21
Nodes (16): _course_by_id(), get_admin_roster(), get_content_state(), get_course_catalog(), get_user_enrolments(), get_user_profile(), get_user_workplace_evidence(), JSONResponse (+8 more)

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.08
Nodes (50): Code, GyanBot(), GyanHero(), LanguageMenu(), LanguageMenuProps, CAPABILITIES, ChatWidget(), ChatWidgetProps (+42 more)

### Community 8 - "post"
Cohesion: 0.19
Nodes (20): admin_adjust_karma(), AdminAdjustRequest, _assert_self_or_admin(), award_karma_event(), _award_response(), CbpClaimRequest, claim_cbp_bonus(), _enrollments_or_503() (+12 more)

### Community 9 - "karma_engine.py"
Cohesion: 0.11
Nodes (18): AdminAdjustmentStrategy, AwardResult, CompletionKarmaStrategy, FixedPointsStrategy, IKarmaStrategy, KarmaRule, ABC, services/karma_engine.py… (+10 more)

### Community 10 - "Request"
Cohesion: 0.20
Nodes (10): exception_handler, HTTPException, get_competencies(), get_item_bank(), get_job_profiles(), http_exc_handler(), 2PL MCQ item bank (a, b on the FRAC level scale, Bloom level, answer key).…, GET /api/job-profiles — NCO Job Role Catalogue (Sunbird-compliant). Served from… (+2 more)

### Community 11 - "pipeline.py"
Cohesion: 0.07
Nodes (39): csv, Code, main(), FILE: scripts/eval_media_quiz.py…, build_chunks(), slide_windows: [{"t_start", "t_end", "evidence_ids": [ocr/vlm ids of that…, fact_check(), _match() (+31 more)

### Community 12 - "Code"
Cohesion: 0.12
Nodes (33): Connections, Code, assess_competency(), rows_for(), tag_id(), _completed_courses(), _education_score(), enrollment_course_id() (+25 more)

### Community 13 - "UserAuth"
Cohesion: 0.07
Nodes (48): AuthBase, Returns a FastAPI dependency that checks the current user's role. Example:…, require_role(), UserAuth, get_achievements(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments() (+40 more)

### Community 14 - "typing"
Cohesion: 0.07
Nodes (36): argparse, base64, collections, functools, hashlib, json, logging, load_eval() (+28 more)

### Community 15 - "generate.py"
Cohesion: 0.08
Nodes (43): difflib, _call(), _computed_ok(), _density(), difficulty_quotas(), DocChunk, excerpt(), generate() (+35 more)

### Community 16 - "gemini_json"
Cohesion: 0.17
Nodes (20): gemini_json(), gemini_key(), _groq_json(), LLMUnavailable, ollama_vision_json(), parse_json(), Any, RuntimeError (+12 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "3. Core data flow"
Cohesion: 0.12
Nodes (14): 3. Core data flow, _diagnostic_step(), absorb(), add_step(), advance(), open_ladders(), _PrerequisiteGate, Any (+6 more)

### Community 19 - "test_pathway.py"
Cohesion: 0.08
Nodes (23): Opportunity to practise (SCIL v6 §4), StudyPlanSummary(), _edge(), _kinds_levels(), Skill-gap levels + level-aware recommendations + learning pathways. Runs on a…, _resolved(), test_already_met_prerequisite_changes_nothing(), test_completed_never_suggested_and_in_progress_is_continued() (+15 more)

### Community 20 - "domain.ts"
Cohesion: 0.03
Nodes (79): Props, TIER_LABEL, DEFER_REASON, KIND_STYLE, PathwayLadder(), formatDate(), ProfileHeaderProps, TAGLINE (+71 more)

### Community 21 - "extractors.py"
Cohesion: 0.10
Nodes (32): concurrent_futures, add_captions(), flush(), _budget(), caption_regions(), describe_keyframes(), guarded(), run_batch() (+24 more)

### Community 22 - "media_io.py"
Cohesion: 0.05
Nodes (60): BaseException, Getting past the bot check, When the wall is the IP itself, YouTube, _Attempt, _blocked_message(), Caption, _change() (+52 more)

### Community 23 - "main-lms-backend/main.py"
Cohesion: 0.06
Nodes (53): asyncio, Connections, fastapi_middleware_cors, httpx, adapters/igot_adapter.py — iGOT Platform Adapter…, main.py — MoSPI LMS Backend API (Main Orchestrator)…, _ensure_can_view(), get_achievements_by_user_id() (+45 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "vector_store.py"
Cohesion: 0.10
Nodes (26): Code, Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, build_system_prompt(), generate_chat_response(), Runs the full RAG pipeline: 1. Retrieve top-k relevant document chunks from… (+18 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "media_quiz.py"
Cohesion: 0.13
Nodes (24): fastapi_responses, ImportError, importlib_util, capabilities(), _importable(), MediaMetadata, MediaQuizQuestion, MediaQuizResponse (+16 more)

### Community 28 - "DiagnosticSessions"
Cohesion: 0.30
Nodes (5): DiagnosticSessions, public_item(), Any, What the learner sees: no answer key, no parameters., In-memory adaptive sessions (per process). Lost on restart — a session is…

### Community 29 - "Code"
Cohesion: 0.09
Nodes (24): AI Course Recommendation Engine + Learning Pathways, Code, Connections, In / out, TODOs / edge cases, _build_engine(), Engine + assembler from one catalogue (sync — run in a thread). Course vectors…, Reload the catalogue on a timer instead of only at restart. Every… (+16 more)

### Community 30 - "competency_service.py"
Cohesion: 0.24
Nodes (7): CompetencyCalculator, datetime, FILE: main-lms-backend/services/competency_service.py…, Maps FRAC types from the JSON to calculation categories., Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, test_missing_channels_do_not_drag_the_score_to_zero()

### Community 31 - "react"
Cohesion: 0.05
Nodes (59): Visual design system (shared by every page), AdminDashboard, App(), DashboardRedirect(), TokenBridge(), AshokaChakra(), CountUp(), GovEmblem() (+51 more)

### Community 32 - "test_proficiency_foresight.py"
Cohesion: 0.12
Nodes (24): cluster_of(), cohort_prior(), office_phase(), population_stats(), Any, Cohort prior for an UNASSESSED competency, with the divergence check., The GSBPM phase the office spends most officer-hours in ('4' Collect, 'OA'…, comp → (μ_pop, σ_pop, n) over officials with assessed evidence on it. (+16 more)

### Community 33 - "ReplyContext"
Cohesion: 0.16
Nodes (19): importlib, Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile(), Any, Everything a reply template may personalise, built once per chat request., ReplyContext, _by_page(), _gap_lines() (+11 more)

### Community 34 - "chatbot.py"
Cohesion: 0.25
Nodes (19): low_confidence_threshold(), chat(), ChatResponse, detect_intent_keyword(), _intent_response(), _intercept(), FILE: routers/chatbot.py Multilingual AI Learning Assistant — Gyan (ज्ञान)…, Deterministic handling of English commands the classifier has historically… (+11 more)

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

### Community 40 - "career.py"
Cohesion: 0.19
Nodes (18): career_readiness(), _dispute_view(), DisputeBody, _ensure_can_view(), my_disputes(), office_ladder(), open_dispute(), Any (+10 more)

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 42 - "language_service.py"
Cohesion: 0.18
Nodes (13): classify_intent(), Returns (best_intent, confidence). ("general", 0.0) if the embedder is…, detect_chat_language(), detect_chat_variant(), detect_chat_variant_or_none(), _devanagari_language(), Small, offline language routing for Gyan chat. This deliberately does *not* use…, Supported ISO 639-1 code for a chat message. (+5 more)

### Community 43 - "providers.py"
Cohesion: 0.11
Nodes (17): dataclasses, Exception, _family(), GroqProvider, _Key, parse_json_object(), ProviderError, Response (+9 more)

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
Cohesion: 0.17
Nodes (20): 7. Mismatches between the mermaid diagram and the code, Base, TODOs / edge cases, enum, Admin, AssessmentSkillMapping, BaseUser, Course (+12 more)

### Community 58 - "opportunity"
Cohesion: 0.18
Nodes (16): In / out, Skill Gap Analysis (evidence-based competency baselines), TODOs / edge cases, opportunity(), Any, services/gsbpm_service.py — GSBPM scoping (SCIL v6 §1) + opportunity to…, Opportunity to practise a competency in the official's office this cycle (SCIL…, Which competencies are in scope under the officer-hours rule, and why. (+8 more)

### Community 60 - "test_admin_analytics.py"
Cohesion: 0.20
Nodes (15): emerging_skills(), datetime, Per FRAC competency, over the (filtered) officials in the workforce snapshot: *…, Admin console aggregates (services/admin_analytics.py): filters, pagination,…, _snap_row(), test_department_compliance_suppresses_small_departments(), test_emerging_skills_forecasts_shortfall_from_retirement_and_ranks_by_priority(), test_emerging_skills_recommends_commissioning_missing_catalogue_levels() (+7 more)

### Community 61 - "estimate_uplift"
Cohesion: 0.17
Nodes (19): estimate_uplift(), _features(), _ipw(), Any, ndarray, services/uplift_service.py — measured course uplift (SCIL v6 §6 coverage…, [1, z, z², tenure/10, statistics degree] with z = preθ − (level − 0.5): takers…, Newton–Raphson for an L2-penalised logistic regression (intercept unpenalised). (+11 more)

### Community 62 - "_roster"
Cohesion: 0.16
Nodes (28): Endpoints (`/api/v1/admin/console`, all take `?department=&grade=&office=`), _behind(), _behind_row(), _csv(), _emerging(), emerging_skills(), export_csv(), filter_options() (+20 more)

### Community 63 - "MockIgotAdapter"
Cohesion: 0.10
Nodes (18): Cross-competency prerequisite DAG (SCIL v6 §5, B4), GSBPM scope — the 80% officer-hours rule (SCIL v6 §1), Reference data loading, TODOs / limits, Used by the admin console, Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight), MockIgotAdapter, Forget every cached read for this user. (+10 more)

### Community 64 - "LearnerDashboard.tsx"
Cohesion: 0.04
Nodes (72): `frontend/src/`, Code, Connections, In / out, Learner Dashboard (frontend shell), Responsive layout (phones 360–430px, tablets 768–1024px), TODOs / edge cases, LearnerDashboard (+64 more)

### Community 65 - "items.py"
Cohesion: 0.20
Nodes (30): ast, Document question pipeline (`main-lms-backend/services/doc_quiz/`), TODOs / edge cases, _build_review(), Type-aware answer review, missed questions first. Each wrong answer gets…, accepted_texts(), answer_display(), _choice_set() (+22 more)

### Community 66 - "prerequisite_service.py"
Cohesion: 0.14
Nodes (24): find_cycle(), infer_edges(), _node(), _norm_sf(), _ols(), Any, ndarray, services/prerequisite_service.py — cross-competency prerequisite DAG (SCIL v6… (+16 more)

### Community 67 - "generate_mock_data.py"
Cohesion: 0.07
Nodes (58): _batch(), build_acbp(), build_catalog(), build_crosswalk(), build_enrollments(), build_frac(), build_gsbpm_map(), build_hrms() (+50 more)

### Community 68 - "BaselineAssembler"
Cohesion: 0.15
Nodes (15): BaselineAssembler, _normalise_course_map(), Accept {courseId: {compId: level}} or the legacy {courseId: [compId]}., test_verified_cert_lifts_confidence_over_documented(), The old `requiredLevel - 1` cap made every evidence-backed gap permanent., test_completion_evidence_follows_the_crosswalk(), test_evidence_can_close_a_gap(), _one() (+7 more)

### Community 69 - "ILearningPlatformAdapter"
Cohesion: 0.11
Nodes (14): 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator, ILearningPlatformAdapter (+6 more)

### Community 70 - "ai_tools.py"
Cohesion: 0.17
Nodes (14): is_ollama_available(), Fast, synchronous check — just hits the Ollama /api/tags endpoint. Returns True…, ai_health_check(), HealthResponse, BaseModel, get, UploadFile, FILE: routers/ai_tools.py… (+6 more)

### Community 71 - "rag.py"
Cohesion: 0.07
Nodes (51): Code, Code, Connections, In / out, LLM providers (Groq multi-key → Gemini), Personalised feedback (`items.feedback`), RAG Document → Quiz Generator & Grading (quiz ↔ skill gap), Verification (+43 more)

### Community 72 - "test_doc_quiz.py"
Cohesion: 0.10
Nodes (21): io, Document quiz: extraction (DOCX, OCR), cited multi-type generation, grading…, Evaluate +,-,*,/,**,%, parentheses and a few math functions. Raises ValueError…, safe_eval(), ev(), _chunks(), _mcq(), parametrize (+13 more)

### Community 76 - ".__init__"
Cohesion: 0.14
Nodes (10): _CourseDoc, _parse_level(), ndarray, Bayesian shrinkage toward global prior mean. Returns None if either input is…, Level 3' / 3 / '3' → 3; anything outside 1..5 → None., `catalog` / `frac` / `crosswalk` are the lists served by the mock iGOT server…, Stored vectors whose text hash still matches; encode (disk-memoised) the rest., [(courseId, text_hash, vector)] — what catalogue_store persists. (+2 more)

### Community 77 - "AdminDashboard.tsx"
Cohesion: 0.08
Nodes (59): Frontend, AdminActions(), AssignForm(), when(), AdminFilterBar(), ExportButton(), facetLabels(), describeFilters() (+51 more)

### Community 87 - "api.ts"
Cohesion: 0.03
Nodes (80): CertificateReviewQueue(), Row(), STATUS_CLS, TABS, when(), AGENDA_TYPE, CapabilityRiskPanel(), ForesightPanel() (+72 more)

### Community 88 - "learning_mode.py"
Cohesion: 0.20
Nodes (18): ErrorResponse, _generate_overview(), learning_chat(), LearningChatMessage, LearningChatRequest, LearningChatResponse, LearningCitation, LearningMetadata (+10 more)

### Community 89 - "seed.py"
Cohesion: 0.17
Nodes (14): dotenv, FILE: ai/rag_engine.py…, hash_password(), Return a bcrypt hash of the plain-text password., _derive_password(), _fetch_officials(), main(), auth/seed.py… (+6 more)

### Community 90 - "mock-igot-server/main.py"
Cohesion: 0.13
Nodes (21): contextlib, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history(), health() (+13 more)

### Community 91 - "Code"
Cohesion: 0.15
Nodes (14): AsyncClient, Code, _competencies(), fetch(), fetch(), fetch(), _prof_detail(), Pooled client for the running loop — no new TCP connection per call. (+6 more)

### Community 92 - "Media (Video / Audio / YouTube) → Evidence-Cited Quiz"
Cohesion: 0.29
Nodes (6): In / out, Media (Video / Audio / YouTube) → Evidence-Cited Quiz, Pipeline, Setup, TODOs / edge cases, Verification

### Community 93 - "admin_console.py"
Cohesion: 0.10
Nodes (36): fastapi_concurrency, AdminDailySnapshot, One row per calendar day (UTC): the workforce headline numbers plus the same…, An admin assigning courses (a training plan) to a department or a list of…, A reminder sent by an admin to an official behind on mandatory (ACBP) training., TrainingAssignment, TrainingNudge, _assignment_out() (+28 more)

### Community 94 - "feedback_service.py"
Cohesion: 0.26
Nodes (11): One learner interaction with a recommended course. `event` ∈ impression | click…, RecommendationFeedback, Any, services/feedback_service.py — recommendation feedback (clicks, enrolments,…, {courseId: "up" | "down"} — the latest vote event per course., Per-course counts of each event + click-through by rank (admin view)., record(), summary() (+3 more)

### Community 95 - "competency.py"
Cohesion: 0.10
Nodes (35): CertificateSubmission, Competency, EvidenceLog, LevelDispute, One uploaded certificate (routers/competency.py). On upload each extracted…, status: OPEN (test started) → CONFIRMED | RAISED | LOWER_THAN_SHOWN once the…, CertificateReview, certificates_for_review() (+27 more)

### Community 96 - "test_certificate_evidence.py"
Cohesion: 0.08
Nodes (31): Connections, fastapi, fastapi_security, fastapi_testclient, auth/database.py…, get_current_user(), auth/dependencies.py…, Decodes the Bearer JWT, looks up the user in auth.db. Raises HTTP 401 for any… (+23 more)

### Community 97 - "CourseCard.tsx"
Cohesion: 0.18
Nodes (13): BADGE_STYLE, CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps, MODALITY_LABEL, SOURCE_STYLES, matches() (+5 more)

### Community 98 - "lifespan"
Cohesion: 0.33
Nodes (7): lifespan(), _load_json(), _load_json_from_dir(), Any, FastAPI, Load all datasets into memory once at startup, so no request touches the file…, Load a JSON file from ROOT_DIR. Raises RuntimeError on missing file.

### Community 99 - "system_health.py"
Cohesion: 0.23
Nodes (20): is_semantic_engine_ready(), chat_mode(), get, Which response engine is active; the frontend shows it as a badge., configured_providers(), groq_keys(), Groq providers built from env, in GROQ_MODELS order. Cached so cooldowns…, basic() (+12 more)

### Community 100 - "reranker.py"
Cohesion: 0.22
Nodes (10): get_reranker(), ndarray, FILE: ai/reranker.py…, Cross-encoder scores for `passages` against `query`, or None if no reranker., Relevance logits, one per (query, passage) pair (higher = better match)., The loaded cross-encoder, or None when disabled / unavailable (logged once)., rerank_scores(), _Reranker (+2 more)

### Community 101 - "test_reply_regression.py"
Cohesion: 0.30
Nodes (10): ChatHistoryItem, ChatRequest, BaseModel, RecommendationContext, SkillGapContext, sample_request(), parametrize, English and Hinglish replies must match the pre-catalogue output, except… (+2 more)

### Community 102 - "proficiency_service.py"
Cohesion: 0.15
Nodes (25): decay(), expected_shortfall(), months_between(), _phi(), _Phi(), proficiency_state(), datetime, services/proficiency_service.py — probabilistic proficiency state (SCIL v6 §2)… (+17 more)

### Community 103 - "test_chat_endpoint.py"
Cohesion: 0.44
Nodes (9): _chat(), parametrize, End-to-end /chat behaviour per language through the real multilingual…, test_dark_mode_action(), test_my_courses_navigation(), test_questions_answer_in_chat_without_navigating(), test_recommendations(), test_sidebar_section_navigation() (+1 more)

### Community 104 - "extract.py"
Cohesion: 0.16
Nodes (17): extract_docx(), _ocr_engine(), ocr_pdf_pages(), OcrUnavailable, ndarray, RuntimeError, FILE: services/doc_quiz/extract.py…, (text in reading order, mean confidence, weak lines dropped). (+9 more)

### Community 105 - "practice_assessment.py"
Cohesion: 0.09
Nodes (40): Practice ability (`main-lms-backend/services/practice_assessment.py`), _competency_rows(), grade_quiz(), Any, _question_difficulties(), The learner's resolved role competencies (same rows the skill-gap view shows),…, **Grade Quiz → Skill Gap** - user_id comes from the JWT…, Per-question difficulty for grading, calibrated from response data… (+32 more)

### Community 106 - "Deploy: backend on Oracle Cloud, frontend on Vercel"
Cohesion: 0.22
Nodes (8): 1. Create the VM (Oracle Cloud console), 2. Pick the API hostname, 3. Set up the VM, 4. Frontend on Vercel, Deploy: backend on Oracle Cloud, frontend on Vercel, Troubleshooting, Updating: just `git push` to `main`, YouTube links on the VM

### Community 107 - ".award_safe"
Cohesion: 0.25
Nodes (6): Connections, In / out, Karma Points (gamification), Rules (`RULES` in `karma_engine.py`, served by `GET /karma/rules`), TODOs / edge cases, For server-side hooks (quiz grading, diagnostics): own session, never raises.

### Community 108 - "Decisions log (made without the user)"
Cohesion: 0.18
Nodes (8): Before / after metrics, Could not do / blocked, Decisions log (made without the user), Noticed but out of scope (not fixed), SCIL v6 — mock data + blocked features: progress report, Status, Catalogue duration in hours, or None for a course not in the catalogue., Median cosine between the competency query and the courses NOT tagged with it —…

### Community 109 - "mock_igot_server.py"
Cohesion: 0.19
Nodes (15): composite_search(), CompositeSearchRequest, _course_tags(), _enriched_view(), EnrolPayload, get_enriched_courses(), legacy_enroll_user(), legacy_push_score() (+7 more)

### Community 110 - "admin_analytics.py"
Cohesion: 0.14
Nodes (26): Backend, _competency_metrics(), daily_metrics(), by(), dept_compliance(), facets(), Filters, heatmap() (+18 more)

### Community 111 - "test_irt.py"
Cohesion: 0.24
Nodes (13): laplace_posterior(), (mode, sd) of N(prior) × Π 2PL likelihoods, Laplace approximation. responses =…, _bank(), _grid_posterior(), Tier-1 2PL posterior + adaptive diagnostic (SCIL v6 §2). pytest…, _run(), test_answering_the_wrong_item_or_after_the_end_is_rejected(), test_correct_answers_move_the_estimate_up_wrong_ones_down() (+5 more)

### Community 112 - "CLAUDE.md — index & router"
Cohesion: 0.33
Nodes (6): CLAUDE.md — index & router, Conventions, Feature index, graphify, How to use these docs, Run commands

### Community 113 - "test_gap_and_recommendation_upgrades.py"
Cohesion: 0.12
Nodes (23): calculate_baseline(), EvidencePayload, BaseModel, Stateless calculator for one competency, on exactly the scoring path the…, correct_supervisor_rating(), rater_leniency_offsets(), (corrected rating on 1..5, offset applied). Unknown rater → unchanged., [{raterId, grantedValue}] → {raterId: {offset, n, mean, grandMean}} (shrunk… (+15 more)

### Community 114 - "_warm_up"
Cohesion: 0.09
Nodes (22): AbstractEventLoop, 1. Runtime topology, Connections, Gyan — Multilingual Chat Assistant, In / out, TODOs / edge cases, Measured uplift → coverage learning + training effectiveness (SCIL v6 §6, B5), Workforce snapshot (+14 more)

### Community 119 - "document_extractor.py"
Cohesion: 0.06
Nodes (55): Code, CertificateExtractionResult, _clamp_level(), DocumentExtractorService, ExtractedCompetency, ExtractionError, frac_by_id(), frac_dictionary() (+47 more)

### Community 123 - "Learning Mode — NotebookLM-style study chat (AI Assessment Studio)"
Cohesion: 0.33
Nodes (5): Connections, In / out, Learning Mode — NotebookLM-style study chat (AI Assessment Studio), TODOs / edge cases, Verification

### Community 124 - "irt_service.py"
Cohesion: 0.53
Nodes (5): fisher_information(), next_item(), p_correct(), services/irt_service.py — Tier-1 Bayesian 2PL posterior + adaptive diagnostic…, test_next_item_maximises_fisher_information()

### Community 126 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.29
Nodes (6): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only, data(), files(), fixture

### Community 127 - "CLAUDE.md"
Cohesion: 0.24
Nodes (6): Authentication & RBAC, In / out, Shared database (Neon), Certificate / Resume Evidence Extraction, In / out, TODOs / edge cases

### Community 128 - "Shared Embedder (chat + catalog roles)"
Cohesion: 0.40
Nodes (4): Connections, In / out, Shared Embedder (chat + catalog roles), TODOs / edge cases

### Community 129 - "calibration.py"
Cohesion: 0.19
Nodes (15): Difficulty calibration (`services/doc_quiz/calibration.py`), QuizItemStat, Response data per quiz item (services/doc_quiz/calibration.py). itemKey is a…, calibrate(), calibrate_items(), difficulty_from_b(), load_stats(), Any (+7 more)

### Community 130 - "_create_schema"
Cohesion: 0.50
Nodes (5): _create_schema(), _create(), Create users_auth and the karma/evidence tables if missing (idempotent)., migrate_karma_schema(), Idempotent upgrade for databases created before the daily-cap rework: adds…

### Community 131 - "client"
Cohesion: 0.50
Nodes (4): client(), roster(), fixture, _u()

### Community 133 - "chat_actions.py"
Cohesion: 0.50
Nodes (4): detect_ui_actions(), _mentions(), Detect website theme / language changes requested in any supported chat…, Returns (theme, language): theme in {"dark", "light", "toggle"}, language in…

### Community 134 - "HybridRecommendationEngine"
Cohesion: 0.12
Nodes (21): _course_summary(), _fmt_levels(), GapEntry, HybridRecommendationEngine, _interleave_by_level(), BaseModel, Returns deduplicated, level-gated recommendations in gap-priority order. Only…, Step-by-step path for one competency: one course per FRAC level from current+1… (+13 more)

### Community 135 - "Mock iGOT Karmayogi Integration (Adapter + mock server + mock data)"
Cohesion: 0.50
Nodes (4): Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server + mock data), TODOs / edge cases

### Community 136 - "engine"
Cohesion: 0.20
Nodes (13): on_event, Create users_auth table if it doesn't exist yet., _startup(), test_stored_embeddings_are_reused_only_when_text_matches(), _course(), engine(), _frac(), fixture (+5 more)

### Community 137 - "ist_day_start_utc"
Cohesion: 0.67
Nodes (4): ist_date(), ist_day_start_utc(), date, datetime

### Community 141 - "reconstruct_history"
Cohesion: 0.20
Nodes (8): Admin Dashboard, Code, How the parts work, TODOs / edge cases, What the synthetic data shows, date, Daily training-rate history rebuilt from dated iGOT course completions, for…, reconstruct_history()

### Community 143 - "get"
Cohesion: 0.14
Nodes (14): get_crosswalk(), get_org_roles(), health(), legacy_catalog(), legacy_frac(), legacy_job_profiles(), legacy_user_history(), get (+6 more)

### Community 145 - "Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)"
Cohesion: 0.50
Nodes (4): Cold start for UNASSESSED competencies, Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8), Foresight, Proficiency belief with dated decay

### Community 150 - "get_embedder"
Cohesion: 0.07
Nodes (37): Code, _Embedder, encode_cached(), get_embedder(), is_embedder_ready(), _load(), model_name(), onnx_model_dir() (+29 more)

### Community 155 - "Any"
Cohesion: 0.13
Nodes (12): fetch(), Any, The full CBP course catalogue, paged through POST /api/composite/v1/search.…, POST /api/composite/v1/search — Sunbird composite search, every page. `filters`…, GET /api/frac/competencies — the catalogue FRAC set incl. L1–L5 descriptors., GET /api/frac/v1/crosswalk — iGOT dictionary CID id → catalogue FRAC id., GET /api/course/v1/user/enrollment/list/{user_id} Returns: result.courses —…, GET /api/admin/v1/users Returns: result.users — full list of officials. (+4 more)

### Community 157 - "Timeline"
Cohesion: 0.12
Nodes (19): Performance, Chunk, Evidence, fmt_ts(), _make_chunk(), FILE: services/media_quiz/evidence.py…, Append another timeline's records, renumbered after this one's, plus its drop…, _tag() (+11 more)

## Knowledge Gaps
- **309 isolated node(s):** `setup.sh script`, `name`, `private`, `version`, `type` (+304 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1091 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **43 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Code` connect `pipeline.py` to `AssessmentPage.tsx`, `chatbot.py`, `practice_assessment.py`, `gemini_json`, `media_io.py`, `document_extractor.py`, `get_embedder`, `Media (Video / Audio / YouTube) → Evidence-Cited Quiz`, `Timeline`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `UserAuth` connect `UserAuth` to `test_certificate_evidence.py`, `router.py`, `client`, `rag.py`, `career.py`, `post`, `practice_assessment.py`, `document_extractor.py`, `main-lms-backend/main.py`, `seed.py`, `admin_console.py`, `_roster`, `competency.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `Code` connect `router.py` to `engine`, `UserAuth`, `AdminDashboard.tsx`, `seed.py`, `CLAUDE.md`, `react`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 78 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `HybridRecommendationEngine` (e.g. with `7. Mismatches between the mermaid diagram and the code` and `Code`) actually correct?**
  _`HybridRecommendationEngine` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `setup.sh script`, `name`, `private` to the rest of the system?**
  _309 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `AssessmentPage.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.04491161012900143 - nodes in this community are weakly interconnected._