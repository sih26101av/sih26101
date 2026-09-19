"""
FILE: routers/learning_mode.py
─────────────────────────────────────────────────────────────────────────────
Learning Mode — NotebookLM-style study chat for the AI Assessment Studio.

Reuses the document quiz's extraction (routers/rag.py) and chunk-locating
(services/doc_quiz/generate.locate_chunks) so a PDF/PPTX/DOCX/TXT upload here
behaves identically to a quiz upload, but instead of generating questions it
opens a grounded Q&A session over the document:

  POST /start — extract + chunk the document, embed the chunks (shared "chat"
                embedder, ai/embedder.py), ask Gemini for a summary + starter
                questions. Returns a `material_id` for /chat.
  POST /chat  — embed the learner's message, retrieve the closest chunks by
                cosine similarity, and ask Gemini to answer using only those
                excerpts, with locator citations.

Unauthenticated and in-memory, like /rag/upload's QUIZ_STORE — sessions are
lost on restart and not shared across workers (see rag-quiz-generator.md).
─────────────────────────────────────────────────────────────────────────────
"""

import asyncio
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from routers.rag import (
    MAX_FILE_SIZE_BYTES,
    SUPPORTED_EXTENSIONS,
    _chunk_document_text,
    _clean_text,
    _extract_pdf,
    _extract_pptx,
    _extract_txt,
)

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_LEARNING_CHUNKS = 80       # evenly sampled if the document has more
MAX_RETRIEVED_CHUNKS = 5
SUMMARY_EXCERPT_CHARS = 9000
# google.generativeai has no request timeout of its own; a rate-limited or stalled
# call would otherwise keep the learner's spinner going indefinitely.
OVERVIEW_TIMEOUT_S = float(os.getenv("LEARNING_OVERVIEW_TIMEOUT_S", "30"))
CHAT_TIMEOUT_S = float(os.getenv("LEARNING_CHAT_TIMEOUT_S", "60"))


# =============================================================================
# IN-MEMORY STUDY SESSION STORE
# =============================================================================

LEARNING_STORE: Dict[str, Dict[str, Any]] = {}


# =============================================================================
# SCHEMAS
# =============================================================================

class LearningMetadata(BaseModel):
    filename: str
    file_type: str
    character_count: int
    word_count: int
    chunk_count: int
    page_count: Optional[int] = None
    slide_count: Optional[int] = None
    line_count: Optional[int] = None
    section_count: Optional[int] = None
    ocr: Optional[Dict[str, Any]] = None


class LearningStartResponse(BaseModel):
    status: str = "success"
    material_id: str = Field(..., description="Key for POST /chat")
    filename: str
    file_type: str
    metadata: LearningMetadata
    summary: str = Field(..., description="Plain-language overview of the document")
    topics: List[str] = Field(default_factory=list, description="Topics actually covered")
    suggested_questions: List[str] = Field(default_factory=list, description="Starter questions the learner can tap")


class LearningChatMessage(BaseModel):
    role: str   # "user" | "model"
    content: str


class LearningChatRequest(BaseModel):
    material_id: str
    message: str
    history: List[LearningChatMessage] = Field(default_factory=list)


class LearningCitation(BaseModel):
    locator: str
    quote: str


class LearningChatResponse(BaseModel):
    status: str = "success"
    material_id: str
    reply: str
    citations: List[LearningCitation] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    status: str = "error"
    detail: str


# =============================================================================
# HELPERS
# =============================================================================

def _select_summary_text(chunks: List[Any], limit_chars: int = SUMMARY_EXCERPT_CHARS) -> str:
    out, total = [], 0
    for c in chunks:
        piece = f"[{c.locator}] {c.text}"
        if total + len(piece) > limit_chars:
            break
        out.append(piece)
        total += len(piece)
    return "\n\n".join(out)


async def _generate_overview(filename: str, chunks: List[Any]) -> tuple:
    """(summary, topics, suggested_questions). Falls back to a plain summary if Gemini is unavailable."""
    from services.media_quiz import llm

    excerpt = _select_summary_text(chunks)
    prompt = f"""You are an AI study assistant preparing a learner to study a document.
Read the excerpts below (each tagged with its source locator) and return **only** JSON:
{{"summary": "3-5 sentence plain-language summary of what this document covers",
  "topics": ["short topic 1", "short topic 2"],
  "suggested_questions": ["a question a learner could ask to study this document"]}}

Rules:
- Base everything only on the excerpts below — do not invent content that isn't there.
- 4-8 topics, 4-6 suggested_questions.
- Plain sentences in the summary, no markdown.

DOCUMENT: {filename}

EXCERPTS:
{excerpt}
"""
    try:
        data = await asyncio.wait_for(llm.gemini_json(prompt, temperature=0.3), OVERVIEW_TIMEOUT_S)
        summary = str(data.get("summary") or "").strip() or f"Study material from {filename}."
        topics = [str(t).strip() for t in (data.get("topics") or []) if str(t).strip()][:8]
        questions = [str(q).strip() for q in (data.get("suggested_questions") or []) if str(q).strip()][:6]
        return summary, topics, questions
    except Exception as exc:
        logger.warning("[learning] overview generation failed (%s) — using a plain fallback.",
                       exc if str(exc) else type(exc).__name__)
        preview = " ".join(c.text for c in chunks[:3])[:400].strip()
        return (preview or f"Study material from {filename}."), [], []


def _sample_evenly(items: List[Any], n: int) -> List[Any]:
    if len(items) <= n:
        return items
    step = len(items) / n
    return [items[int(i * step)] for i in range(n)]


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post(
    "/start",
    response_model=LearningStartResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload a document and open a grounded study chat session (NotebookLM-style Learning Mode)",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file format or empty payload."},
        413: {"model": ErrorResponse, "description": "File exceeds maximum size limit."},
        422: {"model": ErrorResponse, "description": "Unprocessable document or no readable text."},
        500: {"model": ErrorResponse, "description": "Internal server processing error."},
    },
)
async def start_learning_session(
    file: UploadFile = File(..., description="Document file to study (.pdf, .pptx, .docx, .txt)"),
) -> LearningStartResponse:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided in upload payload.")

    filename = os.path.basename(file.filename)
    _, ext = os.path.splitext(filename.lower())
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed document formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to read uploaded file: {e}")
    finally:
        await file.close()

    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The uploaded file is empty (0 bytes).")
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES // (1024 * 1024)
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                             detail=f"File size exceeds maximum allowed limit of {max_mb} MB.")

    t0 = time.perf_counter()
    page_count = slide_count = line_count = section_count = None
    ocr_report = None
    extracted_text = ""
    is_zip = file_bytes.startswith(b"PK\x03\x04")

    try:
        if ext == ".pdf":
            extracted_text, page_count, ocr_report = await asyncio.to_thread(_extract_pdf, file_bytes)
        elif ext in {".ppt", ".pptx"}:
            if ext == ".ppt" and not is_zip:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                     detail="Legacy binary .ppt files must be converted to .pptx format or PDF.")
            extracted_text, slide_count = _extract_pptx(file_bytes)
        elif ext in {".doc", ".docx"}:
            if not is_zip:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                     detail="Legacy binary .doc files must be saved as .docx or PDF.")
            from services.doc_quiz.extract import extract_docx
            text, section_count = await asyncio.to_thread(extract_docx, file_bytes)
            extracted_text = _clean_text(text)
        elif ext == ".txt":
            extracted_text, line_count = _extract_txt(file_bytes)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.exception("[learning] extraction failed for %s: %s", filename, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail=f"Internal error processing document: {e}")

    if not extracted_text or not extracted_text.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                             detail="No readable text could be extracted from this document.")

    t_extract = time.perf_counter()
    raw_chunks = await asyncio.to_thread(_chunk_document_text, extracted_text, 1000, 150)
    if not raw_chunks:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                             detail="This document is too short to build a study session from.")
    raw_chunks = _sample_evenly(raw_chunks, MAX_LEARNING_CHUNKS)

    from services.doc_quiz.generate import locate_chunks
    doc_chunks = await asyncio.to_thread(locate_chunks, extracted_text, raw_chunks)

    t_chunk = time.perf_counter()
    chunk_vecs = None
    try:
        from ai.embedder import get_embedder
        embedder = await asyncio.to_thread(get_embedder, "chat")
        chunk_vecs = await asyncio.to_thread(
            embedder.encode, [c.text[:1500] for c in doc_chunks], "passage",
            normalize_embeddings=True, show_progress_bar=False,
        )
        chunk_vecs = np.asarray(chunk_vecs, dtype="float32")
    except Exception as exc:
        logger.warning("[learning] embedder unavailable (%s) — chat will use the first chunks unranked.", exc)

    t_embed = time.perf_counter()
    summary, topics, suggested_questions = await _generate_overview(filename, doc_chunks)
    logger.info("[learning] %s: extract %.1fs, chunk %.1fs (%d chunks), embed %.1fs, overview %.1fs",
                filename, t_extract - t0, t_chunk - t_extract, len(doc_chunks),
                t_embed - t_chunk, time.perf_counter() - t_embed)

    material_id = f"LM-{uuid.uuid4().hex[:10].upper()}"
    LEARNING_STORE[material_id] = {
        "material_id": material_id,
        "filename": filename,
        "file_type": ext,
        "chunks": doc_chunks,
        "chunk_vecs": chunk_vecs,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    metadata = LearningMetadata(
        filename=filename, file_type=ext,
        character_count=len(extracted_text), word_count=len(extracted_text.split()),
        chunk_count=len(doc_chunks), page_count=page_count, slide_count=slide_count,
        line_count=line_count, section_count=section_count, ocr=ocr_report,
    )
    return LearningStartResponse(
        material_id=material_id, filename=filename, file_type=ext, metadata=metadata,
        summary=summary, topics=topics, suggested_questions=suggested_questions,
    )


@router.post(
    "/chat",
    response_model=LearningChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a grounded question about the uploaded document (Learning Mode)",
    responses={
        400: {"model": ErrorResponse, "description": "Empty message."},
        404: {"model": ErrorResponse, "description": "Unknown or expired material_id."},
        500: {"model": ErrorResponse, "description": "GEMINI_API_KEY not configured."},
        502: {"model": ErrorResponse, "description": "The LLM failed to answer."},
    },
)
async def learning_chat(payload: LearningChatRequest) -> LearningChatResponse:
    material = LEARNING_STORE.get(payload.material_id)
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="This study session has expired or was never created — upload the document again.")

    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message cannot be empty.")

    chunks: List[Any] = material["chunks"]
    chunk_vecs: Optional[np.ndarray] = material.get("chunk_vecs")
    retrieved = chunks[:MAX_RETRIEVED_CHUNKS]

    if chunk_vecs is not None:
        try:
            from ai.embedder import get_embedder
            embedder = await asyncio.to_thread(get_embedder, "chat")
            q_vec = await asyncio.to_thread(
                embedder.encode, [message], "query", normalize_embeddings=True, show_progress_bar=False,
            )
            sims = np.asarray(chunk_vecs) @ np.asarray(q_vec, dtype="float32")[0]
            order = np.argsort(-sims)[:MAX_RETRIEVED_CHUNKS]
            retrieved = [chunks[i] for i in order]
        except Exception as exc:
            logger.warning("[learning] retrieval embedding failed (%s) — using the first chunks.", exc)

    context_text = "\n\n".join(f"[{c.locator}] {c.text}" for c in retrieved)
    history_text = "\n".join(f"{h.role}: {h.content}" for h in payload.history[-6:]) or "(none yet)"

    prompt = f"""You are Gyan's study companion inside the AI Assessment Studio's Learning Mode — a
NotebookLM-style tutor helping a learner study the document "{material['filename']}" they uploaded.

Answer ONLY using the source excerpts below (each tagged with its locator). If the excerpts don't
contain the answer, say so honestly and suggest what part of the document might help instead — never
invent facts that aren't in the excerpts. Reply in the same language the learner's question is written
in (English or Hindi).

Return **only** JSON:
{{"reply": "<the answer, plain text, may include short markdown>",
  "citations": [{{"locator": "<must be one of the excerpt tags above>", "quote": "<short verbatim phrase from that excerpt>"}}]}}

Recent conversation:
{history_text}

Source excerpts:
{context_text}

Learner's question: {message}
"""

    from services.media_quiz.llm import LLMUnavailable, gemini_json
    try:
        data = await asyncio.wait_for(gemini_json(prompt, temperature=0.2), CHAT_TIMEOUT_S)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                             detail=f"The AI model didn't answer within {int(CHAT_TIMEOUT_S)} s — please ask again.")
    except LLMUnavailable as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail=f"Learning Mode needs GEMINI_API_KEY configured: {exc}")
    except Exception as exc:
        logger.exception("[learning] chat generation failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Could not generate a study answer: {exc}")

    reply = str(data.get("reply") or "").strip() or \
        "I couldn't find that in the document — try asking about one of the suggested topics instead."

    known_locators = {c.locator for c in retrieved}
    citations: List[LearningCitation] = []
    for c in (data.get("citations") or []):
        if not isinstance(c, dict):
            continue
        loc = str(c.get("locator") or "").strip()
        quote = str(c.get("quote") or "").strip()
        if loc and quote and loc in known_locators:
            citations.append(LearningCitation(locator=loc, quote=quote))

    return LearningChatResponse(material_id=payload.material_id, reply=reply, citations=citations[:4])
