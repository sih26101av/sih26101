# RAG Document → Quiz Generator & Grading (Assessment Studio)

Upload a training document (PDF/PPTX/TXT) and pick a difficulty. The backend generates 5 MCQs,
and every one of them is traceable to a quote in the document and confirmed by a second AI model.
The learner takes the quiz, gets a per-question review with the source quote, and a passing score
is recorded as competency evidence.

## Code

### `main-lms-backend/ai/quiz/` — generation pipeline (no vendor SDKs; httpx + stdlib + numpy)

- `pipeline.py` — `build_quiz(text, chunks, n=5, difficulty, seed=None, providers=None, use_cache=True)`
  → `QuizResult(questions: list[Candidate], meta)`; raises `QuizBuildError` when fewer than 3
  verified questions survive. Steps:
  1. `select_passages` picks up to `n+3` passages, labelled `P1..Pk`.
  2. `_pick_roles` chooses the generator (the first available provider) and the checker (the first
     available provider of a **different family**).
  3. The generator is asked for `n+3` questions, each with `source_id`, a verbatim `evidence`
     quote, `bloom_level` and `explanation`.
  4. `verifier.gate` and `verifier.dedupe` filter the candidates.
  5. `_cross_check` runs one batched blind call on the checker. It lists every defensible option,
     and a question is kept only if exactly the key is defensible.
  6. One repair round regenerates the missing count.
  7. `offline.build_offline` fills any remaining gap.
  8. `_choose` balances passage coverage against the bloom mix for the difficulty.
  9. `_balance_positions` shuffles the options so correct answers are spread over A–D.
  10. The result is cached (LRU, 64 entries) by `sha256(difficulty|n|text)`, so re-uploading the
      same document makes no API calls.
- `passages.py` — `clean_passage` drops page markers, table-of-contents lines and bibliography lines.
  `informativeness` scores a chunk by sentences, definition cues, figures and acronyms.
  `select_passages` runs MMR (λ 0.65) over `get_embedder("catalog")` vectors and keeps the
  `Page N`/`Slide N` location.
- `providers.py`:
  - `GroqProvider` (one instance per model in `GROQ_MODELS`) and `GeminiProvider` both call REST in
    JSON mode.
  - `GROQ_API_KEYS` holds comma-separated keys. They rotate, and each key cools down per
    `retry-after` on 429/413. 401/403 disables a key.
  - Groq rate limits are per key **and** per model, so every model has its own budget.
  - `configured_providers()` is cached for the process lifetime, so cooldowns persist across
    requests.
- `prompts.py` — `generation_prompt` (difficulty rubric, grounding rules, no synonym distractors,
  no length giveaways) and `check_prompt`/`CHECK_SYSTEM` (the blind checker marks every defensible
  option).
- `verifier.py` — `Candidate`, `coerce` (alias keys, letter answers, "the passage" → "the document")
  and `gate`, which returns rejection reasons:

  | Group | Reasons |
  |---|---|
  | Structure | `bad_options`, `duplicate_options`, `banned_option` ("all/none of the above"), `meta_question`, `answer_length_giveaway` |
  | Grounding | `evidence_not_in_source` (fuzzy coverage ≥ 0.85; a mis-cited passage is repaired), `number_not_in_source`, `answer_not_in_source`, `wrong_key`, `stem_number_not_in_source` |
  | Leakage | `answer_in_stem` |

  Grounding and leakage checks run only for recall/understand questions; apply/analyse questions
  (calculations, scenarios) rely on the cross-check. `dedupe` drops pairs with cosine > 0.85.
- `offline.py` — key-free last resort. It builds cloze and definition questions from document
  sentences. Distractors are same-type terms from the document (concepts, names, acronyms, years,
  percentages) ranked by similarity: far for Easy, nearest for Hard.
- `textutil.py` — normalisation, quote coverage, sentence splitting (headings kept separate),
  page/slide location lookup, and `vectorize` (the embedder, with a TF-IDF fallback).

### `main-lms-backend/routers/rag.py` (mounted at `/api/v1/rag`)

- Extraction: `_extract_pdf` (pdfplumber → pypdf), `_extract_pptx` (python-pptx incl. tables and
  notes → raw XML), `_extract_txt`. `_chunk_document_text` splits into 1000-char chunks with
  150-char overlap.
- `_generate_mcqs_from_text(text, chunks, difficulty, num_questions)` wraps `build_quiz` and maps
  `QuizBuildError` to 422. Returns `(QuizQuestion[], generation_meta)`.
- `POST /upload` — multipart `file` + `difficulty` (`Easy|Medium|Hard`, default Medium).
  - Stores the full `QuizQuestion` (key, explanation, evidence, source, bloom_level) in `QUIZ_STORE`.
  - Returns `PublicQuizQuestion` only (`question`, `options`, `bloom_level`), so the **answer key is
    never sent before grading**.
  - Also returns `generation`: `{difficulty, generator, checker, verification, passages_used,
    llm_questions, offline_questions, rejected{reason:count}, provider_errors, api_calls, seconds,
    cached}`.
  - `verification` is one of `cross-model | same-family | self | gate-only | offline`.
  - **No auth dependency.**
- `POST /grade` — JWT required; the user comes from `current_user.username`.
  - Scores the answers (pass ≥ 70%) and returns `review[]`: `{question, options, your_answer,
    correct_answer, is_correct, explanation, evidence, source}`.
  - `QuizAttempt` is unique on `userId + quizId`.
  - On the first pass it writes an `EvidenceLog` row with type `PRACTICE_ASSESSMENT` and
    `grantedValue = clamp(2.5 + (score-70)/30 * 1.5, 2.5, 4.0)`.
  - A resubmission reports "Evidence already recorded" (via `already_recorded`).
- `_update_internal_db_competency` — legacy `db_updated` path, plus a POST to
  `IGOT_COMPETENCIES_UPDATE_URL`.

### Frontend

- `src/services/api.ts` — `gradeRagQuiz(quizId, answers)` makes an authenticated `lmsFetch`
  (JWT + 401 refresh). It also defines the `QuizGradeResult` and `QuizQuestionReview` types.
- `src/pages/AssessmentPage.tsx` (`/assessment`):
  - Sends `difficulty` on upload.
  - Shows a verification badge (`VERIFICATION_LABEL[generation.verification]`) and a bloom-level
    chip per question.
  - After grading, shows an **Answer review**: the correct answer and your answer, the explanation,
    and the quoted evidence with its page or slide.
- `src/components/dashboard/AssessmentUploadZone.tsx` grades through `gradeRagQuiz`. Its `userId`
  prop is deprecated.

## Config (`main-lms-backend/.env`)

| Variable | Meaning |
|---|---|
| `GROQ_API_KEYS` | Comma-separated Groq keys (`GROQ_API_KEY` also accepted) |
| `GROQ_MODELS` | Preference order, default `openai/gpt-oss-120b,qwen/qwen3.8-27b,openai/gpt-oss-20b`. The first model generates; the first of another family checks |
| `GEMINI_API_KEY`, `GEMINI_MODEL` | Optional extra family (default `gemini-2.5-flash`). Placeholder or invalid keys are ignored or disabled |

With no keys at all, the offline engine is used, with `verification: "offline"`.

## Testing & evaluation

- `tests/test_quiz_verifier.py` checks that handcrafted hallucinated or malformed questions are
  rejected and good ones pass. It also covers passage selection (TOC/references skipped, page
  labels).
- `tests/test_quiz_pipeline.py` uses scripted `FakeProvider`s from `tests/quiz_fakes.py`, so it
  needs no network. It covers:
  - the gate and the cross-check dropping questions, and repair topping the quiz back up
  - a 429 failing over to another family, self-check, gate-only and offline modes
  - balanced answer positions, the Hard bloom mix, and the cache
  - offline grounding on every fixture
  - `/upload` hiding the key and honouring difficulty, and `/grade` returning a review
- `python scripts/eval_quiz.py [--difficulty all] [--offline] [--doc file.pdf] [--json out.json]`
  runs the **live** pipeline on `tests/data/quiz_docs/*.txt` and prints every question with its
  evidence, the bloom mix, answer positions, rejections, API calls and latency.
- Measured live results (2026-09-18, 7 fixtures):
  - Every kept question passed both checks.
  - Hard produced scenario and calculation questions.
  - Typical run: about 9–16 s and 2 API calls per quiz.
  - The cross-check rejected about 1 in 8 candidates (wrong key or ambiguous).

## Connections

A passed quiz's `PRACTICE_ASSESSMENT` evidence row is read by `BaselineAssembler`. That raises the
baseline and shrinks the gap shown on the dashboard (see `skill-gap-analysis.md`).

## TODOs / edge cases

- `QUIZ_STORE` and the quiz cache are in-memory: quizzes vanish on restart and are not shared
  across workers.
- Groq free tier allows about 8k tokens/minute per key per model. A quiz uses about 6k on the
  generator, so back-to-back uploads rotate keys and then fail over to the next model family. This
  is visible in `generation.provider_errors`.
- GPT-OSS models as *checkers* follow "passage only" literally and miss synonym distractors, which
  Qwen catches. They only check when Qwen is the generator (failover).
- Bloom labels come from the generator and are sometimes generous (a recall question tagged
  "apply").
- `competency_id` is hardcoded to `"FRAC-STAT-001"`, so evidence falls back to find-or-create by
  detected skill name.
- `/upload` is unauthenticated and spends API quota, which is an abuse risk.
- Legacy `.ppt` binaries are rejected. Scanned PDFs without OCR return 422.
- The offline engine only produces recall questions and needs definitional or named-term
  sentences. Very thin documents return 422.
- Karma is **not** awarded automatically on a pass.
