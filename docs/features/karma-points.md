# Karma Points (gamification)

iGOT-style points ledger: immutable events, per-event-type strategies, a monthly
cap on non-CBP completions, and a login streak.

## Code

- `main-lms-backend/services/karma_engine.py`
  - `IKarmaStrategy.compute(userId, metadata, db) -> AwardResult` (Strategy pattern).
  - Concrete strategies: `RegistrationKarmaStrategy` (+5 one-time),
    `EnrollmentKarmaStrategy` (+5 first enrollment ever),
    `CompletionKarmaStrategy` (+5; non-CBP capped at 4 per calendar month via
    `KarmaMonthlyUsage`; CBP courses exempt), `AssessmentKarmaStrategy` (+5 per pass),
    `RatingKarmaStrategy` (+2), `CbpBonusKarmaStrategy` (+10, idempotent per courseId,
    retroactive-safe).
  - `KarmaEngine` (module singleton `karma_engine`): `award`, `get_balance`,
    `get_ledger`, `get_monthly_usage`, `get_breakdown`, `get_streak`,
    `seed_from_enrollments`, `_increment_monthly_usage`.
  - DTOs `AwardResult(points_awarded, cap_reached, already_claimed)` and
    `MonthlyUsage(used, cap=4)`.
- `main-lms-backend/models/models.py` — `KarmaEventType` enum, `KarmaEvent`
  (immutable ledger row), `KarmaMonthlyUsage` (year/month counter).
- `main-lms-backend/routers/karma.py` (mounted at `/api/v1`)
  - `GET /learner/{user_id}/karma` — auto-seeds from real iGOT enrollments on the
    first visit so the card is never blank, then returns balance, streak, monthly
    usage, per-type breakdown and the 10 most recent events.
  - `POST /learner/{user_id}/karma/event` — award by `eventType`.
  - `POST /learner/{user_id}/karma/claim-cbp-bonus` — retroactive +10.
  - `_assert_self_or_admin` — learners may only touch their own ledger.
- Frontend: `src/services/api.ts` (`fetchKarmaLedger` — returns `null` instead of
  throwing, `awardKarmaEvent`, `claimCbpBonus`),
  `src/components/dashboard/RightSidebar.tsx` (`KarmaCard`, `PassbookRow`,
  `MonthlyCapBar`, activity pills, donut), types in `src/types/domain.ts`.

## In / out

- In: `{eventType, courseId?, isCbp, is_mdo_onboarded}` + JWT.
- Out (ledger): `{userId, totalPoints, streak, monthlyUsage{used,cap,remaining},
  breakdown{EVENT_TYPE: points}, ledger[{eventId,eventType,pointsAwarded,courseId,
  isCbp,createdAt}]}`.
- Out (award): `{pointsAwarded, capReached, newBalance}`.

## Connections

Seeds itself from `MockIgotAdapter.fetch_user_enrollments`. Rendered in the learner
dashboard's right sidebar. Shares `auth.db` with auth and evidence tables.

## TODOs / edge cases

- `KarmaEvent.userId` / `KarmaMonthlyUsage.userId` declare a FK to `users.uuid`, but
  the router writes **iGOT userIds**. This only works because SQLite does not enforce
  foreign keys by default — the FK should be dropped like it was on `EvidenceLog`.
- Nothing awards karma automatically: passing a quiz or completing a course does not
  fire an event unless the frontend calls the award endpoint (see the missing
  Observer/EventBus in `ARCHITECTURE.md` §7).
- Monthly usage uses `datetime.utcnow()` — month boundaries are UTC, not IST.
- `AssessmentKarmaStrategy` and `RatingKarmaStrategy` have no idempotency guard;
  repeated calls keep awarding points.
- Seeding runs inside the GET request and is skipped (with a `print`, not a log) if
  the mock server is offline.
