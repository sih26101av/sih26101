# Graph Report - SIH_IGot  (2026-09-24)

## Corpus Check
- 297 files · ~5,036,129 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 6, .service 2, .example 2)

## Summary
- 3501 nodes · 8816 edges · 174 communities (127 shown, 47 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 969 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e63c3aa8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_live_catalogue.py
- useLearnerDashboard.ts
- Code
- Code
- package.json
- mock_igot_server.py
- career_readiness
- ChatWidget.tsx
- karma.py
- Timeline
- ytrelay.py
- test_doc_quiz.py
- Code
- insights.py
- download_model.py
- generate.py
- gemini_json
- What You Must Do When Invoked
- recommendation_service.py
- test_pathway.py
- KarmaRewardsView.tsx
- extractors.py
- router.py
- ytgemini.py
- compilerOptions
- pydantic
- 🇮🇳 MoSPI Skill Intelligence Platform
- media_quiz.py
- .__init__
- Admin console tier
- math
- react
- LearnerDashboard.tsx
- ReplyContext
- api.ts
- speech.d.ts
- graphify reference: extra exports and benchmark
- resolve_level
- BaseModel
- compilerOptions
- mock_data_metrics.py
- graphify reference: query, path, explain
- test_irt.py
- Any
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- test_mock_data.py
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- models/models.py
- .claude/CLAUDE.md
- extraction-spec.md
- test_admin_chat.py
- rag.py
- get_learning_pathway
- media_io.py
- UserAuth
- MockIgotAdapter
- domain.ts
- items.py
- numpy
- generate_mock_data.py
- Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)
- mock-igot-server/main.py
- lifespan
- learning_mode.py
- QuizQuestionInput.tsx
- faker
- CourseCard.tsx
- chat
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
- catalogue_source.py
- CertificateReviewQueue.tsx
- proficiency_service.py
- test_certificate_evidence.py
- _competencies
- _probe_clients
- AssessmentPage.tsx
- calibration.py
- mediaQuizApi.ts
- workforce_service.py
- test_chat_messages.py
- Mock iGOT Karmayogi Integration (Adapter + mock server + mock data)
- system_health.py
- Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)
- extract.py
- competency.py
- typing
- LearningChat.tsx
- practice_assessment.py
- Deploy: backend on Oracle Cloud, frontend on Vercel
- get_embedder
- Decisions log (made without the user)
- get_enriched_courses
- admin_analytics.py
- _Session
- App.tsx
- test_proficiency_foresight.py
- BaselineAssembler
- google_generativeai
- langchain_text_splitters
- IKarmaStrategy
- pdfplumber
- probe.py
- pptx
- pypdf
- requests
- admin_chat.py
- _warm_up
- urllib_request
- services/__init__.py
- CLAUDE.md
- test_chat_endpoint.py
- seed.py
- generate
- _answer_admin
- karma_engine.py
- datetime
- HybridRecommendationEngine
- safe_eval
- test_gap_and_recommendation_upgrades.py
- build_enrollments
- update.sh
- QuizSkillImpact.tsx
- youtube-access.sh
- Karma Points (gamification)
- vercel.json
- language_service.py
- Code
- schemas.py
- setup.sh
- _resolve_competency_state
- catalogue_store.py
- services_media_quiz_pipeline
- graphify reference: incremental update and cluster-only
- client
- main-lms-backend/main.py
- engine
- frontend_src_hooks_useadmindata_adminrosterrow
- routers
- KarmaEventType
- pipeline.py
- chat_actions.py
- _user_enrolments
- mockdata/domain.py
- services
- services_media_quiz
- services_media_quiz_evidence
- services_media_quiz_fact_check
- document_extractor.py
- services_media_quiz_llm
- services_media_quiz_question_gen
- services_media_quiz_relevance
- ai
- mockdata
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
- `Code` --references--> `WhyThisLevel()`  [INFERRED]
  docs/features/skill-gap-analysis.md → frontend/src/components/dashboard/SkillGapCard.tsx
- `TODOs / edge cases` --references--> `gradeQuiz()`  [INFERRED]
  docs/features/media-quiz-generator.md → frontend/src/services/api.ts
- `Code` --references--> `KarmaLevel`  [INFERRED]
  docs/features/karma-points.md → frontend/src/types/domain.ts

## Import Cycles
- None detected.

## Communities (174 total, 47 thin omitted)

### Community 0 - "test_live_catalogue.py"
Cohesion: 0.05
Nodes (48): Live iGOT (the real portal), _as_list(), course_url(), _first_str(), LiveIgotAdapter, normalise_course(), Any, AsyncClient (+40 more)

### Community 1 - "useLearnerDashboard.ts"
Cohesion: 0.11
Nodes (18): ProgressViewProps, Props, RecentActivityList(), relative(), _cache, NO_ACHIEVEMENTS, NO_ENROLLMENTS, NO_GAPS (+10 more)

### Community 2 - "Code"
Cohesion: 0.13
Nodes (14): Code, KarmaEvent, KarmaMonthlyUsage, Immutable ledger entry — one row per karma point award event., Rolling monthly counter for non-CBP COURSE_COMPLETION events. Enforces the…, AwardResult, KarmaEngine, Dispatches an eventType to its strategy, then applies the shared rules in… (+6 more)

### Community 3 - "Code"
Cohesion: 0.09
Nodes (36): bcrypt, Code, TokenBridge(), mapRole(), registerLogoutCallback(), setApiToken(), hashlib, jose (+28 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (43): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+35 more)

### Community 5 - "mock_igot_server.py"
Cohesion: 0.10
Nodes (53): exception_handler, HTTPException, composite_search(), get_admin_roster(), get_assessment_outcomes(), get_competencies(), get_course_catalog(), get_crosswalk() (+45 more)

### Community 6 - "career_readiness"
Cohesion: 0.24
Nodes (12): career_readiness(), _dispute_view(), _ensure_can_view(), my_disputes(), office_ladder(), Any, get, Roles of one office grouped by tier, most junior tier first. (+4 more)

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.07
Nodes (62): AdminChatWidget(), AdminChatWidgetProps, CAPABILITIES, SUGGESTION_KEYS, MessageBubble(), NavConfirmBanner(), renderMarkdown(), TypingIndicator() (+54 more)

### Community 8 - "karma.py"
Cohesion: 0.17
Nodes (22): fastapi_concurrency, admin_adjust_karma(), AdminAdjustRequest, _assert_self_or_admin(), award_karma_event(), _award_response(), CbpClaimRequest, claim_cbp_bonus() (+14 more)

### Community 9 - "Timeline"
Cohesion: 0.10
Nodes (24): dataclasses, Performance, build_chunks(), Chunk, Evidence, fmt_ts(), _make_chunk(), FILE: services/media_quiz/evidence.py… (+16 more)

### Community 10 - "ytrelay.py"
Cohesion: 0.07
Nodes (46): _bench(), _benched(), _body_error(), candidates(), _checked(), classify(), _clean(), _client() (+38 more)

### Community 11 - "test_doc_quiz.py"
Cohesion: 0.13
Nodes (17): Document quiz: extraction (DOCX, OCR), cited multi-type generation, grading…, _chunks(), _mcq(), parametrize, services/doc_quiz — question types, validator, dedup, selection, calibration,…, test_choice_feedback_uses_option_rationale(), test_courses_for_topics_prefers_competency_courses(), test_fill_blank_and_true_false_rules() (+9 more)

### Community 12 - "Code"
Cohesion: 0.15
Nodes (27): Connections, Code, rows_for(), tag_id(), _completed_courses(), _education_score(), enrollment_course_id(), is_completed() (+19 more)

### Community 13 - "insights.py"
Cohesion: 0.14
Nodes (22): capability_risk(), _frac_names(), gsbpm_scope(), prerequisite_dag(), get, post, routers/insights.py — admin-only SCIL v6 workforce insights Every number here…, Rebuild the workforce snapshot now (≈ a few seconds). (+14 more)

### Community 14 - "download_model.py"
Cohesion: 0.15
Nodes (19): onnx_model_dir(), get_reranker(), ndarray, FILE: ai/reranker.py…, Cross-encoder scores for `passages` against `query`, or None if no reranker., Relevance logits, one per (query, passage) pair (higher = better match)., The loaded cross-encoder, or None when disabled / unavailable (logged once)., rerank_scores() (+11 more)

### Community 15 - "generate.py"
Cohesion: 0.09
Nodes (40): _call(), _density(), difficulty_quotas(), DocChunk, excerpt(), generate(), _index(), _jaccard() (+32 more)

### Community 16 - "gemini_json"
Cohesion: 0.08
Nodes (37): LLM providers (Groq multi-key → Gemini), Exception, gemini_json(), _groq_json(), llm_configured(), ollama_vision_json(), parse_json(), Any (+29 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "recommendation_service.py"
Cohesion: 0.13
Nodes (17): _by_score(), _course_summary(), _diagnostic_step(), _fmt_levels(), _interleave_by_level(), FILE: main-lms-backend/services/recommendation_service.py…, Returns deduplicated, level-gated recommendations in gap-priority order. Only…, Step-by-step path for one competency: one course per FRAC level from current+1… (+9 more)

### Community 19 - "test_pathway.py"
Cohesion: 0.06
Nodes (32): test_mandatory_courses_always_included_with_badge(), test_why_recommended_describes_the_level_step(), _edge(), _gap(), _kinds_levels(), Skill-gap levels + level-aware recommendations + learning pathways. Runs on a…, Bug #11: the block used to come back in level order, so a weak course sat above…, Bugs #9/#10: relevance and quality were min-maxed inside the shortlist, so the… (+24 more)

### Community 20 - "KarmaRewardsView.tsx"
Cohesion: 0.10
Nodes (26): KarmaCard(), PassbookRow(), PILL_ORDER, RightSidebar(), RightSidebarProps, EVENT_META, formatPoints(), KarmaEventMeta (+18 more)

### Community 21 - "extractors.py"
Cohesion: 0.09
Nodes (36): add_captions(), flush(), _budget(), describe_keyframes(), guarded(), run_batch(), get_whisper(), lang_of() (+28 more)

### Community 22 - "router.py"
Cohesion: 0.08
Nodes (37): fastapi, fastapi_security, get_db(), auth/database.py…, FastAPI dependency — `db: Session = Depends(get_db)`; closed after the request., get_current_user(), auth/dependencies.py…, Decodes the Bearer JWT, looks up the user in auth.db. Raises HTTP 401 for any… (+29 more)

### Community 23 - "ytgemini.py"
Cohesion: 0.06
Nodes (48): Client, concurrent_futures, gemini_key(), _call(), _cues(), diagnosis(), enabled(), fetch() (+40 more)

### Community 24 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 25 - "pydantic"
Cohesion: 0.07
Nodes (40): Code, Connections, In / out, Ollama RAG Knowledge Base (Tier 3 — disconnected), TODOs / edge cases, build_system_prompt(), generate_chat_response(), is_ollama_available() (+32 more)

### Community 26 - "🇮🇳 MoSPI Skill Intelligence Platform"
Cohesion: 0.11
Nodes (17): 🧠 AI Models Required, 🛠️ API Reference, 🏗️ Architecture, 🔑 Environment Variables, 🤖 Gyan AI Chat — How It Works, 🇮🇳 MoSPI Skill Intelligence Platform, 📁 Project Structure, 🚀 Quick Start (First-Time Setup) (+9 more)

### Community 27 - "media_quiz.py"
Cohesion: 0.11
Nodes (31): fastapi_responses, functools, ImportError, importlib_util, _cached_result(), capabilities(), _importable(), MediaMetadata (+23 more)

### Community 28 - ".__init__"
Cohesion: 0.14
Nodes (10): _CourseDoc, _parse_level(), Stable hash of a course's embedded text — decides whether a stored vector is…, Bayesian shrinkage toward global prior mean. Returns None if either input is…, Level 3' / 3 / '3' → 3; anything outside 1..5 → None., `catalog` / `frac` / `crosswalk` are the lists served by the mock iGOT server…, Fix the quality scale to the catalogue instead of to the shortlist. Quality…, Stored vectors whose text hash still matches; encode (disk-memoised) the rest. (+2 more)

### Community 29 - "Admin console tier"
Cohesion: 0.16
Nodes (25): Admin console tier, AdminTab, behind_facts(), _clean(), competency_names(), department_facts(), find_officials(), _full_name() (+17 more)

### Community 30 - "math"
Cohesion: 0.22
Nodes (8): CompetencyCalculator, datetime, FILE: main-lms-backend/services/competency_service.py…, Maps FRAC types from the JSON to calculation categories., Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, test_missing_channels_do_not_drag_the_score_to_zero(), math

### Community 31 - "react"
Cohesion: 0.06
Nodes (57): Accessibility preferences, GIGW compliance & accessibility (frontend chrome), Statutory pages, The chrome, and where it comes from, TODO, Verifying a change here, Visual design system (shared by every page), Breadcrumbs() (+49 more)

### Community 32 - "LearnerDashboard.tsx"
Cohesion: 0.06
Nodes (59): `frontend/src/`, Other GIGW / WCAG work applied across the app, Code, Connections, In / out, Learner Dashboard (frontend shell), Responsive layout (phones 360–430px, tablets 768–1024px), TODOs / edge cases (+51 more)

### Community 33 - "ReplyContext"
Cohesion: 0.16
Nodes (19): importlib, Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile(), Any, Everything a reply template may personalise, built once per chat request., ReplyContext, _by_page(), _gap_lines() (+11 more)

### Community 34 - "api.ts"
Cohesion: 0.04
Nodes (65): AGENDA_TYPE, CapabilityRiskPanel(), ForesightPanel(), GsbpmScopePanel(), pct(), PrerequisitePanel(), PRIORITY_CHIP, RISK_CHIP (+57 more)

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
Cohesion: 0.09
Nodes (24): field_validator, CompetencyOut, CompositeSearchRequest, ContentStateRequest, _course_by_id(), CourseOut, EnrolPayload, get_content_state() (+16 more)

### Community 39 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 40 - "mock_data_metrics.py"
Cohesion: 0.27
Nodes (11): collections, _get(), live_metrics(), _login(), main(), offline_metrics(), _pct(), Mock-data quality metrics — run before/after regenerating mock data. cd main-… (+3 more)

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 42 - "test_irt.py"
Cohesion: 0.13
Nodes (22): DiagnosticSessions, fisher_information(), laplace_posterior(), next_item(), p_correct(), public_item(), Any, services/irt_service.py — Tier-1 Bayesian 2PL posterior + adaptive diagnostic… (+14 more)

### Community 43 - "Any"
Cohesion: 0.12
Nodes (14): Opportunity to practise (SCIL v6 §4), StudyPlanSummary(), absorb(), add_step(), advance(), open_ladders(), _PrerequisiteGate, Any (+6 more)

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
Cohesion: 0.09
Nodes (36): 7. Mismatches between the mermaid diagram and the code, Base, Authentication & RBAC, Connections, In / out, Shared database (Neon), TODOs / edge cases, Connections (+28 more)

### Community 54 - "test_admin_chat.py"
Cohesion: 0.16
Nodes (24): ask(), client(), fixture, Gyan on the admin console: routers/admin_chat.py end to end, with the roster,…, Both classifiers answer fixed (intent, confidence) pairs — no embedder., stub_intents(), test_a_department_named_in_the_message_scopes_the_answer(), test_a_shared_surname_asks_which_official() (+16 more)

### Community 58 - "rag.py"
Cohesion: 0.10
Nodes (30): QuizAttempt, Persists every MCQ-quiz submission BEFORE evidence is written. UniqueConstraint…, _competency_rows(), _detect_skill_name(), DocumentMetadata, DocumentUploadResponse, ErrorResponse, _generate_questions() (+22 more)

### Community 60 - "get_learning_pathway"
Cohesion: 0.20
Nodes (8): _ensure_can_view(), get_learning_pathway(), get_recommendations_by_user_id(), get_skill_gaps_by_user_id(), A learner may only read their own competency data; admins may read anyone's., Skill-gap analysis on the 6-term baseline formula — a weighted mean over the…, Level-gated hybrid recommendations: Stage 0 — gap prioritisation (priority_k =…, Step-by-step learning paths. For every role competency: one course per FRAC…

### Community 61 - "media_io.py"
Cohesion: 0.05
Nodes (78): How well it actually works, The Gemini tier, The relay tier, Two bugs that made a walled host look worse than it was, When the wall is the IP itself, _blocked_message(), _cache_dir(), cache_load() (+70 more)

### Community 62 - "UserAuth"
Cohesion: 0.08
Nodes (63): AuthBase, csv, UserAuth, AdminDailySnapshot, One row per calendar day (UTC): the workforce headline numbers plus the same…, An admin assigning courses (a training plan) to a department or a list of…, A reminder sent by an admin to an official behind on mandatory (ACBP) training., TrainingAssignment (+55 more)

### Community 63 - "MockIgotAdapter"
Cohesion: 0.06
Nodes (41): Connections, Code, GSBPM scope — the 80% officer-hours rule (SCIL v6 §1), Noticed but out of scope (not fixed), MockIgotAdapter, fetch(), fetch(), fetch() (+33 more)

### Community 64 - "domain.ts"
Cohesion: 0.04
Nodes (51): Props, TIER_LABEL, DEFER_REASON, KIND_STYLE, PathwayLadder(), COLORS, Props, MyCoursesViewProps (+43 more)

### Community 65 - "items.py"
Cohesion: 0.23
Nodes (28): ast, Document question pipeline (`main-lms-backend/services/doc_quiz/`), TODOs / edge cases, _build_review(), Type-aware answer review, missed questions first. Each wrong answer gets…, accepted_texts(), answer_display(), _choice_set() (+20 more)

### Community 66 - "numpy"
Cohesion: 0.07
Nodes (45): Cross-competency prerequisite DAG (SCIL v6 §5, B4), find_cycle(), infer_edges(), _node(), _norm_sf(), _ols(), Any, ndarray (+37 more)

### Community 67 - "generate_mock_data.py"
Cohesion: 0.17
Nodes (25): build_catalog(), build_item_bank(), build_offices(), build_officials(), build_role(), build_workplace_evidence(), _course_id(), _covariates() (+17 more)

### Community 68 - "Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)"
Cohesion: 0.50
Nodes (4): Reference data loading, TODOs / limits, Used by the admin console, Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)

### Community 69 - "mock-igot-server/main.py"
Cohesion: 0.13
Nodes (22): contextlib, enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles(), get_user_history(), health() (+14 more)

### Community 70 - "lifespan"
Cohesion: 0.33
Nodes (7): lifespan(), _load_json(), _load_json_from_dir(), Any, FastAPI, Load all datasets into memory once at startup, so no request touches the file…, Load a JSON file from ROOT_DIR. Raises RuntimeError on missing file.

### Community 71 - "learning_mode.py"
Cohesion: 0.12
Nodes (34): Code, Code, Connections, Personalised feedback (`items.feedback`), ErrorResponse, _generate_overview(), learning_chat(), LearningChatMessage (+26 more)

### Community 72 - "QuizQuestionInput.tsx"
Cohesion: 0.19
Nodes (19): Frontend, emptyAnswer(), hindi(), isAnswered(), pick(), Props, qType(), QuizLang (+11 more)

### Community 74 - "CourseCard.tsx"
Cohesion: 0.18
Nodes (14): BADGE_STYLE, CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBar(), MatchScoreBarProps, MODALITY_LABEL, SOURCE_STYLES (+6 more)

### Community 75 - "chat"
Cohesion: 0.18
Nodes (17): Code, TabType, low_confidence_threshold(), chat(), ChatHistoryItem, ChatRequest, detect_intent_keyword(), BaseModel (+9 more)

### Community 76 - "chatbot.py"
Cohesion: 0.33
Nodes (15): ChatResponse, _intent_response(), _intercept(), FILE: routers/chatbot.py Multilingual AI Learning Assistant — Gyan (ज्ञान)…, Deterministic handling of English commands the classifier has historically…, _response(), _theme_action(), _ui_action_response() (+7 more)

### Community 77 - "AdminDashboard.tsx"
Cohesion: 0.07
Nodes (61): Frontend, AdminActions(), AssignForm(), when(), AdminFilterBar(), ExportButton(), facetLabels(), describeFilters() (+53 more)

### Community 87 - "catalogue_source.py"
Cohesion: 0.16
Nodes (16): _apply_crosswalk(), configured_source(), fetch(), is_live(), _load_disk_catalogue(), Any, services/catalogue_source.py — where the course catalogue comes from The…, The catalogue to rank over, plus the resolved source label. Raises only if… (+8 more)

### Community 88 - "CertificateReviewQueue.tsx"
Cohesion: 0.17
Nodes (14): CertificateReviewQueue(), Row(), STATUS_CLS, TABS, when(), CertificateUploadZone(), clean(), STATUS_CHIP (+6 more)

### Community 89 - "proficiency_service.py"
Cohesion: 0.14
Nodes (20): cluster_of(), decay(), expected_shortfall(), months_between(), office_phase(), _phi(), _Phi(), proficiency_state() (+12 more)

### Community 90 - "test_certificate_evidence.py"
Cohesion: 0.16
Nodes (15): fastapi_testclient, Admin console write actions end to end on an in-memory SQLite DB, with the…, test_nudge_only_officials_behind_and_respect_cooldown(), Certificate upload → EvidenceLog → admin review, end to end on in-memory SQLite…, _rows(), test_admin_approve_turns_rows_verified(), test_admin_reject_removes_rows(), test_bad_extension_rejected() (+7 more)

### Community 91 - "_competencies"
Cohesion: 0.20
Nodes (4): _competencies(), Return the competencies list from profileDetails.competencies., Return the full user roster (all officials)., Look up a single user by their iGOT userId (usr_...). Returns None if not found.

### Community 92 - "_probe_clients"
Cohesion: 0.07
Nodes (21): BaseException, Getting past the bot check, In / out, Media (Video / Audio / YouTube) → Evidence-Cited Quiz, Pipeline, Setup, TODOs / edge cases, Verification (+13 more)

### Community 93 - "AssessmentPage.tsx"
Cohesion: 0.18
Nodes (16): Gyan hand-off (document → quiz or Learning Mode, no second upload), AssessmentPage, AssessmentPage(), DIFFICULTIES, Difficulty, errorText(), formatDate(), guessUploadFormat() (+8 more)

### Community 94 - "calibration.py"
Cohesion: 0.21
Nodes (14): Difficulty calibration (`services/doc_quiz/calibration.py`), QuizItemStat, Response data per quiz item (services/doc_quiz/calibration.py). itemKey is a…, calibrate(), calibrate_items(), difficulty_from_b(), load_stats(), Any (+6 more)

### Community 95 - "mediaQuizApi.ts"
Cohesion: 0.13
Nodes (21): CONTENT_LABEL, MediaAnalysisCard(), MediaAnswerReview(), pct(), QuestionEvidence(), SOURCE_LABEL, YoutubeLinkInput(), API_BASE_URL (+13 more)

### Community 96 - "workforce_service.py"
Cohesion: 0.26
Nodes (15): How the parts work, _as_date(), capability_risk(), cell(), foresight(), _level(), _p_capable(), Any (+7 more)

### Community 97 - "test_chat_messages.py"
Cohesion: 0.23
Nodes (12): Loads a language's template table on first use ("or" lives in or_.py; `or` is a…, templates(), _alternatives(), _fields(), parametrize, Catalogue completeness: every language has every template, placeholders are…, test_every_classifier_intent_has_a_reply(), test_every_intent_renders() (+4 more)

### Community 98 - "Mock iGOT Karmayogi Integration (Adapter + mock server + mock data)"
Cohesion: 0.50
Nodes (4): Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server + mock data), TODOs / edge cases

### Community 99 - "system_health.py"
Cohesion: 0.21
Nodes (22): is_embedder_ready(), model_name(), Non-blocking check — True only if the role's model is already loaded., is_semantic_engine_ready(), admin_chat_mode(), get, chat_mode(), get (+14 more)

### Community 100 - "Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)"
Cohesion: 0.50
Nodes (4): Cold start for UNASSESSED competencies, Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8), Foresight, Proficiency belief with dated decay

### Community 101 - "extract.py"
Cohesion: 0.15
Nodes (16): extract_docx(), needs_ocr(), _ocr_engine(), ocr_pdf_pages(), OcrUnavailable, ndarray, RuntimeError, FILE: services/doc_quiz/extract.py… (+8 more)

### Community 102 - "competency.py"
Cohesion: 0.15
Nodes (21): CertificateSubmission, One uploaded certificate (routers/competency.py). On upload each extracted…, CertificateReview, certificates_for_review(), _find(), my_certificates(), get, post (+13 more)

### Community 103 - "typing"
Cohesion: 0.09
Nodes (26): asyncio, dotenv, httpx, json, logging, ILearningPlatformAdapter, ABC, adapters/igot_adapter.py — iGOT Platform Adapter… (+18 more)

### Community 104 - "LearningChat.tsx"
Cohesion: 0.26
Nodes (12): ChatEntry, LearningChat(), LearningChatProps, fetchWithTimeout(), LearningChatResponse, LearningChatTurn, LearningCitation, LearningMetadata (+4 more)

### Community 105 - "practice_assessment.py"
Cohesion: 0.08
Nodes (42): Practice ability (`main-lms-backend/services/practice_assessment.py`), grade_quiz(), **Grade Quiz → Skill Gap** - user_id comes from the JWT…, Sync DB work for /grade (runs in a worker thread). First submission of a quiz →…, _record_attempt(), bump(), courses_for_topics(), latest_practice_value() (+34 more)

### Community 106 - "Deploy: backend on Oracle Cloud, frontend on Vercel"
Cohesion: 0.22
Nodes (8): 1. Create the VM (Oracle Cloud console), 2. Pick the API hostname, 3. Set up the VM, 4. Frontend on Vercel, Deploy: backend on Oracle Cloud, frontend on Vercel, Troubleshooting, Updating: just `git push` to `main`, YouTube links on the VM

### Community 107 - "get_embedder"
Cohesion: 0.05
Nodes (48): difflib, Code, Connections, In / out, Shared Embedder (chat + catalog roles), TODOs / edge cases, io, _Embedder (+40 more)

### Community 108 - "Decisions log (made without the user)"
Cohesion: 0.25
Nodes (6): Before / after metrics, Could not do / blocked, Decisions log (made without the user), SCIL v6 — mock data + blocked features: progress report, Status, Catalogue duration in hours, or None for a course not in the catalogue.

### Community 109 - "get_enriched_courses"
Cohesion: 0.40
Nodes (6): _course_tags(), _enriched_view(), get_enriched_courses(), _matches_filters(), Sunbird-style filters: each key → value or list of accepted values., The catalogue in the older "enriched" shape. Query params:…

### Community 110 - "admin_analytics.py"
Cohesion: 0.08
Nodes (48): Backend, overview(), _competency_metrics(), daily_metrics(), by(), dept_compliance(), emerging_skills(), facets() (+40 more)

### Community 111 - "_Session"
Cohesion: 0.15
Nodes (21): One learner interaction with a recommended course. `event` ∈ impression | click…, RecommendationFeedback, feedback_summary(), FeedbackBody, my_feedback(), post_feedback(), BaseModel, get (+13 more)

### Community 112 - "App.tsx"
Cohesion: 0.06
Nodes (33): AdminDashboard, App(), DashboardRedirect(), LearnerDashboard, ProtectedRoute(), ProtectedRouteProps, AuthContext, AuthContextType (+25 more)

### Community 113 - "test_proficiency_foresight.py"
Cohesion: 0.21
Nodes (15): cohort_prior(), population_stats(), Cohort prior for an UNASSESSED competency, with the divergence check., comp → (μ_pop, σ_pop, n) over officials with assessed evidence on it., _hrms(), _official(), SCIL v6 §2 dated decay / expected-shortfall / cold start, and §11 workforce…, _snap() (+7 more)

### Community 114 - "BaselineAssembler"
Cohesion: 0.25
Nodes (7): BaselineAssembler, _normalise_course_map(), Accept {courseId: {compId: level}} or the legacy {courseId: [compId]}., test_verified_cert_lifts_confidence_over_documented(), The old `requiredLevel - 1` cap made every evidence-backed gap permanent., test_completion_evidence_follows_the_crosswalk(), test_evidence_can_close_a_gap()

### Community 117 - "IKarmaStrategy"
Cohesion: 0.14
Nodes (11): AdminAdjustmentStrategy, CompletionKarmaStrategy, IKarmaStrategy, ABC, Computes the base points for an event (before the engine's idempotency, per-day…, +5 on self-registration; MDO-onboarded users are not eligible., +5 per completion; non-CBP completions capped per IST calendar month., Milestone-dependent points, passed in by KarmaEngine.check_in. (+3 more)

### Community 119 - "probe.py"
Cohesion: 0.10
Nodes (28): VideoScan, _detector(), get_ocr(), _limit_threads(), map_frames(), probe(), ProbeResult, ndarray (+20 more)

### Community 123 - "admin_chat.py"
Cohesion: 0.21
Nodes (15): admin_chat(), AdminChatFilters, AdminChatRequest, AdminChatResponse, ChatHistoryItem, _nav_action(), _official_reply(), Any (+7 more)

### Community 124 - "_warm_up"
Cohesion: 0.07
Nodes (33): AbstractEventLoop, 1. Runtime topology, 2. Folder map, 3. Core data flow, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026) (+25 more)

### Community 126 - "services/__init__.py"
Cohesion: 0.22
Nodes (13): opportunity(), Any, services/gsbpm_service.py — GSBPM scoping (SCIL v6 §1) + opportunity to…, Opportunity to practise a competency in the official's office this cycle (SCIL…, Which competencies are in scope under the officer-hours rule, and why., scope_report(), _sp_name(), subprocess_hours() (+5 more)

### Community 127 - "CLAUDE.md"
Cohesion: 0.09
Nodes (21): CLAUDE.md — index & router, Conventions, Feature index, graphify, How to use these docs, Run commands, Admin Dashboard, Code (+13 more)

### Community 128 - "test_chat_endpoint.py"
Cohesion: 0.44
Nodes (9): _chat(), parametrize, End-to-end /chat behaviour per language through the real multilingual…, test_dark_mode_action(), test_my_courses_navigation(), test_questions_answer_in_chat_without_navigating(), test_recommendations(), test_sidebar_section_navigation() (+1 more)

### Community 129 - "seed.py"
Cohesion: 0.23
Nodes (12): hash_password(), Return a bcrypt hash of the plain-text password., _derive_password(), _fetch_officials(), main(), auth/seed.py…, Insert the hardcoded admin user. Returns True if inserted, False if already…, Default password = lowercase(firstName) + last 2 digits of the numeric userId… (+4 more)

### Community 130 - "generate"
Cohesion: 0.12
Nodes (18): build_crosswalk(), build_frac(), build_gsbpm_map(), build_hrms(), build_prerequisites(), dumps(), dumps_records(), find_cycle() (+10 more)

### Community 131 - "_answer_admin"
Cohesion: 0.26
Nodes (30): Endpoints (`/api/v1/admin/console`, all take `?department=&grade=&office=`), _answer_admin(), (reply, navigate_action) for an admin-tier intent., ambiguous(), assignments(), _bullet(), compliance(), _count() (+22 more)

### Community 132 - "karma_engine.py"
Cohesion: 0.18
Nodes (9): ist_date(), ist_day_start_utc(), ist_now(), MonthlyUsage, date, datetime, services/karma_engine.py…, Current and longest run of consecutive IST days with any karma activity. The… (+1 more)

### Community 133 - "datetime"
Cohesion: 0.17
Nodes (14): argparse, datetime, main(), scripts/fetch_live_catalog.py — pull the real iGOT Karmayogi catalogue to disk…, _write(), apply_crosswalk(), build_crosswalk(), _derive_threshold() (+6 more)

### Community 134 - "HybridRecommendationEngine"
Cohesion: 0.12
Nodes (19): _clamp01(), HybridRecommendationEngine, _lex_ref(), _logistic(), ndarray, P(relevant) from the cross-encoder for the top RERANK_TOP_N by RRF; {} if…, (relevance, quality) for a single course scored on its own, with no candidate…, The BM25 score this query gives a *typical matching* course — the median of its… (+11 more)

### Community 135 - "safe_eval"
Cohesion: 0.20
Nodes (10): In / out, RAG Document → Quiz Generator & Grading (quiz ↔ skill gap), Verification, _computed_ok(), expression_numbers(), Evaluate +,-,*,/,**,%, parentheses and a few math functions. Raises ValueError…, Literal numbers used in an expression (for the 'inputs come from the source'…, safe_eval() (+2 more)

### Community 136 - "test_gap_and_recommendation_upgrades.py"
Cohesion: 0.13
Nodes (22): calculate_baseline(), EvidencePayload, BaseModel, Stateless calculator for one competency, on exactly the scoring path the…, assess_competency(), explain_level(), One competency, K/A/U/S fused — the scoring path shared by compute_for_user and…, "Why this level" for one competency, built only from numbers the API already… (+14 more)

### Community 137 - "build_enrollments"
Cohesion: 0.16
Nodes (14): _batch(), build_acbp(), build_enrollments(), build_outcomes(), record(), course_hours(), course_tags(), _fit() (+6 more)

### Community 139 - "QuizSkillImpact.tsx"
Cohesion: 0.15
Nodes (11): Delta(), DIFF_CLASS, DifficultyChip(), QuizQuestionReview(), QuizRecommendations(), signed(), SkillImpactCard(), TYPE_NAMES (+3 more)

### Community 141 - "Karma Points (gamification)"
Cohesion: 0.40
Nodes (4): In / out, Karma Points (gamification), Rules (`RULES` in `karma_engine.py`, served by `GET /karma/rules`), TODOs / edge cases

### Community 143 - "language_service.py"
Cohesion: 0.27
Nodes (9): detect_chat_language(), detect_chat_variant_or_none(), _devanagari_language(), Small, offline language routing for Gyan chat. This deliberately does *not* use…, Supported ISO 639-1 code for a chat message., The variant the *text itself* signals, or None when it carries no signal. Plain…, Pick the reply variant for a message, honouring the UI language picker. A…, resolve_chat_variant() (+1 more)

### Community 144 - "Code"
Cohesion: 0.13
Nodes (13): AI Course Recommendation Engine + Learning Pathways, Code, Connections, In / out, TODOs / edge cases, GapEntry, BaseModel, Structured "why recommended": the gap it closes, the level step it covers and… (+5 more)

### Community 145 - "schemas.py"
Cohesion: 0.36
Nodes (7): ChangePasswordRequest, Config, BaseModel, auth/schemas.py…, RefreshResponse, TokenResponse, UserAuthOut

### Community 147 - "_resolve_competency_state"
Cohesion: 0.33
Nodes (6): _load_db_evidence(), iGOT profile competencyLevel ('Level 3') → 3; missing → 0 (no claim)., The LMS's own EvidenceLog rows for one user (sync — run in a worker thread)., Profile + enrollments + EvidenceLog → one resolved row per role competency.…, _resolve_competency_state(), _self_reported_level()

### Community 148 - "catalogue_store.py"
Cohesion: 0.26
Nodes (12): base64, _build_engine(), Engine + assembler from one catalogue (sync — run in a thread). Course vectors…, Course, _decode_vec(), _encode_vec(), load_embeddings(), ndarray (+4 more)

### Community 150 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.29
Nodes (6): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only, data(), files(), fixture

### Community 151 - "client"
Cohesion: 0.50
Nodes (3): client(), fixture, _u()

### Community 152 - "main-lms-backend/main.py"
Cohesion: 0.06
Nodes (54): fastapi_middleware_cors, get_achievements(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments(), get_enrollments_by_user_id(), get_profile_by_user_id(), get_recommendations() (+46 more)

### Community 153 - "engine"
Cohesion: 0.19
Nodes (14): on_event, Create users_auth table if it doesn't exist yet., _startup(), test_stored_embeddings_are_reused_only_when_text_matches(), test_tpac_boost_depends_on_provenance(), _course(), engine(), _frac() (+6 more)

### Community 156 - "KarmaEventType"
Cohesion: 0.16
Nodes (10): _create_schema(), _create(), Create users_auth and the karma/evidence tables if missing (idempotent)., KarmaEventType, FixedPointsStrategy, KarmaRule, migrate_karma_schema(), Awards the rule's fixed points; eligibility is left to the engine. (+2 more)

### Community 157 - "pipeline.py"
Cohesion: 0.07
Nodes (39): Code, main(), FILE: scripts/eval_media_quiz.py…, caption_regions(), fact_check(), _match(), protect_terms(), FILE: services/media_quiz/fact_check.py… (+31 more)

### Community 158 - "chat_actions.py"
Cohesion: 0.50
Nodes (4): detect_ui_actions(), _mentions(), Detect website theme / language changes requested in any supported chat…, Returns (theme, language): theme in {"dark", "light", "toggle"}, language in…

### Community 159 - "_user_enrolments"
Cohesion: 0.50
Nodes (4): legacy_user_history(), Merge seed enrolments with any runtime mutations., ICatalogSync.fetchUserHistory() — consumed by MockIgotPlatformAdapter., _user_enrolments()

### Community 165 - "document_extractor.py"
Cohesion: 0.14
Nodes (29): Code, CertificateExtractionResult, _clamp_level(), DocumentExtractorService, ExtractedCompetency, ExtractionError, frac_by_id(), frac_dictionary() (+21 more)

## Knowledge Gaps
- **326 isolated node(s):** `setup.sh script`, `name`, `private`, `version`, `type` (+321 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1242 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **47 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Admin console tier` connect `Admin console tier` to `workforce_service.py`, `test_chat_messages.py`, `_answer_admin`, `ChatWidget.tsx`, `get_embedder`, `chatbot.py`, `AdminDashboard.tsx`, `chat`, `language_service.py`, `admin_chat.py`, `UserAuth`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `UserAuth` connect `UserAuth` to `seed.py`, `Code`, `career_readiness`, `karma.py`, `insights.py`, `router.py`, `client`, `main-lms-backend/main.py`, `document_extractor.py`, `test_admin_chat.py`, `rag.py`, `get_learning_pathway`, `test_certificate_evidence.py`, `system_health.py`, `competency.py`, `practice_assessment.py`, `admin_analytics.py`, `_Session`, `admin_chat.py`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `Code` connect `Code` to `domain.ts`, `LearnerDashboard.tsx`, `useLearnerDashboard.ts`, `_answer_admin`, `numpy`, `HybridRecommendationEngine`, `CourseCard.tsx`, `Any`, `.__init__`, `_Session`, `_warm_up`, `BaselineAssembler`, `recommendation_service.py`, `catalogue_store.py`, `get_learning_pathway`, `services/__init__.py`, `MockIgotAdapter`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 81 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 81 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `HybridRecommendationEngine` (e.g. with `7. Mismatches between the mermaid diagram and the code` and `Code`) actually correct?**
  _`HybridRecommendationEngine` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `setup.sh script`, `name`, `private` to the rest of the system?**
  _326 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_live_catalogue.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._