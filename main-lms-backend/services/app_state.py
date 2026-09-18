"""
services/app_state.py — process-wide singletons built in main._startup.

Routers read them from here instead of importing main (avoids a circular import).
"""
from __future__ import annotations

from typing import Any, Optional

from services.reference_data import ReferenceData

engine: Optional[Any] = None          # HybridRecommendationEngine
assembler: Optional[Any] = None       # BaselineAssembler
ref: ReferenceData = ReferenceData()  # SCIL v6 reference datasets
