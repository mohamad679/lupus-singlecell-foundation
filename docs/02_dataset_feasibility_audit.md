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

## CELLxGENE Metadata Feasibility Protocol

### Search Objectives

Identify CELLxGENE Census or related public CELLxGENE collection metadata that may describe SLE, lupus, or lupus nephritis single-cell datasets. This is a metadata-only feasibility plan and does not perform live CELLxGENE queries, full data downloads, model implementation, or model training.

Do not populate `metadata/dataset_catalog.csv` from CELLxGENE candidates until manual metadata verification is complete.

### Query Terms

Use these terms for planned CELLxGENE metadata searches:

- `lupus`
- `systemic lupus erythematosus`
- `SLE`
- `lupus nephritis`
- `autoimmune`
- `PBMC`
- `kidney`

### Metadata Fields To Inspect

For each candidate, use `metadata/cellxgene_candidate_schema.yaml` and inspect:

- `collection_id`
- `dataset_id`
- `title`
- `source`
- `publication`
- `organism`
- `tissue`
- `assay_type`
- `disease_context`
- `lupus_subtype`
- `n_donors`
- `n_samples`
- `n_cells`
- `donor_id_available`
- `sample_id_available`
- `disease_label_available`
- `activity_label_available`
- `treatment_info_available`
- `batch_info_available`
- `cell_type_labels_available`
- `raw_count_available`
- `processed_object_available`
- `notes`
- `audit_status`

Rows must not be added unless `collection_id`, `dataset_id`, and `audit_status` are explicit. Candidate rows that are not yet manually verified must use `candidate_pending_audit`.

### Disease Ontology Checks

Manual review must determine whether CELLxGENE disease metadata use ontology-backed disease terms, free text, publication labels, or collection-specific annotations.

Required checks:

- Whether disease terms explicitly identify SLE, systemic lupus erythematosus, lupus, lupus nephritis, or a relevant autoimmune comparator.
- Whether ontology IDs are present and interpretable.
- Whether disease labels are available at donor, sample, or cell level.
- Whether healthy controls and disease controls can be distinguished.
- Whether ambiguous autoimmune labels should remain `TODO` or be rejected.

### Tissue And Assay Checks

Manual review must verify:

- Tissue or sample source, such as PBMC, blood, kidney, urine, renal biopsy, or TODO.
- Assay type, such as scRNA-seq, snRNA-seq, or TODO.
- Whether the object represents single-cell or single-nucleus transcriptomics rather than bulk or aggregate data.
- Whether cell type labels are available and whether they are source-provided or computationally inferred.

### Patient-Level Metadata Requirements

CELLxGENE candidates must be assessed for donor-level and sample-level metadata without guessing labels from cell names or sample names.

Required checks:

- Donor ID availability.
- Sample ID availability.
- Donor-to-sample mapping.
- Disease label availability.
- Activity label availability.
- Treatment metadata availability.
- Batch or cohort metadata availability.
- Whether donor metadata are preserved in the public collection.

### Donor And Sample Availability Checks

The audit must separately record:

- Number of donors.
- Number of samples.
- Number of cells.
- Whether donor IDs are stable across tissues or assays.
- Whether sample IDs are stable across collection metadata and object metadata.
- Whether donor or sample counts are source-provided or TODO.

Counts must not be guessed from filenames or collection titles.

### SLE / Lupus Nephritis Relevance Checks

Manual review must determine whether a candidate is relevant to:

- SLE without kidney-specific metadata.
- Lupus nephritis.
- Kidney or renal biopsy data.
- PBMC or blood immune profiling.
- Autoimmune comparator cohorts that could support validation or rejection.

For lupus nephritis, check renal involvement, nephritis class, active nephritis labels, biopsy timing, and treatment timing when available. Missing details remain `TODO`.

### Raw-Data And Processed-Object Checks

For CELLxGENE candidates, record:

- Whether raw counts are available through CELLxGENE metadata or linked source metadata.
- Whether the public object is processed only.
- Whether processed object access is metadata-only, previewable, or requires full download.
- Whether gene identifiers and cell metadata are documented.
- Whether source publication or collection links point to raw data elsewhere.

Do not download full data before Human Gate 1 approval.

### External Validation Suitability Checks

Assess whether each CELLxGENE candidate could be a discovery cohort, external validation cohort, or neither.

Suitability requires:

- Independent collection or source publication.
- Compatible disease and control labels.
- Compatible tissue and assay type.
- Sufficient donor and sample metadata.
- No unresolved overlap with another candidate cohort.

If suitability cannot be established from metadata, record `TODO`.

### CELLxGENE Rejection Rules

Reject or defer a CELLxGENE candidate if:

- `collection_id`, `dataset_id`, or `audit_status` is missing.
- Disease labels are guessed or too broad to support SLE / lupus / lupus nephritis feasibility.
- Donor or sample labels are inferred rather than source-provided.
- The assay is not single-cell or single-nucleus transcriptomics.
- Full data download is required before basic metadata feasibility can be assessed.
- Human Gate 1 is treated as approved while it remains PENDING.

## Dataset Eligibility Scoring Framework

### Scoring Objective

Evaluate whether candidate SLE, lupus, or lupus nephritis single-cell datasets are usable for training, internal validation, external cross-cohort validation, disease-activity prediction, and biological interpretation.

This framework defines scoring criteria only. Numerical scoring must not be applied to empty, unaudited, guessed, or unverifiable candidate rows. Human Gate 1 remains required before data acquisition or modeling.

### Scoring Dimensions

Total score: 100 points.

- Core Dataset Validity: 25 points.
- Prediction Task Feasibility: 20 points.
- Patient-level Modeling Feasibility: 20 points.
- Cross-cohort Validation Suitability: 15 points.
- Bioinformatics Interpretability: 10 points.
- Reproducibility and Accessibility: 10 points.

### Required Vs Optional Criteria

Required criteria protect against invalid scientific use:

- Single-cell or single-nucleus assay verification.
- Human organism.
- SLE, lupus, or lupus nephritis relevance.
- Patient or donor identifiers.
- Disease labels.
- Source-verifiable metadata.
- Clear accession, collection ID, or dataset ID.

Optional or strengthening criteria improve score but do not alone determine eligibility:

- Activity labels.
- Treatment metadata.
- Longitudinal or repeated samples.
- External validation cohort compatibility.
- Cell-type labels.
- Raw counts and processed object availability.
- Publication, license, and access clarity.

### Minimum Thresholds

Eligibility categories are:

- Excellent: score >= 80.
- Usable with caution: score 60-79.
- Limited: score 40-59.
- Reject: score < 40.

These categories are not sufficient to start modeling. They only support Human Gate 1 review.

### Exclusion Rules

Hard rejection applies when any of the following are true:

- Dataset is not single-cell or single-nucleus transcriptomics.
- Dataset is not human.
- Patient or donor IDs are unavailable.
- Disease labels are unavailable.
- Metadata are invented, guessed, or unverifiable.
- Dataset is bulk RNA-seq only.
- Accession or source identity is ambiguous.

### External Validation Suitability Rules

A candidate is suitable for external cross-cohort validation only if it is independent from the discovery cohort and has compatible tissue, assay, labels, donor/sample metadata, and batch/cohort metadata. If cohort overlap is unresolved, suitability remains `TODO`.

### Lupus Nephritis-Specific Scoring Considerations

Lupus nephritis candidates should score higher when metadata distinguish renal involvement, nephritis class, biopsy timing, active nephritis status, treatment timing, kidney or renal biopsy source, and matched blood/kidney samples when available.

Missing lupus nephritis subtype or renal activity metadata should be marked `TODO` and may limit disease-specific usability.

### Activity-Label Scoring Considerations

Disease-activity prediction requires source-supported activity labels, activity scores, active/inactive status, flare/remission annotations, or a documented clinical proxy. Treatment metadata and sampling time are required to judge confounding.

If activity labels are absent or guessed, disease-activity prediction suitability must remain `TODO` or reject.

### Uncertainty And Calibration Relevance

Datasets intended for prediction should contain enough independent patients, controls or comparator groups, and batch metadata to support calibrated uncertainty estimates and leakage-aware evaluation. Small or confounded cohorts may remain useful for interpretation but should not be marked suitable for predictive training without review.

### Biological Interpretation Relevance

Biological interpretation suitability depends on cell-type labels, gene identifiers, tissue relevance, raw counts or normalized matrix availability, and support for pathway or signature analysis. Interpretability cannot compensate for missing disease labels, non-human data, or unverifiable metadata.

## Patient-level Metadata Audit Framework

### Why Patient-level Metadata Matters

Patient-level metadata determine whether a candidate single-cell lupus dataset can support patient-level prediction, leakage-free cohort splitting, external validation, and interpretable biological claims. Cell-level records alone are not sufficient because cells from the same patient are correlated and must not be split across training and evaluation sets.

### Leakage Risks

Major leakage risks include:

- Splitting cells from the same patient across training and validation partitions.
- Inferring patient IDs from sample names instead of using source-provided identifiers.
- Mixing repeated samples from the same patient across partitions.
- Ignoring batch, cohort, site, chemistry, or processing identifiers.
- Treating treatment or disease activity labels as independent when they are confounded by patient, cohort, or timepoint.

Cell-level splitting is forbidden for feasibility planning.

### Donor Vs Sample Distinction

The audit must distinguish patient, donor, and sample identifiers. A donor can have multiple samples, tissues, timepoints, or batches. A sample can contain many cells. Patient-level prediction requires source-supported mapping from cells to samples and samples to patients or donors.

If the source only provides sample IDs but no patient or donor mapping, patient-level splitting remains unsupported.

### Repeated Samples

Repeated samples from the same patient must be tracked so they are grouped during splitting. Multiple tissues, technical replicates, sorted fractions, or library preparations from one patient must not be treated as independent patients.

### Longitudinal Samples

Longitudinal samples require explicit timepoint metadata such as visit, flare, remission, pre-treatment, post-treatment, or other source-defined timing. Disease-activity prediction requires documenting whether labels are contemporaneous with sampling.

### Cohort Identifiers

Cohort identifiers are required to identify discovery versus validation cohorts, multi-study merges, and possible cohort overlap across GEO, CELLxGENE, Human Cell Atlas, or publication-hosted repositories.

### Batch Identifiers

Batch identifiers should capture source-provided batch, site, library, chemistry, sequencing run, processing workflow, or cohort variables. Missing batch metadata limits leakage control and confounding assessment.

### Disease Labels

Disease labels must be source-supported and must distinguish SLE, lupus nephritis, healthy controls, and disease controls when available. Labels must not be guessed from titles, filenames, or broad autoimmune annotations.

### Disease Activity Labels

Disease activity labels may include disease activity scores, active/inactive status, flare/remission labels, renal activity, lupus nephritis class, or documented clinical proxies. Missing activity labels should be recorded as `TODO` and may make disease-activity prediction infeasible.

### Treatment Metadata

Treatment metadata should record exposure, timing, and status at sampling when available. Treatment can confound disease activity, cell state, and cohort differences, so unknown treatment status must be marked `TODO`.

### External Validation Requirements

External validation requires independent patient groups with compatible tissue, assay, disease labels, donor/sample mappings, and batch/cohort metadata. A validation cohort must not be only a cell-level split or sample-level split from the same patients unless human review explicitly approves that limitation.

### Rejection Rules

Reject or defer a candidate for patient-level prediction if:

- Patient or donor identifiers are missing.
- Patient IDs are inferred instead of source-provided.
- Disease labels are missing or guessed.
- Samples from the same patient cannot be grouped.
- Cohort or batch metadata are too ambiguous to assess leakage.
- Activity prediction is proposed without activity labels.
- Any candidate requires dataset download before basic patient metadata feasibility can be assessed.
- Human Gate 1 is treated as approved while it remains PENDING.

## Label Availability Audit Framework

### Why Label Audit Is Required Before Task Selection

Prediction tasks must be selected only after labels are verified at the correct biological and clinical level. A dataset can be scientifically useful for interpretation while still being unusable for diagnosis, disease activity, lupus nephritis, treatment, or external validation tasks. Label feasibility must be audited before any modeling begins.

### Label Provenance Rules

Every label must have explicit provenance from source metadata, supplementary files, curated public collection metadata, or publication text. Labels must not be inferred from dataset titles, accessions, tissue names, cell types, file names, or general disease context.

Unknown label provenance must be recorded as `TODO`. Labels without provenance cannot support training, validation, task selection, or scientific claims.

### Diagnosis Label Requirements

Diagnosis labels must distinguish cases and comparators at patient or donor level where possible.

Diagnosis / case-control prediction tasks to audit:

- SLE vs healthy control.
- Lupus nephritis vs control.
- SLE vs other autoimmune disease if available.

Minimum requirements:

- Patient-level or donor-level diagnosis labels.
- Source-supported control or comparator labels.
- Counts of labeled patients and samples.
- Clear label provenance.

### Disease Activity Label Requirements

Disease activity prediction requires explicit metadata or publication evidence for active/inactive status, SLEDAI-derived categories, flare/remission status, or another documented activity score or proxy.

Disease activity tasks to audit:

- Active vs inactive SLE.
- SLEDAI-based category if available.
- Flare vs remission if explicitly available.

Disease activity labels must not be inferred from treatment, tissue, cohort, or sampling time unless the source explicitly defines that relationship.

### Lupus Nephritis Label Requirements

Lupus nephritis labels must be source-supported and separated from general SLE diagnosis labels.

Lupus nephritis tasks to audit:

- Lupus nephritis vs non-nephritis SLE.
- Kidney compartment or tissue if available.
- Histologic class if explicitly available.

Kidney tissue alone does not prove nephritis status. Histologic class and renal activity must remain `TODO` unless explicitly available.

### Treatment Label Requirements

Treatment-related labels must include source-supported treatment status, medication exposure, treatment timing, or treatment response definitions.

Treatment-related tasks to audit:

- Treated vs untreated.
- Treatment response if explicitly available.
- Medication exposure if available.

Treatment labels must not be inferred from cohort name, disease severity, or publication focus.

### Flare And Remission Label Requirements

Flare and remission labels require explicit source definitions. If flare/remission status is tied to a score threshold, the threshold and score name must be recorded. Ambiguous activity wording must remain `TODO`.

### Control And Comparator Requirements

Control groups must be source-defined and distinguishable from cases. The audit must record whether controls are healthy controls, disease controls, other autoimmune disease controls, non-nephritis SLE comparators, or another comparator type.

### Ambiguous Label Handling

Ambiguous labels must be marked with `ambiguity_flag` and `ambiguity_reason`. Ambiguous labels cannot be treated as usable for training or external validation until manually resolved. If ambiguity affects disease activity, lupus nephritis status, or treatment response, the corresponding prediction task remains infeasible.

### Minimum Label Requirements Per Prediction Task

Diagnosis / case-control prediction requires:

- Diagnosis label.
- Control or comparator group.
- Patient-level or donor-level availability.
- Label provenance.

Disease activity prediction requires:

- Disease activity label or named score.
- Patient-level or sample-level availability with patient mapping.
- Activity score name when applicable.
- Treatment metadata or explicit TODO for treatment confounding.

Lupus nephritis task requires:

- Lupus nephritis status.
- Non-nephritis or control comparator.
- Tissue or compartment context when relevant.
- Histologic class only when explicitly available.

Treatment-related task requires:

- Treatment status, medication exposure, or treatment response label.
- Timing relative to sampling when available.
- Source-defined response criteria for response tasks.

### Rejection Rules

Reject or defer label use for prediction if:

- `dataset_id`, `prediction_task`, `label_type`, `label_provenance`, or `audit_status` is missing.
- Label provenance is absent, ambiguous, or guessed.
- Disease activity labels are inferred rather than explicit.
- Labels are cell-level only for patient-level prediction.
- Control or comparator groups are unavailable for case-control tasks.
- Lupus nephritis status is inferred from kidney tissue alone.
- Treatment response lacks a source definition.
- Human Gate 1 is treated as approved while it remains PENDING.

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
