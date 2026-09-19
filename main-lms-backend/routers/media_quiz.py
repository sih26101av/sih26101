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
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from routers.rag import QUIZ_STORE, QuizQuestion
from services.practice_assessment import media_question_difficulty
from services.media_quiz import extractors, media_io
from services.media_quiz.llm import LLMUnavailable
from services.media_quiz.pipeline import NotLearnable, run

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_MEDIA_BYTES = int(os.getenv("MEDIA_MAX_UPLOAD_MB", "1024")) * 1024 * 1024
MEDIA_EXTS = media_io.MEDIA_VIDEO_EXTS | media_io.MEDIA_AUDIO_EXTS
DIFFICULTIES = {"Easy", "Medium", "Hard"}


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
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Media dependencies missing ({exc}). Run: pip install -r requirements-media.txt")

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


@router.get("/capabilities", summary="Which media backends are installed / configured")
async def capabilities() -> JSONResponse:
    has = lambda m: importlib.util.find_spec(m) is not None  # noqa: E731
    return JSONResponse({
        "asr": {"available": has("faster_whisper"), "model": extractors.WHISPER_MODEL},
        "vad": {"available": has("faster_whisper"), "model": "silero (bundled with faster-whisper)"},
        "ocr": {"available": has("rapidocr_onnxruntime"), "engine": "RapidOCR (PaddleOCR models, ONNX)"},
        "video": {"available": has("cv2") and has("av")},
        "vlm": {"backend": extractors.vlm_backend(), "label": extractors.vlm_label()},
        "youtube": {"available": has("yt_dlp"), "max_duration_s": media_io.YOUTUBE_MAX_DURATION_S},
        "accepted_extensions": sorted(MEDIA_EXTS),
        "max_upload_mb": MAX_MEDIA_BYTES // (1024 * 1024),
    })
