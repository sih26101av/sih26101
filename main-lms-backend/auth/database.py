"""
auth/database.py
─────────────────────────────────────────────────────────────────────────────
SQLAlchemy engine + session factory for the auth-only SQLite database.

Intentionally separate from the future domain DB (models/models.py) so the
two concerns never share a connection pool or migration surface.

The database file is created as:
  main-lms-backend/auth.db   (relative to wherever uvicorn is launched from)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ── Database path ──────────────────────────────────────────────────────────────
# Resolve relative to this file so it always lands inside main-lms-backend/
_HERE = os.path.dirname(os.path.abspath(__file__))
_DB_PATH = os.path.join(_HERE, "..", "auth.db")

DATABASE_URL = f"sqlite:///{os.path.normpath(_DB_PATH)}"

# ── Engine ─────────────────────────────────────────────────────────────────────
# check_same_thread=False is required for SQLite + FastAPI's async request handling
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# ── Session factory ────────────────────────────────────────────────────────────
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── Declarative base (only for auth models) ────────────────────────────────────
AuthBase = declarative_base()


# ── FastAPI dependency ─────────────────────────────────────────────────────────
def get_db():
    """Yields a database session and ensures it is closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
