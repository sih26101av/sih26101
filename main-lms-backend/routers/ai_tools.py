"""
FILE: routers/ai_tools.py
─────────────────────────────────────────────────────────────────────────────
AI Tools Router — Knowledge Ingestion & Health Endpoints
MoSPI Skill Intelligence Platform | SIH 2026

Exposes two admin/utility endpoints:
  POST /api/v1/ai/upload-knowledge  — Ingest a PDF into ChromaDB
  GET  /api/v1/ai/health            — Ollama + ChromaDB connectivity status

These are separate from the Gemini quiz upload (/api/v1/rag/upload).
The upload-knowledge endpoint is intentionally left open (no auth) for
demo convenience — it can be gated with Depends(get_current_user) later.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import logging
import os
import shutil
import time
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

# Temporary directory for uploaded files during ingestion
_TEMP_DIR = Path("./temp_uploads")
_TEMP_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf"}


# ── Response models ───────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    ollama_status: str          # "connected" | "offline"
    ollama_model: str
    ollama_url: str
    chromadb_status: str        # "connected" | "error"
    chromadb_chunks: int | None
    chromadb_path: str | None
    embed_model: str

class UploadKnowledgeResponse(BaseModel):
    status: str
    filename: str
    chunks_indexed: int
    message: str


# ── GET /api/v1/ai/health ─────────────────────────────────────────────────────

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check Ollama LLM + ChromaDB vector store connectivity",
)
async def ai_health_check() -> HealthResponse:
    """
    Returns the live status of the two AI backend components:
    - Ollama local LLM runner
    - ChromaDB persistent vector store
    Use this from the frontend to display 'AI Powered' vs 'Standard Mode'.
    """
    from ai.rag_engine import is_ollama_available, _OLLAMA_MODEL, _OLLAMA_URL
    from ai.vector_store import get_store_stats, _EMBED_MODEL

    ollama_ok = is_ollama_available()

    db_stats = get_store_stats()

    return HealthResponse(
        ollama_status="connected" if ollama_ok else "offline",
        ollama_model=_OLLAMA_MODEL,
        ollama_url=_OLLAMA_URL,
        chromadb_status=db_stats.get("status", "error"),
        chromadb_chunks=db_stats.get("document_chunks"),
        chromadb_path=db_stats.get("db_path"),
        embed_model=_EMBED_MODEL,
    )


# ── POST /api/v1/ai/upload-knowledge ─────────────────────────────────────────

@router.post(
    "/upload-knowledge",
    response_model=UploadKnowledgeResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload a PDF document into the ChromaDB knowledge base",
)
async def upload_knowledge_document(
    file: UploadFile = File(
        ...,
        description="PDF document to embed into the RAG knowledge base",
    ),
) -> UploadKnowledgeResponse:
    """
    Accepts a PDF file, embeds it into the local ChromaDB vector store
    using nomic-embed-text (via Ollama), and makes it immediately
    available for Gyan's RAG pipeline to retrieve and reason over.

    Requires Ollama to be running with nomic-embed-text pulled:
        ollama pull nomic-embed-text
    """
    # 1. Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided.",
        )

    filename = Path(file.filename).name
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only PDF files are supported for knowledge ingestion. Got: '{ext}'",
        )

    # 2. Read file
    try:
        file_bytes = await file.read()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file: {exc}",
        ) from exc
    finally:
        await file.close()

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes).",
        )

    if len(file_bytes) > 25 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds 25 MB limit.",
        )

    # 3. Save to temp file (PyPDFLoader needs a disk path)
    temp_path = _TEMP_DIR / f"{int(time.time())}_{filename}"
    try:
        with open(temp_path, "wb") as f:
            f.write(file_bytes)

        # 4. Ingest into ChromaDB
        from ai.vector_store import add_documents_from_file

        try:
            chunks = add_documents_from_file(str(temp_path))
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    f"Ollama embedding service is unavailable. "
                    f"Ensure Ollama is running and 'nomic-embed-text' is pulled. "
                    f"Error: {exc}"
                ),
            ) from exc

    finally:
        # Clean up temp file regardless
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)

    return UploadKnowledgeResponse(
        status="success",
        filename=filename,
        chunks_indexed=chunks,
        message=(
            f"Successfully indexed {chunks} chunks from '{filename}' into the "
            "knowledge base. Gyan will now use this document in future responses."
        ),
    )
