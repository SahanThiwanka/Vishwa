# 6 DISCUSSION AND CONCLUSIONS

## 6.1 Weight elicitation

The methodology in Section 4.5 specifies weight elicitation by Best-Worst
Method. It was carried out, and this section reports it.

### 6.1.1 The instrument

- A web instrument implementing BWM across eight comparison levels (86 comparisons, approximately fifteen minutes), with a participation and
  confidentiality notice, collecting a self-chosen participant code, years of
  experience, institution type and role, and no name or customer information.
- A linear BWM solver [22], verified two ways on deliberately
  inconsistent inputs: the maximum deviation recomputed from the returned weights
  matches the reported ξ\*, and an independent optimiser from forty random starts
  finds no better solution, agreeing to six decimal places (Section 4.5.3).
- An analysis pipeline computing per-respondent consistency ratios, excluding
  responses above CR 0.25, and aggregating by geometric mean.

The instrument was deployed publicly so that practitioners could complete it
from their own device without an account, which is what made recruitment
feasible.

### 6.1.2 Respondents

Ten credit practitioners completed the instrument, above the five-to-eight range
typical of published BWM studies.

[Table: Profile of the ten elicitation respondents]

| | |
|---|---|
| Respondents | 10 |
| Experience | 1–12 years, median 8 |
| Credit / appraisal officers | 4 |
| Branch managers | 3 |
| Regional or head-office credit | 2 |
| Not stated | 1 |
| Institution | State commercial bank (9); not stated (1) |

All respondents are from state commercial banking, which is the setting the
instrument comes from and also a limitation: these weights describe one segment
of Sri Lankan SME lending, not the sector.

### 6.1.3 Consistency

Each respondent produced eight level-responses, giving 80 in total. Three were
excluded for a consistency ratio above 0.25 and the remaining 77 retained. The
exclusions are reported rather than absorbed: two fell in
`dimension:borrower_management` and `dimension:credit_conduct` from one
respondent (CR 0.298 and 0.377), and one at `objective:credit_risk` from another
(CR 0.293).

Most responses were highly consistent, a majority of them at CR = 0.000, meaning
the stated comparisons admit a weight vector that reproduces them exactly.

### 6.1.4 The weights

At the objective level, practitioners weight the six credit-risk areas as:

[Table: Elicited weights for the six credit-risk dimensions]

| Dimension | Weight | Against equal |
|---|---:|---:|
| Project Viability & Projections | 0.2504 | ×1.50 |
| Borrower & Management Capacity | 0.2062 | ×1.24 |
| Credit History & Banking Conduct | 0.1733 | ×1.04 |
| Market & Competitive Position | 0.1527 | ×0.92 |
| Historic Financial Performance | 0.1116 | ×0.67 |
| Risk, Security & Compliance | 0.1058 | ×0.63 |

The ordering is itself a finding. Forward-looking project viability outranks
historic financial performance by more than two to one, which inverts the
emphasis of an instrument whose longest section is the historic financial
analysis. Security and compliance ranks last of the six, despite occupying a
full clause of the form.

`weightStatus` is now `ELICITED`, recording ten respondents, three exclusions and
the date. Every score in the system is computed from these weights.

### 6.1.5 What the placeholders cost

Until elicitation completed, every scored result used equal weights within each
level. Section 5.16 argued this mattered less than it appeared, on a simulation
perturbing weights by up to ±25%.

**The elicited weights fall outside that range.** Within a level the ratio of
largest to smallest reaches 3.25, and the largest departure from equal weighting
is 79%, three times the perturbation tested. The earlier reassurance was
therefore about a narrower disturbance than the one that actually occurred.

It survives the test anyway. Scoring the same 2,000 simulated appraisals under
both vectors:

[Table: Scoring under placeholder and elicited weights compared]

| | Credit risk | Development impact |
|---|---:|---:|
| Spearman correlation | 0.9136 | 0.9662 |
| Same risk band | 86.7% | 84.1% |
| Two or more bands apart | 0.0% | 0.0% |
| Mean absolute score shift | 1.85 | 2.45 |

No case moves two bands. Between 13% and 16% move one band. That is not nothing:
those are appraisals that would carry a different recommendation. The ordering
is nonetheless substantially preserved across a weight change far larger than
the one Section 5.16 modelled.

This is a stronger result than the simulation it replaces, because it is not a
simulation of possible weights. It is the placeholder vector against the
elicited one, on identical cases.

## 6.2 Answers to the research questions

### 6.2.1 RQ1: can the instrument be formalised?

Yes, and the artefact demonstrates it. Forty-nine criteria across seven
dimensions and two objectives, each traceable to a numbered clause of the
People's Bank form. Twenty-eight quantitative criteria map through
piecewise-linear bands; twenty-one qualitative criteria are captured on a
five-point linguistic scale as triangular fuzzy numbers.

The working system scores, explains, and exports in the bank's own report
format. Contributions decompose exactly to the score, so any recommendation is
traceable to the clause that produced it.

What the formalisation does not do is preserve everything. Stein's (2002)
distinction between hard and soft information implies that hardening a judgement
loses something, and the fuzzy linguistic scale mitigates that loss rather than
avoiding it.

### 6.2.2 RQ2: what weights do practitioners assign, and how much do they matter?

Both halves are now answered.

*What they assign.* Ten practitioners, 1–12 years' experience, produced the
weights in Section 6.1.4. The ordering is the substantive result:
forward-looking project viability outranks historic financial performance by
more than two to one, and security and compliance ranks last of the six
credit-risk areas. Three of 80 level-responses were excluded for inconsistency.

*How much they matter.* Less than the effort of eliciting them might imply, and
the answer is now measured rather than simulated. The elicited weights depart
from the placeholders by up to 79% within a level, three times the ±25% Section
5.16 modelled, yet rank correlation between the two scorings is 0.9136 (credit)
and
0.9662 (development), no case moves two risk bands, and 84–87% keep the same
band (Section 6.1.5).

Three qualifications. The 13–16% that change band are real appraisals that would
carry a different recommendation. All ten respondents come from state commercial
banking, so these weights describe one segment, not the sector. And the criteria
tree is structurally asymmetric: a development-impact criterion carries four to
seven times the leverage of a credit-risk criterion, so elicitation error costs
more on that side.

### 6.2.3 RQ3: what can be established from public data?

Less than hoped, and the reasons are themselves the contribution.

The scoring method could not be validated against the criteria tree, because no
public dataset contains its variables. Substituting SBA-observable proxies
produced a scorecard with no discrimination (AUC 0.4144 random, 0.5275
temporal), a negative result reported as it occurred (Section 5.15).

The attempt surfaced something more useful. The SBA National dataset's `Term`
field carries outcome information: roundness alone predicts default at AUC 0.889
within every approval year, and excluding the field drops gradient-boosting
temporal AUC from 0.9461 to 0.6076 (Sections 5.3 to 5.4). Confidence intervals
do not overlap and paired DeLong tests give p < 0.001.

Two further hazards emerged. Calibration degrades roughly 700-fold across the
temporal boundary, with models systematically under-predicting default (Section
5.5a). And at realistic cost ratios, none of the models beats a fixed policy on
the stressed cohort (Section 5.14).

### 6.2.4 RQ4: are the objectives separable?

Not independent, but they disagree constantly, and the second fact is what
matters.

Across 652,284 facilities the two scores correlate at r = +0.40, or +0.36 with
the shared-input confound removed. That is *moderate*, and it removes the strong
form of the premise the design was justified on. It does not, however, overturn
Arvanitis et al. [25]. Their estimate was also positive (slope 0.048) and
merely non-significant in 109 observations; this study measures the same
direction at a sample size able to resolve it (Section 5.17.1). What went wrong
was the reading of that paper: an underpowered null carried forward as an
established independence result. This thesis made that error before correcting
it.

The practical case survives by a different route. The two objectives place the
same facility in different risk bands 88.2% of the time, and 38.4% differ by two
bands or more. A correlation of 0.40 leaves enormous scatter, and it is
per-facility disagreement, not average co-movement, that a combined score
destroys.

Additionally, development impact is positively associated with default (10.8% in
the lowest development band against 30.3% in the highest). Reported as
association, not cause, and likely confounded by facility size and business age.
If it survives proper controls, a development mandate carries a measurable
credit cost, exactly the trade-off the dual-objective design exists to surface.

## 6.3 Discussion

### 6.3.1 What the contamination finding means

The SBA National dataset is widely used in credit-scoring research and teaching.
A model given `Term` and free to split on exact values inherits an artefact
worth up to 0.34 AUC, and a meaningless roundness probe reaches 0.887 on its
own.

The transferable lesson is about how anomalies are treated. The finding emerged
only because an AUC of 0.9726 was investigated rather than reported. Had it been
published it would have exceeded every benchmark it would have been compared
against, which is precisely why it would not have been questioned.

Kapoor and Narayanan [28] found leakage affecting 294 papers across seventeen
fields. This case is harder to catch than the textbook forms: the offending
field is documented as legitimate, is available at prediction time under its
documented meaning, and is economically meaningful. It is caught only by
noticing that the *shape* of its relationship with the outcome is not one any
economic mechanism could produce.

### 6.3.2 What the negative result means

Substituting available proxies for the intended criteria tests the proxies, not
the model. Institutions without clean historical default data cannot fit a
scorecard, and this study shows they cannot borrow someone else's dataset to
validate one either. Expert elicitation is not a second-best option in that
situation; it is the only sound one, which is why the weights reported in
Section 6.1 were elicited from practitioners rather than fitted to borrowed
outcomes.

### 6.3.3 What temporal validation reveals

Logistic regression scored 0.4565 temporally, below chance. Trained on cohorts
defaulting at 9.1% and tested on cohorts defaulting at 35.9%, its ranking
inverted.

Calibration degraded further than discrimination. For a lender that is the more
dangerous failure: falling discrimination is visible and invites scrutiny,
whereas a model that still ranks tolerably while pricing a 45% risk at 20%
under-provisions by more than half and appears to be working. Recalibration on
recent outcomes is a separate requirement from revalidation of discrimination,
and the two are routinely conflated. Given Sri Lanka's recent macroeconomic
volatility, this is the most directly actionable result in the thesis.

### 6.3.4 On the system

Two design decisions proved more consequential than expected.

The completeness gate (Section 5.3) arose from a defect found in testing: a
14%-complete file produced a confident recommendation. Weight renormalisation
keeps a sparse appraisal's score plausible while its evidential basis collapses.
The gate is a refusal to answer rather than a score adjustment, because a
discounted score would preserve the false impression that the system had an
opinion.

That was a safety argument, and Section 5.19 shows it was the weaker of the two
available. The stronger one is that the alternative is exploitable: both
conventional models tested score a withheld field as favourable rather than as
unknown, so under a fixed threshold an applicant improves their assessment by
answering less. A design decision taken on cautionary grounds turned out to have
an incentive justification that is harder to argue with.

Authenticated sign-off (Section 4.13) replaced a typed name. An audit trail of
self-declared signatories records nothing; the signatory is now the
authenticated user and roles are enforced server-side.

### 6.3.5 Who the models serve worst

Two findings sit outside the research questions and are reported because they
bear directly on whether any of this should be deployed.

The first is that the artefact discriminates against the applicants it was
designed to serve. The scorecard fails the four-fifths rule on four of five
credit-access attributes, and would decline 36.11% of creditworthy agricultural
borrowers, the worst rate of any sector, while agriculture has the lowest
default rate in the cohort at 19.19%. The trained model is not much better:
creditworthy micro-enterprises are declined at 2.81 times the rate of large
firms, and the smallest facility quartile at 3.42 times the largest.
Micro-firms, small facilities and agriculture are precisely the segments that
SME and development finance exist to reach.

This has to be stated carefully. These are credit-access proxies; the dataset
records no protected characteristic, so no claim about lawful discrimination
follows. Group default rates genuinely differ, so selection-rate gaps are not by
themselves evidence of injustice, which is why the error-rate comparison, taken
only over borrowers who actually repaid, is the one reported as the finding.

The second is that both conventional models reward applicants for withholding
information (Section 5.19), which is the empirical case for the completeness
gate discussed above.

Neither finding was sought. Both emerged from taking the model card's own list
of untested risks seriously, and the first of them is a defect in this study's
own artefact rather than in someone else's. It is reported for that reason: an
appraisal instrument that penalises the best-performing sector is not ready to
inform decisions, and saying so is more useful than not having looked.

## 6.4 Limitations

Empirical validation is on a proxy dataset from another jurisdiction. Nothing
transfers directly to Sri Lankan SME credit.

**The criteria tree is not empirically validated.** No dataset contains its
variables.

No weight elicitation was carried out (Section 6.1). RQ2 as originally posed is
unanswered.

**Fairness is assessed only on credit-access proxies.** The SBA file records no
race, sex, age, disability or marital-status field. Passing, or failing, on
rurality, firm size, sector and facility size establishes nothing about
discrimination on protected characteristics, which remains untested and is a
precondition for any deployment.

**The fuzzy layer is not exercised by the validation.** All SBA-observable
criteria are quantitative and enter as degenerate fuzzy numbers, under which the
fuzzy weighted average reduces exactly to a weighted arithmetic mean.

**The development objective is thinly proxied.** Only employment is observable;
five of the nine clause-5 items have no counterpart. Section 5.17 tests the
employment dimension, not the whole objective.

**The development–default association is uncontrolled.** Facility size and
business age are plausible confounders and were not adjusted for.

**No inter-rater reliability study.** The premise that manual appraisal is
inconsistent is supported from the literature [2] but not
measured here. This remains the single most significant omission.

**No field evaluation and no fairness assessment.** No officer has used the
system on live applications, so neither perceived usefulness [36] nor
usability [37] has been measured, and no disparate-impact analysis has
been performed. For a credit model the second is a serious gap, recorded in the
model card.

Novelty of the contamination finding is not established as priority. A
literature search found no prior report, but was not exhaustive.

## 6.5 Future work

**Measure the inconsistency.** Have N officers appraise the same M files
independently, compute inter-rater reliability, then repeat with the system.
This directly tests the premise the research rests on and requires only
practitioner time and constructed cases.

**Complete the elicitation.** The instrument and pipeline are built and
verified; they need respondents.

**Control the development–default association.** Adjust for facility size,
business age and sector to determine whether the relationship in Section 5.17.3
is causal. If it is, it has direct policy implications for development lending.

**Establish the contamination mechanism.** Determining why `Term` behaves as it
does, through SBA documentation or the agency itself, would convert a caution
into a full account, and is publishable independently.

**Validate on institutional data.** With permission and anonymisation, even a
few hundred historical files with outcomes would allow the criteria tree itself
to be tested, not a proxy.

## 6.6 Conclusion

This study set out to formalise a Sri Lankan state bank's narrative SME
appraisal instrument into an explainable, dual-objective decision-support
system.

The artefact was built. A 49-criterion model was derived clause by clause from
the People's Bank appraisal form and implemented in a working system that scores
credit risk and development impact separately, decomposes every score into exact
per-criterion contributions, withholds a recommendation when too little has been
assessed, enforces the form's own sign-off chain, and exports its output in the
bank's format.

The empirical work produced results the study did not set out to find. The most
substantial contribution is not the model but a caution about the data others
use to evaluate such models: the `Term` field in the widely used SBA National
dataset carries outcome information, inflating gradient-boosting temporal
discrimination by 0.34 AUC. Alongside it sit a negative result, an expert
scorecard that failed to discriminate on proxy variables, and the methodological
point that follows: instrument-specific appraisal models cannot be validated on
datasets lacking their variables.

Two further findings emerged from asking questions the study could answer rather
than the ones it could not. The model's output is robust to weight disagreement
within the range experts plausibly exhibit, which bounds what the missing
elicitation costs. And the two objectives, while moderately correlated, place
the same facility in different bands 88.2% of the time, so reporting them
separately preserves information that a combined score would destroy, even
though the independence premise that originally justified the separation does
not hold on this population. The design decision survives; the argument for it
had to be rebuilt.

The claim this thesis does not make is that a better credit scoring model has
been built. The evidence does not support it, and Chapter 3 establishes that the
methods used are not themselves new. What it offers instead is a transferable
method for formalising institutional appraisal instruments, a working artefact
that implements it, and three findings about evaluation — contamination in a
common benchmark, the limits of proxy validation, and the divergence between
discrimination and calibration under temporal shift — that should change how
others approach the same problem.
