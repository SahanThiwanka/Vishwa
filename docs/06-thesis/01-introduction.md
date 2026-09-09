# 1 INTRODUCTION

## 1.1 Background

Small and medium enterprises are reported to account for approximately 75% of
active enterprises in Sri Lanka, 45% of employment and 52% of GDP.[^smestats] Their access to formal credit is
persistently constrained. Documented supply-side barriers include the absence of
formal accounting records, insufficient tangible collateral, non-submission of
financial statements, and limited management capacity — with policy responses
proposed around SME credit rating, credit guarantee schemes, and SME-friendly
banking practice.

Most of that literature examines whether credit is *available*. This study
examines something narrower and less studied: how a bank *decides*, once an
application is in front of an officer.

[^smestats]: These figures are widely reported but currently rest on secondary
    sources. **Attribute them to a primary source — the National Policy Framework
    for SME Development, Department of Census and Statistics, or Central Bank of
    Sri Lanka — before submission.** Note also that Sri Lanka had no uniform SME
    definition before 2015, so figures spanning that boundary are not necessarily
    comparable.

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
officer's head rather than in the instrument. This is not speculation: Cortés,
Duchin and Sosyura [1] show that officers' credit approvals move with their
mood — instrumented by local sunshine — and that the effect is **larger where
decisions carry more discretion and reviews are less automated**, which is
exactly the regime this form operates in.

**It is difficult to audit.** A recommendation records a conclusion but not the
reasoning that produced it. When a facility later performs badly, there is no
record of which factors were weighed and how heavily.

None of this reflects poorly on the officers. It reflects an instrument that
codifies what to look at without codifying how to judge it.

## 1.3 Research questions

- **RQ1** — How can the narrative, multi-section appraisal instrument used by a
  Sri Lankan state bank be formalised into a computable multi-criteria model
  without discarding the judgement it encodes?
- **RQ2** — How sensitive is such a model's output to its criterion weights, and
  what follows for a model deployed before those weights are empirically
  established?
- **RQ3** — What can and cannot be established about an instrument-specific
  appraisal model from publicly available credit data, and how does it compare
  with standard credit-scoring benchmarks?
- **RQ4** — Are credit risk and development impact separable objectives in
  practice, and what would a combined score conceal?

These differ from the questions in the original research proposal, for two
reasons, both stated openly.

First, the literature review (§5.10.3) established that the contribution
originally claimed — applying fuzzy multi-criteria methods to SME credit scoring —
is already published. The questions were revised rather than restated in a form
the literature no longer supports.

Second, the original RQ2 asked what weights practitioners assign to the criteria.
Answering it requires practitioner participation that was not obtained within the
study period (§6.1). Rather than pose a question the study cannot answer, RQ2 now
asks something it can: how much the model's output depends on its weights at all.
That is answerable by simulation, is arguably the more useful question for anyone
deploying such a model, and it bounds what the missing elicitation costs. The
elicitation instrument was nonetheless built, tested and is reported in §6.1 as
prepared but not administered.

## 1.4 A note on the second objective

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
alongside credit risk (§3.6.1); what is done differently here is the refusal to
aggregate. That refusal is supported by evidence: appraisal at a multilateral
development bank shows development and credit concerns to be empirically
independent (§3.6.2), so a combined score would discard real information rather
than summarise it.

## 1.5 Scope and delimitations

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

## 1.6 Contributions

1. **Contamination in a widely used benchmark dataset.** In the SBA National
   dataset, whether the `Term` field is an exact multiple of twelve predicts
   default at AUC 0.889 — within every approval year, despite carrying no
   economic meaning. Excluding the field drops gradient-boosting temporal AUC
   from 0.946 to 0.608. The contamination is demonstrated; its mechanism is
   reported as unresolved rather than asserted.
2. **A methodological consequence**: an instrument-specific appraisal model
   cannot be validated on a dataset lacking its variables. Substituting available
   proxies tests the proxies, not the model — evidenced by a scorecard that failed
   to discriminate (§5.15).
3. **A clause-traceable formalisation method** taking a named state bank's
   production form to a 49-criterion computable model, transferable to comparable
   institutions.
4. **A working system** producing dual-objective, explainable assessments and
   exporting them in the bank's own report format.
5. **A design finding**: weight renormalisation over unassessed criteria allows a
   sparse appraisal to produce a confident score, requiring an explicit
   completeness gate (§5.10).
6. **Evidence on objective separability**: across 652,284 facilities the two
   objectives correlate moderately (r = +0.40) yet band the same facility
   differently 88.2% of the time — and development impact is positively
   associated with default. Reporting them separately preserves information a
   combined score would destroy (§5.17).
7. **A calibration finding**: reliability degrades roughly 700-fold across a
   temporal boundary while discrimination falls far less, so a scorecard can
   continue to rank while systematically mispricing risk (§5.13).

Contributions 1 and 2 are the substantial ones. Contributions 3 to 7 are real but
incremental, and are described as such throughout.

## 1.7 Structure

| Chapter | Content |
|---|---|
| 2 | Literature: MCDM in credit, non-financial objectives, explainability, and what remains open |
| 3 | Methodology: design science, formalisation, BWM elicitation, validation protocol, ethics |
| 4 | Design and implementation of the criteria model and system |
| 5 | Empirical validation, the contamination finding, and a negative result |
| 6 | Answers to the research questions, discussion, limitations, conclusion |

A note on presentation. This thesis reports several things that did not work: a
claimed contribution withdrawn after the literature review, a scorecard that
failed to discriminate, a mechanism hypothesis tested and rejected, an elicitation
designed but not administered, and an independence premise that its own data
partly contradicts. These are reported because a study that presents only its
successes gives the reader no way to judge the reliability of any of them.
