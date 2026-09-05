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
    Dense  : sentence-transformers/all-MiniLM-L6-v2 (384-dim) + FAISS IndexFlatIP
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
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
_EMBED_MODEL   = "sentence-transformers/all-MiniLM-L6-v2"
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
    priorityRank:   int            # 1-based, across all returned recs
    matchReasons:   List[str]      # human-readable explanation chips


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
    rating:           float = 3.5
    rating_count:     int   = 30
    enrollment_count: int   = 100
    completion_rate:  float = 0.60
    is_tpac:          bool  = False
    corpus_text:      str   = ""   # title + description, lowercased, for BM25


# ── Wilson lower bound ─────────────────────────────────────────────────────────

def _wilson_lower_bound(rating: float, n: int, z: float = _WILSON_Z) -> float:
    """
    Convert a mean rating (0-5 scale) and count n into Wilson lower bound.
    Treats each rating as a fraction of 5 (proxy for binary positive votes).
    Returns 0.0 if n < 1.
    """
    if n < 1:
        return 0.0
    phat = rating / 5.0
    phat = max(0.0, min(1.0, phat))
    denom = 1.0 + (z * z) / n
    centre = phat + (z * z) / (2 * n)
    spread = z * math.sqrt(phat * (1.0 - phat) / n + (z * z) / (4 * n * n))
    return max(0.0, (centre - spread) / denom)


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
        logger.info("[RecEngine] Loading embedding model %s …", _EMBED_MODEL)
        self._embedder = SentenceTransformer(_EMBED_MODEL)

        corpus_texts = [doc.corpus_text for doc in self._catalog]
        embeddings = self._embedder.encode(
            corpus_texts, batch_size=64, normalize_embeddings=True, show_progress_bar=False
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

            # TPAC / NSSTA flag — use pre-enriched field if available, else infer
            is_tpac = item.get("is_tpac", None)
            if is_tpac is None:
                creator = item.get("creator", "")
                orgs    = item.get("organisation", [])
                is_tpac = (
                    any(kw in creator for kw in NSSTA_CREATORS)
                    or any(any(kw in org for kw in NSSTA_CREATORS) for org in orgs)
                )

            corpus_text = (
                (item.get("name", "") + " " + item.get("description", "")).lower().strip()
            )

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
                rating           = float(item.get("rating", 3.5)),
                rating_count     = int(item.get("rating_count", 30)),
                enrollment_count = int(item.get("enrollment_count", 100)),
                completion_rate  = float(item.get("completion_rate", 0.60)),
                is_tpac          = bool(is_tpac),
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
        """
        # Stage 1: FRAC-tag filter
        candidate_indices = self._comp_index.get(gap.competencyId, [])
        if not candidate_indices:
            logger.debug("[RecEngine] No courses tagged for comp %s", gap.competencyId)
            return []

        candidate_set = set(candidate_indices)

        # Stage 2: Build query anchor from official FRAC description
        frac_meta   = self._frac_map.get(gap.competencyId, {})
        frac_name   = frac_meta.get("name", gap.competencyName)
        frac_desc   = frac_meta.get("description", "")
        query_text  = f"{frac_name}. {frac_desc}".strip()
        query_tok   = query_text.lower().split()

        # 2a. Dense search (FAISS cosine, L2-normalised)
        import faiss  # already loaded at startup
        q_emb = self._embedder.encode(
            [query_text], normalize_embeddings=True, show_progress_bar=False
        ).astype("float32")
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
        quality = 0.35*completion + 0.35*rating_wilson + 0.20*pop_norm + 0.10*tpac_flag
        All sub-scores are normalised within the shortlist.
        """
        if not shortlist:
            return 0.0

        # completion_rate is already [0,1] — normalise within shortlist
        completions   = [d.completion_rate for d in shortlist]
        c_min, c_max  = min(completions), max(completions)
        c_range       = c_max - c_min if c_max > c_min else 1.0
        completion_n  = (doc.completion_rate - c_min) / c_range

        # Wilson lower bound for rating, normalised within shortlist
        wilson_scores = [_wilson_lower_bound(d.rating, d.rating_count) for d in shortlist]
        w_min, w_max  = min(wilson_scores), max(wilson_scores)
        w_range       = w_max - w_min if w_max > w_min else 1.0
        my_wilson     = _wilson_lower_bound(doc.rating, doc.rating_count)
        rating_n      = (my_wilson - w_min) / w_range

        # log(1 + enroll), normalised within shortlist
        pop_raw       = [math.log1p(d.enrollment_count) for d in shortlist]
        p_min, p_max  = min(pop_raw), max(pop_raw)
        p_range       = p_max - p_min if p_max > p_min else 1.0
        my_pop        = math.log1p(doc.enrollment_count)
        pop_n         = (my_pop - p_min) / p_range

        tpac_flag = 1.0 if doc.is_tpac else 0.0

        return (
            0.35 * completion_n
            + 0.35 * rating_n
            + 0.20 * pop_n
            + 0.10 * tpac_flag
        )

    # ── Public API ─────────────────────────────────────────────────────────────

    def get_recommendations(
        self,
        gaps:           List[GapEntry],
        limit_per_gap:  int = 3,
        enrolled_ids:   Optional[set] = None,
    ) -> List[RecommendationResult]:
        """
        Returns deduplicated, globally ranked RecommendationResult list.

        Parameters
        ----------
        gaps           : output of calculate_gaps(), sorted by priority DESC
        limit_per_gap  : max courses to return per gap (default 3)
        enrolled_ids   : set of courseIds already enrolled — excluded from results
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

            gap_results: List[Tuple[float, RecommendationResult]] = []
            for (idx, rrf_raw), doc in zip(retrieved, shortlist_docs):
                # Stage 3 scores
                relevance_n = (rrf_raw - rrf_min) / rrf_range
                quality_n   = self._quality_score(doc, shortlist_docs)
                final       = round(0.6 * relevance_n + 0.4 * quality_n, 4)

                # Build human-readable match reasons
                reasons = [f"FRAC tag: {gap.competencyName}"]
                if doc.is_tpac:
                    reasons.append("NSSTA TPAC-vetted course")
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
                    priorityRank   = 0,   # assigned after global sort below
                    matchReasons   = reasons,
                )
                gap_results.append((final, result))
                seen_course_ids.add(doc.identifier)

            # Keep top-K per gap
            gap_results.sort(key=lambda x: x[0], reverse=True)
            all_results.extend(r for _, r in gap_results[:limit_per_gap])

        # Global sort by finalScore, assign priorityRank
        all_results.sort(key=lambda r: r.finalScore, reverse=True)
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