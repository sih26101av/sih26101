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
| `routers/media_quiz.py` | Mounted at `/api/v1/rag/media`, in `main.py`. Handles `POST /upload` (multipart `file`, `difficulty`, `target_lang`), `POST /youtube` (JSON `{url, difficulty, target_lang}`) and `GET /capabilities`. Streams uploads to `temp_uploads/media_*` (deleted afterwards). Stores the quiz in `QUIZ_STORE` with a real FRAC `competency_id`, the quiz `difficulty`, and a `difficulty` on each question (`practice_assessment.media_question_difficulty`: the target level, one step harder for `synthesis` questions). `/grade` uses these for the difficulty-aware skill update. Generation is unchanged. Holds the **quiz result cache** for `/youtube` (`MEDIA_YOUTUBE_RESULT_TTL_S`, keyed by video id + difficulty + target_lang); a hit re-issues the same questions under a fresh `quiz_id`. |
| `services/media_quiz/media_io.py` | PyAV stream info and audio decode; a single-pass OpenCV `scan_video` that takes change metrics, keyframes and text-probe frames from the whole video; `download_youtube` → `MediaSource`, built from `_probe_clients`' per-client `_Attempt`s (see *YouTube* below); `_relay_fill` asks `ytrelay` for whatever YouTube withheld; `cache_load` / `cache_store` keep the fetched captions and media per video id; `youtube_diagnosis` answers what this host can reach. |
| `services/media_quiz/ytrelay.py` | The **relay tier**: YouTube through a public Invidious / Piped / cobalt instance instead of directly, so the fetch leaves from *that* server's IP. Instance discovery, a parallel race behind a deadline, a penalty box for failures, VTT / TTML / json3 caption parsing, and `classify()` / `diagnosis()` for the report. See *The relay tier* below. |
| `services/media_quiz/ytgemini.py` | The **Gemini tier**: the Gemini API reads a *public* YouTube link on Google's side (`fileData.fileUri`), so a walled host only talks to `generativelanguage.googleapis.com`. Verbatim transcript + on-screen text, in parallel `videoMetadata` windows; video-token guard, loop guard, speculative windows when the length is unknown. The tier that works from the Oracle VM. See *The Gemini tier* below. |
| `services/media_quiz/probe.py` | Computes `speech_ratio` (Silero VAD bundled with faster-whisper), `text_density` (RapidOCR **detector only**, one frame every ~10 s) and `screen_activity`, then `route()`. |
| `services/media_quiz/extractors.py` | ASR (faster-whisper, per-window language, `task="transcribe"`, Whisper cut-offs), OCR on keyframes (RapidOCR, which runs the PaddleOCR models on ONNX) and the VLM (Gemini for demos, or Ollama Qwen2.5-VL offline). |
| `services/media_quiz/evidence.py` | `Timeline` holds the shared evidence records and prunes them by confidence; `build_chunks` does slide/speech alignment. |
| `services/media_quiz/relevance.py` | Scores each chunk with multilingual-e5 (`ai/embedder.py` role `chat`) against the FRAC descriptions in `mock-igot-server/data/frac_competencies.json` (read-only). |
| `services/media_quiz/question_gen.py` | Per-chunk generation, a synthesis pass and the validator. `generate_naive` is the eval baseline. |
| `services/media_quiz/fact_check.py` | Checks answers against `reference_facts.json` (flags, never rejects), plus translation with ⟦T1⟧-protected terms. The per-answer check (`review_answer`) and the string translator (`translate_texts`) are shared with the document quiz (`services/doc_quiz`); `fact_check` / `translate_questions` wrap them and behave as before. |
| `services/media_quiz/llm.py` | `gemini_json` for text and images, shared with the document quiz. Text prompts go to Groq first (`providers.py`: the `GROQ_API_KEYS` rotate on 429 and the `GROQ_MODELS` fail over), then Gemini. Images use Gemini only. See rag-quiz-generator.md § LLM providers. Also holds `ollama_vision_json`. `DEFAULT_GEMINI_MODEL` (`gemini-3.5-flash-lite`) is the one model id for both quiz paths; `.env.example` matches it. |
| `services/media_quiz/pipeline.py` | `run()` orchestrates the steps; one job at a time (semaphore). Independent stages run concurrently (see *Performance*). `warm_up()` preloads the CPU models and the FRAC competency vectors; the router starts it in a background thread at startup (`MEDIA_WARMUP=0` turns it off). `run_naive()` is the old behaviour. |
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
     A Gemini transcript (*The Gemini tier*) is treated the same way as auto captions
     (0.72, `media.speech.source = gemini_youtube_transcript`).
   - **Gemini screen text replaces OCR** when the host got no frames: each screen row
     becomes `ocr` evidence (`via=gemini_youtube`, confidence 0.78) and its own slide
     window. Routing uses the share of the video with text on screen as the text
     density, just as caption spans stand in for VAD.
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
   - One LLM call (Groq, then Gemini) per group of 4 chunks. Questions must cite evidence ids
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

## Performance

The pipeline's output doesn't depend on scheduling. Only the scheduling below was
tuned, and a benchmark (below) checks that the timeline, chunks and drop counts come
out **identical** to the sequential version.

- **Probe:** the audio branch (decode, then VAD) runs next to the video branch (the
  scan, then the text detector). Routing waits for both. Whisper starts loading
  during the probe when ASR might be needed.
- **Extract:** speech (Whisper or captions) runs next to visuals (OCR, then VLM).
  Visual evidence is written to a staging `Timeline` and appended with
  `Timeline.absorb()`, so the evidence ids are the same as a sequential run's
  (ASR first, then OCR, then VLM).
- **Whisper:** speech windows are independent (`condition_on_previous_text=False`),
  so they decode in parallel on `MEDIA_WHISPER_WORKERS` CTranslate2 workers ×
  `MEDIA_WHISPER_THREADS` threads. The defaults scale with `os.cpu_count()`.
  Library default: 1 × 4. Results are written in window order.
- **OCR:** RapidOCR's ONNX sessions are rebuilt with `MEDIA_OCR_THREADS`=2 intra-op
  threads. By default each session takes every core, and on a single frame most of
  those threads just spin. RapidOCR's det/cls/rec sub-engines are resolved by name
  (`probe._sub_engine`): they are `text_det` / `text_cls` / `text_rec` since 1.3.9
  and `text_detector` / `text_recognizer` in older builds, so a hard-coded layout
  silently skips the tuning here and crashes the text-density probe. `MEDIA_OCR_WORKERS` frames are then recognised in
  parallel, and the probe's text detector uses the same pool. Timeline writes stay
  sequential, in keyframe order.
- **YouTube fetch:** the first player client is asked alone — on a host YouTube trusts
  it returns captions *and* formats and there is nothing left to ask. Only if it
  doesn't are the remaining clients asked **all at once**, stopping at the first that
  has both, so the healthy path is unchanged while a fully walled host pays the slowest
  client instead of the sum of six. Probe retries are 1, not 3: there is a whole chain
  and then the relay tier behind each attempt. When there are no captions, the
  video-only and audio-only streams download in parallel.
- **Repeat links:** the fetch is cached per video id and the finished quiz per
  (video, difficulty, target_lang), so asking for the same link again costs neither
  the download nor the pipeline. The cached result is the same object, so the questions
  are identical — only the `quiz_id` is new, because grading is per attempt.
- **Cold start:** Whisper, RapidOCR, Silero VAD and e5 are loaded by the startup
  warm-up instead of by the first request.
- **Walled hosts:** the Gemini tier replaces the two slowest CPU stages (Whisper,
  OCR) with windows transcribed in parallel on Google's side, and runs next to the
  relay race rather than after it. `media.timings.relevance_s` now reports the e5
  scoring, the one stage `total_s` did not account for.

Measured on the dev laptop (20 logical cores, warm models, VLM off). The input was a
77-min 360p screen recording plus a 3-min narration, routed as `narrated_slides`.
Gemini generation isn't included; it was already concurrent.

| Stage | Before | After |
|---|---|---|
| Probe: scan ∥ text detector (55 frames) | 12 s + 19–22 s, sequential | 13 s + 11 s, alongside VAD |
| OCR, 20 keyframes | 56–64 s | 24–34 s (identical text and scores) |
| Whisper, 6 windows / 180 s of speech | 34–69 s (1 × 4 threads) | 30.5 s alone at 3 × 4 (identical transcript) |
| ASR and OCR | sequential | concurrent (≈51 s together) |
| **Probe + extract, wall time** | **122–154 s** | **≈74 s** |
| First request after a restart | also loads the models | models loaded by the warm-up (≈20 s, in the background) |

YouTube fetch stage, measured 2026-09-23 (6-client chain):

| Case | Before | After |
|---|---|---|
| Healthy host, first client answers fully | 1 probe | 1 probe (unchanged — wave 2 never runs) |
| Healthy host, 2nd client answers (`android_vr`) | 5.9 s | 7.1 s, **same client chosen** |
| Every client walled (the VM) | 12.1 s | **4.0 s** (then the tiers below) |
| Walled host, quiz still built (21-min lecture, Gemini tier ∥ relay race) | failed | **≈20 s** fetch, ≈25 s pipeline, no Whisper / OCR |
| Same, `MEDIA_YOUTUBE_GEMINI=first` (direct probe skipped) | — | ≈20–25 s fetch |
| Healthy host, captions + video | captions, *then* the video stream | both at once (the caption round trips no longer delay the download) |
| Same link again, any path | full download + pipeline | **0.03 s** (fetch cache) / instant (result cache) |

Tuning notes:
- Whisper sweep (workers × threads → seconds): 1×4 69, 1×8 52, 2×4 42, 2×6 34,
  3×4 30.5, 4×3 32. The default is 3 workers when there are ≥12 cores.
- More OCR workers beyond about `cores/4` bring little.
- On machines with fewer than 6 cores, the defaults fall back to one Whisper worker,
  which is the old behaviour.

## YouTube

YouTube serves almost no combined audio+video files any more, and merging
separate streams needs an ffmpeg binary. So `download_youtube` fetches parts:

0. **Cache.** The whole fetch is keyed by video id under `temp_uploads/yt_cache/<id>/`
   (`MEDIA_YOUTUBE_CACHE_TTL_S`=86400, 0 disables). Streams download straight into it,
   so they outlive the request's workdir and a second quiz from the same link starts
   with the captions and the 360p file already on disk.
1. **Metadata** through yt-dlp, with `js_runtimes` deno/node, which are needed
   for YouTube's signature challenges. Playlists and live streams are rejected.
   The length limit is `MEDIA_YOUTUBE_MAX_DURATION_S`=4 h. Every player client in
   the chain is asked (see *Getting past the bot check*) and the best answer wins.
2. **Captions:** manual subtitles first (preferring the video's language), then
   the *original-language* auto captions (`<lang>-orig`), then — only if neither
   exists — any auto track at all. `[Music]` cues are dropped and rolling cues are
   clipped. A track is taken in whatever format the client listed it in
   (`_CAPTION_EXTS`: json3 → srv3 → vtt → ttml → srv2 → srv1) and read by
   `parse_caption_bytes`, which is `ytrelay`'s sniffing parser — the same one both
   paths now use.
3. **Video-only stream** at ≤360p H.264 for frames (about 0.4 MB per minute).
4. **Audio-only stream** (smallest m4a), only when there are no captions.
   Transcription then uses the ASR budget.
5. **The relay tier**, for whatever is still missing — see below. It is only reached
   for gaps: a link yt-dlp served completely never pays for it.

When captions are available, the probe computes the speech ratio from the
caption spans instead of running VAD.

### Getting past the bot check

From a **datacenter IP** — including the Oracle VM — YouTube answers differently
than it does from a laptop, in two ways that must not be confused:

| Symptom | What it means | Does it stop a quiz? |
|---|---|---|
| "Sign in to confirm you're not a bot" | The request was refused outright | Yes — nothing comes back |
| Metadata and caption tracks arrive, but **zero downloadable formats** | The media URLs are gated behind a PO token; the rest of the response is fine | **No** — captions are the speech evidence |

The second case is the common one, and it used to fail the whole link: yt-dlp
raises `No video formats found` / `Requested format is not available` while
resolving the *format selector*, even though the title and the caption tracks were
already in hand. So the metadata pass now runs with `ignore_no_formats_error=True`
and **format availability never decides whether a client "worked"**.

`_probe_clients` asks every client in
`MEDIA_YOUTUBE_PLAYER_CLIENTS=default,android_vr,ios,tv_simply,web_embedded,mweb`
(`default` is whatever yt-dlp ships; an unsupported name only costs one wasted
attempt) and keeps each one's `_Attempt`: captions found, and how many video /
audio formats it advertised. It stops early only when one client has both, and
gives up early only on `_FATAL_MARKERS` (private, removed, members-only), because
a client that can't deliver is not evidence about the video itself. Then:

- **Captions** are fetched from the highest-scoring client that has them —
  `_Attempt.score` ranks captions above streams, since they cost no download and
  are what the questions are built from. If that client's caption fetch fails, the
  next one is tried.
- **Streams** are downloaded only from clients that advertised a usable format,
  best first. `android_vr` and `ios` are the ones that still hand out media URLs
  on datacenter IPs, which is why they now come early in the chain.
- **No video stream is not a failure.** The source is marked
  `video frames unavailable from this server — speech only`, the probe routes it as
  `talking_head`, and the quiz loses only the OCR evidence. It is also much faster
  (no scan, no OCR: ~45 s for a 93-min lecture).
- Only when there are **no captions and no audio** does the link fail, with
  `YOUTUBE_NO_SPEECH_MESSAGE`; when nothing came back at all, with
  `YOUTUBE_BLOCKED_MESSAGE`.

### The relay tier

`ytrelay.py`. Every option above asks YouTube **from this machine**, which is the
thing that fails. The relay tier asks somebody else to ask: a public
[Invidious](https://docs.invidious.io/api/), [Piped](https://docs.piped.video/docs/api-documentation/)
or [cobalt](https://github.com/imputnet/cobalt) instance fetches the video from *its*
address and re-serves it over a plain JSON API. All three are AGPL and need no account
and no API key, so unlike cookies and proxies this costs nothing and needs no setup —
it is on by default (`MEDIA_YOUTUBE_RELAYS=auto`, `off` disables).

| Software | Endpoint | Gives |
|---|---|---|
| Invidious | `GET /api/v1/videos/<id>?local=true` | caption tracks (VTT) + formats proxied through the instance |
| Piped | `GET /streams/<id>` | `subtitles[]` (TTML, refetched as json3) + `pipedproxy-*` streams |
| cobalt | `POST /` | no captions — one **muxed** 360p file, so speech comes from Whisper instead |

Details that matter:

- **Instances are raced, not chained.** They die, rate-limit and get IP-blocked
  constantly, so all candidates are asked at once behind `MEDIA_YOUTUBE_RELAY_DEADLINE_S`=15;
  the first with captions wins. A failure benches that instance for
  `MEDIA_YOUTUBE_RELAY_PENALTY_S`=900, so the next request doesn't re-pay for the graveyard.
- **The list is discovered live** (Invidious' `instances.json`, Piped's registry, both
  fetched in parallel and memoised for an hour); the hardcoded list only fills in behind
  it. It has to be: of the six Piped hosts in that fallback, four had already stopped
  resolving. Instances whose API the operator disabled are dropped, as are Yggdrasil
  mirrors the registry lists as ordinary HTTPS.
- **A media URL is used only if the instance serves it.** A format URL still pointing at
  `googlevideo.com` is discarded — fetching it would leave from this host's IP, the
  address YouTube already refused.
- **Caption policy matches the direct path**: manual tracks first, preferring the video's
  own language, then the original-language auto captions, never a machine translation.
- **Frames are opt-in** (`MEDIA_YOUTUBE_RELAY_FRAMES=0` by default) because no public
  instance currently serves media bytes; a cobalt muxed file is the exception and is
  used for frames anyway, since the bytes are already there.

#### How well it actually works

Measured 2026-09-23 from a residential connection, 45 instances across the three pools,
and it is worth being precise because the answer is "sometimes", not "yes":

| Video | Result |
|---|---|
| 5-min explainer (`dMRDzicSvXk`) | **344 caption cues** from `api.piped.private.coffee` in ~8 s; a cobalt instance also served a muxed file |
| 77-min Python tutorial (`rfscVS0vtbw`) | nothing — Piped got `SignInConfirmNotBotException`, cobalt `error.api.content.too_long` |
| 13.7-hour course (`8DvywoWv6fI`) | nothing — and over the 4 h limit anyway (the deployed server now rejects it as "820 min long") |

The failure modes are reported per instance by `classify()` and summarised in the
diagnosis, because they need different answers:

| `why` | Meaning |
|---|---|
| `youtube_walls_the_instance` | The instance is up and answering, but YouTube refuses **it** — the public pools live in the same datacenter address space the VM does. This is the wall again, one hop out. |
| `instance_refuses_api_clients` | The operator turned the JSON API off or put the host behind a scraper block (`Endpoint disabled`, openresty 403, cobalt `auth.jwt.missing`). |
| `instance_unreachable` | Dead DNS or timeouts — the majority. |

So the tier **does** rescue a walled host, for free and with no configuration, but per
video it is luck. The dependable version is the same code pointed at an instance you
run somewhere that is not a flagged datacenter:
`youtube-access.sh --relay piped:https://my-piped.example` (which also turns frames back
on). That is the only free option that needs no Google account at all.

End-to-end check with every player client forced to fail — i.e. the Oracle VM's state:

```
INFO [relay] piped https://api.piped.private.coffee answered in 10.5s: 344 caption cues (auto/en)
RELAY-ONLY 18.6s  caps=344 kind=auto lang=en
  notes: ['speech from YouTube auto captions (en) relayed by piped (api.piped.private.coffee)',
          'video frames unavailable from this server — speech only']
```

#### Two bugs that made a walled host look worse than it was

Both were found on 2026-09-24, after the VM reported *"gave this server the video's
details but refused its captions, audio and video"* — a state the wall alone does not
explain, because details arriving means the client was answered.

1. **Captions were only taken when a `json3` variant was listed.** `_pick_captions`
   filtered on `ext == "json3"` and returned nothing otherwise, so a client that listed
   the track only as `vtt` or `srv3` was reported as having no captions at all. A second
   case had the same effect: the auto-caption search only considered `<lang>-orig` keys
   and the video's own `language`, so a client that returned the caption list *without*
   `language` (normal on a partly-walled client) left both candidate lists empty and
   threw away a usable track. Any listed format is now accepted, and a plain auto track
   is the last resort — a possibly-translated track beats no speech.
2. **`MEDIA_YOUTUBE_POT_URL` bought nothing on the default chain.** `_yt_clients` only
   appended the PO-token clients `web_safari` / `web` when no client already started
   with `"web"` — and the default chain contains `web_embedded`, so the guard was always
   true and they were **never added**. Configuring a PO-token provider therefore changed
   nothing, in exactly the state (metadata served, formats gated) a PO token exists to
   fix. `_POT_CLIENTS` is now appended whenever a provider is configured.

The failure messages also carry what was attempted now (`_relay_trace`): how many relay
instances were tried, whether YouTube refused those too, or whether the tier is switched
off. Without it a deploy that changes nothing is indistinguishable from a deploy that
did not happen. `ADMIN_NEXT_STEPS` puts the diagnosis first and then orders the fixes by
cost, rather than each message naming a different subset of env vars.

#### When the wall is the IP itself

The Oracle VM is in the harder case, and measuring it settled the question
(2026-09-20, `141-148-192-11.sslip.io`):

```
default, android_vr, ios, web_embedded, mweb   → "Sign in to confirm you're not a bot"
tv_simply                                      → title only: no captions, no formats
android, tv, tv_embedded, web, web_safari, web_creator → same wall
watch page (browser UA, 1.3 MB)                → playability: LOGIN_REQUIRED, caption_tracks: []
```

The second and third lines were measured through `?clients=…`, which overrides the
chain for one call — so this is not "the configured clients fail", it is every
client yt-dlp has. `tv_simply` reaching a title and nothing else is the shape of
the wall: identity is served, content is not.

Every InnerTube client **and** the plain watch page are refused, so there is no
surface left for code to read: the captions work above cannot help a host in this
state, and no chain of player clients will. What *can* help is not reading a different
surface but not being the one to ask — the relay tier above, which rescues this exact
state when an instance is healthy.

The watch page is not a way around this even when it *is* served. Measured from a
residential IP on 2026-09-20: the page returns 200 with `captionTracks` present,
and every one of those `baseUrl`s — plain, `&fmt=json3`, or `&c=WEB` — answers
**200 with an empty body**. `timedtext` now wants a PO token too, so
`fetch_watch_page` / `parse_player_response` / `watch_page_caption_tracks` are
worth keeping for the diagnosis and are not a caption source. Captions come from
yt-dlp, which signs those URLs. The request has to carry credentials
or leave from another address. `deploy/oracle/youtube-access.sh` does each option
and then re-runs the diagnosis:

| Command | What it does | Dependable? |
|---|---|---|
| `--pot` | Docker bgutil PO-token provider on :4416 + the yt-dlp plugin, sets `MEDIA_YOUTUBE_POT_URL`. Also appends `web_safari,web` to the client chain, since a PO token means nothing to the other clients. | Free, but it attests the *client*, not the IP — it may not beat a LOGIN_REQUIRED wall |
| `--cookies <file>` | base64s a Netscape `cookies.txt` into `MEDIA_YOUTUBE_COOKIES_B64` | Yes, until the cookies expire |
| `--proxy <url>` | sets `MEDIA_YOUTUBE_PROXY` | Yes, with a residential/mobile proxy |
| `--relay <kind>:<url>` | pins `MEDIA_YOUTUBE_RELAYS` to your own Invidious/Piped/cobalt instance and turns `MEDIA_YOUTUBE_RELAY_FRAMES` on | Yes, if the instance isn't in a flagged datacenter — and it needs no Google account |
| `--gemini [first\|auto\|off]` | sets `MEDIA_YOUTUBE_GEMINI` (default `first`) and warns if `GEMINI_API_KEY` is missing | **Yes**, for public videos — see *The Gemini tier*. The recommended setting for the VM. |

The relay tier needs none of these to be tried first: it runs by default and is what
makes a link work on the VM today, when an instance happens to be healthy.

Cookies arrive as base64 in `.env` because that is the only writable, persistent,
gitignored thing on the VM — `update.sh` runs `git reset --hard`. `cookies_path()`
materialises them to `main-lms-backend/.yt-cookies.txt` (mode 600, gitignored) the
first time, because yt-dlp needs a real file it can write refreshed cookies back
to. Use a **throwaway** Google account: YouTube suspends accounts whose cookies are
used from a server. When cookies are configured and YouTube still refuses, the
learner is told the saved sign-in expired (`YOUTUBE_STALE_COOKIES_MESSAGE`) rather
than being sent to set up cookies they already set up.

`MEDIA_YOUTUBE_COOKIES_FROM_BROWSER` still exists for dev machines.
`GET /capabilities` reports `youtube.player_clients`, `youtube.cookies`,
`youtube.proxy`, `youtube.pot_provider`, `youtube.relays` and `youtube.cache`.

`GET /youtube/diagnose?url=…` answers what this host can actually do — yt-dlp
version, JS runtimes, per-client captions **and format counts**, watch-page
reachability — and ends with a `verdict`. `&clients=android,tv,web_safari` tries
those instead of the configured chain, which is how a candidate client gets tested
against the real IP without a redeploy (nothing else can settle it):

```json
"verdict": {"can_generate_quiz": true, "can_use_video_frames": false,
            "speech_from": "relay:piped captions", "relay_rescues_this_host": true}
```

It also carries a `relays` block: the candidates tried, which served the video, and a
`failures` histogram over the `why` values above. `pools_are_walled_too` is the one
that settles whether a public instance is worth waiting for on this host or whether
only your own instance / cookies will do.

Failures reach the learner as one sentence, not yt-dlp's multi-line dump
(`_yt_message` strips the `ERROR: [youtube] <id>:` prefix and the wiki links).
Keep `yt-dlp` recent — only new releases keep up with the checks; `setup.sh` and
`update.sh` both `pip install --upgrade yt-dlp`, because the floor pinned in
`requirements-media.txt` counts as satisfied forever.

### WARP egress (no key, no account)

`deploy/oracle/warp.sh`. YouTube judges the *address*, so the one fix that needs no
key, no Google account and no paid proxy is to give yt-dlp a different address:
Cloudflare WARP. [wgcf](https://github.com/ViRb3/wgcf) registers a free anonymous
WARP device, and [wireproxy](https://github.com/windtf/wireproxy) runs the WireGuard
tunnel **in userspace** as SOCKS5 on `127.0.0.1:40000`. It creates no interface and
changes no routes, so only yt-dlp (via `MEDIA_YOUTUBE_PROXY=socks5h://127.0.0.1:40000`)
uses it; SSH, Caddy, Neon and the LLM APIs are untouched. It runs as the deploy user
(`warp-socks.service`), with pinned versions checked against GitHub's sha256 digests.
If the tunnel does not come up, the script removes the proxy setting again rather than
leave yt-dlp pointed at a dead port, and it never overwrites an admin-set proxy.

Verified from the dev machine through WARP (egress `warp=on`, colo BOM), 2026-09-24:
the `default` client answered fully (344 auto captions, 36 video formats) and the full
fetch took ~15 s.

**Live on the VM since 2026-09-24 (`be1641a`/`2e02a2c`)**, installed by the `update.sh`
hook on deploy (`touch ~/.warp/disabled` opts out; `youtube-access.sh --warp` re-runs
it by hand). Measured on the deployed server:

| Check | Before WARP | Through WARP |
|---|---|---|
| `proxy_egress` | — | `warp: on`, colo BOM, a Cloudflare IPv6 |
| `default` client, `dMRDzicSvXk` | BLOCKED ("not a bot") | captions `en`, 36 video / 65 audio formats |
| `default` client, `kqtD5dpn9C8` (1-h tutorial) | BLOCKED | captions `en`, 26 video / 100 audio formats |
| `POST /youtube`, 21-min lecture | 400 | **200 in 93 s**: 7 questions (2 synthesis) from real captions + OCR on 16 screens |

That run's timings on the ARM VM: probe 50 s (the scan of the 360p stream dominates),
OCR 16 s, relevance 6 s, generation 6 s. `GET /youtube/diagnose` shows `proxy_egress`
(the proof YouTube is judging WARP's address) and `warp_setup` (the last `warp.sh` run
and the `warp-socks` service state), since the deploy log itself is behind a GitHub login.
If YouTube ever walls WARP's ranges too, the relay and Gemini tiers still run behind it.

### The Gemini tier

`ytgemini.py`. Everything above asks YouTube for bytes — from this host, from a public
relay, or through credentials the admin supplies — and from the Oracle VM all of those
are walled or luck. The Gemini API is different in kind: it accepts a **public
YouTube URL** as `fileData.fileUri` and Google fetches the video itself. The VM only
makes an HTTPS call to `generativelanguage.googleapis.com`, which no IP wall touches, and
it needs nothing beyond the `GEMINI_API_KEY` the quizzes already use. It is on by
default whenever that key is set.

What it returns is shaped like the other tiers' output:

| Gemini gives | Becomes | Replaces |
|---|---|---|
| `speech` rows — verbatim, in the spoken language, never translated | `MediaSource.captions`, `caption_kind="gemini"` | captions / Whisper |
| `screen` rows — slide text, code, formulas, chart labels | `MediaSource.screen_text` → `ocr` evidence + slide windows | OCR on frames |

**When it runs** (`MEDIA_YOUTUBE_GEMINI`):
- `auto` (default): whenever the direct path left a gap — no speech, or (with
  `MEDIA_YOUTUBE_GEMINI_SCREEN=1`) captions but no frames. It runs **side by side
  with the relay race** in `media_io._gap_fill`. Precedence is by evidence quality,
  not arrival: real captions (direct or relayed) beat the model transcript, and real
  frames beat model-read screens; Gemini fills only what is still missing.
- `first`: skip the direct yt-dlp probe (it can only fail on the VM) and go straight to
  the tiers; if they give nothing, the normal path still runs, without asking the tiers twice.
- `off`.

**Speed.** The video is cut into `MEDIA_YOUTUBE_GEMINI_WINDOW_S`=300 s windows
(`videoMetadata.startOffset/endOffset`) transcribed `MEDIA_YOUTUBE_GEMINI_PARALLEL`=6 at
a time, at `MEDIA_RESOLUTION_LOW` (measured ≈ 91 tokens per second of video). Videos
longer than `MEDIA_YOUTUBE_GEMINI_MAX_S`=3600 get windows spread evenly across their
whole length, like the Whisper budget. On a walled host the length is usually unknown
(YouTube refused the metadata too), so windows go out in **speculative waves**: a
window entirely past the end fails fast (measured: HTTP 500 in ~3 s, no video tokens),
the wave after the one where the speech stops is never sent, and the last cue gives the
duration (1287 s estimated vs 1288 s real). The title comes from YouTube's oEmbed
endpoint, which is plain metadata and answered where the player is not.

**Quality guards** — each one found necessary by measurement, not assumed:

| Guard | Why |
|---|---|
| `usageMetadata.promptTokensDetails` must show `VIDEO`/`AUDIO` tokens | A model that answers without having received the video spends only `TEXT` tokens; its transcript is invented. Refused, not trusted. |
| Rows outside the requested window are dropped; clip-relative times are shifted | The prompt asks for full-video time; this catches the model that didn't comply. |
| `_unloop` drops rows repeating one of the last 4, and `maxOutputTokens` is sized to the window (≈28 tokens/s, min 8192) | One window fell into a repetition loop and wrote **905 rows / 32k tokens in ~110 s**; with the cap and the dedupe it costs one normal window. |
| Truncated JSON is salvaged row by row | A window that hits the cap still yields the rows before the cut. |
| `[Music]`-style rows dropped | Same as the caption parser. |
| A 400 is not retried on other models; 404 models are skipped for the process | A 400 is about the video (private, unlisted); a 404 is a model this key isn't served. |

Measured 2026-09-24, `dMRDzicSvXk` (21-min lecture), every yt-dlp client forced to
fail, cache off:

```
[yt-gemini] dMRDzicSvXk: 113 speech + 17 screen rows from 5/6 windows via gemini-3.5-flash-lite in 19.9s
FETCH 20.7s  caps=113 kind=gemini screen=17
PIPELINE     content=narrated_slides (screen density 0.59)  evidence asr 80 + ocr 17, none dropped
             7 questions (2 synthesis), 10 rejected as "about the video"
```

The questions cite both kinds (e.g. *"What was the initial P Pitch & Roll gain value
displayed on the ESP32 webserver?"* comes from a screen row). From the laptop's own IP the
direct path is untouched: 344 auto captions + the 360p stream in 12.4 s, Gemini not called.
Offline tests: `tests/test_ytgemini.py`.

**Limits.** Public videos only (not unlisted or private). The Gemini free tier allows
8 hours of YouTube video per day, counted per window sent. Model-read screen text is
less exact than OCR on the frames, so it is the fallback, never the first choice.
`GET /youtube/diagnose` now includes a `gemini` block (one 60 s window) and
`verdict.gemini_rescues_this_host`; `/capabilities` reports `youtube.gemini`.

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

**On a headless server, put the headless OpenCV wheel back afterwards:**

```bash
pip uninstall -y opencv-python opencv-contrib-python
pip install --force-reinstall opencv-python-headless
```

`rapidocr_onnxruntime` depends on the **full** `opencv-python` wheel, so pip
installs it over `opencv-python-headless` — and that wheel needs `libGL.so.1` at
import time, which a headless VM doesn't have. `import cv2` then raises and
**only the video path breaks**: audio uploads and document quizzes keep working,
so the symptom is a 503 ("A system library the video decoder needs is missing…")
on video uploads alone. Both wheels own `cv2/`, so the uninstall takes those files
with it — hence `--force-reinstall`. Re-running `pip install -r
requirements-media.txt` undoes this, so it has to come last.

`deploy/oracle/setup.sh` does it with the media extras, and `update.sh` repairs it
on any deploy where `import cv2` fails, falling back to `apt-get install libgl1
libglib2.0-0t64` (one package per call — the names differ across Ubuntu releases
and apt aborts the whole transaction over a single unknown name).

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

Timing on CPU: about 2 min for a 1-min narrated video (ASR dominated). That was
measured before the concurrency work in *Performance*, which roughly halves the CPU
stages; the startup warm-up also removes the cold-start penalty.

## TODOs / edge cases

- **YouTube links work on the deployed VM through WARP** (see *WARP egress*). The Gemini
  tier is still OFF there — the VM's `.env` has no `GEMINI_API_KEY` — so it is not yet a
  backstop if YouTube ever walls WARP's ranges too. Adding the key (then
  `youtube-access.sh --gemini auto`) makes it one; keep `auto`, not `first`, while WARP
  works, since real captions + frames beat a model transcript.
- **`update.sh` rewrote itself mid-run.** Its `git reset --hard` replaces the file bash
  is reading by byte offset, so any deploy that changed `update.sh` ran a splice of the
  old and new script — the first WARP deploy silently skipped WARP that way. It now
  re-execs the synced copy right after the reset; keep its first 10 lines unchanged.
- **Not yet tested:** the real test set above, the Ollama VLM backend, the bgutil
  PO-token provider on the VM, and the relay tier *from the Oracle VM itself* — it was
  verified from a dev machine with the player clients forced to fail, which reproduces
  the VM's refusal but not its IP. Run `GET /youtube/diagnose` there; if `relays.failures`
  is dominated by `youtube_walls_the_instance`, the public pools share the VM's problem
  and only `--relay <your own>` / `--cookies` will do.
- **Relay instances are luck.** One of three test videos was served (see *The relay
  tier*). cobalt refuses long videos outright (`error.api.content.too_long`), and it has
  no captions, so a cobalt rescue costs a Whisper pass. Self-hosting is the fix.
- **YouTube from a datacenter IP** has two failure levels and they need different
  answers (see *Getting past the bot check*):
  - *Formats gated, metadata and captions fine* — handled in code now, verified by
    forcing the client chain onto clients that answer this way. The quiz is built
    from captions, loses only OCR evidence, and is much faster.
  - *Everything refused (LOGIN_REQUIRED)* — what the Oracle VM actually returns as
    of 2026-09-20. Nothing that asks YouTube directly can fix this, but the **relay
    tier** does rescue it when a public instance is healthy (verified end-to-end), and
    always when `youtube-access.sh --relay` points it at your own instance. The
    **Gemini tier** rescues it for every public video with no setup beyond the key.
    Cookies and a residential proxy remain the answers for unlisted videos.
  Run `GET /youtube/diagnose` on the server to see which case you are in rather
  than guessing — its `verdict` answers it in one line. A third state showed up on
  2026-09-24 (details served, no captions and no formats); two code bugs were part of
  it — see *Two bugs that made a walled host look worse than it was*.
- **Checking a deploy took:** `GET /capabilities` reports `youtube.relays` and
  `youtube.cache` only on the current code. If those keys are missing, the VM is
  running an older build and no amount of re-testing the link will change anything.
- **Dev server:** `uvicorn --reload` on Windows hangs on reload in this app. The
  old worker never exits, so new routes 404 until the server is restarted by
  hand. This isn't specific to this feature; after pulling changes, restart the
  backend.
- Whisper `small` transcribes Hinglish poorly. YouTube captions avoid the
  problem; for uploads, `MEDIA_WHISPER_MODEL=medium` is better but slower.
- The endpoints are **unauthenticated**, like `/rag/upload`, and CPU-heavy. They
  should take a JWT once the frontend has a multipart-capable authenticated fetch.
- Processing is synchronous. Long videos keep the request open for minutes. A job
  queue with polling would be better. Only one job runs per process (each job
  already uses most of the CPU).
- The remaining big CPU costs: RapidOCR's detector upscales the short side to
  736 px (`limit_type: min`), and recognition uses about 2 s of CPU per text-heavy
  frame. Lowering either changes the OCR output, so both were left alone. Try them
  against the eval set.
- On hosts with little RAM, the startup warm-up keeps Whisper (~0.5 GB) resident.
  Set `MEDIA_WARMUP=0` there.
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
