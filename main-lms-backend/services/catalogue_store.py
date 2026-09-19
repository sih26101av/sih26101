"""
services/catalogue_store.py — course embeddings persisted in the database

The recommendation engine's course vectors are saved to `courses`
(models.Course): `syllabusVectorEmbedding` holds the float32 vector as base64,
`embeddingModelVersion` holds "<model name>|<text hash>". On startup and on
each catalogue refresh the engine reuses a stored vector when both the model
and the course's title + description hash still match, and encodes only the
rest (ai.embedder.encode_cached still memoises those on local disk).

Why the DB as well as the disk cache: the disk cache lives on one machine and is
lost on a fresh deploy; the shared Neon database survives both, so a new
instance starts without re-embedding the catalogue.

All functions are synchronous (run them with asyncio.to_thread) and never
raise: a DB problem only means the vectors are recomputed.
"""
from __future__ import annotations

import base64
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

_SOURCE = "igot_catalogue"


def _encode_vec(vec: np.ndarray) -> str:
    return base64.b64encode(np.asarray(vec, dtype="<f4").tobytes()).decode("ascii")


def _decode_vec(raw: str) -> np.ndarray:
    return np.frombuffer(base64.b64decode(raw), dtype="<f4").copy()


def load_embeddings(model: str) -> Dict[str, Tuple[str, np.ndarray]]:
    """{courseId: (text_hash, vector)} for vectors stored under `model`; {} on any error."""
    from auth.database import session_scope
    from models.models import Course
    out: Dict[str, Tuple[str, np.ndarray]] = {}
    try:
        with session_scope() as db:
            for row in db.query(Course).filter(Course.source == _SOURCE).all():
                ver = row.embeddingModelVersion or ""
                name, _, digest = ver.rpartition("|")
                if name == model and digest and row.syllabusVectorEmbedding:
                    out[row.courseId] = (digest, _decode_vec(row.syllabusVectorEmbedding))
    except Exception as exc:
        logger.warning("[catalogue-store] could not read stored embeddings (%s) — encoding instead.", exc)
        return {}
    return out


def save_embeddings(model: str, items: List[Tuple[str, str, np.ndarray]],
                    known: Optional[Dict[str, Tuple[str, np.ndarray]]] = None) -> int:
    """
    Upsert (courseId, text_hash, vector) rows; rows already stored with the same
    model + hash are skipped. Returns how many rows were written.
    """
    from auth.database import session_scope
    from models.models import Course
    known = known or {}
    todo = [(cid, h, v) for cid, h, v in items if known.get(cid, ("",))[0] != h]
    if not todo:
        return 0
    try:
        with session_scope() as db:
            existing = {c.courseId: c for c in
                        db.query(Course).filter(Course.courseId.in_([cid for cid, _, _ in todo])).all()}
            for cid, h, vec in todo:
                row = existing.get(cid) or Course(courseId=cid, source=_SOURCE)
                row.source = _SOURCE
                row.syllabusVectorEmbedding = _encode_vec(vec)
                row.embeddingModelVersion = f"{model}|{h}"
                db.add(row)
            db.commit()
        return len(todo)
    except Exception as exc:
        logger.warning("[catalogue-store] could not save embeddings (%s).", exc)
        return 0


def catalogue_fingerprint(catalog: List[Dict[str, Any]], frac: Optional[List[Dict[str, Any]]] = None) -> str:
    """Hash of the catalogue + FRAC set as served — a changed hash triggers an engine rebuild."""
    payload = json.dumps([catalog or [], frac or []], sort_keys=True, default=str)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()
