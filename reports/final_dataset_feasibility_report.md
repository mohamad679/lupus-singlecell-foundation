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
