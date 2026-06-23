# P1-F011 Scientific Judge Report

Current feature: P1-F011 - Scientific Judge review of dataset feasibility.

Decision boundary: No dataset is approved. Human Gate 1 remains PENDING. All candidates remain `candidate_pending_audit`.

## Review Inputs

- `reports/tables/manual_metadata_audit_summary.csv`
- `reports/tables/geo_candidate_datasets.csv`
- `reports/tables/cellxgene_candidate_datasets.csv`
- `reports/tables/dataset_eligibility_scores.csv`
- `reports/final_dataset_feasibility_report.md`
- `metadata/dataset_eligibility_scoring.yaml`
- `metadata/patient_metadata_schema.yaml`
- `metadata/label_availability_schema.yaml`
- `metadata/external_validation_criteria.yaml`

## Cross-Candidate Findings

The candidates satisfy several core dataset-validity signals: human organism, single-cell transcriptomics context, lupus/SLE relevance, and PBMC or blood tissue for most records. None currently satisfies the required patient-level, label-level, external-validation, and leakage-prevention evidence needed for dataset approval.

Patient-level feasibility is unresolved because source-verified patient/donor/sample mappings are not fully audited into a patient metadata table. The CELLxGENE/HCA row exposes donor IDs in metadata, but donor-level modeling usability is still unverified and sample-level metadata remain unclear.

Label feasibility is incomplete. Source-level SLE or normal/control terms are visible, but patient-level label provenance, disease activity labels, treatment labels, lupus nephritis labels, and activity-score names remain unresolved.

External validation feasibility is unresolved for every candidate. The strongest large PBMC candidates appear related across GEO, HCA, and CELLxGENE records, so cohort independence cannot be assumed. No candidate should be assigned an external validation role before deduplication and cohort-overlap audit.

Leakage risk remains high until patient, donor, sample, batch, and cohort identifiers are verified. Cell-level splitting is not acceptable under the project rules.

Cohort-shift risk cannot be assessed yet because batch/site/cohort metadata and compatible label definitions have not been manually resolved.

Disease-activity prediction is not feasible yet. Active flare text is visible for GSE137029, but patient/sample-level activity labels are not audited. SLEDAI, flare/remission, or equivalent score fields are not source-verified in the project tables.

Lupus nephritis prediction is not feasible from the current candidate audit. No candidate has audited lupus nephritis status, renal tissue, kidney compartment, or histologic class labels.

## Candidate Assessments

### GSE162577

Scientific status: `limited_candidate`

Verified evidence: Human PBMC 10X Genomics single-cell RNA sequencing, SLE context, 2 SLE patients, 1 healthy volunteer, 3 samples, raw SRA visibility, and processed MTX/TSV supplementary file visibility.

Patient-level feasibility: Limited. The cohort is too small for meaningful patient-level model development, and patient ID availability remains unclear.

Label feasibility: Limited. Diagnosis context is visible, but patient-level label provenance and disease-activity labels remain unclear.

External validation feasibility: Not feasible at this stage. The cohort is too small and independence against other candidates is not established.

Leakage risk: High until patient/sample IDs and batch metadata are verified.

Cohort-shift risk: Not assessable from current metadata.

Disease-activity prediction feasibility: Not feasible from current audit.

Lupus nephritis feasibility: Not feasible from current audit.

Data-access risk: Moderate. Public metadata and supplementary file visibility are noted, but full data were not downloaded and content is not audited.

Recommendation: Keep as a limited candidate for methods sanity checks or biological context only after manual verification. Do not use for training or external validation without Human Gate 1 approval.

### GSE137029

Scientific status: `continue_audit`

Verified evidence: Human PBMC multiplexed scRNA-seq, SLE cases, healthy controls, 66 samples, approximately 1 million PBMCs, raw SRA visibility, processed Series data visibility, and source text mentioning active disease flares.

Patient-level feasibility: Potentially promising but unresolved. Patient identifiers, sample mappings, and leakage-prevention metadata are not yet audited.

Label feasibility: Diagnosis labels appear source-supported at the study level. Disease-activity label usability remains unclear because flare text is not yet mapped to patient/sample-level labels.

External validation feasibility: Not assignable yet. The candidate likely overlaps with HCA/CELLxGENE lupus PBMC resources and requires provenance reconciliation.

Leakage risk: High until donor/sample identifiers, batch labels, and cohort labels are verified.

Cohort-shift risk: Unresolved. Batch, site, and processing metadata must be audited before cross-cohort claims.

Disease-activity prediction feasibility: Needs manual verification. Flare-related text is promising but insufficient.

Lupus nephritis feasibility: Not feasible from current audit.

Data-access risk: Moderate. Public raw and processed data are visible in metadata, but files were not downloaded or inspected.

Recommendation: Continue audit as a leading candidate for case-control feasibility if patient-level identifiers, labels, and batch metadata can be verified.

### GSE174188

Scientific status: `needs_manual_verification`

Verified evidence: Human PBMC multiplexed scRNA-seq, SLE cases, controls, over 1.2 million PBMCs, 88 samples, and related dbGaP study `phs002812.v1.p1`.

Patient-level feasibility: Unresolved. Patient ID availability and subject/sample metadata are not audited.

Label feasibility: Diagnosis context is visible, but patient-level label provenance, disease activity labels, treatment labels, and batch metadata remain unclear.

External validation feasibility: Not assignable yet. Controlled-access status and potential overlap with related GEO/HCA/CELLxGENE records block validation-role assignment.

Leakage risk: High until access-controlled subject, sample, and cohort metadata are reviewed under approved access.

Cohort-shift risk: Unresolved.

Disease-activity prediction feasibility: Not feasible from current audit.

Lupus nephritis feasibility: Not feasible from current audit.

Data-access risk: High. GEO indicates raw and processed data are controlled-access through dbGaP and not provided on the GEO record.

Recommendation: Needs manual verification of dbGaP access, allowed-use constraints, subject/sample metadata, processed object availability, and cohort overlap before continuing.

### CELLxGENE / HCA Lupus PBMC-Linked Project

Scientific status: `continue_audit`

Candidate ID: `436154da-bcf1-4130-9c8b-120ff9a888f2::218acb0f-9f2f-4f76-b90b-15a4b7c7f629`

Verified evidence: CELLxGENE/HCA metadata show human blood, 10x 3' v2, normal and systemic lupus erythematosus disease terms, visible donor IDs, 261 donors, 1,263,676 cells, cell type labels, `raw.X`, and a visible H5AD asset.

Patient-level feasibility: Potentially promising but unresolved. Donor IDs are visible, but donor-level split usability and sample-level mappings remain unaudited.

Label feasibility: Diagnosis disease terms are visible. Patient-level label provenance, activity labels, treatment labels, and lupus nephritis labels remain unclear.

External validation feasibility: Not assignable yet. The record appears linked to GSE137029/GSE174188/HCA and must be deduplicated before any external validation role.

Leakage risk: High until donor/sample/cohort/batch mappings are audited.

Cohort-shift risk: High if treated as independent from linked GEO/HCA records without deduplication.

Disease-activity prediction feasibility: Not feasible from current audit.

Lupus nephritis feasibility: Not feasible from current audit.

Data-access risk: Moderate. H5AD and FASTQ metadata are visible, but no full data were downloaded and use remains gated.

Recommendation: Continue audit as a leading metadata-rich candidate, with priority on donor/sample mapping, provenance reconciliation, label audit, and batch metadata.

## Judge Recommendation Summary

| candidate | recommendation |
| --- | --- |
| GSE162577 | limited_candidate |
| GSE137029 | continue_audit |
| GSE174188 | needs_manual_verification |
| CELLxGENE / HCA lupus PBMC-linked project | continue_audit |

No candidate is ready for modeling, training, external validation, disease-activity prediction, or lupus nephritis prediction. Human Gate 1 must remain PENDING until patient-level metadata, label availability, access conditions, and cohort overlap are manually resolved.
