"""One visual style for every figure in the thesis.

WHY THIS EXISTS
---------------
The seven figures were written at different times and looked it. Between them
they used four colour schemes, so the same series was blue in one figure and
green in the next; three carried a title inside the image that repeated the
caption printed underneath it; the axis labels alternated between sentence case
and lower case; one year axis read 1990.0, 1992.5, 1995.0; and two legends
printed the column names out of the data file, `credit_risk` and
`development_impact`, rather than words.

A figure in a thesis is typography as much as it is data. It sits inside a
Times New Roman page and is introduced by a numbered caption, so it should not
announce its own title in a sans-serif face, and a reader should be able to tell
at a glance that two figures showing the same quantity are showing the same
quantity.

USAGE
-----
    from figure_style import apply_style, CREDIT, DEVELOPMENT, year_axis

    apply_style()          # once, before any figure is built
"""

from __future__ import annotations

import matplotlib
from matplotlib.ticker import MaxNLocator

# Series colours. Each meaning keeps its colour across every figure.
CLEAN = "#2b6ca3"        # a model with the contaminated field excluded
CONTAM = "#b3382c"       # the same model with it included
CREDIT = "#2b6ca3"       # the credit-risk objective
DEVELOPMENT = "#7a4fa3"  # the development-impact objective
REPAID = "#2b6ca3"       # facilities repaid in full
CHARGED_OFF = "#b3382c"  # facilities charged off
NEUTRAL = "#6f6f6f"      # reference lines, annotations, anything not data
FAINT = "#cfcfcf"


def apply_style() -> None:
    """Set the rcParams every figure in the thesis is drawn under."""
    matplotlib.rcParams.update({
        # Times New Roman, so a figure does not change typeface mid-page.
        # DejaVu stays as the fallback on machines without the Microsoft fonts.
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
        "mathtext.fontset": "stix",

        "font.size": 9,
        "axes.titlesize": 9.5,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,

        # A thesis figure is captioned, not titled, and the page around it is
        # white, so the frame can be lighter than matplotlib's default.
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#555555",
        "axes.grid": True,
        "grid.color": "#dddddd",
        "grid.linewidth": 0.6,
        "axes.axisbelow": True,

        "legend.frameon": False,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.bbox": "tight",
        "savefig.dpi": 200,
    })


def year_axis(ax) -> None:
    """Whole years on the x axis.

    A year is not a continuous quantity, and matplotlib's default locator was
    labelling the approval-year axis 1990.0, 1992.5, 1995.0.
    """
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=8))
    ax.xaxis.set_major_formatter(lambda v, _pos: f"{int(v)}")


def panel_label(ax, text: str) -> None:
    """A short neutral label for one panel of a multi-panel figure.

    Neutral is the point. A panel headed "Assessed risk falls as information is
    withheld" states the finding twice, once here and once in the caption, and
    the reader is entitled to reach it themselves.
    """
    ax.set_title(text, fontsize=10, pad=8)
