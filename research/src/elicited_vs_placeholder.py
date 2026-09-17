"""Did scoring on placeholder weights distort anything?

Run:  python research/src/elicited_vs_placeholder.py

THE QUESTION
------------
Every scored result in this study was produced with equal weights inside each
level, flagged PLACEHOLDER, while elicitation was outstanding. §5.16 argued that
this mattered less than it looked, on the strength of a simulation: perturb the
weights by up to ±25% and the rankings barely move.

Elicitation has since been completed with ten practitioners, so the argument no
longer has to rest on a simulation. The placeholder vector and the elicited
vector both exist, and the same cases can be scored under each.

This matters because **the elicited weights fall outside the range §5.16
tested.** Within a level the ratio of largest to smallest elicited weight
reaches 3.25, and the extreme weights depart from equal by far more than 25%.
The earlier reassurance was therefore about a narrower perturbation than the one
that actually occurred, and saying so is the honest reading whichever way the
comparison comes out.

WHAT IT REPORTS
---------------
Spearman correlation between the two rankings, the share of cases keeping their
risk band, and the share moving two bands or more - the same measures §5.16
used, so the two are directly comparable.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tree_scoring import (  # noqa: E402
    equal_weights,
    load_tree,
    risk_bands,
    score_matrix,
    score_objectives,
)
from weight_sensitivity import simulate_cases  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT_TABLES = ROOT / "research" / "outputs" / "tables"

N_CASES = 2000
SEED = 42


def tree_weights(tree: dict) -> dict[str, np.ndarray]:
    """The weights actually stored in the tree, whatever they are.

    After `derive_weights.py --apply` these are the elicited ones. Falls back to
    equal for any level the tree does not carry a weight for, so the comparison
    degrades to identity rather than failing.
    """
    weights: dict[str, np.ndarray] = {}
    for objective in tree["objectives"]:
        dims = objective["dimensions"]
        raw = np.array([float(d.get("weight") or 0.0) for d in dims])
        weights[f"objective:{objective['id']}"] = (
            raw / raw.sum() if raw.sum() > 0 else np.full(len(dims), 1 / len(dims))
        )
        for dim in dims:
            crits = dim["criteria"]
            raw = np.array([float(c.get("weight") or 0.0) for c in crits])
            weights[f"dimension:{dim['id']}"] = (
                raw / raw.sum() if raw.sum() > 0
                else np.full(len(crits), 1 / len(crits))
            )
    return weights


def main() -> int:
    tree = load_tree()
    status = tree.get("weightStatus", {}).get("state")
    if status != "ELICITED":
        print(f"weightStatus is {status}, not ELICITED. Nothing to compare: "
              "run derive_weights.py --apply first.")
        return 1

    rng = np.random.default_rng(SEED)
    cases = simulate_cases(tree, N_CASES, rng)
    matrix = score_matrix(cases, tree)

    placeholder = equal_weights(tree)
    elicited = tree_weights(tree)

    # How far apart are the two weight vectors themselves?
    spreads = []
    for level, w in elicited.items():
        eq = placeholder[level]
        spreads.append({
            "level": level,
            "n": len(w),
            "max_over_min": round(float(w.max() / w.min()), 4),
            "max_departure_from_equal": round(float(np.abs(w - eq).max()), 4),
            "max_relative_departure": round(float(np.abs(w / eq - 1).max()), 4),
        })

    worst = max(spreads, key=lambda s: s["max_relative_departure"])
    print(f"Elicited weights against equal weighting")
    print("=" * 70)
    print(f"  levels compared                {len(spreads)}")
    print(f"  largest within-level ratio     "
          f"{max(s['max_over_min'] for s in spreads):.2f}x")
    print(f"  largest relative departure     "
          f"{worst['max_relative_departure'] * 100:.0f}%  ({worst['level']})")
    print(f"  §5.16 tested perturbations up to 25%.")

    findings = {
        "n_cases": N_CASES,
        "n_respondents": tree["weightStatus"]["elicitation"]["respondents"],
        "level_spreads": spreads,
        "largest_within_level_ratio": max(s["max_over_min"] for s in spreads),
        "largest_relative_departure": worst["max_relative_departure"],
        "objectives": {},
    }

    print(f"\nScoring {N_CASES:,} simulated appraisals under each vector")
    print("=" * 70)
    print(f"  {'objective':<22} {'Spearman':>9} {'same band':>11} "
          f"{'2+ bands':>10} {'mean shift':>11}")
    print(f"  {'-' * 22} {'-' * 9} {'-' * 11} {'-' * 10} {'-' * 11}")

    for objective in tree["objectives"]:
        oid = objective["id"]
        base = score_objectives(matrix, tree, placeholder)[oid]
        new = score_objectives(matrix, tree, elicited)[oid]

        rho = float(spearmanr(base, new).statistic)
        b0 = risk_bands(base, tree)
        b1 = risk_bands(new, tree)
        same = float((b0 == b1).mean())

        order = {c: i for i, c in enumerate(["A", "B", "C", "D"])}
        d0 = np.array([order.get(str(b), -1) for b in b0])
        d1 = np.array([order.get(str(b), -1) for b in b1])
        valid = (d0 >= 0) & (d1 >= 0)
        two_plus = float((np.abs(d0 - d1)[valid] >= 2).mean())
        shift = float(np.abs(new - base).mean())

        findings["objectives"][oid] = {
            "spearman": round(rho, 4),
            "same_band": round(same, 4),
            "two_or_more_bands": round(two_plus, 4),
            "mean_absolute_score_shift": round(shift, 4),
        }
        print(f"  {oid:<22} {rho:>9.4f} {same:>10.1%} {two_plus:>9.1%} "
              f"{shift:>11.2f}")

    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    (OUT_TABLES / "elicited_vs_placeholder.json").write_text(
        json.dumps(findings, indent=2), encoding="utf-8")

    print("\n" + "=" * 70)
    print("READING")
    print("=" * 70)
    print("  This is not a simulation of possible weights. It is the actual")
    print("  placeholder vector against the actual elicited one, on the same")
    print("  cases, so it says directly what scoring on placeholders cost.")
    print("\nSaved elicited_vs_placeholder.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
