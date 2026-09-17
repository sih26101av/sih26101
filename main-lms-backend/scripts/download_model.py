"""
scripts/download_model.py
─────────────────────────────────────────────────────────────────────────────
Production model download script.

Fetches the pre-quantized ONNX INT8 model from HuggingFace Hub.
Runs in Render's Build Command — takes ~3 seconds (no PyTorch needed).

Render Build Command (set in render.yaml or Render dashboard):
    pip install -r requirements.txt && python scripts/download_model.py

Usage locally:
    python scripts/download_model.py

Environment variables (optional):
    HF_TOKEN   — HuggingFace token (only needed if repo is private)
─────────────────────────────────────────────────────────────────────────────
"""

import logging
import os
import sys
import urllib.request

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ── UPDATE THESE after uploading to HuggingFace Hub ───────────────────────────
# Option A — HuggingFace Hub (recommended)
HF_REPO_ID  = "FILL_IN_AFTER_UPLOAD"   # e.g. "your-username/gyan-multilingual-onnx"
HF_FILENAME = "model_int8.onnx"

# Option B — Direct URL (GitHub Release, CDN, etc.)
DIRECT_URL  = ""   # e.g. "https://github.com/your-org/repo/releases/download/v1.0/model_int8.onnx"
# ──────────────────────────────────────────────────────────────────────────────

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "ai", ".cache")
DEST_PATH = os.path.join(CACHE_DIR, "model_int8.onnx")


def _download_from_hf() -> None:
    """Download from HuggingFace Hub using huggingface_hub library."""
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        logger.error("huggingface_hub not installed. Add it to requirements.txt.")
        sys.exit(1)

    token = os.getenv("HF_TOKEN")
    logger.info("Downloading %s from HuggingFace Hub repo: %s", HF_FILENAME, HF_REPO_ID)
    cached = hf_hub_download(
        repo_id=HF_REPO_ID,
        filename=HF_FILENAME,
        token=token,
        local_dir=CACHE_DIR,
    )
    logger.info("Downloaded to: %s", cached)


def _download_from_url(url: str) -> None:
    """Fallback: download via urllib (no extra deps)."""
    logger.info("Downloading model from: %s", url)
    os.makedirs(CACHE_DIR, exist_ok=True)

    def _progress(block_num, block_size, total_size):
        if total_size > 0:
            pct = block_num * block_size / total_size * 100
            print(f"\r  Downloading… {min(pct, 100):.1f}%", end="", flush=True)

    urllib.request.urlretrieve(url, DEST_PATH, reporthook=_progress)
    print()  # newline after progress
    logger.info("Saved to: %s", DEST_PATH)


def main() -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)

    if os.path.exists(DEST_PATH):
        size_mb = os.path.getsize(DEST_PATH) / 1_048_576
        logger.info("✅ Model already cached at %s (%.1f MB) — skipping download.", DEST_PATH, size_mb)
        return

    if HF_REPO_ID != "FILL_IN_AFTER_UPLOAD":
        _download_from_hf()
    elif DIRECT_URL:
        _download_from_url(DIRECT_URL)
    else:
        logger.error(
            "Model download not configured.\n"
            "  1. Run `python scripts/quantize_model.py` to generate the ONNX file locally.\n"
            "  2. Upload it to HuggingFace Hub and set HF_REPO_ID in this script.\n"
            "  OR set DIRECT_URL to a direct download link."
        )
        sys.exit(1)

    if os.path.exists(DEST_PATH):
        size_mb = os.path.getsize(DEST_PATH) / 1_048_576
        logger.info("✅ Download complete. Model size: %.1f MB", size_mb)
    else:
        logger.error("Download seemed to succeed but file not found at %s", DEST_PATH)
        sys.exit(1)


if __name__ == "__main__":
    main()
