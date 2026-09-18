"""
Key-free extractive MCQ builder, used only when no LLM provider is reachable.

Every question is a sentence lifted from the document, with its key term or figure
blanked out. Distractors are other terms or figures of the same type from the same
document, ranked by vector similarity: far for Easy, nearest for Hard. The questions
are recall-level, but they cannot hallucinate, because every word comes from the source.
"""

from __future__ import annotations

import random
import re

import numpy as np

from ai.quiz import textutil as tu
from ai.quiz.passages import Passage
from ai.quiz.verifier import Candidate

_ACRONYM = re.compile(r"\b[A-Z]{2,6}\b")
# Proper-noun phrase: capitalised words, optional of/and/for/the between them, ending on a capitalised word.
_PHRASE = re.compile(r"\b[A-Z][a-z]+(?:[ -](?:(?:of|and|for|the|on|in) )?[A-Z][a-z]+){1,4}\b")
_YEAR = re.compile(r"\b(?:19|20)\d{2}(?:-\d{2})?\b")
_PERCENT = re.compile(r"\b\d+(?:\.\d+)?\s?(?:%|per ?cent)")
_DEFINITION = re.compile(
    r"^(?:The |An? )?(?P<term>[A-Za-z][\w()\-/ ]{2,60}?)\s+(?:is|are) (?:defined as|known as|called|the|a|an)\b"
    r"|^(?:The |An? )?(?P<term2>[A-Za-z][\w()\-/ ]{2,60}?)\s+(?:refers to|refer to|means)\b"
)
_GENERIC = {"the", "this", "it", "these", "there", "india", "government", "table", "figure", "chapter", "section"}


def _kind(term: str) -> str:
    if _PERCENT.fullmatch(term):
        return "percent"
    if _YEAR.fullmatch(term):
        return "year"
    if _ACRONYM.fullmatch(term):
        return "acronym"
    return "name"


def _base(term: str) -> str:
    """'Gross Domestic Product (GDP)' → 'gross domestic product' (for near-duplicate checks)."""
    return tu.normalize(re.sub(r"\s*\([^)]*\)", "", re.sub(r"^(the|an?) ", "", term, flags=re.I)))


def _definition_term(sent: str) -> str | None:
    d = _DEFINITION.match(sent)
    if not d:
        return None
    term = re.sub(r"^(the|an?) ", "", (d.group("term") or d.group("term2")).strip(), flags=re.I)
    if not 1 <= len(term.split()) <= 5 or term.lower() in _GENERIC:
        return None
    return term


def term_inventory(texts: list[str]) -> dict[str, list[str]]:
    """Candidate answer terms grouped by type ('concept' = defined terms), deduplicated."""
    seen: dict[str, tuple[str, str]] = {}
    for text in texts:
        for sent in tu.split_sentences(text):
            if not tu.is_sentence(sent):
                continue
            term = _definition_term(sent)
            if term:
                seen.setdefault(_base(term), (term, "concept"))
            for rx in (_PERCENT, _YEAR, _ACRONYM, _PHRASE):
                for m in rx.finditer(sent):
                    t = re.sub(r"^The ", "", m.group(0).strip())
                    if t.lower() in _GENERIC or len(t) < 2 or (rx is _PHRASE and m.start() == 0 and " " not in t):
                        continue
                    seen.setdefault(_base(t), (t, _kind(t)))
    inventory: dict[str, list[str]] = {}
    for term, kind in seen.values():
        inventory.setdefault(kind, []).append(term)
    return inventory


def _pick_distractors(answer: str, pool: list[str], sentence: str, difficulty: str, rng: random.Random) -> list[str]:
    ans_b = _base(answer)
    sent_n = tu.normalize(sentence)
    options = [
        t for t in pool
        if _base(t) and _base(t) != ans_b and _base(t) not in sent_n
        and ans_b not in _base(t) and _base(t) not in ans_b
    ]
    if len(options) < 3:
        return []
    vecs = tu.vectorize([answer] + options)
    sims = vecs[1:] @ vecs[0]
    order = [options[i] for i in np.argsort(-sims) if sims[i] < 0.92]
    if len(order) < 3:
        return []
    if difficulty == "Hard":
        chosen = order[:3]
    elif difficulty == "Easy":
        chosen = order[-3:]
    else:
        mid = len(order) // 2
        chosen = order[max(0, mid - 1): mid + 2]
    rng.shuffle(chosen)
    return chosen


def _near_numbers(answer: str, kind: str, rng: random.Random) -> list[str]:
    """Plausible neighbouring years/percentages when the document has too few of its own."""
    if kind == "year":
        m = re.match(r"(\d{4})(?:-(\d{2}))?", answer)
        base = int(m.group(1))
        shifts = rng.sample([-10, -5, -3, -2, 2, 3, 5], 3)
        if m.group(2):
            return [f"{base + s}-{(base + s + 1) % 100:02d}" for s in shifts]
        return [str(base + s) for s in shifts]
    value = float(re.match(r"\d+(?:\.\d+)?", answer).group(0))
    suffix = answer[len(re.match(r"\d+(?:\.\d+)?", answer).group(0)):]
    factors = rng.sample([0.5, 0.75, 1.25, 1.5, 2.0], 3)
    fmt = (lambda v: f"{v:.1f}") if "." in answer else (lambda v: str(int(round(v))))
    out = [fmt(value * f) + suffix for f in factors]
    return out if len(set(out + [answer])) == 4 else []


def build_offline(passages: list[Passage], count: int, difficulty: str, seed: int = 0) -> list[Candidate]:
    rng = random.Random(seed)
    inventory = term_inventory([p.text for p in passages])
    per_passage: list[list[Candidate]] = []

    for p in passages:
        found: list[Candidate] = []
        for sent in tu.split_sentences(p.text):
            if not 50 <= len(sent) <= 320 or sent.count("|") > 1 or not tu.is_sentence(sent):
                continue
            defined = _definition_term(sent)
            targets: list[tuple[str, str]] = [(defined, "concept")] if defined else []
            for rx, kind in ((_PERCENT, "percent"), (_YEAR, "year"), (_ACRONYM, "acronym"), (_PHRASE, "name")):
                targets += [(re.sub(r"^The ", "", m.group(0).strip()), kind) for m in rx.finditer(sent)]
            for term, kind in targets:
                if term.lower() in _GENERIC or sent.count(term) != 1:
                    continue
                if kind == "acronym" and f"({term})" in sent:
                    continue  # "Gross Domestic Product (_____)" gives the answer away
                pool = inventory.get(kind, [])
                distractors = _pick_distractors(term, pool, sent, difficulty, rng)
                if not distractors and kind in ("year", "percent"):
                    distractors = _near_numbers(term, kind, rng)
                if len(distractors) != 3:
                    continue
                blanked = sent.replace(term, "_____", 1)
                if kind == "concept":
                    stem = f"Which term does the document describe in this statement: “{blanked}”"
                else:
                    stem = f"Complete the statement from the document: “{blanked}”"
                options = [term] + distractors
                found.append(
                    Candidate(
                        question=stem,
                        options=options,
                        correct_answer=0,
                        explanation=f"The document states: “{sent}”",
                        evidence=sent,
                        source_id=p.id,
                        bloom_level="recall",
                        engine="offline",
                        location=p.location,
                    )
                )
                break  # one question per sentence
        per_passage.append(found)

    # Round-robin across passages so the quiz covers the document.
    out: list[Candidate] = []
    while len(out) < count and any(per_passage):
        for bucket in per_passage:
            if bucket and len(out) < count:
                out.append(bucket.pop(0))
    return out
