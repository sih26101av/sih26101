"""
FILE: main-lms-backend/routers/competency.py
─────────────────────────────────────────────────────────────────────────────
Exposes the Skill Intelligence endpoints:

  POST /api/v1/competencies/upload-certificate            (learner)
      PDF / image → FRAC competencies (Gemini, else OCR + e5). Writes one
      DOCUMENTED_CERT EvidenceLog row per competency, so the gap moves at once
      (MEDIUM confidence), and queues the certificate for admin review.
  GET  /api/v1/competencies/certificates                  (learner)
      The caller's certificate submissions and their review status.
  GET  /api/v1/competencies/certificates/review?status=   (admin)
  POST /api/v1/competencies/certificates/{id}/review      (admin)
      approve → rows become VERIFIED_CERT (verified channel, HIGH confidence);
      reject  → rows are deleted.

  POST /api/v1/competencies/baseline
      Level for a single competency from a hand-supplied evidence payload, on the
      same assembler path as the dashboard (assess_competency + resolve_level).

NOTE: The AI recommendation route (/api/v1/learner/{user_id}/recommendations)
      lives in main.py so it shares the app-level engine singleton and the
      adapter/auth stack. This router handles only competency-specific concerns.
─────────────────────────────────────────────────────────────────────────────
"""

import hashlib
import logging
import os
from datetime import datetime, timezone
from typing import Literal, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth.database import get_db
from auth.dependencies import get_current_user, require_role
from auth.models import UserAuth
from services import app_state
from services.document_extractor import (
    IMAGE_EXTS, DocumentExtractorService, ExtractionError, frac_by_id,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/competencies", tags=["Competencies"])

# ── Singletons ─────────────────────────────────────────────────────────────────
extractor = DocumentExtractorService()

MAX_CERT_BYTES = int(os.getenv("CERT_MAX_MB", "10")) * 1024 * 1024
_ALLOWED_EXTS = {".pdf"} | IMAGE_EXTS
# FRAC type → the Competency.domain vocabulary used by the skill-gap view.
_DOMAIN = {"Domain": "Statistical", "Functional": "Governance",
           "Behavioural": "Leadership", "Technical": "Technical"}
_DUPLICATE = "This certificate was already submitted."


def _view(sub, with_user: bool = False) -> dict:
    extraction = sub.extraction or {}
    out = {
        "id":                  sub.id,
        "filename":            sub.filename,
        "issuingOrganization": sub.issuingOrganization,
        "extractor":           sub.extractor,
        "status":              sub.status,
        # The evidence tier the rows currently carry in the baseline formula.
        "verification":        {"PENDING": "documented", "VERIFIED": "verified"}.get(sub.status, "rejected"),
        "competencies":        extraction.get("extracted_competencies", []),
        "reviewNote":          sub.reviewNote,
        "createdAt":           sub.createdAt.isoformat() if sub.createdAt else None,
        "reviewedAt":          sub.reviewedAt.isoformat() if sub.reviewedAt else None,
    }
    if with_user:
        out["userId"] = sub.userId
        out["reviewedBy"] = sub.reviewedBy
        out["isValidCredential"] = extraction.get("is_valid_credential")
    return out


def _find(db: Session, user_id: str, sha: str):
    from models.models import CertificateSubmission

    return db.query(CertificateSubmission).filter(
        CertificateSubmission.userId == user_id, CertificateSubmission.sha256 == sha).first()


# ─────────────────────────────────────────────────────────────────────────────
# POST /upload-certificate
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/upload-certificate")
async def upload_certificate(
    file: UploadFile = File(...),
    current_user: UserAuth = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Accepts a PDF or image certificate / resume for the signed-in official.
    The file is read into memory (never written to disk) and hashed; the same
    file uploaded twice returns the existing submission.
    """
    from models.models import CertificateSubmission, Competency, EvidenceLog

    user_id = current_user.username                      # iGOT userId — never from the body
    filename = os.path.basename(file.filename or "certificate")[:200]
    if os.path.splitext(filename)[1].lower() not in _ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail="Only PDF or image (PNG/JPG/WEBP) certificates are supported.")
    data = await file.read(MAX_CERT_BYTES + 1)
    if len(data) > MAX_CERT_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large (max {MAX_CERT_BYTES // (1024 * 1024)} MB).")
    if not data:
        raise HTTPException(status_code=400, detail="Empty file.")

    sha = hashlib.sha256(data).hexdigest()
    existing = _find(db, user_id, sha)
    if existing:
        return {"status": "duplicate", "message": _DUPLICATE, "certificate": _view(existing)}

    try:
        result = await extractor.extract(data, filename)
    except ExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("[certificate] extraction failed")
        raise HTTPException(status_code=502, detail=f"Certificate extraction failed: {exc}")

    if not result.is_valid_credential or not result.extracted_competencies:
        return {
            "status": "no_evidence",
            "message": ("This does not look like a certificate or resume." if not result.is_valid_credential
                        else "No FRAC competency in this document matched closely enough."),
            "data": result.model_dump(),
        }

    frac = frac_by_id()
    sub = CertificateSubmission(
        userId=user_id, filename=filename, sha256=sha,
        issuingOrganization=result.issuing_organization, extractor=result.extractor,
        extraction=result.model_dump(), status="PENDING",
    )
    db.add(sub)
    db.flush()                                           # sub.id for the back-links below
    evidence_ids = []
    for comp in result.extracted_competencies:
        if not db.get(Competency, comp.competency_id):
            ftype = frac.get(comp.competency_id, {}).get("competencyType", "Domain")
            db.add(Competency(compId=comp.competency_id, domain=_DOMAIN.get(ftype, "Statistical"),
                              skillName=comp.competency_name))
            db.flush()
        row = EvidenceLog(
            userId=user_id, compId=comp.competency_id, evidenceType="DOCUMENTED_CERT",
            grantedValue=comp.extracted_level,
            # Recency decay runs from the certificate's own date; undated → today.
            issueDate=datetime.fromisoformat(comp.issue_date) if comp.issue_date else datetime.now(timezone.utc),
            metadata_payload={
                "source": "certificate_upload", "certificateId": sub.id, "verification": "documented",
                "filename": filename, "issuer": result.issuing_organization,
                "competencyName": comp.competency_name, "justification": comp.justification,
                "extractor": result.extractor, "matchScore": comp.match_score,
            },
        )
        db.add(row)
        db.flush()
        evidence_ids.append(row.id)
    sub.evidenceIds = evidence_ids
    try:
        db.commit()
    except IntegrityError:                               # the same file raced in twice
        db.rollback()
        existing = _find(db, user_id, sha)
        return {"status": "duplicate", "message": _DUPLICATE,
                "certificate": _view(existing) if existing else None}

    app_state.invalidate_user(user_id)                   # the gap reflects the documented evidence at once
    return {
        "status": "success",
        "message": "Recorded as documented evidence; it becomes verified once an admin approves it.",
        "certificate": _view(sub),
        "data": result.model_dump(),
    }


@router.get("/certificates")
async def my_certificates(current_user: UserAuth = Depends(get_current_user), db: Session = Depends(get_db)):
    from models.models import CertificateSubmission

    subs = (db.query(CertificateSubmission)
              .filter(CertificateSubmission.userId == current_user.username)
              .order_by(CertificateSubmission.createdAt.desc()).all())
    return {"certificates": [_view(s) for s in subs]}


# ─────────────────────────────────────────────────────────────────────────────
# Admin review — documented → verified (or rejected)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/certificates/review")
async def certificates_for_review(
    status: Literal["PENDING", "VERIFIED", "REJECTED", "ALL"] = Query("PENDING"),
    limit: int = Query(100, ge=1, le=500),
    _admin: UserAuth = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    from models.models import CertificateSubmission

    q = db.query(CertificateSubmission)
    if status != "ALL":
        q = q.filter(CertificateSubmission.status == status)
    subs = q.order_by(CertificateSubmission.createdAt.desc()).limit(limit).all()
    pending = db.query(CertificateSubmission).filter(CertificateSubmission.status == "PENDING").count()
    return {"certificates": [_view(s, with_user=True) for s in subs], "pendingCount": pending}


class CertificateReview(BaseModel):
    decision: Literal["approve", "reject"]
    note: Optional[str] = None


@router.post("/certificates/{certificate_id}/review")
async def review_certificate(
    certificate_id: str,
    body: CertificateReview,
    admin: UserAuth = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    from models.models import CertificateSubmission, EvidenceLog

    sub = db.get(CertificateSubmission, certificate_id)
    if sub is None:
        raise HTTPException(status_code=404, detail="Certificate not found.")
    if sub.status != "PENDING":
        raise HTTPException(status_code=409, detail=f"Certificate already {sub.status.lower()}.")

    rows = db.query(EvidenceLog).filter(EvidenceLog.id.in_(sub.evidenceIds or [])).all()
    if body.decision == "approve":
        for row in rows:
            row.evidenceType = "VERIFIED_CERT"
            row.metadata_payload = {**(row.metadata_payload or {}), "verification": "verified",
                                    "reviewedBy": admin.username}
        sub.status = "VERIFIED"
    else:
        for row in rows:
            db.delete(row)
        sub.status = "REJECTED"
    sub.reviewedBy = admin.username
    sub.reviewNote = (body.note or "").strip()[:500] or None
    sub.reviewedAt = datetime.now(timezone.utc)
    db.commit()

    app_state.invalidate_user(sub.userId)
    return {"status": "success", "certificate": _view(sub, with_user=True)}


# ─────────────────────────────────────────────────────────────────────────────
# POST /baseline  — calculate b_k for a single competency
# ─────────────────────────────────────────────────────────────────────────────

class EvidencePayload(BaseModel):
    frac_type:              str              # "Domain" | "Functional" | "Behavioural" | "Technical"
    comp_id:                Optional[str] = None   # FRAC catalogue id — enables adjacency synergy
    verified:               float = 0.0     # 0-5, from verified assessment / completed course level
    documented:             float = 0.0     # 0-5, from certificates / latest practice score
    doc_date:               Optional[str] = None   # ISO date of certificate
    tenure:                 float = 0.0     # 0-5, inferred from tenure
    self_report:            float = 0.0     # 0-5, self-assessed
    education:              float = 0.0     # 0-5, from formal education
    seniority:              float = 0.0     # 0-5, designation-based (zeroed for Domain/Functional)
    # SCIL v6 §3 workplace channels (optional)
    work_sample_level:      Optional[int] = None    # level of the best work sample attempted
    work_sample_passed:     bool = False
    utility_level:          Optional[int] = None    # supervisor-confirmed use at this course level
    supervisor_rating:      Optional[float] = None  # APAR 1-5
    rater_id:               Optional[str] = None    # → leniency correction when the rater is known
    completed_level:        int = 0                 # highest completed course level (evidence floor)
    self_reported_level:    int = 0                 # profile claim, resolved as in the dashboard
    # Adjacent competencies' verified scores {compId: 0-5} for synergy (replaces the old count).
    adjacent_verified:      dict[str, float] = {}
    # Deprecated: the count-based synergy path is gone; kept so old clients don't 422.
    verified_count_in_category: int = 0


@router.post("/baseline")
async def calculate_baseline(payload: EvidencePayload):
    """
    Stateless calculator for one competency, on exactly the scoring path the
    dashboard uses (baseline_assembler.assess_competency → resolve_level):
    6-term K with adjacency synergy and recency decay, fused with the optional
    A/U/S workplace channels, confidence ceilings, then the monotone level floors.
    """
    from services import app_state
    from services.baseline_assembler import assess_competency, explain_level, resolve_level
    from services.competency_service import correct_supervisor_rating

    doc_date = None
    if payload.doc_date:
        try:
            doc_date = datetime.fromisoformat(payload.doc_date)
        except ValueError:
            doc_date = None

    ws_level = payload.work_sample_level or 0
    s_raw = payload.supervisor_rating
    s_val, offset = (correct_supervisor_rating(s_raw, payload.rater_id, app_state.ref.rater_offsets)
                     if s_raw is not None else (None, 0.0))
    work = {
        "A": (float(ws_level) if payload.work_sample_passed else max(0.0, ws_level - 0.5)) if ws_level else None,
        "U": float(payload.utility_level) if payload.utility_level else None,
        "S": s_val, "S_raw": s_raw, "raterId": payload.rater_id, "raterOffset": round(offset, 3),
        "workSampleLevel": ws_level if payload.work_sample_passed else 0,
        "appliedLevel": payload.utility_level or 0,
        "peer": 0,
    }
    comp_id = payload.comp_id or "_adhoc"
    assessment = assess_competency(
        frac_type=payload.frac_type, comp_id=comp_id,
        evidence={"verified": payload.verified, "documented": payload.documented, "doc_date": doc_date,
                  "tenure": payload.tenure, "self_report": payload.self_report,
                  "education": payload.education, "seniority": payload.seniority},
        work=work, verified_scores_by_comp={**payload.adjacent_verified, comp_id: payload.verified},
        completed_level=payload.completed_level,
    )
    resolved = resolve_level(assessment, payload.self_reported_level)

    return {
        "status":        "success",
        "baselineScore": assessment["score"],          # fused K/A/U/S, capped by the ceiling
        "knowledgeScore": assessment["knowledgeScore"],  # 6-term b_k
        "confidence":    resolved["confidence"],
        "level":         resolved["level"],
        "basis":         resolved["basis"],
        "evidenceLevel": resolved["evidenceLevel"],
        "ceiling":       assessment["ceiling"],
        "channels":      assessment["channels"],
        "evidence":      assessment["_evidence"],
        "whyThisLevel":  explain_level(assessment, resolved, payload.self_reported_level),
    }
