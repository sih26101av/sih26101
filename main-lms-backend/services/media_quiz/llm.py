"""
FILE: services/media_quiz/llm.py
─────────────────────────────────────────────────────────────────────────────
LLM calls for the media-quiz pipeline, kept separate from routers/rag.py so the
two quiz paths can evolve independently.

  gemini_json(prompt, images=None) — JSON output for every Assessment Studio
                                     LLM call. Text prompts go to Groq first
                                     (GROQ_API_KEYS rotate on 429, GROQ_MODELS
                                     fail over — see providers.py), then Gemini.
                                     Prompts with images (vision) use Gemini only.
  llm_json                         — alias of gemini_json.
  llm_configured()                 — True if Groq or Gemini has a key.
  ollama_vision_json(prompt, image) — offline VLM (e.g. qwen2.5vl:3b) via a
                                     local Ollama server.
Env: GROQ_API_KEYS, GROQ_MODELS, GEMINI_API_KEY, GEMINI_MODEL.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import re
from typing import Any, List, Optional

import httpx
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Single source of truth for the model id (document + media quizzes). Keep
# .env.example's GEMINI_MODEL equal to this. Verified against the key's
# ListModels on 2026-09-19 (gemini-1.5-flash is no longer served).
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"
_FALLBACK_MODELS = [DEFAULT_GEMINI_MODEL, "gemini-3.6-flash", "gemini-3.5-flash", "gemini-flash-latest"]


class LLMUnavailable(RuntimeError):
    pass


def gemini_key() -> str:
    load_dotenv()
    key = os.getenv("GEMINI_API_KEY", "").strip()
    return "" if key in {"", "your-actual-api-key-here", "your-gemini-api-key-here", "YOUR_GEMINI_API_KEY"} else key


def llm_configured() -> bool:
    """True when at least one text LLM (Groq or Gemini) has a key."""
    from services.media_quiz.providers import groq_keys
    return bool(groq_keys() or gemini_key())


_GROQ_SYSTEM = ("You are a careful assistant for a government e-learning platform. Follow the user's "
                "instructions exactly and respond with a single valid JSON object only — no prose, no code fences.")


async def _groq_json(prompt: str, temperature: float) -> Any:
    """Try each configured Groq model in order; each rotates its keys. Raises LLMUnavailable if all fail."""
    from services.media_quiz.providers import ProviderError, configured_providers

    errors: List[str] = []
    for provider in configured_providers():
        if not provider.available():
            errors.append(f"{provider.name}: all keys cooling down")
            continue
        try:
            return await provider.complete_json(_GROQ_SYSTEM, prompt, temperature=temperature)
        except ProviderError as exc:
            errors.append(str(exc))
        except Exception as exc:  # unexpected payload shape etc. — fail over, don't crash the request
            errors.append(f"{provider.name}: {exc.__class__.__name__}: {exc}")
            logger.warning("[llm] %s failed: %s", provider.name, exc)
    raise LLMUnavailable("; ".join(errors) or "no Groq providers configured")


def parse_json(raw: str) -> Any:
    s = (raw or "").strip()
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s)
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        m = re.search(r"(\{.*\}|\[.*\])", s, re.S)
        if m:
            return json.loads(m.group(1))
        raise


async def gemini_json(prompt: str, images: Optional[List[bytes]] = None, temperature: float = 0.3) -> Any:
    groq_error: Optional[LLMUnavailable] = None
    if not images:
        from services.media_quiz.providers import configured_providers
        if configured_providers():
            try:
                return await _groq_json(prompt, temperature)
            except LLMUnavailable as exc:
                groq_error = exc
                logger.warning("[llm] Groq failed, falling back to Gemini: %s", exc)

    key = gemini_key()
    if not key:
        if groq_error:
            raise LLMUnavailable(f"All Groq models/keys failed ({groq_error}) and GEMINI_API_KEY is not configured.")
        raise LLMUnavailable("No LLM configured — set GROQ_API_KEYS or GEMINI_API_KEY in main-lms-backend/.env."
                             if not images else "Vision needs GEMINI_API_KEY in main-lms-backend/.env.")

    import google.generativeai as genai

    genai.configure(api_key=key)
    configured = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip()
    models = ([configured] if configured else []) + [m for m in _FALLBACK_MODELS if m != configured]
    parts: List[Any] = [prompt] + [{"mime_type": "image/jpeg", "data": img} for img in (images or [])]

    last: Optional[Exception] = None
    for name in models:
        try:
            model = genai.GenerativeModel(
                model_name=name,
                generation_config={"response_mime_type": "application/json", "temperature": temperature},
            )
            resp = await asyncio.to_thread(model.generate_content, parts)
            if resp and resp.text:
                return parse_json(resp.text)
        except json.JSONDecodeError as exc:
            last = exc
            logger.warning("[media-llm] %s returned non-JSON: %s", name, exc)
        except Exception as exc:
            last = exc
            logger.warning("[media-llm] %s failed: %s", name, exc)
    prefix = f"Groq failed ({groq_error}); " if groq_error else ""
    raise LLMUnavailable(f"{prefix}All Gemini models failed: {last}")


llm_json = gemini_json


async def ollama_vision_json(prompt: str, image: bytes) -> Any:
    url = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
    model = os.getenv("MEDIA_VLM_MODEL", "qwen2.5vl:3b")
    async with httpx.AsyncClient(timeout=180) as client:
        r = await client.post(f"{url}/api/generate", json={
            "model": model, "prompt": prompt, "images": [base64.b64encode(image).decode()],
            "format": "json", "stream": False, "options": {"temperature": 0.1},
        })
        r.raise_for_status()
        return parse_json(r.json().get("response", ""))
