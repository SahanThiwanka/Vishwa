"""Convert the thesis sections from author-date to IEEE numbered referencing.

Run:  python scripts/to_ieee.py     (after restructure_thesis.py)

The NSBM guideline permits Vancouver, APA or IEEE as specified by the faculty.
IEEE was chosen, which means:

  * citations are bracketed numbers, [1], [2], assigned in order of FIRST
    appearance reading the thesis front to back;
  * the reference list is ordered by that number, not alphabetically;
  * entries use IEEE style - initials before surname, title in quotes, journal
    in italics, volume/number/pages/year.

Why this runs on the generated sections rather than the source chapters: the
numbers depend on reading order, and reading order is decided by the
restructure. Keeping the ch*.md chapters in author-date form also keeps them
readable while drafting, which bracketed numbers do not.

Pipeline:  restructure_thesis.py  ->  to_ieee.py  ->  build_thesis_nsbm.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "docs" / "06-thesis"

# Sections in reading order. Numbering follows this sequence.
# Numbering starts at the Introduction. The front matter carries no numbered
# citations: an abstract and an acknowledgement that referred to "[1]" would be
# both unconventional and, since they precede the reference list, unreadable.
ORDER = [
    "01-introduction.md",
    "02-objectives.md",
    "03-literature-review.md",
    "04-methodology.md",
    "05-results.md",
    "06-discussion-conclusions.md",
    "08-appendices.md",
]

# key -> (surname alternatives for in-text matching, year, IEEE entry)
REFERENCES: dict[str, tuple[tuple[str, ...], str, str]] = {
    "altman1968": (
        ("Altman",), "1968",
        'E. I. Altman, "Financial ratios, discriminant analysis and the '
        'prediction of corporate bankruptcy," *Journal of Finance*, vol. 23, '
        "no. 4, pp. 589-609, 1968."),
    "ohlson1980": (
        ("Ohlson",), "1980",
        'J. A. Ohlson, "Financial ratios and the probabilistic prediction of '
        'bankruptcy," *Journal of Accounting Research*, vol. 18, no. 1, '
        "pp. 109-131, 1980."),
    "handhenley1997": (
        ("Hand and Henley", "Hand & Henley", "Hand"), "1997",
        'D. J. Hand and W. E. Henley, "Statistical classification methods in '
        'consumer credit scoring: a review," *Journal of the Royal Statistical '
        "Society Series A*, vol. 160, no. 3, pp. 523-541, 1997."),
    "thomas1992": (
        ("Thomas, Crook and Edelman",), "1992",
        "L. C. Thomas, J. N. Crook and D. B. Edelman, *Credit Scoring and "
        "Credit Control*. Oxford, U.K.: Clarendon Press, 1992."),
    "thomas2002": (
        ("Thomas, Edelman and Crook",), "2002",
        "L. C. Thomas, D. B. Edelman and J. N. Crook, *Credit Scoring and its "
        "Applications*. Philadelphia, PA: SIAM, 2002."),
    "lessmann2015": (
        ("Lessmann et al.", "Lessmann"), "2015",
        'S. Lessmann, B. Baesens, H.-V. Seow and L. C. Thomas, "Benchmarking '
        "state-of-the-art classification algorithms for credit scoring: an "
        'update of research," *European Journal of Operational Research*, '
        "vol. 247, no. 1, pp. 124-136, 2015."),
    "ciampi2021": (
        ("Ciampi, Giannozzi, Marzi and Altman", "Ciampi et al.", "Ciampi"),
        "2021",
        'F. Ciampi, A. Giannozzi, G. Marzi and E. I. Altman, "Rethinking SME '
        'default prediction: a systematic literature review and future '
        'perspectives," *Scientometrics*, vol. 126, pp. 2141-2188, 2021.'),
    "beck2006": (
        ("Beck and Demirgüç-Kunt", "Beck and Demirguc-Kunt", "Beck"), "2006",
        'T. Beck and A. Demirgüç-Kunt, "Small and medium-size enterprises: '
        'access to finance as a growth constraint," *Journal of Banking & '
        "Finance*, vol. 30, no. 11, pp. 2931-2943, 2006."),
    "berger2006": (
        ("Berger and Udell", "Berger"), "2006",
        'A. N. Berger and G. F. Udell, "A more complete conceptual framework '
        'for SME finance," *Journal of Banking & Finance*, vol. 30, no. 11, '
        "pp. 2945-2966, 2006."),
    "stein2002": (
        ("Stein",), "2002",
        'J. C. Stein, "Information production and capital allocation: '
        'decentralized versus hierarchical firms," *Journal of Finance*, '
        "vol. 57, no. 5, pp. 1891-1921, 2002."),
    "cortes2016": (
        ("Cortés, Duchin and Sosyura", "Cortes, Duchin and Sosyura",
         "Cortés et al.", "Cortes et al.", "Cortés", "Cortes"), "2016",
        'K. R. Cortés, R. Duchin and D. Sosyura, "Clouded judgment: the role '
        'of sentiment in credit origination," *Journal of Financial '
        "Economics*, vol. 121, no. 2, pp. 392-413, 2016."),
    "sharafeldin2025": (
        ("SharafEldin, Idrees and Ouf", "SharafEldin et al.", "SharafEldin"),
        "2025",
        'M. A. SharafEldin, A. M. Idrees and S. Ouf, "A proposed framework for '
        'loan default prediction using machine learning techniques," '
        "*International Journal of Advanced Computer Science and "
        "Applications*, vol. 16, no. 6, pp. 412-425, 2025."),
    "zadeh1965": (
        ("Zadeh",), "1965",
        'L. A. Zadeh, "Fuzzy sets," *Information and Control*, vol. 8, no. 3, '
        "pp. 338-353, 1965."),
    "saaty1980": (
        ("Saaty",), "1980",
        "T. L. Saaty, *The Analytic Hierarchy Process*. New York, NY: "
        "McGraw-Hill, 1980."),
    "saaty1990": (
        ("Saaty",), "1990",
        'T. L. Saaty, "An exposition of the AHP in reply to the paper '
        "'Remarks on the Analytic Hierarchy Process',\" *Management Science*, "
        "vol. 36, no. 3, pp. 259-268, 1990."),
    "chang1996": (
        ("Chang",), "1996",
        'D.-Y. Chang, "Applications of the extent analysis method on fuzzy '
        'AHP," *European Journal of Operational Research*, vol. 95, no. 3, '
        "pp. 649-655, 1996."),
    "chen2000": (
        ("Chen",), "2000",
        'C.-T. Chen, "Extensions of the TOPSIS for group decision-making '
        'under fuzzy environment," *Fuzzy Sets and Systems*, vol. 114, no. 1, '
        "pp. 1-9, 2000."),
    "rezaei2015": (
        ("Rezaei",), "2015",
        'J. Rezaei, "Best-worst multi-criteria decision-making method," '
        "*Omega*, vol. 53, pp. 49-57, 2015."),
    "rezaei2016": (
        ("Rezaei",), "2016",
        'J. Rezaei, "Best-worst multi-criteria decision-making method: some '
        'properties and a linear model," *Omega*, vol. 64, pp. 126-130, 2016.'),
    "roy2021": (
        ("Roy and Shaw", "Roy"), "2021",
        'P. K. Roy and K. Shaw, "A multicriteria credit scoring model for SMEs '
        'using hybrid BWM and TOPSIS," *Financial Innovation*, vol. 7, no. 1, '
        "2021."),
    "gutierrez2016": (
        ("Gutiérrez-Nieto, Serrano-Cinca and Camón-Cala",
         "Gutierrez-Nieto, Serrano-Cinca and Camon-Cala",
         "Gutiérrez-Nieto et al.", "Gutierrez-Nieto et al.",
         "Gutiérrez-Nieto", "Gutierrez-Nieto"), "2016",
        'B. Gutiérrez-Nieto, C. Serrano-Cinca and J. Camón-Cala, "A credit '
        'score system for socially responsible lending," *Journal of Business '
        "Ethics*, vol. 133, no. 4, pp. 691-701, 2016."),
    "arvanitis2015": (
        ("Arvanitis, Stampini and Vencatachellum", "Arvanitis et al.",
         "Arvanitis"), "2015",
        'Y. Arvanitis, M. Stampini and D. Vencatachellum, "Balancing '
        "development returns and credit risks: project appraisal in a "
        'multilateral development bank," *Impact Assessment and Project '
        "Appraisal*, vol. 33, no. 3, pp. 195-206, 2015."),
    "ribeiro2016": (
        ("Ribeiro, Singh and Guestrin", "Ribeiro et al.", "Ribeiro"), "2016",
        'M. T. Ribeiro, S. Singh and C. Guestrin, "\'Why should I trust '
        "you?': explaining the predictions of any classifier,\" in *Proc. 22nd "
        "ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining*, 2016, "
        "pp. 1135-1144."),
    "lundberg2017": (
        ("Lundberg and Lee", "Lundberg"), "2017",
        'S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting '
        'model predictions," in *Advances in Neural Information Processing '
        "Systems 30*, 2017, pp. 4765-4774."),
    "kapoor2023": (
        ("Kapoor and Narayanan", "Kapoor"), "2023",
        'S. Kapoor and A. Narayanan, "Leakage and the reproducibility crisis '
        'in machine-learning-based science," *Patterns*, vol. 4, no. 9, '
        "art. 100804, 2023."),
    "li2018": (
        ("Li, Mickel and Taylor", "Li et al.", "Li"), "2018",
        "M. Li, A. Mickel and S. Taylor, \"'Should this loan be approved or "
        "denied?': a large dataset with class assignment guidelines,\" "
        "*Journal of Statistics Education*, vol. 26, no. 1, pp. 55-66, 2018."),
    "delong1988": (
        ("DeLong, DeLong and Clarke-Pearson", "DeLong et al.", "DeLong"),
        "1988",
        'E. R. DeLong, D. M. DeLong and D. L. Clarke-Pearson, "Comparing the '
        "areas under two or more correlated receiver operating characteristic "
        'curves: a nonparametric approach," *Biometrics*, vol. 44, no. 3, '
        "pp. 837-845, 1988."),
    "hanley1982": (
        ("Hanley and McNeil", "Hanley"), "1982",
        'J. A. Hanley and B. J. McNeil, "The meaning and use of the area under '
        'a receiver operating characteristic (ROC) curve," *Radiology*, '
        "vol. 143, no. 1, pp. 29-36, 1982."),
    "brier1950": (
        ("Brier",), "1950",
        'G. W. Brier, "Verification of forecasts expressed in terms of '
        'probability," *Monthly Weather Review*, vol. 78, no. 1, pp. 1-3, '
        "1950."),
    "murphy1973": (
        ("Murphy",), "1973",
        'A. H. Murphy, "A new vector partition of the probability score," '
        "*Journal of Applied Meteorology*, vol. 12, no. 4, pp. 595-600, 1973."),
    "cohen1960": (
        ("Cohen",), "1960",
        'J. Cohen, "A coefficient of agreement for nominal scales," '
        "*Educational and Psychological Measurement*, vol. 20, no. 1, "
        "pp. 37-46, 1960."),
    "landis1977": (
        ("Landis and Koch", "Landis"), "1977",
        'J. R. Landis and G. G. Koch, "The measurement of observer agreement '
        'for categorical data," *Biometrics*, vol. 33, no. 1, pp. 159-174, '
        "1977."),
    "hevner2004": (
        ("Hevner, March, Park and Ram", "Hevner et al.", "Hevner"), "2004",
        'A. R. Hevner, S. T. March, J. Park and S. Ram, "Design science in '
        'information systems research," *MIS Quarterly*, vol. 28, no. 1, '
        "pp. 75-105, 2004."),
    "peffers2007": (
        ("Peffers et al.", "Peffers"), "2007",
        'K. Peffers, T. Tuunanen, M. A. Rothenberger and S. Chatterjee, "A '
        "design science research methodology for information systems "
        'research," *Journal of Management Information Systems*, vol. 24, '
        "no. 3, pp. 45-77, 2007."),
    "davis1989": (
        ("Davis",), "1989",
        'F. D. Davis, "Perceived usefulness, perceived ease of use, and user '
        'acceptance of information technology," *MIS Quarterly*, vol. 13, '
        "no. 3, pp. 319-340, 1989."),
    "brooke1996": (
        ("Brooke",), "1996",
        'J. Brooke, "SUS: a \'quick and dirty\' usability scale," in *Usability '
        "Evaluation in Industry*, P. W. Jordan et al., Eds. London, U.K.: "
        "Taylor & Francis, 1996, pp. 189-194."),
    # The source of the sector statistics quoted in the Introduction. Cited so
    # that those figures carry a primary attribution rather than the "widely
    # reported" hedge they had while the draft was being written.
    "moic2015": (
        ("Ministry of Industry and Commerce",), "2015",
        "Ministry of Industry and Commerce, *National Policy Framework for "
        "Small and Medium Enterprise (SME) Development*. Colombo, Sri Lanka: "
        "Government of Sri Lanka, 2015."),
}


def citation_patterns(names: tuple[str, ...], year: str) -> list[re.Pattern]:
    """Regexes matching the author-date forms used in the draft.

    Author lists are wrapped across lines in the source, so a literal escape of
    "DeLong, DeLong and Clarke-Pearson" fails against "DeLong, DeLong and

    Clarke-Pearson". Every run of whitespace inside a name is therefore matched
    flexibly.
    """
    pats = []
    for name in names:
        n = r"\s+".join(re.escape(part) for part in name.split())
        # "(Author, 2016)" and "(Author 2016)"
        pats.append(re.compile(rf"\(\s*{n},?\s+{year}\s*\)"))
        # "Author (2016)" -> keep the name, replace the year
        pats.append(re.compile(rf"(?<![\w-]){n}\s+\({year}\)"))
        # bare "Author, 2016" inside a longer parenthetical
        pats.append(re.compile(rf"(?<![\w-]){n},\s+{year}(?![\d)])"))
    return pats


def main() -> int:
    missing = [n for n in ORDER if not (CH / n).exists()]
    if missing:
        print("Missing sections: " + ", ".join(missing))
        print("Run restructure_thesis.py first.")
        return 1

    texts = {n: (CH / n).read_text(encoding="utf-8") for n in ORDER}

    # ---- assign numbers in order of first appearance -----------------------
    assigned: dict[str, int] = {}
    next_number = 1

    for name in ORDER:
        text = texts[name]
        # Walk the text once, recording the earliest position of each reference
        # so numbering follows reading order rather than dictionary order.
        positions: list[tuple[int, str]] = []
        for key, (names, year, _) in REFERENCES.items():
            if key in assigned:
                continue
            earliest = None
            for pat in citation_patterns(names, year):
                m = pat.search(text)
                if m and (earliest is None or m.start() < earliest):
                    earliest = m.start()
            if earliest is not None:
                positions.append((earliest, key))

        for _, key in sorted(positions):
            assigned[key] = next_number
            next_number += 1

    # ---- rewrite citations -------------------------------------------------
    replaced = 0
    for name in ORDER:
        text = texts[name]
        for key, number in assigned.items():
            names, year, _ = REFERENCES[key]
            for pat in citation_patterns(names, year):
                def sub(m: re.Match) -> str:
                    nonlocal replaced
                    replaced += 1
                    raw = m.group(0)
                    # "Author (2016)" keeps the name: "Author [12]"
                    if raw.endswith(")") and not raw.startswith("("):
                        return re.sub(rf"\({year}\)$", f"[{number}]", raw)
                    return f"[{number}]"
                text = pat.sub(sub, text)
        (CH / name).write_text(text, encoding="utf-8")
        texts[name] = text

    # ---- regenerate the reference list in citation order -------------------
    ordered = sorted(assigned.items(), key=lambda kv: kv[1])
    lines = [
        "# REFERENCES",
        "",
        "References are numbered in order of first citation, following IEEE "
        "style. Sources located through a database search whose full text has "
        "not been obtained are recorded as such in the accompanying "
        "bibliography (docs/02-literature/bibliography.md) rather than "
        "concealed here.",
        "",
    ]
    for key, number in ordered:
        lines.append(f"[{number}] {REFERENCES[key][2]}")
        lines.append("")

    uncited = [k for k in REFERENCES if k not in assigned]
    if uncited:
        lines.append("")
        lines.append("<!-- Not cited in the text, so omitted from the "
                     "numbered list per IEEE practice: "
                     + ", ".join(sorted(uncited)) + " -->")

    (CH / "07-references.md").write_text("\n".join(lines).rstrip() + "\n",
                                         encoding="utf-8")

    print(f"Converted to IEEE numbering:")
    print(f"  {replaced} in-text citations rewritten")
    print(f"  {len(assigned)} references numbered by first appearance")
    if uncited:
        print(f"  {len(uncited)} defined but never cited, omitted from the list:")
        for k in sorted(uncited):
            print(f"      {k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
