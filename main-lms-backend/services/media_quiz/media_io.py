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

import json
import logging
import os
import re
import tempfile
import threading
import time
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
    caption_kind: Optional[str] = None      # "manual" | "auto" | "gemini"
    caption_lang: Optional[str] = None
    duration: Optional[float] = None
    notes: List[str] = field(default_factory=list)
    # On-screen text (slides, code, formulas) read by Gemini when this host got no
    # video frames to OCR — see ytgemini.py. Used by the pipeline in place of OCR.
    screen_text: Optional[List[Caption]] = None

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


# YouTube blocks datacenter IPs with "Sign in to confirm you're not a bot", and the
# block depends on which InnerTube player client asks. So extraction is retried over
# a chain of clients (one attempt each, in order) before giving up; a cookies.txt
# export or an outbound proxy fixes the cases no client gets through.
#
# The two failures are *different* and must not be conflated (this is what broke the
# deployed server): a client can be walled at the metadata stage ("not a bot"), or it
# can hand over metadata and captions perfectly well while serving **no downloadable
# formats**, because on an untrusted IP YouTube gates the media URLs behind a PO
# token. The second case is not a block — captions alone are enough for a quiz — so
# format availability is never allowed to decide whether a client "worked".
YOUTUBE_PLAYER_CLIENTS = os.getenv(
    "MEDIA_YOUTUBE_PLAYER_CLIENTS",
    # android_vr and ios are the ones that still hand out media URLs on datacenter IPs;
    # the web family usually answers with metadata + captions but no formats.
    "default,android_vr,ios,tv_simply,web_embedded,mweb")
YOUTUBE_COOKIES_FILE = os.getenv("MEDIA_YOUTUBE_COOKIES_FILE", "").strip()
# A server has no browser to export from and no convenient way to receive a file:
# the repo is reset --hard on every deploy and .env is the only writable, persistent,
# gitignored thing on it. So cookies.txt can also arrive as one base64 line in .env.
YOUTUBE_COOKIES_B64 = os.getenv("MEDIA_YOUTUBE_COOKIES_B64", "").strip()
YOUTUBE_COOKIES_BROWSER = os.getenv("MEDIA_YOUTUBE_COOKIES_FROM_BROWSER", "").strip()
YOUTUBE_PROXY = os.getenv("MEDIA_YOUTUBE_PROXY", "").strip()
# Metadata probes are cheap, and behind each one there is a whole chain of clients and
# then the relay tier, so a client that stumbles is not worth three retries — those
# triple the wall time of a link this host was never going to be served.
PROBE_RETRIES = int(os.getenv("MEDIA_YOUTUBE_PROBE_RETRIES", "1"))
PROBE_WORKERS = int(os.getenv("MEDIA_YOUTUBE_PROBE_WORKERS", "5"))
PROBE_DEADLINE_S = float(os.getenv("MEDIA_YOUTUBE_PROBE_DEADLINE_S", "45"))
# Fetching the same link twice (a learner retrying at another difficulty, a demo
# replaying one video) should not re-download anything: the captions and the 360p
# stream are cached on disk per video id and reused until the TTL expires.
YOUTUBE_CACHE_TTL_S = int(os.getenv("MEDIA_YOUTUBE_CACHE_TTL_S", "86400"))
# Optional bgutil PO-token provider (`docker run -p 4416:4416 brainicism/bgutil-ytdlp-pot-provider`
# plus `pip install bgutil-ytdlp-pot-provider`). With it the web clients get their
# formats back on a datacenter IP, which restores video frames / OCR.
YOUTUBE_POT_URL = os.getenv("MEDIA_YOUTUBE_POT_URL", "").strip()
WATCH_PAGE_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                 "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")

YOUTUBE_BLOCKED_MESSAGE = (
    "YouTube is blocking this server (its anti-bot check) and would not return the "
    "video's captions or audio. Upload the video or audio file instead — that path is "
    "unaffected."
)
# Ordered by what actually fixes a datacenter host, cheapest first. Run the diagnosis
# before any of them: it says which of the three states this host is in, and two of
# these are answers to only one of those states.
ADMIN_NEXT_STEPS = (
    " (Server admin: run GET /api/v1/rag/media/youtube/diagnose to see which wall this is, "
    "then set GEMINI_API_KEY (Gemini reads public videos on Google's side — works from any IP), "
    "deploy/oracle/youtube-access.sh --pot (free, fixes gated formats), "
    "--relay <kind>:<url of an instance you run> (free, fixes a refused IP), "
    "or --cookies / --proxy.)"
)
YOUTUBE_STALE_COOKIES_MESSAGE = (
    "YouTube rejected this server's saved sign-in — the cookies have expired. Upload the "
    "video or audio file instead. (Server admin: export a fresh cookies.txt and update "
    "MEDIA_YOUTUBE_COOKIES_B64; YouTube invalidates them when the account is used elsewhere.)"
)


def _relay_trace(relay: Optional[dict]) -> str:
    """One clause describing the relay tier's attempt. Without it the learner (and the
    admin reading the same sentence) cannot tell the tier from a tier that never ran,
    which is the first thing anyone asks when a deploy does not change the error."""
    if not relay or not relay.get("tried"):
        return (" The open relay instances are switched off on this server."
                if relay is not None and not relay.get("enabled") else "")
    n = relay["tried"]
    if relay.get("walled"):
        return (f" {n} public relay instances were tried too, and YouTube refused those "
                "servers for the same reason — they are in the same datacenter address space.")
    return f" {n} public relay instances were tried too, and none could serve it."


def _gemini_trace(relay: Optional[dict]) -> str:
    gem = (relay or {}).get("gemini")
    if not gem:
        return ""
    if not gem.get("enabled"):
        return " Gemini's YouTube reader is not configured on this server (GEMINI_API_KEY)."
    if gem.get("errors"):
        return f" Gemini could not read it either ({gem['errors'][0][:160]}) — it reads public videos only."
    return " Gemini could not read it either — it reads public videos only."


def _no_speech_message(relay: Optional[dict] = None) -> str:
    if has_cookies():
        return YOUTUBE_STALE_COOKIES_MESSAGE
    return YOUTUBE_NO_SPEECH_MESSAGE + _relay_trace(relay) + _gemini_trace(relay) + ADMIN_NEXT_STEPS


def _blocked_message(relay: Optional[dict] = None) -> str:
    # Configured-but-refused is a different job from never-configured: one needs a fresh
    # export, the other needs a first one. Saying "set cookies" to an admin who already
    # did sends them looking in the wrong place.
    if has_cookies():
        return YOUTUBE_STALE_COOKIES_MESSAGE
    return YOUTUBE_BLOCKED_MESSAGE + _relay_trace(relay) + _gemini_trace(relay) + ADMIN_NEXT_STEPS
# Not "this video has no captions": on a walled host YouTube returns the title and
# withholds the caption tracks, so blaming the video sends the learner to look for a
# different one when every video will do the same thing from this server.
YOUTUBE_NO_SPEECH_MESSAGE = (
    "YouTube gave this server the video's details but refused its captions, audio and "
    "video (its anti-bot check), so there is nothing to build questions from. Upload the "
    "video or audio file instead — that path is unaffected."
)
_BLOCKED_MARKERS = ("not a bot", "sign in to confirm", "confirm your age", "use --cookies",
                    "cookies-from-browser", "too many requests", "http error 429",
                    "failed to extract any player response")
# Not a block: YouTube answered, but withheld the media URLs from this IP. Captions still work.
_GATED_MARKERS = ("no video formats found", "requested format is not available",
                  "only images are available", "po token", "missing a url")
# The video itself is the problem — no other player client will do better.
_FATAL_MARKERS = ("private video", "removed by the uploader", "account associated with this video",
                  "members-only", "join this channel", "requires payment", "video is unavailable",
                  "not available in your country", "who has blocked it on copyright")


def _yt_message(exc: BaseException) -> str:
    """yt-dlp errors are multi-line and full of wiki links — keep the sentence that matters."""
    msg = " ".join(str(exc).split())
    msg = re.sub(r"^ERROR:\s*", "", msg)
    msg = re.sub(r"^\[[^\]]+\]\s*[\w-]{3,24}:\s*", "", msg)       # "[youtube] dMRDzicSvXk: "
    msg = re.sub(r"^\[[^\]]+\]\s*", "", msg)                      # "[youtube] " (captured via the logger)
    msg = re.sub(r"\s*(?:See|Also see)?\s*https?://\S+", "", msg)
    return " ".join(msg.split())[:300] or exc.__class__.__name__


def _is_blocked(exc: BaseException) -> bool:
    low = str(exc).lower()
    return any(m in low for m in _BLOCKED_MARKERS)


def _is_gated(exc: BaseException) -> bool:
    """YouTube answered but withheld the media URLs (PO token). Captions may still work."""
    low = str(exc).lower()
    return any(m in low for m in _GATED_MARKERS)


def _is_fatal(exc: BaseException) -> bool:
    """Something about the video itself — retrying other player clients is pointless."""
    low = str(exc).lower()
    return any(m in low for m in _FATAL_MARKERS)


def cookies_path() -> Optional[str]:
    """The cookies.txt yt-dlp should use, materialising MEDIA_YOUTUBE_COOKIES_B64 onto
    disk the first time. yt-dlp writes refreshed cookies back, so it needs a real file
    in a directory that survives a deploy — not a temp file."""
    if YOUTUBE_COOKIES_FILE:
        return YOUTUBE_COOKIES_FILE if os.path.exists(YOUTUBE_COOKIES_FILE) else None
    if not YOUTUBE_COOKIES_B64:
        return None
    global _COOKIES_CACHE
    if _COOKIES_CACHE:
        return _COOKIES_CACHE
    import base64

    path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".yt-cookies.txt"))
    try:
        raw = base64.b64decode(YOUTUBE_COOKIES_B64, validate=False)
        if b"\t" not in raw:
            logger.error("[youtube] MEDIA_YOUTUBE_COOKIES_B64 does not decode to a Netscape "
                         "cookies.txt (no tabs) — ignoring it")
            return None
        with open(path, "wb") as fh:
            fh.write(raw)
        try:
            os.chmod(path, 0o600)                 # it is a live Google session
        except OSError:
            pass
    except Exception as exc:                      # noqa: BLE001 — bad env must not break the request
        logger.error("[youtube] could not write cookies from MEDIA_YOUTUBE_COOKIES_B64: %s", exc)
        return None
    logger.info("[youtube] cookies written to %s from MEDIA_YOUTUBE_COOKIES_B64", path)
    _COOKIES_CACHE = path
    return path


_COOKIES_CACHE: Optional[str] = None


def has_cookies() -> bool:
    return bool(cookies_path() or YOUTUBE_COOKIES_BROWSER)


class _Collect:
    """`ignore_no_formats_error` stops yt-dlp raising, but the reason — "Sign in to
    confirm you're not a bot", "Video unavailable" — is still reported through its
    logger. Without capturing it, an empty response is indistinguishable from a dead
    link, and the learner gets the wrong explanation."""

    def __init__(self) -> None:
        self.lines: List[str] = []

    def debug(self, msg: str) -> None:
        pass

    def info(self, msg: str) -> None:
        pass

    def warning(self, msg: str) -> None:
        self.lines.append(str(msg))

    def error(self, msg: str) -> None:
        self.lines.append(str(msg))

    @property
    def text(self) -> str:
        return " ".join(self.lines)


# The clients a PO token actually buys full formats for. `web_embedded` is in the
# default chain and starts with "web", which used to satisfy a `startswith("web")`
# guard here and so silently stopped these two from ever being appended — meaning
# configuring MEDIA_YOUTUBE_POT_URL bought nothing on the default chain, which is the
# one state (metadata served, formats gated) a PO token is supposed to fix.
_POT_CLIENTS = ("web_safari", "web")


def _yt_clients() -> List[str]:
    clients = [c.strip() for c in YOUTUBE_PLAYER_CLIENTS.split(",") if c.strip()] or ["default"]
    if YOUTUBE_POT_URL:
        clients += [c for c in _POT_CLIENTS if c not in clients]
    return clients


def _yt_opts(client: Optional[str] = None, **extra) -> dict:
    opts = {"quiet": True, "no_warnings": True, "noprogress": True, "noplaylist": True,
            # A JS runtime is needed for YouTube's signature challenges; node is common on dev machines.
            "js_runtimes": {"deno": {}, "node": {}}, "retries": 3, "socket_timeout": 30}
    args: dict = {}
    if client and client != "default":
        # An unsupported name is only warned about by yt-dlp, so a bad env value
        # costs one wasted attempt rather than breaking the request.
        args["youtube"] = {"player_client": [client]}
    if YOUTUBE_POT_URL:
        args["youtubepot-bgutilhttp"] = {"base_url": [YOUTUBE_POT_URL]}
    if args:
        opts["extractor_args"] = args
    jar = cookies_path()
    if jar:
        opts["cookiefile"] = jar
    elif YOUTUBE_COOKIES_BROWSER:
        browser, _, profile = YOUTUBE_COOKIES_BROWSER.partition(":")
        opts["cookiesfrombrowser"] = (browser.strip(), profile.strip() or None, None, None)
    if YOUTUBE_PROXY:
        opts["proxy"] = YOUTUBE_PROXY
    opts.update(extra)
    return opts


# Formats we can read, best first. json3 carries exact per-cue durations; the rest are
# parsed by the same sniffing parser the relay tier uses. Insisting on json3 — which
# this did until it was found to be why a walled host reported "no captions" — throws
# the track away whenever a player client happens to list only vtt or srv3.
_CAPTION_EXTS = ("json3", "srv3", "vtt", "ttml", "srv2", "srv1")


def _track(tracks) -> tuple[Optional[str], Optional[str]]:
    """(url, ext) of the most readable variant of one caption track."""
    best = None
    for t in tracks or []:
        if not t.get("url"):
            continue
        ext = str(t.get("ext") or "").lower()
        rank = _CAPTION_EXTS.index(ext) if ext in _CAPTION_EXTS else len(_CAPTION_EXTS)
        if best is None or rank < best[0]:
            best = (rank, t["url"], ext or "vtt")
    return (best[1], best[2]) if best else (None, None)


def _pick_captions(info: dict) -> tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """(url, kind, lang, ext) — manual subtitles first, then original-language auto captions."""
    video_lang = (info.get("language") or "").split("-")[0].lower()

    manual = {k: v for k, v in (info.get("subtitles") or {}).items() if k != "live_chat"}
    order = sorted(manual, key=lambda k: (k.split("-")[0].lower() != video_lang, not k.startswith("en"), k))
    for lang in order:
        url, ext = _track(manual[lang])
        if url:
            return url, "manual", lang, ext
    auto = info.get("automatic_captions") or {}
    # "<lang>-orig" is the ASR of the spoken language; plain "<lang>" tracks are machine translations.
    # YouTube now lists several "-orig" tracks on some videos, in no fixed order, so the
    # video's own language wins — an English track on a Hindi lecture is the worse read.
    orig = sorted((k for k in auto if k.endswith("-orig")),
                  key=lambda k: (k.split("-")[0].lower() != video_lang, k))
    candidates = orig + ([video_lang] if video_lang in auto else [])
    # Last resort: any auto track at all. A walled client often returns the caption list
    # without the video's `language`, which leaves video_lang empty and the two lists
    # above empty with it — so the quiz failed outright while a usable track was sitting
    # right there. A possibly-translated track is worth far more than no speech at all.
    candidates += sorted(k for k in auto if k not in candidates)
    for lang in candidates:
        url, ext = _track(auto[lang])
        if url:
            return url, "auto", lang.replace("-orig", ""), ext
    return None, None, None, None


def parse_caption_bytes(raw: bytes, ext: Optional[str] = None) -> List[Caption]:
    """Any of the formats YouTube serves a track in. The sniffing parser lives in
    ytrelay (it had to handle Invidious VTT and Piped TTML already); this reuses it so
    both paths read a caption track the same way."""
    from services.media_quiz.ytrelay import parse_captions

    text = raw.decode("utf-8", errors="replace") if isinstance(raw, (bytes, bytearray)) else str(raw)
    return [Caption(c.start, c.end, c.text) for c in parse_captions(text)]


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


@dataclass
class _Attempt:
    """What one player client managed to get. A client is useful if it returned captions
    *or* a downloadable stream — not only if it returned both."""
    client: str
    info: dict
    caption_url: Optional[str] = None
    caption_kind: Optional[str] = None
    caption_lang: Optional[str] = None
    caption_ext: Optional[str] = None
    video_formats: int = 0
    audio_formats: int = 0

    @property
    def has_captions(self) -> bool:
        return bool(self.caption_url)

    @property
    def has_media(self) -> bool:
        return bool(self.video_formats or self.audio_formats)

    @property
    def score(self) -> tuple:
        # Captions outrank streams: they are the speech evidence the quiz is built on,
        # and they cost no download. Among equals, prefer the one with video frames.
        return (self.has_captions, self.video_formats > 0, self.audio_formats > 0,
                self.video_formats + self.audio_formats)


def _count_formats(info: dict) -> tuple[int, int]:
    """(video-only/muxed formats we could use for frames, audio-bearing formats)."""
    video = audio = 0
    for f in info.get("formats") or []:
        if not f.get("url"):
            continue
        has_v = f.get("vcodec") not in (None, "none") and f.get("ext") != "mhtml"
        has_a = f.get("acodec") not in (None, "none")
        if has_v and (f.get("height") or 0) <= 720:
            video += 1
        if has_a:
            audio += 1
    return video, audio


def _probe_one(yt_dlp, url: str, client: str) -> tuple[Optional[_Attempt], Optional[BaseException]]:
    """One client's answer: (attempt, error). Never raises except for MediaInputError,
    which is a problem with the *link* and so applies to every client."""
    said = _Collect()
    try:
        with yt_dlp.YoutubeDL(_yt_opts(client=client, ignore_no_formats_error=True, retries=PROBE_RETRIES,
                                       logger=said, no_warnings=False)) as ydl:
            info = ydl.extract_info(url, download=False)
        if not info:
            return None, RuntimeError(said.text or "yt-dlp returned no metadata")
        if info.get("_type") == "playlist" or info.get("entries"):
            raise MediaInputError("Please paste a link to a single video, not a playlist.")
        cap_url, kind, lang, ext = _pick_captions(info)
        vf, af = _count_formats(info)
        if not (info.get("duration") or cap_url or vf or af):
            # ignore_no_formats_error also swallows the refusal: yt-dlp then hands
            # back a placeholder ("youtube video #<id>", no duration, no channel).
            # What it swallowed decides the message, so carry its own words — a bot
            # wall and a deleted video look identical from the info dict alone.
            logger.warning("[youtube] player_client=%s returned an empty placeholder: %s",
                           client, _yt_message(RuntimeError(said.text))[:160])
            return None, RuntimeError(said.text or
                                      "the video is unavailable (private, removed, or the link is wrong).")
        logger.info("[youtube] player_client=%s ok: captions=%s/%s formats=%d video / %d audio",
                    client, kind or "none", ext or "-", vf, af)
        return _Attempt(client, info, cap_url, kind, lang, ext, vf, af), None
    except MediaInputError:
        raise
    except Exception as exc:                          # noqa: BLE001 — every client is retried
        logger.warning("[youtube] player_client=%s failed: %s", client, _yt_message(exc))
        return None, exc


def _probe_clients(yt_dlp, url: str) -> tuple[List[_Attempt], Optional[BaseException]]:
    """Ask every player client in the chain what it can give us, and keep them all.

    `ignore_no_formats_error` is the important flag: without it, a client that is
    perfectly willing to hand over the title and the caption tracks still raises
    "No video formats found" on an untrusted IP, and the whole link fails even though
    everything the quiz needs was already in the response.

    Scheduling: the first client is asked alone, because on a host YouTube trusts it
    comes back with captions *and* formats and there is nothing left to ask. Only when
    it doesn't are the remaining clients asked **all at once** — six sequential probes
    against a wall cost six round trips plus their retries, and that is most of the
    wall time of a link that was never going to work. The answers are re-sorted into
    the configured chain order afterwards, so which client gets used never depends on
    which one happened to reply first.
    """
    clients = _yt_clients()
    attempts: List[_Attempt] = []
    last: Optional[BaseException] = None

    def enough(att: Optional[_Attempt]) -> bool:
        return bool(att and att.has_captions and att.video_formats)

    def gone(err: Optional[BaseException]) -> bool:
        # A fatal marker is about the video, not the client: nothing else will find it.
        return err is not None and _is_fatal(err) and not _is_blocked(err)

    att, last = _probe_one(yt_dlp, url, clients[0])
    if att:
        attempts.append(att)
    rest = clients[1:]
    if enough(att) or gone(last) or not rest:
        return attempts, last

    if PROBE_WORKERS <= 1 or cookies_path():
        # yt-dlp writes refreshed cookies back to the jar as it closes, so clients
        # sharing one cookies.txt would race on that file. Cookies are the path that
        # works anyway — keep it sequential there, and keep the early exits.
        for client in rest:
            att, err = _probe_one(yt_dlp, url, client)
            if att:
                attempts.append(att)
            last = err or last
            if enough(att) or gone(err):
                break
        return attempts, last

    from concurrent.futures import ThreadPoolExecutor, as_completed

    # Start them all, but stop at the first client that has captions *and* formats, the
    # same condition the sequential version stops on. Waiting for the stragglers would
    # make a healthy host slower than asking in order, which is the opposite of the
    # point: the sum only has to become a maximum when every client is going to fail.
    pool = ThreadPoolExecutor(max_workers=min(PROBE_WORKERS, len(rest)), thread_name_prefix="ytprobe")
    try:
        futures = {pool.submit(_probe_one, yt_dlp, url, c): c for c in rest}
        for fut in as_completed(futures, timeout=PROBE_DEADLINE_S):
            att, err = fut.result()               # MediaInputError (a bad link) propagates
            if att:
                attempts.append(att)
            last = err or last
            if enough(att):
                break
    except TimeoutError:
        logger.warning("[youtube] the client probe hit its %ss deadline", PROBE_DEADLINE_S)
    finally:
        pool.shutdown(wait=False, cancel_futures=True)
    # Arrival order is a network accident; the configured chain is the intended
    # preference, so selection is made to depend only on it.
    attempts.sort(key=lambda a: clients.index(a.client) if a.client in clients else len(clients))
    return attempts, last


def youtube_video_id(url: str) -> Optional[str]:
    from urllib.parse import parse_qs, urlparse

    u = urlparse(url.strip())
    if (u.hostname or "").lower() == "youtu.be":
        return (u.path.lstrip("/").split("/") or [None])[0] or None
    if u.path.startswith(("/shorts/", "/embed/", "/live/")):
        return u.path.split("/")[2] or None
    return (parse_qs(u.query).get("v") or [None])[0]


def youtube_diagnosis(url: str, clients: Optional[List[str]] = None) -> dict:
    """What can this host actually do with YouTube? Reports the yt-dlp version, the
    JavaScript runtimes on PATH (without one, yt-dlp drops to its js-less client set),
    the outcome per player client, and whether a plain watch-page GET is served or
    walled. Downloads nothing. This is the one dependency that breaks by IP reputation
    rather than by code, so it is worth being able to ask the server itself.

    `clients` overrides the configured chain, so a candidate player client can be tried
    against the deployed host before it is made the default — which IP reputation is the
    only way to settle."""
    import shutil

    out: dict = {"url": url, "video_id": youtube_video_id(url), "clients": {}}
    try:
        import yt_dlp
        out["yt_dlp"] = yt_dlp.version.__version__
    except ImportError as exc:
        return {**out, "error": f"yt-dlp not installed: {exc}"}

    import platform

    out["arch"] = f"{platform.system()}/{platform.machine()}"
    out["js_runtimes"] = {name: shutil.which(name) for name in ("deno", "node", "bun")}
    out["cookies"] = has_cookies()
    out["proxy"] = bool(YOUTUBE_PROXY)
    if YOUTUBE_PROXY:
        out["proxy_egress"] = _safe(_proxy_egress)
    out["pot_provider"] = _safe(_pot_provider_installed)

    for client in (clients or _yt_clients()):
        said = _Collect()
        try:
            with yt_dlp.YoutubeDL(_yt_opts(client=client, ignore_no_formats_error=True,
                                           logger=said, no_warnings=False)) as ydl:
                info = ydl.extract_info(url.strip(), download=False)
            cap, kind, lang, cap_ext = _pick_captions(info or {})
            vf, af = _count_formats(info or {})
            if not ((info or {}).get("duration") or cap or vf or af):
                # An empty placeholder is a refusal yt-dlp was told not to raise.
                # Reporting it as "ok" would hide exactly what this endpoint is for.
                why = RuntimeError(said.text)
                out["clients"][client] = {"ok": False, "blocked": _is_blocked(why),
                                          "gated": _is_gated(why), "error": _yt_message(why)}
                continue
            out["clients"][client] = {"ok": True, "title": (info or {}).get("title"),
                                      "captions": bool(cap), "caption_kind": kind, "caption_lang": lang,
                                      "caption_ext": cap_ext,
                                      # 0 formats with captions present is the normal datacenter
                                      # answer, and still enough for a captions-only quiz.
                                      "video_formats": vf, "audio_formats": af}
        except Exception as exc:                  # noqa: BLE001 — this is the diagnosis
            out["clients"][client] = {"ok": False, "blocked": _is_blocked(exc),
                                      "gated": _is_gated(exc), "error": _yt_message(exc)}

    out["watch_page"] = _safe(_watch_page_probe, out["video_id"])
    from services.media_quiz import ytrelay

    from services.media_quiz import ytgemini

    out["relays"] = _safe(ytrelay.diagnosis, out["video_id"])
    out["gemini"] = _safe(ytgemini.diagnosis, out["video_id"])
    ok = [c for c in out["clients"].values() if c.get("ok")]
    relay = out["relays"] if isinstance(out["relays"], dict) else {}
    rbest = relay.get("best") or {}
    gem_ok = bool(isinstance(out["gemini"], dict) and out["gemini"].get("ok")
                  and out["gemini"].get("speech_rows"))
    out["verdict"] = {
        "can_generate_quiz": bool(any(c.get("captions") or c.get("audio_formats") for c in ok)
                                  or rbest.get("cues") or rbest.get("audio_stream") or gem_ok),
        "can_use_video_frames": bool(any(c.get("video_formats") for c in ok) or rbest.get("video_stream")),
        "speech_from": ("captions" if any(c.get("captions") for c in ok)
                        else "audio+asr" if any(c.get("audio_formats") for c in ok)
                        else f"relay:{rbest.get('kind')} captions" if rbest.get("cues")
                        else f"relay:{rbest.get('kind')} audio+asr" if rbest.get("audio_stream")
                        else "gemini transcript" if gem_ok else None),
        # Direct access is refused but a relay answers: the IP wall is no longer the
        # end of the road, which is the one thing this endpoint exists to settle.
        "relay_rescues_this_host": bool(not ok and (rbest.get("cues") or rbest.get("audio_stream"))),
        # Gemini reads the public link on Google's side, so it answers even where every
        # other tier is walled — the dependable answer for the Oracle VM.
        "gemini_rescues_this_host": bool(not ok and gem_ok),
    }
    return out


def _proxy_egress() -> dict:
    """Where yt-dlp's traffic actually leaves from, through the configured proxy — the
    proof that the proxy (e.g. the WARP tunnel from deploy/oracle/warp.sh) is up, and
    that YouTube is judging *its* address rather than this host's."""
    import yt_dlp

    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "proxy": YOUTUBE_PROXY,
                           "socket_timeout": 10}) as ydl:
        raw = ydl.urlopen("https://www.cloudflare.com/cdn-cgi/trace").read().decode("utf-8", "replace")
    kv = dict(line.split("=", 1) for line in raw.splitlines() if "=" in line)
    return {k: kv.get(k) for k in ("ip", "colo", "loc", "warp")}


def _safe(fn, *args):
    """A diagnosis that raises is useless — report the failure as its own answer."""
    try:
        return fn(*args)
    except Exception as exc:                      # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {exc}"}


def _pot_provider_installed() -> bool:
    import importlib.util

    # The bgutil PO-token provider ships as a yt-dlp plugin package. find_spec() on a
    # dotted name imports the parent, which raises when the plugin isn't installed.
    for m in ("yt_dlp_plugins.extractor.getpot_bgutil", "bgutil_ytdlp_pot_provider"):
        try:
            if importlib.util.find_spec(m) is not None:
                return True
        except (ImportError, ValueError):
            continue
    return False


def fetch_watch_page(video_id: str) -> tuple[str, str]:
    """(html, final url) for a plain watch-page GET — a different surface from the
    InnerTube player API, so it can still answer when that one says "not a bot"."""
    import httpx

    r = httpx.get(f"https://www.youtube.com/watch?v={video_id}",
                  headers={"User-Agent": WATCH_PAGE_UA, "Accept-Language": "en-US,en;q=0.9",
                           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"},
                  timeout=25.0, follow_redirects=True)
    return r.text, str(r.url)


def parse_player_response(html: str) -> Optional[dict]:
    """The ytInitialPlayerResponse object embedded in the watch page. It is followed by
    arbitrary JS, so decode it with a JSON decoder rather than matching braces by regex."""
    import json

    marker = re.search(r"ytInitialPlayerResponse\s*=\s*\{", html)
    if not marker:
        return None
    try:
        obj, _ = json.JSONDecoder().raw_decode(html[marker.end() - 1:])
        return obj if isinstance(obj, dict) else None
    except ValueError:
        return None


def watch_page_caption_tracks(pr: dict) -> List[dict]:
    caps = (pr.get("captions") or {}).get("playerCaptionsTracklistRenderer") or {}
    return [t for t in (caps.get("captionTracks") or []) if t.get("baseUrl")]


def _watch_page_probe(video_id: Optional[str]) -> dict:
    if not video_id:
        return {"skipped": "no video id"}
    try:
        html, final_url = fetch_watch_page(video_id)
    except Exception as exc:                      # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {exc}"}

    out = {
        "bytes": len(html),
        "has_player_response": "ytInitialPlayerResponse" in html,
        # A consent interstitial or a bot wall instead of the video page.
        "consent_wall": "consent.youtube.com" in final_url or "/sorry/" in final_url,
        "final_url": final_url[:200],
    }
    pr = parse_player_response(html)
    if not pr:
        return {**out, "player_response_parsed": False}
    status = pr.get("playabilityStatus") or {}
    tracks = watch_page_caption_tracks(pr)
    return {
        **out,
        "player_response_parsed": True,
        # LOGIN_REQUIRED here means the bot wall reached the page itself, and only
        # cookies / a PO token / another IP can help. OK means captions are usable.
        "playability": status.get("status"),
        "playability_reason": str(status.get("reason") or "")[:160],
        "has_streaming_data": "streamingData" in pr,
        "caption_tracks": [{"lang": t.get("languageCode"), "kind": t.get("kind")} for t in tracks],
        "title": (pr.get("videoDetails") or {}).get("title"),
        "duration_s": (pr.get("videoDetails") or {}).get("lengthSeconds"),
    }


def _cache_root() -> str:
    base = os.path.join(os.path.dirname(__file__), "..", "..", "temp_uploads", "yt_cache")
    base = os.path.normpath(base)
    os.makedirs(base, exist_ok=True)
    return base


def _cache_dir(video_id: str) -> str:
    return os.path.join(_cache_root(), re.sub(r"[^A-Za-z0-9_-]", "", video_id)[:24])


def _cache_sweep() -> None:
    """Drop expired entries. The cache holds whole video files, so it cannot just grow."""
    import shutil

    now = time.time()
    try:
        entries = os.listdir(_cache_root())
    except OSError:
        return
    for name in entries:
        meta = os.path.join(_cache_root(), name, "meta.json")
        try:
            if now - os.path.getmtime(meta) > YOUTUBE_CACHE_TTL_S:
                shutil.rmtree(os.path.join(_cache_root(), name), ignore_errors=True)
        except OSError:
            continue


def cache_load(video_id: Optional[str]) -> Optional[MediaSource]:
    """The MediaSource from an earlier fetch of this video, or None. Only the *fetch*
    is cached, not the quiz: the pipeline still runs, so a different difficulty or
    target language still gets its own questions."""
    if not (video_id and YOUTUBE_CACHE_TTL_S > 0):
        return None
    meta = os.path.join(_cache_dir(video_id), "meta.json")
    try:
        if time.time() - os.path.getmtime(meta) > YOUTUBE_CACHE_TTL_S:
            return None
        with open(meta, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    # A half-written entry (the process died mid-download) must not be served.
    for key in ("video_path", "audio_path"):
        if data.get(key) and not os.path.exists(data[key]):
            return None
    src = MediaSource(title=data.get("title") or "YouTube video", video_path=data.get("video_path"),
                      audio_path=data.get("audio_path"), duration=data.get("duration"),
                      caption_kind=data.get("caption_kind"), caption_lang=data.get("caption_lang"),
                      notes=list(data.get("notes") or []))
    caps = data.get("captions")
    if caps:
        src.captions = [Caption(c[0], c[1], c[2]) for c in caps]
    if data.get("screen_text"):
        src.screen_text = [Caption(c[0], c[1], c[2]) for c in data["screen_text"]]
    if not (src.captions or src.audio_path or src.video_path or src.screen_text):
        return None
    logger.info("[youtube] reusing the cached fetch of %s (%s)", video_id, src.title)
    return src


def cache_store(video_id: Optional[str], src: MediaSource) -> None:
    if not (video_id and YOUTUBE_CACHE_TTL_S > 0):
        return
    try:
        os.makedirs(_cache_dir(video_id), exist_ok=True)
        with open(os.path.join(_cache_dir(video_id), "meta.json"), "w", encoding="utf-8") as f:
            json.dump({"title": src.title, "duration": src.duration, "video_path": src.video_path,
                       "audio_path": src.audio_path, "caption_kind": src.caption_kind,
                       "caption_lang": src.caption_lang, "notes": src.notes,
                       "captions": [[c.start, c.end, c.text] for c in src.captions or []],
                       "screen_text": [[c.start, c.end, c.text] for c in src.screen_text or []]}, f)
    except (OSError, TypeError, ValueError) as exc:
        logger.info("[youtube] could not cache the fetch of %s: %s", video_id, exc)


def _download_dir(video_id: Optional[str], workdir: str) -> str:
    """Where the media files land. With the cache on that is the per-video cache
    directory, so the files outlive the request (the router deletes the workdir) and
    the next quiz from the same link starts with them already on disk."""
    if not (video_id and YOUTUBE_CACHE_TTL_S > 0):
        return workdir
    try:
        os.makedirs(_cache_dir(video_id), exist_ok=True)
        return _cache_dir(video_id)
    except OSError:
        return workdir


# One fetch per video at a time: two learners pasting the same link would otherwise
# write the same cache files from two threads.
_fetch_locks: dict = {}
_fetch_locks_guard = threading.Lock()


def _fetch_lock(video_id: Optional[str]):
    with _fetch_locks_guard:
        return _fetch_locks.setdefault(video_id or "-", threading.Lock())


def _relay_fill(src: MediaSource, video_id: Optional[str], workdir: str,
                trace: Optional[dict] = None) -> MediaSource:
    """Ask the open-source front-ends (Invidious / Piped) for whatever this host was
    refused. They talk to YouTube from their own address, so the bot wall on *this*
    IP — the state the Oracle VM is in, where every player client and the watch page
    answer LOGIN_REQUIRED — does not apply to them.

    Only the gaps are filled. yt-dlp's own captions and a direct googlevideo download
    are both better when they are available, so a relay is never asked for something
    already in hand."""
    from services.media_quiz import ytrelay

    if trace is not None:
        trace["enabled"] = ytrelay.enabled()
    if not (video_id and ytrelay.enabled()):
        return src
    need_speech = not (src.captions or src.audio_path)
    need_video = not src.video_path and ytrelay.RELAY_FRAMES
    if not (need_speech or need_video):
        return src
    tried: List[dict] = []
    try:
        res = ytrelay.fetch(video_id, attempts=tried)
    except Exception as exc:                          # noqa: BLE001 — a fallback must not raise
        logger.warning("[youtube] relay tier failed: %s: %s", type(exc).__name__, exc)
        return src
    finally:
        if trace is not None:
            trace["tried"] = len(tried)
            trace["walled"] = sum(1 for a in tried if a.get("why") == "youtube_walls_the_instance")
    if not res:
        return src

    from urllib.parse import urlparse

    where = f"{res.kind} ({urlparse(res.instance).hostname})"
    if _too_long(res.duration) and not src.duration:
        # The length gate hasn't run yet on the relay-only path. Check it before
        # spending a public instance's bandwidth on a video we are going to refuse.
        src.duration = res.duration
        return src
    if need_speech and res.captions:
        src.captions = [Caption(c.start, c.end, c.text) for c in res.captions]
        src.caption_kind, src.caption_lang = res.caption_kind, res.caption_lang
        src.notes.append(f"speech from YouTube {res.caption_kind} captions "
                         f"({res.caption_lang}) relayed by {where}")
    still_mute = not (src.captions or src.audio_path)
    if res.muxed and res.video_url:
        # cobalt serves one file with both tracks. Fetch it once if either half is
        # wanted, then use it for both — the frames are free once the bytes are here,
        # so they come back even with MEDIA_YOUTUBE_RELAY_FRAMES off.
        if still_mute or need_video:
            got = ytrelay.download(res.video_url, os.path.join(workdir, f"relay_{video_id}.mp4"))
            if got:
                src.video_path = src.video_path or got
                if still_mute:
                    src.audio_path = got
                src.notes.append(f"video and audio relayed by {where} — no caption track there, "
                                 "so the speech is transcribed")
    else:
        if need_video and res.video_url:
            got = ytrelay.download(res.video_url, os.path.join(workdir, f"relay_v_{video_id}.mp4"))
            if got:
                src.video_path = got
                src.notes.append(f"video frames relayed by {where}")
        if still_mute and res.audio_url:
            got = ytrelay.download(res.audio_url, os.path.join(workdir, f"relay_a_{video_id}.m4a"))
            if got:
                src.audio_path = got
                src.notes.append(f"audio relayed by {where} (no captions)")
    if res.title and src.title in (None, "", "YouTube video"):
        src.title = res.title
    src.duration = src.duration or res.duration
    return src


def _gap_fill(src: MediaSource, video_id: Optional[str], workdir: str,
              trace: Optional[dict] = None) -> MediaSource:
    """Fill what YouTube withheld from this host, from the two tiers that do not ask
    YouTube from this IP: the relay pool (`_relay_fill`) and Gemini, which reads a
    public link on Google's side (`ytgemini`). They run **side by side** — the relay
    race has a 15 s deadline and Gemini takes ~10–25 s, so running them one after the
    other would add the first's wait to every walled request.

    Precedence is by evidence quality, not by who answers first: real caption tracks
    (direct or relayed) beat a model transcript, and real frames (OCR) beat model-read
    screen text. Gemini's output is used only for what is still missing."""
    from services.media_quiz import ytgemini

    trace = trace if trace is not None else {}
    gem_trace = trace.setdefault("gemini", {"enabled": ytgemini.enabled()})
    need_speech = not (src.captions or src.audio_path)
    need_screen = not src.video_path and ytgemini.SCREEN_WHEN_NO_FRAMES
    if not (video_id and ytgemini.enabled() and (need_speech or need_screen)):
        return _relay_fill(src, video_id, workdir, trace)

    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="yt-gemini") as pool:
        job = pool.submit(ytgemini.fetch, video_id, src.duration, gem_trace)
        src = _relay_fill(src, video_id, workdir, trace)      # meanwhile, on this thread
        gem = job.result()
    if not gem:
        return src
    src.duration = src.duration or gem.duration
    if not (src.captions or src.audio_path) and gem.speech:
        src.captions = [Caption(c.start, c.end, c.text) for c in gem.speech]
        src.caption_kind, src.caption_lang = "gemini", gem.lang or "en"
        src.notes.append(f"speech transcribed from the public video by Gemini ({gem.model}, "
                         f"{gem.windows_ok} parallel windows) — YouTube refused this server directly")
    if not src.video_path and gem.screen:
        src.screen_text = [Caption(c.start, c.end, c.text) for c in gem.screen]
        src.notes.append(f"on-screen text read by Gemini ({len(gem.screen)} screens) in place of OCR")
    return src


def _too_long(seconds: Optional[float]) -> bool:
    return bool(seconds and seconds > YOUTUBE_MAX_DURATION_S)


def _check_duration(seconds: Optional[float]) -> None:
    if _too_long(seconds):
        raise MediaInputError(f"Video is {seconds / 60:.0f} min long; the limit is "
                              f"{YOUTUBE_MAX_DURATION_S // 60} min.")


def download_youtube(url: str, workdir: str) -> MediaSource:
    try:
        import yt_dlp
    except ImportError as exc:
        raise RuntimeError("yt-dlp is not installed (pip install -r requirements-media.txt)") from exc

    if not is_youtube_url(url):
        raise MediaInputError("Only YouTube links (youtube.com / youtu.be) are supported.")

    url = url.strip()
    video_id = youtube_video_id(url)
    with _fetch_lock(video_id):
        return _fetch_youtube(yt_dlp, url, video_id, workdir)


def _fetch_youtube(yt_dlp, url: str, video_id: Optional[str], workdir: str) -> MediaSource:
    _cache_sweep()
    cached = cache_load(video_id)
    if cached:
        return cached
    dldir = _download_dir(video_id, workdir)

    from services.media_quiz import ytgemini

    # Set once the relay / Gemini tiers have run for this request, so they are not asked twice.
    tiers: Optional[dict] = None
    if ytgemini.first():
        # A host known to be walled (the Oracle VM): the direct probe can only fail, and
        # skipping it saves its round trips. Anything the tiers cannot give falls back
        # to the normal path below.
        tiers = {}
        done = _tiers_only(_gap_fill(MediaSource(title="YouTube video"), video_id, dldir, tiers), video_id)
        if done:
            return done

    try:
        attempts, last_error = _probe_clients(yt_dlp, url)
    except MediaInputError:
        raise
    except Exception as exc:                          # noqa: BLE001 — turned into a sentence below
        attempts, last_error = [], exc

    if not attempts:
        exc = last_error or RuntimeError("yt-dlp returned no metadata")
        # Everything this host could ask YouTube directly has been refused. The relay
        # tier asks somebody else's server instead, which is the only thing left that
        # can work from a walled IP without credentials — so it is tried before the
        # link is declared dead.
        relay: dict = tiers if tiers is not None else {}
        if tiers is None and (not _is_fatal(exc) or _is_blocked(exc)):
            # An over-long video is a plain refusal, not "YouTube blocked this server":
            # _tiers_only checks the length the tiers learnt before anything else.
            done = _tiers_only(_gap_fill(MediaSource(title="YouTube video"), video_id, dldir, relay), video_id)
            if done:
                return done
        # Order matters. A refused request often *also* reports "No video formats
        # found", and a removed video reports it too, so the unambiguous wording has
        # to be tested first or every dead link is blamed on the anti-bot check.
        if _is_blocked(exc):
            raise MediaInputError(_blocked_message(relay)) from exc
        if _is_fatal(exc):
            raise MediaInputError("That video is unavailable — it may be private, removed, "
                                  "age-restricted or region-locked.") from exc
        if _is_gated(exc):
            raise MediaInputError(_blocked_message(relay)) from exc
        raise MediaInputError(f"Could not read that YouTube link: {_yt_message(exc)}") from exc

    best = max(attempts, key=lambda a: a.score)
    info = best.info
    if info.get("is_live"):
        raise MediaInputError("Live streams are not supported.")
    src = MediaSource(title=str(info.get("title") or "YouTube video"),
                      duration=float(info.get("duration") or 0) or None)
    _check_duration(src.duration)                     # before any download

    def fetch_captions() -> None:
        """Captions, from any client that has them — a client can be denied the media URLs
        and still serve the caption tracks, which is the common case on a datacenter IP."""
        for att in sorted((a for a in attempts if a.has_captions), key=lambda a: a.score, reverse=True):
            try:
                with yt_dlp.YoutubeDL(_yt_opts(client=att.client)) as ydl:
                    caps = parse_caption_bytes(ydl.urlopen(att.caption_url).read(), att.caption_ext)
            except Exception as exc:                  # noqa: BLE001 — try the next client
                logger.warning("[youtube] captions via %s failed: %s", att.client, _yt_message(exc))
                continue
            if caps:
                src.captions, src.caption_kind, src.caption_lang = caps, att.caption_kind, att.caption_lang
                src.notes.append(f"speech from YouTube {att.caption_kind} captions ({att.caption_lang})")
                return
            logger.warning("[youtube] captions via %s were empty", att.client)

    def fetch(fmt: str, prefix: str, clients: List[str]) -> Optional[str]:
        """Download one stream, trying each client that advertised a usable format."""
        for client in clients:
            try:
                with yt_dlp.YoutubeDL(_yt_opts(client=client, format=fmt,
                                               outtmpl=os.path.join(dldir, prefix + "_%(id)s.%(ext)s"))) as y:
                    got = y.extract_info(url, download=True)
                    path = y.prepare_filename(got)
                if os.path.exists(path) and os.path.getsize(path) > 0:
                    return path
            except Exception as exc:                  # noqa: BLE001 — next client
                logger.warning("[youtube] %s download via %s failed: %s", prefix, client, _yt_message(exc))
        return None

    def order(kind: str) -> List[str]:
        """Clients that said they have this kind of stream, best first."""
        return [a.client for a in sorted(attempts, key=lambda a: a.score, reverse=True)
                if getattr(a, kind) > 0]

    # The video stream downloads while the captions are fetched: it is always wanted
    # (frames for OCR), and it used to wait for the caption round trips. The audio
    # stream is only wanted when there are no captions, so it starts once that is known.
    from concurrent.futures import ThreadPoolExecutor

    video_clients, audio_clients = order("video_formats"), order("audio_formats")
    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="yt") as pool:
        video_job = pool.submit(fetch, _YT_VIDEO_FORMAT, "v", video_clients) if video_clients else None
        fetch_captions()
        audio_job = (pool.submit(fetch, _YT_AUDIO_FORMAT, "a", audio_clients)
                     if audio_clients and not src.captions else None)
        src.video_path = video_job.result() if video_job else None
        audio_path = audio_job.result() if audio_job else None
    if not src.captions:
        src.audio_path = audio_path
        if src.audio_path:
            src.notes.append("speech transcribed from the audio track (no captions)")
    # Whatever YouTube withheld from this host, ask the relay tier for. On a datacenter
    # IP that is usually the media URLs (captions come through), so this is what brings
    # the video frames — and with them the OCR evidence — back.
    relay: dict = tiers if tiers is not None else {}
    if tiers is None:
        src = _gap_fill(src, video_id, dldir, relay)
    if not src.video_path and not src.screen_text:
        # Frames are optional: the quiz is built from speech, and on-screen text only
        # adds OCR evidence. Losing them is a note, not a failure.
        src.notes.append("video frames unavailable from this server — speech only")
    if not src.captions and not src.audio_path:
        # Nothing to read and nothing to listen to.
        if src.video_path or src.screen_text:
            src.notes.append("no captions and no audio track — questions come from on-screen text only")
        elif audio_clients:
            # A stream was offered and the download still failed: a transfer problem,
            # not a refusal, so don't send the admin looking for cookies.
            raise MediaInputError("Could not download this video's audio from YouTube. "
                                  "Upload the video or audio file instead.")
        else:
            raise MediaInputError(_no_speech_message(relay))
    _finish_youtube(src, video_id)
    return src


def _oembed_title(video_id: Optional[str]) -> Optional[str]:
    """The title from YouTube's oEmbed endpoint — plain metadata, not the player, so it
    is answered even where the player refuses this host. Used only to name a quiz that
    was built without yt-dlp's metadata."""
    if not video_id:
        return None
    try:
        import httpx

        r = httpx.get("https://www.youtube.com/oembed", timeout=5, params={
            "url": f"https://www.youtube.com/watch?v={video_id}", "format": "json"})
        return (r.json().get("title") or None) if r.status_code == 200 else None
    except Exception:                                 # noqa: BLE001 — cosmetic only
        return None


def _tiers_only(src: MediaSource, video_id: Optional[str]) -> Optional[MediaSource]:
    """Finish a source built only by the relay / Gemini tiers (YouTube refused this host
    directly), or None when they found nothing to learn from."""
    _check_duration(src.duration)
    if not (src.captions or src.audio_path or src.screen_text):
        return None
    # oEmbed is authoritative; a relay's title can be a download filename ("… (360p, h264)").
    src.title = _oembed_title(video_id) or src.title or "YouTube video"
    if not src.video_path and not src.screen_text:
        src.notes.append("video frames unavailable from this server — speech only")
    _finish_youtube(src, video_id)
    return src


def _finish_youtube(src: MediaSource, video_id: Optional[str]) -> None:
    """Last gate before the pipeline sees it, on every path into it (relay-only too)."""
    _check_duration(src.duration)
    cache_store(video_id, src)


def temp_dir() -> str:
    base = os.path.join(os.path.dirname(__file__), "..", "..", "temp_uploads")
    os.makedirs(base, exist_ok=True)
    return tempfile.mkdtemp(prefix="media_", dir=os.path.normpath(base))
