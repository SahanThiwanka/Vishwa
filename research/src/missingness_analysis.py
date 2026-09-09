"""What a credit model does with information the applicant did not supply.

Run:  python research/src/missingness_analysis.py

WHERE THIS CAME FROM
--------------------
The fairness analysis found that applicants whose rurality was not recorded were
declined at 72% against 21% for urban and 14% for rural firms, despite a default
rate slightly BELOW the urban group's. The obvious reading - "the model punishes
missing data" - turned out to be wrong, and the way it was wrong is the finding.

That group is confounded. Its records are mostly 2004 approvals, carry a much
higher SBA guarantee share (0.83 against 0.58), are larger, and are missing
several other fields as well. Their decline rate is explained by those features,
not by the absence of the rurality flag.

So the mechanism was tested directly instead, by counterfactual: take the
applicants whose records are COMPLETE, blank one field, and re-score the same
applicant. Everything else is held fixed, so whatever moves is caused by the
absence itself.

WHAT IT SHOWS
-------------
The model does not punish missing data. It rewards it. Blanking the rurality
flag drops mean predicted default from 16.8% to 6.4%, and 97.7% of applicants
are scored as LESS risky than when they answered. Withhold four fields and the
average applicant's assessed default probability roughly halves.

The reason is mundane and entirely general. A gradient booster sends missing
values down whichever branch carried more training weight; `is_urban` was absent
for about a third of the training rows, and those rows defaulted less often, so
"not stated" is scored like a low-risk population. Median imputation, used here
for the logistic regression, fails differently: it does not reward omission but
silently asserts a value the applicant never gave.

WHY IT MATTERS FOR THIS THESIS
------------------------------
Chapter 5 reports a completeness gate that refuses to return a band when too
little of an objective has been assessed. That was introduced as a safety
property after testing found a 14%-complete appraisal being handed a
recommendation. This analysis shows the alternative is not merely unsafe but
exploitable: under a single portfolio threshold, an applicant can move from
decline to approve by leaving fields blank. Refusing to answer is not
conservatism, it is the only response that cannot be gamed.
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

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "research" / "data" / "processed" / "sba_clean.parquet"
OUT_TABLES = ROOT / "research" / "outputs" / "tables"

# Same policy as the fairness analysis: decline the riskiest fifth.
DECLINE_SHARE = 0.20

# Draws per withheld-field count in the progressive experiment. The variance
# across draws is small; this is enough for a stable mean and a spread.
N_DRAWS = 30
SEED = 42


def fit_models(train: pd.DataFrame):
    y = train["default"].to_numpy()
    gbm = HistGradientBoostingClassifier(
        max_iter=300, learning_rate=0.1, max_depth=6, random_state=SEED
    )
    gbm.fit(train[CLEAN_FEATURES], y)

    logit = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000)),
    ])
    logit.fit(train[CLEAN_FEATURES], y)
    return gbm, logit


def per_field(model, name: str, X: pd.DataFrame, base: np.ndarray,
              threshold: float) -> list[dict]:
    """Blank one field at a time and measure what it does to the same applicant."""
    rows = []
    declined_base = base >= threshold

    for field in CLEAN_FEATURES:
        Xm = X.copy()
        Xm[field] = np.nan
        p = model.predict_proba(Xm)[:, 1]
        declined = p >= threshold

        rows.append({
            "model": name,
            "field_withheld": field,
            "mean_p_stated": round(float(base.mean()), 5),
            "mean_p_withheld": round(float(p.mean()), 5),
            "shift": round(float(p.mean() - base.mean()), 5),
            "share_scored_less_risky": round(float((p < base).mean()), 4),
            "share_scored_more_risky": round(float((p > base).mean()), 4),
            # The decision-level consequence: withholding flips a decline to an
            # approval for this share of applicants.
            "decline_to_approve": round(
                float((declined_base & ~declined).mean()), 5),
            "approve_to_decline": round(
                float((~declined_base & declined).mean()), 5),
        })
    return rows


def progressive(model, name: str, X: pd.DataFrame, base: np.ndarray,
                threshold: float) -> list[dict]:
    """Withhold k randomly chosen fields, for k = 1..all."""
    rng = np.random.default_rng(SEED)
    declined_base = base >= threshold
    rows = []

    for k in range(1, len(CLEAN_FEATURES) + 1):
        means, flips = [], []
        for _ in range(N_DRAWS):
            fields = rng.choice(CLEAN_FEATURES, size=k, replace=False)
            Xm = X.copy()
            for f in fields:
                Xm[f] = np.nan
            p = model.predict_proba(Xm)[:, 1]
            means.append(float(p.mean()))
            flips.append(float((declined_base & (p < threshold)).mean()))

        rows.append({
            "model": name,
            "fields_withheld": k,
            "completeness": round(1 - k / len(CLEAN_FEATURES), 4),
            "mean_p_default": round(float(np.mean(means)), 5),
            "mean_p_low": round(float(np.min(means)), 5),
            "mean_p_high": round(float(np.max(means)), 5),
            "decline_to_approve": round(float(np.mean(flips)), 5),
        })
    return rows


def main() -> int:
    if not PROCESSED.exists():
        print(f"Missing {PROCESSED}. Run prepare_sba.py first.")
        return 1

    df = pd.read_parquet(PROCESSED)
    df = df[df["ApprovalFY"].between(COHORT_MIN, COHORT_MAX)].copy()
    df = df[(df["ApprovalFY"] + df["term_years"]) <= DATA_CUTOFF_YEAR].copy()

    train = df[df["ApprovalFY"] <= TEMPORAL_BOUNDARY]
    test = df[df["ApprovalFY"] > TEMPORAL_BOUNDARY]

    gbm, logit = fit_models(train)

    # Only complete records can be used: the counterfactual is "this applicant
    # answered, then did not answer", which is meaningless if they never did.
    X_all = test[CLEAN_FEATURES]
    complete = X_all.notna().all(axis=1).to_numpy()
    X = X_all[complete].copy()

    print("Counterfactual withholding on the temporal test cohort")
    print(f"  test rows            {len(test):,}")
    print(f"  complete records     {complete.sum():,} "
          f"({complete.mean():.1%}) - the only ones this can be run on")

    all_rows: list[dict] = []
    progressive_rows: list[dict] = []
    summary: dict = {}

    for model, name in ((gbm, "Gradient boosting (native NaN)"),
                        (logit, "Logistic regression (median imputation)")):
        base = model.predict_proba(X)[:, 1]
        threshold = float(np.quantile(base, 1 - DECLINE_SHARE))

        print(f"\n{'=' * 76}")
        print(f"{name}")
        print(f"  baseline mean P(default) {base.mean():.4f} | "
              f"decline threshold {threshold:.4f}")
        print(f"{'=' * 76}")
        print(f"  {'field withheld':<24} {'mean P':>8} {'shift':>9} "
              f"{'less risky':>11} {'decline->approve':>17}")
        print(f"  {'-' * 24} {'-' * 8} {'-' * 9} {'-' * 11} {'-' * 17}")

        rows = per_field(model, name, X, base, threshold)
        for r in rows:
            print(f"  {r['field_withheld']:<24} {r['mean_p_withheld']:>8.4f} "
                  f"{r['shift']:>+9.4f} {r['share_scored_less_risky']:>10.1%} "
                  f"{r['decline_to_approve']:>16.2%}")
        all_rows.extend(rows)

        prog = progressive(model, name, X, base, threshold)
        progressive_rows.extend(prog)

        worst = max(rows, key=lambda r: r["share_scored_less_risky"])
        biggest_flip = max(rows, key=lambda r: r["decline_to_approve"])
        half = next((p for p in prog
                     if p["mean_p_default"] <= base.mean() / 2), None)

        summary[name] = {
            "baseline_mean_p": round(float(base.mean()), 5),
            "decline_threshold": round(threshold, 5),
            "fields_that_reduce_risk_when_withheld": sum(
                1 for r in rows if r["shift"] < 0),
            "field_most_rewarding_to_withhold": worst["field_withheld"],
            "share_scored_less_risky_when_withheld": worst[
                "share_scored_less_risky"],
            "field_flipping_most_decisions": biggest_flip["field_withheld"],
            "decline_to_approve_share": biggest_flip["decline_to_approve"],
            "fields_to_halve_assessed_risk": (
                half["fields_withheld"] if half else None),
        }

        print(f"\n  Withholding lowers assessed risk for "
              f"{summary[name]['fields_that_reduce_risk_when_withheld']} of "
              f"{len(CLEAN_FEATURES)} fields.")
        print(f"  Most rewarding single omission: {worst['field_withheld']} "
              f"({worst['share_scored_less_risky']:.1%} of applicants scored "
              f"less risky).")
        if half:
            print(f"  Withholding {half['fields_withheld']} of "
                  f"{len(CLEAN_FEATURES)} fields halves mean assessed risk "
                  f"(completeness {half['completeness']:.0%}).")

    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(all_rows).to_csv(
        OUT_TABLES / "missingness_per_field.csv", index=False)
    pd.DataFrame(progressive_rows).to_csv(
        OUT_TABLES / "missingness_progressive.csv", index=False)

    with open(OUT_TABLES / "missingness_summary.json", "w",
              encoding="utf-8") as fh:
        json.dump({
            "protocol": "temporal",
            "n_complete_records": int(complete.sum()),
            "decline_share": DECLINE_SHARE,
            "n_features": len(CLEAN_FEATURES),
            "draws_per_k": N_DRAWS,
            "models": summary,
        }, fh, indent=2)

    print(f"\nSaved missingness_per_field.csv, missingness_progressive.csv "
          f"and missingness_summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
