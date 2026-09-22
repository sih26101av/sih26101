# Graph Report - SIH_IGot  (2026-09-20)

## Corpus Check
- 261 files · ~4,974,119 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 6, .service 2, .example 2)

## Summary
- 3000 nodes · 7383 edges · 157 communities (114 shown, 43 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 836 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fbcc221b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_chat_messages.py
- AssessmentPage.tsx
- Code
- router.py
- package.json
- _require_auth
- sunbird_ok
- ChatWidget.tsx
- karma.py
- lucide-react
- Request
- pipeline.py
- Code
- UserAuth
- os
- generate.py
- gemini_json
- What You Must Do When Invoked
- Any
- test_pathway.py
- domain.ts
- media_io.py
- download_youtube
- main-lms-backend/main.py
- compilerOptions
- ai_tools.py
- 🇮🇳 MoSPI Skill Intelligence Platform
- media_quiz.py
- irt_service.py
- catalogue_store.py
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
- proficiency_service.py
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
- LearnerDashboard.tsx
- items.py
- prerequisite_service.py
- generate_mock_data.py
- generate
- Any
- capabilities
- rag.py
- test_doc_quiz.py
- faker
- services_chat_messages
- services_chat_messages_context
- validate
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
- .fetch_user_cbplan
- Media (Video / Audio / YouTube) → Evidence-Cited Quiz
- TrainingNudge
- services/__init__.py
- competency.py
- test_certificate_evidence.py
- CourseCard.tsx
- lifespan
- system_health.py
- LearningChat.tsx
- test_reply_regression.py
- workforce_service.py
- mock_data_metrics.py
- typing
- practice_assessment.py
- _db
- youtube_diagnosis
- .__init__
- mock_igot_server.py
- admin_analytics.py
- test_irt.py
- build_outcomes
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
- _Collect
- MockIgotAdapter
- urllib_request
- graphify reference: incremental update and cluster-only
- CLAUDE.md
- Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)
- calibration.py
- ndarray
- Admin Dashboard
- routers
- safe_eval
- HybridRecommendationEngine
- ValueError
- _StubEmbedder
- Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)
- When the wall is the IP itself
- services
- AI Course Recommendation Engine + Learning Pathways
- reconstruct_history
- has_cookies
- get
- Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)
- BaseModel
- get
- Code
- semantic_engine.py
- get_embedder
- JSONResponse
- on_event
- UploadFile
- _sunbird_result
- Timeline
- services_media_quiz_question_gen
- services_media_quiz_relevance

## God Nodes (most connected - your core abstractions)
1. `UserAuth` - 101 edges
2. `react` - 55 edges
3. `HybridRecommendationEngine` - 47 edges
4. `Code` - 46 edges
5. `MockIgotAdapter` - 39 edges
6. `Code` - 39 edges
7. `lmsFetch()` - 38 edges
8. `lucide-react` - 38 edges
9. `Code` - 38 edges
10. `post()` - 36 edges

## Surprising Connections (you probably didn't know these)
- `TODOs / edge cases` --references--> `gradeQuiz()`  [INFERRED]
  docs/features/media-quiz-generator.md → frontend/src/services/api.ts
- `Code` --references--> `KarmaLevel`  [INFERRED]
  docs/features/karma-points.md → frontend/src/types/domain.ts
- `Code` --references--> `KarmaToday`  [INFERRED]
  docs/features/karma-points.md → frontend/src/types/domain.ts
- `7. Mismatches between the mermaid diagram and the code` --references--> `SkillGapReport`  [INFERRED]
  ARCHITECTURE.md → frontend/src/types/domain.ts
- `TODOs / edge cases` --references--> `EvidenceLog`  [INFERRED]
  docs/features/karma-points.md → main-lms-backend/models/models.py

## Import Cycles
- None detected.

## Communities (157 total, 43 thin omitted)

### Community 0 - "test_chat_messages.py"
Cohesion: 0.23
Nodes (11): Loads a language's template table on first use ("or" lives in or_.py; `or` is a…, templates(), _alternatives(), _fields(), parametrize, Catalogue completeness: every language has every template, placeholders are…, test_every_intent_renders(), test_placeholders_match_english() (+3 more)

### Community 1 - "AssessmentPage.tsx"
Cohesion: 0.05
Nodes (67): Gyan hand-off (document → quiz or Learning Mode, no second upload), Frontend, AssessmentPage, CONTENT_LABEL, MediaAnalysisCard(), MediaAnswerReview(), pct(), QuestionEvidence() (+59 more)

### Community 2 - "Code"
Cohesion: 0.05
Nodes (52): Code, Connections, In / out, Karma Points (gamification), Rules (`RULES` in `karma_engine.py`, served by `GET /karma/rules`), TODOs / edge cases, _create_schema(), _create() (+44 more)

### Community 3 - "router.py"
Cohesion: 0.08
Nodes (43): bcrypt, datetime, Code, hashlib, jose, get_db(), FastAPI dependency — `db: Session = Depends(get_db)`; closed after the request., change_password() (+35 more)

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

### Community 8 - "karma.py"
Cohesion: 0.20
Nodes (21): admin_adjust_karma(), AdminAdjustRequest, _assert_self_or_admin(), award_karma_event(), _award_response(), CbpClaimRequest, claim_cbp_bonus(), _enrollments_or_503() (+13 more)

### Community 9 - "lucide-react"
Cohesion: 0.10
Nodes (26): KarmaCard(), PassbookRow(), PILL_ORDER, RightSidebar(), RightSidebarProps, EVENT_META, formatPoints(), KarmaEventMeta (+18 more)

### Community 10 - "Request"
Cohesion: 0.20
Nodes (10): exception_handler, HTTPException, get_competencies(), get_item_bank(), get_job_profiles(), http_exc_handler(), 2PL MCQ item bank (a, b on the FRAC level scale, Bloom level, answer key).…, GET /api/job-profiles — NCO Job Role Catalogue (Sunbird-compliant). Served from… (+2 more)

### Community 11 - "pipeline.py"
Cohesion: 0.08
Nodes (33): Code, main(), FILE: scripts/eval_media_quiz.py…, caption_regions(), fact_check(), _match(), protect_terms(), FILE: services/media_quiz/fact_check.py… (+25 more)

### Community 12 - "Code"
Cohesion: 0.13
Nodes (27): Connections, Code, get_recommendations_by_user_id(), Level-gated hybrid recommendations: Stage 0 — gap prioritisation (priority_k =…, rows_for(), tag_id(), _completed_courses(), _education_score() (+19 more)

### Community 13 - "UserAuth"
Cohesion: 0.07
Nodes (49): AuthBase, UserAuth, get_me(), get, Return the current authenticated user's profile. Used by the frontend to re-…, get_achievements(), get_achievements_by_user_id(), get_admin_roster() (+41 more)

### Community 14 - "os"
Cohesion: 0.12
Nodes (16): argparse, asyncio, dataclasses, io, json, logging, FILE: ai/rag_engine.py…, Benchmark Gyan's intent classifier on the held-out multilingual set. python… (+8 more)

### Community 15 - "generate.py"
Cohesion: 0.13
Nodes (28): Connections, _call(), _density(), difficulty_quotas(), DocChunk, generate(), _index(), _label() (+20 more)

### Community 16 - "gemini_json"
Cohesion: 0.07
Nodes (42): LLM providers (Groq multi-key → Gemini), Exception, gemini_json(), gemini_key(), _groq_json(), llm_configured(), LLMUnavailable, ollama_vision_json() (+34 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "Any"
Cohesion: 0.11
Nodes (15): _diagnostic_step(), absorb(), add_step(), advance(), open_ladders(), _parse_level(), _PrerequisiteGate, Any (+7 more)

### Community 19 - "test_pathway.py"
Cohesion: 0.07
Nodes (27): BaselineAssembler, _normalise_course_map(), Accept {courseId: {compId: level}} or the legacy {courseId: [compId]}., test_verified_cert_lifts_confidence_over_documented(), _edge(), _kinds_levels(), Skill-gap levels + level-aware recommendations + learning pathways. Runs on a…, The old `requiredLevel - 1` cap made every evidence-backed gap permanent. (+19 more)

### Community 20 - "domain.ts"
Cohesion: 0.04
Nodes (53): Props, TIER_LABEL, DEFER_REASON, KIND_STYLE, PathwayLadder(), COLORS, Props, MyCoursesViewProps (+45 more)

### Community 21 - "media_io.py"
Cohesion: 0.07
Nodes (47): concurrent_futures, add_captions(), flush(), _budget(), describe_keyframes(), guarded(), run_batch(), get_whisper() (+39 more)

### Community 22 - "download_youtube"
Cohesion: 0.20
Nodes (16): BaseException, download_youtube(), fetch(), _is_blocked(), _is_fatal(), _is_gated(), MediaInputError, _probe_clients() (+8 more)

### Community 23 - "main-lms-backend/main.py"
Cohesion: 0.06
Nodes (51): fastapi, fastapi_middleware_cors, fastapi_security, httpx, adapters/igot_adapter.py — iGOT Platform Adapter…, get_current_user(), Session, auth/dependencies.py… (+43 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "ai_tools.py"
Cohesion: 0.07
Nodes (38): Code, Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, build_system_prompt(), generate_chat_response(), is_ollama_available() (+30 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "media_quiz.py"
Cohesion: 0.14
Nodes (22): BaseModel, fastapi_responses, ImportError, importlib_util, MediaMetadata, MediaQuizQuestion, MediaQuizResponse, _missing_dep_message() (+14 more)

### Community 28 - "irt_service.py"
Cohesion: 0.22
Nodes (10): DiagnosticSessions, fisher_information(), next_item(), p_correct(), public_item(), Any, services/irt_service.py — Tier-1 Bayesian 2PL posterior + adaptive diagnostic…, What the learner sees: no answer key, no parameters. (+2 more)

### Community 29 - "catalogue_store.py"
Cohesion: 0.17
Nodes (17): base64, _build_engine(), Engine + assembler from one catalogue (sync — run in a thread). Course vectors…, Reload the catalogue on a timer instead of only at restart. Every…, _refresh_catalogue_loop(), Course, catalogue_fingerprint(), _decode_vec() (+9 more)

### Community 30 - "competency_service.py"
Cohesion: 0.24
Nodes (7): CompetencyCalculator, datetime, FILE: main-lms-backend/services/competency_service.py…, Maps FRAC types from the JSON to calculation categories., Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, test_missing_channels_do_not_drag_the_score_to_zero()

### Community 31 - "react"
Cohesion: 0.05
Nodes (59): Visual design system (shared by every page), App(), DashboardRedirect(), TokenBridge(), AshokaChakra(), CountUp(), GovEmblem(), Reveal() (+51 more)

### Community 32 - "test_proficiency_foresight.py"
Cohesion: 0.16
Nodes (19): iGOT profile competencyLevel ('Level 3') → 3; missing → 0 (no claim)., Profile + enrollments + EvidenceLog → one resolved row per role competency.…, _resolve_competency_state(), _self_reported_level(), cohort_prior(), population_stats(), Cohort prior for an UNASSESSED competency, with the divergence check., comp → (μ_pop, σ_pop, n) over officials with assessed evidence on it. (+11 more)

### Community 33 - "ReplyContext"
Cohesion: 0.16
Nodes (19): importlib, Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile(), Any, Everything a reply template may personalise, built once per chat request., ReplyContext, _by_page(), _gap_lines() (+11 more)

### Community 34 - "chatbot.py"
Cohesion: 0.18
Nodes (24): low_confidence_threshold(), chat(), ChatRequest, ChatResponse, detect_intent_keyword(), _intent_response(), _intercept(), FILE: routers/chatbot.py Multilingual AI Learning Assistant — Gyan (ज्ञान)… (+16 more)

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
Cohesion: 0.18
Nodes (19): career_readiness(), _dispute_view(), DisputeBody, _ensure_can_view(), my_disputes(), office_ladder(), open_dispute(), Any (+11 more)

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 42 - "language_service.py"
Cohesion: 0.18
Nodes (13): load_eval(), main(), detect_chat_language(), detect_chat_variant(), detect_chat_variant_or_none(), _devanagari_language(), Small, offline language routing for Gyan chat. This deliberately does *not* use…, Supported ISO 639-1 code for a chat message. (+5 more)

### Community 43 - "proficiency_service.py"
Cohesion: 0.14
Nodes (20): cluster_of(), decay(), expected_shortfall(), months_between(), office_phase(), _phi(), _Phi(), proficiency_state() (+12 more)

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
Cohesion: 0.12
Nodes (25): 7. Mismatches between the mermaid diagram and the code, Base, Authentication & RBAC, Connections, In / out, Shared database (Neon), TODOs / edge cases, enum (+17 more)

### Community 58 - "opportunity"
Cohesion: 0.18
Nodes (16): Opportunity to practise (SCIL v6 §4), StudyPlanSummary(), opportunity(), Any, services/gsbpm_service.py — GSBPM scoping (SCIL v6 §1) + opportunity to…, Opportunity to practise a competency in the official's office this cycle (SCIL…, Which competencies are in scope under the officer-hours rule, and why., scope_report() (+8 more)

### Community 60 - "test_admin_analytics.py"
Cohesion: 0.20
Nodes (15): emerging_skills(), datetime, Per FRAC competency, over the (filtered) officials in the workforce snapshot: *…, Admin console aggregates (services/admin_analytics.py): filters, pagination,…, _snap_row(), test_department_compliance_suppresses_small_departments(), test_emerging_skills_forecasts_shortfall_from_retirement_and_ranks_by_priority(), test_emerging_skills_recommends_commissioning_missing_catalogue_levels() (+7 more)

### Community 61 - "estimate_uplift"
Cohesion: 0.17
Nodes (19): estimate_uplift(), _features(), _ipw(), Any, ndarray, services/uplift_service.py — measured course uplift (SCIL v6 §6 coverage…, [1, z, z², tenure/10, statistics degree] with z = preθ − (level − 0.5): takers…, Newton–Raphson for an L2-penalised logistic regression (intercept unpenalised). (+11 more)

### Community 62 - "admin_console.py"
Cohesion: 0.16
Nodes (34): csv, fastapi_concurrency, An admin assigning courses (a training plan) to a department or a list of…, TrainingAssignment, _assignment_out(), AssignmentIn, _behind(), _behind_row() (+26 more)

### Community 63 - "Code"
Cohesion: 0.13
Nodes (13): Code, Cross-competency prerequisite DAG (SCIL v6 §5, B4), _competencies(), _prof_detail(), GET a Sunbird endpoint and return its `result` object., GET /api/frac/v1/prerequisites — {count, edges[]} expert-seeded prerequisite…, GET /api/course/v1/assessment/outcomes — {outcomes[], comparisons[]} pre/post θ…, GET /api/assessment/v1/itembank — 2PL items incl. answer keys (server side… (+5 more)

### Community 64 - "LearnerDashboard.tsx"
Cohesion: 0.05
Nodes (55): `frontend/src/`, Code, Connections, In / out, Learner Dashboard (frontend shell), TODOs / edge cases, LearnerDashboard, CareerReadinessCard() (+47 more)

### Community 65 - "items.py"
Cohesion: 0.22
Nodes (28): ast, Document question pipeline (`main-lms-backend/services/doc_quiz/`), Personalised feedback (`items.feedback`), _build_review(), Type-aware answer review, missed questions first. Each wrong answer gets…, accepted_texts(), answer_display(), _choice_set() (+20 more)

### Community 66 - "prerequisite_service.py"
Cohesion: 0.14
Nodes (24): find_cycle(), infer_edges(), _node(), _norm_sf(), _ols(), Any, ndarray, services/prerequisite_service.py — cross-competency prerequisite DAG (SCIL v6… (+16 more)

### Community 67 - "generate_mock_data.py"
Cohesion: 0.13
Nodes (30): _batch(), build_catalog(), build_enrollments(), build_item_bank(), build_offices(), build_officials(), build_role(), build_workplace_evidence() (+22 more)

### Community 68 - "generate"
Cohesion: 0.12
Nodes (18): build_crosswalk(), build_frac(), build_gsbpm_map(), build_hrms(), build_prerequisites(), dumps(), dumps_records(), find_cycle() (+10 more)

### Community 69 - "Any"
Cohesion: 0.19
Nodes (9): ILearningPlatformAdapter, ABC, Any, Interface for external learning platform integration. All concrete adapters…, Return the full CBP course catalog., Return learning history for a user (legacy, by govId or userId)., Return the full user roster (all officials)., Look up a single user by their iGOT userId (usr_...). Returns None if not found. (+1 more)

### Community 70 - "capabilities"
Cohesion: 0.25
Nodes (9): get, JSONResponse, capabilities(), _importable(), YouTube blocks by IP reputation, so the same link works from a laptop and fails…, Really import it. find_spec() only proves the wheel is on disk — OpenCV's wheel…, youtube_diagnose(), is_youtube_url() (+1 more)

### Community 71 - "rag.py"
Cohesion: 0.08
Nodes (48): Conventions, Code, Code, QuizAttempt, Persists every MCQ-quiz submission BEFORE evidence is written. UniqueConstraint…, _chunk_document_text(), _clean_text(), _competency_rows() (+40 more)

### Community 72 - "test_doc_quiz.py"
Cohesion: 0.11
Nodes (21): extract_docx(), Returns (text with section markers, section count)., _table_rows(), Document quiz: extraction (DOCX, OCR), cited multi-type generation, grading…, _chunks(), _mcq(), parametrize, services/doc_quiz — question types, validator, dedup, selection, calibration,… (+13 more)

### Community 76 - "validate"
Cohesion: 0.12
Nodes (15): excerpt(), _jaccard(), _numberish(), _opts(), plausibility_and_dedup(), quote_in_source(), The sentence(s) of the source that best match the quote — the passage shown to…, Returns a normalised question dict or None (reason counted in stats). (+7 more)

### Community 77 - "AdminDashboard.tsx"
Cohesion: 0.06
Nodes (71): Frontend, AdminDashboard, AdminActions(), AssignForm(), when(), AdminFilterBar(), ExportButton(), facetLabels() (+63 more)

### Community 87 - "api.ts"
Cohesion: 0.04
Nodes (70): AGENDA_TYPE, CapabilityRiskPanel(), ForesightPanel(), GsbpmScopePanel(), pct(), PrerequisitePanel(), PRIORITY_CHIP, RISK_CHIP (+62 more)

### Community 88 - "learning_mode.py"
Cohesion: 0.22
Nodes (17): ErrorResponse, _generate_overview(), learning_chat(), LearningChatMessage, LearningChatRequest, LearningChatResponse, LearningCitation, LearningMetadata (+9 more)

### Community 89 - "seed.py"
Cohesion: 0.15
Nodes (18): hash_password(), Return a bcrypt hash of the plain-text password., _derive_password(), _fetch_officials(), main(), Session, auth/seed.py…, Insert the hardcoded admin user. Returns True if inserted, False if already… (+10 more)

### Community 90 - "mock-igot-server/main.py"
Cohesion: 0.13
Nodes (21): contextlib, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history(), health() (+13 more)

### Community 91 - ".fetch_user_cbplan"
Cohesion: 0.17
Nodes (11): AsyncClient, fetch(), fetch(), fetch(), fetch(), Pooled client for the running loop — no new TCP connection per call., TTL memo for one user's read. Concurrent callers share one in-flight request;…, GET /api/evidence/v1/user/{id} — EvidenceLog-style workplace evidence rows ([]… (+3 more)

### Community 92 - "Media (Video / Audio / YouTube) → Evidence-Cited Quiz"
Cohesion: 0.15
Nodes (10): Getting past the bot check, In / out, Media (Video / Audio / YouTube) → Evidence-Cited Quiz, Pipeline, Setup, TODOs / edge cases, Verification, YouTube (+2 more)

### Community 93 - "TrainingNudge"
Cohesion: 0.15
Nodes (14): A reminder sent by an admin to an official behind on mandatory (ACBP) training., TrainingNudge, create(), _ensure_self_or_admin(), _last_nudges(), my_training_actions(), NudgeIn, BaseModel (+6 more)

### Community 94 - "services/__init__.py"
Cohesion: 0.13
Nodes (23): One learner interaction with a recommended course. `event` ∈ impression | click…, RecommendationFeedback, feedback_summary(), FeedbackBody, my_feedback(), post_feedback(), BaseModel, get (+15 more)

### Community 95 - "competency.py"
Cohesion: 0.10
Nodes (36): CertificateSubmission, Competency, EvidenceLog, LevelDispute, One uploaded certificate (routers/competency.py). On upload each extracted…, status: OPEN (test started) → CONFIRMED | RAISED | LOWER_THAN_SHOWN once the…, CertificateReview, certificates_for_review() (+28 more)

### Community 96 - "test_certificate_evidence.py"
Cohesion: 0.13
Nodes (17): dotenv, fastapi_testclient, auth/database.py…, auth/models.py…, Admin console write actions end to end on an in-memory SQLite DB, with the…, test_nudge_only_officials_behind_and_respect_cooldown(), Certificate upload → EvidenceLog → admin review, end to end on in-memory SQLite…, _rows() (+9 more)

### Community 97 - "CourseCard.tsx"
Cohesion: 0.18
Nodes (13): BADGE_STYLE, CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBarProps, MODALITY_LABEL, SOURCE_STYLES, matches() (+5 more)

### Community 98 - "lifespan"
Cohesion: 0.33
Nodes (7): lifespan(), _load_json(), _load_json_from_dir(), Any, FastAPI, Load all datasets into memory once at startup, so no request touches the file…, Load a JSON file from ROOT_DIR. Raises RuntimeError on missing file.

### Community 99 - "system_health.py"
Cohesion: 0.29
Nodes (17): is_embedder_ready(), Non-blocking check — True only if the role's model is already loaded., is_semantic_engine_ready(), groq_keys(), basic(), _component(), detailed(), _embedders() (+9 more)

### Community 100 - "LearningChat.tsx"
Cohesion: 0.26
Nodes (12): ChatEntry, LearningChat(), LearningChatProps, fetchWithTimeout(), LearningChatResponse, LearningChatTurn, LearningCitation, LearningMetadata (+4 more)

### Community 101 - "test_reply_regression.py"
Cohesion: 0.19
Nodes (17): ChatHistoryItem, BaseModel, RecommendationContext, SkillGapContext, sample_request(), _chat(), parametrize, End-to-end /chat behaviour per language through the real multilingual… (+9 more)

### Community 102 - "workforce_service.py"
Cohesion: 0.26
Nodes (15): How the parts work, _as_date(), capability_risk(), cell(), foresight(), _level(), _p_capable(), Any (+7 more)

### Community 103 - "mock_data_metrics.py"
Cohesion: 0.27
Nodes (11): collections, _get(), live_metrics(), _login(), main(), offline_metrics(), _pct(), Mock-data quality metrics — run before/after regenerating mock data. cd main-… (+3 more)

### Community 104 - "typing"
Cohesion: 0.10
Nodes (28): needs_ocr(), _ocr_engine(), ocr_pdf_pages(), OcrUnavailable, ndarray, RuntimeError, FILE: services/doc_quiz/extract.py…, (text in reading order, mean confidence, weak lines dropped). (+20 more)

### Community 105 - "practice_assessment.py"
Cohesion: 0.09
Nodes (38): Practice ability (`main-lms-backend/services/practice_assessment.py`), bump(), courses_for_topics(), latest_practice_value(), link_competency(), media_question_difficulty(), next_difficulty(), normalise_difficulty() (+30 more)

### Community 106 - "_db"
Cohesion: 0.16
Nodes (12): AdminDailySnapshot, One row per calendar day (UTC): the workforce headline numbers plus the same…, daily_snapshot_loop(), _db(), mark_nudge_read(), Run fn(session) in the threadpool with a committed-or-rolled-back session., Upsert today's AdminDailySnapshot from the live roster + workforce snapshot., Started once from main._startup. Waits for the DB, gives the workforce snapshot… (+4 more)

### Community 107 - "youtube_diagnosis"
Cohesion: 0.18
Nodes (10): _count_formats(), _pick_captions(), _pot_provider_installed(), (url of a json3 track, kind, lang) — manual subtitles first, then original-…, (video-only/muxed formats we could use for frames, audio-bearing formats)., What can this host actually do with YouTube? Reports the yt-dlp version, the…, A diagnosis that raises is useless — report the failure as its own answer., _safe() (+2 more)

### Community 108 - ".__init__"
Cohesion: 0.11
Nodes (14): Before / after metrics, Could not do / blocked, Decisions log (made without the user), Noticed but out of scope (not fixed), SCIL v6 — mock data + blocked features: progress report, Status, ndarray, Stable hash of a course's embedded text — decides whether a stored vector is… (+6 more)

### Community 109 - "mock_igot_server.py"
Cohesion: 0.19
Nodes (15): composite_search(), CompositeSearchRequest, _course_tags(), _enriched_view(), EnrolPayload, get_enriched_courses(), legacy_enroll_user(), legacy_push_score() (+7 more)

### Community 110 - "admin_analytics.py"
Cohesion: 0.14
Nodes (28): Backend, overview(), _competency_metrics(), daily_metrics(), by(), dept_compliance(), facets(), Filters (+20 more)

### Community 111 - "test_irt.py"
Cohesion: 0.27
Nodes (12): laplace_posterior(), (mode, sd) of N(prior) × Π 2PL likelihoods, Laplace approximation. responses =…, _bank(), _grid_posterior(), Tier-1 2PL posterior + adaptive diagnostic (SCIL v6 §2). pytest…, _run(), test_answering_the_wrong_item_or_after_the_end_is_rejected(), test_correct_answers_move_the_estimate_up_wrong_ones_down() (+4 more)

### Community 112 - "build_outcomes"
Cohesion: 0.24
Nodes (10): build_acbp(), build_outcomes(), record(), course_hours(), course_tags(), _fit(), _mandatory_entry(), _mandatory_pick() (+2 more)

### Community 113 - "test_gap_and_recommendation_upgrades.py"
Cohesion: 0.09
Nodes (30): calculate_baseline(), EvidencePayload, BaseModel, Stateless calculator for one competency, on exactly the scoring path the…, assess_competency(), explain_level(), datetime, One competency, K/A/U/S fused — the scoring path shared by compute_for_user and… (+22 more)

### Community 114 - "_warm_up"
Cohesion: 0.07
Nodes (30): AbstractEventLoop, 1. Runtime topology, 3. Core data flow, Connections, Gyan — Multilingual Chat Assistant, In / out, TODOs / edge cases, Connections (+22 more)

### Community 119 - "document_extractor.py"
Cohesion: 0.12
Nodes (30): CertificateExtractionResult, _clamp_level(), DocumentExtractorService, ExtractedCompetency, ExtractionError, frac_by_id(), frac_dictionary(), _gemini_extract() (+22 more)

### Community 124 - "MockIgotAdapter"
Cohesion: 0.20
Nodes (6): MockIgotAdapter, Forget every cached read for this user., The full CBP course catalogue, paged through POST /api/composite/v1/search.…, POST /api/composite/v1/search — Sunbird composite search, every page. `filters`…, Legacy method that maps fetch_user_enrollments to the old simple-mock shape.…, Calls the Sunbird-compliant mock iGOT server (mock_igot_server.py) on port 8001…

### Community 126 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.29
Nodes (6): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only, data(), files(), fixture

### Community 127 - "CLAUDE.md"
Cohesion: 0.08
Nodes (23): CLAUDE.md — index & router, Feature index, graphify, How to use these docs, Run commands, Certificate / Resume Evidence Extraction, In / out, TODOs / edge cases (+15 more)

### Community 128 - "Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)"
Cohesion: 0.22
Nodes (7): GSBPM scope — the 80% officer-hours rule (SCIL v6 §1), Reference data loading, TODOs / limits, Used by the admin console, Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight), GET /api/gsbpm/v1/map — GSBPM sub-processes + competency → sub-processes., GET /api/org/v1/offices — {cycle, offices[{officeId, subprocesses[{id,…

### Community 129 - "calibration.py"
Cohesion: 0.21
Nodes (14): Difficulty calibration (`services/doc_quiz/calibration.py`), QuizItemStat, Response data per quiz item (services/doc_quiz/calibration.py). itemKey is a…, calibrate(), calibrate_items(), difficulty_from_b(), load_stats(), Any (+6 more)

### Community 131 - "Admin Dashboard"
Cohesion: 0.18
Nodes (11): Admin Dashboard, Code, Endpoints (`/api/v1/admin/console`, all take `?department=&grade=&office=`), TODOs / edge cases, What the synthetic data shows, normalise(), One mock-roster user → the row shape every admin view uses., client() (+3 more)

### Community 133 - "safe_eval"
Cohesion: 0.18
Nodes (11): In / out, RAG Document → Quiz Generator & Grading (quiz ↔ skill gap), TODOs / edge cases, Verification, _computed_ok(), expression_numbers(), Evaluate +,-,*,/,**,%, parentheses and a few math functions. Raises ValueError…, Literal numbers used in an expression (for the 'inputs come from the source'… (+3 more)

### Community 134 - "HybridRecommendationEngine"
Cohesion: 0.08
Nodes (29): Code, _course_summary(), _CourseDoc, _fmt_levels(), GapEntry, HybridRecommendationEngine, _interleave_by_level(), BaseModel (+21 more)

### Community 136 - "_StubEmbedder"
Cohesion: 0.31
Nodes (9): test_stored_embeddings_are_reused_only_when_text_matches(), test_tpac_boost_depends_on_provenance(), _course(), _frac(), Hashed bag-of-words → L2-normalised vector. Shared words ⇒ positive cosine., _StubEmbedder, test_classroom_cap_defers_the_ladder(), test_curated_crosswalk_is_used_before_embeddings() (+1 more)

### Community 137 - "Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026)"
Cohesion: 0.25
Nodes (7): 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator

### Community 138 - "When the wall is the IP itself"
Cohesion: 0.38
Nodes (7): When the wall is the IP itself, fetch_watch_page(), parse_player_response(), (html, final url) for a plain watch-page GET — a different surface from the…, The ytInitialPlayerResponse object embedded in the watch page. It is followed…, watch_page_caption_tracks(), _watch_page_probe()

### Community 140 - "AI Course Recommendation Engine + Learning Pathways"
Cohesion: 0.33
Nodes (5): AI Course Recommendation Engine + Learning Pathways, Connections, In / out, TODOs / edge cases, {courseId: {compId: FRAC level}} — feeds BaselineAssembler so the Verified…

### Community 141 - "reconstruct_history"
Cohesion: 0.40
Nodes (3): date, Daily training-rate history rebuilt from dated iGOT course completions, for…, reconstruct_history()

### Community 142 - "has_cookies"
Cohesion: 0.40
Nodes (5): _blocked_message(), cookies_path(), has_cookies(), _no_speech_message(), The cookies.txt yt-dlp should use, materialising MEDIA_YOUTUBE_COOKIES_B64 onto…

### Community 143 - "get"
Cohesion: 0.14
Nodes (14): get_crosswalk(), get_org_roles(), health(), legacy_catalog(), legacy_frac(), legacy_job_profiles(), legacy_user_history(), get (+6 more)

### Community 145 - "Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)"
Cohesion: 0.50
Nodes (4): Cold start for UNASSESSED competencies, Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8), Foresight, Proficiency belief with dated decay

### Community 148 - "Code"
Cohesion: 0.18
Nodes (15): Code, CertificateReviewQueue(), Row(), STATUS_CLS, TABS, when(), CertificateUploadZone(), clean() (+7 more)

### Community 149 - "semantic_engine.py"
Cohesion: 0.11
Nodes (23): difflib, model_name(), classify_intent(), _correct_tokens(), _ensure_prototypes(), load_corpus(), FILE: ai/semantic_engine.py…, Encode all prototype phrases once, via the shared singleton embedder. (+15 more)

### Community 150 - "get_embedder"
Cohesion: 0.07
Nodes (32): Code, functools, _Embedder, encode_cached(), get_embedder(), _load(), onnx_model_dir(), _OnnxEmbedder (+24 more)

### Community 155 - "_sunbird_result"
Cohesion: 0.25
Nodes (5): GET /api/frac/competencies — the catalogue FRAC set incl. L1–L5 descriptors., GET /api/frac/v1/crosswalk — iGOT dictionary CID id → catalogue FRAC id., GET /api/admin/v1/users Returns: result.users — full list of officials., Safely drill into a Sunbird envelope: data['result']['key1']['key2']..., _sunbird_result()

### Community 157 - "Timeline"
Cohesion: 0.11
Nodes (21): Performance, build_chunks(), Chunk, Evidence, fmt_ts(), _make_chunk(), FILE: services/media_quiz/evidence.py…, slide_windows: [{"t_start", "t_end", "evidence_ids": [ocr/vlm ids of that… (+13 more)

## Knowledge Gaps
- **300 isolated node(s):** `Pipeline`, `In / out`, `Setup`, `Verification`, `AssessmentUploadZoneProps` (+295 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1082 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **43 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `UserAuth` connect `UserAuth` to `test_certificate_evidence.py`, `router.py`, `Admin Dashboard`, `rag.py`, `career.py`, `karma.py`, `_db`, `Code`, `admin_analytics.py`, `services/__init__.py`, `document_extractor.py`, `main-lms-backend/main.py`, `seed.py`, `TrainingNudge`, `admin_console.py`, `competency.py`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `Code` connect `Code` to `rag.py`, `karma.py`, `lucide-react`, `AdminDashboard.tsx`, `domain.ts`, `api.ts`, `.fetch_user_cbplan`, `competency.py`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `Code` connect `pipeline.py` to `AssessmentPage.tsx`, `chatbot.py`, `typing`, `practice_assessment.py`, `youtube_diagnosis`, `generate.py`, `gemini_json`, `media_io.py`, `download_youtube`, `get_embedder`, `Media (Video / Audio / YouTube) → Evidence-Cited Quiz`, `Timeline`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 78 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `HybridRecommendationEngine` (e.g. with `7. Mismatches between the mermaid diagram and the code` and `Code`) actually correct?**
  _`HybridRecommendationEngine` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 45 inferred relationships involving `Code` (e.g. with `KarmaCard()` and `formatPoints()`) actually correct?**
  _`Code` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Pipeline`, `In / out`, `Setup` to the rest of the system?**
  _300 weakly-connected nodes found - possible documentation gaps or missing edges._