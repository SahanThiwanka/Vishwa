"""Verify the TypeScript and Python scoring engines agree.

Run:  python research/src/test_parity.py

WHY THIS EXISTS
---------------
The scoring method is implemented twice: TypeScript for the deployed system,
Python for the thesis analysis. That is a genuine hazard. If the two drift apart,
the thesis could report numbers produced by one implementation while demonstrating
a system running the other, and nothing would surface the discrepancy.

This script generates random appraisals, scores them through both engines, and
fails loudly on any disagreement beyond floating-point tolerance.

Both engines read the same `shared/model/criteria-tree.json`, so a divergence here
means the *logic* has drifted, not the model.
"""

from __future__ import annotations

import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fuzzy_scorecard import score_from_bands  # noqa: E402

import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
TREE_PATH = ROOT / "shared" / "model" / "criteria-tree.json"
WEB = ROOT / "web"

TOLERANCE = 0.15  # both engines round to 1 dp independently
N_CASES = 40
LINGUISTIC = ["VP", "P", "F", "G", "E"]


def load_tree() -> dict:
    return json.loads(TREE_PATH.read_text(encoding="utf-8"))


def generate_cases(tree: dict, n: int, seed: int = 7) -> list[dict]:
    """Random appraisals, including deliberately sparse ones.

    Sparsity matters: it exercises weight renormalisation and the completeness
    gate, which is where two implementations are most likely to disagree.
    """
    rng = random.Random(seed)
    criteria = [
        c for o in tree["objectives"] for d in o["dimensions"] for c in d["criteria"]
    ]

    cases = []
    for i in range(n):
        # Vary how much of the file is filled in, from very sparse to complete.
        fill = [1.0, 0.85, 0.6, 0.35, 0.12][i % 5]
        case: dict = {}

        for criterion in criteria:
            if rng.random() > fill:
                continue

            if criterion["type"] == "qualitative":
                case[criterion["id"]] = rng.choice(LINGUISTIC)
            else:
                bands = criterion["bands"]
                lo = min(b[0] for b in bands)
                hi = max(b[0] for b in bands)
                span = hi - lo
                # Deliberately sample outside the anchor range too, to check that
                # both engines clamp identically.
                value = rng.uniform(lo - 0.2 * span, hi + 0.2 * span)
                case[criterion["id"]] = round(value, 4)

        cases.append(case)

    return cases


def score_python(cases: list[dict], tree: dict) -> list[dict]:
    """Python implementation of criteria-tree scoring."""
    levels = {lv["code"]: lv["tfn"] for lv in tree["linguisticScale"]["levels"]}
    min_complete = tree["completenessPolicy"]["minObjectiveCompleteness"]

    out = []
    for case in cases:
        objectives = []
        total_criteria = 0
        total_assessed = 0
        breaches = []

        for objective in tree["objectives"]:
            dim_results = []

            for dimension in objective["dimensions"]:
                scores, n_assessed = [], 0

                for criterion in dimension["criteria"]:
                    total_criteria += 1
                    raw = case.get(criterion["id"])
                    if raw is None:
                        continue

                    if criterion["type"] == "qualitative":
                        tfn = levels[raw]
                        score = sum(tfn) / 3.0
                    else:
                        score = float(
                            score_from_bands(pd.Series([raw]), criterion["bands"]).iloc[0]
                        )
                        # Critical breach judged on the RAW value, matching the
                        # TypeScript engine: threshold is the first anchor
                        # scoring >= 25.
                        if criterion.get("critical"):
                            anchor = next(
                                (b[0] for b in criterion["bands"] if b[1] >= 25), 0
                            )
                            if raw < anchor:
                                breaches.append(criterion["id"])

                    scores.append(round(score, 1))
                    n_assessed += 1
                    total_assessed += 1

                # Equal weights within a dimension, renormalised over assessed.
                dim_score = round(float(np.mean(scores)), 1) if scores else None
                dim_results.append({
                    "id": dimension["id"],
                    "score": dim_score,
                    "completeness": n_assessed / len(dimension["criteria"]),
                })

            scored = [d for d in dim_results if d["score"] is not None]
            obj_score = round(float(np.mean([d["score"] for d in scored])), 1) if scored else None

            n_obj_criteria = sum(len(d["criteria"]) for d in objective["dimensions"])
            n_obj_assessed = sum(
                1 for d in objective["dimensions"] for c in d["criteria"]
                if case.get(c["id"]) is not None
            )
            completeness = n_obj_assessed / n_obj_criteria if n_obj_criteria else 0.0

            objectives.append({
                "id": objective["id"],
                "score": obj_score,
                "completeness": completeness,
                "sufficient": completeness >= min_complete,
                "dimensions": dim_results,
            })

        out.append({
            "objectives": objectives,
            "overallCompleteness": total_assessed / total_criteria if total_criteria else 0.0,
            "criticalBreaches": sorted(breaches),
        })

    return out


def main() -> int:
    tree = load_tree()
    cases = generate_cases(tree, N_CASES)
    print(f"Generated {len(cases)} random appraisals from model v{tree['version']}")

    tmp = Path(tempfile.mkdtemp())
    in_path, out_path = tmp / "cases.json", tmp / "ts.json"
    in_path.write_text(json.dumps(cases), encoding="utf-8")

    print("Scoring with the TypeScript engine ...")
    proc = subprocess.run(
        ["npx", "tsx", "scripts/score-cases.ts", str(in_path), str(out_path)],
        cwd=WEB, capture_output=True, text=True, shell=(sys.platform == "win32"),
    )
    if proc.returncode != 0:
        print("TypeScript engine failed:")
        print(proc.stdout[-2000:])
        print(proc.stderr[-2000:])
        return 1

    ts_results = json.loads(out_path.read_text(encoding="utf-8"))
    py_results = score_python(cases, tree)

    print("Comparing ...\n")

    failures = []
    for i, (ts, py) in enumerate(zip(ts_results, py_results)):
        for ts_obj, py_obj in zip(ts["objectives"], py["objectives"]):
            a, b = ts_obj["score"], py_obj["score"]
            if (a is None) != (b is None):
                failures.append(f"case {i} {ts_obj['id']}: TS={a} PY={b} (null mismatch)")
            elif a is not None and abs(a - b) > TOLERANCE:
                failures.append(f"case {i} {ts_obj['id']}: TS={a} PY={b} (diff {abs(a-b):.3f})")

            if ts_obj["sufficient"] != py_obj["sufficient"]:
                failures.append(
                    f"case {i} {ts_obj['id']}: completeness gate disagrees "
                    f"(TS={ts_obj['sufficient']} PY={py_obj['sufficient']})"
                )

            if abs(ts_obj["completeness"] - py_obj["completeness"]) > 1e-6:
                failures.append(
                    f"case {i} {ts_obj['id']}: completeness "
                    f"TS={ts_obj['completeness']:.4f} PY={py_obj['completeness']:.4f}"
                )

        if sorted(ts["criticalBreaches"]) != py["criticalBreaches"]:
            failures.append(
                f"case {i}: critical breaches differ "
                f"TS={sorted(ts['criticalBreaches'])} PY={py['criticalBreaches']}"
            )

    n_checks = len(cases) * (len(tree["objectives"]) * 3 + 1)
    if failures:
        print(f"PARITY FAILED - {len(failures)} disagreement(s) across {n_checks} checks:\n")
        for f in failures[:25]:
            print(f"  {f}")
        if len(failures) > 25:
            print(f"  ... and {len(failures) - 25} more")
        return 1

    scored = sum(
        1 for r in ts_results for o in r["objectives"] if o["score"] is not None
    )
    gated = sum(
        1 for r in ts_results for o in r["objectives"] if not o["sufficient"]
    )
    breaches = sum(len(r["criticalBreaches"]) for r in ts_results)

    print(f"PARITY OK - {n_checks} checks across {len(cases)} cases")
    print(f"  objective scores compared : {scored}")
    print(f"  gated as insufficient     : {gated}")
    print(f"  critical breaches matched : {breaches}")
    print("\nThe TypeScript and Python engines agree.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
