# Skill Gap Analysis (evidence-based competency baselines)

Computes each official's current level per FRAC competency from six evidence
channels, tags it with a confidence level, and subtracts it from the role's
required level to produce the gap shown on the learner dashboard. The same
resolved level drives the recommendation and learning-pathway endpoints, so the
three can never disagree.

## Code

- `main-lms-backend/services/competency_service.py` — `CompetencyCalculator`
  - `WEIGHTS`: verified .45, documented .15, tenure .20, self_report .10, education .05, seniority .05
  - `calculate_baseline(frac_type, evidence_data, …) -> (b_k, confidence)`.
    All-zero evidence → `(0.0, "UNASSESSED")`. The core is a **weighted mean over
    the channels that carry evidence** — missing channels are renormalised out,
    not scored 0 (SCIL v6 §3). Confidence comes from *which* channel fired:
    verified → HIGH (ceiling 5.0), documented → MEDIUM (3.5), otherwise LOW (2.5).
    Final `b_k = min(core_k + synergy_k, ceiling)`, on the 0–5 FRAC scale.
  - `_calculate_recency_multiplier` — true half-life decay (`0.5^(t/h)`) on
    certificate age, 3y Domain/Technical, 8y Behavioural, floor 0.2.
  - `compute_synergy(comp_id, verified_scores_by_comp)` — bonus only for pairs in
    `ADJACENT_COMPETENCIES` (now keyed by the real FRAC catalogue ids), cap 0.15.
  - Self-report is discounted ×0.6; seniority is zeroed for Domain/Technical.
- `main-lms-backend/services/baseline_assembler.py`
  - `BaselineAssembler(course_comp_map)` — map is `{courseId: {compId: FRAC level}}`
    from `HybridRecommendationEngine.course_comp_levels()` (legacy
    `{courseId: [compId]}` still accepted).
  - `compute_for_user(user, enrollments, db_evidence, now, comp_aliases)` →
    `{compId: {score, confidence, currentLevel, completedLevel, _evidence{…}}}`.
    Two passes (verified first, for synergy). `comp_aliases` = crosswalk
    `{roleCompId: catalogueCompId}`: tags, adjacency and evidence rows are read
    under both ids.
  - `_verified_from_enrollments` → `(value, completedLevel)`: only **completed**
    courses (status 2 or 100%) tagged with the competency count, credited at their
    **FRAC tag level**. Partial progress counts for nothing.
  - `currentLevel = floor(b_k)`, `None` when UNASSESSED. No `requiredLevel − 1` cap.
  - `resolve_level(assessment, self_reported_level)` — **the single source of truth**
    for the displayed level. Every evidence source is a floor (completing a Level-N
    course, passing a quiz, holding a certificate show *at least* that level), so the
    level is the highest floor and is monotone: more learning never lowers it.
    Self-report still counts as a floor but, when it is what sets the level, the
    result is `confidence: LOW, basis: "self_report"` and the pathway adds a
    diagnostic first. Returns `{level, confidence, basis, evidenceLevel}`.
  - Helpers: `is_completed`, `enrollment_course_id`, `_tenure_score`,
    `_education_score` (`_EDU_RELEVANCE`), `_TIER_SENIORITY` (also maps the tier
    names profiles actually carry: `TIER1_APEX`, `TIER2_SENIOR`), `_map_category`.
  - `PRACTICE_ASSESSMENT` evidence rows are read through the *documented* channel.
- `main-lms-backend/main.py`
  - `_learner_competency_state(user_id)` — profile + enrollments + `EvidenceLog` →
    crosswalk (`_rec_engine.crosswalk`) → assembler → `resolve_level` → one row per
    role competency. Shared by `/skill-gaps`, `/recommendations`, `/pathway`.
  - `_ensure_can_view(user_id, current_user)` — learners may only read their own
    data (403 otherwise); admins may read anyone's.
  - `get_skill_gaps_by_user_id` — maps FRAC type → UI domain
    (`Domain→Statistical`, `Functional→Governance`, `Behavioural→Leadership`,
    `Technical→Technical`), disambiguates duplicate display names, sorts known gaps
    first (largest gap, then lowest raw score), UNASSESSED last.
- `main-lms-backend/routers/competency.py::POST /api/v1/competencies/baseline` —
  stateless calculator for a single hand-supplied `EvidencePayload` (demo/debug).
- `main-lms-backend/models/models.py::EvidenceLog` — the evidence store
  (`VERIFIED_IGOT`, `DOCUMENTED_CERT`, `TENURE`, `SELF_REPORT`, `PRACTICE_ASSESSMENT`).
- Frontend: `src/services/api.ts::fetchSkillGapsAndProfile`,
  `src/hooks/useLearnerDashboard.ts`, `src/components/dashboard/SkillGapCard.tsx`
  (pip strip, target gauge, `CONFIDENCE_CONFIG` badge incl. UNASSESSED and a
  "Self-reported" label, per-channel `EvidenceBar`, "Not yet assessed" section,
  per-gap learning-path toggle — see
  [recommendation-engine.md](recommendation-engine.md)).
- **SCIL v6 §3 evidence channels (B6).** The 6-term `b_k` above is channel
  **K** (knowledge). Three workplace channels are fused with it:
  - **A (application).** Auto-graded work samples. A passed Level-L sample
    counts as L; a failed one counts as L − 0.5.
  - **U (utility).** The highest course level whose use the supervisor
    confirmed ≥ 90 days after completion.
  - **S (supervisor).** The latest APAR rating, 1–5.

  How it is computed:
  - `competency_service.fuse_channels` takes a weighted mean over the channels
    present, with `CHANNEL_WEIGHTS = 0.25` each. These weights are an
    **explicitly labelled equal placeholder** (`CHANNEL_WEIGHTS_STATUS`) until
    an expert AHP elicitation exists; nothing is fitted.
  - `baseline_assembler._workplace_channels` reads EvidenceLog-style rows
    (`WORK_SAMPLE`, `UTILITY`, `SUPERVISOR_RATING`). `PEER_RATING` rows are
    counted (`peerFeedback`) and **never scored**.
  - Confidence comes from the strongest objective channel: a passed work sample
    gives HIGH; confirmed use lifts LOW/UNASSESSED to MEDIUM; a supervisor
    rating alone gives LOW. The ceilings (5.0 / 3.5 / 2.5) still apply, so a
    lenient rater without objective evidence can't push a level above 2.
  - `resolve_level` gains two monotone floors: `workSampleLevel` (HIGH,
    basis `work_sample`) and `appliedLevel` (MEDIUM, basis `applied_at_work`).
    A supervisor rating is never a floor.
  - Assessments now carry `knowledgeScore` (b_k), `score` (fused),
    `channels{K,A,U,S}` and `completeness{present, missing, weights,
    weightsStatus}`.
  - The workplace rows come from the mock at
    `GET /api/evidence/v1/user/{id}` (`MockIgotAdapter.fetch_user_evidence`).
    `_learner_competency_state` merges them with the LMS's own `EvidenceLog`
    rows.
- Tests: `main-lms-backend/tests/test_pathway.py` (formula renormalisation,
  monotone levels, partial progress, crosswalked evidence, UNASSESSED),
  `tests/test_evidence_channels.py` (equal weights, renormalisation,
  lenient-rater ceiling, work-sample and confirmed-use floors, peer never
  scored, monotonicity).

## In / out

**In** — iGOT user profile (`competencies[]` with `requiredLevel`,
`competencyLevel` (self-report), `type`; `careerHistory`, `education`,
`jobProfile.tier`, `experienceYears`), enrollment completions, `EvidenceLog` rows.

**Out** — `GET /api/v1/learner/{user_id}/skill-gaps` (self or admin):
```json
{ "userId", "govId", "jobRole", "department", "totalCourses", "completedCourses",
  "skillGaps": [{ "competencyId", "skillName", "domain", "currentLevel",
                  "targetLevel", "gapScore", "confidence", "basis", "evidenceLevel",
                  "rawScore", "crosswalk", "opportunity",
                  "channels": { "K","A","U","S" },
                  "evidenceCompleteness": { "present","missing","weights","weightsStatus" },
                  "peerFeedback",
                  "evidence": { "verified","documented","tenure","selfReport",
                                "education","seniority","workSample","utility",
                                "supervisor" } }] }
```
`rawScore` is the fused K/A/U/S score. `basis` also takes `work_sample` and
`applied_at_work` values.
`opportunity` (SCIL v6 §4, `null` when the office is unknown) =
`{level: Low|Medium|High, share, officerHours, officeId, officeName, cycle,
subprocesses[]}` — see [workforce-insights.md](workforce-insights.md).
`currentLevel` and `gapScore` are `null` when UNASSESSED. `basis` ∈
`evidence | course_completion | self_report | none`; `evidenceLevel` is what the
evidence alone supports (differs from `currentLevel` only when self-reported).

## Connections

Levels feed the recommendation engine and pathway builder through the shared
`_learner_competency_state`. Quiz passes and certificate uploads write `EvidenceLog`
rows that move these numbers. The chatbot receives the computed gaps as request
context.

## TODOs / edge cases

- Weights, half-lives, the adjacency table and `SYNERGY_CAP` are reasoned defaults,
  **not empirically validated** (SCIL v6 §3 wants AHP-elicited weights).
- Every evidence source is a floor: nothing (not even a practice quiz, which only
  writes evidence on a pass) can show an official is *below* a self-reported level.
  The pathway's diagnostic step flags it, but a real "fail" signal needs the quiz
  to record failed attempts as evidence too.
- Documented/quiz evidence alone is capped at Level 3 by the MEDIUM ceiling (3.5);
  only verified completions reach Level 4–5.
- If `_assembler` fails to build at startup, levels fall back to self-report only.
- Sessions are opened with `next(get_db())` rather than via `Depends(get_db)`.
- `routers/competency.py::/baseline` still uses the legacy count-based synergy path.
- **Supervisor ratings are not corrected for rater leniency.** The synthetic
  raters are lenient by +0.4 levels on average, plus halo. With equal weights,
  S raises the fused level where K is weak; the ceilings bound it only when no
  objective evidence exists. A per-rater leniency correction needs repeated
  ratings per rater and is a TODO.
- Opportunity badge: done (B1).
- Tier-2 attribute mastery (DINA) is not built. It needs 30–50 real
  respondents; synthetic data is not enough.
- Bayesian IRT, CAT, cold start and expected-shortfall gaps are covered by the
  B7/B8 items; see [workforce-insights.md](workforce-insights.md).
