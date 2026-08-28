"""
FILE: ai/rag_engine.py
─────────────────────────────────────────────────────────────────────────────
RAG Reasoning Engine — Gyan (ज्ञान) AI Core
MoSPI Skill Intelligence Platform | SIH 2026

Connects the vector store retriever to the local Ollama LLM to produce
context-grounded, personalized responses for MoSPI statistical officials.

Architecture:
  1. build_system_prompt()    → injects user profile + skill gap context
  2. generate_chat_response() → runs RAG chain: retrieve → prompt → generate
  3. is_ollama_available()    → lightweight connectivity check (no model load)

Design decisions:
  • Uses ChatOllama from langchain-ollama (async-compatible, streaming-ready).
  • Temperature 0.2 → factual, consistent answers for a professional context.
  • System prompt always injects user's role, top gaps, and top recommendations,
    giving the LLM the same context the template engine used — but it can now
    reason over retrieved document chunks too.
  • Raises RuntimeError on Ollama connection failure so the router can fall back
    to the template engine transparently.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
_OLLAMA_URL   = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
_TEMPERATURE  = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))


# ── Connectivity check ────────────────────────────────────────────────────────

def is_ollama_available() -> bool:
    """
    Fast, synchronous check — just hits the Ollama /api/tags endpoint.
    Returns True if reachable, False otherwise (no exceptions propagate).
    """
    import httpx
    try:
        r = httpx.get(f"{_OLLAMA_URL}/api/tags", timeout=2.0)
        return r.status_code == 200
    except Exception:
        return False


# ── System prompt builder ─────────────────────────────────────────────────────

def build_system_prompt(
    job_role: str,
    department: str,
    skill_gaps: list[dict],
    recommendations: list[dict],
    language_hint: str = "en",
) -> str:
    """
    Builds a rich system prompt that grounds the LLM in the user's live context.
    The personalized profile gives the LLM the same contextual awareness the
    template engine had, but now it can combine it with retrieved document chunks.
    """
    # Summarise top 3 gaps (highest gap score first)
    top_gaps = sorted(
        [g for g in skill_gaps if g.get("gapScore", 0) > 0],
        key=lambda x: -x.get("gapScore", 0),
    )[:3]

    gaps_text = "\n".join(
        f"  • {g['skillName']}: Level {g['currentLevel']} → {g['targetLevel']} needed (gap: {g['gapScore']})"
        for g in top_gaps
    ) or "  • No active skill gaps"

    # Summarise top 3 recommendations
    top_recs = recommendations[:3]
    recs_text = "\n".join(
        f"  {i+1}. {r['title']} ({r['provider']}, {r.get('durationHours', '?')}h) — {r.get('matchReason', '')}"
        for i, r in enumerate(top_recs)
    ) or "  • No recommendations available"

    lang_instruction = (
        "Always respond in Hindi (Devanagari script or Hinglish is acceptable) "
        "when the user writes in Hindi."
        if language_hint == "hi"
        else "Respond in clear, professional English."
    )

    return f"""You are Gyan (ज्ञान), the AI Learning Assistant for the MoSPI Skill Intelligence Platform.
You help Indian government statistical officials navigate their personalised learning journey
on iGOT Karmayogi as part of Mission Karmayogi.

User Profile:
  Role        : {job_role}
  Department  : {department}

Active Skill Gaps (highest priority first):
{gaps_text}

Recommended Courses:
{recs_text}

Guidelines:
- Use the retrieved knowledge-base context (provided below) to answer accurately.
- If the answer is not in the context, draw on your training knowledge about Indian 
  official statistics, MoSPI, iGOT Karmayogi, and the FRAC competency framework.
- Keep responses concise, structured, and actionable — use bullet points where helpful.
- Reference specific courses, competency levels, or FRAC codes when relevant.
- {lang_instruction}
- Never fabricate statistics or policy numbers — say "refer to official MoSPI publications" 
  if uncertain.
- Sign off as "Gyan" with a relevant emoji (🎓 📊 🇮🇳) when appropriate."""


# ── Main RAG response function ────────────────────────────────────────────────

async def generate_chat_response(
    query: str,
    history: list[dict[str, str]],
    job_role: str = "Statistical Official",
    department: str = "MoSPI",
    skill_gaps: list[dict] | None = None,
    recommendations: list[dict] | None = None,
    language_hint: str = "en",
) -> str:
    """
    Runs the full RAG pipeline:
      1. Retrieve top-k relevant document chunks from ChromaDB.
      2. Build a personalized system prompt.
      3. Send to Ollama LLM (via LangChain ChatOllama).
      4. Return the text answer.

    Raises RuntimeError if Ollama is unreachable (caller should catch and fall back).

    This is async-safe — the synchronous LangChain invoke is wrapped with
    asyncio.to_thread() so it doesn't block the FastAPI event loop.
    """
    from langchain_ollama import ChatOllama
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    from ai.vector_store import get_retriever

    skill_gaps     = skill_gaps or []
    recommendations = recommendations or []

    # 1. Retrieve relevant context chunks
    try:
        retriever = get_retriever(k=4)
        context_docs = await asyncio.to_thread(retriever.invoke, query)
        context_text = "\n\n---\n\n".join(
            f"[Source: {d.metadata.get('source', 'knowledge base')}]\n{d.page_content}"
            for d in context_docs
        )
    except Exception as exc:
        logger.warning("Retrieval failed (will answer without context): %s", exc)
        context_text = ""

    # 2. Build system prompt with user context
    system_prompt = build_system_prompt(
        job_role=job_role,
        department=department,
        skill_gaps=skill_gaps,
        recommendations=recommendations,
        language_hint=language_hint,
    )

    if context_text:
        system_prompt += f"\n\nRelevant Knowledge Base Extracts:\n{context_text}"

    # 3. Build message history for the LLM
    messages: list[Any] = [SystemMessage(content=system_prompt)]

    # Add recent conversation history (last 6 turns to stay within context window)
    for turn in history[-6:]:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        else:
            messages.append(AIMessage(content=content))

    # Add the current user query
    messages.append(HumanMessage(content=query))

    # 4. Call Ollama
    try:
        llm = ChatOllama(
            model=_OLLAMA_MODEL,
            base_url=_OLLAMA_URL,
            temperature=_TEMPERATURE,
        )
        response = await asyncio.to_thread(llm.invoke, messages)
        return response.content.strip()
    except Exception as exc:
        raise RuntimeError(
            f"Ollama LLM call failed (model={_OLLAMA_MODEL}): {exc}"
        ) from exc
