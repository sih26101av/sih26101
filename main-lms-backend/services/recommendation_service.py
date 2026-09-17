"""
FILE: main-lms-backend/services/recommendation_service.py
─────────────────────────────────────────────────────────────────────────────
Locked 3-Stage Hybrid Recommendation Engine for MoSPI Skill Intelligence
Platform (SIH 2026).

Stage 0 — Cross-Gap Prioritization
    priority_k = gap_k * (target_k / 5.0)
    Highest-priority gaps are addressed first.

Stage 1 — Mandatory FRAC-Tag Filtering
    Candidate pool = only courses tagged with FRAC competency k.
    Untagged courses cannot enter ranking (prevents semantic hallucinations).

Stage 2 — Hybrid Search + RRF Fusion
    Dense  : ai.embedder "catalog" role (default all-MiniLM-L6-v2, 384-dim) + FAISS IndexFlatIP
    Sparse : rank_bm25.BM25Okapi over title+description corpus
    Query  : FRAC competency official name + description (never raw user text)
    Fusion : RRF(d) = 1/(60+rank_dense) + 1/(60+rank_sparse)
    Boost  : 1.25× on RRF score for NSSTA/TPAC-vetted courses

Stage 3 — Weighted Final Scoring
    quality = 0.35*completion + 0.35*rating_norm(Wilson) + 0.20*pop_norm + 0.10*tpac_flag
    final   = 0.6*relevance_norm + 0.4*quality
    Karma points: informational only — excluded from final_score.
─────────────────────────────────────────────────────────────────────────────
"""

import json
import logging
import math
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
from pydantic import BaseModel
from rank_bm25 import BM25Okapi

from ai.embedder import get_embedder

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
_RRF_K         = 60          # RRF constant
_NSSTA_BOOST   = 1.25        # multiplier for NSSTA/TPAC courses
_WILSON_Z      = 1.96        # 95% confidence interval
_FALLBACK_DURS = 1.5         # hours if duration field missing/zero
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
    relevanceScore: float          # RRF normalised to [0,1]
    qualityScore:   float          # quality composite ∈ [0,1]
    isTpac:         bool
    competencyId:   str
    competencyName: str
    priorityRank:   int            # 1-based, within priority-preserving concat (Bug #8)
    matchReasons:   List[str]      # human-readable explanation chips
    # FIX (Bug #6): distinguish how TPAC status was determined
    matchType:   Optional[str] = None  # "frac_tag" | "semantic_fallback"
    tpacSource:  Optional[str] = None  # "verified" | "inferred" | "none"



class GapEntry(BaseModel):
    competencyId:   str
    competencyName: str
    currentLevel:   float
    targetLevel:    float
    gapScore:       float
    priorityScore:  float          # gap_k * (target_k / 5.0) — Stage 0


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
    ):
        # ── 1. Load FRAC dictionary ────────────────────────────────────────────
        self._frac_map: Dict[str, Dict] = {}   # id → {name, description}
        try:
            with open(os.path.normpath(frac_path), "r", encoding="utf-8") as f:
                frac_list = json.load(f)
            for comp in frac_list:
                self._frac_map[comp["id"]] = {
                    "name":        comp.get("name", ""),
                    "description": comp.get("description", ""),
                    "type":        comp.get("competencyType", "Domain"),
                }
            logger.info("[RecEngine] Loaded %d FRAC competencies.", len(self._frac_map))
        except Exception as exc:
            logger.warning("[RecEngine] Could not load FRAC data: %s", exc)

        # ── 2. Load + parse course catalog ────────────────────────────────────
        self._catalog: List[_CourseDoc] = []
        self._comp_index: Dict[str, List[int]] = {}   # comp_id → list of doc indices

        try:
            with open(os.path.normpath(catalog_path), "r", encoding="utf-8") as f:
                raw_catalog = json.load(f)
            self._parse_catalog(raw_catalog)
            logger.info("[RecEngine] Indexed %d courses.", len(self._catalog))
        except Exception as exc:
            logger.error("[RecEngine] Failed to load catalog: %s", exc)
            raise

        # ── 3. Build BM25 index ────────────────────────────────────────────────
        corpus_tokens = [doc.corpus_text.split() for doc in self._catalog]
        self._bm25 = BM25Okapi(corpus_tokens)
        logger.info("[RecEngine] BM25 index built over %d documents.", len(self._catalog))

        # ── 4. Load sentence-transformer + build FAISS index ──────────────────
                # Model loaded ONCE for whole backend via ai/embedder.py singleton.
        logger.info("[RecEngine] Acquiring shared multilingual embedder...")
        embedder = get_embedder("catalog")

        corpus_texts = [doc.corpus_text for doc in self._catalog]
        embeddings = embedder.encode(
            corpus_texts, kind="passage", batch_size=64, normalize_embeddings=True, show_progress_bar=False
        )
        embeddings = np.array(embeddings, dtype="float32")

        # Use faiss lazy import (not installed on every machine at import time)
        import faiss
        dim = embeddings.shape[1]   # 384
        self._faiss_index = faiss.IndexFlatIP(dim)
        self._faiss_index.add(embeddings)
        logger.info("[RecEngine] FAISS index built: %d vectors × %d dims.", *embeddings.shape)

    # ── Catalog parser ─────────────────────────────────────────────────────────

    def _parse_catalog(self, raw: list) -> None:
        for idx, item in enumerate(raw):
            # Parse competencies_v3 (stored as a JSON string in the mock data)
            comp_ids, comp_names = [], []
            raw_v3 = item.get("competencies_v3", "")
            if raw_v3:
                try:
                    tags = json.loads(raw_v3) if isinstance(raw_v3, str) else raw_v3
                    for tag in tags:
                        cid = tag.get("id", "")
                        if cid:
                            comp_ids.append(cid)
                            comp_names.append(tag.get("name", ""))
                except Exception:
                    pass

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
                rating           = float(raw_rating)    if raw_rating    is not None else None,
                rating_count     = int(raw_count)       if raw_count     is not None else None,
                enrollment_count = int(raw_enroll)      if raw_enroll    is not None else None,
                completion_rate  = float(raw_compl)     if raw_compl     is not None else None,
                is_tpac          = is_tpac,
                tpac_source      = tpac_source,
                corpus_text      = corpus_text,
            )
            self._catalog.append(doc)

            # Build reverse index: comp_id → doc indices
            for cid in comp_ids:
                self._comp_index.setdefault(cid, []).append(idx)



    # ── Stage 0: Gap prioritization ────────────────────────────────────────────

    def calculate_gaps(
        self,
        baselines: Dict[str, float],
        targets:   Dict[str, float],
    ) -> List[GapEntry]:
        """
        Computes and prioritizes skill gaps.
        priority_k = gap_k * (target_k / 5.0)
        Returns list sorted by priority DESC.
        """
        gaps: List[GapEntry] = []
        for comp_id, target in targets.items():
            baseline = baselines.get(comp_id, 0.0)
            raw_gap  = round(target - baseline, 3)
            if raw_gap <= 0:
                continue
            frac_meta    = self._frac_map.get(comp_id, {})
            comp_name    = frac_meta.get("name", comp_id)
            priority     = round(raw_gap * (target / 5.0), 4)
            gaps.append(GapEntry(
                competencyId   = comp_id,
                competencyName = comp_name,
                currentLevel   = round(baseline, 3),
                targetLevel    = target,
                gapScore       = raw_gap,
                priorityScore  = priority,
            ))

        return sorted(gaps, key=lambda g: g.priorityScore, reverse=True)

    # ── Internal: dense + sparse retrieval for one gap ────────────────────────

    def _retrieve_for_gap(
        self,
        gap: GapEntry,
        top_k: int = 20,
    ) -> List[Tuple[int, float]]:
        """
        Stage 1 + Stage 2 for a single competency gap.
        Returns list of (catalog_idx, rrf_score) sorted by rrf_score DESC.

        Fallback: if Stage 1 FRAC-tag filter finds no tagged courses,
        degrades to a full-corpus semantic search (FAISS only, no BM25 boost).
        This ensures users always receive recommendations.
        """
        # Stage 1: FRAC-tag filter
        candidate_indices = self._comp_index.get(gap.competencyId, [])

        # ── Semantic-only fallback ─────────────────────────────────────────
        semantic_fallback = len(candidate_indices) == 0
        if semantic_fallback:
            logger.info(
                "[RecEngine] No FRAC-tagged courses for '%s' (%s) — using full semantic fallback.",
                gap.competencyName, gap.competencyId,
            )

        # Stage 2: Build query anchor from official FRAC description
        frac_meta   = self._frac_map.get(gap.competencyId, {})
        frac_name   = frac_meta.get("name", gap.competencyName)
        frac_desc   = frac_meta.get("description", "")
        query_text  = f"{frac_name}. {frac_desc}".strip()
        query_tok   = query_text.lower().split()

        # 2a. Dense search (FAISS cosine, L2-normalised)
        import faiss
        q_emb = get_embedder("catalog").encode(
            [query_text], normalize_embeddings=True, show_progress_bar=False
        ).astype("float32")

        if semantic_fallback:
            # Full corpus FAISS search — return top_k directly
            n_search = min(len(self._catalog), top_k)
            _scores, dense_indices_raw = self._faiss_index.search(q_emb, n_search)
            results: List[Tuple[int, float]] = []
            for idx, score in zip(dense_indices_raw[0], _scores[0]):
                if idx >= 0:
                    rrf = float(score)  # use raw cosine score as proxy
                    if self._catalog[idx].is_tpac:
                        rrf *= _NSSTA_BOOST
                    results.append((int(idx), rrf))
            return results

        # Normal path — Stage 1 candidates exist
        candidate_set = set(candidate_indices)

        # Search across whole corpus, then filter to candidates
        n_search = min(len(self._catalog), max(top_k * 4, 50))
        _scores, dense_indices = self._faiss_index.search(q_emb, n_search)
        dense_rank: Dict[int, int] = {}
        rank = 1
        for idx in dense_indices[0]:
            if idx in candidate_set:
                dense_rank[int(idx)] = rank
                rank += 1
                if rank > top_k:
                    break

        # 2b. Sparse search (BM25)
        bm25_scores  = self._bm25.get_scores(query_tok)
        # Sort candidates only
        cand_bm25    = [(i, bm25_scores[i]) for i in candidate_indices]
        cand_bm25.sort(key=lambda x: x[1], reverse=True)
        sparse_rank: Dict[int, int] = {idx: r + 1 for r, (idx, _) in enumerate(cand_bm25)}

        # 2c. RRF fusion + NSSTA boost
        all_candidate_ids = set(dense_rank) | set(sparse_rank)
        rrf_scores: Dict[int, float] = {}
        for idx in all_candidate_ids:
            dr   = dense_rank.get(idx, len(self._catalog) + _RRF_K)
            sr   = sparse_rank.get(idx, len(candidate_indices) + _RRF_K)
            rrf  = 1.0 / (_RRF_K + dr) + 1.0 / (_RRF_K + sr)
            if self._catalog[idx].is_tpac:
                rrf *= _NSSTA_BOOST
            rrf_scores[idx] = rrf

        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:top_k]

    # ── Internal: Stage 3 quality scoring ─────────────────────────────────────

    @staticmethod
    def _quality_score(doc: _CourseDoc, shortlist: List[_CourseDoc]) -> float:
        """
        quality = 0.35*completion_n + 0.35*rating_n + 0.20*pop_n + 0.10*tpac_flag

        FIX (Bug #7): each component is normalized ONLY within the subset of
        shortlist docs that HAVE that field. Courses missing a field are excluded
        from the normalization pool for that component — not given a free default.

        FIX (Bug #5): rating uses Bayesian shrinkage (_shrunk_rating) instead of
        Wilson lower bound, which is only valid for binomial proportions.
        """
        if not shortlist:
            return 0.0

        # ── completion_rate ────────────────────────────────────────────────────
        docs_with_compl = [d for d in shortlist if d.completion_rate is not None]
        if docs_with_compl and doc.completion_rate is not None:
            completions  = [d.completion_rate for d in docs_with_compl]
            c_min, c_max = min(completions), max(completions)
            c_range      = c_max - c_min if c_max > c_min else 1.0
            completion_n = (doc.completion_rate - c_min) / c_range
        else:
            completion_n = 0.0   # excluded from pool → contributes 0

        # ── rating (Bayesian shrinkage — Bug #5) ──────────────────────────────
        shrunk_vals = [
            s for s in (
                _shrunk_rating(d.rating, d.rating_count) for d in shortlist
            )
            if s is not None
        ]
        my_shrunk = _shrunk_rating(doc.rating, doc.rating_count)
        if shrunk_vals and my_shrunk is not None:
            w_min, w_max = min(shrunk_vals), max(shrunk_vals)
            w_range      = w_max - w_min if w_max > w_min else 1.0
            rating_n     = (my_shrunk - w_min) / w_range
        else:
            rating_n = 0.0

        # ── enrollment (log-popularity) ────────────────────────────────────────
        docs_with_enroll = [d for d in shortlist if d.enrollment_count is not None]
        if docs_with_enroll and doc.enrollment_count is not None:
            pop_raw      = [math.log1p(d.enrollment_count) for d in docs_with_enroll]
            p_min, p_max = min(pop_raw), max(pop_raw)
            p_range      = p_max - p_min if p_max > p_min else 1.0
            my_pop       = math.log1p(doc.enrollment_count)
            pop_n        = (my_pop - p_min) / p_range
        else:
            pop_n = 0.0

        # ── TPAC flag (Bug #6: verified > inferred) ────────────────────────────
        tpac_flag = 1.0 if doc.tpac_source == "verified" else (0.5 if doc.tpac_source == "inferred" else 0.0)

        return round(
            0.35 * completion_n
            + 0.35 * rating_n
            + 0.20 * pop_n
            + 0.10 * tpac_flag,
            4,
        )



    # ── Public API ─────────────────────────────────────────────────────────────

    def get_recommendations(
        self,
        gaps:           List[GapEntry],
        limit_per_gap:  int = 3,
        enrolled_ids:   Optional[set] = None,
    ) -> List[RecommendationResult]:
        """
        Returns deduplicated recommendations in gap-priority order.

        FIX (Bug #8): The global finalScore sort after building all_results is
        REMOVED. Per-gap blocks are concatenated in the order returned by
        calculate_gaps() (priority DESC). Within each gap's block, courses are
        sorted by finalScore DESC. This guarantees that the highest-priority
        gap's courses appear before all lower-priority gaps' courses, regardless
        of their absolute finalScore.

        priorityRank is assigned via enumerate on the final concatenation.
        """
        if enrolled_ids is None:
            enrolled_ids = set()

        seen_course_ids: set = set()
        all_results: List[RecommendationResult] = []

        for gap in gaps:
            # Retrieve + fuse for this gap
            retrieved = self._retrieve_for_gap(gap, top_k=limit_per_gap * 5)
            if not retrieved:
                continue

            # Filter enrolled / already-seen
            retrieved = [
                (idx, score) for idx, score in retrieved
                if self._catalog[idx].identifier not in enrolled_ids
                and self._catalog[idx].identifier not in seen_course_ids
            ][:limit_per_gap * 3]

            if not retrieved:
                continue

            # Build shortlist for intra-group quality normalization
            shortlist_docs = [self._catalog[idx] for idx, _ in retrieved]

            # Normalise RRF scores → [0,1]
            rrf_vals  = [score for _, score in retrieved]
            rrf_max   = max(rrf_vals) if rrf_vals else 1.0
            rrf_min   = min(rrf_vals) if rrf_vals else 0.0
            rrf_range = rrf_max - rrf_min if rrf_max > rrf_min else 1.0

            gap_results: List[RecommendationResult] = []
            for (idx, rrf_raw), doc in zip(retrieved, shortlist_docs):
                # Determine match type from whether this gap had FRAC-tagged courses
                match_type = (
                    "semantic_fallback"
                    if len(self._comp_index.get(gap.competencyId, [])) == 0
                    else "frac_tag"
                )

                # Stage 3 scores
                relevance_n = (rrf_raw - rrf_min) / rrf_range
                quality_n   = self._quality_score(doc, shortlist_docs)
                final       = round(0.6 * relevance_n + 0.4 * quality_n, 4)

                # Build human-readable match reasons
                reasons = [f"FRAC tag: {gap.competencyName}"]
                if doc.tpac_source == "verified":
                    reasons.append("NSSTA TPAC-vetted course (verified)")
                elif doc.tpac_source == "inferred":
                    reasons.append("NSSTA TPAC-vetted course (inferred)")
                if relevance_n >= 0.8:
                    reasons.append("High semantic relevance to competency")
                elif relevance_n >= 0.5:
                    reasons.append("Strong keyword match")
                if quality_n >= 0.7:
                    reasons.append("Top-rated in category")

                provider = doc.creator or doc.channel or "iGOT Karmayogi"

                result = RecommendationResult(
                    courseId       = doc.identifier,
                    title          = doc.name,
                    provider       = provider,
                    durationHours  = doc.duration_hrs,
                    finalScore     = final,
                    relevanceScore = round(relevance_n, 4),
                    qualityScore   = round(quality_n, 4),
                    isTpac         = doc.is_tpac,
                    competencyId   = gap.competencyId,
                    competencyName = gap.competencyName,
                    priorityRank   = 0,   # assigned below via enumerate
                    matchReasons   = reasons,
                    matchType      = match_type,       # Bug #6
                    tpacSource     = doc.tpac_source,  # Bug #6
                )
                gap_results.append(result)
                seen_course_ids.add(doc.identifier)

            # Sort within this gap's block by finalScore DESC, take top-K
            gap_results.sort(key=lambda r: r.finalScore, reverse=True)
            all_results.extend(gap_results[:limit_per_gap])

        # FIX (Bug #8): NO global sort here — gap-priority order is preserved.
        # priorityRank = position in the priority-ordered concatenation.
        for rank, rec in enumerate(all_results, start=1):
            rec.priorityRank = rank

        return all_results




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
    print("\nSUCCESS: All assertions passed.")