"""Are credit risk and development impact independent? (RQ4)

Run:  python research/src/objective_independence.py

WHY THIS MATTERS
----------------
The model reports two scores and refuses to combine them. That design decision
rests on Arvanitis, Stampini and Vencatachellum (2015), who found development and
credit concerns to be empirically independent in appraisal at the African
Development Bank. If they were instead strongly correlated, a single combined
score would lose almost nothing and the separation would be ceremony.

Their finding is from one multilateral institution's project portfolio. This
script tests the same proposition on 652,284 small-business facilities with
realised outcomes — a different population, a different instrument, and orders of
magnitude more cases.

WHAT IS BEING CORRELATED
    credit-risk score      the SBA-observable credit criteria
    development score      jobs created + retained, jobs per unit of facility,
                           job creation relative to existing workforce

The development proxy is thin: SBA data carries employment only, so five of the
nine items in clause 5 of the People's Bank form have no counterpart here. The
test is therefore of the *employment* dimension of development impact against
credit risk, and is reported as such.

THREE QUESTIONS
  1. Do the two scores co-move? (correlation)
  2. Does development impact predict default at all? (default by quartile)
  3. How often do the two objectives disagree about the same facility?
     — the practical question, since disagreement is what a single combined
       score would hide.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from benchmark import COHORT_MAX, COHORT_MIN, DATA_CUTOFF_YEAR  # noqa: E402
from fuzzy_scorecard import add_scorecard_columns, load_scorecard  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "research" / "data" / "processed" / "sba_clean.parquet"
OUT_TABLES = ROOT / "research" / "outputs" / "tables"


def band(scores: pd.Series, tree_bands: list[dict]) -> pd.Series:
    out = pd.Series(index=scores.index, dtype=object)
    for b in sorted(tree_bands, key=lambda x: x["min"]):
        hit = scores.between(b["min"], b["max"])
        out[hit] = b["code"]
    return out


def main() -> int:
    if not PROCESSED.exists():
        print("Run prepare_sba.py first.")
        return 1

    df = pd.read_parquet(PROCESSED)
    df = df[df["ApprovalFY"].between(COHORT_MIN, COHORT_MAX)]
    df = df[(df["ApprovalFY"] + df["term_years"]) <= DATA_CUTOFF_YEAR].copy()
    df = add_scorecard_columns(df)

    ok = df["scorecard_credit_risk"].notna() & df["scorecard_development"].notna()
    df = df[ok]

    credit = df["scorecard_credit_risk"]
    dev = df["scorecard_development"]

    print(f"{len(df):,} facilities with both objectives scored")
    print(f"default rate {df['default'].mean():.2%}\n")

    findings: dict = {"n": int(len(df))}

    # ---- 1. do the objectives co-move? -------------------------------------
    pearson = stats.pearsonr(credit, dev)
    spearman = stats.spearmanr(credit, dev)

    print("=" * 74)
    print("1. CORRELATION BETWEEN THE TWO OBJECTIVES")
    print("=" * 74)
    print(f"  Pearson  r = {pearson.statistic:+.4f}   (p = {pearson.pvalue:.3g})")
    print(f"  Spearman rho = {spearman.statistic:+.4f}   (p = {spearman.pvalue:.3g})")
    print(f"  Shared variance (r^2) = {pearson.statistic ** 2:.4f}")

    findings["pearson_r"] = round(float(pearson.statistic), 4)
    findings["spearman_rho"] = round(float(spearman.statistic), 4)
    findings["r_squared"] = round(float(pearson.statistic ** 2), 4)

    # With n this large, statistical significance is uninformative - a trivial
    # correlation will register as significant. Effect size is what matters.
    r = abs(pearson.statistic)
    verdict = ("essentially independent" if r < 0.10 else
               "weakly related" if r < 0.30 else
               "moderately related" if r < 0.50 else
               "strongly related")
    print(f"\n  -> {verdict}")
    print("     (n is large enough that any correlation is 'significant';")
    print("      the effect size is what carries meaning)")
    findings["verdict"] = verdict

    # ---- 2. does development impact predict default? -----------------------
    print("\n" + "=" * 74)
    print("2. DEFAULT RATE BY DEVELOPMENT-IMPACT QUARTILE")
    print("=" * 74)

    # Development scores are heavily tied (many facilities create zero jobs), so
    # qcut may return fewer bins than requested. Label them after the fact.
    df["dev_quartile"] = pd.qcut(dev, 4, duplicates="drop")
    by_dev = df.groupby("dev_quartile", observed=True)["default"].agg(["count", "mean"])
    for i, (q, row) in enumerate(by_dev.iterrows(), start=1):
        print(f"  bin {i} {str(q):<22} n={row['count']:>7,.0f}   "
              f"default={row['mean']:.2%}")

    spread = float(by_dev["mean"].max() - by_dev["mean"].min())
    print(f"\n  spread across quartiles: {spread:.2%}")
    findings["dev_quartile_default_spread"] = round(spread, 4)
    findings["dev_quartile_rates"] = {
        str(q): round(float(v), 4) for q, v in by_dev["mean"].items()
    }
    findings["n_dev_bins"] = int(len(by_dev))

    if spread < 0.05:
        print("  -> development impact carries little information about default")
    else:
        print("  -> development impact is associated with default; report the direction")

    # ---- 2b. control for shared inputs -------------------------------------
    # The two proxy scores are not built from disjoint variables: NoEmp feeds the
    # credit criterion "employees" and the development criterion
    # "job_creation_rate"; GrAppv feeds "loan_per_employee" and "jobs_per_100k".
    # Some of the observed correlation is therefore mechanical rather than
    # economic, and has to be removed before the result means anything.
    print("\n" + "=" * 74)
    print("2b. CONTROLLING FOR SHARED INPUTS")
    print("=" * 74)
    print("  NoEmp and GrAppv feed criteria on BOTH sides, so the headline")
    print("  correlation is inflated by construction. Recomputing with a")
    print("  development measure that shares no inputs with the credit score:")
    print("  raw jobs supported (CreateJob + RetainedJob), unnormalised.")

    from fuzzy_scorecard import score_from_bands
    sc = load_scorecard()
    jobs_criterion = next(
        c for o in sc["objectives"] for d in o["dimensions"]
        for c in d["criteria"] if c["id"] == "jobs_supported"
    )
    dev_clean = score_from_bands(df["jobs_supported"], jobs_criterion["bands"])

    # And a credit score excluding the two criteria that touch NoEmp or GrAppv.
    from fuzzy_scorecard import score_objective, SBA_COLUMN_MAP
    trimmed = json.loads(json.dumps(sc))
    for o in trimmed["objectives"]:
        for d in o["dimensions"]:
            d["criteria"] = [c for c in d["criteria"]
                             if c["id"] not in ("employees", "loan_per_employee")]
        o["dimensions"] = [d for d in o["dimensions"] if d["criteria"]]
    credit_clean, _ = score_objective(df, trimmed, "credit_risk", SBA_COLUMN_MAP)

    both = credit_clean.notna() & dev_clean.notna()
    pc = stats.pearsonr(credit_clean[both], dev_clean[both])
    sc_rho = stats.spearmanr(credit_clean[both], dev_clean[both])

    print(f"\ndisjoint-input Pearson  r = {pc.statistic:+.4f}")
    print(f"  disjoint-input Spearman rho = {sc_rho.statistic:+.4f}")
    print(f"  shared variance (r^2)       = {pc.statistic ** 2:.4f}")

    r2 = abs(pc.statistic)
    verdict2 = ("essentially independent" if r2 < 0.10 else
                "weakly related" if r2 < 0.30 else
                "moderately related" if r2 < 0.50 else
                "strongly related")
    print(f"\n-> {verdict2}")
    print(f"  (headline r = {pearson.statistic:+.4f} with shared inputs;")
    print(f"   r = {pc.statistic:+.4f} without. The difference is the confound.)")

    findings["disjoint_pearson_r"] = round(float(pc.statistic), 4)
    findings["disjoint_spearman_rho"] = round(float(sc_rho.statistic), 4)
    findings["disjoint_verdict"] = verdict2

    # ---- 3. how often do the objectives disagree? --------------------------
    print("\n" + "=" * 74)
    print("3. DISAGREEMENT BETWEEN THE OBJECTIVES")
    print("=" * 74)

    tree = json.loads(
        (ROOT / "shared" / "model" / "criteria-tree.json").read_text(encoding="utf-8")
    )
    df["credit_band"] = band(credit, tree["riskBands"])
    df["dev_band"] = band(dev, tree["riskBands"])

    order = {"A": 0, "B": 1, "C": 2, "D": 3}
    gap = (df["dev_band"].map(order) - df["credit_band"].map(order)).abs()

    same = float((gap == 0).mean())
    one = float((gap == 1).mean())
    two_plus = float((gap >= 2).mean())

    print(f"  same band                : {same:.1%}")
    print(f"  one band apart           : {one:.1%}")
    print(f"  two or more bands apart  : {two_plus:.1%}")
    print(f"\n  disagree at all          : {1 - same:.1%}")

    findings["band_same"] = round(same, 4)
    findings["band_one_apart"] = round(one, 4)
    findings["band_two_plus_apart"] = round(two_plus, 4)

    cross = pd.crosstab(df["credit_band"], df["dev_band"], normalize=True)
    print("\n  credit band (rows) x development band (columns), share of portfolio:")
    print(cross.round(4).to_string())
    cross.to_csv(OUT_TABLES / "objective_crosstab.csv")

    # ---- the point of the whole exercise -----------------------------------
    print("\n" + "=" * 74)
    print("WHAT A COMBINED SCORE WOULD HIDE")
    print("=" * 74)
    print(f"  {1 - same:.1%} of facilities fall in different bands on the two")
    print(f"  objectives, and {two_plus:.1%} differ by two bands or more. A single")
    print("  averaged score would report one number for all of them, making a")
    print("  strong-credit/weak-development facility indistinguishable from a")
    print("  middling one on both.")

    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    with open(OUT_TABLES / "objective_independence.json", "w", encoding="utf-8") as fh:
        json.dump(findings, fh, indent=2)
    by_dev.to_csv(OUT_TABLES / "development_quartile_default.csv")

    print(f"\nSaved research/outputs/tables/objective_independence.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
