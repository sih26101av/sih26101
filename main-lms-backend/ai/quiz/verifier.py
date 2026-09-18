"""
Deterministic grounding gate: no API calls, and every engine's output passes through it.

`gate()` returns the list of reasons a candidate question is rejected (empty = accepted).
It catches fabricated evidence quotes, facts and figures missing from the source, answers
leaked in the stem, and malformed option sets. Questions that need reasoning (apply/analyse)
cannot be checked lexically, so the pipeline relies on the blind cross-model check for those.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np

from ai.quiz import textutil as tu
from ai.quiz.passages import Passage

BLOOM_LEVELS = ("recall", "understand", "apply", "analyse")
EVIDENCE_MIN_COVERAGE = 0.85
DUPLICATE_COSINE = 0.85

_BANNED_OPTION = re.compile(
    r"^(all|none|both|neither)\b.*\b(above|below|of these|options?)\b|^(all|none) of (the )?(above|these)$"
    r"|^both [a-d] and [a-d]$|^option [a-d]$|^[a-d]$",
    re.I,
)
_META_STEM = re.compile(r"\b(chunk|P\d+\b|page \d+|slide \d+|this document'?s? (title|author))", re.I)
_PASSAGE_WORD = re.compile(r"\b(the|this|that) (given |above |provided )?(passage|text|excerpt)s?\b", re.I)


@dataclass
class Candidate:
    question: str
    options: list[str]
    correct_answer: int
    explanation: str
    evidence: str
    source_id: str
    bloom_level: str = "recall"
    engine: str = "llm"
    location: str | None = None
    checked_by: str | None = None
    rejections: list[str] = field(default_factory=list)

    @property
    def answer_text(self) -> str:
        return self.options[self.correct_answer]


def coerce(item: dict, engine: str) -> Candidate | None:
    """Normalise one raw LLM question dict (alias keys, letter answers) into a Candidate."""
    if not isinstance(item, dict):
        return None
    question = str(item.get("question") or item.get("question_text") or item.get("stem") or "").strip()
    raw_opts = item.get("options") or item.get("choices") or []
    if isinstance(raw_opts, dict):
        raw_opts = list(raw_opts.values())
    if not isinstance(raw_opts, list):
        return None
    options = [re.sub(r"^\s*(?:\(?[A-Da-d][).:]|[A-Da-d]\s-)\s+", "", str(o)).strip() for o in raw_opts]

    raw_ans = item.get("correct_answer", item.get("correctAnswer", item.get("answer")))
    answer = -1
    if isinstance(raw_ans, bool):
        answer = -1
    elif isinstance(raw_ans, int):
        answer = raw_ans
    elif isinstance(raw_ans, str):
        s = raw_ans.strip()
        if s.isdigit():
            answer = int(s)
        elif len(s) == 1 and s.upper() in "ABCD":
            answer = ord(s.upper()) - ord("A")
        else:
            answer = next((i for i, o in enumerate(options) if tu.normalize(o) == tu.normalize(s)), -1)

    bloom = str(item.get("bloom_level") or "recall").strip().lower().replace("analyze", "analyse")
    question = _PASSAGE_WORD.sub("the document", question)
    return Candidate(
        question=question,
        options=options,
        correct_answer=answer,
        explanation=_PASSAGE_WORD.sub("the document", str(item.get("explanation") or "").strip()),
        evidence=str(item.get("evidence") or item.get("quote") or "").strip().strip('"“”'),
        source_id=str(item.get("source_id") or item.get("source") or "").strip(),
        bloom_level=bloom if bloom in BLOOM_LEVELS else "understand",
        engine=engine,
    )


def _resolve_source(c: Candidate, passages: dict[str, Passage]) -> tuple[Passage | None, float]:
    """Best passage for the evidence quote: the cited one, or another if the model mis-cited."""
    cited = passages.get(c.source_id)
    best, best_cov = cited, tu.quote_coverage(c.evidence, cited.text) if cited else 0.0
    if best_cov < EVIDENCE_MIN_COVERAGE:
        for p in passages.values():
            cov = tu.quote_coverage(c.evidence, p.text)
            if cov > best_cov:
                best, best_cov = p, cov
    return best, best_cov


def gate(c: Candidate, passages: dict[str, Passage]) -> list[str]:
    reasons: list[str] = []

    # ── Structure ─────────────────────────────────────────────────────────────
    if len(c.question) < 12:
        reasons.append("empty_question")
    if len(c.options) != 4 or any(not o for o in c.options):
        reasons.append("bad_options")
        return reasons
    if len({tu.normalize(o) for o in c.options}) < 4:
        reasons.append("duplicate_options")
    if any(_BANNED_OPTION.search(o.strip()) for o in c.options):
        reasons.append("banned_option")
    if not 0 <= c.correct_answer < 4:
        reasons.append("bad_answer_index")
        return reasons
    if _META_STEM.search(c.question):
        reasons.append("meta_question")
    longest_distractor = max(len(o) for i, o in enumerate(c.options) if i != c.correct_answer)
    if len(c.answer_text) > 50 and len(c.answer_text) > 1.8 * longest_distractor:
        reasons.append("answer_length_giveaway")

    # ── Grounding ─────────────────────────────────────────────────────────────
    passage, coverage = _resolve_source(c, passages)
    if passage is None or len(c.evidence) < 15 or coverage < EVIDENCE_MIN_COVERAGE:
        reasons.append("evidence_not_in_source")
        return reasons
    c.source_id, c.location = passage.id, passage.location
    source = passage.text

    answer = c.answer_text
    reasoning = c.bloom_level in ("apply", "analyse")
    if not reasoning:
        support = tu.token_support(answer, c.evidence + " " + source)
        answer_nums = tu.numbers(answer)
        if answer_nums and not answer_nums <= tu.numbers(source):
            reasons.append("number_not_in_source")
        elif tu.content_tokens(answer) and support < 0.5:
            rival = max(
                tu.token_support(o, c.evidence) for i, o in enumerate(c.options) if i != c.correct_answer
            )
            reasons.append("wrong_key" if rival >= 0.8 else "answer_not_in_source")
    # Figures in the stem must come from the source unless it is a hypothetical scenario.
    if not reasoning and not tu.numbers(c.question) <= tu.numbers(source):
        reasons.append("stem_number_not_in_source")

    # ── Answer leaked in the stem (scenarios legitimately reuse option words) ──
    ans_norm = tu.normalize(answer)
    if not reasoning and len(ans_norm) >= 5 and re.search(rf"\b{re.escape(ans_norm)}\b", tu.normalize(c.question)):
        others_in_stem = sum(
            bool(re.search(rf"\b{re.escape(tu.normalize(o))}\b", tu.normalize(c.question)))
            for i, o in enumerate(c.options) if i != c.correct_answer and len(tu.normalize(o)) >= 3
        )
        if others_in_stem == 0:
            reasons.append("answer_in_stem")
    return reasons


def dedupe(cands: list[Candidate], threshold: float = DUPLICATE_COSINE) -> tuple[list[Candidate], int]:
    """Drop near-duplicate questions (same fact asked twice); earlier candidates win."""
    if len(cands) < 2:
        return cands, 0
    vecs = tu.vectorize([f"{c.question} {c.answer_text}" for c in cands])
    kept: list[int] = []
    for i in range(len(cands)):
        if all(float(np.dot(vecs[i], vecs[j])) < threshold for j in kept):
            kept.append(i)
    return [cands[i] for i in kept], len(cands) - len(kept)
