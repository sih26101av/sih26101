"""
Grounded MCQ generation for the Assessment Studio (routers/rag.py).

    passages.py  — pick diverse, information-dense passages from the document
    providers.py — Groq (key rotation, several model families) + Gemini over httpx
    prompts.py   — generation / blind cross-check prompts
    verifier.py  — deterministic grounding gate (no API)
    offline.py   — key-free extractive builder, last resort
    pipeline.py  — build_quiz(): generate → gate → cross-check → repair → fill → shuffle
"""

from ai.quiz.pipeline import QuizBuildError, QuizResult, build_quiz  # noqa: F401
