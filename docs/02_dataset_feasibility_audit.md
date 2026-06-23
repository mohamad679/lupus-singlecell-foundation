# Dataset Feasibility Audit

## Objective

Create a rigorous public dataset feasibility audit plan for SLE, lupus, and lupus nephritis single-cell transcriptomics.

This phase is planning and audit scaffolding only. It must not download full datasets, implement modeling, train models, invent dataset accessions, or populate `metadata/dataset_catalog.csv` with guessed datasets.

## Inclusion Criteria

A candidate dataset may be considered only if source evidence verifies:

- Disease context is SLE, lupus, lupus nephritis, or a directly relevant comparator context.
- Data are single-cell or single-nucleus transcriptomics.
- Human samples are preferred; non-human datasets require explicit justification and human review.
- Public metadata are sufficient to evaluate donor, sample, disease, control, assay, tissue, and provenance fields.
- Access terms allow at least feasibility review.
- Raw or processed data availability can be verified from an authoritative source.

## Exclusion Criteria

Reject candidates when any of the following apply:

- Bulk RNA-seq is presented as single-cell or single-nucleus data.
- Dataset accession, patient count, sample count, or assay type cannot be verified.
- Disease labels are absent and cannot support SLE or lupus nephritis feasibility review.
- Patient-level metadata are unavailable and no alternative reproducible grouping is documented.
- Access terms forbid planned reuse.
- The dataset requires full download before basic feasibility can be assessed.
- The candidate is based on memory, citation fragments, or guessed accession identifiers.

## Required Metadata Fields

The audit must evaluate the fields already defined in `metadata/dataset_catalog.csv`:

- `dataset_id`
- `source_name`
- `source_url`
- `accession`
- `organism`
- `disease_context`
- `case_definition`
- `control_definition`
- `tissue_or_sample_type`
- `assay_type`
- `platform`
- `donor_count`
- `sample_count`
- `cell_count`
- `raw_data_available`
- `processed_data_available`
- `clinical_metadata_available`
- `treatment_metadata_available`
- `disease_activity_metadata_available`
- `batch_metadata_available`
- `cell_type_annotations_available`
- `license_or_access_terms`
- `download_status`
- `feasibility_status`
- `feasibility_notes`
- `provenance_notes`
- `last_verified`

Unknown fields must remain `TODO`.

## Patient-Level Metadata Requirements

Feasibility review should determine whether patient-level or donor-level metadata include:

- Stable donor or patient identifiers: TODO until verified.
- Sample-to-donor mapping: TODO until verified.
- Disease status and diagnosis criteria: TODO until verified.
- Control status and matching strategy: TODO until verified.
- Tissue or sample source: TODO until verified.
- Treatment exposure: TODO until verified.
- Disease activity score or proxy: TODO until verified.
- Lupus nephritis class or renal involvement status: TODO until verified.
- Age, sex, ancestry, and other confounder fields: TODO until verified.
- Batch, site, library, chemistry, and processing variables: TODO until verified.

Patient identifiers must never be assumed from sample names.

## Disease And Activity Label Requirements

The audit must distinguish:

- SLE case labels from lupus nephritis labels.
- Active disease from inactive disease when available.
- Renal from non-renal involvement when available.
- Healthy controls from disease controls when available.
- Treated from untreated or pre-treatment samples when available.

If labels are ambiguous, the candidate remains unresolved until documented evidence supports a decision.

## Raw Vs Processed Data Requirements

For each candidate, record:

- Whether raw count matrices are available.
- Whether processed objects are available.
- Whether processed objects are AnnData, Seurat, loom, matrix formats, or another format.
- Whether cell-level metadata are included.
- Whether gene identifiers are documented.
- Whether raw and processed objects can be linked to the same samples.
- Whether access requires controlled authorization.

Do not download full data before Human Gate 1 approval.

## External Validation Requirements

The feasibility audit must identify whether an external validation cohort exists.

Validation candidates must be independently sourced, not merely a split of the same dataset, unless human review explicitly approves a different strategy. If no validation cohort is verified, record `TODO` and treat this as a feasibility risk.

Current external validation cohort: TODO.

## GEO / NCBI Metadata Audit Protocol

### Search Objectives

Identify real public GEO / NCBI records that may contain SLE, lupus, or lupus nephritis single-cell or single-nucleus transcriptomics data. This protocol is metadata-only until Human Gate 1 is approved.

Do not download full datasets. Do not infer accessions from publications or memory. Do not add candidates to `metadata/dataset_catalog.csv` until manual metadata verification is complete.

### Exact Search Terms

Use these terms exactly when planning GEO / NCBI searches:

- `systemic lupus erythematosus single cell RNA sequencing`
- `SLE scRNA-seq`
- `lupus nephritis single cell RNA-seq`
- `autoimmune lupus single-cell transcriptomics`
- `PBMC lupus single cell`
- `kidney lupus nephritis single cell`

### GEO / NCBI Inclusion Criteria

A GEO / NCBI candidate can be recorded in `reports/tables/geo_candidate_datasets.csv` only when an explicit accession is visible in source metadata and the row is marked `candidate_pending_audit`.

Candidate inclusion requires metadata evidence for:

- Single-cell or single-nucleus transcriptomics assay.
- SLE, lupus, lupus nephritis, or directly relevant autoimmune lupus context.
- Organism.
- Tissue, compartment, or sample source.
- Disease and control label availability or a clear TODO when unresolved.
- Raw-data availability and processed-object availability status.
- Manual audit status.

### GEO / NCBI Exclusion Criteria

Reject or defer records when:

- The assay is bulk RNA-seq, microarray, proteomics, spatial-only without single-cell transcriptomics, or otherwise not single-cell or single-nucleus transcriptomics.
- The accession is absent or inferred.
- Patient IDs, sample counts, disease labels, or assay types are guessed.
- Full data download is required before basic metadata can be assessed.
- SLE and lupus nephritis labels cannot be separated and this ambiguity is not documented.
- The source appears to duplicate a previously reviewed cohort and overlap cannot be resolved.

### Metadata Fields To Extract

For each candidate, use `metadata/geo_candidate_schema.yaml` and capture:

- `accession`
- `title`
- `source`
- `publication`
- `organism`
- `tissue`
- `assay_type`
- `disease_context`
- `lupus_subtype`
- `n_patients`
- `n_samples`
- `n_cells`
- `patient_id_available`
- `disease_label_available`
- `activity_label_available`
- `treatment_info_available`
- `batch_info_available`
- `raw_data_available`
- `processed_object_available`
- `notes`
- `audit_status`

Unknown values must be `TODO`. Header-only templates are valid before any candidate has been manually identified.

### Patient-Level Requirements

Manual verification must determine whether GEO / NCBI metadata expose donor-level or patient-level structure. Patient IDs must not be reconstructed from sample names unless the source explicitly documents that mapping.

Required checks:

- Patient or donor ID availability.
- Sample-to-patient mapping.
- Number of patients and samples.
- Whether multiple samples per patient exist.
- Whether controls are matched or independently recruited.
- Whether treatment, activity, nephritis status, and batch metadata are patient-level or sample-level.

### Label Requirements

Disease labels must be source-supported. Record whether labels distinguish:

- SLE.
- Lupus nephritis.
- Healthy controls.
- Disease controls.
- Active versus inactive disease.
- Treated versus untreated samples.
- Renal versus non-renal involvement.

Ambiguous labels remain `TODO` or trigger rejection if they prevent feasibility assessment.

### Single-Cell Assay Verification Rules

A candidate must not be treated as single-cell data unless source metadata indicate a single-cell or single-nucleus transcriptomics assay. Acceptable evidence may include platform, library strategy, processed object description, cell barcode matrices, or source text that explicitly states scRNA-seq, snRNA-seq, single-cell RNA sequencing, or single-nucleus RNA sequencing.

Do not classify sorted bulk, pseudo-bulk, microarray, or bulk RNA-seq as single-cell transcriptomics.

### Lupus Nephritis-Specific Checks

For lupus nephritis candidates, manually check:

- Kidney, renal biopsy, urine, PBMC, or other tissue/sample source.
- Lupus nephritis class if available.
- Renal involvement criteria.
- Active nephritis versus inactive or historical nephritis.
- Matched blood and kidney samples if present.
- Treatment timing relative to biopsy or sampling.

Missing nephritis-specific metadata must be recorded as `TODO`.

### Raw-Data Vs Processed-Object Checks

For each candidate, record separately:

- Raw count matrix availability.
- FASTQ availability or controlled-access status.
- Processed matrix availability.
- AnnData, Seurat, loom, HDF5, Matrix Market, or other object availability.
- Cell-level metadata availability.
- Gene identifier format.
- Whether processed objects can be linked to raw data and sample metadata.

Do not download full raw or processed objects before Human Gate 1 approval.

### External Validation Suitability Checks

Assess whether the candidate could serve as a discovery cohort, validation cohort, or neither.

External validation suitability requires:

- Independent cohort or study source.
- Comparable disease and control labels.
- Compatible tissue or sample type.
- Compatible assay type.
- Sufficient patient-level metadata.
- No obvious cohort overlap with the discovery candidate.

If suitability is unclear, record `TODO`.

### GEO / NCBI Rejection Rules

Reject a GEO / NCBI candidate if:

- The accession is not explicit.
- `audit_status` is missing.
- Any row is added by script-generated inference rather than manual source review.
- Full data download is needed to answer basic metadata questions.
- The assay is not verified as single-cell or single-nucleus transcriptomics.
- Disease labels are absent, guessed, or incompatible with SLE / lupus / lupus nephritis feasibility.
- Human Gate 1 is used as if approved when it remains PENDING.

## Risks And Limitations

- Public lupus single-cell datasets may have limited patient-level metadata.
- Treatment, disease activity, renal involvement, and batch variables may be missing or confounded.
- Processed annotations may not be reproducible from raw data.
- Access terms may limit reuse or redistribution.
- Multiple publications may describe overlapping cohorts.
- Candidate datasets may require controlled-access approval.
- Search results may mix bulk, spatial, sorted-cell, and single-cell assays.

## Audit Workflow

1. Confirm `metadata/dataset_catalog.csv` schema before recording candidates.
2. Review search terms and sources in `configs/data_audit.yaml`.
3. Search approved public sources manually or with a later approved search tool.
4. Record only verified candidates and mark unknown fields as `TODO`.
5. Reject or defer candidates that do not meet inclusion criteria.
6. Summarize feasible, infeasible, and unresolved candidates in `reports/tables/dataset_feasibility_table.csv`.
7. Request Human Gate 1 review before data acquisition.

## Judge Rejection Rules

Engineering judge rejects if:

- Audit scripts query the internet in this scaffold.
- Tests require network access.
- The script invents rows or modifies source catalog data without review.
- Modeling files are introduced.

Scientific judge rejects if:

- Dataset accessions are guessed.
- Disease labels are accepted without source evidence.
- SLE and lupus nephritis labels are conflated without justification.
- Feasibility conclusions are made before metadata review.

Bioinformatics judge rejects if:

- Bulk RNA-seq is treated as single-cell data.
- Patient IDs, cell counts, assay chemistry, or annotations are assumed.
- Raw and processed data availability are not distinguished.
- Batch and donor structure are not evaluated.

Reproducibility judge rejects if:

- Unknowns are left blank instead of marked `TODO`.
- Source URLs, access terms, or verification dates are missing for claimed candidates.
- Human Gate 1 approval is bypassed.
- Full datasets are downloaded before approval.
