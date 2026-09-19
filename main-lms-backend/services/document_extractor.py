"""
FILE: main-lms-backend/services/document_extractor.py
─────────────────────────────────────────────────────────────────────────────
Maps an uploaded certificate / resume (PDF or image) to FRAC competencies.

Two backends, tried in order:
  1. gemini  — Gemini JSON output (services/media_quiz/llm.gemini_json) given the
               document text, or the image itself for scans / photos.
  2. ocr+e5  — fully local: pypdf text (RapidOCR for images and scanned PDFs),
               multilingual-e5 cosine against the FRAC descriptions, and
               keyword rules for level / issuer / date. No local LLM needed.

Competency ids always come from the canonical FRAC dictionary
(mock-igot-server/data/frac_competencies.json), the same ids the recommendation
engine and the skill-gap crosswalk use. Ids the LLM invents are dropped.

The service works on bytes in memory — nothing is written to disk.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import asyncio
import io
import json
import logging
import os
import re
from datetime import date
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

_FRAC_PATH = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "mock-igot-server", "data", "frac_competencies.json"))

MATCH_FLOOR = float(os.getenv("CERT_MATCH_FLOOR", "0.80"))   # e5 cosine to count as a match
MATCH_BAND = 0.02                                             # keep matches this close to the best
MAX_COMPETENCIES = 3
MAX_LLM_CHARS = 12000
MAX_IMAGES = 3


# ── Structured Output Schemas ────────────────────────────────────────────────

class ExtractedCompetency(BaseModel):
    competency_id: str = Field(..., description="The exact id of the matched FRAC competency.")
    competency_name: str = Field(..., description="Name of the matched competency.")
    extracted_level: float = Field(..., description="Skill level (1.0 to 5.0). Beginner=2.0, Intermediate=3.0, Advanced=4.0.")
    issue_date: Optional[str] = Field(None, description="Date of issuance (YYYY-MM-DD).")
    justification: str = Field(..., description="Brief rationale explaining why this score was chosen based on document text.")
    match_score: Optional[float] = None     # e5 cosine (ocr+e5 backend only)


class CertificateExtractionResult(BaseModel):
    is_valid_credential: bool = Field(..., description="True if document is a valid training record or resume.")
    issuing_organization: Optional[str] = Field(None, description="Organization that issued the credential.")
    extracted_competencies: List[ExtractedCompetency]
    extractor: str = "gemini"


class ExtractionError(ValueError):
    """The document could not be read (no text layer, OCR unavailable, bad file)."""


# ── FRAC dictionary ──────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def frac_dictionary() -> List[Dict[str, str]]:
    with open(_FRAC_PATH, encoding="utf-8") as f:
        data = json.load(f)
    items = data if isinstance(data, list) else next((v for v in data.values() if isinstance(v, list)), [])
    return [{"id": c["id"], "name": c.get("name", ""), "description": c.get("description", ""),
             "competencyType": c.get("competencyType", "Domain")}
            for c in items if isinstance(c, dict) and c.get("id")]


def frac_by_id() -> Dict[str, Dict[str, str]]:
    return {c["id"]: c for c in frac_dictionary()}


# ── Field normalisation (shared by both backends) ────────────────────────────

_MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}
_DATE_PATTERNS = [
    (re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b"), ("y", "m", "d")),
    (re.compile(r"\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})\b"), ("d", "m", "y")),       # Indian DD/MM/YYYY
    (re.compile(r"\b([A-Za-z]{3,9})\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b"), ("mon", "d", "y")),
    (re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]{3,9})\.?,?\s+(\d{4})\b"), ("d", "mon", "y")),
    (re.compile(r"\b([A-Za-z]{3,9})\.?,?\s+(\d{4})\b"), ("mon", "y")),
]


def normalise_date(raw: Optional[str]) -> Optional[str]:
    """Any common date spelling → YYYY-MM-DD; None if absent, unparseable or in the future."""
    if not raw:
        return None
    s = str(raw).strip()
    for rx, order in _DATE_PATTERNS:
        for m in rx.finditer(s):
            parts = dict(zip(order, m.groups()))
            try:
                month = _MONTHS.get(parts["mon"][:3].lower()) if "mon" in parts else int(parts["m"])
                if not month:
                    continue
                d = date(int(parts["y"]), month, int(parts.get("d", 1)))
            except (ValueError, KeyError):
                continue
            if 1980 <= d.year and d <= date.today():
                return d.isoformat()
    y = re.search(r"\b(19[89]\d|20\d\d)\b", s)
    if y and int(y.group(1)) <= date.today().year:
        return f"{y.group(1)}-01-01"
    return None


def _clamp_level(v) -> float:
    try:
        return float(min(5.0, max(1.0, float(v))))
    except (TypeError, ValueError):
        return 2.0


def _validated(raw: dict, extractor: str) -> CertificateExtractionResult:
    """LLM JSON → result with only real FRAC ids (unknown ids re-matched by name, else dropped)."""
    by_id = frac_by_id()
    by_name = {c["name"].lower(): c for c in frac_dictionary()}
    comps: List[ExtractedCompetency] = []
    seen = set()
    for c in raw.get("extracted_competencies") or []:
        if not isinstance(c, dict):
            continue
        ref = by_id.get(str(c.get("competency_id", "")).strip()) \
            or by_name.get(str(c.get("competency_name", "")).strip().lower())
        if not ref or ref["id"] in seen:
            continue
        seen.add(ref["id"])
        comps.append(ExtractedCompetency(
            competency_id=ref["id"], competency_name=ref["name"],
            extracted_level=_clamp_level(c.get("extracted_level")),
            issue_date=normalise_date(c.get("issue_date")),
            justification=str(c.get("justification") or "")[:500],
        ))
    return CertificateExtractionResult(
        is_valid_credential=bool(raw.get("is_valid_credential")),
        issuing_organization=(str(raw.get("issuing_organization")).strip()[:120]
                              if raw.get("issuing_organization") else None),
        extracted_competencies=comps[:MAX_COMPETENCIES],
        extractor=extractor,
    )


# ── Document reading ─────────────────────────────────────────────────────────

def _pdf_text_and_images(data: bytes) -> Tuple[str, List[bytes]]:
    """Text layer + (for scans) the embedded page images of the first pages."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        text = "\n".join((p.extract_text() or "") for p in reader.pages)
        images: List[bytes] = []
        if len(text.strip()) < 40:
            for page in reader.pages[:MAX_IMAGES]:
                for img in page.images[:1]:
                    images.append(img.data)
        return text, images
    except Exception as exc:
        raise ExtractionError(f"Failed to read PDF: {exc}") from exc


def _to_jpeg(img: bytes) -> bytes:
    try:
        from PIL import Image
        with Image.open(io.BytesIO(img)) as im:
            out = io.BytesIO()
            im.convert("RGB").save(out, format="JPEG", quality=90)
            return out.getvalue()
    except Exception:
        return img


def _ocr(images: List[bytes]) -> str:
    try:
        from services.media_quiz.probe import get_ocr
        eng = get_ocr()
    except Exception as exc:
        raise ExtractionError(
            "This file has no text layer and OCR is not installed "
            "(pip install -r requirements-media.txt) — configure GEMINI_API_KEY or upload a text PDF."
        ) from exc
    lines: List[str] = []
    for img in images:
        result, _ = eng(_to_jpeg(img))
        lines += [r[1] for r in (result or []) if len(r) > 2 and float(r[2]) >= 0.5]
    return "\n".join(lines)


# ── Local backend: keyword rules + e5 similarity ─────────────────────────────

_CREDENTIAL_WORDS = re.compile(
    r"certif|completion|completed|awarded|successfully|diploma|degree|course|training|"
    r"curriculum vitae|resume|résumé|programme|program|workshop", re.I)
_LEVEL_RULES = [
    (4.0, re.compile(r"\b(advanced|expert|master(?:'s|s)? |professional certificate|specialist|mastery)", re.I)),
    (3.0, re.compile(r"\b(intermediate|bootcamp|specialization|applied|practitioner|post[- ]graduate)", re.I)),
    (2.0, re.compile(r"\b(beginner|introduct|basic|fundamental|foundation|essentials|primer)", re.I)),
]
_KNOWN_ISSUERS = [
    "Coursera", "Udemy", "edX", "NPTEL", "SWAYAM", "C-DAC", "CDAC", "NSSTA", "iGOT", "NIELIT",
    "LinkedIn Learning", "Google", "Microsoft", "IBM", "AWS", "Amazon Web Services", "DataCamp",
    "Indian Statistical Institute", "ISI", "World Bank", "IMF", "UNSIAP", "UN Statistics Division",
    "Great Learning", "Simplilearn", "upGrad",
]
_ISSUER_RX = re.compile(
    r"(?:issued|offered|awarded|presented|conducted|organi[sz]ed)\s+by\s*:?\s+(?:the\s+)?"
    r"([A-Z][\w&.,'()\- ]{2,80}?)(?:\s+on\b|[.\n]|$)")


def _issuer(text: str) -> Optional[str]:
    m = _ISSUER_RX.search(text)
    if m:
        return m.group(1).strip(" ,.-")
    for name in _KNOWN_ISSUERS:
        if re.search(rf"\b{re.escape(name)}\b", text, re.I):
            return name
    for rx in (r"\b(?:Indian Institute of [A-Z][\w ]+|IIT \w+|IIM \w+|University of [A-Z][\w ]+|[A-Z][\w ]+ University)\b",):
        m = re.search(rx, text)
        if m:
            return m.group(0).strip()
    return None


def _level(text: str) -> Optional[float]:
    for lvl, rx in _LEVEL_RULES:
        if rx.search(text):
            return lvl
    return None


def _segments(text: str) -> List[str]:
    parts = [p.strip() for p in re.split(r"[\n\r]+|(?<=[.!?])\s+", text) if len(p.strip()) >= 8]
    return (parts or [text.strip()])[:80]


def _local_extract(text: str) -> CertificateExtractionResult:
    from ai.embedder import encode_cached, get_embedder

    comps = frac_dictionary()
    emb = get_embedder("chat")
    comp_vecs = encode_cached("chat", [f"{c['name']}. {c['description']}" for c in comps],
                              kind="passage", embedder=emb)
    segs = _segments(text)
    seg_vecs = np.asarray(emb.encode(segs + [text[:1500]], kind="query",
                                     normalize_embeddings=True, show_progress_bar=False), dtype="float32")
    sims = seg_vecs @ comp_vecs.T                       # (segments, competencies)
    best = sims.max(axis=0)
    order = np.argsort(-best)
    top = float(best[order[0]]) if len(order) else 0.0

    issue = normalise_date(text)
    out: List[ExtractedCompetency] = []
    for j in order[:MAX_COMPETENCIES]:
        s = float(best[j])
        if s < MATCH_FLOOR or s < top - MATCH_BAND:
            break
        seg = segs[int(sims[:, j][:len(segs)].argmax())] if segs else text[:120]
        lvl = _level(seg) or _level(text) or 2.0
        out.append(ExtractedCompetency(
            competency_id=comps[j]["id"], competency_name=comps[j]["name"],
            extracted_level=lvl, issue_date=issue, match_score=round(s, 3),
            justification=f'"{seg[:160]}" matches this competency (similarity {s:.2f}); level from wording.',
        ))
    return CertificateExtractionResult(
        is_valid_credential=bool(_CREDENTIAL_WORDS.search(text)),
        issuing_organization=_issuer(text),
        extracted_competencies=out,
        extractor="ocr+e5",
    )


# ── Gemini backend ───────────────────────────────────────────────────────────

_SYSTEM_PROMPT = (
    "You are an expert HR Skill Intelligence Auditor for Indian government statistical officials. "
    "Extract the training record below into JSON with keys is_valid_credential (bool), "
    "issuing_organization (string or null) and extracted_competencies (list of "
    "{competency_id, competency_name, extracted_level, issue_date, justification}).\n\n"
    "RULES:\n"
    "1. ISSUER: extract the issuing organisation (e.g. Coursera, NPTEL, CDAC, NSSTA, a university).\n"
    "2. SKILL MAPPING: map the document's skills ONLY to entries of the FRAC list, copying the id "
    "exactly. At most 3 competencies; omit anything without a close match.\n"
    "3. DATES: issue_date as YYYY-MM-DD; if only a year is present use YYYY-01-01; null if absent.\n"
    "4. LEVELS: 2.0 beginner/introductory, 3.0 intermediate/bootcamp, 4.0 advanced/expert.\n"
    "5. NO HALLUCINATIONS: if the document is not a certificate, transcript or resume set "
    "is_valid_credential to false and return an empty list."
)


async def _gemini_extract(text: str, images: List[bytes]) -> CertificateExtractionResult:
    from services.media_quiz.llm import gemini_json

    ref = json.dumps([{"id": c["id"], "name": c["name"], "category": c["competencyType"]}
                      for c in frac_dictionary()])
    body = f"Document Text:\n{text[:MAX_LLM_CHARS]}" if text.strip() else "The document is the attached image(s)."
    raw = await gemini_json(f"{_SYSTEM_PROMPT}\n\nFRAC Dictionary Reference:\n{ref}\n\n{body}",
                            images=[_to_jpeg(i) for i in images[:MAX_IMAGES]] or None, temperature=0.0)
    if not isinstance(raw, dict):
        raise ValueError("Gemini returned a non-object JSON value")
    return _validated(raw, "gemini")


# ── Service ──────────────────────────────────────────────────────────────────

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


class DocumentExtractorService:
    """`await extract(data, filename)` — Gemini if configured, else OCR + e5."""

    async def extract(self, data: bytes, filename: str) -> CertificateExtractionResult:
        ext = os.path.splitext(filename or "")[1].lower()
        if ext == ".pdf":
            text, images = await asyncio.to_thread(_pdf_text_and_images, data)
        elif ext in IMAGE_EXTS:
            text, images = "", [data]
        else:
            raise ExtractionError("Only PDF or image (PNG/JPG/WEBP) certificates are supported.")

        from services.media_quiz.llm import gemini_key
        if gemini_key():
            try:
                return await _gemini_extract(text, images)
            except Exception as exc:        # LLMUnavailable, bad JSON, quota … → local path
                logger.warning("[certificate] Gemini extraction failed, using OCR+e5: %s", exc)

        if images and len(text.strip()) < 40:
            text = await asyncio.to_thread(_ocr, images)
        if len(text.strip()) < 20:
            raise ExtractionError("No readable text found in the document.")
        return await asyncio.to_thread(_local_extract, text)


# ─────────────────────────────────────────────────────────────────────────────
# Self-test: python -m services.document_extractor   (from main-lms-backend/)
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mock_text = (
        "CERTIFICATE OF COMPLETION\nThis certifies that Anshika Sharma has successfully "
        "completed the 'Advanced Python for Data Science and Statistical Modeling' bootcamp.\n"
        "Issued by Coursera on August 15, 2023."
    )
    res = _local_extract(mock_text)
    print(res.model_dump_json(indent=2))
