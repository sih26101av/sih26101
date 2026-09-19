"""Groq multi-key rotation / model failover and the Groq → Gemini routing in llm.gemini_json."""
import asyncio

import httpx
import pytest

from services.media_quiz import llm, providers


class _Resp:
    def __init__(self, status, content='{"ok": true}', headers=None, text=""):
        self.status_code = status
        self.headers = headers or {}
        self.text = text
        self._content = content

    def json(self):
        return {"choices": [{"message": {"content": self._content}}]}


@pytest.fixture
def groq_env(monkeypatch):
    monkeypatch.setattr(providers, "load_dotenv", lambda: None)
    monkeypatch.setenv("GROQ_API_KEYS", "k1,k2")
    monkeypatch.setenv("GROQ_MODELS", "openai/gpt-oss-120b,qwen/qwen3.8-27b")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    providers.reset_providers()
    yield
    providers.reset_providers()


def _script(monkeypatch, plan):
    """plan(key, model) -> _Resp; records calls."""
    calls = []

    async def post(self, url, json=None, headers=None, **kw):
        key = headers["Authorization"].split()[-1]
        calls.append((key, json["model"]))
        return plan(key, json["model"])

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    return calls


def test_rate_limited_key_rotates_to_next_key(groq_env, monkeypatch):
    calls = _script(monkeypatch, lambda k, m: _Resp(429, headers={"retry-after": "60"}) if k == "k1" else _Resp(200))
    out = asyncio.run(llm.gemini_json("prompt"))
    assert out == {"ok": True}
    assert calls == [("k1", "openai/gpt-oss-120b"), ("k2", "openai/gpt-oss-120b")]
    p = providers.configured_providers()[0]
    assert not p._keys[0].usable() and p._keys[1].usable()


def test_all_keys_limited_fails_over_to_next_model(groq_env, monkeypatch):
    calls = _script(monkeypatch, lambda k, m: _Resp(429) if "gpt-oss" in m else _Resp(200, '{"m": "qwen"}'))
    assert asyncio.run(llm.gemini_json("prompt")) == {"m": "qwen"}
    assert [m for _, m in calls] == ["openai/gpt-oss-120b"] * 2 + ["qwen/qwen3.8-27b"]


def test_invalid_key_is_disabled(groq_env, monkeypatch):
    _script(monkeypatch, lambda k, m: _Resp(401) if k == "k1" else _Resp(200))
    asyncio.run(llm.gemini_json("prompt"))
    assert providers.configured_providers()[0]._keys[0].dead


def test_groq_exhausted_without_gemini_raises(groq_env, monkeypatch):
    _script(monkeypatch, lambda k, m: _Resp(429))
    monkeypatch.setattr(llm, "gemini_key", lambda: "")
    with pytest.raises(llm.LLMUnavailable, match="Groq"):
        asyncio.run(llm.gemini_json("prompt"))


def test_images_skip_groq(groq_env, monkeypatch):
    calls = _script(monkeypatch, lambda k, m: _Resp(200))
    monkeypatch.setattr(llm, "gemini_key", lambda: "")
    with pytest.raises(llm.LLMUnavailable, match="Vision"):
        asyncio.run(llm.gemini_json("prompt", images=[b"x"]))
    assert calls == []


def test_llm_configured_with_groq_only(groq_env, monkeypatch):
    monkeypatch.setattr(llm, "gemini_key", lambda: "")
    assert llm.llm_configured()


def test_parse_json_object_strips_think_and_fences():
    assert providers.parse_json_object('<think>x</think>```json\n{"a": 1}\n```') == {"a": 1}
    assert providers.parse_json_object('[{"q": 1}]') == {"questions": [{"q": 1}]}
