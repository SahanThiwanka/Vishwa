"""What would this model be worth to a lender, and at what cut-off?

Run:  python research/src/cost_analysis.py

WHY
---
AUC weights both error types equally. A bank does not. Approving a facility that
charges off costs the loss given default on the exposure; declining a sound one
costs the margin that would have been earned. Those are not the same number, and
the ratio between them determines where the cut-off should sit.

This converts discrimination into two things a credit committee can act on:

1. The **decision threshold** implied by a given cost ratio.
2. The **expected cost per facility** at that threshold, against two baselines —
   approving everything, and declining everything.

The second matters more than it looks. A model that cannot beat "approve
everything" is worse than useless: it consumes effort and adds process while
losing money relative to doing nothing.

WHAT THE COST RATIO MEANS
    C = cost(false negative) / cost(false positive)

A false negative is an approved facility that defaults; a false positive is a
declined facility that would have performed. C = 10 says one bad approval costs
as much as ten good declines. For SME term lending, plausible values sit roughly
between 5 and 20 depending on loss given default, security cover and margin. The
range is swept rather than assumed, because the right value is a policy question
for the lender, not something this study can settle.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from benchmark import (  # noqa: E402
    CLEAN_FEATURES,
    COHORT_MAX,
    COHORT_MIN,
    DATA_CUTOFF_YEAR,
    TEMPORAL_BOUNDARY,
)
from fuzzy_scorecard import add_scorecard_columns  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "research" / "data" / "processed" / "sba_clean.parquet"
OUT_TABLES = ROOT / "research" / "outputs" / "tables"

COST_RATIOS = [2, 5, 10, 20, 50]


def expected_cost(y_true: np.ndarray, y_score: np.ndarray,
                  ratio: float) -> tuple[float, float]:
    """Minimum expected cost per case, and the threshold achieving it.

    Cost is expressed in units of one false positive, so a false negative costs
    `ratio`. Thresholds are swept over the score quantiles rather than a fixed
    grid, so the search adapts to however the model's scores are distributed.
    """
    thresholds = np.quantile(y_score, np.linspace(0.001, 0.999, 400))

    best_cost, best_threshold = np.inf, thresholds[0]
    n = len(y_true)

    for t in thresholds:
        declined = y_score >= t
        # Declined but would have performed.
        fp = int(np.sum(declined & (y_true == 0)))
        # Approved but defaulted.
        fn = int(np.sum(~declined & (y_true == 1)))

        cost = (fp + ratio * fn) / n
        if cost < best_cost:
            best_cost, best_threshold = cost, float(t)

    return float(best_cost), best_threshold


def baseline_costs(y_true: np.ndarray, ratio: float) -> tuple[float, float]:
    """Cost of approving everything, and of declining everything."""
    n = len(y_true)
    approve_all = ratio * int(np.sum(y_true == 1)) / n   # every default realised
    decline_all = int(np.sum(y_true == 0)) / n           # every good loan lost
    return approve_all, decline_all


def build(df: pd.DataFrame, protocol: str):
    if protocol == "temporal":
        train = df[df["ApprovalFY"] <= TEMPORAL_BOUNDARY]
        test = df[df["ApprovalFY"] > TEMPORAL_BOUNDARY]
    else:
        rng = np.random.default_rng(42)
        mask = rng.random(len(df)) < 0.7
        train, test = df[mask], df[~mask]

    y_train = train["default"].to_numpy()

    logit = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000)),
    ]).fit(train[CLEAN_FEATURES], y_train)

    gbm = HistGradientBoostingClassifier(
        max_iter=300, learning_rate=0.1, max_depth=6, random_state=42
    ).fit(train[CLEAN_FEATURES], y_train)

    scores = {
        "Logistic regression": logit.predict_proba(test[CLEAN_FEATURES])[:, 1],
        "Gradient boosting": gbm.predict_proba(test[CLEAN_FEATURES])[:, 1],
    }
    # Scorecard: high score means low risk, so negate for a risk ranking.
    card = -test["scorecard_credit_risk"].to_numpy()
    if not np.all(np.isnan(card)):
        scores["Expert scorecard (unfitted)"] = card

    return test["default"].to_numpy(), scores


def main() -> int:
    if not PROCESSED.exists():
        print("Run prepare_sba.py first.")
        return 1

    df = pd.read_parquet(PROCESSED)
    df = df[df["ApprovalFY"].between(COHORT_MIN, COHORT_MAX)]
    df = df[(df["ApprovalFY"] + df["term_years"]) <= DATA_CUTOFF_YEAR].copy()
    df = add_scorecard_columns(df)

    print(f"{len(df):,} fully-matured loans, default rate {df['default'].mean():.2%}")
    print("Costs are in units of one false positive (a good facility declined).\n")

    rows = []

    for protocol in ("random", "temporal"):
        y_test, scores = build(df, protocol)
        print("=" * 78)
        print(f"PROTOCOL: {protocol}   (test default rate {y_test.mean():.2%})")
        print("=" * 78)

        for ratio in COST_RATIOS:
            approve_all, decline_all = baseline_costs(y_test, ratio)
            best_baseline = min(approve_all, decline_all)
            baseline_name = ("approve all" if approve_all <= decline_all
                             else "decline all")

            print(f"\n  cost ratio {ratio}:1   "
                  f"baseline = {best_baseline:.4f} ({baseline_name})")

            for name, y_score in scores.items():
                ok = ~np.isnan(y_score)
                cost, threshold = expected_cost(y_test[ok], y_score[ok], ratio)
                saving = (best_baseline - cost) / best_baseline * 100

                # A model that cannot beat doing nothing is worse than useless.
                verdict = "" if saving > 0 else "   <-- WORSE THAN NO MODEL"
                print(f"    {name:<30} cost={cost:.4f}  "
                      f"saving={saving:>6.1f}%{verdict}")

                rows.append({
                    "protocol": protocol,
                    "cost_ratio": ratio,
                    "model": name,
                    "expected_cost": round(cost, 5),
                    "baseline_cost": round(best_baseline, 5),
                    "baseline_strategy": baseline_name,
                    "saving_pct": round(saving, 2),
                    "threshold": round(threshold, 5),
                })

    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT_TABLES / "cost_analysis.csv", index=False)
    with open(OUT_TABLES / "cost_analysis_meta.json", "w", encoding="utf-8") as fh:
        json.dump({"cost_ratios": COST_RATIOS, "n_loans": int(len(df)),
                   "unit": "one false positive"}, fh, indent=2)

    # --- the summary a credit committee would want ---------------------------
    print("\n" + "=" * 78)
    print("READING")
    print("=" * 78)
    table = pd.DataFrame(rows)
    for protocol in ("random", "temporal"):
        sub = table[table.protocol == protocol]
        worse = sub[sub.saving_pct <= 0]
        print(f"\n  {protocol}: {len(worse)} of {len(sub)} model/cost-ratio "
              f"combinations are no better than the best fixed policy")
        if len(worse):
            for _, r in worse.iterrows():
                print(f"    {r['model']:<30} at {int(r['cost_ratio'])}:1")

    print("\n  A model that cannot beat 'approve all' or 'decline all' adds")
    print("  process and cost while losing money relative to doing nothing.")
    print(f"\nSaved {(OUT_TABLES / 'cost_analysis.csv').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
