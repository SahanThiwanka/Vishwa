# Datasets — download instructions

Download into `research/data/raw/` using the **exact filenames** in the "Save as" column. The pipeline
looks for those names. This folder is git-ignored; the files are too large to commit.

---

## 1. SBA National — PRIMARY dataset ⭐

The one that carries the empirical chapter. ~899,000 US Small Business Administration loan guarantees,
1987–2014, **with real repayment outcomes**. This is the closest public analogue to SME loan appraisal
with ground truth that exists.

| | |
|---|---|
| **Source** | Kaggle — search: `Should This Loan be Approved or Denied` |
| **Origin** | Li, Mickel & Taylor (2018), *Journal of Statistics Education* 26(1) |
| **Save as** | `research/data/raw/SBAnational.csv` |
| **Size** | ~180 MB, ~899,164 rows, 27 columns |
| **Target variable** | `MIS_Status` — `P I F` (paid in full) vs `CHGOFF` (charged off / defaulted) |

Key columns we use: `Term`, `NoEmp`, `NewExist`, `CreateJob`, `RetainedJob`, `DisbursementGross`,
`GrAppv`, `SBA_Appv`, `UrbanRural`, `RevLineCr`, `LowDoc`, `NAICS`, `MIS_Status`.

**Note `CreateJob` and `RetainedJob`** — employment-generation fields. These are the only public proxy
for the development-impact objective, and they matter for Chapter 5.

---

## 2. Statlog German Credit — benchmark

Small, clean, and universally recognised by credit-scoring reviewers. Including it means your results
sit on a comparable footing with the published literature.

| | |
|---|---|
| **Source** | UCI Machine Learning Repository — dataset 144, *Statlog (German Credit Data)* |
| **Save as** | `research/data/raw/german.data` (and `german.doc` for the column key) |
| **Size** | 1,000 rows, 20 attributes |
| **Target** | column 21 — `1` = good credit, `2` = bad credit |

Use the `german.data` (space-delimited, coded) version, not `german.data-numeric`.

---

## 3. World Bank Enterprise Surveys — Sri Lanka context

Not for modelling — for **Chapter 1 and 2**, to evidence the access-to-finance problem with real Sri
Lankan firm-level data instead of assertion.

| | |
|---|---|
| **Source** | `enterprisesurveys.org` → Data → Sri Lanka (registration required, free) |
| **Save as** | `research/data/raw/wbes_srilanka.csv` |
| **Use** | % of SMEs citing access to finance as a major constraint; loan application/rejection rates |

---

## 4. Central Bank of Sri Lanka — national context

Published statistics for the motivation section. Annual Report and *Economic and Social Statistics of
Sri Lanka* carry SME credit volumes and NPL ratios. Cite as publications, no download needed.

---

## Honest limitation you must write into the thesis

SBA and German Credit contain the **financial and credit-conduct** variables. Neither contains the
**qualitative** ones — Porter's five forces, management quality, technological and environmental risk —
nor most of the development-impact items.

So the validation is deliberately split, and the thesis must say so plainly:

- **Quantitative branch** (28 criteria) → validated empirically on SBA, with real AUC / KS / F1 against
  actual default outcomes, benchmarked versus logistic regression and gradient boosting.
- **Qualitative branch** (21 criteria) → evaluated through documented expert judgement on a case set,
  reported with the number of experts and their consistency ratios.
- **Development-impact objective** → only partially observable, via SBA's `CreateJob` / `RetainedJob`.
  Everything else in that objective is design contribution, not empirically validated. **Say this.**

Do not blur these three into a single claim of "the model was validated." State which branch, on what
data, with what n. A clearly-bounded result is worth more in review than an overreaching one, and it is
the first thing an examiner will probe.

---

## Verify your downloads

```bash
python research/src/check_data.py
```

## SBA 7(a) and 504 FOIA extracts

The SBA's own loan-level publication, refreshed quarterly. Used by
`research/src/sba_foia_replication.py` to establish that the `Term` artefact is
present in the authoritative records rather than introduced by the widely used
derivative file, and to show it is absent from the 504 programme.

Source: <https://data.sba.gov/dataset/7a-504-foia>

Download into `research/data/raw/` and rename as below. Both are gitignored.

| Save as | Approx. size | Release used |
|---|---|---|
| `FOIA_7a_FY2000_FY2009.csv` | 318 MB | as of 2026-06-30 |
| `FOIA_7a_FY2010_FY2019.csv` | 255 MB | as of 2026-06-30 |
| `FOIA_504_FY1991_FY2009.csv` | 54 MB | as of 2026-06-30 |

**The two files spell the paid-in-full status differently** — `P I F` in the 7(a)
extract, `PIF` in the 504 one. Filtering for one spelling silently yields a frame
of pure charge-offs and a default rate of 100%. `sba_foia_replication.py` accepts
both.

A later quarterly release will contain more resolved loans and the figures will
move slightly. Re-run the script and `scripts/verify_claims.py` will flag any
chapter that no longer matches.
