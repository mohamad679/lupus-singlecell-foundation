# Current Feature

Feature: P3-F012 - Dataset selection and label verification.

Status: completed with unresolved modeling-readiness blockers.

Planner and Scientific Judge findings:

- GSE137029 is the primary candidate for continued verification only.
- GSE137029 is not selected and is not approved for modeling.
- The CELLxGENE/HCA representation is useful for metadata verification but may
  overlap GSE137029 and cannot be treated as independent.
- Human lupus single-cell study context is verified for both candidates.
- Patient-level diagnosis-label provenance is not verified.
- GSE137029 patient/donor identifier availability remains unclear.
- CELLxGENE donor identifiers are visible, but donor/sample/label linkage and
  cross-source deduplication remain unresolved.

Modeling controls:

- `modeling_readiness`: `not_ready`
- `training_permission`: `blocked`
- `allow_modeling`: false
- `selected_datasets`: []
- `external_validation_cohort`: TODO

Explicitly forbidden:

- Training or fitting models.
- Creating model artifacts or predictions.
- Selecting or approving either candidate without a separate evidence-backed
  human decision.
- Guessing patient IDs, labels, sample relationships, or cohort independence.
- Treating CELLxGENE/HCA as an independent external cohort.
- Downloading full datasets.
- Starting Phase 4.

Next work must inspect explicitly approved metadata assets, record exact
patient/donor/sample and diagnosis-label fields, reconcile cross-source cohort
overlap, and return for a separate selection decision.
