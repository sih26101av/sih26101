"""
auth/database.py
─────────────────────────────────────────────────────────────────────────────
SQLAlchemy engine + session factory for the auth / evidence / karma database.

Intentionally separate from the future domain DB (models/models.py) so the
two concerns never share a connection pool or migration surface.

Where the data lives
────────────────────
- DATABASE_URL set (main-lms-backend/.env) → shared Neon Postgres. This is the
  normal setup: every teammate and every deployment sees the same users,
  passwords, evidence and karma rows.
- DATABASE_URL unset → local SQLite file main-lms-backend/auth.db (offline
  fallback; credentials then exist on this machine only).

The URL carries the DB password — it must only ever live in .env, never in code
or logs.
"""

import logging
import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

log = logging.getLogger(__name__)

_HERE = os.path.dirname(os.path.abspath(__file__))
_BACKEND_ROOT = os.path.normpath(os.path.join(_HERE, ".."))

# Load main-lms-backend/.env regardless of the cwd uvicorn / seed is launched from.
load_dotenv(os.path.join(_BACKEND_ROOT, ".env"))


def _resolve_database_url() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        return f"sqlite:///{os.path.join(_BACKEND_ROOT, 'auth.db')}"
    # Neon / Heroku style "postgres://" is not accepted by SQLAlchemy 2.x.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg2://" + url[len("postgresql://"):]
    return url


DATABASE_URL = _resolve_database_url()
IS_SQLITE = DATABASE_URL.startswith("sqlite")

# ── Engine ─────────────────────────────────────────────────────────────────────
if IS_SQLITE:
    # check_same_thread=False is required for SQLite + FastAPI's threadpool
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    log.warning("DATABASE_URL not set — using local SQLite auth.db (credentials are per-machine).")
else:
    connect_args = {}
    if "sslmode=" not in DATABASE_URL:
        connect_args["sslmode"] = "require"   # never talk to a remote DB in cleartext
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        # Neon suspends idle compute and drops connections; ping before use and
        # recycle well inside its idle window so requests never get a dead socket.
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=5,
        echo=False,
    )
    log.info("Using shared Postgres database at %s", engine.url.render_as_string(hide_password=True))

# ── Session factory ────────────────────────────────────────────────────────────
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── Declarative base (only for auth models) ────────────────────────────────────
AuthBase = declarative_base()


# ── FastAPI dependency ─────────────────────────────────────────────────────────
def get_db():
    """FastAPI dependency — `db: Session = Depends(get_db)`; closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# The same session lifecycle for code that is not a route (worker threads, background
# snapshot builds): `with session_scope() as db: ...`. Routes use Depends(get_db).
session_scope = contextmanager(get_db)
