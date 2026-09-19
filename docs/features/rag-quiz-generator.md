# RAG Document → Quiz Generator & Grading (quiz ↔ skill gap)

Upload a training document (PDF/PPT/PPTX/TXT) at a chosen difficulty and get 5
AI-generated MCQs, each tagged Easy/Medium/Hard. Every first attempt, pass
**or** fail, moves the learner's practice ability on the matching role
competency, and that ability feeds the skill-gap baseline. The result screen
shows the skill impact, an answer review and recommendations. Video, audio and
YouTube quizzes grade through the same `/grade` endpoint.

## Code

`main-lms-backend/routers/rag.py` (mounted at `/api/v1/rag`):

- Extraction — `_extract_pdf` (pdfplumber → pypdf fallback), `_extract_pptx`
  (python-pptx incl. tables + speaker notes → raw slide-XML fallback),
  `_extract_txt` (multi-encoding), `_clean_text`.
- `_chunk_document_text` — LangChain `RecursiveCharacterTextSplitter`
  (1000 chars, 150 overlap).
- `_detect_skill_name(text, filename)` — keyword heuristic mapping the document to
  a skill label (Machine Learning, National Accounts, Sample Surveys, …), default
  "General Statistics". Only a display fallback now; linking happens at grading.
- `_generate_mcqs_from_text(text, chunks, difficulty)`:
  - Calls Google Gemini (`google-generativeai`) with
    `response_mime_type: application/json` and temperature 0.3. The model comes
    from `GEMINI_MODEL`, with a hardcoded fallback list.
  - Normalises the output defensively: it strips code fences, accepts
    `questions[]`, a list or a single object, handles alternate key names,
    pads or truncates to exactly 4 options, and coerces `correct_answer` from an
    int, a letter or a string.
  - The prompt asks for a difficulty mix (`_DIFFICULTY_MIX`) and a `difficulty`
    tag on each question. The levels are defined in `_DIFFICULTY_GUIDE`:

    | Target | Mix |
    |---|---|
    | Easy | 3 Easy + 2 Medium |
    | Medium | 1 Easy + 3 Medium + 1 Hard |
    | Hard | 1 Medium + 4 Hard |

  - A missing or odd tag falls back to the quiz difficulty
    (`pa.normalise_difficulty`).
- `POST /upload` takes a multipart `file` and a `difficulty` Form field (default
  Medium).
  - It validates the extension (`SUPPORTED_EXTENSIONS`) and the size
    (`MAX_FILE_SIZE_BYTES` = 25 MB), then extracts, chunks and generates.
  - It stores the quiz in `QUIZ_STORE` under `QZ-XXXXXXXX` with `difficulty` and
    `competency_id: None`. The old hardcoded `FRAC-STAT-001` is gone.
  - **It has no auth dependency.**
- `POST /grade` requires a JWT. The user id is `current_user.username`, never the
  request body. The steps:
  1. **Score.** The plain % decides the pass (≥ 70 %). The difficulty-weighted %
     comes from `pa.weighted_score` (Easy 1, Medium 1.5, Hard 2).
  2. **Link.** `_competency_rows` reads the learner's resolved skill-gap rows
     through `app_state.competency_state`; these are the same rows
     `/skill-gaps` shows. `pa.link_competency` then picks one row, trying in
     order:
     - the quiz's FRAC tag, matched against the row id or its crosswalked
       catalogue id;
     - e5 cosine similarity (the "chat" embedder, floor 0.72) against
       "name. FRAC description";
     - keyword overlap.

     With no match, the evidence falls back to the quiz's own FRAC tag or a
     find-or-create by skill name. That evidence does not move a gap.
  3. **Record.** `_record_attempt` runs in a worker thread. On the **first**
     submission of a quiz, pass or fail, it writes one `QuizAttempt` and one
     `EvidenceLog` `PRACTICE_ASSESSMENT` row.
     - `grantedValue` is the updated practice ability θ (see below).
     - The row is keyed by the matched row's `catalogueId`, else its role id.
     - `metadata_payload` carries the quiz id, title, difficulty, score,
       weighted score, θ before and after, the start basis, a per-question trace
       and the link.
     - Re-submissions are scored for display only and write nothing, so
       retaking a quiz after seeing its answers can't farm the level.
  4. **Refresh.** It calls `app_state.invalidate_user` and re-resolves the
     learner's state. `_row_snapshot` builds `skillImpact.before` and `after`
     (level, fused score, confidence, target, gap).
  5. **First pass only:**
     - `ASSESSMENT_PASSED` karma (`karma_engine.award_safe`);
     - the legacy `_update_internal_db_competency` write;
     - the iGOT sync, with `new_level` set to the resolved level after the quiz.
       The legacy +1 level is used only as a fallback.
  6. **Review.** `questionReview` comes from `pa.review_topics`, missed
     questions first. `recommendations` holds the next difficulty
     (`pa.next_difficulty`), focus topics (the missed questions), courses for the
     matched competency (`pa.suggest_courses`, from the engine's catalogue index)
     and a summary.
- `GET /attempts` requires a JWT. It returns the learner's `QuizAttempt` rows,
  newest first (at most 100), joined with their practice-evidence metadata. It
  backs the studio history.
- `_update_internal_db_competency` is a legacy path kept for the `db_updated`
  response field. It finds or creates a `Competency`, upserts
  `CompetencyProfile`/`UserCompetency` (level +1, capped at 5) and merges an
  `Assessment` audit row. It does **not** hold the learner's real level.
- `_question_difficulties(quiz)` gives each question's own tag, else the quiz's
  difficulty.
- Schemas: `QuizQuestion` (with an optional `difficulty`), `QuizPayload`,
  `DocumentMetadata`, `DocumentUploadResponse`, `GradeRequest`, `GradeResponse`
  and `ErrorResponse`.

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
  competency (a quiz or the adaptive diagnostic), then the current fused skill
  score, then the current level, then 2.0.
- **`latest_practice_value(rows)`** is also what `baseline_assembler` uses.
- **`media_question_difficulty`**: media quizzes use the target difficulty,
  one step harder for `synthesis` questions.

Frontend:
- `src/services/api.ts`:
  - `gradeQuiz(quizId, answers)`, an authenticated `lmsFetch`;
  - `fetchQuizAttempts()`;
  - types `QuizGradeResult`, `QuizSkillImpact`, `QuizQuestionReview` and
    `QuizAttemptRecord`.
- `src/components/assessment/QuizSkillImpact.tsx`:
  - `SkillImpactCard`: ability, skill score and level/target before → after,
    plus how each question moved the ability;
  - `QuizRecommendations`: the next difficulty with a "New quiz at …" button,
    focus topics and courses;
  - `QuizQuestionReview`;
  - `DifficultyChip`.
- `src/components/dashboard/AssessmentUploadZone.tsx` is the drop zone, inline
  quiz and result card on the learner dashboard. It grades with `gradeQuiz` and
  calls `onQuizPassed()` whenever evidence was written (pass or fail), so the
  dashboard refetches the gaps.
- `src/pages/AssessmentPage.tsx` is the full-page Assessment Studio at
  `/assessment`, built on the shared `AppShell`. It has the sections
  `new_quiz` / `history` / `settings` (`StudioTab`) and the `status` machine
  `idle → loading → quiz → grading → result`.
  - `difficulty` (`Easy | Medium | Hard`) is posted to both `/rag/upload` and
    the media endpoints. Questions show a difficulty chip.
  - Grading uses `gradeQuiz`. The result screen adds the difficulty-weighted
    score, `SkillImpactCard`, `QuizRecommendations` and `QuizQuestionReview`.
    Media quizzes keep `MediaAnswerReview`.
  - The history table (skill, difficulty, score and weighted score, ability
    change, result) and the "Your Last Assessment" card read
    `fetchQuizAttempts()`. The old `fetchAchievements` filter on `'RAG Quiz'`
    never matched anything.

## In / out

- In: multipart `file` + `difficulty`; then `{quiz_id, answers: number[]}` and a
  Bearer token.
- Out (upload): `{status, message, quiz_id, filename, file_type,
  questions[{question, options, correct_answer, explanation, difficulty}],
  metadata{character_count, word_count, chunk_count, page_count, slide_count, line_count}}`.
- Out (grade):
  ```
  {status, user_id, quiz_id, score, passed, correct_count, total_questions, message,
   synced_to_igot, igot_response, db_updated, evidenceWritten, karmaAwarded, karmaNote,
   difficulty, weighted_score,
   skillImpact{recorded, linkedToSkillGap, competencyId, competencyName, linkMethod,
     linkScore, before{level, score, confidence, basis, targetLevel, gap}, after{…},
     abilityBefore, abilityAfter, abilityDelta, startBasis,
     perQuestion[{difficulty, correct, expected, delta}], scoreDelta, levelDelta, note?},
   questionReview[{index, question, difficulty, correct, yourAnswer, correctAnswer, explanation}],
   recommendations{nextDifficulty, nextDifficultyReason, focusTopics[],
     courses[{courseId, title, level, durationHours, rating}], summary}}
  ```
- Out (attempts): `{status, attempts[{id, quizId, title, date, score, passed,
  weightedScore, difficulty, competencyId, competencyName, abilityBefore, abilityAfter}]}`.

## Connections

`BaselineAssembler` reads the `PRACTICE_ASSESSMENT` row through the documented
channel. It takes the **latest** practice row, not the max, so a good attempt
raises the fused skill score and a poor one lowers it. The move is bounded, and
the other channels dilute it (see `skill-gap-analysis.md`).

Floors (completed courses, work samples, self-report) still hold. The displayed
whole-number level therefore often stays put while the score moves.

The adaptive diagnostic writes the same row type, so the next quiz continues from
its posterior mean.

Video, audio and YouTube sources use a separate pipeline (`routers/media_quiz.py`,
see `media-quiz-generator.md`). It writes into this router's `QUIZ_STORE` with
per-question difficulty, so `/grade` handles those quizzes too.

## TODOs / edge cases

- Fixed: both frontend callers now grade through the authenticated `lmsFetch`
  (`gradeQuiz`), so `/grade` no longer returns 401.
- Linking needs the mock server running, for the learner's profile. If
  `competency_state` fails, the attempt is still recorded, but the evidence
  lands on the quiz's own tag or skill name and `skillImpact.linkedToSkillGap`
  is false.
- The difficulty constants (item b, slope 1.7, step, ±0.6 cap, weights) are
  reasoned defaults, not calibrated. They have the same status as the baseline
  weights.
- For document quizzes, each question's difficulty is the LLM's own tag. It is
  not validated against response data.
- A quiz whose content matches none of the role competencies (e5 < 0.72 and no
  keyword overlap) never moves a gap. This is by design.
- `QUIZ_STORE` is in-memory: quizzes vanish on restart and are not shared across
  workers. `quiz_demo` is a hardcoded demo quiz.
- `/upload` is unauthenticated and calls a paid external API, which is a rate
  and abuse exposure.
- The default `GEMINI_MODEL` in code (`gemini-3.5-flash-lite`) differs from
  `.env.example` (`gemini-1.5-flash`). Check the model id is valid before demos.
- Legacy `.ppt` binaries are rejected; scanned PDFs without OCR return 422.
- `QuizAttempt.gradedAt` is naive UTC and serialised without a `Z`, so the
  browser renders it as local time.
- The first passing submission awards `ASSESSMENT_PASSED` karma server-side
  (`karma_engine.award_safe`, idempotent per quizId, subject to the daily cap).
  `GradeResponse.karmaAwarded` and `karmaNote` report it.
