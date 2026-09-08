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


def figure_weight_sensitivity() -> None:
    """How far rankings and bands move as criterion weights are perturbed."""
    df = pd.read_csv(TABLES / "weight_sensitivity.csv")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    colours = {"credit_risk": CLEAN, "development_impact": "#7a4fa3"}

    for objective, group in df.groupby("objective"):
        g = group.sort_values("perturbation")
        x = g["perturbation"] * 100
        c = colours.get(objective, CONTAM)

        axes[0].plot(x, g["spearman_mean"], marker="o", color=c, label=objective)
        axes[0].fill_between(x, g["spearman_p05"], g["spearman_mean"],
                             color=c, alpha=0.15)

        axes[1].plot(x, g["band_agreement_mean"] * 100, marker="o", color=c,
                     label=objective)
        axes[1].fill_between(x, g["band_agreement_p05"] * 100,
                             g["band_agreement_mean"] * 100, color=c, alpha=0.15)

    for ax, title, ylabel in [
        (axes[0], "Ranking stability", "Spearman rho vs baseline"),
        (axes[1], "Risk band stability", "% of cases keeping their band"),
    ]:
        # Mark the level of disagreement experts plausibly exhibit.
        ax.axvline(25, color="#999999", ls=":", lw=1.2)
        ax.text(26, ax.get_ylim()[0], " plausible expert\n disagreement",
                fontsize=7.5, color="#777777", va="bottom")
        ax.set_xlabel("weight perturbation (%)")
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontsize=11)
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8)

    fig.suptitle("Sensitivity of model output to criterion weights "
                 "(2,000 simulated appraisals, 400 draws per level)", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIGURES / "weight_sensitivity.png", dpi=200)
    print("  weight_sensitivity.png")


def figure_calibration() -> None:
    """Reliability diagrams: does a predicted probability mean what it says?

    AUC measures ranking only. A bank pricing risk needs the predicted
    probability to be right in level as well as in order, and these two panels
    show that a model well calibrated under random splitting can be badly
    miscalibrated on a later period.
    """
    df = pd.read_csv(TABLES / "reliability_curves.csv")
    summary = pd.read_csv(TABLES / "calibration.csv")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharex=True, sharey=True)
    colours = {"Gradient boosting (clean)": CLEAN,
               "Logistic regression (clean)": "#c07a2a"}

    for ax, protocol in zip(axes, ["random", "temporal"]):
        ax.plot([0, 1], [0, 1], ls="--", color="#999999", lw=1.2)
        ax.text(0.52, 0.46, "perfect calibration", fontsize=7.5,
                color="#777777", rotation=38)

        sub = df[df["protocol"] == protocol]
        for model, group in sub.groupby("model"):
            g = group.sort_values("mean_predicted")
            # Marker area tracks how many cases sit in each bin, so sparsely
            # populated bins are not read as strongly as dense ones.
            sizes = 18 + 90 * (g["n"] / g["n"].max())
            c = colours.get(model, CONTAM)
            ax.plot(g["mean_predicted"], g["observed_rate"], color=c, lw=1.5,
                    zorder=2)
            ax.scatter(g["mean_predicted"], g["observed_rate"], s=sizes,
                       color=c, zorder=3, label=model.replace(" (clean)", ""))

            row = summary[(summary.protocol == protocol) &
                          (summary.model == model)]
            if not row.empty:
                ax.plot([], [], " ",
                        label=f"   reliability {row.iloc[0]['reliability']:.5f}")

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel("mean predicted probability of default")
        ax.set_title(f"{protocol} split", fontsize=11)
        ax.grid(alpha=0.25)
        ax.legend(fontsize=7.5, loc="upper left")

    axes[0].set_ylabel("observed default rate")
    fig.suptitle("Calibration: predicted vs observed default rate "
                 "(lower reliability is better)", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIGURES / "calibration.png", dpi=200)
    print("  calibration.png")


def main() -> int:
    if not (TABLES / "benchmark_results.csv").exists():
        print("Missing result tables. Run benchmark.py and leakage_analysis.py first.")
        return 1

    FIGURES.mkdir(parents=True, exist_ok=True)
    print("Generating figures:")
    figure_inflation()
    figure_within_year()
    figure_adjacent_terms()
    if (TABLES / 'weight_sensitivity.csv').exists():
        figure_weight_sensitivity()
    if (TABLES / 'reliability_curves.csv').exists():
        figure_calibration()

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
