"""
FILE: services/media_quiz/media_io.py
─────────────────────────────────────────────────────────────────────────────
Low-level media access for the media-quiz pipeline.

  • stream_info   — duration / has audio / has video via PyAV (container
                    duration, so variable-frame-rate phone recordings are not
                    mis-timed by frame_count / fps).
  • load_audio    — 16 kHz mono float32 via faster-whisper's PyAV decoder
                    (works on video containers too; no ffmpeg binary needed).
  • scan_video    — ONE pass over the whole video (not just the opening frames):
                    grey thumbnails for change detection, the LAST frame before
                    every scene change (the fully built slide — flaw 6), periodic
                    frames during localised on-screen activity (screen demos),
                    and one frame every ~10 s for the text-density probe.
                    Frame times come from the decoder's presentation timestamp
                    (CAP_PROP_POS_MSEC), not frame_index / fps (timestamp drift).
  • download_youtube — yt-dlp: captions + small video-only stream (+ audio only
                     when there are no captions); returns a MediaSource.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import logging
import os
import tempfile
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

logger = logging.getLogger(__name__)

SAMPLE_BUDGET = int(os.getenv("MEDIA_SCAN_SAMPLES", "600"))      # frames examined per video
TEXT_SAMPLE_EVERY_S = float(os.getenv("MEDIA_TEXT_SAMPLE_S", "10"))
TEXT_SAMPLE_MAX = 60
MAX_KEYFRAMES = int(os.getenv("MEDIA_MAX_KEYFRAMES", "40"))
FRAME_WIDTH = 960                                                 # stored frames are resized to this width

# A change is classified by how much of the frame it touches, not only how many
# pixels flip: a new white slide changes few pixels but spread over the whole
# frame, while a cursor, typing or one bullet appearing stays in a small box.
SCENE_CHANGE_FRAC = 0.22     # share of thumbnail pixels changed → scene change regardless of spread
SCENE_SPREAD = 0.15          # changed-pixel bounding box covers ≥15 % of the frame …
SCENE_MIN_FRAC = 0.01        # … and ≥1 % of pixels changed (a cursor jump is spread out but tiny)
LOCAL_CHANGE_MIN = 0.0008    # below this: noise / compression flicker
ACTIVITY_KEYFRAME_EVERY_S = 20.0

MEDIA_VIDEO_EXTS = {".mp4", ".mkv", ".webm", ".mov", ".avi", ".m4v", ".mpeg", ".mpg", ".3gp"}
MEDIA_AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".oga", ".opus", ".flac", ".wma"}


@dataclass
class StreamInfo:
    duration: float
    has_audio: bool
    has_video: bool


@dataclass
class Keyframe:
    t: float                 # timestamp of this frame
    t_start: float           # when this screen state began (previous scene change)
    t_end: float             # when it was replaced
    image: np.ndarray        # BGR, FRAME_WIDTH wide
    reason: str              # "scene_end" | "activity" | "final" | "uniform"
    ocr_conf: Optional[float] = None
    visual_score: float = 0.0   # edge density outside text → chart / table / diagram
    superseded: bool = False    # partial slide build — a later frame shows the same text and more


@dataclass
class VideoScan:
    duration: float
    samples: int
    scene_changes: List[float] = field(default_factory=list)
    local_changes: int = 0
    change_pairs: int = 0
    keyframes: List[Keyframe] = field(default_factory=list)
    text_frames: List[np.ndarray] = field(default_factory=list)

    @property
    def screen_activity(self) -> float:
        return self.local_changes / self.change_pairs if self.change_pairs else 0.0


def stream_info(path: str) -> StreamInfo:
    import av

    with av.open(path) as c:
        has_audio = any(s.type == "audio" for s in c.streams)
        video = [s for s in c.streams if s.type == "video"]
        # Cover art in an mp3 shows up as a single-frame "video" stream.
        has_video = any((s.frames or 0) != 1 and (s.average_rate or 0) for s in video)
        duration = (c.duration or 0) / 1_000_000
        if not duration:
            for s in c.streams:
                if s.duration and s.time_base:
                    duration = max(duration, float(s.duration * s.time_base))
    return StreamInfo(duration=float(duration), has_audio=has_audio, has_video=has_video)


def load_audio(path: str) -> Optional[np.ndarray]:
    from faster_whisper.audio import decode_audio

    try:
        audio = decode_audio(path, sampling_rate=16000)
        return audio if audio is not None and audio.size else None
    except Exception as exc:          # no audio stream / undecodable
        logger.info("[media] no decodable audio in %s: %s", os.path.basename(path), exc)
        return None


def _resize(frame: np.ndarray, width: int) -> np.ndarray:
    import cv2

    h, w = frame.shape[:2]
    if w <= width:          # never upscale: it only slows OCR down (a 360p stream stays 640 wide)
        return frame
    return cv2.resize(frame, (width, max(1, int(h * width / w))), interpolation=cv2.INTER_AREA)


def _thumb(frame: np.ndarray) -> np.ndarray:
    import cv2

    g = cv2.cvtColor(cv2.resize(frame, (160, 90), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(g, (3, 3), 0)


def _change(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    """(share of pixels changed, share of the frame covered by their bounding box)."""
    import cv2

    diff = (cv2.absdiff(a, b) > 25).astype(np.uint8)
    diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))   # drop speckle
    frac = float(diff.mean())
    if not frac:
        return 0.0, 0.0
    ys, xs = np.nonzero(diff)
    spread = (np.ptp(xs) + 1) * (np.ptp(ys) + 1) / float(diff.size)
    return frac, float(spread)


def scan_video(path: str, duration: float) -> Optional[VideoScan]:
    import cv2

    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return None
    try:
        step = max(0.5, duration / SAMPLE_BUDGET) if duration > 0 else 1.0
        text_every = max(TEXT_SAMPLE_EVERY_S, duration / TEXT_SAMPLE_MAX) if duration > 0 else TEXT_SAMPLE_EVERY_S
        scan = VideoScan(duration=duration, samples=0)

        prev_thumb = prev_frame = None
        prev_t = 0.0
        segment_start = 0.0
        next_text_t = 0.0
        last_activity_kf = -1e9
        target = 0.0
        # Sequential grab for short clips (cheap, exact); seek for long ones.
        sequential = duration <= 0 or duration < 240

        while True:
            if sequential:
                if not cap.grab():
                    break
                t = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                if t + 1e-6 < target:
                    continue
                ok, frame = cap.retrieve()
            else:
                if target > duration:
                    break
                cap.set(cv2.CAP_PROP_POS_MSEC, target * 1000.0)
                ok, frame = cap.read()
                t = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0 or target
            if not ok or frame is None:
                if sequential:
                    continue
                break
            target = t + step
            scan.samples += 1
            frame = _resize(frame, FRAME_WIDTH)
            thumb = _thumb(frame)

            if t >= next_text_t:
                scan.text_frames.append(frame)
                next_text_t = t + text_every

            if prev_thumb is not None:
                frac, spread = _change(thumb, prev_thumb)
                scan.change_pairs += 1
                if frac >= SCENE_CHANGE_FRAC or (frac >= SCENE_MIN_FRAC and spread >= SCENE_SPREAD):
                    scan.scene_changes.append(t)
                    # The last frame BEFORE the change is the fully built slide.
                    scan.keyframes.append(Keyframe(prev_t, segment_start, t, prev_frame, "scene_end"))
                    segment_start = t
                elif frac >= LOCAL_CHANGE_MIN:
                    scan.local_changes += 1
                    if t - last_activity_kf >= ACTIVITY_KEYFRAME_EVERY_S:
                        scan.keyframes.append(Keyframe(t, max(segment_start, t - ACTIVITY_KEYFRAME_EVERY_S),
                                                       t + ACTIVITY_KEYFRAME_EVERY_S, frame, "activity"))
                        last_activity_kf = t
            prev_thumb, prev_frame, prev_t = thumb, frame, t

        if prev_frame is not None:
            end = max(prev_t, duration)
            scan.keyframes.append(Keyframe(prev_t, segment_start, end, prev_frame, "final"))
            scan.duration = end
        scan.keyframes = _select_keyframes(scan.keyframes)
        return scan
    finally:
        cap.release()


def _select_keyframes(kfs: List[Keyframe]) -> List[Keyframe]:
    kfs = sorted(kfs, key=lambda k: k.t)
    # Near-duplicate removal: an activity frame inside a slide segment that also
    # ends in a scene_end frame adds little.
    out: List[Keyframe] = []
    for k in kfs:
        if out and abs(k.t - out[-1].t) < 2.0:
            if k.reason == "scene_end":
                out[-1] = k
            continue
        out.append(k)
    if len(out) <= MAX_KEYFRAMES:
        return out
    idx = np.linspace(0, len(out) - 1, MAX_KEYFRAMES).round().astype(int)
    return [out[i] for i in sorted(set(idx.tolist()))]


def encode_jpeg(image: np.ndarray, quality: int = 80) -> bytes:
    import cv2

    ok, buf = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    return buf.tobytes() if ok else b""


# ── YouTube ──────────────────────────────────────────────────────────────────

YOUTUBE_MAX_DURATION_S = int(os.getenv("MEDIA_YOUTUBE_MAX_DURATION_S", str(4 * 3600)))

# YouTube serves (almost) no combined audio+video files any more, and merging
# separate streams needs an ffmpeg binary. So the streams are fetched separately:
#   • video-only, ≤360p H.264  → frames for the probe / OCR / VLM (small: ~0.5 MB/min)
#   • captions (manual first, then the ORIGINAL-language auto captions — never
#     the machine-translated tracks) → speech evidence without running Whisper
#   • audio-only (smallest m4a) → only when there are no usable captions
_YT_VIDEO_FORMAT = ("bv*[height<=360][ext=mp4][vcodec^=avc1]/bv*[height<=480][ext=mp4][vcodec^=avc1]"
                    "/bv*[height<=480][ext=mp4]/bv*[height<=480]/b[height<=480]/wv*")
_YT_AUDIO_FORMAT = "wa[ext=m4a]/ba[ext=m4a]/wa/ba"


class MediaInputError(ValueError):
    """User-facing problem with the supplied media (bad link, too long, unreadable)."""


@dataclass
class Caption:
    start: float
    end: float
    text: str


@dataclass
class MediaSource:
    """What the pipeline processes: one uploaded file, or YouTube's separate parts."""
    title: str
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    captions: Optional[List[Caption]] = None
    caption_kind: Optional[str] = None      # "manual" | "auto"
    caption_lang: Optional[str] = None
    duration: Optional[float] = None
    notes: List[str] = field(default_factory=list)

    @classmethod
    def from_file(cls, path: str, title: str) -> "MediaSource":
        return cls(title=title, video_path=path, audio_path=path)


def is_youtube_url(url: str) -> bool:
    from urllib.parse import urlparse

    try:
        host = (urlparse(url.strip()).hostname or "").lower()
    except ValueError:
        return False
    return host in {"youtu.be", "youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}


def _yt_opts(**extra) -> dict:
    opts = {"quiet": True, "no_warnings": True, "noprogress": True, "noplaylist": True,
            # A JS runtime is needed for YouTube's signature challenges; node is common on dev machines.
            "js_runtimes": {"deno": {}, "node": {}}, "retries": 3, "socket_timeout": 30}
    opts.update(extra)
    return opts


def _pick_captions(info: dict) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """(url of a json3 track, kind, lang) — manual subtitles first, then original-language auto captions."""
    video_lang = (info.get("language") or "").split("-")[0].lower()

    def json3(tracks):
        return next((t["url"] for t in tracks or [] if t.get("ext") == "json3" and t.get("url")), None)

    manual = {k: v for k, v in (info.get("subtitles") or {}).items() if k != "live_chat"}
    order = sorted(manual, key=lambda k: (k.split("-")[0].lower() != video_lang, not k.startswith("en"), k))
    for lang in order:
        url = json3(manual[lang])
        if url:
            return url, "manual", lang
    auto = info.get("automatic_captions") or {}
    # "<lang>-orig" is the ASR of the spoken language; plain "<lang>" tracks are machine translations.
    candidates = [k for k in auto if k.endswith("-orig")] + ([video_lang] if video_lang in auto else [])
    for lang in candidates:
        url = json3(auto[lang])
        if url:
            return url, "auto", lang.replace("-orig", "")
    return None, None, None


def _parse_json3(raw: bytes) -> List[Caption]:
    import json

    data = json.loads(raw.decode("utf-8", errors="replace"))
    out: List[Caption] = []
    for ev in data.get("events", []):
        segs = ev.get("segs")
        if not segs or "tStartMs" not in ev:
            continue
        text = " ".join("".join(s.get("utf8", "") for s in segs).split())
        if not text or (text.startswith("[") and text.endswith("]")):    # [Music], [Applause]
            continue
        start = ev["tStartMs"] / 1000.0
        out.append(Caption(start, start + ev.get("dDurationMs", 2000) / 1000.0, " ".join(text.split())))
    # Auto captions overlap (rolling display): clip each cue at the next one's start.
    for a, b in zip(out, out[1:]):
        a.end = max(a.start + 0.2, min(a.end, b.start))
    return out


def download_youtube(url: str, workdir: str) -> MediaSource:
    try:
        import yt_dlp
    except ImportError as exc:
        raise RuntimeError("yt-dlp is not installed (pip install -r requirements-media.txt)") from exc

    if not is_youtube_url(url):
        raise MediaInputError("Only YouTube links (youtube.com / youtu.be) are supported.")

    try:
        with yt_dlp.YoutubeDL(_yt_opts()) as ydl:
            info = ydl.extract_info(url.strip(), download=False)
            if info.get("_type") == "playlist" or info.get("entries"):
                raise MediaInputError("Please paste a link to a single video, not a playlist.")
            src = MediaSource(title=str(info.get("title") or "YouTube video"),
                              duration=float(info.get("duration") or 0) or None)
            if info.get("is_live"):
                raise MediaInputError("Live streams are not supported.")
            if (src.duration or 0) > YOUTUBE_MAX_DURATION_S:
                raise MediaInputError(f"Video is {src.duration / 60:.0f} min long; the limit is "
                                      f"{YOUTUBE_MAX_DURATION_S // 60} min.")

            cap_url, kind, lang = _pick_captions(info)
            if cap_url:
                try:
                    caps = _parse_json3(ydl.urlopen(cap_url).read())
                    if caps:
                        src.captions, src.caption_kind, src.caption_lang = caps, kind, lang
                        src.notes.append(f"speech from YouTube {kind} captions ({lang})")
                except Exception as exc:
                    logger.warning("[youtube] captions failed (%s) — falling back to audio + ASR", exc)
    except MediaInputError:
        raise
    except Exception as exc:
        raise MediaInputError(f"Could not read that YouTube link: {exc}") from exc

    def fetch(fmt: str, prefix: str) -> Optional[str]:
        try:
            with yt_dlp.YoutubeDL(_yt_opts(format=fmt, outtmpl=os.path.join(workdir, prefix + "_%(id)s.%(ext)s"))) as y:
                got = y.extract_info(url.strip(), download=True)
                path = y.prepare_filename(got)
            return path if os.path.exists(path) and os.path.getsize(path) > 0 else None
        except Exception as exc:
            logger.warning("[youtube] %s download failed: %s", prefix, exc)
            return None

    src.video_path = fetch(_YT_VIDEO_FORMAT, "v")
    if not src.video_path:
        src.notes.append("video frames unavailable — speech only")
    if not src.captions:
        src.audio_path = fetch(_YT_AUDIO_FORMAT, "a")
        if src.audio_path:
            src.notes.append("speech transcribed from the audio track (no captions)")
    if not src.video_path and not src.audio_path and not src.captions:
        raise MediaInputError("Could not download that YouTube video (it may be private, age-restricted "
                              "or region-blocked).")
    return src


def temp_dir() -> str:
    base = os.path.join(os.path.dirname(__file__), "..", "..", "temp_uploads")
    os.makedirs(base, exist_ok=True)
    return tempfile.mkdtemp(prefix="media_", dir=os.path.normpath(base))
