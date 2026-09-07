# Chapter 2 — Literature Review

> **Verification note for the author.** Every source cited here was located
> through a literature search and its bibliographic details checked. Before
> submission, obtain and read each paper directly — do not cite from a summary.
> Where this chapter says a claim is "not found in the searched literature", that
> is a statement about a non-exhaustive search, not a claim of priority.

## 2.1 Scope

This review covers four bodies of work bearing on the research questions:
credit scoring for SMEs; multi-criteria decision methods applied to credit;
non-financial objectives in lending; and explainability requirements. It closes
by stating what the present study adds — which, after examining the literature,
is narrower than initially supposed.

## 2.2 SME credit assessment

Credit scoring has a long statistical lineage, from discriminant analysis through
logistic regression to modern machine learning. For SMEs the problem is harder
than for consumer credit: financial statements are often unaudited or absent,
trading histories are short, and collateral is thin.

In Sri Lanka specifically, access to finance is repeatedly identified as a
principal constraint on SME growth. The supply-side barriers documented include
absent formal records, lack of tangible collateral, non-submission of financial
statements, and limited management capacity — with policy responses proposed
around SME credit rating, credit guarantee schemes and SME-friendly banking
practice (Institute of Policy Studies, Sri Lanka). This establishes the practical
motivation for the present study but does not address the appraisal *process*
itself, which is where this research is situated.

## 2.3 Multi-criteria decision methods in credit evaluation

### 2.3.1 Fuzzy MCDM for credit scoring

Where credit judgement is linguistic and imprecise, fuzzy set theory offers a
representation that discards less information than forcing a crisp number.
Fuzzy AHP has been applied to generate criteria weights in credit scoring
decision-support systems, with fuzzy linguistic variables used explicitly to
capture the vagueness arising from human subjectivity. More recent work combines
fuzzy AHP with neural approaches for SME credit risk assessment, identifying
financial status and development planning as dominant risk themes.

### 2.3.2 Best-Worst Method

The Best-Worst Method (Rezaei, 2015) determines criteria weights from two
comparison vectors: the best criterion against all others, and all others against
the worst. It requires 2n−3 comparisons rather than AHP's n(n−1)/2, and the
anchoring of every comparison to a fixed reference tends to produce more
consistent responses. Rezaei (2016) subsequently gave a linear formulation with a
unique solution, which is the form used in this study.

### 2.3.3 Prior work closest to this study

**Roy and Shaw (2021) is the nearest precedent and must be acknowledged plainly.**
They construct a multicriteria credit scoring model for SMEs using exactly the
hybrid this study's methodology chapter proposes: BWM to determine criteria
weights, combined with a ranking method (TOPSIS) to score applicants. They report
credit history, cash liquidity and repayment period as the dominant criteria.

The implication is direct: **applying BWM to SME credit scoring is not novel.** An
earlier draft of this research treated the fuzzy-MCDM combination as its
methodological contribution. The literature does not support that claim, and it is
withdrawn. Related work extends the same family further — fuzzy BWM with fuzzy
TOPSIS for sustainable credit scoring, and fuzzy-BWM with TOPSIS-Sort-C for credit
rating — confirming that the method space is well populated.

What remains open is not the method but its **object**: no located study
formalises a *specific, named, operational appraisal instrument* of a state bank,
with every criterion traceable to a numbered clause of that institution's own
document.

## 2.4 Non-financial objectives in lending

### 2.4.1 Social criteria in credit scoring

Gutiérrez-Nieto, Serrano-Cinca and Camón-Cala (2016) build a credit score system
for socially responsible lending that evaluates social alongside financial
aspects, quantifying a loan's impact on outcomes such as employment, education,
environment and health, and using MCDM to combine them. Their system yields not
only a score but an account of an application's strengths and weaknesses.

This is close to the present study's second objective, and again narrows the
novelty claim: **scoring social impact alongside credit risk has been done.** The
difference here is one of institutional grounding — the development criteria in
this study are not selected by the researcher from a development framework, but
taken from clause 5 of an instrument a state bank already uses in production.

### 2.4.2 Development returns and credit risk in development banking

Arvanitis, Stampini and Vencatachellum (2015) examine ex-ante appraisal at the
African Development Bank and report a result of direct consequence for this study:
**development and risk concerns considered during project appraisal are empirically
independent of one another**, and no assumption should be made about one from the
other.

This is the strongest available justification for the design decision taken in
Chapter 4. If the two objectives were strongly correlated, a single combined score
would lose little. Because they are independent, aggregation destroys real
information: a facility strong on credit and weak on development is a materially
different proposition from one moderate on both, and a combined score renders them
indistinguishable. The present study's refusal to merge the two objectives is
therefore not merely a presentational preference but is supported by prior
empirical evidence.

## 2.5 Explainability and its regulatory basis

Explainability in credit is a legal requirement, not a design preference. Under
the U.S. Equal Credit Opportunity Act and Regulation B, creditors must state the
specific principal reasons for adverse action; regulatory guidance has held that a
creditor cannot excuse non-compliance on the grounds that its technology is too
complex to interpret, nor satisfy the requirement by citing broad categories.
Credit scoring is designated high-risk under the EU AI Act.

Two consequences follow for this study. First, a scoring model intended for
adoption inside a bank must decompose its output into per-criterion contributions
— which is why the engine reports contributions summing exactly to the parent
score. Second, an interpretable model that loses some discrimination relative to
an opaque one may still be the only deployable option, which reframes the
comparison in Chapter 5: the question is not merely which model scores highest.

## 2.6 The SBA National dataset

Li, Mickel and Taylor (2018) introduced the SBA National dataset — 899,164 loan
guarantees, 1987–2014, with realised outcomes — as a teaching resource for
statistics as investigative decision-making. It has since become a widely used
benchmark in small-business credit research.

The searched literature discusses feature importance in this dataset, and notes
`Term`, disbursement and approval amounts as significant predictors of default.
General treatments of leakage in credit modelling identify interest rate, issue
date and outstanding principal as fields to remove.

**No located source reports that the `Term` field itself carries outcome
information.** Chapter 5 presents evidence that it does. This is stated as a
finding the author has not found documented elsewhere, which is weaker than a
claim of priority and is the appropriate claim given a non-exhaustive search.

## 2.7 Research gap

Consolidating the above, the following are **not** contributions of this study,
contrary to the initial proposal:

- applying BWM or fuzzy MCDM to SME credit scoring (Roy and Shaw, 2021);
- scoring social or developmental impact alongside credit risk
  (Gutiérrez-Nieto et al., 2016);
- observing that development banks appraise against two objectives
  (Arvanitis et al., 2015).

What the literature leaves open, and what this study addresses:

1. **Formalising a specific operational instrument.** Existing models select
   criteria from theory or from the researcher's judgement. None located takes a
   named state bank's production appraisal form and derives a computable model
   from it clause by clause, with full traceability maintained as a design
   constraint.
2. **Keeping dual objectives unaggregated.** Prior dual-objective systems combine
   social and financial scores. Given Arvanitis et al.'s independence result, this
   study reports them separately by design and never produces a combined figure.
3. **The Sri Lankan state-bank context**, which is documented as finance-constrained
   but not studied at the level of appraisal process.
4. **Contamination in a widely used benchmark dataset** (Chapter 5), and the
   consequent methodological point that instrument-specific models cannot be
   validated on datasets lacking their variables.

Contribution 4 is the most substantial and the most transferable. Contributions 1
to 3 are real but incremental, and are stated as such.

---

## References

Arvanitis, Y., Stampini, M. and Vencatachellum, D. (2015) 'Balancing development
returns and credit risks: project appraisal in a multilateral development bank',
*Impact Assessment and Project Appraisal*, 33(3), pp. 195–206.
doi:10.1080/14615517.2015.1041837.

Gutiérrez-Nieto, B., Serrano-Cinca, C. and Camón-Cala, J. (2016) 'A Credit Score
System for Socially Responsible Lending', *Journal of Business Ethics*, 133(4),
pp. 691–701. doi:10.1007/s10551-014-2448-5.

Li, M., Mickel, A. and Taylor, S. (2018) '"Should This Loan be Approved or
Denied?": A Large Dataset with Class Assignment Guidelines', *Journal of
Statistics Education*, 26(1), pp. 55–66. doi:10.1080/10691898.2018.1434342.

Rezaei, J. (2015) 'Best-worst multi-criteria decision-making method', *Omega*, 53,
pp. 49–57. doi:10.1016/j.omega.2014.11.009.

Rezaei, J. (2016) 'Best-worst multi-criteria decision-making method: Some
properties and a linear model', *Omega*, 64, pp. 126–130.

Roy, P.K. and Shaw, K. (2021) 'A multicriteria credit scoring model for SMEs using
hybrid BWM and TOPSIS', *Financial Innovation*, 7(1). doi:10.1186/s40854-021-00295-5.

**To be completed before submission** — the following were located but require
retrieval and full bibliographic capture:

- Fuzzy decision support system for credit scoring, *Neural Computing and
  Applications* (Springer), doi:10.1007/s00521-016-2592-1
- Integrated fuzzy credit rating model using fuzzy-BWM and fuzzy-TOPSIS-Sort-C,
  *Complex & Intelligent Systems*, doi:10.1007/s40747-022-00823-5
- Multi-criteria sustainable credit score system using fuzzy BWM and fuzzy TOPSIS,
  *Environment, Development and Sustainability*, doi:10.1007/s10668-021-01662-z
- Knowledge-informed neural network integrating fuzzy AHP and PCA for SME credit
  risk assessment, *Scientific Reports* (2025), doi:10.1038/s41598-025-21441-4
- Institute of Policy Studies Sri Lanka, *Banking on SME Growth: Concepts,
  Challenges and Policy Options to Improve Access to Finance in Sri Lanka*
- Central Bank of Sri Lanka, *Annual Report* — for national SME credit statistics
- World Bank Enterprise Surveys — Sri Lanka firm-level access-to-finance data
