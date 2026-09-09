# Chapter 2 — Literature Review

> **Verification note for the author.** Every source cited here was located
> through a literature search and its bibliographic details checked against an
> authoritative record. That is **not** the same as having read it. Before
> submission, obtain and read every source cited for a substantive claim — the
> priority order is in `docs/02-literature/bibliography.md`. Where this chapter
> says a claim is "not found in the searched literature", that is a statement
> about a non-exhaustive search, not a claim of priority.

## 2.1 Scope and structure

This review covers six bodies of work bearing on the research questions:

1. the statistical lineage of credit scoring, and what discrimination it achieves;
2. SME finance specifically, and why SMEs are harder to appraise than consumers;
3. variability in human credit judgement — the premise this study rests on;
4. multi-criteria decision methods, and their application to credit;
5. non-financial objectives in lending;
6. data quality and reproducibility in machine-learning-based science.

It closes (§2.8) by stating what this study adds — which, after examining the
literature, is narrower than the research proposal supposed.

## 2.2 Credit scoring: sixty years of weighted ratios

Quantitative credit assessment begins with Altman (1968), who applied multiple
discriminant analysis to twenty-two financial ratios across sixty-six firms to
produce the Z-score. Ohlson (1980) replaced discriminant analysis with conditional
logit, shifting the output from a classification to a probability — a change that
matters here, because a probability can be checked for *calibration* while a class
label cannot (§5.5).

Hand and Henley (1997) reviewed the statistical methods then in use, and Thomas,
Crook and Edelman (1992) and Thomas, Edelman and Crook (2002) provided the
standard textbook treatments. The most useful modern reference point is Lessmann et al.
(2015), who benchmarked **forty-one classifiers across seven** real-world retail
credit scoring datasets, updating Baesens et al. (2003). They report a *tendency*
for homogeneous ensembles to outperform individual classifiers — the five best
methods all belong to that family, with random forest giving the most accurate
probability-of-default estimates — but the picture is not uniform, and they note
that several sophisticated techniques, including rotation forests and dynamic
ensemble selection, predict less accurately than plain logistic regression.

**Two implications for this study.** First, the core idea here — combining
weighted financial ratios into a score — is a sixty-year-old one, and any novelty
claim must rest elsewhere. Second, Lessmann et al. establish what discrimination
is realistically achievable on credit data, which is the yardstick that made the
anomalous result in Chapter 5 recognisable as anomalous — with the caveat that
their datasets are **retail** credit, not SME lending, so they bound expectations
by analogy rather than directly.

## 2.3 SME credit assessment

SMEs are harder than consumer credit. Financial statements are frequently
unaudited or absent, trading histories are short, and collateral is thin. Beck and
Demirgüç-Kunt (2006) is the standard reference for access to finance as a binding
growth constraint on SMEs internationally.

Berger and Udell (2006) provide the framework this study sits inside. They
identify nine distinct SME lending technologies — relationship lending, financial
statement lending, trade credit, equipment lending, real-estate-based lending,
leasing, factoring, small business credit scoring, and asset-based lending — and
argue that credit availability depends on which are feasible in a given
institutional setting. **The People's Bank instrument is principally financial
statement lending with substantial relationship and asset-based elements**, and
this study adds a scoring layer without discarding the relationship content.

Stein (2002) explains why that is difficult. He distinguishes *hard* information,
which can be credibly transmitted through a hierarchy, from *soft* information,
which cannot, and shows that decentralised structures outperform where information
is soft. An appraisal officer's judgement about management quality is soft
information in exactly this sense.

> **This is the central tension of the present study.** Formalising narrative
> appraisal is an attempt to *harden* soft information. Stein's analysis implies
> something is necessarily lost in that transformation. The design response — a
> five-point linguistic scale represented as fuzzy numbers rather than a forced
> crisp value (§4.4.2) — is an attempt to lose less, not to avoid the loss.

Ciampi, Giannozzi, Marzi and Altman (2021) provide the anchoring review: a
systematic analysis of over a hundred articles on SME default prediction across
thirty-four years, identifying five research streams and calling for work
exploiting new data sources.

Sri Lanka is documented as finance-constrained. Reported supply-side barriers
include absent formal records, insufficient tangible collateral, non-submission of
financial statements and limited management capacity, with policy responses
proposed around SME credit rating and credit guarantee schemes. This establishes
the practical motivation but does not address the appraisal *process*, which is
where this study is situated.

## 2.4 Variability in human credit judgement

This study is premised on manual appraisal being inconsistent. That premise should
not rest on assertion, and it does not have to.

Cortés, Duchin and Sosyura (2016) provide causal evidence. Using daily variation
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

Their most directly relevant result is finer than the headline. Examining the
reasons officers recorded for their decisions, they find that **a loan with the
same quantitative measures of risk is less likely to be rejected for subjective
reasons on sunny days**. It is not the arithmetic that moves; it is the
judgemental residue around it — which is precisely the part of the People's Bank
form that this study formalises, and precisely the part it leaves to the officer
where it cannot be formalised.

**The setting must be stated, because it is not this one.** Their evidence comes
from US residential mortgage applications in the confidential Home Mortgage
Disclosure Act registry — standardised consumer lending, not SME appraisal, and
not Sri Lanka. Nothing transfers automatically. What supports the transfer is the
direction of their own cross-sectional result: the effect grows as decisions
become more discretionary and less automated, and a narrative SME appraisal form
completed by hand sits further along that dimension than a residential mortgage
does. That is an argument, not an observation, and it is offered as one.

Related work reaches similar conclusions from other directions: studies of
discretion in loan rate setting, and of loan officers' subjective judgement in
microfinance, where risk classification rests on recollected professional
experience rather than an explicit model. SharafEldin, Idrees and Ouf (2025)
similarly motivate their work by observing that traditional credit assessment
"often relied on subjective judgment, leading to inconsistent decisions".

The premise is therefore supported by the literature. This study does **not**
itself measure inter-rater reliability, which remains its most significant gap
(§6.4); Cohen (1960), Landis and Koch (1977) and Krippendorff's α provide the
instruments a proper measurement would use.

## 2.5 Multi-criteria decision methods

### 2.5.1 Foundations

Zadeh (1965) introduced fuzzy sets, providing a representation for gradations of
membership rather than binary classification. Saaty (1980) introduced the
Analytic Hierarchy Process, later defending it against criticism (Saaty, 1990), deriving priority weights from pairwise comparisons on
a 1–9 scale — still the most widely used weighting method.

Fuzzy extensions followed. Chang (1996) proposed extent analysis for fuzzy AHP,
and Chen (2000) extended TOPSIS to fuzzy group decision-making with linguistic
ratings.

**A caution that shaped this study's method choice.** Chang's extent analysis is
very widely used, but subsequent work shows it *cannot recover true weights* from
a fuzzy comparison matrix and has produced a considerable number of
misapplications. Adopting it uncritically would have been the path of least
resistance; it is also documented to be wrong.

### 2.5.2 Best-Worst Method

Rezaei (2015) introduced the Best-Worst Method, which derives weights from two
comparison vectors — the best criterion against all others, and all others against
the worst — requiring 2n−3 comparisons rather than AHP's n(n−1)/2. Anchoring every
comparison to a fixed reference tends to produce more consistent responses.
Rezaei (2016) gave a linear formulation with a unique solution, which is the form
implemented here (§3.5).

For this study's criteria tree the difference is decisive: **168 comparisons under
pairwise AHP against 86 under BWM** (§3.5.1). That is the difference between an
hour of a practitioner's attention and fifteen minutes, and therefore between
usable and unusable responses.

### 2.5.3 Application to credit — and the nearest precedent

**Roy and Shaw (2021) must be acknowledged plainly.** They construct a
multicriteria credit scoring model for SMEs using exactly the hybrid this study's
proposal treated as novel: BWM to determine criteria weights, combined with a
ranking method (TOPSIS) to score applicants. Their instrument has 30 subcriteria
finalised by a panel of 12 experts — seven from banking and SME lending, five
from SMEs that had obtained credit — and they validate it against a commercial
rating agency's ratings on a real-life case study, reporting 90.32% accuracy and
a Type-II error rate of 14.28% against the commercial model's 28.57%.

The implication is direct: **applying BWM to SME credit scoring is not novel.** An
earlier draft of this research claimed the fuzzy-MCDM combination as its
methodological contribution. The literature does not support that claim, and it is
withdrawn here.

Two differences are worth stating precisely, because they cut in opposite
directions and the honest positioning depends on both.

Roy and Shaw **elicited their weights**; this study did not (§6.1), which is the
more serious gap of the two and is theirs to claim. Against that, their
validation rests on **31 SMEs** — an accuracy of 90.32% is 28 firms out of 31,
and a Type-II rate of 14.28% is one or two misclassifications. A sample that size
cannot separate a good model from a fortunate one. This study validates its
scoring method on 652,284 facilities with realised outcomes, and reports that the
expert-structured scorecard fails on them (§5.6).

They also aggregate. TOPSIS returns a single closeness coefficient, so
development and credit considerations, where both are present, are resolved into
one number. This study reports two and refuses to combine them.

Related work populates the space further: fuzzy BWM with fuzzy TOPSIS for
sustainable credit scoring, fuzzy-BWM with TOPSIS-Sort-C for credit rating, fuzzy
decision support systems for credit scoring, and fuzzy AHP combined with neural
approaches for SME credit risk assessment. The method space is well occupied.

What remains open is not the method but its **object**: no located study
formalises a *specific, named, operational appraisal instrument* of a state bank,
with every criterion traceable to a numbered clause of that institution's own
document.

## 2.6 Non-financial objectives in lending

### 2.6.1 Social criteria in credit scoring

Gutiérrez-Nieto, Serrano-Cinca and Camón-Cala (2016) build a credit score system
for socially responsible lending that evaluates social alongside financial
aspects, quantifying a loan's impact on outcomes such as employment, education,
environment and health, and using MCDM to combine them. Their system yields not
only a score but an account of an application's strengths and weaknesses.

This narrows the novelty claim again: **scoring social impact alongside credit
risk has been done.** Their method is AHP in its absolute-measurement mode, with
social outcomes valued through Social Return on Investment, and it is
demonstrated on a single real application — a bike courier company's loan request
to a Spanish financial services cooperative, whose board supplied the preference
weights. AHP was chosen, they report, largely because the algorithm was already
available in a spreadsheet and the cooperative's analysts found it easy to use.

Two differences remain. The first is institutional grounding: the development
criteria here are not selected by the researcher from a development framework but
taken from clause 5 of an instrument a state bank already uses in production. The
second is aggregation. Their system merges financial ratios and social indicators
in one model to produce a single assessment; this study keeps the two objectives
apart and never issues a combined figure, which §5.6b shows changes the answer for
88.2% of facilities.

### 2.6.2 Development returns and credit risk

Arvanitis, Stampini and Vencatachellum (2015) examine ex-ante appraisal at the
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
collapsing them into one number. §5.6b tests the association directly on a sample
large enough to resolve it.

## 2.7 Explainability, regulation, and data quality

### 2.7.1 Why explanation is not optional

Explainability in credit is a legal requirement, not a design preference. Under
the U.S. Equal Credit Opportunity Act and Regulation B, creditors must state the
specific principal reasons for adverse action; regulatory guidance holds that a
creditor cannot excuse non-compliance on the grounds that its technology is too
complex to interpret, nor satisfy the requirement by citing broad categories.
Credit scoring is designated high-risk under the EU AI Act.

The technical response has been post-hoc explanation: LIME (Ribeiro, Singh and
Guestrin, 2016) fits an interpretable local surrogate around a prediction, and
SHAP (Lundberg and Lee, 2017) assigns each feature a Shapley-value contribution
with uniqueness guarantees.

**This study takes a different route, and the distinction is worth stating.**
LIME and SHAP explain an opaque model after the fact. The model here is additive
by construction, so per-criterion contributions are exact rather than
approximated, and they sum precisely to the score (§4.7). That is a stronger
guarantee than a post-hoc method can offer — at the cost of the discrimination a
flexible model might achieve, which Chapter 5 shows to be a real cost.

### 2.7.2 Leakage and reproducibility

Kapoor and Narayanan (2023) surveyed machine-learning-based science across
seventeen fields and found leakage affecting **294 papers**, in some cases
producing wildly overoptimistic conclusions. They argue leakage is the single
largest cause of irreproducibility in the area, and set out a taxonomy of eight
types ranging from textbook errors to open research problems.

This is the frame within which Chapter 5's finding sits: not a curiosity peculiar
to one dataset, but an instance of a documented, recurring failure.

### 2.7.3 The SBA National dataset

Li, Mickel and Taylor (2018) introduced the SBA National dataset — 899,164 loan
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

## 2.8 Research gap

Consolidating, the following are **not** contributions of this study, contrary to
the original proposal:

- combining weighted financial ratios into a credit score (Altman, 1968, and
  sixty years of work after it);
- applying BWM or fuzzy MCDM to SME credit scoring (Roy and Shaw, 2021, and the
  surrounding literature in §2.5.3);
- scoring social or developmental impact alongside credit risk (Gutiérrez-Nieto
  et al., 2016);
- observing that development banks appraise against two objectives (Arvanitis
  et al., 2015).

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
   the separation is warranted rather than assuming it (§5.6b).
4. **The Sri Lankan state-bank context**, documented as finance-constrained but
   not studied at the level of appraisal process.

Contribution 1 is the substantial one and the most transferable. Contributions 2
to 4 are real but incremental, and are stated as such throughout.

---

## References

Full bibliography, with per-entry verification status, in
`docs/02-literature/bibliography.md`.

Altman, E.I. (1968) 'Financial Ratios, Discriminant Analysis and the Prediction of
Corporate Bankruptcy', *Journal of Finance*, 23(4), pp. 589–609.
doi:10.1111/j.1540-6261.1968.tb00843.x

Arvanitis, Y., Stampini, M. and Vencatachellum, D. (2015) 'Balancing development
returns and credit risks: project appraisal in a multilateral development bank',
*Impact Assessment and Project Appraisal*, 33(3), pp. 195–206.
doi:10.1080/14615517.2015.1041837

Beck, T. and Demirgüç-Kunt, A. (2006) 'Small and medium-size enterprises: Access
to finance as a growth constraint', *Journal of Banking & Finance*, 30(11),
pp. 2931–2943.

Berger, A.N. and Udell, G.F. (2006) 'A more complete conceptual framework for SME
finance', *Journal of Banking & Finance*, 30(11), pp. 2945–2966.

Brier, G.W. (1950) 'Verification of forecasts expressed in terms of probability',
*Monthly Weather Review*, 78(1), pp. 1–3.

Chang, D.-Y. (1996) 'Applications of the extent analysis method on fuzzy AHP',
*European Journal of Operational Research*, 95(3), pp. 649–655.

Chen, C.-T. (2000) 'Extensions of the TOPSIS for group decision-making under fuzzy
environment', *Fuzzy Sets and Systems*, 114(1), pp. 1–9.

Ciampi, F., Giannozzi, A., Marzi, G. and Altman, E.I. (2021) 'Rethinking SME
default prediction: a systematic literature review and future perspectives',
*Scientometrics*, 126, pp. 2141–2188. doi:10.1007/s11192-020-03856-0

Cohen, J. (1960) 'A coefficient of agreement for nominal scales', *Educational and
Psychological Measurement*, 20(1), pp. 37–46.

Cortés, K.R., Duchin, R. and Sosyura, D. (2016) 'Clouded judgment: The role of
sentiment in credit origination', *Journal of Financial Economics*, 121(2),
pp. 392–413.

DeLong, E.R., DeLong, D.M. and Clarke-Pearson, D.L. (1988) 'Comparing the areas
under two or more correlated receiver operating characteristic curves: a
nonparametric approach', *Biometrics*, 44(3), pp. 837–845.

Gutiérrez-Nieto, B., Serrano-Cinca, C. and Camón-Cala, J. (2016) 'A Credit Score
System for Socially Responsible Lending', *Journal of Business Ethics*, 133(4),
pp. 691–701. doi:10.1007/s10551-014-2448-5

Hand, D.J. and Henley, W.E. (1997) 'Statistical Classification Methods in Consumer
Credit Scoring: A Review', *Journal of the Royal Statistical Society Series A*,
160(3), pp. 523–541.

Hanley, J.A. and McNeil, B.J. (1982) 'The meaning and use of the area under a
receiver operating characteristic (ROC) curve', *Radiology*, 143(1), pp. 29–36.

Hevner, A.R., March, S.T., Park, J. and Ram, S. (2004) 'Design Science in
Information Systems Research', *MIS Quarterly*, 28(1), pp. 75–105.

Kapoor, S. and Narayanan, A. (2023) 'Leakage and the reproducibility crisis in
machine-learning-based science', *Patterns*, 4(9), 100804.
doi:10.1016/j.patter.2023.100804

Landis, J.R. and Koch, G.G. (1977) 'The measurement of observer agreement for
categorical data', *Biometrics*, 33(1), pp. 159–174.

Lessmann, S., Baesens, B., Seow, H.-V. and Thomas, L.C. (2015) 'Benchmarking
state-of-the-art classification algorithms for credit scoring: An update of
research', *European Journal of Operational Research*, 247(1), pp. 124–136.

Li, M., Mickel, A. and Taylor, S. (2018) '"Should This Loan be Approved or
Denied?": A Large Dataset with Class Assignment Guidelines', *Journal of
Statistics Education*, 26(1), pp. 55–66. doi:10.1080/10691898.2018.1434342

Lundberg, S.M. and Lee, S.-I. (2017) 'A Unified Approach to Interpreting Model
Predictions', *Advances in Neural Information Processing Systems 30*,
pp. 4765–4774.

Ohlson, J.A. (1980) 'Financial Ratios and the Probabilistic Prediction of
Bankruptcy', *Journal of Accounting Research*, 18(1), pp. 109–131.

Peffers, K., Tuunanen, T., Rothenberger, M.A. and Chatterjee, S. (2007) 'A Design
Science Research Methodology for Information Systems Research', *Journal of
Management Information Systems*, 24(3), pp. 45–77.

Rezaei, J. (2015) 'Best-worst multi-criteria decision-making method', *Omega*, 53,
pp. 49–57. doi:10.1016/j.omega.2014.11.009

Rezaei, J. (2016) 'Best-worst multi-criteria decision-making method: Some
properties and a linear model', *Omega*, 64, pp. 126–130.

Ribeiro, M.T., Singh, S. and Guestrin, C. (2016) '"Why Should I Trust You?":
Explaining the Predictions of Any Classifier', *Proceedings of the 22nd ACM SIGKDD
International Conference on Knowledge Discovery and Data Mining*, pp. 1135–1144.

Roy, P.K. and Shaw, K. (2021) 'A multicriteria credit scoring model for SMEs using
hybrid BWM and TOPSIS', *Financial Innovation*, 7(1).
doi:10.1186/s40854-021-00295-5

Saaty, T.L. (1980) *The Analytic Hierarchy Process*. New York: McGraw-Hill.

Saaty, T.L. (1990) 'An exposition of the AHP in reply to the paper "Remarks on the
Analytic Hierarchy Process"', *Management Science*, 36(3), pp. 259–268.

SharafEldin, M.A., Idrees, A.M. and Ouf, S. (2025) 'A Proposed Framework for Loan
Default Prediction Using Machine Learning Techniques', *International Journal of
Advanced Computer Science and Applications*, 16(6), pp. 412–425.

Stein, J.C. (2002) 'Information Production and Capital Allocation: Decentralized
versus Hierarchical Firms', *Journal of Finance*, 57(5), pp. 1891–1921.

Thomas, L.C., Crook, J.N. and Edelman, D.B. (1992) *Credit Scoring and Credit
Control*. Oxford: Clarendon Press.

Thomas, L.C., Edelman, D.B. and Crook, J.N. (2002) *Credit Scoring and its
Applications*. Philadelphia: SIAM.

Zadeh, L.A. (1965) 'Fuzzy sets', *Information and Control*, 8(3), pp. 338–353.
