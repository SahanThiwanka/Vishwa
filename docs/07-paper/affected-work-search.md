# Systematic search: published work affected by the `Term` contamination

**Status: EVIDENCE GATHERED, VERIFICATION INCOMPLETE.**

The paper's §VIII states that published results on the SBA National dataset
warrant re-examination. That claim needs specific evidence. This document records
what the search found and — equally important — what still has to be verified
before the claim can stand in a submitted paper.

**Do not submit the paper with the §VIII claim until Section 5 below is done.**

---

## 1. What we are looking for

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

## 3. What the search found

Searches run September 2026 across general web and academic indexes.

| Reported result | Model | Source type | Relevance |
|---|---|---|---|
| **ROC AUC 0.9714** | XGBoost | Journal paper, business process management | **Within 0.002 of our contaminated GBM (0.9726)** |
| ROC AUC ~0.97 | XGBoost | Applied project | Same region |
| ROC AUC 0.94 | not stated | SBA loan model | Above the probe ceiling |
| AUC 0.89 | Random Forest with resampling | Journal paper | At the probe ceiling |
| Accuracy 98.5%, recall 99% | Logistic regression | Journal paper, Jan 2024, explicitly 899,164 observations × 27 features | Implausible for credit; warrants checking |

Multiple sources independently report **`Term` among the most important
features**, typically alongside `DisbursementGross`, `SBA_Appv` and `GrAppv`.

### The pattern

Published tree-model results on this dataset cluster in the **0.94–0.97** range.
Our clean specification reaches **0.6076** temporally and **0.7898** on a random
split. A variable with no economic meaning reaches **0.887–0.897** on its own.

That is the argument, and it is a strong one. But it is currently an argument
about a *pattern*, not about specific verified papers.

## 4. What we verified, and what we did not

**Verified by reading:** SharafEldin, Idrees and Ouf (2025), *IJACSA* 16(6) —
retrieved and read. It uses **Agricultural Bank of Egypt data, not SBA**, so it is
**not** evidence for this claim and must not be cited as such. Recorded here
because checking it and finding it irrelevant is part of the search record.

*(It is, separately, a useful citation for the inconsistency premise: its abstract
states that traditional credit assessment "often relied on subjective judgment,
leading to inconsistent decisions".)*

**Not verified.** The results in Section 3 come from search-result summaries and
abstracts. For each, we have **not** confirmed:

- which SBA file was used (the National file, the smaller teaching subset, or
  another SBA extract);
- whether `Term` was among the features actually fed to the model;
- what preprocessing was applied — some studies resample heavily, which changes
  what an AUC means;
- whether right-censoring was controlled.

**A result that looks inflated may have a different explanation.** Heavy
oversampling, leakage from a different field, or evaluation on a non-comparable
subset would each produce a high number without involving `Term` at all.

## 5. Required before submission

For each candidate study:

- [ ] Obtain the full text.
- [ ] Confirm the dataset is the SBA National file.
- [ ] Confirm `Term` (or a derivative) is in the feature set.
- [ ] Record the model class and whether it can split on exact values.
- [ ] Record the exact metric, the split protocol, and any resampling.
- [ ] Classify: **likely affected** / **not affected** / **cannot determine**.

Then in the paper:

- Cite only the studies verified as **likely affected**.
- State the number examined and the number affected.
- **Name no study as affected without having read it.** An incorrect accusation
  of methodological error is a serious matter, and it would be the first thing a
  reviewer checks.

## 6. How to phrase the claim now

If the verification in Section 5 has not been completed, §VIII should say:

> Published results on this dataset using tree-based models cluster in the
> 0.94–0.97 AUC range. A variable with no economic content reaches 0.887–0.897 on
> its own, and our contaminated specification reaches 0.9726 against 0.6076 when
> `Term` is excluded. We have not examined the full text of these studies and do
> not claim that any specific result is an artefact; we report that results in
> this region, obtained from models able to split on exact term values, cannot be
> distinguished from the artefact on published information alone, and that this
> warrants re-examination.

That is defensible without having read every paper, and it is the claim to make
if time runs short. **The stronger claim requires the reading.**

---

## Search queries used

Recorded for reproducibility:

1. `SBA National dataset "Should This Loan Be Approved or Denied" Term variable data leakage credit scoring`
2. `SBA National dataset small business loan default prediction random forest XGBoost gradient boosting AUC results paper`
3. `"SBA" loan dataset machine learning "Term" feature importance most important predictor default prediction study`
4. `SBA loan default prediction "0.9714" OR "97.14" XGBoost gradient boosting ROC AUC small business`
5. `"Machine Learning Approach for Small Business Loan Default Prediction" SBA authors journal 2024`

**Not exhaustive.** No academic database with full-text search (Scopus, Web of
Science, IEEE Xplore) was queried, and those are where a proper systematic search
would run. Access to one through the university library would substantially
improve this.
