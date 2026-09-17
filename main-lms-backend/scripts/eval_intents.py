"""
Benchmark Gyan's intent classifier on the held-out multilingual set.

    python scripts/eval_intents.py
    python scripts/eval_intents.py --model intfloat/multilingual-e5-small --top-k 1
    python scripts/eval_intents.py --detect          # route by detected language, not the true one
    python scripts/eval_intents.py --json out.json

Eval phrases: tests/data/intent_eval/<lang>.json  ({intent: [phrases]}).
"""

from __future__ import annotations

import argparse
import io
import json
import logging
import os
import sys
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVAL_DIR = os.path.join(ROOT, "tests", "data", "intent_eval")


def load_eval() -> dict[str, dict[str, list[str]]]:
    return {
        name[:-5]: json.load(open(os.path.join(EVAL_DIR, name), encoding="utf-8"))
        for name in sorted(os.listdir(EVAL_DIR)) if name.endswith(".json")
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", help="CHAT_EMBEDDER_MODEL override")
    parser.add_argument("--top-k", type=int, default=None)
    parser.add_argument("--detect", action="store_true", help="classify using detected language")
    parser.add_argument("--json", help="write results to this path")
    args = parser.parse_args()

    if args.model:
        os.environ["CHAT_EMBEDDER_MODEL"] = args.model
    sys.path.insert(0, ROOT)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    logging.disable(logging.WARNING)

    from ai import embedder, semantic_engine as se
    from services.language_service import detect_chat_variant

    top_k = args.top_k or se.TOP_K
    data = load_eval()

    prototypes = {p.strip().lower() for p in se._PROTOTYPE_SENTENCES}
    leaked = [(l, i, p) for l, d in data.items() for i, ps in d.items() for p in ps if p.strip().lower() in prototypes]
    if leaked:
        print(f"WARNING: {len(leaked)} eval phrases also appear as prototypes: {leaked[:5]}")

    results: dict = {"model": embedder.model_name("chat"), "top_k": top_k, "detect": args.detect, "languages": {}}
    confusions: Counter = Counter()
    in_scope_conf, oos_conf = [], []

    print(f"model={results['model']}  top_k={top_k}  routing={'detected' if args.detect else 'true'} language\n")
    print(f"{'lang':<8} {'acc':>6} {'n':>4} {'detect_acc':>10}")
    print("-" * 32)
    for lang, intents in data.items():
        correct = total = detected_ok = 0
        for intent, phrases in intents.items():
            for phrase in phrases:
                detected = detect_chat_variant(phrase)
                routed = detected if args.detect else lang
                scores = se.score_intents(phrase, routed, top_k=top_k)
                predicted = max(scores, key=scores.get)
                total += 1
                correct += predicted == intent
                detected_ok += detected == lang or {detected, lang} <= {"en", "hi_latn"}
                if predicted != intent:
                    confusions[(lang, intent, predicted)] += 1
                (oos_conf if intent == "out_of_scope" else in_scope_conf).append(scores[predicted])
        acc = correct / total
        results["languages"][lang] = {"accuracy": round(acc, 4), "n": total, "detect_accuracy": round(detected_ok / total, 4)}
        print(f"{lang:<8} {acc:6.1%} {total:4d} {detected_ok / total:10.1%}")

    accs = [v["accuracy"] for v in results["languages"].values()]
    results["macro_accuracy"] = round(sum(accs) / len(accs), 4)
    print("-" * 32)
    print(f"{'macro':<8} {results['macro_accuracy']:6.1%}\n")

    print("Top confusions (lang, true -> predicted):")
    for (lang, true, pred), n in confusions.most_common(15):
        print(f"  {n}x  {lang:<8} {true} -> {pred}")

    def pct(values, q):
        values = sorted(values)
        return values[min(len(values) - 1, int(q * len(values)))] if values else 0.0

    print("\nWinning confidence  p10 / p50 / p90")
    print(f"  in-scope      {pct(in_scope_conf, .1):.3f} / {pct(in_scope_conf, .5):.3f} / {pct(in_scope_conf, .9):.3f}")
    print(f"  out_of_scope  {pct(oos_conf, .1):.3f} / {pct(oos_conf, .5):.3f} / {pct(oos_conf, .9):.3f}")
    results["top_confusions"] = [[*k, n] for k, n in confusions.most_common(30)]

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\nwrote {args.json}")


if __name__ == "__main__":
    main()
