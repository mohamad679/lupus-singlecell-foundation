# Model Card — Lupus Single-Cell Foundation Model


## Claim boundary

**Claim boundary:** internal LOOCV only; no clinical claim; no external validation.

The reported Stage 7 metrics are internal patient-level leave-one-patient-out cross-validation results only. No independent external validation was performed. No clinical claim, clinical diagnostic claim, or clinical deployment claim is made.

## Model family

Mean-pooled Geneformer patient embeddings with logistic regression.

## Project scope

This repository evaluates whether frozen single-cell foundation-model embeddings can support patient-level discrimination of active systemic lupus erythematosus (SLE) flare status from managed SLE and healthy controls in an exploratory PBMC single-cell cohort.

The current model is a research baseline for internal validation only.

## Intended use

Intended use:

- computational biology research
- internal benchmarking of patient-level single-cell representation models
- evaluation of leakage-controlled machine-learning workflows
- exploratory assessment of SLE flare discrimination from frozen embeddings

## Not intended use

This model is not intended for:

- clinical diagnosis
- clinical decision support
- patient triage
- treatment recommendation
- prospective flare forecasting
- deployment in medical or laboratory workflows

## Dataset

Primary exploratory cohort:

- Dataset: GSE174188 / Perez et al. lupus PBMC single-cell RNA-seq cohort
- Source used in exploratory work: CELLxGENE Census
- CELLxGENE dataset identifier: 218acb0f-9f2f-4f76-b90b-15a4b7c7f629
- Evaluation unit: patient/donor

Stage 7 patient groups:

- Managed SLE: 149
- Active flare: 14
- Healthy controls: 98
- Total patients: 261

## Labeling policy

Exploratory donor grouping rule:

- `FLARE*` -> active flare
- `HC-*` or `IGTB*` -> healthy control
- numeric donor identifiers -> managed SLE

This rule is treated as an exploratory cohort-specific label mapping and should not be generalized without independent validation.

## Feature representation

Input representation:

- per-patient Geneformer embedding files
- mean-pooled patient-level embedding vectors
- no cell-level train/test split

The Stage 7 reconciliation uses patient-level embeddings only.

## Evaluation design

Primary internal evaluation:

- leave-one-patient-out cross-validation
- evaluation unit: patient
- model: logistic regression
- class-balanced training
- StandardScaler fit within each training fold only
- model fit within each training fold only

The held-out patient is never used for scaler fitting or model fitting.

## Leakage controls

The Stage 7 run explicitly records the following leakage controls:

- patient-level evaluation only
- leave-one-patient-out cross-validation
- no cell-level split
- fold-local StandardScaler fitting
- fold-local LogisticRegression fitting
- held-out prediction manifest generation

## Internal validation results

### Flare vs managed SLE

- Patients: 163
- Active flare cases: 14
- Managed SLE controls: 149
- AUROC (internal LOOCV only): 0.9962
- AUPRC (internal LOOCV only): 0.9529
- Sensitivity: 14/14
- Specificity: 147/149

### Flare vs healthy controls

- Patients: 112
- Active flare cases: 14
- Healthy controls: 98
- AUROC (internal LOOCV only): 0.9927
- AUPRC (internal LOOCV only): 0.9634
- Sensitivity: 12/14
- Specificity: 97/98

These are internal validation results only.

## Outputs

Stage 7 controlled outputs:

- `scripts/13_stage7_kaggle_result_reconciliation.py`
- `reports/stage7_kaggle_result_reconciliation/stage7_run_summary.json`
- `reports/stage7_kaggle_result_reconciliation/stage7_metric_results.csv`
- `reports/stage7_kaggle_result_reconciliation/stage7_prediction_manifest.csv`

## Limitations

Current limitations:

- small active flare class size
- no independent external validation
- cross-sectional active flare discrimination only
- no longitudinal flare forecasting
- batch/source confounding requires deeper audit
- sex, ancestry, and cell-type composition controls require further expansion
- no clinical deployment claim
- no pathway-level or network-level mechanistic interpretation yet

## Claim boundary

The current repository supports the following claim:

> Frozen Geneformer patient-level embeddings show strong internal leave-one-patient-out discrimination of active SLE flare status in an exploratory PBMC single-cell cohort.

The repository does not support claims of:

- clinical or diagnostic claims
- clinical utility
- external generalization
- deployment readiness
- prospective flare prediction
- treatment-response prediction

## Reproducibility status

The Stage 7 reconciliation run is repository-controlled and produces saved prediction and metric artifacts.

The project remains research-stage and requires additional robustness, confounding, and external validation work before any translational claim.
