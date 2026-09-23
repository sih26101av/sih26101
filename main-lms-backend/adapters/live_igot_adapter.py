"""
adapters/live_igot_adapter.py — the REAL iGOT Karmayogi platform (read-only)

Talks to https://portal.igotkarmayogi.gov.in. Only the *content* half of the
Sunbird API is reachable without credentials, and that is deliberate on their
side — content is public, anything about a named official is not:

    open (HTTP 200, no auth)          gated (HTTP 401 at the Kong gateway)
    ──────────────────────────        ──────────────────────────────────
    POST /api/content/v1/search       POST /api/composite/v1/search
    GET  /api/content/v1/read/{id}    GET  /api/user/v2/read/{id}
    GET  /api/course/v1/hierarchy/{id}GET  /api/course/v1/user/enrollment/list/{id}
    GET  /api/framework/v1/read/{fw}  POST /api/user/v1/search
    GET  /api/channel/v1/read/{id}

So this adapter serves the catalogue and the competency framework, and refuses
the per-user calls rather than pretending to answer them — `MockIgotAdapter`
keeps serving those until Karmayogi Bharat issues a Kong consumer key (see
docs/features/mock-igot-integration.md § "Live iGOT").

Two fields the mock invents do NOT exist upstream: `enrollment_count` and
`completion_rate`. They are learner-behaviour aggregates and live behind the
401. Live courses therefore carry `None` for both, which the engine already
handles — a course missing a quality field takes the catalogue mean rather than
a fabricated default (see recommendation_service._build_quality_norms).

Competency tags: production has moved to `competencies_v6` (the Karmayogi
Competency Model — 99.9% of live courses carry it, and the search endpoint
returns it inline). The legacy `competencies_v3` CID tags survive on a small
minority of courses only, so v6 is the field to rank on.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

import httpx

from adapters.igot_adapter import ILearningPlatformAdapter

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://portal.igotkarmayogi.gov.in"

# The framework that holds the Karmayogi Competency Model: 3 competency areas,
# 146 themes, 601 sub-themes. `competencies_v6` tags reference its refIds.
KCM_FRAMEWORK_ID = "kcmfinal_fw"

# Live search honours limits well past 1000, but a page carrying full course
# descriptions is ~4 MB and the portal can take a while to assemble one. 400 is
# comfortably inside the read timeout on a slow connection; the pager halves it
# further on a timeout rather than giving up.
_SEARCH_PAGE = 400
_SEARCH_TIMEOUT = 120.0

# Fields to project in the catalogue search. Asking for exactly what the engine
# parses keeps the whole 5k-course pull around 10 MB instead of ~120 MB.
_CATALOG_FIELDS = [
    "identifier", "name", "description", "primaryCategory", "objectType",
    "duration", "leafNodesCount", "avgRating", "totalNoOfRating",
    "competencies_v6", "keywords", "language", "difficultyLevel",
    "source", "organisation", "creator", "channel", "posterImage",
    "contentType", "mimeType", "learningMode",
]

_GATED = (
    "iGOT serves this only to an authenticated Kong consumer. The live adapter "
    "is read-only over the public content APIs; keep MockIgotAdapter for "
    "per-user data until a platform key is issued."
)


def course_url(identifier: str, base_url: Optional[str] = None) -> str:
    """
    The learner-facing page for a course on the real portal:
    https://portal.igotkarmayogi.gov.in/app/toc/<identifier>/overview

    This only formats the URL — it does NOT check that the course exists. The
    mock catalogue mints ids in the same `do_<digits>` shape as iGOT and none of
    them are real, so a pattern match is not enough to decide whether a link is
    safe to show. Call `services.catalogue_source.live_course_url()` instead,
    which only returns a URL for a course the live catalogue actually served.
    """
    base = (base_url or os.getenv("IGOT_LIVE_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    return f"{base}/app/toc/{identifier.strip()}/overview"


class LiveIgotAdapter(ILearningPlatformAdapter):
    """
    Read-only adapter over the public iGOT content APIs.

    Catalogue calls go upstream; per-user calls raise `NotImplementedError` so a
    wiring mistake fails loudly instead of silently serving an empty roster.
    """

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None) -> None:
        # Read the environment here rather than at import, so the harvest script,
        # the tests and anything that loads .env after this module can still
        # redirect the adapter.
        self.base_url = (base_url or os.getenv("IGOT_LIVE_BASE_URL")
                         or DEFAULT_BASE_URL).rstrip("/")
        # No key is needed today. If Karmayogi Bharat issues one it is a Kong
        # consumer key and belongs in the standard Sunbird Authorization header;
        # sending it also unlocks the composite-search and user endpoints.
        self.token = token if token is not None else os.getenv("IGOT_LIVE_TOKEN", "")
        self.page_size = int(os.getenv("IGOT_LIVE_PAGE_SIZE", str(_SEARCH_PAGE)))
        self.timeout = float(os.getenv("IGOT_LIVE_TIMEOUT", str(_SEARCH_TIMEOUT)))
        self._headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.token:
            self._headers["Authorization"] = f"Bearer {self.token}"
        self._clients: Dict[int, httpx.AsyncClient] = {}

    def _client(self) -> httpx.AsyncClient:
        """Pooled client per event loop — the warm-up thread runs its own."""
        key = id(asyncio.get_running_loop())
        client = self._clients.get(key)
        if client is None or client.is_closed:
            client = httpx.AsyncClient(headers=self._headers, timeout=self.timeout,
                                       follow_redirects=True)
            self._clients[key] = client
        return client

    # ── Catalogue (public) ────────────────────────────────────────────────────

    async def fetch_catalog(self) -> List[Dict[str, Any]]:
        """
        Every Live course, normalised to the internal catalogue shape.

        Pages POST /api/content/v1/search. ~5.2k courses in a handful of
        requests; the whole pull takes a few seconds.
        """
        raw = await self.search_catalog({"primaryCategory": ["Course"], "status": ["Live"]})
        return [normalise_course(c) for c in raw]

    async def search_catalog(self, filters: Optional[Dict[str, Any]] = None,
                             fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        POST /api/content/v1/search — every page, raw upstream records.

        `filters` takes any indexed content field, e.g.
        {"primaryCategory": ["Course"], "status": ["Live"], "se_FWIds": [...]}.
        """
        out: List[Dict[str, Any]] = []
        total: Optional[int] = None
        page_size = self.page_size
        while True:
            result = await self._search_page(
                filters or {"primaryCategory": ["Course"], "status": ["Live"]},
                fields if fields is not None else _CATALOG_FIELDS,
                offset=len(out), limit=page_size,
            )
            page = result.get("content") or []
            if total is None:
                total = int(result.get("count") or 0)
                logger.info("[live-igot] catalogue: %d Live courses upstream.", total)
            out.extend(page)
            # Upstream repeats the last page rather than returning [] past the end.
            if not page or (total and len(out) >= total):
                return out[:total] if total else out

    async def _search_page(self, filters: Dict[str, Any], fields: List[str],
                           offset: int, limit: int) -> Dict[str, Any]:
        """
        One page, with the retry matched to the failure:

        * read timeout, or a 502/503/504 from the gateway — the portal is
          struggling to assemble a large response, so halve the page and back
          off. The public gateway does this intermittently under a full
          catalogue pull, and a smaller page usually goes straight through.
        * connect error — nothing is listening. Shrinking the request cannot
          help, so fail immediately rather than sleeping through four attempts.
        """
        client = self._client()
        attempt_limit = limit
        last: Optional[Exception] = None
        for attempt in range(4):
            body = {"request": {"filters": filters, "fields": fields,
                                "limit": attempt_limit, "offset": offset}}
            try:
                resp = await client.post(f"{self.base_url}/api/content/v1/search", json=body)
                resp.raise_for_status()
                return resp.json().get("result", {}) or {}
            except httpx.ConnectError as exc:
                raise RuntimeError(
                    f"live iGOT unreachable at {self.base_url}: {exc}") from exc
            except (httpx.TimeoutException, httpx.HTTPStatusError, httpx.TransportError) as exc:
                status = getattr(getattr(exc, "response", None), "status_code", None)
                if status is not None and status not in (502, 503, 504):
                    raise                       # a real 4xx — retrying changes nothing
                last = exc
                if attempt == 3:
                    break
                attempt_limit = max(25, attempt_limit // 2)
                logger.warning("[live-igot] search failed at offset %d (%s) — retrying with limit %d.",
                               offset, status or type(exc).__name__, attempt_limit)
                await asyncio.sleep(2.0 * (attempt + 1))
        raise RuntimeError(f"live iGOT search failed at offset {offset}: {last}") from last

    async def fetch_course(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        GET /api/content/v1/read/{id} — the full ~94-field record for one course.
        Richer than the search projection (adds instructions, toc_url, the legacy
        competencies_v3/v5 tags where they survive). None if the id is unknown.
        """
        try:
            resp = await self._client().get(
                f"{self.base_url}/api/content/v1/read/{identifier}")
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            raise
        return (resp.json().get("result") or {}).get("content")

    async def fetch_course_hierarchy(self, identifier: str) -> Optional[Dict[str, Any]]:
        """GET /api/course/v1/hierarchy/{id} — the module / leaf tree inside a course."""
        try:
            resp = await self._client().get(
                f"{self.base_url}/api/course/v1/hierarchy/{identifier}")
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            raise
        return (resp.json().get("result") or {}).get("content")

    async def fetch_kcm_framework(self) -> Dict[str, Any]:
        """
        GET /api/framework/v1/read/kcmfinal_fw — the Karmayogi Competency Model.
        Returns {competencyarea: [...], theme: [...], subtheme: [...]}, each term
        carrying `refId` (COMTHEME-000225 …), `name`, `description`.
        """
        resp = await self._client().get(
            f"{self.base_url}/api/framework/v1/read/"
            f"{os.getenv('IGOT_KCM_FRAMEWORK') or KCM_FRAMEWORK_ID}")
        resp.raise_for_status()
        fw = (resp.json().get("result") or {}).get("framework") or {}
        return {c.get("code"): (c.get("terms") or []) for c in (fw.get("categories") or [])}

    # ── Gated behind the Kong gateway ─────────────────────────────────────────

    async def fetch_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError(f"GET /api/user/v2/read — {_GATED}")

    async def fetch_user_enrollments(self, user_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError(f"GET /api/course/v1/user/enrollment/list — {_GATED}")

    async def fetch_user_roster(self) -> List[Dict[str, Any]]:
        raise NotImplementedError(f"POST /api/user/v1/search — {_GATED}")

    async def fetch_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError(f"user learning history — {_GATED}")

    async def aclose(self) -> None:
        for client in self._clients.values():
            if not client.is_closed:
                await client.aclose()
        self._clients.clear()


# ── Upstream record → internal catalogue shape ───────────────────────────────

def _first_str(value: Any) -> str:
    """Upstream returns some fields as a bare string and others as a list."""
    if isinstance(value, list):
        return str(value[0]) if value else ""
    return str(value) if value else ""


def _as_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(v) for v in value if v]
    return [str(value)] if value else []


def normalise_course(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    One upstream content record → the dict shape `_parse_catalog` consumes.

    Deliberately omits `enrollment_count`, `completion_rate` and `is_tpac`:
    iGOT does not publish the first two at all, and TPAC vetting is an NSSTA
    concept with no iGOT field. Leaving them absent makes the engine treat the
    course as "unknown" on those axes (catalogue mean) instead of scoring it a
    zero it never earned.
    """
    comps = raw.get("competencies_v6")
    if isinstance(comps, str):                       # occasionally a JSON string
        try:
            comps = json.loads(comps)
        except ValueError:
            comps = None

    return {
        "identifier":      raw.get("identifier", ""),
        "name":            (raw.get("name") or "").strip(),
        "description":     (raw.get("description") or "").strip(),
        # duration is seconds-as-string upstream, which is what the parser expects.
        "duration":        str(raw.get("duration") or "0"),
        "leafNodesCount":  raw.get("leafNodesCount"),
        "competencies_v6": comps or [],
        # Kept so a course that still carries legacy CID tags keeps them; the
        # parser prefers v3 when present because those ids match the FRAC set.
        "competencies_v3": raw.get("competencies_v3") or "",
        "rating":          raw.get("avgRating"),
        "rating_count":    raw.get("totalNoOfRating"),
        "level":           raw.get("difficultyLevel"),
        "creator":         _first_str(raw.get("creator") or raw.get("source")),
        "organisation":    _as_list(raw.get("organisation") or raw.get("source")),
        "channel":         _first_str(raw.get("channel")),
        "language":        _as_list(raw.get("language")),
        "keywords":        _as_list(raw.get("keywords")),
        "posterImage":     raw.get("posterImage") or "",
        "source":          "iGOT Karmayogi",
    }
