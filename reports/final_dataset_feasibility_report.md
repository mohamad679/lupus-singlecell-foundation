# Final Dataset Feasibility Report

## 1. Executive Summary

TODO: Human Gate 1 remains PENDING. No dataset has been approved.

## 2. Scientific Goal

TODO: Define the final scientific goal after candidate datasets are manually audited.

## 3. Search Sources

- GEO: TODO candidate rows added for GSE162577, GSE137029, and GSE174188 pending manual audit.
- CELLxGENE: TODO candidate row added for collection `436154da-bcf1-4130-9c8b-120ff9a888f2`, dataset `218acb0f-9f2f-4f76-b90b-15a4b7c7f629`, pending manual audit.
- Human Cell Atlas: TODO HCA project link identified from CELLxGENE/GSE137029 metadata: `https://explore.data.humancellatlas.org/projects/9fc0064b-84ce-40a5-a768-e6eb3d364ee0`.
- Published AnnData/Seurat objects: TODO.

## 4. Candidate Dataset Table

| accession | source | tissue | assay | disease context | number of patients | labels available | patient IDs available | external validation suitability | eligibility score | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GSE162577 | GEO / NCBI | PBMC | 10X Genomics single cell RNA sequencing | SLE PBMC | 2 SLE patients + 1 healthy volunteer | diagnosis yes; activity unclear | unclear | TODO | TODO | candidate_pending_audit |
| GSE137029 | GEO / NCBI | PBMC | multiplexed single-cell RNA-seq | SLE and healthy controls | 134 SLE cases + 58 healthy controls; 15 active flare cases also described | diagnosis visible in source; activity usability unclear | unclear | TODO | TODO | candidate_pending_audit |
| GSE174188 | GEO / NCBI | PBMC | multiplexed single-cell RNA-seq | SLE and healthy controls | 162 SLE donors + 99 healthy individuals | diagnosis yes; activity unclear | unclear | TODO | TODO | candidate_pending_audit |
| 436154da-bcf1-4130-9c8b-120ff9a888f2 / 218acb0f-9f2f-4f76-b90b-15a4b7c7f629 | CELLxGENE | blood | 10x 3' v2 | normal; systemic lupus erythematosus | TODO | source disease terms visible; label usability unclear | unclear | TODO | TODO | candidate_pending_audit |

## Candidate Provenance and Caution Notes

### GSE162577

- Source URL: `https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE162577`
- Verified: public GEO record, human organism, SLE/PBMC context, and single-cell RNA sequencing metadata.
- Unclear: patient ID availability, patient-level label usability, activity labels, batch metadata, and full task suitability.
- Not approved because manual patient-level metadata and label audit are incomplete.
- Training or external validation use: TODO; possible only after Human Gate 1 review and explicit metadata audit approval.

### GSE137029

- Source URL: `https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE137029`
- Related HCA project URL: `https://explore.data.humancellatlas.org/projects/9fc0064b-84ce-40a5-a768-e6eb3d364ee0`
- Verified: public GEO record, human organism, PBMC context, SLE/control source description, and single-cell RNA sequencing metadata.
- Unclear: patient-level usability, activity-label usability, treatment metadata, batch metadata, assay suitability for the target task, and any external validation role.
- Not approved because source-level metadata has not been converted into audited patient-level evidence.
- Training or external validation use: TODO; may support training or validation only after manual feasibility scoring and Human Gate 1 approval.

### GSE174188

- Source URL: `https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE174188`
- Related dbGaP URL: `https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id=phs002812.v1.p1`
- Verified: public GEO record, human organism, PBMC context, SLE/control source description, and multiplexed scRNA-seq metadata.
- Unclear: patient ID availability, activity-label usability, treatment metadata, batch metadata, open processed object availability, and whether controlled-access data can be used.
- Not approved because controlled-access/genotype-related availability creates an unresolved feasibility risk.
- Training or external validation use: TODO; not usable until access, labels, and patient-level metadata are manually audited.

### CELLxGENE Collection 436154da-bcf1-4130-9c8b-120ff9a888f2

- Source URL: `https://cellxgene.cziscience.com/collections/436154da-bcf1-4130-9c8b-120ff9a888f2`
- Dataset ID: `218acb0f-9f2f-4f76-b90b-15a4b7c7f629`
- Verified: public CELLxGENE collection metadata, human organism, blood tissue, 10x 3' v2 assay metadata, and visible disease terms for normal and systemic lupus erythematosus.
- Unclear: donor-level usability, sample-level usability, patient-level label provenance, activity labels, treatment metadata, batch metadata, and overlap with GEO/HCA records.
- Not approved because CELLxGENE metadata has not been reconciled against GEO/HCA provenance or patient-level audit requirements.
- Training or external validation use: TODO; candidate only after deduplication, label audit, and Human Gate 1 approval.

## Manual Metadata Audit Summary

### GSE162577

- Verified facts: GEO verifies `Homo sapiens`, PBMC, 10X Genomics single cell RNA sequencing, 2 SLE new onset patients without immunosuppressive drugs, 1 healthy volunteer, 3 samples, SRA raw data, and processed MTX/TSV supplementary files.
- Unresolved fields: patient ID availability, n_cells, activity labels, batch metadata, and patient-level label provenance.
- Training usability risk: patient-level split feasibility and label provenance are unresolved.
- External validation risk: cohort independence and patient-level metadata are unresolved.
- Label risk: diagnosis context is visible, but activity labels are unclear.
- Data access risk: public GEO/SRA metadata and supplementary file visibility are noted; no data were downloaded.
- Next manual checks needed: inspect sample metadata and publication tables for patient/sample IDs, disease labels, activity labels, cell counts, and batch variables.

### GSE137029

- Verified facts: GEO verifies `Homo sapiens`, PBMC, multiplexed scRNA-seq, approximately 1 million PBMCs, 134 SLE cases, 58 healthy controls, 66 samples, SRA raw data, processed data on the Series record, and source text mentioning active disease flares.
- Unresolved fields: patient ID availability, patient-level flare/activity mapping, treatment metadata, batch metadata, and whether labels are usable for patient-level prediction.
- Training usability risk: patient-level leakage prevention cannot be assessed yet.
- External validation risk: overlap with the HCA/CELLxGENE lupus PBMC project must be reconciled before assigning any validation role.
- Label risk: source-level diagnosis labels are visible; patient/sample-level activity labels remain unclear.
- Data access risk: public data files are visible but large; no data were downloaded.
- Next manual checks needed: verify donor/sample identifiers, flare labels, disease labels, treatment metadata, and batch/cohort metadata from source metadata and publication supplements.

### GSE174188

- Verified facts: GEO verifies `Homo sapiens`, PBMC, multiplexed scRNA-seq, over 1.2 million PBMCs, 162 SLE donors, 99 healthy individuals, 88 samples, and controlled-access raw/processed data availability through dbGaP; dbGaP `phs002812.v1.p1` reports a related case-control genotype study and 258 consented subjects.
- Unresolved fields: patient ID availability, activity labels, treatment metadata, batch metadata, open processed object availability, and controlled-access usability.
- Training usability risk: access and patient-level metadata are unresolved.
- External validation risk: controlled-access status and project overlap block any validation role assignment.
- Label risk: case-control disease context is visible; activity labels are unclear.
- Data access risk: raw and processed data are not provided on the GEO record and are controlled-access through dbGaP.
- Next manual checks needed: verify dbGaP access requirements, allowed uses, subject/sample metadata fields, label definitions, and processed object availability.

### CELLxGENE / HCA Lupus PBMC-Linked Project

- Verified facts: CELLxGENE collection metadata verifies collection `436154da-bcf1-4130-9c8b-120ff9a888f2`, dataset `218acb0f-9f2f-4f76-b90b-15a4b7c7f629`, `Homo sapiens`, blood tissue, 10x 3' v2 assay, normal and systemic lupus erythematosus disease terms, visible donor IDs, 1,263,676 cells, cell type labels, `raw.X`, and an H5AD asset; HCA lists blood/PBMC metadata, donor count 261, FASTQ file format, and links to GSE137029 and GSE174188.
- Unresolved fields: donor-level usability, sample ID availability, activity labels, treatment metadata, batch metadata, and overlap across GEO/HCA/CELLxGENE records.
- Training usability risk: donor-level split feasibility is not approved until metadata fields are reconciled.
- External validation risk: likely overlap with GEO/HCA records prevents treating it as an independent validation cohort without deduplication.
- Label risk: disease ontology terms are visible; patient-level label provenance and activity labels remain unclear.
- Data access risk: H5AD/FASTQ assets are visible in metadata, but no full data were downloaded and use remains gated.
- Next manual checks needed: reconcile collection, HCA, and GEO provenance; verify donor/sample IDs, label provenance, activity labels, treatment metadata, and batch metadata.

## Scientific Judge Review

No dataset is approved yet. Human Gate 1 remains PENDING, `selected_datasets` remains empty, and `external_validation_cohort` remains TODO.

Strongest candidates for continued audit:

- `GSE137029`: continue audit because it has visible human PBMC single-cell case/control metadata and large cohort scale, but patient identifiers, patient-level labels, activity labels, treatment metadata, batch metadata, and overlap with HCA/CELLxGENE records remain unresolved.
- `436154da-bcf1-4130-9c8b-120ff9a888f2::218acb0f-9f2f-4f76-b90b-15a4b7c7f629`: continue audit because CELLxGENE/HCA metadata expose donor IDs, disease terms, cell count, and cell type labels, but donor-level split usability, sample IDs, label provenance, activity labels, treatment metadata, batch metadata, and GEO/HCA/CELLxGENE deduplication remain unresolved.

Candidates requiring caution:

- `GSE162577`: limited candidate only. The record is scientifically relevant, but the cohort has 2 SLE patients and 1 healthy volunteer, patient IDs are unclear, n_cells is TODO, and activity labels are unclear.
- `GSE174188`: needs manual verification. It is large and scientifically relevant, but controlled-access dbGaP requirements, subject/sample metadata, processed-object access, and cohort overlap risks remain unresolved.

Candidates not suitable for immediate modeling:

- All current candidates are not suitable for immediate modeling, training, disease-activity prediction, lupus nephritis prediction, or external validation assignment.
- The current eligibility score table keeps all scores and usability fields as TODO.

Next required checks before Human Gate 1:

- Verify patient/donor/sample identifiers and whether patient-level splitting is possible.
- Verify patient-level disease labels, activity labels, treatment metadata, and label provenance.
- Verify batch, cohort, site, library, and processing metadata for leakage prevention.
- Reconcile overlap among GEO, HCA, and CELLxGENE records before any external validation decision.
- Resolve controlled-access constraints for `GSE174188` and dbGaP `phs002812.v1.p1`.
- Confirm whether any candidate includes lupus nephritis-specific labels, renal tissue, kidney compartment, or histologic class; current audit does not support lupus nephritis modeling.

## Bioinformatics Judge Review

No dataset is approved by the bioinformatics review. Human Gate 1 remains PENDING, `selected_datasets` remains empty, and `external_validation_cohort` remains TODO.

Strengths:

- All current candidates are human single-cell transcriptomics candidates with lupus/SLE relevance.
- PBMC or blood tissue is relevant for circulating immune-cell analysis in SLE.
- `GSE137029` has large public PBMC scale and visible raw/processed availability statements.
- The CELLxGENE/HCA record exposes donor IDs, 1,263,676 cells, cell-type labels, `raw.X`, and an H5AD asset in public metadata.

Weaknesses:

- Patient/donor/sample metadata are not fully validated for leakage-free splitting.
- GEO cell-type annotation status is unclear in the current audit tables.
- Gene identifier formats, count layers, and processed-object contents have not been inspected.
- `GSE162577` is too small for robust model development.
- `GSE174188` has controlled-access raw/processed data risk.

Interpretation risks:

- Biological interpretation is premature until gene identifiers, raw/normalized layers, cell-type labels, and QC-relevant metadata are verified.
- Pathway enrichment is not ready for any candidate until gene identifiers and matrix layers are audited.
- Disease-activity and lupus nephritis interpretation are unsupported by the current metadata.

Cross-cohort risks:

- GEO, HCA, and CELLxGENE records may overlap and must be deduplicated before any cross-cohort harmonization decision.
- Batch, site, library, chemistry, cohort, and processing metadata remain unresolved.
- No candidate can be assigned an external validation role yet.

Annotation risks:

- CELLxGENE cell-type labels are visible, but annotation provenance and compatibility require manual review.
- GEO candidate cell-type labels are not explicitly audited in current tables.
- Harmonizing annotations across GEO and CELLxGENE/HCA is unresolved.

Remaining unknowns:

- Patient/sample ID usability for every candidate.
- Batch/cohort metadata and treatment metadata for every candidate.
- Exact gene identifier fields and pathway-compatible feature mappings.
- Whether raw count matrices and processed objects are usable under project governance.
- Whether any candidate can support lupus nephritis-specific analysis; current evidence says no.

## Judge Repair Queue

No dataset can be approved yet. The Scientific Judge and Bioinformatics Judge identified unresolved blockers that must be repaired with auditable evidence before Human Gate 1 can be considered.

Unresolved scientific blockers:

- Patient or donor identifiers are unresolved for GEO candidates and donor/sample usability is unresolved for CELLxGENE/HCA.
- Label provenance is incomplete for all candidates; source-level disease terms are not enough for patient-level prediction.
- Disease activity labels are not audited at patient or sample level.
- Treatment metadata and batch metadata remain unclear for candidate task feasibility and confounding review.
- External validation roles are unresolved because cohort independence and label compatibility have not been proven.

Unresolved bioinformatics blockers:

- GEO cell-type annotation status is unclear.
- Gene identifier feasibility requires source-supported feature metadata.
- Pathway analysis is not ready until gene identifiers, count layers, and annotation provenance are verified.
- `GSE174188` has controlled-access raw and processed data restrictions.
- Raw count and processed object usability remain uninspected because no full data files have been downloaded.
- Cross-cohort harmonization is blocked until GEO, HCA, and CELLxGENE overlap is mapped.

Candidate-specific next checks:

- `GSE162577`: verify patient/sample IDs, n_cells, cell-type labels, feature identifiers, label provenance, and batch metadata; likely remains a limited candidate because of small cohort size.
- `GSE137029`: verify patient identifiers, label provenance, activity labels, treatment metadata, batch metadata, cell-type labels, feature identifiers, and overlap with HCA/CELLxGENE.
- `GSE174188`: verify dbGaP access constraints, subject/sample metadata, raw count availability, processed object availability, labels, and cohort overlap before any further feasibility claim.
- CELLxGENE/HCA linked candidate: verify donor/sample mapping, label provenance, activity labels, treatment metadata, batch metadata, annotation provenance, feature identifiers, and deduplication against GEO/HCA records.

Evidence required for Human Gate 1:

- A source-supported patient/donor/sample identifier map for any candidate proposed for use.
- A label audit table with exact label names, observed values, label level, and provenance.
- A batch/cohort/site/library metadata audit sufficient for leakage and confounding review.
- A raw/processed data availability decision that distinguishes public metadata visibility from approved data access.
- A feature/gene identifier feasibility note for pathway and biological interpretation plans.
- A cohort overlap and external-validation independence table.
- Repair queue rows moved only through manual review; no row may be marked resolved without source evidence and human review.

## 5. Rejected Datasets

| dataset | reason for rejection | scientific risk |
| --- | --- | --- |
| TODO | TODO | TODO |

## 6. Selected Training Cohort(s)

TODO: None selected. Human Gate 1 remains PENDING.

## 7. Selected External Validation Cohort(s)

TODO: None selected. `external_validation_cohort` remains TODO.

## 8. Label Availability Summary

TODO: Candidate dataset labels are not manually audited. Source-level disease labels are visible for candidate rows, but patient-level label feasibility remains TODO.

## 9. Patient Metadata Summary

TODO: Patient metadata rows have not been manually audited. Patient or donor identifier availability remains unclear for all candidate rows.

## 10. Cross-cohort Risks

TODO: Cross-cohort risks have not been evaluated. CELLxGENE/HCA/GEO overlap for GSE137029-linked records must be manually resolved before any external validation decision.

## 11. Known Limitations

TODO: Candidate dataset limitations must be documented after manual audit.

## 12. Human Gate 1 Recommendation

TODO: Human Gate 1 remains PENDING. Do not approve datasets, downloads, or modeling from this scaffold.

## 13. TODOs

- TODO: Manually audit candidate datasets.
- TODO: Populate candidate evidence tables only with verified metadata.
- TODO: Record rejected datasets with source-supported reasons.
- TODO: Request Human Gate 1 review after feasibility evidence is complete.
