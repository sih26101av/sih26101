# Admin Dashboard

Ministry-side view at `/admin` (role `admin` only), built on the shared `AppShell`
(see [learner-dashboard.md](learner-dashboard.md) for the shell components).

## Code

- `src/pages/AdminDashboard.tsx` — five in-page sections, `AdminTab = 'dashboard' |
  'officials' | 'competencies' | 'analytics' | 'reports'` (state only, **no** new
  routes, so the single `/admin` guard still covers everything).
  - `dashboard` → 4 `StatCard`s (total officials, FRAC competencies, training
    compliance, avg missing skills) + `shortageChart` + `deptChart` + "Officials
    Needing Training" + "Data Sources" + the Generate Report banner.
  - `officials` → status filter chips (`statusFilter`), paginated `RosterRow` table,
    CSV export.
  - `competencies` → paginated `SkillTableRow` table, CSV export.
  - `analytics` → status tiles + both charts at full height.
  - `reports` → three export cards.
  - Helpers: `ITEMS_PER_PAGE = 10`, `enrollmentLabel(status)`, `STATUS_CHIP`,
    `downloadCsv`, `Pagination`, `TableSkeleton`, `ErrorBanner`, `FeedStatus`.
  - Charts are derived from live data: `shortageChart` renders the hook's `heatmap`
    (previously ignored in favour of a hardcoded array); `deptChart` renders
    `deptCompliance`, the per-department completion rate computed from the roster.
  - The topbar search is wired to `searchTerm` (it used to be a dead input), and the
    "Filters" button is replaced by working status chips.
- `src/hooks/useAdminData.ts` — fetches the roster via `fetchAllUsers()`, derives
  `AdminRosterRow`, `AdminKPIs` and `HeatmapEntry[]`; `levelToNumber` parses
  `"Level 3"`; `GAP_COLORS` drives the heatmap palette.
- `src/hooks/useSkillsData.ts` — FRAC dictionary via `fetchCompetencies()`
  (`SkillRow = FracCompetency`).
- `src/services/api.ts` — `fetchAllUsers()` → `GET /api/v1/admin/users`,
  `fetchCompetencies()` → `GET /api/v1/admin/frac/competencies`.
- Backend: `main-lms-backend/main.py::get_admin_roster` and
  `get_frac_competencies` — both `Depends(require_role("admin"))`, proxy to the mock
  server with `x-authenticated-user-token`, and return the unwrapped `result`.
- Route guard: `<ProtectedRoute requiredRole="admin">` in `src/App.tsx`.

## In / out

- In: admin JWT.
- Out (roster): `{users: [{userId, govId, firstName, lastName, email, designation,
  department, competencies[], enrollmentStatus, missingSkill}], count}`.
- Out (FRAC): `{competencies: [{competency_id, name, category, description}], count}`.

## Connections

The backend is the single auth-enforcement point — the admin UI never calls port
8001 directly. Data originates from the mock server's generated (synthetic)
`data/userdata.json` and `data/frac_competencies.json`; the FRAC table now lists
the 40 catalogue competencies roles are defined in (the 331-entry iGOT CID
dictionary is still served by the mock at `?dictionary=igot`).

## TODOs / edge cases

- The hardcoded demo constants (`SPARKLINE_DATA`, `PIE_DATA`, the static bar-chart
  array, and the `151` / `2.4` / `87%` KPI fallbacks) have been removed. Empty data
  now renders as an empty state rather than invented numbers.
- No time-series data exists anywhere in the API, so there is no "user growth over
  time" chart; the slot holds departmental compliance instead.
- There is no activity-feed or service-health endpoint. "Data Sources" reports the
  real load state of the two hooks; it is not a health probe.
- KPIs, the heatmap and departmental compliance are computed client-side over the
  full roster on every load; there is no server-side aggregation or pagination.
- The roster proxy has no timeout tuning beyond 15 s and no retry; a mock-server
  outage surfaces as an httpx exception → 500.
- Admin still has no write actions (no CBP assignment, no user edit). The only
  outbound actions are the three client-side CSV exports.
