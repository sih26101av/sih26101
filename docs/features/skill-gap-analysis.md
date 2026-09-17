# Skill Gap Analysis (evidence-based competency baselines)

Computes each official's current level per FRAC competency from six evidence
channels, tags it with a confidence level, and subtracts it from the role's
required level to produce the gap shown on the learner dashboard.

## Code

- `main-lms-backend/services/competency_service.py` — `CompetencyCalculator`
  - `WEIGHTS`: verified .45, documented .15, tenure .20, self_report .10, education .05, seniority .05
  - `calculate_baseline(frac_type, evidence_data, …) -> (b_k, confidence)`.
    All-zero evidence → `(0.0, "UNASSESSED")`. Confidence comes from *which*
    channel fired: verified → HIGH (ceiling 5.0), documented → MEDIUM (3.5),
    otherwise LOW (2.5). Final `b_k = min(core_k + synergy_k, ceiling)`.
  - `_calculate_recency_multiplier` — exponential decay on certificate age,
    half-life 3y for Domain/Technical, 8y for Behavioural, floor 0.2.
  - `compute_synergy(comp_id, verified_scores_by_comp)` — bonus only for pairs in
    the hand-curated `ADJACENT_COMPETENCIES` table, capped at `SYNERGY_CAP = 0.15`.
  - Self-report is discounted ×0.6; seniority is zeroed for Domain/Technical.
- `main-lms-backend/services/baseline_assembler.py` — `BaselineAssembler`
  - Constructed at startup with `course_comp_map: {courseId: [compId]}` inverted
    from the recommendation engine's `_comp_index`.
  - `compute_for_user(user, enrollments, db_evidence, now)` → `{compId: {score,
    confidence, currentLevel, _evidence{…}}}`. Two passes: pass 1 computes the
    Verified channel for every competency (needed before synergy), pass 2 runs the
    full fusion.
  - Helpers: `_verified_from_enrollments` (strictly FRAC-tag-matched completions,
    no general-engagement fallback), `_tenure_score` (career history, keyword
    overlap + decay), `_education_score` (`_EDU_RELEVANCE` degree table),
    `_TIER_SENIORITY` (designation tier), `_map_category`.
  - `PRACTICE_ASSESSMENT` evidence rows are read through the *documented* channel.
  - `currentLevel` is scaled relative to the confidence ceiling and capped at
    `requiredLevel - 1`; `None` when UNASSESSED.
- `main-lms-backend/main.py::get_skill_gaps_by_user_id` — the endpoint. Fetches
  profile + enrollments via the adapter, loads `EvidenceLog` rows by iGOT userId,
  runs the assembler, maps FRAC type → UI domain (`Domain→Statistical`,
  `Functional→Governance`, `Behavioural→Leadership`, `Technical→Technical`),
  dedupes competencies, disambiguates duplicate display names, then picks the
  displayed level: HIGH/MEDIUM trust the formula; LOW/UNASSESSED prefer the iGOT
  self-reported `competencyLevel` and use the formula as a floor. Sorts known gaps
  first (largest gap, then lowest raw score), UNASSESSED last.
- `main-lms-backend/routers/competency.py::POST /api/v1/competencies/baseline` —
  stateless calculator for a single hand-supplied `EvidencePayload` (demo/debug).
- `main-lms-backend/models/models.py::EvidenceLog` — the evidence store
  (`VERIFIED_IGOT`, `DOCUMENTED_CERT`, `TENURE`, `SELF_REPORT`, `PRACTICE_ASSESSMENT`).
- Frontend: `src/services/api.ts::fetchSkillGapsAndProfile`,
  `src/hooks/useLearnerDashboard.ts`, `src/components/dashboard/SkillGapCard.tsx`
  (pip strip, target gauge, `CONFIDENCE_CONFIG` badge, per-channel `EvidenceBar`).

## In / out

**In** — iGOT user profile (`competencies[]` with `requiredLevel`,
`competencyLevel`, `type`; `careerHistory`, `education`, `jobProfile.tier`,
`experienceYears`), enrollment completions, `EvidenceLog` rows.

**Out** — `GET /api/v1/learner/{user_id}/skill-gaps`:
```json
{ "userId", "govId", "jobRole", "department", "totalCourses", "completedCourses",
  "skillGaps": [{ "competencyId", "skillName", "domain", "currentLevel",
                  "targetLevel", "gapScore", "confidence", "rawScore",
                  "evidence": { "verified","documented","tenure","selfReport",
                                "education","seniority" } }] }
```
`currentLevel` and `gapScore` are `null` when UNASSESSED.

## Connections

Baselines feed the recommendation engine (same assembler call in
`get_recommendations_by_user_id`). Quiz passes and certificate uploads write
`EvidenceLog` rows that move these numbers. The chatbot receives the computed gaps
as request context.

## TODOs / edge cases

- Weights, half-lives, the adjacency table and `SYNERGY_CAP` are documented in the
  module's "honesty ledger" as reasoned defaults, **not empirically validated**.
- `ADJACENT_COMPETENCIES` uses ids like `comp_python`, while the catalog uses
  `comp_python_stats_017`-style ids — synergy likely never fires on real data.
- If `_assembler` fails to build at startup, the endpoint silently degrades to
  `baseline_results = {}` (everything UNASSESSED / self-report only).
- Sessions are opened with `next(get_db())` inside the endpoint rather than via
  `Depends(get_db)`.
- `routers/competency.py::/baseline` still uses the legacy count-based synergy path.
