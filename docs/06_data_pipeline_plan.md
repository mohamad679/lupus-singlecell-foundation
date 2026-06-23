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

## Metadata Harmonization Strategy

Metadata harmonization must map source fields into a common contract without guessing. Required future fields include:

- `patient_id`
- `donor_id`
- `sample_id`
- `cohort_id`
- `batch_id`
- `disease_label`
- `tissue`
- `assay_type`

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
