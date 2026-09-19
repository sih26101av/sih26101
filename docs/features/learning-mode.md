# Learning Mode — NotebookLM-style study chat (AI Assessment Studio)

A second mode inside the Assessment Studio, next to quiz generation. The
learner uploads the same document types the quiz pipeline accepts (PDF,
DOCX, PPTX, TXT); instead of generating questions, the backend opens a
grounded Q&A chat over the document — every answer is retrieved from the
learner's own source text and (when the model supports it) cites the
locator it came from. Unlike Gyan, Learning Mode runs where `GEMINI_API_KEY`
is configured, so it can use a real LLM.

## Code

Backend, `main-lms-backend/routers/learning_mode.py` (mounted at
`/api/v1/rag/learning`):

- Reuses `routers/rag.py`'s extraction helpers (`_extract_pdf`, `_extract_pptx`,
  `_extract_txt`, `_clean_text`, `_chunk_document_text`, `SUPPORTED_EXTENSIONS`,
  `MAX_FILE_SIZE_BYTES`) and `services/doc_quiz/extract.extract_docx`, so a
  Learning Mode upload is parsed identically to a quiz upload (including
  scanned-PDF OCR).
- Reuses `services/doc_quiz/generate.locate_chunks` to give each chunk the
  same `"Page 4"` / `"Slide 2"` / `"Section 3: Price collection"` locators the
  quiz pipeline cites.
- `POST /start` (multipart `file`): extract → chunk (`_chunk_document_text`,
  evenly sampled down to `MAX_LEARNING_CHUNKS`=80 if the document is long) →
  locate → embed every chunk with the shared "chat" embedder
  (`ai/embedder.py`, `kind="passage"`) → ask Gemini for a JSON
  `{summary, topics[], suggested_questions[]}` overview. Stores the chunks and
  their embeddings in `LEARNING_STORE` under a `material_id`
  (`LM-XXXXXXXXXX`). If the embedder is unavailable, retrieval falls back to
  the first `MAX_RETRIEVED_CHUNKS` chunks unranked; if Gemini is unavailable,
  the overview falls back to a plain 400-character preview (the session still
  opens — only `/chat` hard-requires the key).
- `POST /chat` (JSON `{material_id, message, history}`): embeds the message
  (`kind="query"`), ranks the stored chunk vectors by cosine similarity, takes
  the top `MAX_RETRIEVED_CHUNKS`=5, and asks Gemini to answer using only that
  context, replying in the same language as the question. Citations are kept
  only if their `locator` matches one of the retrieved chunks (no
  hallucinated locators). Raises 500 without `GEMINI_API_KEY`, 502 if the LLM
  call fails, 404 for an unknown/expired `material_id`.
- `LEARNING_STORE` is in-memory, like `rag.QUIZ_STORE` — sessions are lost on
  restart and not shared across workers.
- **Timeouts.** `google.generativeai` has no request timeout of its own, so a
  rate-limited or stalled call used to leave the learner's spinner running
  indefinitely. The overview Gemini call is bounded by
  `LEARNING_OVERVIEW_TIMEOUT_S`=30 (falls back to the plain preview) and the
  chat call by `LEARNING_CHAT_TIMEOUT_S`=60 (504). The frontend
  (`learningApi.ts`) aborts `/start` after 120 s and `/chat` after 90 s with a
  readable error. That covers a hung `uvicorn --reload` worker, which accepts
  the connection and never answers. `/start` logs per-stage timings (extract /
  chunk / embed / overview) at INFO.
- Typical `/start` time is 3–5 s warm. The first call after a restart takes
  about 20 s more, because `_chunk_document_text` imports LangChain, which
  pulls in torch.

Frontend, `frontend/src/`:
- `services/learningApi.ts` — `startLearningSession(file)`,
  `sendLearningMessage(materialId, message, history)`, and the response
  types.
- `components/assessment/LearningChat.tsx` — the tab's whole UI: an upload
  zone when there's no session, then a chat panel (topic chips, message
  history with citation quotes, suggested-question chips shown until the
  learner's first message, an input bar).
- `pages/AssessmentPage.tsx` — a fourth sidebar tab, `"learning"`, next to
  `new_quiz` / `history` / `settings`. Holds `learningSession` /
  `learningLoading` / `learningError` state and passes them to `LearningChat`.

## Gyan hand-off (document → quiz or Learning Mode, no second upload)

Gyan (`docs/features/chatbot-gyan.md`) stays fully offline — it never reads an
attached file itself. It only forwards the file to the Studio, which already
has `GEMINI_API_KEY` wired up:

1. `components/dashboard/ChatWidget.tsx` gets a paperclip button next to the
   mic (`accept=".pdf,.docx,.pptx,.txt"`). Attaching a file shows a banner
   with two buttons, **"📝 Generate a quiz"** and **"📖 Help me study this"**,
   above the input bar (same slot pattern as the existing nav-confirmation
   banner).
2. If the learner instead types a message while a file is attached, a local
   regex (`QUIZ_INTENT_RE` / `LEARN_INTENT_RE` in `ChatWidget.tsx`) picks a
   mode from the wording (`quiz|test|assess|…` vs `learn|study|explain|…`);
   an ambiguous message falls through to the normal `/api/v1/chat` call and
   the banner stays up so the learner can pick explicitly.
3. Picking a mode calls `setPendingStudioUpload(file, mode)`
   (`services/pendingStudioUpload.ts` — a plain module singleton, since a
   `File` object can't survive `sessionStorage` or router `state` across a
   lazy-loaded route) and fires a `{type: "redirect", target: "/assessment"}`
   `navigate_action` through the existing `onNavigate` prop
   (`LearnerDashboard.tsx` already handles `"redirect"` by calling
   `navigate(action.target)`).
4. `AssessmentPage.tsx` calls `consumePendingStudioUpload()` once on mount.
   `mode: "quiz"` sets the file, guesses the matching upload-format chip
   (`guessUploadFormat`) and calls `handleGenerate(file)` directly (the
   function now takes an optional file override so it doesn't have to wait a
   render cycle for `file` state). `mode: "learn"` switches to the
   `"learning"` tab and calls `startLearning(file)`.

## In / out

- **In (`/start`):** multipart `file` (.pdf, .pptx, .docx, .txt; same 25 MB
  cap as `/rag/upload`).
- **Out (`/start`):**
  ```
  {status, material_id, filename, file_type,
   metadata{filename, file_type, character_count, word_count, chunk_count,
     page_count?, slide_count?, line_count?, section_count?, ocr?},
   summary, topics[], suggested_questions[]}
  ```
- **In (`/chat`):** `{material_id, message, history: [{role, content}]}`.
- **Out (`/chat`):** `{status, material_id, reply, citations: [{locator, quote}]}`.

## Connections

Shares its extraction and chunk-locating code with
`docs/features/rag-quiz-generator.md` (imports from `routers/rag.py` and
`services/doc_quiz/generate.py` directly — no duplication) and its retrieval
embedder with `docs/features/shared-embedder.md` / the media quiz's
`services/media_quiz/relevance.py` pattern (same "chat" role, same
query/passage `kind` convention). Reached from `docs/features/chatbot-gyan.md`
via the hand-off above; see `ARCHITECTURE.md`'s "Chat → Assessment Studio
hand-off" note.

## Verification

- `python -c "import main"` — the app still imports cleanly with the new
  router registered (`/api/v1/rag/learning/start`, `/api/v1/rag/learning/chat`
  appear in `app.routes`).
- `npx tsc --noEmit` — clean.
- Not yet run end-to-end against a live Gemini key in this change (no key
  configured in this environment); the extraction/chunking/retrieval path was
  verified by import and by re-reading the reused `rag.py` /
  `doc_quiz/generate.py` functions it calls unchanged.

## TODOs / edge cases

- **Unauthenticated**, like `/rag/upload` and `/rag/media/*` — same rate/abuse
  exposure the other docs already flag. No evidence/karma is written from
  Learning Mode; it's read-only study, not an assessment.
- `LEARNING_STORE` is in-memory and per-worker, like `QUIZ_STORE` — a session
  started on one uvicorn worker (or before a restart) 404s on another.
- The overview/chat prompts ask Gemini to answer only from the retrieved
  excerpts, but nothing enforces that server-side beyond the locator-match
  filter on citations — same trust level as the document quiz's fact-check
  (flags, doesn't reject).
- Retrieval always takes the top 5 chunks per question; there's no
  multi-turn re-retrieval or query rewriting, so a follow-up like "and the
  next one?" without restating the topic may retrieve the wrong chunks.
- The intent regex in `ChatWidget.tsx` is a simple keyword split, not the
  semantic classifier Gyan uses elsewhere — consistent with Gyan staying
  offline for this feature (classifying would need the file's content, which
  Gyan never reads).
- No i18n pass for the new Learning Mode UI strings or the attach banner
  (English only); Gyan's own reply stays fully localized since it never
  changes for this feature.
