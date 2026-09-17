# AI Course Recommendation Engine

Three-stage hybrid retrieval: prioritise gaps, filter the catalog by FRAC tag,
fuse dense (FAISS) and sparse (BM25) rankings with RRF, then re-score by quality.

## Code

`main-lms-backend/services/recommendation_service.py` — `HybridRecommendationEngine`
(singleton, built once in `main.py::_startup` as `_rec_engine`).

- `__init__(catalog_path, frac_path)` — loads `mock-igot-server/data/frac_competencies.json`
  into `_frac_map`, parses `mock-igot-server/data/course_catalog.json` into
  `_catalog: List[_CourseDoc]` + `_comp_index: {compId: [catalogIdx]}`, builds a
  `BM25Okapi` corpus over `title + description`, encodes the corpus with
  `ai.embedder.get_embedder()` and adds it to a `faiss.IndexFlatIP` (384-dim, cosine
  on L2-normalised vectors).
- `_parse_catalog` — parses the JSON-string `competencies_v3` tags, derives duration
  hours, classifies TPAC provenance (`verified` when `is_tpac: true` in the catalog,
  `inferred` when creator/organisation matches `NSSTA_CREATORS`, else `none`), and
  keeps missing quality fields as `None` rather than fabricating defaults.
- `calculate_gaps(baselines, targets) -> List[GapEntry]` — **Stage 0**:
  `priority = gap * (target / 5)`, sorted descending; non-positive gaps dropped.
- `_retrieve_for_gap(gap, top_k)` — **Stage 1** FRAC-tag candidate filter, **Stage 2**
  dense + sparse retrieval on a query built from the official FRAC name + description
  (never raw user text), RRF fusion `1/(60+rank_dense) + 1/(60+rank_sparse)` with a
  `1.25×` NSSTA boost. If a competency has no tagged courses it degrades to a
  full-corpus FAISS search (`semantic_fallback`, raw cosine as the score).
- `_quality_score(doc, shortlist)` — **Stage 3** quality composite
  `0.35·completion + 0.35·rating + 0.20·log-popularity + 0.10·tpac_flag`, each
  component min-max normalised only over shortlist docs that actually have the field.
  Ratings use Bayesian shrinkage `_shrunk_rating` (`_PRIOR_MEAN=3.0`, `_SHRINK_K=15`),
  which replaced an earlier (mathematically invalid) Wilson lower bound.
- `get_recommendations(gaps, limit_per_gap, enrolled_ids)` — per gap: retrieve,
  drop enrolled/already-seen courses, score `final = 0.6·relevance + 0.4·quality`,
  build human-readable `matchReasons`, sort within the gap block, take top-K.
  Blocks are concatenated in gap-priority order — **no global re-sort** — and
  `priorityRank` is the 1-based position in that concatenation.
- Pydantic outputs: `GapEntry`, `RecommendationResult`.
- `python -m services.recommendation_service` runs a built-in smoke test.

Endpoint: `main-lms-backend/main.py::get_recommendations_by_user_id` — fetches the
profile and enrollments, recomputes baselines with `BaselineAssembler`, injects
readable competency names into `_frac_map`, calls `calculate_gaps` then
`get_recommendations(limit_per_gap=3)`, and shapes the response.

Frontend: `src/services/api.ts::fetchRecommendations`, `useLearnerDashboard`,
`components/dashboard/CourseCard.tsx` (score chips, TPAC badge, match reasons).

## In / out

**In** — `{compId: baseline}` and `{compId: target}` derived from the assembler;
`enrolled_ids` for exclusion.

**Out** — `GET /api/v1/learner/{user_id}/recommendations`:
```json
{ "status", "officialId",
  "skillGaps": [{ "competencyId","competencyName","currentLevel","targetLevel",
                  "gapScore","priorityScore" }],
  "recommendations": [{ "courseId","title","provider","durationHours","finalScore",
                        "relevanceScore","qualityScore","isTpac","competencyId",
                        "competencyName","priorityRank","matchReasons","matchType",
                        "tpacSource","matchReason","tags" }] }
```
Returns `503` if the engine failed to build, `"No skill gaps detected"` when there
are none.

## Connections

Shares `ai/embedder.py` with the chatbot's semantic engine. Its `_comp_index` is
inverted at startup to build the `BaselineAssembler`'s `course_comp_map`, so the
Verified evidence channel and the candidate filter stay consistent.

## TODOs / edge cases

- The catalog is read **from disk**, bypassing `MockIgotAdapter` — so
  `/api/v1/learner/*/recommendations` uses `data/course_catalog.json` while the mock
  server itself serves `courses.json` / `courses_1.json`. These sets can drift.
- Embeddings are recomputed on every startup; `Course.syllabusVectorEmbedding` in
  `models.py` is never used. Startup cost scales with catalog size.
- Startup failure is swallowed (`_rec_engine = None`) and only surfaces as a 503 later.
- `_frac_map` is mutated per request when injecting names — fine while read-mostly
  and single-process, but it is shared mutable state.
- The 1.25× NSSTA boost applies to any `is_tpac` course, while Stage 3 distinguishes
  verified (1.0) from inferred (0.5) — two different treatments of the same signal.
- The docstring mentions differentiated 1.15×/1.05× boosts that are not implemented.
