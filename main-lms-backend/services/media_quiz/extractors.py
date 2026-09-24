"""
FILE: services/media_quiz/extractors.py
─────────────────────────────────────────────────────────────────────────────
The three evidence producers. Each writes to the shared Timeline.

ASR (faster-whisper)
  • Speech regions from the probe's Silero VAD are merged into ≤28 s windows;
    the language is detected PER WINDOW (flaw 5: Hinglish lecture with an
    English intro) and every window is transcribed with task="transcribe"
    (never "translate").
  • Whisper's own signals gate each segment (standard cut-offs):
        no_speech_prob < 0.6    really speech, not music / noise
        avg_logprob   > -1.0    model reasonably sure of the words
        compression_ratio < 2.4 not a repetitive hallucination loop
    plus a short blocklist of the classic outro hallucinations
    ("thank you for watching") that show up over music (flaw 1).
  • confidence = exp(avg_logprob) · (1 − no_speech_prob).

OCR (RapidOCR = PaddleOCR det/cls/rec on ONNX Runtime)
  • Full recognition on the selected keyframes only; per-line scores give the
    evidence confidence. Consecutive near-identical screens are merged.
  • Also scores "visual" content (edge density outside text boxes) so charts,
    tables and diagrams can be sent to the VLM (flaw 3).

VLM (flaws 2, 3)
  • MEDIA_VLM_BACKEND=gemini  → cloud Gemini vision. DEMO-ONLY choice (flaw 12):
    frames leave the machine. Reported as such in every response.
  • MEDIA_VLM_BACKEND=ollama  → local Qwen2.5-VL (MEDIA_VLM_MODEL, default
    qwen2.5vl:3b) through Ollama — the offline path; needs a GPU to be quick.
  • MEDIA_VLM_BACKEND=none    → disabled (silent demos then fall back to OCR).
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import asyncio
import logging
import math
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple

import numpy as np

from services.media_quiz.evidence import Timeline
from services.media_quiz.llm import LLMUnavailable, gemini_json, gemini_key, ollama_vision_json
from services.media_quiz.media_io import Keyframe, encode_jpeg
from services.media_quiz.probe import get_ocr, map_frames

logger = logging.getLogger(__name__)

WHISPER_MODEL = os.getenv("MEDIA_WHISPER_MODEL", "small")
WHISPER_DEVICE = os.getenv("MEDIA_WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE = os.getenv("MEDIA_WHISPER_COMPUTE", "int8")
# CTranslate2 defaults to 4 threads and one worker, which leaves most of a modern CPU
# idle. Several workers decode speech windows in parallel (each window is independent:
# condition_on_previous_text=False), and some cores are left free for OCR, which
# runs concurrently on the visual routes.
_CPUS = os.cpu_count() or 4
WHISPER_WORKERS = max(1, int(os.getenv("MEDIA_WHISPER_WORKERS", "3" if _CPUS >= 12 else "2" if _CPUS >= 6 else "1")))
WHISPER_THREADS = max(1, int(os.getenv("MEDIA_WHISPER_THREADS", str(max(2, min(8, _CPUS // (WHISPER_WORKERS + 1)))))))
WINDOW_MAX_S = 28.0
# CPU Whisper runs at roughly real time, so long lectures are transcribed on an
# evenly spread SAMPLE of speech windows up to this many seconds (coverage of the
# whole video beats a perfect transcript of its first minutes).
ASR_BUDGET_S = float(os.getenv("MEDIA_ASR_BUDGET_S", "150"))
# "gemini": a transcript Gemini made from the public video (ytgemini) — a model's ASR,
# so it is trusted like YouTube's own auto captions.
CAPTION_CONFIDENCE = {"manual": 0.92, "auto": 0.72, "gemini": 0.72}
CAPTION_PIECE_S = 20.0

OCR_LINE_MIN_SCORE = 0.5
OCR_LOW_CONF = 0.75           # below this, a keyframe also goes to the VLM
VISUAL_HIGH = 0.05            # edge density outside text → chart / table / diagram
VLM_MAX_FRAMES = int(os.getenv("MEDIA_VLM_MAX_FRAMES", "24"))
VLM_BATCH = 4
VLM_CONF_CAP = 0.85           # a VLM description is never treated as more certain than this

_HALLUCINATIONS = re.compile(
    r"thank(s| you) (so much )?for watching|please subscribe|like and subscribe|subscribe to (my|our|the) channel"
    r"|see you (in the )?next (video|time)|देखने के लिए धन्यवाद|सब्सक्राइब",
    re.I,
)
_DEVANAGARI = re.compile(r"[ऀ-ॿ]")

_whisper = None
_whisper_lock = threading.Lock()


def get_whisper():
    global _whisper
    if _whisper is None:
        with _whisper_lock:
            if _whisper is None:
                from faster_whisper import WhisperModel
                logger.info("[asr] loading faster-whisper '%s' (%s/%s, %d workers x %d threads)", WHISPER_MODEL,
                            WHISPER_DEVICE, WHISPER_COMPUTE, WHISPER_WORKERS, WHISPER_THREADS)
                _whisper = WhisperModel(WHISPER_MODEL, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE,
                                        cpu_threads=WHISPER_THREADS, num_workers=WHISPER_WORKERS)
    return _whisper


def vlm_backend() -> str:
    b = os.getenv("MEDIA_VLM_BACKEND", "").strip().lower()
    if b in {"gemini", "ollama", "none"}:
        return b
    return "gemini" if gemini_key() else "none"


def vlm_label() -> str:
    b = vlm_backend()
    if b == "gemini":
        return "gemini (cloud vision — demo-only; frames leave the machine)"
    if b == "ollama":
        return f"ollama:{os.getenv('MEDIA_VLM_MODEL', 'qwen2.5vl:3b')} (offline)"
    return "disabled"


def lang_of(text: str) -> str:
    return "hi" if len(_DEVANAGARI.findall(text)) > 0.2 * max(1, len(text.replace(" ", ""))) else "en"


# ── ASR ──────────────────────────────────────────────────────────────────────

def _windows(regions: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    out: List[Tuple[float, float]] = []
    for s, e in regions:
        while e - s > WINDOW_MAX_S:                       # split very long speech runs
            out.append((s, s + WINDOW_MAX_S))
            s += WINDOW_MAX_S
        if out and e - out[-1][0] <= WINDOW_MAX_S and s - out[-1][1] < 1.5:
            out[-1] = (out[-1][0], e)
        else:
            out.append((s, e))
    return out


def segment_ok(seg) -> Optional[str]:
    """None if the segment passes Whisper's quality gates, else the drop reason."""
    if seg.no_speech_prob >= 0.6:
        return "asr_no_speech"
    if seg.avg_logprob <= -1.0:
        return "asr_low_logprob"
    if seg.compression_ratio >= 2.4:
        return "asr_repetition_loop"
    text = seg.text.strip()
    if len(text) < 80 and _HALLUCINATIONS.search(text):
        return "asr_outro_hallucination"
    return None


def _budget(windows: List[Tuple[float, float]], budget_s: float) -> Tuple[List[Tuple[float, float]], float]:
    total = sum(e - s for s, e in windows)
    if total <= budget_s or not windows:
        return windows, 1.0
    k = max(1, int(len(windows) * budget_s / total))
    idx = sorted(set(np.linspace(0, len(windows) - 1, k).round().astype(int).tolist()))
    picked = [windows[i] for i in idx]
    return picked, sum(e - s for s, e in picked) / total


def transcribe(audio: np.ndarray, regions: List[Tuple[float, float]], timeline: Timeline,
               budget_s: float = ASR_BUDGET_S) -> Dict:
    """Per-window language detection + transcription. Returns {languages_s, speech_coverage, windows}."""
    model = get_whisper()
    langs: Dict[str, float] = {}
    windows, coverage = _budget(_windows(regions), budget_s)
    beam = 3 if coverage >= 1.0 else 1          # sampled long media: favour speed
    jobs = []
    for ws, we in windows:
        clip = audio[int(ws * 16000):int(we * 16000)]
        if clip.size >= 8000:                              # skip < 0.5 s
            jobs.append((ws, clip))

    def decode(job):
        # language=None → Whisper detects the language of THIS window (code-switching).
        # The anti-repetition settings stop the decoder looping on accented / Hinglish
        # speech: loops are rejected by the gates anyway, but cost ~2× real time.
        segments, info = model.transcribe(
            job[1], task="transcribe", language=None, beam_size=beam, condition_on_previous_text=False,
            vad_filter=False, temperature=[0.0, 0.4], no_repeat_ngram_size=3, repetition_penalty=1.15,
            max_new_tokens=224,
        )
        return list(segments), info             # segments are lazy: decode inside the worker

    # Windows are independent, so they decode in parallel; results are written in
    # window order, which keeps evidence ids identical to a sequential run.
    if WHISPER_WORKERS > 1 and len(jobs) > 1:
        with ThreadPoolExecutor(max_workers=WHISPER_WORKERS, thread_name_prefix="asr") as pool:
            decoded = list(pool.map(decode, jobs))
    else:
        decoded = [decode(j) for j in jobs]

    for (ws, _), (segments, info) in zip(jobs, decoded):
        lang_prob = float(info.language_probability or 0.0)
        used_lang = info.language or "en"
        for seg in segments:
            reason = segment_ok(seg)
            if reason:
                timeline.drop(reason)
                continue
            conf = math.exp(seg.avg_logprob) * (1.0 - seg.no_speech_prob)
            ev = timeline.add(ws + seg.start, ws + seg.end, "asr", seg.text, conf, lang=used_lang,
                              lang_prob=round(lang_prob, 3))
            if ev:
                langs[used_lang] = langs.get(used_lang, 0.0) + (ev.t_end - ev.t_start)
    return {"languages_s": {k: round(v, 1) for k, v in langs.items()}, "speech_coverage": round(coverage, 3),
            "windows": len(windows)}


def add_captions(captions, kind: str, lang: str, timeline: Timeline) -> int:
    """YouTube captions → speech evidence, merged into ≤20 s pieces ending on sentence breaks."""
    conf = CAPTION_CONFIDENCE.get(kind, 0.7)
    n, buf = 0, []

    def flush():
        nonlocal n
        if buf:
            text = " ".join(c.text for c in buf)
            if not (len(text) < 80 and _HALLUCINATIONS.search(text)):
                ev = timeline.add(buf[0].start, buf[-1].end, "asr", text, conf,
                                  lang="hi" if lang_of(text) == "hi" else (lang or "en"),
                                  via=f"youtube_{kind}_captions")
                n += 1 if ev else 0
            buf.clear()

    for c in captions:
        if buf and (c.start - buf[0].start > CAPTION_PIECE_S or c.start - buf[-1].end > 2.0):
            flush()
        buf.append(c)
        if c.text.rstrip().endswith((".", "?", "!", "।")) and c.end - buf[0].start > 6:
            flush()
    flush()
    return n


def caption_regions(captions) -> List[Tuple[float, float]]:
    out: List[Tuple[float, float]] = []
    for c in captions:
        if out and c.start - out[-1][1] < 1.0:
            out[-1] = (out[-1][0], max(out[-1][1], c.end))
        else:
            out.append((c.start, c.end))
    return out


def transcribe_naive(audio: np.ndarray) -> str:
    """BASELINE for the eval only: one language, no VAD, no quality gates."""
    segments, _ = get_whisper().transcribe(audio, task="transcribe", beam_size=5)
    return " ".join(s.text.strip() for s in segments)


# ── OCR ──────────────────────────────────────────────────────────────────────

def _visual_score(image: np.ndarray, boxes: List[np.ndarray]) -> float:
    import cv2

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mask = np.ones(gray.shape, np.uint8)
    for b in boxes:
        x0, y0 = np.maximum(b.min(axis=0).astype(int) - 4, 0)
        x1, y1 = b.max(axis=0).astype(int) + 4
        mask[y0:y1, x0:x1] = 0
    edges = cv2.Canny(gray, 80, 160) > 0
    free = mask.sum()
    return float((edges & (mask > 0)).sum() / free) if free else 0.0


def _words(t: str) -> set:
    return set(re.findall(r"\w+", t.lower()))


def ocr_keyframes(keyframes: List[Keyframe], timeline: Timeline) -> Dict[int, List[str]]:
    """OCR every keyframe. Returns keyframe index → evidence ids."""
    eng = get_ocr()
    out: Dict[int, List[str]] = {}
    # Frames are recognised in parallel; everything that touches the timeline stays
    # below, in keyframe order.
    read: List[Optional[Tuple[str, float, int]]] = []
    for res, weak_lines in map_frames(lambda kf: _ocr_one(eng, kf), keyframes):
        if weak_lines:
            timeline.drop("ocr_line_low_score", weak_lines)
        read.append(res)

    # Slide builds (flaw 6): a frame whose words all reappear in the next frame of
    # the same screen segment is a partial build — keep only the fully built one.
    for i in range(len(keyframes) - 1):
        a, b = read[i], read[i + 1]
        if a and b and keyframes[i].t_start == keyframes[i + 1].t_start:
            wa, wb = _words(a[0]), _words(b[0])
            if wa and len(wa & wb) / len(wa) >= 0.9:
                keyframes[i].superseded = True
                keyframes[i + 1].t_start = min(keyframes[i + 1].t_start, keyframes[i].t_start)
                timeline.drop("ocr_partial_slide_build")

    prev_ev = None
    for i, kf in enumerate(keyframes):
        if not read[i] or kf.superseded:
            continue
        text, conf, n_lines = read[i]
        # Same screen as the previous keyframe (cursor moved, slide re-shown): extend it.
        if prev_ev is not None:
            a, b = _words(prev_ev.text), _words(text)
            if a and b and len(a & b) / len(a | b) >= 0.9:
                prev_ev.t_end = max(prev_ev.t_end, kf.t_end)
                out[i] = [prev_ev.id]
                continue
        ev = timeline.add(kf.t_start, kf.t_end, "ocr", text, conf, lang=lang_of(text),
                          frame_t=round(kf.t, 2), lines=n_lines)
        if ev:
            out[i] = [ev.id]
            prev_ev = ev
    return out


def _ocr_one(eng, kf: Keyframe) -> Tuple[Optional[Tuple[str, float, int]], int]:
    """Recognise one keyframe → ((text in reading order, confidence, line count) or None,
    number of lines dropped for a low score). Thread-safe: touches only this keyframe."""
    try:
        result, _ = eng(kf.image)
    except Exception as exc:
        logger.warning("[ocr] keyframe %.1fs failed: %s", kf.t, exc)
        result = None
    lines, weak = [], 0
    for box, text, score in result or []:
        score = float(score)
        text = str(text).strip()
        if score >= OCR_LINE_MIN_SCORE and len(text) >= 2:
            lines.append((np.asarray(box, dtype=float), text, score))
        else:
            weak += 1
    kf.visual_score = _visual_score(kf.image, [l[0] for l in lines])
    if not lines:
        kf.ocr_conf = None
        return None, weak
    lines.sort(key=lambda l: (round(l[0][:, 1].min() / 12), l[0][:, 0].min()))
    weights = np.array([len(l[1]) for l in lines], dtype=float)
    kf.ocr_conf = float(np.average([l[2] for l in lines], weights=weights))
    return (" / ".join(l[1] for l in lines), kf.ocr_conf, len(lines)), weak


def needs_vlm(kf: Keyframe, content_type: str) -> bool:
    if kf.superseded:
        return False
    if content_type == "silent_screen_demo":
        return True
    return kf.ocr_conf is None or kf.ocr_conf < OCR_LOW_CONF or kf.visual_score >= VISUAL_HIGH


# ── VLM ──────────────────────────────────────────────────────────────────────

_VLM_PROMPT = (
    "You are documenting a training video for civil servants of India's Ministry of Statistics (MoSPI). "
    "For EACH image below (in order; timestamps given), describe precisely what a trainee can learn from it: "
    "the application or document shown, the data, table headers, chart type/axes/trend, formulas, code, and — "
    "comparing with the previous frame — the action the user is performing (e.g. 'dragging Month into Columns "
    "of a pivot table'). Only state values you can actually read; never guess numbers. "
    "If a frame has nothing learnable (blank, logo, a face only, decorative), say so with kind 'blank'.\n"
    'Return JSON: {"frames":[{"index":0,"kind":"slide|chart|table|code|spreadsheet|ui|diagram|blank",'
    '"description":"...","action":"... or empty","confidence":0.0-1.0}]}'
)


def _vlm_item_to_evidence(item: dict, kf: Keyframe, timeline: Timeline, backend: str) -> Optional[str]:
    if not isinstance(item, dict):
        return None
    kind = str(item.get("kind", "")).lower()
    desc = str(item.get("description", "")).strip()
    action = str(item.get("action", "")).strip()
    try:
        conf = float(item.get("confidence", 0.6))
    except (TypeError, ValueError):
        conf = 0.6
    if kind == "blank" or len(desc) < 15:
        timeline.drop("vlm_blank_frame")
        return None
    text = desc + (f" Action: {action}" if action and action.lower() not in {"none", "n/a"} else "")
    ev = timeline.add(kf.t_start, kf.t_end, "vlm", text, min(conf, VLM_CONF_CAP), lang=lang_of(text),
                      frame_t=round(kf.t, 2), kind=kind, backend=backend)
    return ev.id if ev else None


async def describe_keyframes(items: List[Tuple[int, Keyframe]], timeline: Timeline) -> Dict[int, List[str]]:
    backend = vlm_backend()
    out: Dict[int, List[str]] = {}
    if backend == "none" or not items:
        return out
    if len(items) > VLM_MAX_FRAMES:
        pick = np.linspace(0, len(items) - 1, VLM_MAX_FRAMES).round().astype(int)
        items = [items[i] for i in sorted(set(pick.tolist()))]

    if backend == "ollama":
        for idx, kf in items:
            try:
                data = await ollama_vision_json(_VLM_PROMPT.replace("EACH image below", "the image") +
                                                "\nReturn a single frame object.", encode_jpeg(kf.image))
                item = (data.get("frames") or [data])[0] if isinstance(data, dict) else data
                eid = _vlm_item_to_evidence(item, kf, timeline, backend)
                if eid:
                    out.setdefault(idx, []).append(eid)
            except Exception as exc:
                logger.warning("[vlm] ollama frame %.1fs failed: %s", kf.t, exc)
                timeline.drop("vlm_error")
        return out

    async def run_batch(batch: List[Tuple[int, Keyframe]]):
        stamps = ", ".join(f"image {j}: t={kf.t:.0f}s" for j, (_, kf) in enumerate(batch))
        try:
            data = await gemini_json(f"{_VLM_PROMPT}\nImages: {stamps}",
                                     images=[encode_jpeg(kf.image) for _, kf in batch], temperature=0.1)
        except LLMUnavailable as exc:
            logger.warning("[vlm] gemini batch failed: %s", exc)
            timeline.drop("vlm_error", len(batch))
            return
        frames = data.get("frames", []) if isinstance(data, dict) else data if isinstance(data, list) else []
        for j, item in enumerate(frames):
            try:
                pos = int(item.get("index", j))
            except (TypeError, ValueError, AttributeError):
                pos = j
            if 0 <= pos < len(batch):
                idx, kf = batch[pos]
                eid = _vlm_item_to_evidence(item, kf, timeline, backend)
                if eid:
                    out.setdefault(idx, []).append(eid)

    batches = [items[i:i + VLM_BATCH] for i in range(0, len(items), VLM_BATCH)]
    sem = asyncio.Semaphore(3)

    async def guarded(b):
        async with sem:
            await run_batch(b)

    await asyncio.gather(*(guarded(b) for b in batches))
    return out
