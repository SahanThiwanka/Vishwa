"""Subgroup performance and disparate-impact analysis.

Run:  python research/src/fairness_analysis.py

WHY THIS EXISTS
---------------
The model card listed "no disparate-impact analysis has been performed on any
protected characteristic" as a serious gap, and separately warned that a credit
model untested for disparate impact should not touch real applicants. This
script closes as much of that gap as the available data permits, and states
precisely how much it does not close.

WHAT THIS IS NOT
----------------
The SBA national dataset records no legally protected characteristic. There is
no race, sex, age, disability or marital-status field. Nothing here is a
protected-attribute fairness audit, and this analysis must never be described as
one.

What it does test is the set of axes along which SME credit exclusion actually
operates in development finance, all of which are present in the data:

    rurality        rural firms are the classic underserved segment
    firm size       micro-enterprises are the segment SME finance policy targets
    firm age        start-ups lack the history that scoring models reward
    sector          agriculture in particular is chronically under-lent
    facility size   small facilities carry the same fixed appraisal cost

Those are proxies for credit access, not for protected class. A model can be
clean on all of them and still discriminate unlawfully.

HOW TO READ THE OUTPUT
----------------------
Two different things get measured and they must not be conflated:

1. SELECTION-RATE DISPARITY (the four-fifths rule). Whether a group is approved
   less often. This alone is NOT evidence of unfairness here: the groups have
   genuinely different default rates, and a model that declines a higher-risk
   group more often is doing its job. Reported because regulators use it, and
   because a large disparity is worth knowing about whatever its cause.

2. ERROR-RATE DISPARITY (equal opportunity). Among borrowers who DID repay,
   what fraction would have been wrongly declined? This is the one that
   indicates a defect. If creditworthy rural firms are declined at twice the
   rate of creditworthy urban firms, the model is worse for rural firms, and no
   appeal to base rates excuses it.

Missing data is carried as its own group rather than dropped. `is_urban` is
absent for roughly a third of rows, and if the model performs worse where the
data is thin, that is itself an access finding rather than a nuisance.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import brier_score_loss, roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
from benchmark import (  # noqa: E402
    CLEAN_FEATURES,
    COHORT_MAX,
    COHORT_MIN,
    DATA_CUTOFF_YEAR,
    MATURED_ONLY,
    TEMPORAL_BOUNDARY,
)
from fuzzy_scorecard import add_scorecard_columns  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "research" / "data" / "processed" / "sba_clean.parquet"
OUT_TABLES = ROOT / "research" / "outputs" / "tables"

# Portfolio-level policy: decline the riskiest share of applicants. A single
# threshold is applied to everyone - which is what a bank actually does, and is
# exactly the condition under which disparate impact arises.
DECLINE_SHARE = 0.20

# A group needs enough cases, and enough of BOTH outcomes, before within-group
# AUC means anything. Below this the row is reported with a null AUC rather than
# a number that is really just noise.
MIN_GROUP_N = 500
MIN_MINORITY_CLASS = 30

# Bootstrap resamples for the disparity intervals. The disparity measures are
# min/max ratios across groups, which are biased and noisy, so a point estimate
# on its own is not reportable.
N_BOOT = 400
SEED = 42


def size_band(n_emp: pd.Series) -> pd.Series:
    """Employee-count bands on the conventional SME definitions."""
    return pd.cut(
        n_emp,
        bins=[-np.inf, 0, 4, 19, 99, np.inf],
        labels=["Not reported (0)", "Micro (1-4)", "Small (5-19)",
                "Medium (20-99)", "Large (100+)"],
    )


def group_definitions(df: pd.DataFrame) -> dict[str, pd.Series]:
    """The grouping variables, each with missing carried as a real category."""
    urban = df["is_urban"].map({1.0: "Urban", 0.0: "Rural"})
    urban = urban.where(df["is_urban"].notna(), "Not recorded")

    new = df["is_new_business"].map({1.0: "New business", 0.0: "Existing"})
    new = new.where(df["is_new_business"].notna(), "Not recorded")

    sector = df["naics_sector"].where(df["naics_sector"].notna(), "Not recorded")

    facility = pd.qcut(
        df["GrAppv"], q=4,
        labels=["Smallest 25%", "Lower-mid", "Upper-mid", "Largest 25%"],
    )

    return {
        "Rurality": urban.astype(str),
        "Firm size (employees)": size_band(df["NoEmp"]).astype(str),
        "Firm age": new.astype(str),
        "Sector": sector.astype(str),
        "Facility size": facility.astype(str),
    }


def group_metrics(y_true: np.ndarray, risk: np.ndarray, declined: np.ndarray,
                  is_probability: bool) -> dict:
    """Performance and error rates within one group.

    `declined` is the decision under the single portfolio-wide threshold, so the
    error rates below answer "what would this policy have done to this group".
    """
    n = len(y_true)
    positives = int(y_true.sum())
    out: dict = {
        "n": n,
        "default_rate": round(float(y_true.mean()), 4),
        "decline_rate": round(float(declined.mean()), 4),
        "auc": None,
        "brier": None,
        "mean_predicted": None,
        "calibration_gap": None,
        "fpr_good_declined": None,
        "fnr_bad_approved": None,
    }

    if n >= MIN_GROUP_N and min(positives, n - positives) >= MIN_MINORITY_CLASS:
        out["auc"] = round(float(roc_auc_score(y_true, risk)), 4)

    if is_probability:
        out["brier"] = round(float(brier_score_loss(y_true, risk)), 5)
        out["mean_predicted"] = round(float(risk.mean()), 4)
        # Positive gap = the model overstates risk for this group.
        out["calibration_gap"] = round(float(risk.mean() - y_true.mean()), 4)

    good = y_true == 0
    bad = y_true == 1
    if good.sum():
        # Creditworthy applicants this policy would have turned away.
        out["fpr_good_declined"] = round(float(declined[good].mean()), 4)
    if bad.sum():
        # Applicants who defaulted and would have been approved anyway.
        out["fnr_bad_approved"] = round(float((~declined[bad]).mean()), 4)

    return out


def analyse(model_name: str, y_true: np.ndarray, risk: np.ndarray,
            groups: dict[str, pd.Series], is_probability: bool) -> list[dict]:
    """Apply one portfolio threshold, then measure every group under it."""
    threshold = float(np.quantile(risk, 1 - DECLINE_SHARE))
    declined = risk >= threshold

    print(f"\n{'=' * 74}")
    print(f"{model_name}   (decline the riskiest {DECLINE_SHARE:.0%}; "
          f"threshold {threshold:.4f})")
    print(f"{'=' * 74}")

    rows: list[dict] = []
    for attribute, series in groups.items():
        values = series.to_numpy()
        print(f"\n  {attribute}")
        print(f"    {'group':<22} {'n':>8} {'default':>8} {'declined':>9} "
              f"{'AUC':>7} {'good declined':>14}")
        print(f"    {'-' * 22} {'-' * 8} {'-' * 8} {'-' * 9} {'-' * 7} "
              f"{'-' * 14}")

        for value in sorted(pd.unique(values)):
            mask = values == value
            if mask.sum() == 0:
                continue
            m = group_metrics(y_true[mask], risk[mask], declined[mask],
                              is_probability)
            m.update({"model": model_name, "attribute": attribute,
                      "group": value})
            rows.append(m)

            auc = f"{m['auc']:.4f}" if m["auc"] is not None else "     -"
            fpr = (f"{m['fpr_good_declined']:.4f}"
                   if m["fpr_good_declined"] is not None else "     -")
            print(f"    {value[:22]:<22} {m['n']:>8,} "
                  f"{m['default_rate']:>7.2%} {m['decline_rate']:>8.2%} "
                  f"{auc:>7} {fpr:>14}")

    return rows


def bootstrap_disparities(model_name: str, y: np.ndarray, risk: np.ndarray,
                          groups: dict[str, pd.Series], n_boot: int,
                          seed: int) -> list[dict]:
    """Confidence intervals for the disparity ratios, and a bias warning.

    WHY THIS IS NOT OPTIONAL. Both headline measures are ratios of a MINIMUM to a
    MAXIMUM taken across groups. That structure is biased even when every group
    is identical in truth: sampling noise pushes the observed minimum down and
    the observed maximum up, so a disparity ratio computed this way looks worse
    than reality, and the smaller the groups the worse it looks. Reporting
    "DI = 0.325" from subgroups as small as 752 without an interval invites
    exactly the challenge it deserves.

    Two things are therefore reported alongside each interval:

    `selection_stability` - the share of resamples in which the SAME group comes
    out worst. A disparity attached to a group that changes from resample to
    resample is a statement about noise, not about that group.

    `null_ratio_median` - the ratio obtained when the decision is permuted at
    random within the sample, holding the group sizes fixed. This is what the
    measure reads when there is no disparity at all. A observed ratio close to
    this is not evidence of anything, and for small groups it can sit well below
    the 0.8 threshold on its own.
    """
    rng = np.random.default_rng(seed)
    n = len(y)
    good = y == 0

    coded = {}
    for attribute, series in groups.items():
        values = series.to_numpy()
        labels, codes = np.unique(values, return_inverse=True)
        coded[attribute] = (labels, codes)

    def ratios(idx: np.ndarray, declined: np.ndarray, attribute: str):
        labels, codes = coded[attribute]
        k = len(labels)
        c = codes[idx]
        counts = np.bincount(c, minlength=k).astype(float)
        declines = np.bincount(c, weights=declined, minlength=k)

        g = good[idx]
        good_counts = np.bincount(c[g], minlength=k).astype(float)
        good_declines = np.bincount(c[g], weights=declined[g], minlength=k)

        eligible = counts >= MIN_GROUP_N
        if eligible.sum() < 2:
            return None, None, None, None

        with np.errstate(invalid="ignore", divide="ignore"):
            approval = 1 - declines / counts
            fpr = good_declines / good_counts

        ap = np.where(eligible, approval, np.nan)
        di = np.nanmin(ap) / np.nanmax(ap) if np.nanmax(ap) > 0 else np.nan
        worst_ap = int(np.nanargmin(ap))

        fp = np.where(eligible & (good_counts > 0), fpr, np.nan)
        valid = np.isfinite(fp)
        if valid.sum() >= 2 and np.nanmin(fp) > 0:
            eo = np.nanmax(fp) / np.nanmin(fp)
            worst_fp = int(np.nanargmax(fp))
        else:
            eo, worst_fp = np.nan, -1
        return di, eo, worst_ap, worst_fp

    collected: dict[str, dict[str, list]] = {
        a: {"di": [], "eo": [], "worst_ap": [], "worst_fp": [], "null_di": []}
        for a in groups
    }

    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        rb = risk[idx]
        threshold = float(np.quantile(rb, 1 - DECLINE_SHARE))
        declined = (rb >= threshold).astype(float)

        # Null: same decline volume, assigned at random. Gives the reading the
        # measure produces when no group is treated differently at all.
        null_declined = np.zeros(n)
        null_declined[rng.choice(n, size=int(DECLINE_SHARE * n),
                                 replace=False)] = 1.0

        for attribute in groups:
            di, eo, wap, wfp = ratios(idx, declined, attribute)
            if di is not None:
                collected[attribute]["di"].append(di)
                collected[attribute]["eo"].append(eo)
                collected[attribute]["worst_ap"].append(wap)
                collected[attribute]["worst_fp"].append(wfp)
            ndi, _, _, _ = ratios(idx, null_declined, attribute)
            if ndi is not None:
                collected[attribute]["null_di"].append(ndi)

    out = []
    for attribute, c in collected.items():
        di = np.array(c["di"], dtype=float)
        eo = np.array(c["eo"], dtype=float)
        if di.size == 0:
            continue
        labels, _ = coded[attribute]
        wap = np.array(c["worst_ap"])
        wfp = np.array([w for w in c["worst_fp"] if w >= 0])

        mode_ap = np.bincount(wap).argmax() if wap.size else -1
        mode_fp = np.bincount(wfp).argmax() if wfp.size else -1

        out.append({
            "model": model_name,
            "attribute": attribute,
            "n_boot": int(di.size),
            "di_lo": round(float(np.nanpercentile(di, 2.5)), 4),
            "di_hi": round(float(np.nanpercentile(di, 97.5)), 4),
            "eo_lo": round(float(np.nanpercentile(eo, 2.5)), 4)
            if np.isfinite(eo).any() else None,
            "eo_hi": round(float(np.nanpercentile(eo, 97.5)), 4)
            if np.isfinite(eo).any() else None,
            "di_below_four_fifths_share": round(float((di < 0.8).mean()), 4),
            "selection_stability_approval": round(
                float((wap == mode_ap).mean()), 4) if wap.size else None,
            "most_often_least_approved": str(labels[mode_ap])
            if mode_ap >= 0 else None,
            "selection_stability_error": round(
                float((wfp == mode_fp).mean()), 4) if wfp.size else None,
            "most_often_wrongly_declined": str(labels[mode_fp])
            if mode_fp >= 0 else None,
            "null_ratio_median": round(
                float(np.nanmedian(c["null_di"])), 4) if c["null_di"] else None,
        })
    return out


def disparities(rows: list[dict], model_name: str) -> list[dict]:
    """Reduce each attribute to the two disparity measures that matter."""
    out = []
    frame = pd.DataFrame([r for r in rows if r["model"] == model_name])

    for attribute, block in frame.groupby("attribute", sort=False):
        eligible = block[block["n"] >= MIN_GROUP_N]
        if len(eligible) < 2:
            continue

        approval = 1 - eligible["decline_rate"]
        # Four-fifths rule: least-approved group relative to most-approved.
        di_ratio = float(approval.min() / approval.max())
        worst_approved = eligible.loc[approval.idxmin(), "group"]
        best_approved = eligible.loc[approval.idxmax(), "group"]

        fpr = eligible["fpr_good_declined"].dropna()
        eo_gap = float(fpr.max() - fpr.min()) if len(fpr) >= 2 else None
        eo_ratio = (float(fpr.max() / fpr.min())
                    if len(fpr) >= 2 and fpr.min() > 0 else None)
        worst_fpr = (eligible.loc[fpr.idxmax(), "group"]
                     if len(fpr) >= 2 else None)

        aucs = eligible["auc"].dropna()
        auc_spread = float(aucs.max() - aucs.min()) if len(aucs) >= 2 else None
        worst_auc_group = (eligible.loc[aucs.idxmin(), "group"]
                           if len(aucs) >= 2 else None)

        out.append({
            "model": model_name,
            "attribute": attribute,
            "groups_compared": int(len(eligible)),
            "disparate_impact_ratio": round(di_ratio, 4),
            "fails_four_fifths": bool(di_ratio < 0.8),
            "least_approved_group": worst_approved,
            "most_approved_group": best_approved,
            "equal_opportunity_gap": (round(eo_gap, 4)
                                      if eo_gap is not None else None),
            "equal_opportunity_ratio": (round(eo_ratio, 4)
                                        if eo_ratio is not None else None),
            "most_wrongly_declined_group": worst_fpr,
            "auc_spread": round(auc_spread, 4) if auc_spread is not None else None,
            "worst_served_group": worst_auc_group,
        })
    return out


def main() -> int:
    if not PROCESSED.exists():
        print(f"Missing {PROCESSED}. Run prepare_sba.py first.")
        return 1

    df = pd.read_parquet(PROCESSED)
    df = df[df["ApprovalFY"].between(COHORT_MIN, COHORT_MAX)].copy()

    if MATURED_ONLY:
        matures_by = df["ApprovalFY"] + df["term_years"]
        df = df[matures_by <= DATA_CUTOFF_YEAR].copy()

    df = add_scorecard_columns(df)

    # Temporal protocol only. The random split is reported elsewhere purely to
    # quantify its optimism; it would be indefensible to assess fairness under a
    # protocol the study itself argues overstates performance.
    train = df[df["ApprovalFY"] <= TEMPORAL_BOUNDARY]
    test = df[df["ApprovalFY"] > TEMPORAL_BOUNDARY].copy()

    print(f"Fairness assessment on the temporal test cohort")
    print(f"  train n={len(train):,}  ({train['ApprovalFY'].min():.0f}-"
          f"{train['ApprovalFY'].max():.0f})")
    print(f"  test  n={len(test):,}  ({test['ApprovalFY'].min():.0f}-"
          f"{test['ApprovalFY'].max():.0f})")
    print(f"  test default rate {test['default'].mean():.2%}")

    gbm = HistGradientBoostingClassifier(
        max_iter=300, learning_rate=0.1, max_depth=6, random_state=42
    )
    gbm.fit(train[CLEAN_FEATURES], train["default"].to_numpy())
    p_default = gbm.predict_proba(test[CLEAN_FEATURES])[:, 1]

    y_test = test["default"].to_numpy()
    groups = group_definitions(test)

    rows = analyse("Gradient boosting (clean, temporal)", y_test, p_default,
                   groups, is_probability=True)

    # The scorecard is the artefact this thesis actually proposes, so it is the
    # one whose disparate impact matters most - even though it discriminates
    # barely above chance. High score = low risk, hence the negation.
    card = test["scorecard_credit_risk"]
    valid = card.notna().to_numpy()
    card_rows = analyse(
        "Expert scorecard (unfitted)", y_test[valid],
        -card.to_numpy()[valid],
        {k: v[valid] for k, v in groups.items()},
        is_probability=False,
    )
    rows.extend(card_rows)

    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    detail = pd.DataFrame(rows)[[
        "model", "attribute", "group", "n", "default_rate", "decline_rate",
        "auc", "brier", "mean_predicted", "calibration_gap",
        "fpr_good_declined", "fnr_bad_approved",
    ]]
    detail.to_csv(OUT_TABLES / "fairness_groups.csv", index=False)

    summary = (disparities(rows, "Gradient boosting (clean, temporal)")
               + disparities(rows, "Expert scorecard (unfitted)"))

    print(f"\nBootstrapping disparity intervals ({N_BOOT} resamples)...")
    intervals = (
        bootstrap_disparities("Gradient boosting (clean, temporal)", y_test,
                              p_default, groups, N_BOOT, SEED)
        + bootstrap_disparities("Expert scorecard (unfitted)", y_test[valid],
                                -card.to_numpy()[valid],
                                {k: v[valid] for k, v in groups.items()},
                                N_BOOT, SEED)
    )
    by_key = {(i["model"], i["attribute"]): i for i in intervals}
    for s in summary:
        s.update({k: v for k, v in
                  by_key.get((s["model"], s["attribute"]), {}).items()
                  if k not in ("model", "attribute")})

    print(f"\n{'=' * 74}")
    print("DISPARITY SUMMARY")
    print(f"{'=' * 74}")
    print("  Selection-rate disparity below 0.80 fails the four-fifths rule.")
    print("  The equal-opportunity ratio compares how often CREDITWORTHY")
    print("  applicants are declined across groups; 1.0 is parity.")
    print("  'null' is what the DI measure reads when declines are assigned at")
    print("  random - the floor below which a ratio means nothing.\n")
    for s in summary:
        flag = "FAILS" if s["fails_four_fifths"] else "passes"
        eo = (f"{s['equal_opportunity_ratio']:.2f}x"
              if s["equal_opportunity_ratio"] else "   -")
        ci = (f"[{s['di_lo']:.3f}, {s['di_hi']:.3f}]"
              if s.get("di_lo") is not None else "-")
        null = (f"{s['null_ratio_median']:.3f}"
                if s.get("null_ratio_median") is not None else "-")
        print(f"  {s['model'][:26]:<26} {s['attribute'][:22]:<22} "
              f"DI={s['disparate_impact_ratio']:.3f} {ci:<16} {flag:<6} "
              f"null={null}  EO {eo:>7}")

    print("\n  Is the same group identified as worst across resamples?")
    print(f"    {'model':<26} {'attribute':<22} {'stability':>10}  group")
    for s in summary:
        st = s.get("selection_stability_error")
        if st is not None:
            note = "" if st >= 0.8 else "   <-- unstable"
            print(f"    {s['model'][:26]:<26} {s['attribute'][:22]:<22} "
                  f"{st:>9.0%}  {s['most_often_wrongly_declined']}{note}")

    with open(OUT_TABLES / "fairness_summary.json", "w", encoding="utf-8") as fh:
        json.dump({
            "protocol": "temporal",
            "decline_share": DECLINE_SHARE,
            "test_n": int(len(test)),
            "test_default_rate": round(float(test["default"].mean()), 4),
            "min_group_n": MIN_GROUP_N,
            "n_boot": N_BOOT,
            "protected_characteristics_available": False,
            "note": ("The dataset records no legally protected characteristic. "
                     "These are credit-access proxies, not protected classes."),
            "disparities": summary,
        }, fh, indent=2)

    print(f"\nSaved fairness_groups.csv and fairness_summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
