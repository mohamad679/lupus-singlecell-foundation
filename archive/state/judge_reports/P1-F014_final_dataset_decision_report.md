# P1-F014 Final Dataset Feasibility Decision Report

Current feature: P1-F014 - Final Dataset Feasibility Decision Table.

No dataset is approved for modeling.

Human Gate 1 is approved_with_restrictions for Phase 2 scaffold work only. `selected_datasets` remains empty. `external_validation_cohort` remains TODO. Modeling and dataset downloads remain disallowed.

## Executive Summary

The final pre-gate decision framework preserves all candidates as `candidate_pending_audit`. Two candidates are strong enough to continue auditing, one candidate is limited by cohort size, and one candidate needs manual verification because controlled-access data and metadata constraints remain unresolved.

No candidate satisfies the combined scientific, bioinformatics, patient-level, label, access, and external-validation requirements for approval.

## Per-Candidate Decision

### GSE162577

- Overall readiness: `limited_candidate`
- Scientific status: `limited_candidate`
- Bioinformatics status: `limited_candidate`
- Recommended role: limited biological context candidate only after repair review; not for modeling.
- Main blockers: small cohort, unclear patient IDs, n_cells TODO, unclear activity labels, unclear cell-type labels, and unclear batch metadata.

### GSE137029

- Overall readiness: `continue_audit`
- Scientific status: `continue_audit`
- Bioinformatics status: `continue_audit`
- Recommended role: priority continued-audit candidate for case-control feasibility after repairs.
- Main blockers: patient IDs unclear, label provenance unresolved, activity labels not mapped, treatment metadata unclear, batch metadata unclear, and GEO/HCA/CELLxGENE overlap unresolved.

### GSE174188

- Overall readiness: `needs_manual_verification`
- Scientific status: `needs_manual_verification`
- Bioinformatics status: `needs_manual_verification`
- Recommended role: manual access and metadata verification candidate only.
- Main blockers: controlled-access data, unclear patient IDs, unresolved raw/processed data access, unclear activity/treatment/batch metadata, and overlap risk.

### CELLxGENE / HCA Lupus PBMC-Linked Project

- Candidate ID: `436154da-bcf1-4130-9c8b-120ff9a888f2::218acb0f-9f2f-4f76-b90b-15a4b7c7f629`
- Overall readiness: `continue_audit`
- Scientific status: `continue_audit`
- Bioinformatics status: `continue_audit`
- Recommended role: priority continued-audit candidate for metadata-rich PBMC/blood feasibility after deduplication repairs.
- Main blockers: sample IDs unclear, label provenance unclear, activity/treatment/batch metadata unclear, feature identifiers require review, and overlap with GEO/HCA records remains unresolved.

## Strongest Candidates

- `GSE137029`: strongest GEO continued-audit candidate because of cohort scale, PBMC relevance, and visible source-level case/control metadata.
- CELLxGENE/HCA linked candidate: strongest metadata-rich continued-audit candidate because donor IDs, disease terms, cell count, cell-type labels, raw layer metadata, and H5AD asset visibility are present in public metadata.

These are not approved. They only warrant focused repair work.

## Main Unresolved Blockers

- Patient/donor/sample identifier usability.
- Patient-level label provenance.
- Disease activity label availability.
- Treatment metadata and batch metadata.
- Cell-type annotation provenance.
- Gene identifier and pathway mapping feasibility.
- Raw count and processed object usability.
- Controlled-access constraints for `GSE174188`.
- Cohort overlap across GEO, HCA, and CELLxGENE records.

## Cross-Cohort Risks

The linked GEO, HCA, and CELLxGENE resources may contain overlapping donors, samples, or cells. No candidate can serve as an external validation cohort until overlap is mapped and cohort independence is source-supported.

## External Validation Risks

No external validation cohort is assigned. External validation remains blocked by unresolved patient IDs, sample IDs, cohort identifiers, label compatibility, assay compatibility, tissue compatibility, and batch metadata.

## Data Access Risks

- `GSE162577`: public metadata and supplementary file visibility exist, but data contents are not inspected.
- `GSE137029`: public raw/processed availability is visible, but no files were downloaded or inspected.
- `GSE174188`: raw and processed data are controlled-access through dbGaP.
- CELLxGENE/HCA linked candidate: H5AD/FASTQ asset metadata are visible, but no full asset was downloaded or inspected.

## Remaining Requirements Before Human Gate 1

- Complete repair queue evidence for patient IDs, labels, activity labels, treatment metadata, and batch metadata.
- Create a source-supported cohort overlap and deduplication table.
- Verify raw count and processed object accessibility under project governance.
- Verify gene identifiers and cell-type annotation provenance.
- Produce a candidate feasibility package that a human can review without inferred metadata.

Human Gate 1 restricted approval does not approve modeling, downloads, selected datasets, or external validation cohorts.
