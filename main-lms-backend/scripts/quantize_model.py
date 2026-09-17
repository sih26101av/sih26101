"""
scripts/quantize_model.py
─────────────────────────────────────────────────────────────────────────────
ONE-TIME LOCAL SETUP SCRIPT — Do NOT run on Render.

Exports paraphrase-multilingual-MiniLM-L12-v2 to ONNX and quantizes it
to INT8, shrinking it from ~470 MB → ~115 MB with 2-3x faster CPU inference.

Requirements (dev only — NOT needed in production requirements.txt):
    pip install optimum[onnxruntime] torch

Output:
    main-lms-backend/ai/.cache/model_int8.onnx   ← commit via Git LFS or
                                                     upload to HuggingFace Hub

Run:
    cd main-lms-backend
    python scripts/quantize_model.py

After running:
    1. Upload ai/.cache/model_int8.onnx to HuggingFace Hub
       (see scripts/upload_instructions.md)
    2. Update REPO_ID in scripts/download_model.py
─────────────────────────────────────────────────────────────────────────────
"""

import logging
import os
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

MODEL_NAME   = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CACHE_DIR    = os.path.join(os.path.dirname(__file__), "..", "ai", ".cache")
EXPORT_DIR   = os.path.join(CACHE_DIR, "model_onnx_fp32")
ONNX_FP32    = os.path.join(EXPORT_DIR, "model.onnx")
ONNX_INT8    = os.path.join(CACHE_DIR, "model_int8.onnx")


def main() -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(EXPORT_DIR, exist_ok=True)

    # ── Step 1: Check for required packages ──────────────────────────────────
    try:
        from optimum.onnxruntime import ORTModelForFeatureExtraction
        from onnxruntime.quantization import quantize_dynamic, QuantType
        from transformers import AutoTokenizer
    except ImportError as e:
        logger.error("Missing dependency: %s", e)
        logger.error("Install with:  pip install optimum[onnxruntime] torch")
        sys.exit(1)

    # ── Step 2: Export to ONNX (FP32) ───────────────────────────────────────
    if os.path.exists(ONNX_FP32):
        logger.info("FP32 ONNX already exists at %s — skipping export.", ONNX_FP32)
    else:
        logger.info("Exporting %s to ONNX (FP32)…", MODEL_NAME)
        logger.info("This downloads ~470 MB from HuggingFace Hub on first run.")
        model = ORTModelForFeatureExtraction.from_pretrained(MODEL_NAME, export=True)
        model.save_pretrained(EXPORT_DIR)
        logger.info("FP32 ONNX saved to %s", EXPORT_DIR)

        # Save tokenizer alongside (needed for verification)
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        tokenizer.save_pretrained(EXPORT_DIR)
        logger.info("Tokenizer saved to %s", EXPORT_DIR)

    # ── Step 3: INT8 Dynamic Quantization ───────────────────────────────────
    if os.path.exists(ONNX_INT8):
        logger.info("INT8 ONNX already exists at %s — skipping quantization.", ONNX_INT8)
    else:
        logger.info("Quantizing FP32 ONNX → INT8 (dynamic quantization)…")
        quantize_dynamic(
            model_input=ONNX_FP32,
            model_output=ONNX_INT8,
            weight_type=QuantType.QInt8,
            optimize_model=True,
        )
        logger.info("INT8 ONNX saved to %s", ONNX_INT8)

    # ── Step 4: Smoke test ───────────────────────────────────────────────────
    logger.info("Running smoke test on quantized model…")
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    # Temporarily point the embedder at the freshly quantized file
    import ai.embedder as _emb_mod
    _emb_mod._embedder = None  # reset singleton for test
    _emb_mod._ONNX_PATH = ONNX_INT8
    embedder = _emb_mod.get_embedder()

    test_pairs = [
        ("Show my skill gaps", "what are my skill gaps"),
        ("नमस्ते",             "hello"),
        ("मेरे कौशल अंतराल",   "skill gap analysis"),
        ("कौन सा कोर्स करूँ",  "recommend me a course"),
    ]
    passed = 0
    for q_regional, q_english in test_pairs:
        v_regional = embedder.encode(q_regional, normalize_embeddings=True)
        v_english  = embedder.encode(q_english,  normalize_embeddings=True)
        similarity = float(v_regional @ v_english)
        status = "✅" if similarity > 0.5 else "⚠️ "
        logger.info("  %s  Similarity(%-35s / %-25s) = %.3f",
                    status, repr(q_regional), repr(q_english), similarity)
        if similarity > 0.5:
            passed += 1

    size_mb = os.path.getsize(ONNX_INT8) / 1_048_576
    logger.info("\n── Summary ─────────────────────────────────────────────")
    logger.info("  INT8 model size : %.1f MB", size_mb)
    logger.info("  Smoke tests     : %d / %d passed", passed, len(test_pairs))

    if passed < len(test_pairs) // 2:
        logger.error("Too many smoke tests failed — quantization may have degraded quality.")
        sys.exit(1)

    logger.info("\n✅ Quantization complete!")
    logger.info("Next steps:")
    logger.info("  1. Upload %s to HuggingFace Hub or GitHub Release", ONNX_INT8)
    logger.info("  2. Update REPO_ID / DOWNLOAD_URL in scripts/download_model.py")
    logger.info("  3. Add ai/.cache/ to .gitignore if not already there")


if __name__ == "__main__":
    main()
