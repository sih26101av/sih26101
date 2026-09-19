"""
FILE: services/doc_quiz/generate.py
─────────────────────────────────────────────────────────────────────────────
Document → cited, validated, multi-type quiz. Brings the document quiz to
parity with the media pipeline (services/media_quiz/question_gen.py):

  1. Locate + select chunks. Each LangChain chunk gets an id (c1…) and a
     locator ("Page 4", "Slide 2", "Section 3: Price collection") from the
     extractor's markers. Up to MAX_CHUNKS are chosen evenly across the
     document, preferring information-dense chunks.
  2. Generate. One Gemini call per group of CHUNKS_PER_CALL chunks (run
     concurrently), asking ~1.8× the needed questions over the requested types.
     Every question cites its chunk and a VERBATIM quote from it, and gives a
     per-option "why_wrong" rationale (used for personalised feedback).
  3. Validate (reasons counted in report.rejected):
       • type-specific shape (4 options, T/F, 2+ correct for multi-select, one
         blank, a parseable number…);
       • the cited chunk exists and the quote is really in it;
       • numbers in the answer appear in the cited source — or, for computed
         answers, the `expression` evaluates to the answer and uses only inputs
         from the stem or the source;
       • a fill-in answer is in the source and not given away by the stem;
       • distractors: no "all/none of the above", no near-duplicates, no answer
         that is conspicuously longer, numeric answers get numeric distractors;
       • not about the document itself ("on page 3", "the author") and no
         internal chunk labels.
  4. Plausibility + dedup (multilingual-e5 "chat" embedder, optional):
     distractors unrelated to the stem or paraphrasing the answer are rejected;
     questions whose stems are near-identical, or that test the same fact from
     the same chunk, are dropped.
  5. Select to the requested count: type quotas → difficulty mix → spread over
     chunks. Options are shuffled deterministically.
  6. Fact-check numbers/definitions against reference_facts.json (flags only)
     — the same check as the media pipeline.
  7. Translate to Hindi (language "hi" or bilingual "bi") with glossary terms
     protected; stored under question["translations"]["hi"].
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import asyncio
import difflib
import logging
import math
import random
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from services import practice_assessment as pa
from services.doc_quiz import items as it
from services.media_quiz.fact_check import review_answer, translate_texts
from services.media_quiz.llm import LLMUnavailable, gemini_json
from services.media_quiz.question_gen import _INTERNAL_REF, numbers_in

logger = logging.getLogger(__name__)

MAX_QUESTIONS = 20
MIN_QUESTIONS = 3
MAX_CHUNKS = 24
CHUNKS_PER_CALL = 4
OVERGENERATE = 1.8
LANGUAGES = ("en", "hi", "bi")

_MARKER = re.compile(r"--- (Page|Slide|Section) (\d+)(?::\s*(.*?))? ---")
_DOC_META = re.compile(
    r"\b(this|the) (document|pdf|file|presentation|slide deck|handout|author)\b|\b(on|in|at) (page|slide) \d+\b",
    re.I)
_CATCH_ALL = re.compile(r"\b(all|none|both|neither) of (the )?(above|these|them|the options)\b", re.I)

# Share of each difficulty in a quiz, by target difficulty (generalises the old fixed 5-question mix).
DIFFICULTY_MIX = {"Easy": {"Easy": 0.6, "Medium": 0.4, "Hard": 0.0},
                  "Medium": {"Easy": 0.2, "Medium": 0.6, "Hard": 0.2},
                  "Hard": {"Easy": 0.0, "Medium": 0.2, "Hard": 0.8}}
_DIFFICULTY_GUIDE = {
    "Easy": "recall and recognition — facts, definitions and terms stated directly in the text",
    "Medium": "understanding and application — explain, compare, or apply a stated procedure or formula to a simple case",
    "Hard": "analysis and evaluation — multi-step reasoning, interpreting results, choosing between methods, spotting an error",
}


@dataclass
class DocChunk:
    id: str
    text: str
    locator: str
    index: int
    segments: List[Tuple[str, str]] = field(default_factory=list)   # (locator, text) per page/section inside the chunk

    def locate(self, quote: str) -> str:
        """The page / slide / section the quote actually sits in (a chunk can span two)."""
        if len(self.segments) < 2:
            return self.locator
        qt = set(_tokens(quote))
        best = max(self.segments, key=lambda seg: len(qt & set(_tokens(seg[1]))))
        return best[0] or self.locator


# ── 1. Chunks ─────────────────────────────────────────────────────────────────

def _label(kind: str, num: str, title: Optional[str]) -> str:
    return f"{kind} {num}" + (f": {title.strip()}" if title and title.strip() else "")


def locate_chunks(text: str, chunks: List[str]) -> List[DocChunk]:
    """Give each chunk an id and a human locator from the page/slide/section markers."""
    markers = [(m.start(), m.group(1), m.group(2), m.group(3)) for m in _MARKER.finditer(text)]
    out, cursor = [], 0
    for i, chunk in enumerate(chunks):
        probe = chunk[:80]
        pos = text.find(probe, cursor)
        if pos < 0:
            pos = text.find(probe)
        if pos < 0:
            pos = cursor
        end = pos + len(chunk)
        cursor = max(cursor, pos + 1)
        before = [m for m in markers if m[0] <= pos]
        inside = [m for m in markers if pos < m[0] < end]
        first = before[-1] if before else (inside[0] if inside else None)
        last = inside[-1] if inside else first
        if first is None:
            loc = f"Part {i + 1}"
        elif last is first or (last[1], last[2]) == (first[1], first[2]):
            loc = _label(first[1], first[2], first[3])
        elif first[1] == last[1]:
            loc = f"{first[1]}s {first[2]}–{last[2]}"
        else:
            loc = _label(first[1], first[2], first[3])
        parts = _MARKER.split(chunk)          # [text, kind, num, title, text, kind, num, title, text, …]
        segments = [(_label(first[1], first[2], first[3]) if before else "", parts[0])]
        for j in range(1, len(parts) - 3, 4):
            segments.append((_label(parts[j], parts[j + 1], parts[j + 2]), parts[j + 3]))
        segments = [(lab, txt) for lab, txt in segments if txt.strip()]
        clean = _MARKER.sub(" ", chunk).strip()
        out.append(DocChunk(id=f"c{i + 1}", text=clean, locator=loc, index=i, segments=segments))
    return out


def _density(c: DocChunk) -> float:
    words = len(c.text.split())
    return min(words, 180) + 6 * min(len(numbers_in(c.text)), 10)


def select_chunks(chunks: List[DocChunk], n_questions: int) -> List[DocChunk]:
    usable = [c for c in chunks if len(re.sub(r"\s", "", c.text)) >= 150] or chunks
    k = min(len(usable), MAX_CHUNKS, max(3, math.ceil(n_questions * 0.8)))
    if k >= len(usable):
        return usable
    # One chunk per equal slice of the document: coverage first, then density.
    picked = []
    for s in range(k):
        lo, hi = s * len(usable) // k, (s + 1) * len(usable) // k
        picked.append(max(usable[lo:hi], key=_density))
    return picked


def _quantitative(chunks: List[DocChunk]) -> bool:
    nums = set()
    for c in chunks:
        nums |= {n for n in numbers_in(c.text) if len(n) > 1 or "." in n}
    return len(nums) >= 4


# ── Quotas ────────────────────────────────────────────────────────────────────

def _largest_remainder(shares: Dict[str, float], n: int) -> Dict[str, int]:
    total = sum(shares.values()) or 1.0
    raw = {k: n * v / total for k, v in shares.items()}
    out = {k: int(math.floor(v)) for k, v in raw.items()}
    for k in sorted(raw, key=lambda k: raw[k] - out[k], reverse=True)[: n - sum(out.values())]:
        out[k] += 1
    return out


def type_quotas(types: List[str], n: int) -> Dict[str, int]:
    """MCQ gets a double share (the PS's core type); others share the rest evenly."""
    shares = {t: (2.0 if t == "mcq" else 1.0) for t in types}
    return _largest_remainder(shares, n)


def difficulty_quotas(target: str, n: int) -> Dict[str, int]:
    return _largest_remainder(DIFFICULTY_MIX[pa.normalise_difficulty(target)], n)


def parse_types(value: Any) -> List[str]:
    raw = value if isinstance(value, (list, tuple)) else str(value or "").split(",")
    seen = []
    for v in raw:
        if str(v).strip():
            t = it.normalise_type(v)
            if t not in seen:
                seen.append(t)
    return seen or ["mcq"]


# ── 2. Generation ─────────────────────────────────────────────────────────────

_TYPE_SPEC = {
    "mcq": '{"type":"mcq","options":["","","",""],"correct_answer":0,"why_wrong":["","why B is wrong","…","…"]}',
    "true_false": '{"type":"true_false","question":"<a full statement to judge>","correct_answer":true,'
                  '"why_wrong":"<what is wrong with the other verdict>"}',
    "multi_select": '{"type":"multi_select","question":"Which of the following … ? (select all that apply)",'
                    '"options":["","","","",""],"correct_answers":[0,2],"why_wrong":["","why B is wrong","","…",""]}',
    "fill_blank": '{"type":"fill_blank","question":"… _____ …","answer_text":"<1-4 words copied from the source>",'
                  '"accepted_answers":["<synonym/abbreviation>"]}',
    "numeric": '{"type":"numeric","numeric_answer":12.5,"unit":"%","expression":"(25/200)*100",'
               '"solution":"<one-line working>"}',
}
_TYPE_RULES = {
    "mcq": "mcq: exactly 4 distinct options, one correct.",
    "true_false": "true_false: the question is a single declarative statement; false statements must change one "
                  "specific fact from the source (a figure, a term, a direction), not be absurd.",
    "multi_select": "multi_select: 4-5 options, 2-3 of them correct; the stem says '(select all that apply)'.",
    "fill_blank": "fill_blank: the stem is a sentence from the source with ONE key term replaced by _____; the "
                  "answer is 1-4 words that appear in the source and NOT elsewhere in the stem.",
    "numeric": "numeric: a calculation a statistics officer would do (index, percentage change, mean, ratio, "
               "growth rate, weight). Give inputs in the stem, the answer as a number, and an arithmetic "
               "`expression` using only + - * / ** ( ) sqrt log that evaluates to it, with every input taken "
               "from the stem or the source. Only when the chunk has quantitative content; otherwise use another type.",
}


def _prompt(group: List[DocChunk], difficulty: str, types: List[str], n_questions: int) -> str:
    mix = difficulty_quotas(difficulty, 10)
    body = "\n\n".join(f"=== CHUNK {c.id} ({c.locator}) ===\n{c.text}" for c in group)
    return (
        "You write objective assessment questions for MoSPI (Ministry of Statistics, India) officials from a "
        "training document.\n"
        f"Write {n_questions} questions in total over the chunks below, spread across chunks, each on a different point.\n"
        f"Question types to use (mix them): {', '.join(types)}.\n"
        + "".join(f"- {_TYPE_RULES[t]}\n" for t in types) +
        f"Target difficulty {difficulty}: about {mix['Easy'] * 10}% Easy, {mix['Medium'] * 10}% Medium, "
        f"{mix['Hard'] * 10}% Hard, where Easy = {_DIFFICULTY_GUIDE['Easy']}; Medium = {_DIFFICULTY_GUIDE['Medium']}; "
        f"Hard = {_DIFFICULTY_GUIDE['Hard']}. Tag each question's own \"difficulty\" honestly.\n"
        "Rules:\n"
        "- Use ONLY facts stated in the chunks. Each question names its \"chunk\" and a \"quote\": one sentence "
        "copied VERBATIM from that chunk that supports the correct answer.\n"
        "- Test the subject matter (statistics, methods, definitions, procedures), never the document itself: no "
        "'on page 3', 'the author', 'this document'. Never mention chunk ids.\n"
        "- Distractors must be plausible to a partly-prepared reader: same kind of thing as the answer (a number for "
        "a number, a method for a method), drawn from related concepts in the text. No 'all of the above' / "
        "'none of the above', no joke options, no two options meaning the same.\n"
        "- \"why_wrong\": for every wrong option, one short sentence saying why it is wrong (the misconception it "
        "reflects); empty string for correct options.\n"
        "- \"explanation\": why the answer is right, citing the source's reasoning.\n"
        "- \"answer_type\": number, definition, concept or procedure.\n"
        "Common fields: {\"chunk\":\"c1\",\"quote\":\"...\",\"question\":\"...\",\"explanation\":\"...\","
        "\"difficulty\":\"Medium\",\"answer_type\":\"concept\"} plus the type's fields:\n"
        + "".join(f"  {_TYPE_SPEC[t]}\n" for t in types) +
        'Return JSON: {"questions":[ ... ]}\n\n' + body
    )


async def _call(group: List[DocChunk], difficulty: str, types: List[str], n_questions: int) -> List[Dict]:
    data = await gemini_json(_prompt(group, difficulty, types, n_questions))
    qs = data.get("questions", []) if isinstance(data, dict) else data if isinstance(data, list) else []
    return [q for q in qs if isinstance(q, dict)]


# ── 3. Validation ─────────────────────────────────────────────────────────────

def _tokens(s: str) -> List[str]:
    return it.normalise_text(s).split()


def quote_in_source(quote: str, source: str) -> bool:
    q, src = it.normalise_text(quote), it.normalise_text(source)
    if len(q.split()) < 4:
        return False
    if q in src:
        return True
    qt, st = _tokens(quote), set(_tokens(source))
    return sum(1 for t in qt if t in st) / len(qt) >= 0.85


def excerpt(source: str, quote: str, limit: int = 420) -> str:
    """The sentence(s) of the source that best match the quote — the passage shown to the learner."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?।])\s+|\n+", source) if s.strip()]
    if not sentences:
        return source[:limit]
    qt = set(_tokens(quote))
    best = max(range(len(sentences)), key=lambda i: len(qt & set(_tokens(sentences[i]))))
    out = sentences[best]
    j = best + 1
    while j < len(sentences) and len(out) + len(sentences[j]) < limit:
        out += " " + sentences[j]
        j += 1
    return out[:limit]


def _numberish(s: str) -> bool:
    return bool(re.search(r"\d", s)) and len(re.sub(r"[\d\s.,%₹$/\-−:]", "", s)) <= 12


def _opts(item: Dict) -> List[str]:
    raw = item.get("options") or item.get("choices") or []
    if isinstance(raw, dict):
        raw = list(raw.values())
    return [str(o).strip() for o in raw] if isinstance(raw, list) else []


def _index(v: Any, opts: List[str]) -> int:
    if isinstance(v, bool):
        return -1
    if isinstance(v, int):
        return v
    s = str(v or "").strip()
    if len(s) == 1 and s.upper() in "ABCDEF":
        return ord(s.upper()) - 65
    if s.isdigit():
        return int(s)
    return next((i for i, o in enumerate(opts) if o.lower() == s.lower()), -1)


def _why_list(item: Dict, n: int) -> List[str]:
    why = item.get("why_wrong") or []
    if isinstance(why, dict):
        why = [why.get(str(i), why.get(chr(65 + i), "")) for i in range(n)]
    if isinstance(why, str):
        why = [why] * n
    why = [str(w or "").strip() for w in why][:n]
    return why + [""] * (n - len(why))


def _computed_ok(expr: str, target: float, tol: float, allowed_numbers: set) -> Tuple[bool, str]:
    try:
        val = it.safe_eval(expr)
    except (ValueError, SyntaxError, ZeroDivisionError, OverflowError, TypeError):
        return False, "expression_invalid"
    if abs(val - target) > tol:
        return False, "expression_mismatch"
    constants = {"0", "1", "2", "3", "4", "10", "12", "100", "1000"}
    used = {n.rstrip("0").rstrip(".") if "." in n else n for n in it.expression_numbers(expr)}
    allowed = {n.rstrip("0").rstrip(".") if "." in n else n for n in allowed_numbers} | constants
    if not used <= allowed:
        return False, "expression_inputs_not_in_source"
    return True, ""


def validate(item: Dict, chunk_map: Dict[str, DocChunk], allowed: set, stats: Dict[str, int],
             allowed_types: List[str]) -> Optional[Dict[str, Any]]:
    """Returns a normalised question dict or None (reason counted in stats)."""
    def reject(reason: str):
        stats[reason] = stats.get(reason, 0) + 1
        return None

    if not isinstance(item, dict):
        return reject("malformed")
    t = it.normalise_type(item.get("type"))
    if t not in allowed_types:
        return reject("type_not_requested")
    q = " ".join(str(item.get("question") or "").split())
    expl = str(item.get("explanation") or "").strip()
    if len(q) < 12:
        return reject("empty_question")
    if _DOC_META.search(q):
        return reject("about_the_document_not_the_subject")

    # Citation: a known chunk and a verbatim quote from it.
    cid = item.get("chunk")
    if not cid and isinstance(item.get("chunks"), list) and item["chunks"]:
        cid = item["chunks"][0]
    cid = str(cid or "").strip()
    chunk = chunk_map.get(cid)
    if chunk is None or cid not in allowed:
        return reject("cited_unknown_chunk")
    quote = " ".join(str(item.get("quote") or "").split())
    if not quote:
        return reject("no_quote_cited")
    if not quote_in_source(quote, chunk.text):
        return reject("quote_not_in_source")
    source_numbers = numbers_in(chunk.text) | numbers_in(quote)

    out: Dict[str, Any] = {
        "type": t, "question": q, "options": [], "correct_answer": -1, "explanation": expl,
        "difficulty": pa.normalise_difficulty(item.get("difficulty") or item.get("level")),
        "answer_type": str(item.get("answer_type") or "concept").lower(),
        "citations": [{"chunkId": cid, "locator": chunk.locate(quote), "quote": quote,
                       "passage": excerpt(chunk.text, quote)}],
        "why_wrong": [],
    }
    if out["answer_type"] not in {"number", "definition", "concept", "procedure"}:
        out["answer_type"] = "concept"
    expr = str(item.get("expression") or "").strip()

    if t in ("mcq", "multi_select"):
        opts = _opts(item)
        lo, hi = (4, 4) if t == "mcq" else (4, 6)
        if not lo <= len(opts) <= hi or any(not o for o in opts):
            return reject("bad_options")
        norm = [it.normalise_text(o) for o in opts]
        if len(set(norm)) != len(opts):
            return reject("bad_options")
        # Options that differ only in a figure ("base year 2004" / "2012") are fine distractors.
        if any(difflib.SequenceMatcher(None, a, b).ratio() >= 0.9 and numbers_in(a) == numbers_in(b)
               for i, a in enumerate(norm) for b in norm[i + 1:]):
            return reject("near_duplicate_options")
        if any(_CATCH_ALL.search(o) for o in opts):
            return reject("catch_all_option")
        if t == "mcq":
            ans = _index(item.get("correct_answer"), opts)
            if not 0 <= ans < 4:
                return reject("bad_answer_index")
            correct = [ans]
        else:
            raw = item.get("correct_answers") or item.get("correct_answer") or []
            raw = raw if isinstance(raw, list) else [raw]
            correct = sorted({_index(v, opts) for v in raw})
            if any(not 0 <= c < len(opts) for c in correct) or not 2 <= len(correct) <= len(opts) - 1:
                return reject("bad_answer_index")
        wrong = [i for i in range(len(opts)) if i not in correct]
        right_opts = [opts[i] for i in correct]
        # Distractor plausibility (surface checks; semantic ones run in plausibility_and_dedup).
        if t == "mcq":
            longest_wrong = max(len(opts[i]) for i in wrong)
            if len(opts[ans]) > 2.2 * longest_wrong and len(opts[ans]) - longest_wrong >= 30:
                return reject("answer_length_giveaway")
        if all(_numberish(o) for o in right_opts) and any(not re.search(r"\d", opts[i]) for i in wrong):
            return reject("implausible_distractor_type")
        # Figures in the answer must be in the source, or computed by a checked expression.
        for o in right_opts:
            nums = numbers_in(o) - numbers_in(q)
            if nums and not nums <= source_numbers:
                target = it.parse_number(o)
                ok = bool(expr) and target is not None and \
                    _computed_ok(expr, target, max(0.01 * abs(target), 0.005), source_numbers | numbers_in(q))[0]
                if not ok:
                    return reject("answer_number_not_in_source")
        out.update(options=opts, correct_answer=correct[0] if t == "mcq" else -1,
                   correct_answers=correct if t == "multi_select" else None,
                   why_wrong=_why_list(item, len(opts)))
        for i in correct:
            out["why_wrong"][i] = ""

    elif t == "true_false":
        v = item.get("correct_answer", item.get("answer"))
        if isinstance(v, str):
            v = {"true": True, "false": False, "0": True, "1": False, "t": True, "f": False}.get(v.strip().lower())
        elif isinstance(v, int) and not isinstance(v, bool):
            v = {0: True, 1: False}.get(v)
        if not isinstance(v, bool):
            return reject("bad_answer_index")
        if v:
            nums = numbers_in(q)
            if nums and not nums <= source_numbers:
                return reject("answer_number_not_in_source")
        elif len(expl) < 15:
            return reject("false_statement_without_correction")
        why = item.get("why_wrong")
        why = why if isinstance(why, str) else (" ".join(str(w) for w in why if w) if isinstance(why, list) else "")
        wrong_idx = 1 if v else 0
        out.update(options=list(it.TRUE_FALSE_OPTIONS), correct_answer=0 if v else 1,
                   why_wrong=["", ""])
        out["why_wrong"][wrong_idx] = why.strip() or expl

    elif t == "fill_blank":
        if not it.has_blank(q) or len(it._BLANK_RE.findall(q)) != 1:
            return reject("fill_blank_needs_one_blank")
        q = it.with_canonical_blank(q)
        ans = " ".join(str(item.get("answer_text") or item.get("answer") or "").split())
        if not ans or len(ans.split()) > 6:
            return reject("fill_blank_bad_answer")
        stem_wo_blank = it.normalise_text(q.replace(it.BLANK, " "))
        if re.search(r"(?<!\w)" + re.escape(it.normalise_text(ans)) + r"(?!\w)", stem_wo_blank):
            return reject("fill_blank_answer_in_stem")
        if it.normalise_text(ans) not in it.normalise_text(chunk.text):
            return reject("fill_blank_answer_not_in_source")
        acc = item.get("accepted_answers") or []
        acc = [" ".join(str(a).split()) for a in (acc if isinstance(acc, list) else [acc])]
        acc = [a for a in acc if a and len(a.split()) <= 6 and it.normalise_text(a) != it.normalise_text(ans)][:5]
        out.update(question=q, answer_text=ans, accepted_answers=acc)
        if out["answer_type"] == "concept":
            out["answer_type"] = "definition"

    elif t == "numeric":
        ans = it.parse_number(item.get("numeric_answer", item.get("answer")))
        if ans is None:
            return reject("numeric_bad_answer")
        unit = str(item.get("unit") or "").strip()[:20]
        probe = {"numeric_answer": ans, "tolerance": item.get("tolerance")}
        tol = it.numeric_tolerance(probe)
        if expr:
            ok, why = _computed_ok(expr, ans, tol, source_numbers | numbers_in(q))
            if not ok:
                return reject(why)
        elif not numbers_in(f"{ans:g}") <= source_numbers:
            return reject("numeric_answer_unverifiable")
        try:
            given_tol = abs(float(item.get("tolerance") or 0))
        except (TypeError, ValueError):
            given_tol = 0.0
        out.update(numeric_answer=ans, unit=unit, tolerance=given_tol or None, expression=expr or None,
                   solution=str(item.get("solution") or "").strip() or None, answer_type="number")

    if _INTERNAL_REF.search(" ".join([q, expl] + out["options"])):
        return reject("mentions_internal_ids")
    if not out["explanation"]:
        out["explanation"] = f"The source ({chunk.locator}) states: “{quote}”"
    return out


# ── 4. Plausibility + dedup ───────────────────────────────────────────────────

def _jaccard(a: str, b: str) -> float:
    x, y = set(_tokens(a)), set(_tokens(b))
    return len(x & y) / len(x | y) if x and y else 0.0


DISTRACTOR_FLOOR = 0.72      # e5 cosines are compressed high; below this a distractor is off-topic
PARAPHRASE_CEIL = 0.97       # a distractor this close to the answer is probably also correct
DUPLICATE_STEM = 0.93


def plausibility_and_dedup(cands: List[Dict[str, Any]], stats: Dict[str, int]) -> Tuple[List[Dict[str, Any]], str]:
    """Sync (run in a worker thread). Returns (kept candidates, method used)."""
    def reject(reason: str):
        stats[reason] = stats.get(reason, 0) + 1

    method = "lexical"
    stem_vecs = None
    try:
        import numpy as np
        from ai.embedder import get_embedder

        emb = get_embedder("chat")
        stems = [c["question"] for c in cands]
        stem_vecs = np.asarray(emb.encode(stems, kind="query", normalize_embeddings=True,
                                          show_progress_bar=False), dtype="float32")
        # Option texts (choice types, non-numeric options only).
        opt_rows = [(ci, oi, o) for ci, c in enumerate(cands) if c["type"] in ("mcq", "multi_select")
                    for oi, o in enumerate(c["options"]) if not _numberish(o)]
        if opt_rows:
            ov = np.asarray(emb.encode([o for *_, o in opt_rows], kind="passage", normalize_embeddings=True,
                                       show_progress_bar=False), dtype="float32")
            vec = {(ci, oi): ov[k] for k, (ci, oi, _) in enumerate(opt_rows)}
            bad = set()
            for ci, c in enumerate(cands):
                if c["type"] not in ("mcq", "multi_select"):
                    continue
                right = [c["correct_answer"]] if c["type"] == "mcq" else c["correct_answers"]
                for oi in range(len(c["options"])):
                    if oi in right or (ci, oi) not in vec:
                        continue
                    if float(vec[(ci, oi)] @ stem_vecs[ci]) < DISTRACTOR_FLOOR:
                        bad.add((ci, "distractor_off_topic"))
                    if any((ci, r) in vec and float(vec[(ci, oi)] @ vec[(ci, r)]) >= PARAPHRASE_CEIL for r in right):
                        bad.add((ci, "distractor_paraphrases_answer"))
            drop = {}
            for ci, reason in bad:
                drop.setdefault(ci, reason)
            for ci, reason in drop.items():
                reject(reason)
            keep_idx = [i for i in range(len(cands)) if i not in drop]
            cands = [cands[i] for i in keep_idx]
            stem_vecs = stem_vecs[keep_idx]
        method = "embedding"
    except Exception as exc:
        logger.info("[doc-quiz] embedder unavailable, lexical dedup only: %s", exc)
        stem_vecs = None

    kept: List[int] = []
    for i, c in enumerate(cands):
        dup = False
        for j in kept:
            d = cands[j]
            same_stem = (float(stem_vecs[i] @ stem_vecs[j]) >= DUPLICATE_STEM if stem_vecs is not None
                         else _jaccard(c["question"], d["question"]) >= 0.6)
            same_fact = (c["citations"][0]["chunkId"] == d["citations"][0]["chunkId"]
                         and it.normalise_text(it.correct_display(c)) == it.normalise_text(it.correct_display(d))
                         and _jaccard(c["question"], d["question"]) >= 0.35)
            if same_stem or same_fact:
                dup = True
                break
        if dup:
            reject("duplicate")
        else:
            kept.append(i)
    return [cands[i] for i in kept], method


# ── 5. Selection ──────────────────────────────────────────────────────────────

def select(cands: List[Dict[str, Any]], n: int, types: List[str], difficulty: str) -> List[Dict[str, Any]]:
    tq = type_quotas(types, n)
    dq = difficulty_quotas(difficulty, n)
    chosen: List[Dict[str, Any]] = []
    pool = list(enumerate(cands))
    used_chunks: Dict[str, int] = {}
    while pool and len(chosen) < n:
        tc = {t: sum(1 for c in chosen if c["type"] == t) for t in types}
        dc = {d: sum(1 for c in chosen if c["difficulty"] == d) for d in pa.DIFFICULTIES}

        def rank(entry):
            order, c = entry
            return (0 if tc.get(c["type"], 0) < tq.get(c["type"], 0) else 1,
                    0 if dc.get(c["difficulty"], 0) < dq.get(c["difficulty"], 0) else 1,
                    used_chunks.get(c["citations"][0]["chunkId"], 0),
                    order)
        best = min(pool, key=rank)
        pool.remove(best)
        chosen.append(best[1])
        cid = best[1]["citations"][0]["chunkId"]
        used_chunks[cid] = used_chunks.get(cid, 0) + 1
    return chosen


def shuffle_options(q: Dict[str, Any]) -> Dict[str, Any]:
    """LLMs favour the first slot — shuffle choice options deterministically (not T/F)."""
    if q["type"] not in ("mcq", "multi_select"):
        return q
    order = list(range(len(q["options"])))
    random.Random(q["question"]).shuffle(order)
    q["options"] = [q["options"][i] for i in order]
    q["why_wrong"] = [q["why_wrong"][i] for i in order]
    if q["type"] == "mcq":
        q["correct_answer"] = order.index(q["correct_answer"])
    else:
        q["correct_answers"] = sorted(order.index(i) for i in q["correct_answers"])
    return q


# ── 7. Translation ────────────────────────────────────────────────────────────

async def translate(questions: List[Dict[str, Any]], lang: str = "hi") -> Dict[str, Any]:
    slots: List[Tuple[int, str, int]] = []
    texts: List[str] = []

    def add(qi: int, field: str, idx: int, val: Any):
        if val:
            slots.append((qi, field, idx))
            texts.append(str(val))

    for qi, q in enumerate(questions):
        add(qi, "question", -1, q["question"])
        add(qi, "explanation", -1, q["explanation"])
        if q["type"] in ("mcq", "multi_select"):
            for oi, o in enumerate(q["options"]):
                add(qi, "options", oi, o)
        for wi, w in enumerate(q.get("why_wrong") or []):
            add(qi, "why_wrong", wi, w)
        if q["type"] == "fill_blank":
            add(qi, "answer_text", -1, q.get("answer_text"))
        if q["type"] == "numeric":
            add(qi, "unit", -1, q.get("unit"))
            add(qi, "solution", -1, q.get("solution"))

    out, report = await translate_texts(texts, lang)
    if out is None:
        return report
    for q in questions:
        tr: Dict[str, Any] = {"options": list(q["options"]), "why_wrong": list(q.get("why_wrong") or [])}
        if q["type"] == "true_false":
            tr["options"] = ["सही", "गलत"] if lang == "hi" else list(q["options"])
        q.setdefault("translations", {})[lang] = tr
    for (qi, field, idx), val in zip(slots, out):
        tr = questions[qi]["translations"][lang]
        if idx >= 0:
            tr[field][idx] = val
        else:
            tr[field] = val
    lost_blank = 0
    for q in questions:
        tr = q["translations"][lang]
        if q["type"] == "fill_blank":
            if it.has_blank(tr.get("question", "")):
                tr["question"] = it.with_canonical_blank(tr["question"])
            else:
                tr["question"] = q["question"]          # the blank did not survive — keep English
                lost_blank += 1
    report["fill_blank_kept_english"] = lost_blank
    return report


# ── Orchestration ─────────────────────────────────────────────────────────────

async def generate(text: str, raw_chunks: List[str], difficulty: str = "Medium", n_questions: int = 5,
                   types: Optional[List[str]] = None, language: str = "en") -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    difficulty = pa.normalise_difficulty(difficulty)
    n = max(MIN_QUESTIONS, min(MAX_QUESTIONS, int(n_questions or 5)))
    types = parse_types(types or ["mcq"])
    language = language if language in LANGUAGES else "en"

    all_chunks = locate_chunks(text, raw_chunks or [text[:4000]])
    chosen_chunks = select_chunks(all_chunks, n)
    report: Dict[str, Any] = {"requested": n, "types_requested": list(types), "language": language,
                              "chunks_total": len(all_chunks), "chunks_used": len(chosen_chunks)}
    if "numeric" in types and not _quantitative(chosen_chunks):
        types = [t for t in types if t != "numeric"] or ["mcq"]
        report["numeric_skipped"] = "The selected passages have too few figures for calculation questions."
    report["types_used"] = list(types)

    chunk_map = {c.id: c for c in chosen_chunks}
    groups = [chosen_chunks[i:i + CHUNKS_PER_CALL] for i in range(0, len(chosen_chunks), CHUNKS_PER_CALL)]
    per_group = [max(2, math.ceil(n * OVERGENERATE * len(g) / len(chosen_chunks))) for g in groups]
    results = await asyncio.gather(*[_call(g, difficulty, types, k) for g, k in zip(groups, per_group)],
                                   return_exceptions=True)
    errors = [r for r in results if isinstance(r, Exception)]
    if errors and len(errors) == len(results):
        raise errors[0] if isinstance(errors[0], LLMUnavailable) else LLMUnavailable(str(errors[0]))
    for e in errors:
        logger.warning("[doc-quiz] a generation call failed: %s", e)

    stats: Dict[str, int] = {}
    cands: List[Dict[str, Any]] = []
    raw = 0
    for g, res in zip(groups, results):
        if isinstance(res, Exception):
            continue
        allowed = {c.id for c in g}
        for item in res:
            raw += 1
            q = validate(item, chunk_map, allowed, stats, types)
            if q:
                cands.append(q)

    cands, method = await asyncio.to_thread(plausibility_and_dedup, cands, stats)
    chosen = [shuffle_options(q) for q in select(cands, n, types, difficulty)]

    fc = {"checked": 0, "flagged": 0, "ok": 0, "no_reference": 0}
    for q in chosen:
        q["review"], bucket = review_answer(q["question"], it.correct_display(q), q["answer_type"])
        if bucket != "skipped":
            fc["checked"] += 1
            fc[bucket] += 1

    report.update({
        "raw_candidates": raw, "valid_candidates": len(cands), "accepted": len(chosen),
        "rejected": stats, "rejected_total": sum(stats.values()), "plausibility_check": method,
        "type_counts": {t: sum(1 for q in chosen if q["type"] == t) for t in types},
        "difficulty_counts": {d: sum(1 for q in chosen if q["difficulty"] == d) for d in pa.DIFFICULTIES},
        "fact_check": fc, "llm_errors": len(errors),
    })
    if language in ("hi", "bi") and chosen:
        report["translation"] = await translate(chosen, "hi")
    return chosen, report
