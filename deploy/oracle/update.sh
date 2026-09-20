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

# OpenCV comes from rapidocr as the full (non-headless) wheel, which needs these
# system libraries. Without them video uploads 503 with "libGL.so.1: cannot open
# shared object file" while audio keeps working. Idempotent: only runs when broken.
if [ "$MEDIA" = "1" ] && ! "$REPO/venv/bin/python" -c "import cv2" >/dev/null 2>&1; then
  echo "==> cv2 will not import; installing libgl1 libglib2.0-0"
  # Never fail the deploy over this: without it only video uploads break.
  sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq || true
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y libgl1 libglib2.0-0 || true
  if "$REPO/venv/bin/python" -c "import cv2" >/dev/null 2>&1; then
    echo "==> cv2 imports now"
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
