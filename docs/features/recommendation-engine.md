# AI Course Recommendation Engine + Learning Pathways

Level-aware hybrid retrieval: prioritise gaps, filter the catalogue by FRAC tag
**and FRAC level**, fuse dense and sparse rankings with RRF, re-score by quality —
then turn the ranked courses into a step-by-step learning path per competency and
one study order across all gaps.

## Code

`main-lms-backend/services/recommendation_service.py` — `HybridRecommendationEngine`
(singleton, built once in `main.py::_startup` as `_rec_engine`).

- `__init__(catalog_path, frac_path)` — loads `frac_competencies.json` into
  `_frac_map` (incl. `levels`: the L1–L5 proficiency descriptors from `children`),
  parses `course_catalog.json` into `_catalog` + `_comp_index` + `_by_id`, builds
  BM25 over `title + description`, encodes the corpus with `ai.embedder`, keeps the
  matrix as `_embeddings` and in a `faiss.IndexFlatIP`, and builds the crosswalk
  anchors (`_xw_ids`, `_xw_emb`, `_xw_threshold`).
- `_parse_catalog` — parses the JSON-string `competencies_v3` tags **including
  `competencyLevel`** into `_CourseDoc.comp_levels {compId: 1..5}`, duration, TPAC
  provenance (`verified`/`inferred`/`none`), quality fields kept as `None` if missing.
- Accessors: `course_comp_levels()` (feeds `BaselineAssembler`),
  `levels_available(comp)`, `level_descriptor(comp, level)`.
- `crosswalk(comp_id, name)` — maps a role competency to the catalogue FRAC
  competency that serves it: `exact` when the id is tagged in the catalogue, else
  the nearest anchor by name embedding if it beats `_xw_threshold` = the 95th
  percentile of similarities between **distinct** FRAC competencies (derived from
  the FRAC set, not tuned) → `semantic_crosswalk` (unconfirmed), else `None`.
- `calculate_gaps(baselines, targets, names, confidence, catalogue_ids)` —
  **Stage 0**: `priority = gap · target/5`. Competencies missing from `baselines`
  (UNASSESSED) are skipped — "no evidence" is not "level 0".
- `_retrieve_for_gap(gap, top_k, levels)` — **Stage 1** FRAC-tag filter restricted
  to `levels`; **Stage 2** exact cosine over the candidate pool + BM25, RRF
  `1/(60+rank_dense) + 1/(60+rank_sparse)`, `1.25×` NSSTA boost. Query = official
  FRAC name + description of `gap.catalogue_key` (cached per competency in
  `_query_cache`). No tagged courses at all → full-corpus FAISS `semantic_fallback`.
- `_score_candidates(gap, levels, exclude_ids)` — Stages 1–3 for one gap:
  `final = 0.6·relevance + 0.4·quality`, `courseLevel`, `tagSupported`, reasons.
  Sorted content-supported tags first, then `finalScore`.
- `_tag_support_threshold(comp)` — median cosine of courses *not* tagged with the
  competency; a tagged course at or below it has `tagSupported=False` (its
  author-declared tag isn't backed by content → preferred last, flagged for review).
- `_quality_score` — **Stage 3** `0.35·completion + 0.35·rating + 0.20·log-pop +
  0.10·tpac_flag`, min-max within the shortlist; ratings use Bayesian shrinkage.
- `get_recommendations(gaps, limit_per_gap, enrolled_ids)` — level-gated: only
  courses with `current < courseLevel ≤ target` (nearest level above target as a
  flagged stretch if the band is empty); picks interleaved by level (best of each
  level, lowest first). Blocks concatenated in gap-priority order, no global re-sort.
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
- `build_study_plan(pathways, budget_hours)` — **Stage 4b**: SCIL v6 §5 greedy —
  repeatedly take the frontier course with the highest Σ priority × levels covered
  / hours; a course that is the next rung for two gaps counts for both and advances
  both (the other pathway's step is swapped to it in place). Ladder order is the
  prerequisite DAG. With a budget, a course that doesn't fit blocks its ladder
  (`deferred`). UNASSESSED ladders are not scheduled; they're listed in
  `diagnostics`. **No approximation guarantee is claimed** — the (1−1/e) bound does
  not hold for ratio-greedy under a budget with precedence constraints.
- Pydantic outputs: `GapEntry` (+ `confidence`, `catalogueId`, `catalogue_key`),
  `RecommendationResult` (+ `courseLevel`, `tagSupported`).
- `python -m services.recommendation_service` runs a smoke test on the real
  catalogue (asserts the level gate and ascending pathway order).

Endpoints (`main-lms-backend/main.py`, self or admin only via `_ensure_can_view`,
all reading `_learner_competency_state` — see
[skill-gap-analysis.md](skill-gap-analysis.md)):

- `get_recommendations_by_user_id` — resolved levels → `calculate_gaps` →
  `get_recommendations(limit_per_gap=3)`.
- `get_learning_pathway` — `build_pathway` per role competency (catalogue id from
  the crosswalk, role id echoed back) + `build_study_plan`.

Frontend: `src/services/api.ts::fetchRecommendations`, `fetchLearningPathways`;
`components/dashboard/CourseCard.tsx`; `components/dashboard/LearningPathway.tsx`
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
                        "tpacSource","courseLevel","tagSupported","matchReason","tags" }] }
```
`GET /api/v1/learner/{user_id}/pathway?competencyId=&budgetHours=`:
```json
{ "status", "officialId",
  "pathways": [{ "competencyId","catalogueCompetencyId","crosswalk","competencyName",
                 "currentLevel","startLevel","targetLevel","gap","priorityScore",
                 "confidence","basis","evidenceLevel","status","needsDiagnostic",
                 "message","totalHours","bridgeHours","coverageGaps",
                 "unreachableLevels","tagReviewFlags",
                 "steps": [{ "order","kind","fromLevel","toLevel","covers",
                             "levelDescriptor","course","hours","reason",
                             "alternatives","action?" }] }],
  "studyPlan": { "budgetHours","totalHours","diagnostics","steps","deferred","method" } }
```
Both return `503` if the engine failed to build and `403` for another learner's id.

## Connections

Shares `ai/embedder.py` with the chatbot's semantic engine. `course_comp_levels()`
feeds `BaselineAssembler`, so a completed pathway course raises the Verified
channel at its FRAC level — for crosswalked competencies too (`comp_aliases`).

## TODOs / edge cases

- **Mock data mismatch (mock-igot feature):** the mock server serves role
  competencies from `userdata.json` (`CID####` ids, 210 broad FRAC names), while
  the catalogue is tagged with the 40 MoSPI ids from `frac_competencies.json`
  (which `users.json` uses). The crosswalk maps ~25% of those names (52/210);
  the rest get `no_content` paths and semantic-fallback recommendations.
- Mock `competencies_v3` tags look random: 192/403 tags score no closer to their
  competency than an average untagged course. `tagSupported` / `tagReviewFlags`
  surface this; they don't hide those courses when nothing better exists.
- Semantic crosswalk mappings are unconfirmed (e.g. "Institutional Governance →
  e-Governance Platforms"); SCIL v6 wants a human confirmation queue.
- The catalogue is read **from disk**, bypassing `MockIgotAdapter`; embeddings are
  recomputed on every startup (`Course.syllabusVectorEmbedding` unused).
- Startup failure is swallowed (`_rec_engine = None`) and surfaces as a 503.
- The 1.25× NSSTA boost applies to any `is_tpac` course while Stage 3 distinguishes
  verified (1.0) from inferred (0.5).
- Not implemented from SCIL v6: cross-encoder re-ranking, expert/data-inferred
  cross-competency prerequisite edges, mandatory-ACBP force-include, modality mix,
  opportunity tie-breaker, coverage learning from measured gain, bandit logging.
