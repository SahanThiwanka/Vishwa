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

### 2.2.7 Prepare a weight elicitation instrument

Design and implement an instrument for eliciting criterion weights from credit
practitioners, with a response burden realistic for professional participants and
a measurable consistency criterion.

> **Status note.** Objective 2.2.7 was met in that the instrument, solver and
> analysis pipeline were built and verified. The elicitation itself was **not
> administered**: no practitioner responses were obtained within the study period.
> Section 5.9 reports this, and Section 6.3 treats it as a principal limitation.
> The criteria model accordingly carries placeholder weights throughout, and every
> score derived from them is labelled as such.
