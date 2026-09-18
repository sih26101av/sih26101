"""
Evaluate the Assessment Studio quiz pipeline on fixture documents.

    python scripts/eval_quiz.py                       # all fixtures, Medium, configured providers
    python scripts/eval_quiz.py --difficulty all      # Easy, Medium and Hard
    python scripts/eval_quiz.py --offline             # key-free extractive engine only
    python scripts/eval_quiz.py --doc path/to/file.pdf --json out.json

Fixtures: tests/data/quiz_docs/*.txt (PDF/PPTX paths go through the router's extractors).
Reports per quiz: generator/checker, gate + cross-check rejections, bloom mix,
answer-position spread, API calls and latency; prints each question for human review.
"""

from __future__ import annotations

import argparse
import asyncio
import glob
import io
import json
import logging
import os
import sys
import time
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
DOC_DIR = os.path.join(ROOT, "tests", "data", "quiz_docs")


def load_document(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    data = open(path, "rb").read()
    if ext == ".txt":
        return data.decode("utf-8")
    from routers.rag import _extract_pdf, _extract_pptx  # heavy import, only when needed

    return (_extract_pdf if ext == ".pdf" else _extract_pptx)(data)[0]


async def run(paths: list[str], difficulties: list[str], offline: bool, n: int) -> list[dict]:
    from dotenv import load_dotenv
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    from ai.quiz import QuizBuildError, build_quiz
    from ai.quiz.providers import configured_providers

    load_dotenv(os.path.join(ROOT, ".env"))
    providers = [] if offline else configured_providers()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150,
                                              separators=["\n\n", "\n", ". ", " ", ""])
    out = []
    for path in paths:
        text = load_document(path)
        chunks = splitter.split_text(text)
        for diff in difficulties:
            started = time.monotonic()
            name = os.path.basename(path)
            try:
                res = await build_quiz(text, chunks, n=n, difficulty=diff, providers=providers, use_cache=False)
            except QuizBuildError as exc:
                print(f"\n=== {name} [{diff}] → rejected: {exc}")
                out.append({"doc": name, "difficulty": diff, "error": str(exc)})
                continue
            meta = res.meta
            blooms = Counter(q.bloom_level for q in res.questions)
            positions = Counter(q.correct_answer for q in res.questions)
            print(f"\n=== {name} [{diff}]  {time.monotonic() - started:.1f}s  gen={meta['generator']}  "
                  f"check={meta['checker']}  verification={meta['verification']}  calls={meta['api_calls']}")
            print(f"    bloom={dict(blooms)}  answer_positions={dict(sorted(positions.items()))}  "
                  f"llm={meta['llm_questions']} offline={meta['offline_questions']}  rejected={meta['rejected']}")
            if meta.get("provider_errors"):
                print(f"    provider_errors={meta['provider_errors']}")
            for i, q in enumerate(res.questions, 1):
                print(f"  {i}. [{q.bloom_level}] {q.question}")
                for j, opt in enumerate(q.options):
                    print(f"       {'*' if j == q.correct_answer else ' '} {'ABCD'[j]}) {opt}")
                print(f"       evidence ({q.source_id}{', ' + q.location if q.location else ''}): {q.evidence[:160]}")
            out.append({"doc": name, "difficulty": diff, "meta": meta,
                        "questions": [q.__dict__ for q in res.questions]})
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc", action="append", help="document path (repeatable); default: all fixtures")
    parser.add_argument("--difficulty", default="Medium", help="Easy | Medium | Hard | all")
    parser.add_argument("--offline", action="store_true", help="skip LLM providers")
    parser.add_argument("-n", type=int, default=5)
    parser.add_argument("--json", help="write full results to this path")
    args = parser.parse_args()

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
    logging.basicConfig(level=logging.WARNING)
    paths = args.doc or sorted(glob.glob(os.path.join(DOC_DIR, "*.txt")))
    diffs = ["Easy", "Medium", "Hard"] if args.difficulty.lower() == "all" else [args.difficulty.capitalize()]
    results = asyncio.run(run(paths, diffs, args.offline, args.n))

    ok = [r for r in results if "meta" in r]
    total_rej = Counter()
    for r in ok:
        total_rej.update(r["meta"]["rejected"])
    print(f"\nSUMMARY: {len(ok)}/{len(results)} quizzes built; "
          f"LLM questions {sum(r['meta']['llm_questions'] for r in ok)}, "
          f"offline {sum(r['meta']['offline_questions'] for r in ok)}; rejections {dict(total_rej)}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2, ensure_ascii=False, default=str)


if __name__ == "__main__":
    main()
