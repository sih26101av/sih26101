"""
services/app_state.py — process-wide singletons built in main._startup.

Routers read them from here instead of importing main (avoids a circular import).
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Optional

from services.reference_data import ReferenceData

engine: Optional[Any] = None          # HybridRecommendationEngine
assembler: Optional[Any] = None       # BaselineAssembler
ref: ReferenceData = ReferenceData()  # SCIL v6 reference datasets

# Workforce snapshot (SCIL v6 §2 / §11): userId → {officeId, phase, tier,
# experienceYears, competencies[{catalogueId, level, target, confidence, mu,
# lastEvidenceDate, decayClass}]}. Built in the background after startup.
snapshot: Optional[Dict[str, Dict[str, Any]]] = None
snapshot_status: str = "not built"
snapshot_builder: Optional[Callable[[], Awaitable[None]]] = None
