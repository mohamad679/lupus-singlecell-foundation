# Current Feature

Feature: P3-F016 - Modeling Readiness Re-check.

Status: completed; readiness remains `not_ready`.

Scientific Judge decision:

- No blocking readiness condition moved to passed.
- The external-validation planning protocol remains passed, but no external
  cohort is assignable.
- GSE137029 remains unselected.
- CELLxGENE/HCA remains unsuitable as independent external validation.

Remaining blockers:

- dataset selection;
- patient/donor-linked label provenance;
- stable person identifiers and sample relationships;
- patient/donor-level split manifest;
- real leakage checks and exact overlap resolution;
- training-cohort suitability;
- dataset-specific QC approval;
- populated feature manifest.

Recommendation: `more_metadata_inspection_required`.

A pivot should be considered later if explicit patient-level mappings cannot be
obtained without prohibited full-data access or metadata inference.

Modeling controls remain:

- `modeling_readiness`: `not_ready`
- `training_permission`: `blocked`
- `allow_modeling`: false
- `selected_datasets`: []
- `external_validation_cohort`: TODO

No preprocessing, training, model artifacts, dataset assignment, or Phase 4
work is allowed.
