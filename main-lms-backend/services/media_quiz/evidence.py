"""
FILE: services/media_quiz/evidence.py
─────────────────────────────────────────────────────────────────────────────
One shared timeline for everything the media pipeline extracts.

Every tool (ASR, OCR, VLM) writes the same record:

    {"id": "e42", "t_start": 312.4, "t_end": 327.9,
     "source": "asr" | "ocr" | "vlm", "text": "...", "confidence": 0.87, "lang": "hi"}

Low-confidence evidence is dropped before question generation (flaw 4), and
questions must cite evidence ids that the validator can look up here.

Chunking:
  • visual routes — one chunk per keyframe: its OCR/VLM evidence plus the speech
    from the slide's display window *and the next ALIGN_TAIL_S seconds*
    (flaw 9: speakers talk about a slide just after it appears).
  • talking head — speech windows of ~CHUNK_WINDOW_S seconds.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from typing import Dict, Iterable, List, Optional

MIN_CONFIDENCE = float(os.getenv("MEDIA_MIN_CONFIDENCE", "0.45"))
ALIGN_TAIL_S = float(os.getenv("MEDIA_ALIGN_TAIL_S", "20"))
CHUNK_WINDOW_S = float(os.getenv("MEDIA_CHUNK_WINDOW_S", "90"))
CHUNK_MAX_CHARS = 1800


@dataclass
class Evidence:
    id: str
    t_start: float
    t_end: float
    source: str            # "asr" | "ocr" | "vlm"
    text: str
    confidence: float
    lang: str = "en"
    meta: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["t_start"] = round(self.t_start, 2)
        d["t_end"] = round(self.t_end, 2)
        d["confidence"] = round(self.confidence, 3)
        return d


@dataclass
class Chunk:
    id: str
    t_start: float
    t_end: float
    evidence_ids: List[str]
    text: str               # evidence lines tagged with their ids, as shown to the LLM
    plain: str              # untagged text, used for embeddings
    relevance: Optional[float] = None
    competency_id: Optional[str] = None


def fmt_ts(seconds: float) -> str:
    s = int(max(0, seconds))
    return f"{s // 3600:d}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60:02d}:{s % 60:02d}"


class Timeline:
    def __init__(self) -> None:
        self._items: Dict[str, Evidence] = {}
        self.dropped: Dict[str, int] = {}      # reason → count (reported to the trainer / eval)
        self._n = 0

    # ── writing ───────────────────────────────────────────────────────────────
    def add(self, t_start: float, t_end: float, source: str, text: str, confidence: float,
            lang: str = "en", **meta) -> Optional[Evidence]:
        text = " ".join((text or "").split())
        if not text:
            return None
        self._n += 1
        ev = Evidence(f"e{self._n}", float(t_start), float(max(t_end, t_start)), source, text,
                      float(max(0.0, min(1.0, confidence))), lang or "en", dict(meta))
        self._items[ev.id] = ev
        return ev

    def drop(self, reason: str, n: int = 1) -> None:
        self.dropped[reason] = self.dropped.get(reason, 0) + n

    def prune_low_confidence(self, threshold: float = MIN_CONFIDENCE) -> int:
        weak = [k for k, e in self._items.items() if e.confidence < threshold]
        for k in weak:
            self.drop(f"low_confidence_{self._items[k].source}")
            del self._items[k]
        return len(weak)

    # ── reading ───────────────────────────────────────────────────────────────
    def get(self, eid: str) -> Optional[Evidence]:
        return self._items.get(eid)

    def all(self, source: Optional[str] = None) -> List[Evidence]:
        items = sorted(self._items.values(), key=lambda e: (e.t_start, e.id))
        return [e for e in items if source is None or e.source == source]

    def overlapping(self, t0: float, t1: float, source: Optional[str] = None) -> List[Evidence]:
        return [e for e in self.all(source) if e.t_start < t1 and e.t_end > t0]

    def counts(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for e in self._items.values():
            out[e.source] = out.get(e.source, 0) + 1
        return out

    def __len__(self) -> int:
        return len(self._items)

    def to_list(self) -> List[Dict]:
        return [e.to_dict() for e in self.all()]


def _tag(e: Evidence) -> str:
    return f"[{e.id} | {e.source} | {fmt_ts(e.t_start)}-{fmt_ts(e.t_end)} | {e.lang}] {e.text}"


def _make_chunk(idx: int, evs: Iterable[Evidence]) -> Optional[Chunk]:
    evs = sorted({e.id: e for e in evs}.values(), key=lambda e: (e.source != "ocr", e.source != "vlm", e.t_start))
    if not evs:
        return None
    lines, plain, used, size = [], [], [], 0
    for e in evs:
        line = _tag(e)
        if size + len(line) > CHUNK_MAX_CHARS and used:
            break
        lines.append(line)
        plain.append(e.text)
        used.append(e.id)
        size += len(line)
    return Chunk(
        id=f"c{idx}",
        t_start=min(e.t_start for e in evs),
        t_end=max(e.t_end for e in evs),
        evidence_ids=used,
        text="\n".join(lines),
        plain=" ".join(plain),
    )


def build_chunks(timeline: Timeline, slide_windows: List[Dict]) -> List[Chunk]:
    """
    slide_windows: [{"t_start", "t_end", "evidence_ids": [ocr/vlm ids of that keyframe]}],
    in display order. Empty for talking-head / audio-only content.
    """
    chunks: List[Chunk] = []
    speech = timeline.all("asr")
    attached: set = set()

    for w in slide_windows:
        visual = [timeline.get(i) for i in w["evidence_ids"]]
        visual = [v for v in visual if v is not None]
        talk = [e for e in speech if e.t_start < w["t_end"] + ALIGN_TAIL_S and e.t_end > w["t_start"]]
        attached.update(e.id for e in talk)
        c = _make_chunk(len(chunks) + 1, visual + talk)
        if c and (visual or len(c.plain) > 120):
            chunks.append(c)

    # Speech not covered by any slide window (or all speech, for talking heads).
    window: List[Evidence] = []
    for e in speech:
        if e.id in attached:
            continue
        if window and (e.t_end - window[0].t_start > CHUNK_WINDOW_S
                       or sum(len(x.text) for x in window) > CHUNK_MAX_CHARS - 200):
            c = _make_chunk(len(chunks) + 1, window)
            if c:
                chunks.append(c)
            window = []
        window.append(e)
    if window:
        c = _make_chunk(len(chunks) + 1, window)
        if c:
            chunks.append(c)

    # Merge tiny chunks forward so every chunk can carry a question.
    merged: List[Chunk] = []
    for c in sorted(chunks, key=lambda c: c.t_start):
        if merged and len(merged[-1].plain) < 150:
            prev = merged.pop()
            evs = [timeline.get(i) for i in prev.evidence_ids + c.evidence_ids]
            c = _make_chunk(0, [e for e in evs if e]) or c
        merged.append(c)
    for i, c in enumerate(merged, 1):
        c.id = f"c{i}"
    return merged
