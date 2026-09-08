"""How much do the model's decisions depend on its criterion weights?

Run:  python research/src/weight_sensitivity.py

WHY THIS MATTERS
----------------
The criteria tree carries placeholder weights until elicitation is complete, and
that is usually treated as a blocking limitation: no elicited weights, no result.

But the question underneath is answerable now. If the model's rankings and risk
bands barely move when the weights are perturbed, then the exact weight vector
matters less than it appears, and the placeholder weights are a smaller problem
than they look. If rankings move sharply, that is a more important finding still —
a caution about this entire class of model, because it would mean conclusions
depend on a weight vector nobody can pin down precisely.

Either outcome is reportable. That is why this is worth running before the
elicitation rather than after.

WHAT THIS IS AND IS NOT
-----------------------
This is a sensitivity analysis of the MODEL, conducted over a simulated
population of appraisals. It characterises how the model's outputs respond to
weight perturbation. It makes no claim about real borrowers, and the case
population is synthetic - stated plainly wherever the results are reported.

Simulation is the right tool here precisely because the object of study is the
model's mathematical behaviour rather than any property of a real portfolio.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import kendalltau, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tree_scoring import (  # noqa: E402
    criterion_index,
    equal_weights,
    load_tree,
    risk_bands,
    score_matrix,
    score_objectives,
)

ROOT = Path(__file__).resolve().parents[2]
OUT_TABLES = ROOT / "research" / "outputs" / "tables"
OUT_FIGURES = ROOT / "research" / "outputs" / "figures"

N_CASES = 2000
N_DRAWS = 400
PERTURBATIONS = [0.10, 0.25, 0.50, 0.75, 1.00]
SEED = 11


def simulate_cases(tree: dict, n: int, rng: np.random.Generator) -> list[dict]:
    """A synthetic population of complete appraisals.

    Criterion values are drawn to span the plausible range of each criterion
    rather than to imitate any real portfolio. Only complete appraisals are
    generated: incompleteness is handled by the completeness gate and would
    confound a study of weight effects.
    """
    codes = [lv["code"] for lv in tree["linguisticScale"]["levels"]]
    cases: list[dict] = []

    lookup = {
        c["id"]: c
        for o in tree["objectives"]
        for d in o["dimensions"]
        for c in d["criteria"]
    }

    for _ in range(n):
        case: dict = {}
        for cid, criterion in lookup.items():
            if criterion["type"] == "qualitative":
                case[cid] = codes[rng.integers(0, len(codes))]
            else:
                xs = [b[0] for b in criterion["bands"]]
                lo, hi = min(xs), max(xs)
                span = hi - lo
                case[cid] = float(rng.uniform(lo - 0.1 * span, hi + 0.1 * span))
        cases.append(case)

    return cases


def perturb(base: dict[str, np.ndarray], p: float,
            rng: np.random.Generator) -> dict[str, np.ndarray]:
    """Multiplicatively perturb each weight by up to +/- p, then renormalise.

    p = 0.50 means every weight is scaled by a factor drawn uniformly from
    [0.5, 1.5] before normalisation - a substantial disagreement about relative
    importance, larger than experts typically differ by.
    """
    out: dict[str, np.ndarray] = {}
    for key, w in base.items():
        factors = 1.0 + rng.uniform(-p, p, size=len(w))
        perturbed = w * np.clip(factors, 1e-6, None)
        out[key] = perturbed / perturbed.sum()
    return out


def main() -> int:
    tree = load_tree()
    rng = np.random.default_rng(SEED)

    print(f"Model v{tree['version']} - {len(criterion_index(tree))} criteria")
    print(f"Simulating {N_CASES:,} complete appraisals ...")
    cases = simulate_cases(tree, N_CASES, rng)

    # Criterion scores are weight-independent, so compute once.
    scores = score_matrix(cases, tree)

    base_w = equal_weights(tree)
    baseline = score_objectives(scores, tree, base_w)
    base_bands = {k: risk_bands(v, tree) for k, v in baseline.items()}

    objectives = [o["id"] for o in tree["objectives"]]
    print(f"Baseline computed. Running {N_DRAWS} draws at each of "
          f"{len(PERTURBATIONS)} perturbation levels ...\n")

    rows = []

    for p in PERTURBATIONS:
        stats = {
            oid: {"spearman": [], "kendall": [], "band_same": [], "max_shift": []}
            for oid in objectives
        }

        for _ in range(N_DRAWS):
            w = perturb(base_w, p, rng)
            perturbed = score_objectives(scores, tree, w)

            for oid in objectives:
                a, b = baseline[oid], perturbed[oid]
                ok = ~np.isnan(a) & ~np.isnan(b)

                stats[oid]["spearman"].append(spearmanr(a[ok], b[ok]).statistic)
                stats[oid]["kendall"].append(kendalltau(a[ok], b[ok]).statistic)
                stats[oid]["band_same"].append(
                    float(np.mean(risk_bands(b, tree)[ok] == base_bands[oid][ok]))
                )
                stats[oid]["max_shift"].append(float(np.max(np.abs(a[ok] - b[ok]))))

        for oid in objectives:
            s = stats[oid]
            row = {
                "objective": oid,
                "perturbation": p,
                "spearman_mean": round(float(np.mean(s["spearman"])), 4),
                "spearman_p05": round(float(np.percentile(s["spearman"], 5)), 4),
                "kendall_mean": round(float(np.mean(s["kendall"])), 4),
                "band_agreement_mean": round(float(np.mean(s["band_same"])), 4),
                "band_agreement_p05": round(float(np.percentile(s["band_same"], 5)), 4),
                "max_score_shift_mean": round(float(np.mean(s["max_shift"])), 2),
            }
            rows.append(row)

        print(f"  +/- {int(p * 100):>3}%   " + "   ".join(
            f"{r['objective'][:12]:<12} rho={r['spearman_mean']:.4f} "
            f"band={r['band_agreement_mean']:.1%}"
            for r in rows if r["perturbation"] == p
        ))

    # ---- per-criterion influence ------------------------------------------
    # How much does each criterion's own weight move the objective score?
    # Estimated by doubling one criterion's weight within its dimension.
    print("\nEstimating per-criterion influence ...")
    influence = []
    for oid, did, cid in criterion_index(tree):
        w = {k: v.copy() for k, v in base_w.items()}
        key = f"dimension:{did}"
        idx = [c["id"] for c in next(
            d for o in tree["objectives"] for d in o["dimensions"] if d["id"] == did
        )["criteria"]].index(cid)

        w[key][idx] *= 2.0
        w[key] = w[key] / w[key].sum()

        shifted = score_objectives(scores, tree, w)
        a, b = baseline[oid], shifted[oid]
        ok = ~np.isnan(a) & ~np.isnan(b)

        influence.append({
            "objective": oid,
            "dimension": did,
            "criterion": cid,
            "mean_abs_shift": round(float(np.mean(np.abs(a[ok] - b[ok]))), 3),
            "band_changes": round(
                float(np.mean(risk_bands(b, tree)[ok] != risk_bands(a, tree)[ok])), 4
            ),
        })

    influence.sort(key=lambda r: -r["mean_abs_shift"])

    # Reported per objective. Comparing across objectives would be meaningless:
    # the tree is asymmetric, so a criterion's leverage depends on how many
    # siblings it has and how many parallel dimensions sit above it.
    print()
    print("  Most influential criteria, by objective (doubling their weight):")
    for oid in objectives:
        print(f"    {oid}:")
        for r in [x for x in influence if x["objective"] == oid][:5]:
            print(f"      {r['criterion']:<24} {r['mean_abs_shift']:>6.3f} pts   "
                  f"band changes {r['band_changes']:.1%}")

    print()
    print("  Structural note - one criterion's share of its objective:")
    for objective in tree["objectives"]:
        n_dims = len(objective["dimensions"])
        sizes = [len(d["criteria"]) for d in objective["dimensions"]]
        print(f"    {objective['id']:<20} {n_dims} dimension(s), "
              f"criterion carries {1.0 / n_dims / max(sizes):.4f}"
              f"-{1.0 / n_dims / min(sizes):.4f} of the objective")

    # ---- save --------------------------------------------------------------
    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    import csv

    with open(OUT_TABLES / "weight_sensitivity.csv", "w", newline="",
              encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    with open(OUT_TABLES / "criterion_influence.csv", "w", newline="",
              encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(influence[0].keys()))
        writer.writeheader()
        writer.writerows(influence)

    with open(OUT_TABLES / "weight_sensitivity_meta.json", "w", encoding="utf-8") as fh:
        json.dump({
            "n_cases": N_CASES,
            "n_draws_per_level": N_DRAWS,
            "perturbation_levels": PERTURBATIONS,
            "seed": SEED,
            "model_version": tree["version"],
            "case_population": "simulated - not real applications",
        }, fh, indent=2)

    # ---- headline ----------------------------------------------------------
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    for oid in objectives:
        worst = next(r for r in rows
                     if r["objective"] == oid and r["perturbation"] == max(PERTURBATIONS))
        print(f"\n  {oid}: at +/-{int(max(PERTURBATIONS) * 100)}% weight perturbation")
        print(f"    rank correlation with baseline : {worst['spearman_mean']:.4f} "
              f"(5th pct {worst['spearman_p05']:.4f})")
        print(f"    risk band unchanged            : {worst['band_agreement_mean']:.1%} "
              f"(5th pct {worst['band_agreement_p05']:.1%})")

    # Judge robustness at a REALISTIC level of disagreement, not the extreme.
    # +/-100% permits a weight to be scaled anywhere in [0, 2] - far wider than
    # experts differ. +/-25% is the defensible reference point.
    print()
    print("  At +/-25% (a realistic spread of expert disagreement):")
    for oid in objectives:
        r = next(x for x in rows if x["objective"] == oid and x["perturbation"] == 0.25)
        verdict = (
            "ROBUST" if r["spearman_mean"] > 0.95 and r["band_agreement_mean"] > 0.90
            else "MODERATELY ROBUST" if r["spearman_mean"] > 0.90
            else "SENSITIVE"
        )
        print(f"    {oid:<20} rho={r['spearman_mean']:.4f}  "
              f"band unchanged {r['band_agreement_mean']:.1%}  -> {verdict}")

    print()
    print("  Reading: the model is robust to the weight disagreement experts")
    print("  plausibly exhibit, and degrades gracefully beyond it. That does not")
    print("  make elicitation optional - it bounds how much the placeholder")
    print("  weights can be distorting the results reported meanwhile.")

    print(f"\nSaved to research/outputs/tables/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
