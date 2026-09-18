"""Prompts for grounded MCQ generation and the blind cross-check."""

from __future__ import annotations

import json

from ai.quiz.passages import Passage

DIFFICULTY_RUBRIC = {
    "Easy": (
        "EASY: mostly 'recall' and 'understand' questions — direct facts, definitions, "
        "who/what/which as stated. Distractors are clearly different but same type."
    ),
    "Medium": (
        "MEDIUM: mix of 'understand' and 'apply'. Ask the learner to interpret a definition, "
        "pick the example that fits a stated concept, relate two facts stated in the passage, "
        "or choose the correct method for a situation the passage describes. At most two plain recall questions. "
        "Distractors are plausible: related terms, near-miss figures or common misconceptions."
    ),
    "Hard": (
        "HARD: mostly 'apply' and 'analyse'. Use short scenarios (\"An officer needs to…; based on the "
        "document, which approach/value/conclusion is correct?\"), computations using figures or formulas "
        "stated in the passage, consequences of a stated rule, or combining two statements from the same "
        "passage. At most one recall question. Distractors must be close: the right idea applied wrongly, "
        "a correct fact that does not answer this question, or an off-by-one-step calculation."
    ),
}

GENERATE_SYSTEM = (
    "You are a senior assessment designer for India's Ministry of Statistics and Programme "
    "Implementation (MoSPI), writing multiple-choice questions for government officials. "
    "Every question must be answerable from the supplied passages alone. You never use outside "
    "knowledge, even when it is true, and you never invent figures, names, years or definitions. "
    "You reply with a single JSON object and nothing else."
)

_RULES = """Rules:
1. Ground every question in exactly one passage (source_id). The correct option must be provably
   right from that passage alone; each distractor must be wrong or unsupported by it.
2. "evidence" is copied VERBATIM (character-for-character) from that passage: the 1-2 sentences
   that prove the answer. Do not paraphrase, merge or shorten words inside it.
3. Exactly 4 options, one correct. Options are similar in length, style and type (all years, all
   methods, all organisations…); the correct option must not be noticeably longer or the only one copied
   from the document, so it cannot be spotted by its wording. Never use "All of the above", "None of the above", "Both A and B".
   A distractor must never be a synonym, alternative name, rounding or superset of the correct answer
   (e.g. not "Employment-to-population ratio" beside "Worker population ratio"), and must be something
   a subject expert would call wrong.
4. The stem is self-contained and must not contain the answer's key words. Do not mention "passage",
   "P1" or chunk numbers; you may say "according to the document".
5. Never ask about headings, page numbers, authors, file names, or the document itself.
6. Each question tests a different fact; spread questions across different passages.
7. Avoid negative stems ("Which is NOT…") unless the passage explicitly lists the complete set.
8. "explanation": 1-2 sentences saying why the answer is right and why the most tempting distractor is wrong,
   using only the passage."""

_SCHEMA = """Return JSON exactly in this shape:
{"questions": [
  {"source_id": "P3",
   "bloom_level": "recall | understand | apply | analyse",
   "question": "...",
   "options": ["...", "...", "...", "..."],
   "correct_answer": 0,
   "evidence": "verbatim sentence(s) from P3",
   "explanation": "..."}
]}"""


def format_passages(passages: list[Passage]) -> str:
    return "\n\n".join(f"[{p.id}]\n{p.text.strip()}" for p in passages)


def generation_prompt(passages: list[Passage], count: int, difficulty: str, avoid: list[str] | None = None) -> str:
    rubric = DIFFICULTY_RUBRIC.get(difficulty, DIFFICULTY_RUBRIC["Medium"])
    avoid_block = ""
    if avoid:
        listed = "\n".join(f"- {q}" for q in avoid)
        avoid_block = f"\nThese questions already exist; do NOT repeat or rephrase them:\n{listed}\n"
    return (
        f"Write {count} multiple-choice questions from the passages below.\n\n"
        f"Difficulty — {rubric}\n\n{_RULES}\n{avoid_block}\n{_SCHEMA}\n\n"
        f"PASSAGES:\n{format_passages(passages)}"
    )


CHECK_SYSTEM = (
    "You are a meticulous exam checker. You answer each multiple-choice question using ONLY the "
    "passage attached to it, ignoring anything you know from elsewhere. If the passage does not "
    "establish exactly one correct option (none is supported, or two or more could be right), you "
    "answer -1. Also answer -1 when another option is merely a different name, synonym or rounding "
    "of the best option, so an expert could defend it as correct. For calculations, work the numbers "
    "out yourself. You reply with a single JSON object and nothing else."
)


def check_prompt(items: list[dict]) -> str:
    """items: [{"id": "q1", "passage": str, "question": str, "options": [...]}]"""
    payload = [
        {
            "id": it["id"],
            "passage": it["passage"],
            "question": it["question"],
            "options": {str(i): opt for i, opt in enumerate(it["options"])},
        }
        for it in items
    ]
    return (
        "Answer every question below using only its own passage.\n"
        "For each question, first judge EVERY option: list in \"defensible\" all option numbers an expert "
        "could defend as correct (synonyms and alternative names of the right answer count as correct). "
        "Then give \"answer\": the single best option, or -1 if \"defensible\" does not contain exactly one option.\n"
        'Return: {"answers": [{"id": "q1", "defensible": [<option numbers>], "answer": <0-3 or -1>, '
        '"reason": "<one short sentence>"}]}\n\n'
        + json.dumps(payload, ensure_ascii=False, indent=1)
    )
