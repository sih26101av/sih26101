"""
adapters/igot_adapter.py — iGOT Platform Adapter
─────────────────────────────────────────────────────────────────────────────
Follows the Adapter / Port-and-Adapter pattern:

  ILearningPlatformAdapter   ← abstract interface (Port)
  FileBasedIgotAdapter       ← reads mock-igot-server/data/*.json (Adapter)
  MockIgotAdapter            ← HTTP calls to mock server (kept for compat)

Using FileBasedIgotAdapter means the backend is completely independent of
which mock server is running or whether any is running at all.
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import httpx

# ── Path resolution ────────────────────────────────────────────────────────────
# This file lives at main-lms-backend/adapters/igot_adapter.py
# Data files live at mock-igot-server/data/
_DATA_DIR = os.path.join(
    os.path.dirname(__file__),   # .../main-lms-backend/adapters/
    "..",                         # .../main-lms-backend/
    "..",                         # .../SIH_IGot/
    "mock-igot-server",
    "data",
)


def _load_json(filename: str) -> Any:
    """Load a JSON file from the mock server's data directory."""
    path = os.path.abspath(os.path.join(_DATA_DIR, filename))
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── Helper: extract nested profile fields ─────────────────────────────────────
def _prof_detail(user: Dict, key: str, default: str = "") -> str:
    """Safely read a field from profileDetails.professionalDetails[0]."""
    prof_list = user.get("profileDetails", {}).get("professionalDetails", [])
    if prof_list:
        return prof_list[0].get(key, default)
    return default


def _competencies(user: Dict) -> List[Dict]:
    """Return the competencies list from profileDetails.competencies."""
    return user.get("profileDetails", {}).get("competencies", [])


# ── Abstract Interface (Port) ──────────────────────────────────────────────────
class ILearningPlatformAdapter(ABC):
    """
    Interface for external learning platform integration.

    All concrete adapters must implement these methods.
    """

    @abstractmethod
    async def fetch_catalog(self) -> List[Dict[str, Any]]:
        """Return the full CBP course catalog."""
        pass

    @abstractmethod
    async def fetch_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Return the learning history (enrollments) for a given user.

        user_id may be a govId (EMP-XXXX) or iGOT userId (usr_...).
        Implementations must handle both or document which they expect.
        """
        pass

    @abstractmethod
    async def fetch_user_roster(self) -> List[Dict[str, Any]]:
        """Return the full user roster (all officials)."""
        pass

    @abstractmethod
    async def fetch_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Look up a single user by their iGOT userId (usr_...).
        Returns None if not found.
        """
        pass

    @abstractmethod
    async def fetch_user_enrollments(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Return all enrollment records for a user by their iGOT userId (usr_...).
        Each record contains: courseId, courseName, status (int 0/1/2),
        completionPercentage, progress, leafNodesCount, enrolledDate, etc.
        """
        pass


# ── Concrete: File-Based Adapter ───────────────────────────────────────────────
class FileBasedIgotAdapter(ILearningPlatformAdapter):
    """
    Reads data directly from mock-igot-server/data/*.json files.

    Advantages over the HTTP adapter:
    - Works without any mock server running.
    - Never produces 404/connection errors due to port conflicts.
    - Correct field navigation (profileDetails.competencies, etc.).
    - seed_data.py uses random.seed(42) so IDs are stable across restarts.
    """

    # In-memory cache per adapter instance
    _catalog_cache:  List[Dict]         = []
    _roster_cache:   List[Dict]         = []
    _enroll_cache:   List[Dict]         = []

    async def fetch_catalog(self) -> List[Dict[str, Any]]:
        if not FileBasedIgotAdapter._catalog_cache:
            FileBasedIgotAdapter._catalog_cache = _load_json("course_catalog.json")
        return FileBasedIgotAdapter._catalog_cache

    async def fetch_user_roster(self) -> List[Dict[str, Any]]:
        if not FileBasedIgotAdapter._roster_cache:
            FileBasedIgotAdapter._roster_cache = _load_json("users.json")
        return FileBasedIgotAdapter._roster_cache

    async def fetch_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        roster = await self.fetch_user_roster()
        return next((u for u in roster if u.get("userId") == user_id), None)

    async def fetch_user_enrollments(self, user_id: str) -> List[Dict[str, Any]]:
        """Return all enrollment records for a user by their iGOT userId (usr_...)."""
        if not FileBasedIgotAdapter._enroll_cache:
            FileBasedIgotAdapter._enroll_cache = _load_json("enrollments.json")
        return [e for e in FileBasedIgotAdapter._enroll_cache
                if e.get("userId") == user_id]

    async def fetch_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Legacy method: returns enrollments by userId in the simple-mock format.
        Maps the Sunbird enrollment record shape into the dict shape that
        the existing govId-based endpoints expect.
        """
        enrollments = await self.fetch_user_enrollments(user_id)
        catalog = await self.fetch_catalog()
        result = []
        for e in enrollments:
            course = next(
                (c for c in catalog if c.get("identifier") == e.get("courseId")),
                None,
            )
            result.append({
                "igot_course_id":      e.get("courseId", ""),
                "course_title":        e.get("courseName", ""),
                "status":              "COMPLETED" if e.get("status") == 2
                                       else "IN_PROGRESS" if e.get("status") == 1
                                       else "NOT_STARTED",
                "progress_percentage": e.get("completionPercentage", 0),
                "remaining_minutes":   max(
                    0,
                    (e.get("leafNodesCount", 0) - e.get("progress", 0)) * 30,
                ),
                "last_accessed_at":    e.get("enrolledDate", ""),
                "provider_name":       course.get("provider", "iGOT Karmayogi")
                                       if course else "iGOT Karmayogi",
            })
        return result


# ── Concrete: HTTP Adapter (kept for backward compat / future live iGOT) ──────
class MockIgotAdapter(ILearningPlatformAdapter):
    """
    Delegates to the mock iGOT server over HTTP.

    Still useful if you run mock_igot_server.py (the Sunbird-compliant one).
    Prefer FileBasedIgotAdapter for local development to avoid port issues.
    """

    def __init__(self) -> None:
        self.base_url = "http://localhost:8001/api/external/igot"
        self.headers = {"Authorization": "Bearer mock_igot_secret_2026"}

    async def fetch_catalog(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/catalog", headers=self.headers, timeout=10.0
            )
            response.raise_for_status()
            return response.json().get("data", [])

    async def fetch_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/users/{user_id}/history",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json().get("data", [])

    async def fetch_user_roster(self) -> List[Dict[str, Any]]:
        # HTTP mock (simple main.py) doesn't have a roster endpoint;
        # fall back to the file-based approach.
        file_adapter = FileBasedIgotAdapter()
        return await file_adapter.fetch_user_roster()

    async def fetch_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        file_adapter = FileBasedIgotAdapter()
        return await file_adapter.fetch_user_by_id(user_id)

    async def fetch_user_enrollments(self, user_id: str) -> List[Dict[str, Any]]:
        file_adapter = FileBasedIgotAdapter()
        return await file_adapter.fetch_user_enrollments(user_id)
