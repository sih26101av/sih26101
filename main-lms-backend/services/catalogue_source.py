"""
services/catalogue_source.py — where the course catalogue comes from

The backend ranks over exactly one catalogue. `IGOT_CATALOGUE_SOURCE` decides
which:

    mock (default)  mock-igot-server on :8001 — synthetic courses carrying
                    competencies_v3 tags in the FRAC id space, plus the
                    enrollment_count / completion_rate signals the ranker's
                    quality composite likes. Everything works offline.

    live            the real iGOT Karmayogi catalogue over its public content
                    APIs (~5.2k courses). Real names, real descriptions, real
                    ratings, real KCM competency tags — but no enrolment or
                    completion aggregates, because iGOT does not publish them.

`live` is only the catalogue. Users, enrolments, ACBP plans, evidence and the
FRAC dictionary itself still come from the mock server: those iGOT endpoints sit
behind the Kong gateway and need a consumer key this project does not have.

Live courses are tagged against the Karmayogi Competency Model, not FRAC, so
they are rewritten through services.kcm_crosswalk on the way in — otherwise
they index under keys no gap ever asks for. See
docs/features/mock-igot-integration.md § "Live iGOT".

Order of preference in `live` mode: the portal, then the last good harvest on
disk (scripts/fetch_live_catalog.py), then the mock server. Each fallback is
logged, and `describe()` reports what actually happened so the admin console and
the startup log never imply data is live when it is not.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

LIVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "live")
LIVE_CATALOG_PATH   = os.path.join(LIVE_DIR, "live_catalog.json")
LIVE_CROSSWALK_PATH = os.path.join(LIVE_DIR, "live_kcm_crosswalk.json")

# Set by fetch(): "mock" | "live-api" | "live-disk", for the startup log and
# anywhere the UI has to say where the courses came from.
_resolved: str = "mock"

# Identifiers the live catalogue actually served, so a course can be linked to
# its page on the real portal. This has to be a membership test, not a pattern
# match: the mock generator mints ids in iGOT's own `do_<digits>` shape and not
# one of them is a real course, so every synthetic enrolment would otherwise
# render a link that 404s on portal.igotkarmayogi.gov.in.
_live_ids: frozenset = frozenset()


def configured_source() -> str:
    """"mock" or "live" — what .env asked for, not what was achieved."""
    return (os.getenv("IGOT_CATALOGUE_SOURCE") or "mock").strip().lower()


def describe() -> str:
    """What the catalogue actually resolved to on the last fetch()."""
    return _resolved


def is_live() -> bool:
    """True when the catalogue in memory came from the real portal."""
    return _resolved.startswith("live")


def live_course_url(course_id: Optional[str]) -> Optional[str]:
    """
    The course's page on the real iGOT portal, or None when we cannot vouch for
    it — mock mode, or an id the live catalogue never served (an enrolment from
    the synthetic roster, say). None means the UI shows a plain button instead
    of a dead link.
    """
    if not course_id or course_id not in _live_ids:
        return None
    from adapters.live_igot_adapter import course_url
    return course_url(course_id)


def _load_disk_catalogue() -> Optional[List[Dict[str, Any]]]:
    try:
        with open(LIVE_CATALOG_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError) as exc:
        logger.warning("[catalogue] no harvested live catalogue at %s (%s).", LIVE_CATALOG_PATH, exc)
        return None


def _apply_crosswalk(catalog: List[Dict[str, Any]]) -> None:
    """
    Stamp FRAC ids onto KCM tags in place. A missing crosswalk file is survivable
    but means live courses cannot match a gap, so it is logged loudly.
    """
    from services.kcm_crosswalk import apply_crosswalk, load_crosswalk
    mapping = load_crosswalk(LIVE_CROSSWALK_PATH)
    if not mapping:
        logger.warning("[catalogue] live catalogue has no KCM→FRAC crosswalk — courses will not "
                       "match competency gaps. Run: python -m scripts.fetch_live_catalog")
        return
    apply_crosswalk(catalog, mapping)


async def fetch(mock_adapter: Any) -> Tuple[List[Dict[str, Any]], str]:
    """
    The catalogue to rank over, plus the resolved source label.

    Raises only if every route failed — the caller already treats that as "run
    without an engine", and _warm_up logs it.
    """
    global _resolved, _live_ids
    if configured_source() != "live":
        _resolved, _live_ids = "mock", frozenset()
        return await mock_adapter.fetch_catalog(), _resolved

    from adapters.live_igot_adapter import LiveIgotAdapter
    live = LiveIgotAdapter()
    try:
        catalog = await live.fetch_catalog()
        _resolved = "live-api"
        logger.info("[catalogue] %d courses from the live iGOT portal (%s).",
                    len(catalog), live.base_url)
    except Exception as exc:
        logger.warning("[catalogue] live iGOT unreachable (%s) — trying the last harvest on disk.", exc)
        catalog = _load_disk_catalogue()
        if catalog is None:
            logger.warning("[catalogue] falling back to the mock server.")
            _resolved, _live_ids = "mock", frozenset()
            return await mock_adapter.fetch_catalog(), _resolved
        _resolved = "live-disk"
        logger.info("[catalogue] %d courses from the last live harvest on disk.", len(catalog))
    finally:
        await live.aclose()

    _apply_crosswalk(catalog)
    _live_ids = frozenset(c["identifier"] for c in catalog if c.get("identifier"))
    return catalog, _resolved
