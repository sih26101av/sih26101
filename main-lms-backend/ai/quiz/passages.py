"""
Pick the passages a quiz is built from.

Instead of "the first 20 chunks", chunks are scored for how much testable
content they hold (definitions, figures, named terms), boilerplate (tables of
contents, references, headers) is dropped, and MMR over sentence vectors picks
a diverse set so the quiz covers the whole document. Only these passages are
sent to an LLM, which keeps each request well inside Groq's per-minute token cap.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np

from ai.quiz import textutil as tu

_DEFINITION_CUES = re.compile(
    r"\b(is defined as|are defined as|refers to|refer to|is known as|are known as|is called|are called|"
    r"means|is the|are the|consists of|comprises|is used to|is computed|is calculated|is measured|"
    r"is compiled|is estimated|formula|ratio|index|method|approach)\b",
    re.I,
)
_TOC_LINE = re.compile(r"(\.{3,}|…{2,}|\s{2,})\s*\d{1,4}\s*$")
_REFERENCE_CUES = re.compile(r"\b(references|bibliography|et al\.|doi:|isbn|https?://|www\.)", re.I)
_ACRONYM = re.compile(r"\b[A-Z]{2,6}s?\b")

MIN_PASSAGE_CHARS = 180


@dataclass
class Passage:
    id: str
    text: str
    order: int  # position in the document, for stable ordering
    location: str | None = None
    score: float = 0.0


def clean_passage(chunk: str) -> str:
    """Drop page markers, table-of-contents lines and bibliography lines from a chunk."""
    kept = []
    for ln in tu.strip_markers(chunk).splitlines():
        s = ln.strip()
        if _TOC_LINE.search(s) or (_REFERENCE_CUES.search(s) and len(s) < 200) or re.fullmatch(r"(contents|references|bibliography)", s, re.I):
            continue
        kept.append(ln)
    return "\n".join(kept).strip()


def informativeness(chunk: str) -> float:
    """Heuristic 0..~1 score of how much examinable content a (cleaned) chunk contains."""
    body = clean_passage(chunk)
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    if not lines:
        return 0.0
    alpha = sum(c.isalpha() for c in body) / max(len(body), 1)
    short_ratio = sum(len(ln) < 30 for ln in lines) / len(lines)
    sentences = [s for s in tu.split_sentences(body) if 40 <= len(s) <= 400 and tu.is_sentence(s)]

    if len(body) < MIN_PASSAGE_CHARS or alpha < 0.55 or not sentences:
        return 0.0

    score = (
        0.35 * min(len(sentences) / 5, 1.0)
        + 0.25 * min(len(_DEFINITION_CUES.findall(body)) / 4, 1.0)
        + 0.15 * min(len(tu.numbers(body)) / 4, 1.0)
        + 0.15 * min(len(set(_ACRONYM.findall(body))) / 3, 1.0)
        + 0.10 * alpha
    )
    return max(0.0, score - 0.4 * short_ratio)


def select_passages(full_text: str, chunks: list[str], k: int = 8, mmr_lambda: float = 0.65) -> list[Passage]:
    """Return up to k diverse, informative passages labelled P1..Pk in document order."""
    if not chunks:
        return []
    index = tu.location_index(full_text)
    scored = [(i, c, informativeness(c)) for i, c in enumerate(chunks)]
    pool = [(i, c, s) for i, c, s in scored if s > 0]
    if not pool:
        return []

    vecs = tu.vectorize([clean_passage(c) for _, c, _ in pool])
    rel = np.array([s for _, _, s in pool], dtype=np.float32)
    rel = rel / max(float(rel.max()), 1e-9)

    chosen: list[int] = []
    remaining = list(range(len(pool)))
    while remaining and len(chosen) < k:
        if chosen:
            sim = vecs[remaining] @ vecs[chosen].T
            redundancy = sim.max(axis=1)
        else:
            redundancy = np.zeros(len(remaining), dtype=np.float32)
        mmr = mmr_lambda * rel[remaining] - (1 - mmr_lambda) * redundancy
        best = remaining[int(np.argmax(mmr))]
        chosen.append(best)
        remaining.remove(best)

    picked = sorted((pool[j] for j in chosen), key=lambda t: t[0])
    return [
        Passage(
            id=f"P{n}",
            text=clean_passage(chunk),
            order=i,
            location=tu.locate(full_text, chunk, index),
            score=round(s, 3),
        )
        for n, (i, chunk, s) in enumerate(picked, start=1)
    ]
