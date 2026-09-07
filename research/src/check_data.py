"""Verify which datasets have been downloaded and profile what is present.

Run:  python research/src/check_data.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"

EXPECTED = {
    "SBAnational.csv": {
        "label": "SBA National (PRIMARY)",
        "required": True,
        "min_mb": 50,
        "target": "MIS_Status",
    },
    "german.data": {
        "label": "Statlog German Credit (benchmark)",
        "required": False,
        "min_mb": 0,
        "target": "column 21",
    },
    "wbes_srilanka.csv": {
        "label": "World Bank Enterprise Survey - Sri Lanka (context)",
        "required": False,
        "min_mb": 0,
        "target": None,
    },
}


def human_mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024)


def profile_sba(path: Path) -> None:
    import pandas as pd

    print("    profiling (reading first 200k rows)...")
    df = pd.read_csv(path, nrows=200_000, low_memory=False)
    print(f"    columns ({len(df.columns)}): {', '.join(df.columns[:12])} ...")

    if "MIS_Status" in df.columns:
        counts = df["MIS_Status"].value_counts(dropna=False)
        print("    MIS_Status distribution in sample:")
        for value, n in counts.items():
            print(f"        {str(value):12s} {n:>8,}  ({n / len(df):.1%})")
    else:
        print("    !! MIS_Status column not found - wrong file?")

    for col in ("CreateJob", "RetainedJob"):
        if col in df.columns:
            print(f"    {col}: present (development-impact proxy)")


def main() -> int:
    print(f"Looking in: {RAW}\n")
    RAW.mkdir(parents=True, exist_ok=True)

    missing_required = []

    for name, meta in EXPECTED.items():
        path = RAW / name
        tag = "REQUIRED" if meta["required"] else "optional"

        if not path.exists():
            print(f"[ MISSING ] {name}  ({tag}) - {meta['label']}")
            if meta["required"]:
                missing_required.append(name)
            continue

        size = human_mb(path)
        print(f"[ OK      ] {name}  ({size:.1f} MB) - {meta['label']}")

        if size < meta["min_mb"]:
            print(f"    !! expected at least {meta['min_mb']} MB - file may be truncated")

        if name == "SBAnational.csv":
            try:
                profile_sba(path)
            except Exception as exc:  # noqa: BLE001
                print(f"    !! could not profile: {exc}")

    print()
    if missing_required:
        print("Required datasets still missing: " + ", ".join(missing_required))
        print("See research/data/DATASETS.md for where to get them.")
        return 1

    print("All required datasets present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
