"""
services/reference_data.py — SCIL v6 reference datasets

Loaded ONCE at startup (main._warm_up, concurrently) through MockIgotAdapter. If the mock
iGOT server is down, each dataset falls back to the same generated file in
mock-igot-server/data/ and a warning is logged, the same rule as the course
catalogue. All of it is synthetic mock data (see mock-igot-server/data/README.md).
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any, Awaitable, Callable, Dict, List, Optional

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
        self.prerequisites: List[Dict[str, Any]] = []   # validated, acyclic expert edges ([] if rejected)
        self.prerequisite_check: Dict[str, Any] = {}    # {cycle, rejected, invalid, received}
        self.outcomes: List[Dict[str, Any]] = []        # course pre/post assessments
        self.comparisons: List[Dict[str, Any]] = []     # non-taker comparison episodes
        self.hrms: Dict[str, Any] = {}                  # {officials{userId: …}, products, productCriticalCompetencies}
        self.item_bank: Dict[str, List[Dict[str, Any]]] = {}   # competencyId → 2PL items (with keys)
        self.item_bank_calibration: str = ""
        # Role competency profiles (career ladder): roleId → {officeId, designation, tier, competencies}
        self.roles: Dict[str, Dict[str, Any]] = {}
        # Per-rater leniency offsets for APAR supervisor ratings (competency_service.rater_leniency_offsets)
        self.rater_offsets: Dict[str, Dict[str, Any]] = {}
        self.sources: Dict[str, str] = {}          # dataset → "adapter" | "disk" | "missing"
        self.cache: Dict[str, Any] = {}            # derived analytics computed once per process

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
        # Independent datasets: fetch concurrently (sequential round-trips were ~6 s).
        gsbpm, offices, prereq, bank, hrms, outcomes, roles, ratings = await asyncio.gather(
            ref._load("gsbpm", adapter.fetch_gsbpm_map, "gsbpm_map.json"),
            ref._load("offices", adapter.fetch_offices, "offices.json"),
            ref._load("prerequisites", adapter.fetch_prerequisites, "prerequisites.json"),
            ref._load("itemBank", adapter.fetch_item_bank, "item_bank.json"),
            ref._load("hrms", adapter.fetch_hrms, "hrms.json"),
            ref._load("outcomes", adapter.fetch_course_outcomes, "course_outcomes.json"),
            ref._load("roles", adapter.fetch_roles, "roles.json"),
            ref._load("supervisorRatings", adapter.fetch_supervisor_ratings, "workplace_evidence.json"),
        )
        if gsbpm:
            ref.gsbpm = {k: v for k, v in gsbpm.items() if k != "_meta"}
        if offices:
            ref.offices = {o["officeId"]: o for o in offices.get("offices", [])}
            ref.cycle = offices.get("cycle", {})
        if prereq:
            from services.prerequisite_service import validate_edges
            raw = prereq.get("edges", [])
            check = validate_edges(raw)
            ref.prerequisites = check["edges"]
            ref.prerequisite_check = {k: check[k] for k in ("cycle", "rejected", "invalid")} | {"received": len(raw)}
            if check["rejected"]:
                logger.error("[reference] prerequisite edges REJECTED — cycle: %s", " → ".join(check["cycle"]))
        if bank:
            ref.item_bank = {}
            for item in bank.get("items", []):
                ref.item_bank.setdefault(item["competencyId"], []).append(item)
            ref.item_bank_calibration = bank.get("calibration", "synthetic — demo only")
        if hrms:
            ref.hrms = {k: v for k, v in hrms.items() if k != "_meta"}
        if outcomes:
            ref.outcomes = outcomes.get("outcomes", [])
            ref.comparisons = outcomes.get("comparisons", [])
        if roles:
            ref.roles = {r["roleId"]: r for r in roles.get("roles", []) if r.get("roleId")}
        if ratings:
            from services.competency_service import rater_leniency_offsets
            # Adapter → {ratings[]}; disk fallback → the raw workplace_evidence.json {rows[]}.
            raw = ratings.get("ratings") or [
                {"raterId": (r.get("meta") or {}).get("raterId"), "compId": r.get("compId"),
                 "grantedValue": r.get("grantedValue")}
                for r in ratings.get("rows", []) if r.get("evidenceType") == "SUPERVISOR_RATING"
            ]
            ref.rater_offsets = rater_leniency_offsets(raw)
        logger.info("[reference] loaded: %s", ref.sources)
        return ref
