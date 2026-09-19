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
  - `BaselineAssembler(course_comp_map, rater_offsets=None)` — map is `{courseId: {compId: FRAC level}}`
    from `HybridRecommendationEngine.course_comp_levels()` (legacy
    `{courseId: [compId]}` still accepted); `rater_offsets` from
    `ReferenceData.rater_offsets` (see *Supervisor leniency* below).
  - `assess_competency(frac_type, comp_id, evidence, work, verified_scores_by_comp, now,
    completed_level)` — **the one scoring path**: 6-term K (adjacency synergy) fused
    with A/U/S, confidence from the strongest objective channel, ceilings,
    `currentLevel`. Used by `compute_for_user` (Pass 2) and by `POST /baseline`.
    Returns `ceiling` and `_evidence` including `supervisorRaw` / `raterOffset`.
  - `explain_level(assessment, resolved, self_reported_level, completed_courses,
    practice_rows)` → `{summary, basis, factors[{key,label,value,detail,role}], caps[]}`:
    the "why this level" text. `role` ∈ `sets_level | floor | contributes | context`.
    It names the completed course behind a course floor, the rater
    correction behind S, and the confidence ceiling ("capped at 3.5 without a
    completed course") and self-report caveat as `caps`. It is built only from
    values the assessment already holds. `compute_for_user` adds
    `completedCourses` and `practiceRows` to each result for it.
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
    They are a running practice ability (quizzes and the adaptive diagnostic, see
    `services/practice_assessment.py`), so the channel takes the **latest**
    practice row (`latest_practice_value`), not the max. The documented value is
    then `max(best certificate, latest practice)`. As a result, a poor quiz
    lowers the fused score and a good one raises it.
- `main-lms-backend/main.py`
  - `_learner_competency_state(user_id)` — returns `{user, enrollments, competencies,
    evidenceRows, aliases}`; each row now carries `explanation` (`explain_level`). Pipeline: profile + enrollments + `EvidenceLog` →
    crosswalk (`_rec_engine.crosswalk`) → assembler → `resolve_level` → one row per
    role competency. Shared by `/skill-gaps`, `/recommendations`, `/pathway`.
    It is a memo over `_resolve_competency_state` keyed `(userId, annotate)`
    (`app_state.user_state_cache`, `COMPETENCY_STATE_CACHE_SECONDS`, default 30):
    the three dashboard calls share one in-flight resolution. The four reads
    (profile, enrollments, iGOT evidence, `EvidenceLog` via `_load_db_evidence` in
    a worker thread) run concurrently. **Any new `EvidenceLog` writer must call
    `app_state.invalidate_user(user_id)`** (rag grading and the diagnostic do); a
    new workforce snapshot drops all annotated entries. The returned dict is
    shared — do not mutate it.
  - `_ensure_can_view(user_id, current_user)` — learners may only read their own
    data (403 otherwise); admins may read anyone's.
  - `get_skill_gaps_by_user_id` — maps FRAC type → UI domain
    (`Domain→Statistical`, `Functional→Governance`, `Behavioural→Leadership`,
    `Technical→Technical`), disambiguates duplicate display names, sorts known gaps
    first (largest gap, then lowest raw score), UNASSESSED last.
- `main-lms-backend/routers/competency.py::POST /api/v1/competencies/baseline` —
  stateless calculator for a single hand-supplied `EvidencePayload` (demo/debug), now
  on the assembler path (`assess_competency` → `resolve_level` → `explain_level`).
  The optional payload fields are `comp_id` (adjacency synergy),
  `adjacent_verified`, workplace channels (`work_sample_level/passed`,
  `utility_level`, `supervisor_rating` + `rater_id`), `completed_level` and
  `self_reported_level`. The response carries `level`, `basis`,
  `knowledgeScore`, `channels` and `whyThisLevel`. `verified_count_in_category`
  is accepted and ignored.
- **Supervisor leniency (per-rater mean offset).**
  `competency_service.rater_leniency_offsets(ratings)` computes, for each rater,
  `offset = (rater mean − grand mean) · n/(n+5)` (no correction below 3
  ratings). `correct_supervisor_rating` gives `S = clamp(raw − offset, 1, 5)`.
  Ratings come from the mock's `GET /api/evidence/v1/supervisor-ratings`
  (`ReferenceData.rater_offsets`, 46 raters in the mock data), and the offsets
  are applied in `_workplace_channels` before fusion.
- **Career readiness** — `routers/career.py::GET /api/v1/learner/{id}/career-readiness[?targetRoleId=]`.
  The next role is the role(s) in the official's office one tier up
  (`roles.json` via `ReferenceData.roles`, `TIER_RANK`). Levels for the role's
  competencies come from `_learner_competency_state`. Competencies not in the
  current profile are scored on the same evidence through
  `assembler.compute_for_user` (no self-report), using `state["evidenceRows"]`.
  `readiness = mean(min(level, required)/required)`, with UNASSESSED counted as
  0 and listed. The primary option is the highest-readiness role in that tier;
  the others go under `alternatives`. `milestones` = current → next → the tier
  after.
- **Level disputes** — `routers/career.py::POST/GET /api/v1/level-disputes`
  (`models.LevelDispute`). Posting one records the shown and claimed level and
  starts an adaptive session (`diagnostic.start_session`); with no item bank it
  is stored as `NEEDS_REVIEW`. When the session finishes,
  `diagnostic._resolve_dispute` sets `CONFIRMED | RAISED | LOWER_THAN_SHOWN`
  from `floor(posterior μ)`, and the answer view carries `dispute`. The usual
  PRACTICE_ASSESSMENT row is what moves the level, so floors still hold.
- `main-lms-backend/models/models.py::EvidenceLog` — the evidence store
  (`VERIFIED_IGOT`, `DOCUMENTED_CERT`, `VERIFIED_CERT`, `TENURE`, `SELF_REPORT`, `PRACTICE_ASSESSMENT`).
  `VERIFIED_CERT` rows (admin-approved certificates) are read by the verified channel
  together with `VERIFIED_IGOT` (`baseline_assembler.VERIFIED_EVIDENCE`).
- `_load_db_evidence` and every non-route DB use go through `auth.database.session_scope()`;
  routes use `Depends(get_db)` (no `next(get_db())` left).
- Frontend: `src/services/api.ts::fetchSkillGapsAndProfile` (+ `whyThisLevel`),
  `fetchCareerReadiness`, `openLevelDispute`, `answerDiagnostic`;
  `components/dashboard/CareerReadinessCard.tsx`, `LevelCheckModal.tsx`,
  `src/hooks/useLearnerDashboard.ts`, `src/components/dashboard/SkillGapCard.tsx`
  (pip strip, target gauge, `CONFIDENCE_CONFIG` badge incl. UNASSESSED and a
  "Self-reported" label, "Why this level?" panel (`WhyThisLevel`), "Disagree with
  this level?" → `LevelCheckModal`, per-channel `EvidenceBar`, "Not yet assessed" section,
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
- Tests: `tests/test_practice_assessment.py` (difficulty-aware update, latest
  practice row wins, a failed quiz lowers the score and a passed one raises it),
  `main-lms-backend/tests/test_pathway.py` (formula renormalisation,
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
                                "supervisor","supervisorRaw","raterOffset" },
                  "whyThisLevel": { "summary","basis",
                                    "factors": [{ "key","label","value","detail","role" }],
                                    "caps": [] } }] }
```
`GET /api/v1/learner/{id}/career-readiness` →
`{currentRole{roleId,designation,tier,officeId,readinessPct}, nextRole{roleId,designation,tier,
readinessPct,metCount,gapCount,unassessedCount,competencies[{competencyId,competencyName,
requiredLevel,currentLevel,gap,confidence,basis,inCurrentRole}]} | null, alternatives[],
atTopOfLadder, milestones[{roleId,designation,tier,status}], method}`.

`POST /api/v1/level-disputes {competencyId, claimedLevel?, reason?}` →
`{dispute{disputeId,competencyId,shownLevel,claimedLevel,status,testedLevel,sessionId,…},
session: <diagnostic view> | null}`; `GET /api/v1/level-disputes` → `{disputes[]}`.
`rawScore` is the fused K/A/U/S score. `basis` also takes `work_sample` and
`applied_at_work` values. Each row also carries `proficiency` (SCIL v6 §2
belief θ ~ N(μ, σ²) with dated two-class decay, expected-shortfall gap,
refresher flag) and, for UNASSESSED rows, `coldStartPrior` (cohort prior
"inferred from role — unassessed"). See
[workforce-insights.md](workforce-insights.md). Neither changes the displayed
level.
`opportunity` (SCIL v6 §4, `null` when the office is unknown) =
`{level: Low|Medium|High, share, officerHours, officeId, officeName, cycle,
subprocesses[]}` — see [workforce-insights.md](workforce-insights.md).
`currentLevel` and `gapScore` are `null` when UNASSESSED. `basis` ∈
`evidence | course_completion | self_report | none`; `evidenceLevel` is what the
evidence alone supports (differs from `currentLevel` only when self-reported).

## Connections

Levels feed the recommendation engine and pathway builder through the shared
`_learner_competency_state`. Quiz attempts (pass or fail) and certificate
uploads write `EvidenceLog` rows that move these numbers. `/rag/grade` links a
quiz to one of these rows and returns the before → after snapshot as
`skillImpact`. The chatbot receives the computed gaps as request
context.

## TODOs / edge cases

- Weights, half-lives, the adjacency table and `SYNERGY_CAP` are reasoned defaults,
  **not empirically validated** (SCIL v6 §3 wants AHP-elicited weights).
- Quizzes now record failed attempts too: every first attempt writes the updated
  practice ability, and a poor result lowers the fused `rawScore` (see
  [rag-quiz-generator.md](rag-quiz-generator.md)). Floors still hold, though.
  Nothing can show an official *below* a self-reported level, a completed course
  or a passed work sample. The practice signal moves the score, and the
  displayed level only when the formula is what sets it.
- Documented/quiz evidence alone is capped at Level 3 by the MEDIUM ceiling (3.5);
  only verified completions reach Level 4–5.
- If `_assembler` fails to build at startup, levels fall back to self-report only.
- Sessions: done (routes use `Depends(get_db)`, the rest `session_scope()`).
- `/baseline`: done (assembler path).
- **Rater leniency is corrected relative to other raters only.** Mean-centring
  cannot remove leniency that every rater shares: the synthetic raters are
  all +0.4 on average, and the grand mean absorbs that. A rater whose team
  really is stronger also gets corrected as if lenient. An anchor against
  objective evidence (K/A of the same ratees) would fix both; that is a TODO.
  Offsets are computed once at startup.
- Career readiness assumes promotion stays within the office, one tier up. Cross-office
  moves need `?targetRoleId=`. Competencies outside the current profile have no
  self-report, so they are often LOW or UNASSESSED; the level check is the fix.
- Level disputes: `LOWER_THAN_SHOWN` is recorded but cannot push the level
  below evidence floors (completed course, passed work sample). There is no
  reviewer UI for `NEEDS_REVIEW` disputes yet.
- Opportunity badge: done (B1).
- Tier-2 attribute mastery (DINA) is not built. It needs 30–50 real
  respondents; synthetic data is not enough.
- Bayesian IRT, CAT, cold start and expected-shortfall gaps are covered by the
  B7/B8 items; see [workforce-insights.md](workforce-insights.md).
