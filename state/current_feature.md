# Current Feature

Feature: P3-F014 - Controlled metadata inspection plan.

Status: completed as a plan only; no inspection has been executed.

Planner, Scientific Judge, and Bioinformatics Judge findings:

- Nine metadata/file-manifest targets are defined for GSE137029 and the linked
  CELLxGENE/HCA candidate.
- Allowed future actions are limited to public metadata pages, schema field
  descriptions, file listings, and metadata-only manifests.
- The evidence log contains headers only.
- Every inspection target remains `pending_inspection`.
- Patient/donor identifiers, sample linkage, label provenance, and cohort
  overlap remain unresolved.
- Raw/processed object, QC, feature, and split feasibility remain unverified.

Modeling controls:

- `inspection_gate_status`: `pending`
- `allow_metadata_only_inspection`: true
- `allow_full_data_download`: false
- `modeling_readiness`: `not_ready`
- `training_permission`: `blocked`
- `allow_modeling`: false
- `selected_datasets`: []
- `external_validation_cohort`: TODO

Explicitly forbidden:

- Executing metadata inspection without a later explicit feature.
- Downloading full data, expression objects, sequencing reads, or file bundles.
- Guessing identifiers, labels, sample relationships, or cohort overlap.
- Preprocessing, splitting, feature extraction, training, or artifact creation.
- Selecting a dataset, assigning external validation, or starting Phase 4.

Next work remains P3-F015 TODO and requires explicit approval before any
metadata target is inspected or evidence row is added.
