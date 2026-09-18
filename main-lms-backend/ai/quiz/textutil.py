"""Small text helpers shared by the quiz modules (stdlib + numpy only)."""

from __future__ import annotations

import logging
import math
import re
from collections import Counter
from difflib import SequenceMatcher

import numpy as np

logger = logging.getLogger(__name__)

STOPWORDS = frozenset(
    """a an the and or but if then than of to in on at by for from with without into onto
    is are was were be been being am do does did has have had having it its this that these
    those which who whom whose what when where why how as such also not no nor only own same so
    very can could should would may might must shall will just about above below between both
    each few more most other some any all there their them they he she his her we our you your
    i me my per via within upon over under again further once here while during before after
    according document passage following statement statements""".split()
)

_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[.'][A-Za-z0-9]+)*")
_SENT_RE = re.compile(r"(?<=[.!?])\s+(?=[\"'(\[]?[A-Z0-9])")
_MARKER_RE = re.compile(r"^---\s*(Page|Slide)\s+(\d+)\s*---$", re.MULTILINE)


def normalize(text: str) -> str:
    """Lowercase, unify quotes/dashes, collapse whitespace — for fuzzy comparisons."""
    text = (text or "").lower()
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"[‐-―]", "-", text)
    text = re.sub(r"[^a-z0-9%.\-' ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _stem(word: str) -> str:
    for suffix in ("ies", "es", "s"):
        if len(word) > 4 and word.endswith(suffix):
            return word[: -len(suffix)] + ("y" if suffix == "ies" else "")
    return word


def tokens(text: str) -> list[str]:
    return [_stem(w.lower()) for w in _WORD_RE.findall(text or "")]


def content_tokens(text: str) -> list[str]:
    return [t for t in tokens(text) if t not in STOPWORDS and len(t) > 1]


def numbers(text: str) -> set[str]:
    """Numeric literals, with thousands separators removed (e.g. '2011-12' → {'2011', '12'})."""
    return {n.replace(",", "") for n in re.findall(r"\d[\d,]*(?:\.\d+)?", text or "")}


def quote_coverage(quote: str, source: str) -> float:
    """Fraction of `quote` (normalised chars) found in `source` as matching blocks ≥ 8 chars."""
    q, s = normalize(quote), normalize(source)
    if not q:
        return 0.0
    if q in s:
        return 1.0
    matcher = SequenceMatcher(None, q, s, autojunk=False)
    matched = sum(b.size for b in matcher.get_matching_blocks() if b.size >= 8)
    return matched / len(q)


def token_support(option: str, source: str) -> float:
    """Fraction of the option's content tokens that occur in `source`."""
    opt = content_tokens(option)
    if not opt:
        return 0.0
    src = set(content_tokens(source))
    return sum(1 for t in opt if t in src) / len(opt)


def split_sentences(text: str) -> list[str]:
    """Sentences; a short line without closing punctuation (a heading/title) stays on its own."""
    out: list[str] = []
    for block in re.split(r"\n\s*\n|\n(?=[-•*•]\s)", text or ""):
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        buf: list[str] = []
        for i, ln in enumerate(lines):
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            heading = (
                not buf and len(ln.split()) <= 10 and not re.search(r"[.!?:;,]$", ln)
                and (not nxt or nxt[:1].isupper() or nxt[:1].isdigit())
            )
            if heading:
                out.append(ln)
                continue
            buf.append(ln)
        joined = " ".join(buf)
        if joined:
            out.extend(s.strip() for s in _SENT_RE.split(joined) if s.strip())
    return out


def is_sentence(text: str) -> bool:
    return bool(re.search(r"[.!?]$", text.strip())) and len(text.split()) >= 6


def location_index(full_text: str) -> list[tuple[int, str]]:
    """[(char_offset, 'Page 3'), ...] for extractor page/slide markers."""
    return [(m.start(), f"{m.group(1)} {m.group(2)}") for m in _MARKER_RE.finditer(full_text or "")]


def locate(full_text: str, snippet: str, index: list[tuple[int, str]]) -> str | None:
    if not index:
        return None
    pos = full_text.find(snippet[:80])
    if pos < 0:
        return None
    label = None
    for offset, name in index:
        if offset > pos:
            break
        label = name
    return label


def strip_markers(text: str) -> str:
    return _MARKER_RE.sub(" ", text or "").strip()


# ── Vectors ────────────────────────────────────────────────────────────────────

def tfidf_vectors(texts: list[str]) -> np.ndarray:
    docs = [Counter(content_tokens(t)) for t in texts]
    vocab = sorted({w for d in docs for w in d})
    if not vocab:
        return np.zeros((len(texts), 1), dtype=np.float32)
    col = {w: i for i, w in enumerate(vocab)}
    df = Counter(w for d in docs for w in d)
    mat = np.zeros((len(texts), len(vocab)), dtype=np.float32)
    for r, d in enumerate(docs):
        for w, c in d.items():
            mat[r, col[w]] = (1 + math.log(c)) * math.log((1 + len(docs)) / (1 + df[w]) + 1)
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    return mat / np.clip(norms, 1e-9, None)


def vectorize(texts: list[str]) -> np.ndarray:
    """L2-normalised sentence vectors from the shared catalog embedder; TF-IDF if unavailable."""
    if not texts:
        return np.zeros((0, 1), dtype=np.float32)
    try:
        from ai.embedder import get_embedder

        return np.asarray(get_embedder("catalog").encode(
            texts, kind="passage", normalize_embeddings=True, show_progress_bar=False))
    except Exception as exc:  # embedder missing on this box — lexical vectors still work
        logger.warning("[quiz] embedder unavailable (%s); using TF-IDF vectors.", exc)
        return tfidf_vectors(texts)
