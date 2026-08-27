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

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import httpx

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

    def __init__(self) -> None:
        self.base_url = "http://localhost:8001"
        # The mock server accepts any non-empty token value
        self.token = "mock-api-key-2026"
        self._headers = {"x-authenticated-user-token": self.token}

    # ── Catalog ────────────────────────────────────────────────────────────────

    async def fetch_catalog(self) -> List[Dict[str, Any]]:
        """
        GET /api/content/read
        Returns: result.content  — list of Sunbird course objects.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/api/content/read",
                headers=self._headers,
                timeout=10.0,
            )
            resp.raise_for_status()
        data = resp.json()
        return _sunbird_result(data, "content") or []

    # ── User Profile ───────────────────────────────────────────────────────────

    async def fetch_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        GET /api/user/v2/read/{user_id}
        Returns: result.response  — single user object with profileDetails nested.
        Returns None on 404.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/api/user/v2/read/{user_id}",
                headers=self._headers,
                timeout=10.0,
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
        data = resp.json()
        return _sunbird_result(data, "response")

    # ── Enrollments ────────────────────────────────────────────────────────────

    async def fetch_user_enrollments(self, user_id: str) -> List[Dict[str, Any]]:
        """
        GET /api/course/v1/user/enrollment/list/{user_id}
        Returns: result.courses  — list of UserEnrolment records keyed by userId.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/api/course/v1/user/enrollment/list/{user_id}",
                headers=self._headers,
                timeout=10.0,
            )
            if resp.status_code == 404:
                return []
            resp.raise_for_status()
        data = resp.json()
        return _sunbird_result(data, "courses") or []

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
