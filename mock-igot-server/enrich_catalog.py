"""
FILE: mock-igot-server/enrich_catalog.py
─────────────────────────────────────────────────────────────────────────────
One-time seed script: adds quality-scoring fields to course_catalog.json.
Run ONCE before starting the backend.

Fields added per course (idempotent — skips if already present):
  rating           float  [3.0, 5.0]   — Bayesian-weighted avg rating
  rating_count     int    [10, 800]    — number of ratings
  enrollment_count int    [50, 5000]   — total enrollments
  completion_rate  float  [0.30, 0.95] — fraction who completed
  is_tpac          bool               — True if NSSTA-created or vetted
─────────────────────────────────────────────────────────────────────────────
"""

import json
import hashlib
import random
import os
import sys

CATALOG_PATH = os.path.join(os.path.dirname(__file__), "data", "course_catalog.json")

NSSTA_CREATORS = {
    "National Academy of Statistical Administration",
    "NSSTA",
}
NSSTA_ORG_KEYWORDS = {"NSSTA", "National Academy of Statistical Administration"}


def _seeded_rng(identifier: str) -> random.Random:
    """Returns a deterministic RNG seeded by the course identifier hash."""
    seed = int(hashlib.md5(identifier.encode()).hexdigest(), 16) % (2**31)
    return random.Random(seed)


def enrich_course(course: dict) -> dict:
    """Add quality fields to a course dict (in-place, idempotent)."""
    # Skip if already enriched
    if "rating" in course and "is_tpac" in course:
        return course

    identifier = course.get("identifier", course.get("id", "unknown"))
    rng = _seeded_rng(identifier)

    # ── Quality metrics ────────────────────────────────────────────────────────
    course.setdefault("rating",           round(rng.uniform(3.0, 5.0), 2))
    course.setdefault("rating_count",     rng.randint(10, 800))
    course.setdefault("enrollment_count", rng.randint(50, 5000))
    course.setdefault("completion_rate",  round(rng.uniform(0.30, 0.95), 4))

    # ── TPAC / NSSTA flag ──────────────────────────────────────────────────────
    creator = course.get("creator", "")
    orgs    = course.get("organisation", [])
    is_tpac = (
        any(keyword in creator for keyword in NSSTA_CREATORS)
        or any(
            any(keyword in org for keyword in NSSTA_ORG_KEYWORDS)
            for org in orgs
        )
    )
    course.setdefault("is_tpac", is_tpac)

    return course


def main():
    if not os.path.exists(CATALOG_PATH):
        print(f"[ERROR] Catalog not found at: {CATALOG_PATH}", file=sys.stderr)
        sys.exit(1)

    print(f"[enrich_catalog] Reading {CATALOG_PATH} …")
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    already_enriched = sum(1 for c in catalog if "rating" in c and "is_tpac" in c)
    if already_enriched == len(catalog):
        print(f"[enrich_catalog] All {len(catalog)} courses already enriched. Nothing to do.")
        return

    enriched = [enrich_course(c) for c in catalog]
    tpac_count = sum(1 for c in enriched if c.get("is_tpac"))

    print(f"[enrich_catalog] Writing {len(enriched)} courses "
          f"({tpac_count} NSSTA/TPAC-vetted) …")

    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print("[enrich_catalog] Done. course_catalog.json is now quality-enriched.")


if __name__ == "__main__":
    main()
