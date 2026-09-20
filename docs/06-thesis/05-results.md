# 5 RESULTS

## 5.1 The derived criteria model

The derivation produced forty-nine criteria across seven dimensions and two
objectives. @tbl:criterion-counts-source-clauses gives the count for each
dimension together with the clauses of the form it derives from. Six of the
seven dimensions belong to credit risk; the seventh carries the whole of the
development-impact objective, an asymmetry inherited from the source document
that Section 5.16.3 shows to have consequences for weighting.

[Table: criterion-counts-source-clauses | Criterion counts and source clauses by dimension]

| Objective | Dimension | Criteria | Form clauses |
|---|---|---:|---|
| Credit Risk | Borrower & Management Capacity | 6 | 2.8, 2.10, 3.2, 3.4 |
| | Credit History & Banking Conduct | 5 | 2.11, 2.14 |
| | Historic Financial Performance | 9 | 2.13, 2.15–2.18 |
| | Project Viability & Projections | 8 | 3.1.3, 3.7, 4 |
| | Market & Competitive Position | 7 | 3.10 |
| | Risk, Security & Compliance | 6 | 3.3, 3.5, 3.6, 3.11, 3.12, 6.5 |
| Development Impact | Economic & Social Contribution | 8 | 5, 3.4.1 |
| Total | 7 dimensions | 49 | |

Twenty-eight criteria are quantitative and twenty-one qualitative. The model is
held in a single machine-readable file as the single source of truth,
consumed by both the web application and the analysis pipeline.

## 5.2 The dual-objective structure

### 5.2.1 Rationale

Clause 5 of the form, *Economic Consideration*, scores nine before/after
outcomes: manpower, women's participation, local raw material usage, productive
capacity, production, export sales, import substitution, value added, and
foreign exchange earnings. Clause 3.4.1 separately disaggregates employment by
gender.

These are not credit risk. A project can employ many people, substitute imports
and earn foreign exchange while still being a poor credit; the reverse also
holds. People's Bank is a state bank with a development mandate, and its
appraisal form reflects that it is being asked to serve two objectives at once.

Mainstream credit scoring optimises a single objective: the probability of
repayment. Applying that framing here would mean discarding clause 5 entirely,
deleting the developmental half of the institution's own mandate because it does
not fit the model.

### 5.2.2 Design decision

The model therefore carries two objectives and reports them separately. They are
never combined into a single number.

This is enforced in the engine, not left to convention: a result record holds
an array of objective results, and no code path produces an overall score. The
interface presents them side by side; the exported report presents them as
distinct sections with an explicit note that the trade-off is a matter for the
approving authority.

The reason is that a weighted combination would destroy the information the
structure exists to expose. A facility scoring 80 on credit and 40 on
development and one scoring 60 on both are materially different propositions,
and a combined score of 60 would render them identical. Making the divergence
visible is the contribution; resolving it is a policy question that belongs to
the bank, not to the model.

Verification of this behaviour appears in the test case of Section 5.6: the same
application scored 80.2 on credit risk (band A) and 74.6 on development impact
(band B).

## 5.3 The completeness gate

### 5.3.1 A problem found by testing

During verification, an appraisal with only seven of forty-nine criteria
entered, 14% complete, returned a credit risk score of 73.7 and the
recommendation *"Band B: recommend with conditions."*

The arithmetic was correct. Weight renormalisation (Section 4.11.3) had worked
exactly as designed: the seven entered criteria carried the full weight, and
they happened to score well. But the system was confidently recommending a
facility on almost no information, and nothing in the output signalled that.

This is a genuine hazard of renormalisation, and it is not specific to this
implementation. A sparse appraisal produces a plausible score while its
evidential basis collapses, and the score itself gives no indication of the
difference.

### 5.3.2 Response

An objective assessed below a completeness threshold (0.6) returns its score but
no risk band and no recommendation. The result carries a *sufficient* flag and a
list of outstanding criteria, and the interface tells the officer what is
missing instead of offering a number to sign against.

@fig:completeness-gate-refusal shows the gate holding. Credit risk stands at
78.7, which on a complete file would be a comfortable Band B, and the system
declines to say so: 7% of the objective has been assessed against the 60%
required. The number is still shown, because hiding it would be its own kind of
dishonesty, but no band and no recommendation accompany it.

[Image: system-completeness-gate.jpg | completeness-gate-refusal | The completeness gate refusing to recommend. A credit-risk score of 78.7 is displayed, and withheld from banding, because only 7% of the objective has been assessed.]

The gate is deliberately a refusal to answer, not a scoring adjustment.
Discounting the score for incompleteness would have preserved the false
impression that the system had an opinion. It does not; it has insufficient
information, and saying so is the correct output.

## 5.4 Explainability

Each criterion's contribution is computed as its normalised weight times its
score, expressed in points of the parent's score. Contributions sum exactly to
the parent score, which is what makes the breakdown a decomposition rather than
a decoration.

The interface presents, for each dimension: its score, its contribution to the
objective, its completeness, and a table of constituent criteria showing raw
value, derived score and contribution, each labelled with its source clause. An
officer can therefore trace any recommendation from the headline score down to
the clause of the bank's own form that produced it.

@fig:completed-appraisal-result shows a completed appraisal. The two objectives
are reported side by side and are never added together: the same facility scores
68.0 on credit risk, which bands B and carries a recommendation with conditions,
and 26.0 on development impact, which bands D and carries a recommendation to
decline. A single combined figure would have averaged those into a middling
number that describes neither.

[Image: system-result.jpg | completed-appraisal-result | A completed appraisal. The two objectives are scored and banded separately and are never combined. Each dimension's contribution is expressed in points of the objective score, and each criterion shows its entered value, its derived score, its contribution and the clause it comes from.]

Beneath the two objective scores, each dimension's contribution is given in
points of the objective score, and every criterion shows the value entered, the
score it mapped to, and the points it contributed. Borrower and management
capacity scores 94.4 and contributes 15.7 points; project viability scores 47.0
and contributes 7.8. The contributions sum to the objective score exactly, so
the breakdown accounts for the whole of it and not merely for the part that is
convenient to explain.

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

The engine carries a structural test suite covering
three cases: a sound manufacturing expansion, a thin startup with a DSCR
breach, and a deliberately incomplete file. @tbl:behavioural-tests-scoring-engine
lists the properties asserted and the result of each.

The suite covers the scoring engine, the validation schemas and the
authorisation logic, 62 tests in total. Server Actions are reachable by direct
POST, not only through the application's own forms, so every action validates
its input before use, and validation failures report which field failed without
echoing the submitted value back.

[Table: behavioural-tests-scoring-engine | Behavioural tests of the scoring engine and their outcomes]

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
| Weight status correctly reflects the elicitation state | pass |

The system was additionally verified end to end through the browser: all 49
criteria entered through the interface, producing credit risk 80.2 (band A)
against development impact 74.6 (band B), persisted to the database, rendered
with full contribution breakdown, and exported to a valid Word in bank
format.

These are structural checks. They establish that the engine behaves as
specified, not that its scores are accurate. Accuracy is the subject of Chapter
5, and the answer given there is heavily qualified.

## 5.7 Status of the weights

The model now carries an elicited state, recording eleven respondents, three
level-responses excluded for inconsistency, and the date. Section 6.1 reports
the elicitation; the weights themselves are in Section 6.1.4.

The state is machine-enforced rather than merely documented, and that mattered.
While elicitation was outstanding the model carried the placeholder state, all
criteria equally weighted within their level. The synchronisation script warned
on every run, the interface displayed a standing notice, and the
weight-derivation pipeline refused to mark the model elicited without usable
responses. A claim check also fails the build if any chapter still describes the
weights as placeholders once the model says otherwise, which is how the stale
passages in this chapter were caught when elicitation completed.

The design principle is worth stating separately from this instance: a
placeholder that is only described in prose will outlive the condition it
describes, because nothing breaks when the condition changes.

## 5.8 Empirical evaluation: purpose and scope

The preceding sections presented a criteria tree of 49 criteria derived from the
People's Bank *Project / Business Appraisal Report for SME Credit Facility*, and
a scoring method that maps appraisal inputs onto two separate objectives. The
rest of this chapter asks what can and cannot be established about that model
from data.

The scope must be stated precisely, because the answer is narrower than the
question a reader might expect.

The criteria tree is instrument-specific. It scores debt service cover, the
competitive forces bearing on the applicant's market, management quality,
environmental risk, and nine development outcomes. No public dataset contains
those variables. Access to People's Bank's own historical files was not
available within this study, and would in any case be confidential.

The validation is therefore split three ways, and @tbl:three-validation-claims-evidence keeps the three claims separate: what is being validated, the evidence available for it, and where that evidence is reported.

[Table: three-validation-claims-evidence | The three validation claims and the evidence available for each]

| Component | Evidence | Reported in |
|---|---|---|
| Scoring method (band mapping, weighted aggregation, defuzzification) | Real default outcomes, SBA National | Sections 5.10 to 5.12 |
| Criterion weights | Expert elicitation, Best-Worst Method | Chapter 6 |
| Full 49-criterion tree | Design contribution; not empirically validated | Section 5.20 |

The distinction matters. A claim that "the model was validated" would be false.
What is validated here is the scoring machinery, on a proxy dataset, for the
observable subset of criteria.

One point about how this chapter is written. Results are conventionally
presented without interpretation, with the reading of them deferred to the
discussion. The findings here form a chain, in which each experiment exists
because the one before it ruled something out, and presenting them as a bare
sequence of tables would leave the reader unable to follow why any of them was
run. This chapter therefore carries the reasoning needed to make the next
experiment intelligible, and no more. Every claim about what the findings mean
for practice, for the literature and for the artefact is held back to
Chapter 6.

## 5.9 Dataset

The SBA National dataset [33] records 899,164 loan
guarantees issued by the U.S. Small Business Administration between 1987 and
2014, with realised outcomes in *MIS_Status* (*P I F* = paid in full, *CHGOFF* =
charged off). It is the largest public dataset of small-business lending with
ground truth, and is widely used in credit-scoring research and teaching.

After removing 1,997 records with no usable outcome, 897,167 remain, with an
overall default rate of 17.56%.

### 5.9.1 Outcome-derived fields

Three fields are populated only after a loan has defaulted: *ChgOffPrinGr*
(charged-off principal), *ChgOffDate*, and *BalanceGross*. A model given any of
them reads the answer instead of predicting it. They are dropped in
the data preparation step, and their absence is asserted before the prepared file is
written.

### 5.9.2 Right-censoring

A loan approved in 2013 on a fifteen-year term cannot have defaulted by the 2014
data cut-off. Such loans appear to perform well only because insufficient time
has elapsed.

Restricting to the 1990–2010 approval window of 847,980 loans and separating those whose full term elapsed before the cut-off gives the rates in @tbl:default-rate-censoring-status.

[Table: default-rate-censoring-status | Default rate by censoring status, 1990-2010 approvals]

| Cohort | n | Default rate |
|---|---:|---:|
| Censored (term not yet elapsed) | 195,696 | 7.77% |
| Fully matured | 652,284 | 20.41% |

The difference is large enough to dominate any model permitted to infer
censoring status. All analysis below uses the 652,284 fully-matured loans. This
biases the sample toward shorter terms in later years, which is noted as a
limitation in Section 5.20.

## 5.10 A contaminated predictor

### 5.10.1 How the problem surfaced

Initial benchmarking produced a gradient-boosting AUC of 0.9726 under random
splitting and 0.9461 under temporal splitting. Credit-scoring models on
small-business data do not ordinarily discriminate this well. The result was
treated as a symptom rather than an achievement.

Permutation importance showed the model to be, in substance, a function of a
single variable: shuffling term in years cost 0.395 AUC, while no other feature
cost more than 0.008. Yet *Term* as a monotone predictor reaches only 0.82. The
discrimination was coming from a non-monotone structure in the variable.

### 5.10.2 The structure

@tbl:default-rate-exact-term gives the default rate at each exact term value for 2007 approvals, which is where the shape of the relationship becomes visible.

[Table: default-rate-exact-term | Default rate by exact term in months, 2007 approvals]

| Term (months) | n | Default rate |
|---:|---:|---:|
| 58 | 634 | 92.1% |
| 59 | 663 | 86.7% |
| 60 | 5,040 | 11.1% |
| 61 | 641 | 92.2% |
| 62 | 609 | 90.1% |
| 63 | 674 | 81.0% |
| 64 | 596 | 88.1% |

A one-month difference in contractual term cannot produce an eight-fold change in default rate. Sixty months is not economically distinct from fifty-nine. @fig:default-rate-exact-contractual plots the same relationship across the full range of terms, and the alternation is regular rather than noisy.

[Image: adjacent_terms.png | default-rate-exact-contractual | Default rate by exact contractual term, 2007 approvals. Terms that are multiples of twelve are shown in blue.]

Only the sixty-month bar falls below 80%, and it is the only term in the range that is a multiple of twelve. The pattern is roundness. Across the 1990–2010 cohort:

- 86.4% of repaid loans have a term that is an exact multiple of twelve
- 8.5% of charged-off loans do
- Charged-off loans are distributed almost uniformly across *Term mod 12*
  (7.7%–9.0% in each of the twelve residues, against 86.4% at residue zero for
  repaid loans)

The single boolean *"is the term a multiple of twelve"*, a quantity with no economic content whatsoever, achieves AUC 0.8894. @fig:distribution-across-term-mod shows the distribution behind that figure: repaid facilities pile up at residue zero while charged-off facilities spread almost uniformly across the twelve residues.

[Image: term_leakage.png | distribution-across-term-mod | Left: the share of facilities at each value of *Term* modulo twelve, separately for those repaid and those charged off. Right: default rate within each approval year, for facilities whose term is a multiple of twelve and for the rest.]

The two panels say different things about the same field. The left shows where the terms sit: repaid facilities are concentrated almost entirely at residue zero, while charged-off facilities are spread across all twelve residues at between 7.7% and 9.0% each. The right shows that the gap between the two groups is present in every approval year, and widens as the overall default rate climbs after 2003.

### 5.10.3 Ruling out cohort composition

Irregular-term loans became more common over the period, and so did defaults, so
the association might be an artefact of pooling cohorts. It is not. @tbl:default-rate-roundness-auc computes the association within each approval year separately.

[Table: default-rate-roundness-auc | Default rate and roundness AUC within each approval year]

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

The association holds in every year, within a band of 0.859–0.900, and @fig:discrimination-achieved-term-roundness plots that year-by-year discrimination. Cohort composition is excluded.

[Image: roundness_by_year.png | discrimination-achieved-term-roundness | Discrimination achieved by the term-roundness boolean alone, computed separately within each approval year.]

Discrimination stays between 0.8589 and 0.8995 across the whole twenty-one year period. A variable that is genuinely a cohort artefact would not hold a band that narrow across two recessions and a doubling of the default rate.

### 5.10.4 The mechanism is not established

The obvious explanation is that *Term* for defaulted loans has been overwritten
with elapsed time to charge-off. This was tested and rejected. Among 156,266
charged-off loans with both disbursement and charge-off dates:

- correlation between *Term* and actual months to charge-off: 0.043
- proportion matching within ±3 months: 5.0%

*Term* is not survival time. That left three possibilities: the value is
rewritten on restructuring, recomputed under some servicing convention, or
introduced when this derivative file was assembled. The third would make the
finding uninteresting, a packaging error in one upload rather than a property of
the data, and Section 5.10.5 rules it out.

The dataset codebook documents *Term* as "loan term in months", the contractual
term. The observed distribution is not consistent with that definition for
charged-off loans. The contamination is established; the choice between the
remaining two explanations is not. This study reports it accordingly and does
not assert a mechanism it has not demonstrated.

### 5.10.5 The artefact is in the SBA's own records

The derivation hypothesis can be tested without contacting anyone. The SBA publishes loan-level extracts of the same programme under the Freedom of Information Act (FOIA), refreshed quarterly;
the release used here is current to 30 June 2026. If the pattern appears there,
the derivative did not create it.

It appears there. @tbl:term-roundness-sba-foia compares the two files across the 603,665 resolved 7(a) facilities approved between fiscal years (FY) 2000 and 2009.

[Table: term-roundness-sba-foia | Term roundness, SBA FOIA 7(a) against SBA National]

| | SBA FOIA 7(a) | SBA National (derivative) |
|---|---:|---:|
| Repaid, term a multiple of twelve | 82.02% | 86.4% |
| Charged off, multiple of twelve | 8.46% | 8.5% |
| AUC of the roundness boolean | 0.8678 | 0.8894 |

and it holds in every approval year, between 0.8562 and 0.8808. The
contamination is not an artefact of the derivative file. It is present in the
authoritative publication, which removes one of the three candidate explanations
and moves the finding from a problem with one dataset to a property of the
records themselves.

**Nor is it historical.** The same release covers FY2010–FY2019, a decade lying
entirely outside the derivative's coverage and now old enough to have resolved.
Across 428,652 resolved facilities there the boolean reaches AUC 0.8815, with
repaid facilities 86.44% round-termed against 10.15% for charge-offs, and every
approval year falls between 0.8587 and 0.8904.

Taken together the two extracts span 1,032,317 resolved facilities across twenty
consecutive approval years, FY2000 to FY2019, with the probe never leaving the
range 0.8562 to 0.8904. This is not a defect in an old teaching file. It is a
live property of loan data the SBA published in June 2026, and anyone building a
model on the current release is exposed to it exactly as anyone using the 2014
derivative was.

This is not an independent replication and is not claimed as one. The SBA
National dataset is itself built from SBA FOIA releases, so these are the same
underlying loans at a different vintage, not a second source. What the
comparison settles is where the artefact originates, not whether it recurs
elsewhere.

The same release supplies a control. The 504 programme is a different facility
type under the same agency, released in the same extract, and its terms are
fixed by programme design: 95.5% are written at exactly 240 months. There the
boolean discriminates at AUC 0.4997, indistinguishable from chance, and
charged-off facilities are marginally *more* round-termed (99.85%) than repaid
ones (99.80%).

That contrast is informative. In a programme where the term is set by the
programme and effectively never varies, charged-off records retain their round
terms. In 7(a), where the term is negotiated facility by facility, charged-off
records overwhelmingly do not. Whatever produces the pattern acts on 7(a)
records and not on 504 records, which is consistent with a servicing or
restructuring process that touches the term field, and inconsistent with
anything applied uniformly across the agency's data. It narrows the mechanism;
it does not establish it, and the distinction is maintained here.

### 5.10.6 Is twelve doing the work?

The finding rests on one boolean, so the obvious challenge is whether twelve
matters at all. If "multiple of two" or "multiple of five" discriminated equally
well, this would not be about round contractual terms and the interpretation
above would be wrong.

Twenty moduli were tested on the 651,501 matured facilities with a positive
term. The strata overlap by construction — every multiple of twelve is also a
multiple of six, four, three and two — so raw discrimination is reported
alongside *residual* discrimination computed within the multiples of twelve and
within the non-multiples separately, which strips out whatever a modulus inherits from twelve. @tbl:share-terms-divisible-modulus reports both for every modulus from two to twelve.

[Table: share-terms-divisible-modulus | Share of terms divisible by each modulus, with the resulting AUC]

| Modulus | Share divisible | Raw AUC |
|---:|---:|---:|
| 12 | 70.07% | 0.8859 |
| 6 | 74.39% | 0.8600 |
| 4 | 74.74% | 0.8109 |
| 3 | 80.24% | 0.7934 |
| 2 | 84.04% | 0.7125 |
| 7 | 34.90% | 0.6291 |
| 5 | 33.24% | 0.5856 |
| 13 | 2.23% | 0.4699 |
| 11 | 2.91% | 0.4660 |

Twelve is the strongest, and the ordering of its divisors (12 > 6 > 4 > 3 > 2)
is exactly the dilution pattern expected if multiples of twelve are the carrier:
each coarser modulus admits more non-annual terms and loses discrimination in
proportion. The moduli that do *not* divide twelve behave quite differently.
Eleven and thirteen sit at or below chance, at 0.4660 and 0.4699. It is not the
case that any modulus would do.

One qualification, and it refines rather than threatens the finding. Within the
facilities that are *not* multiples of twelve, "multiple of three" still reaches
0.5888 and "multiple of six" 0.5684. Some signal therefore attaches to
quarter- and half-year terms independently of whole years. The pattern is
roundness on a calendar grid, not annual roundness alone, which is if anything
the more natural reading of a contractual convention.

(The 0.8859 here and the 0.8894 in Section 5.10.2 differ because this probe
additionally excludes facilities with a term of zero. Both are produced by the
same analysis.)

### 5.10.7 The contamination reaches the dataset's own documentation

Li, Mickel and Taylor [33], the paper that documents this dataset, derive a
feature from *Term* themselves. They define a dummy *RealEstate*, set to 1 where
*Term* ≥ 240 months, reasoning that only real-estate-backed loans run twenty
years or more, and report those loans defaulting at 1.64% against 21.16% for the
rest. The 1990–2010 cohort used here reproduces that closely: 1.45% against
20.69%.

If *Term* carries outcome information, a feature derived from it does too. Two
explanations were tested.

**Right-censoring: tested and rejected.** A twenty-year loan approved after 1994
cannot mature before the 2014 cut-off, and indeed 87.6% of these facilities are
censored. But restricting to the ones that did mature *lowers* their default
rate, to 0.56%, against 1.57% for the censored. Censoring does not explain the
contrast, and the hypothesis is recorded as refuted rather than dropped.

**Roundness: the dominant factor, but not a simple confound.** *Term* ≥ 240
requires a value at or above a multiple of twelve, and the group is 95.96%
round-termed against 69.27% for the rest. Stratifying by roundness does not
reduce the contrast so much as split it in two: among matured facilities the gap
is 20.40 points unstratified, 2.51 points within round terms, and 50.32 points
within irregular ones.

What actually dominates is roundness itself. Among matured facilities under 240
months, round terms default at 2.58% and irregular terms at 62.39%. The
documented *RealEstate* contrast is largely a restatement of that, and the
separation surviving inside the irregular stratum is real and unexplained here.

The point is not that Li, Mickel and Taylor made an error. Their paper documents
a teaching dataset and derives a feature on entirely reasonable economic
reasoning. The point is that a field carrying outcome information contaminates
whatever is built from it, including the dataset's own documentation, and that
nothing in the published description of either would let a reader detect it.

## 5.11 Consequences for reported performance

Two model specifications were run. The clean specification excludes *Term* and
every feature derived from it; the contaminated specification adds them back,
solely to quantify the inflation.

AUCs are reported with 95% stratified bootstrap confidence intervals (300
replicates, positives and negatives resampled separately so the interval
reflects uncertainty in discrimination rather than in prevalence).
@tbl:discrimination-random-temporal-validation reports all four model-by-protocol
combinations.

[Table: discrimination-random-temporal-validation | Discrimination under random and temporal validation, with intervals]

| Model | Fitted | Random AUC [95% confidence interval] | Temporal AUC [95% CI] |
|---|:--:|---|---|
| Clean specification | | | |
| Expert scorecard | no | 0.4144 [0.4111, 0.4175] | 0.5275 [0.5252, 0.5296] |
| Logistic regression | yes | 0.6745 [0.6722, 0.6774] | 0.4565 [0.4545, 0.4586] |
| Gradient boosting | yes | 0.7898 [0.7877, 0.7926] | 0.6076 [0.6053, 0.6097] |
| Contaminated specification | | | |
| Logistic regression | yes | 0.8452 [0.8433, 0.8472] | 0.7854 [0.7839, 0.7869] |
| Gradient boosting | yes | 0.9726 [0.9718, 0.9732] | 0.9461 [0.9453, 0.9469] |
| *Term-roundness probe* | no | *0.8870* | *0.8965* |

**The intervals do not overlap.** Gradient boosting under the clean
specification tops out at 0.7926 on a random split; the contaminated
specification starts at 0.9718. On temporal validation the gap is wider still:
[0.6053, 0.6097] against [0.9453, 0.9469]. With 195,000–275,000 test cases the
estimates are precise enough that the leakage effect cannot be attributed to
sampling variation.

Paired DeLong tests confirm this formally. Because the models are compared on identical cases, the paired test is the correct one; treating the AUCs as independent would overstate the uncertainty. @tbl:paired-delong-tests-leakage gives each comparison.

[Table: paired-delong-tests-leakage | Paired DeLong tests of the leakage and protocol effects]

| Comparison | Protocol | AUCs | p |
|---|---|---|---|
| Leakage effect, gradient boosting | random | 0.7898 vs 0.9726 | < 0.001 |
| Leakage effect, gradient boosting | temporal | 0.6076 vs 0.9461 | < 0.001 |
| Leakage effect, logistic regression | random | 0.6745 vs 0.8452 | < 0.001 |
| Leakage effect, logistic regression | temporal | 0.4565 vs 0.7854 | < 0.001 |
| Gradient boosting vs logistic, clean | both | — | < 0.001 |

Each row compares two models or two protocols on the same facilities, so
the p-values are those of a paired test. Three observations follow.

**The inflation is severe.** Gradient boosting rises from 0.6076 to 0.9461 on
temporal validation, 0.339 AUC obtained from a contaminated field.

**The probe bounds the artefact.** A single boolean with no economic meaning
reaches 0.8870 and 0.8965. Any model on this dataset scoring in that region,
having been given *Term*, is largely reproducing the artefact.

**Tree models are more exposed than linear ones.** Logistic regression, monotone
in term, gains 0.33 AUC from contamination; gradient boosting, free to split on
exact values, gains more and reaches further. Published results on this dataset using tree ensembles with the *Term* field should be read with this in mind. @fig:discrimination-without-term-field sets the four values side by side against the level the roundness boolean reaches on its own.

[Image: leakage_inflation.png | discrimination-without-term-field | Discrimination with and without the *Term* field, under both validation protocols. The dashed line marks the level the roundness boolean reaches on its own.]

The dashed line in each panel marks what the roundness boolean reaches on its own: 0.887 under random splitting and 0.8965 under temporal splitting. Under temporal validation every trained model sits below that line when the field is excluded and well above it when it is included, which places the gain in the field and not in the model that consumes it.

## 5.12 Validation protocol matters independently

Under the clean specification, gradient boosting scores 0.7898 on a random split
and 0.6076 on a temporal split, a gap of 0.182 AUC. Random splitting places
loans from the same economic cycle in both training and test sets, so the model
is partly recalling conditions instead of generalising to unseen ones.

Logistic regression falls to 0.4565 temporally, below chance. Trained on
1990–2003 (9.1% default) and tested on 2004–2010 (35.9% default), the linear
model does not merely lose accuracy; its ranking inverts. This is a substantive
finding about credit-scoring practice: a linear scorecard fitted to a benign
cycle can rank borrowers backwards in a stressed one.

## 5.13 Calibration: ranking is not the same as being right

AUC measures whether a model *orders* borrowers correctly. It says nothing about
whether a predicted probability means what it says. A bank pricing risk, setting
provisions, or reporting expected loss needs the second property, and a model
can have the first without it.

Calibration is reported here as the Brier score [39] under Murphy's
decomposition [40], *Brier = reliability − resolution + uncertainty*,
where reliability measures how far predicted probabilities sit from observed
rates (lower is better; zero is perfect) and resolution measures how far the model separates cases from the base rate (higher is better). @tbl:brier-score-decomposed-reliability gives the decomposition for both models under both protocols.

[Table: brier-score-decomposed-reliability | Brier score decomposed into reliability and resolution]

| Model | Protocol | Brier | Reliability | Resolution |
|---|---|---:|---:|---:|
| Gradient boosting (clean) | random | 0.1319 | 0.00005 | 0.03003 |
| Logistic regression (clean) | random | 0.1539 | 0.00091 | 0.00838 |
| Gradient boosting (clean) | temporal | 0.2592 | 0.03705 | 0.00729 |
| Logistic regression (clean) | temporal | 0.2882 | 0.05803 | 0.00121 |

Reliability degrades by roughly 700× for gradient boosting, from 0.00005 to
0.03705, and by 64× for logistic regression. Under random splitting the boosted
model is almost perfectly calibrated: its reliability diagram sits on the
diagonal. Under temporal validation the entire curve lifts above the diagonal,
meaning the model systematically under-predicts default. At a predicted
probability of 0.2 the observed default rate is approximately 0.45.

The mechanism is straightforward. The model is trained on 1990–2003 approvals
defaulting at 9.1% and tested on 2004–2010 approvals defaulting at 35.9%. It has learned the base rate of a benign period and carries it into a stressed one. @fig:reliability-diagrams-random-temporal shows this directly: under temporal validation the curve lifts away from the diagonal, in the direction of under-prediction.

[Image: calibration.png | reliability-diagrams-random-temporal | Reliability diagrams under random and temporal validation. Marker area is proportional to the number of facilities in each bin. Under temporal validation the curve lifts above the diagonal, indicating systematic under-prediction of default.]

The shape is the finding. Under random splitting the gradient-boosting curve follows the diagonal closely, so a predicted 40% means an observed 40%. Under temporal splitting the same curve sits above the diagonal across the whole range: at every level of predicted risk, more facilities defaulted than the model said would.

### 5.13.1 Why this matters more than the AUC result

For a lender this is the more consequential finding. A model whose
discrimination falls is visibly worse and invites scrutiny. A model that still
ranks tolerably but prices a 45% risk as 20% produces provisions that are less
than half what they should be, and does so while appearing to work.

Given Sri Lanka's recent macroeconomic volatility, the implication is direct: a
scorecard calibrated on pre-crisis SME lending should not be assumed to carry
its probability estimates into a stressed period. Recalibration on recent
outcomes is a separate requirement from revalidation of discrimination, and the
two are frequently conflated.

**A caveat on scope.** This concerns the trained benchmark models, not the
criteria model this study proposes. The proposed model produces an ordinal band
rather than a probability, and is therefore not calibrated in this sense at all,
which is itself a limitation (Section 5.20) and the reason it must never be used
to price a facility.

## 5.14 What the models are worth to a lender

AUC weights both error types equally; a lender does not. Approving a facility
that charges off costs the loss given default; declining a sound one costs the
margin forgone. The ratio between them determines where the cut-off belongs.

Expected cost is reported in units of one false positive, so a cost ratio of
10:1 means one bad approval costs as much as ten good declines. The ratio is swept, not assumed, because the right value is a policy question for the
lender.

Two fixed policies provide the floor: approve everything, or decline everything. @tbl:expected-cost-per-application reports the expected cost per application at a 10:1 ratio against the better of those two.

[Table: expected-cost-per-application | Expected cost per application at a 10:1 loss ratio]

| Temporal split, 10:1 | Expected cost | vs best fixed policy |
|---|---:|---:|
| "Decline all" baseline | 0.6411 | — |
| Gradient boosting | 0.6455 | −0.7% |
| Logistic regression | 0.6475 | −1.0% |
| Expert scorecard | 0.6413 | −0.0% |

Under temporal validation, 12 of 15 model/cost-ratio combinations fail to beat
the better fixed policy. At the discrimination levels the clean specification
achieves, AUC 0.6076 against a 35.9% default rate, none of these models earns
its place economically on that cohort. Under random splitting, where
discrimination is higher, the picture improves: gradient boosting saves 10.2% at
a 2:1 ratio.

**An important caveat.** "Decline all" is a floor for comparison, not a
strategy. A bank that declines every application has no business, so this is not
a claim that lenders should stop lending. It is a claim that a model must clear
a low bar before it is worth the process it adds, and on the stressed cohort
these models do not clear it.

The finding is consistent with everything else in this chapter and is reported
without softening.

## 5.15 The expert scorecard: a negative result

The a priori scorecard, whose bands were set from credit reasoning before any
outcome was inspected, achieved AUC 0.4144 (random) and 0.5275 (temporal), at or
below chance. It provides no reliable discrimination on this dataset.

This is reported as it stands. Three readings are available, and the evidence
does not distinguish between the first two:

1. **The proxies are inadequate.** The scorecard was built from SBA-observable
   variables — guarantee share, franchise status, urban/rural — because the
   People's Bank criteria are absent. These are not what the appraisal form
   scores. The strongest legitimate criteria in the tree (DSCR, ISCR, security
   cover, management quality, market position) have no counterpart here.
2. The a priori bands are wrong. Domain reasoning about which direction each
   proxy should point may simply be mistaken. With the scorecard's individual
   features carrying univariate AUC between 0.51 and 0.63, an equal-weighted
   aggregate of several mis-signed weak proxies can land below chance.
3. The method itself does not work: not supported, since the same machinery
   discriminates when given informative inputs, and its arithmetic is verified
   against an independent implementation.

The methodological conclusion is the useful one, and it is stronger than the
individual result:

> An instrument-specific appraisal model cannot be validated against a dataset
> that does not contain its variables. Substituting available proxies for the
> intended criteria does not test the model; it tests the proxies.

This is why the criterion weights are established by expert elicitation (Chapter
6) rather than fitted to borrowed outcome data, and why that choice is a methodological requirement, not a fallback.

## 5.16 How much do the weights matter?

This analysis was carried out while the criteria model still carried placeholder
weights, and that is ordinarily treated as blocking: no elicited weights, no
reportable result. The question underneath — *how much does the output depend on
the weight vector at all?* — was answerable without respondents, and answering
it bounded the damage the placeholders could be doing.

It is retained here, unchanged, because elicitation has since been completed and
Section 6.1.5 checks its prediction against the weights that actually arrived. A
sensitivity analysis that is only reported after the answer is known is worth
less than one that made a prediction first.

### 5.16.1 Method

Two thousand complete appraisals were simulated by drawing each criterion across
its plausible range. The population is synthetic: the object of study is the
model's mathematical behaviour, not any real portfolio, and no claim is made
about real borrowers. Simulation is appropriate precisely because the question
is about the model rather than the world.

Each weight was then perturbed multiplicatively by up to ±p and renormalised,
at 10%, 25%, 50%, 75% and 100%, with 400 draws at each level. For every draw
the whole population was rescored and compared against the equal-weight baseline
on three measures: Spearman rank correlation, the proportion of cases keeping
their risk band, and the largest score shift.

### 5.16.2 Results

@tbl:rank-correlation-band-stability reports all three measures at each perturbation level, for both objectives.

[Table: rank-correlation-band-stability | Rank correlation and band stability under weight perturbation]

| Perturbation | Credit risk ρ | Band unchanged | Development ρ | Band unchanged |
|---:|---:|---:|---:|---:|
| ±10% | 0.9971 | 97.6% | 0.9982 | 97.1% |
| ±25% | 0.9822 | 94.0% | 0.9890 | 92.7% |
| ±50% | 0.9314 | 88.2% | 0.9586 | 85.5% |
| ±75% | 0.8517 | 82.2% | 0.9121 | 78.3% |
| ±100% | 0.7547 | 76.1% | 0.8543 | 71.2% |

At ±25%, a spread wider than experienced practitioners typically differ by, the
ranking is essentially preserved (ρ ≈ 0.98–0.99) and roughly 93–94% of cases
keep their risk band. Degradation beyond that is gradual, not abrupt; even at ±100%, where a weight may be scaled anywhere in [0, 2], rank correlation remains above 0.75. @fig:ranking-stability-risk-band plots both measures against the magnitude of the perturbation.

[Image: weight_sensitivity.png | ranking-stability-risk-band | Ranking stability and risk-band stability against the magnitude of the weight perturbation. Shaded bands show the range down to the fifth percentile across draws; the dotted line marks the level of disagreement practitioners plausibly exhibit.]

**Interpretation.** The model's conclusions do not hinge on the precise weight
vector within the range over which experts plausibly disagree. This does not
make elicitation optional: the weights still need to be defensible, and the 6–7%
of cases whose band changes at ±25% are real appraisals that would receive a
different recommendation. What it does is bound the distortion: results reported
under placeholder weights are unlikely to be qualitatively wrong, and that can
be stated rather than hoped.

### 5.16.3 An unanticipated structural finding

Estimating each criterion's influence separately, by doubling its weight within
its dimension and measuring the shift, exposed an asymmetry in the tree itself, which @tbl:leverage-single-criterion-over quantifies.

[Table: leverage-single-criterion-over | Leverage of a single criterion over its objective]

| Objective | Dimensions | One criterion's share of the objective |
|---|---:|---|
| Credit risk | 6 | 0.0185 – 0.0333 |
| Development impact | 1 | 0.1250 |

A development-impact criterion carries roughly four to seven times the leverage
of a credit-risk criterion over its own objective. Doubling
employment generation moves the development score by 3.06 points and changes
the risk band for 19.2% of cases; doubling account turnover, the most
influential credit criterion, moves the credit score by 0.71 points and changes
5.1% of bands.

This is not an error. It follows directly from the source instrument: clause 5
of the People's Bank form is a single section of nine items, while the
credit-risk material is spread across six sections. The tree faithfully
reproduces that shape. But the consequence should be stated plainly: the
development objective is materially more sensitive to individual weight choices
than the credit objective, so elicitation error there carries more consequence,
and the development weights deserve more respondents, not fewer.

## 5.17 Are the two objectives independent? (RQ4)

The model reports two scores and refuses to combine them. That decision was
justified in Section 5.2.2 on Arvanitis, Stampini and Vencatachellum [29], who
report that development and credit concerns in development-bank appraisal are
"rather independent from each other".

As Section 3.6.2 sets out, their evidence is a *positive but non-significant*
relationship — slope 0.048, p = 0.49 — across the 109 African Development Bank
operations carrying both ratings. That is an underpowered null. A sample of 109
cannot distinguish independence from a moderate association, so the premise the
design rests on has never actually been tested with the power to resolve it.

It can be here, on 652,284 small-business facilities with realised outcomes.

### 5.17.1 The objectives are not independent

@tbl:association-between-credit-risk reports the association between the two scores on all 652,284 facilities.

[Table: association-between-credit-risk | Association between the credit-risk and development-impact scores]

| Measure | Value |
|---|---|
| Pearson r | +0.4003 |
| Spearman ρ | +0.4213 |
| Shared variance (r²) | 0.1602 |

With n this large every correlation is statistically significant, so effect size
is what carries meaning. An r of 0.40 is moderate, not negligible.

The two proxy scores do not draw on disjoint variables, which inflates this:
*NoEmp* feeds both the credit criterion *employees* and the development criterion
*job creation rate*, and *GrAppv* feeds both *loan per employee* and *jobs per
100k*. Recomputing with a development measure sharing no inputs with the credit score, raw jobs supported, gives r = +0.3563. The confound accounts for
part of the association but not most of it.

**This does not contradict Arvanitis et al.; it resolves them.** Their estimate
was positive too, slope 0.048, and simply could not be separated from zero in
109 observations. The direction found here is the same direction they measured,
at a sample size that can actually detect it. The correct reading is not that
the earlier study was wrong, but that a non-significant result in a small sample
was carried forward, by this study among others, as though it had established
independence. It had not.

What is contradicted is the *strong* form of the premise: that the objectives
are independent and therefore that aggregation destroys information. On this
population they are moderately associated, and that form of the argument is no
longer available. Section 5.17.2 sets out why the design decision nevertheless
stands, by a different route.

### 5.17.2 The practical case survives by a different route

Correlation describes average co-movement across a population. It does not say whether the two objectives agree about any *particular* facility, which is the question a combined score actually settles. @tbl:agreement-between-two-objectives answers that question directly.

[Table: agreement-between-two-objectives | Agreement between the two objectives' risk bands]

| Relationship between the two bands | Share of facilities |
|---|---:|
| Same band | 11.8% |
| One band apart | 49.7% |
| Two or more bands apart | 38.4% |
| Disagree at all | 88.2% |

An r of 0.40 leaves enormous scatter. The two objectives place the same facility
in different risk bands 88.2% of the time, and more than a third differ by two
bands or more.

That is the argument for reporting them separately, and it is stronger than the
independence argument it replaces. A combined score would issue one number for
the 88% of cases where the objectives disagree, making a strong-credit,
weak-development facility indistinguishable from one that is middling on both.
Whether the underlying scores correlate on average is beside the point; what a
decision-maker needs is whether *this* application is one of the many where they
diverge.

### 5.17.3 Development impact is associated with higher default

@tbl:default-rate-development-impact gives the realised default rate within each development-impact band.

[Table: default-rate-development-impact | Default rate by development-impact band]

| Development band | n | Default rate |
|---|---:|---:|
| Lowest | 326,491 | 10.80% |
| Middle | 162,746 | 29.77% |
| Highest | 163,047 | 30.32% |

Facilities supporting more employment default substantially more, a spread of
19.5 percentage points.

**Read this as association, not cause.** It is very likely confounded:
facilities creating more jobs tend to be larger, newer, and more expansionary,
and each of those independently raises credit risk. Establishing a causal
relationship would require controls this study has not applied, and the claim is
not made.

But if the association holds under proper controls, it has a direct implication
for a state bank with a development mandate: the developmental objective and the
credit objective may genuinely pull against each other. Development-oriented
lending would then carry a real and measurable credit cost.

That is precisely the trade-off the dual-objective design exists to surface. A
model that averaged the two into one figure would report a middling score and
conceal the fact that the institution is being asked to choose.

## 5.18 Who the models work less well for

The model card recorded, as a stated weakness, that no disparate-impact analysis
had been performed, and that a credit model untested for disparate impact should
not touch real applicants. This section closes as much of that gap as the data
permits.

### 5.18.1 What can and cannot be tested

The SBA file records no legally protected characteristic. There is no race, sex,
age, disability or marital-status field, and nothing that follows is a
protected-attribute audit. Describing it as one would be false.

What the data does carry are the axes along which SME credit exclusion actually
operates in development finance: rurality, firm size, firm age, sector, and
facility size. These are proxies for credit access, not for protected class, and
a model can be clean on every one of them and still discriminate unlawfully. The
analysis is reported for what it is.

Two distinct quantities are measured and must not be conflated. The first is
selection-rate disparity, whether a group is declined more often, assessed
against the four-fifths rule, in the form Feldman et al. [43] formalise. On its own this is weak evidence, because the
groups have genuinely different default rates and a model that declines a
riskier group more often is doing its job. The second is error-rate disparity, which is Hardt, Price and Srebro's [44] equality-of-opportunity criterion:
among borrowers who actually repaid, what share would have been declined. That
measure has no base-rate defence. If creditworthy firms in one group are turned
away at three times the rate of another, the model is worse for that group.

A single portfolio-wide threshold is applied, declining the riskiest 20%,
because that is what a bank does, and it is the condition under which disparate
impact arises. The temporal test cohort is used throughout: 275,487 facilities
approved between 2004 and 2010, default rate 35.89%.

### 5.18.2 Results

The trained gradient booster fails the four-fifths rule on three of the five
attributes; the expert scorecard fails on four of five. @tbl:equal-opportunity-ratios-attribute reports the ratios. Intervals are 95% bootstrap percentiles over 400 resamples of the test cohort, with the decline threshold recomputed inside each resample.

[Table: equal-opportunity-ratios-attribute | Equal-opportunity ratios by attribute, with bootstrap intervals]

| Attribute | Gradient boosting | Expert scorecard |
|---|---|---|
| Rurality | 0.325 [0.308, 0.344] (fails) | 0.183 [0.170, 0.209] (fails) |
| Firm size | 0.832 [0.820, 0.838] (passes) | 0.729 [0.711, 0.746] (fails) |
| Firm age | 0.993 [0.989, 0.997] (passes) | 0.711 [0.707, 0.714] (fails) |
| Sector | 0.773 [0.752, 0.783] (fails) | 0.731 [0.702, 0.758] (fails) |
| Facility size | 0.789 [0.785, 0.793] (fails) | 0.831 [0.828, 0.836] (passes) |

Both measures are ratios of a minimum to a maximum across groups, and that
structure is biased. Sampling noise pushes the observed minimum down and the
maximum up, so a disparity ratio computed this way reads worse than reality even
when no group is treated differently, and the smaller the groups, the worse it
reads. This has to be quantified rather than asserted away, since one group here
has only 752 members.

It was quantified by permuting the decisions: assigning the same volume of
declines at random, holding group sizes fixed, and re-measuring. Under random
assignment the ratio reads 0.973 to 0.999 across the five attributes. That is
the floor the measure produces with no disparity present. The observed values —
0.325, 0.711, 0.729, 0.773, 0.789 — are nowhere near it, so the bias is real but
far too small to account for the findings.

The identification is also stable. Resampling the cohort names the same group as
worst-affected in 89% to 100% of draws, depending on the attribute; only sector
under the gradient booster falls below 100%, at 89%. A disparity attached to a
group that changed between resamples would be a statement about noise, and none
of these are.

The error-rate disparities are the substantive finding. Under the gradient
booster, 17.96% of micro-enterprises that repaid would have been declined,
against 6.39% of firms with 100 or more employees, a ratio of 2.81. By facility
size the gap is wider: 21.22% of creditworthy applicants in the smallest
quartile declined, against 6.20% in the largest, a ratio of 3.42. Micro-firms
and small facilities are precisely the segment that SME finance policy exists to
serve, and they are the segment the model serves worst.

The scorecard's failure is sharper and less defensible. It would decline 36.11%
of creditworthy agricultural borrowers, the highest rate of any sector, even
though agriculture has the lowest default rate in the cohort at 19.19%. The
model penalises most heavily the sector that performs best. This is not a
base-rate artefact; it is the a priori bands mis-scoring a sector.

Discrimination is also unevenly distributed. The booster's within-group AUC
ranges from 0.5468 in agriculture to 0.6424 in wholesale trade. The scorecard is
worse than a coin toss inside several substantial groups: 0.4369 for wholesale
trade (n = 18,018), 0.4874 for the upper-middle facility quartile (n = 68,881),
0.4955 for the largest quartile (n = 68,852). Within those groups its ranking is
inverted: it is not merely uninformative but actively misleading.

### 5.18.3 A confound that had to be ruled out

The largest single disparity looked at first like the clearest finding and
turned out not to be. Applicants whose rurality was not recorded are declined at
71.97% against 20.78% for urban and 13.74% for rural firms, with 64.14% of the
creditworthy among them declined, while their default rate, 34.75%, sits
slightly *below* the urban group's 37.70%. The natural reading is that the model
punishes missing data.

That reading does not survive inspection. The group is confounded: its records
are mostly 2004 approvals, carry a far higher SBA guarantee share (0.83 against
0.58), are larger, and are missing several other fields as well. Their decline
rate is explained by those characteristics, not by the absent flag. The
hypothesis was therefore tested directly, not inferred, and Section 5.19 reports
what that test found, which is the opposite.

## 5.19 What the models do with information the applicant did not supply

Section 5.3 reported a completeness gate: the artefact refuses to return a band
when too little of an objective has been assessed. It was introduced as a safety
measure after testing found a 14%-complete appraisal being handed a
recommendation. This section asks what the alternative actually does, and the
answer is a stronger argument for the gate than the safety argument that
motivated it.

### 5.19.1 Method

The question is causal, so it is answered by counterfactual instead of by
comparing groups. Take the 201,566 test-cohort applicants whose records are
complete, blank one field, and re-score the same applicant. Everything else is
held fixed, so whatever moves is caused by the absence itself. The decline
threshold is the same portfolio rule as Section 5.18: decline the riskiest 20%,
which on these applicants falls at a predicted default probability of 0.2293.
Section 5.19.3 shows the conclusion does not depend on that choice.

### 5.19.2 The models reward withholding

They do not penalise missing data. They reward it. For the gradient booster,
withholding lowers assessed risk for 11 of the 14 fields. Withholding the
rurality flag alone scores 97.7% of applicants as less risky than when they
answered, dropping mean assessed default from 16.84% to 6.44%, and moves 19.84%
of all applicants from decline to approval. Withholding whether the business is
new does the same for 92.0% of applicants and flips 16.48%.

The mechanism is mundane and entirely general. A gradient booster sends missing
values down whichever branch carried the greater training weight; the urban indicator was
absent for about a third of training rows and those rows defaulted less often,
so "not stated" is scored like a low-risk population.

The distinction matters because neither model treats absence as Rubin [45] would have it treated: as information about the mechanism that produced the gap. Median imputation, the standard alternative, fails differently rather than
better. Under the logistic regression, withholding the SBA guarantee share
scores
90.5% of applicants as less risky and flips 19.61% from decline to approval. It does not reward omission through a missingness branch; it silently asserts a value the applicant never gave. @fig:effect-withholding-information-same traces both models as fields are progressively withheld.

[Image: missingness.png | effect-withholding-information-same | The effect of withholding information about the same applicants. Left: mean assessed probability of default as fields are withheld, shaded across draws, with the thin horizontal line marking each model's assessment when nothing is withheld. Right: the share of all applicants converted from decline to approval. Both models converge on the ceiling, at which every applicant who would have been declined is approved.]

Both models behave the same way and differ only in pace. Assessed risk falls monotonically as fields are withheld, and on the right-hand panel both curves reach the ceiling once twelve of the fourteen fields are withheld, at which point every applicant who would have been declined has been approved.

### 5.19.3 The limit case

Withholding 7 of the 14 fields halves mean assessed risk. At the limit the
result is unambiguous. An applicant who supplies nothing at all receives an
assessed default probability of 0.0615 from the gradient booster, identical for
every applicant, because nothing remains for the model to vary on.

This does not depend on where the decline threshold is placed, which is the
obvious objection to a result reported under a single policy. That score sits at
the 6.5th percentile of real applicants' scores. Supplying nothing therefore
beats 93.5% of genuine applications, and remains an approval under any policy
declining less than 93.5% of the portfolio. The logistic regression is worse:
its no-information score of 0.0669 sits at the 3.9th percentile, giving a
crossover at 96.1%.

No lender declines nine applicants in ten. Within the entire range of policies a
bank might actually operate, an applicant who answers nothing is approved.

### 5.19.4 Why this matters for the artefact

The completeness gate was justified in Section 5.3 on safety grounds: a score
computed from 14% of the evidence should not be presented as a recommendation.
This analysis shows the weaker justification was the wrong one. A scoring model
that answers regardless of how much it was told is not merely unreliable on thin
evidence: it is exploitable, and in a direction that rewards the applicant for
supplying less. Under a fixed threshold, omission is a dominant strategy.

Refusing to answer is not conservatism. It is the only response to insufficient
evidence that cannot be gamed, and this is the empirical case for the design
decision, not the a priori one.

Two qualifications. The counterfactual asks what the model does with a blank
field, not what a bank's own process would do; a real institution would refuse
an incomplete application at intake, and the vulnerability arises only where an
automated score is taken at face value. And the specific numbers belong to these
two models on this dataset. The direction, that absent information is scored as
favourable rather than as unknown, follows from how both missing-value
strategies work, and is not particular to either.

## 5.20 Limitations

**Jurisdiction.** SBA data reflects U.S. government-guaranteed small-business
lending. Sri Lankan SME credit differs in legal environment, collateral
practice, and macroeconomic volatility. Nothing here transfers directly.

**The fuzzy layer is not exercised.** Every SBA-observable criterion is
quantitative, so each input enters as a degenerate triangular fuzzy number
[*x*, *x*, *x*]. Centroid defuzzification returns *x*, and the fuzzy weighted average
reduces exactly to an ordinary weighted mean. On this dataset the fuzzy
machinery does no work. It is exercised only by qualitative criteria, which SBA
data does not contain. What Sections 5.10 to 5.15 validates is band mapping and
weighted aggregation, not fuzzy inference.

**Maturity filtering biases composition.** Restricting to fully-matured loans
removes censoring but over-represents short-term facilities in later cohorts.

**These results were computed under placeholder weights.** All figures in this
chapter use equal weights within each level, so they test structure, not the
elicited model. Elicitation completed after the analyses were run (Section
6.1), and Section 6.1.5 measures the consequence directly: moving from the
placeholder vector to the elicited one preserves the ranking (ρ = 0.91 credit,
0.97 development) and moves no case by two risk bands, though 13–16% move by
one. Section 5.16 bounds it independently: within ±25% perturbation ρ ≈ 0.98 and
~94% of bands are unchanged. The limitation stands, but its magnitude is now
measured rather than merely acknowledged.

**The independence test uses thin development proxies.** SBA data carries
employment only; five of the nine items in clause 5 have no counterpart. Section
5.17 tests the employment dimension of development impact, not the whole
objective.

**The proposed model is not calibrated.** It produces an ordinal risk band, not
a probability of default. Section 5.13 shows that even trained probabilistic
models lose calibration badly across time periods; the proposed model does not
offer a probability to lose. It must not be used for pricing or provisioning.

**The sensitivity analysis uses a simulated population.** It characterises the
model's response to weight change; it says nothing about how real Sri Lankan SME
applications are distributed, and the two must not be confused.

**The development objective is barely observable.** Only *CreateJob* and
*RetainedJob* proxy the development-impact objective. Five of the nine items in
clause 5 of the People's Bank form — women's participation, local raw material
usage, import substitution, value added, foreign exchange earnings — have no
counterpart in SBA data. The development objective is a design contribution and
is not empirically validated in this chapter.

Novelty of the contamination finding is not fully established. A literature
search found no published report of it, but that search was not exhaustive and
cannot support a claim of priority. The finding is reported as one the author is
not aware of having been documented, which is a weaker and defensible claim.

## 5.21 Summary

1. *Term* in the SBA National dataset carries outcome information. Roundness
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
   appraisal models require elicitation, not proxy-dataset fitting.
6. The model is robust to weight perturbation within the range experts plausibly
   disagree over (ρ ≈ 0.98 and ~94% band stability at ±25%), which bounds the
   distortion introduced by reporting under placeholder weights.
7. The criteria tree is structurally asymmetric: a development-impact criterion
   carries four to seven times the leverage of a credit-risk criterion over its
   objective, a direct consequence of clause 5 being one section of the source
   form.
8. The two objectives are not independent on this population (r = +0.40, or
   +0.36 with disjoint inputs), which partly contradicts the premise the
   non-aggregation design was justified on. They nonetheless band the same
   facility differently 88.2% of the time, which is the stronger argument for
   reporting them separately.
9. Development impact is positively associated with default (10.8% in the lowest
   band against 30.3% in the highest). Reported as association, not cause; if it
   survives proper controls, a development mandate carries a measurable credit
   cost.
10. At realistic cost ratios under temporal validation, none of the models beats the better fixed policy: discrimination at this level does not convert into
    economic value.
11. Calibration degrades far more sharply than discrimination across time periods:
   gradient-boosting reliability worsens roughly 700-fold (0.00005 to 0.03705),
   with the model systematically under-predicting default, pricing an observed 45% risk at 20%. For a lender this is the more consequential failure, because
   it is less visible than a fall in discrimination.

Findings 1 and 5 are the contributions of this chapter. Finding 1 is a caution
to users of a widely-adopted benchmark; finding 5 justifies the methodological
design of the study.

---
