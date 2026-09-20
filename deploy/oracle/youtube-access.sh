#!/usr/bin/env bash
# Give the VM a way past YouTube's anti-bot check, and say whether it worked.
#
#   bash deploy/oracle/youtube-access.sh                     # just diagnose
#   bash deploy/oracle/youtube-access.sh --pot               # free: PO-token provider
#   bash deploy/oracle/youtube-access.sh --cookies ~/yt.txt  # dependable: cookies.txt
#   bash deploy/oracle/youtube-access.sh --proxy http://user:pass@host:port
#
# Why this exists: YouTube decides by IP reputation, and Oracle's ranges are flagged.
# From this VM every InnerTube player client AND a plain browser-UA watch-page GET come
# back LOGIN_REQUIRED / "Sign in to confirm you're not a bot", so no amount of code
# gets a video — the request has to carry credentials or leave from another address.
# Nothing here affects file uploads, which never touch YouTube.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
ENVF="$REPO/main-lms-backend/.env"
POT_PORT=4416
MODE="check"
ARG=""

while [ $# -gt 0 ]; do
  case "$1" in
    --pot)     MODE="pot" ;;
    --cookies) MODE="cookies"; ARG="${2:-}"; shift ;;
    --proxy)   MODE="proxy";   ARG="${2:-}"; shift ;;
    --check)   MODE="check" ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

[ -f "$ENVF" ] || { echo "!! no $ENVF" >&2; exit 1; }

# Replace KEY=... in .env, or append it. .env is gitignored and survives the
# `git reset --hard` in update.sh, which is why the settings live there.
set_env() {
  local key="$1" val="$2"
  if grep -q "^${key}=" "$ENVF"; then
    # The value is base64 or a URL, so use a delimiter neither can contain.
    python3 - "$ENVF" "$key" "$val" <<'PY'
import sys
path, key, val = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(path, encoding="utf-8").read().splitlines()
out = [f"{key}={val}" if l.startswith(f"{key}=") else l for l in lines]
open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
PY
  else
    printf '\n%s=%s\n' "$key" "$val" >> "$ENVF"
  fi
  echo "==> $key set in .env"
}

case "$MODE" in

cookies)
  # The dependable fix. Export cookies.txt (Netscape format) from a browser signed
  # in to a THROWAWAY Google account — YouTube suspends accounts whose cookies are
  # reused from a server — then scp it here and point this at it.
  [ -f "$ARG" ] || { echo "!! --cookies needs a readable cookies.txt (got '$ARG')" >&2; exit 2; }
  grep -q $'\t' "$ARG" || { echo "!! $ARG is not Netscape cookies.txt (no tabs)" >&2; exit 2; }
  grep -qi 'youtube\.com' "$ARG" || echo "!! warning: no youtube.com cookies in $ARG"
  # One base64 line, because .env cannot hold a multi-line value and the backend
  # materialises it back to a file (media_io.cookies_path).
  set_env MEDIA_YOUTUBE_COOKIES_B64 "$(base64 -w0 < "$ARG")"
  chmod 600 "$ENVF"
  echo "==> cookies stored. They expire — re-run this when YouTube starts refusing again."
  ;;

pot)
  # The free attempt: a PO-token provider attests the request the way a browser does.
  # It can restore the gated media URLs; it does NOT always beat an IP-level wall.
  if ! command -v docker >/dev/null 2>&1; then
    echo "==> installing Docker"
    sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y docker.io
  fi
  sudo docker rm -f bgutil-pot >/dev/null 2>&1 || true
  echo "==> starting the bgutil PO-token provider on :$POT_PORT"
  sudo docker run -d --restart unless-stopped --name bgutil-pot \
    -p "127.0.0.1:$POT_PORT:$POT_PORT" brainicism/bgutil-ytdlp-pot-provider
  "$REPO/venv/bin/pip" install --quiet --upgrade bgutil-ytdlp-pot-provider
  set_env MEDIA_YOUTUBE_POT_URL "http://127.0.0.1:$POT_PORT"
  ;;

proxy)
  # The other dependable fix: leave from an address YouTube does not distrust.
  # A residential/mobile proxy works; another datacenter is usually just as blocked.
  [ -n "$ARG" ] || { echo "!! --proxy needs a URL" >&2; exit 2; }
  set_env MEDIA_YOUTUBE_PROXY "$ARG"
  ;;

esac

if [ "$MODE" != "check" ]; then
  echo "==> restarting the backend"
  sudo systemctl restart lms-backend
  # The router's diagnosis imports yt-dlp and reaches YouTube; give uvicorn a moment.
  for _ in $(seq 1 30); do
    curl -fsS --max-time 2 http://127.0.0.1:8000/health >/dev/null 2>&1 && break
    sleep 1
  done
fi

echo "==> asking the server what it can reach"
DIAG=/tmp/yt-diagnose.json
curl -fsS --max-time 180 -o "$DIAG" \
  "http://127.0.0.1:8000/api/v1/rag/media/youtube/diagnose?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DdMRDzicSvXk"

python3 - "$DIAG" <<'PY'
import json, sys

d = json.load(open(sys.argv[1], encoding="utf-8"))
v = d.get("verdict") or {}
print("  yt-dlp        :", d.get("yt_dlp"), "|", d.get("arch"))
print("  cookies/proxy :", d.get("cookies"), "/", d.get("proxy"), "| pot:", d.get("pot_provider"))
for name, c in (d.get("clients") or {}).items():
    if c.get("ok"):
        caps = c.get("caption_lang") or "-"
        print("  %-13s: ok  captions=%s formats=%sv/%sa"
              % (name, caps, c.get("video_formats"), c.get("audio_formats")))
    else:
        why = "BLOCKED" if c.get("blocked") else "failed "
        print("  %-13s: %s %s" % (name, why, (c.get("error") or "")[:70]))
w = d.get("watch_page") or {}
print("  watch page    :", w.get("playability"), "| caption tracks:", len(w.get("caption_tracks") or []))
print()
if v.get("can_generate_quiz"):
    frames = "yes" if v.get("can_use_video_frames") else "no (captions-only quiz, which is fine)"
    print("  YOUTUBE LINKS WORK. speech from:", v.get("speech_from"), "| video frames:", frames)
else:
    print("  YOUTUBE LINKS STILL BLOCKED from this IP.")
    print("  Next: --pot (free, may not be enough) -> --cookies (dependable) -> --proxy.")
    print("  Uploads are unaffected and are the reliable demo path.")
PY
