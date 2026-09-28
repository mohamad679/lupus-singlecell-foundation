# Preliminary reporting and bias review — 29 September 2026

This is a working assessment of the **historical** release. It must be
revisited after corrected predictions and before submission. It applies
[TRIPOD+AI](https://www.bmj.com/content/385/bmj-2023-078378) as reporting
guidance and [PROBAST+AI](https://www.bmj.com/content/388/bmj-2024-082505)
as a structured assessment of development quality, evaluation bias, and
applicability. It is not a completed item-by-item official checklist.

| Domain | Present evidence | Required manuscript or analysis action |
|---|---|---|
| Participants and data sources | 261 adult development donors; 56 mostly pediatric external donors, 16 controls; source cohort definitions and accessions recorded | Add donor/cell flow, eligibility and exclusion rules, missingness, repeated-visit audit, and source-defined age groups. State the limits of this case-versus-healthy sample for clinical diagnosis. |
| Predictors | Pseudobulk reference spaces differ; historical Geneformer V1 input semantics are defective; external metadata are sparse | Report raw-count QC, shared-gene rule, vocabulary coverage, tokenization losses, covariate availability, checkpoint hashes, and all feature transformations. Correct V1 extraction before any performance claim. |
| Outcome | Both cohorts use source SLE/healthy labels; healthy controls do not represent symptomatic differential diagnosis | Document source label definitions and timing; avoid diagnostic claims for clinical populations with other inflammatory diseases. |
| Analysis | Donor-level splitting and fold-local scaling are sound; original co-primary label-shuffle p-values target the wrong null; external controls number 16 | Report paired DeLong plus paired bootstrap with Holm correction, calibration with uncertainty, fixed-prediction versus model-fitting uncertainty, and the post-hoc correction boundary. Explain small-sample imprecision. |

## Reporting items still to complete

- Full, page-referenced TRIPOD+AI checklist for the final manuscript and
  supplement, including data sources, participants, predictors, outcome,
  sample size, missing data, model specification, validation, and all
  performance measures.
- Separate PROBAST+AI development-quality and evaluation-risk judgments,
  with explicit answers and rationale for every applicable signalling
  question. The present table records concerns but does not assign a final
  overall risk-of-bias grade before the corrected pipeline is run.
- Table of original protocol, historical implementation, scientific
  correction, and effect on each reported result.
- Calibration display, versioned prediction vectors, exact runtime and model
  provenance, and updated figure-to-artifact references.
