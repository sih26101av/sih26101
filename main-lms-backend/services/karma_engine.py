"""
services/karma_engine.py
─────────────────────────────────────────────────────────────────────────────
PATTERN: Strategy Pattern  (mirrors IRecommendationStrategy in the Mermaid diagram)

RULES (single source of truth — also served to the UI by GET /karma/rules)
  DAILY_LOGIN            +1   once per IST day                    (cap-exempt)
  STREAK_BONUS     +5/+20/+50 at 7/30/100 consecutive days        (cap-exempt)
  SELF_REGISTRATION      +5   one-time                            (cap-exempt)
  FIRST_ENROLLMENT       +5   one-time                            (cap-exempt)
  COURSE_COMPLETION      +5   per course; non-CBP max 4 / month
  ASSESSMENT_PASSED      +5   per quiz, first pass ≥70 %; max 5 / day
  DIAGNOSTIC_COMPLETED   +5   per adaptive diagnostic; max 3 / day
  COURSE_RATED           +2   per course; max 5 / day
  CBP_BONUS             +10   once per CBP-mandated course         (cap-exempt)
  ADMIN_ADJUSTMENT      ±n    admin grant / deduction              (cap-exempt)

  Daily cap: at most DAILY_CAP (50) KP per IST day from capped events. An award
  that would cross the cap is trimmed to what is left (Stack Overflow-style);
  blocked awards are written as 0-point passbook rows with a note, so the
  learner sees why and the same action cannot be re-tried for points later.

IKarmaStrategy          <<interface>>   compute(userId, metadata, db) -> AwardResult
KarmaEngine             (context class)
  award / award_safe / check_in / sync_from_igot / seed_from_enrollments
  get_balance / get_ledger / get_monthly_usage / get_breakdown / get_streak_stats
  get_today / get_level / get_rank
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.models import KarmaEvent, KarmaEventType, KarmaMonthlyUsage

log = logging.getLogger(__name__)

E = KarmaEventType

# --- Time: all karma day/month boundaries are IST ------------------------------

IST = timedelta(hours=5, minutes=30)


def ist_now() -> datetime:
    """Naive IST wall-clock time (createdAt is stored as naive UTC)."""
    return datetime.utcnow() + IST


def ist_date(utc_naive: datetime) -> date:
    return (utc_naive + IST).date()


def ist_day_start_utc(d: date) -> datetime:
    return datetime.combine(d, time.min) - IST


# --- Rules ----------------------------------------------------------------------

DAILY_CAP = 50                     # KP per IST day from capped events
MONTHLY_COMPLETION_CAP = 4         # non-CBP course completions per IST month
STREAK_MILESTONES: Dict[int, int] = {7: 5, 30: 20, 100: 50}
ONCE = "once"                      # referenceId for one-time events


@dataclass(frozen=True)
class KarmaRule:
    event_type: KarmaEventType
    points: int
    title: str
    how: str
    frequency: str
    category: str                      # "engagement" | "learning" | "milestone" | "admin"
    per_day: Optional[int] = None      # max awards of this type per IST day
    daily_capped: bool = True          # counts toward DAILY_CAP
    client_awardable: bool = False     # learner may POST it to /karma/event

    def to_dict(self) -> dict:
        d = asdict(self)
        d["eventType"] = d.pop("event_type").value
        d["perDay"] = d.pop("per_day")
        d["dailyCapped"] = d.pop("daily_capped")
        d.pop("client_awardable")
        return d


RULES: Dict[KarmaEventType, KarmaRule] = {r.event_type: r for r in [
    KarmaRule(E.DAILY_LOGIN, 1, "Daily check-in",
              "Open your learner dashboard on any day.",
              "Once per day", "engagement", per_day=1, daily_capped=False),
    KarmaRule(E.STREAK_BONUS, 5, "Streak bonus",
              "Stay active on consecutive days: +5 at 7 days, +20 at 30 days, +50 at 100 days.",
              "Once per milestone per streak", "engagement", daily_capped=False),
    KarmaRule(E.SELF_REGISTRATION, 5, "Registration bonus",
              "Self-register on iGOT Karmayogi (not MDO-onboarded).",
              "One-time", "milestone", daily_capped=False, client_awardable=True),
    KarmaRule(E.FIRST_ENROLLMENT, 5, "First enrolment",
              "Enrol in your first course on iGOT Karmayogi.",
              "One-time", "milestone", daily_capped=False, client_awardable=True),
    KarmaRule(E.COURSE_COMPLETION, 5, "Course completion",
              "Complete a course on iGOT. CBP-mandated courses are exempt from the monthly limit.",
              f"Per course · max {MONTHLY_COMPLETION_CAP} non-CBP per month", "learning",
              client_awardable=True),
    KarmaRule(E.ASSESSMENT_PASSED, 5, "Assessment passed",
              "Score 70 % or more on a document, video or YouTube quiz (first pass only).",
              "Per quiz · max 5 per day", "learning", per_day=5),
    KarmaRule(E.DIAGNOSTIC_COMPLETED, 5, "Diagnostic completed",
              "Finish an adaptive competency diagnostic from Assessments.",
              "Per diagnostic · max 3 per day", "learning", per_day=3),
    KarmaRule(E.COURSE_RATED, 2, "Course feedback",
              "Rate a course you are enrolled in.",
              "Per course · max 5 per day", "engagement", per_day=5, client_awardable=True),
    KarmaRule(E.CBP_BONUS, 10, "CBP mandated bonus",
              "Complete a course mandated in your Capacity Building Plan, then claim the bonus.",
              "Once per CBP course", "milestone", daily_capped=False),
    KarmaRule(E.ADMIN_ADJUSTMENT, 0, "Admin adjustment",
              "Manual grant or correction by an administrator, always with a reason.",
              "As needed", "admin", daily_capped=False),
]}

CAPPED_TYPES = [t for t, r in RULES.items() if r.daily_capped]

# Levels: (minimum points, name)
LEVELS: List[Tuple[int, str]] = [
    (0, "Novice"), (50, "Learner"), (150, "Achiever"),
    (300, "Expert"), (600, "Champion"), (1000, "Karmayogi"),
]


def rules_payload() -> dict:
    return {
        "dailyCap": DAILY_CAP,
        "monthlyCompletionCap": MONTHLY_COMPLETION_CAP,
        "streakMilestones": [{"days": d, "points": p} for d, p in STREAK_MILESTONES.items()],
        "levels": [{"name": n, "minPoints": m} for m, n in LEVELS],
        "rules": [r.to_dict() for r in RULES.values()],
        "timezone": "Asia/Kolkata",
    }


# --- Result DTOs -----------------------------------------------------------------

@dataclass
class AwardResult:
    points_awarded: int
    cap_reached: bool = False          # monthly non-CBP completion cap
    already_claimed: bool = False      # idempotent event already in the ledger
    daily_cap_reached: bool = False    # DAILY_CAP hit (award trimmed or blocked)
    daily_limit_reached: bool = False  # per-event-type daily limit hit
    event_type: Optional[str] = None
    reason: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "eventType": self.event_type,
            "pointsAwarded": self.points_awarded,
            "capReached": self.cap_reached,
            "alreadyClaimed": self.already_claimed,
            "dailyCapReached": self.daily_cap_reached,
            "dailyLimitReached": self.daily_limit_reached,
            "reason": self.reason,
        }


@dataclass
class MonthlyUsage:
    used: int
    cap: int = MONTHLY_COMPLETION_CAP

    @property
    def remaining(self) -> int:
        return max(0, self.cap - self.used)

    def to_dict(self) -> dict:
        return {"used": self.used, "cap": self.cap, "remaining": self.remaining}


# --- IKarmaStrategy interface ------------------------------------------------------

class IKarmaStrategy(ABC):
    """
    Computes the base points for an event (before the engine's idempotency,
    per-day limit and daily-cap checks). Returns 0 points when ineligible.
    """
    @abstractmethod
    def compute(self, userId: str, metadata: dict, db: Session) -> AwardResult:
        ...


class FixedPointsStrategy(IKarmaStrategy):
    """Awards the rule's fixed points; eligibility is left to the engine."""
    def __init__(self, event_type: KarmaEventType) -> None:
        self.event_type = event_type

    def compute(self, userId: str, metadata: dict, db: Session) -> AwardResult:
        return AwardResult(RULES[self.event_type].points)


class RegistrationKarmaStrategy(IKarmaStrategy):
    """+5 on self-registration; MDO-onboarded users are not eligible."""
    def compute(self, userId: str, metadata: dict, db: Session) -> AwardResult:
        if metadata.get("is_mdo_onboarded", False):
            return AwardResult(0, reason="MDO-onboarded users do not earn the registration bonus.")
        return AwardResult(RULES[E.SELF_REGISTRATION].points)


class CompletionKarmaStrategy(IKarmaStrategy):
    """+5 per completion; non-CBP completions capped per IST calendar month."""
    MONTHLY_CAP = MONTHLY_COMPLETION_CAP

    def compute(self, userId: str, metadata: dict, db: Session) -> AwardResult:
        pts = RULES[E.COURSE_COMPLETION].points
        if metadata.get("isCbp", False):
            return AwardResult(pts)
        if karma_engine.get_monthly_usage(userId, db).used >= self.MONTHLY_CAP:
            return AwardResult(0, cap_reached=True,
                               reason=f"Monthly limit of {self.MONTHLY_CAP} non-CBP completions reached.")
        return AwardResult(pts)


class StreakBonusStrategy(IKarmaStrategy):
    """Milestone-dependent points, passed in by KarmaEngine.check_in."""
    def compute(self, userId: str, metadata: dict, db: Session) -> AwardResult:
        return AwardResult(int(STREAK_MILESTONES.get(metadata.get("milestone"), 0)))


class AdminAdjustmentStrategy(IKarmaStrategy):
    """Signed admin grant / deduction. A deduction never takes the balance below 0."""
    def compute(self, userId: str, metadata: dict, db: Session) -> AwardResult:
        pts = int(metadata.get("points", 0))
        if pts < 0:
            pts = -min(-pts, karma_engine.get_balance(userId, db))
        return AwardResult(pts)


# --- KarmaEngine (context class) -----------------------------------------------------

class KarmaEngine:
    """
    Dispatches an eventType to its strategy, then applies the shared rules in
    order: idempotency → per-day limit → daily cap, and appends an immutable
    ledger row.
    """

    def __init__(self) -> None:
        self._strategies: Dict[KarmaEventType, IKarmaStrategy] = {
            t: FixedPointsStrategy(t) for t in RULES
        }
        self._strategies.update({
            E.SELF_REGISTRATION: RegistrationKarmaStrategy(),
            E.COURSE_COMPLETION: CompletionKarmaStrategy(),
            E.STREAK_BONUS:      StreakBonusStrategy(),
            E.ADMIN_ADJUSTMENT:  AdminAdjustmentStrategy(),
        })

    # -- Award ---------------------------------------------------------------------

    @staticmethod
    def reference_for(event_type: KarmaEventType, metadata: dict) -> Optional[str]:
        """Idempotency key for an event; None means 'not idempotent' (admin only)."""
        if event_type in (E.SELF_REGISTRATION, E.FIRST_ENROLLMENT):
            return ONCE
        if event_type == E.DAILY_LOGIN:
            return ist_now().date().isoformat()
        if event_type == E.ADMIN_ADJUSTMENT:
            return None
        if event_type in (E.COURSE_COMPLETION, E.COURSE_RATED, E.CBP_BONUS):
            return metadata.get("referenceId") or metadata.get("courseId")
        return metadata.get("referenceId")

    def award(
        self,
        userId: str,
        event_type: KarmaEventType,
        metadata: dict,
        db: Session,
    ) -> AwardResult:
        rule = RULES.get(event_type)
        strategy = self._strategies.get(event_type)
        if rule is None or strategy is None:
            return AwardResult(0, already_claimed=True, event_type=event_type.value,
                               reason="Unknown event type.")

        ref = self.reference_for(event_type, metadata)
        if ref is None and event_type != E.ADMIN_ADJUSTMENT:
            return AwardResult(0, event_type=event_type.value,
                               reason="A courseId / referenceId is required for this event.")

        # 1. Idempotency — each action earns once
        if ref is not None and self._already(userId, event_type, ref, db):
            return AwardResult(0, already_claimed=True, event_type=event_type.value,
                               reason="Already awarded for this activity.")

        # 2. Strategy (eligibility + base points)
        result = strategy.compute(userId, metadata, db)
        result.event_type = event_type.value
        if result.points_awarded == 0 and not result.cap_reached:
            return result

        # 3. Per-event-type daily limit
        today = ist_now().date()
        if rule.per_day is not None and result.points_awarded > 0:
            if self._count_today(userId, event_type, today, db) >= rule.per_day:
                result.points_awarded = 0
                result.daily_limit_reached = True
                result.reason = f"Daily limit of {rule.per_day} × {rule.title} reached."

        # 4. Global daily cap (trim, then block)
        if rule.daily_capped and result.points_awarded > 0:
            remaining = DAILY_CAP - self.get_today(userId, db)["earned"]
            if remaining <= 0:
                result.points_awarded = 0
                result.daily_cap_reached = True
                result.reason = f"Daily cap of {DAILY_CAP} KP reached."
            elif result.points_awarded > remaining:
                result.points_awarded = remaining
                result.daily_cap_reached = True
                result.reason = f"Trimmed to the {DAILY_CAP} KP daily cap."

        # 5. Persist. Blocked idempotent actions are recorded as 0-point rows so the
        #    passbook explains them and they can't be replayed later for points.
        if result.points_awarded == 0 and ref is None:
            return result
        note = metadata.get("note")
        if result.reason and (result.points_awarded == 0 or result.daily_cap_reached):
            note = f"{note} — {result.reason}" if note else result.reason
        entry = KarmaEvent(
            eventId=str(uuid.uuid4()),
            userId=userId,
            eventType=event_type,
            pointsAwarded=result.points_awarded,
            courseId=metadata.get("courseId"),
            isCbp=bool(metadata.get("isCbp", False)),
            createdAt=datetime.utcnow(),
            referenceId=ref,
            note=(note or None) and str(note)[:250],
        )
        db.add(entry)
        if (event_type == E.COURSE_COMPLETION and result.points_awarded > 0
                and not metadata.get("isCbp", False)):
            self._increment_monthly_usage(userId, db)
        try:
            db.commit()
        except IntegrityError:           # concurrent duplicate hit the unique index
            db.rollback()
            return AwardResult(0, already_claimed=True, event_type=event_type.value,
                               reason="Already awarded for this activity.")
        return result

    def award_safe(self, userId: str, event_type: KarmaEventType, metadata: dict) -> Optional[AwardResult]:
        """For server-side hooks (quiz grading, diagnostics): own session, never raises."""
        from auth.database import SessionLocal
        db = SessionLocal()
        try:
            return self.award(userId, event_type, metadata, db)
        except Exception as exc:
            db.rollback()
            log.warning("[karma] award %s for %s failed: %s", event_type.value, userId, exc)
            return None
        finally:
            db.close()

    # -- Daily check-in + iGOT sync ---------------------------------------------------

    def check_in(self, userId: str, db: Session) -> List[AwardResult]:
        """DAILY_LOGIN for today, then any streak milestone the current streak has reached."""
        awards = [self.award(userId, E.DAILY_LOGIN, {"note": "Daily check-in"}, db)]
        stats = self.get_streak_stats(userId, db)
        for days in STREAK_MILESTONES:
            if stats["current"] >= days and stats["runStart"]:
                awards.append(self.award(userId, E.STREAK_BONUS, {
                    "milestone": days,
                    "referenceId": f"{days}d@{stats['runStart']}",
                    "note": f"{days}-day streak",
                }, db))
        return [a for a in awards if a.points_awarded > 0]

    def sync_from_igot(self, userId: str, raw_enrollments: list, db: Session) -> List[AwardResult]:
        """
        Seeds an empty ledger from iGOT history; afterwards awards any newly
        completed courses (and the first-enrolment bonus) found on iGOT.
        """
        if not self.get_ledger(userId, db, limit=1):
            self.seed_from_enrollments(userId, raw_enrollments, db)
            return []
        awards: List[AwardResult] = []
        if raw_enrollments:
            awards.append(self.award(userId, E.FIRST_ENROLLMENT, {"note": "First enrolment"}, db))
        for e in raw_enrollments:
            if e.get("status") == 2 and e.get("courseId"):
                awards.append(self.award(userId, E.COURSE_COMPLETION, {
                    "courseId": e["courseId"],
                    "isCbp": bool(e.get("isCbp", False)),
                    "note": e.get("courseName") or e.get("name"),
                }, db))
        return [a for a in awards if a.points_awarded > 0]

    # -- Reads -------------------------------------------------------------------------

    def get_balance(self, userId: str, db: Session) -> int:
        total = (
            db.query(func.sum(KarmaEvent.pointsAwarded))
            .filter(KarmaEvent.userId == userId)
            .scalar()
        )
        return max(0, int(total or 0))

    def get_ledger(self, userId: str, db: Session, limit: int = 10,
                   offset: int = 0) -> List[KarmaEvent]:
        return (
            db.query(KarmaEvent)
            .filter(KarmaEvent.userId == userId)
            .order_by(KarmaEvent.createdAt.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def count_events(self, userId: str, db: Session) -> int:
        return db.query(func.count(KarmaEvent.eventId)).filter(KarmaEvent.userId == userId).scalar() or 0

    def get_monthly_usage(self, userId: str, db: Session) -> MonthlyUsage:
        now = ist_now()
        row = db.query(KarmaMonthlyUsage).filter(
            KarmaMonthlyUsage.userId == userId,
            KarmaMonthlyUsage.year  == now.year,
            KarmaMonthlyUsage.month == now.month,
        ).first()
        return MonthlyUsage(used=row.nonCbpCompletions if row else 0)

    def get_breakdown(self, userId: str, db: Session) -> dict:
        """Per-event-type total points."""
        rows = (
            db.query(KarmaEvent.eventType, func.sum(KarmaEvent.pointsAwarded))
            .filter(KarmaEvent.userId == userId)
            .group_by(KarmaEvent.eventType)
            .all()
        )
        return {row[0].value: int(row[1] or 0) for row in rows}

    def get_today(self, userId: str, db: Session) -> dict:
        """Capped points earned today (IST) against DAILY_CAP, plus all points today."""
        today = ist_now().date()
        start = ist_day_start_utc(today)
        base = db.query(func.sum(KarmaEvent.pointsAwarded)).filter(
            KarmaEvent.userId == userId, KarmaEvent.createdAt >= start,
        )
        capped = int(base.filter(KarmaEvent.eventType.in_(CAPPED_TYPES)).scalar() or 0)
        total = int(base.scalar() or 0)
        checked_in = db.query(KarmaEvent.eventId).filter(
            KarmaEvent.userId == userId, KarmaEvent.eventType == E.DAILY_LOGIN,
            KarmaEvent.referenceId == today.isoformat(),
        ).first() is not None
        resets_at = ist_day_start_utc(today + timedelta(days=1))
        return {
            "earned": capped,
            "totalEarned": total,
            "cap": DAILY_CAP,
            "remaining": max(0, DAILY_CAP - capped),
            "checkedIn": checked_in,
            "resetsAt": resets_at.isoformat() + "Z",
        }

    def get_streak_stats(self, userId: str, db: Session) -> dict:
        """
        Current and longest run of consecutive IST days with any karma activity.
        The current streak survives until the end of today if yesterday was active.
        """
        rows = db.query(KarmaEvent.createdAt).filter(KarmaEvent.userId == userId).all()
        days = sorted({ist_date(r[0]) for r in rows if r[0] is not None})
        if not days:
            return {"current": 0, "longest": 0, "runStart": None}

        longest, run = 1, 1
        for prev, cur in zip(days, days[1:]):
            run = run + 1 if cur - prev == timedelta(days=1) else 1
            longest = max(longest, run)

        today = ist_now().date()
        active = set(days)
        anchor = today if today in active else today - timedelta(days=1)
        current, d = 0, anchor
        while d in active:
            current += 1
            d -= timedelta(days=1)
        run_start = (d + timedelta(days=1)).isoformat() if current else None
        return {"current": current, "longest": max(longest, current), "runStart": run_start}

    def get_streak(self, userId: str, db: Session) -> int:
        return self.get_streak_stats(userId, db)["current"]

    @staticmethod
    def get_level(points: int) -> dict:
        idx = max(i for i, (m, _) in enumerate(LEVELS) if points >= m)
        cur_min, cur_name = LEVELS[idx]
        if idx + 1 < len(LEVELS):
            nxt_min, nxt_name = LEVELS[idx + 1]
            pct = round((points - cur_min) / (nxt_min - cur_min) * 100, 1)
        else:
            nxt_min, nxt_name, pct = None, None, 100.0
        return {
            "rank": idx + 1, "name": cur_name, "minPoints": cur_min,
            "nextName": nxt_name, "nextMinPoints": nxt_min,
            "pointsToNext": (nxt_min - points) if nxt_min is not None else 0,
            "progressPct": pct,
        }

    def get_rank(self, userId: str, db: Session) -> dict:
        totals = (
            db.query(KarmaEvent.userId, func.sum(KarmaEvent.pointsAwarded).label("pts"))
            .group_by(KarmaEvent.userId)
            .subquery()
        )
        learners = db.query(func.count()).select_from(totals).scalar() or 0
        mine = self.get_balance(userId, db)
        above = db.query(func.count()).select_from(totals).filter(totals.c.pts > mine).scalar() or 0
        position = above + 1
        top_pct = round(position / learners * 100, 1) if learners else 100.0
        return {"position": position, "totalLearners": max(learners, 1), "topPercent": top_pct}

    # -- Karma seeder (mock data bootstrap) ---------------------------------------------

    def seed_from_enrollments(
        self, userId: str, raw_enrollments: list, db: Session
    ) -> None:
        """
        One-time historical seeder, called when a user's ledger is empty.
        Derives backdated events from real iGOT enrollment records:
          • SELF_REGISTRATION  +5   always
          • FIRST_ENROLLMENT   +5   if ≥1 enrollment
          • COURSE_COMPLETION  +5   per completed course (status=2), spread over past months
          • ASSESSMENT_PASSED  +5   per completed course with pct ≥ 80
          • COURSE_RATED       +2   every other completed course
          • CBP_BONUS          +10  every 3rd fully-completed course (treated as CBP)
        Seeded rows bypass the caps (they are history) but carry referenceIds so
        later live awards stay idempotent.
        """
        now = datetime.utcnow()
        events: list[KarmaEvent] = []

        def _evt(etype, pts, ref, course_id=None, is_cbp=False, days_ago=0):
            return KarmaEvent(
                eventId=str(uuid.uuid4()),
                userId=userId,
                eventType=etype,
                pointsAwarded=pts,
                courseId=course_id,
                isCbp=is_cbp,
                createdAt=now - timedelta(days=max(days_ago, 1)),
                referenceId=ref,
                note="Imported from iGOT history",
            )

        events.append(_evt(E.SELF_REGISTRATION, 5, ONCE, days_ago=90))
        if raw_enrollments:
            events.append(_evt(E.FIRST_ENROLLMENT, 5, ONCE, days_ago=85))

        seen: set = set()
        completed = []
        for e in raw_enrollments:
            cid = e.get("courseId")
            if e.get("status") == 2 and cid not in seen:
                seen.add(cid)
                completed.append(e)

        for idx, enrollment in enumerate(completed):
            course_id = enrollment.get("courseId") or f"mock-course-{idx}"
            pct = enrollment.get("completionPercentage", 100)
            is_cbp = (pct == 100 and idx % 3 == 0)

            days_ago = 80 - (idx * 35)
            if days_ago < 10:
                days_ago = 10 + idx * 5

            events.append(_evt(E.COURSE_COMPLETION, 5, course_id,
                               course_id=course_id, is_cbp=is_cbp, days_ago=days_ago))
            if pct >= 80:
                events.append(_evt(E.ASSESSMENT_PASSED, 5, f"seed:{course_id}",
                                   course_id=course_id, days_ago=days_ago - 1))
            if is_cbp:
                events.append(_evt(E.CBP_BONUS, 10, course_id,
                                   course_id=course_id, is_cbp=True, days_ago=days_ago - 2))
            if idx % 2 == 0:
                events.append(_evt(E.COURSE_RATED, 2, course_id,
                                   course_id=course_id, days_ago=days_ago - 3))

        for evt in events:
            db.add(evt)

        # Count seeded non-CBP completions landing in the current IST month
        ist = ist_now()
        cur_month_non_cbp = sum(
            1 for e in events
            if e.eventType == E.COURSE_COMPLETION and not e.isCbp
            and (e.createdAt + IST).year == ist.year
            and (e.createdAt + IST).month == ist.month
        )
        if cur_month_non_cbp > 0:
            usage_row = db.query(KarmaMonthlyUsage).filter(
                KarmaMonthlyUsage.userId == userId,
                KarmaMonthlyUsage.year  == ist.year,
                KarmaMonthlyUsage.month == ist.month,
            ).first()
            if usage_row:
                usage_row.nonCbpCompletions += cur_month_non_cbp
            else:
                db.add(KarmaMonthlyUsage(
                    userId=userId, year=ist.year, month=ist.month,
                    nonCbpCompletions=min(cur_month_non_cbp, MONTHLY_COMPLETION_CAP),
                ))
        try:
            db.commit()
        except IntegrityError:           # a concurrent request seeded first
            db.rollback()

    # -- Private helpers -------------------------------------------------------------------

    @staticmethod
    def _already(userId: str, event_type: KarmaEventType, ref: str, db: Session) -> bool:
        q = db.query(KarmaEvent.eventId).filter(
            KarmaEvent.userId == userId, KarmaEvent.eventType == event_type,
        )
        if ref != ONCE:
            # Legacy rows predate referenceId and only carry a courseId
            q = q.filter(or_(
                KarmaEvent.referenceId == ref,
                and_(KarmaEvent.referenceId.is_(None), KarmaEvent.courseId == ref),
            ))
        return q.first() is not None

    @staticmethod
    def _count_today(userId: str, event_type: KarmaEventType, today: date, db: Session) -> int:
        return db.query(func.count(KarmaEvent.eventId)).filter(
            KarmaEvent.userId == userId,
            KarmaEvent.eventType == event_type,
            KarmaEvent.pointsAwarded > 0,
            KarmaEvent.createdAt >= ist_day_start_utc(today),
        ).scalar() or 0

    def _increment_monthly_usage(self, userId: str, db: Session) -> None:
        now = ist_now()
        row = db.query(KarmaMonthlyUsage).filter(
            KarmaMonthlyUsage.userId == userId,
            KarmaMonthlyUsage.year  == now.year,
            KarmaMonthlyUsage.month == now.month,
        ).first()
        if row:
            row.nonCbpCompletions += 1
        else:
            db.add(KarmaMonthlyUsage(userId=userId, year=now.year, month=now.month,
                                     nonCbpCompletions=1))


# --- Schema migration (called from main._create_schema after create_all) ------------------

def migrate_karma_schema(engine) -> None:
    """
    Idempotent upgrade for databases created before the daily-cap rework:
    adds referenceId / note columns, new Postgres enum values and the partial
    unique index that makes awards idempotent under concurrency.
    """
    from sqlalchemy import inspect, text

    insp = inspect(engine)
    if "karma_events" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("karma_events")}
    with engine.begin() as conn:
        for col in ("referenceId", "note"):
            if col not in cols:
                conn.execute(text(f'ALTER TABLE karma_events ADD COLUMN "{col}" VARCHAR'))

    if engine.dialect.name == "postgresql":
        # ALTER TYPE ... ADD VALUE must not share a transaction with its first use
        with engine.execution_options(isolation_level="AUTOCOMMIT").connect() as conn:
            for v in KarmaEventType:
                conn.execute(text(f"ALTER TYPE karmaeventtype ADD VALUE IF NOT EXISTS '{v.name}'"))

    with engine.begin() as conn:
        conn.execute(text(
            'CREATE UNIQUE INDEX IF NOT EXISTS uq_karma_event_ref '
            'ON karma_events ("userId", "eventType", "referenceId") '
            'WHERE "referenceId" IS NOT NULL'
        ))


# --- Module-level singleton (imported by the router) ----------------------------------
karma_engine = KarmaEngine()
