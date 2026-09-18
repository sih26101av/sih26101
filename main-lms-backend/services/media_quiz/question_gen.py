"""
FILE: services/media_quiz/question_gen.py
─────────────────────────────────────────────────────────────────────────────
Step 4: questions that CITE evidence ids.

  1. Per-chunk pass — chunks are sent in small groups (one Gemini call per
     group, run concurrently); every question must cite evidence ids from its
     own chunk: "evidence": ["e42", "e43"].
  2. Synthesis pass (flaw 10) — one call over a short summary of the whole
     video writes 2–3 questions that need ≥2 different chunks.
  3. Validator — a question survives only if
       • it has 4 distinct non-empty options and a valid answer index,
       • every cited id exists on the (already confidence-pruned) timeline and
         its confidence ≥ MIN_CONFIDENCE,
       • any number in the correct option appears in the cited evidence
         (catches invented figures),
       • it is not about the video itself ("what did the speaker say at the end").
     Rejections are counted per reason for the before/after comparison.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import asyncio
import logging
import random
import re
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Tuple

from services.media_quiz.evidence import MIN_CONFIDENCE, Chunk, Timeline, fmt_ts
from services.media_quiz.llm import LLMUnavailable, gemini_json

logger = logging.getLogger(__name__)

CHUNK_QUESTIONS_TARGET = 5
SYNTHESIS_TARGET = 2
CHUNKS_PER_CALL = 4

_META_Q = re.compile(
    r"\b(the (speaker|presenter|narrator|instructor|video)|this video|in the video|subscribe|thank(s| you) for watching)\b",
    re.I,
)
# Internal labels must never reach the learner ("as shown in chunk c4", "evidence e12").
# Only "chunk"/"evidence"/"section" phrasing is matched, so code like print(c1) or cell E5 passes.
_INTERNAL_REF = re.compile(r"\b(chunks?|sections?)\s+c?\d+\b|\bevidence\s+(ids?\s+)?e\d+\b|\[e\d+", re.I)
_NUM = re.compile(r"\d+(?:[.,]\d+)*")
_DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


def numbers_in(text: str) -> set:
    return {n.replace(",", "") for n in _NUM.findall(text.translate(_DEVANAGARI_DIGITS))}


_DIFFICULTY = {
    "Easy": "recall of clearly stated facts and definitions",
    "Medium": "understanding and application of the concepts and procedures",
    "Hard": "analysis: interpreting results, comparing methods, spotting errors, multi-step reasoning",
}


@dataclass
class MediaQuestion:
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    evidence: List[str]
    kind: str = "chunk"                  # "chunk" | "synthesis"
    answer_type: str = "concept"         # "number" | "definition" | "concept" | "procedure"
    chunk_ids: List[str] = field(default_factory=list)
    t_start: Optional[float] = None
    t_end: Optional[float] = None
    review: Dict = field(default_factory=lambda: {"status": "unchecked"})

    def to_dict(self) -> Dict:
        return asdict(self)


def _rules(difficulty: str) -> str:
    return (
        f"Target difficulty: {difficulty} — {_DIFFICULTY.get(difficulty, _DIFFICULTY['Medium'])}.\n"
        "Rules:\n"
        "- Use ONLY facts stated in the evidence lines. Each line starts with [id | source | time | lang].\n"
        "  source asr = what was said, ocr = text on screen, vlm = description of what the screen shows.\n"
        "- Every question MUST list the evidence ids that support its correct answer in \"evidence\".\n"
        "- Evidence ids and chunk labels are internal: NEVER mention them, or the words 'chunk' / 'section' / "
        "'evidence', in the question, options or explanation. Refer to the topic instead.\n"
        "- Test the subject matter (statistics, methods, tools, procedures), never the video itself: no questions "
        "about the speaker, the video, greetings, or timing.\n"
        "- For screen demos, ask about the actions and their purpose (e.g. what a pivot-table step achieves).\n"
        "- For charts/tables, ask what they show.\n"
        "- Exactly 4 distinct, plausible options; \"correct_answer\" is the 0-based index.\n"
        "- \"answer_type\": number (answer is a figure/year/value), definition, concept or procedure.\n"
        "- Write questions in English even if the evidence is Hindi / Hinglish; keep technical terms as used.\n"
    )


def _schema(extra: str = "") -> str:
    return ('Return JSON: {"questions":[{"chunk":"c1","question":"...","options":["","","",""],'
            '"correct_answer":0,"explanation":"...","evidence":["e1","e2"],"answer_type":"concept"' + extra + '}]}')


def _coerce(item: Dict) -> Optional[Tuple[str, List[str], int, str, List[str], str]]:
    if not isinstance(item, dict):
        return None
    q = str(item.get("question") or "").strip()
    opts = item.get("options") or []
    if isinstance(opts, dict):
        opts = list(opts.values())
    opts = [str(o).strip() for o in opts] if isinstance(opts, list) else []
    ans = item.get("correct_answer")
    if isinstance(ans, str):
        a = ans.strip().upper()
        ans = ord(a) - 65 if a in {"A", "B", "C", "D"} else (int(a) if a.isdigit() else
                                                             next((i for i, o in enumerate(opts) if o.lower() == ans.strip().lower()), -1))
    ev = item.get("evidence") or []
    ev = [str(e).strip() for e in (ev if isinstance(ev, list) else [ev])]
    return (q, opts, ans if isinstance(ans, int) else -1, str(item.get("explanation") or "").strip(), ev,
            str(item.get("answer_type") or "concept").lower())


def validate(item: Dict, timeline: Timeline, allowed_ids: Optional[set], stats: Dict[str, int],
             kind: str, min_chunks: int = 1, id_to_chunk: Optional[Dict[str, str]] = None) -> Optional[MediaQuestion]:
    def reject(reason: str):
        stats[reason] = stats.get(reason, 0) + 1
        return None

    c = _coerce(item)
    if not c:
        return reject("malformed")
    q, opts, ans, expl, ev_ids, atype = c
    if len(q) < 12:
        return reject("empty_question")
    if len(opts) != 4 or any(not o for o in opts) or len({o.lower() for o in opts}) != 4:
        return reject("bad_options")
    if not 0 <= ans < 4:
        return reject("bad_answer_index")
    if _META_Q.search(q):
        return reject("about_the_video_not_the_subject")
    if _INTERNAL_REF.search(" ".join([q, expl] + opts)):
        return reject("mentions_internal_ids")
    if not ev_ids:
        return reject("no_evidence_cited")
    evs = []
    for eid in ev_ids:
        e = timeline.get(eid)
        if e is None or (allowed_ids is not None and eid not in allowed_ids):
            return reject("cited_unknown_evidence")
        if e.confidence < MIN_CONFIDENCE:
            return reject("cited_low_confidence_evidence")
        evs.append(e)
    chunks = {id_to_chunk.get(e.id) for e in evs} if id_to_chunk else set()
    if len(chunks - {None}) < min_chunks:
        return reject("synthesis_not_cross_chunk")
    cited_text = " ".join(e.text for e in evs)
    if not numbers_in(opts[ans]) <= numbers_in(cited_text):
        return reject("answer_number_not_in_evidence")

    # Shuffle so the key is not always "A" (LLMs favour the first slot).
    order = list(range(4))
    random.Random(q).shuffle(order)
    new_opts = [opts[i] for i in order]
    return MediaQuestion(
        question=q, options=new_opts, correct_answer=order.index(ans),
        explanation=expl or "Supported by the cited evidence.", evidence=ev_ids, kind=kind,
        answer_type=atype if atype in {"number", "definition", "concept", "procedure"} else "concept",
        chunk_ids=sorted(chunks - {None}),
        t_start=min(e.t_start for e in evs), t_end=max(e.t_end for e in evs),
    )


async def _chunk_pass(group: List[Chunk], difficulty: str, per_chunk: int = 2) -> List[Dict]:
    body = "\n\n".join(f"=== CHUNK {c.id} ({fmt_ts(c.t_start)}–{fmt_ts(c.t_end)}) ===\n{c.text}" for c in group)
    prompt = (
        "You write multiple-choice assessment questions for MoSPI (Ministry of Statistics, India) officials "
        "from the evidence extracted out of a training video.\n"
        f"Write up to {per_chunk} questions PER CHUNK, each on a different point. A question may cite only evidence ids from its own chunk.\n{_rules(difficulty)}"
        f"{_schema()}\n\n{body}"
    )
    data = await gemini_json(prompt)
    qs = data.get("questions", []) if isinstance(data, dict) else data if isinstance(data, list) else []
    return [q for q in qs if isinstance(q, dict)]


def _summary(chunks: List[Chunk], timeline: Timeline, per_chunk_chars: int = 420) -> str:
    parts = []
    for c in chunks:
        lines, size = [], 0
        for eid in c.evidence_ids:
            e = timeline.get(eid)
            if not e:
                continue
            line = f"[{e.id} | {e.source}] {e.text[:220]}"
            if size + len(line) > per_chunk_chars:
                break
            lines.append(line)
            size += len(line)
        parts.append(f"--- {c.id} ({fmt_ts(c.t_start)}) ---\n" + "\n".join(lines))
    return "\n".join(parts)


async def _synthesis_pass(chunks: List[Chunk], timeline: Timeline, difficulty: str) -> List[Dict]:
    prompt = (
        "Below is a condensed summary of a whole MoSPI training video, section by section.\n"
        "Write 3 synthesis questions that can only be answered by combining information from AT LEAST TWO "
        "different sections (e.g. how a step shown early relates to a result shown later, or comparing two methods).\n"
        f"Each must cite evidence ids from at least two different sections.\n{_rules(difficulty)}{_schema()}\n\n"
        f"{_summary(chunks, timeline)}"
    )
    data = await gemini_json(prompt)
    qs = data.get("questions", []) if isinstance(data, dict) else data if isinstance(data, list) else []
    return [q for q in qs if isinstance(q, dict)]


async def generate(chunks: List[Chunk], timeline: Timeline, difficulty: str = "Medium") -> Tuple[List[MediaQuestion], Dict]:
    stats: Dict[str, int] = {}
    id_to_chunk = {eid: c.id for c in chunks for eid in c.evidence_ids}
    groups = [chunks[i:i + CHUNKS_PER_CALL] for i in range(0, len(chunks), CHUNKS_PER_CALL)]

    # Short media → few chunks: ask more per chunk (+1 spare for validator losses).
    n_per_chunk = min(6, max(2, -(-(CHUNK_QUESTIONS_TARGET + 1) // len(chunks))))
    tasks = [_chunk_pass(g, difficulty, n_per_chunk) for g in groups]
    if len(chunks) >= 2:
        tasks.append(_synthesis_pass(chunks, timeline, difficulty))
    results = await asyncio.gather(*tasks, return_exceptions=True)

    errors = [r for r in results if isinstance(r, Exception)]
    if errors and len(errors) == len(results):
        raise errors[0] if isinstance(errors[0], LLMUnavailable) else LLMUnavailable(str(errors[0]))
    for e in errors:
        logger.warning("[media-qgen] a generation call failed: %s", e)

    per_chunk: Dict[str, List[MediaQuestion]] = {}
    raw_count = 0
    for g, res in zip(groups, results[:len(groups)]):
        if isinstance(res, Exception):
            continue
        allowed = {eid for c in g for eid in c.evidence_ids}
        for item in res:
            raw_count += 1
            mq = validate(item, timeline, allowed, stats, "chunk", 1, id_to_chunk)
            if mq:
                per_chunk.setdefault(mq.chunk_ids[0] if mq.chunk_ids else "?", []).append(mq)

    synthesis: List[MediaQuestion] = []
    if len(results) > len(groups) and not isinstance(results[-1], Exception):
        allowed = set(id_to_chunk)
        for item in results[-1]:
            raw_count += 1
            mq = validate(item, timeline, allowed, stats, "synthesis", 2, id_to_chunk)
            if mq:
                synthesis.append(mq)

    # Round-robin across chunks (in time order) so questions cover the whole video.
    chosen: List[MediaQuestion] = []
    seen_q = set()
    order = [c.id for c in chunks]
    while len(chosen) < CHUNK_QUESTIONS_TARGET and any(per_chunk.get(cid) for cid in order):
        for cid in order:
            if per_chunk.get(cid) and len(chosen) < CHUNK_QUESTIONS_TARGET:
                q = per_chunk[cid].pop(0)
                if q.question.lower() not in seen_q:
                    chosen.append(q)
                    seen_q.add(q.question.lower())
    chosen += [q for q in synthesis if q.question.lower() not in seen_q][:SYNTHESIS_TARGET]

    report = {"raw_candidates": raw_count, "accepted": len(chosen),
              "rejected": stats, "rejected_total": sum(stats.values()),
              "synthesis_accepted": sum(1 for q in chosen if q.kind == "synthesis"),
              "llm_errors": len(errors)}
    return chosen, report


async def generate_naive(transcript: str, difficulty: str = "Medium") -> List[Dict]:
    """BASELINE for the eval only: raw transcript → 5 MCQs, no citations, no validator."""
    data = await gemini_json(
        "Generate exactly 5 multiple-choice questions (4 options, 0-based correct_answer, explanation) from this "
        f"training video transcript. Difficulty: {difficulty}.\n"
        '{"questions":[{"question":"","options":["","","",""],"correct_answer":0,"explanation":""}]}\n\n'
        f"Transcript:\n{transcript[:40000]}"
    )
    qs = data.get("questions", []) if isinstance(data, dict) else data
    return [q for q in qs if isinstance(q, dict)]
