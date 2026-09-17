"""Small, offline language routing for Gyan chat.

This deliberately does *not* use a generative model. Most Indian scripts map
unambiguously to one supported language, so Unicode-script routing is both
faster and more reliable than downloading another transformer. ``langdetect``
is only used for the Devanagari ambiguity (primarily Hindi vs Marathi).
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

SUPPORTED_CHAT_LANGUAGES = frozenset({"en", "hi", "bn", "mr", "gu", "or", "ta", "te"})

# These scripts identify one of the languages that Gyan currently has reply
# templates for. Devanagari is handled separately because Hindi and Marathi
# share it.
_SCRIPT_LANGUAGE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"[\u0980-\u09FF]"), "bn"),  # Bengali
    (re.compile(r"[\u0A80-\u0AFF]"), "gu"),  # Gujarati
    (re.compile(r"[\u0B00-\u0B7F]"), "or"),  # Odia
    (re.compile(r"[\u0B80-\u0BFF]"), "ta"),  # Tamil
    (re.compile(r"[\u0C00-\u0C7F]"), "te"),  # Telugu
)
_DEVANAGARI = re.compile(r"[\u0900-\u097F]")
# Romanized Hindi marker words. Deliberately excludes tokens that are also
# common English words ("do", "ho", "to", "me", "par").
_HINGLISH_WORDS = {
    "kya", "kaun", "kaunsa", "kaunse", "kaise", "kaisa", "kaisi", "mujhe", "mera", "meri", "mere",
    "mein", "hai", "hain", "hoon", "tha", "thi", "hua", "nahi", "nahin", "batao", "bolo", "karo",
    "karna", "karu", "karun", "karein", "lena", "chahiye", "acha", "accha", "achha", "theek",
    "samjhao", "kab", "kahan", "kyun", "kitna", "kitne", "kitni", "sikho", "padhna", "padhu",
    "seekhna", "seekhun", "dikhao", "kholo", "badlo", "banao", "jao", "chalo", "aap", "tum",
    "apna", "apne", "baare", "kuch", "sab", "bahut", "shukriya", "dhanyavad", "alvida", "haal",
    "wala", "wali", "raha", "rahi", "abhi", "yaar", "maine", "kisne", "gaya", "lag", "bhi",
    "mann", "ka", "ke", "ki", "ko", "se", "ji", "namaste", "namaskar", "pranam",
}


def _devanagari_language(text: str) -> str:
    try:
        from langdetect import DetectorFactory, LangDetectException, detect
    except ImportError:
        logger.warning("langdetect is not installed; treating Devanagari input as Hindi.")
        return "hi"

    DetectorFactory.seed = 0
    try:
        language = detect(text)
    except LangDetectException:
        return "hi"
    return language if language in {"hi", "mr"} else "hi"


def detect_chat_variant(text: str) -> str:
    """Internal language variant: en, hi (Devanagari), hi_latn (romanized Hindi), mr, bn, gu, or, ta, te.

    Replies mirror the user's script, so Devanagari and romanized Hindi are
    distinct variants even though both are ISO "hi".
    """
    for pattern, language in _SCRIPT_LANGUAGE_PATTERNS:
        if pattern.search(text):
            return language

    if _DEVANAGARI.search(text):
        return _devanagari_language(text)

    words = set(re.findall(r"[a-zA-Z]+", text.lower()))
    if words & _HINGLISH_WORDS:
        return "hi_latn"

    return "en"


def to_iso(variant: str) -> str:
    return "hi" if variant == "hi_latn" else variant


def detect_chat_language(text: str) -> str:
    """Supported ISO 639-1 code for a chat message."""
    return to_iso(detect_chat_variant(text))
