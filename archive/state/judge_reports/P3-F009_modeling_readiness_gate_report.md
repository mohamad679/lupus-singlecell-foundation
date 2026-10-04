# P3-F009 Modeling Readiness Gate Report

## Current Readiness Status

**Modeling readiness: not_ready**

This gate does not authorize training. `allow_modeling` and `training_allowed`
remain false. `selected_datasets` remains empty, and
`external_validation_cohort` remains TODO. Phase 4 is not started.

## Evidence Decision

Three planning conditions are currently supported:

- The prediction task is approved with restrictions for SLE diagnosis /
  case-control baseline design.
- An external validation planning framework is documented, although no cohort
  is assigned.
- The patient-level evaluation and calibration protocol scaffold is ready.

These passes do not compensate for the unresolved blocking conditions.

## Blocking Items

1. **Dataset selected:** no dataset is assigned for training.
2. **Labels verified:** patient-level diagnosis and control labels and
   provenance remain unresolved.
3. **Patient/donor IDs verified:** identifier and repeated-sample usability has
   not been demonstrated for a selected cohort.
4. **Split manifest ready:** the split manifest contains headers only.
5. **Leakage checks ready:** utilities exist, but no real approved split has
   passed overlap and confounding checks.
6. **Training cohort selected:** no cohort, patient count, class balance, or
   access package is approved.
7. **QC protocol approved:** the QC scaffold exists, but no real thresholds,
   filtering report, or human QC approval exists.
8. **Feature manifest ready:** feature manifests contain headers only and key
   feature policies remain TODO.

## Required Actions Before Training

- Complete P3-F010 dataset and label verification planning.
- Obtain explicit human selection of the training dataset/cohort.
- Verify patient/donor/sample IDs, diagnosis/control labels, and provenance.
- Approve data acquisition and QC before any real processing.
- Finalize normalization, gene filtering, annotation, and rare-cell policies.
- Populate a patient- or donor-level split manifest.
- Pass patient, donor, sample, cell, cohort, batch, duplicate, and label
  leakage checks on the approved split.
- Populate and audit the selected feature manifest.
- Review patient counts, class balance, missingness, and dimensionality.
- Finalize tuning, threshold, bootstrap, and ECE policies.
- Complete P3-F011 as a separate training permission decision.

## What Is Allowed Next

- Readiness blocker planning.
- Metadata-only dataset and label verification planning.
- Evidence collection that does not download or preprocess data.
- Updating gate evidence after explicit human review.

The next planned feature is P3-F010, Dataset and Label Verification Plan.

## What Remains Forbidden

- Dataset downloads or preprocessing.
- Real feature extraction.
- Model fitting or training.
- Prediction or metric generation.
- Model, preprocessing, prediction, or figure artifacts.
- Phase 4.
- Foundation models, DeepSets, MIL, or other deep learning.
- Uncertainty, abstention, selective prediction, or clinical utility claims.
- Dataset selection or external validation assignment without an explicit
  human decision.

The gate remains blocked until every blocking condition is supported by
auditable evidence and P3-F011 explicitly grants or denies training permission.
