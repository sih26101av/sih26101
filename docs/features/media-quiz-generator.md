# Media (Video / Audio / YouTube) → Evidence-Cited Quiz

The Assessment Studio can build a quiz from a video file, an audio file or a
YouTube link. The pipeline doesn't assume every video is a narrated slide
lecture. It first probes what kind of media it has, runs only the tools that fit,
and puts everything they extract on one timeline with a confidence score. The
generated questions have to cite evidence ids from that timeline.

This pipeline is separate from the document quiz in `routers/rag.py`, which it
doesn't modify. It stores quizzes in `rag.QUIZ_STORE`, so the existing `/grade`
endpoint (evidence write, iGOT sync) grades them unchanged.

## Code

Backend, `main-lms-backend/`:

| File | Role |
|---|---|
| `routers/media_quiz.py` | Mounted at `/api/v1/rag/media`, in `main.py`. Handles `POST /upload` (multipart `file`, `difficulty`, `target_lang`), `POST /youtube` (JSON `{url, difficulty, target_lang}`) and `GET /capabilities`. Streams uploads to `temp_uploads/media_*` (deleted afterwards). Stores the quiz in `QUIZ_STORE` with a real FRAC `competency_id`, the quiz `difficulty`, and a `difficulty` on each question (`practice_assessment.media_question_difficulty`: the target level, one step harder for `synthesis` questions). `/grade` uses these for the difficulty-aware skill update. Generation is unchanged. |
| `services/media_quiz/media_io.py` | PyAV stream info and audio decode; a single-pass OpenCV `scan_video` that takes change metrics, keyframes and text-probe frames from the whole video; `download_youtube` → `MediaSource` (see *YouTube* below). |
| `services/media_quiz/probe.py` | Computes `speech_ratio` (Silero VAD bundled with faster-whisper), `text_density` (RapidOCR **detector only**, one frame every ~10 s) and `screen_activity`, then `route()`. |
| `services/media_quiz/extractors.py` | ASR (faster-whisper, per-window language, `task="transcribe"`, Whisper cut-offs), OCR on keyframes (RapidOCR, which runs the PaddleOCR models on ONNX) and the VLM (Gemini for demos, or Ollama Qwen2.5-VL offline). |
| `services/media_quiz/evidence.py` | `Timeline` holds the shared evidence records and prunes them by confidence; `build_chunks` does slide/speech alignment. |
| `services/media_quiz/relevance.py` | Scores each chunk with multilingual-e5 (`ai/embedder.py` role `chat`) against the FRAC descriptions in `mock-igot-server/data/frac_competencies.json` (read-only). |
| `services/media_quiz/question_gen.py` | Per-chunk generation, a synthesis pass and the validator. `generate_naive` is the eval baseline. |
| `services/media_quiz/fact_check.py` | Checks answers against `reference_facts.json` (flags, never rejects), plus translation with ⟦T1⟧-protected terms. |
| `services/media_quiz/llm.py` | `gemini_json` for text and images (same `GEMINI_API_KEY`/`GEMINI_MODEL` as the document quiz) and `ollama_vision_json`. |
| `services/media_quiz/pipeline.py` | `run()` orchestrates the steps; one job at a time (semaphore). `run_naive()` is the old behaviour. |
| `scripts/eval_media_quiz.py` | Runs a test folder through the old and new pipelines and writes `results.csv` and `summary.md`. |
| `requirements-media.txt` | Optional dependencies. Without them the endpoints return 503; the document quiz is unaffected. |

Frontend, `frontend/src/`:
- `services/mediaQuizApi.ts` has `generateMediaQuiz`, `generateYoutubeQuiz`, `isMediaFile`, `MEDIA_ACCEPT` and the response types.
- `components/assessment/MediaQuizExtras.tsx` has:
  - `YoutubeLinkInput`, shown for the "Paste Text/URL" source.
  - `MediaAnalysisCard`, shown above a media quiz.
  - `MediaAnswerReview`, shown only on the result screen because cited evidence would reveal the answers.
- `pages/AssessmentPage.tsx` has a few hook-in lines: the media branch in `handleGenerate`, the `youtubeUrl` state, the `accept` list, and rendering of the three components.

## Pipeline

1. **Probe** (seconds, across the whole file):
   - Speech ratio from VAD.
   - Text density: the share of sampled frames with real text boxes.
   - Screen activity: the share of frame pairs with *localised* change.

   Changes are classified by spread. A new slide changes few pixels, but its
   bounding box covers ≥15% of the frame. A cursor, typing or a single bullet
   build stays in a small box. Timestamps come from the decoder PTS
   (`CAP_PROP_POS_MSEC`), which keeps variable-frame-rate phone recordings aligned.
2. **Route** (thresholds are env-tunable: `MEDIA_SPEECH_HIGH=0.30`,
   `MEDIA_TEXT_HIGH=0.40`, `MEDIA_ACTIVITY_HIGH=0.15`):

   | Content type | Rule | Tools |
   |---|---|---|
   | `narrated_slides` | High speech, high text | ASR + OCR, plus VLM on charts and low-OCR frames |
   | `talking_head` | High speech, low text (or audio-only) | ASR |
   | `silent_screen_demo` | Low speech, high activity | VLM on every keyframe + OCR |
   | `silent_slides` | Low speech, high text | OCR + VLM on diagrams |
   | `reject` | Everything else | 422 "Not enough learnable content found." |
3. **Extract to the timeline.** Every record has the form
   `{id, t_start, t_end, source: asr|ocr|vlm, text, confidence, lang}`.
   - **ASR:** a segment is kept only if `no_speech_prob < 0.6`, `avg_logprob > -1.0`
     and `compression_ratio < 2.4`, and it isn't on the outro-hallucination
     blocklist. Its confidence is `exp(avg_logprob)·(1−no_speech_prob)`. Language
     is detected for each VAD window of ≤28 s (for code-switching), and ASR never
     translates. Decoding uses `no_repeat_ngram_size=3`, `repetition_penalty=1.15`
     and temperatures `[0, 0.4]`: Whisper `small` loops on Hinglish, and the loops
     are rejected anyway but cost about 2× real time.
   - **ASR budget:** CPU Whisper runs at about real time, so if a file has more speech
     than `MEDIA_ASR_BUDGET_S`=150 s, an evenly spread sample of speech windows is
     transcribed instead (the coverage is reported in `media.speech.speech_coverage`).
   - **YouTube captions replace ASR** when they exist (see below): manual captions
     get confidence 0.92, auto-generated 0.72. They're merged into pieces of ≤20 s.
   - **OCR:** confidence is the length-weighted mean of the line scores. Narrated
     videos OCR at most `MEDIA_OCR_MAX_FRAMES_NARRATED`=20 evenly spread keyframes
     (text-heavy code screens cost 2–3 s each on CPU); silent videos OCR all ≤40.
     Frames are never upscaled. For a slide
     build, only the last frame before the scene change is kept (earlier partial
     builds are dropped). Repeated screens are merged.
   - **VLM:** runs on at most `MEDIA_VLM_MAX_FRAMES`=24 keyframes, in batches of 4,
     and describes actions by comparing consecutive frames. Confidence is capped
     at 0.85.
   - Records below `MEDIA_MIN_CONFIDENCE`=0.45 are dropped. Drop reasons are
     counted in `media.evidence.dropped`.
4. **Chunk.** Each keyframe becomes a chunk: its OCR/VLM text plus the speech from
   the slide's display window **and the next 20 s** (`MEDIA_ALIGN_TAIL_S`).
   Leftover speech is grouped into ~90 s windows.
5. **Relevance.** Chunks are scored by e5 cosine against the FRAC competencies.
   The top `MEDIA_MAX_CHUNKS`=12 above `MEDIA_RELEVANCE_FLOOR`=0.76 are kept
   (never fewer than 6, so general study videos still yield a quiz). The competency
   with the most votes becomes the quiz's `competency_id` / `skill_name`. If even
   the best chunk is below the floor (`off_topic`, e.g. a biology lecture), no FRAC
   id is assigned and the skill is "General Learning".
6. **Generate.**
   - One Gemini call per group of 4 chunks. Questions must cite evidence ids
     from their own chunk.
   - One synthesis call over a summary of the whole video. These questions must
     cite ≥2 chunks.
   - The validator rejects a question for:
     - bad options or a bad answer index;
     - unknown or low-confidence evidence ids;
     - a number in the correct answer that is absent from the cited evidence (Devanagari digits are normalised first);
     - asking about the video itself.
   - Options are shuffled deterministically, and questions are picked round-robin
     across chunks: 5 chunk questions plus up to 2 synthesis questions.
7. **Review.**
   - Answers of type number or definition are matched against
     `reference_facts.json`. A mismatch sets `review.status="flagged"` with a note
     for the trainer.
   - If `target_lang` is set (hi, bn, ta, …), glossary terms are protected as
     ⟦Tn⟧, the text is translated and the terms are restored. A field whose
     placeholders are lost keeps its English text.

## YouTube

YouTube serves almost no combined audio+video files any more, and merging
separate streams needs an ffmpeg binary. So `download_youtube` fetches parts:

1. **Metadata** through yt-dlp, with `js_runtimes` deno/node, which are needed
   for YouTube's signature challenges. Playlists and live streams are rejected.
   The length limit is `MEDIA_YOUTUBE_MAX_DURATION_S`=4 h.
2. **Captions:** manual subtitles first (preferring the video's language), then
   the *original-language* auto captions (`<lang>-orig`). Machine-translated
   tracks are never used. Captions are read as json3, `[Music]` cues are dropped,
   and rolling cues are clipped.
3. **Video-only stream** at ≤360p H.264 for frames (about 0.4 MB per minute).
4. **Audio-only stream** (smallest m4a), only when there are no captions.
   Transcription then uses the ASR budget.

When captions are available, the probe computes the speech ratio from the
caption spans instead of running VAD.

## In / out

- **Upload response:** the document-quiz fields (`status, message, quiz_id, filename,
  file_type, questions[]`) plus `competency_id` and `skill_name`, and:
  - each question also has `evidence[]`, `kind` (chunk|synthesis), `answer_type`,
    `t_start/t_end` and `review{status, note}`;
  - `metadata{duration_s, source, chunk_count, …}`;
  - `media{content_type, probe, evidence, relevance, generation, fact_check,
    translation?, timings, chunks, vlm_backend}`;
  - `evidence[]` (the cited records only).
- **Not learnable:** 422 with `detail = {message, media}`.
- **Errors:** 400 for a bad extension or link, 413 when the upload exceeds
  `MEDIA_MAX_UPLOAD_MB`=1024, 502 when the LLM fails, 503 when dependencies are missing.

## Setup

```bash
cd main-lms-backend
pip install -r requirements-media.txt   # faster-whisper, opencv-headless, rapidocr_onnxruntime, yt-dlp
```

The first ASR call downloads Whisper `small` (~480 MB; set it with
`MEDIA_WHISPER_MODEL`, `MEDIA_WHISPER_DEVICE` and `MEDIA_WHISPER_COMPUTE`). No
PyTorch or ffmpeg binary is needed.

The VLM backend is set by `MEDIA_VLM_BACKEND`. The default is `gemini` when a key
is set, otherwise `none`:
- `gemini` is **demo-only**: frames leave the machine, and every response and the
  UI say so.
- `ollama` is the offline option: `ollama pull qwen2.5vl:3b`, then set
  `MEDIA_VLM_MODEL`. It needs a GPU to run at a usable speed.

## Verification

Test set and expected behaviour:

| Test video | What it checks | Expected after the fix |
|---|---|---|
| 5-min narrated slide lecture, no captions | Question 1 | Normal question set |
| Phone screen recording, variable frame rate | Question 2, timestamp drift | Slides still matched to the right speech |
| Silent Excel or Python screen demo | Flaws 1, 2 | Questions about the actions shown, not empty or invented |
| Lecture with music in the intro | Flaw 1 | No "thank you for watching"-style questions |
| Hinglish lecture with an English intro | Flaw 5 | Hindi sections transcribed correctly |
| Slides with charts and formulas | Flaw 3 | Questions about what the chart shows |
| Blank screen with music | Routing | Clean rejection message |

To run it:

```bash
python scripts/eval_media_quiz.py path/to/test_videos --out eval_out
```

Then fill in `usable (y/n)` in `eval_out/results.csv` and compare the unusable
counts for old vs new.

Smoke-tested (2026-09-19) on synthetic clips: Windows TTS narration, rendered
slides with bullet builds, and a tone over a blank screen. Each clip routed
correctly:
- **Narrated slides:** 16 evidence records, 2 partial builds dropped, 6 cited
  questions including 1 synthesis, 3 fact-checks OK.
- **Talking head:** 5 questions; `hi` translation kept the protected terms.
- **Silent slides:** 6 questions; one hallucinated number was rejected.
- **Silent Excel demo** (cells typed in, then a formula): routed to
  `silent_screen_demo`; OCR plus the Gemini VLM; 4 questions about the table and
  what `=AVERAGE(D2:D5)` calculates.
- **Blank screen with music:** 422.

Real YouTube video (2026-09-19): "Python Tutorial for Beginners", 77 min,
Hinglish, with Hindi auto-captions. Runs on warm CPU:

| Path | Download | Total | Result |
|---|---|---|---|
| Captions (normal) | 9 s | about 2 min | 212 speech pieces + 18 OCR screens; 7 questions (2 synthesis); tagged "Python for Statistical Computing" |
| No captions (forced) | 16 s | about 7 min (at the old 240 s budget) | Sampled Whisper at 4.7 % coverage + OCR; 7 questions |

Through the live API with the frontend's `Origin` header: HTTP 200, CORS OK,
7 questions (about 4 min on a cold server).

Timing on CPU: about 2 min for a 1-min narrated video (ASR dominates).

## TODOs / edge cases

- **Not yet tested:** the real test set above, the Ollama VLM backend, and
  YouTube videos that have neither captions nor a downloadable video stream.
- **Dev server:** `uvicorn --reload` on Windows hangs on reload in this app. The
  old worker never exits, so new routes 404 until the server is restarted by
  hand. This isn't specific to this feature; after pulling changes, restart the
  backend.
- Whisper `small` transcribes Hinglish poorly. YouTube captions avoid the
  problem; for uploads, `MEDIA_WHISPER_MODEL=medium` is better but slower.
- The endpoints are **unauthenticated**, like `/rag/upload`, and CPU-heavy. They
  should take a JWT once the frontend has a multipart-capable authenticated fetch.
- Processing is synchronous. Long videos keep the request open for minutes. A job
  queue with polling would be better. Only one job runs per process.
- The RapidOCR recognition model is Chinese/English. Devanagari slides OCR poorly
  and are mostly dropped by the confidence gate. A Devanagari recognition model is
  needed for Hindi slides.
- The chart/table detector is a heuristic: edge density outside text boxes ≥0.05.
- `reference_facts.json` is a 10-entry seed. Extend it from the NSSO manuals, the
  CPI handbook and the glossary.
- The relevance floor 0.76 and the probe thresholds were tuned on synthetic clips
  only. Re-tune them with the eval set.
- The quiz is in-memory, like the document quiz. Grading is now authenticated
  (`gradeQuiz`) and moves the learner's practice ability on the linked role
  competency. See `rag-quiz-generator.md`.
