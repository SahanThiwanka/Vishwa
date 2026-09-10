# Field Protocols

Three studies remain undone, and all three are blocked on people rather than on
analysis. This document exists so that none of them still needs *designing* when
people become available — each is written to be run as it stands.

They are listed in priority order. If only one can be done, do the first.

| # | Study | People needed | Time per person | What it unlocks |
|---|---|---|---|---|
| 1 | Weight elicitation | 5–8 loan officers | ~20 min | RQ2; removes `PLACEHOLDER` from every score in the thesis |
| 2 | Inter-rater reliability | 4–6 officers | ~90 min | The study's own premise, currently taken from literature |
| 3 | Usability evaluation | 5 officers | ~45 min | Any claim that the artefact is usable by its intended user |

**Before running any of them, check NSBM's research-ethics requirements.** This
document sets out the study design and the participant-facing wording; it does
not and cannot substitute for whatever approval your institution requires. If
approval is needed, the consent wording in §2 is written to be submitted with
the application.

---

## 1. What all three share

**Participants.** Credit or appraisal officers who assess SME facilities. Branch
officers are the intended users of the artefact; head-office credit staff are
acceptable and should be recorded separately, because their judgement is formed
under different constraints.

**Anonymity.** No participant is identified in any output. Each is assigned a
code — `R01`, `R02`, … — at the point of consent, and only the code is stored.
Do not record names anywhere that reaches the repository. The elicitation
instrument stores only the code, years of experience, institution and role.

**Use `R01`, `R02`, … and nothing else.** `derive_weights.py` excludes any code
beginning `TESTDATA`, `TEST-`, `PILOT` or `DEMO`, case-insensitively, so that a
pilot run cannot be aggregated into real weights. It prints what it excluded
rather than dropping it silently, but a real participant coded that way would
still be lost from the analysis. Sequential codes avoid the question entirely.

**Recording.** Written notes only unless a participant explicitly consents to
audio. Nothing in these three studies requires a recording.

**Withdrawal.** A participant may stop at any point and have their data removed.
For elicitation this means deleting their rows from `ElicitationResponse`; for
the other two, destroying their sheets. Say so before starting, and mean it.

---

## 2. Consent wording

Read aloud or hand over; keep one signed copy per participant.

> I am conducting research for an MSc at NSBM Green University on how SME loan
> appraisal decisions are made and whether the process can be supported by a
> structured tool.
>
> I would like to ask you to [complete a short comparison exercise / appraise a
> small number of anonymised case files / use a prototype system and tell me
> what you think of it]. It will take about [20 / 90 / 45] minutes.
>
> There are no right or wrong answers, and nothing here is a test of you. I am
> interested in how experienced officers weigh things up, and disagreement
> between officers is a finding rather than a problem.
>
> Your name will not be recorded. You will be given a code, and only that code
> appears in any analysis. I will not report anything that identifies you or
> your branch. The results will appear in a thesis and possibly an academic
> paper, in aggregate form.
>
> You can stop at any time, and you can ask me to destroy your responses
> afterwards without giving a reason.
>
> The case files used are constructed or anonymised. Please do not tell me
> anything about a real customer.
>
> Do you have any questions? Are you willing to take part?

That last instruction is not a formality. An officer describing a real applicant
turns an anonymous study into one holding customer data, with consequences for
you and for them.

---

## 3. Study 1 — Weight elicitation (RQ2)

### 3.1 What it is

The criteria tree has 49 criteria but no evidence about their relative
importance. Every score in the thesis is currently computed with equal weights
inside each dimension, flagged `PLACEHOLDER`. This study replaces that with
weights derived from practitioner judgement using the Best-Worst Method.

### 3.2 Participants

**Target 5–8; do not stop below 5.** Below five, one atypical respondent moves
the aggregate enough that reporting it as "practitioner weights" would overstate
what you have. Between five and eight is where published BWM studies typically
sit, and it is defensible.

Record for each: years of experience, institution, role. Report the range in the
thesis. If you get fewer than five, report the number honestly and treat the
result as indicative — §5.16's sensitivity analysis already bounds how much the
weights matter, so a thin sample is not fatal to the thesis.

### 3.3 Setup

1. Deploy the system, or run it locally and put the machine in front of the
   participant (`npm run dev`, then `/elicitation`).
2. The elicitation route **does not require an account** — that is deliberate, so
   a participant never handles a credential.
3. Assign the next code in sequence. Write it on the consent form.

### 3.4 The session

The instrument has **eight sections and 86 comparisons** in total:

| Section | Compares | Comparisons |
|---|---|---|
| 1 | The six credit-risk dimensions against each other | 9 |
| 2 | Borrower & management — 6 criteria | 9 |
| 3 | Credit conduct — 5 criteria | 7 |
| 4 | Historic financials — 9 criteria | 15 |
| 5 | Project viability — 8 criteria | 13 |
| 6 | Market position — 7 criteria | 11 |
| 7 | Risk & security — 6 criteria | 9 |
| 8 | Development impact — 8 criteria | 13 |

Each section asks the same three things: which item is **most** important, which
is **least** important, then two sets of 1–9 ratings against those two anchors.

**Script for the first section**, then let them proceed:

> On this screen you'll see the six areas the appraisal form covers. First, pick
> the one you think matters most when you're deciding whether a facility is
> sound. Then pick the one that matters least — least important of the six, not
> unimportant.
>
> Then you'll rate the others against those two. A 1 means "equally important", a
> 9 means "very much more important". Most answers land in the middle.
>
> Answer as you actually weigh things, not as the manual says you should.

**What not to say.** Do not suggest an answer, do not react to their choices
("interesting", "really?"), and do not explain what the model does with the
numbers. If asked whether an answer is right: *"There's no right answer — I'm
recording how you weigh it."*

**Time.** Budget 20 minutes. If someone is rushing in under eight, they are
probably clicking through; note it, and check their consistency ratio afterwards.

### 3.5 Afterwards

```bash
python research/src/derive_weights.py           # dry run, shows CR per level
python research/src/derive_weights.py --apply   # writes into the criteria tree
```

`--apply` flips `weightStatus.state` from `PLACEHOLDER` to `ELICITED` and records
the respondent codes. `verify_claims.py` enforces the consequence: with elicited
weights in place, any chapter still saying "PLACEHOLDER" fails the build.

**Consistency.** Responses with CR > 0.25 are excluded, not averaged in. Report
how many were excluded and why. Do not quietly drop them — a study that discards
respondents without saying so is not reporting its sample.

**Then re-run everything downstream**, because the weights feed the scorecard:

```bash
python research/src/benchmark.py
python research/src/weight_sensitivity.py
python research/src/objective_independence.py
python research/src/fairness_analysis.py
python scripts/verify_claims.py
```

Expect the numbers to move. That is the point. Update the chapters to whatever
the re-run produces — **do not** keep the placeholder-weight figures because they
read better.

### 3.6 What to write

§6.1 currently explains that elicitation was prepared but not administered.
Replace it with: how many respondents, their experience range, how many were
excluded for inconsistency, the derived dimension weights, and how far they
differ from equal weighting. Then state whether the conclusions changed — §5.16
predicts they will not move much, and confirming or refuting that prediction is
itself a result.

---

## 4. Study 2 — Inter-rater reliability

### 4.1 Why this is the most important one for the argument

The thesis is premised on manual appraisal being inconsistent between officers.
That premise is currently supported entirely from the literature — Cortés et al.
(2016), whose evidence is US residential mortgages rather than SME appraisal.
An examiner is entitled to ask whether the problem exists in the setting the
study addresses. This measures it.

### 4.2 Design

**4–6 officers each appraise the same 8–10 case files, independently.**

Independence is the whole study. If two officers discuss a case, both readings
are lost. Run them in separate sittings or separate rooms, and collect each set
of sheets before any discussion.

**Cases.** Construct 8–10 files from the People's Bank form structure. Vary them
deliberately:

- 2–3 that should be clear approvals
- 2–3 that should be clear declines
- **3–4 genuinely marginal** — thin collateral against strong cash flow, a
  first-time borrower in a strong sector, good ratios in a declining market

The marginal cases carry the study. Everyone agrees on the obvious ones, and
agreement on obvious cases tells you nothing.

Anonymise or construct. Do not use identifiable real files.

### 4.3 What each officer records, per case

1. An overall recommendation: **approve / approve with conditions / decline**
2. A confidence rating, 1–5
3. If your scale permits it, a credit score out of 100
4. Free text: the two or three factors that decided it

Item 4 matters more than it looks. If officers reach the same verdict for
different stated reasons, that is a distinct and reportable finding.

### 4.4 Analysis

| Measure | For | Interpretation |
|---|---|---|
| **Krippendorff's α** | The recommendation across all raters | Handles >2 raters and missing values; the right default here |
| **Fleiss' κ** | Same, if you prefer a more familiar statistic | Requires all raters on all cases |
| **ICC(2,k)** | The 0–100 score, if collected | Two-way random effects, absolute agreement |
| **Pairwise Cohen's κ** | Officer-to-officer | Shows whether one rater is the outlier |

Landis and Koch's bands — slight / fair / moderate / substantial / almost perfect
— are the conventional interpretation and are already in the bibliography.

**Be honest about power.** Four raters on eight cases is a small study. It can
show that disagreement is substantial; it cannot precisely estimate how
substantial. Report the point estimate with a confidence interval and resist the
temptation to describe a wide interval as a precise finding. This is the same
discipline §5.18 applies to the disparity ratios.

### 4.5 The second half — and the reason to do this properly

Once the manual round is complete and collected, have the **same officers score
the same cases through the system**, at least a week later so they are not
reproducing their own notes from memory.

Then compare agreement before and against after. If structured scoring raises
agreement, that is the strongest possible evidence for the artefact and it is
currently entirely absent from the thesis. If it does not, that is a real
negative result and belongs in Chapter 6 next to the scorecard's failure.

Either outcome is worth having. Design it so both are reportable, and decide the
analysis before seeing the data.

---

## 5. Study 3 — Usability evaluation

### 5.1 Participants

**Five officers.** Five is the conventional number for detecting the majority of
usability problems, and this is a problem-finding study, not a measurement study.
Do not use participants from Study 2 if avoidable — they have seen the cases.

### 5.2 Tasks

Give each participant the system and a constructed case file, with no training
beyond "here is the system, here is a file". Ask them to think aloud.

1. Sign in and create a new appraisal.
2. Enter the general information and borrower details from the file.
3. Enter the financial criteria.
4. **Stop deliberately at roughly half the criteria and ask what the system is
   telling them.** This tests the completeness gate — the design decision
   §5.19 argues hardest for. Do they understand that no band has been issued,
   and why?
5. Complete the remaining criteria and reach a recommendation.
6. Ask them to explain the score to you as if you were the applicant. This tests
   whether the per-criterion contributions are actually usable as an
   explanation, which is a claim the thesis makes.
7. Record a decision and export the report.

### 5.3 Measures

- **System Usability Scale** (10 items, standard wording) — gives a comparable
  number, and Brooke's original is in the bibliography.
- **Task completion**: completed unaided / completed with a prompt / not
  completed.
- **Time on task**, against the ~45 minutes the form currently takes by hand.
- **Every point of confusion**, verbatim. This is the most useful output and the
  one most often discarded.

### 5.4 What to report

SUS gives a single number and is easy to over-read on five participants. Report
it with the count, and lead with the qualitative findings. "Four of five
participants did not initially understand why no band had been issued" is worth
more to this thesis than a mean SUS score, because it bears directly on whether
the completeness gate communicates what it is for.

---

## 6. Order and time budget

| | Elapsed | Why this order |
|---|---|---|
| Study 1 | ~3 hours across 5–8 people | Highest value per hour; unblocks RQ2 and needs no case construction |
| Study 2 | ~1 day to construct cases, then ~90 min × 4–6, twice | Highest value to the argument; the before/after design needs a week's gap |
| Study 3 | ~4 hours across 5 people | Depends on nothing; can run in parallel with the gap in Study 2 |

If time collapses to a single afternoon, run Study 1. It is the one whose absence
currently propagates a `PLACEHOLDER` warning through every score the system
produces.

---

## 7. What each study changes in the thesis

| Study | Sections to rewrite |
|---|---|
| 1 | §6.1 (prepared, not administered), §5.7 (status of the weights), the model card's weights section, and every figure downstream of a re-run |
| 2 | §2.4 and §1.2 — the premise stops being borrowed from a different lending context and becomes measured in this one. New results section. |
| 3 | New section in Chapter 5; removes "no field evaluation" from the weaknesses table in the briefing and the viva document |

All three appear in `docs/SUPERVISOR-BRIEFING.md` §5 as known weaknesses. Each
one completed removes a row from that table, and the rows are there precisely so
a supervisor can see what is missing without having to find it.
