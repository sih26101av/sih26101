"""
FILE: ai/embedder.py
─────────────────────────────────────────────────────────────────────────────
Embedding models for the backend, one per role. Each role loads lazily and
roles configured with the same model share a single instance.

  role "chat"    — Gyan intent classification (ai/semantic_engine.py)
                   default: intfloat/multilingual-e5-small
                   Short user queries in 8 Indian languages + English.
  role "catalog" — course recommendation dense search (services/recommendation_service.py)
                   default: sentence-transformers/all-MiniLM-L6-v2
                   English competency text vs the English course catalogue.

Why two models (see scripts/eval_intents.py and the recommendation A/B):
  • paraphrase-multilingual-MiniLM-L12-v2 scored 45–54% intent accuracy for
    ta/or/bn; multilingual-e5-small scored 79–92% in every language.
  • e5-small ranked English courses noticeably worse than the MiniLM models
    (e.g. "Financial Planning" -> time-series courses), while all-MiniLM-L6-v2
    matched or beat the multilingual MiniLM. Measured cost of the split:
    ~+85 MB RAM over the previous single multilingual model.

Override with CHAT_EMBEDDER_MODEL / CATALOG_EMBEDDER_MODEL.

Usage:
    from ai.embedder import get_embedder
    vecs = get_embedder("chat").encode(["text1", "text2"], normalize_embeddings=True)
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import logging
import os

import numpy as np

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────────
DEFAULT_MODELS = {
    "chat": "intfloat/multilingual-e5-small",
    "catalog": "sentence-transformers/all-MiniLM-L6-v2",
}
_ENV_VARS = {"chat": "CHAT_EMBEDDER_MODEL", "catalog": "CATALOG_EMBEDDER_MODEL"}

# scripts/quantize_model.py exports this model only; the ONNX file is used
# solely when a role is explicitly configured to it.
ONNX_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
_ONNX_PATH = os.path.join(_CACHE_DIR, "model_int8.onnx")

# E5 models are trained with these input prefixes and degrade without them.
_E5_PREFIXES = {"query": "query: ", "passage": "passage: "}

_instances: dict[str, "_Embedder"] = {}


def model_name(role: str = "chat") -> str:
    return os.getenv(_ENV_VARS[role], DEFAULT_MODELS[role])


class _Embedder:
    """Adds `kind` ("query" for short user/intent text, "passage" for catalogue documents)."""

    def __init__(self, model, name: str) -> None:
        self._model = model
        self.name = name
        self._prefixed = "e5" in name.lower()

    def encode(self, sentences, kind: str = "query", **kwargs) -> np.ndarray:
        if self._prefixed:
            prefix = _E5_PREFIXES[kind]
            sentences = prefix + sentences if isinstance(sentences, str) else [prefix + s for s in sentences]
        return self._model.encode(sentences, **kwargs)


# ── ONNX Inference Wrapper ────────────────────────────────────────────────────

class _OnnxEmbedder:
    """
    Lightweight ONNX runtime embedder for ONNX_MODEL — no PyTorch at inference.
    Tokenizer + INT8 onnxruntime session + mean pooling + L2 normalisation.
    """

    def __init__(self, onnx_path: str) -> None:
        import onnxruntime as ort
        from transformers import AutoTokenizer

        opts = ort.SessionOptions()
        opts.inter_op_num_threads = 2
        opts.intra_op_num_threads = 2
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        logger.info("[Embedder] Starting ONNX session from %s", onnx_path)
        self._session = ort.InferenceSession(
            onnx_path,
            sess_options=opts,
            providers=["CPUExecutionProvider"],
        )
        self._input_names: set[str] = {inp.name for inp in self._session.get_inputs()}
        self._tokenizer = AutoTokenizer.from_pretrained(ONNX_MODEL)

    def encode(
        self,
        sentences,
        normalize_embeddings: bool = True,
        batch_size: int = 64,
        show_progress_bar: bool = False,  # compatibility shim
        **kwargs,
    ) -> np.ndarray:
        if isinstance(sentences, str):
            sentences = [sentences]

        all_embs: list[np.ndarray] = []
        for i in range(0, len(sentences), batch_size):
            encoded = self._tokenizer(
                sentences[i : i + batch_size],
                padding=True,
                truncation=True,
                max_length=128,
                return_tensors="np",
            )
            inputs: dict[str, np.ndarray] = {
                "input_ids": encoded["input_ids"].astype(np.int64),
                "attention_mask": encoded["attention_mask"].astype(np.int64),
            }
            if "token_type_ids" in self._input_names and "token_type_ids" in encoded:
                inputs["token_type_ids"] = encoded["token_type_ids"].astype(np.int64)

            token_embeddings: np.ndarray = self._session.run(None, inputs)[0]

            attn = encoded["attention_mask"].astype(np.float32)[:, :, np.newaxis]
            summed = (token_embeddings * attn).sum(axis=1)
            counts = np.clip(attn.sum(axis=1), a_min=1e-9, a_max=None)
            mean_pooled = summed / counts

            if normalize_embeddings:
                norms = np.linalg.norm(mean_pooled, axis=1, keepdims=True)
                mean_pooled /= np.clip(norms, a_min=1e-9, a_max=None)

            all_embs.append(mean_pooled.astype(np.float32))

        return np.vstack(all_embs) if len(all_embs) > 1 else all_embs[0]


# ── Public API ─────────────────────────────────────────────────────────────────

def _load(name: str) -> _Embedder:
    if name == ONNX_MODEL and os.path.exists(_ONNX_PATH):
        try:
            embedder = _Embedder(_OnnxEmbedder(_ONNX_PATH), name)
            logger.info("[Embedder] ONNX INT8 active for %s.", name)
            return embedder
        except Exception as exc:
            logger.warning("[Embedder] ONNX init failed (%s) — falling back to PyTorch.", exc)

    try:
        from sentence_transformers import SentenceTransformer
        logger.info("[Embedder] Loading %s via sentence-transformers.", name)
        return _Embedder(SentenceTransformer(name), name)
    except Exception as exc:
        logger.error("[Embedder] Could not load %s: %s", name, exc)
        raise RuntimeError(f"No embedding model available for {name}: {exc}") from exc


def get_embedder(role: str = "chat") -> _Embedder:
    """Lazily loaded embedder for `role` ("chat" | "catalog"); thread-safe for encode() once loaded."""
    name = model_name(role)
    if name not in _instances:
        _instances[name] = _load(name)
    return _instances[name]


def is_embedder_ready(role: str = "chat") -> bool:
    """Non-blocking check — True only if the role's model is already loaded."""
    return model_name(role) in _instances
