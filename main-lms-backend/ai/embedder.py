"""
FILE: ai/embedder.py
─────────────────────────────────────────────────────────────────────────────
Shared Singleton Embedder — MoSPI Skill Intelligence Platform (SIH 2026)

Loads ONE embedding model for the ENTIRE backend.
  • ai/semantic_engine.py (chatbot intent classification)
  • services/recommendation_service.py (FAISS course search)

Previously both files loaded 'all-MiniLM-L6-v2' independently (~80 MB × 2).
This singleton fixes that waste and upgrades to a multilingual model.

Model: paraphrase-multilingual-MiniLM-L12-v2
  • 50+ languages: Hindi, Bengali, Marathi, Tamil, Telugu, Gujarati, …
  • Same 384-dim output as all-MiniLM-L6-v2 → zero FAISS index changes
  • Maps Devanagari queries and English catalog into the SAME vector space
    → "साइबर सुरक्षा" matches "Cyber Security" without a translation API

Runtime modes (auto-detected, priority order):
  1. ONNX INT8 (production):  ai/.cache/model_int8.onnx
     • ~115 MB, 2–3× faster CPU inference, NO PyTorch at runtime
     • Generate with:  python scripts/quantize_model.py
     • Download with:  python scripts/download_model.py
  2. sentence-transformers / PyTorch (dev fallback):
     • ~470 MB, requires torch — used when ONNX cache is absent

Usage:
    from ai.embedder import get_embedder
    vecs = get_embedder().encode(["text1", "text2"], normalize_embeddings=True)
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────────
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_CACHE_DIR  = os.path.join(os.path.dirname(__file__), ".cache")
_ONNX_PATH  = os.path.join(_CACHE_DIR, "model_int8.onnx")

# ── Singleton ──────────────────────────────────────────────────────────────────
_embedder: Optional[object] = None


# ── ONNX Inference Wrapper ────────────────────────────────────────────────────

class _OnnxEmbedder:
    """
    Lightweight ONNX runtime embedder — no PyTorch needed at inference time.

    Implements:
      1. HuggingFace AutoTokenizer (sentencepiece, ~few MB download once)
      2. onnxruntime.InferenceSession (CPU, INT8 weights)
      3. Mean pooling + L2 normalization (same as sentence-transformers)

    Output is a float32 np.ndarray, identical contract to SentenceTransformer.encode().
    """

    def __init__(self, onnx_path: str) -> None:
        import onnxruntime as ort
        from transformers import AutoTokenizer

        opts = ort.SessionOptions()
        opts.inter_op_num_threads  = 2
        opts.intra_op_num_threads  = 2
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        logger.info("[Embedder] Starting ONNX session from %s", onnx_path)
        self._session = ort.InferenceSession(
            onnx_path,
            sess_options=opts,
            providers=["CPUExecutionProvider"],
        )
        # Store input names to avoid passing unsupported keys
        self._input_names: set[str] = {inp.name for inp in self._session.get_inputs()}

        logger.info("[Embedder] Loading multilingual tokenizer (%s)…", MODEL_NAME)
        self._tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        logger.info("[Embedder] ONNX embedder ready (inputs: %s).", self._input_names)

    def encode(
        self,
        sentences,
        normalize_embeddings: bool = True,
        batch_size: int = 64,
        show_progress_bar: bool = False,  # ignored (compatibility shim)
        **kwargs,
    ) -> np.ndarray:
        """
        Encode sentences into L2-normalised float32 embeddings.
        API-compatible with SentenceTransformer.encode().
        """
        if isinstance(sentences, str):
            sentences = [sentences]

        all_embs: list[np.ndarray] = []

        for i in range(0, len(sentences), batch_size):
            batch = sentences[i : i + batch_size]
            encoded = self._tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=128,
                return_tensors="np",
            )

            # Build inputs — only pass what the ONNX graph expects
            inputs: dict[str, np.ndarray] = {
                "input_ids":      encoded["input_ids"].astype(np.int64),
                "attention_mask": encoded["attention_mask"].astype(np.int64),
            }
            if "token_type_ids" in self._input_names and "token_type_ids" in encoded:
                inputs["token_type_ids"] = encoded["token_type_ids"].astype(np.int64)

            # ONNX forward pass → last_hidden_state (batch, seq_len, hidden_dim)
            token_embeddings: np.ndarray = self._session.run(None, inputs)[0]

            # Mean pooling weighted by attention mask
            attn   = encoded["attention_mask"].astype(np.float32)[:, :, np.newaxis]
            summed = (token_embeddings * attn).sum(axis=1)
            counts = np.clip(attn.sum(axis=1), a_min=1e-9, a_max=None)
            mean_pooled = summed / counts   # (batch, hidden_dim)

            if normalize_embeddings:
                norms = np.linalg.norm(mean_pooled, axis=1, keepdims=True)
                mean_pooled /= np.clip(norms, a_min=1e-9, a_max=None)

            all_embs.append(mean_pooled.astype(np.float32))

        return np.vstack(all_embs) if len(all_embs) > 1 else all_embs[0]


# ── Public API ─────────────────────────────────────────────────────────────────

def get_embedder() -> _OnnxEmbedder:
    """
    Returns the singleton embedder, loading it on the first call.

    • Thread-safe for concurrent encode() calls after initialization.
    • Automatically chooses ONNX INT8 if cache exists, PyTorch otherwise.
    """
    global _embedder

    if _embedder is not None:
        return _embedder  # type: ignore[return-value]

    # ── Mode 1: ONNX INT8 (production) ────────────────────────────────────
    if os.path.exists(_ONNX_PATH):
        try:
            _embedder = _OnnxEmbedder(_ONNX_PATH)
            logger.info(
                "[Embedder] ✅ ONNX INT8 active (~115 MB). "
                "Single instance shared by chatbot + recommendation engine."
            )
            return _embedder  # type: ignore[return-value]
        except Exception as exc:
            logger.warning("[Embedder] ONNX init failed (%s) — falling back to PyTorch.", exc)

    # ── Mode 2: sentence-transformers / PyTorch (dev fallback) ────────────
    try:
        from sentence_transformers import SentenceTransformer
        logger.warning(
            "[Embedder] ONNX cache not found at %s. "
            "Loading full multilingual model via sentence-transformers (~470 MB). "
            "Run `python scripts/quantize_model.py` to generate the ONNX cache "
            "for a 4× smaller, faster deployment.",
            _ONNX_PATH,
        )
        _embedder = SentenceTransformer(MODEL_NAME)
        return _embedder  # type: ignore[return-value]
    except Exception as exc:
        logger.error("[Embedder] Could not load any embedding model: %s", exc)
        raise RuntimeError(
            f"No embedding model available. "
            f"Either run 'python scripts/download_model.py' or install sentence-transformers. "
            f"Original error: {exc}"
        ) from exc


def is_embedder_ready() -> bool:
    """Non-blocking check — True only if the singleton is already loaded."""
    return _embedder is not None
