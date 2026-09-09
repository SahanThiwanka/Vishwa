# APPENDICES

## Appendix 1 The criteria model

The complete criteria model is held as a single machine-readable file,
`shared/model/criteria-tree.json`, consumed by both the decision-support system
and the analysis pipeline so that the model described in this thesis and the
model the system runs cannot diverge.

Every criterion records the clause of the People's Bank *Project / Business
Appraisal Report for SME Credit Facility* from which it derives.

[Table: Criteria model summary by objective and dimension]

| Objective | Dimension | Criteria | Source clauses |
|---|---|---:|---|
| Credit Risk | Borrower and Management Capacity | 6 | 2.8, 2.10, 3.2, 3.4 |
| Credit Risk | Credit History and Banking Conduct | 5 | 2.11, 2.14 |
| Credit Risk | Historic Financial Performance | 9 | 2.13, 2.15–2.18 |
| Credit Risk | Project Viability and Projections | 8 | 3.1.3, 3.7, 4 |
| Credit Risk | Market and Competitive Position | 7 | 3.10 |
| Credit Risk | Risk, Security and Compliance | 6 | 3.3, 3.5, 3.6, 3.11, 3.12, 6.5 |
| Development Impact | Economic and Social Contribution | 8 | 5, 3.4.1 |
| **Total** | **7 dimensions** | **49** | |

Twenty-eight criteria are quantitative and twenty-one qualitative.

## Appendix 2 The weight elicitation instrument

The instrument was built and verified but **not administered** (Section 5.19).
It is reproduced here so that the design can be assessed and so that a
subsequent study can administer it unchanged.

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
> **Participation and confidentiality.** Participation is voluntary and you may
> stop at any point. Do not enter your name or any customer information.
> Responses are identified only by the code you choose below, are used solely for
> academic research, and are reported only in aggregate.

### Appendix 2.3 Data collected

Participant code (self-chosen), years in credit or appraisal work, institution
type, and role. **No name and no customer information are collected.**

### Appendix 2.4 Comparison scale

[Table: Scale used for pairwise judgements]

| Value | Meaning |
|---|---|
| 1 | Equally important |
| 3 | Moderately more important |
| 5 | Strongly more important |
| 7 | Very strongly more important |
| 9 | Extremely more important |

Even values represent intermediate judgements.

## Appendix 3 Reproducing the results

Every quantitative result in this thesis is produced by code in the accompanying
repository. No value was entered by hand.

```
python research/src/prepare_sba.py            # clean the raw dataset
python research/src/leakage_analysis.py       # contamination evidence
python research/src/benchmark.py              # clean vs contaminated benchmarks
python research/src/statistical_tests.py      # intervals, DeLong, calibration
python research/src/weight_sensitivity.py     # weight perturbation study
python research/src/objective_independence.py # objective separability
python research/src/cost_analysis.py          # cost-sensitive evaluation
python research/src/modulus_probe.py          # is twelve arbitrary?
python research/src/realestate_probe.py       # the documentation's own feature
python research/src/fairness_analysis.py      # disparate impact, bootstrapped
python research/src/missingness_analysis.py   # what withholding does
python research/src/make_figures.py           # all figures
python research/src/test_parity.py            # engine agreement check
python research/src/bwm.py                    # solver self-test
python scripts/verify_claims.py               # consistency checks
cd web && npm test                            # system unit tests
```

`scripts/verify_claims.py` re-derives the load-bearing figures from the generated
result files and checks each against what this thesis states. It reports 25
checks and currently passes all of them.

## Appendix 4 Dataset

The SBA National dataset is public and is not reproduced here. It may be obtained
as described in `research/data/DATASETS.md`.

[Table: Dataset filtering applied]

| Stage | Records |
|---|---:|
| Raw dataset | 899,164 |
| With a usable outcome | 897,167 |
| Approval years 1990–2010 | 847,980 |
| Fully matured before the 2014 cut-off | 652,284 |

## Appendix 5 Ethical considerations

**Source material.** The appraisal instrument analysed is a blank template. No
customer file, borrower record or internal credit policy document was accessed at
any point, and the system was demonstrated using constructed cases.

**Human participants.** The elicitation instrument was designed to collect no
name and no customer information, with voluntary participation and aggregate-only
reporting. It was not administered, so no participant data exists.

**Research integrity.** Every reported result is generated by code and is
regenerable from the raw data. Where an experiment could not be run, the claim is
withdrawn and the gap recorded as a limitation rather than filled with an
estimate. Negative results are reported as they occurred, including a scorecard
that failed to discriminate (Section 5.15), a hypothesis tested and rejected
(Section 5.10.4), and an independence premise that the study's own data partly
contradicts (Section 5.17.1).
