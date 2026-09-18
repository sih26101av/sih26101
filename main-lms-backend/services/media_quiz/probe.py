"""
FILE: services/media_quiz/probe.py
─────────────────────────────────────────────────────────────────────────────
Step 1 + 2: probe the upload across its whole length, then route it.

Three cheap signals:
  • speech_ratio    — Silero VAD (bundled with faster-whisper as ONNX, no
                      PyTorch): fraction of the audio that is speech.
  • text_density    — one frame every ~10 s through the text DETECTOR only
                      (PaddleOCR's DB detection model via RapidOCR/ONNX, no
                      recognition): fraction of sampled frames with real text.
  • screen_activity — fraction of frame pairs with small localised changes
                      (cursor, typing) as opposed to full scene changes.

Routing table:
  high speech + high text   → narrated_slides     ASR + OCR on slides (+VLM on charts)
  high speech + low text    → talking_head        ASR only
  low speech  + high activity → silent_screen_demo VLM on keyframes + OCR for code
  low speech  + high text   → silent_slides       OCR + VLM for diagrams
  low speech  + low text    → reject              "Not enough learnable content found."
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import logging
import os
import threading
import time
from dataclasses import asdict, dataclass, field
from typing import List, Optional, Tuple

import numpy as np

from services.media_quiz.media_io import VideoScan

logger = logging.getLogger(__name__)

SPEECH_HIGH = float(os.getenv("MEDIA_SPEECH_HIGH", "0.30"))
TEXT_HIGH = float(os.getenv("MEDIA_TEXT_HIGH", "0.40"))
ACTIVITY_HIGH = float(os.getenv("MEDIA_ACTIVITY_HIGH", "0.15"))
MIN_TEXT_AREA = 0.004        # text-box share of the frame for it to count as "has text"
MIN_TEXT_BOXES = 3

NARRATED_SLIDES = "narrated_slides"
TALKING_HEAD = "talking_head"
SILENT_SCREEN_DEMO = "silent_screen_demo"
SILENT_SLIDES = "silent_slides"
REJECT = "reject"

ROUTE_TOOLS = {
    NARRATED_SLIDES: ["asr", "ocr", "vlm(charts / low-OCR frames)"],
    TALKING_HEAD: ["asr"],
    SILENT_SCREEN_DEMO: ["vlm", "ocr"],
    SILENT_SLIDES: ["ocr", "vlm(diagrams)"],
    REJECT: [],
}

_ocr = None
_ocr_lock = threading.Lock()


def get_ocr():
    """Shared RapidOCR engine (PaddleOCR det/cls/rec models on ONNX Runtime)."""
    global _ocr
    if _ocr is None:
        with _ocr_lock:
            if _ocr is None:
                from rapidocr_onnxruntime import RapidOCR
                _ocr = RapidOCR()
    return _ocr


@dataclass
class ProbeResult:
    duration: float
    has_audio: bool
    has_video: bool
    speech_ratio: float = 0.0
    text_density: float = 0.0
    screen_activity: float = 0.0
    scene_changes: int = 0
    keyframes: int = 0
    content_type: str = REJECT
    tools: List[str] = field(default_factory=list)
    speech_regions: List[Tuple[float, float]] = field(default_factory=list)
    elapsed_s: float = 0.0

    def to_dict(self) -> dict:
        d = asdict(self)
        d.pop("speech_regions")
        for k in ("speech_ratio", "text_density", "screen_activity", "duration", "elapsed_s"):
            d[k] = round(d[k], 3)
        d["thresholds"] = {"speech_high": SPEECH_HIGH, "text_high": TEXT_HIGH, "activity_high": ACTIVITY_HIGH}
        return d


def speech_regions(audio: Optional[np.ndarray]) -> List[Tuple[float, float]]:
    if audio is None or not audio.size:
        return []
    from faster_whisper.vad import VadOptions, get_speech_timestamps

    ts = get_speech_timestamps(audio, VadOptions(min_silence_duration_ms=500, speech_pad_ms=200))
    return [(t["start"] / 16000.0, t["end"] / 16000.0) for t in ts]


def text_density(frames: List[np.ndarray]) -> float:
    if not frames:
        return 0.0
    det = get_ocr().text_detector
    hits = 0
    for f in frames:
        try:
            boxes, _ = det(f)
        except Exception as exc:
            logger.debug("[probe] text detector failed on a frame: %s", exc)
            continue
        if boxes is None or len(boxes) == 0:
            continue
        h, w = f.shape[:2]
        area = sum(float(np.ptp(b[:, 0]) * np.ptp(b[:, 1])) for b in boxes) / float(w * h)
        # A few lines of real text, or one large block (a title slide).
        if (len(boxes) >= MIN_TEXT_BOXES and area >= MIN_TEXT_AREA) or area >= MIN_TEXT_AREA * 4:
            hits += 1
    return hits / len(frames)


def route(speech: float, text: float, activity: float, has_video: bool) -> str:
    if speech >= SPEECH_HIGH:
        return NARRATED_SLIDES if (has_video and text >= TEXT_HIGH) else TALKING_HEAD
    if has_video and activity >= ACTIVITY_HIGH:
        return SILENT_SCREEN_DEMO
    if has_video and text >= TEXT_HIGH:
        return SILENT_SLIDES
    return REJECT


def probe(duration: float, has_audio: bool, has_video: bool,
          audio: Optional[np.ndarray], scan: Optional[VideoScan],
          regions: Optional[List[Tuple[float, float]]] = None) -> ProbeResult:
    """`regions` — precomputed speech spans (e.g. from YouTube captions) instead of running VAD."""
    t0 = time.perf_counter()
    res = ProbeResult(duration=duration, has_audio=bool(regions) or (has_audio and audio is not None),
                      has_video=has_video)

    if regions is not None:
        res.speech_regions = regions
        total = duration or (max(e for _, e in regions) if regions else 0.0)
    else:
        res.speech_regions = speech_regions(audio)
        total = audio.size / 16000.0 if audio is not None and audio.size else 0.0
    if total:
        res.speech_ratio = min(1.0, sum(e - s for s, e in res.speech_regions) / total)

    if scan is not None:
        res.text_density = text_density(scan.text_frames)
        res.screen_activity = scan.screen_activity
        res.scene_changes = len(scan.scene_changes)
        res.keyframes = len(scan.keyframes)

    res.content_type = route(res.speech_ratio, res.text_density, res.screen_activity, has_video and scan is not None)
    res.tools = ROUTE_TOOLS[res.content_type]
    res.elapsed_s = time.perf_counter() - t0
    logger.info("[probe] speech=%.2f text=%.2f activity=%.2f → %s",
                res.speech_ratio, res.text_density, res.screen_activity, res.content_type)
    return res
