# Graph Report - SIH_IGot  (2026-09-23)

## Corpus Check
- 295 files · ~5,029,859 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 6, .service 2, .example 2)

## Summary
- 3413 nodes · 8659 edges · 158 communities (112 shown, 46 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 956 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0b0073a9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_live_catalogue.py
- useLearnerDashboard.ts
- _Session
- router.py
- package.json
- mock_igot_server.py
- career.py
- ChatWidget.tsx
- karma.py
- Timeline
- ytrelay.py
- test_doc_quiz.py
- Code
- UserAuth
- embedder.py
- generate.py
- gemini_json
- What You Must Do When Invoked
- 3. Core data flow
- test_pathway.py
- lucide-react
- extractors.py
- pipeline.py
- LiveIgotAdapter
- compilerOptions
- ai_tools.py
- 🇮🇳 MoSPI Skill Intelligence Platform
- media_quiz.py
- .__init__
- Admin console tier
- CompetencyCalculator
- react
- AwardResult
- ReplyContext
- test_irt.py
- speech.d.ts
- graphify reference: extra exports and benchmark
- resolve_level
- BaseModel
- compilerOptions
- mock_data_metrics.py
- graphify reference: query, path, explain
- irt_service.py
- .build_study_plan
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
- _learner_competency_state
- media_io.py
- admin_console.py
- MockIgotAdapter
- domain.ts
- items.py
- estimate_uplift
- generate_mock_data.py
- Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)
- _PrerequisiteGate
- lifespan
- rag.py
- get_embedder
- faker
- CourseCard.tsx
- semantic_engine.py
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
- ILearningPlatformAdapter
- Media (Video / Audio / YouTube) → Evidence-Cited Quiz
- datetime
- AssessmentPage.tsx
- workforce_service.py
- test_chat_messages.py
- Mock iGOT Karmayogi Integration (Adapter + mock server + mock data)
- system_health.py
- Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)
- karma_engine.py
- competency.py
- main-lms-backend/main.py
- authApi.ts
- practice_assessment.py
- Deploy: backend on Oracle Cloud, frontend on Vercel
- Decisions log (made without the user)
- get_enriched_courses
- admin_analytics.py
- DashboardCreator
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
- admin_chat.py
- _warm_up
- urllib_request
- _Collect
- CLAUDE.md
- test_chat_endpoint.py
- generate
- _answer_admin
- HybridRecommendationEngine
- safe_eval
- test_gap_and_recommendation_upgrades.py
- build_enrollments
- update.sh
- youtube-access.sh
- Karma Points (gamification)
- vercel.json
- Code
- setup.sh
- services_media_quiz
- services_media_quiz_llm
- services_media_quiz_pipeline
- graphify reference: incremental update and cluster-only
- main_backup.py
- engine
- _create_schema
- Code
- mockdata/domain.py
- services_media_quiz_question_gen
- services_media_quiz_relevance
- test_certificate_evidence.py
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
- `Code` --references--> `WhyThisLevel()`  [INFERRED]
  docs/features/skill-gap-analysis.md → frontend/src/components/dashboard/SkillGapCard.tsx
- `TODOs / edge cases` --references--> `gradeQuiz()`  [INFERRED]
  docs/features/media-quiz-generator.md → frontend/src/services/api.ts
- `7. Mismatches between the mermaid diagram and the code` --references--> `SkillGapReport`  [INFERRED]
  ARCHITECTURE.md → frontend/src/types/domain.ts

## Import Cycles
- None detected.

## Communities (158 total, 46 thin omitted)

### Community 0 - "test_live_catalogue.py"
Cohesion: 0.09
Nodes (27): hashlib, course_url(), The learner-facing page for a course on the real portal:…, _engine(), parametrize, Live iGOT catalogue: record normalisation, competencies_v6 parsing and the KCM…, A wiring mistake must not look like "this official has no enrolments"., Unmapped is not the same as untagged: the course is still indexed, just under a… (+19 more)

### Community 1 - "useLearnerDashboard.ts"
Cohesion: 0.13
Nodes (18): Connections, In / out, Learner Dashboard (frontend shell), TODOs / edge cases, _cache, NO_ACHIEVEMENTS, NO_ENROLLMENTS, NO_GAPS (+10 more)

### Community 2 - "_Session"
Cohesion: 0.15
Nodes (12): Code, KarmaEvent, Immutable ledger entry — one row per karma point award event., KarmaEngine, MonthlyUsage, Dispatches an eventType to its strategy, then applies the shared rules in…, DAILY_LOGIN for today, then any streak milestone the current streak has reached., Seeds an empty ledger from iGOT history; afterwards awards any newly completed… (+4 more)

### Community 3 - "router.py"
Cohesion: 0.06
Nodes (54): bcrypt, Code, fastapi_security, jose, change_password(), _clear_refresh_cookie(), get_me(), login() (+46 more)

### Community 4 - "package.json"
Cohesion: 0.05
Nodes (43): dependencies, lucide-react, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+35 more)

### Community 5 - "mock_igot_server.py"
Cohesion: 0.09
Nodes (60): exception_handler, HTTPException, composite_search(), _course_by_id(), get_admin_roster(), get_assessment_outcomes(), get_competencies(), get_content_state() (+52 more)

### Community 6 - "career.py"
Cohesion: 0.19
Nodes (18): career_readiness(), _dispute_view(), DisputeBody, _ensure_can_view(), my_disputes(), office_ladder(), open_dispute(), Any (+10 more)

### Community 7 - "ChatWidget.tsx"
Cohesion: 0.06
Nodes (66): AdminChatWidget(), AdminChatWidgetProps, CAPABILITIES, SUGGESTION_KEYS, MessageBubble(), NavConfirmBanner(), renderMarkdown(), TypingIndicator() (+58 more)

### Community 8 - "karma.py"
Cohesion: 0.17
Nodes (21): fastapi_concurrency, admin_adjust_karma(), AdminAdjustRequest, _assert_self_or_admin(), award_karma_event(), _award_response(), CbpClaimRequest, claim_cbp_bonus() (+13 more)

### Community 9 - "Timeline"
Cohesion: 0.11
Nodes (21): Performance, build_chunks(), Chunk, Evidence, fmt_ts(), _make_chunk(), FILE: services/media_quiz/evidence.py…, slide_windows: [{"t_start", "t_end", "evidence_ids": [ocr/vlm ids of that… (+13 more)

### Community 10 - "ytrelay.py"
Cohesion: 0.07
Nodes (47): concurrent_futures, _bench(), _benched(), _body_error(), candidates(), _checked(), classify(), _clean() (+39 more)

### Community 11 - "test_doc_quiz.py"
Cohesion: 0.13
Nodes (17): Document quiz: extraction (DOCX, OCR), cited multi-type generation, grading…, _chunks(), _mcq(), parametrize, services/doc_quiz — question types, validator, dedup, selection, calibration,…, test_choice_feedback_uses_option_rationale(), test_courses_for_topics_prefers_competency_courses(), test_fill_blank_and_true_false_rules() (+9 more)

### Community 12 - "Code"
Cohesion: 0.13
Nodes (30): Connections, Code, assess_competency(), rows_for(), tag_id(), _completed_courses(), _education_score(), enrollment_course_id() (+22 more)

### Community 13 - "UserAuth"
Cohesion: 0.08
Nodes (41): AuthBase, fastapi, get_current_user(), auth/dependencies.py…, Decodes the Bearer JWT, looks up the user in auth.db. Raises HTTP 401 for any…, Returns a FastAPI dependency that checks the current user's role. Example:…, require_role(), auth/models.py… (+33 more)

### Community 14 - "embedder.py"
Cohesion: 0.08
Nodes (30): Code, _Embedder, _load(), model_name(), onnx_model_dir(), _OnnxEmbedder, ndarray, FILE: ai/embedder.py… (+22 more)

### Community 15 - "generate.py"
Cohesion: 0.08
Nodes (43): _generate_questions(), Cited, validated, multi-type questions (services/doc_quiz/generate.py) →…, _call(), _computed_ok(), _density(), difficulty_quotas(), DocChunk, excerpt() (+35 more)

### Community 16 - "gemini_json"
Cohesion: 0.08
Nodes (37): base64, LLM providers (Groq multi-key → Gemini), Exception, gemini_json(), gemini_key(), _groq_json(), llm_configured(), ollama_vision_json() (+29 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "3. Core data flow"
Cohesion: 0.11
Nodes (19): 3. Core data flow, _by_score(), _course_summary(), _diagnostic_step(), _fmt_levels(), _interleave_by_level(), Any, BaseModel (+11 more)

### Community 19 - "test_pathway.py"
Cohesion: 0.06
Nodes (32): test_mandatory_courses_always_included_with_badge(), test_why_recommended_describes_the_level_step(), _edge(), _gap(), _kinds_levels(), Skill-gap levels + level-aware recommendations + learning pathways. Runs on a…, Bug #11: the block used to come back in level order, so a weak course sat above…, Bugs #9/#10: relevance and quality were min-maxed inside the shortlist, so the… (+24 more)

### Community 20 - "lucide-react"
Cohesion: 0.10
Nodes (27): KarmaCard(), PassbookRow(), PILL_ORDER, RightSidebar(), RightSidebarProps, EVENT_META, formatPoints(), KarmaEventMeta (+19 more)

### Community 21 - "extractors.py"
Cohesion: 0.11
Nodes (31): add_captions(), flush(), _budget(), describe_keyframes(), guarded(), run_batch(), get_whisper(), lang_of() (+23 more)

### Community 22 - "pipeline.py"
Cohesion: 0.20
Nodes (11): main(), FILE: scripts/eval_media_quiz.py…, Media → quiz pipeline (video, audio, YouTube) for the Assessment Studio. Entry…, NotLearnable, ValueError, FILE: services/media_quiz/pipeline.py…, The pre-fix behaviour: assume a narrated lecture, transcribe everything, ask…, run_naive() (+3 more)

### Community 23 - "LiveIgotAdapter"
Cohesion: 0.10
Nodes (20): Live iGOT (the real portal), _as_list(), _first_str(), LiveIgotAdapter, normalise_course(), Any, AsyncClient, Pooled client per event loop — the warm-up thread runs its own. (+12 more)

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
Cohesion: 0.11
Nodes (31): fastapi_responses, ImportError, importlib_util, _cached_result(), capabilities(), _importable(), MediaMetadata, MediaQuizQuestion (+23 more)

### Community 28 - ".__init__"
Cohesion: 0.15
Nodes (9): _parse_level(), Stable hash of a course's embedded text — decides whether a stored vector is…, Bayesian shrinkage toward global prior mean. Returns None if either input is…, Level 3' / 3 / '3' → 3; anything outside 1..5 → None., `catalog` / `frac` / `crosswalk` are the lists served by the mock iGOT server…, Fix the quality scale to the catalogue instead of to the shortlist. Quality…, Stored vectors whose text hash still matches; encode (disk-memoised) the rest., _shrunk_rating() (+1 more)

### Community 29 - "Admin console tier"
Cohesion: 0.15
Nodes (26): difflib, Admin console tier, AdminTab, behind_facts(), _clean(), competency_names(), department_facts(), find_officials() (+18 more)

### Community 30 - "CompetencyCalculator"
Cohesion: 0.29
Nodes (6): CompetencyCalculator, datetime, Maps FRAC types from the JSON to calculation categories., Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table. Only adjacent…, Calculates the baseline score (b_k) and returns (score, confidence_tag).…, test_missing_channels_do_not_drag_the_score_to_zero()

### Community 31 - "react"
Cohesion: 0.05
Nodes (78): `frontend/src/`, Accessibility preferences, GIGW compliance & accessibility (frontend chrome), Other GIGW / WCAG work applied across the app, Statutory pages, The chrome, and where it comes from, TODO, Verifying a change here (+70 more)

### Community 32 - "AwardResult"
Cohesion: 0.12
Nodes (14): AdminAdjustmentStrategy, AwardResult, CompletionKarmaStrategy, FixedPointsStrategy, IKarmaStrategy, ABC, Computes the base points for an event (before the engine's idempotency, per-day…, Awards the rule's fixed points; eligibility is left to the engine. (+6 more)

### Community 33 - "ReplyContext"
Cohesion: 0.16
Nodes (19): importlib, Flat numeric profile features from skill-gap dicts ({skillName, domain,…, vectorize_profile(), Any, Everything a reply template may personalise, built once per chat request., ReplyContext, _by_page(), _gap_lines() (+11 more)

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
Cohesion: 0.26
Nodes (16): Single source of truth for an official's level on one competency. Every…, resolve_level(), fuse_channels(), Weighted mean over the K/A/U/S channels that carry evidence (None → absent)., _assess(), SCIL v6 §3 evidence channels K/A/U/S (knowledge, application, utility,…, _row(), test_confirmed_use_is_a_floor_unconfirmed_is_not() (+8 more)

### Community 38 - "BaseModel"
Cohesion: 0.10
Nodes (18): field_validator, CompetencyOut, CompositeSearchRequest, ContentStateRequest, CourseOut, EnrolPayload, ingest_telemetry(), JobProfileOut (+10 more)

### Community 39 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 40 - "mock_data_metrics.py"
Cohesion: 0.31
Nodes (10): _get(), live_metrics(), _login(), main(), offline_metrics(), _pct(), Mock-data quality metrics — run before/after regenerating mock data. cd main-…, Admin bearer header; retried while the backend (--reload) restarts. (+2 more)

### Community 41 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 42 - "irt_service.py"
Cohesion: 0.22
Nodes (10): DiagnosticSessions, fisher_information(), next_item(), p_correct(), public_item(), Any, services/irt_service.py — Tier-1 Bayesian 2PL posterior + adaptive diagnostic…, What the learner sees: no answer key, no parameters. (+2 more)

### Community 43 - ".build_study_plan"
Cohesion: 0.25
Nodes (6): absorb(), add_step(), advance(), open_ladders(), Orders the required rungs of several pathways into one sequence. SCIL v6 §5…, Does taking `course_id` complete this ladder's next rung?

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
Nodes (44): 7. Mismatches between the mermaid diagram and the code, Base, Conventions, enum, Admin, Assessment, AssessmentSkillMapping, BaseUser (+36 more)

### Community 54 - "test_admin_chat.py"
Cohesion: 0.09
Nodes (32): fastapi_testclient, ask(), client(), fixture, Gyan on the admin console: routers/admin_chat.py end to end, with the roster,…, Both classifiers answer fixed (intent, confidence) pairs — no embedder., stub_intents(), test_a_department_named_in_the_message_scopes_the_answer() (+24 more)

### Community 58 - "opportunity"
Cohesion: 0.24
Nodes (13): opportunity(), Any, services/gsbpm_service.py — GSBPM scoping (SCIL v6 §1) + opportunity to…, Opportunity to practise a competency in the official's office this cycle (SCIL…, Which competencies are in scope under the officer-hours rule, and why., scope_report(), _sp_name(), subprocess_hours() (+5 more)

### Community 60 - "_learner_competency_state"
Cohesion: 0.09
Nodes (25): Connections, In / out, Skill Gap Analysis (evidence-based competency baselines), TODOs / edge cases, _ensure_can_view(), get_achievements_by_user_id(), get_admin_roster(), get_frac_competencies() (+17 more)

### Community 61 - "media_io.py"
Cohesion: 0.05
Nodes (70): BaseException, Getting past the bot check, _Attempt, _blocked_message(), _cache_dir(), cache_load(), _cache_root(), cache_store() (+62 more)

### Community 62 - "admin_console.py"
Cohesion: 0.08
Nodes (63): csv, AdminDailySnapshot, One row per calendar day (UTC): the workforce headline numbers plus the same…, An admin assigning courses (a training plan) to a department or a list of…, A reminder sent by an admin to an official behind on mandatory (ACBP) training., TrainingAssignment, TrainingNudge, Any (+55 more)

### Community 63 - "MockIgotAdapter"
Cohesion: 0.06
Nodes (40): Connections, Code, GSBPM scope — the 80% officer-hours rule (SCIL v6 §1), Noticed but out of scope (not fixed), _competencies(), MockIgotAdapter, fetch(), fetch() (+32 more)

### Community 64 - "domain.ts"
Cohesion: 0.02
Nodes (110): Code, Responsive layout (phones 360–430px, tablets 768–1024px), LearnerDashboard, CareerReadinessCard(), Props, TIER_LABEL, CompetencyOverviewTable(), LevelPips() (+102 more)

### Community 65 - "items.py"
Cohesion: 0.20
Nodes (30): ast, Document question pipeline (`main-lms-backend/services/doc_quiz/`), TODOs / edge cases, _build_review(), Type-aware answer review, missed questions first. Each wrong answer gets…, accepted_texts(), answer_display(), _choice_set() (+22 more)

### Community 66 - "estimate_uplift"
Cohesion: 0.07
Nodes (44): Cross-competency prerequisite DAG (SCIL v6 §5, B4), find_cycle(), infer_edges(), _node(), _norm_sf(), _ols(), Any, ndarray (+36 more)

### Community 67 - "generate_mock_data.py"
Cohesion: 0.17
Nodes (25): build_catalog(), build_item_bank(), build_offices(), build_officials(), build_role(), build_workplace_evidence(), _course_id(), _covariates() (+17 more)

### Community 68 - "Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)"
Cohesion: 0.20
Nodes (9): Measured uplift → coverage learning + training effectiveness (SCIL v6 §6, B5), Opportunity to practise (SCIL v6 §4), Reference data loading, TODOs / limits, Used by the admin console, Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight), StudyPlanSummary(), Attach per-course measured uplift (uplift_service.estimate_uplift) — SCIL v6 §6. (+1 more)

### Community 69 - "_PrerequisiteGate"
Cohesion: 0.33
Nodes (3): _PrerequisiteGate, Cross-competency prerequisite DAG for build_study_plan (SCIL v6 §5, B4). A rung…, Edges that changed or annotate the plan: ordered (waited, then met), blocked,…

### Community 70 - "lifespan"
Cohesion: 0.33
Nodes (7): lifespan(), _load_json(), _load_json_from_dir(), Any, FastAPI, Load all datasets into memory once at startup, so no request touches the file…, Load a JSON file from ROOT_DIR. Raises RuntimeError on missing file.

### Community 71 - "rag.py"
Cohesion: 0.07
Nodes (61): Code, Code, Connections, Personalised feedback (`items.feedback`), ErrorResponse, _generate_overview(), learning_chat(), LearningChatMessage (+53 more)

### Community 72 - "get_embedder"
Cohesion: 0.09
Nodes (29): argparse, encode_cached(), get_embedder(), Lazily loaded embedder for `role` ("chat" | "catalog"); thread-safe., L2-normalised float32 embeddings of a fixed corpus, memoised on disk under…, CorpusIndex, An independently-tuned prototype index over `ai/<dirname>/<lang>.json`. The…, (best_intent, confidence) on the same cosine scale as classify_intent. (+21 more)

### Community 74 - "CourseCard.tsx"
Cohesion: 0.18
Nodes (14): BADGE_STYLE, CourseCard(), CourseCardProps, getSourceStyle(), MatchScoreBar(), MatchScoreBarProps, MODALITY_LABEL, SOURCE_STYLES (+6 more)

### Community 75 - "semantic_engine.py"
Cohesion: 0.15
Nodes (16): collections, io, _correct_tokens(), _ensure_prototypes(), load_corpus(), FILE: ai/semantic_engine.py…, Encode all prototype phrases once, via the shared singleton embedder., Per-intent confidence for `query`, searched within `lang`'s pool only. (+8 more)

### Community 76 - "chatbot.py"
Cohesion: 0.15
Nodes (27): Code, TabType, classify_intent(), Returns (best_intent, confidence). ("general", 0.0) if the embedder is…, chat(), ChatRequest, ChatResponse, detect_intent_keyword() (+19 more)

### Community 77 - "api.ts"
Cohesion: 0.03
Nodes (130): Frontend, AdminDashboard, AdminActions(), AssignForm(), when(), AdminFilterBar(), ExportButton(), facetLabels() (+122 more)

### Community 87 - "catalogue_source.py"
Cohesion: 0.12
Nodes (20): get_enrollments_by_user_id(), Active/in-progress enrollments for a learner by iGOT userId., _apply_crosswalk(), configured_source(), fetch(), is_live(), live_course_url(), _load_disk_catalogue() (+12 more)

### Community 88 - "CertificateUploadZone.tsx"
Cohesion: 0.31
Nodes (7): CertificateUploadZone(), clean(), STATUS_CHIP, CertificateStatus, CertificateSubmission, fetchMyCertificates(), uploadCertificate()

### Community 89 - "proficiency_service.py"
Cohesion: 0.16
Nodes (17): cluster_of(), cohort_prior(), expected_shortfall(), months_between(), office_phase(), _phi(), proficiency_state(), Any (+9 more)

### Community 90 - "post"
Cohesion: 0.11
Nodes (26): contextlib, fastapi_middleware_cors, post(), enroll_user(), EnrollRequest, get_catalog(), get_frac_dictionary(), get_job_profiles() (+18 more)

### Community 91 - "ILearningPlatformAdapter"
Cohesion: 0.11
Nodes (15): 2. Folder map, 4. Persistence, 5. Tech stack, 6. Design patterns actually implemented, Architecture — MoSPI AI Skill Intelligence Platform (SIH 2026), `main-lms-backend/` — FastAPI orchestrator, `mock-igot-server/` — external-system simulator, ILearningPlatformAdapter (+7 more)

### Community 92 - "Media (Video / Audio / YouTube) → Evidence-Cited Quiz"
Cohesion: 0.13
Nodes (16): How well it actually works, In / out, Media (Video / Audio / YouTube) → Evidence-Cited Quiz, Pipeline, Setup, The relay tier, TODOs / edge cases, Verification (+8 more)

### Community 94 - "datetime"
Cohesion: 0.16
Nodes (16): datetime, Difficulty calibration (`services/doc_quiz/calibration.py`), Stamp each item with its content key and its response-calibrated difficulty.…, _with_calibration(), calibrate(), calibrate_items(), difficulty_from_b(), load_stats() (+8 more)

### Community 95 - "AssessmentPage.tsx"
Cohesion: 0.05
Nodes (67): Gyan hand-off (document → quiz or Learning Mode, no second upload), Frontend, AssessmentPage, CONTENT_LABEL, MediaAnalysisCard(), MediaAnswerReview(), pct(), QuestionEvidence() (+59 more)

### Community 96 - "workforce_service.py"
Cohesion: 0.24
Nodes (16): How the parts work, _Phi(), _as_date(), capability_risk(), cell(), foresight(), _level(), _p_capable() (+8 more)

### Community 97 - "test_chat_messages.py"
Cohesion: 0.14
Nodes (22): ChatHistoryItem, BaseModel, RecommendationContext, SkillGapContext, Loads a language's template table on first use ("or" lives in or_.py; `or` is a…, templates(), sample_request(), _alternatives() (+14 more)

### Community 98 - "Mock iGOT Karmayogi Integration (Adapter + mock server + mock data)"
Cohesion: 0.50
Nodes (4): Connections, In / out, Mock iGOT Karmayogi Integration (Adapter + mock server + mock data), TODOs / edge cases

### Community 99 - "system_health.py"
Cohesion: 0.17
Nodes (24): is_embedder_ready(), Non-blocking check — True only if the role's model is already loaded., is_semantic_engine_ready(), health(), Liveness + warm-up state. Cheap: use it as the Render health check / keep-alive…, admin_chat_mode(), get, chat_mode() (+16 more)

### Community 100 - "Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)"
Cohesion: 0.50
Nodes (4): Cold start for UNASSESSED competencies, Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8), Foresight, Proficiency belief with dated decay

### Community 101 - "karma_engine.py"
Cohesion: 0.15
Nodes (14): KarmaEventType, KarmaMonthlyUsage, Rolling monthly counter for non-CBP COURSE_COMPLETION events. Enforces the…, ist_date(), ist_day_start_utc(), ist_now(), KarmaRule, date (+6 more)

### Community 102 - "competency.py"
Cohesion: 0.09
Nodes (33): get_db(), auth/database.py…, FastAPI dependency — `db: Session = Depends(get_db)`; closed after the request., CertificateSubmission, One uploaded certificate (routers/competency.py). On upload each extracted…, CertificateReview, certificates_for_review(), _find() (+25 more)

### Community 103 - "main-lms-backend/main.py"
Cohesion: 0.08
Nodes (33): asyncio, dataclasses, functools, httpx, json, logging, adapters/igot_adapter.py — iGOT Platform Adapter…, adapters/live_igot_adapter.py — the REAL iGOT Karmayogi platform (read-only)… (+25 more)

### Community 104 - "authApi.ts"
Cohesion: 0.13
Nodes (23): ChatEntry, LearningChat(), LearningChatProps, API_BASE_URL, AuthProvider(), mapRole(), extractError(), getMe() (+15 more)

### Community 105 - "practice_assessment.py"
Cohesion: 0.09
Nodes (35): Practice ability (`main-lms-backend/services/practice_assessment.py`), bump(), courses_for_topics(), link_competency(), media_question_difficulty(), next_difficulty(), normalise_difficulty(), p_correct() (+27 more)

### Community 106 - "Deploy: backend on Oracle Cloud, frontend on Vercel"
Cohesion: 0.22
Nodes (8): 1. Create the VM (Oracle Cloud console), 2. Pick the API hostname, 3. Set up the VM, 4. Frontend on Vercel, Deploy: backend on Oracle Cloud, frontend on Vercel, Troubleshooting, Updating: just `git push` to `main`, YouTube links on the VM

### Community 108 - "Decisions log (made without the user)"
Cohesion: 0.25
Nodes (6): Before / after metrics, Could not do / blocked, Decisions log (made without the user), SCIL v6 — mock data + blocked features: progress report, Status, Catalogue duration in hours, or None for a course not in the catalogue.

### Community 109 - "get_enriched_courses"
Cohesion: 0.40
Nodes (6): _course_tags(), _enriched_view(), get_enriched_courses(), _matches_filters(), Sunbird-style filters: each key → value or list of accepted values., The catalogue in the older "enriched" shape. Query params:…

### Community 110 - "admin_analytics.py"
Cohesion: 0.08
Nodes (48): Backend, overview(), _competency_metrics(), daily_metrics(), by(), dept_compliance(), emerging_skills(), facets() (+40 more)

### Community 112 - "DashboardCreator"
Cohesion: 0.16
Nodes (4): AdminDashboardCreator, DashboardCreator, OfficialDashboardCreator, TrainerDashboardCreator

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
Cohesion: 0.07
Nodes (40): needs_ocr(), _ocr_engine(), ocr_pdf_pages(), OcrUnavailable, ndarray, RuntimeError, FILE: services/doc_quiz/extract.py…, (text in reading order, mean confidence, weak lines dropped). (+32 more)

### Community 123 - "admin_chat.py"
Cohesion: 0.16
Nodes (19): low_confidence_threshold(), admin_chat(), AdminChatFilters, AdminChatRequest, AdminChatResponse, ChatHistoryItem, _nav_action(), BaseModel (+11 more)

### Community 124 - "_warm_up"
Cohesion: 0.08
Nodes (32): AbstractEventLoop, 1. Runtime topology, Connections, Gyan — Multilingual Chat Assistant, In / out, TODOs / edge cases, Workforce snapshot, _build_engine() (+24 more)

### Community 127 - "CLAUDE.md"
Cohesion: 0.07
Nodes (26): CLAUDE.md — index & router, Feature index, graphify, How to use these docs, Run commands, Admin Dashboard, Code, TODOs / edge cases (+18 more)

### Community 128 - "test_chat_endpoint.py"
Cohesion: 0.44
Nodes (9): _chat(), parametrize, End-to-end /chat behaviour per language through the real multilingual…, test_dark_mode_action(), test_my_courses_navigation(), test_questions_answer_in_chat_without_navigating(), test_recommendations(), test_sidebar_section_navigation() (+1 more)

### Community 130 - "generate"
Cohesion: 0.12
Nodes (18): build_crosswalk(), build_frac(), build_gsbpm_map(), build_hrms(), build_prerequisites(), dumps(), dumps_records(), find_cycle() (+10 more)

### Community 131 - "_answer_admin"
Cohesion: 0.25
Nodes (32): Endpoints (`/api/v1/admin/console`, all take `?department=&grade=&office=`), _answer_admin(), _official_reply(), (reply, navigate_action) for an admin-tier intent., ambiguous(), assignments(), _bullet(), compliance() (+24 more)

### Community 134 - "HybridRecommendationEngine"
Cohesion: 0.11
Nodes (20): _clamp01(), _CourseDoc, HybridRecommendationEngine, _lex_ref(), _logistic(), ndarray, P(relevant) from the cross-encoder for the top RERANK_TOP_N by RRF; {} if…, (relevance, quality) for a single course scored on its own, with no candidate… (+12 more)

### Community 135 - "safe_eval"
Cohesion: 0.29
Nodes (7): In / out, RAG Document → Quiz Generator & Grading (quiz ↔ skill gap), Verification, Evaluate +,-,*,/,**,%, parentheses and a few math functions. Raises ValueError…, safe_eval(), ev(), test_safe_eval()

### Community 136 - "test_gap_and_recommendation_upgrades.py"
Cohesion: 0.11
Nodes (23): calculate_baseline(), EvidencePayload, BaseModel, Stateless calculator for one competency, on exactly the scoring path the…, explain_level(), "Why this level" for one competency, built only from numbers the API already…, correct_supervisor_rating(), rater_leniency_offsets() (+15 more)

### Community 137 - "build_enrollments"
Cohesion: 0.16
Nodes (14): _batch(), build_acbp(), build_enrollments(), build_outcomes(), record(), course_hours(), course_tags(), _fit() (+6 more)

### Community 141 - "Karma Points (gamification)"
Cohesion: 0.40
Nodes (4): In / out, Karma Points (gamification), Rules (`RULES` in `karma_engine.py`, served by `GET /karma/rules`), TODOs / edge cases

### Community 144 - "Code"
Cohesion: 0.12
Nodes (13): AI Course Recommendation Engine + Learning Pathways, Code, Connections, In / out, TODOs / edge cases, GapEntry, Structured "why recommended": the gap it closes, the level step it covers and…, SCIL v6 §4 tie-break: gaps whose priority is within OPPORTUNITY_TIE_BAND (10%)… (+5 more)

### Community 150 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.29
Nodes (6): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only, data(), files(), fixture

### Community 152 - "main_backup.py"
Cohesion: 0.08
Nodes (38): get_achievements(), get_achievements_by_user_id(), get_admin_roster(), get_enrollments(), get_enrollments_by_user_id(), get_profile_by_user_id(), get_recommendations(), get_recommendations_by_user_id() (+30 more)

### Community 153 - "engine"
Cohesion: 0.26
Nodes (11): test_stored_embeddings_are_reused_only_when_text_matches(), test_tpac_boost_depends_on_provenance(), _course(), engine(), _frac(), fixture, Hashed bag-of-words → L2-normalised vector. Shared words ⇒ positive cosine., _StubEmbedder (+3 more)

### Community 156 - "_create_schema"
Cohesion: 0.50
Nodes (5): _create_schema(), _create(), Create users_auth and the karma/evidence tables if missing (idempotent)., migrate_karma_schema(), Idempotent upgrade for databases created before the daily-cap rework: adds…

### Community 157 - "Code"
Cohesion: 0.10
Nodes (24): Code, caption_regions(), fact_check(), _match(), protect_terms(), FILE: services/media_quiz/fact_check.py…, Translate strings with glossary terms protected as ⟦Tn⟧. Returns (translations…, Fact-check one answer. Returns (review dict, summary bucket) where the bucket… (+16 more)

### Community 165 - "test_certificate_evidence.py"
Cohesion: 0.09
Nodes (38): Code, CertificateExtractionResult, _clamp_level(), DocumentExtractorService, ExtractedCompetency, ExtractionError, frac_by_id(), frac_dictionary() (+30 more)

## Knowledge Gaps
- **326 isolated node(s):** `setup.sh script`, `name`, `private`, `version`, `type` (+321 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1212 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **46 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Admin console tier` connect `Admin console tier` to `workforce_service.py`, `test_chat_messages.py`, `_answer_admin`, `ChatWidget.tsx`, `get_embedder`, `semantic_engine.py`, `chatbot.py`, `api.ts`, `admin_chat.py`, `admin_console.py`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `UserAuth` connect `UserAuth` to `router.py`, `system_health.py`, `test_certificate_evidence.py`, `career.py`, `main-lms-backend/main.py`, `competency.py`, `karma.py`, `rag.py`, `admin_analytics.py`, `models/models.py`, `test_admin_chat.py`, `catalogue_source.py`, `main_backup.py`, `admin_chat.py`, `_learner_competency_state`, `admin_console.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `Code` connect `Code` to `domain.ts`, `useLearnerDashboard.ts`, `estimate_uplift`, `_answer_admin`, `Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)`, `_PrerequisiteGate`, `HybridRecommendationEngine`, `CourseCard.tsx`, `.build_study_plan`, `.__init__`, `_learner_competency_state`, `models/models.py`, `BaselineAssembler`, `3. Core data flow`, `opportunity`, `_warm_up`, `MockIgotAdapter`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 81 inferred relationships involving `UserAuth` (e.g. with `Code` and `get_current_user()`) actually correct?**
  _`UserAuth` has 81 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `HybridRecommendationEngine` (e.g. with `7. Mismatches between the mermaid diagram and the code` and `Code`) actually correct?**
  _`HybridRecommendationEngine` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `setup.sh script`, `name`, `private` to the rest of the system?**
  _326 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_live_catalogue.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08817204301075268 - nodes in this community are weakly interconnected._