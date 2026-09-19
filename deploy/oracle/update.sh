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
"$PIP" show faster-whisper >/dev/null 2>&1 && REQS+=(-r main-lms-backend/requirements-media.txt)
"$PIP" install --quiet "${REQS[@]}"

# Pick up edits to the unit files too.
sudo cp deploy/oracle/mock-igot.service deploy/oracle/lms-backend.service /etc/systemd/system/
sudo sed -i "s|/home/ubuntu/sih26101|$REPO|g; s|^User=ubuntu|User=$USER|" \
  /etc/systemd/system/mock-igot.service /etc/systemd/system/lms-backend.service
sudo systemctl daemon-reload
sudo systemctl restart mock-igot lms-backend
echo "==> Restarted. Warm-up runs in the background; /health shows \"ready\":true when done."
