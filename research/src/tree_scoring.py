"""Score appraisals against the full 49-criterion tree, with configurable weights.

Separated from test_parity.py so the same scorer serves the parity check, the
weight sensitivity analysis, and anything else that needs the full model in
Python. The TypeScript engine remains the reference implementation; this mirrors
it and is checked against it by test_parity.py.

Weights are passed in rather than read from the tree, because the whole point of
the sensitivity analysis is to vary them.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
TREE_PATH = ROOT / "shared" / "model" / "criteria-tree.json"


def load_tree() -> dict:
    return json.loads(TREE_PATH.read_text(encoding="utf-8"))


def criterion_index(tree: dict) -> list[tuple[str, str, str]]:
    """Flat list of (objective_id, dimension_id, criterion_id) in tree order."""
    return [
        (o["id"], d["id"], c["id"])
        for o in tree["objectives"]
        for d in o["dimensions"]
        for c in d["criteria"]
    ]


def equal_weights(tree: dict) -> dict[str, np.ndarray]:
    """Equal weights within each level, matching the engine's placeholder behaviour.

    Returns a mapping from level key to a weight vector:
      "objective:<id>"  weights over that objective's dimensions
      "dimension:<id>"  weights over that dimension's criteria
    """
    weights: dict[str, np.ndarray] = {}
    for objective in tree["objectives"]:
        n = len(objective["dimensions"])
        weights[f"objective:{objective['id']}"] = np.full(n, 1.0 / n)
        for dimension in objective["dimensions"]:
            k = len(dimension["criteria"])
            weights[f"dimension:{dimension['id']}"] = np.full(k, 1.0 / k)
    return weights


def _band_score(value: float, bands: list[list[float]]) -> float:
    anchors = sorted(bands, key=lambda b: b[0])
    xp = np.array([a[0] for a in anchors], dtype=float)
    fp = np.array([a[1] for a in anchors], dtype=float)
    return float(np.clip(np.interp(value, xp, fp), 0, 100))


def score_matrix(cases: list[dict], tree: dict) -> dict[str, np.ndarray]:
    """Pre-compute each criterion's 0-100 score for every case.

    Criterion scores do not depend on weights, so computing them once and
    reusing across thousands of weight draws is what makes the Monte Carlo
    tractable. NaN marks a criterion that was not assessed.
    """
    levels = {lv["code"]: sum(lv["tfn"]) / 3.0 for lv in tree["linguisticScale"]["levels"]}

    out: dict[str, np.ndarray] = {}
    for _, _, cid in criterion_index(tree):
        out[cid] = np.full(len(cases), np.nan)

    lookup = {
        c["id"]: c
        for o in tree["objectives"]
        for d in o["dimensions"]
        for c in d["criteria"]
    }

    for i, case in enumerate(cases):
        for cid, raw in case.items():
            criterion = lookup.get(cid)
            if criterion is None or raw is None:
                continue
            if criterion["type"] == "qualitative":
                if raw in levels:
                    out[cid][i] = levels[raw]
            else:
                out[cid][i] = _band_score(float(raw), criterion["bands"])

    return out


def score_objectives(
    scores: dict[str, np.ndarray],
    tree: dict,
    weights: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Aggregate criterion scores to objective scores under the given weights.

    Missing criteria are excluded and weights renormalised over what remains,
    matching the engine. An objective with nothing assessed returns NaN rather
    than zero.
    """
    result: dict[str, np.ndarray] = {}

    for objective in tree["objectives"]:
        dim_scores, dim_weights = [], []

        for j, dimension in enumerate(objective["dimensions"]):
            cids = [c["id"] for c in dimension["criteria"]]
            block = np.vstack([scores[cid] for cid in cids])          # (k, n)
            w = weights[f"dimension:{dimension['id']}"][:, None]      # (k, 1)

            mask = ~np.isnan(block)
            wm = np.where(mask, w, 0.0)
            total = wm.sum(axis=0)

            with np.errstate(invalid="ignore", divide="ignore"):
                dim_score = np.where(
                    total > 0,
                    (np.nan_to_num(block) * wm).sum(axis=0) / total,
                    np.nan,
                )

            dim_scores.append(dim_score)
            dim_weights.append(weights[f"objective:{objective['id']}"][j])

        block = np.vstack(dim_scores)
        w = np.array(dim_weights)[:, None]

        mask = ~np.isnan(block)
        wm = np.where(mask, w, 0.0)
        total = wm.sum(axis=0)

        with np.errstate(invalid="ignore", divide="ignore"):
            result[objective["id"]] = np.where(
                total > 0,
                (np.nan_to_num(block) * wm).sum(axis=0) / total,
                np.nan,
            )

    return result


def risk_bands(scores: np.ndarray, tree: dict) -> np.ndarray:
    """Map scores to risk band codes. NaN scores become an empty string."""
    bands = sorted(tree["riskBands"], key=lambda b: b["min"])
    out = np.full(len(scores), "", dtype=object)
    for band in bands:
        hit = (~np.isnan(scores)) & (scores >= band["min"]) & (scores <= band["max"])
        out[hit] = band["code"]
    return out
