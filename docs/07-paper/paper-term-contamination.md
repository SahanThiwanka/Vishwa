# Target Contamination in a Widely Used Small-Business Credit Benchmark: Evidence from the SBA National Dataset

**A. A. V. Athukorala**
NSBM Green University, Sri Lanka

---

## Abstract

The SBA National dataset — 899,164 U.S. Small Business Administration loan
guarantees issued between 1987 and 2014, with realised repayment outcomes — is
widely used as a benchmark in small-business credit-scoring research and
teaching. We report that its `Term` field carries information about the outcome
it is used to predict. Whether `Term` is an exact multiple of twelve, a property
with no economic content, predicts default with AUC 0.889 across the dataset and
between 0.859 and 0.900 within *every* approval year from 1990 to 2010. Among
2007 approvals, facilities at 60 months defaulted at 11.1% while those at 59 and
61 months defaulted at 86.7% and 92.2%. Including the field raises
gradient-boosting discrimination from AUC 0.608 to 0.946 under temporal
validation — an inflation of 0.339. We test and reject the natural explanation
that `Term` records elapsed time to charge-off (correlation 0.043 with observed
survival). The contamination is therefore demonstrated but its mechanism remains
unresolved. We further show that right-censoring is a separate and independent
hazard in this dataset, that random splitting overstates performance by 0.182 AUC relative to temporal
validation, and that calibration degrades roughly 700-fold across the same
boundary, with models systematically under-predicting default. We recommend excluding `Term` and every
derived feature, restricting to fully-matured facilities, validating temporally,
and — generally — treating a variable that outperforms the plausible ceiling for
its domain as a suspected defect rather than a result.

**Keywords:** credit scoring, target leakage, benchmark datasets, SME lending,
model validation, reproducibility

---

## I. Introduction

Public benchmark datasets shape the fields that use them. When a dataset contains
a variable that encodes the outcome, every model given that variable reports
discrimination it does not possess, and the inflated figure becomes the standard
against which subsequent work is measured.

The SBA National dataset was introduced by Li, Mickel and Taylor [1] as a teaching
resource for statistics as investigative decision-making, and has since become a
common benchmark for small-business credit modelling. It records 899,164 loan
guarantees with realised outcomes, making it one of the largest public datasets of
small-business lending with ground truth.

This paper reports that the dataset's `Term` field is contaminated. The finding
emerged during an unrelated study — the construction of a multi-criteria appraisal
model for Sri Lankan SME lending — when a gradient-boosting benchmark returned an
AUC of 0.9726. Rather than reporting a result that exceeded plausible
expectations for the domain, we investigated it.

Our contributions:

1. Evidence that `Term` carries outcome information, robust to cohort controls
   (§IV).
2. Quantification of the resulting inflation in reported performance, with a
   meaningless-variable probe establishing an artefact ceiling (§V).
3. Rejection of the natural mechanism hypothesis, leaving the cause open and
   stated as such (§IV-F).
4. Three further validation hazards in the same dataset: right-censoring, the
   optimism of random splitting, and a roughly 700-fold degradation in
   calibration across a temporal boundary (§VI).

All analysis is reproducible from code and the public dataset.

## II. Related Work

Target leakage — the presence in training data of information unavailable at
prediction time — is a recognised failure mode in applied machine learning, and
general treatments of credit modelling identify fields such as interest rate,
issue date and outstanding principal as requiring removal.

Its prevalence is not marginal. Kapoor and Narayanan [3] surveyed ML-based
science across seventeen fields and found leakage affecting **294 papers**, in
some cases producing wildly overoptimistic conclusions, and argue that leakage is
the single largest cause of irreproducibility in the area. They set out a
taxonomy of eight leakage types ranging from textbook errors to open research
problems.

The case reported here falls squarely in their category **[L2], "model uses
features that are not legitimate"**, and specifically in the instance they name:
"if a feature is a proxy for the outcome variable". What makes it harder to
detect than the textbook forms of [L2] is that the offending field is
**documented as legitimate**, is available at prediction time under its
documented meaning, and is economically meaningful — so it passes the checks a
careful analyst would apply, and it passes their own model info sheet, which asks
the researcher to argue why each feature is legitimate. `Term` can be argued
legitimate, correctly, from the codebook. It is caught only by noticing that the
*shape* of its relationship with the outcome is not one any economic mechanism
could produce.

This is the respect in which the case extends rather than merely instantiates
their taxonomy. Their remedy is to have the researcher justify each feature; here
that justification is available and sound, and the leakage is still present.

Within the SBA National dataset specifically, the literature we surveyed
identifies `Term`, disbursement and approval amounts as significant predictors of
default, and uses them accordingly. The dataset's own codebook documents `Term` as
"loan term in months" — that is, the contractual term agreed at origination, which
is legitimately available at appraisal time and would properly be used.

The same paper derives a feature from `Term`: a dummy `RealEstate`, set to 1
where `Term` ≥ 240 months on the reasoning that only real-estate-backed lending
runs twenty years or more, with reported default rates of 1.64% against 21.16%.
Our 1990–2010 cohort reproduces this at 1.45% against 20.69%. Right-censoring is
the obvious explanation and is not the answer — 87.6% of these facilities are
censored, but the matured subset defaults *lower*, at 0.56%. Roundness accounts
for more: the group is 95.96% round-termed against 69.27% for the rest, and
stratifying splits the 20.40-point gap into 2.51 points among round terms and
50.32 points among irregular ones. Among facilities under 240 months, round terms
default at 2.58% and irregular ones at 62.39%.

We draw no criticism of that paper from this. It documents a teaching dataset and
derives a feature on sound economic reasoning. The observation is that a field
carrying outcome information contaminates what is built from it, up to and
including the dataset's own documentation, and that nothing in the published
description of either would allow a reader to detect it.

We located no source reporting that the field itself carries outcome information.
We state this as a finding we have not found documented rather than as a claim of
priority: our search was not exhaustive.

## III. Data and Method

### A. Dataset

We use the SBA National dataset (899,164 records, 1987–2014). The outcome is
`MIS_Status`: `P I F` (paid in full) or `CHGOFF` (charged off). Removing 1,997
records with no usable outcome leaves 897,167, with an overall default rate of
17.56%.

### B. Removing known outcome-derived fields

Three fields are populated only after default: `ChgOffPrinGr`, `ChgOffDate` and
`BalanceGross`. These are dropped, and their absence asserted before analysis.
This is standard practice and is not the subject of this paper.

### C. Cohort window and maturity

We restrict to approvals between 1990 and 2010 (847,980 records); earlier volumes
are small and erratic, later approvals are heavily censored. We then separate
facilities whose full contractual term elapsed before the 2014 data cut-off:

| Cohort | n | Default rate |
|---|---:|---:|
| Censored (term not yet elapsed) | 195,696 | 7.77% |
| Fully matured | 652,284 | 20.41% |

Analysis uses the 652,284 fully-matured facilities. This control is applied
*before* the contamination analysis, so the results in §IV cannot be attributed to
censoring.

### D. Models and protocols

We compare an unfitted expert scorecard (bands set a priori, never exposed to
outcome labels), logistic regression, and histogram gradient boosting, under two
protocols: a 70/30 random split, and a temporal split training on approvals up to
2003 and testing on 2004–2010.

Each is run under two feature specifications: **clean**, excluding `Term` and all
derived features, and **contaminated**, including them.

## IV. Evidence of Contamination

### A. Discovery

Under the contaminated specification, gradient boosting reached AUC 0.9726
(random) and 0.9461 (temporal). Permutation importance showed the model to be
substantially a function of one variable: shuffling term cost 0.395 AUC, while no
other feature cost more than 0.008.

Yet `Term` as a monotone predictor reaches only 0.82. The discrimination therefore
came from **non-monotone structure** within the variable — a model splitting on
exact values could exploit something a linear model could not.

### B. The structure is roundness

Default rates by exact term value among 2007 approvals:

| Term (months) | n | Default rate |
|---:|---:|---:|
| 58 | 634 | 92.1% |
| 59 | 663 | 86.7% |
| **60** | **5,040** | **11.1%** |
| 61 | 641 | 92.2% |
| 62 | 609 | 90.1% |
| 63 | 674 | 81.0% |
| 64 | 596 | 88.1% |

A one-month difference in contractual term cannot produce an eight-fold change in
default rate. Sixty months is not an economically distinct product from
fifty-nine.

Across the full cohort:

- **86.4%** of repaid facilities have a term that is an exact multiple of twelve
- **8.5%** of charged-off facilities do
- charged-off facilities are distributed near-uniformly across `Term mod 12`
  (7.7%–9.0% in each of the twelve residues)

The single boolean *"Term is a multiple of twelve"* achieves **AUC 0.8894**.

### C. Not a cohort artefact

Irregular terms became more common over the period, as did defaults, raising the
possibility that the association reflects pooling of heterogeneous cohorts. It
does not. Computed within each approval year:

| Year | n | Default, round | Default, irregular | AUC |
|---:|---:|---:|---:|---:|
| 1990 | 14,859 | 0.6% | 19.2% | 0.859 |
| 1993 | 23,299 | 0.2% | 11.2% | 0.885 |
| 1997 | 37,718 | 0.6% | 29.8% | 0.888 |
| 2000 | 37,352 | 1.4% | 42.0% | 0.874 |
| 2003 | 58,000 | 1.6% | 54.1% | 0.893 |
| 2006 | 75,756 | 4.9% | 80.8% | 0.900 |
| 2007 | 71,649 | 6.7% | 85.5% | 0.899 |
| 2008 | 39,458 | 6.4% | 84.4% | 0.898 |

The association holds in every year within 0.859–0.900.

### D. Twelve is not an arbitrary choice

If any modulus discriminated comparably, the pattern would not be about round
contractual terms. Twenty moduli were tested on the 651,501 matured facilities
with a positive term. Because the strata overlap — every multiple of twelve is
also a multiple of six, four, three and two — discrimination is reported both raw
and residually, the latter computed within the multiples of twelve and within the
non-multiples separately.

| Modulus | Raw AUC | | Modulus | Raw AUC |
|---:|---:|---|---:|---:|
| **12** | **0.8859** | | 7 | 0.6291 |
| 6 | 0.8600 | | 5 | 0.5856 |
| 4 | 0.8109 | | 13 | 0.4699 |
| 3 | 0.7934 | | 11 | 0.4660 |
| 2 | 0.7125 | | | |

Twelve leads, and its divisors decline in the order 12 > 6 > 4 > 3 > 2 — the
dilution pattern expected when multiples of twelve are the carrier and each
coarser modulus admits more non-annual terms. Moduli that do not divide twelve
behave differently: eleven and thirteen sit at or below chance.

One qualification. Within facilities that are *not* multiples of twelve,
"multiple of three" still reaches 0.5888 and "multiple of six" 0.5684, so some
signal attaches to quarter- and half-year terms independently. The pattern is
roundness on a calendar grid rather than strictly annual roundness — which is the
more natural reading of a contractual convention, and does not affect the
argument that the field carries outcome information.

### E. The artefact is in the SBA's own records, not in the derivative

One candidate explanation would make this finding uninteresting: that the
artefact was introduced when the widely used derivative file was assembled. It
can be excluded.

The SBA publishes loan-level FOIA extracts of the same programme, refreshed
quarterly. Using the release current to 30 June 2026, across **603,665 resolved
7(a) facilities approved FY2000–FY2009**:

| | SBA FOIA 7(a) | Derivative file |
|---|---:|---:|
| Repaid, term a multiple of twelve | 82.02% | 86.4% |
| Charged off, multiple of twelve | 8.46% | 8.5% |
| AUC of the roundness boolean | **0.8678** | 0.8894 |

The pattern holds in every approval year, from 0.8562 to 0.8808. **The artefact
is present in the authoritative publication.**

We do not claim independent replication. The derivative is itself built from SBA
FOIA releases, so these are the same loans at a different vintage. The comparison
establishes where the artefact originates, not that it recurs in a second source.

The same release provides a control. The **504 programme** is a different
facility type under the same agency, in the same extract, with terms fixed by
programme design — 95.5% written at exactly 240 months. There the boolean reaches
**AUC 0.4997**, and charged-off facilities are marginally *more* round-termed
(99.85%) than repaid ones (99.80%).

Where the term is set by the programme and does not vary, charged-off records
keep their round terms. Where it is negotiated facility by facility, they
overwhelmingly do not. This is consistent with a servicing or restructuring
process that writes to the term field of 7(a) records, and inconsistent with any
uniform agency-wide transformation. It narrows the mechanism without
establishing it.

### F. The mechanism is still not fully established

The natural hypothesis is that `Term` for charged-off facilities has been
overwritten with elapsed time to charge-off. **We tested and rejected it.** Among
156,266 charged-off facilities with both disbursement and charge-off dates:

- correlation between `Term` and observed months to charge-off: **0.043**
- proportion agreeing within ±3 months: **5.0%**

`Term` is not survival time. Whether values are rewritten on restructuring,
recomputed under a servicing convention, or introduced during preparation of the
distributed file cannot be determined from the data alone. We report the
contamination as demonstrated and the mechanism as open, and we caution against
citing a cause that has not been shown.

## V. Impact on Reported Performance

AUCs carry 95% stratified bootstrap confidence intervals (300 replicates).

| Model | Fitted | Random [95% CI] | Temporal [95% CI] |
|---|:--:|---|---|
| **Clean specification** | | | |
| Expert scorecard | no | 0.4144 [0.4111, 0.4175] | 0.5275 [0.5252, 0.5296] |
| Logistic regression | yes | 0.6745 [0.6722, 0.6774] | 0.4565 [0.4545, 0.4586] |
| Gradient boosting | yes | 0.7898 [0.7877, 0.7926] | 0.6076 [0.6053, 0.6097] |
| **Contaminated specification** | | | |
| Logistic regression | yes | 0.8452 [0.8433, 0.8472] | 0.7854 [0.7839, 0.7869] |
| Gradient boosting | yes | 0.9726 [0.9718, 0.9732] | 0.9461 [0.9453, 0.9469] |
| *Roundness probe* | no | *0.8870* | *0.8965* |

The intervals for the clean and contaminated specifications do not overlap at
either protocol, and paired DeLong tests [4] give p < 0.001 for every
clean-versus-contaminated comparison. The effect is not attributable to sampling
variation.

Three observations.

**The inflation is large.** Gradient boosting rises from 0.6076 to 0.9461 under
temporal validation: **0.339 AUC** attributable to a contaminated field.

**The probe bounds the artefact.** A single boolean with no economic content
reaches 0.887 and 0.897. Results on this dataset in that region, obtained from a
model given `Term`, are substantially reproducing the artefact rather than
measuring credit risk.

**Flexible models are more exposed.** Logistic regression, monotone in term, gains
0.33 AUC; gradient boosting, free to split on exact values, gains more and reaches
further. The contamination is most damaging precisely to the model families most
commonly reported as state of the art on this dataset.

## VI. Three Further Hazards

### A. Right-censoring

Censored facilities default at 7.77% against 20.41% for
matured ones (§III-C). A model able to infer censoring status from feature
interactions — facility size tracks inflation, some programmes ran only in certain
years — obtains discrimination unrelated to credit risk. This is independent of
the `Term` contamination and requires its own control.

### B. Optimism of random splitting

Under the clean specification, gradient boosting
scores 0.7898 randomly against 0.6076 temporally: a gap of **0.182 AUC**. Random
splitting places facilities from the same economic cycle on both sides.

Logistic regression falls to 0.4565 temporally — **below chance**. Trained on
1990–2003 (9.1% default) and tested on 2004–2010 (35.9% default), its ranking
inverts. This has direct practical significance: a linear scorecard fitted during
benign conditions may rank borrowers backwards under stress.

### C. Calibration degrades further than discrimination

Discrimination is not the only thing temporal validation damages, and it is not
the most consequential. Reporting the Brier score under Murphy's decomposition,
reliability — the distance between predicted probabilities and observed rates —
worsens by roughly **700-fold** for gradient boosting between protocols:

| Model | Protocol | Brier | Reliability | Resolution |
|---|---|---:|---:|---:|
| Gradient boosting (clean) | random | 0.1319 | 0.00005 | 0.03003 |
| Gradient boosting (clean) | temporal | 0.2592 | 0.03705 | 0.00729 |
| Logistic regression (clean) | random | 0.1539 | 0.00091 | 0.00838 |
| Logistic regression (clean) | temporal | 0.2882 | 0.05803 | 0.00121 |

Under random splitting the boosted model's reliability diagram lies on the
diagonal. Under temporal validation the whole curve lifts above it: the model
**systematically under-predicts default**, reporting roughly 0.2 where the
observed rate is 0.45. Trained on cohorts defaulting at 9.1% and tested on
cohorts defaulting at 35.9%, it carries a benign period's base rate into a
stressed one.

For a lender this is the more dangerous failure mode. Falling discrimination is
visible and invites scrutiny; a model that still ranks tolerably while pricing a
45% risk at 20% produces provisions less than half of what they should be, and
appears to be working while doing so. **Recalibration on recent outcomes is a
separate requirement from revalidation of discrimination**, and the two are
frequently conflated.

## VII. Limitations

We have not fully established the mechanism of the contamination (§IV-F), and we do not
claim priority for the finding — our literature search was not exhaustive.

Restricting to fully-matured facilities removes censoring but over-represents
short-term facilities in later cohorts. Excluding `Term` also discards genuine
predictive signal: contractual term is economically meaningful, and some of the
0.339 AUC difference is legitimate. We exclude the whole field because the
contaminated and legitimate components cannot be separated, which is conservative
rather than precise.

Our findings concern the distributed SBA National file. We have not compared
against SBA's primary records, which would be the direct route to resolving the
mechanism.

## VIII. Recommendations and Conclusion

For work using the SBA National dataset:

1. **Exclude `Term` and all derived features.** Report performance without it, or
   report both specifications side by side.
2. **Control right-censoring** by restricting to facilities whose term elapsed
   before the data cut-off.
3. **Validate temporally**, not randomly.
4. **Include a meaningless-variable probe.** The roundness boolean costs nothing
   to compute and bounds how much apparent performance is artefact.

These extend, for this dataset, the general remedies Kapoor and Narayanan [3]
propose — principally that authors document leakage checks explicitly rather than
leaving them implicit.

More generally: **an unexpectedly strong result should be treated as a suspected
defect until explained.** The contamination reported here was found only because
an AUC of 0.9726 was investigated rather than published. It would have passed
review comfortably — it exceeded the benchmarks it would have been compared
against, which is precisely why it would not have been questioned.

The `Term` field in the SBA National dataset carries information about the outcome
it is used to predict. Its roundness alone predicts default at AUC 0.889, within
every approval year, despite carrying no economic meaning. Its inclusion inflates
gradient-boosting temporal discrimination by 0.339 AUC.

### A. Published work in the affected region

We examined seven candidate studies against four criteria: use of the SBA
National file, inclusion of `Term` among the predictors, a model class able to
split on exact values, and a reported result in the region the roundness probe
alone can reach. Four were excluded on reading, as they use other datasets. Two
could not be obtained.

One meets every criterion. Yussuph [5] uses the SBA National file — "27 columns
and 899164 rows" — and ranks `Term` the **most important feature for both** a
random forest and an XGBoost model, reporting ROC-AUC of 0.961 and 0.97
respectively under a 70/15/15 random split.

Two qualifications are necessary. We did not reproduce that study's pipeline. And
its description of preprocessing leaves a second leakage path open: it reports
type-converting `ChgOffDate`, `Balance Gross` and `ChgOffPrinGr` — all populated
only after charge-off — and does not state that they were excluded from the
feature set. Either path would produce a result of this magnitude.

We therefore make the narrow claim the evidence supports. A result in this
region, from a model able to split on exact term values and ranking that field
first, **cannot be distinguished from the artefact on published information
alone**. That this cannot be settled from a published methods section is itself
the argument for recommendation 4 below: without a meaningless-variable probe, a
reader has no way to tell an artefact from a finding.

Published results on this dataset obtained from tree-based models with `Term`
included warrant re-examination.

---

## References

[1] M. Li, A. Mickel, and S. Taylor, "'Should This Loan be Approved or Denied?': A
Large Dataset with Class Assignment Guidelines," *Journal of Statistics
Education*, vol. 26, no. 1, pp. 55–66, 2018, doi:10.1080/10691898.2018.1434342.

[2] P. K. Roy and K. Shaw, "A multicriteria credit scoring model for SMEs using
hybrid BWM and TOPSIS," *Financial Innovation*, vol. 7, no. 1, 2021,
doi:10.1186/s40854-021-00295-5.

[4] E. R. DeLong, D. M. DeLong and D. L. Clarke-Pearson, "Comparing the areas
under two or more correlated receiver operating characteristic curves: a
nonparametric approach," *Biometrics*, vol. 44, no. 3, pp. 837-845, 1988.

[3] S. Kapoor and A. Narayanan, "Leakage and the reproducibility crisis in
machine-learning-based science," *Patterns*, vol. 4, no. 9, 100804, 2023,
doi:10.1016/j.patter.2023.100804.

[5] T. T. Yussuph, "Leveraging machine learning algorithm to enable access to
credit for small businesses in the United States of America," *International
Journal on Cybernetics & Informatics*, vol. 13, no. 1, pp. 53-66, 2024,
doi:10.5121/ijci.2024.130105.

*Additional references to be completed on submission: general treatments of target
leakage in applied machine learning. The search for affected published work is
recorded in `docs/07-paper/affected-work-search.md`; two candidates remain
unobtainable without library access.*

---

## Reproducibility

All results are produced by the following, in order, against the public dataset:

```
research/src/prepare_sba.py        # cleaning, leakage-column removal, censoring flags
research/src/leakage_analysis.py   # Sections IV-B, IV-C, IV-F
research/src/sba_foia_replication.py # Section IV-E
research/src/modulus_probe.py      # Section IV-D
research/src/benchmark.py          # Section V
research/src/make_figures.py       # figures
```

No value in this paper was entered by hand.

---

## Submission notes (not for publication)

**Before submitting, complete these:**

1. **Systematic search for affected published work — PARTLY DONE.** One study
   (Yussuph 2024) is verified by full text and cited in §VIII-A; four are excluded
   by full text; two could not be retrieved without library access (Zhou et al.
   2023 via ResearchGate, and *Mathematics* 12(21) 3423, which returns 403).
   Retrieve both before submission and re-run the check with
   `scripts/read_pdf.py`. A database search (Scopus, Web of Science, IEEE Xplore)
   has still not been run and is what a reviewer will expect of a claim framed as
   systematic.
2. **Contact the SBA or the dataset authors** about the mechanism — now a
   narrower question than it was. §IV-E establishes that the artefact is in the
   SBA's own FOIA publication and absent from the 504 programme, which points at
   a servicing or restructuring process acting on 7(a) records. What remains is
   confirmation of which process, and only the agency can supply that.
3. **Complete the leakage literature review** — reference [4] onward. Kapoor and
   Narayanan's taxonomy is cited; position this case explicitly against the
   specific type it instantiates.
4. **Reformat to the target venue's template** (IEEE two-column or the venue's
   equivalent).

**Suggested venues:** a Sri Lankan IEEE conference (ICIIS, ICAC, ICTer) for speed;
or, given that the finding concerns research practice rather than a new method, a
data-quality or reproducibility track. *Journal of Statistics and Data Science
Education* is worth considering since it published the original dataset paper and
the finding bears directly on its use in teaching.
