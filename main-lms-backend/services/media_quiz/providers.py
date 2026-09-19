"""
FILE: services/media_quiz/providers.py
─────────────────────────────────────────────────────────────────────────────
Groq JSON-mode chat providers with multi-key rotation and model failover
(ported from the ai/quiz/providers.py of the grounded-quiz branch).

Groq serves several model families (GPT-OSS, Qwen, …) behind one
OpenAI-compatible endpoint. GROQ_API_KEYS may hold several comma-separated keys
that rotate: a key that hits a rate limit (429/413) cools down for the server's
`retry-after`, an invalid key (401/403) is disabled for the process lifetime,
and when every key is cooling for one model the next model in GROQ_MODELS is
tried. llm.gemini_json uses these first for text prompts, then Gemini.

Env:
    GROQ_API_KEYS   comma-separated (GROQ_API_KEY also accepted)
    GROQ_MODELS     comma-separated, in preference order
                    (default: openai/gpt-oss-120b,qwen/qwen3.8-27b,openai/gpt-oss-20b)
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from typing import List, Optional

import httpx
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_GROQ_MODELS = "openai/gpt-oss-120b,qwen/qwen3.8-27b,openai/gpt-oss-20b"
_PLACEHOLDER_KEYS = {"", "your-groq-api-key-here", "gsk_your-key-here"}
REQUEST_TIMEOUT = 60.0
DEFAULT_COOLDOWN = 30.0
DEFAULT_MAX_TOKENS = 8192


class ProviderError(Exception):
    """A provider could not produce a usable JSON answer."""


def parse_json_object(raw: str) -> dict:
    """Parse model output into a dict, tolerating code fences, <think> blocks and leading chatter."""
    text = (raw or "").strip()
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text).strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise ProviderError(f"no JSON object in model output: {text[:120]!r}")
        try:
            parsed = json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ProviderError(f"malformed JSON from model: {exc}") from exc
    if isinstance(parsed, list):
        parsed = {"questions": parsed}
    if not isinstance(parsed, dict):
        raise ProviderError("model output is not a JSON object")
    return parsed


def _family(model: str) -> str:
    m = model.lower()
    for fam in ("gpt-oss", "qwen", "llama", "gemma", "mistral", "deepseek", "kimi"):
        if fam in m:
            return fam
    return m.split("/")[0]


def _retry_after(resp: httpx.Response) -> float:
    try:
        return max(1.0, float(resp.headers.get("retry-after", "")))
    except ValueError:
        return DEFAULT_COOLDOWN


@dataclass
class _Key:
    value: str
    cooling_until: float = 0.0
    dead: bool = False

    def usable(self) -> bool:
        return not self.dead and time.monotonic() >= self.cooling_until


# Keys are shared across models, but Groq rate limits are per (key, model), so
# each model keeps its own cooldown table.
@dataclass
class GroqProvider:
    model: str
    api_keys: List[str]
    _keys: List[_Key] = field(default_factory=list)
    _cursor: int = 0

    def __post_init__(self) -> None:
        self._keys = [_Key(k) for k in self.api_keys]
        self.name = f"groq:{self.model}"
        self.family = _family(self.model)
        self.calls = 0

    def available(self) -> bool:
        return any(k.usable() for k in self._keys)

    def _extra(self) -> dict:
        m = self.model.lower()
        if "gpt-oss" in m:
            return {"reasoning_effort": "medium"}
        if "qwen3" in m:
            return {"reasoning_format": "hidden"}
        return {}

    async def complete_json(self, system: str, user: str, *, max_tokens: int = DEFAULT_MAX_TOKENS,
                            temperature: float = 0.3) -> dict:
        body = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "response_format": {"type": "json_object"},
            "temperature": temperature,
            "max_completion_tokens": max_tokens,
            **self._extra(),
        }
        last_error = "no usable key"
        for _ in range(len(self._keys)):
            key = self._keys[self._cursor % len(self._keys)]
            self._cursor += 1
            if not key.usable():
                continue
            try:
                async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                    resp = await client.post(GROQ_URL, json=body, headers={"Authorization": f"Bearer {key.value}"})
            except httpx.HTTPError as exc:
                last_error = f"network: {exc.__class__.__name__}"
                key.cooling_until = time.monotonic() + 10
                continue
            self.calls += 1
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"].get("content") or ""
                return parse_json_object(content)
            if resp.status_code in (401, 403):
                key.dead = True
                last_error = f"HTTP {resp.status_code} (key disabled)"
            elif resp.status_code in (413, 429):
                key.cooling_until = time.monotonic() + _retry_after(resp)
                last_error = f"HTTP {resp.status_code} rate limited"
            elif resp.status_code == 400 and "json_validate_failed" in resp.text:
                last_error = "model produced invalid JSON"
            elif resp.status_code == 404 or "model_not_found" in resp.text or "decommissioned" in resp.text:
                # The model is gone for every key — stop trying it.
                for k in self._keys:
                    k.dead = True
                last_error = f"HTTP {resp.status_code}: model unavailable"
                logger.warning("[llm] %s: %s", self.name, last_error)
                break
            else:
                key.cooling_until = time.monotonic() + 10
                last_error = f"HTTP {resp.status_code}: {resp.text[:160]}"
            logger.warning("[llm] %s: %s", self.name, last_error)
        raise ProviderError(f"{self.name}: {last_error}")


_registry: Optional[List[GroqProvider]] = None


def groq_keys() -> List[str]:
    load_dotenv()
    raw = os.getenv("GROQ_API_KEYS") or os.getenv("GROQ_API_KEY") or ""
    return [k.strip() for k in raw.split(",") if k.strip() and k.strip() not in _PLACEHOLDER_KEYS]


def configured_providers() -> List[GroqProvider]:
    """Groq providers built from env, in GROQ_MODELS order. Cached so cooldowns persist across requests."""
    global _registry
    if _registry is None:
        keys = groq_keys()
        providers: List[GroqProvider] = []
        if keys:
            models = [m.strip() for m in os.getenv("GROQ_MODELS", DEFAULT_GROQ_MODELS).split(",") if m.strip()]
            providers = [GroqProvider(model=m, api_keys=keys) for m in models]
        _registry = providers
        logger.info("[llm] groq providers: %s (%d key(s))", [p.name for p in providers] or "none", len(keys))
    return _registry


def reset_providers() -> None:
    """Forget cached providers (tests, or after editing .env)."""
    global _registry
    _registry = None
