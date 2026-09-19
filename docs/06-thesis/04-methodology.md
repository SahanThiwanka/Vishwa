# 4 METHODOLOGY

## 4.1 Research design

This study follows Design Science Research [34]: knowledge is
produced by building an artefact and evaluating it, not by testing hypotheses
about existing phenomena. The process follows the six activities set out by
Peffers et al. [35]: problem identification, objectives, design and
development, demonstration, evaluation, and communication. The artefact is a
dual-objective decision-support system for SME credit appraisal, together with
the criteria model beneath it.

Five activities make up the design. @tbl:research-activities-questions-they sets each against the research question it addresses, the method used, and where its output is reported.

[Table: research-activities-questions-they | Research activities, the questions they address and their outputs]

| Activity | Addresses | Method | Output |
|---|---|---|---|
| Formalisation | RQ1 | Clause-by-clause derivation from the bank's form | 49-criterion model, working system |
| Weight elicitation | RQ2 | Best-Worst Method with ten practitioners | Section 6.1 |
| Weight sensitivity | RQ2 | Monte Carlo over perturbed weight vectors | Section 5.16 |
| Empirical validation | RQ3 | Benchmarking against realised outcomes, with confidence intervals (CIs) and paired tests | Sections 5.3 to 5.6 |
| Objective separability | RQ4 | Correlation and band agreement across 652,284 facilities | Section 5.17 |

Weight elicitation by Best-Worst Method is specified in Section 4.5 and was
carried out; Section 6.1 reports the respondents, the consistency screening and
the resulting weights.

## 4.2 Research questions

The questions were revised from the original proposal after the literature
review established that the initially claimed contribution was already published
(Section 3.5.3). The revised set:

- RQ1: How can the narrative, multi-section appraisal instrument used by a
  Sri Lankan state bank be formalised into a computable multi-criteria model
  without discarding the judgement it encodes?
- RQ2: What criterion weights do experienced credit practitioners assign to the criteria, and how far does the model's output depend on them?
- RQ3: What can and cannot be established about an instrument-specific
  appraisal model from publicly available credit data, and how does it compare
  with standard credit-scoring benchmarks?
- RQ4: Are credit risk and development impact separable objectives in
  practice, and what would a combined score conceal?

## 4.3 Formalisation method (RQ1)

The source instrument is the People's Bank *Project / Business Appraisal Report
for SME Credit Facility* (Annexure I–V), an operational form in current use.

Each clause was classified as directly computable, structured judgement,
unstructured judgement, or administrative, and criteria were derived accordingly
(Section 4.10.2). One constraint governed the process:

> **No criterion may exist without a source clause.**

Every criterion in the model records the clause it derives from. This is not
documentation added afterwards; it is a constraint that shaped which criteria
were admitted. Its purpose is twofold. It makes any score auditable back to the
institutional document that authorises it, and it prevents the model from
acquiring criteria the institution never adopted.

The resulting model is held as a single machine-readable file consumed by both
the application and the analysis pipeline, so that no divergence between "the
model in the paper" and "the model in the system" is possible.

## 4.4 Scoring method

Quantitative criteria map to 0–100 through piecewise-linear band anchors.
Qualitative criteria are captured on a five-point linguistic scale represented
as triangular fuzzy numbers, aggregated by fuzzy weighted average and
defuzzified by centroid. Full specification in Section 4.11.

Three rules govern edge cases, each chosen deliberately:

1. Unassessed criteria are excluded and weights renormalised, never treated as zero, because an incomplete appraisal is not a bad one.
2. Below a completeness threshold, no recommendation is issued, because rule 1 alone allows a sparse file to produce a confident score (Section 5.3).
3. Critical criteria are evaluated on raw values and surfaced separately, so a
   debt service cover ratio (DSCR) below 1.0 cannot be averaged away.

## 4.5 Weight elicitation (RQ2)

### 4.5.1 Method selection

Classical pairwise AHP over this criteria tree requires 168 comparisons per
respondent. At even ten seconds each that is close to an hour of sustained
attention, and response quality degrades well before the end. Inconsistency
introduced by fatigue would make the resulting weights unusable regardless of
how carefully the instrument was designed.

The Best-Worst Method [25] requires 2n−3 comparisons per level,
reducing the instrument to 86 comparisons, roughly fifteen minutes. Because
every comparison is anchored to a fixed reference rather than a rotating
partner, BWM also tends to yield more consistent responses. The linear
formulation [26] is used, giving a unique solution.

The choice is a response to a real constraint on practitioner time, not a
convenience.

### 4.5.2 Instrument

Elicitation is conducted through a web instrument forming part of the system, in
eight sections: one comparing the six credit-risk dimensions, and one for the
criteria within each of the seven dimensions.

For each section the respondent identifies the most important item, identifies
the least important, then rates the best against each other item and each item
against the worst, on the 1–9 scale.

@fig:elicitation-instrument-landing shows the screen a practitioner meets first.
It states the time the exercise takes and the number of comparisons before
asking for anything, carries the participation and confidentiality notice in
full, and collects only a self-chosen code, years of experience, institution
type and role. There is no field for a name, and none for any borrower.

[Image: system-elicitation.png | elicitation-instrument-landing | The opening screen of the weight elicitation instrument, as a practitioner receives it. The participation notice is shown before any question is asked, and the only identifier collected is a code the respondent chooses.]

Nothing on the screen asks the respondent to commit before they know what
they are agreeing to, which is the design response to a recruitment problem:
a practitioner deciding in ten seconds whether to spend fifteen minutes.

### 4.5.3 Analysis

Each response is solved as a linear programme minimising the maximum deviation
between stated ratios and derived weights, subject to weights summing to one.
The optimal deviation ξ\* divided by the consistency index for the stated
best-to-worst value gives a consistency ratio comparable across respondents and
level sizes.

**The solver is verified against an independent optimiser.** A weighting
programme that silently returns the wrong answer would corrupt every result
downstream of it, and property-based checks do not catch this: the worked
example usually used to sanity-check a BWM implementation is perfectly
consistent, so
ξ\* = 0 and the weights follow from normalisation alone. The optimiser is never
exercised, and an error would surface only on inconsistent responses, which is
every real response.

The implementation is therefore checked two further ways on deliberately
inconsistent inputs. First, the maximum deviation is recomputed directly from
the returned weights, written from the definition instead of from the
programme's constraint matrix, and must equal the reported ξ\*. Second, the same
objective is minimised by sequential least-squares from forty random starts;
because the programme is convex, no general-purpose optimiser can beat it, so a
lower value found that way would prove the formulation wrong. Across three
inconsistent cases the two agree to six decimal places, and the returned weights
exhibit exactly the deviation reported. Both checks run as part of the
solver's own test suite.

Responses with a consistency ratio (CR) above 0.25 are excluded, not averaged in. The number excluded is
reported: silently discarding respondents would make the study unreproducible.

Surviving responses are aggregated by geometric mean, the standard aggregation
for ratio-scale priority vectors, which preserves the ratio relationships that
an arithmetic mean distorts.

### 4.5.4 Sampling and its limits

Respondents are credit and appraisal practitioners recruited through
professional contact. This is purposive, non-probability sampling with a small
n, and the resulting weights represent the judgement of those respondents, not
of Sri Lankan credit practice generally. Chapter 6 reports the achieved sample
and treats this as a primary limitation.

## 4.6 Empirical validation (RQ3)

### 4.6.1 The proxy problem, stated in advance

No public dataset contains the criteria this model scores. Access to the bank's
own historical files was not available and would in any case be confidential.

Validation therefore uses the SBA National dataset as a proxy, and the resulting
claim is correspondingly narrow: it tests the scoring *machinery* on observable
financial and structural variables, not the criteria tree. This limitation is
stated in advance rather than discovered afterwards, because it determines what
Chapter 5 is entitled to conclude.

### 4.6.2 Protocol

- Outcome-derived fields are dropped and their absence asserted.
- Right-censored loans are excluded; only fully-matured facilities are analysed.
- Two validation protocols are run: random split, and temporal split (train on
  earlier cohorts, test on later). Both are reported, because random splitting
  places the same economic cycle on both sides and overstates performance.
- The unfitted expert scorecard is compared against logistic regression and
  gradient boosting [36], both trained on hundreds of thousands of labelled outcomes and fitted with scikit-learn [37].
- Metrics: area under the receiver operating characteristic (ROC) curve [38], Kolmogorov–Smirnov
  separation, average precision, the Brier score [39] under
  Murphy's decomposition [40], and F1 at the Youden-optimal threshold.
- Paired comparisons of AUC use DeLong's test [41], which accounts for the correlation induced by
  evaluating both models on identical cases.
- Interval estimates are stratified bootstrap percentile intervals [42], resampling
  positives and negatives separately.

The comparison is deliberately asymmetric. The scorecard never sees a default
label; its bands were fixed from a priori reasoning before outcomes were
inspected. The question is not whether it wins, which it will not, but how much
discrimination an unfitted, explainable, expert-structured model retains. That
ratio is what matters for institutions without clean historical default data,
which is the common situation in Sri Lankan SME lending.

### 4.6.3 Treatment of anomalous results

An unexpectedly strong result is treated as a suspected defect until explained.
This rule was applied during the study and is what produced the finding in
Section 5.10: an AUC of 0.97 was investigated rather than reported, and proved to
arise from contamination in a predictor. The rule is stated here because it is
part of the method, not a lucky accident.

## 4.7 Ethical considerations

**Human participants.** The elicitation instrument collects a self-chosen
participant code, years of experience, institution type and role. It collects no
name and no customer information. The landing page states that participation is
voluntary, may be stopped at any time, and that responses are used solely for
academic research and reported only in aggregate.

**Confidentiality of bank material.** The source appraisal form is a blank
template. No customer file, no borrower data and no internal credit policy
document was accessed. The system was demonstrated using constructed cases, not
real applications.

**Institutional approval.** Formal ethics clearance and any institutional
permission required for practitioner participation must be obtained and recorded
before elicitation data is used in the submitted work. Where this study was
conducted under time constraints that limited the scale of participant
recruitment, that constraint is reported in the limitations and not concealed by
the sample size.

**Research integrity.** Every quantitative result reported in this thesis is
produced by code in the accompanying repository and is regenerable from the raw
data. No value is entered by hand. Where an experiment could not be run, the
claim is withdrawn and the gap recorded as a limitation rather than filled with
an estimate. Negative results, including a scorecard that failed to discriminate
(Section 5.15), are reported as they occurred.

## 4.8 Limitations of the design

- The empirical validation uses a proxy dataset from a different jurisdiction;
  the qualitative criteria are not tested against outcomes at all.
- The fuzzy layer is not exercised by the validation, since all
  SBA-observable criteria are quantitative and enter as degenerate fuzzy numbers.
- Elicitation is small-n and purposive, so weights are not generalisable.
- There is no inter-rater reliability study. Establishing how much two officers
  disagree on the same file, and whether the system narrows that gap, would directly evidence the consistency claim motivating this research. It was not
  feasible within the time available and is the single most valuable extension.
- The system is evaluated for structural correctness, not field usability. No
  officer has used it on live applications.

## 4.9 The artefact

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

## 4.10 Formalising a narrative instrument

### 4.10.1 The source

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

### 4.10.2 Method

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

## 4.11 Scoring method

### 4.11.1 Quantitative criteria

Each quantitative criterion carries a set of (raw value, score) anchors
defining a piecewise-linear map onto 0–100. A DSCR of 0.8, for example, scores 0; 1.0 scores 25; 1.25 scores 50; 1.5 scores 75; and 2.0 scores 100. Values outside the anchor range clamp to the nearest
endpoint.

Because interpolation simply follows the anchor sequence, a single
implementation serves higher-is-better, lower-is-better and band-optimal
criteria alike. Current ratio uses the third form: it peaks at 2.0 and declines
above it, since a ratio of
8.0 signals idle working capital rather than strength.

### 4.11.2 Qualitative criteria

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

Fuzzy representation is used because appraisal judgements are linguistic and
imprecise. An officer writing "management is sound" is not asserting 75.0; the
triangular number carries that imprecision explicitly instead of discarding it.

Quantitative values enter as degenerate triangular fuzzy numbers (TFNs) of the
form [*x*, *x*, *x*], so both criterion types
flow through one aggregation path. Aggregation is the fuzzy weighted average;
defuzzification is by centroid, which for a TFN reduces to the mean of its three
points.

### 4.11.3 Missing criteria

A criterion left unassessed is excluded and the remaining weights renormalised,
never treated as zero. Scoring an incomplete file as though the missing sections
had scored nothing would misrepresent an unfinished appraisal as a bad one.

This choice creates a hazard addressed in Section 5.3.

### 4.11.4 Critical criteria

DSCR below 1.0 means projected cash flow does not cover debt service. Under most
credit policies this is a knock-out, not a factor to be averaged.

The engine evaluates critical breaches against the raw value, not the derived
score, and surfaces them as a separate list on the result. A weighted average
cannot dilute them, and the interface displays them above the scores, not within
them.

## 4.12 System architecture

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

### 4.12.1 Reproducibility of stored appraisals

An appraisal stores its inputs, its complete result document, and the model
version that produced it, not merely a score column.

The criteria tree changes over time: elicitation replaced the placeholder
weights, and bands may be revised. Without versioned storage, every historical
recommendation would silently re-interpret under the current model, and an
appraisal signed in March could not be explained in September. Storing the
result document makes past decisions permanently reconstructible.

### 4.12.2 Deployment

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

## 4.13 Access control and the integrity of the audit trail

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

### 4.13.1 What this is not

Session cookies are HMAC-signed and passwords are hashed with scrypt, with no
external authentication dependency, so the system runs without network access
for demonstration purposes. It is not a production authentication system: there
is no password reset, no multi-factor authentication, no account lockout, no
rate limiting on sign-in attempts, and no password policy. A banking deployment
would require all of these, along with penetration testing and an accessibility
audit. These are recorded as limitations, not presented as complete.
