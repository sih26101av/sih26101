# Authentication & RBAC

JWT access token + httpOnly refresh cookie, bcrypt passwords, role guards on both
backend and frontend. Login usernames **are iGOT userIds** (`usr_720465595`), which
makes the JWT subject the canonical identity used by evidence, quiz and karma tables.

## Code

Backend (`main-lms-backend/auth/`):
- `models.py` — `UserAuth` (`users_auth` table): username, password_hash, role,
  `must_change_password`, refresh-token hash. Uses its own declarative base `AuthBase`.
- `database.py` — SQLite engine at `main-lms-backend/auth.db`, `SessionLocal`, `get_db()`.
- `security.py` — `hash_password` / `verify_password` (bcrypt),
  `create_access_token` / `decode_access_token` (jose JWT),
  `generate_refresh_token` / `hash_refresh_token` / `verify_refresh_token`.
- `dependencies.py` — `get_current_user(Authorization: Bearer)` → `UserAuth`;
  `require_role(*roles)` factory returning a dependency that 403s on mismatch.
- `router.py` — `POST /auth/login`, `/auth/refresh`, `/auth/logout`,
  `/auth/change-password`, `GET /auth/me`. Refresh cookie name `refresh_token`,
  `REFRESH_TOKEN_EXPIRE_DAYS`, set/cleared by `_set_refresh_cookie` / `_clear_refresh_cookie`.
- `seed.py` — one-shot seeding. Fetches officials from the mock server
  (`GET :8001/api/admin/v1/users`), derives password = `lowercase(firstName) +
  last 2 digits of the userId suffix`, inserts `role="learner"`,
  `must_change_password=True`, plus a hardcoded `admin` / `admin123`. Idempotent.

Frontend:
- `src/context/AuthContext.tsx` — token in React state (never localStorage), silent
  `/auth/refresh` on mount, `mapRole()` maps server `learner` → UI `official`.
- `src/services/authApi.ts` — raw auth calls (`credentials: 'include'`).
- `src/services/api.ts` — `lmsFetch` injects `Authorization: Bearer`, and on 401
  refreshes once and retries; on second failure calls the registered logout callback
  and hard-navigates to `/login`. Bridged to context via `setApiToken` /
  `registerLogoutCallback` in `App.tsx` (`TokenBridge`).
- `src/components/ProtectedRoute.tsx` — redirects unauthenticated users to `/login`
  and forces `/change-password` when `must_change_password` is set; `requiredRole`
  prop enforces per-route roles.
- `src/patterns/DashboardFactory.ts` — role → destination route after login.

## In / out

- In: `{username, password}`; refresh cookie on subsequent calls.
- Out: `{access_token, token_type, role, must_change_password}`; `UserAuthOut` from `/auth/me`.
- CORS in `main.py` is pinned to `localhost:3000/5173` with `allow_credentials=True`
  (a wildcard origin would break the refresh cookie).

## Connections

Every learner/admin/karma endpoint depends on `get_current_user`. `require_role("admin")`
guards the two admin proxies in `main.py`. `routers/karma.py::_assert_self_or_admin`
adds per-record ownership checks. `routers/rag.py::grade_quiz` reads
`current_user.username` as the iGOT userId.

## TODOs / edge cases

- Seeding requires the mock server to be running first; re-running is safe.
- Role vocabulary is inconsistent across layers: DB `learner`, UI `official`,
  UML `Official`. `require_role("admin")` is the only role check on the backend —
  there is no backend `learner` guard beyond ownership checks in karma.
- `/trainer` route renders the learner dashboard; the `Trainer` role exists in
  `models/models.py` but is never seeded or used.
- Quiz endpoints in `AssessmentUploadZone.tsx` / `AssessmentPage.tsx` use bare
  `fetch` without the Authorization header — see `rag-quiz-generator.md`.
- Default seeded passwords are predictable by design (demo data); the forced
  change-password flow is the mitigation.
