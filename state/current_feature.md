# Current Feature

Feature: P3-F019 - Dataset strategy decision / pivot gate.

Status: completed; training remains blocked.

Strategy decision:

- `switch_primary_to_CELLxGENE_HCA`
- Scope: primary-candidate validation only.
- GSE137029 remains blocked for patient-level modeling because no explicit
  person mapping exists.
- CELLxGENE/HCA has verified donor, sample, and diagnosis linkage and is the
  stronger candidate for the next validation feature.
- No dataset is selected or approved.
- CELLxGENE/HCA is not assigned as external validation.

Pivot decision:

- The SLE diagnosis / case-control objective is unchanged.
- `pivot_status`: `not_activated`.
- A dataset-strategy adjustment is documented without activating a paper or
  scientific-objective pivot.

Next allowed feature:

- P3-F020 - CELLxGENE/HCA primary dataset validation.
- Validation must address access, metadata completeness, repeated samples,
  QC, donor-level splitting, leakage, and feature readiness.
- A separate independent cohort search remains required for external
  validation.

Controls remain:

- `modeling_readiness`: `not_ready`
- `training_permission`: `blocked`
- `allow_modeling`: false
- `phase4_permission`: `blocked`
- `selected_datasets`: []
- `external_validation_cohort`: TODO

No downloads, preprocessing, training, model artifacts, dataset selection, or
Phase 4 work is allowed.
