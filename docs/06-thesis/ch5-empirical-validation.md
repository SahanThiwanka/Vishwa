# Chapter 5 — Empirical Validation

> **Reproducibility.** Every figure and table in this chapter is produced by code in
> `research/src/`. Re-running `prepare_sba.py`, `leakage_analysis.py` and
> `benchmark.py` in that order regenerates all of it. No value has been entered by
> hand.

## 5.1 Purpose and scope of this chapter

Chapter 4 presented a criteria tree of 49 criteria derived from the People's Bank
*Project / Business Appraisal Report for SME Credit Facility*, and a scoring
method that maps appraisal inputs onto two separate objectives. This chapter asks
what can and cannot be established about that model from data.

The scope must be stated precisely, because the answer is narrower than the
question a reader might expect.

The criteria tree is instrument-specific. It scores debt service cover, the
competitive forces bearing on the applicant's market, management quality,
environmental risk, and nine development outcomes. **No public dataset contains
those variables.** Access to People's Bank's own historical files was not
available within this study, and would in any case be confidential.

The validation is therefore split three ways, and the three claims are kept
separate throughout:

| Component | Evidence | Reported in |
|---|---|---|
| Scoring **method** (band mapping, weighted aggregation, defuzzification) | Real default outcomes, SBA National | §5.3–5.5 |
| **Criterion weights** | Expert elicitation, Best-Worst Method | Chapter 6 |
| Full 49-criterion **tree** | Design contribution; not empirically validated | §5.7 |

The distinction matters. A claim that "the model was validated" would be false.
What is validated here is the scoring machinery, on a proxy dataset, for the
observable subset of criteria.

## 5.2 Dataset

The SBA National dataset (Li, Mickel and Taylor, 2018) records 899,164 loan
guarantees issued by the U.S. Small Business Administration between 1987 and
2014, with realised outcomes in `MIS_Status` (`P I F` = paid in full, `CHGOFF` =
charged off). It is the largest public dataset of small-business lending with
ground truth, and is widely used in credit-scoring research and teaching.

After removing 1,997 records with no usable outcome, 897,167 remain, with an
overall default rate of 17.56%.

### 5.2.1 Outcome-derived fields

Three fields are populated only after a loan has defaulted: `ChgOffPrinGr`
(charged-off principal), `ChgOffDate`, and `BalanceGross`. A model given any of
them reads the answer rather than predicting it. They are dropped in
`prepare_sba.py`, and their absence is asserted before the prepared file is
written.

### 5.2.2 Right-censoring

A loan approved in 2013 on a fifteen-year term cannot have defaulted by the 2014
data cut-off. Such loans appear to perform well only because insufficient time
has elapsed.

Restricting to the 1990–2010 approval window (847,980 loans) and separating those
whose full term elapsed before the cut-off:

| Cohort | n | Default rate |
|---|---:|---:|
| Censored (term not yet elapsed) | 195,696 | 7.77% |
| Fully matured | 652,284 | 20.41% |

The difference is large enough to dominate any model permitted to infer censoring
status. All analysis below uses the 652,284 fully-matured loans. This biases the
sample toward shorter terms in later years, which is noted as a limitation in
§5.7.

## 5.3 A contaminated predictor

### 5.3.1 How the problem surfaced

Initial benchmarking produced a gradient-boosting AUC of 0.9726 under random
splitting and 0.9461 under temporal splitting. Credit-scoring models on
small-business data do not ordinarily discriminate this well. The result was
treated as a symptom rather than an achievement.

Permutation importance showed the model to be, in substance, a function of a
single variable: shuffling `term_years` cost 0.395 AUC, while no other feature
cost more than 0.008. Yet `Term` as a monotone predictor reaches only 0.82. The
discrimination was coming from a **non-monotone** structure in the variable.

### 5.3.2 The structure

Default rates by exact term value, 2007 approvals:

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
default rate. Sixty months is not economically distinct from fifty-nine.

The pattern is roundness. Across the 1990–2010 cohort:

- **86.4%** of repaid loans have a term that is an exact multiple of twelve
- **8.5%** of charged-off loans do
- Charged-off loans are distributed almost uniformly across `Term mod 12`
  (7.7%–9.0% in each of the twelve residues, against 86.4% at residue zero for
  repaid loans)

The single boolean *"is the term a multiple of twelve"* — a quantity with no
economic content whatsoever — achieves **AUC 0.8894**.

### 5.3.3 Ruling out cohort composition

Irregular-term loans became more common over the period, and so did defaults, so
the association might be an artefact of pooling cohorts. It is not. Computed
within each approval year separately:

| Year | n | Default, round term | Default, irregular term | AUC |
|---:|---:|---:|---:|---:|
| 1990 | 14,859 | 0.6% | 19.2% | 0.859 |
| 1993 | 23,299 | 0.2% | 11.2% | 0.885 |
| 1997 | 37,718 | 0.6% | 29.8% | 0.888 |
| 2000 | 37,352 | 1.4% | 42.0% | 0.874 |
| 2003 | 58,000 | 1.6% | 54.1% | 0.893 |
| 2006 | 75,756 | 4.9% | 80.8% | 0.900 |
| 2007 | 71,649 | 6.7% | 85.5% | 0.899 |
| 2008 | 39,458 | 6.4% | 84.4% | 0.898 |

The association holds in every year, within a band of 0.859–0.900. Cohort
composition is excluded.

### 5.3.4 The mechanism is not established

The obvious explanation is that `Term` for defaulted loans has been overwritten
with elapsed time to charge-off. **This was tested and rejected.** Among 156,266
charged-off loans with both disbursement and charge-off dates:

- correlation between `Term` and actual months to charge-off: **0.043**
- proportion matching within ±3 months: **5.0%**

`Term` is not survival time. Whether the value is rewritten on restructuring,
recomputed under some servicing convention, or introduced when this derivative
file was assembled cannot be determined from the data.

The dataset codebook documents `Term` as "loan term in months" — the contractual
term. The observed distribution is not consistent with that definition for
charged-off loans. **The contamination is established; its cause is not.** This
study reports it accordingly and does not assert a mechanism it has not
demonstrated.

## 5.4 Consequences for reported performance

Two model specifications were run. The **clean** specification excludes `Term`
and every feature derived from it; the **contaminated** specification adds them
back, solely to quantify the inflation.

| Model | Fitted | Random AUC | Temporal AUC |
|---|:--:|---:|---:|
| **Clean specification** | | | |
| Expert scorecard | no | 0.4144 | 0.5275 |
| Logistic regression | yes | 0.6745 | 0.4565 |
| Gradient boosting | yes | 0.7898 | 0.6076 |
| **Contaminated specification** | | | |
| Logistic regression | yes | 0.8452 | 0.7854 |
| Gradient boosting | yes | 0.9726 | 0.9461 |
| *Term-roundness probe* | no | *0.8870* | *0.8965* |

Three observations.

**The inflation is severe.** Gradient boosting rises from 0.6076 to 0.9461 on
temporal validation — **0.339 AUC** obtained from a contaminated field.

**The probe bounds the artefact.** A single boolean with no economic meaning
reaches 0.8870 and 0.8965. Any model on this dataset scoring in that region,
having been given `Term`, is largely reproducing the artefact.

**Tree models are more exposed than linear ones.** Logistic regression, monotone
in term, gains 0.33 AUC from contamination; gradient boosting, free to split on
exact values, gains more and reaches further. Published results on this dataset
using tree ensembles with `Term` should be read with this in mind.

## 5.5 Validation protocol matters independently

Under the clean specification, gradient boosting scores 0.7898 on a random split
and 0.6076 on a temporal split — a gap of **0.182 AUC**. Random splitting places
loans from the same economic cycle in both training and test sets, so the model
is partly recalling conditions rather than generalising to unseen ones.

Logistic regression falls to 0.4565 temporally — below chance. Trained on
1990–2003 (9.1% default) and tested on 2004–2010 (35.9% default), the linear
model does not merely lose accuracy; its ranking inverts. This is a substantive
finding about credit-scoring practice: **a linear scorecard fitted to a benign
cycle can rank borrowers backwards in a stressed one.**

## 5.6 The expert scorecard: a negative result

The a priori scorecard, whose bands were set from credit reasoning before any
outcome was inspected, achieved **AUC 0.4144 (random) and 0.5275 (temporal)** —
at or below chance. It provides no reliable discrimination on this dataset.

This is reported as it stands. Three readings are available, and the evidence
does not distinguish between the first two:

1. **The proxies are inadequate.** The scorecard was built from SBA-observable
   variables — guarantee share, franchise status, urban/rural — because the
   People's Bank criteria are absent. These are not what the appraisal form
   scores. The strongest legitimate criteria in the tree (DSCR, ISCR, security
   cover, management quality, market position) have no counterpart here.
2. **The a priori bands are wrong.** Domain reasoning about which direction each
   proxy should point may simply be mistaken. With the scorecard's individual
   features carrying univariate AUC between 0.51 and 0.63, an equal-weighted
   aggregate of several mis-signed weak proxies can land below chance.
3. The method itself does not work — **not supported**, since the same machinery
   discriminates when given informative inputs, and its arithmetic is verified
   against an independent implementation.

The methodological conclusion is the useful one, and it is stronger than the
individual result:

> **An instrument-specific appraisal model cannot be validated against a dataset
> that does not contain its variables.** Substituting available proxies for the
> intended criteria does not test the model; it tests the proxies.

This is why the criterion weights are established by expert elicitation
(Chapter 6) rather than fitted to borrowed outcome data, and why that choice is a
methodological requirement rather than a fallback.

## 5.7 Limitations

**Jurisdiction.** SBA data reflects U.S. government-guaranteed small-business
lending. Sri Lankan SME credit differs in legal environment, collateral practice,
and macroeconomic volatility. Nothing here transfers directly.

**The fuzzy layer is not exercised.** Every SBA-observable criterion is
quantitative, so each input enters as a degenerate triangular fuzzy number
`[x,x,x]`. Centroid defuzzification returns `x`, and the fuzzy weighted average
reduces exactly to an ordinary weighted mean. **On this dataset the fuzzy
machinery does no work.** It is exercised only by qualitative criteria, which SBA
data does not contain. What §5.3–5.6 validates is band mapping and weighted
aggregation, not fuzzy inference.

**Maturity filtering biases composition.** Restricting to fully-matured loans
removes censoring but over-represents short-term facilities in later cohorts.

**Weights were placeholders.** All results here use equal weights within each
level. They therefore test structure, not the elicited model.

**The development objective is barely observable.** Only `CreateJob` and
`RetainedJob` proxy the development-impact objective. Five of the nine items in
clause 5 of the People's Bank form — women's participation, local raw material
usage, import substitution, value added, foreign exchange earnings — have no
counterpart in SBA data. The development objective is a design contribution and
is **not** empirically validated in this chapter.

**Novelty of the contamination finding is not fully established.** A literature
search found no published report of it, but that search was not exhaustive and
cannot support a claim of priority. The finding is reported as one the author is
not aware of having been documented, which is a weaker and defensible claim.

## 5.8 Summary

1. `Term` in the SBA National dataset carries outcome information. Roundness
   alone predicts default at AUC 0.889 overall and 0.859–0.900 within every
   approval year, despite having no economic meaning.
2. Excluding it drops gradient-boosting temporal AUC from 0.9461 to 0.6076.
3. Right-censoring is a separate and independent hazard: censored loans default
   at 7.77% against 20.41% for matured loans.
4. Random splitting overstates performance by 0.182 AUC relative to temporal
   validation; a linear scorecard fitted to a benign cycle ranks *backwards*
   under stress.
5. The a priori expert scorecard shows no discrimination on SBA-observable
   proxies (AUC 0.41–0.53), supporting the conclusion that instrument-specific
   appraisal models require elicitation rather than proxy-dataset fitting.

Findings 1 and 5 are the contributions of this chapter. Finding 1 is a caution to
users of a widely-adopted benchmark; finding 5 justifies the methodological
design of the study.

---

### References cited in this chapter

Li, M., Mickel, A. and Taylor, S. (2018) '"Should This Loan be Approved or
Denied?": A Large Dataset with Class Assignment Guidelines', *Journal of
Statistics Education*, 26(1), pp. 55–66. doi:10.1080/10691898.2018.1434342.
