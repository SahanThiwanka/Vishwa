"""Draw the conceptual architecture of the model in one figure.

Run:  python research/src/make_architecture_figure.py

An examiner meeting this thesis has to hold seven things at once before any
result means anything: that the criteria come from a real bank form, that two
kinds of input travel one scoring path, that the weights were elicited rather
than assumed, that the two objectives are never added together, and that two
gates sit between a score and a recommendation. Chapter 4 establishes all of
that, at length and correctly, but not at a glance.

The counts are read from the criteria model rather than written here, so the
figure cannot claim a model the system does not implement.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_style import CREDIT, DEVELOPMENT, NEUTRAL, apply_style  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "shared" / "model" / "criteria-tree.json"
FIGURES = ROOT / "research" / "outputs" / "figures"
THESIS_FIGURES = ROOT / "docs" / "05-results" / "figures"

INK = "#333333"
BOX_EDGE = "#777777"
BOX_FILL = "#f4f4f4"


def box(ax, x, y, w, h, text, *, fill=BOX_FILL, edge=BOX_EDGE, weight="normal",
        size=8.2):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02",
        linewidth=0.9, edgecolor=edge, facecolor=fill, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=size, color=INK, zorder=3, linespacing=1.45,
            fontweight=weight)


def arrow(ax, start, end, *, colour=NEUTRAL):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=9, linewidth=0.9,
        color=colour, shrinkA=1, shrinkB=1, zorder=1))


def main() -> int:
    if not MODEL.exists():
        print(f"Missing model: {MODEL}")
        return 1
    model = json.loads(MODEL.read_text(encoding="utf-8"))

    n_criteria = sum(len(d["criteria"]) for o in model["objectives"]
                     for d in o["dimensions"])
    n_dimensions = sum(len(o["dimensions"]) for o in model["objectives"])
    n_quant = sum(1 for o in model["objectives"] for d in o["dimensions"]
                  for c in d["criteria"] if c["type"] == "quantitative")
    n_qual = n_criteria - n_quant
    n_levels = len(model["linguisticScale"]["levels"])
    floor = int(model["completenessPolicy"]["minObjectiveCompleteness"] * 100)
    respondents = model["weightStatus"]["elicitation"]["respondents"]

    credit, development = model["objectives"][0], model["objectives"][1]

    apply_style()
    fig, ax = plt.subplots(figsize=(6.4, 6.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # 1. the source instrument
    box(ax, 0.22, 0.925, 0.56, 0.062,
        "People's Bank SME appraisal form\n(Annexure I–V, clauses 2–6)",
        weight="bold")

    # 2. formalisation
    arrow(ax, (0.5, 0.925), (0.5, 0.878))
    box(ax, 0.17, 0.815, 0.66, 0.062,
        f"Clause-by-clause derivation\n{n_criteria} criteria in {n_dimensions} "
        "dimensions, each carrying its source clause")

    # 3. the two input paths
    arrow(ax, (0.36, 0.815), (0.30, 0.762))
    arrow(ax, (0.64, 0.815), (0.70, 0.762))
    box(ax, 0.055, 0.688, 0.40, 0.072,
        f"{n_quant} quantitative criteria\nPiecewise-linear band\nanchors → 0–100")
    box(ax, 0.545, 0.688, 0.40, 0.072,
        f"{n_qual} qualitative criteria\n{n_levels}-point scale as triangular\n"
        "fuzzy numbers → centroid")

    # 4. one aggregation path, with the elicited weights entering from the left
    arrow(ax, (0.255, 0.688), (0.46, 0.638))
    arrow(ax, (0.745, 0.688), (0.72, 0.638))
    box(ax, 0.295, 0.568, 0.66, 0.070,
        "Fuzzy weighted average over one scoring path\n"
        "Unassessed criteria excluded, weights renormalised")
    box(ax, 0.015, 0.561, 0.235, 0.084,
        f"Best-Worst Method\n{respondents} practitioners\n"
        "Weights per level", edge=NEUTRAL, fill="#ffffff")
    arrow(ax, (0.250, 0.603), (0.295, 0.603))

    # 5. the two objectives, scored and banded separately
    arrow(ax, (0.50, 0.568), (0.34, 0.505))
    arrow(ax, (0.76, 0.568), (0.80, 0.505))
    box(ax, 0.10, 0.428, 0.32, 0.077,
        f"Credit risk\n{len(credit['dimensions'])} dimensions",
        edge=CREDIT, fill="#eef4fa", weight="bold")
    box(ax, 0.64, 0.428, 0.34, 0.077,
        f"Development impact\n{len(development['dimensions'])} dimension",
        edge=DEVELOPMENT, fill="#f4eefa", weight="bold")
    ax.text(0.53, 0.466, "never\nsummed", ha="center", va="center",
            fontsize=7.6, color="#b3382c", style="italic", linespacing=1.3)

    # 6. the two gates, which both objectives pass through
    arrow(ax, (0.26, 0.428), (0.36, 0.378))
    arrow(ax, (0.81, 0.428), (0.64, 0.378))
    box(ax, 0.145, 0.288, 0.71, 0.088,
        f"Completeness gate — below {floor}% assessed, the score is shown but\n"
        "no band and no recommendation are issued\n"
        "Critical criteria — evaluated on raw values and surfaced separately",
        edge="#b3382c", fill="#fbf0ef")

    # 8. explanation
    arrow(ax, (0.5, 0.288), (0.5, 0.235))
    box(ax, 0.145, 0.145, 0.71, 0.088,
        "Per-criterion contribution in points of the objective score,\n"
        "summing exactly to it, each labelled with its source clause\n"
        "Risk band and recommended action")

    # 9. the artefact the bank receives
    arrow(ax, (0.5, 0.145), (0.5, 0.092))
    box(ax, 0.235, 0.028, 0.53, 0.062,
        "Appraisal report in the bank's own format,\nwith its sign-off chain",
        weight="bold")

    FIGURES.mkdir(parents=True, exist_ok=True)
    out = FIGURES / "conceptual_architecture.png"
    fig.savefig(out, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    THESIS_FIGURES.mkdir(parents=True, exist_ok=True)
    (THESIS_FIGURES / "conceptual-architecture.png").write_bytes(
        out.read_bytes())
    print(f"Wrote {out.relative_to(ROOT)}")
    print(f"  and docs/05-results/figures/conceptual-architecture.png")
    print(f"  {n_criteria} criteria, {n_dimensions} dimensions, "
          f"{respondents} respondents, {floor}% floor - all read from the model")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
