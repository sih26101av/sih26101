"""
FILE: scripts/eval_media_quiz.py
─────────────────────────────────────────────────────────────────────────────
Runs every file in a test folder through the OLD pipeline (assume a narrated
lecture: transcribe everything → 5 MCQs) and the NEW one (probe → route →
confidence-scored evidence → cited, validated questions), and writes:

  <out>/results.csv   one row per generated question, with an empty
                      `usable (y/n)` column to fill in by hand
  <out>/summary.md    per-video table: route, questions old vs new,
                      validator rejections, flagged-for-review, rejections

Suggested test set (see docs/features/media-quiz-generator.md):
  narrated_slides.mp4, phone_vfr_recording.mp4, silent_excel_demo.mp4,
  music_intro_lecture.mp4, hinglish_lecture.mp4, charts_formulas.mp4,
  blank_music.mp4

Usage (from main-lms-backend/):
  python scripts/eval_media_quiz.py path/to/test_videos --out eval_out [--skip-old]

After marking `usable`, count unusable/hallucinated questions per video for
old vs new — that comparison is the before/after slide.
─────────────────────────────────────────────────────────────────────────────
"""

import argparse
import asyncio
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.media_quiz import media_io  # noqa: E402
from services.media_quiz.pipeline import NotLearnable, run, run_naive  # noqa: E402


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out", default="eval_media_out")
    ap.add_argument("--difficulty", default="Medium")
    ap.add_argument("--skip-old", action="store_true", help="only run the new pipeline")
    args = ap.parse_args()

    exts = media_io.MEDIA_VIDEO_EXTS | media_io.MEDIA_AUDIO_EXTS
    files = sorted(f for f in os.listdir(args.folder) if os.path.splitext(f.lower())[1] in exts)
    if not files:
        sys.exit(f"No media files in {args.folder}")
    os.makedirs(args.out, exist_ok=True)

    rows, summary = [], []
    for name in files:
        path = os.path.join(args.folder, name)
        print(f"\n▶ {name}")
        entry = {"video": name}

        if not args.skip_old:
            t = time.perf_counter()
            try:
                old = await run_naive(path, args.difficulty)
            except Exception as exc:          # the old path fails loudly — record it
                old, entry["old_error"] = [], str(exc)[:120]
            entry["old_questions"] = len(old)
            entry["old_s"] = round(time.perf_counter() - t, 1)
            for q in old:
                rows.append({"video": name, "pipeline": "old", "question": q.get("question", ""),
                             "answer": (q.get("options") or [""] * 4)[q.get("correct_answer", 0) or 0]
                             if isinstance(q.get("correct_answer"), int) else "",
                             "evidence": "", "flag": "", "usable (y/n)": ""})

        t = time.perf_counter()
        try:
            res = await run(path, args.difficulty)
            rep = res.report
            entry.update({
                "route": rep["content_type"],
                "speech": rep["probe"]["speech_ratio"], "text": rep["probe"]["text_density"],
                "activity": rep["probe"]["screen_activity"],
                "evidence_kept": sum(rep["evidence"]["kept"].values()),
                "evidence_dropped": sum(rep["evidence"]["dropped"].values()),
                "new_questions": len(res.questions),
                "validator_rejected": rep["generation"]["rejected_total"],
                "flagged": rep["fact_check"]["flagged"],
                "competency": res.competency_name,
            })
            for q in res.questions:
                rows.append({"video": name, "pipeline": "new", "question": q.question,
                             "answer": q.options[q.correct_answer], "evidence": " ".join(q.evidence),
                             "flag": q.review.get("status", ""), "usable (y/n)": ""})
        except NotLearnable as exc:
            entry.update({"route": exc.report.get("content_type", "reject"), "new_questions": 0,
                          "rejected_msg": str(exc)[:120]})
        entry["new_s"] = round(time.perf_counter() - t, 1)
        print("  ", entry)
        summary.append(entry)

    with open(os.path.join(args.out, "results.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["video", "pipeline", "question", "answer", "evidence", "flag", "usable (y/n)"])
        w.writeheader()
        w.writerows(rows)

    cols = ["video", "route", "speech", "text", "activity", "old_questions", "new_questions",
            "validator_rejected", "flagged", "evidence_kept", "evidence_dropped", "old_s", "new_s", "rejected_msg"]
    with open(os.path.join(args.out, "summary.md"), "w", encoding="utf-8") as f:
        f.write("| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n")
        for e in summary:
            f.write("| " + " | ".join(str(e.get(c, "")) for c in cols) + " |\n")
    print(f"\nWrote {args.out}/results.csv and {args.out}/summary.md — mark `usable` by hand, then compare.")


if __name__ == "__main__":
    asyncio.run(main())
