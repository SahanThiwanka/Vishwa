# Model Card — Dual-Objective SME Credit Appraisal Model

Following the model-card convention for documenting intended use, performance and
limitations of a decision model. Written so that someone considering deploying
this can determine, without reading the thesis, whether they should.

**Short answer: they should not, yet.** §7 says why.

---

## 1. Model details

| | |
|---|---|
| **Name** | Dual-Objective SME Credit Appraisal Criteria Model |
| **Version** | 0.1.0-draft |
| **Type** | Additive multi-criteria decision model with fuzzy linguistic inputs |
| **Owner** | AAV Athukorala, MSc IT, NSBM Green University |
| **Source instrument** | People's Bank *Project / Business Appraisal Report for SME Credit Facility*, Annexure I–V |
| **Definition** | `shared/model/criteria-tree.json` |
| **Implementations** | TypeScript (`web/src/lib/scoring/`), Python (`research/src/tree_scoring.py`) — parity-verified, 280 checks |
| **Licence / status** | Research prototype. Not licensed for operational use. |

### Structure

49 criteria → 7 dimensions → 2 objectives. 28 criteria quantitative, 21
qualitative. **Every criterion cites the clause of the source form it derives
from**; no criterion exists without one.

### Scoring

- Quantitative inputs map to 0–100 by piecewise-linear interpolation over band
  anchors, clamped outside the anchor range.
- Qualitative inputs use a five-point linguistic scale (Very Poor … Excellent)
  represented as triangular fuzzy numbers.
- Aggregation is the fuzzy weighted average; defuzzification is by centroid.
- Quantitative values enter as degenerate fuzzy numbers, so one path handles both.

## 2. Intended use

**Intended.** Decision *support* for a credit or appraisal officer completing the
People's Bank SME appraisal form. The model computes what is computable,
structures what must be judged, and produces a traceable breakdown. **The officer
decides.**

**Intended users.** Credit and appraisal officers, recommending officers, and
head-office credit staff at an institution using this or a closely similar
instrument.

**Out of scope.**

- **Automated credit decisioning.** The model does not approve or decline
  anything. It carries no authority and is not designed to.
- **Consumer, retail, or corporate credit.** It was derived from an SME
  instrument and its bands are calibrated to SME magnitudes.
- **Institutions using a different appraisal form.** The criteria trace to
  specific clauses; a different form means a different tree.
- **Any jurisdiction outside Sri Lanka** without re-deriving criteria and
  re-eliciting weights.
- **Pricing.** The model produces an ordinal risk band, not a probability of
  default, and must not be used to set interest rates.

## 3. Inputs

Criterion inputs keyed by id, each either a number or one of `VP`/`P`/`F`/`G`/`E`.
Missing criteria are **excluded and remaining weights renormalised** — never
treated as zero.

No personal data of loan applicants is required by the model itself. The
surrounding system stores business-level appraisal data.

## 4. Outputs

Two scores, **reported separately and never combined**:

| Output | Range |
|---|---|
| Credit risk / bankability | 0–100 |
| Development impact | 0–100 |

Plus, per objective: a risk band (A/B/C/D) **only when completeness ≥ 60%**, a
completeness proportion, a list of unassessed criteria, and a per-criterion
contribution decomposition summing exactly to the score.

Plus, globally: a list of critical breaches (currently DSCR < 1.0), surfaced
separately so they cannot be averaged away.

**Why the gate refuses rather than flags.** Returning a score with a caveat was
the obvious alternative and is the wrong one. Testing what conventional models do
with absent information (§5.19 of the thesis) found that both a gradient booster
and a median-imputing logistic regression score a withheld field as *favourable*
rather than as unknown. Omitting a single field moves 19.84% of applicants from
decline to approval, and an applicant who supplies nothing at all is assessed at
a 6.15% probability of default - the 6.5th percentile of real applicants. That
applicant is approved under any policy declining less than 93.5% of the
portfolio, so the result does not depend on where the threshold is set. A gate
that answers anyway, however it is captioned, is a gate that rewards
withholding.

### Why two scores and not one

The original justification was that Arvanitis et al. (2015) had found development
and credit concerns to be empirically independent in development-bank appraisal.
**That reading was wrong and has been corrected.** What they report is a positive
but statistically non-significant relationship — slope 0.048, p = 0.49 — across
109 operations, which cannot distinguish independence from a moderate
association. §5.17 of the thesis measures the association directly on 652,284
facilities and finds r = +0.40: the same direction they estimated, at a sample
size that resolves it.

The separation therefore stands on a different footing. It is not that the two
objectives are independent, but that they **disagree about individual
facilities**: they place the same firm in different risk bands 88.2% of the time,
and two or more bands apart 38.4% of the time. A facility scoring 80/40 and one
scoring 60/60 are materially different propositions that a combined score of 60
would render identical, and that remains true whether or not the two are
correlated on average.

## 5. Weights

> ## WEIGHTS ARE ELICITED
>
> `weightStatus.state = "ELICITED"`. Derived from **eleven credit practitioners**
> by the Best-Worst Method (Rezaei 2015; linear model 2016). Three of
> eighty-eight level-responses were excluded for a consistency ratio above 0.25;
> the remaining 85 were aggregated by geometric mean.
>
> **The sample is one segment, not the sector.** Ten of the eleven respondents
> are from state commercial banking and the eleventh did not state an
> institution, which is the setting the source instrument
> comes from. These weights describe that setting. They are not validated for
> lending decisions at any institution without that institution's own review.

Objective-level weights, credit risk:

| Dimension | Weight | Against equal |
|---|---:|---:|
| Project Viability & Projections | 0.2698 | 1.62 |
| Borrower & Management Capacity | 0.2190 | 1.31 |
| Credit History & Banking Conduct | 0.1594 | 0.96 |
| Market & Competitive Position | 0.1423 | 0.85 |
| Historic Financial Performance | 0.1073 | 0.64 |
| Risk, Security & Compliance | 0.1023 | 0.61 |

Forward-looking project viability outranks historic financial performance by
more than two to one, inverting the emphasis of an instrument whose longest
section is the historic financial analysis.

`research/src/derive_weights.py` refuses to mark the model `ELICITED` without
usable responses, and excludes any participant code beginning `TEST`, `PILOT`
or `DEMO`.

### Sensitivity to weights

Measured over 2,000 simulated appraisals × 400 draws per perturbation level:

| Perturbation | Credit ρ | Band unchanged | Development ρ | Band unchanged |
|---:|---:|---:|---:|---:|
| ±10% | 0.997 | 97.6% | 0.998 | 97.1% |
| ±25% | 0.982 | 94.0% | 0.989 | 92.7% |
| ±50% | 0.931 | 88.2% | 0.959 | 85.5% |
| ±100% | 0.755 | 76.1% | 0.854 | 71.2% |

Within the range experts plausibly disagree over (±25%), ranking is preserved
and roughly 93–94% of bands are unchanged.

The elicited weights turned out to fall **outside** that range: within a level
the ratio of largest to smallest reaches 3.57, and the largest departure from
equal weighting is 87%. Scoring 2,000 simulated appraisals under the equal
vector and then under the elicited one gives a rank correlation of 0.8983 for
credit risk and 0.9671 for development impact, with **no case moving two risk
bands** and about 15% moving one. The perturbation study understated the
disturbance and still called the outcome correctly.

### Structural asymmetry

A development-impact criterion carries **0.125** of its objective; a credit-risk
criterion carries **0.019–0.033**. Development criteria therefore have roughly
four to seven times the leverage. This follows from clause 5 of the source form
being a single section against six for credit material. Elicitation error on
development weights costs more, and those weights warrant more respondents.

## 6. Evaluation

### What has been evaluated

| Aspect | Method | Result |
|---|---|---|
| Structural correctness | 62 unit tests | all pass |
| Cross-implementation agreement | 280 parity checks | TS and Python agree |
| Weight sensitivity | Monte Carlo, simulated population | robust at ±25% |
| Scoring method on real outcomes | SBA National, proxy criteria | **AUC 0.41–0.53 — no discrimination** |

### What has NOT been evaluated

- **The criteria tree against real outcomes.** No public dataset contains its
  variables; People's Bank data was not available.
- **The weights.** No elicitation completed.
- **The fuzzy layer.** All SBA-observable criteria are quantitative, so the fuzzy
  machinery was never exercised by the empirical work.
- **The development objective.** Only employment proxies are observable; five of
  the nine clause-5 items have no counterpart in any available data.
- **Usability or acceptance.** No officer has used it on live applications.
- **Fairness against protected characteristics.** Still not assessed, and not
  assessable here: the SBA file records no race, sex, age, disability or
  marital-status field. Disparate impact HAS now been measured on credit-access
  proxies - rurality, firm size, firm age, sector, facility size - and the
  results are in the section below. Those are not protected classes, and passing
  on them would not establish lawfulness.

### The negative result, stated plainly

An a priori scorecard built from SBA-observable proxies achieved **AUC 0.4144
(random) and 0.5275 (temporal)** — at or below chance. The honest reading is that
the proxies are not the criteria; it does not establish that the criteria tree
works, and it does not establish that it fails.

## 7. Limitations and risks

**Do not deploy this model to make or influence real credit decisions.** The
following would each independently prevent responsible deployment:

1. **Weights are not elicited.** The model has no empirically grounded basis for
   how it trades criteria off.
2. **The tree is not validated against outcomes.** Nobody has shown that it
   separates good credits from bad.
3. **Measured disparate impact.** The scorecard fails the four-fifths rule on
   four of the five credit-access attributes tested, and would decline 36.11% of
   creditworthy agricultural borrowers - the worst rate of any sector - despite
   agriculture having the lowest default rate in the cohort at 19.19%. This is no
   longer an untested risk; it is an observed defect.
4. **Bands are a priori.** Thresholds (DSCR 1.0 → 25, and so on) reflect
   reasoning about credit policy, not calibration against outcomes.
5. **Not calibrated.** Output is ordinal. Treating a score of 80 as "20% chance of
   default" would be unfounded.
6. **Single-instrument, single-jurisdiction.** Derived from one form in one
   country.

### Risks if misused

- **Automation bias.** A number carries authority. An officer who defers to the
  score rather than using it as input has been made worse off, not better. The
  completeness gate and the separated objectives are partial mitigations; they
  are not sufficient.
- **False precision.** 80.2 looks more exact than the underlying judgements.
- **Entrenchment.** Weights elicited from current practitioners encode current
  practice, including whatever biases it contains. Elicitation reproduces the
  status quo unless deliberately examined.

## 8. Ethical considerations

**Data.** The source form is a blank template. No customer file, borrower record
or internal credit policy was accessed. The system was demonstrated with
constructed cases.

**Participants.** The elicitation instrument collects a self-chosen participant
code, years of experience, institution type and role — **no name, no customer
information**. Participation is voluntary and stoppable; responses are reported
only in aggregate.

**Fairness.** Assessed on credit-access proxies, not on protected
characteristics, which the data does not carry. Any deployment must still test
for disparate impact across whatever protected characteristics apply in the
relevant jurisdiction; nothing here substitutes for that.

What was measured, on 275,487 facilities under a policy of declining the riskiest
20%, is reported in full in §5.18 of the thesis. In summary: the scorecard fails
the four-fifths rule on rurality (0.183), firm size (0.729), firm age (0.711) and
sector (0.731); the trained gradient booster fails on rurality (0.325), sector
(0.773) and facility size (0.789). Creditworthy micro-enterprises are declined at
2.81 times the rate of large firms, and creditworthy applicants in the smallest
facility quartile at 3.42 times the rate of the largest. Within several
substantial groups the scorecard's ranking is inverted rather than merely weak -
AUC 0.4369 for wholesale trade (n = 18,018).

Base rates genuinely differ between these groups, so the selection-rate
disparities are not by themselves evidence of injustice. The error-rate
disparities, which compare only borrowers who actually repaid, have no such
defence.

**Human oversight.** The design keeps the officer as decision-maker. Credit
scoring is designated high-risk under the EU AI Act, and comparable regimes
require that adverse decisions be explained in specific terms — which is why
contributions are exact and clause-traceable rather than post-hoc approximations.

## 9. Reproducing everything

```bash
python research/src/prepare_sba.py         # clean the dataset
python research/src/leakage_analysis.py    # Term contamination evidence
python research/src/benchmark.py           # clean vs contaminated
python research/src/statistical_tests.py   # CIs, DeLong, calibration
python research/src/weight_sensitivity.py  # weight Monte Carlo
python research/src/test_parity.py         # TS/Python agreement
python research/src/bwm.py                 # BWM solver self-test
python research/src/make_figures.py        # figures
cd web && npm test                         # 62 unit tests
```

Every number in the thesis is produced by one of these. None was entered by hand.

## 10. Version history

| Version | Change |
|---|---|
| 0.1.0-draft | Initial 49-criterion tree derived from the source form. Weights placeholder. |
| 0.1.0-draft | Weights elicited from ten practitioners and applied; `weightStatus` set to `ELICITED`. |
| 0.1.0-draft | Re-derived after an eleventh respondent completed the instrument. |

**On any change to criteria, bands or weights**, bump the version. Stored
appraisals record the version that scored them, so historical recommendations
stay reproducible under the model that actually produced them.
