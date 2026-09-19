# Ollama RAG Knowledge Base (Tier 3 — disconnected)

A fully local RAG pipeline (Ollama LLM + ChromaDB) kept in the tree but **not in any
hot path**. The chatbot's Tier 3 is commented out; only the health and ingest
endpoints remain reachable.

## Code

- `main-lms-backend/ai/vector_store.py` — ChromaDB persistent store at
  `CHROMA_DB_DIR` (default `./chroma_db`), embeddings via Ollama `nomic-embed-text`.
  `_get_embeddings`, `get_store`, `get_retriever(k=4)`, `get_store_stats`,
  `add_documents_from_file(path)`, `add_text_to_store(text, metadata)`.
  Chunking from `CHUNK_SIZE` / `CHUNK_OVERLAP`.
- `main-lms-backend/ai/rag_engine.py` — `is_ollama_available()`,
  `build_system_prompt(...)` (injects role, department, skill gaps, recommendations,
  language hint), `generate_chat_response(...)` against `OLLAMA_MODEL`
  (default `llama3.2:3b`, temperature `OLLAMA_TEMPERATURE`).
- `main-lms-backend/ai/seed_knowledge.py` — `seed()` loads curated MoSPI/iGOT/FRAC
  content into Chroma. Run with `python -m ai.seed_knowledge`.
- `main-lms-backend/routers/ai_tools.py` (mounted at `/api/v1/ai`)
  - `GET /health` → `{ollama_status, ollama_model, ollama_url, chromadb_status,
    chromadb_chunks, chromadb_path, embed_model}`.
  - `POST /upload-knowledge` → PDF only, embeds into Chroma, returns
    `{status, filename, chunks_indexed, message}`. Temp files under `./temp_uploads`.
- Revert switch: `routers/chatbot.py`, search `REVERT_OLLAMA` — uncomment the Tier 3
  block and disable Tier 1 to route chat through this pipeline.

## In / out

- In: PDF uploads, or seeded text; chat queries if re-enabled.
- Out: indexed chunk counts, health status; generated replies when re-enabled.

## Connections

Separate from `ai/embedder.py` — this path uses Ollama's `nomic-embed-text`, not the
shared ONNX model. (`document_extractor.py` no longer uses Ollama — it uses Gemini,
or OCR + the shared e5 embedder.)

## TODOs / edge cases

- Dead code by design: nothing in production calls `generate_chat_response`.
- Requires a local Ollama install plus two pulled models (~2.3 GB) — not viable on
  the deployment target, which is why Tier 1 became the default.
- `chroma_db/` and `temp_uploads/` are gitignored; each dev must seed locally.
- `ai_tools.py` imports private module attributes (`_OLLAMA_MODEL`, `_EMBED_MODEL`).
- Both endpoints are unauthenticated.
- If the chatbot's Tier 3 is ever re-enabled, note that the live Tier-1 path also
  handles navigation actions — those would need re-implementing.
