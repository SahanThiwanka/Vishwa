# Bibliography

**Verification status.** Every entry below was located by search and its
bibliographic details — authors, year, journal, volume, pages, DOI — checked
against at least one authoritative source. That is *not* the same as having read
the paper.

| Marker | Meaning |
|---|---|
| ✅ | Full text obtained and read |
| ◐ | Bibliographic details verified; abstract read; **full text not yet read** |
| ⬜ | Identified as relevant; details need confirming before citing |

**Before submission, every ◐ that is cited for a substantive claim must become
✅.** Citing a paper for what an abstract appeared to say is how a viva goes
wrong: an examiner asks what the paper actually found, and there is no recovery.

---

## 1. Credit scoring: foundations and reviews

◐ **Altman, E.I.** (1968) 'Financial Ratios, Discriminant Analysis and the
Prediction of Corporate Bankruptcy', *Journal of Finance*, 23(4), pp. 589–609.
doi:10.1111/j.1540-6261.1968.tb00843.x
> The origin of quantitative credit assessment. Multiple discriminant analysis
> over 22 ratios for 66 firms. Establishes that this study's approach — weighted
> financial ratios — is a sixty-year-old idea, which is part of why the novelty
> claim had to be narrowed.

◐ **Ohlson, J.A.** (1980) 'Financial Ratios and the Probabilistic Prediction of
Bankruptcy', *Journal of Accounting Research*, 18(1), pp. 109–131.
> Introduced conditional logit to the problem, moving from classification to
> probability. Relevant to §5.5 on calibration.

◐ **Hand, D.J. and Henley, W.E.** (1997) 'Statistical Classification Methods in
Consumer Credit Scoring: A Review', *Journal of the Royal Statistical Society
Series A*, 160(3), pp. 523–541.

◐ **Thomas, L.C., Crook, J.N. and Edelman, D.B.** (1992) *Credit Scoring and
Credit Control*. Oxford: Clarendon Press.

◐ **Thomas, L.C., Edelman, D.B. and Crook, J.N.** (2002) *Credit Scoring and its
Applications*. Philadelphia: SIAM.

◐ **Lessmann, S., Baesens, B., Seow, H.-V. and Thomas, L.C.** (2015)
'Benchmarking state-of-the-art classification algorithms for credit scoring: An
update of research', *European Journal of Operational Research*, 247(1),
pp. 124–136.
> 41 classifiers across 8 credit datasets. The reference point for what
> discrimination is achievable, and therefore for judging when a reported AUC is
> implausible.

◐ **Ciampi, F., Giannozzi, A., Marzi, G. and Altman, E.I.** (2021) 'Rethinking
SME default prediction: a systematic literature review and future perspectives',
*Scientometrics*, 126, pp. 2141–2188. doi:10.1007/s11192-020-03856-0
> 100+ articles over 34 years, co-authored by Altman. The anchor review for
> Chapter 2's SME section.

## 2. SME finance and access to credit

◐ **Beck, T. and Demirgüç-Kunt, A.** (2006) 'Small and medium-size enterprises:
Access to finance as a growth constraint', *Journal of Banking & Finance*,
30(11), pp. 2931–2943.

◐ **Berger, A.N. and Udell, G.F.** (2006) 'A more complete conceptual framework
for SME finance', *Journal of Banking & Finance*, 30(11), pp. 2945–2966.
> Identifies nine distinct SME lending technologies. Useful for situating the
> People's Bank instrument as *financial statement lending* combined with
> relationship elements.

◐ **Stein, J.C.** (2002) 'Information Production and Capital Allocation:
Decentralized versus Hierarchical Firms', *Journal of Finance*, 57(5),
pp. 1891–1921.
> The soft/hard information distinction. Directly relevant: this study is an
> attempt to *harden* soft appraisal information without discarding it, and Stein
> explains why that is difficult and what is lost.

⬜ Digitalisation and soft information in SME credit evaluation (Indian banks),
*Digital Finance*, doi:10.1007/s42521-023-00078-w

⬜ Enhancing credit risk assessments of SMEs with non-financial information,
*Cogent Economics & Finance* (2024), doi:10.1080/23322039.2024.2418910

## 3. Judgement, discretion and inconsistency in lending

◐ **Cortés, K.R., Duchin, R. and Sosyura, D.** (2016) 'Clouded judgment: The role
of sentiment in credit origination', *Journal of Financial Economics*, 121(2),
pp. 392–413.
> **The citation supporting this study's premise.** Officers' approvals move with
> mood (instrumented by sunshine), and the effect is larger where discretion is
> higher and review less automated.

✅ **SharafEldin, M.A., Idrees, A.M. and Ouf, S.** (2025) 'A Proposed Framework
for Loan Default Prediction Using Machine Learning Techniques', *International
Journal of Advanced Computer Science and Applications*, 16(6), pp. 412–425.
> Read. Uses Agricultural Bank of Egypt data, **not** SBA — recorded so it is not
> mistakenly cited as evidence for the contamination claim. Its framing that
> traditional assessment "relied on subjective judgment, leading to inconsistent
> decisions" supports the premise.

⬜ Rules versus discretion in loan rate setting, *Journal of Financial
Intermediation* (2011), doi:10.1016/j.jfi.2010.10.002

⬜ The loan officer's subjective judgment and its role in microfinance
institutions, *International Journal of Risk Assessment and Management*, 17(3),
2014, pp. 233–245

## 4. Multi-criteria decision making: methods

◐ **Zadeh, L.A.** (1965) 'Fuzzy sets', *Information and Control*, 8(3),
pp. 338–353.

◐ **Saaty, T.L.** (1980) *The Analytic Hierarchy Process*. New York: McGraw-Hill.

◐ **Saaty, T.L.** (1990) 'An exposition of the AHP in reply to the paper
"Remarks on the Analytic Hierarchy Process"', *Management Science*, 36(3),
pp. 259–268.

◐ **Chang, D.-Y.** (1996) 'Applications of the extent analysis method on fuzzy
AHP', *European Journal of Operational Research*, 95(3), pp. 649–655.
> Cite **with the criticism attached**: subsequent work shows extent analysis
> cannot recover true weights from a fuzzy comparison matrix and has been widely
> misapplied. Part of the justification for choosing BWM.

◐ **Chen, C.-T.** (2000) 'Extensions of the TOPSIS for group decision-making
under fuzzy environment', *Fuzzy Sets and Systems*, 114(1), pp. 1–9.

◐ **Rezaei, J.** (2015) 'Best-worst multi-criteria decision-making method',
*Omega*, 53, pp. 49–57. doi:10.1016/j.omega.2014.11.009
> **The method used in this study.**

◐ **Rezaei, J.** (2016) 'Best-worst multi-criteria decision-making method: Some
properties and a linear model', *Omega*, 64, pp. 126–130.
> The linear formulation implemented in `research/src/bwm.py`.

⬜ A discussion on extent analysis method and applications of fuzzy AHP,
*European Journal of Operational Research* (1999) — the critique of Chang

⬜ Best-worst multi-criteria decision-making method: A review of the literature,
*Socio-Economic Planning Sciences* (2025)

## 5. MCDM applied to credit and finance

✅ **Roy, P.K. and Shaw, K.** (2021) 'A multicriteria credit scoring model for
SMEs using hybrid BWM and TOPSIS', *Financial Innovation*, 7(1), article 77.
doi:10.1186/s40854-021-00295-5
> **READ IN FULL** (open access). **The nearest precedent, and the withdrawal it
> prompted is correct** — the paper does exactly what an earlier draft of this
> study claimed as novel: BWM for criteria weights, TOPSIS to score SME
> applicants, financial and non-financial criteria together. §2.5.3 withdraws the
> claim on this basis and the reading confirms the withdrawal rather than
> softening it.
>
> Detail that matters for positioning: **30 subcriteria**, finalised by a panel of
> **12 experts** (7 banking/SME lending, 5 from SMEs that had obtained credit);
> validated against a commercial rating agency on a case study of **31 SMEs**,
> reporting 90.32% accuracy and Type-II error 14.28% against the commercial
> model's 28.57%.
>
> They have the elicitation this study lacks. This study has a validation sample
> that can carry a conclusion — 31 firms means 90.32% accuracy is 28 of 31, and
> the reported Type-II rate is one or two cases. They also aggregate to a single
> TOPSIS closeness coefficient, where this study reports two objectives and
> refuses to combine them.

✅ **Gutiérrez-Nieto, B., Serrano-Cinca, C. and Camón-Cala, J.** (2016) 'A Credit
Score System for Socially Responsible Lending', *Journal of Business Ethics*,
133(4), pp. 691–701. doi:10.1007/s10551-014-2448-5
> **READ IN FULL** (author e-offprint, obtained via the FIR-PRI awards site).
> **The withdrawal it prompted is correct**: the paper does score social impact
> alongside financial variables, so §2.6.1's claim stands as withdrawn.
>
> Specifics: the method is **AHP** in absolute-measurement mode, not BWM — chosen,
> they say, largely because the algorithm was already in a spreadsheet and the
> analysts found it easy. Social outcomes are valued through **Social Return on
> Investment**. Weights come from the board of the lending cooperative, aggregated
> by geometric mean. Demonstrated on **one** real application, a bike courier
> company's loan request to the Spanish cooperative Coop57.
>
> They merge financial ratios and social indicators into a single assessment.
> That is the difference this study can still claim: two objectives kept apart,
> with §5.6b showing the separation changes the answer for 88.2% of facilities.

⬜ An integrated fuzzy credit rating model using fuzzy-BWM and fuzzy-TOPSIS-Sort-C,
*Complex & Intelligent Systems* (2022), doi:10.1007/s40747-022-00823-5

⬜ Developing a multi-criteria sustainable credit score system using fuzzy BWM
and fuzzy TOPSIS, *Environment, Development and Sustainability* (2021),
doi:10.1007/s10668-021-01662-z

⬜ A fuzzy decision support system for credit scoring, *Neural Computing and
Applications*, doi:10.1007/s00521-016-2592-1

⬜ A knowledge-informed neural network integrating fuzzy AHP and PCA for SME
credit risk assessment, *Scientific Reports* (2025), doi:10.1038/s41598-025-21441-4

## 6. Development finance and dual objectives

✅ **Arvanitis, Y., Stampini, M. and Vencatachellum, D.** (2015) 'Balancing
development returns and credit risks: project appraisal in a multilateral
development bank', *Impact Assessment and Project Appraisal*, 33(3), pp. 195–206.
doi:10.1080/14615517.2015.1041837
> **READ IN FULL, and this study had over-read it.** The text obtained and read
> is the African Development Bank working-paper version - Working Paper Series
> No. 186, November 2013, same three authors and same title in the form
> 'Evidence from the African Development Bank's Experience'. The journal version
> is paywalled and has not been compared line by line; nothing below depends on
> wording unique to it.
>
> What the paper actually reports: comparing development outcome ratings against
> credit risk ratings across the **109** operations carrying both, a **positive
> but statistically non-significant** relationship, **slope 0.048, p = 0.49**,
> which the authors read as the two factors being "somewhat independent". Their
> abstract generalises this to variables at appraisal being "rather independent
> from each other" with "no assumption ... made on one variable given information
> on the others".
>
> **This is an underpowered null, not a demonstration of independence.** n = 109
> cannot separate independence from a moderate association. The thesis originally
> cited it as an established independence result and justified the
> non-aggregation design on it; §2.6.2, §5.6b and §6.2 were corrected after this
> was read. Note also that the significant result in the same paper is a
> *different* pair - development outcomes against **additionality** (0.4 points
> per point, n = 121) - which is not the relationship this study relies on.
>
> Their measured association is positive, and §5.6b finds r = +0.40 on 652,284
> facilities. Same direction, resolvable sample. The finding here corrects the
> reading of this paper rather than contradicting the paper.

⬜ The Dual Nature of Multilateral Development Banks, Cambridge Elements

## 7. Explainability and regulation

◐ **Lundberg, S.M. and Lee, S.-I.** (2017) 'A Unified Approach to Interpreting
Model Predictions', *Advances in Neural Information Processing Systems 30*,
pp. 4765–4774.

◐ **Ribeiro, M.T., Singh, S. and Guestrin, C.** (2016) '"Why Should I Trust
You?": Explaining the Predictions of Any Classifier', *KDD '16*, pp. 1135–1144.
arXiv:1602.04938

⬜ CFPB Circular 2023-03, adverse action notification requirements and complex
algorithms

⬜ EU Artificial Intelligence Act — credit scoring as a high-risk application

⬜ FinRegLab, *Explainability in Credit Underwriting* (AI FAQs)

## 8. Data quality, leakage and reproducibility

◐ **Kapoor, S. and Narayanan, A.** (2023) 'Leakage and the reproducibility crisis
in machine-learning-based science', *Patterns*, 4(9), 100804.
doi:10.1016/j.patter.2023.100804
> Leakage across 17 fields affecting 294 papers; a taxonomy of eight types. The
> frame within which Chapter 5's finding sits.

✅ **Li, M., Mickel, A. and Taylor, S.** (2018) '"Should This Loan be Approved or
Denied?": A Large Dataset with Class Assignment Guidelines', *Journal of
Statistics Education*, 26(1), pp. 55–66. doi:10.1080/10691898.2018.1434342
> **READ IN FULL.** The dataset paper. Table 1 defines `Term` as "Loan term in
> months" — the quotation in §5.3.4 and in the paper is verbatim and correct.
> Table 1 also confirms the three post-outcome fields this study drops:
> `ChgOffDate` "the date when a loan is declared to be in default",
> `ChgOffPrinGr` "charged-off amount", `BalanceGross` "gross amount outstanding".
>
> **The reading produced a finding, §5.3.5.** In section 4.1.5 the authors derive
> a feature from `Term`: a dummy `RealEstate`, 1 where `Term` ≥ 240 months, and
> report default rates of 1.64% against 21.16%. Our cohort reproduces this at
> 1.45% against 20.69%, and the contrast turns out to be dominated by term
> roundness rather than by real-estate backing. This is not a criticism of the
> paper — it documents a teaching dataset and reasons soundly — but it shows the
> contamination reaching the dataset's own documentation.

⬜ Candidate studies reporting inflated results on this dataset — see
`docs/07-paper/affected-work-search.md`. **Must be obtained and read before
§VIII of the paper can name any of them.**

## 9. Evaluation methodology and statistics

◐ **DeLong, E.R., DeLong, D.M. and Clarke-Pearson, D.L.** (1988) 'Comparing the
areas under two or more correlated receiver operating characteristic curves: a
nonparametric approach', *Biometrics*, 44(3), pp. 837–845.
> The paired AUC test used in `statistical_tests.py`.

◐ **Hanley, J.A. and McNeil, B.J.** (1982) 'The meaning and use of the area under
a receiver operating characteristic (ROC) curve', *Radiology*, 143(1), pp. 29–36.

◐ **Brier, G.W.** (1950) 'Verification of forecasts expressed in terms of
probability', *Monthly Weather Review*, 78(1), pp. 1–3.
> The calibration score used in §5. What separates "ranks well" from "predicts
> well" is its decomposition, which is Murphy's rather than Brier's — see below.

◐ **Murphy, A.H.** (1973) 'A New Vector Partition of the Probability Score',
*Journal of Applied Meteorology*, 12(4), pp. 595–600.
doi:10.1175/1520-0450(1973)012<0595:ANVPOT>2.0.CO;2
> The reliability / resolution / uncertainty partition of the Brier score, which
> §5.13 and §4.6 both name as "Murphy's decomposition". It was named in the text
> with no source attached until this was audited; the attribution was being made
> to Brier (1950), which does not contain it.
> Bibliographic details confirmed against the AMS journal record, NASA ADS and
> Crossref, which agree. The abstract could not be retrieved (the publisher
> returns 403), so this is a details-verified entry, not an abstract-read one.

◐ **Cohen, J.** (1960) 'A coefficient of agreement for nominal scales',
*Educational and Psychological Measurement*, 20(1), pp. 37–46.

◐ **Landis, J.R. and Koch, G.G.** (1977) 'The measurement of observer agreement
for categorical data', *Biometrics*, 33(1), pp. 159–174.
> The interpretation thresholds (slight / fair / moderate / substantial / almost
> perfect) for the inter-rater study recommended in future work.

⬜ **Krippendorff, K.** *Content Analysis: An Introduction to Its Methodology*.
Sage — confirm edition and year before citing.

◐ **Sun, X. and Xu, W.** (2014) 'Fast Implementation of DeLong's Algorithm for
Comparing the Areas Under Correlated Receiver Operating Characteristic Curves',
*IEEE Signal Processing Letters*, 21(11), pp. 1389–1393.
> The algorithm actually implemented in `statistical_tests.py` — DeLong (1988)
> gives the test, this gives the O(n log n) computation of it. Volume, issue and
> pages confirmed against NASA ADS and the IEEE record.

## 10. Design science and system evaluation

◐ **Hevner, A.R., March, S.T., Park, J. and Ram, S.** (2004) 'Design Science in
Information Systems Research', *MIS Quarterly*, 28(1), pp. 75–105.
> **The methodological foundation of Chapter 3.** Currently cited implicitly;
> must be cited explicitly.

◐ **Peffers, K., Tuunanen, T., Rothenberger, M.A. and Chatterjee, S.** (2007) 'A
Design Science Research Methodology for Information Systems Research', *Journal
of Management Information Systems*, 24(3), pp. 45–77.
> The six-step process this study follows: problem identification, objectives,
> design, demonstration, evaluation, communication.

◐ **Davis, F.D.** (1989) 'Perceived Usefulness, Perceived Ease of Use, and User
Acceptance of Information Technology', *MIS Quarterly*, 13(3), pp. 319–340.

◐ **Brooke, J.** (1996) 'SUS: A "quick and dirty" usability scale', in Jordan,
P.W. et al. (eds.) *Usability Evaluation in Industry*. London: Taylor & Francis,
pp. 189–194.
> For the usability evaluation listed as future work.

## 11. Sri Lankan context

⬜ **Ministry of Industry and Commerce, Sri Lanka**, *National Policy Framework
for SME Development* — sed.gov.lk
> Source of the SME definition used. Sri Lanka had no uniform SME definition
> before 2015, which matters for interpreting any national statistics.

⬜ **Institute of Policy Studies of Sri Lanka**, *Banking on SME Growth: Concepts,
Challenges and Policy Options to Improve Access to Finance in Sri Lanka*

⬜ **Central Bank of Sri Lanka**, *Annual Report* — SME credit volumes, NPL ratios

⬜ **World Bank**, *Enterprise Surveys: Sri Lanka* — firm-level access-to-finance
data

⬜ **Asian Development Bank**, *Small and Medium-Sized Enterprises Line of Credit
Project* (Sri Lanka), project 49273-001

### Figures located, sources to confirm

SMEs reportedly account for **75% of active enterprises, 45% of employment and
52% of GDP** in Sri Lanka, with the MSME count projected to rise from 1.1m (2024)
to 1.4m by 2030. **Attribute these to a primary source before use** — they
currently rest on secondary reporting, and Chapter 1 should not cite a figure
whose origin has not been checked.

---

## Status

| | Count |
|---|---:|
| ✅ read in full | 1 |
| ◐ details verified, abstract read | 30 |
| ⬜ identified, needs confirming | 19 |
| **Total** | **50** |

The ⬜ entries are real and relevant; they need a library session to confirm
details and obtain full text. Priority for that session, in order:

1. ~~Roy & Shaw (2021) and Gutiérrez-Nieto et al. (2016)~~ — **done.** Both read
   in full. Both withdrawals stand, and the readings sharpened the positioning
   rather than changing it.
2. ~~Arvanitis et al. (2015)~~ — **done.** Read in full; the thesis's reading of
   it was wrong and has been corrected. See the entry above.
3. Cortés et al. (2016) — the premise citation.
4. Kapoor & Narayanan (2023) — for the leakage taxonomy classification.
5. Li, Mickel & Taylor (2018) — the `Term` definition, quoted in the paper.
6. The candidate affected studies in `affected-work-search.md`.

Everything else can be cited from verified bibliographic details for context,
but nothing load-bearing should rest on an unread source.
