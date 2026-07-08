# Dataset and Label Verification Plan

Current feature: P3-F010 - Dataset and label verification plan.

## Purpose

This plan defines the auditable evidence required to resolve the eight
blocking conditions in the Modeling Readiness Gate. It does not select a
dataset, approve a training cohort, download data, preprocess data, or authorize
modeling.

All unknown facts must remain `TODO` or `unclear`. A requirement can move from
pending to verified only after a named reviewer records source-supported
evidence and a verification date.

## Current Blockers

- Dataset selection.
- Patient-level diagnosis and control label provenance.
- Patient or donor identifier availability and sample linkage.
- Patient-, donor-, or cohort-level split manifest readiness.
- Leakage-check readiness on a populated split.
- Training cohort suitability.
- QC approval for the selected data.
- Patient-level feature manifest readiness.

## Required Evidence Per Blocker

### Dataset Selection

Required evidence:

- exact accession, collection ID, and dataset ID
- authoritative repository and publication links
- human single-cell assay verification
- tissue, assay, disease, control, and cohort scope
- patient and sample counts supported by source evidence
- access and licensing status
- relationship to other GEO, HCA, and CELLxGENE records
- explicit human decision assigning a restricted training role

Candidate status or planning priority is not dataset selection.

### Label Provenance

Required evidence:

- exact source field name for SLE and healthy-control labels
- observed source values and their definitions
- label level: patient, donor, sample, or cell
- mapping from each sample to a verified patient or donor label
- metadata file, repository page, supplement, or publication location
- ambiguity review and comparator definition
- patient and sample counts for each class

Study titles, search terms, disease ontology matches, and tissue names are not
patient-level labels.

### Patient or Donor ID Availability

Required evidence:

- exact source fields for patient ID, donor ID, and sample ID
- documented relationships among patients, donors, samples, timepoints, and
  tissues
- repeated and longitudinal sample identification
- missingness and uniqueness review
- evidence that IDs can support leakage-safe grouping
- overlap assessment across candidate repositories and cohorts

IDs must not be synthesized from row order, filenames, barcodes, or inferred
clinical attributes.

### Split Manifest Readiness

Required evidence:

- populated `metadata/table_schemas/split_manifest.csv`
- aggregation unit limited to patient, donor, or cohort
- all samples and cells from one patient assigned to one compatible split
- explicit train, validation, test, holdout, or external-validation role
- patient-level class counts per split
- repeated-sample and longitudinal handling
- source dataset and cohort provenance
- audit status for every row

Cell IDs and barcodes are forbidden split units.

### Leakage Check Readiness

Required evidence:

- no patient overlap
- no donor overlap
- no sample overlap where required
- no duplicated cell or barcode overlap
- no unreviewed cohort overlap
- batch and site confounding assessment
- label-to-split confounding assessment
- confirmation that normalization, filtering, scaling, annotation, feature
  selection, tuning, calibration, and threshold selection are training-only
- an auditable leakage-check report tied to the split manifest version

Mock tests demonstrate utility behavior but do not satisfy this requirement.

### Training Cohort Suitability

Required evidence:

- explicit human-approved cohort role
- verified patient and class counts
- adequate case and control representation
- tissue and assay suitability for the approved task
- treatment, batch, site, and cohort metadata review
- missingness and access-risk assessment
- dimensionality and sample-size feasibility review
- no unresolved overlap with planned validation data

No minimum patient count is invented in this plan. Suitability must be judged
after real metadata are verified.

### QC Approval

Required evidence:

- approved source files and checksums
- sample- and patient-level QC summaries
- before/after counts for any filtering
- documented threshold source and rationale
- doublet, ambient RNA, mitochondrial, count-depth, and tissue-specific review
- batch-aware and disease-group-aware QC assessment
- no unlogged cell or sample removal
- named human approver and approval date

The existing QC scaffold is not QC approval.

### Feature Manifest Readiness

Required evidence:

- populated pseudobulk or cell-type composition feature manifest
- patient, donor, sample, dataset, cell-type, gene, and split provenance as
  applicable
- finalized normalization and gene-filtering policy
- cell-type annotation provenance and rare-cell policy where applicable
- training-only feature fitting and transformation evidence
- missing-feature, duplicate-gene, unmapped-gene, and excluded-stratum reports
- audit status for every feature record

Header-only manifests do not satisfy readiness.

## Verification Workflow

1. Assign a verification ID and requirement type.
2. Identify the candidate without assigning an approved role.
3. Record the exact evidence required before inspecting sources.
4. Inspect authoritative public metadata and linked publications manually.
5. Record the exact source location and observed evidence without inference.
6. Cross-check patient, sample, label, cohort, and access relationships.
7. Record unresolved fields as `TODO` or `unclear`.
8. Have a named Scientific or Bioinformatics Judge review the evidence.
9. Record reviewer and date only after review.
10. Update the Modeling Readiness Gate only through a separate evidence review.

No checklist row is automatically verified.

## Acceptable Evidence Sources

- authoritative GEO, SRA, dbGaP, NCBI, HCA, or CELLxGENE metadata
- repository-hosted sample and donor metadata files
- linked peer-reviewed publication methods, tables, and supplements
- data dictionaries and controlled-access metadata summaries
- checksummed files obtained only after a separate download approval
- generated QC, split, leakage, and feature reports from explicitly approved
  future features
- signed or otherwise explicit human gate decisions

## Unacceptable Evidence Sources

- guessed accessions, IDs, labels, counts, or cohort roles
- study title or abstract alone when patient-level metadata are required
- search-engine snippets or unsourced summaries
- filename, barcode, row-order, or folder-name inference
- disease labels inferred from tissue, cell type, treatment, or publication
  context
- activity, nephritis, flare, or control labels inferred from diagnosis
- cell-level labels treated as patient-level outcomes
- mock rows, schemas, empty tables, or passing unit tests as evidence that real
  data satisfy a requirement

## Manual Inspection Requirements

Manual inspection must:

- preserve source wording and field names
- record source URLs or controlled-access references
- distinguish repository metadata from publication interpretation
- identify the level of every ID and label
- compare patient/sample counts across sources
- document discrepancies, missingness, and access limitations
- check whether GEO, HCA, and CELLxGENE records represent the same study,
  donors, samples, or cells
- avoid downloading full data until separately approved

## Label Provenance Rules

- Diagnosis and control labels must be explicit at patient or linked sample
  level.
- Healthy controls must be distinguishable from disease controls.
- Label values must have a source-supported definition.
- Any recoding must preserve the original value and mapping rationale.
- Ambiguous or publication-only labels remain pending until sample linkage is
  demonstrated.
- Disease activity, flare, lupus nephritis, treatment response, and other
  blocked tasks must not be introduced into the approved case-control target.

## Patient or Donor ID Verification Rules

- Patient, donor, and sample identifiers must retain their distinct meanings.
- Repeated samples from one patient must be discoverable and grouped.
- Missing identifiers cannot be imputed.
- Cell barcodes are not patient identifiers.
- IDs must support overlap testing across repositories and cohorts.
- De-identification is acceptable only when stable grouping remains possible.

## Split Manifest Requirements

- Split assignment must occur at patient, donor, or independent cohort level.
- Cell-level and barcode-level splits are prohibited.
- All records for one patient or donor must remain in one compatible split.
- Class counts and cohort composition must be reviewed before approval.
- The manifest must be versioned and linked to leakage-check evidence.
- External validation remains TODO until cohort independence is verified.

## Leakage Verification Requirements

- Run all existing overlap checks on the populated split.
- Add cohort-overlap evidence for linked GEO, HCA, and CELLxGENE records.
- Verify preprocessing and feature decisions are fitted on training data only.
- Review batch, site, assay, treatment, and cell-count confounding.
- Fail readiness if any critical overlap is unresolved.

## QC Approval Requirements

- QC decisions must be dataset-specific and evidence-based.
- Thresholds cannot be guessed or copied without justification.
- Applied thresholds require a named approver.
- Sample and patient exclusions must be logged.
- QC cannot use outcome labels to selectively improve apparent separability.
- QC approval must precede feature extraction and training.

## Feature Manifest Requirements

- Every feature must be traceable to an approved dataset and biological
  aggregate.
- Gene identifiers and cell-type labels must follow their approved policies.
- Split provenance must be recorded.
- Unknown values remain `TODO` or `unclear`.
- Real feature values cannot be created until data, QC, and extraction are
  explicitly approved.

## Criteria for Allowing Training Later

Training may be considered only when:

- all eight verification checklist rows are verified with auditable evidence
- the Modeling Readiness Gate has no pending blocking condition
- selected dataset and training cohort decisions are explicit
- labels and patient/donor IDs are verified
- QC, split, leakage, and feature evidence is complete
- evaluation policies are finalized for the intended preliminary analysis
- P3-F011 records an explicit human training permission decision

Meeting these criteria does not approve foundation models or uncertainty
methods.

## Criteria for Rejecting Training

Training must be denied when:

- labels or patient IDs are inferred, ambiguous, or cell-level only
- no suitable case and control cohort exists
- patient-level splitting is impossible
- overlap or leakage remains unresolved
- QC decisions are unsupported or outcome-driven
- feature provenance or transformation policy is incomplete
- patient count or class balance is scientifically inadequate
- access, licensing, or cohort independence cannot be established
- any evidence is invented or unverifiable

Current decision: training remains blocked.
