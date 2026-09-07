"""Benchmark the unfitted expert scorecard against trained credit-scoring models.

Run:  python research/src/benchmark.py

The comparison that matters for RQ3:

    The scorecard NEVER SEES A DEFAULT LABEL. Its bands were set from a priori
    credit reasoning. The logistic regression and gradient booster are trained on
    hundreds of thousands of labelled outcomes.

So the question is not "does the scorecard win" - it will not. The question is how
much discrimination an unfitted, fully explainable, expert-structured model
retains relative to the trained ceiling. That ratio is the finding, and it is the
one that matters for banks with no clean historical default data, which is the
common situation in Sri Lankan SME lending.

Two validation protocols are reported:
  * random split   - what most published work on this dataset does
  * temporal split - train on earlier cohorts, test on later ones

The gap between them is itself reported, because random splits leak future
information through shared economic cycles and overstate performance.
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
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fuzzy_scorecard import add_scorecard_columns  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "research" / "data" / "processed" / "sba_clean.parquet"
OUT_TABLES = ROOT / "research" / "outputs" / "tables"

# Cohort window. Pre-1990 volumes are tiny and erratic; post-2010 approvals are
# right-censored (a 2013 loan on a 15-year term cannot have defaulted by the 2014
# data cut-off, so it looks artificially good).
COHORT_MIN, COHORT_MAX = 1990, 2010

# Restrict to loans whose FULL TERM elapsed before the 2014 data cut-off.
#
# Why this matters - a finding in its own right:
#   Without this filter, gradient boosting reaches AUC 0.9725. That is not credit
#   discrimination. No single feature leaks (highest univariate AUC is term at
#   0.82), but the booster reconstructs loan vintage from feature interactions
#   (facility size tracks inflation; the LowDoc programme ran only in certain
#   years) and combines it with term to infer "this loan has not yet had time to
#   default". Censored loans default at 7.8% versus 20.4% for matured ones, so
#   that inference is worth an enormous amount of apparent accuracy.
#
#   Set to False to reproduce the inflated figure for the thesis comparison.
MATURED_ONLY = True
DATA_CUTOFF_YEAR = 2014

# Temporal split boundary: train on approvals up to and including this year.
TEMPORAL_BOUNDARY = 2003

# CLEAN specification. Term and every feature derived from it are excluded,
# because leakage_analysis.py shows the field carries outcome information
# (roundness alone predicts default at AUC ~0.89 within every approval year).
# This costs genuine predictive power - part of the term signal is economic -
# but the contaminated and legitimate components cannot be separated.
CLEAN_FEATURES = [
    "sba_guarantee_share", "disbursement_ratio", "is_new_business", "is_urban",
    "has_franchise", "rev_line_of_credit", "low_doc_program", "NoEmp",
    "CreateJob", "RetainedJob", "GrAppv", "loan_per_employee", "jobs_per_100k",
    "naics_sector_code",
]

# CONTAMINATED specification, reported ONLY to quantify how much the leak
# inflates results. Never present these as the study's performance.
CONTAMINATED_FEATURES = CLEAN_FEATURES + ["term_years", "real_estate_backed"]


def ks_statistic(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """Kolmogorov-Smirnov separation - standard in credit scoring practice."""
    fpr, tpr, _ = roc_curve(y_true, y_score)
    return float(np.max(tpr - fpr))


def evaluate(name: str, y_true: np.ndarray, y_score: np.ndarray,
             fitted: bool) -> dict:
    """Compute the metric set. `y_score` is P(default) or a monotone proxy."""
    auc = roc_auc_score(y_true, y_score)
    ks = ks_statistic(y_true, y_score)
    ap = average_precision_score(y_true, y_score)

    # Brier only means anything for a calibrated probability.
    if y_score.min() >= 0 and y_score.max() <= 1:
        brier = brier_score_loss(y_true, y_score)
    else:
        brier = float("nan")

    # F1 at the threshold maximising Youden's J.
    fpr, tpr, thresholds = roc_curve(y_true, y_score)
    best = thresholds[np.argmax(tpr - fpr)]
    f1 = f1_score(y_true, (y_score >= best).astype(int))

    return {
        "model": name,
        "fitted_on_outcomes": fitted,
        "auc": round(float(auc), 4),
        "ks": round(float(ks), 4),
        "avg_precision": round(float(ap), 4),
        "brier": round(float(brier), 4) if brier == brier else None,
        "f1_at_youden": round(float(f1), 4),
    }


def run_protocol(df: pd.DataFrame, protocol: str,
                 features: list[str], spec: str) -> list[dict]:
    if protocol == "temporal":
        train = df[df["ApprovalFY"] <= TEMPORAL_BOUNDARY]
        test = df[df["ApprovalFY"] > TEMPORAL_BOUNDARY]
    else:
        rng = np.random.default_rng(42)
        mask = rng.random(len(df)) < 0.7
        train, test = df[mask], df[~mask]

    print(f"\n{'=' * 72}")
    print(f"SPEC: {spec}   PROTOCOL: {protocol}")
    print(f"{'=' * 72}")
    print(f"  train n={len(train):>8,}  default={train['default'].mean():.2%}")
    print(f"  test  n={len(test):>8,}  default={test['default'].mean():.2%}")
    if protocol == "temporal":
        print(f"  train years {train['ApprovalFY'].min():.0f}-{train['ApprovalFY'].max():.0f}"
              f" | test years {test['ApprovalFY'].min():.0f}-{test['ApprovalFY'].max():.0f}")

    y_train = train["default"].to_numpy()
    y_test = test["default"].to_numpy()
    X_train = train[features]
    X_test = test[features]

    results = []

    # --- 1. Expert scorecard: UNFITTED -------------------------------------
    # High score = low risk, so negate to make it a risk ranking.
    scorecard_risk = -test["scorecard_credit_risk"].to_numpy()
    valid = ~np.isnan(scorecard_risk)
    results.append(
        evaluate("Expert scorecard (unfitted)", y_test[valid],
                 scorecard_risk[valid], fitted=False)
    )

    # --- 2. Logistic regression --------------------------------------------
    logit = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000)),
    ])
    logit.fit(X_train, y_train)
    results.append(
        evaluate("Logistic regression", y_test,
                 logit.predict_proba(X_test)[:, 1], fitted=True)
    )

    # --- 3. Gradient boosting ----------------------------------------------
    gbm = HistGradientBoostingClassifier(
        max_iter=300, learning_rate=0.1, max_depth=6, random_state=42
    )
    gbm.fit(X_train, y_train)
    results.append(
        evaluate("Gradient boosting", y_test,
                 gbm.predict_proba(X_test)[:, 1], fitted=True)
    )

    # --- 4. Leakage probe ---------------------------------------------------
    # A single boolean - "is the term a multiple of 12" - carries no economic
    # meaning whatsoever. Whatever AUC it achieves is pure contamination, and it
    # is the yardstick for how much the contaminated spec is inflated by.
    if spec == "contaminated":
        roundness = ((test["Term"] % 12 != 0) | (test["Term"] <= 0)).astype(float)
        results.append(
            evaluate("Term-roundness probe (LEAKAGE)", y_test,
                     roundness.to_numpy(), fitted=False)
        )

    for r in results:
        r["protocol"] = protocol
        r["spec"] = spec

    print()
    print(f"  {'model':<34} {'AUC':>7} {'KS':>7} {'AP':>7} {'F1':>7}  fitted")
    print(f"  {'-' * 34} {'-' * 7} {'-' * 7} {'-' * 7} {'-' * 7}  ------")
    for r in results:
        print(f"  {r['model']:<34} {r['auc']:>7.4f} {r['ks']:>7.4f} "
              f"{r['avg_precision']:>7.4f} {r['f1_at_youden']:>7.4f}  "
              f"{'yes' if r['fitted_on_outcomes'] else 'NO'}")

    return results


def main() -> int:
    if not PROCESSED.exists():
        print(f"Missing {PROCESSED}. Run prepare_sba.py first.")
        return 1

    df = pd.read_parquet(PROCESSED)
    print(f"Loaded {len(df):,} rows")

    df = df[df["ApprovalFY"].between(COHORT_MIN, COHORT_MAX)].copy()
    print(f"Cohort {COHORT_MIN}-{COHORT_MAX}: {len(df):,} rows, "
          f"default rate {df['default'].mean():.2%}")

    if MATURED_ONLY:
        matures_by = df["ApprovalFY"] + df["term_years"]
        censored = matures_by > DATA_CUTOFF_YEAR
        print(f"\nRight-censoring control:")
        print(f"  censored (term not yet elapsed) n={censored.sum():>7,} "
              f"default={df.loc[censored, 'default'].mean():.2%}")
        print(f"  fully matured                   n={(~censored).sum():>7,} "
              f"default={df.loc[~censored, 'default'].mean():.2%}")
        df = df[~censored].copy()
        print(f"  -> analysing {len(df):,} fully-matured loans only")

    df = add_scorecard_columns(df)
    coverage = df["scorecard_credit_risk"].notna().mean()
    print(f"Scorecard computed for {coverage:.1%} of rows")

    all_results = []
    for spec, features in (("clean", CLEAN_FEATURES),
                           ("contaminated", CONTAMINATED_FEATURES)):
        for protocol in ("random", "temporal"):
            all_results.extend(run_protocol(df, protocol, features, spec))

    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    table = pd.DataFrame(all_results)[
        ["spec", "protocol", "model", "fitted_on_outcomes", "auc", "ks",
         "avg_precision", "brier", "f1_at_youden"]
    ]
    table.to_csv(OUT_TABLES / "benchmark_results.csv", index=False)

    with open(OUT_TABLES / "benchmark_results.json", "w", encoding="utf-8") as fh:
        json.dump({
            "cohort": [COHORT_MIN, COHORT_MAX],
            "temporal_boundary": TEMPORAL_BOUNDARY,
            "n_rows": int(len(df)),
            "default_rate": round(float(df["default"].mean()), 4),
            "results": all_results,
        }, fh, indent=2)

    # --- the headline comparison -------------------------------------------
    print(f"\n{'=' * 72}\nRETENTION ANALYSIS (RQ3)\n{'=' * 72}")
    for protocol in ("random", "temporal"):
        rows = [r for r in all_results
                if r["protocol"] == protocol and r["spec"] == "clean"]
        card = next(r for r in rows if r["model"].startswith("Expert"))
        best = max((r for r in rows if r["fitted_on_outcomes"]),
                   key=lambda r: r["auc"])

        # Discrimination above chance, scorecard as a share of the trained best.
        retention = (card["auc"] - 0.5) / (best["auc"] - 0.5)
        print(f"\n  {protocol}:")
        print(f"    unfitted scorecard AUC     {card['auc']:.4f}")
        print(f"    best trained model AUC     {best['auc']:.4f}  ({best['model']})")
        print(f"    discrimination retained    {retention:.1%}")

    rand = next(r for r in all_results
                if r["protocol"] == "random" and r["model"] == "Gradient boosting")
    temp = next(r for r in all_results
                if r["protocol"] == "temporal" and r["model"] == "Gradient boosting")
    print(f"\n  Optimism from random splitting (gradient boosting):")
    print(f"    random {rand['auc']:.4f} - temporal {temp['auc']:.4f} "
          f"= {rand['auc'] - temp['auc']:+.4f} AUC")

    print(f"\nSaved {(OUT_TABLES / 'benchmark_results.csv').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
