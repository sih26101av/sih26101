"""
JSON-mode chat providers for quiz generation and cross-checking.

Groq serves several model families (GPT-OSS, Qwen, …) behind one
OpenAI-compatible endpoint; GROQ_API_KEYS may hold several comma-separated keys
that rotate when one is rate-limited. Gemini is an optional extra family.
Every provider carries a `family` so the pipeline can have one family write
the questions and a *different* family answer them blind.

Rate limits are handled with per-key cooldowns taken from `retry-after`.
Invalid keys are disabled for the process lifetime.

Env:
    GROQ_API_KEYS   comma-separated (GROQ_API_KEY also accepted)
    GROQ_MODELS     comma-separated, in preference order
                    (default: openai/gpt-oss-120b,qwen/qwen3.8-27b,openai/gpt-oss-20b)
    GEMINI_API_KEY, GEMINI_MODEL (default gemini-2.5-flash)
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_GROQ_MODELS = "openai/gpt-oss-120b,qwen/qwen3.8-27b,openai/gpt-oss-20b"
_PLACEHOLDER_KEYS = {"", "your-gemini-api-key-here", "your-actual-api-key-here", "YOUR_GEMINI_API_KEY"}
REQUEST_TIMEOUT = 45.0
DEFAULT_COOLDOWN = 30.0


class ProviderError(Exception):
    """A provider could not produce a usable JSON answer."""


def parse_json_object(raw: str) -> dict:
    """Parse model output into a dict, tolerating code fences and leading chatter."""
    text = (raw or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text).strip()
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
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
    for fam in ("gpt-oss", "qwen", "llama", "gemini", "gemma", "mistral", "deepseek", "kimi"):
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


class ChatProvider:
    name: str
    family: str
    model: str
    calls: int = 0

    def available(self) -> bool:  # pragma: no cover - interface
        raise NotImplementedError

    async def complete_json(self, system: str, user: str, *, max_tokens: int, temperature: float = 0.3,
                            purpose: str = "generate") -> dict:  # pragma: no cover - interface
        raise NotImplementedError


# Groq keys are shared across model instances, but rate limits are per (key, model),
# so each model keeps its own cooldown table keyed by the key string.
@dataclass
class GroqProvider(ChatProvider):
    model: str
    api_keys: list[str]
    _keys: list[_Key] = field(default_factory=list)
    _cursor: int = 0

    def __post_init__(self) -> None:
        self._keys = [_Key(k) for k in self.api_keys]
        self.name = f"groq:{self.model}"
        self.family = _family(self.model)
        self.calls = 0

    def available(self) -> bool:
        return any(k.usable() for k in self._keys)

    def _extra(self, purpose: str) -> dict:
        m = self.model.lower()
        if "gpt-oss" in m:
            return {"reasoning_effort": "medium"}
        if "qwen3" in m:
            return {"reasoning_format": "hidden"}
        return {}

    async def complete_json(self, system: str, user: str, *, max_tokens: int, temperature: float = 0.3,
                            purpose: str = "generate") -> dict:
        body = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "response_format": {"type": "json_object"},
            "temperature": temperature,
            "max_completion_tokens": max_tokens,
            **self._extra(purpose),
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
                last_error = f"network: {exc}"
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
            else:
                key.cooling_until = time.monotonic() + 10
                last_error = f"HTTP {resp.status_code}: {resp.text[:160]}"
            logger.warning("[quiz] %s: %s", self.name, last_error)
        raise ProviderError(f"{self.name}: {last_error}")


@dataclass
class GeminiProvider(ChatProvider):
    model: str
    api_key: str
    _key: _Key | None = None

    def __post_init__(self) -> None:
        self._key = _Key(self.api_key)
        self.name = f"gemini:{self.model}"
        self.family = "gemini"
        self.calls = 0

    def available(self) -> bool:
        return self._key.usable()

    async def complete_json(self, system: str, user: str, *, max_tokens: int, temperature: float = 0.3,
                            purpose: str = "generate") -> dict:
        body = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                resp = await client.post(GEMINI_URL.format(model=self.model), params={"key": self._key.value}, json=body)
        except httpx.HTTPError as exc:
            self._key.cooling_until = time.monotonic() + 10
            raise ProviderError(f"{self.name}: network: {exc}") from exc
        self.calls += 1
        if resp.status_code == 200:
            try:
                parts = resp.json()["candidates"][0]["content"]["parts"]
            except (KeyError, IndexError) as exc:
                raise ProviderError(f"{self.name}: empty candidate") from exc
            return parse_json_object("".join(p.get("text", "") for p in parts))
        if resp.status_code in (401, 403) or "API_KEY_INVALID" in resp.text or resp.status_code == 404:
            self._key.dead = True
        elif resp.status_code == 429:
            self._key.cooling_until = time.monotonic() + _retry_after(resp)
        else:
            self._key.cooling_until = time.monotonic() + 10
        raise ProviderError(f"{self.name}: HTTP {resp.status_code}: {resp.text[:160]}")


_registry: list[ChatProvider] | None = None


def configured_providers() -> list[ChatProvider]:
    """Providers built from env, in preference order. Cached so cooldowns persist across requests."""
    global _registry
    if _registry is None:
        keys = os.getenv("GROQ_API_KEYS") or os.getenv("GROQ_API_KEY") or ""
        groq_keys = [k.strip() for k in keys.split(",") if k.strip()]
        providers: list[ChatProvider] = []
        if groq_keys:
            models = [m.strip() for m in os.getenv("GROQ_MODELS", DEFAULT_GROQ_MODELS).split(",") if m.strip()]
            providers += [GroqProvider(model=m, api_keys=groq_keys) for m in models]
        gemini_key = (os.getenv("GEMINI_API_KEY") or "").strip()
        if gemini_key not in _PLACEHOLDER_KEYS:
            providers.append(GeminiProvider(model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip(), api_key=gemini_key))
        _registry = providers
        logger.info("[quiz] providers: %s", [p.name for p in providers] or "none (offline only)")
    return _registry


def reset_providers() -> None:
    """Forget cached providers (tests, or after editing .env)."""
    global _registry
    _registry = None
