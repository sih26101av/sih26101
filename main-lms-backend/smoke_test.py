"""
smoke_test.py — End-to-end API test for skill-gaps + recommendations
Run from: c:\Users\avi40\Desktop\SIH_IGot\main-lms-backend
"""
import httpx
import json
import sys

BASE = "http://localhost:8000"

# ── 1. Login ──────────────────────────────────────────────────────────────────
print("=== STEP 1: Login ===")
try:
    resp = httpx.post(
        f"{BASE}/auth/login",
        data={"username": "admin", "password": "admin123"},
        timeout=10,
    )
except Exception as e:
    print(f"FATAL: Backend not reachable — {e}")
    sys.exit(1)

print(f"Status: {resp.status_code}")
if resp.status_code != 200:
    print("Login failed:", resp.text[:300])
    sys.exit(1)

token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("Got JWT token OK")

# ── 2. Get first learner userId ───────────────────────────────────────────────
print("\n=== STEP 2: Get first learner ID from mock server ===")
try:
    resp2 = httpx.get(
        "http://localhost:8001/api/v1/users",
        headers={"x-authenticated-userid": "usr_admin", "x-authenticated-token": "mock-api-key-2026"},
        timeout=10,
    )
    users_raw = resp2.json()
    users_list = users_raw if isinstance(users_raw, list) else users_raw.get("users", [])
except Exception as e:
    print(f"WARN: Mock server error — {e}. Using hardcoded userId.")
    users_list = [{"userId": "usr_720465595"}]

uid = None
for u in users_list:
    uid = u.get("userId") or u.get("id")
    if uid and uid.startswith("usr_"):
        break

if not uid:
    print("FATAL: No learner userId found.")
    sys.exit(1)
print(f"Using userId: {uid}")

# ── 3. Skill Gaps ─────────────────────────────────────────────────────────────
print("\n=== STEP 3: Skill Gaps ===")
resp3 = httpx.get(f"{BASE}/api/v1/learner/{uid}/skill-gaps", headers=headers, timeout=15)
print(f"Status: {resp3.status_code}")
if resp3.status_code == 200:
    data = resp3.json()
    gaps = data.get("skillGaps", [])
    print(f"Gaps returned: {len(gaps)}")
    for g in gaps[:5]:
        status = "POSITIVE GAP" if g["gapScore"] > 0 else "NO GAP"
        print(f"  [{status}] {g['skillName'][:45]}: {g['currentLevel']} → {g['targetLevel']} (gap={g['gapScore']}, domain={g['domain']})")
    if not any(g["gapScore"] > 0 for g in gaps):
        print("  *** WARNING: All gaps are 0 — fix may not have worked ***")
    else:
        print("  ✓ Non-zero gaps found — skill gap logic working correctly!")
else:
    print("ERROR:", resp3.text[:400])

# ── 4. Recommendations ───────────────────────────────────────────────────────
print("\n=== STEP 4: Recommendations ===")
resp4 = httpx.get(f"{BASE}/api/v1/learner/{uid}/recommendations", headers=headers, timeout=60)
print(f"Status: {resp4.status_code}")
if resp4.status_code == 200:
    data = resp4.json()
    recs = data.get("recommendations", [])
    print(f"Recommendations returned: {len(recs)}")
    for r in recs[:5]:
        print(f"\n  #{r['priorityRank']} [{r['finalScore']:.3f}] {r['title'][:55]}")
        print(f"     Gap     : {r['competencyName']}")
        print(f"     Scores  : relevance={r['relevanceScore']:.3f}  quality={r['qualityScore']:.3f}")
        reasons = " | ".join(r.get("matchReasons", [])[:2])
        print(f"     Reasons : {reasons}")
    if len(recs) == 0:
        print("  *** WARNING: Zero recommendations returned ***")
    else:
        print(f"\n  ✓ {len(recs)} recommendations returned — recommendation engine working!")
else:
    print("ERROR:", resp4.text[:400])

print("\n=== SMOKE TEST COMPLETE ===")
