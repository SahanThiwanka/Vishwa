# Chapter 3 — Methodology

## 3.1 Research design

This study follows **Design Science Research**: knowledge is produced by building
an artefact and evaluating it. The artefact is a dual-objective decision-support
system for SME credit appraisal, together with the criteria model beneath it.

Three activities make up the design:

| Activity | Addresses | Method | Output |
|---|---|---|---|
| Formalisation | RQ1 | Clause-by-clause derivation from the bank's form | 49-criterion model |
| Weight elicitation | RQ2 | Best-Worst Method with practitioners | Weights + consistency ratios |
| Empirical validation | RQ3 | Benchmarking against realised outcomes | Chapter 5 |
| Objective comparison | RQ4 | Dual-objective scoring of the same applications | Chapters 4–6 |

## 3.2 Research questions

The questions were revised from the original proposal after the literature review
established that the initially claimed contribution was already published
(§2.3.3). The revised set:

- **RQ1** — How can the narrative, multi-section appraisal instrument used by a
  Sri Lankan state bank be formalised into a computable multi-criteria model
  without discarding the judgement it encodes?
- **RQ2** — What relative weights do experienced credit practitioners assign to
  the resulting criteria, and how consistent are those judgements?
- **RQ3** — How does the resulting model perform against realised loan outcomes on
  observable criteria, relative to standard credit-scoring benchmarks?
- **RQ4** — How does treating development impact as a separate objective change
  the assessment of applications, compared with credit risk alone?

## 3.3 Formalisation method (RQ1)

The source instrument is the People's Bank *Project / Business Appraisal Report
for SME Credit Facility* (Annexure I–V), an operational form in current use.

Each clause was classified as directly computable, structured judgement,
unstructured judgement, or administrative, and criteria were derived accordingly
(§4.2.2). One constraint governed the process:

> **No criterion may exist without a source clause.**

Every criterion in the model records the clause it derives from. This is not
documentation added afterwards; it is a constraint that shaped which criteria were
admitted. Its purpose is twofold — it makes any score auditable back to the
institutional document that authorises it, and it prevents the model from
acquiring criteria the institution never adopted.

The resulting model is held as a single machine-readable file consumed by both the
application and the analysis pipeline, so that no divergence between "the model in
the paper" and "the model in the system" is possible.

## 3.4 Scoring method

Quantitative criteria map to 0–100 through piecewise-linear band anchors.
Qualitative criteria are captured on a five-point linguistic scale represented as
triangular fuzzy numbers, aggregated by fuzzy weighted average and defuzzified by
centroid. Full specification in §4.4.

Three rules govern edge cases, each chosen deliberately:

1. **Unassessed criteria are excluded and weights renormalised**, never treated as
   zero — an incomplete appraisal is not a bad one.
2. **Below a completeness threshold, no recommendation is issued** — rule 1 alone
   allows a sparse file to produce a confident score (§4.5).
3. **Critical criteria are evaluated on raw values** and surfaced separately, so a
   DSCR below 1.0 cannot be averaged away.

## 3.5 Weight elicitation (RQ2)

### 3.5.1 Method selection

Classical pairwise AHP over this criteria tree requires **168 comparisons** per
respondent. At even ten seconds each that is close to an hour of sustained
attention, and response quality degrades well before the end. Inconsistency
introduced by fatigue would make the resulting weights unusable regardless of how
carefully the instrument was designed.

The Best-Worst Method (Rezaei, 2015) requires 2n−3 comparisons per level,
reducing the instrument to **86 comparisons** — roughly fifteen minutes. Because
every comparison is anchored to a fixed reference rather than a rotating partner,
BWM also tends to yield more consistent responses. The linear formulation
(Rezaei, 2016) is used, giving a unique solution.

The choice is a response to a real constraint on practitioner time, not a
convenience.

### 3.5.2 Instrument

Elicitation is conducted through a web instrument forming part of the system, in
eight sections: one comparing the six credit-risk dimensions, and one for the
criteria within each of the seven dimensions.

For each section the respondent identifies the most important item, identifies the
least important, then rates the best against each other item and each item against
the worst, on the 1–9 scale.

### 3.5.3 Analysis

Each response is solved as a linear programme minimising the maximum deviation
between stated ratios and derived weights, subject to weights summing to one. The
optimal deviation ξ\* divided by the consistency index for the stated
best-to-worst value gives a consistency ratio comparable across respondents and
level sizes.

Responses with **CR > 0.25** are excluded rather than averaged in. The number
excluded is reported: silently discarding respondents would make the study
unreproducible.

Surviving responses are aggregated by **geometric mean**, the standard aggregation
for ratio-scale priority vectors, which preserves the ratio relationships that an
arithmetic mean distorts.

### 3.5.4 Sampling and its limits

Respondents are credit and appraisal practitioners recruited through professional
contact. This is **purposive, non-probability sampling** with a small n, and the
resulting weights represent the judgement of those respondents, not of Sri Lankan
credit practice generally. Chapter 6 reports the achieved sample and treats this
as a primary limitation.

## 3.6 Empirical validation (RQ3)

### 3.6.1 The proxy problem, stated in advance

No public dataset contains the criteria this model scores. Access to the bank's
own historical files was not available and would in any case be confidential.

Validation therefore uses the SBA National dataset as a **proxy**, and the
resulting claim is correspondingly narrow: it tests the scoring *machinery* on
observable financial and structural variables, not the criteria tree. This
limitation is stated in advance rather than discovered afterwards, because it
determines what Chapter 5 is entitled to conclude.

### 3.6.2 Protocol

- Outcome-derived fields are dropped and their absence asserted.
- Right-censored loans are excluded; only fully-matured facilities are analysed.
- Two validation protocols are run: random split, and **temporal split** (train on
  earlier cohorts, test on later). Both are reported, because random splitting
  places the same economic cycle on both sides and overstates performance.
- The unfitted expert scorecard is compared against logistic regression and
  gradient boosting, both trained on hundreds of thousands of labelled outcomes.
- Metrics: AUC, Kolmogorov-Smirnov separation, average precision, Brier score,
  F1 at the Youden-optimal threshold.

The comparison is deliberately asymmetric. The scorecard never sees a default
label; its bands were fixed from a priori reasoning before outcomes were
inspected. The question is not whether it wins — it will not — but how much
discrimination an unfitted, explainable, expert-structured model retains. That
ratio is what matters for institutions without clean historical default data,
which is the common situation in Sri Lankan SME lending.

### 3.6.3 Treatment of anomalous results

An unexpectedly strong result is treated as a suspected defect until explained.
This rule was applied during the study and is what produced the finding in §5.3:
an AUC of 0.97 was investigated rather than reported, and proved to arise from
contamination in a predictor. The rule is stated here because it is part of the
method, not a lucky accident.

## 3.7 Ethical considerations

**Human participants.** The elicitation instrument collects a self-chosen
participant code, years of experience, institution type and role. It collects **no
name and no customer information**. The landing page states that participation is
voluntary, may be stopped at any time, and that responses are used solely for
academic research and reported only in aggregate.

**Confidentiality of bank material.** The source appraisal form is a blank
template. No customer file, no borrower data and no internal credit policy
document was accessed. The system was demonstrated using constructed cases, not
real applications.

**Institutional approval.** Formal ethics clearance and any institutional
permission required for practitioner participation must be obtained and recorded
before elicitation data is used in the submitted work. Where this study was
conducted under time constraints that limited the scale of participant
recruitment, that constraint is reported in the limitations rather than concealed
by the sample size.

**Research integrity.** Every quantitative result reported in this thesis is
produced by code in the accompanying repository and is regenerable from the raw
data. No value is entered by hand. Where an experiment could not be run, the claim
is withdrawn and the gap recorded as a limitation rather than filled with an
estimate. Negative results — including a scorecard that failed to discriminate
(§5.6) — are reported as they occurred.

## 3.8 Limitations of the design

- The empirical validation uses a **proxy dataset from a different jurisdiction**;
  the qualitative criteria are not tested against outcomes at all.
- The **fuzzy layer is not exercised** by the validation, since all
  SBA-observable criteria are quantitative and enter as degenerate fuzzy numbers.
- **Elicitation is small-n and purposive**, so weights are not generalisable.
- There is **no inter-rater reliability study**. Establishing how much two officers
  disagree on the same file — and whether the system narrows that gap — would
  directly evidence the consistency claim motivating this research. It was not
  feasible within the time available and is the single most valuable extension.
- The system is evaluated for **structural correctness, not field usability**. No
  officer has used it on live applications.
