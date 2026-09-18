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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_style import (  # noqa: E402
    CHARGED_OFF, CLEAN, CONTAM, CREDIT, DEVELOPMENT, NEUTRAL, REPAID,
    apply_style, panel_label, year_axis,
)

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "research" / "outputs" / "tables"
FIGURES = ROOT / "research" / "outputs" / "figures"

PROBE = NEUTRAL


def figure_inflation() -> None:
    """Clean vs contaminated AUC, with the meaningless probe as a reference line."""
    df = pd.read_csv(TABLES / "benchmark_results.csv")

    models = ["Expert scorecard (unfitted)", "Logistic regression", "Gradient boosting"]
    short = ["Expert\nscorecard", "Logistic\nregression", "Gradient\nboosting"]

    fig, axes = plt.subplots(1, 2, figsize=(6.6, 3.1), sharey=True)

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
        panel_label(ax, f"{protocol.capitalize()} split")

    axes[0].set_ylabel("Area under the ROC curve")
    axes[0].legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(FIGURES / "leakage_inflation.png", dpi=200)
    print("  leakage_inflation.png")


def figure_within_year() -> None:
    """Roundness AUC by approval year - shows it is not a cohort artefact."""
    df = pd.read_csv(TABLES / "leakage_within_year.csv")

    fig, ax = plt.subplots(figsize=(6.3, 3.0))
    ax.plot(df["year"], df["auc"], marker="o", color=CONTAM, lw=1.8)
    ax.axhline(0.5, color="#999999", ls="--", lw=1)
    ax.text(df["year"].min(), 0.515, "chance", fontsize=8, color="#777777")

    ax.set_ylim(0.45, 0.95)
    ax.set_xlabel("Approval year")
    ax.set_ylabel("AUC of term roundness alone")
    year_axis(ax)
    fig.tight_layout()
    fig.savefig(FIGURES / "roundness_by_year.png", dpi=200)
    print("  roundness_by_year.png")


def figure_adjacent_terms() -> None:
    """The 60-month discontinuity."""
    df = pd.read_csv(TABLES / "leakage_adjacent_terms.csv")

    fig, ax = plt.subplots(figsize=(6.3, 3.2))
    colours = [CLEAN if t % 12 == 0 else CONTAM for t in df["Term"]]
    ax.bar(df["Term"].astype(str), df["mean"] * 100, color=colours)

    for pos, (_, row) in enumerate(df.iterrows()):
        ax.text(pos, row["mean"] * 100 + 2.5, f"{row['mean']*100:.0f}%",
                ha="center", va="bottom", fontsize=8)

    ax.set_xlabel("Contractual term (months)")
    ax.set_ylabel("Default rate (%)")
    ax.set_ylim(0, 105)
    fig.tight_layout()
    fig.savefig(FIGURES / "adjacent_terms.png", dpi=200)
    print("  adjacent_terms.png")


def figure_weight_sensitivity() -> None:
    """How far rankings and bands move as criterion weights are perturbed."""
    df = pd.read_csv(TABLES / "weight_sensitivity.csv")

    fig, axes = plt.subplots(1, 2, figsize=(6.6, 3.1))
    colours = {"credit_risk": CREDIT, "development_impact": DEVELOPMENT}
    names = {"credit_risk": "Credit risk",
             "development_impact": "Development impact"}

    for objective, group in df.groupby("objective"):
        g = group.sort_values("perturbation")
        x = g["perturbation"] * 100
        c = colours.get(objective, CONTAM)

        axes[0].plot(x, g["spearman_mean"], marker="o", color=c,
                     label=names.get(objective, objective))
        axes[0].fill_between(x, g["spearman_p05"], g["spearman_mean"],
                             color=c, alpha=0.15)

        axes[1].plot(x, g["band_agreement_mean"] * 100, marker="o", color=c,
                     label=names.get(objective, objective))
        axes[1].fill_between(x, g["band_agreement_p05"] * 100,
                             g["band_agreement_mean"] * 100, color=c, alpha=0.15)

    for ax, title, ylabel in [
        (axes[0], "Ranking stability", "Spearman correlation with baseline"),
        (axes[1], "Risk band stability", "Cases keeping their band (%)"),
    ]:
        # Mark the level of disagreement experts plausibly exhibit.
        ax.axvline(25, color="#999999", ls=":", lw=1.2)
        ax.text(26, ax.get_ylim()[0], " Plausible expert\n disagreement",
                fontsize=7.5, color="#777777", va="bottom")
        ax.set_xlabel("Weight perturbation (%)")
        ax.set_ylabel(ylabel)
        panel_label(ax, title)
        ax.legend()

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

    fig, axes = plt.subplots(1, 2, figsize=(6.6, 3.3), sharex=True, sharey=True)
    colours = {"Gradient boosting (clean)": CLEAN,
               "Logistic regression (clean)": CONTAM}

    for ax, protocol in zip(axes, ["random", "temporal"]):
        ax.plot([0, 1], [0, 1], ls="--", color="#999999", lw=1.2)
        ax.text(0.52, 0.46, "Perfect calibration", fontsize=7.5,
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
        ax.set_xlabel("Mean predicted probability of default")
        panel_label(ax, f"{protocol.capitalize()} split")
        ax.legend(fontsize=8.5, loc="upper left")

    axes[0].set_ylabel("Observed default rate")
    fig.tight_layout()
    fig.savefig(FIGURES / "calibration.png", dpi=200)
    print("  calibration.png")


def figure_missingness() -> None:
    """What withholding information does to the assessed risk of the same applicant.

    Left: mean predicted default as fields are withheld. Right: the share of the
    declined population that withholding converts into approvals. Both curves end
    at the same place - an applicant who supplies nothing is approved outright.
    """
    prog = pd.read_csv(TABLES / "missingness_progressive.csv")
    meta = json.loads((TABLES / "missingness_summary.json").read_text(encoding="utf-8"))

    styles = {
        "Gradient boosting (native NaN)": (CLEAN, "-", "Gradient boosting\n(native missing handling)"),
        "Logistic regression (median imputation)": (CONTAM, "--", "Logistic regression\n(median imputation)"),
    }

    fig, axes = plt.subplots(1, 2, figsize=(6.6, 3.3))

    for model, (colour, ls, label) in styles.items():
        sub = prog[prog["model"] == model].sort_values("fields_withheld")
        x = sub["fields_withheld"]

        axes[0].plot(x, sub["mean_p_default"], ls, color=colour, lw=2, label=label)
        axes[0].fill_between(x, sub["mean_p_low"], sub["mean_p_high"],
                             color=colour, alpha=0.15, lw=0)

        base = meta["models"][model]["baseline_mean_p"]
        # The thin line is the same model's assessment with nothing withheld.
        axes[0].axhline(base, color=colour, lw=0.9, alpha=0.5)

        axes[1].plot(x, sub["decline_to_approve"] * 100, ls, color=colour, lw=2,
                     label=label)

    axes[0].set_xlabel("Fields withheld (of 14)")
    axes[0].set_ylabel("Mean assessed probability of default")
    panel_label(axes[0], "Assessed risk")
    axes[0].set_ylim(0, None)
    axes[0].legend(loc="lower left")

    # The decline share is the ceiling: reaching it means every applicant who
    # would have been declined has been converted into an approval.
    ceiling = meta["decline_share"] * 100
    axes[1].axhline(ceiling, color=PROBE, ls=":", lw=1.4)
    # Bottom right: the curves occupy the upper left and converge on the ceiling.
    axes[1].text(len(prog["fields_withheld"].unique()) - 0.2, ceiling * 0.12,
                 "ceiling = every declined\napplicant now approved",
                 fontsize=8, color=PROBE, style="italic", ha="right")
    axes[1].set_xlabel("Fields withheld (of 14)")
    axes[1].set_ylabel("Share of all applicants (%)")
    panel_label(axes[1], "Declines converted to approvals")
    axes[1].set_ylim(0, ceiling * 1.15)

    fig.tight_layout()
    fig.savefig(FIGURES / "missingness.png", dpi=200)
    plt.close(fig)
    print("  missingness.png")


def figure_term_leakage() -> None:
    """Where the roundness sits, and what it does within each approval year.

    Moved here from leakage_analysis.py, which needs the 800 MB raw dataset to
    run. Both inputs are committed result tables, so every figure in the thesis
    can now be regenerated from the repository alone, and every figure is drawn
    under one style.
    """
    residue = pd.read_csv(TABLES / "leakage_residue_distribution.csv")
    within = pd.read_csv(TABLES / "leakage_within_year.csv")

    fig, axes = plt.subplots(1, 2, figsize=(6.6, 3.1))

    x = np.arange(len(residue))
    w = 0.4
    axes[0].bar(x - w / 2, residue["repaid"], w, label="Repaid", color=REPAID)
    axes[0].bar(x + w / 2, residue["charged_off"], w, label="Charged off",
                color=CHARGED_OFF)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(residue["Term"].astype(int))
    axes[0].set_xlabel("Term modulo 12 (months)")
    axes[0].set_ylabel("Share of facilities")
    axes[0].legend()
    panel_label(axes[0], "Where the terms fall")

    axes[1].plot(within["year"], within["default_round"] * 100, marker="o",
                 color=REPAID, label="Term a multiple of twelve")
    axes[1].plot(within["year"], within["default_irregular"] * 100, marker="s",
                 color=CHARGED_OFF, label="Irregular term")
    axes[1].set_xlabel("Approval year")
    axes[1].set_ylabel("Default rate (%)")
    year_axis(axes[1])
    axes[1].legend()
    panel_label(axes[1], "Default rate within each year")

    fig.tight_layout()
    fig.savefig(FIGURES / "term_leakage.png")
    plt.close(fig)
    print("  term_leakage.png")


def main() -> int:
    if not (TABLES / "benchmark_results.csv").exists():
        print("Missing result tables. Run benchmark.py and leakage_analysis.py first.")
        return 1

    FIGURES.mkdir(parents=True, exist_ok=True)
    apply_style()
    print("Generating figures:")
    figure_term_leakage()
    figure_inflation()
    figure_within_year()
    figure_adjacent_terms()
    if (TABLES / 'weight_sensitivity.csv').exists():
        figure_weight_sensitivity()
    if (TABLES / 'reliability_curves.csv').exists():
        figure_calibration()
    if (TABLES / 'missingness_progressive.csv').exists():
        figure_missingness()

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
