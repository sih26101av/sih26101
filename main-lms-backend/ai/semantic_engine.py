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
import re
from collections import Counter
from difflib import get_close_matches
from typing import Optional

import numpy as np

from ai.embedder import get_embedder, is_embedder_ready, model_name

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

# Winning scores below this mean "nothing here really matches" and the query is
# answered with "I don't know" rather than the nearest-but-unrelated intent.
# Similarity scales differ per model: e5 scores cluster in 0.85–1.00. Measured on
# tests/data/gibberish_eval.json vs the held-out benchmark, 0.89 rejects 98% of
# nonsense and costs 6 of 906 real queries; 0.87 rejected only 85% of nonsense.
_LOW_CONFIDENCE = {
    "intfloat/multilingual-e5-small": 0.89,
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": 0.50,
}


def low_confidence_threshold() -> float:
    return _LOW_CONFIDENCE.get(model_name("chat"), 0.0)

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


# ── Typo correction ───────────────────────────────────────────────────────────
# Tuned on tests/data/typo_eval.json: these values give ~90% intent accuracy on
# misspelled queries with no loss on the held-out benchmark. Correcting against a
# small hand-written word list (the previous approach) scored *worse than no
# correction at all* — it snapped unknown words onto the nearest of ~50 entries,
# so "helo" became "help" (→ Contact section) and "goodby" became "good".
_TYPO_MIN_LENGTH = 4      # shorter tokens have too many equally-close neighbours
_TYPO_CUTOFF = 0.85       # difflib ratio; below ~0.8 real words get rewritten
_PUNCTUATION = ".,!?;:'\"()[]{}"

# Texting shorthand is too short for fuzzy matching ("r" is one edit from a dozen
# words), so the unambiguous ones are expanded from an explicit table instead.
_SHORTHAND = {
    "u": "you", "ur": "your", "urs": "yours", "r": "are", "n": "and",
    "pls": "please", "plz": "please", "thx": "thanks", "thnx": "thanks", "ty": "thanks",
    "abt": "about", "b4": "before", "bcoz": "because", "bcz": "because", "coz": "because",
    "wat": "what", "wut": "what", "wht": "what", "hw": "how",
    "info": "information", "msg": "message",
}


def _build_vocabulary() -> frozenset[str]:
    """Every word used in a Latin-script prototype — the vocabulary Gyan must understand."""
    words: set[str] = set()
    for per_language in INTENT_CORPUS.values():
        for language in LATIN_LANGUAGES:
            for phrase in per_language.get(language, []):
                words.update(w for w in re.findall(r"[a-z]+", phrase.lower()) if len(w) >= 3)
    return frozenset(words)


VOCABULARY = _build_vocabulary()


def _correct_tokens(query: str) -> str:
    """Repair typos in Latin-script queries ("dasboard" -> "dashboard", "helo" -> "hello").

    Words already in the vocabulary are never rewritten, so valid input passes through.
    """
    corrected = []
    for token in query.lower().split():
        word = token.strip(_PUNCTUATION)
        if word in _SHORTHAND:
            corrected.append(_SHORTHAND[word])
        elif len(word) >= _TYPO_MIN_LENGTH and word.isalpha() and word not in VOCABULARY:
            match = get_close_matches(word, VOCABULARY, n=1, cutoff=_TYPO_CUTOFF)
            corrected.append(match[0] if match else token)
        else:
            corrected.append(token)
    return " ".join(corrected)

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
        _prototype_vecs = get_embedder("chat").encode(
            _PROTOTYPE_SENTENCES,
            normalize_embeddings=True,
            batch_size=64,
            show_progress_bar=False,
        )
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
    """Returns (intent, confidence) — a final decision the caller can render directly.

    A query that matches nothing well enough comes back as "out_of_scope" rather than
    the nearest unrelated intent, so random input gets "I don't know" instead of a
    confident wrong answer. ("general", 0.0) means the embedder is unavailable.
    """
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
    confidence = scores[best_intent]
    if confidence < low_confidence_threshold():
        logger.debug(
            "[SemanticEngine] query=%r lang=%s best=%s confidence=%.3f below threshold — out_of_scope",
            query, lang, best_intent, confidence,
        )
        return "out_of_scope", confidence

    logger.debug(
        "[SemanticEngine] query=%r lang=%s intent=%s confidence=%.3f",
        query, lang, best_intent, confidence,
    )
    return best_intent, confidence


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
