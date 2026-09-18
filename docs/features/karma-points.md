# Karma Points (gamification)

A points system in the style of iGOT, Stack Overflow and Duolingo. Every award is an immutable ledger row, and the balance is the sum of those rows, so it persists in Neon Postgres. One rules table drives both the engine and the "How to earn" UI. Limits: a 50 KP daily cap, per-activity daily limits, and a monthly cap of 4 non-CBP completions. Also covers streaks, streak milestone bonuses, levels, rank, iGOT completion sync and admin adjustments. All day and month boundaries are **IST**.

## Rules (`RULES` in `karma_engine.py`, served by `GET /karma/rules`)

| Event | KP | Frequency / limit | Daily cap | Who awards |
|---|---|---|---|---|
| `DAILY_LOGIN` | +1 | once per IST day | exempt | check-in |
| `STREAK_BONUS` | +5 / +20 / +50 | at 7 / 30 / 100-day streak, once per milestone per streak run | exempt | check-in |
| `SELF_REGISTRATION` | +5 | one-time; MDO-onboarded users excluded | exempt | client (`/event`) or seed |
| `FIRST_ENROLLMENT` | +5 | one-time, verified against iGOT | exempt | iGOT sync / client |
| `COURSE_COMPLETION` | +5 | per course; non-CBP max 4 per IST month | counted | iGOT sync / client (verified status=2) |
| `ASSESSMENT_PASSED` | +5 | per quizId, first pass ≥70 %; max 5/day | counted | `rag.py` grading (document + media quizzes) |
| `DIAGNOSTIC_COMPLETED` | +5 | per diagnostic session; max 3/day | counted | `diagnostic.py` on finish |
| `COURSE_RATED` | +2 | per course (must be enrolled); max 5/day | counted | client (`/event`, verified) |
| `CBP_BONUS` | +10 | once per course; requires a recorded completion | exempt | `/claim-cbp-bonus` |
| `ADMIN_ADJUSTMENT` | ±n | with a reason; a deduction never takes the balance below 0 | exempt | `/admin/karma/{id}/adjust` |

The engine applies checks in this order (`KarmaEngine.award`):
1. **Idempotency.** Each event has a `referenceId` (quizId, courseId, IST date, `"once"`, session id, `"{days}d@{runStart}"`). The engine checks it before awarding, and a partial unique index `uq_karma_event_ref (userId, eventType, referenceId) WHERE referenceId IS NOT NULL` backs it under concurrency. An `IntegrityError` is reported as `alreadyClaimed`. Legacy rows without a referenceId are matched by `courseId`.
2. **Strategy.** It computes the base points: MDO exclusion, the monthly completion cap (CBP exempt), streak milestone points, and the admin clamp.
3. **Per-type daily limit.** This is `rule.per_day`.
4. **Daily cap.** At most `DAILY_CAP = 50` KP per IST day comes from capped events. An award that would cross the cap is trimmed to what is left (Stack Overflow-style). Once the cap is reached, the award is blocked.
5. **Persist.** A blocked idempotent action is written as a **0-point row with a `note`**. The passbook then explains why, and the action cannot be replayed later for points. Points over a limit are not banked.

Levels (`LEVELS`): Novice 0 · Learner 50 · Achiever 150 · Expert 300 · Champion 600 · Karmayogi 1000.

## Code

- `main-lms-backend/services/karma_engine.py`
  - IST helpers: `ist_now`, `ist_date`, `ist_day_start_utc`. Config: `DAILY_CAP`, `MONTHLY_COMPLETION_CAP`, `STREAK_MILESTONES`, `LEVELS`, `RULES` (`KarmaRule`), `rules_payload()`.
  - Strategies: `IKarmaStrategy`, `FixedPointsStrategy` (default), `RegistrationKarmaStrategy`, `CompletionKarmaStrategy`, `StreakBonusStrategy`, `AdminAdjustmentStrategy`.
  - `KarmaEngine` (singleton `karma_engine`)
    - Awards: `award`, `award_safe` (own session, never raises; used by server hooks), `check_in`, `sync_from_igot` (seeds an empty ledger, otherwise awards new iGOT completions and first enrolment), `seed_from_enrollments` (backdated history with referenceIds; bypasses caps).
    - Reads: `get_balance`, `get_ledger(limit, offset)`, `count_events`, `get_monthly_usage`, `get_breakdown`, `get_today`, `get_streak_stats` (current, longest, runStart), `get_level`, `get_rank`.
  - DTOs: `AwardResult` (`points_awarded`, `cap_reached`, `already_claimed`, `daily_cap_reached`, `daily_limit_reached`, `reason`) and `MonthlyUsage`.
  - `migrate_karma_schema(engine)` runs idempotently on every startup from `main._create_schema`. It adds the `referenceId` and `note` columns, adds the new Postgres `karmaeventtype` enum values (autocommit), and creates the unique index.
- `main-lms-backend/models/models.py` holds `KarmaEventType`, `KarmaEvent` (now with `referenceId` and `note`) and `KarmaMonthlyUsage`.
- `main-lms-backend/routers/karma.py` is mounted at `/api/v1`, and its DB work runs in the threadpool:
  - `GET /karma/rules` returns the rules, caps, milestones and levels.
  - `POST /learner/{id}/karma/check-in?limit=` does the iGOT sync and seed, the daily check-in and streak bonuses, then returns the summary plus `recentAwards`. The check-in is skipped when an admin views someone else.
  - `GET /learner/{id}/karma?limit=&offset=` returns the summary with a passbook page. It is read-only apart from the first-visit seed.
  - `POST /learner/{id}/karma/event` accepts only rules with `client_awardable`. Completion, rating and first enrolment are verified against `MockIgotAdapter.fetch_user_enrollments`; the endpoint returns 409 if not proven and 503 if iGOT is down. Server-only types return 403.
  - `POST /learner/{id}/karma/claim-cbp-bonus` requires a `COURSE_COMPLETION` row for that course.
  - `POST /admin/karma/{id}/adjust` (`{points, reason}`) is admin only.
  - `_assert_self_or_admin` means learners only ever touch their own ledger.
- Server award hooks:
  - `routers/rag.py` `grade_quiz` fires on the first submission that passes. It sets `GradeResponse.karmaAwarded` and `karmaNote`, and adds "+N Karma Points earned." to `message`.
  - `routers/diagnostic.py` `_write_evidence` fires when a diagnostic finishes.
- Frontend:
  - `src/components/karma/KarmaRewardsView.tsx` is the Karma & Rewards tab. It contains the check-in banner, stat tiles (balance and level, today vs cap, streak, rank), the level ladder, **How to earn** (rendered from `/karma/rules`), rules & limits, unclaimed CBP bonuses, a passbook with filter and load-more, and an FAQ.
  - `src/components/karma/karmaMeta.tsx` has `EVENT_META` (label, icon and colour per type), `metaFor` and `formatPoints`.
  - `src/services/api.ts` has `fetchKarmaLedger`, which POSTs to check-in and returns `null` on error. It also has `fetchKarmaHistory`, `fetchKarmaRules`, `awardKarmaEvent` and `claimCbpBonus`.
  - The types are in `src/types/domain.ts`: `KarmaLedger`, `KarmaLevel`, `KarmaToday`, `KarmaAward`, `KarmaRule(s)` and `KarmaTransaction`.
  - `src/components/dashboard/RightSidebar.tsx` (compact `KarmaCard` + career card) is **no longer mounted**.

## In / out

- Summary is `{userId, totalPoints, level{rank,name,minPoints,nextName,nextMinPoints,pointsToNext,progressPct}, today{earned,totalEarned,cap,remaining,checkedIn,resetsAt}, streak, longestStreak, rank{position,totalLearners,topPercent}, monthlyUsage{used,cap,remaining}, breakdown{TYPE: pts}, totalEvents, ledger[{eventId,eventType,pointsAwarded,courseId,isCbp,referenceId,note,createdAt(Z)}], recentAwards[AwardResult]}`.
- Award / claim / adjust returns `{userId, eventType, pointsAwarded, capReached, alreadyClaimed, dailyCapReached, dailyLimitReached, reason, newBalance, monthlyUsage, today}`.

## Connections

- Seeding and sync use `MockIgotAdapter.fetch_user_enrollments`.
- Quiz and diagnostic grading call `karma_engine.award_safe` directly. There is still no EventBus/Observer (`ARCHITECTURE.md` §7).
- Karma shares the auth DB engine (Neon Postgres; see `auth-and-rbac.md`).
- The dashboard hook (`useLearnerDashboard`) triggers the check-in on every load, and the Karma tab re-runs it on mount.

## TODOs / edge cases

- `KarmaEvent.userId` / `KarmaMonthlyUsage.userId` store **iGOT userIds** with no FK (same as `EvidenceLog`).
- Mock enrollments carry no CBP flag, so iGOT-synced completions count as non-CBP unless an enrollment has `isCbp`. The seeder still treats every third fully-completed course as CBP.
- Nothing on the site calls `/event` for `COURSE_RATED` yet (there is no rating UI). The endpoint is ready.
- The certificate upload (`/upload-certificate`) is unauthenticated and writes no evidence, so it earns no karma.
- Rank counts only learners with at least one ledger row. There is no public leaderboard, by design, for privacy.
- There is no admin UI for adjustments yet. Use the endpoint.
- `KarmaMonthlyUsage` rows written before the IST switch used UTC months. This only matters within 5.5 h of a month boundary.
