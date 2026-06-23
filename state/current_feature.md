# Current Feature

Feature: P3-F002 - Pseudobulk feature design.

Status: completed pending review.

Builder scope:

- Pseudobulk design only.
- Define safe aggregation units, aggregation methods, a feature schema, an
  empty manifest, and mock-only validation utilities.
- Keep normalization and gene filtering policies as TODO.
- Preserve patient/donor-level split and leakage controls.

Scientific decision:

- SLE diagnosis / case-control prediction: approved for baseline design only.
- Disease activity prediction: `blocked`.
- Flare prediction: `blocked`.
- Lupus nephritis prediction: `blocked`.
- Foundation models, deep patient-level MIL, uncertainty modeling, and dashboard
  work are not approved.

Explicitly forbidden:

- Real pseudobulk feature extraction or matrix creation.
- Actual training or real model fitting.
- Loading or preprocessing real data.
- Deep learning or DeepSets.
- Foundation models.
- Uncertainty modeling.
- Dashboard work.
- Model artifacts.
- Dataset approval or selection.
- External validation assignment.
- Cell-level splitting.
- Starting P3-F003 or later features.

The pseudobulk manifest contains headers only. The utility validates config,
schema, headers, and caller-provided mock rows; it does not process real data.
`allow_modeling` remains false, `selected_datasets` remains `[]`, and
`external_validation_cohort` remains TODO.
