"""
services/app_state.py — process-wide singletons built in main._warm_up (background, after startup).

Routers read them from here instead of importing main (avoids a circular import).
"""
from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, Dict, Optional, Tuple

from services.reference_data import ReferenceData

# Set once main._warm_up has built everything below (success or not); the
# readiness gate in main.py holds engine-dependent requests until then.
ready: asyncio.Event = asyncio.Event()
# Set once the auth/karma tables exist (main._create_schema); every DB-backed
# request waits on it, which takes a second or two after boot at most.
db_ready: asyncio.Event = asyncio.Event()

engine: Optional[Any] = None          # HybridRecommendationEngine
assembler: Optional[Any] = None       # BaselineAssembler
ref: ReferenceData = ReferenceData()  # SCIL v6 reference datasets
# Hash of the catalogue + FRAC set the engine was built from (main._refresh_catalogue_loop)
catalogue_fingerprint: Optional[str] = None

# Workforce snapshot (SCIL v6 §2 / §11): userId → {officeId, phase, tier,
# experienceYears, competencies[{catalogueId, level, target, confidence, mu,
# lastEvidenceDate, decayClass}]}. Built in the background after startup.
snapshot: Optional[Dict[str, Dict[str, Any]]] = None
snapshot_status: str = "not built"
snapshot_builder: Optional[Callable[[], Awaitable[None]]] = None
# main._learner_competency_state (async, userId → resolved rows) for routers
competency_state: Optional[Callable[[str], Awaitable[Dict[str, Any]]]] = None

# Memo for main._learner_competency_state: (userId, annotate) → (expiry, state |
# in-flight task). The dashboard fires /skill-gaps, /recommendations and /pathway
# together; they now share one resolution instead of three. Anything that writes
# an EvidenceLog row must call invalidate_user() so the next read sees it.
user_state_cache: Dict[Tuple[str, bool], Tuple[float, Any]] = {}


def invalidate_user(user_id: str) -> None:
    """Drop the memoised competency state for one learner (after new evidence)."""
    for key in [k for k in user_state_cache if k[0] == user_id]:
        user_state_cache.pop(key, None)
