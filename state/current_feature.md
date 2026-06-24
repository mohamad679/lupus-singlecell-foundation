# Current Feature

Feature: P3-F015 - Dataset/label evidence review.

Status: metadata-only review completed with unresolved training blockers.

Verified:

- GSE137029 sample-level GEO field `condition` with inspected values `SLE`,
  `healthy`, and `SLE flare`.
- GSE137029 raw/processed availability, SRA relations, and processed file
  manifest.
- CELLxGENE collection/dataset identity, `donor_id` field visibility, aggregate
  normal/SLE disease terms, raw.X, and H5AD asset metadata.
- HCA donor count, assay/tissue metadata, and source accessions.
- Official source-level linkage among GSE137029, HCA, and CELLxGENE.

Still blocked:

- GSE137029 patient/donor identifiers and sample-to-person mapping.
- Patient-level case/control linkage and class counts.
- CELLxGENE sample IDs and donor-to-disease linkage.
- Exact cross-repository donor/sample/cell overlap.
- QC approval, split manifest, leakage checks, and feature manifest.

Judge decisions:

- GSE137029 cannot be selected.
- CELLxGENE/HCA cannot be assigned as external validation.
- Source linkage is verified, but exact overlap remains unresolved.

Modeling controls:

- `modeling_readiness`: `not_ready`
- `training_permission`: `blocked`
- `allow_modeling`: false
- `selected_datasets`: []
- `external_validation_cohort`: TODO

No full data were downloaded. Preprocessing, training, model artifacts, dataset
selection, external-validation assignment, and Phase 4 remain forbidden.
