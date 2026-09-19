"""
FILE: services/practice_assessment.py
─────────────────────────────────────────────────────────────────────────────
Quiz → skill-gap bridge for the Assessment Studio (document, video, audio and
YouTube quizzes all grade through routers/rag.py::/grade).

A quiz no longer just "passes or doesn't". Every first attempt moves a
per-competency PRACTICE ABILITY θ on the FRAC 0–5 scale, question by question,
with a difficulty-aware (Elo / 1-PL IRT style) update:

    P(correct) = 1 / (1 + exp(-A · (θ − b_q)))      b_q = item difficulty
    θ ← θ + k · (y − P)                              y = 1 if correct else 0

so, for the same learner:
  • failing an EASY question costs more  (P was high → y − P very negative)
  • failing a HARD question costs little (P was low  → y − P slightly negative)
  • solving a HARD question gains more   (P was low  → y − P large)
  • solving an EASY question gains a little.

The new θ is written as the PRACTICE_ASSESSMENT EvidenceLog value; the
baseline assembler reads the LATEST practice value into the documented channel
(see baseline_assembler.py), so a quiz nudges the learner's skill score up or
down by a bounded amount. Floors (completed courses, work samples,
self-report) still hold — one bad quiz never erases a completed course.

Pure functions only (no DB / HTTP) so the maths is unit-testable.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import math
import re
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

DIFFICULTIES = ("Easy", "Medium", "Hard")

# Item difficulty on the FRAC level scale (what a learner at this level answers ~50%).
ITEM_DIFFICULTY_B = {"Easy": 1.5, "Medium": 2.5, "Hard": 3.5}
# Weight of a question in the difficulty-weighted score.
SCORE_WEIGHT = {"Easy": 1.0, "Medium": 1.5, "Hard": 2.0}

DISCRIMINATION_A = 1.7      # logistic slope (≈ normal-ogive scaling)
QUIZ_STEP = 0.8             # total step size per quiz, split across its questions
MAX_QUIZ_MOVE = 0.6         # hard cap on |Δθ| from one quiz
THETA_MIN, THETA_MAX = 0.5, 5.0   # θ stays > 0 so the channel never reads as "absent"
DEFAULT_PRIOR = 2.0         # starting θ when nothing is known about the learner
PASS_THRESHOLD = 70.0


def normalise_difficulty(value: Any, default: str = "Medium") -> str:
    s = str(value or "").strip().lower()
    for d in DIFFICULTIES:
        if s == d.lower() or s.startswith(d.lower()[:3]):
            return d
    if s in {"beginner", "basic", "low", "simple"}:
        return "Easy"
    if s in {"intermediate", "moderate", "mid", "average"}:
        return "Medium"
    if s in {"advanced", "difficult", "high", "expert", "tough"}:
        return "Hard"
    return default


def bump(difficulty: str, steps: int = 1) -> str:
    i = DIFFICULTIES.index(normalise_difficulty(difficulty)) + steps
    return DIFFICULTIES[max(0, min(len(DIFFICULTIES) - 1, i))]


def media_question_difficulty(quiz_difficulty: str, kind: str) -> str:
    """Media quizzes carry one target difficulty; a synthesis question (must join
    ≥2 parts of the video) is one step harder than a single-chunk question."""
    return bump(quiz_difficulty, 1) if kind == "synthesis" else normalise_difficulty(quiz_difficulty)


def p_correct(theta: float, difficulty: str) -> float:
    b = ITEM_DIFFICULTY_B[normalise_difficulty(difficulty)]
    return 1.0 / (1.0 + math.exp(-DISCRIMINATION_A * (theta - b)))


def update_ability(theta0: float, results: List[Dict[str, Any]]) -> Tuple[float, List[Dict[str, Any]]]:
    """
    results: [{"difficulty": "Easy|Medium|Hard", "correct": bool}, ...] in question order.
    Returns (θ after, per-question [{difficulty, correct, expected, delta}]).
    """
    theta = min(THETA_MAX, max(THETA_MIN, float(theta0)))
    start = theta
    k = min(0.25, QUIZ_STEP / max(1, len(results)))   # 0.16 per question for a 5-question quiz
    trace = []
    for r in results:
        d = normalise_difficulty(r.get("difficulty"))
        p = p_correct(theta, d)
        y = 1.0 if r.get("correct") else 0.0
        delta = k * (y - p)
        theta = min(THETA_MAX, max(THETA_MIN, theta + delta))
        trace.append({"difficulty": d, "correct": bool(y), "expected": round(p, 3), "delta": round(delta, 3)})
    # One quiz is a small sample — bound its total influence.
    moved = max(-MAX_QUIZ_MOVE, min(MAX_QUIZ_MOVE, theta - start))
    return round(start + moved, 3), trace


def weighted_score(results: List[Dict[str, Any]]) -> float:
    """Difficulty-weighted percentage: a Hard question is worth 2× an Easy one."""
    total = sum(SCORE_WEIGHT[normalise_difficulty(r.get("difficulty"))] for r in results)
    got = sum(SCORE_WEIGHT[normalise_difficulty(r.get("difficulty"))] for r in results if r.get("correct"))
    return round(100.0 * got / total, 2) if total else 0.0


def latest_practice_value(rows: Iterable[Dict[str, Any]]) -> Tuple[float, Optional[datetime]]:
    """(value, date) of the newest PRACTICE_ASSESSMENT row; (0.0, None) when there is none."""
    best: Tuple[datetime, float, Optional[datetime]] = (datetime.min, 0.0, None)
    for r in rows:
        if (r.get("evidence_type") or r.get("evidenceType")) != "PRACTICE_ASSESSMENT":
            continue
        val = float(r.get("granted_value") or r.get("grantedValue") or 0)
        d = r.get("issue_date") or r.get("issueDate")
        if d is not None and not isinstance(d, datetime):
            try:
                d = datetime.fromisoformat(str(d).replace("Z", "+00:00"))
            except ValueError:
                d = None
        if d is not None and d.tzinfo is not None:
            d = d.replace(tzinfo=None)
        if val > 0 and (d or datetime.min) >= best[0]:     # ties → the later row wins
            best = (d or datetime.min, val, d)
    return best[1], best[2]


def starting_ability(prior_practice: float, row: Optional[Dict[str, Any]]) -> Tuple[float, str]:
    """Where the quiz update starts: last practice θ → current fused score → level → prior."""
    if prior_practice > 0:
        return prior_practice, "previous_practice"
    if row:
        if row.get("confidence") not in (None, "UNASSESSED") and float(row.get("rawScore") or 0) > 0:
            return float(row["rawScore"]), "current_skill_score"
        if row.get("currentLevel") is not None:
            return float(row["currentLevel"]), "current_level"
    return DEFAULT_PRIOR, "default_prior"


# ── Competency linking ────────────────────────────────────────────────────────

_STOP = {"and", "the", "for", "of", "in", "to", "a", "an", "with", "on", "management", "skills",
         "general", "data", "official", "officials", "use", "using"}


def _tokens(text: str) -> set:
    return {t for t in re.findall(r"[a-z][a-z0-9+#]{2,}", (text or "").lower()) if t not in _STOP}


def link_competency(rows: List[Dict[str, Any]], quiz: Dict[str, Any],
                    descriptions: Optional[Dict[str, str]] = None) -> Tuple[Optional[Dict[str, Any]], str, float]:
    """
    Pick which of the learner's ROLE competencies this quiz is evidence for.
      1. the quiz's FRAC tag equals the row's id or crosswalked catalogue id;
      2. multilingual-e5 similarity (shared "chat" embedder) between the quiz
         content and "name. description" of each role competency;
      3. keyword overlap as an offline fallback.
    Returns (row | None, method, similarity).
    """
    if not rows:
        return None, "none", 0.0
    descriptions = descriptions or {}
    tag = quiz.get("competency_id")
    if tag:
        for r in rows:
            if tag in (r.get("competencyId"), r.get("catalogueId")):
                return r, "frac_tag", 1.0

    questions = quiz.get("questions") or []
    q_text = " ".join(getattr(q, "question", "") or (q.get("question", "") if isinstance(q, dict) else "")
                      for q in questions)
    quiz_text = f"{quiz.get('skill_name') or ''}. {q_text} {(quiz.get('extracted_text') or '')[:1500]}".strip()

    def comp_text(r):
        key = r.get("catalogueId") or r.get("competencyId")
        return f"{r.get('name', '')}. {descriptions.get(key, '')}".strip()

    try:
        import numpy as np
        from ai.embedder import get_embedder

        emb = get_embedder("chat")
        qv = np.asarray(emb.encode([quiz_text[:2000]], kind="query", normalize_embeddings=True,
                                   show_progress_bar=False), dtype="float32")
        cv = np.asarray(emb.encode([comp_text(r) for r in rows], kind="passage", normalize_embeddings=True,
                                   show_progress_bar=False), dtype="float32")
        sims = (cv @ qv[0]).tolist()
        j = max(range(len(rows)), key=lambda i: sims[i])
        if sims[j] >= 0.72:          # e5 cosines are compressed high; below this it's unrelated
            return rows[j], "semantic", round(float(sims[j]), 3)
    except Exception:
        pass

    qt = _tokens(quiz_text)
    scored = [(len(qt & _tokens(comp_text(r))), r) for r in rows]
    overlap, best = max(scored, key=lambda s: s[0])
    if overlap >= 1:
        return best, "keyword", float(overlap)
    return None, "none", 0.0


# ── Recommendations ───────────────────────────────────────────────────────────

def next_difficulty(current: str, weighted: float) -> Tuple[str, str]:
    current = normalise_difficulty(current)
    if weighted >= 85 and current != "Hard":
        return bump(current, 1), "Strong result — step up the difficulty to keep growing."
    if weighted < 50 and current != "Easy":
        return bump(current, -1), "Consolidate the basics at a lower difficulty before stepping up again."
    return current, ("Stay at this level and aim for 85%+ before moving up."
                     if weighted < 85 else "You are at the top difficulty — keep practising new material.")


def review_topics(questions: List[Any], answers: List[int], difficulties: List[str]) -> List[Dict[str, Any]]:
    """Per-question review, missed ones first. Reads QuizQuestion objects or dicts."""
    out = []
    for i, q in enumerate(questions):
        get = (lambda k, q=q: getattr(q, k, None)) if not isinstance(q, dict) else q.get
        opts = get("options") or []
        correct_idx = int(get("correct_answer") or 0)
        chosen = answers[i] if i < len(answers) else -1
        out.append({
            "index": i,
            "question": get("question") or "",
            "difficulty": difficulties[i] if i < len(difficulties) else "Medium",
            "correct": chosen == correct_idx,
            "yourAnswer": opts[chosen] if 0 <= chosen < len(opts) else None,
            "correctAnswer": opts[correct_idx] if 0 <= correct_idx < len(opts) else None,
            "explanation": get("explanation") or "",
        })
    return sorted(out, key=lambda r: (r["correct"], r["index"]))


def suggest_courses(engine: Any, comp_id: Optional[str], current_level: Optional[int],
                    target_level: Optional[int], limit: int = 3) -> List[Dict[str, Any]]:
    """Catalogue courses tagged with the competency, preferring the band the learner still has to climb."""
    if engine is None or not comp_id:
        return []
    try:
        idxs = engine._comp_index.get(comp_id, [])
        catalog = engine._catalog
    except AttributeError:
        return []
    lo = (current_level or 0) + 1
    hi = max(lo, target_level or lo)
    docs = []
    for i in idxs:
        d = catalog[i]
        lvl = (d.comp_levels or {}).get(comp_id)
        in_band = lvl is None or lo <= lvl <= hi
        docs.append((0 if in_band else 1, abs((lvl or lo) - lo), -(d.rating or 0), d, lvl))
    docs.sort(key=lambda t: t[:3])
    return [{"courseId": d.identifier, "title": d.name, "level": lvl,
             "durationHours": d.duration_hrs, "rating": d.rating}
            for *_, d, lvl in docs[:limit]]
