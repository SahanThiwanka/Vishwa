# DECLARATION

I declare that the content of this thesis, titled *A Dual-Objective Decision
Support Model for SME Credit Appraisal in Sri Lankan Development Banking*, is my
own work, and that it does not incorporate without acknowledgement any material
previously submitted for a degree or diploma at any university or other
institution of higher learning.

Where the work of others has been used, it is acknowledged in the text and listed
in the references. The datasets, source code and analysis scripts that produced
every quantitative result reported here are included with this submission.

&SPACE;

Signature: ...................................................

Name: A. A. V. Athukorala

Date: ...........................

&SPACE;

&SPACE;

I certify that this thesis was prepared under my supervision, and that it is of a
standard suitable for examination.

&SPACE;

Signature: ...................................................

Name: Dr. Pabudi Abeyrathne

Date: ...........................

Principal Supervisor

Senior Lecturer, Department of Computing and Information Systems

NSBM Green University

<<<PAGEBREAK>>>

# ACKNOWLEDGEMENT

I thank my supervisor, Dr. Pabudi Abeyrathne, for guidance throughout this
research, and in particular for the latitude to revise the study's direction when
the literature and the available data made the original scope untenable.

I am grateful to People's Bank for the appraisal instrument that forms the
foundation of this work. The *Project / Business Appraisal Report for SME Credit
Facility* is a carefully constructed document, and the analysis here rests
entirely on the institutional expertise embedded in it.

I acknowledge the authors of the SBA National dataset for placing it in the
public domain. The principal finding of this thesis is a caution about
that dataset, and it could not have been made had they not published it. Making
data open invites exactly this kind of scrutiny, and the field is better for it.

Finally, I thank the Faculty of Computing at NSBM Green University for the
research environment in which this work was carried out.

<<<PAGEBREAK>>>

# ABSTRACT

Small and medium enterprises account for an estimated 75% of enterprises, 45% of
employment and 52% of GDP in Sri Lanka, yet access to formal credit remains a
binding constraint. Appraisal at People's Bank uses a seven-section instrument
requiring thirteen financial ratios, cover ratios, a competitive-forces analysis
and nine developmental outcomes, and then asks the officer to certify viability
without stating any procedure for combining that evidence.

This study formalises that narrative instrument into a computable multi-criteria
model of 49 criteria across seven dimensions and two objectives, every criterion
traceable to a numbered clause of the source form. Quantitative criteria map
through piecewise-linear bands; qualitative criteria are captured on a five-point
linguistic scale as triangular fuzzy numbers. A working decision-support system
implements the model, scoring credit risk and development impact separately,
decomposing each score into exact per-criterion contributions, withholding a
recommendation when too little has been assessed, and exporting results in the
bank's own report format. Criterion weights were elicited from ten credit
practitioners by the Best-Worst Method, three of eighty level-responses being
excluded for inconsistency. Practitioners weight forward-looking project
viability above historic financial performance by more than two to one,
inverting the emphasis of an instrument whose longest section is the historic
financial analysis.

Empirical validation used the SBA National dataset of 899,164 loan guarantees,
and produced an unanticipated principal finding: the dataset's *Term* field
carries outcome information. Whether the term is a multiple of twelve, a
property with no economic content, predicts default at AUC 0.889 within every
approval year from 1990 to 2010, and excluding the field reduces
gradient-boosting temporal discrimination from 0.9461 to 0.6076 (p < 0.001). The
artefact is not confined to that file. It is present in the SBA's own loan-level
FOIA extracts published in June 2026, across 1,032,317 resolved facilities and
twenty consecutive approval years, and absent from the 504 programme whose terms
are fixed by programme design. The mechanism is narrowed to a process acting on
7(a) records but is not fully established, and is reported as such. A scorecard
built from dataset-observable proxies failed to discriminate (AUC 0.41-0.53),
supporting the methodological conclusion that instrument-specific appraisal
models cannot be validated on datasets lacking their variables.

Three further results concern automated credit assessment generally. Both a
gradient booster and a median-imputing logistic regression score information the
applicant withheld as *favourable* instead of as unknown: omitting a single
field moves 19.84% of applicants from decline to approval, and an applicant
supplying nothing at all is approved outright. Subgroup analysis across
credit-access proxies finds the expert scorecard failing the four-fifths rule on
four of five attributes and declining 36.11% of creditworthy agricultural
borrowers, the worst rate of any sector, though agriculture defaults least; the
dataset records no protected characteristic, so no claim about lawful
discrimination follows. And calibration degrades roughly 700-fold across a
temporal boundary while discrimination falls far less, so a model may continue
to rank while systematically mispricing risk. The proposed model's own output
proves more stable: the elicited weights depart from the equal weighting used
during development by up to 79% within a level, three times the perturbation a
prior sensitivity analysis had tested, yet rank correlation between the two
scorings is 0.91 and 0.97 and no appraisal moves two risk bands. The two
objectives assign the same facility different risk bands 88.2% of the time,
which is the argument for reporting them separately.

**Keywords:** SME credit appraisal, multi-criteria decision analysis, fuzzy sets,
decision support systems, data leakage, algorithmic fairness, missing data,
development banking

<<<PAGEBREAK>>>

# LIST OF ABBREVIATIONS

| Abbreviation | Meaning |
|---|---|
| AHP | Analytic Hierarchy Process |
| AUC | Area Under the Receiver Operating Characteristic Curve |
| BWM | Best-Worst Method |
| CI | Confidence Interval |
| CR | Consistency Ratio |
| DSCR | Debt Service Cover Ratio |
| FOIA | Freedom of Information Act (United States) |
| FY | Fiscal Year |
| GDP | Gross Domestic Product |
| ISCR | Interest Service Cover Ratio |
| LIME | Local Interpretable Model-agnostic Explanations |
| MCDM | Multi-Criteria Decision Making |
| ROC | Receiver Operating Characteristic |
| ROI | Return on Investment |
| SBA | United States Small Business Administration |
| SHAP | SHapley Additive exPlanations |
| SME | Small and Medium Enterprise |
| TFN | Triangular Fuzzy Number |
| TOPSIS | Technique for Order Preference by Similarity to Ideal Solution |
