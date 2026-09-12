# Your next steps

Everything that could be done at a keyboard has been done. What remains needs a
person: officers who will answer questions, a library login, a deployment
account, and two decisions.

This is written to be worked through in order. Each item says what to do, what to
send, and what happens afterwards.

---

## Priority order

| | Task | Your time | Why this order |
|---|---|---|---|
| 1 | Recruit officers for the weight elicitation | ~3 hours total | Unblocks RQ2. Every score the system produces currently carries a PLACEHOLDER warning. |
| 2 | Request 7 papers from the library | ~20 min to request | Three of the eight already read needed corrections. This is a correction-finding exercise, not box-ticking. |
| 3 | Inter-rater reliability study | ~2 days spread over 2 weeks | The strongest evidence the thesis could still gain. |
| ~~4~~ | ~~Deploy to Vercel~~ | **DONE** | Live at `https://vishwa-ten.vercel.app` |
| 5 | Usability evaluation | ~4 hours | Removes "no field evaluation". |
| 6 | Two decisions (below) | minutes | Only you can make them. |

If you can only do one thing, do **task 1**.

**Task 4 is done.** The instrument is live at
`https://vishwa-ten.vercel.app/elicitation`, needs no account, and works on a
phone. Setup is closed, an administrator account exists, and further accounts
are created from the Accounts page while signed in.

Before sending that link to anyone, complete one run yourself under the code
`TEST-DELETE`. Two reasons: you will know exactly what you are asking an officer
to spend twenty minutes on, and it proves submissions are reaching the database.
Check `/api/health` afterwards — `elicitationResponses` should read 1. The row is
safe to leave; `derive_weights.py` excludes anything starting `TEST-` and says so
when it does.

---

## Task 1 — Weight elicitation

**You need 5–8 loan or credit officers.** Your friend works at a bank, so this is
the most achievable item on the list. Colleagues, branch contacts, anyone who
appraises SME facilities. They do not need to be from People's Bank.

**Time per person: about 20 minutes.** No preparation needed on their side.

### What to send them

> Hi [name] — I'm doing an MSc research project on how SME loan appraisal
> decisions are made, and I need about 20 minutes of help from people who
> actually do the job.
>
> It's a short online exercise: you pick which factors matter most and least when
> you're judging a facility, and rate the others against them. No preparation, no
> right answers, and nothing about any real customer.
>
> It's anonymous — I record a code, not your name.
>
> Link: https://vishwa-ten.vercel.app/elicitation
>
> Could you spare 20 minutes this week?

### Running it

Full detail is in `docs/PROTOCOLS.md` §3. The essentials:

- Give each person a code: **R01, R02, R03…** Do not use anything starting
  `TEST`, `PILOT` or `DEMO` — those are filtered out of the analysis.
- Do not sit and watch, and do not react to their answers. If they ask whether an
  answer is right, say *"there's no right answer, I'm recording how you weigh
  it."*
- Note anyone who finishes in under eight minutes — they may have clicked
  through, and you will check their consistency score afterwards.

### When you have the responses

```bash
python research/src/derive_weights.py
```

That shows each person's consistency score without changing anything. Then:

```bash
python research/src/derive_weights.py --apply
```

That writes the real weights into the model and flips the status from
PLACEHOLDER to ELICITED. **Then re-run everything downstream**, because the
weights feed the scores:

```bash
python research/src/benchmark.py
python research/src/weight_sensitivity.py
python research/src/objective_independence.py
python research/src/fairness_analysis.py
python scripts/verify_claims.py
```

The last command will tell you which chapters no longer match the new numbers.
**Send me the output and I will update the thesis.** Do not hand-edit figures.

Expect the numbers to move slightly. §5.16 predicts the conclusions will not
change much; confirming or refuting that is itself a result.

---

## Task 2 — Seven papers from the library

You do **not** need all 28 unread sources. Most are cited only for naming a
method — nobody is going to challenge that Zadeh invented fuzzy sets. These seven
are cited for a *claim*, which is where a misreading does damage.

Ask NSBM's library for these. Most universities have inter-library loan or a
publisher subscription; the librarian will know. Send the list as-is.

| # | Full citation | Why |
|---|---|---|
| 1 | Berger, A.N. and Udell, G.F. (2006) 'A more complete conceptual framework for SME finance', *Journal of Banking & Finance*, 30(11), pp. 2945–2966 | §2.3 says they identify **nine** SME lending technologies and positions this study's instrument inside their framework |
| 2 | Stein, J.C. (2002) 'Information Production and Capital Allocation', *Journal of Finance*, 57(5), pp. 1891–1921 | §2.3 builds the thesis's "central tension" on his hard/soft information argument |
| 3 | Ciampi, F. et al. (2021) 'Rethinking SME default prediction', *Scientometrics*, 126, pp. 2141–2188 | §2.3 attributes specific counts to it — 100+ articles, 34 years, five research streams |
| 4 | Beck, T. and Demirgüç-Kunt, A. (2006) 'Small and medium-size enterprises: Access to finance as a growth constraint', *Journal of Banking & Finance*, 30(11), pp. 2931–2943 | **Could not be obtained at all.** No abstract is published anywhere. The claim resting on it was weakened as a result |
| 5 | Rezaei, J. (2015) 'Best-worst multi-criteria decision-making method', *Omega*, 53, pp. 49–57 | The method this study uses. The consistency-index table comes from here |
| 6 | Rezaei, J. (2016) 'Best-worst method: some properties and a linear model', *Omega*, 64, pp. 126–130 | The exact formulation implemented in the code |
| 7 | Chang, D.-Y. (1996) 'Applications of the extent analysis method on fuzzy AHP', *EJOR*, 95(3), pp. 649–655 | Cited **with a criticism attached**, and that criticism needs checking before it stands |

Also worth requesting if easy, for the paper rather than the thesis:

- Zhou et al. (2023) 'Machine Learning Approach for Small Business Loan Default Prediction'
- 'Ensemble-Based Machine Learning Algorithm for Loan Default Risk Prediction', *Mathematics*, 12(21), 3423

**When you get them, send them to me.** I will read them, check what the thesis
claims against what they say, and correct anything that is wrong — the same as
was done for the eight already read, three of which needed correcting.

### Also ask about database access

Ask whether NSBM gives you **Scopus, Web of Science or IEEE Xplore**. The paper
describes its search for affected published work as systematic, and no proper
database search has been run. If you get access, tell me and I will run it.

---

## Task 3 — Inter-rater reliability

This is the study that would most strengthen the argument, because the thesis's
whole premise is that manual appraisal is inconsistent — and right now that is
borrowed from a study of **US home loans**, not SME lending.

Full protocol: `docs/PROTOCOLS.md` §4. Shape of it:

1. **4–6 officers**, each appraising the **same 8–10 case files**, separately.
2. They must not discuss the cases. If two officers talk, both readings are lost.
3. Include **3–4 genuinely marginal cases** — those carry the study. Everyone
   agrees on the obvious ones.
4. A week later, the **same officers score the same cases through the system**.

Step 4 is the point. Comparing agreement before and after is the strongest
evidence the artefact could have. If agreement does not improve, that is a real
negative result and it goes in the thesis too — say so to yourself now, before
you see the data.

**I can build the 8–10 case files for you** from the People's Bank form
structure, with a designed mix of clear and marginal cases. Ask and I will.

---

## Task 4 — Deploy

Follow `docs/DEPLOYMENT.md` — it is step-by-step and current. You need:

- a **Neon** account (free tier) for the PostgreSQL database
- a **Vercel** account (free tier)
- a **GitHub** account to push the repository to

Roughly an hour if the accounts are new. Do this before task 1 if you can, so
officers can complete the elicitation from their own device.

**Do not put real customer data into the deployed system.** It is a research
prototype, the weights are placeholders, and every page says so.

---

## Task 5 — Usability evaluation

`docs/PROTOCOLS.md` §5. Five officers, about 45 minutes each, no training given.

One instruction that looks odd and is deliberate: **stop them halfway through
entering the criteria and ask what the system is telling them.** That tests
whether the completeness gate — the refusal to issue a band on thin evidence —
actually communicates what it is for. It is the design decision the thesis argues
hardest for, and nobody outside this project has ever looked at it.

---

## Task 6 — Two decisions only you can make

### The interim reports

The uploaded interim reports state that 1,250 loan applications were obtained
from a partnering Sri Lankan commercial bank under a formal data-sharing
agreement. The thesis states there is no such data and that validation used a
public US dataset.

Both documents are with the university. Anyone reading them together will find
this immediately, and a viva is exactly where that happens.

You have said not to worry about it, and I have not. But the options are worth
stating plainly:

- **Tell the supervisor before submission**, framed as the interim being written
  ahead of work that was not completed as planned. Awkward, survivable, and it is
  your choice of timing rather than an examiner's.
- **Say nothing** and prepare an answer. `docs/VIVA-PREPARATION.md` §8 has the
  only safe one, which is a straight admission that the interim figures were not
  produced by completed experiments. **Do not invent a methodology for them under
  questioning** — that is much worse than the original problem.

This is your call and your friend's, not mine. But do not be surprised by it.

### Where to send the paper

The contamination finding is now considerably stronger than when the venue note
was written — it is present in the SBA's own 2026 publication across a million
resolved facilities and twenty years, not just in one teaching dataset.

Options, in `docs/07-paper/paper-term-contamination.md`:

- A Sri Lankan IEEE conference (ICIIS, ICAC, ICTer) — fastest
- A data-quality or reproducibility venue — best fit for what the finding is
- *Journal of Statistics and Data Science Education* — published the original
  dataset paper, and the finding bears directly on its use in teaching

Tell me which and I will reformat to that venue's template.

---

## What to send me

Anything from this list, and I will do the rest:

- Elicitation responses collected → I update RQ2 and every affected chapter
- PDFs of the seven papers → I check them and correct the text
- Database access → I run the systematic search
- Reliability or usability data → I write up the results
- A venue choice → I reformat the paper
- "Build me the case files" → I build them

The repository stays verifiable throughout: `python scripts/verify_claims.py`
checks every load-bearing number in the thesis against the generated results, and
CI runs it on every push. If something drifts, it fails loudly rather than
quietly.
