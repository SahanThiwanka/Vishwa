"""Evidence that the `Term` field in the SBA National dataset is contaminated.

Run:  python research/src/leakage_analysis.py

FINDING
-------
In the SBA National dataset, whether `Term` is an exact multiple of 12 predicts
default with AUC ~0.89 - on its own, within every approval year. Contractual loan
terms cannot behave this way. `Term` therefore carries information about the
outcome, and any model permitted to split on its exact value inherits that.

This matters beyond the present study: SBA National is widely used in credit-
scoring research and teaching, and tree-based models given `Term` will report
inflated discrimination.

WHAT IS ESTABLISHED
  * 86.6% of repaid loans have a term that is a multiple of 12; only 8.5% of
    charged-off loans do.
  * Charged-off loans are distributed near-uniformly across Term mod 12
    (~8-9% in each of the twelve residues), as though the value were produced by
    a process unrelated to contracting.
  * The association holds WITHIN each approval year (AUC 0.87-0.90, 1993-2008),
    so it is not a cohort-composition effect.
  * Neighbouring terms diverge implausibly: in 2007, 60-month loans defaulted at
    11.1%, 59-month at 86.7%, 63-month at 81.0%.

WHAT IS NOT ESTABLISHED
  The mechanism. `Term` is NOT simply the elapsed months to charge-off:
  correlation with actual disbursement-to-chargeoff duration is only 0.043, and
  just 5% of cases match within three months. Whether the value is rewritten on
  restructuring, recomputed under some servicing rule, or introduced when this
  derivative file was assembled cannot be determined from the data alone.

  The thesis must report the contamination as demonstrated and the mechanism as
  unresolved. Do not assert a cause that has not been shown.

CONSEQUENCE
  `Term` and every feature derived from it are excluded from the clean model
  specification. This costs real predictive power - some of the term signal is
  genuinely economic - but the contaminated and legitimate components cannot be
  separated, so the whole field must go.
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
OUT_FIGURES = ROOT / "research" / "outputs" / "figures"

COHORT_MIN, COHORT_MAX = 1990, 2010


def main() -> int:
    if not PROCESSED.exists():
        print(f"Missing {PROCESSED}. Run prepare_sba.py first.")
        return 1

    df = pd.read_parquet(PROCESSED)
    df = df[df["ApprovalFY"].between(COHORT_MIN, COHORT_MAX)].copy()
    df["round12"] = (df["Term"] % 12 == 0) & (df["Term"] > 0)

    findings: dict = {"cohort": [COHORT_MIN, COHORT_MAX], "n": int(len(df))}

    # --- 1. headline association -------------------------------------------
    by_round = df.groupby("round12")["default"].agg(["count", "mean"])
    overall_auc = roc_auc_score(df["default"], ~df["round12"])

    print("=" * 70)
    print("1. TERM ROUNDNESS vs DEFAULT")
    print("=" * 70)
    print(by_round.to_string())
    print(f"\n  AUC of the single boolean 'Term % 12 == 0': {overall_auc:.4f}")
    print(f"  repaid loans with round term    : {df[df['default'] == 0]['round12'].mean():.1%}")
    print(f"  charged-off loans w/ round term : {df[df['default'] == 1]['round12'].mean():.1%}")

    findings["roundness_auc"] = round(float(overall_auc), 4)
    findings["round_share_repaid"] = round(float(df[df["default"] == 0]["round12"].mean()), 4)
    findings["round_share_default"] = round(float(df[df["default"] == 1]["round12"].mean()), 4)

    # --- 2. residue distribution -------------------------------------------
    residue = pd.crosstab(df["Term"] % 12, df["default"], normalize="columns")
    residue.columns = ["repaid", "charged_off"]

    print("\n" + "=" * 70)
    print("2. DISTRIBUTION ACROSS Term mod 12")
    print("=" * 70)
    print("  Repaid loans concentrate at residue 0. Charged-off loans spread")
    print("  near-uniformly, which contracting behaviour does not produce.\n")
    print(residue.round(4).to_string())
    residue.to_csv(OUT_TABLES / "leakage_residue_distribution.csv")

    # --- 3. within-year control --------------------------------------------
    print("\n" + "=" * 70)
    print("3. WITHIN-YEAR ASSOCIATION (rules out cohort composition)")
    print("=" * 70)
    print(f"  {'year':>6} {'n':>8} {'round':>9} {'irregular':>10} {'AUC':>7}")

    rows = []
    for year, group in df.groupby("ApprovalFY"):
        if len(group) < 5000 or group["default"].nunique() < 2:
            continue
        r = group[group["round12"]]["default"].mean()
        i = group[~group["round12"]]["default"].mean()
        auc = roc_auc_score(group["default"], ~group["round12"])
        rows.append({
            "year": int(year), "n": int(len(group)),
            "default_round": round(float(r), 4),
            "default_irregular": round(float(i), 4),
            "auc": round(float(auc), 4),
        })
        print(f"  {int(year):>6} {len(group):>8,} {r:>9.2%} {i:>10.2%} {auc:>7.3f}")

    within = pd.DataFrame(rows)
    within.to_csv(OUT_TABLES / "leakage_within_year.csv", index=False)
    findings["within_year_auc_min"] = float(within["auc"].min())
    findings["within_year_auc_max"] = float(within["auc"].max())

    # --- 4. adjacent-term discontinuity ------------------------------------
    print("\n" + "=" * 70)
    print("4. ADJACENT-TERM DISCONTINUITY (2007 approvals)")
    print("=" * 70)
    y2007 = df[df["ApprovalFY"] == 2007]
    adjacent = (
        y2007[y2007["Term"].between(58, 64)]
        .groupby("Term")["default"].agg(["count", "mean"])
    )
    print("  A one-month difference in contractual term cannot do this:\n")
    print(adjacent.round(4).to_string())
    adjacent.to_csv(OUT_TABLES / "leakage_adjacent_terms.csv")

    # --- 5. mechanism test that FAILED -------------------------------------
    print("\n" + "=" * 70)
    print("5. MECHANISM TEST: is Term the elapsed time to charge-off?")
    print("=" * 70)
    raw = pd.read_csv(
        ROOT / "research" / "data" / "raw" / "SBAnational.csv",
        low_memory=False,
        usecols=["Term", "MIS_Status", "DisbursementDate", "ChgOffDate"],
    )
    d = raw[raw["MIS_Status"].astype(str).str.strip() == "CHGOFF"].copy()
    d["dis"] = pd.to_datetime(d["DisbursementDate"], errors="coerce", format="mixed")
    d["chg"] = pd.to_datetime(d["ChgOffDate"], errors="coerce", format="mixed")
    d = d.dropna(subset=["dis", "chg"])
    d["months_alive"] = (d["chg"] - d["dis"]).dt.days / 30.44
    d = d[(d["months_alive"] > 0) & (d["months_alive"] < 400) & (d["Term"] > 0)]

    corr = float(d["Term"].corr(d["months_alive"]))
    within3 = float((d["Term"] - d["months_alive"]).abs().le(3).mean())

    print(f"  correlation(Term, months to charge-off) : {corr:.4f}")
    print(f"  matching within +/- 3 months            : {within3:.1%}")
    print("\n  -> NO. Term is not simply survival time. The contamination is real")
    print("     but its mechanism is unresolved. Report it that way.")

    findings["survival_correlation"] = round(corr, 4)
    findings["survival_match_within_3mo"] = round(within3, 4)
    findings["mechanism"] = "unresolved"

    # --- figure -------------------------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))

        residue.plot(kind="bar", ax=axes[0], width=0.8,
                     color=["#2b7a4b", "#b3382c"])
        axes[0].set_title("Distribution across Term mod 12")
        axes[0].set_xlabel("Term mod 12")
        axes[0].set_ylabel("share of loans")
        axes[0].legend(["repaid", "charged off"])

        axes[1].plot(within["year"], within["default_round"] * 100,
                     marker="o", label="round term", color="#2b7a4b")
        axes[1].plot(within["year"], within["default_irregular"] * 100,
                     marker="s", label="irregular term", color="#b3382c")
        axes[1].set_title("Default rate by term roundness, within year")
        axes[1].set_xlabel("approval year")
        axes[1].set_ylabel("default rate (%)")
        axes[1].legend()

        fig.tight_layout()
        OUT_FIGURES.mkdir(parents=True, exist_ok=True)
        fig.savefig(OUT_FIGURES / "term_leakage.png", dpi=200)
        print(f"\nSaved figure: research/outputs/figures/term_leakage.png")
    except ImportError:
        print("\n(matplotlib not available - figure skipped)")

    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    with open(OUT_TABLES / "leakage_findings.json", "w", encoding="utf-8") as fh:
        json.dump(findings, fh, indent=2)

    print(f"\nSaved tables to research/outputs/tables/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
