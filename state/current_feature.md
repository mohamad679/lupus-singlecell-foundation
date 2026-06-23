# Current Feature

Feature: P3-F005 - Cell-type proportion baseline scaffold.

Status: completed pending review.

Builder scope:

- Cell-type proportion baseline design/scaffold only.
- Define restricted patient/donor/sample composition feature metadata.
- Create header-only feature and result tables.
- Validate caller-provided mock counts and fractions only.
- Preserve patient/donor grouping and patient/cohort split requirements.

Scientific decision:

- SLE diagnosis / case-control prediction: approved for baseline design only.
- Disease activity prediction: `blocked`.
- Flare prediction: `blocked`.
- Lupus nephritis prediction: `blocked`.
- Foundation models, deep patient-level MIL, uncertainty modeling, and dashboard
  work are not approved.

Explicitly forbidden:

- Computing real cell-type counts, totals, fractions, or transformations.
- Fitting or training classifiers.
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
- Starting P3-F006 or later features.

The cell-type feature and result tables contain headers only. The utility
validates mock metadata and numeric ranges without loading cells, computing
proportions, fitting models, or generating predictions.
`allow_modeling` remains false, `selected_datasets` remains `[]`, and
`external_validation_cohort` remains TODO.
