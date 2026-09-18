# RAG Document → Quiz Generator & Grading

Upload a training document (PDF/PPT/PPTX/TXT), get 5 AI-generated MCQs, take the
quiz, and have a passing score recorded as competency evidence.

## Code

`main-lms-backend/routers/rag.py` (mounted at `/api/v1/rag`):

- Extraction — `_extract_pdf` (pdfplumber → pypdf fallback), `_extract_pptx`
  (python-pptx incl. tables + speaker notes → raw slide-XML fallback),
  `_extract_txt` (multi-encoding), `_clean_text`.
- `_chunk_document_text` — LangChain `RecursiveCharacterTextSplitter`
  (1000 chars, 150 overlap).
- `_detect_skill_name(text, filename)` — keyword heuristic mapping the document to
  a skill label (Machine Learning, National Accounts, Sample Surveys, …), default
  "General Statistics".
- `_generate_mcqs_from_text(text, chunks)` — Google Gemini (`google-generativeai`)
  with `response_mime_type: application/json`, temperature 0.3, model from
  `GEMINI_MODEL` with a hardcoded fallback list. Heavily defensive normalisation:
  strips code fences, accepts `questions[]`/list/single object, alternate key names,
  pads/truncates to exactly 4 options, coerces `correct_answer` from int/letter/string.
- `POST /upload` — validates extension (`SUPPORTED_EXTENSIONS`) and size
  (`MAX_FILE_SIZE_BYTES` = 25 MB), extracts, chunks, generates, stores the quiz in
  the module-level `QUIZ_STORE` under `QZ-XXXXXXXX`, returns questions + metadata.
  **No auth dependency.**
- `POST /grade` — requires JWT (`Depends(get_current_user)`); the user id is taken
  from `current_user.username`, never the body. Scores the answers (pass ≥ 70%),
  then in one transaction writes a `QuizAttempt` (unique on `userId + quizId`) and,
  on a **first** passing attempt, an `EvidenceLog` row with
  `evidenceType="PRACTICE_ASSESSMENT"` and
  `grantedValue = clamp(2.5 + (score-70)/30 * 1.5, 2.5, 4.0)`. Re-submissions are
  re-scored for UX but write no second evidence row.
- `_update_internal_db_competency` — legacy path kept for the `db_updated` response
  field: find-or-create `Competency`, upsert `CompetencyProfile`/`UserCompetency`
  (level +1, capped at 5), merge an `Assessment` audit row.
- After a pass it POSTs `{user_id, competency, new_level}` to
  `IGOT_COMPETENCIES_UPDATE_URL` (default `http://localhost:8001/competencies/update`);
  failures are swallowed into `synced_to_igot: false`.
- Schemas: `QuizQuestion`, `QuizPayload`, `DocumentMetadata`, `DocumentUploadResponse`,
  `GradeRequest`, `GradeResponse`, `ErrorResponse`.

Frontend:
- `src/components/dashboard/AssessmentUploadZone.tsx` — drop zone + inline quiz +
  result card on the learner dashboard; calls `onQuizPassed()` to trigger a refetch.
- `src/pages/AssessmentPage.tsx` — the full-page Assessment Studio at `/assessment`,
  built on the shared `AppShell`. Sections `new_quiz` / `history` / `settings`
  (`StudioTab`), plus the `status` machine `idle → loading → quiz → grading → result`.
  - `difficulty` (`Easy | Medium | Hard`) is now a real control posted to
    `/api/v1/rag/upload`; it used to be a dead toggle with `"Medium"` hardcoded.
  - History and the "Your Last Assessment" card read `fetchAchievements(userId)`
    filtered to `category === 'RAG Quiz'`, replacing four hardcoded sample rows and a
    mocked 85% result card. `loadHistory()` re-runs after grading.

## In / out

- In: multipart `file`; then `{quiz_id, answers: number[]}` + Bearer token.
- Out (upload): `{status, message, quiz_id, filename, file_type, questions[],
  metadata{character_count, word_count, chunk_count, page_count, slide_count, line_count}}`.
- Out (grade): `{status, user_id, quiz_id, score, passed, correct_count,
  total_questions, message, synced_to_igot, igot_response, db_updated, evidenceWritten}`.

## Connections

The `PRACTICE_ASSESSMENT` evidence row is read by `BaselineAssembler` through the
documented channel, so a passed quiz directly raises the baseline and shrinks the
gap shown on the dashboard (see `skill-gap-analysis.md`).

Video, audio and YouTube sources use a separate pipeline (`routers/media_quiz.py`,
see `media-quiz-generator.md`) that writes into this router's `QUIZ_STORE`, so
`/grade` handles those quizzes too.

## TODOs / edge cases

- **Known bug:** both frontend callers post to `/grade` without an `Authorization`
  header (and still send a `user_id` in the body), while the endpoint requires a
  JWT — grading will 401 unless the caller is fixed to use an authenticated fetch.
- `QUIZ_STORE` is in-memory: quizzes vanish on restart and are not shared across
  workers. `quiz_demo` is a hardcoded demo quiz.
- `competency_id` is hardcoded to `"FRAC-STAT-001"` on every generated quiz, so
  evidence usually falls back to find-or-create by detected skill name and rarely
  matches a real FRAC competency id.
- `/upload` is unauthenticated and calls a paid external API — rate/abuse exposure.
- The default `GEMINI_MODEL` in code (`gemini-3.5-flash-lite`) differs from
  `.env.example` (`gemini-1.5-flash`); verify a valid model id before demos.
- Legacy `.ppt` binaries are rejected; scanned PDFs without OCR return 422.
- Line 1100 of `rag.py` uses `'existing_attempt' in dir()`, which does not do what
  it looks like it does — the "evidence already recorded" message is unreliable.
- The first passing submission awards `ASSESSMENT_PASSED` karma server-side
  (`karma_engine.award_safe`, idempotent per quizId, subject to the daily cap);
  `GradeResponse.karmaAwarded` / `karmaNote` report it.
