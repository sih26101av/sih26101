"""
services/karma_engine.py
─────────────────────────────────────────────────────────────────────────────
PATTERN: Strategy Pattern  (mirrors IRecommendationStrategy in the Mermaid diagram)

IKarmaStrategy          <<interface>>   compute(userId, metadata, db) -> int
  RegistrationKarmaStrategy             +5, one-time (self-registered only)
  EnrollmentKarmaStrategy               +5, one-time (first enrollment ever)
  CompletionKarmaStrategy               +5, hard cap: 4 non-CBP courses/month
  AssessmentKarmaStrategy               +5, per passing attempt
  RatingKarmaStrategy                   +2, per course rating submitted
  CbpBonusKarmaStrategy                 +10, once per mandated course (retroactive-safe)

KarmaEngine             (context class)
  award(userId, eventType, metadata, db) -> AwardResult
  get_balance(userId, db) -> int
  get_ledger(userId, db, limit) -> List[KarmaEvent]
  get_monthly_usage(userId, db) -> MonthlyUsage
  get_streak(userId, db) -> int    # login-based: consecutive days with any event
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.models import KarmaEvent, KarmaEventType, KarmaMonthlyUsage


# --- Result DTO ---------------------------------------------------------------

@dataclass
class AwardResult:
    points_awarded: int
    cap_reached: bool       # True when COURSE_COMPLETION was blocked by monthly cap
    already_claimed: bool   # True when a one-time event was already consumed


@dataclass
class MonthlyUsage:
    used: int
    cap: int = 4

    @property
    def remaining(self) -> int:
        return max(0, self.cap - self.used)

    def to_dict(self) -> dict:
        return {"used": self.used, "cap": self.cap, "remaining": self.remaining}


# --- IKarmaStrategy interface -------------------------------------------------

class IKarmaStrategy(ABC):
    """
    Computes the points to award for a specific event type.
    Returns 0 if the event is not eligible (already claimed, cap reached, etc.)
    """
    @abstractmethod
    def compute(self, userId: str, metadata: dict, db: Session) -> AwardResult:
        ...


# --- Concrete Strategies ------------------------------------------------------

class RegistrationKarmaStrategy(IKarmaStrategy):
    """
    +5 on first self-registration.
    Guard: if onboarded by MDO admin (metadata["is_mdo_onboarded"]=True), skip.
    """
    def compute(self, userId: str, metadata: dict, db: Session) -> AwardResult:
        if metadata.get("is_mdo_onboarded", False):
            return AwardResult(0, cap_reached=False, already_claimed=True)

        already = db.query(KarmaEvent).filter(
            KarmaEvent.userId == userId,
            KarmaEvent.eventType == KarmaEventType.SELF_REGISTRATION,
        ).first()

        if already:
            return AwardResult(0, cap_reached=False, already_claimed=True)
        return AwardResult(5, cap_reached=False, already_claimed=False)


class EnrollmentKarmaStrategy(IKarmaStrategy):
    """+5 on the very first course enrollment ever. One-time only."""
    def compute(self, userId: str, metadata: dict, db: Session) -> AwardResult:
        already = db.query(KarmaEvent).filter(
            KarmaEvent.userId == userId,
            KarmaEvent.eventType == KarmaEventType.FIRST_ENROLLMENT,
        ).first()

        if already:
            return AwardResult(0, cap_reached=False, already_claimed=True)
        return AwardResult(5, cap_reached=False, already_claimed=False)


class CompletionKarmaStrategy(IKarmaStrategy):
    """
    +5 per course completion.
    CBP-mandated courses (isCbp=True) are EXEMPT from the 4/month cap.
    Non-CBP courses are capped at 4 per calendar month.
    """
    MONTHLY_CAP = 4

    def compute(self, userId: str, metadata: dict, db: Session) -> AwardResult:
        is_cbp = metadata.get("isCbp", False)
        if is_cbp:
            return AwardResult(5, cap_reached=False, already_claimed=False)

        now = datetime.utcnow()
        usage = db.query(KarmaMonthlyUsage).filter(
            KarmaMonthlyUsage.userId == userId,
            KarmaMonthlyUsage.year  == now.year,
            KarmaMonthlyUsage.month == now.month,
        ).first()

        current_count = usage.nonCbpCompletions if usage else 0
        if current_count >= self.MONTHLY_CAP:
            return AwardResult(0, cap_reached=True, already_claimed=False)

        return AwardResult(5, cap_reached=False, already_claimed=False)


class AssessmentKarmaStrategy(IKarmaStrategy):
    """+5 for passing an assessment. Awarded once per passing attempt."""
    def compute(self, userId: str, metadata: dict, db: Session) -> AwardResult:
        return AwardResult(5, cap_reached=False, already_claimed=False)


class RatingKarmaStrategy(IKarmaStrategy):
    """+2 every time the user submits a course rating."""
    def compute(self, userId: str, metadata: dict, db: Session) -> AwardResult:
        return AwardResult(2, cap_reached=False, already_claimed=False)


class CbpBonusKarmaStrategy(IKarmaStrategy):
    """
    +10 bonus for completing a CBP-mandated course.
    Idempotent: second claim for the same courseId returns 0 (no double-dipping).
    Retroactive-safe: user can claim even if the mandate came after their completion.
    """
    def compute(self, userId: str, metadata: dict, db: Session) -> AwardResult:
        course_id = metadata.get("courseId")
        if not course_id:
            return AwardResult(0, cap_reached=False, already_claimed=True)

        already = db.query(KarmaEvent).filter(
            KarmaEvent.userId    == userId,
            KarmaEvent.eventType == KarmaEventType.CBP_BONUS,
            KarmaEvent.courseId  == course_id,
        ).first()

        if already:
            return AwardResult(0, cap_reached=False, already_claimed=True)
        return AwardResult(10, cap_reached=False, already_claimed=False)


# --- KarmaEngine (context class) -----------------------------------------------

class KarmaEngine:
    """
    Context class that holds the strategy registry and executes point awards.
    Strategy pattern: calling layer fires an eventType; engine dispatches to
    the right strategy and persists the immutable ledger entry.
    """

    def __init__(self) -> None:
        self._strategies: Dict[KarmaEventType, IKarmaStrategy] = {
            KarmaEventType.SELF_REGISTRATION: RegistrationKarmaStrategy(),
            KarmaEventType.FIRST_ENROLLMENT:  EnrollmentKarmaStrategy(),
            KarmaEventType.COURSE_COMPLETION:  CompletionKarmaStrategy(),
            KarmaEventType.ASSESSMENT_PASSED:  AssessmentKarmaStrategy(),
            KarmaEventType.COURSE_RATED:       RatingKarmaStrategy(),
            KarmaEventType.CBP_BONUS:          CbpBonusKarmaStrategy(),
        }

    # -- Public interface -------------------------------------------------------

    def award(
        self,
        userId: str,
        event_type: KarmaEventType,
        metadata: dict,
        db: Session,
    ) -> AwardResult:
        """
        Execute the correct strategy, persist the ledger entry (if points > 0),
        and update the monthly usage counter when applicable.
        """
        strategy = self._strategies.get(event_type)
        if strategy is None:
            return AwardResult(0, cap_reached=False, already_claimed=True)

        result = strategy.compute(userId, metadata, db)

        if result.points_awarded > 0:
            entry = KarmaEvent(
                eventId=str(uuid.uuid4()),
                userId=userId,
                eventType=event_type,
                pointsAwarded=result.points_awarded,
                courseId=metadata.get("courseId"),
                isCbp=metadata.get("isCbp", False),
                createdAt=datetime.utcnow(),
            )
            db.add(entry)

            # Update monthly cap tracker for non-CBP completions
            if (
                event_type == KarmaEventType.COURSE_COMPLETION
                and not metadata.get("isCbp", False)
            ):
                self._increment_monthly_usage(userId, db)

            db.commit()

        return result

    def get_balance(self, userId: str, db: Session) -> int:
        total = (
            db.query(func.sum(KarmaEvent.pointsAwarded))
            .filter(KarmaEvent.userId == userId)
            .scalar()
        )
        return total or 0

    def get_ledger(self, userId: str, db: Session, limit: int = 10) -> List[KarmaEvent]:
        return (
            db.query(KarmaEvent)
            .filter(KarmaEvent.userId == userId)
            .order_by(KarmaEvent.createdAt.desc())
            .limit(limit)
            .all()
        )

    def get_monthly_usage(self, userId: str, db: Session) -> MonthlyUsage:
        now = datetime.utcnow()
        row = db.query(KarmaMonthlyUsage).filter(
            KarmaMonthlyUsage.userId == userId,
            KarmaMonthlyUsage.year  == now.year,
            KarmaMonthlyUsage.month == now.month,
        ).first()
        return MonthlyUsage(used=row.nonCbpCompletions if row else 0)

    def get_breakdown(self, userId: str, db: Session) -> dict:
        """Per-event-type total points for the Activity Pills in the frontend."""
        rows = (
            db.query(KarmaEvent.eventType, func.sum(KarmaEvent.pointsAwarded))
            .filter(KarmaEvent.userId == userId)
            .group_by(KarmaEvent.eventType)
            .all()
        )
        return {row[0].value: (row[1] or 0) for row in rows}

    def get_streak(self, userId: str, db: Session) -> int:
        """
        Login-based streak: consecutive calendar days with any KarmaEvent.
        A gap breaks the streak back to 0.
        """
        rows = (
            db.query(func.date(KarmaEvent.createdAt).label("event_date"))
            .filter(KarmaEvent.userId == userId)
            .distinct()
            .order_by(func.date(KarmaEvent.createdAt).desc())
            .all()
        )

        if not rows:
            return 0

        def _to_date(val) -> date:
            if isinstance(val, date):
                return val
            return date.fromisoformat(str(val))

        today = date.today()
        streak = 0
        expected = today

        for row in rows:
            event_date = _to_date(row.event_date)
            if event_date == expected:
                streak += 1
                expected = expected - timedelta(days=1)
            else:
                # Grace: allow yesterday to start the streak if no event today
                if streak == 0 and event_date == today - timedelta(days=1):
                    streak += 1
                    expected = event_date - timedelta(days=1)
                else:
                    break

        return streak

    # -- Karma Seeder (mock data bootstrap) ------------------------------------

    def seed_from_enrollments(
        self, userId: str, raw_enrollments: list, db: Session
    ) -> None:
        """
        One-time historical seeder. Called when a user's karma ledger is
        completely empty. Derives karma events from their actual iGOT
        enrollment records and inserts them as historic events.

        Rules applied (faithful to iGOT algorithm):
          • SELF_REGISTRATION  +5   (always — they self-registered)
          • FIRST_ENROLLMENT   +5   (if they have ≥1 enrollment)
          • COURSE_COMPLETION  +5   per completed course (status=2)
                               ─ cap is bypassed by spreading dates across past months
          • ASSESSMENT_PASSED  +5   per completed course where pct ≥ 80%
          • COURSE_RATED       +2   for every alternate completed course (simulates
                               realistic 50% rating engagement)
          • CBP_BONUS          +10  for every 3rd completed course (treated as
                               CBP-mandated, based on high completion rate heuristic)
        """
        from datetime import datetime, timedelta

        now = datetime.utcnow()
        events: list[KarmaEvent] = []

        def _evt(etype, pts, course_id=None, is_cbp=False, days_ago=0):
            return KarmaEvent(
                eventId=str(uuid.uuid4()),
                userId=userId,
                eventType=etype,
                pointsAwarded=pts,
                courseId=course_id,
                isCbp=is_cbp,
                createdAt=now - timedelta(days=max(days_ago, 0)),
            )

        # 1. Self-registration — always awarded (90 days ago)
        events.append(_evt(KarmaEventType.SELF_REGISTRATION, 5, days_ago=90))

        # 2. First enrollment — if they have any enrollment at all
        if raw_enrollments:
            events.append(_evt(KarmaEventType.FIRST_ENROLLMENT, 5, days_ago=85))

        # Partition enrollments
        completed   = [e for e in raw_enrollments if e.get("status") == 2]
        in_progress = [e for e in raw_enrollments if e.get("status") == 1]

        # 3. Seed events for each completed course
        for idx, enrollment in enumerate(completed):
            course_id = enrollment.get("courseId", f"mock-course-{idx}")
            pct       = enrollment.get("completionPercentage", 100)

            # Determine CBP: every 3rd fully-completed course is treated as
            # CBP-mandated (heuristic — mimics MDO assignment)
            is_cbp = (pct == 100 and idx % 3 == 0)

            # Spread completions back in time: oldest first, 35 days apart,
            # so they land in different calendar months (avoids cap issues)
            days_ago = 80 - (idx * 35)
            if days_ago < 10:
                days_ago = 10 + idx * 5   # graceful fallback for many completions

            # COURSE_COMPLETION
            events.append(_evt(
                KarmaEventType.COURSE_COMPLETION, 5,
                course_id=course_id, is_cbp=is_cbp, days_ago=days_ago,
            ))

            # ASSESSMENT_PASSED — awarded when completion ≥ 80% (they passed)
            if pct >= 80:
                events.append(_evt(
                    KarmaEventType.ASSESSMENT_PASSED, 5,
                    course_id=course_id, days_ago=days_ago - 1,
                ))

            # CBP_BONUS — only for the courses flagged as CBP
            if is_cbp:
                events.append(_evt(
                    KarmaEventType.CBP_BONUS, 10,
                    course_id=course_id, is_cbp=True, days_ago=days_ago - 2,
                ))

            # COURSE_RATED — alternate courses (realistic 50% rating rate)
            if idx % 2 == 0:
                events.append(_evt(
                    KarmaEventType.COURSE_RATED, 2,
                    course_id=course_id, days_ago=days_ago - 3,
                ))

        # Bulk insert all seeded events
        for evt in events:
            db.add(evt)

        # Update the monthly usage table: count seeded COURSE_COMPLETION events
        # that landed in the current calendar month (avoid negative days_ago)
        cur_month_non_cbp = sum(
            1 for e in events
            if e.eventType == KarmaEventType.COURSE_COMPLETION
            and not e.isCbp
            and e.createdAt.year  == now.year
            and e.createdAt.month == now.month
        )
        if cur_month_non_cbp > 0:
            usage_row = db.query(KarmaMonthlyUsage).filter(
                KarmaMonthlyUsage.userId == userId,
                KarmaMonthlyUsage.year  == now.year,
                KarmaMonthlyUsage.month == now.month,
            ).first()
            if usage_row:
                usage_row.nonCbpCompletions += cur_month_non_cbp
            else:
                db.add(KarmaMonthlyUsage(
                    userId=userId,
                    year=now.year,
                    month=now.month,
                    nonCbpCompletions=min(cur_month_non_cbp, 4),
                ))

        db.commit()

    # -- Private helpers --------------------------------------------------------

    def _increment_monthly_usage(self, userId: str, db: Session) -> None:
        now = datetime.utcnow()
        row = db.query(KarmaMonthlyUsage).filter(
            KarmaMonthlyUsage.userId == userId,
            KarmaMonthlyUsage.year  == now.year,
            KarmaMonthlyUsage.month == now.month,
        ).first()

        if row:
            row.nonCbpCompletions += 1
        else:
            db.add(KarmaMonthlyUsage(
                userId=userId,
                year=now.year,
                month=now.month,
                nonCbpCompletions=1,
            ))


# --- Module-level singleton (imported by the router) --------------------------
karma_engine = KarmaEngine()
