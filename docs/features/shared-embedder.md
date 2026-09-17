# Shared Multilingual Embedder

One embedding model for the whole backend, used by both the chatbot's intent
classifier and the recommendation engine's FAISS index.

## Code

- `main-lms-backend/ai/embedder.py`
  - `MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"`
    (384-dim, 50+ languages — Devanagari queries land in the same vector space as
    the English catalog, so no translation API is needed).
  - `get_embedder()` — module singleton. Mode 1: ONNX INT8 from
    `ai/.cache/model_int8.onnx` (~115 MB, no PyTorch at runtime). Mode 2 fallback:
    `SentenceTransformer(MODEL_NAME)` (~470 MB). Raises `RuntimeError` if neither
    is available.
  - `_OnnxEmbedder` — HF `AutoTokenizer` + `onnxruntime.InferenceSession`
    (CPU, 2 inter/intra-op threads), attention-masked mean pooling + optional L2
    normalisation. `encode()` is API-compatible with `SentenceTransformer.encode`
    (`normalize_embeddings`, `batch_size`, `show_progress_bar` shim), max length 128.
  - `is_embedder_ready()` — non-blocking; True only once loaded.
- `main-lms-backend/scripts/download_model.py` — fetches the model/ONNX cache
  (intended as the deploy build step).
- `main-lms-backend/scripts/quantize_model.py` — produces `ai/.cache/model_int8.onnx`
  locally (needs `optimum[onnxruntime]` + `torch`, dev-only).

## In / out

- In: `list[str]` (or a single string).
- Out: `np.ndarray` float32, shape `(n, 384)`, L2-normalised by default.

## Connections

`ai/semantic_engine.py` encodes intent prototypes and each incoming query;
`services/recommendation_service.py` encodes the course corpus at startup and each
FRAC query at request time. Replacing the model changes both features at once.

## TODOs / edge cases

- `ai/.cache/` is not committed; without it the first startup silently downloads the
  ~470 MB PyTorch model, which is slow and memory-heavy.
- Truncation at 128 tokens means long course descriptions are cut off during indexing.
- Loading is lazy and not lock-protected — two concurrent first calls could both
  construct the model.
- `requirements.txt` pins `onnxruntime-cpu`; the package name differs across
  platforms and is a common install failure point.
- The return type hint on `get_embedder()` says `_OnnxEmbedder` even in the
  sentence-transformers fallback path.
