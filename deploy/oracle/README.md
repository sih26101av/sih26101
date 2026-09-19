# Deploy: backend on Oracle Cloud, frontend on Vercel

```
Browser ──► Vercel (static React build)
   │
   └──HTTPS──► Oracle VM: Caddy :443 ──► uvicorn main:app 127.0.0.1:8000
                                              └──► mock iGOT 127.0.0.1:8001
                                              └──► Neon Postgres (DATABASE_URL)
```

Only Caddy is exposed to the internet. Ports 8000 and 8001 stay on localhost.

## 1. Create the VM (Oracle Cloud console)

1. **Compute → Instances → Create instance.**
   - Image: **Canonical Ubuntu 24.04** (or 22.04).
   - Shape: **Ampere VM.Standard.A1.Flex**, **2 OCPU / 12 GB** (the whole Always Free
     allowance; 1 / 6 also works). The ONNX embedders need about 2 GB, so the 1 GB AMD
     micro shape is too small. Free-tier instances idle for 7 days can be reclaimed;
     a Pay As You Go account avoids that and is still ₹0 within the free limits.
   - Upload or download the SSH key.
2. **Networking → your VCN → Security List → Add Ingress Rules:** source `0.0.0.0/0`,
   TCP, destination ports **80** and **443**.
3. Note the instance's **public IP**.

## 2. Pick the API hostname

- **Own domain:** add an `A` record, `api.yourdomain` → public IP.
- **No domain:** use `<ip-with-dashes>.sslip.io`, for example `140-238-10-20.sslip.io`.
  It resolves to your IP automatically and still gets a real HTTPS certificate.

HTTPS is required, not optional. A Vercel page served over HTTPS cannot call a plain
`http://` API, and the cross-site refresh cookie needs `Secure`.

## 3. Set up the VM

```bash
ssh -i <key> ubuntu@<public-ip>
git clone https://github.com/sih26101av/sih26101.git
cd sih26101
nano main-lms-backend/.env        # see below
bash deploy/oracle/setup.sh <api-hostname>
# add video/audio quiz support:  WITH_MEDIA=1 bash deploy/oracle/setup.sh <api-hostname>
```

`main-lms-backend/.env` starts from your local `.env`, with these changes:

```ini
DATABASE_URL=...              # same Neon URL as local, so existing logins keep working
JWT_SECRET_KEY=...            # a long random value
IGOT_MOCK_BASE_URL=http://127.0.0.1:8001
IGOT_MOCK_TOKEN=mock-api-key-2026
GROQ_API_KEYS=...
GEMINI_API_KEY=...
CORS_ORIGINS=https://<your-app>.vercel.app
COOKIE_SAMESITE=none
```

Check it:

```bash
curl https://<api-hostname>/health     # "ready": true once warm-up has finished
journalctl -u lms-backend -f           # logs
```

Seed users once, and only if the Neon database is new: `cd main-lms-backend && ../venv/bin/python -m auth.seed`.

## 4. Frontend on Vercel

1. vercel.com → **Add New → Project** → import `sih26101av/sih26101`.
2. **Root Directory:** `frontend`. The framework preset is detected as Vite.
   The build command is `npm run build` and the output directory is `dist`.
3. **Environment Variables:** `VITE_API_BASE_URL = https://<api-hostname>` (no trailing slash).
4. Deploy. If the final URL differs from what you put in `CORS_ORIGINS`, update
   `.env` on the VM and run `sudo systemctl restart lms-backend`.

`VITE_API_BASE_URL` is compiled into the bundle, so changing it needs a Vercel redeploy.

## Updating: just `git push` to `main`

- **Frontend:** Vercel rebuilds on every push.
- **Backend:** `.github/workflows/deploy-backend.yml` runs on pushes that touch
  `main-lms-backend/`, `mock-igot-server/` or `deploy/oracle/`. It SSHes into the VM,
  runs `deploy/oracle/update.sh` (reset to `origin/main`, `pip install`, restart), then
  waits for `/health` to report `"ready":true`. Watch it under the repo's **Actions** tab.
  To re-run it by hand, use Actions → *Deploy backend (Oracle)* → *Run workflow*.
- The workflow needs two repo secrets (**Settings → Secrets and variables → Actions**):
  - `ORACLE_HOST`: the VM's public IP
  - `ORACLE_SSH_KEY`: a dedicated private key whose `.pub` is in the VM's `~/.ssh/authorized_keys`
- Manual fallback on the VM: `bash ~/sih26101/deploy/oracle/update.sh`.
- Changing `.env` on the VM needs a restart only: `sudo systemctl restart lms-backend`.
  `.env` is never touched by deploys.

## Troubleshooting

| Symptom | Cause |
|---|---|
| `curl https://…` hangs or times out | Port 80/443 is missing from the Security List, or from the VM's iptables (`setup.sh` opens them) |
| Caddy log shows a certificate error | DNS doesn't point at the VM yet, or port 80 is blocked |
| Browser shows a CORS error | `CORS_ORIGINS` doesn't exactly match the Vercel origin (scheme included, no trailing slash) |
| Logged out on page reload | The refresh cookie was blocked: check `COOKIE_SAMESITE=none`. Safari and strict third-party-cookie settings block it anyway; a custom domain on both sides (`app.x` + `api.x`) fixes that |
| Dashboard slow right after a restart | Normal. Routes wait for the AI warm-up (`/health` → `ready`) |
