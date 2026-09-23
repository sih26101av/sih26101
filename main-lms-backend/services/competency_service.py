"""
FILE: main-lms-backend/services/competency_service.py
─────────────────────────────────────────────────────────────────────────────
Core engine for calculating official competency baselines (b_k).
Implements locked 6-term formula, anti-gaming ceilings, and recency decay.

Changes vs prior version:
- UNASSESSED branch (Bug #1 + #3): when ALL six evidence channels are zero,
  calculate_baseline now returns (0.0, "UNASSESSED") instead of falling back
  to any fabricated or borrowed value. Callers must treat this as "no data",
  not as "level 0 confirmed".
- ADJACENT_COMPETENCIES dict + compute_synergy() (Bug #4): synergy bonus is
  now scoped to an explicit, hand-curated adjacency table. No more blanket
  "any verified comp in the same broad category" credit. Cap reduced to 0.15.
- Missing channels are RENORMALISED OUT of the weighted sum instead of being
  counted as zero (SCIL v6 §3). Previously an official with one strong channel
  and nothing else was structurally pinned near 0 (a fully completed course
  alone gave b_k ≈ 1.6), which is what forced the display-layer hacks.
  Weak-evidence-only estimates are still bounded by the confidence ceilings.
- Recency decay now uses a true half-life (value halves every `half_life`
  years); it previously used exp(-t/h), i.e. a time constant mislabelled as one.
- Adjacency ids now match the real FRAC catalogue ids (the old `comp_python`
  style ids never matched, so synergy never fired).

Honesty ledger:
- Channel weights (0.45/0.15/0.20/0.10/0.05/0.05): reasoned defaults carried
  over; not empirically validated against HR outcome data. SCIL v6 §3 replaces
  them with AHP-elicited weights once an expert panel exists.
- Half-lives (3.0y Domain/Technical, 8.0y Behavioural): reasoned defaults
  loosely informed by skill-decay literature — NOT a validated equivalence.
- Synergy cap 0.15 and the adjacency pairs are illustrative/hand-curated;
  extend with real FRAC adjacency data as it becomes available.
"""

import math
from datetime import datetime
from typing import Dict, Optional, Tuple


# ── Adjacency table for synergy bonus (Bug #4 fix) ──────────────────────────
# Synergy is ONLY granted between competencies with a documented, deliberate
# skill-adjacency relationship — never a blanket "same broad category" credit.
# Extend this dict with real FRAC-adjacency data as it becomes available.
# Ids are the FRAC catalogue ids (mock-igot-server/data/frac_competencies.json).
# Translated from the original illustrative table; "sampling" is folded into
# Survey Design & Sampling (002), and pairs with no catalogue counterpart
# (cybersecurity, government cloud, data quality) were dropped.
ADJACENT_COMPETENCIES: Dict[str, list] = {
    # Statistical / Domain
    "comp_survey_design_002": ["comp_nat_accounts_001"],
    "comp_nat_accounts_001":  ["comp_survey_design_002", "comp_price_stats_003"],
    "comp_price_stats_003":   ["comp_nat_accounts_001", "comp_index_numbers_004"],
    "comp_index_numbers_004": ["comp_price_stats_003"],
    # Technical
    "comp_python_stats_017":  ["comp_r_analytics_018", "comp_ml_stats_005", "comp_data_viz_019"],
    "comp_r_analytics_018":   ["comp_python_stats_017", "comp_data_viz_019"],
    "comp_ml_stats_005":      ["comp_python_stats_017", "comp_cloud_infra_027"],
    "comp_data_viz_019":      ["comp_python_stats_017", "comp_r_analytics_018"],
    "comp_cloud_infra_027":   ["comp_ml_stats_005"],
    # Macro accounts and prices — each pair shares a compilation framework, so
    # evidence on one is partial evidence on the other.
    "comp_io_tables_083":     ["comp_nat_accounts_001", "comp_deflators_088"],
    "comp_qna_086":           ["comp_nat_accounts_001", "comp_time_series_013"],
    "comp_regional_accounts_085": ["comp_nat_accounts_001"],
    "comp_deflators_088":     ["comp_index_numbers_004", "comp_io_tables_083"],
    "comp_producer_price_090": ["comp_price_stats_003", "comp_index_numbers_004"],
    "comp_cost_living_093":   ["comp_poverty_014", "comp_price_stats_003"],
    "comp_gfs_080":           ["comp_public_fin_025"],
    # Survey methodology — the estimation chain: design → weights → variance.
    "comp_calibration_102":   ["comp_survey_design_002", "comp_var_estimation_106"],
    "comp_var_estimation_106": ["comp_survey_design_002", "comp_calibration_102"],
    "comp_small_area_101":    ["comp_survey_design_002"],
    "comp_questionnaire_115": ["comp_survey_design_002"],
    "comp_labour_stats_041":  ["comp_survey_design_002", "comp_informal_sector_043"],
    "comp_informal_sector_043": ["comp_labour_stats_041", "comp_econ_census_007"],
    "comp_tabulation_130":    ["comp_statistical_sw_030"],
    # Field operations — one craft split across three competencies.
    "comp_survey_ops_126":    ["comp_field_supervision_127"],
    "comp_field_supervision_127": ["comp_survey_ops_126", "comp_data_scrutiny_129"],
    "comp_data_scrutiny_129": ["comp_field_supervision_127"],
    # Data / platform engineering.
    "comp_data_eng_136":      ["comp_db_design_029", "comp_dwh_139", "comp_python_stats_017"],
    "comp_dwh_139":           ["comp_db_design_029", "comp_data_eng_136"],
    "comp_devops_142":        ["comp_containers_143", "comp_cloud_infra_027"],
    "comp_containers_143":    ["comp_cloud_infra_027", "comp_devops_142"],
    "comp_nlp_153":           ["comp_ml_stats_005", "comp_python_stats_017"],
    "comp_mlops_155":         ["comp_ml_stats_005", "comp_devops_142"],
    "comp_bi_tools_162":      ["comp_data_viz_019"],
    "comp_econometrics_111":  ["comp_r_analytics_018", "comp_statistical_sw_030"],
    # Confidentiality: the statistical and the legal/security side of one job.
    "comp_disclosure_105":    ["comp_data_privacy_026"],
}

SYNERGY_CAP = 0.15  # maximum bonus from adjacency, regardless of how many fire


# ── SCIL v6 §3 evidence channels ──────────────────────────────────────────────
#   K  Knowledge   — the 6-term baseline b_k below (courses, certificates, quizzes, priors)
#   A  Application — auto-graded work samples
#   U  Utility     — "will use within 90 days" + supervisor confirmation of the use
#   S  Supervisor  — one structured APAR item, 1–5 against the FRAC descriptors
# PLACEHOLDER WEIGHTS: equal (0.25 each) until an expert AHP elicitation exists.
# They are NOT fitted or validated; a channel with no evidence is renormalised
# out, exactly like the 6-term formula. Peer ratings are never a channel.
CHANNEL_WEIGHTS = {"K": 0.25, "A": 0.25, "U": 0.25, "S": 0.25}
CHANNEL_WEIGHTS_STATUS = "equal placeholder — pending expert AHP elicitation"


# ── Supervisor-rater leniency (SCIL v6 §3 S channel) ─────────────────────────
# A rater's offset is how far their mean rating sits from the mean of all
# ratings, shrunk toward 0 by n/(n+k) so a rater with few ratings is barely
# corrected. The corrected rating is raw − offset, clamped to 1..5.
# Limits: this removes RELATIVE leniency between raters only. If every rater is
# lenient by the same amount, the grand mean absorbs it; and a rater whose team
# really is stronger is corrected as if lenient. k = 5 is a reasoned default.
RATER_SHRINK_K = 5.0
RATER_MIN_RATINGS = 3        # fewer ratings than this → no correction at all


def rater_leniency_offsets(ratings: list, shrink_k: float = RATER_SHRINK_K) -> Dict[str, Dict]:
    """[{raterId, grantedValue}] → {raterId: {offset, n, mean, grandMean}} (shrunk mean offsets)."""
    by_rater: Dict[str, list] = {}
    for r in ratings or []:
        rid, val = r.get("raterId"), r.get("grantedValue")
        if rid and val is not None:
            by_rater.setdefault(rid, []).append(float(val))
    values = [v for vs in by_rater.values() for v in vs]
    if not values:
        return {}
    grand = sum(values) / len(values)
    out: Dict[str, Dict] = {}
    for rid, vs in by_rater.items():
        n, mean = len(vs), sum(vs) / len(vs)
        offset = (mean - grand) * n / (n + shrink_k) if n >= RATER_MIN_RATINGS else 0.0
        out[rid] = {"offset": round(offset, 3), "n": n, "mean": round(mean, 3), "grandMean": round(grand, 3)}
    return out


def correct_supervisor_rating(value: float, rater_id: Optional[str],
                              offsets: Optional[Dict[str, Dict]]) -> Tuple[float, float]:
    """(corrected rating on 1..5, offset applied). Unknown rater → unchanged."""
    offset = float(((offsets or {}).get(rater_id or "") or {}).get("offset", 0.0))
    return min(5.0, max(1.0, float(value) - offset)), offset


def fuse_channels(channels: Dict[str, Optional[float]]) -> Optional[float]:
    """Weighted mean over the K/A/U/S channels that carry evidence (None → absent)."""
    present = {k: float(v) for k, v in channels.items() if v is not None and k in CHANNEL_WEIGHTS}
    if not present:
        return None
    total = sum(CHANNEL_WEIGHTS[k] for k in present)
    return sum(CHANNEL_WEIGHTS[k] * v for k, v in present.items()) / total


class CompetencyCalculator:
    WEIGHTS = {
        'verified':     0.45,
        'documented':   0.15,
        'tenure':       0.20,
        'self_report':  0.10,
        'education':    0.05,
        'seniority':    0.05,
    }

    @staticmethod
    def _map_frac_type(frac_competency_type: str) -> str:
        """Maps FRAC types from the JSON to calculation categories."""
        if frac_competency_type.lower() == 'behavioural':
            return 'GENERIC_BEHAVIOURAL'
        return 'DOMAIN_TECHNICAL'

    def _calculate_recency_multiplier(
        self,
        issue_date: datetime,
        comp_category: str,
        current_time: datetime = None,
    ) -> float:
        if not issue_date:
            return 1.0
        now = current_time or datetime.utcnow()
        years_ago = max(0.0, (now - issue_date).days / 365.25)
        half_life = 3.0 if comp_category == 'DOMAIN_TECHNICAL' else 8.0
        return max(0.2, 0.5 ** (years_ago / half_life))

    # ── Bug #4 fix: explicit adjacency-based synergy ──────────────────────────
    @staticmethod
    def compute_synergy(comp_id: str, verified_scores_by_comp: Dict[str, float]) -> float:
        """
        Synergy bonus scoped strictly to the ADJACENT_COMPETENCIES table.
        Only adjacent competencies with REAL verified>0 evidence contribute.
        Capped at SYNERGY_CAP (0.15) regardless of how many fire.
        Returns 0.0 for any comp not in the adjacency table.
        """
        adjacent = ADJACENT_COMPETENCIES.get(comp_id, [])
        if not adjacent:
            return 0.0
        firing = sum(
            1 for a in adjacent
            if verified_scores_by_comp.get(a, 0.0) > 0
        )
        if firing == 0:
            return 0.0
        return min(SYNERGY_CAP, 0.05 * firing)

    def calculate_baseline(
        self,
        frac_type: str,
        evidence_data: Dict,
        verified_count_in_category: int,
        current_time: datetime = None,
        # NEW: pass the full verified-by-comp map for proper adjacency synergy.
        # Falls back to legacy count-based synergy when not provided, so existing
        # call-sites that have not been updated yet continue to work.
        verified_scores_by_comp: Optional[Dict[str, float]] = None,
        comp_id: Optional[str] = None,
    ) -> Tuple[float, str]:
        """
        Calculates the baseline score (b_k) and returns (score, confidence_tag).

        evidence_data expects:
        {
            'verified':    float (0-5),
            'documented':  float (0-5),
            'doc_date':    datetime | None,
            'tenure':      float (0-5),
            'self_report': float (0-5),
            'education':   float (0-5),
            'seniority':   float (0-5),
        }

        confidence_tag values: "UNASSESSED" | "LOW" | "MEDIUM" | "HIGH"
        """
        comp_category = self._map_frac_type(frac_type)

        # 1. Extract raw evidence values
        verified      = evidence_data.get('verified', 0.0)
        doc_raw       = evidence_data.get('documented', 0.0)
        doc_date      = evidence_data.get('doc_date')
        tenure        = evidence_data.get('tenure', 0.0)
        self_report_raw = evidence_data.get('self_report', 0.0)
        education     = evidence_data.get('education', 0.0)
        seniority_raw = evidence_data.get('seniority', 0.0)

        # 2. Apply rules and decay
        doc_multiplier = (
            self._calculate_recency_multiplier(doc_date, comp_category, current_time)
            if doc_raw > 0 else 0.0
        )
        documented   = doc_raw * doc_multiplier
        self_report  = self_report_raw * 0.6   # 0.6 reliability discount
        # Seniority is ZERO for Technical/Domain/Functional skills
        seniority    = seniority_raw if comp_category == 'GENERIC_BEHAVIOURAL' else 0.0

        # ── Bug #1 + #3 fix: reachable UNASSESSED branch ──────────────────────
        # When every channel is genuinely zero, return UNASSESSED rather than
        # any fabricated value. The caller is responsible for treating None/null
        # as "no data", not as "confirmed level 0".
        all_zero = all(v <= 0.0 for v in [
            verified, documented, tenure, self_report, education, seniority
        ])
        if all_zero:
            return 0.0, "UNASSESSED"

        # 3. Core weighted mean over the channels that actually carry evidence.
        #    A channel with no evidence is "not instrumented", not "scored 0"
        #    (SCIL v6 §3), so its weight is renormalised out rather than
        #    dragging the estimate towards zero.
        channels = {
            'verified':    verified,
            'documented':  documented,
            'tenure':      tenure,
            'self_report': self_report,
            'education':   education,
            'seniority':   seniority,
        }
        present = {k: v for k, v in channels.items() if v > 0}
        weight_sum = sum(self.WEIGHTS[k] for k in present)
        core_k = sum(self.WEIGHTS[k] * v for k, v in present.items()) / weight_sum

        # 4. Synergy bonus — Bug #4 fix: use adjacency table when available,
        #    fall back to legacy count-based bonus if comp_id not provided.
        if comp_id is not None and verified_scores_by_comp is not None:
            synergy_k = self.compute_synergy(comp_id, verified_scores_by_comp)
        else:
            # Legacy path — kept so existing callers not yet updated still work
            synergy_k = min(0.4, 0.1 * verified_count_in_category) if core_k > 0 else 0.0

        # 5. Anti-gaming ceilings & confidence tagging
        #    Confidence tier derived strictly from WHICH channel fired (Bug #3 fix).
        if verified > 0:
            ceiling    = 5.0
            confidence = "HIGH"
        elif doc_raw > 0:
            ceiling    = 3.5
            confidence = "MEDIUM"
        else:
            ceiling    = 2.5
            confidence = "LOW"

        # 6. Final clamped value
        b_k = min(core_k + synergy_k, ceiling)
        return round(b_k, 3), confidence


# ─────────────────────────────────────────────────────────────────────────────
# Verification Test Block
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    calculator = CompetencyCalculator()

    # Test 1: Standard case with documented evidence
    mock_current_time = datetime(2026, 8, 20)
    mock_cert_date = datetime(2023, 8, 20)
    evidence = {
        'verified': 0.0, 'documented': 3.5, 'doc_date': mock_cert_date,
        'tenure': 1.4, 'self_report': 3.0, 'education': 1.0, 'seniority': 5.0,
    }
    score, tag = calculator.calculate_baseline(
        frac_type="Domain", evidence_data=evidence,
        verified_count_in_category=1, current_time=mock_current_time,
    )
    # documented 3.5 × 0.5^(3y/3y) = 1.75; mean over the 4 present channels
    # (documented, tenure, self-report×0.6, education) = 0.772/0.50 = 1.545,
    # plus legacy synergy 0.1 → 1.645. Seniority is zeroed for Domain.
    print(f"Test 1 — Calculated Score: {score}, Confidence: {tag}")
    assert abs(score - 1.645) < 0.005, f"Math failed! Expected ~1.645, got {score}"
    assert tag == "MEDIUM", f"Tag failed! Expected MEDIUM, got {tag}"
    print("Test 1 PASSED: Engine math matches specification.")

    # Test 2: All-zero evidence → UNASSESSED (Bug #1 fix)
    zero_evidence = {
        'verified': 0.0, 'documented': 0.0, 'doc_date': None,
        'tenure': 0.0, 'self_report': 0.0, 'education': 0.0, 'seniority': 0.0,
    }
    score2, tag2 = calculator.calculate_baseline(
        frac_type="Domain", evidence_data=zero_evidence,
        verified_count_in_category=0,
    )
    assert score2 == 0.0 and tag2 == "UNASSESSED", f"Bug #1 not fixed! Got {score2}, {tag2}"
    print("Test 2 PASSED: UNASSESSED branch works correctly.")

    # Test 3: Adjacency synergy (Bug #4 fix)
    synergy = CompetencyCalculator.compute_synergy(
        "comp_python_stats_017",
        {"comp_r_analytics_018": 0.0, "comp_ml_stats_005": 2.5, "comp_data_viz_019": 0.0},
    )
    assert synergy == 0.05, f"Bug #4 synergy wrong: {synergy}"
    print("Test 3 PASSED: Adjacency synergy uses explicit table.")
    print("\nSUCCESS: All assertions passed.")