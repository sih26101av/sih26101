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

Honesty ledger:
- Channel weights (0.45/0.15/0.20/0.10/0.05/0.05): reasoned defaults carried
  over; not empirically validated against HR outcome data.
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
ADJACENT_COMPETENCIES: Dict[str, list] = {
    # Statistical / Domain
    "comp_survey_design":    ["comp_sampling", "comp_data_quality"],
    "comp_sampling":         ["comp_survey_design", "comp_national_accounts"],
    "comp_national_accounts": ["comp_sampling", "comp_price_statistics"],
    "comp_price_statistics": ["comp_national_accounts", "comp_index_numbers"],
    "comp_index_numbers":    ["comp_price_statistics"],
    # Technical
    "comp_python":           ["comp_r", "comp_ai_ml", "comp_data_visualization"],
    "comp_r":                ["comp_python", "comp_data_visualization"],
    "comp_ai_ml":            ["comp_python", "comp_cloud_computing"],
    "comp_data_visualization": ["comp_python", "comp_r"],
    "comp_cloud_computing":  ["comp_ai_ml", "comp_cybersecurity"],
    # Governance / Cybersecurity
    "comp_cybersecurity":    ["comp_data_privacy", "comp_government_cloud"],
    "comp_data_privacy":     ["comp_cybersecurity"],
    "comp_government_cloud": ["comp_cybersecurity", "comp_cloud_computing"],
}

SYNERGY_CAP = 0.15  # maximum bonus from adjacency, regardless of how many fire


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
        return max(0.2, math.exp(-years_ago / half_life))

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

        # 3. Core weighted sum
        core_k = (
            (self.WEIGHTS['verified']    * verified)   +
            (self.WEIGHTS['documented']  * documented) +
            (self.WEIGHTS['tenure']      * tenure)     +
            (self.WEIGHTS['self_report'] * self_report)+
            (self.WEIGHTS['education']   * education)  +
            (self.WEIGHTS['seniority']   * seniority)
        )

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
    print(f"Test 1 — Calculated Score: {score}, Confidence: {tag}")
    assert round(score, 2) == 0.80, f"Math failed! Expected ~0.80, got {score}"
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
        "comp_python", {"comp_r": 0.0, "comp_ai_ml": 2.5, "comp_data_visualization": 0.0}
    )
    assert synergy == 0.05, f"Bug #4 synergy wrong: {synergy}"
    print("Test 3 PASSED: Adjacency synergy uses explicit table.")
    print("\nSUCCESS: All assertions passed.")