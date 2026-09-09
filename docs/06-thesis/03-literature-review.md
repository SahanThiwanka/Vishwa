# 3 LITERATURE REVIEW

## 3.1 Scope and structure

This review covers six bodies of work bearing on the research questions:

1. the statistical lineage of credit scoring, and what discrimination it achieves;
2. SME finance specifically, and why SMEs are harder to appraise than consumers;
3. variability in human credit judgement — the premise this study rests on;
4. multi-criteria decision methods, and their application to credit;
5. non-financial objectives in lending;
6. data quality and reproducibility in machine-learning-based science.

It closes (§3.8) by stating what this study adds — which, after examining the
literature, is narrower than the research proposal supposed.

## 3.2 Credit scoring: sixty years of weighted ratios

Quantitative credit assessment begins with Altman [2], who applied multiple
discriminant analysis to twenty-two financial ratios across sixty-six firms to
produce the Z-score. Ohlson [3] replaced discriminant analysis with conditional
logit, shifting the output from a classification to a probability — a change that
matters here, because a probability can be checked for *calibration* while a class
label cannot (§5.12).

Hand and Henley [4] reviewed the statistical methods then in use, and Thomas,
Crook and Edelman [5] and Thomas, Edelman and Crook [6] provided the
standard textbook treatments. The most useful modern reference point is Lessmann et al.
[7], who benchmarked forty-one classifiers across eight credit datasets and
found ensemble methods consistently ahead.

**Two implications for this study.** First, the core idea here — combining
weighted financial ratios into a score — is a sixty-year-old one, and any novelty
claim must rest elsewhere. Second, Lessmann et al. establish what discrimination
is realistically achievable on credit data, which is precisely the yardstick that
made the anomalous result in Chapter 5 recognisable as anomalous.

## 3.3 SME credit assessment

SMEs are harder than consumer credit. Financial statements are frequently
unaudited or absent, trading histories are short, and collateral is thin. Beck and
Demirgüç-Kunt [8] establish access to finance as a binding growth constraint
for SMEs internationally.

Berger and Udell [9] provide the framework this study sits inside. They
identify nine distinct SME lending technologies — relationship lending, financial
statement lending, trade credit, equipment lending, real-estate-based lending,
leasing, factoring, small business credit scoring, and asset-based lending — and
argue that credit availability depends on which are feasible in a given
institutional setting. **The People's Bank instrument is principally financial
statement lending with substantial relationship and asset-based elements**, and
this study adds a scoring layer without discarding the relationship content.

Stein [10] explains why that is difficult. He distinguishes *hard* information,
which can be credibly transmitted through a hierarchy, from *soft* information,
which cannot, and shows that decentralised structures outperform where information
is soft. An appraisal officer's judgement about management quality is soft
information in exactly this sense.

> **This is the central tension of the present study.** Formalising narrative
> appraisal is an attempt to *harden* soft information. Stein's analysis implies
> something is necessarily lost in that transformation. The design response — a
> five-point linguistic scale represented as fuzzy numbers rather than a forced
> crisp value (§4.11.2) — is an attempt to lose less, not to avoid the loss.

Ciampi, Giannozzi, Marzi and Altman [11] provide the anchoring review: a
systematic analysis of over a hundred articles on SME default prediction across
thirty-four years, identifying five research streams and calling for work
exploiting new data sources.

Sri Lanka is documented as finance-constrained. Reported supply-side barriers
include absent formal records, insufficient tangible collateral, non-submission of
financial statements and limited management capacity, with policy responses
proposed around SME credit rating and credit guarantee schemes. This establishes
the practical motivation but does not address the appraisal *process*, which is
where this study is situated.

## 3.4 Variability in human credit judgement

This study is premised on manual appraisal being inconsistent. That premise should
not rest on assertion, and it does not have to.

Cortés, Duchin and Sosyura [1] provide causal evidence. Using daily variation
in local sunshine as an instrument for sentiment, they show that the mood of
lower-level financial officers affects day-to-day credit decisions: positive
sentiment raises approval rates, negative sentiment lowers them by a larger
magnitude, and the resulting variation affects subsequent financial performance
and produces real effects. Officers are measurably influenced by something with no
bearing whatever on the borrower.

Two features matter here. The effects are **stronger where decisions require more
discretion and reviews are less automated** — which describes the People's Bank
instrument precisely, since clause 7 asks for a viability judgement with no stated
procedure for reaching it. And the mechanism is ordinary human variability rather
than incompetence, which is why the response pursued here is to *structure* the
judgement rather than remove the officer.

Related work reaches similar conclusions from other directions: studies of
discretion in loan rate setting, and of loan officers' subjective judgement in
microfinance, where risk classification rests on recollected professional
experience rather than an explicit model. SharafEldin, Idrees and Ouf [12]
similarly motivate their work by observing that traditional credit assessment
"often relied on subjective judgment, leading to inconsistent decisions".

The premise is therefore supported by the literature. This study does **not**
itself measure inter-rater reliability, which remains its most significant gap
(§6.3); Cohen [13], Landis and Koch [14] and Krippendorff's α provide the
instruments a proper measurement would use.

## 3.5 Multi-criteria decision methods

### 3.5.1 Foundations

Zadeh [15] introduced fuzzy sets, providing a representation for gradations of
membership rather than binary classification. Saaty [16] introduced the
Analytic Hierarchy Process, later defending it against criticism [17], deriving priority weights from pairwise comparisons on
a 1–9 scale — still the most widely used weighting method.

Fuzzy extensions followed. Chang [18] proposed extent analysis for fuzzy AHP,
and Chen [19] extended TOPSIS to fuzzy group decision-making with linguistic
ratings.

**A caution that shaped this study's method choice.** Chang's extent analysis is
very widely used, but subsequent work shows it *cannot recover true weights* from
a fuzzy comparison matrix and has produced a considerable number of
misapplications. Adopting it uncritically would have been the path of least
resistance; it is also documented to be wrong.

### 3.5.2 Best-Worst Method

Rezaei [20] introduced the Best-Worst Method, which derives weights from two
comparison vectors — the best criterion against all others, and all others against
the worst — requiring 2n−3 comparisons rather than AHP's n(n−1)/2. Anchoring every
comparison to a fixed reference tends to produce more consistent responses.
Rezaei [21] gave a linear formulation with a unique solution, which is the form
implemented here (§4.5).

For this study's criteria tree the difference is decisive: **168 comparisons under
pairwise AHP against 86 under BWM** (§4.5.1). That is the difference between an
hour of a practitioner's attention and fifteen minutes, and therefore between
usable and unusable responses.

### 3.5.3 Application to credit — and the nearest precedent

**Roy and Shaw [22] must be acknowledged plainly.** They construct a
multicriteria credit scoring model for SMEs using exactly the hybrid this study's
proposal treated as novel: BWM to determine criteria weights, combined with a
ranking method (TOPSIS) to score applicants. They report credit history, cash
liquidity and repayment period as dominant criteria.

The implication is direct: **applying BWM to SME credit scoring is not novel.** An
earlier draft of this research claimed the fuzzy-MCDM combination as its
methodological contribution. The literature does not support that claim, and it is
withdrawn here.

Related work populates the space further: fuzzy BWM with fuzzy TOPSIS for
sustainable credit scoring, fuzzy-BWM with TOPSIS-Sort-C for credit rating, fuzzy
decision support systems for credit scoring, and fuzzy AHP combined with neural
approaches for SME credit risk assessment. The method space is well occupied.

What remains open is not the method but its **object**: no located study
formalises a *specific, named, operational appraisal instrument* of a state bank,
with every criterion traceable to a numbered clause of that institution's own
document.

## 3.6 Non-financial objectives in lending

### 3.6.1 Social criteria in credit scoring

Gutiérrez-Nieto, Serrano-Cinca and Camón-Cala [23] build a credit score system
for socially responsible lending that evaluates social alongside financial
aspects, quantifying a loan's impact on outcomes such as employment, education,
environment and health, and using MCDM to combine them. Their system yields not
only a score but an account of an application's strengths and weaknesses.

This narrows the novelty claim again: **scoring social impact alongside credit
risk has been done.** The difference here is institutional grounding — the
development criteria in this study are not selected by the researcher from a
development framework, but taken from clause 5 of an instrument a state bank
already uses in production.

### 3.6.2 Development returns and credit risk

Arvanitis, Stampini and Vencatachellum [24] examine ex-ante appraisal at the
African Development Bank, and their result is the closest thing in the literature
to a test of whether the two objectives need to be reported separately. They
conclude that the variables weighed at appraisal, "whether they pertain to
development or risk concerns, are rather independent from each other and no
assumption should be made on one variable given information on the others".

**What that conclusion rests on has to be stated precisely, because it is weaker
than the wording suggests.** Comparing development outcome ratings against credit
risk ratings for the 109 operations that carried both, they find a *positive but
statistically non-significant* relationship — a slope of 0.048 with a p-value of
0.49 — and read it as showing the two factors to be "somewhat independent". A
non-significant association in 109 observations is an absence of evidence, not
evidence of absence: a sample that size cannot detect a moderate correlation, so
the finding is consistent both with genuine independence and with a real
association the study was underpowered to see. Their measured association is
positive, which is worth carrying forward.

The distinction matters for how the design decision in Chapter 4 is justified.
The strong reading — that the objectives are independent, so aggregating them
destroys information — is not available on this evidence. The weaker and
defensible reading is that no one has shown the two can be inferred from each
other, and that a bank with a development mandate therefore has no warrant for
collapsing them into one number. §5.17 tests the association directly on a sample
large enough to resolve it.

## 3.7 Explainability, regulation, and data quality

### 3.7.1 Why explanation is not optional

Explainability in credit is a legal requirement, not a design preference. Under
the U.S. Equal Credit Opportunity Act and Regulation B, creditors must state the
specific principal reasons for adverse action; regulatory guidance holds that a
creditor cannot excuse non-compliance on the grounds that its technology is too
complex to interpret, nor satisfy the requirement by citing broad categories.
Credit scoring is designated high-risk under the EU AI Act.

The technical response has been post-hoc explanation: LIME [25] fits an interpretable local surrogate around a prediction, and
SHAP [26] assigns each feature a Shapley-value contribution
with uniqueness guarantees.

**This study takes a different route, and the distinction is worth stating.**
LIME and SHAP explain an opaque model after the fact. The model here is additive
by construction, so per-criterion contributions are exact rather than
approximated, and they sum precisely to the score (§5.4). That is a stronger
guarantee than a post-hoc method can offer — at the cost of the discrimination a
flexible model might achieve, which Chapter 5 shows to be a real cost.

### 3.7.2 Leakage and reproducibility

Kapoor and Narayanan [27] surveyed machine-learning-based science across
seventeen fields and found leakage affecting **294 papers**, in some cases
producing wildly overoptimistic conclusions. They argue leakage is the single
largest cause of irreproducibility in the area, and set out a taxonomy of eight
types ranging from textbook errors to open research problems.

This is the frame within which Chapter 5's finding sits: not a curiosity peculiar
to one dataset, but an instance of a documented, recurring failure.

### 3.7.3 The SBA National dataset

Li, Mickel and Taylor [28] introduced the SBA National dataset — 899,164 loan
guarantees, 1987–2014, with realised outcomes — as a teaching resource for
statistics as investigative decision-making. It has since become a widely used
benchmark in small-business credit research.

The searched literature reports `Term`, disbursement and approval amounts as
significant predictors, and uses them accordingly. The dataset codebook documents
`Term` as "loan term in months" — the contractual term, legitimately available at
appraisal time.

**No located source reports that the field itself carries outcome information.**
Chapter 5 presents evidence that it does. This is stated as a finding the author
has not found documented elsewhere, which is weaker than a claim of priority and
is the appropriate claim given a non-exhaustive search.

## 3.8 Research gap

Consolidating, the following are **not** contributions of this study, contrary to
the original proposal:

- combining weighted financial ratios into a credit score ([2], and
  sixty years of work after it);
- applying BWM or fuzzy MCDM to SME credit scoring ([22], and the
  surrounding literature in §3.5.3);
- scoring social or developmental impact alongside credit risk [23];
- observing that development banks appraise against two objectives [24].

What the literature leaves open, and what this study addresses:

1. **Contamination in a widely used benchmark dataset** (Chapter 5), and the
   consequent methodological point that instrument-specific models cannot be
   validated on datasets lacking their variables. Situated within Kapoor and
   Narayanan's taxonomy but, on the searched literature, unreported for this
   dataset.
2. **Formalising a specific operational instrument.** Existing models select
   criteria from theory or from researcher judgement. None located takes a named
   state bank's production appraisal form and derives a computable model from it
   clause by clause, with traceability maintained as a design constraint.
3. **Keeping dual objectives unaggregated.** Prior dual-objective systems combine
   social and financial scores. This study reports them separately by design and
   never produces a combined figure, and — unlike the prior work — tests whether
   the separation is warranted rather than assuming it (§5.17).
4. **The Sri Lankan state-bank context**, documented as finance-constrained but
   not studied at the level of appraisal process.

Contribution 1 is the substantial one and the most transferable. Contributions 2
to 4 are real but incremental, and are stated as such throughout.

---
