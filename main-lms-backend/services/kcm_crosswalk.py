"""
services/kcm_crosswalk.py — Karmayogi Competency Model → catalogue FRAC ids

Live iGOT courses are tagged with `competencies_v6`, which references the KCM
framework (`kcmfinal_fw`): 3 competency areas, 146 themes, 601 sub-themes, with
ids like COMTHEME-000225. This platform's gap engine, baselines, role profiles
and ACBP plans all speak the catalogue FRAC id space instead. Without a bridge,
a live course can never be recommended against a measured gap — it would index
under keys nothing else uses.

This module builds that bridge the same way the engine already crosswalks role
competencies onto catalogue anchors (recommendation_service §5): embed both
sides with the shared multilingual model, take each KCM theme's nearest FRAC
competency, and accept the pair only when it clears `_derive_threshold`.

Expect most of the KCM to map to nothing, and treat that as the correct result.
The KCM describes the whole civil service — escalator maintenance, high-voltage
power systems, food waste — while this platform's FRAC set is written for
official statistics. Roughly 30 of 146 themes have a real counterpart. Forcing
the rest into the nearest statistical competency is how a live course about
lift maintenance ends up recommended against a sampling-frame gap.

Every rule is written `confirmed: false`, matching the convention in
`data/frac_crosswalk.json` — these are machine proposals awaiting the human
confirmation queue SCIL v6 asks for, not settled mappings.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

# A KCM theme maps onto a FRAC competency only above this cosine. Default None
# means "derive from the FRAC set" (see _derive_threshold).
_FLOOR = os.getenv("KCM_CROSSWALK_MIN_SIM")


def _text(name: str, description: str) -> str:
    return f"{(name or '').strip()}. {(description or '').strip()}".strip()


# A cosine below this is not a mapping, however the FRAC set is distributed.
# Calibrated by hand against the live KCM (see the table in
# docs/features/mock-igot-integration.md § "Live iGOT"): at 0.50 the crosswalk
# already accepts "Gender-sensitive Disaggregation → Disaster Preparedness",
# which is plainly wrong; at 0.55 the weakest survivors ("Data Protection →
# Data Privacy, Security", "Strategic Leadership → Leadership & Team
# Management") are all correct.
_ABS_FLOOR = 0.55


def _derive_threshold(frac_emb: np.ndarray, percentile: float = 99.0) -> float:
    """
    How close is "close enough"? Take the distribution of cosines between
    DISTINCT FRAC competencies and use its 99th percentile — a KCM theme must be
    nearer to its match than 99% of genuinely different FRAC competencies are to
    each other — then floor it at `_ABS_FLOOR`.

    The percentile alone is not enough. The FRAC set here is statistics-specific,
    so its members are mutually distinct (p99 ≈ 0.49) and the bar it implies is
    low; meanwhile the KCM spans all of government, including themes like
    "Escalator and Travelator Maintenance" that have no statistical counterpart
    at any threshold. Without the floor those map anyway, onto whatever happens
    to be least unlike them. The floor is what keeps the mapping honest; the
    percentile is what makes it adapt if the FRAC set is ever rewritten to be
    broader and mushier.
    """
    if len(frac_emb) < 2:
        return _ABS_FLOOR
    sims = frac_emb @ frac_emb.T
    off_diag = sims[~np.eye(len(sims), dtype=bool)]
    return max(float(np.percentile(off_diag, percentile)), _ABS_FLOOR)


def build_crosswalk(
    kcm_terms: List[Dict[str, Any]],
    frac: List[Dict[str, Any]],
    embedder: Any = None,
    threshold: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Propose KCM theme → FRAC competency mappings.

    `kcm_terms` are the framework's `theme` (and optionally `subtheme`) terms
    from LiveIgotAdapter.fetch_kcm_framework(). `frac` is the catalogue FRAC set
    (`id`, `name`, `description`).

    Returns {threshold, count, mappings: [{kcmRefId, kcmName, fracId, fracName,
    similarity, confirmed}]} — ready to json.dump next to the catalogue.
    """
    from ai.embedder import encode_cached, get_embedder

    frac = [c for c in frac or [] if c.get("id")]
    kcm_terms = [t for t in kcm_terms or [] if (t.get("refId") or t.get("identifier"))]
    if not frac or not kcm_terms:
        logger.warning("[kcm-crosswalk] nothing to map (frac=%d, kcm=%d).", len(frac), len(kcm_terms))
        return {"threshold": 0.0, "count": 0, "mappings": []}

    embedder = embedder or get_embedder("catalog")
    frac_emb = encode_cached("catalog", [_text(c.get("name", ""), c.get("description", "")) for c in frac],
                             kind="passage", embedder=embedder)
    kcm_emb = encode_cached("catalog", [_text(t.get("name", ""), t.get("description", "")) for t in kcm_terms],
                            kind="passage", embedder=embedder)

    if threshold is None:
        threshold = float(_FLOOR) if _FLOOR else _derive_threshold(frac_emb)

    sims = kcm_emb @ frac_emb.T                    # both are L2-normalised
    best = sims.argmax(axis=1)
    mappings: List[Dict[str, Any]] = []
    for i, term in enumerate(kcm_terms):
        j = int(best[i])
        score = float(sims[i, j])
        if score < threshold:
            continue
        mappings.append({
            "kcmRefId":   term.get("refId") or term.get("identifier"),
            "kcmName":    term.get("name", ""),
            "fracId":     frac[j]["id"],
            "fracName":   frac[j].get("name", ""),
            "similarity": round(score, 4),
            "confirmed":  False,
        })

    logger.info("[kcm-crosswalk] %d/%d KCM terms mapped at threshold %.3f.",
                len(mappings), len(kcm_terms), threshold)
    return {"threshold": round(float(threshold), 4), "count": len(mappings), "mappings": mappings}


def load_crosswalk(path: str) -> Dict[str, str]:
    """
    {kcmRefId: fracId} from a file written by build_crosswalk. Returns {} when
    the file is missing or unreadable — live courses then keep their own KCM
    ids, which is harmless: they simply do not match a FRAC-keyed gap.
    """
    try:
        with open(os.path.normpath(path), "r", encoding="utf-8") as fh:
            raw = json.load(fh)
    except (OSError, ValueError) as exc:
        logger.info("[kcm-crosswalk] no crosswalk at %s (%s) — live courses keep KCM ids.", path, exc)
        return {}
    rows = raw.get("mappings", raw) if isinstance(raw, dict) else raw
    return {m["kcmRefId"]: m["fracId"] for m in rows
            if isinstance(m, dict) and m.get("kcmRefId") and m.get("fracId")}


def apply_crosswalk(catalog: List[Dict[str, Any]], mapping: Dict[str, str]) -> int:
    """
    Rewrite each live course's `competencies_v6` theme refIds to catalogue FRAC
    ids in place, so the engine indexes live courses in the same keyspace as
    gaps. A tag whose theme has no mapping keeps its KCM refId.

    Returns how many courses got at least one FRAC id.
    """
    if not mapping:
        return 0
    touched = 0
    for course in catalog:
        tags = course.get("competencies_v6") or []
        hit = False
        for tag in tags:
            if not isinstance(tag, dict):
                continue
            ref = tag.get("competencyThemeRefId")
            frac_id = mapping.get(ref)
            if frac_id:
                tag["fracId"] = frac_id
                hit = True
        touched += 1 if hit else 0
    logger.info("[kcm-crosswalk] %d/%d live courses carry at least one FRAC id.", touched, len(catalog))
    return touched
