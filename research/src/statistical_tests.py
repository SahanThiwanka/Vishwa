"""Confidence intervals, significance tests, and calibration for the benchmarks.

Run:  python research/src/statistical_tests.py

WHY
---
Chapter 5 currently reports point estimates. "0.9461 versus 0.6076" is a
statement about two numbers; whether it is a statement about the world depends on
how precisely each is estimated. With 275,000 test cases the intervals will be
narrow, but that has to be shown rather than assumed - and the reader is entitled
to know that the leakage effect is not a sampling artefact.

Three things are computed:

1. **Bootstrap confidence intervals** on every AUC.
2. **DeLong's test** for paired AUC comparisons on the same test set. Paired is
   the right test here because the models are compared on identical cases, so
   treating the AUCs as independent would overstate the uncertainty.
3. **Calibration.** AUC measures ranking. A bank pricing risk needs the predicted
   probability to mean what it says, and a model can rank well while being badly
   calibrated. Reported as Brier score decomposed into reliability and
   resolution, plus a reliability curve.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from benchmark import (  # noqa: E402
    CLEAN_FEATURES,
    COHORT_MAX,
    COHORT_MIN,
    CONTAMINATED_FEATURES,
    DATA_CUTOFF_YEAR,
    TEMPORAL_BOUNDARY,
)
from fuzzy_scorecard import add_scorecard_columns  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "research" / "data" / "processed" / "sba_clean.parquet"
OUT_TABLES = ROOT / "research" / "outputs" / "tables"

N_BOOTSTRAP = 500
SEED = 23


# ---------------------------------------------------------------------------
# DeLong's test
# ---------------------------------------------------------------------------

def _midrank(x: np.ndarray) -> np.ndarray:
    """Ranks with ties averaged - the tie handling DeLong's estimator requires."""
    order = np.argsort(x)
    sorted_x = x[order]
    n = len(x)
    ranks = np.empty(n, dtype=float)

    i = 0
    while i < n:
        j = i
        while j < n - 1 and sorted_x[j + 1] == sorted_x[i]:
            j += 1
        ranks[i:j + 1] = 0.5 * (i + j) + 1
        i = j + 1

    out = np.empty(n, dtype=float)
    out[order] = ranks
    return out


def delong_test(y_true: np.ndarray, score_a: np.ndarray,
                score_b: np.ndarray) -> tuple[float, float, float]:
    """Paired DeLong test for two AUCs on the same cases.

    Returns (auc_a, auc_b, two-sided p-value).

    Implements the fast algorithm of Sun and Xu (2014) for DeLong's covariance
    estimator (DeLong, DeLong and Clarke-Pearson, 1988).
    """
    pos = y_true == 1
    neg = ~pos
    m, n = int(pos.sum()), int(neg.sum())

    scores = np.vstack([score_a, score_b])
    k = scores.shape[0]

    tx = np.empty([k, m], dtype=float)
    ty = np.empty([k, n], dtype=float)
    tz = np.empty([k, m + n], dtype=float)

    for r in range(k):
        tx[r] = _midrank(scores[r, pos])
        ty[r] = _midrank(scores[r, neg])
        tz[r] = _midrank(scores[r])

    aucs = tz[:, :m].sum(axis=1) / (m * n) - (m + 1) / (2 * n)

    v01 = (tz[:, :m] - tx) / n
    v10 = 1 - (tz[:, m:] - ty) / m

    sx = np.cov(v01)
    sy = np.cov(v10)
    cov = sx / m + sy / n
    cov = np.atleast_2d(cov)

    contrast = np.array([[1, -1]], dtype=float)
    var = float((contrast @ cov @ contrast.T).item())

    if var <= 0:
        return float(aucs[0]), float(aucs[1]), 1.0

    z = (aucs[0] - aucs[1]) / np.sqrt(var)
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return float(aucs[0]), float(aucs[1]), float(p)


def bootstrap_auc_ci(y_true: np.ndarray, y_score: np.ndarray,
                     n_boot: int = N_BOOTSTRAP,
                     seed: int = SEED) -> tuple[float, float, float]:
    """Stratified bootstrap percentile interval for an AUC.

    Resampling positives and negatives separately keeps the class balance fixed
    across replicates, so the interval reflects uncertainty in discrimination
    rather than in prevalence.
    """
    rng = np.random.default_rng(seed)
    pos_idx = np.flatnonzero(y_true == 1)
    neg_idx = np.flatnonzero(y_true == 0)

    point = roc_auc_score(y_true, y_score)
    draws = np.empty(n_boot, dtype=float)

    n_pos, n_neg = len(pos_idx), len(neg_idx)

    for b in range(n_boot):
        p = rng.choice(pos_idx, size=n_pos, replace=True)
        n = rng.choice(neg_idx, size=n_neg, replace=True)
        s_all = np.concatenate([y_score[p], y_score[n]])
        ranks = stats.rankdata(s_all)
        draws[b] = (ranks[:n_pos].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)

    lo, hi = np.percentile(draws, [2.5, 97.5])
    return float(point), float(lo), float(hi)


# ---------------------------------------------------------------------------
# Calibration
# ---------------------------------------------------------------------------

def calibration(y_true: np.ndarray, y_prob: np.ndarray,
                bins: int = 10) -> dict:
    """Brier score with Murphy's decomposition, plus a reliability curve.

    Brier = reliability - resolution + uncertainty.
      reliability  how far predicted probabilities sit from observed rates
                   (lower is better; 0 is perfect calibration)
      resolution   how much the model separates cases from the base rate
                   (higher is better)
      uncertainty  the base rate's own variance - a property of the data
    """
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(y_prob, edges) - 1, 0, bins - 1)

    base = float(y_true.mean())
    reliability = resolution = 0.0
    curve = []

    for b in range(bins):
        sel = idx == b
        n = int(sel.sum())
        if n == 0:
            continue
        mean_pred = float(y_prob[sel].mean())
        observed = float(y_true[sel].mean())

        reliability += n * (mean_pred - observed) ** 2
        resolution += n * (observed - base) ** 2

        curve.append({
            "bin": b,
            "n": n,
            "mean_predicted": round(mean_pred, 4),
            "observed_rate": round(observed, 4),
        })

    total = len(y_true)
    return {
        "brier": round(float(np.mean((y_prob - y_true) ** 2)), 5),
        "reliability": round(reliability / total, 5),
        "resolution": round(resolution / total, 5),
        "uncertainty": round(base * (1 - base), 5),
        "base_rate": round(base, 4),
        "curve": curve,
    }


# ---------------------------------------------------------------------------

def build(df: pd.DataFrame, features: list[str], protocol: str):
    if protocol == "temporal":
        train = df[df["ApprovalFY"] <= TEMPORAL_BOUNDARY]
        test = df[df["ApprovalFY"] > TEMPORAL_BOUNDARY]
    else:
        rng = np.random.default_rng(42)
        mask = rng.random(len(df)) < 0.7
        train, test = df[mask], df[~mask]

    y_train, y_test = train["default"].to_numpy(), test["default"].to_numpy()

    logit = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000)),
    ]).fit(train[features], y_train)

    gbm = HistGradientBoostingClassifier(
        max_iter=300, learning_rate=0.1, max_depth=6, random_state=42
    ).fit(train[features], y_train)

    return y_test, {
        "Logistic regression": logit.predict_proba(test[features])[:, 1],
        "Gradient boosting": gbm.predict_proba(test[features])[:, 1],
    }, test


def main() -> int:
    if not PROCESSED.exists():
        print("Run prepare_sba.py first.")
        return 1

    df = pd.read_parquet(PROCESSED)
    df = df[df["ApprovalFY"].between(COHORT_MIN, COHORT_MAX)]
    df = df[(df["ApprovalFY"] + df["term_years"]) <= DATA_CUTOFF_YEAR].copy()
    df = add_scorecard_columns(df)
    print(f"{len(df):,} fully-matured loans, default rate {df['default'].mean():.2%}\n")

    ci_rows, test_rows, calib_rows = [], [], []

    for protocol in ("random", "temporal"):
        print("=" * 72)
        print(f"PROTOCOL: {protocol}")
        print("=" * 72)

        y_test, clean_preds, test_df = build(df, CLEAN_FEATURES, protocol)
        _, contam_preds, _ = build(df, CONTAMINATED_FEATURES, protocol)

        preds = {f"{m} (clean)": p for m, p in clean_preds.items()}
        preds.update({f"{m} (contaminated)": p for m, p in contam_preds.items()})

        # The scorecard is unfitted; negate so a high score means low risk.
        card = -test_df["scorecard_credit_risk"].to_numpy()
        ok = ~np.isnan(card)

        print(f"\n  {'model':<36} {'AUC':>7}  {'95% CI':>18}")
        print(f"  {'-' * 36} {'-' * 7}  {'-' * 18}")

        point, lo, hi = bootstrap_auc_ci(y_test[ok], card[ok])
        print(f"  {'Expert scorecard (unfitted)':<36} {point:>7.4f}  [{lo:.4f}, {hi:.4f}]")
        ci_rows.append({"protocol": protocol, "model": "Expert scorecard (unfitted)",
                        "auc": round(point, 4), "ci_low": round(lo, 4),
                        "ci_high": round(hi, 4)})

        for name, p in preds.items():
            point, lo, hi = bootstrap_auc_ci(y_test, p)
            print(f"  {name:<36} {point:>7.4f}  [{lo:.4f}, {hi:.4f}]")
            ci_rows.append({"protocol": protocol, "model": name,
                            "auc": round(point, 4), "ci_low": round(lo, 4),
                            "ci_high": round(hi, 4)})

        # --- the comparison the thesis rests on ---
        print(f"\n  DeLong paired tests:")
        comparisons = [
            ("Gradient boosting (clean)", "Gradient boosting (contaminated)",
             "leakage effect, GBM"),
            ("Logistic regression (clean)", "Logistic regression (contaminated)",
             "leakage effect, logistic"),
            ("Gradient boosting (clean)", "Logistic regression (clean)",
             "GBM vs logistic, clean"),
        ]
        for a, b, label in comparisons:
            auc_a, auc_b, p = delong_test(y_test, preds[a], preds[b])
            sig = "p < 0.001" if p < 0.001 else f"p = {p:.4f}"
            print(f"    {label:<28} {auc_a:.4f} vs {auc_b:.4f}   {sig}")
            test_rows.append({"protocol": protocol, "comparison": label,
                              "auc_a": round(auc_a, 4), "auc_b": round(auc_b, 4),
                              "p_value": p})

        # --- calibration ---
        print(f"\n  Calibration (Brier decomposition):")
        for name in ["Gradient boosting (clean)", "Logistic regression (clean)"]:
            c = calibration(y_test, preds[name])
            print(f"    {name:<34} Brier={c['brier']:.4f}  "
                  f"reliability={c['reliability']:.5f}  resolution={c['resolution']:.5f}")
            calib_rows.append({"protocol": protocol, "model": name,
                               **{k: v for k, v in c.items() if k != "curve"}})
        print()

    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(ci_rows).to_csv(OUT_TABLES / "auc_confidence_intervals.csv", index=False)
    pd.DataFrame(test_rows).to_csv(OUT_TABLES / "delong_tests.csv", index=False)
    pd.DataFrame(calib_rows).to_csv(OUT_TABLES / "calibration.csv", index=False)

    with open(OUT_TABLES / "statistical_tests_meta.json", "w", encoding="utf-8") as fh:
        json.dump({"n_bootstrap": N_BOOTSTRAP, "seed": SEED,
                   "n_loans": int(len(df))}, fh, indent=2)

    print("Saved to research/outputs/tables/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
