# 6 DISCUSSION AND CONCLUSIONS

## 6.1 Weight elicitation: prepared, not administered

The methodology in §4.5 specifies weight elicitation by Best-Worst Method. **That
elicitation was not carried out.** This section states plainly what was built,
what was not done, and what follows.

### 6.1.1 What exists

- A web instrument implementing BWM across eight comparison levels — 86
  comparisons, approximately fifteen minutes — with a participation and
  confidentiality notice, collecting a self-chosen participant code, years of
  experience, institution type and role, and **no name or customer information**.
- A linear BWM solver [21] verified against the published worked
  example, reproducing its weights exactly (ξ\* = 0, CR = 0) and flagging a
  deliberately contradictory response at CR = 1.18.
- An analysis pipeline computing per-respondent consistency ratios, excluding
  responses above CR 0.25, and aggregating by geometric mean.

The pipeline was verified end to end with a synthetic respondent, which produced
consistency ratios of 0.031–0.042 across the eight levels. **That synthetic
response was then deleted**, and the criteria model carries
`weightStatus: PLACEHOLDER`.

### 6.1.2 What was not done, and why

No practitioner responses were collected. Recruiting credit officers requires
institutional access and participant time that were not secured within the study
period.

The consequence is stated without softening: **the original RQ2 — what weights
practitioners assign — is unanswered by this study.** The weights reported
throughout are equal splits within each level, and every score computed from them
is labelled accordingly. `derive_weights.py` refuses to mark the model `ELICITED`
without usable responses, so no analysis in this thesis can have silently treated
placeholder weights as elicited ones.

### 6.1.3 What was done instead

Rather than leave the question open, the study asks a different one that is
answerable without respondents and is arguably more useful: **how much does the
model's output depend on its weights at all?** That is the revised RQ2, and §5.16
answers it.

This is a genuine narrowing of scope, not a substitution of equivalent value.
Elicited weights would tell us what Sri Lankan practitioners believe. The
sensitivity analysis tells us only how much such beliefs would matter. Both are
worth knowing; only the second was obtainable here.

## 6.2 Answers to the research questions

## 6.3 Discussion

### 6.3.1 What the contamination finding means

The SBA National dataset is widely used in credit-scoring research and teaching.
A model given `Term` and free to split on exact values inherits an artefact worth
up to 0.34 AUC, and a meaningless roundness probe reaches 0.887 on its own.

The transferable lesson is about **how anomalies are treated**. The finding
emerged only because an AUC of 0.9726 was investigated rather than reported. Had
it been published it would have exceeded every benchmark it would have been
compared against — which is precisely why it would not have been questioned.

Kapoor and Narayanan [27] found leakage affecting 294 papers across seventeen
fields. This case is harder to catch than the textbook forms: the offending field
is documented as legitimate, is available at prediction time under its documented
meaning, and is economically meaningful. It is caught only by noticing that the
*shape* of its relationship with the outcome is not one any economic mechanism
could produce.

### 6.3.2 What the negative result means

Substituting available proxies for the intended criteria tests the proxies, not
the model. Institutions without clean historical default data cannot fit a
scorecard, and this study shows they cannot borrow someone else's dataset to
validate one either. Expert elicitation is not a second-best option in that
situation; it is the only sound one — which makes §6.1's omission the more
regrettable.

### 6.3.3 What temporal validation reveals

Logistic regression scored 0.4565 temporally — below chance. Trained on cohorts
defaulting at 9.1% and tested on cohorts defaulting at 35.9%, its ranking
inverted.

Calibration degraded further than discrimination. For a lender that is the more
dangerous failure: falling discrimination is visible and invites scrutiny,
whereas a model that still ranks tolerably while pricing a 45% risk at 20%
under-provisions by more than half and appears to be working. **Recalibration on
recent outcomes is a separate requirement from revalidation of discrimination**,
and the two are routinely conflated. Given Sri Lanka's recent macroeconomic
volatility, this is the most directly actionable result in the thesis.

### 6.3.4 On the system

Two design decisions proved more consequential than expected.

The **completeness gate** (§5.3) arose from a defect found in testing: a
14%-complete file produced a confident recommendation. Weight renormalisation
keeps a sparse appraisal's score plausible while its evidential basis collapses.
The gate is a refusal to answer rather than a score adjustment, because a
discounted score would preserve the false impression that the system had an
opinion.

That was a safety argument, and §5.19 shows it was the weaker of the two
available. The stronger one is that the alternative is exploitable: both
conventional models tested score a withheld field as favourable rather than as
unknown, so under a fixed threshold an applicant improves their assessment by
answering less. A design decision taken on cautionary grounds turned out to have
an incentive justification that is harder to argue with.

**Authenticated sign-off** (§4.13) replaced a typed name. An audit trail of
self-declared signatories records nothing; the signatory is now the authenticated
user and roles are enforced server-side.

### 6.3.5 Who the models serve worst

Two findings sit outside the research questions and are reported because they
bear directly on whether any of this should be deployed.

The first is that **the artefact discriminates against the applicants it was
designed to serve**. The scorecard fails the four-fifths rule on four of five
credit-access attributes, and would decline 36.11% of creditworthy agricultural
borrowers — the worst rate of any sector — while agriculture has the lowest
default rate in the cohort at 19.19%. The trained model is not much better:
creditworthy micro-enterprises are declined at 2.81 times the rate of large
firms, and the smallest facility quartile at 3.42 times the largest. Micro-firms,
small facilities and agriculture are precisely the segments that SME and
development finance exist to reach.

This has to be stated carefully. These are credit-access proxies; the dataset
records no protected characteristic, so no claim about lawful discrimination
follows. Group default rates genuinely differ, so selection-rate gaps are not by
themselves evidence of injustice — which is why the error-rate comparison, taken
only over borrowers who actually repaid, is the one reported as the finding.

The second is that both conventional models **reward applicants for withholding
information** (§5.19), which is the empirical case for the completeness gate
discussed above.

Neither finding was sought. Both emerged from taking the model card's own list of
untested risks seriously, and the first of them is a defect in this study's own
artefact rather than in someone else's. It is reported for that reason: an
appraisal instrument that penalises the best-performing sector is not ready to
inform decisions, and saying so is more useful than not having looked.

## 6.4 Limitations

**Empirical validation is on a proxy dataset from another jurisdiction.** Nothing
transfers directly to Sri Lankan SME credit.

**The criteria tree is not empirically validated.** No dataset contains its
variables.

**No weight elicitation was carried out** (§6.1). RQ2 as originally posed is
unanswered.

**Fairness is assessed only on credit-access proxies.** The SBA file records no
race, sex, age, disability or marital-status field. Passing — or failing — on
rurality, firm size, sector and facility size establishes nothing about
discrimination on protected characteristics, which remains untested and is a
precondition for any deployment.

**The fuzzy layer is not exercised by the validation.** All SBA-observable
criteria are quantitative and enter as degenerate fuzzy numbers, under which the
fuzzy weighted average reduces exactly to a weighted arithmetic mean.

**The development objective is thinly proxied.** Only employment is observable;
five of the nine clause-5 items have no counterpart. §5.17 tests the employment
dimension, not the whole objective.

**The development–default association is uncontrolled.** Facility size and
business age are plausible confounders and were not adjusted for.

**No inter-rater reliability study.** The premise that manual appraisal is
inconsistent is supported from the literature [1] but not
measured here. This remains the single most significant omission.

**No field evaluation and no fairness assessment.** No officer has used the
system on live applications, so neither perceived usefulness [35] nor
usability [36] has been measured, and no disparate-impact analysis has
been performed.
For a credit model the second is a serious gap, recorded in the model card.

**Novelty of the contamination finding is not established as priority.** A
literature search found no prior report, but was not exhaustive.

## 6.5 Future work

**Measure the inconsistency.** Have N officers appraise the same M files
independently, compute inter-rater reliability, then repeat with the system. This
directly tests the premise the research rests on and requires only practitioner
time and constructed cases.

**Complete the elicitation.** The instrument and pipeline are built and verified;
they need respondents.

**Control the development–default association.** Adjust for facility size,
business age and sector to determine whether the relationship in §5.17.3 is
causal. If it is, it has direct policy implications for development lending.

**Establish the contamination mechanism.** Determining why `Term` behaves as it
does — through SBA documentation or the agency itself — would convert a caution
into a full account, and is publishable independently.

**Validate on institutional data.** With permission and anonymisation, even a few
hundred historical files with outcomes would allow the criteria tree itself to be
tested rather than a proxy.

## 6.6 Conclusion

This study set out to formalise a Sri Lankan state bank's narrative SME appraisal
instrument into an explainable, dual-objective decision-support system.

The artefact was built. A 49-criterion model was derived clause by clause from the
People's Bank appraisal form and implemented in a working system that scores
credit risk and development impact separately, decomposes every score into exact
per-criterion contributions, withholds a recommendation when too little has been
assessed, enforces the form's own sign-off chain, and exports its output in the
bank's format.

The empirical work produced results the study did not set out to find. The most
substantial contribution is not the model but a caution about the data others use
to evaluate such models: the `Term` field in the widely used SBA National dataset
carries outcome information, inflating gradient-boosting temporal discrimination
by 0.34 AUC. Alongside it sit a negative result — an expert scorecard that failed
to discriminate on proxy variables — and the methodological point that follows:
instrument-specific appraisal models cannot be validated on datasets lacking
their variables.

Two further findings emerged from asking questions the study could answer rather
than the ones it could not. The model's output is robust to weight disagreement
within the range experts plausibly exhibit, which bounds what the missing
elicitation costs. And the two objectives, while moderately correlated, place the
same facility in different bands 88.2% of the time — so reporting them separately
preserves information that a combined score would destroy, even though the
independence premise that originally justified the separation does not hold on
this population.

The claim this thesis does **not** make is that a better credit scoring model has
been built. The evidence does not support it, and Chapter 2 establishes that the
methods used are not themselves new. What it offers instead is a transferable
method for formalising institutional appraisal instruments, a working artefact
that implements it, and three findings about evaluation — contamination in a
common benchmark, the limits of proxy validation, and the divergence between
discrimination and calibration under temporal shift — that should change how
others approach the same problem.
