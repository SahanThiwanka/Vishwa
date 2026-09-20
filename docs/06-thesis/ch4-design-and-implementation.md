# Chapter 4 — Design and Implementation

## 4.1 The artefact

Following the design science paradigm, this study's primary artefact is a
decision-support system for SME credit appraisal, together with the criteria
model that underpins it. This chapter describes how a narrative appraisal
instrument was formalised into a computable model, the design decisions taken
along the way, and how each was verified.

The system is deliberately decision support, not automation. It does not approve
loans and does not replace the appraisal officer. It computes what can be
computed, structures what must be judged, and makes the resulting recommendation
traceable. The officer still decides. This positioning is not modesty: automated
credit decisioning faces regulatory constraints in most jurisdictions, and an
instrument whose value lies in encoding institutional expertise would forfeit
that value by discarding the expert.

@fig:conceptual-architecture-model sets out the whole model in one view, from
the bank's form to the report an officer signs. The sections that follow take
each stage of it in turn, and the figure is the map to read them against.

[Image: conceptual-architecture.png | conceptual-architecture-model | The model end to end. The bank's appraisal form is decomposed clause by clause into criteria; measured and judged inputs travel separate mappings into a single aggregation path governed by elicited weights; the two objectives are scored separately and never summed; and two gates stand between a score and a recommendation.]

Three features of that diagram carry most of the design argument, and each is
defended in its own section below. Quantitative and qualitative criteria are
mapped differently but aggregated identically, so a judgement and a measurement
can be combined without either being converted into the other (Section 4.4).
The two objectives run in parallel to the end and are never added together,
because a combined figure would conceal the disagreement between them (Section
4.3). And a score does not become a recommendation until it has passed the
completeness gate, because weight renormalisation otherwise lets a nearly empty
file produce a confident one (Section 4.5).

## 4.2 Formalising a narrative instrument

### 4.2.1 The source

The People's Bank *Project / Business Appraisal Report for SME Credit Facility*
(Annexure I–V) is an operational form running to seven numbered sections plus
five annexures. It is largely narrative. Clause 2.18 asks the officer to write
comments on profitability, liquidity, activity and gearing. Clause 3.10.3 asks
for a written assessment of five competitive forces. Clauses 3.11 and 3.12 ask
for prose on technological and environmental risk. Clause 7 then asks the
officer to certify that the project is "financially viable and technically
feasible", with no stated procedure for combining any of the preceding material
into that judgement.

This is the gap the artefact addresses. The form specifies *what* to consider
exhaustively and *how to weigh it* not at all.

### 4.2.2 Method

Each clause of the form was examined and classified:

- Directly computable: the thirteen ratios of clause 2.17, the debt service cover, interest service cover (ISCR) and return on investment (ROI) series of clause 4, the cost-of-project structure of clause 3.7, the working
  capital computation of Annexure II. These become quantitative criteria with
  explicit thresholds.
- Judgement, but structured: clause 3.10.3 is already Porter's five forces;
  clause 5 is already a nine-item before/after table. These decompose naturally
  into criteria scored on a linguistic scale.
- Judgement, unstructured: management style (3.2), technological risk (3.11).
  These become single qualitative criteria.
- Administrative: addresses, registration numbers, signature blocks. These
  are captured by the system but carry no score.

The rule applied throughout: no criterion exists without a source clause. Every
entry in the resulting model carries a *ref* field naming the clause it derives
from. This constraint is what makes the model auditable, since any score can be
traced to the institutional document that authorises it, and it prevents the
common failure of a scoring model quietly acquiring criteria its users never
agreed to.

### 4.2.3 The derived criteria model

The derivation produced forty-nine criteria across seven dimensions and two
objectives. @tbl:criterion-counts-source-clauses gives the count for each
dimension together with the clauses of the form it derives from. Six of the
seven dimensions belong to credit risk; the seventh carries the whole of the
development-impact objective, an asymmetry inherited from the source document
that Section 5.16.3 shows to have consequences for weighting.

[Table: criterion-counts-source-clauses | Criterion counts and source clauses by dimension]

| Objective | Dimension | Criteria | Form clauses |
|---|---|---:|---|
| Credit Risk | Borrower & Management Capacity | 6 | 2.8, 2.10, 3.2, 3.4 |
| | Credit History & Banking Conduct | 5 | 2.11, 2.14 |
| | Historic Financial Performance | 9 | 2.13, 2.15–2.18 |
| | Project Viability & Projections | 8 | 3.1.3, 3.7, 4 |
| | Market & Competitive Position | 7 | 3.10 |
| | Risk, Security & Compliance | 6 | 3.3, 3.5, 3.6, 3.11, 3.12, 6.5 |
| Development Impact | Economic & Social Contribution | 8 | 5, 3.4.1 |
| Total | 7 dimensions | 49 | |

Twenty-eight criteria are quantitative and twenty-one qualitative. The model is
held in a single machine-readable file as the single source of truth,
consumed by both the web application and the analysis pipeline.

## 4.3 The dual-objective structure

### 4.3.1 Rationale

Clause 5 of the form, *Economic Consideration*, scores nine before/after
outcomes: manpower, women's participation, local raw material usage, productive
capacity, production, export sales, import substitution, value added, and
foreign exchange earnings. Clause 3.4.1 separately disaggregates employment by
gender.

These are not credit risk. A project can employ many people, substitute imports
and earn foreign exchange while still being a poor credit; the reverse also
holds. People's Bank is a state bank with a development mandate, and its
appraisal form reflects that it is being asked to serve two objectives at once.

Mainstream credit scoring optimises a single objective: the probability of
repayment. Applying that framing here would mean discarding clause 5 entirely,
deleting the developmental half of the institution's own mandate because it does
not fit the model.

### 4.3.2 Design decision

The model therefore carries two objectives and reports them separately. They are
never combined into a single number.

This is enforced in the engine, not left to convention: a result record holds
an array of objective results, and no code path produces an overall score. The
interface presents them side by side; the exported report presents them as
distinct sections with an explicit note that the trade-off is a matter for the
approving authority.

The reason is that a weighted combination would destroy the information the
structure exists to expose. A facility scoring 80 on credit and 40 on
development and one scoring 60 on both are materially different propositions,
and a combined score of 60 would render them identical. Making the divergence
visible is the contribution; resolving it is a policy question that belongs to
the bank, not to the model.

Verification of this behaviour appears in the test case of Section 4.9: the same
application scored 80.2 on credit risk (band A) and 74.6 on development impact
(band B).

## 4.4 Scoring method

### 4.4.1 Quantitative criteria

Each quantitative criterion carries a set of (raw value, score) anchors
defining a piecewise-linear map onto 0–100. A DSCR of 0.8, for example, scores 0; 1.0 scores 25; 1.25 scores 50; 1.5 scores 75; and 2.0 scores 100. Values outside the anchor range clamp to the nearest
endpoint.

Because interpolation simply follows the anchor sequence, a single
implementation serves higher-is-better, lower-is-better and band-optimal
criteria alike. Current ratio uses the third form: it peaks at 2.0 and declines
above it, since a ratio of
8.0 signals idle working capital rather than strength.

### 4.4.2 Qualitative criteria

Qualitative criteria are captured on a five-point linguistic scale of Very Poor,
Poor, Fair, Good and Excellent, represented as the triangular fuzzy numbers in @tbl:five-point-linguistic-scale.

[Table: five-point-linguistic-scale | Five-point linguistic scale and its triangular fuzzy numbers]

| Code | Label | Triangular fuzzy number |
|---|---|---|
| VP | Very Poor | [0, 0, 25] |
| P | Poor | [0, 25, 50] |
| F | Fair | [25, 50, 75] |
| G | Good | [50, 75, 100] |
| E | Excellent | [75, 100, 100] |

@fig:appraisal-form-live-scoring shows the scale as the officer meets it, in
one dimension of a file part-way through entry. Both criterion types appear
together: a quantitative one, where twelve years of sponsor experience maps to
85, and four qualitative ones on the five-point scale, where Good maps to 75.
Two criteria are unassessed, and their scores read as a dash. The dimension
scores 78.7 at 50% assessed, computed over what has been entered and not over
what has not.

[Image: system-appraisal-form.jpg | appraisal-form-live-scoring | One dimension of an appraisal during entry. Each criterion carries the clause of the People's Bank form it derives from. Quantitative criteria take a value, qualitative criteria a point on the five-point scale, and unassessed criteria show a dash instead of a zero.]

Fuzzy representation is used because appraisal judgements are linguistic and
imprecise. An officer writing "management is sound" is not asserting 75.0; the
triangular number carries that imprecision explicitly instead of discarding it.

Quantitative values enter as degenerate triangular fuzzy numbers (TFNs) of the
form [*x*, *x*, *x*], so both criterion types
flow through one aggregation path. Aggregation is the fuzzy weighted average;
defuzzification is by centroid, which for a TFN reduces to the mean of its three
points.

### 4.4.3 Missing criteria

A criterion left unassessed is excluded and the remaining weights renormalised,
never treated as zero. Scoring an incomplete file as though the missing sections
had scored nothing would misrepresent an unfinished appraisal as a bad one.

This choice creates a hazard addressed in Section 4.5.

### 4.4.4 Critical criteria

DSCR below 1.0 means projected cash flow does not cover debt service. Under most
credit policies this is a knock-out, not a factor to be averaged.

The engine evaluates critical breaches against the raw value, not the derived
score, and surfaces them as a separate list on the result. A weighted average
cannot dilute them, and the interface displays them above the scores, not within
them.

## 4.5 The completeness gate

### 4.5.1 A problem found by testing

During verification, an appraisal with only seven of forty-nine criteria
entered, 14% complete, returned a credit risk score of 73.7 and the
recommendation *"Band B: recommend with conditions."*

The arithmetic was correct. Weight renormalisation (Section 4.4.3) had worked
exactly as designed: the seven entered criteria carried the full weight, and
they happened to score well. But the system was confidently recommending a
facility on almost no information, and nothing in the output signalled that.

This is a genuine hazard of renormalisation, and it is not specific to this
implementation. A sparse appraisal produces a plausible score while its
evidential basis collapses, and the score itself gives no indication of the
difference.

### 4.5.2 Response

An objective assessed below a completeness threshold (0.6) returns its score but
no risk band and no recommendation. The result carries a *sufficient* flag and a
list of outstanding criteria, and the interface tells the officer what is
missing instead of offering a number to sign against.

@fig:completeness-gate-refusal shows the gate holding. Credit risk stands at
78.7, which on a complete file would be a comfortable Band B, and the system
declines to say so: 7% of the objective has been assessed against the 60%
required. The number is still shown, because hiding it would be its own kind of
dishonesty, but no band and no recommendation accompany it.

[Image: system-completeness-gate.jpg | completeness-gate-refusal | The completeness gate refusing to recommend. A credit-risk score of 78.7 is displayed, and withheld from banding, because only 7% of the objective has been assessed.]

The gate is deliberately a refusal to answer, not a scoring adjustment.
Discounting the score for incompleteness would have preserved the false
impression that the system had an opinion. It does not; it has insufficient
information, and saying so is the correct output.

## 4.6 System architecture

@tbl:system-architecture-layer-reason lists the technology used at each layer
and the reason it was chosen. The pattern throughout is that the scoring engine
runs where the officer is, so that a score changes as a figure is typed, while
anything that must not be tampered with runs on the server.

[Table: system-architecture-layer-reason | System architecture by layer, with the reason for each choice]

| Layer | Technology | Rationale |
|---|---|---|
| Interface | Next.js 16, React 19, TypeScript, Tailwind 4 | Engine runs client-side for live scoring |
| Persistence | Prisma 7, SQLite | No external services; one config change to PostgreSQL |
| Analysis | Python, pandas, scikit-learn, SciPy | No TypeScript equivalent for the empirical work |
| Model | A single machine-readable criteria file | Single source of truth for both stacks |

The two stacks never communicate at runtime. The Python pipeline calibrates and
validates, exporting weights as JSON; the web application consumes that JSON.
The handoff is one-directional and inspectable.

The scoring engine is implemented twice, TypeScript for the product and Python
for the analysis, which is a deliberate risk. Divergence between them would mean
the thesis reporting numbers from one implementation while demonstrating a
system running the other. Both read the same criteria file, and the arithmetic
is verified against shared expectations.

### 4.6.1 Reproducibility of stored appraisals

An appraisal stores its inputs, its complete result document, and the model
version that produced it, not merely a score column.

The criteria tree changes over time: elicitation replaced the placeholder
weights, and bands may be revised. Without versioned storage, every historical
recommendation would silently re-interpret under the current model, and an
appraisal signed in March could not be explained in September. Storing the
result document makes past decisions permanently reconstructible.

### 4.6.2 Deployment

The system was deployed to a public URL on the Vercel platform, with the
SQLite development database replaced by a managed PostgreSQL instance. Nothing
in the application changed: the persistence layer selects its driver from the
connection string, so the same build runs against either.

Deployment was not a presentation exercise. The elicitation instrument had to
reach practitioners who would complete it on a phone, in their own time, from a
link in a message, and who would not install anything or create an account to
do so. Section 6.1 reports ten completed responses; a locally-hosted instrument
would have obtained none of them. The deployment is therefore part of the
method, and it is what made the answer to RQ2 possible.

Two consequences follow for the artefact. First, the serverless execution model
means a request may reach a process that has just started, so the connection
pool is kept small and connections are retired quickly. Second, the platform's
filesystem does not persist between invocations, which is why the file-backed
database that serves local demonstration cannot serve the deployment, and why
the driver is selected rather than assumed.

## 4.6a Access control and the integrity of the audit trail

An audit trail is only worth as much as the identity behind each entry.

An earlier iteration of the sign-off panel accepted a typed name. It recorded
who *claimed* to have signed, which is no record at all: anyone could enter any
name, and the trail would look complete while proving nothing. The system now
authenticates users and takes the signatory from the session.

Roles map directly onto the sign-off chain in clause 7 of the form, as @tbl:application-roles-permitted-actions sets out.

[Table: application-roles-permitted-actions | Application roles and permitted actions, against clause 7 of the form]

| Role | Permitted |
|---|---|
| Officer | prepare an appraisal |
| Recommender | endorse |
| Head office | approve or decline |
| Administrator | all of the above, plus user administration |

Three properties are enforced rather than merely displayed. The interface offers
only the actions a user's role permits; the server re-checks the role before
writing, so the restriction cannot be bypassed by calling the action directly;
and an appraisal that has been approved or declined rejects further decisions; a
correction is made by raising a new appraisal, never by rewriting a signed one.

@fig:system-sign-in shows the sign-in screen. It states on its face that the
weighting study needs no account, so a practitioner who follows the study link
and lands here by accident is not left thinking they must register to take part.

[Image: system-signin.png | system-sign-in | The sign-in screen. Appraisal records are restricted; the screen states that the criterion weighting study is not, so a practitioner arriving by mistake is told immediately that no account is needed.]

**The elicitation instrument is deliberately left public.** Requiring accounts
of practitioners completing a fifteen-minute voluntary study would collapse the
response rate, and the instrument collects no name and no customer data, so
there is nothing behind it to protect. The research instrument and the
operational system have different threat models and are treated differently.

### 4.6a.1 What this is not

Session cookies are HMAC-signed and passwords are hashed with scrypt, with no
external authentication dependency, so the system runs without network access
for demonstration purposes. It is not a production authentication system: there
is no password reset, no multi-factor authentication, no account lockout, no
rate limiting on sign-in attempts, and no password policy. A banking deployment
would require all of these, along with penetration testing and an accessibility
audit. These are recorded as limitations, not presented as complete.

## 4.7 Explainability

Each criterion's contribution is computed as its normalised weight times its
score, expressed in points of the parent's score. Contributions sum exactly to
the parent score, which is what makes the breakdown a decomposition rather than
a decoration.

The interface presents, for each dimension: its score, its contribution to the
objective, its completeness, and a table of constituent criteria showing raw
value, derived score and contribution, each labelled with its source clause. An
officer can therefore trace any recommendation from the headline score down to
the clause of the bank's own form that produced it.

@fig:completed-appraisal-result shows a completed appraisal. The two objectives
are reported side by side and are never added together: the same facility scores
68.0 on credit risk, which bands B and carries a recommendation with conditions,
and 26.0 on development impact, which bands D and carries a recommendation to
decline. A single combined figure would have averaged those into a middling
number that describes neither.

[Image: system-result.jpg | completed-appraisal-result | A completed appraisal. The two objectives are scored and banded separately and are never combined. Each dimension's contribution is expressed in points of the objective score, and each criterion shows its entered value, its derived score, its contribution and the clause it comes from.]

Beneath the two objective scores, each dimension's contribution is given in
points of the objective score, and every criterion shows the value entered, the
score it mapped to, and the points it contributed. Borrower and management
capacity scores 94.4 and contributes 15.7 points; project viability scores 47.0
and contributes 7.8. The contributions sum to the objective score exactly, so
the breakdown accounts for the whole of it and not merely for the part that is
convenient to explain.

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

The engine carries a structural test suite covering
three cases: a sound manufacturing expansion, a thin startup with a DSCR
breach, and a deliberately incomplete file. @tbl:behavioural-tests-scoring-engine
lists the properties asserted and the result of each.

The suite covers the scoring engine, the validation schemas and the
authorisation logic, 62 tests in total. Server Actions are reachable by direct
POST, not only through the application's own forms, so every action validates
its input before use, and validation failures report which field failed without
echoing the submitted value back.

[Table: behavioural-tests-scoring-engine | Behavioural tests of the scoring engine and their outcomes]

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
| Weight status correctly reflects the elicitation state | pass |

The system was additionally verified end to end through the browser: all 49
criteria entered through the interface, producing credit risk 80.2 (band A)
against development impact 74.6 (band B), persisted to the database, rendered
with full contribution breakdown, and exported to a valid Word in bank
format.

These are structural checks. They establish that the engine behaves as
specified, not that its scores are accurate. Accuracy is the subject of Chapter
5, and the answer given there is heavily qualified.

## 4.10 Status of the weights

The model now carries an elicited state, recording eleven respondents, three
level-responses excluded for inconsistency, and the date. Section 6.1 reports
the elicitation; the weights themselves are in Section 6.1.4.

The state is machine-enforced rather than merely documented, and that mattered.
While elicitation was outstanding the model carried the placeholder state, all
criteria equally weighted within their level. The synchronisation script warned
on every run, the interface displayed a standing notice, and the
weight-derivation pipeline refused to mark the model elicited without usable
responses. A claim check also fails the build if any chapter still describes the
weights as placeholders once the model says otherwise, which is how the stale
passages in this chapter were caught when elicitation completed.

The design principle is worth stating separately from this instance: a
placeholder that is only described in prose will outlive the condition it
describes, because nothing breaks when the condition changes.
