"""
FILE: ai/reranker.py
─────────────────────────────────────────────────────────────────────────────
Optional multilingual cross-encoder for re-ranking the recommendation engine's
top candidates (services/recommendation_service.py, Stage 2b).

A cross-encoder reads (query, course text) together and scores their match —
more accurate than comparing two independent embeddings, but one model call
per pair, so it only re-scores the top RERANK_TOP_N (20) of a shortlist.

  default model: cross-encoder/mmarco-mMiniLMv2-L12-H384-v1 (multilingual, ~118M params)
  RERANKER_MODEL      — override the model
  ENABLE_CROSS_ENCODER — "1"/"true" to turn it on (OFF by default: production
                         runs without PyTorch and the model is a ~470 MB download)

Backends, in order: an ONNX export in ai/.cache/onnx/<model>/ (model.onnx +
tokenizer.json, same layout as scripts/download_model.py writes), else
sentence_transformers.CrossEncoder. If neither loads, get_reranker() returns
None and the engine keeps its RRF ranking — never an error on the request path.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
import os
import threading
from typing import List, Optional, Sequence, Tuple

import numpy as np

from ai.embedder import onnx_model_dir

logger = logging.getLogger(__name__)

DEFAULT_RERANKER = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
RERANK_TOP_N = 20

_instance: Optional["_Reranker"] = None
_failed = False
_lock = threading.Lock()


def reranker_enabled() -> bool:
    return os.getenv("ENABLE_CROSS_ENCODER", "").strip().lower() in ("1", "true", "yes")


def reranker_name() -> str:
    return os.getenv("RERANKER_MODEL", DEFAULT_RERANKER)


class _Reranker:
    def __init__(self, name: str) -> None:
        self.name = name
        self._onnx = None
        self._st = None
        model_dir = onnx_model_dir(name)
        if os.path.exists(os.path.join(model_dir, "model.onnx")):
            import onnxruntime as ort
            from tokenizers import Tokenizer
            self._onnx = ort.InferenceSession(os.path.join(model_dir, "model.onnx"),
                                              providers=["CPUExecutionProvider"])
            self._inputs = {i.name for i in self._onnx.get_inputs()}
            self._tok = Tokenizer.from_file(os.path.join(model_dir, "tokenizer.json"))
            self._tok.enable_truncation(max_length=256)
            self._tok.enable_padding()
            logger.info("[Reranker] ONNX cross-encoder active: %s", name)
        else:
            from sentence_transformers import CrossEncoder
            self._st = CrossEncoder(name, max_length=256)
            logger.info("[Reranker] sentence-transformers cross-encoder active: %s", name)

    def score(self, pairs: Sequence[Tuple[str, str]]) -> np.ndarray:
        """Relevance logits, one per (query, passage) pair (higher = better match)."""
        if not pairs:
            return np.zeros(0, dtype=np.float32)
        if self._st is not None:
            return np.asarray(self._st.predict(list(pairs), show_progress_bar=False), dtype=np.float32).reshape(-1)
        encs = self._tok.encode_batch([(q, p) for q, p in pairs])
        feeds = {"input_ids": np.array([e.ids for e in encs], dtype=np.int64),
                 "attention_mask": np.array([e.attention_mask for e in encs], dtype=np.int64)}
        if "token_type_ids" in self._inputs:
            feeds["token_type_ids"] = np.array([e.type_ids for e in encs], dtype=np.int64)
        logits = self._onnx.run(None, feeds)[0]
        return np.asarray(logits, dtype=np.float32)[:, 0] if logits.ndim == 2 else logits.reshape(-1)


def get_reranker() -> Optional[_Reranker]:
    """The loaded cross-encoder, or None when disabled / unavailable (logged once)."""
    global _instance, _failed
    if not reranker_enabled() or _failed:
        return None
    if _instance is None:
        with _lock:
            if _instance is None and not _failed:
                try:
                    _instance = _Reranker(reranker_name())
                except Exception as exc:
                    _failed = True
                    logger.warning("[Reranker] cross-encoder unavailable (%s) — keeping RRF ranking.", exc)
                    return None
    return _instance


def rerank_scores(query: str, passages: List[str]) -> Optional[np.ndarray]:
    """Cross-encoder scores for `passages` against `query`, or None if no reranker."""
    rr = get_reranker()
    if rr is None:
        return None
    try:
        return rr.score([(query, p) for p in passages])
    except Exception as exc:
        logger.warning("[Reranker] scoring failed (%s) — keeping RRF ranking.", exc)
        return None
