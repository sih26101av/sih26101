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


async def _run(src: media_io.MediaSource, difficulty: str, target_lang: Optional[str]) -> MediaQuizResult:
    timings: Dict[str, float] = {}
    t0 = time.perf_counter()

    # ── 1-2. probe + route ───────────────────────────────────────────────────
    duration, has_video, has_audio = await asyncio.to_thread(_inspect, src)
    audio = await asyncio.to_thread(media_io.load_audio, src.audio_path) if has_audio and src.audio_path else None
    scan = await asyncio.to_thread(media_io.scan_video, src.video_path, duration) if has_video else None
    regions = extractors.caption_regions(src.captions) if src.captions else None
    pr = await asyncio.to_thread(probe_mod.probe, duration, has_audio, has_video, audio, scan, regions)
    timings["probe_s"] = round(time.perf_counter() - t0, 2)
    report: Dict = {"probe": pr.to_dict(), "content_type": pr.content_type, "vlm_backend": extractors.vlm_label(),
                    "source_notes": src.notes}

    if pr.content_type == probe_mod.REJECT:
        raise NotLearnable(
            f"{REJECT_MESSAGE} The file has little speech ({pr.speech_ratio:.0%}) and little on-screen text "
            f"({pr.text_density:.0%}) — e.g. music or a blank screen.", report)

    # ── 3. extract ──────────────────────────────────────────────────────────
    timeline = Timeline()
    ctype = pr.content_type
    t1 = time.perf_counter()
    if ctype in {probe_mod.NARRATED_SLIDES, probe_mod.TALKING_HEAD}:
        if src.captions:
            n = extractors.add_captions(src.captions, src.caption_kind or "auto", src.caption_lang or "en", timeline)
            report["speech"] = {"source": f"youtube_{src.caption_kind}_captions", "lang": src.caption_lang,
                                "pieces": n, "speech_coverage": 1.0}
        elif audio is not None:
            report["speech"] = {"source": "whisper",
                                **await asyncio.to_thread(extractors.transcribe, audio, pr.speech_regions, timeline)}
    timings["asr_s"] = round(time.perf_counter() - t1, 2)

    slide_windows: List[Dict] = []
    if scan is not None and ctype != probe_mod.TALKING_HEAD:
        t2 = time.perf_counter()
        kfs = scan.keyframes
        if ctype == probe_mod.NARRATED_SLIDES and len(kfs) > OCR_MAX_FRAMES_NARRATED:
            # Speech already carries the lecture; OCR (~2–3 s per text-heavy frame on CPU)
            # only needs to cover the screens, evenly across the video.
            pick = sorted(set(np.linspace(0, len(kfs) - 1, OCR_MAX_FRAMES_NARRATED).round().astype(int).tolist()))
            kfs = [kfs[i] for i in pick]
        ocr_ids = await asyncio.to_thread(extractors.ocr_keyframes, kfs, timeline)
        timings["ocr_s"] = round(time.perf_counter() - t2, 2)

        t3 = time.perf_counter()
        vlm_items = [(i, k) for i, k in enumerate(kfs) if extractors.needs_vlm(k, ctype)]
        vlm_ids = await extractors.describe_keyframes(vlm_items, timeline)
        timings["vlm_s"] = round(time.perf_counter() - t3, 2)
        report["vlm_frames"] = len(vlm_items)

        for i, k in enumerate(kfs):
            ids = ocr_ids.get(i, []) + vlm_ids.get(i, [])
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
    chunks = build_chunks(timeline, slide_windows)
    chunks, rel = await asyncio.to_thread(score_chunks, chunks)
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
