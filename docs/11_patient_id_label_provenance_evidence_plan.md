# Patient/Donor ID and Label Provenance Evidence Plan

Current feature: P3-F013 - Patient/donor ID and label provenance evidence plan.

## Purpose

This plan defines the exact evidence needed to verify patient or donor
identifiers, diagnosis labels, and cohort overlap for GSE137029 and its linked
CELLxGENE/HCA representation. It does not perform verification by inference,
download full data, select a dataset, or authorize modeling.

## Why Patient/Donor ID Verification Is Mandatory

Patient-level prediction requires every sample and cell to be grouped under a
stable patient or donor identifier. Without this grouping:

- cells from one person can enter multiple splits;
- repeated or longitudinal samples can leak across splits;
- patient-level class counts cannot be calculated;
- sample and donor overlap across GEO, HCA, and CELLxGENE cannot be excluded;
- patient-level metrics would not have a defensible evaluation unit.

Cell barcodes, filenames, row order, library identifiers, and inferred
combinations of metadata fields are not substitutes for explicit patient or
donor identifiers.

## Why Label Provenance Is Mandatory

The approved task is restricted to SLE diagnosis versus a verified comparator.
Every target label must have an explicit source field, observed value,
definition, and patient/donor/sample linkage. Study titles, abstracts, disease
ontology summaries, and aggregate cohort descriptions do not establish the
label for an individual modeling unit.

Unverified labels create outcome misclassification, leakage, comparator
ambiguity, and unsupported scientific claims.

## Evidence Required for GSE137029

Required identifier evidence:

- exact patient or donor identifier field name;
- exact sample and library identifier fields;
- sample-to-patient or sample-to-donor mapping;
- identifier uniqueness and missingness;
- repeated, longitudinal, or multiple-library relationships;
- evidence that all records from one person can be kept in one split.

Required label evidence:

- exact SLE diagnosis field and observed source value;
- exact healthy-control field and observed source value;
- source definitions for case and comparator groups;
- linkage from each sample to one patient/donor and one diagnosis label;
- patient-level case/control counts after missingness and duplication review;
- evidence that flare or activity descriptions are not silently used as the
  diagnosis target.

Preferred source locations are GEO Series and Sample metadata, repository-hosted
metadata matrices or data dictionaries, and linked publication supplements.
The GEO title or summary alone is insufficient.

## Evidence Required for CELLxGENE/HCA

Required identifier evidence:

- exact CELLxGENE donor identifier field and completeness statistics;
- exact sample, library, or specimen identifier field;
- donor-to-sample and donor-to-library relationships;
- repeated-sample and missingness review;
- stable correspondence to HCA project metadata;
- evidence supporting or rejecting overlap with GSE137029.

Required label evidence:

- exact disease field and ontology values;
- mapping of normal/control and SLE values to individual donors;
- comparator definition and exclusions;
- donor-level class counts after missingness review;
- original source provenance for any normalized CELLxGENE labels;
- confirmation that cell-level ontology labels do not substitute for
  patient-level target provenance.

Visible donor identifiers and disease terms in the existing audit justify
continued inspection, but do not verify training usability.

## Donor/Patient ID Verification Checklist

- [ ] Record the original identifier field name.
- [ ] Record its data level: patient, donor, sample, library, or cell.
- [ ] Confirm stable grouping across all cells and samples.
- [ ] Quantify missing, duplicated, and conflicting values.
- [ ] Identify repeated and longitudinal samples.
- [ ] Record sample-to-patient or sample-to-donor relationships.
- [ ] Confirm that split assignment can occur at patient/donor level.
- [ ] Preserve original values and source locations.
- [ ] Obtain named Scientific and Bioinformatics Judge review.

## Label Provenance Checklist

- [ ] Record the original label field name.
- [ ] Record all observed source values.
- [ ] Record definitions and ontology identifiers where applicable.
- [ ] Identify whether the label is patient, donor, sample, or cell level.
- [ ] Link every proposed modeling unit to exactly one verified target.
- [ ] Quantify missing, ambiguous, and conflicting labels.
- [ ] Define the healthy or comparator population explicitly.
- [ ] Preserve the original value and any future recoding map.
- [ ] Keep activity, flare, nephritis, and treatment labels separate.
- [ ] Obtain named Scientific Judge review.

## Cohort Overlap Checklist

- [ ] Compare study, project, collection, and dataset identifiers.
- [ ] Compare publication, accession, and repository cross-references.
- [ ] Compare donor/sample identifiers only when source-supported.
- [ ] Compare reported donor, sample, and cell counts.
- [ ] Determine whether CELLxGENE is a processed representation of GEO data.
- [ ] Identify whether GSE137029 and the HCA project share donors or samples.
- [ ] Record unresolved mappings without guessing.
- [ ] Prohibit external-validation use until independence is demonstrated.

## Acceptable Evidence Sources

- GEO Series and Sample metadata pages;
- repository-provided metadata matrices and data dictionaries;
- NCBI SRA links and metadata, inspected only under an approved metadata-access
  feature;
- HCA project manifests and schema-documented metadata;
- CELLxGENE collection/dataset metadata and schema-documented fields;
- peer-reviewed publication methods, tables, and supplements;
- explicit accession and project cross-references;
- versioned, source-preserving inspection reports signed by a named reviewer.

## Unacceptable Evidence Sources

- guessed or constructed patient/donor identifiers;
- cell barcodes, filenames, row order, or directory structure treated as IDs;
- labels inferred from study title, abstract, tissue, assay, or cell type;
- disease activity inferred from diagnosis or publication narrative;
- lupus nephritis inferred from SLE status or kidney relevance;
- search snippets, unsourced summaries, or unverifiable secondary claims;
- aggregate case/control counts without individual sample linkage;
- mock data, schemas, passing tests, or empty tables as real-data evidence.

## Forbidden Until Verified

- dataset selection or approved training-cohort assignment;
- patient-, donor-, or cohort-level split creation;
- feature extraction, model fitting, prediction, or evaluation;
- treating CELLxGENE/HCA as an independent validation cohort;
- disease activity, flare, or lupus nephritis modeling;
- clinical, diagnostic, calibration, or performance claims;
- Phase 4 start.

## Criteria for Unblocking Training Later

Training can be reconsidered only when:

1. exact patient/donor/sample fields and relationships are documented;
2. exact case/control label fields, values, definitions, and linkage are
   documented;
3. missingness, uniqueness, repeats, and class counts are audited;
4. GEO/CELLxGENE/HCA overlap is resolved;
5. a human gate explicitly selects a training dataset and role;
6. QC, split, leakage, and feature-manifest blockers are separately resolved;
7. the Modeling Readiness Gate is re-reviewed and passed;
8. a new explicit training permission decision replaces the current block.

Until then, `modeling_readiness` remains `not_ready`,
`training_permission` remains `blocked`, and `allow_modeling` remains false.

