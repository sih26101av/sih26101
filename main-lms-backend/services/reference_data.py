"""
services/reference_data.py — SCIL v6 reference datasets

Loaded ONCE at startup (main._startup) through MockIgotAdapter. If the mock
iGOT server is down, each dataset falls back to the same generated file in
mock-igot-server/data/ and a warning is logged, the same rule as the course
catalogue. All of it is synthetic mock data (see mock-igot-server/data/README.md).
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Awaitable, Callable, Dict, Optional

logger = logging.getLogger(__name__)

DATA_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "mock-igot-server", "data"))


def _read_disk(filename: str) -> Optional[Dict[str, Any]]:
    try:
        with open(os.path.join(DATA_DIR, filename), encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


class ReferenceData:
    """Plain holder; every attribute defaults to empty so features degrade, not crash."""

    def __init__(self) -> None:
        self.gsbpm: Dict[str, Any] = {}            # {subprocesses, competencies, phases, version}
        self.offices: Dict[str, Dict[str, Any]] = {}   # officeId → office workload
        self.cycle: Dict[str, Any] = {}
        self.sources: Dict[str, str] = {}          # dataset → "adapter" | "disk" | "missing"

    async def _load(self, name: str, fetch: Callable[[], Awaitable[Dict[str, Any]]],
                    filename: str) -> Optional[Dict[str, Any]]:
        try:
            data = await fetch()
            if data:
                self.sources[name] = "adapter"
                return data
        except Exception as exc:                       # mock down / endpoint missing
            logger.warning("[reference] %s: adapter failed (%s) — reading data/%s from disk.",
                           name, exc, filename)
        data = _read_disk(filename)
        self.sources[name] = "disk" if data else "missing"
        if not data:
            logger.warning("[reference] %s: not available — feature disabled.", name)
        return data

    @classmethod
    async def load(cls, adapter) -> "ReferenceData":
        ref = cls()
        gsbpm = await ref._load("gsbpm", adapter.fetch_gsbpm_map, "gsbpm_map.json")
        if gsbpm:
            ref.gsbpm = {k: v for k, v in gsbpm.items() if k != "_meta"}
        offices = await ref._load("offices", adapter.fetch_offices, "offices.json")
        if offices:
            ref.offices = {o["officeId"]: o for o in offices.get("offices", [])}
            ref.cycle = offices.get("cycle", {})
        logger.info("[reference] loaded: %s", ref.sources)
        return ref
