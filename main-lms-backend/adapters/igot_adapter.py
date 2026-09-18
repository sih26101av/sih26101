"""
adapters/igot_adapter.py — iGOT Platform Adapter
─────────────────────────────────────────────────────────────────────────────
Follows the Adapter / Port-and-Adapter pattern:

  ILearningPlatformAdapter   ← abstract interface (Port)
  MockIgotAdapter            ← HTTP adapter calling mock_igot_server.py (Adapter)

The adapter calls the Sunbird-compliant mock server (mock_igot_server.py)
running on port 8001. Data only flows when that server is actually running,
correctly simulating a real external iGOT API call.

Run the mock server with:
    cd mock-igot-server
    uvicorn mock_igot_server:app --reload --port 8001
"""

from __future__ import annotations

import asyncio
import os
import time
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

import httpx

# Per-user reads (profile, enrollments, evidence, ACBP plan) are memoised this
# long. One dashboard load asks for the same user ~10 times across endpoints;
# the LMS never writes to iGOT, so a short TTL cannot hide an LMS-side change.
_USER_CACHE_TTL_S = float(os.getenv("IGOT_USER_CACHE_SECONDS", "30"))

# ── Sunbird-format response extractor helpers ──────────────────────────────────

def _sunbird_result(data: dict, *keys: str) -> Any:
    """Safely drill into a Sunbird envelope: data['result']['key1']['key2']..."""
    node = data.get("result", {})
    for key in keys:
        if not isinstance(node, dict):
            return None
        node = node.get(key)
    return node


def _prof_detail(user: Dict, key: str, default: str = "") -> str:
    """Safely read a field from profileDetails.professionalDetails[0]."""
    prof_list = (user.get("profileDetails") or {}).get("professionalDetails") or []
    if prof_list:
        return prof_list[0].get(key, default)
    return default


def _competencies(user: Dict) -> List[Dict]:
    """Return the competencies list from profileDetails.competencies."""
    return (user.get("profileDetails") or {}).get("competencies") or []


# ── Abstract Interface (Port) ──────────────────────────────────────────────────

class ILearningPlatformAdapter(ABC):
    """
    Interface for external learning platform integration.
    All concrete adapters must implement these five methods.
    """

    @abstractmethod
    async def fetch_catalog(self) -> List[Dict[str, Any]]:
        """Return the full CBP course catalog."""

    @abstractmethod
    async def fetch_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Return learning history for a user (legacy, by govId or userId)."""

    @abstractmethod
    async def fetch_user_roster(self) -> List[Dict[str, Any]]:
        """Return the full user roster (all officials)."""

    @abstractmethod
    async def fetch_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Look up a single user by their iGOT userId (usr_...). Returns None if not found."""

    @abstractmethod
    async def fetch_user_enrollments(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Return all enrollment records for a user by their iGOT userId (usr_...).
        Each record matches the Sunbird UserEnrolment shape:
          courseId, courseName, userId, status (int 0/1/2), completionPercentage,
          progress, leafNodesCount, enrolledDate, issuedCertificates, channel.
        """


# ── Concrete: HTTP Adapter → mock_igot_server.py (Sunbird-compliant) ──────────

class MockIgotAdapter(ILearningPlatformAdapter):
    """
    Calls the Sunbird-compliant mock iGOT server (mock_igot_server.py) on port 8001
    via HTTP. Data only flows when that server is running, exactly like a real
    external iGOT API call. This is the production-ready adapter shape.

    Auth header: x-authenticated-user-token (required on every call).
    All responses follow the Sunbird envelope: { result: { ... } }.
    """

    # Page size for catalogue search (the mock caps composite search at 1000).
    _SEARCH_PAGE = 500

    def __init__(self) -> None:
        self.base_url = os.getenv("IGOT_MOCK_BASE_URL", "http://localhost:8001")
        # The mock server accepts any non-empty token value
        self.token = os.getenv("IGOT_MOCK_TOKEN", "mock-api-key-2026")
        self._headers = {"x-authenticated-user-token": self.token}
        # Keep-alive client per event loop (the warm-up thread runs its own loop),
        # and (method, userId) → (expiry, value | in-flight task) for per-user reads.
        self._clients: Dict[int, httpx.AsyncClient] = {}
        self._user_cache: Dict[Tuple[str, str], Tuple[float, Any]] = {}

    def _client(self) -> httpx.AsyncClient:
        """Pooled client for the running loop — no new TCP connection per call."""
        key = id(asyncio.get_running_loop())
        client = self._clients.get(key)
        if client is None or client.is_closed:
            client = httpx.AsyncClient(headers=self._headers, timeout=10.0)
            self._clients[key] = client
        return client

    async def _cached(self, kind: str, user_id: str, fetch: Callable[[], Awaitable[Any]]) -> Any:
        """
        TTL memo for one user's read. Concurrent callers share one in-flight
        request; failures are not cached.
        """
        key = (kind, user_id)
        now = time.monotonic()
        hit = self._user_cache.get(key)
        if hit and hit[0] > now:
            value = hit[1]
            return await asyncio.shield(value) if isinstance(value, asyncio.Future) else value

        task = asyncio.ensure_future(fetch())
        self._user_cache[key] = (now + _USER_CACHE_TTL_S, task)
        try:
            value = await asyncio.shield(task)
        except Exception:
            self._user_cache.pop(key, None)
            raise
        self._user_cache[key] = (time.monotonic() + _USER_CACHE_TTL_S, value)
        if len(self._user_cache) > 2048:                 # drop expired entries now and then
            self._user_cache = {k: v for k, v in self._user_cache.items() if v[0] > now}
        return value

    def invalidate_user(self, user_id: str) -> None:
        """Forget every cached read for this user."""
        for key in [k for k in self._user_cache if k[1] == user_id]:
            self._user_cache.pop(key, None)

    # ── Catalog ────────────────────────────────────────────────────────────────

    async def fetch_catalog(self) -> List[Dict[str, Any]]:
        """
        The full CBP course catalogue, paged through
        POST /api/composite/v1/search. Returns: list of Sunbird course objects.
        """
        return await self.search_catalog({"primaryCategory": ["Course"]})

    async def search_catalog(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        POST /api/composite/v1/search — Sunbird composite search, every page.
        `filters` e.g. {"competencies_v3.id": ["comp_price_stats_003"], "level": [3]}.
        """
        out: List[Dict[str, Any]] = []
        async with httpx.AsyncClient() as client:
            while True:
                resp = await client.post(
                    f"{self.base_url}/api/composite/v1/search",
                    headers=self._headers,
                    json={"request": {"filters": filters or {}, "limit": self._SEARCH_PAGE,
                                      "offset": len(out)}},
                    timeout=15.0,
                )
                resp.raise_for_status()
                result = resp.json().get("result", {})
                page = result.get("content") or []
                out.extend(page)
                if not page or len(out) >= int(result.get("count") or 0):
                    return out

    async def fetch_frac_competencies(self) -> List[Dict[str, Any]]:
        """GET /api/frac/competencies — the catalogue FRAC set incl. L1–L5 descriptors."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/api/frac/competencies",
                                    headers=self._headers, timeout=10.0)
            resp.raise_for_status()
        return _sunbird_result(resp.json(), "competencies") or []

    async def _get_result(self, path: str, timeout: float = 10.0) -> Dict[str, Any]:
        """GET a Sunbird endpoint and return its `result` object."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}{path}", headers=self._headers, timeout=timeout)
            resp.raise_for_status()
        return resp.json().get("result", {}) or {}

    # ── SCIL v6 reference data ─────────────────────────────────────────────────

    async def fetch_gsbpm_map(self) -> Dict[str, Any]:
        """GET /api/gsbpm/v1/map — GSBPM sub-processes + competency → sub-processes."""
        return await self._get_result("/api/gsbpm/v1/map")

    async def fetch_offices(self) -> Dict[str, Any]:
        """GET /api/org/v1/offices — {cycle, offices[{officeId, subprocesses[{id, officerHours}]}]}."""
        return await self._get_result("/api/org/v1/offices")

    async def fetch_prerequisites(self) -> Dict[str, Any]:
        """GET /api/frac/v1/prerequisites — {count, edges[]} expert-seeded prerequisite DAG."""
        return await self._get_result("/api/frac/v1/prerequisites")

    async def fetch_course_outcomes(self) -> Dict[str, Any]:
        """GET /api/course/v1/assessment/outcomes — {outcomes[], comparisons[]} pre/post θ records."""
        return await self._get_result("/api/course/v1/assessment/outcomes", timeout=30.0)

    async def fetch_item_bank(self) -> Dict[str, Any]:
        """GET /api/assessment/v1/itembank — 2PL items incl. answer keys (server side only)."""
        return await self._get_result("/api/assessment/v1/itembank", timeout=30.0)

    async def fetch_hrms(self) -> Dict[str, Any]:
        """GET /api/hrms/v1/officials — {officials{userId: DOB, superannuationDate, products}, products, …}."""
        return await self._get_result("/api/hrms/v1/officials")

    async def fetch_user_evidence(self, user_id: str) -> List[Dict[str, Any]]:
        """GET /api/evidence/v1/user/{id} — EvidenceLog-style workplace evidence rows ([] on 404)."""
        async def fetch():
            resp = await self._client().get(f"{self.base_url}/api/evidence/v1/user/{user_id}")
            if resp.status_code == 404:
                return []
            resp.raise_for_status()
            return (resp.json().get("result") or {}).get("rows") or []
        return await self._cached("evidence", user_id, fetch)

    async def fetch_user_cbplan(self, user_id: str) -> Optional[Dict[str, Any]]:
        """GET /api/cbplan/v1/user/{id} — ACBP mandatory courses + learning hours/quarter. None on 404."""
        async def fetch():
            resp = await self._client().get(f"{self.base_url}/api/cbplan/v1/user/{user_id}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json().get("result") or None
        return await self._cached("cbplan", user_id, fetch)

    async def fetch_frac_crosswalk(self) -> List[Dict[str, Any]]:
        """GET /api/frac/v1/crosswalk — iGOT dictionary CID id → catalogue FRAC id."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/api/frac/v1/crosswalk",
                                    headers=self._headers, timeout=10.0)
            resp.raise_for_status()
        return _sunbird_result(resp.json(), "mappings") or []

    # ── User Profile ───────────────────────────────────────────────────────────

    async def fetch_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        GET /api/user/v2/read/{user_id}
        Returns: result.response  — single user object with profileDetails nested.
        Returns None on 404.
        """
        async def fetch():
            resp = await self._client().get(f"{self.base_url}/api/user/v2/read/{user_id}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return _sunbird_result(resp.json(), "response")
        return await self._cached("user", user_id, fetch)

    # ── Enrollments ────────────────────────────────────────────────────────────

    async def fetch_user_enrollments(self, user_id: str) -> List[Dict[str, Any]]:
        """
        GET /api/course/v1/user/enrollment/list/{user_id}
        Returns: result.courses  — list of UserEnrolment records keyed by userId.
        """
        async def fetch():
            resp = await self._client().get(
                f"{self.base_url}/api/course/v1/user/enrollment/list/{user_id}")
            if resp.status_code == 404:
                return []
            resp.raise_for_status()
            return _sunbird_result(resp.json(), "courses") or []
        return await self._cached("enrollments", user_id, fetch)

    # ── User Roster ────────────────────────────────────────────────────────────

    async def fetch_user_roster(self) -> List[Dict[str, Any]]:
        """
        GET /api/admin/v1/users
        Returns: result.users  — full list of officials.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/api/admin/v1/users",
                headers=self._headers,
                timeout=15.0,
            )
            resp.raise_for_status()
        data = resp.json()
        return _sunbird_result(data, "users") or []

    # ── Legacy: user history by govId (kept for backward compat) ──────────────

    async def fetch_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Legacy method that maps fetch_user_enrollments to the old simple-mock shape.
        Called by legacy govId-based endpoints. Accepts userId or govId — the
        Sunbird mock server uses userId internally.
        """
        return await self.fetch_user_enrollments(user_id)
