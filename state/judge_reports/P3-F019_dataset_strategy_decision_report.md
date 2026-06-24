# P3-F019 Dataset Strategy Decision / Pivot Gate

## Executive Summary

The strategy decision is `switch_primary_to_CELLxGENE_HCA`, restricted to
primary-candidate validation.

This is not dataset selection and does not authorize access, preprocessing, or
training. `selected_datasets` remains empty, `external_validation_cohort`
remains `TODO`, and Phase 4 remains blocked.

The scientific objective has not pivoted away from SLE diagnosis /
case-control prediction. `pivot_status` therefore remains `not_activated`.

## Why GSE137029 Remains Blocked

GSE137029 has verified study-level SLE context and complete condition values
for its 66 pooled GEO Samples. The inspected GEO MINiML metadata does not
contain a patient, donor, subject, or individual identifier and does not link
the pooled samples to the reported individuals.

Continuing with GSE137029 would require inferring person identity or treating
pooled samples as patients. Both would invalidate patient-level splitting and
create unacceptable leakage and unit-of-analysis risk.

## Why CELLxGENE/HCA Is Stronger

Metadata-only inspection supports:

- 261 donor identifiers;
- 274 sample identifiers;
- consistent sample-to-donor mapping;
- consistent donor-to-disease mapping;
- 162 SLE donors and 99 normal donors;
- explicit repeated-sample grouping.

These facts directly address the identifier and diagnosis-linkage failures
that block GSE137029. They justify making CELLxGENE/HCA the next primary
validation target.

They do not establish dataset selection, matrix integrity, QC acceptance,
split readiness, feature readiness, or training permission.

## Why External Validation Remains Unresolved

The CELLxGENE/HCA resource has linked provenance to GEO and the HCA project.
The public metadata does not provide a record-level crosswalk that establishes
independence from GSE137029.

CELLxGENE/HCA must not be assigned as external validation for GSE137029. If it
later becomes the primary cohort, a separate independent cohort must be found
and audited for compatible labels, tissue, assay, person identifiers, and
non-overlap.

## Risk of Continuing Without Verified Person Mapping

Using GSE137029 without person mapping would:

- confuse pooled sequencing samples with patients;
- permit the same person to cross data splits;
- invalidate patient-level performance estimates;
- make diagnosis labels scientifically ambiguous at the modeling unit;
- prevent defensible calibration and external-validation claims.

These are hard blockers, not documentation gaps.

## Recommended Strategy

Proceed to `P3-F020 - CELLxGENE/HCA primary dataset validation`.

P3-F020 may validate the candidate's access plan, metadata completeness,
repeated-sample handling, QC feasibility, donor-level split feasibility, and
feature-manifest feasibility. It must not select the dataset, download data,
or enable modeling without separate explicit permission.

A focused search for a genuinely independent external-validation cohort
remains required after the primary-candidate strategy is validated.

## Rejected and Deferred Strategies

### Continue GSE137029

Rejected because no authoritative person mapping was found after the final
metadata expansion.

### Search New Dataset

Deferred as the immediate primary strategy, but retained as required parallel
work for independent external validation and as a fallback if CELLxGENE/HCA
fails validation.

### Pivot to Dataset Audit Paper

Rejected for now because CELLxGENE/HCA provides a scientifically stronger
candidate-validation path. Reconsider only if that path fails.

### Pause Modeling

Rejected as the project strategy because modeling is already blocked while
safe validation planning can still make progress.

## Work Allowed Next

- create the P3-F020 CELLxGENE/HCA validation plan;
- define evidence required for access, QC, donor-level splitting, and feature
  readiness;
- plan a separate independent-cohort search;
- maintain source provenance and unresolved fields.

## Work Still Forbidden

- downloading or preprocessing data;
- selecting a training dataset;
- assigning an external-validation cohort;
- training or evaluating models;
- creating model artifacts;
- cell-level splitting;
- treating GSE137029 pooled samples as patients;
- starting Phase 4.

## Judge Decision

The Scientific and Bioinformatics Judges accept CELLxGENE/HCA as the primary
candidate for the next validation feature only.

Training remains blocked. Phase 4 remains blocked. The research-objective
pivot remains inactive.
