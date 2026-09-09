"""Check that numbers quoted in the thesis match the generated result files.

Run:  python scripts/verify_claims.py

WHY THIS EXISTS
---------------
Every figure in the thesis is supposed to come from code in `research/`. Nothing
enforces that. Chapters are edited by hand, analyses are re-run with different
settings, and a number that was right in March quietly becomes wrong in
September while still reading perfectly well.

This script re-derives the load-bearing figures from
`research/outputs/tables/` and checks each against what the chapters actually
say. It has already earned its place: two values in Chapter 5 were wrong on
first drafting and were corrected against the generated tables.

Exit code 1 on any mismatch, so it can gate a build.
"""

from __future__ import annotations

import csv
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "research" / "outputs" / "tables"
CHAPTERS = ROOT / "docs" / "06-thesis"
PAPER = ROOT / "docs" / "07-paper" / "paper-term-contamination.md"


def load_csv(name: str) -> list[dict]:
    path = TABLES / name
    if not path.exists():
        return []
    with io.open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_json(name: str) -> dict:
    path = TABLES / name
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def documents() -> dict[str, str]:
    """The source chapters, the restructured sections, and the paper.

    Both copies of the thesis content are checked. The ch*.md chapters are the
    editable originals; the numbered 0N-*.md sections are generated from them by
    restructure_thesis.py and are what the submitted document is built from. If
    a chapter is edited without re-running the restructure, the two diverge and
    the submitted document silently carries stale numbers - so both are verified.
    """
    docs = {}
    for pattern in ("ch*.md", "0[0-9]-*.md"):
        for path in sorted(CHAPTERS.glob(pattern)):
            docs[path.name] = path.read_text(encoding="utf-8")
    if PAPER.exists():
        docs[PAPER.name] = PAPER.read_text(encoding="utf-8")
    return docs


def check_restructure_current() -> tuple[bool, str]:
    """Are the generated sections newer than the chapters they derive from?"""
    sources = list(CHAPTERS.glob("ch*.md"))
    generated = list(CHAPTERS.glob("0[1-9]-*.md"))
    if not sources or not generated:
        return True, "OK    restructure check skipped (files absent)"

    newest_source = max(p.stat().st_mtime for p in sources)
    oldest_generated = min(p.stat().st_mtime for p in generated)

    if newest_source > oldest_generated + 1:
        return False, ("FAIL  a source chapter is newer than the generated "
                       "sections - re-run restructure_thesis.py")
    return True, "OK    generated sections are current with source chapters"


def check(label: str, expected: str, docs: dict[str, str],
          required_in: list[str] | None = None) -> tuple[bool, str]:
    """Is `expected` present verbatim in the documents that should carry it?"""
    targets = required_in or list(docs)
    found = [name for name in targets if expected in docs.get(name, "")]

    if found:
        return True, f"OK    {label:<46} {expected:>10}  ({', '.join(found)})"
    return False, f"FAIL  {label:<46} {expected:>10}  not found in {targets}"


def main() -> int:
    docs = documents()
    if not docs:
        print("No chapters found.")
        return 1

    checks: list[tuple[bool, str]] = []

    # ---- leakage findings --------------------------------------------------
    leak = load_json("leakage_findings.json")
    if leak:
        checks.append(check("roundness AUC", f"{leak['roundness_auc']:.4f}", docs))
        checks.append(check("round share, repaid",
                            f"{leak['round_share_repaid'] * 100:.1f}%", docs))
        checks.append(check("round share, charged off",
                            f"{leak['round_share_default'] * 100:.1f}%", docs))
        checks.append(check("survival correlation",
                            f"{leak['survival_correlation']:.3f}", docs))
        checks.append(check("cohort size", f"{leak['n']:,}", docs))

    # ---- benchmark AUCs ----------------------------------------------------
    bench = load_csv("benchmark_results.csv")
    key_models = [
        ("clean", "temporal", "Gradient boosting"),
        ("clean", "random", "Gradient boosting"),
        ("contaminated", "temporal", "Gradient boosting"),
        ("contaminated", "random", "Gradient boosting"),
        ("clean", "temporal", "Logistic regression"),
        ("clean", "random", "Expert scorecard (unfitted)"),
        ("clean", "temporal", "Expert scorecard (unfitted)"),
    ]
    for spec, protocol, model in key_models:
        row = next((r for r in bench if r["spec"] == spec
                    and r["protocol"] == protocol and r["model"] == model), None)
        if row:
            checks.append(check(f"{model[:22]} {spec}/{protocol}",
                                f"{float(row['auc']):.4f}", docs))

    # ---- derived quantities ------------------------------------------------
    def auc(spec, protocol, model):
        r = next((x for x in bench if x["spec"] == spec
                  and x["protocol"] == protocol and x["model"] == model), None)
        return float(r["auc"]) if r else None

    if bench:
        gbm_c = auc("contaminated", "temporal", "Gradient boosting")
        gbm_k = auc("clean", "temporal", "Gradient boosting")
        if gbm_c and gbm_k:
            checks.append(check("leakage inflation (temporal)",
                                f"{gbm_c - gbm_k:.3f}", docs))

        rand_k = auc("clean", "random", "Gradient boosting")
        if rand_k and gbm_k:
            checks.append(check("random-split optimism",
                                f"{rand_k - gbm_k:.3f}", docs))

    # ---- weight sensitivity ------------------------------------------------
    sens = load_csv("weight_sensitivity.csv")
    for row in sens:
        if row["objective"] == "credit_risk" and float(row["perturbation"]) == 0.25:
            checks.append(check("weight sensitivity rho at +/-25%",
                                f"{float(row['spearman_mean']):.4f}", docs,
                                ["ch5-empirical-validation.md"]))
            checks.append(check("band stability at +/-25%",
                                f"{float(row['band_agreement_mean']) * 100:.1f}%", docs,
                                ["ch5-empirical-validation.md"]))

    # ---- objective separability (RQ4) --------------------------------------
    indep = load_json("objective_independence.json")
    if indep:
        checks.append(check("objectives Pearson r",
                            f"+{indep['pearson_r']:.4f}", docs,
                            ["ch5-empirical-validation.md"]))
        checks.append(check("disjoint-input r",
                            f"+{indep['disjoint_pearson_r']:.4f}", docs,
                            ["ch5-empirical-validation.md"]))
        checks.append(check("bands disagree",
                            f"{(1 - indep['band_same']) * 100:.1f}%", docs))
        checks.append(check("two or more bands apart",
                            f"{indep['band_two_plus_apart'] * 100:.1f}%", docs))

    # ---- calibration --------------------------------------------------------
    calib = load_csv("calibration.csv")
    for row in calib:
        if row["protocol"] == "temporal" and row["model"].startswith("Gradient"):
            checks.append(check("GBM temporal reliability",
                                f"{float(row['reliability']):.5f}", docs))
        if row["protocol"] == "random" and row["model"].startswith("Gradient"):
            checks.append(check("GBM random reliability",
                                f"{float(row['reliability']):.5f}", docs))

    # ---- model structure ---------------------------------------------------
    tree = json.loads(
        (ROOT / "shared" / "model" / "criteria-tree.json").read_text(encoding="utf-8")
    )
    n_criteria = sum(len(d["criteria"]) for o in tree["objectives"]
                     for d in o["dimensions"])
    n_dims = sum(len(o["dimensions"]) for o in tree["objectives"])
    checks.append(check("criteria count", str(n_criteria), docs))
    checks.append(check("dimension count", str(n_dims), docs))

    checks.append(check_restructure_current())

    # ---- placeholder-weight guard -----------------------------------------
    state = tree["weightStatus"]["state"]
    placeholder_claimed = any(
        "PLACEHOLDER" in text for text in docs.values()
    )
    if state == "PLACEHOLDER" and not placeholder_claimed:
        checks.append((False,
                       "FAIL  weights are PLACEHOLDER but no chapter says so"))
    elif state == "ELICITED" and placeholder_claimed:
        checks.append((False,
                       "FAIL  weights are ELICITED but a chapter still says PLACEHOLDER"))
    else:
        checks.append((True, f"OK    weight status consistent ({state})"))

    # ---- report ------------------------------------------------------------
    print("Verifying thesis claims against generated results")
    print("=" * 78)
    for ok, line in checks:
        print(line)

    failed = sum(1 for ok, _ in checks if not ok)
    print("=" * 78)

    if failed:
        print(f"{failed} of {len(checks)} checks FAILED.")
        print()
        print("A failure means a number in the thesis no longer matches the")
        print("result files. Either the analysis was re-run and the chapter is")
        print("stale, or the chapter was edited by hand. Fix the chapter — never")
        print("adjust this script to make it pass.")
        return 1

    print(f"All {len(checks)} checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
