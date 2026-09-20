# APPENDICES

## Appendix 1 The criteria model

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
| Credit Risk / Bankability | Borrower & Management Capacity | 6 | 2.8, 2.10, 3.2, 3.4 |
| Credit Risk / Bankability | Credit History & Banking Conduct | 5 | 2.11, 2.14 |
| Credit Risk / Bankability | Historic Financial Performance | 9 | 2.13, 2.15-2.18 |
| Credit Risk / Bankability | Project Viability & Projections | 8 | 3.1.3, 3.7, 4 |
| Credit Risk / Bankability | Market & Competitive Position | 7 | 3.10 |
| Credit Risk / Bankability | Risk, Security & Compliance | 6 | 3.3, 3.5, 3.6, 3.11, 3.12, 6.5 |
| Development Impact | Economic & Social Contribution | 8 | 5, 3.4.1 |
| Total | 7 dimensions | 49 | |

This table contains the seven dimensions of the model, the objective each
belongs to, the number of criteria it carries and the clauses of the source form
those criteria were derived from. 28 criteria are quantitative and
21 qualitative.

### Appendix 1.1 The full criteria listing

@tbl:criteria-model-full-listing gives every criterion in the model. Dimensions
are abbreviated: BMC Borrower & Management Capacity; CHB Credit History & Banking Conduct; HFP Historic Financial Performance; PVP Project Viability & Projections; MCP Market & Competitive Position; RSC Risk, Security & Compliance; ESC Economic & Social Contribution.

[Table: criteria-model-full-listing | Every criterion in the model, with its source clause, input type and weight]

| # | Dim | Criterion | Clause | Input | Weight % |
|---:|---|---|---|---|---:|
| 1 | BMC | Sponsor experience in the field | 2.10 | Measured | 4.71 |
| 2 | BMC | Educational/professional qualifications | 2.8 | Judged | 2.69 |
| 3 | BMC | Organizational structure & management style | 3.2 | Judged | 5.48 |
| 4 | BMC | HR adequacy & succession depth | 3.4 | Judged | 3.39 |
| 5 | BMC | EPF/ETF payment compliance | 3.4.2 | Judged | 2.87 |
| 6 | BMC | Years since business commenced | 2.3 | Measured | 2.77 |
| 7 | CHB | Repayment performance on prior facilities | 2.11.1, 2.11.2 | Judged | 3.44 |
| 8 | CHB | Arrears as % of outstanding | 2.11 | Measured | 1.67 |
| 9 | CHB | Credit turnover through account vs. sales | 2.14.1 | Measured | 5.96 |
| 10 | CHB | Cheque returns on refer-to-drawer | 2.14.1 | Measured | 2.98 |
| 11 | CHB | Exposure to other financial institutions | 2.11.2 | Judged | 1.90 |
| 12 | HFP | Gross profit ratio | 2.17 | Measured | 0.70 |
| 13 | HFP | Net profit ratio | 2.17 | Measured | 1.33 |
| 14 | HFP | Current ratio | 2.17 | Measured | 1.60 |
| 15 | HFP | Debt-equity ratio | 2.17 | Measured | 1.30 |
| 16 | HFP | Gearing ratio | 2.17 | Measured | 1.26 |
| 17 | HFP | Asset turnover ratio | 2.17 | Measured | 1.07 |
| 18 | HFP | Stock retention period | 2.17 | Measured | 1.23 |
| 19 | HFP | Debtors retention period | 2.17 | Measured | 1.26 |
| 20 | HFP | Sales trend & stability | 2.13 | Judged | 0.97 |
| 21 | PVP | Debt service cover ratio (critical) | 4 | Measured | 4.96 |
| 22 | PVP | Interest service cover ratio | 4 | Measured | 2.55 |
| 23 | PVP | Return on investment | 4 | Measured | 3.34 |
| 24 | PVP | Projected net profit ratio | 4 | Measured | 3.43 |
| 25 | PVP | Project debt-equity ratio | 3.7.1 | Measured | 3.64 |
| 26 | PVP | Promoter equity contribution | 3.7 | Measured | 3.28 |
| 27 | PVP | Growth in production capacity | 3.1.3 | Measured | 3.23 |
| 28 | PVP | Headroom above break-even | 4 | Measured | 2.55 |
| 29 | MCP | Rivalry among competing sellers | 3.10.3 | Judged | 2.40 |
| 30 | MCP | Competitive force of potential entry | 3.10.3 | Judged | 2.12 |
| 31 | MCP | Power of buyers | 3.10.3 | Judged | 2.39 |
| 32 | MCP | Power of suppliers | 3.10.3 | Judged | 1.77 |
| 33 | MCP | Pressure from substitute products | 3.10.3 | Judged | 1.84 |
| 34 | MCP | Security of raw material supply | 3.10.2 | Judged | 2.27 |
| 35 | MCP | Distribution arrangements | 3.10.4 | Judged | 1.43 |
| 36 | RSC | Security cover (FSV / facility amount) | 6.5 | Measured | 2.21 |
| 37 | RSC | Technological risk | 3.11 | Judged | 1.90 |
| 38 | RSC | Environmental risk | 3.12 | Judged | 1.45 |
| 39 | RSC | Government approvals obtained & current | 3.6 | Judged | 1.59 |
| 40 | RSC | Insurance coverage adequacy | 3.3 | Judged | 1.60 |
| 41 | RSC | Realism of implementation schedule | 3.5 | Judged | 1.48 |
| 42 | ESC | Employment generation (manpower before/after) | 5.1, 3.4.1 | Measured | 12.48 |
| 43 | ESC | Women's participation in workforce | 5.2, 3.4.1 | Measured | 5.57 |
| 44 | ESC | Local raw material usage | 5.3 | Measured | 15.61 |
| 45 | ESC | Increase in productive capacity | 5.4, 5.5 | Measured | 15.77 |
| 46 | ESC | Export sales as % of turnover | 5.6 | Measured | 11.58 |
| 47 | ESC | Import substitution effect | 5.7 | Judged | 11.11 |
| 48 | ESC | Value added | 5.8 | Measured | 12.31 |
| 49 | ESC | Foreign exchange earnings | 5.9 | Judged | 15.57 |

This table contains all 49 criteria the system scores. For each it gives the
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
represented as the triangular fuzzy numbers Very Poor [0, 0, 25]; Poor [0, 25, 50]; Fair [25, 50, 75]; Good [50, 75, 100]; Excellent [75, 100, 100], and are defuzzified by
centroid.

[Table: criteria-model-quantitative-anchors | Scoring anchors for the quantitative criteria]

| # | Criterion | Unit | Direction | Anchors (value → score) |
|---:|---|---|---|---|
| 1 | Sponsor experience in the field | years | higher is better | 0 → 0; 2 → 25; 5 → 50; 10 → 75; 15 → 100 |
| 6 | Years since business commenced | years | higher is better | 0 → 0; 1 → 25; 3 → 50; 5 → 75; 10 → 100 |
| 8 | Arrears as % of outstanding | % | lower is better | 0 → 100; 2 → 75; 5 → 50; 10 → 25; 20 → 0 |
| 9 | Credit turnover through account vs. sales | ratio | higher is better | 0 → 0; 0.25 → 25; 0.5 → 50; 0.75 → 75; 1 → 100 |
| 10 | Cheque returns on refer-to-drawer | count | lower is better | 0 → 100; 1 → 75; 3 → 50; 6 → 25; 12 → 0 |
| 12 | Gross profit ratio | % | higher is better | 0 → 0; 10 → 25; 20 → 50; 30 → 75; 45 → 100 |
| 13 | Net profit ratio | % | higher is better | 0 → 0; 3 → 25; 7 → 50; 12 → 75; 20 → 100 |
| 14 | Current ratio | ratio | an interior band is best | 0.5 → 0; 1 → 40; 1.33 → 70; 2 → 100; 3.5 → 70 |
| 15 | Debt-equity ratio | ratio | lower is better | 0.5 → 100; 1 → 80; 2 → 55; 3 → 30; 4 → 0 |
| 16 | Gearing ratio | % | lower is better | 20 → 100; 40 → 75; 60 → 50; 75 → 25; 90 → 0 |
| 17 | Asset turnover ratio | × | higher is better | 0 → 0; 0.5 → 25; 1 → 50; 2 → 75; 3 → 100 |
| 18 | Stock retention period | days | lower is better | 15 → 100; 30 → 80; 60 → 55; 90 → 30; 150 → 0 |
| 19 | Debtors retention period | days | lower is better | 15 → 100; 30 → 80; 60 → 55; 90 → 30; 150 → 0 |
| 21 | Debt service cover ratio | × | higher is better | 0.8 → 0; 1 → 25; 1.25 → 50; 1.5 → 75; 2 → 100 |
| 22 | Interest service cover ratio | × | higher is better | 1 → 0; 1.5 → 25; 2 → 50; 3 → 75; 4 → 100 |
| 23 | Return on investment | % | higher is better | 0 → 0; 8 → 25; 15 → 50; 25 → 75; 35 → 100 |
| 24 | Projected net profit ratio | % | higher is better | 0 → 0; 3 → 25; 7 → 50; 12 → 75; 20 → 100 |
| 25 | Project debt-equity ratio | ratio | lower is better | 0.5 → 100; 1 → 80; 1.5 → 60; 2.33 → 35; 4 → 0 |
| 26 | Promoter equity contribution | % | higher is better | 10 → 0; 20 → 35; 30 → 60; 40 → 80; 50 → 100 |
| 27 | Growth in production capacity | % | higher is better | 0 → 0; 15 → 25; 35 → 50; 60 → 75; 100 → 100 |
| 28 | Headroom above break-even | % | higher is better | 0 → 0; 10 → 25; 25 → 50; 40 → 75; 60 → 100 |
| 36 | Security cover (FSV / facility amount) | ratio | higher is better | 0.5 → 0; 0.8 → 30; 1 → 55; 1.5 → 80; 2 → 100 |
| 42 | Employment generation (manpower before/after) | % increase | higher is better | 0 → 0; 10 → 25; 25 → 50; 50 → 75; 100 → 100 |
| 43 | Women's participation in workforce | % | higher is better | 0 → 0; 10 → 25; 25 → 50; 40 → 75; 50 → 100 |
| 44 | Local raw material usage | % | higher is better | 0 → 0; 25 → 25; 50 → 50; 75 → 75; 100 → 100 |
| 45 | Increase in productive capacity | % increase | higher is better | 0 → 0; 15 → 25; 35 → 50; 60 → 75; 100 → 100 |
| 46 | Export sales as % of turnover | % | higher is better | 0 → 0; 10 → 30; 25 → 55; 50 → 80; 75 → 100 |
| 48 | Value added | % | higher is better | 0 → 0; 15 → 25; 30 → 50; 50 → 75; 70 → 100 |

This table contains the band anchors for each of the 28 quantitative
criteria, numbered as in @tbl:criteria-model-full-listing. The direction column
records whether a larger measured value improves or worsens the score, which is
not uniform: arrears and gearing score inversely, and one criterion is best in
an interior band rather than at either extreme. The anchors are design
assumptions, set from the thresholds the source form and Sri Lankan SME lending
practice already use, and Section 5.16 reports how far the model's output moves
when they and the weights are perturbed.

## Appendix 2 The weight elicitation instrument

The instrument was built, verified and administered; eleven practitioners completed
it and Section 6.1 reports the result. It is reproduced here so that the design
can be assessed independently of its findings, and so that a later study can
administer it unchanged and compare.

### Appendix 2.1 Structure

Eight comparison levels: one comparing the six credit-risk dimensions, and one
for the criteria within each of the seven dimensions. Under the Best-Worst
Method each level of *n* items requires 2*n* − 3 comparisons, giving 86 in total
against 168 under classical pairwise AHP.

### Appendix 2.2 Participant information presented

> This exercise asks how much weight the different parts of an SME credit
> appraisal should carry. It takes about 15 minutes and involves 86 quick
> comparisons. There are no right answers — the study is measuring experienced
> judgement, including where practitioners disagree.
>
> Participation and confidentiality. Participation is voluntary and you may
> stop at any point. Do not enter your name or any customer information.
> Responses are identified only by the code you choose below, are used solely for
> academic research, and are reported only in aggregate.

### Appendix 2.3 Data collected

Participant code (self-chosen), years in credit or appraisal work, institution
type, and role. No name and no customer information are collected.

### Appendix 2.4 Comparison scale

Comparisons are made on the nine-point scale in @tbl:scale-used-pairwise-judgements.

[Table: scale-used-pairwise-judgements | Scale used for pairwise judgements]

| Value | Meaning |
|---|---|
| 1 | Equally important |
| 3 | Moderately more important |
| 5 | Strongly more important |
| 7 | Very strongly more important |
| 9 | Extremely more important |

Even values represent intermediate judgements, so a respondent who finds one
item somewhat more important than another but not clearly so has a value to
express it with. The scale is the one Saaty defined for the Analytic
Hierarchy Process and that the Best-Worst Method inherits unchanged.

## Appendix 3 Reproducing the results

Every quantitative result in this thesis is produced by an analysis that can be
re-run against the raw data. No value was entered by hand.

@tbl:analysis-scripts-results-produces lists the analyses in the order they run,
and the result each one produces. Each writes its output to a file from which
the chapters draw their numbers, so a figure quoted in the text can always be
traced back to the analysis that generated it.

[Table: analysis-scripts-results-produces | The analyses, in the order they run, and what each produces]

| # | Analysis | Produces | Reported in |
|---:|---|---|---|
| 1 | Data preparation | The cleaned dataset, with outcome-derived fields removed | 5.9 |
| 2 | Contamination analysis | Evidence that the term field carries outcome information | 5.10 |
| 3 | FOIA replication | The same artefact in the SBA's own loan-level extracts | 5.10.5 |
| 4 | Modulus probe | Whether a twelve-month modulus is arbitrary | 5.10.6 |
| 5 | Real-estate probe | The feature the dataset documentation itself proposes | 5.10.7 |
| 6 | Benchmarking | Clean against contaminated model performance | 5.11 |
| 7 | Significance testing | Confidence intervals, paired DeLong tests, calibration | 5.11, 5.13 |
| 8 | Cost-sensitive evaluation | Expected cost against fixed policies | 5.14 |
| 9 | Weight sensitivity | The weight perturbation study | 5.16 |
| 10 | Objective independence | Separability of the two objectives | 5.17 |
| 11 | Subgroup analysis | Disparate impact, with bootstrap intervals | 5.18 |
| 12 | Missingness analysis | The effect of withholding a field | 5.19 |
| 13 | Weight derivation | Best-Worst Method weights from the elicitation responses | 6.1.4 |
| 14 | Elicited against placeholder | What changed when the elicited weights replaced equal ones | 6.1.5 |
| 15 | Figure generation | Every figure in the thesis | — |
| 16 | Engine parity check | Agreement between the two implementations of the scoring engine | 4.12 |
| 17 | Solver self-test | The Best-Worst solver against a known-inconsistent input | 3.5.3 |

Two further checks guard the document itself. The first re-derives the
load-bearing figures from the generated result files and compares each against
what the chapters state, currently over ninety separate checks; a failure means
a number in the thesis no longer matches the analysis that produced it, and the
chapter is corrected rather than the check. The second runs the system's own
unit tests, of which there are 105.

## Appendix 4 Dataset

The SBA National dataset is public and is not reproduced here; it is distributed through the Kaggle dataset repository and is described by Li, Mickel and Taylor [33]. @tbl:dataset-filtering-applied records the filtering applied to it before analysis, and the number of records surviving each stage.

[Table: dataset-filtering-applied | Dataset filtering applied]

| Stage | Records |
|---|---:|
| Raw dataset | 899,164 |
| With a usable outcome | 897,167 |
| Approval years 1990–2010 | 847,980 |
| Fully matured before the 2014 cut-off | 652,284 |

Each stage removes records that would otherwise bias the estimate: those with no recorded outcome, those approved outside the window in which both the leakage and the benchmark results are computed, and those whose contractual term had not elapsed by the data cut-off. The 652,284 facilities that survive are the population every result in Chapter 5 is computed on.

## Appendix 5 Ethical considerations

**Source material.** The appraisal instrument analysed is a blank template. No
customer file, borrower record or internal credit policy document was accessed at
any point, and the system was demonstrated using constructed cases.

**Human participants.** The elicitation instrument collects no name and no
customer information. Participation was voluntary, participants identified
themselves only by a code of their own choosing, and the responses are reported
in aggregate. Eleven practitioners took part. What is stored is a participant code,
years of experience, institution type, role, and the comparison judgements
themselves; nothing in that record identifies a person or a borrower.

**Research integrity.** Every reported result is generated by code and is
regenerable from the raw data. Where an experiment could not be run, the claim is
withdrawn and the gap recorded as a limitation rather than filled with an
estimate. Negative results are reported as they occurred, including a scorecard
that failed to discriminate (Section 5.15), a hypothesis tested and rejected
(Section 5.10.4), and an independence premise that the study's own data partly
contradicts (Section 5.17.1).
