"""
FILE: services/media_quiz/fact_check.py
─────────────────────────────────────────────────────────────────────────────
Step 5: flag speaker errors and protect terms.

Fact-check (flaw 11): a question whose answer is a number or a definition is
matched (keyword hits) against a small reference set — reference_facts.json,
seeded from the CPI handbook / NSSO / NAS facts, to be extended with the NSSO
manuals and the MoSPI glossary. If the answer's figures are not among the
figures the reference accepts, the question is FLAGGED for the trainer (the
speaker may have misspoken); it is never silently rejected.

Translation (flaw 13): glossary terms are replaced by placeholders ⟦T1⟧, ⟦T2⟧…
before translating and restored afterwards, so "Laspeyres", "PLFS" or
"base year" are not mistranslated. A field whose placeholders do not survive
translation keeps its original text.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import logging
import os
import re
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

from services.media_quiz.llm import LLMUnavailable, gemini_json
from services.media_quiz.question_gen import MediaQuestion, numbers_in

logger = logging.getLogger(__name__)

_REF_PATH = os.path.join(os.path.dirname(__file__), "reference_facts.json")
LANG_NAMES = {"hi": "Hindi", "bn": "Bengali", "ta": "Tamil", "te": "Telugu", "mr": "Marathi",
              "gu": "Gujarati", "kn": "Kannada", "ml": "Malayalam", "or": "Odia", "pa": "Punjabi"}


@lru_cache(maxsize=1)
def _reference() -> Dict:
    try:
        with open(_REF_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as exc:
        logger.warning("[fact-check] reference set unavailable: %s", exc)
        return {"facts": [], "glossary_terms": []}


def _match(text: str) -> Tuple[Dict, int]:
    low = text.lower()
    best, best_hits = {}, 0
    for fact in _reference().get("facts", []):
        hits = sum(1 for k in fact.get("keywords", []) if re.search(r"\b" + re.escape(k) + r"\b", low))
        if hits >= fact.get("min_hits", 1) and hits > best_hits:
            best, best_hits = fact, hits
    return best, best_hits


def review_answer(question: str, answer: str, answer_type: str) -> Tuple[Dict, str]:
    """Fact-check one answer. Returns (review dict, summary bucket) where the bucket is
    "skipped" (not a number/definition), "no_reference", "flagged" or "ok".
    Shared by the media and the document quiz (services/doc_quiz)."""
    nums = numbers_in(answer)
    if answer_type not in {"number", "definition"} and not nums:
        return {"status": "unchecked"}, "skipped"
    fact, _ = _match(f"{question} {answer}")
    if not fact:
        return {"status": "no_reference", "note": "No reference entry covers this; trainer may verify."}, "no_reference"
    accepted = {n for v in fact.get("numbers", []) for n in numbers_in(v)}
    if nums and accepted and not nums & accepted:
        return {
            "status": "flagged",
            "reference_id": fact["id"],
            "note": (f"Answer states {', '.join(sorted(nums))}, but the reference ({fact.get('source')}) says: "
                     f"{fact['statement']} The source may be wrong or outdated — please review."),
        }, "flagged"
    return {"status": "ok", "reference_id": fact["id"], "note": fact["statement"]}, "ok"


def fact_check(questions: List[MediaQuestion]) -> Dict[str, int]:
    summary = {"checked": 0, "flagged": 0, "ok": 0, "no_reference": 0}
    for q in questions:
        review, bucket = review_answer(q.question, q.options[q.correct_answer], q.answer_type)
        if bucket == "skipped":
            continue
        summary["checked"] += 1
        summary[bucket] += 1
        if bucket == "flagged":
            review["note"] = review["note"].replace("The source may be wrong or outdated", "The speaker may have misspoken")
        q.review = review
    return summary


# ── Term-protected translation ───────────────────────────────────────────────

def protect_terms(text: str, terms: List[str]) -> Tuple[str, Dict[str, str]]:
    mapping: Dict[str, str] = {}
    # Longest first so "SNA 2008" wins over "SNA".
    for term in sorted(set(terms), key=len, reverse=True):
        pattern = re.compile(r"(?<![\w⟦])" + re.escape(term) + r"(?![\w⟧])", re.I)
        def repl(m):
            key = f"⟦T{len(mapping) + 1}⟧"
            mapping[key] = m.group(0)
            return key
        text = pattern.sub(repl, text)
    return text, mapping


def restore_terms(text: str, mapping: Dict[str, str]) -> Tuple[str, bool]:
    ok = all(k in text for k in mapping)
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text, ok


async def translate_texts(texts: List[str], target_lang: str) -> Tuple[Optional[List[str]], Dict]:
    """Translate strings with glossary terms protected as ⟦Tn⟧. Returns (translations in
    order | None on failure, report). A string whose placeholders are lost keeps its
    original text. Shared by the media and the document quiz."""
    name = LANG_NAMES.get(target_lang)
    if not name or not texts:
        return None, {"target": target_lang, "status": "skipped"}
    terms = _reference().get("glossary_terms", [])
    protected, maps = [], []
    for val in texts:
        t, m = protect_terms(val, terms)
        protected.append(t)
        maps.append(m)

    prompt = (
        f"Translate each string in the JSON array into {name}. Keep every placeholder like ⟦T1⟧ exactly as is "
        "(same characters, same count), keep numbers and units unchanged. "
        'Return JSON: {"translations": ["...", ...]} with the same length and order.\n\n'
        + json.dumps(protected, ensure_ascii=False)
    )
    try:
        data = await gemini_json(prompt, temperature=0.1)
    except LLMUnavailable as exc:
        return None, {"target": target_lang, "status": f"failed: {exc}"}
    out = data.get("translations") if isinstance(data, dict) else data
    if not isinstance(out, list) or len(out) != len(texts):
        return None, {"target": target_lang, "status": "failed: length mismatch"}

    kept_original = 0
    result = []
    for tr, m, orig in zip(out, maps, protected):
        restored, ok = restore_terms(str(tr), m)
        if not ok:
            restored, _ = restore_terms(orig, m)
            kept_original += 1
        result.append(restored)
    return result, {"target": target_lang, "status": "ok", "fields": len(texts),
                    "fields_kept_in_english_placeholder_lost": kept_original}


async def translate_questions(questions: List[MediaQuestion], target_lang: str) -> Dict:
    if not LANG_NAMES.get(target_lang) or not questions:
        return {"target": target_lang, "status": "skipped"}
    fields: List[Tuple[int, str, int]] = []       # (question index, field, option index)
    texts: List[str] = []
    for qi, q in enumerate(questions):
        for fname, oi, val in [("question", -1, q.question), ("explanation", -1, q.explanation)] + \
                              [("option", i, o) for i, o in enumerate(q.options)]:
            fields.append((qi, fname, oi))
            texts.append(val)

    out, report = await translate_texts(texts, target_lang)
    if out is None:
        return report
    for (qi, fname, oi), restored in zip(fields, out):
        q = questions[qi]
        if fname == "question":
            q.question = restored
        elif fname == "explanation":
            q.explanation = restored
        else:
            q.options[oi] = restored
    return report
