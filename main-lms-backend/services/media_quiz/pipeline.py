"""
FILE: services/media_quiz/pipeline.py
─────────────────────────────────────────────────────────────────────────────
Video / audio / YouTube → evidence timeline → cited MCQs.

  1. probe      — speech ratio, text density, screen activity (whole file)
  2. route      — narrated_slides | talking_head | silent_screen_demo |
                  silent_slides | reject ("Not enough learnable content found.")
  3. extract    — only the tools the route needs, all onto one Timeline with
                  confidences; low-confidence evidence is pruned
  4. chunk      — keyframe windows + 20 s speech tail, or speech windows
  5. relevance  — multilingual-e5 vs FRAC competencies (also picks the competency)
  6. generate   — per-chunk questions citing evidence ids + synthesis pass,
                  validated against the timeline
  7. review     — fact-check numbers/definitions (flag, not reject);
                  optional term-protected translation

run_naive() is the "old pipeline" baseline used only by scripts/eval_media_quiz.py.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

import numpy as np

from services.media_quiz import extractors, media_io, probe as probe_mod
from services.media_quiz.evidence import MIN_CONFIDENCE, Timeline, build_chunks
from services.media_quiz.fact_check import fact_check, translate_questions
from services.media_quiz.question_gen import MediaQuestion, generate, generate_naive
from services.media_quiz.relevance import score_chunks

logger = logging.getLogger(__name__)

REJECT_MESSAGE = "Not enough learnable content found."
OCR_MAX_FRAMES_NARRATED = int(os.getenv("MEDIA_OCR_MAX_FRAMES_NARRATED", "20"))

# Whisper / OCR are CPU-heavy: one media job at a time per process.
_JOB_LOCK = asyncio.Semaphore(1)


class NotLearnable(ValueError):
    def __init__(self, message: str, report: Dict):
        super().__init__(message)
        self.report = report


@dataclass
class MediaQuizResult:
    questions: List[MediaQuestion]
    report: Dict
    competency_id: Optional[str]
    competency_name: Optional[str]
    transcript_excerpt: str
    evidence: List[Dict] = field(default_factory=list)


def _excerpt(timeline: Timeline, limit: int = 4000) -> str:
    out, size = [], 0
    for e in timeline.all():
        if size + len(e.text) > limit:
            break
        out.append(e.text)
        size += len(e.text)
    return " ".join(out)


async def run(source: Union[str, media_io.MediaSource], difficulty: str = "Medium",
              target_lang: Optional[str] = None) -> MediaQuizResult:
    """`source`: a local media path, or a MediaSource (YouTube: captions + separate video / audio)."""
    if isinstance(source, str):
        source = media_io.MediaSource.from_file(source, os.path.basename(source))
    async with _JOB_LOCK:
        return await _run(source, difficulty, target_lang)


async def _gather_all(*coros):
    """gather() that lets every branch finish before re-raising, so no worker thread
    outlives the job lock."""
    results = await asyncio.gather(*coros, return_exceptions=True)
    for r in results:
        if isinstance(r, BaseException):
            raise r
    return results


def _preload_whisper() -> None:
    try:
        extractors.get_whisper()
    except Exception as exc:                 # re-raised where ASR actually needs the model
        logger.debug("[media] Whisper preload failed: %s", exc)


def warm_up() -> None:
    """Load the CPU models (RapidOCR, Silero VAD, Whisper, e5) off the request path, so the
    first media quiz after a restart doesn't pay for them. Each one is optional."""
    t0 = time.perf_counter()
    steps = [
        ("ocr", probe_mod.get_ocr),
        ("vad", lambda: probe_mod.speech_regions(np.zeros(16000, dtype=np.float32))),
        ("whisper", extractors.get_whisper),
    ]

    def e5():
        from ai.embedder import get_embedder
        get_embedder("chat")

    def frac():
        # The FRAC descriptions are embedded once and memoised (encode_cached), but the
        # first media quiz pays for it. It is the same model as e5 above, so warming it
        # here costs a few hundred ms and takes a step off the request path.
        from ai.embedder import encode_cached
        from services.media_quiz.relevance import frac_competencies
        comps = frac_competencies()
        if comps:
            encode_cached("chat", [f"{c['name']}. {c['description']}" for c in comps], kind="passage")

    steps += [("e5", e5), ("frac", frac)]
    for name, fn in steps:
        try:
            fn()
        except Exception as exc:
            logger.info("[media] warm-up of %s skipped: %s", name, exc)
    logger.info("[media] models warm in %.1fs.", time.perf_counter() - t0)


def _inspect(src: media_io.MediaSource):
    """(duration, has_video, has_audio_stream) across the source's parts."""
    duration, has_video, has_audio = src.duration or 0.0, False, False
    if src.video_path:
        vi = media_io.stream_info(src.video_path)
        has_video = vi.has_video
        has_audio = vi.has_audio and src.audio_path == src.video_path
        duration = max(duration, vi.duration)
    if src.audio_path and src.audio_path != src.video_path:
        ai = media_io.stream_info(src.audio_path)
        has_audio = ai.has_audio
        duration = max(duration, ai.duration)
    return duration, has_video, has_audio


def _coverage(spans, duration: float) -> float:
    """Share of the video covered by the union of the spans."""
    total, end = 0.0, 0.0
    for c in sorted(spans, key=lambda c: c.start):
        s, e = max(c.start, end), max(c.end, c.start)
        if e > s:
            total += e - s
            end = e
    return min(1.0, total / duration) if duration else 0.0


def _screen_evidence(screen, timeline: Timeline):
    """Gemini's screen rows → the same (windows, ocr_ids, vlm_ids) shape visual_branch
    returns for real keyframes, so chunking treats a screen like a slide. The source is
    "ocr" because to the question writer that is what it is: text shown on screen."""
    from types import SimpleNamespace

    from services.media_quiz.ytgemini import SCREEN_CONFIDENCE

    wins, ids = [], {}
    for c in screen:
        ev = timeline.add(c.start, c.end, "ocr", c.text, SCREEN_CONFIDENCE,
                          lang=extractors.lang_of(c.text), via="gemini_youtube")
        if ev:
            ids[len(wins)] = [ev.id]
            wins.append(SimpleNamespace(t_start=c.start, t_end=max(c.end, c.start + 1.0)))
    return wins, ids, {}


async def _run(src: media_io.MediaSource, difficulty: str, target_lang: Optional[str]) -> MediaQuizResult:
    timings: Dict[str, float] = {}
    t0 = time.perf_counter()

    # ── 1-2. probe + route ───────────────────────────────────────────────────
    # The audio branch (decode + VAD) and the video branch (scan + text detector) are
    # independent, so they run side by side; routing waits for both.
    duration, has_video, has_audio = await asyncio.to_thread(_inspect, src)
    regions = extractors.caption_regions(src.captions) if src.captions else None
    # Whisper loads (cold: several seconds) while the probe runs; the reference keeps the task alive.
    preload = (asyncio.create_task(asyncio.to_thread(_preload_whisper))
               if has_audio and src.audio_path and not src.captions else None)

    async def audio_branch():
        if not (has_audio and src.audio_path):
            return None, None
        audio = await asyncio.to_thread(media_io.load_audio, src.audio_path)
        vad = await asyncio.to_thread(probe_mod.speech_regions, audio) if regions is None else None
        return audio, vad

    async def video_branch():
        if not has_video:
            return None, None
        scan = await asyncio.to_thread(media_io.scan_video, src.video_path, duration)
        dens = await asyncio.to_thread(probe_mod.text_density, scan.text_frames) if scan is not None else None
        return scan, dens

    (audio, vad), (scan, dens) = await _gather_all(audio_branch(), video_branch())
    pr = await asyncio.to_thread(probe_mod.probe, duration, has_audio, has_video, audio, scan, regions, vad, dens)
    screen = src.screen_text if scan is None else None
    if screen:
        # No frames reached this host, but Gemini read the screens (ytgemini). Route on
        # that instead: the share of the video with text on screen stands in for the
        # text detector's density, exactly as caption spans stand in for VAD.
        pr.text_density = _coverage(screen, duration or pr.duration)
        pr.content_type = probe_mod.route(pr.speech_ratio, pr.text_density, 0.0, True)
        pr.tools = [t.replace("ocr", "ocr(gemini screen text)") for t in probe_mod.ROUTE_TOOLS[pr.content_type]
                    if not t.startswith("vlm")]
    timings["probe_s"] = round(time.perf_counter() - t0, 2)
    report: Dict = {"probe": pr.to_dict(), "content_type": pr.content_type, "vlm_backend": extractors.vlm_label(),
                    "source_notes": src.notes}

    if pr.content_type == probe_mod.REJECT:
        raise NotLearnable(
            f"{REJECT_MESSAGE} The file has little speech ({pr.speech_ratio:.0%}) and little on-screen text "
            f"({pr.text_density:.0%}) — e.g. music or a blank screen.", report)

    # ── 3. extract ──────────────────────────────────────────────────────────
    # Speech (ASR / captions) and visuals (OCR → VLM) don't depend on each other, so
    # they run concurrently: Whisper on CPU while OCR shares the remaining cores and
    # the VLM waits on the network. Visual evidence goes to its own timeline and is
    # appended afterwards, so the evidence ids are the same as in a sequential run.
    timeline = Timeline()
    visual_tl = Timeline()
    ctype = pr.content_type
    t1 = time.perf_counter()

    async def speech_branch():
        t = time.perf_counter()
        if preload is not None:
            await preload                    # never raises; transcribe() surfaces a missing model
        if ctype in {probe_mod.NARRATED_SLIDES, probe_mod.TALKING_HEAD}:
            if src.captions:
                n = extractors.add_captions(src.captions, src.caption_kind or "auto", src.caption_lang or "en",
                                            timeline)
                report["speech"] = {"source": ("gemini_youtube_transcript" if src.caption_kind == "gemini"
                                               else f"youtube_{src.caption_kind}_captions"), "lang": src.caption_lang,
                                    "pieces": n, "speech_coverage": 1.0}
            elif audio is not None:
                report["speech"] = {"source": "whisper", **await asyncio.to_thread(
                    extractors.transcribe, audio, pr.speech_regions, timeline)}
        timings["asr_s"] = round(time.perf_counter() - t, 2)

    async def visual_branch():
        if screen and ctype != probe_mod.TALKING_HEAD:
            return _screen_evidence(screen, visual_tl)
        if scan is None or ctype == probe_mod.TALKING_HEAD:
            return [], {}, {}
        t2 = time.perf_counter()
        kfs = scan.keyframes
        if ctype == probe_mod.NARRATED_SLIDES and len(kfs) > OCR_MAX_FRAMES_NARRATED:
            # Speech already carries the lecture; OCR (~2–3 s per text-heavy frame on CPU)
            # only needs to cover the screens, evenly across the video.
            pick = sorted(set(np.linspace(0, len(kfs) - 1, OCR_MAX_FRAMES_NARRATED).round().astype(int).tolist()))
            kfs = [kfs[i] for i in pick]
        ocr_ids = await asyncio.to_thread(extractors.ocr_keyframes, kfs, visual_tl)
        timings["ocr_s"] = round(time.perf_counter() - t2, 2)

        t3 = time.perf_counter()
        vlm_items = [(i, k) for i, k in enumerate(kfs) if extractors.needs_vlm(k, ctype)]
        vlm_ids = await extractors.describe_keyframes(vlm_items, visual_tl)
        timings["vlm_s"] = round(time.perf_counter() - t3, 2)
        report["vlm_frames"] = len(vlm_items)
        return kfs, ocr_ids, vlm_ids

    _, (kfs, ocr_ids, vlm_ids) = await _gather_all(speech_branch(), visual_branch())
    remap = timeline.absorb(visual_tl)
    timings["extract_s"] = round(time.perf_counter() - t1, 2)

    slide_windows: List[Dict] = []
    for i, k in enumerate(kfs):
        ids = [remap[e] for e in ocr_ids.get(i, []) + vlm_ids.get(i, [])]
        if ids:
            slide_windows.append({"t_start": k.t_start, "t_end": k.t_end, "evidence_ids": ids})

    extracted = timeline.counts()
    timeline.prune_low_confidence(MIN_CONFIDENCE)
    report["evidence"] = {"extracted": extracted, "kept": timeline.counts(),
                          "dropped": dict(timeline.dropped), "min_confidence": MIN_CONFIDENCE}
    if len(timeline) == 0:
        raise NotLearnable(f"{REJECT_MESSAGE} Nothing extracted from the {ctype.replace('_', ' ')} passed the "
                           "confidence checks.", report)

    # ── 4-5. chunk + relevance ──────────────────────────────────────────────
    t5 = time.perf_counter()
    chunks = build_chunks(timeline, slide_windows)
    chunks, rel = await asyncio.to_thread(score_chunks, chunks)
    timings["relevance_s"] = round(time.perf_counter() - t5, 2)
    report["relevance"] = rel
    if not chunks:
        raise NotLearnable(REJECT_MESSAGE, report)

    # ── 6. generate + validate ──────────────────────────────────────────────
    t4 = time.perf_counter()
    questions, gen = await generate(chunks, timeline, difficulty)
    timings["generation_s"] = round(time.perf_counter() - t4, 2)
    report["generation"] = gen
    if not questions:
        raise NotLearnable(f"{REJECT_MESSAGE} No generated question could be traced back to reliable evidence.",
                           report)

    # ── 7. review ───────────────────────────────────────────────────────────
    report["fact_check"] = fact_check(questions)
    if target_lang and target_lang != "en":
        report["translation"] = await translate_questions(questions, target_lang)

    timings["total_s"] = round(time.perf_counter() - t0, 2)
    report["timings"] = timings
    report["chunks"] = [{"id": c.id, "t_start": round(c.t_start, 1), "t_end": round(c.t_end, 1),
                         "relevance": round(c.relevance, 3) if c.relevance is not None else None,
                         "competency_id": c.competency_id, "evidence": c.evidence_ids} for c in chunks]
    cited = {eid for q in questions for eid in q.evidence}
    return MediaQuizResult(
        questions=questions, report=report,
        competency_id=rel.get("competency_id"), competency_name=rel.get("competency_name"),
        transcript_excerpt=_excerpt(timeline),
        evidence=[e.to_dict() for e in timeline.all() if e.id in cited],
    )


async def run_naive(path: str, difficulty: str = "Medium") -> List[Dict]:
    # Eval baseline for local files only.
    """The pre-fix behaviour: assume a narrated lecture, transcribe everything, ask for 5 MCQs."""
    audio = await asyncio.to_thread(media_io.load_audio, path)
    transcript = await asyncio.to_thread(extractors.transcribe_naive, audio) if audio is not None else ""
    if not transcript.strip():
        return []
    return await generate_naive(transcript, difficulty)
