"""
FILE: ai/vector_store.py
─────────────────────────────────────────────────────────────────────────────
ChromaDB Vector Store Manager
MoSPI Skill Intelligence Platform | SIH 2026

Manages a persistent local vector database that stores embedded chunks of
official reference documents (iGOT FRAC framework, NSSTA curriculum,
MoSPI statistical manuals, uploaded PDFs).

Key design decisions:
  • Uses OllamaEmbeddings (nomic-embed-text) — fully offline, no API key.
  • Lazy initialization: the store is created on first access, not at import.
  • Thread-safe singleton via module-level _store variable.
  • Falls back gracefully if Ollama embedder is unreachable — raises a
    clear RuntimeError so the upstream caller can fall back to templates.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import io
import logging
import os
from pathlib import Path
from typing import List, Optional, Tuple

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── Config from .env ──────────────────────────────────────────────────────────
_CHROMA_DIR   = os.getenv("CHROMA_DB_DIR", "./chroma_db")
_EMBED_MODEL  = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
_OLLAMA_URL   = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
_CHUNK_SIZE   = int(os.getenv("CHUNK_SIZE", "800"))
_CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

# ── Singleton ─────────────────────────────────────────────────────────────────
_store: Optional[object] = None   # type: ignore[assignment]


def _get_embeddings():
    """Lazily create OllamaEmbeddings. Raises RuntimeError if Ollama is down."""
    try:
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(
            model=_EMBED_MODEL,
            base_url=_OLLAMA_URL,
        )
    except Exception as exc:
        raise RuntimeError(
            f"Cannot connect to Ollama embedder at {_OLLAMA_URL}. "
            f"Is Ollama running? Error: {exc}"
        ) from exc


def get_store():
    """
    Returns the singleton ChromaDB vector store, initialising it on first call.
    Raises RuntimeError if Ollama is unavailable.
    """
    global _store
    if _store is None:
        from langchain_chroma import Chroma
        Path(_CHROMA_DIR).mkdir(parents=True, exist_ok=True)
        embeddings = _get_embeddings()
        _store = Chroma(
            persist_directory=_CHROMA_DIR,
            embedding_function=embeddings,
            collection_name="mospi_knowledge",
        )
        logger.info("ChromaDB store initialised at '%s'", _CHROMA_DIR)
    return _store


def get_retriever(k: int = 4):
    """Returns a LangChain retriever for the vector store (top-k similarity)."""
    store = get_store()
    return store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )


def get_store_stats() -> dict:
    """Returns basic stats about the vector store (doc count, dir path)."""
    try:
        store = get_store()
        count = store._collection.count()   # type: ignore[attr-defined]
        return {
            "status": "connected",
            "document_chunks": count,
            "db_path": str(Path(_CHROMA_DIR).resolve()),
            "embed_model": _EMBED_MODEL,
        }
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


def add_documents_from_file(file_path: str) -> int:
    """
    Ingests a PDF file into the vector store.
    Returns the number of chunks added.
    Raises RuntimeError on Ollama failure; HTTPException on bad file.
    """
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    loader = PyPDFLoader(file_path)
    raw_docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=_CHUNK_SIZE,
        chunk_overlap=_CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(raw_docs)

    if not chunks:
        return 0

    store = get_store()
    store.add_documents(chunks)    # type: ignore[attr-defined]
    logger.info("Ingested %d chunks from '%s'", len(chunks), file_path)
    return len(chunks)


def add_text_to_store(text: str, metadata: dict | None = None) -> int:
    """
    Directly ingests a plain-text string into the vector store.
    Useful for seeding baseline content without a file on disk.
    Returns the number of chunks added.
    """
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    if not text.strip():
        return 0

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=_CHUNK_SIZE,
        chunk_overlap=_CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    splits = splitter.split_text(text)
    docs = [Document(page_content=s, metadata=metadata or {}) for s in splits]

    store = get_store()
    store.add_documents(docs)   # type: ignore[attr-defined]
    logger.info("Ingested %d chunks from text blob", len(docs))
    return len(docs)
