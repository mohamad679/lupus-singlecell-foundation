# Baseline Modeling Plan

Current feature: P3-F001 - Baseline modeling scaffold.

## Phase 3 Goal

Phase 3 will establish transparent patient-level baselines for the restricted
SLE diagnosis / case-control prediction task. P3-F001 creates design structure
only. It does not load data, create features, fit models, evaluate predictions,
or produce model artifacts.

## Approved Task

The only task in scope is:

- SLE diagnosis / case-control prediction

Human Gate 2 approved only baseline design for this task. Candidate datasets
remain unselected, label provenance remains subject to verification, and any
future result must be labeled preliminary until source labels are verified.

## Blocked Tasks

The following tasks remain blocked and must not be represented as model
targets:

- disease activity prediction
- flare prediction
- lupus nephritis prediction

Foundation models, deep patient-level multiple-instance learning, uncertainty
methods, and dashboard work are also outside the approved scope.

## Baseline Rationale

Strong baselines are required to determine whether a patient-level signal is
detectable without unnecessary model complexity. They provide interpretable
reference performance, expose leakage and confounding, and make later
complexity scientifically testable rather than assumed.

## Why Baselines Precede Foundation Models

Foundation models are not approved. Even if considered later, they would
require comparison with simpler methods under identical patient-level splits,
labels, features, and evaluation metrics. A complex model is not justified
unless it improves clinically relevant performance beyond reproducible
baselines without increasing leakage, calibration, or interpretation risk.

## Baseline Families

### Pseudobulk and Logistic Regression

Design patient- or donor-level aggregate expression features and an
interpretable regularized linear classifier. Future design must specify
aggregation, normalization, feature selection, regularization, and
patient-level cross-validation without using test data.

### Pseudobulk and Random Forest / XGBoost

Design nonlinear tabular comparators over the same patient-level pseudobulk
features. These families remain disabled for training. Future work must control
feature selection, hyperparameter tuning, class imbalance, and overfitting at
the patient rather than cell level.

### HVG and Linear Classifier

Design a linear baseline using a prespecified highly variable gene feature
space. HVG selection must be fitted inside training partitions in future work;
it must never use held-out patients or external cohorts.

### Cell-Type Proportion Baseline

Design patient-level features from verified cell-type proportions. Cell-type
annotation provenance, minimum cell counts, compositional constraints, and
batch sensitivity must be documented before this baseline can be trained.

### Simple DeepSets

DeepSets may be considered only in a later explicitly approved feature. It is
disabled for design and training in P3-F001 because deep patient-level
multiple-instance learning is outside the Human Gate 2 scope.

## Input Requirements

Future baseline work requires:

- source-verified patient or donor identifiers
- source-verified SLE and healthy control labels
- sample, cohort, batch, tissue, and assay identifiers
- documented label provenance and comparator definitions
- verified gene identifiers for expression features
- verified cell-type annotation provenance for proportion features
- a patient-level split manifest
- documented dataset and cohort overlap checks

Unknown or unresolved values must remain `TODO` or `unclear`; they must not be
inferred.

## Patient-Level Split Requirements

- Split units must be patients, donors, or independent cohorts.
- All cells and repeated samples from one patient must remain in one partition.
- Donors and samples must not overlap across train, validation, test, or
  external validation partitions.
- External validation remains TODO and cannot be simulated by a random
  cell-level split.
- Stratification must operate on patient-level labels and must not leak labels
  through feature construction.

## Leakage-Prevention Requirements

Before any later training feature:

- verify no patient, donor, sample, or cell identifier overlap
- fit normalization, HVG selection, aggregation parameters, and feature
  selection using training partitions only
- prevent cohort, batch, and source identifiers from acting as target proxies
- inspect duplicate cells and barcodes
- verify that label definitions are independent of the split assignment
- document repeated and longitudinal sample handling

Cell-level train/test splitting is forbidden.

## Planned Metrics

Future baseline evaluation should define patient-level:

- balanced accuracy
- sensitivity and specificity
- precision, recall, and F1 score
- ROC AUC
- precision-recall AUC
- confusion matrix
- confidence intervals or resampling uncertainty appropriate to patient count

Metric computation is not implemented in P3-F001.

## Calibration Metrics Planned Later

Calibration is a later scaffold topic, not an approved uncertainty-modeling
task. Planned descriptive metrics may include calibration curves, Brier score,
calibration intercept, and calibration slope when sample size permits. No
calibration or uncertainty method is implemented here.

## Limitations

- No dataset is selected or fully approved for modeling.
- Patient-level labels and provenance remain incompletely verified.
- External validation is unresolved.
- Candidate sources may contain overlapping patients, samples, or cells.
- Cohort, treatment, assay, and batch confounding may dominate case-control
  signals.
- Small patient counts may make nonlinear baselines unstable.
- Results cannot support clinical claims and must remain preliminary until
  label verification and judge review.

## Forbidden Actions

- Downloading or preprocessing real data.
- Creating real feature matrices.
- Fitting or training any model.
- Implementing deep learning, foundation models, or uncertainty methods.
- Creating serialized model artifacts.
- Selecting or approving datasets.
- Assigning an external validation cohort.
- Creating cell-level split assignments.
- Reporting baseline performance.
- Starting P3-F002 or later work in this feature.

## Pseudobulk Feature Design

### Why Pseudobulk Is a Strong Baseline

Pseudobulk aggregation summarizes single-cell measurements at a biological
replicate level rather than treating cells as independent patients. This
reduces pseudoreplication, provides a conventional patient-level feature table,
and supports transparent linear and tabular baselines. It does not remove
cohort, batch, treatment, cell-composition, or label-quality risks.

### Patient-Level Aggregation

The preferred aggregation unit is `patient_id` or `donor_id`. All cells and
repeated samples belonging to the same person must remain associated with that
person. A future extractor must preserve source dataset, sample, cohort, batch,
tissue, assay, disease label, and split provenance alongside each aggregate.

Aggregation must occur after a patient- or donor-level split manifest is
defined. No transformation, gene filtering, normalization decision, or feature
selection may learn from held-out patients.

### Sample-Level Aggregation Caveats

`sample_id` is allowed only as an intermediate biological replicate when it can
be linked to a verified patient or donor. Samples from one person must not be
distributed across incompatible splits. A sample-level aggregate must not be
treated as an independent patient observation when repeated or longitudinal
samples exist.

### Cell-Type-Specific Pseudobulk

Cell-type-stratified pseudobulk is included in the design. It requires verified
cell-type annotation provenance and enough cells per patient-cell-type stratum.
Missing cell types, rare strata, annotation differences, and tissue-specific
composition must be reported rather than silently imputed or dropped.

### Allowed Aggregation Functions

- `sum_counts`: preferred count-preserving aggregate when verified raw counts
  are available.
- `mean_expression`: permitted only with a documented input scale and
  normalization state.
- `fraction_expressing`: permitted as a separately identified value type with
  an explicit expression threshold defined later.

No aggregation may use `cell_id` or `barcode` as the biological replicate.

### Normalization Policy Placeholder

`normalization_policy` remains TODO. A later feature must define whether
normalization is applied before or after aggregation, which library-size
method is used, how zero counts are handled, and how the policy is fitted
without held-out-patient information.

### Gene Filtering Policy Placeholder

`gene_filtering_policy` remains TODO. Future policy must define gene identifier
requirements, prevalence or count filters, training-only fitting, mitochondrial
and ribosomal handling, and a report of all removed or unmapped genes. Genes
must not be silently discarded.

### Leakage Risks

- Aggregating cells before assigning patients to splits can leak patient
  information into feature construction.
- Splitting samples from one patient across partitions creates patient leakage.
- Global normalization or gene filtering can use held-out cohort information.
- Cell-type annotation derived jointly across all cohorts may transfer test
  structure into training features.
- Batch, source, treatment, or cell count can become proxies for diagnosis.
- Reusing overlapping GEO and CELLxGENE/HCA records can contaminate
  cross-cohort evaluation.

### Patient-Level Split Dependency

Every future aggregate must reference `split_group` from a validated patient-,
donor-, or cohort-level split manifest. Cell-level split assignments are
forbidden. External validation remains TODO and cannot be assigned by this
design.

### Batch and Cell-Type Caveats

Pseudobulk does not automatically correct batch effects. Batch distributions
must be inspected at patient level, and any later correction must be fitted
without held-out leakage. Cell-type-specific aggregates may be missing
non-randomly by disease, tissue, assay, or cell count; this must be represented
explicitly in future feature manifests.

### Forbidden Assumptions

- Do not assume cells are independent observations.
- Do not assume sample IDs are patient IDs.
- Do not assume a cell type exists for every patient.
- Do not infer missing patient, donor, sample, gene, label, or split metadata.
- Do not assume matrices contain raw counts without verification.
- Do not assume normalization or gene filtering policies before approval.
- Do not assign selected datasets or an external validation cohort.

### Future Output Artifacts

After an explicit future extraction feature, expected artifacts may include:

- a patient/donor-by-feature pseudobulk matrix
- `reports/tables/pseudobulk_feature_manifest.csv`
- aggregation and cell-count summaries
- normalization and gene-filtering decisions
- missing-stratum and dropped-feature reports
- checksums and provenance records

P3-F002 creates none of these real feature outputs. The feature manifest
contains headers only.
