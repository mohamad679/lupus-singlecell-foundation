# Current Feature

Feature: P3-F004 - Random forest / XGBoost baseline scaffold.

Status: completed pending review.

Builder scope:

- Tree-based baseline design/scaffold only.
- Define restricted random forest and optional XGBoost design metadata.
- Create header-only results and feature-importance tables.
- Provide explicit training and required-dependency refusal paths.
- Preserve patient-level pseudobulk and patient/cohort split requirements.

Scientific decision:

- SLE diagnosis / case-control prediction: approved for baseline design only.
- Disease activity prediction: `blocked`.
- Flare prediction: `blocked`.
- Lupus nephritis prediction: `blocked`.
- Foundation models, deep patient-level MIL, uncertainty modeling, and dashboard
  work are not approved.

Explicitly forbidden:

- Fitting or training random forest or XGBoost.
- Prediction or probability generation.
- Model artifact creation.
- Loading real features, labels, or datasets.
- Importing XGBoost as a required dependency.
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
- Starting P3-F005 or later features.

The tree result and feature-importance tables contain headers only. The utility
imports no estimator library, treats XGBoost as optional, and cannot fit or
predict.
`allow_modeling` remains false, `selected_datasets` remains `[]`, and
`external_validation_cohort` remains TODO.
