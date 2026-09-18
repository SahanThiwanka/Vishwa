# How this thesis must be written

The rules below are the standard every chapter is held to. Part A is taken from
*Thesis Preparation and Formatting Guidelines for Undergraduate and Postgraduate
Degree Programmes* (Senate approved), which is in the repository root. Part B is
ordinary research-writing convention that the guideline assumes without stating.
Part C records where the draft of 17 September 2026 broke these rules, with
counts, so the repair can be checked rather than believed.

Nothing here is a matter of taste. Each rule either comes from the guideline or
can be checked mechanically, and `scripts/verify_claims.py` enforces the ones
that can be automated.

---

## Part A — What the guideline requires

### A1 Structure, in this order

Title page, Declaration, Acknowledgement, Abstract, Table of Contents, List of
Figures, List of Tables, List of Abbreviations, Introduction, Objectives,
Literature Review, Methodology, Results, Discussion and Conclusions, References,
Appendices.

### A2 The two title pages are both required, and are not duplicates

Appendix I of the guideline specifies a **cover page**: title in capitals, bold,
16 pt; full name; degree; department; university; country; month and year.

Appendix II specifies an **inner title page**, which adds three things the cover
does not carry: the line *A thesis submitted to NSBM Green University for the
degree of*, the word *By* above the candidate's name, and the Faculty line
beneath the Department.

They look similar on purpose. The cover is what is printed on the binding; the
inner title page is the first page of the text block and counts as page i, with
the number suppressed.

### A3 Abstract

**200 to 300 words.** The guideline gives the shape explicitly:

| Part | Length |
|---|---|
| Background to the project | 1-2 sentences |
| Aims | 1 sentence |
| Methods | a few sentences |
| Results | a few sentences |
| Conclusions | 1-2 sentences |

Written last, after every other section is finished.

### A4 Pagination

Lower-case Roman from the inner title page, which is i and shows no number, so
the first number that appears is ii on the Declaration. Roman numbering ends
with the List of Abbreviations. Arabic numbering restarts at 1 on the first page
of the Introduction and continues to the end of the appendices. Page numbers sit
at the bottom centre. No running headers or footers of any other kind.

### A5 Headings

Arabic numerals to at most three decimals; anything deeper takes Roman numerals.

| Level | Example | Format |
|---|---|---|
| 1 | 1 INTRODUCTION | Bold capitals, 12 pt |
| 2 | 1.1 Justification | Bold, 12 pt |
| 3 | 1.2.1 General objective | Plain, 12 pt, first letter capitalised only |
| 4 | 2.3.1.1 Factors affecting synthesis | Plain, 12 pt, first letter capitalised only |

### A6 Page setup

A4. Margins 1 inch top, right and bottom; left 1 inch, or 1.25 inches to allow
for binding. Times New Roman 12 pt. Single column. 1.5 line spacing throughout.

### A7 Tables and figures

* Table captions **above** the table. Figure captions **below** the figure. Both
  12 pt.
* Numbered `Section.Sequence`: Table 2.1 is the first table in Section 2,
  Figure 1.2 the second figure in Section 1.
* No shading in table cells.
* Each must appear **as close as possible to its first mention in the text**,
  which presupposes that it is mentioned in the text.
* Every figure and every table carries a caption, and both are listed with their
  page numbers in the List of Figures and the List of Tables.

### A8 Abbreviations

Listed **in alphabetical order** with their full meanings, and **explained in
the text at first use**. Both halves are required; the list does not discharge
the obligation to expand the term where the reader first meets it.

### A9 What each chapter is for

| Chapter | The guideline's words |
|---|---|
| Introduction | Background; why the area is worth investigating; an overview of research already carried out; the gaps in knowledge; ending with the research questions |
| Objectives | The general and the specific objectives |
| Literature Review | Key theories and concepts; major studies and their findings; gaps, key debates, and areas of disagreement or conflicting results; closing by linking the literature to the research question |
| Methodology | Enough detail for another researcher to replicate the study accurately |
| Results | A logical sequence of tables and figures summarising the findings, organised as a results story, **without attempting to interpret them** |
| Discussion and Conclusions | Analysis of the findings against the study's rationale and the literature; limitations and their effect on validity; implications for theory, research and practice; future studies; and conclusions that are not a summary |
| References | Starting on a fresh page, in Vancouver, APA or IEEE style |
| Appendices | After the references, each one numbered, all listed in the Table of Contents, pagination continuing |

---

## Part B — Conventions the guideline assumes

### B1 A thesis is read by someone who does not have the repository

No file paths, script names, directory names or shell commands anywhere in the
body. `python research/src/bwm.py` tells an examiner nothing they can act on and
reads as a note the author forgot to remove. Where the point is that a result is
reproducible, the prose says what was checked and the appendix lists the
analyses by name.

Dataset field names are part of the subject matter and stay, but they are set in
*italics*, not in a code font: the *Term* field, not `Term`. A monospace font in
the middle of a Times New Roman paragraph is a typographic error in a thesis.

Internal engineering vocabulary does not appear at all: no `weightStatus`, no
`dimension:borrower_management`, no `ELICITED`.

### B2 Every table and figure is introduced, referred to by number, and read for the reader

The guideline's own worked example (its Appendix VIII) shows the required
pattern:

> A total of 110 pregnant women were recruited (Figure 4.1) at the booking
> visit, and socio-economic characteristics are shown in Table 5.1. There was no
> significant difference in the ethnic distribution among the studied women.

Three things happen there. The exhibit is named by number. The sentence says
what it contains. The sentences after it state what the reader should take from
it. A table dropped into the page after a colon, with nothing before or after
it, fails all three.

The rule applied here:

1. Refer to the exhibit by number in the sentence that introduces it.
2. Follow it with at least one sentence stating what it shows.
3. If nothing can be said about an exhibit, it does not belong in the thesis.

### B3 Figures are part of the typography

* No title inside the image. The caption below it is the title; an embedded one
  repeats it in the wrong typeface.
* Axis labels in sentence case, with units.
* A year axis shows 1990, not 1990.0.
* Legend entries are written in prose: "Credit risk", not `credit_risk`.
* The same series means the same colour in every figure in the thesis.
* Tick labels are not rotated unless they genuinely do not fit.
* Anything drawn on the plot that is not data, such as a reference line, is
  explained in the legend or the caption.

### B4 Emphasis, tense and number

* Bold is for headings and for a run-in heading that opens a paragraph. It is
  never used to emphasise a word or a result in running prose; if a result needs
  emphasis, it goes at the end of the sentence.
* Past tense for what was done and what was found. Present tense for what is
  generally true, and for what the thesis itself does.
* A quantity is reported to the same number of decimal places every time it
  appears.
* Punctuation earns its place: an em dash is correct when the phrase it encloses
  already contains commas, and a comma, colon or full stop is correct otherwise.

### B5 Nothing appears that only the author can act on

No notes to self, no "before submission", no unresolved placeholders. A
statement about what a later study should do belongs in Future Work, phrased as
a recommendation.

---

## Part C — What the 17 September draft violated

Measured, not estimated.

| # | Rule | Violation found |
|---|---|---|
| 1 | A3 | Abstract ran to **584 words** against a 200-300 limit, in six paragraphs |
| 2 | B2 | **Not one** of the 32 tables and 7 figures was referred to by number anywhere in the text |
| 3 | A8 | **16 of 18** abbreviations were never expanded at first use |
| 4 | B1 | **45 distinct** file paths, script names and shell commands appeared in the body |
| 5 | B1 | Dataset fields and internal state names were set in a monospace code font |
| 6 | B3 | Figures carried embedded titles duplicating their captions |
| 7 | B3 | The approval-year axis read 1990.0, 1992.5, 1995.0 |
| 8 | B3 | Legends read `credit_risk` and `development_impact` |
| 9 | B3 | Four different colour schemes across seven figures |
| 10 | A9 | Chapter 5 interprets its results throughout, which the guideline reserves for Chapter 6 |

Item 10 is the one judgement call in this list. The finding in Chapter 5 is a
chain: each experiment exists because the previous one ruled something out, and
stripping the reasoning out would leave a sequence of tables an examiner cannot
follow. The thesis therefore keeps the reasoning that makes the next experiment
intelligible in Chapter 5, and defers every claim about what the findings *mean*
for practice, theory and the literature to Chapter 6. Section 5.1 states that
this is what it does, so the departure is declared and not accidental.

---

## Part D — Checks that run automatically

`scripts/verify_claims.py` fails the build on:

* a source heading without a section number;
* a cross-reference to a section that does not exist;
* a generated section number that is out of sequence;
* a drafted section missing from the generated document;
* any figure quoted in the text that does not match the analysis output;
* an abstract outside 200-300 words;
* a table or figure never referred to in the text;
* an abbreviation used before it is expanded;
* a file path, script name or shell command in the body.

The last four were added when this standard was written.
