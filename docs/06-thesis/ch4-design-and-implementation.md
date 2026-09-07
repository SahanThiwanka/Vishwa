# Chapter 4 — Design and Implementation

## 4.1 The artefact

Following the design science paradigm, this study's primary artefact is a
decision-support system for SME credit appraisal, together with the criteria
model that underpins it. This chapter describes how a narrative appraisal
instrument was formalised into a computable model, the design decisions taken
along the way, and how each was verified.

The system is deliberately **decision support, not automation**. It does not
approve loans and does not replace the appraisal officer. It computes what can be
computed, structures what must be judged, and makes the resulting recommendation
traceable. The officer still decides. This positioning is not modesty: automated
credit decisioning faces regulatory constraints in most jurisdictions, and an
instrument whose value lies in encoding institutional expertise would forfeit
that value by discarding the expert.

## 4.2 Formalising a narrative instrument

### 4.2.1 The source

The People's Bank *Project / Business Appraisal Report for SME Credit Facility*
(Annexure I–V) is an operational form running to seven numbered sections plus
five annexures. It is largely **narrative**. Clause 2.18 asks the officer to write
comments on profitability, liquidity, activity and gearing. Clause 3.10.3 asks for
a written assessment of five competitive forces. Clauses 3.11 and 3.12 ask for
prose on technological and environmental risk. Clause 7 then asks the officer to
certify that the project is "financially viable and technically feasible" — with
no stated procedure for combining any of the preceding material into that
judgement.

This is the gap the artefact addresses. The form specifies *what* to consider
exhaustively and *how to weigh it* not at all.

### 4.2.2 Method

Each clause of the form was examined and classified:

- **Directly computable** — the thirteen ratios of clause 2.17, the DSCR/ISCR/ROI
  series of clause 4, the cost-of-project structure of clause 3.7, the working
  capital computation of Annexure II. These become quantitative criteria with
  explicit thresholds.
- **Judgement, but structured** — clause 3.10.3 is already Porter's five forces;
  clause 5 is already a nine-item before/after table. These decompose naturally
  into criteria scored on a linguistic scale.
- **Judgement, unstructured** — management style (3.2), technological risk (3.11).
  These become single qualitative criteria.
- **Administrative** — addresses, registration numbers, signature blocks. These
  are captured by the system but carry no score.

The rule applied throughout: **no criterion exists without a source clause.**
Every entry in the resulting model carries a `ref` field naming the clause it
derives from. This constraint is what makes the model auditable — any score can be
traced to the institutional document that authorises it — and it prevents the
common failure of a scoring model quietly acquiring criteria its users never
agreed to.

### 4.2.3 Result

| Objective | Dimension | Criteria | Form clauses |
|---|---|---:|---|
| Credit Risk | Borrower & Management Capacity | 6 | 2.8, 2.10, 3.2, 3.4 |
| | Credit History & Banking Conduct | 5 | 2.11, 2.14 |
| | Historic Financial Performance | 9 | 2.13, 2.15–2.18 |
| | Project Viability & Projections | 8 | 3.1.3, 3.7, 4 |
| | Market & Competitive Position | 7 | 3.10 |
| | Risk, Security & Compliance | 6 | 3.3, 3.5, 3.6, 3.11, 3.12, 6.5 |
| Development Impact | Economic & Social Contribution | 8 | 5, 3.4.1 |
| **Total** | **7 dimensions** | **49** | |

Twenty-eight criteria are quantitative and twenty-one qualitative. The model is
held in `shared/model/criteria-tree.json` as the single source of truth, consumed
by both the web application and the analysis pipeline.

## 4.3 The dual-objective structure

### 4.3.1 Rationale

Clause 5 of the form, *Economic Consideration*, scores nine before/after outcomes:
manpower, women's participation, local raw material usage, productive capacity,
production, export sales, import substitution, value added, and foreign exchange
earnings. Clause 3.4.1 separately disaggregates employment by gender.

These are not credit risk. A project can employ many people, substitute imports
and earn foreign exchange while still being a poor credit; the reverse also holds.
People's Bank is a state bank with a development mandate, and its appraisal form
reflects that it is being asked to serve two objectives at once.

Mainstream credit scoring optimises a single objective: the probability of
repayment. Applying that framing here would mean **discarding clause 5 entirely**
— deleting the developmental half of the institution's own mandate because it does
not fit the model.

### 4.3.2 Design decision

The model therefore carries two objectives and **reports them separately. They are
never combined into a single number.**

This is enforced in the engine rather than left to convention: `AppraisalResult`
holds an array of objective results, and no code path produces an overall score.
The interface presents them side by side; the exported report presents them as
distinct sections with an explicit note that the trade-off is a matter for the
approving authority.

The reason is that a weighted combination would destroy the information the
structure exists to expose. A facility scoring 80 on credit and 40 on development
and one scoring 60 on both are materially different propositions, and a combined
score of 60 would render them identical. Making the divergence visible is the
contribution; resolving it is a policy question that belongs to the bank, not to
the model.

Verification of this behaviour appears in the test case of §4.9: the same
application scored **80.2 on credit risk (band A) and 74.6 on development impact
(band B)**.

## 4.4 Scoring method

### 4.4.1 Quantitative criteria

Each quantitative criterion carries a set of `[rawValue, score]` anchors defining
a piecewise-linear map onto 0–100. DSCR, for example, anchors at 0.8→0, 1.0→25,
1.25→50, 1.5→75, 2.0→100. Values outside the anchor range clamp to the nearest
endpoint.

Because interpolation simply follows the anchor sequence, a single implementation
serves higher-is-better, lower-is-better and band-optimal criteria alike. Current
ratio uses the third form: it peaks at 2.0 and declines above it, since a ratio of
8.0 signals idle working capital rather than strength.

### 4.4.2 Qualitative criteria

Qualitative criteria are captured on a five-point linguistic scale — Very Poor,
Poor, Fair, Good, Excellent — represented as triangular fuzzy numbers:

| Code | Label | TFN |
|---|---|---|
| VP | Very Poor | [0, 0, 25] |
| P | Poor | [0, 25, 50] |
| F | Fair | [25, 50, 75] |
| G | Good | [50, 75, 100] |
| E | Excellent | [75, 100, 100] |

Fuzzy representation is used because appraisal judgements are linguistic and
imprecise. An officer writing "management is sound" is not asserting 75.0; the
triangular number carries that imprecision explicitly rather than discarding it.

Quantitative values enter as degenerate TFNs `[x,x,x]`, so both criterion types
flow through one aggregation path. Aggregation is the fuzzy weighted average;
defuzzification is by centroid, which for a TFN reduces to the mean of its three
points.

### 4.4.3 Missing criteria

A criterion left unassessed is **excluded and the remaining weights
renormalised** — never treated as zero. Scoring an incomplete file as though the
missing sections had scored nothing would misrepresent an unfinished appraisal as
a bad one.

This choice creates a hazard addressed in §4.5.

### 4.4.4 Critical criteria

DSCR below 1.0 means projected cash flow does not cover debt service. Under most
credit policies this is a knock-out, not a factor to be averaged.

The engine evaluates critical breaches against the **raw value**, not the derived
score, and surfaces them as a separate list on the result. A weighted average
cannot dilute them, and the interface displays them above the scores rather than
within them.

## 4.5 The completeness gate

### 4.5.1 A problem found by testing

During verification, an appraisal with only seven of forty-nine criteria entered —
14% complete — returned a credit risk score of 73.7 and the recommendation *"Band
B — recommend with conditions."*

The arithmetic was correct. Weight renormalisation (§4.4.3) had worked exactly as
designed: the seven entered criteria carried the full weight, and they happened to
score well. But the system was confidently recommending a facility on almost no
information, and nothing in the output signalled that.

This is a genuine hazard of renormalisation, and it is not specific to this
implementation. **A sparse appraisal produces a plausible score while its
evidential basis collapses**, and the score itself gives no indication of the
difference.

### 4.5.2 Response

An objective assessed below a completeness threshold (0.6) returns its score but
**no risk band and no recommendation.** The result carries a `sufficient` flag and
a list of outstanding criteria, and the interface tells the officer what is
missing instead of offering a number to sign against.

The gate is deliberately a **refusal to answer, not a scoring adjustment**.
Discounting the score for incompleteness would have preserved the false
impression that the system had an opinion. It does not; it has insufficient
information, and saying so is the correct output.

## 4.6 System architecture

| Layer | Technology | Rationale |
|---|---|---|
| Interface | Next.js 16, React 19, TypeScript, Tailwind 4 | Engine runs client-side for live scoring |
| Persistence | Prisma 7, SQLite | No external services; one config change to PostgreSQL |
| Analysis | Python, pandas, scikit-learn, SciPy | No TypeScript equivalent for the empirical work |
| Model | `shared/model/criteria-tree.json` | Single source of truth for both stacks |

The two stacks never communicate at runtime. The Python pipeline calibrates and
validates, exporting weights as JSON; the web application consumes that JSON. The
handoff is one-directional and inspectable.

The scoring engine is implemented **twice** — TypeScript for the product, Python
for the analysis — which is a deliberate risk. Divergence between them would mean
the thesis reporting numbers from one implementation while demonstrating a system
running the other. Both read the same criteria file, and the arithmetic is
verified against shared expectations.

### 4.6.1 Reproducibility of stored appraisals

An appraisal stores its **inputs, its complete result document, and the model
version that produced it** — not merely a score column.

The criteria tree will change: elicitation replaces the placeholder weights, and
bands may be revised. Without versioned storage, every historical recommendation
would silently re-interpret under the current model, and an appraisal signed in
March could not be explained in September. Storing the result document makes past
decisions permanently reconstructible.

## 4.7 Explainability

Each criterion's contribution is computed as its normalised weight times its
score, expressed in points of the parent's score. **Contributions sum exactly to
the parent score**, which is what makes the breakdown a decomposition rather than
a decoration.

The interface presents, for each dimension: its score, its contribution to the
objective, its completeness, and a table of constituent criteria showing raw
value, derived score and contribution — each labelled with its source clause. An
officer can therefore trace any recommendation from the headline score down to the
clause of the bank's own form that produced it.

## 4.8 Report generation

The system exports a completed appraisal as a Word document in the People's Bank
format: Annexure I heading, clause-numbered sections, the scoring evidence, and
the clause 7 signature blocks.

This closes the loop. The officer receives back the document the institution
already uses, with no retyping and no change to the existing approval chain. A
system that produced its own report format would require the bank to adopt new
paperwork alongside new software; producing the incumbent document removes that
barrier entirely.

## 4.9 Verification

The engine carries a structural test suite (`npm run test:scoring`) covering three
cases — a sound manufacturing expansion, a thin startup with a DSCR breach, and a
deliberately incomplete file:

| Check | Result |
|---|---|
| Strong case scores above weak on credit risk | pass |
| Strong case scores above weak on development impact | pass |
| Weak case flags a critical breach (DSCR 0.92) | pass |
| Strong case flags no breach | pass |
| Strong case reaches band A or B | pass |
| Weak case falls to band C or D | pass |
| Objectives reported separately, not merged | pass |
| Contributions sum to parent score | pass |
| Weight status still flagged PLACEHOLDER | pass |

The system was additionally verified end to end through the browser: all 49
criteria entered through the interface, producing credit risk 80.2 (band A)
against development impact 74.6 (band B), persisted to the database, rendered with
full contribution breakdown, and exported to a valid `.docx` in bank format.

These are **structural** checks. They establish that the engine behaves as
specified — not that its scores are accurate. Accuracy is the subject of
Chapter 5, and the answer given there is heavily qualified.

## 4.10 Status of the weights

Throughout this chapter the model carries `weightStatus: PLACEHOLDER`. All
criteria are equally weighted within their level.

This is enforced rather than merely noted. The model synchronisation script warns
on every run; the interface displays a standing notice; and the weight-derivation
pipeline refuses to mark the model `ELICITED` without usable elicitation
responses. Scores computed under placeholder weights are structurally valid and
**must not be reported as research results**. Chapter 6 describes the elicitation
that replaces them.
