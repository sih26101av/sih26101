"""
FILE: services/media_quiz/relevance.py
─────────────────────────────────────────────────────────────────────────────
Relevance filter (flaw 8): multilingual embedding similarity between each chunk
and the FRAC competency descriptions, instead of a keyword scorer. Uses the
shared "chat" embedder (intfloat/multilingual-e5-small, ai/embedder.py), so it
behaves the same for Hindi and English and does not depend on numbers.

The best-matching competency over the kept chunks also becomes the quiz's
competency_id / skill_name, so a passed media quiz writes evidence against a
real FRAC id instead of the hardcoded "FRAC-STAT-001".
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import numpy as np

from services.media_quiz.evidence import Chunk

logger = logging.getLogger(__name__)

RELEVANCE_FLOOR = float(os.getenv("MEDIA_RELEVANCE_FLOOR", "0.76"))
MAX_CHUNKS = int(os.getenv("MEDIA_MAX_CHUNKS", "12"))
MIN_CHUNKS = 6          # general study videos score low against FRAC but must still yield a quiz

_FRAC_PATH = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "mock-igot-server", "data", "frac_competencies.json"))


@lru_cache(maxsize=1)
def frac_competencies() -> List[Dict[str, str]]:
    try:
        with open(_FRAC_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as exc:
        logger.warning("[relevance] FRAC dictionary unavailable (%s) — relevance filter disabled.", exc)
        return []
    items = data if isinstance(data, list) else next((v for v in data.values() if isinstance(v, list)), [])
    return [{"id": c["id"], "name": c.get("name", ""), "description": c.get("description", "")}
            for c in items if isinstance(c, dict) and c.get("id")]


def score_chunks(chunks: List[Chunk]) -> Tuple[List[Chunk], Dict]:
    """
    Sets chunk.relevance / chunk.competency_id, keeps the MAX_CHUNKS most relevant
    chunks above RELEVANCE_FLOOR (never fewer than MIN_CHUNKS), and returns
    (kept chunks in time order, report).
    """
    comps = frac_competencies()
    report: Dict = {"method": "multilingual-e5 cosine vs FRAC descriptions", "floor": RELEVANCE_FLOOR}
    if not chunks:
        return chunks, report
    if not comps:
        report["method"] = "disabled (no FRAC dictionary)"
        return chunks[:MAX_CHUNKS], report
    try:
        from ai.embedder import encode_cached, get_embedder

        comp_vecs = encode_cached("chat", [f"{c['name']}. {c['description']}" for c in comps], kind="passage")
        chunk_vecs = np.asarray(get_embedder("chat").encode(
            [c.plain[:1500] for c in chunks], kind="query", normalize_embeddings=True, show_progress_bar=False,
        ), dtype="float32")
    except Exception as exc:
        logger.warning("[relevance] embedder unavailable (%s) — keeping chunks unfiltered.", exc)
        report["method"] = f"disabled ({type(exc).__name__})"
        return chunks[:MAX_CHUNKS], report

    sims = chunk_vecs @ comp_vecs.T
    for c, row in zip(chunks, sims):
        j = int(row.argmax())
        c.relevance = float(row[j])
        c.competency_id = comps[j]["id"]

    ranked = sorted(chunks, key=lambda c: c.relevance or 0.0, reverse=True)
    kept = [c for c in ranked if (c.relevance or 0) >= RELEVANCE_FLOOR][:MAX_CHUNKS]
    if len(kept) < MIN_CHUNKS:
        kept = ranked[:max(MIN_CHUNKS, len(kept))]
    kept_ids = {c.id for c in kept}

    votes: Dict[str, float] = {}
    for c in kept:
        votes[c.competency_id] = votes.get(c.competency_id, 0.0) + (c.relevance or 0.0)
    best_id = max(votes, key=votes.get) if votes else None
    off_topic = (ranked[0].relevance or 0.0) < RELEVANCE_FLOOR
    if off_topic:
        best_id = None          # a general study video: don't tag it with an unrelated FRAC competency
    best = next((c for c in comps if c["id"] == best_id), None)

    report.update({
        "chunks_scored": len(chunks),
        "chunks_kept": len(kept),
        "dropped_as_irrelevant": [c.id for c in chunks if c.id not in kept_ids],
        "top_score": round(ranked[0].relevance or 0.0, 3),
        "off_topic": off_topic,
        "competency_id": best_id,
        "competency_name": best["name"] if best else None,
    })
    return sorted(kept, key=lambda c: c.t_start), report


def competency_name(comp_id: Optional[str]) -> Optional[str]:
    return next((c["name"] for c in frac_competencies() if c["id"] == comp_id), None)
