"""Generate the figures used in the paper and thesis.

Run:  python research/src/make_figures.py

Reads only from research/outputs/tables/, so every figure is derived from
committed result files rather than recomputed with different settings.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "research" / "outputs" / "tables"
FIGURES = ROOT / "research" / "outputs" / "figures"

CLEAN = "#2b6ca3"
CONTAM = "#b3382c"
PROBE = "#7a7a7a"


def figure_inflation() -> None:
    """Clean vs contaminated AUC, with the meaningless probe as a reference line."""
    df = pd.read_csv(TABLES / "benchmark_results.csv")

    models = ["Expert scorecard (unfitted)", "Logistic regression", "Gradient boosting"]
    short = ["Expert\nscorecard", "Logistic\nregression", "Gradient\nboosting"]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)

    for ax, protocol in zip(axes, ["random", "temporal"]):
        sub = df[df["protocol"] == protocol]
        clean = [sub[(sub.spec == "clean") & (sub.model == m)]["auc"].iloc[0] for m in models]
        contam = [sub[(sub.spec == "contaminated") & (sub.model == m)]["auc"].iloc[0] for m in models]

        x = np.arange(len(models))
        w = 0.36
        ax.bar(x - w / 2, clean, w, label="Term excluded (clean)", color=CLEAN)
        ax.bar(x + w / 2, contam, w, label="Term included", color=CONTAM)

        probe = sub[(sub.spec == "contaminated")
                    & (sub.model == "Term-roundness probe (LEAKAGE)")]["auc"].iloc[0]
        ax.axhline(probe, color=PROBE, ls="--", lw=1.4)
        # Label sits low-left: the tall contaminated bars occupy the upper right.
        ax.text(-0.42, probe - 0.045,
                f"roundness probe alone ({probe:.3f})",
                fontsize=8, color=PROBE, ha="left", style="italic")

        ax.axhline(0.5, color="#cccccc", lw=1)
        ax.set_xticks(x)
        ax.set_xticklabels(short, fontsize=9)
        ax.set_ylim(0.3, 1.0)
        ax.set_title(f"{protocol} split", fontsize=11)
        ax.grid(axis="y", alpha=0.25)

    axes[0].set_ylabel("AUC")
    axes[0].legend(fontsize=8, loc="upper left")
    fig.suptitle(
        "Effect of the contaminated Term field on reported discrimination",
        fontsize=12)
    fig.tight_layout()
    fig.savefig(FIGURES / "leakage_inflation.png", dpi=200)
    print("  leakage_inflation.png")


def figure_within_year() -> None:
    """Roundness AUC by approval year - shows it is not a cohort artefact."""
    df = pd.read_csv(TABLES / "leakage_within_year.csv")

    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    ax.plot(df["year"], df["auc"], marker="o", color=CONTAM, lw=1.8)
    ax.axhline(0.5, color="#999999", ls="--", lw=1)
    ax.text(df["year"].min(), 0.515, "chance", fontsize=8, color="#777777")

    ax.set_ylim(0.45, 0.95)
    ax.set_xlabel("approval year")
    ax.set_ylabel("AUC of 'Term is a multiple of 12'")
    ax.set_title(
        "A variable with no economic meaning, predicting default in every year",
        fontsize=11)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "roundness_by_year.png", dpi=200)
    print("  roundness_by_year.png")


def figure_adjacent_terms() -> None:
    """The 60-month discontinuity."""
    df = pd.read_csv(TABLES / "leakage_adjacent_terms.csv")

    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    colours = [CLEAN if t % 12 == 0 else CONTAM for t in df["Term"]]
    ax.bar(df["Term"].astype(str), df["mean"] * 100, color=colours)

    for _, row in df.iterrows():
        ax.text(str(row["Term"]), row["mean"] * 100 + 2,
                f"{row['mean']*100:.0f}%", ha="center", fontsize=8)

    ax.set_xlabel("contractual term (months), 2007 approvals")
    ax.set_ylabel("default rate (%)")
    ax.set_ylim(0, 105)
    ax.set_title("A one-month difference in term, an eight-fold difference in default",
                 fontsize=11)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "adjacent_terms.png", dpi=200)
    print("  adjacent_terms.png")


def main() -> int:
    if not (TABLES / "benchmark_results.csv").exists():
        print("Missing result tables. Run benchmark.py and leakage_analysis.py first.")
        return 1

    FIGURES.mkdir(parents=True, exist_ok=True)
    print("Generating figures:")
    figure_inflation()
    figure_within_year()
    figure_adjacent_terms()

    # Mirror into the thesis results folder.
    dest = ROOT / "docs" / "05-results" / "figures"
    dest.mkdir(parents=True, exist_ok=True)
    import shutil
    for png in FIGURES.glob("*.png"):
        shutil.copy2(png, dest / png.name)
    print(f"\nCopied {len(list(FIGURES.glob('*.png')))} figures to docs/05-results/figures/")

    tdest = ROOT / "docs" / "05-results" / "tables"
    tdest.mkdir(parents=True, exist_ok=True)
    for f in TABLES.glob("*.csv"):
        shutil.copy2(f, tdest / f.name)
    for f in TABLES.glob("*.json"):
        shutil.copy2(f, tdest / f.name)
    print(f"Copied result tables to docs/05-results/tables/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
