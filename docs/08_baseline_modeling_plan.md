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

## Logistic Regression Baseline Design

### Why Logistic Regression Is the First Baseline

Logistic regression is the first planned classifier because it is transparent,
well understood, and appropriate for testing whether patient-level pseudobulk
features contain a reproducible case-control signal. Its coefficients can be
audited against feature provenance, and its complexity can be controlled
directly through regularization. It remains a scaffold in P3-F003; no estimator
is instantiated or fitted.

### Input Requirement

The only planned input feature type is `patient_level_pseudobulk`. Future input
must include:

- a patient- or donor-by-feature pseudobulk matrix
- source-verified patient-level SLE and healthy control labels
- a patient-, donor-, or cohort-level split manifest
- the pseudobulk feature manifest

Cell-level feature matrices and cell-level labels are forbidden. Sample-level
aggregates may be inputs only after linkage to a patient or donor and leakage-
safe grouping.

### Task

The target remains **SLE diagnosis / case-control prediction**. Disease
activity, flare, lupus nephritis, treatment response, and other clinical tasks
remain blocked.

### Regularization Plan

Planned regularization options are L1, L2, and elastic net. Solver and penalty
compatibility must be validated in a later authorized implementation. Any
regularization strength or elastic-net mixing parameter must be selected using
training data only, within patient-level resampling. No hyperparameter is
selected in P3-F003.

### Class Imbalance Handling Plan

Planned class-weight options are `balanced` and `none`. A later protocol must
record patient counts by class, define the primary class-weight strategy before
test evaluation, and prevent cell counts from substituting for patient counts.
Resampling cells or duplicating patients is not an approved imbalance method.

### Feature Scaling Plan

Scaling is required for a fair regularized linear baseline but remains a future
implementation decision. Any scaler must be fitted on training patients only
and applied unchanged to validation, test, and future external cohorts. Sparse
and count-derived feature behavior must be documented. P3-F003 performs no
scaling.

### Patient-Level Split Dependency

Model design depends on a validated patient-, donor-, or cohort-level split.
All samples and cells from one patient or donor must remain in one partition.
Feature scaling, filtering, regularization selection, and class weighting must
not use held-out patient information.

### Cross-Cohort Evaluation Dependency

External validation remains TODO. Cross-cohort evaluation cannot begin until
cohort independence, compatible label definitions, tissue and assay
compatibility, and absence of patient/sample/cell overlap are verified.

### Calibration Metrics Planned Later

Future evaluation may report Brier score, expected calibration error,
calibration intercept, calibration slope, and calibration curves when patient
counts permit. These are descriptive evaluation plans, not approval for
uncertainty modeling. No probability predictions or calibration metrics are
generated in P3-F003.

### Leakage Risks

- Global feature scaling or feature filtering can expose held-out cohorts.
- Hyperparameter selection outside patient-level resampling can overfit.
- Repeated samples from one patient can cross partitions.
- Batch, source, treatment, assay, or cell count can proxy the disease label.
- Overlapping GEO and CELLxGENE/HCA records can invalidate cross-cohort claims.
- Coefficient interpretation can be misleading when correlated features,
  compositional effects, or unstable gene mappings are ignored.

### Failure Modes

Future execution must fail when:

- inputs are cell-level rather than patient-level pseudobulk
- patient/donor identifiers or labels are unresolved
- the split manifest permits patient, donor, or sample overlap
- feature and split manifests are absent
- label provenance is not documented
- training or prediction has not been explicitly enabled
- an external cohort is claimed without independent-cohort evidence
- result tables omit audit status or preliminary-result labeling

### Forbidden Actions Before Modeling Gate

- Do not load real feature matrices or labels.
- Do not instantiate or fit logistic regression.
- Do not generate probabilities, classifications, metrics, or coefficients.
- Do not create serialized model or preprocessing artifacts.
- Do not select hyperparameters.
- Do not use cell-level features or splits.
- Do not select datasets or assign an external validation cohort.
- Do not report performance or biological associations.

The results and coefficient tables created by P3-F003 contain headers only.
