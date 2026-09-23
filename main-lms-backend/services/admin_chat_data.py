"""
services/admin_chat_data.py — the facts behind Gyan's admin answers.

routers/admin_chat.py asks a question, this module answers it with *numbers*
(dicts of plain values), and services/chat_messages/admin.py turns those into
a localized reply. Nothing here formats user-visible prose, so a translator
never has to touch a query.

Everything reads the same sources the admin console itself does:

  • the iGOT roster            routers.admin_console._roster()  (60 s cache —
                               reused on purpose so a chat question does not
                               trigger a second 151-user fetch)
  • pure aggregates            services.admin_analytics
  • competency levels          services.app_state.snapshot (workforce snapshot)
  • karma / nudges / plans     the auth DB (KarmaEvent, TrainingNudge,
                               TrainingAssignment)

Layering note: a service importing a router is unusual here. The import is
lazy and one-way (admin_console never imports this module); it exists so the
roster cache, the stale-copy fallback and the filter semantics stay in exactly
one place.
"""
from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple

from services import admin_analytics as aa
from services import app_state

# ── Identity lookup ───────────────────────────────────────────────────────────

_USER_ID_RE = re.compile(r"\busr[_-][A-Za-z0-9]+\b", re.IGNORECASE)
_GOV_ID_RE = re.compile(r"\bemp[\s_-]?\d{2,8}\b", re.IGNORECASE)
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.\w{2,}")

# "tell me about Shikha Thakur", "usr_720465595 ka status", "अनिल के बारे में"
_NAME_HINT_RE = re.compile(
    r"(?:about|details?\s+(?:of|for|about)|detail\s+of|profile\s+(?:of|for)|record\s+of|"
    r"status\s+of|look\s*up|lookup|search\s+for|find|who\s+is|show\s+me)\s+"
    r"(?P<name>[A-Za-z][A-Za-z.'’\- ]{2,60})",
    re.IGNORECASE,
)

# Words that survive the hint regex but are never part of an official's name.
_NAME_STOP = {
    "the", "a", "an", "official", "officials", "officer", "officers", "user", "users",
    "employee", "employees", "person", "profile", "details", "detail", "record", "records",
    "status", "about", "of", "for", "me", "please", "show", "tell", "give", "info",
    "information", "karmayogi", "igot", "mospi", "nso", "admin", "dashboard", "training",
    "course", "courses", "skill", "skills", "gap", "gaps", "karma", "points", "progress",
    "ka", "ki", "ke", "hai", "hain", "batao", "dikhao", "kaun", "kya", "bare", "baare", "mein",
    # "tell me about yourself" / "about GDP" reach the name pass through the
    # same lead-in as a real lookup, so the subjects Gyan already answers on
    # must not drift onto a surname.
    "yourself", "yourselves", "myself", "you", "gyan", "bot", "assistant", "console",
    "platform", "system", "statistics", "data", "gdp", "cpi", "wpi", "frac", "acbp",
    "nsso", "plfs", "sampling", "census", "quiz", "compliance", "department", "office",
}

_MIN_NAME_RATIO = 0.86   # difflib cut-off for a fuzzy name hit ("Shika" → "Shikha")
MAX_MATCHES = 6


def _clean(text: str) -> str:
    return re.sub(r"[^\w\s@.'’-]", " ", text, flags=re.UNICODE).strip()


def _name_tokens(text: str) -> List[str]:
    return [t for t in _clean(text).lower().split()
            if len(t) >= 3 and t not in _NAME_STOP and not t.isdigit()]


def _full_name(row: Dict[str, Any]) -> str:
    return f"{row['firstName']} {row['lastName']}".strip() or row["govId"]


def find_officials(message: str, rows: List[Dict[str, Any]], *, require_hint: bool = True,
                   identifiers_only: bool = False) -> Tuple[List[Dict[str, Any]], str]:
    """
    Officials the message could be referring to, and the term that was matched.

    Exact identifiers win outright (userId → govId → email); otherwise the
    message is read as a name. Returns ([], "") when nothing in the message
    looks like a person.

    `identifiers_only` stops before the name pass — the caller is only asking
    "does this message name someone beyond doubt?". `require_hint` keeps the
    name pass to what follows a lead-in like "tell me about …"; the classifier
    turns it off once it is confident the question *is* a lookup, so a bare
    "Shikha Thakur" resolves too.
    """
    uid = _USER_ID_RE.search(message)
    if uid:
        wanted = uid.group(0).replace("-", "_").lower()
        hit = [r for r in rows if r["userId"].lower() == wanted]
        if hit:
            return hit, uid.group(0)

    gov = _GOV_ID_RE.search(message)
    if gov:
        wanted = re.sub(r"[\s_-]+", "-", gov.group(0).upper())
        hit = [r for r in rows if r["govId"].upper() == wanted]
        if hit:
            return hit, gov.group(0)

    email = _EMAIL_RE.search(message)
    if email:
        wanted = email.group(0).lower()
        hit = [r for r in rows if r["email"].lower() == wanted]
        if hit:
            return hit, email.group(0)

    if identifiers_only:
        return [], ""

    hint = _NAME_HINT_RE.search(message)
    if hint is None and require_hint:
        return [], ""
    candidate = hint.group("name") if hint else message
    tokens = _name_tokens(candidate)
    if not tokens:
        return [], ""

    # Without a lead-in ("tell me about …") the whole message is the candidate,
    # so an ordinary word must not fuzzy-drift onto a surname: demand at least
    # one exact or prefix hit before believing a bare message names someone.
    strict = hint is None
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for r in rows:
        first, last = r["firstName"].lower(), r["lastName"].lower()
        full = f"{first} {last}".strip()
        hits: List[float] = []
        for tok in tokens:
            if tok == first or tok == last:
                hits.append(1.0)
            elif len(tok) >= 4 and (first.startswith(tok) or last.startswith(tok)):
                hits.append(0.95)
            else:
                ratio = max(SequenceMatcher(None, tok, first).ratio(),
                            SequenceMatcher(None, tok, last).ratio())
                if ratio >= _MIN_NAME_RATIO:
                    hits.append(ratio)
        if not hits or (strict and max(hits) < 0.95):
            continue
        # Summed, so "Shika Takur" (both names, both misspelt) beats every
        # official who merely shares one of them.
        score = sum(hits) + (1.0 if len(tokens) >= 2 and " ".join(tokens[:2]) == full else 0.0)
        scored.append((score, r))

    if not scored:
        return [], " ".join(tokens)
    scored.sort(key=lambda sr: (-sr[0], _full_name(sr[1])))
    top = scored[0][0]
    # Keep only equally-good matches, so "Sharma" lists the Sharmas rather than
    # every fuzzy near-miss behind them.
    return [r for score, r in scored if score >= top - 0.01][:MAX_MATCHES], " ".join(tokens)


# ── Scope (the chat's equivalent of the dashboard's filter bar) ────────────────

_GRADE_WORDS = {
    "TIER1_APEX": ("tier 1", "tier1", "apex", "sag"),
    "TIER2_SENIOR": ("tier 2", "tier2", "senior", "jag", "ddg"),
    "TIER3_MID": ("tier 3", "tier3", "middle", "mid ", "deputy director", "assistant director"),
    "TIER4_JUNIOR": ("tier 4", "tier4", "junior", "sso", "jso"),
}


def _names_in(value: str, lowered: str) -> bool:
    """Whole-word match, so the department "Data" never fires on "data governance"."""
    return len(value) >= 4 and re.search(rf"\b{re.escape(value.lower())}\b", lowered) is not None


def resolve_scope(message: str, ui_filters: Optional[Dict[str, str]],
                  rows: List[Dict[str, Any]]) -> Tuple[aa.Filters, Dict[str, str]]:
    """
    The filter this answer should use, and its active values for the reply.

    A department / office / grade named in the message wins over the filter bar
    the admin has set in the UI, so "compliance in Economic Statistics" answers
    about that department even while the page is filtered to another.
    """
    lowered = message.lower()
    ui = ui_filters or {}
    department = ui.get("department") or None
    office = ui.get("office") or None
    grade = ui.get("grade") or None

    facets = aa.facets(rows)
    for opt in facets["departments"]:
        if _names_in(opt["value"], lowered):
            department = opt["value"]
            break
    for opt in facets["offices"]:
        if _names_in(opt["label"], lowered):
            office = opt["value"]
            break
    for value, words in _GRADE_WORDS.items():
        if any(w in lowered for w in words):
            grade = value
            break

    f = aa.Filters(department, grade, office)
    labels = {}
    if department:
        labels["department"] = department
    if grade:
        labels["grade"] = aa.GRADE_LABELS.get(grade, grade)
    if office:
        labels["office"] = next((o["label"] for o in facets["offices"] if o["value"] == office), office)
    return f, labels


# ── Aggregate facts ───────────────────────────────────────────────────────────

def overview_facts(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    k = aa.kpis(rows)
    sc = aa.status_counts(rows)
    return {
        "total": k["totalOfficials"],
        "compliancePct": k["trainingCompliancePct"],
        "avgMissing": k["avgMissingSkills"],
        "compliant": sc["compliant"],
        "inProgress": sc["inProgress"],
        "required": sc["required"],
        "mandatory": k["mandatory"],
        "suppressed": k["suppressed"],
    }


def department_facts(rows: List[Dict[str, Any]], top: int = 5) -> List[Dict[str, Any]]:
    return aa.dept_compliance(rows, top=top)


def shortage_facts(rows: List[Dict[str, Any]], top: int = 5) -> List[Dict[str, Any]]:
    return aa.heatmap(rows, top=top)


def needs_training_facts(rows: List[Dict[str, Any]], top: int = 5) -> List[Dict[str, Any]]:
    return [{"name": _full_name(r), "govId": r["govId"], "department": r["department"],
             "missingCount": r["missingCount"], "missingSkill": r["missingSkill"]}
            for r in rows if r["enrollmentStatus"] == 0][:top]


def behind_facts(rows: List[Dict[str, Any]], top: int = 5) -> List[Dict[str, Any]]:
    behind = [r for r in rows if aa.is_behind_mandatory(r)]
    behind.sort(key=lambda r: r["mandatory"]["total"] - r["mandatory"]["completed"], reverse=True)
    return [{"name": _full_name(r), "govId": r["govId"], "department": r["department"],
             "completed": r["mandatory"]["completed"], "total": r["mandatory"]["total"]}
            for r in behind[:top]]


def trend_facts(series: Dict[str, Any]) -> Dict[str, Any]:
    """First / latest reading of the trend series, plus the direction between them."""
    points = [p for p in series.get("points", []) if p.get("trainedLast12mPct") is not None]
    weekly = [w for w in series.get("weeklyCompletions", []) if w.get("completions") is not None]
    if not points:
        return {"available": False}
    first, last = points[0], points[-1]
    delta = round((last["trainedLast12mPct"] or 0) - (first["trainedLast12mPct"] or 0), 1)
    recent = weekly[-4:]
    return {
        "available": True,
        "firstDate": first["date"], "lastDate": last["date"],
        "firstPct": first["trainedLast12mPct"], "lastPct": last["trainedLast12mPct"],
        "delta": delta, "direction": "up" if delta > 0.5 else "down" if delta < -0.5 else "flat",
        "mandatoryPct": last.get("mandatoryCompletionPct"),
        "avgLevel": last.get("avgLevel"), "atTargetPct": last.get("atTargetPct"),
        "weeklyAvg": round(sum(w["completions"] for w in recent) / len(recent), 1) if recent else None,
        "liveSnapshots": series.get("liveSnapshots", 0),
    }


# ── One official ──────────────────────────────────────────────────────────────

def competency_names() -> Dict[str, str]:
    engine = app_state.engine
    return {cid: m.get("name", cid) for cid, m in (engine._frac_map.items() if engine else [])}


def official_facts(row: Dict[str, Any], db_facts: Optional[Dict[str, Any]] = None,
                   top_gaps: int = 4) -> Dict[str, Any]:
    """Everything Gyan says about one official — roster row + snapshot + DB."""
    names = competency_names()
    snapshot = (app_state.snapshot or {}).get(row["userId"]) or {}
    comps = snapshot.get("competencies") or []
    assessed = [c for c in comps if c.get("level") is not None]
    gaps = sorted(
        ({"name": names.get(c["competencyId"], c["competencyId"]),
          "level": c["level"], "target": c["target"], "gap": round(c["target"] - c["level"], 1)}
         for c in assessed if c.get("target") and c["level"] < c["target"]),
        key=lambda g: -g["gap"],
    )
    mandatory = row.get("mandatory") or {}
    pending = (mandatory.get("pending") or [])[:3]
    return {
        "name": _full_name(row),
        "userId": row["userId"], "govId": row["govId"], "email": row["email"],
        "designation": row["designation"], "department": row["department"],
        "gradeLabel": row["gradeLabel"], "officeName": row["officeName"],
        "statusLabel": aa.STATUS_LABELS.get(row["enrollmentStatus"], "Training Required"),
        "missingCount": row["missingCount"], "missingSkill": row["missingSkill"],
        "completedCourses": len(row.get("completedCourseIds") or []),
        "mandatoryCycle": mandatory.get("cycle"),
        "mandatoryCompleted": mandatory.get("completed"),
        "mandatoryTotal": mandatory.get("total"),
        "pendingCourses": [p.get("title") or p.get("courseId") for p in pending],
        "assessedCount": len(assessed),
        "competencyCount": len(comps),
        "gaps": gaps[:top_gaps],
        "gapCount": len(gaps),
        "snapshotReady": bool(app_state.snapshot),
        **(db_facts or {}),
    }


def learner_db_facts(db, user_id: str) -> Dict[str, Any]:
    """Karma, nudges and assigned plans for one official (runs in a thread)."""
    from sqlalchemy import func

    from models.models import KarmaEvent, TrainingAssignment, TrainingNudge

    karma = db.query(func.coalesce(func.sum(KarmaEvent.pointsAwarded), 0)) \
              .filter(KarmaEvent.userId == user_id).scalar() or 0
    nudges = db.query(TrainingNudge).filter(TrainingNudge.userId == user_id) \
               .order_by(TrainingNudge.createdAt.desc()).limit(1).all()
    plans = [a for a in db.query(TrainingAssignment).all() if user_id in (a.assigneeIds or [])]
    return {
        "karmaPoints": int(karma),
        "nudgeCount": db.query(func.count(TrainingNudge.nudgeId))
                        .filter(TrainingNudge.userId == user_id).scalar() or 0,
        "lastNudgedAt": nudges[0].createdAt.date().isoformat() if nudges and nudges[0].createdAt else None,
        "assignedPlans": len(plans),
        "assignedPlanTitles": [a.title for a in plans[:2]],
    }
