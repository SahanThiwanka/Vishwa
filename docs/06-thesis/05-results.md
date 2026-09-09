# 5 RESULTS

## 5.1 Result

| Objective | Dimension | Criteria | Form clauses |
|---|---|---:|---|
| Credit Risk | Borrower & Management Capacity | 6 | 2.8, 2.10, 3.2, 3.4 |
| | Credit History & Banking Conduct | 5 | 2.11, 2.14 |
| | Historic Financial Performance | 9 | 2.13, 2.15–2.18 |
| | Project Viability & Projections | 8 | 3.1.3, 3.7, 4 |
| | Market & Competitive Position | 7 | 3.10 |
| | Risk, Security & Compliance | 6 | 3.3, 3.5, 3.6, 3.11, 3.12, 6.5 |
| Development Impact | Economic & Social Contribution | 8 | 5, 3.4.1 |
| **Total** | **7 dimensions** | **49** | |

Twenty-eight criteria are quantitative and twenty-one qualitative. The model is
held in `shared/model/criteria-tree.json` as the single source of truth, consumed
by both the web application and the analysis pipeline.

## 5.2 The dual-objective structure

### 5.2.1 Rationale

Clause 5 of the form, *Economic Consideration*, scores nine before/after outcomes:
manpower, women's participation, local raw material usage, productive capacity,
production, export sales, import substitution, value added, and foreign exchange
earnings. Clause 3.4.1 separately disaggregates employment by gender.

These are not credit risk. A project can employ many people, substitute imports
and earn foreign exchange while still being a poor credit; the reverse also holds.
People's Bank is a state bank with a development mandate, and its appraisal form
reflects that it is being asked to serve two objectives at once.

Mainstream credit scoring optimises a single objective: the probability of
repayment. Applying that framing here would mean **discarding clause 5 entirely**
— deleting the developmental half of the institution's own mandate because it does
not fit the model.

### 5.2.2 Design decision

The model therefore carries two objectives and **reports them separately. They are
never combined into a single number.**

This is enforced in the engine rather than left to convention: `AppraisalResult`
holds an array of objective results, and no code path produces an overall score.
The interface presents them side by side; the exported report presents them as
distinct sections with an explicit note that the trade-off is a matter for the
approving authority.

The reason is that a weighted combination would destroy the information the
structure exists to expose. A facility scoring 80 on credit and 40 on development
and one scoring 60 on both are materially different propositions, and a combined
score of 60 would render them identical. Making the divergence visible is the
contribution; resolving it is a policy question that belongs to the bank, not to
the model.

Verification of this behaviour appears in the test case of §5.15: the same
application scored **80.2 on credit risk (band A) and 74.6 on development impact
(band B)**.

## 5.3 The completeness gate

### 5.3.1 A problem found by testing

During verification, an appraisal with only seven of forty-nine criteria entered —
14% complete — returned a credit risk score of 73.7 and the recommendation *"Band
B — recommend with conditions."*

The arithmetic was correct. Weight renormalisation (§4.11.3) had worked exactly as
designed: the seven entered criteria carried the full weight, and they happened to
score well. But the system was confidently recommending a facility on almost no
information, and nothing in the output signalled that.

This is a genuine hazard of renormalisation, and it is not specific to this
implementation. **A sparse appraisal produces a plausible score while its
evidential basis collapses**, and the score itself gives no indication of the
difference.

### 5.3.2 Response

An objective assessed below a completeness threshold (0.6) returns its score but
**no risk band and no recommendation.** The result carries a `sufficient` flag and
a list of outstanding criteria, and the interface tells the officer what is
missing instead of offering a number to sign against.

The gate is deliberately a **refusal to answer, not a scoring adjustment**.
Discounting the score for incompleteness would have preserved the false
impression that the system had an opinion. It does not; it has insufficient
information, and saying so is the correct output.

## 5.4 Explainability

Each criterion's contribution is computed as its normalised weight times its
score, expressed in points of the parent's score. **Contributions sum exactly to
the parent score**, which is what makes the breakdown a decomposition rather than
a decoration.

The interface presents, for each dimension: its score, its contribution to the
objective, its completeness, and a table of constituent criteria showing raw
value, derived score and contribution — each labelled with its source clause. An
officer can therefore trace any recommendation from the headline score down to the
clause of the bank's own form that produced it.

## 5.5 Report generation

The system exports a completed appraisal as a Word document in the People's Bank
format: Annexure I heading, clause-numbered sections, the scoring evidence, and
the clause 7 signature blocks.

This closes the loop. The officer receives back the document the institution
already uses, with no retyping and no change to the existing approval chain. A
system that produced its own report format would require the bank to adopt new
paperwork alongside new software; producing the incumbent document removes that
barrier entirely.

## 5.6 Verification

The engine carries a structural test suite (`npm run test:scoring`) covering three
cases — a sound manufacturing expansion, a thin startup with a DSCR breach, and a
deliberately incomplete file:

The suite covers the scoring engine, the validation schemas, and the
authorisation logic — 62 tests in total. Server Actions are reachable by direct
POST rather than only through the application's own forms, so every action
validates its input before use, and validation failures report which field failed
without echoing the submitted value back.

| Check | Result |
|---|---|
| Strong case scores above weak on credit risk | pass |
| Strong case scores above weak on development impact | pass |
| Weak case flags a critical breach (DSCR 0.92) | pass |
| Strong case flags no breach | pass |
| Strong case reaches band A or B | pass |
| Weak case falls to band C or D | pass |
| Objectives reported separately, not merged | pass |
| Contributions sum to parent score | pass |
| Weight status still flagged PLACEHOLDER | pass |

The system was additionally verified end to end through the browser: all 49
criteria entered through the interface, producing credit risk 80.2 (band A)
against development impact 74.6 (band B), persisted to the database, rendered with
full contribution breakdown, and exported to a valid `.docx` in bank format.

These are **structural** checks. They establish that the engine behaves as
specified — not that its scores are accurate. Accuracy is the subject of
Chapter 5, and the answer given there is heavily qualified.

## 5.7 Status of the weights

Throughout this chapter the model carries `weightStatus: PLACEHOLDER`. All
criteria are equally weighted within their level.

This is enforced rather than merely noted. The model synchronisation script warns
on every run; the interface displays a standing notice; and the weight-derivation
pipeline refuses to mark the model `ELICITED` without usable elicitation
responses. Scores computed under placeholder weights are structurally valid and
**must not be reported as research results**. Chapter 6 describes the elicitation
that replaces them.

## 5.8 Purpose and scope of this chapter

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
| Scoring **method** (band mapping, weighted aggregation, defuzzification) | Real default outcomes, SBA National | §5.10–5.5 |
| **Criterion weights** | Expert elicitation, Best-Worst Method | Chapter 6 |
| Full 49-criterion **tree** | Design contribution; not empirically validated | §5.18 |

The distinction matters. A claim that "the model was validated" would be false.
What is validated here is the scoring machinery, on a proxy dataset, for the
observable subset of criteria.

## 5.9 Dataset

The SBA National dataset (Li, Mickel and Taylor, 2018) records 899,164 loan
guarantees issued by the U.S. Small Business Administration between 1987 and
2014, with realised outcomes in `MIS_Status` (`P I F` = paid in full, `CHGOFF` =
charged off). It is the largest public dataset of small-business lending with
ground truth, and is widely used in credit-scoring research and teaching.

After removing 1,997 records with no usable outcome, 897,167 remain, with an
overall default rate of 17.56%.

### 5.9.1 Outcome-derived fields

Three fields are populated only after a loan has defaulted: `ChgOffPrinGr`
(charged-off principal), `ChgOffDate`, and `BalanceGross`. A model given any of
them reads the answer rather than predicting it. They are dropped in
`prepare_sba.py`, and their absence is asserted before the prepared file is
written.

### 5.9.2 Right-censoring

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
§5.18.

## 5.10 A contaminated predictor

### 5.10.1 How the problem surfaced

Initial benchmarking produced a gradient-boosting AUC of 0.9726 under random
splitting and 0.9461 under temporal splitting. Credit-scoring models on
small-business data do not ordinarily discriminate this well. The result was
treated as a symptom rather than an achievement.

Permutation importance showed the model to be, in substance, a function of a
single variable: shuffling `term_years` cost 0.395 AUC, while no other feature
cost more than 0.008. Yet `Term` as a monotone predictor reaches only 0.82. The
discrimination was coming from a **non-monotone** structure in the variable.

### 5.10.2 The structure

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

### 5.10.3 Ruling out cohort composition

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

### 5.10.4 The mechanism is not established

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

## 5.11 Consequences for reported performance

Two model specifications were run. The **clean** specification excludes `Term`
and every feature derived from it; the **contaminated** specification adds them
back, solely to quantify the inflation.

AUCs are reported with 95% stratified bootstrap confidence intervals (300
replicates, positives and negatives resampled separately so the interval
reflects uncertainty in discrimination rather than in prevalence).

| Model | Fitted | Random AUC [95% CI] | Temporal AUC [95% CI] |
|---|:--:|---|---|
| **Clean specification** | | | |
| Expert scorecard | no | 0.4144 [0.4111, 0.4175] | 0.5275 [0.5252, 0.5296] |
| Logistic regression | yes | 0.6745 [0.6722, 0.6774] | 0.4565 [0.4545, 0.4586] |
| Gradient boosting | yes | 0.7898 [0.7877, 0.7926] | 0.6076 [0.6053, 0.6097] |
| **Contaminated specification** | | | |
| Logistic regression | yes | 0.8452 [0.8433, 0.8472] | 0.7854 [0.7839, 0.7869] |
| Gradient boosting | yes | 0.9726 [0.9718, 0.9732] | 0.9461 [0.9453, 0.9469] |
| *Term-roundness probe* | no | *0.8870* | *0.8965* |

**The intervals do not overlap.** Gradient boosting under the clean
specification tops out at 0.7926 on a random split; the contaminated
specification starts at 0.9718. On temporal validation the gap is wider still —
[0.6053, 0.6097] against [0.9453, 0.9469]. With 195,000–275,000 test cases the
estimates are precise enough that the leakage effect cannot be attributed to
sampling variation.

Paired DeLong tests confirm this formally. Because the models are compared on
identical cases, the paired test is the correct one; treating the AUCs as
independent would overstate the uncertainty.

| Comparison | Protocol | AUCs | p |
|---|---|---|---|
| Leakage effect, gradient boosting | random | 0.7898 vs 0.9726 | < 0.001 |
| Leakage effect, gradient boosting | temporal | 0.6076 vs 0.9461 | < 0.001 |
| Leakage effect, logistic regression | random | 0.6745 vs 0.8452 | < 0.001 |
| Leakage effect, logistic regression | temporal | 0.4565 vs 0.7854 | < 0.001 |
| Gradient boosting vs logistic, clean | both | — | < 0.001 |

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

## 5.12 Validation protocol matters independently

Under the clean specification, gradient boosting scores 0.7898 on a random split
and 0.6076 on a temporal split — a gap of **0.182 AUC**. Random splitting places
loans from the same economic cycle in both training and test sets, so the model
is partly recalling conditions rather than generalising to unseen ones.

Logistic regression falls to 0.4565 temporally — below chance. Trained on
1990–2003 (9.1% default) and tested on 2004–2010 (35.9% default), the linear
model does not merely lose accuracy; its ranking inverts. This is a substantive
finding about credit-scoring practice: **a linear scorecard fitted to a benign
cycle can rank borrowers backwards in a stressed one.**

## 5.15 The expert scorecard: a negative result

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

## 5.18 Limitations

**Jurisdiction.** SBA data reflects U.S. government-guaranteed small-business
lending. Sri Lankan SME credit differs in legal environment, collateral practice,
and macroeconomic volatility. Nothing here transfers directly.

**The fuzzy layer is not exercised.** Every SBA-observable criterion is
quantitative, so each input enters as a degenerate triangular fuzzy number
`[x,x,x]`. Centroid defuzzification returns `x`, and the fuzzy weighted average
reduces exactly to an ordinary weighted mean. **On this dataset the fuzzy
machinery does no work.** It is exercised only by qualitative criteria, which SBA
data does not contain. What §5.10–5.6 validates is band mapping and weighted
aggregation, not fuzzy inference.

**Maturity filtering biases composition.** Restricting to fully-matured loans
removes censoring but over-represents short-term facilities in later cohorts.

**Weights were placeholders.** All results here use equal weights within each
level, so they test structure rather than the elicited model. Section 5.16 bounds
how much this matters: within ±25% perturbation the ranking is preserved
(ρ ≈ 0.98) and ~94% of risk bands are unchanged. The limitation stands, but its
magnitude is now measured rather than merely acknowledged.

**The independence test uses thin development proxies.** SBA data carries
employment only; five of the nine items in clause 5 have no counterpart. §5.17
tests the employment dimension of development impact, not the whole objective.

**The proposed model is not calibrated.** It produces an ordinal risk band, not a
probability of default. Section 5.13 shows that even trained probabilistic models
lose calibration badly across time periods; the proposed model does not offer a
probability to lose. It must not be used for pricing or provisioning.

**The sensitivity analysis uses a simulated population.** It characterises the
model's response to weight change; it says nothing about how real Sri Lankan SME
applications are distributed, and the two must not be confused.

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

## 5.19 Summary

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
6. The model is robust to weight perturbation within the range experts plausibly
   disagree over (ρ ≈ 0.98 and ~94% band stability at ±25%), which bounds the
   distortion introduced by reporting under placeholder weights.
7. The criteria tree is structurally asymmetric: a development-impact criterion
   carries four to seven times the leverage of a credit-risk criterion over its
   objective, a direct consequence of clause 5 being one section of the source
   form.
8. The two objectives are **not** independent on this population (r = +0.40, or
   +0.36 with disjoint inputs), which partly contradicts the premise the
   non-aggregation design was justified on. They nonetheless band the same
   facility differently 88.2% of the time, which is the stronger argument for
   reporting them separately.
9. Development impact is positively associated with default (10.8% in the lowest
   band against 30.3% in the highest). Reported as association, not cause; if it
   survives proper controls, a development mandate carries a measurable credit
   cost.
10. At realistic cost ratios under temporal validation, none of the models beats
    the better fixed policy — discrimination at this level does not convert into
    economic value.
11. Calibration degrades far more sharply than discrimination across time periods:
   gradient-boosting reliability worsens roughly 700-fold (0.00005 to 0.03705),
   with the model systematically under-predicting default — pricing an observed
   45% risk at 20%. For a lender this is the more consequential failure, because
   it is less visible than a fall in discrimination.

Findings 1 and 5 are the contributions of this chapter. Finding 1 is a caution to
users of a widely-adopted benchmark; finding 5 justifies the methodological
design of the study.

---
