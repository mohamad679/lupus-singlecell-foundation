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

## Tree-based Baseline Design

### Rationale for Random Forest and XGBoost Baselines

Random forest and XGBoost are planned as nonlinear tabular comparators for
patient-level pseudobulk features. They may capture interactions and threshold
effects that a linear classifier cannot represent. Their inclusion is for
comparative baseline design only; P3-F004 does not instantiate, fit, or import
either estimator.

### Why Tree Models Are Secondary to Logistic Regression

Logistic regression remains the first baseline because it is simpler, more
transparent, and less flexible when patient counts are small. Tree models add
capacity and hyperparameters, increasing overfitting and interpretation risk.
They should be considered only after the linear baseline, using identical
patient-level features, labels, partitions, and evaluation rules.

### Input Requirement

The only planned input feature type is `patient_level_pseudobulk`. Future tree
baselines require a patient/donor-by-feature matrix, patient-level labels, a
patient- or cohort-level split manifest, and the feature manifest. Cell-level
features and cell-level partitions are forbidden.

### Hyperparameter Search Plan Placeholder

Hyperparameter profiles remain TODO for both model families. A later authorized
implementation must define a small, prespecified search space and perform
selection inside patient-level resampling using training data only. Test or
external-cohort performance must not guide tree depth, number of trees,
learning rate, subsampling, feature subsampling, or regularization.

### Class Imbalance Handling Plan

Random forest may later compare balanced class weights with no weighting.
XGBoost may later consider a training-fold-derived positive-class scale. Any
weight must be calculated from patient counts, not cell counts, and must be
fitted independently within each training partition. No weighting strategy is
selected in P3-F004.

### Feature Importance Caveats

Impurity, gain, split-count, and permutation importance can be unstable or
biased by correlated genes, feature scale, sparsity, cell-type stratification,
and cohort confounding. Importance does not establish causality or biological
mechanism. A future report must state the method, training partition, feature
provenance, and stability across patient-level resamples.

### Leakage Risks

- Global filtering, normalization, or feature selection can expose held-out
  cohorts.
- Hyperparameter tuning outside patient-level resampling can overfit.
- Repeated samples from one patient can cross partitions.
- Batch, treatment, source, assay, or cell count can proxy diagnosis.
- Feature-importance inspection on test data can influence model refinement.
- Overlapping GEO and CELLxGENE/HCA records can invalidate cross-cohort claims.

### Overfitting Risks with Small Patient Counts

Tree ensembles can fit high-dimensional pseudobulk noise when the number of
features greatly exceeds the number of patients. Deep trees, large searches,
and repeated tuning can produce optimistic internal estimates. Future work
must constrain model capacity, report patient counts and class balance, and
compare against logistic regression under identical partitions.

### XGBoost Optional Dependency Caution

XGBoost is not a required dependency in P3-F004. The configuration marks it
optional, and the scaffold does not import it. A later feature must explicitly
approve dependency installation and implementation before XGBoost can be used.
Absence of XGBoost must not block validation of the repository scaffold.

### Forbidden Actions Before Modeling Gate

- Do not load real pseudobulk matrices or labels.
- Do not instantiate or fit random forest or XGBoost estimators.
- Do not import XGBoost as a required dependency.
- Do not generate predictions, probabilities, metrics, or feature importance.
- Do not create serialized model or preprocessing artifacts.
- Do not search or select hyperparameters.
- Do not use cell-level features or partitions.
- Do not select datasets or assign an external validation cohort.
- Do not report performance or biological claims.

The tree results and feature-importance tables created by P3-F004 contain
headers only.

## Cell-type Proportion Baseline Design

### Rationale for Cell-type Proportion Baselines

Cell-type proportions provide a compact patient-level summary of immune or
tissue composition without using gene-expression values as predictors. This
baseline can test whether broad composition differences carry case-control
signal and provides a biologically recognizable comparator to pseudobulk
expression models. P3-F005 defines validation contracts only and computes no
proportions.

### Biological Relevance in SLE

SLE can involve shifts in circulating and tissue immune-cell composition.
Patient-level fractions or counts may therefore reflect disease-associated
immune states. However, composition can also reflect treatment, sampling,
processing, tissue, cell recovery, annotation choices, and batch effects.
Observed associations must not be interpreted as causal or disease-specific
without those factors being assessed.

### Required Input: Cell-type Labels

Every future feature requires source-supported or auditable cell-type labels.
The annotation method, ontology or naming scheme, granularity, confidence, and
source dataset must be documented. Missing, uncertain, or incompatible labels
must remain `TODO` or `unclear`; they must not be inferred from marker genes in
this scaffold.

### Patient-level Aggregation

The preferred biological replicate is `patient_id` or `donor_id`. For each
aggregate, future extraction must record cell-type count, total cells, fraction,
split group, dataset, and audit status. All cells and repeated samples from one
person must stay within the same split.

### Sample-level Caveats

`sample_id` is permitted only when it is linked to a verified patient or donor.
Multiple samples from one person are not independent observations and must not
cross train, validation, test, or external-validation partitions. Tissue,
timepoint, treatment, and processing differences between samples must be
retained.

### Compositional Data Caveats

Cell-type fractions sum to one within an aggregation unit, so an increase in
one component necessarily affects others. Raw fractions are not independent
features. Logit and centered-log-ratio transformations are planned only as
future options and require explicit zero-handling, reference, and fitting
policies. No transformation is selected or computed in P3-F005.

### Normalization Policy Placeholder

The initial design records raw cell counts, total cells, and fractions.
Normalization, weighting by total cells, minimum-cell thresholds, and
compositional transformations remain future decisions. Any parameters must be
defined without held-out-patient information.

### Rare Cell-type Handling

Rare cell types must not be silently removed, merged, or imputed. Future policy
must define minimum cells per aggregate, minimum patient prevalence, zero
handling, and a report of excluded or merged annotations. Decisions must be
fitted on training partitions only.

### Batch and Annotation Risks

- Different annotation pipelines can create incompatible cell-type categories.
- Batch, chemistry, tissue processing, and cell recovery can alter proportions.
- Disease groups may be confounded with site, assay, treatment, or cohort.
- Missing cell types may reflect insufficient cell recovery rather than true
  biological absence.
- Annotation performed jointly across held-out cohorts may leak structure.

### Leakage Risks

- Cell-level splitting creates direct patient leakage.
- Repeated samples from one patient can cross partitions.
- Global category merging, rare-cell filtering, or transformations can use
  held-out information.
- Cohort-specific annotations or cell counts can proxy diagnosis.
- Overlapping GEO and CELLxGENE/HCA records can invalidate cross-cohort claims.

### Interpretability Limits

A predictive proportion does not establish that the cell type causes disease
or that its abundance is clinically actionable. Relative abundance cannot
distinguish expansion of one population from loss of another without absolute
counts. Annotation uncertainty, denominator choice, and compositional
dependence must accompany any future interpretation.

### Forbidden Actions Before Modeling Gate

- Do not load or preprocess real cell-level data.
- Do not compute real counts, totals, fractions, or transformations.
- Do not train classifiers or generate predictions.
- Do not create model or preprocessing artifacts.
- Do not infer or reannotate cell types.
- Do not silently remove or merge rare cell types.
- Do not use cell-level features or partitions.
- Do not select datasets or assign an external validation cohort.
- Do not report performance or biological claims.

The feature and result tables created by P3-F005 contain headers only.

## Baseline Evaluation Protocol

### Evaluation Objective

The evaluation protocol defines how future baseline models would be compared
for SLE diagnosis / case-control prediction without computing any current
performance. Evaluation must estimate patient-level discrimination,
classification behavior, and probability calibration under leakage-safe
partitions. P3-F006 creates contracts and validation rules only.

### Patient-level Evaluation Requirement

Predictions must be associated with a patient or donor. Sample-level
predictions are permitted only when samples remain linked to a verified patient
or donor and repeated samples do not cross partitions. Cell-level predictions
must not be reported as independent evaluation observations or converted into
inflated patient counts.

Each future prediction row must include the source dataset, split, true label,
score, prediction unit, label verification status, leakage-check status, and
audit status.

### Cohort-level and External Validation Placeholder

External validation is required later but remains TODO. A true external cohort
must be independent of training data and have compatible patient-level labels,
tissue, assay, feature construction, and evaluation definitions. Until a
cohort is explicitly approved and overlap is excluded, only internal
patient-level or leave-cohort-out evaluation may be designed, not claimed.

### Required Metrics

Future evaluation must define:

- **AUROC:** ranking discrimination across patient-level cases and controls.
- **AUPRC:** precision-recall performance, interpreted against class
  prevalence.
- **Balanced accuracy:** mean recall across classes.
- **F1:** harmonic mean of precision and recall at a prespecified threshold.
- **Sensitivity:** case recall at the selected threshold.
- **Specificity:** control recall at the selected threshold.
- **Brier score:** squared error of patient-level probability estimates.
- **Expected Calibration Error:** binned calibration summary with binning
  policy documented later.

P3-F006 computes none of these metrics.

### Confidence Interval Plan

Confidence intervals are planned for patient-level metrics. The resampling unit
must be the patient or donor, never the cell. Intervals must preserve class and
cohort structure where feasible, report the method and number of successful
resamples, and disclose instability caused by small patient counts.

### Bootstrap Policy Placeholder

Bootstrap is the planned method, but `n_bootstraps` remains TODO. A later
feature must specify stratification, random seed, handling of single-class
resamples, percentile or other interval construction, and whether resampling
is nested within cohort. No bootstrap is executed here.

### Class Imbalance Considerations

Patient counts, not cell counts, define class prevalence. AUPRC must be
interpreted relative to that prevalence. Balanced accuracy, sensitivity,
specificity, and F1 should accompany AUROC. Any class weighting or threshold
choice must be fitted without held-out patient information.

### Calibration Caveats

Calibration metrics require patient-level probability scores and enough
patients across the probability range. Expected Calibration Error depends on
binning and can be unstable in small cohorts. Calibration assessment does not
authorize uncertainty modeling, entropy, selective prediction, or clinical
risk claims.

### Threshold Selection Policy

A classification threshold must be prespecified or selected using training or
validation patients only. The test set and future external cohort must not be
used to choose a threshold, optimize F1, or target sensitivity/specificity.
Every threshold-dependent metric must record the threshold source.

### Leakage-prevention Dependency

Evaluation cannot proceed unless patient, donor, sample, cell, cohort, batch,
and label leakage checks pass. Feature extraction, normalization,
hyperparameter selection, class weighting, calibration, and threshold
selection must be isolated from held-out patients.

### No Performance Claims Before Verified Labels

No metric may be reported as scientific evidence until patient-level labels
and provenance are verified. Even after verification, baseline findings remain
preliminary until dataset scope, cohort overlap, and judge review are complete.
This protocol makes no performance or clinical utility claim.

### Failure Modes

Future evaluation must fail when:

- evaluation is attempted while `allow_real_evaluation` is false
- predictions are cell-level or patient linkage is absent
- labels are unverified
- leakage checks have not passed
- split or prediction manifests are missing
- test data are used for threshold selection or model refinement
- metrics are reported without patient counts and class counts
- confidence intervals resample cells instead of patients
- external validation is claimed without an approved independent cohort
- clinical utility is claimed from scaffold or preliminary results

The baseline evaluation results and prediction manifest created by P3-F006
contain headers only.
