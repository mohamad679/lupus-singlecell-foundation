# P1-F012 Bioinformatics Judge Report

Current feature: P1-F012 - Bioinformatics Judge review of metadata validity.

Decision boundary: No dataset is approved. Human Gate 1 remains PENDING. No data files were downloaded. All candidates remain `candidate_pending_audit`.

## Review Inputs

- `reports/tables/manual_metadata_audit_summary.csv`
- `reports/tables/geo_candidate_datasets.csv`
- `reports/tables/cellxgene_candidate_datasets.csv`
- `reports/tables/scientific_judge_dataset_review.csv`
- `reports/final_dataset_feasibility_report.md`
- `metadata/patient_metadata_schema.yaml`
- `metadata/label_availability_schema.yaml`
- `metadata/external_validation_criteria.yaml`

## Cross-Candidate Bioinformatics Findings

All current candidates are human single-cell transcriptomics candidates with SLE or lupus relevance. PBMC/blood tissue is biologically relevant for circulating immune-cell analysis, but the current metadata do not support any immediate modeling or external-validation use.

The strongest bioinformatics candidates for continued audit are `GSE137029` and the linked CELLxGENE/HCA record because they have large PBMC/blood scale and visible public metadata. They are not independent until overlap among GEO, HCA, and CELLxGENE records is reconciled.

Raw-count and processed-object claims remain source-specific. GEO candidates have source-level raw or processed availability statements, but no files were downloaded and matrix contents were not inspected. `GSE174188` is controlled-access. CELLxGENE/HCA exposes `raw.X`, donor IDs, cell-type labels, and an H5AD asset in metadata, but the asset was not downloaded and sample/batch metadata remain unresolved.

Gene identifier and pathway-analysis feasibility cannot be fully judged until gene identifiers, count layers, normalization state, and feature mapping are inspected from source metadata or approved downstream files.

## Candidate Assessments

### GSE162577

Recommendation: `limited_candidate`

- Assay validity: 10X Genomics single-cell RNA sequencing is source-verified.
- Tissue suitability: PBMC is relevant for circulating immune-cell SLE analysis.
- Human organism verification: `Homo sapiens` is verified.
- Raw counts availability: raw SRA data are visible in GEO metadata, but raw count matrix contents were not downloaded or inspected.
- Processed object availability: supplementary MTX/TSV processed files are visible in GEO metadata, but contents are not audited.
- Donor metadata quality: weak; only 2 SLE patients and 1 healthy volunteer are visible, and patient IDs remain unclear.
- Cell-type label availability: unclear from current project metadata.
- Gene identifier feasibility: needs manual verification from MTX/TSV feature metadata.
- Pathway enrichment feasibility: limited and not ready; gene identifiers and cell-level QC are unaudited.
- Cross-cohort harmonization feasibility: poor at this stage because sample size is very small and batch metadata are unclear.
- Biological interpretation feasibility: limited candidate for qualitative context only after metadata verification.
- Main blockers: very small cohort, patient IDs unclear, n_cells TODO, cell-type labels unclear, batch metadata unclear.

### GSE137029

Recommendation: `continue_audit`

- Assay validity: multiplexed scRNA-seq is source-verified.
- Tissue suitability: PBMC is relevant for SLE immune-cell analysis.
- Human organism verification: `Homo sapiens` is verified.
- Raw counts availability: raw data are visible through SRA metadata; no data were downloaded.
- Processed object availability: processed data are visible on the GEO Series record; contents are not audited.
- Donor metadata quality: promising by scale, but patient/sample identifiers are not audited.
- Cell-type label availability: unclear from current project metadata.
- Gene identifier feasibility: likely assessable after approved metadata/file inspection, but not verified in the current tables.
- Pathway enrichment feasibility: potentially feasible after gene identifiers, raw/normalized layer, and cell-type labels are verified.
- Cross-cohort harmonization feasibility: unresolved because HCA/CELLxGENE overlap and batch/cohort metadata must be reconciled.
- Biological interpretation feasibility: promising for PBMC immune-cell biology after annotation and metadata verification.
- Main blockers: patient IDs unclear, cell-type labels not audited, activity/treatment/batch metadata unclear, overlap with linked HCA/CELLxGENE records.

### GSE174188

Recommendation: `needs_manual_verification`

- Assay validity: multiplexed scRNA-seq is source-verified.
- Tissue suitability: PBMC is relevant for SLE immune-cell analysis.
- Human organism verification: `Homo sapiens` is verified.
- Raw counts availability: controlled-access only according to current audit.
- Processed object availability: controlled-access only; open processed object availability is not assumed.
- Donor metadata quality: unresolved; subject/sample metadata require dbGaP/access review.
- Cell-type label availability: unclear from current project metadata.
- Gene identifier feasibility: blocked until controlled-access metadata or approved files can be reviewed.
- Pathway enrichment feasibility: not ready because raw/processed data access and gene identifiers are unresolved.
- Cross-cohort harmonization feasibility: unresolved because controlled-access status and overlap with GEO/HCA/CELLxGENE records must be assessed.
- Biological interpretation feasibility: potentially high if access and metadata are resolved, but not valid for current use.
- Main blockers: controlled-access data, patient IDs unclear, processed object not openly verified, treatment/batch metadata unclear, overlap risk unresolved.

### CELLxGENE / HCA Lupus PBMC-Linked Project

Candidate ID: `436154da-bcf1-4130-9c8b-120ff9a888f2::218acb0f-9f2f-4f76-b90b-15a4b7c7f629`

Recommendation: `continue_audit`

- Assay validity: 10x 3' v2 is source-verified in CELLxGENE metadata.
- Tissue suitability: blood/PBMC-linked metadata are relevant for circulating immune-cell SLE analysis.
- Human organism verification: `Homo sapiens` is verified.
- Raw counts availability: `raw.X` is visible in CELLxGENE metadata; no asset was downloaded.
- Processed object availability: H5AD asset visibility is documented; no processed object was downloaded or inspected.
- Donor metadata quality: donor IDs are visible, but donor-level split usability and sample IDs are unresolved.
- Cell-type label availability: cell-type labels are visible in CELLxGENE metadata.
- Gene identifier feasibility: likely feasible after approved inspection of H5AD feature metadata, but not fully audited yet.
- Pathway enrichment feasibility: promising after gene identifiers, raw count layer, and cell-type annotations are verified.
- Cross-cohort harmonization feasibility: unresolved because the collection links to GEO/HCA records and must be deduplicated before any cross-cohort use.
- Biological interpretation feasibility: strongest current candidate for continued audit because donor IDs, cell count, cell-type labels, and raw layer metadata are visible.
- Main blockers: sample IDs unclear, label provenance unclear, activity/treatment/batch metadata unclear, and GEO/HCA/CELLxGENE overlap unresolved.

## Recommendation Summary

| candidate | recommendation |
| --- | --- |
| GSE162577 | limited_candidate |
| GSE137029 | continue_audit |
| GSE174188 | needs_manual_verification |
| CELLxGENE / HCA lupus PBMC-linked project | continue_audit |

No candidate satisfies the full bioinformatics requirements for future analysis yet. Required next checks are donor/sample metadata verification, cell-type annotation provenance, gene identifier review, raw/processed layer validation, batch/cohort metadata audit, and cross-cohort deduplication.
