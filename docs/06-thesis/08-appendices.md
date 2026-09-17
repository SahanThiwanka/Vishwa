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

The instrument was built, verified and administered; ten practitioners completed
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

The commands below regenerate every figure and table, in order. Each writes its
output to `research/outputs/`, from which the thesis draws its numbers.

[Table: Analysis scripts and the results each produces]

| Script | Produces |
|---|---|
| `prepare_sba.py` | The cleaned dataset, with leakage-bearing fields removed |
| `leakage_analysis.py` | Evidence that the term field carries outcome information |
| `sba_foia_replication.py` | The same artefact in the SBA's own FOIA extracts |
| `benchmark.py` | Clean against contaminated model benchmarks |
| `statistical_tests.py` | Confidence intervals, DeLong tests, calibration |
| `weight_sensitivity.py` | The weight perturbation study |
| `derive_weights.py` | Best-Worst Method weights from the elicitation responses |
| `elicited_vs_placeholder.py` | What changed when elicited weights replaced equal ones |
| `objective_independence.py` | Separability of the two objectives |
| `cost_analysis.py` | Cost-sensitive evaluation |
| `modulus_probe.py` | Whether a twelve-month modulus is arbitrary |
| `realestate_probe.py` | The feature the dataset documentation itself proposes |
| `fairness_analysis.py` | Disparate impact, with bootstrap intervals |
| `missingness_analysis.py` | The effect of withholding a field |
| `make_figures.py` | Every figure in the thesis |
| `test_parity.py` | Agreement between the Python and TypeScript engines |
| `bwm.py` | Solver self-test against a known-inconsistent input |

Two further checks guard the document itself. `scripts/verify_claims.py`
re-derives the load-bearing figures from the generated result files and compares
each against what the chapters state; it currently runs ninety checks. `npm test`
in `web/` exercises the system's own unit tests. A failure in the first means a
number in the thesis no longer matches the analysis that produced it, and the
chapter is corrected rather than the check.

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

**Human participants.** The elicitation instrument collects no name and no
customer information. Participation was voluntary, participants identified
themselves only by a code of their own choosing, and the responses are reported
in aggregate. Ten practitioners took part. What is stored is a participant code,
years of experience, institution type, role, and the comparison judgements
themselves; nothing in that record identifies a person or a borrower.

**Research integrity.** Every reported result is generated by code and is
regenerable from the raw data. Where an experiment could not be run, the claim is
withdrawn and the gap recorded as a limitation rather than filled with an
estimate. Negative results are reported as they occurred, including a scorecard
that failed to discriminate (Section 5.15), a hypothesis tested and rejected
(Section 5.10.4), and an independence premise that the study's own data partly
contradicts (Section 5.17.1).
