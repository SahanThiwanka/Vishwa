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
employment and 52% of gross domestic product in Sri Lanka, yet access to formal
credit remains a binding constraint. Appraisal at People's Bank uses a
seven-section instrument requiring thirteen financial ratios, a
competitive-forces analysis and nine developmental outcomes, then asks the
officer to certify viability without stating how to combine that evidence.

This study formalises that instrument into a computable, explainable
multi-criteria model, and establishes what public data can and cannot validate
about such a model. The form was examined clause by
clause and expressed as 49 criteria across seven dimensions and two objectives,
each traceable to a numbered clause. Quantitative criteria map
through piecewise-linear bands and qualitative criteria through a five-point
linguistic scale represented as triangular fuzzy numbers. A working system implements it,
scoring credit risk and development impact separately. Weights were elicited from eleven credit
practitioners by the Best-Worst Method, and the scoring method was benchmarked
against the SBA National dataset of 899,164 loan guarantees.

Practitioners weight forward-looking project viability above historic financial
performance by more than two to one, inverting the emphasis of the source form. Scoring proved robust
to that change: rank correlation against equal weighting is 0.90 for credit risk and 0.97 for development impact, and no
appraisal moves two risk bands. Validation produced an unanticipated principal
finding: whether a facility's term is an exact multiple of twelve, a property
with no economic content, predicts default at an area under the curve of 0.889
in every approval year, and the artefact is present in the SBA's own published
extracts.

An instrument-specific appraisal model cannot be validated against a dataset
that lacks its variables: substituting proxies tests the proxies. Expert
elicitation is therefore not a second-best option but the only sound one.

**Keywords:** SME credit appraisal, multi-criteria decision analysis, fuzzy sets,
decision support systems, data leakage, development banking

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
