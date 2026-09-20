"""
FILE: routers/media_quiz.py
─────────────────────────────────────────────────────────────────────────────
Media → quiz endpoints for the Assessment Studio (mounted at /api/v1/rag/media).

  POST /upload        multipart: file (video/audio), difficulty, target_lang
  POST /youtube       JSON: {url, difficulty, target_lang}
  GET  /capabilities  which backends (ASR / OCR / VLM / yt-dlp) are available

The generated quiz is stored in routers.rag.QUIZ_STORE in the same shape as a
document quiz, so the existing POST /api/v1/rag/grade grades it unchanged
(evidence write, iGOT sync). The pipeline lives in services/media_quiz/.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import importlib.util
import logging
import os
import shutil
import threading
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from routers.rag import QUIZ_STORE, QuizQuestion
from services.practice_assessment import media_question_difficulty
from services.media_quiz import extractors, media_io
from services.media_quiz.llm import LLMUnavailable
from services.media_quiz.pipeline import NotLearnable, run, warm_up

logger = logging.getLogger(__name__)
router = APIRouter()


@router.on_event("startup")
async def _warm_media_models() -> None:
    # Whisper / RapidOCR / VAD load in the background so the first media quiz starts
    # warm. MEDIA_WARMUP=0 turns it off (e.g. small hosts without the media extras).
    if os.getenv("MEDIA_WARMUP", "1") != "0" and importlib.util.find_spec("faster_whisper"):
        threading.Thread(target=warm_up, name="media-warm-up", daemon=True).start()

MAX_MEDIA_BYTES = int(os.getenv("MEDIA_MAX_UPLOAD_MB", "1024")) * 1024 * 1024
MEDIA_EXTS = media_io.MEDIA_VIDEO_EXTS | media_io.MEDIA_AUDIO_EXTS
DIFFICULTIES = {"Easy", "Medium", "Hard"}


@lru_cache(maxsize=None)
def _importable(module: str) -> bool:
    """Really import it. find_spec() only proves the wheel is on disk — OpenCV's wheel
    is installed but fails to load without libGL/libglib on a headless server."""
    if importlib.util.find_spec(module) is None:
        return False
    try:
        importlib.import_module(module)
        return True
    except Exception as exc:                    # noqa: BLE001 — a broken install is "not available"
        logger.warning("[media] %s is installed but will not import: %s", module, exc)
        return False


def _missing_dep_message(exc: ImportError) -> str:
    text = str(exc)
    if ".so" in text or "DLL" in text:
        # e.g. "libGL.so.1: cannot open shared object file" — rapidocr pulls in the full
        # opencv-python wheel, which needs these system libraries even on a headless host.
        return (f"A system library the video decoder needs is missing ({text}). On the server run: "
                f"sudo apt-get install -y libgl1 libglib2.0-0")
    return f"Media dependencies missing ({text}). Run: pip install -r requirements-media.txt"


class MediaQuizQuestion(QuizQuestion):
    evidence: List[str] = Field(default_factory=list, description="Timeline evidence ids backing the answer")
    kind: str = Field("chunk", description="'chunk' or 'synthesis' (cross-section)")
    answer_type: str = "concept"
    t_start: Optional[float] = Field(None, description="Seconds into the media where the evidence starts")
    t_end: Optional[float] = None
    review: Dict[str, Any] = Field(default_factory=dict, description="Fact-check status: ok | flagged | no_reference | unchecked")


class MediaMetadata(BaseModel):
    filename: str
    file_type: str
    file_size_bytes: int
    duration_s: float
    character_count: int
    word_count: int
    chunk_count: int
    source: str = Field(..., description="'upload' or 'youtube'")


class MediaQuizResponse(BaseModel):
    status: str = "success"
    message: str
    quiz_id: str
    filename: str
    file_type: str
    competency_id: Optional[str] = None
    skill_name: str
    questions: List[MediaQuizQuestion]
    metadata: MediaMetadata
    media: Dict[str, Any] = Field(..., description="Probe, routing, evidence counts, validator + fact-check report")
    evidence: List[Dict[str, Any]] = Field(default_factory=list, description="The evidence records the questions cite")


class YoutubeRequest(BaseModel):
    url: str
    difficulty: str = "Medium"
    target_lang: Optional[str] = None


async def _process(media: media_io.MediaSource, filename: str, ext: str, size: int, difficulty: str,
                   target_lang: Optional[str], source: str) -> MediaQuizResponse:
    difficulty = difficulty if difficulty in DIFFICULTIES else "Medium"
    try:
        result = await run(media, difficulty=difficulty, target_lang=(target_lang or None))
    except NotLearnable as exc:
        # A clean, explained rejection instead of hallucinated questions.
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail={"message": str(exc), "media": exc.report})
    except LLMUnavailable as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Question generation failed: {exc}")
    except ImportError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=_missing_dep_message(exc))
    except media_io.MediaInputError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:                    # noqa: BLE001
        # Anything else is a bug or an unreadable file. Without this the learner gets
        # uvicorn's bare "Internal Server Error" page and the cause is only in the log.
        logger.exception("[media] pipeline failed for %s (%s)", filename, source)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Could not process this file: {type(exc).__name__}: {exc}")

    skill_name = result.competency_name or "General Learning"
    questions = [MediaQuizQuestion(**q.to_dict(), difficulty=media_question_difficulty(difficulty, q.kind))
                 for q in result.questions]
    quiz_id = f"QZ-{uuid.uuid4().hex[:8].upper()}"
    QUIZ_STORE[quiz_id] = {
        "quiz_id": quiz_id,
        # Per-question difficulty for the difficulty-aware skill update at /grade:
        # the quiz's target level, one step harder for cross-section synthesis questions.
        "questions": [QuizQuestion(question=q.question, options=q.options, correct_answer=q.correct_answer,
                                   explanation=q.explanation, difficulty=q.difficulty) for q in questions],
        "difficulty": difficulty,
        "filename": filename,
        "extracted_text": result.transcript_excerpt,
        "chunk_count": len(result.report.get("chunks", [])),
        "competency_id": result.competency_id,      # None for general (non-FRAC) study videos
        "skill_name": skill_name,
        "source_type": f"media:{result.report.get('content_type')}",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    text = result.transcript_excerpt
    ctype = result.report.get("content_type", "")
    flagged = result.report.get("fact_check", {}).get("flagged", 0)
    return MediaQuizResponse(
        message=(f"Detected: {ctype.replace('_', ' ')}. Generated {len(questions)} evidence-cited questions "
                 f"from {filename}" + (f" ({flagged} flagged for trainer review)." if flagged else ".")),
        quiz_id=quiz_id, filename=filename, file_type=ext,
        competency_id=result.competency_id, skill_name=skill_name,
        questions=questions,
        metadata=MediaMetadata(
            filename=filename, file_type=ext, file_size_bytes=size,
            duration_s=round(result.report.get("probe", {}).get("duration", 0.0), 1),
            character_count=len(text), word_count=len(text.split()),
            chunk_count=len(result.report.get("chunks", [])), source=source,
        ),
        media=result.report,
        evidence=result.evidence,
    )


@router.post("/upload", response_model=MediaQuizResponse,
             summary="Generate an evidence-cited quiz from a video or audio file")
async def upload_media(
    file: UploadFile = File(..., description="Video (.mp4, .mkv, .webm, .mov…) or audio (.mp3, .wav, .m4a…)"),
    difficulty: str = Form("Medium"),
    target_lang: Optional[str] = Form(None),
) -> MediaQuizResponse:
    filename = os.path.basename(file.filename or "")
    ext = os.path.splitext(filename.lower())[1]
    if ext not in MEDIA_EXTS:
        raise HTTPException(status_code=400, detail=f"Unsupported media format '{ext}'. "
                                                    f"Allowed: {', '.join(sorted(MEDIA_EXTS))}")
    workdir = media_io.temp_dir()
    path = os.path.join(workdir, f"upload{ext}")
    size = 0
    try:
        with open(path, "wb") as out:                 # stream to disk; media can be large
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_MEDIA_BYTES:
                    raise HTTPException(status_code=413, detail=f"File exceeds {MAX_MEDIA_BYTES // (1024 * 1024)} MB.")
                out.write(chunk)
        await file.close()
        if size == 0:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")
        return await _process(media_io.MediaSource.from_file(path, filename), filename, ext, size,
                              difficulty, target_lang, "upload")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


@router.post("/youtube", response_model=MediaQuizResponse,
             summary="Generate an evidence-cited quiz from a YouTube link")
async def youtube_media(payload: YoutubeRequest) -> MediaQuizResponse:
    import asyncio

    workdir = media_io.temp_dir()
    try:
        try:
            media = await asyncio.to_thread(media_io.download_youtube, payload.url, workdir)
        except media_io.MediaInputError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc))
        size = sum(os.path.getsize(p) for p in {media.video_path, media.audio_path} if p)
        return await _process(media, media.title, ".youtube", size, payload.difficulty,
                              payload.target_lang, "youtube")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


@router.get("/youtube/diagnose", summary="Why YouTube links fail from this host")
async def youtube_diagnose(url: str = "https://www.youtube.com/watch?v=dMRDzicSvXk",
                           clients: Optional[str] = None) -> JSONResponse:
    """YouTube blocks by IP reputation, so the same link works from a laptop and fails
    from the server. This reports what this host can reach — yt-dlp version, JS runtimes,
    per-player-client outcome, watch-page reachability — without downloading anything."""
    import asyncio

    if not media_io.is_youtube_url(url):
        raise HTTPException(status_code=400, detail="Only YouTube links can be diagnosed.")
    try:
        chain = [c.strip() for c in clients.split(",") if c.strip()] if clients else None
        return JSONResponse(await asyncio.to_thread(media_io.youtube_diagnosis, url, chain))
    except Exception as exc:                    # noqa: BLE001 — a diagnosis must always answer
        logger.exception("[media] youtube diagnosis failed")
        return JSONResponse({"error": f"{type(exc).__name__}: {exc}"}, status_code=200)


@router.get("/capabilities", summary="Which media backends are installed / configured")
def capabilities() -> JSONResponse:          # sync: _importable() really imports, so keep it off the event loop
    has = _importable
    return JSONResponse({
        "asr": {"available": has("faster_whisper"), "model": extractors.WHISPER_MODEL},
        "vad": {"available": has("faster_whisper"), "model": "silero (bundled with faster-whisper)"},
        "ocr": {"available": has("rapidocr_onnxruntime"), "engine": "RapidOCR (PaddleOCR models, ONNX)"},
        "video": {"available": has("cv2") and has("av")},
        "vlm": {"backend": extractors.vlm_backend(), "label": extractors.vlm_label()},
        "youtube": {"available": has("yt_dlp"), "max_duration_s": media_io.YOUTUBE_MAX_DURATION_S,
                    # YouTube blocks datacenter IPs; these say which work-arounds are configured.
                    "player_clients": media_io._yt_clients(),
                    "cookies": media_io.has_cookies(),
                    "proxy": bool(media_io.YOUTUBE_PROXY),
                    "pot_provider": bool(media_io.YOUTUBE_POT_URL)},
        "accepted_extensions": sorted(MEDIA_EXTS),
        "max_upload_mb": MAX_MEDIA_BYTES // (1024 * 1024),
    })
