"""Detect website theme / language changes requested in any supported chat language.

Only consulted after the classifier returns `ui_action_request`, so a message
merely mentioning "Hindi" or "dark" elsewhere never triggers an action.
Matching is by substring so inflected forms ("हिंदीत", "இந்தியில்") still match.
"""

from __future__ import annotations

from typing import Optional

_HINDI = ("hindi", "हिंदी", "हिन्दी", "হিন্দি", "હિન્દી", "ହିନ୍ଦୀ", "இந்தி", "హిందీ")
_ENGLISH = ("english", "अंग्रेज़ी", "अंग्रेजी", "इंग्रजी", "ইংরেজি", "અંગ્રેજી", "ଇଂରାଜୀ", "ஆங்கில", "ఇంగ్లీష్")
_DARK = ("dark", "डार्क", "गहर", "गडद", "ডার্ক", "গাঢ়", "ડાર્ક", "ઘેરી", "ଡାର୍କ", "ଗାଢ଼", "டார்க்", "இருண்ட", "డార్క్", "ముదురు")
_LIGHT = ("light", "लाइट", "লাইট", "લાઇટ", "ଲାଇଟ", "லைட்", "లైట్")
_THEME = ("theme", "colour", "color", "थीम", "रंग", "থিম", "রঙ", "થીમ", "રંગ", "ଥିମ", "ରଙ୍ଗ", "தீம", "வண்ண", "థీమ్", "రంగు")


def _mentions(text: str, words: tuple[str, ...]) -> bool:
    return any(word in text for word in words)


def detect_ui_actions(message: str) -> tuple[Optional[str], Optional[str]]:
    """Returns (theme, language): theme in {"dark", "light", "toggle"}, language in {"hi", "en"}; None when absent."""
    text = message.lower()

    language = "hi" if _mentions(text, _HINDI) else "en" if _mentions(text, _ENGLISH) else None

    if _mentions(text, _DARK):
        theme = "dark"
    elif _mentions(text, _LIGHT):
        theme = "light"
    elif _mentions(text, _THEME):
        theme = "toggle"
    else:
        theme = None
    return theme, language
