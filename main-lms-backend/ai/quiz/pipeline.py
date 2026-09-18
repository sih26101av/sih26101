"""
build_quiz(): passages → generate (model family A) → deterministic gate → blind
cross-check (model family B) → repair round → offline fill → pick best n → shuffle.

A question is kept only if its evidence quote is really in the document (gate)
and a model from a different family, seeing only the passage, independently
picks the same answer (cross-check). Groq keys/models and Gemini fail over to
one another; if every provider is down, the extractive builder takes over.
"""

from __future__ import annotations

import hashlib
import logging
import random
import time
from collections import Counter, OrderedDict
from dataclasses import dataclass, field

from ai.quiz import prompts
from ai.quiz.offline import build_offline
from ai.quiz.passages import Passage, select_passages
from ai.quiz.providers import ChatProvider, ProviderError, configured_providers
from ai.quiz.verifier import Candidate, coerce, dedupe, gate

logger = logging.getLogger(__name__)

DIFFICULTIES = ("Easy", "Medium", "Hard")
MIN_QUESTIONS = 3
_BLOOM_PREFERENCE = {
    "Easy": {"recall": 3, "understand": 2, "apply": 1, "analyse": 0},
    "Medium": {"understand": 3, "apply": 3, "recall": 1, "analyse": 2},
    "Hard": {"analyse": 3, "apply": 3, "understand": 1, "recall": 0},
}
_CACHE: "OrderedDict[str, QuizResult]" = OrderedDict()
_CACHE_SIZE = 64


class QuizBuildError(Exception):
    """The document cannot support a reliable quiz."""


@dataclass
class QuizResult:
    questions: list[Candidate]
    meta: dict = field(default_factory=dict)


def _pick_roles(providers: list[ChatProvider], exclude: set[str]) -> tuple[ChatProvider | None, ChatProvider | None]:
    """Generator = first available; checker = first available of a *different* family (else any other)."""
    live = [p for p in providers if p.available() and p.name not in exclude]
    if not live:
        return None, None
    gen = live[0]
    other_family = [p for p in live[1:] if p.family != gen.family]
    others = other_family or live[1:]
    return gen, (others[0] if others else gen)


async def _generate(gen: ChatProvider, passages: list[Passage], count: int, difficulty: str,
                    avoid: list[str]) -> list[Candidate]:
    data = await gen.complete_json(
        prompts.GENERATE_SYSTEM,
        prompts.generation_prompt(passages, count, difficulty, avoid),
        max_tokens=4096,
        temperature=0.4,
        purpose="generate",
    )
    raw = data.get("questions") if isinstance(data.get("questions"), list) else []
    return [c for c in (coerce(item, engine=gen.name) for item in raw) if c]


async def _cross_check(checker: ChatProvider, cands: list[Candidate], by_id: dict[str, Passage]) -> dict[int, tuple[int, str]]:
    """Blind-answer every candidate; returns {index: (answer, reason)}."""
    items = [
        {"id": f"q{i + 1}", "passage": by_id[c.source_id].text, "question": c.question, "options": c.options}
        for i, c in enumerate(cands)
    ]
    data = await checker.complete_json(
        prompts.CHECK_SYSTEM, prompts.check_prompt(items), max_tokens=3000, temperature=0.0, purpose="check"
    )
    out: dict[int, tuple[int, str]] = {}
    for row in data.get("answers") or []:
        try:
            idx = int(str(row.get("id", "")).lstrip("qQ")) - 1
            answer = int(row.get("answer", -1))
            defensible = row.get("defensible")
            if isinstance(defensible, list) and len({int(d) for d in defensible}) > 1:
                answer = -1  # more than one option could be argued correct → ambiguous
            out[idx] = (answer, str(row.get("reason", ""))[:200])
        except (TypeError, ValueError):
            continue
    return out


def _balance_positions(cands: list[Candidate], rng: random.Random) -> None:
    """Shuffle options so correct answers are spread evenly over A-D."""
    slots = [0, 1, 2, 3] * (len(cands) // 4 + 1)
    rng.shuffle(slots)
    for c, target in zip(cands, slots):
        answer = c.options[c.correct_answer]
        rest = [o for i, o in enumerate(c.options) if i != c.correct_answer]
        rng.shuffle(rest)
        rest.insert(target, answer)
        c.options, c.correct_answer = rest, target


def _choose(cands: list[Candidate], n: int, difficulty: str) -> list[Candidate]:
    """Greedy pick: prefer LLM over offline, the difficulty's bloom mix, and unused passages."""
    pref = _BLOOM_PREFERENCE[difficulty]
    chosen: list[Candidate] = []
    pool = list(cands)
    while pool and len(chosen) < n:
        used_sources = Counter(c.source_id for c in chosen)
        used_bloom = Counter(c.bloom_level for c in chosen)

        def score(c: Candidate) -> float:
            return (
                (0 if c.engine == "offline" else 10)
                + pref.get(c.bloom_level, 1)
                - 4 * used_sources[c.source_id]
                - 0.5 * used_bloom[c.bloom_level]
            )

        best = max(pool, key=score)
        chosen.append(best)
        pool.remove(best)
    return sorted(chosen, key=lambda c: int(c.source_id.lstrip("P") or 0))


async def build_quiz(
    text: str,
    chunks: list[str],
    n: int = 5,
    difficulty: str = "Medium",
    seed: int | None = None,
    providers: list[ChatProvider] | None = None,
    use_cache: bool = True,
) -> QuizResult:
    difficulty = difficulty.capitalize() if difficulty and difficulty.capitalize() in DIFFICULTIES else "Medium"
    cache_key = hashlib.sha256(f"{difficulty}|{n}|{text}".encode("utf-8", "ignore")).hexdigest()
    if use_cache and cache_key in _CACHE:
        _CACHE.move_to_end(cache_key)
        cached = _CACHE[cache_key]
        return QuizResult([Candidate(**{**c.__dict__, "options": list(c.options)}) for c in cached.questions],
                          {**cached.meta, "cached": True})

    started = time.monotonic()
    rng = random.Random(seed if seed is not None else int(cache_key[:8], 16))
    providers = configured_providers() if providers is None else providers
    calls_before = sum(getattr(p, "calls", 0) for p in providers)

    passages = select_passages(text, chunks, k=min(10, n + 3))
    if not passages:
        raise QuizBuildError("The document has too little readable content to build a reliable quiz.")
    by_id = {p.id: p for p in passages}

    rejected: Counter = Counter()
    kept: list[Candidate] = []
    engines: list[str] = []
    checkers: list[str] = []
    verification = "cross-model"
    failed: set[str] = set()
    events: list[str] = []

    for round_no in range(2):  # initial round + one repair round
        need = n - len(kept)
        if need <= 0:
            break
        gen, checker = _pick_roles(providers, failed)
        if gen is None:
            break
        want = need + 3 if round_no == 0 else need + 2
        try:
            cands = await _generate(gen, passages, want, difficulty, [c.question for c in kept])
        except ProviderError as exc:
            events.append(str(exc))
            failed.add(gen.name)
            continue
        engines.append(gen.name)

        gated: list[Candidate] = []
        for c in cands:
            reasons = gate(c, by_id)
            if reasons:
                rejected.update(reasons)
                logger.info("[quiz] gate rejected (%s): %s", ",".join(reasons), c.question[:90])
            else:
                gated.append(c)
        gated, dupes = dedupe(kept + gated)
        if dupes:
            rejected["duplicate"] += dupes
        gated = gated[len(kept):] if len(gated) > len(kept) else []
        if not gated:
            continue

        verdicts: dict[int, tuple[int, str]] | None = None
        for attempt_checker in [checker] + [p for p in providers if p.available() and p.name not in {checker.name, gen.name}]:
            try:
                verdicts = await _cross_check(attempt_checker, gated, by_id)
                checkers.append(attempt_checker.name)
                if attempt_checker.family == gen.family:
                    verification = "self" if attempt_checker is gen else "same-family"
                break
            except ProviderError as exc:
                events.append(str(exc))
                failed.add(attempt_checker.name)
        if verdicts is None:
            # No checker reachable: keep only gate-verifiable (recall/understand) questions.
            verification = "gate-only"
            kept += [c for c in gated if c.bloom_level in ("recall", "understand")]
            unchecked = sum(c.bloom_level not in ("recall", "understand") for c in gated)
            if unchecked:
                rejected["unchecked_reasoning"] += unchecked
            continue

        for i, c in enumerate(gated):
            answer, reason = verdicts.get(i, (-2, "no verdict"))
            if answer == c.correct_answer:
                c.checked_by = checkers[-1]
                kept.append(c)
            else:
                rejected["ambiguous" if answer == -1 else "cross_check_disagree"] += 1
                logger.info("[quiz] cross-check rejected (key=%s, checker=%s, %s): %s",
                            c.correct_answer, answer, reason, c.question[:90])

    offline_used = 0
    if len(kept) < n:
        extra = build_offline(passages, (n - len(kept)) * 3, difficulty, seed=rng.randint(0, 10**6))
        extra = [c for c in extra if not gate(c, by_id)]
        merged, _ = dedupe(kept + extra)
        fill = merged[len(kept):][: n - len(kept)]
        offline_used = len(fill)
        kept += fill

    if len(kept) < min(MIN_QUESTIONS, n):
        raise QuizBuildError(
            "Could not build enough verified questions from this document. "
            "Try a document with more explanatory text (definitions, procedures, figures)."
        )

    questions = _choose(kept, n, difficulty)
    _balance_positions(questions, rng)

    meta = {
        "difficulty": difficulty,
        "generator": engines[0] if engines else "offline",
        "checker": checkers[0] if checkers else None,
        "verification": verification if checkers else ("gate-only" if engines else "offline"),
        "passages_used": len(passages),
        "llm_questions": sum(q.engine != "offline" for q in questions),
        "offline_questions": sum(q.engine == "offline" for q in questions),
        "rejected": dict(rejected),
        "provider_errors": events[:5],
        "api_calls": sum(getattr(p, "calls", 0) for p in providers) - calls_before,
        "seconds": round(time.monotonic() - started, 2),
        "cached": False,
    }
    if offline_used and not engines:
        meta["verification"] = "offline"
    result = QuizResult(questions, meta)
    if use_cache:
        _CACHE[cache_key] = result
        while len(_CACHE) > _CACHE_SIZE:
            _CACHE.popitem(last=False)
    return QuizResult([Candidate(**{**c.__dict__, "options": list(c.options)}) for c in questions], dict(meta))
