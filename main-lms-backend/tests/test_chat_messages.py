"""Catalogue completeness: every language has every template, placeholders are valid, every intent renders."""

import re
import string

import pytest

from ai.semantic_engine import INTENTS
from services.chat_messages import REPLY_INTENTS, VARIANTS, render, templates
from services.chat_messages.context import ReplyContext
from tests.fixtures import COURSE_TITLES, GAP_NAMES, sample_request

# English text that non-English templates may legitimately leave out.
OPTIONAL_FIELDS = {"first_reason"}

SCRIPT = {
    "hi": r"[ऀ-ॿ]", "mr": r"[ऀ-ॿ]", "bn": r"[ঀ-৿]", "gu": r"[઀-૿]",
    "or": r"[଀-୿]", "ta": r"[஀-௿]", "te": r"[ఀ-౿]",
}

_formatter = string.Formatter()


def _fields(template: str) -> set[str]:
    return {name for _, name, _, _ in _formatter.parse(template) if name}


def _alternatives(value) -> list[str]:
    return value if isinstance(value, list) else [value]


def test_every_classifier_intent_has_a_reply():
    assert set(INTENTS) <= REPLY_INTENTS


@pytest.mark.parametrize("variant", VARIANTS)
def test_variant_has_every_english_key(variant):
    assert set(templates("en")) - set(templates(variant)) == set()
    assert set(templates(variant)) - set(templates("en")) == set()


@pytest.mark.parametrize("variant", VARIANTS)
def test_placeholders_match_english(variant):
    english = templates("en")
    for key, value in templates(variant).items():
        allowed = set().union(*(_fields(t) for t in _alternatives(english[key])))
        required = allowed - OPTIONAL_FIELDS
        for template in _alternatives(value):
            assert _fields(template) <= allowed, f"{variant}.{key} uses unknown placeholders"
            assert required <= _fields(template), f"{variant}.{key} drops {required - _fields(template)}"


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("page", ["home", "dashboard"])
def test_every_intent_renders(variant, page):
    ctx = ReplyContext.from_request(sample_request("x", page))
    for intent in sorted(REPLY_INTENTS):
        reply = render(intent, variant, ctx)
        assert reply.strip(), f"{variant}/{page}/{intent} is empty"


@pytest.mark.parametrize("variant", sorted(SCRIPT))
@pytest.mark.parametrize("intent", ["skill_gaps", "recommend", "progress", "profile_stats", "navigation_my_courses"])
def test_regional_reply_is_in_native_script_and_personalised(variant, intent):
    ctx = ReplyContext.from_request(sample_request("x", "dashboard"))
    reply = render(intent, variant, ctx)
    letters = re.findall(r"[^\W\d_]", reply)
    native = re.findall(SCRIPT[variant], reply)
    assert len(native) / len(letters) > 0.4, f"{variant}/{intent} is mostly not in native script"
    if intent == "skill_gaps":
        assert GAP_NAMES[0] in reply
    if intent == "recommend":
        assert COURSE_TITLES[0] in reply
