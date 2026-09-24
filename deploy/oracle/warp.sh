#!/usr/bin/env bash
# Give yt-dlp a way out of Oracle's flagged address space: Cloudflare WARP, as a
# local SOCKS5 proxy that ONLY yt-dlp uses.
#
#   bash deploy/oracle/warp.sh        # install / repair; idempotent
#   (or: bash deploy/oracle/youtube-access.sh --warp, which also restarts + diagnoses)
#
# Why: YouTube decides by IP reputation. From this VM every player client and the
# watch page answer "Sign in to confirm you're not a bot", and the public relays sit
# in the same datacenter space. Through WARP the request leaves from a Cloudflare
# address instead — verified from a dev machine on 2026-09-24: default client, 344
# auto captions + 36 video formats, 360p stream downloaded, ~15 s.
#
# How, and why it is safe on a server:
#   • wgcf (MIT, github.com/ViRb3/wgcf) registers a free, anonymous WARP device — no
#     email, no account, no key to manage.
#   • wireproxy (ISC, github.com/windtf/wireproxy) runs that WireGuard tunnel in
#     USERSPACE and exposes it as SOCKS5 on 127.0.0.1. It creates no network interface
#     and changes no routes, so SSH, Caddy, Neon, Groq/Gemini and everything else keep
#     using the VM's own connection. Only yt-dlp is pointed at it (MEDIA_YOUTUBE_PROXY).
#   • Runs as the deploy user under systemd (Restart=always), not as root.
#   • Pinned versions; each download is checked against the sha256 digest GitHub
#     publishes for the release asset.
#   • If the tunnel does not come up, MEDIA_YOUTUBE_PROXY is removed again, so yt-dlp
#     is never left pointing at a dead proxy. An admin-set proxy is never overwritten.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
ENVF="$REPO/main-lms-backend/.env"
STATE="$HOME/.warp"                 # outside the repo: survives update.sh's git reset --hard
PORT="${WARP_SOCKS_PORT:-40000}"
PROXY="socks5h://127.0.0.1:$PORT"   # socks5h: DNS resolved inside the tunnel too
WGCF_VERSION=2.3.0
WIREPROXY_VERSION=1.1.3

case "$(uname -m)" in
  aarch64|arm64) ARCH=arm64 ;;
  x86_64|amd64)  ARCH=amd64 ;;
  *) echo "!! WARP: unsupported architecture $(uname -m)"; exit 1 ;;
esac

# Replace / remove KEY=... in .env (same approach as youtube-access.sh's set_env).
env_set() {
  python3 - "$ENVF" "$@" <<'PY'
import sys
path, key = sys.argv[1], sys.argv[2]
val = sys.argv[3] if len(sys.argv) > 3 else None
lines = open(path, encoding="utf-8").read().splitlines()
out = [l for l in lines if not l.startswith(key + "=")]
if val is not None:
    out.append(f"{key}={val}")
open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
PY
}

# Download one release asset and verify it against GitHub's published sha256 digest.
fetch() {  # <owner/repo> <tag> <asset> <dest>
  local repo="$1" tag="$2" asset="$3" dest="$4" want got
  want="$(curl -fsSL "https://api.github.com/repos/$repo/releases/tags/$tag" | python3 -c '
import json, sys
assets = [a for a in json.load(sys.stdin).get("assets", []) if a["name"] == sys.argv[1]]
print((assets[0].get("digest") or "").replace("sha256:", "") if assets else "")' "$asset" || true)"
  curl -fsSL -o "$dest" "https://github.com/$repo/releases/download/$tag/$asset"
  got="$(sha256sum "$dest" | cut -d' ' -f1)"
  if [ -n "$want" ] && [ "$want" != "$got" ]; then
    echo "!! WARP: checksum mismatch for $asset (want $want, got $got)"; rm -f "$dest"; return 1
  fi
  [ -n "$want" ] || echo "   (GitHub published no digest for $asset; sha256 $got)"
}

mkdir -p "$STATE" && chmod 700 "$STATE"

# ── binaries (only when the pinned versions change) ────────────────────────────
if [ "$(cat "$STATE/versions" 2>/dev/null || true)" != "$WGCF_VERSION $WIREPROXY_VERSION $ARCH" ]; then
  echo "==> installing wgcf $WGCF_VERSION + wireproxy $WIREPROXY_VERSION ($ARCH)"
  tmp="$(mktemp -d)"
  fetch ViRb3/wgcf "v$WGCF_VERSION" "wgcf_${WGCF_VERSION}_linux_${ARCH}" "$tmp/wgcf"
  fetch windtf/wireproxy "v$WIREPROXY_VERSION" "wireproxy_linux_${ARCH}.tar.gz" "$tmp/wp.tgz"
  tar xzf "$tmp/wp.tgz" -C "$tmp"
  bin="$(find "$tmp" -type f -name wireproxy | head -1)"
  [ -n "$bin" ] || { echo "!! WARP: no wireproxy binary in the release archive"; exit 1; }
  sudo install -m 755 "$tmp/wgcf" /usr/local/bin/wgcf
  sudo install -m 755 "$bin" /usr/local/bin/wireproxy
  rm -rf "$tmp"
  echo "$WGCF_VERSION $WIREPROXY_VERSION $ARCH" > "$STATE/versions"
fi

# ── anonymous WARP device + WireGuard profile (once) ───────────────────────────
cd "$STATE"
if [ ! -f wgcf-account.toml ]; then
  echo "==> registering a free WARP device"
  for _ in 1 2 3; do wgcf register --accept-tos >/dev/null 2>&1 && break; sleep 5; done
fi
[ -f wgcf-account.toml ] || { echo "!! WARP: registration failed"; exit 1; }
[ -f wgcf-profile.conf ] || wgcf generate >/dev/null 2>&1
[ -f wgcf-profile.conf ] || { echo "!! WARP: could not generate the WireGuard profile"; exit 1; }
chmod 600 wgcf-account.toml wgcf-profile.conf
printf 'WGConfig = %s/wgcf-profile.conf\n\n[Socks5]\nBindAddress = 127.0.0.1:%s\n' "$STATE" "$PORT" > wireproxy.conf

# ── service ────────────────────────────────────────────────────────────────────
sudo tee /etc/systemd/system/warp-socks.service >/dev/null <<UNIT
[Unit]
Description=Cloudflare WARP as a local SOCKS5 proxy (yt-dlp egress for YouTube only)
After=network-online.target
Wants=network-online.target

[Service]
User=$USER
ExecStart=/usr/local/bin/wireproxy -c $STATE/wireproxy.conf
Restart=always
RestartSec=5
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload
sudo systemctl enable warp-socks >/dev/null 2>&1
sudo systemctl restart warp-socks

# ── verify, then point yt-dlp at it (or take it away again) ────────────────────
trace=""
for _ in $(seq 1 15); do
  trace="$(curl -s --max-time 8 --socks5-hostname "127.0.0.1:$PORT" https://www.cloudflare.com/cdn-cgi/trace || true)"
  echo "$trace" | grep -q '^warp=on' && break
  trace=""; sleep 2
done
current="$(grep -E '^MEDIA_YOUTUBE_PROXY=' "$ENVF" | cut -d= -f2- || true)"
if [ -n "$trace" ]; then
  where="$(echo "$trace" | grep -E '^(ip|colo)=' | tr '\n' ' ')"
  if [ -z "$current" ] || [ "$current" = "$PROXY" ]; then
    env_set MEDIA_YOUTUBE_PROXY "$PROXY"
    echo "==> WARP up ($where) — yt-dlp now leaves through it ($PROXY)"
  else
    echo "==> WARP up ($where), but MEDIA_YOUTUBE_PROXY is already set to another proxy — left alone"
  fi
else
  echo "!! WARP tunnel did not come up (journalctl -u warp-socks)"
  if [ "$current" = "$PROXY" ]; then
    env_set MEDIA_YOUTUBE_PROXY      # never leave yt-dlp pointed at a dead proxy
    echo "   removed MEDIA_YOUTUBE_PROXY again"
  fi
  exit 1
fi
