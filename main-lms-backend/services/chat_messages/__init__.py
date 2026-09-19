"""
Localized reply catalogue for Gyan.

Language modules (en.py, hi.py, bn.py, ...) contain ONLY strings: a dict `T`
of `str.format` templates (or lists of alternatives picked at random). All
branching — home vs dashboard page, gaps vs none, progress thresholds — lives
here once, so translators and reviewers never touch logic.

Variants: en, hi (Devanagari), hi_latn (romanized Hindi), mr, bn, gu, or, ta, te.
"""

from __future__ import annotations

import functools
import importlib
import logging
import random
from typing import Callable

from services.chat_messages.context import ReplyContext

logger = logging.getLogger(__name__)

VARIANTS = ("en", "hi_latn", "hi", "mr", "bn", "gu", "or", "ta", "te")

LANDING_SECTIONS = {"navigation_features": "Features", "navigation_about": "About", "navigation_contact": "Contact"}


@functools.lru_cache(maxsize=None)
def templates(variant: str) -> dict:
    """Loads a language's template table on first use ("or" lives in or_.py; `or` is a keyword)."""
    variant = variant if variant in VARIANTS else "en"
    return importlib.import_module(f"{__name__}.{'or_' if variant == 'or' else variant}").T


def text(key: str, variant: str, **fields) -> str:
    template = templates(variant).get(key)
    if template is None:
        logger.warning("[chat_messages] %r missing for %s; using English.", key, variant)
        template = templates("en")[key]
    if isinstance(template, list):
        template = random.choice(template)
    return template.format(**fields)


Translator = Callable[..., str]


def _gap_lines(ctx: ReplyContext, t: Translator) -> str:
    return "\n".join(
        t("gap_line", skill=g.skillName, domain=g.domain, current=g.currentLevel, target=g.targetLevel, gap=g.gapScore)
        for g in ctx.sorted_active_gaps
    )


def _rec_lines(ctx: ReplyContext, t: Translator) -> str:
    return "\n".join(
        t("rec_line", index=i, title=r.title, provider=r.provider, hours=f"{r.durationHours:.0f}")
        for i, r in enumerate(ctx.recs[:3], start=1)
    )


def _greeting(ctx: ReplyContext, t: Translator) -> str:
    if ctx.page == "home":
        return t("greeting.home")
    return t("greeting.dashboard", role=ctx.role, dept=ctx.dept, gap_count=len(ctx.active_gaps))


def _user_identity(ctx: ReplyContext, t: Translator) -> str:
    if ctx.page == "home":
        return t("user_identity.home")
    name_line = t("user_identity.name_known", full_name=ctx.full_name) if ctx.full_name else t("user_identity.name_unknown")
    id_line = t("user_identity.id_known", gov_id=ctx.gov_id) if ctx.gov_id else t("user_identity.id_unknown")
    return t("user_identity.dashboard", name_line=name_line, id_line=id_line, dept=ctx.dept, role=ctx.role)


def _profile_stats(ctx: ReplyContext, t: Translator) -> str:
    if ctx.page == "home":
        return t("profile_stats.home")
    stats = ctx.stats
    top = ctx.top_gap
    domain_lines = "\n".join(
        t("domain_line", domain=domain, count=count) for domain, count in stats["domain_breakdown"].items()
    ) or t("domain_none")
    return t(
        "profile_stats.dashboard",
        role=ctx.role, dept=ctx.dept,
        total=stats["total_competencies"], met=stats["met_count"], gap_count=stats["gaps_count"],
        completion_pct=stats["completion_pct"], tier_label=t(f"tier.{stats['tier']}"),
        top_skill=top.skillName if top else t("none"), top_gap=top.gapScore if top else 0,
        avg_gap=stats["avg_gap_score"], domain_lines=domain_lines,
    )


def _skill_gaps(ctx: ReplyContext, t: Translator) -> str:
    if ctx.page == "home":
        return t("skill_gaps.home")
    top = ctx.top_gap
    if top is None:
        return t("skill_gaps.none", total=len(ctx.gaps), role=ctx.role)
    return t("skill_gaps.list", role=ctx.role, gap_lines=_gap_lines(ctx, t), top_skill=top.skillName, top_gap=top.gapScore)


def _recommend(ctx: ReplyContext, t: Translator) -> str:
    if not ctx.recs:
        return t("recommend.none")
    top = ctx.top_gap
    reason = t("recommend.reason_gap", top_gap=top.gapScore, top_skill=top.skillName) if top else t("recommend.reason_role")
    first = ctx.recs[0]
    return t(
        "recommend.list",
        reason=reason, rec_lines=_rec_lines(ctx, t),
        first_title=first.title, first_reason=first.matchReason.lower(),
    )


def _progress(ctx: ReplyContext, t: Translator) -> str:
    total = len(ctx.gaps)
    met = total - len(ctx.active_gaps)
    pct = round((met / total * 100) if total else 0)
    encouragement = t("progress.good" if pct >= 60 else "progress.keep_going")
    return t("progress", role=ctx.role, met=met, total=total, pct=pct,
             gap_count=len(ctx.active_gaps), encouragement=encouragement)


def _motivation(ctx: ReplyContext, t: Translator) -> str:
    first_rec = ctx.recs[0].title if ctx.recs else t("motivation.default_course")
    return t("motivation", first_rec=first_rec)


def _by_page(intent: str) -> Callable[[ReplyContext, Translator], str]:
    return lambda ctx, t: t(f"{intent}.{ctx.page}")


def _landing_section(intent: str) -> Callable[[ReplyContext, Translator], str]:
    def build(ctx: ReplyContext, t: Translator) -> str:
        if ctx.page == "home":
            return t(f"{intent}.home")
        return t("landing_section.dashboard", section=LANDING_SECTIONS[intent])
    return build


_BUILDERS: dict[str, Callable[[ReplyContext, Translator], str]] = {
    "greeting": _greeting,
    "user_identity": _user_identity,
    "profile_stats": _profile_stats,
    "skill_gaps": _skill_gaps,
    "recommend": _recommend,
    "progress": _progress,
    "motivation": _motivation,
    "navigation_home": _by_page("navigation_home"),
    "navigation_login": _by_page("navigation_login"),
    "fallback": _by_page("fallback"),
    **{intent: _landing_section(intent) for intent in LANDING_SECTIONS},
}

_STATIC_INTENTS = frozenset({
    "how_are_you", "bot_identity", "concept_skill_gap", "gratitude", "last_assessment", "achievements",
    "navigation_dashboard", "navigation_my_courses", "navigation_progress", "navigation_ai_quiz",
    "navigation_skill_gap", "navigation_recommendations", "navigation_certificates", "navigation_karma",
    "navigation_profile", "about_platform", "about_mospi", "statistics_gdp", "statistics_cpi",
    "statistics_sampling", "statistics_frac", "out_of_scope", "ui_action_request", "farewell",
})

REPLY_INTENTS = frozenset(_BUILDERS) | _STATIC_INTENTS


def render(intent: str, variant: str, ctx: ReplyContext) -> str:
    """Localized reply for `intent`; unknown intents get the page's fallback reply."""
    t = lambda key, **fields: text(key, variant, **fields)  # noqa: E731
    if intent in _BUILDERS:
        return _BUILDERS[intent](ctx, t)
    if intent in _STATIC_INTENTS:
        return t(intent)
    return _BUILDERS["fallback"](ctx, t)


def render_theme_action(variant: str, theme: str) -> str:
    return text(f"action.theme.{theme}", variant)


def render_language_action(variant: str, language: str) -> str:
    return text("action.language", variant, language_name=text(f"language_name.{language}", variant))


def render_theme_language_action(variant: str, theme: str, language: str) -> str:
    return text(
        "action.theme_language", variant,
        theme_name=text(f"theme_name.{theme}", variant),
        language_name=text(f"language_name.{language}", variant),
    )


def render_login_credentials(variant: str) -> str:
    return text("navigation_login.credentials", variant)
