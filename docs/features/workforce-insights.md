# Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)

The SCIL v6 features that used to be blocked by missing data. Each one follows
the same path: the generator writes data, the mock iGOT server serves it,
`MockIgotAdapter` fetches it, the backend computes, and the UI shows it.

**All inputs are synthetic** (`mock-igot-server/generate_mock_data.py`). Every
admin response carries `dataNote: "Computed on synthetic mock data — demo only."`
and the Insights tab opens with the same warning.

## Reference data loading

- `main-lms-backend/services/reference_data.py` — `ReferenceData.load(adapter)`
  runs once in `main._startup`. Each dataset tries the adapter first. If that
  fails, it logs a warning and reads the same generated file in
  `mock-igot-server/data/`. `sources` records `adapter | disk | missing` per
  dataset. A missing dataset disables its feature (it gives a 503 or no badge)
  but crashes nothing.
- `services/app_state.py` holds the process singletons (`engine`, `assembler`,
  `ref`) so routers don't import `main`.
- `routers/insights.py` has the admin-only endpoints (`require_role("admin")`),
  under `/api/v1/admin/...`.

## GSBPM scope — the 80% officer-hours rule (SCIL v6 §1)

**Data**
- `data/gsbpm_map.json` holds the GSBPM v5.1 phases and sub-processes (plus
  unnumbered overarching processes `OA.*`) and `competencies: {fracId: [sub-process ids]}`.
- `data/offices.json` holds 12 offices. For each: the sub-processes it runs this
  cycle (`FY2026-27-Q2`), with `officerHours` = headcount × 480 h × share, and
  its statistical `products`.
- Every official has `jobProfile.officeId`.

**Mock endpoints:** `GET /api/gsbpm/v1/map`, `GET /api/org/v1/offices`,
`GET /api/org/v1/offices/{officeId}`. The adapter methods are
`fetch_gsbpm_map()` and `fetch_offices()`.

**Computation** — `services/gsbpm_service.py::scope_report`:
1. Sum officer-hours per sub-process (whole NSO, or one office with `?officeId=`).
2. Rank the sub-processes by hours. "Core" is the smallest prefix covering
   `SCOPE_OFFICER_HOURS_SHARE = 0.80` of all hours.
3. A competency is in scope if it is exercised in at least one core
   sub-process. The report lists those sub-processes and their share of hours
   as the reason, and gives the reason for each out-of-scope competency too.

Nothing is a hard-coded count. On the generated data, 13 sub-processes cover
80.8% of 709k officer-hours; 28 competencies are in scope and 12 are out.

**Endpoint:** `GET /api/v1/admin/gsbpm/scope?officeId=` returns
```json
{ "cycle", "officeId", "threshold", "totalOfficerHours", "coreShare",
  "coreSubprocesses": [{ "id","name","officerHours","share","cumulativeShare" }],
  "inScopeCount", "outOfScopeCount",
  "competencies": [{ "competencyId","competencyName","inScope","subprocesses",
                     "coreSubprocesses","officerHours","share","reason" }],
  "offices", "method", "dataNote" }
```

**UI:** Admin → Insights → "GSBPM scope". It has an office selector, core
sub-process bars and a competency table with the reason for each decision
(`frontend/src/components/admin/WorkforceInsights.tsx::GsbpmScopePanel`).

## Opportunity to practise (SCIL v6 §4)

**Computation** — `gsbpm_service.opportunity(office, comp_subprocesses, gsbpm)`.
`share` = the office's officer-hours in the competency's sub-processes divided
by the office's total hours. The level is:
- `High` if share ≥ `OPPORTUNITY_HIGH_SHARE = 0.20` (about a day a week or more)
- `Medium` if share ≥ `OPPORTUNITY_MEDIUM_SHARE = 0.05`
- `Low` otherwise

It returns `{level, share, officerHours, officeId, officeName, cycle, subprocesses[]}`.

**Where it appears**
- `main._learner_competency_state` adds `opportunity` to every competency row, so
  `/skill-gaps` returns it per gap and `/pathway` copies it onto each pathway.
- **Study-plan tie-breaker only** (`recommendation_service.build_study_plan`):
  1. Compute gain/hour for every frontier course.
  2. Candidates within `OPPORTUNITY_TIE_BAND = 0.10` of the best gain/hour are
     near-ties.
  3. Among them, pick the one advancing the highest-opportunity gap
     (High > Medium > Low > unknown). Remaining ties fall back to the old
     ordering.

  Plan steps carry `opportunity` and `selectedBy` (`gain_per_hour` |
  `opportunity_tie_break`). Opportunity is **never** a score multiplier and
  never removes or hides a gap. Tests:
  `test_pathway.py::test_opportunity_breaks_near_ties_towards_the_practisable_gap`
  and `…never_overrides_a_clear_gain_per_hour_winner`.
- **UI**
  - `SkillGapCard` shows a badge on every gap: "Opportunity to practise: Low
    this cycle → queued". The tooltip lists the office's sub-processes and
    their hours share.
  - `StudyPlanSummary` marks tie-break picks with "practise at work".

## Cross-competency prerequisite DAG (SCIL v6 §5, B4)

**Data**
- `data/prerequisites.json` holds 18 expert-seeded edges
  `{from:{competencyId, level}, to:{competencyId, level}, source:"expert", rationale}`,
  hand-written in `mockdata/domain.py::EXPERT_PREREQUISITES`. The generator
  refuses to write a cyclic set.
- `data/course_outcomes.json` holds platform-wide pre/post assessments (see
  B5). Each record lists `priorCompleted`, the competencies the learner had
  finished before the course, which the inference uses.

**Mock / adapter:** `GET /api/frac/v1/prerequisites` →
`fetch_prerequisites()`; `GET /api/course/v1/assessment/outcomes` →
`fetch_course_outcomes()`.

**Validation** — `services/prerequisite_service.py`
- `find_cycle` / `validate_edges` check the expert edges **together with the
  implicit ladder edges** `c@L-1 → c@L`. For example, "B@2 needs A@3" plus
  "A@2 needs B@3" is a cycle through the ladders.
- A cyclic set is rejected as a whole. Plans then run without cross-competency
  prerequisites, and the startup log and the admin endpoint show the cycle.
- Self-edges and out-of-range levels are dropped (`invalid`).
- `ReferenceData.prerequisites` holds only validated edges.

**Enforcement** — `recommendation_service._PrerequisiteGate` inside `build_study_plan`:
- A rung of X that closes level Lx is on the frontier only if every edge
  `A@La → X@Lx` is met.
- A's level is its ladder's progress **in this plan** if A has a ladder; otherwise
  it is the official's current level (`current_levels`, keyed by catalogue id).
- If A's level is unknown (A not in the profile, or UNASSESSED), the edge is
  **advisory**: reported, never enforced, so a missing measurement can't
  dead-end a plan.
- A ladder that is never unblocked is deferred with the reason
  `prerequisite: <A> Level La first`.
- `absorb()` respects the gate too.
- Plan output `prerequisitesApplied[]`: `{edgeId, from, to, status: ordered |
  blocked | advisory}`.
- Each pathway step gets `prerequisites[]` (`step_prerequisites`:
  `{competencyId, competencyName, level, currentLevel, met: true|false|null,
  rationale}`).

**Data-driven suggestions** — `prerequisite_service.infer_edges(outcomes, expert_edges)`:
1. For each (course competency B, level L) and each A that takers completed
   earlier, fit OLS `gain_B ~ 1 + preθ + completedA`. The `completedA`
   coefficient is the extra gain, adjusted for starting ability.
2. Test pairs with ≥ `SUGGEST_MIN_GROUP = 8` learners on each side.
3. Keep pairs that pass Benjamini–Hochberg at `SUGGEST_FDR = 0.10` with effect
   ≥ `SUGGEST_MIN_EFFECT = 0.20` levels.
4. Give each a 95% bootstrap CI (`BOOTSTRAP_ROUNDS = 400`, seeded).
5. Mark it `new_suggestion` or `supports_expert_edge`, with `applied: false`
   always.

This is an observational association for expert review, not a causal claim, and
**never auto-applied**.

**Recovery of planted synthetic effects** (not validation): the generator plants
two precedence bonuses.
- SPSS/SAS before Survey Design L3 (+0.35) is not an expert edge. It comes out
  as a `new_suggestion`: +0.23 [0.06, 0.42], n 20/27.
- Index Numbers before Price Statistics L3 (+0.25) is an expert edge. It comes
  out as `supports_expert_edge`: +0.32 [0.19, 0.45], n 18/23.
- Only these 2 pairs reach the minimum group size in the synthetic data, so the
  false-positive behaviour of the screen is **not** exercised by this data.

**Endpoint:** `GET /api/v1/admin/prerequisites` returns `{edges, validation,
enforced, inference{testedPairs, fdr, minEffect, minGroup, suggestions[],
method}, dataNote}`. Inference is computed once and cached in
`ReferenceData.cache`.

**UI**
- Learner ladder steps show "Needs <A> Level N first (you're at Level M)" or
  "Builds on <A> Level N — your level there isn't assessed yet".
- The study plan lists the ordering it applied.
- Admin → Insights → "Prerequisite DAG" shows the edge table and the suggestion
  table (effect, CI, n, status).

## Measured uplift → coverage learning + training effectiveness (SCIL v6 §6, B5)

**Data:** `data/course_outcomes.json` (see the data README for the planted
effects) holds 2,571 learner records and 2,400 comparison episodes. It is
served at `GET /api/course/v1/assessment/outcomes` and loaded into
`ReferenceData.outcomes/comparisons` at startup.

**Computation** — `services/uplift_service.py::estimate_uplift`, run once in
`main._startup` (~1 s) and cached in `ReferenceData.cache["uplift"]`:
1. **Groups.** Treated = takers of course j. Controls = comparison episodes of
   learners with no course on j's primary competency.
2. **Propensity model.** Ridge logistic (`PROPENSITY_RIDGE = 0.1`) on
   `[1, z, z², tenure/10, statistics degree]`, with `z = preθ − (L − 0.5)`.
   The quadratic captures that takers sit in a band just below the course
   level. Propensities are clipped to `PROPENSITY_CLIP = (0.02, 0.98)`.
3. **ATT weighting.** Control weights `w = e/(1−e)`:
   `ipwUplift = mean_T(Δθ) − Σ w·Δθ_C / Σ w`. `naiveUplift` (unweighted) is
   reported alongside.
4. **Shrinkage.** `q̂_jc = (n·ipwUplift + κ·q_prior)/(n + κ)` with `KAPPA = 5`.
   `q_prior` = pooled IPW uplift of all courses at the same FRAC level
   (data-derived).
5. **Bootstrap CIs** (`BOOTSTRAP_ROUNDS = 300`, vectorised, seeded per course;
   the propensity model is held fixed, so the CIs are conditional on it):
   `ci95` for q̂ and `ipwCi95` for the unshrunk estimate.
6. **Mis-tag flag.** The primary FRAC tag declares the competency (high
   declared relevance), but the **unshrunk** `ipwCi95` upper bound is below
   `MIS_TAG_MAX_UPLIFT = 0.15` levels, with n ≥ `MIN_TAKERS_FOR_FLAG = 10`. It
   uses the unshrunk interval because shrinking toward a positive prior would
   hide exactly these courses.

**Coverage learning in the engine**
- `HybridRecommendationEngine.set_measured_uplift()` attaches the estimates.
  Every `RecommendationResult` / pathway course carries `measuredUplift` and
  `upliftFlag`.
- A flagged course is ordered like a content-unsupported tag: used only when
  nothing else exists at that level, never hidden, with a reason note.
- q̂ is **not** blended into `finalScore`. Most courses have few learners, and
  the data is synthetic.

**Recovery of planted synthetic effects** (the generator's `_truth/`; not a
validation):
- **Planted zero-uplift courses.** All 4 are flagged, and no other course is.
  These courses are popular and highly rated: rating 4.65–4.77, 8.7k–15.8k
  enrolments. Their measured q̂ runs from −0.11 to 0.00.
- **Correlation.** Estimated vs planted true uplift: r = 0.91 over the 22
  courses with n ≥ 15.
- **Confounding.** Maturation grows with ability, and strong officers take the
  advanced courses. Mean bias of the naive estimate by level is −0.10 / −0.07 /
  −0.01 / +0.03 / +0.07. IPW reduces it to −0.07 / −0.04 / −0.01 / −0.01 /
  +0.04. There is residual bias at the extremes, where few comparison learners
  exist.
- **CI coverage.** The unshrunk IPW CIs contain the planted truth for 80% of
  courses, below the nominal 95%. That is expected: the intervals are
  conditional on the fitted propensity model, and courses on one competency
  share one control pool.

**Endpoint:** `GET /api/v1/admin/training-effectiveness?competencyId=&flaggedOnly=&minLearners=`
returns `{summary{courses, learnerRecords, comparisonEpisodes, flagged,
medianMeasuredUplift, priorsByLevel}, courses[{…, n, naiveUplift, ipwUplift,
prior, measuredUplift, ci95, ipwCi95, misTagFlag, flagReason}], constants,
method, dataNote}`. The backend never reads `_truth/`; recovery is checked in
`tests/test_uplift.py`.

**UI**
- Admin → Insights → "Training effectiveness" shows a table with a CI whisker
  per course, naive vs IPW, rating and enrolments next to measured uplift, and
  "Review tag" chips. It has a flagged-only filter, a minimum-n filter and a
  sort toggle.
- Learner ladders show "Low measured uplift" on flagged courses.

## TODOs / limits

- GSBPM **v5.1** sub-process list; "5.2" was requested but could not be
  confirmed. The map is data (`mock-igot-server/mockdata/domain.py`).
- Competency → sub-process links and office workloads are hand-designed
  synthetic data, not measured time use.
- Opportunity is per office, not per individual work allocation.
