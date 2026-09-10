# Viva Preparation

Read this alongside the thesis, not instead of it. Examiners test whether you
understand your own work, and the fastest way to fail is to recite an answer you
cannot follow up on.

**The single rule: never claim more than the evidence supports.** This thesis is
unusually honest — it withdraws claims, reports a failure, and rejects one of its
own hypotheses. That is a strength, and it only works if you defend it as one.

---

## 1. Before anything else

If you cannot do all five of these from memory, you are not ready to sit:

1. Explain what the system does and who uses it, in under a minute.
2. State your contribution and, crucially, what is **not** your contribution.
3. Explain the `Term` finding and why it matters beyond your study.
4. Explain why your scorecard failed and why that is in the thesis.
5. Open any file in the repository and explain what it does.

Item 5 matters. An examiner may ask you to walk through code. Spend an evening
reading `web/src/lib/scoring/engine.ts`, `research/src/leakage_analysis.py` and
`research/src/bwm.py` until you could re-derive them.

---

## 2. The 60-second answer

Have this ready for "tell us about your research":

> People's Bank appraises SME credit using a seven-section form that asks for
> thirteen financial ratios, cover ratios, a Porter's five-forces market analysis,
> and nine development outcomes — then asks the officer to certify the project is
> viable, with no stated procedure for combining any of it. I formalised that form
> into 49 criteria, every one traceable to a numbered clause, and built a
> decision-support system that scores credit risk and development impact as two
> separate objectives and explains every score criterion by criterion.
>
> The empirical work produced something I did not set out to find. Benchmarking on
> a public SME loan dataset gave an implausibly high result, and on investigation
> the dataset's `Term` field turned out to carry information about the outcome.
> That became the study's main contribution: a caution about a benchmark other
> researchers rely on.

Then stop. Let them ask.

---

## 3. The questions that will actually be asked

### 3.1 "Your contribution changed from the proposal. Why?"

**This will come up. Answer it head-on.**

> The proposal claimed that applying fuzzy multi-criteria methods to SME credit
> scoring was novel. When I did the literature review properly I found Roy and
> Shaw (2021) in *Financial Innovation*, who use exactly that combination —
> Best-Worst Method for weights plus a ranking method for scoring — on SME credit.
> I also found Gutiérrez-Nieto and colleagues (2016) in the *Journal of Business
> Ethics*, who already score social impact alongside credit risk.
>
> So two claims in my proposal were not defensible, and I withdrew them explicitly
> in sections 2.3.3 and 2.4.1 rather than restating them in a weaker form. What
> survives is narrower and I say so: the objects of the study rather than the
> methods.

**Do not** get defensive. A student who finds their own claim already published
and says so is doing research correctly. The failure mode would have been not
looking.

### 3.2 "So what IS your contribution?"

Know the order. The first two are the substantial ones:

1. **The `Term` contamination** in the SBA National dataset — reproducible,
   documented, and a caution to everyone using that benchmark.
2. **A methodological result**: an instrument-specific appraisal model cannot be
   validated on a dataset that lacks its variables. Substituting proxies tests
   the proxies, not the model.
3. A clause-traceable formalisation method for a named institutional instrument.
4. A working dual-objective system that exports in the bank's own format.
5. A design finding: weight renormalisation lets a sparse appraisal produce a
   confident score, so a completeness gate is required.

If pressed on 3–5: *"Those are real but incremental, and the thesis describes them
that way."*

### 3.3 "Your scorecard scored below chance. Isn't that a failed project?"

> No — it is a result, and it is why the methodological contribution holds.
>
> The scorecard I could test on SBA data was built from SBA-observable proxies:
> guarantee share, franchise status, urban or rural. Those are not what the
> People's Bank form scores. The form scores debt service cover, management
> quality, competitive position, security cover — none of which exist in that
> dataset. So the test tells you the proxies carry no signal. It does not tell you
> the criteria tree is wrong, and I am careful in section 5.6 not to claim it does.
>
> Two explanations remain live: the proxies are inadequate, or my a priori bands
> are mis-signed. The evidence does not separate them, and I say so.

**Follow-up you should expect:** *"Then why report it at all?"*

> Because it is the evidence for the methodological point. If I had quietly
> dropped it, the claim that instrument-specific models need elicitation rather
> than proxy validation would be an assertion. With it, it is a demonstration.

### 3.4 "Your main finding is about a US dataset. How is that Sri Lankan research?"

Fair question, answer directly:

> The Sri Lankan contribution is the artefact: the formalisation of People's
> Bank's instrument and the working system. The dataset finding emerged from
> trying to validate that artefact honestly, and it turned out to be the more
> transferable result.
>
> I could not validate against Sri Lankan data — People's Bank files are
> confidential and were not available to me. The thesis states that as its central
> limitation in section 1.6, before any results are presented, rather than
> discovering it afterwards.

### 3.5 "How do you know `Term` is contaminated and not just predictive?"

Know these numbers cold:

| Evidence | Value |
|---|---|
| Repaid loans with term a multiple of 12 | **86.4%** |
| Charged-off loans with term a multiple of 12 | **8.5%** |
| AUC of that single boolean | **0.889** |
| Same, within every year 1990–2010 | **0.859 – 0.900** |
| 2007 approvals at 60 months | **11.1% default** |
| 2007 approvals at 59 / 61 months | **86.7% / 92.2%** |
| GBM temporal AUC with `Term` | **0.9461** |
| GBM temporal AUC without | **0.6076** |

> The decisive one is the 59-60-61 month comparison. A one-month difference in
> contractual term cannot produce an eight-fold difference in default rate. There
> is no economic mechanism that does that. And the association is not a cohort
> effect — I computed it within each approval year separately and it holds in
> every one.

### 3.6 "What causes it?"

**Do not speculate. This is a trap and the honest answer is stronger.**

> I don't know, and I tested the obvious explanation and rejected it. The natural
> hypothesis is that `Term` was overwritten with elapsed time to charge-off. Among
> 156,000 charged-off loans with both dates, the correlation between `Term` and
> actual months to charge-off is 0.043, and only 5% agree within three months. So
> it is not survival time.
>
> The contamination is demonstrated; the mechanism is not. Section 5.3.4 reports
> it that way. Resolving it would need the SBA's own records, and I say so in
> future work.

### 3.7 "Has nobody noticed this before?"

> I searched and found no report of it, but my search was not exhaustive, so I
> claim only that I am not aware of it having been documented — not priority. The
> paper draft carries a note that a systematic search for affected published work
> must be completed before submission.

That is the correct, defensible answer. **Never claim priority you have not
established.**

---

## 4. Method questions

### 4.1 "Why fuzzy numbers? Why not just score 1–5?"

> Because appraisal judgements are linguistic and imprecise. An officer writing
> "management is sound" is not asserting exactly 75. A triangular fuzzy number
> carries that imprecision through the aggregation instead of discarding it at the
> first step.

**Expect the follow-up, and be honest:** *"Does it actually change your results?"*

> On the SBA validation, no — and I say so explicitly. Every SBA-observable
> criterion is quantitative, so each enters as a degenerate fuzzy number, and the
> fuzzy weighted average reduces exactly to an ordinary weighted mean. The fuzzy
> layer does no work on that dataset. It is exercised only by the 21 qualitative
> criteria, which SBA data does not contain.

Admitting this is much safer than being caught claiming a fuzzy model was
validated when it was not.

### 4.2 "Why Best-Worst Method instead of AHP?"

> Response burden. Full pairwise AHP over my criteria tree needs 168 comparisons
> per respondent — about an hour. Nobody completes that carefully, and the
> inconsistency from fatigue would make the weights worthless. BWM needs 2n−3 per
> level, which is 86 comparisons, about fifteen minutes, and it has a clean
> consistency ratio. Rezaei 2015 for the method, 2016 for the linear formulation
> I used.

### 4.3 "Why not just train a machine learning model?"

> Two reasons. First, many banks — including in Sri Lanka — do not have clean
> historical default data to train on, so a method that requires it is not
> available to them. Second, credit decisions must be explainable: under
> regulations like ECOA a lender has to state the specific reasons for declining,
> and guidance is explicit that model complexity is not an excuse. My system
> decomposes every score into per-criterion contributions that sum exactly to the
> total.

### 4.4 "Why do you refuse to combine the two objectives?"

> Because combining them destroys the information the structure exists to expose.
> A facility scoring 80 on credit and 40 on development, and one scoring 60 on
> both, are materially different propositions — a combined score of 60 makes them
> identical.
>
> It is not just my preference. Arvanitis, Stampini and Vencatachellum (2015)
> studied appraisal at the African Development Bank and found development and
> credit concerns are empirically **independent**. If they were correlated, a
> combined score would lose little. Because they are independent, aggregation
> discards real information.

### 4.5 "Why temporal validation?"

> Because random splitting puts loans from the same economic cycle on both sides,
> so the model is partly recalling conditions rather than generalising. The gap in
> my results is 0.182 AUC.
>
> The more striking result is that logistic regression fell to 0.4565 temporally —
> below chance. Trained on 1990–2003 at 9.1% default and tested on 2004–2010 at
> 35.9%, its ranking inverted. That is a practical warning: a scorecard fitted in
> benign conditions can rank borrowers backwards under stress. Given Sri Lanka's
> recent volatility, that matters here.

---

## 5. System questions

### 5.1 "Show me the system."

Have this sequence rehearsed and **practise it on the actual machine you will
use**:

1. Sign in as `officer` — point out that roles come from clause 7 of the form.
2. New appraisal → fill the header → **show the live score updating** as criteria
   are entered.
3. Point at the completeness gate while it is still withholding: *"It has a score
   but refuses to give a band, because too little has been assessed."*
4. Complete the file → **credit risk 80.2 band A, development impact 74.6 band
   B** — *"the same application, different on the two objectives. That divergence
   is the point."*
5. Save → show the contribution breakdown, each row citing a form clause.
6. Sign out, sign in as `headoffice`, approve → show the audit trail.
7. Export the DOCX → *"this is the bank's own form, filled in."*

**Run this end to end at least twice before the viva.** Use SQLite, offline. Do
not rely on a deployment.

### 5.2 "Anyone could type any name in your sign-off."

They could not, and this is worth knowing because it was true earlier:

> The signatory comes from the authenticated session, not a text field. Roles are
> enforced server-side, not just hidden in the interface — an officer calling the
> action directly still gets refused. And an approved or declined appraisal
> rejects further decisions; a correction means raising a new appraisal.

### 5.3 "Is this production-ready for a bank?"

**Say no. Confidently.**

> No, and the thesis says so in section 4.6a.1. It is a research prototype built
> to good engineering standards: input validation at trust boundaries, 62 tests,
> real authorisation, an audit trail, reproducible builds.
>
> A banking deployment would need password reset, multi-factor authentication,
> account lockout, sign-in rate limiting, a password policy, penetration testing,
> an accessibility audit, and a data-retention policy. None of those are present
> and I do not claim they are.

Overclaiming here is one of the easiest ways to lose credibility in a viva.

### 5.4 "Why two implementations of the scoring engine?"

> TypeScript for the system, Python for the analysis — pandas and scikit-learn
> have no real TypeScript equivalent. That is a genuine risk: if they drift, the
> thesis reports numbers from one implementation while the demonstration runs
> another. So there is a parity test that generates random appraisals, scores them
> through both, and fails on any disagreement. 280 checks, all passing.

---

## 6. The weak points — know them before they do

Volunteer these when relevant. An examiner who finds a limitation you have not
acknowledged assumes you did not notice.

| Weakness | How to answer |
|---|---|
| **No inter-rater reliability study** | "The most significant omission. My premise is that appraisal is inconsistent, and I support it from the literature — Cortés et al. (2016) show officers' approvals move with their mood, more so where discretion is high — but their setting is US residential mortgages, not SME appraisal, so it does not transfer automatically and I did not measure it myself. It is the first thing I would add, and the study is designed and written up ready to run: 4–6 officers, 8–10 constructed cases, Krippendorff's alpha, then the same cases through the system a week later to compare agreement before and after." |
| **Small or absent elicitation sample** | State the actual number. If zero: "RQ2 is unanswered. The instrument and analysis pipeline are built and tested — the Best-Worst solver is verified against an independent optimiser — but I did not obtain responses in the time available, and I report the weights as placeholders rather than presenting equal weights as elicited. The protocol for running it is written; what it needs is practitioners." |
| **Proxy dataset from another jurisdiction** | "Stated as the central limitation in section 1.6, before any results." |
| **Criteria tree not empirically validated** | "No dataset contains its variables. That is the methodological finding, not an oversight." |
| **Development objective barely observable** | "Only job creation and retention proxy it. Five of the nine clause-5 items have no counterpart in the data. It is a design contribution, not a validated one." |
| **No field evaluation** | "No officer has used it on live applications. There is no usability or acceptance evidence." |
| **The scorecard shows disparate impact** | Volunteer this before they find it. "It fails the four-fifths rule on four of five credit-access attributes, and it would decline 36.11% of creditworthy agricultural borrowers — the worst of any sector — while agriculture has the lowest default rate in the cohort at 19.19%. It penalises the sector that performs best. That is a defect in my own artefact and it is reported in §5.18 rather than left for someone else to find." |
| **Fairness is not tested on protected characteristics** | "It cannot be, on this data — the SBA file records no race, sex, age or disability field. What I tested are credit-access proxies. Passing on them establishes nothing about lawful discrimination, and I say so." |
| **Disparity ratios are min/max statistics** | "Which are biased upward in apparent severity. I quantified that rather than arguing it away: assigning declines at random, the measure reads 0.973 to 0.999. The observed values sit far below that floor, the bootstrap intervals are tight, and resampling names the same worst-affected group 89–100% of the time." |

---

## 7. Sources you re-read, and what changed

Five sources carrying load-bearing claims were obtained and read in full late in
the work. Three of them did not say quite what the thesis had said they said, and
all three corrections are now in the text. **This is a strength if you present it
as one and a disaster if you are caught not knowing it**, so learn these.

**Arvanitis, Stampini and Vencatachellum (2015) — the important one.**

> Q: "Your whole dual-objective design rests on their independence result. What
> did they actually find?"

> A: "A *positive but statistically non-significant* relationship — slope 0.048,
> p = 0.49 — across the 109 African Development Bank operations carrying both a
> development and a credit rating. They describe the factors as 'somewhat
> independent'. That is an underpowered null, not a demonstration of
> independence: 109 observations cannot separate independence from a moderate
> association. An earlier draft of this thesis treated it as established and I
> corrected that after reading the paper."

Then the payoff, which is the part that earns credit:

> "It also changes what my RQ4 result means. I found r = +0.40 across 652,284
> facilities and had written that up as *contradicting* them. It doesn't. Their
> point estimate was positive too. I measure the same direction at a sample size
> that can resolve it. The design decision survives, but the argument for it is
> now the 88.2% band-disagreement rate rather than an independence premise that
> was never established."

**Lessmann et al. (2015).** 41 classifiers across **seven** datasets, not eight —
the eight belongs to Baesens et al. (2003), which they update, and the thesis had
conflated the two. They report a *tendency* for homogeneous ensembles to lead,
not uniform superiority; rotation forests and dynamic ensemble selection perform
worse than plain logistic regression. Their data is retail credit, not SME.

**Cortés, Duchin and Sosyura (2016).** Holds exactly as cited, but the setting is
**US residential mortgages** from the confidential HMDA registry — not SME
lending, not Sri Lanka. If pressed on transferability: "It doesn't transfer
automatically. What supports the transfer is the direction of their own
cross-sectional result — the effect grows as decisions become more discretionary
and less automated, and a hand-completed narrative SME form is further along that
dimension than a residential mortgage. That's an argument, not an observation,
and the thesis says so."

**If asked why you did not read everything.** Be straight: 8 of 58 entries are
read in full, and they are the ones carrying substantive claims. The bibliography
marks every entry by status, including one — Beck and Demirgüç-Kunt (2006) — that
could not be obtained at all, where the claim resting on it was weakened to what
an unread citation can carry. Do not overstate this. The honest line is that the
reading is incomplete and the incompleteness is documented rather than hidden.

---

## 8. If you are asked about the interim submissions

If discrepancies between the interim reports and this thesis come up, the only
safe answer is a straight one:

> The interim figures were not produced by completed experiments. The results in
> this thesis are, and every one is regenerable by running the code in the
> repository.

Then stop. **Do not invent a methodology that produced the earlier numbers.** A
fabricated explanation under questioning is far worse than an awkward admission,
and examiners are practised at pulling on that thread. Everything in the final
work is real and reproducible — that is the ground you want to be standing on.

---

## 9. When you do not know

You will be asked something you cannot answer. The good response is short:

> I don't know. My guess would be X, but I haven't tested it, so I wouldn't want
> to claim it.

That is exactly the posture the thesis takes about the contamination mechanism,
and it is consistent. Bluffing is the failure mode — examiners ask follow-ups
precisely to find the edge of what you actually know, and a confident wrong answer
invites three more questions.

---

## 10. Numbers to memorise

| | |
|---|---|
| Criteria / dimensions / objectives | 49 / 7 / 2 |
| Quantitative / qualitative criteria | 28 / 21 |
| Completeness gate threshold | 60% |
| Linguistic scale | 5-point, triangular fuzzy, centroid defuzzification |
| BWM comparisons (vs AHP) | 86 (vs 168) |
| BWM consistency cut-off | CR > 0.25 excluded |
| SBA rows / usable / matured | 899,164 / 897,167 / 652,284 |
| Overall default rate | 17.56% |
| Roundness AUC | 0.889 |
| GBM temporal, with / without `Term` | 0.9461 / 0.6076 |
| Random vs temporal optimism | 0.182 AUC |
| Modulus 12 / 6 / 3 / 11 raw AUC | 0.8859 / 0.8600 / 0.7934 / 0.4660 |
| Objectives correlation (RQ4) | r = +0.40, or +0.36 disjoint-input |
| Bands disagree / by two or more | 88.2% / 38.4% |
| Weight sensitivity at ±25% | ρ = 0.9822, band stability 94.0% |
| Scorecard AUC, random / temporal | 0.4144 / 0.5275 |
| Four-fifths failures (scorecard / GBM) | 4 of 5 / 3 of 5 |
| Agriculture: creditworthy declined vs default rate | 36.11% vs 19.19% |
| Micro-firm equal-opportunity ratio | 2.81× |
| Withholding one field: scored less risky / flipped | 97.7% / 19.84% |
| No-information applicant | P = 0.0615 vs 0.2293 threshold — approved |
| Demo case scores | credit 80.2 (A), development 74.6 (B) |
| Tests | 89 unit, 280 parity checks, 62 claim checks |

---

## 11. The evening before

- Re-run everything: `npm test`, `python research/src/test_parity.py`,
  `python research/src/bwm.py`. Confirm green.
- Run the demo sequence twice, offline, on the machine you will use.
- Re-read Chapter 5 and section 2.7 — the two places examiners will push hardest.
- Read the six papers in the Chapter 2 bibliography. **Not the summaries.** If you
  cite a paper you have not read and are asked what it found, there is no recovery.
- Prepare one honest sentence for "what would you do differently?" —
  the inter-rater reliability study is the right answer.
