"""Clean and prepare the SBA National dataset for model validation.

Run:  python research/src/prepare_sba.py

    ~~~ LEAKAGE WARNING - READ BEFORE CHANGING THIS FILE ~~~

The SBA dataset contains columns that are only populated AFTER a loan has already
defaulted:

    ChgOffPrinGr   charged-off principal   (non-zero only if defaulted)
    ChgOffDate     date of charge-off      (present only if defaulted)
    BalanceGross   outstanding balance at charge-off

Any model given these will score near-perfect AUC and the result is worthless -
it is reading the answer, not predicting it. This is the single most common error
in published work on this dataset. They are dropped explicitly below and the drop
is asserted at the end of this script.

If a reported AUC ever exceeds ~0.90 here, suspect leakage before celebrating.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "research" / "data" / "raw" / "SBAnational.csv"
OUT = ROOT / "research" / "data" / "processed"

# Populated only after default. Never available at appraisal time.
LEAKAGE_COLUMNS = ["ChgOffPrinGr", "ChgOffDate", "BalanceGross", "MIS_Status"]

# Free-text / identifier columns with no appraisal meaning.
DROP_COLUMNS = ["LoanNr_ChkDgt", "Name", "City", "Zip", "Bank"]

CURRENCY_COLUMNS = [
    "DisbursementGross",
    "BalanceGross",
    "ChgOffPrinGr",
    "GrAppv",
    "SBA_Appv",
]

# NAICS 2-digit sector labels, for industry-level analysis.
NAICS_SECTORS = {
    11: "Agriculture/Forestry/Fishing", 21: "Mining", 22: "Utilities",
    23: "Construction", 31: "Manufacturing", 32: "Manufacturing",
    33: "Manufacturing", 42: "Wholesale Trade", 44: "Retail Trade",
    45: "Retail Trade", 48: "Transportation", 49: "Transportation",
    51: "Information", 52: "Finance/Insurance", 53: "Real Estate",
    54: "Professional/Scientific", 55: "Management", 56: "Admin/Waste",
    61: "Education", 62: "Health Care", 71: "Arts/Entertainment",
    72: "Accommodation/Food", 81: "Other Services", 92: "Public Admin",
}


def parse_currency(series: pd.Series) -> pd.Series:
    """'$60,000.00 ' -> 60000.0"""
    return pd.to_numeric(
        series.astype(str)
        .str.replace(r"[$,]", "", regex=True)
        .str.strip()
        .replace({"": None, "nan": None}),
        errors="coerce",
    )


def clean_yn(series: pd.Series) -> pd.Series:
    """RevLineCr/LowDoc carry Y, N and a lot of junk ('0', 'T', '1', 'R'...).

    Only Y and N are meaningful; everything else becomes missing rather than being
    silently folded into 'N', which would invent information we do not have.
    """
    cleaned = series.astype(str).str.strip().str.upper()
    return cleaned.where(cleaned.isin(["Y", "N"]))


def main() -> int:
    if not RAW.exists():
        print(f"Missing {RAW}. See research/data/DATASETS.md")
        return 1

    print(f"Loading {RAW.name} ...")
    df = pd.read_csv(RAW, low_memory=False)
    print(f"  {len(df):,} rows x {len(df.columns)} columns")

    # ---- target -----------------------------------------------------------
    status = df["MIS_Status"].astype(str).str.strip().str.upper()
    df = df[status.isin(["P I F", "CHGOFF"])].copy()
    status = status.loc[df.index]
    df["default"] = (status == "CHGOFF").astype(int)
    print(f"  {len(df):,} rows with a usable outcome")
    print(f"  default rate: {df['default'].mean():.2%}")

    # ---- currency ---------------------------------------------------------
    for col in CURRENCY_COLUMNS:
        if col in df.columns:
            df[col] = parse_currency(df[col])

    # ---- dates ------------------------------------------------------------
    df["ApprovalDate"] = pd.to_datetime(df["ApprovalDate"], errors="coerce", format="mixed")
    df["DisbursementDate"] = pd.to_datetime(df["DisbursementDate"], errors="coerce", format="mixed")

    # ApprovalFY has stray strings like '1976A'
    df["ApprovalFY"] = pd.to_numeric(
        df["ApprovalFY"].astype(str).str.extract(r"(\d{4})")[0], errors="coerce"
    )

    # ---- feature engineering ---------------------------------------------
    # Guarantee share: how much risk the SBA retained. A lender-behaviour signal
    # analogous to the security-cover criterion (form clause 6.5).
    df["sba_guarantee_share"] = (df["SBA_Appv"] / df["GrAppv"]).replace([np.inf, -np.inf], np.nan)

    # Disbursed vs approved - a proxy for facility utilisation.
    df["disbursement_ratio"] = (
        df["DisbursementGross"] / df["GrAppv"]
    ).replace([np.inf, -np.inf], np.nan)

    df["term_years"] = df["Term"] / 12.0

    # Terms >= 240 months are effectively real-estate backed; a known and
    # strongly predictive distinction in this dataset.
    df["real_estate_backed"] = (df["Term"] >= 240).astype(int)

    # NewExist: 1 = existing business, 2 = new. 0 and blanks are invalid.
    df["is_new_business"] = df["NewExist"].map({1: 0, 2: 1})

    df["is_urban"] = df["UrbanRural"].map({1: 1, 2: 0})
    df["has_franchise"] = (~df["FranchiseCode"].isin([0, 1])).astype(int)

    df["rev_line_of_credit"] = clean_yn(df["RevLineCr"]).map({"Y": 1, "N": 0})
    df["low_doc_program"] = clean_yn(df["LowDoc"]).map({"Y": 1, "N": 0})

    # NAICS 0 means unrecorded, not sector zero.
    naics2 = pd.to_numeric(df["NAICS"], errors="coerce").fillna(0).astype(int) // 10000
    df["naics_sector_code"] = naics2.where(naics2 > 0)
    df["naics_sector"] = df["naics_sector_code"].map(NAICS_SECTORS)

    # Loans approved 2007-2009 sit in the financial crisis; a cohort control.
    df["crisis_cohort"] = df["ApprovalFY"].between(2007, 2009).astype(int)

    df["loan_per_employee"] = (
        df["GrAppv"] / df["NoEmp"].replace(0, np.nan)
    ).replace([np.inf, -np.inf], np.nan)

    # ---- development-impact proxies --------------------------------------
    # These are the ONLY observable stand-ins for the development-impact
    # objective (form clause 5). Employment generation and retention only -
    # nothing here proxies women's participation, import substitution or
    # foreign-exchange earnings. The thesis must state that limitation.
    df["jobs_supported"] = df["CreateJob"] + df["RetainedJob"]
    df["jobs_per_100k"] = (
        df["jobs_supported"] / (df["GrAppv"] / 100_000)
    ).replace([np.inf, -np.inf], np.nan)
    df["job_creation_rate"] = (
        df["CreateJob"] / df["NoEmp"].replace(0, np.nan)
    ).replace([np.inf, -np.inf], np.nan)

    # ---- drop leakage and identifiers ------------------------------------
    df = df.drop(columns=[c for c in LEAKAGE_COLUMNS + DROP_COLUMNS if c in df.columns])

    for col in LEAKAGE_COLUMNS:
        assert col not in df.columns, f"LEAKAGE: {col} survived the drop"

    # ---- save -------------------------------------------------------------
    OUT.mkdir(parents=True, exist_ok=True)
    out_path = OUT / "sba_clean.parquet"
    df.to_parquet(out_path, index=False)

    print(f"\nSaved {out_path.relative_to(ROOT)}")
    print(f"  {len(df):,} rows x {len(df.columns)} columns")
    print(f"  approval years {df['ApprovalFY'].min():.0f}-{df['ApprovalFY'].max():.0f}")
    print(f"  default rate  {df['default'].mean():.2%}")
    print("\nLeakage columns confirmed absent:", ", ".join(LEAKAGE_COLUMNS))

    print("\nDefault rate by approval decade:")
    decade = (df["ApprovalFY"] // 10 * 10).astype("Int64")
    summary = df.groupby(decade)["default"].agg(["count", "mean"])
    for dec, row in summary.iterrows():
        print(f"  {dec}s  n={row['count']:>8,.0f}  default={row['mean']:.2%}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
