"""
FILE: ai/semantic_engine.py
─────────────────────────────────────────────────────────────────────────────
Gyan — Semantic Intent Engine (multilingual)
MoSPI Skill Intelligence Platform | SIH 2026

  classify_intent(query, lang) -> (intent, confidence)
    • Prototype phrases live in ai/intent_corpus/<lang>.json (one file per
      language so native speakers can review their own language in isolation).
    • The query is compared only against prototypes in its own language pool
      (e.g. Bengali + English). With a complete corpus this measures the same
      as a global search; it guards against a language whose prototypes cover
      only a few intents pulling every query in that script towards them.
    • Each intent scores the mean of its top-k prototype similarities. k=1
      (nearest neighbour) measured best on scripts/eval_intents.py; averaging
      more neighbours lost ~4 points of macro accuracy.

  vectorize_profile(skill_gaps) -> dict of numeric profile features
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import logging
import os
from collections import Counter
from difflib import get_close_matches
from typing import Optional

import numpy as np

from ai.embedder import encode_cached, get_embedder, is_embedder_ready, model_name

logger = logging.getLogger(__name__)

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "intent_corpus")
CORPUS_LANGUAGES = ("en", "hi_latn", "hi", "mr", "bn", "gu", "or", "ta", "te")

# Devanagari Hindi/Marathi share a pool because langdetect often confuses them
# on short text; Latin English/Hinglish share one because detection between
# them rests on a small marker-word list.
LANGUAGE_POOLS: dict[str, tuple[str, ...]] = {
    "en": ("en", "hi_latn"),
    "hi_latn": ("hi_latn", "en"),
    "hi": ("hi", "mr", "en"),
    "mr": ("mr", "hi", "en"),
    "bn": ("bn", "en"),
    "gu": ("gu", "en"),
    "or": ("or", "en"),
    "ta": ("ta", "en"),
    "te": ("te", "en"),
}
LATIN_LANGUAGES = frozenset({"en", "hi_latn"})
TOP_K = 1

# Winning scores below this are treated as "not understood". Similarity scales
# differ per model: e5 scores cluster in 0.85–0.97. 0.87 sits below ~99% of
# held-out in-scope queries and above keyboard-mash input (scripts/eval_intents.py).
_LOW_CONFIDENCE = {
    "intfloat/multilingual-e5-small": 0.87,
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": 0.50,
}


def low_confidence_threshold() -> float:
    return _LOW_CONFIDENCE.get(model_name("chat"), 0.0)

_NAV_VOCAB = [
    "dashboard", "skill", "gap", "gaps", "competency", "competencies",
    "course", "courses", "enroll", "enrollment", "my courses", "active",
    "progress", "achievement", "achievements", "radar", "chart",
    "quiz", "assessment", "upload", "pdf", "generate", "ai generator",
    "profile", "header", "mandatory", "statistics", "analysis",
    "recommend", "recommendation", "pathway", "learning",
    "navigate", "how", "where", "help", "find", "access", "open", "go to",
    "tab", "section", "button", "panel",
    "great", "thanks", "good", "bye", "yes", "okay",
]


def _correct_tokens(query: str) -> str:
    """Fuzzy-correct English UI vocabulary typos ('dasboard' -> 'dashboard')."""
    corrected = []
    for tok in query.lower().split():
        if len(tok) >= 3:
            match = get_close_matches(tok, _NAV_VOCAB, n=1, cutoff=0.75)
            corrected.append(match[0] if match else tok)
        else:
            corrected.append(tok)
    return " ".join(corrected)


def load_corpus() -> dict[str, dict[str, list[str]]]:
    """Returns {intent: {lang: [phrases]}}."""
    corpus: dict[str, dict[str, list[str]]] = {}
    for lang in CORPUS_LANGUAGES:
        with open(os.path.join(CORPUS_DIR, f"{lang}.json"), encoding="utf-8") as f:
            for intent, phrases in json.load(f).items():
                corpus.setdefault(intent, {})[lang] = phrases
    return corpus


INTENT_CORPUS = load_corpus()
INTENTS: tuple[str, ...] = tuple(sorted(INTENT_CORPUS))

_INTENT_LABELS: list[str] = []
_PROTOTYPE_SENTENCES: list[str] = []
_PROTOTYPE_LANGS: list[str] = []
for _intent in INTENTS:
    for _lang, _phrases in INTENT_CORPUS[_intent].items():
        for _phrase in _phrases:
            _INTENT_LABELS.append(_intent)
            _PROTOTYPE_SENTENCES.append(_phrase)
            _PROTOTYPE_LANGS.append(_lang)

_LABELS_ARR = np.array(_INTENT_LABELS)
_LANGS_ARR = np.array(_PROTOTYPE_LANGS)

_prototype_vecs: Optional[np.ndarray] = None


def _ensure_prototypes() -> None:
    """Encode all prototype phrases once, via the shared singleton embedder."""
    global _prototype_vecs
    if _prototype_vecs is not None:
        return
    try:
        logger.info(
            "[SemanticEngine] Encoding %d prototypes (%d intents, %d languages)…",
            len(_PROTOTYPE_SENTENCES), len(INTENTS), len(CORPUS_LANGUAGES),
        )
        # Memoised on disk; the model is loaded regardless since queries are encoded live.
        _prototype_vecs = encode_cached("chat", _PROTOTYPE_SENTENCES, kind="query", embedder=get_embedder("chat"))
        logger.info("[SemanticEngine] Intent prototypes ready.")
    except Exception as exc:
        logger.warning("[SemanticEngine] Could not encode prototypes: %s", exc)
        _prototype_vecs = None


def is_semantic_engine_ready() -> bool:
    return is_embedder_ready("chat") and _prototype_vecs is not None


def score_intents(query: str, lang: str, top_k: int = TOP_K) -> dict[str, float]:
    """Per-intent confidence for `query`, searched within `lang`'s pool only."""
    _ensure_prototypes()
    if _prototype_vecs is None:
        return {}

    text = _correct_tokens(query) if lang in LATIN_LANGUAGES else query
    query_vec = get_embedder("chat").encode(text, normalize_embeddings=True, show_progress_bar=False)
    if query_vec.ndim == 2:
        query_vec = query_vec[0]

    pool = LANGUAGE_POOLS.get(lang, ("en",))
    in_pool = np.isin(_LANGS_ARR, pool)
    sims = _prototype_vecs @ query_vec

    scores: dict[str, float] = {}
    for intent in INTENTS:
        intent_sims = sims[in_pool & (_LABELS_ARR == intent)]
        if intent_sims.size:
            k = min(top_k, intent_sims.size)
            scores[intent] = float(np.sort(intent_sims)[-k:].mean())
    return scores


def classify_intent(query: str, lang: Optional[str] = None) -> tuple[str, float]:
    """Returns (best_intent, confidence). ("general", 0.0) if the embedder is unavailable."""
    if lang is None:
        from services.language_service import detect_chat_variant
        lang = detect_chat_variant(query)
    try:
        scores = score_intents(query, lang)
    except Exception as exc:
        logger.warning("[SemanticEngine] classification failed: %s", exc)
        return "general", 0.0
    if not scores:
        return "general", 0.0

    best_intent = max(scores, key=scores.get)
    logger.debug(
        "[SemanticEngine] query=%r lang=%s intent=%s confidence=%.3f",
        query, lang, best_intent, scores[best_intent],
    )
    return best_intent, scores[best_intent]


def vectorize_profile(skill_gaps: list[dict]) -> dict:
    """
    Flat numeric profile features from skill-gap dicts
    ({skillName, domain, currentLevel, targetLevel, gapScore}).
    """
    active = [g for g in skill_gaps if g.get("gapScore", 0) > 0]
    total = len(skill_gaps)
    met = total - len(active)
    completion_pct = round((met / max(total, 1)) * 100)

    avg_gap = (
        sum(g.get("gapScore", 0) for g in active) / len(active)
        if active else 0.0
    )
    max_gap = max((g.get("gapScore", 0) for g in active), default=0)

    domain_counts: Counter = Counter(g.get("domain", "Unknown") for g in active)
    top_domain = domain_counts.most_common(1)[0][0] if domain_counts else "None"

    if completion_pct >= 70:
        tier = "on_track"
    elif completion_pct >= 40:
        tier = "needs_focus"
    else:
        tier = "critical"

    return {
        "total_competencies": total,
        "gaps_count": len(active),
        "met_count": met,
        "completion_pct": completion_pct,
        "avg_gap_score": round(avg_gap, 1),
        "max_gap": max_gap,
        "top_domain": top_domain,
        "domain_breakdown": dict(domain_counts),
        "tier": tier,
    }
