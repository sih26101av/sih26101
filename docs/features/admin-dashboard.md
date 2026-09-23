# Admin Dashboard

Ministry-side view at `/admin` (role `admin` only), built on the shared `AppShell`
(see [learner-dashboard.md](learner-dashboard.md) for the shell components).
Everything except the FRAC dictionary is computed on the server by the **admin
console** (`routers/admin_console.py`). The browser gets one page or one
aggregate at a time. It never downloads and aggregates the whole roster.

## Code

### Frontend
- `src/pages/AdminDashboard.tsx` — eight in-page sections, `AdminTab =
  'dashboard' | 'officials' | 'competencies' | 'analytics' | 'emerging' |
  'actions' | 'insights' | 'reports'`. These are state only, **not** routes, so the
  single `/admin` guard still covers everything.
  - **Shared filters.** One `AdminFilters` state `{department, grade, office}`
    feeds every per-official view and every export, through `AdminFilterBar`.
    The `competencies` tab is excluded because the FRAC dictionary isn't
    per-official. On `insights`, the office filter drives the GSBPM scope panel
    (`WorkforceInsights office=…`). The product-level panels there stay NSO-wide.
  - `dashboard` has:
    - 4 `StatCard`s: officials, training compliance, mandatory (ACBP)
      completion, and avg missing skills;
    - a compact `TrendsPanel`, the shortage chart and the department chart
      (the 5 largest departments);
    - "Officials needing training" and a compact `SystemHealthPanel`;
    - a CTA to Emerging Skills.
  - `officials` shows a server-paginated roster (`useAdminRoster`), status chips
    with server counts, the grade and mandatory progress columns, and CSV/PDF
    export. Search is debounced by 300 ms.
  - `competencies` shows the FRAC dictionary, paginated client-side (40 rows),
    with a client CSV export.
  - `analytics` shows the status tiles, the full `TrendsPanel`, the shortage index
    and the department chart (all departments with at least 5 officials,
    compliance % and mandatory % side by side), each with CSV/PDF.
  - `emerging` → `components/admin/EmergingSkills.tsx`.
  - `actions` → `components/admin/AdminActions.tsx` + `CertificateReviewQueue.tsx`
    (approve/reject external certificates: documented → verified; see
    [certificate-evidence-extraction.md](certificate-evidence-extraction.md)).
  - `insights` → `components/admin/WorkforceInsights.tsx`. See
    [workforce-insights.md](workforce-insights.md).
  - `reports` has six export cards: roster, behind on mandatory, emerging skills,
    trends, departments and shortages. Each card has CSV and PDF.
- **Mobile/tablet.** KPI tiles are 2-up (dashboard) and 3-up (analytics status) on
  phones; data tables (roster, behind-on-mandatory, Insights) scroll horizontally inside
  their panel. Shell behaviour is shared — see "Responsive layout" in
  [learner-dashboard.md](learner-dashboard.md).
- `src/hooks/useAdminData.ts`:
  - `useAsync(fn, key)` is a generic loader with refetch; it drops stale
    responses.
  - `useAdminFacets`, `useAdminOverview(filters)`,
    `useAdminRoster(filters, page, size, search, status)`, `filterKey`.
- `src/components/admin/`:
  - `AdminFilterBar.tsx`: the three facet selects with headcounts, `ExportButton`
    and `facetLabels`. Below `sm` the selects stack full width (filter icon hidden).
  - `TrendsPanel.tsx`: one point per day for the range (30d / 90d / 1y).
    - **Training rates (%)**: trained in the last 12 months
      (`trainedLast12mPct`), mandatory completion, and competencies at target.
      The first is always from reconstruction (exact, also on snapshot days);
      mandatory comes from snapshots or reconstruction; "at target" exists only
      on snapshot days. A dashed marker shows where the daily snapshots begin.
      The cumulative `compliancePct` ("ever completed ≥1 course") is no longer
      plotted: it only rises and sits at 100% on this roster.
    - **Course completions per week**: a bar chart.
    - **Average FRAC level**: a line once there are two or more daily
      snapshots, until then today's value as text.
    - The compact dashboard version shows rates + weekly completions. The full
      version adds "Snapshot now" and CSV.
  - `SystemHealthPanel.tsx`: per-component status chips (icon + label). "Live
    check" re-probes everything, including a real Gemini call.
  - `EmergingSkills.tsx`: shortlist cards, a grouped bar chart (required / supply
    today / expected in 36 m) and a full ranked table, with CSV/PDF.
  - `AdminActions.tsx`: the assign-plan form (catalogue search, department or
    selected officials, due date), the "behind on mandatory" table (selection,
    nudge selected / nudge all in view, custom message), the assigned plans
    with progress bars, and the recent nudges log.
  - `AdminChatWidget.tsx`: Gyan on the console — the floating assistant, mounted
    in `AdminDashboard.tsx`. It posts to `/api/v1/admin/console/chat` and answers
    from the same aggregates these panels use, so the two can't disagree. The
    filter bar is passed down as the default scope, and a `tab` action switches
    `activeTab` while a `redirect` navigates. See
    [chatbot-gyan.md](chatbot-gyan.md).
  - `adminReport.ts`: `printReport` (a print-styled HTML report in a new window
    → the browser's "Save as PDF") and `describeFilters`.
  - Chart colours come from a palette checked with the dataviz validator:
    `#1d4ed8 / #ea580c / #0d9488` (light) and `#3b82f6 / …` (dark), in fixed
    order.
- `src/services/api.ts` (section "ADMIN CONSOLE") has the typed fetchers for
  every endpoint below, plus `downloadAdminCsv(kind, filters, extra)`, an
  authenticated blob download with 401 refresh.

### Backend
- `routers/admin_chat.py`: the assistant's admin tier — `POST /chat` and
  `GET /chat/mode` under the same `/api/v1/admin/console` prefix and the same
  `require_role("admin")`. It reads `admin_console._roster()` and
  `services/admin_chat_data.py` rather than re-querying iGOT.
- `routers/admin_console.py`:
  - Admin endpoints use `require_role("admin")` and sit under
    `/api/v1/admin/console`.
  - The roster comes from `MockIgotAdapter.fetch_user_roster()`. It is
    normalised and cached for 60 s; when the mock is down, the stale copy is
    served.
- `services/admin_analytics.py`: pure functions `normalise`, `Filters`,
  `search`, `paginate`, `facets`, `kpis`, `heatmap`, `dept_compliance`,
  `mandatory_summary`, `daily_metrics`, `trend_point` and `emerging_skills`.
  Tests: `tests/test_admin_analytics.py`, `tests/test_admin_console_api.py`
  (in-memory SQLite).
- `services/system_health.py`:
  - `basic()` is the `GET /health` payload (main.py now returns it).
  - `detailed(probe_gemini)` adds probes: iGOT `/health` with latency, the
    auth DB (`SELECT 1`; SQLite counts as degraded), the engine, the reference
    datasets, the workforce snapshot, the catalogue and chat embedders, the Gyan
    semantic tier, and Gemini. Without `probeGemini`, Gemini only checks that a
    key is configured; with it, it calls `list_models` with a 10 s timeout.
- `models/models.py` adds three tables to the auth DB (created by
  `main._create_schema`):
  - `AdminDailySnapshot`: `snapshotDate` PK and `metrics` JSON;
  - `TrainingAssignment`;
  - `TrainingNudge`.
- `main.py`:
  - includes `admin_console.router` + `learner_router` + `admin_chat.router`;
  - `_startup` launches `daily_snapshot_loop()`;
  - the legacy `GET /api/v1/admin/users` and `/admin/frac/competencies` proxies
    are unchanged.
- The mock roster (`GET /api/admin/v1/users`) now also returns `grade`,
  `officeId`, `officeName`, `roleId`, `completedCourseIds` and `mandatory`. See
  [mock-igot-integration.md](mock-igot-integration.md).

## Endpoints (`/api/v1/admin/console`, all take `?department=&grade=&office=`)

| Method | Path | Returns |
|---|---|---|
| GET | `/filters` | `{departments, grades, offices}`: `[{value, label, count}]` over the whole roster |
| GET | `/overview` | `{kpis{totalOfficials, trainingCompliancePct, avgMissingSkills, mandatory{officialsWithPlan, behind, coursesAssigned, coursesCompleted, completionPct}, suppressed}, statusCounts, heatmap[{competency, gap, officials}], deptCompliance[{dept, headcount, pct, mandatoryPct, behindMandatory, suppressed}], needsTraining[5]}` |
| GET | `/roster?page=&pageSize=&search=&status=` | `{items[AdminRosterRow], total, page, pageSize, totalPages, statusCounts}` |
| GET | `/trends?days=` | `{points[{date, reconstructed, officials, compliancePct, trainedLast12mPct, mandatoryCompletionPct, behindMandatory?, avgMissingSkills?, avgLevel?, atTargetPct?, assessedPct?}], weeklyCompletions[{weekStart, completions}], liveSnapshots, firstLiveSnapshot, scope, note}`: one point per day |
| POST | `/trends/snapshot` | upserts today's snapshot now |
| GET | `/courses?q=` | catalogue search for the assign form |
| GET/POST | `/assignments` | the plans assigned so far, with progress `{completedAll, completedSome, completionPct}` and `overdue` / create one |
| GET | `/mandatory-behind?page=&pageSize=&search=` | officials with pending ACBP courses, with `lastNudgedAt`, plus `summary` |
| GET/POST | `/nudges` | the nudge log / send nudges `{userIds?, department?, grade?, office?, message?, force?}` → `{sent, skipped[{userId, reason}]}` |
| GET | `/emerging-skills` | see below |
| POST | `/chat` | Gyan, answering from this console — see [chatbot-gyan.md](chatbot-gyan.md). Body `{message, history[], preferred_language, filters, full_name}` → `{reply, detected_language, engine, intent, navigate_action, navigate_actions}` |
| GET | `/chat/mode` | which tier of the assistant is live |
| GET | `/system-health?probeGemini=` | `{overall, checkedAt, health (= /health), components[{id, label, status, detail, latencyMs?}], lastDailySnapshot}` |
| GET | `/export/{kind}.csv` | kind: `roster` (also takes `search`, `status`), `mandatory-behind`, `emerging-skills`, `trends` (`days`), `departments`, `shortages` |

Learner side (the learner or an admin only):
- `GET /api/v1/learner/{id}/training-actions` returns
  `{nudges[], assignments[], unread}`.
- `POST /api/v1/learner/{id}/nudges/{nudgeId}/read` marks a nudge read.

## How the parts work

- **Daily snapshot.**
  - `daily_snapshot_loop` waits for the DB, then waits up to 10 min for the
    workforce snapshot so that the first row carries competency levels.
  - After that it **upserts today's row every hour**, so each day keeps its last
    reading.
  - A row stores the `overall` metrics plus `byDepartment`, `byGrade` and
    `byOffice`.
  - With several filters, a trend uses the most specific stored breakdown
    (office > department > grade), and the response says which. The stored
    breakdowns are one-dimensional, so exact combinations are not stored.
- **Reconstructed history.** `admin_analytics.reconstruct_history` is computed
  on read and never stored. It covers every day in range that has no stored
  snapshot:
  - `compliancePct` = officials whose first completion (from the mock
    roster's `completions[{courseId, completedDate}]`) falls on or before the
    day (cumulative; CSV only);
  - `trainedLast12mPct` = officials with a completion in the trailing
    `TRAINED_WINDOW_DAYS` (365) up to the day. `_trend_series` copies it onto
    stored-snapshot days too, since old snapshot rows don't carry it;
  - `mandatoryCompletionPct` = current-cycle ACBP courses (`mandatory.courseIds`)
    completed by the day, over all courses assigned;
  - `weeklyCompletions` = course completions per week.

  It is exact for any filter combination. Assumptions: the population is
  today's roster and the ACBP plan is today's, so courses completed before the
  cycle started count as done. A stored snapshot wins on its own day. Points
  are flagged `reconstructed: true/false`. Competency levels are never
  reconstructed.
- **Competency growth.**
  - `avgLevel`, `atTargetPct` and `assessedPct` come from the workforce snapshot
    (`app_state.snapshot`). They are `null` until the snapshot is built.
- **Assignments.**
  - Assignees are resolved when the assignment is created. For a department,
    that means the department narrowed by the grade / office in the body; for
    officials, the explicit `userIds`.
  - Course IDs are validated against the engine catalogue.
  - Progress is computed from `completedCourseIds` in the roster.
  - Nothing is pushed to iGOT. The mock has no CBP-assignment write API.
- **Nudges.**
  - Only officials whose ACBP `mandatory.completed < total` can be nudged.
  - There is a 24 h cooldown per official (`NUDGE_COOLDOWN_H`) unless
    `force`.
  - Each nudge row stores the courses that were pending at send time.
- **Emerging skills** (`admin_analytics.emerging_skills`), per FRAC competency,
  over the filtered officials in the workforce snapshot:
  - `required` = officials whose role sets a target on it.
  - `supplyNow` = those whose displayed level meets the target.
  - `expectedSupply36` = Σ P(in service at 36 m) × P(θ ≥ own target). θ is
    decayed with `workforce_service._p_capable`, which now takes an optional
    `threshold`. P(in service) = before superannuation × (1 − 0.03)³.
  - Assumptions: no new learning, and role demand held constant.
  - `priorityScore` = shortfall36 × 1.25 if in the GSBPM core × 1.25 if
    product-critical.
  - The top 10 with a shortfall are flagged `trainNextYear`.
  - `recommendedAction`, checked in this order:
    1. commission a course at the missing catalogue levels;
    2. otherwise, review existing courses if any are flagged for low uplift;
    3. otherwise, run a cohort programme;
    4. otherwise, monitor.
  - Counts of 1–4 are suppressed to `<5`.
- **Small cells.**
  - Departments, trend groups and KPI sets with fewer than 5 officials
    suppress their percentages.
  - Counts use `workforce_service.cell`.

## What the synthetic data shows

- FY2026-27 ACBP completion is 2.8%: 151 of 151 officials have at least one
  pending mandatory course, because the cycle has just started. Filter by
  department before using "Nudge all".
- Every official has `enrollmentStatus = 2`, so "training compliance" (at
  least one completed course) is 100%. The mandatory-completion KPI is the
  informative one. The trend chart therefore plots "trained in last 12 months"
  (~76–81% over the past year) instead.
- Emerging skills puts Survey Design, Price Statistics / CPI, Change
  Management, Leadership and Data Governance on top. As in the foresight view,
  the 6.5-month accuracy half-life drives most of the 36-month decline.

## TODOs / edge cases

- The assistant answers about any single official — including karma and nudge
  history — to anyone holding the admin role. Same data as the Officials tab and
  the roster CSV, one sentence away instead of three clicks.
- The assistant's scope is one filter set, like the panels: it has no "compare
  these two departments" answer.
- There is no learner UI yet for nudges and assignments. The endpoint exists
  (`/training-actions`); wiring it into the learner dashboard notifications is
  left for the learner-dashboard feature.
- Assignments are not pushed to iGOT, and completion only counts courses
  completed in iGOT enrolments.
- The roster is still fetched whole from the mock (cached for 60 s) and
  paginated in the backend. A real iGOT deployment would need server-side
  paging upstream.
- The trend breakdowns are one dimension each, so exact filter combinations
  are not stored.
- The PDF export uses the browser print dialog; pop-ups must be allowed. Roster
  and "behind" PDFs cap at 200 rows (the CSV has everything).
- Several backend instances sharing Neon each upsert the same daily row. This
  is harmless (last writer wins), but a unique-key race on the very first
  insert of a day is logged and retried by the next hourly tick.
