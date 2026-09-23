"""
FILE: main-lms-backend/services/recommendation_service.py
─────────────────────────────────────────────────────────────────────────────
Locked 3-Stage Hybrid Recommendation Engine for MoSPI Skill Intelligence
Platform (SIH 2026).

Stage 0 — Cross-Gap Prioritization
    priority_k = gap_k * (target_k / 5.0)
    Highest-priority gaps are addressed first.

Stage 1 — Mandatory FRAC-Tag + Level Filtering
    Candidate pool = only courses tagged with FRAC competency k AT a level the
    official still has to climb: current < courseLevel <= target. Every
    competencies_v3 tag carries a FRAC "Level N"; a beginner is never shown a
    Level-5 course first and an expert is never shown a Level-1 course.
    Untagged courses cannot enter ranking (prevents semantic hallucinations).

Stage 2 — Hybrid Search + RRF Fusion
    Dense  : ai.embedder "catalog" role (default all-MiniLM-L6-v2, 384-dim),
             exact cosine over the candidate pool (FAISS only for the
             untagged-competency fallback)
    Sparse : rank_bm25.BM25Okapi over title+description corpus
    Query  : FRAC competency official name + description (never raw user text)
    Fusion : RRF(d) = 1/(60+rank_dense) + 1/(60+rank_sparse)
    Boost  : RRF × 1.25 for verified TPAC courses, × 1.10 for inferred ones
    Rerank : optional multilingual cross-encoder over the top 20 (ai/reranker.py,
             ENABLE_CROSS_ENCODER=1): relevance = mean of RRF and cross-encoder,
             each min-max normalised within the re-ranked set

Stage 3 — Weighted Final Scoring
    quality = 0.35*completion + 0.35*rating_norm(Bayesian shrinkage) + 0.20*pop_norm + 0.10*tpac_flag
    final   = 0.6*relevance_norm + 0.4*quality
    Karma points: informational only — excluded from final_score.

Stage 4 — Learning Pathway (build_pathway / build_study_plan)
    Per competency: one course per FRAC level from current+1 up to target —
    "first this course, then that one". Catalogue holes are bridged by the
    next level's course (a flagged "stretch" step) and reported as coverage
    gaps; unassessed / self-reported levels get a diagnostic step first.
    Across competencies: greedy gain-per-hour over the level ladders (SCIL v6
    §5 cost-benefit rule) with an optional hours budget. The ladder order is
    the prerequisite DAG. No approximation guarantee is claimed: the classic
    (1-1/e) bound does not hold for ratio-greedy under a budget with
    precedence constraints.
─────────────────────────────────────────────────────────────────────────────
"""

import json
import logging
import math
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
from pydantic import BaseModel
from rank_bm25 import BM25Okapi

from ai.embedder import encode_cached, get_embedder

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
_RRF_K         = 60          # RRF constant
# RRF multiplier by TPAC provenance: a catalogue-confirmed TPAC course gets the
# full boost; one inferred only from its NSSTA creator name gets a smaller one.
_TPAC_BOOST    = {"verified": 1.25, "inferred": 1.10}
# ── Relevance scale (Bug #9) ──────────────────────────────────────────────────
# Relevance used to be the RRF score min-max normalised *inside the shortlist*,
# so the weakest candidate of every pool scored exactly 0.000 however good it was,
# and a 3-course pool and a 50-course pool were on different scales. It is now an
# ABSOLUTE score in [0,1], so "62%" means the same thing for every gap:
#   semantic  cosine to the official FRAC anchor, calibrated against the null
#             distribution of the courses NOT tagged with that competency
#             (0.5 = as close as a typical untagged course, → 1 = far closer)
#   lexical   BM25, saturating at the corpus median of its positive scores
#   fusion    this course's RRF rank fusion over the theoretical RRF maximum
_REL_W_SEM, _REL_W_LEX, _REL_W_FUS = 0.45, 0.20, 0.35
_RRF_MAX       = 2.0 / (_RRF_K + 1)   # 1st on both rankings → the largest RRF possible
_SEM_MIN_SIGMA = 1e-3                 # guards the calibration on a degenerate corpus
_POP_REF_PCT   = 95                   # enrolments at this percentile = full popularity
_FALLBACK_DURS = 1.5         # hours if duration field missing/zero
_MAX_LEVEL     = 5           # FRAC proficiency scale is Level 1..5
_MIN_STEP_HRS  = 0.1         # floor on hours in gain-per-hour (avoids /0)
# Study-plan tie band (SCIL v6 §4): frontier courses whose gain/hour is within
# 10% of the best are treated as near-ties, and the gap the official can practise
# at work this cycle (higher opportunity) goes first. 10% is well inside the
# noise of the hour estimates, so the tie-break never overrides a clear winner.
OPPORTUNITY_TIE_BAND = 0.10
# Modality mix (SCIL v6 §5): at most 30 classroom hours in one quarter's plan —
# five 6-hour training days away from the desk. Longer TPAC programmes need a
# quarter planned around them (they show up as deferred: "classroom cap").
CLASSROOM_CAP_HOURS_PER_QUARTER = 30.0
_OPPORTUNITY_RANK  = {"High": 3, "Medium": 2, "Low": 1}
_OPPORTUNITY_LEVEL = {v: k for k, v in _OPPORTUNITY_RANK.items()}
_DEFAULT_CATALOG = os.path.join(
    os.path.dirname(__file__), "..", "..", "mock-igot-server", "data", "course_catalog.json"
)
_DEFAULT_FRAC = os.path.join(
    os.path.dirname(__file__), "..", "..", "mock-igot-server", "data", "frac_competencies.json"
)

NSSTA_CREATORS = {
    "National Academy of Statistical Administration",
    "NSSTA",
}

# ── Pydantic output schema ─────────────────────────────────────────────────────

class RecommendationResult(BaseModel):
    courseId:       str
    title:          str
    provider:       str
    durationHours:  float
    finalScore:     float          # 0.6*relevance + 0.4*quality  ∈ [0,1]
    relevanceScore: float          # absolute semantic + lexical + fusion match ∈ [0,1]
    qualityScore:   float          # absolute quality composite ∈ [0,1]
    isTpac:         bool
    competencyId:   str
    competencyName: str
    priorityRank:   int            # 1-based, within priority-preserving concat (Bug #8)
    matchReasons:   List[str]      # human-readable explanation chips
    # FIX (Bug #6): distinguish how TPAC status was determined
    matchType:   Optional[str] = None  # "frac_tag" | "semantic_fallback"
    tpacSource:  Optional[str] = None  # "verified" | "inferred" | "none"
    courseLevel: Optional[int] = None  # FRAC level this course is tagged at for competencyId
    # False = course text is no closer to the competency than a typical UNtagged
    # course, i.e. the author-declared tag isn't supported by content (review it).
    tagSupported: Optional[bool] = None
    # SCIL v6 §6: measured uplift (FRAC levels, shrunk) from course outcome data, and
    # whether that data says the course barely moves its competency (synthetic data).
    measuredUplift: Optional[float] = None
    upliftFlag:     Optional[bool]  = None
    modality:       Optional[str]   = None   # self_paced | virtual_lab | classroom
    mandatory:      bool            = False  # in the official's ACBP (departmental training plan)
    reranked:       Optional[bool]  = None   # True → relevance includes the cross-encoder score
    # "Why recommended": {gap{…}, levelStep{…}, badges[], summary} — see _why()
    why:            Optional[Dict[str, Any]] = None



class GapEntry(BaseModel):
    competencyId:   str
    competencyName: str
    currentLevel:   float
    targetLevel:    float
    gapScore:       float
    priorityScore:  float          # gap_k * (target_k / 5.0) — Stage 0
    confidence:     Optional[str] = None   # "HIGH" | "MEDIUM" | "LOW" | "UNASSESSED"
    # Catalogue FRAC id this role competency is crosswalked to (None = same id)
    catalogueId:    Optional[str] = None

    @property
    def catalogue_key(self) -> str:
        """The id whose FRAC tags / levels / official text drive retrieval."""
        return self.catalogueId or self.competencyId


# ── Internal dataclass (not exposed to API) ────────────────────────────────────

@dataclass
class _CourseDoc:
    idx:              int
    identifier:       str
    name:             str
    description:      str
    channel:          str
    creator:          str
    organisation:     List[str]
    duration_hrs:     float
    comp_ids:         List[str]    # parsed from competencies_v3
    comp_names:       List[str]
    # comp_id → FRAC level (1-5) the course is tagged at; None if the tag has no level
    comp_levels:      Dict[str, Optional[int]] = field(default_factory=dict)
    # FIX (Bug #7): these fields are Optional — missing = excluded from
    # normalization pool, NOT replaced with fabricated defaults.
    # A course with no rating data does not get a free 3.5/30 bonus.
    rating:           Optional[float] = None
    rating_count:     Optional[int]   = None
    enrollment_count: Optional[int]   = None
    completion_rate:  Optional[float] = None
    is_tpac:          bool  = False
    # FIX (Bug #6): distinguishes catalog-confirmed TPAC from inferred-by-name.
    # "verified" = is_tpac field present & True in raw catalog JSON
    # "inferred" = creator/org name matched NSSTA_CREATORS heuristic
    # "none"     = no TPAC signal found
    tpac_source:      str   = "none"
    corpus_text:      str   = ""   # title + description, lowercased, for BM25
    modality:         Optional[str] = None   # "self_paced" | "virtual_lab" | "classroom"
    fmt:              Optional[str] = None   # catalogue `format` (micro_learning, tpac_programme, …)


# ── Bayesian shrinkage rating (Bug #5 fix — replaces Wilson lower bound) ───────
# Wilson lower bound is only valid for a *binomial proportion* (0/1 outcomes).
# It is mathematically invalid when applied to mean star ratings (1-5 scale).
# Bayesian additive shrinkage is the correct tool:
#   shrunk = (n * mean + k * prior) / (n + k)
# where k is the "prior weight" (how many prior-mean observations to assume).
# This pulls sparse-rated courses toward the global prior mean (3.0 stars),
# preventing a single 5-star rating from dominating quality ranking.

_PRIOR_MEAN = 3.0   # global prior mean (midpoint of 1-5 scale)
_SHRINK_K   = 15    # prior weight — equivalent to 15 "average" reviews


def _shrunk_rating(rating: Optional[float], count: Optional[int]) -> Optional[float]:
    """
    Bayesian shrinkage toward global prior mean.
    Returns None if either input is None (course excluded from normalization pool).
    """
    if rating is None or count is None:
        return None
    if count < 0:
        return None
    return (_SHRINK_K * _PRIOR_MEAN + count * rating) / (_SHRINK_K + count)


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else float(x))


def _logistic(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-min(max(z, -30.0), 30.0)))


def _lex_ref(bm25: np.ndarray) -> float:
    """
    The BM25 score this query gives a *typical matching* course — the median of
    its positive scores over the whole corpus. Used as the saturation point of
    `b / (b + ref)`, which turns an unbounded BM25 score into an absolute [0,1)
    lexical match (0.5 at the median) without min-maxing inside a shortlist.
    """
    pos = bm25[bm25 > 0]
    ref = float(np.median(pos)) if pos.size else 0.0
    return ref if ref > 0 else 1.0


def _parse_level(raw: Any) -> Optional[int]:
    """'Level 3' / 3 / '3' → 3; anything outside 1..5 → None."""
    if raw is None:
        return None
    m = re.search(r"\d+", str(raw))
    if not m:
        return None
    lvl = int(m.group())
    return lvl if 1 <= lvl <= _MAX_LEVEL else None




# ── Main Engine ────────────────────────────────────────────────────────────────

class HybridRecommendationEngine:
    """
    Singleton — built ONCE at app startup.
    Holds FAISS index + BM25 corpus in memory.
    Thread-safe for read-only inference.
    """

    def __init__(
        self,
        catalog_path: str = _DEFAULT_CATALOG,
        frac_path:    str = _DEFAULT_FRAC,
        catalog:      Optional[List[Dict[str, Any]]] = None,
        frac:         Optional[List[Dict[str, Any]]] = None,
        crosswalk:    Optional[List[Dict[str, Any]]] = None,
        crosswalk_path: Optional[str] = None,
        precomputed_embeddings: Optional[Dict[str, Tuple[str, np.ndarray]]] = None,
    ):
        """
        `catalog` / `frac` / `crosswalk` are the lists served by the mock iGOT
        server (loaded through MockIgotAdapter in main._startup). When a list
        is not given, the matching file is read from disk instead — the same
        generated file the mock server serves, so the two cannot drift.

        `precomputed_embeddings` = {courseId: (text_hash, vector)} loaded from the
        database (services/catalogue_store.py). A vector is reused only when its
        text hash matches the course's current title + description and it has
        the right dimension; every other course is encoded.
        """
        self.catalog_source = "adapter" if catalog is not None else "disk"
        # ── 1. Load FRAC dictionary ────────────────────────────────────────────
        self._frac_map: Dict[str, Dict] = {}   # id → {name, description}
        try:
            if frac is not None:
                frac_list = frac
            else:
                with open(os.path.normpath(frac_path), "r", encoding="utf-8") as f:
                    frac_list = json.load(f)
            for comp in frac_list:
                # children = the FRAC proficiency descriptors, one per level
                levels = {
                    int(ch["level"]): (ch.get("description") or "").strip()
                    for ch in (comp.get("children") or [])
                    if isinstance(ch, dict) and ch.get("level")
                }
                self._frac_map[comp["id"]] = {
                    "name":        comp.get("name", ""),
                    "description": comp.get("description", ""),
                    "type":        comp.get("competencyType", "Domain"),
                    "levels":      levels,
                    # SCIL v6 §2 two-class decay (accuracy | procedural), from FRAC data
                    "decayClass":  comp.get("decayClass", "procedural"),
                }
            logger.info("[RecEngine] Loaded %d FRAC competencies.", len(self._frac_map))
        except Exception as exc:
            logger.warning("[RecEngine] Could not load FRAC data: %s", exc)

        # ── 2. Load + parse course catalog ────────────────────────────────────
        self._catalog: List[_CourseDoc] = []
        self._comp_index: Dict[str, List[int]] = {}   # comp_id → list of doc indices
        self._by_id: Dict[str, int] = {}              # course identifier → doc index
        # (comp_id, query_text) → (query embedding, BM25 scores over corpus).
        # The query for a competency is fixed (official FRAC text), so it is
        # encoded once instead of once per level / per request.
        self._query_cache: Dict[Tuple[str, str], Tuple[np.ndarray, np.ndarray]] = {}
        # comp_id → (median, mean, std) cosine of the courses NOT tagged with it.
        # The median is the tag-support null; the mean and std calibrate the
        # absolute semantic relevance score.
        self._untagged_stats: Dict[str, Tuple[float, float, float]] = {}
        # Catalogue-wide normalisers for the quality composite (filled after parsing).
        self._quality_norms: Dict[str, float] = {}

        try:
            if catalog is not None:
                raw_catalog = catalog
            else:
                with open(os.path.normpath(catalog_path), "r", encoding="utf-8") as f:
                    raw_catalog = json.load(f)
            self._parse_catalog(raw_catalog)
            logger.info("[RecEngine] Indexed %d courses.", len(self._catalog))
        except Exception as exc:
            logger.error("[RecEngine] Failed to load catalog: %s", exc)
            raise

        # Catalogue-wide quality normalisers — absolute, so a course's quality no
        # longer depends on which shortlist it happens to land in (Bug #10).
        self._build_quality_norms()

        # ── 3. Build BM25 index ────────────────────────────────────────────────
        corpus_tokens = [doc.corpus_text.split() for doc in self._catalog]
        self._bm25 = BM25Okapi(corpus_tokens)
        logger.info("[RecEngine] BM25 index built over %d documents.", len(self._catalog))

        # ── 4. Load the embedder + build FAISS index ──────────────────────────
        # Model loaded ONCE for whole backend via ai/embedder.py singleton; it is
        # needed for per-request queries even when the corpus vectors are cached.
        logger.info("[RecEngine] Acquiring catalog embedder...")
        embedder = get_embedder("catalog")

        corpus_texts = [doc.corpus_text for doc in self._catalog]
        self._text_hash = [text_hash(t) for t in corpus_texts]
        embeddings = self._corpus_embeddings(corpus_texts, precomputed_embeddings or {}, embedder)
        self._embeddings = embeddings   # kept for exact cosine over small candidate pools

        # Use faiss lazy import (not installed on every machine at import time)
        import faiss
        dim = embeddings.shape[1]   # 384
        self._faiss_index = faiss.IndexFlatIP(dim)
        self._faiss_index.add(embeddings)
        logger.info("[RecEngine] FAISS index built: %d vectors × %d dims.", *embeddings.shape)

        # ── 5. Crosswalk anchors (SCIL v6 §1) ─────────────────────────────────
        # Role profiles can carry competency ids from a wider FRAC dictionary
        # than this catalogue is tagged with. Anchors = FRAC competencies that
        # actually have tagged courses. A role competency maps to its nearest
        # anchor only if it is closer than 95% of pairs of DISTINCT anchors are
        # to each other — a threshold derived from the FRAC set itself.
        self._xw_ids = [cid for cid in self._frac_map if cid in self._comp_index]
        self._xw_cache: Dict[Tuple[str, str], Optional[Dict[str, Any]]] = {}
        self._xw_threshold = float("inf")      # uncalibrated → never map semantically
        if self._xw_ids:
            self._xw_emb = encode_cached("catalog", [
                f"{self._frac_map[c]['name']}. {self._frac_map[c]['description']}".strip()
                for c in self._xw_ids
            ], kind="passage", embedder=embedder)
            if len(self._xw_ids) >= 2:
                sims = self._xw_emb @ self._xw_emb.T
                self._xw_threshold = float(np.percentile(sims[~np.eye(len(sims), dtype=bool)], 95))
        logger.info("[RecEngine] Crosswalk: %d anchors, threshold %.3f.",
                    len(self._xw_ids), self._xw_threshold)

        # Explicit crosswalk (data/frac_crosswalk.json): iGOT dictionary CID id →
        # catalogue id, each with a `confirmed` flag. Consulted before embeddings.
        self._xw_curated: Dict[str, Dict[str, Any]] = {}
        # courseId → {measuredUplift, ci95, misTagFlag, …} (set_measured_uplift, SCIL v6 §6)
        self._uplift: Dict[str, Dict[str, Any]] = {}
        if crosswalk is None:
            path = crosswalk_path or os.path.join(os.path.dirname(os.path.normpath(catalog_path)),
                                                  "frac_crosswalk.json")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    raw_xw = json.load(f)
                crosswalk = raw_xw.get("mappings", []) if isinstance(raw_xw, dict) else raw_xw
            except (OSError, ValueError):
                crosswalk = []
        for m in crosswalk or []:
            if m.get("fracId") and m["fracId"] in self._comp_index:
                self._xw_curated[m["cidId"]] = m

    # ── Catalog parser ─────────────────────────────────────────────────────────

    def _parse_catalog(self, raw: list) -> None:
        for idx, item in enumerate(raw):
            # Parse competencies_v3 (stored as a JSON string in the mock data)
            comp_ids, comp_names = [], []
            comp_levels: Dict[str, Optional[int]] = {}
            raw_v3 = item.get("competencies_v3", "")
            if raw_v3:
                try:
                    tags = json.loads(raw_v3) if isinstance(raw_v3, str) else raw_v3
                    for tag in tags:
                        cid = tag.get("id", "")
                        if cid and cid not in comp_levels:
                            comp_ids.append(cid)
                            comp_names.append(tag.get("name", ""))
                            comp_levels[cid] = _parse_level(tag.get("competencyLevel"))
                except Exception:
                    pass

            # Live iGOT tags courses with competencies_v6 (the Karmayogi
            # Competency Model) instead: 99.9% of the live catalogue carries it,
            # while the CID-based v3 tags above survive on a small minority. Read
            # v6 only when v3 gave nothing, so mock data behaves exactly as before.
            #
            # `fracId` is stamped by services.kcm_crosswalk when a KCM theme maps
            # onto a catalogue competency; without it the theme's own refId is
            # used, which simply will not match a FRAC-keyed gap. KCM tags carry
            # no proficiency level, so the level is None — the ranker already
            # treats that as "no band stated" rather than level 0.
            if not comp_ids:
                for tag in item.get("competencies_v6") or []:
                    if not isinstance(tag, dict):
                        continue
                    cid = tag.get("fracId") or tag.get("competencyThemeRefId") or ""
                    if cid and cid not in comp_levels:
                        comp_ids.append(cid)
                        comp_names.append(tag.get("competencyThemeName", ""))
                        comp_levels[cid] = None

            # Duration in hours
            dur_sec = item.get("duration", "0")
            try:
                dur_hrs = round(int(dur_sec) / 3600, 1) if dur_sec else 0.0
            except (ValueError, TypeError):
                dur_hrs = round((item.get("leafNodesCount") or 10) * 0.5, 1)
            if dur_hrs <= 0:
                dur_hrs = _FALLBACK_DURS

            # FIX (Bug #6): separate verified vs inferred TPAC.
            # "verified" = catalog JSON has explicit is_tpac: true field.
            # "inferred" = creator/org name matches NSSTA_CREATORS heuristic.
            # "none"     = no signal found.
            # Different boost factors apply: 1.15× verified, 1.05× inferred.
            raw_is_tpac = item.get("is_tpac", None)
            if raw_is_tpac is True:
                tpac_source = "verified"
                is_tpac = True
            elif raw_is_tpac is False:
                # The catalogue states it explicitly: not TPAC-vetted, whoever made it.
                tpac_source = "none"
                is_tpac = False
            else:
                creator = item.get("creator", "")
                orgs    = item.get("organisation", [])
                name_match = (
                    any(kw in creator for kw in NSSTA_CREATORS)
                    or any(any(kw in org for kw in NSSTA_CREATORS) for org in orgs)
                )
                if name_match:
                    tpac_source = "inferred"
                    is_tpac = True
                else:
                    tpac_source = "none"
                    is_tpac = False

            corpus_text = (
                (item.get("name", "") + " " + item.get("description", "")).lower().strip()
            )

            # FIX (Bug #7): use None for missing quality fields — no fabricated defaults.
            raw_rating    = item.get("rating")
            raw_count     = item.get("rating_count")
            raw_enroll    = item.get("enrollment_count")
            raw_compl     = item.get("completion_rate")

            doc = _CourseDoc(
                idx              = idx,
                identifier       = item.get("identifier", f"course_{idx}"),
                name             = item.get("name", ""),
                description      = item.get("description", ""),
                channel          = item.get("channel", ""),
                creator          = item.get("creator", ""),
                organisation     = item.get("organisation", []),
                duration_hrs     = dur_hrs,
                comp_ids         = comp_ids,
                comp_names       = comp_names,
                comp_levels      = comp_levels,
                rating           = float(raw_rating)    if raw_rating    is not None else None,
                rating_count     = int(raw_count)       if raw_count     is not None else None,
                enrollment_count = int(raw_enroll)      if raw_enroll    is not None else None,
                completion_rate  = float(raw_compl)     if raw_compl     is not None else None,
                is_tpac          = is_tpac,
                tpac_source      = tpac_source,
                corpus_text      = corpus_text,
                modality         = item.get("modality"),
                fmt              = item.get("format"),
            )
            self._catalog.append(doc)
            self._by_id[doc.identifier] = idx

            # Build reverse index: comp_id → doc indices
            for cid in comp_ids:
                self._comp_index.setdefault(cid, []).append(idx)

    # ── Catalogue-wide quality normalisers (Bug #10) ──────────────────────────

    def _build_quality_norms(self) -> None:
        """
        Fix the quality scale to the catalogue instead of to the shortlist.

        Quality used to be min-max normalised inside each gap's shortlist, so the
        worst course of every pool scored 0 on every component, and one course
        scored differently for two competencies. Every component is now an
        absolute catalogue-wide ratio, and a course simply *missing* a field takes
        the catalogue mean of that component (neutral) rather than the 0 it did
        not earn — ~9% of the catalogue carries no rating/enrolment data at all.
        """
        enrol = [float(d.enrollment_count) for d in self._catalog if d.enrollment_count is not None]
        pop_ref = math.log1p(float(np.percentile(enrol, _POP_REF_PCT))) if enrol else 0.0
        self._quality_norms["pop_ref"] = pop_ref if pop_ref > 0 else 1.0
        compl = [d.completion_rate for d in self._catalog if d.completion_rate is not None]
        shrunk = [_shrunk_rating(d.rating, d.rating_count) for d in self._catalog]
        rates = [(v - 1.0) / 4.0 for v in shrunk if v is not None]
        pops  = [min(math.log1p(e) / self._quality_norms["pop_ref"], 1.0) for e in enrol]
        self._quality_norms["completion_mean"] = float(np.mean(compl)) if compl else 0.5
        self._quality_norms["rating_mean"]     = float(np.mean(rates)) if rates else 0.5
        self._quality_norms["pop_mean"]        = float(np.mean(pops))  if pops  else 0.5
        logger.info(
            "[RecEngine] Quality scale: completion mean %.2f, rating mean %.2f, "
            "popularity mean %.2f (p%d enrolments = %.0f).",
            self._quality_norms["completion_mean"], self._quality_norms["rating_mean"],
            self._quality_norms["pop_mean"], _POP_REF_PCT,
            math.expm1(self._quality_norms["pop_ref"]),
        )

    def _neutral_quality(self) -> float:
        """Quality of a course the catalogue knows nothing about (an ACBP course
        that is not in the catalogue): the catalogue average, never 0."""
        n = self._quality_norms
        return round(0.35 * n.get("completion_mean", 0.5)
                     + 0.35 * n.get("rating_mean", 0.5)
                     + 0.20 * n.get("pop_mean", 0.5), 4)

    # ── Catalogue accessors ────────────────────────────────────────────────────

    def course_comp_levels(self) -> Dict[str, Dict[str, Optional[int]]]:
        """{courseId: {compId: FRAC level}} — feeds BaselineAssembler so the
        Verified channel and the candidate filter read the same tags."""
        return {d.identifier: dict(d.comp_levels) for d in self._catalog if d.comp_levels}

    def _corpus_embeddings(self, texts: List[str], stored: Dict[str, Tuple[str, np.ndarray]],
                           embedder) -> np.ndarray:
        """Stored vectors whose text hash still matches; encode (disk-memoised) the rest."""
        reuse: Dict[int, np.ndarray] = {}
        for i, doc in enumerate(self._catalog):
            hit = stored.get(doc.identifier)
            if hit is not None and hit[0] == self._text_hash[i]:
                reuse[i] = np.asarray(hit[1], dtype="float32")
        dims = {v.shape[-1] for v in reuse.values()}
        missing = [i for i in range(len(texts)) if i not in reuse]
        fresh = (encode_cached("catalog", [texts[i] for i in missing], kind="passage", embedder=embedder)
                 if missing else None)
        if fresh is not None and dims and fresh.shape[1] not in dims:
            reuse, missing = {}, list(range(len(texts)))          # model changed → re-encode all
            fresh = encode_cached("catalog", texts, kind="passage", embedder=embedder)
        self.embedding_stats = {"fromStore": len(reuse), "encoded": len(missing)}
        if not reuse:
            return fresh
        dim = next(iter(reuse.values())).shape[-1]
        out = np.zeros((len(texts), dim), dtype="float32")
        for i, v in reuse.items():
            out[i] = v
        for row, i in enumerate(missing):
            out[i] = fresh[row]
        return out

    def course_embeddings(self) -> List[Tuple[str, str, np.ndarray]]:
        """[(courseId, text_hash, vector)] — what catalogue_store persists."""
        return [(d.identifier, self._text_hash[i], self._embeddings[i]) for i, d in enumerate(self._catalog)]

    def set_measured_uplift(self, estimates: List[Dict[str, Any]]) -> None:
        """Attach per-course measured uplift (uplift_service.estimate_uplift) — SCIL v6 §6."""
        self._uplift = {e["courseId"]: e for e in estimates}

    def course_meta(self) -> Dict[str, Dict[str, Any]]:
        """{courseId: title, primary competency, format, rating, enrolments} for analytics views."""
        out = {}
        for d in self._catalog:
            comp = d.comp_ids[0] if d.comp_ids else None
            out[d.identifier] = {
                "title": d.name, "competencyName": self._frac_map.get(comp, {}).get("name", comp),
                "format": d.fmt, "rating": d.rating, "enrollmentCount": d.enrollment_count,
            }
        return out

    def course_hours(self, course_id: str) -> Optional[float]:
        """Catalogue duration in hours, or None for a course not in the catalogue."""
        idx = self._by_id.get(course_id)
        return self._catalog[idx].duration_hrs if idx is not None else None

    def levels_available(self, comp_id: str) -> Set[int]:
        """FRAC levels at which the catalogue has at least one course for comp_id."""
        return {
            lvl for i in self._comp_index.get(comp_id, [])
            if (lvl := self._catalog[i].comp_levels.get(comp_id))
        }

    def level_descriptor(self, comp_id: str, level: int) -> str:
        return self._frac_map.get(comp_id, {}).get("levels", {}).get(level, "")

    def crosswalk(self, comp_id: str, name: str = "") -> Optional[Dict[str, Any]]:
        """
        Map a role competency to the catalogue FRAC competency whose tagged
        courses and level ladder should serve it.

          * id already tagged in the catalogue → method "exact"
          * else an explicit entry in data/frac_crosswalk.json → method
            "curated_crosswalk" (+ its `confirmed` flag)
          * else nearest crosswalk anchor by embedding of the name, accepted
            only above the data-derived threshold → method "semantic_crosswalk"
            (unconfirmed — shown as such; a human should confirm it, SCIL v6 §5)
          * else None — no ladder; recommendations fall back to semantic search
        """
        if comp_id in self._comp_index:
            return {"catalogueId": comp_id, "method": "exact", "similarity": 1.0,
                    "catalogueName": self._frac_map.get(comp_id, {}).get("name", comp_id)}
        curated = self._xw_curated.get(comp_id)
        if curated:
            fid = curated["fracId"]
            return {"catalogueId": fid, "method": "curated_crosswalk", "similarity": None,
                    "confirmed": bool(curated.get("confirmed")),
                    "catalogueName": self._frac_map.get(fid, {}).get("name", fid)}
        text = (name or "").strip()
        if not text or not self._xw_ids:
            return None
        key = (comp_id, text)
        if key not in self._xw_cache:
            q = np.asarray(get_embedder("catalog").encode(
                [text], normalize_embeddings=True, show_progress_bar=False,
            ), dtype="float32")
            sims = self._xw_emb @ q[0]
            best = int(np.argmax(sims))
            result = None
            if float(sims[best]) > self._xw_threshold:
                fid = self._xw_ids[best]
                result = {"catalogueId": fid, "method": "semantic_crosswalk",
                          "similarity": round(float(sims[best]), 3),
                          "catalogueName": self._frac_map[fid]["name"]}
            self._xw_cache[key] = result
        return self._xw_cache[key]



    # ── Stage 0: Gap prioritization ────────────────────────────────────────────

    def calculate_gaps(
        self,
        baselines:  Dict[str, float],
        targets:    Dict[str, float],
        names:      Optional[Dict[str, str]] = None,
        confidence: Optional[Dict[str, str]] = None,
        catalogue_ids: Optional[Dict[str, str]] = None,
    ) -> List[GapEntry]:
        """
        Computes and prioritizes skill gaps.
        priority_k = gap_k * (target_k / 5.0)
        Returns list sorted by priority DESC.

        `baselines` are current FRAC levels (from baseline_assembler.resolve_level).
        A competency missing from `baselines` is UNASSESSED and is skipped —
        "no evidence" is not "level 0", and ranking it as the largest gap would
        push a full course at someone who may already be competent. Callers
        route those to a diagnostic instead. `names` supplies display names
        for competencies not in the FRAC file (no shared-state mutation), and
        `catalogue_ids` the crosswalk target (see crosswalk()) per competency.
        """
        names, confidence, catalogue_ids = names or {}, confidence or {}, catalogue_ids or {}
        gaps: List[GapEntry] = []
        for comp_id, target in targets.items():
            if comp_id not in baselines:
                continue
            baseline = baselines[comp_id]
            raw_gap  = round(target - baseline, 3)
            if raw_gap <= 0:
                continue
            comp_name    = names.get(comp_id) or self._frac_map.get(comp_id, {}).get("name") or comp_id
            priority     = round(raw_gap * (target / 5.0), 4)
            gaps.append(GapEntry(
                competencyId   = comp_id,
                competencyName = comp_name,
                currentLevel   = round(baseline, 3),
                targetLevel    = target,
                gapScore       = raw_gap,
                priorityScore  = priority,
                confidence     = confidence.get(comp_id),
                catalogueId    = catalogue_ids.get(comp_id),
            ))

        return sorted(gaps, key=lambda g: g.priorityScore, reverse=True)

    # ── Internal: dense + sparse retrieval for one gap ────────────────────────

    def _query_signals(self, comp_id: str, query_text: str) -> Tuple[np.ndarray, np.ndarray]:
        """(query embedding, BM25 scores over the whole corpus), cached."""
        key = (comp_id, query_text)
        hit = self._query_cache.get(key)
        if hit is None:
            q_emb = np.asarray(
                get_embedder("catalog").encode(
                    [query_text], normalize_embeddings=True, show_progress_bar=False
                ),
                dtype="float32",
            )
            bm25 = np.asarray(self._bm25.get_scores(query_text.lower().split()))
            hit = (q_emb, bm25)
            self._query_cache[key] = hit
        return hit

    def _query_text(self, gap: GapEntry) -> str:
        return self._comp_query_text(gap.catalogue_key, gap.competencyName)

    def _comp_query_text(self, comp_id: str, fallback_name: str = "") -> str:
        """The official FRAC name + description used as the retrieval anchor."""
        frac_meta = self._frac_map.get(comp_id, {})
        return f"{frac_meta.get('name', fallback_name)}. {frac_meta.get('description', '')}".strip()

    def _untagged_null(self, comp_id: str, q_emb: np.ndarray) -> Tuple[float, float, float]:
        """
        (median, mean, std) of the cosine between the competency query and the
        courses NOT tagged with it — the null distribution for "an unrelated
        course", derived from the data with no tuned constant.

        The median is the tag-support threshold: a tagged course at or below it is
        no more about this competency than a typical untagged one, so its author
        tag is flagged (SCIL v6 §6 — author tags are never checked against
        content). The mean and std calibrate the absolute semantic score.
        """
        hit = self._untagged_stats.get(comp_id)
        if hit is None:
            tagged = set(self._comp_index.get(comp_id, []))
            others = [i for i in range(len(self._catalog)) if i not in tagged]
            sims = self._embeddings[others] @ q_emb[0] if others else np.zeros(1)
            hit = (float(np.median(sims)), float(np.mean(sims)),
                   max(float(np.std(sims)), _SEM_MIN_SIGMA))
            self._untagged_stats[comp_id] = hit
        return hit

    def _tag_support_threshold(self, comp_id: str, q_emb: np.ndarray) -> float:
        """Median of the untagged null — see `_untagged_null`."""
        return self._untagged_null(comp_id, q_emb)[0]

    def _relevance(
        self,
        idx:     int,
        comp_id: str,
        q_emb:   np.ndarray,
        bm25:    np.ndarray,
        lex_ref: float,
        rrf_raw: Optional[float] = None,
    ) -> float:
        """
        Absolute relevance of one course to one competency, in [0,1] (Bug #9) —
        `_REL_W_SEM`·semantic + `_REL_W_LEX`·lexical + `_REL_W_FUS`·fusion.

        `rrf_raw` is the course's fused rank score inside this gap's candidate
        pool. Without one — a semantic fallback (no tag-filtered pool to rank
        against) or a mandatory course scored on its own — the two pool-free
        signals are re-weighted to carry the whole score, so the number stays
        comparable instead of losing a third of its range.
        """
        _, mu, sigma = self._untagged_null(comp_id, q_emb)
        cos = float(self._embeddings[idx] @ q_emb[0])
        return self._blend_relevance(_logistic((cos - mu) / sigma),
                                     float(bm25[idx]), lex_ref, rrf_raw)

    def _blend_relevance(self, sem: float, bm25_raw: float, lex_ref: float,
                         rrf_raw: Optional[float]) -> float:
        lex = bm25_raw / (bm25_raw + lex_ref) if bm25_raw > 0 else 0.0
        if rrf_raw is None:
            w = _REL_W_SEM + _REL_W_LEX
            return round(_clamp01((_REL_W_SEM * sem + _REL_W_LEX * lex) / w), 4)
        # The TPAC boost can push RRF past its unboosted ceiling — that is the
        # boost doing its job, and the clamp keeps the scale honest at 1.0.
        fus = _clamp01(rrf_raw / _RRF_MAX)
        return round(_clamp01(_REL_W_SEM * sem + _REL_W_LEX * lex + _REL_W_FUS * fus), 4)

    def _retrieve_for_gap(
        self,
        gap: GapEntry,
        top_k: int = 20,
        levels: Optional[Set[int]] = None,
    ) -> List[Tuple[int, float]]:
        """
        Stage 1 + Stage 2 for a single competency gap.
        Returns list of (catalog_idx, rrf_score) sorted by rrf_score DESC.

        `levels` restricts Stage 1 to courses tagged with this competency at
        one of those FRAC levels (an empty result is returned as-is — the
        caller decides whether to stretch to another level).

        Fallback: if the competency has NO tagged courses at all, degrades to a
        full-corpus semantic search (FAISS only, no BM25 boost). Those results
        carry no level for this competency, so they are never level-filtered.
        """
        # Stage 1: FRAC-tag filter (+ level filter)
        tagged = self._comp_index.get(gap.catalogue_key, [])
        semantic_fallback = len(tagged) == 0
        if semantic_fallback:
            logger.info(
                "[RecEngine] No FRAC-tagged courses for '%s' (%s) — using full semantic fallback.",
                gap.competencyName, gap.catalogue_key,
            )
            candidate_indices: List[int] = []
        elif levels is None:
            candidate_indices = list(tagged)
        else:
            candidate_indices = [
                i for i in tagged
                if self._catalog[i].comp_levels.get(gap.catalogue_key) in levels
            ]
            if not candidate_indices:
                return []

        # Stage 2: Build query anchor from official FRAC description
        q_emb, bm25_scores = self._query_signals(gap.catalogue_key, self._query_text(gap))

        if semantic_fallback:
            # Full corpus FAISS search — return top_k directly
            n_search = min(len(self._catalog), top_k)
            _scores, dense_indices_raw = self._faiss_index.search(q_emb, n_search)
            results: List[Tuple[int, float]] = []
            for idx, score in zip(dense_indices_raw[0], _scores[0]):
                if idx >= 0:
                    rrf = float(score) * _TPAC_BOOST.get(self._catalog[idx].tpac_source, 1.0)  # raw cosine as proxy
                    results.append((int(idx), rrf))
            return results

        # Normal path — Stage 1 candidates exist.
        # 2a. Dense: exact cosine for every candidate (vectors are L2-normalised).
        #     The pool is at most a few dozen courses, so this is cheaper than a
        #     corpus-wide FAISS probe — and unlike a top-N probe it can't leave a
        #     candidate without a dense rank.
        dense_sims  = self._embeddings[candidate_indices] @ q_emb[0]
        dense_order = sorted(zip(candidate_indices, dense_sims), key=lambda x: x[1], reverse=True)
        dense_rank: Dict[int, int] = {idx: r + 1 for r, (idx, _) in enumerate(dense_order)}

        # 2b. Sparse search (BM25), candidates only
        cand_bm25    = [(i, bm25_scores[i]) for i in candidate_indices]
        cand_bm25.sort(key=lambda x: x[1], reverse=True)
        sparse_rank: Dict[int, int] = {idx: r + 1 for r, (idx, _) in enumerate(cand_bm25)}

        # 2c. RRF fusion + TPAC boost (verified 1.25×, inferred 1.10×)
        rrf_scores: Dict[int, float] = {}
        for idx in candidate_indices:
            rrf  = 1.0 / (_RRF_K + dense_rank[idx]) + 1.0 / (_RRF_K + sparse_rank[idx])
            rrf_scores[idx] = rrf * _TPAC_BOOST.get(self._catalog[idx].tpac_source, 1.0)

        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:top_k]

    # ── Internal: Stage 3 quality scoring ─────────────────────────────────────

    def _quality_score(self, doc: _CourseDoc, shortlist: Optional[List[_CourseDoc]] = None) -> float:
        """
        quality = 0.35*completion + 0.35*rating + 0.20*log-popularity + 0.10*tpac,
        on an ABSOLUTE catalogue-wide scale (Bug #10). `shortlist` is accepted for
        call-site compatibility and ignored — that argument is exactly what used
        to make the same course score 0.90 for one gap and 0.10 for another.

        * completion — the published completion rate, already a ratio in [0,1]
        * rating     — Bayesian-shrunk stars mapped from 1..5 onto 0..1 (Bug #5:
                       shrinkage, not a Wilson bound, which is binomial-only)
        * popularity — log1p(enrolments) / log1p(p95 enrolments), capped at 1
        * tpac       — 1.0 verified, 0.5 inferred, 0 none (Bug #6)

        A missing field takes the catalogue mean of its component. Bug #7 scored
        it 0 instead, which quietly punished the ~9% of courses that carry no
        rating or enrolment data and dragged them to a fabricated 0% match.
        """
        n = self._quality_norms
        completion_n = (doc.completion_rate if doc.completion_rate is not None
                        else n.get("completion_mean", 0.5))
        shrunk   = _shrunk_rating(doc.rating, doc.rating_count)
        rating_n = (shrunk - 1.0) / 4.0 if shrunk is not None else n.get("rating_mean", 0.5)
        pop_n    = (min(math.log1p(doc.enrollment_count) / (n.get("pop_ref") or 1.0), 1.0)
                    if doc.enrollment_count is not None else n.get("pop_mean", 0.5))
        tpac_flag = 1.0 if doc.tpac_source == "verified" else (0.5 if doc.tpac_source == "inferred" else 0.0)
        return round(
            0.35 * _clamp01(completion_n)
            + 0.35 * _clamp01(rating_n)
            + 0.20 * _clamp01(pop_n)
            + 0.10 * tpac_flag,
            4,
        )

    # ── Internal: Stages 1-3 for one gap's candidate pool ─────────────────────

    def _score_candidates(
        self,
        gap:         GapEntry,
        levels:      Optional[Set[int]],
        exclude_ids: Set[str],
        pool_size:   int = 50,
    ) -> List[RecommendationResult]:
        """
        Retrieve (tag + level filtered), drop excluded courses, then score
        final = 0.6·relevance + 0.4·quality over the surviving pool.
        Sorted by finalScore DESC; priorityRank is left at 0 for the caller.
        """
        retrieved = [
            (idx, score)
            for idx, score in self._retrieve_for_gap(gap, top_k=pool_size, levels=levels)
            if self._catalog[idx].identifier not in exclude_ids
        ]
        if not retrieved:
            return []

        # Relevance and quality are both absolute now (Bugs #9/#10): nothing here
        # is min-maxed against the shortlist, so the bottom course of a pool is no
        # longer forced to 0.000 and two gaps' scores are directly comparable.
        shortlist_docs = [self._catalog[idx] for idx, _ in retrieved]
        is_tagged  = bool(self._comp_index.get(gap.catalogue_key))
        match_type = "frac_tag" if is_tagged else "semantic_fallback"
        current, target = int(gap.currentLevel), int(math.ceil(gap.targetLevel))
        q_emb, bm25 = self._query_signals(gap.catalogue_key, self._query_text(gap))
        lex_ref     = _lex_ref(bm25)
        support_thr = self._tag_support_threshold(gap.catalogue_key, q_emb) if is_tagged else 0.0
        ce_norm = self._cross_encoder_norm(gap, retrieved)   # {idx: P(relevant)} over the top 20, or {}

        results: List[RecommendationResult] = []
        for (idx, rrf_raw), doc in zip(retrieved, shortlist_docs):
            # A semantic fallback has no tag-filtered pool, so `rrf_raw` there is a
            # bare cosine and carries no fusion rank — see `_relevance`.
            relevance_n = self._relevance(idx, gap.catalogue_key, q_emb, bm25, lex_ref,
                                          rrf_raw=rrf_raw if is_tagged else None)
            if idx in ce_norm:
                # Stage 2b: blend with the cross-encoder over the re-ranked head only.
                # A course the re-ranker never looked at keeps its own score instead
                # of being zeroed for not having been looked at.
                relevance_n = round(0.5 * relevance_n + 0.5 * ce_norm[idx], 4)
            quality_n   = self._quality_score(doc)
            final       = round(0.6 * relevance_n + 0.4 * quality_n, 4)
            course_level = doc.comp_levels.get(gap.catalogue_key)
            tag_supported = (
                bool(float(self._embeddings[idx] @ q_emb[0]) > support_thr) if is_tagged else None
            )

            # Build human-readable match reasons
            reasons = [f"FRAC tag: {gap.competencyName}"]
            uplift = self._uplift.get(doc.identifier) or {}
            if uplift.get("misTagFlag"):
                reasons.append("Measured uplift near zero in outcome data — flagged for review")
            if tag_supported is False:
                reasons.append("Tag flagged for review — course content doesn't clearly match this competency")
            if course_level:
                if course_level > target:
                    reasons.append(f"Level {course_level} stretch — no closer-level course in the catalogue")
                elif course_level == current + 1:
                    reasons.append(f"Level {course_level} — the next step up from your Level {current}")
                else:
                    reasons.append(f"Level {course_level} — on the way to your target Level {target}")
            if doc.tpac_source == "verified":
                reasons.append("NSSTA TPAC-vetted course (verified)")
            elif doc.tpac_source == "inferred":
                reasons.append("NSSTA TPAC-vetted course (inferred)")
            # Thresholds read against the absolute scale (Bug #9): a tag-filtered,
            # level-gated candidate normally lands in the 0.7-0.95 band, so the
            # chip only appears for a course that stands out inside that band.
            if relevance_n >= 0.90:
                reasons.append("Very close match to the official FRAC description")
            elif relevance_n >= 0.75:
                reasons.append("Good match to the FRAC description")
            if quality_n >= 0.70:
                reasons.append("Top-rated in category")

            results.append(RecommendationResult(
                courseId       = doc.identifier,
                title          = doc.name,
                provider       = doc.creator or doc.channel or "iGOT Karmayogi",
                durationHours  = doc.duration_hrs,
                finalScore     = final,
                relevanceScore = round(relevance_n, 4),
                qualityScore   = round(quality_n, 4),
                isTpac         = doc.is_tpac,
                competencyId   = gap.competencyId,
                competencyName = gap.competencyName,
                priorityRank   = 0,
                matchReasons   = reasons,
                matchType      = match_type,       # Bug #6
                tpacSource     = doc.tpac_source,  # Bug #6
                courseLevel    = course_level,
                tagSupported   = tag_supported,
                measuredUplift = uplift.get("measuredUplift"),
                upliftFlag     = uplift.get("misTagFlag"),
                modality       = doc.modality,
                reranked       = (idx in ce_norm) if ce_norm else None,
                why            = self._why(gap, doc, course_level, uplift, tag_supported),
            ))

        # Content-supported tags first, then finalScore — so wherever a level
        # has a course that genuinely teaches the competency, it wins.
        # A flagged course (content doesn't match the tag, or measured uplift ≈ 0) is
        # used only when nothing else exists at that level — never hidden.
        results.sort(key=lambda r: (r.tagSupported is False or bool(r.upliftFlag), -r.finalScore))
        return results

    def _cross_encoder_norm(self, gap: GapEntry, retrieved: List[Tuple[int, float]]) -> Dict[int, float]:
        """
        P(relevant) from the cross-encoder for the top RERANK_TOP_N by RRF; {} if
        disabled. The logits go through a sigmoid — their natural calibration —
        rather than a min-max over the head, which used to hand the weakest of the
        20 a 0.000 even when the re-ranker rated it highly in absolute terms.
        """
        from ai.reranker import RERANK_TOP_N, rerank_scores
        top = sorted(retrieved, key=lambda x: x[1], reverse=True)[:RERANK_TOP_N]
        if len(top) < 2:
            return {}
        passages = [f"{self._catalog[i].name}. {self._catalog[i].description}" for i, _ in top]
        scores = rerank_scores(self._query_text(gap), passages)
        if scores is None:
            return {}
        return {i: _logistic(float(sc)) for (i, _), sc in zip(top, scores)}

    def _why(self, gap: GapEntry, doc: _CourseDoc, course_level: Optional[int],
             uplift: Dict[str, Any], tag_supported: Optional[bool]) -> Dict[str, Any]:
        """
        Structured "why recommended": the gap it closes, the level step it
        covers and its badges (TPAC verified / inferred, measured improvement).
        Built from the same fields the ranking used; nothing new is inferred.
        """
        current, target = int(gap.currentLevel), int(math.ceil(gap.targetLevel))
        if not course_level:
            kind = "untagged_level"
        elif course_level > target:
            kind = "stretch"
        elif course_level == current + 1:
            kind = "next_step"
        else:
            kind = "on_the_way"
        badges = []
        if doc.tpac_source == "verified":
            badges.append({"key": "tpac_verified", "label": "TPAC verified"})
        elif doc.tpac_source == "inferred":
            badges.append({"key": "tpac_inferred", "label": "TPAC (inferred)"})
        mu = uplift.get("measuredUplift")
        if mu is not None and not uplift.get("misTagFlag") and mu > 0:
            badges.append({"key": "measured_improvement", "label": f"Measured +{mu:.1f} level",
                           "value": round(float(mu), 2)})
        if tag_supported is False or uplift.get("misTagFlag"):
            badges.append({"key": "under_review", "label": "Tag under review"})
        step = f"Level {current} → {course_level}" if course_level else "level not tagged"
        summary = {
            "next_step": f"Closes your {gap.competencyName} gap one step: {step} (target {target}).",
            "on_the_way": f"Builds {gap.competencyName} from Level {current} towards target {target} ({step}).",
            "stretch": f"No course at Levels {current + 1}–{target}; this Level-{course_level} course covers the gap.",
            "untagged_level": f"Semantically closest course for {gap.competencyName}.",
        }[kind]
        return {
            "gap": {"competencyId": gap.competencyId, "competencyName": gap.competencyName,
                    "currentLevel": current, "targetLevel": target, "gap": gap.gapScore},
            "levelStep": {"from": current, "to": course_level, "kind": kind},
            "badges": badges,
            "summary": summary,
        }

    def order_gaps_by_opportunity(self, gaps: List[GapEntry],
                                  opportunity: Dict[str, Optional[str]]) -> List[GapEntry]:
        """
        SCIL v6 §4 tie-break: gaps whose priority is within OPPORTUNITY_TIE_BAND
        (10%) of each other are near-ties; among them the competency the
        official's office uses more this cycle (High > Medium > Low) goes first.
        Ordinal only — a clearly larger gap always stays ahead.
        """
        out = list(gaps)

        def rank(g: GapEntry) -> int:
            return _OPPORTUNITY_RANK.get(opportunity.get(g.competencyId) or "", 0)

        changed = True
        while changed:                    # adjacent swaps inside tie bands until stable
            changed = False
            for i in range(len(out) - 1):
                a, b = out[i], out[i + 1]
                near = abs(a.priorityScore - b.priorityScore) <= OPPORTUNITY_TIE_BAND * max(a.priorityScore, 1e-9)
                if near and rank(b) > rank(a):
                    out[i], out[i + 1] = b, a
                    changed = True
        return out

    def mandatory_recommendations(
        self,
        mandatory:    List[Dict[str, Any]],
        exclude_ids:  Set[str],
        gaps:         Dict[str, GapEntry],
        names:        Optional[Dict[str, str]] = None,
    ) -> List[RecommendationResult]:
        """
        ACBP mandatory courses (the departmental training plan) as recommendations,
        always included whatever their score and listed APAR-linked first, then
        best match — the order the ACBP happens to list them in is not a ranking.
        `gaps` is keyed by catalogue competency id, so a mandatory course that
        also closes a gap says so.
        """
        out: List[RecommendationResult] = []
        apar: Dict[str, bool] = {}
        for m in mandatory:
            cid = m.get("courseId")
            if not cid or cid in exclude_ids:
                continue
            idx = self._by_id.get(cid)
            doc = self._catalog[idx] if idx is not None else None
            comp = m.get("competencyId") or ""
            gap = gaps.get(comp)
            comp_key = gap.catalogue_key if gap else comp
            level = m.get("level") or (doc.comp_levels.get(comp) if doc else None)
            comp_name = ((gap.competencyName if gap else None) or (names or {}).get(comp)
                         or self._frac_map.get(comp, {}).get("name") or comp)
            if gap and doc:
                why = self._why(gap, doc, level, self._uplift.get(cid) or {}, None)
            else:
                why = {"gap": None, "levelStep": {"from": None, "to": level, "kind": "mandatory"},
                       "badges": [], "summary": m.get("reason") or "Mandatory in your capacity-building plan."}
            why["badges"] = [{"key": "mandatory", "label": "Mandatory"
                              + (" · APAR-linked" if m.get("aparLinked") else "")}] + why["badges"]
            apar[cid] = bool(m.get("aparLinked"))
            reasons = ["Mandatory in your Annual Capacity Building Plan"
                       + (" (APAR-linked)" if m.get("aparLinked") else "")]
            if m.get("reason"):
                reasons.append(m["reason"])
            # Bug #12: these used to be shipped as a flat finalScore 1.0 / quality
            # 0.0, so every ACBP course claimed a 100% match it had not been scored
            # for. They are scored like any other course — the Mandatory badge, not
            # a fake score, is what pins them to the top of the list.
            relevance, quality = self._score_one(doc, m.get("title") or "", comp_key, comp_name)
            out.append(RecommendationResult(
                courseId=cid, title=(doc.name if doc else m.get("title") or cid),
                provider=((doc.creator or doc.channel) if doc else "") or "iGOT Karmayogi",
                durationHours=(doc.duration_hrs if doc else float(m.get("hours") or _FALLBACK_DURS)),
                finalScore=round(0.6 * relevance + 0.4 * quality, 4),
                relevanceScore=relevance, qualityScore=quality,
                isTpac=bool(doc and doc.is_tpac), competencyId=(gap.competencyId if gap else comp),
                competencyName=comp_name, priorityRank=0, matchReasons=reasons, matchType="acbp_mandatory",
                tpacSource=(doc.tpac_source if doc else "none"), courseLevel=level,
                modality=(doc.modality if doc else None), mandatory=True, why=why,
            ))
        out.sort(key=lambda r: (not apar.get(r.courseId, False), -(r.finalScore or 0.0)))
        return out

    def _score_one(self, doc: Optional[_CourseDoc], title: str,
                   comp_id: str, comp_name: str) -> Tuple[float, float]:
        """
        (relevance, quality) for a single course scored on its own, with no
        candidate pool behind it — an ACBP mandatory course. A course the
        catalogue does not have is embedded from its title so it still gets a
        real semantic score, and takes the catalogue's average quality.
        """
        query = self._comp_query_text(comp_id, comp_name)
        if not query.strip(" ."):
            return (self._neutral_quality(), self._quality_score(doc) if doc else self._neutral_quality())
        try:
            q_emb, bm25 = self._query_signals(comp_id, query)
            if doc is not None:
                return (self._relevance(doc.idx, comp_id, q_emb, bm25, _lex_ref(bm25)),
                        self._quality_score(doc))
            vec = encode_cached("catalog", [title or comp_name], kind="passage")
            _, mu, sigma = self._untagged_null(comp_id, q_emb)
            sem = _logistic((float(vec[0] @ q_emb[0]) - mu) / sigma)
            return (self._blend_relevance(sem, 0.0, 1.0, None), self._neutral_quality())
        except Exception as exc:                       # never block an ACBP course
            logger.debug("[RecEngine] mandatory course scoring failed (%s)", exc)
            return (self._neutral_quality(),
                    self._quality_score(doc) if doc else self._neutral_quality())

    # ── Public API ─────────────────────────────────────────────────────────────

    def get_recommendations(
        self,
        gaps:           List[GapEntry],
        limit_per_gap:  int = 3,
        enrolled_ids:   Optional[set] = None,
    ) -> List[RecommendationResult]:
        """
        Returns deduplicated, level-gated recommendations in gap-priority order.

        Only courses tagged at a level the official still has to climb
        (current < level <= target) are eligible. If the catalogue has none in
        that band, the nearest level above target is offered as a flagged
        stretch.

        Within a gap, level interleaving and the modality spread choose *which*
        courses to show (a ladder across levels and a mix of formats, never three
        Level-5 courses), and the block is then shown best match first.

        FIX (Bug #11): the block used to be returned in level order, so a weak
        Level-2 course sat above a far better Level-4 one and the list disagreed
        with the match score printed on every card. The order to *study* them in
        is the pathway's job (`build_pathway`), not this list's.

        FIX (Bug #8): no global finalScore sort — per-gap blocks are
        concatenated in calculate_gaps() priority order, and priorityRank is
        the 1-based position in that concatenation.
        """
        enrolled_ids = set(enrolled_ids or ())
        seen_course_ids: Set[str] = set()
        all_results: List[RecommendationResult] = []

        for gap in gaps:
            current, target = int(gap.currentLevel), int(math.ceil(gap.targetLevel))
            available = self.levels_available(gap.catalogue_key)
            levels: Optional[Set[int]] = None     # no levelled tags → level-agnostic
            if available:
                levels = set(range(current + 1, target + 1))
                if not (available & levels):
                    above = sorted(lvl for lvl in available if lvl > target)
                    if above:
                        levels = {above[0]}

            scored = self._score_candidates(
                gap, levels, enrolled_ids | seen_course_ids,
                pool_size=max(limit_per_gap * 5, 50),
            )
            picked = _by_score(_spread_modalities(_interleave_by_level(scored), limit_per_gap))
            seen_course_ids.update(r.courseId for r in picked)
            all_results.extend(picked)

        for rank, rec in enumerate(all_results, start=1):
            rec.priorityRank = rank

        return all_results

    # ── Stage 4: learning pathway for one competency ──────────────────────────

    def build_pathway(
        self,
        comp_id:        str,
        comp_name:      str,
        current_level:  Optional[int],
        target_level:   int,
        confidence:     str = "LOW",
        basis:          str = "evidence",
        evidence_level: Optional[int] = None,
        completed_ids:  Optional[Set[str]] = None,
        in_progress:    Optional[Dict[str, float]] = None,
        n_alternatives: int = 2,
        role_comp_id:   Optional[str] = None,
        crosswalk:      Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Step-by-step path for one competency: one course per FRAC level from
        current+1 to target, lowest level first.

        `comp_id` is the CATALOGUE competency whose tagged courses form the
        ladder; `role_comp_id` (default: comp_id) is the id the official's role
        profile uses, echoed back as `competencyId` so the UI can match it.

          * diagnostic  — first, when the level is UNASSESSED, inferred only
                          (LOW) or self-reported: confirm before skipping rungs.
          * bridge      — only for self-reported levels: the rungs between what
                          the evidence supports and what was claimed. Optional
                          if the claim is accurate; not counted in totalHours.
          * course      — the best course at the next level.
          * continue    — an in-progress course at that level wins over a new one.
          * stretch     — the catalogue has no course at a level, so the next
                          level's course covers it (reported in coverageGaps).
          * optional    — target already met: one course to go further.

        `current_level` None means UNASSESSED; the path then provisionally
        starts at Level 0. Completed courses are never suggested.
        """
        completed_ids = set(completed_ids or ())
        in_progress   = dict(in_progress or {})
        role_id = role_comp_id or comp_id
        name    = comp_name or self._frac_map.get(comp_id, {}).get("name") or role_id
        start   = max(0, min(_MAX_LEVEL, int(current_level or 0)))
        target  = max(0, min(_MAX_LEVEL, int(target_level)))
        gap     = max(0, target - start)
        entry   = GapEntry(
            competencyId=role_id, competencyName=name, currentLevel=start,
            targetLevel=target, gapScore=gap, priorityScore=round(gap * target / 5.0, 4),
            confidence=confidence, catalogueId=comp_id,
        )

        steps: List[Dict[str, Any]] = []
        diagnostic = _diagnostic_step(
            start, confidence, basis, evidence_level, unassessed=current_level is None,
        )
        if diagnostic:
            steps.append(diagnostic)

        bridge_from = start
        if basis == "self_report" and evidence_level is not None and evidence_level < start:
            bridge_from = evidence_level

        # One retrieval + scoring pass for every level we might place.
        by_level: Dict[int, List[RecommendationResult]] = {}
        if bridge_from < _MAX_LEVEL and self.levels_available(comp_id):
            for r in self._score_candidates(
                entry, set(range(bridge_from + 1, _MAX_LEVEL + 1)), completed_ids, pool_size=200,
            ):
                if r.courseLevel:
                    by_level.setdefault(r.courseLevel, []).append(r)   # finalScore DESC

        # Bridge rungs (self-reported levels only)
        for lvl in range(bridge_from + 1, start + 1):
            if by_level.get(lvl):
                steps.append(self._course_step(
                    comp_id, lvl - 1, lvl, [lvl], by_level[lvl], in_progress,
                    n_alternatives, kind="bridge",
                ))

        # Required rungs: current+1 .. target
        holes: List[int] = []
        level_reached = start
        for lvl in range(start + 1, target + 1):
            if not by_level.get(lvl):
                holes.append(lvl)
                continue
            steps.append(self._course_step(
                comp_id, level_reached, lvl, holes + [lvl], by_level[lvl], in_progress, n_alternatives,
            ))
            level_reached, holes = lvl, []

        unreachable: List[int] = []
        if holes:
            # Nothing at the top of the ladder — the closest course above target covers it.
            above = [lvl for lvl in range(target + 1, _MAX_LEVEL + 1) if by_level.get(lvl)]
            if above:
                steps.append(self._course_step(
                    comp_id, level_reached, target, holes, by_level[above[0]], in_progress, n_alternatives,
                ))
            else:
                unreachable = holes

        if gap == 0 and start < _MAX_LEVEL:
            nxt = next((lvl for lvl in range(start + 1, _MAX_LEVEL + 1) if by_level.get(lvl)), None)
            if nxt:
                steps.append(self._course_step(
                    comp_id, start, nxt, [nxt], by_level[nxt], in_progress,
                    n_alternatives, kind="optional",
                ))

        for i, s in enumerate(steps, start=1):
            s["order"] = i

        catalogue_levels = self.levels_available(comp_id)
        required = [s for s in steps if s["kind"] in ("course", "continue", "stretch")]
        message = None
        if gap == 0:
            status = "met"
        elif not required:
            status = "no_content"
            message = (
                "No course in the catalogue is tagged with this competency at a FRAC level, "
                "so no level-by-level path can be built. See Recommended Courses for "
                "semantically related content."
                if not catalogue_levels else
                f"The catalogue has no course above Level {start} for this competency."
            )
        elif unreachable:
            status = "partial"
            message = f"No course in the catalogue reaches Level {_fmt_levels(unreachable)}."
        else:
            status = "ready"

        return {
            "competencyId":      role_id,
            "catalogueCompetencyId": comp_id,
            "crosswalk":         crosswalk,
            "message":           message,
            "competencyName":    name,
            "currentLevel":      current_level,
            "startLevel":        start,
            "targetLevel":       target,
            "gap":               gap,
            "priorityScore":     entry.priorityScore,
            "confidence":        confidence,
            "basis":             basis,
            "evidenceLevel":     evidence_level,
            "status":            status,
            "needsDiagnostic":   diagnostic is not None,
            "steps":             steps,
            "totalHours":        round(sum(s["hours"] or 0 for s in required), 1),
            "bridgeHours":       round(sum(s["hours"] or 0 for s in steps if s["kind"] == "bridge"), 1),
            "coverageGaps":      [lvl for lvl in range(start + 1, target + 1) if lvl not in catalogue_levels],
            "unreachableLevels": unreachable,
            # courses used in this path whose FRAC tag isn't supported by content
            "tagReviewFlags":    sorted({
                s["course"]["courseId"] for s in steps
                if s["course"] and s["course"]["tagSupported"] is False
            }),
        }

    def _course_step(
        self,
        comp_id:     str,
        from_level:  int,
        to_level:    int,
        covers:      List[int],
        candidates:  List[RecommendationResult],
        in_progress: Dict[str, float],
        n_alternatives: int,
        kind:        Optional[str] = None,
    ) -> Dict[str, Any]:
        """One rung of a ladder. Finishing an in-progress course beats starting a new one."""
        ongoing = [r for r in candidates if r.courseId in in_progress]
        choice  = max(ongoing, key=lambda r: in_progress[r.courseId]) if ongoing else candidates[0]
        pct     = float(in_progress.get(choice.courseId, 0.0))
        course_level = choice.courseLevel or to_level

        if kind is None:
            if ongoing:
                kind = "continue"
            elif len(covers) > 1 or course_level > to_level:
                kind = "stretch"
            else:
                kind = "course"

        missing = [lvl for lvl in covers if lvl != course_level]
        if kind == "continue":
            reason = (f"You're {pct:.0f}% through this Level-{course_level} course — "
                      f"finish it before starting anything new.")
        elif kind == "stretch" and course_level > to_level:
            reason = (f"The catalogue has no course at Level {_fmt_levels(missing)}; this "
                      f"Level-{course_level} course is the closest and goes beyond your target.")
        elif kind == "stretch":
            reason = (f"The catalogue has no course at Level {_fmt_levels(missing)}, so this "
                      f"Level-{course_level} course covers it too — expect a steeper step.")
        elif kind == "bridge":
            reason = (f"Level {to_level} is only self-reported. Skip this if the diagnostic "
                      f"confirms it; otherwise it fills the gap below your claimed level.")
        elif kind == "optional":
            reason = f"Target met. Optional: this Level-{course_level} course takes you further."
        else:
            reason = f"Takes you from Level {from_level} to Level {to_level}."
        if choice.upliftFlag:
            reason += (" Note: outcome data shows near-zero measured uplift for this course; it is the "
                       "only option at this level and is flagged for review.")
        if choice.tagSupported is False:
            reason += (" Note: no course at this level clearly matches the competency by content; "
                       "this one's FRAC tag is flagged for review.")

        return {
            "kind":            kind,
            "fromLevel":       from_level,
            "toLevel":         to_level,
            "covers":          covers,
            "levelDescriptor": self.level_descriptor(comp_id, to_level),
            "course":          _course_summary(choice, pct),
            "hours":           round(choice.durationHours * (1 - pct / 100.0), 1),
            "reason":          reason,
            "alternatives":    [
                _course_summary(r) for r in candidates if r.courseId != choice.courseId
            ][:n_alternatives],
        }

    # ── Stage 4b: one study plan across all competencies ──────────────────────

    def build_study_plan(
        self,
        pathways:      List[Dict[str, Any]],
        budget_hours:  Optional[float] = None,
        mandatory:     Optional[List[Dict[str, Any]]] = None,
        completed_ids: Optional[Set[str]] = None,
        in_progress:   Optional[Dict[str, float]] = None,
        classroom_cap_hours: Optional[float] = None,
        prerequisites: Optional[List[Dict[str, Any]]] = None,
        current_levels: Optional[Dict[str, Optional[int]]] = None,
    ) -> Dict[str, Any]:
        """
        Orders the required rungs of several pathways into one sequence.

        SCIL v6 §5 cost-benefit greedy: among courses that are the NEXT rung of
        some ladder, repeatedly take the one with the highest
            Σ_c priority_c × levels_covered_c  /  hours
        summed over every competency it is the next rung for — a course tagged
        at the right level for two gaps counts for both and advances both.
        Ladder order is the within-competency prerequisite chain: a Level-4
        course is never scheduled before the Level-3 rung of the same
        competency. With a budget, a course that no longer fits blocks its
        ladder (later rungs depend on it) while other ladders keep going.

        SCIL v6 §5 constraints:
          * `mandatory` (ACBP, APAR-linked) courses are force-included FIRST,
            whatever their gain/hour and even beyond the budget (overBudget is
            then reported). Completed ones are listed as done; a ladder whose
            rung a mandatory course satisfies advances with it.
          * `classroom_cap_hours` caps classroom hours in this plan (modality
            mix); a classroom course that would exceed it blocks its ladder.
          * `prerequisites` (cross-competency DAG, see prerequisite_service)
            keep a rung off the frontier until its prerequisite levels are met.

        Opportunity to practise (pathway["opportunity"]["level"], SCIL v6 §4)
        is only an ordinal tie-breaker among frontier courses whose gain/hour is
        within OPPORTUNITY_TIE_BAND of the best; it never scales a score.

        UNASSESSED competencies are not scheduled — their diagnostic comes
        first (listed under `diagnostics`). Bridge / optional steps are never
        scheduled. When a shared course satisfies another ladder's rung, that
        pathway's step is updated in place to point at the shared course (its
        own pick becomes the first alternative), so plan and pathways agree.
        """
        completed_ids = set(completed_ids or ())
        in_progress   = dict(in_progress or {})
        diagnostics: List[Dict[str, Any]] = []
        ladders: List[Dict[str, Any]] = []
        for p in sorted(pathways, key=lambda p: p["priorityScore"], reverse=True):
            if p.get("needsDiagnostic"):
                diag = next(s for s in p["steps"] if s["kind"] == "diagnostic")
                diagnostics.append({
                    "competencyId":   p["competencyId"],
                    "competencyName": p["competencyName"],
                    "reason":         diag["reason"],
                })
            if p["confidence"] == "UNASSESSED":
                continue
            rungs = [s for s in p["steps"] if s["kind"] in ("course", "continue", "stretch")]
            if rungs:
                ladders.append({"p": p, "rungs": rungs, "ptr": 0, "blocked": False, "why": None})

        gate = _PrerequisiteGate(prerequisites, current_levels, ladders,
                                 names={c: m.get("name", c) for c, m in self._frac_map.items()})
        plan: List[Dict[str, Any]] = []
        taken: Dict[str, Dict[str, Any]] = {}      # courseId → plan step
        totals = {"used": 0.0, "classroom": 0.0}

        def open_ladders() -> List[Dict[str, Any]]:
            return [l for l in ladders if not l["blocked"] and l["ptr"] < len(l["rungs"])]

        def advance(m: Dict[str, Any], cid: str) -> Dict[str, Any]:
            rung = m["rungs"][m["ptr"]]
            if rung["course"]["courseId"] != cid:
                self._swap_in_shared_course(rung, cid, m["p"]["catalogueCompetencyId"])
            m["ptr"] += 1
            return {
                "competencyId":   m["p"]["competencyId"],
                "competencyName": m["p"]["competencyName"],
                "fromLevel":      rung["fromLevel"],
                "toLevel":        rung["toLevel"],
                "covers":         rung["covers"],
            }

        def add_step(cid: str, course: Dict[str, Any], kind: str, hours: float,
                     advances: List[Dict[str, Any]], **extra: Any) -> None:
            totals["used"] += hours
            modality = self._modality(cid)
            if modality == "classroom":
                totals["classroom"] += hours
            step = {
                "order":           len(plan) + 1,
                "courseId":        cid,
                "title":           course["title"],
                "provider":        course["provider"],
                "isTpac":          course["isTpac"],
                "kind":            kind,
                "hours":           round(hours, 1),
                "cumulativeHours": round(totals["used"], 1),
                "advances":        advances,
                "modality":        modality,
                "mandatory":       False,
                **extra,
            }
            plan.append(step)
            taken[cid] = step

        def absorb() -> None:
            """A ladder whose next rung is a course already in the plan advances for free
            (once its prerequisites are met — the gate still orders it)."""
            moved = True
            while moved:
                moved = False
                for m in open_ladders():
                    if not gate.check(m)[0]:
                        continue
                    cid = next((c for c in taken if self._satisfies(c, m)), None)
                    if cid is not None:
                        taken[cid]["advances"].append(advance(m, cid))
                        moved = True

        # 1 ── Mandatory ACBP courses: force-included first ──────────────────
        mandatory_out: List[Dict[str, Any]] = []
        for mc in mandatory or []:
            cid = mc["courseId"]
            if cid in completed_ids:
                mandatory_out.append({**mc, "status": "completed"})
                continue
            if cid in taken:
                continue
            pct   = float(in_progress.get(cid, 0.0))
            full  = self.course_hours(cid) or float(mc.get("hours") or 0.0)
            hours = full * (1 - pct / 100.0)
            advances = [advance(m, cid) for m in open_ladders() if self._satisfies(cid, m)]
            add_step(cid, self._doc_summary(cid, mc.get("title")), "mandatory", hours, advances,
                     mandatory=True, selectedBy="mandatory_acbp", opportunity=None,
                     reason=mc.get("reason") or "Mandatory (ACBP)")
            mandatory_out.append({**mc, "status": "in_progress" if pct else "scheduled"})
        absorb()

        # 2 ── Greedy over the ladders' frontier ─────────────────────────────
        while True:
            active = open_ladders()
            if not active:
                break
            eligible = []
            for owner in active:
                ok, why = gate.check(owner)
                if ok:
                    eligible.append(owner)
                else:
                    owner["why"] = why
            if not eligible:
                for m in active:                       # nothing reachable: waiting on prerequisites
                    m["blocked"] = True
                break

            # Frontier = each eligible ladder's next rung (deduplicated by course).
            frontier: Dict[str, Dict[str, Any]] = {}
            for owner in eligible:
                rung = owner["rungs"][owner["ptr"]]
                frontier.setdefault(rung["course"]["courseId"], rung)

            cands = []
            for cid, rung in frontier.items():
                advances = [m for m in eligible if self._satisfies(cid, m)]
                gain  = sum(m["p"]["priorityScore"] * len(m["rungs"][m["ptr"]]["covers"]) for m in advances)
                hours = rung["hours"] or 0.0
                opp   = max((_OPPORTUNITY_RANK.get(((m["p"].get("opportunity") or {}).get("level"))) or 0
                             for m in advances), default=0)
                # ties: more total gain, then shorter, then course id (deterministic)
                key   = (gain / max(hours, _MIN_STEP_HRS), gain, -hours, cid)
                cands.append({"key": key, "cid": cid, "hours": hours, "rung": rung,
                              "advances": advances, "opp": opp})
            by_ratio = max(cands, key=lambda c: c["key"])
            # SCIL v6 §4: opportunity to practise is an ORDINAL tie-breaker among
            # candidates within OPPORTUNITY_TIE_BAND of the best gain/hour — never
            # a multiplier on the score, and it never removes a candidate.
            floor = by_ratio["key"][0] * (1.0 - OPPORTUNITY_TIE_BAND)
            best = max((c for c in cands if c["key"][0] >= floor),
                       key=lambda c: (c["opp"], c["key"]))

            blocked_why = None
            if budget_hours is not None and totals["used"] + best["hours"] > budget_hours + 1e-9:
                blocked_why = "over budget"
            elif (classroom_cap_hours is not None and self._modality(best["cid"]) == "classroom"
                  and totals["classroom"] + best["hours"] > classroom_cap_hours + 1e-9):
                blocked_why = "classroom cap"
            if blocked_why:
                # Can't take it: every ladder whose own next rung IS this course is stuck.
                for m in active:
                    if m["rungs"][m["ptr"]]["course"]["courseId"] == best["cid"]:
                        m["blocked"], m["why"] = True, blocked_why
                continue

            advanced = [advance(m, best["cid"]) for m in best["advances"]]
            add_step(best["cid"], best["rung"]["course"], best["rung"]["kind"], best["hours"], advanced,
                     opportunity=_OPPORTUNITY_LEVEL.get(best["opp"]),
                     selectedBy="opportunity_tie_break" if best["cid"] != by_ratio["cid"] else "gain_per_hour")
            absorb()

        deferred = [
            {
                "competencyId":   l["p"]["competencyId"],
                "competencyName": l["p"]["competencyName"],
                "remainingSteps": len(l["rungs"]) - l["ptr"],
                "remainingHours": round(sum(r["hours"] or 0 for r in l["rungs"][l["ptr"]:]), 1),
                "reason":         l["why"] or "over budget",
            }
            for l in ladders if l["ptr"] < len(l["rungs"])
        ]

        return {
            "budgetHours":       budget_hours,
            "totalHours":        round(totals["used"], 1),
            "overBudget":        budget_hours is not None and totals["used"] > budget_hours + 1e-9,
            "classroomCapHours": classroom_cap_hours,
            "classroomHours":    round(totals["classroom"], 1),
            "mandatory":         mandatory_out,
            "diagnostics":       diagnostics,
            "steps":             plan,
            "deferred":          deferred,
            "prerequisitesApplied": gate.applied,
            "method":      ("mandatory ACBP courses first; then greedy priority-weighted levels per hour over "
                            "FRAC level ladders (SCIL v6 §5) within the budget, classroom cap and prerequisite "
                            f"DAG; near-ties within {OPPORTUNITY_TIE_BAND:.0%} of the best go to the higher "
                            "opportunity to practise (SCIL v6 §4, ordinal only)"),
        }

    def _modality(self, course_id: str) -> Optional[str]:
        idx = self._by_id.get(course_id)
        return self._catalog[idx].modality if idx is not None else None

    def _doc_summary(self, course_id: str, title: Optional[str] = None) -> Dict[str, Any]:
        idx = self._by_id.get(course_id)
        if idx is None:
            return {"title": title or course_id, "provider": "iGOT Karmayogi", "isTpac": False}
        doc = self._catalog[idx]
        return {"title": doc.name, "provider": doc.creator or doc.channel or "iGOT Karmayogi",
                "isTpac": doc.is_tpac}

    def _satisfies(self, course_id: str, ladder: Dict[str, Any]) -> bool:
        """Does taking `course_id` complete this ladder's next rung?"""
        rung = ladder["rungs"][ladder["ptr"]]
        if rung["course"]["courseId"] == course_id:
            return True
        if rung["kind"] == "continue":        # never abandon an in-progress course
            return False
        idx = self._by_id.get(course_id)
        if idx is None:
            return False
        level = self._catalog[idx].comp_levels.get(ladder["p"]["catalogueCompetencyId"])
        return level is not None and level == rung["course"]["courseLevel"]

    def _swap_in_shared_course(self, rung: Dict[str, Any], course_id: str, comp_id: str) -> None:
        own = rung["course"]
        alt = next((a for a in rung["alternatives"] if a["courseId"] == course_id), None)
        if alt is None:
            doc = self._catalog[self._by_id[course_id]]
            alt = {
                "courseId": doc.identifier, "title": doc.name,
                "provider": doc.creator or doc.channel or "iGOT Karmayogi",
                "durationHours": doc.duration_hrs, "courseLevel": doc.comp_levels.get(comp_id),
                "isTpac": doc.is_tpac, "tpacSource": doc.tpac_source,
                "finalScore": None, "relevanceScore": None, "qualityScore": None,
                "tagSupported": None, "progressPercentage": 0.0,
            }
        rung["alternatives"] = [own] + [a for a in rung["alternatives"] if a["courseId"] != course_id]
        rung["course"] = alt
        rung["reason"] += " Shared: this course also advances another of your gaps."


class _PrerequisiteGate:
    """
    Cross-competency prerequisite DAG for build_study_plan (SCIL v6 §5, B4).

    A rung of competency X that closes level Lx is on the frontier only when
    every edge A@La → X@Lx is met: A's level — its ladder's progress in THIS
    plan, else the official's current level — is at least La. That is what
    orders "A first, then X". An unknown level (A not in the official's
    profile, or UNASSESSED) is advisory: reported, never enforced, so a
    missing measurement can't dead-end a plan. Edges must already be
    validated acyclic (prerequisite_service.validate_edges).
    """

    def __init__(self, edges, current_levels, ladders, names=None):
        self._into: Dict[str, List[Dict[str, Any]]] = {}
        for e in edges or []:
            self._into.setdefault(e["to"]["competencyId"], []).append(e)
        self._levels = dict(current_levels or {})
        self._ladders = {l["p"]["catalogueCompetencyId"]: l for l in ladders}
        self._names = names or {}
        self._status: Dict[str, Dict[str, Any]] = {}

    def level_of(self, comp: str) -> Optional[int]:
        ladder = self._ladders.get(comp)
        if ladder is not None:
            return ladder["rungs"][ladder["ptr"] - 1]["toLevel"] if ladder["ptr"] else ladder["p"]["startLevel"]
        return self._levels.get(comp)

    def check(self, ladder: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        comp = ladder["p"]["catalogueCompetencyId"]
        rung = ladder["rungs"][ladder["ptr"]]
        covers = set(rung.get("covers") or [rung["toLevel"]])
        waiting = None
        for e in self._into.get(comp, []):
            if int(e["to"]["level"]) not in covers:
                continue
            a, need = e["from"]["competencyId"], int(e["from"]["level"])
            have = self.level_of(a)
            rec = self._status.setdefault(e.get("id") or f"{a}>{comp}", {
                "edgeId": e.get("id"),
                "from": {"competencyId": a, "competencyName": self._names.get(a, a), "level": need},
                "to": {"competencyId": comp, "competencyName": ladder["p"]["competencyName"],
                       "level": int(e["to"]["level"])},
                "status": None,
            })
            if have is None:
                rec["status"] = rec["status"] or "advisory"
            elif have < need:
                rec["status"] = "blocked"          # becomes "ordered" if it is met later in the plan
                waiting = waiting or f"prerequisite: {self._names.get(a, a)} Level {need} first"
            elif rec["status"] == "blocked":
                rec["status"] = "ordered"
            elif rec["status"] is None:
                rec["status"] = "met"
        return waiting is None, waiting

    @property
    def applied(self) -> List[Dict[str, Any]]:
        """Edges that changed or annotate the plan: ordered (waited, then met), blocked, advisory."""
        return [r for r in self._status.values() if r["status"] in ("ordered", "blocked", "advisory")]


# ── Module helpers ─────────────────────────────────────────────────────────────

def _interleave_by_level(results: List[RecommendationResult]) -> List[RecommendationResult]:
    """Best course of each level (ascending), then the second-best of each, …
    Input must already be in preference order (as _score_candidates returns it)."""
    by_level: Dict[Optional[int], List[RecommendationResult]] = {}
    for r in results:
        by_level.setdefault(r.courseLevel, []).append(r)
    order = sorted(by_level, key=lambda lvl: (lvl is None, lvl or 0))
    out: List[RecommendationResult] = []
    depth = 0
    while len(out) < len(results):
        for lvl in order:
            if depth < len(by_level[lvl]):
                out.append(by_level[lvl][depth])
        depth += 1
    return out


def _by_score(picks: List[RecommendationResult]) -> List[RecommendationResult]:
    """
    Best match first (Bug #11). A course whose tag the content does not support,
    or whose measured uplift is ~0, stays last however well it scores — it is a
    last resort at its level, never hidden and never promoted. Equal scores are
    broken by the lower FRAC level, which is the one to take first.
    """
    return sorted(picks, key=lambda r: (r.tagSupported is False or bool(r.upliftFlag),
                                        -(r.finalScore or 0.0),
                                        r.courseLevel or _MAX_LEVEL + 1))


# A course of a format not yet picked for this gap may replace the next in line
# if it is at the same level, among the next 3 candidates, and its finalScore is
# within this margin of it — near-equal courses only, never a clearly worse one.
_MODALITY_SWAP_MARGIN = 0.15
_MODALITY_WINDOW = 3


def _spread_modalities(ordered: List[RecommendationResult], k: int) -> List[RecommendationResult]:
    """
    Pick k from `ordered` (already in preference order) but spread formats
    (self-paced, classroom, virtual lab): at each slot, a near-equal candidate
    with an unseen modality is taken ahead of a repeat. The picks keep their
    interleaved order (best of each level, lowest level first).
    """
    pool, picked, seen = list(ordered), [], set()
    while pool and len(picked) < k:
        head = pool[0]
        choice = head
        if head.modality in seen:
            for cand in pool[1:_MODALITY_WINDOW + 1]:
                if (cand.modality and cand.modality not in seen
                        and cand.finalScore >= head.finalScore - _MODALITY_SWAP_MARGIN
                        and (cand.courseLevel or 0) == (head.courseLevel or 0)):
                    choice = cand
                    break
        pool.remove(choice)
        picked.append(choice)
        if choice.modality:
            seen.add(choice.modality)
    order = {id(r): i for i, r in enumerate(ordered)}
    return sorted(picked, key=lambda r: order[id(r)])


def text_hash(text: str) -> str:
    """Stable hash of a course's embedded text — decides whether a stored vector is still valid."""
    import hashlib
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def _course_summary(r: RecommendationResult, progress: float = 0.0) -> Dict[str, Any]:
    return {
        "courseId":           r.courseId,
        "title":              r.title,
        "provider":           r.provider,
        "durationHours":      r.durationHours,
        "courseLevel":        r.courseLevel,
        "isTpac":             r.isTpac,
        "tpacSource":         r.tpacSource,
        "finalScore":         r.finalScore,
        "relevanceScore":     r.relevanceScore,
        "qualityScore":       r.qualityScore,
        "tagSupported":       r.tagSupported,
        "measuredUplift":     r.measuredUplift,
        "upliftFlag":         r.upliftFlag,
        "progressPercentage": progress,
    }


def _fmt_levels(levels: List[int]) -> str:
    return ", ".join(str(lvl) for lvl in levels) if levels else "?"


def _diagnostic_step(
    current: int, confidence: str, basis: str, evidence_level: Optional[int], unassessed: bool,
) -> Optional[Dict[str, Any]]:
    """High-uncertainty levels get a short check before a full course (SCIL v6 §2)."""
    if unassessed or confidence == "UNASSESSED":
        reason = ("No evidence of your level yet. Take the practice assessment first so the "
                  "path starts where you really are — until then it assumes Level 0.")
    elif basis == "self_report":
        reason = (f"Level {current} is self-reported; evidence so far supports Level "
                  f"{evidence_level or 0}. A practice assessment confirms it before you skip "
                  f"the lower steps.")
    elif confidence == "LOW":
        reason = ("Your level is inferred from tenure and education only. A practice "
                  "assessment confirms it.")
    else:
        return None
    return {
        "kind": "diagnostic", "fromLevel": current, "toLevel": current, "covers": [],
        "levelDescriptor": "", "course": None, "hours": None, "reason": reason,
        "alternatives": [], "action": "practice_assessment",
    }




# ─────────────────────────────────────────────────────────────────────────────
# Smoke-test — run: python -m services.recommendation_service
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    print("=" * 70)
    print("Hybrid Recommendation Engine — Smoke Test")
    print("=" * 70)

    engine = HybridRecommendationEngine()

    # Mock baselines and targets using real FRAC IDs from the catalog
    mock_baselines = {
        "comp_nat_accounts_001":    1.5,
        "comp_survey_design_002":   2.0,
        "comp_big_data_006":        0.5,
    }
    mock_targets = {
        "comp_nat_accounts_001":    4.0,
        "comp_survey_design_002":   4.0,
        "comp_big_data_006":        3.0,
    }

    print("\n--- STAGE 0: Prioritised Skill Gaps ---")
    gaps = engine.calculate_gaps(mock_baselines, mock_targets)
    for g in gaps:
        print(f"  [{g.priorityScore:.3f}] {g.competencyName}: "
              f"{g.currentLevel} → {g.targetLevel} (gap={g.gapScore})")

    print("\n--- STAGES 1-3: Hybrid Recommendations ---")
    recs = engine.get_recommendations(gaps, limit_per_gap=2)
    for r in recs:
        tpac_tag = " 🛡 NSSTA" if r.isTpac else ""
        print(f"\n  #{r.priorityRank} [{r.finalScore:.3f}] {r.title}{tpac_tag}")
        print(f"     Gap  : {r.competencyName}")
        print(f"     Scores: relevance={r.relevanceScore:.3f}  quality={r.qualityScore:.3f}")
        print(f"     Why  : {' | '.join(r.matchReasons)}")

    assert len(recs) > 0, "FAILED: No recommendations returned!"
    assert all(0.0 <= r.finalScore <= 1.0 for r in recs), "FAILED: finalScore out of [0,1]!"
    assert all(r.competencyId in mock_targets for r in recs), "FAILED: Stage 1 filter broken — untagged course leaked!"
    for r in recs:
        g = next(g for g in gaps if g.competencyId == r.competencyId)
        assert r.courseLevel is None or r.courseLevel > int(g.currentLevel), \
            f"FAILED: level gate — Level-{r.courseLevel} course for an official at {g.currentLevel}"

    print("\n--- STAGE 4: Learning pathways + study plan ---")
    pathways = [
        engine.build_pathway(g.competencyId, g.competencyName, int(g.currentLevel),
                             int(g.targetLevel), confidence="HIGH")
        for g in gaps
    ]
    for p in pathways:
        print(f"\n  {p['competencyName']}: L{p['startLevel']} → L{p['targetLevel']} "
              f"[{p['status']}] {p['totalHours']}h, catalogue holes={p['coverageGaps']}")
        for s in p["steps"]:
            title = s["course"]["title"] if s["course"] else "Practice assessment"
            print(f"     {s['order']}. [{s['kind']}] L{s['fromLevel']}→L{s['toLevel']}  {title}")
        levels = [s["toLevel"] for s in p["steps"] if s["kind"] != "diagnostic"]
        assert levels == sorted(levels), "FAILED: pathway not in ascending level order!"
    plan = engine.build_study_plan(pathways, budget_hours=None)
    print(f"\n  Study plan: {len(plan['steps'])} courses, {plan['totalHours']}h")
    for s in plan["steps"]:
        print(f"     {s['order']}. {s['title']} ({s['hours']}h) → "
              + ", ".join(f"{a['competencyName']} L{a['toLevel']}" for a in s["advances"]))
    print("\nSUCCESS: All assertions passed.")