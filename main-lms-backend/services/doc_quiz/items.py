"""
FILE: services/doc_quiz/items.py
─────────────────────────────────────────────────────────────────────────────
Objective question types for the document quiz — pure functions, no I/O.

  mcq           one of 4 options                     answer: int
  true_false    options ["True", "False"]            answer: int (0 = True)
  multi_select  4–6 options, ≥2 correct              answer: List[int]  (all-or-nothing)
  fill_blank    stem contains "_____"                answer: str        (normalised / fuzzy match)
  numeric       a number (statistics formulas)       answer: str | float (tolerance)

A question is a QuizQuestion (routers/rag.py) or a plain dict; `_get` reads
either. Media quizzes carry no `type`, so everything defaults to "mcq" and
their int answers grade exactly as before.

Also here: the safe arithmetic evaluator that checks numeric answers against
the generator's `expression`, and the personalised wrong-answer feedback.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import ast
import difflib
import hashlib
import math
import operator
import re
from typing import Any, Dict, List, Optional

QUESTION_TYPES = ("mcq", "true_false", "multi_select", "fill_blank", "numeric")
CHOICE_TYPES = {"mcq", "true_false", "multi_select"}
TYPE_LABELS = {"mcq": "Multiple choice", "true_false": "True / False", "multi_select": "Select all that apply",
               "fill_blank": "Fill in the blank", "numeric": "Numeric answer"}
TRUE_FALSE_OPTIONS = ["True", "False"]
BLANK = "_____"

_DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
_BLANK_RE = re.compile(r"_{3,}|\[blank\]|\(blank\)|…{2,}|\.{4,}", re.I)
_NUMBER_RE = re.compile(r"[-−]?\d[\d,]*(?:\.\d+)?|[-−]?\.\d+")


def _get(q: Any, key: str, default: Any = None) -> Any:
    val = q.get(key, default) if isinstance(q, dict) else getattr(q, key, default)
    return default if val is None else val


def normalise_type(value: Any) -> str:
    s = re.sub(r"[\s\-/]+", "_", str(value or "").strip().lower())
    aliases = {"multiple_choice": "mcq", "single_choice": "mcq", "mcq_single": "mcq",
               "truefalse": "true_false", "tf": "true_false", "boolean": "true_false",
               "multiple_select": "multi_select", "multi": "multi_select", "select_all": "multi_select",
               "msq": "multi_select", "fill_in_the_blank": "fill_blank", "fill_in_blank": "fill_blank",
               "cloze": "fill_blank", "blank": "fill_blank", "number": "numeric", "numerical": "numeric",
               "calculation": "numeric"}
    s = aliases.get(s, s)
    return s if s in QUESTION_TYPES else "mcq"


def qtype(q: Any) -> str:
    return normalise_type(_get(q, "type", "mcq"))


def has_blank(text: str) -> bool:
    return bool(_BLANK_RE.search(text or ""))


def with_canonical_blank(text: str) -> str:
    return _BLANK_RE.sub(BLANK, text or "", count=1)


# ── Normalisation ─────────────────────────────────────────────────────────────

def normalise_text(s: Any) -> str:
    s = str(s or "").translate(_DEVANAGARI_DIGITS).casefold()
    s = re.sub(r"(?<=\d),(?=\d{3})", "", s)                # 1,234 → 1234
    s = re.sub(r"[^\w\s.%]", " ", s)                       # \w keeps Devanagari letters
    s = re.sub(r"\b(the|a|an)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip(" .")


def parse_number(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value) if math.isfinite(value) else None
    s = str(value or "").translate(_DEVANAGARI_DIGITS).replace("−", "-").strip()
    frac = re.fullmatch(r"\s*(-?\d+)\s*/\s*(\d+)\s*", s)
    if frac and int(frac.group(2)):
        return int(frac.group(1)) / int(frac.group(2))
    m = _NUMBER_RE.search(s)
    if not m:
        return None
    try:
        return float(m.group(0).replace(",", "").replace("−", "-"))
    except ValueError:
        return None


def numeric_tolerance(q: Any) -> float:
    ans = float(_get(q, "numeric_answer", 0.0))
    given = _get(q, "tolerance", 0.0)
    try:
        given = abs(float(given))
    except (TypeError, ValueError):
        given = 0.0
    # The generator's tolerance is honoured only when it is tight (≤ 5 %); a loose
    # one would accept wrong working.
    if given > 0.05 * abs(ans) + 1e-9:
        given = 0.0
    return max(given, 0.01 * abs(ans), 0.005)


# ── Safe arithmetic (numeric-answer verification) ─────────────────────────────

_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.Mod: operator.mod}
_FUNCS = {"sqrt": math.sqrt, "log": math.log, "ln": math.log, "log10": math.log10, "exp": math.exp,
          "abs": abs, "round": round, "min": min, "max": max, "sum": lambda *a: sum(a),
          "mean": lambda *a: sum(a) / len(a)}


def safe_eval(expr: str) -> float:
    """Evaluate +,-,*,/,**,%, parentheses and a few math functions. Raises ValueError otherwise."""
    expr = str(expr or "").translate(_DEVANAGARI_DIGITS).replace("×", "*").replace("÷", "/") \
        .replace("^", "**").replace("−", "-")
    expr = re.sub(r"(?<=\d),(?=\d{3})", "", expr)
    if len(expr) > 300:
        raise ValueError("expression too long")
    tree = ast.parse(expr, mode="eval")

    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN:
            left, right = ev(node.left), ev(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise ValueError("exponent too large")
            return _BIN[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            v = ev(node.operand)
            return -v if isinstance(node.op, ast.USub) else v
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS \
                and not node.keywords and len(node.args) <= 50:
            return float(_FUNCS[node.func.id](*[ev(a) for a in node.args]))
        raise ValueError(f"unsupported expression element: {type(node).__name__}")

    val = ev(tree)
    if not math.isfinite(val):
        raise ValueError("non-finite result")
    return val


def expression_numbers(expr: str) -> set:
    """Literal numbers used in an expression (for the 'inputs come from the source' check)."""
    return {n.replace(",", "") for n in re.findall(r"\d+(?:\.\d+)?", str(expr or "").translate(_DEVANAGARI_DIGITS))}


# ── Grading ───────────────────────────────────────────────────────────────────

def _choice_set(answer: Any) -> Optional[set]:
    if isinstance(answer, (list, tuple, set)):
        try:
            return {int(a) for a in answer}
        except (TypeError, ValueError):
            return None
    return None


def accepted_texts(q: Any) -> List[str]:
    out = [_get(q, "answer_text", "")] + list(_get(q, "accepted_answers", []) or [])
    for tr in (_get(q, "translations", {}) or {}).values():
        if isinstance(tr, dict):
            out += [tr.get("answer_text") or ""] + list(tr.get("accepted_answers") or [])
    return [a for a in dict.fromkeys(str(a).strip() for a in out) if a]


def _fill_match(given: str, accepted: List[str]) -> bool:
    g = normalise_text(given)
    if not g:
        return False
    for a in accepted:
        n = normalise_text(a)
        if not n:
            continue
        if g == n:
            return True
        # Numbers must match exactly; words may carry a small typo.
        if re.search(r"\d", n) or re.search(r"\d", g):
            continue
        if len(n) >= 6 and difflib.SequenceMatcher(None, g, n).ratio() >= 0.88:
            return True
    return False


def is_correct(q: Any, answer: Any) -> bool:
    t = qtype(q)
    if t == "multi_select":
        chosen = _choice_set(answer)
        return chosen is not None and chosen == set(_get(q, "correct_answers", []) or [])
    if t in ("mcq", "true_false"):
        try:
            return int(answer) == int(_get(q, "correct_answer", -1))
        except (TypeError, ValueError):
            return False
    if t == "fill_blank":
        return isinstance(answer, (str, int, float)) and _fill_match(str(answer), accepted_texts(q))
    if t == "numeric":
        x = parse_number(answer)
        ans = _get(q, "numeric_answer", None)
        return x is not None and ans is not None and abs(x - float(ans)) <= numeric_tolerance(q)
    return False


def is_answered(q: Any, answer: Any) -> bool:
    t = qtype(q)
    if t == "multi_select":
        return bool(_choice_set(answer))
    if t in ("mcq", "true_false"):
        return isinstance(answer, int) and not isinstance(answer, bool) and answer >= 0
    return str(answer if answer is not None else "").strip() != ""


def _fmt_num(x: float) -> str:
    return f"{x:,.6g}" if abs(x) >= 1e4 else f"{x:.6g}"


def correct_display(q: Any) -> str:
    t = qtype(q)
    opts = list(_get(q, "options", []) or [])
    if t == "multi_select":
        return "; ".join(opts[i] for i in sorted(_get(q, "correct_answers", []) or []) if 0 <= i < len(opts))
    if t in ("mcq", "true_false"):
        i = int(_get(q, "correct_answer", -1))
        return opts[i] if 0 <= i < len(opts) else ""
    if t == "fill_blank":
        return str(_get(q, "answer_text", ""))
    ans = _get(q, "numeric_answer", None)
    unit = _get(q, "unit", "")
    return f"{_fmt_num(float(ans))}{(' ' + unit) if unit else ''}" if ans is not None else ""


def answer_display(q: Any, answer: Any) -> Optional[str]:
    t = qtype(q)
    opts = list(_get(q, "options", []) or [])
    if t == "multi_select":
        chosen = _choice_set(answer) or set()
        picked = [opts[i] for i in sorted(chosen) if 0 <= i < len(opts)]
        return "; ".join(picked) or None
    if t in ("mcq", "true_false"):
        try:
            i = int(answer)
        except (TypeError, ValueError):
            return None
        return opts[i] if 0 <= i < len(opts) else None
    s = str(answer if answer is not None else "").strip()
    return s or None


# ── Personalised feedback ─────────────────────────────────────────────────────

def _why(q: Any, i: int) -> str:
    why = list(_get(q, "why_wrong", []) or [])
    return str(why[i]).strip().rstrip(".") if 0 <= i < len(why) and why[i] else ""


def feedback(q: Any, answer: Any) -> str:
    """Why THIS learner's answer is wrong (empty string when it is right)."""
    if is_correct(q, answer):
        return ""
    t = qtype(q)
    opts = list(_get(q, "options", []) or [])
    right = correct_display(q)
    if not is_answered(q, answer):
        return f"You left this unanswered. The answer is: {right}."

    if t in ("mcq", "true_false"):
        i = int(answer)
        chosen = opts[i] if 0 <= i < len(opts) else "?"
        reason = _why(q, i)
        if t == "true_false":
            # The explanation states the correct fact; the rationale is only a fallback.
            expl = str(_get(q, "explanation", "") or "").strip().rstrip(".")
            reason = expl if len(expl) >= 15 else reason
            head = f"The statement is {right}, not {chosen}."
        else:
            head = f"You chose “{chosen}”, but the source supports “{right}”."
        return f"{head} {reason}." if reason else head

    if t == "multi_select":
        chosen = _choice_set(answer) or set()
        correct = set(_get(q, "correct_answers", []) or [])
        parts = []
        for i in sorted(chosen - correct):
            parts.append(f"“{opts[i]}” should not be selected" + (f" — {_why(q, i)}" if _why(q, i) else "") + ".")
        missed = [opts[i] for i in sorted(correct - chosen) if 0 <= i < len(opts)]
        if missed:
            parts.append("You missed: " + "; ".join(f"“{m}”" for m in missed) + ".")
        return " ".join(parts) or f"The correct set is: {right}."

    if t == "fill_blank":
        given = str(answer).strip()
        best = max((difflib.SequenceMatcher(None, normalise_text(given), normalise_text(a)).ratio()
                    for a in accepted_texts(q)), default=0.0)
        if best >= 0.7:
            what = "figure" if re.search(r"\d", right) else "term"
            return f"Close — you wrote “{given}”; the source uses “{right}”. Check the exact {what}."
        return f"You wrote “{given}”; the source passage says “{right}”."

    # numeric
    x = parse_number(answer)
    ans = float(_get(q, "numeric_answer", 0.0))
    tol = numeric_tolerance(q)
    solution = str(_get(q, "solution", "") or "").strip()
    tail = f" Working: {solution}" if solution else ""
    if x is None:
        return f"“{answer}” is not a number. The answer is {right}.{tail}"
    if abs(x * 100 - ans) <= tol:
        hint = "You gave a fraction; the question expects a percentage."
    elif abs(x / 100 - ans) <= tol:
        hint = "You gave a percentage; the question expects a fraction or proportion."
    elif ans != 0 and abs(x + ans) <= tol:
        hint = "The size is right but the sign is wrong."
    elif ans != 0 and abs(x - ans) <= 0.1 * abs(ans):
        hint = "Close — recheck rounding or an intermediate step."
    else:
        hint = "Recheck which formula applies and which inputs it uses."
    return f"You answered {_fmt_num(x)}; the answer is {right}. {hint}{tail}"


def item_key(q: Any) -> str:
    """Stable id of an item's content, so response statistics survive new quiz ids."""
    base = "|".join([qtype(q), normalise_text(_get(q, "question", "")), normalise_text(correct_display(q))])
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:20]
