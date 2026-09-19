# RAG Document → Quiz Generator & Grading (quiz ↔ skill gap)

Upload a training document (PDF, including scanned PDFs; PPTX; DOCX; TXT) and
choose a difficulty, a question count (3–20), the question types and the
language (English, Hindi, or bilingual). The service returns source-cited
objective questions:

- MCQ;
- True/False;
- multi-select;
- fill-in-the-blank;
- numeric (for statistics formulas).

Every question quotes the passage it was written from, and it passes the same
kind of validator and fact-check as the media pipeline. Every first attempt,
pass **or** fail, moves the learner's practice ability on the matching role
competency, and that ability feeds the skill-gap baseline.

The result screen shows the skill impact and next-step recommendations. Its
answer review explains *why each wrong answer is wrong*, shows the exact source
passage, and links a course for the missed point. Each item's difficulty comes
from how learners actually answer it once there is enough data; until then the
LLM's tag is used. Video, audio and YouTube quizzes grade through the same
`/grade` endpoint.

## Code

`main-lms-backend/routers/rag.py` (mounted at `/api/v1/rag`):

- **Extraction:**
  - `_pdf_text_layer`: pdfplumber, with pypdf as the fallback.
  - `_extract_pdf`: any page with fewer than `DOC_OCR_MIN_CHARS`=40 characters
    of text layer is treated as scanned and OCR'd (see `doc_quiz/extract.py`
    below). It returns `(text, page_count, ocr_report)`.
  - `_extract_pptx`: python-pptx, including tables and speaker notes; falls back
    to the raw slide XML.
  - `.docx`: `doc_quiz.extract.extract_docx`.
  - `_extract_txt`: tries several encodings.
  - `_clean_text`.
  - Legacy binary `.ppt` and `.doc` files return 400.
  - The extractors emit `--- Page N ---`, `--- Slide N ---` and
    `--- Section N: Heading ---` markers, which the citations use as locators.
- `_chunk_document_text`: LangChain `RecursiveCharacterTextSplitter` (1000
  chars, 150 overlap).
- `_detect_skill_name(text, filename)`: a keyword heuristic, now only a display
  fallback. Linking happens at grading.
- `_generate_questions(...)`:
  - calls `doc_quiz.generate.generate`;
  - maps "no Groq and no Gemini key" (`llm_configured()`) to 500, an LLM failure to 502, and "nothing survived
    validation" to 502 with `detail = {message, generation}`;
  - wraps the results as `QuizQuestion`;
  - runs `_with_calibration`, which stamps `item_key`, `llm_difficulty`,
    `calibration` and the effective `difficulty`.
- `POST /upload` takes multipart `file` plus the Form fields `difficulty`
  (default Medium), `num_questions` (default 5, clamped to 3–20),
  `question_types` (comma list; default all five) and `language`
  (`en` | `hi` | `bi`).
  - It validates the extension and the size (25 MB).
  - Extraction (OCR, DOCX) and chunking run in a worker thread.
  - It stores the quiz in `QUIZ_STORE` under `QZ-XXXXXXXX` with `difficulty`,
    `language`, `source_type: "document"`, the `generation` report and
    `competency_id: None`.
  - **It has no auth dependency.**
- `POST /grade` requires a JWT. The user id is `current_user.username`, never
  the request body. `answers[i]` can be an option index (mcq, true_false), a
  list of indices (multi_select), text (fill_blank) or a number or text
  (numeric). The steps:
  1. **Difficulty.** `_question_difficulties` re-reads the calibration at
     grading time, keyed by `item_key` with the generator's tag as the prior.
     Media quizzes go through the same calibration.
  2. **Score.** Each answer is scored by `doc_quiz.items.is_correct`. The plain
     % decides the pass (≥ 70 %). The difficulty-weighted % comes from
     `pa.weighted_score` (Easy 1, Medium 1.5, Hard 2).
  3. **Link.** `_competency_rows` reads the learner's resolved skill-gap rows
     through `app_state.competency_state`; these are the same rows
     `/skill-gaps` shows. `pa.link_competency` then picks one row, trying in
     order:
     - the quiz's FRAC tag;
     - e5 similarity (the "chat" embedder, floor 0.72);
     - keyword overlap.

     With no match, the evidence falls back to the quiz's tag or skill name, and
     it does not move a gap.
  4. **Record.** `_record_attempt` runs in a worker thread. On the **first**
     submission it writes one `QuizAttempt` and one `EvidenceLog`
     `PRACTICE_ASSESSMENT` row.
     - `grantedValue` is the updated practice ability θ.
     - The metadata carries the quiz id, title, difficulty, scores, θ before
       and after, `per_question`, `question_types` and the link.
     - After that, `calibration.record_responses` adds every item's response
       and the learner's θ *before* the quiz to `quiz_item_stats`.
     - Re-submissions are scored for display only and write nothing, neither
       evidence nor item statistics.
  5. **Refresh.** It calls `app_state.invalidate_user` and re-resolves the
     learner's state. `_row_snapshot` builds `skillImpact.before` and `after`.
  6. **First pass only:**
     - `ASSESSMENT_PASSED` karma;
     - the legacy `_update_internal_db_competency` write;
     - the iGOT sync, with `new_level` set to the resolved level.
  7. **Review.** `_build_review` returns one row per question, missed ones
     first, with:
     - `type`, `yourAnswer` and `correctAnswer` (as display text);
     - `feedback`: personalised, see below;
     - `explanation`, and `solution` for numeric questions;
     - `source`: `{locator, quote, passage}`;
     - `course`: from `pa.courses_for_topics`, for missed questions;
     - `calibration`, the fact-check `review`, and the Hindi `translation`.

     The `recommendations` field keeps the next difficulty, focus topics,
     competency courses and summary.
- `GET /attempts` (JWT): unchanged.
- `QuizQuestion`:
  - The original fields stay: `question`, `options`, `correct_answer`,
    `explanation` and `difficulty`.
  - `options` now defaults to `[]` and `correct_answer` to −1, so a media or
    demo question (with none of the new fields) is an `mcq`.
  - New fields:
    - `type`;
    - `correct_answers`;
    - `answer_text`, `accepted_answers`;
    - `numeric_answer`, `tolerance`, `unit`, `expression`, `solution`;
    - `why_wrong[]`;
    - `citations[]`;
    - `answer_type`;
    - `review`;
    - `llm_difficulty`, `calibration`, `item_key`;
    - `translations.hi`.

### Document question pipeline (`main-lms-backend/services/doc_quiz/`)

| File | Role |
|---|---|
| `extract.py` | `extract_docx`: python-docx, paragraphs **and** tables in body order; headings become `--- Section k: Title ---` markers; falls back to raw `word/document.xml`. `ocr_pdf_pages`: pypdfium2 renders each page (`DOC_OCR_SCALE`=2, about 144 dpi), in batches because pdfium is not thread-safe, and RapidOCR (the media pipeline's shared engine, `probe.get_ocr`) reads them in parallel. Lines are kept at score ≥ 0.5 and put in reading order. At most `DOC_OCR_MAX_PAGES`=40 pages are OCR'd. Raises `OcrUnavailable` without rapidocr (from `requirements-media.txt`). |
| `generate.py` | The pipeline (below). |
| `items.py` | Pure logic for each type: `is_correct`, `is_answered`, `answer_display`, `correct_display`, `feedback`, `item_key`, `safe_eval` (an AST whitelist: + − × ÷ ** %, parentheses, sqrt/log/exp/abs/round/min/max/sum/mean), `parse_number` (handles commas, %, fractions and Devanagari digits), and `numeric_tolerance` (1 % relative or 0.005 minimum; a generator tolerance is honoured only if it is ≤ 5 %). |
| `calibration.py` | `calibrate` (pure), `calibrate_items`, `load_stats` and `record_responses` on the `quiz_item_stats` table (`models.QuizItemStat`). |

`generate.generate(text, chunks, difficulty, n_questions, types, language)`:

1. **Chunks.**
   - `locate_chunks` gives each chunk an id (`c1…`) and a locator.
   - `DocChunk.locate(quote)` finds the page or section the quote is actually
     in, since a chunk can span two.
   - `select_chunks` keeps at most `MAX_CHUNKS`=24: one per equal slice of the
     document, taking the densest chunk (words plus figures). It drops chunks
     with fewer than 150 characters.
   - `numeric` is dropped, and the report says why, when the chosen chunks have
     fewer than 4 distinct figures.
2. **Generate.**
   - One LLM call (Groq, then Gemini) per group of 4 chunks, run concurrently, asking for about
     1.8× the requested count.
   - The prompt has per-type rules, the difficulty mix (`DIFFICULTY_MIX`,
     generalised from the old fixed 5-question mix) and plausibility rules for
     distractors.
   - Each question must cite its `chunk`, a VERBATIM `quote`, `why_wrong` for
     every wrong option, and an honest `difficulty`.
3. **Validate** (reasons are counted in `generation.rejected`):
   - **Common:**
     - the stem is at least 12 characters;
     - the question isn't about the document itself (`on page 3`, `the
       author`);
     - it doesn't mention internal ids (the media pipeline's `_INTERNAL_REF`);
     - `cited_unknown_chunk`, `no_quote_cited`;
     - `quote_not_in_source`: the quote must be a normalised substring of the
       chunk, or ≥ 85 % of its tokens must appear in it.
   - **mcq / multi_select:**
     - `bad_options`, `bad_answer_index` (multi-select needs 2 to n−1 correct);
     - `near_duplicate_options`: similarity ratio ≥ 0.9 with the same figures;
       "base year 2004" vs "2012" is allowed;
     - `catch_all_option` ("all/none of the above");
     - `answer_length_giveaway` (mcq): the answer is > 2.2× and ≥ 30 characters
       longer than every distractor;
     - `implausible_distractor_type`: the answer is a number but a distractor
       isn't;
     - `answer_number_not_in_source`: allowed only if the item's `expression`
       evaluates to that number.
   - **true_false:**
     - options fixed to True/False;
     - a true statement's figures must be in the source;
     - a false one needs an explanation that corrects it
       (`false_statement_without_correction`).
   - **fill_blank:**
     - exactly one blank;
     - the answer is ≤ 6 words, present in the source, and not already in the
       stem.
   - **numeric:**
     - `expression` must evaluate to the answer within tolerance
       (`expression_mismatch`);
     - its literal inputs must come from the stem or the source, plus small
       constants such as 1, 2 and 100 (`expression_inputs_not_in_source`);
     - without an expression, the answer must appear in the source
       (`numeric_answer_unverifiable`).
4. **Plausibility and dedup** (`plausibility_and_dedup`, worker thread):
   - Uses the multilingual-e5 "chat" embedder.
   - A distractor with cosine < 0.72 to the stem is `distractor_off_topic`.
   - A distractor with cosine ≥ 0.97 to a correct option is
     `distractor_paraphrases_answer`. Numeric-looking options are skipped.
   - `duplicate`: stem cosine ≥ 0.93, or the same fact (same chunk, same answer
     and Jaccard ≥ 0.35).
   - Without the embedder, dedup is lexical (Jaccard ≥ 0.6) and the report says
     `plausibility_check: "lexical"`.
5. **Select.**
   - Order of preference: type quotas (`type_quotas`: MCQ gets a double share),
     then difficulty quotas, then chunk spread, then generation order.
   - `shuffle_options` shuffles mcq and multi-select options deterministically
     and remaps `why_wrong`.
6. **Fact-check.** `media_quiz.fact_check.review_answer` runs on every chosen
   question. It is the same check as media and only flags, never rejects.
7. **Translate** (language `hi` or `bi`):
   - `media_quiz.fact_check.translate_texts` translates the question, the
     options, the explanation, the `why_wrong` texts, the fill-in answer, and
     the unit and solution.
   - Glossary terms are protected as ⟦Tn⟧.
   - True/False options become सही / गलत.
   - A Hindi fill-in whose blank got lost keeps the English stem.
   - The Hindi fill-in answer is also accepted when grading.

### Personalised feedback (`items.feedback`)

| Type | What the learner sees for a wrong answer |
|---|---|
| mcq | "You chose X, but the source supports Y." plus the generator's reason why X is wrong |
| true_false | "The statement is False, not True." plus the explanation, which states the correct fact |
| multi_select | Each extra pick with its reason, and each missed correct option |
| fill_blank | A near miss ("Close — check the exact figure/term"), or the source's term |
| numeric | A fraction instead of a percentage (and vice versa), a sign error, "close — check rounding", or "recheck the formula", always with the working |

Each row also carries `source` (the locator, quote and surrounding passage) and
a `course`. `pa.courses_for_topics` picks the course by embedding the missed
question and its answer with the catalogue embedder, against the recommender's
own course vectors. It searches courses tagged with the linked competency
first. When none are tagged it searches the whole catalogue, and then only
accepts a cosine ≥ 0.35.

### Difficulty calibration (`services/doc_quiz/calibration.py`)

`quiz_item_stats` (keyed by `items.item_key`, a hash of the type, the
normalised stem and the correct answer) counts first-submission responses:
`responses`, `correctCount`, and `thetaSum` (each respondent's practice θ before
the quiz).

A raw p-value confounds difficulty with who answered: strong learners choose
Hard quizzes. So the estimate is the ability-adjusted Rasch one:

```
p̂ = (correct + 0.5) / (n + 1)
b̂ = mean θ − logit(p̂) / 1.7
b = (n·b̂ + 6·b₀) / (n + 6)        b₀ = b of the LLM tag (1.5 / 2.5 / 3.5)
class = Easy if b < 2.0, Hard if b ≥ 3.0, else Medium
```

- Below `MIN_RESPONSES`=5 the LLM's tag stands (`source: "llm_tag"`).
- From 5 responses on, the calibrated class is used (`source:
  "response_data"`). It feeds the θ update and the weighted score, and it is
  shown on the question chip and in the review ("Difficulty from N learner
  responses — the generator had tagged it Hard").
- The table is created by `create_all` at startup. If it is missing or the DB
  is down, `load_stats` returns nothing and the tags are used.

### Practice ability (`main-lms-backend/services/practice_assessment.py`)

These are pure functions, unit-tested in `tests/test_practice_assessment.py`.

- **Item difficulty** on the FRAC scale (`ITEM_DIFFICULTY_B`): Easy 1.5,
  Medium 2.5, Hard 3.5. The model is `P(correct) = 1/(1+exp(−1.7·(θ−b)))`.
- **`update_ability(θ0, results)`** applies `θ += k·(y − P)` for each question.
  - The step is `k = min(0.25, 0.8/n)`, which is 0.16 for 5 questions.
  - The total move from one quiz is capped at ±0.6, and θ stays within [0.5, 5].
  - The effect: missing an Easy question costs more than missing a Hard one,
    and solving a Hard one gains more than solving an Easy one. For one
    question at θ = 2.5:

    | Difficulty | Right | Wrong |
    |---|---|---|
    | Easy | +0.04 | −0.21 |
    | Medium | +0.125 | −0.125 |
    | Hard | +0.21 | −0.04 |

- **`starting_ability`** starts from, in order: the latest practice θ for the
  competency, then the fused skill score, then the level, then 2.0.
- **`latest_practice_value(rows)`** is also what `baseline_assembler` uses.
- **`media_question_difficulty`**: media quizzes use the target difficulty, one
  step harder for `synthesis` questions.
- **`courses_for_topics(engine, texts, comp_id)`**: one course per missed
  question (see above). `review_topics` is the legacy MCQ-only review; `/grade`
  no longer uses it.

### LLM providers (Groq multi-key → Gemini)

Every Assessment Studio text prompt goes through
`services/media_quiz/llm.gemini_json`: the document quiz, the media quiz, the
fact-check and translation, and Learning Mode. `llm_json` is an alias. Calls
go to Groq first and fall back to Gemini:

1. **Groq** (`services/media_quiz/providers.py`, ported from the
   `a057bcf` grounded-quiz branch):
   - `GROQ_API_KEYS` is comma-separated (`GROQ_API_KEY` is also accepted).
     Keys rotate round-robin.
   - A 429 or 413 response cools that key down for `retry-after`, or 30 s.
   - A 401 or 403 disables the key for the life of the process.
   - A 404, `model_not_found` or `decommissioned` disables the model.
   - Rate limits are per (key, model), so each model in `GROQ_MODELS` keeps its
     own cooldown table. When every key is cooling for one model, the next
     model is tried. The default order is
     `openai/gpt-oss-120b,qwen/qwen3.8-27b,openai/gpt-oss-20b`.
   - It calls the REST API with `httpx` in JSON mode, with
     `max_completion_tokens` 8192 and a 60 s timeout.
   - The providers are cached once per process
     (`configured_providers` / `reset_providers`), so cooldowns persist across
     requests.
2. **Gemini:** the text fallback, and the only path for **vision** (prompts
   with `images`, i.e. video keyframes).
   - `DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"` is used when
     `GEMINI_MODEL` is unset.
   - It then falls back to `gemini-3.6-flash`, `gemini-3.5-flash` and
     `gemini-flash-latest`.

`llm_configured()` is true when either Groq or Gemini has a key. `/upload`
returns 500 only when neither does. When every provider fails, the error
names the Groq errors and the Gemini one (502).

The admin system-health panel shows a `groq` component with the key count,
the models and how many are currently usable, and it makes no API call.
Gemini missing while Groq is configured shows as `degraded`, because vision is
off.

Live run, 2026-09-19, Groq only with Gemini disabled: 2 keys × 3 models all
answered. A bilingual 5-question document quiz took 21.5 s with 0 LLM errors
and 45 of 45 Hindi fields translated; the same kind of run took 40–65 s on
Gemini.
`tests/test_llm_providers.py` (7 tests) covers:

- key rotation on 429 and model failover;
- disabling an invalid key;
- Groq exhausted with no Gemini key;
- vision bypassing Groq;
- `parse_json_object`.

### Frontend

- `src/services/api.ts`:
  - `gradeQuiz(quizId, answers: QuizAnswer[])`;
  - types `QuizAnswer` (`number | number[] | string | null`),
    `QuizQuestionType`, `DocQuizQuestion`, `QuizCitation` and
    `ItemCalibration`;
  - `QuizQuestionReview` now has `type`, `feedback`, `solution`, `source`,
    `course`, `calibration`, `review` and `translation`.
- `src/components/assessment/QuizQuestionInput.tsx` renders any question type:
  - radio options, a two-column True/False, checkboxes, an inline blank input,
    or a number input with its unit;
  - a type chip and a difficulty chip;
  - `lang` `en` | `hi` | `bi` (bilingual shows the Hindi under the English);
  - helpers `emptyAnswer`, `isAnswered`, `qType` and `TYPE_LABEL`.
- `src/components/assessment/QuizSkillImpact.tsx` → `QuizQuestionReview` shows:
  - a "Why:" feedback callout;
  - a source block with the locator and the passage;
  - "Revise with <course>";
  - trainer-check flags;
  - the calibration note.
- `src/pages/AssessmentPage.tsx`:
  - A fourth sidebar tab, `"learning"`, renders `LearningChat.tsx` — see
    `docs/features/learning-mode.md`. On mount, the page calls
    `consumePendingStudioUpload()` once to pick up a document Gyan already
    uploaded (`docs/features/chatbot-gyan.md`).
  - The generation panel has the question count (3/5/8/10/15/20), type chips
    and a language choice (English / हिंदी / Bilingual). The Settings tab
    repeats the type defaults.
  - These are posted as `num_questions`, `question_types` and `language`.
  - The quiz header has a display-language toggle for Hindi or bilingual
    quizzes.
  - Answers are `QuizAnswer[]`, and submit requires `isAnswered` for every
    question.
  - Error handling reads `detail.message` when `detail` is an object.
- `src/components/dashboard/AssessmentUploadZone.tsx` uses the same
  `QuizQuestionInput` (compact) with the server's default settings: 5
  questions, all types, English.

## In / out

- **In (upload):** multipart `file` plus `difficulty`, `num_questions`,
  `question_types`, `language`.
- **In (grade):** `{quiz_id, answers: (int | int[] | str | number)[]}` and a
  Bearer token.
- Out (upload):
  ```
  {status, message, quiz_id, filename, file_type, difficulty, language,
   questions[{question, options, correct_answer, explanation, difficulty, type,
     correct_answers?, answer_text?, accepted_answers?, numeric_answer?, tolerance?, unit?,
     expression?, solution?, why_wrong[], citations[{chunkId, locator, quote, passage}],
     answer_type, review{status, note?}, llm_difficulty, item_key,
     calibration{difficulty, source, llmDifficulty, responses, pValue?, b?, …},
     translations?{hi{question, options, explanation, why_wrong, answer_text?, unit?, solution?}}}],
   metadata{character_count, word_count, chunk_count, page_count, slide_count, line_count,
     section_count, ocr?{pages_ocrd, pages_with_text, pages_skipped_over_cap, mean_confidence} | {status, detail}},
   generation{requested, types_requested, types_used, numeric_skipped?, language, chunks_total,
     chunks_used, raw_candidates, valid_candidates, accepted, rejected{reason: n},
     plausibility_check, type_counts, difficulty_counts, fact_check, llm_errors, translation?}}
  ```
- Out (grade): as before, plus each `questionReview` row now has
  `{type, feedback, solution, source{chunkId, locator, quote, passage} | null,
  course{courseId, title, level, durationHours, rating, match, fromCompetency} | null,
  calibration, review, translation}`. `yourAnswer` and `correctAnswer` are
  display text for every type.
- Out (attempts): `{status, attempts[{id, quizId, title, date, score, passed,
  weightedScore, difficulty, competencyId, competencyName, abilityBefore, abilityAfter}]}`.

## Connections

`BaselineAssembler` reads the `PRACTICE_ASSESSMENT` row through the documented
channel. It takes the **latest** practice row, not the max. Floors (completed
courses, work samples, self-report) still hold (see `skill-gap-analysis.md`).
The adaptive diagnostic writes the same row type.

Video, audio and YouTube sources use `routers/media_quiz.py` (see
`media-quiz-generator.md`). Those quizzes land in this router's `QUIZ_STORE` as
plain MCQs, so `/grade` handles them, calibration included.

**Learning Mode** (`routers/learning_mode.py`, `docs/features/learning-mode.md`)
is a sibling mode in the same Assessment Studio page: the same upload, but a
grounded study chat instead of a quiz. It imports this router's extraction
helpers (`_extract_pdf`, `_extract_pptx`, `_extract_txt`, `_clean_text`,
`_chunk_document_text`) and `services/doc_quiz/generate.locate_chunks`
directly, so it stays in lock-step with any extraction change here without
duplicating it. `AssessmentPage.tsx`'s `handleGenerate` takes an optional file
override so Gyan's document hand-off (`docs/features/chatbot-gyan.md`) can
call it right after mount without waiting for `file` state to commit.

The document pipeline reuses the media pipeline's pieces:
- `llm.gemini_json` (Groq multi-key first, then Gemini) and `DEFAULT_GEMINI_MODEL`;
- `fact_check.review_answer` and `translate_texts`, which were factored out so
  the media behaviour is unchanged;
- `question_gen.numbers_in` and `_INTERNAL_REF`;
- `probe.get_ocr`.

## Verification

- `tests/test_doc_quiz.py` has 25 tests: type scoring, feedback, `safe_eval`,
  every validator rejection, numeric expression checks, fill-in and True/False
  rules, lexical dedup, selection quotas, calibration, DOCX order, per-quote
  locators, course picking, and an end-to-end `generate()` with a stub LLM.
  The full backend suite passes, 176 tests. The chat tests that import
  `tests.fixtures` were excluded because of a separate collection issue.
- Live run, 2026-09-19: a 2-section DOCX (CPI and sampling), 8 questions, all
  types, bilingual. HTTP 200 in 65 s.
  - 15 candidates, 0 rejected, 8 accepted (3 MCQ, 2 T/F, 1 multi-select,
    1 fill-in, 1 numeric verified by `45.86 + 10.07 + 6.84`).
  - Plausibility used the embedder.
  - Fact-check: 1 ok and 2 with no reference.
  - All 48 Hindi fields translated, with terms protected.
- Live run: an image-only 2-page PDF (a synthetic scan).
  - Both pages OCR'd, mean confidence 0.915, about 9 s cold.
  - 3 questions (MCQ, fill-in, numeric) in Hindi, HTTP 200 in 42 s.
  - The same file returned 422 before this change.
- Frontend: `tsc --noEmit` is clean and `vite build` succeeds.

## TODOs / edge cases

- `/grade` has not been run end-to-end against the live Neon DB in this change,
  to avoid writing test evidence to the shared DB. Its parts are tested:
  `_question_difficulties`, `_build_review` on a real generated quiz,
  `record_responses` logic and the type scoring.
- **Calibration data is sparse by design.** Items are keyed by content, but
  each upload generates new items, so an item only gathers responses when a
  quiz is taken by several learners. The same `quiz_id` can be shared, but
  there is no share UI yet. A persistent item bank (the same document serves
  the same vetted items) would make calibration effective. The thresholds
  (`MIN_RESPONSES`=5, prior weight 6) are defaults, not tuned.
- **The upload response still contains the answer keys** (`correct_answer`,
  `answer_text`, `numeric_answer`, `citations`), as before; the frontend just
  doesn't show them before grading. Strip them from the response and keep them
  server-side before any real deployment.
- `/upload` is unauthenticated and calls a paid external API. That is a rate
  and abuse exposure, and OCR adds CPU cost (at most 40 pages per upload).
- The plausibility thresholds (0.72 off-topic, 0.97 paraphrase, 0.93 duplicate
  stem) are e5 defaults carried over from the linking and relevance code, not
  tuned on quiz data. The surface checks catch most bad distractors on their
  own.
- Multi-select is all-or-nothing, which keeps the 1-PL update binary. Partial
  credit would need a different item model.
- RapidOCR's recognition model is Chinese/English, so scanned **Hindi** PDFs
  OCR poorly (the same caveat as media OCR). Pages beyond
  `DOC_OCR_MAX_PAGES`=40 are skipped and counted in `ocr.pages_skipped_over_cap`.
- Hindi feedback: the `feedback` sentences are English templates around
  translated rationales. Only the question and explanation have Hindi versions
  in the review.
- A large document still only samples `MAX_CHUNKS`=24 chunks (coverage by
  slices, not by topic).
- `QUIZ_STORE` is in-memory: quizzes vanish on restart and are not shared
  across workers. `quiz_demo` is a hardcoded demo quiz.
- Generation takes about 20 s on Groq, or 40–65 s on Gemini, with translation; the LLM calls dominate.
  The frontend loading text is time-based.
- Linking needs the mock server running. Without it, the attempt is recorded
  but lands on the quiz's own tag or skill name.
- The difficulty constants (item b, slope 1.7, step, ±0.6 cap, weights) are
  reasoned defaults, not calibrated.
- `QuizAttempt.gradedAt` is naive UTC and serialised without a `Z`.
- The first passing submission awards `ASSESSMENT_PASSED` karma (idempotent per
  quizId, subject to the daily cap).
