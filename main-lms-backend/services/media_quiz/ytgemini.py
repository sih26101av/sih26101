"""
FILE: services/media_quiz/ytgemini.py
─────────────────────────────────────────────────────────────────────────────
The Google-side tier: Gemini reads a *public* YouTube link itself.

Every other YouTube path asks YouTube for bytes from somewhere — this host (walled
on a datacenter IP), a public Invidious / Piped / cobalt instance (usually walled
too: same address space), or a proxy / cookies the admin has to provide. The
Gemini API accepts a YouTube URL as `fileData.fileUri` and fetches the video on
Google's side, so the only thing that leaves this host is an HTTPS call to
generativelanguage.googleapis.com. That is why it works from the Oracle VM, and
it needs nothing beyond the GEMINI_API_KEY the quiz already uses.

What comes back is shaped like the other tiers' output, so the pipeline treats it
the same way:
  • speech  → Caption list (kind "gemini") → ASR evidence, like auto captions
  • screen  → ScreenText list → on-screen evidence (slides, code, formulas) in
              place of OCR, which this host could not run without the frames

Speed: the video is split into windows (`videoMetadata.startOffset/endOffset`)
that are transcribed in parallel, so a long lecture costs about one window's
latency rather than one long generation. Quality guards:
  • usageMetadata must show VIDEO/AUDIO prompt tokens — a model that answers
    without having received the video is refused, not trusted
  • timestamps outside the requested window are dropped; a window answered in
    clip-relative time is shifted back
  • the transcript is verbatim and in the spoken language (never translated),
    which the downstream number / citation validator depends on
Env: MEDIA_YOUTUBE_GEMINI (auto|first|off), MEDIA_YOUTUBE_GEMINI_MODEL,
     MEDIA_YOUTUBE_GEMINI_WINDOW_S, _PARALLEL, _MAX_S, _TIMEOUT_S, _RESOLUTION.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import logging
import math
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import httpx

logger = logging.getLogger(__name__)

# auto  — used when this host could not get speech (or frames) from YouTube directly
# first — skip the direct yt-dlp probe (a host known to be walled, like the VM)
# off   — never
MODE = os.getenv("MEDIA_YOUTUBE_GEMINI", "auto").strip().lower()
MODEL = os.getenv("MEDIA_YOUTUBE_GEMINI_MODEL", "").strip()
# 5-minute windows: ~27k prompt tokens and ~2.5k output tokens each, ≈15–25 s apiece.
WINDOW_S = float(os.getenv("MEDIA_YOUTUBE_GEMINI_WINDOW_S", "300"))
PARALLEL = int(os.getenv("MEDIA_YOUTUBE_GEMINI_PARALLEL", "6"))
# Longest stretch transcribed. Longer videos get windows spread evenly across the
# whole length — the pipeline keeps only the ~12 most relevant chunks anyway, and
# this mirrors the Whisper budget's even sampling.
MAX_COVER_S = float(os.getenv("MEDIA_YOUTUBE_GEMINI_MAX_S", "3600"))
TIMEOUT_S = float(os.getenv("MEDIA_YOUTUBE_GEMINI_TIMEOUT_S", "150"))
# LOW ≈ 90 tokens per second of video (measured). Slides and code stay legible at it.
RESOLUTION = os.getenv("MEDIA_YOUTUBE_GEMINI_RESOLUTION", "MEDIA_RESOLUTION_LOW").strip()
# Also ask Gemini when captions came through directly but the frames did not — it
# restores the on-screen evidence (slides / code) that OCR would otherwise have given.
SCREEN_WHEN_NO_FRAMES = os.getenv("MEDIA_YOUTUBE_GEMINI_SCREEN", "1") != "0"

API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
SCREEN_CONFIDENCE = 0.78        # text read off the screen by a model: below manual captions, above the floor


@dataclass
class GeminiCue:
    start: float
    end: float
    text: str


@dataclass
class GeminiResult:
    speech: List[GeminiCue] = field(default_factory=list)
    screen: List[GeminiCue] = field(default_factory=list)
    lang: Optional[str] = None
    model: Optional[str] = None
    duration: Optional[float] = None    # estimated where the video's length was unknown
    windows: int = 0
    windows_ok: int = 0
    covered_s: float = 0.0
    elapsed_s: float = 0.0


def _key() -> str:
    from services.media_quiz.llm import gemini_key
    return gemini_key()


def enabled() -> bool:
    return MODE != "off" and bool(_key())


def first() -> bool:
    return MODE == "first" and enabled()


def _models() -> List[str]:
    from services.media_quiz.llm import DEFAULT_GEMINI_MODEL, _FALLBACK_MODELS
    head = MODEL or os.getenv("GEMINI_MODEL", "").strip() or DEFAULT_GEMINI_MODEL
    return [head] + [m for m in _FALLBACK_MODELS if m != head]


# Model ids this key does not serve (404) are skipped for the rest of the process.
_dead_models: set = set()


def _ts(value) -> Optional[float]:
    if isinstance(value, (int, float)):
        return float(value)
    m = re.fullmatch(r"\s*(?:(\d+):)?(\d{1,3}):(\d{2})(?:[.,](\d+))?\s*", str(value or ""))
    if not m:
        return None
    h, mnt, s, frac = m.groups()
    return int(h or 0) * 3600 + int(mnt) * 60 + int(s) + (float(f"0.{frac}") if frac else 0.0)


def _fmt(seconds: float) -> str:
    s = int(max(0, seconds))
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60:02d}:{s % 60:02d}"


_ROW = re.compile(r'\[\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*"((?:[^"\\]|\\.)*)"\s*\]')


def _rows(raw: str) -> Tuple[Dict, List, List]:
    """Parse the model's JSON. A response cut off at the output limit is still
    salvaged row by row — the rows before the cut are good evidence."""
    try:
        data = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip()))
        if isinstance(data, dict):
            return data, list(data.get("speech") or []), list(data.get("screen") or [])
    except (json.JSONDecodeError, ValueError):
        pass
    head, _, tail = raw.partition('"screen"')
    unq = lambda t: json.loads(f'"{t}"')                 # noqa: E731 — JSON string unescape
    speech = [[a, b, unq(c)] for a, b, c in _ROW.findall(head)]
    screen = [[a, b, unq(c)] for a, b, c in _ROW.findall(tail)]
    lang = re.search(r'"lang"\s*:\s*"([^"]*)"', raw)
    return ({"lang": lang.group(1)} if lang else {}), speech, screen


def _prompt(a: float, b: Optional[float]) -> str:
    span = (f"the clip from {_fmt(a)} to {_fmt(b)} of the full video" if b is not None
            else "the whole video")
    return (
        f"You are given {span} (a public YouTube training video). Extract evidence for a "
        "quiz generator. Return ONE JSON object:\n"
        '{"lang":"<ISO 639-1 code of the main spoken language>",'
        '"speech":[["MM:SS","MM:SS","verbatim words"]],'
        '"screen":[["MM:SS","MM:SS","verbatim on-screen text"]]}\n'
        "Rules:\n"
        "- speech: a VERBATIM transcript of everything spoken, in order, in the language actually "
        "spoken (Hindi in Devanagari, Hinglish as spoken). Never translate, summarise or paraphrase; "
        "keep numbers exactly as said. One row per sentence or about 10-20 seconds.\n"
        "- screen: text visibly shown — slide titles and bullets, code, formulas, table and chart "
        "labels and values — copied exactly, one row per distinct screen, with the span it is "
        "visible. Skip logos, watermarks, subscribe prompts and burned-in subtitles that repeat "
        "the speech. [] if there is none.\n"
        "- Timestamps are start and end, measured from the START OF THE FULL VIDEO "
        "(H:MM:SS past an hour).\n"
        "- Include nothing you cannot actually hear or see. A clip with no speech and no text "
        'returns {"lang":"","speech":[],"screen":[]}.'
    )


def _output_cap(a: float, b: Optional[float]) -> int:
    """Room for a verbatim transcript of the window and no more. A real 5-minute window
    needs ~2–4k tokens (Devanagari tokenises heaviest). The cap matters for speed, not
    cost: a model that falls into a repetition loop writes until it hits it — measured
    at 32k tokens and ~110 s for one window — while the loop itself is discarded."""
    span = (b - a) if b is not None else MAX_COVER_S
    return int(min(65536, max(8192, span * 28)))


class _WindowError(RuntimeError):
    def __init__(self, message: str, status: int = 0):
        super().__init__(message)
        self.status = status


def _call(client: httpx.Client, url: str, a: float, b: Optional[float],
          speculative: bool = False) -> Tuple[str, Dict, List, List]:
    """One window through the model chain. Returns (model, meta, speech rows, screen rows).
    `speculative`: the window may lie past the end of a video of unknown length, which
    Gemini answers with a 5xx — so a 5xx ends it instead of being retried on every model."""
    part: Dict = {"fileData": {"fileUri": url}}
    if b is not None:
        part["videoMetadata"] = {"startOffset": f"{int(a)}s", "endOffset": f"{int(math.ceil(b))}s"}
    gen: Dict = {"responseMimeType": "application/json", "temperature": 0.1,
                 "maxOutputTokens": _output_cap(a, b)}
    if RESOLUTION:
        gen["mediaResolution"] = RESOLUTION
    body = {"contents": [{"role": "user", "parts": [part, {"text": _prompt(a, b)}]}], "generationConfig": gen}

    last: Optional[_WindowError] = None
    for model in _models():
        if model in _dead_models:
            continue
        try:
            r = client.post(API.format(model=model), headers={"x-goog-api-key": _key()}, json=body)
        except httpx.HTTPError as exc:
            last = _WindowError(f"{model}: {type(exc).__name__}: {exc}")
            continue
        if r.status_code == 404:
            _dead_models.add(model)
            last = _WindowError(f"{model}: not served to this key", 404)
            continue
        if r.status_code != 200:
            try:
                msg = r.json().get("error", {}).get("message", "")
            except ValueError:
                msg = r.text[:200]
            last = _WindowError(f"{model}: HTTP {r.status_code}: {msg[:240]}", r.status_code)
            if r.status_code == 400:
                # A bad request is about the video (private, unlisted, too long), not the
                # model — trying the next model only repeats it.
                raise last
            if speculative and r.status_code >= 500:
                raise last
            continue                                   # 429 / 5xx → next model
        data = r.json()
        # The one check that separates "transcribed the video" from "made one up": a
        # model that never received the video spends no VIDEO / AUDIO prompt tokens.
        details = (data.get("usageMetadata") or {}).get("promptTokensDetails") or []
        if details and not any(d.get("modality") in {"VIDEO", "AUDIO"} and d.get("tokenCount")
                                for d in details):
            last = _WindowError(f"{model}: answered without receiving the video")
            continue
        cands = data.get("candidates") or []
        parts = ((cands[0].get("content") or {}).get("parts") or []) if cands else []
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
        if not text.strip():
            reason = cands[0].get("finishReason") if cands else (data.get("promptFeedback") or {})
            last = _WindowError(f"{model}: empty answer ({reason})")
            continue
        meta, speech, screen = _rows(text)
        if cands[0].get("finishReason") == "MAX_TOKENS":
            logger.info("[yt-gemini] %s window %s hit the output limit; kept %d rows", model, _fmt(a), len(speech))
        return model, meta, speech, screen
    raise last or _WindowError("no Gemini model is available")


# "[Music]", "(applause)", "♪" — sound labels, dropped like the caption parser drops them.
_NOISE = re.compile(r"[\s♪]*(?:[\[(][^\])]{0,40}[\])][\s♪]*)*[\s♪]*")


def _unloop(cues: List[GeminiCue], lookback: int = 4) -> List[GeminiCue]:
    """Drop rows that repeat one of the last few rows — the shape of a decoder loop
    (the same sentence, or the same 2–3 sentences, over and over). Whisper's
    no_repeat_ngram_size guards the same failure on the local path."""
    out: List[GeminiCue] = []
    recent: List[str] = []
    for c in cues:
        key = re.sub(r"\W+", " ", c.text.lower()).strip()
        if key and key in recent:
            continue
        out.append(c)
        recent = (recent + [key])[-lookback:]
    return out


def _cues(rows: List, a: float, b: Optional[float]) -> List[GeminiCue]:
    out: List[GeminiCue] = []
    for row in rows:
        if not (isinstance(row, (list, tuple)) and len(row) >= 3):
            continue
        s, e, text = _ts(row[0]), _ts(row[1]), " ".join(str(row[2]).split())
        if s is None or not text or _NOISE.fullmatch(text):
            continue
        out.append(GeminiCue(s, e if e is not None and e >= s else s + 5.0, text))
    out = _unloop(out)
    if not out or b is None:
        return out
    # Asked for full-video time; a clip answered in clip time is shifted back.
    if a > 0 and max(c.start for c in out) < a - 1:
        out = [GeminiCue(c.start + a, c.end + a, c.text) for c in out]
    return [c for c in out if a - 2 <= c.start <= b + 2]


def plan(duration: Optional[float]) -> List[Tuple[float, Optional[float]]]:
    """The windows for a video of known length (an unknown one goes through `_waves`)."""
    if not duration or duration <= 0:
        return [(0.0, None)]
    n = max(1, math.ceil(duration / WINDOW_S))
    keep = max(1, int(MAX_COVER_S // WINDOW_S))
    if n <= keep:
        return [(i * WINDOW_S, min(duration, (i + 1) * WINDOW_S)) for i in range(n)]
    # Evenly spread across the whole video, always including the start.
    starts = sorted({round(i * (duration - WINDOW_S) / (keep - 1)) for i in range(keep)}) if keep > 1 else [0.0]
    return [(float(s), float(min(duration, s + WINDOW_S))) for s in starts]


def _waves(duration: Optional[float]):
    """Yield lists of windows. A known length gives one planned batch. An unknown one —
    the walled host's normal case, since YouTube refused this host the metadata too —
    is probed in speculative waves of PARALLEL windows: a window past the end fails
    fast (measured: HTTP 500 in ~3 s, no video tokens), so the wave after the one where
    the speech stops is simply never sent."""
    if duration and duration > 0:
        yield plan(duration), False
        return
    start = 0.0
    while start < MAX_COVER_S:
        wave = [(start + i * WINDOW_S, start + (i + 1) * WINDOW_S)
                for i in range(max(1, PARALLEL)) if start + i * WINDOW_S < MAX_COVER_S]
        yield wave, True
        start = wave[-1][1]


def fetch(video_id: str, duration: Optional[float] = None,
          trace: Optional[Dict] = None) -> Optional[GeminiResult]:
    """Transcript + on-screen text for a public YouTube video, read by Gemini. None when
    the tier is off or nothing usable came back; never raises."""
    if not (video_id and enabled()):
        return None
    t0 = time.perf_counter()
    url = f"https://www.youtube.com/watch?v={video_id}"
    res = GeminiResult()
    langs: Dict[str, float] = {}
    errors: List[str] = []
    ended_at: Optional[float] = None

    def one(w, speculative):
        a, b = w
        with httpx.Client(timeout=TIMEOUT_S) as client:
            return _call(client, url, a, b, speculative)

    with ThreadPoolExecutor(max_workers=max(1, PARALLEL), thread_name_prefix="ytgem") as pool:
        for wave, speculative in _waves(duration):
            res.windows += len(wave)
            futures = [(w, pool.submit(one, w, speculative)) for w in wave]
            full_to_the_end = True
            for (a, b), f in futures:
                try:
                    model, meta, speech, screen = f.result()
                except Exception as exc:                   # noqa: BLE001 — a fallback must not raise
                    if not (speculative and a > 0):
                        errors.append(str(exc))        # past-the-end windows are expected to fail
                    full_to_the_end = False
                    continue
                sp, sc = _cues(speech, a, b), _cues(screen, a, b)
                if not (sp or sc):
                    full_to_the_end = False
                    continue
                res.windows_ok += 1
                res.model = res.model or model
                res.speech += sp
                res.screen += sc
                last = max(c.end for c in sp + sc)
                res.covered_s += (min(b, last) - a) if b is not None else last
                if b is not None and last < b - 45:
                    full_to_the_end = False                # the video ends inside this window
                    ended_at = max(ended_at or 0.0, last)
                lang = str(meta.get("lang") or "").split("-")[0].lower()
                if lang and sp:
                    langs[lang] = langs.get(lang, 0.0) + sum(c.end - c.start for c in sp)
            if speculative and not full_to_the_end:
                break

    res.speech.sort(key=lambda c: c.start)
    res.screen.sort(key=lambda c: c.start)
    res.lang = max(langs, key=langs.get) if langs else None
    if not duration and (res.speech or res.screen):
        res.duration = ended_at or max(c.end for c in res.speech + res.screen)
    res.elapsed_s = round(time.perf_counter() - t0, 1)
    if trace is not None:
        trace.update({"enabled": True, "windows": res.windows, "windows_ok": res.windows_ok,
                      "errors": errors[:3], "elapsed_s": res.elapsed_s})
    for e in errors:
        logger.warning("[yt-gemini] %s: window failed: %s", video_id, e)
    if not (res.speech or res.screen):
        return None
    logger.info("[yt-gemini] %s: %d speech + %d screen rows from %d/%d windows via %s in %.1fs",
                video_id, len(res.speech), len(res.screen), res.windows_ok, res.windows, res.model, res.elapsed_s)
    return res


def diagnosis(video_id: Optional[str]) -> Dict:
    """Can this host get a transcript through Gemini? Asks for one short window only."""
    if not enabled():
        return {"enabled": False, "mode": MODE, "reason": "off" if MODE == "off" else "GEMINI_API_KEY not set"}
    out: Dict = {"enabled": True, "mode": MODE, "models": [m for m in _models() if m not in _dead_models]}
    if not video_id:
        return {**out, "skipped": "no video id"}
    t0 = time.perf_counter()
    try:
        with httpx.Client(timeout=TIMEOUT_S) as client:
            model, _, speech, screen = _call(client, f"https://www.youtube.com/watch?v={video_id}", 0.0, 60.0)
        out.update({"ok": True, "model": model, "speech_rows": len(_cues(speech, 0.0, 60.0)),
                    "screen_rows": len(_cues(screen, 0.0, 60.0))})
    except Exception as exc:                               # noqa: BLE001 — a diagnosis always answers
        out.update({"ok": False, "error": str(exc)[:300]})
    out["elapsed_s"] = round(time.perf_counter() - t0, 1)
    return out
