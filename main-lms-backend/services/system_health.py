"""
services/system_health.py — the liveness payload behind GET /health and the
admin system-health panel (GET /api/v1/admin/console/system-health).

`basic()` is cheap and never does I/O — it is what /health returns (Render
health check / keep-alive). `detailed()` adds live probes: the auth DB, the
mock iGOT server, the embedders, Groq (key count) and (on request) Gemini.
"""
from __future__ import annotations

import asyncio
import os
import time
from typing import Any, Dict, List

import httpx

from services import app_state

_GEMINI_PLACEHOLDERS = {"", "your-actual-api-key-here", "your-gemini-api-key-here", "YOUR_GEMINI_API_KEY"}
_RANK = {"ok": 0, "unknown": 1, "degraded": 2, "down": 3}


def basic() -> Dict[str, Any]:
    from ai.semantic_engine import is_semantic_engine_ready
    return {
        "status": "ok",
        "ready": app_state.ready.is_set(),
        "recommendationEngine": app_state.engine is not None,
        "chatSemantic": is_semantic_engine_ready(),
        "workforceSnapshot": app_state.snapshot_status,
    }


def _component(cid: str, label: str, status: str, detail: str, **extra: Any) -> Dict[str, Any]:
    return {"id": cid, "label": label, "status": status, "detail": detail, **extra}


def _probe_db() -> Dict[str, Any]:
    from sqlalchemy import text
    from auth.database import IS_SQLITE, engine
    t0 = time.perf_counter()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        return _component("database", "Auth / evidence database", "down", f"Unreachable: {exc.__class__.__name__}")
    ms = round((time.perf_counter() - t0) * 1000)
    if IS_SQLITE:
        return _component("database", "Auth / evidence database", "degraded",
                          "Local SQLite fallback (DATABASE_URL not set) — data is per-machine.", latencyMs=ms)
    return _component("database", "Auth / evidence database", "ok", "Shared Postgres reachable.", latencyMs=ms)


async def _probe_igot() -> Dict[str, Any]:
    base = os.getenv("IGOT_MOCK_BASE_URL", "http://localhost:8001")
    t0 = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{base}/health")
            resp.raise_for_status()
            body = resp.json()
    except Exception as exc:
        return _component("igot", "iGOT Karmayogi connection", "down",
                          f"{base} unreachable ({exc.__class__.__name__}).")
    ms = round((time.perf_counter() - t0) * 1000)
    loaded = body.get("data_loaded") or {}
    return _component("igot", "iGOT Karmayogi connection", "ok",
                      f"{body.get('server', 'iGOT')} — {loaded.get('users', '?')} users, "
                      f"{loaded.get('courses', '?')} courses.", latencyMs=ms, dataLoaded=loaded)


def _gemini_list_models(key: str) -> List[str]:
    import google.generativeai as genai
    genai.configure(api_key=key)
    return [m.name for m in genai.list_models()]


async def _probe_gemini(probe: bool) -> Dict[str, Any]:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "").strip() or "default"
    if key in _GEMINI_PLACEHOLDERS:
        from services.media_quiz.providers import groq_keys
        if groq_keys():
            return _component("gemini", "Gemini (quiz generation)", "degraded",
                              "GEMINI_API_KEY is not configured — quizzes use Groq; video frame vision is off.",
                              model=model)
        return _component("gemini", "Gemini (quiz generation)", "down",
                          "GEMINI_API_KEY is not configured — AI quizzes are unavailable.", model=model)
    if not probe:
        return _component("gemini", "Gemini (quiz generation)", "unknown",
                          "API key configured; not probed (run a live check to call Gemini).", model=model)
    t0 = time.perf_counter()
    try:
        names = await asyncio.wait_for(asyncio.to_thread(_gemini_list_models, key), timeout=10.0)
    except asyncio.TimeoutError:
        return _component("gemini", "Gemini (quiz generation)", "degraded", "Gemini did not answer in 10 s.",
                          model=model)
    except Exception as exc:
        return _component("gemini", "Gemini (quiz generation)", "down",
                          f"Gemini call failed: {exc.__class__.__name__}.", model=model)
    ms = round((time.perf_counter() - t0) * 1000)
    return _component("gemini", "Gemini (quiz generation)", "ok", f"Reachable — {len(names)} models listed.",
                      model=model, latencyMs=ms)


def _groq_component() -> Dict[str, Any]:
    """Groq is the primary text LLM for quizzes; report key/model rotation state without calling it."""
    from services.media_quiz.providers import configured_providers, groq_keys
    keys = groq_keys()
    if not keys:
        return _component("groq", "Groq (primary quiz LLM)", "unknown",
                          "GROQ_API_KEYS not configured — quizzes use Gemini only.")
    providers = configured_providers()
    usable = [p.model for p in providers if p.available()]
    status = "ok" if usable else "degraded"
    detail = (f"{len(keys)} key(s) rotating over {len(providers)} model(s); "
              f"{len(usable)} model(s) currently usable." if usable else
              "All keys are rate-limited or disabled — falling back to Gemini.")
    return _component("groq", "Groq (primary quiz LLM)", status, detail,
                      model=", ".join(p.model for p in providers), keyCount=len(keys))


def _embedders() -> List[Dict[str, Any]]:
    from ai.embedder import is_embedder_ready, model_name
    from ai.semantic_engine import is_semantic_engine_ready
    out = []
    for role, label in (("catalog", "Catalogue embedder (recommendations)"), ("chat", "Chat embedder (Gyan)")):
        ready = is_embedder_ready(role)
        out.append(_component(f"embedder_{role}", label, "ok" if ready else
                              ("degraded" if app_state.ready.is_set() else "unknown"),
                              f"{model_name(role)} {'loaded' if ready else 'not loaded'}.", model=model_name(role)))
    out.append(_component("chat_semantic", "Gyan semantic intent tier",
                          "ok" if is_semantic_engine_ready() else "degraded",
                          "Ready." if is_semantic_engine_ready() else "Falling back to the template tier."))
    return out


def _engine_and_data() -> List[Dict[str, Any]]:
    warming = not app_state.ready.is_set()
    engine = app_state.engine
    out = [_component("engine", "Recommendation engine",
                      "ok" if engine else ("unknown" if warming else "down"),
                      (f"Catalogue source: {getattr(engine, 'catalog_source', '?')}." if engine
                       else "Warming up…" if warming else "Failed to initialise — see the startup log."))]
    sources = app_state.ref.sources
    missing = sorted(k for k, v in sources.items() if v == "missing")
    disk = sorted(k for k, v in sources.items() if v == "disk")
    status = "unknown" if not sources else "down" if missing else "degraded" if disk else "ok"
    detail = ("Not loaded yet." if not sources else
              f"Missing: {', '.join(missing)}." if missing else
              f"Read from disk (adapter failed): {', '.join(disk)}." if disk else
              f"All {len(sources)} datasets loaded from iGOT.")
    out.append(_component("reference_data", "SCIL reference datasets", status, detail, sources=sources))
    snap = app_state.snapshot_status
    out.append(_component("workforce_snapshot", "Workforce snapshot",
                          "ok" if snap == "ready" else "down" if snap.startswith("failed") else "unknown",
                          f"{snap} ({len(app_state.snapshot or {})} officials)."))
    return out


async def detailed(probe_gemini: bool = False) -> Dict[str, Any]:
    db, igot, gemini = await asyncio.gather(asyncio.to_thread(_probe_db), _probe_igot(),
                                            _probe_gemini(probe_gemini))
    components = [igot, db, *_engine_and_data(), *_embedders(), _groq_component(), gemini]
    worst = max((c["status"] for c in components), key=lambda s: _RANK[s])
    overall = {"ok": "ok", "unknown": "ok", "degraded": "degraded", "down": "degraded"}[worst]
    if igot["status"] == "down" or db["status"] == "down":
        overall = "down"
    return {"overall": overall, "checkedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "health": basic(), "components": components}
