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

### Research

| Component | State |
|---|---|
| Criteria tree — 49 criteria, clause-traceable | ✅ |
| `Term` contamination finding | ✅ reproducible, figures generated |
| Weight sensitivity (Monte Carlo) | ✅ robust at ±25%; structural asymmetry found |
| AUC confidence intervals, DeLong, calibration | 🔄 running |
| Bibliography | ✅ 50 entries, details verified |
| Thesis chapters 1–6 | ✅ ~13,000 words |
| Conference paper | ✅ drafted |
| Model card | ✅ |
| Systematic search for affected prior work | ◐ evidence gathered, **verification outstanding** |
| **Criterion weights** | ⛔ **PLACEHOLDER — no respondents** |
| Thesis §6.1–6.2 (elicitation results) | ⛔ **awaiting respondents** |
| Inter-rater reliability study | ⛔ needs officers |

### System

| Component | State |
|---|---|
| Scoring engine (TypeScript + Python) | ✅ parity-verified, 280 checks |
| Web application | ✅ intake, live scoring, explainability, audit trail |
| Authentication + role-based sign-off | ✅ clause-7 chain, enforced server-side |
| Input validation on all Server Actions | ✅ |
| Test suite | ✅ 62 tests |
| DOCX export in bank format | ✅ |
| BWM elicitation instrument + solver | ✅ |
| Deployment path (Vercel + Postgres) | ✅ documented, not executed |
| Fairness / disparate-impact assessment | ⬜ **not done — see model card §7** |
| Rate limiting, pagination, accessibility audit, CI | ⬜ |

### The blocker

Everything that can be done without people is done or in progress.
`derive_weights.py` will not mark the model `ELICITED` without usable responses,
and should not be made to. Until practitioners complete `/elicitation`:

- RQ2 is unanswered
- every score stays labelled as computed under placeholder weights

Three respondents changes that. §5.6a bounds how much the placeholders distort
results meanwhile — ranking holds to ρ ≈ 0.98 at ±25% perturbation — but 6–7% of
cases would still band differently.

### Key documents

| Path | What |
|---|---|
| `docs/06-thesis/THESIS.docx` | Assembled thesis |
| `docs/07-paper/paper-term-contamination.md` | Conference paper draft |
| `docs/07-paper/affected-work-search.md` | Systematic search — **read before citing §VIII** |
| `docs/02-literature/bibliography.md` | 50 sources, verification status per entry |
| `docs/04-criteria-model/MODEL-CARD.md` | Intended use, limitations, risks |
| `docs/VIVA-PREPARATION.md` | Likely questions with answers |
| `docs/RESEARCH-STRENGTHENING-PLAN.md` | What remains, ordered by value |
| `docs/DEPLOYMENT.md` | Vercel walkthrough |

## Rebuilding everything

```bash
python research/src/prepare_sba.py        # clean the raw dataset
python research/src/leakage_analysis.py   # the Term contamination evidence
python research/src/benchmark.py          # clean vs contaminated benchmarks
python research/src/test_parity.py        # TypeScript/Python engine agreement
python research/src/bwm.py                # BWM solver self-test
python research/src/statistical_tests.py  # CIs, DeLong tests, calibration
python research/src/weight_sensitivity.py # weight perturbation Monte Carlo
python research/src/make_figures.py       # all figures
python research/src/derive_weights.py     # weights (needs responses)
python scripts/build_thesis.py            # assemble THESIS.docx
cd web && npm test && npm run dev
```
