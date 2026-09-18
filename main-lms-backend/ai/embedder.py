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

Backends, in order of preference:
  1. ONNX Runtime over ai/.cache/onnx/<model>/ (scripts/download_model.py) —
     the model's own fp32 ONNX export, so the same vectors as (2) without
     importing PyTorch (~15 s) or holding it in memory.
  2. sentence-transformers (PyTorch), downloading from the HF Hub if needed.

Override with CHAT_EMBEDDER_MODEL / CATALOG_EMBEDDER_MODEL.

Usage:
    from ai.embedder import get_embedder, encode_cached
    vecs = get_embedder("chat").encode(["text1", "text2"], normalize_embeddings=True)
    corpus = encode_cached("catalog", texts)      # memoised on disk
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import hashlib
import logging
import os
import threading

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
_CACHE_DIR = os.getenv("EMBEDDER_CACHE_DIR", os.path.join(os.path.dirname(__file__), ".cache"))
_ONNX_PATH = os.path.join(_CACHE_DIR, "model_int8.onnx")
# Per-model ONNX exports fetched by scripts/download_model.py.
_ONNX_DIR = os.path.join(_CACHE_DIR, "onnx")
# Encoded fixed corpora (intent prototypes, course catalogue), keyed by model + texts.
_EMB_DIR = os.path.join(_CACHE_DIR, "emb")

# E5 models are trained with these input prefixes and degrade without them.
_E5_PREFIXES = {"query": "query: ", "passage": "passage: "}

_instances: dict[str, "_Embedder"] = {}
_load_lock = threading.Lock()


def model_name(role: str = "chat") -> str:
    return os.getenv(_ENV_VARS[role], DEFAULT_MODELS[role])


def onnx_model_dir(name: str) -> str:
    return os.path.join(_ONNX_DIR, name.replace("/", "__"))


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
    sentence-transformers-compatible encoder on onnxruntime + HF `tokenizers`
    (neither imports PyTorch or transformers). Tokenise → ONNX transformer →
    attention-masked mean pooling → optional L2 normalisation.
    """

    def __init__(self, onnx_path: str, tokenizer, max_length: int, lower_case: bool = False) -> None:
        import onnxruntime as ort

        opts = ort.SessionOptions()
        opts.inter_op_num_threads = 1
        opts.intra_op_num_threads = int(os.getenv("EMBEDDER_THREADS", "0")) or min(4, os.cpu_count() or 1)
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        opts.enable_cpu_mem_arena = False   # lower resident memory on small instances

        logger.info("[Embedder] Starting ONNX session from %s", onnx_path)
        self._session = ort.InferenceSession(onnx_path, sess_options=opts, providers=["CPUExecutionProvider"])
        self._input_names: set[str] = {inp.name for inp in self._session.get_inputs()}
        self._tokenizer = tokenizer
        self._tokenizer.enable_truncation(max_length=max_length)
        self._lower_case = lower_case

    @classmethod
    def from_dir(cls, model_dir: str) -> "_OnnxEmbedder":
        """A directory written by scripts/download_model.py."""
        import json
        from tokenizers import Tokenizer

        def _json(*parts):
            with open(os.path.join(model_dir, *parts), encoding="utf-8") as f:
                return json.load(f)

        st_config = _json("sentence_bert_config.json")
        max_length = int(st_config.get("max_seq_length", 512))
        if not _json("1_Pooling", "config.json").get("pooling_mode_mean_tokens", False):
            raise ValueError("only mean pooling is implemented for ONNX")
        pad = _json("special_tokens_map.json").get("pad_token")
        pad_token = pad["content"] if isinstance(pad, dict) else pad

        tokenizer = Tokenizer.from_file(os.path.join(model_dir, "tokenizer.json"))
        tokenizer.enable_padding(pad_id=tokenizer.token_to_id(pad_token) or 0, pad_token=pad_token)
        return cls(os.path.join(model_dir, "model.onnx"), tokenizer, max_length,
                   bool(st_config.get("do_lower_case", False)))

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
        # Same preprocessing as sentence_transformers.models.Transformer.tokenize.
        sentences = [s.strip().lower() if self._lower_case else s.strip() for s in sentences]

        # Batch similar lengths together (as sentence-transformers does) so short
        # texts are not padded to the longest one in the corpus.
        order = np.argsort([-len(s) for s in sentences], kind="stable")
        out: list = [None] * len(sentences)
        for i in range(0, len(sentences), batch_size):
            idx = order[i : i + batch_size]
            encs = self._tokenizer.encode_batch([sentences[j] for j in idx])
            ids = np.array([e.ids for e in encs], dtype=np.int64)
            mask = np.array([e.attention_mask for e in encs], dtype=np.int64)
            inputs: dict[str, np.ndarray] = {"input_ids": ids, "attention_mask": mask}
            if "token_type_ids" in self._input_names:
                inputs["token_type_ids"] = np.array([e.type_ids for e in encs], dtype=np.int64)

            token_embeddings: np.ndarray = self._session.run(None, inputs)[0]

            attn = mask.astype(np.float32)[:, :, np.newaxis]
            pooled = (token_embeddings * attn).sum(axis=1) / np.clip(attn.sum(axis=1), 1e-9, None)
            if normalize_embeddings:
                pooled /= np.clip(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-9, None)
            for row, j in enumerate(idx):
                out[j] = pooled[row]

        return np.vstack(out).astype(np.float32)


# ── Public API ─────────────────────────────────────────────────────────────────

def _load(name: str) -> _Embedder:
    model_dir = onnx_model_dir(name)
    if os.path.exists(os.path.join(model_dir, "model.onnx")):
        try:
            embedder = _Embedder(_OnnxEmbedder.from_dir(model_dir), name)
            logger.info("[Embedder] ONNX runtime active for %s.", name)
            return embedder
        except Exception as exc:
            logger.warning("[Embedder] ONNX init failed for %s (%s) — falling back to PyTorch.", name, exc)

    if name == ONNX_MODEL and os.path.exists(_ONNX_PATH):
        try:
            from tokenizers import Tokenizer
            tokenizer = Tokenizer.from_pretrained(ONNX_MODEL)
            tokenizer.enable_padding(pad_id=tokenizer.token_to_id("<pad>") or 0, pad_token="<pad>")
            embedder = _Embedder(_OnnxEmbedder(_ONNX_PATH, tokenizer, 128), name)
            logger.info("[Embedder] ONNX INT8 active for %s.", name)
            return embedder
        except Exception as exc:
            logger.warning("[Embedder] ONNX init failed (%s) — falling back to PyTorch.", exc)

    try:
        from sentence_transformers import SentenceTransformer
        logger.info("[Embedder] Loading %s via sentence-transformers "
                    "(run scripts/download_model.py to use ONNX and skip PyTorch).", name)
        return _Embedder(SentenceTransformer(name), name)
    except Exception as exc:
        logger.error("[Embedder] Could not load %s: %s", name, exc)
        raise RuntimeError(f"No embedding model available for {name}: {exc}") from exc


def get_embedder(role: str = "chat") -> _Embedder:
    """Lazily loaded embedder for `role` ("chat" | "catalog"); thread-safe."""
    name = model_name(role)
    if name not in _instances:
        with _load_lock:                    # startup warm-up loads from a worker thread
            if name not in _instances:
                _instances[name] = _load(name)
    return _instances[name]


def is_embedder_ready(role: str = "chat") -> bool:
    """Non-blocking check — True only if the role's model is already loaded."""
    return model_name(role) in _instances


def encode_cached(role: str, texts: list[str], kind: str = "passage", batch_size: int = 64,
                  embedder=None) -> np.ndarray:
    """
    L2-normalised float32 embeddings of a fixed corpus, memoised on disk under
    ai/.cache/emb/ by model name + kind + the exact texts. A hit skips the
    encoding, so a restart — or a deploy whose build step pre-warmed the cache —
    does not re-embed the catalogue or the intent prototypes.

    `embedder` defaults to get_embedder(role). Anything other than that real
    singleton (e.g. a test stub) is used as-is and never read from or written
    to the cache.
    """
    name = model_name(role)
    if embedder is None:
        embedder = get_embedder(role)
    if embedder is not _instances.get(name):
        return np.asarray(embedder.encode(texts, kind=kind, batch_size=batch_size,
                                          normalize_embeddings=True, show_progress_bar=False), dtype="float32")
    onnx_file = os.path.join(onnx_model_dir(name), "model.onnx")
    # Backend tag: a different ONNX variant (e.g. a quantised one) must not reuse fp32 vectors.
    backend = f"onnx:{os.path.getsize(onnx_file)}" if os.path.exists(onnx_file) else "st"
    digest = hashlib.sha1("\x1f".join([name, backend, kind, *texts]).encode("utf-8")).hexdigest()
    path = os.path.join(_EMB_DIR, f"{digest}.npy")
    try:
        cached = np.load(path)
        if cached.shape[0] == len(texts):
            return cached
    except (OSError, ValueError):
        pass

    vecs = np.asarray(embedder.encode(
        texts, kind=kind, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=False,
    ), dtype="float32")
    try:
        os.makedirs(_EMB_DIR, exist_ok=True)
        tmp = os.path.join(_EMB_DIR, f"{digest}.{os.getpid()}.tmp.npy")
        np.save(tmp, vecs)
        os.replace(tmp, path)
    except OSError as exc:
        logger.warning("[Embedder] Could not write embedding cache %s: %s", path, exc)
    return vecs
