"""
seed_data.py — superseded.

All mock data now comes from ONE deterministic generator:

    python generate_mock_data.py

This shim is kept so old instructions ("python seed_data.py") still produce
the same, reproducible data instead of the previous Faker/now()-based output.
"""
import sys

from generate_mock_data import main

if __name__ == "__main__":
    sys.exit(main())
