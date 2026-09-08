# SME Credit Appraisal — MSc Research Project

**Working title:** *A Fuzzy Multi-Criteria Decision Model for SME Credit Appraisal in Development
Banking: Formalising Narrative Appraisal under Dual Credit-Risk and Development-Impact Objectives —
Evidence from Sri Lanka*

Institution: NSBM Green University · MSc in Information Technology
Supervisor: Dr. Pabudi Abeyrathne

This repository holds **both** halves of the project: the research (thesis, analysis, results) and the
product (a working Next.js appraisal system). They are deliberately separate and communicate through
one file: `shared/model/criteria-tree.json`.

---

## Ground rule

> **Every number that appears in the thesis must be reproducible by running code in this repository.**

No figure, table, accuracy score or p-value gets written into a chapter unless a script in `research/`
produced it and wrote it into `research/outputs/`. If an experiment could not be run, the claim is cut
and the gap is recorded as a stated limitation — not filled with a plausible-looking number.

`shared/model/criteria-tree.json` currently carries `weightStatus.state = "PLACEHOLDER"`. **Nothing
computed from placeholder weights may be reported.** That flag flips only after real elicitation.

---

## Folder structure

```
Vishwa/
├── README.md                     ← you are here
├── docs/                         ← all research writing
│   ├── 00-source-material/       ← original People's Bank form + original proposal (never edit)
│   ├── 01-proposal/              ← revised proposal
│   ├── 02-literature/            ← literature review + bibliography
│   ├── 03-methodology/           ← research design, elicitation instrument, evaluation protocol
│   ├── 04-criteria-model/        ← criteria tree documentation + weight derivation
│   ├── 05-results/               ← figures/ and tables/ — COPIED FROM research/outputs, never hand-made
│   ├── 06-thesis/                ← thesis chapters
│   └── 07-paper/                 ← conference / journal paper
│
├── shared/
│   └── model/
│       └── criteria-tree.json    ← SINGLE SOURCE OF TRUTH for criteria, bands, scales, risk bands
│
├── research/                     ← Python: empirical validation (does NOT run in production)
│   ├── data/raw/                 ← downloaded datasets (git-ignored, too large to commit)
│   ├── data/processed/
│   ├── src/                      ← analysis pipeline
│   └── outputs/figures|tables/   ← generated artefacts, feed docs/05-results
│
├── web/                          ← Next.js 16 + TypeScript + Tailwind 4 — the deliverable system
└── scripts/                      ← setup and data-download helpers
```

### Why research and web are separate

The product is TypeScript because that is the stack being demonstrated and maintained. The empirical
validation is Python because pandas/scikit-learn/SHAP have no real TypeScript equivalent. They never
talk to each other at runtime — the Python pipeline *calibrates and validates*, then exports weights
as JSON, and the Next.js app *consumes* that JSON. One-way handoff, easy to explain in a viva.

---

## The model in one paragraph

The People's Bank appraisal form is a narrative instrument: an officer writes prose about management
quality, market competition and environmental risk, then forms a judgement. This project formalises
that form into **49 criteria across 7 dimensions under 2 objectives** — every criterion traceable to a
numbered clause of the original form. Quantitative criteria (28) map raw financial values to a 0–100
score through piecewise-linear bands. Qualitative criteria (21) are captured on a 5-point linguistic
scale, represented as triangular fuzzy numbers, aggregated by fuzzy weighted average and defuzzified
by centroid. The result is two scores reported **side by side, never merged**: a credit-risk score and
a development-impact score.

**The second objective**, taken from clause 5 of the bank's form, scores nine development outcomes
(employment, women's participation, import substitution, foreign exchange earnings), with clause 3.4.1
splitting employment by gender. Mainstream credit scoring discards all of this; a state bank with a
development mandate cannot.

> **Novelty claim corrected.** An earlier version of this file claimed no published model handles both
> objectives at once. That is false — Gutiérrez-Nieto, Serrano-Cinca & Camón-Cala (2016, *J. Business
> Ethics*) score social impact alongside credit risk, and Roy & Shaw (2021, *Financial Innovation*)
> already apply BWM to SME credit scoring. Both claims are withdrawn in Chapter 2 (§2.3.3, §2.4.1).
>
> What survives: the two objectives are **never aggregated** here, which prior work does do — and that
> is supported by Arvanitis et al. (2015), who find development and credit concerns to be empirically
> independent in development-bank appraisal. The substantial contributions are instead the `Term`
> contamination finding and the methodological result that instrument-specific models cannot be
> validated on datasets lacking their variables (§2.7).

---

## Getting started

```bash
cd web && npm run dev
```

Dataset download instructions: see `research/data/DATASETS.md`.

---

## Status

| Component | State |
|---|---|
| Criteria tree | ✅ v0.1.0-draft — 49 criteria, all clause-traceable |
| Scoring engine (TypeScript) | ✅ 9/9 structural checks |
| Test suite | ✅ 62 tests (engine, validation, auth) |
| Authentication + role-based sign-off | ✅ clause-7 chain enforced server-side |
| Input validation on all Server Actions | ✅ |
| Scoring engine (Python) | ✅ parity-verified against TypeScript, 280 checks |
| Web application | ✅ intake, live scoring, explainability, audit trail |
| DOCX export in bank format | ✅ |
| SBA data pipeline + benchmarks | ✅ |
| `Term` contamination finding | ✅ documented, reproducible |
| BWM elicitation instrument | ✅ built and verified |
| BWM solver + weight derivation | ✅ self-tested |
| **Criterion weights** | ⛔ **PLACEHOLDER — no respondents yet** |
| Thesis chapters 1–6 | ✅ drafted (~10,400 words) |
| Thesis §6.1–6.2 (elicitation results) | ⛔ **awaiting respondents** |
| Journal/conference paper | ⬜ not started |

### The one blocker

Everything except the elicitation is done. `derive_weights.py` will not mark the
model `ELICITED` without usable responses, and it should not be made to. Until
practitioners complete the instrument at `/elicitation`:

- RQ2 is unanswered
- every score in the thesis stays labelled as computed under placeholder weights

Three respondents would change that. Deployment to Vercel, or fifteen minutes each
on a laptop, are both sufficient.

## Rebuilding everything

```bash
python research/src/prepare_sba.py        # clean the raw dataset
python research/src/leakage_analysis.py   # the Term contamination evidence
python research/src/benchmark.py          # clean vs contaminated benchmarks
python research/src/test_parity.py        # TypeScript/Python engine agreement
python research/src/bwm.py                # BWM solver self-test
python research/src/derive_weights.py     # weights (needs responses)
python scripts/build_thesis.py            # assemble THESIS.docx
cd web && npm run test:scoring && npm run dev
```
