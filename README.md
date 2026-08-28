# 🇮🇳 MoSPI Skill Intelligence Platform
### Smart India Hackathon 2026 | Team Project

An **offline-first AI-powered learning platform** for Ministry of Statistics and Programme Implementation (MoSPI) officials. It analyses skill gaps against the iGOT Karmayogi FRAC framework, recommends personalised courses, generates AI quizzes from uploaded documents, and provides a multilingual AI learning assistant — **Gyan (ज्ञान)** — powered completely by a local LLM, with zero cloud dependency for chat.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              FRONTEND  (React + Vite, port 3000)        │
│  Learner Dashboard · Chat Widget · Quiz Engine           │
└─────────────────┬───────────────────────────────────────┘
                  │ REST API
┌─────────────────▼───────────────────────────────────────┐
│         MAIN LMS BACKEND  (FastAPI, port 8000)           │
│  Auth/JWT · Skill Gap Engine · Course Recommendations    │
│  ┌──────────────────┐   ┌────────────────────────────┐  │
│  │  Gyan AI Chat    │   │  RAG Quiz Generator         │  │
│  │  (Ollama local)  │   │  (Google Gemini API)        │  │
│  └────────┬─────────┘   └────────────────────────────┘  │
│           │                                              │
│  ┌────────▼──────────┐   ┌─────────────────────────┐    │
│  │ ChromaDB          │   │ Ollama Local LLM         │    │
│  │ (Vector Store)    │   │ llama3.2:3b + nomic-emb  │    │
│  └───────────────────┘   └─────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│         MOCK iGOT SERVER  (FastAPI, port 8001)           │
│  Sunbird-compliant mock of the real iGOT Karmayogi API   │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start (First-Time Setup)

> **Prerequisites:** Python 3.10+, Node.js 18+, Git

### Step 1 — Clone the repo
```bash
git clone https://github.com/your-org/sih26101.git
cd sih26101
```

---

### Step 2 — Install Ollama (Local AI Runtime)

Ollama runs the LLM and embedding model entirely on your machine — no internet needed after download.

| OS | Command |
|---|---|
| **Windows** | `winget install Ollama.Ollama` |
| **macOS** | `brew install ollama` |
| **Linux** | `curl -fsSL https://ollama.com/install.sh \| sh` |

After installation, **pull the two required models** (~2.3 GB total, one-time):
```bash
ollama pull llama3.2:3b        # Chat LLM (~2 GB)  — powers Gyan AI chat
ollama pull nomic-embed-text   # Embedding model (~274 MB) — powers ChromaDB search
```

> **Note:** Ollama must be running (`ollama serve` or it auto-starts on Windows) before the backend starts.

---

### Step 3 — Backend Setup

```bash
cd main-lms-backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

# Install Python dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env         # Windows
# cp .env.example .env         # Mac/Linux
# Then open .env and add your GEMINI_API_KEY
```

**Get a free Gemini API key** (needed for quiz generation only):
👉 https://aistudio.google.com/app/apikey

---

### Step 4 — Seed the AI Knowledge Base (first time only)

This embeds MoSPI/iGOT domain knowledge into the local ChromaDB vector store so Gyan can answer domain questions immediately.

```bash
# Make sure Ollama is running, then:
python -m ai.seed_knowledge
```

Expected output:
```
INFO | Starting baseline knowledge seeding...
INFO | ✓ Seeded 'iGOT_FRAC_Framework' → 7 chunks
INFO | ✓ Seeded 'National_Accounts_GDP_SNA2008' → 8 chunks
...
INFO | Total chunks in DB : 46
```

> ✅ You only need to do this **once**. The `chroma_db/` folder is gitignored — every team member runs this step independently.

---

### Step 5 — Start All Three Services

Open **three terminal windows**:

**Terminal 1 — Mock iGOT Server:**
```bash
cd mock-igot-server
pip install -r requirements.txt
uvicorn mock_igot_server:app --reload --port 8001
```

**Terminal 2 — Main LMS Backend:**
```bash
cd main-lms-backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

**Terminal 3 — Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Then open: **http://localhost:3000**

---

### Step 6 — Verify Everything is Working

| Check | URL | Expected |
|---|---|---|
| Frontend | http://localhost:3000 | Login page loads |
| Backend docs | http://localhost:8000/docs | Swagger UI |
| AI health | http://localhost:8000/api/v1/ai/health | `"ollama_status": "connected"` |
| Chat mode | http://localhost:8000/api/v1/chat/mode | `"engine": "rag_ollama"` |
| Mock iGOT | http://localhost:8001/docs | Swagger UI |

**Test login credentials:**
| Role | Email | Password |
|---|---|---|
| Learner | `test@mospi.gov.in` | `password123` |
| Admin | `admin@mospi.gov.in` | `admin123` |

---

## 🤖 Gyan AI Chat — How It Works

Gyan uses a **two-tier response engine**:

```
User message
     │
     ├─► Tier 1: Ollama RAG (if Ollama is running)
     │     ├─ Retrieves top-4 relevant chunks from ChromaDB
     │     ├─ Injects user role + skill gaps + recommendations as context
     │     └─ Generates reasoned, document-grounded answer (llama3.2:3b)
     │
     └─► Tier 2: Template engine (automatic fallback if Ollama is offline)
           - Intent-matching + pre-written bilingual responses
           - The demo always works even without Ollama
```

**Check which mode is active:**
```bash
curl http://localhost:8000/api/v1/chat/mode
```

**Add your own documents to Gyan's knowledge base:**
```bash
# Via API (PDF only):
curl -X POST http://localhost:8000/api/v1/ai/upload-knowledge \
     -F "file=@your_document.pdf"

# Or use the frontend upload panel
```

---

## 📁 Project Structure

```
sih26101/
├── frontend/                  # React + Vite + TypeScript + TailwindCSS
│   └── src/
│       ├── components/        # Dashboard, ChatWidget, QuizEngine, etc.
│       ├── pages/             # LearnerDashboard, AdminDashboard, Login
│       └── services/          # chatApi.ts, learnerApi.ts
│
├── main-lms-backend/          # FastAPI backend (port 8000)
│   ├── ai/
│   │   ├── vector_store.py    # ChromaDB manager
│   │   ├── rag_engine.py      # Ollama LLM + LangChain RAG chain
│   │   └── seed_knowledge.py  # One-shot knowledge base seeder
│   ├── routers/
│   │   ├── chatbot.py         # Gyan AI chat endpoint (/api/v1/chat)
│   │   ├── rag.py             # Quiz generation endpoint (Gemini API)
│   │   └── ai_tools.py        # Health check + knowledge upload
│   ├── auth/                  # JWT authentication
│   ├── models/                # SQLAlchemy + domain models
│   ├── .env.example           # ← Copy to .env and fill in values
│   └── requirements.txt
│
├── mock-igot-server/          # Sunbird-compliant iGOT mock (port 8001)
│   └── mock_igot_server.py
│
└── README.md
```

---

## 🔑 Environment Variables

Copy `main-lms-backend/.env.example` to `main-lms-backend/.env`:

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | ✅ Yes | For quiz MCQ generation. Free at [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| `OLLAMA_MODEL` | Optional | Default: `llama3.2:3b`. Use `phi3` for better quality on GPU |
| `OLLAMA_BASE_URL` | Optional | Default: `http://localhost:11434` |
| `IGOT_MOCK_BASE_URL` | Optional | Default: `http://localhost:8001` |

---

## 🧠 AI Models Required

| Model | Purpose | Size | Command |
|---|---|---|---|
| `llama3.2:3b` | Powers Gyan chat (LLM) | ~2 GB | `ollama pull llama3.2:3b` |
| `nomic-embed-text` | Powers ChromaDB search | ~274 MB | `ollama pull nomic-embed-text` |

> **GPU not required** — both models run on CPU. On a typical laptop (8 GB RAM), response time is ~5-15 seconds.

**Alternative models** (better quality, need more RAM):
```bash
ollama pull phi3          # Microsoft Phi-3 — sharper reasoning (~2.3 GB)
ollama pull llama3:8b     # Full Llama 3 — best quality (~4.7 GB, needs 8 GB+ RAM)
```
Then update `OLLAMA_MODEL=phi3` in `.env`.

---

## 🛠️ API Reference

| Endpoint | Method | Description |
|---|---|---|
| `POST /auth/register` | — | Register a new user |
| `POST /auth/login` | — | Get JWT access token |
| `GET /api/v1/learner/{id}/skill-gaps` | 🔒 Auth | Skill gap analysis |
| `GET /api/v1/learner/{id}/recommendations` | 🔒 Auth | Course recommendations |
| `POST /api/v1/chat` | 🔒 Auth | **Gyan AI chat** |
| `GET /api/v1/chat/mode` | Public | Check AI engine status |
| `GET /api/v1/ai/health` | Public | Ollama + ChromaDB status |
| `POST /api/v1/ai/upload-knowledge` | Public | Add PDF to knowledge base |
| `POST /api/v1/rag/upload` | 🔒 Auth | Upload doc → generate quiz |
| `POST /api/v1/rag/grade` | 🔒 Auth | Grade quiz + sync competency |

Full interactive docs: **http://localhost:8000/docs**

---

## ⚠️ Troubleshooting

**`ollama` not found after install (Windows)**
```bash
# Restart your terminal, or manually add to PATH:
$env:PATH += ";$env:LOCALAPPDATA\Programs\Ollama"
```

**`chromadb` import error**
```bash
pip install --upgrade chromadb langchain-chroma
```

**Gyan responds in template mode (slow/pre-written answers)**
- Check Ollama is running: `ollama list` should show `llama3.2:3b`
- Check: `curl http://localhost:11434/api/tags`
- Restart Ollama, then restart the backend

**Backend crashes on startup**
- Ensure `.env` exists (copy from `.env.example`)
- Ensure the mock iGOT server is running on port 8001

---

## 👥 Team

| Name | Role |
|---|---|
| Archit Shukla | Backend · AI Pipeline · RAG · Auth |

---

*Built for Smart India Hackathon 2026 | MoSPI Problem Statement*