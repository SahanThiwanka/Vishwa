# Research Strengthening Plan

Written after the first complete draft. The thesis is defensible as it stands;
this is about moving it from *defensible* to *strong*.

**Honest framing first.** Some weaknesses cannot be fixed by more work at a
keyboard. They need people — practitioners completing an elicitation, officers
scoring cases for a reliability study. Those are marked ⛔ and no amount of
analysis substitutes for them. Everything else is work I can do, and there is a
lot of it.

---

## Where the current draft is weak

| Weakness | Severity | Fixable without people? |
|---|---|---|
| Bibliography has ~6 verified sources | **High** — an MSc expects 50+ | ✅ yes |
| Novelty of the `Term` finding unestablished | **High** — the paper's central claim | ✅ yes |
| No confidence intervals or significance tests on any AUC | **High** | ✅ yes |
| Single validation dataset | Medium | ✅ yes |
| No calibration analysis | Medium | ✅ yes |
| Weights are placeholders, RQ2 unanswered | **High** | ⛔ partly — see A4 |
| No inter-rater reliability study | **High** | ⛔ no |
| No field evaluation | Medium | ⛔ no |
| Contamination mechanism unresolved | Medium | ⚠️ needs SBA contact |

---

## Track A — Empirical rigour

The empirical chapter currently reports point estimates with no uncertainty.
That is the most visible methodological gap to an examiner who knows statistics.

### A1. Confidence intervals and significance tests
Bootstrap confidence intervals on every AUC, and DeLong's test for the paired
comparisons that matter: clean vs contaminated, random vs temporal, scorecard vs
trained models. Without these, "0.9461 versus 0.6076" is an assertion about two
numbers rather than a demonstrated difference.

**Deliverable:** every table in Chapter 5 gains CIs; the leakage claim gains a
p-value.

### A2. Calibration
Discrimination (AUC) says whether ranking works. Calibration says whether the
predicted probabilities mean anything — which is what a bank pricing risk
actually needs. Reliability curves plus Brier decomposition.

**Why it matters:** a model can rank well and still be badly calibrated, and the
distinction is exactly the kind of thing a viva probes.

### A3. Cost-sensitive evaluation
AUC weights both error types equally. A bank does not: a defaulted facility costs
far more than a declined good one. Evaluate across a range of cost ratios and
report the decision threshold each implies.

**Why it matters:** it converts an abstract metric into the number a credit
committee would actually act on.

### A4. Weight sensitivity analysis ⭐
**This partially rescues RQ2 without any respondents.**

Monte Carlo over perturbed weight vectors: sample thousands of weightings,
rescore the case set, and measure how far rankings and risk bands move. If the
model's decisions are robust to ±30% weight perturbation, then the placeholder
weights matter far less than they appear to, and that is a reportable finding. If
rankings are fragile, that is *also* a finding — and an important caution about
this whole class of model.

**Either outcome is publishable.** This is the highest-value item in the plan.

### A5. Second dataset
Add Statlog German Credit as an independent check. It is small, clean, and
universally recognised, so results on it are directly comparable with the
published literature.

---

## Track B — Literature

### B1. Build the bibliography to 50–80 verified sources
Systematically, across: SME credit scoring; fuzzy MCDM; AHP/BWM; credit scoring
in emerging economies; explainable AI in credit; development finance and dual
mandates; judgement and decision-making under discretion; data leakage and ML
reproducibility; Sri Lankan SME finance.

**Every entry verified by search.** No citation from memory — that is how
fabricated references get into a thesis.

### B2. Systematic search for affected published work ⭐
The paper claims published results on the SBA dataset warrant re-examination.
That claim is currently unsupported. Find the specific papers that use `Term`
with tree-based models, and either cite them or withdraw the claim.

**This is the difference between a publishable paper and a rejected one.**
A reviewer will ask for exactly this.

### B3. Position against the SME credit scoring literature properly
Chapter 2 is thin on the mainstream statistical lineage — Altman, Ohlson,
logistic scorecards, the Lending Club literature. An examiner will expect it.

---

## Track C — Model and system

### C1. Classical benchmark
Add an Altman Z-score-style classical scorecard as a reference point. It is the
benchmark every credit examiner knows.

### C2. Band sensitivity
The a priori band thresholds are a design choice presented without
justification. Test how much the results move under alternative thresholds.

### C3. Model card
A formal model card documenting intended use, out-of-scope use, training data,
evaluation, limitations, and ethical considerations. Increasingly expected for
any deployed decision model, and it demonstrates awareness of responsible-AI
practice.

### C4. System hardening
Rate limiting on sign-in, pagination, accessibility pass, CI workflow.

---

## Track D — Blocked on people ⛔

Listed so the thesis can be explicit about what was not done and why.

- **Elicitation** — 3+ practitioners, 15 minutes each. Until then RQ2 is
  unanswered and weights stay placeholders.
- **Inter-rater reliability** — N officers independently scoring M cases. The
  single most valuable addition to the whole study, because it would measure the
  premise the research rests on.
- **Usability / acceptance evaluation** — SUS or TAM with real officers.
- **Contamination mechanism** — requires contact with the SBA or the dataset
  authors.

---

## Execution order

Highest value per unit of effort first:

| # | Item | Why first |
|---|---|---|
| 1 | **A4** weight sensitivity | Partially answers RQ2 without respondents |
| 2 | **A1** CIs and significance | Biggest visible methodological gap |
| 3 | **B2** systematic search | Determines whether the paper is submittable |
| 4 | **B1** bibliography to 50+ | Explicit MSc requirement |
| 5 | **A2, A3** calibration and cost | Converts metrics into banking decisions |
| 6 | **A5, C1** second dataset, classical benchmark | Generalisation |
| 7 | **C2, C3** band sensitivity, model card | Rigour and responsible practice |
| 8 | **C4** system hardening | Lowest research value |

---

## What "perfect" cannot mean here

Worth stating plainly, because it shapes what to aim for.

This study cannot become a validated credit scoring model for Sri Lankan SME
lending. That would require People's Bank's own historical files with outcomes,
which are confidential and were not available. No amount of additional analysis
on proxy data changes that.

What it *can* become is a rigorous, honest, well-evidenced study that makes two
transferable contributions — a caution about a widely used benchmark, and a
methodological result about validating instrument-specific models — supported by
a working artefact and a properly grounded literature review.

That is a strong MSc thesis and a publishable paper. Aiming beyond it would mean
claiming things the evidence does not support, which is the one thing this
project has consistently refused to do.
