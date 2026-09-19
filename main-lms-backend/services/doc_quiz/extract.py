"""
FILE: services/doc_quiz/extract.py
─────────────────────────────────────────────────────────────────────────────
Document sources the quiz router did not read before:

  extract_docx(bytes)            .docx via python-docx, paragraphs AND tables in
                                 body order; headings start "--- Section k: … ---"
                                 markers so citations can say where a passage is.
                                 Falls back to the raw word/document.xml text.
  ocr_pdf_pages(bytes, pages)    scanned PDF pages: pypdfium2 renders each page
                                 (DOC_OCR_SCALE=2 → 144 dpi), RapidOCR (the same
                                 engine as the media pipeline) reads it. Pages are
                                 rendered in small batches (pdfium is not thread-
                                 safe) and recognised in parallel.

RapidOCR is optional (requirements-media.txt). Without it a scanned PDF still
returns 422, with a message saying OCR is not installed. Its recognition model
is Chinese/English: Devanagari scans read poorly (same caveat as media OCR).
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import io
import logging
import os
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)

OCR_MIN_CHARS = int(os.getenv("DOC_OCR_MIN_CHARS", "40"))      # a page with less text layer than this is OCR'd
OCR_MAX_PAGES = int(os.getenv("DOC_OCR_MAX_PAGES", "40"))
OCR_SCALE = float(os.getenv("DOC_OCR_SCALE", "2.0"))
OCR_LINE_MIN_SCORE = 0.5


class OcrUnavailable(RuntimeError):
    pass


# ── DOCX ──────────────────────────────────────────────────────────────────────

_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _table_rows(table) -> List[str]:
    rows = []
    for row in table.rows:
        cells: List[str] = []
        for cell in row.cells:
            t = " ".join(cell.text.split())
            if t and (not cells or cells[-1] != t):        # merged cells repeat their text
                cells.append(t)
        if cells:
            rows.append(" | ".join(cells))
    return rows


def extract_docx(file_bytes: bytes) -> Tuple[str, int]:
    """Returns (text with section markers, section count)."""
    try:
        from docx import Document
        from docx.table import Table
        from docx.text.paragraph import Paragraph

        doc = Document(io.BytesIO(file_bytes))
        parts: List[str] = []
        sections = 0
        for child in doc.element.body.iterchildren():
            tag = child.tag.rsplit("}", 1)[-1]
            if tag == "p":
                para = Paragraph(child, doc)
                text = " ".join(para.text.split())
                if not text:
                    continue
                style = (para.style.name if para.style is not None else "") or ""
                if style.lower().startswith(("heading", "title")):
                    sections += 1
                    parts.append(f"--- Section {sections}: {text[:120]} ---")
                else:
                    parts.append(text)
            elif tag == "tbl":
                rows = _table_rows(Table(child, doc))
                if rows:
                    parts.append("\n".join(rows))
        if parts:
            if not sections:
                parts.insert(0, "--- Section 1 ---")
                sections = 1
            return "\n\n".join(parts), sections
    except Exception as exc:
        logger.warning("[doc-quiz] python-docx failed (%s); reading word/document.xml directly", exc)

    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            root = ET.fromstring(z.read("word/document.xml"))
    except Exception as exc:
        raise ValueError(f"Could not open the Word document: {exc}") from exc
    paras = []
    for p in root.iter(f"{_W}p"):
        text = "".join(t.text or "" for t in p.iter(f"{_W}t")).strip()
        if text:
            paras.append(" ".join(text.split()))
    return ("--- Section 1 ---\n\n" + "\n\n".join(paras)) if paras else "", 1 if paras else 0


# ── OCR for scanned PDFs ──────────────────────────────────────────────────────

def _ocr_engine():
    try:
        from services.media_quiz.probe import get_ocr, map_frames
        return get_ocr(), map_frames
    except ImportError as exc:
        raise OcrUnavailable("OCR is not installed (pip install -r requirements-media.txt for rapidocr_onnxruntime).") from exc


def _read(eng, image: np.ndarray) -> Tuple[str, float, int]:
    """(text in reading order, mean confidence, weak lines dropped)."""
    try:
        result, _ = eng(image)
    except Exception as exc:
        logger.warning("[doc-quiz] OCR failed on a page: %s", exc)
        return "", 0.0, 0
    lines, weak = [], 0
    for box, text, score in result or []:
        text = str(text).strip()
        if float(score) >= OCR_LINE_MIN_SCORE and len(text) >= 2:
            lines.append((np.asarray(box, dtype=float), text, float(score)))
        else:
            weak += 1
    if not lines:
        return "", 0.0, weak
    # Row by row (12 px bands at 144 dpi), then left to right.
    lines.sort(key=lambda l: (round(l[0][:, 1].min() / 12), l[0][:, 0].min()))
    weights = np.array([len(l[1]) for l in lines], dtype=float)
    conf = float(np.average([l[2] for l in lines], weights=weights))
    return "\n".join(l[1] for l in lines), conf, weak


def ocr_pdf_pages(file_bytes: bytes, pages: List[int]) -> Tuple[Dict[int, str], Dict]:
    """OCR the given 1-based pages. Returns ({page: text}, report)."""
    try:
        import pypdfium2 as pdfium
    except ImportError as exc:
        raise OcrUnavailable("pypdfium2 is not installed (it ships with pdfplumber).") from exc
    eng, map_frames = _ocr_engine()

    wanted = sorted(set(pages))
    todo, skipped = wanted[:OCR_MAX_PAGES], wanted[OCR_MAX_PAGES:]
    out: Dict[int, str] = {}
    confs: List[float] = []
    weak_total = 0
    pdf = pdfium.PdfDocument(file_bytes)
    try:
        batch = max(1, int(os.getenv("MEDIA_OCR_WORKERS", "4")))
        for i in range(0, len(todo), batch):
            images = []
            for pno in todo[i:i + batch]:
                page = pdf[pno - 1]
                try:
                    pil = page.render(scale=OCR_SCALE).to_pil().convert("RGB")
                finally:
                    page.close()
                images.append((pno, np.ascontiguousarray(np.asarray(pil)[:, :, ::-1])))   # RGB → BGR
            for (pno, _), (text, conf, weak) in zip(images, map_frames(lambda it: _read(eng, it[1]), images)):
                weak_total += weak
                if text:
                    out[pno] = text
                    confs.append(conf)
    finally:
        pdf.close()
    report = {
        "pages_ocrd": len(todo),
        "pages_with_text": len(out),
        "pages_skipped_over_cap": len(skipped),
        "mean_confidence": round(float(np.mean(confs)), 3) if confs else None,
        "weak_lines_dropped": weak_total,
    }
    return out, report


def needs_ocr(page_text: str) -> bool:
    return len(re.sub(r"\s+", "", page_text or "")) < OCR_MIN_CHARS
