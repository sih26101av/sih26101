"""
scripts/download_model.py
─────────────────────────────────────────────────────────────────────────────
Build-time model fetch + cache warm-up, so the server starts without PyTorch
and without re-embedding anything.

  1. For each embedder role (ai/embedder.py: "chat", "catalog") downloads the
     model's own ONNX export + tokenizer/pooling configs from the HF Hub into
     ai/.cache/onnx/<org>__<model>/. These are the upstream fp32 exports, so
     vectors match sentence-transformers.
  2. Warm-up (skip with --no-warm): encodes the Gyan intent prototypes and the
     on-disk course catalogue once into ai/.cache/emb/, so the first boot after
     a deploy loads vectors instead of computing them.

Render Build Command:
    pip install -r requirements.txt && python scripts/download_model.py

Environment variables (optional):
    HF_TOKEN              — HuggingFace token (higher rate limits)
    EMBEDDER_ONNX_FILE    — ONNX file inside the model repo (default onnx/model.onnx).
                            A quantised export (e.g. onnx/model_qint8_avx512_vnni.onnx)
                            cuts RAM ~4× but shifts scores slightly — re-run
                            scripts/eval_intents.py before using it for "chat".
    CHAT_EMBEDDER_MODEL / CATALOG_EMBEDDER_MODEL — same overrides as the server.
─────────────────────────────────────────────────────────────────────────────
"""

import logging
import os
import shutil
import sys

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BACKEND_DIR)

from ai.embedder import DEFAULT_MODELS, model_name, onnx_model_dir  # noqa: E402

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ONNX_FILE = os.getenv("EMBEDDER_ONNX_FILE", "onnx/model.onnx")
CONFIG_FILES = ["sentence_bert_config.json", "special_tokens_map.json", "1_Pooling/config.json"]


def _fetch(repo: str, filename: str, dest: str) -> None:
    from huggingface_hub import hf_hub_download

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    src = hf_hub_download(repo_id=repo, filename=filename, token=os.getenv("HF_TOKEN") or None)
    shutil.copyfile(src, dest)


def download(name: str) -> None:
    target = onnx_model_dir(name)
    model_path = os.path.join(target, "model.onnx")
    if os.path.exists(model_path):
        logger.info("OK %s already cached (%.1f MB).", name, os.path.getsize(model_path) / 1_048_576)
        return

    logger.info("Downloading %s (%s) …", name, ONNX_FILE)
    tmp = target + ".partial"
    shutil.rmtree(tmp, ignore_errors=True)
    for f in CONFIG_FILES:
        _fetch(name, f, os.path.join(tmp, f))
    try:
        _fetch(name, "tokenizer.json", os.path.join(tmp, "tokenizer.json"))
    except Exception:
        _fetch(name, "onnx/tokenizer.json", os.path.join(tmp, "tokenizer.json"))
    _fetch(name, ONNX_FILE, os.path.join(tmp, "model.onnx"))   # last: its presence marks "complete"
    shutil.rmtree(target, ignore_errors=True)
    os.replace(tmp, target)
    logger.info("OK %s -> %s (%.1f MB).", name, target, os.path.getsize(model_path) / 1_048_576)


def warm() -> None:
    """Encode the fixed corpora once so the server's startup is a cache hit."""
    from ai import semantic_engine
    from services.recommendation_service import HybridRecommendationEngine

    semantic_engine._ensure_prototypes()
    if not semantic_engine.is_semantic_engine_ready():
        raise RuntimeError("intent prototypes could not be encoded")
    engine = HybridRecommendationEngine()   # disk catalogue — the same files the mock server serves
    logger.info("OK Embedding cache warm (%d intent prototypes, catalogue from %s).",
                len(semantic_engine._PROTOTYPE_SENTENCES), engine.catalog_source)


def main() -> None:
    for name in sorted({model_name(role) for role in DEFAULT_MODELS}):
        download(name)
    if "--no-warm" not in sys.argv:
        try:
            warm()
        except Exception as exc:        # a cold cache only costs startup time, never correctness
            logger.warning("Cache warm-up skipped: %s", exc)


if __name__ == "__main__":
    main()
