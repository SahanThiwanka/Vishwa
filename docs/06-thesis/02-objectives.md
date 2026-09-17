# 2 OBJECTIVES

## 2.1 General objective

To formalise the narrative SME credit appraisal instrument used by a Sri Lankan
state bank into a computable, explainable multi-criteria decision-support model
that assesses credit risk and development impact as separate objectives, and to
establish what can and cannot be validated about such a model using available
data.

## 2.2 Specific objectives

### 2.2.1 Derive a computable criteria model from the source instrument

Examine the People's Bank *Project / Business Appraisal Report for SME Credit
Facility* clause by clause, classify each clause as directly computable,
structured judgement, unstructured judgement or administrative, and derive a
criteria model in which every criterion is traceable to a numbered clause of the
original document.

### 2.2.2 Implement a scoring method for measured and judged inputs

Specify and implement an aggregation method handling quantitative measurements
and linguistic judgements within a single scoring path, reporting per-criterion
contributions that sum exactly to the score rather than approximating them after
the fact.

### 2.2.3 Build a working decision-support system

Develop a system through which a credit officer can complete an appraisal, see
the resulting assessment and its justification, record the institution's own
sign-off chain, and export the result in the format the bank already uses.

### 2.2.4 Establish how far the model depends on its criterion weights

Determine, by systematic perturbation, how far the model's rankings and risk
bands depend on the precise weight vector, and therefore what is at stake in
setting those weights.

### 2.2.5 Evaluate the scoring method against realised loan outcomes

Benchmark the method against standard credit-scoring approaches on public data
carrying realised outcomes, reporting confidence intervals and significance
tests, and state explicitly what such an evaluation can and cannot establish
about an instrument-specific model.

### 2.2.6 Determine whether the two objectives are separable in practice

Test whether credit risk and development impact behave as distinct objectives on
a large population of facilities, and establish what a single combined score
would conceal.

### 2.2.7 Elicit criterion weights from credit practitioners

Design, administer and analyse an instrument for eliciting criterion weights from
credit practitioners, with a response burden realistic for working professionals,
a measurable consistency criterion, and a stated rule for excluding inconsistent
responses before aggregation.

> **Status note.** The instrument, solver and analysis pipeline were built and
> verified, and the instrument was administered. Ten practitioners completed it,
> three of eighty level-responses were excluded for inconsistency, and the
> resulting weights now govern every score the system produces. Section 6.1
> reports the elicitation in full, including what changed when the elicited
> weights replaced the equal weighting used during development. The recruited
> sample is drawn from state commercial banking alone, which Section 6.3 treats
> as a limitation on how far the weights generalise.
