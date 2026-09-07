"""Best-Worst Method weight derivation (Rezaei 2015, linear model Rezaei 2016).

Run the self-test:  python research/src/bwm.py

WHY BWM RATHER THAN AHP
-----------------------
Classical pairwise AHP needs n(n-1)/2 comparisons per level - 168 across this
criteria tree. That is about an hour per respondent, and the inconsistency that
creeps in through fatigue would make the weights worthless. BWM needs 2n-3
comparisons, bringing the instrument to 86 (~15 minutes), and it is generally
more consistent because every comparison is anchored to a fixed reference rather
than being made against a rotating partner.

THE METHOD
  1. The respondent names the MOST important criterion (best, B) and the LEAST
     important (worst, W).
  2. They rate how much more important B is than each other criterion, 1-9.
  3. They rate how much more important each criterion is than W, 1-9.
  4. Weights are the solution to a min-max programme: find w minimising the
     largest deviation xi from the stated ratios, subject to sum(w) = 1.

  The optimal xi* is the raw inconsistency. Dividing it by the consistency index
  for the stated best-to-worst value gives a consistency ratio comparable across
  respondents and level sizes.
"""

from __future__ import annotations

import sys

import numpy as np
from scipy.optimize import linprog

# Consistency index by the best-to-worst comparison value a_BW (Rezaei 2015).
CONSISTENCY_INDEX = {
    1: 0.00, 2: 0.44, 3: 1.00, 4: 1.63, 5: 2.30,
    6: 3.00, 7: 3.73, 8: 4.47, 9: 5.23,
}

# Above this, a response is treated as unreliable and reported separately rather
# than silently averaged into the group weights.
CONSISTENCY_THRESHOLD = 0.25


class BWMResult:
    def __init__(self, items, weights, xi, consistency_ratio):
        self.items = items
        self.weights = dict(zip(items, weights))
        self.xi = xi
        self.consistency_ratio = consistency_ratio

    @property
    def reliable(self) -> bool:
        return self.consistency_ratio <= CONSISTENCY_THRESHOLD

    def __repr__(self) -> str:
        ranked = sorted(self.weights.items(), key=lambda kv: -kv[1])
        top = ", ".join(f"{k}={v:.3f}" for k, v in ranked[:3])
        flag = "" if self.reliable else "  [INCONSISTENT]"
        return f"<BWM CR={self.consistency_ratio:.3f} {top}{flag}>"


def solve_bwm(
    items: list[str],
    best: str,
    worst: str,
    best_to_others: dict[str, float],
    others_to_worst: dict[str, float],
) -> BWMResult:
    """Solve the linear BWM programme for one level of the tree.

    `best_to_others[j]`  = how many times more important B is than j.
    `others_to_worst[j]` = how many times more important j is than W.
    Both use the 1-9 scale; the entry for B itself and W itself is 1.
    """
    n = len(items)
    idx = {item: i for i, item in enumerate(items)}
    b, w = idx[best], idx[worst]

    # Decision variables: [w_1 ... w_n, xi]. Objective: minimise xi.
    c = np.zeros(n + 1)
    c[-1] = 1.0

    rows: list[np.ndarray] = []

    # |w_B - a_Bj * w_j| <= xi
    for item, a in best_to_others.items():
        j = idx[item]
        if j == b:
            continue
        row = np.zeros(n + 1)
        row[b] += 1.0
        row[j] -= a
        row[-1] = -1.0
        rows.append(row.copy())
        rows.append(-row + np.eye(n + 1)[-1] * -2.0)  # negated, xi stays -1

    # |w_j - a_jW * w_W| <= xi
    for item, a in others_to_worst.items():
        j = idx[item]
        if j == w:
            continue
        row = np.zeros(n + 1)
        row[j] += 1.0
        row[w] -= a
        row[-1] = -1.0
        rows.append(row.copy())
        rows.append(-row + np.eye(n + 1)[-1] * -2.0)

    A_ub = np.vstack(rows)
    b_ub = np.zeros(len(rows))

    # Weights sum to 1.
    A_eq = np.zeros((1, n + 1))
    A_eq[0, :n] = 1.0
    b_eq = np.array([1.0])

    bounds = [(0.0, 1.0)] * n + [(0.0, None)]

    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                  bounds=bounds, method="highs")

    if not res.success:
        raise RuntimeError(f"BWM did not converge: {res.message}")

    weights = res.x[:n]
    xi = float(res.x[-1])

    a_bw = float(best_to_others.get(worst, others_to_worst.get(best, 9)))
    ci = CONSISTENCY_INDEX.get(int(round(a_bw)), 5.23)
    cr = 0.0 if ci == 0 else xi / ci

    return BWMResult(items, weights, xi, cr)


def aggregate(results: list[BWMResult], drop_inconsistent: bool = True) -> dict[str, float]:
    """Combine several respondents' weights by geometric mean, then renormalise.

    Geometric mean is the standard aggregation for ratio-scale priority vectors:
    it preserves the ratio relationships that the arithmetic mean distorts.

    Inconsistent responses are excluded by default rather than averaged in. The
    number dropped MUST be reported in the thesis - silently discarding
    respondents is how an elicitation study becomes unreproducible.
    """
    usable = [r for r in results if r.reliable] if drop_inconsistent else results
    if not usable:
        raise ValueError("no usable responses")

    items = usable[0].items
    out = {}
    for item in items:
        # Clip away exact zeros so a single zero weight cannot annihilate the mean.
        values = np.array([max(r.weights[item], 1e-9) for r in usable])
        out[item] = float(np.exp(np.mean(np.log(values))))

    total = sum(out.values())
    return {k: v / total for k, v in out.items()}


def _self_test() -> int:
    print("BWM self-test\n" + "=" * 60)

    # Rezaei's worked example: choosing a mobile phone.
    items = ["price", "quality", "brand", "design"]
    result = solve_bwm(
        items,
        best="price",
        worst="brand",
        best_to_others={"price": 1, "quality": 2, "brand": 8, "design": 4},
        others_to_worst={"price": 8, "quality": 4, "brand": 1, "design": 2},
    )

    print("Consistent example (textbook shape):")
    for k, v in sorted(result.weights.items(), key=lambda kv: -kv[1]):
        print(f"    {k:10s} {v:.4f}")
    print(f"    xi* = {result.xi:.4f}   CR = {result.consistency_ratio:.4f}")

    checks: list[tuple[str, bool]] = [
        ("weights sum to 1", abs(sum(result.weights.values()) - 1.0) < 1e-6),
        ("all weights non-negative", all(v >= -1e-9 for v in result.weights.values())),
        ("best criterion has the largest weight",
         max(result.weights, key=result.weights.get) == "price"),
        ("worst criterion has the smallest weight",
         min(result.weights, key=result.weights.get) == "brand"),
        ("ordering respects stated preference",
         result.weights["price"] > result.weights["quality"]
         > result.weights["design"] > result.weights["brand"]),
        ("consistent response flagged reliable", result.reliable),
    ]

    # A deliberately contradictory response: B is barely better than everything,
    # yet everything is hugely better than W. Should register as inconsistent.
    bad = solve_bwm(
        items,
        best="price",
        worst="brand",
        best_to_others={"price": 1, "quality": 9, "brand": 2, "design": 9},
        others_to_worst={"price": 2, "quality": 9, "brand": 1, "design": 9},
    )
    print(f"\nContradictory example: CR = {bad.consistency_ratio:.4f} "
          f"({'flagged' if not bad.reliable else 'NOT flagged'})")
    checks.append(("contradictory response flagged inconsistent", not bad.reliable))

    # Aggregation across respondents.
    group = aggregate([result, result])
    checks.append(("aggregating identical responses reproduces them",
                   abs(group["price"] - result.weights["price"]) < 1e-6))
    checks.append(("aggregate sums to 1", abs(sum(group.values()) - 1.0) < 1e-6))

    print("\n" + "=" * 60)
    failed = 0
    for label, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {label}")
        if not ok:
            failed += 1

    print(f"\n{'All checks passed.' if failed == 0 else f'{failed} FAILED.'}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(_self_test())
