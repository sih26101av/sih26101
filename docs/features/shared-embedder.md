# Shared Embedder (chat + catalog roles)

Embedding models for the backend, one per role, loaded once per process and shared
by every caller. Production runs them on ONNX Runtime; PyTorch is not installed.

## Code

- `main-lms-backend/ai/embedder.py`
  - Roles → models (override with `CHAT_EMBEDDER_MODEL` / `CATALOG_EMBEDDER_MODEL`):
    - `"chat"` → `intfloat/multilingual-e5-small` (Gyan intents, 8 Indian languages
      + English; E5 `query: ` / `passage: ` prefixes added by `_Embedder`).
    - `"catalog"` → `sentence-transformers/all-MiniLM-L6-v2` (English course search).
  - `get_embedder(role)` — lazy singleton per model name, guarded by a lock
    (warm-up loads from a worker thread). Backends, in order:
    1. `_OnnxEmbedder.from_dir(ai/.cache/onnx/<org>__<model>/)` — the model's own
       fp32 `onnx/model.onnx` from the HF Hub + `tokenizers` (Rust) tokenizer.
       Copies sentence-transformers: `.strip()` (+ lower-case if configured),
       truncation at `sentence_bert_config.max_seq_length` (512 e5 / 256 MiniLM),
       attention-masked mean pooling, optional L2 norm, length-sorted batches.
       Verified equal to sentence-transformers to ~1e-7, and
       `scripts/eval_intents.py` gives identical results on both.
    2. Legacy `ai/.cache/model_int8.onnx` (only for
       `paraphrase-multilingual-MiniLM-L12-v2`, from `scripts/quantize_model.py`).
    3. `SentenceTransformer(name)` — needs `requirements-dev.txt` (PyTorch).
    Raises `RuntimeError` if none is available.
  - `encode_cached(role, texts, kind, embedder=None)` — L2-normalised embeddings of a fixed
    corpus memoised as `ai/.cache/emb/<sha1>.npy`. The key covers model name,
    backend (ONNX file size or `st`), kind and the exact texts, so any text or
    model change is a cache miss. Used for the intent prototypes
    (`semantic_engine._ensure_prototypes`), the course corpus and the crosswalk
    anchors (`HybridRecommendationEngine.__init__`). Callers pass their
    `get_embedder(...)` result so test stubs (`tests/test_pathway.py` patches
    `recommendation_service.get_embedder`) still apply; a non-singleton embedder
    bypasses the cache entirely.
  - `is_embedder_ready(role)` — non-blocking; True once loaded.
  - Env: `EMBEDDER_CACHE_DIR` (default `ai/.cache`), `EMBEDDER_THREADS`
    (ONNX intra-op threads, default `min(4, cpu_count)`).
- `main-lms-backend/scripts/download_model.py` — **deploy build step**. Downloads
  both roles' ONNX export + `tokenizer.json`, `special_tokens_map.json`,
  `sentence_bert_config.json`, `1_Pooling/config.json` (≈ 450 MB + 86 MB), then
  pre-warms `ai/.cache/emb/` from the on-disk catalogue (`--no-warm` skips it).
  `EMBEDDER_ONNX_FILE` picks another export (e.g. a quantised one) and `HF_TOKEN`
  is optional.
- `main-lms-backend/scripts/quantize_model.py` — legacy INT8 export (dev-only).
- `main-lms-backend/requirements-dev.txt` — adds `sentence-transformers` and
  `optimum` on top of `requirements.txt`.

## In / out

- In: `list[str]` (or a single string), `kind="query" | "passage"`.
- Out: `np.ndarray` float32, shape `(n, 384)`. Every caller passes
  `normalize_embeddings=True`.

## Connections

`ai/semantic_engine.py` encodes intent prototypes (cached) and each incoming query;
`services/recommendation_service.py` encodes the course corpus and crosswalk
anchors (cached) at warm-up, and each FRAC query at request time. Both load during
`main._warm_up` (background thread, after the port is bound). Changing a role's
model changes that feature only.

## TODOs / edge cases

- Without `ai/.cache/onnx/` (build step not run) the server falls back to
  sentence-transformers. That needs `requirements-dev.txt` and is slow (PyTorch
  import ~15 s). Without it, `get_embedder` raises and chat and recommendations
  degrade.
- `ai/.cache/emb/` never evicts: stale `.npy` files pile up when catalogue text
  changes. They are small (≤ 3.3 MB each) and safe to delete at any time.
- The fp32 e5 export is ~450 MB resident. A quantised export
  (`EMBEDDER_ONNX_FILE=onnx/model_qint8_avx512_vnni.onnx`) cuts that ~4× but shifts
  scores. Re-run `scripts/eval_intents.py` and re-check `_LOW_CONFIDENCE` first.
- Catalog text is truncated at 256 tokens (MiniLM `max_seq_length`), so long
  descriptions are cut off.
