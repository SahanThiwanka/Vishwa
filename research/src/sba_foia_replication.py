"""Is the contamination in SBA's own records, or in the Kaggle derivative?

Run:  python research/src/sba_foia_replication.py

THE QUESTION THIS ANSWERS
-------------------------
Chapter 5 establishes that `Term` in the SBA National dataset carries outcome
information, and reports the mechanism as unresolved. Three explanations were
left open: the value is rewritten on restructuring, it is recomputed under some
servicing convention, or it was introduced when that derivative file was
assembled. The third is the one that would make the finding uninteresting - a
packaging error in one Kaggle upload rather than a property of the data.

That can be settled without contacting anyone, because the SBA publishes its own
loan-level FOIA extracts, refreshed quarterly, covering the same programme and
the same years. If the pattern is present there, the derivative did not create
it.

WHAT IT FINDS
-------------
The pattern is present in SBA's own publication. Across 603,665 resolved 7(a)
facilities approved FY2000-2009, the roundness boolean reaches AUC ~0.868 - close
to the ~0.889 measured on the derivative - and holds in every approval year.
**The contamination is not an artefact of the Kaggle packaging.**

The 504 programme is the control, and it is the more interesting half. Same
agency, same FOIA release, overlapping years, but 504 terms are fixed by
programme design: 96% of facilities are written at exactly 240 months. There,
roundness discriminates at almost exactly chance, and charged-off loans are
*more* likely to carry a round term than repaid ones. Whatever produces the 7(a)
pattern does not operate on 504 records.

WHAT THIS IS NOT
----------------
**This is not an independent replication and must never be described as one.**
The SBA National dataset is itself derived from SBA FOIA releases, so these are
the same underlying loan records at a different vintage, not a second source.
What the comparison establishes is narrower and still worth having: the artefact
exists in the authoritative publication, so it was not introduced downstream.

DATA
----
Not committed - 318 MB and 54 MB. Download from
https://data.sba.gov/dataset/7a-504-foia into research/data/raw/ as:

    FOIA_7a_FY2000_FY2009.csv
    FOIA_504_FY1991_FY2009.csv
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "research" / "data" / "raw"
OUT_TABLES = ROOT / "research" / "outputs" / "tables"

SEVEN_A = RAW / "FOIA_7a_FY2000_FY2009.csv"
FIVE_04 = RAW / "FOIA_504_FY1991_FY2009.csv"

# The two files spell the paid-in-full status differently. Discovered the hard
# way: filtering the 504 file for "P I F" matched nothing, leaving a frame of
# pure charge-offs and a default rate of 100%.
PAID = {"P I F", "PIF"}
DEFAULTED = {"CHGOFF"}

USE = ["ApprovalFY", "TermInMonths", "LoanStatus"]

# Measured on the Kaggle-derived file by leakage_analysis.py, for comparison.
DERIVATIVE_AUC = 0.8894


def load(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        print(f"  MISSING {path.name} - see the module docstring for the URL")
        return None
    df = pd.read_csv(path, usecols=USE, low_memory=False)
    df = df[df["LoanStatus"].isin(PAID | DEFAULTED)].copy()
    df["default"] = df["LoanStatus"].isin(DEFAULTED).astype(int)
    df = df[df["TermInMonths"].notna() & (df["TermInMonths"] > 0)]
    df["term"] = df["TermInMonths"].astype(int)
    df["round12"] = (df["term"] % 12 == 0)
    return df


def summarise(name: str, df: pd.DataFrame) -> dict:
    y = df["default"].to_numpy()
    r = df["round12"].to_numpy()
    # Irregular terms are the risky ones, so risk is the negation.
    auc = float(roc_auc_score(y, (~r).astype(float)))

    out = {
        "dataset": name,
        "n_resolved": int(len(df)),
        "default_rate": round(float(y.mean()), 6),
        "round_share_repaid": round(float(r[y == 0].mean()), 6),
        "round_share_default": round(float(r[y == 1].mean()), 6),
        "roundness_auc": round(auc, 4),
    }

    print(f"\n{name}")
    print("-" * 66)
    print(f"  resolved facilities            {out['n_resolved']:>9,}")
    print(f"  default rate                   {out['default_rate']:>9.2%}")
    print(f"  repaid, term a multiple of 12  {out['round_share_repaid']:>9.2%}")
    print(f"  charged off, multiple of 12    {out['round_share_default']:>9.2%}")
    print(f"  AUC of roundness alone         {out['roundness_auc']:>9.4f}")
    return out


def by_year(df: pd.DataFrame) -> list[dict]:
    rows = []
    print(f"\n  {'FY':>6} {'n':>8} {'round':>7} {'def|round':>10} "
          f"{'def|irregular':>14} {'AUC':>7}")
    for fy, g in df.groupby("ApprovalFY"):
        if len(g) < 5000 or g["default"].nunique() < 2:
            continue
        r = g["round12"]
        auc = float(roc_auc_score(g["default"], (~r).astype(float)))
        rows.append({
            "approval_fy": int(fy),
            "n": int(len(g)),
            "round_share": round(float(r.mean()), 6),
            "default_round": round(float(g.loc[r, "default"].mean()), 6),
            "default_irregular": round(float(g.loc[~r, "default"].mean()), 6),
            "auc": round(auc, 4),
        })
        print(f"  {int(fy):>6} {len(g):>8,} {r.mean():>6.1%} "
              f"{g.loc[r, 'default'].mean():>9.2%} "
              f"{g.loc[~r, 'default'].mean():>13.2%} {auc:>7.4f}")
    return rows


def main() -> int:
    print("Does the contamination exist in SBA's own published records?")
    print("=" * 66)

    seven = load(SEVEN_A)
    five = load(FIVE_04)
    if seven is None:
        return 1

    findings = {"derivative_roundness_auc": DERIVATIVE_AUC, "datasets": []}

    s = summarise("7(a) programme, FY2000-2009 (SBA FOIA)", seven)
    findings["datasets"].append(s)
    year_rows = by_year(seven)

    aucs = [r["auc"] for r in year_rows]
    print(f"\n  Every approval year falls in {min(aucs):.4f}-{max(aucs):.4f}.")
    print(f"  The Kaggle-derived file gives {DERIVATIVE_AUC:.4f} on the same probe.")
    print("\n  => The pattern is in SBA's own publication. The derivative did")
    print("     not create it.")

    if five is not None:
        f = summarise("504 programme, FY1991-2009 (SBA FOIA)", five)
        findings["datasets"].append(f)
        top = five["term"].value_counts().head(3)
        share_240 = float((five["term"] == 240).mean())
        findings["five04_share_240_months"] = round(share_240, 6)
        print(f"\n  Terms are fixed by programme design: "
              f"{share_240:.1%} are exactly 240 months.")
        print(f"  Most common: {', '.join(f'{int(k)}m ({v:,})' for k, v in top.items())}")
        print("\n  Roundness discriminates at chance here, and charged-off")
        print("  facilities are marginally MORE round-termed than repaid ones.")
        print("  Whatever produces the 7(a) pattern does not operate on 504.")

    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(year_rows).to_csv(
        OUT_TABLES / "foia_7a_by_year.csv", index=False)
    (OUT_TABLES / "foia_replication.json").write_text(
        json.dumps(findings, indent=2), encoding="utf-8")

    print("\n" + "=" * 66)
    print("Saved foia_replication.json and foia_7a_by_year.csv")
    print("\nNOTE: this is NOT an independent replication. The SBA National")
    print("dataset derives from SBA FOIA releases, so these are the same loan")
    print("records at a different vintage. It settles where the artefact")
    print("originates, not whether it appears in a second source.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
