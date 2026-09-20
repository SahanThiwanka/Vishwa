"""Generate Appendix 1 from the criteria model the system actually runs.

Run:  python scripts/gen_appendix_criteria.py

The appendix previously summarised the model by dimension - seven rows saying
how many criteria each dimension held. That is a description of the model, not
the model, and it leaves an examiner unable to check a single claim the thesis
makes about it. This writes the criteria themselves: every criterion, the clause
of the People's Bank form it derives from, how it is scored, and what it weighs.

It is generated rather than typed for the same reason every other number in the
thesis is. A hand-written appendix is correct on the day it is written and
silently wrong after the next weight elicitation; this one cannot disagree with
`shared/model/criteria-tree.json`, because it has no independent existence.

The section is rewritten in place, between its own heading and the next appendix
heading, so re-running after a model change is the whole update.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "shared" / "model" / "criteria-tree.json"
APPENDICES = ROOT / "docs" / "06-thesis" / "08-appendices.md"

# Codes keep the dimension column narrow enough that the criterion names, which
# are what the table is actually for, are not squeezed into two words a line.
CODES = {
    "Borrower & Management Capacity": "BMC",
    "Credit History & Banking Conduct": "CHB",
    "Historic Financial Performance": "HFP",
    "Project Viability & Projections": "PVP",
    "Market & Competitive Position": "MCP",
    "Risk, Security & Compliance": "RSC",
    "Economic & Social Contribution": "ESC",
}

UNITS = {
    "years": "years",
    "percent": "%",
    "percent_increase": "% increase",
    "ratio": "ratio",
    "count": "count",
    "times": "×",
    "days": "days",
}

DIRECTIONS = {
    "higher_better": "higher is better",
    "lower_better": "lower is better",
    "band_optimal": "an interior band is best",
}


def esc(text: str) -> str:
    """Escape what would otherwise be read as table or inline markup."""
    return text.replace("|", "\\|")


def anchors(criterion: dict) -> str:
    """The piecewise-linear anchors, as "value -> score" pairs.

    The unit is carried in its own column rather than repeated on every value:
    five repetitions widened the column for no information, and turned a band
    boundary of one year into "1 years".
    """
    return "; ".join(f"{value:g} → {score:g}"
                     for value, score in criterion["bands"])


def build() -> str:
    model = json.loads(MODEL.read_text(encoding="utf-8"))

    rows: list[str] = []
    quant: list[str] = []
    n = 0
    critical: list[str] = []

    for objective in model["objectives"]:
        for dimension in objective["dimensions"]:
            code = CODES.get(dimension["name"], dimension["name"][:3].upper())
            for criterion in dimension["criteria"]:
                n += 1
                # Within-objective weight: a criterion's share of its dimension,
                # scaled by that dimension's share of the objective. This is the
                # number that decides how much the criterion moves a score, and
                # the per-level weights alone do not show it.
                effective = dimension["weight"] * criterion["weight"] * 100
                name = esc(criterion["name"])
                if criterion.get("critical"):
                    # A word, not a dagger: a footnote symbol in a fifty-row
                    # table sends the reader looking for a footnote, and the
                    # marker has to survive extraction from the PDF.
                    name += " (critical)"
                    critical.append(criterion["name"])
                # "Measured" and "Judged" rather than "Quantitative" and
                # "Linguistic", which were long enough to hyphenate down the
                # column and leave every other row two lines deep.
                kind = ("Measured" if criterion["type"] == "quantitative"
                        else "Judged")
                rows.append(
                    f"| {n} | {code} | {name} | {esc(criterion['ref'])} | "
                    f"{kind} | {effective:.2f} |")

                if criterion["type"] == "quantitative":
                    quant.append(
                        f"| {n} | {esc(criterion['name'])} | "
                        f"{UNITS.get(criterion.get('unit'), '—')} | "
                        f"{DIRECTIONS.get(criterion.get('direction'), '—')} | "
                        f"{esc(anchors(criterion))} |")

    # Semicolons, because one of the dimension names contains a comma.
    legend = "; ".join(f"{c} {name}" for name, c in CODES.items())
    scale = model["linguisticScale"]
    levels = "; ".join(
        f"{lv['label']} [{', '.join(f'{x:g}' for x in lv['tfn'])}]"
        for lv in scale["levels"])

    qual_n = sum(1 for objective in model["objectives"]
                 for dimension in objective["dimensions"]
                 for criterion in dimension["criteria"]
                 if criterion["type"] == "qualitative")

    out = f"""## Appendix 1 The criteria model

The complete criteria model is held as a single machine-readable file, consumed
by both the decision-support system and the analysis pipeline, so that the model
described in this thesis and the model the system runs cannot diverge. This
appendix is generated from that file rather than transcribed from it, and so
cannot describe a model the system does not implement.

Every criterion records the clause of the People's Bank *Project / Business
Appraisal Report for SME Credit Facility* from which it derives.
@tbl:criteria-model-summary-objective summarises the model by objective and
dimension, and @tbl:criteria-model-full-listing then lists every criterion in it.

[Table: criteria-model-summary-objective | Criteria model summary by objective and dimension]

| Objective | Dimension | Criteria | Source clauses |
|---|---|---:|---|
"""
    for objective in model["objectives"]:
        for dimension in objective["dimensions"]:
            out += (f"| {objective['name']} | {dimension['name']} | "
                    f"{len(dimension['criteria'])} | {dimension['ref']} |\n")
    dims = sum(len(o["dimensions"]) for o in model["objectives"])
    out += f"| Total | {dims} dimensions | {n} | |\n"

    out += f"""
This table contains the seven dimensions of the model, the objective each
belongs to, the number of criteria it carries and the clauses of the source form
those criteria were derived from. {n - qual_n} criteria are quantitative and
{qual_n} qualitative.

### Appendix 1.1 The full criteria listing

@tbl:criteria-model-full-listing gives every criterion in the model. Dimensions
are abbreviated: {legend}.

[Table: criteria-model-full-listing | Every criterion in the model, with its source clause, input type and weight]

| # | Dim | Criterion | Clause | Input | Weight % |
|---:|---|---|---|---|---:|
"""
    out += "\n".join(rows) + "\n"

    out += f"""
This table contains all {n} criteria the system scores. For each it gives the
dimension it belongs to, the clause of the source form it derives from, whether
it takes a measured value or a judgement, and the weight it carries *within its
own objective* — that is, its share of its dimension multiplied by that
dimension's share of the objective, so the column sums to 100 for each objective
separately rather than across both. The weights are the elicited ones reported
in Section 6.1.4, not the equal weighting used during development. The one
criterion marked critical is evaluated on its raw value and surfaced separately,
so it cannot be averaged away by strong performance elsewhere.

### Appendix 1.2 Scoring anchors for the quantitative criteria

Quantitative criteria map to 0–100 by linear interpolation between the anchors
in @tbl:criteria-model-quantitative-anchors. Values below the lowest anchor take
the lowest score and values above the highest take the highest, so the mapping
is bounded at both ends. Linguistic criteria instead take one of five points,
represented as the triangular fuzzy numbers {levels}, and are defuzzified by
{scale['defuzzification']}.

[Table: criteria-model-quantitative-anchors | Scoring anchors for the quantitative criteria]

| # | Criterion | Unit | Direction | Anchors (value → score) |
|---:|---|---|---|---|
"""
    out += "\n".join(quant) + "\n"

    out += f"""
This table contains the band anchors for each of the {n - qual_n} quantitative
criteria, numbered as in @tbl:criteria-model-full-listing. The direction column
records whether a larger measured value improves or worsens the score, which is
not uniform: arrears and gearing score inversely, and one criterion is best in
an interior band rather than at either extreme. The anchors are design
assumptions, set from the thresholds the source form and Sri Lankan SME lending
practice already use, and Section 5.16 reports how far the model's output moves
when they and the weights are perturbed.

"""
    return out


def main() -> int:
    if not MODEL.exists():
        print(f"Missing model: {MODEL}")
        return 1

    text = APPENDICES.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^## Appendix 1 .*?(?=^## Appendix 2 )", re.M | re.S)
    if not pattern.search(text):
        print("Could not find the Appendix 1 block to replace.")
        return 1

    # A function replacement, because re.sub reads a backslash in a string
    # replacement as a group reference and the cells carry escaped pipes.
    generated = build()
    APPENDICES.write_text(pattern.sub(lambda _: generated, text),
                          encoding="utf-8")
    model = json.loads(MODEL.read_text(encoding="utf-8"))
    total = sum(len(d["criteria"]) for o in model["objectives"]
                for d in o["dimensions"])
    print(f"Appendix 1 regenerated from the model: {total} criteria listed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
