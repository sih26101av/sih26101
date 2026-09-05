"""
FILE: main-lms-backend/services/competency_service.py
─────────────────────────────────────────────────────────────────────────────
Core engine for calculating official competency baselines (b_k).
Implements locked 6-term formula, anti-gaming ceilings, and recency decay.
"""

import math
from datetime import datetime
from typing import Dict, Tuple

class CompetencyCalculator:
    WEIGHTS = {
        'verified': 0.45,
        'documented': 0.15,
        'tenure': 0.20,
        'self_report': 0.10,
        'education': 0.05,
        'seniority': 0.05
    }

    @staticmethod
    def _map_frac_type(frac_competency_type: str) -> str:
        """Maps FRAC types from the JSON to calculation categories."""
        if frac_competency_type.lower() == 'behavioural':
            return 'GENERIC_BEHAVIOURAL'
        # 'Domain' and 'Functional' fall under technical
        return 'DOMAIN_TECHNICAL' 

    def _calculate_recency_multiplier(self, issue_date: datetime, comp_category: str, current_time: datetime = None) -> float:
        if not issue_date:
            return 1.0
        
        now = current_time or datetime.utcnow()
        years_ago = (now - issue_date).days / 365.25
        
        if years_ago < 0:
            years_ago = 0
            
        half_life = 3.0 if comp_category == 'DOMAIN_TECHNICAL' else 8.0
        
        # Recency formula: max(0.2, e^(-years / half_life))
        return max(0.2, math.exp(-years_ago / half_life))

    def calculate_baseline(self, frac_type: str, evidence_data: Dict, verified_count_in_category: int, current_time: datetime = None) -> Tuple[float, str]:
        """
        Calculates the baseline score (b_k) and returns (score, confidence_tag).
        
        evidence_data expects: 
        {
            'verified': float (0-5),
            'documented': float (0-5),
            'doc_date': datetime,
            'tenure': float (0-5),
            'self_report': float (0-5),
            'education': float (0-5),
            'seniority': float (0-5)
        }
        """
        comp_category = self._map_frac_type(frac_type)
        
        # 1. Extract raw evidence values
        verified = evidence_data.get('verified', 0.0)
        doc_raw = evidence_data.get('documented', 0.0)
        doc_date = evidence_data.get('doc_date')
        tenure = evidence_data.get('tenure', 0.0)
        self_report_raw = evidence_data.get('self_report', 0.0)
        education = evidence_data.get('education', 0.0)
        seniority_raw = evidence_data.get('seniority', 0.0)

        # 2. Apply rules and decay
        doc_multiplier = self._calculate_recency_multiplier(doc_date, comp_category, current_time) if doc_raw > 0 else 0.0
        documented = doc_raw * doc_multiplier
        
        self_report = self_report_raw * 0.6  # 0.6 Reliability factor
        
        # Seniority is ZERO for Technical/Domain/Functional skills regardless of input
        seniority = seniority_raw if comp_category == 'GENERIC_BEHAVIOURAL' else 0.0

        # 3. Core Weighted Sum
        core_k = (
            (self.WEIGHTS['verified'] * verified) +
            (self.WEIGHTS['documented'] * documented) +
            (self.WEIGHTS['tenure'] * tenure) +
            (self.WEIGHTS['self_report'] * self_report) +
            (self.WEIGHTS['education'] * education) +
            (self.WEIGHTS['seniority'] * seniority)
        )

        # 4. Synergy Bonus (only applied if there is a core foundation)
        synergy_k = min(0.4, 0.1 * verified_count_in_category) if core_k > 0 else 0.0

        # 5. Anti-Gaming Ceilings & Confidence Tagging
        if verified > 0:
            ceiling = 5.0
            confidence = "HIGH"
        elif doc_raw > 0:
            ceiling = 3.5
            confidence = "MEDIUM"
        else:
            ceiling = 2.5
            confidence = "LOW"

        # 6. Final clamped value
        b_k = min(core_k + synergy_k, ceiling)
        
        return round(b_k, 3), confidence


# ─────────────────────────────────────────────────────────────────────────────
# Verification Test Block
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    calculator = CompetencyCalculator()
    
    # Simulating the official from the worked example:
    # - 3 years old cert (Domain/Technical)
    mock_current_time = datetime(2026, 8, 20)
    mock_cert_date = datetime(2023, 8, 20) 
    
    evidence = {
        'verified': 0.0,
        'documented': 3.5,
        'doc_date': mock_cert_date,
        'tenure': 1.4,
        'self_report': 3.0,
        'education': 1.0,
        'seniority': 5.0 # Deliberately high to test that the engine forces it to 0
    }
    
    score, tag = calculator.calculate_baseline(
        frac_type="Domain", 
        evidence_data=evidence, 
        verified_count_in_category=1,
        current_time=mock_current_time
    )
    
    print(f"Calculated Score: {score}")
    print(f"Confidence Tag: {tag}")
    
    # The expected score from the locked math is ~0.804
    assert round(score, 2) == 0.80, f"Math failed! Expected ~0.80, got {score}"
    assert tag == "MEDIUM", f"Tag failed! Expected MEDIUM, got {tag}"
    print("SUCCESS: Engine math exactly matches the specification!")