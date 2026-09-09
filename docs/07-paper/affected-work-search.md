# Systematic search: published work affected by the `Term` contamination

**Status: ONE STUDY VERIFIED BY FULL TEXT. Four excluded by full text. Two
candidates unobtainable.**

The paper's §VIII states that published results on the SBA National dataset
warrant re-examination. That claim needs specific evidence. This document records
what the search found, what was read, and what could not be obtained.

The standing rule is unchanged: **name no study as affected without having read
it.** An incorrect accusation of methodological error is a serious matter and
would be the first thing a reviewer checks.

---

## 1. Inclusion criteria

Studies that:

1. use the SBA National dataset (899,164 loans, 1987–2014), **and**
2. include `Term` (or a feature derived from it) among their predictors, **and**
3. use a model class able to split on exact values — trees, forests, boosting —
   rather than a monotone linear model, **and**
4. report discrimination in the region a meaningless roundness probe reaches.

Criterion 3 matters: our results show a linear model gains far less from the
contamination than a tree ensemble, because exploiting the artefact requires
splitting on exact term values rather than treating term monotonically.

## 2. Our own reference points

| Quantity | Value |
|---|---|
| Contaminated gradient boosting, random split | **0.9726** |
| Contaminated gradient boosting, temporal split | **0.9461** |
| Roundness probe alone (no economic content) | **0.8870 / 0.8965** |
| Clean gradient boosting, temporal split | **0.6076** |

Any result on this dataset at or above ~0.89, obtained from a tree-based model
given `Term`, is in the region the artefact alone can produce.

## 3. Verified: likely affected

### Yussuph, T.T. (2024)

> 'Leveraging Machine Learning Algorithm to Enable Access to Credit for Small
> Businesses in the United States of America', *International Journal on
> Cybernetics & Informatics*, 13(1), pp. 53–66.
> doi:10.5121/ijci.2024.130105

**Full text obtained and read.** Every inclusion criterion is met.

| Criterion | Finding in the paper |
|---|---|
| Dataset | "Data was sourced from the SBA website. It has 27 columns and 899164 rows" — the National file |
| `Term` in features | Yes, and **ranked first in both models**: Random Forest importance ordered "Term, Disbursement Gross, SBA Approval, Gross Approval"; XGBoost "Term, Urban or Rural, Retained Job, Gross Approval" |
| Model class | Random Forest and XGBoost — both split on exact values |
| Reported result | **ROC-AUC 97% (XGBoost), 96.1% (Random Forest)**; precision and recall 95–96% |
| Split protocol | 70/15/15 train/validation/test, stratified k-folds, balanced class weights — **random, not temporal** |
| Resampling | None stated beyond balanced class weighting |

The reported AUC sits above our contaminated gradient booster (0.9726 random,
0.9461 temporal) and far above the 0.887–0.897 that the roundness boolean reaches
on its own. The feature the study ranks first is the contaminated one.

**A second leakage path cannot be excluded, and this must be stated whenever the
study is cited.** The paper describes preprocessing `ChgOffDate` to a datetime
type and `Balance Gross` and `ChgOffPrinGr` to numeric types, and never states
that these fields were dropped before modelling. All three are populated only
after a loan has been charged off. If they entered the feature set, that alone
would explain a result of this magnitude without any involvement of `Term`.

**Classification: affected by at least one leakage path; which one cannot be
determined from the published text.** That is the honest finding, and it is
arguably the stronger one — it shows the dataset carries more than one trap, and
that the paper's own description does not let a reader tell which was triggered.

## 4. Excluded by full text

Checking a candidate and finding it irrelevant is part of the search record.

| Study | Reason for exclusion |
|---|---|
| Haque, F.M.A. and Hassan, M.M., 'Bank Loan Prediction Using Machine Learning Techniques', arXiv:2410.08886 | Not the SBA dataset — 148,670 instances, 37 attributes. No occurrence of "SBA" in the text. Reports 99.99% accuracy from AdaBoost, which is implausible for credit, but on a different dataset and so out of scope here. |
| Li, D. (2025) 'The Comprehensive Analysis of Bank Loan Approval Prediction Based on Machine Learning Models', SciTePress | No occurrence of "SBA". Different dataset. |
| 'Bank Loan Prediction Using Machine Learning Techniques', *American Journal of Industrial and Business Management*, 14 (2024), pp. 1690–1711 | No occurrence of "SBA". Different dataset. |
| SharafEldin, Idrees and Ouf (2025), *IJACSA* 16(6) | Agricultural Bank of Egypt data, not SBA. Separately useful for the inconsistency premise: its abstract states that traditional credit assessment "often relied on subjective judgment, leading to inconsistent decisions". |

## 5. Candidates that could not be obtained

| Study | Obstacle | What is known |
|---|---|---|
| Zhou et al. (2023), 'Machine Learning Approach for Small Business Loan Default Prediction' | Available only via ResearchGate, which refuses automated retrieval | Reported as SBA data, Random Forest and XGBoost, **AUC 0.89**, with `Term`, `Disbursement Gross`, `SBA Approval` and `Gross Approval` named as the significant variables. Matches every criterion on the available description, and 0.89 is exactly the roundness ceiling — but this is second-hand and must not be cited as verified. |
| 'Ensemble-Based Machine Learning Algorithm for Loan Default Risk Prediction', *Mathematics*, 12(21), 3423 | Publisher returns HTTP 403 to automated retrieval | Not established whether it uses the SBA National file. |

Both are obtainable through a university library. Retrieving them is the single
highest-value remaining step for §VIII.

## 6. How the claim should be phrased

The verification now supports naming one study. The wording below is what the
evidence carries and no more:

> We examined seven candidate studies. Four were excluded on reading as not using
> this dataset, and two could not be obtained. One, Yussuph (2024), meets every
> criterion: it uses the SBA National file, ranks `Term` as the most important
> feature for both a random forest and an XGBoost model, and reports ROC-AUC of
> 0.961 and 0.97 under a random split. A variable with no economic content
> reaches 0.887–0.897 on this dataset unaided, and our own contaminated
> specification reaches 0.9726 against 0.6076 when `Term` is excluded. We do not
> claim to have reproduced that study's pipeline, and we note that its
> description of preprocessing leaves open a second leakage path through the
> post-charge-off fields, which it does not state were dropped. What we do claim
> is that a result in this region, from a model able to split on exact term
> values and ranking that field first, cannot be distinguished from the artefact
> on published information alone.

**Do not strengthen this to an assertion that the study's result is an
artefact.** The pipeline was not reproduced, and a competing explanation is live.

---

## Search queries used

Recorded for reproducibility. Run September 2026.

1. `SBA National dataset "Should This Loan Be Approved or Denied" Term variable data leakage credit scoring`
2. `SBA National dataset small business loan default prediction random forest XGBoost gradient boosting AUC results paper`
3. `"SBA" loan dataset machine learning "Term" feature importance most important predictor default prediction study`
4. `SBA loan default prediction "0.9714" OR "97.14" XGBoost gradient boosting ROC AUC small business`
5. `"Machine Learning Approach for Small Business Loan Default Prediction" SBA authors journal 2024`
6. `SBA National dataset "Should this loan be approved or denied" XGBoost random forest loan default prediction AUC feature importance Term`
7. `"SBA" loan dataset 899164 OR "899,164" machine learning default prediction paper Term feature`
8. `"SBA" small business loan default prediction machine learning paper "Term" most important feature random forest AUC 2023 2024 2025 journal`
9. `Zhou "Machine Learning Approach for Small Business Loan Default Prediction" SBA 2023 random forest AUC 0.89 full text pdf`

**Still not exhaustive.** No academic database with full-text search (Scopus, Web
of Science, IEEE Xplore) was queried, and those are where a proper systematic
search would run. `scripts/read_pdf.py` extracts and probes a downloaded PDF
against the inclusion criteria, so the marginal cost of checking each additional
candidate is now small — the constraint is access, not effort.
