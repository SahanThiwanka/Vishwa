# Chapter 1 — Introduction

## 1.1 Background

Small and medium enterprises account for the large majority of businesses in Sri
Lanka and a substantial share of employment. Their access to formal credit is
persistently constrained. Documented supply-side barriers include the absence of
formal accounting records, insufficient tangible collateral, non-submission of
financial statements, and limited management capacity — with policy responses
proposed around SME credit rating, credit guarantee schemes, and SME-friendly
banking practice.

Most of that literature examines whether credit is *available*. This study
examines something narrower and less studied: how a bank *decides*, once an
application is in front of an officer.

## 1.2 The appraisal problem

People's Bank appraises SME credit using a *Project / Business Appraisal Report
for SME Credit Facility* — a seven-section form with five annexures, in
operational use. It is a thorough instrument. It requires thirteen financial
ratios, three-to-five-year projections with debt service and interest service
cover, a Porter's five-forces analysis of the applicant's market, technological
and environmental risk assessments, and a nine-item table of economic
contribution covering employment, women's participation, import substitution and
foreign exchange earnings.

It is also, in large part, **narrative**. Clause 2.18 asks for written comments on
profitability, liquidity, activity and gearing. Clause 3.2 asks for a description
of management style. Clause 7 then asks the officer to certify that the project is
"financially viable and technically feasible."

Between the evidence and the certification there is no stated procedure. The form
specifies exhaustively *what* to consider and says nothing about *how to weigh it*.

Three consequences follow:

**It is slow.** Thirteen ratios, cover ratios, break-even and working capital
computations are performed by hand for every application.

**It is inconsistent.** Two officers with the same file may reach different
conclusions, because the method for combining the evidence lives in each
officer's head rather than in the instrument.

**It is difficult to audit.** A recommendation records a conclusion but not the
reasoning that produced it. When a facility later performs badly, there is no
record of which factors were weighed and how heavily.

None of this reflects poorly on the officers. It reflects an instrument that
codifies what to look at without codifying how to judge it.

## 1.3 Research questions

- **RQ1** — How can the narrative, multi-section appraisal instrument used by a
  Sri Lankan state bank be formalised into a computable multi-criteria model
  without discarding the judgement it encodes?
- **RQ2** — What relative weights do experienced credit practitioners assign to
  the resulting criteria, and how consistent are those judgements?
- **RQ3** — How does the resulting model perform against realised loan outcomes on
  observable criteria, relative to standard credit-scoring benchmarks?
- **RQ4** — How does treating development impact as a separate objective change
  the assessment of applications, compared with credit risk alone?

These differ from the questions in the original research proposal. The literature
review (§2.3.3) established that the contribution originally claimed — applying
fuzzy multi-criteria methods to SME credit scoring — is already published. The
questions were revised accordingly rather than restated in a form the literature
no longer supports.

## 1.4 Objectives

1. Derive a computable criteria model from the People's Bank appraisal form, with
   every criterion traceable to a numbered clause.
2. Implement a scoring method handling both measured quantities and linguistic
   judgements, reporting per-criterion contributions.
3. Build a working decision-support system that produces its output in the
   institution's own report format.
4. Elicit criterion weights from practitioners using a method whose response
   burden is realistic and whose consistency is measurable.
5. Evaluate what can be established about the model empirically — and state
   plainly what cannot.

## 1.5 A note on the second objective

The bank's form scores nine developmental outcomes in clause 5 and disaggregates
employment by gender in clause 3.4.1. These are not credit risk. A project can
create employment, substitute imports and earn foreign exchange while remaining a
weak credit; the reverse also holds.

Conventional credit scoring optimises one thing: the probability of repayment.
Applying that framing to this instrument would mean deleting clause 5 — discarding
the developmental half of a state bank's mandate because it does not fit the
model.

This study therefore scores two objectives and **reports them separately, never
combining them into a single figure**. Prior work has scored social impact
alongside credit risk (§2.4.1); what is done differently here is the refusal to
aggregate. That refusal is supported by evidence: appraisal at a multilateral
development bank shows development and credit concerns to be empirically
independent (§2.4.2), so a combined score would discard real information rather
than summarise it.

## 1.6 Scope and delimitations

**In scope.** One institution's appraisal instrument; a working system; weight
elicitation from practitioners; empirical validation of the scoring machinery
against public data with realised outcomes.

**Out of scope.** Automated credit decisioning — the system supports the officer
and does not replace them. Validation against People's Bank's own historical
outcomes, which were not accessible and are confidential. Field deployment. Any
claim that the model generalises beyond the instrument it was derived from.

**The central limitation, stated at the outset.** No public dataset contains the
criteria this model scores. Empirical validation therefore uses a proxy dataset
and tests the scoring machinery, not the criteria tree. Chapter 5 reports what
follows from that honestly, including a negative result.

## 1.7 Contributions

1. **Contamination in a widely used benchmark dataset.** In the SBA National
   dataset, whether the `Term` field is an exact multiple of twelve predicts
   default at AUC 0.889 — within every approval year, despite carrying no
   economic meaning. Excluding the field drops gradient-boosting temporal AUC
   from 0.946 to 0.608. The contamination is demonstrated; its mechanism is
   reported as unresolved rather than asserted.
2. **A methodological consequence**: an instrument-specific appraisal model
   cannot be validated on a dataset lacking its variables. Substituting available
   proxies tests the proxies, not the model — evidenced by a scorecard that failed
   to discriminate (§5.6).
3. **A clause-traceable formalisation method** taking a named state bank's
   production form to a 49-criterion computable model, transferable to comparable
   institutions.
4. **A working system** producing dual-objective, explainable assessments and
   exporting them in the bank's own report format.
5. **A design finding**: weight renormalisation over unassessed criteria allows a
   sparse appraisal to produce a confident score, requiring an explicit
   completeness gate (§4.5).

Contributions 1 and 2 are the substantial ones. Contributions 3 to 5 are real but
incremental, and are described as such throughout.

## 1.8 Structure

| Chapter | Content |
|---|---|
| 2 | Literature: MCDM in credit, non-financial objectives, explainability, and what remains open |
| 3 | Methodology: design science, formalisation, BWM elicitation, validation protocol, ethics |
| 4 | Design and implementation of the criteria model and system |
| 5 | Empirical validation, the contamination finding, and a negative result |
| 6 | Elicitation results, discussion, limitations, conclusion |

A note on presentation. This thesis reports several things that did not work: a
claimed contribution withdrawn after the literature review, a scorecard that
failed to discriminate, and a mechanism hypothesis tested and rejected. These are
reported because a study that presents only its successes gives the reader no way
to judge the reliability of any of them.
