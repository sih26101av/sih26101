#!/usr/bin/env bash
# One-time setup on a fresh Oracle Cloud Ubuntu 22.04/24.04 VM.
#   bash deploy/oracle/setup.sh <api-domain>
# Run from the repo root (/home/ubuntu/sih26101) as the ubuntu user.
set -euo pipefail
DOMAIN="${1:?usage: setup.sh <api-domain>}"
REPO="$(cd "$(dirname "$0")/../.." && pwd)"

echo "==> System packages"
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip git curl debian-keyring debian-archive-keyring apt-transport-https

echo "==> Caddy"
if ! command -v caddy >/dev/null; then
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --batch --yes --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
  sudo apt-get update && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y caddy
fi

echo "==> Open ports 80/443 in the VM firewall (Oracle images block them by default)"
# Insert before the image's catch-all REJECT rule, or the ACCEPT never matches.
for p in 80 443; do
  if ! sudo iptables -C INPUT -m state --state NEW -p tcp --dport $p -j ACCEPT 2>/dev/null; then
    R=$(sudo iptables -L INPUT --line-numbers -n | awk '/REJECT/{print $1; exit}')
    sudo iptables -I INPUT "${R:-1}" -m state --state NEW -p tcp --dport $p -j ACCEPT
  fi
done
sudo netfilter-persistent save || true

echo "==> Python venv + dependencies"
python3 -m venv "$REPO/venv"
"$REPO/venv/bin/pip" install --upgrade pip
"$REPO/venv/bin/pip" install -r "$REPO/main-lms-backend/requirements.txt" -r "$REPO/mock-igot-server/requirements.txt"
if [ "${WITH_MEDIA:-0}" = "1" ]; then
  "$REPO/venv/bin/pip" install -r "$REPO/main-lms-backend/requirements-media.txt"
fi

echo "==> Embedding models + caches"
(cd "$REPO/main-lms-backend" && "$REPO/venv/bin/python" scripts/download_model.py)

echo "==> systemd services"
sudo cp "$REPO/deploy/oracle/mock-igot.service" "$REPO/deploy/oracle/lms-backend.service" /etc/systemd/system/
sudo sed -i "s|/home/ubuntu/sih26101|$REPO|g; s|^User=ubuntu|User=$USER|" /etc/systemd/system/mock-igot.service /etc/systemd/system/lms-backend.service
sudo systemctl daemon-reload
sudo systemctl enable --now mock-igot lms-backend

echo "==> Caddy (HTTPS for $DOMAIN)"
sed "s|API_DOMAIN|$DOMAIN|" "$REPO/deploy/oracle/Caddyfile" | sudo tee /etc/caddy/Caddyfile >/dev/null
sudo systemctl reload caddy || sudo systemctl restart caddy

echo "Done. Check: curl https://$DOMAIN/health"
