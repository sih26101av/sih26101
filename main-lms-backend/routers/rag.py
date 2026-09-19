"""
FILE: routers/rag.py
─────────────────────────────────────────────────────────────────────────────
RAG Document-to-Quiz Router
MoSPI Skill Intelligence Platform | SIH 2026

Handles document ingestion (PDF incl. OCR of scanned pages, PPTX, DOCX, TXT),
generates a configurable number (3-20) of source-cited objective questions —
MCQ, True/False, multi-select, fill-in-the-blank, numeric — through the
validated pipeline in services/doc_quiz (optionally in Hindi / bilingual),
and grades any quiz in QUIZ_STORE (document or media) with personalised
feedback, response-calibrated item difficulty and competency sync to iGOT.
─────────────────────────────────────────────────────────────────────────────
"""

import io
import os
import re
import uuid
import asyncio
import logging
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple, List

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from auth.database import SessionLocal, engine, get_db
from auth.dependencies import get_current_user
from auth.models import UserAuth
from models.models import (
    Base,
    Competency,
    UserCompetency,
    CompetencyProfile,
    Official,
    Assessment,
    EvidenceLog,
    QuizAttempt,
)
from fastapi import Depends
from services import app_state
from services import practice_assessment as pa
from services.doc_quiz import calibration as calib
from services.doc_quiz import items as qitems

# Load environment variables (such as GEMINI_API_KEY, IGOT_COMPETENCIES_UPDATE_URL)
load_dotenv()

# PDF/PPTX extraction, LangChain and Gemini are imported inside the functions
# that use them: langchain_text_splitters alone pulls in torch + transformers
# (~20 s), which kept the server from binding its port at startup.

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

# ── Configuration Constants ───────────────────────────────────────────────────
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB max limit
SUPPORTED_EXTENSIONS = {".pdf", ".ppt", ".pptx", ".txt", ".docx", ".doc"}


# =============================================================================
# PYDANTIC SCHEMAS
# =============================================================================

class QuizQuestion(BaseModel):
    # Media quizzes and the demo quiz set only the first five fields → type "mcq".
    question: str = Field(..., description="The quiz question text (fill_blank: contains _____)")
    options: List[str] = Field(default_factory=list, description="Choices (mcq: 4, true_false: True/False, multi_select: 4-6); empty for fill_blank / numeric")
    correct_answer: int = Field(-1, description="Zero-based index of the correct option (mcq, true_false); -1 otherwise")
    explanation: str = Field(..., description="Detailed explanation for why the answer is correct")
    difficulty: Optional[str] = Field(None, description="Effective Easy | Medium | Hard — the calibrated class once the item has response data, else the generator's tag")
    type: str = Field("mcq", description="mcq | true_false | multi_select | fill_blank | numeric")
    correct_answers: Optional[List[int]] = Field(None, description="multi_select: indices of all correct options")
    answer_text: Optional[str] = Field(None, description="fill_blank: the expected term")
    accepted_answers: Optional[List[str]] = Field(None, description="fill_blank: accepted alternatives")
    numeric_answer: Optional[float] = Field(None, description="numeric: the answer")
    tolerance: Optional[float] = Field(None, description="numeric: absolute tolerance (default 1 %)")
    unit: Optional[str] = Field(None, description="numeric: unit shown next to the input")
    expression: Optional[str] = Field(None, description="numeric: arithmetic the answer was verified against")
    solution: Optional[str] = Field(None, description="numeric: one-line working, shown after grading")
    why_wrong: Optional[List[str]] = Field(None, description="Per-option reason it is wrong (personalised feedback)")
    citations: Optional[List[Dict[str, Any]]] = Field(None, description="[{chunkId, locator, quote, passage}] — the source passage supporting the answer")
    answer_type: Optional[str] = Field(None, description="number | definition | concept | procedure (fact-check)")
    review: Optional[Dict[str, Any]] = Field(None, description="Fact-check status: ok | flagged | no_reference | unchecked")
    llm_difficulty: Optional[str] = Field(None, description="The generator's own difficulty tag")
    calibration: Optional[Dict[str, Any]] = Field(None, description="Response-data calibration (services/doc_quiz/calibration.py)")
    item_key: Optional[str] = Field(None, description="Content hash keying the item's response statistics")
    translations: Optional[Dict[str, Dict[str, Any]]] = Field(None, description='{"hi": {question, options, explanation, why_wrong, answer_text, unit, solution}}')


class QuizPayload(BaseModel):
    questions: List[QuizQuestion] = Field(..., description="Generated questions")


class DocumentMetadata(BaseModel):
    filename: str = Field(..., description="Original name of the uploaded file")
    file_type: str = Field(..., description="Detected file extension (.pdf, .ppt, .pptx, .docx, .txt)")
    file_size_bytes: int = Field(..., description="Size of the uploaded file in bytes")
    character_count: int = Field(..., description="Total extracted character count")
    word_count: int = Field(..., description="Total extracted word count")
    chunk_count: Optional[int] = Field(None, description="Total number of chunks generated by LangChain text splitter")
    page_count: Optional[int] = Field(None, description="Total number of pages (for PDF)")
    slide_count: Optional[int] = Field(None, description="Total number of slides (for PPT/PPTX)")
    line_count: Optional[int] = Field(None, description="Total number of lines (for TXT)")
    section_count: Optional[int] = Field(None, description="Heading-delimited sections (for DOCX)")
    ocr: Optional[Dict[str, Any]] = Field(None, description="Scanned-page OCR report (for PDF), when any page was OCR'd")


class DocumentUploadResponse(BaseModel):
    status: str = Field("success", description="Status code or status description ('success' or 'error')")
    message: str = Field(..., description="Human-readable status summary")
    quiz_id: str = Field(..., description="Unique identifier for the generated quiz session")
    filename: str = Field(..., description="Uploaded document filename")
    file_type: str = Field(..., description="Document file type")
    questions: List[QuizQuestion] = Field(..., description="Generated, source-cited questions")
    metadata: DocumentMetadata = Field(..., description="Structured metadata of the processed document")
    difficulty: Optional[str] = Field(None, description="Target difficulty")
    language: str = Field("en", description="en | hi | bi (bilingual) — Hindi text is in each question's translations.hi")
    generation: Optional[Dict[str, Any]] = Field(None, description="Validator / plausibility / dedup / fact-check / translation report")


class GradeRequest(BaseModel):
    # FIX (Bug #10): user_id removed from request body.
    # The authenticated user's iGOT userId is derived from current_user.username
    # (populated via JWT in Depends(get_current_user)).
    # Accepting user_id from the body allowed unauthenticated identity spoofing.
    quiz_id: str = Field(..., description="Unique ID of the quiz session being graded")
    answers: List[Any] = Field(..., description="Per question: option index (mcq, true_false), list of indices "
                                                 "(multi_select), text (fill_blank) or number/text (numeric)")


class GradeResponse(BaseModel):
    status: str = Field("success", description="Status code or status description ('success' or 'error')")
    user_id: str = Field(..., description="User ID of the learner (from JWT)")
    quiz_id: str = Field(..., description="Quiz ID evaluated")
    score: float = Field(..., description="Percentage score achieved (0-100)")
    passed: bool = Field(..., description="True if score >= 70%, False otherwise")
    correct_count: int = Field(..., description="Number of correctly answered questions")
    total_questions: int = Field(..., description="Total number of questions in the quiz")
    message: str = Field(..., description="Human-readable result summary message")
    synced_to_igot: Optional[bool] = Field(None, description="Indicates whether the competency update was pushed to iGOT")
    igot_response: Optional[Dict[str, Any]] = Field(None, description="Response from the mock iGOT server if synced")
    db_updated: Optional[bool] = Field(None, description="Indicates whether the internal SQLite database was updated")
    # FIX (Bug #10): new field — True only on first submission
    evidenceWritten: Optional[bool] = Field(None, description="True if a new EvidenceLog row was written (first submission only)")
    karmaAwarded: Optional[int] = Field(None, description="Karma Points earned by this submission (first pass only)")
    karmaNote: Optional[str] = Field(None, description="Why fewer / no karma points were awarded (daily cap, limit)")
    # Quiz ↔ skill-gap connection (services/practice_assessment.py)
    difficulty: Optional[str] = Field(None, description="Target difficulty the quiz was generated at")
    weighted_score: Optional[float] = Field(None, description="Difficulty-weighted % (Hard = 2x Easy)")
    skillImpact: Optional[Dict[str, Any]] = Field(None, description="Linked role competency, practice ability and skill score/level before → after")
    questionReview: Optional[List[Dict[str, Any]]] = Field(None, description="Per-question result, missed first: your answer, correct answer, explanation, personalised feedback, source passage, a course for the missed point, difficulty calibration")
    recommendations: Optional[Dict[str, Any]] = Field(None, description="Next difficulty, focus topics, courses for the linked competency")




class ErrorResponse(BaseModel):
    status: str = Field("error", description="Failure indicator")
    detail: str = Field(..., description="Error message details")


# =============================================================================
# IN-MEMORY QUIZ STORE
# =============================================================================

QUIZ_STORE: Dict[str, Dict[str, Any]] = {
    "quiz_demo": {
        "quiz_id": "quiz_demo",
        "questions": [
            QuizQuestion(
                question="What is the primary international standard for National Accounts?",
                options=["SNA 2008", "GDP 1993", "IMF 2020", "OECD 2015"],
                correct_answer=0,
                explanation="System of National Accounts (SNA 2008) is the international statistical standard."
            ),
            QuizQuestion(
                question="Which organisation compiles CPI-Combined in India?",
                options=["Reserve Bank of India", "NSO / MoSPI", "NITI Aayog", "Ministry of Finance"],
                correct_answer=1,
                explanation="NSO (National Statistical Office) under MoSPI compiles and releases CPI."
            ),
            QuizQuestion(
                question="What is the base year for the current CPI series in India?",
                options=["2004-05", "2011-12", "2012", "2016"],
                correct_answer=2,
                explanation="The current CPI series has base year 2012 = 100."
            ),
            QuizQuestion(
                question="Which sampling technique gives every unit an equal probability of selection?",
                options=["Simple Random Sampling", "Judgment Sampling", "Quota Sampling", "Snowball Sampling"],
                correct_answer=0,
                explanation="Simple Random Sampling (SRS) ensures equal inclusion probability."
            ),
            QuizQuestion(
                question="What formula is predominantly used for consumer price indices in India?",
                options=["Laspeyres formula", "Fisher ideal index", "Törnqvist index", "Divisia index"],
                correct_answer=0,
                explanation="Laspeyres base-weighted formula is standard in CPI compilation."
            )
        ],
        "filename": "sample_mospi_overview.pdf",
        "competency_id": "FRAC-STAT-001",
        "skill_name": "National Accounts & Official Statistics",
        "difficulty": "Medium",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
}


# =============================================================================
# TEXT EXTRACTION HELPERS
# =============================================================================

def _clean_text(text: str) -> str:
    """
    Normalizes whitespace, removes null bytes, and cleans up repeated linebreaks.
    """
    if not text:
        return ""
    # Remove null bytes
    text = text.replace("\x00", "")
    # Normalize carriage returns
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Replace multiple continuous whitespace (except single newlines)
    text = re.sub(r"[ \t]+", " ", text)
    # Condense 3+ newlines to double newline
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _pdf_text_layer(file_bytes: bytes) -> Tuple[Dict[int, str], int]:
    """{page: text} from the PDF's text layer (pdfplumber, else pypdf) and the page count."""
    try:
        import pdfplumber
    except ImportError:
        pdfplumber = None
    try:
        import pypdf
    except ImportError:
        pypdf = None

    # 1. pdfplumber (superior layout & table preservation)
    if pdfplumber is not None:
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages = {idx: (page.extract_text() or "").strip() for idx, page in enumerate(pdf.pages, start=1)}
            if any(pages.values()) or pypdf is None:
                return pages, len(pages)
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}. Falling back to pypdf.")

    # 2. Fallback to pypdf
    if pypdf is not None:
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            pages = {idx: (page.extract_text() or "").strip() for idx, page in enumerate(reader.pages, start=1)}
            return pages, len(pages)
        except Exception as e:
            logger.error(f"pypdf extraction failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Could not parse PDF content: {str(e)}"
            )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="No PDF extraction library available on the server (pdfplumber/pypdf)."
    )


def _extract_pdf(file_bytes: bytes) -> Tuple[str, int, Optional[Dict[str, Any]]]:
    """
    Text layer first; pages with (almost) no text layer — scanned pages — are
    rendered and OCR'd (services/doc_quiz/extract.py). Returns
    (text with "--- Page N ---" markers, page_count, OCR report or None).
    """
    from services.doc_quiz import extract as dx

    pages, page_count = _pdf_text_layer(file_bytes)
    ocr_report: Optional[Dict[str, Any]] = None
    scanned = [p for p, t in pages.items() if dx.needs_ocr(t)]
    if scanned:
        try:
            ocr_text, ocr_report = dx.ocr_pdf_pages(file_bytes, scanned)
            for p, t in ocr_text.items():
                if len(t) > len(pages.get(p, "")):
                    pages[p] = t
            logger.info("[rag] OCR'd %d scanned page(s): %s", len(scanned), ocr_report)
        except dx.OcrUnavailable as exc:
            ocr_report = {"status": "unavailable", "detail": str(exc), "scanned_pages": len(scanned)}
        except Exception as exc:
            logger.exception("[rag] OCR failed: %s", exc)
            ocr_report = {"status": "failed", "detail": str(exc), "scanned_pages": len(scanned)}
    combined = "\n\n".join(f"--- Page {p} ---\n{t}" for p, t in sorted(pages.items()) if t.strip())
    return _clean_text(combined), page_count, ocr_report


def _extract_pptx(file_bytes: bytes) -> Tuple[str, int]:
    """
    Extracts text from PPTX files using python-pptx with XML fallback.
    Returns a tuple of (extracted_text, slide_count).
    """
    try:
        from pptx import Presentation
    except ImportError:
        Presentation = None

    slide_texts = []
    slide_count = 0

    # 1. Primary extraction via python-pptx
    if Presentation is not None:
        try:
            prs = Presentation(io.BytesIO(file_bytes))
            slide_count = len(prs.slides)

            for idx, slide in enumerate(prs.slides, start=1):
                parts = []
                # Extract slide shape texts (titles, textboxes, tables)
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            text = "".join(run.text for run in paragraph.runs).strip()
                            if text:
                                parts.append(text)
                    elif shape.has_table:
                        for row in shape.table.rows:
                            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                            if row_text:
                                parts.append(row_text)

                # Extract speaker notes if available
                if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
                    notes = slide.notes_slide.notes_text_frame.text.strip()
                    if notes:
                        parts.append(f"[Notes: {notes}]")

                if parts:
                    slide_texts.append(f"--- Slide {idx} ---\n" + "\n".join(parts))

            combined_text = "\n\n".join(slide_texts)
            if combined_text.strip():
                return _clean_text(combined_text), slide_count
        except Exception as e:
            logger.warning(f"python-pptx failed: {e}. Attempting direct XML parsing.")
            slide_texts.clear()

    # 2. Fallback: Parse slide XML files from PPTX (ZIP container) directly
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            slide_files = [f for f in z.namelist() if f.startswith("ppt/slides/slide") and f.endswith(".xml")]
            slide_count = len(slide_files)
            # Sort numerically by slide number
            slide_files.sort(key=lambda name: int(re.search(r"\d+", name).group()) if re.search(r"\d+", name) else 0)

            for idx, slide_file in enumerate(slide_files, start=1):
                xml_content = z.read(slide_file)
                tree = ET.fromstring(xml_content)
                # PPTX text elements are in the 'a:t' tags
                texts = [elem.text for elem in tree.iter() if elem.tag.endswith("}t") and elem.text]
                if texts:
                    slide_texts.append(f"--- Slide {idx} ---\n" + "\n".join(texts))

            combined_text = "\n\n".join(slide_texts)
            return _clean_text(combined_text), slide_count
    except Exception as e:
        logger.error(f"PPTX extraction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not parse PowerPoint presentation: {str(e)}"
        )


def _extract_txt(file_bytes: bytes) -> Tuple[str, int]:
    """
    Extracts text from plain text bytes trying multiple character encodings.
    Returns a tuple of (extracted_text, line_count).
    """
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]
    decoded_text = None

    for enc in encodings:
        try:
            decoded_text = file_bytes.decode(enc)
            break
        except UnicodeDecodeError:
            continue

    if decoded_text is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unable to decode text file. Ensure it is encoded in UTF-8 or standard ASCII."
        )

    cleaned = _clean_text(decoded_text)
    line_count = len(decoded_text.splitlines())
    return cleaned, line_count


def _chunk_document_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 150) -> List[str]:
    """
    Splits extracted document plain-text into semantically coherent chunks using
    LangChain's RecursiveCharacterTextSplitter for RAG processing and vector indexing.
    """
    if not text or not text.strip():
        return []

    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    return splitter.split_text(text)


def _detect_skill_name(text: str = "", filename: str = "") -> str:
    """
    Infers or extracts the skill/competency topic dynamically from the document's
    filename and text content. Falls back to 'General Statistics' if no match.
    """
    combined = f"{filename} {text[:4000]}".lower()

    if any(k in combined for k in ["machine learning", "supervised learning", "unsupervised learning", "deep learning", "neural network", "classification model"]):
        return "Machine Learning"
    if any(k in combined for k in ["generative ai", "genai", "llm", "large language model", "transformer", "diffusion"]):
        return "Generative AI"
    if any(k in combined for k in ["national account", "gdp", "gross domestic product", "gva", "national income", "macroeconomic indicator"]):
        return "National Accounts"
    if any(k in combined for k in ["data analysis", "data analytics", "exploratory data", "data visualization", "descriptive statistics"]):
        return "Data Analysis"
    if any(k in combined for k in ["index number", "cpi", "wpi", "consumer price index", "wholesale price", "inflation index"]):
        return "Index Numbers"
    if any(k in combined for k in ["sample survey", "sampling design", "nsso", "stratified sampling", "survey methodology", "multistage sampling"]):
        return "Sample Surveys"
    if any(k in combined for k in ["official statistics", "statistical system", "mospi", "cso", "nsso"]):
        return "Official Statistics"
    if any(k in combined for k in ["time series", "forecasting", "arima", "seasonality", "trend analysis"]):
        return "Time Series Analysis"
    if any(k in combined for k in ["python", "pandas", "numpy", "scikit-learn"]):
        return "Python for Data Science"
    if any(k in combined for k in ["sql", "database", "relational database", "query"]):
        return "Database Management"

    return "General Statistics"


def _update_internal_db_competency(
    user_id: str,
    competency_name: str = "General Statistics",
    default_level: int = 3,
    score: float = 0.0,
    quiz_id: str = "",
) -> Tuple[bool, int]:
    """
    Updates the internal auth.db SQLite database via SQLAlchemy models:
    1. Only executed when passed == True.
    2. Uses the correct column name `profileId` (NOT user_id).
    3. Checks if the user exists in the `competency_profiles` table.
    4. If user EXISTS: increases their current_level by 1 (capped at max level 5).
    5. If user DOES NOT EXIST: creates a new record with:
       - profileId = payload.user_id
       - skill_name = dynamically determined skill name
       - current_level = 3 (baseline passing level)
       - target_level = 4
       - updated_at = current timestamp
    6. Explicitly sets these values in INSERT/UPDATE statements so they override database defaults.
    7. Commits changes to the database.
    8. Robust error handling ensures the endpoint never crashes on database errors.
    Returns: (success: bool, final_level: int)
    """
    final_level = default_level
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            # 1. Find or create Competency for the dynamic skill_name
            comp = db.query(Competency).filter(Competency.skillName == competency_name).first()
            if not comp:
                comp = Competency(
                    compId=f"COMP-{uuid.uuid4().hex[:6].upper()}",
                    domain="Statistical",
                    skillName=competency_name,
                )
                db.add(comp)
                db.flush()

            # 2. Check if user exists in competency_profiles table using profileId
            profile = db.query(CompetencyProfile).filter(CompetencyProfile.profileId == user_id).first()

            if profile:
                logger.info(f"User '{user_id}' EXISTS in competency_profiles. Updating skill '{competency_name}'.")
                profile.skill_name = competency_name
                profile.lastEvaluatedDate = datetime.now(timezone.utc)
                
                # Check UserCompetency record for this profile and competency
                user_comp = db.query(UserCompetency).filter(
                    UserCompetency.profileId == profile.profileId,
                    UserCompetency.compId == comp.compId,
                ).first()

                existing_level = getattr(profile, "current_level", None) or 1

                if user_comp:
                    old_level = user_comp.currentLevel or existing_level or 1
                    final_level = min(old_level + 1, 5)  # increment by 1, capped at max level 5
                    user_comp.currentLevel = final_level
                    user_comp.evaluatedAt = datetime.now(timezone.utc)
                    user_comp.verificationSource = f"RAG Assessment Quiz ({quiz_id})"
                    logger.info(f"User '{user_id}' skill '{competency_name}' increased from Level {old_level} to Level {final_level}")
                else:
                    # User exists in profile table, but first assessment for this skill
                    final_level = default_level  # baseline level 3
                    user_comp = UserCompetency(
                        profileId=profile.profileId,
                        compId=comp.compId,
                        currentLevel=final_level,
                        verificationSource=f"RAG Assessment Quiz ({quiz_id})",
                        evaluatedAt=datetime.now(timezone.utc),
                    )
                    db.add(user_comp)
                    logger.info(f"Created new UserCompetency for user '{user_id}' skill '{competency_name}' at Level {final_level}")

                profile.current_level = final_level
                profile.target_level = min(final_level + 1, 5)
            else:
                logger.info(f"User '{user_id}' DOES NOT EXIST in competency_profiles. Creating new record.")
                final_level = default_level  # baseline level 3
                profile = CompetencyProfile(
                    profileId=user_id,
                    skill_name=competency_name,
                    current_level=final_level,
                    target_level=4,
                    lastEvaluatedDate=datetime.now(timezone.utc),
                )
                db.add(profile)
                db.flush()

                user_comp = UserCompetency(
                    profileId=profile.profileId,
                    compId=comp.compId,
                    currentLevel=final_level,
                    verificationSource=f"RAG Assessment Quiz ({quiz_id})",
                    evaluatedAt=datetime.now(timezone.utc),
                )
                db.add(user_comp)
                logger.info(f"Created new CompetencyProfile with profileId='{user_id}', skill_name='{competency_name}', current_level={final_level}")

            # 3. Save assessment audit entry
            if quiz_id:
                assessment = Assessment(
                    assessmentId=quiz_id,
                    passingScore=70.0,
                    sourceDocumentId=f"RAG Assessment ({competency_name})",
                )
                db.merge(assessment)

            # 4. Commit changes to SQLite auth.db
            db.commit()
            logger.info(f"Successfully committed competency update to auth.db: profileId='{user_id}', skill='{competency_name}', level={final_level}")
            return True, final_level
        except Exception as ex:
            db.rollback()
            logger.exception(f"Failed to update internal auth.db for user {user_id}: {ex}")
            return False, final_level
        finally:
            db.close()
    except Exception as e:
        logger.exception(f"Database connection error updating competency for user {user_id}: {e}")
        return False, final_level


# =============================================================================
# QUIZ GENERATION (services/doc_quiz) + DIFFICULTY CALIBRATION
# =============================================================================

DEFAULT_QUESTION_TYPES = "mcq,true_false,multi_select,fill_blank,numeric"


def _with_calibration(questions: List[QuizQuestion]) -> List[QuizQuestion]:
    """Stamp each item with its content key and its response-calibrated difficulty.
    The generator's tag is kept as llm_difficulty; `difficulty` is what grading uses."""
    for q in questions:
        q.item_key = q.item_key or qitems.item_key(q)
        q.llm_difficulty = q.llm_difficulty or pa.normalise_difficulty(q.difficulty)
    cal = calib.calibrate_items([(q.item_key, q.llm_difficulty) for q in questions])
    for q, c in zip(questions, cal):
        q.calibration = c
        q.difficulty = c["difficulty"]
    return questions


async def _generate_questions(text: str, chunks: List[str], difficulty: str, n_questions: int,
                              question_types: str, language: str) -> Tuple[List[QuizQuestion], Dict[str, Any]]:
    """Cited, validated, multi-type questions (services/doc_quiz/generate.py) → QuizQuestion."""
    from services.doc_quiz import generate as gen
    from services.media_quiz.llm import LLMUnavailable, gemini_key

    if not gemini_key():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GEMINI_API_KEY is not configured in the .env file. Please configure a valid Gemini API key.",
        )
    try:
        raw, report = await gen.generate(text, chunks, difficulty=difficulty, n_questions=n_questions,
                                         types=gen.parse_types(question_types), language=language)
    except LLMUnavailable as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                            detail=f"Gemini API error during quiz generation: {exc}")
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"message": "No generated question passed validation (citation, grounding and distractor "
                               "checks). Try another document or fewer question types.", "generation": report},
        )
    questions = [QuizQuestion(**{k: v for k, v in q.items() if k in QuizQuestion.model_fields}) for q in raw]
    return await asyncio.to_thread(_with_calibration, questions), report


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload a document and generate a source-cited objective quiz (MCQ, T/F, multi-select, fill-in, numeric)",
    responses={
        200: {"description": "Document parsed and questions generated, validated and cited."},
        400: {"model": ErrorResponse, "description": "Invalid file format or empty payload."},
        413: {"model": ErrorResponse, "description": "File exceeds maximum size limit."},
        422: {"model": ErrorResponse, "description": "Unprocessable document or no readable text (incl. scanned PDF without OCR)."},
        500: {"model": ErrorResponse, "description": "Internal server processing or configuration error."},
        502: {"model": ErrorResponse, "description": "Gemini API error, or no question survived validation."},
    },
)
async def upload_document_for_rag(
    file: UploadFile = File(..., description="Document file to process (.pdf, .pptx, .docx, .txt)"),
    difficulty: str = Form("Medium", description="Easy | Medium | Hard — question mix and grading weights"),
    num_questions: int = Form(5, description="How many questions (3-20)"),
    question_types: str = Form(DEFAULT_QUESTION_TYPES,
                               description="Comma list of mcq, true_false, multi_select, fill_blank, numeric"),
    language: str = Form("en", description="en | hi (Hindi) | bi (bilingual English + Hindi)"),
) -> DocumentUploadResponse:
    """
    **RAG Document Ingestion & Quiz Generator**

    - Accepts **PDF** (scanned pages are OCR'd), **PPTX**, **DOCX** and **TXT** (max 25 MB).
    - Extracts text with page / slide / section markers, chunks it, and generates
      `num_questions` questions of the requested `question_types` through
      services/doc_quiz: every question cites its source chunk with a verbatim quote,
      and passes the validator (grounding, numbers, distractor plausibility), dedup
      and the reference fact-check. `language` = hi / bi adds Hindi text.
    - Each question's difficulty is calibrated from response data once it has enough.
    - Stores the quiz in-memory under a unique `quiz_id` for grading.
    """
    # 1. Validate presence of filename
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided in upload payload."
        )

    filename = os.path.basename(file.filename)
    _, ext = os.path.splitext(filename.lower())

    # 2. Validate file extension
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported file format '{ext}'. "
                f"Allowed document formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )
        )

    # 3. Read file content safely
    try:
        file_bytes = await file.read()
    except Exception as e:
        logger.error(f"Error reading uploaded stream for {filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file: {str(e)}"
        )
    finally:
        await file.close()

    # 4. Validate file size
    file_size = len(file_bytes)
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty (0 bytes)."
        )

    if file_size > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed limit of {max_mb} MB."
        )

    # 5. Extract text based on file type (OCR and DOCX parsing are CPU work → worker thread)
    page_count: Optional[int] = None
    slide_count: Optional[int] = None
    line_count: Optional[int] = None
    section_count: Optional[int] = None
    ocr_report: Optional[Dict[str, Any]] = None
    extracted_text = ""
    is_zip = file_bytes.startswith(b"PK\x03\x04")

    try:
        if ext == ".pdf":
            extracted_text, page_count, ocr_report = await asyncio.to_thread(_extract_pdf, file_bytes)
        elif ext in {".ppt", ".pptx"}:
            if ext == ".ppt" and not is_zip:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Legacy binary .ppt files must be converted to .pptx format or PDF."
                )
            extracted_text, slide_count = _extract_pptx(file_bytes)
        elif ext in {".doc", ".docx"}:
            if not is_zip:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Legacy binary .doc files must be saved as .docx or PDF."
                )
            from services.doc_quiz.extract import extract_docx
            text, section_count = await asyncio.to_thread(extract_docx, file_bytes)
            extracted_text = _clean_text(text)
        elif ext == ".txt":
            extracted_text, line_count = _extract_txt(file_bytes)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error extracting text from {filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error processing document: {str(e)}"
        )

    # 6. Verify that readable text was obtained
    if not extracted_text or len(extracted_text.strip()) == 0:
        if ocr_report and ocr_report.get("status") == "unavailable":
            detail = ("This PDF looks scanned (no text layer) and OCR is not installed on the server — "
                      "run `pip install -r requirements-media.txt` or upload a PDF with selectable text.")
        elif ocr_report:
            detail = "This PDF looks scanned and OCR could not read any text from it (blurred, handwritten or non-Latin script?)."
        else:
            detail = "No readable text could be extracted from this document."
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

    # 7. Chunk extracted text using LangChain TextSplitter
    chunks = await asyncio.to_thread(_chunk_document_text, extracted_text, 1000, 150)
    chunk_count = len(chunks)

    # 8. Generate cited, validated questions
    difficulty = pa.normalise_difficulty(difficulty)
    language = language if language in ("en", "hi", "bi") else "en"
    questions, generation = await _generate_questions(extracted_text, chunks, difficulty, num_questions,
                                                      question_types, language)

    # 9. Store in-memory for grading
    inferred_skill = _detect_skill_name(text=extracted_text, filename=filename)
    quiz_id = f"QZ-{uuid.uuid4().hex[:8].upper()}"
    QUIZ_STORE[quiz_id] = {
        "quiz_id": quiz_id,
        "questions": questions,
        "filename": filename,
        "extracted_text": extracted_text[:4000],
        "chunks": chunks,
        "chunk_count": chunk_count,
        # No hardcoded FRAC id any more: /grade links the quiz to the learner's
        # own role competency (practice_assessment.link_competency).
        "competency_id": None,
        "skill_name": inferred_skill,
        "difficulty": difficulty,
        "language": language,
        "source_type": "document",
        "generation": generation,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # 10. Response metadata
    metadata = DocumentMetadata(
        filename=filename,
        file_type=ext,
        file_size_bytes=file_size,
        character_count=len(extracted_text),
        word_count=len(extracted_text.split()),
        chunk_count=chunk_count,
        page_count=page_count,
        slide_count=slide_count,
        line_count=line_count,
        section_count=section_count,
        ocr=ocr_report,
    )

    requested = generation.get("requested", num_questions)
    short = f" ({requested} requested; the rest failed validation)" if len(questions) < requested else ""
    ocr_note = (f" {ocr_report['pages_with_text']} scanned page(s) were read with OCR."
                if ocr_report and ocr_report.get("pages_with_text") else "")
    return DocumentUploadResponse(
        status="success",
        message=(f"Generated {len(questions)} {difficulty}-level source-cited questions{short} "
                 f"from {filename} ({chunk_count} chunks).{ocr_note}"),
        quiz_id=quiz_id,
        filename=filename,
        file_type=ext,
        questions=questions,
        metadata=metadata,
        difficulty=difficulty,
        language=language,
        generation=generation,
    )


def _question_difficulties(quiz: Dict[str, Any]) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Per-question difficulty for grading, calibrated from response data
    (services/doc_quiz/calibration.py) — read fresh at grading time, so items gain
    calibration while a quiz is live. The prior is the question's own tag (the
    generator's), else the quiz's target difficulty. Media quizzes go through the
    same calibration. Returns (difficulties, calibration dicts).
    """
    quiz_difficulty = pa.normalise_difficulty(quiz.get("difficulty"))
    questions = quiz.get("questions", [])
    items = []
    for q in questions:
        key = getattr(q, "item_key", None) or qitems.item_key(q)
        prior = getattr(q, "llm_difficulty", None) or getattr(q, "difficulty", None)
        items.append((key, pa.normalise_difficulty(prior, quiz_difficulty)))
    cals = calib.calibrate_items(items)
    for (key, _), c in zip(items, cals):
        c["itemKey"] = key
    return [c["difficulty"] for c in cals], cals


def _build_review(questions: List[QuizQuestion], answers: List[Any], difficulties: List[str],
                  cals: List[Dict[str, Any]], engine: Any, comp_id: Optional[str]) -> List[Dict[str, Any]]:
    """
    Type-aware answer review, missed questions first. Each wrong answer gets
    personalised feedback (why THIS answer is wrong — the generator's per-option
    rationale, or numeric/fill-in diagnostics), the exact source passage and a
    course for the missed point (practice_assessment.courses_for_topics).
    """
    rows = []
    for i, q in enumerate(questions):
        ans = answers[i] if i < len(answers) else None
        correct = qitems.is_correct(q, ans)
        cite = (getattr(q, "citations", None) or [None])[0]
        tr = (getattr(q, "translations", None) or {}).get("hi")
        rows.append({
            "index": i,
            "type": qitems.qtype(q),
            "question": q.question,
            "difficulty": difficulties[i] if i < len(difficulties) else "Medium",
            "calibration": cals[i] if i < len(cals) else None,
            "correct": correct,
            "yourAnswer": qitems.answer_display(q, ans),
            "correctAnswer": qitems.correct_display(q),
            "explanation": q.explanation or "",
            "feedback": "" if correct else qitems.feedback(q, ans),
            "solution": getattr(q, "solution", None),
            "source": cite,
            "review": getattr(q, "review", None),
            "translation": ({"question": tr.get("question"), "explanation": tr.get("explanation")} if tr else None),
            "course": None,
        })
    missed = [r for r in rows if not r["correct"]]
    if missed:
        courses = pa.courses_for_topics(engine, [f"{r['question']} {r['correctAnswer']}" for r in missed], comp_id)
        for r, c in zip(missed, courses):
            r["course"] = c
    return sorted(rows, key=lambda r: (r["correct"], r["index"]))


def _row_snapshot(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not row:
        return {}
    level, target = row.get("currentLevel"), row.get("targetLevel")
    return {
        "level": level,
        "score": round(float(row.get("rawScore") or 0.0), 3),
        "confidence": row.get("confidence"),
        "basis": row.get("basis"),
        "targetLevel": target,
        "gap": (max(0, int(target) - int(level)) if level is not None and target is not None else None),
    }


def _record_attempt(
    user_id: str, quiz_id: str, quiz: Dict[str, Any], answers: List[Any], score: float, weighted: float,
    passed: bool, results: List[Dict[str, Any]], row: Optional[Dict[str, Any]], link: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Sync DB work for /grade (runs in a worker thread).

    First submission of a quiz → one QuizAttempt row and, pass OR fail, one
    PRACTICE_ASSESSMENT EvidenceLog row whose value is the learner's updated
    practice ability θ for the linked competency (practice_assessment.update_ability).
    Re-submissions of the same quiz are scored for UX only — no second row, so
    retaking a quiz whose answers you have now seen cannot farm the skill level.
    """
    out: Dict[str, Any] = {"firstAttempt": False, "evidenceWritten": False}
    db = SessionLocal()
    try:
        if db.query(QuizAttempt).filter(QuizAttempt.userId == user_id, QuizAttempt.quizId == quiz_id).first():
            return out
        out["firstAttempt"] = True

        # Evidence is keyed by the catalogue id when the role competency is
        # crosswalked (the assembler reads both ids), else the role id; with no
        # linked role competency, by the quiz's own FRAC tag or its skill name.
        comp_id = (row.get("catalogueId") or row.get("competencyId")) if row else quiz.get("competency_id")
        comp_name = (row.get("name") if row else None) or quiz.get("skill_name") or "General Statistics"
        comp_obj = db.query(Competency).filter(Competency.compId == comp_id).first() if comp_id else None
        if not comp_obj and not comp_id:
            comp_obj = db.query(Competency).filter(Competency.skillName == comp_name).first()
        if not comp_obj:
            comp_obj = Competency(compId=comp_id or f"COMP-{uuid.uuid4().hex[:6].upper()}",
                                  domain="Statistical", skillName=comp_name)
            db.add(comp_obj)
            db.flush()

        ids = {i for i in ((row or {}).get("competencyId"), (row or {}).get("catalogueId"), comp_obj.compId) if i}
        prior_rows = [
            {"evidence_type": e.evidenceType, "granted_value": e.grantedValue, "issue_date": e.issueDate}
            for e in db.query(EvidenceLog).filter(
                EvidenceLog.userId == user_id,
                EvidenceLog.evidenceType == "PRACTICE_ASSESSMENT",
                EvidenceLog.compId.in_(ids),
            ).all()
        ]
        prior, _ = pa.latest_practice_value(prior_rows)
        theta0, start_basis = pa.starting_ability(prior, row)
        theta1, trace = pa.update_ability(theta0, results)

        attempt = QuizAttempt(userId=user_id, quizId=quiz_id, compId=comp_obj.compId, answers=answers,
                              score=score, passed=passed, evidenceWritten=False)
        db.add(attempt)
        db.flush()
        db.add(EvidenceLog(
            userId=user_id, compId=comp_obj.compId, evidenceType="PRACTICE_ASSESSMENT",
            grantedValue=theta1, issueDate=datetime.now(timezone.utc),
            metadata_payload={
                "source": "assessment_studio_quiz",
                "quiz_id": quiz_id,
                "title": quiz.get("filename"),
                "quiz_source": quiz.get("source_type", "document"),
                "competencyName": comp_name,
                "difficulty": pa.normalise_difficulty(quiz.get("difficulty")),
                "score": score,
                "weighted_score": weighted,
                "passed": passed,
                "pass_threshold": pa.PASS_THRESHOLD,
                "ability_before": round(theta0, 3),
                "ability_after": theta1,
                "start_basis": start_basis,
                "per_question": trace,
                "question_types": [qitems.qtype(q) for q in quiz.get("questions", [])],
                "link": link,
            },
        ))
        attempt.evidenceWritten = True
        db.commit()
        out.update({
            "evidenceWritten": True, "compId": comp_obj.compId, "competencyName": comp_name,
            "abilityBefore": round(theta0, 3), "abilityAfter": theta1,
            "abilityDelta": round(theta1 - theta0, 3), "startBasis": start_basis, "perQuestion": trace,
        })
        logger.info("[grade_quiz] practice evidence: user=%s comp=%s θ %.2f → %.2f (score %.0f%%)",
                    user_id, comp_obj.compId, theta0, theta1, score)
        return out
    except Exception as exc:
        db.rollback()
        logger.exception("[grade_quiz] DB error during QuizAttempt/EvidenceLog write: %s", exc)
        out["error"] = str(exc)
        return out
    finally:
        db.close()


async def _competency_rows(user_id: str) -> Optional[List[Dict[str, Any]]]:
    """The learner's resolved role competencies (same rows the skill-gap view shows), or None."""
    if app_state.competency_state is None:
        return None
    try:
        state = await app_state.competency_state(user_id, annotate=False)
        return list(state.get("competencies") or [])
    except Exception as exc:
        logger.warning("[grade_quiz] competency state unavailable for %s: %s", user_id, exc)
        return None


@router.post(
    "/grade",
    response_model=GradeResponse,
    status_code=status.HTTP_200_OK,
    summary="Grade a quiz, update the learner's practice ability on the linked competency, and recommend next steps",
    responses={
        200: {"description": "Quiz evaluated successfully."},
        400: {"model": ErrorResponse, "description": "Invalid submission or answers format."},
        401: {"model": ErrorResponse, "description": "Authentication required."},
        404: {"model": ErrorResponse, "description": "Quiz session not found."},
        500: {"model": ErrorResponse, "description": "Internal grading error."},
    },
)
async def grade_quiz(
    payload: GradeRequest,
    current_user: UserAuth = Depends(get_current_user),   # FIX (Bug #10): auth required
) -> GradeResponse:
    """
    **Grade Quiz → Skill Gap**

    - user_id comes from the JWT (current_user.username), never the body (Bug #10).
    - The quiz is linked to one of the learner's ROLE competencies (FRAC tag →
      e5 similarity → keyword overlap; practice_assessment.link_competency).
    - Every question moves the learner's practice ability θ by a
      difficulty-aware step: missing an Easy question costs more than missing a
      Hard one; solving a Hard one gains more than solving an Easy one.
    - First submission (pass or fail) writes one PRACTICE_ASSESSMENT EvidenceLog
      row = θ after; the baseline assembler reads the latest one into the
      documented channel, so the skill score moves up or down a bounded amount.
      Re-submissions are re-scored for UX only (QuizAttempt UNIQUE(userId, quizId)).
    - Pass (≥ 70 %) still awards karma, updates the legacy CompetencyProfile
      table and syncs to iGOT.
    - The response carries the before → after skill impact, a question review
      and recommendations (next difficulty, focus topics, courses).
    """
    igot_user_id = current_user.username   # e.g. "usr_720465595"

    quiz = QUIZ_STORE.get(payload.quiz_id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz session '{payload.quiz_id}' not found. Please upload a document to generate a quiz.",
        )
    questions: List[QuizQuestion] = quiz.get("questions", [])
    total_questions = len(questions)
    if total_questions == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="The specified quiz contains no questions to grade.")
    if not payload.answers:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No answers provided in submission payload.")

    # 1. Score — plain % (pass rule) and difficulty-weighted %
    quiz_difficulty = pa.normalise_difficulty(quiz.get("difficulty"))
    # Difficulty per item: calibrated from response data once an item has enough
    # first-attempt responses, else the generator's tag (services/doc_quiz/calibration.py).
    difficulties, calibrations = await asyncio.to_thread(_question_difficulties, quiz)
    results = [
        {"difficulty": difficulties[i],
         "correct": i < len(payload.answers) and qitems.is_correct(q, payload.answers[i])}
        for i, q in enumerate(questions)
    ]
    correct_count = sum(r["correct"] for r in results)
    score_percentage = round((correct_count / total_questions) * 100.0, 2)
    weighted = pa.weighted_score(results)
    passed = score_percentage >= pa.PASS_THRESHOLD

    # 2. Link the quiz to the learner's role competency (the skill-gap rows)
    rows_before = await _competency_rows(igot_user_id)
    engine = app_state.engine
    descriptions = {cid: m.get("description", "") for cid, m in (getattr(engine, "_frac_map", None) or {}).items()}
    row_before, link_method, link_score = await asyncio.to_thread(
        pa.link_competency, rows_before or [], quiz, descriptions)
    link = {"method": link_method, "score": link_score,
            "competencyId": row_before.get("competencyId") if row_before else None}

    # 3. Persist attempt + practice evidence (first submission only)
    rec = await asyncio.to_thread(
        _record_attempt, igot_user_id, payload.quiz_id, quiz, payload.answers, score_percentage,
        weighted, passed, results, row_before, link)
    evidence_written = rec["evidenceWritten"]

    # 3b. Item response data for difficulty calibration — first submissions only
    # (a retake after seeing the answers would bias the p-value).
    if evidence_written:
        responses = [{"key": c.get("itemKey"), "correct": r["correct"], "llm_difficulty": c.get("llmDifficulty"),
                      "type": qitems.qtype(q), "question": q.question}
                     for q, r, c in zip(questions, results, calibrations)]
        try:
            await asyncio.to_thread(calib.record_responses, responses, rec.get("abilityBefore", pa.DEFAULT_PRIOR))
        except Exception as exc:
            logger.warning("[grade_quiz] item statistics not recorded: %s", exc)

    # 4. Re-resolve the skill gap so the learner sees the effect immediately
    row_after = None
    if evidence_written:
        app_state.invalidate_user(igot_user_id)
        if row_before:
            rows_after = await _competency_rows(igot_user_id)
            row_after = next((r for r in rows_after or [] if r.get("competencyId") == row_before["competencyId"]), None)

    before, after = _row_snapshot(row_before), _row_snapshot(row_after or row_before)
    skill_impact: Dict[str, Any] = {
        "recorded": evidence_written,
        "linkedToSkillGap": row_before is not None,
        "competencyId": row_before.get("competencyId") if row_before else rec.get("compId"),
        "competencyName": row_before.get("name") if row_before else (rec.get("competencyName") or quiz.get("skill_name")),
        "linkMethod": link_method,
        "linkScore": link_score,
        "before": before,
        "after": after,
    }
    if evidence_written:
        skill_impact.update({k: rec[k] for k in ("abilityBefore", "abilityAfter", "abilityDelta",
                                                   "startBasis", "perQuestion")})
        if before and after:
            skill_impact["scoreDelta"] = round(after["score"] - before["score"], 3)
            if before.get("level") is not None and after.get("level") is not None:
                skill_impact["levelDelta"] = after["level"] - before["level"]
    elif not rec["firstAttempt"]:
        skill_impact["note"] = ("You already submitted this quiz — practice evidence is recorded once per quiz. "
                                "Generate a new quiz to move your skill level again.")
    elif rec.get("error"):
        skill_impact["note"] = "Could not record practice evidence (database unavailable)."

    # 5. Karma (first pass only)
    karma_result = None
    if passed and rec["firstAttempt"] and evidence_written:
        from models.models import KarmaEventType
        from services.karma_engine import karma_engine
        karma_result = await asyncio.to_thread(
            karma_engine.award_safe, igot_user_id, KarmaEventType.ASSESSMENT_PASSED,
            {"referenceId": payload.quiz_id, "note": skill_impact["competencyName"] or quiz.get("filename") or "Quiz passed"})

    # 6. Review + recommendations
    catalogue_id = (row_before or {}).get("catalogueId") or (row_before or {}).get("competencyId") or quiz.get("competency_id")
    review = await asyncio.to_thread(_build_review, questions, payload.answers, difficulties, calibrations,
                                     engine, catalogue_id)
    next_diff, next_reason = pa.next_difficulty(quiz_difficulty, weighted)
    focus = [r["question"] for r in review if not r["correct"]][:5]
    courses = pa.suggest_courses(engine, catalogue_id, after.get("level"), after.get("targetLevel"))
    name = skill_impact["competencyName"] or "this topic"
    if after.get("gap"):
        summary = (f"{name}: you are at Level {after['level']} of the Level {after['targetLevel']} your role needs "
                   f"(gap {after['gap']}).")
    elif after.get("level") is not None and after.get("targetLevel") is not None:
        summary = f"{name}: you meet your role's Level {after['targetLevel']} — keep the skill fresh with harder quizzes."
    else:
        summary = f"{name}: not one of your role competencies, so this quiz does not change your skill gap."
    if focus:
        summary += f" Revise the {len(focus)} question{'s' if len(focus) != 1 else ''} you missed first."
    recommendations = {"nextDifficulty": next_diff, "nextDifficultyReason": next_reason,
                       "focusTopics": focus, "courses": courses, "summary": summary}

    # 7. Pass → legacy CompetencyProfile table + iGOT sync
    synced_to_igot: Optional[bool] = None
    igot_response_data: Optional[Dict[str, Any]] = None
    db_updated: Optional[bool] = None
    if passed:
        skill_name = skill_impact["competencyName"] or quiz.get("skill_name") or "General Statistics"
        db_updated, legacy_level = _update_internal_db_competency(
            user_id=igot_user_id, competency_name=skill_name, default_level=3,
            score=score_percentage, quiz_id=payload.quiz_id,
        )
        igot_url = os.getenv("IGOT_COMPETENCIES_UPDATE_URL", "http://localhost:8001/competencies/update")
        igot_token = os.getenv("IGOT_MOCK_TOKEN", "mock-api-key-2026")
        update_payload = {
            "user_id": igot_user_id,
            "competency": skill_name,
            "competency_id": skill_impact["competencyId"],
            "new_level": after.get("level") if after.get("level") is not None else legacy_level,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(igot_url, json=update_payload,
                                         headers={"x-authenticated-user-token": igot_token})
            synced_to_igot = resp.status_code in (200, 201)
            try:
                igot_response_data = resp.json()
            except Exception:
                igot_response_data = {"status_code": resp.status_code, "raw": resp.text}
        except httpx.RequestError as exc:
            synced_to_igot = False
            igot_response_data = {"warning": f"iGOT server unreachable at {igot_url}: {str(exc)}"}

    # 8. Message
    msg = (f"{'Passed' if passed else 'Not passed'} — {score_percentage:g}% ({correct_count}/{total_questions} correct), "
           f"{weighted:g}% difficulty-weighted.")
    if evidence_written and "abilityDelta" in skill_impact:
        d = skill_impact["abilityDelta"]
        msg += (f" {name} practice ability {skill_impact['abilityBefore']:.2f} → {skill_impact['abilityAfter']:.2f}"
                f" ({'+' if d >= 0 else ''}{d:.2f}).")
    elif skill_impact.get("note"):
        msg += " " + skill_impact["note"]
    if karma_result and karma_result.points_awarded > 0:
        msg += f" +{karma_result.points_awarded} Karma Points earned."
    if not passed:
        msg += f" {pa.PASS_THRESHOLD:g}% is needed to pass."

    return GradeResponse(
        status="success",
        user_id=igot_user_id,
        quiz_id=payload.quiz_id,
        score=score_percentage,
        passed=passed,
        correct_count=correct_count,
        total_questions=total_questions,
        message=msg,
        synced_to_igot=synced_to_igot,
        igot_response=igot_response_data,
        db_updated=db_updated,
        evidenceWritten=evidence_written,
        karmaAwarded=karma_result.points_awarded if karma_result else None,
        karmaNote=karma_result.reason if karma_result else None,
        difficulty=quiz_difficulty,
        weighted_score=weighted,
        skillImpact=skill_impact,
        questionReview=review,
        recommendations=recommendations,
    )


@router.get("/attempts", summary="The signed-in learner's graded quiz attempts, newest first")
async def list_attempts(current_user: UserAuth = Depends(get_current_user)) -> Dict[str, Any]:
    """Assessment Studio history: QuizAttempt rows joined with their practice evidence (skill impact)."""
    user_id = current_user.username

    def _load() -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            attempts = (db.query(QuizAttempt).filter(QuizAttempt.userId == user_id)
                        .order_by(QuizAttempt.gradedAt.desc()).limit(100).all())
            evidence = {}
            for e in db.query(EvidenceLog).filter(EvidenceLog.userId == user_id,
                                                  EvidenceLog.evidenceType == "PRACTICE_ASSESSMENT").all():
                meta = e.metadata_payload or {}
                if meta.get("quiz_id"):
                    evidence[meta["quiz_id"]] = meta
            names = {c.compId: c.skillName for c in db.query(Competency).filter(
                Competency.compId.in_({a.compId for a in attempts if a.compId})).all()} if attempts else {}
            out = []
            for a in attempts:
                meta = evidence.get(a.quizId, {})
                stored = QUIZ_STORE.get(a.quizId) or {}
                out.append({
                    "id": a.attemptId,
                    "quizId": a.quizId,
                    "title": meta.get("title") or stored.get("filename") or a.quizId,
                    "date": a.gradedAt.isoformat() if a.gradedAt else None,
                    "score": a.score,
                    "passed": a.passed,
                    "weightedScore": meta.get("weighted_score"),
                    "difficulty": meta.get("difficulty") or stored.get("difficulty"),
                    "competencyId": a.compId,
                    "competencyName": meta.get("competencyName") or names.get(a.compId),
                    "abilityBefore": meta.get("ability_before"),
                    "abilityAfter": meta.get("ability_after"),
                })
            return out
        finally:
            db.close()

    try:
        return {"status": "success", "attempts": await asyncio.to_thread(_load)}
    except Exception as exc:
        logger.exception("[attempts] %s", exc)
        return {"status": "error", "attempts": []}
