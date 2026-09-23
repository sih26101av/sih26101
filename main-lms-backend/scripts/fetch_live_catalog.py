"""
scripts/fetch_live_catalog.py — pull the real iGOT Karmayogi catalogue to disk

Harvests every Live course from https://portal.igotkarmayogi.gov.in (public
content APIs, no credentials needed — see adapters/live_igot_adapter.py for
which endpoints are open and which sit behind the Kong 401), maps the Karmayogi
Competency Model tags onto this platform's FRAC competency ids, and writes the
result where the backend can boot from it.

    python -m scripts.fetch_live_catalog                 # harvest + crosswalk
    python -m scripts.fetch_live_catalog --no-crosswalk  # skip the embedder
    python -m scripts.fetch_live_catalog --limit 200     # quick smoke test

Output (all gitignored, under main-lms-backend/data/live/):
    live_catalog.json     normalised courses, KCM tags stamped with fracId
    live_kcm.json         the raw KCM framework (areas / themes / sub-themes)
    live_kcm_crosswalk.json  the proposed KCM → FRAC mappings, all unconfirmed
    MANIFEST.json         when it was pulled, from where, and how many

Run it on a schedule (the backend also refreshes in-process every
CATALOGUE_REFRESH_SECONDS when IGOT_CATALOGUE_SOURCE=live). The files on disk
are the offline fallback: if the portal is unreachable at boot — or the venue
wifi dies mid-demo — the engine still starts on real data.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.live_igot_adapter import LiveIgotAdapter  # noqa: E402

LIVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "live")
CATALOG_PATH   = os.path.join(LIVE_DIR, "live_catalog.json")
KCM_PATH       = os.path.join(LIVE_DIR, "live_kcm.json")
CROSSWALK_PATH = os.path.join(LIVE_DIR, "live_kcm_crosswalk.json")
MANIFEST_PATH  = os.path.join(LIVE_DIR, "MANIFEST.json")

_FRAC_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "mock-igot-server", "data", "frac_competencies.json",
)


def _write(path: str, payload) -> int:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False)
    return os.path.getsize(path)


async def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=0,
                    help="keep only the first N courses (smoke test)")
    ap.add_argument("--no-crosswalk", action="store_true",
                    help="skip the KCM→FRAC mapping (does not load the embedder)")
    ap.add_argument("--frac", default=_FRAC_PATH, help="FRAC competency set to map onto")
    args = ap.parse_args()

    os.makedirs(LIVE_DIR, exist_ok=True)
    adapter = LiveIgotAdapter()
    print(f"→ {adapter.base_url}")

    try:
        catalog, kcm = await asyncio.gather(adapter.fetch_catalog(),
                                            adapter.fetch_kcm_framework())
    finally:
        await adapter.aclose()

    if args.limit:
        catalog = catalog[:args.limit]

    tagged = sum(1 for c in catalog if c.get("competencies_v6"))
    print(f"  catalogue : {len(catalog)} courses ({tagged} carry KCM tags)")
    print(f"  KCM       : " + ", ".join(f"{k}={len(v)}" for k, v in kcm.items()))

    mapped = 0
    crosswalk = {"threshold": 0.0, "count": 0, "mappings": []}
    if not args.no_crosswalk:
        try:
            with open(args.frac, "r", encoding="utf-8") as fh:
                frac = json.load(fh)
        except OSError as exc:
            print(f"  ! FRAC set unreadable ({exc}) — skipping crosswalk", file=sys.stderr)
            frac = []
        if frac:
            from services.kcm_crosswalk import apply_crosswalk, build_crosswalk
            print("  mapping KCM themes onto FRAC competencies (loads the embedder)…")
            crosswalk = build_crosswalk(kcm.get("theme") or [], frac)
            mapping = {m["kcmRefId"]: m["fracId"] for m in crosswalk["mappings"]}
            mapped = apply_crosswalk(catalog, mapping)
            print(f"  crosswalk : {crosswalk['count']} themes mapped "
                  f"(threshold {crosswalk['threshold']}), {mapped} courses reachable by gap")

    sizes = {
        "live_catalog.json":       _write(CATALOG_PATH, catalog),
        "live_kcm.json":           _write(KCM_PATH, kcm),
        "live_kcm_crosswalk.json": _write(CROSSWALK_PATH, crosswalk),
    }
    _write(MANIFEST_PATH, {
        "source":          adapter.base_url,
        "fetchedAt":       datetime.now(timezone.utc).isoformat(),
        "synthetic":       False,
        "courses":         len(catalog),
        "coursesWithKcmTags":   tagged,
        "coursesMappedToFrac":  mapped,
        "kcmTerms":        {k: len(v) for k, v in kcm.items()},
        "crosswalkThreshold":   crosswalk["threshold"],
        "crosswalkMappings":    crosswalk["count"],
        "files":           sizes,
        "note": "Live iGOT content APIs are public and read-only. enrollment_count "
                "and completion_rate do not exist upstream and are absent here.",
    })
    for name, size in sizes.items():
        print(f"  wrote {name:26} {size/1024:8.0f} KB")
    print(f"  wrote {'MANIFEST.json':26}")
    print(f"\n✓ {LIVE_DIR}")
    print("  Set IGOT_CATALOGUE_SOURCE=live in main-lms-backend/.env to rank on it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
