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

## TODOs / limits

- GSBPM **v5.1** sub-process list; "5.2" was requested but could not be
  confirmed. The map is data (`mock-igot-server/mockdata/domain.py`).
- Competency → sub-process links and office workloads are hand-designed
  synthetic data, not measured time use.
- Opportunity is per office, not per individual work allocation.
