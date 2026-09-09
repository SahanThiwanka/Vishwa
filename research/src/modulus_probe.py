"""Is twelve special, or would any modulus look like this?

Run:  python research/src/modulus_probe.py

WHY THIS EXISTS
---------------
The contamination finding rests on a single boolean - "is `Term` an exact
multiple of twelve" - reaching AUC ~0.89 with no economic content. The obvious
reviewer question is whether twelve is doing any work at all. If "multiple of
two" or "multiple of five" discriminated just as well, the finding would not be
about round contractual terms; it would be about something else entirely, and the
interpretation in Chapter 5 would be wrong.

The strata overlap by construction - every multiple of twelve is also a multiple
of six, four, three and two - so a raw sweep across moduli cannot be read
naively. Two things are therefore reported:

  raw AUC          discrimination of "Term mod m == 0" on its own
  residual AUC     the same, computed only WITHIN the loans that are already
                   multiples of twelve or already not, which removes the part of
                   m's performance that is inherited from twelve

A modulus that only looks good because it contains the multiples of twelve has
raw discrimination and no residual discrimination. A modulus carrying independent
signal has both.

The prediction, if the finding is what Chapter 5 says it is: the year-multiples
(12, 24, 36, 60) lead on raw AUC, and nothing has meaningful residual AUC once
twelve is held fixed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "research" / "data" / "processed" / "sba_clean.parquet"
OUT_TABLES = ROOT / "research" / "outputs" / "tables"

COHORT_MIN, COHORT_MAX = 1990, 2010
DATA_CUTOFF_YEAR = 2014

MODULI = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 18, 20, 24, 30, 36, 48, 60]

# A stratum needs enough of both outcomes before a within-stratum AUC means
# anything.
MIN_STRATUM = 1000
MIN_MINORITY = 50


def auc_of(flag: np.ndarray, y: np.ndarray) -> float | None:
    """AUC of a boolean predictor. Irregular = higher risk, so flag is negated."""
    if len(y) < MIN_STRATUM:
        return None
    if min(int(y.sum()), int((1 - y).sum())) < MIN_MINORITY:
        return None
    if flag.min() == flag.max():
        return None
    # flag is "is a multiple of m"; multiples repay more, so risk is NOT flag.
    return float(roc_auc_score(y, (~flag.astype(bool)).astype(float)))


def main() -> int:
    if not PROCESSED.exists():
        print(f"Missing {PROCESSED}. Run prepare_sba.py first.")
        return 1

    df = pd.read_parquet(PROCESSED)
    df = df[df["ApprovalFY"].between(COHORT_MIN, COHORT_MAX)]
    df = df[(df["ApprovalFY"] + df["term_years"]) <= DATA_CUTOFF_YEAR]
    df = df[df["Term"] > 0]

    term = df["Term"].to_numpy()
    y = df["default"].to_numpy()
    round12 = (term % 12 == 0)

    print(f"Matured facilities with a positive term: {len(df):,}")
    print(f"Multiples of twelve: {round12.mean():.2%}\n")

    print(f"  {'m':>4} {'share ≡0':>10} {'raw AUC':>9} "
          f"{'residual: within mult of 12':>28} {'within not':>11}")
    print(f"  {'-' * 4} {'-' * 10} {'-' * 9} {'-' * 28} {'-' * 11}")

    rows = []
    for m in MODULI:
        flag = (term % m == 0)
        raw = auc_of(flag, y)

        # Residual discrimination, holding multiple-of-twelve status fixed.
        inside = auc_of(flag[round12], y[round12])
        outside = auc_of(flag[~round12], y[~round12])

        rows.append({
            "modulus": m,
            "share_zero_residue": round(float(flag.mean()), 6),
            "raw_auc": round(raw, 4) if raw is not None else None,
            "auc_within_multiples_of_12": round(inside, 4)
            if inside is not None else None,
            "auc_within_non_multiples_of_12": round(outside, 4)
            if outside is not None else None,
        })
        fmt = lambda v: f"{v:.4f}" if v is not None else "       -"
        marker = "  <-- year" if m % 12 == 0 else ""
        print(f"  {m:>4} {flag.mean():>9.2%} {fmt(raw):>9} "
              f"{fmt(inside):>28} {fmt(outside):>11}{marker}")

    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT_TABLES / "modulus_probe.csv", index=False)

    year_multiples = frame[frame["modulus"] % 12 == 0]["raw_auc"].dropna()
    others = frame[frame["modulus"] % 12 != 0]["raw_auc"].dropna()
    residual = pd.concat([
        frame["auc_within_multiples_of_12"].dropna(),
        frame["auc_within_non_multiples_of_12"].dropna(),
    ])

    print("\n" + "=" * 78)
    print("READING")
    print("=" * 78)
    print(f"  best raw AUC among multiples of twelve : {year_multiples.max():.4f}")
    print(f"  best raw AUC among all other moduli    : {others.max():.4f}")
    print(f"  largest residual AUC, twelve held fixed: {residual.max():.4f}")
    print("\n  A residual near 0.5 means the modulus carries nothing once")
    print("  multiple-of-twelve status is known - i.e. twelve is the signal and")
    print("  the rest is inherited from it.")

    summary = {
        "n": int(len(df)),
        "share_multiple_of_12": round(float(round12.mean()), 6),
        "best_raw_auc_year_multiples": round(float(year_multiples.max()), 4),
        "best_raw_auc_other_moduli": round(float(others.max()), 4),
        "max_residual_auc": round(float(residual.max()), 4),
        "moduli_tested": MODULI,
    }
    (OUT_TABLES / "modulus_probe.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nSaved modulus_probe.csv and modulus_probe.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
