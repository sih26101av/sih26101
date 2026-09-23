"""
FILE: services/media_quiz/ytrelay.py
─────────────────────────────────────────────────────────────────────────────
The relay tier: YouTube through an open-source front-end instead of directly.

WHY THIS EXISTS
    yt-dlp asks YouTube from *this* machine. On a datacenter IP — the Oracle VM —
    every InnerTube player client and the plain watch page answer
    LOGIN_REQUIRED / "Sign in to confirm you're not a bot", so there is no
    surface left for `media_io._probe_clients` to read. That is a property of the
    IP, not of the code, and no chain of player clients can change it.

    An Invidious, Piped or cobalt instance is a third-party server that talks to
    YouTube from *its own* address and re-serves the result over a plain JSON API.
    The VM only ever connects to the instance, so the wall on the VM's IP never
    applies. All three are AGPL, public, and need no account or API key.

    MEASURED STATE, 2026-09-23 — read this before trusting the tier. 45 public
    instances across the three pools were asked for one ordinary video from a
    residential connection. **None returned usable media.** The failures split into:
      • `youtube_walls_the_instance` — the instance is up and answers, but YouTube
        refuses *it* (Piped: `SignInConfirmNotBotException`; cobalt: a tunnel that
        opens and then streams 0 bytes). This is the same wall the VM hits: the
        public pools live in the same datacenter address space.
      • `instance_refuses_api_clients` — the operator turned the JSON API off or put
        the host behind a scraper block (`Endpoint disabled`, openresty 403).
      • `instance_unreachable` — dead DNS or timeouts, the majority.
    So this tier is not a fix for the Oracle VM *today*. It is kept because it costs
    almost nothing when it fails (one parallel race behind a 15 s deadline and a
    penalty box), it self-heals as instances recover, and — the part that does work
    now — pointing `MEDIA_YOUTUBE_RELAYS` at an instance **you** run, anywhere that
    is not a flagged datacenter, turns YouTube links back on with one env var and no
    Google account. `GET /youtube/diagnose` reports which of the three states this
    host is in rather than leaving it to be guessed.

WHAT IT GETS
    • captions  — the real YouTube caption track, relayed as VTT / TTML / json3.
                  This is what the quiz is built from, so a relay with captions
                  is a working YouTube link.
    • streams   — a ≤360p video-only file **through the instance's own proxy**
                  (`local=true` on Invidious, `pipedproxy-*` on Piped), which
                  restores the OCR / VLM evidence that a captions-only run loses.
                  A format URL that still points at googlevideo.com is discarded:
                  the VM cannot fetch it either.
    • audio     — smallest audio stream, only when there are no captions at all.

HOW IT PICKS AN INSTANCE
    Public instances die, rate-limit and get IP-blocked themselves, so there is
    no single one worth hardcoding — of the six Piped hosts in the static list,
    four had stopped resolving by the time this was written. The list is discovered
    live (Invidious' instances.json, Piped's instance registry) with the static list
    only filling in behind it, and the candidates are **raced in parallel** — the
    first that answers with captions wins. One dead instance therefore costs nothing
    but a socket, and is then benched for PENALTY_S so it stops costing even that.

    This tier is a fallback: `media_io.download_youtube` runs it only when
    yt-dlp came back without speech, so the direct path (faster, and the
    authoritative caption picker) is always preferred where it works.

Caption policy matches `media_io._pick_captions`: manual tracks first, preferring
the video's own language, then the original-language auto captions — never a
machine-translated track, which would be a translation of a translation.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# "auto" — discover instances and race them. "off" — disable the tier entirely.
# Otherwise a comma list of explicit entries: "invidious:https://yewtu.be,piped:https://pipedapi.kavin.rocks"
RELAYS = os.getenv("MEDIA_YOUTUBE_RELAYS", "auto").strip()
RELAY_TIMEOUT_S = float(os.getenv("MEDIA_YOUTUBE_RELAY_TIMEOUT_S", "8"))
RELAY_DEADLINE_S = float(os.getenv("MEDIA_YOUTUBE_RELAY_DEADLINE_S", "15"))
RELAY_MAX_INSTANCES = int(os.getenv("MEDIA_YOUTUBE_RELAY_MAX", "10"))
RELAY_PARALLEL = int(os.getenv("MEDIA_YOUTUBE_RELAY_PARALLEL", "10"))
RELAY_MAX_MB = int(os.getenv("MEDIA_YOUTUBE_RELAY_MAX_MB", "200"))
# Pull video frames through the relay when yt-dlp got none. OFF by default: measured
# 2026-09-23, no public instance in any of the three pools actually serves media bytes
# (see the module docstring), so it is a download that reliably buys nothing and only
# adds seconds. Turn it on with a self-hosted relay, where it does work.
RELAY_FRAMES = os.getenv("MEDIA_YOUTUBE_RELAY_FRAMES", "0") != "0"
DISCOVERY_TTL_S = int(os.getenv("MEDIA_YOUTUBE_RELAY_DISCOVERY_TTL_S", "3600"))
# An instance that just failed is skipped for this long. Public instances fail in
# bulk, and re-asking 10 dead hosts on every request is most of the tier's cost.
PENALTY_S = int(os.getenv("MEDIA_YOUTUBE_RELAY_PENALTY_S", "900"))

# Last-resort list for when discovery itself is unreachable. Public instances come
# and go — this is a floor, not the source of truth; discovery replaces it.
FALLBACK_INVIDIOUS = ["https://yewtu.be", "https://inv.nadeko.net",
                      "https://invidious.nerdvpn.de", "https://invidious.f5.si"]
FALLBACK_PIPED = ["https://pipedapi.kavin.rocks", "https://pipedapi.adminforge.de",
                  "https://api.piped.private.coffee", "https://pipedapi.drgns.space",
                  "https://pipedapi.ducks.party", "https://pipedapi.reallyaweso.me"]
# cobalt has no registry that resolves (instances.cobalt.best served an invalid
# certificate on 2026-09-23), so this list is all there is for that pool.
FALLBACK_COBALT = ["https://co.otomir23.me", "https://cobalt-backend.canine.tools",
                   "https://capi.3kh0.net", "https://cobalt-api.kwiatekmiki.com",
                   "https://api.cobalt.best"]

INVIDIOUS_REGISTRY = "https://api.invidious.io/instances.json?sort_by=type,users"
PIPED_REGISTRY = "https://piped-instances.kavin.rocks/"

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/140.0.0.0 Safari/537.36")


@dataclass
class RelayCaption:
    start: float
    end: float
    text: str


@dataclass
class RelayResult:
    """One instance's answer. `kind` is the software, `instance` the base API url."""
    kind: str
    instance: str
    title: Optional[str] = None
    duration: Optional[float] = None
    captions: List[RelayCaption] = field(default_factory=list)
    caption_kind: Optional[str] = None       # "manual" | "auto"
    caption_lang: Optional[str] = None
    # Proxied media URLs — already verified to be served by the instance, not googlevideo.
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    # cobalt hands back ONE muxed file (video + audio). Downloading it twice would be
    # the same bytes, so the caller uses one path for both.
    muxed: bool = False
    error: Optional[str] = None

    @property
    def usable(self) -> bool:
        return bool(self.captions or self.audio_url)

    @property
    def score(self) -> tuple:
        return (bool(self.captions), self.caption_kind == "manual",
                bool(self.video_url), bool(self.audio_url))


def enabled() -> bool:
    return RELAYS.lower() not in {"off", "0", "false", "none", ""}


# An instance that is up but cannot get past YouTube itself is a different diagnosis
# from one that is down — it is this host's own wall, one hop further away — and it is
# the reason the public pools are unusable rather than merely flaky.
_WALLED = ("signinconfirmnotbot", "not a bot", "sign in to confirm", "login_required",
           "age-restricted", "captcha", "please sign in", "youtube.login", "youtube.token",
           "content.video.age", "error.api.youtube")
_DISABLED = ("endpoint disabled", "api disabled", "403 forbidden", "forbidden",
             "auth.jwt", "auth.key", "api.auth")


def classify(error: str) -> str:
    low = (error or "").lower()
    if any(m in low for m in _WALLED):
        return "youtube_walls_the_instance"
    if any(m in low for m in _DISABLED):
        return "instance_refuses_api_clients"
    if low.startswith(("connecterror", "connecttimeout", "readtimeout", "timeouterror",
                       "connectionerror", "remoteprotocolerror")) or "getaddrinfo" in low:
        return "instance_unreachable"
    return "instance_error"


# Instances that just failed, and until when.
_penalty: Dict[str, float] = {}


def _benched(base: str) -> bool:
    until = _penalty.get(base, 0.0)
    return bool(until and time.time() < until)


def _bench(base: str) -> None:
    _penalty[base] = time.time() + PENALTY_S


# ── caption parsing ──────────────────────────────────────────────────────────
# Each front-end hands back a different format (Invidious VTT, Piped TTML, the
# raw timedtext proxy json3), so the payload is sniffed rather than assumed.

_TS = re.compile(r"(?:(\d+):)?(\d{1,2}):(\d{2})(?:[.,](\d{1,3}))?")


def _seconds(value: str) -> Optional[float]:
    value = (value or "").strip()
    if not value:
        return None
    if value.endswith("s"):                       # TTML offset time: "12.345s"
        try:
            return float(value[:-1])
        except ValueError:
            return None
    m = _TS.fullmatch(value)
    if m:
        h, mm, ss, ms = m.groups()
        return int(h or 0) * 3600 + int(mm) * 60 + int(ss) + int((ms or "0").ljust(3, "0")) / 1000.0
    try:
        return float(value)
    except ValueError:
        return None


def _clean(text: str) -> str:
    # Caption payloads carry markup (<i>, <c.colorE5E5E5>) and karaoke <00:00:01.234> stamps.
    text = re.sub(r"<[^>]{0,80}>", " ", text)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'")
    return " ".join(text.split())


def _parse_vtt(raw: str) -> List[RelayCaption]:
    out: List[RelayCaption] = []
    for block in re.split(r"\n\s*\n", raw.replace("\r\n", "\n")):
        lines = [ln for ln in block.split("\n") if ln.strip()]
        idx = next((i for i, ln in enumerate(lines) if "-->" in ln), None)
        if idx is None:
            continue
        left, _, right = lines[idx].partition("-->")
        start = _seconds(left.strip())
        end = _seconds(right.strip().split()[0] if right.strip() else "")
        text = _clean(" ".join(lines[idx + 1:]))
        if start is None or not text:
            continue
        out.append(RelayCaption(start, end if end is not None else start + 2.0, text))
    return out


def _parse_ttml(raw: str) -> List[RelayCaption]:
    import xml.etree.ElementTree as ET

    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return []
    out: List[RelayCaption] = []
    for el in root.iter():
        tag = el.tag.rsplit("}", 1)[-1]
        if tag not in {"p", "text"}:
            continue
        # TTML uses begin/end|dur; YouTube's legacy transcript XML uses start/dur.
        start = _seconds(el.get("begin") or el.get("start") or "")
        if start is None:
            continue
        end = _seconds(el.get("end") or "")
        if end is None:
            dur = _seconds(el.get("dur") or "")
            end = start + (dur if dur is not None else 2.0)
        text = _clean("".join(el.itertext()))
        if text:
            out.append(RelayCaption(start, end, text))
    return out


def _parse_json3(raw: str) -> List[RelayCaption]:
    try:
        data = json.loads(raw)
    except ValueError:
        return []
    out: List[RelayCaption] = []
    for ev in data.get("events", []) if isinstance(data, dict) else []:
        segs, start_ms = ev.get("segs"), ev.get("tStartMs")
        if not segs or start_ms is None:
            continue
        text = _clean("".join(s.get("utf8", "") for s in segs))
        if not text:
            continue
        start = start_ms / 1000.0
        out.append(RelayCaption(start, start + ev.get("dDurationMs", 2000) / 1000.0, text))
    return out


def parse_captions(raw: str) -> List[RelayCaption]:
    """Sniff the payload and parse it, then apply the same hygiene as the yt-dlp path:
    drop [Music] / [Applause] cues and clip rolling cues at the next one's start."""
    head = raw.lstrip()[:16]
    if head.startswith("{"):
        caps = _parse_json3(raw)
    elif head.startswith("<"):
        caps = _parse_ttml(raw)
    elif head.upper().startswith("WEBVTT"):
        caps = _parse_vtt(raw)
    else:
        caps = _parse_vtt(raw) or _parse_ttml(raw) or _parse_json3(raw)
    caps = [c for c in caps if not (c.text.startswith("[") and c.text.endswith("]"))]
    caps.sort(key=lambda c: c.start)
    for a, b in zip(caps, caps[1:]):
        a.end = max(a.start + 0.2, min(a.end, b.start))
    return caps


# ── instance discovery ───────────────────────────────────────────────────────

_discovered: Dict[str, Tuple[float, List[str]]] = {}


def _body_error(resp) -> RuntimeError:
    """httpx's HTTPStatusError says only the status code, and the reason an instance
    failed is in the *body* — `SignInConfirmNotBotException`, `Endpoint disabled`. That
    string is the whole diagnosis (see classify()), so it must not be thrown away."""
    return RuntimeError(f"HTTP {resp.status_code}: {' '.join(resp.text[:300].split())}")


def _checked(resp):
    if resp.status_code >= 400:
        raise _body_error(resp)
    return resp


def _client(timeout: Optional[float] = None):
    import httpx

    return httpx.Client(timeout=timeout or RELAY_TIMEOUT_S, follow_redirects=True,
                        headers={"User-Agent": UA, "Accept": "application/json, */*"})


DISCOVERY_TIMEOUT_S = float(os.getenv("MEDIA_YOUTUBE_RELAY_DISCOVERY_TIMEOUT_S", "5"))


def _discover_all() -> None:
    """Refresh every stale registry at once. Serially, a registry that has gone away
    (Piped's took 8 s to time out when this was measured) is added straight onto the
    wall time of the request that triggered the refresh."""
    stale = [k for k in ("invidious", "piped", "cobalt")
             if not (_discovered.get(k) and time.time() - _discovered[k][0] < DISCOVERY_TTL_S)]
    if len(stale) < 2:
        return
    with ThreadPoolExecutor(max_workers=len(stale), thread_name_prefix="relay-disc") as pool:
        list(pool.map(_discover, stale))


def _public(url: str) -> bool:
    """Reachable from an ordinary host. The Invidious registry lists Yggdrasil mirrors
    with type "https", but .ygg (like .i2p / .onion) resolves only inside that overlay
    network, so from the VM they are a guaranteed timeout."""
    host = (urlparse(url).hostname or "").lower()
    return bool(host) and not host.endswith((".ygg", ".i2p", ".onion"))


def _discover(kind: str) -> List[str]:
    """Live instance list, memoised for DISCOVERY_TTL_S. A registry that is itself down
    must not take the tier down with it, so every failure falls back to the static list."""
    hit = _discovered.get(kind)
    if hit and time.time() - hit[0] < DISCOVERY_TTL_S:
        return hit[1]
    fallback = {"invidious": FALLBACK_INVIDIOUS, "piped": FALLBACK_PIPED,
                "cobalt": FALLBACK_COBALT}[kind]
    if kind == "cobalt":                          # no registry answers for this pool
        _discovered[kind] = (time.time(), list(fallback))
        return list(fallback)
    found: List[str] = []
    try:
        with _client(DISCOVERY_TIMEOUT_S) as c:
            data = c.get(INVIDIOUS_REGISTRY if kind == "invidious" else PIPED_REGISTRY).json()
        if kind == "invidious":
            # [[name, {uri, type, api, monitor…}], …]. `api` is tri-state: False means the
            # operator turned the JSON API off, None only means the registry doesn't know,
            # so excluding None would throw away instances that do answer.
            for entry in data if isinstance(data, list) else []:
                meta = entry[1] if isinstance(entry, list) and len(entry) > 1 else {}
                if isinstance(meta, dict) and meta.get("type") == "https" and meta.get("uri") \
                        and meta.get("api") is not False and _public(str(meta["uri"])):
                    found.append(str(meta["uri"]).rstrip("/"))
        else:
            for inst in data if isinstance(data, list) else []:
                if isinstance(inst, dict) and inst.get("api_url"):
                    found.append(str(inst["api_url"]).rstrip("/"))
    except Exception as exc:                      # noqa: BLE001 — registries go down too
        logger.info("[relay] %s instance discovery failed (%s) — using the built-in list.", kind, exc)
    # The registry leads: a hardcoded list goes stale within weeks (of the six Piped
    # hosts below, four had already stopped resolving by the time this was measured),
    # and an instance the registry still lists is at least alive. The static list only
    # fills in behind it, for when the registry itself is unreachable.
    out = list(found) + [u for u in fallback if u not in found]
    _discovered[kind] = (time.time(), out)
    return out


def candidates() -> List[Tuple[str, str]]:
    """[(kind, base_url)] to race, best-known first, interleaved so one dead software
    family does not consume the whole budget."""
    if not enabled():
        return []
    if RELAYS.lower() != "auto":
        out = []
        for item in RELAYS.split(","):
            item = item.strip()
            if not item:
                continue
            kind, _, base = item.partition(":")
            if base.startswith("//"):             # bare "https://host" — no kind prefix
                kind, base = ("piped" if "piped" in item else "invidious"), item
            out.append((kind.strip().lower() or "invidious", base.strip().rstrip("/")))
        return out[:RELAY_MAX_INSTANCES]
    _discover_all()
    pools = [(k, _discover(k)) for k in ("invidious", "piped", "cobalt")]
    mixed: List[Tuple[str, str]] = []
    # Interleave the pools so one dead software family cannot eat the whole budget,
    # and so a request never depends on the ordering inside a single registry.
    for i in range(max((len(v) for _, v in pools), default=0)):
        for kind, urls in pools:
            if i < len(urls) and not _benched(urls[i]):
                mixed.append((kind, urls[i]))
    return mixed[:RELAY_MAX_INSTANCES]


# ── per-software adapters ────────────────────────────────────────────────────

def _proxied(url: Optional[str], instance: str) -> Optional[str]:
    """Keep a media URL only if the *instance* serves it. A format URL pointing at
    googlevideo.com is no use here: fetching it would leave from this host's IP, which
    is the address YouTube already refused."""
    if not url:
        return None
    host = (urlparse(url).hostname or "").lower()
    inst_host = (urlparse(instance).hostname or "").lower()
    if not host:
        return None
    if "googlevideo.com" in host or host.endswith("youtube.com"):
        return None
    # Piped serves media from sibling pipedproxy-* hosts, not the API host itself.
    root = ".".join(inst_host.split(".")[-2:])
    return url if root and root in host else None


def _pick_track(tracks: List[Dict], video_lang: str) -> Optional[Dict]:
    """Manual first (video's language, then English, then anything), else the
    original-language auto track. Machine translations never qualify."""
    def lang_of(t: Dict) -> str:
        return str(t.get("lang") or "").split("-")[0].lower()

    manual = [t for t in tracks if not t.get("auto")]
    auto = [t for t in tracks if t.get("auto")]
    for pool in (manual, auto):
        if not pool:
            continue
        return sorted(pool, key=lambda t: (lang_of(t) != video_lang, lang_of(t) != "en", lang_of(t)))[0]
    return None


def _fetch_invidious(client, base: str, video_id: str) -> RelayResult:
    r = RelayResult(kind="invidious", instance=base)
    # local=true rewrites the format URLs to the instance's own /videoplayback proxy.
    resp = _checked(client.get(f"{base}/api/v1/videos/{video_id}",
                               params={"local": "true", "hl": "en"}))
    data = resp.json()
    if not isinstance(data, dict) or data.get("error"):
        raise RuntimeError(str(data.get("error") if isinstance(data, dict) else "bad response")[:160])
    if data.get("liveNow"):
        raise RuntimeError("live stream")
    r.title = data.get("title")
    r.duration = float(data.get("lengthSeconds") or 0) or None
    video_lang = str(data.get("language") or "").split("-")[0].lower()

    tracks = []
    for cap in data.get("captions") or []:
        url = str(cap.get("url") or "")
        if not url:
            continue
        label = str(cap.get("label") or "")
        tracks.append({"lang": cap.get("language_code") or cap.get("languageCode") or "",
                       "auto": "auto-generated" in label.lower(),
                       "url": url if url.startswith("http") else f"{base}{url}"})
    chosen = _pick_track(tracks, video_lang)
    if chosen:
        r.caption_kind = "auto" if chosen["auto"] else "manual"
        r.caption_lang = str(chosen["lang"] or "en").split("-")[0]
        r.captions = parse_captions(client.get(chosen["url"]).text)

    formats = list(data.get("adaptiveFormats") or []) + list(data.get("formatStreams") or [])
    r.video_url = _pick_stream(formats, base, want="video")
    r.audio_url = _pick_stream(formats, base, want="audio")
    return r


def _fetch_piped(client, base: str, video_id: str) -> RelayResult:
    r = RelayResult(kind="piped", instance=base)
    resp = _checked(client.get(f"{base}/streams/{video_id}"))
    data = resp.json()
    if not isinstance(data, dict) or data.get("error"):
        raise RuntimeError(str(data.get("error") if isinstance(data, dict) else "bad response")[:160])
    if data.get("livestream"):
        raise RuntimeError("live stream")
    r.title = data.get("title")
    r.duration = float(data.get("duration") or 0) or None

    tracks = [{"lang": s.get("code") or "", "auto": bool(s.get("autoGenerated")), "url": s.get("url")}
              for s in data.get("subtitles") or [] if s.get("url")]
    chosen = _pick_track(tracks, "")
    if chosen:
        r.caption_kind = "auto" if chosen["auto"] else "manual"
        r.caption_lang = str(chosen["lang"] or "en").split("-")[0]
        # Piped hands out a timedtext proxy URL with fmt=ttml; json3 carries the same
        # cues with exact durations, so ask for it and fall back to whatever arrives.
        url = re.sub(r"fmt=[a-z0-9]+", "fmt=json3", chosen["url"])
        r.captions = parse_captions(client.get(url).text) or parse_captions(client.get(chosen["url"]).text)

    r.video_url = _pick_stream(data.get("videoStreams") or [], base, want="video")
    r.audio_url = _pick_stream(data.get("audioStreams") or [], base, want="audio")
    return r


def _pick_stream(formats: List[Dict], instance: str, want: str) -> Optional[str]:
    """Smallest usable proxied stream: ≤360p H.264 mp4 for frames, or the lowest-bitrate
    audio. Resolution is capped because the frames are only read by OCR / the VLM, and a
    relay proxy is a shared resource — a 1080p pull would be rude and slow."""
    scored: List[Tuple[tuple, str]] = []
    for f in formats:
        url = _proxied(f.get("url"), instance)
        if not url:
            continue
        mime = str(f.get("type") or f.get("mimeType") or "")
        quality = str(f.get("qualityLabel") or f.get("resolution") or f.get("quality") or "")
        height = int(m.group(1)) if (m := re.search(r"(\d{3,4})p", quality)) else 0
        bitrate = int(f.get("bitrate") or 0)
        is_video = mime.startswith("video") or bool(height)
        if want == "video":
            if not is_video or not mime.startswith("video"):
                continue
            if height and height > 480:
                continue
            # mp4/avc1 decodes everywhere; webm/vp9 needs a codec PyAV may not carry.
            scored.append(((0 if "mp4" in mime else 1, 0 if "avc1" in mime else 1,
                            abs(height - 360), bitrate), url))
        else:
            if not mime.startswith("audio"):
                continue
            scored.append(((0 if "mp4" in mime or "m4a" in mime else 1, bitrate or 1_000_000), url))
    if not scored:
        return None
    return min(scored, key=lambda s: s[0])[1]


def _fetch_cobalt(client, base: str, video_id: str) -> RelayResult:
    """cobalt is a downloader, not a front-end: it has no captions API, and it answers
    with ONE muxed 360p file. That still makes a quiz — audio for ASR, frames for OCR —
    it just costs a Whisper pass instead of reading a caption track, so this pool is
    only reached when neither of the other two could produce captions."""
    r = RelayResult(kind="cobalt", instance=base)
    resp = client.post(base + "/", json={"url": f"https://www.youtube.com/watch?v={video_id}",
                                         "downloadMode": "auto", "videoQuality": "360",
                                         "youtubeVideoCodec": "h264", "filenameStyle": "basic"},
                       headers={"Content-Type": "application/json",
                                # cobalt checks this exactly and refuses the client
                                # default ("application/json, */*") outright.
                                "Accept": "application/json"})
    data = resp.json() if "json" in resp.headers.get("content-type", "") else {}
    status = str(data.get("status") or "")
    if status == "error" or not data:
        # cobalt reports refusals in the body with a 400, so the code matters more
        # than the status: "error.api.youtube.login" is the wall, "auth.jwt.missing"
        # is an instance that now wants an API key.
        raise RuntimeError(str((data.get("error") or {}).get("code") or _body_error(resp)))
    if status not in {"tunnel", "redirect"}:
        # "picker" is a multi-part answer (a gallery); nothing to do with a lecture video.
        raise RuntimeError(f"unsupported cobalt status {status!r}")
    r.title = os.path.splitext(str(data.get("filename") or ""))[0] or None
    r.video_url = r.audio_url = str(data["url"])
    r.muxed = True
    return r


_ADAPTERS: Dict[str, Callable] = {"invidious": _fetch_invidious, "piped": _fetch_piped,
                                  "cobalt": _fetch_cobalt}


# ── the race ─────────────────────────────────────────────────────────────────

def fetch(video_id: str, attempts: Optional[List[Dict]] = None) -> Optional[RelayResult]:
    """Race every candidate instance and return the best answer, or None.

    Instances fail constantly — rate limits, their own IP blocks, plain downtime —
    so they are asked all at once rather than in a chain: the wall time is one
    instance's, not the sum. The first answer carrying captions ends the race; a
    stream-only answer is kept in case nothing better arrives.

    `attempts`, when given, is filled with one dict per instance for the diagnosis.
    """
    cands = candidates()
    if not cands:
        return None
    try:
        import httpx                               # noqa: F401 — the adapters need it
    except ImportError:
        logger.info("[relay] httpx is not installed — relay tier unavailable.")
        return None

    t0 = time.perf_counter()
    best: Optional[RelayResult] = None

    def one(kind: str, base: str) -> RelayResult:
        with _client() as c:
            return _ADAPTERS[kind](c, base, video_id)

    workers = max(1, min(RELAY_PARALLEL, len(cands)))
    pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="relay")
    try:
        futures = {pool.submit(one, kind, base): (kind, base) for kind, base in cands if kind in _ADAPTERS}
        # A hard deadline, not a per-instance timeout: this tier sits in front of a
        # learner waiting on a request, and the whole point of racing is that the slowest
        # instance must not set the wall time.
        for fut in as_completed(futures, timeout=RELAY_DEADLINE_S):
            kind, base = futures[fut]
            try:
                res = fut.result()
            except Exception as exc:               # noqa: BLE001 — a dead instance is the norm
                msg = f"{type(exc).__name__}: {exc}"
                _bench(base)
                logger.debug("[relay] %s %s failed: %s", kind, base, msg[:160])
                if attempts is not None:
                    attempts.append({"kind": kind, "instance": base, "ok": False,
                                     "why": classify(msg), "error": msg[:160]})
                continue
            if attempts is not None:
                attempts.append({"kind": kind, "instance": base, "ok": True, "title": res.title,
                                 "captions": len(res.captions), "caption_kind": res.caption_kind,
                                 "caption_lang": res.caption_lang, "video_stream": bool(res.video_url),
                                 "audio_stream": bool(res.audio_url), "muxed": res.muxed})
            if res.usable and (best is None or res.score > best.score):
                best = res
            elif not res.usable:
                _bench(base)                       # answered, but with nothing we can use
            if best is not None and best.captions:
                break                              # captions are the whole point; stop paying for the rest
    except TimeoutError:
        logger.info("[relay] the instance race hit the %.0fs deadline", RELAY_DEADLINE_S)
        for fut, (_, base) in futures.items():
            if not fut.done():
                _bench(base)
    finally:
        # Don't wait on the losers: they are network reads that will time out on their own.
        pool.shutdown(wait=False, cancel_futures=True)

    if best:
        logger.info("[relay] %s %s answered in %.1fs: %d caption cues (%s/%s), video=%s audio=%s",
                    best.kind, best.instance, time.perf_counter() - t0, len(best.captions),
                    best.caption_kind, best.caption_lang, bool(best.video_url), bool(best.audio_url))
    else:
        logger.info("[relay] no instance could serve %s (%.1fs, %d tried)",
                    video_id, time.perf_counter() - t0, len(cands))
    return best


def download(url: str, dest: str) -> Optional[str]:
    """Stream one proxied media file to `dest`. Capped by RELAY_MAX_MB, because a relay
    is somebody else's bandwidth and a wrong format pick must not fill the disk."""
    import httpx

    limit = RELAY_MAX_MB * 1024 * 1024
    size = 0
    try:
        with _client(RELAY_TIMEOUT_S * 10) as c, c.stream("GET", url) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as out:
                for block in resp.iter_bytes(512 * 1024):
                    size += len(block)
                    if size > limit:
                        raise RuntimeError(f"stream exceeded {RELAY_MAX_MB} MB")
                    out.write(block)
    except Exception as exc:                        # noqa: BLE001 — frames are optional
        logger.warning("[relay] download failed (%s): %s", type(exc).__name__, str(exc)[:160])
        try:
            os.path.exists(dest) and os.remove(dest)
        except OSError:
            pass
        return None
    return dest if size > 0 else None


def diagnosis(video_id: Optional[str]) -> Dict:
    """What the relay tier can reach from this host — the companion to the per-client
    report in `media_io.youtube_diagnosis`, and the thing that answers "is the IP wall
    the end of the road?" with a yes or a no."""
    if not enabled():
        return {"enabled": False}
    out: Dict = {"enabled": True, "mode": "auto" if RELAYS.lower() == "auto" else "explicit",
                 "candidates": [f"{k}:{b}" for k, b in candidates()]}
    if not video_id:
        return {**out, "skipped": "no video id"}
    tried: List[Dict] = []
    best = fetch(video_id, attempts=tried)
    out["tried"] = tried
    out["working"] = [a["instance"] for a in tried if a.get("ok") and (a.get("captions") or a.get("audio_stream"))]
    why: Dict[str, int] = {}
    for a in tried:
        if not a.get("ok"):
            why[a.get("why") or "instance_error"] = why.get(a.get("why") or "instance_error", 0) + 1
    out["failures"] = why
    # The finding that matters: if the public instances are refused by YouTube for the
    # same reason this host is, the pool is not a way around the wall — it is the wall
    # again, one hop further out, and only a self-hosted relay or cookies will do.
    out["pools_are_walled_too"] = bool(why.get("youtube_walls_the_instance")) and not out["working"]
    out["best"] = ({"kind": best.kind, "instance": best.instance, "cues": len(best.captions),
                    "caption_kind": best.caption_kind, "caption_lang": best.caption_lang,
                    "video_stream": bool(best.video_url), "audio_stream": bool(best.audio_url)}
                   if best else None)
    return out
