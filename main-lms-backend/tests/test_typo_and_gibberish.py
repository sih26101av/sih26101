"""Gyan must tolerate misspellings and must refuse to invent answers for random input.

Rates are asserted in aggregate (not per case) so a small corpus or model change
doesn't break the suite, while a real regression still fails it. Measured with
`python scripts/eval_intents.py --robustness`.
"""

import functools
import json
import os

import pytest

from ai.semantic_engine import _correct_tokens, classify_intent
from services.language_service import detect_chat_variant

DATA = os.path.join(os.path.dirname(__file__), "data")
TYPOS = json.load(open(os.path.join(DATA, "typo_eval.json"), encoding="utf-8"))
GIBBERISH = json.load(open(os.path.join(DATA, "gibberish_eval.json"), encoding="utf-8"))

MIN_TYPO_ACCURACY = 0.85          # measured 90%
MIN_GIBBERISH_REJECTION = 0.93    # measured 98%


@functools.lru_cache(maxsize=None)
def _classify(query: str) -> str:
    """Cached: every embedding call costs ~50ms and the assertions re-check queries."""
    return classify_intent(query, detect_chat_variant(query))[0]


@pytest.mark.parametrize("word,expected", [
    ("helo", "hello"),
    ("goodby", "goodbye"),
    ("skil", "skill"),
    ("corse", "course"),
    ("dashbord", "dashboard"),
    ("achievments", "achievements"),
    ("recomend", "recommend"),
])
def test_common_misspellings_are_repaired(word, expected):
    assert _correct_tokens(word) == expected


@pytest.mark.parametrize("phrase", [
    "what are my skill gaps",
    "show my progress",
    "recommend a course",
    "open the dashboard",
])
def test_correctly_spelled_input_is_left_alone(phrase):
    assert _correct_tokens(phrase) == phrase


def test_typo_accuracy():
    """Misspelled queries still reach the right intent."""
    correct = [c for c in TYPOS if _classify(c["query"]) == c["intent"]]
    accuracy = len(correct) / len(TYPOS)
    missed = [(c["query"], _classify(c["query"]), c["intent"]) for c in TYPOS if c not in correct]
    assert accuracy >= MIN_TYPO_ACCURACY, f"typo accuracy {accuracy:.0%}; missed {missed}"


def test_typos_never_produce_a_wildly_unrelated_answer():
    """A typo may cost precision, but must not silently pick an unrelated intent.

    Anything not matched confidently has to come back as out_of_scope ("I don't know").
    """
    unrelated = {
        "helo": {"greeting"}, "byee": {"farewell"}, "goodby": {"farewell"},
        "thnaks": {"gratitude"}, "shw my progres": {"progress", "navigation_progress"},
        "wheres the dashbord": {"navigation_dashboard"},
    }
    for query, acceptable in unrelated.items():
        got = _classify(query)
        assert got in acceptable | {"out_of_scope"}, f"{query!r} -> {got}"


def test_gibberish_is_rejected():
    """Nonsense and off-topic questions get 'I don't know', not a confident guess."""
    rejected = [c for c in GIBBERISH if _classify(c["query"]) == "out_of_scope"]
    rate = len(rejected) / len(GIBBERISH)
    answered = [(c["query"], _classify(c["query"])) for c in GIBBERISH if c not in rejected]
    assert rate >= MIN_GIBBERISH_REJECTION, f"only {rate:.0%} rejected; answered {answered}"


@pytest.mark.parametrize("query", [
    "asdkjaskjd",
    "qwertyuiop",
    "how do I bake a chocolate cake",
    "what is the capital of Australia",
    "write me a python function to sort a list",
    "are you sentient",
    "course gap dashboard banana",
])
def test_specific_nonsense_never_gets_a_domain_answer(query):
    assert _classify(query) == "out_of_scope"
