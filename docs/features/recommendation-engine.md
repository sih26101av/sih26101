# AI Course Recommendation Engine + Learning Pathways

Level-aware hybrid retrieval: prioritise gaps, filter the catalogue by FRAC tag
**and FRAC level**, fuse dense and sparse rankings with RRF, re-score by quality —
then turn the ranked courses into a step-by-step learning path per competency and
one study order across all gaps.

**Scores are absolute.** Relevance and quality are both measured against the
catalogue, never min-maxed inside the shortlist, so a course scores the same
whatever it is shown next to, two gaps' scores are comparable, and the weakest
candidate of a pool is no longer forced to 0.000. The list is shown best match
first; the order to *study* the courses in is the pathway's job, not this list's.

## Code

`main-lms-backend/services/recommendation_service.py` — `HybridRecommendationEngine`
(singleton, built once in `main.py::_warm_up` as `_rec_engine`).

- `__init__(catalog_path, frac_path, catalog=None, frac=None, crosswalk=None,
  precomputed_embeddings=None)` —
  takes the catalogue / FRAC set / crosswalk **as served by the mock iGOT server**
  (`main._warm_up` loads them through `MockIgotAdapter`); a list not given is read
  from the same generated file on disk (`catalog_source` = `adapter` | `disk`).
  Loads the FRAC set into `_frac_map` (incl. `levels`: the L1–L5 proficiency
  descriptors from `children`), parses the catalogue into `_catalog` + `_comp_index` + `_by_id`, builds
  BM25 over `title + description`, encodes the corpus with `ai.embedder` (reusing
  `precomputed_embeddings = {courseId: (text_hash, vec)}` from the DB where the hash
  still matches — `_corpus_embeddings`, `embedding_stats`, `course_embeddings()`), keeps the
  matrix as `_embeddings` and in a `faiss.IndexFlatIP`, and builds the crosswalk
  anchors (`_xw_ids`, `_xw_emb`, `_xw_threshold`).
- `_parse_catalog` — parses the JSON-string `competencies_v3` tags **including
  `competencyLevel`** into `_CourseDoc.comp_levels {compId: 1..5}`, duration
  (`duration` is seconds), `modality` / `fmt`, TPAC provenance (`verified` when
  `is_tpac: true`, `none` when the catalogue says `is_tpac: false`, `inferred`
  from the NSSTA creator name only when the field is absent), quality fields kept
  as `None` if missing.
- Accessors: `course_comp_levels()` (feeds `BaselineAssembler`),
  `levels_available(comp)`, `level_descriptor(comp, level)`, `course_hours(courseId)`
  (the learner enrollments endpoint uses it for course hours).
- `crosswalk(comp_id, name)` — maps a role competency to the catalogue FRAC
  competency that serves it: `exact` when the id is tagged in the catalogue, else an
  explicit entry in `data/frac_crosswalk.json` → `curated_crosswalk` (with its
  `confirmed` flag; every rule there is unconfirmed), else the nearest anchor by name embedding if it beats `_xw_threshold` = the 95th
  percentile of similarities between **distinct** FRAC competencies (derived from
  the FRAC set, not tuned) → `semantic_crosswalk` (unconfirmed), else `None`.
- `calculate_gaps(baselines, targets, names, confidence, catalogue_ids)` —
  **Stage 0**: `priority = gap · target/5`. Competencies missing from `baselines`
  (UNASSESSED) are skipped — "no evidence" is not "level 0".
- `_retrieve_for_gap(gap, top_k, levels)` — **Stage 1** FRAC-tag filter restricted
  to `levels`; **Stage 2** exact cosine over the candidate pool + BM25, RRF
  `1/(60+rank_dense) + 1/(60+rank_sparse)`, TPAC boost by provenance
  (`_TPAC_BOOST`: verified 1.25×, inferred 1.10×, none 1×). Query = official
  FRAC name + description of `gap.catalogue_key` (cached per competency in
  `_query_cache`). No tagged courses at all → full-corpus FAISS `semantic_fallback`.
- `_relevance(idx, comp, q_emb, bm25, lex_ref, rrf_raw)` / `_blend_relevance` —
  **the relevance scale**, absolute in [0,1]:
  `0.45·semantic + 0.20·lexical + 0.35·fusion`.
  *semantic* = `logistic((cos − µ) / σ)` of the cosine to the FRAC anchor against
  the **untagged null** (`_untagged_null`: mean/std of the cosines of the courses
  *not* tagged with the competency) — 0.5 means "as close as a typical untagged
  course"; *lexical* = `b / (b + _lex_ref(bm25))`, saturating at the corpus median
  of the query's positive BM25 scores; *fusion* = `rrf / _RRF_MAX` where
  `_RRF_MAX = 2/(k+1)` is the score of a course ranked 1st on both lists.
  With no pool behind the course — a `semantic_fallback`, or an ACBP course
  scored on its own (`_score_one`) — the fusion term is dropped and the other two
  are re-weighted to carry the whole score.
- `_score_candidates(gap, levels, exclude_ids)` — Stages 1–3 for one gap:
  `final = 0.6·relevance + 0.4·quality`, `courseLevel`, `tagSupported`, reasons,
  `modality`, `why` (`_why`). **Stage 2b** `_cross_encoder_norm`: when
  `ENABLE_CROSS_ENCODER=1`, `ai/reranker.py` scores the top 20 by RRF with a
  multilingual cross-encoder (`cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`,
  ONNX in `ai/.cache/onnx/<model>/` or sentence-transformers;
  `python scripts/download_model.py --reranker` fetches it). The logits go
  through a **sigmoid** (their natural calibration), and only the re-ranked head
  is blended: `0.5·relevance + 0.5·P(relevant)`. A course the re-ranker never
  looked at keeps its own relevance instead of being zeroed for it. Off by
  default, falls back silently (`reranked` is `null`).
- `_why(gap, doc, course_level, uplift, tag_supported)` — structured "why recommended":
  `{gap{competencyId,competencyName,currentLevel,targetLevel,gap},
  levelStep{from,to,kind: next_step|on_the_way|stretch|untagged_level|mandatory},
  badges[{key: mandatory|tpac_verified|tpac_inferred|measured_improvement|under_review,label}],
  summary}`.
- `order_gaps_by_opportunity(gaps, {compId: Low|Medium|High})` — gaps whose priority
  is within `OPPORTUNITY_TIE_BAND` (10%) are near-ties, and the one the office
  uses more this cycle goes first (adjacent swaps). Ordinal only.
- `mandatory_recommendations(mandatory, exclude_ids, gaps, names)` — ACBP courses as
  `RecommendationResult(mandatory=True, matchType="acbp_mandatory")` with a
  Mandatory badge; courses outside the catalogue are still listed from ACBP fields.
  They are **scored like any other course** (`_score_one`) instead of the flat
  `finalScore = 1.0` they used to claim — an ACBP course outside the catalogue is
  embedded from its title and takes `_neutral_quality()`. Listed APAR-linked
  first, then best match; the Mandatory badge, not a fabricated score, is what
  pins them to the top (the card says so).
- `_spread_modalities(ordered, k)` — per-gap picks. A candidate in an unseen format
  (`self_paced | classroom | virtual_lab`) replaces a repeat when it is at the
  same level, within the next 3, and within 0.15 finalScore. Picks keep
  their interleaved order until `_by_score` re-orders the block for display.
  `_score_candidates` itself still returns content-supported tags first, then
  `finalScore` — `build_pathway` reads that order.
- `_untagged_null(comp, q_emb)` — (median, mean, std) of the cosines of the
  courses *not* tagged with the competency: the null distribution for "an
  unrelated course", derived from the data with no tuned constant. The median is
  `_tag_support_threshold` (a tagged course at or below it has
  `tagSupported=False` — its author-declared tag isn't backed by content →
  preferred last, flagged for review); the mean and std calibrate the semantic
  half of the relevance score. Cached per competency.
- `set_measured_uplift(estimates)` / `course_meta()` — SCIL v6 §6 coverage
  learning: per-course measured uplift from outcome data
  (`uplift_service.estimate_uplift`, run at startup). Results carry
  `measuredUplift` / `upliftFlag`; an uplift-flagged course is ordered like an
  unsupported tag (last resort at its level, reason note) — see
  [workforce-insights.md](workforce-insights.md). Not blended into `finalScore`.
- `_quality_score(doc)` — **Stage 3** `0.35·completion + 0.35·rating +
  0.20·log-pop + 0.10·tpac_flag` on an **absolute catalogue-wide scale**
  (`_build_quality_norms`, run once at build time): completion is the published
  rate as-is, rating is the Bayesian-shrunk stars mapped 1..5 → 0..1, popularity
  is `log1p(enrolments)/log1p(p95 enrolments)` capped at 1. A course *missing* a
  field takes the catalogue mean of that component — ~9% of the catalogue has no
  rating or enrolment data at all and used to score 0 for it.
  `_neutral_quality()` is the same average for a course the catalogue does not
  have. The `shortlist` argument is still accepted and ignored.
- `get_recommendations(gaps, limit_per_gap, enrolled_ids)` — level-gated: only
  courses with `current < courseLevel ≤ target` (nearest level above target as a
  flagged stretch if the band is empty). Level interleaving and the modality
  spread choose *which* courses to show (a ladder across levels, mixed formats),
  then `_by_score` orders the block **best match first** so the list agrees with
  the score printed on each card; a flagged tag / ~0 measured uplift still sorts
  last. Blocks concatenated in gap-priority order, no global re-sort.
- `build_pathway(comp_id, comp_name, current_level, target_level, confidence, basis,
  evidence_level, completed_ids, in_progress, role_comp_id, crosswalk)` — **Stage 4**:
  one course per FRAC level from current+1 to target. Step kinds:
  `diagnostic` (UNASSESSED / LOW / self-reported — take the practice assessment
  first), `bridge` (self-reported levels only: rungs between evidence and claim,
  optional, not in `totalHours`), `course`, `continue` (in-progress course at that
  level wins), `stretch` (catalogue hole → next level's course covers it),
  `optional` (target met → one course further). Completed courses are never
  suggested. Status `ready | partial | no_content | met`; reports `coverageGaps`,
  `unreachableLevels`, `tagReviewFlags`, `message`.
- `build_study_plan(pathways, budget_hours, mandatory, completed_ids, in_progress,
  classroom_cap_hours, prerequisites, current_levels)` — **Stage 4b**, SCIL v6 §5:
  1. **Mandatory ACBP courses first** (APAR-linked). They are force-included
     even beyond the budget (`overBudget: true`). A completed one is listed as
     `status: completed` and not scheduled. A ladder whose next rung a mandatory
     course satisfies advances with it.
  2. **Greedy over the frontier.** Repeatedly take the frontier course with the
     highest Σ priority × levels covered / hours. A course that is the next rung
     for two gaps counts for both and advances both (the other pathway's step is
     swapped to it in place). A later rung already in the plan (e.g. a mandatory
     course) is absorbed for free, so no course is taken twice (`absorb()`).
     Ladder order is the within-competency prerequisite chain.
     `_PrerequisiteGate` adds the cross-competency DAG (B4).
  3. **Blocking.** A course that doesn't fit the budget
     (`over budget`), or a classroom course that would exceed
     `classroom_cap_hours` (`classroom cap`), blocks its ladder; the ladder is
     listed under `deferred` with that reason.
  4. **Diagnostics.** UNASSESSED ladders are not scheduled; they're listed in
     `diagnostics`.
  5. **Opportunity tie-break (SCIL v6 §4).** Frontier courses within
     `OPPORTUNITY_TIE_BAND = 0.10` of the best gain/hour are near-ties. Among
     them, the one advancing the gap with the highest
     `pathway["opportunity"]["level"]` goes first. This is ordinal only: never a
     multiplier, and it never hides a gap.

  Steps carry `kind` (rung kind or `mandatory`), `mandatory`, `modality`,
  `opportunity` and `selectedBy` (`gain_per_hour` | `opportunity_tie_break` |
  `mandatory_acbp`); see [workforce-insights.md](workforce-insights.md).
  **No approximation guarantee is claimed**: the (1−1/e) bound does not hold for
  ratio-greedy under a budget with precedence constraints.
- `CLASSROOM_CAP_HOURS_PER_QUARTER = 30.0` is five 6-hour training days away
  from the desk per quarter. It applies only to the default quarterly plan.
- Pydantic outputs: `GapEntry` (+ `confidence`, `catalogueId`, `catalogue_key`),
  `RecommendationResult` (+ `courseLevel`, `tagSupported`).
- `python -m services.recommendation_service` runs a smoke test on the real
  catalogue (asserts the level gate and ascending pathway order).

Endpoints (`main-lms-backend/main.py`, self or admin only via `_ensure_can_view`,
all reading `_learner_competency_state` — see
[skill-gap-analysis.md](skill-gap-analysis.md)):

- `get_recommendations_by_user_id` — resolved levels → `calculate_gaps` →
  `order_gaps_by_opportunity` → ACBP (`fetch_user_cbplan`) `mandatory_recommendations`
  first (completed ones skipped) → `get_recommendations(limit_per_gap=3)` excluding
  enrolled, mandatory and **thumbs-down** courses (`feedback_service.downvoted_ids`).
  `priorityRank` runs over the concatenation.
- `_build_engine` / `_refresh_catalogue_loop` (`main.py`) — the engine and assembler are
  built from `catalogue_store.load_embeddings()` and saved back with
  `save_embeddings()`. Every `CATALOGUE_REFRESH_SECONDS` (default 3600, 0 = off)
  the catalogue + FRAC set are re-fetched. If `catalogue_fingerprint` changed,
  a new engine is built in a thread and swapped in (`app_state.engine`), and
  the competency-state memo is cleared.
- `services/catalogue_store.py` — `Course.syllabusVectorEmbedding` = base64 float32,
  `embeddingModelVersion = "<model>|<text hash>"`, `source = "igot_catalogue"`.
  Never raises (a DB error only means re-encoding).
- **Feedback** — `routers/recommendation_feedback.py` + `services/feedback_service.py`
  (`models.RecommendationFeedback`, one row per event):
  `POST /api/v1/recommendations/feedback {courseId, event, competencyId?, rank?, finalScore?, context?}`
  with `event ∈ impression|click|enrol|thumbs_up|thumbs_down|clear_vote`;
  `GET /api/v1/recommendations/feedback/mine` → `{votes{courseId: up|down}}` (latest vote wins);
  `GET /api/v1/admin/recommendations/feedback` → per-course counts + click-through
  by rank (`byRank[].ctr` = clicks / impressions, `null` until that rank has
  impressions).
  Not gated on warm-up (`_UNGATED`).
- `get_learning_pathway` — `build_pathway` per role competency (catalogue id from
  the crosswalk, role id echoed back), each pathway gets the row's `opportunity`,
  then `build_study_plan`.

Frontend: `src/services/api.ts::fetchRecommendations` (maps `why`, `mandatory`, `modality`,
`courseLevel`, `tpacSource`, `measuredUplift`), `sendRecommendationFeedback`,
`fetchMyRecommendationVotes`, `fetchLearningPathways`;
`components/dashboard/CourseCard.tsx` (Mandatory badge, format + level line, "Why
recommended?" summary + level step + badges, 👍/👎, title click and Enroll logged).
Its `MatchScoreBar` bands read against the absolute scale — ≥80 green, ≥65 blue,
amber below — and a mandatory card says in one line that it is listed first
because the ACBP requires it, not because of its score.
`RecommendationsPanel.tsx` owns the vote state (optimistic), sends feedback, and
logs one **impression** per card it actually shows (once per course per panel,
best-effort), which is the denominator the admin click-through report needs;
`components/dashboard/LearningPathway.tsx`
(`PathwayLadder` timeline, `StudyPlanSummary`), rendered from `SkillGapCard.tsx`
("View learning path" per gap, study order on top; needs `officialId` prop).

Tests: `main-lms-backend/tests/test_pathway.py` — tiny synthetic catalogue +
deterministic stub embedder (no model download): level gate, holes/stretch,
mis-tagged course handling, diagnostic/bridge/continue/optional steps, study-plan
ordering, course sharing, budget, crosswalk.

## In / out

**In** — resolved `{compId: level}` and `{compId: target}`; enrollments
(completed ids excluded, in-progress continued); crosswalk ids.

**Out** — `GET /api/v1/learner/{user_id}/recommendations`:
```json
{ "status", "officialId", "needsDiagnostic": [{ "competencyId","competencyName" }],
  "skillGaps": [{ "competencyId","competencyName","currentLevel","targetLevel",
                  "gapScore","priorityScore","confidence" }],
  "recommendations": [{ "courseId","title","provider","durationHours","finalScore",
                        "relevanceScore","qualityScore","isTpac","competencyId",
                        "competencyName","priorityRank","matchReasons","matchType",
                        "tpacSource","courseLevel","tagSupported","matchReason","tags",
                        "measuredUplift","modality","mandatory","reranked",
                        "why": { "gap","levelStep","badges","summary" } }],
  "hiddenByFeedback", "acbpCycle", "message" }
```
`skillGaps[]` also carries `opportunity` (Low | Medium | High | null). `matchType` adds
`acbp_mandatory`.
`GET /api/v1/learner/{user_id}/pathway?competencyId=&budgetHours=&unbudgeted=`.
The endpoint reads the official's ACBP through
`MockIgotAdapter.fetch_user_cbplan()`. With no `budgetHours`, the plan is
**this quarter's**: budget = `learningHoursPerQuarter`, classroom cap = 30 h,
`budgetSource: "quarterly_hours"`. `budgetHours` overrides the budget
(`"query"`, no cap). `unbudgeted=true` plans everything (`"none"`). Mandatory
courses are always passed in, except for single-competency requests, and
pathway steps get `mandatory: true` when their course is one.
```json
{ "status", "officialId",
  "pathways": [{ "competencyId","catalogueCompetencyId","crosswalk","competencyName",
                 "currentLevel","startLevel","targetLevel","gap","priorityScore",
                 "confidence","basis","evidenceLevel","status","needsDiagnostic",
                 "message","totalHours","bridgeHours","coverageGaps",
                 "unreachableLevels","tagReviewFlags","opportunity",
                 "steps": [{ "order","kind","fromLevel","toLevel","covers",
                             "levelDescriptor","course","hours","reason",
                             "alternatives","action?","mandatory",
                             "prerequisites": [{ "competencyId","competencyName","level",
                                                 "currentLevel","met","rationale","source" }] }] }],
  "studyPlan": { "budgetHours","totalHours","diagnostics","deferred","method",
                 "budgetSource","learningHoursPerQuarter","acbpCycle","overBudget",
                 "classroomCapHours","classroomHours","prerequisitesApplied",
                 "mandatory": [{ "courseId","title","competencyId","level","hours",
                                 "aparLinked","reason","status" }],
                 "steps": [{ "order","courseId","title","provider","isTpac","kind",
                             "hours","cumulativeHours","advances",
                             "opportunity","selectedBy" }] } }
```
Both return `503` if the engine failed to build and `403` for another learner's id.

## Connections

Shares `ai/embedder.py` with the chatbot's semantic engine. `course_comp_levels()`
feeds `BaselineAssembler`, so a completed pathway course raises the Verified
channel at its FRAC level — for crosswalked competencies too (`comp_aliases`).

## TODOs / edge cases

- Mock data (regenerated, SCIL v6 Phase A, then scaled to a full FRAC-size
  dictionary): role competencies use the catalogue ids (100% `exact`
  crosswalk), and the catalogue is now **205 competencies / 1,785 courses**
  (was 40 / 514). Tag support is 100% of 2,115 tag↔course pairs (was 52% before
  Phase A), 166 of 205 competencies have a full L1–L5 ladder and the other 39
  are documented holes (see `mock-igot-server/data/README.md`). Durations stay
  realistic (median 5.5 h; 1.25 h micro-learning, 12 h workshop, 48 h TPAC).
  `tagSupported` / `tagReviewFlags` still guard against mis-tags in real data.
- **Startup cost scales with the catalogue:** 1,785 courses is 3.5× the vectors
  to encode. A cold machine with no disk cache and no rows in `courses` spends
  about 45 s on catalogue embeddings before the engine is ready; with either
  cache warm it is unchanged. `scripts/download_model.py` pre-warms the disk
  cache as a deploy build step.
- Semantic / curated crosswalk mappings are unconfirmed; SCIL v6 wants a human
  confirmation queue.
- Course vectors are stored in the DB (`courses`) and memoised on disk; crosswalk
  anchors only on disk. The catalogue is re-checked on a timer (no restart needed).
  Swapping the engine does not rebuild the uplift estimates (reused from startup).
- Warm-up failure is swallowed (`_rec_engine = None`) and surfaces as a 503.
  Requests made while warm-up is still running wait in `main._readiness_gate`
  (up to `WARMUP_WAIT_SECONDS`, default 240) instead of getting that 503.
- TPAC boost now follows provenance (verified 1.25×, inferred 1.10×), consistent with
  Stage 3's 1.0 / 0.5 flag. Both multipliers are reasoned defaults.
- Cross-encoder: `python scripts/download_model.py --reranker` fetches it (opt-in,
  ~470 MB, not part of the default build step); if the repo ships no ONNX export
  the script says so and `sentence-transformers` runs the PyTorch weights instead.
  The 50/50 relevance/CE blend is still not tuned on relevance labels.
- The relevance weights (0.45 / 0.20 / 0.35) and the 0.6 / 0.4 final split are
  reasoned defaults, not fitted — there are no relevance judgements to fit them
  on. The calibration they sit on (the untagged null, the BM25 median, the p95
  enrolment reference) is all derived from the catalogue.
- Because every candidate is tag-filtered *and* level-gated, real scores cluster
  in roughly 0.70–0.90. That band is the honest one: these courses really are all
  plausible. The old 0.00–1.00 spread was the shortlist's rank in disguise.
- Thumbs-down hides a course from that learner only. Feedback is logged, not yet
  learned from: no bandit or re-weighting. Impressions *are* sent now, so
  `byRank[].ctr` is a real rate — but only for ranks seen since that change.
- Not implemented from SCIL v6: data-inferred cross-competency prerequisite edges,
  bandit learning from the feedback log. Cross-encoder re-ranking (opt-in),
  mandatory ACBP in recommendations, modality spread, opportunity tie-break
  and feedback logging are in.
