# Lupus Single-Cell Foundation Model

Patient-level benchmarking of frozen single-cell foundation-model embeddings for active systemic lupus erythematosus (SLE) flare discrimination from peripheral blood single-cell RNA-seq.

## Scientific objective

This project investigates whether frozen single-cell foundation-model representations, especially Geneformer embeddings, can support patient-level discrimination of active SLE flare from managed SLE and healthy controls.

The current working claim is intentionally conservative:

> Frozen Geneformer patient-level embeddings show strong internal leave-one-patient-out discrimination of active SLE flare status in an exploratory PBMC single-cell cohort.

This project should not be described as future flare prediction. The available analysis is cross-sectional active flare discrimination, not longitudinal pre-flare forecasting.

## Current status

Current repository status:

- Stage 7 reconciliation complete
- patient-level Geneformer embedding evaluation implemented as a script
- leakage-controlled internal leave-one-patient-out cross-validation completed
- metric table saved
- prediction manifest saved
- run summary saved
- external validation not performed
- clinical deployment claim not made

Key controlled outputs:

- `scripts/13_stage7_kaggle_result_reconciliation.py`
- `reports/stage7_kaggle_result_reconciliation/stage7_run_summary.json`
- `reports/stage7_kaggle_result_reconciliation/stage7_metric_results.csv`
- `reports/stage7_kaggle_result_reconciliation/stage7_prediction_manifest.csv`

Project documentation:

- `MODEL_CARD.md`
- `docs/limitations.md`

## Primary dataset

Primary exploratory cohort:

- Dataset: GSE174188 / Perez et al. lupus PBMC single-cell RNA-seq cohort
- Source used in exploratory work: CELLxGENE Census
- CELLxGENE dataset identifier: 218acb0f-9f2f-4f76-b90b-15a4b7c7f629
- Census version used in exploratory notebooks: 2025-11-08
- Evaluation unit: patient/donor

Stage 7 patient groups:

| Group | Patients |
|---|---:|
| Managed SLE | 149 |
| Active flare | 14 |
| Healthy controls | 98 |
| Total | 261 |

Exploratory donor grouping rule:

- `FLARE*` -> active flare
- `HC-*` or `IGTB*` -> healthy control
- numeric donor identifiers -> managed SLE

This label rule is cohort-specific and should not be generalized without independent validation.

## Method summary

The Stage 7 reconciliation evaluates:

- per-patient Geneformer embedding files
- mean-pooled patient-level embedding vectors
- logistic regression
- class-balanced training
- leave-one-patient-out cross-validation

The evaluation is patient-level only. No cell-level train/test split is used.

## Leakage-control policy

The Stage 7 evaluation records the following leakage controls:

- patient-level evaluation only
- leave-one-patient-out cross-validation
- no cell-level split
- StandardScaler fit within each training fold only
- LogisticRegression fit within each training fold only
- held-out prediction manifest written from fold-held-out patients only

## Internal validation results

### Flare vs managed SLE

| Metric | Value |
|---|---:|
| Patients | 163 |
| Active flare cases | 14 |
| Managed SLE controls | 149 |
| AUROC | 0.9962 |
| AUPRC | 0.9529 |
| Sensitivity | 14/14 |
| Specificity | 147/149 |

### Flare vs healthy controls

| Metric | Value |
|---|---:|
| Patients | 112 |
| Active flare cases | 14 |
| Healthy controls | 98 |
| AUROC | 0.9927 |
| AUPRC | 0.9634 |
| Sensitivity | 12/14 |
| Specificity | 97/98 |

These are internal validation results only.

## Main scientific risks

The key risks are:

1. small active flare class size
2. lack of independent external validation
3. potential batch/source confounding
4. possible sex, ancestry, or cell-type composition effects
5. strong raw/pseudobulk baselines may reduce the incremental value of frozen foundation-model embeddings
6. no pathway-level or network-level mechanistic interpretation yet

The project therefore uses conservative claim boundaries and does not claim clinical readiness.

## Claim boundary

This repository supports research-stage internal benchmarking only.

It does not currently support claims of:

- clinical diagnostic performance
- clinical utility
- treatment recommendation
- prospective flare prediction
- independent external generalization
- deployment readiness

## Reproducibility status

Current reproducibility level:

- repository-controlled Stage 7 evaluation script: complete
- saved prediction manifest: complete
- saved metric table: complete
- saved run summary: complete
- automated tests: present
- external validation: pending
- extended confounding analysis: pending
- pathway/network interpretation: pending

## Development status

The repository is currently at:

- Stage 7 complete
- documentation refinement in progress
- next scientific step: robustness, confounding, and external validation controls

The project remains a research-stage computational biology pipeline.
