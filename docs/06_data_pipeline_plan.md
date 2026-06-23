# Phase 2 Data Pipeline Plan

## Phase 2 Goal

Phase 2 creates a reproducible scaffold for future single-cell data handling. It defines the structure for AnnData/Scanpy processing, metadata harmonization, QC planning, and patient-level split validation.

This phase does not download datasets, preprocess data, train models, or approve any dataset for modeling.

## Approved-With-Restrictions Dataset Context

Human Gate 1 is `approved_with_restrictions`.

- `GSE137029` is approved only as the primary candidate for Phase 2 pipeline development, not for modeling.
- `CELLxGENE/HCA 436154da-bcf1-4130-9c8b-120ff9a888f2 / 218acb0f-9f2f-4f76-b90b-15a4b7c7f629` is approved only for metadata harmonization design, not for modeling.
- `GSE174188` remains `needs_manual_verification` and is not part of Phase 2 processing.
- `GSE162577` remains `limited_candidate` and is not the primary Phase 2 candidate.
- `selected_datasets` remains empty until a later explicit human gate approves dataset selection.

## Data Lifecycle

Future data handling must separate lifecycle stages:

- Raw: immutable source files or approved source exports.
- Interim: validated local staging outputs created after an explicit acquisition feature.
- Processed: reproducible outputs created by documented QC and harmonization steps.

This scaffold does not create any raw, interim, or processed data files.

## Raw, Interim, and Processed Boundaries

Raw data must never be overwritten. Interim outputs must record provenance, checksums, source accession, and generation command. Processed objects must be reproducible from raw or approved interim inputs.

No data boundary is activated in P2-F001 because downloads and preprocessing are forbidden.

## AnnData Expectations

Future AnnData objects must define:

- `obs` fields for patient, donor, sample, cohort, batch, tissue, assay, and disease labels.
- `var` fields for gene identifier, gene symbol, feature type, and genome/reference if source-provided.
- `layers` policy for raw counts, normalized counts, and transformed matrices.
- `uns` provenance metadata for source, accession, pipeline version, and QC decisions.

P2-F001 does not create AnnData objects.

## AnnData Schema and Integrity Contract

The AnnData schema contract defines what future single-cell objects must contain before any downstream QC, harmonization, or patient-level split validation. P2-F002 defines the contract only; it does not create AnnData files or load real datasets.

### Expected AnnData Structure

Future AnnData-like objects must expose:

- `obs`: cell-level metadata table with one row per cell.
- `var`: feature-level metadata table with one row per gene or feature.
- `X`: primary cells-by-genes matrix.
- `layers`: named matrices for raw and transformed data states.
- `uns`: unstructured provenance and pipeline metadata.

### obs Requirements

Required future `obs` fields:

- `cell_id`
- `patient_id`
- `donor_id`
- `sample_id`
- `cohort_id`
- `batch_id`
- `tissue`
- `assay_type`
- `disease_label`
- `cell_type`
- `source_dataset`
- `split_group`

Patient, donor, sample, cohort, and batch fields must come from source metadata or approved harmonization rules. Missing values must remain `TODO` or `unclear` until verified.

### var Requirements

Required future `var` fields:

- `gene_id`
- `gene_symbol`
- `feature_type`
- `genome`

Gene identifiers must not be inferred from organism, assay, file name, or platform. They require source-supported feature metadata.

### X Matrix Expectations

`X` must be a cells-by-genes matrix. Its first dimension must match the number of `obs` rows, and its second dimension must match the number of `var` rows.

The matrix contents must not be assumed to be raw counts unless source documentation or approved inspection verifies that status.

### Layers Policy

Required future layers:

- `counts`
- `normalized`
- `log_normalized`

The `counts` layer is the protected raw-count layer and must not be overwritten. Normalized and log-normalized layers must be generated reproducibly by documented future pipeline steps.

### uns Metadata Policy

Required future `uns` fields:

- `dataset_id`
- `source`
- `preprocessing_version`
- `schema_version`
- `audit_status`
- `patient_level_split_policy`

`patient_level_split_policy` must indicate patient-level or cohort-level splitting only.

### Raw Count Policy

Raw counts must be preserved in `layers["counts"]` or another explicitly documented raw-count location. They must not be overwritten by normalized data.

### Normalized Data Policy

Normalized and log-normalized matrices must be derived from source-supported counts using a documented pipeline version. P2-F002 defines names and integrity rules only.

### Cell-Level Metadata Rules

Cell-level metadata may describe cell identity, source dataset, assay, tissue, and annotation. It must not be used to create random cell-level train/test splits.

### Patient-Level Metadata Rules

Patient-level or donor-level identifiers are required for modeling-ready data. Missing `patient_id` is a failure for modeling-ready data. If the source provides only `donor_id`, a future harmonization feature must explicitly document whether `donor_id` can serve as the split unit.

### Forbidden Assumptions

- Do not assume patient IDs from cell barcodes.
- Do not assume labels from accession names.
- Do not assume raw counts from assay type.
- Do not assume cell-type labels from publication title.
- Do not assume gene identifiers from human organism metadata.
- Do not assign cell-level split groups.
- Do not mark a dataset modeling-ready from schema compliance alone.

### Integrity Checks

Future validators must check:

- `obs` index uniqueness.
- `var` index uniqueness.
- `X` shape equals cells by genes.
- required `obs`, `var`, `layers`, and `uns` fields are present.
- no missing `patient_id` in modeling-ready data.
- no cell-level split assignment.
- `split_group` is patient-level or cohort-level only.
- unknown values are `TODO` or `unclear`, not guessed.

### Failure Modes

Validation must fail when:

- required `obs`, `var`, `layers`, or `uns` fields are missing.
- `patient_id` is missing in modeling-ready data.
- `disease_label` is missing.
- `split_group` or `patient_level_split_policy` indicates cell-level splitting.
- `obs` or `var` indexes are not unique.
- `X` shape does not match `obs` and `var`.

## Metadata Harmonization Strategy

Metadata harmonization maps source-specific fields from GEO, CELLxGENE, and HCA into a canonical metadata contract without guessing. P2-F003 defines the schema and mapping rules only; it does not download data, inspect full datasets, preprocess matrices, or create AnnData objects.

### Source Datasets

The current restricted Phase 2 design context includes:

- GEO candidate `GSE137029` for pipeline-development planning only.
- CELLxGENE/HCA lupus-linked metadata context for harmonization design only.
- Restricted or non-primary candidates remain out of processing until later explicit approval.

No source is selected for modeling by this harmonization schema.

### GEO Metadata Challenges

GEO records may distribute patient, sample, platform, and disease information across series-level records, sample-level records, supplementary file descriptions, and publication text. Sample titles may contain hints, but hints are not evidence for patient IDs, disease activity, treatment status, or batch labels. GEO metadata must therefore be mapped only after explicit field-level verification.

### CELLxGENE Metadata Challenges

CELLxGENE collections may expose standardized fields, ontology labels, donor metadata, cell-type annotations, and dataset-level provenance, but availability varies by collection and dataset. Donor/sample identifiers, raw count status, and disease activity labels must be treated as `TODO` or `unclear` unless visible in public metadata or later approved inspection.

### HCA Metadata Challenges

HCA metadata may use project, specimen, donor, library, and file-level entities. The harmonization step must preserve provenance from the specific HCA entity that supports each canonical field. HCA project context alone is not sufficient evidence for patient-level labels or split eligibility.

### Canonical Metadata Schema

The canonical schema is defined in `metadata/metadata_harmonization_schema.yaml`. It includes:

- `patient_id`
- `donor_id`
- `sample_id`
- `cell_id`
- `cohort_id`
- `batch_id`
- `dataset_id`
- `source_dataset`
- `source_database`
- `organism`
- `tissue`
- `assay_type`
- `disease_label`
- `disease_activity`
- `cell_type`
- `treatment_status`
- `sex`
- `age`
- `timepoint`
- `split_group`

### Harmonization Principles

- Preserve source values before applying any transformation.
- Record the source database and source dataset for every harmonized record.
- Prefer explicit patient or donor identifiers over derived sample labels.
- Keep source-specific terminology when no approved mapping exists.
- Avoid collapsing disease labels, activity labels, or treatment labels without a documented rule.
- Keep harmonization deterministic and auditable.

### Missing-Value Policy

Unknown values must remain `TODO` or `unclear`. Empty strings, inferred labels, and placeholder guesses are not acceptable for required future metadata. If a source field cannot be verified, the mapping file must retain `TODO` for the original field and transformation.

### Provenance Tracking

Every canonical field must be traceable to a source database, source dataset, and original source field once data acquisition is approved. Provenance must distinguish manually audited metadata from future machine-parsed metadata.

### Batch Awareness

Batch identifiers must come from explicit batch, library, processing, site, platform, lane, or cohort metadata. Batch labels must not be invented from file order, sample order, or accession suffixes.

### Patient-Level Requirements

Patient-level prediction requires patient or donor identifiers that support leakage-free splitting. Cell barcodes, sample titles, and inferred sample groupings are not valid patient identifiers unless a later manually approved evidence trail establishes the relationship.

### Forbidden Assumptions

- Do not infer disease labels from titles or accession names.
- Do not infer disease activity from diagnosis labels.
- Do not infer lupus nephritis status from kidney tissue alone.
- Do not infer treatment status from study design summaries.
- Do not infer patient IDs from sample IDs or cell barcodes.
- Do not infer batch labels from file names without source documentation.
- Do not assume CELLxGENE or HCA ontology fields are present before verification.

### Future Failure Modes

Harmonization must fail or remain blocked when:

- required canonical fields such as `dataset_id` or `disease_label` are missing.
- source mapping is still `TODO` for a field needed by a downstream task.
- patient, donor, sample, cohort, or batch relationships are ambiguous.
- values are inferred rather than source-supported.
- split metadata implies cell-level rather than patient-level or cohort-level partitioning.

Unknown fields must remain `TODO` or `unclear` until source evidence is available.

## Patient-Level Splitting Policy

All future split logic must be patient-level or cohort-level only. Cell-level splits are forbidden.

The minimum valid split unit is a source-supported patient or donor identifier. If patient or donor identifiers are unavailable, the dataset cannot be used for patient-level prediction.

## QC Strategy

Future QC scaffolding should plan checks for:

- cell count by patient, donor, sample, and batch
- detected genes per cell
- total counts per cell
- mitochondrial/ribosomal percentages if source-compatible
- doublet handling policy
- batch and cohort distributions
- cell-type annotation provenance

P2-F001 does not compute QC metrics.

## Leakage Prevention Policy

Future leakage checks must ensure:

- no cells from the same patient or donor appear in both train and test partitions
- no sample from a held-out cohort leaks into training
- batch and cohort labels are inspected before any modeling
- external validation is cohort-level and source-supported

Cell-level random train/test splitting is forbidden.

## Reproducibility Policy

Every future pipeline step must record:

- source accession or collection ID
- input path or manifest
- output path
- command or script
- software version
- random seed where relevant
- checksums for downloaded or generated files after explicit acquisition approval

## Forbidden Actions

- Downloading full datasets.
- Creating AnnData objects in this feature.
- Running Scanpy preprocessing in this feature.
- Training or implementing models.
- Creating model files.
- Approving datasets for modeling.
- Creating `selected_datasets`.
- Assigning `external_validation_cohort`.
- Splitting cells.
- Inferring patient IDs, labels, activity scores, treatment metadata, batch metadata, cell-type labels, or gene identifiers.

## Phase 2 Exit Criteria

Phase 2 scaffold is complete when:

- data-pipeline config exists and blocks downloads/modeling
- source package directories exist
- scaffold validation script confirms Phase 2 restrictions
- tests verify no downloads, no modeling, no cell-level splits, and no selected datasets

Later Phase 2 features must still pass explicit human and judge gates before acquisition, QC, labels, or prediction tasks are advanced.
