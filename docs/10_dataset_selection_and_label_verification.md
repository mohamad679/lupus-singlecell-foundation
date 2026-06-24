# Dataset Selection and Label Verification

Current feature: P3-F012 - Dataset selection and label verification.

## Purpose

This review begins resolving Modeling Readiness Gate blockers for GSE137029
and its linked CELLxGENE/HCA representation. It records only evidence already
documented in repository candidate tables and source-provenance notes.

This review does not download full data, inspect unrecorded metadata fields,
select a dataset, authorize training, or start Phase 4.

## Evidence Policy

An evidence item is:

- `verified` only when the existing audit records an explicit public source and
  the fact can be stated without inference;
- `unclear` when a relevant fact is mentioned but its patient-, donor-, or
  sample-level meaning is unresolved;
- `blocked` when the missing evidence prevents dataset selection or training;
- `pending` when a later approved inspection or human decision is required.

Repository and publication-level case/control descriptions are not sufficient
proof of patient-level target labels. Visible donor identifiers are not
sufficient proof of sample linkage, repeated-measure handling, or leakage-safe
training usability.

## Candidates Reviewed

### GSE137029

Verified from the existing GEO audit:

- the accession and GEO source URL;
- human PBMC multiplexed single-cell RNA sequencing;
- an SLE case and healthy-control study context;
- reported cohort and sample counts;
- raw SRA and processed Series data availability.

Unresolved:

- exact patient or donor identifier fields;
- exact patient/sample disease-label fields and observed values;
- patient-to-sample linkage;
- activity, treatment, and batch metadata;
- overlap with the linked HCA/CELLxGENE representation;
- approved training-cohort role.

Scientific status: strongest candidate for continued case-control verification,
but not selected and not approved for modeling.

### CELLxGENE/HCA

Candidate identifier:
`CELLxGENE_HCA_436154da-bcf1-4130-9c8b-120ff9a888f2_218acb0f-9f2f-4f76-b90b-15a4b7c7f629`.

Verified from the existing CELLxGENE/HCA audit:

- collection and dataset identifiers with source URLs;
- human blood/PBMC-linked single-cell data;
- normal and systemic lupus erythematosus disease terms;
- visible donor identifiers;
- visible cell-type labels, raw count indication, and H5AD asset;
- linkage to the same HCA project and GEO accessions.

Unresolved:

- exact patient-level label provenance and donor-to-label linkage;
- sample identifier availability and donor-to-sample relationships;
- activity, treatment, and batch metadata;
- whether this is a derivative representation of GSE137029 rather than an
  independent cohort;
- approved training or external-validation role.

Scientific status: useful for metadata harmonization and continued
verification, but not independently selectable until overlap and label linkage
are resolved.

## Dataset Selection Decision

No dataset is selected.

GSE137029 remains the primary candidate for continued verification because its
public audit documents a large human SLE case-control single-cell study.
Selection remains blocked by missing patient/donor identifiers, exact
patient-level label provenance, cohort overlap evidence, QC approval, and
training-cohort suitability review.

The CELLxGENE/HCA candidate must not be treated as an independent validation
cohort or a second training cohort until provenance and overlap are resolved.

## Label Provenance Decision

The study-level SLE and healthy-control context is verified for both candidate
representations. Patient-level diagnosis label provenance is not verified.

Required next evidence:

- exact source metadata field names;
- observed SLE and healthy-control values;
- definitions and any recoding rules;
- patient/donor/sample level of each label;
- linkage from every training unit to one verified target label;
- class counts after linkage and missingness review.

Disease activity, flare, lupus nephritis, and treatment-response labels remain
outside the approved task and must not be inferred.

## Patient and Donor Identifier Decision

GSE137029 patient/donor identifier availability remains unclear.

CELLxGENE donor identifiers are visible in recorded public metadata, but sample
linkage, repeated measures, uniqueness, missingness, and cross-source
deduplication remain unresolved. This is not sufficient for a leakage-safe
split.

## Training Readiness Consequences

The following remain blocked:

- dataset selection;
- verified patient-level diagnosis labels;
- verified patient/donor grouping;
- training-cohort suitability;
- split manifest creation;
- real leakage checks;
- dataset-specific QC approval;
- populated feature manifests.

`allow_modeling` remains false, `training_permission` remains `blocked`,
`selected_datasets` remains empty, and `external_validation_cohort` remains
TODO. Phase 4 is not started.

## Next Actions

1. Perform an explicitly approved metadata-file inspection without full-data
   download.
2. Record exact patient/donor/sample and diagnosis-label fields with source
   locations.
3. Reconcile GEO, HCA, and CELLxGENE provenance and donor/sample overlap.
4. Quantify missingness, uniqueness, class counts, and repeated samples.
5. Request a separate human dataset-selection review only after the evidence is
   complete.

