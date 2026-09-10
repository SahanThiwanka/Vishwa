# Supervisor Briefing

**Project:** A Dual-Objective Decision Support Model for SME Credit Appraisal
**Student:** AAV Athukorala · MSc IT, NSBM Green University
**Supervisor:** Dr. Pabudi Abeyrathne
**Date:** September 2026

Accompanies the thesis draft (~15,400 words), the working system, and a draft
conference paper.

---

## 1. What this document is for

Three things have changed since the proposal, each for a reason that should be
reviewed before the work goes further. This briefing sets them out, summarises
what the study now contains, and lists the decisions needed.

---

## 2. Three changes since the proposal

### 2.1 The claimed contribution was already published

The proposal claimed novelty in applying fuzzy multi-criteria methods to SME
credit scoring. The literature review found this is not novel:

- **Roy and Shaw (2021)**, *Financial Innovation* 7(1) — a multicriteria credit
  scoring model for SMEs using Best-Worst Method combined with a ranking method:
  the same hybrid the proposal treated as new.
- **Gutiérrez-Nieto, Serrano-Cinca and Camón-Cala (2016)**, *Journal of Business
  Ethics* 133(4) — a credit score system evaluating social impact alongside
  financial aspects using MCDM.

Both claims are **withdrawn explicitly** in §2.5.3 and §2.6.1 rather than
restated in a weaker form. The contribution now rests elsewhere (§3 below).

### 2.2 Weight elicitation was not carried out

The methodology specifies eliciting criterion weights from credit practitioners
by Best-Worst Method. **This was not done.** Recruiting officers requires
institutional access and participant time that were not secured.

What exists: the web instrument (86 comparisons, ~15 minutes, no name or customer
data collected), a verified BWM solver, and the full analysis pipeline. What does
not exist: any practitioner response.

The model therefore carries `weightStatus: PLACEHOLDER`, and this is enforced
mechanically — the derivation script refuses to mark it otherwise without usable
responses, and an automated check fails the build if any chapter claims
elicitation occurred.

### 2.3 The research questions were revised

RQ2 originally asked what weights practitioners assign. Since that cannot be
answered, it now asks **how much the model's output depends on its weights at
all** — answerable by simulation, and it bounds what the missing elicitation
costs. RQ4 was likewise reframed to something testable on available data.

§1.3 and §6.1 state both changes openly. This is a narrowing of scope, not a
substitution of equivalent value, and the thesis says so.

---

## 3. What the study now contributes

### 3.1 Contamination in a widely used benchmark dataset — the principal finding

The SBA National dataset (899,164 loans) is a common benchmark in
small-business credit research. Its `Term` field carries information about the
outcome:

| Evidence | Value |
|---|---|
| Repaid loans with term a multiple of 12 | 86.4% |
| Charged-off loans with term a multiple of 12 | 8.5% |
| AUC of that single boolean alone | **0.8894** |
| Same, within every approval year 1990–2010 | 0.859 – 0.900 |
| 2007 approvals at 60 months | 11.1% default |
| 2007 approvals at 59 / 61 months | 86.7% / 92.2% |

Excluding the field drops gradient-boosting temporal AUC from **0.9461 to
0.6076**. Confidence intervals do not overlap; paired DeLong tests give
p < 0.001.

Twelve is not an arbitrary modulus. Across twenty tested, it leads at 0.8859 and
its divisors fall away in the order 12 > 6 > 4 > 3 > 2 — the dilution expected if
multiples of twelve are the carrier — while moduli that do not divide twelve sit
at or below chance (11: 0.4660, 13: 0.4699). The contamination also reaches the
dataset's **own documentation**: Li, Mickel and Taylor derive a `RealEstate`
feature from `Term` and report default rates of 1.64% against 21.16%, a contrast
largely restating roundness.

The finding emerged because an AUC of 0.9726 was investigated rather than
reported. The mechanism is **not** established — the obvious hypothesis (that
`Term` records survival time) was tested and rejected — and the thesis reports it
as unresolved rather than asserting a cause.

### 3.2 A methodological result

An instrument-specific appraisal model cannot be validated on a dataset lacking
its variables. Evidenced by a negative result: an a priori scorecard built from
SBA-observable proxies achieved **AUC 0.4144 / 0.5275**, at or below chance. That
is reported as it occurred.

### 3.3 Supporting findings

- **Weight sensitivity.** At ±25% perturbation, rank correlation holds at 0.982
  and 94% of risk bands are unchanged — bounding the placeholder-weight problem.
- **Objective separability.** Across 652,284 facilities the two objectives
  correlate at r = +0.40. This removes the *strong* form of the premise the design
  was justified on, but does **not** contradict Arvanitis et al. (2015): reading
  that paper showed their estimate was also positive (slope 0.048) and merely
  non-significant in 109 observations. This study measures the same direction at a
  size that resolves it. The objectives nonetheless band the same facility
  differently **88.2%** of the time, which is now the argument for separation.
- **Development impact is positively associated with default** (10.8% lowest band
  vs 30.3% highest). Reported as association, not cause.
- **Calibration degrades ~700-fold** across a temporal boundary while
  discrimination falls far less: models keep ranking while systematically
  under-pricing risk.
- **Disparate impact, including in our own artefact.** The scorecard fails the
  four-fifths rule on four of five credit-access attributes and would decline
  **36.11% of creditworthy agricultural borrowers** — the worst of any sector —
  though agriculture has the lowest default rate at 19.19%. Bootstrap intervals
  are tight and a permutation floor (0.973–0.999) shows the measure's known bias
  cannot explain it. These are credit-access proxies; the data holds no protected
  characteristic, and no claim about lawful discrimination follows.
- **Conventional models reward withholding information.** Blanking one field
  scores 97.7% of applicants as less risky and moves 19.84% from decline to
  approve. An applicant supplying **nothing** scores 0.0615 against a 0.2293
  decline threshold and is approved. This is the empirical case for the
  completeness gate: refusing is the only response that cannot be gamed.

### 3.4 The artefact

A working system: 49 clause-traceable criteria, live dual-objective scoring,
exact per-criterion explanation, a completeness gate, authenticated role-based
sign-off mirroring clause 7, and export in the People's Bank report format. 89
unit tests; the TypeScript and Python engines are parity-checked across 280 cases;
62 automated checks verify every load-bearing figure in the thesis against the
generated result tables, and CI runs all of it.

---

## 4. Reproducibility

Every number in the thesis is generated by code in the repository. No value was
entered by hand.

`scripts/verify_claims.py` re-derives 25 load-bearing figures from the result
tables and checks them against the chapters. It currently passes, and it has
already caught two real drifts during drafting.

```
python research/src/prepare_sba.py          # clean the dataset
python research/src/leakage_analysis.py     # contamination evidence
python research/src/benchmark.py            # clean vs contaminated
python research/src/statistical_tests.py    # CIs, DeLong, calibration
python research/src/weight_sensitivity.py   # weight Monte Carlo
python research/src/objective_independence.py
python research/src/cost_analysis.py
python research/src/modulus_probe.py        # is twelve arbitrary?
python research/src/realestate_probe.py     # the documentation's own feature
python research/src/fairness_analysis.py    # disparate impact + bootstrap
python research/src/missingness_analysis.py # what withholding does
python research/src/bwm.py                  # BWM solver verification
python scripts/verify_claims.py             # 62 consistency checks
cd web && npm test                          # 89 unit tests
```

---

## 5. Known weaknesses

Listed here rather than buried, because they should shape the feedback.

The three that need people are no longer just identified — `docs/PROTOCOLS.md`
sets out each as a runnable study: participant numbers and why, consent wording,
session scripts, the analysis to apply, and what has to be rewritten afterwards.
They need people and time, not design work.

| Weakness | Status |
|---|---|
| No weight elicitation | RQ2 as originally posed is unanswered |
| No inter-rater reliability study | The inconsistency premise is cited (Cortés et al., 2016) but not measured |
| Validation on a US proxy dataset | Central limitation, stated in §1.6 before any result |
| Criteria tree not validated against outcomes | No dataset contains its variables |
| Fuzzy layer not exercised by the validation | All observable criteria are quantitative |
| Development objective thinly proxied | Only employment observable; 5 of 9 clause-5 items absent |
| Fairness on protected characteristics untested | Not testable on this data — no race, sex or age field. Credit-access proxies **are** now tested, and the artefact fails four of five |
| No field evaluation | No officer has used the system on live applications |
| Contamination novelty not established | One affected study now verified by full text (Yussuph, 2024); two candidates unobtainable without library access |
| Literature only partly read | 8 of 58 sources read in full — the ones carrying substantive claims. Three of those corrections changed the text. One source could not be obtained at all and the claim on it was weakened accordingly |

---

## 6. Decisions needed

1. **Is the revised scope acceptable?** The study now contributes a dataset
   finding and a methodological result rather than a novel scoring model. §2.8
   and §6.6 state this plainly. If a different emphasis is wanted, it is better
   known now.

2. **Can practitioner access be arranged?** Three respondents at fifteen minutes
   each would answer RQ2 as originally posed. The instrument is built and tested.
   This is the single highest-value addition available.

3. **Is there a route to institutional data?** Even a few hundred anonymised
   historical files with outcomes would allow the criteria tree itself to be
   tested rather than a proxy.

4. **Does the thesis structure match NSBM requirements?** It follows standard
   academic convention; the department's template or rubric has not been seen and
   the structure should be checked against it.

5. **Should the conference paper be submitted?** The contamination finding stands
   alone and is drafted. It requires one further step first: a systematic search
   confirming which published studies are affected. The protocol is in
   `docs/07-paper/affected-work-search.md`; **no paper should be named as
   affected without being read.**

---

## 7. Accompanying materials

| Path | Contents |
|---|---|
| `docs/06-thesis/THESIS-NSBM.docx` | **The thesis**, in NSBM senate format, IEEE referencing |
| `docs/07-paper/paper-term-contamination.md` | Conference paper draft |
| `docs/07-paper/affected-work-search.md` | Search record: one affected study verified, four excluded, two unobtainable |
| `docs/02-literature/bibliography.md` | 58 sources with per-entry verification status |
| `docs/04-criteria-model/MODEL-CARD.md` | Intended use, limitations, risks, fairness results |
| `docs/PROTOCOLS.md` | **The three outstanding studies, written to be run** |
| `docs/VIVA-PREPARATION.md` | Anticipated questions, weak points, numbers to memorise |
| `docs/DEPLOYMENT.md` | Step-by-step deployment to Vercel and PostgreSQL |
| `docs/RESEARCH-STRENGTHENING-PLAN.md` | The original plan, annotated with what was delivered |
| `web/` | The system |
| `research/` | Analysis pipeline and generated results |

**A note on the bibliography.** Sources are marked read / verified-not-read /
retrieval-failed / needs-confirming. Bibliographic details were checked against
authoritative records; **8 of 58 have been read in full**, and those are the ones
carrying substantive claims.

That reading mattered more than expected. Of the eight, **three did not say what
the thesis had said they said** — most seriously Arvanitis et al. (2015), whose
"independence" result turns out to be a positive but non-significant relationship
in 109 observations, which the design's justification had been resting on. All
three are corrected in the text, and §7 of the viva document prepares the answers.
The remaining 28 unread entries are the clearest argument for library access.
