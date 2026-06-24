# Current Feature

Feature: P3-F007 - Calibration metrics scaffold.

Status: completed pending review.

Builder scope:

- Calibration protocol and scaffold only.
- Define Brier score, ECE, and future reliability diagram contracts without
  computing or plotting them.
- Create header-only calibration and reliability-manifest tables.
- Validate caller-provided mock calibration metadata only.
- Keep ECE binning strategy and bin count as TODO.

Scientific decision:

- SLE diagnosis / case-control prediction: approved for baseline design only.
- Disease activity prediction: `blocked`.
- Flare prediction: `blocked`.
- Lupus nephritis prediction: `blocked`.
- Foundation models, deep patient-level MIL, uncertainty modeling, and dashboard
  work are not approved.

Explicitly forbidden:

- Computing real or mock calibration metrics.
- Generating reliability diagrams or calibration curves.
- Implementing uncertainty, abstention, or selective prediction methods.
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
- Starting P3-F008 or later features.

The calibration result and reliability-manifest tables contain headers only.
The utility validates mock metadata without computing metrics, loading
predictions, or generating figures.
`allow_modeling` remains false, `selected_datasets` remains `[]`, and
`external_validation_cohort` remains TODO.
