"""
FILE: main-lms-backend/routers/competency.py
─────────────────────────────────────────────────────────────────────────────
Exposes the Skill Intelligence endpoints:

  POST /api/v1/competencies/upload-certificate
      Accepts a PDF, runs local Ollama extraction, returns FRAC-mapped skills.

  POST /api/v1/competencies/baseline
      Calculates b_k for a single competency given an evidence payload.

NOTE: The AI recommendation route (/api/v1/learner/{user_id}/recommendations)
      lives in main.py so it shares the app-level engine singleton and the
      adapter/auth stack. This router handles only competency-specific concerns.
─────────────────────────────────────────────────────────────────────────────
"""

import os
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from services.competency_service import CompetencyCalculator
from services.document_extractor import DocumentExtractorService
from adapters.igot_adapter import MockIgotAdapter

router = APIRouter(prefix="/api/v1/competencies", tags=["Competencies"])

# ── Singletons ─────────────────────────────────────────────────────────────────
calculator = CompetencyCalculator()
extractor  = DocumentExtractorService()
igot       = MockIgotAdapter()


# ─────────────────────────────────────────────────────────────────────────────
# POST /upload-certificate
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/upload-certificate")
async def upload_certificate(file: UploadFile = File(...)):
    """
    Accepts a PDF certificate or resume from the React frontend.
    Extracts text → sends to local Ollama (llama3.2:3b) → returns
    a list of FRAC-mapped competencies with skill levels and justifications.

    Privacy: the PDF is processed entirely on-device. No data leaves the server.
    """
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    temp_path = f"temp_upload_{file.filename}"
    try:
        # 1. Persist upload to a temporary file
        with open(temp_path, "wb") as buf:
            shutil.copyfileobj(file.file, buf)

        # 2. Fetch FRAC dictionary from mock iGOT so Ollama can map to real IDs
        catalog = await igot.fetch_catalog()
        seen: set = set()
        frac_dict = []
        for course in catalog:
            raw_v3 = course.get("competencies_v3", "")
            if not raw_v3:
                continue
            try:
                import json
                tags = json.loads(raw_v3) if isinstance(raw_v3, str) else raw_v3
            except Exception:
                continue
            for tag in tags:
                cid = tag.get("id", "")
                if cid and cid not in seen:
                    seen.add(cid)
                    frac_dict.append({
                        "id":             cid,
                        "name":           tag.get("name", ""),
                        "competencyType": tag.get("competencyType", "Domain"),
                    })

        # 3. Extract text from PDF → parse with Ollama
        text   = extractor.extract_text_from_pdf(temp_path)
        result = extractor.parse_document(text, frac_dict)

        return {"status": "success", "data": result.model_dump()}

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ─────────────────────────────────────────────────────────────────────────────
# POST /baseline  — calculate b_k for a single competency
# ─────────────────────────────────────────────────────────────────────────────

class EvidencePayload(BaseModel):
    frac_type:              str              # "Domain" | "Functional" | "Behavioural"
    verified:               float = 0.0     # 0-5, from verified assessment
    documented:             float = 0.0     # 0-5, from certificates
    doc_date:               Optional[str] = None   # ISO date of certificate
    tenure:                 float = 0.0     # 0-5, inferred from tenure
    self_report:            float = 0.0     # 0-5, self-assessed
    education:              float = 0.0     # 0-5, from formal education
    seniority:              float = 0.0     # 0-5, designation-based (zeroed for Domain/Functional)
    verified_count_in_category: int = 0    # synergy bonus input


@router.post("/baseline")
async def calculate_baseline(payload: EvidencePayload):
    """
    Calculates the skill baseline score b_k ∈ [0, 5] using the locked
    6-term formula with recency decay, anti-gaming ceilings, and
    confidence tagging (HIGH / MEDIUM / LOW).
    """
    evidence = payload.model_dump()

    # Convert doc_date string → datetime if present
    doc_date_str = evidence.pop("doc_date", None)
    if doc_date_str:
        try:
            evidence["doc_date"] = datetime.fromisoformat(doc_date_str)
        except ValueError:
            evidence["doc_date"] = None

    frac_type = evidence.pop("frac_type")
    verified_count = evidence.pop("verified_count_in_category", 0)

    score, confidence = calculator.calculate_baseline(
        frac_type=frac_type,
        evidence_data=evidence,
        verified_count_in_category=verified_count,
    )

    return {
        "status":     "success",
        "baselineScore": score,
        "confidence": confidence,
        "ceiling":    5.0 if evidence.get("verified", 0) > 0 else (3.5 if evidence.get("documented", 0) > 0 else 2.5),
    }