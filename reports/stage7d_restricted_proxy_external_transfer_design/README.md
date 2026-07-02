# Stage 7D restricted proxy external transfer evaluation design

This package defines the evaluation design for using `GSE135779` as a restricted proxy external transfer cohort.

## Scope

This stage is design-only. It does not execute external evaluation and does not claim strict external validation.

Stage 7C established that Supplementary Table 1b contains sample-level disease-activity metadata, including SLEDAI total score and SLEDAI-style component fields. It also established that the table does not contain explicit clinician-adjudicated `flare`, `managed`, `stable`, `remission`, or longitudinal visit-status labels.

## Approved endpoint

The only approved primary endpoint for this restricted external transfer design is:

| Class | Definition | Meaning |
|---|---|---|
| Positive | SLE sample with `SLEDAI > 4` | high-activity SLE |
| Negative | SLE sample with `SLEDAI <= 4` | low-activity SLE |

This endpoint is a disease-activity proxy. It is not equivalent to Stage 6 `FLARE` versus managed SLE.

## Exclusions

- Exclude healthy controls from the primary proxy endpoint.
- Exclude samples without an explicit numeric SLEDAI value from the primary analysis.
- Exclude the two child-SLE rows with missing explicit SLEDAI unless a separate pre-registered inference rule is written before evaluation.
- Do not infer `managed SLE` from `SLEDAI <= 4`.

## Model-freeze rule

All model components must be frozen before any GSE135779 labels are used.

Frozen components include:

- the Geneformer embedding extraction strategy;
- cell selection or cell cap policy;
- donor/sample aggregation policy;
- internal PCA or dimensionality-reduction transform;
- internal classifier weights;
- any threshold selected on Stage 6 internal data.

No PCA, classifier, threshold, feature selection, or hyperparameter may be fit or tuned using GSE135779 labels.

## Primary analysis

The primary analysis is external transfer scoring of GSE135779 SLE samples under the `SLEDAI > 4` versus `SLEDAI <= 4` proxy endpoint.

Primary reported metrics:

- ROC-AUC;
- AUPRC with high-activity SLE as the positive class;
- balanced accuracy at a frozen internal threshold, if such threshold is available;
- sensitivity and specificity at the same frozen threshold;
- bootstrap confidence intervals over donor/sample units.

## Claim language

Allowed:

`GSE135779 was used for a restricted proxy external transfer analysis of high-activity versus low-activity SLE using a paper-aligned SLEDAI threshold.`

Not allowed:

`The Stage 6 model was externally validated on GSE135779 for FLARE versus managed SLE.`

## Decision

Proceed to implementation only as a restricted proxy external transfer test.
