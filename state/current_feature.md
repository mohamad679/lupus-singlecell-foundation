# Current Feature

Feature: P3-F018 - Metadata inspection evidence expansion.

Status: completed; strategy decision required.

Expanded evidence:

- GSE137029 has complete pooled sample-level condition labels but no
  patient/donor field or sample-to-person mapping.
- CELLxGENE/HCA has 261 donors, 274 samples, consistent donor-to-disease
  linkage, and explicit repeated-sample grouping.
- Exact GSE137029-to-CELLxGENE/HCA record overlap remains unresolved.
- CELLxGENE/HCA cannot be assigned as external validation.

Judge decisions:

- GSE137029 cannot be selected for patient-level training.
- CELLxGENE/HCA mapping feasibility is improved but no dataset is selected.
- Repeating inspection of the same public metadata sources is unlikely to
  resolve GSE137029.
- P3-F019 dataset strategy/pivot gate should be prepared.
- Pivot remains `not_activated`.

Modeling controls remain:

- `modeling_readiness`: `not_ready`
- `training_permission`: `blocked`
- `allow_modeling`: false
- `phase4_permission`: `blocked`
- `selected_datasets`: []
- `external_validation_cohort`: TODO

No full data, preprocessing, training, model artifacts, pivot activation, or
Phase 4 work is allowed.
