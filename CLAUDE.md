# CLAUDE.md — index & router

AI skill-intelligence LMS for MoSPI (SIH 2026): FastAPI backend + React/Vite frontend
+ a Sunbird-shaped mock iGOT Karmayogi server, computing evidence-based competency
baselines, skill gaps, course recommendations, AI quizzes and a bilingual assistant.

## How to use these docs

**Before working on a feature, read its `docs/features/*.md` file instead of scanning
the full codebase. Only read source files directly when the docs are insufficient or
out of date.** If you find a doc is stale, update it in the same change.

System design, folder map, data flow and the mermaid-vs-code mismatches:
→ **[ARCHITECTURE.md](ARCHITECTURE.md)** (intended design lives in
`mospi-competency-platform.mermaid`; ARCHITECTURE.md §7 lists where code diverges).

## Feature index

| Feature | Docs |
|---|---|
| Auth, JWT, RBAC, seeding | [docs/features/auth-and-rbac.md](docs/features/auth-and-rbac.md) |
| Skill gap analysis (6-term baseline formula) | [docs/features/skill-gap-analysis.md](docs/features/skill-gap-analysis.md) |
| AI course recommendations (FAISS + BM25 + RRF) | [docs/features/recommendation-engine.md](docs/features/recommendation-engine.md) |
| RAG document → quiz + grading → evidence | [docs/features/rag-quiz-generator.md](docs/features/rag-quiz-generator.md) |
| Video / audio / YouTube → evidence-cited quiz | [docs/features/media-quiz-generator.md](docs/features/media-quiz-generator.md) |
| Learning Mode (NotebookLM-style study chat) | [docs/features/learning-mode.md](docs/features/learning-mode.md) |
| Gyan chatbot (semantic + template tiers) | [docs/features/chatbot-gyan.md](docs/features/chatbot-gyan.md) |
| Karma points / gamification | [docs/features/karma-points.md](docs/features/karma-points.md) |
| Certificate → FRAC evidence extraction | [docs/features/certificate-evidence-extraction.md](docs/features/certificate-evidence-extraction.md) |
| Mock iGOT server + adapter | [docs/features/mock-igot-integration.md](docs/features/mock-igot-integration.md) |
| Learner dashboard (frontend shell) | [docs/features/learner-dashboard.md](docs/features/learner-dashboard.md) |
| Admin dashboard | [docs/features/admin-dashboard.md](docs/features/admin-dashboard.md) |
| SCIL v6 workforce insights (GSBPM scope, opportunity, admin foresight) | [docs/features/workforce-insights.md](docs/features/workforce-insights.md) |
| Shared multilingual embedder | [docs/features/shared-embedder.md](docs/features/shared-embedder.md) |
| Ollama/Chroma RAG (disconnected Tier 3) | [docs/features/ollama-knowledge-base.md](docs/features/ollama-knowledge-base.md) |

## Run commands

Start in this order — the backend and the seeder both depend on the mock server.

```bash
# 1) Mock iGOT server (port 8001)
cd mock-igot-server && uvicorn mock_igot_server:app --reload --port 8001

# 2) LMS backend (port 8000)
cd main-lms-backend && uvicorn main:app --reload --port 8000

# 3) Frontend (port 5173)
cd frontend && npm run dev
```

One-time / occasional:
```bash
cd main-lms-backend
python -m auth.seed              # seed users_auth from the mock server (idempotent)
python scripts/download_model.py # ONNX embedders + embedding cache into ai/.cache/ (also the deploy build step)
python -m ai.seed_knowledge      # optional: seed ChromaDB (needs local Ollama)
```

## Conventions

- **Identity:** the iGOT userId (`usr_XXXXXXXXX`) is the canonical user key — it is the
  auth username, the JWT subject, and the `userId` on `EvidenceLog`, `QuizAttempt` and
  karma rows. It is *not* `users.uuid`. Never take a user id from a request body;
  derive it from `current_user.username`.
- **Layering:** the browser talks only to port 8000; port 8001 is reached through
  `MockIgotAdapter` or an admin-guarded proxy. Add new external calls behind the adapter.
- **Env:** backend config lives in `main-lms-backend/.env` (see `.env.example`).
  `.env*` is gitignored except the example. The frontend reads its backend origin
  from `VITE_API_BASE_URL` via `frontend/src/config.ts` (default `http://localhost:8000`)
  — never hardcode a URL elsewhere.
- **Deploy:** backend + mock server on an Oracle Cloud VM (systemd + Caddy HTTPS,
  files and steps in `deploy/oracle/`), frontend on Vercel (`frontend/vercel.json`).
  Cross-site auth needs `CORS_ORIGINS` and `COOKIE_SAMESITE=none` in the backend `.env`.
- **DB:** auth/evidence/karma live in shared Neon Postgres (`DATABASE_URL` in
  `main-lms-backend/.env`); `auth.db` is only the offline fallback.
- **Data:** `auth.db`, `chroma_db/`, `temp_uploads/`, `ai/.cache/` are generated and
  gitignored. Mock datasets under `mock-igot-server/` are committed fixtures — treat
  them as read-only unless the task is about data generation.
- **Ports:** 8001 mock, 8000 backend, 5173 frontend (CORS on the backend is pinned to
  3000/5173 plus `CORS_ORIGINS`, with credentials enabled — a wildcard origin breaks
  the refresh cookie).
- **Folders:** `node/`, `node-v20.17.0-win-x64/`, `node.zip` are a vendored Node runtime;
  ignore them. `main-lms-backend/main_backup.py`, `_*.txt`, `_h.py` and
  `mock-igot-server/main.py` are legacy leftovers — do not build on them.
- Backend HTTP uses `httpx`; prefer it over `requests` in new code.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
