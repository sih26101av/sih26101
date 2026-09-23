"""
main.py — MoSPI LMS Backend API (Main Orchestrator)
─────────────────────────────────────────────────────────────────────────────
Service #3: My App Backend (port 8000)

Responsibilities
────────────────
• Owns all application-level authentication & authorisation (JWT + RBAC).
• Calls the Mock iGOT Server (port 8001) as an internal data-fetch step
  AFTER a request has been authenticated/authorised here.
• Never stores auth data on the mock server; never proxies raw tokens.

On startup the port binds at once; the rest happens in the background:
  • _create_schema — users_auth + karma tables in the auth DB (Neon Postgres,
    or SQLite auth.db fallback), idempotent → app_state.db_ready
  • _warm_up — embedders, recommendation engine, SCIL reference data → app_state.ready
_readiness_gate holds each request only for what it needs (see _UNGATED).
GET /health reports both states and never waits.
"""

from routers import competency
from services.recommendation_service import CLASSROOM_CAP_HOURS_PER_QUARTER, HybridRecommendationEngine
from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from adapters.igot_adapter import MockIgotAdapter
from auth.database import AuthBase, engine
from auth.dependencies import get_current_user, require_role
from auth.models import UserAuth
from auth.router import router as auth_router
from models.domain import (
    AchievementsResponse,
    EnrollmentsResponse,
    RecommendationResponse,
    SkillGapResponse,
)
from routers.chatbot import router as chatbot_router
from routers.rag import router as rag_router
from routers.media_quiz import router as media_quiz_router
from routers.learning_mode import router as learning_mode_router
from routers.ai_tools import router as ai_tools_router
from routers.karma import router as karma_router
import httpx
import json
import os
import uvicorn


# ── App bootstrap ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="MoSPI LMS Backend API",
    description="Main Orchestrator Server — owns auth, delegates data to iGOT adapter",
    version="2.0",
)

# ── Readiness gate ─────────────────────────────────────────────────────────────
# Startup binds the port before the schema check and AI warm-up finish. Every
# request except /health and the docs waits for the schema (_create_schema);
# routes that read the engine / assembler / reference data / chat embedder
# also wait for _warm_up instead of failing. Auth, karma and RAG only need the
# DB. Registered before CORS so CORS stays the outermost middleware.
import asyncio
import re as _re
from starlette.middleware.base import BaseHTTPMiddleware

_NO_WAIT = _re.compile(r"^/(?:health|docs|redoc|openapi\.json)")
_UNGATED = _re.compile(r"^/(?:$|auth/|api/v1/(?:rag/|ai/|chat/mode|recommendations/feedback))|/karma(?:/|$)")
_WARMUP_WAIT_S = float(os.getenv("WARMUP_WAIT_SECONDS", "240"))


async def _readiness_gate(request, call_next):
    path = request.url.path
    if request.method != "OPTIONS" and not _NO_WAIT.search(path):
        waits = [app_state.db_ready] + ([] if _UNGATED.search(path) else [app_state.ready])
        for event in waits:
            if not event.is_set():
                try:
                    await asyncio.wait_for(event.wait(), timeout=_WARMUP_WAIT_S)
                except asyncio.TimeoutError:
                    pass    # handlers already degrade (503) when the engine is missing
    return await call_next(request)


app.add_middleware(BaseHTTPMiddleware, dispatch=_readiness_gate)

# ── CORS ───────────────────────────────────────────────────────────────────────
# Tightened from allow_origins=["*"] to explicit frontend origin so that
# httpOnly cookies are accepted (credentials require a non-wildcard origin).
# Deployed frontends (e.g. the Vercel URL) are added via CORS_ORIGINS, comma-separated.
_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",   # Vite default dev server port
    "http://127.0.0.1:5173",
] + [o.strip().rstrip("/") for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=True,   # Required for cookies to be sent cross-origin
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup: create auth.db table ─────────────────────────────────────────────
# ── App-level recommendation engine singleton ─────────────────────────────────
# Built once at startup: loads catalog JSON, builds FAISS index + BM25 corpus.
# All recommendation requests share this singleton (thread-safe read-only).
from services.baseline_assembler import BaselineAssembler

# ── App-level recommendation engine singleton ─────────────────────────────────
# Built once at startup: loads catalog JSON, builds FAISS index + BM25 corpus.
# All recommendation requests share this singleton (thread-safe read-only).
_rec_engine: HybridRecommendationEngine | None = None

# ── App-level baseline assembler singleton ────────────────────────────────────
# Shares the course→comp index from _rec_engine so we don't duplicate it.
_assembler: BaselineAssembler | None = None

# ── SCIL v6 reference data (GSBPM map, office workload, …) ────────────────────
from services.reference_data import ReferenceData
from services import app_state, gsbpm_service, prerequisite_service, proficiency_service
_ref: ReferenceData = ReferenceData()



@app.on_event("startup")
async def _startup():
    """Return at once so uvicorn binds the port; schema + warm-up run in the background."""
    import threading
    loop = asyncio.get_running_loop()
    loop.create_task(_create_schema())
    # Admin console: upserts today's workforce trend snapshot hourly (waits for the DB itself).
    from routers.admin_console import daily_snapshot_loop
    loop.create_task(daily_snapshot_loop())
    # Own thread + own event loop: the warm-up's HTTP clients, JSON parsing and
    # model loading never delay the server binding its port or answering requests.
    threading.Thread(target=lambda: asyncio.run(_warm_up(loop)), name="warm-up", daemon=True).start()


async def _create_schema():
    """Create users_auth and the karma/evidence tables if missing (idempotent)."""
    import logging

    def _create():
        from models.models import Base as DomainBase
        with engine.begin() as conn:        # one connection for all the table checks
            AuthBase.metadata.create_all(bind=conn)
            # Karma tables (KarmaEvent, KarmaMonthlyUsage) live in the same auth DB
            DomainBase.metadata.create_all(bind=conn)
        from services.karma_engine import migrate_karma_schema
        migrate_karma_schema(engine)        # referenceId/note columns, enum values, unique index
    try:
        await asyncio.to_thread(_create)
    except Exception as exc:
        logging.getLogger(__name__).error("[startup] Auth DB schema check failed: %s", exc)
    finally:
        app_state.db_ready.set()


async def _warm_up(server_loop: asyncio.AbstractEventLoop):
    """
    Everything slow, off the request path, on the "warm-up" thread's own loop
    so `server_loop` keeps serving auth, karma and /health meanwhile. Sets
    app_state.ready (on server_loop) when done — even on failure, since the
    handlers already cope with a missing engine — then starts the workforce
    snapshot on server_loop.
    """
    global _rec_engine, _assembler, _ref
    import logging
    import time
    log = logging.getLogger(__name__)
    t0 = time.perf_counter()
    try:
        # Chat embedder + intent prototypes (cached on disk by ai/embedder.encode_cached).
        from ai.semantic_engine import _ensure_prototypes
        chat_warm = asyncio.to_thread(_ensure_prototypes)

        # One catalogue: rank over exactly what the mock iGOT server serves. If it
        # is down, fall back to the same generated files on disk (and say so).
        # Fetched concurrently with the chat warm-up and the reference data.
        async def _catalogue():
            try:
                return await asyncio.gather(adapter.fetch_catalog(), adapter.fetch_frac_competencies(),
                                            adapter.fetch_frac_crosswalk())
            except Exception as exc:
                log.warning("[startup] iGOT mock server unreachable (%s) — loading the catalogue from "
                            "mock-igot-server/data/*.json on disk instead.", exc)
                return None, None, None

        # SCIL v6 reference data (GSBPM map, office workload, …) — adapter, disk fallback.
        _, (catalog, frac, crosswalk), _ref = await asyncio.gather(
            chat_warm, _catalogue(), ReferenceData.load(adapter))
        if catalog is not None:
            log.info("[startup] Catalogue loaded from iGOT adapter: %d courses, %d FRAC competencies.",
                     len(catalog), len(frac))

        try:
            _rec_engine, _assembler = await asyncio.to_thread(_build_engine, catalog, frac, crosswalk, _ref)
            log.info("[startup] HybridRecommendationEngine ready (catalogue source: %s, embeddings %s).",
                     _rec_engine.catalog_source, _rec_engine.embedding_stats)
            log.info("[startup] BaselineAssembler ready. Mapped %d courses, %d rater offsets.",
                     len(_rec_engine.course_comp_levels()), len(_ref.rater_offsets))
            if catalog is not None:
                from services.catalogue_store import catalogue_fingerprint
                app_state.catalogue_fingerprint = catalogue_fingerprint(catalog, frac)
        except Exception as exc:
            log.error("[startup] Engine/Assembler failed to initialise: %s", exc)
            _rec_engine = None
            _assembler  = None

        app_state.engine, app_state.assembler, app_state.ref = _rec_engine, _assembler, _ref
        app_state.snapshot_builder = _build_workforce_snapshot
        app_state.competency_state = _learner_competency_state

        # SCIL v6 §6: measured course uplift from outcome assessments (~1 s), used to
        # flag near-zero-uplift courses in ranking and for the admin effectiveness view.
        if _ref.outcomes and _rec_engine is not None:
            from services.uplift_service import estimate_uplift
            try:
                _ref.cache["uplift"] = await asyncio.to_thread(
                    estimate_uplift, _ref.outcomes, _ref.comparisons, _rec_engine.course_meta())
                _rec_engine.set_measured_uplift(_ref.cache["uplift"]["courses"])
                log.info("[startup] Measured uplift for %d courses (%d flagged).",
                         len(_ref.cache["uplift"]["courses"]),
                         sum(c["misTagFlag"] for c in _ref.cache["uplift"]["courses"]))
            except Exception as exc:
                log.error("[startup] Uplift estimation failed: %s", exc)
    except Exception as exc:
        log.error("[startup] Warm-up failed: %s", exc)
    finally:
        server_loop.call_soon_threadsafe(app_state.ready.set)
        log.info("[startup] Warm-up finished in %.1fs.", time.perf_counter() - t0)

    async def _snapshot_after_schema():
        await app_state.db_ready.wait()     # the snapshot reads EvidenceLog
        await _build_workforce_snapshot()
    asyncio.run_coroutine_threadsafe(_snapshot_after_schema(), server_loop)
    asyncio.run_coroutine_threadsafe(_refresh_catalogue_loop(), server_loop)


def _build_engine(catalog, frac, crosswalk, ref: ReferenceData):
    """
    Engine + assembler from one catalogue (sync — run in a thread). Course vectors
    come from the database when their model and text hash still match
    (services/catalogue_store.py); new or changed courses are encoded and saved back.
    """
    from ai.embedder import model_name
    from services import catalogue_store
    model = model_name("catalog")
    stored = catalogue_store.load_embeddings(model)
    engine_ = HybridRecommendationEngine(catalog=catalog, frac=frac, crosswalk=crosswalk,
                                         precomputed_embeddings=stored)
    catalogue_store.save_embeddings(model, engine_.course_embeddings(), known=stored)
    # {course_id → {comp_id → FRAC level}} from the same tags the engine filters
    # on, so the Verified channel credits a completed course at its tagged level.
    assembler_ = BaselineAssembler(engine_.course_comp_levels(), rater_offsets=ref.rater_offsets)
    return engine_, assembler_


_CATALOGUE_REFRESH_S = float(os.getenv("CATALOGUE_REFRESH_SECONDS", "3600"))


async def _refresh_catalogue_loop() -> None:
    """
    Reload the catalogue on a timer instead of only at restart. Every
    CATALOGUE_REFRESH_SECONDS (default 1 h, 0 disables) the catalogue + FRAC set
    are fetched through the adapter; if their fingerprint changed, a new engine
    is built in a thread (unchanged courses reuse their stored vectors) and
    swapped in atomically. Requests in flight keep the old engine.
    """
    global _rec_engine, _assembler
    import logging
    from services.catalogue_store import catalogue_fingerprint
    log = logging.getLogger(__name__)
    if _CATALOGUE_REFRESH_S <= 0:
        return
    while True:
        await asyncio.sleep(_CATALOGUE_REFRESH_S)
        try:
            catalog, frac, crosswalk = await asyncio.gather(
                adapter.fetch_catalog(), adapter.fetch_frac_competencies(), adapter.fetch_frac_crosswalk())
            fp = catalogue_fingerprint(catalog, frac)
            if fp == app_state.catalogue_fingerprint:
                continue
            engine_, assembler_ = await asyncio.to_thread(_build_engine, catalog, frac, crosswalk, _ref)
            if "uplift" in _ref.cache:
                engine_.set_measured_uplift(_ref.cache["uplift"]["courses"])
            _rec_engine, _assembler = engine_, assembler_
            app_state.engine, app_state.assembler = engine_, assembler_
            app_state.catalogue_fingerprint = fp
            app_state.user_state_cache.clear()          # levels depend on course tags
            log.info("[catalogue] refreshed: %d courses (embeddings %s).",
                     len(catalog), engine_.embedding_stats)
        except Exception as exc:
            log.warning("[catalogue] refresh skipped: %s", exc)


@app.get("/health", tags=["meta"])
async def health():
    """Liveness + warm-up state. Cheap: use it as the Render health check / keep-alive ping.
    The admin console's system-health panel extends the same payload with live probes."""
    from services import system_health
    return system_health.basic()


# ── Register routers ───────────────────────────────────────────────────────────
app.include_router(auth_router,    prefix="/auth",       tags=["auth"])
app.include_router(chatbot_router, prefix="/api/v1",     tags=["chatbot"])
app.include_router(rag_router,     prefix="/api/v1/rag", tags=["rag"])
app.include_router(media_quiz_router, prefix="/api/v1/rag/media", tags=["media-quiz"])
app.include_router(learning_mode_router, prefix="/api/v1/rag/learning", tags=["learning-mode"])
app.include_router(ai_tools_router,prefix="/api/v1/ai",  tags=["ai-tools"])
app.include_router(karma_router,   prefix="/api/v1",     tags=["karma"])
app.include_router(competency.router)
from routers.insights import router as insights_router
app.include_router(insights_router)
from routers.diagnostic import router as diagnostic_router
app.include_router(diagnostic_router)
from routers.career import router as career_router
app.include_router(career_router)
from routers.recommendation_feedback import router as recommendation_feedback_router
app.include_router(recommendation_feedback_router)
from routers import admin_console
app.include_router(admin_console.router)
app.include_router(admin_console.learner_router)
# Gyan on the admin console — same assistant, plus a tier that reads admin data.
from routers.admin_chat import router as admin_chat_router
app.include_router(admin_chat_router)
    
    



# ── iGOT Adapter singleton (HTTP → mock_igot_server.py on port 8001) ────────────
# Data only flows when the Sunbird-compliant mock server is running.
# Run: cd mock-igot-server && uvicorn mock_igot_server:app --reload --port 8001
adapter = MockIgotAdapter()

# ── iGOT mock server config (kept for admin proxy endpoint) ────────────────────
_IGOT_BASE = os.getenv("IGOT_MOCK_BASE_URL", "http://localhost:8001")
_IGOT_TOKEN = os.getenv("IGOT_MOCK_TOKEN", "mock-api-key-2026")




# ── Helper: parse competency level string → int ────────────────────────────────
def _level_to_int(level_str: str) -> int:
    """'Level 3' → 3, 'Level 2' → 2, fallback → 2"""
    digits = "".join(filter(str.isdigit, level_str or ""))
    return int(digits) if digits else 2


# ── Skill-gap / recommendation / pathway shared state ─────────────────────────

def _ensure_can_view(user_id: str, current_user: UserAuth) -> None:
    """A learner may only read their own competency data; admins may read anyone's."""
    from fastapi import HTTPException
    if current_user.username != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only view your own learning data.")


def _self_reported_level(comp: dict) -> int:
    """iGOT profile competencyLevel ('Level 3') → 3; missing → 0 (no claim)."""
    import re
    m = re.search(r"\d+", comp.get("competencyLevel") or "")
    return int(m.group()) if m else 0


async def _build_workforce_snapshot() -> None:
    """
    Every official's resolved competency rows, for the SCIL v6 population /
    cohort priors and the admin foresight views. Built in the background after
    startup (≈ 151 officials × 3 mock calls) and on demand from the admin API.
    """
    import logging
    log = logging.getLogger(__name__)
    app_state.snapshot_status = "building"
    try:
        roster = await adapter.fetch_user_roster()
        snap = {}
        for entry in roster:
            uid = entry["userId"]
            try:
                state = await _learner_competency_state(uid, annotate=False)
            except Exception as exc:                        # one bad profile must not stop the rest
                log.warning("[snapshot] %s skipped: %s", uid, exc)
                continue
            user = state["user"]
            jp = user.get("jobProfile") or {}
            snap[uid] = {
                "officeId": jp.get("officeId"),
                "phase": proficiency_service.office_phase(_ref.offices.get(jp.get("officeId") or "")),
                "tier": jp.get("tier"),
                "experienceYears": int(user.get("experienceYears") or 0),
                "competencies": [
                    {"catalogueId": r["catalogueId"] or r["competencyId"], "competencyId": r["competencyId"],
                     "level": r["currentLevel"], "target": r["targetLevel"], "confidence": r["confidence"],
                     "mu": r["rawScore"], "lastEvidenceDate": r["lastEvidenceDate"],
                     "decayClass": r["decayClass"]}
                    for r in state["competencies"]
                ],
            }
        app_state.snapshot = snap
        app_state.snapshot_status = "ready"
        # Annotated states were built against the old population / cohort priors.
        for key in [k for k in app_state.user_state_cache if k[1]]:
            app_state.user_state_cache.pop(key, None)
        _ref.cache.pop("workforce", None)
        log.info("[snapshot] workforce snapshot ready: %d officials.", len(snap))
    except Exception as exc:
        app_state.snapshot_status = f"failed: {exc}"
        log.error("[snapshot] failed: %s", exc)


_STATE_CACHE_TTL_S = float(os.getenv("COMPETENCY_STATE_CACHE_SECONDS", "30"))


async def _learner_competency_state(user_id: str, annotate: bool = True) -> dict:
    """
    Memoised _resolve_competency_state. Concurrent callers (the dashboard's
    /skill-gaps, /recommendations, /pathway) share one in-flight resolution;
    the result is kept for _STATE_CACHE_TTL_S or until an EvidenceLog write
    calls app_state.invalidate_user. Errors are never cached. The returned
    dict is shared — callers must not mutate it.
    """
    import time
    key = (user_id, annotate)
    now = time.monotonic()
    hit = app_state.user_state_cache.get(key)
    if hit and hit[0] > now:
        value = hit[1]
        return await asyncio.shield(value) if isinstance(value, asyncio.Future) else value

    task = asyncio.ensure_future(_resolve_competency_state(user_id, annotate))
    app_state.user_state_cache[key] = (now + _STATE_CACHE_TTL_S, task)
    try:
        state = await asyncio.shield(task)
    except Exception:
        if app_state.user_state_cache.get(key, (0, None))[1] is task:
            app_state.user_state_cache.pop(key, None)
        raise
    # Only store if nobody invalidated this entry while it was being computed.
    if app_state.user_state_cache.get(key, (0, None))[1] is task:
        app_state.user_state_cache[key] = (time.monotonic() + _STATE_CACHE_TTL_S, state)
    return state


def _load_db_evidence(user_id: str) -> list:
    """The LMS's own EvidenceLog rows for one user (sync — run in a worker thread)."""
    from auth.database import session_scope
    from models.models import EvidenceLog

    try:
        with session_scope() as db_session:
            return [
                {
                    "comp_id":       row.compId,
                    "evidence_type": row.evidenceType,
                    "granted_value": row.grantedValue,
                    "issue_date":    row.issueDate,
                }
                for row in db_session.query(EvidenceLog).filter(EvidenceLog.userId == user_id).all()
            ]
    except Exception:
        return []


async def _resolve_competency_state(user_id: str, annotate: bool = True) -> dict:
    """
    Profile + enrollments + EvidenceLog → one resolved row per role competency.

    This is the ONLY place a learner's level is decided (via
    baseline_assembler.resolve_level); skill-gaps, recommendations and pathway
    all read these rows, so the dashboard and the course suggestions can no
    longer disagree about the same gap.

    The four reads (profile, enrollments, iGOT workplace evidence, the LMS
    EvidenceLog in Postgres) run concurrently; the DB read runs in a thread so
    a slow Neon round-trip never blocks the event loop.
    """
    from fastapi import HTTPException
    from services.baseline_assembler import explain_level, resolve_level

    user_r, enrollments_r, igot_evidence_r, db_evidence = await asyncio.gather(
        adapter.fetch_user_by_id(user_id),
        adapter.fetch_user_enrollments(user_id),
        adapter.fetch_user_evidence(user_id),
        asyncio.to_thread(_load_db_evidence, user_id),
        return_exceptions=True,
    )
    if isinstance(user_r, BaseException):
        raise HTTPException(
            status_code=503,
            detail="iGOT mock server is unreachable. Start it with: "
                   "cd mock-igot-server && uvicorn mock_igot_server:app --port 8001",
        )
    user = user_r
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")

    enrollments = [] if isinstance(enrollments_r, BaseException) else enrollments_r
    if isinstance(db_evidence, BaseException):
        db_evidence = []

    # SCIL v6 §3 workplace channels (supervisor / utility / work sample / peer),
    # EvidenceLog-style rows from the iGOT side, merged with the LMS's own rows.
    if not isinstance(igot_evidence_r, BaseException):
        for row in igot_evidence_r:
            db_evidence.append({
                "comp_id":       row.get("compId"),
                "evidence_type": row.get("evidenceType"),
                "granted_value": row.get("grantedValue"),
                "issue_date":    row.get("issueDate"),
                "source":        row.get("source"),
                "meta":          row.get("meta") or {},
            })

    raw_comps = user.get("competencies") or \
                (user.get("profileDetails") or {}).get("competencies") or []
    seen_ids: set = set()
    comps = []
    for comp in raw_comps:
        cid = comp.get("id", "")
        if cid and cid not in seen_ids:
            seen_ids.add(cid)
            comps.append(comp)

    # Role profiles may use a wider FRAC dictionary than the catalogue is tagged
    # with; map each competency to the catalogue competency that serves it.
    crosswalks = {
        c["id"]: (_rec_engine.crosswalk(c["id"], c.get("name") or "") if _rec_engine else None)
        for c in comps
    }
    aliases = {cid: xw["catalogueId"] for cid, xw in crosswalks.items()
               if xw and xw["catalogueId"] != cid}

    baseline_results = (
        _assembler.compute_for_user(user=user, enrollments=enrollments,
                                    db_evidence=db_evidence, comp_aliases=aliases)
        if _assembler is not None else {}
    )

    office = _ref.offices.get((user.get("jobProfile") or {}).get("officeId") or "")
    gsbpm_subs = _ref.gsbpm.get("competencies", {})

    rows = []
    for comp in comps:
        cid = comp["id"]
        bline = baseline_results.get(cid, {})
        self_reported = _self_reported_level(comp)
        resolved = resolve_level(bline, self_reported)
        catalogue_id = (crosswalks[cid] or {}).get("catalogueId") or cid
        rows.append({
            "competencyId":  cid,
            "name":          (comp.get("name") or "").strip(),
            "type":          comp.get("type", "Functional"),
            "targetLevel":   int(comp.get("requiredLevel") or 3),
            "currentLevel":  resolved["level"],          # None when UNASSESSED
            "confidence":    resolved["confidence"],
            "basis":         resolved["basis"],          # evidence | course_completion | self_report | none
            "evidenceLevel": resolved["evidenceLevel"],
            "rawScore":      float(bline.get("score", 0.0)),
            "evidence":      bline.get("_evidence", {}),
            "channels":      bline.get("channels"),       # SCIL v6 §3 K/A/U/S values (None = absent)
            "completeness":  bline.get("completeness"),
            "peerFeedback":  bline.get("peerFeedback", 0),
            "catalogueId":   (crosswalks[cid] or {}).get("catalogueId"),
            "crosswalk":     crosswalks[cid],                # None → not in catalogue
            # SCIL v6 §4: how much the official's office works in this
            # competency's GSBPM sub-processes this cycle (badge + tie-break only)
            "opportunity":   gsbpm_service.opportunity(office, gsbpm_subs.get(catalogue_id, []),
                                                       _ref.gsbpm, _ref.cycle),
            "lastEvidenceDate": bline.get("lastEvidenceDate"),   # newest dated objective evidence
            "decayClass":    (_rec_engine._frac_map.get(catalogue_id, {}).get("decayClass", "procedural")
                              if _rec_engine else "procedural"),
            # "Why this level": the source that set it, the floors and channels behind it.
            "explanation":   explain_level(bline, resolved, self_reported,
                                           bline.get("completedCourses"), bline.get("practiceRows", 0)),
        })

    # SCIL v6 §2: probabilistic belief with dated decay (assessed) or a cohort
    # prior (UNASSESSED). Needs the workforce snapshot for population / cohort
    # statistics; until it exists the population defaults are used.
    if annotate:
        snap = app_state.snapshot or {}
        population = proficiency_service.population_stats(snap) if snap else {}
        for row in rows:
            row["proficiency"] = proficiency_service.proficiency_state(row, row["decayClass"], population)
            row["coldStartPrior"] = (
                proficiency_service.cohort_prior(user_id, row["catalogueId"] or row["competencyId"],
                                                 snap, population)
                if row["confidence"] == "UNASSESSED" and snap else None
            )

    # evidenceRows: the merged iGOT + LMS evidence, reused by career readiness to score
    # competencies of the NEXT role that are not in the official's current profile.
    return {"user": user, "enrollments": enrollments, "competencies": rows,
            "evidenceRows": db_evidence, "aliases": aliases}


# ─────────────────────────────────────────────────────────────────────────────
# LEARNER ENDPOINTS — by userId (usr_...)
# All data access goes through adapter methods (Adapter pattern / OCP).
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/v1/profile/{user_id}")
async def get_profile_by_user_id(
    user_id: str,
    _current_user: UserAuth = Depends(get_current_user),
):
    """
    Full user profile for the given iGOT userId (usr_...).
    Reads from profileDetails.professionalDetails and profileDetails.competencies.
    """
    from fastapi import HTTPException
    user = await adapter.fetch_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")

    prof = (user.get("profileDetails") or {}).get("professionalDetails") or [{}]
    prof = prof[0] if prof else {}
    competencies = (user.get("profileDetails") or {}).get("competencies") or []

    return {
        "userId":       user.get("userId"),
        "govId":        user.get("govId"),
        "firstName":    user.get("firstName"),
        "lastName":     user.get("lastName"),
        "email":        user.get("email"),
        "designation":  prof.get("designation", "Official"),
        "department":   prof.get("department", "MoSPI"),
        "experienceYears": user.get("experienceYears", 0),
        "competencies": competencies,
    }


@app.get("/api/v1/learner/{user_id}/skill-gaps")
async def get_skill_gaps_by_user_id(
    user_id: str,
    current_user: UserAuth = Depends(get_current_user),
):
    """
    Skill-gap analysis on the 6-term baseline formula — a weighted mean over
    the evidence channels that are actually present (see
    services/competency_service.py):

      b_k = clamp(mean_w(Verified, Documented, Tenure, SelfReport, Education,
                         Seniority) + synergy_k, 0, ConfidenceCeiling_k)

    Evidence sources:
      Verified    — completed iGOT/NSSTA courses, credited at their FRAC tag level
      Documented  — certificates + passed practice assessments (EvidenceLog DB)
      Tenure      — career history from user profile (role-relevant, decayed)
      SelfReport  — EvidenceLog SELF_REPORT rows (0 if not provided)
      Education   — degree relevance to competency type
      Seniority   — designation tier (only for Behavioural; 0 otherwise)

    The displayed level comes from baseline_assembler.resolve_level — the same
    value /recommendations and /pathway use. `basis` says what set it
    (evidence | course_completion | self_report | none); LOW / UNASSESSED
    levels get a diagnostic step first in the learning pathway.
    """
    _ensure_can_view(user_id, current_user)
    from services.baseline_assembler import is_completed

    # ── FRAC type → frontend CompetencyDomain ─────────────────────────────
    _DOMAIN_MAP: dict[str, str] = {
        "Domain":      "Statistical",
        "Functional":  "Governance",
        "Behavioural": "Leadership",
        "Technical":   "Technical",
        "COMPETENCY":  "Statistical",
    }

    state = await _learner_competency_state(user_id)
    user, enrollments, rows = state["user"], state["enrollments"], state["competencies"]

    prof_list = (user.get("profileDetails") or {}).get("professionalDetails") or [{}]
    prof      = prof_list[0] if prof_list else {}

    # Two comps sharing a name but not an id (mock data artifact) get the id
    # appended so the UI shows them as distinct.
    name_counts: dict[str, int] = {}
    for row in rows:
        name_counts[row["name"]] = name_counts.get(row["name"], 0) + 1

    skill_gaps = []
    for row in rows:
        current = row["currentLevel"]
        skill_gaps.append({
            "competencyId":  row["competencyId"],
            "skillName":     row["name"] if name_counts.get(row["name"], 1) == 1
                             else f"{row['name']} ({row['competencyId']})",
            "domain":        _DOMAIN_MAP.get(row["type"], "Governance"),
            "currentLevel":  current,                        # None when UNASSESSED
            "targetLevel":   row["targetLevel"],
            "gapScore":      max(0, row["targetLevel"] - current) if current is not None else None,
            "confidence":    row["confidence"],              # "UNASSESSED" | "LOW" | "MEDIUM" | "HIGH"
            "basis":         row["basis"],
            "evidenceLevel": row["evidenceLevel"],
            "rawScore":      round(row["rawScore"], 3),
            "evidence":      row["evidence"],                # per-channel breakdown dict
            "crosswalk":     row["crosswalk"],               # catalogue competency serving it
            "opportunity":   row["opportunity"],             # Low | Medium | High this cycle (or None)
            "channels":      row["channels"],                # K/A/U/S values, None = no evidence
            "evidenceCompleteness": row["completeness"],     # present / missing channels + weight status
            "peerFeedback":  row["peerFeedback"],            # count only — peer ratings are never scored
            "proficiency":   row.get("proficiency"),         # SCIL v6 §2 θ ~ N(μ, σ²) with dated decay
            "coldStartPrior": row.get("coldStartPrior"),     # UNASSESSED: inferred from role (cohort prior)
            "whyThisLevel":  row["explanation"],             # {summary, basis, factors[], caps[]}
        })

    # Sort: known gaps first (largest gap, lowest score), UNASSESSED last
    skill_gaps.sort(key=lambda g: (
        g["gapScore"] is None,           # False (0) sorts before True (1)
        -(g["gapScore"] or 0),           # larger gap first
        g["rawScore"],                   # lower raw score first within same gap
    ))

    return {
        "userId":           user_id,
        "govId":            user.get("govId", user_id),
        "jobRole":          prof.get("designation", "Official"),
        "department":       prof.get("department", "MoSPI"),
        "totalCourses":     len(enrollments),
        "completedCourses": sum(1 for e in enrollments if is_completed(e)),
        "skillGaps":        skill_gaps,
    }


@app.get("/api/v1/learner/{user_id}/enrollments")
async def get_enrollments_by_user_id(
    user_id: str,
    _current_user: UserAuth = Depends(get_current_user),
):
    """Active/in-progress enrollments for a learner by iGOT userId."""
    raw_enrollments = await adapter.fetch_user_enrollments(user_id)

    enrollments = []
    for i, e in enumerate(raw_enrollments):
        status_int = e.get("status", 0)
        # Show both IN_PROGRESS (1) and COMPLETED (2) courses
        status_label = "Completed" if status_int == 2 else "In Progress" if status_int == 1 else "Not Started"
        leaf = e.get("leafNodesCount", 0) or 1
        progress_pct = e.get("completionPercentage", 0)
        # Hours from the catalogue `duration` (seconds) when the course is known;
        # the old rule (0.5 h per leaf module) only as a fallback.
        catalogue_hrs = _rec_engine.course_hours(e.get("courseId", "")) if _rec_engine else None
        if catalogue_hrs:
            total_hrs     = round(catalogue_hrs, 1)
            remaining_hrs = round(catalogue_hrs * (1 - (progress_pct or 0) / 100.0), 1)
        else:
            done_nodes    = int(leaf * progress_pct / 100) if progress_pct else e.get("progress", 0)
            remaining_hrs = round(max(0, leaf - done_nodes) * 0.5, 1)
            total_hrs     = round(leaf * 0.5, 1)

        enrollments.append({
            "enrollmentId":       f"ENR-{user_id}-{i:03d}",
            "courseId":           e.get("courseId", ""),
            "courseTitle":        e.get("courseName", ""),
            "provider":           e.get("channel", "iGOT Karmayogi"),
            "durationHours":      total_hrs,
            "progressPercentage": progress_pct,
            "remainingHours":     remaining_hrs,
            "lastAccessed":       e.get("enrolledDate", ""),
            "status":             status_label,
        })

    return {"status": "success", "enrollments": enrollments}


@app.get("/api/v1/learner/{user_id}/recommendations")
async def get_recommendations_by_user_id(
    user_id: str,
    current_user: UserAuth = Depends(get_current_user),
):
    """
    Level-gated hybrid recommendations:
      Stage 0 — gap prioritisation (priority_k = gap_k * target_k/5) on the
                resolved levels shared with /skill-gaps; near-equal priorities
                are ordered by how much the official's office uses the
                competency this cycle (SCIL v6 §4 opportunity)
      Stage 1 — FRAC-tag + level filter (current < courseLevel <= target)
      Stage 2 — dense + BM25, RRF fusion, TPAC boost (verified 1.25×, inferred 1.10×),
                optional cross-encoder re-rank of the top 20
      Stage 3 — final = 0.6*relevance + 0.4*quality (Bayesian-shrunk rating, log-pop)
      Picks   — per gap, interleaved by level with formats spread (self-paced /
                classroom / lab) among near-equal courses, then ordered by
                finalScore so the list agrees with the score on every card
    Mandatory ACBP courses (the departmental training plan) are always listed
    first with mandatory=true. Courses the learner thumbed down are skipped
    (mandatory ones excepted). UNASSESSED competencies are not ranked as gaps;
    they are returned under `needsDiagnostic` instead.
    """
    from fastapi import HTTPException
    from services.baseline_assembler import enrollment_course_id, is_completed
    from services.feedback_service import downvoted_ids

    _ensure_can_view(user_id, current_user)
    engine_ = _rec_engine                      # one engine for the whole request (refresh may swap it)
    if engine_ is None:
        raise HTTPException(
            status_code=503,
            detail="Recommendation engine is not available. Check startup logs.",
        )

    async def _cbplan():
        try:
            return await adapter.fetch_user_cbplan(user_id)
        except Exception:
            return None

    state, cbplan, downvoted = await asyncio.gather(
        _learner_competency_state(user_id), _cbplan(), asyncio.to_thread(downvoted_ids, user_id))
    rows = state["competencies"]
    enrolled_ids = {enrollment_course_id(e) for e in state["enrollments"]} - {""}
    completed_ids = {enrollment_course_id(e) for e in state["enrollments"] if is_completed(e)} - {""}

    needs_diagnostic = [
        {"competencyId": r["competencyId"], "competencyName": r["name"]}
        for r in rows if r["currentLevel"] is None
    ]
    gaps = engine_.calculate_gaps(
        baselines  = {r["competencyId"]: float(r["currentLevel"])
                      for r in rows if r["currentLevel"] is not None},
        targets    = {r["competencyId"]: float(r["targetLevel"]) for r in rows},
        names      = {r["competencyId"]: r["name"] for r in rows},
        confidence = {r["competencyId"]: r["confidence"] for r in rows},
        catalogue_ids = {r["competencyId"]: r["catalogueId"] for r in rows if r["catalogueId"]},
    )
    gaps = engine_.order_gaps_by_opportunity(
        gaps, {r["competencyId"]: (r["opportunity"] or {}).get("level") for r in rows})

    # ACBP mandatory courses — always included (completed ones are not repeated).
    mandatory = (cbplan or {}).get("mandatoryCourses") or []
    mandatory_recs = engine_.mandatory_recommendations(
        mandatory, exclude_ids=completed_ids, gaps={g.catalogue_key: g for g in gaps},
        names={(r["catalogueId"] or r["competencyId"]): r["name"] for r in rows},
    )
    mandatory_ids = {r.courseId for r in mandatory_recs}

    recs = engine_.get_recommendations(
        gaps=gaps,
        limit_per_gap=3,
        enrolled_ids=enrolled_ids | mandatory_ids | downvoted,
    ) if gaps else []
    all_recs = mandatory_recs + recs
    for rank, r in enumerate(all_recs, start=1):
        r.priorityRank = rank

    opportunity = {r["competencyId"]: r["opportunity"] for r in rows}
    skill_gaps_payload = [
        {
            "competencyId":   g.competencyId,
            "competencyName": g.competencyName,
            "currentLevel":   g.currentLevel,
            "targetLevel":    g.targetLevel,
            "gapScore":       g.gapScore,
            "priorityScore":  g.priorityScore,
            "confidence":     g.confidence,
            "opportunity":    (opportunity.get(g.competencyId) or {}).get("level"),
        }
        for g in gaps
    ]

    recommendations_payload = [
        {
            "courseId":       r.courseId,
            "title":          r.title,
            "provider":       r.provider,
            "durationHours":  r.durationHours,
            "matchReason":    r.matchReasons[0] if r.matchReasons else "",
            "tags":           r.matchReasons,
            "finalScore":     r.finalScore,
            "relevanceScore": r.relevanceScore,
            "qualityScore":   r.qualityScore,
            "isTpac":         r.isTpac,
            "competencyId":   r.competencyId,
            "competencyName": r.competencyName,
            "priorityRank":   r.priorityRank,
            "matchReasons":   r.matchReasons,
            "matchType":      r.matchType,     # "frac_tag" | "semantic_fallback" | "acbp_mandatory"
            "tpacSource":     r.tpacSource,    # "verified" | "inferred" | "none"
            "courseLevel":    r.courseLevel,   # FRAC level the course is tagged at
            "tagSupported":   r.tagSupported,  # False → tag flagged for review
            "measuredUplift": r.measuredUplift,
            "modality":       r.modality,      # self_paced | virtual_lab | classroom
            "mandatory":      r.mandatory,     # in the official's ACBP → "Mandatory" badge
            "reranked":       r.reranked,      # relevance includes the cross-encoder
            "why":            r.why,           # {gap, levelStep, badges[], summary}
        }
        for r in all_recs
    ]

    return {
        "status":          "success",
        "officialId":      user_id,
        "message":         None if gaps else "No skill gaps detected. Keep learning!",
        "skillGaps":       skill_gaps_payload,
        "recommendations": recommendations_payload,
        "needsDiagnostic": needs_diagnostic,
        "hiddenByFeedback": len(downvoted - mandatory_ids),
        "acbpCycle":       (cbplan or {}).get("cycle"),
    }


@app.get("/api/v1/learner/{user_id}/pathway")
async def get_learning_pathway(
    user_id: str,
    competencyId: str | None = None,
    budgetHours: float | None = Query(default=None, gt=0),
    unbudgeted: bool = False,
    current_user: UserAuth = Depends(get_current_user),
):
    """
    Step-by-step learning paths. For every role competency: one course per
    FRAC level from the official's current level up to the target, lowest
    level first ("first this course, then that one"), with a diagnostic step
    first when the level is unassessed, inferred or self-reported. Plus one
    study plan ordering the rungs of all paths by priority-weighted levels
    gained per hour, never breaking a ladder's level order.

    ?competencyId=… returns only that competency's path (and a plan for it).
    ?budgetHours=… caps the plan; ladders that don't fit are listed under
    studyPlan.deferred. Without it the plan is THIS QUARTER's plan: the budget
    is the official's ACBP learning hours per quarter and classroom hours are
    capped (CLASSROOM_CAP_HOURS_PER_QUARTER). ?unbudgeted=true plans everything.
    APAR-linked mandatory ACBP courses are always included first (SCIL v6 §5).
    """
    from fastapi import HTTPException
    from services.baseline_assembler import enrollment_course_id, is_completed

    _ensure_can_view(user_id, current_user)
    if _rec_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Recommendation engine is not available. Check startup logs.",
        )

    async def _cbplan():
        try:
            return await adapter.fetch_user_cbplan(user_id)
        except Exception:
            return None

    state, cbplan = await asyncio.gather(_learner_competency_state(user_id), _cbplan())
    rows = state["competencies"]
    if competencyId:
        rows = [r for r in rows if r["competencyId"] == competencyId]
        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"Competency '{competencyId}' is not part of this official's role profile.",
            )

    enrollments   = state["enrollments"]
    completed_ids = {enrollment_course_id(e) for e in enrollments if is_completed(e)} - {""}
    in_progress   = {
        enrollment_course_id(e): float(e.get("completionPercentage") or 0)
        for e in enrollments
        if enrollment_course_id(e) and not is_completed(e)
    }

    pathways = [
        _rec_engine.build_pathway(
            comp_id        = r["catalogueId"] or r["competencyId"],
            role_comp_id   = r["competencyId"],
            crosswalk      = r["crosswalk"],
            comp_name      = r["name"],
            current_level  = r["currentLevel"],
            target_level   = r["targetLevel"],
            confidence     = r["confidence"],
            basis          = r["basis"],
            evidence_level = r["evidenceLevel"],
            completed_ids  = completed_ids,
            in_progress    = in_progress,
        )
        for r in rows
    ]
    for p, r in zip(pathways, rows):
        p["opportunity"] = r["opportunity"]

    # ACBP (SCIL v6 §5): mandatory courses + this official's learning hours per quarter.
    mandatory = (cbplan or {}).get("mandatoryCourses") or []
    quarter_hours = (cbplan or {}).get("learningHoursPerQuarter")
    if unbudgeted:
        budget, budget_source, classroom_cap = None, "none", None
    elif budgetHours is not None:
        budget, budget_source, classroom_cap = budgetHours, "query", None
    elif quarter_hours:
        budget, budget_source = float(quarter_hours), "quarterly_hours"
        classroom_cap = CLASSROOM_CAP_HOURS_PER_QUARTER
    else:
        budget, budget_source, classroom_cap = None, "none", None

    # Cross-competency prerequisites (SCIL v6 §5): the official's current level per
    # catalogue competency (None = UNASSESSED → advisory only) and, per step, the
    # expert edges it depends on so the UI can say "needs X Level N first".
    current_levels = {(r["catalogueId"] or r["competencyId"]): r["currentLevel"]
                      for r in state["competencies"]}
    frac_names = {c: m.get("name", c) for c, m in _rec_engine._frac_map.items()}

    mandatory_ids = {m["courseId"] for m in mandatory}
    for p in pathways:
        for s in p["steps"]:
            s["mandatory"] = bool(s.get("course") and s["course"]["courseId"] in mandatory_ids)
            if s["kind"] in ("course", "continue", "stretch", "bridge"):
                s["prerequisites"] = prerequisite_service.step_prerequisites(
                    _ref.prerequisites, p["catalogueCompetencyId"], s["covers"], current_levels, frac_names)

    study_plan = _rec_engine.build_study_plan(
        pathways, budget_hours=budget, mandatory=mandatory if not competencyId else [],
        completed_ids=completed_ids, in_progress=in_progress, classroom_cap_hours=classroom_cap,
        prerequisites=_ref.prerequisites, current_levels=current_levels,
    )
    study_plan["budgetSource"] = budget_source            # quarterly_hours | query | none
    study_plan["learningHoursPerQuarter"] = quarter_hours
    study_plan["acbpCycle"] = (cbplan or {}).get("cycle")
    pathways.sort(key=lambda p: (p["status"] == "met", -p["priorityScore"]))

    return {
        "status":     "success",
        "officialId": user_id,
        "pathways":   pathways,
        "studyPlan":  study_plan,
    }


@app.get("/api/v1/learner/{user_id}/achievements")
async def get_achievements_by_user_id(
    user_id: str,
    _current_user: UserAuth = Depends(get_current_user),
):
    """Completed courses (status=2) treated as achievements."""
    raw_enrollments = await adapter.fetch_user_enrollments(user_id)
    achievements = []
    for i, e in enumerate(raw_enrollments):
        if e.get("status") == 2:
            certs = e.get("issuedCertificates") or []
            achievements.append({
                "id":       certs[0].get("identifier", f"ACH-{i:03d}") if certs else f"ACH-{i:03d}",
                "title":    e.get("courseName", ""),
                "score":    int(e.get("completionPercentage", 100)),
                "date":     e.get("enrolledDate", ""),
                "category": "iGOT Course" if not certs else "Certificate",
            })
    return {"status": "success", "achievements": achievements}


# ─────────────────────────────────────────────────────────────────────────────
# LEARNER ENDPOINTS — legacy by govId (kept for backward compat)
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/v1/admin/users")
async def get_admin_roster(
    _current_user: UserAuth = Depends(require_role("admin")),
):
    """
    Admin Roster: proxies the mock iGOT server's /api/admin/v1/users endpoint.

    Enforces: authenticated + admin role.
    The frontend admin dashboard calls this endpoint (port 8000), NOT the mock
    server directly, keeping the backend as the single auth enforcement point.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{_IGOT_BASE}/api/admin/v1/users",
            headers={"x-authenticated-user-token": _IGOT_TOKEN},
            timeout=15.0,
        )
        resp.raise_for_status()

    # Unwrap the Sunbird envelope — return result.users directly
    data = resp.json()
    return data.get("result", {})


@app.get("/api/v1/admin/frac/competencies")
async def get_frac_competencies(
    _current_user: UserAuth = Depends(require_role("admin")),
):
    """
    FRAC Competency Dictionary: proxies the mock iGOT server's
    /api/frac/competencies endpoint.

    Enforces: authenticated + admin role.
    Returns the unwrapped list: { count, competencies }
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{_IGOT_BASE}/api/frac/competencies",
            headers={"x-authenticated-user-token": _IGOT_TOKEN},
            timeout=15.0,
        )
        resp.raise_for_status()

    data = resp.json()
    return data.get("result", {})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)