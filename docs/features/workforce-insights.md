# Workforce Insights (SCIL v6 — GSBPM scope, opportunity, admin foresight)

The SCIL v6 features that used to be blocked by missing data. Each one follows
the same path: the generator writes data, the mock iGOT server serves it,
`MockIgotAdapter` fetches it, the backend computes, and the UI shows it.

**All inputs are synthetic** (`mock-igot-server/generate_mock_data.py`). Every
admin response carries `dataNote: "Computed on synthetic mock data — demo only."`
and the Insights tab opens with the same warning.

## Reference data loading

- `main-lms-backend/services/reference_data.py` — `ReferenceData.load(adapter)`
  runs once in `main._warm_up` (the six fetches run concurrently). Each dataset tries the adapter first. If that
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
`main._warm_up` (~1 s) and cached in `ReferenceData.cache["uplift"]`:
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

## Dated decay, cold start and workforce foresight (SCIL v6 §2 / §11, B8)

### Proficiency belief with dated decay

`services/proficiency_service.py`. The **displayed FRAC level stays the
monotone evidence-floor level** from `resolve_level`. The probabilistic layer
sits on top of it:
- **Belief.** θ ~ N(μ, σ²), with μ = the fused K/A/U/S score and σ by
  confidence tier: `SIGMA_BY_CONFIDENCE` HIGH 0.45 / MEDIUM 0.7 / LOW 0.95.
- **Decay clock.** `baseline_assembler._last_evidence_date` gives the newest
  dated objective evidence: completion, certificate, quiz, work sample,
  supervisor rating or confirmed use. Tenure, education, self-report and peer
  ratings are undated.
- **Two-class decay** (`HALF_LIFE_MONTHS`: accuracy 6.5, procedural 12, class
  from `frac_competencies.json::decayClass`). λ = 0.5^(age/h);
  μ_t = μ_pop + λ(μ − μ_pop); σ_t² = λ²σ² + (1−λ²)σ_pop². The belief
  **relaxes toward the population mean**; it never snaps to zero.
- **Expected-shortfall gap.** `G = (T−μ)Φ(z) + σφ(z)`.
- **Refresher.** `refresherRecommended` when the decayed μ is more than
  `REFRESH_MARGIN = 1.0` level below the displayed level.
- **Output.** `/skill-gaps` rows carry `proficiency{mu, sigma, decayedMu,
  decayedSigma, band80, evidenceAgeMonths, decayClass, halfLifeMonths,
  retention, populationMu, expectedShortfall, refresherRecommended}`.

### Cold start for UNASSESSED competencies

`proficiency_service.cohort_prior`:
- **Posting cluster.** The office's dominant GSBPM phase (by officer-hours) ×
  tenure band (`TENURE_BANDS`: 0–5, 6–15, 16+ years).
- **Prior.** The mean of assessed μ over the cluster, widened by
  `COHORT_BAND_INFLATION = 1.5`, needs ≥ `COHORT_MIN_N = 5` peers. Otherwise
  the population prior is used, and a cohort smaller than 5 is suppressed
  (`cohortN: null`).
- **Divergence check.** The mean |z| of the official's assessed μ against
  their cohort; above `DIVERGENCE_Z = 2.0`, pooling is dropped and the
  population prior is used.
- **UI.** "Inferred from role — unassessed: about Level 1.7 (likely 0.6–2.9,
  officials in GSBPM phase 5 × 0–5 y). Not used as your level."

### Workforce snapshot

`main._build_workforce_snapshot` runs every official through
`_learner_competency_state(annotate=False)`:
- It starts as a background task after startup (≈ 2–3 min for 151 officials
  against the dev mock) and can be refreshed with
  `POST /api/v1/admin/workforce/refresh`.
- It is stored in `app_state.snapshot`, with status at
  `GET /api/v1/admin/workforce/status`.
- It feeds the population / cohort statistics and every foresight view.

### Foresight

`services/workforce_service.py`:
- **HRMS data.** `data/hrms.json` holds date of birth / joining,
  superannuation (age 60, last day of the month) and the statistical products
  each official works on. It is served at `GET /api/hrms/v1/officials`.
  `PRODUCT_CRITICAL` maps each product to its critical competencies.
- **`capability_risk`**, per product × critical competency:
  - team size, capable (displayed level ≥ `CAPABLE_LEVEL = 3`), and capable
    officials retiring within 36 months;
  - a `singlePointOfFailure` flag;
  - a risk band: critical = 0 or 1 capable, or all capable retire; high = < 3
    capable or ≥ 50% retiring; moderate = < 5; low otherwise.
- **`foresight`**, at 0, 6, …, 36 months: expected capable = Σ over the team of
  P(in service at t) × P(θ ≥ 3) with θ decayed from the newest evidence plus t.
  - In service: before superannuation, × (1 − `ANNUAL_ATTRITION = 0.03`)^years.
    That rate is a placeholder, not measured.
  - An "attrition only" series (today's Level-3+ officials who stay) separates
    the two effects. No new learning is assumed.
- **`tpac_agenda`** builds draft items for the NSSTA training programme
  committee:
  - catalogue coverage holes with demand (officials whose target passes the
    missing level); high priority if critical to a product or in GSBPM scope;
  - critical / high capability risks, with the 36-month projection;
  - near-zero-uplift courses (B5);
  - new prerequisite suggestions (B4).

  Every item is `status: "draft"`.
- **Small-cell suppression.** Every count of officials in an aggregate is
  suppressed when it is 1–4 (`SUPPRESS_BELOW = 5` → `display: "<5"`); 0 is
  shown. The single-point-of-failure flag is kept because it is the purpose
  of the view, even though it implies a count of one. That tension is logged
  in the decisions log.

**Endpoints:** `GET /api/v1/admin/workforce/{status | capability-risk |
foresight | tpac-agenda}` and `POST /api/v1/admin/workforce/refresh`. Results
are cached per snapshot in `ReferenceData.cache["workforce"]`.

**UI:** Admin → Insights → "Workforce foresight" has three panels: capability
risk table (suppressed cells in grey), 36-month table (attrition + decay vs
attrition only; "declining only" filter), and the draft TPAC agenda.

**What the synthetic data shows:**
- Capability risk flags NAS (no Level-3+ official in Index Numbers on the
  team), IIP (none in Industrial Statistics) and Economic Census (a single
  point of failure in Survey Design) as critical.
- With the specified 6.5-month accuracy half-life, decay dominates the
  projection. For CPI price statistics, expected capable officials fall from
  14 (level-based) to about 5. This is the half-life assumption at work, not
  a measured forgetting rate.

## TODOs / limits

- GSBPM **v5.1** sub-process list; "5.2" was requested but could not be
  confirmed. The map is data (`mock-igot-server/mockdata/domain.py`).
- Competency → sub-process links and office workloads are hand-designed
  synthetic data, not measured time use.
- Opportunity is per office, not per individual work allocation.
