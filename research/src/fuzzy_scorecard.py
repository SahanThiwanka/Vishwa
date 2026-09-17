"""Vectorised fuzzy scorecard scoring, mirroring the TypeScript engine in web/.

Two implementations of the same method exist on purpose: TypeScript for the
product, Python for the empirical work. `test_parity.py` checks they agree, which
guards against the thesis reporting numbers from one implementation while the
demonstrated system uses another.

    ~~~ HONEST NOTE ON THE FUZZY LAYER ~~~

Every SBA-observable criterion is quantitative, so each input enters as a
degenerate triangular fuzzy number [x, x, x]. Centroid defuzzification of a
degenerate TFN returns x, and the fuzzy weighted average therefore reduces
EXACTLY to an ordinary weighted arithmetic mean.

In other words: on this dataset the fuzzy machinery does no work. It is exercised
only by qualitative criteria, which the SBA data does not contain. The thesis must
say this plainly rather than implying that "a fuzzy model was validated". What is
validated here is the band-mapping and weighted-aggregation structure.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def load_scorecard(name: str = "sba-validation-scorecard.json") -> dict:
    with open(ROOT / "shared" / "model" / name, encoding="utf-8") as fh:
        return json.load(fh)


def score_from_bands(values: pd.Series, bands: list[list[float]]) -> pd.Series:
    """Piecewise-linear map from raw value to 0-100, clamped at both ends.

    np.interp clamps to the endpoint values outside the anchor range, which is the
    behaviour the TypeScript engine implements explicitly.
    """
    anchors = sorted(bands, key=lambda b: b[0])
    xp = np.array([a[0] for a in anchors], dtype=float)
    fp = np.array([a[1] for a in anchors], dtype=float)

    raw = pd.to_numeric(values, errors="coerce").to_numpy(dtype=float)
    out = np.interp(raw, xp, fp)
    out = np.clip(out, 0, 100)
    out[np.isnan(raw)] = np.nan
    return pd.Series(out, index=values.index)


def _weighted_mean_ignoring_nan(frame: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    """Weighted mean that renormalises over non-missing entries per row.

    A missing criterion is excluded, never treated as zero - the same rule the
    TypeScript engine applies. Rows with nothing assessed return NaN.
    """
    values = frame.to_numpy(dtype=float)
    mask = ~np.isnan(values)

    w = np.broadcast_to(weights, values.shape) * mask
    total = w.sum(axis=1)

    filled = np.where(mask, values, 0.0)
    numerator = (filled * w).sum(axis=1)

    with np.errstate(invalid="ignore", divide="ignore"):
        result = np.where(total > 0, numerator / total, np.nan)

    return pd.Series(result, index=frame.index)


def score_objective(
    df: pd.DataFrame,
    scorecard: dict,
    objective_id: str,
    column_map: dict[str, str],
) -> tuple[pd.Series, pd.DataFrame]:
    """Score one objective. Returns (objective score, per-criterion scores)."""
    objective = next(
        o for o in scorecard["objectives"] if o["id"] == objective_id
    )

    dimension_scores: dict[str, pd.Series] = {}
    criterion_scores: dict[str, pd.Series] = {}

    def _weights_for(nodes: list[dict], present) -> np.ndarray:
        """Weights for the nodes actually present, renormalised to sum to one.

        Reads `weight` from the criteria tree, which derive_weights.py writes
        after elicitation. Falls back to equal weighting for any node without
        one, so the scorecard still runs against a PLACEHOLDER tree.

        This used to hardcode equal weights with a comment saying elicitation
        was outstanding. When elicitation completed, every scored result stayed
        exactly as it had been - the weights were written into the tree and the
        analysis silently ignored them. A hardcoded constant standing in for
        data is fine until the data arrives; the danger is that nothing fails
        when it does.
        """
        by_id = {n["id"]: n for n in nodes}
        raw = np.array(
            [float(by_id[i].get("weight") or 0.0) for i in present],
            dtype=float,
        )
        if raw.sum() <= 0:
            return np.full(len(present), 1.0 / len(present))
        return raw / raw.sum()

    for dimension in objective["dimensions"]:
        per_criterion = {}

        for criterion in dimension["criteria"]:
            source = column_map.get(criterion["id"], criterion["id"])
            if source not in df.columns:
                raise KeyError(
                    f"criterion '{criterion['id']}' expects column '{source}', "
                    f"which is not in the dataframe"
                )
            scored = score_from_bands(df[source], criterion["bands"])
            per_criterion[criterion["id"]] = scored
            criterion_scores[criterion["id"]] = scored

        block = pd.DataFrame(per_criterion)
        weights = _weights_for(dimension["criteria"], block.columns)
        dimension_scores[dimension["id"]] = _weighted_mean_ignoring_nan(block, weights)

    dim_frame = pd.DataFrame(dimension_scores)
    dim_weights = _weights_for(objective["dimensions"], dim_frame.columns)
    objective_score = _weighted_mean_ignoring_nan(dim_frame, dim_weights)

    return objective_score, pd.DataFrame(criterion_scores)


# Maps scorecard criterion ids onto prepared dataframe columns.
SBA_COLUMN_MAP = {
    "sba_guarantee_share": "sba_guarantee_share",
    "is_established": "is_established",
    "employees": "NoEmp",
    "loan_per_employee": "loan_per_employee",
    "has_franchise": "has_franchise",
    "rev_line_of_credit": "rev_line_of_credit",
    "disbursement_ratio": "disbursement_ratio",
    "low_doc_program": "low_doc_program",
    "jobs_supported": "jobs_supported",
    "jobs_per_100k": "jobs_per_100k",
    "job_creation_rate": "job_creation_rate",
}


def add_scorecard_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Attach credit-risk and development-impact scores to a prepared frame."""
    df = df.copy()
    df["is_established"] = 1 - df["is_new_business"]

    scorecard = load_scorecard()

    credit, _ = score_objective(df, scorecard, "credit_risk", SBA_COLUMN_MAP)
    development, _ = score_objective(
        df, scorecard, "development_impact", SBA_COLUMN_MAP
    )

    df["scorecard_credit_risk"] = credit
    df["scorecard_development"] = development
    return df
