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

The instrument, solver and analysis pipeline were built, verified and
administered. Eleven practitioners completed the instrument, three of the
eighty-eight level-responses were excluded for inconsistency, and the resulting
weights govern every score the system now produces. Section 6.1 reports the
elicitation in full, including what changed when the elicited weights replaced
the equal weighting used during development. The recruited sample is drawn from
state commercial banking alone, which Section 6.4 treats as a limitation on how
far the weights generalise.

## 2.3 How the objectives answer the research questions

The seven specific objectives are not in one-to-one correspondence with the four
research questions: RQ1 asks whether a narrative instrument can be formalised at
all, and answering it takes a criteria model, a scoring method and a working
system rather than any one of them.
@tbl:objectives-questions-they-serve sets each objective against the question it
serves and the section reporting its outcome.

[Table: objectives-questions-they-serve | The specific objectives, the research question each serves and where its outcome is reported]

| Objective | Serves | Outcome reported in |
|---|---|---|
| 2.2.1 Derive a computable criteria model | RQ1 | Sections 4.10, 5.1 |
| 2.2.2 Implement a scoring method for measured and judged inputs | RQ1 | Section 4.11 |
| 2.2.3 Build a working decision-support system | RQ1 | Sections 4.12, 5.4, 5.5 |
| 2.2.4 Establish how far the model depends on its weights | RQ2 | Section 5.16 |
| 2.2.5 Evaluate the scoring method against realised outcomes | RQ3 | Sections 5.10 to 5.15 |
| 2.2.6 Determine whether the two objectives are separable | RQ4 | Section 5.17 |
| 2.2.7 Elicit criterion weights from credit practitioners | RQ2 | Section 6.1 |

This table contains the mapping from objective to research question, and the
section in which each objective's outcome is reported. Three objectives serve
RQ1 and two serve RQ2, because formalisation and weighting are each established
by more than one piece of work; RQ3 and RQ4 are each answered by a single
objective. No objective serves two questions, and no question is left without
one, so the set is a partition of the work rather than a list of activities
assembled after the fact.
