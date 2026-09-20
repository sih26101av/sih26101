#!/usr/bin/env bash
# Sync the VM to origin/main and restart. Run by the GitHub Action on every
# backend push, or by hand: bash ~/sih26101/deploy/oracle/update.sh
# .env, venv/ and model caches are gitignored, so the reset leaves them alone.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO"

git fetch --quiet origin main
git reset --quiet --hard origin/main
echo "==> Now at $(git log -1 --format='%h %an: %s')"

PIP="$REPO/venv/bin/pip"
REQS=(-r main-lms-backend/requirements.txt -r mock-igot-server/requirements.txt)
# Keep media support if it was installed at setup time.
MEDIA=0
"$PIP" show faster-whisper >/dev/null 2>&1 && { MEDIA=1; REQS+=(-r main-lms-backend/requirements-media.txt); }
"$PIP" install --quiet "${REQS[@]}"

# rapidocr depends on the FULL opencv-python wheel, which pip installs over the
# headless one and which needs libGL/libglib at import time. On a headless server
# `import cv2` then raises and video uploads 503 with "libGL.so.1: cannot open
# shared object file", while audio and documents keep working. Both steps below
# are idempotent and only run when cv2 is actually broken; neither may fail the
# deploy, because everything except video works without them.
cv2_ok() { [ "$MEDIA" = "1" ] && "$REPO/venv/bin/python" -c "import cv2" >/dev/null 2>&1; }

if [ "$MEDIA" = "1" ] && ! cv2_ok; then
  # Preferred fix: the headless wheel is the same cv2 minus the GUI calls we never
  # make, and needs no system libraries. Must come after the pip install above, or
  # it gets overwritten again. --force-reinstall because both wheels own cv2/ and
  # the uninstall takes those files with it.
  echo "==> cv2 will not import; switching to the headless OpenCV wheel"
  "$PIP" uninstall -y opencv-python opencv-contrib-python >/dev/null 2>&1 || true
  "$PIP" install --quiet --force-reinstall opencv-python-headless || true
fi

if [ "$MEDIA" = "1" ] && ! cv2_ok; then
  echo "==> still no cv2; installing the OpenCV system libraries"
  sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq || true
  # One package per call: the names differ across releases (noble renamed
  # libglib2.0-0 to libglib2.0-0t64, and dropped libgl1-mesa-glx), and apt aborts
  # the whole transaction over a single unknown name — which would skip the rest.
  for pkg in libgl1 libgl1-mesa-glx libglib2.0-0t64 libglib2.0-0; do
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "$pkg" >/dev/null 2>&1 || true
  done
fi

if [ "$MEDIA" = "1" ]; then
  if cv2_ok; then
    echo "==> cv2 ok"
  else
    echo "!! cv2 still will not import — video uploads will 503 (audio and documents keep working)"
  fi
fi

# Pick up edits to the unit files too.
sudo cp deploy/oracle/mock-igot.service deploy/oracle/lms-backend.service /etc/systemd/system/
sudo sed -i "s|/home/ubuntu/sih26101|$REPO|g; s|^User=ubuntu|User=$USER|" \
  /etc/systemd/system/mock-igot.service /etc/systemd/system/lms-backend.service
sudo systemctl daemon-reload
sudo systemctl restart mock-igot lms-backend
echo "==> Restarted. Warm-up runs in the background; /health shows \"ready\":true when done."
