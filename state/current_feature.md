# Current Feature

Feature: P3-F006 - Baseline evaluation protocol.

Status: completed pending review.

Builder scope:

- Evaluation protocol and validation scaffold only.
- Define required discrimination and calibration metrics without computing them.
- Create header-only evaluation and prediction-manifest tables.
- Validate caller-provided mock prediction metadata only.
- Require verified labels, patient-level units, and passed leakage checks.

Scientific decision:

- SLE diagnosis / case-control prediction: approved for baseline design only.
- Disease activity prediction: `blocked`.
- Flare prediction: `blocked`.
- Lupus nephritis prediction: `blocked`.
- Foundation models, deep patient-level MIL, uncertainty modeling, and dashboard
  work are not approved.

Explicitly forbidden:

- Computing metrics on real or mock predictions.
- Reporting performance or clinical utility claims.
- Fitting or training models.
- Prediction or probability generation.
- Model artifact creation.
- Loading real features, labels, or datasets.
- Loading or preprocessing real cell-level data.
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
- Starting P3-F007 or later features.

The evaluation result and prediction-manifest tables contain headers only. The
utility validates mock metadata without computing metrics or reading data.
`allow_modeling` remains false, `selected_datasets` remains `[]`, and
`external_validation_cohort` remains TODO.
