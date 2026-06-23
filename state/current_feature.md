# Current Feature

Feature: P3-F003 - Logistic regression baseline scaffold.

Status: completed pending review.

Builder scope:

- Logistic regression design/scaffold only.
- Define restricted configuration, required input-manifest metadata, and
  header-only results and coefficient tables.
- Provide an explicit training refusal path.
- Preserve patient-level pseudobulk and patient/cohort split requirements.

Scientific decision:

- SLE diagnosis / case-control prediction: approved for baseline design only.
- Disease activity prediction: `blocked`.
- Flare prediction: `blocked`.
- Lupus nephritis prediction: `blocked`.
- Foundation models, deep patient-level MIL, uncertainty modeling, and dashboard
  work are not approved.

Explicitly forbidden:

- Fitting or training logistic regression.
- Prediction or probability generation.
- Model artifact creation.
- Loading real features, labels, or datasets.
- Real pseudobulk feature extraction or matrix creation.
- Loading or preprocessing real data.
- Deep learning or DeepSets.
- Foundation models.
- Uncertainty modeling.
- Dashboard work.
- Model artifacts.
- Dataset approval or selection.
- External validation assignment.
- Cell-level splitting.
- Starting P3-F004 or later features.

The logistic regression result and coefficient tables contain headers only.
The utility imports no estimator library and cannot fit or predict.
`allow_modeling` remains false, `selected_datasets` remains `[]`, and
`external_validation_cohort` remains TODO.
