# P3-F008 Baseline Scientific Judge Report

## Executive Summary

The Phase 3 baseline scaffold is **adequate as a restricted scientific design
framework** for SLE diagnosis / case-control prediction.

The scaffold correctly prioritizes patient-level pseudobulk and cell-type
composition baselines, begins with interpretable logistic regression, treats
tree models as secondary comparators, requires patient- or cohort-level splits,
and separates discrimination, calibration, and provenance contracts.

This decision does not authorize data loading, feature extraction, fitting,
prediction, evaluation, or performance reporting.

**Training is allowed now: NO.**

`allow_modeling` remains false. `selected_datasets` remains empty.
`external_validation_cohort` remains TODO. Phase 4 is not started.

## Approved Baseline Design Components

The following components are accepted for future controlled implementation,
subject to the conditions in this report:

- Patient- or donor-level pseudobulk design with cell/barcode aggregation
  forbidden.
- Logistic regression as the first interpretable baseline.
- Random forest and optional XGBoost as secondary nonlinear comparators.
- Cell-type proportion and count features as composition baselines.
- Patient-level evaluation using discrimination and threshold-dependent
  metrics.
- Patient-level calibration planning using Brier score and ECE.
- Header-only feature, result, prediction, coefficient, importance, and
  calibration contracts.
- Explicit refusal paths for disabled extraction, training, prediction,
  evaluation, plotting, artifacts, and performance claims.

Acceptance applies to design structure only. It is not approval of a dataset,
feature matrix, model, result, or clinical claim.

## Blocked Modeling Actions

- Loading or preprocessing real candidate datasets.
- Creating real pseudobulk or cell-type proportion matrices.
- Fitting logistic regression, random forest, XGBoost, or any other classifier.
- Generating prediction scores or labels.
- Computing discrimination, threshold-dependent, or calibration metrics.
- Selecting hyperparameters, thresholds, ECE bins, or bootstrap settings.
- Creating model, preprocessing, prediction, or figure artifacts.
- Implementing foundation models, DeepSets, MIL, or uncertainty methods.
- Claiming external validation, clinical utility, biological causality, or
  generalization.

## Scientific Strengths

- The biological replicate is the patient or donor, not the cell.
- Cell-level split and aggregation units are explicitly rejected.
- Feature, split, prediction, and result provenance are represented in
  manifests and schemas.
- Logistic regression provides an interpretable reference before higher-
  capacity tree models.
- Tree-based models are framed as secondary and high-risk under small patient
  counts.
- Cell-type composition is separated from gene-expression features.
- Evaluation requires verified labels and passed leakage checks.
- Calibration is separated from uncertainty modeling and clinical claims.
- All execution and artifact flags remain disabled.

## Scientific Weaknesses

- No dataset has been selected for controlled modeling.
- No patient-level feature matrix or prediction manifest exists.
- Pseudobulk normalization and gene-filtering policies remain TODO.
- Patient and class counts are unknown for the final modeling cohort.
- Hyperparameter search, feature scaling, class weighting, and threshold
  policies are not finalized.
- Bootstrap count and ECE binning remain TODO.
- Cell-type annotation compatibility and rare-cell handling are unresolved.
- The planned HVG linear classifier has no dedicated scaffold.
- The framework has not been tested against real metadata distributions,
  missingness, or cohort structure.

## Leakage Risks

The design identifies the principal leakage routes, but no real evidence has
yet passed the checks. Training remains blocked until:

- patient, donor, sample, and cell overlap are excluded across partitions
- repeated and longitudinal samples remain grouped by patient
- feature filtering, normalization, scaling, annotation, and transformation
  decisions are fitted within training partitions only
- threshold and hyperparameter selection use no test or external data
- GEO, HCA, and CELLxGENE record overlap is resolved
- cohort, batch, treatment, assay, site, and cell-count proxies are assessed

## Label Risks

The approved task remains only partially feasible. Exact patient-level SLE and
healthy-control label fields, values, definitions, sample linkage, and source
provenance must be verified. Study titles, accession descriptions, tissue, and
cell annotations cannot substitute for patient-level diagnosis labels.

No result may be reported while label verification is unresolved.

## External Validation Risks

No external validation cohort is assigned. Candidate sources may overlap in
patients, samples, or cells. Compatible labels, tissue, assay, preprocessing,
feature definitions, and cohort independence have not been demonstrated.

Internal patient-level evaluation may be designed later under an explicit
training gate, but external validation and generalization claims remain
blocked until an independent cohort is approved.

## Calibration Risks

Calibration plans are scientifically appropriate but incomplete:

- ECE binning strategy and number of bins are TODO.
- Bootstrap count and interval construction are TODO.
- Small patient counts may make bins and confidence intervals unstable.
- Prevalence and cohort shift can invalidate internal calibration.
- Calibration does not establish uncertainty, abstention safety, or clinical
  usefulness.

No Brier score, ECE, reliability diagram, recalibration method, or uncertainty
analysis is approved now.

## Overfitting Risks

High-dimensional pseudobulk features and small patient counts create a major
overfitting risk. Tree ensembles are especially vulnerable. A later gate must
require:

- patient and class count review
- restricted, prespecified hyperparameter spaces
- training-only feature selection and scaling
- nested or otherwise leakage-safe patient-level resampling
- comparison against logistic regression under identical partitions
- transparent reporting of instability and failed resamples

## Scaffold Adequacy Decision

**Decision: accepted_with_restrictions**

The baseline scaffold is adequate for organizing a future controlled
modeling/training gate. It is not adequate evidence that modeling is currently
feasible, and it does not resolve dataset, label, access, leakage, sample-size,
or external-validation blockers.

## Training Decision

**Training is allowed now: NO.**

The project must not change `allow_modeling` until a separate explicit human
modeling/training gate reviews the required evidence below.

## Required Conditions Before Training

1. A candidate dataset is explicitly selected for the restricted SLE
   case-control task under a human gate.
2. Patient/donor IDs, sample linkage, diagnosis labels, comparator definitions,
   and label provenance are verified.
3. Data acquisition and QC are explicitly approved and reproducibly recorded.
4. Pseudobulk normalization and gene-filtering policies are finalized.
5. Cell-type annotation provenance and rare-cell handling are finalized for
   composition features.
6. A patient- or donor-level split manifest is populated.
7. Patient, donor, sample, cell, cohort, batch, and label leakage checks pass.
8. Patient counts, class balance, missingness, and feature dimensionality are
   reviewed for model feasibility.
9. Feature scaling, class weighting, hyperparameter search, and threshold
   selection policies are prespecified.
10. Bootstrap and ECE policies are finalized before confirmatory evaluation.
11. A separate gate defines whether initial work is an internal preliminary
    baseline or includes an approved independent external cohort.
12. All results remain preliminary until label and cohort verification is
    complete and a Scientific Judge reviews the outputs.

Foundation models and uncertainty modeling remain blocked regardless of a
future baseline-training decision.
